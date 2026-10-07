"""Deterministic generators; setup positions are distinguished from playouts."""
import numpy as np
from .rules import Position, IllegalMove, legalize


def random_position(size, rng, density=None):
    density = float(rng.uniform(.2, .75)) if density is None else density
    pos = Position.empty(size)
    desired = int(density*size*size)
    for _ in range(size*size*4):
        if np.count_nonzero(pos.board) >= desired:
            break
        empty = np.argwhere(pos.board == 0)
        if not len(empty):
            break
        for i in rng.permutation(len(empty)):
            try:
                pos = pos.play(tuple(empty[i]))
                break
            except IllegalMove:
                continue
        else:
            pos = pos.play(None)
            if pos.passes == 2:
                break
    return pos.board


def structured(size, rng, shape=None,return_color=False):
    shape = shape or str(rng.choice(["snake", "ring", "spiral", "comb"]))
    b = np.zeros((size, size), np.int8)
    color = int(rng.integers(1, 3))
    if shape == "ring":
        lo = int(rng.integers(1, max(2, size//3)))
        hi = int(rng.integers(max(lo+2, size//2), size-1))
        b[lo:hi+1, lo] = b[lo:hi+1, hi] = color
        b[lo, lo:hi+1] = b[hi, lo:hi+1] = color
        if hi-lo > 3 and rng.random() < .5:
            b[lo+2:hi-1, lo+2:hi-1] = 3-color
    elif shape == "snake":
        path = []
        for r in range(1, size-1, 2):
            cols = range(1, size-1) if (r//2)%2 == 0 else range(size-2, 0, -1)
            row = [(r, c) for c in cols]
            if path:
                path.append((r-1, row[0][1]))
            path.extend(row)
        stop = len(path) if rng.random() < .2 else int(rng.integers(1, len(path)+1))
        for p in path[:stop]:
            b[p] = color
    elif shape == "comb":
        b[1:size-1, 1] = color
        b[1:size-1:2, 1:size-1] = color
    elif shape == "spiral":
        lo, hi = 1, size-2
        while lo <= hi:
            b[lo, lo:hi+1] = color
            b[lo:hi+1, hi] = color
            b[hi, lo:hi+1] = color
            if hi-lo > 2:
                b[lo+2:hi+1, lo] = color
                b[lo+2, lo:lo+3] = color
            lo, hi = lo+2, hi-2
    else:
        raise ValueError(shape)
    # Random opponent stones near the chain create nontrivial liberty classes.
    if rng.random() < .6:
        b[(b == 0) & (rng.random(b.shape) < rng.uniform(.05, .5))] = 3-color
    result = legalize(np.rot90(b, int(rng.integers(4))))
    return (result,color) if return_color else result


def living(size, rng, alive=True, color=None, enrich=False):
    color = int(rng.integers(1, 3)) if color is None else color
    b = np.zeros((size, size), np.int8)
    height = int(rng.integers(3,max(4,size)))
    width = int(rng.integers(5,max(6,size+1)))
    r = int(rng.integers(0, size-height+1))
    c = int(rng.integers(0, size-width+1))
    b[r:r+height, c:c+width] = color
    eyeheight = int(rng.integers(1,min(2,height-2)+1))
    b[r+1:r+1+eyeheight,c+1] = 0
    b[r+1:r+1+eyeheight,c+width-2] = 0
    if not alive:
        mode = int(rng.integers(3))
        if mode == 0:
            b[r+1:r+1+eyeheight, c+width-2] = color
        elif mode == 1:
            b[r+1:r+1+eyeheight, c+1:c+width-1] = 0
        else:
            b[r, c+1] = 0
            b[r+1, c+1] = 3-color
    # Keep two eyes isolated while adding many unique, independently legal surroundings.
    outside = b == 0
    outside[max(0,r-1):min(size,r+height+1),max(0,c-1):min(size,c+width+1)] = False
    clutter = outside & (rng.random(b.shape) < .2)
    b[clutter] = rng.integers(1,3,size=clutter.sum())
    if enrich:
        b[clutter] = 0
        # Extra isolated eyes and connected boundary growth vary geometry without
        # adding many neither-class chains to each living training example.
        for _ in range(int(rng.integers(1,max(2,size)))):
            rr = int(rng.integers(r+1,r+height-1))
            cc = int(rng.integers(c+1,c+width-1))
            if all(b[p] == color for p in ((rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1))):
                b[rr,cc] = 0
        for _ in range(size*size):
            rr,cc = rng.integers(size,size=2)
            if not (r <= rr < r+height and c <= cc < c+width) and b[rr,cc] == 0:
                adjacent = [(a,d) for a,d in ((rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1)) if 0 <= a < size and 0 <= d < size]
                if any(b[p] == color for p in adjacent):
                    b[rr,cc] = color
    return legalize(np.rot90(b, int(rng.integers(4))))


def ladder_position(size, rng, return_anchor=False):
    b = np.zeros((size, size), np.int8)
    r, c = int(rng.integers(1, size-2)), int(rng.integers(1, size-2))
    color = int(rng.integers(1, 3))
    b[r, c] = color
    b[r-1, c] = b[r, c-1] = 3-color
    b[r-1, c+1] = 3-color
    if rng.random() < .5:
        b[r+1, c] = 3-color
    for _ in range(int(rng.integers(0, max(2, size//2)))):
        rr, cc = rng.integers(size, size=2)
        if b[rr, cc] == 0 and max(abs(rr-r), abs(cc-c)) > 1:
            b[rr, cc] = int(rng.integers(1, 3))
    rotation = int(rng.integers(4))
    anchor = r,c
    for _ in range(rotation):
        anchor = size-1-anchor[1],anchor[0]
    result = legalize(np.rot90(b,rotation))
    return (result,anchor) if return_anchor else result


def ring_pair(size, rng, attempts=300):
    from .labels import liberties
    from .rules import chains, neighbors
    for _ in range(attempts):
        ring = structured(size, rng, "ring")
        for chain in chains(ring):
            color = chain.color
            points = set(chain.points)
            if len(points) < size or any(sum(q in points for q in neighbors(p,size)) != 2 for p in points):
                continue
            for p in rng.permutation(np.array(chain.points)):
                path = ring.copy()
                path[tuple(p)] = 0
                a, _ = liberties(ring)
                b, _ = liberties(path)
                common = (ring == color) & (path == color)
                if np.all(a[common] == b[common]):
                    return ring, path, color
    raise RuntimeError("Could not generate a matched ring/path pair")


def canonical_key(board):
    forms = []
    for rotation in range(4):
        rotated = np.rot90(board,rotation)
        for form in (rotated,rotated[::-1]):
            forms.append(form.tobytes())
            forms.append(np.array([0, 2, 1, 3, 7, 6, 5, 4], np.int8)[form].tobytes())
    return min(forms)


def controlled_structure(size,rng,return_metadata=False,target_liberties=None):
    """Keep a chosen number of liberties on the largest structured chain."""
    from .rules import chains
    target = int(rng.integers(1,5)) if target_liberties is None else int(target_liberties)
    if not 1 <= target <= 16:
        raise ValueError("Requested controlled liberty count must be 1 through16")
    for _ in range(300):
        original,color = structured(size,rng,return_color=True)
        candidates = [c for c in chains(original) if c.color == color]
        if not candidates:
            continue
        chain = max(candidates,key=lambda c:len(c.points))
        b = np.zeros_like(original)
        for p in chain.points:
            b[p] = chain.color
        chain = chains(b)[0]
        if len(chain.liberties) < target:
            continue
        free = list(chain.liberties)
        rng.shuffle(free)
        for p in free[target:]:
            b[p] = 3-chain.color
        b = legalize(b)
        if any(b[p] != chain.color for p in chain.points):
            continue
        result = next(c for c in chains(b) if chain.points[0] in c.points)
        if len(result.liberties) == target:
            return (b,{"color":chain.color,"points":chain.points,"target_liberties":target}) if return_metadata else b
    raise RuntimeError("Could not build a legal structure with the requested liberty count")


def balanced_benson(size,count,seed):
    from .labels import benson
    from .rules import chains
    rng = np.random.default_rng(seed)
    counts = np.zeros(3,np.int64)
    boards,sources,seen = [],[],set()
    attempts = 0
    while len(boards) < count:
        attempts += 1
        if attempts > count*200:
            raise RuntimeError("Balanced Benson generator exhausted unique samples")
        desired = int(np.argmin(counts))
        if desired in (0,1):
            b = living(size,rng,True,color=desired+1,enrich=True)
            source = "synthetic multi-eye life"
        elif rng.random() < .5:
            b,source = random_position(size,rng),"P-random; self-play engine unavailable"
        else:
            b,source = living(size,rng,False),"synthetic near-miss"
        key = canonical_key(b)
        if key in seen:
            continue
        labels,_ = benson(b)
        increment = np.zeros(3,np.int64)
        for chain in chains(b):
            increment[labels[chain.points[0]]] += 1
        if not increment[desired]:
            continue
        counts += increment
        boards.append(b)
        sources.append(source)
        seen.add(key)
    return np.stack(boards),sources,counts


def balanced_ladders(size,count,seed,max_nodes=100000,exclude=()):
    """Pair captured/escaped canonical defenders within PV-length bins."""
    from collections import defaultdict,deque
    from .labels import ladders
    if count % 2:
        raise ValueError("Balanced ladder splits require an even board count")
    rng = np.random.default_rng(seed)
    seen,buffers = set(exclude),defaultdict(deque)
    boards,targets,infos,sources = [],[],[],[]
    counts = defaultdict(lambda:[0,0])
    maximum_length = 8 if size == 9 else 35
    for _ in range(count*200):
        if len(boards) == count:
            break
        b,anchor = ladder_position(size,rng,return_anchor=True)
        key = canonical_key(b)
        if key in seen or b[anchor] == 0:
            continue
        seen.add(key)
        labels,info = ladders(b,max_nodes=max_nodes)
        outcome,length = int(labels[anchor]),int(info["length"][anchor])
        if outcome not in (1,2) or not 1 <= length <= maximum_length:
            continue
        info["defender_anchor"] = anchor
        length_bin = 2**int(np.floor(np.log2(length)))
        counterpart = buffers[(length_bin,3-outcome)]
        example = b,labels,info
        if counterpart:
            for board,target,descriptor in (counterpart.popleft(),example):
                boards.append(board)
                targets.append(target)
                infos.append(descriptor)
                sources.append(f"canonical ladder; balanced defender PV bin {length_bin}")
            counts[length_bin][0] += 1
            counts[length_bin][1] += 1
        else:
            buffers[(length_bin,outcome)].append(example)
    if len(boards) != count:
        raise RuntimeError("Could not fill a balanced ladder split within the search budget")
    return np.stack(boards),sources,np.stack(targets),infos,dict(counts)


def generate(task, size, count, seed, generator="mixed",exclude=(),controlled=False):
    rng = np.random.default_rng(seed)
    boards, sources = [], []
    seen = set(exclude)
    attempts = 0
    while len(boards) < count:
        attempts += 1
        if attempts > count*100:
            raise RuntimeError("Dataset deduplication exhausted generator")
        if generator == "random":
            b, source = random_position(size, rng), "P-random"
        elif generator == "structured":
            b, source = (controlled_structure(size,rng),"P-structured; controlled liberties") if controlled else (structured(size,rng),"P-structured")
        elif task == "benson":
            if rng.random() < .8:
                b, source = living(size, rng, alive=rng.random() < .75), "synthetic life"
            else:
                b, source = random_position(size, rng), "P-random"
        elif task == "ladders":
            b, source = ladder_position(size, rng), "canonical ladder"
        elif rng.random() < .6:
            b, source = random_position(size, rng), "P-random"
        else:
            b, source = (controlled_structure(size,rng),"P-structured; controlled liberties") if controlled else (structured(size,rng),"P-structured")
        key = canonical_key(b)
        if key not in seen:
            boards.append(b)
            sources.append(source)
            seen.add(key)
    return np.stack(boards), sources
