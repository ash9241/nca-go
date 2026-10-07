"""CPU-only descriptive audit of previously opened final checkpoints and data.

Graph diameter is a chain-message distance proxy. It is not the unrestricted
grid NCA's strict light cone: that model may communicate across empty cells and
diagonals. All stratified results preserve class counts and generator labels.
"""
from collections import defaultdict
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numba import njit
from ncago.go.rules import group
from .common import ROOT, write_json


@njit(cache=True)
def chain_features(board):
    n = len(board)
    features = np.full((n, n, 6), -1, np.int32)
    visited = np.zeros((n, n), np.bool_)
    chain_id = 0
    for row in range(n):
        for col in range(n):
            if board[row, col] not in (1, 2) or visited[row, col]:
                continue
            points, libs = group(board, row, col)
            edges, edge_distance, span = 0, n, 0
            index = np.full((n, n), -1, np.int32)
            for i, point in enumerate(points):
                r, c = point
                visited[r, c] = True
                index[r, c] = i
                edge_distance = min(edge_distance, r, c, n-1-r, n-1-c)
            for r, c in points:
                if r+1 < n and index[r+1, c] >= 0:
                    edges += 1
                if c+1 < n and index[r, c+1] >= 0:
                    edges += 1
            diameter = 0
            queue = np.empty(len(points), np.int32)
            for start in range(len(points)):
                distances = np.full(len(points), -1, np.int32)
                distances[start] = 0
                queue[0] = start
                head, tail = 0, 1
                while head < tail:
                    current = queue[head]
                    head += 1
                    r, c = points[current]
                    diameter = max(diameter, distances[current])
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        rr, cc = r+dr, c+dc
                        if 0 <= rr < n and 0 <= cc < n:
                            other = index[rr, cc]
                            if other >= 0 and distances[other] < 0:
                                distances[other] = distances[current]+1
                                queue[tail] = other
                                tail += 1
                span = max(span, abs(points[start, 0]-row), abs(points[start, 1]-col))
            # Connected undirected graph: E >= V iff at least one cycle exists.
            cyclic = int(edges >= len(points))
            liberty_points = np.argwhere(libs)
            for r, c in points:
                geometric_distance = 0
                for rr, cc in liberty_points:
                    geometric_distance = max(geometric_distance, abs(rr-r), abs(cc-c))
                features[r, c] = np.array([chain_id, diameter, cyclic, len(points), edge_distance, geometric_distance])
            chain_id += 1
    return features


def bin_value(value, boundaries):
    lower = 0
    for upper in boundaries:
        if value <= upper:
            return f"{lower}–{upper}"
        lower = upper+1
    return f"{lower}+"


def matrix_metrics(matrix):
    count = int(matrix.sum())
    correct = int(np.trace(matrix))
    under, over = int(np.tril(matrix, -1).sum()), int(np.triu(matrix, 1).sum())
    class_counts = matrix.sum(1)
    supported = class_counts > 0
    macro = float(np.mean(np.diag(matrix)[supported]/class_counts[supported])) if supported.any() else None
    return {"stone_trials": count, "accuracy": correct/count if count else None,
            "macro_accuracy": macro, "overcounts": over, "undercounts": under,
            "confusion": matrix.tolist(), "class_counts": class_counts.tolist()}


def matrix_blocks(matrix):
    return ['```', str(matrix), '```', '', 'Overcounts only:', '```', str(np.triu(matrix, 1)),
            '```', '', 'Undercounts only:', '```', str(np.tril(matrix, -1)), '```', '']


