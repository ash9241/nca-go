PYTHON ?= python
export MPLCONFIGDIR := $(CURDIR)/.cache/matplotlib
export NUMBA_CACHE_DIR := $(CURDIR)/.cache/numba

.PHONY: install test figures verify
install:
	$(PYTHON) -m pip install -e .
test:
	$(PYTHON) -m pytest -q
figures:
	$(PYTHON) tools/published_results.py
verify:
	$(PYTHON) tools/verify_saved_results.py
