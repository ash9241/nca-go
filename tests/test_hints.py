import jax
import jax.numpy as jnp
import numpy as np
from ncago.baselines.local import liberty_ca
from ncago.experiments.learnability import balanced_targets
from ncago.nca.hints import initial_ids, id_step, discovered_count


def test_vectorized_teacher_matches_exact_local_ca_trajectory():
    boards, _, _ = balanced_targets(7, 8, 512)
    tokens = jnp.asarray(boards)
    def body(state, index):
        next_state = id_step(state, tokens, jnp.ones(tokens.shape, bool))
        return next_state, discovered_count(next_state, tokens)
    _, trace = jax.jit(lambda: jax.lax.scan(body, initial_ids(tokens), jnp.arange(50)))()
    trace = np.asarray(trace)
    for i, board in enumerate(boards):
        expected, _ = liberty_ca(board, max_steps=50)
        mask = (board == 1) | (board == 2)
        np.testing.assert_array_equal(trace[:len(expected)-1, i][:, mask], (expected[1:]+1)[:, mask])
        np.testing.assert_array_equal(trace[-1, i][mask], (expected[-1]+1)[mask])


def test_teacher_firing_freezes_inactive_cells_and_preserves_monotonic_counts():
    boards, _, _ = balanced_targets(7, 4, 31)
    tokens = jnp.asarray(boards)
    initial = initial_ids(tokens)
    np.testing.assert_array_equal(id_step(initial, tokens, jnp.zeros(tokens.shape, bool)), initial)
    state = initial
    for i in range(30):
        firing = jax.random.bernoulli(jax.random.PRNGKey(i), .8, tokens.shape)
        new = id_step(state, tokens, firing)
        assert np.all(np.asarray(discovered_count(new, tokens)) >= np.asarray(discovered_count(state, tokens)))
        state = new
