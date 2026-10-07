"""Inspect local hardware and optional executables without global installation."""
import shutil
import subprocess
from pathlib import Path
from .common import ROOT, hardware, write_json


def main():
    info = hardware()
    info["optional"] = {}
    for program in ("katago", "gnugo"):
        executable = shutil.which(program)
        info["optional"][program] = {"path": executable}
        if executable:
            result = subprocess.run([executable,"version" if program == "katago" else "--version"], text=True, capture_output=True, timeout=15)
            info["optional"][program]["version"] = (result.stdout+result.stderr).strip()
    write_json(ROOT/"results"/"environment.json", info)
    print(info, flush=True)


if __name__ == "__main__":
    main()
