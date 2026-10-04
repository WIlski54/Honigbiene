"""Zeichen-Bibliothek für die Schaubilder des Reiters „Das Bienenvolk“ (grafiken_volk.py).

Baut auf svg_helfer.py auf (nicht ändern) und liefert, was dort fehlt:

  * Bienen von oben (Arbeiterin, Königin, Drohne) und von der Seite als wiederverwendbare <g>-Bausteine in <defs>,
    benutzt per <use> – so bleiben auch wimmelnde Bilder klein (Dateigröße < 60 KB).
  * Wabenzellen (sechseckig, Spitze oben) als Muster (Hintergrund) und als Einzelbausteine (Honig, Pollen, Deckel, Brut).
  * Wabe-Raster mit Zellkoordinaten, Rähmchen, Bienenkasten im Querschnitt, Pfeil-Schilder.

Koordinaten der Bienen: Kopf oben, Hinterleib unten, Mitte der Brust bei (0, -19); eine Arbeiterin ist etwa 106 Einheiten lang.
Mit `biene_o(art, x, y, winkel, groesse)`: Winkel in Grad, 0 = Kopf zeigt nach oben, 90 = Kopf zeigt nach rechts.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_helfer import *  # noqa: F401,F403  (Farben, t, pfeil, svg, erzeuge, …)
from svg_helfer import _mk  # noqa: F401

SQ3 = math.sqrt(3)

# ═══════════════════════════════════════════════════════════════════════════
#  Farben und Verläufe
# ═══════════════════════════════════════════════════════════════════════════
DUNKELBRAUN = "#3a281a"
VERLAEUFE_VOLK = (
    # Körper der Biene
    "<radialGradient id='gaBrust' cx='.45' cy='.38' r='.7'><stop offset='0' stop-color='#f7da82'/><stop offset='.55' stop-color='#c98f2c'/><stop offset='1' stop-color='#7a4c12'/></radialGradient>"
    "<radialGradient id='gaBrustD' cx='.45' cy='.38' r='.7'><stop offset='0' stop-color='#a07a48'/><stop offset='.55' stop-color='#6a4a28'/><stop offset='1' stop-color='#2c1f12'/></radialGradient>"
    "<radialGradient id='gaBrustK' cx='.45' cy='.38' r='.7'><stop offset='0' stop-color='#fbe39a'/><stop offset='.5' stop-color='#d99a34'/><stop offset='1' stop-color='#8a5614'/></radialGradient>"
    "<linearGradient id='gaHinter' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#a56e18'/><stop offset='.32' stop-color='#f8cd55'/><stop offset='.62' stop-color='#e3a82b'/><stop offset='1' stop-color='#94620f'/></linearGradient>"
    "<linearGradient id='gaHinterK' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#a85f14'/><stop offset='.32' stop-color='#f6b650'/><stop offset='.62' stop-color='#e08f2b'/><stop offset='1' stop-color='#8f520e'/></linearGradient>"
    "<linearGradient id='gaHinterD' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#241810'/><stop offset='.35' stop-color='#6b4b2a'/><stop offset='.65' stop-color='#4a3320'/><stop offset='1' stop-color='#1e140c'/></linearGradient>"
    "<linearGradient id='gaBand' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#120b06'/><stop offset='.4' stop-color='#4a3323'/><stop offset='1' stop-color='#120b06'/></linearGradient>"
    "<radialGradient id='gaAuge' cx='.38' cy='.32' r='.75'><stop offset='0' stop-color='#6a5444'/><stop offset='.5' stop-color='#2b2019'/><stop offset='1' stop-color='#0c0705'/></radialGradient>"
    "<linearGradient id='gaFluegel' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='.85'/><stop offset='1' stop-color='#c9e3f5' stop-opacity='.5'/></linearGradient>"
    "<radialGradient id='gaPunkt' cx='.35' cy='.3' r='.8'><stop offset='0' stop-color='#ff8a7a'/><stop offset='.6' stop-color='#e02424'/><stop offset='1' stop-color='#8e1010'/></radialGradient>"
    # Wabe, Zellen, Honig, Pollen
    "<radialGradient id='gzTiefe' cx='.62' cy='.68' r='.9'><stop offset='0' stop-color='#e9bd58'/><stop offset='.6' stop-color='#b97d1b'/><stop offset='1' stop-color='#7a4a0c'/></radialGradient>"
    "<linearGradient id='gzRand' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#fff2bd'/><stop offset='1' stop-color='#e3b94e'/></linearGradient>"
    "<radialGradient id='gzHonig' cx='.38' cy='.32' r='.85'><stop offset='0' stop-color='#ffe27a'/><stop offset='.55' stop-color='#f3a91a'/><stop offset='1' stop-color='#c36d06'/></radialGradient>"
    "<radialGradient id='gzDeckel' cx='.4' cy='.34' r='.85'><stop offset='0' stop-color='#fffbe6'/><stop offset='.7' stop-color='#f6e4a5'/><stop offset='1' stop-color='#dcbc62'/></radialGradient>"
    "<radialGradient id='gzBrut' cx='.4' cy='.34' r='.85'><stop offset='0' stop-color='#d9ad6c'/><stop offset='.7' stop-color='#b78840'/><stop offset='1' stop-color='#8c5f22'/></radialGradient>"
    "<radialGradient id='gzPollen' cx='.4' cy='.34' r='.85'><stop offset='0' stop-color='#ffc84a'/><stop offset='.7' stop-color='#ec8a1a'/><stop offset='1' stop-color='#b4560c'/></radialGradient>"
    "<linearGradient id='gRaehm' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#e2bb82'/><stop offset='.5' stop-color='#cf9a58'/><stop offset='1' stop-color='#a8743c'/></linearGradient>"
    "<linearGradient id='gRaehmQ' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e2bb82'/><stop offset='.5' stop-color='#cf9a58'/><stop offset='1' stop-color='#a8743c'/></linearGradient>"
    "<radialGradient id='gStockDunkel' cx='.5' cy='.5' r='.75'><stop offset='0' stop-color='#6d4318'/><stop offset='.7' stop-color='#4a2c10'/><stop offset='1' stop-color='#25140a'/></radialGradient>"
    # bemalter Bienenkasten: Honigraum senfgelb, Brutraum petrolgrün, Dach korall, Boden Holz
    "<linearGradient id='gkHonig' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#f6c94c'/><stop offset='.55' stop-color='#e7ae2c'/><stop offset='1' stop-color='#c58d17'/></linearGradient>"
    "<linearGradient id='gkBrut' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#46a6aa'/><stop offset='.55' stop-color='#2f8589'/><stop offset='1' stop-color='#1f6064'/></linearGradient>"
    "<linearGradient id='gkDach' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ef8878'/><stop offset='1' stop-color='#c35644'/></linearGradient>"
    "<linearGradient id='gkBoden' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d3a56b'/><stop offset='1' stop-color='#9a6a35'/></linearGradient>"
    "<linearGradient id='gkInnen' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#000' stop-opacity='.55'/><stop offset='.12' stop-color='#000' stop-opacity='0'/><stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.55'/></linearGradient>"
)


def _kreis_punkte(n, seed):
    r = random.Random(seed)
    return [(r.uniform(0, 2 * math.pi), math.sqrt(r.random()), r.random()) for _ in range(n)]


def _fell(cx, cy, rx, ry, n, seed, hell="#f9e29a", dunkel="#6c420f", laenge=4.2, breite=.85, rueck=.6):
    """Kurze Haarstriche auf einer Ellipse (Pelz der Brust). Richtung: von der Mitte nach außen, leicht nach hinten."""
    hell_d, dunkel_d = [], []
    for a, d, k in _kreis_punkte(n, seed):
        x, y = cx + math.cos(a) * rx * d * .93, cy + math.sin(a) * ry * d * .93
        dx, dy = (x - cx) / rx * laenge * .75, ((y - cy) / ry * .6 + rueck) * laenge
        (hell_d if k > .35 else dunkel_d).append(f"M{x:.0f} {y:.0f}l{dx:.1f} {dy:.1f}")
    return (f"<path d='{''.join(hell_d)}' stroke='{hell}' stroke-width='{breite}' stroke-linecap='round' opacity='.75' fill='none'/>"
            f"<path d='{''.join(dunkel_d)}' stroke='{dunkel}' stroke-width='{breite}' stroke-linecap='round' opacity='.55' fill='none'/>")


def _sym(s):
    """Rechte Hälfte `s` plus an der Mittelachse gespiegelte linke Hälfte."""
    return s + f"<g transform='scale(-1 1)'>{s}</g>"


def _bein(punkte, w=2.3, farbe=DUNKELBRAUN):
    d = "M" + " L".join(f"{x},{y}" for x, y in punkte)
    fuss = punkte[-1]
    return (f"<path d='{d}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<circle cx='{punkte[1][0]}' cy='{punkte[1][1]}' r='{w * .62:.1f}' fill='#5b4330'/>"
            f"<path d='M{fuss[0]},{fuss[1]} l1.6,2.4 M{fuss[0]},{fuss[1]} l-1.4,2.6' stroke='{farbe}' stroke-width='.9' stroke-linecap='round'/>")


def _fluegel(cx, cy, rx, ry, rot, adern=True, op=1.0):
    """Ein Flügel (rechte Seite), Mittelpunkt (cx, cy), lange Achse nach unten, um `rot` Grad gedreht."""
    out = (f"<g transform='rotate({rot} {cx} {cy})' opacity='{op}'>"
           f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='url(#gaFluegel)' stroke='#8fb4cf' stroke-width='.9'/>")
    if adern:
        out += (f"<path d='M{cx - rx * .55:.1f},{cy - ry * .9:.1f} Q{cx - rx * .2:.1f},{cy:.1f} {cx + rx * .1:.1f},{cy + ry * .85:.1f}' "
                f"stroke='#8fb4cf' stroke-width='.7' fill='none'/>"
                f"<path d='M{cx - rx * .55:.1f},{cy - ry * .1:.1f} Q{cx:.1f},{cy + ry * .05:.1f} {cx + rx * .8:.1f},{cy + ry * .15:.1f}' "
                f"stroke='#8fb4cf' stroke-width='.6' fill='none'/>"
                f"<ellipse cx='{cx - rx * .3:.1f}' cy='{cy - ry * .35:.1f}' rx='{rx * .22:.1f}' ry='{ry * .35:.1f}' fill='#fff' opacity='.45'/>")
    return out + "</g>"


# ═══════════════════════════════════════════════════════════════════════════
#  Bienen von oben
# ═══════════════════════════════════════════════════════════════════════════
def _arbeiterin():
    hint = "M-8,-4 C-17,6 -17,30 -6,46 Q0,55 6,46 C17,30 17,6 8,-4 Z"
    legs = _sym(_bein([(11, -27), (25, -36), (29, -26)]) + _bein([(14, -18), (30, -19), (35, -8)]) +
                _bein([(12, -10), (26, -4), (29, 12)], 2.6))
    bands = "".join(
        f"<path d='M-20,{y} Q0,{y + 7} 20,{y} L20,{y + h} Q0,{y + h + 7} -20,{y + h} Z' fill='url(#gaBand)'/>"
        for y, h in ((12, 5.5), (25, 6), (37, 6.5)))
    fuzz_abd = "".join(
        f"<path d='M{x},{y} l{dx},{dy}' stroke='#fbe9b0' stroke-width='.8' stroke-linecap='round' opacity='.65'/>"
        for x, y, dx, dy in ((-12, 8, -2, 1.5), (12, 8, 2, 1.5), (-14, 22, -2, 1.5), (14, 22, 2, 1.5),
                              (-12, 35, -2, 1.5), (12, 35, 2, 1.5), (-8, 3, -1.5, 2), (8, 3, 1.5, 2)))
    wings = _sym(_fluegel(14, 8, 5.6, 28, -12, op=.9) + _fluegel(17, 11, 7.4, 37, -19))     # Flügel reichen bis zum Hinterleibsende
    kopf = ("<path d='M-12,-44 Q-12,-55 0,-55 Q12,-55 12,-44 Q12,-32 0,-30.5 Q-12,-32 -12,-44 Z' fill='#4a3424'/>"
            "<path d='M-6,-36 Q0,-31 6,-36 L5,-31 Q0,-28.5 -5,-31 Z' fill='#b58a52'/>"
            + _sym("<ellipse cx='9.6' cy='-44' rx='5.6' ry='9.8' transform='rotate(-8 9.6 -44)' fill='url(#gaAuge)' stroke='#120b06' stroke-width='.6'/>"
                   "<ellipse cx='8.2' cy='-48' rx='1.5' ry='2.6' fill='#fff' opacity='.55' transform='rotate(-8 8.2 -48)'/>")
            + "<circle cx='-2.8' cy='-50.5' r='1.2' fill='#cbb79c'/><circle cx='2.8' cy='-50.5' r='1.2' fill='#cbb79c'/><circle cx='0' cy='-46.8' r='1.2' fill='#cbb79c'/>")
    fuehler = _sym("<path d='M3.4,-54 L7,-62 Q9,-66 14,-68 L19,-75' fill='none' stroke='#2c1d12' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/>"
                   "<circle cx='7' cy='-62' r='1.2' fill='#2c1d12'/>")
    return ("<g id='bA' filter='url(#fSchatten)'>" + legs +
            f"<path d='{hint}' fill='url(#gaHinter)'/><g clip-path='url(#cpA)'>{bands}"
            "<path d='M-20,45 Q0,53 20,45 V60 H-20 Z' fill='url(#gaBand)'/>"
            f"<ellipse cx='-6' cy='20' rx='3' ry='16' fill='#fff' opacity='.28'/>{fuzz_abd}</g>"
            f"<path d='{hint}' fill='none' stroke='#5a3a10' stroke-width='.8' opacity='.7'/>"
            "<path d='M-1.6,52 L0,61 L1.6,52 Z' fill='#2b1a0e'/>"
            + wings +
            "<ellipse cx='0' cy='-19' rx='15.5' ry='14.5' fill='url(#gaBrust)'/>"
            + _fell(0, -19, 15.5, 14.5, 42, 7) +
            "<path d='M-8,-9 Q0,-4 8,-9' stroke='#3a2410' stroke-width='1.4' fill='none' stroke-linecap='round' opacity='.7'/>"
            + kopf + fuehler + "</g>")


def _koenigin():
    hint = "M-8,-4 C-15,10 -14,40 -5,62 Q0,77 5,62 C14,40 15,10 8,-4 Z"
    legs = _sym(_bein([(11, -27), (26, -37), (30, -26)]) + _bein([(14, -18), (31, -20), (37, -7)]) +
                _bein([(12, -10), (28, -3), (31, 16)], 2.5))
    bands = "".join(
        f"<path d='M-20,{y} Q0,{y + 6} 20,{y} L20,{y + h} Q0,{y + h + 6} -20,{y + h} Z' fill='#5a3a1c' opacity='.8'/>"
        for y, h in ((19, 2.6), (30, 2.8), (41, 3), (52, 3.2), (63, 3.4)))
    wings = _sym(_fluegel(13, -1, 5.0, 17, -12, op=.9) + _fluegel(15, 0, 6.6, 23, -16))
    kopf = ("<path d='M-11.5,-43 Q-11.5,-54 0,-54 Q11.5,-54 11.5,-43 Q11.5,-31 0,-29.5 Q-11.5,-31 -11.5,-43 Z' fill='#4a3424'/>"
            "<path d='M-6,-35 Q0,-30 6,-35 L5,-30 Q0,-27.5 -5,-30 Z' fill='#b58a52'/>"
            + _sym("<ellipse cx='8.6' cy='-43' rx='4.7' ry='8.4' transform='rotate(-6 8.6 -43)' fill='url(#gaAuge)' stroke='#120b06' stroke-width='.6'/>"
                   "<ellipse cx='7.4' cy='-46.5' rx='1.3' ry='2.3' fill='#fff' opacity='.55'/>")
            + "<circle cx='-2.6' cy='-49.5' r='1.15' fill='#cbb79c'/><circle cx='2.6' cy='-49.5' r='1.15' fill='#cbb79c'/><circle cx='0' cy='-46' r='1.15' fill='#cbb79c'/>")
    fuehler = _sym("<path d='M3.2,-53 L7,-61 Q9,-65 13,-67 L17,-73' fill='none' stroke='#2c1d12' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/>"
                   "<circle cx='7' cy='-61' r='1.1' fill='#2c1d12'/>")
    return ("<g id='bK' filter='url(#fSchatten)'>" + legs +
            f"<path d='{hint}' fill='url(#gaHinterK)'/><g clip-path='url(#cpK)'>{bands}"
            "<path d='M-20,70 Q0,80 20,70 V90 H-20 Z' fill='#6b421c' opacity='.85'/>"
            "<ellipse cx='-5' cy='30' rx='2.6' ry='26' fill='#fff' opacity='.3'/></g>"
            f"<path d='{hint}' fill='none' stroke='#6a3c0c' stroke-width='.8' opacity='.7'/>"
            "<path d='M-1.5,74 L0,82 L1.5,74 Z' fill='#2b1a0e'/>"
            + wings +
            "<ellipse cx='0' cy='-19' rx='14.5' ry='13.5' fill='url(#gaBrustK)'/>"
            + _fell(0, -19, 14.5, 13.5, 22, 11, laenge=3.2) +
            "<circle cx='0' cy='-18.5' r='5.2' fill='#fff' opacity='.9'/><circle cx='0' cy='-18.5' r='4.4' fill='url(#gaPunkt)'/>"
            "<circle cx='-1.4' cy='-20' r='1.3' fill='#fff' opacity='.7'/>"
            + kopf + fuehler + "</g>")


def _drohne():
    hint = "M-11,-4 C-25,6 -25,30 -12,43 Q0,52 12,43 C25,30 25,6 11,-4 Z"
    legs = _sym(_bein([(14, -27), (30, -36), (34, -25)], 2.8) + _bein([(18, -18), (36, -19), (41, -7)], 2.8) +
                _bein([(15, -9), (31, -3), (34, 13)], 3))
    bands = "".join(
        f"<path d='M-30,{y} Q0,{y + 8} 30,{y} L30,{y + h} Q0,{y + h + 8} -30,{y + h} Z' fill='#9c7432' opacity='.85'/>"
        for y, h in ((10, 3.2), (22, 3.6), (33, 4)))
    fuzz = "".join(
        f"<path d='M{x},{y} l{dx},{dy}' stroke='#d9b36c' stroke-width='.9' stroke-linecap='round' opacity='.6'/>"
        for x, y, dx, dy in ((-20, 10, -2.4, 1.4), (20, 10, 2.4, 1.4), (-22, 22, -2.4, 1.4), (22, 22, 2.4, 1.4),
                              (-19, 34, -2.4, 1.4), (19, 34, 2.4, 1.4), (-10, 44, -1.5, 2), (10, 44, 1.5, 2), (-14, 0, -2, 1.5), (14, 0, 2, 1.5)))
    wings = _sym(_fluegel(21, 8, 7.0, 40, -12, op=.9) + _fluegel(26, 10, 10.0, 49, -17))
    kopf = ("<path d='M-17,-44 Q-17,-58 0,-58 Q17,-58 17,-44 Q17,-32 0,-30 Q-17,-32 -17,-44 Z' fill='#3a281a'/>"
            + _sym("<ellipse cx='10.5' cy='-45' rx='11' ry='13.2' transform='rotate(-5 10.5 -45)' fill='url(#gaAuge)' stroke='#120b06' stroke-width='.7'/>"
                   "<ellipse cx='7.6' cy='-50.5' rx='2.4' ry='4' fill='#fff' opacity='.5' transform='rotate(-10 7.6 -50.5)'/>")
            + "<path d='M-6,-35 Q0,-30 6,-35 L5,-30.5 Q0,-28.5 -5,-30.5 Z' fill='#8d6a3e'/>")
    fuehler = _sym("<path d='M4,-54 L9,-64 Q12,-69 18,-71 L25,-79' fill='none' stroke='#2c1d12' stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round'/>"
                   "<circle cx='9' cy='-64' r='1.3' fill='#2c1d12'/>")
    return ("<g id='bD' filter='url(#fSchatten)'>" + legs +
            f"<path d='{hint}' fill='url(#gaHinterD)'/><g clip-path='url(#cpD)'>{bands}{fuzz}"
            "<ellipse cx='-8' cy='20' rx='4' ry='17' fill='#fff' opacity='.16'/></g>"
            f"<path d='{hint}' fill='none' stroke='#120b06' stroke-width='.8' opacity='.8'/>"
            + wings +
            "<ellipse cx='0' cy='-20' rx='21.5' ry='18.5' fill='url(#gaBrustD)'/>"
            + _fell(0, -20, 21.5, 18.5, 60, 21, hell="#cdb089", dunkel="#241709", laenge=5, breite=1.0) +
            "<path d='M-11,-8 Q0,-3 11,-8' stroke='#241709' stroke-width='1.6' fill='none' stroke-linecap='round' opacity='.7'/>"
            + kopf + fuehler + "</g>")


# ═══════════════════════════════════════════════════════════════════════════
#  Biene von der Seite (Flug, Flugloch); Blick nach rechts
# ═══════════════════════════════════════════════════════════════════════════
def _seite():
    stre = "".join(f"<path d='M{x},-11 Q{x + 3},0 {x},11' fill='none' stroke='#2a1c10' stroke-width='3.6' stroke-linecap='round'/>" for x in (-26, -16, -7))
    fuzz = "".join(f"<path d='M{x},{y} l2.6,1.4' stroke='#f9e29a' stroke-width='.9' stroke-linecap='round' opacity='.7'/>"
                   for x, y in ((6, -8), (9, -3), (4, 2), (11, 4), (13, -7), (8, 7), (15, 0), (2, -4), (12, -10)))
    return ("<g id='bS' filter='url(#fSchatten)'>"
            "<path d='M-6,10 L-13,20 M2,12 L-1,23 M10,10 L15,20' stroke='#3a281a' stroke-width='2.2' stroke-linecap='round' fill='none'/>"
            "<g transform='rotate(-62 6 -8)'><ellipse cx='6' cy='-8' rx='8' ry='19' fill='url(#gaFluegel)' stroke='#8fb4cf' stroke-width='.9' opacity='.9'/></g>"
            "<g transform='rotate(-38 6 -8)'><ellipse cx='6' cy='-8' rx='8.6' ry='23' fill='url(#gaFluegel)' stroke='#8fb4cf' stroke-width='.9'/></g>"
            "<path d='M-8,-9 C-24,-14 -42,-8 -46,2 C-42,12 -26,13 -8,9 Z' fill='url(#gaHinter)' stroke='#5a3a10' stroke-width='.8'/>"
            "<clipPath id='cpS'><path d='M-8,-9 C-24,-14 -42,-8 -46,2 C-42,12 -26,13 -8,9 Z'/></clipPath>"
            f"<g clip-path='url(#cpS)'>{stre}</g>"
            "<path d='M-46,2 L-52,4 L-46,5 Z' fill='#2b1a0e'/>"
            "<ellipse cx='7' cy='-1' rx='13' ry='12' fill='url(#gaBrust)'/>" + fuzz +
            "<ellipse cx='27' cy='1' rx='8.4' ry='8.8' fill='#4a3424'/>"
            "<ellipse cx='28.4' cy='-1.5' rx='5.2' ry='6.4' fill='url(#gaAuge)' stroke='#120b06' stroke-width='.5'/>"
            "<ellipse cx='27' cy='-4.4' rx='1.4' ry='2' fill='#fff' opacity='.6'/>"
            "<path d='M33,3 Q38,6 37,10' stroke='#b58a52' stroke-width='2' fill='none' stroke-linecap='round'/>"
            "<path d='M31,-6 Q37,-14 44,-12' stroke='#2c1d12' stroke-width='1.5' fill='none' stroke-linecap='round'/>"
            "</g>")


# ═══════════════════════════════════════════════════════════════════════════
#  Wabenzellen (Spitze oben): Bausteine mit r = 10
# ═══════════════════════════════════════════════════════════════════════════
def _hex_pts(cx, cy, r):
    return " ".join(f"{cx + r * math.cos(-math.pi / 2 + i * math.pi / 3):.2f},{cy + r * math.sin(-math.pi / 2 + i * math.pi / 3):.2f}" for i in range(6))


def _zelle_leer(x=0, y=0, r=10):
    return (f"<polygon points='{_hex_pts(x, y, r)}' fill='url(#gzRand)' stroke='#c08a25' stroke-width='.9' stroke-linejoin='round'/>"
            f"<polygon points='{_hex_pts(x, y, r * .72)}' fill='url(#gzTiefe)' stroke='#8a5410' stroke-width='.7' stroke-linejoin='round'/>"
            f"<path d='M{x - r * .55:.1f},{y - r * .35:.1f} L{x:.1f},{y - r * .7:.1f} L{x + r * .55:.1f},{y - r * .35:.1f}' fill='none' stroke='#4a2c08' stroke-width='.9' opacity='.45' stroke-linecap='round'/>")


def _zelle_honig(r=10):
    return (f"<polygon points='{_hex_pts(0, 0, r)}' fill='url(#gzRand)' stroke='#c08a25' stroke-width='.9' stroke-linejoin='round'/>"
            f"<polygon points='{_hex_pts(0, 0, r * .8)}' fill='url(#gzHonig)' stroke='#b36a05' stroke-width='.6' stroke-linejoin='round'/>"
            f"<ellipse cx='-2.4' cy='-3' rx='2.6' ry='1.5' fill='#fff' opacity='.7' transform='rotate(-30 -2.4 -3)'/>")


def _zelle_deckel(r=10, honig=True):
    """Verdeckelte Zelle: Honig = helles Wachs, Brut = braun und porös."""
    if honig:
        return (f"<polygon points='{_hex_pts(0, 0, r)}' fill='url(#gzRand)' stroke='#c08a25' stroke-width='.9' stroke-linejoin='round'/>"
                f"<polygon points='{_hex_pts(0, 0, r * .86)}' fill='url(#gzDeckel)' stroke='#c9a24a' stroke-width='.6' stroke-linejoin='round'/>"
                f"<circle cx='0' cy='0' r='{r * .45:.1f}' fill='none' stroke='#fff' stroke-width='.8' opacity='.55'/>")
    return (f"<polygon points='{_hex_pts(0, 0, r)}' fill='url(#gzRand)' stroke='#c08a25' stroke-width='.9' stroke-linejoin='round'/>"
            f"<polygon points='{_hex_pts(0, 0, r * .86)}' fill='url(#gzBrut)' stroke='#8c5f22' stroke-width='.6' stroke-linejoin='round'/>"
            f"<circle cx='0' cy='0' r='{r * .13:.1f}' fill='#6d4716' opacity='.7'/>"
            f"<ellipse cx='-2' cy='-3' rx='2.4' ry='1.2' fill='#fff' opacity='.28' transform='rotate(-30 -2 -3)'/>")


def _zelle_pollen(r=10):
    return (f"<polygon points='{_hex_pts(0, 0, r)}' fill='url(#gzRand)' stroke='#c08a25' stroke-width='.9' stroke-linejoin='round'/>"
            f"<polygon points='{_hex_pts(0, 0, r * .8)}' fill='url(#gzPollen)' stroke='#9a4b08' stroke-width='.6' stroke-linejoin='round'/>"
            "<circle cx='-3' cy='-2.6' r='2.1' fill='#ffe066'/><circle cx='1.8' cy='-3.6' r='1.7' fill='#f08a1c'/>"
            "<circle cx='3.4' cy='.6' r='1.9' fill='#fff1a8'/><circle cx='-.4' cy='.4' r='1.9' fill='#c4532a'/>"
            "<circle cx='-3.6' cy='2' r='1.6' fill='#f7b733'/><circle cx='1.2' cy='3.8' r='1.9' fill='#ffe066'/>"
            "<circle cx='-1.8' cy='-3.6' r='.6' fill='#fff' opacity='.8'/><circle cx='3.4' cy='3' r='1.1' fill='#e07a18'/>")


def _zellen_defs():
    return ("<g id='zL'>" + _zelle_leer() + "</g><g id='zH'>" + _zelle_honig() + "</g>"
            "<g id='zD'>" + _zelle_deckel(honig=True) + "</g><g id='zB'>" + _zelle_deckel(honig=False) + "</g>"
            "<g id='zP'>" + _zelle_pollen() + "</g>")


def muster_wabe(pid, r, px=0, py=0):
    """Wabenmuster (leere Zellen) als <pattern>. Zelle (c, z) liegt bei Wabe(px, py, r).pos(c, z)."""
    dx = SQ3 * r
    zellen = [(dx / 2, r), (0, 2.5 * r), (dx, 2.5 * r), (0, -0.5 * r), (dx, -0.5 * r)]
    inhalt = "".join(_zelle_leer(cx, cy, r) for cx, cy in zellen)
    return (f"<pattern id='{pid}' x='{px:.2f}' y='{py:.2f}' width='{dx:.3f}' height='{3 * r}' patternUnits='userSpaceOnUse'>"
            f"{inhalt}</pattern>")


class Wabe:
    """Raster aus sechseckigen Zellen (Spitze oben). Zelle (c, z): Spalte c, Zeile z; ungerade Zeilen sind halb versetzt.
    Passt zu muster_wabe(pid, r, px, py), wenn dieselben Werte benutzt werden."""

    def __init__(self, px, py, r):
        self.px, self.py, self.r = px, py, r
        self.dx = SQ3 * r

    def pos(self, c, z):
        return (self.px + self.dx / 2 + c * self.dx + (self.dx / 2 if z % 2 else 0), self.py + self.r + z * 1.5 * self.r)

    def zelle(self, art, c, z):
        """Baustein-Zelle ('L' leer, 'H' Honig, 'D' Deckel Honig, 'B' Brut verdeckelt, 'P' Pollen) als <use>."""
        x, y = self.pos(c, z)
        return f"<use href='#z{art}' transform='translate({x:.1f} {y:.1f}) scale({self.r / 10:.3f})'/>"

    def lokal(self, art, c, z):
        """Wie zelle(), aber in Einheiten mit r = 10 relativ zum Ursprung (px, py) – für eine Gruppe
        <g transform='translate(px py) scale(r/10)'>. Spart Platz (x/y statt transform)."""
        dx0 = SQ3 * 10
        x = dx0 / 2 + c * dx0 + (dx0 / 2 if z % 2 else 0)
        return f"<use href='#z{art}' x='{x:.1f}' y='{10 + z * 15}'/>"

    def gruppe(self, zellen):
        """Zellen aus lokal() in die Gruppe mit passender Transformation setzen."""
        return f"<g transform='translate({self.px:.1f} {self.py:.1f}) scale({self.r / 10:.3f})'>{''.join(zellen)}</g>"

    def nahe(self, x, y):
        """Zelle (c, z), deren Mittelpunkt (x, y) am nächsten liegt."""
        best = None
        for z in range(int((y - self.py) / (1.5 * self.r)) - 2, int((y - self.py) / (1.5 * self.r)) + 3):
            for c in range(int((x - self.px) / self.dx) - 2, int((x - self.px) / self.dx) + 3):
                cx, cy = self.pos(c, z)
                d = (cx - x) ** 2 + (cy - y) ** 2
                if best is None or d < best[0]:
                    best = (d, c, z)
        return best[1], best[2]


# ═══════════════════════════════════════════════════════════════════════════
#  defs, Verwendung
# ═══════════════════════════════════════════════════════════════════════════
def defs_volk(extra="", bausteine="AKDSZ"):
    """Gemeinsame Bausteine (Verläufe, Bienen, Zellen, Clip-Pfade) als defs_extra für svg().
    `bausteine`: nur die gebrauchten Teile einbauen (Dateigröße!): A Arbeiterin, K Königin, D Drohne, S Seitenansicht, Z Zellen."""
    clips = {
        "A": "<clipPath id='cpA'><path d='M-8,-4 C-17,6 -17,30 -6,46 Q0,55 6,46 C17,30 17,6 8,-4 Z'/></clipPath>",
        "K": "<clipPath id='cpK'><path d='M-8,-4 C-15,10 -14,40 -5,62 Q0,77 5,62 C14,40 15,10 8,-4 Z'/></clipPath>",
        "D": "<clipPath id='cpD'><path d='M-11,-4 C-25,6 -25,30 -12,43 Q0,52 12,43 C25,30 25,6 11,-4 Z'/></clipPath>",
    }
    teile = {"A": _arbeiterin, "K": _koenigin, "D": _drohne, "S": _seite, "Z": _zellen_defs}
    out = VERLAEUFE_VOLK
    for k in "AKDSZ":
        if k in bausteine:
            out += clips.get(k, "") + teile[k]()
    return out + extra


def biene_o(art, x, y, winkel=0, groesse=1.0, schatten=True):
    """Biene von oben. art: 'A' Arbeiterin, 'K' Königin, 'D' Drohne. Winkel in Grad (0 = Kopf oben, 90 = Kopf rechts)."""
    return f"<use href='#b{art}' transform='translate({x:.1f} {y:.1f}) rotate({winkel:.0f}) scale({groesse:.3f})'/>"


def biene_s(x, y, groesse=1.0, spiegeln=False, winkel=0):
    """Biene von der Seite (Blick nach rechts, spiegeln = nach links)."""
    sx = -groesse if spiegeln else groesse
    return f"<use href='#bS' transform='translate({x:.1f} {y:.1f}) rotate({winkel:.0f}) scale({sx:.3f} {groesse:.3f})'/>"


def volk_svg(titel, *teile, w=W, h=H, extra="", grund="url(#gHimmel)", rahmen=True, bausteine="AKDSZ"):
    """svg() mit den Bausteinen dieses Reiters."""
    return svg(titel, *teile, w=w, h=h, defs_extra=defs_volk(extra, bausteine), grund=grund, rahmen=rahmen)
