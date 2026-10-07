"""Online, reproducible whole-board data and multiple causal witness geometries."""
from hashlib import sha256
import numpy as np
from numba import njit
from .rules import group, play_array, legalize
from .generators import controlled_structure, canonical_key


@njit(cache=True)
def count_labels(board, cap=4):
    labels = np.full(board.shape, -1, np.int32)
    visited = np.zeros(board.shape, np.bool_)
    for r in range(len(board)):
        for c in range(len(board)):
            if board[r, c] in (1, 2) and not visited[r, c]:
                points, liberties = group(board, r, c)
                value = min(cap, int(liberties.sum()))-1
                for rr, cc in points:
                    labels[rr, cc] = value
                    visited[rr, cc] = True
    return labels


@njit(cache=True)
def fast_random_position(size, seed):
    """Legal alternating playouts with suicide and simple-ko checks."""
    np.random.seed(seed)
    board = np.zeros((size, size), np.int8)
    previous = np.full_like(board, -1)
    desired = int(np.random.uniform(.2, .75)*size*size)
    color, passes = 1, 0
    for _ in range(size*size*4):
        if np.count_nonzero(board) >= desired:
            break
        order = np.random.permutation(size*size)
        played = False
        for index in order:
            r, c = index//size, index % size
            if board[r, c] != 0:
                continue
            child, legal = play_array(board, r, c, color)
            if legal and not np.array_equal(child, previous):
                previous, board = board, child
                passes, played = 0, True
                break
        if not played:
            previous = board.copy()
            passes += 1
        if passes == 2:
            break
        color = 3-color
    return board


class OnlineStream:
    """The data stream depends on data_seed, never on model weights or seed.

    No finite training set is sampled. Repeated canonical positions can occur
    naturally online, but frozen evaluation positions are rejected explicitly.
    """
    def __init__(self, seed, sizes=(5, 6, 7, 8, 9), canvas=9, cap=4, exclude=(), task="liberties"):
        self.rng = np.random.default_rng(seed)
        self.sizes, self.canvas, self.cap = tuple(sizes), canvas, cap
        self.exclude = set(exclude)
        self.task = task
        self.draws, self.rejected = 0, 0
        self.digest = sha256()
        self.seen_canonical_hashes = set()
        self.last_sources = []
        self.source_draw_counts = {}

    def draw(self, count):
        boards, targets, sources = [], [], []
        while len(boards) < count:
            size = int(self.rng.choice(self.sizes))
            target = None
            if self.task == "race":
                source = "regular_rectangular_race"
                from .research_tasks import capture_race_board
                board, target, _ = capture_race_board(size, self.rng)
            elif self.task == "eyes":
                from .research_tasks import eye_board, simple_eye_counts
                source = "simple_eye_setup" if self.rng.random() < .7 else "legal_random"
                board = eye_board(size, self.rng) if source == "simple_eye_setup" else fast_random_position(size, int(self.rng.integers(2**31-1)))
                target = simple_eye_counts(board, self.cap-1)
            elif self.rng.random() < .5:
                source = "legal_random"
                board = fast_random_position(size, int(self.rng.integers(2**31-1)))
            else:
                source = "controlled"
                if self.cap > 4:
                    requested = int(self.rng.integers(1, min(self.cap, 4*(size-2)+1)+1))
                    board = controlled_structure(size, self.rng, target_liberties=requested)
                else:
                    board = controlled_structure(size, self.rng)
            if size < self.canvas:
                row, col = self.rng.integers(self.canvas-size+1, size=2)
                padded = np.full((self.canvas, self.canvas), 3, np.int8)
                padded[row:row+size, col:col+size] = board
                board = padded
                if target is not None:
                    padded_target = np.full((self.canvas, self.canvas), -1, np.int32)
                    padded_target[row:row+size, col:col+size] = target
                    target = padded_target
            key = canonical_key(board)
            if key in self.exclude:
                self.rejected += 1
                continue
            if target is None:
                target = count_labels(board, self.cap)
            if not np.any(target >= 0):
                continue
            if self.task == "liberties" and np.any(target[(board == 1) | (board == 2)] < 0):
                raise AssertionError("Online generator made a chain without liberties")
            self.digest.update(board.tobytes())
            self.seen_canonical_hashes.add(sha256(key).digest())
            self.draws += 1
            self.source_draw_counts[source] = self.source_draw_counts.get(source, 0)+1
            sources.append(source)
            boards.append(board)
            targets.append(target)
        self.last_sources = sources
        return np.stack(boards), np.stack(targets)


