"""Read the identical oracle-generated candidate stream in its original order."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .generators import canonical_key


class CachedRaceStream:
    def __init__(self, path, config):
        self.path = Path(path)
        manifest = json.loads((self.path/'manifest.json').read_text())
        assert config['task'] == manifest['task'] == 'race'
        for key in ('cap', 'data_seed', 'batch_size', 'validation_seed', 'validation_count'):
            assert config[key] == manifest[key], key
        assert config['training_steps'] <= manifest['steps']
        for name, digest in manifest['files'].items():
            assert sha256((self.path/name).read_bytes()).hexdigest() == digest, name
        self.boards = np.load(self.path/'boards.npy', mmap_mode='r')
        self.labels = np.load(self.path/'labels.npy', mmap_mode='r')
        self.prefix_rejected = np.load(self.path/'prefix_rejected.npy')
        self.batch, self.calls, self.draws, self.rejected = manifest['batch_size'], 0, 0, 0
        self.digest, self.seen_canonical_hashes = sha256(), set()
        self.last_sources, self.source_draw_counts = [], {}

    def draw(self, count):
        expected = 4*self.batch if self.calls == 0 else self.batch
        if count != expected or self.draws+count > len(self.boards):
            raise ValueError('Cached race stream consumed with a different batch protocol')
        x = np.array(self.boards[self.draws:self.draws+count], dtype=np.int8)
        y = np.array(self.labels[self.draws:self.draws+count], dtype=np.int32)
        for board in x:
            self.digest.update(board.tobytes())
            self.seen_canonical_hashes.add(sha256(canonical_key(board)).digest())
        self.rejected = int(self.prefix_rejected[self.calls])
        self.calls += 1; self.draws += count
        self.last_sources = ['regular_rectangular_race']*count
        self.source_draw_counts = {'regular_rectangular_race': self.draws}
        return x, y
