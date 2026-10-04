"""Schaubilder des Reiters „Nutztier Biene“ (Lesestrecke L1) und die Karte „Beim Imker“.

Aufruf:  python werkzeuge/grafiken_nutztier.py
Ausgabe: static/img/lese/nutztier-1.svg … nutztier-4.svg, glossar-bienenkasten.svg (480 × 288),
         imker-karte.svg (900 × 560) und werkzeuge/imker_karte_punkte.json (Mittelpunkte der antippbaren Objekte).

Die Karte trägt keine Nummern und keine Beschriftung; das Modul bildpunkte.js zeichnet die Nummern darüber.
"""
import json
import os

from bienen_zeichnen import *  # noqa: F401,F403
from szenen_zeichnen import *  # noqa: F401,F403

HIER = os.path.dirname(os.path.abspath(__file__))


def biene_dir(x, y, s=.5, rot=0, links=False):
    """Kleine fliegende Biene (biene_klein), optional nach links blickend."""
    b = biene_klein(0, 0, s, rot)
    if links:
        return f"<g transform='translate({x:.1f} {y:.1f}) scale(-1 1)'>{b}</g>"
    return f"<g transform='translate({x:.1f} {y:.1f})'>{b}</g>"


def flugspur(d, farbe="#ffffff", w=1.4, opa=.85):
    return f"<path d='{d}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-dasharray='1.5 5' stroke-linecap='round' opacity='{opa}'/>"


def chip(x, y, text, size=13, farbe=TEXT, fuell="#ffffff"):
    """Kleines Schild (weißer Kasten mit Text) – für kurze Beschriftungen auf Fotohintergründen."""
    w = len(text) * size * .6 + 18
    return (f"<rect x='{x - w / 2:.1f}' y='{y - size - 3:.1f}' width='{w:.1f}' height='{size + 12:.1f}' rx='{(size + 12) / 2:.1f}' fill='{fuell}' opacity='.94' stroke='#cbd5e1'/>"
            + tp(x, y + 1, text, size, 800, farbe))


# ═══════════════════════════════════════════════════════════════════════════
def nutztier_1():
    p = [sonne(430, 40, 15), wolke(96, 40, .75), wolke(300, 52, .6),
         huegel(150, "#bfe19a", "#9ccb6f", amp=9, phase=.3), ferne_baeume([210, 238, 262], 164, .5, "#79b05d"),
         huegel(176, "#a9d97c", "#74ad48", amp=7, phase=1.6),
         stall(104, 180, .98),
         zaun(0, 330, 200, .85)]
    # Bienenkästen am rechten Rand
    p += [bienenkasten(406, 226, .66, "#f2cf5e"), bienenkasten(452, 240, .66, "#8fc3ea")]
    p += [blume_gross(376, 254, .5, "#f06aa0", stiel=26), blume_gross(428, 258, .5, "#fff", stiel=22), blume_gross(472, 256, .5, "#b58cf0", stiel=24)]
    p += [flugspur("M396,182 C404,164 424,154 442,164"), biene_dir(402, 174, .42, -8), biene_dir(436, 152, .4, 10, True), biene_dir(462, 196, .4, -6, True), biene_dir(380, 196, .36, 8)]
    # Tiere und ihre Erzeugnisse
    p += [kuh(94, 246, .74), milchkanne(22, 252, .95), wollknaeuel(176, 254, .8), schaf(226, 248, .82),
          huhn(300, 252, .9), kueken(332, 254, .8), eier(352, 255, .8)]
    p.append(fussleiste(["Nutztiere helfen uns"], hoehe=30, size=13))
    return bild("Schaubild: Bauernhof mit Kuh, Schaf, Huhn und Stall, am rechten Rand zwei Bienenkästen mit Bienen", *p)


