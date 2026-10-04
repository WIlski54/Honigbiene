"""Schaubilder des Reiters „Die Biene“ (Lesestrecke L2) und seiner Glossarbilder.

Aufruf:  python werkzeuge/grafiken_koerper.py
Ausgabe: static/img/lese/koerper-1.svg … koerper-5.svg, glossar-facettenauge.svg, glossar-honigmagen.svg,
         glossar-pollenkoerbchen.svg, glossar-stachel.svg   (viewBox 480 × 288)

Biologie (Regeln): 3 Körperteile, 6 Beine, 4 Flügel (vorn/hinten), 2 Fühler, 2 Facettenaugen + 3 Punktaugen.
"""
import random
from bienen_zeichnen import *  # noqa: F401,F403
from bienen_kopf import kopf_vorn
from bienen_innen import biene_oben, brust_schnitt, lupe
from bienen_situs import situs_hinterleib
from bienen_bein import hinterbein_gross, MARKEN
from koerper_glossar import glossar_facettenauge, glossar_honigmagen, glossar_pollenkoerbchen, glossar_stachel

ROT_K, BLAU_K, GRUEN_K, MAG_K = "#d6336c", "#006AB3", "#12894a", "#AD007C"


def koerper_1():
    tint = {"kopf": BLAU_K, "brust": MAG_K, "hinterleib": GRUEN_K}
    bee = biene_seite(tint=tint, ruessel="kurz")
    teile = [hintergrund_blueten(),
             "<ellipse cx='235' cy='250' rx='170' ry='8' fill='#000' opacity='.12'/>",
             platz(bee, 262, 140, 1.0),
             beschriftung(392, 70, "Kopf", 352, 112, BLAU_K, size=15),
             beschriftung(298, 56, "Brust", 284, 98, MAG_K, size=15),
             beschriftung(104, 214, "Hinterleib", 126, 178, GRUEN_K, ueber=False, size=15),
             klammer_unten(250, 355, 246, TEXT), t(302, 270, "6 Beine", 13, 800, TEXT)]
    return bild("Schaubild: Biene von der Seite, Kopf, Brust und Hinterleib farbig abgesetzt", *teile)


def koerper_2():
    kopf = platz(kopf_vorn(), 240, 114, .74)
    teile = [hintergrund_blueten(), kopf,
             beschriftung(410, 46, "Fühler", 358, 78, GRUEN_K, size=14),
             beschriftung(116, 152, "Facettenauge", 180, 126, BLAU_K, size=14, anker="end"),
             beschriftung(240, 38, "Punktaugen", 240, 72, MAG_K, size=14, ueber=True),
             beschriftung(380, 220, "Rüssel", 249, 208, ROT_K, size=14, anker="start")]
    return bild("Schaubild: Kopf der Biene von vorn mit Fühlern, Facettenaugen, Punktaugen und Rüssel", *teile)


def koerper_3():
    bx, by, bs = 148, 140, .84
    lx, ly, lr = 378, 124, 78
    (a1, a2), (b1, b2) = tangenten((bx, by), 36 * bs + 6, (lx, ly), lr)
    kegel = (f"<polygon points='{a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {b1[0]:.1f},{b1[1]:.1f}' fill='#fff' opacity='.55'/>"
             f"<line x1='{a1[0]:.1f}' y1='{a1[1]:.1f}' x2='{a2[0]:.1f}' y2='{a2[1]:.1f}' stroke='#14304a' stroke-width='1.3' stroke-dasharray='5 4' opacity='.6'/>"
             f"<line x1='{b1[0]:.1f}' y1='{b1[1]:.1f}' x2='{b2[0]:.1f}' y2='{b2[1]:.1f}' stroke='#14304a' stroke-width='1.3' stroke-dasharray='5 4' opacity='.6'/>"
             f"<circle cx='{bx}' cy='{by}' r='{36 * bs + 6:.1f}' fill='none' stroke='#14304a' stroke-width='1.6' stroke-dasharray='5 4' opacity='.7'/>")
    lp = lupe(lx, ly, lr, platz(brust_schnitt(), lx, ly + 2, .88))
    teile = [hintergrund_blueten(), kegel,
             "<ellipse cx='140' cy='250' rx='120' ry='6' fill='#000' opacity='.1'/>",
             platz(biene_oben(), bx, by, bs), lp,
             beschriftung(66, 100, "Vorderflügel", 80, 140, BLAU_K, size=13),
             beschriftung(14, 214, "Hinterflügel", 90, 184, MAG_K, ueber=False, size=13, anker="start"),
             beschriftung(246, 246, "Beine", 214, 222, GRUEN_K, ueber=False, size=13),
             beschriftung(392, 206, "Flugmuskeln", 384, 128, ROT_K, ueber=False, size=14),
             t(378, 36, "Brust aufgeschnitten", 12, 700, GRAU)]
    return bild("Schaubild: Brust der Biene von oben mit vier Flügeln und sechs Beinen, daneben die Flugmuskeln im Schnitt", *teile)


