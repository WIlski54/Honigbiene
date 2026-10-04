"""Bienen von oben, Schnitte durch die Brust (koerper-3).

Lokale Koordinaten wie in bienen_zeichnen.py; `biene_oben()` zeigt die Biene von oben (Kopf oben, Ursprung = Brustmitte).
"""
from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz
import bienen_situs  # noqa: F401  (registriert u. a. den Verlauf bDarmRosa)

_bz.DEFS_EXTRA.append(
    "<radialGradient id='bMusk' cx='.4' cy='.3' r='.9'><stop offset='0' stop-color='#f08b7a'/><stop offset='.55' stop-color='#d64a40'/><stop offset='1' stop-color='#8e1f1a'/></radialGradient>"
    "<linearGradient id='bMuskV' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#b42f28'/><stop offset='.45' stop-color='#ee7a68'/><stop offset='1' stop-color='#a42a24'/></linearGradient>"
)

KOPF_O_D = "M-26,-50 C-26,-70 26,-70 26,-50 C26,-36 14,-30 0,-30 C-14,-30 -26,-36 -26,-50 Z"


def _halb_rechts():
    """Rechte Hälfte (Beine, Flügel); die linke entsteht durch Spiegeln."""
    o = []
    # Beine (unter den Flügeln)
    beine = [
        ([(26, -22), (46, -38), (64, -36), (76, -46), (82, -52)], [9, 7, 4.5, 3]),     # Vorderbein
        ([(32, 2), (58, 6), (82, 20), (94, 38), (98, 46)], [9.5, 7.5, 5, 3.4]),         # Mittelbein
        ([(30, 20), (52, 38), (68, 66), (72, 88), (72, 96)], [10.5, 8.5, 5.5, 3.6]),    # Hinterbein
    ]
    for pts, dk in beine:
        o.append(bein(pts, dk, haare_n=8, seed=int(pts[0][0] + pts[-1][1])))
    # Flügel: Hinterflügel zuerst (liegt unter dem Vorderflügel)
    o.append(fluegel_platz(20, -2, 52, 96, 30, "hinter", 1.0))
    o.append(fluegel_platz(26, -14, 18, 142, 44, "vor", 1.0))
    return "".join(o)


def biene_oben(seed=5):
    """Biene von oben, Flügel gespreizt: 2 Vorderflügel, 2 Hinterflügel, 6 Beine, Kopf mit 2 Augen und 2 Fühlern."""
    halb = _halb_rechts()
    o = [f"<g>{halb}</g>", f"<g transform='scale(-1 1)'>{halb}</g>"]
    # Hinterleib
    cid = neue_id("ho")
    d_hl = "M-30,34 C-46,60 -42,102 -9,124 L0,130 L9,124 C42,102 46,60 30,34 Z"
    bands = ""
    for i, (ya, c) in enumerate([(30, "#e9a924"), (50, "#33230f"), (68, "#e9a924"), (86, "#33230f"), (102, "#e9a924"), (116, "#33230f")]):
        yb = [50, 68, 86, 102, 116, 140][i]
        bands += f"<path d='M-60,{ya} Q0,{ya + 8} 60,{ya} L60,{yb} Q0,{yb + 8} -60,{yb} Z' fill='{c}'/>"
    o.append(f"<clipPath id='{cid}'><path d='{d_hl}'/></clipPath>"
             f"<g clip-path='url(#{cid})'><g filter='url(#bWeich2)'>{bands}</g>"
             + haare_linie(-44, 52, 44, 58, 16, 7, "#fbe08a", .9, richtung=(0, 1), seed=3, opa=.8)
             + haare_linie(-44, 88, 44, 94, 16, 7, "#fbe08a", .9, richtung=(0, 1), seed=4, opa=.8)
             + f"<path d='{d_hl}' fill='url(#bVolSeite)'/></g><path d='{d_hl}' fill='none' stroke='#4a2f10' stroke-width='1.3'/>"
             + haare(0, 82, 40, 50, 40, 7, "#f6d672", .9, seed=12, a0=-10, a1=190, aussen=.9, richtung=(0, 1)))
    # Kopf
    o.append("<path d='M-14,-70 C-30,-100 -48,-110 -50,-120 M14,-70 C30,-100 48,-110 50,-120' fill='none' stroke='#150d06' stroke-width='4.6' stroke-linecap='round'/>"
             "<path d='M-14,-70 C-30,-100 -48,-110 -50,-120 M14,-70 C30,-100 48,-110 50,-120' fill='none' stroke='#5a4030' stroke-width='2.8' stroke-linecap='round'/>")
    o.append(f"<path d='{KOPF_O_D}' fill='url(#bKopf)' stroke='#150d06' stroke-width='1.3'/>")
    for vz in (-1, 1):
        o.append(f"<g transform='translate({24 * vz} -50) rotate({-14 * vz})'><ellipse rx='11.5' ry='19' fill='url(#bAuge)' stroke='#0c0602' stroke-width='1'/>"
                 f"<ellipse rx='11.5' ry='19' fill='url(#bHex)'/><ellipse cx='{-3 * vz}' cy='-8' rx='3.2' ry='6.5' fill='url(#bGlanz)'/></g>")
    for px, py in ((-6, -62), (6, -62), (0, -54)):
        o.append(f"<circle cx='{px}' cy='{py}' r='2.8' fill='#e7c777' stroke='#150d06' stroke-width='.8'/>")
    o.append(haare(0, -48, 26, 18, 24, 7, "#e6bd58", 1.0, a0=190, a1=350, richtung=(0, -1), aussen=.9, seed=seed))
    # Brust (Pelz)
    o.append("<ellipse cx='0' cy='0' rx='37' ry='36' fill='#7a4a14' filter='url(#bFuzz)'/>")
    o.append("<ellipse cx='0' cy='0' rx='36' ry='35' fill='url(#bBrust)' filter='url(#bFuzz)'/>")
    o.append(flaum(0, 0, 33, 32, 130, 8, "#f6cf62", 1.2, richtung=(0, 1), seed=seed + 1, opa=.75))
    o.append(flaum(0, 4, 30, 28, 50, 8, "#6b3f10", 1.3, richtung=(0, 1), seed=seed + 2, opa=.4))
    o.append(f"<ellipse cx='0' cy='0' rx='36' ry='35' fill='url(#bVolSeite)' opacity='.55'/>")
    o.append(haare(0, 0, 37, 36, 110, 11, "#f4c94f", 1.3, seed=seed, aussen=1.0, richtung=(0, 0)))
    o.append(haare(0, 0, 37, 36, 40, 11, "#fff0ad", 1.1, seed=seed + 9, a0=-160, a1=-20, aussen=1.0, richtung=(0, 0)))
    return "".join(o)


