# Codex task: Neural Cellular Automata for Go, with a visual capability report

## 0. Mission

Build a research codebase that tests where Neural Cellular Automata (NCAs) work for Go and where they fail, run the experiments below, and finish with a self-contained visual report that shows where and how NCAs are useful.

Core hypothesis: NCAs (weight-tied, strictly local, asynchronous recurrent cells) can compute Go quantities that need long-range propagation (chain liberties, unconditional life, ladders, cyclic groups) and generalize exactly to larger boards, while fixed-depth CNNs fail once the required information distance exceeds their receptive field.

Reference paper: "Reasoning with Neural Cellular Automata", Etcheverry et al., arXiv:2609.36126 (https://arxiv.org/abs/2609.36126). Read it if you have network access. Section 2 contains everything you need from it if you don't.

### Ground rules (non-negotiable)

1. Never fabricate, estimate, or hand-type a number that appears in results or the report. Every number comes from a logged run. Anything not run is marked "not run: <reason>".
2. In-distribution failure is a bug: debug it. Out-of-distribution failure is a finding: report it. Never tune on OOD test sets. Use 13x13 as the OOD validation split for model selection and leave 19x19 and larger test sets untouched until final evaluation.
3. Work phase by phase. Each phase ends with passing tests, a git commit, and an entry in `RESULTS_LOG.md` (what ran, config hash, seeds, key metrics, wall clock, hardware).
4. Record every deviation from this spec in `DECISIONS.md` with a one-line reason.
5. If a step needs network access and it fails (KataGo binary or model, FAR adversarial SGFs, GnuGo), skip only the parts that depend on it, mark them "not run" in the report with the reason, and continue. Never silently substitute another data source.
6. Support two profiles. `smoke` runs on CPU in under 30 minutes end to end with tiny data and produces the full report (proves the pipeline). `full` runs on a single GPU. Get `smoke` passing before any `full` run.
7. When you change code, keep files whole and coherent. Do not leave partial stubs, TODO bodies, or dead code paths in committed files.

## 1. Stack and repo layout

Python 3.11, JAX (`jax[cuda12]` on GPU), Equinox or Flax linen (pick one and record it in DECISIONS.md), Optax, NumPy, numba (flood fills and data generation), matplotlib, imageio, pandas, pytest, pyyaml, sgfmill (rules cross-check and SGF parsing), tqdm.

```
ncago/
  go/           rules engine, SGF IO, position generators, exact labelers (liberties, Benson, ladders)
  nca/          model, training loop (replay pool, perturbations), rollout, test-time scaling
  baselines/    fixed-depth ResNet, plain recurrent CNN, hand-coded local CA references
  experiments/  one module per phase, each with main() reading configs/
  viz/          board rendering, filmstrips, GIFs, plots
  report/       HTML report builder
configs/        YAML per experiment and profile
tests/
results/        <phase>/<run_id>/{config.yaml, metrics.jsonl, eval/*.csv, viz/*.npz, ckpt/}
reports/        nca_go_report.html, SUMMARY.md, figures/
Makefile        setup, test, smoke, full, report
```

## 2. NCA specification (follow the paper unless noted)

**State.** `X` has shape (H, W, C), split into channel slices: `C_in` (frozen input embedding), `C_out` (prediction readout), `C_hid` (latent).

**Inputs.** Tokens per intersection: empty, black, white, off-board. Embed each as a fixed orthonormal vector of size `C_in` (not learned). Input channels never update. Off-board cells keep all channels frozen, which works like the paper's maze walls and lets one model run on any board size padded onto a larger canvas.

**Perception.** `K_heads` learned 3x3 convolutions over the full state, position-independent. Do not use the paper's position-specific "fixed attention", because it breaks substrate scaling. The perception vector is the concatenation of head outputs.

**Update.** Per-cell MLP via 1x1 convs: `Linear(K_heads*C -> E*C) -> ReLU -> Linear(E*C -> C)`. Zero-initialize the final layer.

**Asynchronous residual update.** `x <- x + m * dx` with `m ~ Bernoulli(p_fire)` per cell per step, `p_fire = 0.8`. Force `dx = 0` on frozen channels and off-board cells.

**Optional normalization.** Per-cell group normalization (state split into U groups, each L2-normalized after the update). Off by default, used as an ablation.

**Readout (default, paper-faithful).** Map target classes to fixed orthonormal embeddings in `C_out`. Loss is MSE between `C_out` and the target embedding. Decode by L2 similarity `1 / (1 + ||x_out - e_v||)`, take argmax. Cell confidence is the max similarity. Flag `readout=ce` switches to a linear head with cross-entropy.

**Initialization.** Input channels from embeddings, all other channels `N(0, sigma_init^2)` with `sigma_init = 0.15`.

### Training (sample replay, per the paper)

- Replay pool of `M = 4*B` states. Each step: sample B from the pool, replace a fraction `r_seed = 0.25` with fresh samples, then apply pre-rollout perturbations:
  - Damage with p = 0.1: 1 to 3 circular masks, radius 0.1 to 0.4 of board width, zero all non-frozen channels inside.
  - Target swap with p = 0.1: replace the input board and target with another sample's while keeping the hidden state.
- During rollout, state noise: at each step with probability `p_t = 0.1`, add `N(0, 0.15^2)` to a random `p_s = 0.2` fraction of cells (non-frozen channels only).
- Unroll N steps with `jax.lax.scan`, truncated BPTT over a chunk of `N_chunk` steps, loss averaged over all steps in the chunk, masked to cells where the label is defined. Use `jax.checkpoint` if memory requires.
- AdamW, lr 4e-4 constant (cosine allowed, record it), grad clip 1.0, weight EMA 0.999 used for all evaluation.
- Write post-rollout states back into the pool.
- Augmentation: 8 dihedral transforms plus color swap (swap black and white tokens and any color-dependent labels).
- Starting hyperparameters, adapted from the paper's Maze-OOD config: `C = 32` (sweep 16, 32, 64), `C_in = 8`, `C_out = max(4, n_classes)`, `K_heads = 4`, `E = 2` (sweep 2, 4), `B = 64`, `N = N_chunk = 128` for 9x9 tasks, 5k to 20k training steps.

### Test-time compute

- **Temporal scaling.** Roll out D steps with D on the schedule {32, 64, ..., 8192}, plus `D_auto = 4 x` the task's information-distance upper bound. Store predictions and confidence at log-spaced checkpoints so steps-to-solve can be computed.
- **Spatial substrate scaling.** Same weights on 13, 19, 25, 37 boards.
- **Parallel trials.** K rollouts with board-mean-confidence selection (conf@K) and test-time noise during the first 25% of the rollout (`p_t = 0.1`, `p_s = 0.2`, sigma in {0, 0.1, 0.3, 1.0}).
- **Adaptive firing.** `p_fire = 0.4` if cell confidence > 0.95, else 0.8. Log per-cell fire counts.
- **FLOPs.** Per-step FLOPs from the compiled XLA graph (`jax.jit(...).lower(...).compile().cost_analysis()`), total = per-step x D x K. Also log wall-clock per evaluation.

### Metric definitions (implement exactly)

- Per-stone accuracy, per-chain accuracy (a chain is correct iff all its stones are correct), per-board exact accuracy.
- `t_solve`: earliest logged step after which the decoded prediction is correct and stays correct through `D_max`.
- Information distance: defined per task below. Light-cone efficiency = `t_solve / information distance`.
- Report mean and std over 3 training seeds (smoke: 1 seed). Report 95% bootstrap CIs on all accuracy gaps.

## 3. Baselines (identical data, augmentation, and step budget)

- **B1, fixed-depth ResNet.** L in {4, 8, 16} residual blocks of two 3x3 convs, fully convolutional so it runs on any board size. Two widths: params roughly equal to the NCA's, and roughly 10x. Compute and record the exact receptive-field radius from the architecture.
- **B2, plain recurrent CNN.** The NCA architecture trained synchronously (`p_fire = 1`), no replay pool, no perturbations, fixed N steps. Tests whether the paper's training recipe matters.
- **B3, hand-coded local references.** Exact, non-learned algorithms used as speed-of-light yardsticks, defined per phase.
- **NCA ablation grid** (Phases 1 and 3): remove each of {async, replay pool, noise, damage, target swap} one at a time.

## 4. Phase 0: rules engine, data, tests (gate G0)

- **Rules engine** (NumPy plus numba): any N x N from 5 to 37, orthogonal adjacency, chains by flood fill, liberties, capture of opponent chains left with zero liberties after a move, suicide illegal, simple ko required, positional superko optional. Tromp-Taylor area scoring.
- **Cross-check.** Replay 10,000 random games (random legal moves, small pass probability) at sizes 9 and 19 through both your engine and `sgfmill.boards.Board`, and assert identical boards after every move.
- **Position generators** (seeded and deterministic):
  - `P-random`: random legal playouts stopped at a random move count, stone densities 0.2 to 0.75.
  - `P-game`: positions from self-play games. Preferred source is KataGo low-visit self-play over GTP (setup in Phase 5), fallback GnuGo self-play, fallback `P-random`. Record which source was used.
  - `P-structured`: snakes (1-wide self-avoiding single-color paths, length up to 0.5 x N^2), rings (cyclic chains enclosing a region), spirals, combs. Place opponent stones to control liberty counts. Legalize everything.
- **Exact labelers** for liberties, Benson (Phase 2), and ladders (Phase 3), each with hand-built fixture tests.
- **Gate G0:** all tests pass and the engine matches sgfmill on 100% of moves.

## 5. Phase 1: liberties and atari

- **Task.** For each stone, the liberty count of its chain, capped into classes {1, 2, 3, 4+}. Class 1 is atari. Empty and off-board cells are masked from the loss.
- **Information distance.** Chain graph diameter (BFS inside the chain over orthogonal adjacency) plus 1.
- **B3 reference.** The k-smallest-liberty-id CA. Give every empty point a unique id. Each stone repeatedly merges the distinct ids held by itself, its orthogonal same-color neighbors, and its adjacent empty points, keeping the 4 smallest. This converges to the exact capped count in about diameter steps. Implement it in NumPy and record its step count per chain.
- **Splits.** Train on 9x9 only (60% `P-random`, 40% `P-structured`). Validate on 13x13. Test on 9, 13, 19, 25, 37 for each generator, stratified by information-distance bins.
- **Extra ablation.** Moore vs von Neumann neighborhood (mask the diagonal kernel taps). Go connectivity is orthogonal, and diagonal leakage is a plausible failure mode.
- **Gate G1:** NCA per-stone accuracy of at least 99.5% on the 9x9 test set. If it misses, debug before Phase 2. OOD results get reported whatever they are.
- **Save for visualization:** full per-step rollout tensors (hidden-state PCA to 3 components, decoded prediction, confidence, fire mask) for 6 showcase boards: the longest snake on 37x37, a ring, a spiral, a dense random 19x19, and two more of your choice.

## 6. Phase 2: Benson's unconditional life

**Exact labeler.** Implement exactly this, separately for each color P:

1. Let X be all chains of color P, and R be all P-enclosed regions (maximal orthogonally connected sets of points that are not P stones).
2. A region r is vital to a chain c if every empty point in r is a liberty of c.
3. Repeat until nothing changes: (a) remove from X every chain with fewer than two vital regions in R; (b) remove from R every region adjacent to a P stone whose chain is not in X.
4. The final X is the set of pass-alive chains of color P.

**Tests.** Two separate one-point eyes is alive. One large eye is not pass-alive. False-eye fixtures are not pass-alive. Seki is not pass-alive. Property test: for every chain labeled pass-alive, 2,000 random opponent playouts in which P always passes never capture it.

**Task.** Per stone: {black pass-alive, white pass-alive, neither}.

**Data.** Pass-alive chains are rare in random positions. Build the training set from (a) end-of-game `P-game` positions, (b) synthetic living groups with two eyes of random shapes plus near-misses (one eye, false eye, eye containing an opponent stone), and (c) random positions. Balance classes to roughly one third each at the chain level.

**Information distance.** Log the Benson iteration count and the maximum chain diameter among affected chains. Plot `t_solve` against both and against their product.

**B3 reference.** The exact algorithm's iteration count times diameter.

**Splits.** Train 9x9, validate 13x13, test 9 to 37.

**Optional Phase 2b** (only if time remains after Phase 5): discrete rule extraction from the Phase 1 model. Run k-means with S in {4, 8, 16, 32} on non-frozen channel states pooled across rollouts, build a lookup table from 3x3 neighborhood cluster tuples to next cluster by majority vote, rerun it as a discrete CA on the 37x37 test set, and report accuracy and table size.

## 7. Phase 3: ladders

**Exact ladder reader** (AND-OR search, defender chain D, attacker A):

- D to move with 1 liberty. D's candidate moves are playing its liberty and capturing any adjacent A chain that is in atari. Skip illegal moves. After each candidate: 3 or more liberties means escaped, 1 liberty means captured (A takes it), 2 liberties means A's turn.
- A to move with D at 2 liberties. For each of D's two liberties where an A move is legal and leaves D in atari, it becomes D's turn.
- D is ladder-captured iff some A choice makes every D response end in capture. Memoize positions. Depth limit N^2.

**Labels.** L1: chains with 1 liberty, captured even with D to move. L2: chains with 2 liberties, capturable by ladder with A to move. Per-stone classes: {not applicable, ladder-captured, escapes}.

**Generator.** Canonical ladder starts at a random location and orientation, plus random breaker stones (D color) and maker stones (A color) placed near the diagonal path at random distances, plus random clutter elsewhere. Legalize, then label with the reader. Ladder length is the principal-variation length in moves. Balance captured vs escapes within each length bin. Mix in `P-game` positions containing 1- or 2-liberty chains.

**Information distance.** Chebyshev distance from the defender's start to the farthest point on the principal variation.

**Splits.** Train 9x9 (ladder lengths up to about 8). Validate 13x13. Test 19, 25, 37, with lengths up to about 35. Plot accuracy vs ladder length and `t_solve` vs ladder length with a fitted slope.

**KataGo reference (optional).** If KataGo is available, record its raw-net ownership sign for the defender chain on the 19x19 test positions (`kata-raw-nn` or analysis engine with `maxVisits: 1`). KataGo receives engineered ladder input features, so label this a reference point and keep it out of the baseline comparison.

## 8. Phase 4: cyclic groups

**4a (no external dependencies).** Build a matched-pair test set. For each ring chain (a cycle enclosing a region that holds opponent stones and/or empty points), build an open-path partner with the same stone count (within 1) and the same liberty class, made by breaking the cycle. Boards up to 37x37, ring perimeters up to about 120. Information distance for rings is half the perimeter. Evaluate the Phase 1 and Phase 2 models and all baselines on rings vs paths. Report the accuracy gap (ring minus path) per model with 95% bootstrap CIs. Hypothesis: fixed-depth CNNs show a larger gap than the NCA.

**4b (needs the Phase 5 model, KataGo, and the adversarial SGFs).** Get the adversarial game records from the FAR AI go_attack project (github.com/AlignmentResearch/go_attack, goattack.far.ai). Select positions 1 to 30 moves before the victim's cyclic group is captured. Ground truth: those group points are captured later in the game. Compare predicted ownership of the doomed points from KataGo raw net (`maxVisits: 1`), KataGo with 1,000 or more visits, and the Phase 5 NCA run to convergence. Report mean predicted ownership of the doomed group and the fraction of its points predicted as victim-owned.

## 9. Phase 5: distilled NCA player (stretch, start after Phases 1 to 4a are in the report)

**KataGo setup.** Download a release binary matching the hardware (CUDA, TensorRT, or OpenCL; Eigen on CPU) from github.com/lightvector/KataGo/releases and a network from katagotraining.org. Record versions. Rules `tromp-taylor`, komi 7.5 on all sizes. Set the analysis perspective explicitly (`reportAnalysisWinratesAs`) and verify it with a fixture where Black obviously owns a corner.

**Positions.** KataGo low-visit self-play (16 to 64 visits, 2 to 6 random opening moves) at 9x9, 13x13, 19x19. Sample positions uniformly over game length and dedupe by hash. Full profile: at least 500k 9x9 positions for training, 20k each of 13x13 and 19x19 for evaluation only. Smoke profile: 2k total.

**Teacher labels** from the analysis engine: raw policy over N^2 + 1 moves including pass (`includePolicy`, `maxVisits: 1`), ownership (`includeOwnership`), scoreLead, winrate. Also label a subset at 400 visits for a policy-after-search comparison.

**Inputs.** Stone planes for side to move and opponent, last 5 move planes, ko-ban plane, plus global scalars (komi, side to move) broadcast into dedicated frozen channels, the same way the paper injects the ARC task embedding. Do not use KataGo's ladder features or any engineered tactical features.

**Heads.** All local except one pooled readout. Per-cell move logit. Per-cell ownership (tanh). Pass logit and winrate from a pooled readout (mean and max over cells of the output slice). Score estimate is the sum of ownership plus the komi term, with no separate network.

**Loss.** Policy KL to teacher, ownership MSE, score MSE, winrate cross-entropy. Weights in config.

**Training and evaluation.** Train on 9x9 only. Evaluate policy top-1 agreement, policy KL, ownership MSE, and score error on 9, 13, 19 across a D sweep.

**Warm-start evaluation (NCA-specific).** After a move, start the child's evaluation from the parent's converged state with the new input board, which is exactly the paper's target-swap setting. Add an "advance one move" training perturbation with p = 0.1 (replace the board with the next position from the same game, keep the hidden state). Measure steps to reconverge for warm vs cold start, and log fire-count maps under adaptive firing.

**MCTS.** Batched PUCT in JAX or NumPy, `c_puct = 1.5`, NCA policy and winrate. Game length cap 2 x N^2 moves. Score finished games by removing dead stones with GnuGo `final_status_list dead`, then area scoring; cross-check a sample against KataGo ownership if available.

- vs GnuGo 3.8 (`apt-get install gnugo`, `--mode gtp --level 10 --chinese-rules --komi 7.5`) at 9x9 and 19x19, 200 games each, alternating colors, at NCA visits in {1, 16, 128}.
- vs KataGo raw net (1 visit) as a strength anchor.
- Same wall-clock budget, warm vs cold start.
- Report win rates with Wilson 95% CIs and Elo differences.

## 10. Visualization and final report (required)

Build `reports/nca_go_report.html` as one self-contained file (images and GIFs base64-embedded, opens offline), plus `reports/SUMMARY.md`. Save every figure as PNG (and SVG for line plots) in `reports/figures/`. `make report` regenerates everything from `results/` with no retraining.

**Board rendering.** Standard Go board look: light wood background, black grid lines, star points, black and white stones with thin outlines. Overlays are semi-transparent heatmaps with colorbars. Use one diverging colormap for ownership and one sequential colormap for confidence and fire counts across all figures. Colorblind-safe.

### Required sections and figures

1. **Capability map** (top of the page)
   - F1a. Heatmap with rows = tasks (liberties, atari, Benson, ladder L1, ladder L2, ring-vs-path, policy agreement, ownership) and columns = board sizes (9, 13, 19, 25, 37). Cell value = NCA accuracy, annotated with the delta vs the best fixed-depth baseline. Gray cells mean not run, with the reason in the caption.
   - F1b. "Where NCAs win" scatter. x = information distance (log scale), y = NCA accuracy minus best baseline accuracy, one point per (task, board size, distance bin), colored by task. Vertical lines at each B1 receptive-field radius.
   - T1. Verdict table computed by rule. "Use NCA" if NCA OOD accuracy is at least 95% and at least 2 points above the best baseline on the same split. "Use baseline" if the baseline is at least 2 points above the NCA. "Tie" otherwise. "Unknown" if not run. Columns: task, information-distance range, NCA accuracy (ID and OOD), best baseline accuracy (ID and OOD), compute per evaluation (FLOPs and ms), verdict, figure link.
2. **Substrate scaling.** F2: accuracy vs board size per task for NCA, B1 (L = 4, 8, 16), and B2, mean and std over seeds.
3. **Light cone.** F3: `t_solve` vs information distance per task, with the B3 reference and a slope-1 line, fitted slopes in the legend. Histogram of light-cone efficiency.
4. **How the NCA computes.** F4: 8-frame filmstrips plus GIFs for each showcase board, with panels for stones, decoded prediction overlay, confidence, hidden-state PCA as RGB, and fire mask. Include the 37x37 snake, a ring, a 19x19 ladder (show the signal traveling down the diagonal), a Benson position, and a 9x9 game position from Phase 5.
5. **Adaptive compute and repair.** F5a: cumulative fire-count heatmaps, uniform vs adaptive. F5b: accuracy vs total cell updates. F5c: damage injected mid-rollout, accuracy and cells updated over time, uniform vs adaptive (mirrors the paper's Figure 8).
6. **Ablations.** F6: OOD accuracy with each recipe component removed (Phases 1 and 3), plus Moore vs von Neumann.
7. **Test-time scaling.** F7: accuracy vs D and vs K (conf@K), with the noise sigma sweep.
8. **Cyclic groups.** F8a: ring-vs-path accuracy gap per model with CIs. F8b (if 4b ran): predicted ownership of doomed cyclic groups per model, with 3 annotated board examples.
9. **Distilled player** (if Phase 5 ran). F9a: policy agreement and ownership MSE vs board size (trained on 9x9 only). F9b: teacher vs NCA ownership maps on 3 19x19 positions. F9c: warm vs cold start steps-to-reconverge and fire maps after a move. T2: match results with CIs and Elo.
10. **Compute.** F10: FLOPs and wall-clock per evaluation vs board size, NCA (at the D needed for 95% of its final accuracy) vs baselines.
11. **Findings.** For each task, 2 to 3 sentences with the numbers, where it works, where it breaks, and the figure reference. Then a "Where to use NCAs in Go" paragraph and a "Where not to" paragraph, both drawn only from T1. Then a "Not run" list with reasons.

### Writing rules for all report text

Lead with the number. Plain language. No em dashes. No hype words. State negative results as plainly as positive ones. Every claim cites a figure or table.

## 11. Commands, order of work, deliverables

```
make setup                       # install deps, detect GPU, fetch optional binaries
make test                        # full pytest suite
make smoke                       # every phase on CPU with tiny data, then the report, under 30 min
make full PHASES="0 1 2 3 4a"
make full PHASES="5 4b"
make report                      # rebuild report from results/ only
```

**Order of work:** Phase 0, then the full smoke pipeline including the report, then full runs of Phases 1, 2, 3, 4a, then report v1, then Phase 5, then 4b, then the final report.

**Deliverables checklist:**

- `reports/nca_go_report.html` opens offline with every figure slot filled or marked not run.
- `reports/SUMMARY.md` with a key-numbers table and the T1 verdict table.
- `RESULTS_LOG.md` and `DECISIONS.md` up to date.
- All configs and seeds committed. One command reproduces each figure.
- `README.md` listing hardware used and wall-clock per phase.