# ═══════════════════════════════════════════════════════════════════════════
def nutztier_2():
    p = [sonne(424, 44, 16), wolke(80, 44, .8), wolke(250, 34, .55),
         huegel(132, "#c2e29e", "#9fcc72", amp=9, phase=.8), ferne_baeume([30, 70, 120, 330, 380], 150, .55, "#6fa956"),
         huegel(166, "#a9d97c", "#6fa845", amp=8, phase=2.2)]
    # Kästen in der Mitte (leicht gestaffelt)
    p += [bienenkasten(102, 206, .86, "#f2cf5e"), bienenkasten(206, 214, .86, "#8fc3ea"), bienenkasten(304, 204, .86, "#f4f0e2")]
    # Blumenwiese vorn
    farben = ["#f06aa0", "#ffffff", "#b58cf0", "#ff8a4a", "#f6dc3a", "#f06aa0", "#7fb7ff"]
    rng = random.Random(11)
    for i in range(22):
        bx = 12 + i * 21 + rng.uniform(-6, 6)
        by = 236 + rng.uniform(0, 18)
        p.append(blume_gross(bx, by, rng.uniform(.5, .8), farben[i % len(farben)], stiel=rng.uniform(20, 30)))
    # Imker am rechten Rand
    p.append(imker(412, 250, 1.28, haende=((-26, -42), (26, -42))))
    # fliegende Bienen mit Flugspuren
    p += [flugspur("M120,186 C140,150 170,136 200,150"), flugspur("M222,196 C250,160 270,170 290,150"), flugspur("M310,186 C340,166 360,176 372,168"),
          flugspur("M60,226 C80,200 96,196 110,200", opa=.6), flugspur("M250,230 C262,214 270,212 284,214", opa=.6)]
    for bx, by, r, l in [(204, 148, -10, False), (160, 138, 8, True), (290, 148, -6, False), (262, 172, 12, True), (360, 168, -4, True), (128, 176, 10, False),
                         (84, 196, -8, True), (236, 202, 6, False), (330, 190, -6, False), (60, 224, 8, False), (278, 214, -6, True)]:
        p.append(biene_dir(bx, by, .46, r, l))
    p.append(fussleiste(["Die Biene lebt frei"], hoehe=30, size=13))
    return bild("Schaubild: Drei Bienenkästen auf einer Blumenwiese, ein Imker mit Hut und Schleier und fliegende Bienen", *p)


# ═══════════════════════════════════════════════════════════════════════════
def nutztier_3():
    wand = "<rect width='480' height='288' fill='#fdf1cf'/><circle cx='150' cy='120' r='170' fill='#fff8e0' opacity='.8'/>"
    tisch = ("<rect x='0' y='206' width='480' height='82' fill='url(#gHolz)'/>"
             "<path d='M0,206 H480' stroke='#7a4b22' stroke-width='3'/>"
             "<path d='M0,230 H480 M0,254 H480 M0,276 H480' stroke='#7a4b22' stroke-width='1' opacity='.35'/>"
             "<path d='M70,206 V230 M300,230 V254 M150,254 V276 M390,206 V230' stroke='#7a4b22' stroke-width='1' opacity='.3'/>"
             "<rect x='0' y='206' width='480' height='10' fill='#fff' opacity='.18'/>")
    p = [wand, tisch]
    # Apfelzweig rechts oben mit Blüten und Biene
    p.append(apfelzweig(226, 38, .96))
    for bx, by, r in ((286, 52, 12), (326, 58, 40), (374, 71, 0)):
        p.append(apfelbluete(bx, by, .6, r))
    p.append(biene_dir(326, 36, 1.0, 14))
    # Honigglas und Wabe
    p += [honigglas(104, 244, 1.75), wabenstueck(198, 252, 1.0)]
    # Kerzen
    p += [kerze(272, 244, 90, 1.0), kerze(304, 244, 64, 1.0, spirale=True)]
    # Apfel auf dem Tisch
    p.append(apfel(404, 252, 1.0))
    p += [chip(106, 276, "Honig", 14), chip(290, 276, "Wachs", 14), chip(408, 276, "Bestäubung", 14)]
    return bild("Schaubild: Honigglas, Bienenwachskerzen und ein Apfelzweig mit Blüten, Äpfeln und einer Biene", *p, grund="#fdf1cf")


