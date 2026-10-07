"""Check animation predictions against their saved final-evaluation draws."""
import json
from hashlib import sha256
import numpy as np
import yaml
from .common import ROOT, write_json


def main():
    evaluations = {}
    for file in sorted((ROOT / 'results/research_evaluation').glob('*/summary.json')):
        summary = json.loads(file.read_text())
        if summary['status'] != 'complete':
            continue
        config = yaml.safe_load((file.parent / 'config.yaml').read_text())
        key = summary['source_run'], config['namespace']
        if key in evaluations:
            raise RuntimeError(f'Duplicate final evaluation for {key}')
        evaluations[key] = file.parent
    checks = []
    for file in sorted((ROOT / 'reports/research_followup/media').glob('*/manifest.json')):
        manifest = json.loads(file.read_text())
        evaluation = evaluations[(manifest['source_run'], manifest['final_namespace'])]
        for example in manifest['examples']:
            media_file = file.parent / (example['name']+'.npz')
            evaluator_files = [evaluation / 'eval' / name for name in example['evaluator_files']]
            checked_depths = []
            with np.load(media_file) as media:
                indices = np.asarray(example['evaluator_board_indices'])
                for evaluator_file in evaluator_files:
                    with np.load(evaluator_file) as saved:
                        if len(media['queries']):
                            common = sorted(set(map(int, media['depths'])) & set(map(int, saved['depths'])))
                        else:
                            common = [int(saved['depths'][indices[0]])]
                        for depth in common:
                            m = int(np.flatnonzero(media['depths'] == depth)[0])
                            predictions = media['predictions'][m]
                            if len(media['queries']):
                                e = int(np.flatnonzero(saved['depths'] == depth)[0])
                                query = media['queries']
                                predictions = predictions[np.arange(len(query)), query[:, 0], query[:, 1]]
                                expected = saved['predictions'][e, indices]
                            else:
                                expected = saved['predictions'][indices]
                            if not np.array_equal(predictions, expected):
                                raise AssertionError(f'Animation differs from final evaluation: {media_file}, step {depth}')
                            checked_depths.append(depth)
            if not checked_depths:
                raise RuntimeError('Animation has no depth in common with its final evaluation')
            checks.append(dict(source_run=manifest['source_run'], namespace=manifest['final_namespace'],
                example=example['name'], depths=sorted(set(checked_depths)), exact_prediction_match=True,
                media_sha256=sha256(media_file.read_bytes()).hexdigest(),
                evaluator_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in evaluator_files}))
    if not checks:
        raise RuntimeError('No completed learned animations to audit')
    write_json(ROOT / 'results/cloud/research/media_prediction_audit.json', dict(
        all_exact=True, examples=len(checks), checks=checks,
        scope='Predetermined draw0 animations match saved fixed-depth final predictions; no outcome-based selection'))
    print(f'All {len(checks)} learned animations match saved final predictions', flush=True)


if __name__ == '__main__':
    main()
