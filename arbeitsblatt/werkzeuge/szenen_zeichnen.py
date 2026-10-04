"""Gegenstände und Tiere für die Szenen des Reiters „Nutztier Biene“ (nutztier-1 … 4, imker-karte, glossar-bienenkasten).

Jedes Objekt: `name(x, y, s, …)` mit x = Mitte, y = Boden (Standlinie), s = Maßstab (1 ≈ Größe in der Beschreibung).
Alle Grafiken nutzen die gemeinsamen Verläufe aus svg_helfer.py und DEFS_BIENE (bienen_zeichnen.py).
"""
import math
import random

from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz
import bienen_innen  # noqa: F401  (registriert den Verlauf bVolSeite)

_bz.DEFS_EXTRA.append(
    "<linearGradient id='sKuhFell' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff'/><stop offset='1' stop-color='#dfe5ec'/></linearGradient>"
    "<linearGradient id='sWolle' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffffff'/><stop offset='1' stop-color='#d9d4c6'/></linearGradient>"
    "<linearGradient id='sScheune' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#c8493a'/><stop offset='1' stop-color='#9a2f26'/></linearGradient>"
    "<linearGradient id='sDach' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#7b5a4a'/><stop offset='1' stop-color='#4a342b'/></linearGradient>"
    "<linearGradient id='sBlech' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e3e8ec'/><stop offset='.5' stop-color='#b4bdc6'/><stop offset='1' stop-color='#7d8792'/></linearGradient>"
    "<linearGradient id='sMetall' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#6f7983'/><stop offset='.35' stop-color='#d3dae0'/><stop offset='.7' stop-color='#98a2ac'/><stop offset='1' stop-color='#5d6670'/></linearGradient>"
    "<linearGradient id='sLeder' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#7a4a24'/><stop offset='.5' stop-color='#b27a45'/><stop offset='1' stop-color='#6a3f1d'/></linearGradient>"
    "<linearGradient id='sAnzug' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#ffffff'/><stop offset='.55' stop-color='#f1eee2'/><stop offset='1' stop-color='#cdc8b4'/></linearGradient>"
    "<linearGradient id='sHut' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#f6edd0'/><stop offset='1' stop-color='#d6c897'/></linearGradient>"
    "<linearGradient id='sGlas' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#ffffff' stop-opacity='.65'/><stop offset='.25' stop-color='#ffffff' stop-opacity='.05'/><stop offset='.8' stop-color='#ffffff' stop-opacity='0'/><stop offset='1' stop-color='#ffffff' stop-opacity='.4'/></linearGradient>"
    "<linearGradient id='sKerze' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#e8c15a'/><stop offset='.35' stop-color='#fff2b6'/><stop offset='1' stop-color='#d9a93c'/></linearGradient>"
    "<radialGradient id='sFlamme' cx='.5' cy='.7' r='.7'><stop offset='0' stop-color='#fff8d0'/><stop offset='.45' stop-color='#ffc93a'/><stop offset='1' stop-color='#ff7a1a'/></radialGradient>"
    "<radialGradient id='sFlammenGlanz' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#ffe9a0' stop-opacity='.8'/><stop offset='1' stop-color='#ffe9a0' stop-opacity='0'/></radialGradient>"
    "<radialGradient id='sApfel' cx='.35' cy='.3' r='.9'><stop offset='0' stop-color='#ff8a6b'/><stop offset='.5' stop-color='#d62f25'/><stop offset='1' stop-color='#8e1712'/></radialGradient>"
    "<radialGradient id='sApfelG' cx='.35' cy='.3' r='.9'><stop offset='0' stop-color='#f8f089'/><stop offset='.5' stop-color='#e2b72a'/><stop offset='1' stop-color='#b3801a'/></radialGradient>"
    "<radialGradient id='sRauch' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#f4f5f6' stop-opacity='.95'/><stop offset='1' stop-color='#b9c0c6' stop-opacity='.55'/></radialGradient>"
    "<linearGradient id='sHolzD' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#c79a62'/><stop offset='1' stop-color='#8a5d30'/></linearGradient>"
    "<pattern id='sNetz' patternUnits='userSpaceOnUse' width='2.4' height='2.4'><path d='M0,0 H2.4 M0,0 V2.4' stroke='#1d2a30' stroke-width='.35' opacity='.6'/></pattern>"
    "<pattern id='sWabe' patternUnits='userSpaceOnUse' width='13.86' height='24'><g fill='#f1b629' stroke='#b57f10' stroke-width='1.1'>"
    "<polygon points='6.93,0 13.86,4 13.86,12 6.93,16 0,12 0,4' transform='translate(0 -4)'/><polygon points='6.93,0 13.86,4 13.86,12 6.93,16 0,12 0,4' transform='translate(0 8)'/>"
    "<polygon points='6.93,0 13.86,4 13.86,12 6.93,16 0,12 0,4' transform='translate(-6.93 2)'/><polygon points='6.93,0 13.86,4 13.86,12 6.93,16 0,12 0,4' transform='translate(6.93 2)'/>"
    "<polygon points='6.93,0 13.86,4 13.86,12 6.93,16 0,12 0,4' transform='translate(-6.93 14)'/><polygon points='6.93,0 13.86,4 13.86,12 6.93,16 0,12 0,4' transform='translate(6.93 14)'/></g></pattern>"
)


def schatten(x, y, rx, ry, opa=.22):
    return f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='{rx:.1f}' ry='{ry:.1f}' fill='#1a2a10' opacity='{opa}'/>"


def _g(x, y, s, inhalt, spiegeln=False, rot=0):
    sx = -s if spiegeln else s
    r = f" rotate({rot})" if rot else ""
    return f"<g transform='translate({x:.1f} {y:.1f}){r} scale({sx:.3f} {s:.3f})'>{inhalt}</g>"