class OnlinePrefetch:
    """Generate one fresh batch ahead without changing the candidate stream.

    A separate data RNG and a single producer preserve exact ordering. Capture
    the consumed prefix before launching the next batch, so logs never include
    timing-dependent partially generated candidates.
    """
    def __init__(self, stream, batch, iterations):
        from concurrent.futures import ThreadPoolExecutor
        self.stream, self.batch, self.remaining = stream, batch, iterations
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="online-data")
        self.future = self.executor.submit(stream.draw, batch)
        self.stats = None

    def draw(self):
        boards, labels = self.future.result()
        self.stats = dict(online_boards=self.stream.draws, stream_sha256=self.stream.digest.hexdigest())
        self.remaining -= 1
        self.future = self.executor.submit(self.stream.draw, self.batch) if self.remaining else None
        return boards, labels

    def close(self):
        self.executor.shutdown(wait=True, cancel_futures=True)


def witness_board(size, geometry, rng, base_liberties=1):
    """k/(k+1)-liberty pair with identical geometry and one changed cell."""
    if base_liberties < 1:
        raise ValueError('Witness liberty counts must be positive')
    board = np.zeros((size, size), np.int8)
    lo, hi = 1, size-2
    middle = size//2
    if geometry == "straight":
        board[middle, lo:hi+1] = 1
    elif geometry == "elbow":
        board[lo:hi+1, lo] = 1
        board[hi, lo:hi+1] = 1
    elif geometry == "snake":
        for i, r in enumerate(range(lo, hi+1, 2)):
            board[r, lo:hi+1] = 1
            if r+2 <= hi:
                board[r+1, hi if i % 2 == 0 else lo] = 1
    elif geometry == "comb":
        board[lo:hi+1, lo] = 1
        board[lo:hi+1:2, lo:hi+1] = 1
    elif geometry == "ring":
        board[lo, lo:hi+1] = board[hi, lo:hi+1] = 1
        board[lo:hi+1, lo] = board[lo:hi+1, hi] = 1
    else:
        raise ValueError(geometry)
    points, liberty_mask = group(board, *np.argwhere(board == 1)[0])
    liberties = np.argwhere(liberty_mask)
    # Select distant query and extra liberty; base liberty is independently varied.
    candidates = []
    for q in points:
        distances = np.max(np.abs(liberties-q), axis=1)
        far = np.flatnonzero(distances == distances.max())
        candidates.append((int(distances.max()), tuple(q), int(rng.choice(far))))
    maximum = max(x[0] for x in candidates)
    options = [x for x in candidates if x[0] == maximum]
    _, query, extra = options[int(rng.integers(len(options)))]
    base = int(rng.choice([i for i in range(len(liberties)) if i != extra]))
    kept = [base]
    if base_liberties > 1:
        remaining = [i for i in range(len(liberties)) if i not in (extra, base)]
        if base_liberties > len(liberties)-1:
            raise ValueError('Requested witness count exceeds available liberty points')
        kept.extend(rng.choice(remaining, base_liberties-1, replace=False).tolist())
    board[liberty_mask] = 2
    for index in kept:
        board[tuple(liberties[index])] = 0
    board = legalize(board)
    changed = tuple(liberties[extra])
    other = board.copy()
    other[changed] = 0
    verification_cap = max(4, base_liberties+2)
    if (count_labels(board, verification_cap)[query], count_labels(other, verification_cap)[query]) != (base_liberties-1, base_liberties):
        raise AssertionError("Witness labels changed unexpectedly")
    # Rotate/reflect/color-swap both sides together, including query coordinates.
    marks = np.zeros(board.shape, np.int8)
    marks[query], marks[changed] = 1, 2
    rotation = int(rng.integers(4))
    board, other, marks = [np.rot90(x, rotation).copy() for x in (board, other, marks)]
    if rng.random() < .5:
        board, other, marks = [x[::-1].copy() for x in (board, other, marks)]
    if rng.random() < .5:
        board, other = [np.where(x == 1, 2, np.where(x == 2, 1, x)).astype(np.int8) for x in (board, other)]
    query = tuple(np.argwhere(marks == 1)[0])
    changed = tuple(np.argwhere(marks == 2)[0])
    return board, other, query, changed


