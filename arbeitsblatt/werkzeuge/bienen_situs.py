"""Hinterleib im Längsschnitt (koerper-4) und Biene im Schnitt (Glossar Honigmagen).

Lokale Koordinaten = Koordinaten von HL_D (x −216 … −36, y −50 … 52), Blick nach rechts.
Organe: Honigmagen (mit Nektar), Mitteldarm, Dünndarm, Enddarm, Herz (Rückengefäß), Giftblase mit Stachel,
vier Wachsdrüsen mit Wachsplättchen an der Bauchseite.
"""
from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz

_bz.DEFS_EXTRA.append(
    "<radialGradient id='bCreme' cx='.55' cy='.4' r='.8'><stop offset='0' stop-color='#fffaf0'/><stop offset='.7' stop-color='#fdeec2'/><stop offset='1' stop-color='#f1d28c'/></radialGradient>"
    "<linearGradient id='bSackW' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffe2ea'/><stop offset='1' stop-color='#e07a9c'/></linearGradient>"
    "<linearGradient id='bMitteldarm' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d3c36a'/><stop offset='.5' stop-color='#a39a3c'/><stop offset='1' stop-color='#6a6320'/></linearGradient>"
    "<linearGradient id='bDruese' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff4b8'/><stop offset='1' stop-color='#e9c04c'/></linearGradient>"
    "<linearGradient id='bGiftW' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#f1faff'/><stop offset='1' stop-color='#8cc2e0'/></linearGradient>"
    "<linearGradient id='bDarmRosa' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffe0e8'/><stop offset='1' stop-color='#e48fa8'/></linearGradient>"
)


def _bauch_y(x):
    """y der Bauchlinie (Unterseite) des Hinterleibs bei x (aus HL_D, Kurve von (−200,24) nach (−62,36))."""
    p0, p1, p2, p3 = (-200, 24), (-178, 44), (-112, 52), (-62, 36)
    best = None
    for i in range(201):
        u = i / 200
        bx = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
        by = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
        if best is None or abs(bx - x) < abs(best[0] - x):
            best = (bx, by)
    return best[1]


def roehre(d, breite, farbe, rand="#3b2a10", glanz="#ffffff", glanz_opa=.45, ringe=None):
    """Röhrenförmiges Organ entlang eines Pfads: Rand, Füllung, Glanzlicht, optionale Ringe."""
    o = (f"<path d='{d}' fill='none' stroke='{rand}' stroke-width='{breite + 2.4}' stroke-linecap='round' stroke-linejoin='round'/>"
         f"<path d='{d}' fill='none' stroke='{farbe}' stroke-width='{breite}' stroke-linecap='round' stroke-linejoin='round'/>")
    if ringe:
        o += f"<path d='{d}' fill='none' stroke='{rand}' stroke-width='{breite - 1}' stroke-dasharray='1.1 {ringe}' opacity='.45'/>"
    o += (f"<path d='{d}' fill='none' stroke='{glanz}' stroke-width='{max(breite * .22, 1):.1f}' stroke-linecap='round' "
          f"opacity='{glanz_opa}' transform='translate(0 {-breite * .22:.1f})'/>")
    return o


CROP_D = "M-44,2 C-44,-24 -70,-35 -92,-28 C-116,-21 -120,2 -113,15 C-107,31 -80,37 -62,31 C-50,27 -44,16 -44,2 Z"