# ═══════════════════════════════════════════════════════════════════════════
#  Tiere des Bauernhofs
# ═══════════════════════════════════════════════════════════════════════════
def kuh(x, y, s=1.0, spiegeln=False):
    """Kuh (schwarz-weiß), Blick nach rechts; Breite ≈ 150, Höhe ≈ 100 bei s = 1."""
    flecken = "".join(f"<path d='{d}' fill='#2a2c33'/>" for d in [
        "M-40,-84 C-20,-92 -6,-76 -14,-62 C-24,-52 -44,-60 -46,-72 Z",
        "M14,-80 C32,-86 48,-72 42,-56 C34,-46 14,-52 10,-64 Z",
        "M-48,-48 C-36,-52 -28,-40 -34,-30 C-42,-24 -54,-34 -48,-48 Z",
        "M26,-44 C36,-50 50,-42 46,-32 C40,-26 26,-30 26,-44 Z"])
    o = ""
    # ferne Beine
    for lx in (-38, 26):
        o += f"<rect x='{lx + 5}' y='-38' width='11' height='38' rx='3' fill='#c4cad2' stroke='#7a828c' stroke-width='1'/><rect x='{lx + 5}' y='-6' width='11' height='6' rx='2' fill='#3a3a3f'/>"
    # Schwanz
    o += ("<path d='M-56,-82 C-70,-76 -70,-52 -66,-34' fill='none' stroke='#2a2c33' stroke-width='3' stroke-linecap='round'/>"
          "<path d='M-66,-34 q-5,8 -1,15 q4,-6 3,-15 z' fill='#2a2c33'/>")
    # Körper
    korper = "M-58,-66 C-60,-88 -34,-96 0,-96 C38,-96 62,-90 64,-68 C66,-46 56,-36 46,-34 L-46,-34 C-58,-38 -60,-52 -58,-66 Z"
    o += f"<clipPath id='kuhk'><path d='{korper}'/></clipPath>"
    o += f"<path d='{korper}' fill='url(#sKuhFell)' stroke='#8a929c' stroke-width='1.6'/>"
    o += f"<g clip-path='url(#kuhk)'>{flecken}<path d='{korper}' fill='url(#bVol)' opacity='.55'/></g>"
    # Euter
    o += ("<path d='M-30,-36 C-30,-24 -10,-24 -8,-36 Z' fill='#f2a7b8' stroke='#c76a85' stroke-width='1.2'/>"
          "<path d='M-26,-27 v5 M-18,-26 v5 M-12,-28 v4' stroke='#e57d9b' stroke-width='3' stroke-linecap='round'/>")
    # nahe Beine
    for lx in (-48, 34):
        o += (f"<rect x='{lx + 2}' y='-42' width='13' height='42' rx='3.5' fill='url(#sKuhFell)' stroke='#7a828c' stroke-width='1.2'/>"
              f"<rect x='{lx + 2}' y='-8' width='13' height='8' rx='2.5' fill='#2e2e33'/>")
    # fernes Horn und fernes Ohr (hinter dem Kopf)
    o += ("<path d='M82,-94 C84,-104 90,-114 99,-117 C99,-108 96,-99 92,-92 Z' fill='#f4efe0' stroke='#b8b09a' stroke-width='1'/>"
          "<path d='M64,-92 C58,-104 60,-116 67,-121 C73,-114 77,-102 76,-91 Z' fill='#f4efe0' stroke='#b8b09a' stroke-width='1'/>"
          "<ellipse cx='92' cy='-98' rx='12' ry='5.4' transform='rotate(-52 92 -98)' fill='#2a2c33'/>"
          "<ellipse cx='92' cy='-98' rx='7.4' ry='3' transform='rotate(-52 92 -98)' fill='#e9a5b3'/>")
    # Kopf
    o += ("<path d='M56,-90 C74,-104 98,-98 104,-80 C110,-64 112,-46 106,-38 C98,-28 80,-32 72,-44 C64,-56 54,-72 56,-90 Z' fill='url(#sKuhFell)' stroke='#8a929c' stroke-width='1.6'/>"
          "<path d='M62,-94 C76,-102 90,-98 90,-84 C84,-76 72,-72 62,-76 Z' fill='#2a2c33'/>"
          "<ellipse cx='103' cy='-45' rx='12' ry='10.5' fill='#f6b3c1' stroke='#c76a85' stroke-width='1.3'/>"
          "<ellipse cx='107' cy='-48' rx='2.2' ry='3' fill='#a04462'/><ellipse cx='99' cy='-42' rx='2' ry='2.8' fill='#a04462'/>"
          "<circle cx='88' cy='-72' r='4.2' fill='#15151a'/><circle cx='89.4' cy='-73.4' r='1.4' fill='#fff'/>"
          "<ellipse cx='60' cy='-88' rx='13' ry='6.5' transform='rotate(24 60 -88)' fill='#2a2c33'/>"
          "<ellipse cx='60' cy='-88' rx='8' ry='3.4' transform='rotate(24 60 -88)' fill='#e9a5b3'/>")
    return schatten(x, y, 62 * s, 7 * s) + _g(x, y, s, o, spiegeln)


def schaf(x, y, s=1.0, spiegeln=False, kontur="#cfc9b6", kontur_w=1.2):
    """Schaf mit flauschiger Wolle, Blick nach rechts; Breite ≈ 96, Höhe ≈ 62 bei s = 1."""
    o = ""
    for lx in (-26, 18):
        o += f"<rect x='{lx}' y='-24' width='6' height='24' rx='2' fill='#34343a'/><rect x='{lx + 9}' y='-24' width='6' height='24' rx='2' fill='#2a2a30'/>"
    # Wolle: viele Kreise
    rng = random.Random(7)
    kreise = [(-30, -40, 15), (-14, -50, 17), (4, -52, 17), (22, -46, 15), (34, -36, 12), (-36, -28, 11), (-22, -30, 15), (-2, -32, 16), (16, -30, 15), (30, -26, 11),
              (-8, -44, 14), (10, -42, 13)]
    wolle = ""
    for cx, cy, r in kreise:
        wolle += f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='url(#sWolle)' stroke='{kontur}' stroke-width='{kontur_w}'/>"
    o += wolle
    kringel = "".join(f"<path d='M{cx - r * .5:.1f},{cy - r * .2:.1f} q{r * .3:.1f},-{r * .5:.1f} {r * .6:.1f},0' fill='none' stroke='#c9c2ac' stroke-width='1.1' stroke-linecap='round'/>" for cx, cy, r in kreise)
    o += kringel
    # Kopf
    o += ("<ellipse cx='46' cy='-34' rx='10' ry='13' transform='rotate(-14 46 -34)' fill='#3b3b42' stroke='#222' stroke-width='1'/>"
          "<path d='M36,-44 C40,-56 54,-56 58,-46 C52,-48 42,-48 36,-44 Z' fill='#fff' stroke='#cfc9b6' stroke-width='1'/>"
          "<ellipse cx='36' cy='-34' rx='6' ry='3' transform='rotate(30 36 -34)' fill='#2a2a30'/>"
          "<circle cx='50' cy='-38' r='2.4' fill='#fff'/><circle cx='50.6' cy='-38' r='1.2' fill='#111'/>"
          "<ellipse cx='54' cy='-26' rx='3.4' ry='2.2' fill='#8a7068'/>")
    return schatten(x, y, 44 * s, 5 * s) + _g(x, y, s, o, spiegeln)


def huhn(x, y, s=1.0, spiegeln=False):
    """Huhn (braun-rot), Blick nach rechts; Breite ≈ 50, Höhe ≈ 52 bei s = 1."""
    o = ("<path d='M-4,-14 L-6,-2 M4,-14 L6,-2' stroke='#e0a010' stroke-width='3' stroke-linecap='round'/>"
         "<path d='M-6,-2 l-6,3 M-6,-2 l0,4 M-6,-2 l5,3 M6,-2 l-4,3 M6,-2 l1,4 M6,-2 l6,3' stroke='#e0a010' stroke-width='2' stroke-linecap='round'/>"
         # Schwanzfedern
         "<path d='M-18,-24 C-34,-30 -38,-48 -30,-54 C-26,-46 -22,-38 -14,-34 Z' fill='#7a2f1a' stroke='#4d1d0f' stroke-width='1'/>"
         "<path d='M-18,-22 C-30,-26 -40,-38 -38,-46 C-30,-42 -24,-34 -14,-30 Z' fill='#b84a26' stroke='#7a2f1a' stroke-width='1'/>"
         # Körper
         "<path d='M-22,-26 C-22,-42 4,-48 18,-40 C26,-34 26,-18 8,-12 C-8,-8 -22,-12 -22,-26 Z' fill='url(#bPelz)' stroke='#7a3a10' stroke-width='1.3'/>"
         "<path d='M-22,-26 C-22,-42 4,-48 18,-40 C26,-34 26,-18 8,-12 C-8,-8 -22,-12 -22,-26 Z' fill='#c4592a' opacity='.55'/>"
         "<path d='M-18,-30 C-8,-38 6,-32 4,-22 C-6,-18 -16,-20 -18,-30 Z' fill='#b24420' stroke='#7a2f1a' stroke-width='1'/>"
         "<path d='M-14,-27 q8,-6 14,-4 M-12,-23 q8,-4 12,-3' stroke='#e8946a' stroke-width='1' fill='none' stroke-linecap='round'/>"
         # Kopf
         "<circle cx='20' cy='-48' r='9.5' fill='#d65a2a' stroke='#7a3a10' stroke-width='1.2'/>"
         "<path d='M13,-56 q2,-9 6,-4 q2,-8 6,-2 q3,-6 4,2 q-6,2 -16,4 z' fill='#e0302a' stroke='#8e1712' stroke-width='1'/>"
         "<path d='M28,-48 l9,3 l-9,3 z' fill='#f2b020' stroke='#a06a00' stroke-width='1'/>"
         "<path d='M26,-42 q3,6 0,9 q-4,-3 0,-9 z' fill='#e0302a' stroke='#8e1712' stroke-width='.8'/>"
         "<circle cx='23.5' cy='-50' r='2' fill='#111'/><circle cx='24.1' cy='-50.6' r='.7' fill='#fff'/>")
    return schatten(x, y, 24 * s, 3 * s) + _g(x, y, s, o, spiegeln)


