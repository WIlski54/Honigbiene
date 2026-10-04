"""Tanzrätsel (Aufgabentyp `bildwahl`, docs/FORSCHEN.md): drei Karten 900 × 560 mit Trefferkreisen.

Links der Tanz auf der senkrechten Wabe (Schwänzellauf mit wackelnder Biene, gestrichelte Senkrechte, Winkelbogen,
kleine Sonne oben = „oben auf der Wabe heißt Richtung Sonne“), rechts die Wiese von oben mit Bienenkasten, Sonne und
drei Blumenfeldern A, B, C. Genau ein Feld passt zum Tanz:

  Runde 1  Lauf senkrecht nach oben (0°), mittellang      -> Feld in Richtung Sonne (B); die anderen zwei liegen woanders
  Runde 2  Lauf nach rechts (90°), mittellang             -> Feld 90° rechts von der Sonne (C); Gegenspieler: links (Spiegelbild), halb rechts oben
  Runde 3  Lauf schräg rechts (50°), SEHR lang            -> ferne Wiese in 50° (A); gleiche Richtung nah (B); ferne Wiese in anderer Richtung (C)

Nichts verrät das Richtige außer dem Tanz: alle Felder sehen gleich aus (gleiche Größe, gleiche Blumenfarben, gleiche
Plakette), das richtige Feld hat jede Runde einen anderen Buchstaben und liegt jede Runde woanders.
Beschriftungen im Bild: nur „A“, „B“, „C“, „Sonne“, „Stock“.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_szenen import *  # noqa: F401,F403
from volk_tanz import _gestrichelt, _winkelbogen  # noqa: F401

ZIELE_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tanzraetsel_ziele.json")
KW, KH = 900, 560
RTREFF = 60                     # Radius der Trefferkreise (Bildpixel)
M_ZIEL = 40                     # Mindestabstand zwischen den Kreisen (Rand zu Rand)
M_RAND = 24                     # Mindestabstand der Kreise zum Bildrand

# Runde -> Tanz (Winkel zur Senkrechten, Länge des Laufs in px), Standort Bienenkasten, Felder (Buchstabe, Richtung, Entfernung, passt?)
RUNDEN = {
    1: dict(alpha=0, laenge=190, start=(200, 452), kasten=(650, 330),
            felder=[("A", -70, 175, False), ("B", 0, 165, True), ("C", 130, 165, False)],
            info="Lauf senkrecht nach oben, mittellang: Das Futter liegt in Richtung der Sonne (Feld B). A und C liegen woanders.",
            hinweis="Oben auf der Wabe heißt: in Richtung Sonne.",
            erklaerung="Der Schwänzellauf zeigt senkrecht nach oben. Das heißt: Das Futter liegt in Richtung Sonne."),
    2: dict(alpha=90, laenge=190, start=(96, 336), kasten=(650, 300),
            felder=[("A", -90, 165, False), ("B", 30, 170, False), ("C", 90, 160, True)],
            info="Lauf waagerecht nach rechts (90° zur Senkrechten), mittellang: Futter 90° rechts von der Sonne (Feld C). A ist das Spiegelbild (links), B liegt nur halb rechts oben.",
            hinweis="Vergleiche den Winkel zur Senkrechten mit dem Winkel zur Sonne. Achte auf links und rechts.",
            erklaerung="Der Schwänzellauf zeigt im rechten Winkel nach rechts. Das Futter liegt im gleichen Winkel rechts von der Sonne."),
    3: dict(alpha=50, laenge=330, start=(84, 480), kasten=(505, 468),
            felder=[("A", 50, 300, True), ("B", 50, 125, False), ("C", 85, 290, False)],
            info="Lauf schräg nach rechts oben (50°), sehr lang: ferne Wiese in 50° (Feld A). B liegt in derselben Richtung, aber nah (Lauf zu lang). C ist genauso weit weg, aber in anderer Richtung.",
            hinweis="Zwei Dinge zählen: die Richtung und die Länge des Schwänzellaufs.",
            erklaerung="Der Schwänzellauf geht schräg nach rechts oben und ist lang. Das Futter liegt in dieser Richtung und weit weg."),
}

ZUSATZ = ("<linearGradient id='gTDunkel' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a1608' stop-opacity='.58'/><stop offset='1' stop-color='#2a1608' stop-opacity='.38'/></linearGradient>"
          "<radialGradient id='gTVig' cx='.5' cy='.5' r='.75'><stop offset='.55' stop-color='#1a0d04' stop-opacity='0'/><stop offset='1' stop-color='#1a0d04' stop-opacity='.55'/></radialGradient>")


def feld_mitte(kasten, theta, d):
    """Mittelpunkt eines Feldes: Richtung theta (Grad im Uhrzeigersinn von oben = Sonne), Entfernung d."""
    a = math.radians(theta)
    return kasten[0] + d * math.sin(a), kasten[1] - d * math.cos(a)


def ziele(nr):
    r = RUNDEN[nr]
    out = []
    for bst, th, d, ok in r["felder"]:
        x, y = feld_mitte(r["kasten"], th, d)
        out.append({"id": bst, "x": round(x), "y": round(y), "r": RTREFF, "ok": ok})
    return out


def pruefen():
    """Vorgaben: r >= 55, Abstand Rand zu Rand >= 40, Abstand zum Bildrand >= 24, genau ein richtiges Feld je Runde."""
    for nr in RUNDEN:
        z = ziele(nr)
        assert sum(1 for t_ in z if t_["ok"]) == 1, nr
        for i, a in enumerate(z):
            assert a["r"] >= 55
            assert a["x"] - a["r"] >= M_RAND and a["y"] - a["r"] >= M_RAND, (nr, a)
            assert a["x"] + a["r"] <= KW - M_RAND and a["y"] + a["r"] <= KH - M_RAND, (nr, a)
            for b in z[i + 1:]:
                assert math.dist((a["x"], a["y"]), (b["x"], b["y"])) - a["r"] - b["r"] >= M_ZIEL, (nr, a["id"], b["id"])


def schreibe_ziele():
    pruefen()
    daten = {
        "breite": KW, "hoehe": KH,
        "bilder": [f"/static/img/lese/tanzraetsel-{n}.svg" for n in RUNDEN],
        "runden": [ziele(n) for n in RUNDEN],
        "info": [{"runde": n, "richtig": next(f[0] for f in RUNDEN[n]["felder"] if f[3]), "tanz_winkel_grad": RUNDEN[n]["alpha"],
                  "tanz_laenge_px": RUNDEN[n]["laenge"], "beschreibung": RUNDEN[n]["info"], "hinweis": RUNDEN[n]["hinweis"],
                  "erklaerung": RUNDEN[n]["erklaerung"]} for n in RUNDEN],
    }
    with open(ZIELE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
FARBEN = ["#e879a6", "#f5c542", "#ffffff", "#c08adf", "#ff8a65"]


def _bluete_def(i, farbe):
    """Blüte von oben (fünf Blütenblätter, gelbe Mitte), Radius 10, als Baustein `bl<i>`."""
    out = ""
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        mx, my = math.cos(a) * 6.2, math.sin(a) * 6.2
        out += (f"<ellipse cx='{mx:.1f}' cy='{my:.1f}' rx='5.2' ry='3.6' fill='{farbe}' stroke='#00000026' stroke-width='.6' "
                f"transform='rotate({math.degrees(a):.0f} {mx:.1f} {my:.1f})'/>")
    return f"<g id='bl{i}'>{out}<circle r='3.6' fill='#ffd530' stroke='#b88a10' stroke-width='.6'/></g>"


_KREISE = [(0, 0, 52)] + [(math.cos(k * math.pi / 3 + .5) * 32, math.sin(k * math.pi / 3 + .5) * 32, 27) for k in range(6)]
FELD_DEFS = ("<g id='fblob'>" + "".join(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{rr + 3}' fill='#3f8a2c'/>" for cx, cy, rr in _KREISE)
             + "".join(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{rr}' fill='#8fd35f'/>" for cx, cy, rr in _KREISE)
             + "<circle r='40' fill='#9bdc68' opacity='.6'/></g>"
             + "".join(_bluete_def(i, f) for i, f in enumerate(FARBEN)))


def blumenfeld(x, y, bst, seed):
    """Wiesenfleck mit Blüten und Plakette. Alle Felder haben dieselbe Form, Größe, Blumenfarben und Plakette."""
    rnd = random.Random(seed)
    out = f"<use href='#fblob' x='{x:.1f}' y='{y:.1f}'/>"
    for i in range(11):
        a = (i * 360 / 11 + rnd.uniform(-12, 12)) * math.pi / 180
        rad = rnd.uniform(33, 45)
        out += f"<use href='#bl{i % 5}' transform='translate({x + math.cos(a) * rad:.1f} {y + math.sin(a) * rad:.1f}) scale({rnd.uniform(.75, .95):.2f})'/>"
    out += (f"<circle cx='{x:.1f}' cy='{y:.1f}' r='21' fill='#fff' stroke='{DUNKEL}' stroke-width='3.4' filter='url(#fSchatten)'/>"
            f"<text x='{x:.1f}' y='{y + 9:.1f}' font-size='27' font-weight='800' fill='{DUNKEL}' text-anchor='middle'>{bst}</text>")
    return out


def kasten_oben(x, y):
    """Bienenkasten von oben (Satteldach: zwei Dachhälften, First)."""
    return (f"<g filter='url(#fSchatten)'><rect x='{x - 36}' y='{y - 28}' width='72' height='56' rx='5' fill='#b5503f' stroke='#6e2a1f' stroke-width='2'/>"
            f"<rect x='{x - 34}' y='{y - 26}' width='33' height='52' rx='3' fill='url(#gkDach)'/>"
            f"<rect x='{x + 1}' y='{y - 26}' width='33' height='52' rx='3' fill='#c35644'/>"
            f"<path d='M{x},{y - 26} V{y + 26}' stroke='#7a2f22' stroke-width='2.4'/>"
            f"<path d='M{x - 30},{y - 14} H{x - 6} M{x - 30},{y} H{x - 6} M{x - 30},{y + 14} H{x - 6} M{x + 6},{y - 14} H{x + 30} M{x + 6},{y} H{x + 30} M{x + 6},{y + 14} H{x + 30}' "
            f"stroke='#7a2f22' stroke-opacity='.3' stroke-width='1.6'/></g>")


def _rot(dx, dy):
    return math.degrees(math.atan2(dx, -dy))


def karte(nr):
    r = RUNDEN[nr]
    al = math.radians(r["alpha"])
    u = (math.sin(al), -math.cos(al))              # Richtung des Laufs (0° = senkrecht nach oben)
    n = (math.cos(al), math.sin(al))               # rechts davon
    sx, sy = r["start"]
    L = r["laenge"]
    ex, ey = sx + u[0] * L, sy + u[1] * L

    # ---- links: senkrechte Wabe im dunklen Stock
    px0, py0, pw, ph = 12, 12, 388, 536
    links = [f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='18' fill='#8a5410' stroke='#a8743c' stroke-width='8'/>",
             f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='18' fill='url(#pTR)'/>",
             f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='18' fill='url(#gTDunkel)'/>",
             f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='18' fill='url(#gTVig)'/>"]
    # Senkrechte (gestrichelt) mit kleiner Sonne oben
    links.append(_gestrichelt(sx, 92, sx, 526, "#fff", 3, "9 7"))
    links.append(sonne(sx, 54, 15, True))
    # Zuschauerinnen (Köpfe zum Lauf)
    seiten = [(.2, 1), (.5, 1), (.8, -1)]
    zuschau = ""
    for f, s_ in seiten:
        qx, qy = sx + u[0] * L * f + n[0] * s_ * 78, sy + u[1] * L * f + n[1] * s_ * 78
        zuschau += biene_o("A", qx, qy, _rot(-n[0] * s_, -n[1] * s_), .62)
    # Schwänzellauf: Zickzack von S bis fast zur Tänzerin, Pfeilspitze nicht nötig (die Tänzerin zeigt die Richtung)
    dancer = (ex - u[0] * 24, ey - u[1] * 24)
    ende = (dancer[0] - u[0] * 40, dancer[1] - u[1] * 40)
    lauf_len = math.dist((sx, sy), ende)
    N = max(10, int(lauf_len / 3))
    pts = []
    for i in range(N + 1):
        t_ = i / N
        amp = 5.4 * math.sin(2 * math.pi * t_ * lauf_len / 13)
        pts.append((sx + (ende[0] - sx) * t_ + n[0] * amp, sy + (ende[1] - sy) * t_ + n[1] * amp))
    zz = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    lauf = (f"<path d='{zz}' fill='none' stroke='#fff' stroke-width='9' stroke-linecap='round' stroke-linejoin='round' opacity='.85'/>"
            f"<path d='{zz}' fill='none' stroke='{ROT}' stroke-width='4.4' stroke-linecap='round' stroke-linejoin='round'/>")
    arc = _winkelbogen(sx, sy, 90, r["alpha"], MAGENTA, 4) if r["alpha"] else ""
    tanz = biene_o("A", dancer[0], dancer[1], r["alpha"], .82)
    links += [lauf, zuschau, arc, tanz]

    # ---- rechts: Wiese von oben
    qx0, qy0, qw, qh = 412, 12, 476, 536
    hx, hy = r["kasten"]
    rnd = random.Random(40 + nr)
    wiese = [f"<rect x='{qx0}' y='{qy0}' width='{qw}' height='{qh}' rx='18' fill='url(#gWiese)' stroke='#5b8a3a' stroke-width='5'/>"]
    # Grasbüschel, nicht in der Nähe der Felder
    mitten = [feld_mitte(r["kasten"], th, d) for _, th, d, _ in r["felder"]] + [(hx, hy)]
    buescheln = 0
    for _ in range(200):
        gx, gy = rnd.uniform(qx0 + 24, qx0 + qw - 24), rnd.uniform(qy0 + 110, qy0 + qh - 24)
        if all(math.dist((gx, gy), m) > 92 for m in mitten) and abs(gx - hx) > 20:
            wiese.append(gras(gx, gy, rnd.uniform(.9, 1.3)))
            buescheln += 1
            if buescheln >= 14:
                break
    # Sonnenlinie vom Kasten nach oben, Sonne oben
    wiese.append(_gestrichelt(hx, hy - 36, hx, 96, "#f2a900", 3.4, "10 8"))
    wiese.append(sonne(hx, 56, 22, True))
    wiese.append(t(hx + 56, 62, "Sonne", 20, 800, TEXT, "start"))
    for k, (bst, th, d, ok) in enumerate(r["felder"]):
        x, y = feld_mitte(r["kasten"], th, d)
        wiese.append(blumenfeld(x, y, bst, 100 * nr + k * 7))
    wiese.append(kasten_oben(hx, hy))
    wiese.append(t(hx, hy + 52, "Stock", 18, 800, TEXT))
    titel = (f"Tanzrätsel, Runde {nr}: Links tanzt eine Biene auf der senkrechten Wabe im Stock. "
             f"Rechts liegen auf der Wiese um den Bienenkasten drei Blumenfelder A, B und C, dazu die Sonne als Richtungsmarke")
    extra = muster_wabe("pTR", 22, 12, 12) + ZUSATZ + FELD_DEFS
    return volk_svg(titel, *links, *wiese, w=KW, h=KH, bausteine="A", extra=extra)


def _mk(nr):
    def f():
        schreibe_ziele()
        return karte(nr)
    return f


GRAFIKEN_RAETSEL = {f"tanzraetsel-{n}": _mk(n) for n in RUNDEN}
