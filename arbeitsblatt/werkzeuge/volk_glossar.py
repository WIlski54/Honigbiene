"""Glossarbilder Königin, Drohne und Wabe (480 × 288) für den Reiter „Das Bienenvolk“."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_nah import EXTRA_NAH, ei, gross  # noqa: F401
from volk_szenen import *  # noqa: F401,F403
from volk_szenen import Wabe, namensschild, rahmen, zeiger, zone_brut, zone_honig  # noqa: F401
from volk_zeichnen import _hex_pts  # noqa: F401

HINTERGRUND = "<radialGradient id='gGlanz' cx='.5' cy='.45' r='.7'><stop offset='.45' stop-color='#fff' stop-opacity='.6'/><stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>"


def _wabengrund(pid, w=W, h=H, hell=.72):
    """Blasser Wabenhintergrund (Muster `pid` muss in defs_extra stehen)."""
    return (f"<rect width='{w}' height='{h}' fill='url(#{pid})'/><rect width='{w}' height='{h}' fill='#fff8e2' opacity='{hell}'/>"
            f"<rect width='{w}' height='{h}' fill='url(#gGlanz)'/>")


# ═══════════════════════════════════════════════════════════════════════════
def glossar_koenigin():
    r = 24
    wb = Wabe(-10, -6, r)
    qx, qy, qs = 240, 112, 1.12
    zellen, eier = "", ""
    for (c, z, rot) in ((5, 6, 20), (6, 6, -25), (4, 7, 15), (5, 7, -10), (6, 7, 40), (3, 6, 5)):
        x, y = wb.pos(c, z)
        zellen += gross("L", x, y, r)
        eier += ei(x, y + 1, r, rot)
    hof = [(122, 120, 92), (362, 124, -88), (150, 54, 118), (336, 52, -122)]
    hofstaat = "".join(biene_o("A", x, y, rot, .86) for x, y, rot in hof)
    p = [_wabengrund("pK", hell=.7), zellen, eier, hofstaat, biene_o("K", qx, qy, 0, qs)]
    p.append(zeiger("Königin", 78, 262, qx - 14, qy - 19 * qs + 6, size=15))
    ex, ey = wb.pos(6, 6)
    p.append(zeiger("Ei", 386, 262, ex + 6, ey + 4, size=15))
    p.append(zeiger("Arbeiterin", 400, 214, hof[1][0] + 8, hof[1][1] + 26, size=14))
    return volk_svg("Die Königin auf der Wabe: großer Körper mit langem Hinterleib und rotem Punkt auf dem Rücken, umgeben von Arbeiterinnen, in den Zellen liegen Eier",
                    *p, bausteine="AKZ", extra=muster_wabe("pK", r, -10, -6) + HINTERGRUND, grund="#fff3cf")


# ═══════════════════════════════════════════════════════════════════════════
def glossar_drohne():
    r = 24
    s_d, s_a = 1.5, 1.0
    dx, dy = 168, 142
    ax, ay = 372, 140
    p = [_wabengrund("pD"), biene_o("A", ax, ay, 8, s_a), biene_o("D", dx, dy, -6, s_d)]
    # Merkmale
    a = math.radians(-6)

    def rot(x, y):          # Punkt der Drohne (Einheiten) -> Bild
        return dx + (x * math.cos(a) - y * math.sin(a)) * s_d, dy + (x * math.sin(a) + y * math.cos(a)) * s_d
    p.append(zeiger("riesige\nAugen", 66, 46, *rot(-12, -46), size=15))
    p.append(zeiger("kein\nStachel", 62, 232, *rot(-3, 49), size=15))
    p.append(namensschild(dx, 247, "Drohne", "#b06a00", 15))
    p.append(namensschild(ax, 247, "Arbeiterin", BLAU, 15))
    return volk_svg("Die Drohne neben einer Arbeiterin: Die Drohne ist dicker, hat riesige Augen und keinen Stachel",
                    *p, bausteine="ADZ", extra=muster_wabe("pD", r, 0, 0) + HINTERGRUND, grund="#fff3cf")


# ═══════════════════════════════════════════════════════════════════════════
def _lupe(cx, cy, r):
    """Lupe mit Griff; innen drei große Zellen (Honig, Deckel, Honig)."""
    R = 31
    zellen = (gross("H", cx - 16, cy - 20, R) + gross("D", cx + 36, cy + 3, R) + gross("H", cx - 14, cy + 36, R)
              + gross("H", cx - 62, cy + 2, R))
    return (f"<clipPath id='cpLupe'><circle cx='{cx}' cy='{cy}' r='{r - 3}'/></clipPath>"
            f"<path d='M{cx + r * .72:.1f},{cy + r * .72:.1f} L{cx + r * 1.28:.1f},{cy + r * 1.28:.1f}' stroke='#6b4423' stroke-width='13' stroke-linecap='round'/>"
            f"<path d='M{cx + r * .76:.1f},{cy + r * .7:.1f} L{cx + r * 1.24:.1f},{cy + r * 1.22:.1f}' stroke='#c9965a' stroke-width='5' stroke-linecap='round'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#fff7dc'/>"
            f"<g clip-path='url(#cpLupe)'>{zellen}</g>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='#8a96a3' stroke-width='6'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r - 3}' fill='none' stroke='#dfe6ec' stroke-width='2'/>"
            f"<path d='M{cx - r * .6:.1f},{cy - r * .35:.1f} A{r * .72:.1f},{r * .72:.1f} 0 0 1 {cx - r * .2:.1f},{cy - r * .72:.1f}' fill='none' stroke='#fff' stroke-width='4' stroke-linecap='round' opacity='.85'/>")


def glossar_wabe():
    fx, fy, fw, fh = 34, 24, 276, 240
    lx, ly, lr = 396, 134, 58
    bee = "".join(biene_o("A", fx + 22 + u * (fw - 44), fy + 24 + v * (fh - 44), rot, .5)
                  for u, v, rot in ((.3, .42, 30), (.68, .6, -60), (.46, .82, 150)))
    zone = zone_brut(17)
    kamm_x, kamm_y = fx + 196, fy + 64
    p = [f"<rect width='{W}' height='{H}' fill='url(#gGlanz)' opacity='.5'/>",
         # Lupenkegel von der Wabe zur Lupe
         f"<ellipse cx='{fx + fw / 2}' cy='{fy + fh + 6}' rx='{fw * .5:.0f}' ry='8' fill='#7a5a20' opacity='.25'/>",
         rahmen(fx, fy, fw, fh, 13, zone, ob=24, sb=22, ub=20, lug_l=16, lug_r=16, bienen=bee),
         f"<path d='M{kamm_x + 14},{kamm_y - 10} L{lx - lr * .8:.1f},{ly - lr * .62:.1f} L{lx - lr * .8:.1f},{ly + lr * .62:.1f} L{kamm_x + 14},{kamm_y + 10} Z' fill='#fff' opacity='.42'/>",
         f"<circle cx='{kamm_x}' cy='{kamm_y}' r='15' fill='none' stroke='#fff' stroke-width='3'/>",
         _lupe(lx, ly, lr)]
    p.append(zeiger("Rähmchen", 392, 36, fx + fw + 6, fy + 12, size=14))
    p.append(zeiger("Wabe", 372, 262, fx + fw - 40, fy + fh - 60, size=14))
    p.append(zeiger("Zelle", 396, 226, lx + 6, ly + 40, size=14))
    return volk_svg("Ein Rähmchen mit Wabe und eine Lupe, die eine sechseckige Zelle vergrößert", *p, bausteine="AZ",
                    extra=HINTERGRUND, grund="#fff3cf")
