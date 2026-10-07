"""Regenerate the learnability chart and compact evidence from two saved runs."""
import argparse
import json
from pathlib import Path

import numpy as np

from .common import ROOT, write_json


def aggregate(rows, variant, split, depth):
    chosen = [r["macro_stone_accuracy"] for r in rows
              if (r["variant"], r["split"], r["depth"]) == (variant, split, depth)]
    if not chosen:
        raise ValueError(f"Missing measurement: {variant}, {split}, {depth}")
    return float(np.mean(chosen))


def build(small_run, replay_run):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import yaml

    small_run, replay_run = Path(small_run), Path(replay_run)
    a = json.loads((small_run / "eval" / "scores.json").read_text())
    b = json.loads((replay_run / "eval" / "scores.json").read_text())
    config = yaml.safe_load((small_run / "config.yaml").read_text())
    variants = ["mse_all", "mse_late", "ce_late", "ce_late_async"]
    depth = config["rollout_steps"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout="constrained")
    x = np.arange(len(variants))
    for offset, split, label, color in [(-.18, "train", "Training chains", "#236f9b"),
                                      (.18, "validation9", "Held-out 9x9 chains", "#e09c39")]:
        axes[0].bar(x + offset, [100 * aggregate(a, v, split, depth) for v in variants],
                    width=.36, label=label, color=color)
    axes[0].axhline(25, color="#777", ls=":", label="Constant prediction (25%)")
    axes[0].set_xticks(x, ["MSE\nall steps", "MSE\nlate loss", "CE\nlate loss", "CE async\nlate loss"])
    axes[0].set_title("Small-set fit and held-out accuracy", fontsize=11)
    axes[0].set_ylabel("Class-balanced accuracy (%)")
    axes[0].legend(fontsize=8, loc="upper center", bbox_to_anchor=(.5, -.2), ncol=2)
    depths = sorted({r["depth"] for r in a if r["variant"] == "ce_late"})
    for split, label, color in [("train", "Training", "#236f9b"),
                                ("validation9", "Held-out 9x9", "#e09c39"),
                                ("validation13", "Validation 13x13", "#8b6d9e")]:
        axes[1].plot(depths, [100 * aggregate(a, "ce_late", split, d) for d in depths],
                     "-o", label=label, color=color)
    axes[1].axhline(25, color="#777", ls=":")
    axes[1].set_title("Extra steps degrade the small-set CE model", fontsize=11)
    axes[1].set_xlabel("Rollout steps")
    axes[1].set_xticks(depths)
    axes[1].legend(fontsize=8, loc="upper center", bbox_to_anchor=(.5, -.2), ncol=2)
    for ax in axes:
        ax.set_ylim(0, 105)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Liberty probes: {config['train_count']} balanced target chains, "
                 f"{config['training_steps']:,} updates, one training seed", fontsize=11)
    output = ROOT / "reports" / "learnability_diagnostic.png"
    fig.savefig(output, dpi=180, bbox_inches="tight", pad_inches=.15)
    plt.close(fig)
    replay_depths = sorted({r["depth"] for r in b})
    summary = {
        "source_runs": [str(small_run), str(replay_run)],
        "scope": "Constructed target chains only; not whole-board G1; no final test boards evaluated",
        "training_rollout_depth": depth,
        "longer_rollout_depth": max(depths),
        "small_set": {v: {"train": aggregate(a, v, "train", depth),
                          "validation9": aggregate(a, v, "validation9", depth),
                          "validation13": aggregate(a, v, "validation13", depth),
                          "train_at_longer_depth": aggregate(a, v, "train", max(depths))} for v in variants},
        "combined_replay_pilot": {split: {str(d): aggregate(b, "ce_late_async", split, d)
                                           for d in replay_depths}
                                  for split in ["train", "validation9", "validation13"]},
        "limitations": ["One training seed", "No matched learned baseline in this diagnostic",
                        "Replay pilot changes data, augmentation, initial noise, depth and optimizer together; no isolated causal attribution",
                        "Final weights used; no checkpoint selection"],
    }
    write_json(output.with_suffix(".json"), summary)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("small_run", type=Path)
    parser.add_argument("replay_run", type=Path)
    args = parser.parse_args()
    build(args.small_run, args.replay_run)
