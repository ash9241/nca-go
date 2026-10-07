# Experiments that could resolve the failure

The next experiment should distinguish competing explanations. All work below is prospective, except for the completed maze control and the existing descriptive audits. The machine-readable plan is [next_counting_protocol.json](../configs/next_counting_protocol.json).

| Experiment | Discriminating observation | Current status |
|---|---|---|
| Reproduce a reliable maze control across training seeds | ≥99% clean 9×9 exact, ≥95% at 59×59 and 201×201 for each inference draw | Three 5k seeds and a 10k continuation failed the full gate |
| Same-generator task ladder: marked-point OR → atari → cap 4 | OR transfers but atari fails, localizing a possible distinctness issue | Held |
| Influence length for all six final model families | Measure a single remote edit's converged effect and fit log magnitude against distance | Held; existing examples are not this complete fit |
| Sparse 256-bucket IDs and saturated messages | Elementwise-max union becomes an explicit learnable target | Held |
| Step-aligned set-union supervision | Intermediate states match causal reference states, beyond matching final labels | Held |
| Two ID draws and consistency loss | Predictions remain stable across identifier assignments | Held |
| Train 5–19 on a 19×19 canvas; test 25–49 | More modest size extrapolation succeeds where 5–9 training fails | Held |
| Repair eye-family diversity and require five race seeds | Class support and seed variability cease dominating conclusions | Held until cap 4 extrapolates |

For sparse bucket IDs, collisions can only undercount **in the hand-coded union algorithm**. A learned predictor has no such guarantee and can overcount. Taking the maximum over eight learned predictions must therefore be evaluated for both directions of error; it cannot be assumed correct. Consistency penalties can also conflict with legitimately different bucket collisions. Record the reference collision floor separately.

A useful cap-4 success criterion is at least 95% class-macro accuracy and 90% pair-both-correct on every prespecified larger size, at no more than four times chain diameter, for each of three training seeds. Before opening a new test set, every evaluated model must independently pass its small-board qualification. Retain the 9×9-only condition as an extreme extrapolation control and publish failures.

When contributing, include source revision, exact config, candidate and supervised stream hashes, checkpoint hashes, per-seed results, pair geometry, and raw predictions. State which choices were made before evaluating a set and which followed an observed failure. A concise reproducer of a failure is valuable evidence.