def kueken(x, y, s=1.0):
    o = ("<ellipse cx='0' cy='-9' rx='9' ry='8' fill='#ffd84a' stroke='#c79a10' stroke-width='1'/><circle cx='8' cy='-15' r='5.5' fill='#ffd84a' stroke='#c79a10' stroke-width='1'/>"
         "<path d='M13,-15 l5,1.5 l-5,1.5 z' fill='#f08a10'/><circle cx='9.4' cy='-16' r='1.1' fill='#111'/>"
         "<path d='M-2,-2 v2 M3,-2 v2' stroke='#f08a10' stroke-width='1.6'/>")
    return schatten(x, y, 10 * s, 2 * s, .2) + _g(x, y, s, o)


def stall(x, y, s=1.0):
    """Roter Stall mit Heuboden, Breite ≈ 140, Höhe ≈ 120 bei s = 1 (Mitte = x, Boden = y)."""
    o = ("<path d='M-70,0 V-62 L-52,-96 H52 L70,-62 V0 Z' fill='url(#sScheune)' stroke='#6e1f18' stroke-width='2'/>"
         "".join(f"<line x1='{bx}' y1='-96' x2='{bx}' y2='0' stroke='#7e251d' stroke-width='1' opacity='.5'/>" for bx in range(-60, 70, 12)) +
         # Dach
         "<path d='M-80,-60 L-56,-108 H56 L80,-60 L70,-58 L54,-96 H-54 L-70,-58 Z' fill='url(#sDach)' stroke='#2c1d17' stroke-width='1.6' stroke-linejoin='round'/>"
         "<path d='M-76,-62 L-54,-104 H54 L76,-62' fill='none' stroke='#9a7a68' stroke-width='1.6' opacity='.7'/>"
         # Heuboden
         "<rect x='-14' y='-86' width='28' height='24' rx='2' fill='#3b1d12' stroke='#f4ede0' stroke-width='3'/>"
         "<path d='M-12,-62 V-70 C-6,-74 4,-74 12,-70 V-62 Z' fill='#e7c35a'/>"
         "<path d='M-9,-66 l5,-5 M0,-66 l6,-5 M-4,-62 l7,-6' stroke='#c79a2a' stroke-width='1.3' stroke-linecap='round'/>"
         # Tür
         "<rect x='-26' y='-46' width='52' height='46' fill='#f4ede0' stroke='#6e1f18' stroke-width='2'/>"
         "<rect x='-22' y='-42' width='44' height='42' fill='#a83228'/>"
         "<path d='M-22,-42 L22,0 M22,-42 L-22,0 M0,-42 V0' stroke='#f4ede0' stroke-width='3'/>"
         "<rect x='-26' y='-46' width='52' height='46' fill='none' stroke='#f4ede0' stroke-width='3'/>"
         # Fenster
         "<rect x='-58' y='-44' width='16' height='16' rx='1' fill='#cfe6f5' stroke='#f4ede0' stroke-width='3'/><path d='M-50,-44 V-28 M-58,-36 H-42' stroke='#f4ede0' stroke-width='2'/>"
         "<rect x='42' y='-44' width='16' height='16' rx='1' fill='#cfe6f5' stroke='#f4ede0' stroke-width='3'/><path d='M50,-44 V-28 M42,-36 H58' stroke='#f4ede0' stroke-width='2'/>"
         # Wetterhahn
         "<path d='M0,-108 V-120 M-6,-116 H6' stroke='#3a3a40' stroke-width='2'/><path d='M0,-124 q8,-2 10,3 q-6,3 -10,-3z' fill='#3a3a40'/>")
    return schatten(x, y, 78 * s, 7 * s) + _g(x, y, s, o)


def zaun(x0, x1, y, s=1.0):
    """Holzzaun von x0 bis x1 (Standlinie y)."""
    o = ""
    n = max(2, int((x1 - x0) / (20 * s)))
    for i in range(n + 1):
        px = x0 + (x1 - x0) * i / n
        o += (f"<rect x='{px - 2.6 * s:.1f}' y='{y - 26 * s:.1f}' width='{5.2 * s:.1f}' height='{26 * s:.1f}' rx='1.2' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='.9'/>"
              f"<path d='M{px - 2.6 * s:.1f},{y - 26 * s:.1f} l{2.6 * s:.1f},-{3 * s:.1f} l{2.6 * s:.1f},{3 * s:.1f}' fill='#b98a52' stroke='#5a3a1c' stroke-width='.9'/>")
    for yy in (y - 20 * s, y - 10 * s):
        o += f"<rect x='{x0:.1f}' y='{yy - 2.3 * s:.1f}' width='{x1 - x0:.1f}' height='{4.6 * s:.1f}' rx='1' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='.9'/>"
    return o


def milchkanne(x, y, s=1.0):
    """Milchkanne (Metall), Höhe ≈ 40 bei s = 1."""
    o = ("<path d='M-10,0 L-12,-26 C-12,-30 -9,-32 -7,-32 H7 C9,-32 12,-30 12,-26 L10,0 Z' fill='url(#sMetall)' stroke='#5d6670' stroke-width='1.2'/>"
         "<rect x='-8' y='-35' width='16' height='4' rx='1.5' fill='#c3cbd2' stroke='#5d6670' stroke-width='1'/>"
         "<path d='M-6,-35 C-6,-42 6,-42 6,-35' fill='none' stroke='#5d6670' stroke-width='2.2' stroke-linecap='round'/>"
         "<path d='M-11,-22 H11 M-10.5,-8 H10.5' stroke='#5d6670' stroke-width='1' opacity='.6'/>"
         "<path d='M12,-26 q7,0 7,7 q0,6 -7,6' fill='none' stroke='#8a939c' stroke-width='2.6' stroke-linecap='round'/>"
         "<circle cx='0' cy='-15' r='4.4' fill='#fff' stroke='#9aa3ad' stroke-width='.8'/>")
    return schatten(x, y, 14 * s, 3 * s) + _g(x, y, s, o)


def eier(x, y, s=1.0):
    """Drei Eier im Strohnest, Breite ≈ 40."""
    o = ("<path d='M-22,0 C-24,-8 -10,-10 0,-8 C10,-10 24,-8 22,0 C12,4 -12,4 -22,0 Z' fill='#d9b45a' stroke='#a37a22' stroke-width='1'/>"
         "<path d='M-18,-3 l8,-2 M-6,-6 l10,1 M8,-4 l9,-1 M-14,1 l9,1 M4,1 l10,0' stroke='#f2d886' stroke-width='1.2' stroke-linecap='round'/>")
    for ex, ey, c in ((-8, -10, "#fff7ec"), (6, -11, "#f3d9b0"), (-1, -16, "#fffaf0")):
        o += (f"<ellipse cx='{ex}' cy='{ey}' rx='6.2' ry='8' fill='{c}' stroke='#c8b48e' stroke-width='1'/>"
              f"<ellipse cx='{ex - 2}' cy='{ey - 3}' rx='1.8' ry='3' fill='#fff' opacity='.8'/>")
    return _g(x, y, s, o)