# ═══════════════════════════════════════════════════════════════════════════
def nutztier_4():
    p = [sonne(430, 40, 15), wolke(70, 44, .7), wolke(290, 30, .5),
         huegel(140, "#c2e29e", "#9fcc72", amp=9, phase=.4), ferne_baeume([20, 56, 410, 452], 156, .6, "#6fa956"),
         huegel(172, "#a9d97c", "#6fa845", amp=8, phase=2.0)]
    # offener Bienenkasten rechts mit Rauchgerät
    p += [bienenkasten(386, 232, 1.0, "#8fc3ea", zargen=2, deckel_ab=True), rauchgeraet(450, 244, .8)]
    # Imker mit Rähmchen
    ix, iy, sc = 178, 254, 1.95
    p.append(imker(ix, iy, sc, haende=((-40, -62), (40, -62))))
    rahmen = raehmchen(0, -66, 66, 44, 1.0)
    bienen = "".join(biene_auf_wabe(bx, by, .3, r) for bx, by, r in [(-22, -50, 20), (-8, -38, -30), (10, -52, 60), (22, -40, 10), (-26, -32, 80), (0, -28, 0), (14, -30, -40), (-14, -56, 0)])
    p.append(f"<g transform='translate({ix} {iy}) scale({sc})'>{rahmen}{bienen}</g>")
    p.append(f"<g transform='translate({ix} {iy}) scale({sc})'>{handschuh(-40, -62, 1)}{handschuh(40, -62, 1)}</g>")
    # Bienen in der Luft
    p += [biene_dir(84, 110, .5, -8), biene_dir(284, 96, .5, 6, True), biene_dir(274, 164, .46, -12), biene_dir(96, 196, .46, 10, True), biene_dir(334, 140, .46, -6, True)]
    p.append(fussleiste(["Der Imker kontrolliert das Bienenvolk"], hoehe=30, size=13))
    return bild("Schaubild: Ein Imker zieht ein Rähmchen mit Wabe und Bienen aus dem offenen Bienenkasten, das Rauchgerät steht daneben", *p)


# ═══════════════════════════════════════════════════════════════════════════
def glossar_bienenkasten():
    p = [sonne(430, 40, 15), wolke(330, 46, .6), huegel(150, "#c2e29e", "#9fcc72", amp=8, phase=1.1), huegel(184, "#a9d97c", "#6fa845", amp=7, phase=2.6)]
    # Blumen
    for bx, by, f in ((40, 248, "#f06aa0"), (70, 256, "#fff"), (410, 252, "#b58cf0"), (440, 246, "#ff8a4a"), (380, 258, "#f6dc3a"), (20, 262, "#7fb7ff"), (458, 262, "#f06aa0")):
        p.append(blume_gross(bx, by, .7, f, stiel=24))
    p.append(bienenkasten(222, 250, 2.05, "#f2cf5e", zargen=2))
    p += [biene_dir(150, 214, .5, -10), biene_dir(168, 240, .46, 20), biene_dir(330, 196, .5, -8, True), biene_dir(372, 128, .5, 6, True), biene_dir(200, 270, .4, 8)]
    p.append(beschriftung(96, 60, "Bienenkasten", 176, 140, BLAU, size=14))
    p.append(beschriftung(352, 248, "Flugloch", 262, 224, MAGENTA, ueber=False, size=14))
    return bild("Glossarbild: Ein gelber Bienenkasten auf der Wiese mit Flugloch und Bienen", *p)


# ═══════════════════════════════════════════════════════════════════════════
#  Karte „Beim Imker“ (900 × 560)
# ═══════════════════════════════════════════════════════════════════════════
KW, KH = 900, 560


def _obj(name, inhalt):
    return f"<g id='o-{name}'>{inhalt}</g>"


# Antippbare Objekte: Name → (Anzeigename, Tippmitte x, y, Kategorie 0 = Lebewesen, 1 = kein Lebewesen)
KARTE_OBJEKTE = {
    "bienenkasten": ("Bienenkasten", 656, 372, 1),
    "imker": ("Imker", 298, 376, 0),
    "schleier": ("Schleier", 298, 304, 1),
    "rauchgeraet": ("Rauchgerät", 460, 474, 1),
    "honigglas": ("Honigglas", 842, 466, 1),
    "bluete": ("Blüten", 98, 492, 0),
    "obstbaum": ("Obstbaum", 102, 272, 0),
    "biene": ("Biene", 596, 164, 0),
    "sonne": ("Sonne", 800, 92, 1),
    "wolke": ("Wolke", 330, 84, 1),
}


# Dekorbienen der Karte: (x, y, Maßstab, Drehung, blickt nach links). Beweis dafür, dass die Biene draußen Futter holt:
# 1 sitzt an einer Blüte unten links, 1 an der Blüte des Apfelbaums, 1 fliegt von den Blüten zum Bienenkasten,
# 3 winzige fliegen am Flugloch ein und aus. Jede liegt ≥ 60 px von jeder Tippmitte (KARTE_OBJEKTE) entfernt.
DEKOR_BIENEN = [
    (36, 462, .42, 22, False),      # an der Blüte unten links
    (163, 288, .42, -10, True),     # an der Apfelblüte (rechter Kronenrand)
    (474, 280, .46, -8, False),     # fliegt zwischen den Blüten und dem Bienenkasten
    (574, 412, .30, -6, False),     # am Flugloch: kommt von links
    (640, 448, .30, -18, False),    # am Flugloch: unter dem Flugbrett
    (712, 444, .30, 12, True),      # am Flugloch: fliegt davon
]


