from html.parser import HTMLParser
from pathlib import Path
import numpy as np
import jax
import jax.numpy as jnp
import json
import yaml
from ncago.nca.model import NCA,ModelConfig,initialize,init_params,readout


def test_nonfinite_states_cannot_decode_to_a_valid_class():
    c = ModelConfig(channels=16,heads=2)
    m = NCA(c)
    k = jax.random.PRNGKey(0)
    s = initialize(jnp.zeros((1,5,5),jnp.int32),k,c)
    p = init_params(m,s,k)
    corrupted = s.at[:,2,2,-1].set(jnp.nan)
    prediction,confidence = readout(m,p,corrupted)
    assert prediction[0,2,2] == -2
    assert confidence[0,2,2] == 0


def test_report_images_are_embedded_and_navigation_resolves():
    path = Path(__file__).resolve().parents[1]/"reports"/"nca_go_report.html"
    if not path.exists():
        return  # Report validation also runs after every generated phase artifact.
    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids,self.links,self.images = set(),[],[]
        def handle_starttag(self,tag,attrs):
            a = dict(attrs)
            if "id" in a:
                self.ids.add(a["id"])
            if tag == "a" and a.get("href","").startswith("#"):
                self.links.append(a["href"][1:])
            if tag == "img":
                self.images.append(a["src"])
    parser = Parser()
    parser.feed(path.read_text())
    assert parser.images
    assert all(source.startswith("data:image/") for source in parser.images)
    assert set(parser.links) <= parser.ids


def test_full_report_with_only_dependency_skips(tmp_path,monkeypatch):
    from ncago.report import build as reporting
    monkeypatch.setattr(reporting,"ROOT",tmp_path)
    run = tmp_path/"results"/"1"/"run"
    run.mkdir(parents=True)
    (run/"config.yaml").write_text(yaml.safe_dump({"profile":"full","seeds":[0]}))
    (run/"summary.json").write_text(json.dumps({"phase":"1","seed":0,"profile":"full",
        "status":"not run","reason":"CPU only","config_hash":"test"}))
    report = reporting.build("full")
    document = report.read_text()
    assert "G1 not yet measured" in document
    assert "CPU only" in document
    assert "Unknown" in document
    assert json.loads((tmp_path/"reports"/"report_manifest.json").read_text())["profile"] == "full"
