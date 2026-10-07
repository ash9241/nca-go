import numpy as np
import jax
import jax.numpy as jnp
from ncago.experiments.propagation_probe import paired_queries, predict
from ncago.go.labels import liberties
from ncago.go.rules import chains
from ncago.nca.model import ModelConfig, NCA, initialize, init_params


def test_query_pairs_have_distant_exact_answer_changes():
    boards, queries, labels, distance = paired_queries(13, 8, 17)
    assert distance == 10
    np.testing.assert_array_equal(labels, np.tile([0, 1], 8))
    for one, two, q in zip(boards[::2], boards[1::2], queries[::2]):
        changed = np.argwhere(one != two)
        assert len(changed) == 1
        assert np.max(np.abs(changed[0]-q)) > 9
        for b in (one, two):
            assert all(len(chain.liberties) > 0 for chain in chains(b))
        assert liberties(one)[0][tuple(q)] == 0
        assert liberties(two)[0][tuple(q)] == 1


def test_coupled_randomness_preserves_precausal_query_equality():
    boards, queries, _, distance = paired_queries(13, 2, 3)
    config = ModelConfig(channels=16, heads=2, readout="ce", init_sigma=.15)
    model = NCA(config)
    key = jax.random.PRNGKey(77)
    template = initialize(jnp.asarray(boards[:1]), key, config)
    params = init_params(model, template, key)
    params = jax.tree_util.tree_map(lambda p: p+jax.random.normal(key, p.shape)*.05, params)
    out = np.asarray(predict(model, params, jnp.asarray(boards), key, distance-1))
    values = out[np.arange(len(out)), queries[:, 0], queries[:, 1]]
    np.testing.assert_array_equal(values[::2], values[1::2])
