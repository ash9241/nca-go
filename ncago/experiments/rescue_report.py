"""Summarize frozen final evaluations with uncertainty from saved predictions."""
import argparse
from collections import defaultdict
import html
import json
from pathlib import Path
import numpy as np
import yaml
from .common import ROOT, write_json


def render_markdown(lines):
    """Render this report's limited, generated Markdown into readable HTML."""
    blocks, code, table = [], None, False
    for line in lines:
        if line.startswith("```"):
            if code is None:
                code = []
            else:
                blocks.append("<pre><code>"+html.escape("\n".join(code))+"</code></pre>")
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if line.startswith("|"):
            if set(line.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
                continue
            cells = [html.escape(cell.strip()) for cell in line.strip("|").split("|")]
            if not table:
                blocks.append('<div class="table"><table><thead><tr>'+"".join(f"<th>{c}</th>" for c in cells)+"</tr></thead><tbody>")
                table = True
            else:
                blocks.append("<tr>"+"".join(f"<td>{c}</td>" for c in cells)+"</tr>")
            continue
        if table:
            blocks.append("</tbody></table></div>")
            table = False
        if line.startswith("#"):
            level = len(line)-len(line.lstrip("#"))
            blocks.append(f"<h{level}>{html.escape(line[level:].strip())}</h{level}>")
        elif line:
            blocks.append("<p>"+html.escape(line)+"</p>")
    if table:
        blocks.append("</tbody></table></div>")
    return "\n".join(blocks)


def aggregate(path, bootstrap_samples=2000):
    summary = json.loads((path / "summary.json").read_text())
    config = yaml.safe_load((path / "config.yaml").read_text())
    manifest = config["manifest"]
    grouped = defaultdict(list)
    for record in summary["records"]:
        grouped[(record["size"], record["depth"])].append(record)
    measurements = []
    rng = np.random.default_rng(75001)
    for (size, depth), records in sorted(grouped.items()):
        seeds = sorted({r["training_seed"] for r in records})
        correct, counts, exact, classes = {}, {}, {}, {}
        per_seed = []
        for seed in seeds:
            correct[seed], counts[seed], exact[seed], classes[seed] = {}, {}, {}, {}
            for generator in ("random", "structured"):
                labels = np.load(path / "data" / f"test_{generator}_{size}.npz")["labels"]
                mask = labels >= 0
                trials = sorted({r["trial"] for r in records if r["training_seed"] == seed and r["generator"] == generator})
                predictions = np.stack([np.load(path / "eval" / f"{seed}_{generator}_{size}_d{depth}_t{trial}.npz")["predictions"] for trial in trials])
                matches = (predictions == labels) & mask
                correct[seed][generator] = matches.sum((2, 3)).mean(0)
                counts[seed][generator] = mask.sum((1, 2))
                exact[seed][generator] = ((predictions == labels) | ~mask).all((2, 3)).mean(0)
                classes[seed][generator] = [(float((matches & (labels == v)).sum()) / len(trials), int((labels == v).sum())) for v in range(4)]
            stone = sum(a.sum() for a in correct[seed].values()) / sum(a.sum() for a in counts[seed].values())
            class_accuracy = [sum(classes[seed][g][v][0] for g in classes[seed]) / sum(classes[seed][g][v][1] for g in classes[seed]) for v in range(4)]
            per_seed.append({"seed": seed, "stone_accuracy": float(stone), "macro_accuracy": float(np.mean(class_accuracy)),
                             "per_class_accuracy": class_accuracy, "board_exact": float(np.concatenate(list(exact[seed].values())).mean())})
        # Stratified board bootstrap, averaging fixed training seeds and trials.
        bootstrap = np.zeros(bootstrap_samples)
        denominator = np.zeros(bootstrap_samples)
        for generator in ("random", "structured"):
            average_correct = np.mean([correct[s][generator] for s in seeds], axis=0)
            n = len(average_correct)
            indices = rng.integers(n, size=(bootstrap_samples, n))
            bootstrap += average_correct[indices].sum(1)
            denominator += counts[seeds[0]][generator][indices].sum(1)
        estimates = [r["stone_accuracy"] for r in per_seed]
        measurements.append({"size": size, "depth": depth, "primary": depth == manifest["primary_depth"],
                             "per_seed": per_seed, "stone_mean": float(np.mean(estimates)),
                             "stone_seed_std": float(np.std(estimates, ddof=1)) if len(seeds) > 1 else None,
                             "stone_board_bootstrap_95": np.quantile(bootstrap/denominator, [.025, .975]).tolist(),
                             "macro_mean": float(np.mean([r["macro_accuracy"] for r in per_seed])),
                             "board_exact_mean": float(np.mean([r["board_exact"] for r in per_seed]))})
    source = Path(manifest["checkpoints"][0]["run_path"]).name
    local_source = ROOT / "results" / "learnability" / source
    training = yaml.safe_load((local_source / "config.yaml").read_text())
    variant = manifest["checkpoints"][0]["variant"]
    label = ("Asynchronous" if "async" in variant else "Synchronous") + (" + algorithm hints" if training.get("hint_weight") else "")
    if training.get("channels", 64) != 64:
        label = f"C{training['channels']} "+label
    return {"run": path.name, "label": label, "G1_passed": summary["accuracy_gate_certified"],
            "G1_per_seed": summary["G1_per_seed"], "manifest": manifest, "training_config": training,
            "measurements": measurements}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-runs", type=Path, nargs="+", required=True)
    parser.add_argument("--paired-runs", type=Path, nargs="*", default=[])
    args = parser.parse_args()
    results = [aggregate(path) for path in args.final_runs]
    pairs = []
    for path in args.paired_runs:
        item = json.loads((path / "summary.json").read_text())
        item["evaluation_scope"] = yaml.safe_load((path / "config.yaml").read_text())["scope"]
        pairs.append(item)
    output = ROOT / "reports" / "GPU_RESULTS"
    write_json(output.with_suffix(".json"), {"final_evaluations": results, "paired_evaluations": pairs,
               "uncertainty": "Training-seed sample standard deviation; stratified board bootstrap conditional on recorded training seeds and firing trials"})
    paragraphs = ["# A100 investigation: final results", "",
        "Frozen checkpoints evaluated on fresh final boards. Every previously opened dataset is excluded up to rotation, reflection and color swap. The primary inference depth was frozen before opening these boards. Larger-board results were not used to retune the models.", "",
        "| Recipe | Training seeds | 9×9 accuracy per seed | G1 accuracy threshold |",
        "|---|---|---|---|"]
    asynchronous = next((r for r in results if r["label"] == "Asynchronous"), None)
    if asynchronous:
        primary = next(r for r in asynchronous["measurements"] if r["size"] == 9 and r["primary"])
        statement = (f"The asynchronous whole-board model passes the numeric G1 threshold in every recorded training seed: "
                     f"{100*primary['stone_mean']:.3f}% mean per-stone accuracy and {100*primary['macro_mean']:.3f}% class-balanced accuracy. "
                     "The improvement is reproducible on independent 9×9 positions. Exact generalization to arbitrary larger boards remains unresolved.")
        paragraphs[2:2] = [statement, ""]
    for result in results:
        paragraphs.append(f"| {result['label']} | {', '.join(result['G1_per_seed'])} | "+", ".join(f"{100*v:.4f}%" for v in result['G1_per_seed'].values())+f" | {'Passed' if result['G1_passed'] else 'Failed'} |")
    paragraphs += ["", "## Independent final accuracy", "",
        "Per-stone results pool random and controlled positions. Macro accuracy weights all four liberty classes equally; board exactness requires every stone to be correct. The bootstrap resamples boards within each generator, preserving shared test boards across seeds. It does not certify arbitrary Go positions.", "",
        "| Recipe | Board | Depth | Stone mean ± seed SD | Board bootstrap 95% interval | Macro mean | Boards entirely correct |",
        "|---|---|---:|---:|---:|---:|---:|"]
    for result in results:
        for row in result["measurements"]:
            if not row["primary"]:
                continue
            sd = row["stone_seed_std"]
            estimate = f"{100*row['stone_mean']:.3f}%"+(f" ± {100*sd:.3f}%" if sd is not None else " (one seed)")
            lo, hi = row["stone_board_bootstrap_95"]
            paragraphs.append(f"| {result['label']} | {row['size']}×{row['size']} | {row['depth']} | {estimate} | {100*lo:.3f}–{100*hi:.3f}% | {100*row['macro_mean']:.2f}% | {100*row['board_exact_mean']:.2f}% |")
    paragraphs += ["", "## What changed and why", "",
        "The CPU smoke run established that the pipeline worked but failed to learn liberty counting. The GPU sweep varied width, readout/loss, replay, curriculum, normalization, rollout horizon, initialization, gating, intermediate supervision and training board sizes. All completed, failed and interrupted attempts remain recorded in gpu_investigation.md.", "",
        "The successful whole-board recipe balances class contributions, uses a late cross-entropy loss, wider cells, augmentation, a decaying learning rate, final weight averaging and a bounded gated update. Those changes address majority-class collapse and recurrent optimization. Several were combined, so this sweep does not identify a unique cause for the entire improvement. Matched experiments isolate the effect of asynchronous firing and auxiliary algorithm supervision.", "",
        "Auxiliary hints teach each cell how many distinct liberties have reached it so far. An exact local algorithm supplies training labels. Its IDs and hidden states are never inputs to neural inference. The message-routing experiment additionally restricts hidden communication to orthogonally adjacent stones of the same color; that is an explicit Go connectivity prior. Its component neighborhoods are deduplicated across splits, including translation and irrelevant clutter.", "",
        "Passing the numeric G1 threshold does not establish the original stronger hypothesis of exact size generalization. Synchronous results use a plain recurrent cell model; the asynchronous variant retains stochastic local firing. More rollout steps can reduce accuracy, and large-board averages can hide failure on a distant-information witness. Life, ladders and playing strength have not been rescued by these liberty experiments.", ""]
    if pairs:
        paragraphs += ["## Distant-information tests", "",
            "Each pair differs at one distant cell and has identical query neighborhoods inside that distance. Firing and initial noise are coupled within the pair. A fixed CNN whose receptive-field radius is nine cannot exceed 50% query accuracy when the changed input is farther away. This is a structural upper bound, not an empirical CNN training comparison.", "",
            "The table includes every measured depth; the sealed graph-family primary depth is 64. Each size uses one distant-query geometry with rotations, color swaps and surrounding clutter. These repeated variants do not establish broad chain-shape generalization.", "",
            "| Model | Board | Steps | Distance | Query accuracy | Both pair answers correct |",
            "|---|---|---:|---:|---:|---:|"]
        witness = [r for s in pairs if s["evaluation_scope"] == "sealed paired-query family" for r in s["records"]
                   if r["size"] == 37 and r["depth"] == 64 and r["model_config"].get("algorithm_hints") and r["model_config"]["fire_rate"] < 1]
        if witness:
            from ncago.baselines.resnet import ResNet
            radius = ResNet(classes=4, blocks=16).receptive_field_radius
            paragraphs[-3:-3] = [f"The separately trained asynchronous graph model with intermediate hints reaches {100*np.mean([r['query_accuracy'] for r in witness]):.2f}% "
                f"on the sealed 37×37 witness at the frozen depth of 64. The changed cell is {witness[0]['causal_distance']} grid steps away; "
                f"the supplied 16-block CNN has radius {radius} and therefore cannot exceed 50% on these balanced pairs. "
                "The graph model uses training sizes 5–9, an explicit connectivity prior and one training seed with three firing trials. "
                "This supports a narrow learned-propagation claim. Its later accuracy declines, so it does not certify convergence or exact liberty counting.", ""]
        grouped = defaultdict(list)
        for summary in pairs:
            for row in summary["records"]:
                grouped[(row["source_run"], row["size"], row["depth"], row["causal_distance"])].append(row)
        for (source, size, depth, distance), rows in sorted(grouped.items()):
            c = yaml.safe_load((ROOT / "results" / "learnability" / source / "config.yaml").read_text())
            model_label = ("Graph" if c.get("chain_messages") else "Grid")+": "+("async" if "async" in c["variants"][0] else "sync")+(" + hints" if c.get("hint_weight") else "")+(" target chain" if not c.get("whole_board") else " whole board")
            paragraphs.append(f"| {model_label} | {size}×{size} | {depth} | {distance} | {100*np.mean([r['query_accuracy'] for r in rows]):.2f}% | {100*np.mean([r['pair_exact'] for r in rows]):.2f}% |")
    paragraphs += ["", "## Reproduction", "",
        "The machine metadata and dependency locks are under results/cloud/. The final checkpoint hashes, source paths, board counts and evaluation depths are embedded in GPU_RESULTS.json and each final run's config.yaml. Raw boards, predictions and checkpoint weights are preserved locally under results/. Recreate the reports without training with:", "",
        "```sh", ".venv/bin/python -m ncago.experiments.gpu_report",
        ".venv/bin/python -m ncago.experiments.rescue_report --final-runs "+" ".join(str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p) for p in args.final_runs)+
        ((" --paired-runs "+" ".join(str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p) for p in args.paired_runs)) if args.paired_runs else ""), "```", ""]
    output.with_suffix(".md").write_text("\n".join(paragraphs))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), layout="constrained")
    for result in results:
        rows = [r for r in result["measurements"] if r["primary"]]
        sizes = [r["size"] for r in rows]
        for ax, key in zip(axes[:2], ("stone_mean", "macro_mean")):
            ax.plot(sizes, [100*r[key] for r in rows], marker="o", label=result["label"])
        longer = [r for r in result["measurements"] if r["size"] == 9]
        axes[2].plot([r["depth"] for r in longer], [100*r["macro_mean"] for r in longer], marker="o", label=result["label"])
    for ax, title in zip(axes, ("Final all-stone accuracy", "Final class-balanced accuracy", "Longer rollout on final 9×9")):
        ax.set_title(title)
        ax.set_ylabel("Accuracy (%)")
        ax.set_ylim(0, 101)
        ax.grid(alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_xlabel("Board size")
    axes[1].set_xlabel("Board size")
    axes[2].set_xlabel("Rollout steps")
    axes[0].legend(fontsize=8)
    fig.savefig(output.with_suffix(".png"), dpi=180)
    plt.close(fig)
    propagation_picture = ""
    sealed = [s for s in pairs if s["evaluation_scope"] == "sealed paired-query family"]
    if sealed:
        from ncago.baselines.resnet import ResNet
        fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
        trajectories = defaultdict(list)
        for summary in sealed:
            for row in summary["records"]:
                if row["size"] == 37:
                    trajectories[row["source_run"]].append(row)
        for source, rows in trajectories.items():
            c = yaml.safe_load((ROOT / "results" / "learnability" / source / "config.yaml").read_text())
            label = ("Asynchronous" if "async" in c["variants"][0] else "Synchronous")+(" + hints" if c.get("hint_weight") else " without hints")
            depths = sorted({r["depth"] for r in rows})
            means = [100*np.mean([r["query_accuracy"] for r in rows if r["depth"] == d]) for d in depths]
            ax.plot(depths, means, marker="o", label=label)
        radius = ResNet(classes=4, blocks=16).receptive_field_radius
        distance = next(iter(trajectories.values()))[0]["causal_distance"]
        assert distance > radius
        ax.axhline(50, ls="--", color="#606873", label=f"16-block CNN upper bound (radius {radius})")
        ax.axvline(distance, ls=":", color="#606873", label=f"Changed input {distance} grid steps away")
        ax.set(xscale="log", ylim=(0, 101), xlabel="Recurrent steps · same weights", ylabel="Paired-query accuracy (%)",
               title="Sealed 37×37 witness: propagation works, convergence remains fragile")
        ax.set_xticks(depths, list(map(str, depths)))
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8)
        ax.grid(alpha=.2)
        destination = ROOT / "reports" / "GPU_PROPAGATION.png"
        fig.savefig(destination, dpi=180)
        plt.close(fig)
        import base64
        propagation_picture = '<h2>Sealed distant-query behavior</h2><img alt="37x37 query accuracy against recurrent steps" src="data:image/png;base64,'+base64.b64encode(destination.read_bytes()).decode()+'">'
    import base64
    picture = base64.b64encode(output.with_suffix(".png").read_bytes()).decode()
    demo = ROOT / "reports" / "figures" / "gpu_rollout.gif"
    illustration = ('<h2>Recorded dynamics on one held-out board</h2><p>This predetermined example illustrates learning and longer-rollout drift. Aggregate accuracy is reported above.</p><img alt="Exact counts, learned counts and hidden-state PCA" src="data:image/gif;base64,'+base64.b64encode(demo.read_bytes()).decode()+'">') if demo.exists() else ""
    output.with_suffix(".html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A100 final results</title><style>body{max-width:1200px;margin:40px auto;padding:0 24px;font:16px/1.65 system-ui;color:#172331;background:#fafbfc}h1,h2{line-height:1.25}h2{margin-top:40px}img{width:100%;background:white;border:1px solid #dce2e8;border-radius:8px}.table{overflow-x:auto}table{border-collapse:collapse;min-width:100%;font-size:14px;background:white}th,td{padding:10px;text-align:left;border-bottom:1px solid #dce2e8}th{background:#e9f0f6}pre{padding:18px;background:#e9f0f6;white-space:pre-wrap;overflow-wrap:anywhere}</style><img alt="Final accuracy and longer-rollout behavior" src="data:image/png;base64,'+picture+'">'+propagation_picture+render_markdown(paragraphs)+illustration+'</html>')
    print(output.with_suffix(".md"))


if __name__ == "__main__":
    main()
