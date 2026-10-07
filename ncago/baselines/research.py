"""Recurrent CNN and stone-graph baselines sharing the NCA training interface."""
import jax.numpy as jnp
from flax import linen as nn
from ncago.nca.model import NCA, perception_inputs, identifier_kernel_init


class RecurrentCNN(NCA):
    @nn.compact
    def __call__(self, state):
        c = self.config
        hidden = nn.relu(nn.Conv(c.channels, (3, 3), name="conv1", kernel_init=identifier_kernel_init(c))(perception_inputs(state, c)))
        proposal = nn.Conv(c.channels, (3, 3), kernel_init=nn.initializers.zeros,
                           name="conv2")(hidden)
        gate = nn.sigmoid(nn.Dense(c.channels, bias_init=nn.initializers.constant(-2.),
                                  kernel_init=nn.initializers.zeros, name="gate")(hidden))
        return gate*(nn.tanh(proposal)-state)


class StoneGNN(NCA):
    aggregation: str = "sum"

    @nn.compact
    def __call__(self, state):
        c = self.config
        tokens = jnp.argmax(state[..., :4], axis=-1)
        mutable = state[..., c.input_channels:]
        # Local static information includes adjacent liberty IDs. Learned
        # mutable messages travel exclusively on same-color stone edges.
        local = nn.Conv(c.channels, (3, 3), name="local", kernel_init=identifier_kernel_init(c))(perception_inputs(state, c)[..., :c.input_channels])
        padded = jnp.pad(mutable, ((0, 0), (1, 1), (1, 1), (0, 0)))
        tpad = jnp.pad(tokens, ((0, 0), (1, 1), (1, 1)), constant_values=3)
        h, w = tokens.shape[1:]
        messages, masks = [], []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = padded[:, 1+dr:1+dr+h, 1+dc:1+dc+w]
            other = tpad[:, 1+dr:1+dr+h, 1+dc:1+dc+w]
            mask = (other == tokens) & ((tokens == 1) | (tokens == 2))
            messages.append(neighbor)
            masks.append(mask)
        messages, masks = jnp.stack(messages), jnp.stack(masks)
        if self.aggregation == "sum":
            aggregate = jnp.sum(jnp.where(masks[..., None], messages, 0.), axis=0)
        elif self.aggregation == "max":
            aggregate = jnp.max(jnp.where(masks[..., None], messages, -1e9), axis=0)
            aggregate = jnp.where(jnp.any(masks, axis=0)[..., None], aggregate, 0.)
        else:
            raise ValueError(self.aggregation)
        features = jnp.concatenate((mutable, aggregate, local), axis=-1)
        hidden = nn.relu(nn.Dense(c.channels*2, name="expand")(features))
        proposal = nn.Dense(mutable.shape[-1], kernel_init=nn.initializers.zeros, name="proposal")(hidden)
        gate = nn.sigmoid(nn.Dense(mutable.shape[-1], kernel_init=nn.initializers.zeros,
                                  bias_init=nn.initializers.constant(-2.), name="gate")(hidden))
        change = gate*(nn.tanh(proposal)-mutable)
        return jnp.concatenate((jnp.zeros_like(state[..., :c.input_channels]), change), axis=-1)
