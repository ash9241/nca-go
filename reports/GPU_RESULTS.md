# A100 investigation: final results

The asynchronous whole-board model passes the numeric G1 threshold in every recorded training seed: 99.886% mean per-stone accuracy and 99.882% class-balanced accuracy. The improvement is reproducible on independent 9×9 positions. Exact generalization to arbitrary larger boards remains unresolved.

Frozen checkpoints evaluated on fresh final boards. Every previously opened dataset is excluded up to rotation, reflection and color swap. The primary inference depth was frozen before opening these boards. Larger-board results were not used to retune the models.

| Recipe | Training seeds | 9×9 accuracy per seed | G1 accuracy threshold |
|---|---|---|---|
| Asynchronous | 0, 1, 2 | 99.8705%, 99.8588%, 99.9294% | Passed |
| Synchronous | 0, 1, 2 | 99.8224%, 99.7663%, 99.9304% | Passed |
| Synchronous + algorithm hints | 0 | 99.6718% | Passed |
| C128 Synchronous | 0 | 99.9574% | Passed |

## Independent final accuracy

Per-stone results pool random and controlled positions. Macro accuracy weights all four liberty classes equally; board exactness requires every stone to be correct. The bootstrap resamples boards within each generator, preserving shared test boards across seeds. It does not certify arbitrary Go positions.

| Recipe | Board | Depth | Stone mean ± seed SD | Board bootstrap 95% interval | Macro mean | Boards entirely correct |
|---|---|---:|---:|---:|---:|---:|
| Asynchronous | 9×9 | 32 | 99.886% ± 0.038% | 99.854–99.916% | 99.88% | 98.57% |
| Asynchronous | 13×13 | 32 | 78.136% ± 1.915% | 76.474–79.876% | 78.60% | 59.70% |
| Asynchronous | 19×19 | 32 | 74.106% ± 1.190% | 71.221–77.182% | 72.36% | 51.95% |
| Asynchronous | 25×25 | 32 | 75.401% ± 0.480% | 71.366–79.404% | 73.38% | 47.05% |
| Asynchronous | 37×37 | 32 | 65.421% ± 0.656% | 59.591–71.980% | 62.23% | 40.62% |
| Synchronous | 9×9 | 32 | 99.840% ± 0.083% | 99.788–99.884% | 99.85% | 97.62% |
| Synchronous | 13×13 | 32 | 77.178% ± 2.837% | 75.559–78.832% | 77.61% | 56.12% |
| Synchronous | 19×19 | 32 | 72.625% ± 3.299% | 69.845–75.702% | 70.89% | 50.78% |
| Synchronous | 25×25 | 32 | 74.828% ± 2.517% | 70.873–78.792% | 72.83% | 47.92% |
| Synchronous | 37×37 | 32 | 65.349% ± 2.005% | 59.787–71.680% | 62.19% | 41.67% |
| Synchronous + algorithm hints | 9×9 | 32 | 99.672% (one seed) | 99.546–99.791% | 99.65% | 97.00% |
| Synchronous + algorithm hints | 13×13 | 32 | 88.697% (one seed) | 87.227–90.173% | 88.12% | 63.67% |
| Synchronous + algorithm hints | 19×19 | 32 | 76.438% (one seed) | 73.910–78.915% | 74.26% | 50.78% |
| Synchronous + algorithm hints | 25×25 | 32 | 70.815% (one seed) | 66.822–74.742% | 69.95% | 42.97% |
| Synchronous + algorithm hints | 37×37 | 32 | 59.543% (one seed) | 54.641–64.605% | 57.22% | 39.06% |
| C128 Synchronous | 9×9 | 32 | 99.957% (one seed) | 99.915–99.990% | 99.96% | 99.55% |
| C128 Synchronous | 13×13 | 32 | 80.845% (one seed) | 79.287–82.492% | 80.85% | 59.96% |
| C128 Synchronous | 19×19 | 32 | 75.185% (one seed) | 72.518–78.068% | 73.30% | 52.34% |
| C128 Synchronous | 25×25 | 32 | 76.556% (one seed) | 72.717–80.471% | 74.57% | 51.56% |
| C128 Synchronous | 37×37 | 32 | 66.576% (one seed) | 60.878–72.943% | 63.43% | 43.75% |

