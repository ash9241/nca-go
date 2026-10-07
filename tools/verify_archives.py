"""Verify CRCs, unique safe paths and every per-file SHA256 without extraction."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import zipfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('archives',nargs='+',type=Path)
args=p.parse_args()
for archive in args.archives:
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        assert len(names)==len(set(names)), 'Duplicate archive path'
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert z.testzip() is None, 'CRC mismatch'
        manifest=json.loads(z.read('PUBLIC_MANIFEST.json'))
        assert set(names)=={e['path'] for e in manifest['files']}|{'PUBLIC_MANIFEST.json'}
        for entry in manifest['files']:
            data=z.read(entry['path'])
            assert len(data)==entry['bytes']
            assert sha256(data).hexdigest()==entry['sha256'],entry['path']
    print(f'{archive.name}: {len(manifest["files"])} files verified; SHA256 {sha256(archive.read_bytes()).hexdigest()}')
