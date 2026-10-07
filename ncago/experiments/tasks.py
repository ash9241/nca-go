"""Train once on 9, select on 13, then unlock immutable final evaluation splits."""
from dataclasses import replace, asdict
from pathlib import Path
import copy
import json
import hashlib
import time
import numpy as np
import pandas as pd
import jax
import jax.numpy as jnp
from ncago.go.generators import generate,canonical_key,balanced_benson,balanced_ladders
from ncago.go.labels import LABELERS
from ncago.baselines.resnet import ResNet,matched_width
from ncago.baselines.local import liberty_ca
from ncago.nca.model import NCA,ModelConfig
from ncago.nca.train import train_nca,train_resnet
from .common import Run,write_json
from .evaluate import evaluate_nca,evaluate_resnet
from .metrics import accuracy


def labeled(task,boards,config):
    labeler = LABELERS[task]
    outputs = [labeler(b,max_nodes=config["ladder_node_budget"]) if task == "ladders" else labeler(b) for b in boards]
    return np.stack([y for y,_ in outputs]),[info for _,info in outputs]


def split_seed(task,split,size):
    # Stable across model/ablation/training seed; identical data for every model.
    return int(hashlib.sha256(f"ncago/{task}/{split}/{size}".encode()).hexdigest()[:8],16)


def split(task,size,count,seed,config,run,name,generator="mixed",exclude=()):
    if task == "ladders" and config["profile"] == "full":
        boards,sources,labels,infos,counts = balanced_ladders(size,count,seed,config["ladder_node_budget"],exclude)
        run.log(event="balanced_ladder_split",split=name,size=size,defender_outcomes_per_PV_bin=counts)
    else:
        boards,sources = generate(task,size,count,seed,generator,exclude,controlled=task == "liberties" and config["profile"] == "full")
        labels,infos = labeled(task,boards,config)
    return boards,sources,labels,infos


