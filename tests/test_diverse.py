import jax
import jax.numpy as jnp
import numpy as np
from ncago.go.diverse import component_key
from ncago.go.labels import liberties
from ncago.experiments.learnability import balanced_targets, locality_witness
from ncago.nca.model import ModelConfig, NCA, initialize, init_params, step


def test_diverse_components_are_exact_and_disjoint():
    boards, targets, _ = balanced_targets(9, 32, 71, diverse=True, component_dedup=True)
    keys = {component_key(b, np.argwhere(y >= 0)) for b, y in zip(boards, targets)}
    held, labels, _ = balanced_targets(9, 16, 72, keys, diverse=True, component_dedup=True)
    assert len(keys) == 32
    assert not keys.intersection(component_key(b, np.argwhere(y >= 0)) for b, y in zip(held, labels))
    for board, target in zip(boards, targets):
        mask = target >= 0
        np.testing.assert_array_equal(liberties(board)[0][mask], target[mask])


def test_chain_messages_ignore_background_outside_static_neighborhood():
    board, _, query, _ = locality_witness(13)
    changed = board.copy()
    changed[:query[0]-1] = 2
    changed[query[0]+2:] = 2
    points = np.argwhere(board == 1)
    assert component_key(board, points) == component_key(changed, points)
    config = ModelConfig(channels=32, heads=2, readout="ce", gated=True, chain_messages=True, init_sigma=0., fire_rate=1.)
    model = NCA(config)
    tokens = jnp.asarray(np.stack([board, changed]))
    key = jax.random.PRNGKey(92)
    state = initialize(tokens, key, config)
    params = init_params(model, state, key)
    params = jax.tree_util.tree_map(lambda p: p+jax.random.normal(key, p.shape)*.3, params)
    def body(s, i):
        return step(model, params, s, tokens, jax.random.fold_in(key, i))[0], None
    final, _ = jax.lax.scan(body, state, jnp.arange(64))
    rows, cols = points.T
    np.testing.assert_allclose(final[0, rows, cols], final[1, rows, cols], atol=1e-6, rtol=1e-6)
