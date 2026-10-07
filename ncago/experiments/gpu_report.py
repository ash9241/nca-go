"""Build an honest GPU investigation summary from recorded measurements."""
from collections import defaultdict
import json
from pathlib import Path

import numpy as np
import yaml
from .common import ROOT, write_json


def title(config, seed):
    scope = "whole board" if config.get("whole_board") else "target chain"
    parts = [f"C{config['channels']}", config['variants'][0].replace('_', ' ')]
    if config.get("normalization_groups"):
        parts.append("normalized")
    if config.get("gated"):
        parts.append("gated")
    if config.get("min_depth"):
        parts.append("varied horizon")
    if config.get("replay"):
        parts.append("replay")
    if config.get("curriculum"):
        parts.append("curriculum")
    if config.get("ema_decay"):
        parts.append("EMA + decay")
    if config.get("hint_weight"):
        parts.append("algorithm hints")
    if config.get("chain_messages"):
        parts.append("same-chain messages")
    if config.get("diverse_chains"):
        parts.append("diverse shapes")
    if len(config.get("train_sizes", [9])) > 1:
        parts.append("5–9 sizes")
    return ", ".join(parts)+f" | {scope} | seed {seed}"


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = []
    for path in sorted((ROOT / "results" / "learnability").glob("*/summary.json")):
        summary = json.loads(path.read_text())
        if not any("cuda" in d for d in summary["hardware"]["devices"]):
            continue
        config = yaml.safe_load((path.parent / "config.yaml").read_text())
        groups = defaultdict(list)
        for r in summary.get("records", []):
            groups[(r["split"], r["depth"])].append(r)
        measured = {}
        for (split, depth), values in groups.items():
            measured.setdefault(split, {})[str(depth)] = {
                k: float(np.mean([r[k] for r in values]))
                for k in ("macro_stone_accuracy", "stone_accuracy", "target_chain_exact", "board_exact")
                if k in values[0]}
            measured[split][str(depth)]["per_class_accuracy"] = np.mean(
                [r["per_class_accuracy"] for r in values], axis=0).tolist()
        rows.append({"run": path.parent.name, "label": title(config, summary["seed"]),
                     "status": summary["status"], "seed": summary["seed"],
                     "config": config, "measurements": measured,
                     "error": summary.get("error"), "source_commit": summary.get("commit")})
    output = ROOT / "reports" / "gpu_investigation.json"
    workers = [json.loads(p.read_text()) for p in (ROOT / "results" / "cloud").glob("*worker.json")]
    write_json(output, {"workers": workers,
                        "scope": "Training/validation investigation; sealed G1 and larger final tests are separate",
                        "experiments": rows})
    completed = [r for r in rows if r["status"] == "measured"]
    if completed:
        fig, axes = plt.subplots(1, 2, figsize=(14, max(5, len(completed)*.48)), layout="constrained")
        y = np.arange(len(completed))
        for ax, split, label in zip(axes, ("validation9", "validation13"), ("Held-out 9×9", "Larger validation 13×13")):
            for offset, multiplier, color in ((-.25, 1, "#28658b"), (0, 2, "#dc9340"), (.25, 4, "#8874a0")):
                values = [100*r["measurements"][split][str(multiplier*r["config"]["rollout_steps"])]["macro_stone_accuracy"]
                          for r in completed]
                ax.barh(y+offset, values, height=.24, color=color, label=f"{multiplier}× training depth")
            ax.axvline(25, color="#666", ls=":", lw=1)
            ax.set_xlim(0, 102)
            ax.invert_yaxis()
            ax.set_title(label)
            ax.set_xlabel("Class-balanced per-stone accuracy (%)")
            ax.spines[["top", "right"]].set_visible(False)
        axes[0].set_yticks(y, [r["label"] for r in completed], fontsize=8)
        axes[1].set_yticks(y, [])
        axes[1].legend(loc="lower right", fontsize=8)
        fig.suptitle("A100 liberty investigation: accuracy and rollout stability", fontsize=13)
        fig.savefig(output.with_suffix(".png"), dpi=160, bbox_inches="tight")
        plt.close(fig)
    markdown = ["# GPU liberty investigation", "",
                "Measured training/validation results from the dedicated A100 worker. "
                "Target-chain rows supervise one constructed chain per board; whole-board rows supervise all stones. "
                "Neither is a sealed final G1 result. Constant class predictions score 25% on the macro metric.", "",
                "| Experiment | Boards / updates | 9×9 at trained depth | 9×9 at 4× depth | 13×13 at trained depth | Status |",
                "|---|---:|---:|---:|---:|---|"]
    for r in rows:
        c, m = r["config"], r["measurements"]
        def cell(split, multiplier):
            v = m.get(split, {}).get(str(multiplier*c["rollout_steps"]), {}).get("macro_stone_accuracy")
            return f"{100*v:.2f}%" if v is not None else "—"
        readable_label = r['label'].replace('|', '·')
        markdown.append(f"| {readable_label} | {c['train_count']:,} / {c['training_steps']:,} | "
                        f"{cell('validation9', 1)} | {cell('validation9', 4)} | {cell('validation13', 1)} | {r['status']} |")
    markdown += ["", "Raw summaries, source snapshots, logs, dataset files, and checkpoints are stored under "
                 "`results/learnability/<run>/`. Each row's source revision is included in the JSON report.", "",
                 "The experiments vary capacity, loss/readout, curriculum, replay, normalization, "
                 "weight averaging, learning-rate decay, gating, rollout horizon and training board size. "
                 "Only matched recipes isolate a single factor; combined recipe improvements do not establish "
                 "which individual change caused them.", ""]
    output.with_suffix(".md").write_text("\n".join(markdown))
    print(output)


if __name__ == "__main__":
    build()
