"""Fixed cheap race heuristics, chosen on validation before final tests."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .common import ROOT, write_json
from .research_train import metrics
from ncago.go.rules import group
from ncago.go.research_tasks import simple_eye_counts


def predictions(boards):
    result = {name: [] for name in ('side_to_move', 'liberty_advantage_then_turn', 'two_simple_eyes_plus_liberty_advantage')}
    for board in boards:
        black = tuple(np.argwhere((board == 4) | (board == 6))[0])
        white = tuple(np.argwhere((board == 5) | (board == 7))[0])
        plain = np.where(board >= 4, np.where(board % 2 == 0, 1, 2), board)
        lb, lw = int(group(plain, *black)[1].sum()), int(group(plain, *white)[1].sum())
        turn = int(np.any(board >= 6))
        count = 0 if lb > lw else 1 if lw > lb else turn
        eyes = simple_eye_counts(plain)
        eye = 2 if eyes[black] >= 2 and eyes[white] >= 2 else count
        for name, value in zip(result, (turn, count, eye)):
            result[name].append(np.full(board.shape, value, np.int32))
    return {name: np.stack(value) for name, value in result.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--namespace', help='Optional sealed race final namespace; default is frozen validation')
    args = p.parse_args()
    if args.namespace:
        root = ROOT / 'results/research_final_data' / args.namespace
        manifest = json.loads((root / 'manifest.json').read_text())
        if manifest['task'] != 'race':
            raise ValueError('Race final namespace required')
        for row in manifest['files']:
            if sha256((root / row['name']).read_bytes()).hexdigest() != row['sha256']:
                raise RuntimeError('Frozen final checksum mismatch')
        sizes, prefix, scope = (9, 13, 19, 25, 37), 'boards_', 'final'
    else:
        c = json.loads((ROOT / 'configs/research_race3.json').read_text())
        root = ROOT / 'results/research_validation' / f"regular_race_cap3_n{c['validation_count']}_s{c['validation_seed']}"
        sizes, prefix, scope = (9, 13), 'val_', 'validation'
    rows, paired = [], []
    for size in sizes:
        with np.load(root / f'{prefix}{size}.npz') as data:
            boards, labels = data['boards'], data['labels']
        for name, prediction in predictions(boards).items():
            rows.append(dict(split=scope, size=size, baseline=name, **metrics(prediction, labels, 3, 'race')))
        if args.namespace:
            for kind in ('race_witness', 'cycle_pairs'):
                with np.load(root / f'{kind}_{size}.npz') as data:
                    boards, queries, targets = data['boards'], data['queries'], data['labels']
                for name, prediction in predictions(boards).items():
                    query_prediction = prediction[np.arange(len(queries)), queries[:, 0], queries[:, 1]]
                    correct = query_prediction == targets
                    matrix = np.bincount(3*targets+query_prediction, minlength=9).reshape(3, 3)
                    paired.append(dict(kind=kind, size=size, baseline=name, pairs=len(targets)//2,
                        pair_both_correct=float(correct.reshape(-1, 2).all(1).mean()),
                        query_accuracy=float(correct.mean()), confusion=matrix.tolist()))
    out = ROOT / 'reports/checkpoint_audit' / f'race_heuristic_{args.namespace or "validation"}.json'
    write_json(out, dict(scope=scope, namespace=args.namespace,
                         rule_selection='fixed on9/13 validation before any new larger final sets',
                         access='Full board with exact group liberties and static simple-eye counts;not a local learned baseline',
                         records=rows, paired=paired))
    print(out, flush=True)


if __name__ == '__main__':
    main()
