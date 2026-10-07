from functools import partial,lru_cache
import time
import numpy as np
import jax
import jax.numpy as jnp
from ncago.nca.model import initialize, rollout, step
from ncago.go.rules import chains
from .metrics import accuracy,solve_times,distance_bin


def xla_flops(function,*arguments):
    analysis = jax.jit(function).lower(*arguments).compile().cost_analysis()
    if isinstance(analysis,list):
        return float(sum(a.get("flops",0) for a in analysis))
    if "flops" not in analysis:
        return None
    return float(analysis["flops"])


@lru_cache(maxsize=256)
def compiled_rollout(model,steps,keep_states=False,adaptive=False,noise_sigma=0.,damage_step=-1):
    return jax.jit(partial(rollout,model,steps=steps,keep_states=keep_states,adaptive=adaptive,noise_sigma=noise_sigma,damage_step=damage_step))


def evaluate_nca(model,params,boards,labels,infos,config,seed,name,generator,run,showcase=False,sweep=True):
    batch = config.get("evaluation_batch_size",4)
    rows,chainrows = [],[]
    for start in range(0,len(boards),batch):
        rr,cc = _evaluate_nca_batch(model,params,boards[start:start+batch],labels[start:start+batch],infos[start:start+batch],config,seed+start,name,generator,run,showcase and start == 0,sweep)
        for row in rr+cc:
            row["board_id"] += start
            row["seed"] = seed
        rows.extend(rr)
        chainrows.extend(cc)
    return rows,chainrows


