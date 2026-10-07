"""Illustrate explicit identifier counting on already opened witnesses.

These figures describe a hand-written algorithm, never a learned-model result.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import imageio.v2 as imageio
from ncago.go.research_data import identifier_reference_fast, count_labels
from ncago.go.rules import group
from .checkpoint_audit import chain_features
from .common import ROOT, write_json


def main(render_only=False):
    out = ROOT / "reports/checkpoint_audit"
    records = json.loads((out / "reference_depth.json").read_text())["records"] if render_only else []
    rng = np.random.default_rng(970005)
    for size in (() if render_only else (9, 13, 19, 25, 37)):
        with np.load(out / f"reference_witness_{size}.npz") as d:
            data = {k: d[k] for k in d.files}
        diameters = np.asarray([max(1, int(chain_features(b)[tuple(q)][1])) for b, q in zip(data["boards"], data["queries"])])
        for draw in range(8):
            identifiers = [rng.integers(0, 2**32, (size, size), dtype=np.int64) for _ in range(len(diameters)//2)]
            for ratio in (.5, 1., 2., 4.):
                correct = []
                for i, (b, q, y, diameter) in enumerate(zip(data["boards"], data["queries"], data["labels"], diameters)):
                    p, _ = identifier_reference_fast(b, identifiers[i//2], max(1, int(np.ceil(ratio*diameter))))
                    correct.append(bool(p[tuple(q)] == y))
                for geometry in sorted(set(data["geometries"])):
                    mask = data["geometries"] == geometry
                    pair = np.asarray(correct)[mask].reshape(-1, 2)
                    records.append(dict(size=size, draw=draw, ratio=ratio, geometry=str(geometry),
                                        pairs=len(pair), pair_both_correct=float(pair.all(1).mean())))
        print(f"Reference diameter audit {size}", flush=True)
    write_json(out / "reference_depth.json", dict(records=records, bits=32, learned=False,
               clock="D chain-message rounds after one local liberty-ID loading phase",
               scope="Previously opened five-geometry witnesses; eight coupled ID draws, no training seeds"))
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.5), layout="constrained")
    for ax, size in zip(axes, (9, 13, 19, 25, 37)):
        for geometry in ("straight", "elbow", "snake", "comb", "ring"):
            ax.plot([.5, 1, 2, 4], [100*np.mean([r["pair_both_correct"] for r in records if r["size"] == size and r["geometry"] == geometry and r["ratio"] == ratio]) for ratio in (.5, 1, 2, 4)], "o-", label=geometry)
        ax.set(title=f"{size}×{size}", xlabel="Message rounds / chain diameter", ylim=(-2, 102), xscale="log", xticks=[.5, 1, 2, 4])
        ax.set_xticklabels(["0.5", "1", "2", "4"])
        ax.minorticks_off()
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Pair both correct (%)"); axes[-1].legend(fontsize=7, loc="lower right")
    fig.suptitle("Hand-coded smallest-four-ID counting", fontsize=12)
    fig.savefig(out / "reference_depth.png", dpi=180); plt.close(fig)

    with np.load(out / "reference_witness_37.npz") as d:
        b, q, y = d["boards"][32:34], d["queries"][32:34], d["labels"][32:34]
    ids = np.random.default_rng(970006).integers(0, 2**32, (37, 37), dtype=np.int64)
    diameter = max(int(chain_features(board)[tuple(query)][1]) for board, query in zip(b, q))
    depths = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, diameter]
    predictions = np.stack([[identifier_reference_fast(board, ids, depth)[0] for board in b] for depth in depths])
    np.savez_compressed(out / "reference_animation_data.npz", boards=b, queries=q, labels=y,
                        identifiers=ids, depths=depths, predictions=predictions)
    frames = []
    cmap = ListedColormap(["#b8c0c9", "#2478a7", "#e39b2f", "#9c6baf", "#368469"])
    for depth, prediction in zip(depths, predictions):
        fig, axes = plt.subplots(1, 2, figsize=(8, 4.4), layout="constrained")
        fig.get_layout_engine().set(rect=(0, .08, 1, .92))
        for side, ax in enumerate(axes):
            points, _ = group(b[side], *q[side])
            mask = np.zeros(b[side].shape, bool)
            for rr, cc in points:
                mask[rr, cc] = True
            ax.set_facecolor("#f0f2f4")
            ax.imshow(np.ma.masked_where(~mask, prediction[side]+1), cmap=cmap, vmin=0, vmax=4, origin="lower", interpolation="nearest")
            rr, cc = q[side]
            ax.scatter([cc], [rr], s=180, facecolors="none", edgecolors="#101820", linewidths=2)
            observed = int(prediction[side, rr, cc])+1
            ax.set_title(f"Query count: exact {y[side]+1} · observed {observed}", fontsize=11)
            ax.set(xticks=[], yticks=[])
        fig.suptitle(f"Hand-coded ID-set counting · {depth} message rounds\n37×37 snake · diameter {diameter} · shared random IDs", fontsize=12)
        fig.text(.04, .025, "Target chain only · grey: 0 seen · blue: 1 · orange: 2 · purple: 3 · green: 4+", fontsize=9)
        fig.canvas.draw(); frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()); plt.close(fig)
    imageio.mimsave(out / "reference_propagation.gif", frames, duration=700, loop=0)

    board = np.zeros((5, 5), np.int8)
    board[1, 1] = board[1, 2] = board[2, 2] = 1
    points, liberties = group(board, 1, 1)
    adjacent_sum = sum(sum(0 <= rr < 5 and 0 <= cc < 5 and board[rr, cc] == 0 for rr, cc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1))) for r,c in points)
    write_json(out / "acyclic_double_counting_example.json", dict(board=board, stone_graph_cycle=False,
               exact_liberties=int(liberties.sum()), sum_of_local_liberties=int(adjacent_sum),
               cap4_hides_error=min(4, int(liberties.sum())) == min(4, adjacent_sum),
               interpretation="A liberty may touch two stones in an acyclic chain. Stone-graph cycles are not necessary for naive double counting."))
    assert int(liberties.sum()) == 7 and adjacent_sum == 8
    print(out / "reference_propagation.gif", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--render-only", action="store_true")
    main(p.parse_args().render_only)
