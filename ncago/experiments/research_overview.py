"""Explain completed sealed measurements without filling missing results."""
import json
from collections import defaultdict
import numpy as np
from .common import ROOT


def seed_range(values):
    return dict(mean=float(np.mean(values)), minimum=float(min(values)), maximum=float(max(values)), seeds=len(values))


def overview(training, evaluations):
    complete = {(row['namespace'], row['source_run']): row for row in evaluations if row['status'] == 'complete'}
    training_by_name = {row['run']: row for row in training}
    namespaces = []
    for file in sorted((ROOT / 'results/research_final_data').glob('*/manifest.json')):
        manifest = json.loads(file.read_text())
        sources = manifest['source_checkpoints']
        if not all((manifest['namespace'], source['run']) in complete for source in sources):
            continue
        groups = defaultdict(list)
        for source in sources:
            groups[(source['kind'], source['model_config']['identifier_channels'])].append(complete[(manifest['namespace'], source['run'])])
        kind = {'liberties': 'witness', 'eyes': 'eye_witness', 'race': 'race_witness'}[manifest['task']]
        cohorts = []
        for (model, identifiers), runs in sorted(groups.items()):
            rows = []
            for run in runs:
                boards = [row for row in run['records'] if row['size'] == 37 and row['ratio'] == 4]
                pairs = [row for row in run['paired'] if row['size'] == 37 and row['kind'] == kind and row.get('ratio') == 4]
                cycles = [row for row in run['paired'] if row['size'] == 37 and row['kind'] == 'cycle_pairs' and row.get('ratio') == 4]
                if not boards or not pairs or not cycles:
                    raise RuntimeError('Completed evaluation is missing prespecified overview measurements')
                rows.append(dict(seed=run['seed'], source_run=run['source_run'],
                    macro=float(np.mean([r['macro_accuracy'] for r in boards])),
                    stone=float(np.mean([r['stone_accuracy'] for r in boards])),
                    witness_both=float(np.mean([r['pair_both_correct'] for r in pairs])),
                    cycle_both=float(np.mean([r['pair_both_correct'] for r in cycles])),
                    ID_macro_range=float(max(r['macro_accuracy'] for r in boards)-min(r['macro_accuracy'] for r in boards)),
                    overcounts=sum(r['overcounts'] for r in boards) if manifest['task'] != 'race' else None,
                    undercounts=sum(r['undercounts'] for r in boards) if manifest['task'] != 'race' else None))
            cohorts.append(dict(model=model, identifiers=identifiers, per_seed=rows,
                macro=seed_range([r['macro'] for r in rows]), witness_both=seed_range([r['witness_both'] for r in rows]),
                cycle_both=seed_range([r['cycle_both'] for r in rows])))
        namespaces.append(dict(namespace=manifest['namespace'], task=manifest['task'], cap=manifest['cap'], cohorts=cohorts,
            primary_sources=[source['run'] for source in sources if source.get('primary')]))
    lines = []
    main = next((row for row in namespaces if row['task'] == 'liberties' and row['cap'] == 4), None)
    if main:
        primary = [complete[(main['namespace'], name)] for name in main['primary_sources']]
        if len(primary) != 3 or len({row['seed'] for row in primary}) != 3:
            raise RuntimeError('The main interpretation requires three independent primary seeds')
        selected = next(row for row in main['cohorts'] if row['model'] == 'nca' and row['identifiers'] == 32)
        q = [training_by_name[name]['user_gate_assessment'] for name in main['primary_sources']]
        a128 = 100*np.mean([row['nine_accuracy'][128] for row in q])
        a1024 = 100*np.mean([row['nine_accuracy'][1024] for row in q])
        macro = selected['macro']; pairs = selected['witness_both']
        strong = macro['mean'] >= .95 and pairs['minimum'] >= .9
        lines += ['## What we achieved, in plain language', '',
            'Each grid cell repeatedly updates a small memory using its neighbors. Random fingerprints let a counting algorithm recognize the same empty point when it reaches that point through several paths. The fingerprints contain no correct answers; a learned model still has to discover how to use them.', '',
            f'The main three-seed model averaged {a128:.3f}% stone accuracy on frozen 9×9 validation at 128 steps and {a1024:.3f}% at 1,024 steps. All three seeds passed the prespecified depth-stability and random-ID gates before larger tests were generated.', '',
            f'At 37×37 and D/diameter=4, it reached {100*macro["mean"]:.2f}% macro accuracy (training-seed range {100*macro["minimum"]:.2f}–{100*macro["maximum"]:.2f}%) and {100*pairs["mean"]:.2f}% witness pairs both correct (range {100*pairs["minimum"]:.2f}–{100*pairs["maximum"]:.2f}%). A witness pair differs at one distant stone, so its primary score requires two correct answers.', '',
            ('This is a promising result on the stated synthetic counting tests: the model remained stable and handled the larger boards and difficult paired queries. It does not establish general Go reasoning or playing strength.' if strong else
             'The stability improvement is real, but these larger-board and witness measurements do not establish reliable systematic counting. A model can settle into a stable wrong answer. The difficult paired-query failures are part of the result and should appear in any public claim.'), '',
            'The successful small-board recipe combines bounded mutable states, scaled random-ID inputs, consistent IDs across replay continuations and a shorter gradient window. The separate pilots and failed earlier recipes are retained below. Because the successful recipe changes several ingredients together, these runs do not prove which ingredient caused the improvement.', '',
            'We tested these changes for specific reasons. Bounding the memory limits runaway amplitudes during extra updates. Scaling the 32 ID channels keeps their combined input variance comparable to the board clues. Retaining one fingerprint field while replay continues avoids changing names underneath stored messages. A 32-step gradient window makes long forward rollouts practical while still supervising their late predictions. Damage, noise, random horizons and late state-change penalties train the model to recover and settle. These are the motivations for the recipe; the measurements certify its stability rather than isolating each ingredient’s causal effect.', '',
            'The old errors were mostly inside the strict grid light cone and mostly undercounts. That rules out insufficient radius 32 as a complete explanation. It does not prove a particular counting shortcut or cycle mechanism. Sum/max GNN differences and cyclic/broken-cycle measurements below are diagnostic evidence; optimization differences and changes in stone geometry remain possible explanations.', '']
    richer = [row for row in namespaces if row is not main]
    if richer:
        lines += ['## Richer tasks: the complete three-seed picture', '',
            'These tasks test counts above the cap 4 ceiling, static eye points and finite first-capture outcomes. The table uses D/diameter=4 and averages nuisance draws within each training seed before reporting the training-seed range.', '',
            '| Task | 37-board macro accuracy: mean (seed range) | Outcome-changing pairs both correct | Label-preserving cycle pairs both correct |',
            '|---|---:|---:|---:|']
        for row in richer:
            cohort = next(c for c in row['cohorts'] if c['model'] == 'nca' and c['identifiers'] == 32)
            if cohort['macro']['seeds'] != 3:
                raise RuntimeError('Richer interpretation requires three completed training seeds')
            label = ('Liberties 1–15 and 16+' if row['task'] == 'liberties' else
                     'Static simple-eye counts 0–7 and 8+' if row['task'] == 'eyes' else
                     'First capture: 5×37 boards / 37×37 paired witnesses')
            cells = []
            for name in ('macro', 'witness_both', 'cycle_both'):
                value = cohort[name]
                cells.append(f"{100*value['mean']:.2f}% ({100*value['minimum']:.2f}–{100*value['maximum']:.2f}%)")
            lines.append('| '+label+' | '+' | '.join(cells)+' |')
        lines += ['', 'The richer learned models are NCAs; the matched neural-architecture comparison belongs to the main cap 4 task. Hand-coded references and fixed race heuristics are reported separately. Static simple eyes are not unconditional life, and the capturing-race witness uses one synthetic two-point-eye family. These measurements do not establish performance on FAR positions or full Go.', '']
    return dict(completed_namespaces=namespaces, interpretation_scope='Completed sealed evaluations only;seed ranges are not confidence intervals'), lines
