from hashlib import sha256
import numpy as np
import pytest
from ncago.go.research_data import OnlineStream
from ncago.go.cached_race_stream import CachedRaceStream
from ncago.go.generators import canonical_key
from ncago.experiments.race_stream_cache import build_cache


def test_cached_candidates_and_labels_match_online_oracle(tmp_path, monkeypatch):
    import ncago.experiments.race_stream_cache as cache_module
    validation = OnlineStream(110005, (9,), 9, 3, task='race').draw(4)
    monkeypatch.setattr(cache_module, 'validation_data', lambda config: {9: validation})
    config = dict(task='race', cap=3, data_seed=110004, validation_seed=110005,
                  validation_count=4, batch_size=4, training_steps=5)
    path = tmp_path/'cache'
    build_cache(config, 5, path)
    cached = CachedRaceStream(path, config)
    original = OnlineStream(110004, cap=3, task='race', exclude=[canonical_key(b) for b in validation[0]])
    for count in (16, 4, 4, 4, 4, 4):
        x, y = original.draw(count)
        cx, cy = cached.draw(count)
        assert cx.dtype == x.dtype and cy.dtype == y.dtype
        np.testing.assert_array_equal(cx, x)
        np.testing.assert_array_equal(cy, y)
        assert cached.digest.hexdigest() == original.digest.hexdigest()
        assert cached.rejected == original.rejected
        assert cached.seen_canonical_hashes == original.seen_canonical_hashes
    with pytest.raises(ValueError):
        cached.draw(4)
    labels = path/'labels.npy'
    labels.write_bytes(labels.read_bytes()+b'tampered')
    with pytest.raises(AssertionError):
        CachedRaceStream(path, config)
