import numpy as np
from ncago.go.rules import chains, neighbors


def liberty_ca(board, max_steps=None):
    """Synchronous orthogonal k-smallest-ID propagation, with no global reads."""
    n = len(board)
    cap = n*n+1
    state = np.full((n, n, 4), cap, np.int32)
    history = [state.copy()]
    max_steps = n*n+1 if max_steps is None else max_steps
    for _ in range(max_steps):
        out = state.copy()
        for p in map(tuple, np.argwhere(board != 0).tolist()):
            ids = list(state[p])
            for q in neighbors(p, n):
                if board[q] == 0:
                    ids.append(q[0]*n+q[1])
                elif board[q] == board[p]:
                    ids.extend(state[q])
            smallest = sorted(set(ids))[:4]
            out[p] = np.array(smallest + [cap]*(4-len(smallest)), np.int32)
        history.append(out.copy())
        if np.array_equal(out, state):
            break
        state = out
    predictions = np.stack([(s < cap).sum(-1)-1 for s in history])
    predictions[:, board == 0] = -1
    convergence = []
    for chain in chains(board):
        points = tuple(zip(*chain.points))
        correct = np.all(predictions[:, points[0], points[1]] == min(4, len(chain.liberties))-1, axis=1)
        stable = np.logical_and.accumulate(correct[::-1])[::-1]
        convergence.append(int(np.flatnonzero(stable)[0]) if stable.any() else None)
    return predictions, convergence
