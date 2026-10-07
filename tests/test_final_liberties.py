import pytest
from ncago.experiments.final_liberties import certify_g1, validate_manifest


def test_gate_uses_frozen_primary_depth_and_requires_every_seed():
    records = [dict(training_seed=seed, size=9, primary=True, stone_correct=996, stone_count=1000)
               for seed in (0, 1, 2)]
    scores, passed = certify_g1(records)
    assert passed and scores == {"0": .996, "1": .996, "2": .996}
    records.append(dict(training_seed=1, size=9, primary=False, stone_correct=0, stone_count=100000))
    assert certify_g1(records)[1]
    records[2]["stone_correct"] = 994
    assert not certify_g1(records)[1]
    assert not certify_g1([])[1]


def test_gate_pools_stones_instead_of_averaging_boards():
    records = [dict(training_seed=0, size=9, primary=True, stone_correct=0, stone_count=1),
               dict(training_seed=0, size=9, primary=True, stone_correct=999, stone_count=999)]
    assert certify_g1(records) == ({"0": .999}, True)


def test_final_manifest_cannot_pool_recipes_with_the_same_seed():
    manifest = dict(checkpoints=[dict(seed=0, variant="ce_late"), dict(seed=1, variant="ce_late")],
                    primary_depth=32, evaluation_depths=[32, 64], test_counts={"9": 10})
    validate_manifest(manifest)
    manifest["checkpoints"][1]["seed"] = 0
    with pytest.raises(ValueError, match="unique training seeds"):
        validate_manifest(manifest)
    manifest["checkpoints"][1].update(seed=1, variant="ce_late_async")
    with pytest.raises(ValueError, match="different recipes"):
        validate_manifest(manifest)
