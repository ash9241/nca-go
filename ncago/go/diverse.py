"""Varied connected chains and component-level symmetry keys."""
import numpy as np
from .rules import chains, legalize, neighbors


def random_controlled_chain(size, rng, return_metadata=False):
    target = int(rng.integers(1, 5))
    for _ in range(500):
        color = int(rng.integers(1, 3))
        points = {tuple(map(int, rng.integers(size, size=2)))}
        length = int(rng.integers(1, max(2, int(.65*size*size))))
        frontier = set(neighbors(next(iter(points)), size)) - points
        while len(points) < length and frontier:
            point = list(sorted(frontier))[int(rng.integers(len(frontier)))]
            points.add(point)
            frontier |= set(neighbors(point, size))
            frontier -= points
        board = np.zeros((size, size), np.int8)
        for point in points:
            board[point] = color
        chain = chains(board)[0]
        if len(chain.liberties) < target:
            continue
        available = sorted(chain.liberties)
        rng.shuffle(available)
        for point in available[target:]:
            board[point] = 3-color
        board = legalize(board)
        remaining = next((c for c in chains(board) if c.color == color), None)
        if remaining and set(remaining.points) == points and len(remaining.liberties) == target:
            metadata = {"color": color, "points": tuple(sorted(points)), "target_liberties": target}
            return (board, metadata) if return_metadata else board
    raise RuntimeError("Failed to construct a legal random connected chain")


def component_key(board, points):
    """Ignore translation and inputs the chain-message model cannot observe.

    Keep the component and its complete static 3x3 neighborhoods. Encode real
    array padding separately from frozen off-board cells; ignore farther input.
    """
    points = np.asarray(points)
    lo, hi = points.min(0)-1, points.max(0)+2
    crop = np.full(tuple(hi-lo), 4, np.int8)
    h, w = board.shape
    for r, c in points:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = int(r+dr), int(c+dc)
                crop[rr-lo[0], cc-lo[1]] = board[rr, cc] if 0 <= rr < h and 0 <= cc < w else 5
    forms = []
    for rotation in range(4):
        rotated = np.rot90(crop, rotation)
        for form in (rotated, rotated[::-1]):
            shape = np.array(form.shape, np.int16).tobytes()
            forms.append(shape+form.tobytes())
            swapped = np.where(form == 1, 2, np.where(form == 2, 1, form)).astype(np.int8)
            forms.append(shape+swapped.tobytes())
    return b"component:"+min(forms)
