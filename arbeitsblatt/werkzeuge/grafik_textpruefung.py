"""Prüft Beschriftungen in SVG-Schaubildern mit dem Browser (Edge headless): Überlappungen, Abstand zu Pfeillinien, Rand.

Aufruf:   python werkzeuge/grafik_textpruefung.py nutztier-1 koerper-2 …     (Namen ohne .svg, aus static/img/lese)
          python werkzeuge/grafik_textpruefung.py --alle koerper-            (alle Dateien mit diesem Anfang)
          python werkzeuge/grafik_textpruefung.py imker-karte --objekte      (zusätzlich Rahmen der Gruppen id='o-…')

Je Bild: Zahl der <text>-Elemente, Überlappungen von Texten (getBoundingClientRect), Texte, die weniger als 4 px von einer
Pfeillinie (<line> oder <path> mit marker-end) entfernt liegen (Beschriftung nie auf der Linie), Texte näher als 3 px am Rand.
Ausgabe 0 Probleme = in Ordnung. Benötigt Edge unter C:/Program Files (x86)/Microsoft/Edge/Application/.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BILDER = os.path.join(WURZEL, "static", "img", "lese")
EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"

JS = r"""
const svg = document.querySelector('svg');
const vb = svg.viewBox.baseVal;
const S = svg.getBoundingClientRect();
const k = vb.width / S.width;
function box(el) { const r = el.getBoundingClientRect(); return [(r.left - S.left) * k, (r.top - S.top) * k, (r.right - S.left) * k, (r.bottom - S.top) * k]; }
function dpt(b, x, y) { const dx = Math.max(b[0] - x, 0, x - b[2]), dy = Math.max(b[1] - y, 0, y - b[3]); return Math.hypot(dx, dy); }
const texte = [...svg.querySelectorAll('text')].map(t => ({ t: t.textContent, b: box(t) }));
const probleme = [];
for (let i = 0; i < texte.length; i++) for (let j = i + 1; j < texte.length; j++) {
  const a = texte[i].b, b = texte[j].b;
  if (a[0] < b[2] - 1 && b[0] < a[2] - 1 && a[1] < b[3] - 1 && b[1] < a[3] - 1) probleme.push('Überlappung: "' + texte[i].t + '" / "' + texte[j].t + '"');
}
// Pfeillinien: <line marker-end> und <path marker-end> (Strecken per Stichprobe entlang des Pfads)
const linien = [];
svg.querySelectorAll('[marker-end]').forEach(el => {
  if (el.tagName === 'line') linien.push([el.x1.baseVal.value, el.y1.baseVal.value, el.x2.baseVal.value, el.y2.baseVal.value]);
});
function dseg(px, py, l) { const [x1, y1, x2, y2] = l; const dx = x2 - x1, dy = y2 - y1; const L2 = dx * dx + dy * dy || 1; let u = ((px - x1) * dx + (py - y1) * dy) / L2; u = Math.max(0, Math.min(1, u)); return Math.hypot(px - (x1 + u * dx), py - (y1 + u * dy)); }
for (const tx of texte) {
  const b = tx.b;
  for (const l of linien) {
    let m = 1e9;
    for (let n = 0; n <= 40; n++) { const px = l[0] + (l[2] - l[0]) * n / 40, py = l[1] + (l[3] - l[1]) * n / 40; m = Math.min(m, dpt(b, px, py)); }
    if (m < 4) probleme.push('Text nah an Pfeil (' + m.toFixed(1) + ' px): "' + tx.t + '"');
  }
  if (b[0] < 3 || b[1] < 3 || b[2] > vb.width - 3 || b[3] > vb.height - 3) probleme.push('Text am Rand/abgeschnitten: "' + tx.t + '" ' + b.map(v => v.toFixed(0)).join(','));
}
const objekte = {};
svg.querySelectorAll('g[id^="o-"]').forEach(g => { objekte[g.id.slice(2)] = box(g).map(v => Math.round(v)); });
const out = { texte: texte.length, probleme, objekte, textboxen: texte.map(t => [t.t, t.b.map(v => Math.round(v))]) };
document.getElementById('out').textContent = JSON.stringify(out);
"""


def pruefe(name):
    pfad = os.path.join(BILDER, name + ".svg")
    svgtext = open(pfad, encoding="utf-8").read()
    m = re.search(r"viewBox='0 0 (\d+) (\d+)'", svgtext)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (480, 288)
    svgtext = svgtext.replace("<svg ", f"<svg style='width:{w * 2}px;height:{h * 2}px;display:block' ", 1)
    html = f"<!doctype html><meta charset='utf-8'><body style='margin:0'>{svgtext}<pre id='out'></pre><script>{JS}</script>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = f.name
    prof = tempfile.mkdtemp()
    try:
        r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", "--virtual-time-budget=4000",
                            "--dump-dom", "file:///" + tmp.replace("\\", "/")], capture_output=True, timeout=90)
    finally:
        os.unlink(tmp)
        import shutil
        shutil.rmtree(prof, ignore_errors=True)
    dom = r.stdout.decode("utf-8", "replace")
    mm = re.search(r"<pre id=\"out\">(.*?)</pre>", dom, re.S)
    if not mm:
        return {"fehler": "keine Ausgabe", "probleme": ["Messung fehlgeschlagen"], "texte": 0, "objekte": {}}
    import html as _h
    return json.loads(_h.unescape(mm.group(1)))


def main(argv):
    namen = [a for a in argv if not a.startswith("--")]
    if "--alle" in argv:
        pre = namen[0] if namen else ""
        namen = sorted(f[:-4] for f in os.listdir(BILDER) if f.endswith(".svg") and f.startswith(pre))
    gesamt = 0
    for n in namen:
        r = pruefe(n)
        gesamt += len(r["probleme"])
        print(f"{n}: {r['texte']} Texte, {len(r['probleme'])} Probleme")
        for p in r["probleme"]:
            print("   -", p)
        if "--objekte" in argv:
            for k, v in r["objekte"].items():
                print("   objekt", k, v)
    print("Gesamt:", gesamt, "Probleme")
    return 1 if gesamt else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
