# Reproduce and audit

The release distinguishes three levels: regenerate presentation from committed measurements; rescore raw predictions without training; rerun neural inference or training. The original checkpoint/data hashes and seeds are retained. Cross-hardware bitwise equality is not promised.

## Install and check the code

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pytest -q
python tools/published_results.py
```

Python 3.12 is also supported. The packaging file pins JAX, Flax, Optax, NumPy, and the other dependencies. `requirements.lock.txt` records the original CPU environment; `pip install -e .` is the portable installation path. The public export's full test suite passed 74 tests before publication.

For Linux/NVIDIA training:

```bash
python -m pip install 'jax[cuda12]==0.6.2'
python -c 'import jax; print(jax.devices())'
```

The recorded GPU experiments used A100 accelerators. Tests and independent scoring work on CPU. Large-maze neural evaluation can be expensive because 201×201 runs use 13,000 steps.

## Download and verify the frozen evidence

Download the three archives and `SHA256SUMS` from [v1.0.0](https://github.com/ash9241/nca-go/releases/tag/v1.0.0), or use GitHub CLI:

```bash
mkdir -p downloads
gh release download v1.0.0 --repo ash9241/nca-go --dir downloads
cd downloads
shasum -a 256 -c SHA256SUMS
cd ..
python tools/verify_archives.py downloads/go-evaluation-v1.zip downloads/maze-control-v1.zip downloads/measurements-v1.zip
unzip -q downloads/go-evaluation-v1.zip -d .
unzip -q downloads/maze-control-v1.zip -d .
```

Each archive has its own `PUBLIC_MANIFEST.json`. Extracting the second archive replaces that manifest, so verify each ZIP before extraction. The original weights, arrays, and measured numbers are unchanged. Workspace prefixes were made relative; machine account inventory and operational logs were omitted. Nested source archives retain the original Python code; their editable-install paths and tar owner metadata are sanitized. Both original and public archive hashes are recorded in `results/published/source_archive_redactions.json`. Historical source revision IDs predate this public repository.

The archive of measurements includes historical appendices and duplicate figures. Extract it into a separate directory when reading the appendices:

```bash
mkdir -p complete-measurements
unzip -q downloads/measurements-v1.zip -d complete-measurements
```

Its `reports/research_followup/RESULTS.json`, `pair_members.csv`, and `confusions.json` contain the complete final measurement record, beyond the compact tables in Git. Historical prose reflects earlier stages; the repository README defines the final interpretation.

## Independently rescore predictions

After extracting the Go and maze archives into the repository root:

```bash
python tools/verify_saved_results.py
python -m ncago.experiments.research_media_audit
python -m ncago.experiments.research_completion
python -m ncago.experiments.maze_control_report
```

The first command checks all 27 Go headline macro scores, raw confusion matrices, and primary witness-pair scores at 37×37 and ratio 4; it also checks 24 large-maze inference trials and 12 small-maze qualifications. It uses NumPy and JSON, without a learned model. The next two check the 15 Go animation traces, all final data/checkpoint hashes, and cohort completeness. The maze command independently rechecks predictions and rebuilds its plots and three animations. These commands write audit records and report files locally.

## Rerun final Go inference

Use a separate copy of the extracted evidence, because fresh evaluations should not be pooled with the originals. This example uses the first main NCA checkpoint:

```bash
python -m ncago.experiments.research_eval evaluate \
  --runs results/research_training/20261007T025650760669Z_1434950c_s0 \
  --namespace sealed_main_cap4_20261007 --draws 8
```

The evaluator verifies the frozen data and checkpoint hashes, then creates a new timestamped evaluation directory. It does not retrain. All 27 checkpoint identities and namespaces are in [final_cohorts.json](../results/published/final_cohorts.json). Eight ID/firing draws are used for ID models; the no-ID model uses three firing draws. Compare the newly produced predictions to the released records without replacing the original records. The completion audit expects one original evaluation per model; run it before producing duplicate evaluations.

## Train the final Go recipe

Run each seed 0, 1, and 2 on a GPU:

```bash
python -m ncago.experiments.research_train \
  --config configs/research_ids32_rescue.json \
  --seed 0 --steps 30000 --require-gpu
```

Replace the seed for independent repetitions. Architecture overrides are `--model resnet`, `--model rcnn`, `--model gnn_sum`, and `--model gnn_max`; use `--ids 0` for the reserved-capacity no-ID NCA. Data seeds remain fixed to preserve matched examples. Inspect `config.yaml`, `model.json`, `summary.json`, and qualification metrics in each generated run. The historical `research_qualification` tool documents the original cohort check; new confirmatory evaluations must qualify **every** model independently. Do not reuse already opened final boards to select new recipes.

The Go release does not contain every pilot's full optimizer/replay state. It supports checking final inference, regenerating data streams from code/config, and new training runs. A bitwise replay of the entire exploratory history is outside its scope.

## Train the maze control

The maze asset includes the converted public data and provenance. It preserves the upstream MIT notice. Source archives are the University of Maryland's `Easy_to_Hard_Datav2/maze_data_{train|test}_{size}.tar.gz`; conversion code is `maze_control convert` and validates logical-cell blocks and labels with BFS.

```bash
python -m ncago.experiments.maze_control train \
  --train results/maze_data/train_9.npz --validation results/maze_data/test_9.npz \
  --seed 0 --updates 5000 --batch 64 --validation-count 512
```

Replace `NEW_RUN` below with the newly printed run directory:

```bash
python -m ncago.experiments.maze_control qualify --run NEW_RUN --data results/maze_data
python -m ncago.experiments.maze_control evaluate --run NEW_RUN --data results/maze_data
```

Evaluation refuses a failed qualification, a changed checkpoint, or a run whose large-maze evaluation already started. Seeds 1 and 2 use the same recipe. For the exploratory continuation:

```bash
python -m ncago.experiments.maze_control train \
  --train results/maze_data/train_9.npz --validation results/maze_data/test_9.npz \
  --seed 0 --updates 10000 --batch 64 --validation-count 512 \
  --resume results/maze_control/20261007T104409022623Z_ee2e3824_s0
```

Qualify the new continuation directory, then evaluate with `--offset59 256 --offset201 64`. This confirms on different subsets. Full optimizer, EMA, replay, and RNG state is provided for this continuation.