def wollknaeuel(x, y, s=1.0):
    """Wollknäuel (hellblau) mit Faden, Durchmesser ≈ 26."""
    o = ("<circle cx='0' cy='-12' r='12' fill='#9ec9ea' stroke='#5b8fb8' stroke-width='1.2'/>"
         "<path d='M-10,-16 q10,-8 20,0 M-11,-11 q11,-8 22,2 M-9,-5 q10,-7 18,3 M-4,-23 q8,6 12,16' fill='none' stroke='#6fa3cc' stroke-width='1.2' stroke-linecap='round'/>"
         "<path d='M-3,-22 q-8,-2 -4,-8' fill='none' stroke='#6fa3cc' stroke-width='1.2' stroke-linecap='round'/>"
         "<path d='M10,-4 C20,2 22,-2 28,0' fill='none' stroke='#9ec9ea' stroke-width='2' stroke-linecap='round'/>"
         "<ellipse cx='-4' cy='-17' rx='3' ry='4' fill='#fff' opacity='.5'/>")
    return schatten(x, y, 13 * s, 2.4 * s, .18) + _g(x, y, s, o)


# ═══════════════════════════════════════════════════════════════════════════
#  Imkerei
# ═══════════════════════════════════════════════════════════════════════════
def bienenkasten(x, y, s=1.0, farbe="#f2cf5e", zargen=2, deckel_ab=False):
    """Bienenkasten (Magazinbeute) im Dreiviertelblick: Steinfüße, Boden mit Flugloch und Flugbrett, `zargen` Kästen, Blechdach.
    Mitte der Vorderseite = x, Boden = y. Breite ≈ 110, Höhe ≈ 40 + 26·zargen bei s = 1."""
    def hell(c, f):
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        k = lambda v: max(0, min(255, int(v * f)))
        return f"#{k(r):02x}{k(g):02x}{k(b):02x}"
    W_, H_, DX, DY = 60, 26, 15, 8
    o = ""
    # Steinfüße
    for fx in (-26, 18):
        o += (f"<rect x='{fx}' y='-12' width='14' height='12' rx='1.5' fill='#aab2bb' stroke='#6b747d' stroke-width='1'/>"
              f"<path d='M{fx},-12 l4,-3 h14 l-4,3 z' fill='#c8cfd6' stroke='#6b747d' stroke-width='.8'/>")
    # Boden mit Flugbrett
    o += (f"<rect x='-33' y='-18' width='66' height='7' fill='{hell(farbe, .8)}' stroke='#4a3a22' stroke-width='1'/>"
          "<path d='M-26,-11 L26,-11 L30,-4 L-30,-4 Z' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1'/>"
          "<path d='M-22,-8 H22' stroke='#5a3a1c' stroke-width='.8' opacity='.7'/>")
    y0 = -18
    for i in range(zargen):
        top = y0 - H_
        # Seitenfläche
        o += (f"<path d='M{W_ / 2},{y0} L{W_ / 2 + DX},{y0 - DY} V{top - DY} L{W_ / 2},{top} Z' fill='{hell(farbe, .72)}' stroke='#4a3a22' stroke-width='1.1' stroke-linejoin='round'/>"
              f"<rect x='{W_ / 2 + 4}' y='{y0 - H_ / 2 - 4 - DY * .5}' width='8' height='3.4' rx='1.5' fill='#3a2a14' opacity='.7' transform='skewY({-math.degrees(math.atan2(DY, DX)):.1f})'/>")
        # Vorderfläche
        o += (f"<rect x='{-W_ / 2}' y='{top}' width='{W_}' height='{H_}' fill='{farbe}' stroke='#4a3a22' stroke-width='1.1'/>"
              f"<rect x='{-W_ / 2}' y='{top}' width='{W_}' height='{H_}' fill='url(#bVolSeite)' opacity='.35'/>"
              f"<path d='M{-W_ / 2 + 2},{top + 7} H{W_ / 2 - 2} M{-W_ / 2 + 2},{top + 14} H{W_ / 2 - 2} M{-W_ / 2 + 2},{top + 20} H{W_ / 2 - 2}' stroke='#000' stroke-width='.6' opacity='.12'/>"
              f"<rect x='-13' y='{top + H_ / 2 - 2}' width='26' height='3.4' rx='1.5' fill='#3a2a14' opacity='.65'/>")
        y0 = top
    # Flugloch (Schlitz) im Boden
    o += "<rect x='-14' y='-17.4' width='28' height='4.6' rx='1.2' fill='#1f150a'/>"
    # Dach (Blech)
    ty = y0 - 8
    if deckel_ab:
        top_face = f"M{-W_ / 2},{y0} L{W_ / 2},{y0} L{W_ / 2 + DX},{y0 - DY} L{-W_ / 2 + DX},{y0 - DY} Z"
        o += f"<path d='{top_face}' fill='#3a2a14' stroke='#4a3a22' stroke-width='1.1'/>"
        for k in range(1, 9):
            fx = -W_ / 2 + k * W_ / 9
            if k == 5:
                continue            # hier fehlt ein Rähmchen (der Imker hat es herausgezogen)
            o += f"<path d='M{fx},{y0} L{fx + DX},{y0 - DY}' stroke='#c79a62' stroke-width='3' stroke-linecap='butt'/><path d='M{fx - .9},{y0 - .4} L{fx + DX - .9},{y0 - DY - .4}' stroke='#e6c590' stroke-width='.8'/>"
    if not deckel_ab:
        o += (f"<path d='M{-W_ / 2 - 5},{y0} L{W_ / 2 + 5},{y0} L{W_ / 2 + DX + 5},{y0 - DY} L{-W_ / 2 + DX - 5},{y0 - DY} Z' fill='#9aa3ac' stroke='#5d6670' stroke-width='1'/>"
              f"<path d='M{-W_ / 2 - 5},{y0} V{ty + 2} L{W_ / 2 + 5},{ty + 2} V{y0} Z' fill='url(#sBlech)' stroke='#5d6670' stroke-width='1.1'/>"
              f"<path d='M{W_ / 2 + 5},{ty + 2} L{W_ / 2 + DX + 5},{ty + 2 - DY} V{y0 - DY} L{W_ / 2 + 5},{y0} Z' fill='#8a939c' stroke='#5d6670' stroke-width='1.1'/>"
              f"<path d='M{-W_ / 2 - 5},{ty + 2} L{-W_ / 2 + DX - 5},{ty + 2 - DY} L{W_ / 2 + DX + 5},{ty + 2 - DY} L{W_ / 2 + 5},{ty + 2} Z' fill='#d9dfe4' stroke='#5d6670' stroke-width='1.1'/>")
    return schatten(x + 6 * s, y, 44 * s, 4 * s) + _g(x, y, s, o)


