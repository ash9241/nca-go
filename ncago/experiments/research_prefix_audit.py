"""Verify the prospective scratch extension against saved20k prefixes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import yaml
from .common import ROOT, write_json


def audit(old, extended, cutoff=20000):
    old, extended = Path(old), Path(extended)
    configs = [yaml.safe_load((path / 'config.yaml').read_text()) for path in (old, extended)]
    differences = {key: [configs[0].get(key), configs[1].get(key)] for key in configs[0].keys() | configs[1].keys()
                   if configs[0].get(key) != configs[1].get(key)}
    if differences != {'training_steps': [cutoff, 30000]}:
        raise RuntimeError(f'Unexpected extension recipe differences: {differences}')
    prefixes = []
    for path in (old, extended):
        rows = [json.loads(line) for line in (path / 'metrics.jsonl').read_text().splitlines()]
        prefixes.append([{key: value for key, value in row.items() if key != 'elapsed_seconds'}
                         for row in rows if row.get('event') == 'validation' and row['iteration'] <= cutoff])
    if not prefixes[0] or prefixes[0][-1]['iteration'] != cutoff or len(prefixes[0]) != len(prefixes[1]):
        raise RuntimeError('The complete20k recorded prefix is required')
    old_checkpoint = old / 'ckpt/final.msgpack'
    new_checkpoint = extended / f'ckpt/step_{cutoff:06d}.msgpack'
    hashes = [sha256(path.read_bytes()).hexdigest() for path in (old_checkpoint, new_checkpoint)]
    matching = [a == b for a, b in zip(*prefixes)]
    return dict(seed=configs[0]['seed'], old_run=old.name, extended_run=extended.name,
                recipe_differences=differences, cutoff=cutoff, recorded_milestones=len(matching),
                exact_validation_prefix_match=all(matching), matching_milestones=sum(matching),
                exact_checkpoint_byte_match=hashes[0] == hashes[1], checkpoint_sha256=hashes,
                scope='Saved scratch reruns;no optimizer/replay-state resume;wall timings excluded from equality')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-runs', nargs=3, type=Path, required=True)
    parser.add_argument('--extended-runs', nargs=3, type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/cloud/research/extension_prefix_audit.json')
    args = parser.parse_args()
    rows = [audit(old, new) for old, new in zip(args.old_runs, args.extended_runs)]
    if {row['seed'] for row in rows} != {0, 1, 2}:
        raise RuntimeError('All three distinct primary training seeds required')
    write_json(args.output, dict(records=rows,
               exact_all_three_prefixes=all(row['exact_validation_prefix_match'] and row['exact_checkpoint_byte_match'] for row in rows)))
    print(args.output, flush=True)


if __name__ == '__main__':
    main()
