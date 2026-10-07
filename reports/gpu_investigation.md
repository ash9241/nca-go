# GPU liberty investigation

Measured training/validation results from the dedicated A100 worker. Target-chain rows supervise one constructed chain per board; whole-board rows supervise all stones. Neither is a sealed final G1 result. Constant class predictions score 25% on the macro metric.

| Experiment | Boards / updates | 9×9 at trained depth | 9×9 at 4× depth | 13×13 at trained depth | Status |
|---|---:|---:|---:|---:|---|
| C32, ce late · target chain · seed 0 | 1,024 / 6,000 | 72.06% | 28.93% | 25.07% | measured |
| C64, ce late · target chain · seed 0 | 1,024 / 6,000 | 99.03% | 29.04% | 28.79% | measured |
| C64, ce late async, curriculum · target chain · seed 0 | 1,024 / 6,000 | 93.49% | 34.55% | 27.59% | measured |
| C64, ce late async, replay, curriculum · target chain · seed 0 | 1,024 / 6,000 | 84.84% | 84.57% | 48.13% | measured |
| C64, ce late async, normalized, replay, curriculum · target chain · seed 0 | 1,024 / 6,000 | — | — | — | failed |
| C64, mse late · target chain · seed 0 | 1,024 / 6,000 | 95.37% | 25.61% | 25.30% | measured |
| C64, ce late, EMA + decay · target chain · seed 0 | 2,048 / 12,000 | 99.70% | 42.93% | 26.86% | measured |
| C64, ce late async, gated, EMA + decay, 5–9 sizes · target chain · seed 0 | 8,192 / 20,000 | 100.00% | 98.29% | 95.48% | measured |
| C64, ce late, gated, EMA + decay · target chain · seed 0 | 2,048 / 12,000 | 95.64% | 49.50% | 27.33% | measured |
| C64, ce late, gated, EMA + decay · whole board · seed 0 | 8,192 / 30,000 | 99.94% | 86.77% | 80.67% | measured |
| C64, ce late async, normalized, replay, curriculum · target chain · seed 0 | 1,024 / 6,000 | 63.84% | 62.45% | 34.54% | measured |
| C64, ce late, gated, EMA + decay, algorithm hints · whole board · seed 0 | 8,192 / 30,000 | 99.78% | 97.65% | 92.74% | measured |
| C64, ce late, gated, varied horizon, EMA + decay · target chain · seed 0 | 2,048 / 12,000 | — | — | — | interrupted |
| C64, ce late, gated, varied horizon, EMA + decay · target chain · seed 0 | 2,048 / 12,000 | 89.02% | 87.88% | 25.34% | measured |
| C64, ce late async, gated, varied horizon, EMA + decay · target chain · seed 0 | 2,048 / 12,000 | 95.23% | 93.20% | 27.01% | measured |
| C64, ce late async, gated, replay, EMA + decay, 5–9 sizes · target chain · seed 0 | 8,192 / 20,000 | 99.71% | 99.64% | 85.43% | measured |
| C128, ce late, gated, EMA + decay · whole board · seed 0 | 8,192 / 30,000 | 99.99% | 98.75% | 84.24% | measured |
| C64, ce late, gated, EMA + decay · whole board · seed 2 | 8,192 / 30,000 | 99.97% | 93.30% | 83.83% | measured |
| C64, ce late, gated, EMA + decay · whole board · seed 1 | 8,192 / 30,000 | 99.83% | 83.28% | 81.46% | measured |
| C64, ce late, gated, EMA + decay, algorithm hints, same-chain messages, diverse shapes, 5–9 sizes · target chain · seed 0 | 8,192 / 20,000 | — | — | — | interrupted |
| C64, ce late async, gated, EMA + decay · whole board · seed 0 | 8,192 / 30,000 | 99.98% | 96.92% | 83.09% | measured |
| C64, ce late, gated, EMA + decay, algorithm hints, same-chain messages, diverse shapes, 5–9 sizes · target chain · seed 0 | 8,192 / 20,000 | 95.46% | 93.02% | 87.12% | measured |
| C64, ce late async, gated, EMA + decay, algorithm hints, same-chain messages, diverse shapes, 5–9 sizes · target chain · seed 0 | 8,192 / 20,000 | 85.27% | 83.50% | 69.59% | measured |
| C64, ce late async, gated, EMA + decay · whole board · seed 1 | 8,192 / 30,000 | 99.87% | 89.66% | 81.55% | measured |
| C64, ce late async, gated, EMA + decay · whole board · seed 2 | 8,192 / 30,000 | 99.98% | 90.52% | 84.11% | measured |
| C64, ce late async, gated, EMA + decay, same-chain messages, diverse shapes, 5–9 sizes · target chain · seed 0 | 8,192 / 20,000 | 90.87% | 69.58% | 79.29% | measured |
| C64, ce late async, gated, varied horizon, replay, EMA + decay · target chain · seed 0 | 2,048 / 12,000 | 90.90% | 90.95% | 26.40% | measured |

Raw summaries, source snapshots, logs, dataset files, and checkpoints are stored under `results/learnability/<run>/`. Each row's source revision is included in the JSON report.

The experiments vary capacity, loss/readout, curriculum, replay, normalization, weight averaging, learning-rate decay, gating, rollout horizon and training board size. Only matched recipes isolate a single factor; combined recipe improvements do not establish which individual change caused them.
