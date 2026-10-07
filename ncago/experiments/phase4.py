"""Matched ring/path evaluation, paired bootstrap, no weight changes."""
import json
import time
from dataclasses import replace
import numpy as np
import pandas as pd
from flax import serialization
from ncago.go.generators import ring_pair
from ncago.nca.model import ModelConfig,NCA,initialize,init_params
from ncago.baselines.resnet import ResNet
from .common import Run,ROOT,write_json
from .tasks import labeled,split_seed
from .evaluate import evaluate_nca,evaluate_resnet
from .metrics import bootstrap_gap
from .metrics import accuracy
from ncago.baselines.local import liberty_ca
from ncago.go.labels import benson
import jax
import jax.numpy as jnp


def restore_models(path,config):
    details = json.loads((path/"models.json").read_text())
    key = jax.random.PRNGKey(0)
    result = {}
    for name,info in details.items():
        file = path/"ckpt"/f"{name}.msgpack"
        if not file.exists():
            raise FileNotFoundError(f"Checkpoint required: {file}")
        if "config" in info:
            mc = ModelConfig(**info["config"])
            model = NCA(mc)
            template = init_params(model,initialize(jnp.zeros((1,9,9),jnp.int32),key,mc),key)
            kind = "nca"
        else:
            model = ResNet(4 if config["task"] == "liberties" else 3,info["blocks"],info["width"])
            template = model.init(key,jnp.zeros((1,9,9,config["input_channels"])))["params"]
            kind = "resnet"
        result[name] = model,serialization.from_bytes(template,file.read_bytes()),kind
    return result


def run(config,task_models):
    log = Run("4a",config)
    all_rows,gaps = [],[]
    for task,seed,models in task_models:
        taskconfig = {**config,"task":task}
        for size in config["test_sizes"]:
            rng = np.random.default_rng(split_seed(task,"ringpair",size))
            pairs = [ring_pair(size,rng) for _ in range(config["ring_pairs"])]
            for partner in (0,1):
                boards = np.stack([p[partner] for p in pairs])
                labels,infos = labeled(task,boards,taskconfig)
                np.savez_compressed(log.path/"data"/f"pairs_{task}_{seed}_{size}_{partner}.npz",boards=boards,labels=labels)
                for i,info in enumerate(infos):
                    # Ring distance is half its perimeter, per the matched-pair protocol.
                    if partner == 0:
                        info["distance"] = np.full(boards[i].shape,int(np.count_nonzero(boards[i] == pairs[i][2])//2))
                for name,(model,params,kind) in models.items():
                    if name.startswith("without_"):
                        continue
                    if kind == "nca":
                        rows,_ = evaluate_nca(model,params,boards,labels,infos,taskconfig,seed,name,"ring" if partner == 0 else "path",log,showcase=name == "nca" and size == 37,sweep=False)
                    else:
                        rows,_ = evaluate_resnet(model,params,boards,labels,infos,taskconfig,seed,name,"ring" if partner == 0 else "path")
                    for row in rows:
                        row["task"] = task
                        distance = infos[row["board_id"]]["distance"]
                        defined = labels[row["board_id"]] >= 0
                        row["distance_min"] = int(distance[defined].min()) if defined.any() else None
                        row["distance_max"] = int(distance[defined].max()) if defined.any() else None
                    all_rows.extend(rows)
                for i,(b,target,info) in enumerate(zip(boards,labels,infos)):
                    start = time.perf_counter()
                    if task == "liberties":
                        pred,convergence = liberty_ca(b)
                        prediction,steps = pred[-1],len(pred)-1
                    else:
                        prediction,reference_info = benson(b)
                        steps = reference_info["iterations"]*reference_info["diameter"]
                    ms = (time.perf_counter()-start)*1000
                    all_rows.append({"task":task,"model":"b3","seed":seed,"size":size,"generator":"ring" if partner == 0 else "path","board_id":i,"steps":steps,
                        "trials":1,"noise_sigma":0.,"adaptive":False,"damage":False,"ms":ms,**accuracy(b,target,prediction)})
            df = pd.DataFrame(all_rows)
            df = df[(df.task == task)&(df['size'] == size)&(df.seed == seed)]
            if "task_metric" in df:
                df = df[df.task_metric.isna()]
            df = df[df.steps == df.groupby(["model","generator","board_id"]).steps.transform("max")]
            for model,group in df.groupby("model"):
                pivot = group.pivot(index="board_id",columns="generator",values="stone_accuracy")
                gap,lo,hi = bootstrap_gap(pivot.ring,pivot.path,seed,config["bootstrap_samples"])
                gaps.append({"task":task,"model":model,"seed":seed,"size":size,"gap":gap,"ci_low":lo,"ci_high":hi,"pairs":len(pivot)})
            print(f"matched pairs {task} {size}",flush=True)
    pd.DataFrame(all_rows).to_csv(log.path/"eval"/"pairs.csv",index=False)
    pd.DataFrame(gaps).to_csv(log.path/"eval"/"gaps.csv",index=False)
    return log.finish("passed",profile=config["profile"],comparisons=len(gaps),evaluations=len(all_rows))


if __name__ == "__main__":
    from .phase_cli import task_main
    task_main("4a")
