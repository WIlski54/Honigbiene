"""Hinterbein der Honigbiene mit Pollenkörbchen, Pollenhöschen und Bürste (koerper-5, Glossar Pollenkörbchen).

Lokale Koordinaten: Hüfte bei (0, 0), das Bein läuft nach rechts unten; Länge etwa 345, Höhe etwa 150.
Teile: Schenkel (Femur), Schiene (Tibia) mit Körbchen, Pollen-Höschen, Fersenglied (Basitarsus) mit Bürste,
vier kleine Fußglieder mit Klauen.
"""
import math
import random

from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz

_bz.DEFS_EXTRA.append(
    "<linearGradient id='bRohr' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b98a55'/><stop offset='.45' stop-color='#7a4f2a'/><stop offset='1' stop-color='#3e2511'/></linearGradient>"
    "<linearGradient id='bRohrD' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#8a5a30'/><stop offset='.5' stop-color='#5a3a1c'/><stop offset='1' stop-color='#2a170a'/></linearGradient>"
    "<linearGradient id='bKoerbchen' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#6a3f16'/><stop offset='.5' stop-color='#c0883c'/><stop offset='1' stop-color='#4d2c0e'/></linearGradient>"
    "<radialGradient id='bHoeschen' cx='.4' cy='.3' r='.85'><stop offset='0' stop-color='#fff59a'/><stop offset='.45' stop-color='#f7c21e'/><stop offset='1' stop-color='#b96f06'/></radialGradient>"
)


# Maße des Beins (lokal) und wichtige Punkte für Beschriftungen
KX, KY, ANG_T, LT = 94, 20, 17.4, 146
ANG_B, BL = 30, 70


def _loc(ox, oy, ang, x, y):
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return ox + x * c - y * sn, oy + x * sn + y * c


TX, TY = _loc(KX, KY, ANG_T, LT, 0)
MARKEN = {
    "femur": (50, 0),
    "koerbchen": _loc(KX, KY, ANG_T, LT * .4, 0),          # sichtbare Körbchenfläche nahe dem Knie
    "hoeschen": _loc(KX, KY, ANG_T, LT * .78, 0),
    "buerste": _loc(TX, TY, ANG_B, BL * .5, 18),            # Unterkante des Fersenglieds
    "kralle": (TX + 128, TY + 66),
}


def _seg(L, w0, w1, fill="url(#bRohr)", rand="#1c1006"):
    """Kegelförmiges Gliedstück in Standardlage (Anfang im Ursprung, Ende bei x = L), mit abgerundeten Enden."""
    r0, r1 = w0 / 2, w1 / 2
    d = (f"M0,{-r0:.1f} L{L},{-r1:.1f} A{r1:.1f},{r1:.1f} 0 0 1 {L},{r1:.1f} L0,{r0:.1f} A{r0:.1f},{r0:.1f} 0 0 1 0,{-r0:.1f} Z")
    return (f"<path d='{d}' fill='{fill}' stroke='{rand}' stroke-width='1.5' stroke-linejoin='round'/>"
            f"<path d='M{r0 * .2:.1f},{-r0 * .6:.1f} L{L - 2},{-r1 * .62:.1f}' stroke='#fff' stroke-width='{max(w1 * .12, 1):.1f}' stroke-linecap='round' opacity='.3'/>")


def _frame(x, y, ang, inhalt):
    return f"<g transform='translate({x:.1f} {y:.1f}) rotate({ang:.1f})'>{inhalt}</g>"


def _pollenkorn_textur(cx, cy, rx, ry, n, seed):
    """Körnige Oberfläche des Höschens: viele kleine helle und dunkle Körner."""
    rng = random.Random(seed)
    hell, dunkel = [], []
    for i in range(n):
        r = math.sqrt(rng.random())
        th = rng.random() * 2 * math.pi
        x, y = cx + r * rx * .92 * math.cos(th), cy + r * ry * .92 * math.sin(th)
        (hell if i % 3 else dunkel).append(f"M{x:.1f},{y:.1f}h.1")
    return (f"<path d='{''.join(hell)}' stroke='#fff6a8' stroke-width='3' stroke-linecap='round' opacity='.75'/>"
            f"<path d='{''.join(dunkel)}' stroke='#b9700a' stroke-width='2.6' stroke-linecap='round' opacity='.6'/>")