## What changed and why

The CPU smoke run established that the pipeline worked but failed to learn liberty counting. The GPU sweep varied width, readout/loss, replay, curriculum, normalization, rollout horizon, initialization, gating, intermediate supervision and training board sizes. All completed, failed and interrupted attempts remain recorded in gpu_investigation.md.

The successful whole-board recipe balances class contributions, uses a late cross-entropy loss, wider cells, augmentation, a decaying learning rate, final weight averaging and a bounded gated update. Those changes address majority-class collapse and recurrent optimization. Several were combined, so this sweep does not identify a unique cause for the entire improvement. Matched experiments isolate the effect of asynchronous firing and auxiliary algorithm supervision.

Auxiliary hints teach each cell how many distinct liberties have reached it so far. An exact local algorithm supplies training labels. Its IDs and hidden states are never inputs to neural inference. The message-routing experiment additionally restricts hidden communication to orthogonally adjacent stones of the same color; that is an explicit Go connectivity prior. Its component neighborhoods are deduplicated across splits, including translation and irrelevant clutter.

Passing the numeric G1 threshold does not establish the original stronger hypothesis of exact size generalization. Synchronous results use a plain recurrent cell model; the asynchronous variant retains stochastic local firing. More rollout steps can reduce accuracy, and large-board averages can hide failure on a distant-information witness. Life, ladders and playing strength have not been rescued by these liberty experiments.

## Distant-information tests

Each pair differs at one distant cell and has identical query neighborhoods inside that distance. Firing and initial noise are coupled within the pair. A fixed CNN whose receptive-field radius is nine cannot exceed 50% query accuracy when the changed input is farther away. This is a structural upper bound, not an empirical CNN training comparison.

The table includes every measured depth; the sealed graph-family primary depth is 64. Each size uses one distant-query geometry with rotations, color swaps and surrounding clutter. These repeated variants do not establish broad chain-shape generalization.
The separately trained asynchronous graph model with intermediate hints reaches 74.74% on the sealed 37×37 witness at the frozen depth of 64. The changed cell is 34 grid steps away; the supplied 16-block CNN has radius 33 and therefore cannot exceed 50% on these balanced pairs. The graph model uses training sizes 5–9, an explicit connectivity prior and one training seed with three firing trials. This supports a narrow learned-propagation claim. Its later accuracy declines, so it does not certify convergence or exact liberty counting.