def imker(x, y, s=1.0, haende=None, arme="unten", blick=0):
    """Imker von vorn (weißer Schutzanzug, Hut mit Schleier, Handschuhe); Höhe ≈ 108 bei s = 1.

    `haende` = ((x, y), (x, y)) lokale Handpositionen (links, rechts) für gebeugte Arme; sonst hängen die Arme."""
    o = ""
    # Stiefel und Hose
    for sx in (-1, 1):
        o += (f"<path d='M{sx * 3},-8 L{sx * 14},-8 L{sx * 14.5},-3 C{sx * 14.5},-1 {sx * 12},0 {sx * 9},0 H{sx * 3} Z' fill='#d5d9de' stroke='#8b939c' stroke-width='1'/>")
        o += f"<path d='M{sx * 3},-48 L{sx * 15},-48 L{sx * 14},-6 H{sx * 3.5} Z' fill='url(#sAnzug)' stroke='#a39d8a' stroke-width='1.1'/>"
    o += "<path d='M0,-46 V-6' stroke='#bdb7a2' stroke-width='1'/>"
    # Rumpf
    o += ("<path d='M-19,-78 C-24,-78 -26,-70 -25,-60 L-23,-44 C-22,-40 22,-40 23,-44 L25,-60 C26,-70 24,-78 19,-78 Z' fill='url(#sAnzug)' stroke='#a39d8a' stroke-width='1.2'/>"
          "<path d='M-23,-46 H23' stroke='#8a8268' stroke-width='3'/><rect x='-3' y='-48' width='6' height='4' rx='1' fill='#b8a45a' stroke='#8a8268' stroke-width='.7'/>"
          "<path d='M0,-78 V-46' stroke='#a39d8a' stroke-width='1.2'/><path d='M-1.6,-76 v28 M1.6,-76 v28' stroke='#d9d3bd' stroke-width='.6'/>"
          "<rect x='-17' y='-68' width='11' height='10' rx='1.4' fill='none' stroke='#b5af98' stroke-width='1'/><rect x='6' y='-68' width='11' height='10' rx='1.4' fill='none' stroke='#b5af98' stroke-width='1'/>"
          "<path d='M-20,-72 C-12,-68 12,-68 20,-72' fill='none' stroke='#fff' stroke-width='2' opacity='.6'/>")
    # Arme
    if haende is None:
        haende = ((-29, -42), (29, -42))
    for sx, (hx, hy) in zip((-1, 1), haende):
        sh = (sx * 21, -74)
        ell = ((sh[0] + hx) / 2 + sx * 5, (sh[1] + hy) / 2 + 3)
        o += (f"<path d='M{sh[0]},{sh[1]} L{ell[0]:.1f},{ell[1]:.1f} L{hx},{hy}' fill='none' stroke='#a39d8a' stroke-width='11.5' stroke-linecap='round' stroke-linejoin='round'/>"
              f"<path d='M{sh[0]},{sh[1]} L{ell[0]:.1f},{ell[1]:.1f} L{hx},{hy}' fill='none' stroke='url(#sAnzug)' stroke-width='9.6' stroke-linecap='round' stroke-linejoin='round'/>")
        o += (f"<ellipse cx='{hx}' cy='{hy + 2}' rx='6.4' ry='7' fill='#d9c08a' stroke='#8a7448' stroke-width='1.1'/>"
              f"<path d='M{hx - 3},{hy + 6} v4 M{hx},{hy + 7} v4.5 M{hx + 3},{hy + 6} v4' stroke='#8a7448' stroke-width='1.3' stroke-linecap='round'/>")
    # Kopf hinter dem Schleier
    o += ("<ellipse cx='0' cy='-87' rx='8.6' ry='9.6' fill='#f0c7a0' stroke='#b88a62' stroke-width='1'/>"
          f"<circle cx='{-3.2 + blick}' cy='-88' r='1.1' fill='#3a2a1a'/><circle cx='{3.2 + blick}' cy='-88' r='1.1' fill='#3a2a1a'/>"
          "<path d='M-3,-82 q3,2.4 6,0' stroke='#a8604a' stroke-width='1' fill='none' stroke-linecap='round'/>"
          "<path d='M-5,-93 q5,-3 10,0' stroke='#6a4a2a' stroke-width='1.4' fill='none' stroke-linecap='round'/>")
    # Schleier: Netz vom Hutrand bis zu den Schultern
    schleier = "M-21,-95 C-24,-88 -27,-80 -27,-72 C-14,-68 14,-68 27,-72 C27,-80 24,-88 21,-95 Z"
    o += (f"<path d='{schleier}' fill='#30424d' opacity='.28'/><path d='{schleier}' fill='url(#sNetz)'/>"
          f"<path d='{schleier}' fill='none' stroke='#27343c' stroke-width='1.2' stroke-linejoin='round'/>"
          "<path d='M-26,-72 C-14,-67 14,-67 26,-72' fill='none' stroke='#f4efe0' stroke-width='2.6'/>"
          "<path d='M-18,-92 C-20,-86 -22,-80 -22,-74' fill='none' stroke='#fff' stroke-width='1.4' opacity='.5'/>")
    # Hut
    o += ("<ellipse cx='0' cy='-95' rx='24' ry='6.2' fill='#b9a974' stroke='#8a7a48' stroke-width='1'/>"
          "<path d='M-12,-96 C-12,-110 12,-110 12,-96 Z' fill='url(#sHut)' stroke='#9a8a58' stroke-width='1.1'/>"
          "<path d='M-12,-98 H12' stroke='#7a6a3a' stroke-width='2.4'/>"
          "<ellipse cx='0' cy='-96' rx='24' ry='5.6' fill='none' stroke='#f4eed6' stroke-width='1' opacity='.7'/>"
          "<path d='M-7,-107 C-3,-109 3,-109 7,-106' fill='none' stroke='#fff' stroke-width='1.6' opacity='.7' stroke-linecap='round'/>")
    return schatten(x, y, 26 * s, 4 * s) + _g(x, y, s, o)


def rauchgeraet(x, y, s=1.0, rauch=True):
    """Rauchgerät (Smoker): Metallbüchse, Düse, Blasebalg, Rauch; Breite ≈ 56, Höhe ≈ 70 bei s = 1 (ohne Rauch ≈ 52)."""
    o = ""
    # Blasebalg (rechts): Holzplatten, Leder mit Falten
    o += ("<path d='M14,-30 L36,-34 L36,-6 L14,-8 Z' fill='url(#sLeder)' stroke='#4a2a10' stroke-width='1.2' stroke-linejoin='round'/>"
          "<path d='M16,-26 L34,-29 M16,-21 L34,-23 M16,-16 L34,-17.5 M16,-11 L34,-12' stroke='#4a2a10' stroke-width='1' opacity='.7'/>"
          "<path d='M34,-36 L40,-36 L40,-4 L34,-4 Z' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1.1'/>"
          "<path d='M14,-31 L18,-31 L18,-7 L14,-7 Z' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1'/>"
          "<path d='M40,-26 C48,-26 50,-18 44,-14' fill='none' stroke='#5a3a1c' stroke-width='2.4' stroke-linecap='round'/>")
    # Büchse
    o += ("<path d='M-16,0 V-34 C-16,-38 16,-38 16,-34 V0 Z' fill='url(#sMetall)' stroke='#4a535c' stroke-width='1.4'/>"
          "<ellipse cx='0' cy='0' rx='16' ry='3.6' fill='#7a848e' stroke='#4a535c' stroke-width='1.2'/>"
          "<path d='M-16,-8 H16 M-16,-26 H16' stroke='#4a535c' stroke-width='1' opacity='.65'/>"
          "<path d='M-12,-32 V-3' stroke='#fff' stroke-width='2' opacity='.55' stroke-linecap='round'/>"
          # Deckel (Kegel) und Düse
          "<path d='M-17,-34 C-17,-42 -9,-50 2,-52 L14,-48 C16,-44 17,-40 17,-34 Z' fill='url(#sMetall)' stroke='#4a535c' stroke-width='1.4'/>"
          "<path d='M-4,-50 L-12,-58 L-6,-60 L4,-52 Z' fill='#6f7983' stroke='#4a535c' stroke-width='1.3' stroke-linejoin='round'/>"
          "<ellipse cx='-9' cy='-59' rx='3.4' ry='2.2' transform='rotate(-34 -9 -59)' fill='#1e252b'/>"
          "<path d='M-14,-34 C-12,-42 -6,-46 0,-48' fill='none' stroke='#fff' stroke-width='1.6' opacity='.5' stroke-linecap='round'/>"
          "<path d='M8,-50 q6,-6 12,-2 q2,6 -2,8' fill='none' stroke='#6a4a2a' stroke-width='2.4' stroke-linecap='round'/>")
    if rauch:
        for i, (px, py, r) in enumerate([(-14, -66, 4.4), (-20, -75, 6), (-17, -87, 8), (-9, -100, 10), (4, -114, 12)]):
            o += f"<circle cx='{px}' cy='{py}' r='{r}' fill='url(#sRauch)' stroke='#a3adb5' stroke-width='1.2' opacity='.95'/>"
    return schatten(x + 6 * s, y, 32 * s, 4 * s) + _g(x, y, s, o)


