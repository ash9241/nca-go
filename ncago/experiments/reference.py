"""Re-evaluate exact Benson references on an existing, immutable test split."""
import argparse
import json
import time
import numpy as np
import pandas as pd
import yaml
from ncago.go.labels import benson
from ncago.go.rules import chains
from .common import ROOT,Run
from .metrics import accuracy,distance_bin


def run(profile="smoke"):
    sources = []
    for file in (ROOT/"results"/"2").glob("*/summary.json"):
        summary = json.loads(file.read_text())
        if summary.get("profile") == profile and summary.get("pipeline_passed"):
            sources.append((file.parent,summary))
    latest = {}
    for source,summary in sorted(sources):
        latest[summary["seed"]] = source
    if not latest:
        raise RuntimeError("A completed Phase 2 test split is required")
    for seed,source in latest.items():
        config = yaml.safe_load((source/"config.yaml").read_text())
        log = Run("2-reference",{**config,"source_run":str(source.relative_to(ROOT))},seed)
        rows,chainrows = [],[]
        for file in sorted((source/"data").glob("test_*.npz")):
            data = np.load(file)
            generator = file.stem.removeprefix("test_").rsplit("_",1)[0]
            for i,(board,target) in enumerate(zip(data["boards"],data["labels"])):
                started = time.perf_counter()
                prediction,info = benson(board)
                milliseconds = (time.perf_counter()-started)*1000
                np.testing.assert_array_equal(prediction,target)
                yardstick = info["iterations"]*info["diameter"]
                rows.append({"model":"b3","seed":seed,"size":len(board),"generator":generator,"board_id":i,
                    "steps":yardstick,"trials":1,"noise_sigma":0.,"adaptive":False,"damage":False,"ms":milliseconds,**accuracy(board,target,prediction)})
                lo,hi = distance_bin(max(1,yardstick))
                for ci,chain in enumerate(chains(board)):
                    chainrows.append({"model":"b3","seed":seed,"size":len(board),"generator":generator,"board_id":i,
                        "chain_id":ci,"distance":max(1,yardstick),"distance_lo":lo,"distance_hi":hi,
                        "t_solve":yardstick,"efficiency":1. if yardstick else None,"correct":True,
                        "benson_iterations":info["iterations"],"diameter":info["diameter"]})
        if not rows:
            raise RuntimeError("Saved Phase 2 test boards are unavailable")
        pd.DataFrame(rows).to_csv(log.path/"eval"/"boards.csv",index=False)
        pd.DataFrame(chainrows).to_csv(log.path/"eval"/"chains.csv",index=False)
        log.finish("passed",profile=profile,source_run=str(source.relative_to(ROOT)),evaluations=len(rows),chains=len(chainrows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile",choices=["smoke","full"],default="smoke")
    run(parser.parse_args().profile)