| Model | Board | Steps | Distance | Query accuracy | Both pair answers correct |
|---|---|---:|---:|---:|---:|
| Grid: async target chain | 13×13 | 8 | 10 | 50.00% | 0.00% |
| Grid: async target chain | 13×13 | 16 | 10 | 50.00% | 0.00% |
| Grid: async target chain | 13×13 | 32 | 10 | 20.83% | 0.00% |
| Grid: async target chain | 13×13 | 64 | 10 | 0.00% | 0.00% |
| Grid: async target chain | 13×13 | 128 | 10 | 0.00% | 0.00% |
| Grid: async target chain | 13×13 | 256 | 10 | 0.00% | 0.00% |
| Grid: sync whole board | 13×13 | 8 | 10 | 50.00% | 0.00% |
| Grid: sync whole board | 13×13 | 16 | 10 | 50.00% | 0.00% |
| Grid: sync whole board | 13×13 | 32 | 10 | 50.78% | 1.56% |
| Grid: sync whole board | 13×13 | 64 | 10 | 59.38% | 18.75% |
| Grid: sync whole board | 13×13 | 128 | 10 | 41.41% | 0.00% |
| Grid: sync whole board | 13×13 | 256 | 10 | 10.16% | 0.00% |
| Grid: sync + hints whole board | 13×13 | 8 | 10 | 50.00% | 0.00% |
| Grid: sync + hints whole board | 13×13 | 16 | 10 | 67.19% | 34.38% |
| Grid: sync + hints whole board | 13×13 | 32 | 10 | 58.59% | 17.19% |
| Grid: sync + hints whole board | 13×13 | 64 | 10 | 54.69% | 9.38% |
| Grid: sync + hints whole board | 13×13 | 128 | 10 | 50.78% | 1.56% |
| Grid: sync + hints whole board | 13×13 | 256 | 10 | 50.78% | 1.56% |
| Graph: sync + hints target chain | 13×13 | 8 | 10 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 13×13 | 16 | 10 | 46.09% | 46.09% |
| Graph: sync + hints target chain | 13×13 | 32 | 10 | 76.95% | 53.91% |
| Graph: sync + hints target chain | 13×13 | 64 | 10 | 86.72% | 73.44% |
| Graph: sync + hints target chain | 13×13 | 128 | 10 | 86.72% | 73.44% |
| Graph: sync + hints target chain | 13×13 | 256 | 10 | 89.06% | 78.12% |
| Graph: sync + hints target chain | 19×19 | 8 | 16 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 19×19 | 16 | 16 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 19×19 | 32 | 16 | 66.41% | 40.62% |
| Graph: sync + hints target chain | 19×19 | 64 | 16 | 69.53% | 46.88% |
| Graph: sync + hints target chain | 19×19 | 128 | 16 | 75.00% | 57.81% |
| Graph: sync + hints target chain | 19×19 | 256 | 16 | 75.00% | 57.81% |
| Graph: sync + hints target chain | 25×25 | 8 | 22 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 25×25 | 16 | 22 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 25×25 | 32 | 22 | 58.59% | 42.19% |
| Graph: sync + hints target chain | 25×25 | 64 | 22 | 67.97% | 57.81% |
| Graph: sync + hints target chain | 25×25 | 128 | 22 | 67.97% | 57.81% |
| Graph: sync + hints target chain | 25×25 | 256 | 22 | 67.97% | 57.81% |
| Graph: sync + hints target chain | 37×37 | 8 | 34 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 37×37 | 16 | 34 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 37×37 | 32 | 34 | 50.00% | 0.00% |
| Graph: sync + hints target chain | 37×37 | 64 | 34 | 64.06% | 53.12% |
| Graph: sync + hints target chain | 37×37 | 128 | 34 | 69.53% | 64.06% |
| Graph: sync + hints target chain | 37×37 | 256 | 34 | 52.34% | 29.69% |
| Graph: async + hints target chain | 13×13 | 8 | 10 | 50.00% | 0.00% |
| Graph: async + hints target chain | 13×13 | 16 | 10 | 63.02% | 46.88% |
| Graph: async + hints target chain | 13×13 | 32 | 10 | 71.35% | 50.00% |
| Graph: async + hints target chain | 13×13 | 64 | 10 | 65.62% | 44.27% |
| Graph: async + hints target chain | 13×13 | 128 | 10 | 49.22% | 30.21% |
| Graph: async + hints target chain | 13×13 | 256 | 10 | 46.61% | 27.60% |
| Graph: async + hints target chain | 19×19 | 8 | 16 | 50.00% | 0.00% |
| Graph: async + hints target chain | 19×19 | 16 | 16 | 50.00% | 0.00% |
| Graph: async + hints target chain | 19×19 | 32 | 16 | 75.26% | 50.52% |
| Graph: async + hints target chain | 19×19 | 64 | 16 | 61.98% | 42.19% |
| Graph: async + hints target chain | 19×19 | 128 | 16 | 43.23% | 23.44% |
| Graph: async + hints target chain | 19×19 | 256 | 16 | 39.32% | 17.71% |
| Graph: async + hints target chain | 25×25 | 8 | 22 | 50.00% | 0.00% |
| Graph: async + hints target chain | 25×25 | 16 | 22 | 50.00% | 0.00% |
| Graph: async + hints target chain | 25×25 | 32 | 22 | 63.80% | 28.65% |
| Graph: async + hints target chain | 25×25 | 64 | 22 | 57.81% | 39.06% |
| Graph: async + hints target chain | 25×25 | 128 | 22 | 41.67% | 27.08% |
| Graph: async + hints target chain | 25×25 | 256 | 22 | 39.32% | 23.96% |
| Graph: async + hints target chain | 37×37 | 8 | 34 | 50.00% | 0.00% |
| Graph: async + hints target chain | 37×37 | 16 | 34 | 50.00% | 0.00% |
| Graph: async + hints target chain | 37×37 | 32 | 34 | 50.00% | 0.00% |
| Graph: async + hints target chain | 37×37 | 64 | 34 | 74.74% | 52.60% |
| Graph: async + hints target chain | 37×37 | 128 | 34 | 47.14% | 23.44% |
| Graph: async + hints target chain | 37×37 | 256 | 34 | 42.71% | 18.75% |
| Graph: async target chain | 13×13 | 8 | 10 | 50.00% | 0.00% |
| Graph: async target chain | 13×13 | 16 | 10 | 50.26% | 6.25% |
| Graph: async target chain | 13×13 | 32 | 10 | 19.53% | 0.00% |
| Graph: async target chain | 13×13 | 64 | 10 | 78.39% | 57.81% |
| Graph: async target chain | 13×13 | 128 | 10 | 64.58% | 29.17% |
| Graph: async target chain | 13×13 | 256 | 10 | 52.86% | 20.31% |
| Graph: async target chain | 19×19 | 8 | 16 | 50.00% | 0.00% |
| Graph: async target chain | 19×19 | 16 | 16 | 50.00% | 0.00% |
| Graph: async target chain | 19×19 | 32 | 16 | 42.71% | 7.81% |
| Graph: async target chain | 19×19 | 64 | 16 | 61.46% | 26.56% |
| Graph: async target chain | 19×19 | 128 | 16 | 61.20% | 26.56% |
| Graph: async target chain | 19×19 | 256 | 16 | 50.00% | 27.08% |
| Graph: async target chain | 25×25 | 8 | 22 | 50.00% | 0.00% |
| Graph: async target chain | 25×25 | 16 | 22 | 50.00% | 0.00% |
| Graph: async target chain | 25×25 | 32 | 22 | 50.52% | 1.04% |
| Graph: async target chain | 25×25 | 64 | 22 | 23.70% | 16.67% |
| Graph: async target chain | 25×25 | 128 | 22 | 22.40% | 17.19% |
| Graph: async target chain | 25×25 | 256 | 22 | 18.49% | 17.19% |
| Graph: async target chain | 37×37 | 8 | 34 | 50.00% | 0.00% |
| Graph: async target chain | 37×37 | 16 | 34 | 50.00% | 0.00% |
| Graph: async target chain | 37×37 | 32 | 34 | 50.00% | 0.00% |
| Graph: async target chain | 37×37 | 64 | 34 | 42.97% | 8.85% |
| Graph: async target chain | 37×37 | 128 | 34 | 37.24% | 31.77% |
| Graph: async target chain | 37×37 | 256 | 34 | 27.86% | 15.62% |

## Reproduction

The machine metadata and dependency locks are under results/cloud/. The final checkpoint hashes, source paths, board counts and evaluation depths are embedded in GPU_RESULTS.json and each final run's config.yaml. Raw boards, predictions and checkpoint weights are preserved locally under results/. Recreate the reports without training with:

```sh
.venv/bin/python -m ncago.experiments.gpu_report
.venv/bin/python -m ncago.experiments.rescue_report --final-runs results/final_liberties/20261006T212113968288Z_59de8868_s0 results/final_liberties/20261006T204213644556Z_bfe5e188_s0 results/final_liberties/20261006T201154825293Z_9e8b7700_s0 results/final_liberties/20261006T214047538687Z_059b755c_s0 --paired-runs results/propagation_probe/20261006T193551776082Z_a43610fb_s0 results/propagation_probe/20261006T200027485940Z_905f775a_s0 results/propagation_probe/20261006T212012244849Z_ded7d2f1_s0 results/propagation_probe/20261006T212216958801Z_03a04154_s0
```