def honigglas(x, y, s=1.0, mit_etikett=True):
    """Honigglas mit goldenem Deckel und Wabenzeichen, Höhe ≈ 62, Breite ≈ 44 bei s = 1."""
    glas = "M-20,-6 C-22,-8 -22,-40 -19,-46 C-17,-50 -12,-52 -12,-54 H12 C12,-52 17,-50 19,-46 C22,-40 22,-8 20,-6 C18,-2 -18,-2 -20,-6 Z"
    o = (f"<clipPath id='hg{int(x) % 997}{int(y) % 997}'><path d='{glas}'/></clipPath>"
         f"<path d='{glas}' fill='#fff7d8' opacity='.5'/>"
         f"<g clip-path='url(#hg{int(x) % 997}{int(y) % 997})'><rect x='-24' y='-50' width='48' height='50' fill='url(#gHonig)'/>"
         "<rect x='-24' y='-50' width='48' height='14' fill='#fff' opacity='.12'/>"
         "<ellipse cx='5' cy='-30' rx='3' ry='2.4' fill='#fff' opacity='.3'/><ellipse cx='-8' cy='-14' rx='2.4' ry='1.8' fill='#fff' opacity='.25'/></g>"
         f"<path d='{glas}' fill='url(#sGlas)'/>"
         f"<path d='{glas}' fill='none' stroke='#b36a00' stroke-width='1.5' stroke-linejoin='round'/>"
         "<path d='M-15,-44 C-17,-34 -17,-18 -15,-9' fill='none' stroke='#fff' stroke-width='3' stroke-linecap='round' opacity='.7'/>")
    if mit_etikett:
        o += ("<rect x='-14' y='-34' width='28' height='20' rx='4' fill='#fff9e6' stroke='#c79a3a' stroke-width='1.2'/>"
              + "".join(sechseck(cx, cy, 4.3, fill="#f7b800", stroke="#b57f10", sw=.9, spitz_oben=True) for cx, cy in ((-4.5, -26.5), (4.5, -26.5), (0, -19.4)))
              + "<path d='M-9,-17 h18' stroke='#c79a3a' stroke-width='1' opacity='.6'/>")
    # Deckel
    o += ("<rect x='-14' y='-60' width='28' height='7' rx='2' fill='#f1b629' stroke='#8a5a00' stroke-width='1.3'/>"
          "<rect x='-14' y='-60' width='28' height='3' rx='1.5' fill='#fff' opacity='.35'/>"
          "<path d='M-14,-57 H14' stroke='#8a5a00' stroke-width='.8' opacity='.5'/>")
    return schatten(x, y, 26 * s, 3.4 * s) + _g(x, y, s, o)


def honigloeffel(x, y, s=1.0, rot=-24):
    o = ("<path d='M0,0 L0,-52' stroke='url(#sHolzD)' stroke-width='4' stroke-linecap='round'/>"
         "<ellipse cx='0' cy='-60' rx='8' ry='9' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1.1'/>"
         "<path d='M-5,-64 h10 M-7,-60 h14 M-6,-56 h12' stroke='#5a3a1c' stroke-width='1.4' stroke-linecap='round'/>"
         "<path d='M-4,-52 q-2,6 0,10' stroke='#f2a900' stroke-width='3' stroke-linecap='round' fill='none'/>")
    return _g(x, y, s, o, rot=rot)


def kerze(x, y, h=80, s=1.0, brennt=True, spirale=False, farbe_dochtglut=True):
    """Bienenwachskerze, Breite ≈ 22, Höhe `h` bei s = 1 (Flamme darüber)."""
    cid = f"kz{int(x) % 997}{int(y) % 997}"
    o = (f"<clipPath id='{cid}'><path d='M-11,0 V{-h + 4} C-11,{-h - 1} 11,{-h - 1} 11,{-h + 4} V0 C11,5 -11,5 -11,0 Z'/></clipPath>"
         f"<path d='M-11,0 V{-h + 4} C-11,{-h - 1} 11,{-h - 1} 11,{-h + 4} V0 C11,5 -11,5 -11,0 Z' fill='url(#sKerze)' stroke='#b9862a' stroke-width='1.3'/>")
    if spirale:
        o += f"<g clip-path='url(#{cid})'>" + "".join(f"<path d='M-14,{-h + 14 + i * 16} L14,{-h + 4 + i * 16}' stroke='#c99528' stroke-width='3' opacity='.55'/>" for i in range(int(h / 16) + 1)) + "</g>"
    o += (f"<path d='M-7,{-h + 6} V-6' stroke='#fff' stroke-width='3' opacity='.55' stroke-linecap='round'/>"
          f"<ellipse cx='0' cy='{-h + 3}' rx='9' ry='3' fill='#fff3bd' opacity='.9'/>"
          f"<path d='M0,{-h + 3} V{-h - 8}' stroke='#3a2a1a' stroke-width='1.6' stroke-linecap='round'/>")
    if brennt:
        o += (f"<circle cx='0' cy='{-h - 14}' r='20' fill='url(#sFlammenGlanz)'/>"
              f"<path d='M0,{-h - 8} C-7,{-h - 14} -5,{-h - 22} 0,{-h - 30} C5,{-h - 22} 7,{-h - 14} 0,{-h - 8} Z' fill='url(#sFlamme)' stroke='#f09a1a' stroke-width='.8'/>"
              f"<path d='M0,{-h - 9} C-2.4,{-h - 12} -2,{-h - 16} 0,{-h - 19} C2,{-h - 16} 2.4,{-h - 12} 0,{-h - 9} Z' fill='#fff8d8' opacity='.9'/>")
    return schatten(x, y, 14 * s, 3 * s) + _g(x, y, s, o)


def wabenstueck(x, y, s=1.0, rot=0):
    """Stück Wabe (Wachs) mit sechseckigen Zellen, Breite ≈ 60."""
    zellen = ""
    for c, z in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
        zellen += sechseck(-12 + c * 15 + (7.5 if z % 2 else 0) - 7, -30 + z * 13, 8.6, fill="url(#gHonig)" if (c + z) % 2 else "url(#gWachs)", stroke="#c9972b", sw=1.2)
    o = zellen
    return schatten(x, y, 30 * s, 4 * s, .18) + _g(x, y, s, o, rot=rot)


