import numpy as np
from ncago.go.research_data import witness_set, count_labels


def test_cap16_pairs_cover_higher_counts_and_single_distant_edit():
    counts = (1, 5, 6, 8, 10, 12, 14, 15)
    for size in (9, 13, 19, 25, 37):
        data = witness_set(size, per_geometry=8, seed=120001+size, liberty_counts=counts, cap=16)
        assert len(data['boards']) == 80
        assert set(data['geometries']) == {'straight', 'elbow', 'snake', 'comb', 'ring'}
        for index in range(0, 80, 2):
            a, b = data['boards'][index:index+2]
            q = tuple(data['queries'][index])
            edited = np.argwhere(a != b)
            assert len(edited) == 1
            k = int(data['base_liberty_count'][index])
            assert data['labels'][index:index+2].tolist() == [k-1, k]
            assert (count_labels(a, 16)[q], count_labels(b, 16)[q]) == (k-1, k)
            assert np.abs(edited[0]-np.array(q)).max() == data['causal_distance'][index]
        assert set(data['labels']) >= {4, 5, 14, 15}