def _evaluate_nca_batch(model,params,boards,labels,infos,config,seed,name,generator,run,showcase=False,sweep=True):
    tokens = jnp.asarray(boards)
    key = jax.random.PRNGKey(seed)
    initial = initialize(tokens,key,model.config)
    bound = max(int(info["distance"].max()) for info in infos)
    auto = max(1,4*bound)
    if config["auto_steps_cap"] is not None:
        auto = min(auto,config["auto_steps_cap"])
    checkpoints = sorted(set(config["evaluation_steps"]+[auto]))
    maximum = max(checkpoints)
    function = compiled_rollout(model,maximum,showcase)
    # Compile and warm up before timing; synchronization prevents dispatch timing.
    result = function(params,initial,tokens,key)
    jax.block_until_ready(result)
    started = time.perf_counter()
    final,trajectory = function(params,initial,tokens,key)
    jax.block_until_ready((final,trajectory))
    milliseconds = (time.perf_counter()-started)*1000/len(boards)
    predictions,confidence,firing = [np.array(v) for v in trajectory[:3]]
    measured_ms = {maximum:milliseconds}
    for d in checkpoints:
        if d == maximum:
            continue
        timed = compiled_rollout(model,d)
        jax.block_until_ready(timed(params,initial,tokens,key))
        start = time.perf_counter()
        jax.block_until_ready(timed(params,initial,tokens,key))
        measured_ms[d] = (time.perf_counter()-start)*1000/len(boards)
    per_step = xla_flops(lambda p,s,t,k:step(model,p,s,t,k),params,initial[:1],tokens[:1],key)
    rows,chain_rows = [],[]
    for index,(b,y,info) in enumerate(zip(boards,labels,infos)):
        for d in checkpoints:
            row = {"model":name,"seed":seed,"size":len(b),"generator":generator,"board_id":index,"steps":d,"auto_steps":auto,
                   "trials":1,"noise_sigma":0.,"adaptive":False,"damage":False,
                   "ms":measured_ms[d],"flops":None if per_step is None else per_step*d,
                   "updates":int(firing[:d,index].sum()),**accuracy(b,y,predictions[d-1,index])}
            row["nonfinite_cells"] = int((predictions[d-1,index] == -2).sum())
            rows.append(row)
            if config["task"] == "liberties":
                rows.append({**row,"task_metric":"atari",**accuracy(b,(y == 0).astype(int), (predictions[d-1,index] == 0).astype(int),b != 0)})
            elif config["task"] == "ladders":
                for label in (1,2):
                    rows.append({**row,"task_metric":f"ladder L{label}",**accuracy(b,y,predictions[d-1,index],info["kind"] == label)})
        for ci,chain in enumerate(chains(b)):
            mask = np.zeros(b.shape,bool)
            for p in chain.points:
                mask[p] = True
            d = max(int(info["distance"][p]) for p in chain.points)
            if not np.any(mask&(y >= 0)):
                continue
            solve = solve_times(predictions[:,index],y,np.arange(1,maximum+1),mask)
            lo,hi = distance_bin(max(d,1))
            chain_rows.append({"model":name,"seed":seed,"size":len(b),"generator":generator,"board_id":index,"chain_id":ci,
                "distance":d,"distance_lo":lo,"distance_hi":hi,"t_solve":solve,"efficiency":solve/d if solve is not None and d else None,
                "correct":bool(np.all(predictions[-1,index][mask&(y >= 0)] == y[mask&(y >= 0)])),
                "length":max((int(info.get("length",np.zeros(b.shape))[p]) for p in chain.points)),
                "ladder_kind":max((int(info.get("kind",np.zeros(b.shape))[p]) for p in chain.points)),
                "benson_iterations":info.get("iterations"),"diameter":info.get("diameter")})
    if showcase:
        hidden = np.array(trajectory[3])
        np.savez_compressed(run.path/"viz"/f"{name}_{generator}_{len(boards[0])}.npz",board=boards[0],target=labels[0],
            predictions=predictions[:,0],confidence=confidence[:,0],fire=firing[:,0],states=hidden,steps=np.arange(1,maximum+1),input_channels=model.config.input_channels,output_channels=model.config.output_channels)
    if sweep and name == "nca":
        for sigma in config["noise_sigmas"]:
            trial_predictions,trial_confidence,trial_fires = [],[],[]
            for trial in range(max(config["trials"])):
                trial_key = jax.random.fold_in(key,trial+100)
                trial_initial = initialize(tokens,trial_key,model.config)
                f = compiled_rollout(model,maximum,noise_sigma=sigma)
                _,values = f(params,trial_initial,tokens,trial_key)
                jax.block_until_ready(values)
                trial_predictions.append(np.array(values[0][-1]))
                trial_confidence.append(np.array(values[1][-1]).mean(axis=(1,2)))
                trial_fires.append(np.array(values[2]).sum(axis=(0,2,3)))
            for k in config["trials"]:
                selected = np.argmax(np.stack(trial_confidence[:k]),axis=0)
                for i,(b,y) in enumerate(zip(boards,labels)):
                    rows.append({"model":name,"seed":seed,"size":len(b),"generator":generator,"board_id":i,"steps":maximum,"trials":k,
                        "noise_sigma":sigma,"adaptive":False,"damage":False,"sweep":True,"flops":None if per_step is None else per_step*maximum*k,
                        "updates":int(sum(v[i] for v in trial_fires[:k])),**accuracy(b,y,trial_predictions[selected[i]][i])})
        if showcase:
            for adaptive in (False,True):
                for damage in (False,True):
                    f = compiled_rollout(model,maximum,adaptive=adaptive,damage_step=maximum//2 if damage else -1)
                    _,values = f(params,initial,tokens,key)
                    p,conf,fire = [np.array(v) for v in values]
                    np.savez_compressed(run.path/"viz"/f"repair_{generator}_{len(boards[0])}_{adaptive}_{damage}.npz",board=boards[0],target=labels[0],predictions=p[:,0],confidence=conf[:,0],fire=fire[:,0],steps=np.arange(1,maximum+1),adaptive=adaptive,damage=damage)
                    for d in checkpoints:
                        for i,(b,y) in enumerate(zip(boards,labels)):
                            rows.append({"model":name,"seed":seed,"size":len(b),"generator":generator,"board_id":i,"steps":d,"trials":1,
                                "noise_sigma":0.,"adaptive":adaptive,"damage":damage,"repair":True,"updates":int(fire[:d,i].sum()),**accuracy(b,y,p[d-1,i])})
    return rows,chain_rows


def evaluate_resnet(model,params,boards,labels,infos,config,seed,name,generator):
    inputs = jax.nn.one_hot(jnp.asarray(boards),config["input_channels"])
    function = jax.jit(lambda p,x:model.apply({"params":p},x))
    jax.block_until_ready(function(params,inputs))
    started = time.perf_counter()
    values = function(params,inputs)
    values.block_until_ready()
    milliseconds = (time.perf_counter()-started)*1000/len(boards)
    pred = np.array(jnp.argmax(values,-1))
    flops = xla_flops(lambda p,x:model.apply({"params":p},x),params,inputs[:1])
    rows,chain_rows = [],[]
    for i,(b,y,info) in enumerate(zip(boards,labels,infos)):
        row = {"model":name,"seed":seed,"size":len(b),"generator":generator,"board_id":i,"steps":1,"trials":1,"noise_sigma":0.,"adaptive":False,"damage":False,
            "ms":milliseconds,"flops":flops,"updates":0,"receptive_field_radius":model.receptive_field_radius,**accuracy(b,y,pred[i])}
        rows.append(row)
        if config["task"] == "liberties":
            rows.append({**row,"task_metric":"atari",**accuracy(b,(y == 0).astype(int),(pred[i] == 0).astype(int),b != 0)})
        elif config["task"] == "ladders":
            for label in (1,2):
                rows.append({**row,"task_metric":f"ladder L{label}",**accuracy(b,y,pred[i],info["kind"] == label)})
        for ci,chain in enumerate(chains(b)):
            points = [p for p in chain.points if y[p] >= 0]
            if points:
                d = max(int(info["distance"][p]) for p in points)
                lo,hi = distance_bin(max(1,d))
                chain_rows.append({"model":name,"seed":seed,"size":len(b),"generator":generator,"board_id":i,"chain_id":ci,"distance":d,"distance_lo":lo,"distance_hi":hi,
                    "length":max((int(info.get("length",np.zeros(b.shape))[p]) for p in points)),
                    "ladder_kind":max((int(info.get("kind",np.zeros(b.shape))[p]) for p in points)),"correct":all(pred[i][p] == y[p] for p in points)})
    return rows,chain_rows
