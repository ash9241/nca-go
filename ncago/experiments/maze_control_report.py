"""Build the local, evidence-linked positive-control report and animations."""
from hashlib import sha256
import html
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
from .common import ROOT, write_json
from .maze_control import maze_metrics


RUNS=["20261007T104409022623Z_ee2e3824_s0", "20261007T105026177670Z_31d139e7_s1",
      "20261007T105355765423Z_9d260402_s2", "20261007T105829309282Z_105065db_s0"]


def animate(source,destination):
    with np.load(source) as d:
        tokens,labels,scores,steps=d["tokens"],d["labels"],d["scores"],d["steps"]
        final=d["predictions"]
    predictions=np.argmax(scores,-1)
    predictions[:,tokens==2]=0;predictions[:,tokens==3]=1
    if not np.array_equal(predictions[-1],final):
        raise AssertionError("Recorded scores disagree with measured final prediction")
    scale=max(2,450//len(tokens));side=len(tokens)*scale
    font=ImageFont.truetype(matplotlib.font_manager.findfont("DejaVu Sans"),16)
    colors=dict(wall=[31,41,55],empty=[244,247,251],path=[43,129,214],end=[247,190,61],
                false=[241,112,34],miss=[194,46,98])
    def board_image(pred,reference=False):
        rgb=np.empty(tokens.shape+(3,),np.uint8);rgb[:]=colors["empty"]
        rgb[tokens==2]=colors["wall"]
        rgb[pred==1]=colors["path"]
        if not reference:
            rgb[(pred==1)&(labels==0)]=colors["false"]
            rgb[(pred==0)&(labels==1)]=colors["miss"]
        rgb[tokens==3]=colors["end"]
        return Image.fromarray(rgb).resize((side,side),Image.Resampling.NEAREST)
    reference=board_image(labels,True)
    frames=[]
    for step,pred in zip(steps,predictions):
        frame=Image.new("RGB",(side*2+48,side+112),"white")
        draw=ImageDraw.Draw(frame)
        draw.text((16,8),"Ground truth",font=font,fill="#172033")
        draw.text((side+32,8),f"Learned NCA · step {step:,}",font=font,fill="#172033")
        frame.paste(reference,(16,38));frame.paste(board_image(pred),(side+32,38))
        errors=int((pred!=labels).sum())
        draw.text((16,side+48),f"{len(tokens)}×{len(tokens)} · {errors:,} wrong cells",font=font,fill="#172033")
        draw.text((16,side+74),"Blue: path   Gold: endpoint   Orange: extra path   Pink: missed path",font=font,fill="#172033")
        frames.append(np.asarray(frame))
    imageio.mimsave(destination,frames,duration=140,loop=0)
    Image.fromarray(frames[-1]).save(destination.with_suffix(".png"))
    return dict(file=destination.name,raw_file=str(source.relative_to(ROOT)),frames=len(frames),
                final_errors=int((final!=labels).sum()),sha256=sha256(source.read_bytes()).hexdigest())


def main():
    out=ROOT/"reports/maze_positive_control"
    out.mkdir(parents=True,exist_ok=True)
    records=[];checks=[];media=[]
    for name in RUNS:
        run=ROOT/"results/maze_control"/name
        import yaml
        config=yaml.safe_load((run/"config.yaml").read_text())
        gate=json.loads((run/"positive_control_gate.json").read_text())
        checks.append(dict(run=name,passed=gate["positive_control_passed"],
                           checkpoint_sha256=gate["checkpoint_sha256"],
                           source_snapshot_sha256=sha256((run/"maze_control_source.py").read_bytes()).hexdigest()))
        if checks[-1]["source_snapshot_sha256"]!=config["source_sha256"]:
            raise AssertionError("Training source snapshot hash mismatch")
        if sha256((run/"ckpt/final.msgpack").read_bytes()).hexdigest()!=gate["checkpoint_sha256"]:
            raise AssertionError("Checkpoint hash mismatch")
        for row in gate["ood"]:
            with np.load(run/f"eval/ood_{row['size']}_s{row['inference_seed']}.npz") as d:
                rescored=maze_metrics(d["predictions"],d["labels"],d["tokens"])
            for k,v in rescored.items():
                if row[k]!=v:raise AssertionError((name,k,row[k],v))
            records.append(dict(run=name,training_seed=config["seed"],updates=config["training_steps"],
                                phase="confirmation after extra training" if config.get("continuation_from") else "published recipe",
                                **row))
        clean=json.loads((run/"qualification_clean.json").read_text())
        for row in clean["qualification"]:
            with np.load(run/f"eval/clean_9_d{row['depth']}.npz") as d:
                rescored=maze_metrics(d["predictions"],d["labels"],d["tokens"])
            for k,v in rescored.items():
                if row[k]!=v:raise AssertionError((name,k))
    for size,index in ((59,0),(201,7),(201,2)):
        source=ROOT/"results/maze_control"/RUNS[0]/f"eval/animation_{size}_i{index}.npz"
        destination=out/f"maze_{size}_i{index}.gif"
        if source.exists():
            result=animate(source,destination)
            with np.load(source) as d:pred=d["predictions"]
            with np.load(source.parent/f"ood_{size}_s20001.npz") as d:
                if not np.array_equal(pred,d["predictions"][index]):
                    raise AssertionError("Animation does not match original OOD evaluation")
            media.append(result)
    write_json(out/"RESULTS.json",dict(results=records,checkpoint_and_source_audit=checks,
               positive_control_passed=all(c["passed"] for c in checks[:3]),
               any_control_passed=any(c["passed"] for c in checks),media=media,
               downstream_status="Go task ladder, influence experiments, sparse IDs and richer tasks held per positive-control gate"))
    import csv
    with (out/"accuracy.csv").open("w") as f:
        writer=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in records for k in row)))
        writer.writeheader();writer.writerows(records)
    fig,ax=plt.subplots(figsize=(9,4.6))
    for i,name in enumerate(RUNS):
        rows=[r for r in records if r["run"]==name]
        ys=[[r["exact_path_accuracy"]*100 for r in rows if r["size"]==s] for s in (59,201)]
        xs=np.array([0,1])+(i-1.5)*.06
        line,=ax.plot(xs,[np.mean(y) for y in ys],"o-",label=(f"5k updates · seed {i}" if i<3 else "10k updates · seed 0 · new subsets"))
        ax.errorbar(xs,[np.mean(y) for y in ys],yerr=np.array([[np.mean(y)-min(y) for y in ys],[max(y)-np.mean(y) for y in ys]]),fmt="none",capsize=3,ecolor=line.get_color())
    ax.axhline(100,color="#374151",ls=":",label="Hand-coded local reference (100%)")
    ax.axhline(95,color="#b91c1c",ls="--",label="Prespecified control gate (95%)")
    ax.set_xticks([0,1],["59×59 · D=2,000","201×201 · D=13,000"])
    ax.set_ylim(-3,104);ax.set_ylabel("Exact path solves (%)")
    ax.legend(fontsize=8,loc="lower left");ax.grid(alpha=.15)
    fig.tight_layout();fig.savefig(out/"maze_extrapolation.png",dpi=180);plt.close(fig)
    depth=json.loads((ROOT/"results/maze_control"/RUNS[0]/"depth_audit_201.json").read_text())
    fig,ax=plt.subplots(figsize=(8,3.6))
    ax.plot([r["depth"] for r in depth["results"]],[100*r["exact_path_accuracy"] for r in depth["results"]],"o-",label="Seed0 · first16 opened mazes (diagnostic)")
    ax.axhline(100,color="#374151",ls=":",label="Hand-coded local reference")
    ax.set_xscale("log",base=2);ax.set_ylim(0,105);ax.set_xlabel("Rollout steps");ax.set_ylabel("Exact path solves (%)")
    ax.legend(fontsize=8);ax.grid(alpha=.15);fig.tight_layout();fig.savefig(out/"depth_diagnostic.png",dpi=180);plt.close(fig)
    table=[]
    for i,name in enumerate(RUNS):
        rows=[r for r in records if r["run"]==name]
        values=[]
        for size in (59,201):
            ys=[100*r["exact_path_accuracy"] for r in rows if r["size"]==size]
            values.append(f"{np.mean(ys):.2f}% ({min(ys):.2f}–{max(ys):.2f})")
        table.append(f"<tr><td>{'5,000 · seed '+str(i) if i<3 else '10,000 · seed0 continuation'}</td><td>100%</td><td>{values[0]}</td><td>{values[1]}</td><td>{'PASS' if checks[i]['passed'] else 'FAIL'}</td></tr>")
    media_html="".join(f'<figure><img loading="lazy" src="{html.escape(m["file"])}"><figcaption>{m["file"]}: {m["final_errors"]:,} final wrong cells. ' + ('First official 59×59 board; successful.' if '59_' in m['file'] else 'Selected failure example; not an estimate of frequency.') + '</figcaption></figure>' for m in media)
    passed=any(c["passed"] for c in checks)
    verdict="A control passed; downstream gates still apply." if passed else "The positive control failed. Downstream Go work remains held as requested."
    body=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NCA maze positive control</title><style>body{{font:17px/1.6 system-ui,sans-serif;color:#172033;max-width:1050px;margin:40px auto;padding:0 22px;background:#fafbfe}}h1{{font-size:38px;line-height:1.15}}h2{{font-size:23px}}.verdict{{padding:18px;background:#fff0ee;border-left:5px solid #d24f3f}}table{{border-collapse:collapse;width:100%;font-size:15px}}td,th{{border-bottom:1px solid #d6dce7;text-align:left;padding:12px}}.scroll{{overflow-x:auto}}img{{max-width:100%;height:auto}}figure{{margin:26px 0}}figcaption{{font-size:14px;color:#566174}}a{{color:#1765af}}code{{font-size:14px}}.small{{font-size:14px}}</style>
<h1>Does our recurrent pipeline extrapolate on mazes?</h1><p class="verdict"><strong>{verdict}</strong> Small-maze success and high cell accuracy do not establish reliable long-range reasoning.</p>
<p>We implemented a paper-based reproduction of <a href="https://arxiv.org/html/2609.36126v1">Reasoning with Neural Cellular Automata</a>, trained only on 9×9 mazes. This is our implementation of the stated recipe, not a run of the authors’ source.</p>
<h2>Measured results</h2><p>Each large-maze entry shows the mean and range of three inference seeds with one rollout per maze. The three 5k runs use the same 256 mazes at59×59 and64 at201×201. The10k continuation uses different subsets, so its change is not a paired causal estimate of extra training. All four models solve every one of512 D4-disjoint small qualification mazes at100,400 and800 steps.</p>
<div class="scroll"><table><thead><tr><th>Training</th><th>Clean9×9</th><th>59×59 · D2000</th><th>201×201 · D13000</th><th>Gate</th></tr></thead><tbody>{''.join(table)}</tbody></table></div>
<figure><img src="maze_extrapolation.png"><figcaption>Range bars show inference randomness, not confidence intervals. Shared subsets make the5k seeds comparable. The repair is a separate confirmation experiment.</figcaption></figure>
<h2>Why the gate failed</h2><p>The best5k seed solves roughly98% of59×59 mazes but about48% at201×201. On its first201×201 trial,35 of64 mazes fail.34 failures have only extra path cells; one failure misses4,301 true path cells. Even99.6% mutable-cell accuracy hides these broken paths.</p>
<p>Extra rollout time did not repair the opened diagnostic subset: exact solves were50%,43.75%,50% at13k,26k,52k steps. First-quarter state noiseσ0.15 reduced that subset’s solve rate to31.25%. These diagnostics reuse opened boards and are not fresh final tests.</p>
<figure><img src="depth_diagnostic.png"><figcaption>More time does not reliably fix this learned rule.</figcaption></figure>
<p>An independent hand-coded local leaf-pruning automaton solves every checked control maze. Its maximum synchronous rounds are44 at9×9,1,118 at59×59 and8,106 at201×201. This establishes a local algorithmic ceiling on this tree-maze domain, not a learned success. The learned model uses stochastic updates, so reference rounds are not identical to its iteration count.</p>
<h2>Rollouts: a success and two failures</h2><p>These animations use the checkpoint, batch shape and random stream of the scored evaluation. Their final predictions are checked against saved raw results. Blue is path, orange extra path, pink missed path, gold a fixed endpoint.</p>{media_html}
<h2>Data and implementation checks</h2><p>The public benchmark stores2×2 pixel blocks and a three-pixel border. We verify the blocks before downsampling and check every imported label with independent four-neighbor BFS:50,000 training9×9,10,000 test9×9,10,000 test59×59 and1,000 test201×201 mazes.401 public test9 boards overlap training after D4 symmetry, so qualification excludes those and repeated canonical test boards.</p>
<p>The control uses16 channels,4 learned convolution heads, a32-unit ReLU update, wall padding, fixed walls/endpoints, Gaussian initialization and80% firing. Training uses5k AdamW updates, batch64, zero weight decay, learning rate0.0004, all-step MSE over100 steps, replay, damage, noise, target swaps, D4 augmentation and EMA0.999. Parameter count is11,888; the paper displays10K. Zero final-layer initialization and identity-basis token embeddings are explicit choices where the prose does not specify every implementation detail.</p>
<p>The extra5k updates restore optimizer, EMA, replay, JAX key and NumPy RNG. A continuation test matches uninterrupted training byte for byte. Eight focused tests cover conversion, frozen clues, D4 paths, gradients, clean qualification, the local reference and the OOD gates. A separate report audit independently rescored every saved small and OOD prediction and verified checkpoint/source hashes.</p>
<h2>What this means for Go</h2><p>This is useful but incomplete extrapolation. It does not reproduce the NCA paper’s reported100% largest-maze score. It also does not establish a distinct-counting failure or prove that the JAX engine is broken. Our current recipe can learn a broadly useful local rule, but its reliability changes with size and seed. A successful control is needed before attributing Go’s failures to distinctness, cycles or shortcuts.</p>
<p>The requested chain ladder, checkpoint influence measurement, sparse256-bucket IDs, ID consistency, wider Go training and richer-task experiments have not run in this stage. The frozen protocol keeps them behind the maze gate and keeps race/eyes paused until cap4 extrapolates; future race experiments require at least five training seeds. Collision-only undercounting applies to the exact bucket-union reference. A learned maximum across eight ID draws has no such guarantee.</p>
<p class="small"><a href="RESULTS.json">All measured results and hashes</a> · <a href="accuracy.csv">Accuracy CSV</a> · code: <code>ncago/experiments/maze_control.py</code> · protocol: <code>configs/next_counting_protocol.json</code></p></html>'''
    # Restore prose spacing without changing source paths or HTML attributes.
    from html.parser import HTMLParser
    class ProseSpace(HTMLParser):
        def __init__(self):super().__init__(convert_charrefs=False);self.parts=[];self.raw=False
        def handle_starttag(self,tag,attrs):
            self.parts.append(self.get_starttag_text())
            if tag in ("style","code"):self.raw=True
        def handle_endtag(self,tag):
            self.parts.append(f"</{tag}>")
            if tag in ("style","code"):self.raw=False
        def handle_decl(self,decl):self.parts.append(f"<!{decl}>")
        def handle_entityref(self,name):self.parts.append(f"&{name};")
        def handle_charref(self,name):self.parts.append(f"&#{name};")
        def handle_data(self,data):
            import re
            if not self.raw and not data.startswith("maze_"):
                data=re.sub(r"(?<=[A-Za-zσ])(?=\d)"," ",data)
                data=re.sub(r"([A-Za-z%])[,.](?=\d)",lambda m:m.group(0)+" ",data)
            self.parts.append(data)
    formatted=ProseSpace();formatted.feed(body)
    (out/"REPORT.html").write_text("".join(formatted.parts))
    print(out/"REPORT.html")


if __name__=="__main__":main()
