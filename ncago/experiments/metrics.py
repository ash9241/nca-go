"""Accuracy, convergence and uncertainty definitions shared by all experiments."""
import numpy as np
from ncago.go.rules import chains, diameter


def accuracy(board,target,prediction,eligible=None):
    mask = target >= 0
    if eligible is not None:
        mask &= eligible
    correct = prediction == target
    chain_results = []
    for chain in chains(board):
        points = [p for p in chain.points if mask[p]]
        if points:
            chain_results.append(all(correct[p] for p in points))
    count = int(mask.sum())
    return {"stone_correct":int((correct&mask).sum()),"stone_count":count,
            "stone_accuracy":float(correct[mask].mean()) if count else None,
            "chain_correct":sum(chain_results),"chain_count":len(chain_results),
            "chain_accuracy":float(np.mean(chain_results)) if chain_results else None,
            "board_exact":bool(correct[mask].all()) if count else None}


def solve_times(predictions,target,steps,mask=None):
    """Earliest logged checkpoint correct at every remaining logged checkpoint."""
    defined = target >= 0 if mask is None else ((target >= 0)&mask)
    if not defined.any():
        return None
    correct = np.all((predictions == target)[:,defined],axis=1)
    stable = np.logical_and.accumulate(correct[::-1])[::-1]
    indices = np.flatnonzero(stable)
    return int(steps[indices[0]]) if len(indices) else None


def bootstrap_gap(a,b,seed=0,samples=10000,weights=None):
    a,b = np.asarray(a,float),np.asarray(b,float)
    valid = np.isfinite(a)&np.isfinite(b)
    differences = a[valid]-b[valid]
    if not len(differences):
        return None,None,None
    rng = np.random.default_rng(seed)
    weights = np.ones(len(differences)) if weights is None else np.asarray(weights,float)[valid]
    if np.any(weights <= 0):
        raise ValueError("Bootstrap weights must be positive")
    draws = []
    for start in range(0,samples,512):
        indices = rng.integers(len(differences),size=(min(512,samples-start),len(differences)))
        draws.extend(np.sum(differences[indices]*weights[indices],axis=1)/np.sum(weights[indices],axis=1))
    lo,hi = np.quantile(draws,[.025,.975])
    return float(np.average(differences,weights=weights)),float(lo),float(hi)


def wilson(wins,games):
    if not games:
        return None,None
    z = 1.959963984540054
    p = wins/games
    denom = 1+z*z/games
    center = (p+z*z/(2*games))/denom
    half = z*np.sqrt(p*(1-p)/games+z*z/(4*games*games))/denom
    return float(center-half),float(center+half)


def verdict(nca,baseline):
    if nca is None or baseline is None:
        return "Unknown"
    if nca >= .95 and nca-baseline >= .02:
        return "Use NCA"
    if baseline-nca >= .02:
        return "Use baseline"
    return "Tie"


def distance_bin(distance):
    lo = 1 if distance <= 1 else 2**int(np.floor(np.log2(distance)))
    return lo,2*lo-1