def brust_stumpf():
    """Angeschnittene Brust am vorderen Ende des Hinterleibs (Pelzrand, Schnittfläche, Flugmuskeln, Speiseröhre)."""
    return (haare(6, 0, 46, 42, 40, 8, "#c88a30", 1.4, seed=81, aussen=.9, richtung=(0, 0), einwaerts=2)
            + haare(6, 0, 46, 42, 36, 8, "#f4c94f", 1.1, seed=82, aussen=.9, richtung=(0, 0), einwaerts=2)
            + "<ellipse cx='6' cy='0' rx='46' ry='42' fill='url(#bBrust)' filter='url(#bFuzz)'/>"
              "<ellipse cx='6' cy='0' rx='37' ry='33' fill='url(#bCreme)' stroke='#c9a24a' stroke-width='1.6'/>"
              "<path d='M-26,-10 C-22,-26 34,-26 38,-10 C39,2 28,8 6,8 C-16,8 -28,2 -26,-10 Z' fill='url(#bMusk)' stroke='#6e1814' stroke-width='1.2'/>"
              "<path d='M-16,-12 C4,-17 22,-17 32,-12 M-18,-5 C4,-10 22,-10 32,-5' fill='none' stroke='#f9b0a2' stroke-width='.8' opacity='.6'/>"
              "<path d='M-6,24 L-40,12 M-6,24 L12,34' fill='none' stroke='#fff' stroke-width='0'/>")


