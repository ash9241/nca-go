"""Make a factual social figure only after the sealed primary tests finish."""
import argparse
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import ROOT, write_json
from .research_train import stability_assessment


def mean(rows, field):
    if not rows:
        raise RuntimeError('Missing required final measurements')
    return float(np.mean([row[field] for row in rows]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--namespace', required=True)
    args = parser.parse_args()
    out = ROOT / 'reports/research_followup'
    manifest = json.loads((ROOT / 'results/research_final_data' / args.namespace / 'manifest.json').read_text())
    if manifest['task'] != 'liberties' or manifest['cap'] != 4:
        raise ValueError('Use the prespecified main cap4 namespace')
    result = json.loads((out / 'RESULTS.json').read_text())
    by_source = {row['source_run']: row for row in result['final_evaluations'] if row['status'] == 'complete'
                 and row['namespace'] == args.namespace and row.get('task', 'liberties') == 'liberties' and row.get('cap', 4) == 4}
    primary_names = [row['run'] for row in manifest['source_checkpoints'] if row.get('primary')]
    primary = [by_source[name] for name in primary_names]
    if len({row['seed'] for row in primary}) != 3:
        raise RuntimeError('Three completed independent primary seeds required')
    training = {row['run']: row for row in result['training']}
    qualified = [stability_assessment(training[name]['summary']['results']) for name in primary_names]
    if not all(row['stability_gate'] for row in qualified):
        raise RuntimeError('The primary depth-stability gate did not pass')
    points = []
    for size in (9, 13, 19, 25, 37):
        macro = [mean([row for row in run['records'] if row['size'] == size and row['ratio'] == 4], 'macro_accuracy') for run in primary]
        stone = [mean([row for row in run['records'] if row['size'] == size and row['ratio'] == 4], 'stone_accuracy') for run in primary]
        pair = [mean([row for row in run['paired'] if row['kind'] == 'witness' and row['size'] == size and row.get('ratio') == 4], 'pair_both_correct') for run in primary]
        points.append(dict(size=size, macro_per_seed=macro, stone_per_seed=stone, pair_both_correct_per_seed=pair))
    large = points[-1]
    macro37 = 100*np.mean(large['macro_per_seed']); pair37 = 100*np.mean(large['pair_both_correct_per_seed'])
    strong = macro37 >= 95 and min(large['pair_both_correct_per_seed']) >= .9
    headline = 'Stable local counting passes these size-transfer tests' if strong else 'Stable rollouts do not guarantee systematic counting'
    fig, axes = plt.subplots(1, 3, figsize=(12, 6.75), dpi=150)
    fig.patch.set_facecolor('#f5f7fa')
    sizes = [row['size'] for row in points]
    for ax, field, title, color in zip(axes[:2], ('macro_per_seed', 'pair_both_correct_per_seed'),
                                      ('Unseen boards: macro accuracy', 'Witness pairs: both correct'), ('#246e9d', '#c16f20')):
        values = np.asarray([row[field] for row in points])*100
        ax.plot(sizes, values.mean(1), 'o-', color=color, lw=2)
        ax.fill_between(sizes, values.min(1), values.max(1), color=color, alpha=.17)
        ax.set(title=title, xlabel='Board width', ylabel='Percent', ylim=(-2, 102), xticks=sizes)
    values = np.asarray([[100*row['nine_accuracy'][d] for d in (128, 512, 1024)] for row in qualified])
    axes[2].plot([128, 512, 1024], values.mean(0), 'o-', color='#246e9d', lw=2)
    axes[2].fill_between([128, 512, 1024], values.min(0), values.max(0), color='#246e9d', alpha=.17)
    axes[2].set(title='9×9 validation: longer rollouts', xlabel='Update steps', ylabel='Stone accuracy (%)',
                ylim=(max(0, values.min()-.5), 100.1), xticks=[128, 512, 1024])
    for ax in axes:
        ax.set_facecolor('white'); ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.15); ax.set_title(ax.get_title(), fontsize=11, pad=14)
    fig.suptitle(headline, fontsize=20, fontweight='bold', x=.06, ha='left', y=.92)
    fig.text(.06, .83, f'37×37: {macro37:.1f}% macro accuracy · {pair37:.1f}% witness pairs both correct', fontsize=13)
    fig.text(.06, .17, 'Training: sizes 5–9 · 32 frozen random-ID channels · 3 independent training seeds', fontsize=11)
    fig.text(.06, .12, 'D=4×diameter: maximum chain for boards; queried chain for witness pairs.', fontsize=10)
    fig.text(.06, .075, '8 fresh ID fields per seed. Shading: training-seed range. Synthetic counting tests.', fontsize=9)
    fig.text(.06, .035, 'Fresh training chunks: 32–128 steps. Replay may carry older states.', fontsize=9)
    fig.subplots_adjust(left=.07, right=.97, bottom=.30, top=.70, wspace=.40)
    fig.savefig(out / 'TWITTER_RESULTS.png', facecolor=fig.get_facecolor()); plt.close(fig)
    text = (f'We trained a local recurrent network to count Go liberties on boards of size 5–9. '
            f'On 9×9, three seeds stayed stable to 1,024 steps. On 37×37: {macro37:.1f}% macro accuracy; '
            f'{pair37:.1f}% of difficult witness pairs both correct. '+
            ('A promising synthetic counting result.' if strong else 'Stable dynamics still leave counting failures.'))
    assert len(text) <= 280
    posts = [text]
    overview = json.loads((out / 'outcome_summary.json').read_text())
    richer = {}
    for namespace in overview['completed_namespaces']:
        if namespace['task'] == 'liberties' and namespace['cap'] == 4:
            continue
        cohort = next(row for row in namespace['cohorts'] if row['model'] == 'nca' and row['identifiers'] == 32)
        richer[(namespace['task'], namespace['cap'])] = (100*cohort['macro']['mean'], 100*cohort['witness_both']['mean'])
    if all(key in richer for key in (('liberties', 16), ('eyes', 9), ('race', 3))):
        lib, eye, race = [richer[key] for key in (('liberties', 16), ('eyes', 9), ('race', 3))]
        second = (f'Harder tests (macro accuracy / pairs both correct): liberties1–16+ {lib[0]:.1f}% / {lib[1]:.1f}%; '
                  f'static eyes {eye[0]:.1f}% / {eye[1]:.1f}%; first capture {race[0]:.1f}% / {race[1]:.1f}%. '
                  'Means over3 seeds. Race boards are5×37; their paired witnesses are37×37.')
        second = second.replace('liberties1', 'liberties 1').replace('over3', 'over 3').replace('are5', 'are 5').replace('are37', 'are 37')
        assert len(second) <= 280
        posts.append(second)
    draft = ['# Unpublished Twitter draft', '', '## Post 1', '', text, '']
    if len(posts) > 1:
        draft += ['## Post 2', '', posts[1], '']
    draft += [
             'The main liberty witness changes one distant stone and asks whether both answers are correct. The race witness uses two edits. Random IDs carry no labels and are renewed for each fresh trajectory and test. Matched baseline witness comparisons also use three independent training seeds.', '',
             'Attach TWITTER_RESULTS.png and a predetermined learned-rollout MP4. Link the offline report after choosing a public hosting location. This draft has not been posted.', '']
    (out / 'TWITTER_DRAFT.md').write_text('\n'.join(draft))
    write_json(out / 'social_figure_measurements.json', dict(namespace=args.namespace, headline=headline,
        primary_source_runs=primary_names, ratio=4, training_seed_range_not_confidence_interval=True,
        points=points, qualification=qualified, character_count=len(text), posts=posts,
        post_character_counts=[len(post) for post in posts], published=False))
    print(out / 'TWITTER_RESULTS.png', flush=True)


if __name__ == '__main__':
    main()
