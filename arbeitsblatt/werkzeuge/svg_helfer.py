"""Gemeinsame Zeichenhelfer für die SVG-Schaubilder (Lesestrecken, Glossar, Bildpunkte-Karten).

NICHT ÄNDERN, nur erweitern – alle `werkzeuge/grafiken_<reiter>.py` bauen darauf auf. Wer einen Helfer
braucht, der hier fehlt, legt ihn in der eigenen Datei an (oder bittet darum, ihn hier aufzunehmen).

Abgeleitet aus dem Generator des Skills `ab-bauen` (assets/lese_grafiken_beispiel.py) – nur die
wiederverwendbaren Teile: Verläufe und Schatten, Beschriftung mit Halo, Pfeile, Basisformen, SVG-Rahmen.
Die gegenständlichen Szenen der Vorlage-Grafiken (Tiere, Landschaften anderer ABs) sind absichtlich NICHT übernommen.

Regeln (references/lernpfad.md):
  * Schaubild = gegenständliche, plastische Szene (Verläufe, Schatten), keine reinen Kästchen-Schemata.
  * viewBox 480 × 288 (Lesestrecke, Glossar) bzw. 900 × 560 (Karten für Bildpunkte).
  * Pfeilbeschriftung immer ÜBER oder UNTER dem Pfeil, nie auf der Linie, mit weißem Halo
    (paint-order: stroke), mindestens 10 px Abstand.
  * Animation nur als CSS-Keyframes im SVG, kein SMIL, kein JavaScript. Endzustand trägt die Aussage.
  * Jede Datei lässt sich später durch eine echte Abbildung gleichen Namens ersetzen.

Benutzung in einer Grafik-Datei:

    from svg_helfer import *            # (liegt im selben Ordner)
    def nutztier_1():
        return svg("Bauernhof mit Bienenkästen", himmel_wiese(170), sonne(410, 48), ...)
    GRAFIKEN = {"nutztier-1": nutztier_1}
    if __name__ == "__main__":
        erzeuge(GRAFIKEN)
"""

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ZIEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img", "lese")

# GSM-Farben (references/gestaltung.md) plus Textfarben
BLAU, DUNKEL, ORANGE, MAGENTA = "#006AB3", "#004b80", "#F7B800", "#AD007C"
ROT, GRUEN, GRAU, HELL, TEXT = "#dc2626", "#16a34a", "#6b7280", "#eef5fb", "#1e293b"
FONT = "font-family='Lato, Arial, sans-serif'"
W, H = 480, 288

# ═══════════════════════════════════════════════════════════════════════════
#  Verläufe und Schatten (ids in jedem SVG gleich – Dateien werden als <img> geladen)
# ═══════════════════════════════════════════════════════════════════════════
_VERLAEUFE = (
    "<linearGradient id='gHimmel' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#bfe0f7'/><stop offset='1' stop-color='#eef8ff'/></linearGradient>"
    "<linearGradient id='gWasser' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#7cc4ec'/><stop offset='1' stop-color='#26689b'/></linearGradient>"
    "<linearGradient id='gWiese' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#a5d977'/><stop offset='1' stop-color='#6ba340'/></linearGradient>"
    "<linearGradient id='gErde' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#a4703f'/><stop offset='1' stop-color='#5b3a1d'/></linearGradient>"
    "<linearGradient id='gLaub' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#6cbf4a'/><stop offset='1' stop-color='#2f7d32'/></linearGradient>"
    "<linearGradient id='gStamm' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#a5703c'/><stop offset='1' stop-color='#6b4423'/></linearGradient>"
    "<linearGradient id='gStein' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d7dde3'/><stop offset='1' stop-color='#8f9aa5'/></linearGradient>"
    # Bienen-Themen: Honig, Wachs, Holz (Bienenkasten), Fell der Biene
    "<linearGradient id='gHonig' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffd45a'/><stop offset='1' stop-color='#e08a00'/></linearGradient>"
    "<linearGradient id='gWachs' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#fff1b8'/><stop offset='1' stop-color='#e9c46a'/></linearGradient>"
    "<linearGradient id='gHolz' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#d9b27c'/><stop offset='1' stop-color='#a8743c'/></linearGradient>"
    "<linearGradient id='gFell' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#f6c23e'/><stop offset='1' stop-color='#b9770e'/></linearGradient>"
    "<radialGradient id='gSonne' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#fff6bf'/><stop offset='.55' stop-color='#F7B800'/><stop offset='1' stop-color='#F7B800' stop-opacity='0'/></radialGradient>"
    "<filter id='fSchatten' x='-25%' y='-25%' width='150%' height='160%'><feDropShadow dx='0' dy='2' stdDeviation='1.5' flood-color='#000' flood-opacity='.26'/></filter>"
)

