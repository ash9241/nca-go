"""Cell-to-edge stratification of already opened checkpoint tests."""
from collections import defaultdict
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import ROOT, write_json
from .checkpoint_audit import matrix_metrics, matrix_blocks


def main():
    report = json.loads((ROOT / 'reports/GPU_RESULTS.json').read_text())
    matrices = defaultdict(lambda: np.zeros((4, 4), np.int64))
    names = ('0', '1', '2', '3–4', '5–8', '9–16', '17+')
    for family in report['final_evaluations']:
        source = ROOT / 'results/final_liberties' / family['run']
        for path in sorted((source / 'data').glob('test_*.npz')):
            generator, size = path.stem.split('_')[1:]; size = int(size)
            if size not in (13, 19, 25, 37):
                continue
            with np.load(path) as data:
                labels = data['labels']
            rr, cc = np.indices((size, size))
            distance = np.minimum.reduce((rr, cc, size-1-rr, size-1-cc))
            bucket = np.digitize(distance, [0, 1, 2, 4, 8, 16], right=True)
            for prediction_file in sorted((source / 'eval').glob(f'*_{generator}_{size}_d*_t*.npz')):
                depth = int(prediction_file.stem.split('_d')[1].split('_')[0])
                with np.load(prediction_file) as saved:
                    prediction = saved['predictions']
                for index, name in enumerate(names):
                    mask = (labels >= 0) & (bucket == index)
                    if mask.any():
                        matrices[(family['label'], size, depth, name)] += np.bincount(4*labels[mask]+prediction[mask], minlength=16).reshape(4, 4)
    rows = [dict(recipe=key[0], size=key[1], depth=key[2], query_edge_distance=key[3], **matrix_metrics(value)) for key, value in sorted(matrices.items())]
    out = ROOT / 'reports/checkpoint_audit'
    write_json(out / 'query_edge_stratification.json', dict(scope='Already opened old tests;descriptive,not causal;distance of each predicted stone to the board edge', records=rows))
    lines = ['# Query-cell distance to the edge', '', 'This complements the existing nearest-chain-edge audit. Rows are correlated stone-trials, not independent observations. Macro accuracy conditions only on true liberty class; chain diameter and generator remain potential confounders.', '']
    for row in rows:
        lines += [f"## {row['recipe']} / {row['size']}×{row['size']} / D{row['depth']} / edge distance {row['query_edge_distance']}", '',
                  f"Stone accuracy {100*row['accuracy']:.2f}%; macro {100*row['macro_accuracy']:.2f}%; overcounts {row['overcounts']}; undercounts {row['undercounts']}.", ''] + matrix_blocks(np.asarray(row['confusion']))
    (out / 'QUERY_EDGE.md').write_text('\n'.join(lines)+'\n')
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout='constrained')
    for size in (13, 19, 25, 37):
        selected = [row for row in rows if row['recipe'] == 'Asynchronous' and row['size'] == size and row['depth'] == 32]
        selected.sort(key=lambda row: names.index(row['query_edge_distance']))
        for ax, field in zip(axes, ('accuracy', 'macro_accuracy')):
            ax.plot([names.index(row['query_edge_distance']) for row in selected], [100*row[field] for row in selected], 'o-', label=f'{size}×{size}')
    for ax, title in zip(axes, ('Stone accuracy', 'Macro accuracy across supported classes')):
        ax.set(title=title, xlabel='Query stone distance to the edge', ylabel='Accuracy (%)', ylim=(0, 102), xticks=range(len(names)), xticklabels=names)
        ax.spines[['top', 'right']].set_visible(False)
    axes[1].legend(); fig.suptitle('Old asynchronous checkpoint, D32; already opened tests; descriptive strata', fontsize=10)
    fig.savefig(out / 'query_edge_accuracy.png', dpi=170); plt.close(fig)
    print(out / 'QUERY_EDGE.md', flush=True)


if __name__ == '__main__':
    main()
