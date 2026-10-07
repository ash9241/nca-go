"""Static simple-eye counts and precisely defined two-group capture games.

Simple eyes include the diagonal false-eye checks, but do not establish
Benson life. Capture races use legal search; exhausted budgets stay unknown.
"""
from dataclasses import dataclass
import numpy as np
from numba import njit
from .rules import group, play_array, legalize
from .research_data import count_labels


@njit(cache=True)
def simple_eye_owners(board):
    """Static simple-eye pattern used by KataGo's Board::isSimpleEye.

    All orthogonal neighbors are friendly or walls. Two opposing diagonals
    invalidate an interior point; one invalidates an edge/corner point.
    This is a local shape definition, not unconditional life.
    """
    n = len(board)
    owners = np.zeros(board.shape, np.int8)
    for r in range(n):
        for c in range(n):
            if board[r, c] != 0:
                continue
            color, wall, valid = 0, False, True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r+dr, c+dc
                if not (0 <= rr < n and 0 <= cc < n) or board[rr, cc] == 3:
                    wall = True
                    continue
                value = board[rr, cc]
                if value == 0 or (color and value != color):
                    valid = False
                color = value if not color else color
            if not valid or color not in (1, 2):
                continue
            opposing = 0
            for dr, dc in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                rr, cc = r+dr, c+dc
                if 0 <= rr < n and 0 <= cc < n and board[rr, cc] == 3-color:
                    opposing += 1
            if opposing < 2 and not (wall and opposing):
                owners[r, c] = color
    return owners


@njit(cache=True)
def simple_eye_counts(board, cap=8):
    """Count distinct adjacent simple-eye points per connected stone chain."""
    owners = simple_eye_owners(board)
    labels = np.full(board.shape, -1, np.int32)
    for r in range(len(board)):
        for c in range(len(board)):
            if board[r, c] in (1, 2) and labels[r, c] < 0:
                points, liberties = group(board, r, c)
                count = min(cap, int(((owners == board[r, c]) & liberties).sum()))
                for rr, cc in points:
                    labels[rr, cc] = count
    return labels


def eye_regions(board, cap=8):
    """Count interior empty components bordered by exactly one stone chain.

    Exterior/off-board components do not count. False-eye tactics and region
    vitalness are intentionally outside this diagnostic label definition.
    """
    n = len(board)
    chain_ids = np.full(board.shape, -1, np.int32)
    chains = []
    for r, c in np.argwhere((board == 1) | (board == 2)):
        if chain_ids[r, c] >= 0:
            continue
        points, _ = group(board, r, c)
        index = len(chains)
        for rr, cc in points:
            chain_ids[rr, cc] = index
        chains.append(points)
    seen = set()
    counts = np.zeros(len(chains), np.int32)
    for start in map(tuple, np.argwhere(board == 0)):
        if start in seen:
            continue
        pending, boundary, exterior = [start], set(), False
        seen.add(start)
        while pending:
            r, c = pending.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r+dr, c+dc
                if not (0 <= rr < n and 0 <= cc < n) or board[rr, cc] == 3:
                    exterior = True
                elif board[rr, cc] == 0 and (rr, cc) not in seen:
                    seen.add((rr, cc))
                    pending.append((rr, cc))
                elif board[rr, cc] in (1, 2):
                    boundary.add(int(chain_ids[rr, cc]))
        if not exterior and len(boundary) == 1:
            counts[next(iter(boundary))] += 1
    labels = np.full(board.shape, -1, np.int32)
    for points, count in zip(chains, counts):
        for r, c in points:
            labels[r, c] = min(cap, count)
    return labels


