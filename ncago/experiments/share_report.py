"""Build a self-contained public report and social assets from measured results."""
import base64
from collections import Counter
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import re
import shutil
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .common import ROOT, write_json
from .rescue_report import render_markdown

REPORTS = ROOT / "reports"
OUT = REPORTS / "shareable"


def esc(value):
    return html.escape(str(value), quote=True)


def data_url(path):
    kind = {".png": "image/png", ".gif": "image/gif"}[path.suffix]
    return f"data:{kind};base64,"+base64.b64encode(path.read_bytes()).decode()


def figure(path, caption, alt=None):
    return f'<figure><img loading="lazy" src="{data_url(path)}" alt="{esc(alt or caption)}"><figcaption>{caption}</figcaption></figure>'


def table(headers, rows):
    return '<div class="table"><table><thead><tr>'+''.join(
        f'<th>{esc(v)}</th>' for v in headers)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join(f'<td>{esc(v)}</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def public_data(value):
    """Retain evidence but replace machine-local paths with artifact identifiers."""
    if isinstance(value, dict):
        return {key: public_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [public_data(item) for item in value]
    if isinstance(value, str) and value.startswith(("/home/", "/Users/")):
        return value.split("/results/", 1)[-1] if "/results/" in value else Path(value).name
    if isinstance(value, str) and "/compute/v1/projects/" in value:
        return value.rsplit("/", 1)[-1]
    return value


def export_csv(path, rows):
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def social_card(final):
    async_result = next(f for f in final if f["label"] == "Asynchronous")
    primary = next(m for m in async_result["measurements"] if m["size"] == 9 and m["primary"])
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor="#f6f8fb")
    fig.text(.055, .93, "NCA GO  /  EXPLORATORY RESULTS", color="#346581", fontsize=15, weight="bold")
    fig.text(.055, .825, "Local updates learn Go liberties", color="#172c3e", fontsize=34, weight="bold")
    fig.text(.055, .755, "Strong 9×9 accuracy. A narrow propagation result. Generalization remains fragile.", fontsize=17, color="#4d6577")
    fig.text(.055, .56, f"{primary['stone_mean']*100:.2f}%", fontsize=66, weight="bold", color="#246e9d")
    fig.text(.057, .48, "9×9 liberty-class accuracy", fontsize=21, color="#172c3e")
    fig.text(.057, .425, "Three training seeds: 99.87 / 99.86 / 99.93%", fontsize=15, color="#4d6577")
    fig.text(.057, .375, "2,000 fresh positions · 32 update steps", fontsize=15, color="#4d6577")
    ax = fig.add_axes([.57, .29, .36, .35])
    values = [m for m in async_result["measurements"] if m["primary"]]
    ax.plot([m["size"] for m in values], [m["stone_mean"]*100 for m in values], marker="o", lw=3, color="#246e9d")
    ax.set(ylim=(50, 102), xlim=(8, 38), xticks=[9, 13, 19, 25, 37], ylabel="Stone accuracy (%)", xlabel="Board width")
    ax.set_title("Same weights, larger boards", fontsize=17, loc="left", color="#172c3e", pad=15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#f6f8fb")
    ax.grid(axis="y", alpha=.15)
    fig.text(.055, .20, "37×37 distant witness: 74.7% query accuracy", fontsize=22, weight="bold", color="#172c3e")
    fig.text(.055, .145, "Separate graph NCA + intermediate supervision; changed input 34 cells away; one training seed.", fontsize=15, color="#4d6577")
    fig.text(.055, .09, "Fixed 16-block CNN structural bound: 50%. Narrow paired geometry; no trained-CNN comparison.", fontsize=15, color="#4d6577")
    fig.text(.055, .03, "24 completed A100 training runs · procedural test sets · Go-playing strength unmeasured", fontsize=13, color="#4d6577")
    fig.savefig(OUT / "NCA_GO_TWITTER.png", facecolor=fig.get_facecolor())
    plt.close(fig)


def animation(path, title, caption, ident, historical=False):
    with Image.open(path) as im:
        poster = io.BytesIO()
        im.convert("RGB").save(poster, format="PNG", optimize=True)
    image = "data:image/png;base64,"+base64.b64encode(poster.getvalue()).decode()
    badge = "CPU SMOKE / HISTORICAL" if historical else "RECORDED MODEL / ILLUSTRATION"
    return f'''<details class="animation" id="{ident}"><summary><span>{esc(title)}</span><small>{badge}</small></summary>
<p>{caption}</p><button type="button" class="play" aria-pressed="false">Play animation</button>
<img loading="lazy" src="{image}" data-poster="{image}" data-gif="{data_url(path)}" alt="{esc(title)}">
</details>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    media = OUT / "media"
    media.mkdir(exist_ok=True)
    gpu = json.loads((REPORTS / "GPU_RESULTS.json").read_text())
    investigation = json.loads((REPORTS / "gpu_investigation.json").read_text())
    status = Counter(r["status"] for r in investigation["experiments"])
    assert status["measured"] == 24, status
    final = gpu["final_evaluations"]
    async_result = next(f for f in final if f["label"] == "Asynchronous")
    m9 = next(m for m in async_result["measurements"] if m["size"] == 9 and m["primary"])
    final_rows = []
    for family in final:
        for m in family["measurements"]:
            for s in m["per_seed"]:
                final_rows.append({"recipe": family["label"], "final_run": family["run"],
                    "board_size": m["size"], "depth": m["depth"], "primary": m["primary"],
                    **{k: v for k, v in s.items() if k != "per_class_accuracy"},
                    **{f"class_{label}_accuracy": value for label, value in zip(("1", "2", "3", "4plus"), s["per_class_accuracy"])}})
    export_csv(OUT / "data/final_accuracy.csv", final_rows)
    paired_rows = []
    for probe in gpu["paired_evaluations"]:
        for r in probe["records"]:
            paired_rows.append({"probe_created_utc": probe["created_utc"], **{
                k: v for k, v in r.items() if k not in ("model_config", "prediction_counts")},
                "chain_messages": r["model_config"].get("chain_messages", False),
                "algorithm_hints": r["model_config"].get("algorithm_hints", False)})
    export_csv(OUT / "data/paired_queries.csv", paired_rows)
    training_rows = []
    for r in investigation["experiments"]:
        training_rows.append({"run": r["run"], "recipe": r["label"].replace("|", "·"),
            "status": r["status"], "training_seed": r["seed"], "training_boards": r["config"]["train_count"],
            "planned_updates": r["config"]["training_steps"], "error": json.dumps(r.get("error")),
            "source_commit": r["source_commit"]})
    export_csv(OUT / "data/training_runs.csv", training_rows)
    write_json(OUT / "data/final_results.json", public_data(gpu))
    write_json(OUT / "data/gpu_training_results.json", public_data(investigation))
    write_json(OUT / "data/cpu_learnability.json", json.loads((REPORTS / "learnability_diagnostic.json").read_text()))
    # Archive all phase summaries, including not-run phases, without machine paths.
    phases = []
    for p in sorted((ROOT / "results").glob("*/**/summary.json")):
        if p.parent.parent.name in ("learnability", "final_liberties", "propagation_probe", "gpu_demo"):
            continue
        phases.append({"artifact": str(p.relative_to(ROOT)), "summary": public_data(json.loads(p.read_text()))})
    write_json(OUT / "data/historical_phase_results.json", phases)
    social_card(final)

    tweets = [
        "1/8 I trained a neural cellular automaton to classify Go liberties using local updates. Fresh 9×9 accuracy averaged 99.89% across 3 training seeds. Larger-board transfer is much rougher. Here are the successes, the animation, and the failures.",
        "2/8 A liberty is an empty point touching a connected group of stones. Counting a long group's distinct liberties needs information from far away. The model repeats one shared local rule; its output classes are 1, 2, 3, or 4+ liberties.",
        "3/8 On 2,000 fresh 9×9 positions, the three seeds scored 99.87%, 99.86%, and 99.93% per stone. Class-balanced mean: 99.88%. Entire boards correct: 98.57%. Checkpoints and the 32-step evaluation depth were frozen before opening the final sets.",
        "4/8 Two A100 40GB GPUs, 24 completed training runs. I tested losses, width, replay, gating, horizons, and intermediate supervision. Class balancing and a stronger training recipe rescued learnability. Several changes were combined, so causal claims stay limited.",
        "5/8 A separate graph NCA, trained on sizes 5–9 with intermediate counting labels, reached 74.7% query accuracy on a sealed 37×37 paired witness. Each pair differs at one input 34 cells away. Noise and firing were coupled within pairs.",
        "6/8 The supplied 16-block CNN sees only radius 33, so it cannot exceed 50% on those balanced pairs. This is a structural bound, not a trained-CNN win. The graph result uses one training seed and one underlying geometry with rotated/cluttered variants.",
        "7/8 The limits matter: broad 37×37 accuracy is only 65.4% for the main model. Running more steps can destroy correct answers. The animation deliberately continues past the trained horizon. Reliable size generalization and convergence remain open.",
        "8/8 Inspired by Reasoning with Neural Cellular Automata: https://arxiv.org/abs/2609.36126\nOur Go study leaves size generalization and convergence open. Next: broader geometries, more seeds and matched baselines. Go-playing strength is unmeasured."
    ]
    assert all(len(t) <= 270 for t in tweets), [len(t) for t in tweets]
    (OUT / "TWITTER_THREAD.txt").write_text("\n\n".join(tweets)+"\n")
    (OUT / "SINGLE_POST.txt").write_text(
        "Can local updates learn global Go structure? An NCA reached 99.89% liberty-class accuracy on fresh 9×9 boards across 3 seeds. Larger-board transfer is still fragile. Sharing the rollout, the successes, and the failures.\n")
    (OUT / "POSTING_NOTES.txt").write_text(
        "Suggested upload order\n\n"
        "1. Use TWITTER_THREAD.txt or SINGLE_POST.txt as editable drafts.\n"
        "2. Attach media/liberties_rollout.mp4 to the first post. It includes the failure after the trained horizon.\n"
        "3. Attach NCA_GO_TWITTER.png to the numbers post.\n"
        "4. Attach media/distant_pair_rollout.mp4 to the propagation post. Its first example misses one answer at step 64; this is deliberate.\n"
        "5. Share NCA_GO_REPORT.html through your own hosting or repository, then add that actual URL to the thread.\n\n"
        "Report and drafts are local; no public URL has been created and nothing has been posted.\n"
        "Defensible claim: high 9×9 procedural accuracy plus narrow learned propagation.\n"
        "Avoid claims of universal counting, stable convergence, beating CNNs generally, improved Go strength, or established novelty.\n"
        "All original CPU animations are included in the report, but their models failed the research accuracy criteria.\n")

    primary_rows = []
    for f in final:
        for m in f["measurements"]:
            if not m["primary"]:
                continue
            accuracy = (f"{100*m['stone_mean']:.3f} ± {100*m['stone_seed_std']:.3f}%"
                        if len(m["per_seed"]) > 1 else f"{100*m['stone_mean']:.3f}% (one seed)")
            lo, hi = m["stone_board_bootstrap_95"]
            primary_rows.append([f["label"], f"{m['size']}×{m['size']}", m["depth"],
                                 accuracy, f"{lo*100:.3f}–{hi*100:.3f}%",
                                 f"{100*m['macro_mean']:.2f}%", f"{100*m['board_exact_mean']:.2f}%"])
    all_depth_rows = []
    for f in final:
        for m in f["measurements"]:
            all_depth_rows.append([f["label"], m["size"], m["depth"], "primary" if m["primary"] else "diagnostic",
                                   f"{100*m['stone_mean']:.3f}%", f"{100*m['macro_mean']:.3f}%", f"{100*m['board_exact_mean']:.2f}%"])

    sections = []
    sections.append('''<section id="assessment"><div class="eyebrow">01 / Honest assessment</div><h2>A good exploratory result, with a clear ceiling</h2>
<p>The strongest achievement is repeatable liberty classification on independently generated 9×9 positions. The second is a controlled demonstration that a learned local system responds to a change outside a specified fixed CNN's receptive field. These are useful results to share. They establish progress on this experiment.</p>
<p>The evidence does not yet support an exact size-general counting algorithm, a practical advantage over an exact Go rules engine, or improved Go play. Synchronous training performs almost as well as asynchronous training. The propagation result uses an explicit connectivity prior, intermediate supervision, one training seed and one underlying query geometry. Its accuracy also falls at longer horizons.</p>
<div class="callout"><strong>Recommended public claim:</strong> “A learned local rule achieves high 9×9 liberty-class accuracy and, with graph routing and intermediate supervision, shows limited long-distance propagation. Size generalization and stable convergence remain unresolved.”</div>
<p>A strong research claim would require additional geometries, replicated graph experiments, stronger matched learned baselines and a stable stopping criterion. Novelty has not been established through an exhaustive literature comparison. A classical flood-fill method already computes exact liberties; this project investigates what a learned local system can acquire.</p></section>''')
    sections.append('''<section id="task"><div class="eyebrow">02 / The question</div><h2>Can local updates count a connected group's liberties?</h2>
<p>In Go, a liberty is a distinct empty intersection adjacent to a connected group of same-color stones. All stones in that group share its liberty count. The task labels each stone as 1, 2, 3 or 4+ liberties; empty and off-board cells are excluded. “99.89% accuracy” refers to these capped classes, rather than an uncapped integer count.</p>
<p>The grid NCA repeats the same learned 3×3 update rule at each location. Each step expands the possible range of influence. The main model uses 64 state channels and stochastic firing with probability 0.8. Its static board channels remain frozen, and all cells share weights. At inference, the network receives board tokens and its own recurrent state.</p>
<p>The separate graph variant routes mutable messages only through orthogonally adjacent stones of the same color. Static input perception remains local. An auxiliary head receives training targets for intermediate discovered-liberty counts from an exact local reference algorithm. Reference IDs and teacher hidden states are never supplied as neural inference inputs. The graph routing is an explicit Go prior.</p></section>''')
    sections.append('''<section id="accuracy"><div class="eyebrow">03 / Independent final tests</div><h2>99.89% mean 9×9 accuracy across three training seeds</h2>
<p>The asynchronous model's per-seed results are 99.8705%, 99.8588% and 99.9294%. Every recorded seed passes the numeric 99.5% G1 accuracy threshold at the predeclared 32-step depth. Class-balanced accuracy is 99.882%; entire-board exactness is 98.567%. Passing this numerical threshold does not establish all of the original specification's broader hypotheses.</p>
<p>The 9×9 final set contains 1,000 random legal playout positions and 1,000 controlled positions. Larger sets contain two generators at 256, 128, 64 and 32 boards each for widths 13, 19, 25 and 37. They are procedural datasets, not professional game records. Previously opened datasets are excluded up to rotation, reflection and color swap.</p>
<p>Training seeds change model initialization, optimization and stochastic execution; the recorded repeats share the same training dataset and final test boards. Each asynchronous model has three firing trials, averaged without selecting the best trial. Checkpoint hashes, training budgets and primary inference depth were frozen before opening final boards. Larger-board scores were not used for subsequent retuning.</p>'''+
        table(["Recipe", "Board", "Steps", "Stone mean ± seed SD", "Board bootstrap 95%", "Class-balanced mean", "Entire board correct"], primary_rows)+
        '''<p class="note">Bootstrap intervals resample boards within each generator and preserve their pairing across seeds. They are conditional on the recorded trained models and firing trials. The standard deviation across three training seeds is reported separately in percentage points. “Entire board correct” and per-stone accuracy measure different things.</p>'''+
        figure(REPORTS / "GPU_RESULTS.png", "Final accuracy by board size and longer-rollout behavior. All four measured final recipes are included.")+'''</section>''')

    sections.append('''<section id="rollout"><div class="eyebrow">04 / Recorded behavior</div><h2>Watch the model succeed, then drift</h2>
<p>This is validation-board index zero from the successful asynchronous recipe. It was chosen by index, rather than by its outcome. At step 32 every stone in this example is correct. By steps 64 and 128 accuracy falls to 92.9% and 80.0%. The independent final aggregate, rather than this single example, supports the accuracy claim.</p>
<p>Red numbers mark errors. The hidden-state colors use a shared PCA projection across the trajectory; they are a visualization of representations, not a decoded algorithm. Animation time is slowed for inspection and does not represent inference speed.</p>'''+
        animation(REPORTS / "figures/gpu_rollout.gif", "Successful grid NCA: 9×9 held-out rollout", "Exact labels, learned labels and hidden PCA through steps 1–128. The model was trained at 32 steps.", "main-animation")+
        figure(REPORTS / "figures/gpu_rollout.png", "The same predetermined example, including steps past the trained horizon.")+'''</section>''')

    sections.append('''<section id="propagation"><div class="eyebrow">05 / Distant-information witness</div><h2>74.74% on a controlled 37×37 query family</h2>
<p>A separate asynchronous graph model with intermediate hints reaches 74.7396% query accuracy at the frozen depth of 64. It was trained on sizes 5–9. The test contains 64 one-versus-two-liberty pairs and three firing trials. Both answers in a pair are correct in 52.60% of pair-trials; this is distinct from 74.74% individual-query accuracy.</p>
<p>Each pair differs at exactly one input 34 grid steps from the query. Initial state randomness and firing are identical within the pair. This prevents stochastic differences from masquerading as a distant signal. The supplied 16-block ResNet has receptive-field radius 33: because it must produce the same query output for both balanced labels, its accuracy cannot exceed 50% on these pairs, regardless of its weights. This is a mathematical architecture bound, not an empirical win over a newly trained CNN.</p>
<p>At 32 steps all three graph recipes score exactly 50% on the 37×37 pairs. At 64 steps, asynchronous hints score 74.74%, synchronous hints 64.06%, and asynchronous without hints 42.97%. At 128 steps, the asynchronous hinted model falls to 47.14%. Longer execution does not establish convergence.</p>
<div class="callout warning"><strong>Scope:</strong> Each board size has one underlying witness geometry, varied through symmetry, color swap and clutter. These variants are not many independent chain geometries. Each graph recipe has only one trained seed. Generalization to arbitrary larger chains remains unproven.</div>'''+
        figure(REPORTS / "GPU_PROPAGATION.png", "All three graph recipes and all recorded depths on the sealed 37×37 witness. The 50% line is the fixed CNN's structural upper bound.")+
        animation(media / "distant_pair_rollout.gif", "First sealed pair: where the distant input affects state", "The first pair, trial zero, was replayed with the frozen checkpoint and the evaluator's coupled keys. State differences exclude frozen input channels. The saved 64-step query predictions match the evaluation exactly: 2 and 2, while the true answers are 1 and 2. This example makes a remaining failure visible. Hidden-state differences establish influence, rather than exact algorithm recovery.", "distant-animation")+'''</section>''')

    sections.append('''<section id="reasoning"><div class="eyebrow">06 / Why the training changed</div><h2>Learnability and generalization required different interventions</h2>
<p>The CPU smoke pipeline produced 65.93% 9×9 liberty accuracy and predominantly predicted the common class. Low-budget diagnostics could fit small training data but had roughly 30–39% class-balanced validation accuracy. That pointed to learning and data problems before any stronger algorithmic claim could be tested.</p>
<p>Matched 6,000-update target-chain experiments improved 9×9 class-balanced validation accuracy from 72.06% with 32 channels to 99.03% with 64. Late cross-entropy scored 99.03%, compared with 95.37% for late MSE. The basic high-accuracy recurrent model degraded to 29.04% when run for four times its trained depth. Fitting the training horizon did not produce a stable counting procedure.</p>
<p>Replay improved longer-horizon behavior in some runs but reduced trained-depth accuracy at the short budget. An optional normalization experiment failed numerically; replacing unit-sphere division with unit-ball projection fixed the zero-state gradient singularity, without making it the best learning recipe. Gated updates bounded the mutable state. Bounded state alone does not guarantee a stable correct answer.</p>
<p>The successful whole-board recipe combined 8,192 training boards, 30,000 updates, class-balanced loss, late cross-entropy over the last eight of 32 rollout steps, augmentation, cosine learning-rate decay, EMA weight averaging and 64-channel gated cells. Its initial learning rate was 0.0005 and EMA decay 0.99. Several factors changed together, so the full improvement cannot be attributed to one isolated intervention.</p>
<p>A multiscale target-chain model achieved 95.48% on 13×13 validation but failed the distant-information query. That exposed a shortcut hidden by aggregate accuracy. The graph experiment then added same-chain routing, more diverse shapes, component-neighborhood deduplication and intermediate algorithm supervision before opening the larger sealed query tests. Training labels guide intermediate computation; they do not replace neural inference with the exact reference.</p>
<p>The synchronous whole-board repeats average 99.84% on 9×9, close to the asynchronous 99.89%. The evidence supports reliable learned classification for both recipes; it does not establish that asynchronous firing is necessary. Wider 128-channel synchronous cells reached 99.957% in one final seed, so that number is not treated as a three-seed replication.</p></section>''')

    gpu_md = (REPORTS / "gpu_investigation.md").read_text().splitlines()
    sections.append('''<section id="experiments"><div class="eyebrow">07 / Every GPU attempt</div><h2>24 completed runs, one numerical failure, two interruptions</h2>
<p>The following scores are training/validation diagnostics. Target-chain experiments supervise one constructed chain per board; whole-board experiments supervise every stone. These rows are not interchangeable with sealed final accuracy. Every score below is class-balanced; a constant class predictor scores 25% on this metric.</p>
<p>Some jobs shared a GPU or were paused. Logged wall time is not an isolated throughput benchmark. Interrupted jobs are retained without being presented as completed experiments.</p>'''+
        render_markdown(gpu_md[gpu_md.index(next(x for x in gpu_md if x.startswith("| Experiment"))):])+
        figure(REPORTS / "gpu_investigation.png", "All completed GPU validation experiments, at the training depth and longer depths. Failed and interrupted jobs remain in the table and downloadable data.")+'''</section>''')

    gpu_md_final = (REPORTS / "GPU_RESULTS.md").read_text().splitlines()
    pstart = next(i for i, line in enumerate(gpu_md_final) if line.startswith("| Model | Board"))
    pend = next((i for i in range(pstart, len(gpu_md_final)) if gpu_md_final[i].startswith("## Reproduction")), len(gpu_md_final))
    sections.append('''<section id="appendix"><div class="eyebrow">08 / Complete final measurements</div><h2>Every recorded board size and rollout depth</h2>
<p>Primary settings were frozen in advance. Other depths describe behavior; their strongest observed value does not replace the primary result. Per-seed and per-class measurements are downloadable as CSV and JSON below.</p><details><summary>Expand all 80 final accuracy settings</summary>'''+
        table(["Recipe", "Board width", "Steps", "Setting", "Stone mean", "Class-balanced mean", "Entire board correct"], all_depth_rows)+
        '''</details><details><summary>Expand every recorded paired-query setting</summary>'''+render_markdown(gpu_md_final[pstart:pend])+'''</details></section>''')

    cpu_md = (REPORTS / "SUMMARY.md").read_text().splitlines()
    sections.append('''<section id="history"><div class="eyebrow">09 / Original CPU smoke study</div><h2>The earlier broader Go tasks remain unsuccessful</h2>
<p>These results come from a reduced CPU smoke run with one training seed and a different training protocol. They are retained as historical evidence and are not comparisons against the newer GPU models. The original broader NCA advantage criteria were not met. High atari or aggregate ladder accuracy can reflect class imbalance; typed ladder accuracies expose failure.</p>'''+render_markdown(cpu_md[2:])+
        figure(REPORTS / "learnability_diagnostic.png", "Pre-GPU learnability diagnostics: fitting small training data did not establish validation accuracy or rollout stability.")+'''</section>''')
    smoke_figures = [
        ("F1a", "Original capability map"), ("F1b", "Original accuracy gaps by information distance"),
        ("F2", "Original board-size scaling"), ("F3", "Original light-cone diagnostics"),
        ("F3b", "Original solver-time diagnostic"), ("F3c", "Original convergence diagnostic"),
        ("F5a", "Original firing maps"), ("F5b", "Original adaptive update comparison"),
        ("F5c", "Original damage response"), ("F6", "Original ablations"),
        ("F7", "Original test-time scaling"), ("F8a", "Original ring-versus-path comparison"),
        ("F10", "Original compute measurements")]
    sections.append('<section id="smoke-charts"><div class="eyebrow">10 / Historical figures</div><h2>All original smoke charts</h2><p>These plots describe the failed or limited smoke models. Their apparent patterns do not establish algorithmic success. See the original task table and raw phase records for scope.</p>'+''.join(
        '<details><summary>'+esc(caption)+'</summary>'+figure(REPORTS / f"figures/{name}.png", f"{name}: {caption}. CPU smoke profile; one training seed.")+ '</details>'
        for name, caption in smoke_figures if (REPORTS / f"figures/{name}.png").exists())+'</section>')

    animations = []
    for p in sorted((REPORTS / "figures").glob("F4_*.gif"), key=lambda p: int(p.stem.split("_")[1])):
        source = json.loads(p.with_suffix(".source.json").read_text())["source"]
        relative = source.split("/results/", 1)[1]
        phase = relative.split("/")[0]
        task = {"1": "Liberties", "2": "Benson life", "3": "Ladder labels", "4a": "Ring/path liberties"}.get(phase, f"Phase {phase}")
        name = Path(source).stem.removeprefix("nca_").replace("_", " ")
        title = f"{p.stem}: {task} · {name}"
        caption = f"Historical CPU smoke model. Panels show the board, decoded class and confidence. This animation is not evidence of successful counting, life detection or ladder reading. Source: <code>results/{esc(relative)}</code>."
        animations.append(animation(p, title, caption, p.stem, True))
    sections.append('''<section id="gallery"><div class="eyebrow">11 / Complete animation archive</div><h2>All 22 original CPU animations</h2>
<p>The two newer recorded animations appear above. Every older saved GIF is included here, with its task and source. Each opens paused; use Play to inspect it. Confidence is a model output, not a guarantee of correctness.</p>'''+''.join(animations)+'''</section>''')

    sections.append('''<section id="limits"><div class="eyebrow">12 / What remains open</div><h2>The result is bounded by the tests we ran</h2>
<ul><li><strong>Large-board classification:</strong> the main asynchronous model reaches 78.14% at width 13 and 65.42% at width 37, at its frozen depth of 32.</li>
<li><strong>Temporal stability:</strong> 9×9 class-balanced accuracy falls from 99.88% at 32 steps to 98.41%, 90.88% and 81.55% at 64, 128 and 256. More compute can harm predictions.</li>
<li><strong>Propagation scope:</strong> one geometry per size, one training seed per graph recipe, three firing trials for stochastic models. The result motivates broader tests; it does not replace them.</li>
<li><strong>Baselines:</strong> the narrow CNN bound follows from receptive-field size. A strong CNN with a larger receptive field, a recurrent CNN and graph algorithms can also access the decisive information. The final GPU study does not establish a practical advantage over these alternatives.</li>
<li><strong>Other Go tasks:</strong> life, ladder reading, ownership distillation, policy learning, adversarial cyclic positions and playing strength were not rescued by these liberty experiments. Their earlier results or missing measurements remain above.</li>
<li><strong>Protocol changes:</strong> the rescue uses gated cells, cross-entropy, different widths and budgets, final EMA checkpoints and a 32-step main horizon. The graph variant adds an explicit connectivity prior and intermediate supervision. This is an investigation beyond the original smoke recipe, rather than a complete execution of every original research requirement.</li></ul>
<p>The next discriminating experiments are replication of graph propagation with fresh training seeds and substantially different chain geometries, stable training through longer horizons, distribution-matched learned baselines, and evaluation on realistic game positions. Those experiments have not been run.</p></section>''')

    links = ["data/final_accuracy.csv", "data/paired_queries.csv", "data/training_runs.csv",
             "data/final_results.json", "data/gpu_training_results.json", "data/historical_phase_results.json",
             "TWITTER_THREAD.txt", "SINGLE_POST.txt", "POSTING_NOTES.txt", "NCA_GO_TWITTER.png",
             "media/liberties_rollout.mp4", "media/distant_pair_rollout.mp4"]
    sections.append('''<section id="downloads"><div class="eyebrow">13 / Evidence and sharing</div><h2>Download the data, report and upload assets</h2>
<p>This HTML file embeds all charts and 24 animations and works offline. CSV, JSON and MP4 files are supplied alongside it in the ZIP bundle. The primary data, model weights and full source snapshots remain preserved in the local experiment workspace. The public bundle includes measured summary data; it does not bundle the large checkpoints and training datasets.</p>
<p>Two NVIDIA A100-SXM4-40GB workers ran the investigation. The code suite passed 42 tests, including rule/label checks, finite gradients, local routing and coupled-query behavior. The rules engine matched an independent implementation over 4,056,472 moves in 10,000 random games. These are implementation checks; they do not certify learned-model generalization. Both GPU workers and their task disks were deleted after verified local archiving.</p><div class="downloads">'''+''.join(
        f'<a download href="{esc(path)}">{esc(Path(path).name)}</a>' for path in links)+'''</div>
<h3>Rebuild from saved evidence</h3><pre>.venv/bin/python -m ncago.experiments.share_report</pre>
<p>The CSV tables and all aggregate plots rebuild without training. To regenerate the two upload videos from the recorded rollout and frozen graph checkpoint, run:</p><pre>.venv/bin/python -m ncago.experiments.share_media</pre>
<p>The artifact manifest records hashes and sources. Machine-local account paths are replaced by artifact identifiers in the public metadata. Nothing has been posted or hosted by this report-generation step.</p></section>''')

    sections.append('''<section id="context"><div class="eyebrow">14 / Research context</div><h2>Local learning has an established research history</h2>
<p>The project was inspired by <a href="https://arxiv.org/abs/2609.36126">Reasoning with Neural Cellular Automata</a> (Etcheverry et al., 2026), which studies strictly local asynchronous recurrent cells on visual reasoning tasks including mazes, Sudoku and ARC-AGI-1. This Go study adapts that research direction. Its rescue experiments change the training recipe and, for the graph variant, the routing and supervision; the original paper's benchmark results are not results of this project.</p>
<p><a href="https://distill.pub/2020/growing-ca/">Growing Neural Cellular Automata</a> (Mordvintsev et al., 2020) studies learned local update rules, asynchronous updates and persistent states. It also illustrates instability beyond the training horizon. Our counting study shares that local-learning perspective; its task and measurements differ.</p>
<p><a href="https://proceedings.mlr.press/v162/velickovic22a.html">The CLRS Algorithmic Reasoning Benchmark</a> (Veličković et al., 2022) supplies broader context for learning algorithmic behavior and evaluating generalization. We did not evaluate this model on CLRS, and these sources do not establish novelty or superiority for the present experiment.</p>
<p>Assessment: suitable for an honest public experiment log and a focused discussion of failure modes. Additional comparisons and replication are needed for a strong general algorithmic-reasoning claim.</p></section>''')

    css = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f6f8fb;color:#172c3e;font:17px/1.65 system-ui,-apple-system,sans-serif}main{max-width:1160px;margin:auto;padding:38px 28px 80px}header{padding:46px 0 26px;border-bottom:1px solid #d7e0e8}h1{font-size:clamp(36px,6vw,64px);line-height:1.07;letter-spacing:-2px;margin:20px 0}h2{font-size:30px;line-height:1.2;letter-spacing:-.6px;margin:12px 0 22px}h3{font-size:21px}.eyebrow{font-size:12px;letter-spacing:1.7px;font-weight:750;text-transform:uppercase;color:#346581}.lede{max-width:900px;font-size:23px;color:#4d6577}.badge{display:inline-block;padding:5px 11px;background:#e7eef5;border-radius:4px;font-size:12px;font-weight:700;letter-spacing:.5px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:34px 0}.stat{background:white;border:1px solid #d7e0e8;border-radius:8px;padding:24px}.stat strong{font-size:40px;line-height:1.3;display:block;color:#246e9d}.stat span{font-size:14px;color:#4d6577}.scope{font-size:15px;color:#4d6577}nav{display:flex;flex-wrap:wrap;gap:9px;margin:26px 0}a{color:#246e9d;text-underline-offset:3px}nav a{font-size:13px;background:#e7eef5;padding:7px 10px;border-radius:4px;text-decoration:none}section{padding:38px 0;border-bottom:1px solid #d7e0e8}p{max-width:1020px}.callout{border-left:4px solid #246e9d;background:#eaf2f8;padding:18px 22px;margin:26px 0}.warning{border-color:#b87b31;background:#fcf3e7}.table{overflow-x:auto;border:1px solid #d7e0e8;border-radius:6px;margin:20px 0}table{width:100%;border-collapse:collapse;font-size:13px;background:white}th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #e3eaf0;vertical-align:top}th{background:#e8eff6;font-weight:700;white-space:nowrap}tr:last-child td{border-bottom:0}figure{margin:26px 0}img{max-width:100%;height:auto;display:block;background:white;border:1px solid #d7e0e8;border-radius:6px}figcaption,.note{font-size:14px;color:#4d6577;margin-top:10px}details{background:white;border:1px solid #d7e0e8;padding:18px 22px;border-radius:6px;margin:14px 0}summary{cursor:pointer;font-weight:650}summary small{display:block;color:#7b5d32;font-size:10px;letter-spacing:1px;padding-top:4px}.animation img{margin:18px 0 4px;width:100%}button{background:#246e9d;color:white;border:0;padding:10px 16px;border-radius:4px;font:600 14px system-ui;cursor:pointer}button:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #f2a441;outline-offset:3px}.downloads{display:flex;flex-wrap:wrap;gap:12px}.downloads a{font-size:13px;padding:10px 14px;border:1px solid #d7e0e8;border-radius:4px;background:white}code,pre{font-size:12px;overflow-wrap:anywhere}pre{background:#e7eef5;padding:18px;border-radius:5px;white-space:pre-wrap}li{margin:12px 0}footer{font-size:13px;color:#4d6577;margin-top:35px}@media(max-width:650px){main{padding:24px 16px}.stats{grid-template-columns:1fr;gap:10px}.stat{padding:15px}.stat strong{font-size:32px}.lede{font-size:19px}h2{font-size:25px}details{padding:15px}.eyebrow{font-size:10px}}@media print{nav,button,.downloads{display:none}section{break-inside:auto}details{display:block}.stats{grid-template-columns:repeat(3,1fr)}body{background:white}}'''
    javascript = '''document.querySelectorAll('.animation').forEach(d=>{const i=d.querySelector('img'),b=d.querySelector('button');function stop(){i.src=i.dataset.poster;b.textContent='Play animation';b.setAttribute('aria-pressed','false')}b.addEventListener('click',()=>{if(b.getAttribute('aria-pressed')==='true')stop();else{i.src=i.dataset.gif;b.textContent='Pause animation';b.setAttribute('aria-pressed','true')}});d.addEventListener('toggle',()=>{if(!d.open)stop()})});'''
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Measured NCA Go results: reproducible 9×9 liberty accuracy, limited long-distance propagation, all experiments and animations."><title>NCA Go: local rules, global counting</title><style>'''+css+'''</style></head><body><main><header><div class="eyebrow">NCA GO / EXPERIMENT REPORT / 6 OCTOBER 2026</div><h1>Local rules,<br>global counting</h1><p class="lede">A neural cellular automaton learns Go liberty classes. The evidence is strong on 9×9 boards and narrower for long-distance propagation. Stable size generalization remains open.</p><span class="badge">EXPLORATORY RESEARCH · MEASURED RESULTS</span><div class="stats"><div class="stat"><strong>99.89%</strong><span>9×9 stone accuracy<br>Three training seeds, fresh final boards</span></div><div class="stat"><strong>74.74%</strong><span>Distant 37×37 query accuracy<br>Separate graph model, one trained seed</span></div><div class="stat"><strong>24 runs</strong><span>Completed GPU training attempts<br>Two A100 40GB workers</span></div></div><p class="scope">Liberty classes: 1 / 2 / 3 / 4+. Main model: 32 update steps. Large-board accuracy and longer-rollout stability remain limited. Go-playing strength is unmeasured.</p></header><nav>'''+''.join(f'<a href="#{ident}">{label}</a>' for ident, label in [
        ("assessment", "Assessment"), ("accuracy", "Final accuracy"), ("rollout", "Rollout"),
        ("propagation", "Propagation"), ("experiments", "All GPU runs"), ("appendix", "All final settings"),
        ("history", "CPU results"), ("gallery", "All animations"), ("downloads", "Downloads")])+'''</nav>'''+''.join(sections)+'''<footer>Every numerical result derives from recorded runs. Animations illustrate individual examples; aggregate tables support the claims. Public report generated from the NCA_GO experiment archive.</footer></main><script>'''+javascript+'''</script></body></html>'''
    (OUT / "NCA_GO_REPORT.html").write_text(document)
    # Preserve the original GIFs as directly usable files in the portable bundle.
    for p in (REPORTS / "figures").glob("*.gif"):
        shutil.copy2(p, media / p.name)
    assets = [p for p in sorted(OUT.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "NCA_GO_SHARE_PACKAGE.zip")]
    write_json(OUT / "manifest.json", {"report": "NCA_GO_REPORT.html", "date": "2026-10-06",
        "generator_sources": [{"path": f"ncago/experiments/{name}",
                               "sha256": hashlib.sha256((ROOT / "ncago/experiments" / name).read_bytes()).hexdigest()}
                              for name in ("share_report.py", "share_media.py")],
        "animation_count": len(list(media.glob("*.gif"))), "completed_gpu_training_runs": status["measured"],
        "failed_gpu_training_runs": status["failed"], "interrupted_gpu_training_runs": status["interrupted"],
        "tweet_lengths": [len(t) for t in tweets], "model_data_scope": "Public measured summaries; weights and full datasets preserved separately in local results/",
        "assets": [{"path": str(p.relative_to(OUT)), "bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in assets]})
    with zipfile.ZipFile(OUT / "NCA_GO_SHARE_PACKAGE.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for p in assets+[OUT / "manifest.json"]:
            archive.write(p, p.relative_to(OUT))
    print(json.dumps({"report": str(OUT / "NCA_GO_REPORT.html"), "animations": len(list(media.glob("*.gif"))),
                      "final_settings": len(all_depth_rows), "final_csv_rows": len(final_rows),
                      "paired_csv_rows": len(paired_rows), "gpu_attempts": dict(status),
                      "report_MiB": (OUT / "NCA_GO_REPORT.html").stat().st_size/2**20,
                      "bundle_MiB": (OUT / "NCA_GO_SHARE_PACKAGE.zip").stat().st_size/2**20}, indent=2))


if __name__ == "__main__":
    main()
