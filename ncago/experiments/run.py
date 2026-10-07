"""Orchestrated reproducible phases with explicit gates and failure artifacts."""
import argparse
import json
import subprocess
import time
from pathlib import Path
import yaml
import jax
from .common import ROOT,Run,write_json,commit_phase
from . import phase0
from .tasks import run_task


def skip(phase,config,reason):
    return Run(phase,config).finish("not run",reason=reason,profile=config["profile"])


def execute(config,phases):
    started = time.perf_counter()
    profile = config["profile"]
    if profile == "full":
        smoke = ROOT/"results"/"smoke_pipeline.json"
        if not smoke.exists() or json.loads(smoke.read_text()).get("status") != "passed":
            raise RuntimeError("Run make smoke successfully before full")
        if not any(d.platform == "gpu" for d in jax.devices()):
            for phase in phases:
                skip(phase,config,"full profile requires a JAX GPU; detected CPU only")
            from ncago.report.build import build
            build(profile=profile)
            return
    task_models = []
    phase_paths = {}
    full_gate = True
    for phase in phases:
        print(f"=== phase {phase} ({profile}) ===",flush=True)
        if not full_gate:
            skip(phase,config,"G1 ID accuracy gate failed; debug liberties before later full phases")
            continue
        if phase == "0":
            phase0.run(config["crosscheck_games"])
        elif phase in ("1","2","3"):
            task = {"1":"liberties","2":"benson","3":"ladders"}[phase]
            for seed in config["seeds"]:
                path,models,gate = run_task(task,config,seed)
                phase_paths[(task,seed)] = path
                if task in ("liberties","benson"):
                    task_models.append((task,seed,models))
                if phase == "1" and profile == "full" and not gate:
                    full_gate = False
                    break
        elif phase == "4a":
            from .phase4 import run,restore_models
            if not task_models:
                for task,p in (("liberties","1"),("benson","2")):
                    found = []
                    for s in (ROOT/"results"/p).glob("*/summary.json"):
                        payload = json.loads(s.read_text())
                        if payload.get("profile") == profile and payload.get("pipeline_passed"):
                            found.append((s,payload))
                    for seed in config["seeds"]:
                        candidates = [s for s,payload in found if payload["seed"] == seed]
                        if candidates:
                            path = sorted(candidates)[-1].parent
                            task_models.append((task,seed,restore_models(path,{**config,"task":task})))
            if task_models:
                run(config,task_models)
            else:
                skip(phase,config,"Phase 1 and 2 trained checkpoints unavailable")
        elif phase == "5":
            from .player import run_player
            run_player(config)
        elif phase == "4b":
            from .adversarial import run_adversarial
            run_adversarial(config)
        else:
            raise ValueError(f"Unknown phase {phase}")
        if config.get("commit_phases"):
            subprocess.run([str(ROOT/".venv"/"bin"/"python"),"-m","pytest","-q"],cwd=ROOT,check=True)
            from ncago.report.build import build
            build(profile=profile)
            commit_phase(phase)
    from ncago.report.build import build
    build(profile=profile)
    elapsed = time.perf_counter()-started
    if profile == "smoke" and set(phases) >= {"0","1","2","3","4a"}:
        write_json(ROOT/"results"/"smoke_pipeline.json",{"status":"passed" if elapsed <= 1800 else "time_budget_failed",
            "wall_seconds":elapsed,"profile":profile,"phases":phases,"accuracy_gate_certified":False})
        if elapsed > 1800:
            raise RuntimeError(f"Smoke exceeded CPU budget: {elapsed:.1f} seconds")
    print(f"Pipeline finished in {elapsed:.2f} seconds",flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile",choices=["smoke","full"],default="smoke")
    parser.add_argument("--config")
    parser.add_argument("--readout",choices=["mse","ce"])
    parser.add_argument("--normalization-groups",type=int)
    parser.add_argument("--phases",nargs="+",default=["0","1","2","3","4a"])
    args = parser.parse_args()
    file = ROOT/"configs"/f"{args.profile}.yaml" if not args.config else Path(args.config)
    config = yaml.safe_load(file.read_text())
    if args.readout:
        config["readout"] = args.readout
    if args.normalization_groups is not None:
        config["normalization_groups"] = args.normalization_groups
    execute(config,args.phases)


if __name__ == "__main__":
    main()