def imker_karte():
    p = [huegel(250, "#bfe19a", "#9ccb6f", w=KW, h=KH, amp=16, phase=.5),
         huegel(300, "#a9d97c", "#74ad48", w=KW, h=KH, amp=12, phase=2.0),
         f"<path d='M0,360 Q{KW * .3},340 {KW * .55},352 T{KW},338 V{KH} H0 Z' fill='url(#gWiese)' opacity='.9'/>"]
    # Grasbüschel (nur Dekoration, ohne Blüten)
    for gx, gy, gs in ((30, 420, 1.6), (230, 540, 1.8), (420, 410, 1.5), (560, 540, 1.8), (770, 540, 1.7), (880, 420, 1.5), (360, 548, 1.5), (640, 470, 1.4), (200, 400, 1.3)):
        p.append(gras(gx, gy, gs))
    p.append(_obj("sonne", sonne(800, 92, 40)))
    p.append(_obj("wolke", wolke(330, 86, 1.9)))
    p.append(_obj("obstbaum", obstbaum(102, 372, 1.3, bluete=True, fruechte=True)))
    p.append(_obj("bienenkasten", bienenkasten(650, 430, 1.9, "#f2cf5e", zargen=2)))
    p.append(_obj("imker", imker(298, 500, 2.3)))
    p.append(_obj("rauchgeraet", rauchgeraet(462, 504, 1.5)))
    p.append(_obj("honigglas", honigglas(842, 520, 2.0)))
    bl = (blume_gross(48, 524, 1.6, "#f06aa0", stiel=34) + blume_gross(98, 540, 1.7, "#f6dc3a", stiel=34, mitte="#e0701a")
          + blume_gross(146, 522, 1.5, "#b58cf0", stiel=34))
    p.append(_obj("bluete", bl))
    p.append(_obj("biene", biene_dir(600, 166, 2.2, -8)))
    # Dekorbienen (klein, keine Tippziele; außerhalb der Objekt-Gruppen, ≥ 60 px von jeder Tippmitte, siehe DEKOR_BIENEN)
    p.append(flugspur("M398,300 C424,282 452,284 474,282 C500,282 530,292 556,296", opa=.8))
    for bx, by, sc, rot, links in DEKOR_BIENEN:
        p.append(biene_dir(bx, by, sc, rot, links))
    return bild("Karte: Beim Imker – Bienenkasten, Imker mit Hut und Schleier, Rauchgerät, Honigglas, Blüten, Obstbaum, Biene, Sonne und Wolke",
                *p, w=KW, h=KH)


def messe_objekte():
    """Rahmen der Karten-Objekte (Pixel) aus dem Browser; leer, wenn Edge fehlt."""
    try:
        from grafik_textpruefung import pruefe
        return pruefe("imker-karte").get("objekte", {})
    except Exception:
        return {}