def situs_hinterleib(stachel_aus=True, nur_honigmagen=False, mit_brust=True, mit_speiseroehre=True, hervor=None):
    """Hinterleib im Längsschnitt (lokal wie HL_D). `hervor="honigmagen"` blendet die übrigen Organe blasser ein."""
    o = []
    # Brust (angeschnitten, Pelzrand) hinter dem Hinterleib
    if mit_brust:
        o.append(brust_stumpf())
    # Außenwand mit Streifen
    o.append(_bz.abdomen())
    # Schnittfläche (kleiner als die Außenwand → die gestreifte Körperwand bleibt als Rand sichtbar)
    o.append(f"<g transform='translate(-126 2) scale(.86 .74) translate(126 -2)'><path d='{HL_D}' fill='url(#bCreme)' stroke='#c9a24a' stroke-width='1.8'/></g>")
    rest = []
    if not nur_honigmagen:
        # Wachsdrüsen (Bauchseite) und Wachsplättchen
        segs = [(-62, -88), (-88, -116), (-116, -146), (-146, -178)]
        for xa, xb in segs:
            xm = (xa + xb) / 2
            yb = _bauch_y(xm)
            w = abs(xa - xb) - 5
            ang = math.degrees(math.atan2(_bauch_y(xb) - _bauch_y(xa), xb - xa))
            rest.append(f"<g transform='translate({xm:.1f} {yb - 6.5:.1f}) rotate({ang:.1f})'>"
                        f"<rect x='{-w / 2:.1f}' y='-4.6' width='{w:.1f}' height='9.2' rx='3.4' fill='url(#bDruese)' stroke='#b88a14' stroke-width='1'/>"
                        f"<path d='M{-w / 2 + 3:.1f},-1.8 h{w - 6:.1f} M{-w / 2 + 3:.1f},1.8 h{w - 6:.1f}' stroke='#c9a03a' stroke-width='.9' stroke-dasharray='1.2 2'/></g>")
            xe = xb + 2
            ye = _bauch_y(xe) + 1
            rest.append(f"<g transform='translate({xe:.1f} {ye:.1f}) rotate(24)'><path d='M0,0 L9,-1 C12,2 11,7 6,8 L-1,6 Z' fill='#fffbe6' stroke='#cdb273' stroke-width='.9'/>"
                        f"<path d='M2,2 L8,1' stroke='#e8d9a8' stroke-width='.8'/></g>")
        # Herz (Rückengefäß)
        rest.append(roehre("M-48,-20 C-66,-30 -110,-35 -150,-26 C-168,-21 -180,-12 -186,-6", 4.6, "#cf4a3d", "#6e1814", "#ffd0c8", .5, ringe=7))
        # Ventil (Vormagen) und Mitteldarm
        rest.append("<circle cx='-117' cy='7' r='5.4' fill='#d9879f' stroke='#8e2e55' stroke-width='1.3'/>")
        rest.append(roehre("M-122,6 C-138,-3 -156,-3 -172,5", 20, "url(#bMitteldarm)", "#4b4416", "#fff7bd", .5, ringe=5.2))
        # Dünndarm (Schlinge) und Enddarm
        rest.append(roehre("M-170,8 C-166,26 -142,28 -138,16 C-135,8 -150,5 -156,12", 6.4, "#9a8d3a", "#4b4416", "#f3eaa0", .55))
        rest.append(roehre("M-171,12 C-176,20 -184,16 -187,9", 6.2, "#8f8236", "#4b4416", "#f3eaa0", .5))
        rest.append("<ellipse cx='-192' cy='8' rx='9.6' ry='7' fill='#7a6e28' stroke='#3b3410' stroke-width='1.3'/>"
                    "<ellipse cx='-194' cy='5' rx='4' ry='2' fill='#e8dd8a' opacity='.6'/>")
        # Giftblase und Stachel
        rest.append("<path d='M-186,26 C-174,15 -152,15 -144,25 C-143,34 -156,37 -170,35 C-181,34 -189,32 -186,26 Z' fill='url(#bGiftW)' stroke='#4f8eb5' stroke-width='1.6'/>"
                    "<ellipse cx='-165' cy='22' rx='10' ry='2.8' fill='#fff' opacity='.75'/>"
                    "<path d='M-144,25 C-139,22 -136,16 -134,10 M-144,26 C-138,28 -132,26 -128,22' fill='none' stroke='#a9d0e6' stroke-width='1.8' stroke-linecap='round'/>")
        if stachel_aus:
            rest.append("<path d='M-188,25 L-218,19 L-224,22 L-190,31 Z' fill='url(#bChitin)' stroke='#3a1f06' stroke-width='1.2' stroke-linejoin='round'/>"
                        "<path d='M-200,23 l-2,4 M-206,24 l-2,4 M-212,22 l-2,4' stroke='#3a1f06' stroke-width='1' stroke-linecap='round'/>"
                        "<circle cx='-188' cy='28' r='4.2' fill='#8a5a22' stroke='#3a1f06' stroke-width='1.1'/>")
    o.append(f"<g opacity='.4'>{''.join(rest)}</g>" if hervor else "".join(rest))
    # Honigmagen: Wand, Nektar, Glanz
    o.append("<g transform='translate(-81 3) scale(.88 .84) translate(81 -3)'>"
             f"<path d='{CROP_D}' fill='url(#bSackW)' stroke='#c04a73' stroke-width='2.4' stroke-linejoin='round'/>"
             f"<g transform='translate(-81 3) scale(.84) translate(81 -3)'><path d='{CROP_D}' fill='url(#bNektar)' stroke='#d98200' stroke-width='1.2'/></g>"
             "<ellipse cx='-91' cy='-16' rx='11' ry='5' fill='#fff' opacity='.7' transform='rotate(-24 -91 -16)'/>"
             "<circle cx='-62' cy='10' r='3.2' fill='#fff' opacity='.55'/><circle cx='-72' cy='20' r='2.2' fill='#fff' opacity='.5'/>"
             "<circle cx='-98' cy='12' r='2.6' fill='#fff' opacity='.45'/></g>")
    if mit_speiseroehre:
        o.append(roehre("M10,22 C-4,22 -16,10 -28,6 C-34,4 -40,4 -47,3", 5.4, "url(#bDarmRosa)", "#b4607a", "#fff", .5))
    return "".join(o)


# ═══════════════════════════════════════════════════════════════════════════
#  Ganze Biene im Längsschnitt (lokal wie biene_seite): Kopf, Brust, Hinterleib, Speiseröhre mit Nektar-Tropfen
# ═══════════════════════════════════════════════════════════════════════════
WEG = "M98,34 C86,30 74,24 62,18 C46,12 30,12 12,14 C-6,14 -22,8 -36,5 C-41,4 -44,3 -47,3"   # Mund → Speiseröhre → Honigmagen


