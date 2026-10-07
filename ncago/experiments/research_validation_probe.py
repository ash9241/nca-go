"""Full small-board validation of a saved pilot checkpoint, without training.

This may qualify a recipe while an exploratory pilot continues. It never
opens larger final data and never substitutes for final primary ID checks.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import numpy as np
import jax
from flax import serialization
from .common import Run
from .research_eval import load_run
from .research_train import make_predict, evaluate, metrics, validation_data, stability_assessment


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--checkpoint", default="latest.msgpack")
    p.add_argument("--require-gpu", action="store_true")
    args = p.parse_args()
    if args.require_gpu and not any(d.platform == "gpu" for d in jax.devices()):
        raise RuntimeError("GPU required")
    model, mc, params, config, digest = load_run(args.run, args.checkpoint)
    progress = json.loads((args.run / "progress.json").read_text())
    run = Run("research_validation_probe", dict(source_run=args.run.name,
              checkpoint_sha256=digest, checkpoint=args.checkpoint,
              checkpoint_iteration=progress["iteration"], source_training_config=config,
              selection="9/13 validation only; recipe qualification, not final-test selection"), config["seed"])
    (run.path / "ckpt/probed.msgpack").write_bytes(serialization.to_bytes(params))
    predict = make_predict(model, mc, config["model"] == "resnet")
    results = []
    for size, data in validation_data(config).items():
        depths = (32, 64, 128, 512, 1024)
        for draw in range(8 if mc.identifier_channels else 3):
            pred, dynamics = evaluate(predict, params, data, depths,
                 jax.random.PRNGKey(93001 if mc.identifier_channels else 93001+draw),
                 id_key=jax.random.PRNGKey(94001+draw) if mc.identifier_channels else None)
            np.savez_compressed(run.path / "eval" / f"validation_{size}_draw{draw}.npz", predictions=pred, dynamics=dynamics)
            results.extend(dict(size=size, depth=d, draw=draw, **metrics(y, data[1], mc.classes, config["task"])) for d, y in zip(depths, pred))
    assessed = stability_assessment(results)
    run.finish("complete", source_run=args.run.name, checkpoint_iteration=progress["iteration"],
               checkpoint_sha256=digest, model_config=asdict(mc), results=results, **assessed)
    print(json.dumps(assessed), flush=True)


if __name__ == "__main__":
    main()
