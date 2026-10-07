"""Small balanced liberty probes, separate from G1 and sealed final tests.

Only the constructed target chain is supervised. Every target chain has equal
loss weight, and every minibatch has equal counts of the four liberty classes.
This diagnoses optimization; it does not certify whole-board rule accuracy.
"""
import argparse
from dataclasses import asdict
from functools import partial
import hashlib
from pathlib import Path
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax
from flax import serialization

from ncago.go.generators import canonical_key, controlled_structure
from ncago.go.labels import liberties
from ncago.go.diverse import random_controlled_chain, component_key
from ncago.go.rules import chains, diameter
from ncago.nca.model import ModelConfig, NCA, initialize, init_params, step, readout
from ncago.nca.train import augment
from ncago.nca.hints import initial_ids, id_step, discovered_count
from .common import Run, write_json


VARIANTS = {
    "mse_all": ("mse", "all", 1.0),
    "mse_late": ("mse", "late", 1.0),
    "ce_late": ("ce", "late", 1.0),
    "ce_late_async": ("ce", "late", 0.8),
}


def locality_witness(size=13):
    """Identical query neighborhoods, different exact answers at a far end.

    For this pair, an output with a Chebyshev receptive-field radius smaller
    than size-3 cannot distinguish the two labels at the query stone.
    """
    if size < 7:
        raise ValueError("A locality witness needs size >= 7")
    row = size // 2
    one = np.zeros((size, size), np.int8)
    one[row, 1:size-1] = 1
    one[row-1, :size-1] = one[row+1, :size-1] = 2
    one[row, 0] = 2
    two = one.copy()
    two[row-1, size-2] = 0
    query = row, 1
    a, _ = liberties(one)
    b, _ = liberties(two)
    if (int(a[query]), int(b[query])) != (0, 1):
        raise AssertionError("Locality witness labels are not one and two liberties")
    return one, two, query, size-3


def balanced_targets(size, count, seed, exclude=(), board_sizes=(), diverse=False, component_dedup=False):
    if count <= 0 or count % 4:
        raise ValueError("count must be positive and divisible by four")
    rng = np.random.default_rng(seed)
    seen, boards, targets, metadata = set(exclude), [], [], []
    counts = np.zeros(4, np.int64)
    choices = tuple(board_sizes) or (size,)
    if min(choices) < 5 or max(choices) > size:
        raise ValueError("Training boards must fit the canvas and be at least 5x5")
    for _ in range(count * 1000):
        actual_size = int(rng.choice(choices)) if len(choices) > 1 else choices[0]
        constructor = random_controlled_chain if diverse and rng.random() < .5 else controlled_structure
        board, info = constructor(actual_size, rng, return_metadata=True)
        if actual_size < size:
            row, col = rng.integers(size-actual_size+1, size=2)
            canvas = np.full((size, size), 3, np.int8)
            canvas[row:row+actual_size, col:col+actual_size] = board
            board = canvas
            info["points"] = tuple((r+row, c+col) for r, c in info["points"])
        value = info["target_liberties"] - 1
        key = canonical_key(board)
        observable = component_key(board, info["points"]) if component_dedup else key
        if counts[value] >= count // 4 or key in seen or observable in seen:
            continue
        exact, _ = liberties(board)
        target = np.full(board.shape, -1, np.int32)
        for point in info["points"]:
            if exact[point] != value:
                raise AssertionError("Constructed chain disagrees with exact labels")
            target[point] = value
        chain = next(c for c in chains(board) if info["points"][0] in c.points)
        boards.append(board)
        targets.append(target)
        metadata.append({"class": value, "chain_size": len(chain.points),
                         "chain_diameter": diameter(chain), "board_size": actual_size})
        counts[value] += 1
        seen.add(key)
        seen.add(observable)
        if len(boards) == count:
            return np.stack(boards), np.stack(targets), metadata
    raise RuntimeError("Balanced target generator exhausted unique samples")


