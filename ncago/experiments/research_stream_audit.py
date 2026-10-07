"""Reconstruct a deterministic online stream and verify its recorded digest.

Useful for the first pilot processes launched before canonical hashes were
persisted. No model is trained or tested, and digest mismatch is an error.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
import yaml
from ncago.go.research_data import OnlineStream
from ncago.go.generators import canonical_key
from .common import write_json
from .research_train import validation_data
from ncago.nca.train import augment, perturb
from types import SimpleNamespace


def reconstruct_supervised_stream(config, exclusions):
    """Reproduce actual augmented label batches independently of model state.

    Replay slot selection, board replacements, symmetries and target swaps
    depend only on the data RNG. Learned mutable states cannot affect them.
    """
    stream = OnlineStream(config["data_seed"], cap=config["cap"], exclude=exclusions, task=config["task"])
    rng = np.random.default_rng(config["data_seed"]+100)
    batch = config["batch_size"]
    pool_tokens, pool_targets = stream.draw(4*batch)
    digest = sha256()
    c = SimpleNamespace(input_channels=8, identifier_channels=0)
    for iteration in range(config["training_steps"]):
        slots = rng.choice(len(pool_tokens), batch, replace=False)
        fresh = rng.random(batch) < config["seed_fraction"]
        if iteration < config["warmup_steps"]:
            fresh[:] = True
        candidates, candidate_targets = stream.draw(batch)
        tokens, targets = pool_tokens[slots].copy(), pool_targets[slots].copy()
        tokens[fresh], targets[fresh] = candidates[fresh], candidate_targets[fresh]
        dummy = np.zeros(tokens.shape+(8,), np.float32)
        dummy, tokens, targets = augment(dummy, tokens, targets, config["task"], rng, c)
        _, tokens, targets = perturb(dummy, tokens, targets, candidates, candidate_targets, c, config, rng)
        digest.update(tokens.tobytes()); digest.update(targets.tobytes())
        pool_tokens[slots], pool_targets[slots] = tokens, targets
        if (iteration+1) % 5000 == 0:
            print(f"Reconstructed supervised batches {iteration+1}", flush=True)
    return stream, digest.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--supervised", action="store_true")
    args = p.parse_args()
    config = yaml.safe_load((args.run / "config.yaml").read_text())
    config.setdefault("task", "liberties")
    summary = json.loads((args.run / "summary.json").read_text())
    validation = validation_data(config)
    exclusions = [canonical_key(b) for boards, _ in validation.values() for b in boards]
    supervised = None
    if args.supervised:
        stream, supervised = reconstruct_supervised_stream(config, exclusions)
        if summary.get("supervised_stream_sha256") and supervised != summary["supervised_stream_sha256"]:
            raise AssertionError("Actual supervised batches differ from deterministic reconstruction")
    else:
        stream = OnlineStream(config["data_seed"], cap=config["cap"], exclude=exclusions, task=config["task"])
        remaining = summary["online_boards"]
        while remaining:
            count = min(4096, remaining)
            stream.draw(count)
            remaining -= count
            if remaining % (4096*50) < 4096:
                print(f"Reconstructed {stream.draws} of {summary['online_boards']}", flush=True)
    if stream.digest.hexdigest() != summary["stream_sha256"]:
        raise AssertionError("Reconstructed stream differs from actual training")
    hashes = np.frombuffer(b"".join(sorted(stream.seen_canonical_hashes)), np.uint8).reshape(-1, 32)
    np.savez_compressed(args.run / "data/training_canonical_hashes.npz", hashes=hashes)
    write_json(args.run / "data/stream_reconstruction.json",
               dict(reconstructed=True, recorded_stream_sha256=summary["stream_sha256"],
                    exact_digest_match=True, boards=stream.draws, unique_canonical=len(hashes)))
    if supervised:
        write_json(args.run / "data/supervised_stream_reconstruction.json",
                   dict(reconstructed=True, supervised_stream_sha256=supervised,
                        definition="ordered augmented training tokens and labels after replay, target swaps and symmetry; no model states",
                        candidate_stream_verified=True, training_steps=config["training_steps"]))


if __name__ == "__main__":
    main()