def schreibe_punkte(bboxen=None):
    """Schreibt werkzeuge/imker_karte_punkte.json: je Objekt Anzeigename, Mittelpunkt (x, y in Pixeln der 900 × 560-Karte),
    `kat` (0 = Lebewesen, 1 = kein Lebewesen) und – wenn gemessen – den Rahmen `bbox` [x0, y0, x1, y1].
    Der Schleier ist Teil des Imkers: sein Rahmen liegt innerhalb des Imker-Rahmens."""
    import re
    bboxen = dict(bboxen or {})
    if bboxen:
        bboxen.setdefault("schleier", [236, 247, 360, 344])        # Hut mit Schleier: 2,3 × (−27 … 27, −110 … −68) um (298, 500)
    daten = {}
    for key, (name, x, y, kat) in KARTE_OBJEKTE.items():
        eintrag = {"name": name, "x": x, "y": y, "kat": kat}
        if key in bboxen:
            eintrag["bbox"] = bboxen[key]
        daten[key] = eintrag
    text = json.dumps(daten, ensure_ascii=False, indent=2)
    text = re.sub(r"\[\s+(-?\d+),\s+(-?\d+),\s+(-?\d+),\s+(-?\d+)\s+\]", r"[\1, \2, \3, \4]", text)
    with open(os.path.join(HIER, "imker_karte_punkte.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")


# ═══════════════════════════════════════════════════════════════════════════
#  Freigestellte Tierporträts für die Vergleichstabelle (Aufgabe 43): 240 × 180, transparent, kein Text
# ═══════════════════════════════════════════════════════════════════════════
def _portraet(titel, *teile):
    return bild(titel, *teile, w=240, h=180, grund="none", rahmen=False)


def tier_kuh():
    s = 1.13
    return _portraet("Porträt: schwarz-weiße Kuh mit Hörnern, Ohren und Euter, Blick nach rechts", kuh(120 - 23 * s, 156, s))


def tier_huhn():
    s = 2.4
    return _portraet("Porträt: braunrotes Huhn mit rotem Kamm und gelbem Schnabel, Blick nach rechts", huhn(124, 166, s))


def tier_schaf():
    s = 1.9
    return _portraet("Porträt: Schaf mit weißem Wollfell und dunklem Kopf, Blick nach rechts",
                     schaf(120 - 3.5 * s, 154, s, kontur="#8f8872", kontur_w=1.5))


def tier_biene():
    s = .52
    with dichte(.6):
        b = biene_seite(fluegel_an=True, beine_an=True, stachel=True)
    return _portraet("Porträt: Honigbiene von der Seite mit Streifen, vier Flügeln, sechs Beinen und Fühlern, Blick nach rechts",
                     platz(b, 120 + 22 * s, 92 - 8 * s, s, -8))


TIERE = ["tier-kuh", "tier-huhn", "tier-schaf", "tier-biene"]


def schreibe_tiere_vorschau():
    """Kontrollseite werkzeuge/ausgabe/tiere_vorschau.html: die vier Tierporträts nebeneinander bei 90 px und 180 px Höhe
    (auf weißem und auf farbigem Grund, damit die Transparenz sichtbar wird)."""
    ausgabe = os.path.join(HIER, "ausgabe")
    os.makedirs(ausgabe, exist_ok=True)

    def zeile(hoehe, grund):
        bilder = "".join(f"<figure><img src='../../static/img/lese/{n}.svg' height='{hoehe}' alt='{n}'><figcaption>{n}</figcaption></figure>" for n in TIERE)
        return f"<div class='z' style='background:{grund}'>{bilder}</div>"

    seite = ("<!doctype html><html lang='de'><meta charset='utf-8'><title>Tierporträts – Vorschau</title>"
             "<style>body{font-family:Lato,Arial,sans-serif;margin:16px;background:#f0f4f8;color:#1e293b}h1{font-size:1.1rem}h2{font-size:.95rem;margin:14px 0 4px}"
             ".z{display:flex;gap:14px;padding:10px;border-radius:10px;align-items:flex-end;flex-wrap:wrap}figure{margin:0;text-align:center}"
             "figcaption{font-size:.7rem;color:#64748b}img{display:block;margin:0 auto}</style>"
             "<h1>Tierporträts für die Vergleichstabelle (Aufgabe 43)</h1>"
             "<h2>90 px Höhe (Spaltenkopf), weißer Grund</h2>" + zeile(90, "#ffffff")
             + "<h2>90 px Höhe, farbiger Grund</h2>" + zeile(90, "#dbeafe")
             + "<h2>180 px Höhe, weißer Grund</h2>" + zeile(180, "#ffffff")
             + "<h2>180 px Höhe, farbiger Grund</h2>" + zeile(180, "#fef3c7") + "</html>")
    with open(os.path.join(ausgabe, "tiere_vorschau.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(seite)


GRAFIKEN = {"nutztier-1": nutztier_1, "nutztier-2": nutztier_2, "nutztier-3": nutztier_3, "nutztier-4": nutztier_4,
            "glossar-bienenkasten": glossar_bienenkasten, "imker-karte": imker_karte,
            "tier-kuh": tier_kuh, "tier-huhn": tier_huhn, "tier-schaf": tier_schaf, "tier-biene": tier_biene}

if __name__ == "__main__":
    erzeuge(GRAFIKEN)
    schreibe_punkte(messe_objekte())
    schreibe_tiere_vorschau()
