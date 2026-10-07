import numpy as np
import jax
import jax.numpy as jnp
from ncago.go.research_data import count_labels, fast_random_position, OnlineStream, witness_set, identifier_reference, identifier_reference_fast
from ncago.go.rules import group
from ncago.nca.model import ModelConfig, NCA, initialize, init_params, step
from ncago.experiments.checkpoint_audit import chain_features, matrix_metrics
from ncago.experiments.research_train import balanced_loss, build_model, DEFAULT


def test_chain_features_cycles_diameter_and_actual_grid_cone():
    board = np.zeros((9, 9), np.int8)
    board[1, 1:8] = 1
    board[4:7, 4:7] = 2
    board[5, 5] = 0
    f = chain_features(board)
    assert tuple(f[1, 1, 1:5]) == (6, 0, 7, 1)
    assert tuple(f[4, 4, 1:5]) == (4, 1, 8, 2)
    assert f[1, 1, 5] == 7
    confusion = np.array([[2, 3, 0, 0], [5, 4, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    assert matrix_metrics(confusion)["overcounts"] == 3
    assert matrix_metrics(confusion)["undercounts"] == 5


def test_multiple_edit_light_cone_uses_nearest_edit():
    from ncago.experiments.research_eval import paired_edit_distances
    a = np.zeros((9, 9), np.int8)
    b = a.copy(); b[0, 0] = b[7, 8] = 1
    nearest, farthest = paired_edit_distances([a, b], [(8, 8), (8, 8)])
    np.testing.assert_array_equal(nearest, [1, 1])
    np.testing.assert_array_equal(farthest, [8, 8])


def test_pair_random_fields_are_distinct_by_size_family_and_draw():
    from ncago.experiments.research_eval import pair_test_keys
    keys = [tuple(np.asarray(pair_test_keys(size, kind, draw)[1]))
            for size in (9, 37) for kind in ('witness', 'cycle_pairs') for draw in (0, 1)]
    assert len(set(keys)) == 8
    a, b = pair_test_keys(37, 'witness', 0), pair_test_keys(37, 'witness', 1)
    np.testing.assert_array_equal(a[0], b[0])  # ID-only sensitivity holds firing fixed.
    assert not np.array_equal(a[1], b[1])
    c = pair_test_keys(37, 'witness', 0, namespace='another_task')
    assert not np.array_equal(a[1], c[1])


def test_online_stream_reproducible_legal_and_offboard_not_stones():
    a, b = OnlineStream(5), OnlineStream(5)
    aa, ay = a.draw(12)
    bb, by = b.draw(12)
    np.testing.assert_array_equal(aa, bb)
    np.testing.assert_array_equal(ay, by)
    assert a.digest.hexdigest() == b.digest.hexdigest()
    assert a.last_sources == b.last_sources
    assert sum(a.source_draw_counts.values()) == len(aa)
    fixed = OnlineStream(7)
    fixed.draw(16)
    assert fixed.digest.hexdigest() == "518faaaad99d77f60eb5517fddca3c25af8faffe2721f9b8efe39b8cfa3235df"
    for board, labels in zip(aa, ay):
        assert np.all(labels[board == 3] == -1)
        for r, c in np.argwhere((board == 1) | (board == 2)):
            _, liberties = group(board, r, c)
            assert liberties.any()
            assert labels[r, c] == min(4, liberties.sum())-1
    np.testing.assert_array_equal(fast_random_position(7, 42), fast_random_position(7, 42))


def test_prefetch_preserves_exact_consumed_online_stream():
    from ncago.go.research_data import OnlinePrefetch
    serial, concurrent = OnlineStream(77), OnlineStream(77)
    prefetch = OnlinePrefetch(concurrent, 8, 3)
    try:
        for _ in range(3):
            a, ay = serial.draw(8)
            b, by = prefetch.draw()
            np.testing.assert_array_equal(a, b)
            np.testing.assert_array_equal(ay, by)
            assert prefetch.stats == dict(online_boards=serial.draws, stream_sha256=serial.digest.hexdigest())
    finally:
        prefetch.close()
    assert concurrent.digest.hexdigest() == serial.digest.hexdigest()


def test_user_relative_stability_gate_is_separate_from_accuracy():
    from ncago.experiments.research_train import stability_assessment
    records = [dict(size=size, depth=d, draw=draw, stone_accuracy=.985 if size == 9 else .5,
                    macro_accuracy=.986 if size == 9 else .3)
               for size in (9, 13) for d in (32, 64, 128, 512, 1024) for draw in range(3)]
    measured = stability_assessment(records)
    assert measured["stability_gate"] and measured["useful_accuracy"]
    for r in records:
        if r["size"] == 9 and r["depth"] == 1024:
            r["stone_accuracy"] = .982
    assert not stability_assessment(records)["stability_gate"]
    for r in records:
        r["stone_accuracy"] = r["macro_accuracy"] = .25
    measured = stability_assessment(records)
    assert measured["stability_gate"] and not measured["useful_accuracy"]


def test_identifiers_frozen_resampled_and_no_label_input():
    config = ModelConfig(channels=80, input_channels=24, identifier_channels=16, gated=True, init_sigma=0.)
    tokens = jnp.ones((2, 5, 5), jnp.int32)
    a = initialize(tokens, jax.random.PRNGKey(0), config)
    b = initialize(tokens, jax.random.PRNGKey(1), config)
    assert set(np.unique(a[..., 8:24])) == {-1., 1.}
    assert np.any(np.asarray(a[..., 8:24]) != np.asarray(b[..., 8:24]))
    model = NCA(config)
    params = init_params(model, a, jax.random.PRNGKey(2))
    final, _ = step(model, params, a, tokens, jax.random.PRNGKey(3), noise_sigma=.15, damage=True)
    np.testing.assert_array_equal(final[..., :24], a[..., :24])


def test_identifier_preconditioning_keeps_frozen_ids_and_only_scales_perception():
    from ncago.nca.model import perception_inputs
    c = ModelConfig(channels=80, input_channels=24, identifier_channels=16,
                    identifier_input_scale=.25, gated=True, init_sigma=0.)
    tokens = jnp.ones((1, 5, 5), jnp.int32)
    state = initialize(tokens, jax.random.PRNGKey(1), c)
    perceived = perception_inputs(state, c)
    np.testing.assert_array_equal(perceived[..., :8], state[..., :8])
    np.testing.assert_array_equal(perceived[..., 8:24], state[..., 8:24]*.25)
    np.testing.assert_array_equal(perceived[..., 24:], state[..., 24:])
    model = NCA(c); params = init_params(model, state, jax.random.PRNGKey(2))
    out, _ = step(model, params, state, tokens, jax.random.PRNGKey(3), noise_sigma=.15)
    np.testing.assert_array_equal(out[..., :24], state[..., :24])


def test_zero_initialized_ids_start_ignored_but_remain_available_to_learning():
    from flax.core import unfreeze, freeze
    c = ModelConfig(channels=48, input_channels=24, identifier_channels=16,
                    identifier_zero_init=True, gated=True, init_sigma=0.)
    tokens = jnp.ones((1, 5, 5), jnp.int32)
    a = initialize(tokens, jax.random.PRNGKey(1), c)
    b = initialize(tokens, jax.random.PRNGKey(2), c)
    assert np.any(np.asarray(a[..., 8:24]) != np.asarray(b[..., 8:24]))
    model = NCA(c); weights = unfreeze(init_params(model, a, jax.random.PRNGKey(3)))
    # A nonzero readout-producing update avoids a trivial zero-output test.
    weights['update']['kernel'] = jax.random.normal(jax.random.PRNGKey(4), weights['update']['kernel'].shape)*.05
    def evolve(params, state):
        for i in range(4):
            state, _ = step(model, params, state, tokens, jax.random.PRNGKey(10+i))
        return state[..., c.input_channels:]
    np.testing.assert_array_equal(evolve(freeze(weights), a), evolve(freeze(weights), b))
    kernel = weights['perception_kernel']
    weights['perception_kernel'] = kernel.at[..., 8:24, :].set(jax.random.normal(jax.random.PRNGKey(5), kernel[..., 8:24, :].shape)*.05)
    assert np.any(np.abs(np.asarray(evolve(freeze(weights), a)-evolve(freeze(weights), b))) > 1e-5)


def test_trajectory_ids_refresh_only_for_new_seeds_and_chunk_ids_always_refresh():
    from ncago.experiments.research_train import refresh_frozen_inputs
    c = ModelConfig(channels=48, input_channels=24, identifier_channels=16, init_sigma=0.)
    tokens = jnp.ones((2, 5, 5), jnp.int32)
    state = np.asarray(initialize(tokens, jax.random.PRNGKey(1), c)).copy()
    state[..., 24:] = .25
    fresh = np.array([True, False])
    key = jax.random.PRNGKey(2)
    continued = refresh_frozen_inputs(state.copy(), tokens, key, c, fresh, "trajectory")
    rerolled = refresh_frozen_inputs(state.copy(), tokens, key, c, fresh, "chunk")
    np.testing.assert_array_equal(continued[1], state[1])
    np.testing.assert_array_equal(continued[0, ..., :24], rerolled[0, ..., :24])
    assert np.any(rerolled[1, ..., 8:24] != state[1, ..., 8:24])
    np.testing.assert_array_equal(continued[..., 24:], state[..., 24:])
    np.testing.assert_array_equal(rerolled[..., 24:], state[..., 24:])


def test_split_tbptt_preserves_forward_states_losses_and_has_finite_truncated_gradients():
    from ncago.experiments.research_train import recurrent_objective
    c = ModelConfig(channels=32, heads=2, readout="ce", gated=True, init_sigma=.1,
                    normalization_groups=4)
    model = NCA(c); key = jax.random.PRNGKey(8)
    tokens = jnp.ones((1, 5, 5), jnp.int32)
    state = initialize(tokens, key, c)
    params = init_params(model, state, key)
    params = jax.tree_util.tree_map(lambda x: x+jax.random.normal(key, x.shape)*.02, params)
    full = {**DEFAULT, "max_depth":12, "late_steps":2, "gradient_window":12}
    short = {**full, "gradient_window":4}
    target = jnp.zeros_like(tokens)
    def objective(p, config, horizon):
        return recurrent_objective(model, c, config, p, state, tokens, target, key, horizon)
    for horizon in (3, 9, 12):
        a, b = objective(params, full, horizon), objective(params, short, horizon)
        for x, y in zip(jax.tree_util.tree_leaves(a), jax.tree_util.tree_leaves(b)):
            np.testing.assert_allclose(x, y, rtol=1e-6, atol=1e-7)
    a = jax.grad(lambda p: objective(p, full, 9)[0])(params)
    b = jax.grad(lambda p: objective(p, short, 9)[0])(params)
    assert all(np.all(np.isfinite(v)) for v in jax.tree_util.tree_leaves(b))
    assert any(np.max(np.abs(np.asarray(x-y))) > 1e-7 for x, y in zip(jax.tree_util.tree_leaves(a), jax.tree_util.tree_leaves(b)))


def test_five_witness_geometries_and_reference_dedup_cycles():
    data = witness_set(13, per_geometry=2)
    assert len(set(data["geometries"])) == 5
    assert data["boards"].shape == (20, 13, 13)
    for board, query, label in zip(data["boards"], data["queries"], data["labels"]):
        assert count_labels(board)[tuple(query)] == label
        ids = np.arange(board.size).reshape(board.shape)
        pred = identifier_reference(board, ids, steps=board.size, cap=4)
        np.testing.assert_array_equal(pred, count_labels(board))
        fast, _ = identifier_reference_fast(board, ids, steps=board.size, cap=4)
        np.testing.assert_array_equal(fast, pred)
    ring = data["boards"][-2]
    points, _ = group(ring, *data["queries"][-2])
    f = chain_features(ring)
    assert f[tuple(data["queries"][-2])][2] == 1
    assert len(points) > 20


def test_shared_multihorizon_rollout_matches_independent_exact_horizons():
    from ncago.experiments.research_eval import make_variable_predict, make_multi_variable_predict
    c = ModelConfig(channels=32, heads=2, readout="ce", gated=True, init_sigma=.1,
                    normalization_groups=4, input_channels=24, identifier_channels=16)
    model = NCA(c)
    tokens = jnp.ones((2, 5, 5), jnp.int32).at[:, 2, 2].set(0)
    key = jax.random.PRNGKey(8)
    state = initialize(tokens, key, c)
    params = init_params(model, state, key)
    params = jax.tree_util.tree_map(lambda x: x+jax.random.normal(key, x.shape)*.1, params)
    fire = jax.random.split(jax.random.PRNGKey(10), 2)
    ids = jax.random.split(jax.random.PRNGKey(11), 2)
    required = jnp.array([[1, 3], [5, 7], [9, 12]])
    multiple = make_multi_variable_predict(model, c)(params, tokens, fire, ids, required, 16)
    single = make_variable_predict(model, c)
    for row, prediction in zip(required, multiple):
        np.testing.assert_array_equal(prediction, single(params, tokens, fire, ids, row, 16))
    from ncago.experiments.research_media import trace
    states, predictions, dynamics = trace(model, c, params, tokens, fire, ids, (1, 5, 12))
    assert np.all(np.isfinite(states)) and dynamics.shape == (12, 2)
    for depth, prediction in zip((1, 5, 12), predictions):
        np.testing.assert_array_equal(prediction, single(params, tokens, fire, ids, jnp.full(2, depth), 16))


def test_graph_sum_max_share_parameter_shapes_and_finite_gradients():
    tokens = jnp.array([[[0, 1, 0, 0, 0], [1, 1, 1, 0, 0], [0, 1, 0, 0, 0], [0, 0, 0, 2, 0], [0, 0, 0, 0, 0]]])
    key = jax.random.PRNGKey(3)
    trees = []
    parameters = []
    for kind in ("gnn_sum", "gnn_max", "rcnn"):
        model, c = build_model({**DEFAULT, "model": kind, "channels": 16})
        state = initialize(tokens, key, c)
        params = init_params(model, state, key)
        def objective(p):
            final, _ = step(model, p, state, tokens, key)
            return balanced_loss(model.apply({"params": p}, final, method=model.logits), jnp.where(tokens > 0, 0, -1), 4)
        grad = jax.grad(objective)(params)
        assert all(np.all(np.isfinite(v)) for v in jax.tree_util.tree_leaves(grad))
        trees.append(jax.tree_util.tree_map(lambda x: x.shape, params))
        parameters.append(params)
    assert trees[0] == trees[1]
    for a, b in zip(jax.tree_util.tree_leaves(parameters[0]), jax.tree_util.tree_leaves(parameters[1])):
        np.testing.assert_array_equal(a, b)


def test_padded_diameter_batches_preserve_all_model_predictions_and_pair_keys():
    from ncago.experiments.research_eval import make_multi_variable_predict, variable_predictions
    tokens = np.zeros((6, 5, 5), np.int8)
    tokens[:, 1:4, 1:4] = 1
    for index in range(6):
        tokens[index, index % 3+1, index//3+1] = 0
    required = np.array([[1]*6, [1, 2, 2, 3, 4, 5], [1, 3, 3, 5, 7, 8]])
    key = jax.random.PRNGKey(89)
    for kind in ('nca', 'rcnn', 'gnn_sum', 'gnn_max', 'resnet'):
        model, c = build_model({**DEFAULT, 'model': kind, 'channels': 16,
            'identifier_channels': 16, 'normalization_groups': 4, 'identifier_input_scale': .25})
        state = initialize(jnp.asarray(tokens[:1]), key, c)
        params = (model.init(key, state[..., :c.input_channels])['params'] if kind == 'resnet'
                  else init_params(model, state, key))
        params = jax.tree_util.tree_map(lambda x: x+jax.random.normal(key, x.shape)*.1, params)
        predict = make_multi_variable_predict(model, c, kind == 'resnet')
        for paired in (False, True):
            expected = variable_predictions(predict, params, tokens, required, key,
                jax.random.PRNGKey(91), paired=paired, batch=4, pad_batches=False)
            observed = variable_predictions(predict, params, tokens, required, key,
                jax.random.PRNGKey(91), paired=paired, batch=4, pad_batches=True)
            np.testing.assert_array_equal(observed, expected)


def test_minimal_cycle_pairs_preserve_exact_liberty_sets_and_cavity_labels():
    from ncago.go.research_tasks import minimal_cycle_pair, eye_regions
    rng = np.random.default_rng(13)
    for inner in (False, True):
        a, b, q = minimal_cycle_pair(9, rng, inner)
        assert np.count_nonzero(a != b) == 1
        fa, fb = chain_features(a), chain_features(b)
        assert fa[q][2] == 1 and fb[q][2] == 0
        _, al = group(a, *q)
        _, bl = group(b, *q)
        np.testing.assert_array_equal(al, bl)
        assert eye_regions(a)[q] == eye_regions(b)[q] == int(inner)
    for size in (9, 37):
        for count in range(1, 17):
            a, b, q = minimal_cycle_pair(size, rng, inner_empty=False, liberty_count=count)
            assert count_labels(a, 16)[q] == count_labels(b, 16)[q] == count-1
            np.testing.assert_array_equal(group(a, *q)[1], group(b, *q)[1])


def test_eye_outcome_witness_holds_liberty_set_and_scales_past_radius32():
    from ncago.go.research_tasks import balanced_eye_cycle_pair, simple_eye_counts
    rng = np.random.default_rng(47)
    for size in (9, 37):
        for geometry in ("straight", "elbow", "snake", "comb", "branched"):
            a, b, q = balanced_eye_cycle_pair(size, rng, geometry)
            assert np.count_nonzero(a != b) == 1
            assert chain_features(a)[q][2] == 1 and chain_features(b)[q][2] == 0
            ap, al = group(a, *q); bp, bl = group(b, *q)
            assert len(ap) == len(bp)+1
            np.testing.assert_array_equal(al, bl)
            assert simple_eye_counts(a)[q] == 1 and simple_eye_counts(b)[q] == 0
            assert int(np.abs(np.argwhere(a != b)-q).max()) == size-3


def test_simple_eye_diagonal_checks_and_scaled_cycle_controls():
    from ncago.go.research_tasks import simple_eye_owners, simple_eye_counts, minimal_eye_cycle_pair
    board = np.ones((5, 5), np.int8); board[2, 2] = 0
    assert simple_eye_owners(board)[2, 2] == 1
    board[1, 1] = 2
    assert simple_eye_owners(board)[2, 2] == 1
    board[3, 3] = 2
    assert simple_eye_owners(board)[2, 2] == 0
    board = np.ones((5, 5), np.int8); board[0, 2] = 0; board[1, 1] = 2
    assert simple_eye_owners(board)[0, 2] == 0
    rng = np.random.default_rng(20)
    for n in (9, 37):
        for geometry in ("straight", "elbow", "snake", "comb", "branched"):
            a, b, q = minimal_eye_cycle_pair(n, rng, geometry)
            assert np.count_nonzero(a != b) == 1
            assert chain_features(a)[q][2] == 1 and chain_features(b)[q][2] == 0
            np.testing.assert_array_equal(group(a, *q)[1], group(b, *q)[1])
            assert simple_eye_counts(a)[q] == simple_eye_counts(b)[q] == 1


def test_regular_races_and_equal_liberty_outcome_changing_witness():
    from ncago.go.research_tasks import capture_race_board, balanced_capture_cycle_pair
    rng = np.random.default_rng(21)
    for n in (5, 9, 37):
        board, labels, answer = capture_race_board(n, rng)
        assert answer.winner is not None and answer.cutoff is None
        active = board != 3
        rr, cc = np.where(active)
        assert np.all(active[rr.min():rr.max()+1, cc.min():cc.max()+1])
        assert max(active.sum(0).max(), active.sum(1).max()) == n
        assert np.all(labels[labels >= 0] == {0: 2, 1: 0, 2: 1}[answer.winner])
        assert np.all(labels[board == 0] == -1)
    for turn in (1, 2):
        pair = balanced_capture_cycle_pair(37, rng, turn)
        assert pair is not None
        boards, q, labels, answers = pair
        assert labels[0] == 2 and labels[1] in (0, 1)
        assert np.count_nonzero(boards[0] != boards[1]) == 2
        for encoded in boards:
            board = np.where(encoded >= 4, np.where(encoded % 2 == 0, 1, 2), encoded)
            for anchor in np.argwhere(encoded >= 4):
                assert group(board, *anchor)[1].sum() == 6
        changed = np.argwhere(boards[0] != boards[1])
        assert max(np.abs(changed-np.array(q)).max(axis=1)) > 32


def test_capture_race_legal_search_and_cutoffs_are_unknown():
    from ncago.go.research_tasks import solve_capture_race
    board = np.ones((5, 5), np.int8)
    board[:, 3:] = 2
    board[:, 2] = 3
    board[2, 2] = 0
    # Both target groups have the same one shared liberty. Either player
    # wins by filling it and capturing the opposing group immediately.
    for color in (1, 2):
        result = solve_capture_race(board, (2, 1), (2, 3), color)
        assert result.winner == color
        assert result.principal_variation[0] == (2, 2)
    unknown = solve_capture_race(board, (2, 1), (2, 3), max_nodes=0)
    assert unknown.winner is None and unknown.cutoff is not None
    from ncago.go.research_tasks import capturing_cycle_pair
    rng = np.random.default_rng(14)
    for count in (1, 2, 4):
        for color in (1, 2):
            pair = capturing_cycle_pair(9, rng, count, color)
            assert pair is not None
            expected = color-1 if count == 1 else 0
            assert pair[2] == [expected, expected]


def test_race_input_encodes_only_supplied_anchors_and_turn():
    from ncago.nca.model import frozen_inputs
    c = ModelConfig(channels=32)
    tokens = jnp.ones((1, 5, 5), jnp.int32).at[0, 2, 1].set(6).at[0, 2, 3].set(7)
    inputs = np.asarray(frozen_inputs(tokens, jax.random.PRNGKey(0), c))
    assert inputs[0, 2, 1, 1] == 1
    assert inputs[0, 2, 3, 2] == 1
    assert inputs[..., 4].sum() == inputs[..., 5].sum() == 1
    assert np.all(inputs[..., 6] == 1)
    assert np.all(inputs[..., 7] == 0)


def test_variable_depth_evaluation_matches_separate_coupled_rollouts():
    from ncago.experiments.research_eval import make_variable_predict, make_coupled_predict
    from ncago.experiments.research_train import make_predict
    c = ModelConfig(channels=32, heads=2, readout="ce", gated=True, init_sigma=0.)
    model = NCA(c)
    tokens = jnp.ones((2, 5, 5), jnp.int32)
    keys = jax.random.split(jax.random.PRNGKey(11), 2)
    state = initialize(tokens, keys[0], c)
    params = init_params(model, state, keys[0])
    params = jax.tree_util.tree_map(lambda x: x+jax.random.normal(keys[0], x.shape)*.02, params)
    variable = make_variable_predict(model, c)
    regular = make_predict(model, c)
    batched = np.asarray(variable(params, tokens, keys, keys, jnp.array([3, 7]), 8))
    for index, depth in enumerate((3, 7)):
        single, _ = regular(params, tokens[index:index+1], keys[index], (depth,), keys[index])
        np.testing.assert_array_equal(batched[index], np.asarray(single)[0, 0])
    coupled = np.asarray(make_coupled_predict(regular)(params, tokens, keys, keys, (3, 7)))
    for index in range(2):
        single, _ = regular(params, tokens[index:index+1], keys[index], (3, 7), keys[index])
        np.testing.assert_array_equal(coupled[:, index], np.asarray(single)[:, 0])
