"""Separate paired-member accuracy from saved final predictions; no retraining."""
import csv
from hashlib import sha256
import json
import numpy as np
from .common import ROOT, write_json
from .checkpoint_audit import chain_features


def main():
    records, cache = [], {}
    for path in sorted((ROOT / 'results/research_evaluation').glob('*/summary.json')):
        summary = json.loads(path.read_text())
        if summary['status'] != 'complete':
            continue
        import yaml
        config = yaml.safe_load((path.parent / 'config.yaml').read_text())
        namespace = config['namespace']
        data_root = ROOT / 'results/research_final_data' / namespace
        manifest = json.loads((data_root / 'manifest.json').read_text())
        classes = summary['model_config']['classes']
        for row in summary['paired']:
            kind, size = row['kind'], row['size']
            key = namespace, kind, size
            if key not in cache:
                file = data_root / f'{kind}_{size}.npz'
                expected = next(r['sha256'] for r in manifest['files'] if r['name'] == file.name)
                assert sha256(file.read_bytes()).hexdigest() == expected
                with np.load(file) as data:
                    data = {name: data[name] for name in data.files}
                plain = np.where(data['boards'] >= 4, np.where(data['boards'] % 2 == 0, 1, 2), data['boards'])
                cycles = np.asarray([int(chain_features(board)[tuple(query)][2]) for board, query in zip(plain, data['queries'])])
                cache[key] = data, cycles
            data, cycles = cache[key]
            mask = data['geometries'] == row['geometry'] if 'geometries' in data else np.ones(len(data['labels']), bool)
            ratio = row.get('ratio')
            name = f"{kind}_{size}_ratio{ratio}_draw{row['draw']}.npz" if ratio is not None else f"{kind}_{size}_draw{row['draw']}.npz"
            with np.load(path.parent / 'eval' / name) as saved:
                prediction = saved['predictions'] if ratio is not None else saved['predictions'][int(np.flatnonzero(saved['depths'] == row['depth'])[0])]
            selected, target = prediction[mask], data['labels'][mask]
            for member, offset in (('A', 0), ('B', 1)):
                truth, predicted = target[offset::2], selected[offset::2]
                matrix = np.bincount(classes*truth+predicted, minlength=classes**2).reshape(classes, classes)
                records.append(dict(evaluation_run=path.parent.name, source_run=summary['source_run'], namespace=namespace,
                    model=summary['model'], seed=summary['seed'], task=summary['task'], kind=kind, size=size,
                    geometry=row['geometry'], ratio=ratio, depth=row.get('depth'), draw=row['draw'], member=member,
                    pairs=len(truth), accuracy=float((truth == predicted).mean()), query_chain_cycle_fraction=float(cycles[mask][offset::2].mean()),
                    confusion=matrix.tolist(), overcounts=int(np.triu(matrix, 1).sum()) if summary['task'] != 'race' else None,
                    undercounts=int(np.tril(matrix, -1).sum()) if summary['task'] != 'race' else None))
    out = ROOT / 'reports/research_followup'
    write_json(out / 'pair_members.json', dict(scope='Saved final predictions only;A and B are paired members,not independent observations', records=records))
    if records:
        with (out / 'pair_members.csv').open('w', newline='') as stream:
            fields = [key for key in records[0] if key != 'confusion']
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore'); writer.writeheader(); writer.writerows(records)
    print(out / 'pair_members.json', flush=True)


if __name__ == '__main__':
    main()
