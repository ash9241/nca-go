"""Evaluate frozen liberty checkpoints once on independent final splits."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from ncago.go.generators import generate, canonical_key
from ncago.go.labels import liberties
from ncago.experiments.propagation_probe import load_checkpoint, predict
from ncago.experiments.learnability import scores
from .common import Run, write_json


def independent_split(size, count, seed, generator, exclude):
    boards, sources = generate("liberties", size, count, seed, generator, exclude, controlled=True)
    labels = np.stack([liberties(board)[0] for board in boards])
    return boards, labels, sources


def certify_g1(records):
    grouped = defaultdict(list)
    for row in records:
        if row["primary"] and row["size"] == 9:
            grouped[row["training_seed"]].append(row)
    per_seed = {str(seed): sum(r["stone_correct"] for r in values)/sum(r["stone_count"] for r in values)
                for seed, values in grouped.items()}
    return per_seed, bool(per_seed) and all(value >= .995 for value in per_seed.values())


def validate_manifest(manifest):
    items = manifest["checkpoints"]
    if not items or len({item["seed"] for item in items}) != len(items):
        raise ValueError("A final run requires unique training seeds from one recipe")
    if len({item["variant"] for item in items}) != 1:
        raise ValueError("Evaluate different recipes in separate final runs")
    depths = manifest["evaluation_depths"]
    if manifest["primary_depth"] not in depths or min(depths) < 1:
        raise ValueError("The frozen primary depth must be a positive evaluated depth")
    if "9" not in manifest["test_counts"] or min(manifest["test_counts"].values()) < 1:
        raise ValueError("Positive final test counts including 9x9 are required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--known-roots", type=Path, nargs="+", required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest)
    if args.batch_size % 2:
        parser.error("Use an even inference batch size")
    config = {"manifest": manifest, "batch_size": args.batch_size,
              "final_seed_namespace": "ncago/A100/final/liberties/v1",
              "known_roots": [str(p) for p in args.known_roots],
              "G1_definition": "all-stone 9x9 accuracy >= 0.995 at the frozen primary depth"}
    run = Run("final_liberties", config)
    exclude = defaultdict(set)
    seen_raw = set()
    # Exclude every training/validation board opened during selection.
    for root in args.known_roots:
        for path in (root / "results").glob("*/**/data/*.npz"):
            if path.name.startswith("test_") or "final_liberties" in str(path):
                continue
            with np.load(path) as data:
                if "boards" not in data:
                    continue
                for board in data["boards"]:
                    raw = len(board), board.tobytes()
                    if raw in seen_raw:
                        continue
                    seen_raw.add(raw)
                    exclude[len(board)].add(canonical_key(board))
    records = []
    checkpoints = []
    for item in manifest["checkpoints"]:
        source, variant = Path(item["run_path"]), item["variant"]
        model, params, digest, _ = load_checkpoint(source, variant)
        if digest != item["sha256"]:
            raise ValueError("Frozen checkpoint hash changed")
        metadata = json.loads((source / "metadata.json").read_text())
        if metadata["seed"] != item["seed"]:
            raise ValueError("Frozen seed does not match the recorded training seed")
        if checkpoints and model.config != checkpoints[0][1].config:
            raise ValueError("Evaluate different model recipes in separate final runs")
        checkpoints.append((item, model, params))
    for size_string, count in manifest["test_counts"].items():
        size = int(size_string)
        for generator in ("random", "structured"):
            namespace = f"{config['final_seed_namespace']}/{generator}/{size}"
            seed = int(hashlib.sha256(namespace.encode()).hexdigest()[:8], 16)
            boards, labels, sources = independent_split(size, count, seed, generator, exclude[size])
            exclude[size].update(canonical_key(b) for b in boards)
            np.savez_compressed(run.path / "data" / f"test_{generator}_{size}.npz", boards=boards, labels=labels)
            write_json(run.path / "data" / f"test_{generator}_{size}_sources.json", sources)
            for item, model, params in checkpoints:
                for depth in manifest["evaluation_depths"]:
                    for trial in range(3 if model.config.fire_rate < 1 else 1):
                        outputs = []
                        key = jax.random.PRNGKey(400000+trial)
                        for start in range(0, len(boards), args.batch_size):
                            # Coupling neighboring boards' randomness is harmless
                            # here; final labels are evaluated independently.
                            outputs.append(np.asarray(predict(model, params, jnp.asarray(boards[start:start+args.batch_size]),
                                                              jax.random.fold_in(key, start), depth)))
                        predictions = np.concatenate(outputs)
                        row = {"source_run": Path(item["run_path"]).name,
                               "training_seed": item["seed"], "size": size, "generator": generator,
                               "depth": depth, "trial": trial, "primary": depth == manifest["primary_depth"],
                               "stone_count": int(np.sum(labels >= 0)),
                               "stone_correct": int(np.sum((labels >= 0) & (predictions == labels))),
                               **scores(predictions, labels, "board_exact")}
                        records.append(row)
                        run.log(event="final_liberties", **row)
                        print(f"seed={item['seed']} {generator} N={size} D={depth}: "
                              f"stone={row['stone_accuracy']:.5f}, macro={row['macro_stone_accuracy']:.5f}, "
                              f"board={row['board_exact']:.5f}", flush=True)
                        filename = f"{item['seed']}_{generator}_{size}_d{depth}_t{trial}.npz"
                        np.savez_compressed(run.path / "eval" / filename, predictions=predictions)
    per_seed, passed = certify_g1(records)
    write_json(run.path / "eval" / "scores.json", records)
    run.finish("passed" if passed else "gate_failed", G1_per_seed=per_seed,
               accuracy_gate_certified=passed, records=records,
               limitation="This certifies only liberty counting on the recorded test distributions; life, ladders and playing strength are separate")
    print(f"Saved final evaluation: {run.path}", flush=True)


if __name__ == "__main__":
    main()
