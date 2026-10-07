"""Archive exact code revisions recorded by measured GPU runs."""
from collections import defaultdict
from hashlib import sha256
import json
import subprocess
import tarfile
from .common import ROOT, write_json


def main():
    revisions = defaultdict(list)
    for phase in ('research_training', 'research_evaluation'):
        for path in sorted((ROOT / 'results' / phase).glob('*/summary.json')):
            summary = json.loads(path.read_text())
            if any('cuda' in device.lower() or 'gpu' in device.lower() for device in summary['hardware']['devices']):
                revisions[summary['commit']].append(dict(phase=phase, run=path.parent.name))
    out = ROOT / 'reports/research_followup/reproduction_sources'
    out.mkdir(parents=True, exist_ok=True)
    allowed = ('ncago', 'configs', 'tests', 'tools', 'pyproject.toml', 'requirements.lock.txt')
    rows = []
    for revision, runs in sorted(revisions.items()):
        tracked = subprocess.check_output(['git', 'ls-tree', '--name-only', revision], cwd=ROOT, text=True).splitlines()
        paths = [name for name in allowed if name in tracked]
        archive = out / (revision+'.tar.gz')
        if not archive.exists():
            subprocess.run(['git', 'archive', '--format=tar.gz', '--output', str(archive), revision, *paths], cwd=ROOT, check=True)
        with tarfile.open(archive) as saved:
            assert all(entry.name.split('/')[0] in paths for entry in saved.getmembers())
        rows.append(dict(revision=revision, archive=archive.name, bytes=archive.stat().st_size,
                         sha256=sha256(archive.read_bytes()).hexdigest(), paths=paths, runs=runs))
    write_json(out / 'manifest.json', dict(revisions=rows,
        scope='Exact tracked code/configuration/test/tool trees;data,weights,credentials and Git internals excluded'))
    print(f'{len(rows)} exact run source revisions archived', flush=True)


if __name__ == '__main__':
    main()
