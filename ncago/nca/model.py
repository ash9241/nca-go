from dataclasses import dataclass
import jax
import jax.numpy as jnp
from flax import linen as nn


@dataclass(frozen=True)
class ModelConfig:
    channels: int = 32
    input_channels: int = 8
    output_channels: int = 4
    classes: int = 4
    heads: int = 4
    expansion: int = 2
    neighborhood: str = "moore"
    normalization_groups: int = 0
    readout: str = "mse"
    fire_rate: float = .8
    init_sigma: float = .15
    gated: bool = False
    algorithm_hints: bool = False
    chain_messages: bool = False
    identifier_channels: int = 0
    identifier_input_scale: float = 1.
    identifier_zero_init: bool = False

    def __post_init__(self):
        if self.input_channels < 4 or self.output_channels < self.classes:
            raise ValueError("Not enough channels for orthonormal embeddings")
        if self.identifier_channels < 0 or self.input_channels-self.identifier_channels < 4:
            raise ValueError("Identifier channels must leave at least four token channels")
        if not 0 < self.identifier_input_scale <= 1:
            raise ValueError("Identifier perception scale must be in (0,1]")
        if self.channels <= self.input_channels+self.output_channels:
            raise ValueError("Hidden state must have at least one channel")
        if self.normalization_groups and (self.channels-self.input_channels) % self.normalization_groups:
            raise ValueError("Mutable channels must divide into normalization groups")
        if self.neighborhood not in ("moore", "von_neumann") or self.readout not in ("mse", "ce"):
            raise ValueError("Unknown neighborhood or readout")


class NCA(nn.Module):
    config: ModelConfig

    @nn.compact
    def __call__(self, state):
        c = self.config
        perceived = perception_inputs(state, c)
        kernel = self.param("perception_kernel", identifier_kernel_init(c), (3,3,c.channels,c.heads*c.channels))
        if c.neighborhood == "von_neumann":
            kernel = kernel*jnp.array([[0,1,0],[1,1,1],[0,1,0]])[...,None,None]
        def convolve(values, weights):
            return jax.lax.conv_general_dilated(values, weights, (1,1), "SAME",
                                              dimension_numbers=("NHWC","HWIO","NHWC"))
        if c.chain_messages:
            inputs, hidden_state = perceived[..., :c.input_channels], perceived[..., c.input_channels:]
            static = convolve(inputs, kernel[:, :, :c.input_channels])
            orthogonal = jnp.array([[0,1,0],[1,1,1],[0,1,0]])[..., None, None]
            message_kernel = kernel[:, :, c.input_channels:]*orthogonal
            black = convolve(hidden_state*inputs[..., 1:2], message_kernel)
            white = convolve(hidden_state*inputs[..., 2:3], message_kernel)
            perception = static + jnp.where(inputs[..., 1:2] > .5, black, white)
        else:
            perception = convolve(perceived, kernel)
        perception = perception + self.param("perception_bias", nn.initializers.zeros, (c.heads*c.channels,))
        hidden = nn.relu(nn.Dense(c.expansion*c.channels, name="expand")(perception))
        proposal = nn.Dense(c.channels, kernel_init=nn.initializers.zeros, name="update")(hidden)
        if c.gated:
            gate = nn.sigmoid(nn.Dense(c.channels, kernel_init=nn.initializers.zeros,
                                      bias_init=nn.initializers.constant(-2.), name="gate")(hidden))
            return gate*(nn.tanh(proposal)-state)
        return proposal

    @nn.compact
    def logits(self, state):
        c = self.config
        output = state[..., c.input_channels:c.input_channels+c.output_channels]
        if c.readout == "ce":
            return nn.Dense(c.classes, name="readout")(output)
        return output

    @nn.compact
    def hint_logits(self, state):
        c = self.config
        output = state[..., c.input_channels:c.input_channels+c.output_channels]
        return nn.Dense(5, name="hint_readout")(output)


def identifier_kernel_init(config):
    """Optional zero initialization of the ID input rows, still trainable."""
    initializer = nn.initializers.lecun_normal()
    def initialize_kernel(key, shape, dtype=jnp.float32):
        values = initializer(key, shape, dtype)
        if config.identifier_channels and config.identifier_zero_init:
            start = config.input_channels-config.identifier_channels
            values = values.at[..., start:config.input_channels, :].set(0.)
        return values
    return initialize_kernel


def perception_inputs(state, config):
    """Precondition IID channels without changing their frozen ±1 values."""
    if not config.identifier_channels or config.identifier_input_scale == 1:
        return state
    start = config.input_channels-config.identifier_channels
    return state.at[..., start:config.input_channels].multiply(config.identifier_input_scale)


def initialize(tokens, key, config):
    # Preserve the old initialization stream for identifier-free checkpoints.
    noise_key = jax.random.fold_in(key, 710) if config.identifier_channels else key
    state = jax.random.normal(noise_key, tokens.shape+(config.channels,))*config.init_sigma
    return state.at[..., :config.input_channels].set(frozen_inputs(tokens, key, config))


