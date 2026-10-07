# Methods and scope of inference

The README states the final claims. This page defines the measurements needed to interpret them. Historical appendices retain the stage-specific terminology and decisions used during experimentation.

## Go target and sampling

The main task assigns each stone the size of its chain's distinct liberty set, capped at four. Stored labels are zero-based classes: `0,1,2,3` mean `1,2,3,4+`; negative labels are excluded. Chains connect orthogonally through stones of one color. Random boards come from legal alternating playouts with suicide and simple-ko checks; constructed positions target harder geometries.

Training uses sizes 5, 6, 7, 8, and 9 placed on a 9×9 canvas, with an explicit outside-board token. It is not a strictly 9×9-only experiment. Online candidate generation is mixed with a replay buffer of states. Final main models receive 30,000 optimizer updates, batch size 64, horizons 32–128, a 32-step gradient window, last-eight-step supervision, late-change weight 0.1, learning rate 0.0005, and EMA 0.99. See each released run's `config.yaml` and `model.json` for authoritative settings; the base rescue config says 20,000 updates and the final command overrides this to 30,000.

All 18 main checkpoints share the recorded candidate-stream digest and actual supervised-stream digest. This is a matched-data comparison; parameter counts, receptive fields, optimization difficulty, and FLOPs are not identical. The NCA, no-ID NCA, ResNet, recurrent CNN, and sum/max stone GNN are available in source. No-ID inputs are zero-filled in a reserved 32-channel slot to preserve NCA capacity. The ResNet has 18 residual blocks and a radius-37 receptive field. A recurrent-CNN iteration contains two convolutions and therefore has a different propagation speed from a single NCA step.

The NCA projects mutable channel groups into unit balls, not onto unit spheres. It has no global iteration input. Random IDs are held fixed during a replay trajectory and renewed for fresh rollouts. The eight test ID fields also vary stochastic inference; they are nuisance trials, not independent training seeds. The no-ID condition uses three firing draws.

## Evaluation units

| Metric | Unit and aggregation |
|---|---|
| Stone accuracy | Correct occupied-cell predictions divided by occupied cells |
| Class-macro accuracy | Mean of per-class recalls for classes with support; unsupported classes excluded and recorded |
| Board exact | Fraction of boards with every supervised stone correct |
| Witness pair-both-correct | Both query predictions correct in a paired intervention |
| Cycle pair-both-correct | Both members correct in label-preserving cyclic/broken-cycle controls |
| Seed range | Minimum and maximum across three independently trained models; not a confidence interval |

Repeated stones in one chain, repeated draws of a board, and members of a witness family are dependent observations. We do not treat them as independent sample counts for uncertainty estimates. The headline table first averages nuisance draws within a training seed, then averages training seeds.

The final whole-board sets contain 256 boards per size, at 9, 13, 19, 25, and 37. Exclusion checks remove observed training positions and previously opened positions using canonical symmetries. Deduplication changes the accepted generator mixture; each dataset manifest records it. Large test sets and source checkpoint hashes were frozen before evaluation.

The cap-4 witnesses use five geometry families: straight, elbow, snake, comb, and ring, with eight pairs per family at each size. They change a distant liberty while preserving the query neighborhood. Randomness is coupled within pairs. `pair-both-correct` is the primary outcome metric; query accuracy or prediction invariance alone is weaker. Cycle controls preserve the label and should not be conflated with outcome-changing witnesses.

For whole boards, the budget is `max(1, ceil(ratio × maximum stone-chain diameter))`. Proportional witness budgets use the larger queried-chain diameter of the two members. Ratios are 0.5, 1, 2, and 4. Chain-graph diameter is a useful algorithmic scale, not the grid NCA's strict light cone: the grid NCA can send messages through empty cells. Fixed-depth pair trajectories are separately retained. The ResNet's prediction is feedforward and does not change with a nominal rollout budget.

## Qualification and historical exceptions

