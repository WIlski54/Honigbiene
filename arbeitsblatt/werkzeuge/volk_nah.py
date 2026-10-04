"""Nahaufnahmen von Wabenzellen: volk-4 (Ei, Larve, Puppe, Pollen, Honig) und Bausteine für Glossarbilder.

Gebraucht werden die Verläufe `gaPuppe` und `gaPuppeAuge` (siehe EXTRA_NAH) – sie gehören in defs_extra des Bildes.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_szenen import *  # noqa: F401,F403
from volk_szenen import Wabe, zeiger  # noqa: F401
from volk_zeichnen import _hex_pts  # noqa: F401

EXTRA_NAH = ("<radialGradient id='gaPuppe' cx='.4' cy='.35' r='.8'><stop offset='0' stop-color='#fffaf0'/><stop offset='1' stop-color='#eadcb4'/></radialGradient>"
             "<radialGradient id='gaPuppeAuge' cx='.35' cy='.3' r='.8'><stop offset='0' stop-color='#b7a2c4'/><stop offset='1' stop-color='#6a5478'/></radialGradient>")


def gross(art, x, y, R):
    """Zellbaustein (z. B. 'H', 'D', 'P', 'B', 'L') an Stelle (x, y) mit Zellradius R."""
    return f"<use href='#z{art}' transform='translate({x:.1f} {y:.1f}) scale({R / 10:.3f})'/>"


def ei(x, y, R, rot=18):
    k = R / 25
    return (f"<g transform='translate({x:.1f} {y:.1f}) rotate({rot}) scale({k:.3f})'>"
            "<ellipse cx='1.5' cy='2.5' rx='4.2' ry='8.6' fill='#3a2008' opacity='.35'/>"
            "<ellipse cx='0' cy='0' rx='4.2' ry='8.6' fill='#fffdf4' stroke='#d8cfb4' stroke-width='.9'/>"
            "<ellipse cx='-1.3' cy='-3' rx='1.2' ry='3' fill='#fff' opacity='.9'/></g>")


def larve(x, y, R, g=.5, dreh=0):
    """C-förmige weiße Larve auf dem Zellboden. g = 0 (jung, klein) … 1 (groß, füllt die Zelle)."""
    k = R / 25
    rc, dicke = 5 + 6.5 * g, 4.2 + 5.2 * g
    a0, a1 = math.radians(-40), math.radians(235)
    x0, y0 = rc * math.cos(a0), rc * math.sin(a0)
    x1, y1 = rc * math.cos(a1), rc * math.sin(a1)
    d = f"M{x0:.1f},{y0:.1f} A{rc:.1f},{rc:.1f} 0 1 1 {x1:.1f},{y1:.1f}"
    ticks = ""
    for i in range(1, 9):
        a = a0 + (a1 - a0) * i / 9
        ticks += (f"M{(rc - dicke * .45) * math.cos(a):.1f},{(rc - dicke * .45) * math.sin(a):.1f}"
                  f"L{(rc + dicke * .45) * math.cos(a):.1f},{(rc + dicke * .45) * math.sin(a):.1f}")
    return (f"<g transform='translate({x:.1f} {y:.1f}) rotate({dreh}) scale({k:.3f})'>"
            f"<path d='{d}' fill='none' stroke='#3a2008' stroke-opacity='.35' stroke-width='{dicke + 3.4:.1f}' stroke-linecap='round' transform='translate(1.4 2)'/>"
            f"<path d='{d}' fill='none' stroke='#d9cca2' stroke-width='{dicke + 2:.1f}' stroke-linecap='round'/>"
            f"<path d='{d}' fill='none' stroke='#fffef6' stroke-width='{dicke:.1f}' stroke-linecap='round'/>"
            f"<path d='{ticks}' stroke='#d9cca2' stroke-width='.9' stroke-linecap='round'/>"
            f"<path d='{d}' fill='none' stroke='#fff' stroke-width='{dicke * .3:.1f}' stroke-linecap='round' opacity='.9' transform='translate(-.6 -1.1)'/>"
            f"<circle cx='{x1:.1f}' cy='{y1:.1f}' r='{dicke * .55:.1f}' fill='#fffef6' stroke='#d9cca2' stroke-width='.9'/></g>")


def zelle_leer_gross():
    """Leere Zelle (r = 25) mit Wachsrand und dunklem Boden."""
    return (f"<polygon points='{_hex_pts(0, 0, 25)}' fill='url(#gzRand)' stroke='#c08a25' stroke-width='2' stroke-linejoin='round'/>"
            f"<polygon points='{_hex_pts(0, 0, 20)}' fill='url(#gzTiefe)' stroke='#8a5410' stroke-width='1.6' stroke-linejoin='round'/>"
            "<path d='M-14,-9 L0,-18 L14,-9' fill='none' stroke='#4a2c08' stroke-width='2.2' opacity='.45' stroke-linecap='round'/>")


def puppe_offen(x, y, R):
    """Zelle mit halb aufgenagtem Deckel: oben schaut die Puppe heraus (Kopf mit Augen und Fühlern), von vorn gesehen;
    die untere Hälfte bedeckt noch der braune Deckel."""
    k = R / 25
    return (f"<g transform='translate({x:.1f} {y:.1f}) scale({k:.3f})'>" + zelle_leer_gross() +
            "<ellipse cx='1.2' cy='1' rx='15.5' ry='17' fill='#3a2008' opacity='.35'/>"
            "<ellipse cx='0' cy='-2' rx='15' ry='18' fill='url(#gaPuppe)' stroke='#cdbf94' stroke-width='1'/>"
            "<path d='M-3,-10 Q-8,-18 -13,-16 M3,-10 Q8,-18 13,-16' stroke='#cdbf94' stroke-width='1.8' fill='none' stroke-linecap='round'/>"
            "<ellipse cx='-6.4' cy='-8' rx='4.6' ry='6.2' fill='url(#gaPuppeAuge)' transform='rotate(12 -6.4 -8)'/>"
            "<ellipse cx='6.4' cy='-8' rx='4.6' ry='6.2' fill='url(#gaPuppeAuge)' transform='rotate(-12 6.4 -8)'/>"
            "<ellipse cx='-7.4' cy='-10.2' rx='1.2' ry='1.8' fill='#fff' opacity='.75'/><ellipse cx='5.4' cy='-10.2' rx='1.2' ry='1.8' fill='#fff' opacity='.75'/>"
            "<path d='M-12,4 Q-8,8 -4,6.5 M12,4 Q8,8 4,6.5' stroke='#cdbf94' stroke-width='1.6' fill='none' stroke-linecap='round'/>"
            "<clipPath id='cpPuppe'><path d='M-30,10 Q-12,5 0,8 T30,5 V30 H-30 Z'/></clipPath>"
            f"<g clip-path='url(#cpPuppe)'><polygon points='{_hex_pts(0, 0, 21.5)}' fill='url(#gzBrut)' stroke='#7a521c' stroke-width='1.3' stroke-linejoin='round'/>"
            "<circle cx='0' cy='17' r='2.4' fill='#6d4716' opacity='.7'/></g>"
            "<path d='M-21,10 Q-12,5 0,8 T21,5' fill='none' stroke='#fff' stroke-opacity='.55' stroke-width='1.6' stroke-linecap='round'/>"
            "<path d='M-21,11.4 Q-12,6.4 0,9.4 T21,6.4' fill='none' stroke='#5a3a10' stroke-opacity='.5' stroke-width='1.2' stroke-linecap='round'/></g>")


def volk_4():
    R = 25
    wb = Wabe(98, 22, R)
    plan = ["DDDHDD", "HHDHHH", "PPPHPP", "ELELEL", "VVVVVV", "OBBBBB"]
    groesse = {0: .35, 1: .5, 2: .7, 3: .55, 4: .9, 5: .8}
    eidreh = {0: 25, 2: -15, 4: 60}
    zellen, details = "", ""
    for z, zeile in enumerate(plan):
        for c, a in enumerate(zeile):
            x, y = wb.pos(c, z)
            if a in "DHPB":
                zellen += gross(a, x, y, R)
            elif a == "O":
                zellen += puppe_offen(x, y, R)
            else:
                zellen += gross("L", x, y, R)
                if a == "E":
                    details += ei(x, y + 2, R, eidreh.get(c, 18))
                if a == "V":
                    details += larve(x, y + 1, R, groesse.get(c, .5), (c * 47 + z * 13) % 360)
    p = [f"<ellipse cx='{W / 2}' cy='{H - 8}' rx='170' ry='9' fill='#7a5a20' opacity='.2'/>",
         f"<g filter='url(#fSchatten)'>{zellen}</g>", details]

    def ziel(c, z, dx=0, dy=0):
        x, y = wb.pos(c, z)
        return x + dx, y + dy
    xl, xr = 50, 432
    p.append(zeiger("Pollen", xl, ziel(0, 2)[1] + 5, *ziel(0, 2, -14, 0), size=14))
    p.append(zeiger("Ei", xl, ziel(0, 3)[1] + 5, *ziel(0, 3, -18, 4), size=14))
    p.append(zeiger("Puppe", xl, ziel(0, 5)[1] + 5, *ziel(0, 5, -16, 2), size=14))
    p.append(zeiger("Honig", xr, ziel(5, 1)[1] + 5, *ziel(5, 1, 16, 0), size=14))
    p.append(zeiger("Larve", xr, ziel(5, 4)[1] + 5, *ziel(5, 4, 16, 0), size=14))
    return volk_svg("Wabenausschnitt aus der Nähe: sechseckige Zellen mit Honig, Pollen, Ei, Larve und einer Puppe unter halb abgehobenem Deckel",
                    *p, bausteine="Z", extra=EXTRA_NAH, grund="#fff6df")
