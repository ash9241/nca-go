"""Render a recorded GPU model on a predetermined held-out validation board."""
import argparse
import hashlib
from pathlib import Path
import imageio.v2 as imageio
import jax
import numpy as np
from .common import ROOT, Run
from .propagation_probe import load_checkpoint
from ncago.nca.model import initialize, rollout
from ncago.viz.boards import board, hidden_rgb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--variant", default="ce_late")
    parser.add_argument("--split", default="validation9")
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    model, params, digest, training = load_checkpoint(args.run, args.variant)
    source = args.run / "data" / f"{args.split}.npz"
    with np.load(source) as data:
        tokens, target = data["boards"][args.index], data["labels"][args.index]
    run = Run("gpu_demo", {"source_run": args.run.name, "variant": args.variant,
        "checkpoint_sha256": digest, "split": args.split, "board_index": args.index,
        "input_data_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "depth": 128,
        "scope": "Predetermined single-board illustration; aggregate metrics are evaluated separately"})
    key = jax.random.PRNGKey(76001)
    state = initialize(tokens[None], key, model.config)
    _, (prediction, confidence, fire, states) = jax.jit(lambda s: rollout(model, params, s, tokens[None], key, 128, keep_states=True))(state)
    prediction, confidence, fire, states = map(np.asarray, (prediction[:, 0], confidence[:, 0], fire[:, 0], states))
    np.savez_compressed(run.path / "viz" / "trajectory.npz", board=tokens, target=target,
        predictions=prediction, confidence=confidence, fire=fire, states=states, steps=np.arange(1, 129))
    rgb = hidden_rgb(states, model.config.input_channels, model.config.output_channels)
    mask = target >= 0
    accuracy = ((prediction == target) & mask).sum((1, 2))/mask.sum()
    import matplotlib.pyplot as plt

    def labels(ax, values, errors=False):
        board(ax, tokens)
        for r, c in np.argwhere(mask):
            value = int(values[r, c])
            label = str(value+1) if value < 3 else "4+"
            ax.text(c, r, label, ha="center", va="center", fontsize=8,
                    color="#dd342f" if errors and value != target[r, c] else ("white" if tokens[r, c] == 1 else "#172331"), zorder=4)

    frames = []
    selected = [1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]
    for depth in selected:
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5), layout="constrained")
        labels(axes[0], target)
        axes[0].set_title("Exact liberty counts", fontsize=11)
        labels(axes[1], prediction[depth-1], True)
        axes[1].set_title(f"Learned counts · step {depth} · {100*accuracy[depth-1]:.1f}% correct", fontsize=11)
        axes[2].imshow(rgb[depth-1], origin="lower")
        axes[2].set_title("Hidden state · shared PCA projection", fontsize=11)
        axes[2].axis("off")
        fig.suptitle(f"Held-out {len(tokens)}×{len(tokens)} board · trained at {training['rollout_steps']} steps · red numbers are errors", fontsize=10)
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        plt.close(fig)
    output = ROOT / "reports" / "figures"
    output.mkdir(exist_ok=True)
    imageio.mimsave(output / "gpu_rollout.gif", frames, duration=650, loop=0)
    # Filmstrip explicitly includes steps past the trained horizon.
    chosen = [1, 4, 8, 16, 32, 64, 128]
    fig, axes = plt.subplots(2, len(chosen), figsize=(17, 5), layout="constrained")
    for column, depth in enumerate(chosen):
        labels(axes[0, column], prediction[depth-1], True)
        axes[0, column].set_title(f"Step {depth}: {100*accuracy[depth-1]:.1f}%", fontsize=10)
        axes[1, column].imshow(rgb[depth-1], origin="lower")
        axes[1, column].axis("off")
    fig.suptitle(f"Predetermined held-out board · learned counts (red = wrong) and hidden PCA · trained at {training['rollout_steps']} steps", fontsize=12)
    fig.savefig(output / "gpu_rollout.png", dpi=160)
    plt.close(fig)
    run.finish("visualized", per_step_stone_accuracy=accuracy.tolist(),
               selected_steps=selected, accuracy_gate_certified=False)
    print(output / "gpu_rollout.gif")


if __name__ == "__main__":
    main()