def hinterbein_gross(pollen=True, detail=True):
    """Hinterbein im Ganzen (siehe Modulkopf). Rückgabe: SVG-Gruppeninhalt."""
    o = []
    kx, ky, ang_t, Lt = KX, KY, ANG_T, LT
    tx, ty = TX, TY
    # Schenkel (Femur) mit Haaren
    o.append(_frame(0, 0, 12, _seg(96, 34, 26)))
    o.append(haare_linie(6, -15, 98, -10, 70, 15, "#e8c05a", 1.4, richtung=(.5, -1), seed=3))
    o.append(haare_linie(6, 15, 98, 14, 60, 13, "#c9983f", 1.3, richtung=(.5, 1), seed=4))
    o.append(haare_linie(10, -8, 94, -2, 50, 9, "#f6d672", 1.2, richtung=(.6, -.8), seed=6, opa=.8))
    o.append(f"<circle cx='{kx}' cy='{ky}' r='11' fill='url(#bRohrD)' stroke='#1c1006' stroke-width='1.5'/>")

    # Schiene (Tibia): löffelförmig, Körbchen auf der Außenseite
    def w(s):
        return 14 + 50 * s ** 1.2
    n = 26
    top = [(Lt * i / n, -w(i / n) / 2) for i in range(n + 1)]
    bot = [(Lt * i / n, w(i / n) / 2) for i in range(n, -1, -1)]
    r_end = w(1) / 2
    pts = " L".join(f"{x:.1f},{y:.1f}" for x, y in top)
    pts2 = " L".join(f"{x:.1f},{y:.1f}" for x, y in bot)
    tibia = (f"<path d='M{pts} Q{Lt + r_end * 1.15:.1f},0 {pts2} Z' fill='url(#bRohr)' stroke='#1c1006' stroke-width='1.5' stroke-linejoin='round'/>")
    # Körbchen (glatte, vertiefte Fläche)
    korb = []
    for i in range(n + 1):
        s = .32 + .62 * i / n
        korb.append((Lt * s, -w(s) * .3))
    for i in range(n, -1, -1):
        s = .32 + .62 * i / n
        korb.append((Lt * s, w(s) * .3))
    kpts = " L".join(f"{x:.1f},{y:.1f}" for x, y in korb)
    tibia += (f"<path d='M{kpts} Z' fill='url(#bKoerbchen)' stroke='#3a200a' stroke-width='1.2' stroke-linejoin='round'/>"
              f"<path d='M{Lt * .38:.1f},{-w(.38) * .2:.1f} Q{Lt * .62:.1f},{-w(.62) * .26:.1f} {Lt * .9:.1f},{-w(.9) * .25:.1f}' fill='none' stroke='#ffe6b0' stroke-width='2.4' stroke-linecap='round' opacity='.55'/>")
    o.append(_frame(kx, ky, ang_t, tibia))
    # Fersenglied (Basitarsus) mit Bürste
    ang_b = ANG_B
    bl, bw0, bw1 = BL, 38, 36
    bas = _seg(bl, bw0, bw1, "url(#bRohr)")
    rng = random.Random(5)
    reihen = []
    for i in range(9):
        x = 8 + i * (bl - 12) / 8
        reihen.append(f"M{x:.1f},{-bw1 * .42:.1f} q3,{bw1 * .42:.1f} 0,{bw1 * .9:.1f}")
    bas += f"<path d='{''.join(reihen)}' fill='none' stroke='#2a170a' stroke-width='2' stroke-linecap='round'/>"
    spitzen = []
    for i in range(18):
        x = 6 + i * (bl - 10) / 17
        spitzen.append(f"M{x:.1f},{bw1 * .42:.1f} l{rng.uniform(-1, 2):.1f},{rng.uniform(5, 9):.1f}")
    bas += f"<path d='{''.join(spitzen)}' fill='none' stroke='#3b2410' stroke-width='1.5' stroke-linecap='round'/>"
    bas += f"<path d='M6,{-bw1 * .3:.1f} L{bl - 4},{-bw1 * .3:.1f}' stroke='#e8c286' stroke-width='1.6' stroke-linecap='round' opacity='.55'/>"
    o.append(_frame(tx, ty, ang_b, bas))
    # Pollenpresse (Aurikel) am Ende der Schiene
    o.append(_frame(tx, ty, ang_b - 8, "<path d='M-4,-6 l8,-4 l2,10 l-6,8 z' fill='#2a170a' stroke='#150d06' stroke-width='1'/>"
                    "<path d='M-1,-5 l5,-2 M0,-1 l5,-1 M-1,3 l4,0' stroke='#c8975a' stroke-width='.8'/>"))
    # kleine Fußglieder
    bx_, by_ = tx + bl * math.cos(math.radians(ang_b)), ty + bl * math.sin(math.radians(ang_b))
    a = ang_b + 6
    for L, w0, w1 in ((22, 17, 14), (17, 14, 12), (14, 12, 10), (14, 10, 9)):
        o.append(_frame(bx_, by_, a, _seg(L, w0, w1, "url(#bRohrD)")))
        bx_, by_ = bx_ + L * math.cos(math.radians(a)), by_ + L * math.sin(math.radians(a))
        a += 7
    # Klauen und Haftlappen
    o.append(_frame(bx_, by_, a, "<path d='M2,-3 q9,-1 12,7 M2,3 q9,3 8,11' fill='none' stroke='#150d06' stroke-width='2.2' stroke-linecap='round'/>"
                    "<path d='M2,0 q6,2 9,0' fill='none' stroke='#d9b078' stroke-width='3' stroke-linecap='round'/>"))
    # Körbchenhaare (gebogen, halten das Höschen)
    hh = []
    for i in range(15):
        s = .34 + .6 * i / 14
        x = Lt * s
        yo = -w(s) / 2
        hh.append(f"M{x:.1f},{yo:.1f} q{6 + (i % 3) * 2},{12 + (i % 2) * 4} {13 + (i % 4)},{w(s) * .5:.1f}")
        yu = w(s) / 2
        hh.append(f"M{x + 3:.1f},{yu:.1f} q{5 + (i % 3) * 2},{-12 - (i % 2) * 4} {12 + (i % 4)},{-w(s) * .46:.1f}")
    korbhaare = (f"<path d='{''.join(hh)}' fill='none' stroke='#2f1a08' stroke-width='2.1' stroke-linecap='round'/>"
                 f"<path d='{''.join(hh)}' fill='none' stroke='#d5a24a' stroke-width='.9' stroke-linecap='round' transform='translate(-.6 -.6)'/>")
    # Pollenhöschen
    if pollen:
        px, py_, prx, pry = Lt * .78, 1, 50, 31
        hoesch = (f"<g><ellipse cx='{px:.1f}' cy='{py_ + 4}' rx='{prx + 2}' ry='{pry + 2}' fill='#000' opacity='.18' filter='url(#bWeich2)'/>"
                  f"<ellipse cx='{px:.1f}' cy='{py_}' rx='{prx}' ry='{pry}' fill='url(#bHoeschen)' stroke='#a8650a' stroke-width='1.4'/>"
                  + _pollenkorn_textur(px, py_, prx, pry, 120, 7)
                  + f"<ellipse cx='{px - 14:.1f}' cy='{py_ - 12}' rx='13' ry='6' fill='url(#bGlanz)' opacity='.8' transform='rotate(-14 {px - 14:.1f} {py_ - 12})'/></g>")
        o.append(_frame(kx, ky, ang_t, hoesch + korbhaare))
    else:
        o.append(_frame(kx, ky, ang_t, korbhaare))
    return "".join(o)