def _punkt_auf_weg(d, t):
    """Punkt auf einem aus Kubik-Bézier-Stücken (M … C … C …) zusammengesetzten Weg; t = 0…1 über alle Stücke."""
    import re
    z = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
    sx, sy = z[0], z[1]
    segs = []
    i = 2
    while i + 5 < len(z):
        segs.append(((sx, sy), (z[i], z[i + 1]), (z[i + 2], z[i + 3]), (z[i + 4], z[i + 5])))
        sx, sy = z[i + 4], z[i + 5]
        i += 6
    n = len(segs)
    k = min(int(t * n), n - 1)
    u = t * n - k
    p0, p1, p2, p3 = segs[k]
    a = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
    return (a[0] * p0[0] + a[1] * p1[0] + a[2] * p2[0] + a[3] * p3[0],
            a[0] * p0[1] + a[1] * p1[1] + a[2] * p2[1] + a[3] * p3[1])


def biene_schnitt(ruessel_ende=(160, 66), tropfen_n=5):
    """Ganze Biene im Längsschnitt ohne Beine und Flügel. Der Rüssel läuft zu `ruessel_ende`; Nektar-Tropfen wandern
    durch Rüssel und Speiseröhre in den Honigmagen."""
    o = []
    # drei Beine der nahen Seite (hinter dem Körper) und ferne Flügel
    for pts, dk in BEINE_NAH.values():
        o.append(bein(pts, dk, haare_n=6, seed=7))
    o.append(fluegel_platz(-2, -36, 206, 168, 46, "vor", .5))
    # Hinterleib (Honigmagen betont) – Brust und Speiseröhre zeichnen wir hier selbst
    o.append(situs_hinterleib(mit_brust=False, mit_speiseroehre=False, hervor="honigmagen"))
    # Brust im Schnitt (Pelzrand, Schnittfläche, Flugmuskeln)
    o.append("<g transform='translate(-6 0)'>" + brust_stumpf() + "</g>")
    # Kopf im Schnitt
    o.append(f"<path d='{KOPF_D}' fill='url(#bKopf)' stroke='#150d06' stroke-width='1.6'/>")
    o.append(f"<path d='{KOPF_D}' fill='url(#bCreme)' stroke='#c9a24a' stroke-width='1.6' transform='translate(76 4) scale(.84) translate(-76 -4)'/>")
    o.append("<ellipse cx='95' cy='-4' rx='7' ry='19' fill='url(#bAuge)' stroke='#0c0602' stroke-width='1' transform='rotate(8 95 -4)'/>"
             "<ellipse cx='95' cy='-4' rx='7' ry='19' fill='url(#bHex)' transform='rotate(8 95 -4)'/>")
    o.append("<path d='M62,-18 C58,-30 74,-34 82,-26 C90,-20 84,-8 76,-8 C68,-6 64,-10 62,-18 Z' fill='#e8d2d6' stroke='#a98390' stroke-width='1.3'/>"
             "<path d='M66,-22 C70,-26 76,-24 78,-20 M68,-14 C72,-18 78,-14 80,-12' fill='none' stroke='#b99aa5' stroke-width='1'/>")
    # Rüssel nach außen
    ex, ey = ruessel_ende
    o.append(roehre(f"M99,34 C108,44 {ex - 30},{ey - 10} {ex},{ey}", 6.4, "#a8703a", "#2a1a0c", "#f0cf9a", .7))
    # Speiseröhre
    o.append(roehre(WEG, 5.4, "url(#bDarmRosa)", "#b4607a", "#fff", .5))
    # Flügel der nahen Seite
    o.append(fluegel_platz(-8, -38, 196, 184, 50, "vor", .9))
    o.append(fluegel_platz(-4, -38, 212, 122, 38, "hinter", .9))
    # Nektar-Tropfen in der Speiseröhre
    for i in range(tropfen_n):
        x, y = _punkt_auf_weg(WEG, .12 + i * .17)
        o.append(f"<g><circle cx='{x:.1f}' cy='{y:.1f}' r='3.6' fill='url(#bNektar)' stroke='#c47500' stroke-width='.8'/>"
                 f"<circle cx='{x - 1:.1f}' cy='{y - 1.2:.1f}' r='1.1' fill='#fff' opacity='.9'/></g>")
    return "".join(o)