def witness_set(size, per_geometry=8, seed=86001, liberty_counts=None, cap=4):
    if liberty_counts is not None and (not len(liberty_counts) or any(k < 1 or k >= cap for k in liberty_counts)):
        raise ValueError('Witness base counts must lie below the prediction cap')
    rng = np.random.default_rng(seed)
    boards, queries, labels, geometries, distances, base_counts = [], [], [], [], [], []
    seen = set()
    for geometry in ("straight", "elbow", "snake", "comb", "ring"):
        count = 0
        for _ in range(per_geometry*100):
            base_count = 1 if liberty_counts is None else int(liberty_counts[count % len(liberty_counts)])
            one, two, query, changed = witness_board(size, geometry, rng, base_count)
            signature = (canonical_key(one), canonical_key(two), query)
            if signature in seen:
                continue
            seen.add(signature)
            boards.extend((one, two))
            queries.extend((query, query))
            labels.extend((int(count_labels(one, cap)[query]), int(count_labels(two, cap)[query])))
            base_counts.extend((base_count, base_count))
            geometries.extend((geometry, geometry))
            distances.extend((max(abs(query[0]-changed[0]), abs(query[1]-changed[1])),)*2)
            count += 1
            if count == per_geometry:
                break
        if count != per_geometry:
            raise RuntimeError(f"Insufficient {geometry} witnesses")
    return {"boards": np.stack(boards), "queries": np.asarray(queries), "labels": np.asarray(labels),
            "geometries": np.asarray(geometries), "causal_distance": np.asarray(distances),
            "base_liberty_count": np.asarray(base_counts)}


def identifier_reference(board, identifiers, steps, cap=4):
    """Hand-coded set union of the cap smallest distinct liberty IDs.

    identifiers are arbitrary comparable integer keys. The result is exact if
    liberty IDs are distinct and enough rounds are allowed. IID finite keys
    can collide; this reference deliberately does not silently repair them.
    """
    n = len(board)
    messages = [[set() for _ in range(n)] for _ in range(n)]
    for r, c in np.argwhere((board == 1) | (board == 2)):
        for rr, cc in ((r+1, c), (r-1, c), (r, c+1), (r, c-1)):
            if 0 <= rr < n and 0 <= cc < n and board[rr, cc] == 0:
                messages[r][c].add(int(identifiers[rr, cc]))
        messages[r][c] = set(sorted(messages[r][c])[:cap])
    for _ in range(steps):
        new = [[set() for _ in range(n)] for _ in range(n)]
        changed = False
        for r, c in np.argwhere((board == 1) | (board == 2)):
            values = messages[r][c].copy()
            for rr, cc in ((r+1, c), (r-1, c), (r, c+1), (r, c-1)):
                if 0 <= rr < n and 0 <= cc < n and board[rr, cc] == board[r, c]:
                    values.update(messages[rr][cc])
            new[r][c] = set(sorted(values)[:cap])
            changed |= new[r][c] != messages[r][c]
        messages = new
        if not changed:
            break
    prediction = np.full(board.shape, -1, np.int32)
    for r, c in np.argwhere((board == 1) | (board == 2)):
        prediction[r, c] = len(messages[r][c])-1
    return prediction


@njit(cache=True)
def identifier_reference_fast(board, identifiers, steps, cap=4):
    """Integer implementation of the same smallest-distinct-ID CA."""
    n = len(board)
    sentinel = np.int64(9223372036854775807)
    state = np.full((n, n, cap), sentinel, np.int64)
    for r in range(n):
        for c in range(n):
            if board[r, c] not in (1, 2):
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r+dr, c+dc
                if 0 <= rr < n and 0 <= cc < n and board[rr, cc] == 0:
                    value = identifiers[rr, cc]
                    if not np.any(state[r, c] == value) and value < state[r, c, -1]:
                        state[r, c, -1] = value
                        state[r, c].sort()
    rounds = 0
    for _ in range(steps):
        new = state.copy()
        for r in range(n):
            for c in range(n):
                if board[r, c] not in (1, 2):
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    rr, cc = r+dr, c+dc
                    if 0 <= rr < n and 0 <= cc < n and board[rr, cc] == board[r, c]:
                        for k in range(cap):
                            value = state[rr, cc, k]
                            if not np.any(new[r, c] == value) and value < new[r, c, -1]:
                                new[r, c, -1] = value
                                new[r, c].sort()
        rounds += 1
        if np.array_equal(new, state):
            state = new
            break
        state = new
    labels = np.full(board.shape, -1, np.int32)
    for r in range(n):
        for c in range(n):
            if board[r, c] in (1, 2):
                labels[r, c] = int(np.sum(state[r, c] != sentinel))-1
    return labels, rounds
