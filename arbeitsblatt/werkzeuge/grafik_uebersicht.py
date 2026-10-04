"""Rendert alle static/img/lese/*.svg als HTML-Übersichtsseite zur Sichtprüfung (Überlappungen!).

Aufruf:
    python werkzeuge/grafik_uebersicht.py            # schreibt werkzeuge/ausgabe/grafik_uebersicht.html
    python werkzeuge/grafik_uebersicht.py --oeffnen  # und öffnet die Seite im Standardbrowser
    python werkzeuge/grafik_uebersicht.py reiter-    # nur Dateien, deren Name so beginnt (z. B. biene-)

Zeigt je Bild den Dateinamen, die viewBox und Hinweise (fehlender Titel, unerwartetes Format, Größe).
Überlappende Beschriftungen fallen nur so auf (references/fallstricke.md). Die Seite verweist relativ auf
die SVG-Dateien und läuft deshalb auch direkt von der Festplatte (file://).
"""
import os
import re
import sys
import webbrowser
from html import escape

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BILDER = os.path.join(WURZEL, "static", "img", "lese")
AUSGABE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ausgabe")
ERWARTET = {"480 288", "900 560", "240 180"}   # 240 × 180 = Porträts (tier-*.svg, bienenart-*.svg), z. B. als Spaltenbild in `tabelle`


def pruefen(pfad: str) -> tuple[str, list[str]]:
    text = open(pfad, encoding="utf-8").read()
    hinweise = []
    m = re.search(r"viewBox=['\"]0 0 (\d+) (\d+)['\"]", text)
    vb = f"{m.group(1)} {m.group(2)}" if m else "?"
    if vb not in ERWARTET:
        hinweise.append(f"viewBox {vb} (erwartet 480 × 288, 900 × 560 oder 240 × 180)")
    if "<title>" not in text:
        hinweise.append("kein <title> (Screenreader)")
    if "<script" in text or "<animate" in text:
        hinweise.append("Skript oder SMIL – nur CSS-Keyframes erlaubt")
    if len(text) > 120_000:
        hinweise.append(f"groß: {len(text) // 1024} KB")
    return vb, hinweise


def main(argv):
    praefix = next((a for a in argv if not a.startswith("--")), "")
    dateien = sorted(f for f in os.listdir(BILDER) if f.endswith(".svg") and f.startswith(praefix)) if os.path.isdir(BILDER) else []
    os.makedirs(AUSGABE, exist_ok=True)
    karten, auffaellig = [], 0
    for f in dateien:
        vb, hinweise = pruefen(os.path.join(BILDER, f))
        auffaellig += bool(hinweise)
        rel = os.path.relpath(os.path.join(BILDER, f), AUSGABE).replace(os.sep, "/")
        karten.append(
            f"<figure class='k{' warn' if hinweise else ''}'><img src='{escape(rel)}' alt='{escape(f)}' loading='lazy'>"
            f"<figcaption><b>{escape(f)}</b> <small>{vb}</small>"
            + "".join(f"<br><em>⚠ {escape(h)}</em>" for h in hinweise) + "</figcaption></figure>")
    seite = f"""<!doctype html><html lang="de"><meta charset="utf-8"><title>Schaubilder – Übersicht</title>
<style>
 body {{ font-family: Lato, Arial, sans-serif; margin: 16px; background: #f0f4f8; color: #1e293b }}
 h1 {{ font-size: 1.2rem }} .raster {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 14px }}
 .k {{ margin: 0; background: #fff; border-radius: 10px; padding: 8px; box-shadow: 0 1px 6px #0002 }}
 .k img {{ width: 100%; height: auto; display: block; border-radius: 8px; background: #fff }}
 .k figcaption {{ font-size: .85rem; margin-top: 6px }} .warn {{ outline: 3px solid #d97706 }} em {{ color: #b45309 }}
</style><h1>{len(dateien)} Schaubilder aus static/img/lese/ · {auffaellig} mit Hinweis</h1>
<p>Prüfen: Überlappungen, abgeschnittene Beschriftung, Pfeilbeschriftung über/unter der Linie (≥ 10 px Abstand).</p>
<div class="raster">{"".join(karten) or "<p>Keine SVG-Dateien gefunden.</p>"}</div></html>"""
    ziel = os.path.join(AUSGABE, "grafik_uebersicht.html")
    with open(ziel, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(seite)
    print(f"{len(dateien)} Bilder, {auffaellig} mit Hinweis -> {ziel}")
    if "--oeffnen" in argv:
        webbrowser.open("file:///" + ziel.replace(os.sep, "/"))


if __name__ == "__main__":
    main(sys.argv[1:])
