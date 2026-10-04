"""Glossarbilder Schwänzeltanz und Wintertraube (480 × 288) für den Reiter „Das Bienenvolk“."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_szenen import *  # noqa: F401,F403
from volk_szenen import Wabe, rahmen, zeiger, zone_honig  # noqa: F401

STRICH = "#fff"


def _pt(x, y):
    return f"{x:.1f},{y:.1f}"


def _winkelbogen(cx, cy, r, grad, farbe=MAGENTA, w=3):
    """Bogen von der Senkrechten (oben) um `grad` Grad nach rechts, Mittelpunkt (cx, cy)."""
    a = math.radians(grad)
    x2, y2 = cx + r * math.sin(a), cy - r * math.cos(a)
    return (f"<path d='M{_pt(cx, cy - r)} A{r},{r} 0 0 1 {_pt(x2, y2)}' fill='none' stroke='#fff' stroke-width='{w + 3}' stroke-linecap='round' opacity='.85'/>"
            f"<path d='M{_pt(cx, cy - r)} A{r},{r} 0 0 1 {_pt(x2, y2)}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round'/>")


def _gestrichelt(x1, y1, x2, y2, farbe, w=2.2, dash="7 5"):
    return (f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='#fff' stroke-width='{w + 3}' opacity='.8' stroke-linecap='round'/>"
            f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{farbe}' stroke-width='{w}' stroke-dasharray='{dash}' stroke-linecap='round'/>")


# ═══════════════════════════════════════════════════════════════════════════
def glossar_schwaenzeltanz():
    al = 38                                   # Winkel zur Senkrechten
    a = math.radians(al)
    u = (math.sin(a), -math.cos(a))           # Richtung des Schwänzellaufs (nach oben rechts)
    n = (math.cos(a), math.sin(a))            # Querrichtung (rechts unten)
    ax_, ay_ = 90, 244                        # Beginn des Schwänzellaufs
    L = 152
    bx_, by_ = ax_ + u[0] * L, ay_ + u[1] * L

    # Tafel links: senkrechte Wabe (dunkler, wie im Stock)
    px0, py0, pw, ph = 6, 30, 246, 252
    tafel_a = (f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='12' fill='#8a5410' stroke='#a8743c' stroke-width='6'/>"
               f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='12' fill='url(#pT)'/>"
               f"<rect x='{px0}' y='{py0}' width='{pw}' height='{ph}' rx='12' fill='url(#gDunkel)'/>")
    # Figur: zwei Schleifen und der Schwänzellauf
    def schleife(seite):
        s_ = seite
        c1 = (bx_ + s_ * n[0] * 64 + u[0] * 24, by_ + s_ * n[1] * 64 + u[1] * 24)
        c2 = (ax_ + s_ * n[0] * 64 - u[0] * 24, ay_ + s_ * n[1] * 64 - u[1] * 24)
        d = f"M{_pt(bx_, by_)} C{_pt(*c1)} {_pt(*c2)} {_pt(ax_, ay_)}"
        return (f"<path d='{d}' fill='none' stroke='#fff' stroke-width='5.4' opacity='.8' stroke-linecap='round'/>"
                f"<path d='{d}' fill='none' stroke='{BLAU}' stroke-width='2.6' stroke-dasharray='7 5' stroke-linecap='round'/>")
    figur = schleife(-1) + schleife(1)
    # Schwänzellauf: Zickzack mit Pfeilspitze
    pts = []
    N = 44
    for i in range(N + 1):
        t_ = i / N
        amp = 4.2 * math.sin(2 * math.pi * t_ * (L / 10))
        pts.append((ax_ + u[0] * (L - 10) * t_ + n[0] * amp, ay_ + u[1] * (L - 10) * t_ + n[1] * amp))
    zz = "M" + " L".join(_pt(x, y) for x, y in pts) + f" L{_pt(bx_, by_)}"
    lauf = (f"<path d='{zz}' fill='none' stroke='#fff' stroke-width='6.4' stroke-linecap='round' stroke-linejoin='round' opacity='.85'/>"
            + bogen(zz, ROT, 3.2))
    # Tänzerin und Zuschauerinnen
    dx_, dy_ = ax_ + u[0] * 80, ay_ + u[1] * 80
    zuschau = ""
    for ang, abst in ((340, 56), (32, 58), (96, 57), (152, 56), (292, 56)):
        b = math.radians(ang)
        sx, sy = dx_ + math.sin(b) * abst, dy_ - math.cos(b) * abst
        zuschau += biene_o("A", sx, sy, ang + 180, .4)
    taenzerin = biene_o("A", dx_, dy_, al, .55)
    vert = _gestrichelt(ax_, py0 + 14, ax_, ay_ + 40, "#fff", 2.4, "6 5")
    bogen_a = _winkelbogen(ax_, ay_, 62, al, w=3.6)
    tafel_beschr = t(px0 + pw / 2, 22, "im Stock", 15, 800, TEXT)
    links = [tafel_a, vert, figur, lauf, zuschau, taenzerin, bogen_a, tafel_beschr,
             t(ax_ - 8, py0 + 34, "senkrecht", 12, 800, TEXT, "end"),
             zeiger("Schwänzellauf", 192, 64, *(bx_ + 2, by_ - 2), size=13, farbe=ROT),
             zeiger("Winkel", 44, 158, ax_ + math.sin(a / 2) * 62 - 2, ay_ - math.cos(a / 2) * 62 + 2, size=13, farbe=MAGENTA)]

    # Tafel rechts: draußen (Wiese von oben)
    qx0, qy0, qw, qh = 262, 30, 212, 252
    hx, hy = 330, 244
    L2 = 168
    fx, fy = hx + u[0] * L2, hy + u[1] * L2
    wiese = (f"<rect x='{qx0}' y='{qy0}' width='{qw}' height='{qh}' rx='12' fill='url(#gWiese)' stroke='#5b8a3a' stroke-width='3'/>"
             + "".join(gras(qx0 + 20 + i * 41 % (qw - 30), qy0 + 40 + (i * 53) % (qh - 60), .9) for i in range(9)))
    sonne_p = sonne(hx, 62, 13, True)
    sonnenlinie = _gestrichelt(hx, hy - 22, hx, 82, "#f2a900", 2.6, "7 5")
    sx_, sy_ = hx + u[0] * 22, hy - 6 + u[1] * 22
    ex_, ey_ = fx - u[0] * 18, fy - u[1] * 18
    flug = (f"<line x1='{sx_:.1f}' y1='{sy_:.1f}' x2='{ex_:.1f}' y2='{ey_:.1f}' stroke='#fff' stroke-width='7' opacity='.8' stroke-linecap='round'/>"
            + pfeil(sx_, sy_, ex_, ey_, ROT, 3.2))
    bogen_b = _winkelbogen(hx, hy - 6, 52, al)
    blumen = "".join(blume(fx + dx, fy + dy, 1.15, c) for dx, dy, c in ((-14, 12, "#e879a6"), (10, 8, "#f5c542"), (0, 20, "#c08adf"), (-6, 0, "#ffffff"), (14, 20, "#ff8a65")))
    stock = ("<g filter='url(#fSchatten)'><rect x='%s' y='%s' width='38' height='26' rx='3' fill='url(#gkHonig)' stroke='#7a4b22' stroke-width='1.6'/>"
             "<path d='M%s,%s L%s,%s L%s,%s Z' fill='url(#gkDach)' stroke='#6e2a1f' stroke-width='1.6' stroke-linejoin='round'/>"
             "<rect x='%s' y='%s' width='9' height='5' fill='#2a1608'/></g>") % (
        hx - 19, hy - 8, hx - 25, hy - 8, hx, hy - 30, hx + 25, hy - 8, hx - 4.5, hy + 8)
    biene = biene_s(hx + u[0] * 100 - 14, hy + u[1] * 100 - 2, .5, False, -52)
    rechts = [wiese, sonnenlinie, sonne_p, flug, bogen_b, stock, blumen, biene,
              t(qx0 + qw / 2, 22, "draußen", 15, 800, TEXT),
              zeiger("Sonne", 424, 66, hx + 24, 62, size=13),
              zeiger("Futter", 440, 196, fx + 8, fy + 28, size=13),
              zeiger("Winkel", 290, 176, hx + math.sin(a / 2) * 52 - 3, hy - 6 - math.cos(a / 2) * 52, size=13, farbe=MAGENTA),
              t(400, 272, "gleicher Winkel", 13, 800, MAGENTA)]
    extra = (muster_wabe("pT", 13, 0, 0) +
             "<linearGradient id='gDunkel' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a1608' stop-opacity='.55'/><stop offset='1' stop-color='#2a1608' stop-opacity='.35'/></linearGradient>")
    return volk_svg("Schwänzeltanz: Links tanzt eine Biene auf der senkrechten Wabe, der Schwänzellauf bildet einen Winkel zur Senkrechten. "
                    "Rechts liegt das Futter im gleichen Winkel zur Sonne", *(links + rechts), bausteine="AZS", extra=extra, grund="#d9ecff")


# ═══════════════════════════════════════════════════════════════════════════
def glossar_wintertraube():
    x0, bw, tw = 36, 296, 36
    yb0, hh = 80, 168                                 # Oberkante und Höhe des Kastens
    cx0, cx1 = x0 + tw, x0 + bw - tw
    rnd = random.Random(8)
    himmel = "<rect width='480' height='288' fill='url(#gNacht)'/>"
    sterne = "".join(f"<circle cx='{rnd.uniform(10, 470):.0f}' cy='{rnd.uniform(8, 120):.0f}' r='{rnd.uniform(.8, 1.6):.1f}' fill='#fff' opacity='{rnd.uniform(.5, .95):.2f}'/>" for _ in range(22))
    mond = ("<circle cx='436' cy='42' r='15' fill='#fff7d1'/><circle cx='443' cy='37' r='13' fill='#2c3f6e'/>")
    boden = ("<path d='M0,254 Q90,236 190,248 T380,244 T480,240 V288 H0 Z' fill='url(#gSchnee)'/>"
             "<path d='M0,262 Q120,250 250,260 T480,256' fill='none' stroke='#b9cde6' stroke-width='2' opacity='.8'/>")
    # Kasten (Brutraum) mit Wabe
    fx, fy, fh = cx0 + 8, yb0 + 8, hh - 16
    fw = cx1 - cx0 - 16
    zone = zone_honig(5, deckel=.7)
    comb_x, comb_y = fx + 13, fy + 15
    comb_w, comb_h = fw - 26, fh - 26
    ccx, ccy = comb_x + comb_w / 2, comb_y + comb_h / 2
    rc = 42
    # Traube: Ringe aus Bienen
    bienen = ""
    ringe = ((41, 21), (32, 16), (23, 10), (14, 6), (5, 2))
    for rad, n in ringe:
        for i in range(n):
            ang = 2 * math.pi * i / n + rnd.uniform(-.2, .2)
            r_ = rad + rnd.uniform(-3, 3)
            bx, by = ccx + math.cos(ang) * r_, ccy + math.sin(ang) * r_ * .98
            kopf = math.degrees(math.atan2(-math.cos(ang), math.sin(ang))) + rnd.uniform(-38, 38)
            bienen += biene_o("A", bx, by, kopf, rnd.uniform(.33, .37))
    glut = (f"<circle cx='{ccx:.1f}' cy='{ccy:.1f}' r='{rc + 40}' fill='url(#gGlut)'/>"
            f"<circle cx='{ccx:.1f}' cy='{ccy:.1f}' r='{rc - 6}' fill='#c8561a' opacity='.75'/>")
    kamm = rahmen(fx, fy, fw, fh, 10, zone, ob=15, sb=13, ub=11, lug_l=fx - cx0, lug_r=cx1 - (fx + fw),
                  bienen=glut + bienen + biene_o("K", ccx + 1, ccy + 2, 24, .5))
    ground_y = yb0 + hh + 20 + 12

    def wand(x, y, w, h):
        return (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='url(#gkBrut)' stroke='#3a2410' stroke-width='1.6'/>"
                f"<path d='M{x + 5},{y + 8} V{y + h - 8}' stroke='#fff' stroke-opacity='.35' stroke-width='3' stroke-linecap='round'/>")
    kasten_t = (f"<rect x='{cx0}' y='{yb0}' width='{cx1 - cx0}' height='{hh}' fill='url(#gStockDunkel)'/>" + kamm +
                f"<rect x='{cx0}' y='{yb0}' width='{cx1 - cx0}' height='{hh}' fill='url(#gkInnen)'/>"
                + wand(x0, yb0, tw, hh) + wand(x0 + bw - tw, yb0, tw, hh))
    boden_b = (f"<rect x='{x0 - 10}' y='{yb0 + hh}' width='{bw + 20}' height='22' rx='4' fill='url(#gkBoden)' stroke='#5b3a1d' stroke-width='1.6'/>"
               f"<rect x='{x0 + 16}' y='{yb0 + hh + 20}' width='50' height='12' rx='3' fill='url(#gkBoden)' stroke='#5b3a1d' stroke-width='1.2'/>"
               f"<rect x='{x0 + bw - 66}' y='{yb0 + hh + 20}' width='50' height='12' rx='3' fill='url(#gkBoden)' stroke='#5b3a1d' stroke-width='1.2'/>")
    # Dach mit Schneehaube und Eiszapfen
    ap, eave = yb0 - 60, yb0 - 12
    mx = x0 + bw / 2
    dach = (f"<rect x='{x0 - 22}' y='{eave}' width='{bw + 44}' height='13' rx='3' fill='#b5503f' stroke='#6e2a1f' stroke-width='1.6'/>"
            f"<path d='M{x0 - 22},{eave} L{mx:.0f},{ap} L{x0 + bw + 22},{eave} Z' fill='url(#gkDach)' stroke='#6e2a1f' stroke-width='1.8' stroke-linejoin='round'/>")
    schnee = (f"<path d='M{x0 - 24},{eave + 1} L{mx:.0f},{ap - 6} L{x0 + bw + 24},{eave + 1}' fill='none' stroke='#cfdff2' stroke-width='15' stroke-linejoin='round' stroke-linecap='round'/>"
              f"<path d='M{x0 - 24},{eave - 2} L{mx:.0f},{ap - 9} L{x0 + bw + 24},{eave - 2}' fill='none' stroke='#fff' stroke-width='12' stroke-linejoin='round' stroke-linecap='round'/>"
              + "".join(f"<circle cx='{x0 - 8 + i * 28}' cy='{eave + 2 + (3 if i % 2 else 0)}' r='{6 + i % 3}' fill='#fff'/>" for i in range(1, 11))
              + "".join(f"<path d='M{x_},{eave + 12} l3,{h_} l3,-{h_} z' fill='#e8f3ff' stroke='#a9c3de' stroke-width='.8'/>" for x_, h_ in ((x0 + 6, 12), (x0 + 60, 9), (x0 + 118, 14), (x0 + 196, 10), (x0 + 252, 13), (x0 + 296, 9))))
    flocken = "".join(f"<circle cx='{rnd.uniform(6, 474):.0f}' cy='{rnd.uniform(6, 270):.0f}' r='{rnd.uniform(1.4, 3):.1f}' fill='#fff' opacity='{rnd.uniform(.6, .95):.2f}'/>" for _ in range(30))
    # Beschriftungen rechts neben dem Kasten
    lx = 412
    ziele = [
        zeiger("Honigvorrat", lx, 92, cx1 - 24, fy + 34, size=13),
        zeiger("Wintertraube", lx, 150, ccx + rc - 4, ccy - 12, size=13),
        zeiger("Königin", lx, 214, ccx + 12, ccy + 5, size=13),
    ]
    extra = ("<linearGradient id='gNacht' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#1d2c58'/><stop offset='.55' stop-color='#6f8bbd'/><stop offset='1' stop-color='#c9d9ee'/></linearGradient>"
             "<linearGradient id='gSchnee' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff'/><stop offset='1' stop-color='#cfe0f3'/></linearGradient>"
             "<radialGradient id='gGlut' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#ff6a1f' stop-opacity='.95'/><stop offset='.55' stop-color='#ff8a2c' stop-opacity='.8'/>"
             "<stop offset='1' stop-color='#ff9a3c' stop-opacity='0'/></radialGradient>")
    teile = [himmel, sterne, mond, boden, f"<ellipse cx='{x0 + bw / 2}' cy='{ground_y}' rx='{bw * .6:.0f}' ry='8' fill='#6f86a8' opacity='.35'/>",
             boden_b, kasten_t, dach, schnee, flocken] + ziele
    return volk_svg("Wintertraube: Im Querschnitt durch den verschneiten Bienenkasten sitzen die Bienen als runde Traube dicht zusammen, "
                    "in der Mitte die Königin, rundherum liegt der Honigvorrat", *teile, bausteine="AKZ", extra=extra, grund="#1d2c58")