_bz.DEFS_EXTRA.append(
    "<linearGradient id='bVolSeite' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='.4'/><stop offset='.4' stop-color='#fff' stop-opacity='0'/><stop offset='1' stop-color='#1b0f02' stop-opacity='.45'/></linearGradient>"
)


def lupe(cx, cy, r, inhalt, rand="#fff", clip_id=None):
    """Kreisförmiger Ausschnitt (Lupe) mit Schatten und Rand; `inhalt` wird auf den Kreis beschnitten."""
    cid = clip_id or neue_id("lp")
    return (f"<clipPath id='{cid}'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath>"
            f"<circle cx='{cx}' cy='{cy + 3}' r='{r + 2}' fill='#000' opacity='.18' filter='url(#bWeich2)'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#fffdf2'/>"
            f"<g clip-path='url(#{cid})'>{inhalt}</g>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{rand}' stroke-width='5'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r + 2.5}' fill='none' stroke='#14304a' stroke-width='1.6' opacity='.7'/>")


def brust_schnitt():
    """Längsschnitt durch die Brust (lokal, Ursprung = Mitte, etwa 150 × 125): Flugmuskeln, Speiseröhre, Beinansätze, Flügelansätze."""
    o = []
    # Flügelansätze oben
    o.append("<g transform='translate(-18 -52) rotate(-130)'>" + fluegel(60, 26, "vor", .95) + "</g>")
    o.append("<g transform='translate(8 -52) rotate(-96)'>" + fluegel(50, 22, "hinter", .95) + "</g>")
    # Beinansätze unten
    for x, a in ((-38, 12), (0, -4), (38, -16)):
        o.append(f"<g transform='translate({x} 50) rotate({a})'><path d='M-8,0 L8,0 L5,24 L-5,24 Z' fill='#3b2a1c' stroke='#150d06' stroke-width='1.2'/>"
                 f"<path d='M-4,24 L4,24 L2,38 L-2,38 Z' fill='#2a1e14'/></g>")
    # Haut der Brust (Außenring) + Pelz
    o.append(haare(0, 0, 68, 56, 70, 11, "#c88a30", 1.5, seed=71, aussen=1.0, richtung=(0, 0), einwaerts=1))
    o.append(haare(0, 0, 68, 56, 60, 11, "#f4c94f", 1.2, seed=72, aussen=1.0, richtung=(0, 0), einwaerts=1))
    o.append("<ellipse cx='0' cy='0' rx='68' ry='56' fill='#a8691f' stroke='#5a3910' stroke-width='1.4'/>")
    o.append("<ellipse cx='0' cy='0' rx='60' ry='48' fill='url(#bSchnitt)' stroke='#e0b45a' stroke-width='1.6'/>")
    # Muskeln: Längsmuskel (waagerecht) und zwei Hubmuskeln (senkrecht)
    o.append("<path d='M-52,-14 C-44,-38 44,-38 52,-14 C54,2 40,10 0,10 C-40,10 -54,2 -52,-14 Z' fill='url(#bMusk)' stroke='#6e1814' stroke-width='1.4'/>")
    fa = "".join(f"<path d='M-46,{-24 + i * 6.2} C-20,{-30 + i * 6.8} 20,{-30 + i * 6.8} 46,{-24 + i * 6.2}' fill='none' stroke='#f9b0a2' stroke-width='.9' opacity='.55'/>" for i in range(5))
    o.append(fa)
    for x in (-41, 41):
        o.append(f"<path d='M{x - 9},-8 C{x - 11},12 {x - 9},28 {x - 6},40 L{x + 6},40 C{x + 9},28 {x + 11},12 {x + 9},-8 Z' fill='url(#bMuskV)' stroke='#6e1814' stroke-width='1.3'/>")
        o.append("".join(f"<path d='M{x + dx},-4 L{x + dx * .8},38' stroke='#f9b0a2' stroke-width='.8' opacity='.6'/>" for dx in (-4, 0, 4)))
    # Speiseröhre
    o.append("<path d='M-58,28 C-30,24 -10,34 10,30 C34,26 46,34 60,30' fill='none' stroke='#b4607a' stroke-width='7.4' stroke-linecap='round'/>"
             "<path d='M-58,28 C-30,24 -10,34 10,30 C34,26 46,34 60,30' fill='none' stroke='url(#bDarmRosa)' stroke-width='5' stroke-linecap='round'/>")
    return "".join(o)
