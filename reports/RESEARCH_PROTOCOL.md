# Follow-up research protocol

Protocol recorded before any new final larger-board evaluations. Old test sets
are used only in the descriptive checkpoint audit. New recipe selection uses
the `research_validation` 9x9 and 13x13 namespace. Large final sets will be
generated in a separate frozen namespace after the recipe is selected.

1. Audit old errors by exact chain diameter, cycles (E >= V), chain size and
   nearest edge. Distinguish chain-routing distance from the grid receptive
   field: for the Moore NCA, a cell's strict radius at step D is D in Chebyshev
   distance. A large chain diameter alone is not an impossibility proof.
2. Online whole-board training draws legal random playouts and controlled
   structures equally, sizes 5--9 equally, with off-board padding on a 9x9
   canvas. All stone labels are supervised; class-balanced cross entropy.
   Replay has 4B slots, 25% fresh states after a 5,000-update fresh warmup.
   Horizons are uniform integer draws from 32 through 128. The last eight
   steps receive cross entropy and a mutable-state change penalty (0.1).
   The noise schedule is p_time=.1, p_cell=.2, sigma=.15. Damage probability
   .1 resets 1--3 circular patches, radius .1--.4 of the grid width. Target
   swapping probability .1 updates static board clues and all labels.
   All frozen token and ID channels are protected from damage and noise.
3. The user's stability gate requires absolute accuracy change <=0.2 percentage
   points at D512 and D1024 relative to D128 on new 9x9 validation.
   Accuracy and class-balanced accuracy are reported separately. Scaling also
   requires >=95% macro accuracy, to exclude stable collapsed predictors.
   Also report D32 and D64. D128 is the largest trained horizon; testing only
   D128 as "4x" would under-test a model already trained at that depth.
4. Main random-ID variant has 32 independent frozen +/-1 channels per cell,
   renewed at every rollout including replay chunks. The 16-channel ablation
   and a hand-coded smallest-four-distinct-ID reference measure collisions.
   ID sensitivity uses eight ID draws with the same firing randomness; report
   accuracy range AND disagreement, including pair-both-correct range.
   IID finite IDs are not guaranteed unique. Exact reference claims require
   distinct liberty IDs; collisions are never silently repaired.
   A zero-ID control reserves the same32 frozen channels and total width as
   the32-bit model. This isolates random IDs from the capacity increase.
5. Once the stability and ID gates pass, final evaluation uses D/diameter
   ratios .5, 1, 2 and 4, plus fixed depths. Report stone and macro accuracy,
   over/under confusion, and board exactness. Witnesses use five geometries
   per size (straight, elbow, snake, comb, ring), three training seeds and
   pair-both-correct as the primary metric. Pair members share all random
   channels and firing masks. Group uncertainty by boards/pairs, not stones.
6. Matched baselines use the identical deterministic online candidate stream,
   replay board choices and augmentation sequence, optimizer update counts,
   and batch size. Report parameter count and actual runtime, without claiming
   equal FLOPs. The ResNet has 18 residual blocks and radius37; the recurrent
   CNN ties its two-convolution update; the stone GNN compares sum vs max
   with identical architecture and parameter initialization otherwise.
   Any pretrained NCA warmstart is exploratory and excluded from matched
   from-scratch model comparisons.
7. After the first three steps pass, separately train capped-at-16 liberty
   counts, static simple-eye counts with diagonal false-eye checks and two-group capturing-race
   labels. Minimal cyclic/broken-cycle pairs control labels where possible.
   Unknown search outcomes remain unknown. These are synthetic diagnostic
   tasks, not evidence of defeating or repairing a KataGo adversary.
8. Benson, ladders and playing strength remain parked until steps1--3 pass.

