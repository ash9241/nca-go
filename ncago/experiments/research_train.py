"""Online whole-board stability/identifier experiments and matched baselines.

No final larger-board sets are read by this trainer. Recipe selection uses
only the new 9x9 and 13x13 validation namespace. Every run records its online
board stream digest, including rejected validation duplicates.
"""
import argparse
from dataclasses import asdict
from functools import partial
import json
from hashlib import sha256
from pathlib import Path
import time
import numpy as np
import jax
import jax.numpy as jnp
import optax
from flax import serialization
from ncago.nca.model import ModelConfig, NCA, initialize, frozen_inputs, init_params, step, readout, perception_inputs, identifier_kernel_init
from ncago.nca.train import augment, perturb
from ncago.baselines.resnet import ResNet, parameter_count, matched_width
from ncago.baselines.research import RecurrentCNN, StoneGNN
from ncago.go.research_data import OnlineStream, OnlinePrefetch
from ncago.go.generators import canonical_key
from .common import ROOT, Run, write_json


DEFAULT = dict(training_steps=30000, batch_size=64, learning_rate=.0005,
               min_depth=32, max_depth=128, late_steps=8, change_weight=.1,
               channels=64, identifier_channels=0, seed_fraction=.25,
               warmup_steps=5000, noise_sigma=.15, damage=True, target_swap=True,
               ema_decay=.99, data_seed=91001, cap=4, log_every=1000,
               checkpoint_every=5000, gradient_window=128,
               validation_count=512, validation_seed=91002,
               normalization_groups=0, init_sigma=0., model="nca", task="liberties", reserved_identifier_channels=0,
               online_prefetch=True, identifier_input_scale=1., identifier_zero_init=False,
               identifier_replay_policy="chunk", schedule_steps=None)


def refresh_frozen_inputs(incoming, tokens, key, mc, fresh, policy, input_factory=None):
    """Replay chunks may continue a seeded trajectory with its fixed ID field.

    Fresh seeds always draw new IDs. The original chunk policy renews IDs
    even when continuing mutable state; trajectory policy retains those IDs.
    """
    if policy not in ("chunk", "trajectory"):
        raise ValueError("Unknown identifier replay policy")
    inputs = np.asarray(input_factory(jnp.asarray(tokens), key) if input_factory else frozen_inputs(jnp.asarray(tokens), key, mc))
    base = mc.input_channels-mc.identifier_channels
    incoming[..., :base] = inputs[..., :base]
    if mc.identifier_channels:
        if policy == "chunk":
            incoming[..., base:mc.input_channels] = inputs[..., base:mc.input_channels]
        else:
            incoming[fresh, ..., base:mc.input_channels] = inputs[fresh, ..., base:mc.input_channels]
    return incoming


