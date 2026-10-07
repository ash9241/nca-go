"""Create an offline follow-up report and bundle, without publishing it."""
import base64
from datetime import datetime, timezone
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import zipfile
import subprocess
from PIL import Image
from .common import ROOT, write_json

OUT = ROOT / 'reports/research_followup'


def data_url(path):
    kind = 'image/gif' if path.suffix == '.gif' else 'image/png'
    return f'data:{kind};base64,'+base64.b64encode(path.read_bytes()).decode()


def inline(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    def link(match):
        title, href = match.groups()
        if 'RESEARCH_PROTOCOL.md' in href:
            href = '#protocol'
        elif 'checkpoint_audit/SUMMARY.md' in href:
            href = '#audit'
        return '<a href="'+href+'">'+title+'</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)


def markdown(text, directory):
    """Render the bounded Markdown subset emitted by the research scripts."""
    lines, output, i = text.splitlines(), [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.startswith('```'):
            code = []; i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i += 1
            output.append('<pre><code>'+escape('\n'.join(code))+'</code></pre>'); i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                row = [x.strip() for x in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', x) for x in row):
                    rows.append(row)
                i += 1
            body = []
            for n, row in enumerate(rows):
                cell = 'th' if n == 0 else 'td'
                body.append('<tr>'+''.join(f'<{cell}>{inline(x)}</{cell}>' for x in row)+'</tr>')
            output.append('<div class="table"><table>'+''.join(body)+'</table></div>'); continue
        image = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        if image:
            path = directory / image.group(2)
            output.append('<figure><img src="'+data_url(path)+'" alt="'+escape(image.group(1))+'"></figure>')
            i += 1; continue
        heading = re.match(r'^(#{1,6}) (.*)$', line)
        if heading:
            level = len(heading.group(1))
            output.append(f'<h{level}>'+inline(heading.group(2))+f'</h{level}>'); i += 1; continue
        if line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append('<li>'+inline(lines[i][2:])+'</li>'); i += 1
            output.append('<ul>'+''.join(items)+'</ul>'); continue
        paragraph = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '```', '- ', '![')):
            paragraph.append(lines[i]); i += 1
        output.append('<p>'+inline(' '.join(paragraph))+'</p>')
    return '\n'.join(output)


def animation(path, caption):
    with Image.open(path) as im:
        poster = BytesIO(); im.seek(0); im.convert('RGB').save(poster, format='PNG')
        count = getattr(im, 'n_frames', 1)
    source = 'data:image/png;base64,'+base64.b64encode(poster.getvalue()).decode()
    return ('<details class="animation"><summary>'+escape(caption)+f' · {count} frames</summary>'
            '<p>One predetermined example. Aggregate accuracy and pair-both-correct tables carry the scientific claims.</p>'
            '<button type="button" aria-pressed="false">Play animation</button>'
            '<img alt="'+escape(caption)+'" src="'+source+'" data-poster="'+source+'" data-gif="'+data_url(path)+'"></details>')


def main():
    result = json.loads((OUT / 'RESULTS.json').read_text())
    body = markdown((OUT / 'REPORT.md').read_text(), OUT)
    body += '<section><h2>Final accuracy against rollout depth</h2><p>Macro accuracy averages supported label classes. Curves average the recorded nuisance draws and independent training seeds within each architecture and recipe. Whole-board depth uses the maximum chain diameter. Random capture-race boards are playable 5×N rectangles.</p>'
    for filename, caption in (
        ('depth_by_diameter_liberties_cap4.png', 'Main capped-liberty task: all six matched architecture groups, three training seeds each'),
        ('depth_by_diameter_liberties_cap16.png', 'Liberties 1–15 and 16+: three NCA training seeds'),
        ('depth_by_diameter_eyes_cap9.png', 'Static simple-eye counts: three NCA training seeds; class support is disclosed in the tables'),
        ('depth_by_diameter_race_cap3.png', 'First-capture outcomes on 5×N boards: three NCA training seeds')):
        path = OUT / filename
        if path.exists():
            body += '<figure><img alt="'+escape(caption)+'" src="'+data_url(path)+'"><figcaption>'+escape(caption)+'</figcaption></figure>'
    body += '</section>'
    if (OUT / 'CONFUSIONS.md').exists():
        body += '<details><summary>All new final-test and witness confusion matrices</summary>'+markdown((OUT / 'CONFUSIONS.md').read_text(), OUT)+'</details>'
    audit = ROOT / 'reports/checkpoint_audit'
    body += '<section id="audit"><h2>Existing-checkpoint audit</h2>'
    body += '<p>These are descriptive analyses of previously opened tests. They did not select new models on larger final data.</p>'
    for name, caption in [('error_strata.png', 'Errors by diameter, cycle, chain size and edge distance'),
                          ('query_edge_accuracy.png', 'Old checkpoint accuracy by the query stone distance to the edge'),
                          ('batched_rollout_dynamics.png', 'Old checkpoints: mutable-state change and prediction flips past step32'),
                          ('reference_depth.png', 'Hand-coded identifier-set reference; message rounds follow one local-ID loading phase')]:
        if (audit / name).exists():
            body += '<figure><img alt="'+escape(caption)+'" src="'+data_url(audit / name)+'"><figcaption>'+escape(caption)+'</figcaption></figure>'
    body += '<details><summary>All old final-test and witness confusion matrices</summary>'+markdown((audit / 'SUMMARY.md').read_text(), audit)+'</details></section>'
    if (audit / 'QUERY_EDGE.md').exists():
        body += '<details><summary>Query-edge strata and explicit overcount/undercount matrices</summary>'+markdown((audit / 'QUERY_EDGE.md').read_text(), audit)+'</details>'
    media = sorted((OUT / 'media').glob('*/*.gif'))
    body += '<section><h2>Recorded animations</h2>'
    for path in media:
        caption = path.stem.replace('_', ' ')+' · '+path.parent.name
        body += animation(path, caption)
    if (audit / 'reference_propagation.gif').exists():
        body += animation(audit / 'reference_propagation.gif', 'Hand-coded ID-set algorithm; not a learned model')
    body += '<p><a href="historical_report.html">Original report and its complete animation archive</a></p></section>'
    body += '<details id="protocol"><summary>Prespecified protocol and documented extensions</summary>'+markdown((ROOT / 'reports/RESEARCH_PROTOCOL.md').read_text(), ROOT / 'reports')+'</details>'
    css = '''*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#172c3e;font:16px/1.65 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:36px 28px 80px}h1{font-size:42px;line-height:1.12;letter-spacing:-1px}h2{font-size:27px;margin-top:44px}h3{font-size:21px}p{max-width:1000px}a{color:#246e9d}code{font-size:12px;overflow-wrap:anywhere}pre{padding:18px;background:#e8eef5;overflow:auto;font-size:12px}.table{overflow:auto;margin:20px 0;border:1px solid #d7e0e8}table{border-collapse:collapse;min-width:100%;background:white;font-size:12px}td,th{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid #d7e0e8}th{background:#e8eef5;white-space:nowrap}img{display:block;width:100%;height:auto;border:1px solid #d7e0e8;background:white}figure{margin:28px 0}figcaption{font-size:13px;color:#4d6577}details{background:white;padding:18px 22px;border:1px solid #d7e0e8;margin:18px 0}summary{cursor:pointer;font-weight:650}button{font:600 14px system-ui;background:#246e9d;color:white;border:0;padding:10px 16px;margin:12px 0;cursor:pointer}button:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #e39b2f;outline-offset:3px}.meta{font-size:13px;color:#4d6577}.note{padding:16px 20px;background:#eaf2f8;border-left:4px solid #246e9d}@media(max-width:650px){main{padding:24px 16px}h1{font-size:32px}h2{font-size:24px}details{padding:15px}td,th{padding:8px}}'''
    javascript = '''document.querySelectorAll('.animation').forEach(d=>{const i=d.querySelector('img'),b=d.querySelector('button');const stop=()=>{i.src=i.dataset.poster;b.textContent='Play animation';b.setAttribute('aria-pressed','false')};b.addEventListener('click',()=>{if(b.getAttribute('aria-pressed')==='true')stop();else{i.src=i.dataset.gif;b.textContent='Pause animation';b.setAttribute('aria-pressed','true')}});d.addEventListener('toggle',()=>{if(!d.open)stop()})});'''
    now = datetime.now(timezone.utc).isoformat()
    completed = sum(row['gpu'] and row['summary']['status'] == 'complete' for row in result['training'])
    document = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NCA Go follow-up research</title><style>'+css+'</style></head><body><main><p class="meta">NCA GO · FOLLOW-UP EXPERIMENT ARCHIVE · '+escape(now)+'</p><p class="note">'+str(completed)+' completed new GPU training attempts are archived. The tables distinguish validation, final tests, warmstarts and unfinished work. Hand-coded algorithm demonstrations remain separate from learned results.</p>'+body+'<footer class="meta">Offline report generated from saved measured artifacts. No social post or website was published.</footer></main><script>'+javascript+'</script></body></html>'
    (OUT / 'NCA_GO_FOLLOWUP.html').write_text(document)
    historical = (ROOT / 'reports/shareable/NCA_GO_REPORT.html').read_text()
    historical = historical.replace('href="media/', 'href="historical_media/').replace('src="media/', 'src="historical_media/').replace('href="data/', 'href="historical_data/')
    historical = historical.replace('href="NCA_GO_SHARE_PACKAGE.zip"', 'href="NCA_GO_FOLLOWUP_PACKAGE.zip"')
    (OUT / 'historical_report.html').write_text(historical)
    (OUT / 'historical_media').mkdir(exist_ok=True)
    for path in (ROOT / 'reports/shareable/media').glob('*.mp4'):
        shutil.copy2(path, OUT / 'historical_media' / path.name)
    shutil.copytree(ROOT / 'reports/shareable/data', OUT / 'historical_data', dirs_exist_ok=True)
    bundle = OUT / 'NCA_GO_FOLLOWUP_PACKAGE.zip'
    files = [OUT / 'NCA_GO_FOLLOWUP.html', OUT / 'historical_report.html', OUT / 'REPORT.md', OUT / 'RESULTS.json',
             *OUT.glob('*.csv'), *OUT.glob('*.png'), OUT / 'learning_curves.json', *media,
             *OUT.glob('media/*/manifest.json'), *OUT.glob('media/*/*.mp4'),
             *OUT.glob('reproduction_sources/*.tar.gz'), *OUT.glob('reproduction_sources/manifest.json'),
             *OUT.glob('historical_media/*.mp4'), *OUT.glob('historical_data/*')]
    files += [p for p in (OUT / 'CONFUSIONS.md', OUT / 'confusions.json', OUT / 'stability_dynamics_summary.json',
                          OUT / 'TWITTER_DRAFT.md', OUT / 'social_figure_measurements.json', OUT / 'pair_members.json',
                          OUT / 'outcome_summary.json') if p.exists()]
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, str(path.relative_to(OUT)))
        archive.write(ROOT / 'reports/RESEARCH_PROTOCOL.md', 'protocol.md')
        for path in audit.glob('*.json'):
            archive.write(path, 'existing_checkpoint_audit/'+path.name)
        for path in audit.glob('*.md'):
            archive.write(path, 'existing_checkpoint_audit/'+path.name)
        for path in (ROOT / 'results/cloud/research').glob('*.json'):
            archive.write(path, 'provenance/'+path.name)
        for path in (ROOT / 'results/research_final_data').glob('*/manifest.json'):
            archive.write(path, 'frozen_final_sets/'+path.parent.name+'/manifest.json')
        for path in (ROOT / 'results/race_stream_cache').glob('*/manifest.json'):
            archive.write(path, 'oracle_cache_manifests/'+path.parent.name+'/manifest.json')
        for family in ('research_training', 'research_evaluation'):
            for summary in (ROOT / 'results' / family).glob('*/summary.json'):
                for name in ('config.yaml', 'model.json', 'metadata.json', 'summary.json', 'initialization.json', 'metrics.jsonl'):
                    path = summary.parent / name
                    if path.exists():
                        archive.write(path, f'run_records/{family}/{summary.parent.name}/{name}')
        for folder in ('ncago', 'configs', 'tests', 'tools/cloud'):
            for path in (ROOT / folder).rglob('*'):
                if path.is_file() and path.suffix in ('.py', '.json', '.sh') and '__pycache__' not in path.parts:
                    archive.write(path, 'source/'+str(path.relative_to(ROOT)))
        for name in ('pyproject.toml', 'requirements.lock.txt', 'README.md', 'DECISIONS.md', 'SPECIFICATION.md'):
            path = ROOT / name
            if path.exists():
                archive.write(path, 'source/'+name)
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        archive.writestr('source/SOURCE_REVISION', revision+'\n')
    write_json(OUT / 'share_manifest.json', dict(created_utc=now, completed_new_gpu_training=completed,
                                               learned_animations=len(media), reference_learned=False,
                                               historical_archive='historical_report.html', published=False))
    print(OUT / 'NCA_GO_FOLLOWUP.html', flush=True)


if __name__ == '__main__':
    main()