The three primary cap-4 NCAs passed their full frozen 9×9 validation gates before the larger final sets were opened: at least 95% macro accuracy, absolute stone-accuracy change no greater than 0.2 percentage points from D128 to D512 and D1024, and at most 0.2 points of D128 accuracy range across eight ID draws. The reported 99.508%→99.531% stability result is a mean over those three seeds.

The historical evaluation protocol allowed diagnostic baselines and richer-task cohorts after the primary NCA qualified, even when the evaluated model did not meet the 95% macro gate itself. The GNN optimization gap and poorer richer-task fit limit causal interpretation. We retain those measurements rather than silently treating all models as qualified. **Future experiments require each model to pass its own qualification gate.** The existing evaluator still contains the historical exception; do not invoke `--primary-gates-already-passed` for a new confirmatory cohort.

The old checkpoint audit and hand-coded reference use earlier, already opened data. Their numbers must not be presented as a matched evaluation on the new frozen cohort. Old checkpoints mostly undercounted; that does not imply all final model families do. The full release includes both complete confusion matrices and separate upper/lower error triangles. Nominal race outcomes have no ordered overcount/undercount interpretation.

## Maze positive control

This is an independent implementation based on the Maze-OOD configuration in Etcheverry et al. (2026), not a reproduction from an official released implementation. The model has 16 state channels, two output channels, four learned 3×3 perception heads, expansion two, and 11,888 parameters. Walls and endpoints clamp their complete state; free cells start with Gaussian noise. Firing probability is 0.8. There is no Go-style normalization or gated projection.

Training uses 5,000 updates, batch 64, replay pool 256, 25% fresh examples, 100-step all-step MSE, AdamW at 0.0004 with zero weight decay, gradient clipping at one, and EMA 0.999. Damage, noise, target swap, and D4 augmentation follow the implemented paper-based recipe. Initialization and basis choices not fully specified by the paper are explicit in code; this and the parameter-count difference are reproduction limitations.

All 50,000 training labels, 10,000 test labels at 9 and 59, and 1,000 at 201 were checked with independent BFS after verifying the doubled RGB block representation and converting it to logical cells. Only the subsets stated in the README were evaluated neurally. D4 canonicalization found 401 test9 mazes overlapping training and 27 among the naive first 512. Final qualification instead uses the first 512 eligible, unique, disjoint mazes. All four final checkpoints score 100% at D100/D400/D800 on that corrected split.

The initial three seeds use first256 test59 and first64 test201. Three inference seeds (20001–20003) each produce one rollout per board. The 10,000-update repair continues seed 0 including optimizer, EMA, replay, and RNG state; confirmation uses indices 256:512 at 59 and 64:128 at 201. Those are different boards, so the change is not a paired treatment estimate. Exact CPU continuation was separately tested by comparing 2+2 updates with four uninterrupted updates.

The reliability gate requires ≥99% exact path on clean small-board qualification and ≥95% exact at both larger sizes for every inference seed. None passes. Diagnostic longer inference and injected test noise use already opened examples and are not fresh confirmation tests. A synchronous leaf-pruning reference is exact on the checked tree-maze domain; its clock and computation differ from the stochastic learned model.

## Richer tasks and limits

Cap 16 predicts liberties 1–15 and 16+. Simple eyes predict static eye-point counts 0–7 and 8+; they do not implement Benson unconditional life. Constructed eye data have insufficient diversity at 9×9 after deduplication: 255/256 final boards are legal-random, one is constructed, and classes 5, 6, and 8 lack support. Macro accuracy alone can hide that gap.

Race labels describe a finite first-capture game. Random race boards have size 5×N, padded on N×N canvases. Constructed witness and cycle sets use full N×N boards. An oracle cache delivers the same prescribed race candidate sequence to each model; it is not a learned engine. The three race seeds show large variation, so future race experiments require at least five seeds.

No result here measures full Go strength, a KataGo attack, FAR exploit reproduction, or validated ladder/Benson reasoning. The later task ladder, influence-length fit for all six models, sparse-ID training, two-draw consistency loss, and 5–19 training expansion remain unexecuted because the maze gate failed. The failed positive control does not prove a software bug or an impossibility theorem; it makes stronger mechanism claims premature.
