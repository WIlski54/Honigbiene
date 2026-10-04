"""Zeichenhelfer für die Schaubilder des Reiters „Nutzen & Schutz“ (grafiken_nutzen.py).

Gegenständliche Bausteine in eigenen Koordinaten: Biene von der Seite (mit Pollen oder Wachsplättchen),
Varroa-Milbe, Imker, Bienenkasten, Rähmchen mit Waben, Honigschleuder, Honigglas, Kerzen, Apfelblüte,
Apfel, Wiesenblumen, Insekten. Alle Farbverläufe haben die Vorsilbe `gn` (kollidieren nicht mit svg_helfer).

Jede Szene ruft `szene(...)` statt `svg(...)`: das hängt DEFS (Verläufe, Clip-Pfad der Biene) an. Muster für
Wabenzellen (`wabenmuster`) und weitere Defs gehen über `defs=`.

Regeln: Beschriftung nur über `beschr()` (Halo, Zeigelinie), Pfeile mit Beschriftung über/unter der Linie.
"""
import math
import random
import re

from svg_helfer import (BLAU, DUNKEL, GRAU, GRUEN, HELL, MAGENTA, ORANGE, ROT, TEXT, W, H, bogen, erzeuge,  # noqa: F401
                        gras, pfeil, sechseck, svg, t, tp)


