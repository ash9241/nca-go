"""Independent exact labels. Search cutoffs are unknown, never inferred escape."""
from dataclasses import dataclass
import numpy as np
from .rules import chains, diameter, neighbors, Position, IllegalMove


def liberties(board):
    labels = np.full(board.shape, -1, np.int32)
    distance = np.zeros(board.shape, np.int32)
    for chain in chains(board):
        value = min(4, len(chain.liberties))-1
        d = diameter(chain)+1
        for p in chain.points:
            labels[p], distance[p] = value, d
    return labels, {"distance": distance}


def benson(board):
    labels = np.full(board.shape, -1, np.int32)
    labels[board != 0] = 2
    iterations = 0
    chain_list = chains(board)
    diam = max((diameter(c) for c in chain_list), default=0)
    for color in (1, 2):
        own = [c for c in chain_list if c.color == color]
        point_chain = {p: i for i, c in enumerate(own) for p in c.points}
        regions, boundaries, vital = [], [], []
        seen = set()
        for p in map(tuple, np.argwhere(board != color).tolist()):
            if p in seen:
                continue
            region, boundary, todo = set(), set(), [p]
            while todo:
                q = todo.pop()
                if q in region:
                    continue
                region.add(q)
                for adjacent in neighbors(q, len(board)):
                    if board[adjacent] == color:
                        boundary.add(point_chain[adjacent])
                    elif adjacent not in region:
                        todo.append(adjacent)
            seen.update(region)
            empty = {q for q in region if board[q] == 0}
            if boundary and empty:
                regions.append(region)
                boundaries.append(boundary)
                vital.append({i for i in boundary if empty <= own[i].liberties})
        x, r = set(range(len(own))), set(range(len(regions)))
        count = 0
        while True:
            xx = {i for i in x if sum(i in vital[j] for j in r) >= 2}
            rr = {j for j in r if boundaries[j] <= xx}
            count += 1
            if xx == x and rr == r:
                break
            x, r = xx, rr
        iterations = max(iterations, count)
        for i in x:
            for p in own[i].points:
                labels[p] = color-1
    return labels, {"iterations": iterations, "diameter": diam,
                    "distance": np.full(board.shape, max(1, diam*iterations), np.int32)}


@dataclass
class LadderResult:
    captured: bool | None
    variation: tuple
    nodes: int
    cutoff: str | None = None


def read_ladder(position, anchor, defender_to_move, max_depth=None, max_nodes=100000):
    color = int(position.board[anchor])
    if color == 0:
        raise ValueError("Defender must be a stone")
    attacker = 3-color
    limit = len(position.board)**2 if max_depth is None else max_depth
    memo, active = {}, set()
    node_count = 0

    def search(pos, defending, depth):
        nonlocal node_count
        node_count += 1
        if pos.board[anchor] != color:
            return True, ()
        chain = next(c for c in chains(pos.board) if anchor in c.points)
        if len(chain.liberties) >= 3:
            return False, ()
        if depth >= limit or node_count >= max_nodes:
            return None, ()
        key = (pos.board.tobytes(), pos.previous, defending, limit-depth)
        cycle_key = key[:3]
        if cycle_key in active:
            return None, ()
        if key in memo:
            return memo[key]
        active.add(cycle_key)
        moves = set(chain.liberties)
        if defending:
            for enemy in chains(pos.board):
                if enemy.color == attacker and len(enemy.liberties) == 1 and any(
                    q in chain.points for p in enemy.points for q in neighbors(p, len(pos.board))):
                    moves.update(enemy.liberties)
        outcomes = []
        for p in sorted(moves):
            try:
                child = pos.play(p, color if defending else attacker)
            except IllegalMove:
                continue
            if child.board[anchor] != color:
                result, pv = True, ()
            else:
                after = next(c for c in chains(child.board) if anchor in c.points)
                nlibs = len(after.liberties)
                if defending and nlibs >= 3:
                    result, pv = False, ()
                elif defending and nlibs <= 1:
                    result, pv = True, tuple(sorted(after.liberties))
                elif not defending and nlibs != 1:
                    continue
                else:
                    result, pv = search(child, not defending, depth+1)
            outcomes.append((result, (p,)+pv))
            if (defending and result is False) or (not defending and result is True):
                break
        active.remove(cycle_key)
        decisive = False if defending else True
        match = next((o for o in outcomes if o[0] is decisive), None)
        if match is not None:
            answer = match
        elif any(o[0] is None for o in outcomes):
            answer = None, max((o[1] for o in outcomes), key=len, default=())
        else:
            answer = defending, max((o[1] for o in outcomes), key=len, default=())
        memo[key] = answer
        return answer

    value, pv = search(position, defender_to_move, 0)
    return LadderResult(value, pv, node_count, "depth, node budget, or ko cycle" if value is None else None)


def ladders(board, max_nodes=100000):
    labels = np.full(board.shape, -1, np.int32)
    labels[board != 0] = 0
    dist, length, kind = (np.zeros(board.shape, np.int32) for _ in range(3))
    unknown = 0
    for chain in chains(board):
        nlibs = len(chain.liberties)
        if nlibs not in (1, 2):
            continue
        anchor = chain.points[0]
        answer = read_ladder(Position(board.copy()), anchor, nlibs == 1, max_nodes=max_nodes)
        d = max((max(abs(p[0]-anchor[0]), abs(p[1]-anchor[1])) for p in answer.variation), default=1)
        for p in chain.points:
            labels[p] = -1 if answer.captured is None else (1 if answer.captured else 2)
            dist[p], length[p], kind[p] = max(1, d), len(answer.variation), nlibs
        unknown += int(answer.captured is None)
    return labels, {"distance": dist, "length": length, "kind": kind, "unknown_chains": unknown}


LABELERS = {"liberties": liberties, "benson": benson, "ladders": ladders}
