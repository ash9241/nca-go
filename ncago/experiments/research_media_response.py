"""Describe the query response in every predetermined paired animation."""
import json
import numpy as np
import yaml
from .common import ROOT, write_json


def main():
    records = []
    for path in sorted((ROOT / 'reports/research_followup/media').glob('*/manifest.json')):
        manifest = json.loads(path.read_text())
        run = ROOT / 'results/research_training' / manifest['source_run']
        summary = json.loads((run / 'summary.json').read_text())
        config = yaml.safe_load((run / 'config.yaml').read_text())
        model = json.loads((run / 'model.json').read_text())
        channels = model['model_config']['input_channels'] if 'model_config' in model else summary['model_config']['input_channels']
        for example in manifest['examples']:
            with np.load(path.parent / (example['name']+'.npz')) as data:
                if not len(data['queries']):
                    continue
                queries = data['queries']
                assert np.array_equal(queries[0], queries[1])
                q = tuple(queries[0])
                mutable = data['states'][..., channels:]
                delta = np.sqrt(np.mean((mutable[:, 0]-mutable[:, 1])**2, axis=-1))
                response = delta[:, q[0], q[1]]
                predictions = data['predictions'][:, np.arange(2), queries[:, 0], queries[:, 1]]
                truth = data['targets'][np.arange(2), queries[:, 0], queries[:, 1]]
                edits = np.argwhere(data['boards'][0] != data['boards'][1])
                nearest = int(np.abs(edits-np.asarray(q)).max(axis=1).min())
                depths = data['depths'].astype(int)
                assert np.all(response[depths < nearest] == 0)
                positive = np.flatnonzero(response > 0)
                records.append(dict(source_run=manifest['source_run'], namespace=manifest['final_namespace'],
                    example=example['name'], seed=summary['seed'], task=config['task'], cap=config['cap'], input_channels_excluded_from_RMS=channels,
                    nearest_edit_Chebyshev_distance=nearest, query_truth=truth.tolist(),
                    depths=depths.tolist(), query_predictions=predictions.tolist(),
                    query_mutable_RMS_difference=response.astype(float).tolist(),
                    maximum_mutable_RMS_difference=delta.max(axis=(1, 2)).astype(float).tolist(),
                    first_illustrated_nonzero_step=int(depths[positive[0]]) if len(positive) else None,
                    last_pair_both_correct=bool(np.all(predictions[-1] == truth))))
    write_json(ROOT / 'results/cloud/research/animation_response_audit.json', dict(records=records,
        scope='Single prespecified draw0 pair per seed and task;sampled steps;illustration,not a cohort-level causal attribution'))
    print(f'{len(records)} predetermined paired animations measured', flush=True)


if __name__ == '__main__':
    main()