def frozen_inputs(tokens, key, config):
    base = config.input_channels-config.identifier_channels
    plain = jnp.where(tokens >= 4, jnp.where(tokens % 2 == 0, 1, 2), tokens)
    encoded = jax.nn.one_hot(plain, base)
    if base >= 8:
        # Optional race anchors and the supplied side-to-move occupy unused
        # token planes. Original boards retain their exact old encoding.
        encoded = encoded.at[..., 4].set(((tokens == 4) | (tokens == 6)).astype(encoded.dtype))
        encoded = encoded.at[..., 5].set(((tokens == 5) | (tokens == 7)).astype(encoded.dtype))
        white_turn = jnp.any((tokens == 6) | (tokens == 7), axis=(-2, -1), keepdims=True)
        encoded = encoded.at[..., 6].set(jnp.broadcast_to(white_turn, tokens.shape).astype(encoded.dtype))
    if not config.identifier_channels:
        return encoded
    identifiers = 2*jax.random.bernoulli(jax.random.fold_in(key, 711), .5,
                                       tokens.shape+(config.identifier_channels,)).astype(jnp.float32)-1
    return jnp.concatenate((encoded, identifiers), axis=-1)


def init_params(model, state, key):
    variables = model.init(key, state)
    if model.config.readout == "ce" or model.config.algorithm_hints:
        from flax.core import unfreeze, freeze
        merged = unfreeze(variables)
        if model.config.readout == "ce":
            head = unfreeze(model.init(jax.random.fold_in(key,1), state, method=model.logits))
            merged["params"].update(head["params"])
        if model.config.algorithm_hints:
            head = unfreeze(model.init(jax.random.fold_in(key,2), state, method=model.hint_logits))
            merged["params"].update(head["params"])
        variables = freeze(merged)
    return variables["params"]


def readout(model, params, state):
    c = model.config
    out = model.apply({"params":params}, state, method=model.logits)
    if c.readout == "ce":
        scores = jax.nn.softmax(out, -1)
    else:
        embedding = jnp.eye(c.output_channels)[:c.classes]
        scores = 1/(1+jnp.sqrt(jnp.sum((out[...,None,:]-embedding)**2,-1)+1e-12))
    valid = jnp.all(jnp.isfinite(state),axis=-1)&jnp.all(jnp.isfinite(scores),axis=-1)
    return jnp.where(valid,jnp.argmax(scores,-1),-2),jnp.where(valid,jnp.max(scores,-1),0.)


def step(model, params, state, tokens, key, adaptive=False, noise_sigma=0., damage=False):
    c = model.config
    firing_key, temporal_key, spatial_key, noise_key = jax.random.split(key, 4)
    rate = c.fire_rate
    if adaptive:
        _, confidence = readout(model,params,state)
        rate = jnp.where(confidence > .95, .4, rate)
    active = tokens != 3
    firing = jax.random.bernoulli(firing_key, rate, tokens.shape)&active
    delta = model.apply({"params":params}, state).at[..., :c.input_channels].set(0)
    out = state + firing[...,None]*delta
    mutable = (jnp.arange(c.channels) >= c.input_channels)
    noisy = jax.random.bernoulli(temporal_key,.1,(tokens.shape[0],1,1))&jax.random.bernoulli(spatial_key,.2,tokens.shape)&active
    out += noisy[...,None]*mutable*jax.random.normal(noise_key,state.shape)*noise_sigma
    if c.normalization_groups:
        values = out[...,c.input_channels:]
        shape = values.shape
        values = values.reshape(shape[:-1]+(c.normalization_groups,-1))
        # Project onto the unit ball. Unit-sphere normalization has a huge
        # Jacobian near zero that overflows across recurrent training steps.
        # Clamp the squared norm before sqrt, preserving the zero-state
        # identity derivative and bounding each mutable group by one.
        values /= jnp.sqrt(jnp.maximum(jnp.sum(values**2,axis=-1,keepdims=True),1.))
        out = out.at[...,c.input_channels:].set(values.reshape(shape))
    if damage:
        h, w = tokens.shape[-2:]
        rr, cc = jnp.ogrid[:h,:w]
        circle = (rr-h//2)**2+(cc-w//2)**2 <= (.25*w)**2
        out = jnp.where(circle[...,None]&mutable, 0., out)
    out = jnp.where(active[...,None],out,state)
    return out, firing


def rollout(model, params, state, tokens, key, steps, adaptive=False, noise_sigma=0., noise_fraction=.25, damage_step=-1, keep_states=False):
    def body(carry, index):
        sigma = jnp.where(index < steps*noise_fraction,noise_sigma,0.)
        out, fire = step(model,params,carry,tokens,jax.random.fold_in(key,index),adaptive,sigma)
        if damage_step >= 0:
            h, w = tokens.shape[-2:]
            rr, cc = jnp.ogrid[:h,:w]
            circle = (rr-h//2)**2+(cc-w//2)**2 <= (.25*w)**2
            mutable = jnp.arange(model.config.channels) >= model.config.input_channels
            out = jnp.where((index == damage_step)&circle[...,None]&mutable&(tokens != 3)[...,None],0.,out)
        prediction, confidence = readout(model,params,out)
        return out, (prediction,confidence,fire,out[0]) if keep_states else (prediction,confidence,fire)
    return jax.lax.scan(body,state,jnp.arange(steps))


def supervised_loss(model, params, state, targets):
    c = model.config
    mask = targets >= 0
    values = model.apply({"params":params},state,method=model.logits)
    if c.readout == "ce":
        import optax
        error = optax.softmax_cross_entropy_with_integer_labels(values,jnp.maximum(targets,0))
    else:
        embedding = jax.nn.one_hot(jnp.maximum(targets,0),c.output_channels)
        error = jnp.sum((values-embedding)**2,-1)
    return jnp.sum(jnp.where(mask,error,0))/jnp.maximum(jnp.sum(mask),1)
