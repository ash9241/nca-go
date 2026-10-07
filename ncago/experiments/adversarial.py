"""Find cyclic groups that disappear later in supplied FAR game records."""
from pathlib import Path
import os
import json
import numpy as np
import pandas as pd
from ncago.go.sgfio import read_sgf
from ncago.go.rules import chains,neighbors
from ncago.go.engines import KataAnalysis,teacher_arrays
from .common import ROOT,Run
from .player import dependencies


def doomed_groups(positions):
    events = []
    for capture_turn in range(1,len(positions)):
        before,after = positions[capture_turn-1].board,positions[capture_turn].board
        for chain in chains(before):
            points = set(chain.points)
            edges = sum(sum(q in points for q in neighbors(p,len(before))) for p in points)//2
            if edges < len(points):
                continue
            if all(after[p] != chain.color for p in points):
                for turn in range(max(0,capture_turn-30),capture_turn):
                    doomed = [p for p in points if positions[turn].board[p] == chain.color]
                    if doomed:
                        events.append((turn,capture_turn,chain.color,doomed))
    return events


def run_adversarial(config):
    run = Run("4b",config)
    binary,network,_,reasons = dependencies()
    directory = Path(os.environ.get("NCAGO_FAR_SGFS",str(ROOT/"tools"/"far_sgfs")))
    files = sorted(directory.glob("**/*.sgf")) if directory.exists() else []
    if not files:
        reasons.append("FAR adversarial SGFs unavailable; no substitute games used")
    models = list((ROOT/"results"/"5").glob("*/ckpt/player.msgpack"))
    if not models:
        reasons.append("Phase 5 player checkpoint unavailable")
    if reasons:
        return run.finish("not run",profile=config["profile"],reason="; ".join(reasons))
    from flax import serialization
    from ncago.nca.model import ModelConfig
    from ncago.nca.player import PlayerNCA,inputs,initialize,rollout
    import jax
    import jax.numpy as jnp
    path = sorted(models)[-1]
    mc = ModelConfig(**json.loads((path.parent.parent/"player_model.json").read_text()))
    model = PlayerNCA(mc)
    key = jax.random.PRNGKey(0)
    template = model.init(key,jnp.zeros((1,19,19,mc.channels)))["params"]
    params = serialization.from_bytes(template,path.read_bytes())
    rows = []
    with KataAnalysis([binary,"analysis","-config",str(ROOT/"configs"/"analysis.cfg"),"-model",network],run.path/"teacher.log") as engine:
        for file in files:
            positions = read_sgf(file)
            for turn,capture,color,points in doomed_groups(positions):
                position = positions[turn]
                for visits in (1,1000):
                    reply = engine.analyze(position,visits=visits)
                    _,own,_,_ = teacher_arrays(reply,len(position.board))
                    values = np.array([own[p] for p in points])*(1 if color == 1 else -1)
                    rows.append({"file":str(file),"turn":turn,"capture_turn":capture,"model":f"KataGo_{visits}","mean_victim_ownership":float(values.mean()),"fraction_victim_owned":float((values > 0).mean()),"points":len(points)})
                features = jnp.asarray(inputs(position))[None]
                state = initialize(features,key,mc)
                _,out = rollout(model,params,state,features,key,max(config["evaluation_steps"]),noise=False,keep_history=False)
                own = np.asarray(out[1][0])
                values = np.array([own[p] for p in points])*(1 if color == 1 else -1)
                rows.append({"file":str(file),"turn":turn,"capture_turn":capture,"model":"nca","mean_victim_ownership":float(values.mean()),"fraction_victim_owned":float((values > 0).mean()),"points":len(points)})
    if not rows:
        return run.finish("not run",profile=config["profile"],reason="Supplied FAR SGFs contained no eligible doomed cyclic groups")
    pd.DataFrame(rows).to_csv(run.path/"eval"/"adversarial.csv",index=False)
    return run.finish("passed",profile=config["profile"],evaluations=len(rows))


if __name__ == "__main__":
    from .phase_cli import task_main
    task_main("4b")