# Farben, für die pfeil()/bogen() eine Pfeilspitze (marker) brauchen. svg() schreibt sie genau einmal.
_MARKER = set()


def _marker_defs() -> str:
    return "".join(
        f"<marker id='m{c[1:]}' markerWidth='8' markerHeight='8' refX='6.5' refY='4' orient='auto'>"
        f"<path d='M0,0 L8,4 L0,8 z' fill='{c}'/></marker>"
        for c in sorted(_MARKER))


def svg(titel, *teile, w=W, h=H, defs_extra="", grund="url(#gHimmel)", rahmen=True):
    """SVG-Rahmen: Titel (für Screenreader), Verläufe, Pfeilspitzen und Hintergrund.

    `defs_extra`: zusätzliche <defs>-Inhalte (z. B. clipPath, Muster). `grund`: Füllung des Hintergrunds.
    Muss nach dem Aufbau der Teile aufgerufen werden (sammelt die benötigten Pfeilspitzen ein).
    """
    body = "\n".join(p for p in teile if p)
    defs = f"<defs>{_VERLAEUFE}{_marker_defs()}{defs_extra}</defs>"
    _MARKER.clear()
    rx = " rx='14'" if rahmen else ""
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' role='img' aria-label='{escape(titel)}' {FONT}>\n"
            f"<title>{escape(titel)}</title>\n{defs}\n<rect width='{w}' height='{h}'{rx} fill='{grund}'/>\n{body}\n</svg>\n")


# ═══════════════════════════════════════════════════════════════════════════
#  Text und Pfeile
# ═══════════════════════════════════════════════════════════════════════════
def t(x, y, text, size=13, weight=700, fill=TEXT, anchor="middle"):
    """Text mit Halo – lesbar auf Wasser, Wiese und Himmel.

    Heller Text bekommt einen dunklen Halo. Ein weißer Halo unter weißem Text macht die
    Beschriftung unsichtbar.
    """
    halo = "#14304a" if fill.lower() in ("#fff", "#ffffff") else "#fff"
    return (f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' font-weight='{weight}' fill='{fill}' text-anchor='{anchor}' "
            f"paint-order='stroke' stroke='{halo}' stroke-width='4' stroke-linejoin='round'>{escape(text)}</text>")


def tp(x, y, text, size=12, weight=700, fill=TEXT, anchor="middle"):
    """Text ohne Halo (auf weißem Grund, z. B. in Kästen)."""
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' font-weight='{weight}' fill='{fill}' text-anchor='{anchor}'>{escape(text)}</text>"


def _mk(farbe):
    _MARKER.add(farbe)
    return f"m{farbe[1:]}"


def pfeil(x1, y1, x2, y2, farbe=DUNKEL, w=3, label="", oben=True, dash="", size=11, lfill=None):
    """Pfeil mit Beschriftung ÜBER (oben=True) oder UNTER der Linie – nie darauf."""
    mid = _mk(farbe)
    d = f" stroke-dasharray='{dash}'" if dash else ""
    out = (f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{farbe}' stroke-width='{w}' "
           f"marker-end='url(#{mid})' stroke-linecap='round'{d}/>")
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out += t(mx, my - 11 if oben else my + 17, label, size, 800, lfill or farbe)
    return out


def bogen(d, farbe=DUNKEL, w=3, dash=""):
    """Gebogener Pfeil entlang eines SVG-Pfads `d`."""
    mid = _mk(farbe)
    dd = f" stroke-dasharray='{dash}'" if dash else ""
    return (f"<path d='{d}' fill='none' stroke='{farbe}' stroke-width='{w}' marker-end='url(#{mid})' "
            f"stroke-linecap='round'{dd}/>")


def tafel(x, y, w, h, zeilen, farbe=BLAU, size=12, fuell="#fff"):
    """Beschriftungstafel mit Rahmen – für Legenden und Begriffe."""
    out = (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='8' fill='{fuell}' opacity='.94' "
           f"stroke='{farbe}' stroke-width='2' filter='url(#fSchatten)'/>")
    start = y + h / 2 - (len(zeilen) - 1) * (size + 3) / 2 + size / 3
    for i, z in enumerate(zeilen):
        out += tp(x + w / 2, start + i * (size + 3), z, size, 800 if i == 0 else 600, farbe if i == 0 else TEXT)
    return out