def validation_data(config):
    prefix = "" if config["task"] == "liberties" else ("simple_eyes_" if config["task"] == "eyes" else "regular_race_")
    root = ROOT / "results/research_validation" / f"{prefix}cap{config['cap']}_n{config['validation_count']}_s{config['validation_seed']}"
    root.mkdir(parents=True, exist_ok=True)
    result = {}
    for size in (9, 13):
        path = root / f"val_{size}.npz"
        if not path.exists():
            stream = OnlineStream(config["validation_seed"]+size, (size,), size, config["cap"], task=config["task"])
            boards, labels = stream.draw(config["validation_count"] if size == 9 else config["validation_count"]//2)
            np.savez_compressed(path, boards=boards, labels=labels)
        with np.load(path) as d:
            result[size] = d["boards"], d["labels"]
    return result


def build_model(config):
    ids = config["identifier_channels"]
    slots = max(ids, config.get("reserved_identifier_channels", 0))
    # Hold mutable memory fixed when adding identifiers.
    mc = ModelConfig(channels=config["channels"]+slots, input_channels=8+slots,
                     output_channels=max(4, config["cap"]), classes=config["cap"],
                     heads=2, readout="ce", fire_rate=.8 if config["model"] == "nca" else 1.,
                     init_sigma=config["init_sigma"], gated=True,
                     normalization_groups=config["normalization_groups"], identifier_channels=ids,
                     identifier_input_scale=config.get("identifier_input_scale", 1.),
                     identifier_zero_init=config.get("identifier_zero_init", False))
    if config["model"] == "nca":
        return NCA(mc), mc
    if config["model"] == "rcnn" or config["model"].startswith("gnn_"):
        from dataclasses import replace
        # Closed-form counts mirror the actual modules and include readout.
        # Pick the nearest total parameter budget; report the exact count.
        total, frozen, classes = mc.channels, mc.input_channels, mc.classes
        budget = (18*total*total+2*total + 4*total*total+2*total
                  + 4*total*total+2*total + mc.output_channels*classes+classes)
        def count(width):
            mutable = width-frozen
            if config["model"] == "rcnn":
                return 19*width*width+3*width+mc.output_channels*classes+classes
            return (9*frozen*width+width + (2*mutable+width)*2*width+2*width
                    + 4*width*mutable+2*mutable+mc.output_channels*classes+classes)
        minimum = frozen+mc.output_channels+1
        groups = config["normalization_groups"]
        candidates = [width for width in range(minimum, 513) if not groups or (width-frozen) % groups == 0]
        chosen = min(candidates, key=lambda width: abs(count(width)-budget))
        mc = replace(mc, channels=chosen)
        if config["model"] == "rcnn":
            return RecurrentCNN(mc), mc
        return StoneGNN(mc, aggregation=config["model"].split("_")[1]), mc
    if config["model"] == "resnet":
        # Radius 37 covers every cell of a 37x37 board at every output.
        nca = NCA(mc)
        state = initialize(jnp.zeros((1, 9, 9), jnp.int32), jax.random.PRNGKey(0), mc)
        budget = parameter_count(init_params(nca, state, jax.random.PRNGKey(0)))
        width = matched_width(budget, 18, config["cap"], mc.input_channels)
        return ResNet(config["cap"], blocks=18, width=width, residual_scale=18**-.5,
                      stem_initializer=identifier_kernel_init(mc)), mc
    raise ValueError(config["model"])


def balanced_loss(logits, target, classes):
    safe, mask = jnp.maximum(target, 0), target >= 0
    errors = optax.softmax_cross_entropy_with_integer_labels(logits, safe)
    eligible = mask[..., None] & (safe[..., None] == jnp.arange(classes))
    counts = jnp.sum(eligible, axis=(0, 1, 2))
    totals = jnp.sum(eligible*errors[..., None], axis=(0, 1, 2))
    return jnp.sum(totals/jnp.maximum(counts, 1))/jnp.maximum(jnp.sum(counts > 0), 1)


def class_names(task, cap):
    if task == "race":
        return ["Black capture", "White capture", "draw"]
    if task == "eyes":
        return [str(i) for i in range(cap-1)]+[str(cap-1)+"+"]
    return [str(i) for i in range(1, cap)]+[str(cap)+"+"]


def metrics(prediction, labels, classes, task="liberties"):
    mask = labels >= 0
    if np.any(prediction[mask] < 0):
        raise FloatingPointError("Nonfinite evaluation prediction")
    matrix = np.bincount(classes*labels[mask]+prediction[mask], minlength=classes**2).reshape(classes, classes)
    counts = matrix.sum(axis=1)
    supported = counts > 0
    per_class = [float(matrix[i, i]/counts[i]) if counts[i] else None for i in range(classes)]
    return dict(stone_accuracy=float(np.trace(matrix)/matrix.sum()),
                macro_accuracy=float(np.mean(np.diag(matrix)[supported]/counts[supported])),
                per_class_accuracy=per_class, confusion=matrix.tolist(),
                board_exact=float(np.mean(np.all((prediction == labels) | ~mask, axis=(1, 2)))),
                classification_errors=int(matrix.sum()-np.trace(matrix)),
                overcounts=int(np.triu(matrix, 1).sum()) if task != "race" else None,
                undercounts=int(np.tril(matrix, -1).sum()) if task != "race" else None)


def stability_assessment(results):
    nine = {depth: float(np.mean([r["stone_accuracy"] for r in results if r["size"] == 9 and r["depth"] == depth]))
            for depth in (32, 64, 128, 512, 1024)}
    macro = float(np.mean([r["macro_accuracy"] for r in results if r["size"] == 9 and r["depth"] == 128]))
    gate = all(abs(nine[d]-nine[128]) <= .002 for d in (512, 1024))
    return dict(nine_accuracy=nine, nine_macro_at128=macro, useful_accuracy=bool(macro >= .95),
                stability_gate=bool(gate),
                stability_gate_definition="9x9 absolute accuracy change <=0.2pp from128 to512 and1024")


def make_predict(model, mc, feedforward=False):
    @partial(jax.jit, static_argnames=("depths",))
    def predict(params, tokens, key, depths, id_key=None):
        initial = initialize(tokens, key if id_key is None else id_key, mc)
        if feedforward:
            logits = model.apply({"params": params}, perception_inputs(initial, mc)[..., :mc.input_channels])
            pred = jnp.argmax(logits, -1)
            finite = jnp.all(jnp.isfinite(logits), axis=-1)
            pred = jnp.where(finite, pred, -2)
            return jnp.broadcast_to(pred, (len(depths),)+pred.shape), jnp.zeros((1, 2))
        outputs = jnp.full((len(depths),)+tokens.shape, -2, jnp.int32)
        old_pred = readout(model, params, initial)[0]
        def body(carry, i):
            state, previous, saved = carry
            final, _ = step(model, params, state, tokens, jax.random.fold_in(key, i))
            pred = readout(model, params, final)[0]
            for slot, depth in enumerate(depths):
                saved = saved.at[slot].set(jnp.where(i == depth-1, pred, saved[slot]))
            active = tokens != 3
            change = jnp.sum(jnp.where(active[..., None], (final[..., mc.input_channels:]-state[..., mc.input_channels:])**2, 0))
            change = jnp.sqrt(change/jnp.maximum(active.sum()*(mc.channels-mc.input_channels), 1))
            stones = (tokens == 1) | (tokens == 2) | (tokens >= 4)
            flips = jnp.sum((pred != previous) & stones)/jnp.maximum(stones.sum(), 1)
            return (final, pred, saved), jnp.stack((change, flips))
        (_, _, outputs), dynamics = jax.lax.scan(body, (initial, old_pred, outputs), jnp.arange(max(depths)))
        return outputs, dynamics
    return predict


def evaluate(predict, params, data, depths, key, batch=64, id_key=None):
    boards, labels = data
    predictions, dynamics = [], []
    for start in range(0, len(boards), batch):
        pred, trajectory = predict(params, jnp.asarray(boards[start:start+batch]),
                                   jax.random.fold_in(key, start), depths,
                                   None if id_key is None else jax.random.fold_in(id_key, start))
        predictions.append(np.asarray(pred))
        dynamics.append(np.asarray(trajectory))
    return np.concatenate(predictions, axis=1), np.mean(dynamics, axis=0)


def recurrent_objective(model, mc, config, weights, incoming, tokens, targets, iteration_key, horizon):
    """Full forward horizon with a separately detached, cheaper prefix scan."""
    max_depth, late = config["max_depth"], config["late_steps"]
    window = min(config["gradient_window"], max_depth)
    if not 0 < late <= window:
        raise ValueError("Late supervision must fit inside the gradient window")
    prefix_length = jnp.maximum(horizon-window, 0)
    if window < max_depth:
        frozen_weights = jax.lax.stop_gradient(weights)
        def prefix(state, index):
            out, _ = step(model, frozen_weights, state, tokens, jax.random.fold_in(iteration_key, index),
                          noise_sigma=config["noise_sigma"])
            return jnp.where(index < prefix_length, out, state), None
        start, _ = jax.lax.scan(prefix, incoming, jnp.arange(max_depth-window))
        start = jax.lax.stop_gradient(start)
    else:
        start = incoming
    def body(carry, local_index):
        index = prefix_length+local_index
        state, total, state_total, final = carry
        key = jax.random.fold_in(iteration_key, index)
        out, _ = step(model, weights, state, tokens, key, noise_sigma=config["noise_sigma"])
        deterministic, _ = step(model, weights, state, tokens, key)
        mask = (tokens != 3)[..., None]
        state_change = jnp.sum(jnp.where(mask, (deterministic[..., mc.input_channels:]-state[..., mc.input_channels:])**2, 0))
        state_change /= jnp.maximum(mask.sum()*(mc.channels-mc.input_channels), 1)
        eligible = (index >= horizon-late) & (index < horizon)
        ce = balanced_loss(model.apply({"params": weights}, out, method=model.logits), targets, mc.classes)
        total += jnp.where(eligible, ce, 0.)
        state_total += jnp.where(eligible, state_change, 0.)
        final = jnp.where(index == horizon-1, out, final)
        out = jnp.where(index < horizon-1, out, incoming)
        return (out, total, state_total, final), None
    (_, ce, drift, final), _ = jax.lax.scan(jax.checkpoint(body),
                         (start, jnp.array(0.), jnp.array(0.), incoming), jnp.arange(window))
    return (ce+config["change_weight"]*drift)/late, (final, ce/late, drift/late)


def train(config, seed, warmstart=None, require_gpu=False):
    if require_gpu and not any(d.platform == "gpu" for d in jax.devices()):
        raise RuntimeError("GPU required")
    if warmstart:
        config = {**config, "warmstart_sha256": sha256(Path(warmstart).read_bytes()).hexdigest(),
                  "initialization": "pretrained exploratory warmstart; excluded from matched from-scratch comparison"}
    run = Run("research_training", {**config, "seed": seed,
                                   "selection": "final EMA; validation only; no final-test selection"}, seed)
    val = validation_data(config)
    exclusions = [canonical_key(b) for boards, _ in val.values() for b in boards]
    stream = OnlineStream(config["data_seed"], cap=config["cap"], exclude=exclusions, task=config["task"])
    if config.get('race_stream_cache'):
        from ncago.go.cached_race_stream import CachedRaceStream
        stream = CachedRaceStream(config['race_stream_cache'], config)
    rng = np.random.default_rng(config["data_seed"]+100)
    model, mc = build_model(config)
    seed_state = jax.jit(lambda t, k: initialize(t, k, mc))
    encode_inputs = jax.jit(lambda t, k: frozen_inputs(t, k, mc))
    feedforward = config["model"] == "resnet"
    key = jax.random.PRNGKey(seed)
    batch = config["batch_size"]
    pool_tokens, pool_targets = stream.draw(4*batch)
    pool_states = np.asarray(seed_state(jnp.asarray(pool_tokens), key)).copy()
    params = (model.init(key, jnp.asarray(pool_states[:batch, ..., :mc.input_channels]))["params"]
              if feedforward else init_params(model, jnp.asarray(pool_states[:batch]), key))
    if warmstart:
        if mc.identifier_channels or feedforward or config["model"] != "nca":
            raise ValueError("Warmstart is only compatible with the original identifier-free NCA")
        params = serialization.from_bytes(params, Path(warmstart).read_bytes())
    schedule = optax.cosine_decay_schedule(config["learning_rate"], config.get("schedule_steps") or config["training_steps"], alpha=.02)
    optimizer = optax.chain(optax.clip_by_global_norm(1.), optax.adam(schedule))
    opt_state = optimizer.init(params)
    average = params
    max_depth, late = config["max_depth"], config["late_steps"]

    @jax.jit
    def update(params, opt_state, average, incoming, tokens, targets, iteration_key):
        horizon = jax.random.randint(jax.random.fold_in(iteration_key, 9999), (), config["min_depth"], max_depth+1)
        def objective(weights):
            if feedforward:
                logits = model.apply({"params": weights}, perception_inputs(incoming, mc)[..., :mc.input_channels])
                return balanced_loss(logits, targets, mc.classes), (incoming, jnp.array(0.), jnp.array(0.))
            return recurrent_objective(model, mc, config, weights, incoming, tokens, targets, iteration_key, horizon)
        (loss, (final, ce, drift)), gradients = jax.value_and_grad(objective, has_aux=True)(params)
        updates, opt_state = optimizer.update(gradients, opt_state, params)
        params = optax.apply_updates(params, updates)
        average = jax.tree_util.tree_map(lambda a, p: config["ema_decay"]*a+(1-config["ema_decay"])*p, average, params)
        return params, opt_state, average, final, loss, ce, drift, optax.global_norm(gradients), horizon

    predict = make_predict(model, mc, feedforward)
    write_json(run.path / "model.json", {"model_config": asdict(mc), "kind": config["model"],
                                         "parameters": parameter_count(params),
                                         "resnet_radius": model.receptive_field_radius if feedforward else None})
    print(f"RUN {run.path.name} {config['model']} seed={seed}, params={parameter_count(params)}", flush=True)
    start = time.perf_counter()
    producer = OnlinePrefetch(stream, batch, config["training_steps"]) if config["online_prefetch"] else None
    supervised_stream = sha256()
    for iteration in range(config["training_steps"]):
        slots = rng.choice(len(pool_tokens), batch, replace=False)
        fresh = rng.random(batch) < config["seed_fraction"]
        if iteration < config["warmup_steps"]:
            fresh[:] = True
        # Generate all B candidates every iteration, even when replay uses
        # fewer. This keeps the exact candidate stream identical for baselines.
        candidates, candidate_targets = producer.draw() if producer else stream.draw(batch)
        consumed = producer.stats if producer else dict(online_boards=stream.draws, stream_sha256=stream.digest.hexdigest())
        tokens, targets = pool_tokens[slots].copy(), pool_targets[slots].copy()
        tokens[fresh], targets[fresh] = candidates[fresh], candidate_targets[fresh]
        incoming = pool_states[slots].copy()
        iteration_key = jax.random.fold_in(key, iteration+1)
        seeded = np.asarray(seed_state(jnp.asarray(tokens), iteration_key))
        incoming[fresh] = seeded[fresh]
        incoming, tokens, targets = augment(incoming, tokens, targets, config["task"], rng, mc)
        # Paper target swapping and damage; frozen inputs are never damaged.
        incoming, tokens, targets = perturb(incoming, tokens, targets, candidates, candidate_targets,
                                            mc, config, rng)
        incoming = refresh_frozen_inputs(incoming, tokens, iteration_key, mc, fresh,
                                         config.get("identifier_replay_policy", "chunk"), encode_inputs)
        supervised_stream.update(tokens.tobytes()); supervised_stream.update(targets.tobytes())
        params, opt_state, average, final, loss, ce, drift, norm, horizon = update(
            params, opt_state, average, jnp.asarray(incoming), jnp.asarray(tokens), jnp.asarray(targets), iteration_key)
        values = np.asarray([loss, ce, drift, norm])
        if not np.all(np.isfinite(values)):
            if producer:
                producer.close()
            run.finish("failed_nonfinite", iteration=iteration+1, **consumed)
            raise FloatingPointError(values)
        pool_tokens[slots], pool_targets[slots], pool_states[slots] = tokens, targets, np.asarray(final)
        if iteration == 0 or (iteration+1) % config["log_every"] == 0 or iteration+1 == config["training_steps"]:
            pred, dynamics = evaluate(predict, average, (val[9][0][:128], val[9][1][:128]),
                                      (32, 128, 512, 1024), jax.random.PRNGKey(92001))
            measured = [metrics(p, val[9][1][:128], mc.classes, config["task"]) for p in pred]
            run.log(event="validation", iteration=iteration+1, horizon=int(horizon), loss=float(loss),
                    cross_entropy=float(ce), late_state_change=float(drift), gradient_norm=float(norm),
                    depths=[32, 128, 512, 1024], metrics=measured,
                    **consumed,
                    elapsed_seconds=time.perf_counter()-start)
            print(f"{config['model']} s{seed} {iteration+1}: loss={float(loss):.4f}, "
                  f"9x9 [32,128,512,1024]={[round(100*m['stone_accuracy'], 3) for m in measured]}", flush=True)
        if (iteration+1) % config["checkpoint_every"] == 0 or iteration+1 == config["training_steps"]:
            checkpoint = serialization.to_bytes(average)
            (run.path / "ckpt" / f"step_{iteration+1:06d}.msgpack").write_bytes(checkpoint)
            temp = run.path / "ckpt" / "latest.tmp"
            temp.write_bytes(checkpoint); temp.replace(run.path / "ckpt" / "latest.msgpack")
            write_json(run.path / "progress.json", dict(iteration=iteration+1, model_config=asdict(mc), **consumed))
    if producer:
        producer.close()
    (run.path / "ckpt" / "final.msgpack").write_bytes(serialization.to_bytes(average))
    canonical_hashes = np.frombuffer(b"".join(sorted(stream.seen_canonical_hashes)), np.uint8).reshape(-1, 32)
    np.savez_compressed(run.path / "data" / "training_canonical_hashes.npz", hashes=canonical_hashes)
    results = []
    for size, data in val.items():
        depths = (32, 64, 128, 512, 1024)
        draws = 8 if mc.identifier_channels else 3
        for draw in range(draws):
            pred, dynamics = evaluate(predict, average, data, depths,
                                      jax.random.PRNGKey(93001 if mc.identifier_channels else 93001+draw), batch=64,
                                      id_key=jax.random.PRNGKey(94001+draw) if mc.identifier_channels else None)
            np.savez_compressed(run.path / "eval" / f"validation_{size}_draw{draw}.npz", predictions=pred, dynamics=dynamics)
            for depth, p in zip(depths, pred):
                results.append(dict(size=size, depth=depth, draw=draw, **metrics(p, data[1], mc.classes, config["task"])))
    # Report the user's relative stability gate exactly. Separately flag
    # usefulness so a collapsed constant predictor cannot justify scaling.
    return run.finish("complete", model_config=asdict(mc), model=config["model"],
                      class_names=class_names(config["task"], config["cap"]),
                      parameters=parameter_count(params), results=results,
                      **stability_assessment(results), online_boards=stream.draws,
                      stream_sha256=stream.digest.hexdigest(), rejected_validation_duplicates=stream.rejected,
                      supervised_stream_sha256=supervised_stream.hexdigest(),
                      unique_online_canonical_positions=len(stream.seen_canonical_hashes),
                      candidate_source_counts=stream.source_draw_counts,
                      training_seconds=time.perf_counter()-start)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--model", choices=("nca", "resnet", "rcnn", "gnn_sum", "gnn_max"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int)
    parser.add_argument("--ids", type=int, choices=(0, 16, 32))
    parser.add_argument("--change-weight", type=float)
    parser.add_argument("--warmstart")
    parser.add_argument("--race-stream-cache", type=Path)
    parser.add_argument("--require-gpu", action="store_true")
    args = parser.parse_args()
    config = DEFAULT.copy()
    if args.config:
        config.update(json.loads(Path(args.config).read_text()))
    for key, value in (("model", args.model), ("training_steps", args.steps),
                       ("identifier_channels", args.ids), ("change_weight", args.change_weight)):
        if value is not None:
            config[key] = value
    if args.race_stream_cache:
        config['race_stream_cache'] = str(args.race_stream_cache)
        config['race_stream_cache_manifest_sha256'] = sha256((args.race_stream_cache/'manifest.json').read_bytes()).hexdigest()
        config['oracle_stream_delivery'] = 'materialized exact prescribed online sequence'
    train(config, args.seed, args.warmstart, args.require_gpu)


if __name__ == "__main__":
    main()
