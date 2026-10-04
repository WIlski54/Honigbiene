"""Szenen-Bausteine für grafiken_volk.py: Beschriftung mit Zeiger, Rähmchen mit Wabe, Bienenkasten im Querschnitt.

Aufbauend auf volk_zeichnen.py (Bienen, Zellen) und svg_helfer.py (nicht ändern).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volk_zeichnen import *  # noqa: F401,F403
from volk_zeichnen import Wabe, biene_o, biene_s  # noqa: F401


# ═══════════════════════════════════════════════════════════════════════════
#  Beschriftung mit Zeiger
# ═══════════════════════════════════════════════════════════════════════════
def zeiger(text, tx, ty, zx, zy, size=12, farbe=DUNKEL, abstand=5, w=1.7, ende=1, tfill=TEXT):
    """Kurze Beschriftung mit Pfeil. Der Text (Grundlinie bei ty, Mitte bei tx; mehrere Zeilen mit \\n) steht frei,
    der Pfeil beginnt am Rand des Textfelds und endet bei (zx, zy). Der Pfeil bekommt eine weiße Unterlage."""
    zeilen = text.split("\n")
    lh = round(size * 1.3)
    hw = max(len(z) for z in zeilen) * size * .29 + abstand
    hh = (len(zeilen) * lh) / 2 + abstand - 2
    cx, cy = tx, ty + (len(zeilen) - 1) * lh / 2 - size * .35
    dx, dy = zx - cx, zy - cy
    n = math.hypot(dx, dy) or 1
    k = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    sx, sy = cx + dx * k, cy + dy * k
    ex, ey = zx - dx / n * ende, zy - dy / n * ende
    out = (f"<line x1='{sx:.1f}' y1='{sy:.1f}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='#fff' stroke-width='{w + 3.2}' "
           f"stroke-linecap='round' opacity='.9'/>"
           + pfeil(sx, sy, ex, ey, farbe, w))
    for i, z in enumerate(zeilen):
        out += t(tx, ty + i * lh, z, size, 800, tfill)
    return out


def namensschild(x, y, text, farbe=BLAU, size=13, breite=None):
    """Weißes Namensschild (Mitte x, Oberkante y) mit farbigem Rand – für die Namen der Bienen."""
    w = breite or (len(text) * size * .58 + 22)
    return (f"<rect x='{x - w / 2:.1f}' y='{y}' width='{w:.1f}' height='{size + 12}' rx='{(size + 12) / 2:.0f}' fill='#fff' stroke='{farbe}' "
            f"stroke-width='2.2' filter='url(#fSchatten)'/>"
            + tp(x, y + size + 3, text, size, 800, farbe))


# ═══════════════════════════════════════════════════════════════════════════
#  Rähmchen mit Wabe (von vorn)
# ═══════════════════════════════════════════════════════════════════════════
_ZAEHLER = [0]


def rahmen(fx, fy, fw, fh, r, zone, ob=15, sb=13, ub=11, lug_l=16, lug_r=16, bienen="", dunkel=0.0):
    """Rähmchen von vorn: Holzrahmen (Oberträger mit Ohren, Seitenteile, Unterträger) und Wabe darin.
    `zone(u, v, c, z)` liefert die Zellart ('L', 'H', 'D', 'B', 'P') für die Zelle an der relativen Stelle (u, v) im Kamm.
    `bienen`: fertiger SVG-Text, wird über den Kamm gelegt (und am Kammrand abgeschnitten). `dunkel`: 0..1 abdunkeln."""
    _ZAEHLER[0] += 1
    cid = f"cpR{_ZAEHLER[0]}"
    ix, iy, iw, ih = fx + sb, fy + ob, fw - 2 * sb, fh - ob - ub
    wb = Wabe(ix, iy, r)
    zellen = []
    for z in range(-1, int(ih / (1.5 * r)) + 3):
        for c in range(-1, int(iw / wb.dx) + 3):
            x, y = wb.pos(c, z)
            if x < ix - r or x > ix + iw + r or y < iy - r or y > iy + ih + r:
                continue
            zellen.append(wb.lokal(zone((x - ix) / iw, (y - iy) / ih, c, z), c, z))
    out = (f"<clipPath id='{cid}'><rect x='{ix:.1f}' y='{iy:.1f}' width='{iw:.1f}' height='{ih:.1f}'/></clipPath>"
           f"<rect x='{fx:.1f}' y='{fy:.1f}' width='{fw:.1f}' height='{fh:.1f}' rx='3' fill='url(#gRaehm)' stroke='#6b4423' stroke-width='1.2'/>"
           f"<rect x='{ix:.1f}' y='{iy:.1f}' width='{iw:.1f}' height='{ih:.1f}' fill='#8a5410'/>"
           f"<g clip-path='url(#{cid})'>{wb.gruppe(zellen)}{bienen}</g>"
           f"<rect x='{ix:.1f}' y='{iy:.1f}' width='{iw:.1f}' height='{ih:.1f}' fill='none' stroke='#2a1608' stroke-opacity='.35' stroke-width='3'/>")
    if lug_l or lug_r or ob:
        out += (f"<rect x='{fx - lug_l:.1f}' y='{fy:.1f}' width='{fw + lug_l + lug_r:.1f}' height='{ob:.1f}' rx='2.5' fill='url(#gRaehmQ)' stroke='#6b4423' stroke-width='1.2'/>"
                f"<path d='M{fx - lug_l + 3:.1f},{fy + 3:.1f} H{fx + fw + lug_r - 3:.1f}' stroke='#fff' stroke-opacity='.45' stroke-width='1.4' stroke-linecap='round'/>")
    out += (f"<path d='M{fx + 3:.1f},{fy + ob + 6:.1f} V{fy + fh - 6:.1f} M{fx + fw - sb + 4:.1f},{fy + ob + 6:.1f} V{fy + fh - 6:.1f}' "
            f"stroke='#fff' stroke-opacity='.3' stroke-width='1.2' stroke-linecap='round'/>")
    if dunkel:
        out += f"<rect x='{fx - lug_l:.1f}' y='{fy:.1f}' width='{fw + lug_l + lug_r:.1f}' height='{fh:.1f}' fill='#1a0d04' opacity='{dunkel}'/>"
    return out


def zone_honig(seed=3, deckel=.55):
    """Honigwabe: fast nur Honig, oben viele Deckel, vereinzelt leere Zellen."""
    rnd = random.Random(seed)

    def f(u, v, c, z):
        k = rnd.random()
        if v < .25:
            return "D" if k < .9 else "H"
        if k < .06:
            return "L"
        if k < .06 + (deckel if v < .55 else deckel * .35):
            return "D"
        return "H"
    return f


def zone_brut(seed=5):
    """Brutwabe: oben Honigkranz, darunter ein Pollenband, in der Mitte verdeckelte Brut, unten Reste."""
    rnd = random.Random(seed)

    def f(u, v, c, z):
        k = rnd.random()
        if v < .2:
            return "D" if k < .75 else "H"
        if v < .33 and .12 < u < .88:
            return "P" if k < .6 else "H"
        e = ((u - .5) / .46) ** 2 + ((v - .64) / .33) ** 2
        if e < 1:
            return "B" if k < .86 else "L"
        if v > .8 and k < .5:
            return "H"
        return "D" if k < .5 else ("H" if k < .75 else "L")
    return f


# ═══════════════════════════════════════════════════════════════════════════
#  Bienenkasten im Querschnitt
# ═══════════════════════════════════════════════════════════════════════════
def kasten(bw=460, tw=70, hh=150, bh=172, bod=56, r=12, bienen=True, seed=1, eb=.5, nh=70):
    """Bienenkasten mit weggenommener Vorderwand (Blick von der Seite auf die Rähmchen).
    Ursprung = linke obere Ecke des Honigraums. Rückgabe: (svg_text, anker); anker = Punkte im Kasten-Koordinatensystem.
    `eb` = Größe der Bienen am Anflugbrett, `nh` = Höhe des Flugloch-Ausschnitts."""
    cx0, cx1 = tw, bw - tw
    yB0, yB1 = hh, hh + bh
    yBo = yB1 + bod
    bein_h = 20
    boden_y = yBo + bein_h
    g = []
    # Bodenschatten, Beine, Anflugbrett
    g.append(f"<ellipse cx='{bw / 2:.0f}' cy='{boden_y + 4}' rx='{bw * .66:.0f}' ry='10' fill='#1b3a12' opacity='.3'/>")
    for x in (20, bw - 80):
        g.append(f"<rect x='{x}' y='{yBo - 2}' width='60' height='{bein_h + 2}' rx='3' fill='url(#gkBoden)' stroke='#5b3a1d' stroke-width='1.4'/>")
    bl = 110
    ay, ey = yB1 + 5, boden_y - 3
    g.append(f"<path d='M-12,{ay} L{-12 - bl},{ey - 2} L{-12 - bl},{ey + 9} L-12,{ay + 11} Z' fill='url(#gkBoden)' stroke='#5b3a1d' stroke-width='1.4' stroke-linejoin='round'/>"
             f"<path d='M-14,{ay + 1} L{-12 - bl + 2},{ey - 1}' stroke='#fff' stroke-opacity='.4' stroke-width='1.6' stroke-linecap='round'/>")
    # Hohlräume, Rähmchen (hinten abgedunkelt), Bienen auf den Waben
    fw = cx1 - cx0 - 66
    for (y0, h, honig) in ((0, hh, True), (yB0, bh, False)):
        g.append(f"<rect x='{cx0}' y='{y0}' width='{cx1 - cx0}' height='{h}' fill='url(#gStockDunkel)'/>")
        fx, fy, fh = cx0 + 8, y0 + 12, h - 20
        # hintere Rähmchen: nur schmale Streifen rechts neben dem vorderen (Holz, Wabenrand, abgedunkelt)
        for k, dk in ((3, .55), (2, .42), (1, .28)):
            x1 = fx + fw + 18 * (k - 1)
            g.append(f"<rect x='{x1}' y='{fy}' width='18' height='{fh}' fill='url(#gRaehm)' stroke='#6b4423' stroke-width='1'/>"
                     f"<rect x='{x1 + 3}' y='{fy + 15}' width='12' height='{fh - 26}' fill='#c98a24'/>"
                     f"<path d='M{x1 + 9},{fy + 15} V{fy + fh - 11}' stroke='#8a5410' stroke-width='1.4' stroke-dasharray='5 3'/>"
                     f"<rect x='{x1}' y='{fy}' width='18' height='{fh}' fill='#1a0d04' opacity='{dk}'/>")
        bee = ""
        if bienen:
            pos = [(.28, .5, 60), (.62, .62, -30), (.8, .4, 170)] if honig else [(.2, .55, 20), (.46, .7, -35), (.7, .45, 140), (.34, .3, 80), (.62, .8, 200)]
            for (u, v, rot) in pos:
                bee += biene_o("A", fx + 13 + u * (fw - 26), fy + 15 + v * (fh - 26), rot, .5)
        zone = zone_honig(seed) if honig else zone_brut(seed + 4)
        g.append(rahmen(fx, fy, fw, fh, r, zone, ob=15, sb=13, ub=11, lug_l=fx - cx0, lug_r=cx1 - (fx + fw), bienen=bee))
        g.append(f"<rect x='{cx0}' y='{y0}' width='{cx1 - cx0}' height='{h}' fill='url(#gkInnen)'/>")

    # Wände (bemalt)
    def wand(x, y, w, h, grad):
        return (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='url(#{grad})' stroke='#3a2410' stroke-width='1.6'/>"
                f"<path d='M{x + 6},{y + 8} V{y + h - 8}' stroke='#fff' stroke-opacity='.35' stroke-width='3' stroke-linecap='round'/>"
                + "".join(f"<path d='M{x + 3},{y + h * f:.0f} H{x + w - 3}' stroke='#000' stroke-opacity='.10' stroke-width='1'/>" for f in (.3, .6, .85)))
    g.append(wand(0, 0, tw, hh, "gkHonig") + wand(bw - tw, 0, tw, hh, "gkHonig"))
    g.append(wand(0, yB0, tw, bh - nh, "gkBrut") + wand(bw - tw, yB0, tw, bh, "gkBrut"))
    # Flugloch (Ausschnitt in der linken Wand), Licht von außen
    g.append(f"<rect x='0' y='{yB1 - nh}' width='{tw}' height='{nh}' fill='#1d1007'/>"
             f"<path d='M0,{yB1} H{tw}' stroke='#e9c27d' stroke-width='3'/>"
             f"<rect x='0' y='{yB1 - nh}' width='{tw}' height='{nh}' fill='none' stroke='#3a2410' stroke-width='1.6'/>")
    # Fuge zwischen Honigraum und Brutraum
    g.append(f"<path d='M0,{hh} H{bw}' stroke='#2a1608' stroke-opacity='.75' stroke-width='2.4'/>"
             f"<path d='M0,{hh + 3} H{bw}' stroke='#fff' stroke-opacity='.25' stroke-width='1.4'/>")
    # Boden
    g.append(f"<rect x='-12' y='{yB1}' width='{bw + 24}' height='{bod}' rx='4' fill='url(#gkBoden)' stroke='#5b3a1d' stroke-width='1.6'/>"
             f"<path d='M-4,{yB1 + 9} H{bw + 4}' stroke='#fff' stroke-opacity='.4' stroke-width='1.6' stroke-linecap='round'/>"
             f"<path d='M-4,{yB1 + 26} H{bw + 4}' stroke='#5b3a1d' stroke-opacity='.3' stroke-width='1.4'/>")
    # Dach (Satteldach mit Dachkante)
    ap = -88
    g.append(f"<rect x='-26' y='-14' width='{bw + 52}' height='15' rx='3' fill='#b5503f' stroke='#6e2a1f' stroke-width='1.6'/>"
             f"<path d='M-26,-14 L{bw / 2:.0f},{ap} L{bw + 26},-14 Z' fill='url(#gkDach)' stroke='#6e2a1f' stroke-width='1.8' stroke-linejoin='round'/>"
             + "".join(f"<path d='M{-26 + (bw / 2 + 26) * f:.0f},{-14 + (ap + 14) * f:.0f} L{bw + 26 - (bw / 2 + 26) * f:.0f},{-14 + (ap + 14) * f:.0f}' "
                       f"stroke='#7a2f22' stroke-opacity='.28' stroke-width='1.6'/>" for f in (.22, .44, .66, .86))
             + f"<path d='M-18,-16 L{bw / 2 - 4:.0f},{ap + 6}' stroke='#fff' stroke-opacity='.5' stroke-width='2.4' stroke-linecap='round'/>")
    # Bienen am Anflugbrett und im Flugloch (Seitenansicht)
    if bienen:
        win = -math.degrees(math.atan((ey - ay) / (bl + 12)))
        for f_, sp in ((.2, False), (.52, True), (.82, False)):
            g.append(biene_s(-12 - f_ * bl, ay + f_ * (ey - ay) - 12 * eb / .5, eb, sp, win))
        g.append(biene_s(26, yB1 - 22, min(eb, .55), False, 0))
    anker = {
        "dach": (bw / 2, -50), "honigraum": (bw - tw / 2, hh / 2), "brutraum": (bw - tw / 2, hh + bh / 2),
        "boden": (bw * .66, yB1 + bod / 2), "flugloch": (tw / 2, yB1 - nh / 2),
        "honigraum_innen": (bw / 2, hh / 2), "brutraum_innen": (bw / 2, hh + bh / 2),
        "unten": boden_y, "anflug": (-12 - bl / 2, (ay + ey) / 2),
    }
    return "".join(g), anker
