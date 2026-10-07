"""Make publication media from saved trajectories and frozen checkpoints.

No training or outcome-based example selection. The distant example is pair zero,
trial zero from the sealed query set, using the evaluator's coupled random keys.
"""
import hashlib
import json
from pathlib import Path
import subprocess

import imageio.v2 as imageio
import jax
import jax.numpy as jnp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
import numpy as np

from .common import ROOT, write_json
from .propagation_probe import load_checkpoint
from ncago.nca.model import initialize, readout, step
from ncago.viz.boards import board, hidden_rgb

OUT = ROOT / "reports" / "shareable" / "media"
DEMO = ROOT / "results/gpu_demo/20261006T212604994817Z_581e2df5_s0"
PROBE = ROOT / "results/propagation_probe/20261006T212216958801Z_03a04154_s0"
GRAPH = ROOT / "results/learnability/20261006T201026705778Z_5c97d885_s0"


def video_from_frames(frames, path, fps=4):
    """Encode actual rendered frames as broadly supported H.264/yuv420p."""
    height, width = frames[0].shape[:2]
    process = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps),
        "-i", "-", "-an", "-c:v", "libx264", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)
    ], stdin=subprocess.PIPE)
    for frame in frames:
        process.stdin.write(np.ascontiguousarray(frame[..., :3], dtype=np.uint8).tobytes())
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"Video encoding failed: {path}")


def labels(ax, stones, values, target, error_colors=False):
    board(ax, stones)
    for r, c in np.argwhere(target >= 0):
        value = int(values[r, c])
        text = str(value+1) if value < 3 else "4+"
        color = "#d94838" if error_colors and value != target[r, c] else (
            "white" if stones[r, c] == 1 else "#172331")
        ax.text(c, r, text, ha="center", va="center", fontsize=13, color=color, zorder=4)


def whole_board_movie():
    with np.load(DEMO / "viz/trajectory.npz") as data:
        stones, target, predictions, states = [data[k] for k in (
            "board", "target", "predictions", "states")]
    rgb = hidden_rgb(states, 8, 4)
    mask = target >= 0
    accuracy = ((predictions == target) & mask).sum((1, 2))/mask.sum()*100
    selected = [1, 2, 4, 6, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 80, 96, 112, 128]
    frames = []
    for depth in selected:
        fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#f7f8fa")
        grid = fig.add_gridspec(2, 3, height_ratios=[3.3, 1],
                               top=.82, bottom=.14, left=.04, right=.97,
                               hspace=.32, wspace=.15)
        truth, learned, hidden = [fig.add_subplot(grid[0, i]) for i in range(3)]
        labels(truth, stones, target, target)
        truth.set_title("Exact liberty classes", fontsize=15, pad=12)
        labels(learned, stones, predictions[depth-1], target, True)
        learned.set_title(f"Learned: {accuracy[depth-1]:.1f}% correct", fontsize=15, pad=12)
        hidden.imshow(rgb[depth-1], origin="lower")
        hidden.set_title("Hidden state: shared PCA", fontsize=15, pad=12)
        hidden.axis("off")
        curve = fig.add_subplot(grid[1, :])
        curve.plot(np.arange(1, 129), accuracy, color="#246e9d", lw=2)
        curve.axvline(32, color="#c27a27", ls="--", lw=1.4)
        curve.axvline(depth, color="#172331", alpha=.5)
        curve.scatter([depth], [accuracy[depth-1]], color="#172331", zorder=5)
        curve.set(xlim=(1, 128), ylim=(0, 104), ylabel="Correct (%)",
                  xlabel="NCA update steps")
        curve.set_xticks([1, 16, 32, 64, 96, 128])
        curve.spines[["top", "right"]].set_visible(False)
        fig.text(.04, .94, "Learning to count Go liberties", fontsize=24, weight="bold", color="#172331")
        fig.text(.04, .885, f"Recorded step {depth} / 128   |   trained at 32 steps   |   red numbers are errors", fontsize=14, color="#516373")
        fig.text(.04, .035, "Predetermined 9×9 validation board, index 0. One illustration; final test mean: 99.89% across 3 training seeds.", fontsize=11, color="#516373")
        fig.canvas.draw()
        frame = np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()
        frames.extend([frame]*(7 if depth == 32 else 3 if depth in (1, 64, 128) else 2))
        plt.close(fig)
    video_from_frames(frames, OUT / "liberties_rollout.mp4")
    print("Rendered liberty video", flush=True)


