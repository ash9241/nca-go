"""Orthogonal Go rules. Coordinates are (row, column), row zero at bottom."""
from dataclasses import dataclass, field
from collections import deque
import hashlib
import numpy as np
from numba import njit

EMPTY, BLACK, WHITE, OFFBOARD = 0, 1, 2, 3


class IllegalMove(ValueError):
    pass


@njit(cache=True)
def group(board, row, col):
    n = board.shape[0]
    color = board[row, col]
    seen = np.zeros((n, n), np.bool_)
    liberties = np.zeros((n, n), np.bool_)
    queue = np.empty((n*n, 2), np.int32)
    queue[0] = row, col
    seen[row, col] = True
    head, tail = 0, 1
    while head < tail:
        r, c = queue[head]
        head += 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r+dr, c+dc
            if 0 <= rr < n and 0 <= cc < n:
                if board[rr, cc] == 0:
                    liberties[rr, cc] = True
                elif board[rr, cc] == color and not seen[rr, cc]:
                    seen[rr, cc] = True
                    queue[tail] = rr, cc
                    tail += 1
    return queue[:tail], liberties


@njit(cache=True)
def play_array(board, row, col, color):
    n = board.shape[0]
    if row < 0 or col < 0 or row >= n or col >= n or board[row, col] != 0:
        return board.copy(), False
    out = board.copy()
    out[row, col] = color
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        rr, cc = row+dr, col+dc
        if 0 <= rr < n and 0 <= cc < n and out[rr, cc] == 3-color:
            points, libs = group(out, rr, cc)
            if not libs.any():
                for point in points:
                    out[point[0], point[1]] = 0
    _, libs = group(out, row, col)
    return out, libs.any()


def neighbors(point, n):
    r, c = point
    return [(rr, cc) for rr, cc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1))
            if 0 <= rr < n and 0 <= cc < n]


@dataclass
class Chain:
    color: int
    points: tuple
    liberties: frozenset


def chains(board):
    seen = set()
    result = []
    for r, c in np.argwhere(board != 0):
        p = (int(r), int(c))
        if p not in seen:
            points, libs = group(board, *p)
            pts = tuple(map(tuple, points.tolist()))
            seen.update(pts)
            result.append(Chain(int(board[p]), pts, frozenset(map(tuple, np.argwhere(libs).tolist()))))
    return result


def diameter(chain):
    """Exact graph diameter, including cyclic and branched chains."""
    pts = set(chain.points)
    maximum = 0
    for start in pts:
        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            (r, c), d = queue.popleft()
            maximum = max(maximum, d)
            for p in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                if p in pts and p not in visited:
                    visited.add(p)
                    queue.append((p, d+1))
    return maximum


@dataclass
class Position:
    board: np.ndarray
    to_move: int = BLACK
    previous: bytes | None = None
    superko: bool = False
    history: frozenset = field(default_factory=frozenset)
    passes: int = 0

    @classmethod
    def empty(cls, size, **kwargs):
        if not 5 <= size <= 37:
            raise ValueError("Board size must be 5 through 37")
        return cls(np.zeros((size, size), np.int8), **kwargs)

    def play(self, point, color=None):
        color = self.to_move if color is None else color
        if color not in (BLACK, WHITE):
            raise IllegalMove("Invalid color")
        current = self.board.tobytes()
        history = self.history | {current}
        if point is None:
            return Position(self.board.copy(), 3-color, current, self.superko, history, self.passes+1)
        out, legal = play_array(self.board, *point, color)
        if not legal:
            raise IllegalMove("Occupied, outside board, or suicide")
        encoded = out.tobytes()
        if encoded == self.previous or (self.superko and encoded in history):
            raise IllegalMove("Ko")
        return Position(out, 3-color, current, self.superko, history, 0)

    def legal_moves(self):
        legal = []
        for p in map(tuple, np.argwhere(self.board == 0).tolist()):
            try:
                self.play(p)
                legal.append(p)
            except IllegalMove:
                continue
        return legal + [None]

    def digest(self):
        return hashlib.sha256(self.board.tobytes() + bytes([self.to_move])).hexdigest()

    def score(self, komi=7.5):
        """Tromp-Taylor area score: positive means Black ahead."""
        n = len(self.board)
        black, white = int((self.board == BLACK).sum()), int((self.board == WHITE).sum())
        seen = set()
        for p in map(tuple, np.argwhere(self.board == 0).tolist()):
            if p in seen:
                continue
            region, border, todo = set(), set(), [p]
            while todo:
                q = todo.pop()
                if q in region:
                    continue
                region.add(q)
                for adjacent in neighbors(q, n):
                    if self.board[adjacent] == 0 and adjacent not in region:
                        todo.append(adjacent)
                    elif self.board[adjacent] != 0:
                        border.add(int(self.board[adjacent]))
            seen.update(region)
            if border == {BLACK}:
                black += len(region)
            elif border == {WHITE}:
                white += len(region)
        return black-white-komi


def legalize(board):
    """Remove setup chains without liberties, iterating to a stable legal setup."""
    out = np.array(board, dtype=np.int8, copy=True)
    if not np.isin(out, [0, 1, 2]).all():
        raise ValueError("Invalid setup token")
    for chain in chains(out):
        if not chain.liberties:
            for p in chain.points:
                out[p] = 0
    return out
