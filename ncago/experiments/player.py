"""KataGo distillation is runnable when an engine and teacher network exist."""
from functools import partial
from pathlib import Path
import json
import os
import shutil
import time
import numpy as np
import pandas as pd
import jax
import jax.numpy as jnp
import optax
from flax import serialization
from ncago.go.rules import Position,IllegalMove
from ncago.go.engines import KataAnalysis,GTP,teacher_arrays,parse_coordinate,coordinate
from ncago.go.sgfio import write_sgf
from ncago.nca.model import ModelConfig
from ncago.nca.player import PlayerNCA,initialize,rollout,inputs,PUCT,Node
from .common import ROOT,Run,write_json
from .metrics import wilson


def dependencies():
    manifest = ROOT/"results"/"optional_dependencies.json"
    recorded = json.loads(manifest.read_text()) if manifest.exists() else {}
    binary = os.environ.get("NCAGO_KATAGO") or shutil.which("katago") or recorded.get("katago",{}).get("path")
    network = os.environ.get("NCAGO_KATAGO_MODEL") or recorded.get("model",{}).get("path")
    gnugo = os.environ.get("NCAGO_GNUGO") or shutil.which("gnugo")
    reasons = []
    if not binary:
        reasons.append(recorded.get("katago",{}).get("reason","KataGo executable unavailable"))
    if not network or not Path(network).is_file():
        reasons.append("KataGo teacher network unavailable")
    return binary,network,gnugo,reasons


def dataset(engine,size,count,seed,run,search_subset=10,exclude=()):
    rng = np.random.default_rng(seed)
    features,policies,ownership,scores,wins,next_features = [],[],[],[],[],[]
    next_policy,next_ownership,next_score,next_win = [],[],[],[]
    seen,attempts = set(exclude),0
    while len(features) < count:
        attempts += 1
        if attempts > count*50:
            raise RuntimeError("Teacher dataset failed to produce enough unique positions")
        position = Position.empty(size)
        history = []
        game = []
        opening = int(rng.integers(2,7))
        for turn in range(2*size*size):
            if position.passes == 2:
                break
            if turn < opening:
                legal = position.legal_moves()
                point = legal[int(rng.integers(max(1,len(legal)-1)))]
            else:
                reply = engine.analyze(position,history,visits=int(rng.integers(16,65)))
                point = parse_coordinate(reply["moveInfos"][0]["move"],size)
            child = position.play(point)
            if turn >= opening and position.digest() not in seen:
                game.append((position,tuple(history),child,point))
            history.append((position.to_move,point))
            position = child
        rng.shuffle(game)
        for position,history,child,point in game:
            if len(features) >= count:
                break
            if position.digest() in seen:
                continue
            reply = engine.analyze(position,history,visits=1)
            policy,own,score,win = teacher_arrays(reply,size)
            features.append(inputs(position,[p for _,p in history]))
            next_features.append(inputs(child,[p for _,p in history]+[point]))
            policies.append(policy)
            ownership.append(own)
            scores.append(score)
            wins.append(win)
            child_reply = engine.analyze(child,history+((position.to_move,point),),visits=1)
            cp,co,cs,cw = teacher_arrays(child_reply,size)
            next_policy.append(cp)
            next_ownership.append(co)
            next_score.append(cs)
            next_win.append(cw)
            seen.add(position.digest())
            if len(features) <= search_subset:
                searched = engine.analyze(position,history,visits=400)
                run.log(event="teacher_search_subset",size=size,position_hash=position.digest(),reply=searched)
    return tuple(np.asarray(v,np.float32) for v in (features,policies,ownership,scores,wins,next_features,next_policy,next_ownership,next_score,next_win))


