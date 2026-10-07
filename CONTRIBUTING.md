# Contributing

Reproductions, minimal failure cases, and well-controlled negative results are welcome. Start with the [open experiments](docs/open-problems.md) and [methods](docs/methods.md).

For a result, provide the command/config, source revision, hardware and dependencies, training seed, data-stream hashes, checkpoint hash, and raw predictions. Report independent training seeds separately from repeated inference draws. Keep paired witnesses intact and make pair-both-correct the primary metric for outcome-changing pairs.

State whether choices were fixed before opening evaluation data. Do not select checkpoints on the public final sets and call the result a new held-out test. Use new frozen data for confirmatory claims. Require every model's own small-board qualification before larger evaluation.

Run `python -m pytest -q` for code changes. Use `python tools/published_results.py` to regenerate tables and plots when updating the measured record. Numerical changes should include the evidence and aggregation rule, not hand-edited headline values.

The next priority is the failed maze positive control. Richer Go tasks remain paused until cap-4 extrapolation passes its gate. Please discuss expensive training plans in an issue before relying on them as a shared benchmark protocol.