def apfelzweig(x, y, s=1.0):
    """Apfelzweig mit zwei Äpfeln, Blättern und zwei Blüten; x,y = Ansatz des Zweigs (links oben), der Zweig hängt nach rechts."""
    def blatt(bx, by, ang, l=26):
        return (f"<g transform='translate({bx} {by}) rotate({ang})'><path d='M0,0 C{l * .3},-{l * .38} {l * .8},-{l * .36} {l},0 C{l * .8},{l * .36} {l * .3},{l * .38} 0,0 Z' fill='url(#gLaub)' stroke='#2a6a2a' stroke-width='1.1'/>"
                f"<path d='M2,0 H{l - 3}' stroke='#c9e8a0' stroke-width='1.1'/><path d='M{l * .3},0 l{l * .18},-{l * .16} M{l * .5},0 l{l * .16},{l * .16} M{l * .62},0 l{l * .1},-{l * .12}' stroke='#c9e8a0' stroke-width='.8'/></g>")
    o = ("<path d='M0,0 C40,10 80,6 120,22 C150,34 176,34 206,52' fill='none' stroke='#5a3a1c' stroke-width='8' stroke-linecap='round'/>"
         "<path d='M0,-1.5 C40,8 80,4 120,20 C150,32 176,32 206,50' fill='none' stroke='#9a6a3a' stroke-width='3' stroke-linecap='round'/>"
         "<path d='M70,10 C78,-6 92,-14 104,-16 M130,26 C136,44 142,56 140,70 M168,36 C178,26 190,22 202,22' fill='none' stroke='#5a3a1c' stroke-width='4' stroke-linecap='round'/>")
    for bx, by, a in ((30, 8, -50), (50, 12, 50), (90, 14, -60), (110, 22, 55), (150, 32, -45), (175, 40, 60), (196, 48, -20), (100, -12, -30), (200, 22, -40)):
        o += blatt(bx, by, a, 28 if a < 0 else 24)
    # Äpfel
    o += ("<g transform='translate(140 86)'><path d='M0,-18 C-2,-24 -4,-26 -6,-28' stroke='#5a3a1c' stroke-width='3' fill='none' stroke-linecap='round'/>"
          "<path d='M-3,-24 C2,-34 14,-30 12,-24 C6,-24 0,-22 -3,-24 Z' fill='url(#gLaub)' stroke='#2a6a2a' stroke-width='1'/>"
          "<path d='M0,-18 C-8,-26 -30,-22 -30,0 C-30,24 -10,34 0,28 C10,34 30,24 30,0 C30,-22 8,-26 0,-18 Z' fill='url(#sApfel)' stroke='#7a1310' stroke-width='1.4'/>"
          "<path d='M-18,-8 C-22,0 -20,12 -14,18' fill='none' stroke='#fff' stroke-width='4' opacity='.45' stroke-linecap='round'/>"
          "<path d='M8,-14 C16,-8 20,2 18,12' fill='none' stroke='#f0a55a' stroke-width='3' opacity='.35' stroke-linecap='round'/></g>")
    o += ("<g transform='translate(204 74)'><path d='M0,-14 C-1,-18 -2,-20 -3,-22' stroke='#5a3a1c' stroke-width='2.6' fill='none' stroke-linecap='round'/>"
          "<path d='M0,-14 C-6,-20 -24,-16 -24,2 C-24,20 -8,26 0,22 C8,26 24,20 24,2 C24,-16 6,-20 0,-14 Z' fill='url(#sApfelG)' stroke='#7a5410' stroke-width='1.3'/>"
          "<path d='M-14,-6 C-18,0 -16,10 -11,15' fill='none' stroke='#fff' stroke-width='3.4' opacity='.5' stroke-linecap='round'/>"
          "<path d='M6,-8 C14,-2 16,6 14,12' fill='none' stroke='#e8663a' stroke-width='6' opacity='.25' stroke-linecap='round'/></g>")
    return _g(x, y, s, o)


def apfel(x, y, s=1.0, gelb=False):
    """Einzelner Apfel mit Stiel und Blatt, Durchmesser ≈ 40 bei s = 1."""
    f = "url(#sApfelG)" if gelb else "url(#sApfel)"
    o = (f"<path d='M0,-16 C-1,-21 -2,-23 -3,-25' stroke='#5a3a1c' stroke-width='2.6' fill='none' stroke-linecap='round'/>"
         "<path d='M-2,-22 C3,-31 14,-28 12,-22 C6,-22 1,-20 -2,-22 Z' fill='url(#gLaub)' stroke='#2a6a2a' stroke-width='1'/>"
         f"<path d='M0,-16 C-8,-23 -26,-19 -26,0 C-26,20 -9,28 0,23 C9,28 26,20 26,0 C26,-19 8,-23 0,-16 Z' fill='{f}' stroke='#7a1310' stroke-width='1.3'/>"
         "<path d='M-15,-7 C-19,0 -17,10 -12,15' fill='none' stroke='#fff' stroke-width='3.6' opacity='.5' stroke-linecap='round'/>")
    return schatten(x, y + 1, 18 * s, 3 * s, .2) + _g(x, y - 22 * s, s, o)


def handschuh(x, y, s=1.0):
    """Handschuh des Imkers (lederfarben), Mitte der Hand bei x,y."""
    o = ("<ellipse cx='0' cy='2' rx='6.4' ry='7' fill='#d9c08a' stroke='#8a7448' stroke-width='1.1'/>"
         "<path d='M-3,6 v4 M0,7 v4.5 M3,6 v4' stroke='#8a7448' stroke-width='1.3' stroke-linecap='round'/>")
    return _g(x, y, s, o)


def apfelbluete(x, y, s=1.0, rot=0):
    """Apfelblüte (weiß mit rosa Rand, gelbe Staubblätter), Durchmesser ≈ 40 bei s = 1."""
    if "ab" not in SPRITES:
        o = ""
        for i in range(5):
            a = i * 72 - 90
            o += (f"<g transform='rotate({a})'><path d='M0,0 C-11,-8 -12,-22 0,-24 C12,-22 11,-8 0,0 Z' fill='#fff' stroke='#e9a0b8' stroke-width='1.1'/>"
                  "<path d='M0,-4 C-4,-10 -4,-18 0,-21' stroke='#f2c8d6' stroke-width='1.6' fill='none' stroke-linecap='round'/></g>")
        for i in range(10):
            a = math.radians(i * 36)
            o += (f"<line x1='0' y1='0' x2='{math.cos(a) * 9:.1f}' y2='{math.sin(a) * 9:.1f}' stroke='#e8c34a' stroke-width='1.1'/>"
                  f"<circle cx='{math.cos(a) * 9.6:.1f}' cy='{math.sin(a) * 9.6:.1f}' r='1.9' fill='#f4a900' stroke='#a06a00' stroke-width='.5'/>")
        o += "<circle cx='0' cy='0' r='3.4' fill='#9ccc5a' stroke='#5a8a2a' stroke-width='.8'/>"
        sprite("ab", o)
    return benutze("ab", x, y, s, rot)


def blume_gross(x, y, s=1.0, farbe="#f06aa0", mitte="#ffd530", petalen=8, stiel=34):
    """Wiesenblume mit vielen Blütenblättern; x,y = Fuß; Blütenmitte bei (x, y−stiel·s)."""
    sid = f"fl{farbe[1:]}{mitte[1:]}{petalen}x{int(stiel)}"
    if sid not in SPRITES:
        o = (f"<path d='M0,0 C-3,{-stiel * .4:.1f} 2,{-stiel * .7:.1f} 0,{-stiel}' fill='none' stroke='#3f9b3f' stroke-width='2.6' stroke-linecap='round'/>"
             f"<path d='M0,{-stiel * .35:.1f} C-12,{-stiel * .4:.1f} -16,{-stiel * .55:.1f} -16,{-stiel * .6:.1f} C-6,{-stiel * .62:.1f} -2,{-stiel * .5:.1f} 0,{-stiel * .35:.1f} Z' fill='#4fae4a' stroke='#2a7a2a' stroke-width='.8'/>")
        for i in range(petalen):
            a = i * 360 / petalen
            o += f"<ellipse cx='0' cy='{-stiel - 9}' rx='4.2' ry='8.6' fill='{farbe}' stroke='#00000026' stroke-width='.6' transform='rotate({a:.0f} 0 {-stiel})'/>"
        o += f"<circle cx='0' cy='{-stiel}' r='5.6' fill='{mitte}' stroke='#b88a10' stroke-width='.9'/><circle cx='-1.6' cy='{-stiel - 1.6}' r='1.6' fill='#fff' opacity='.55'/>"
        sprite(sid, o)
    return benutze(sid, x, y, s)


