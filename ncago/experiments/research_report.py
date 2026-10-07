"""Publish measured follow-up research without promoting unfinished jobs."""
import csv
import json
from pathlib import Path
import numpy as np
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .common import ROOT, write_json
from .research_train import stability_assessment, class_names


RECIPE_FIELDS = ("training_steps", "schedule_steps", "batch_size", "min_depth", "max_depth",
                 "gradient_window", "late_steps", "change_weight", "warmup_steps", "seed_fraction",
                 "noise_sigma", "damage", "target_swap", "normalization_groups",
                 "identifier_input_scale", "identifier_zero_init", "identifier_replay_policy", "oracle_stream_delivery")
DATA_FIELDS = ("task", "cap", "data_seed", "validation_seed", "validation_count", "training_steps",
               "batch_size", "warmup_steps", "seed_fraction", "damage", "target_swap")


def signature(config, fields):
    from hashlib import sha256
    return sha256(json.dumps({k: config.get(k) for k in fields}, sort_keys=True).encode()).hexdigest()[:10]


def validation_id_disagreement(path, config):
    if not config['identifier_channels']:
        return None
    from .research_train import validation_data
    mask = validation_data(config)[9][1] >= 0
    paths = sorted((path / 'eval').glob('validation_9_draw*.npz'))
    predictions = []
    for file in paths:
        with np.load(file) as data:
            predictions.append(data['predictions'][2][mask])  # D128 in the recorded qualification order.
    if len(predictions) < 2:
        return None
    return float(np.mean([np.mean(row != predictions[0]) for row in predictions[1:]]))


def matching_audit(training):
    """Verify actual supervised batches, rather than relying on data seeds."""
    groups = {}
    for row in training:
        if not row["gpu"] or row["warmstart"] or row["summary"]["status"] != "complete":
            continue
        key = signature(row["config"], DATA_FIELDS)
        groups.setdefault(key, []).append(row)
    output = []
    for key, rows in groups.items():
        candidates = {r["summary"].get("stream_sha256") for r in rows}
        supervised = {r["supervised_stream_sha256"] for r in rows}
        output.append(dict(data_group=key, runs=[r["run"] for r in rows],
                           candidate_digests_identical=len(candidates) == 1 and None not in candidates,
                           supervised_digests_identical=len(supervised) == 1 and None not in supervised,
                           fully_verified=len(rows) >= 2 and len(candidates) == len(supervised) == 1
                           and None not in candidates and None not in supervised))
    return output


def confusion_archive(evaluations, out):
    """Print matrices without treating repeated IDs as independent samples."""
    lines = ["# Final-test and witness confusion matrices", "",
             "Rows are true classes; columns are predictions. Matrices below sum the recorded nuisance draws, so their entries are prediction trials rather than independent boards. Overcounts occupy the upper triangle; undercounts the lower triangle. Race outcomes are nominal and have no over/under ordering.", ""]
    archive = []
    for run in evaluations:
        for kind, records in [('final_boards', run['records']), ('paired_queries', run['paired'])]:
            groups = {}
            for row in records:
                key = (row.get('kind', kind), row['size'], row.get('ratio'), row.get('depth'), row.get('geometry', 'all'))
                groups.setdefault(key, []).append(row)
            for key, rows in sorted(groups.items(), key=lambda item: str(item[0])):
                matrix = np.sum([row['confusion'] for row in rows], axis=0)
                ordinal = run.get('task', 'liberties') != 'race'
                over = int(np.triu(matrix, 1).sum()) if ordinal else None
                under = int(np.tril(matrix, -1).sum()) if ordinal else None
                name, size, ratio, depth, geometry = key
                label = f"{run['source_run']} / {name} / {size}×{size} / " + (f'D/diameter={ratio}' if ratio is not None else f'D={depth}') + f' / {geometry}'
                lines += [f"## {label}", "", f"Draws: {len(rows)}. Overcounts: {over}; undercounts: {under}.", "", "```text", np.array2string(matrix, max_line_width=180), "```", ""]
                if ordinal:
                    for title, triangle in [('Overcounts only', np.triu(matrix, 1)), ('Undercounts only', np.tril(matrix, -1))]:
                        lines += [title, '', '```text', np.array2string(triangle, max_line_width=180), '```', '']
                archive.append(dict(source_run=run['source_run'], task=run.get('task', 'liberties'), kind=name, size=size,
                                    ratio=ratio, depth=depth, geometry=geometry, draws=len(rows), confusion=matrix.tolist(),
                                    overcounts=over, undercounts=under))
    (out / 'CONFUSIONS.md').write_text('\n'.join(lines)+'\n')
    write_json(out / 'confusions.json', archive)


