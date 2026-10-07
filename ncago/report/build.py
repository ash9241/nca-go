from pathlib import Path
import argparse
import base64
import html
import json
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ncago.experiments.common import ROOT,write_json
from ncago.experiments.metrics import verdict,bootstrap_gap
from ncago.viz.boards import filmstrip,board,CONFIDENCE_CMAP

TASKS = ["liberties","atari","benson","ladder L1","ladder L2","ring-vs-path","policy agreement","ownership"]
SIZES = [9,13,19,25,37]
COLORS = {"nca":"#0072B2","b2":"#D55E00","b3":"#009E73"}
plt.style.use("tableau-colorblind10")
plt.rcParams["svg.hashsalt"] = "ncago"


def completed_runs(profile):
    latest = {}
    other = []
    for source in sorted((ROOT/"results").glob("*/*/summary.json")):
        payload = json.loads(source.read_text())
        if payload.get("status") == "interrupted":
            continue
        if payload.get("status") == "failed":
            other.append((source.parent,payload))
            continue
        configfile = source.parent/"config.yaml"
        import yaml
        config = yaml.safe_load(configfile.read_text())
        if payload.get("phase") == "0":
            other.append((source.parent,payload))
            continue
        if payload.get("profile",config.get("profile")) != profile:
            continue
        if payload.get("seed",0) not in config.get("seeds",[0]):
            continue
        key = payload["phase"],payload.get("seed",0)
        latest[key] = source.parent,payload
    return list(latest.values())+other


def load(profile):
    rows,chainrows,gaps,paths,metadata = [],[],[],[],[]
    runs = completed_runs(profile)
    life_sources = {payload.get("seed",0):path for path,payload in runs if payload.get("phase") == "2" and payload.get("pipeline_passed")}
    for path,payload in runs:
        metadata.append(payload)
        if payload.get("status") == "failed":
            continue
        if payload.get("phase") == "2-reference":
            source = life_sources.get(payload.get("seed",0))
            if source is None or payload.get("source_run") != str(source.relative_to(ROOT)):
                continue
            previous = pd.read_csv(source/"eval"/"boards.csv")
            if (previous.model == "b3").any():
                continue
        file = path/"eval"/"boards.csv"
        if file.exists():
            df = pd.read_csv(file)
            task = {"1":"liberties","2":"benson","2-reference":"benson","3":"ladders"}.get(payload["phase"],payload["phase"])
            df["task"] = task
            if "task_metric" in df:
                df["task"] = df.task_metric.fillna(task)
            df["run"] = str(path.relative_to(ROOT))
            rows.append(df)
        file = path/"eval"/"chains.csv"
        if file.exists():
            df = pd.read_csv(file)
            df["task"] = {"1":"liberties","2":"benson","2-reference":"benson","3":"ladders"}.get(payload["phase"])
            chainrows.append(df)
        file = path/"eval"/"gaps.csv"
        if file.exists():
            gaps.append(pd.read_csv(file))
        pair_file = path/"eval"/"pairs.csv"
        if pair_file.exists():
            pair_rows = pd.read_csv(pair_file)
            pair_rows = pair_rows[pair_rows.task == "liberties"]
            if "task_metric" in pair_rows:
                pair_rows = pair_rows[pair_rows.task_metric.isna()]
            pair_rows["task"] = "ring-vs-path"
            pair_rows["run"] = str(path.relative_to(ROOT))
            rows.append(pair_rows)
        paths.extend(path.glob("viz/*.npz"))
    return (pd.concat(rows,ignore_index=True) if rows else pd.DataFrame(),
            pd.concat(chainrows,ignore_index=True) if chainrows else pd.DataFrame(),
            pd.concat(gaps,ignore_index=True) if gaps else pd.DataFrame(),paths,metadata)


def primary(df):
    if df.empty:
        return df
    result = df.copy()
    for flag in ("sweep","repair"):
        if flag in result:
            result = result[result[flag] != True]
    result = result[result.steps == result.groupby(["task","model","seed","size","generator","board_id"]).steps.transform("max")]
    return result


def aggregate(df):
    if df.empty:
        return pd.DataFrame(columns=["task","model","seed","size","accuracy","ms","flops"])
    grouped = df.groupby(["task","model","seed","size"],as_index=False).agg(
        correct=("stone_correct","sum"),count=("stone_count","sum"),ms=("ms","mean"),flops=("flops","mean"))
    grouped["accuracy"] = grouped.correct/grouped['count'].replace(0,np.nan)
    return grouped


def embed(path):
    path = Path(path)
    mime = "image/gif" if path.suffix == ".gif" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def md_table(df):
    if df.empty:
        return "Not run: no measured rows."
    cols = list(df.columns)
    lines = ["| "+" | ".join(cols)+" |","| "+" | ".join(["---"]*len(cols))+" |"]
    for row in df.itertuples(index=False,name=None):
        lines.append("| "+" | ".join(str(v).replace("|","/") for v in row)+" |")
    return "\n".join(lines)


