"""Free exact-reference and finite-ID collision analysis on already opened data."""
import json
import numpy as np
from ncago.go.research_data import identifier_reference_fast, count_labels, witness_set
from .checkpoint_audit import chain_features
from .common import ROOT, write_json


def main():
    out = ROOT / "reports/checkpoint_audit"
    report = json.loads((ROOT / "reports/GPU_RESULTS.json").read_text())
    source = ROOT / "results/final_liberties" / report["final_evaluations"][0]["run"] / "data"
    records = []
    rng = np.random.default_rng(97001)
    for size in (9, 13, 19, 25, 37):
        for generator in ("random", "structured"):
            with np.load(source / f"test_{generator}_{size}.npz") as data:
                boards, labels = data["boards"][:16], data["labels"][:16]
            features = [chain_features(b) for b in boards]
            for bits in (16, 32):
                for draw in range(8):
                    correct, total, collisions, max_rounds = 0, 0, 0, 0
                    for board, y, f in zip(boards, labels, features):
                        ids = rng.integers(0, 2**bits, size=board.shape, dtype=np.int64)
                        empty_ids = ids[board == 0]
                        collisions += len(empty_ids)-len(np.unique(empty_ids))
                        depth = max(1, int(f[..., 1].max())+1)
                        p, rounds = identifier_reference_fast(board, ids, depth)
                        mask = y >= 0
                        correct += int(((p == y) & mask).sum())
                        total += int(mask.sum())
                        max_rounds = max(max_rounds, rounds)
                    records.append(dict(size=size, generator=generator, bits=bits, draw=draw,
                                        stone_accuracy=correct/total, correct_stones=correct,
                                        total_stones=total, empty_cell_ID_collisions=collisions,
                                        maximum_rounds_to_fixed_point=max_rounds,
                                        scope="first16 boards from existing opened test; exact reference, not learned model"))
            print(f"Identifier reference {generator} {size}", flush=True)
    witness = []
    for size in (9, 13, 19, 25, 37):
        data = witness_set(size, per_geometry=8, seed=98001+size)
        np.savez_compressed(out / f"reference_witness_{size}.npz", **data)
        for bits in (16, 32):
            for draw in range(8):
                results = []
                for i in range(0, len(data["boards"]), 2):
                    ids = rng.integers(0, 2**bits, size=(size, size), dtype=np.int64)
                    pair_correct = []
                    for j in (i, i+1):
                        board, query = data["boards"][j], tuple(data["queries"][j])
                        p, rounds = identifier_reference_fast(board, ids, size*size)
                        pair_correct.append(bool(p[query] == data["labels"][j]))
                    results.append(all(pair_correct))
                witness.append(dict(size=size, bits=bits, draw=draw, pairs=len(results),
                                    pair_both_correct=float(np.mean(results)),
                                    geometries=sorted(set(data["geometries"].tolist())),
                                    coupled_IDs=True, scope="exact reference, not learned replication"))
        print(f"Identifier reference five-geometry witness {size}", flush=True)
    write_json(out / "identifier_reference.json", {"final_existing_subsets": records, "witness": witness,
                                                  "iid_ID_collision_probability": "nonzero; no uniqueness enforcement",
                                                  "warning": "Hand-coded counting results do not establish neural learnability"})


if __name__ == "__main__":
    main()