def chain_weighted_loss(model, params, state, target, class_balance=False):
    values = model.apply({"params": params}, state, method=model.logits)
    mask = target >= 0
    safe = jnp.maximum(target, 0)
    if model.config.readout == "ce":
        error = optax.softmax_cross_entropy_with_integer_labels(values, safe)
    else:
        error = jnp.sum((values - jax.nn.one_hot(safe, model.config.output_channels))**2, -1)
    if class_balance:
        class_masks = mask[..., None] & (safe[..., None] == jnp.arange(model.config.classes))
        counts = jnp.sum(class_masks, (0, 1, 2))
        totals = jnp.sum(class_masks * error[..., None], (0, 1, 2))
        return jnp.sum(totals / jnp.maximum(counts, 1)) / jnp.maximum(jnp.sum(counts > 0), 1)
    # One constructed chain per board: length cannot change its loss weight.
    per_board = jnp.sum(jnp.where(mask, error, 0), (1, 2)) / jnp.maximum(mask.sum((1, 2)), 1)
    return per_board.mean()


def scores(prediction, target, exact_key="target_chain_exact"):
    mask = target >= 0
    valid = prediction[mask]
    if np.any(valid < 0):
        raise FloatingPointError("Nonfinite rollout prediction")
    per_class, exact, predicted = [], [], np.bincount(valid, minlength=4)
    for value in range(4):
        eligible = target == value
        per_class.append(float((prediction[eligible] == value).mean()))
    for p, y, m in zip(prediction, target, mask):
        exact.append(bool(np.all(p[m] == y[m])))
    return {"macro_stone_accuracy": float(np.mean(per_class)),
            "per_class_accuracy": per_class,
            exact_key: float(np.mean(exact)),
            "stone_accuracy": float((prediction[mask] == target[mask]).mean()),
            "prediction_counts": predicted.tolist(),
            "constant_macro_baseline": 0.25}


def predict_batches(predict, params, boards, steps, key, batch_size):
    outputs = [np.asarray(predict(params, jnp.asarray(boards[start:start+batch_size]), steps,
                                  jax.random.fold_in(key, start)))
               for start in range(0, len(boards), batch_size)]
    return np.concatenate(outputs)