def run_task(task,config,seed):
    phase = {"liberties":"1","benson":"2","ladders":"3"}[task]
    config = {**config,"task":task}
    run = Run(phase,config,seed)
    classes = 4 if task == "liberties" else 3
    mc = ModelConfig(**{k:config[k] for k in ("channels","input_channels","heads","expansion","neighborhood","normalization_groups","readout","fire_rate","init_sigma")},classes=classes)
    if task == "benson" and config["profile"] == "full":
        train,train_sources,chain_counts = balanced_benson(9,config["train_count"],split_seed(task,"train",9))
        run.log(event="balanced_training_data",chain_class_counts=chain_counts,class_fractions=chain_counts/chain_counts.sum())
        y,_ = labeled(task,train,config)
    else:
        train,train_sources,y,_ = split(task,9,config["train_count"],split_seed(task,"train",9),config,run,"train")
    val,val_sources,vy,_ = split(task,13,config["validation_count"],split_seed(task,"validation",13),config,run,"validation")
    train_hashes = {canonical_key(b) for b in train}
    validation_hashes = {canonical_key(b) for b in val}
    np.savez_compressed(run.path/"data"/"train.npz",boards=train,labels=y)
    np.savez_compressed(run.path/"data"/"validation.npz",boards=val,labels=vy)
    # Record source and split hashes; test generation occurs only after selection.
    write_json(run.path/"data_manifest.json",{"train_sources":train_sources,"validation_sources":val_sources,
        "train_seed":split_seed(task,"train",9),"validation_seed":split_seed(task,"validation",13),
        "train_hash":hashlib.sha256(train.tobytes()).hexdigest(),"validation_hash":hashlib.sha256(val.tobytes()).hexdigest()})
    models,details = {},{}
    model = NCA(mc)
    params,stats = train_nca(model,train,y,(val,vy),config,seed,run)
    selected_channels,selected_expansion = mc.channels,mc.expansion
    if config["profile"] == "full":
        for channels in config.get("channel_sweep",[16,32,64]):
            for expansion in config.get("expansion_sweep",[2,4]):
                if (channels,expansion) == (mc.channels,mc.expansion):
                    continue
                candidate_mc = replace(mc,channels=channels,expansion=expansion)
                candidate_model = NCA(candidate_mc)
                candidate_name = f"candidate_c{channels}_e{expansion}"
                candidate_params,candidate_stats = train_nca(candidate_model,train,y,(val,vy),config,seed,run,candidate_name)
                if candidate_stats["validation_accuracy"] > stats["validation_accuracy"]:
                    model,params,stats = candidate_model,candidate_params,candidate_stats
                    selected_channels,selected_expansion = channels,expansion
        mc = replace(mc,channels=selected_channels,expansion=selected_expansion)
        from flax import serialization
        (run.path/"ckpt"/"nca.msgpack").write_bytes(serialization.to_bytes(params))
        run.log(event="architecture_selection",channels=selected_channels,expansion=selected_expansion,selection_split="13x13 validation",validation_accuracy=stats["validation_accuracy"])
    models["nca"] = (model,params,"nca")
    details["nca"] = {**stats,"config":asdict(mc)}
    # ID diagnostics are validation data at training size, never the final ID test.
    diagnostic,ds,dy,di = split(task,9,config["validation_count"],split_seed(task,"diagnostic",9),config,run,"diagnostic",exclude=train_hashes)
    diagnostic_rows,_ = evaluate_nca(model,params,diagnostic,dy,di,config,seed,"nca","diagnostic",run,sweep=False)
    primary = [r for r in diagnostic_rows if "task_metric" not in r and r["steps"] == max(x["steps"] for x in diagnostic_rows)]
    diagnostic_acc = sum(r["stone_correct"] for r in primary)/max(1,sum(r["stone_count"] for r in primary))
    run.log(event="ID_diagnostic",accuracy=diagnostic_acc,finite=True,inputs_frozen=True)
    if task == "liberties" and diagnostic_acc < .995 and config["profile"] == "full":
        run.finish("gate_failed",gate="G1 diagnostic",accuracy=diagnostic_acc,reason="ID diagnostics below .995; later phases blocked")
        return run.path,models,False
    recurrent_config = {**config,"replay":False,"noise":False,"damage":False,"target_swap":False}
    recurrent = NCA(replace(mc,fire_rate=1.))
    recurrent_params,stats = train_nca(recurrent,train,y,(val,vy),recurrent_config,seed,run,"b2")
    models["b2"] = recurrent,recurrent_params,"nca"
    details["b2"] = {**stats,"config":asdict(recurrent.config)}
    for blocks in config["baseline_blocks"]:
        for ratio in config["baseline_ratios"]:
            width = matched_width(details["nca"]["params"]*ratio,blocks,classes,config["input_channels"])
            name = f"b1_L{blocks}_x{ratio}"
            net = ResNet(classes,blocks,width)
            pp,stats = train_resnet(net,train,y,(val,vy),config,seed,run,name)
            models[name] = net,pp,"resnet"
            details[name] = {**stats,"blocks":blocks,"width":width,"ratio":ratio,"actual_parameter_ratio":stats["params"]/details["nca"]["params"]}
    if task in ("liberties","ladders"):
        for ablation in config["ablations"]:
            abconfig = copy.deepcopy(config)
            abmc = mc
            if ablation == "async":
                abmc = replace(mc,fire_rate=1.)
            elif ablation == "neighborhood":
                abmc = replace(mc,neighborhood="von_neumann")
            else:
                abconfig[ablation] = False
            name = "without_"+ablation
            net = NCA(abmc)
            pp,stats = train_nca(net,train,y,(val,vy),abconfig,seed,run,name)
            models[name] = net,pp,"nca"
            details[name] = {**stats,"config":asdict(abmc)}
    write_json(run.path/"models.json",details)
    from .showcase import run_showcases
    run_showcases(task,models["nca"][0],models["nca"][1],config,seed,run)
    # All checkpoint choices are now finalized, before any final test set is read.
    all_rows,all_chains = [],[]
    for size in config["test_sizes"]:
        generators = ["random","structured"] if task == "liberties" else ["mixed"]
        for generator in generators:
            exclude = train_hashes if size == 9 else validation_hashes if size == 13 else set()
            boards,sources,yy,infos = split(task,size,config["test_count"],split_seed(task,"test/"+generator,size),config,run,"test",generator,exclude)
            if size == 9 and any(canonical_key(b) in train_hashes for b in boards):
                raise RuntimeError("Train/test duplicate detected")
            np.savez_compressed(run.path/"data"/f"test_{generator}_{size}.npz",boards=boards,labels=yy)
            for name,(net,pp,kind) in models.items():
                if kind == "nca":
                    rows,cr = evaluate_nca(net,pp,boards,yy,infos,config,seed,name,generator,run,
                        showcase=name == "nca" and size in (9,19,37),sweep=name == "nca")
                else:
                    rows,cr = evaluate_resnet(net,pp,boards,yy,infos,config,seed,name,generator)
                all_rows.extend(rows)
                all_chains.extend(cr)
            if task == "liberties":
                for i,(b,target) in enumerate(zip(boards,yy)):
                    started = time.perf_counter()
                    predictions,convergence = liberty_ca(b)
                    elapsed = (time.perf_counter()-started)*1000
                    all_rows.append({"model":"b3","seed":seed,"size":size,"generator":generator,"board_id":i,"steps":len(predictions)-1,"trials":1,"noise_sigma":0.,"adaptive":False,"damage":False,"ms":elapsed,**accuracy(b,target,predictions[-1])})
                    run.log(event="B3",size=size,board_id=i,steps_per_chain=convergence,ms=elapsed)
                    from ncago.go.rules import chains,diameter
                    from .metrics import distance_bin
                    for ci,(chain,solved) in enumerate(zip(chains(b),convergence)):
                        distance = diameter(chain)+1
                        lo,hi = distance_bin(distance)
                        all_chains.append({"model":"b3","seed":seed,"size":size,"generator":generator,"board_id":i,"chain_id":ci,
                            "distance":distance,"distance_lo":lo,"distance_hi":hi,"t_solve":solved,"efficiency":solved/distance if solved is not None else None,"correct":solved is not None})
            elif task == "benson":
                from ncago.go.labels import benson
                from .metrics import distance_bin
                from ncago.go.rules import chains
                for i,(b,target) in enumerate(zip(boards,yy)):
                    started = time.perf_counter()
                    prediction,info = benson(b)
                    milliseconds = (time.perf_counter()-started)*1000
                    yardstick = info["iterations"]*info["diameter"]
                    all_rows.append({"model":"b3","seed":seed,"size":size,"generator":generator,"board_id":i,"steps":yardstick,"trials":1,"noise_sigma":0.,"adaptive":False,"damage":False,"ms":milliseconds,**accuracy(b,target,prediction)})
                    for ci,chain in enumerate(chains(b)):
                        lo,hi = distance_bin(max(1,yardstick))
                        all_chains.append({"model":"b3","seed":seed,"size":size,"generator":generator,"board_id":i,"chain_id":ci,"distance":max(1,yardstick),"distance_lo":lo,"distance_hi":hi,"t_solve":yardstick,"efficiency":1. if yardstick else None,"correct":True,"benson_iterations":info["iterations"],"diameter":info["diameter"]})
            pd.DataFrame(all_rows).to_csv(run.path/"eval"/"boards.csv",index=False)
            pd.DataFrame(all_chains).to_csv(run.path/"eval"/"chains.csv",index=False)
            print(f"evaluated {task} {size} {generator}",flush=True)
    df = pd.DataFrame(all_rows)
    primary = df[(df.model == "nca")&(df['size'] == 9)&df.get("task_metric",pd.Series(index=df.index,dtype=object)).isna()]
    for flag in ("sweep","repair"):
        if flag in primary:
            primary = primary[primary[flag] != True]
    primary = primary[primary.steps == primary.groupby(["generator","board_id"]).steps.transform("max")]
    id_accuracy = float(primary.stone_correct.sum()/max(1,primary.stone_count.sum()))
    gate = task != "liberties" or id_accuracy >= .995
    run.finish("passed" if gate else "gate_failed",id_accuracy=id_accuracy,gate="G1" if task == "liberties" else None,
        pipeline_passed=True,profile=config["profile"],models=list(models),evaluation_rows=len(all_rows))
    return run.path,models,gate