def eye_board(size, rng):
    board = np.zeros((size, size), np.int8)
    color = int(rng.integers(1, 3))
    lo = int(rng.integers(0, 2))
    hi = size-1-int(rng.integers(0, 2))
    board[lo:hi+1, lo:hi+1] = color
    candidates = [(r, c) for r in range(lo+1, hi, 2) for c in range(lo+1, hi, 2)]
    desired = int(rng.integers(0, min(8, len(candidates))+1))
    for index in rng.choice(len(candidates), desired, replace=False):
        board[candidates[index]] = 0
    # With zero holes, allow the surround to provide legal liberties.
    if not np.any(board == 0):
        board[0] = 0
    return legalize(board)


def minimal_eye_cycle_pair(size, rng, geometry="snake"):
    """A three-cell ring with a long tree tail; one corner breaks its cycle.

    The ring encloses a genuine static simple-eye point. The color change
    preserves its diagonal pattern, exact liberty set and eye count, while
    changing the query chain from cyclic to acyclic.
    """
    if size < 9:
        raise ValueError("Scaled eye-cycle controls require size >=9")
    board = np.full((size, size), 2, np.int8)
    hi = size-2
    board[1, 1:4] = board[3, 1:4] = 1
    board[1:4, 1] = board[1:4, 3] = 1
    board[2, 2] = board[0, 0] = 0
    board[1, 4:hi+1 if geometry != "branched" else 6] = 1
    if geometry == "elbow":
        board[1:hi+1, hi] = 1
    elif geometry == "snake":
        previous = hi
        for index, r in enumerate(range(3, hi+1, 2)):
            board[r-1, previous] = 1
            board[r, 5:hi+1] = 1
            previous = 5 if index % 2 == 0 else hi
    elif geometry == "comb":
        board[1:hi+1, 5] = 1
        board[3:hi+1:2, 5:hi+1] = 1
    elif geometry == "branched":
        board[1:hi+1, 5] = 1
        board[size//2, 5:hi+1] = 1
    elif geometry != "straight":
        raise ValueError(geometry)
    points, _ = group(board, 1, 1)
    distance = np.abs(points-np.asarray([2, 2])).sum(1)
    query = tuple(points[int(rng.choice(np.flatnonzero(distance == distance.max())))])
    other = board.copy(); other[3, 1] = 2
    if simple_eye_counts(board)[query] != 1 or simple_eye_counts(other)[query] != 1:
        raise AssertionError("Eye-cycle control lost its eye")
    marks = np.zeros_like(board); marks[query] = 1
    rotation = int(rng.integers(4))
    board, other, marks = [np.rot90(a, rotation).copy() for a in (board, other, marks)]
    if rng.random() < .5:
        board, other, marks = [a[::-1].copy() for a in (board, other, marks)]
    if rng.random() < .5:
        board, other = [np.where(a == 1, 2, np.where(a == 2, 1, a)).astype(np.int8) for a in (board, other)]
    return board, other, tuple(np.argwhere(marks == 1)[0])


def balanced_eye_cycle_pair(size, rng, geometry="snake"):
    """Change a corner simple eye from one to zero at fixed liberties.

    Removing the diagonal shortcut also breaks the stone-graph cycle.
    This is an outcome-changing witness, not a cycle-only causal control.
    """
    if size < 9:
        raise ValueError("Scaled corner-eye witnesses require size >=9")
    board = np.full((size, size), 2, np.int8)
    hi = size-2
    board[0, 1:4] = board[3, :4] = 1
    board[1:4, 0] = board[:4, 3] = 1
    board[1, 1] = 1
    board[0, 0] = board[2, 2] = board[-1, -1] = 0
    board[3, 4:hi+1 if geometry != "branched" else 6] = 1
    if geometry == "elbow":
        board[3:hi+1, hi] = 1
    elif geometry == "snake":
        previous = hi
        for index, r in enumerate(range(5, hi+1, 2)):
            board[r-1, previous] = 1
            board[r, 5:hi+1] = 1
            previous = 5 if index % 2 == 0 else hi
    elif geometry == "comb":
        board[3:hi+1, 5] = 1
        board[5:hi+1:2, 5:hi+1] = 1
    elif geometry == "branched":
        board[3:hi+1, 5] = 1
        board[max(5, size//2), 5:hi+1] = 1
    elif geometry != "straight":
        raise ValueError(geometry)
    points, liberties = group(board, 3, 3)
    distance = np.abs(points-np.asarray([1, 1])).max(1)
    query = tuple(points[int(rng.choice(np.flatnonzero(distance == distance.max())))])
    other = board.copy(); other[1, 1] = 2
    other_points, other_liberties = group(other, *query)
    if len(other_points) != len(points)-1 or not np.array_equal(liberties, other_liberties):
        raise AssertionError("Corner-eye witness changed connectivity or liberties")
    if simple_eye_counts(board)[query] != 1 or simple_eye_counts(other)[query] != 0:
        raise AssertionError("Corner-eye witness lost its one-versus-zero labels")
    marks = np.zeros_like(board); marks[query] = 1
    rotation = int(rng.integers(4))
    board, other, marks = [np.rot90(a, rotation).copy() for a in (board, other, marks)]
    if rng.random() < .5:
        board, other, marks = [a[::-1].copy() for a in (board, other, marks)]
    if rng.random() < .5:
        board, other = [np.where(a == 1, 2, np.where(a == 2, 1, a)).astype(np.int8) for a in (board, other)]
    return board, other, tuple(np.argwhere(marks == 1)[0])


def minimal_cycle_pair(size, rng, inner_empty=True, liberty_count=None):
    """Break a pure ring at a corner with a single stone-color change.

    The corner has no empty orthogonal neighbor, so the query chain keeps
    exactly the same liberty SET, remains connected, and keeps its cavity
    count. This controls labels beyond simply preserving a capped class.
    """
    board = np.zeros((size, size), np.int8)
    lo, hi = 1, size-2
    board[lo, lo:hi+1] = board[hi, lo:hi+1] = 1
    board[lo:hi+1, lo] = board[lo:hi+1, hi] = 1
    corner = (lo, lo)
    board[lo-1, lo] = board[lo, lo-1] = 2
    if not inner_empty:
        # A separate perturbation family has no cavity on either side.
        board[lo+1:hi, lo+1:hi] = 2
        board[(lo+hi)//2, (lo+hi)//2] = 0
        if liberty_count is not None:
            _, free = group(board, hi, hi)
            options = np.argwhere(free)
            if not 1 <= liberty_count <= len(options):
                raise ValueError("Unsupported exact liberty count for this ring")
            board[free] = 2
            keep = options[rng.choice(len(options), liberty_count, replace=False)]
            for r, c in keep:
                board[r, c] = 0
    board = legalize(board)
    broken = board.copy()
    broken[corner] = 2
    broken = legalize(broken)
    query = hi, hi
    one_points, one_libs = group(board, *query)
    two_points, two_libs = group(broken, *query)
    if not np.array_equal(one_libs, two_libs) or len(two_points) != len(one_points)-1:
        raise AssertionError("Minimal cycle pair did not preserve query liberties and connectedness")
    if eye_regions(board)[query] != eye_regions(broken)[query]:
        raise AssertionError("Minimal cycle pair changed cavity count")
    rotation = int(rng.integers(4))
    marker = np.zeros_like(board)
    marker[query] = 1
    board, broken, marker = [np.rot90(x, rotation).copy() for x in (board, broken, marker)]
    if rng.random() < .5:
        board, broken, marker = [x[::-1].copy() for x in (board, broken, marker)]
    if rng.random() < .5:
        board, broken = [np.where(x == 1, 2, np.where(x == 2, 1, x)).astype(np.int8) for x in (board, broken)]
    return board, broken, tuple(np.argwhere(marker == 1)[0])


@dataclass
class CaptureRace:
    winner: int | None  # 1 Black, 2 White, 0 draw, None unknown.
    nodes: int
    principal_variation: tuple
    cutoff: str | None


def solve_capture_race(board, black_anchor, white_anchor, to_move=1, max_nodes=20000, max_depth=24):
    """Enclosed legal Go capture game: first target-chain capture wins.

    All empty cells on the supplied board are playable. Off-board cells are
    walls. Simple ko is checked; two consecutive passes are a draw. Repeated
    search states and budget/depth cutoffs remain unknown. This is a precise
    bounded diagnostic, not an unrestricted semeai adjudicator.
    """
    if board[black_anchor] != 1 or board[white_anchor] != 2:
        raise ValueError("Anchor colors must identify the two initial groups")
    nodes, memo, active = 0, {}, set()
    def search(current, previous, color, passes, depth):
        nonlocal nodes
        nodes += 1
        if current[black_anchor] != 1:
            return 2, ()
        if current[white_anchor] != 2:
            return 1, ()
        if passes == 2:
            return 0, ()
        if nodes > max_nodes or depth >= max_depth:
            return None, ()
        key = current.tobytes(), previous, color, passes
        if key in active:
            return None, ()
        memo_key = key+(max_depth-depth,)
        if memo_key in memo:
            return memo[memo_key]
        # Find terminal target captures before exploring moves that merely
        # capture support stones and create many new empty cells.
        for move in map(tuple, np.argwhere(current == 0)):
            child, legal = play_array(current, *move, color)
            if legal and child.tobytes() != previous:
                enemy_anchor, enemy_color = (white_anchor, 2) if color == 1 else (black_anchor, 1)
                if child[enemy_anchor] != enemy_color:
                    answer = color, (move,)
                    memo[memo_key] = answer
                    return answer
        active.add(key)
        outcomes = []
        moves = list(map(tuple, np.argwhere(current == 0)))+[None]
        # Captures before passes improve pruning without changing the rules.
        for move in moves:
            if nodes >= max_nodes:
                outcomes.append((None, ()))
                break
            if move is None:
                child, next_passes = current.copy(), passes+1
            else:
                child, legal = play_array(current, *move, color)
                if not legal or child.tobytes() == previous:
                    continue
                next_passes = 0
            winner, pv = search(child, current.tobytes(), 3-color, next_passes, depth+1)
            outcomes.append((winner, (move,)+pv))
            if winner == color:
                break
        active.remove(key)
        win = next((x for x in outcomes if x[0] == color), None)
        draw = next((x for x in outcomes if x[0] == 0), None)
        if win is not None:
            answer = win
        elif any(x[0] is None for x in outcomes):
            answer = None, max((x[1] for x in outcomes), key=len, default=())
        elif draw is not None:
            answer = draw
        else:
            answer = 3-color, max((x[1] for x in outcomes), key=len, default=())
        memo[memo_key] = answer
        return answer
    winner, pv = search(board.copy(), None, to_move, 0, 0)
    return CaptureRace(winner, nodes, pv, "search budget, depth or repetition" if winner is None else None)


def capture_race_board(size, rng, max_nodes=20000):
    """Regular 5×N rectangular Go races, with no internal wall intersections.

    Chain length grows with N. Only padding outside the rectangle is wall.
    Labels are first-capture outcomes with pass, suicide and simple-ko rules.
    """
    for _ in range(100):
        local = np.ones((size, 5), np.int8)
        local[:, 3:] = 2
        local[:, 2] = rng.integers(1, 3, size=size)
        rows = rng.choice(size, int(rng.integers(1, 5)), replace=False)
        local[rows, 2] = 0
        # Add up to two exclusive liberties on either side.
        for color, col in ((1, 0), (2, 4)):
            for row in rng.choice(size, int(rng.integers(0, 3)), replace=False):
                local[row, col] = 0
        black, white = (size//2, 1), (size//2, 3)
        to_move = int(rng.integers(1, 3))
        board = np.full((size, size), 3, np.int8)
        col = int(rng.integers(size-4))
        board[:, col:col+5] = local
        black, white = (black[0], black[1]+col), (white[0], white[1]+col)
        answer = solve_capture_race(board, black, white, to_move, max_nodes=max_nodes)
        if answer.winner is None:
            continue
        target = np.full(board.shape, -1, np.int32)
        value = {1: 0, 2: 1, 0: 2}[answer.winner]
        for anchor in (black, white):
            points, _ = group(board, *anchor)
            for r, c in points:
                target[r, c] = value
        # Mark anchors and to-move without exposing a computed group graph.
        board[black], board[white] = (4, 5) if to_move == 1 else (6, 7)
        rotation = int(rng.integers(4))
        return np.rot90(board, rotation).copy(), np.rot90(target, rotation).copy(), answer
    raise RuntimeError("Could not obtain a proved capture-race label within search budgets")


def balanced_capture_cycle_pair(size, rng, to_move=1, max_nodes=100000):
    """Two-point-eye/cycle perturbation at fixed 6-vs-6 liberty counts.

    This is an outcome-changing witness, separate from invariant controls.
    Both labels are proved independently; no tactical result is assumed.
    """
    if size < 7:
        raise ValueError("Balanced race witnesses require size >=7")
    one = np.full((size, size), 2, np.int8)
    one[:size-1, 1] = 1
    one[1, 0] = one[3, 0] = 1
    one[0, 0] = one[2, 0] = 0
    one[:4, 2] = 0
    one[0, 5] = one[2, 5] = 0
    two = one.copy(); two[1, 0] = 0; two[2, 0] = 1
    black, white = (size-2, 1), (2, 3)
    answers = [solve_capture_race(b, black, white, to_move, max_nodes=max_nodes) for b in (one, two)]
    if any(a.winner is None for a in answers):
        return None
    marks = np.zeros_like(one); marks[black] = 1
    boards = []
    for b in (one, two):
        b = b.copy(); b[black], b[white] = (4, 5) if to_move == 1 else (6, 7)
        boards.append(b)
    labels = [{1: 0, 2: 1, 0: 2}[a.winner] for a in answers]
    rotation = int(rng.integers(4))
    boards = [np.rot90(b, rotation).copy() for b in boards]
    marks = np.rot90(marks, rotation)
    if rng.random() < .5:
        boards = [b[::-1].copy() for b in boards]; marks = marks[::-1]
    if rng.random() < .5:
        mapping = np.array([0, 2, 1, 3, 7, 6, 5, 4], np.int8)
        boards = [mapping[b] for b in boards]
        labels = [1-y if y < 2 else y for y in labels]
    return boards, tuple(np.argwhere(marks == 1)[0]), labels, answers


def capturing_cycle_pair(size, rng, liberty_count=2, to_move=1, max_nodes=20000):
    """Two target groups in a cyclic race, with fixed supporting opponent stones.

    Exactly solve both sides. A cycle break alone is never assumed to preserve
    the race label. These remain synthetic enclosed diagnostics, not FAR SGFs.
    """
    one, two, black = minimal_cycle_pair(size, rng, inner_empty=False, liberty_count=liberty_count)
    # Recover named color roles after the common random color swap.
    if one[black] == 2:
        one, two = [np.where(x == 1, 2, np.where(x == 2, 1, x)).astype(np.int8) for x in (one, two)]
    white = size//2, size//2
    if one[white] == 0:
        white = size//2, size//2+1
    if one[white] != 2:
        # Rotation on even boards can shift the eye center by one.
        candidates = np.argwhere(one == 2)
        white = min(map(tuple, candidates), key=lambda q: abs(q[0]-size//2)+abs(q[1]-size//2))
    answers = [solve_capture_race(b, black, white, to_move, max_nodes=max_nodes) for b in (one, two)]
    if any(a.winner is None for a in answers):
        return None
    boards = []
    for b in (one, two):
        encoded = b.copy()
        encoded[black], encoded[white] = (4, 5) if to_move == 1 else (6, 7)
        boards.append(encoded)
    labels = [{1: 0, 2: 1, 0: 2}[a.winner] for a in answers]
    return boards, black, labels, answers
