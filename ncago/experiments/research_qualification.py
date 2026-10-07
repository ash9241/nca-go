"""Record main qualification from completed, immutable small-board results."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import yaml
from .common import ROOT, write_json
from .research_train import stability_assessment


def qualify(runs, output):
    if len(runs) != 3:
        raise ValueError('Exactly three main training runs required')
    rows, recipes = [], []
    for run in map(Path, runs):
        config = yaml.safe_load((run / 'config.yaml').read_text())
        summary = json.loads((run / 'summary.json').read_text())
        if summary['status'] != 'complete' or config['model'] != 'nca' or config['task'] != 'liberties' or config['cap'] != 4:
            raise RuntimeError('Completed main cap4 NCA required')
        if config['identifier_channels'] != 32 or config.get('warmstart_sha256') or (run / 'initialization.json').exists():
            raise RuntimeError('Main qualification requires32 IDs and scratch initialization')
        if not any('cuda' in device.lower() or 'gpu' in device.lower() for device in summary['hardware']['devices']):
            raise RuntimeError('CPU plumbing runs cannot qualify the primary experiment')
        nine = [row for row in summary['results'] if row['size'] == 9 and row['depth'] == 128]
        if len(nine) != 8 or {row['draw'] for row in nine} != set(range(8)):
            raise RuntimeError('All eight prespecified ID draws required')
        assessment = stability_assessment(summary['results'])
        id_range = 100*(max(row['stone_accuracy'] for row in nine)-min(row['stone_accuracy'] for row in nine))
        qualified = bool(assessment['stability_gate'] and assessment['useful_accuracy'] and id_range <= .2)
        rows.append(dict(run=run.name, seed=config['seed'], initialization='scratch', qualified=qualified,
                         assessment=assessment, ID_range_pp=id_range,
                         checkpoint_iteration=config['training_steps'], checkpoint_sha256=sha256((run / 'ckpt/final.msgpack').read_bytes()).hexdigest(),
                         summary_sha256=sha256((run / 'summary.json').read_bytes()).hexdigest(),
                         candidate_stream_sha256=summary['stream_sha256'], supervised_stream_sha256=summary['supervised_stream_sha256']))
        recipes.append({key: value for key, value in config.items() if key != 'seed'})
    if {row['seed'] for row in rows} != {0, 1, 2} or any(recipe != recipes[0] for recipe in recipes[1:]):
        raise RuntimeError('Three distinct seeds of a single prospective recipe required')
    payload = dict(primary_gate_passed=all(row['qualified'] for row in rows), runs=rows,
                   scope='Frozen9/13 validation only;no new final data used to choose checkpoints',
                   thresholds=dict(absolute_depth_change_pp=.2, minimum_macro_accuracy=.95, maximum_ID_accuracy_range_pp=.2),
                   recipe=recipes[0])
    write_json(output, payload)
    print(json.dumps(payload, indent=2), flush=True)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', nargs='+', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/cloud/research/main_qualification.json')
    args = parser.parse_args()
    qualify(args.runs, args.output)


if __name__ == '__main__':
    main()