def build(profile="smoke"):
    reportdir = ROOT/"reports"
    figures = reportdir/"figures"
    figures.mkdir(parents=True,exist_ok=True)
    df,chain_df,gaps,paths,metadata = load(profile)
    p = primary(df)
    ag = aggregate(p)
    grouped = ag.groupby(["task","model","size"],as_index=False).agg(mean=("accuracy","mean"),std=("accuracy","std"),ms=("ms","mean"),flops=("flops","mean")) if len(ag) else pd.DataFrame()
    sections,missing = [],[]
    def figure(key,title,draw=None,caption="",reason=None):
        if reason or draw is None:
            reason = reason or "no measured data"
            missing.append({"figure":key,"reason":reason})
            sections.append(f'<section id="{key}"><h2>{html.escape(title)}</h2><p class="missing">Not run: {html.escape(reason)}</p></section>')
            return
        fig = draw()
        file = figures/f"{key}.png"
        fig.savefig(file,dpi=150,bbox_inches="tight")
        vector = file.with_suffix(".svg")
        fig.savefig(vector,bbox_inches="tight",metadata={"Date":None})
        vector.write_text("\n".join(line.rstrip() for line in vector.read_text().splitlines())+"\n")
        plt.close(fig)
        sections.append(f'<section id="{key}"><h2>{html.escape(title)}</h2><img src="{embed(file)}" alt="{html.escape(title)}"><p>{html.escape(caption)}</p></section>')
    def means(task,model,size):
        if grouped.empty:
            return None
        sel = grouped[(grouped.task == task)&(grouped.model == model)&(grouped['size'] == size)]
        return None if sel.empty or not np.isfinite(sel.iloc[0]['mean']) else float(sel.iloc[0]['mean'])
    best,delta_rows = {},[]
    if not grouped.empty:
        for (task,size),subset in grouped[grouped.model.str.startswith("b1_")].groupby(["task","size"]):
            subset = subset[np.isfinite(subset['mean'])]
            if subset.empty:
                continue
            selected = subset.loc[subset['mean'].idxmax()]
            best[(task,size)] = selected.model
            for nca_seed in ag[(ag.task == task)&(ag.model == "nca")&(ag['size'] == size)].seed.unique():
                part = p[(p.task == task)&(p['size'] == size)&(p.seed == nca_seed)&p.model.isin(["nca",selected.model])]
                pivot = part.pivot(index=["generator","board_id"],columns="model",values="stone_accuracy")
                if "nca" in pivot and selected.model in pivot:
                    weights = part[part.model == "nca"].set_index(["generator","board_id"]).stone_count.reindex(pivot.index)
                    gap,lo,hi = bootstrap_gap(pivot.nca,pivot[selected.model],int(nca_seed),1000 if profile == "smoke" else 10000,weights)
                    delta_rows.append({"task":task,"size":size,"seed":int(nca_seed),"baseline":selected.model,"gap":gap,"ci_low":lo,"ci_high":hi})
    write_json(reportdir/"accuracy_gaps.json",delta_rows)
    def capability():
        values = np.full((len(TASKS),len(SIZES)),np.nan)
        for ti,task in enumerate(TASKS):
            for si,size in enumerate(SIZES):
                value = means(task,"nca",size)
                if value is not None:
                    values[ti,si] = value*100
        fig,ax = plt.subplots(figsize=(10,6))
        cmap = plt.get_cmap("cividis").copy()
        cmap.set_bad("#d9dcdf")
        image = ax.imshow(np.ma.masked_invalid(values),cmap=cmap,vmin=0,vmax=100,aspect="auto")
        ax.set_xticks(range(len(SIZES)),[str(s) for s in SIZES])
        ax.set_yticks(range(len(TASKS)),TASKS)
        ax.set_xlabel("Board width")
        for ti,task in enumerate(TASKS):
            for si,size in enumerate(SIZES):
                value = values[ti,si]
                baseline = means(task,best.get((task,size),""),size)
                label = "not run" if not np.isfinite(value) else f"{value:.1f}%\n"+(f"{value-baseline*100:+.1f} pp" if baseline is not None else "baseline not run")
                ax.text(si,ti,label,ha="center",va="center",fontsize=8,color="black" if not np.isfinite(value) or value > 50 else "white")
        fig.colorbar(image,ax=ax,label="Per-stone accuracy (%)")
        return fig
    figure("F1a","Capability map",capability,caption="Values are measured per-stone accuracy. Deltas compare the best fixed-depth baseline on the same split. Ring-vs-path pools liberty predictions on matched ring/path positions, with pair gaps in F8a. Gray cells have no eligible measured examples; policy and ownership require a Phase 5 teacher. The explicit dependency reasons appear in the Not run list. Bootstrap intervals for accuracy deltas are saved in accuracy_gaps.json.")
    verdict_rows = []
    for task in TASKS:
        ni = means(task,"nca",9)
        bi = means(task,best.get((task,9),""),9)
        nrows = ag[(ag.task == task)&(ag.model == "nca")&ag['size'].isin([19,25,37])]
        no = None if nrows.empty else float((nrows.correct.sum()/nrows['count'].sum()))
        brow = []
        for size in (19,25,37):
            part = ag[(ag.task == task)&(ag.model == best.get((task,size),""))&(ag['size'] == size)]
            if len(part):
                brow.append(part)
        bframe = pd.concat(brow) if brow else pd.DataFrame()
        bo = None if bframe.empty else float(bframe.correct.sum()/bframe['count'].sum())
        distance_task = "liberties" if task == "atari" else "ladders" if task.startswith("ladder L") else task
        chainpart = chain_df[chain_df.task == distance_task] if len(chain_df) else pd.DataFrame()
        if task.startswith("ladder L") and "ladder_kind" in chainpart:
            chainpart = chainpart[chainpart.ladder_kind == int(task[-1])]
        if task.startswith("ladder L") and "distance" in chainpart:
            chainpart = chainpart[chainpart.distance > 0]
        dist = "not run" if chainpart.empty else f"{int(chainpart.distance.min())} to {int(chainpart.distance.max())}"
        if task == "ring-vs-path" and "distance_min" in p:
            part = p[(p.task == task)&(p.model == "nca")]
            if len(part) and part.distance_min.notna().any():
                dist = f"{int(part.distance_min.min())} to {int(part.distance_max.max())}"
        def fmt(v):
            return "not run" if v is None or not np.isfinite(v) else f"{100*v:.2f}%"
        cost = "not run" if nrows.empty else f"{nrows.flops.mean():.0f} FLOPs; {nrows.ms.mean():.3f} ms"
        verdict_rows.append({"Task":task,"Distance":dist,"NCA ID":fmt(ni),"NCA OOD":fmt(no),"Baseline ID":fmt(bi),"Baseline OOD":fmt(bo),"NCA compute":cost,"Verdict":verdict(no,bo),"Figure":"F1a"})
    table = pd.DataFrame(verdict_rows)
    html_table = table.to_html(index=False,escape=True).replace("<td>F1a</td>",'<td><a href="#F1a">F1a</a></td>')
    sections.append('<section id="T1"><h2>Verdicts from the specified rule</h2>'+html_table+'<p>OOD pools measured boards of widths 19, 25 and 37. ID uses width 9. The ring-vs-path row pools liberty predictions on the matched ring and path positions. Smoke verdicts describe this reduced run only.</p></section>')
    def distance_scatter():
        fig,ax = plt.subplots(figsize=(9,5))
        for task,sub in chain_df.groupby("task"):
            for (size,lo),part in sub.groupby(["size","distance_lo"]):
                nca = part[part.model == "nca"]
                baseline = part[part.model == best.get((task,size),"")]
                if len(nca) and len(baseline):
                    ax.scatter(float(nca.distance.mean()),100*(nca.correct.mean()-baseline.correct.mean()),label=task)
        if "receptive_field_radius" in p:
            for radius in sorted(p.receptive_field_radius.dropna().unique()):
                ax.axvline(radius,color="#888888",ls="--",lw=.6)
        handles,labels = ax.get_legend_handles_labels()
        unique = dict(zip(labels,handles))
        if unique:
            ax.legend(unique.values(),unique.keys())
        ax.axhline(0,color="black",lw=.6)
        ax.set(xscale="log",xlabel="Information distance",ylabel="NCA minus baseline chain accuracy (pp)")
        return fig
    figure("F1b","Accuracy advantage by information distance",distance_scatter if len(chain_df) else None,caption="One point per measured task, board size and distance bin. Vertical guides show measured baseline receptive-field radii. The ordinate uses whole-chain correctness.")
    def scaling():
        tasks = sorted(ag.task.unique())
        fig,axes = plt.subplots(1,len(tasks),figsize=(max(8,4*len(tasks)),4),squeeze=False,layout="constrained")
        for ax,task in zip(axes[0],tasks):
            for model,sub in grouped[grouped.task == task].groupby("model"):
                if model.startswith("without_") or model == "b3":
                    continue
                sub = sub.sort_values("size")
                ax.errorbar(sub['size'],sub['mean']*100,yerr=sub['std'].fillna(0)*100,marker="o",ms=3,label=model,color=COLORS.get(model))
            ax.set(title=task,xlabel="Board width",ylabel="Per-stone accuracy (%)",ylim=(0,102))
            ax.legend(fontsize=6)
        return fig
    figure("F2","Substrate scaling",scaling if len(ag) else None,caption="Mean and sample standard deviation across logged training seeds. A single smoke seed has no measurable between-seed standard deviation; error bars are omitted.")
    def lightcone():
        fig,(ax,hist) = plt.subplots(1,2,figsize=(11,4))
        nca = chain_df[(chain_df.model == "nca")&chain_df.t_solve.notna()&(chain_df.distance > 0)]
        for task,sub in nca.groupby("task"):
            slope = np.polyfit(sub.distance,sub.t_solve,1)[0] if sub.distance.nunique() > 1 else None
            ax.scatter(sub.distance,sub.t_solve,s=12,alpha=.5,label=task+(f" slope {slope:.2f}" if slope is not None else ""))
            hist.hist(sub.efficiency.dropna(),bins=20,alpha=.4,label=task)
        reference = chain_df[(chain_df.model == "b3")&chain_df.t_solve.notna()]
        if len(reference):
            ax.scatter(reference.distance,reference.t_solve,s=8,alpha=.35,color="#009E73",label="Exact local CA reference")
        maxdist = max(1,float(chain_df.distance.max()))
        ax.plot([1,maxdist],[1,maxdist],ls="--",color="black",label="Slope 1 guide")
        ax.set(xlabel="Information distance",ylabel="First stable correct step")
        hist.set(xlabel="Steps / information distance",ylabel="Solved chains")
        ax.legend(fontsize=7)
        return fig
    solved = int(((chain_df.model == "nca")&chain_df.t_solve.notna()).sum()) if len(chain_df) and "t_solve" in chain_df else 0
    figure("F3","Light cone and convergence",lightcone if len(chain_df) and "t_solve" in chain_df else None,caption=f"{solved} solved NCA chains contribute measured convergence times. Unsolved chains are censored, with no invented solve time. Correctness must persist through the final logged step.")
    life = chain_df[(chain_df.task == "benson")&(chain_df.model == "nca")] if len(chain_df) else pd.DataFrame()
    def life_convergence():
        data = life[life.t_solve.notna()]
        fig,axes = plt.subplots(1,3,figsize=(12,4),layout="constrained")
        for ax,column,label in zip(axes,("benson_iterations","diameter","distance"),("Benson elimination iterations","Maximum chain diameter","Iterations × diameter")):
            part = data[data[column].notna()]
            ax.scatter(part[column],part.t_solve,s=10,alpha=.5)
            ax.set(xlabel=label,ylabel="First stable correct step")
        return fig
    figure("F3b","Benson convergence by exact algorithm cost",life_convergence if len(life) and "benson_iterations" in life else None,caption="Only solved chains contribute points. The horizontal coordinates come from the exact Benson labeler.")
    ladder = chain_df[(chain_df.task == "ladders")&(chain_df.distance > 0)].copy() if len(chain_df) else pd.DataFrame()
    def ladder_length():
        identifiers = ["seed","size","generator","board_id","chain_id"]
        descriptors = ladder[ladder.model == "nca"].set_index(identifiers)['length']
        inferred = pd.Series(descriptors.reindex(pd.MultiIndex.from_frame(ladder[identifiers])).to_numpy(),index=ladder.index)
        ladder['length'] = ladder['length'].fillna(inferred)
        fig,(ax,bx) = plt.subplots(1,2,figsize=(11,4),layout="constrained")
        for model,part in ladder.groupby("model"):
            if model.startswith("without_"):
                continue
            values = part.groupby("length").correct.mean()
            ax.plot(values.index,100*values,marker="o",ms=3,label=model,color=COLORS.get(model))
        nca = ladder[(ladder.model == "nca")&ladder.t_solve.notna()]
        slope = np.polyfit(nca['length'],nca.t_solve,1)[0] if nca['length'].nunique() > 1 else None
        bx.scatter(nca['length'],nca.t_solve,s=12,alpha=.5,label=f"NCA slope {slope:.2f}" if slope is not None else "NCA")
        if nca.empty:
            bx.text(.5,.5,"No applicable NCA chains solved",ha="center",va="center",transform=bx.transAxes)
        ax.set(xlabel="Principal-variation length (moves)",ylabel="Whole-chain accuracy (%)",ylim=(0,102))
        bx.set(xlabel="Principal-variation length (moves)",ylabel="First stable correct step")
        ax.legend(fontsize=6)
        bx.legend(fontsize=8)
        return fig
    figure("F3c","Ladder accuracy and convergence by length",ladder_length if len(ladder) and "length" in ladder else None,caption="Applicable one- and two-liberty chains are pooled. Unsolved chains contribute accuracy but have no plotted convergence time.")
    showcases = [path for path in paths if path.name.startswith("nca_")]
    for index,source in enumerate(showcases):
        file = figures/f"F4_{index}.png"
        stamp = file.with_suffix(".source.json")
        identity = {"source":str(source),"mtime_ns":source.stat().st_mtime_ns}
        if file.exists() and file.with_suffix(".gif").exists() and stamp.exists() and json.loads(stamp.read_text()) == identity:
            image,gif = file,file.with_suffix(".gif")
        else:
            try:
                image,gif = filmstrip(source,file)
                write_json(stamp,identity)
            except FloatingPointError as error:
                figure(f"F4_{index}",f"Rollout: {source.stem}",reason=str(error))
                continue
        caption = str(source.relative_to(ROOT))
        sections.append(f'<section id="F4_{index}"><h2>Rollout: {html.escape(source.stem)}</h2><img src="{embed(image)}" alt="Eight frame rollout"><img class="animation" src="{embed(gif)}" alt="Animated rollout"><p>F4. Source: {html.escape(caption)}.</p></section>')
    if not showcases:
        eligible = {path.name for path,payload in completed_runs(profile) if payload.get("pipeline_passed") or payload.get("phase") == "4a" and payload.get("status") == "passed"}
        cached = []
        for stamp in sorted(figures.glob("F4_*.source.json")):
            identity = json.loads(stamp.read_text())
            source = Path(identity["source"])
            png = stamp.with_suffix("").with_suffix(".png")
            if source.parent.parent.name in eligible and png.exists() and png.with_suffix(".gif").exists():
                cached.append((source,png))
        for index,(source,png) in enumerate(cached):
            sections.append(f'<section id="F4_cached_{index}"><h2>Rollout: {html.escape(source.stem)}</h2><img src="{embed(png)}" alt="Eight frame rollout"><img class="animation" src="{embed(png.with_suffix(".gif"))}" alt="Animated rollout"><p>F4. Cached rendering from the recorded run {html.escape(source.parent.parent.name)}.</p></section>')
        if not cached:
            figure("F4","How the NCA computes",reason="no saved learned rollout")
    repairs = [path for path in paths if path.name.startswith("repair_")]
    def repair():
        selected = repairs[:4]
        fig,axes = plt.subplots(1,len(selected),figsize=(4*len(selected),4),squeeze=False,layout="constrained")
        for ax,source in zip(axes[0],selected):
            v = np.load(source)
            fire = v["fire"].sum(0)
            im = board(ax,v["board"],fire,vmax=max(1,int(fire.max())),title=f"adaptive={bool(v['adaptive'])}, damage={bool(v['damage'])}")
            fig.colorbar(im,ax=ax,label="Cumulative fired updates",shrink=.6)
        return fig
    figure("F5a","Where cells fire",repair if repairs else None,caption="Counts are sampled update events. Dense XLA still evaluates the full convolution on every cell; firing counts do not imply a proportional hardware speedup.")
    def repair_curves(by_updates):
        fig,ax = plt.subplots(figsize=(8,4))
        for source in repairs[:4]:
            v = np.load(source)
            mask = v["target"] >= 0
            acc = (v["predictions"][:,mask] == v["target"][mask]).mean(1)*100
            x = v["fire"].sum(axis=(1,2)).cumsum() if by_updates else v["steps"]
            ax.plot(x,acc,label=f"adaptive={bool(v['adaptive'])}, damage={bool(v['damage'])}")
        ax.set(xlabel="Total fired cell updates" if by_updates else "Rollout step",ylabel="Per-stone accuracy (%)")
        ax.legend(fontsize=8)
        return fig
    def damage_curves():
        fig,(ax,bx) = plt.subplots(1,2,figsize=(11,4),layout="constrained")
        for source in repairs[:4]:
            v = np.load(source)
            mask = v["target"] >= 0
            label = f"adaptive={bool(v['adaptive'])}, damage={bool(v['damage'])}"
            acc = (v["predictions"][:,mask] == v["target"][mask]).mean(1)*100
            ax.plot(v["steps"],acc,label=label)
            bx.plot(v["steps"],v["fire"].sum(axis=(1,2)),label=label,alpha=.65)
            if bool(v["damage"]):
                ax.axvline(len(v["steps"])//2+1,color="#777777",ls="--",lw=.6)
        ax.set(xlabel="Rollout step",ylabel="Per-stone accuracy (%)")
        bx.set(xlabel="Rollout step",ylabel="Fired cells in that step")
        ax.legend(fontsize=7)
        return fig
    figure("F5b","Accuracy against cell updates",lambda:repair_curves(True) if repairs else None,reason=None if repairs else "no repair rollouts")
    figure("F5c","Damage and recovery",damage_curves if repairs else None,reason=None if repairs else "no damage experiment",caption="Dashed guides mark damage injection; curves show measured accuracy and sampled firing events.")
    def ablations():
        subset = grouped[grouped.model.str.startswith("without_")| (grouped.model == "nca")]
        subset = subset[subset['size'].isin([19,25,37])]
        values = subset.groupby(["task","model"])["mean"].mean().unstack(0)*100
        fig,ax = plt.subplots(figsize=(10,5))
        values.plot.bar(ax=ax)
        ax.set(ylabel="Per-stone OOD accuracy (%)",xlabel="Training component removed",ylim=(0,100))
        fig.tight_layout()
        return fig
    figure("F6","Recipe ablations",ablations if not grouped.empty and grouped.model.str.startswith("without_").any() else None,caption="Each variant uses the same data, augmentation and optimizer step budget; model selection uses separate 13x13 validation.")
    def testtime():
        fig,(ax,bx) = plt.subplots(1,2,figsize=(11,4))
        nca = df[df.model == "nca"]
        for task,sub in nca.groupby("task"):
            ordinary = sub
            for flag in ("repair","sweep"):
                if flag in ordinary:
                    ordinary = ordinary[ordinary[flag] != True]
            points = ordinary.groupby("steps").agg(c=("stone_correct","sum"),n=("stone_count","sum"))
            ax.plot(points.index,100*points.c/points.n,label=task,marker="o")
            sweep = sub[sub.sweep == True] if "sweep" in sub else sub.iloc[:0]
            for sigma,part in sweep.groupby("noise_sigma"):
                values = part.groupby("trials").agg(c=("stone_correct","sum"),n=("stone_count","sum"))
                bx.plot(values.index,100*values.c/values.n,label=f"{task}, sigma={sigma}",marker="o")
        ax.set(xlabel="Rollout steps",ylabel="Accuracy (%)",xscale="log")
        bx.set(xlabel="Parallel trials selected by confidence",ylabel="Accuracy (%)")
        ax.legend(fontsize=6)
        bx.legend(fontsize=6)
        return fig
    figure("F7","Test-time scaling",testtime if len(df) else None,caption="Temporal sweeps reuse logged trajectories. Conf@K selects the greatest board-mean confidence without accessing target labels. Noise is applied only during the initial quarter of a rollout.")
    def cyclic():
        fig,ax = plt.subplots(figsize=(11,5))
        labels = []
        for i,((task,model,size),sub) in enumerate(gaps.groupby(["task","model","size"])):
            mean,lo,hi = sub.gap.mean(),sub.ci_low.mean(),sub.ci_high.mean()
            ax.errorbar(i,100*mean,yerr=[[max(0,100*(mean-lo))],[max(0,100*(hi-mean))]],fmt="o",color=COLORS.get(model,"#777777"))
            labels.append(f"{task}\n{model}\n{size}")
        ax.set_xticks(range(len(labels)),labels,rotation=90,fontsize=6)
        ax.axhline(0,color="black",lw=.6)
        ax.set_ylabel("Ring minus matched path accuracy (pp)")
        return fig
    figure("F8a","Cyclic groups: matched pairs",cyclic if len(gaps) else None,caption="Paired board bootstrap 95% intervals. A single training seed in smoke cannot measure training-seed uncertainty.")
    reason5 = next((m.get("reason") for m in metadata if m["phase"] == "5" and m.get("status") == "not run"),"Phase 5 has no logged evaluation")
    reason4b = next((m.get("reason") for m in metadata if m["phase"] == "4b" and m.get("status") == "not run"),"teacher and adversarial SGF results unavailable")
    player_runs = [path for path,payload in completed_runs(profile) if payload.get("phase") == "5" and payload.get("status") == "passed"]
    adversarial_runs = [path for path,payload in completed_runs(profile) if payload.get("phase") == "4b" and payload.get("status") == "passed"]
    player_path = player_runs[-1] if player_runs else None
    adversarial_path = adversarial_runs[-1] if adversarial_runs else None
    def adversarial():
        data = pd.read_csv(adversarial_path/"eval"/"adversarial.csv")
        fig,(ax,bx) = plt.subplots(1,2,figsize=(11,4))
        grouped = data.groupby("model")[["mean_victim_ownership","fraction_victim_owned"]].mean()
        grouped.mean_victim_ownership.plot.bar(ax=ax)
        grouped.fraction_victim_owned.plot.bar(ax=bx)
        ax.set_ylabel("Mean ownership from victim perspective")
        bx.set_ylabel("Fraction predicted victim-owned")
        return fig
    figure("F8b","Ownership of doomed cyclic groups",adversarial if adversarial_path else None,reason=None if adversarial_path else reason4b)
    def player_scaling():
        data = pd.read_csv(player_path/"eval"/"player.csv")
        fig,(ax,bx) = plt.subplots(1,2,figsize=(10,4))
        for depth,part in data.groupby("steps"):
            part = part.sort_values("size")
            ax.plot(part['size'],part.top1_agreement*100,marker="o",label=f"D={depth}")
            bx.plot(part['size'],part.ownership_mse,marker="o",label=f"D={depth}")
        ax.set(xlabel="Board width",ylabel="Policy top-1 agreement (%)")
        bx.set(xlabel="Board width",ylabel="Ownership MSE")
        ax.legend(fontsize=7)
        return fig
    figure("F9a","Player substrate scaling",player_scaling if player_path else None,reason=None if player_path else reason5)
    def ownership_maps():
        source = sorted((player_path/"viz").glob("ownership_*.npz"))[-1]
        v = np.load(source)
        count = min(3,len(v["teacher"]))
        fig,axes = plt.subplots(2,count,figsize=(4*count,8),squeeze=False,layout="constrained")
        for i in range(count):
            stones = np.zeros(v["teacher"][i].shape,np.int8)
            to_move = 1 if v["features"][i,0,0,9] > 0 else 2
            stones[v["features"][i,...,0] > .5] = to_move
            stones[v["features"][i,...,1] > .5] = 3-to_move
            for row,key in enumerate(("teacher","student")):
                im = board(axes[row,i],stones,v[key][i],cmap="BrBG",vmin=-1,vmax=1,title=key)
                fig.colorbar(im,ax=axes[row,i],shrink=.7,label="Black ownership")
        return fig
    has_ownership = player_path is not None and any((player_path/"viz").glob("ownership_*.npz"))
    figure("F9b","Teacher and student ownership",ownership_maps if has_ownership else None,reason=None if has_ownership else reason5)
    def warm_cold():
        data = pd.concat([pd.read_csv(f) for f in (player_path/"eval").glob("warm_*.csv")],ignore_index=True)
        fig,ax = plt.subplots(figsize=(8,4))
        for warm,part in data.groupby("warm"):
            grouped = part.groupby("size").t_reconverge.mean()
            ax.plot(grouped.index,grouped,marker="o",label="warm" if warm else "cold")
        ax.set(xlabel="Board width",ylabel="Steps to stable reconvergence")
        ax.legend()
        return fig
    has_warm = player_path is not None and any((player_path/"eval").glob("warm_*.csv"))
    figure("F9c","Warm and cold start reconvergence",warm_cold if has_warm else None,reason=None if has_warm else reason5)
    if player_path and (player_path/"eval"/"matches.csv").exists():
        matches = pd.read_csv(player_path/"eval"/"matches.csv")
        sections.append('<section id="T2"><h2>Match results</h2>'+matches.to_html(index=False)+'<p>Wilson 95% intervals. Elo is undefined when the observed win fraction is zero or one.</p></section>')
    else:
        figure("T2","Match results",reason=reason5)
    def compute():
        costs = p.copy()
        ordinary = df.copy()
        for flag in ("sweep","repair"):
            if flag in ordinary:
                ordinary = ordinary[ordinary[flag] != True]
        candidates = ordinary[(ordinary.model == "nca")&(ordinary.task_metric.isna() if "task_metric" in ordinary else True)]
        depth_rows = []
        for _,part in candidates.groupby(["task","seed","size","generator","board_id"]):
            final_acc = part.sort_values("steps").iloc[-1].stone_accuracy
            acceptable = part[part.stone_accuracy >= .95*final_acc].sort_values("steps")
            if len(acceptable):
                depth_rows.append(acceptable.iloc[0])
        if depth_rows:
            selected = pd.DataFrame(depth_rows)
            costs = pd.concat([costs[costs.model != "nca"],selected],ignore_index=True)
        compute_group = aggregate(costs).groupby(["task","model","size"],as_index=False).agg(flops=("flops","mean"),ms=("ms","mean"))
        fig,(ax,bx) = plt.subplots(1,2,figsize=(11,4))
        for (task,model),part in compute_group.groupby(["task","model"]):
            if model.startswith("without_") or model == "b3":
                continue
            part = part.sort_values("size")
            ax.plot(part['size'],part.flops,label=f"{task} {model}",marker="o",ms=2)
            bx.plot(part['size'],part.ms,label=f"{task} {model}",marker="o",ms=2)
        ax.set(xlabel="Board width",ylabel="Compiled FLOPs per evaluation",yscale="log")
        bx.set(xlabel="Board width",ylabel="Measured synchronized milliseconds",yscale="log")
        ax.legend(fontsize=5,ncol=2)
        return fig
    figure("F10","Compute",compute if len(ag) else None,caption="XLA cost analysis measures operations. Wall times exclude compilation and include device synchronization. NCA costs select the earliest logged depth attaining 95% of that board's final accuracy.")
    if profile == "smoke":
        full_reasons = {payload["reason"] for _,payload in completed_runs("full")
                        if payload.get("profile") == "full" and payload.get("status") == "not run" and payload.get("reason")}
        missing.extend({"figure":"Full profile","reason":reason} for reason in sorted(full_reasons))
    findings = []
    for task in sorted(ag.task.unique()):
        value = means(task,"nca",9)
        if value is None:
            continue
        other = [means(task,"nca",s) for s in (19,25,37)]
        measured = [v for v in other if v is not None]
        findings.append(f"{100*value:.2f}% NCA per-stone accuracy on {task} at width 9 (F1a, F2). "+
            (f"{100*min(measured):.2f}% to {100*max(measured):.2f}% across the measured larger test boards (F2). " if measured else "Larger-board evaluations were not run (F1a). ")+
            ("The reduced CPU run does not certify the research accuracy gate (T1)." if profile == "smoke" else "The comparison uses held-out evaluation data (T1)."))
    nca_tasks = table[table.Verdict == "Use NCA"].Task.tolist()
    baseline_tasks = table[table.Verdict == "Use baseline"].Task.tolist()
    use = "Tasks satisfying the NCA rule: "+(", ".join(nca_tasks) if nca_tasks else "none in the measured runs")+" (T1)."
    avoid = "Tasks satisfying the baseline rule: "+(", ".join(baseline_tasks) if baseline_tasks else "none in the measured runs")+" (T1). Unknown tasks need measurements before a recommendation (T1)."
    sections.append('<section id="findings"><h2>Findings</h2>'+"".join(f"<p>{html.escape(t)}</p>" for t in findings+[use,avoid])+"<h3>Not run</h3><ul>"+"".join(f"<li>{html.escape(m['figure'])}: {html.escape(m['reason'])}</li>" for m in missing)+"</ul></section>")
    gate = next((m for m in reversed(metadata) if m.get("gate") == "G1"),None)
    banner = f"Profile: {profile}. " + (f"G1: {gate['status']}, measured ID accuracy {100*gate['id_accuracy']:.2f}%." if gate else "G1 not yet measured.")
    styles = "body{margin:0;background:#f2f4f5;color:#18242c;font:16px/1.6 system-ui,sans-serif}main{max-width:1280px;margin:auto;padding:36px}header{background:#162f3b;color:#fff;padding:40px;border-radius:14px}h1{font-size:42px;line-height:1.1}section{background:white;margin:24px 0;padding:26px;border-radius:12px;overflow:auto}img{max-width:100%;height:auto}img.animation{max-width:700px;display:block}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}.missing{padding:20px;background:#edf0f2;color:#54606a}nav{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}a{color:#0072b2}header a{color:#a8dced}pre{white-space:pre-wrap;font-size:12px}"
    navigation = "".join(f'<a href="#{key}">{key}</a>' for key in ("F1a","T1","F2","F3","F5a","F6","F7","F8a","F10","findings"))
    document = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NCA Go capability report</title><style>'+styles+'</style></head><body><main><header><p>LOCAL REASONING / MEASURED EVIDENCE</p><h1>Neural cellular automata for Go</h1><p>'+html.escape(banner)+'</p><p>All result values come from recorded runs. The report opens offline.</p></header><nav>'+navigation+'</nav>'+"".join(sections)+'<section><h2>Run provenance</h2><pre>'+html.escape(json.dumps(metadata,indent=2))+'</pre><p>Architecture reference: <a href="https://arxiv.org/abs/2609.36126">Etcheverry et al., Reasoning with Neural Cellular Automata</a>.</p></section></main></body></html>'
    (reportdir/"nca_go_report.html").write_text(document)
    summary = f"# NCA Go measured summary\n\n{banner}\n\n"+md_table(table)+"\n\n## Findings\n\n"+"\n\n".join(findings+[use,avoid])+"\n\n## Not run\n\n"+"\n".join(f"- {m['figure']}: {m['reason']}" for m in missing)+"\n\nRegenerate with `make report`. Raw uncertainty data: `reports/accuracy_gaps.json`.\n"
    (reportdir/"SUMMARY.md").write_text(summary)
    rules = [m for m in metadata if m.get("phase") == "0" and m.get("games") == 10000 and m.get("status") == "passed"]
    if rules:
        measured = rules[-1]
        with (reportdir/"SUMMARY.md").open("a") as stream:
            stream.write(f"\nRules cross-check: {measured['matched_moves']:,} matching moves across {measured['games']:,} games; {measured['wall_seconds']:.3f} seconds.\n")
    properties = [json.loads(file.read_text()) for file in sorted((ROOT/"results"/"2-properties").glob("*/summary.json"))]
    properties = [item for item in properties if item.get("status") == "passed"]
    if properties:
        measured = properties[-1]
        with (reportdir/"SUMMARY.md").open("a") as stream:
            stream.write(f"\nBenson property check: {measured['playouts']:,} opponent playouts and {measured['opponent_moves']:,} moves; {measured['wall_seconds']:.3f} seconds.\n")
    readme = ROOT/"README.md"
    if readme.exists():
        timing = pd.DataFrame([{"Phase":m["phase"],"Status":m.get("status"),"Seconds":f"{m['wall_seconds']:.3f}","Hardware":", ".join(m["hardware"]["devices"])} for m in metadata if "wall_seconds" in m and m.get("phase") in ("1","2","3","4a","5","4b")])
        text = readme.read_text()
        start,end = "<!-- measured-run-summary:start -->","<!-- measured-run-summary:end -->"
        block = start+"\n\n## Measured runs\n\n"+md_table(timing)+"\n\n"+end
        if start in text:
            text = re.sub(re.escape(start)+r".*?"+re.escape(end),lambda _:block,text,flags=re.S)
        else:
            text += "\n\n"+block+"\n"
        readme.write_text(text)
    write_json(reportdir/"report_manifest.json",{"profile":profile,"runs":[m.get("config_hash") for m in metadata],"not_run":missing,"self_contained":True})
    print(f"Report built: {reportdir/'nca_go_report.html'}",flush=True)
    return reportdir/"nca_go_report.html"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile",choices=["smoke","full"])
    profile = parser.parse_args().profile
    if profile is None:
        profiles = []
        for path in (ROOT/"results").glob("[123]/*/summary.json"):
            payload = json.loads(path.read_text())
            if payload.get("pipeline_passed"):
                profiles.append((path.parent.name,payload.get("profile","smoke")))
        profile = max(profiles)[1] if profiles else "smoke"
    build(profile)


if __name__ == "__main__":
    main()
