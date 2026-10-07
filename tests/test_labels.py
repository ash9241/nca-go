import numpy as np
from ncago.go.rules import Position, chains
from ncago.go.labels import liberties, benson, read_ladder
from ncago.go.generators import random_position, living, structured, ring_pair
from ncago.baselines.local import liberty_ca


def test_liberty_ca_distinct_ids_and_diameter():
    for size in (5,9):
        rng = np.random.default_rng(9)
        for b in (random_position(size,rng), structured(size,rng,"ring"), structured(size,rng,"snake")):
            expected, info = liberties(b)
            predictions, steps = liberty_ca(b)
            np.testing.assert_array_equal(predictions[-1], expected)
            assert all(s is not None for s in steps)


def test_benson_eyes():
    rng = np.random.default_rng(12)
    b = living(9,rng,True)
    y, _ = benson(b)
    assert np.any((y == 0)|(y == 1))
    b = np.zeros((9,9), np.int8)
    b[2:5,2:7] = 1
    b[3,3:6] = 0
    assert not np.any(benson(b)[0] == 0)
    b[2,3] = 0  # open false eye
    assert not np.any(benson(b)[0] == 0)


def test_pass_alive_survives_opponent_playouts():
    rng = np.random.default_rng(40)
    b = living(5,rng,True)
    labels,_ = benson(b)
    alive = (labels == 0)|(labels == 1)
    color = int(b[alive][0])
    for _ in range(30):
        p = Position(b.copy(), 3-color)
        for _ in range(25):
            moves = p.legal_moves()
            p = p.play(moves[int(rng.integers(len(moves)))]).play(None)
        assert np.all(p.board[alive] == color)


def test_ladder_escape_capture_and_cutoff():
    b = np.zeros((5,5), np.int8)
    b[0,0] = 1
    b[0,1] = 2
    result = read_ladder(Position(b), (0,0), True)
    assert result.captured is True
    b = np.zeros((5,5), np.int8)
    b[2,2] = 1
    b[1,2] = b[2,1] = 2
    result = read_ladder(Position(b), (2,2), False, max_depth=0)
    assert result.captured is None
    b[1,2] = 0
    assert read_ladder(Position(b), (2,2), False).captured is False


def test_benson_seki_and_color_symmetry():
    b = np.zeros((7,7),np.int8)
    b[:5,:3] = 1
    b[:5,4:] = 2
    b[2,1] = b[2,5] = 0
    b[0,3] = b[2,3] = 1
    b[4,3] = 2
    y,_ = benson(b)
    assert np.all(y[b != 0] == 2)
    swapped = np.where(b == 1,2,np.where(b == 2,1,b)).astype(np.int8)
    sy,_ = benson(swapped)
    np.testing.assert_array_equal(sy,y)


def test_matched_pair():
    ring, path, color = ring_pair(9,np.random.default_rng(2))
    assert abs(np.count_nonzero(ring==color)-np.count_nonzero(path==color)) == 1
    a, _ = liberties(ring)
    b, _ = liberties(path)
    common = (ring==color)&(path==color)
    np.testing.assert_array_equal(a[common],b[common])
