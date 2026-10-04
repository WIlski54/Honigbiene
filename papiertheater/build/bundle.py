"""Packt die Animation in EINE HTML-Datei (Skripte + Tonspur eingebettet), die offline per Doppelklick läuft.

Aufruf: python build/bundle.py            -> <datei>.html im Projektordner
        python build/bundle.py --artifact -> zusätzlich build/artifact.html (ohne eigenes Seitengerüst, zum Veröffentlichen als Artifact)
"""
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
narr = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))

html = (SRC / "index.html").read_text(encoding="utf8")
mp3 = base64.b64encode((ROOT / "assets" / "soundtrack.mp3").read_bytes()).decode("ascii")


def inline(m):
    code = (SRC / m.group(1)).read_text(encoding="utf8").replace("</script", "<\\/script")
    return f"<script>/* {m.group(1)} */\n{code}\n</script>"


html = re.sub(r'<script src="([\w.]+\.js)"></script>', inline, html)
html = html.replace("<script>/* data.js */", f'<script>window.SOUNDTRACK_SRC = "data:audio/mpeg;base64,{mp3}";</script>\n<script>/* data.js */', 1)
out = ROOT / (narr["datei"] + ".html")
out.write_text(html, encoding="utf8")
print(f"{out.name}: {out.stat().st_size / 1e6:.1f} MB")

# README-Platzhalter füllen
readme = ROOT / "README.md"
if readme.exists() and "{{" in readme.read_text(encoding="utf8"):
    dur = json.loads((ROOT / "build" / "timeline.json").read_text(encoding="utf8"))["dauer"]
    r = readme.read_text(encoding="utf8")
    for k, v in {"TITEL": narr["titel"], "DATEI": narr["datei"], "SZENEN": str(len(narr["szenen"])),
                 "MINUTEN": f"{int(dur // 60)}:{int(dur % 60):02d} Minuten"}.items():
        r = r.replace("{{" + k + "}}", v)
    readme.write_text(r, encoding="utf8")
    print("README.md ausgefüllt")

if "--artifact" in sys.argv:
    a = re.sub(r"<!DOCTYPE html>\s*<html[^>]*>\s*<head>\s*(<meta[^>]*>\s*)*", "", html, count=1)
    a = a.replace("</head>", "", 1)
    a = re.sub(r'<body class="awake">', '<script>document.documentElement.lang="de";document.body.classList.add("awake");</script>', a, count=1)
    a = a.replace("</body>", "").replace("</html>", "")
    assert a.lstrip().startswith("<title>"), "Titel muss am Anfang stehen"
    (ROOT / "build" / "artifact.html").write_text(a, encoding="utf8")
    print("build/artifact.html erstellt (Artifact-Tool: file_path auf diese Datei)")
