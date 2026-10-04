"""Freigestellte Porträts Königin, Arbeiterin, Drohne (Spaltenköpfe der Vergleichstabelle, Aufgabe 63).

viewBox 240 × 180, transparenter Hintergrund, kein Text. Alle drei Bienen von oben (wie in volk-2), Kopf nach rechts,
im selben Maßstab: Königin und Arbeiterin Faktor 1,0, Drohne 1,06 (wie in volk-2). Die Bienen werden jeweils
in die Bildmitte gesetzt; die längste (Königin) füllt etwa 85 % der Breite.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_zeichnen import biene_o, volk_svg  # noqa: E402

AW, AH = 240, 180
S = 1.4                                        # gemeinsamer Maßstab (Einheiten der Bienenbausteine -> Pixel)
# Ausdehnung längs der Körperachse (Antennenspitze bis Hinterleibsende bzw. Flügelspitze) in Einheiten bei Faktor 1
ARTEN = {
    "koenigin": dict(art="K", faktor=1.0, y0=-74, y1=82, titel="Königin: großer Körper, langer Hinterleib, kurze Flügel, roter Punkt auf dem Rücken"),
    "arbeiterin": dict(art="A", faktor=1.0, y0=-76, y1=61, titel="Arbeiterin: kleinerer, gestreifter Körper, Flügel bis zum Ende des Hinterleibs, Stachel"),
    "drohne": dict(art="D", faktor=1.06, y0=-80, y1=58, titel="Drohne: dicker, rundlicher Körper, riesige Augen, die oben zusammenstoßen, kein Stachel"),
}


def bienenart(name):
    a = ARTEN[name]
    f = a["faktor"] * S
    mitte = (a["y0"] + a["y1"]) / 2               # Mitte der Bienenlänge (Einheiten)
    # Kopf nach rechts: Drehung 90°, lokale y-Achse läuft dann nach links; die Bienenmitte kommt in die Bildmitte
    bio = biene_o(a["art"], AW / 2 + f * mitte, AH / 2, 90, f)
    return volk_svg(f"Porträt {a['titel']}", bio, w=AW, h=AH, bausteine=a["art"], grund="none", rahmen=False)


GRAFIKEN_ARTEN = {f"bienenart-{n}": (lambda n=n: bienenart(n)) for n in ARTEN}


def schreibe_vorschau():
    """werkzeuge/ausgabe/bienenarten_vorschau.html: die drei Porträts nebeneinander bei 90 px und 180 px Höhe (Kontrolle)."""
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ausgabe")
    os.makedirs(ziel, exist_ok=True)

    def reihe(h, hintergrund, titel):
        bilder = "".join(f"<img src='../../static/img/lese/bienenart-{n}.svg' alt='{n}' style='height:{h}px;width:auto'>" for n in ARTEN)
        return f"<h2>{titel}</h2><div class='reihe' style='background:{hintergrund}'>{bilder}</div>"
    html = ("<!doctype html><html lang='de'><meta charset='utf-8'><title>Bienenarten – Vorschau</title>"
            "<style>body{font-family:Lato,Arial,sans-serif;margin:16px;background:#f0f4f8;color:#1e293b}"
            "h1{font-size:1.2rem}h2{font-size:1rem;margin:18px 0 6px}.reihe{display:flex;gap:18px;align-items:center;padding:10px;border-radius:10px}</style>"
            "<h1>Bienenarten: Königin, Arbeiterin, Drohne (transparent, 240 × 180)</h1>"
            "<p>Kontrolle: gleiche Ansicht, gleicher Maßstab, bei 90 px Höhe noch unterscheidbar.</p>"
            + reihe(90, "#ffffff", "90 px Höhe, weißer Grund (Tabellenkopf)")
            + reihe(90, "#006AB3", "90 px Höhe, dunkler Grund (Transparenz)")
            + reihe(180, "#ffffff", "180 px Höhe, weißer Grund")
            + reihe(180, "repeating-conic-gradient(#d9e2ec 0 25%, #ffffff 0 50%) 50% / 24px 24px", "180 px Höhe, Schachbrett (Transparenz)")
            + "</html>")
    with open(os.path.join(ziel, "bienenarten_vorschau.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
