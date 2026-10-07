"""Verify the prescribed final cohorts and their locally saved artifacts."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import yaml
from .common import ROOT, write_json


def main():
    cohorts = json.loads((ROOT / 'results/cloud/research/final_cohorts.json').read_text())['cohorts']
    evaluations = defaultdict(list)
    for path in (ROOT / 'results/research_evaluation').glob('*/summary.json'):
        summary = json.loads(path.read_text())
        config = yaml.safe_load((path.parent / 'config.yaml').read_text())
        evaluations[(config['namespace'], summary['source_run'])].append((path.parent, summary))
    records, media_expected = [], 0
    for role, cohort in cohorts.items():
        dataset = ROOT / 'results/research_final_data' / cohort['namespace']
        manifest = json.loads((dataset / 'manifest.json').read_text())
        assert set(cohort['runs']) == {r['run'] for r in manifest['source_checkpoints']}
        assert len(cohort['runs']) == (18 if role == 'main' else 3)
        for row in manifest['files']:
            assert sha256((dataset / row['name']).read_bytes()).hexdigest() == row['sha256']
        streams, groups, files = set(), defaultdict(list), {}
        for source in manifest['source_checkpoints']:
            train = ROOT / 'results/research_training' / source['run']
            summary = json.loads((train / 'summary.json').read_text())
            config = yaml.safe_load((train / 'config.yaml').read_text())
            assert summary['status'] == 'complete'
            assert config['training_steps'] == (30000 if role == 'main' else 20000)
            assert sha256((train / 'ckpt/final.msgpack').read_bytes()).hexdigest() == source['sha256']
            streams.add((summary['stream_sha256'], summary['supervised_stream_sha256']))
            groups[(source['kind'], source['model_config']['identifier_channels'])].append(source['seed'])
            pair = evaluations[(cohort['namespace'], source['run'])]
            assert len(pair) == 1
            run, measured = pair[0]
            evaluation_config = yaml.safe_load((run / 'config.yaml').read_text())
            assert evaluation_config['checkpoint_sha256'] == source['sha256']
            assert measured['status'] == 'complete'
            assert measured['seed'] == source['seed']
            draws = 8 if source['model_config']['identifier_channels'] else 3
            assert len(measured['records']) == 5*4*draws
            for size in (9, 13, 19, 25, 37):
                for ratio in (.5, 1., 2., 4.):
                    rows = [r for r in measured['records'] if r['size'] == size and r['ratio'] == ratio]
                    assert {r['draw'] for r in rows} == set(range(draws))
                    for row in rows:
                        filename = run / 'eval' / f"size{size}_ratio{ratio}_draw{row['draw']}.npz"
                        files[str(filename.relative_to(ROOT))] = sha256(filename.read_bytes()).hexdigest()
            for row in measured['paired']:
                suffix = f"_ratio{row['ratio']}" if 'ratio' in row else ''
                filename = run / 'eval' / f"{row['kind']}_{row['size']}{suffix}_draw{row['draw']}.npz"
                key = str(filename.relative_to(ROOT))
                if key not in files:
                    files[key] = sha256(filename.read_bytes()).hexdigest()
            if source.get('primary'):
                media = ROOT / 'reports/research_followup/media' / source['run']
                illustrated = json.loads((media / 'manifest.json').read_text())
                assert illustrated['checkpoint_sha256'] == source['sha256']
                assert illustrated['final_namespace'] == cohort['namespace']
                assert len(illustrated['examples']) == (2 if role == 'main' else 1)
                for example in illustrated['examples']:
                    for extension in ('gif', 'mp4', 'npz'):
                        file = media / (example['name']+'.'+extension)
                        assert file.stat().st_size > 0
                    media_expected += 1
        assert len(streams) == 1
        assert all(sorted(seeds) == [0, 1, 2] for seeds in groups.values())
        assert len(groups) == (6 if role == 'main' else 1)
        records.append(dict(role=role, namespace=cohort['namespace'], completed_sources=len(cohort['runs']),
                            matched_streams=True, groups={str(k): v for k, v in groups.items()},
                            saved_prediction_files=files))
    assert media_expected == 15
    audited = json.loads((ROOT / 'results/cloud/research/media_prediction_audit.json').read_text())
    assert audited['all_exact'] and audited['examples'] == 15
    gates = json.loads((ROOT / 'results/cloud/research/main_qualification.json').read_text())
    assert gates['primary_gate_passed'] and all(r['qualified'] for r in gates['runs'])
    write_json(ROOT / 'results/cloud/research/completion_audit.json', dict(all_prescribed_cohorts_complete=True,
        completed_final_evaluations=27, learned_animations=15, checkpoint_and_frozen_data_hashes_verified=True,
        media_predictions_match_final_evaluations=True, cohorts=records,
        scope='Artifact and protocol completion;does not assert successful larger-board learning or playing strength'))
    print('27 final evaluations and15 learned animations verified', flush=True)


if __name__ == '__main__':
    main()
