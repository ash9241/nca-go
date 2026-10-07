"""CPU replay of existing checkpoints on fixed batches, without training."""
import json
import jax
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from .common import ROOT, write_json
from .propagation_probe import load_checkpoint
from .research_train import make_predict, evaluate


def main():
    if any(d.platform != "cpu" for d in jax.devices()):
        raise RuntimeError("This existing-checkpoint audit is explicitly CPU-only")
    report = json.loads((ROOT / "reports/GPU_RESULTS.json").read_text())
    records = []
    for family in report["final_evaluations"][:2]:
        dataset = ROOT / "results/final_liberties" / family["run"] / "data"
        checkpoints = family["manifest"]["checkpoints"]
        for entry in checkpoints:
            source = ROOT / "results/learnability" / __import__("pathlib").Path(entry["run_path"]).name
            model, params, digest, _ = load_checkpoint(source, entry["variant"])
            predict = make_predict(model, model.config)
            for size in (9, 13, 37):
                boards, labels = [], []
                for generator in ("random", "structured"):
                    with np.load(dataset / f"test_{generator}_{size}.npz") as d:
                        boards.append(d["boards"][:16])
                        labels.append(d["labels"][:16])
                boards, labels = np.concatenate(boards), np.concatenate(labels)
                _, dynamics = evaluate(predict, params, (boards, labels), (32, 64, 128, 256),
                                       jax.random.PRNGKey(96001), batch=16)
                records.append(dict(recipe=family["label"], seed=entry["seed"], size=size,
                                    checkpoint_sha256=digest, board_count=len(boards),
                                    selection="first16 random + first16 structured; fixed before replay",
                                    steps=list(range(1, 257)), mutable_state_RMS_change=dynamics[:, 0].tolist(),
                                    stone_prediction_flip_rate=dynamics[:, 1].tolist()))
                print(f"CPU rollout audit {family['label']} seed{entry['seed']} size{size}", flush=True)
    out = ROOT / "reports/checkpoint_audit"
    write_json(out / "batched_rollout_dynamics.json", records)
    fig, axes = plt.subplots(2, 3, figsize=(14, 7), layout="constrained")
    for j, size in enumerate((9, 13, 37)):
        for recipe in sorted({r["recipe"] for r in records}):
            rows = [r for r in records if r["recipe"] == recipe and r["size"] == size]
            for ax, metric in ((axes[0, j], "mutable_state_RMS_change"), (axes[1, j], "stone_prediction_flip_rate")):
                values = np.asarray([r[metric] for r in rows])
                ax.plot(np.arange(1, 257), values.mean(0), label=recipe)
                ax.fill_between(np.arange(1, 257), values.min(0), values.max(0), alpha=.15)
                ax.axvline(32, color="black", ls="--")
                ax.spines[["top", "right"]].set_visible(False)
                ax.set(xlabel="Step", title=f"{size}x{size}")
    axes[0, 0].set_ylabel("Mutable-state RMS change")
    axes[1, 0].set_ylabel("Stone prediction flip fraction")
    axes[0, 0].legend()
    fig.savefig(out / "batched_rollout_dynamics.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
