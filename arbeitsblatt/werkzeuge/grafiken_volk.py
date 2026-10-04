"""Schaubilder des Reiters „Das Bienenvolk“ (Lesestrecke L3, Glossar, Karte „Bienenstock beschriften“).

Aufruf:  python werkzeuge/grafiken_volk.py
Ausgabe: static/img/lese/  volk-1 … volk-4, stock-karte, glossar-koenigin, glossar-drohne, glossar-wabe,
         glossar-schwaenzeltanz, glossar-wintertraube  – und werkzeuge/stock_karte_punkte.json (Mittelpunkte der Karte).

Die Zeichenbausteine (Bienen von oben und von der Seite, Wabenzellen, Rähmchen, Bienenkasten) stehen in
volk_zeichnen.py und volk_szenen.py. Texte im Bild: nur kurze, feste Wörter (AB_KONZEPT.md).
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_szenen import *  # noqa: F401,F403
from volk_glossar import glossar_drohne, glossar_koenigin, glossar_wabe  # noqa: F401
from volk_arten import GRAFIKEN_ARTEN, schreibe_vorschau  # noqa: F401
from volk_nah import volk_4  # noqa: F401
from volk_raetsel import GRAFIKEN_RAETSEL  # noqa: F401
from volk_tanz import glossar_schwaenzeltanz, glossar_wintertraube  # noqa: F401
from volk_szenen import kasten, namensschild, rahmen, zeiger, zone_brut, zone_honig  # noqa: F401

PUNKTE_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stock_karte_punkte.json")
KW, KH = 900, 560


# ═══════════════════════════════════════════════════════════════════════════
#  Gemeinsame Szenenteile
# ═══════════════════════════════════════════════════════════════════════════
def _bl(x, y, s=1.0, farbe="#e879a6"):
    return blume(x, y, s, farbe)


def _wiese_deko(w, h, y0, s=1.0, seed=2):
    """Blumen und Gras am Boden (zufällig, aber fest)."""
    rnd = random.Random(seed)
    farben = ["#e879a6", "#f5c542", "#c08adf", "#ffffff", "#ff8a65"]
    out = ""
    for i in range(int(w / (46 * s))):
        x = rnd.uniform(10, w - 10)
        y = y0 + rnd.uniform(0, h - y0 - 8)
        out += gras(x, y, s * rnd.uniform(.8, 1.2)) if i % 3 else _bl(x, y, s * rnd.uniform(.9, 1.3), rnd.choice(farben))
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  stock-karte (900 × 560) und volk-3
# ═══════════════════════════════════════════════════════════════════════════
HX, HY = 140, 126          # linke obere Ecke des Honigraums in der Karte
FX, FY, FW, FH = 656, 290, 220, 214     # herausgezogenes Rähmchen (Außenmaß)
FSB, FOB, FUB = 38, 34, 28              # Balkenbreiten: Seiten, oben, unten (dick, damit das Holz ein großes Ziel ist)
DREH = -3                               # Neigung des Rähmchens in Grad (um die Mitte der Unterkante)


def _drehen(x, y, cx, cy, grad):
    a = math.radians(grad)
    dx, dy = x - cx, y - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


def stock_karte_punkte(a):
    """Mittelpunkte der sieben Ziele in Bildpixeln (900 × 560)."""
    cx, cy = FX + FW / 2, FY + FH
    p = {
        "Dach": (HX + a["dach"][0], HY + a["dach"][1]),
        "Honigraum": (HX + a["honigraum"][0], HY + a["honigraum"][1]),
        "Brutraum": (HX + a["brutraum"][0], HY + a["brutraum"][1]),
        "Boden": (HX + a["boden"][0], HY + a["boden"][1]),
        "Flugloch": (HX + a["flugloch"][0], HY + a["flugloch"][1]),
        "Rähmchen": _drehen(FX + FSB / 2, FY + FOB + (FH - FOB - FUB) / 2, cx, cy, DREH),
        "Wabe": _drehen(FX + FW / 2, FY + FOB + (FH - FOB - FUB) / 2, cx, cy, DREH),
    }
    return {k: (round(x), round(y)) for k, (x, y) in p.items()}


def _stock_karte_teile():
    kasten_svg, a = kasten(r=12)
    p = [himmel_wiese(486, h=KH, w=KW), sonne(822, 70, 34), wolke(104, 66, 1.15), wolke(742, 140, 1.0),
         f"<g transform='translate({HX} {HY})'>{kasten_svg}</g>"]
    # herausgezogenes Rähmchen mit Brutwabe (rechts)
    iw, ih = FW - 2 * FSB, FH - FOB - FUB
    bee = "".join(biene_o("A", FX + FSB + u * iw, FY + FOB + v * ih, rot, .58)
                  for u, v, rot in ((.2, .26, 30), (.82, .3, -70), (.22, .82, 160), (.8, .82, 100)))
    p.append(f"<g transform='rotate({DREH} {FX + FW / 2} {FY + FH})'>"
             f"<ellipse cx='{FX + FW / 2}' cy='{FY + FH + 4}' rx='{FW * .56:.0f}' ry='9' fill='#1b3a12' opacity='.3'/>"
             + rahmen(FX, FY, FW, FH, 14, zone_brut(31), ob=FOB, sb=FSB, ub=FUB, lug_l=20, lug_r=20, bienen=bee) + "</g>")
    p.append(_wiese_deko(KW, KH, 534, 1.1, 4))
    p.append(biene_s(600, 44, .6, True, 8) + biene_s(790, 196, .55, True, -12) + biene_s(52, 300, .6, False, -8))
    return p, a


def stock_karte():
    p, a = _stock_karte_teile()
    punkte = stock_karte_punkte(a)
    # Prüfung der Vorgaben: Abstand der Mittelpunkte >= 90 px (Punkte haben 48 px Durchmesser), Abstand zum Rand >= 40
    namen = list(punkte)
    for i, n1 in enumerate(namen):
        x, y = punkte[n1]
        assert 40 <= x <= KW - 40 and 40 <= y <= KH - 40, (n1, x, y)
        for n2 in namen[i + 1:]:
            d = math.dist(punkte[n1], punkte[n2])
            assert d >= 90, (n1, n2, round(d))
    with open(PUNKTE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"bild": "stock-karte", "breite": KW, "hoehe": KH,
                   "punkte": {k: {"x": x, "y": y} for k, (x, y) in punkte.items()}}, f, ensure_ascii=False, indent=2)
    return volk_svg("Bienenkasten im Querschnitt mit herausgezogenem Rähmchen", *p, w=KW, h=KH, bausteine="ASZ")



def volk_3():
    s, ox, oy = .5, 95, 62
    kasten_svg, a = kasten(r=12, eb=.8)

    def P(k, dx=0, dy=0):
        return ox + s * (a[k][0] + dx), oy + s * (a[k][1] + dy)
    p = [himmel_wiese(246, h=H, w=W), f"<g transform='translate({ox} {oy}) scale({s})'>{kasten_svg}</g>",
         _wiese_deko(W, H, 258, .55, 6), biene_s(52, 128, .42, False, -12), biene_s(30, 66, .36, False, 10)]
    x = 408
    p.append(zeiger("Dach", x, 44, *P("dach", 118, 16), size=13))
    p.append(zeiger("Honigraum", x, 104, *P("honigraum", 6), size=13))
    p.append(zeiger("Brutraum", x, 172, *P("brutraum", 6), size=13))
    p.append(zeiger("Boden", x, 238, *P("boden", 70), size=13))
    p.append(zeiger("Flugloch", 54, 188, *P("flugloch", -20, -18), size=13))
    p.append(zeiger("Rähmchen", 50, 92, ox + s * 90, oy + s * 19, size=13))
    return volk_svg("Querschnitt durch einen Bienenkasten: Dach, Honigraum oben, Brutraum unten, Boden, Flugloch, Bienen am Eingang",
                    *p, bausteine="ASZ")


# ═══════════════════════════════════════════════════════════════════════════
#  volk-1: wimmelnde Wabe
# ═══════════════════════════════════════════════════════════════════════════
def _verteilen(rnd, n, w, h, abstand, rand=-6, schon=(), versuche=3000):
    """Zufallspunkte mit Mindestabstand (Poisson-Scheibe light)."""
    pts = list(schon)
    neu = []
    for _ in range(versuche):
        x, y = rnd.uniform(rand, w - rand), rnd.uniform(rand, h - rand)
        if all((x - a) ** 2 + (y - b) ** 2 >= abstand ** 2 for a, b in pts):
            pts.append((x, y))
            neu.append((x, y))
            if len(neu) >= n:
                break
    return neu


def volk_1():
    rnd = random.Random(11)
    r = 10
    wb = Wabe(-2, -4, r)
    # Zellen: oben Honig (Deckel), Mitte Brut, dazwischen Pollen – die Bienen verdecken das meiste
    zellen = []
    for z in range(0, 20):
        for c in range(0, 29):
            x, y = wb.pos(c, z)
            u, v = x / W, y / H
            k = rnd.random()
            art = None
            if v < .26:
                art = "D" if k < .7 else "H"
            elif v < .38:
                art = "P" if k < .45 else ("H" if k < .7 else None)
            elif ((u - .5) / .52) ** 2 + ((v - .68) / .36) ** 2 < 1:
                art = "B" if k < .78 else None
            elif k < .35:
                art = "D" if k < .2 else "H"
            if art:
                zellen.append(wb.lokal(art, c, z))
    # Bienen: Hofstaat um die Königin, zwei Drohnen, der Rest Arbeiterinnen
    kx, ky = 318, 156
    teile = [f"<rect width='{W}' height='{H}' fill='url(#pW)'/>", wb.gruppe(zellen),
             f"<rect width='{W}' height='{H}' fill='url(#gVig)'/>"]
    bienen = []
    hof = []
    for i, ang in enumerate((-60, -10, 40, 100, 150, 205, 255)):
        a = math.radians(ang)
        hx, hy = kx + math.sin(a) * 50, ky - math.cos(a) * 50
        hof.append((hx, hy))
        bienen.append((hy, biene_o("A", hx, hy, ang + 180 + rnd.uniform(-8, 8), .4)))
    festes = [(kx, ky)] + hof + [(105, 78), (392, 232)]
    for x, y in _verteilen(rnd, 52, W, H, 27, schon=festes):
        bienen.append((y, biene_o("A", x, y, rnd.uniform(0, 360), rnd.uniform(.38, .46))))
    bienen.append((78, biene_o("D", 105, 78, 38, .44)))
    bienen.append((232, biene_o("D", 392, 232, -50, .44)))
    teile += [b for _, b in sorted(bienen, key=lambda t_: t_[0])]
    teile.append(biene_o("K", kx, ky, -24, .54))        # Königin zuletzt: gut sichtbar
    return volk_svg("Wimmelnde Wabe: viele Bienen auf Wabenzellen, dazwischen eine Königin mit Hofstaat und zwei Drohnen", *teile, bausteine="AKDZ",
                    extra=muster_wabe("pW", r, -2, -4) + "<radialGradient id='gVig' cx='.5' cy='.5' r='.75'><stop offset='.55' stop-color='#2a1608' stop-opacity='0'/>"
                          "<stop offset='1' stop-color='#2a1608' stop-opacity='.6'/></radialGradient>",
                    grund="#8a5410")


# ═══════════════════════════════════════════════════════════════════════════
#  volk-2: Königin, Arbeiterin, Drohne
# ═══════════════════════════════════════════════════════════════════════════
def volk_2():
    S, y0 = 1.1, 96
    xk, xa, xd = 92, 238, 388
    hint = ("<rect width='480' height='288' fill='url(#pW2)'/><rect width='480' height='288' fill='#fff8e2' opacity='.72'/>"
            "<rect width='480' height='288' fill='url(#gGlanz)'/>")
    p = [hint,
         biene_o("K", xk, y0, 0, S), biene_o("A", xa, y0, 0, S), biene_o("D", xd, y0 - 2, 0, S * 1.06)]
    p.append(zeiger("roter\nPunkt", 40, 46, xk - 3, y0 - 19 * S - 2, size=12))
    p.append(zeiger("langer\nHinterleib", 44, 168, xk - 12, y0 + 40 * S, size=12))
    p.append(zeiger("Stachel", xa, y0 + 66 * S + 30, xa, y0 + 60 * S + 4, size=12))
    p.append(zeiger("riesige\nAugen", 312, 40, xd - 11 * S * 1.06, y0 - 2 - 45 * S * 1.06, size=12))
    p.append(zeiger("kein\nStachel", 438, 196, xd + 6, y0 + 50 * S * 1.06, size=12))
    p.append(namensschild(xk, 232, "Königin", MAGENTA, 15))
    p.append(namensschild(xa, 232, "Arbeiterin", BLAU, 15))
    p.append(namensschild(xd, 232, "Drohne", "#b06a00", 15))
    return volk_svg("Königin, Arbeiterin und Drohne nebeneinander: Die Königin hat einen langen Hinterleib und einen roten Punkt, "
                    "die Arbeiterin einen Stachel, die Drohne riesige Augen und keinen Stachel", *p, bausteine="AKDZ",
                    extra=muster_wabe("pW2", 14, 0, 0) + "<radialGradient id='gGlanz' cx='.5' cy='.45' r='.7'><stop offset='.5' stop-color='#fff' stop-opacity='.55'/>"
                          "<stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>", grund="#fff3cf")


GRAFIKEN = {
    "volk-1": volk_1, "volk-2": volk_2, "volk-3": volk_3, "volk-4": volk_4, "stock-karte": stock_karte,
    "glossar-koenigin": glossar_koenigin, "glossar-drohne": glossar_drohne, "glossar-wabe": glossar_wabe,
    "glossar-schwaenzeltanz": glossar_schwaenzeltanz, "glossar-wintertraube": glossar_wintertraube,
}
GRAFIKEN.update(GRAFIKEN_RAETSEL)   # tanzraetsel-1 … 3 (+ tanzraetsel_ziele.json)
GRAFIKEN.update(GRAFIKEN_ARTEN)     # bienenart-koenigin / -arbeiterin / -drohne (240 × 180, transparent)

if __name__ == "__main__":
    erzeuge(GRAFIKEN)
    schreibe_vorschau()          # werkzeuge/ausgabe/bienenarten_vorschau.html
