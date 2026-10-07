from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import time
import subprocess
import yaml
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def hardware():
    import jax
    return {"system": platform.platform(), "processor": platform.processor(),
            "python": platform.python_version(), "jax": jax.__version__,
            "devices": [str(d) for d in jax.devices()]}


def jsonable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=jsonable, allow_nan=False)+"\n")


class Run:
    def __init__(self, phase, config, seed=0):
        self.start = time.perf_counter()
        self.config = config
        self.hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.path = ROOT/"results"/str(phase)/f"{now}_{self.hash[:8]}_s{seed}"
        self.path.mkdir(parents=True)
        for name in ("eval", "viz", "ckpt", "data"):
            (self.path/name).mkdir()
        (self.path/"config.yaml").write_text(yaml.safe_dump(config, sort_keys=True))
        self.metadata = {"phase": str(phase), "seed": seed, "config_hash": self.hash,
                         "hardware": hardware(), "created_utc": now}
        try:
            self.metadata["commit"] = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
        except subprocess.CalledProcessError:
            revision_file = ROOT/"SOURCE_REVISION"
            self.metadata["commit"] = revision_file.read_text().strip() if revision_file.exists() else None
        write_json(self.path/"metadata.json", self.metadata)

    def log(self, **values):
        with (self.path/"metrics.jsonl").open("a") as stream:
            stream.write(json.dumps(values, default=jsonable, allow_nan=False)+"\n")

    def finish(self, status, **metrics):
        payload = {**self.metadata, "status": status,
                   "wall_seconds": time.perf_counter()-self.start, **metrics}
        write_json(self.path/"summary.json", payload)
        self.log(event="finished", **payload)
        log = ROOT/"RESULTS_LOG.md"
        if not log.exists():
            log.write_text("# Results log\n\nAll metrics below are emitted by measured runs.\n")
        with log.open("a") as stream:
            stream.write(f"\n## {self.path.relative_to(ROOT)}\n\n```json\n{json.dumps(payload, indent=2, default=jsonable, allow_nan=False)}\n```\n")
        return payload


def commit_phase(phase):
    """Commit only this project's explicitly staged deliverables after tests pass."""
    subprocess.run(["git","add","ncago","tests","configs","reports","results","README.md","DECISIONS.md","RESULTS_LOG.md","SPECIFICATION.md","Makefile","pyproject.toml",".gitignore"], cwd=ROOT, check=True)
    changed = subprocess.run(["git","diff","--cached","--quiet"], cwd=ROOT)
    if changed.returncode == 1:
        subprocess.run(["git","commit","-m",f"Record phase {phase} implementation and measured status"], cwd=ROOT, check=True)
