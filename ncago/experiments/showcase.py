"""Specified examples are held out and never affect checkpoint selection."""
import numpy as np
import pandas as pd
from ncago.go.generators import structured,random_position,living,ladder_position
from ncago.go.rules import legalize
from .tasks import labeled
from .evaluate import evaluate_nca


def longest_snake(size):
    b = np.zeros((size,size),np.int8)
    for i,r in enumerate(range(1,size-1,2)):
        b[r,1:size-1] = 1
        if i and r > 1:
            b[r-1,1 if i % 2 else size-2] = 1
    return b


def run_showcases(task,model,params,config,seed,run):
    rng = np.random.default_rng(50000+seed)
    if task == "liberties":
        examples = [("longest_snake",longest_snake(37)),("ring",structured(37,rng,"ring")),
            ("spiral",structured(25,rng,"spiral")),("dense_random",random_position(19,rng,.75)),
            ("comb",structured(13,rng,"comb")),("random_game",random_position(9,rng))]
    elif task == "benson":
        examples = [("benson_two_eyes",living(19,rng,True))]
    else:
        b = np.zeros((19,19),np.int8)
        b[2,2] = 1
        b[1,2] = b[1,3] = b[2,1] = 2
        examples = [("ladder_diagonal",b)]
    rows = []
    for name,board in examples:
        boards = board[None]
        labels,infos = labeled(task,boards,config)
        rr,_ = evaluate_nca(model,params,boards,labels,infos,config,seed,"nca",name,run,showcase=True,sweep=False)
        rows.extend(rr)
    pd.DataFrame(rows).to_csv(run.path/"eval"/"showcases.csv",index=False)