def f(v):
    """Zahl kurz formatieren (Dateigröße)."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# ═══════════════════════════════════════════════════════════════════════════
#  Verläufe (Vorsilbe gn) und gemeinsame Defs
# ═══════════════════════════════════════════════════════════════════════════
def _lg(i, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f"<stop offset='{o}' stop-color='{c}'" + (f" stop-opacity='{op}'" if op is not None else "") + "/>"
                for o, c, op in [(a + (None,))[:3] if len(a) == 2 else a for a in stops])
    return f"<linearGradient id='{i}' x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}'>{s}</linearGradient>"


def _rg(i, stops, cx=.5, cy=.5, r=.5):
    s = "".join(f"<stop offset='{o}' stop-color='{c}'" + (f" stop-opacity='{op}'" if op is not None else "") + "/>"
                for o, c, op in [(a + (None,))[:3] if len(a) == 2 else a for a in stops])
    return f"<radialGradient id='{i}' cx='{cx}' cy='{cy}' r='{r}'>{s}</radialGradient>"


ABDOMEN = "M-8,-8 C-22,-13.5 -42,-10.5 -51,1.5 C-42,12.5 -22,14.5 -8,9.5 Z"

DEFS = (
    # Biene
    _lg("gnBGelb", [(0, "#ffdc62"), (.5, "#f4b01e"), (1, "#c37c0c")])
    + _lg("gnBDunkel", [(0, "#5f4324"), (1, "#32200e")])
    + _rg("gnThorax", [(0, "#f6c860"), (.55, "#b9741a"), (1, "#6c400e")], .4, .32, .75)
    + _rg("gnAuge", [(0, "#94725a"), (.5, "#4a2f20"), (1, "#1c0f09")], .35, .3, .8)
    + _lg("gnKopf", [(0, "#4a3826"), (1, "#1c130a")])
    + _lg("gnFlue", [(0, "#ffffff", .88), (1, "#b9daf1", .5)], 0, 1, 1, 0)
    + _rg("gnPollen", [(0, "#fff08a"), (.6, "#ffc928"), (1, "#e59a00")], .35, .3, .8)
    + _lg("gnWachsP", [(0, "#ffffff"), (1, "#f1e2a6")], 0, 0, 1, 1)
    # Blüte, Frucht, Laub
    + _lg("gnPetal", [(0, "#f4a1c1"), (.5, "#fcdce9"), (1, "#ffffff")])
    + _rg("gnApfel", [(0, "#ff9078"), (.45, "#e0262b"), (1, "#870d18")], .36, .3, .85)
    + _lg("gnBlatt", [(0, "#7ccd55"), (1, "#2f7d32")], 0, 0, 1, 1)
    + _lg("gnBlattD", [(0, "#5fae45"), (1, "#256b2a")], 0, 0, 1, 1)
    + _rg("gnHerbst", [(0, "#ffd36a"), (.5, "#ee8a1c"), (1, "#b53f12")], .4, .35, .8)
    # Milbe
    + _rg("gnMilbe", [(0, "#c8643a"), (.5, "#8a3418"), (1, "#521a0a")], .38, .32, .8)
    # Holz, Metall, Glas, Schnee
    + _lg("gnHolz", [(0, "#e2bd86"), (.5, "#cf9a58"), (1, "#a8743c")], 0, 0, 1, 0)
    + _lg("gnHolzQ", [(0, "#e2bd86"), (.5, "#cf9a58"), (1, "#a8743c")])
    + _lg("gnTisch", [(0, "#c98e50"), (1, "#8f5a2c")])
    + _lg("gnMetall", [(0, "#8d99a4"), (.2, "#dfe5ea"), (.42, "#ffffff"), (.7, "#b3bdc6"), (1, "#7d8a96")], 0, 0, 1, 0)
    + _lg("gnMetallD", [(0, "#6f7c88"), (.25, "#c8d0d7"), (.5, "#eef2f5"), (.8, "#9ba7b2"), (1, "#68757f")], 0, 0, 1, 0)
    + _lg("gnWeiss", [(0, "#ffffff"), (1, "#d9e2ea")], 0, 0, 1, 0)
    + _lg("gnWeissQ", [(0, "#ffffff"), (1, "#dbe4ec")])
    + _lg("gnSchnee", [(0, "#ffffff"), (1, "#cfe0ee")])
    + _lg("gnDeckel", [(0, "#b5bfc8"), (1, "#7d8892")])
    + _lg("gnHoniggl", [(0, "#ffd24a"), (.6, "#f0a010"), (1, "#c26e00")], 0, 0, 1, 0)
    + _lg("gnWand", [(0, "#fff6dc"), (1, "#f7e2ad")])
    + _lg("gnBoden", [(0, "#d8aa6c"), (1, "#a8763c")])
    + _lg("gnWachsKerze", [(0, "#ffe9a0"), (.45, "#f4c94d"), (1, "#c98c1b")], 0, 0, 1, 0)
    + _lg("gnWachsHell", [(0, "#fffbe8"), (.5, "#f7e6ae"), (1, "#d9bf74")], 0, 0, 1, 0)
    + _lg("gnWachsDunkel", [(0, "#e5a845"), (.5, "#b8721c"), (1, "#7e470c")], 0, 0, 1, 0)
    + _rg("gnFlamme", [(0, "#ffffff"), (.35, "#fff2a0"), (.75, "#ffb02e"), (1, "#ff7a00", .0)], .5, .6, .5)
    + _rg("gnGlut", [(0, "#ffe9a0", .75), (1, "#ffd24a", 0)], .5, .5, .5)
    + _rg("gnKugel", [(0, "#ffffff", .55), (1, "#ffffff", 0)], .5, .5, .5)
    # Bienenkasten-Farben
    + _lg("gnKastenBlau", [(0, "#8fc4ea"), (1, "#4f8fc2")], 0, 0, 1, 0)
    + _lg("gnKastenGelb", [(0, "#ffe27a"), (1, "#e6b630")], 0, 0, 1, 0)
    + _lg("gnKastenGruen", [(0, "#a6d98a"), (1, "#5fae45")], 0, 0, 1, 0)
    + _lg("gnKastenRot", [(0, "#f08a7c"), (1, "#c85446")], 0, 0, 1, 0)
    + "<clipPath id='cnAbd'><path d='" + ABDOMEN + "'/></clipPath>"
)

KASTENFARBEN = {"weiss": "gnWeiss", "blau": "gnKastenBlau", "gelb": "gnKastenGelb", "gruen": "gnKastenGruen",
                "rot": "gnKastenRot", "holz": "gnHolz"}


_DEF_RE = re.compile(r"<(linearGradient|radialGradient|clipPath) id='(\w+)'.*?</(?:linearGradient|radialGradient|clipPath)>", re.S)


def _beschneiden(defs_text, rest_text):
    """Entfernt Verläufe und Clip-Pfade aus defs_text, die im übrigen Text nirgends benutzt werden (spart Dateigröße)."""
    return _DEF_RE.sub(lambda m: m.group(0) if f"#{m.group(2)})" in rest_text else "", defs_text)


def szene(titel, *teile, defs="", **kw):
    """svg() mit den gemeinsamen Defs dieser Datei und den benutzten Bienen-/Blumen-Varianten (unbenutzte Verläufe entfallen)."""
    bienen = "".join(f"<g id='{k}'>{v}</g>" for k, v in _BIENEN.items())
    _BIENEN.clear()
    rest = "".join(str(x) for x in teile) + bienen + defs + kw.get("grund", "")
    return svg(titel, *teile, defs_extra=_beschneiden(DEFS, rest) + bienen + defs, **kw)


def g(inhalt, x=0, y=0, s=1.0, rot=0, spiegeln=False, extra=""):
    """Gruppe mit Verschiebung, Drehung, Skalierung (spiegeln = an der senkrechten Achse)."""
    sx = -s if spiegeln else s
    tr = f"translate({f(x)} {f(y)})"
    if rot:
        tr += f" rotate({f(rot)})"
    if sx != 1 or s != 1:
        tr += f" scale({sx:.3f} {s:.3f})".replace(".000", "")
    return f"<g transform='{tr}'{(' ' + extra) if extra else ''}>{inhalt}</g>"


# ═══════════════════════════════════════════════════════════════════════════
#  Beschriftung (Halo, Zeigelinie, Etikett) – nur über diese Funktionen
# ═══════════════════════════════════════════════════════════════════════════
def beschr(x, y, text, ziel=None, size=12, anchor="middle", fill=TEXT, farbe="#334155", von=None):
    """Beschriftung mit weißem Halo; `ziel=(tx, ty)` zeichnet eine Zeigelinie mit Punkt zum Bildteil."""
    out = ""
    if ziel:
        tx, ty = ziel
        if von is None:
            von = (x, y + 5) if ty > y else (x, y - size - 1)
        out += (f"<line x1='{f(von[0])}' y1='{f(von[1])}' x2='{f(tx)}' y2='{f(ty)}' stroke='#fff' stroke-width='4.4' stroke-linecap='round'/>"
                f"<line x1='{f(von[0])}' y1='{f(von[1])}' x2='{f(tx)}' y2='{f(ty)}' stroke='{farbe}' stroke-width='1.7' stroke-linecap='round'/>"
                f"<circle cx='{f(tx)}' cy='{f(ty)}' r='3.2' fill='#fff' stroke='{farbe}' stroke-width='1.7'/>")
    return out + t(x, y, text, size, 800, fill, anchor)


def etikett(x, y, text, farbe=BLAU, size=12, breite=None, hoehe=22):
    """Farbiges Schildchen mit weißer Schrift (x = Mitte, y = Oberkante)."""
    b = breite or (len(text) * size * .62 + 18)
    return (f"<rect x='{f(x - b / 2)}' y='{f(y)}' width='{f(b)}' height='{hoehe}' rx='{hoehe / 2:.0f}' fill='{farbe}' "
            f"stroke='#fff' stroke-width='2' filter='url(#fSchatten)'/>"
            f"<text x='{f(x)}' y='{f(y + hoehe / 2 + size / 3)}' font-size='{size}' font-weight='800' fill='#fff' text-anchor='middle'>{text}</text>")


def nummer(x, y, n, r=10, farbe=MAGENTA):
    """Kreis mit Ziffer (Reihenfolge-Marke)."""
    return (f"<circle cx='{f(x)}' cy='{f(y)}' r='{r}' fill='{farbe}' stroke='#fff' stroke-width='2' filter='url(#fSchatten)'/>"
            f"<text x='{f(x)}' y='{f(y + r * .38)}' font-size='{r * 1.25:.0f}' font-weight='800' fill='#fff' text-anchor='middle'>{n}</text>")


# ═══════════════════════════════════════════════════════════════════════════
#  Fell, Haare, Pollen
# ═══════════════════════════════════════════════════════════════════════════
def _haare(cx, cy, rx, ry, n, laenge, farbe, seed, w=.9, von=0, bis=360, op=.9):
    rnd = random.Random(seed)
    d = []
    for i in range(n):
        a = math.radians(von + (bis - von) * (i + rnd.random() * .6) / n)
        x1, y1 = cx + rx * math.cos(a), cy + ry * math.sin(a)
        ll = laenge * (.7 + rnd.random() * .6)
        d.append(f"M{f(x1)},{f(y1)}L{f(x1 + math.cos(a) * ll)},{f(y1 + math.sin(a) * ll)}")
    return f"<path d='{''.join(d)}' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round' fill='none' opacity='{op}'/>"


def pollenpunkte(punkte, r=1.3):
    """Gelbe Pollenkörner an gegebenen Stellen (Liste von (x, y))."""
    return "".join(f"<circle cx='{f(x)}' cy='{f(y)}' r='{r}' fill='url(#gnPollen)' stroke='#d58a00' stroke-width='.35'/>" for x, y in punkte)


def streu(cx, cy, rx, ry, n, seed):
    """n Zufallspunkte in einer Ellipse (für Pollen, Bienenhaufen)."""
    rnd = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if x * x + y * y <= 1:
            out.append((cx + x * rx, cy + y * ry))
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  Biene von der Seite (Kopf nach rechts), ca. 92 Einheiten lang
# ═══════════════════════════════════════════════════════════════════════════
_BEIN_N = ["M9,8 L14,13 L16,20 L13,24", "M2,10 L5,16 L4,23 L1,26.5", "M-5,9 L-8,15 L-14,21 L-18.5,24"]
_BEIN_F = ["M12,6 L18,10 L22,16 L20,20.5", "M5,8 L10,13 L10,21 L7,24.5", "M-2,8 L-3,14 L-8,21 L-12,25"]
_FLU_VORN = "M0,0 C-6,-18 -24,-30 -40,-28 C-42,-14 -24,-4 0,0 Z"
_FLU_HINT = "M0,0 C-2,-12 -12,-22 -24,-23 C-26,-14 -14,-4 0,0 Z"


def _fluegel(x, y, rot, pfad, op=1.0, adern=True):
    ad = ("<path d='M0,0 Q-14,-11 -35,-26 M0,0 Q-16,-6 -37,-14' stroke='#8fb4d0' stroke-width='.6' fill='none' opacity='.8'/>"
          if adern and pfad == _FLU_VORN else
          "<path d='M0,0 Q-9,-9 -22,-21' stroke='#8fb4d0' stroke-width='.6' fill='none' opacity='.8'/>" if adern else "")
    return (f"<g transform='translate({x} {y}) rotate({rot}) scale(.88)' opacity='{op}'><path d='{pfad}' fill='url(#gnFlue)' stroke='#8fb4d0' "
            f"stroke-width='.8' stroke-linejoin='round'/>{ad}</g>")


def biene_koerper(pollen_beine=False, pollen_haare=False, wachs=False, beine=True, fluegel=True, schlaf=False):
    """Biene in eigenen Koordinaten (Kopf rechts, Schwerpunkt ≈ Brust bei 0,0). Rückgabe: SVG-Fragment."""
    o = []
    # ferne Beine und Flügel
    if beine:
        o.append("<g stroke='#5a4630' stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round' fill='none' opacity='.75'>"
                 + "".join(f"<path d='{p}'/>" for p in _BEIN_F) + "</g>")
        if pollen_beine:
            o.append("<ellipse cx='-5.6' cy='17.8' rx='4.4' ry='3.2' transform='rotate(120 -5.6 17.8)' fill='url(#gnPollen)' opacity='.85'/>")
    if fluegel:
        o.append(_fluegel(1, -10, -22, _FLU_VORN, .55) + _fluegel(4, -10, 8, _FLU_HINT, .55))
    # Hinterleib
    abd = (f"<path d='{ABDOMEN}' fill='url(#gnBGelb)'/><g clip-path='url(#cnAbd)'>"
           + "".join(f"<path d='M{x + 2.4},-16 Q{x + 5.4},0 {x + 2.4},16 L{x - 2.4},16 Q{x - .6},0 {x - 2.4},-16 Z' fill='url(#gnBDunkel)'/>"
                     for x in (-19, -30.5, -42))
           + "<path d='M-48.5,-16 Q-45.5,0 -48.5,16 L-60,16 L-60,-16 Z' fill='url(#gnBDunkel)'/>"
           + "<path d='M-8,-16 L-12,-16 Q-9,0 -12,16 L-8,16 Z' fill='#9a5f14' opacity='.55'/>"
           + "<ellipse cx='-26' cy='-6.5' rx='17' ry='2.6' fill='#fff' opacity='.28'/>"
           + "<ellipse cx='-26' cy='13' rx='27' ry='5.5' fill='#000' opacity='.2'/></g>"
           + f"<path d='{ABDOMEN}' fill='none' stroke='#4a3010' stroke-width='.9' stroke-linejoin='round'/>"
           + "<path d='M-50.5,2.2 L-55,4 L-50.6,4.4 Z' fill='#2a1a0c'/>")
    o.append(abd)
    if wachs:
        for (px, py, r) in ((-21, 13.8, 0), (-31, 14.2, 8), (-40.5, 12.4, 22)):
            o.append(f"<g transform='translate({px} {py}) rotate({r}) scale(1.25)'><path d='M-3.6,-1.6 L3.4,-2 L4.6,2.6 L0.4,6 L-4.2,3 Z' "
                     "fill='url(#gnWachsP)' stroke='#d9c27a' stroke-width='.7' stroke-linejoin='round'/>"
                     "<path d='M-2.2,0 L2.4,-.6' stroke='#fff' stroke-width='.8' stroke-linecap='round'/></g>")
    # nahe Flügel, Brust, Kopf
    if fluegel:
        o.append(_fluegel(-1, -9, -10, _FLU_VORN) + _fluegel(3, -9, 14, _FLU_HINT))
    o.append("<ellipse cx='2' cy='-1' rx='13' ry='12' fill='url(#gnThorax)'/>")
    o.append(_haare(2, -1, 12.6, 11.6, 44, 2.3, "#f3d48c", 3, .7, 0, 360, .7))
    o.append("<ellipse cx='-1' cy='-6' rx='7' ry='3.4' fill='#fff' opacity='.2'/>")
    o.append("<ellipse cx='18' cy='1' rx='8.3' ry='9' fill='url(#gnKopf)'/>")
    o.append(_haare(14, -5, 4, 3, 8, 2.4, "#6a4a2a", 5, .8, 180, 360, .8))
    o.append("<ellipse cx='20.4' cy='-1.6' rx='4.7' ry='6.8' fill='url(#gnAuge)' stroke='#120a06' stroke-width='.6'/>"
             "<ellipse cx='22' cy='-4.6' rx='1.3' ry='1.8' fill='#fff' opacity='.7'/>")
    # Rüssel und Fühler
    o.append("<path d='M24.5,5 Q29.5,6.5 31,11' stroke='#3a2a1a' stroke-width='2.2' stroke-linecap='round' fill='none'/>"
             "<path d='M21,-8 Q22,-17 28,-20 Q32,-21 35,-18' stroke='#5a4630' stroke-width='1.2' fill='none' stroke-linecap='round' opacity='.75'/>"
             "<path d='M23,-6.5 Q27,-14 33,-14.5 Q37,-14 38.5,-9.5' stroke='#2a1a0c' stroke-width='1.5' fill='none' stroke-linecap='round'/>"
             "<circle cx='38.6' cy='-9' r='1.5' fill='#2a1a0c'/>")
    # nahe Beine
    if beine:
        o.append("<g stroke='#2a1a0c' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round' fill='none'>"
                 + "".join(f"<path d='{p}'/>" for p in _BEIN_N) + "</g>")
        if pollen_beine:
            o.append("<ellipse cx='-13.2' cy='21' rx='5.8' ry='4.2' transform='rotate(135 -13.2 21)' fill='url(#gnPollen)' stroke='#d58a00' stroke-width='.5'/>"
                     "<ellipse cx='-14.4' cy='19.6' rx='2' ry='1.2' transform='rotate(135 -14.4 19.6)' fill='#fff8c4' opacity='.8'/>")
    if pollen_haare:
        pts = streu(2, -2, 10.5, 9.5, 12, 11) + streu(-24, -3, 17, 6.5, 8, 12) + streu(16, -5, 5, 4, 3, 13)
        o.append(pollenpunkte(pts, 1.25))
    return "".join(o)


_BIENEN = {}        # Variante -> SVG-Fragment; szene() schreibt jede benutzte Variante einmal in die defs


def biene(x, y, s=1.0, rot=0, spiegeln=False, schatten=False, direkt=False, **kw):
    """Biene an Position (x, y) = Brust, Maßstab s, Drehung rot (Grad), spiegeln = Kopf nach links.
    Ohne `direkt` wird die Variante nur einmal definiert und per <use> gesetzt (spart Dateigröße)."""
    extra = "filter='url(#fSchatten)'" if schatten else ""
    if direkt:
        return g(biene_koerper(**kw), x, y, s, rot, spiegeln, extra)
    flags = {k: bool(kw.get(k, d)) for k, d in (("pollen_beine", False), ("pollen_haare", False), ("wachs", False), ("beine", True), ("fluegel", True))}
    key = "gnB" + "".join(str(int(v)) for v in flags.values())
    if key not in _BIENEN:
        _BIENEN[key] = biene_koerper(**flags)
    return g(f"<use href='#{key}'/>", x, y, s, rot, spiegeln, extra)


# ═══════════════════════════════════════════════════════════════════════════
#  Varroa-Milbe (Draufsicht, flach-oval, rotbraun, vier Beinpaare) – Kopfseite oben
# ═══════════════════════════════════════════════════════════════════════════
def varroa_koerper(rx=15.0, ry=11.0, schatten=True):
    """Milbe in eigenen Koordinaten (Mitte 0,0, Breite 2·rx). Beine sind kurz und liegen unter dem Panzer."""
    o = []
    # vier Beinpaare (rechts und links), vom Rand nach außen
    for sg in (-1, 1):
        for i, (yy, wx, wy) in enumerate(((-.58, 1.1, -.5), (-.2, 1.16, -.1), (.2, 1.15, .3), (.56, 1.08, .6))):
            x0 = sg * rx * .85 * math.sqrt(max(0, 1 - (yy * 1.05) ** 2))
            y0 = yy * ry
            x1, y1 = sg * rx * wx, y0 + wy * ry * .3
            x2, y2 = sg * rx * (wx + .12), y1 + ry * (.2 if i < 2 else .3)
            o.append(f"<path d='M{f(x0)},{f(y0)} L{f(x1)},{f(y1)} L{f(x2)},{f(y2)}' stroke='#7a3a1c' stroke-width='{ry * .24:.1f}' "
                     f"stroke-linecap='round' stroke-linejoin='round' fill='none'/>")
    # Mundwerkzeuge vorn
    o.append(f"<ellipse cx='0' cy='{f(-ry * .98)}' rx='{f(rx * .22)}' ry='{f(ry * .22)}' fill='#b0623a' stroke='#5a2410' stroke-width='.7'/>")
    # Panzer
    o.append(f"<ellipse cx='0' cy='0' rx='{f(rx)}' ry='{f(ry)}' fill='url(#gnMilbe)' stroke='#3e1508' stroke-width='{max(.8, ry * .09):.1f}'"
             + (" filter='url(#fSchatten)'" if schatten else "") + "/>")
    # Rand-Haare, Nähte, Glanz
    o.append(_haare(0, 0, rx * .97, ry * .97, 18, ry * .14, "#4a1a0a", 21, max(.6, ry * .06), 0, 360, .75))
    o.append(f"<path d='M{f(-rx * .55)},{f(ry * .1)} Q0,{f(ry * .45)} {f(rx * .55)},{f(ry * .1)} M{f(-rx * .35)},{f(-ry * .35)} Q0,{f(-ry * .12)} {f(rx * .35)},{f(-ry * .35)}' "
             f"stroke='#5a2410' stroke-width='{max(.6, ry * .05):.1f}' fill='none' opacity='.55' stroke-linecap='round'/>")
    o.append(f"<ellipse cx='{f(-rx * .3)}' cy='{f(-ry * .42)}' rx='{f(rx * .42)}' ry='{f(ry * .2)}' transform='rotate(-14 {f(-rx * .3)} {f(-ry * .42)})' fill='#fff' opacity='.3'/>")
    return "".join(o)


def varroa(x, y, s=1.0, rot=0, **kw):
    return g(varroa_koerper(**kw), x, y, s, rot)


# ═══════════════════════════════════════════════════════════════════════════
#  Wabenmuster (Sechsecke mit Spitze oben, wie im Rähmchen)
# ═══════════════════════════════════════════════════════════════════════════
def _hexpts(cx, cy, r):
    return " ".join(f"{cx + r * math.cos(math.radians(-90 + 60 * i)):.1f},{cy + r * math.sin(math.radians(-90 + 60 * i)):.1f}" for i in range(6))


def wabenmuster(pid, art, r=7, drehung=0):
    """<pattern> mit Wabenzellen (Zelle einmal als <g> definiert, fünfmal per <use> gesetzt).
    art: 'leer' (Wachs mit Zellboden), 'deckel' (verdeckelter Honig), 'honig' (offener Honig). Kommt in die defs der Szene."""
    w, h = math.sqrt(3) * r, 3 * r
    zellen = [(0, 0), (w, 0), (w / 2, 1.5 * r), (0, h), (w, h)]
    cx = cy = 0
    if art == "leer":
        z = (f"<polygon points='{_hexpts(0, 0, r)}' fill='#fbeaa8' stroke='#bf8a1f' stroke-width='1.1' stroke-linejoin='round'/>"
             f"<polygon points='{_hexpts(0, 0, r * .66)}' fill='#d9a93f' stroke='#a8761c' stroke-width='.6' stroke-linejoin='round'/>"
             f"<path d='M{f(-r * .45)},{f(-r * .1)} L0,{f(-r * .5)}' stroke='#fff7d0' stroke-width='.9' stroke-linecap='round' opacity='.9'/>")
    elif art == "deckel":
        z = (f"<polygon points='{_hexpts(0, 0, r)}' fill='#ecc96c' stroke='#c08a2a' stroke-width='.9' stroke-linejoin='round'/>"
             f"<polygon points='{_hexpts(0, 0, r * .78)}' fill='#f5dc92'/>"
             f"<path d='M{f(-r * .45)},{f(-r * .1)} Q0,{f(-r * .55)} {f(r * .4)},{f(-r * .2)}' stroke='#fff8dc' stroke-width='.9' fill='none' stroke-linecap='round' opacity='.85'/>")
    else:
        z = (f"<polygon points='{_hexpts(0, 0, r)}' fill='url(#gnHoniggl)' stroke='#b27208' stroke-width='.9' stroke-linejoin='round'/>"
             f"<path d='M{f(-r * .5)},{f(-r * .15)} Q{f(-r * .2)},{f(-r * .6)} {f(r * .3)},{f(-r * .45)}' stroke='#fff3b0' stroke-width='1' fill='none' stroke-linecap='round' opacity='.9'/>")
    uses = "".join(f"<use href='#{pid}z' x='{f(x)}' y='{f(y)}'/>" for x, y in zellen)
    tr = f" patternTransform='rotate({drehung})'" if drehung else ""
    return f"<g id='{pid}z'>{z}</g><pattern id='{pid}' width='{w:.2f}' height='{h:.2f}' patternUnits='userSpaceOnUse'{tr}>{uses}</pattern>"


def raehmchen(x, y, w, h, deckel_anteil=.62, r=7, bienen=0, seed=1, mit_pattern=("pnDeckel", "pnHonig")):
    """Rähmchen (Holzrahmen mit Oberträger und Ohren) mit Wabe: oben verdeckelter, unten offener Honig.
    (x, y) = linke obere Ecke des Oberträgers, w = Breite des Oberträgers ohne Ohren."""
    tb = 8      # Oberträger
    sb = max(4, w * .045)
    ohr = 9
    zx, zy, zw, zh = x + sb, y + tb, w - 2 * sb, h - tb - sb
    hd = zh * deckel_anteil
    o = [f"<g filter='url(#fSchatten)'>"
         f"<rect x='{f(x - ohr)}' y='{f(y)}' width='{f(w + 2 * ohr)}' height='{tb}' rx='2' fill='url(#gnHolzQ)' stroke='#7a4b22' stroke-width='1'/>"
         f"<rect x='{f(x)}' y='{f(y)}' width='{f(w)}' height='{f(h)}' rx='2' fill='url(#gnHolz)' stroke='#7a4b22' stroke-width='1.2'/></g>"
         f"<rect x='{f(x - ohr)}' y='{f(y)}' width='{f(w + 2 * ohr)}' height='{tb}' rx='2' fill='url(#gnHolzQ)' stroke='#7a4b22' stroke-width='1'/>",
         f"<rect x='{f(zx)}' y='{f(zy)}' width='{f(zw)}' height='{f(zh)}' fill='#d9a63a'/>",
         f"<rect x='{f(zx)}' y='{f(zy)}' width='{f(zw)}' height='{f(hd)}' fill='url(#{mit_pattern[0]})'/>",
         f"<rect x='{f(zx)}' y='{f(zy + hd)}' width='{f(zw)}' height='{f(zh - hd)}' fill='url(#{mit_pattern[1]})'/>",
         # Übergang: offene Honigzellen laufen zackig in die Deckel
         f"<path d='M{f(zx)},{f(zy + hd - 2)} q{f(zw * .12)},{f(5)} {f(zw * .25)},{f(1)} t{f(zw * .25)},{f(-1)} t{f(zw * .25)},{f(2)} t{f(zw * .25)},{f(-1)}' stroke='#f2b628' stroke-width='3' fill='none' opacity='.8'/>",
         f"<rect x='{f(zx)}' y='{f(zy)}' width='{f(zw)}' height='{f(zh)}' fill='none' stroke='#7a4b22' stroke-width='1'/>",
         # Glanz auf dem Honig
         f"<ellipse cx='{f(zx + zw * .3)}' cy='{f(zy + hd + (zh - hd) * .35)}' rx='{f(zw * .18)}' ry='{f(2.4)}' fill='#fff' opacity='.35'/>"]
    rnd = random.Random(seed)
    for _ in range(bienen):
        bx, by = zx + rnd.uniform(.15, .85) * zw, zy + rnd.uniform(.2, .75) * zh
        o.append(biene(bx, by, .3, rnd.choice((-20, 12, 6, -8)), rnd.random() < .5, beine=True, fluegel=False, schatten=True))
    return "".join(o)


# ═══════════════════════════════════════════════════════════════════════════
#  Imker (Brustbild von vorn, Hut mit Schleier)
# ═══════════════════════════════════════════════════════════════════════════
def imker(x, y, s=1.0, haende=((-54, -28), (54, -28))):
    """Imker, (x, y) = Mitte des unteren Randes. Rückgabe (körper, arme): zuerst körper, dann das Gehaltene, dann arme."""
    kp = (
        # Rumpf
        "<path d='M-35,0 L-32,-50 Q-31,-64 -16,-66 L16,-66 Q31,-64 32,-50 L35,0 Z' fill='url(#gnWeiss)' stroke='#9fb0bf' stroke-width='1.4'/>"
        "<path d='M0,-62 L0,0' stroke='#b6c4d0' stroke-width='1.4'/>"
        "<path d='M-14,-30 q6,6 12,0' stroke='#c4d0da' stroke-width='1.2' fill='none'/>"
        "<ellipse cx='0' cy='-65' rx='15' ry='4.5' fill='#eaf0f5' stroke='#9fb0bf' stroke-width='1.2'/>"
        # Gesicht hinter dem Schleier
        "<ellipse cx='0' cy='-86' rx='14' ry='16' fill='#f2c7a0' stroke='#c99a73' stroke-width='1'/>"
        "<ellipse cx='-5.4' cy='-88' rx='1.6' ry='2' fill='#3a2a22'/><ellipse cx='5.4' cy='-88' rx='1.6' ry='2' fill='#3a2a22'/>"
        "<path d='M-5,-80 Q0,-75.5 5,-80' stroke='#a8554a' stroke-width='1.8' fill='none' stroke-linecap='round'/>"
        "<circle cx='-9' cy='-82' r='2.6' fill='#f09a8a' opacity='.5'/><circle cx='9' cy='-82' r='2.6' fill='#f09a8a' opacity='.5'/>"
        # Schleier (durchscheinend, mit Netzlinien)
        "<path d='M-26,-100 L-33,-58 Q0,-50 33,-58 L26,-100 Z' fill='#dfe7ee' opacity='.42' stroke='#aab9c6' stroke-width='1'/>"
        "<path d='M-22,-96 L-27,-58 M-11,-98 L-13,-54 M0,-99 L0,-52 M11,-98 L13,-54 M22,-96 L27,-58' stroke='#fff' stroke-width='.8' opacity='.7'/>"
        "<path d='M-29,-84 Q0,-78 29,-84 M-31,-72 Q0,-65 31,-72' stroke='#fff' stroke-width='.8' fill='none' opacity='.7'/>"
        # Hut
        "<ellipse cx='0' cy='-100' rx='34' ry='8.5' fill='#f3e3b8' stroke='#b79b5e' stroke-width='1.4'/>"
        "<path d='M-18,-101 Q-19,-124 0,-124 Q19,-124 18,-101 Q0,-95 -18,-101 Z' fill='#f7ecc9' stroke='#b79b5e' stroke-width='1.4'/>"
        "<path d='M-18.5,-106 Q0,-100.5 18.5,-106' stroke='#c0392b' stroke-width='3.4' fill='none'/>")
    arme = ""
    if haende:
        for (hx, hy), sg in zip(haende, (-1, 1)):
            sx, sy = sg * 30, -58
            ex, ey = (sx + hx) / 2 + sg * 9, (sy + hy) / 2 + 12
            d = f"M{sx},{sy} Q{f(ex)},{f(ey)} {hx},{hy}"
            arme += (f"<path d='{d}' stroke='#9fb0bf' stroke-width='16' stroke-linecap='round' stroke-linejoin='round' fill='none'/>"
                     f"<path d='{d}' stroke='#f2f6f9' stroke-width='13' stroke-linecap='round' stroke-linejoin='round' fill='none'/>"
                     f"<circle cx='{hx}' cy='{hy}' r='7.5' fill='#c9a06a' stroke='#8a6a3c' stroke-width='1.2'/>")
    return g(kp, x, y, s), g(arme, x, y, s)


# ═══════════════════════════════════════════════════════════════════════════
#  Bienenkasten
# ═══════════════════════════════════════════════════════════════════════════
def kasten(x, y, s=1.0, zargen=2, farbe="weiss", deckel=True, schnee=False, anflug=True, bienen=0, seed=2):
    """Bienenkasten (Magazin) von vorn; (x, y) = Mitte der Standfläche. Breite 70, Zarge 22 hoch."""
    fill = f"url(#{KASTENFARBEN.get(farbe, farbe)})"
    o = ["<g filter='url(#fSchatten)'>",
         f"<rect x='-35' y='-8' width='70' height='8' rx='1.5' fill='url(#gnHolz)' stroke='#7a4b22' stroke-width='1'/>"]
    for i in range(zargen):
        yy = -8 - 22 * (i + 1)
        o.append(f"<rect x='-33' y='{yy}' width='66' height='22' fill='{fill}' stroke='#6b7a88' stroke-width='1.1'/>"
                 f"<rect x='-9' y='{yy + 6}' width='18' height='4' rx='2' fill='#2a3440' opacity='.55'/>"
                 f"<path d='M-33,{yy + 1.5} H33' stroke='#fff' stroke-width='1.2' opacity='.7'/>")
    top = -8 - 22 * zargen
    if deckel:
        o.append(f"<path d='M-38,{top} L-35,{top - 9} H35 L38,{top} Z' fill='url(#gnDeckel)' stroke='#5c6670' stroke-width='1.1'/>"
                 f"<path d='M-33,{top - 6} H33' stroke='#fff' stroke-width='1.2' opacity='.55'/>")
        if schnee:
            o.append(f"<path d='M-40,{top + 1} Q-38,{top - 14} -26,{top - 12} Q-14,{top - 17} 0,{top - 13} Q16,{top - 17} 27,{top - 12} Q38,{top - 14} 40,{top + 1} Q30,{top + 4} 20,{top + 1} Q10,{top + 5} 0,{top + 1} Q-10,{top + 5} -20,{top + 1} Q-30,{top + 4} -40,{top + 1} Z' fill='url(#gnSchnee)' stroke='#aac4d8' stroke-width='1'/>")
    o.append("</g>")
    if anflug:
        o.append("<rect x='-12' y='-13' width='24' height='5' rx='2' fill='#2a1a0c'/>"
                 "<path d='M-15,-7 H15 L19,0 H-19 Z' fill='url(#gnHolzQ)' stroke='#7a4b22' stroke-width='1'/>")
    rnd = random.Random(seed)
    for k in range(bienen):
        bx = rnd.uniform(-14, 14)
        o.append(biene(bx, -3 + rnd.uniform(-1, 1), .17, 0, rnd.random() < .5))
    return g("".join(o), x, y, s)


# ═══════════════════════════════════════════════════════════════════════════
#  Honig: Glas, Schleuder, Kerzen, Dose
# ═══════════════════════════════════════════════════════════════════════════
def honigglas(x, y, s=1.0, fuell=.78, text="Honig", deckel=True):
    """Honigglas, (x, y) = Mitte der Standfläche; 30 breit, 40 hoch (ohne Deckel)."""
    top = -40
    fy = -3 - 34 * fuell
    o = [  # Glaskörper
        "<g filter='url(#fSchatten)'><rect x='-15' y='-40' width='30' height='40' rx='7' fill='#eaf5fb' stroke='#8fb0c4' stroke-width='1.4' opacity='.95'/></g>",
        f"<path d='M-13,{fy} H13 V-9 Q13,-2.5 6,-2.5 H-6 Q-13,-2.5 -13,-9 Z' fill='url(#gnHoniggl)'/>",
        f"<ellipse cx='0' cy='{fy}' rx='13' ry='2.2' fill='#ffe58a'/>",
        "<rect x='-15' y='-40' width='30' height='40' rx='7' fill='none' stroke='#8fb0c4' stroke-width='1.4'/>",
        f"<path d='M-10.5,{fy + 4} V-9' stroke='#fff' stroke-width='2.6' stroke-linecap='round' opacity='.6'/>",
        "<rect x='-12.5' y='-32' width='25' height='15' rx='2' fill='#fffaf0' stroke='#c9972b' stroke-width='1'/>"]
    if text:
        o.append(f"<text x='0' y='-21.8' font-size='6.4' font-weight='800' fill='#7a4b0c' text-anchor='middle'>{text}</text>"
                 "<path d='M-8,-27 H8' stroke='#e0a800' stroke-width='1.2'/>")
    if deckel:
        o.append("<rect x='-14.5' y='-46' width='29' height='7' rx='2' fill='#d4a017' stroke='#8a6508' stroke-width='1'/>"
                 "<path d='M-12,-43 H12' stroke='#ffe58a' stroke-width='1.2' opacity='.8'/>")
    return g("".join(o), x, y, s)


def honigschleuder(x, y, s=1.0, fuss=88):
    """Honigschleuder (Edelstahltrommel mit Deckel, Kurbel, Hahn, Gestell). (x, y) = Mitte der Standfläche am Boden.
    Rumpf 100 breit, 84 hoch, `fuss` = Höhe des Gestells. Kurbelgriff bei (23, −fuss−108), Hahnmündung bei (−62, −fuss+10)."""
    bb = -fuss            # Unterkante Rumpf
    bt = bb - 84          # Oberkante Rumpf
    o = [  # Gestell
        f"<path d='M-40,{bb} L-52,0 M40,{bb} L52,0' stroke='#5c6670' stroke-width='5' stroke-linecap='round'/>"
        f"<path d='M-46,{bb * .45:.0f} H46' stroke='#5c6670' stroke-width='4' stroke-linecap='round'/>"
        f"<path d='M-40,{bb} L-52,0 M40,{bb} L52,0' stroke='#b9c3cc' stroke-width='1.6' stroke-linecap='round' transform='translate(-1 0)'/>"
        "<g filter='url(#fSchatten)'>"
        f"<rect x='-50' y='{bt}' width='100' height='84' rx='6' fill='url(#gnMetall)' stroke='#6f7c88' stroke-width='1.6'/>"
        f"<rect x='-50' y='{bt + 26}' width='100' height='4' fill='#8d99a4' opacity='.55'/><rect x='-50' y='{bt + 56}' width='100' height='4' fill='#8d99a4' opacity='.55'/>"
        f"<path d='M-50,{bt} H50 V{bt + 7} H-50 Z' fill='#9ba7b2' stroke='#6f7c88' stroke-width='1'/>"
        f"<ellipse cx='0' cy='{bt}' rx='50' ry='11' fill='url(#gnMetallD)' stroke='#6f7c88' stroke-width='1.6'/>"
        f"<ellipse cx='0' cy='{bt}' rx='42' ry='8' fill='none' stroke='#8d99a4' stroke-width='1'/></g>"
        f"<path d='M-30,{bt + 12} V{bb - 10}' stroke='#fff' stroke-width='4' stroke-linecap='round' opacity='.5'/>"
        # Kurbel
        f"<rect x='-3' y='{bt - 24}' width='6' height='26' rx='2' fill='#6f7c88'/>"
        f"<path d='M0,{bt - 24} H22' stroke='#4a5560' stroke-width='5' stroke-linecap='round'/>"
        f"<circle cx='23' cy='{bt - 24}' r='4.5' fill='#c0392b' stroke='#7e1d12' stroke-width='1'/>"
        f"<circle cx='0' cy='{bt - 24}' r='4' fill='#8d99a4' stroke='#4a5560' stroke-width='1.2'/>"
        # Hahn
        f"<path d='M-50,{bb} H-62 V{bb + 10}' stroke='#5c6670' stroke-width='7' stroke-linecap='round' stroke-linejoin='round' fill='none'/>"
        f"<path d='M-50,{bb} H-62 V{bb + 10}' stroke='#c5ced6' stroke-width='3' stroke-linecap='round' stroke-linejoin='round' fill='none'/>"
        f"<rect x='-67' y='{bb - 15}' width='10' height='6' rx='2' fill='#c0392b'/>"
        f"<path d='M-62,{bb - 15} V{bb - 4}' stroke='#5c6670' stroke-width='3'/>"]
    return g("".join(o), x, y, s)


def honigstrahl(x, y1, y2, w=4.4):
    """Goldener Honigfaden von (x, y1) nach unten bis y2; unten dünner, mit Glanz und kleinem Spiegelfleck."""
    return (f"<path d='M{f(x - w / 2)},{f(y1)} L{f(x + w / 2)},{f(y1)} Q{f(x + w * .3)},{f((y1 + y2) / 2)} {f(x + w * .22)},{f(y2)} L{f(x - w * .22)},{f(y2)} "
            f"Q{f(x - w * .3)},{f((y1 + y2) / 2)} {f(x - w / 2)},{f(y1)} Z' fill='url(#gnHoniggl)' stroke='#b27208' stroke-width='.6'/>"
            f"<path d='M{f(x - w * .15)},{f(y1 + 2)} L{f(x - w * .1)},{f(y2 - 2)}' stroke='#fff3b0' stroke-width='1' stroke-linecap='round' opacity='.85'/>"
            f"<ellipse cx='{f(x)}' cy='{f(y2)}' rx='{f(w * 1.5)}' ry='1.4' fill='#ffe58a' opacity='.9'/>")


def kerze(x, y, h, w=16, art="gelb", flamme=False, spirale=False):
    """Bienenwachskerze, (x, y) = Mitte der Standfläche."""
    grad = {"gelb": "gnWachsKerze", "hell": "gnWachsHell", "dunkel": "gnWachsDunkel"}[art]
    cap = {"gelb": "#ffeeb0", "hell": "#fffdf2", "dunkel": "#f0b860"}[art]
    o = [f"<g filter='url(#fSchatten)'><path d='M{-w / 2},0 V{-h + 3} Q{-w / 2},{-h} {-w / 2 + 3},{-h} H{w / 2 - 3} Q{w / 2},{-h} {w / 2},{-h + 3} V0 Z' fill='url(#{grad})' stroke='#9a6a10' stroke-width='1.1'/></g>"]
    if spirale:
        o.append(f"<rect x='{-w / 2}' y='{-h}' width='{w}' height='{h}' rx='3' fill='url(#pnSpirale)'/>")
    o.append(f"<ellipse cx='0' cy='{-h + 1}' rx='{w / 2 - 1}' ry='2.4' fill='{cap}' stroke='#c99a2a' stroke-width='.8'/>"
             f"<path d='M{-w / 2 + 3},{-h + 6} V-6' stroke='#fff' stroke-width='2' stroke-linecap='round' opacity='.45'/>"
             f"<path d='M0,{-h} V{-h - 6}' stroke='#3a2a1a' stroke-width='1.6' stroke-linecap='round'/>")
    if flamme:
        yy = -h - 7
        o.append(f"<circle cx='0' cy='{yy - 6}' r='17' fill='url(#gnGlut)'/>"
                 f"<path d='M0,{yy + 3} C-6,{yy - 1} -5,{yy - 9} 0,{yy - 17} C5,{yy - 9} 6,{yy - 1} 0,{yy + 3} Z' fill='url(#gnFlamme)' stroke='#ff9a1a' stroke-width='.7'/>")
    return g("".join(o), x, y)


def dose(x, y, s=1.0, text="Salbe"):
    """Runde Blechdose mit Etikett (z. B. Salbe), (x, y) = Mitte der Standfläche; 44 breit, 20 hoch."""
    return g("<g filter='url(#fSchatten)'><path d='M-22,0 V-17 H22 V0 Q0,5 -22,0 Z' fill='url(#gnMetall)' stroke='#6f7c88' stroke-width='1.2'/>"
             "<ellipse cx='0' cy='-17' rx='22' ry='6' fill='#e8ecef' stroke='#6f7c88' stroke-width='1.2'/></g>"
             "<ellipse cx='0' cy='-17' rx='18' ry='4.6' fill='#fff1b8' stroke='#c9972b' stroke-width='1'/>"
             "<rect x='-14' y='-12' width='28' height='9' rx='1.5' fill='#fffaf0' stroke='#c9972b' stroke-width='.8'/>"
             f"<text x='0' y='-5' font-size='7' font-weight='800' fill='#7a4b0c' text-anchor='middle'>{text}</text>", x, y, s)


# ═══════════════════════════════════════════════════════════════════════════
#  Blüte, Apfel, Blätter, Wiesenblumen
# ═══════════════════════════════════════════════════════════════════════════
def apfelbluete(x, y, r=30, rot=0, pollen=True, staubfaeden=14, schatten=True):
    """Apfelblüte von vorn: fünf rosa-weiße Blütenblätter, gelbe Staubblätter mit Pollen, grüner Stempel in der Mitte."""
    o = []
    for i in range(5):
        a = rot + i * 72
        o.append(f"<g transform='rotate({a})'><path d='M0,0 C{-r * .52},{-r * .14} {-r * .66},{-r * .92} 0,{-r * 1.02} "
                 f"C{r * .66},{-r * .92} {r * .52},{-r * .14} 0,0 Z' fill='url(#gnPetal)' stroke='#e6a3bd' stroke-width='.9' stroke-linejoin='round'/>"
                 f"<path d='M0,{-r * .22} V{-r * .78}' stroke='#f2b9cf' stroke-width='.8' opacity='.8'/></g>")
    kern = f"<circle cx='0' cy='0' r='{r * .22:.1f}' fill='#f0e27a' opacity='.9'/>"
    fae = []
    for i in range(staubfaeden):
        a = math.radians(rot + 8 + i * 360 / staubfaeden + (7 if i % 2 else 0))
        rr = r * (.36 if i % 2 else .3)
        fae.append((math.cos(a) * rr, math.sin(a) * rr))
    stab = "".join(f"<line x1='0' y1='0' x2='{f(px)}' y2='{f(py)}' stroke='#e8c75a' stroke-width='.9'/>" for px, py in fae)
    anth = "".join(f"<ellipse cx='{f(px)}' cy='{f(py)}' rx='{r * .075:.1f}' ry='{r * .055:.1f}' transform='rotate({math.degrees(math.atan2(py, px)):.0f} {f(px)} {f(py)})' "
                   f"fill='{'url(#gnPollen)' if pollen else '#e8c75a'}' stroke='#d58a00' stroke-width='.4'/>" for px, py in fae)
    stempel = f"<circle cx='0' cy='0' r='{r * .09:.1f}' fill='#7cb342' stroke='#4e7a24' stroke-width='.7'/>"
    return g("".join(o) + kern + stab + anth + stempel, x, y, extra="filter='url(#fSchatten)'" if schatten else "")


def blatt(x, y, laenge=26, rot=0, dunkel=False):
    """Blatt (Spitze zeigt bei rot=0 nach rechts) mit Mittelrippe."""
    L = laenge
    return g(f"<path d='M0,0 C{L * .25},{-L * .3} {L * .75},{-L * .26} {L},0 C{L * .75},{L * .26} {L * .25},{L * .3} 0,0 Z' fill='url(#{'gnBlattD' if dunkel else 'gnBlatt'})' stroke='#24632a' stroke-width='.9' stroke-linejoin='round'/>"
             f"<path d='M0,0 Q{L * .5},{-1} {L * .95},0' stroke='#cfeab4' stroke-width='.9' fill='none' opacity='.8'/>", x, y, 1, rot)


def apfel(x, y, r=22, mit_blatt=True, stiel=True):
    """Reifer roter Apfel, (x, y) = Mitte."""
    o = (f"<g filter='url(#fSchatten)'><path d='M0,{-r * .72} C{r * .28},{-r * 1.0} {r},{-r * .85} {r},{r * .02} C{r},{r * .68} {r * .55},{r} {r * .2},{r} Q0,{r * .92} {-r * .2},{r} "
         f"C{-r * .55},{r} {-r},{r * .68} {-r},{r * .02} C{-r},{-r * .85} {-r * .28},{-r * 1.0} 0,{-r * .72} Z' fill='url(#gnApfel)' stroke='#7a0c14' stroke-width='1.1'/></g>"
         f"<path d='M{-r * .6},{-r * .5} Q{-r * .75},{-r * .15} {-r * .6},{r * .22}' stroke='#fff' stroke-width='{max(2, r * .13):.1f}' fill='none' stroke-linecap='round' opacity='.5'/>"
         f"<path d='M{-r * .12},{-r * .72} Q0,{-r * .62} {r * .12},{-r * .72}' stroke='#7a0c14' stroke-width='1.2' fill='none' opacity='.6'/>")
    if stiel:
        o += f"<path d='M0,{-r * .7} Q{r * .05},{-r * 1.1} {r * .22},{-r * 1.3}' stroke='#6b4423' stroke-width='{max(2, r * .11):.1f}' fill='none' stroke-linecap='round'/>"
    if mit_blatt:
        o += blatt(r * .15, -r * 1.05, r * 1.0, -28)
    return g(o, x, y)


def _blume_koerper(art, stiel):
    """Wiesenblume mit Stängel (Fuß bei 0,0). art: margerite, mohn, kornblume, loewenzahn, klee."""
    s = 1.0
    cy = -stiel
    o = [f"<path d='M0,0 Q{-2 * s:.1f},{cy / 2:.1f} 0,{cy}' stroke='#3f9b3f' stroke-width='{1.8:.1f}' fill='none' stroke-linecap='round'/>",
         f"<path d='M0,{cy * .4:.1f} q-8,-3 -9,-8 q8,0 9,6 Z' fill='#4fae4f'/>"]
    if art == "margerite":
        pet = "".join(f"M{f(math.cos(a) * 3.2)},{f(cy + math.sin(a) * 3.2)}L{f(math.cos(a) * 8.2)},{f(cy + math.sin(a) * 8.2)}" for a in [i * math.pi / 5 for i in range(10)])
        o.append(f"<path d='{pet}' stroke='#fff' stroke-width='3.4' stroke-linecap='round' fill='none'/><path d='{pet}' stroke='#e9eef2' stroke-width='.7' fill='none'/>"
                 f"<circle cx='0' cy='{cy}' r='3.6' fill='#ffcc1f' stroke='#e69a00' stroke-width='.6'/>")
    elif art == "mohn":
        o.append("".join(f"<ellipse cx='{f(math.cos(a) * 4.5)}' cy='{f(cy + math.sin(a) * 4.5)}' rx='5.2' ry='5.8' fill='#e5322d' stroke='#a8130f' stroke-width='.6' "
                         f"transform='rotate({math.degrees(a) + 90:.0f} {f(math.cos(a) * 4.5)} {f(cy + math.sin(a) * 4.5)})'/>" for a in (math.pi * .25, math.pi * .75, math.pi * 1.25, math.pi * 1.75))
                 + f"<circle cx='0' cy='{cy}' r='2.6' fill='#2a1a1a'/>")
    elif art == "kornblume":
        pet = "".join(f"M{f(math.cos(a) * 2)},{f(cy + math.sin(a) * 2)}L{f(math.cos(a) * 7.5)},{f(cy + math.sin(a) * 7.5)}" for a in [i * math.pi / 4 + .2 for i in range(8)])
        o.append(f"<path d='{pet}' stroke='#3f6fd8' stroke-width='2.6' stroke-linecap='round' fill='none'/><circle cx='0' cy='{cy}' r='2.6' fill='#7a2db0'/>")
    elif art == "loewenzahn":
        pet = "".join(f"M0,{cy}L{f(math.cos(a) * 6.5)},{f(cy + math.sin(a) * 6.5)}" for a in [i * math.pi / 8 for i in range(16)])
        o.append(f"<path d='{pet}' stroke='#ffd21f' stroke-width='1.6' stroke-linecap='round' fill='none'/><circle cx='0' cy='{cy}' r='3' fill='#f2a900'/>")
    else:  # klee
        o.append(f"<circle cx='0' cy='{cy}' r='5.4' fill='#e879a6' stroke='#c24a7e' stroke-width='.7'/><circle cx='-1.6' cy='{cy - 1.6}' r='1.5' fill='#f6b3cd'/>")
    return "".join(o)


def wiesenblume(x, y, s=1.0, art="margerite", stiel=22, spiegeln=False):
    """Wiesenblume (Fuß bei x, y); jede Art wird je Szene nur einmal definiert und per <use> gesetzt."""
    key = f"gnF{art[:3]}{stiel}"
    if key not in _BIENEN:
        _BIENEN[key] = _blume_koerper(art, stiel)
    return g(f"<use href='#{key}'/>", x, y, s, 0, spiegeln)


# ═══════════════════════════════════════════════════════════════════════════
#  Insekten (klein, für Wiesen)
# ═══════════════════════════════════════════════════════════════════════════
def schmetterling(x, y, s=1.0, rot=0, farbe="#f2802a"):
    return g(f"<g filter='url(#fSchatten)'><path d='M0,0 C-8,-16 -24,-18 -22,-4 C-21,4 -9,3 0,0 Z' fill='{farbe}' stroke='#5b2a0a' stroke-width='1'/>"
             f"<path d='M0,0 C8,-16 24,-18 22,-4 C21,4 9,3 0,0 Z' fill='{farbe}' stroke='#5b2a0a' stroke-width='1'/>"
             f"<path d='M0,0 C-7,3 -17,6 -14,14 C-9,17 -2,9 0,0 Z' fill='#f6b04a' stroke='#5b2a0a' stroke-width='1'/>"
             f"<path d='M0,0 C7,3 17,6 14,14 C9,17 2,9 0,0 Z' fill='#f6b04a' stroke='#5b2a0a' stroke-width='1'/>"
             "<circle cx='-14' cy='-8' r='2.6' fill='#fff7e0'/><circle cx='14' cy='-8' r='2.6' fill='#fff7e0'/>"
             "<ellipse cx='0' cy='2' rx='1.8' ry='8' fill='#3a2a1a'/><circle cx='0' cy='-6.5' r='2.4' fill='#3a2a1a'/>"
             "<path d='M-.8,-8 Q-5,-14 -8,-13 M.8,-8 Q5,-14 8,-13' stroke='#3a2a1a' stroke-width='.9' fill='none' stroke-linecap='round'/></g>", x, y, s, rot)


def marienkaefer(x, y, s=1.0):
    return g("<g filter='url(#fSchatten)'><ellipse cx='0' cy='0' rx='7' ry='5.6' fill='#e0262b' stroke='#7a0c14' stroke-width='.9'/>"
             "<path d='M0,-5.6 V5.6' stroke='#2a1010' stroke-width='1'/><circle cx='-3' cy='-1.6' r='1.2' fill='#2a1010'/><circle cx='3' cy='-1.6' r='1.2' fill='#2a1010'/>"
             "<circle cx='-2.4' cy='2.4' r='1.1' fill='#2a1010'/><circle cx='2.4' cy='2.4' r='1.1' fill='#2a1010'/>"
             "<path d='M-4,-5.2 A5,2 0 0 1 4,-5.2 L3,-6.4 Q0,-8.2 -3,-6.4 Z' fill='#2a1010'/></g>", x, y, s)


def hummel(x, y, s=1.0, spiegeln=False, rot=0):
    """Hummel (rund, pelzig, gelb-schwarz mit weißem Hinterende), Seitenansicht, Kopf rechts."""
    o = ("<g filter='url(#fSchatten)'>"
         "<ellipse cx='-9' cy='-2' rx='13' ry='9' fill='#fff7e0' stroke='#8a6a3c' stroke-width='.8'/>"
         "<ellipse cx='-2' cy='-3' rx='10' ry='9.4' fill='#2a1f16'/>"
         "<path d='M-1,-12 Q3,-3 -1,6 L5,6 Q9,-3 5,-12 Z' fill='#f5c518'/>"
         "<ellipse cx='-14' cy='-2' rx='5' ry='7' fill='#f5c518' opacity='.0'/>"
         "<path d='M-9,-10 Q-6,-2 -9,6 L-14,5 Q-12,-2 -14,-10 Z' fill='#f5c518'/>"
         "<circle cx='11' cy='0' r='6' fill='#2a1f16'/><circle cx='13' cy='-1.6' r='1.8' fill='#fff' opacity='.6'/>"
         "<path d='M14,3 Q18,5 18,8' stroke='#2a1f16' stroke-width='1.8' fill='none' stroke-linecap='round'/>"
         "<ellipse cx='-3' cy='-13' rx='11' ry='4' transform='rotate(-24 -3 -13)' fill='url(#gnFlue)' stroke='#8fb4d0' stroke-width='.8'/>"
         "<path d='M-6,8 L-8,14 M0,9 L1,15 M5,8 L8,13' stroke='#2a1f16' stroke-width='1.6' stroke-linecap='round'/></g>")
    return g(o, x, y, s, rot, spiegeln)


def schwebfliege(x, y, s=1.0):
    return g("<g filter='url(#fSchatten)'><ellipse cx='-3' cy='0' rx='8' ry='3.4' fill='#f2c418'/>"
             "<path d='M-6,-3.2 V3.2 M-1,-3.4 V3.4' stroke='#2a1f16' stroke-width='1.6'/>"
             "<circle cx='6' cy='-.4' r='3.2' fill='#3a2a1a'/><circle cx='7' cy='-1.4' r='1.6' fill='#b34a2a'/>"
             "<ellipse cx='-2' cy='-5.4' rx='6.5' ry='2.2' transform='rotate(-18 -2 -5.4)' fill='url(#gnFlue)' stroke='#8fb4d0' stroke-width='.6'/></g>", x, y, s)


# ═══════════════════════════════════════════════════════════════════════════
#  Lupe (Kreis mit Rand und Schatten) und Verbindungslinien
# ═══════════════════════════════════════════════════════════════════════════
def lupe_rand(cx, cy, r, farbe="#c0392b"):
    return (f"<circle cx='{cx}' cy='{cy}' r='{r + 3}' fill='none' stroke='#fff' stroke-width='6'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{farbe}' stroke-width='3.4' filter='url(#fSchatten)'/>")


def clip_kreis(cid, cx, cy, r):
    return f"<clipPath id='{cid}'><circle cx='{cx}' cy='{cy}' r='{r}'/></clipPath>"


def clip_rect(cid, x, y, w, h, rx=12):
    return f"<clipPath id='{cid}'><rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}'/></clipPath>"


def tangenten(c1, r1, c2, r2, farbe="#c0392b", w=2):
    """Zwei Außentangenten zwischen zwei Kreisen (Lupen-Strahlen). c = (x, y)."""
    (x1, y1), (x2, y2) = c1, c2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    b = math.acos((r1 - r2) / d)
    out = ""
    for sg in (-1, 1):
        th = a + sg * b
        p1 = (x1 + r1 * math.cos(th), y1 + r1 * math.sin(th))
        p2 = (x2 + r2 * math.cos(th), y2 + r2 * math.sin(th))
        out += f"<line x1='{f(p1[0])}' y1='{f(p1[1])}' x2='{f(p2[0])}' y2='{f(p2[1])}' stroke='{farbe}' stroke-width='{w}' stroke-dasharray='5 4' opacity='.8'/>"
    return out


# Gemeinsame Muster-Defs für Kerzen (diagonale Streifen) – bei Bedarf in defs= der Szene anhängen
MUSTER_SPIRALE = ("<pattern id='pnSpirale' width='12' height='12' patternUnits='userSpaceOnUse' patternTransform='rotate(-32)'>"
                  "<rect width='12' height='4.5' fill='#fff' opacity='.42'/><rect y='6' width='12' height='2' fill='#7a470c' opacity='.22'/></pattern>")


# ═══════════════════════════════════════════════════════════════════════════
#  Weitere Bausteine
# ═══════════════════════════════════════════════════════════════════════════
def lokal(x, y, s, rot, spiegeln, lx, ly):
    """Rechnet einen Punkt (lx, ly) aus den Koordinaten einer mit g()/biene() gesetzten Figur in Bildkoordinaten um."""
    sx = -s if spiegeln else s
    a = math.radians(rot)
    px, py = lx * sx, ly * s
    return x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)


def wabenstueck(x, y, w, h, muster="pnLeer", dicke=10, rx=12):
    """Freistehendes Wabenstück mit Dicke (Rückseite versetzt). (x, y) = linke obere Ecke der Vorderseite."""
    return (f"<g filter='url(#fSchatten)'><rect x='{f(x + dicke)}' y='{f(y - dicke * .7)}' width='{f(w)}' height='{f(h)}' rx='{rx}' fill='#c9972b' stroke='#a8761c' stroke-width='1.2'/></g>"
            f"<path d='M{f(x + w - rx)},{f(y + h)} L{f(x + w - rx + dicke)},{f(y + h - dicke * .7)} L{f(x + w + dicke)},{f(y + rx - dicke * .7)} L{f(x + w)},{f(y + rx)} Z' fill='#d6a52e'/>"
            f"<rect x='{f(x)}' y='{f(y)}' width='{f(w)}' height='{f(h)}' rx='{rx}' fill='url(#{muster})' stroke='#b88a22' stroke-width='1.6'/>"
            f"<rect x='{f(x + 3)}' y='{f(y + 3)}' width='{f(w - 6)}' height='{f(h * .35)}' rx='{rx - 3}' fill='#fff' opacity='.13'/>")


def wachsplaettchen(x, y, s=1.0, rot=0):
    """Einzelnes Wachsplättchen (kleines Fünfeck)."""
    return g("<path d='M-3.6,-1.6 L3.4,-2 L4.6,2.6 L0.4,6 L-4.2,3 Z' fill='url(#gnWachsP)' stroke='#d9c27a' stroke-width='.7' stroke-linejoin='round'/>"
             "<path d='M-2.2,0 L2.4,-.6' stroke='#fff' stroke-width='.8' stroke-linecap='round'/>", x, y, s, rot)


def holzmaserung(x, y, w, h, n=7, seed=3, farbe="#6b3f19", op=.28):
    """Linien einer Holzmaserung in einem Rechteck."""
    rnd = random.Random(seed)
    d = ""
    for i in range(n):
        yy = y + h * (i + .5) / n + rnd.uniform(-2, 2)
        x0 = x + rnd.uniform(0, w * .25)
        d += f"M{f(x0)},{f(yy)} q{f(w * .2)},{f(rnd.uniform(-2, 2))} {f(w * .35)},0 t{f(w * .3)},{f(rnd.uniform(-1.5, 1.5))} "
    return f"<path d='{d}' stroke='{farbe}' stroke-width='1.1' fill='none' opacity='{op}' stroke-linecap='round'/>"


# ═══════════════════════════════════════════════════════════════════════════
#  Jahreszeiten-Bausteine (Imkerjahr)
# ═══════════════════════════════════════════════════════════════════════════
def eimer(x, y, s=1.0, farbe="#ffffff"):
    """Futtereimer mit Deckel (steht auf dem Kasten), (x, y) = Mitte der Standfläche; 26 breit, 22 hoch."""
    return g(f"<g filter='url(#fSchatten)'><path d='M-12,0 L-14,-19 H14 L12,0 Z' fill='url(#gnWeiss)' stroke='#8fa1b2' stroke-width='1.2'/>"
             f"<rect x='-15' y='-24' width='30' height='6' rx='2.5' fill='#2f7fc1' stroke='#1d5a8c' stroke-width='1'/>"
             f"<path d='M-14,-19 C-14,-34 14,-34 14,-19' stroke='#8fa1b2' stroke-width='1.6' fill='none'/></g>"
             f"<path d='M-9,-4 L-10,-16' stroke='#fff' stroke-width='2.4' opacity='.7' stroke-linecap='round'/>"
             f"<path d='M-7,-12 q3,-3 6,0 t6,0' stroke='#ffc928' stroke-width='2.4' fill='none' stroke-linecap='round'/>", x, y, s)


def kanne(x, y, s=1.0, farbe="#e8eef3"):
    """Kanne mit Griff und Ausguss (Futter), (x, y) = Mitte der Standfläche."""
    return g(f"<g filter='url(#fSchatten)'><path d='M-9,0 V-22 Q-9,-26 -5,-26 H5 Q9,-26 9,-22 V0 Z' fill='url(#gnWeiss)' stroke='#8fa1b2' stroke-width='1.2'/>"
             f"<rect x='-4' y='-31' width='8' height='6' rx='2' fill='#2f7fc1'/>"
             f"<path d='M9,-20 Q17,-20 17,-10 Q17,-3 9,-5' stroke='#8fa1b2' stroke-width='2.4' fill='none'/></g>"
             f"<path d='M-5,-4 V-20' stroke='#fff' stroke-width='2.4' opacity='.7' stroke-linecap='round'/>", x, y, s)


def flasche(x, y, s=1.0):
    """Kleine braune Flasche mit weißem Etikett (Mittel gegen Milben), (x, y) = Mitte der Standfläche."""
    return g("<g filter='url(#fSchatten)'><path d='M-6,0 V-14 Q-6,-18 -3,-20 V-27 H3 V-20 Q6,-18 6,-14 V0 Z' fill='#9a5a1c' stroke='#5c3510' stroke-width='1'/></g>"
             "<rect x='-6' y='-14' width='12' height='9' fill='#fffaf0' stroke='#c9a06a' stroke-width='.6'/>"
             "<path d='M0,-13 V-6 M-3.4,-9.5 H3.4' stroke='#c0392b' stroke-width='1.6'/>"
             "<rect x='-3.4' y='-30' width='6.8' height='4' rx='1' fill='#2f7fc1'/>", x, y, s)


def schneeflocken(w, h, n=24, seed=7, r=(1.2, 2.6)):
    rnd = random.Random(seed)
    return "".join(f"<circle cx='{f(rnd.uniform(0, w))}' cy='{f(rnd.uniform(0, h))}' r='{rnd.uniform(*r):.1f}' fill='#fff' opacity='{rnd.uniform(.7, 1):.2f}'/>" for _ in range(n))


def wintertraube(cx, cy, r=15, seed=9, n=70):
    """Kugel aus vielen Bienen (Wintertraube) mit warmem Schein. Brauchen: DEFS_TRAUBE in defs der Szene."""
    rnd = random.Random(seed)
    o = [f"<circle cx='{cx}' cy='{cy}' r='{r * 1.55:.1f}' fill='url(#gnGlut)'/>",
         f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#8a5516' stroke='#5a3410' stroke-width='1'/>"]
    pts = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = r * (rnd.random() ** .55) * .98
        pts.append((cx + d * math.cos(a), cy + d * math.sin(a) * .98, rnd.uniform(0, 180)))
    pts.sort(key=lambda q: q[1])
    for x, y, rot in pts:
        o.append(f"<use href='#gnKleineBiene' transform='translate({f(x)} {f(y)}) rotate({f(rot)})'/>")
    # Königin in der Mitte: etwas längerer Hinterleib, heller
    o.append(f"<g transform='translate({cx} {cy}) rotate(-20)'><ellipse cx='0' cy='0' rx='6.6' ry='2.6' fill='#f4c24a' stroke='#6a4410' stroke-width='.6'/>"
             f"<circle cx='5.6' cy='0' r='2' fill='#3a2812'/><path d='M-2,-2.4 V2.4 M-5,-2 V2' stroke='#4a3010' stroke-width='1'/></g>")
    return "".join(o)


DEFS_TRAUBE = ("<g id='gnKleineBiene'><ellipse cx='0' cy='0' rx='3.5' ry='2.1' fill='url(#gnBGelb)' stroke='#4a3010' stroke-width='.45'/>"
               "<path d='M-.6,-2 V2 M1.4,-1.9 V1.9' stroke='#3a2410' stroke-width='.8'/><circle cx='3.2' cy='0' r='1.3' fill='#3a2812'/></g>")


def kasten_schnitt(x, y, s=1.0, zargen=2, schnee=True, traube=True, muster=("pnHonig", "pnLeer")):
    """Bienenkasten im Schnitt (Vorderwand weggelassen): Rähmchen-Wabe mit Honig oben, Wintertraube in der Mitte.
    (x, y) = Mitte der Standfläche; Breite 70, Zarge 22 hoch."""
    top = -8 - 22 * zargen
    ih = 22 * zargen - 4
    o = ["<g filter='url(#fSchatten)'>",
         "<rect x='-35' y='-8' width='70' height='8' rx='1.5' fill='url(#gnHolz)' stroke='#7a4b22' stroke-width='1'/>",
         f"<rect x='-33' y='{top}' width='66' height='{22 * zargen}' fill='#6b4423' stroke='#4a2f17' stroke-width='1.2'/></g>",
         f"<rect x='-29' y='{top + 3}' width='58' height='{ih - 2}' fill='#d9a63a'/>",
         f"<rect x='-29' y='{top + 3}' width='58' height='{(ih - 2) * .36:.1f}' fill='url(#{muster[0]})'/>",
         f"<rect x='-29' y='{top + 3 + (ih - 2) * .36:.1f}' width='58' height='{(ih - 2) * .64:.1f}' fill='url(#{muster[1]})'/>",
         f"<rect x='-29' y='{top + 3}' width='58' height='{ih - 2}' fill='none' stroke='#7a4b22' stroke-width='1'/>",
         # Seitenwände (weiß gestrichen) und Rähmchen-Oberträger
         f"<rect x='-35' y='{top}' width='6' height='{22 * zargen}' fill='url(#gnWeissQ)' stroke='#6b7a88' stroke-width='1'/>",
         f"<rect x='29' y='{top}' width='6' height='{22 * zargen}' fill='url(#gnWeissQ)' stroke='#6b7a88' stroke-width='1'/>",
         f"<rect x='-33' y='{top}' width='66' height='4' fill='url(#gnHolzQ)' stroke='#7a4b22' stroke-width='.8'/>"]
    if traube:
        o.append(wintertraube(0, top + 3 + (ih - 2) * .56, 15 if zargen >= 2 else 11))
    o.append(f"<path d='M-38,{top} L-35,{top - 9} H35 L38,{top} Z' fill='url(#gnDeckel)' stroke='#5c6670' stroke-width='1.1'/>")
    if schnee:
        o.append(f"<path d='M-41,{top + 1} Q-39,{top - 15} -26,{top - 12} Q-14,{top - 18} 0,{top - 13} Q16,{top - 18} 27,{top - 12} Q39,{top - 15} 41,{top + 1} "
                 f"Q31,{top + 4} 21,{top + 1} Q11,{top + 5} 0,{top + 1} Q-11,{top + 5} -21,{top + 1} Q-31,{top + 4} -41,{top + 1} Z' fill='url(#gnSchnee)' stroke='#aac4d8' stroke-width='1'/>")
    return g("".join(o), x, y, s)


def traktor(x, y, s=1.0, nebel=True):
    """Kleiner Traktor mit Spritzgestänge (fährt nach links, Gestänge hinten). (x, y) = Boden unter dem Hinterrad.
    Sprühnebel unter dem Gestänge, hell und freundlich gezeichnet."""
    o = []
    if nebel:
        o.append("<g opacity='.85'>"
                 "<ellipse cx='42' cy='-8' rx='36' ry='12' fill='#e8f0f7'/><ellipse cx='30' cy='-13' rx='18' ry='9' fill='#f6fafd'/><ellipse cx='56' cy='-12' rx='16' ry='8' fill='#f6fafd'/></g>")
        o.append("<path d='" + "".join(f"M{xx},-22 L{xx - 5},-2 M{xx},-22 L{xx + 5},-2" for xx in (24, 36, 48, 60)) + "' stroke='#cfe0ee' stroke-width='1.6' stroke-linecap='round' opacity='.9'/>")
        o.append("".join(f"<circle cx='{xx}' cy='{yy}' r='1.2' fill='#fff' stroke='#b7cde0' stroke-width='.5'/>" for xx, yy in
                         ((20, -6), (30, -3), (40, -8), (52, -4), (64, -7), (26, -14), (46, -15), (58, -2), (36, -1))))
    # Gestänge
    o.append("<path d='M12,-26 H70' stroke='#5c6670' stroke-width='3' stroke-linecap='round'/>"
             "<path d='M18,-26 V-22 M30,-26 V-22 M42,-26 V-22 M54,-26 V-22 M66,-26 V-22' stroke='#334155' stroke-width='2' stroke-linecap='round'/>")
    # Räder, Rumpf, Kabine
    o.append("<g filter='url(#fSchatten)'>"
             "<circle cx='2' cy='-15' r='15' fill='#2d3748' stroke='#111827' stroke-width='1.4'/><circle cx='2' cy='-15' r='6.5' fill='#cbd5e1' stroke='#64748b' stroke-width='1'/>"
             "<circle cx='-34' cy='-9' r='9' fill='#2d3748' stroke='#111827' stroke-width='1.2'/><circle cx='-34' cy='-9' r='3.8' fill='#cbd5e1' stroke='#64748b' stroke-width='.8'/>"
             "<path d='M-44,-14 V-28 Q-44,-33 -39,-33 H-14 V-16 H-8 V-14 Z' fill='#d9302c' stroke='#8e1b18' stroke-width='1.2' stroke-linejoin='round'/>"
             "<rect x='-12' y='-52' width='24' height='32' rx='3' fill='#d9302c' stroke='#8e1b18' stroke-width='1.2'/>"
             "<rect x='-8' y='-48' width='16' height='15' rx='2' fill='#cfe8f7' stroke='#8e1b18' stroke-width='1'/>"
             "<rect x='-14' y='-55' width='28' height='4.5' rx='2' fill='#9b1f1c'/>"
             "<path d='M-34,-33 V-42' stroke='#334155' stroke-width='3' stroke-linecap='round'/>"
             "<path d='M-41,-28 H-18 M-41,-24 H-18 M-41,-20 H-18' stroke='#f4a3a0' stroke-width='1' opacity='.7'/></g>"
             "<path d='M-6,-47 L-6,-34' stroke='#fff' stroke-width='1.6' opacity='.7'/>")
    return g("".join(o), x, y, s)
