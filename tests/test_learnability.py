import numpy as np
import pytest

from ncago.experiments.learnability import balanced_targets, scores, locality_witness
from ncago.go.generators import canonical_key
from ncago.go.labels import liberties
from ncago.go.rules import chains


def test_balanced_exact_targets_and_disjoint_splits():
    boards, targets, _ = balanced_targets(9, 8, 73001)
    seen = {canonical_key(b) for b in boards}
    held_out, _, _ = balanced_targets(9, 8, 73002, seen)
    assert not seen.intersection(canonical_key(b) for b in held_out)
    counts = np.zeros(4, int)
    for board, target in zip(boards, targets):
        exact, _ = liberties(board)
        mask = target >= 0
        np.testing.assert_array_equal(target[mask], exact[mask])
        assert sum(any(mask[p] for p in chain.points) for chain in chains(board)) == 1
        counts[int(target[mask][0])] += 1
    np.testing.assert_array_equal(counts, [2, 2, 2, 2])


def test_metrics_do_not_reward_majority_guessing():
    target = np.array([[[0, -1]], [[1, -1]], [[2, -1]], [[3, -1]]])
    result = scores(np.full(target.shape, 3), target)
    assert result["macro_stone_accuracy"] == result["target_chain_exact"] == .25
    assert scores(target, target)["target_chain_exact"] == 1
    with pytest.raises(FloatingPointError):
        scores(np.full(target.shape, -2), target)


def test_multisize_padding_preserves_exact_labels():
    boards, targets, info = balanced_targets(9, 24, 914, board_sizes=(5, 7, 9))
    assert len({m["board_size"] for m in info}) > 1
    for board, target in zip(boards, targets):
        exact, _ = liberties(board)
        np.testing.assert_array_equal(target[target >= 0], exact[target >= 0])
        assert np.all(target[board == 3] == -1)
    with pytest.raises(ValueError):
        balanced_targets(9, 8, 1, board_sizes=(13,))


def test_locality_witness_changes_only_beyond_receptive_field():
    one, two, query, distance = locality_witness(13)
    changes = np.argwhere(one != two)
    assert min(np.max(np.abs(point-np.asarray(query))) for point in changes) == distance
    for board in (one, two):
        assert all(len(chain.liberties) > 0 for chain in chains(board))
    exact_one, _ = liberties(one)
    exact_two, _ = liberties(two)
    assert (exact_one[query], exact_two[query]) == (0, 1)
    assert distance > 9  # Four-block reference CNN has radius nine.
