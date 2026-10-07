"""Optional downloads stay inside tools/ and always emit a dependency manifest."""
import argparse
import hashlib
import json
import platform
import shutil
import urllib.request
import zipfile
from html.parser import HTMLParser
from urllib.parse import urljoin
from pathlib import Path
from .common import ROOT,write_json


def fetch_json(url):
    request = urllib.request.Request(url,headers={"User-Agent":"ncago-research"})
    with urllib.request.urlopen(request,timeout=30) as response:
        return json.load(response)


def latest_network_url():
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.urls = []
        def handle_starttag(self,tag,attrs):
            values = dict(attrs)
            if tag == "a" and values.get("href","").endswith(".bin.gz"):
                self.urls.append(urljoin("https://katagotraining.org/networks/",values["href"]))
    with urllib.request.urlopen("https://katagotraining.org/networks/",timeout=30) as response:
        parser = Links()
        parser.feed(response.read().decode())
    if not parser.urls:
        raise RuntimeError("Official KataGo network index returned no network files")
    return parser.urls[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-url")
    args = parser.parse_args()
    manifest = {"platform":platform.platform(),"katago":{},"model":{}}
    try:
        release = fetch_json("https://api.github.com/repos/lightvector/KataGo/releases/latest")
        manifest["katago"]["version"] = release["tag_name"]
        manifest["katago"]["release_url"] = release["html_url"]
        assets = release.get("assets",[])
        manifest["katago"]["available_assets"] = [a["name"] for a in assets]
        system,machine = platform.system().lower(),platform.machine().lower()
        import jax
        gpu = any(device.platform == "gpu" for device in jax.devices())
        candidates = [a for a in assets if a["name"].endswith(".zip") and
            ((system == "darwin" and ("mac" in a["name"].lower() or "osx" in a["name"].lower())) or
             (system == "linux" and "linux" in a["name"].lower() and ("eigen" in a["name"].lower() or (gpu and "cuda12.1-cudnn8.9.7" in a["name"].lower())) and machine in ("x86_64","amd64")))]
        existing = shutil.which("katago")
        if existing:
            manifest["katago"]["path"] = existing
        elif not candidates:
            manifest["katago"]["reason"] = f"No compatible prebuilt Eigen binary in release for {system}/{machine}"
        else:
            asset = sorted(candidates,key=lambda a:a["name"])[0]
            directory = ROOT/"tools"/"bin"
            directory.mkdir(parents=True,exist_ok=True)
            archive = directory/asset["name"]
            urllib.request.urlretrieve(asset["browser_download_url"],archive)
            manifest["katago"]["sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
            with zipfile.ZipFile(archive) as z:
                for member in z.infolist():
                    target = (directory/member.filename).resolve()
                    if not target.is_relative_to(directory.resolve()):
                        raise ValueError("Unsafe archive path")
                z.extractall(directory)
            executable = next(directory.rglob("katago"))
            executable.chmod(0o755)
            manifest["katago"]["path"] = str(executable)
        if manifest["katago"].get("path"):
            model_url = args.model_url or latest_network_url()
            modeldir = ROOT/"tools"/"models"
            modeldir.mkdir(parents=True,exist_ok=True)
            destination = modeldir/model_url.rsplit("/",1)[-1]
            urllib.request.urlretrieve(model_url,destination)
            manifest["model"] = {"path":str(destination),"url":model_url,"sha256":hashlib.sha256(destination.read_bytes()).hexdigest()}
        else:
            manifest["model"]["reason"] = "KataGo binary unavailable or model URL not configured"
    except Exception as error:
        manifest["katago"]["reason"] = f"Download failed: {type(error).__name__}: {error}"
    write_json(ROOT/"results"/"optional_dependencies.json",manifest)
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