def raehmchen(x, y, w=96, h=66, s=1.0, honig=True):
    """Rähmchen mit Wabe (Holzrahmen mit „Ohren“, Zellen, Honigdeckel oben); x,y = Mitte der Oberkante; hängt nach unten."""
    o = ""
    ear = 11
    cid = f"rm{int(x) % 997}{int(y) % 997}"
    # Wabe
    o += (f"<clipPath id='{cid}'><rect x='{-w / 2 + 5}' y='6' width='{w - 10}' height='{h - 11}' rx='2'/></clipPath>"
          f"<rect x='{-w / 2 + 3}' y='4' width='{w - 6}' height='{h - 7}' fill='#d9a53a'/>"
          f"<g clip-path='url(#{cid})'><rect x='{-w / 2}' y='0' width='{w}' height='{h}' fill='url(#sWabe)'/>")
    if honig:
        o += (f"<path d='M{-w / 2},6 H{w / 2} V{h * .5:.1f} Q{w * .2:.1f},{h * .6:.1f} 0,{h * .5:.1f} Q{-w * .2:.1f},{h * .42:.1f} {-w / 2},{h * .54:.1f} Z' fill='#f6e7b2' opacity='.93'/>"
              f"<path d='M{-w / 2},6 H{w / 2} V{h * .5:.1f} Q{w * .2:.1f},{h * .6:.1f} 0,{h * .5:.1f} Q{-w * .2:.1f},{h * .42:.1f} {-w / 2},{h * .54:.1f} Z' fill='url(#sWabe)' opacity='.18'/>")
    o += f"<rect x='{-w / 2}' y='0' width='{w}' height='{h}' fill='url(#bVolSeite)' opacity='.25'/></g>"
    # Holzrahmen
    o += (f"<rect x='{-w / 2 - ear}' y='-2' width='{w + 2 * ear}' height='9' rx='2' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1.2'/>"
          f"<rect x='{-w / 2 - 1}' y='4' width='5' height='{h - 3}' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1.1'/>"
          f"<rect x='{w / 2 - 4}' y='4' width='5' height='{h - 3}' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1.1'/>"
          f"<rect x='{-w / 2 - 1}' y='{h - 5}' width='{w + 2}' height='5' fill='url(#sHolzD)' stroke='#5a3a1c' stroke-width='1.1'/>")
    return _g(x, y, s, o)


def biene_auf_wabe(x, y, s=1.0, rot=0):
    """Biene von oben auf der Wabe (klein): Körper mit Streifen, Kopf, Flügel, Fühler."""
    o = ("<ellipse cx='0' cy='4' rx='3.8' ry='6.4' fill='#e6a622' stroke='#4a2f10' stroke-width='.7'/>"
         "<path d='M-3.6,2 H3.6 M-3.4,5.4 H3.4 M-2.6,8.4 H2.6' stroke='#33230f' stroke-width='1.5'/>"
         "<ellipse cx='0' cy='-3' rx='3.8' ry='3.4' fill='url(#bBrust)' stroke='#4a2f10' stroke-width='.6'/>"
         "<ellipse cx='0' cy='-8' rx='3' ry='2.8' fill='#3a2615'/>"
         "<path d='M-1.6,-10 q-2,-3 -4,-3 M1.6,-10 q2,-3 4,-3' stroke='#2a1a0a' stroke-width='.7' fill='none' stroke-linecap='round'/>"
         "<ellipse cx='-6' cy='0' rx='2.6' ry='6' transform='rotate(18 -6 0)' fill='#fff' opacity='.55' stroke='#9bb5c8' stroke-width='.5'/>"
         "<ellipse cx='6' cy='0' rx='2.6' ry='6' transform='rotate(-18 6 0)' fill='#fff' opacity='.55' stroke='#9bb5c8' stroke-width='.5'/>")
    return _g(x, y, s, o, rot=rot)


# ═══════════════════════════════════════════════════════════════════════════
#  Landschaft
# ═══════════════════════════════════════════════════════════════════════════
def huegel(y, farbe1="#b9dd8c", farbe2="#8fc063", w=480, h=288, amp=14, phase=0.0):
    """Sanfter Hügelzug; Oberkante bei etwa y."""
    pts = []
    n = 12
    for i in range(n + 1):
        px = w * i / n
        py = y + amp * math.sin(i * .9 + phase) + amp * .5 * math.sin(i * 2.1 + phase)
        pts.append((px, py))
    d = f"M0,{h} L{pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(f"L{px:.1f},{py:.1f}" for px, py in pts[1:]) + f" L{w},{h} Z"
    gid = f"gh{int(y)}{int(phase * 10)}"
    return (f"<linearGradient id='{gid}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{farbe1}'/><stop offset='1' stop-color='{farbe2}'/></linearGradient>"
            f"<path d='{d}' fill='url(#{gid})'/>")


def ferne_baeume(xs, y, s=.6, farbe="#5f9a52"):
    return "".join(f"<g opacity='.85'>{baum(x, y, s, laub=farbe)}</g>" for x in xs)


def obstbaum(x, y, s=1.0, bluete=True, fruechte=False):
    """Apfelbaum (Stamm, Krone, weiße Blüten oder rote Äpfel); Krone ≈ 110 breit bei s = 1."""
    o = ("<path d='M-8,0 C-7,-20 -10,-30 -14,-46 L-6,-48 C-4,-38 -2,-34 0,-30 C2,-34 4,-38 8,-48 L16,-44 C12,-30 8,-20 9,0 Z' fill='url(#gStamm)' stroke='#4a2f17' stroke-width='1.4'/>")
    kronen = [(0, -78, 40), (-30, -66, 28), (30, -66, 28), (-16, -98, 26), (18, -98, 26), (0, -62, 30)]
    for cx, cy, r in kronen:
        o += f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='url(#gLaub)' stroke='#2a6a2a' stroke-width='1.2'/>"
    o += "<ellipse cx='-10' cy='-96' rx='26' ry='12' fill='#fff' opacity='.12'/>"
    rng = random.Random(3)
    if fruechte:
        for (cx, cy) in ((-32, -62), (-12, -50), (20, -56), (34, -70), (-4, -82), (14, -96), (-24, -90)):
            o += f"<circle cx='{cx}' cy='{cy}' r='6.4' fill='url(#sApfel)' stroke='#7a1310' stroke-width='1'/><ellipse cx='{cx - 2}' cy='{cy - 2.4}' rx='1.6' ry='2.4' fill='#fff' opacity='.6'/>"
    if bluete:
        for (cx, cy) in ((-36, -70), (-20, -92), (4, -104), (28, -90), (40, -66), (-8, -66), (18, -72), (-30, -52), (30, -50)):
            o += apfelbluete(cx, cy, .3, rng.randrange(0, 70))
    return schatten(x, y, 36 * s, 5 * s) + _g(x, y, s, o)
