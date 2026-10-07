import json
import numpy as np
import yaml
from ncago.experiments import rescue_report


def test_final_report_weights_stones_and_keeps_seed_uncertainty(tmp_path, monkeypatch):
    monkeypatch.setattr(rescue_report, "ROOT", tmp_path)
    source = tmp_path / "results" / "learnability" / "source"
    source.mkdir(parents=True)
    (source / "config.yaml").write_text(yaml.safe_dump({"hint_weight": 0}))
    final = tmp_path / "results" / "final_liberties" / "final"
    (final / "data").mkdir(parents=True)
    (final / "eval").mkdir()
    manifest = {"checkpoints": [{"run_path": str(source), "variant": "ce_late", "seed": s} for s in (0, 1)], "primary_depth": 32}
    (final / "config.yaml").write_text(yaml.safe_dump({"manifest": manifest}))
    labels = np.array([[[0, 1], [2, 3]], [[0, -1], [-1, -1]]])
    records = []
    for generator in ("random", "structured"):
        np.savez(final / "data" / f"test_{generator}_9.npz", labels=labels)
        for seed in (0, 1):
            prediction = np.maximum(labels, 0).copy()
            if seed:
                prediction[1, 0, 0] = 1
            np.savez(final / "eval" / f"{seed}_{generator}_9_d32_t0.npz", predictions=prediction)
            records.append(dict(size=9, depth=32, trial=0, training_seed=seed, generator=generator))
    (final / "summary.json").write_text(json.dumps({"records": records, "accuracy_gate_certified": False, "G1_per_seed": {"0": 1, "1": .8}}))
    result = rescue_report.aggregate(final, bootstrap_samples=50)["measurements"][0]
    assert np.isclose(result["stone_mean"], .9)
    assert np.isclose(result["stone_seed_std"], np.std([1, .8], ddof=1))
    assert result["per_seed"][1]["per_class_accuracy"] == [.5, 1, 1, 1]
    assert result["board_exact_mean"] == .75