def koerper_4():
    s = 1.66
    tx, ty = 372, 128
    hl = f"<g transform='translate({tx + 36 * s:.1f} {ty}) scale({s})'>{situs_hinterleib()}</g>"
    teile = [hintergrund_blueten(), "<ellipse cx='235' cy='222' rx='190' ry='6' fill='#000' opacity='.1'/>", hl,
             beschriftung(336, 52, "Honigmagen", 296, 118, "#c2185b", size=14),
             beschriftung(142, 52, "Darm", 150, 112, "#4d7c0f", size=14),
             beschriftung(218, 40, "Herz", 232, 70, "#b3261e", size=14),
             beschriftung(236, 240, "Wachsdrüsen", 232, 198, BLAU_K, ueber=False, size=14),
             beschriftung(52, 240, "Stachel", 66, 172, MAG_K, ueber=False, size=14),
             beschriftung(134, 240, "Giftblase", 128, 180, "#0b7285", ueber=False, size=14)]
    return bild("Schaubild: Hinterleib der Biene aufgeschnitten mit Honigmagen, Darm, Wachsdrüsen, Giftblase und Stachel", *teile)


def _abb(x, y, hx, hy, rot, s):
    """Lokalen Punkt (x, y) des Beins in Bildkoordinaten umrechnen (Verschiebung hx,hy; Drehung rot Grad; Maßstab s)."""
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return hx + s * (x * c - y * sn), hy + s * (x * sn + y * c)


def koerper_5():
    hx, hy, rot, s = 30, 64, 5, 1.08
    # Körper am linken Rand (angeschnitten): Hinterleib hinten, Brust vorn
    hinten = platz(abdomen(), -8, 40, 1.45)
    thorax = platz(brust_pelz(), -30, 56, 1.5)
    leg = platz(hinterbein_gross(), hx, hy, s, rot)
    z_h = _abb(*MARKEN["hoeschen"], hx, hy, rot, s)
    z_k = _abb(*MARKEN["koerbchen"], hx, hy, rot, s)
    z_b = _abb(*MARKEN["buerste"], hx, hy, rot, s)
    z_f = _abb(*MARKEN["femur"], hx, hy, rot, s)
    teile = [hintergrund_blueten(), pollenstaub(), hinten, leg, thorax,
             beschriftung(z_f[0] + 56, 30, "Haare", z_f[0] + 4, z_f[1] - 12, GRAU, size=14, lfill="#475569"),
             beschriftung(z_b[0] + 40, 242, "Bürste", z_b[0] + 4, z_b[1] + 8, GRUEN_K, ueber=False, size=14),
             beschriftung(z_h[0] + 20, 36, "Pollenhöschen", z_h[0] + 4, z_h[1] - 14, "#b45309", size=14),
             beschriftung(z_k[0] - 40, 226, "Pollenkörbchen", z_k[0] - 4, z_k[1] + 12, MAG_K, ueber=False, size=14)]
    return bild("Schaubild: Hinterbein der Biene mit Pollenkörbchen, gelbem Pollenhöschen, Haaren und Bürste", *teile)


GRAFIKEN = {"koerper-1": koerper_1, "koerper-2": koerper_2, "koerper-3": koerper_3, "koerper-4": koerper_4, "koerper-5": koerper_5,
            "glossar-facettenauge": glossar_facettenauge, "glossar-honigmagen": glossar_honigmagen,
            "glossar-pollenkoerbchen": glossar_pollenkoerbchen, "glossar-stachel": glossar_stachel}

if __name__ == "__main__":
    erzeuge(GRAFIKEN)
