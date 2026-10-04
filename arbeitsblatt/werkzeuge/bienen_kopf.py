"""Kopf der Honigbiene von vorn (Schaubild koerper-2, Glossar Facettenauge).

Lokale Koordinaten: Kopfmitte = (0, 0); Breite ≈ 192, Höhe ≈ 180 plus Rüssel (bis y ≈ 200).
"""
from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz

KOPF_V_D = ("M-96,-24 C-98,-72 -50,-94 0,-94 C50,-94 98,-72 96,-24 C94,26 66,62 30,80 C14,88 -14,88 -30,80 "
            "C-66,62 -94,26 -96,-24 Z")

_bz.DEFS_EXTRA.append(
    "<radialGradient id='bKopfV' cx='.5' cy='.4' r='.75'><stop offset='0' stop-color='#8a6a42'/><stop offset='.6' stop-color='#3c2813'/><stop offset='1' stop-color='#1a0f06'/></radialGradient>"
    "<radialGradient id='bAugeV' cx='.38' cy='.3' r='.9'><stop offset='0' stop-color='#9a7a52'/><stop offset='.4' stop-color='#4a3320'/><stop offset='1' stop-color='#0e0703'/></radialGradient>"
    "<linearGradient id='bClyp' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b4884e'/><stop offset='1' stop-color='#6a4524'/></linearGradient>"
    "<linearGradient id='bMand' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#9a6a38'/><stop offset='1' stop-color='#3e2410'/></linearGradient>"
    "<linearGradient id='bBeinQuer' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#4a2f18'/><stop offset='.5' stop-color='#a8743c'/><stop offset='1' stop-color='#4a2f18'/></linearGradient>"
)


def _fuehler_vorn(vz):
    """Ein Fühler (vz = +1 rechts, −1 links): Schaft, Knick, Geißel mit Gliedern."""
    def X(x):
        return x * vz
    sock = f"M{X(20)},4 C{X(36)},-14 {X(50)},-40 {X(60)},-70"
    gei = f"M{X(60)},-70 C{X(84)},-94 {X(120)},-100 {X(144)},-86 C{X(158)},-78 {X(164)},-68 {X(166)},-58"
    return (f"<path d='{sock}' fill='none' stroke='#120a04' stroke-width='9' stroke-linecap='round'/>"
            f"<path d='{sock}' fill='none' stroke='#7a5334' stroke-width='6' stroke-linecap='round'/>"
            f"<path d='{sock}' fill='none' stroke='#c19a6a' stroke-width='1.8' stroke-linecap='round' transform='translate({-1.5 * vz} -1)'/>"
            f"<path d='{gei}' fill='none' stroke='#120a04' stroke-width='7.4' stroke-linecap='round'/>"
            f"<path d='{gei}' fill='none' stroke='#5a3d26' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='{gei}' fill='none' stroke='#d6b78a' stroke-width='5' stroke-dasharray='1.2 7.6'/>"
            f"<path d='{gei}' fill='none' stroke='#8a6a4a' stroke-width='1.4' stroke-linecap='round' transform='translate(0 -1.8)' opacity='.8'/>"
            f"<circle cx='{X(60)}' cy='-70' r='4.6' fill='#4a3320' stroke='#120a04' stroke-width='1.2'/>")