def main():
    out = ROOT / "reports/checkpoint_audit"
    out.mkdir(parents=True, exist_ok=True)
    report = json.loads((ROOT / "reports/GPU_RESULTS.json").read_text())
    matrices = defaultdict(lambda: np.zeros((4, 4), np.int64))
    joint = defaultdict(lambda: np.zeros((4, 4), np.int64))
    features_by_dataset = {}
    for family in report["final_evaluations"]:
        source = ROOT / "results/final_liberties" / family["run"]
        for dataset in sorted((source / "data").glob("test_*.npz")):
            generator, size = dataset.stem.split("_")[1:]
            size = int(size)
            with np.load(dataset) as d:
                boards, labels = d["boards"], d["labels"]
            digest = __import__("hashlib").sha256(boards.tobytes()).hexdigest()
            if digest not in features_by_dataset:
                features_by_dataset[digest] = np.stack([chain_features(b) for b in boards])
            features = features_by_dataset[digest]
            mask = labels >= 0
            for prediction_file in sorted((source / "eval").glob(f"*_{generator}_{size}_d*_t*.npz")):
                depth = int(prediction_file.stem.split("_d")[1].split("_")[0])
                prediction = np.load(prediction_file)["predictions"]
                y, p = labels[mask], prediction[mask]
                if np.any(p < 0):
                    raise FloatingPointError(prediction_file)
                values = features[mask]
                raw = np.bincount(4*y+p, minlength=16).reshape(4, 4)
                matrices[(family["label"], size, depth, generator, "all", "all")] += raw
                for feature, indices, bins in (
                    ("diameter", values[:, 1], [4, 8, 16, 31, 63, 127]),
                    ("cycle", values[:, 2], []),
                    ("chain_size", values[:, 3], [1, 4, 8, 16, 32, 64, 128]),
                    ("edge_distance", values[:, 4], [0, 1, 2, 4, 8])):
                    for v in np.unique(indices):
                        selected = indices == v
                        bucket = ("cyclic" if v else "acyclic") if feature == "cycle" else bin_value(v, bins)
                        matrices[(family["label"], size, depth, generator, feature, bucket)] += np.bincount(4*y[selected]+p[selected], minlength=16).reshape(4, 4)
                inside = values[:, 1]+1 <= depth
                for flag in (False, True):
                    selected = inside == flag
                    matrices[(family["label"], size, depth, generator, "chain_distance_vs_depth", "inside" if flag else "outside")] += np.bincount(4*y[selected]+p[selected], minlength=16).reshape(4, 4)
                    geometric = (values[:, 5] <= depth) == flag
                    matrices[(family["label"], size, depth, generator, "liberties_vs_grid_light_cone", "inside" if flag else "outside")] += np.bincount(4*y[geometric]+p[geometric], minlength=16).reshape(4, 4)
                for d, c, s, e in np.unique(values[:, 1:5], axis=0):
                    selected = np.all(values[:, 1:5] == [d, c, s, e], axis=1)
                    joint[(family["label"], size, depth, generator,
                           bin_value(d, [4, 8, 16, 31, 63, 127]), int(c),
                           bin_value(s, [1, 4, 8, 16, 32, 64, 128]), bin_value(e, [0, 1, 2, 4, 8]))] += np.bincount(4*y[selected]+p[selected], minlength=16).reshape(4, 4)
            print(f"Audited {family['label']} {generator} {size}: {len(boards)} boards", flush=True)
    rows = []
    for key, matrix in sorted(matrices.items()):
        recipe, size, depth, generator, feature, bucket = key
        rows.append({"recipe": recipe, "size": size, "depth": depth, "generator": generator,
                     "feature": feature, "bucket": bucket, **matrix_metrics(matrix)})
    write_json(out / "stratified.json", rows)
    write_json(out / "joint_strata.json", [{"stratum": list(k), **matrix_metrics(v)} for k, v in sorted(joint.items())])
    with (out / "stratified.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[k for k in rows[0] if k not in ("confusion", "class_counts")])
        writer.writeheader()
        writer.writerows({k: v for k, v in r.items() if k not in ("confusion", "class_counts")} for r in rows)
    witness = []
    for summary in report["paired_evaluations"]:
        path = next((ROOT / "results/propagation_probe").glob(summary["created_utc"]+"*"))
        grouped = defaultdict(lambda: np.zeros((4, 4), np.int64))
        for record in summary["records"]:
            size, depth = record["size"], record["depth"]
            y = np.load(path / "data" / f"queries_{size}.npz")["labels"]
            name = f"{record['source_run']}_{record['variant']}_n{size}_d{depth}_t{record['trial']}.npz"
            p = np.load(path / "eval" / name)["predictions"]
            grouped[(record["source_run"], size, depth)] += np.bincount(4*y+p, minlength=16).reshape(4, 4)
        witness.extend({"run": k[0], "size": k[1], "depth": k[2], **matrix_metrics(m)} for k, m in sorted(grouped.items()))
    write_json(out / "witness_confusions.json", witness)
    lines = ["# Existing-checkpoint audit", "", "Descriptive analysis of already opened data; no training or checkpoint selection.",
             "Graph diameter + 1 is a chain-propagation proxy, not the grid NCA's exact receptive field. A chain outside this proxy can still be locally classifiable, especially in the 4+ class.", "",
             "Confusion rows are exact classes, columns predicted classes. Above diagonal = overcount; below diagonal = undercount. Values are capped liberty classes, not uncapped numerical errors.", ""]
    lines += ["## Interpretation", "",
              "A strict radius32 light cone cannot explain the 13x13, 19x19 or 25x25 errors: every board cell is within Chebyshev distance32 of every stone. At37x37, most errors still have every liberty within that radius. Chain graph distance strongly predicts failures, but this is descriptive correlation: it does not establish that a learned grid model routes only along chains.",
              "Raw cycle accuracies are confounded by liberty-class and chain-size distributions. Cycles are not the worst raw subgroup; the new sum/max and minimally perturbed pair experiments are needed to test double-counting. Longer rollout degradation is independently visible in the existing depth tables and saved trajectories.", ""]
    for size in (13, 19, 25, 37):
        outside = [r for r in rows if r["recipe"] == "Asynchronous" and r["size"] == size and r["depth"] == 32
                   and r["feature"] == "liberties_vs_grid_light_cone" and r["bucket"] == "outside"]
        total = [r for r in rows if r["recipe"] == "Asynchronous" and r["size"] == size and r["depth"] == 32 and r["feature"] == "all"]
        errors = sum(r["overcounts"]+r["undercounts"] for r in total)
        outside_errors = sum(r["overcounts"]+r["undercounts"] for r in outside)
        lines.append(f"- {size}x{size}: {outside_errors}/{errors} errors ({100*outside_errors/errors:.2f}%) have at least one liberty outside the strict grid radius32.")
    lines += ["", "## Final-test confusion matrices for all recipes and depths", ""]
    for recipe in sorted({r["recipe"] for r in rows}):
        for size in (9, 13, 19, 25, 37):
            for depth in (32, 64, 128, 256):
                selected = [r for r in rows if r["recipe"] == recipe and r["size"] == size and r["depth"] == depth and r["feature"] == "all"]
                matrix = sum((np.array(r["confusion"]) for r in selected), np.zeros((4, 4), np.int64))
                m = matrix_metrics(matrix)
                lines += [f"{recipe} size={size} depth={depth}: over={m['overcounts']} under={m['undercounts']}"] + matrix_blocks(matrix)
    for size in (13, 19, 25, 37):
        for feature in ("all", "diameter", "chain_distance_vs_depth", "liberties_vs_grid_light_cone", "cycle", "chain_size", "edge_distance"):
            selected = [r for r in rows if r["recipe"] == "Asynchronous" and r["size"] == size and r["depth"] == 32 and r["feature"] == feature]
            for bucket in sorted({r["bucket"] for r in selected}):
                matrix = sum((np.array(r["confusion"]) for r in selected if r["bucket"] == bucket), np.zeros((4, 4), np.int64))
                m = matrix_metrics(matrix)
                if not m["stone_trials"]:
                    continue
                lines += [f"## Main asynchronous model: {size}×{size}, {feature}={bucket}",
                          f"Stone accuracy {100*m['accuracy']:.2f}%; macro {100*m['macro_accuracy']:.2f}%; overcounts {m['overcounts']}; undercounts {m['undercounts']}"] + matrix_blocks(matrix)
    lines += ["## All witness confusion matrices", ""]
    for r in witness:
        lines += [f"{r['run']} size={r['size']} depth={r['depth']}: over={r['overcounts']} under={r['undercounts']}"] + matrix_blocks(np.array(r['confusion']))
    (out / "SUMMARY.md").write_text("\n".join(lines)+"\n")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for ax, feature in zip(axes.flat, ("diameter", "cycle", "chain_size", "edge_distance")):
        for size in (13, 19, 25, 37):
            selected = [r for r in rows if r["recipe"] == "Asynchronous" and r["size"] == size and r["depth"] == 32 and r["feature"] == feature]
            buckets = sorted({r["bucket"] for r in selected}, key=lambda v: int(v.split("–")[0].rstrip("+")) if v[0].isdigit() else v)
            accuracies = []
            for bucket in buckets:
                matrix = sum((np.array(r["confusion"]) for r in selected if r["bucket"] == bucket), np.zeros((4, 4), np.int64))
                accuracies.append(100*matrix_metrics(matrix)["accuracy"])
            ax.plot(buckets, accuracies, "o-", label=f"{size}×{size}")
        ax.set(title=feature.replace("_", " "), ylabel="Stone accuracy (%)", ylim=(0, 102))
        ax.tick_params(axis="x", rotation=30)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend()
    fig.savefig(out / "error_strata.png", dpi=160)
    plt.close(fig)
    trajectories = []
    for path in sorted((ROOT / "results/gpu_demo").glob("*/viz/trajectory.npz")):
        data = np.load(path)
        states, prediction = data["states"], data["predictions"]
        change = np.sqrt(np.mean(np.diff(states[..., 8:], axis=0)**2, axis=(1, 2, 3)))
        flips = np.mean(np.diff(prediction, axis=0) != 0, axis=(1, 2))
        stone_mask = data["target"] >= 0
        stone_flips = np.mean((prediction[1:] != prediction[:-1])[:, stone_mask], axis=1)
        trajectories.append({"run": path.parents[1].name, "scope": "predetermined validation board index zero",
                             "steps": list(range(2, len(states)+1)), "mutable_state_RMS_change": change.tolist(),
                             "all_cell_flip_rate": flips.tolist(), "stone_flip_rate": stone_flips.tolist()})
    write_json(out / "rollout_dynamics.json", trajectories)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    for r in trajectories:
        axes[0].plot(r["steps"], r["mutable_state_RMS_change"], label=r["run"])
        axes[1].plot(r["steps"], np.array(r["stone_flip_rate"])*100, label=r["run"])
    for ax in axes:
        ax.axvline(32, color="black", ls="--", label="trained horizon")
        ax.set_xlabel("Update step")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Mutable-state RMS step change")
    axes[1].set_ylabel("Stone predictions changing (%)")
    axes[1].legend(fontsize=6)
    fig.savefig(out / "rollout_dynamics.png", dpi=160)
    plt.close(fig)
    print(out / "SUMMARY.md", flush=True)


if __name__ == "__main__":
    main()
