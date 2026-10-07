"""Paired distant-liberty queries, opened on 13x13 validation during tuning."""
import argparse
from dataclasses import asdict
from functools import partial
import hashlib
import json
from pathlib import Path

from flax import serialization
import jax
import jax.numpy as jnp
import numpy as np
import yaml

from ncago.go.generators import canonical_key
from ncago.go.labels import liberties
from ncago.nca.model import ModelConfig, NCA, initialize, init_params, step, readout
from .common import ROOT, Run, write_json
from .learnability import locality_witness


def paired_queries(size, pairs, seed):
    rng = np.random.default_rng(seed)
    base_one, base_two, query, distance = locality_witness(size)
    rr, _ = np.ogrid[:size, :size]
    outside = np.abs(rr-query[0]) > 1
    boards, queries, labels, seen = [], [], [], set()
    for _ in range(pairs*100):
        clutter = outside & (rng.random((size, size)) < rng.uniform(.1, .7))
        pair = np.stack([np.where(clutter, 2, b) for b in (base_one, base_two)])
        q = query
        rotation = int(rng.integers(4))
        pair = np.rot90(pair, rotation, axes=(1, 2)).copy()
        for _ in range(rotation):
            q = size-1-q[1], q[0]
        if rng.random() < .5:
            pair = pair[:, ::-1].copy()
            q = size-1-q[0], q[1]
        if rng.random() < .5:
            pair = np.where(pair == 1, 2, np.where(pair == 2, 1, pair)).astype(np.int8)
        key = canonical_key(pair[0])
        if key in seen:
            continue
        seen.add(key)
        changed = np.argwhere(pair[0] != pair[1])
        if len(changed) != 1 or int(np.max(np.abs(changed[0]-q))) != distance:
            raise AssertionError("Pair does not satisfy its locality certificate")
        exact = [int(liberties(b)[0][q]) for b in pair]
        if exact != [0, 1]:
            raise AssertionError("Pair's query must have one versus two liberties")
        boards.extend(pair)
        queries.extend([q, q])
        labels.extend(exact)
        if len(boards) == 2*pairs:
            return np.stack(boards), np.array(queries), np.array(labels), distance
    raise RuntimeError("Failed to produce distinct paired queries")


def load_checkpoint(path, variant):
    config = yaml.safe_load((path / "config.yaml").read_text())
    summary = json.loads((path / "summary.json").read_text())
    record = next(r for r in summary["records"] if r["variant"] == variant)
    mc = ModelConfig(**record["model_config"])
    model = NCA(mc)
    template = init_params(model, initialize(jnp.zeros((1, 9, 9), jnp.int32),
                                           jax.random.PRNGKey(0), mc), jax.random.PRNGKey(0))
    checkpoint = path / "ckpt" / f"{variant}.msgpack"
    data = checkpoint.read_bytes()
    return model, serialization.from_bytes(template, data), hashlib.sha256(data).hexdigest(), config


@partial(jax.jit, static_argnames=("model", "depth"))
def predict(model, params, tokens, key, depth):
    # Common random numbers couple both members of each adjacent pair. Thus
    # stochastic firing/initial noise cannot masquerade as a distant signal.
    keys = jax.vmap(lambda i: jax.random.fold_in(key, i//2))(jnp.arange(len(tokens)))
    def one(board, trial_key):
        board = board[None]
        state = initialize(board, trial_key, model.config)
        def body(s, i):
            return step(model, params, s, board, jax.random.fold_in(trial_key, i))[0], None
        final, _ = jax.lax.scan(body, state, jnp.arange(depth))
        return readout(model, params, final)[0][0]
    return jax.vmap(one)(tokens, keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, nargs="+", required=True)
    parser.add_argument("--sizes", type=int, nargs="+", default=[13])
    parser.add_argument("--depths", type=int, nargs="+", default=[8, 16, 32, 64, 128, 256])
    parser.add_argument("--pairs", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--final-manifest", type=Path)
    args = parser.parse_args()
    if args.batch_size < 2 or args.batch_size % 2 or args.pairs < 1 or min(args.depths) < 1:
        parser.error("Positive depths/pair count and an even batch size are required")
    manifest = json.loads(args.final_manifest.read_text()) if args.final_manifest else None
    if max(args.sizes) > 13 and not manifest:
        parser.error("Freeze checkpoint hashes in a final manifest before opening larger test queries")
    config = {"source_runs": [str(p) for p in args.runs], "sizes": args.sizes,
              "depths": args.depths, "pairs": args.pairs, "batch_size": args.batch_size,
              "data_seed": 74002 if manifest else 74001,
              "scope": "sealed paired-query family" if manifest else "13x13 validation query family",
              "final_manifest": manifest,
              "CNN_radius": 9, "CNN_pair_accuracy_upper_bound": .5}
    run = Run("propagation_probe", config)
    datasets = {}
    for size in args.sizes:
        data = paired_queries(size, args.pairs, config["data_seed"]+size)
        datasets[size] = data
        boards, queries, labels, distance = data
        np.savez_compressed(run.path / "data" / f"queries_{size}.npz", boards=boards,
                            queries=queries, labels=labels, causal_distance=distance)
    records = []
    for source in args.runs:
        source_config = yaml.safe_load((source / "config.yaml").read_text())
        for variant in source_config["variants"]:
            model, params, digest, _ = load_checkpoint(source, variant)
            if manifest and digest not in manifest["checkpoint_sha256"]:
                raise ValueError("Checkpoint was not frozen in the final manifest")
            for size, (boards, queries, labels, distance) in datasets.items():
                for depth in args.depths:
                    for trial in range(3 if model.config.fire_rate < 1 else 1):
                        key = jax.random.PRNGKey(300000+trial)
                        predictions = []
                        for start in range(0, len(boards), args.batch_size):
                            tokens = jnp.asarray(boards[start:start+args.batch_size])
                            out = np.asarray(predict(model, params, tokens, jax.random.fold_in(key, start), depth))
                            q = queries[start:start+len(out)]
                            predictions.extend(out[np.arange(len(out)), q[:, 0], q[:, 1]])
                        predictions = np.array(predictions)
                        if np.any(predictions < 0):
                            raise FloatingPointError("Nonfinite checkpoint rollout")
                        correct = predictions == labels
                        record = {"source_run": source.name, "training_seed": source_config.get("seed", json.loads((source / "metadata.json").read_text())["seed"]),
                                  "variant": variant, "model_config": asdict(model.config),
                                  "checkpoint_sha256": digest, "size": size, "depth": depth,
                                  "trial": trial, "causal_distance": distance,
                                  "query_accuracy": float(correct.mean()),
                                  "pair_exact": float(correct.reshape(-1, 2).all(1).mean()),
                                  "prediction_counts": np.bincount(predictions, minlength=4).tolist()}
                        records.append(record)
                        run.log(event="paired_query", **record)
                        filename = f"{source.name}_{variant}_n{size}_d{depth}_t{trial}.npz"
                        np.savez_compressed(run.path / "eval" / filename, predictions=predictions)
                        print(f"{source.name} N={size} D={depth} trial={trial}: "
                              f"queries={record['query_accuracy']:.3f}, pairs={record['pair_exact']:.3f}", flush=True)
    write_json(run.path / "eval" / "scores.json", records)
    run.finish("measured", records=records, accuracy_gate_certified=False,
               limitation="One/two-liberty paired queries; this does not establish full liberty counting")
    print(f"Saved query probe: {run.path}", flush=True)


if __name__ == "__main__":
    main()