def train_probe(config, variant, train, seed, run):
    readout_kind, window, fire_rate = VARIANTS[variant]
    mc = ModelConfig(channels=config["channels"], heads=2, readout=readout_kind,
                     fire_rate=fire_rate, init_sigma=config["init_sigma"],
                     normalization_groups=config["normalization_groups"], gated=config["gated"],
                     algorithm_hints=config["hint_weight"] > 0, chain_messages=config["chain_messages"])
    model, key = NCA(mc), jax.random.PRNGKey(seed)
    boards, labels = train
    rng = np.random.default_rng(seed)
    class_ids = [np.flatnonzero(np.any(labels == value, axis=(1, 2))) for value in range(4)]
    chain_sizes = np.sum(labels >= 0, axis=(1, 2))
    learning_rate = (optax.cosine_decay_schedule(config["learning_rate"], config["training_steps"], alpha=.02)
                     if config["cosine_decay"] else config["learning_rate"])
    optimizer = optax.chain(optax.clip_by_global_norm(1.0), optax.adam(learning_rate))
    initial = initialize(jnp.asarray(boards[:config["batch_size"]]), key, mc)
    params = init_params(model, initial, key)
    ema = params
    opt_state = optimizer.init(params)
    depth, late = config["rollout_steps"], config["late_steps"]
    if config["replay"]:
        pool_classes = np.repeat(np.arange(4), config["batch_size"])
        pool_ids = np.array([rng.choice(class_ids[value]) for value in pool_classes])
        pool_tokens, pool_targets = boards[pool_ids].copy(), labels[pool_ids].copy()
        pool_states = np.asarray(initialize(jnp.asarray(pool_tokens), key, mc)).copy()

    @jax.jit
    def update(p, opt, average, tokens, target, incoming, iteration_key):
        horizon = (jax.random.randint(jax.random.fold_in(iteration_key, 9999), (),
                                     config["min_depth"], depth+1)
                   if config["min_depth"] else depth)
        def objective(weights):
            # The caller can seed every slot during warmup before introducing replay.
            state = incoming
            def body(carry, index):
                s, total, teacher, reported = carry
                s, firing = step(model, weights, s, tokens,
                                 jax.random.fold_in(iteration_key, index))
                reported = jnp.where(index == horizon-1, s, reported) if config["min_depth"] else s
                if mc.algorithm_hints:
                    teacher = id_step(teacher, tokens, firing)
                    hint_target = discovered_count(teacher, tokens)
                    hint_logits = model.apply({"params": weights}, s, method=model.hint_logits)
                    hint_error = optax.softmax_cross_entropy_with_integer_labels(hint_logits, hint_target)
                    hint_mask = target >= 0
                    hint_classes = hint_mask[..., None] & (hint_target[..., None] == jnp.arange(5))
                    hint_counts = jnp.sum(hint_classes, (0, 1, 2))
                    hint_totals = jnp.sum(hint_classes*hint_error[..., None], (0, 1, 2))
                    hint_loss = jnp.sum(hint_totals/jnp.maximum(hint_counts, 1)) / jnp.maximum(jnp.sum(hint_counts > 0), 1)
                else:
                    hint_loss = 0.
                eligible = index < horizon
                if window != "all":
                    eligible &= index >= horizon - late
                if config["min_depth"]:
                    loss = jnp.where(eligible, chain_weighted_loss(model, weights, s, target,
                                                                  config.get("whole_board", False)), 0.)
                    # Fixed execution avoids GPU conditional synchronization.
                    # After the sampled horizon, dummy work is disconnected
                    # from both the objective and the returned replay state.
                    s = jnp.where(index < horizon-1, s, incoming)
                else:
                    loss = jax.lax.cond(eligible, lambda _: chain_weighted_loss(model, weights, s, target,
                                                                              config.get("whole_board", False)),
                                        lambda _: jnp.array(0.0), None)
                loss_normalizer = depth if window == "all" else late
                return (s, total + loss + config["hint_weight"]*hint_loss*loss_normalizer/depth, teacher, reported), None
            (_, total, _, final), _ = jax.lax.scan(body, (state, jnp.array(0.0), initial_ids(tokens), state), jnp.arange(depth))
            return total / (horizon if window == "all" else late), final
        (loss, final), grads = jax.value_and_grad(objective, has_aux=True)(p)
        updates, opt = optimizer.update(grads, opt, p)
        p = optax.apply_updates(p, updates)
        average = jax.tree_util.tree_map(lambda old, new: config["ema_decay"]*old + (1-config["ema_decay"])*new,
                                         average, p)
        return p, opt, loss, optax.global_norm(grads), final, average

    @partial(jax.jit, static_argnames=("steps",))
    def predict(p, tokens, steps, trial_key):
        state = initialize(tokens, trial_key, mc)
        def body(s, index):
            return step(model, p, s, tokens, jax.random.fold_in(trial_key, index))[0], None
        final, _ = jax.lax.scan(body, state, jnp.arange(steps))
        return readout(model, p, final)[0]

    started = time.perf_counter()
    for iteration in range(config["training_steps"]):
        iteration_key = jax.random.fold_in(key, iteration + 1)
        cap = 8 if iteration < config["training_steps"] // 4 else 16 if iteration < config["training_steps"] // 2 else np.inf
        eligible_ids = [indices[chain_sizes[indices] <= cap] if config["curriculum"] else indices
                        for indices in class_ids]
        eligible_ids = [eligible if len(eligible) else indices for eligible, indices in zip(eligible_ids, class_ids)]
        ids = np.concatenate([rng.choice(indices, config["batch_size"] // 4, replace=True)
                              for indices in eligible_ids])
        tokens, target = boards[ids].copy(), labels[ids].copy()
        incoming = np.asarray(initialize(jnp.asarray(tokens), iteration_key, mc)).copy()
        if config["replay"]:
            slots = np.concatenate([rng.choice(np.flatnonzero(pool_classes == value),
                                                config["batch_size"] // 4, replace=False)
                                    for value in range(4)])
            fresh = (rng.random(config["batch_size"]) < config["seed_fraction"]
                     if iteration >= config["warmup_steps"] else np.ones(config["batch_size"], bool))
            incoming[~fresh] = pool_states[slots[~fresh]]
            tokens[~fresh], target[~fresh] = pool_tokens[slots[~fresh]], pool_targets[slots[~fresh]]
        if config["augmentation"]:
            incoming, tokens, target = augment(incoming, tokens, target, "liberties", rng, mc)
        params, opt_state, loss, grad_norm, final, ema = update(params, opt_state, ema, jnp.asarray(tokens),
                                                               jnp.asarray(target), jnp.asarray(incoming), iteration_key)
        if config["replay"]:
            pool_states[slots], pool_tokens[slots], pool_targets[slots] = np.asarray(final), tokens, target
        if not np.isfinite(float(loss)):
            raise FloatingPointError(f"{variant}: nonfinite loss at update {iteration + 1}")
        if iteration == 0 or (iteration + 1) % config["log_every"] == 0 or iteration + 1 == config["training_steps"]:
            prediction = predict_batches(predict, ema, boards, depth, jax.random.fold_in(key, 100000),
                                         config["evaluation_batch_size"])
            exact_key = "board_exact" if config.get("whole_board", False) else "target_chain_exact"
            measured = scores(prediction, labels, exact_key)
            run.log(event="learnability_train", variant=variant, iteration=iteration + 1,
                    loss=float(loss), gradient_norm=float(grad_norm), **measured)
            print(f"{variant} C={mc.channels} {iteration + 1}: loss={float(loss):.4f}, "
                  f"train macro={measured['macro_stone_accuracy']:.3f}, "
                  f"exact={measured[exact_key]:.3f}", flush=True)
    (run.path / "ckpt" / f"{variant}.msgpack").write_bytes(serialization.to_bytes(ema))
    return model, ema, predict, {"model_config": asdict(mc), "training_seconds": time.perf_counter() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=1200)
    parser.add_argument("--count", type=int, default=32)
    parser.add_argument("--train-sizes", type=int, nargs="+", default=[9],
                        help="Mix board sizes <=9 using frozen off-board canvas padding")
    parser.add_argument("--whole-board", action="store_true",
                        help="Supervise all stones on a mix of random and controlled boards")
    parser.add_argument("--diverse-chains", action="store_true")
    parser.add_argument("--chain-messages", action="store_true",
                        help="Restrict mutable messages to orthogonal same-color neighbors")
    parser.add_argument("--validation-count", type=int)
    parser.add_argument("--channels", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--evaluation-batch-size", type=int, default=128)
    parser.add_argument("--normalization-groups", type=int, default=0)
    parser.add_argument("--depth", type=int, default=16)
    parser.add_argument("--min-depth", type=int, default=0,
                        help="Sample training horizons uniformly from min-depth through depth")
    parser.add_argument("--late-steps", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--replication-of", help="Record the source run for an unchanged recipe replication")
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--log-every", type=int, default=200)
    parser.add_argument("--init-sigma", type=float, default=0.0)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--augment", action="store_true")
    parser.add_argument("--curriculum", action="store_true")
    parser.add_argument("--warmup-steps", type=int, default=0)
    parser.add_argument("--require-gpu", action="store_true")
    parser.add_argument("--cosine-decay", action="store_true")
    parser.add_argument("--ema-decay", type=float, default=0.0)
    parser.add_argument("--gated", action="store_true")
    parser.add_argument("--hint-weight", type=float, default=0.,
                        help="Auxiliary loss on exact local intermediate discovery counts")
    parser.add_argument("--variants", nargs="+", choices=list(VARIANTS), default=list(VARIANTS))
    args = parser.parse_args()
    if args.steps < 1 or not 0 < args.late_steps <= args.depth:
        parser.error("Positive training steps and a valid late loss window are required")
    if args.min_depth and not args.late_steps <= args.min_depth <= args.depth:
        parser.error("Random horizons must include the complete late loss window")
    if args.batch_size < 4 or args.batch_size % 4 or not 0 <= args.warmup_steps <= args.steps:
        parser.error("Batch size must be divisible by four, and warmup must be within training")
    if not 0 <= args.ema_decay < 1:
        parser.error("EMA decay must be in [0, 1)")
    if args.hint_weight < 0 or (args.hint_weight and (args.replay or args.min_depth)):
        parser.error("Hint weight must be nonnegative; hints currently require fresh, fixed-horizon rollouts")
    if args.require_gpu and not any(device.platform == "gpu" for device in jax.devices()):
        raise RuntimeError("GPU required; refusing to run this sweep on CPU")
    config = {"profile": "diagnostic", "task": "whole_board_liberties" if args.whole_board else "target_chain_liberties", "training_steps": args.steps,
              "train_count": args.count, "validation_count": args.validation_count or args.count, "channels": args.channels,
              "train_sizes": args.train_sizes,
              "replication_of": args.replication_of,
              "diverse_chains": args.diverse_chains, "chain_messages": args.chain_messages,
              "batch_size": args.batch_size, "rollout_steps": args.depth, "late_steps": args.late_steps,
              "evaluation_batch_size": args.evaluation_batch_size,
              "min_depth": args.min_depth,
              "normalization_groups": args.normalization_groups, "curriculum": args.curriculum,
              "warmup_steps": args.warmup_steps,
              "cosine_decay": args.cosine_decay, "ema_decay": args.ema_decay, "gated": args.gated,
              "hint_weight": args.hint_weight,
              "learning_rate": args.learning_rate, "init_sigma": args.init_sigma,
              "log_every": args.log_every, "variants": args.variants, "seed_fraction": 0.25,
              "test_sizes": [], "selection": "final EMA; no checkpoint selection" if args.ema_decay else "final update; no checkpoint selection",
              "replay": args.replay, "noise": False, "damage": False, "target_swap": False,
              "augmentation": args.augment, "whole_board": args.whole_board,
              "supervision": "all stones, class-balanced minibatch loss" if args.whole_board else "one constructed chain per board, balanced by chain",
              "data_seeds": {"train": 73001, "validation9": 73002, "validation13": 73003}}
    run = Run("learnability", config, args.seed)
    source = Path(__file__)
    (run.path / "source.py").write_bytes(source.read_bytes())
    run.log(event="source_snapshot", sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    splits, used = {}, set()
    for name, size, seed in (("train", 9, 73001), ("validation9", 9, 73002), ("validation13", 13, 73003)):
        count = config["train_count"] if name == "train" else config["validation_count"]
        if args.whole_board:
            from ncago.go.generators import generate
            if args.train_sizes != [9]:
                raise ValueError("Whole-board diagnostic currently trains only on full 9x9 boards")
            boards, sources = generate("liberties", size, count, seed, "mixed", used, controlled=True)
            labels = np.stack([liberties(board)[0] for board in boards])
            info = {"sources": sources, "supervised_stones_per_class":
                    [int(np.sum(labels == value)) for value in range(4)]}
        else:
            boards, labels, info = balanced_targets(size, count, seed, used,
                                                   args.train_sizes if name == "train" else (),
                                                   diverse=args.diverse_chains,
                                                   component_dedup=args.chain_messages)
        used.update(canonical_key(b) for b in boards)
        if args.chain_messages and not args.whole_board:
            used.update(component_key(b, np.argwhere(y >= 0)) for b, y in zip(boards, labels))
        splits[name] = boards, labels
        np.savez_compressed(run.path / "data" / f"{name}.npz", boards=boards, labels=labels)
        write_json(run.path / "data" / f"{name}_metadata.json", info)
    records = []
    try:
        for variant in args.variants:
            model, params, predict, stats = train_probe(config, variant, splits["train"], args.seed, run)
            for name, (boards, labels) in splits.items():
                for depth in sorted({args.depth, 2 * args.depth, 4 * args.depth}):
                    for trial in range(3 if model.config.fire_rate < 1 else 1):
                        pred = predict_batches(predict, params, boards, depth,
                                               jax.random.PRNGKey(200000 + trial), args.evaluation_batch_size)
                        result = {"variant": variant, "split": name, "depth": depth,
                                  "trial": trial, **scores(pred, labels, "board_exact" if args.whole_board else "target_chain_exact"), **stats}
                        records.append(result)
                        run.log(event="learnability_eval", **result)
    except Exception as error:
        run.finish("failed", accuracy_gate_certified=False,
                   error_type=type(error).__name__, error=str(error), records=records)
        raise
    write_json(run.path / "eval" / "scores.json", records)
    summary = run.finish("measured", accuracy_gate_certified=False,
                         limitation="Diagnostic training/validation only; no sealed final G1 or OOD test evaluated",
                         records=records)
    print(f"Saved diagnostic: {run.path}", flush=True)
    return summary


if __name__ == "__main__":
    main()