def fussleiste(zeilen, hoehe=34, farbe=TEXT, size=12, h=H, w=W):
    """Weiße Beschriftungsleiste am unteren Bildrand (eine oder mehrere Zeilen)."""
    sizes = size if isinstance(size, (list, tuple)) else [size] * len(zeilen)
    out = (f"<rect x='0' y='{h - hoehe}' width='{w}' height='{hoehe}' fill='#fff' opacity='.95'/>"
           f"<line x1='0' y1='{h - hoehe}' x2='{w}' y2='{h - hoehe}' stroke='#cbd5e1'/>")
    if len(zeilen) == 1:
        return out + tp(w / 2, h - hoehe / 2 + sizes[0] / 3, zeilen[0], sizes[0], 800, farbe)
    y = h - hoehe + 3
    for i, (z, s) in enumerate(zip(zeilen, sizes)):
        y += s + 1
        out += tp(w / 2, y, z, s, 800 if i == 0 else 600, farbe if i == 0 else GRAU)
    return out


def achsen(x0, y0, w, h, xlabel, ylabel):
    """Koordinatensystem (für Diagramm-Schaubilder); Achsenbeschriftung liegt außerhalb der Fläche."""
    return (f"<rect x='{x0}' y='{y0 - h}' width='{w}' height='{h}' fill='#fff' opacity='.92' rx='6'/>"
            f"<line x1='{x0}' y1='{y0}' x2='{x0 + w + 8}' y2='{y0}' stroke='{TEXT}' stroke-width='2'/>"
            f"<line x1='{x0}' y1='{y0}' x2='{x0}' y2='{y0 - h - 8}' stroke='{TEXT}' stroke-width='2'/>"
            f"<path d='M{x0 + w + 8},{y0} l-6,-4 v8 z' fill='{TEXT}'/>"
            f"<path d='M{x0},{y0 - h - 8} l-4,6 h8 z' fill='{TEXT}'/>"
            + tp(x0 + w / 2, y0 + 17, xlabel, 11, 700, GRAU)
            + f"<text x='{x0 - 13}' y='{y0 - h / 2}' font-size='11' font-weight='700' fill='{GRAU}' text-anchor='middle' "
              f"transform='rotate(-90 {x0 - 13} {y0 - h / 2})'>{escape(ylabel)}</text>")


# ═══════════════════════════════════════════════════════════════════════════
#  Basisformen und Landschaft
# ═══════════════════════════════════════════════════════════════════════════
def himmel_wiese(horizont=180, h=H, w=W):
    """Hügelige Wiese ab `horizont`; der Himmel ist der Hintergrund von svg()."""
    return (f"<path d='M0,{horizont + 12} Q{w * .25},{horizont - 10} {w * .5},{horizont + 4} T{w},{horizont - 2} "
            f"V{h} H0 Z' fill='url(#gWiese)' stroke='#5b8a3a' stroke-width='1.2'/>")


def erdboden(y, h=H, w=W):
    return (f"<path d='M0,{y} Q{w * .3},{y - 6} {w * .6},{y + 3} T{w},{y - 2} V{h} H0 Z' "
            f"fill='url(#gErde)' stroke='#4a2f17' stroke-width='1.2'/>")


def sonne(x, y, r=22, strahlen=True):
    out = f"<circle cx='{x}' cy='{y}' r='{r * 2.1:.1f}' fill='url(#gSonne)'/>"
    if strahlen:
        for i in range(8):
            a = i * math.pi / 4
            x1, y1 = x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3
            x2, y2 = x + math.cos(a) * r * 1.8, y + math.sin(a) * r * 1.8
            out += f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='#f2a900' stroke-width='3' stroke-linecap='round'/>"
    return out + f"<circle cx='{x}' cy='{y}' r='{r}' fill='#ffd43b' stroke='#f2a900' stroke-width='2.5'/>"


