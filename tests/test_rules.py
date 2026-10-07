import numpy as np
import pytest
from sgfmill import boards
from ncago.go.rules import Position, IllegalMove, chains, legalize, diameter
from ncago.go.generators import random_position, generate,canonical_key


def test_capture_suicide_ko():
    b = np.zeros((5,5), np.int8)
    b[1,1] = 2
    b[0,1] = b[1,0] = b[2,1] = 1
    p = Position(b).play((1,2), 1)
    assert p.board[1,1] == 0
    b = np.zeros((5,5), np.int8)
    b[0,1] = b[1,0] = b[1,2] = b[2,1] = 2
    with pytest.raises(IllegalMove):
        Position(b).play((1,1), 1)
    b = np.zeros((5,5), np.int8)
    b[1,1] = 2
    b[0,1] = b[1,0] = b[2,1] = 1
    b[0,2] = b[2,2] = b[1,3] = 2
    p = Position(b).play((1,2), 1)
    with pytest.raises(IllegalMove):
        p.play((1,1), 2)
    p.play(None).play(None).play((1,1), 2)
    p = Position(b, superko=True).play((1,2), 1).play(None).play(None)
    with pytest.raises(IllegalMove):
        p.play((1,1), 2)


def test_scoring_and_input_immutability():
    p = Position.empty(5)
    q = p.play((0,0))
    assert not p.board.any()
    assert q.score() == 25-7.5
    assert Position.empty(5).score() == -7.5
    with pytest.raises(IllegalMove):
        q.play((0,0))


@pytest.mark.parametrize("size", [5,9,19,37])
def test_generator_and_chains(size):
    a = random_position(size, np.random.default_rng(7), .3)
    b = random_position(size, np.random.default_rng(7), .3)
    assert np.array_equal(a,b)
    assert all(c.liberties for c in chains(a))
    assert sum(len(c.points) for c in chains(a)) == np.count_nonzero(a)


def test_sgfmill_replay():
    rng = np.random.default_rng(14)
    for size in (9,19):
        p, reference = Position.empty(size), boards.Board(size)
        for _ in range(size*size*2):
            moves = p.legal_moves()
            move = moves[int(rng.integers(len(moves)))]
            color = p.to_move
            p = p.play(move)
            if move is not None:
                reference.play(*move, "b" if color == 1 else "w")
            actual = np.array([[{None:0,"b":1,"w":2}[reference.get(r,c)] for c in range(size)] for r in range(size)])
            np.testing.assert_array_equal(p.board, actual)


def test_synthetic_splits_exclude_augmented_duplicates():
    train,_ = generate("benson",9,20,100)
    exclusion = {canonical_key(b) for b in train}
    test,_ = generate("benson",9,20,101,exclude=exclusion)
    assert not exclusion.intersection(canonical_key(b) for b in test)
    # Rotations and color swaps of a board are the same partition identity.
    swapped = np.where(train[0] == 1,2,np.where(train[0] == 2,1,train[0])).astype(np.int8)
    assert canonical_key(np.rot90(swapped)) == canonical_key(train[0])
