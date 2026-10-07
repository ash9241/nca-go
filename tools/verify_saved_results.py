"""Independently rescore the headline Go/maze measurements from saved arrays.

Run after extracting the Go and maze release assets into the repository root.
This script uses NumPy and JSON only: no neural inference or training.
"""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def exact(a,b):
    assert np.isclose(a,b,atol=1e-12,rtol=0),(a,b)

def main():
    count=0
    overview=json.loads((ROOT/'reports/research_followup/outcome_summary.json').read_text())
    expected={s['source_run']:s for n in overview['completed_namespaces'] for c in n['cohorts'] for s in c['per_seed']}
    for path in sorted((ROOT/'results/research_evaluation').glob('*/summary.json')):
        summary=json.loads(path.read_text());source=summary['source_run']
        if source not in expected:continue
        # Recover the namespace from its frozen source-checkpoint membership.
        candidates=[]
        for data in (ROOT/'results/research_final_data').iterdir():
            m=json.loads((data/'manifest.json').read_text())
            if source in {r['run'] for r in m['source_checkpoints']}:candidates.append(data)
        assert len(candidates)==1
        data=candidates[0]
        with np.load(data/'boards_37.npz') as d: labels=d['labels']
        mask=labels>=0;classes=summary['cap'];macros=[]
        for saved in sorted((path.parent/'eval').glob('size37_ratio4.0_draw*.npz')):
            with np.load(saved) as d: pred=d['predictions']
            assert np.all((pred[mask]>=0)&(pred[mask]<classes))
            cm=np.bincount(classes*labels[mask]+pred[mask],minlength=classes**2).reshape(classes,classes)
            support=cm.sum(1);macro=np.mean(cm.diagonal()[support>0]/support[support>0]);macros.append(macro)
            draw=int(saved.stem.split('draw')[-1]);row=next(r for r in summary['records'] if r['size']==37 and r['ratio']==4 and r['draw']==draw)
            assert np.array_equal(cm,np.array(row['confusion']))
            exact(macro,row['macro_accuracy']);exact(np.trace(cm)/cm.sum(),row['stone_accuracy'])
        assert macros;exact(np.mean(macros),expected[source]['macro'])
        kind={'liberties':'witness','eyes':'eye_witness','race':'race_witness'}[summary['task']]
        with np.load(data/f'{kind}_37.npz') as d: target=d['labels']
        pairs=[]
        for saved in sorted((path.parent/'eval').glob(f'{kind}_37_ratio4.0_draw*.npz')):
            with np.load(saved) as d: pred=d['predictions']
            pairs.append(np.all((pred==target).reshape(-1,2),axis=1).mean())
        assert pairs;exact(np.mean(pairs),expected[source]['witness_both']);count+=1
    assert count==27,f'Expected 27 original final evaluations, found {count}'
    maze=json.loads((ROOT/'reports/maze_positive_control/RESULTS.json').read_text());n=0
    for row in maze['results']:
        f=ROOT/'results/maze_control'/row['run']/f"eval/ood_{row['size']}_s{row['inference_seed']}.npz"
        with np.load(f) as d: prediction,labels=d['predictions'],d['labels']
        score=np.all(prediction==labels,axis=(1,2)).mean()
        exact(score,row['exact_path_accuracy']);n+=1
    assert n==24
    small=0
    for run in maze['checkpoint_and_source_audit']:
        folder=ROOT/'results/maze_control'/run['run']
        for depth in [100,400,800]:
            with np.load(folder/f'eval/clean_9_d{depth}.npz') as d:
                assert len(d['labels'])==512
                exact(np.all(d['predictions']==d['labels'],axis=(1,2)).mean(),1.0)
            small+=1
    print(f'Verified {count} Go headline scores/confusions/pair metrics, {n} maze OOD scores, and {small} clean small-maze evaluations.')
if __name__=='__main__': main()