def kopf_vorn(ruessel=True, tropfen=True, seed=31):
    """Kopf einer Arbeiterin von vorn: Fühler, zwei Facettenaugen, drei Punktaugen, Mundwerkzeuge, Rüssel."""
    o = []
    # Haarkranz hinter dem Kopf
    o.append(haare(0, -10, 98, 86, 90, 15, "#b88b3d", 1.5, a0=160, a1=380, richtung=(0, -.2), aussen=1.0, seed=seed, einwaerts=3))
    o.append(haare(0, -10, 98, 86, 70, 13, "#e6c06a", 1.3, a0=170, a1=370, richtung=(0, -.2), aussen=1.0, seed=seed + 1, einwaerts=3))
    # Rüssel (hinter den Mandibeln)
    if ruessel:
        o.append("<g>"
                 "<path d='M-12,70 C-12,100 -9,130 -6,160 L6,160 C9,130 12,100 12,70 Z' fill='#2a170a' stroke='#120a04' stroke-width='1.4'/>"
                 "<path d='M-9,72 C-9,100 -6,130 -4,158 L4,158 C6,130 9,100 9,72 Z' fill='url(#bBeinQuer)'/>"
                 "<path d='M-6,78 C-5,104 -3,130 -2,156' fill='none' stroke='#e8c286' stroke-width='1.6' stroke-linecap='round' opacity='.9'/>"
                 "<path d='M-9,92 h18 M-8,108 h16 M-7,124 h14 M-6,140 h12' stroke='#1a0e05' stroke-width='1.1' opacity='.55'/>"
                 "<path d='M-3,158 C-4,172 -2,184 0,190 C2,184 4,172 3,158 Z' fill='#c58a45' stroke='#2a170a' stroke-width='1.1'/>"
                 "<path d='M-3,166 l-5,2 M-3,174 l-5,2 M3,166 l5,2 M3,174 l5,2' stroke='#e6c06a' stroke-width='1' stroke-linecap='round'/>"
                 "</g>")
        if tropfen:
            o.append("<g><ellipse cx='0' cy='196' rx='7.5' ry='8.5' fill='url(#bNektar)' stroke='#c47500' stroke-width='1'/>"
                     "<ellipse cx='-2.5' cy='193' rx='2.2' ry='3.2' fill='#fff' opacity='.85'/></g>")
    # Kopfkapsel
    o.append(f"<path d='{KOPF_V_D}' fill='url(#bKopfV)' stroke='#120a04' stroke-width='1.5'/>")
    o.append(f"<path d='{KOPF_V_D}' fill='url(#bVol)' opacity='.7'/>")
    # Haare auf Stirn und Wangen
    o.append(flaum(0, -62, 52, 22, 46, 10, "#e9c56e", 1.4, richtung=(0, -1), seed=seed + 2, opa=.9))
    o.append(flaum(0, -30, 20, 34, 40, 8, "#d8c9a4", 1.2, richtung=(0, -1), seed=seed + 3, opa=.75))
    o.append(flaum(-80, 40, 20, 30, 18, 8, "#cdb27a", 1.2, richtung=(-.5, .6), seed=seed + 4, opa=.8))
    o.append(flaum(80, 40, 20, 30, 18, 8, "#cdb27a", 1.2, richtung=(.5, .6), seed=seed + 5, opa=.8))
    # Clypeus (Untergesicht) und Oberlippe
    o.append("<path d='M-36,24 C-30,12 30,12 36,24 C34,48 28,64 20,70 L-20,70 C-28,64 -34,48 -36,24 Z' fill='url(#bClyp)' stroke='#3b2410' stroke-width='1.2'/>"
             "<path d='M-18,66 C-18,58 18,58 18,66 C18,78 10,82 0,82 C-10,82 -18,78 -18,66 Z' fill='#7a4f26' stroke='#2a170a' stroke-width='1.2'/>"
             "<path d='M-24,34 C-12,28 12,28 24,34' fill='none' stroke='#e7cf9a' stroke-width='1.6' opacity='.55' stroke-linecap='round'/>")
    o.append(flaum(0, 38, 26, 16, 14, 6, "#f0dca0", 1.1, richtung=(0, 1), seed=seed + 6, opa=.8))
    # Facettenaugen
    for vz in (-1, 1):
        o.append(f"<g transform='translate({64 * vz} -10) rotate({10 * -vz})'>"
                 "<ellipse rx='34' ry='57' fill='url(#bAugeV)' stroke='#0a0502' stroke-width='1.4'/>"
                 "<ellipse rx='34' ry='57' fill='url(#bHexM)'/>"
                 f"<ellipse cx='{-11 * vz}' cy='-24' rx='9' ry='18' fill='url(#bGlanz)' opacity='.9' transform='rotate({14 * vz} {-11 * vz} -24)'/>"
                 f"<ellipse cx='{12 * vz}' cy='28' rx='5' ry='9' fill='url(#bGlanz)' opacity='.35'/>"
                 "</g>")
        o.append(haare(64 * vz, -10, 34, 57, 36, 7, "#b38a4a", 1.1, rot=10 * -vz, a0=0, a1=360, richtung=(0, 0), aussen=1.0, seed=seed + 10 + vz, einwaerts=1))
    # Punktaugen
    for (px, py) in ((-23, -66), (23, -66), (0, -44)):
        o.append(f"<g><circle cx='{px}' cy='{py}' r='7.5' fill='#3a2412' stroke='#120a04' stroke-width='1.2'/>"
                 f"<circle cx='{px}' cy='{py}' r='5.6' fill='#e7c777'/><circle cx='{px - 1.5}' cy='{py - 1.8}' r='2.4' fill='#fff' opacity='.9'/>"
                 f"<circle cx='{px + 1.5}' cy='{py + 1.5}' r='3' fill='#b8801e' opacity='.45'/></g>")
    # Mandibeln
    for vz in (-1, 1):
        o.append(f"<g transform='scale({vz} 1)'>"
                 "<path d='M30,66 C44,70 50,86 40,100 C36,106 26,100 28,92 C32,90 34,80 30,72 Z' fill='url(#bMand)' stroke='#120a04' stroke-width='1.3' stroke-linejoin='round'/>"
                 "<path d='M34,70 C42,76 44,86 38,96' fill='none' stroke='#d5a56a' stroke-width='1.3' stroke-linecap='round' opacity='.8'/>"
                 "<path d='M28,92 l4,3 l2,-6' fill='none' stroke='#120a04' stroke-width='1' stroke-linejoin='round'/></g>")
    # Fühlergruben
    for vz in (-1, 1):
        o.append(f"<circle cx='{20 * vz}' cy='4' r='9' fill='#2a170a' stroke='#120a04' stroke-width='1.2'/>"
                 f"<circle cx='{20 * vz}' cy='4' r='6' fill='#6b4a2c'/>")
    o.append(_fuehler_vorn(-1))
    o.append(_fuehler_vorn(1))
    return "".join(o)