def distant_movie():
    model, params, digest, _ = load_checkpoint(GRAPH, "ce_late_async")
    with np.load(PROBE / "data/queries_37.npz") as data:
        stones, query, target = data["boards"][:2], data["queries"][0], data["labels"][:2]
    key = jax.random.fold_in(jax.random.PRNGKey(300000), 0)
    trial_key = jax.random.fold_in(key, 0)

    def one(tokens):
        tokens = tokens[None]
        state = initialize(tokens, trial_key, model.config)
        def body(s, i):
            updated = step(model, params, s, tokens, jax.random.fold_in(trial_key, i))[0]
            prediction, _ = readout(model, params, updated)
            return updated, (updated[0], prediction[0])
        return jax.lax.scan(body, state, jnp.arange(128))[1]
    states, predictions = map(np.asarray, jax.jit(jax.vmap(one))(jnp.asarray(stones)))
    qpred = predictions[:, :, query[0], query[1]]
    frozen = np.load(next((PROBE / "eval").glob(f"{GRAPH.name}*_n37_d64_t0.npz")))["predictions"][:2]
    np.testing.assert_array_equal(qpred[:, 63], frozen)
    delta = np.linalg.norm(states[0, ..., 8:]-states[1, ..., 8:], axis=-1)
    assert np.all(delta[:32, query[0], query[1]] == 0), "Signal violated its causal distance"
    change = np.argwhere(stones[0] != stones[1])[0]
    np.savez_compressed(OUT / "distant_pair_trajectory.npz", boards=stones,
                        query=query, changed_cell=change, target=target,
                        query_predictions=qpred, mutable_state_difference=delta)
    metadata = {"checkpoint_sha256": digest, "source_run": GRAPH.name,
                "dataset": f"results/propagation_probe/{PROBE.name}/data/queries_37.npz",
                "dataset_sha256": hashlib.sha256((PROBE / "data/queries_37.npz").read_bytes()).hexdigest(),
                "pair_index": 0, "trial": 0, "coupled_randomness": True,
                "selection": "First recorded sealed pair; no selection by outcome",
                "query": query.tolist(), "changed_cell": change.tolist(),
                "predicted_at_frozen_depth_64": (qpred[:, 63]+1).tolist(),
                "exact_classes": (target+1).tolist(),
                "matched_saved_evaluator_predictions": True,
                "interpretation": "State differences visualize causal influence, not a decoded exact counting algorithm"}
    write_json(OUT / "distant_pair.source.json", metadata)
    selected = [1, 4, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 128]
    frames = []
    for depth in selected:
        fig, axes = plt.subplots(1, 3, figsize=(12.8, 7.2), dpi=100, facecolor="#f7f8fa")
        fig.subplots_adjust(top=.78, bottom=.19, left=.025, right=.92, wspace=.13)
        for i in range(2):
            board(axes[i], stones[i])
            axes[i].set_title(f"True class: {target[i]+1}   |   predicted: {qpred[i, depth-1]+1}", fontsize=14, pad=14)
        image = axes[2].imshow(delta[depth-1]+1e-8, origin="lower", cmap="magma",
                               norm=LogNorm(vmin=1e-7, vmax=max(1., float(delta.max()))))
        axes[2].set_title("Where mutable states differ", fontsize=14, pad=14)
        axes[2].set_xticks([])
        axes[2].set_yticks([])
        for ax in axes:
            for point, color, radius in ((query, "#20c5db", .8), (change, "#ec913a", .8)):
                ax.add_patch(Circle((point[1], point[0]), radius=radius, edgecolor=color,
                                    facecolor="none", lw=2.5, zorder=5))
        fig.colorbar(image, ax=axes[2], fraction=.045, pad=.025, label="State difference (log scale)")
        fig.text(.03, .935, "A distant change reaches the query", fontsize=24, weight="bold", color="#172331")
        fig.text(.03, .875, f"37×37 paired inputs   |   update step {depth}   |   changed cell is 34 grid steps away", fontsize=14, color="#516373")
        fig.text(.03, .11, "Cyan = query; orange = only changed input. Firing is identical within the pair. Training sizes: 5–9.", fontsize=12, color="#516373")
        fig.text(.03, .065, "First sealed pair, trial 0: the model misses one answer at step 64. Aggregate over the witness family: 74.74%.", fontsize=11, color="#516373")
        fig.text(.03, .025, "Hidden-state differences establish influence. They do not establish exact algorithm recovery or convergence.", fontsize=10, color="#516373")
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        plt.close(fig)
    imageio.mimsave(OUT / "distant_pair_rollout.gif", frames, duration=800, loop=0)
    video_from_frames([frame for frame in frames for _ in range(3)], OUT / "distant_pair_rollout.mp4")
    imageio.imwrite(OUT / "distant_pair_poster.png", frames[selected.index(64)])
    print("Rendered distant video; first-pair predictions match frozen evaluation", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    whole_board_movie()
    distant_movie()


if __name__ == "__main__":
    main()