def wolke(x, y, s=1.0, regen=False):
    out = (f"<path d='M{x - 30 * s},{y + 10 * s} h{60 * s} a{11 * s},{11 * s} 0 0 0 {4 * s},-{19 * s} "
           f"a{20 * s},{20 * s} 0 0 0 -{26 * s},-{18 * s} a{26 * s},{26 * s} 0 0 0 -{45 * s},-2 "
           f"a{21 * s},{21 * s} 0 0 0 -{17 * s},{26 * s} a{11 * s},{11 * s} 0 0 0 {24 * s},{13 * s} Z' "
           f"fill='#ffffff' stroke='#9db4c8' stroke-width='{2 * s:.1f}' stroke-linejoin='round' filter='url(#fSchatten)'/>")
    if regen:
        for i in range(4):
            rx = x - 22 * s + i * 16 * s
            out += (f"<line x1='{rx:.1f}' y1='{y + 14 * s:.1f}' x2='{rx - 4 * s:.1f}' y2='{y + 28 * s:.1f}' "
                    f"stroke='#4a90d9' stroke-width='{2.6 * s:.1f}' stroke-linecap='round'/>")
    return out


def baum(x, y, s=1.0, laub="url(#gLaub)"):
    """Laubbaum, x = Mitte, y = Boden. Für Obstbäume: `laub` mit eigener Farbe überschreiben."""
    return (f"<g filter='url(#fSchatten)'>"
            f"<path d='M{x - 6 * s},{y} v-{34 * s} h{12 * s} v{34 * s} z' fill='url(#gStamm)'/>"
            f"<path d='M{x - 5 * s},{y - 24 * s} q-{12 * s},-{4 * s} -{18 * s},-{12 * s} M{x + 5 * s},{y - 26 * s} q{12 * s},-{4 * s} {17 * s},-{11 * s}' "
            f"stroke='#6b4423' stroke-width='{3 * s:.1f}' fill='none' stroke-linecap='round'/>"
            f"<circle cx='{x}' cy='{y - 52 * s:.1f}' r='{22 * s:.1f}' fill='{laub}'/>"
            f"<circle cx='{x - 17 * s:.1f}' cy='{y - 42 * s:.1f}' r='{14 * s:.1f}' fill='{laub}'/>"
            f"<circle cx='{x + 17 * s:.1f}' cy='{y - 42 * s:.1f}' r='{14 * s:.1f}' fill='{laub}'/>"
            f"<circle cx='{x - 9 * s:.1f}' cy='{y - 64 * s:.1f}' r='{13 * s:.1f}' fill='{laub}'/>"
            f"<circle cx='{x + 10 * s:.1f}' cy='{y - 63 * s:.1f}' r='{12 * s:.1f}' fill='{laub}'/>"
            f"</g>")


def nadelbaum(x, y, s=1.0):
    return (f"<g filter='url(#fSchatten)'>"
            f"<rect x='{x - 3 * s}' y='{y - 14 * s}' width='{6 * s}' height='{14 * s}' fill='#6b4423'/>"
            f"<path d='M{x},{y - 66 * s} l{15 * s},{24 * s} h-{30 * s} z' fill='#2f7d32'/>"
            f"<path d='M{x},{y - 50 * s} l{19 * s},{26 * s} h-{38 * s} z' fill='#357f38'/>"
            f"<path d='M{x},{y - 32 * s} l{22 * s},{20 * s} h-{44 * s} z' fill='#2f7d32'/>"
            f"</g>")


def gras(x, y, s=1.0, farbe="#2f7d2f"):
    return (f"<path d='M{x - 6 * s},{y} q{2 * s},-{11 * s} -{1 * s},-{16 * s} M{x},{y} q{1 * s},-{12 * s} {4 * s},-{16 * s} "
            f"M{x + 6 * s},{y} q{2 * s},-{9 * s} {7 * s},-{13 * s}' fill='none' stroke='{farbe}' "
            f"stroke-width='{2.2 * s:.1f}' stroke-linecap='round'/>")


def stein(x, y, s=1.0):
    return (f"<path d='M{x - 22 * s},{y} q-{6 * s},-{13 * s} {8 * s},-{18 * s} q{18 * s},-{7 * s} {30 * s},{3 * s} "
            f"q{8 * s},{7 * s} {2 * s},{15 * s} z' fill='url(#gStein)' stroke='#6b7580' stroke-width='{1.6 * s:.1f}' filter='url(#fSchatten)'/>"
            f"<path d='M{x - 10 * s},{y - 11 * s} q{10 * s},-{5 * s} {19 * s},-{1 * s}' fill='none' stroke='#eef2f6' stroke-width='{2 * s:.1f}' stroke-linecap='round'/>")


