"""Package the completed sealed evaluations for independent checking."""
from hashlib import sha256
import json
import subprocess
import zipfile
from .common import ROOT, write_json


def main():
    proof = json.loads((ROOT / 'results/cloud/research/completion_audit.json').read_text())
    assert proof['all_prescribed_cohorts_complete'] and proof['completed_final_evaluations'] == 27
    cohorts = json.loads((ROOT / 'results/cloud/research/final_cohorts.json').read_text())['cohorts']
    files = set()
    for cohort in cohorts.values():
        dataset = ROOT / 'results/research_final_data' / cohort['namespace']
        files.update(p for p in dataset.iterdir() if p.is_file())
        for name in cohort['runs']:
            run = ROOT / 'results/research_training' / name
            for filename in ('config.yaml', 'model.json', 'metadata.json', 'summary.json', 'ckpt/final.msgpack'):
                files.add(run / filename)
    for cohort in proof['cohorts']:
        for relative, expected in cohort['saved_prediction_files'].items():
            path = ROOT / relative
            assert sha256(path.read_bytes()).hexdigest() == expected
            files.add(path)
            run = path.parent.parent
            files.update(run / name for name in ('config.yaml', 'metadata.json', 'summary.json'))
    for folder in ('ncago', 'configs', 'tests', 'tools/cloud'):
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file()
                     and p.suffix in ('.py', '.json', '.sh') and '__pycache__' not in p.parts)
    files.update(p for p in (ROOT / 'results/cloud/research').glob('*.json'))
    for name in ('pyproject.toml', 'requirements.lock.txt', 'reports/RESEARCH_PROTOCOL.md'):
        files.add(ROOT / name)
    files.update(p for p in (ROOT / 'reports/research_followup/media').glob('*/*')
                 if p.suffix in ('.npz', '.json'))
    files.update(p for p in (ROOT / 'reports/research_followup/reproduction_sources').iterdir() if p.is_file())
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    instructions = '''# Sealed evaluation verification bundle

This archive contains all27 final evaluations, their frozen boards and labels,
the27 selected final checkpoints, saved predictions and the15 predetermined
animation state traces. Exact original code snapshots and run metadata record
the source and hardware used. The separate report package contains the GIFs,
MP4s, plots and narrative.

It supports checking the published measurements and rerunning final inference.
Training streams, full replay/optimizer states and earlier diagnostic weights
are outside this bundle. The main training was online; race oracle-cache
delivery is documented in the report and source.

Unzip into a fresh directory. Use Python3.11 or3.12 and install the pinned
dependencies in requirements.lock.txt; GPU installation instructions are in
tools/cloud/bootstrap.sh. Preserve the supplied final-data manifests.

To rerun one checkpoint, from this directory:

    python -m ncago.experiments.research_eval evaluate --runs results/research_training/RUN --namespace NAMESPACE --draws8

Replace RUN and NAMESPACE using results/cloud/research/final_cohorts.json,
and write --draws 8 as two arguments. Reruns create new evaluation records;
keep them separate from the supplied original records when aggregating scores.
Raw prediction filenames give size, depth ratio and nuisance draw. Witness
predictions are query values; whole-board predictions are per-cell classes.
Rows of confusion matrices are true classes, columns are predicted classes.
Race outcomes are nominal. Training seeds and nuisance ID draws are distinct.

MANIFEST.json lists every supplied file's SHA256. These hashes verify the
original artifacts; they do not promise bitwise neural inference equivalence
across different hardware. No final-test recipe or checkpoint selection was
performed. See the report for the measured limitations and race board domains.
'''.replace('all27', 'all 27').replace('the27', 'the 27').replace('the15', 'the 15').replace('Python3.11 or3.12', 'Python 3.11 or 3.12').replace('--draws8', '--draws 8')
    instructions = instructions.replace('and write --draws 8 as two arguments. ', '')
    out = ROOT / 'reports/research_followup/NCA_GO_EVALUATION_BUNDLE.zip'
    entries = []
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(files):
            data = path.read_bytes()
            name = str(path.relative_to(ROOT))
            archive.writestr(name, data)
            entries.append(dict(path=name, bytes=len(data), sha256=sha256(data).hexdigest()))
        archive.writestr('SOURCE_REVISION', revision+'\n')
        archive.writestr('README_EVALUATION.md', instructions)
        archive.writestr('MANIFEST.json', json.dumps(dict(source_revision=revision, files=entries), indent=2)+'\n')
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
    write_json(ROOT / 'reports/research_followup/evaluation_bundle_manifest.json', dict(
        filename=out.name, bytes=out.stat().st_size, sha256=sha256(out.read_bytes()).hexdigest(),
        final_evaluations=27, selected_checkpoints=27, learned_state_traces=15,
        CRC_verified=True, source_revision=revision, scope='Sealed inference and measured-artifact verification;not full training replay'))
    print(out, flush=True)


if __name__ == '__main__':
    main()