def train(model,data,config,seed,run):
    key = jax.random.PRNGKey(seed)
    rng = np.random.default_rng(seed)
    features,policy,own,score,win,child,child_policy,child_own,child_score,child_win = data
    batch = config["batch_size"]
    ids = rng.integers(len(features),size=4*batch)
    advanced_pool = np.zeros(len(ids),bool)
    state = np.array(initialize(jnp.asarray(features[ids]),key,model.config))
    params = model.init(key,jnp.asarray(state[:batch]))["params"]
    ema = params
    opt = optax.chain(optax.clip_by_global_norm(1),optax.adamw(config["learning_rate"]))
    optim = opt.init(params)
    steps = config["rollout_steps"]
    weights = config.get("player_loss_weights",{"policy":1.,"ownership":1.,"score":.001,"winrate":1.})
    @jax.jit
    def update(params,optim,ema,states,x,p,y,s,w,key):
        def loss(params):
            final,values = rollout(model,params,states,x,key,steps)
            logits,ownership,win_logits = values[:3]
            policy_loss = jnp.sum(jnp.where(p > 0,p*(jnp.log(jnp.maximum(p,1e-8))-jax.nn.log_softmax(logits)),0),axis=-1).mean()
            ownership_loss = ((ownership-y)**2).mean()
            score_prediction = ownership.sum(axis=(-2,-1))-100*x[...,8].mean(axis=(-2,-1))
            score_loss = ((score_prediction-s)**2).mean()
            win_loss = optax.sigmoid_binary_cross_entropy(win_logits,w).mean()
            value = weights["policy"]*policy_loss+weights["ownership"]*ownership_loss+weights["score"]*score_loss+weights["winrate"]*win_loss
            return value,final
        (value,final),grad = jax.value_and_grad(loss,has_aux=True)(params)
        changes,optim = opt.update(grad,optim,params)
        params = optax.apply_updates(params,changes)
        ema = jax.tree_util.tree_map(lambda a,b:config["ema"]*a+(1-config["ema"])*b,ema,params)
        return params,optim,ema,final,value
    for iteration in range(config["training_steps"]):
        selected = rng.choice(len(ids),batch,replace=False)
        reseed = rng.random(batch) < .25
        ids[selected[reseed]] = rng.integers(len(features),size=reseed.sum())
        advanced_pool[selected[reseed]] = False
        current = ids[selected]
        x = features[current].copy()
        targets = [a[current].copy() for a in (policy,own,score,win)]
        states = state[selected].copy()
        states[reseed] = np.array(initialize(jnp.asarray(x[reseed]),jax.random.fold_in(key,iteration),model.config))
        advance = advanced_pool[selected] | (rng.random(batch) < .1)
        advanced_pool[selected] = advance
        x[advance] = child[current[advance]]
        for target,next_target in zip(targets,(child_policy,child_own,child_score,child_win)):
            target[advance] = next_target[current[advance]]
        # Replay retains hidden state while inputs and all teacher targets advance.
        transforms = []
        for i in range(batch):
            rotation,reflection = int(rng.integers(4)),bool(rng.integers(2))
            transforms.append((rotation,reflection))
            def transform(a):
                a = np.rot90(a,rotation,axes=(0,1))
                return (a[::-1] if reflection else a).copy()
            states[i],x[i],targets[1][i] = map(transform,(states[i],x[i],targets[1][i]))
            targets[0][i,:-1] = transform(targets[0][i,:-1].reshape(x.shape[1:3])).ravel()
            if config.get("damage",True) and rng.random() < .1:
                rr,cc = np.ogrid[:x.shape[1],:x.shape[2]]
                for _ in range(int(rng.integers(1,4))):
                    cy,cx = rng.uniform(0,x.shape[1]),rng.uniform(0,x.shape[2])
                    radius = rng.uniform(.1,.4)*x.shape[2]
                    states[i,(rr-cy)**2+(cc-cx)**2 <= radius**2,model.config.input_channels:] = 0
        states[...,:model.config.input_channels] = x
        params,optim,ema,final,value = update(params,optim,ema,jnp.asarray(states),jnp.asarray(x),*[jnp.asarray(t) for t in targets],jax.random.fold_in(key,iteration+1))
        if not np.isfinite(float(value)):
            raise FloatingPointError("Nonfinite player loss")
        restored = np.array(final)
        for i,(rotation,reflection) in enumerate(transforms):
            if reflection:
                restored[i] = restored[i,::-1].copy()
            restored[i] = np.rot90(restored[i],-rotation,axes=(0,1))
        state[selected] = restored
        if iteration % max(1,config["training_steps"]//10) == 0:
            run.log(event="player_train",step=iteration+1,loss=float(value))
    return ema


def matches(model,params,mc,config,run,binary,network,gnugo):
    if not gnugo:
        return "not run: GnuGo unavailable for opponent games and dead-stone scoring"
    key = jax.random.PRNGKey(7000)
    horizon = max(config["evaluation_steps"])
    infer = jax.jit(partial(rollout,model,steps=horizon,noise=False,adaptive=True,keep_history=False))
    def evaluate(position,state,recent):
        features = jnp.asarray(inputs(position,recent))[None]
        initial = initialize(features,key,mc,state)
        final,values = infer(params,initial,features,key)
        policy = np.asarray(jax.nn.softmax(values[0][0]))
        win = float(jax.nn.sigmoid(values[2][0]))
        return policy,win,final
    records = []
    with GTP([gnugo,"--mode","gtp","--level","10","--chinese-rules","--komi","7.5"],run.path/"gnugo.log") as opponent, KataAnalysis([binary,"analysis","-config",str(ROOT/"configs"/"analysis.cfg"),"-model",network],run.path/"match_katago.log") as anchor:
        for size in (9,19):
            # Equal wall-clock caps compare warm and cold start. Actual times are logged.
            for opponent_name in ("GnuGo","KataGo_raw"):
                for visits in config["player_visits"]:
                    for warm in (False,True):
                        for game_index in range(config["player_games"]):
                            color = 1 if game_index % 2 == 0 else 2
                            position = Position.empty(size)
                            root = Node(position)
                            search = PUCT(evaluate,warm=warm)
                            history = []
                            spent = 0.
                            capped = False
                            opponent.command(f"boardsize {size}")
                            opponent.command("clear_board")
                            opponent.command("komi 7.5")
                            for turn in range(2*size*size):
                                if position.passes >= 2:
                                    break
                                if position.to_move == color:
                                    start = time.perf_counter()
                                    point,child = search.search(root,visits,time_limit=config.get("match_seconds_per_move",1.))
                                    spent += time.perf_counter()-start
                                    root = child
                                    opponent.command(f"play {'B' if color == 1 else 'W'} {coordinate(point)}")
                                elif opponent_name == "GnuGo":
                                    point = parse_coordinate(opponent.command(f"genmove {'B' if position.to_move == 1 else 'W'}"),size)
                                    root = Node(position.play(point),state=root.state if warm else None,recent=(root.recent+(point,))[-5:])
                                else:
                                    reply = anchor.analyze(position,history,visits=1)
                                    point = parse_coordinate(reply["moveInfos"][0]["move"],size)
                                    opponent.command(f"play {'B' if position.to_move == 1 else 'W'} {coordinate(point)}")
                                    root = Node(position.play(point),state=root.state if warm else None,recent=(root.recent+(point,))[-5:])
                                history.append((position.to_move,point))
                                position = position.play(point)
                            else:
                                capped = True
                            dead_text = opponent.command("final_status_list dead")
                            scored = Position(position.board.copy())
                            for token in dead_text.split():
                                point = parse_coordinate(token,size)
                                if point is not None:
                                    scored.board[point] = 0
                            lead = scored.score()
                            won = lead > 0 if color == 1 else lead < 0
                            record = {"size":size,"opponent":opponent_name,"visits":visits,"warm":warm,"game":game_index,"color":color,"won":won,
                                "black_score":lead,"moves":len(history),"capped":capped,"nca_seconds":spent}
                            records.append(record)
                            write_sgf(run.path/"data"/f"match_{size}_{opponent_name}_{visits}_{warm}_{game_index}.sgf",size,history)
                            run.log(event="match",**record)
    frame = pd.DataFrame(records)
    frame.to_csv(run.path/"eval"/"games.csv",index=False)
    summary = []
    for key,part in frame.groupby(["size","opponent","visits","warm"]):
        wins,games = int(part.won.sum()),len(part)
        low,high = wilson(wins,games)
        rate = wins/games
        elo = 400*np.log10(rate/(1-rate)) if 0 < rate < 1 else None
        summary.append({"size":key[0],"opponent":key[1],"visits":key[2],"warm":key[3],"wins":wins,"games":games,"winrate":rate,"ci_low":low,"ci_high":high,"elo_difference":elo})
    pd.DataFrame(summary).to_csv(run.path/"eval"/"matches.csv",index=False)
    return "passed"


def warm_start(model,params,mc,data,config,run,size):
    features,_,_,_,_,child = data[:6]
    key = jax.random.PRNGKey(8000+size)
    maximum = max(config["evaluation_steps"])
    function = jax.jit(partial(rollout,model,steps=maximum,noise=False,adaptive=True))
    rows = []
    limit = min(len(features),config.get("warm_positions",200))
    batch = config.get("evaluation_batch_size",4)
    terminal = jax.jit(partial(rollout,model,steps=maximum,noise=False,adaptive=True,keep_history=False))
    for start in range(0,limit,batch):
        stop = min(start+batch,limit)
        x,next_x = jnp.asarray(features[start:stop]),jnp.asarray(child[start:stop])
        local_key = jax.random.fold_in(key,start)
        parent,_ = terminal(params,initialize(x,local_key,mc),x,local_key)
        reference = None
        for warm in (False,True):
            initial = initialize(next_x,local_key,mc,parent if warm else None)
            _,values = function(params,initial,next_x,local_key)
            policies,ownership,_,fire = [np.asarray(v) for v in values]
            if reference is None:
                reference = ownership[-1],policies[-1].argmax(-1)
            error = ((ownership-reference[0])**2).mean(axis=(-2,-1))
            correct = (error <= config.get("warm_tolerance",.01)) & (policies.argmax(-1) == reference[1])
            for i in range(len(next_x)):
                stable = np.logical_and.accumulate(correct[::-1,i])[::-1]
                solved = np.flatnonzero(stable)
                rows.append({"size":size,"position":start+i,"warm":warm,"t_reconverge":int(solved[0]+1) if len(solved) else None,
                    "final_ownership_mse_to_cold":float(error[-1,i]),"updates":int(fire[:,i].sum())})
            if start == 0:
                np.savez_compressed(run.path/"viz"/f"warm_{size}_{warm}.npz",features=np.asarray(next_x[:3]),fire=fire[:,:3],ownership=ownership[:,:3],steps=np.arange(1,maximum+1))
    pd.DataFrame(rows).to_csv(run.path/"eval"/f"warm_{size}.csv",index=False)
    run.log(event="warm_definition",size=size,positions=limit,ownership_mse_tolerance=config.get("warm_tolerance",.01),policy_reference="final cold top-1",persistence="all remaining logged steps")


def run_player(config):
    run = Run("5",config)
    binary,network,gnugo,reasons = dependencies()
    if reasons:
        return run.finish("not run",profile=config["profile"],reason="; ".join(reasons))
    mc = ModelConfig(channels=max(32,config["channels"]),input_channels=10,output_channels=4,heads=config["heads"])
    model = PlayerNCA(mc)
    key = jax.random.PRNGKey(0)
    rows = []
    with KataAnalysis([binary,"analysis","-config",str(ROOT/"configs"/"analysis.cfg"),"-model",network],run.path/"teacher.log") as engine:
        # A Black stone with exclusive area verifies the explicitly Black perspective.
        fixture = Position.empty(9)
        fixture.board[0:3,0:3] = 1
        result = engine.analyze(fixture,visits=32)
        _,own,_,_ = teacher_arrays(result,9)
        if own[0,0] <= 0:
            raise AssertionError("Teacher ownership perspective fixture failed")
        run.log(event="perspective_fixture",black_corner_ownership=float(own[0,0]),reportAnalysisWinratesAs="BLACK")
        train_data = dataset(engine,9,config["player_positions"],2100,run)
        training_hashes = set()
        for features in train_data[0]:
            color = 1 if features[0,0,9] > 0 else 2
            stones = np.zeros(features.shape[:2],np.int8)
            stones[features[...,0] > .5] = color
            stones[features[...,1] > .5] = 3-color
            training_hashes.add(Position(stones,to_move=color).digest())
        params = train(model,train_data,config,0,run)
        (run.path/"ckpt"/"player.msgpack").write_bytes(serialization.to_bytes(params))
        write_json(run.path/"player_model.json",mc.__dict__)
        for size in (9,13,19):
            count = config.get("player_evaluation_counts",{}).get(size,20000 if config["profile"] == "full" and size != 9 else config["validation_count"])
            data = dataset(engine,size,count,3100+size,run,exclude=training_hashes if size == 9 else ())
            np.savez_compressed(run.path/"data"/f"teacher_{size}.npz",**dict(zip(("features","policy","ownership","score","winrate","next_features","next_policy","next_ownership","next_score","next_winrate"),data)))
            for d in config["evaluation_steps"]:
                function = jax.jit(partial(rollout,model,steps=d,noise=False,keep_history=False))
                features,policy,ownership,score,wins,child = data[:6]
                statistics,elapsed = [],0.
                for start in range(0,count,config.get("evaluation_batch_size",4)):
                    x = jnp.asarray(features[start:start+config.get("evaluation_batch_size",4)])
                    initial = initialize(x,jax.random.fold_in(key,start),mc)
                    jax.block_until_ready(function(params,initial,x,key))
                    began = time.perf_counter()
                    _,values = function(params,initial,x,key)
                    jax.block_until_ready(values)
                    elapsed += time.perf_counter()-began
                    logits,own,win,fire = [np.asarray(v) for v in values]
                    predpolicy = np.asarray(jax.nn.softmax(jnp.asarray(logits)))
                    p,y,s = policy[start:start+len(x)],ownership[start:start+len(x)],score[start:start+len(x)]
                    statistics.append(np.stack([(p.argmax(-1) == logits.argmax(-1)).astype(float),
                        np.sum(p*(np.log(np.maximum(p,1e-8))-np.log(np.maximum(predpolicy,1e-8))),axis=-1),
                        ((own-y)**2).mean(axis=(-2,-1)),np.abs(own.sum(axis=(-2,-1))-7.5-s)],axis=1))
                    if size == 19 and start == 0:
                        np.savez_compressed(run.path/"viz"/f"ownership_{d}.npz",teacher=y[:3],student=own[:3],features=np.asarray(x[:3]))
                means = np.concatenate(statistics).mean(axis=0)
                row = {"size":size,"steps":d,"top1_agreement":float(means[0]),"policy_kl":float(means[1]),
                    "ownership_mse":float(means[2]),"score_mae":float(means[3]),"ms":elapsed*1000/count}
                rows.append(row)
                run.log(event="player_eval",**row)
            warm_start(model,params,mc,data,config,run,size)
    pd.DataFrame(rows).to_csv(run.path/"eval"/"player.csv",index=False)
    match_status = matches(model,params,mc,config,run,binary,network,gnugo)
    return run.finish("passed",profile=config["profile"],evaluations=len(rows),match_status=match_status)


if __name__ == "__main__":
    from .phase_cli import task_main
    task_main("5")
