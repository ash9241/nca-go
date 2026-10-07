from dataclasses import replace
import numpy as np
import jax
import jax.numpy as jnp
from ncago.nca.model import ModelConfig,NCA,initialize,init_params,step,readout
from ncago.baselines.resnet import ResNet,matched_width,parameter_count
from ncago.experiments.metrics import solve_times,bootstrap_gap,verdict,accuracy


def test_frozen_inputs_offboard_and_locality():
    c = ModelConfig(channels=16,heads=2)
    model = NCA(c)
    tokens = jnp.zeros((1,7,7),jnp.int32).at[:,0,:].set(3)
    key = jax.random.PRNGKey(7)
    state = initialize(tokens,key,c)
    params = init_params(model,state,key)
    params = jax.tree_util.tree_map(lambda p:p+jax.random.normal(key,p.shape)*.02,params)
    out,fire = step(model,params,state,tokens,key,noise_sigma=.15)
    np.testing.assert_array_equal(out[...,:8],state[...,:8])
    np.testing.assert_array_equal(out[:,0],state[:,0])
    assert not np.any(fire[:,0])
    changed = state.at[:,6,6].add(10)
    a,_ = step(model,params,state,tokens,key)
    b,_ = step(model,params,changed,tokens,key)
    np.testing.assert_array_equal(a[:,1:5,1:5],b[:,1:5,1:5])


def test_embedding_and_zero_initialization():
    c = ModelConfig(channels=16,heads=2)
    model = NCA(c)
    key = jax.random.PRNGKey(4)
    tokens = jnp.zeros((1,5,5),jnp.int32)
    state = initialize(tokens,key,c)
    params = init_params(model,state,key)
    out,_ = step(model,params,state,tokens,key)
    np.testing.assert_array_equal(out,state)
    state = state.at[...,8:12].set(jnp.eye(4)[2])
    prediction,confidence = readout(model,params,state)
    assert np.all(prediction == 2)
    np.testing.assert_allclose(confidence,1.,atol=2e-6)


def test_normalized_zero_state_has_finite_training_gradients():
    from ncago.nca.model import supervised_loss
    c = ModelConfig(channels=32,heads=2,normalization_groups=4,init_sigma=0.,readout="ce")
    model = NCA(c)
    key = jax.random.PRNGKey(17)
    tokens = jnp.ones((1,5,5),jnp.int32)
    state = initialize(tokens,key,c)
    params = init_params(model,state,key)
    def loss(p):
        def body(s,i):
            return step(model,p,s,tokens,jax.random.fold_in(key,i))[0],None
        out,_ = jax.lax.scan(body,state,jnp.arange(32))
        return supervised_loss(model,p,out,jnp.zeros(tokens.shape,jnp.int32))
    gradients = jax.grad(loss)(params)
    assert all(np.all(np.isfinite(value)) for value in jax.tree_util.tree_leaves(gradients))


def test_gated_rollout_bounds_mutable_state_and_preserves_inputs():
    c = ModelConfig(channels=32,heads=2,gated=True,init_sigma=0.)
    model = NCA(c)
    key = jax.random.PRNGKey(29)
    tokens = jnp.ones((1,5,5),jnp.int32)
    state = initialize(tokens,key,c)
    original = np.asarray(state[...,:c.input_channels])
    params = init_params(model,state,key)
    params = jax.tree_util.tree_map(lambda p:p + jax.random.normal(key,p.shape)*2,params)
    def body(s,i):
        return step(model,params,s,tokens,jax.random.fold_in(key,i))[0],None
    final,_ = jax.lax.scan(body,state,jnp.arange(128))
    assert np.all(np.isfinite(final))
    assert np.max(np.abs(final[...,c.input_channels:])) <= 1.000001
    np.testing.assert_array_equal(final[...,:c.input_channels],original)


def test_baseline_radius_and_parameter_matching():
    model = ResNet(4,blocks=4,width=8)
    params = model.init(jax.random.PRNGKey(0),jnp.zeros((1,9,9,8)))
    assert model.receptive_field_radius == 9
    assert matched_width(parameter_count(params),4,4) == 8


def test_convergence_bootstrap_and_verdicts():
    target = np.zeros((2,2),int)
    p = np.zeros((4,2,2),int)
    p[1,0,0] = 1
    assert solve_times(p,target,[2,4,8,16]) == 8
    p[-1,0,0] = 1
    assert solve_times(p,target,[2,4,8,16]) is None
    gap,lo,hi = bootstrap_gap([1,1,1],[0,0,0],samples=100)
    assert gap == lo == hi == 1
    assert verdict(.96,.9) == "Use NCA"
    assert verdict(.90,.96) == "Use baseline"
    assert verdict(None,.96) == "Unknown"