def learning_curves(training, out):
    curves = []
    for run in training:
        if not run['gpu']:
            continue
        path = ROOT / 'results/research_training' / run['run'] / 'metrics.jsonl'
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows = [row for row in rows if row.get('event') == 'validation' and 'depths' in row]
        c = run['config']
        for row in rows:
            for depth, measured in zip(row['depths'], row['metrics']):
                curves.append(dict(run=run['run'], task=c['task'], cap=c['cap'], model=c['model'],
                                   recipe=run['recipe'], identifiers=c['identifier_channels'], seed=c['seed'],
                                   warmstart=run['warmstart'], iteration=row['iteration'], depth=depth,
                                   stone_accuracy=measured['stone_accuracy'], macro_accuracy=measured['macro_accuracy']))
    write_json(out / 'learning_curves.json', curves)
    figures = []
    for task, cap in sorted({(r['task'], r['cap']) for r in curves}):
        selected = [r for r in curves if r['task'] == task and r['cap'] == cap]
        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), layout='constrained')
        series = sorted({(r['model'], r['recipe'], r['identifiers'], r['warmstart']) for r in selected})
        for model, recipe, ids, warm in series:
            rows = [r for r in selected if (r['model'], r['recipe'], r['identifiers'], r['warmstart']) == (model, recipe, ids, warm)]
            for ax, depth in zip(axes, (128, 1024)):
                relevant = [r for r in rows if r['depth'] == depth]
                iterations = sorted({r['iteration'] for r in relevant})
                if not iterations:
                    continue
                values = [[100*r['stone_accuracy'] for r in relevant if r['iteration'] == update] for update in iterations]
                ax.plot(iterations, [np.mean(v) for v in values], label=f'{model}, {recipe}, IDs{ids}'+(' warmstart' if warm else ''))
                ax.fill_between(iterations, [min(v) for v in values], [max(v) for v in values], alpha=.12)
        for ax, depth in zip(axes, (128, 1024)):
            ax.set(title=f'{task}, cap{cap}: D{depth}', xlabel='Optimizer updates', ylabel='Stone accuracy (%)', ylim=(0, 102))
            ax.spines[['top', 'right']].set_visible(False)
        axes[-1].legend(fontsize=7)
        fig.suptitle('Fixed first 128 validation boards; full frozen-validation qualification is separate', fontsize=10)
        name = f'learning_curves_{task}_cap{cap}.png'
        fig.savefig(out / name, dpi=170); plt.close(fig); figures.append(name)
    return figures


def rollout_dynamics(training, out):
    figures, records, summaries = [], [], []
    groups = {}
    for run in training:
        if not run['gpu'] or run['summary']['status'] != 'complete' or run['config']['model'] == 'resnet':
            continue
        paths = sorted((ROOT / 'results/research_training' / run['run'] / 'eval').glob('validation_9_draw*.npz'))
        if not paths:
            continue
        traces = []
        for path in paths:
            with np.load(path) as data:
                traces.append(data['dynamics'])
        trace = np.mean(traces, axis=0)
        c = run['config']
        summaries.append(dict(run=run['run'], draws=len(traces),
                              mean_state_change_129_1024=float(trace[128:, 0].mean()),
                              mean_flip_rate_129_1024=float(trace[128:, 1].mean()),
                              state_change_step1024=float(trace[-1, 0]), flip_rate_step1024=float(trace[-1, 1])))
        groups.setdefault((c['task'], c['cap']), []).append((run, trace))
        for index, values in enumerate(trace):
            records.append(dict(run=run['run'], model=c['model'], task=c['task'], cap=c['cap'],
                                seed=c['seed'], step=index+1, state_change=float(values[0]), prediction_flip_rate=float(values[1])))
    if records:
        write_json(out / 'stability_dynamics_summary.json', summaries)
        with (out / 'rollout_dynamics.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
    for (task, cap), runs in groups.items():
        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), layout='constrained')
        series = {}
        for run, values in runs:
            key = run['config']['model'], run['recipe'], run['config']['identifier_channels'], run['warmstart']
            series.setdefault(key, []).append(values)
        for (model, recipe, ids, warm), traces in sorted(series.items()):
            values = np.stack(traces)
            label = f"{model} / {recipe} / IDs{ids} / n={len(traces)}"+(' warmstart' if warm else '')
            for column, ax in enumerate(axes):
                steps = np.arange(1, values.shape[1]+1)
                line, = ax.plot(steps, np.maximum(values[..., column].mean(0), 1e-9), label=label)
                ax.fill_between(steps, np.maximum(values[..., column].min(0), 1e-9),
                                np.maximum(values[..., column].max(0), 1e-9), color=line.get_color(), alpha=.12)
        for ax, label in zip(axes, ('Mutable-state RMS change', 'Stone prediction flip fraction')):
            ax.set(xlabel='Rollout step', ylabel=label, xscale='log', yscale='log', ylim=(1e-9, 1))
            ax.axvline(32, color='black', ls=':', lw=1); ax.axvline(128, color='black', ls='--', lw=1)
            ax.spines[['top', 'right']].set_visible(False)
        axes[1].legend(fontsize=6)
        fig.suptitle('Frozen 9×9 validation; nuisance means then training-seed mean/range; display floor1e-9', fontsize=10)
        name = f'rollout_dynamics_{task}_cap{cap}.png'
        fig.savefig(out / name, dpi=170); plt.close(fig); figures.append(name)
    return figures


