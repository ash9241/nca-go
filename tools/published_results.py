"""Regenerate the README tables and figures from the published measurements."""
from pathlib import Path
import json
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/figures'
LABELS = {('nca', 32): 'NCA + IDs', ('nca', 0): 'NCA, zero IDs',
          ('resnet', 32): 'ResNet + IDs', ('rcnn', 32): 'Recurrent CNN + IDs',
          ('gnn_sum', 32): 'Stone GNN, sum + IDs', ('gnn_max', 32): 'Stone GNN, max + IDs'}
ORDER = list(LABELS)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    namespaces = json.loads((ROOT / 'reports/research_followup/outcome_summary.json').read_text())['completed_namespaces']
    main_cohort = next(n for n in namespaces if n['namespace'] == 'sealed_main_cap4_20261007')
    lookup = {(r['model'], r['identifiers']): r for r in main_cohort['cohorts']}
    cohorts = [lookup[k] for k in ORDER]
    # Assert aggregates are the arithmetic mean of training-seed results.
    for ns in namespaces:
        for row in ns['cohorts']:
            for metric in ('macro', 'witness_both', 'cycle_both'):
                assert np.isclose(row[metric]['mean'], np.mean([s[metric] for s in row['per_seed']]), atol=1e-12)
    table = ['| Model | Macro accuracy | Witness pairs both correct | Cycle controls both correct |',
             '|---|---:|---:|---:|']
    for k, r in zip(ORDER, cohorts):
        table.append(f"| {LABELS[k]} | {100*r['macro']['mean']:.2f} | {100*r['witness_both']['mean']:.3f} | {100*r['cycle_both']['mean']:.2f} |")
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.titleweight': 'bold', 'figure.facecolor': 'white'})
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.1), layout='constrained', sharey=True)
    y = np.arange(len(cohorts))
    colors = ['#157f88', '#84b7b8', '#666b8c', '#8e779e', '#cc8958', '#b6a080']
    for ax, metric, title in zip(axes, ['macro','witness_both'], ['Whole-board class-macro accuracy', 'Distant-edit pairs: both answers correct']):
        mean = np.array([100*r[metric]['mean'] for r in cohorts])
        lo = np.array([100*r[metric]['minimum'] for r in cohorts]); hi = np.array([100*r[metric]['maximum'] for r in cohorts])
        ax.barh(y, mean, color=colors, height=.56)
        ax.errorbar(mean, y, xerr=[mean-lo, hi-mean], fmt='none', ecolor='#273444', capsize=3, lw=1)
        for yi, val, h in zip(y,mean,hi): ax.text(h+1.2,yi,f'{val:.2f}%',va='center',fontsize=10)
        ax.set(xlim=(0,113), xticks=[0,25,50,75,100], xlabel='Accuracy (%)', title=title)
        ax.xaxis.grid(True,alpha=.15); ax.set_axisbelow(True)
    axes[0].set_yticks(y,[LABELS[k] for k in ORDER]);axes[0].invert_yaxis()
    axes[1].axvline(100,color='#263a41',linestyle='--',linewidth=1)
    axes[1].text(98,5.55,'100% exact reference*',ha='right',fontsize=9)
    fig.suptitle('Stable local rules still fail larger-board counting',fontsize=17)
    fig.savefig(OUT/'model_comparison.png',dpi=180);plt.close(fig)
    qual = json.loads((ROOT/'results/published/main_qualification.json').read_text())['runs']
    depths=[128,512,1024]; vals=np.array([[100*r['assessment']['nine_accuracy'][str(d)] for d in depths] for r in qual])
    fig,ax=plt.subplots(figsize=(9,3.8),layout='constrained')
    for i,row in enumerate(vals): ax.plot(depths,row,'o-',alpha=.65,label=f'Training seed {qual[i]["seed"]}')
    ax.plot(depths,vals.mean(0),'o--',color='#182f3a',lw=2,label='Mean across seeds')
    ax.set(xlabel='Rollout steps',ylabel='Stone accuracy (%)',ylim=(98.9,100),xticks=depths,
           title='9×9 validation accuracy survives 8× rollout depth')
    ax.grid(alpha=.15);ax.legend(loc='lower right',ncol=2,fontsize=9)
    for d,v in zip(depths,vals.mean(0)):ax.annotate(f'{v:.3f}%',(d,v),xytext=(0,12),textcoords='offset points',ha='center',fontsize=10)
    fig.savefig(OUT/'stability.png',dpi=180);plt.close(fig)
    maze=json.loads((ROOT/'reports/maze_positive_control/RESULTS.json').read_text())['results']
    mt=['| Training seed / updates | 9×9 exact, all three depths | 59×59 exact | 201×201 exact |', '|---|---:|---:|---:|']
    for run in dict.fromkeys(x['run'] for x in maze):
        rows=[x for x in maze if x['run']==run];r=rows[0]
        a=[100*np.mean([x['exact_path_accuracy'] for x in rows if x['size']==s]) for s in [59,201]]
        mt.append(f"| Seed {r['training_seed']} / {r['updates']:,}"+(' (continuation)' if r['updates']==10000 else '')+f" | 100% | {a[0]:.2f}% | {a[1]:.2f}% |")
    rt=['| Task | Macro accuracy | Outcome-changing pairs both correct | Cycle controls both correct |','|---|---:|---:|---:|']
    names={'sealed_lib16_20261007':'Liberties 1–15 / 16+', 'sealed_eyes_20261007':'Simple eyes 0–7 / 8+', 'sealed_race_20261007':'Finite first-capture race'}
    for namespace,label in names.items():
        r=next(n for n in namespaces if n['namespace']==namespace)['cohorts'][0]
        rt.append(f"| {label} | {100*r['macro']['mean']:.2f}% | {100*r['witness_both']['mean']:.3f}% | {100*r['cycle_both']['mean']:.2f}% |")
    readme=ROOT/'README.md';text=readme.read_text()
    for marker,rows in [('main',table),('maze',mt),('richer',rt)]:
        text=re.sub(f'<!-- {marker}-table:start -->.*?<!-- {marker}-table:end -->',
                    f'<!-- {marker}-table:start -->\n'+ '\n'.join(rows)+f'\n<!-- {marker}-table:end -->',text,flags=re.S)
    readme.write_text(text)
    print('Regenerated three tables and two figures; aggregate seed means verified.')
if __name__=='__main__':main()
