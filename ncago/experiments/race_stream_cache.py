"""Materialize an exact deterministic oracle stream for faster race replicas."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
import numpy as np
from ncago.go.research_data import OnlineStream
from ncago.go.generators import canonical_key
from .research_train import validation_data
from .common import write_json


def build_cache(config, steps, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    assert config['task'] == 'race'
    output.mkdir(parents=True)
    validation = validation_data(config)
    exclusions = [canonical_key(b) for boards, _ in validation.values() for b in boards]
    stream = OnlineStream(config['data_seed'], cap=config['cap'], exclude=exclusions, task='race')
    batch = config['batch_size']
    count = (4+steps)*batch
    boards = np.lib.format.open_memmap(output/'boards.npy', mode='w+', dtype=np.int8, shape=(count, 9, 9))
    labels = np.lib.format.open_memmap(output/'labels.npy', mode='w+', dtype=np.int8, shape=(count, 9, 9))
    rejected = np.zeros(steps+1, np.int64)
    consumed, start = 0, time.perf_counter()
    for index in range(steps+1):
        n = 4*batch if index == 0 else batch
        x, y = stream.draw(n)
        boards[consumed:consumed+n], labels[consumed:consumed+n] = x, y
        consumed += n; rejected[index] = stream.rejected
        if index % 100 == 0 or index == steps:
            boards.flush(); labels.flush()
            print(f'Oracle cache {index}/{steps}: {consumed} boards; {time.perf_counter()-start:.1f}s', flush=True)
    np.save(output/'prefix_rejected.npy', rejected)
    files = {p.name: sha256(p.read_bytes()).hexdigest() for p in output.glob('*.npy')}
    write_json(output/'manifest.json', dict(task='race', cap=config['cap'], data_seed=config['data_seed'],
        batch_size=batch, steps=steps, count=count, stream_sha256=stream.digest.hexdigest(),
        files=files, validation_exclusions=len(exclusions), validation_seed=config['validation_seed'],
        validation_count=config['validation_count'], generator_source='ncago.go.research_data.OnlineStream',
        scope='Exact same prescribed candidate order and oracle labels;materialized delivery for richer-task replicas',
        wall_seconds=time.perf_counter()-start))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True, type=Path)
    p.add_argument('--steps', type=int, default=20000)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    build_cache(json.loads(a.config.read_text()), a.steps, a.output)


if __name__ == '__main__':
    main()
