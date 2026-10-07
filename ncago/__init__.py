"""Go cellular automata research, with explicit evidence provenance."""
from pathlib import Path
import os

# Keep all compiler and rendering caches inside the project.
_cache = Path(__file__).resolve().parents[1]/".cache"
os.environ.setdefault("JAX_COMPILATION_CACHE_DIR",str(_cache/"jax"))
os.environ.setdefault("JAX_PERSISTENT_CACHE_MIN_COMPILE_TIME_SECS","0")
os.environ.setdefault("MPLCONFIGDIR",str(_cache/"matplotlib"))
os.environ.setdefault("NUMBA_CACHE_DIR",str(_cache/"numba"))
os.environ.setdefault("XDG_CACHE_HOME",str(_cache))