def blume(x, y, s=1.0, farbe="#e879a6"):
    """Stängel mit Blatt und fünfblättriger Blüte, x = Fuß, y = Boden."""
    out = (f"<path d='M{x},{y} q-{2 * s},-{14 * s} {1 * s},-{22 * s}' fill='none' stroke='#3f9b3f' stroke-width='{2.2 * s:.1f}' stroke-linecap='round'/>"
           f"<path d='M{x - 1 * s},{y - 10 * s} q-{9 * s},-{4 * s} -{10 * s},-{9 * s} q{8 * s},0 {10 * s},{6 * s} z' fill='#3f9b3f'/>")
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        out += (f"<ellipse cx='{x + 1 * s + math.cos(a) * 6 * s:.1f}' cy='{y - 22 * s + math.sin(a) * 6 * s:.1f}' "
                f"rx='{5 * s:.1f}' ry='{3.4 * s:.1f}' fill='{farbe}' transform='rotate({math.degrees(a):.0f} "
                f"{x + 1 * s + math.cos(a) * 6 * s:.1f} {y - 22 * s + math.sin(a) * 6 * s:.1f})'/>")
    return out + f"<circle cx='{x + 1 * s:.1f}' cy='{y - 22 * s:.1f}' r='{3.4 * s:.1f}' fill='#ffd530'/>"


def biene(x, y, s=1.0):
    """Einfache Biene im Flug von der Seite (Symbolgröße ~16 px). Detailzeichnungen: eigene Datei."""
    return (f"<g filter='url(#fSchatten)'>"
            f"<ellipse cx='{x}' cy='{y}' rx='{8 * s:.1f}' ry='{5.5 * s:.1f}' fill='#f2b705'/>"
            f"<path d='M{x - 3 * s},{y - 5 * s} v{10 * s} M{x + 2 * s},{y - 5.2 * s} v{10.4 * s}' stroke='#2f2a24' stroke-width='{2.2 * s:.1f}'/>"
            f"<circle cx='{x + 8 * s:.1f}' cy='{y - 1 * s:.1f}' r='{3.6 * s:.1f}' fill='#2f2a24'/>"
            f"<ellipse cx='{x - 1 * s:.1f}' cy='{y - 7 * s:.1f}' rx='{7 * s:.1f}' ry='{3 * s:.1f}' fill='#cfe9ff' stroke='#8ec2e8' "
            f"stroke-width='{.8 * s:.1f}' opacity='.9' transform='rotate(-18 {x - 1 * s:.1f} {y - 7 * s:.1f})'/>"
            f"</g>")


def sechseck(cx, cy, r, fill="url(#gWachs)", stroke="#c9972b", sw=1.6, spitz_oben=False):
    """Regelmäßiges Sechseck (Wabenzelle). Standard: flache Seite oben; `spitz_oben` dreht um 30°."""
    off = -math.pi / 2 if spitz_oben else 0
    pts = " ".join(f"{cx + r * math.cos(off + i * math.pi / 3):.1f},{cy + r * math.sin(off + i * math.pi / 3):.1f}" for i in range(6))
    return f"<polygon points='{pts}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' stroke-linejoin='round'/>"


def waben_gitter(x0, y0, spalten, zeilen, r=14, fuellung=None, **kw):
    """Wabenmuster aus Sechsecken (flache Seite oben, Zeilen versetzt). `fuellung(spalte, zeile)` darf eine
    Füllfarbe je Zelle liefern (z. B. Honig, Pollen, Brut); None = Wachs."""
    out = ""
    dx, dy = r * 1.5, r * math.sqrt(3)
    for c in range(spalten):
        for z in range(zeilen):
            cx = x0 + c * dx
            cy = y0 + z * dy + (dy / 2 if c % 2 else 0)
            f = (fuellung(c, z) if fuellung else None) or "url(#gWachs)"
            out += sechseck(cx, cy, r, fill=f, **kw)
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  Ausgabe
# ═══════════════════════════════════════════════════════════════════════════
def schreiben(name, inhalt, ziel=ZIEL):
    os.makedirs(ziel, exist_ok=True)
    pfad = os.path.join(ziel, name + ".svg")
    with open(pfad, "w", encoding="utf-8", newline="\n") as f:
        f.write(inhalt)
    return pfad


def erzeuge(grafiken: dict, ziel=ZIEL):
    """Schreibt alle Grafiken eines Dicts {dateiname_ohne_endung: funktion()} nach static/img/lese/."""
    for name, fn in grafiken.items():
        schreiben(name, fn(), ziel)
    print(f"{len(grafiken)} Grafiken nach {ziel} geschrieben")