Perturbations follow [Reasoning with Neural Cellular Automata](https://arxiv.org/html/2609.36126v1).
Cycle-pair design is motivated by Appendix K of
[Adversarial Policies Beat Superhuman Go AIs](https://arxiv.org/pdf/2211.00241).

## Stability pilot extension (before larger final tests)

The first10k-update full-perturbation warmstart deteriorated after replay began
and missed the depth gate. Test a drift weight of10 and omit the optional target
swap, while retaining the requested damage and Gaussian noise. Candidate
selection still uses only9/13 validation. A unit-ball projection variant with
four mutable groups is the next prespecified rescue if needed. These warmstart
pilots are excluded from matched from-scratch comparisons.

The unit-ball rescue is run alongside the stronger-penalty pilot after its
first two checkpoints still showed deep drift. Both start from the same
completed exploratory checkpoint and use identical candidate board streams.

Before primary ID training or final tests, the extra99.5% floor introduced by
the initial implementation was removed: it was not part of the user's gate.
The exact relative gate is now reported separately from a >=95% macro-accuracy
usefulness flag. Earlier run summaries retain their original definitions;
comparison tables recompute and label the user's criterion from their raw
metrics. This correction does not turn the completed10k pilot into a pass.

## ID optimization diagnostic (before larger final tests)

The unscaled32-ID scratch replicas initially plateaued near70% validation
accuracy. Test a separately labeled10k-update pilot with perceived IDs scaled
by1/sqrt(32). Frozen inputs remain IID ±1 and are still renewed every rollout;
only their contribution to the first learned perception is preconditioned.
This puts their aggregate input variance near that of the board token planes.
The original unscaled runs continue and remain reported. Any selected change
must be replicated with three new seeds and matched baselines before final
large tests. No large final data has been opened for recipe selection.

The eye task now counts distinct simple-eye points adjacent to each chain,
including interior and edge/corner diagonal false-eye checks as in
[KataGo's board helper](https://github.com/lightvector/KataGo/blob/master/cpp/game/board.cpp).
It does not label unconditional life. Cycle controls use a genuine one-point
ring with five scalable tree tails; one corner color change preserves the eye
and exact liberty set while breaking the stone cycle.

The race distribution uses regular5×N rectangular Go boards with two initial
groups and no internal walls. Group lengths grow with N; wall tokens pad only
the outside of the rectangle. Labels are proved first-target-capture minimax
outcomes with suicide prohibited, simple ko and two-pass draws. Search depth,
node or repetition cutoffs stay unknown. This is a finite capture game, not
full-game Go or unrestricted semeai adjudication. Separate equal-liberty
witnesses change a two-point eye using two stones: both groups have six
liberties, yet independently solved outcomes change. They are distinct from
label-preserving cycle controls and cannot establish a cycle-only causal effect.

A second10k diagnostic sets the ID input kernel rows initially to zero, with
all those weights remaining trainable and the frozen channels still IID ±1.
It begins by attending to board clues; correlations between repeated liberty
IDs must then earn their contribution through learning. This changes only
initialization, not labels, capacity or the available input information.
Original, scaled and zero-initialized pilots are selected only on9/13
validation; any winning recipe needs three independent scratch replicas.

A replay-consistency diagnostic holds each ID field fixed across continuation
chunks of one seeded trajectory. Fresh trajectory seeds and every test draw
always receive new independent IDs. The original chunk-resampling runs remain
reported. Replacing IDs while retaining mutable messages can make a simple
monotone ID-union reference count stale and current names for one liberty;
this illustrates a protocol issue, not a demonstrated neural failure cause.
The trajectory pilot stops at10k but uses the same30k cosine schedule as the
original, allowing a matched-prefix comparison at update10k. With fresh IDs
assigned after augmentation, the first5k fresh-only prefix has identical
inputs, noise and initialization; differences begin when replay starts.
The interpretation of a rollout is explicit: a pool trajectory includes its
continuation chunks. If each chunk is regarded as a new rollout, this policy
relaxes the original resampling rule and must be labeled as such.

Race domain clarification recorded during sealed evaluation: random race
training and whole-board tests use5×N rectangles on padded N×N canvases.
The separately proved two-point-eye witnesses and invariant cycle controls
use full N×N boards. Their scores therefore also test a board-domain and
generator-family shift. This corrects the earlier animation annotation;
frozen boards, labels, checkpoints and saved rollout states are unchanged.

## Prospective three-seed ID rescue (before final large data)

The whole-board projected-state pilot passed the full depth gate at99.746%
(D128) and99.741%(D1024). The initial three unscaled-ID runs are still learning
far below the useful-accuracy threshold. Start a new three-seed scratch cohort
with four-group unit-ball projection,1/sqrt(32) ID perception scaling, and
fixed IDs across replay continuation chunks. Keep the original noise, damage,
target swaps,64-board batch and online data stream. The rescue uses20k updates
with a30k cosine schedule and a32-step gradient window. The forward horizon
still spans32--128 and replay carries mature states across chunks. This
combined rescue is a recipe test; it does not identify any one change as the
cause. The separate pilots continue and all completed attempts are reported.
Matched primary baselines will use this same recipe and data, with their exact
parameter budgets disclosed. Extra seeds of the original baselines wait while
the primary qualification runs finish. No new large-model tests were opened.

The shorter-window implementation separates an untracked forward prefix from
32 differentiable late steps. All actual steps still receive training noise.
Forward states, supervised losses and late drift are checked against the full
scan on nonzero model weights; only the gradient history is shortened. Matched
primary baselines use the same20k update budget and32-step gradient window.
The original30k full-BPTT experiments remain separate exploratory cohorts.

The final checkpoint manifest explicitly designates the prospective three-seed primary cohort. Failed variants can be sealed as diagnostics without qualifying them as primary results. All primary seeds must share one recipe and scratch initialization. The separate eye-count witness uses five tree geometries: a one-stone diagonal change breaks a cycle and changes the static eye count from1 to0 at the same exact liberty set. Because the diagonal also changes, this tests distant outcome sensitivity rather than a cycle-only causal effect.

The main witness cohort has three independent training seeds. Matched ResNet, recurrent-CNN, sum-GNN and max-GNN diagnostics use seed0 each; their comparison is preliminary and does not provide across-training-seed uncertainty. The primary ID qualification uses eight fresh ID fields with fixed firing keys; the9x9 D128 accuracy range must be at most0.2 percentage points. Prediction disagreement is reported separately and need not be zero. The cap16 invariant cycle pairs span all sixteen requested count classes, so the cap4 ceiling cannot hide disagreements among counts5--15.

## Prospective30k extension (final tests still sealed)

The20k rescue seed0 passed depth stability at98.275% D128 and98.291% D1024, but its range across eight ID fields was0.289 percentage points, failing the prespecified0.2-point ID threshold. Extend all three scratch seeds to30k with the existing30k cosine schedule and every other recipe setting unchanged. Because optimizer and replay state were not serialized, these are scratch reruns; compare the first20k prefix against the recorded20k runs. Matched baselines and the zero-ID capacity control receive the same30k update budget. The completed20k cohort and all prior attempts remain reported. No final large-board data has been generated or opened.

## Baseline witness replication extension (before final data)

Extend the matched30k ResNet, recurrent CNN, sum GNN, max GNN and zero-ID capacity control to three independent training seeds each. This supersedes the earlier one-seed preliminary comparison. Candidate and supervised streams,30k optimizer budget and batch size64 remain identical. Baseline seed0 pilots remain recorded. Additional seeds start after the current workers reach a natural training boundary and their automatic runtime guard is reset; active optimization is not interrupted for a restart. Primary and baseline checkpoints are all sealed before generating the main larger final namespace.

The richer-task learned diagnostics will also use three scratch training seeds each,20k updates on their existing30k schedule. Their fixed oracle/reference and race-heuristic controls remain separate from the main neural architecture comparison. Main liberty witnesses use five geometries; the richer first-capture witness is explicitly one synthetic two-point-eye family, not a replication of FAR attack positions.

## Exact race-stream delivery acceleration (before final data)

The first three race replicas were CPU-bound by repeated exact-oracle calls:
the loaded A100 host took36.1 seconds for1,280 candidate boards, compared with
4.2 seconds locally. Materialize the prescribed20k candidate stream once using
the original online generator, exact oracle, data seed and validation exclusions.
Replicas then consume those same boards and labels in the same order. Candidate
and supervised stream hashes remain checked, and their replay, augmentation,
IDs, horizons, optimizer and update budget stay prescribed. Labels are restored
to their original int32 dtype before hashing and training. This richer-task
delivery change is disclosed separately; the main whole-board experiments use
online generation throughout.

A cache test compared every board, label, dtype, canonical hash and consumed
candidate digest with fresh generation and checked corruption rejection. Run
three new scratch seeds using this delivery after the complete stream is
checksum-sealed. Preserve the slow original attempts and stop them only at a
saved checkpoint boundary. Compare their saved-prefix validation metrics and
weights against the corresponding accelerated runs wherever available. No
larger final data or model predictions were used for this performance decision.

Before any new final data were generated, extend the cap16 outcome witnesses
to adjacent true counts1/2,5/6,6/7,8/9,10/11,12/13,14/15 and15/16 in each of
the five geometries, eight pairs per geometry and size. This tests distant
information above the old cap4 ceiling. The main cap4 witnesses keep their
original1/2 construction. The cap16 animation uses the first snake pair above
cap4, selected before predictions. Exact labels, one changed stone and causal
distances are verified independently across all five final board sizes.

## Prediction-preserving evaluation batching

After the eye cohort was sealed and its original evaluator dispatched, reduce
compilation overhead for later evaluations by padding ragged diameter buckets
to16 boards with repeated copies of their last member. Real boards retain
their original indices, ID/fire keys and exact horizons; extra independent
predictions are discarded. No model or data recipe changes. Nonzero-parameter
checks across NCA, recurrent CNN, ResNet, sum GNN and max GNN produced identical
predictions with and without padding, for both individual and paired random
keys, on CPU and A100. All23 CPU research checks passed. The active eye queue
retains its original source; later queues use a separate immutable checkout.