def main():
    out = ROOT / "reports/research_followup"
    out.mkdir(parents=True, exist_ok=True)
    training, evaluations, probes = [], [], []
    for path in sorted((ROOT / "results/research_training").glob("*/summary.json")):
        d = json.loads(path.read_text())
        config = yaml.safe_load((path.parent / "config.yaml").read_text())
        config.setdefault("task", "liberties")
        annotation = path.parent / "initialization.json"
        initial = json.loads(annotation.read_text()) if annotation.exists() else {}
        reconstructed = path.parent / "data/supervised_stream_reconstruction.json"
        stream_annotation = json.loads(reconstructed.read_text()) if reconstructed.exists() else {}
        # Separate CPU plumbing checks from measured GPU experiments.
        gpu = any("cuda" in value.lower() or "gpu" in value.lower() for value in d["hardware"]["devices"])
        model_path = path.parent / 'model.json'
        parameters = d.get('parameters') or (json.loads(model_path.read_text()).get('parameters') if model_path.exists() else None)
        nine = [r for r in d.get("results", []) if r["size"] == 9 and r["depth"] == 128]
        training.append(dict(run=path.parent.name, gpu=gpu, config=config, summary=d,
                             parameters=parameters,
                             recipe=signature(config, RECIPE_FIELDS),
                             supervised_stream_sha256=d.get("supervised_stream_sha256", stream_annotation.get("supervised_stream_sha256")),
                             user_gate_assessment=stability_assessment(d["results"]) if d.get("results") else None,
                             warmstart=bool(config.get("warmstart_sha256") or initial.get("warmstart_sha256")),
                             initialization_annotation=initial,
                             ID_prediction_disagreement=validation_id_disagreement(path.parent, config),
                             ID_accuracy_range=(max((r["stone_accuracy"] for r in nine))-min((r["stone_accuracy"] for r in nine)))
                             if config["identifier_channels"] and nine else None))
    for path in sorted((ROOT / "results/research_evaluation").glob("*/summary.json")):
        config = yaml.safe_load((path.parent / 'config.yaml').read_text())
        evaluations.append({"run": path.parent.name, "namespace": config['namespace'], **json.loads(path.read_text())})
    for path in sorted((ROOT / "results/research_validation_probe").glob("*/summary.json")):
        probes.append({"run": path.parent.name, **json.loads(path.read_text())})
    selection_file = ROOT / "results/cloud/research/recipe_selection.json"
    selection = json.loads(selection_file.read_text()) if selection_file.exists() else None
    matched = matching_audit(training)
    curve_figures = learning_curves(training, out)
    dynamics_figures = rollout_dynamics(training, out)
    from .research_overview import overview
    outcome, overview_lines = overview(training, evaluations)
    oracle_caches = [json.loads(path.read_text()) for path in sorted((ROOT/'results/race_stream_cache').glob('*/manifest.json'))]
    write_json(out / 'outcome_summary.json', outcome)
    payload = dict(training=training, final_evaluations=evaluations, validation_probes=probes, recipe_selection=selection, matched_data_audit=matched,
                   outcome_overview=outcome,
                   oracle_materialization=oracle_caches,
                   existing_audit="../checkpoint_audit/SUMMARY.md",
                   protocol="../RESEARCH_PROTOCOL.md",
                   cautions=["CPU smoke runs are not training results", "Warmstarts are excluded from matched from-scratch comparisons",
                             "Static simple-eye counts are not unconditional life or playing strength",
                             "Exact reference success does not imply neural learnability"])
    write_json(out / "RESULTS.json", payload)
    lines = ["# NCA Go follow-up research", "", "All numbers are measured. Unfinished stages remain unfinished.", "",
             "[Prespecified protocol](../RESEARCH_PROTOCOL.md) · [Existing checkpoint audit](../checkpoint_audit/SUMMARY.md)", "",
             "The existing audit rules out a strict radius 32 grid light cone as the dominant explanation. Every 13×13 through 25×25 board lies within that field; 91.5% of the original asynchronous model's 37×37 errors at D32 have every liberty within it. Long chain distance correlates with errors and the old model drifts at longer depths. Cycles are confounded by size and class; learned sum/max baselines and controlled pairs are required for mechanism claims.", "",
             "## Whole-board stability and identifiers", "",
             "The relative gate is the user's 0.2 percentage point criterion, recomputed from raw metrics. Macro accuracy is reported separately; an earlier extra 99.5% floor is retained only in the original run summaries.", "",
             "Opening the new larger tests requires all three primary seeds to pass: absolute depth change at most 0.2 points, macro accuracy at least 95%, and D128 accuracy range across eight ID fields at most 0.2 points. A depth-stability pass alone does not qualify a run.", "",
             "| Run | Recipe | Model | Params | IDs | Seed | Initialization | Wall minutes | D128 | Macro128 | D512 | D1024 | Relative gate | ID range | ID disagreement |", "|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---:|---:|"]
    if overview_lines:
        lines[6:6] = overview_lines
    for r in training:
        if not r["gpu"]:
            continue
        s, c = r["summary"], r["config"]
        means = {d: np.mean(rows) if (rows := [x["stone_accuracy"] for x in s.get("results", []) if x["size"] == 9 and x["depth"] == d]) else np.nan for d in (128, 512, 1024)}
        values = [f"{100*means[d]:.3f}%" if np.isfinite(means[d]) else "not measured" for d in (128, 512, 1024)]
        id_range = f"{100*r['ID_accuracy_range']:.3f}pp" if r['ID_accuracy_range'] is not None else ("not measured" if c["identifier_channels"] else "not applicable")
        assessment = r['user_gate_assessment']
        macro = f"{100*assessment['nine_macro_at128']:.3f}%" if assessment else "not measured"
        gate = assessment['stability_gate'] if assessment else 'not evaluated'
        runtime = f"{s['wall_seconds']/60:.1f}" if 'wall_seconds' in s else 'not recorded'
        disagreement = f"{100*r['ID_prediction_disagreement']:.3f}%" if r['ID_prediction_disagreement'] is not None else ('not measured' if c['identifier_channels'] else 'not applicable')
        lines.append(f"| {r['run']} ({s['status']}) | {r['recipe']} | {c['model']} ({c['task']}, cap{c['cap']}) | {r['parameters']} | {c['identifier_channels']} | {c['seed']} | {'exploratory warmstart' if r['warmstart'] else 'scratch'} | {runtime} | {values[0]} | {macro} | {values[1]} | {values[2]} | {gate} | {id_range} | {disagreement} |")
    lines += ["", "ID disagreement is the mean fraction of 9×9 stone predictions differing from ID draw 0 at D128, with firing fixed. Stable accuracy does not require identical predictions. Recipe differences are disclosed below. Projection bounds mutable-state norm; it does not by itself prove prediction convergence. Replay continuation may carry states older than the 128-step fresh horizon.", "",
              "Recurrent qualification and final rollouts use stochastic firing at rate 0.8, with fresh IDs for each test draw. Gaussian noise, damage and target swaps are training perturbations and are disabled during these accuracy evaluations. The feedforward ResNet uses one forward pass; mutable-state perturbations do not apply to it.", "",
              "| Recipe | Updates / LR schedule | Gradient window | Projection groups | Drift weight | ID input scale | ID replay policy | Target swaps | Oracle delivery |",
              "|---|---|---:|---:|---:|---:|---|---|---|"]
    for key in sorted({r['recipe'] for r in training if r['gpu']}):
        c = next(r['config'] for r in training if r['recipe'] == key)
        lines.append(f"| {key} | {c['training_steps']} / {c.get('schedule_steps') or c['training_steps']} | {c.get('gradient_window', 128)} | {c['normalization_groups']} | {c['change_weight']} | {c.get('identifier_input_scale', 1):.4f} | {c.get('identifier_replay_policy', 'chunk')} | {c['target_swap']} | {c.get('oracle_stream_delivery', 'online generation')} |")
    if any(r['config'].get('race_stream_cache') for r in training):
        lines += ['', 'Accelerated race replicas consume a checksum-sealed sequence generated once by the original exact oracle, with the same candidate order and validation exclusions. This richer-task data-delivery change is disclosed separately. The main whole-board models generate online throughout.', '']
        for cache in oracle_caches:
            lines += [f"The shared oracle sequence contains {cache['count']:,} candidates and took {cache['wall_seconds']/60:.1f} CPU minutes to generate once. This materialization time is separate from the GPU-run wall times above.", '']
        prefix_path = ROOT / 'results/cloud/research/race_prefix_checkpoint_audit.json'
        if prefix_path.exists():
            prefix = json.loads(prefix_path.read_text())
            if prefix['exact_all_three_prefixes']:
                ratios = [row['observed_wall_speed_ratio'] for row in prefix['records']]
                lines += [f"All three accelerated replicas have byte-identical saved 5,000-update checkpoints and identical recorded validation prefixes to their original online runs. Their observed wall-time ratios are {min(ratios):.2f}–{max(ratios):.2f}×; concurrent worker loads differ, so this is not an isolated throughput benchmark. Original runs were safely interrupted and retained as diagnostics, rather than counted as additional independent replicas.", '']
    lines += ["", "### Actual data matching", "",
              "Matching is certified only when both the ordered candidate-board digest and the ordered augmented supervised-token/label digest agree. ID draws are nuisance repetitions; they are not independent training seeds.", "",
              "The baselines share the recipe selected for the NCA and the same update budget. They were not each given a separate hyperparameter search. Parameter counts are approximately matched; receptive fields, FLOPs and wall times differ. Poor training fit or depth drift can confound the sum/max comparison, so a score gap alone does not establish double counting or architecture superiority.", "",
              "| Data group | Completed scratch runs | Candidate digest agrees | Supervised digest agrees | Fully verified |", "|---|---:|---|---|---|"]
    for row in matched:
        lines.append(f"| {row['data_group']} | {len(row['runs'])} | {row['candidate_digests_identical']} | {row['supervised_digests_identical']} | {row['fully_verified']} |")
    if not any(r["gpu"] for r in training):
        lines += ["", "No completed new GPU training runs have been archived locally yet."]
    for name in curve_figures:
        lines += ['', f'![Recorded validation learning curves]({name})', '',
                  'Curves use the same predetermined validation subset. Shading shows the available training-seed range, which may have different counts early in a run. These curves are not the full qualification measurements.']
    for name in dynamics_figures:
        lines += ['', f'![Per-step state change and prediction flips]({name})', '',
                  'Dotted line: step 32. Dashed line: the maximum fresh training horizon 128. Flat accuracy alone does not prove state convergence; the unrounded per-step measurements are saved in rollout_dynamics.csv.']
    if probes:
        lines += ["", "### Saved pilot checkpoint qualification", "",
                  "A saved-checkpoint probe is a validation measurement, not a completed training run. CPU and GPU measurements remain labeled separately.", "",
                  "| Source checkpoint | Device | Saved update | D128 | Macro128 | D512 | D1024 | Relative gate |",
                  "|---|---|---:|---:|---:|---:|---:|---|"]
        for p in probes:
            a = stability_assessment(p['results'])
            gpu = any('cuda' in d.lower() or 'gpu' in d.lower() for d in p['hardware']['devices'])
            lines.append(f"| {p['source_run']} | {'GPU' if gpu else 'CPU'} | {p['checkpoint_iteration']} | {100*a['nine_accuracy'][128]:.3f}% | {100*a['nine_macro_at128']:.3f}% | {100*a['nine_accuracy'][512]:.3f}% | {100*a['nine_accuracy'][1024]:.3f}% | {a['stability_gate']} |")
    if selection:
        if selection.get('active_recipe'):
            lines += ["", f"The active primary recipe is `{selection['active_recipe']}`. It was proposed before larger final data were generated and qualified using only frozen small-board validation. All three primary seeds start from scratch. The earlier recipe selection and failed diagnostics remain recorded; exploratory warmstarts are excluded from matched comparisons."]
        else:
            lines += ["", f"The initial 32-ID recipe was selected from the full small-board validation probe of update {selection.get('qualification_checkpoint_iteration', 'unknown')} in `{selection['source_training_run']}`. A separate prospective rescue is still awaiting qualification. Exploratory warmstarts remain excluded from the matched baseline comparison."]
    lines += ["", "## Proportional depth, matched baselines and witnesses", "",
              "Whole-board D/diameter uses the maximum chain diameter on that board. Proportional witness depth uses the maximum queried-chain diameter across its two members. Fixed-depth witness tables and all confusion matrices remain available separately. Baseline training-seed counts are disclosed in the cohort tables. Nuisance ID draws do not supply training-seed uncertainty.", ""]
    lines += ['The random race boards use playable 5×N rectangles represented on padded N×N canvases. The separate outcome-changing witnesses and cycle controls use full N×N boards, with exactly proved first-capture labels. Their board domains and generator families differ; the pair scores are additional structural diagnostics.', '',
              'Stone accuracy weights labeled stones; macro accuracy averages recall across true classes present in that split. Missing classes are excluded and their support is disclosed below. The board score requires every labeled stone on a board to be correct. Capturing-race labels are game outcomes broadcast to stones, so stone accuracy alone is not a rate of completely solved games.', '']
    if not evaluations:
        lines += ["Final larger-board evaluations have not yet been completed. Their data is sealed only after the primary stability and identifier gates pass."]
    else:
        confusion_archive(evaluations, out)
        lines += ["[All final-test and witness confusion matrices, including overcounts and undercounts](CONFUSIONS.md)", ""]
    member_path = out / 'pair_members.json'
    members = json.loads(member_path.read_text())['records'] if member_path.exists() else []
    for s in evaluations:
        lines += [f"### {s['model']} {s.get('task', 'liberties')} cap{s.get('cap', 4)} seed{s['seed']} ({s['source_run']})", "",
                  "| Size | D/diameter | Stone accuracy | Macro accuracy | All stones on board correct |", "|---:|---:|---:|---:|---:|"]
        for size in (9, 13, 19, 25, 37):
            for ratio in (.5, 1., 2., 4.):
                rows = [r for r in s["records"] if r["size"] == size and r["ratio"] == ratio]
                if rows:
                    lines.append(f"| {size} | {ratio} | {100*np.mean([r['stone_accuracy'] for r in rows]):.3f}% | {100*np.mean([r['macro_accuracy'] for r in rows]):.3f}% | {100*np.mean([r['board_exact'] for r in rows]):.3f}% |")
        if s.get('identifier_checks'):
            lines += ["", "ID sensitivity holds firing randomness fixed and changes only the ID field.", "",
                      "| Size | D/diameter | Stone accuracy range across ID draws | Prediction disagreement from draw0 |",
                      "|---:|---:|---:|---:|"]
            for size in (9, 13, 19, 25, 37):
                for ratio in (.5, 1., 2., 4.):
                    rows = [r for r in s['records'] if r['size'] == size and r['ratio'] == ratio]
                    checks = [r for r in s['identifier_checks'] if r['size'] == size and r['ratio'] == ratio]
                    if rows and checks:
                        accuracy_range = 100*(max(r['stone_accuracy'] for r in rows)-min(r['stone_accuracy'] for r in rows))
                        lines.append(f"| {size} | {ratio} | {accuracy_range:.3f}pp | {100*np.mean([r['disagreement_from_draw0'] for r in checks]):.3f}% |")
        lines += ["", "Witness primary metric: both members correct. Query accuracy alone is insufficient. Pair overlap with online training or previously opened boards is flagged; raw pair metrics then describe structural diagnostics, and unseen-only metrics exclude both kinds of overlap. Boards of 13×13 or larger cannot canonically overlap the 9×9 training canvas, but may overlap earlier diagnostic boards.", ""]
        for kind in ("witness", "cycle_pairs", "race_witness", "eye_witness"):
            lines += [f"{kind}:", "", "| Size | D/diameter | Both correct | Draw range | Unseen both correct | Unseen pairs | Training overlaps | Previously opened overlaps |", "|---:|---:|---:|---:|---:|---:|---:|---:|"]
            for size in (9, 13, 19, 25, 37):
                for ratio in (.5, 1., 2., 4.):
                    rows = [r for r in s["paired"] if r["kind"] == kind and r["size"] == size and r.get("ratio") == ratio]
                    if rows:
                        by_draw = [np.mean([r["pair_both_correct"] for r in rows if r["draw"] == draw]) for draw in sorted(set(r["draw"] for r in rows))]
                        first_draw = min(r['draw'] for r in rows)
                        unique_rows = [r for r in rows if r['draw'] == first_draw]
                        unseen_trials = sum(r.get('unseen_pairs', 0) for r in rows)
                        unseen = (f"{100*sum(r['unseen_pair_both_correct']*r['unseen_pairs'] for r in rows if r.get('unseen_pair_both_correct') is not None)/unseen_trials:.2f}%"
                                  if unseen_trials else 'no unseen pairs')
                        counts = [sum(r.get(field, 0) for r in unique_rows) for field in ('unseen_pairs', 'training_overlap_pairs', 'previously_opened_overlap_pairs')]
                        lines.append(f"| {size} | {ratio} | {100*np.mean(by_draw):.2f}% | {100*min(by_draw):.2f}--{100*max(by_draw):.2f}% | {unseen} | {counts[0]} | {counts[1]} | {counts[2]} |")
        control_members = [row for row in members if row['evaluation_run'] == s['run'] and row['kind'] == 'cycle_pairs' and row.get('ratio') == 4]
        if control_members:
            lines += ['', 'Label-preserving cycle controls, D/diameter=4. A and B refer to paired members; the measured cycle fractions verify which queried chains actually change topology.', '',
                      '| Size | A accuracy | B accuracy | A queried chains cyclic | B queried chains cyclic |', '|---:|---:|---:|---:|---:|']
            for size in (9, 13, 19, 25, 37):
                a = [row for row in control_members if row['size'] == size and row['member'] == 'A']
                b = [row for row in control_members if row['size'] == size and row['member'] == 'B']
                lines.append(f"| {size} | {100*np.mean([r['accuracy'] for r in a]):.2f}% | {100*np.mean([r['accuracy'] for r in b]):.2f}% | {100*np.mean([r['query_chain_cycle_fraction'] for r in a]):.1f}% | {100*np.mean([r['query_chain_cycle_fraction'] for r in b]):.1f}% |")
    lines += ["", "## Richer tasks", "",
              "Liberty counts capped at 16, static simple-eye counts (including diagonal false-eye checks) and finite first-capture games have independent labels. Eye cycle controls preserve the exact liberty set and simple-eye count. Separate corner-eye witnesses change the count at the same liberties; their cycle and diagonal change together. Capture outcomes are proved independently on both members of full N×N board pairs. Separate two-stone race witnesses change the proved outcome at six liberties for both groups. Random race training and whole-board tests use 5×N rectangles, so the paired tests also introduce a domain shift. These synthetic experiments do not establish KataGo robustness or playing strength.", "",
              "Benson, ladders and the player were parked during qualification and remain outside this counting study. Earlier failed-gate smoke results are not used as evidence of ability.", ""]
    heuristic_path = ROOT / 'reports/checkpoint_audit/race_heuristic_validation.json'
    response_path = ROOT / 'results/cloud/research/animation_response_audit.json'
    if response_path.exists():
        lines += ['The table describes the single predetermined draw0 witness animation per seed and task. State differences exclude all frozen input channels, and are exactly zero before the nearest edit can reach the query. A nonzero response does not imply a correct answer or identify the failure mechanism. These sampled trajectories illustrate the aggregate results rather than replace them.', '',
            '| Task / seed | Query state RMS difference at 64 | Last illustrated step | Query predictions A/B | True A/B |',
            '|---|---:|---:|---|---|']
        for row in json.loads(response_path.read_text())['records']:
            i = row['depths'].index(64)
            labels = class_names(row['task'], row['cap'])
            predicted = ' / '.join(labels[index] for index in row['query_predictions'][-1])
            truth = ' / '.join(labels[index] for index in row['query_truth'])
            lines.append(f"| {row['task']} cap{row['cap']} / {row['seed']} | {row['query_mutable_RMS_difference'][i]:.3g} | {row['depths'][-1]} | {predicted} | {truth} |")
        lines += ['']
    reference_path = ROOT / 'reports/checkpoint_audit/richer_reference_validation.json'
    if reference_path.exists():
        lines += ['The top 16 hand-coded ID-set reference below uses 32-bit IID keys on the existing frozen validation split. It has one local-ID loading phase followed by at most the maximum chain diameter in message rounds. This demonstrates a counting algorithm, not neural learning or larger-board generalization.', '',
                  '| Size | Boards | ID draws | Correct stone-draw trials | Accuracy | Empty-ID collisions |', '|---:|---:|---:|---:|---:|---:|']
        for row in json.loads(reference_path.read_text())['records']:
            lines.append(f"| {row['size']} | {row['boards']} | {row['draws']} | {row['correct_stone_draws']} / {row['stone_draws']} | {100*row['accuracy']:.3f}% | {row['empty_ID_collisions']} |")
    if heuristic_path.exists():
        rows = json.loads(heuristic_path.read_text())['records']
        lines += ['The race sanity checks below use only the already frozen small-board validation split. These are fixed hand-written heuristics, not learned models or exact solvers.', '',
                  '| Size | Heuristic | Stone accuracy | Macro accuracy |', '|---:|---|---:|---:|']
        for row in rows:
            lines.append(f"| {row['size']} | {row['baseline']} | {100*row['stone_accuracy']:.2f}% | {100*row['macro_accuracy']:.2f}% |")
    for path in sorted((ROOT / 'reports/checkpoint_audit').glob('race_heuristic_*.json')):
        measured = json.loads(path.read_text())
        if measured['scope'] != 'final':
            continue
        lines += ['', f"Fixed race heuristics on sealed namespace `{measured['namespace']}`. These full-board rules were fixed on small-board validation before the final split; their exact group/eye computations have greater access than a local update rule.", '',
            '| Size | Heuristic | Whole-board macro accuracy | Outcome-changing pairs both correct | Cycle-control pairs both correct |',
            '|---:|---|---:|---:|---:|']
        for row in measured['records']:
            selected = {p['kind']: p['pair_both_correct'] for p in measured['paired'] if p['size'] == row['size'] and p['baseline'] == row['baseline']}
            lines.append(f"| {row['size']} | {row['baseline']} | {100*row['macro_accuracy']:.2f}% | {100*selected['race_witness']:.2f}% | {100*selected['cycle_pairs']:.2f}% |")
    manifests = []
    for path in sorted((ROOT / 'results/research_final_data').glob('*/manifest.json')):
        manifests.append(json.loads(path.read_text()))
    if manifests:
        lines += ["## Final split composition", "",
                  "Final boards reject every saved online training canonical position and validation position, as well as previously saved boards from the old analyses. This can shift the accepted generator mix, particularly when finite controlled support was exhausted during training. Each class's stone support and rejection count are disclosed; this is the accepted unseen distribution.", "",
                  "| Namespace | File | Accepted source counts | Rejected training positions | Rejected previously opened positions | True-class stone support |",
                  "|---|---|---|---:|---:|---|"]
        for manifest in manifests:
            for row in manifest['files']:
                if 'accepted_sources' in row:
                    lines.append(f"| {manifest['namespace']} | {row['name']} | {row['accepted_sources']} | {row['rejected_training_positions']} | {row.get('rejected_previously_opened_positions', 0)} | {row['class_stone_support']} |")
        for manifest in manifests:
            if manifest['task'] == 'eyes':
                row = next(r for r in manifest['files'] if r['name'] == 'boards_9.npz')
                accepted = row['accepted_sources']
                unsupported = [i for i, n in enumerate(row['class_stone_support']) if n == 0]
                lines += ['', f"The 9×9 eye final set accepted {accepted.get('legal_random', 0)} legal-random boards and {accepted.get('simple_eye_setup', 0)} constructed setups after exclusions. Classes with no stone support: {unsupported}. Its score describes this accepted unseen mix, not the original validation distribution. The explicit class-support table is needed when comparing sizes.", '']
        for manifest in manifests:
            by_source = {r['source_run']: r for r in evaluations if r['namespace'] == manifest['namespace']}
            witness_kind = 'race_witness' if manifest['task'] == 'race' else ('eye_witness' if manifest['task'] == 'eyes' else 'witness')
            cohorts = {}
            for source in manifest['source_checkpoints']:
                if source['run'] in by_source:
                    key = (source['kind'], source['model_config']['identifier_channels'])
                    cohorts.setdefault(key, []).append(by_source[source['run']])
            large_label = '5×37 capture board' if manifest['task'] == 'race' else '37×37'
            lines += ['', f"## Architecture cohort summary: {manifest['namespace']}", '',
                      'Average nuisance draws within each training seed first. Ranges below describe training seeds, not independent stone samples. D/diameter=4; the witness column uses outcome-changing pairs when available.', '',
                      f'| Model | IDs | Training seeds | {large_label} macro accuracy | Seed range | Witness both correct | Seed range |',
                      '|---|---:|---:|---:|---:|---:|---:|']
            for (kind, ids), cohort in sorted(cohorts.items()):
                values = [np.mean([r['macro_accuracy'] for r in run['records'] if r['size'] == 37 and r['ratio'] == 4]) for run in cohort]
                pairs = [np.mean([r['pair_both_correct'] for r in run['paired'] if r['kind'] == witness_kind and r['size'] == 37 and r.get('ratio') == 4]) for run in cohort]
                pair_mean = f'{100*np.mean(pairs):.2f}%' if all(np.isfinite(pairs)) else 'not measured'
                pair_range = f'{100*min(pairs):.2f}--{100*max(pairs):.2f}%' if all(np.isfinite(pairs)) else 'not measured'
                lines.append(f"| {kind} | {ids} | {len({r['seed'] for r in cohort})} | {100*np.mean(values):.3f}% | {100*min(values):.3f}--{100*max(values):.3f}% | {pair_mean} | {pair_range} |")
            primary = [by_source[row['run']] for row in manifest['source_checkpoints'] if row.get('primary') and row['run'] in by_source]
            if len({r['seed'] for r in primary}) < 3:
                continue
            lines += ["", f"## Independent training-seed replication: {manifest['namespace']}", "",
                      "Average nuisance ID draws within each training seed first. The range below is across independent training seeds, not a stone-level confidence interval.", "",
                      "| Size | D/diameter | Mean primary witness both-correct | Training-seed range | Seeds |",
                      "|---:|---:|---:|---:|---:|"]
            for size in (9, 13, 19, 25, 37):
                for ratio in (.5, 1., 2., 4.):
                    values = [np.mean([r['pair_both_correct'] for r in s['paired'] if r['kind'] == witness_kind and r['size'] == size and r.get('ratio') == ratio]) for s in primary]
                    if all(np.isfinite(values)):
                        lines.append(f"| {size} | {ratio} | {100*np.mean(values):.2f}% | {100*min(values):.2f}--{100*max(values):.2f}% | {len(values)} |")
    venues = ROOT / 'results/cloud/research/venue_options.json'
    if venues.exists():
        lines += ['', '## Where this work could be submitted', '',
            'My first target would be a relevant ICLR 2027 workshop, once its topic and call are confirmed. The conference suggests February 1, 2027 for workshop contributions; each workshop sets its own deadline. October 9, 2026 is the organizer-proposal deadline, not our paper deadline. [Official workshop call](https://iclr.cc/Conferences/2027/CallForWorkshops)', '',
            'ALIFE 2027 is a good topical match for neural cellular automata and distributed computation. It is scheduled for July 19–23, 2027 in Prague; the official listing has not announced a submission deadline. [Official ALIFE listing](https://alife.org/conference/alife-2027/)', '',
            'ICLR 2027 main-track submissions closed September 25, 2026. This experiment archive does not itself establish main-track readiness or a new counting mechanism. A paper should center the actual three-seed results, matched baselines and reproducible failure analysis. These venue judgments are editorial recommendations, not acceptance predictions. Dates checked October 7, 2026. [Official main-track call](https://iclr.cc/Conferences/2027/CallForPapers)', '']
    (out / "REPORT.md").write_text("\n".join(lines)+"\n")
    records = []
    by_run = {r['run']: r for r in training}
    for s in evaluations:
        recipe = by_run[s['source_run']]['recipe'] if s['source_run'] in by_run else 'unknown recipe'
        label = f"{s['model']} / recipe {recipe} / IDs{s['model_config']['identifier_channels']}"
        records.extend(dict(run=s["run"], model=s["model"], series=label, task=s.get("task", "liberties"),
                            cap=s.get("cap", 4), seed=s["seed"], **r) for r in s["records"])
    if records:
        with (out / "final_accuracy.csv").open("w", newline="") as stream:
            fields = [k for k in records[0] if k not in ("confusion", "per_class_accuracy")]
            w = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(records)
        for task, cap in sorted({(r['task'], r['cap']) for r in records}):
            selected = [r for r in records if r['task'] == task and r['cap'] == cap]
            fig, axes = plt.subplots(1, 5, figsize=(17, 4), layout="constrained")
            for ax, size in zip(axes, (9, 13, 19, 25, 37)):
                for model in sorted(set(r["series"] for r in selected)):
                    rows = [r for r in selected if r["series"] == model and r["size"] == size]
                    ratios = sorted(set(r["ratio"] for r in rows))
                    architecture = {'nca': 'NCA', 'rcnn': 'Recurrent CNN', 'resnet': 'ResNet',
                                    'gnn_sum': 'GNN sum', 'gnn_max': 'GNN max'}[rows[0]['model']]
                    id_label = model.rsplit(' / ', 1)[-1].replace('IDs', 'IDs ')
                    ax.plot(ratios, [100*np.mean([r["macro_accuracy"] for r in rows if r["ratio"] == v]) for v in ratios], "o-", label=f'{architecture} · {id_label}')
                board_title = f"5×{size}" if task == 'race' else f"{size}×{size}"
                ax.set(title=board_title, xlabel="D / maximum chain diameter", ylim=(0, 102), xscale="log", xticks=[.5, 1, 2, 4], xticklabels=['0.5', '1', '2', '4'])
                ax.minorticks_off()
                ax.spines[["top", "right"]].set_visible(False)
            axes[0].set_ylabel("Macro accuracy (%)"); axes[-1].legend(fontsize=7)
            fig.savefig(out / f"depth_by_diameter_{task}_cap{cap}.png", dpi=180)
            plt.close(fig)
    print(out / "REPORT.md", flush=True)


if __name__ == "__main__":
    main()
