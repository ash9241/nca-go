"""Audit the hand-coded top16 ID-set reference on existing validation only."""
from hashlib import sha256
import json
import numpy as np
from .common import ROOT, write_json
from .checkpoint_audit import chain_features
from ncago.go.research_data import identifier_reference_fast


def main():
    config = json.loads((ROOT / 'configs/research_liberties16.json').read_text())
    root = ROOT / 'results/research_validation' / f"cap16_n{config['validation_count']}_s{config['validation_seed']}"
    rng = np.random.default_rng(115001)
    records = []
    for size in (9, 13):
        path = root / f'val_{size}.npz'
        with np.load(path) as data:
            boards, labels = data['boards'], data['labels']
        support = np.bincount(labels[labels >= 0], minlength=16)
        correct = total = collisions = 0
        maximum_rounds = 0
        for board, target in zip(boards, labels):
            diameter = max(1, int(chain_features(board)[..., 1].max()))
            for _ in range(8):
                ids = rng.integers(0, 2**32, size=board.shape, dtype=np.int64)
                empty_ids = ids[board == 0]
                collisions += len(empty_ids)-len(np.unique(empty_ids))
                prediction, rounds = identifier_reference_fast(board, ids, diameter, cap=16)
                mask = target >= 0
                correct += int((prediction[mask] == target[mask]).sum()); total += int(mask.sum())
                maximum_rounds = max(maximum_rounds, rounds)
        records.append(dict(size=size, boards=len(boards), identifier_bits=32, draws=8,
                            correct_stone_draws=correct, stone_draws=total, accuracy=correct/total,
                            empty_ID_collisions=collisions, class_stone_support_per_draw=support.tolist(),
                            maximum_executed_message_rounds=maximum_rounds, validation_sha256=sha256(path.read_bytes()).hexdigest()))
        print(records[-1], flush=True)
    write_json(ROOT / 'reports/checkpoint_audit/richer_reference_validation.json', dict(
        scope='Hand-coded reference; not a learned model; entire existing frozen9/13 validation splits',
        cap=16, seed=115001, loading_phase=1, propagation='At most each board maximum chain diameter message rounds after local-ID loading',
        collision_policy='IID finite identifiers; collisions are not repaired', records=records))


if __name__ == '__main__':
    main()
