"""Zeichenhelfer für Honigbienen-Schaubilder (Reiter „Nutztier Biene“ und „Die Biene“).

Gehört zu `grafiken_nutztier.py` und `grafiken_koerper.py`; andere Grafik-Dateien dürfen sich nicht darauf verlassen.
Alles ist reines SVG-Text-Zeug (kein JavaScript, kein SMIL) und baut auf `svg_helfer.py` auf.

Aufbau
  * Defs (`DEFS_BIENE`): Verläufe, Facettenmuster, Waben – als `defs_extra` an `svg()` übergeben.
  * `haare()` / `flaum()`: Pelz und Borsten (zufällig, aber mit festem Startwert → reproduzierbar).
  * `biene_seite()`: Biene von der Seite in lokalen Koordinaten (Ursprung = Mitte der Brust, Blick nach rechts).
  * `fluegel()`, `bein()`, `kopf_vorn()`, `hinterbein()`, `situs_hinterleib()`, `stachel_gross()`, `biene_klein()`.
  * `beschriftung()`: Beschriftung mit Pfeil – Text immer ÜBER oder UNTER dem Pfeilanfang, nie auf der Linie, mit Halo.
Koordinaten der Körperteile (lokal): Brust = Ellipse (0,0, 44×40), Kopf = KOPF_D, Hinterleib = HL_D.
"""
import math
import random

from svg_helfer import *  # noqa: F401,F403  (svg, t, tp, pfeil, … – gemeinsame Helfer)

# ═══════════════════════════════════════════════════════════════════════════
#  Verläufe, Muster
# ═══════════════════════════════════════════════════════════════════════════
def _hex_pattern(pid, r, rand="#fff", dicke=.6, opa=.5):
    """Facetten-Muster (Sechsecke, Spitze oben) als <pattern>. r = Umkreisradius."""
    w, h = math.sqrt(3) * r, 3 * r

    def poly(cx, cy):
        pts = " ".join(f"{cx + r * math.cos(math.radians(-90 + 60 * i)):.2f},{cy + r * math.sin(math.radians(-90 + 60 * i)):.2f}" for i in range(6))
        return f"<polygon points='{pts}'/>"
    zellen = "".join(poly(x, y) for x, y in [(0, 0), (w, 0), (w / 2, 1.5 * r), (0, 3 * r), (w, 3 * r)])
    return (f"<pattern id='{pid}' patternUnits='userSpaceOnUse' width='{w:.2f}' height='{h:.2f}'>"
            f"<g fill='none' stroke='{rand}' stroke-width='{dicke}' opacity='{opa}'>{zellen}</g></pattern>")


DEFS_BIENE = (
    # Pelz der Biene (goldbraun) und Körperverläufe
    "<radialGradient id='bPelz' cx='.42' cy='.3' r='.85'><stop offset='0' stop-color='#fbd978'/><stop offset='.5' stop-color='#e6a823'/><stop offset='1' stop-color='#9a5f0e'/></radialGradient>"
    "<radialGradient id='bBrust' cx='.45' cy='.32' r='.8'><stop offset='0' stop-color='#f2c660'/><stop offset='.55' stop-color='#c88a30'/><stop offset='1' stop-color='#6a4216'/></radialGradient>"
    "<linearGradient id='bVol' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='.42'/><stop offset='.35' stop-color='#fff' stop-opacity='0'/><stop offset='.7' stop-color='#000' stop-opacity='.1'/><stop offset='1' stop-color='#1b0f02' stop-opacity='.5'/></linearGradient>"
    "<linearGradient id='bKopf' x1='0' y1='0' x2='.4' y2='1'><stop offset='0' stop-color='#6a4a2a'/><stop offset='1' stop-color='#241609'/></linearGradient>"
    "<radialGradient id='bAuge' cx='.35' cy='.28' r='.85'><stop offset='0' stop-color='#8a6a45'/><stop offset='.35' stop-color='#3f2a16'/><stop offset='1' stop-color='#0f0803'/></radialGradient>"
    "<linearGradient id='bBein' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#6b4e35'/><stop offset='.45' stop-color='#3b2a1c'/><stop offset='1' stop-color='#1c130b'/></linearGradient>"
    "<linearGradient id='bFluegel' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffffff' stop-opacity='.85'/><stop offset='.5' stop-color='#d9eefb' stop-opacity='.55'/><stop offset='1' stop-color='#f1dcf5' stop-opacity='.5'/></linearGradient>"
    "<radialGradient id='bGlanz' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#fff' stop-opacity='.95'/><stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>"
    "<radialGradient id='bPollen' cx='.38' cy='.3' r='.85'><stop offset='0' stop-color='#fff08a'/><stop offset='.45' stop-color='#f6bf1c'/><stop offset='1' stop-color='#c27d08'/></radialGradient>"
    "<radialGradient id='bNektar' cx='.35' cy='.3' r='.85'><stop offset='0' stop-color='#fff1a8'/><stop offset='.5' stop-color='#f7b81c'/><stop offset='1' stop-color='#d98200'/></radialGradient>"
    "<linearGradient id='bSack' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffd9e3'/><stop offset='1' stop-color='#e58ba9'/></linearGradient>"
    "<linearGradient id='bDarm' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b9a64a'/><stop offset='1' stop-color='#6f6122'/></linearGradient>"
    "<linearGradient id='bSchnitt' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff6d2'/><stop offset='1' stop-color='#f7e0a0'/></linearGradient>"
    "<linearGradient id='bMuskel' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#e0584b'/><stop offset='1' stop-color='#a42a24'/></linearGradient>"
    "<linearGradient id='bChitin' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#c7852a'/><stop offset='1' stop-color='#6a3d0a'/></linearGradient>"
    "<linearGradient id='bGift' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e8f6ff'/><stop offset='1' stop-color='#9ccbe6'/></linearGradient>"
    "<filter id='bWeich' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='4'/></filter>"
    "<filter id='bFuzz' x='-15%' y='-15%' width='130%' height='130%'><feTurbulence type='fractalNoise' baseFrequency='.5' numOctaves='2' seed='7' result='n'/><feDisplacementMap in='SourceGraphic' in2='n' scale='10' xChannelSelector='R' yChannelSelector='G'/></filter>"
    "<filter id='bWeich2' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='1.6'/></filter>"
    + _hex_pattern("bHex", 3.4, "#e8d0a8", .55, .45)
    + _hex_pattern("bHexG", 9, "#e8d0a8", 1.1, .5)
    + _hex_pattern("bHexM", 5.6, "#f2dfbf", .8, .5)
)

KOPF_D = ("M50,-18 C54,-36 90,-42 104,-18 C114,-2 108,18 100,31 C92,43 72,45 62,37 C52,28 46,-4 50,-18 Z")
HL_D = ("M-36,-6 C-48,-36 -112,-50 -162,-28 C-192,-14 -206,4 -216,14 L-200,24 "
        "C-178,44 -112,52 -62,36 C-44,30 -34,16 -36,-6 Z")
BRUST_E = (0, 0, 44, 40)          # cx, cy, rx, ry
GOLD, DUNKEL_B, HELLGOLD = "#e8aa22", "#2f2013", "#fbe08a"


# ═══════════════════════════════════════════════════════════════════════════
#  Pelz und Borsten
# ═══════════════════════════════════════════════════════════════════════════
HAAR_DICHTE = 1.0   # Faktor für die Zahl der Haare (kleine Bienen brauchen weniger → kleinere Dateien)


class dichte:
    """Kontextmanager: `with dichte(.6): …` zeichnet alle Haare mit 60 % der Anzahl."""
    def __init__(self, f):
        self.f = f

    def __enter__(self):
        global HAAR_DICHTE
        self.alt, HAAR_DICHTE = HAAR_DICHTE, self.f

    def __exit__(self, *a):
        global HAAR_DICHTE
        HAAR_DICHTE = self.alt


def _n(n):
    return max(1, round(n * HAAR_DICHTE))


def _nrm(x, y):
    l = math.hypot(x, y) or 1.0
    return x / l, y / l


def haare(cx, cy, rx, ry, n, laenge, farbe, w=1.1, rot=0, a0=0, a1=360, richtung=(-1, .25), aussen=.7,
          seed=1, einwaerts=2.0, kruemmung=.3, opa=1.0):
    """Haare entlang einer Ellipse (Mitte cx,cy, Halbachsen rx,ry, gedreht um `rot` Grad), Winkelbereich a0…a1 Grad.
    `richtung` = Strichrichtung (Pelz liegt nach hinten), `aussen` = Anteil nach außen. Ein <path> je Aufruf."""
    rng = random.Random(seed)
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    d = []
    for _ in range(_n(n)):
        th = math.radians(a0 + (a1 - a0) * rng.random())
        ex, ey = rx * math.cos(th), ry * math.sin(th)
        nx, ny = _nrm(math.cos(th) / rx, math.sin(th) / ry)
        px, py = cx + ex * cr - ey * sr, cy + ex * sr + ey * cr
        ng_x, ng_y = nx * cr - ny * sr, nx * sr + ny * cr
        dx, dy = _nrm(ng_x * aussen + richtung[0], ng_y * aussen + richtung[1])
        L = laenge * (.6 + .8 * rng.random())
        sx, sy = px - ng_x * einwaerts, py - ng_y * einwaerts
        k = kruemmung * L * (rng.random() - .5) * 2
        mx, my = dx * L / 2 - dy * k, dy * L / 2 + dx * k
        d.append(f"M{sx:.1f},{sy:.1f}q{mx:.1f},{my:.1f} {dx * L:.1f},{dy * L:.1f}")
    o = f" opacity='{opa}'" if opa < 1 else ""
    return (f"<path d='{''.join(d)}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round'{o}/>")


def flaum(cx, cy, rx, ry, n, laenge, farbe, w=1.0, rot=0, richtung=(-1, .35), seed=1, opa=.8):
    """Kurze Pelzstriche im Inneren einer Ellipse (Textur)."""
    rng = random.Random(seed)
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    d = []
    for _ in range(_n(n)):
        r = math.sqrt(rng.random())
        th = rng.random() * 2 * math.pi
        ex, ey = r * rx * math.cos(th), r * ry * math.sin(th)
        px, py = cx + ex * cr - ey * sr, cy + ex * sr + ey * cr
        dx, dy = _nrm(richtung[0] + (rng.random() - .5) * .8, richtung[1] + (rng.random() - .5) * .8)
        L = laenge * (.5 + rng.random())
        d.append(f"M{px:.1f},{py:.1f}l{dx * L:.1f},{dy * L:.1f}")
    return f"<path d='{''.join(d)}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round' opacity='{opa}'/>"


def haare_linie(x0, y0, x1, y1, n, laenge, farbe, w=1.0, richtung=(-1, .4), seed=1, opa=1.0, auswahl=None):
    """Haare entlang einer Strecke (z. B. Nahtkante zwischen Hinterleibsringen)."""
    rng = random.Random(seed)
    d = []
    n = _n(n)
    for i in range(n):
        f = (i + rng.random() * .9) / n
        px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        dx, dy = _nrm(richtung[0] + (rng.random() - .5) * .6, richtung[1] + (rng.random() - .5) * .6)
        L = laenge * (.6 + .8 * rng.random())
        d.append(f"M{px:.1f},{py:.1f}l{dx * L:.1f},{dy * L:.1f}")
    o = f" opacity='{opa}'" if opa < 1 else ""
    return f"<path d='{''.join(d)}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round'{o}/>"


def haare_kurve(segmente, n, laenge, farbe, w=1.0, richtung=(-1, .3), aussen=.8, seed=1, einwaerts=1.5, opa=1.0):
    """Haare entlang zusammengesetzter Kubik-Bézierkurven (je Segment (P0,P1,P2,P3)); die Außenseite liegt links der
    Laufrichtung der Kurve (Normale = (−dy, dx))."""
    rng = random.Random(seed)
    d = []
    for _ in range(_n(n)):
        (p0, p1, p2, p3) = segmente[rng.randrange(len(segmente))]
        u = rng.random()
        a = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
        px = a[0] * p0[0] + a[1] * p1[0] + a[2] * p2[0] + a[3] * p3[0]
        py = a[0] * p0[1] + a[1] * p1[1] + a[2] * p2[1] + a[3] * p3[1]
        b = 3 * (1 - u) ** 2, 6 * (1 - u) * u, 3 * u ** 2
        tx = b[0] * (p1[0] - p0[0]) + b[1] * (p2[0] - p1[0]) + b[2] * (p3[0] - p2[0])
        ty = b[0] * (p1[1] - p0[1]) + b[1] * (p2[1] - p1[1]) + b[2] * (p3[1] - p2[1])
        tx, ty = _nrm(tx, ty)
        nx, ny = -ty, tx
        dx, dy = _nrm(nx * aussen + richtung[0] * (1 - aussen), ny * aussen + richtung[1] * (1 - aussen))
        L = laenge * (.6 + .8 * rng.random())
        sx, sy = px - nx * einwaerts, py - ny * einwaerts
        k = .25 * L * (rng.random() - .5) * 2
        d.append(f"M{sx:.1f},{sy:.1f}q{dx * L / 2 - dy * k:.1f},{dy * L / 2 + dx * k:.1f} {dx * L:.1f},{dy * L:.1f}")
    o = f" opacity='{opa}'" if opa < 1 else ""
    return f"<path d='{''.join(d)}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round'{o}/>"


# Umriss des Hinterleibs als Kubik-Segmente (Oberseite von vorn nach hinten, Unterseite von hinten nach vorn)
HL_SEG_OBEN = [((-36, -6), (-48, -36), (-112, -50), (-162, -28)), ((-162, -28), (-192, -14), (-206, 4), (-216, 14))]
HL_SEG_UNTEN = [((-200, 24), (-178, 44), (-112, 52), (-62, 36)), ((-62, 36), (-44, 30), (-34, 16), (-36, -6))]


def _id_zaehler():
    n = 0
    while True:
        n += 1
        yield n


_IDZ = _id_zaehler()


def neue_id(p="c"):
    return f"{p}{next(_IDZ)}"


# ═══════════════════════════════════════════════════════════════════════════
#  Flügel
# ═══════════════════════════════════════════════════════════════════════════
def fluegel(L=150, w=44, typ="vor", opa=1.0):
    """Flügel in Standardlage: Ansatz im Ursprung, Spitze bei (L, 0), Vorderrand oben (−y).
    Vorderflügel: länger, mit Zellen; Hinterflügel: kleiner, Haken (Hamuli) am Vorderrand."""
    top, bot = -w * .42, w * .58
    umriss = (f"M0,0 C{L * .12:.1f},{top * .9:.1f} {L * .5:.1f},{top * 1.15:.1f} {L:.1f},{-w * .05:.1f} "
              f"C{L * .95:.1f},{bot * .7:.1f} {L * .55:.1f},{bot * 1.15:.1f} {L * .22:.1f},{bot * .55:.1f} C{L * .1:.1f},{bot * .3:.1f} {L * .03:.1f},{bot * .08:.1f} 0,0 Z")
    v = "#6e8798"
    adern = (f"<path d='M2,-1 C{L * .25:.1f},{top * .95:.1f} {L * .6:.1f},{top * .95:.1f} {L * .97:.1f},{-w * .04:.1f}' fill='none' stroke='#5b4a3c' stroke-width='1.6' stroke-linecap='round'/>")
    if typ == "vor":
        adern += (f"<path d='M2,1 C{L * .3:.1f},{w * .02:.1f} {L * .65:.1f},{-w * .1:.1f} {L * .93:.1f},{-w * .05:.1f} "
                  f"M2,2 C{L * .25:.1f},{w * .22:.1f} {L * .55:.1f},{w * .3:.1f} {L * .8:.1f},{w * .28:.1f} "
                  f"M{L * .3:.1f},{w * .02:.1f} L{L * .36:.1f},{top * .8:.1f} M{L * .47:.1f},{-w * .03:.1f} L{L * .52:.1f},{top * .95:.1f} "
                  f"M{L * .6:.1f},{-w * .07:.1f} L{L * .66:.1f},{top * .85:.1f} M{L * .5:.1f},{w * .28:.1f} L{L * .5:.1f},{w * .04:.1f} "
                  f"M{L * .64:.1f},{w * .3:.1f} L{L * .66:.1f},{-w * .05:.1f}' fill='none' stroke='{v}' stroke-width='.9' stroke-linecap='round'/>")
    else:
        adern += (f"<path d='M2,1 C{L * .3:.1f},{w * .03:.1f} {L * .6:.1f},{-w * .05:.1f} {L * .88:.1f},{-w * .04:.1f} "
                  f"M{L * .4:.1f},{w * .01:.1f} L{L * .44:.1f},{w * .3:.1f} M{L * .62:.1f},{-w * .03:.1f} L{L * .66:.1f},{w * .25:.1f}' "
                  f"fill='none' stroke='{v}' stroke-width='.9' stroke-linecap='round'/>")
        haken = "".join(f"<circle cx='{L * (.42 + i * .045):.1f}' cy='{top * .92 + i * .1:.1f}' r='.9' fill='#5b4a3c'/>" for i in range(7))
        adern += haken
    o = f" opacity='{opa}'" if opa < 1 else ""
    return (f"<g{o}><path d='{umriss}' fill='url(#bFluegel)' stroke='#7f9bb0' stroke-width='1.1' stroke-linejoin='round'/>{adern}"
            f"<path d='M{L * .18:.1f},{top * .55:.1f} C{L * .4:.1f},{top * .8:.1f} {L * .6:.1f},{top * .8:.1f} {L * .8:.1f},{top * .3:.1f}' fill='none' stroke='#fff' stroke-width='2' opacity='.55' stroke-linecap='round'/></g>")


def fluegel_platz(x, y, winkel, L, w, typ="vor", opa=1.0, spiegeln=False):
    """Flügel an Position (x,y) mit Richtung `winkel` (Grad, SVG: im Uhrzeigersinn, 0 = nach rechts)."""
    sy = -1 if spiegeln else 1
    return f"<g transform='translate({x:.1f} {y:.1f}) rotate({winkel:.1f}) scale(1 {sy})'>{fluegel(L, w, typ, opa)}</g>"


# ═══════════════════════════════════════════════════════════════════════════
#  Beine
# ═══════════════════════════════════════════════════════════════════════════
def _streck(punkte, dicken, farbe, w_extra=0):
    out = ""
    for (x0, y0), (x1, y1), dk in zip(punkte, punkte[1:], dicken):
        out += f"<line x1='{x0:.1f}' y1='{y0:.1f}' x2='{x1:.1f}' y2='{y1:.1f}' stroke='{farbe}' stroke-width='{dk + w_extra:.1f}' stroke-linecap='round'/>"
    return out


def bein(punkte, dicken, farbe="#3b2a1c", glanz="#8a6a4d", rand="#150d06", haarfarbe=HELLGOLD, haare_n=14, seed=5, klaue=True, opa=1.0):
    """Insektenbein aus Gelenkpunkten: Umriss, Füllung, Glanzlicht, Haare, Klauen am Ende."""
    out = _streck(punkte, dicken, rand, 2.2) + _streck(punkte, dicken, farbe)
    out += _streck([(x - .6, y - .6) for x, y in punkte], [max(d * .28, .9) for d in dicken], glanz)
    rng = random.Random(seed)
    d = []
    for (x0, y0), (x1, y1), dk in list(zip(punkte, punkte[1:], dicken))[:2]:
        for i in range(haare_n // 2):
            f = rng.random()
            px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            nx, ny = _nrm(-(y1 - y0), x1 - x0)
            s = 1 if rng.random() < .5 else -1
            L = 3 + rng.random() * 4
            d.append(f"M{px + nx * s * dk / 2:.1f},{py + ny * s * dk / 2:.1f}l{(nx * s * .6 - .8) * L:.1f},{(ny * s * .6 + .3) * L:.1f}")
    if d:
        out += f"<path d='{''.join(d)}' fill='none' stroke='{haarfarbe}' stroke-width='.9' stroke-linecap='round'/>"
    if klaue:
        (xa, ya), (xb, yb) = punkte[-2], punkte[-1]
        dx, dy = _nrm(xb - xa, yb - ya)
        nx, ny = -dy, dx
        out += (f"<path d='M{xb:.1f},{yb:.1f} q{dx * 3 + nx * 2:.1f},{dy * 3 + ny * 2:.1f} {dx * 3.5 + nx * 5:.1f},{dy * 3.5 + ny * 5:.1f} "
                f"M{xb:.1f},{yb:.1f} q{dx * 3 - nx * 2:.1f},{dy * 3 - ny * 2:.1f} {dx * 3.5 - nx * 5:.1f},{dy * 3.5 - ny * 5:.1f}' "
                f"fill='none' stroke='{rand}' stroke-width='1.3' stroke-linecap='round'/>")
    o = f" opacity='{opa}'" if opa < 1 else ""
    return f"<g{o}>{out}</g>"


# ═══════════════════════════════════════════════════════════════════════════
#  Biene von der Seite (lokale Koordinaten, Blick nach rechts)
# ═══════════════════════════════════════════════════════════════════════════
BEINE_NAH = {
    "vorn": ([(32, 24), (52, 46), (58, 70), (70, 86), (79, 92)], [12.5, 9.5, 6.4, 4.2]),
    "mitte": ([(8, 32), (18, 56), (10, 80), (2, 96), (-1, 103)], [12.5, 10, 6.4, 4.2]),
    "hinten": ([(-22, 28), (-46, 52), (-58, 86), (-76, 104), (-92, 107)], [14.5, 12, 8, 4.8]),
}


def abdomen(streifen=True):
    """Hinterleib mit Streifen, Volumen und Härchen. Rückgabe: SVG-Gruppe (lokal)."""
    cid = neue_id("hl")
    gold, dunk = "#e9a924", "#33230f"
    # Trennlinien der Ringe (leicht nach hinten gewölbt)
    xs = [-36, -62, -88, -116, -146, -178]
    farben = [gold, dunk, gold, dunk, gold, dunk]
    baender = ""
    for i, c in enumerate(farben):
        xa = xs[i]
        xb = xs[i + 1] if i + 1 < len(xs) else -230
        baender += (f"<path d='M{xa},-70 Q{xa - 12},0 {xa},80 L{xb},80 Q{xb - 12},0 {xb},-70 Z' fill='{c}'/>")
    out = f"<clipPath id='{cid}'><path d='{HL_D}'/></clipPath>"
    out += f"<g clip-path='url(#{cid})'><g filter='url(#bWeich2)'>{baender}</g>"
    # goldene Haarsäume an den Ringkanten
    for i in range(1, len(xs)):
        xa = xs[i]
        out += haare_linie(xa, -52, xa - 11, 56, 16, 8, "#f4cf64" if farben[i] == dunk else "#fbe08a", .9, seed=40 + i, opa=.85)
    out += flaum(-90, 0, 100, 40, 70, 6, "#fff0a8", .8, seed=9, opa=.45)
    out += f"<path d='{HL_D}' fill='url(#bVol)'/></g>"
    out += f"<path d='{HL_D}' fill='none' stroke='#4a2f10' stroke-width='1.4'/>"
    out += haare_kurve(HL_SEG_OBEN + HL_SEG_UNTEN, 70, 7, "#f6d672", .9, seed=12, aussen=.85, richtung=(-1, .2))
    return out


def stachel_klein(x=-212, y=16):
    return (f"<path d='M{x},{y} l-6,3 l-8,7 l9,-1 z' fill='#2a1a0a' stroke='#150d06' stroke-width='.8' stroke-linejoin='round'/>")


def kopf_seite(ruessel="kurz", fuehler=True, seed=21):
    """Kopf von der Seite (lokal), inkl. Auge, Rüssel, Fühler."""
    out = ""
    # Rüssel (hinter dem Kopf gezeichnet)
    if ruessel == "kurz":
        out += ("<path d='M97,33 C100,46 92,56 80,62' fill='none' stroke='#2a1a0c' stroke-width='5.6' stroke-linecap='round'/>"
                "<path d='M97,33 C100,46 92,56 80,62' fill='none' stroke='#a8703a' stroke-width='3.4' stroke-linecap='round'/>"
                "<path d='M96,34 C99,45 92,54 81,60' fill='none' stroke='#e2b878' stroke-width='1' stroke-linecap='round'/>")
    elif ruessel == "lang":
        out += ("<path d='M98,32 C112,44 130,50 150,48' fill='none' stroke='#2a1a0c' stroke-width='6.4' stroke-linecap='round'/>"
                "<path d='M98,32 C112,44 130,50 150,48' fill='none' stroke='#8a5a2a' stroke-width='4.2' stroke-linecap='round'/>"
                "<path d='M98,31 C112,43 130,49 149,47' fill='none' stroke='#d8a864' stroke-width='1.2' stroke-linecap='round'/>"
                "<ellipse cx='154' cy='48' rx='5.5' ry='3' fill='#c58a45' stroke='#2a1a0c' stroke-width='1'/>")
    if fuehler:
        out += ("<path d='M101,-6 C112,-20 126,-27 142,-28 C158,-28 172,-18 180,-2' fill='none' stroke='#150d06' stroke-width='4' stroke-linecap='round' opacity='.85'/>"
                "<path d='M101,-6 C112,-20 126,-27 142,-28 C158,-28 172,-18 180,-2' fill='none' stroke='#4a3426' stroke-width='2.4' stroke-linecap='round' opacity='.85'/>")
    # Kopfkapsel
    out += f"<path d='{KOPF_D}' fill='url(#bKopf)' stroke='#150d06' stroke-width='1.4'/>"
    out += f"<path d='{KOPF_D}' fill='url(#bVol)' opacity='.8'/>"
    # Kiefer
    out += "<path d='M98,28 q9,2 9,10 q-6,-1 -11,-4 z' fill='#5a3a1c' stroke='#150d06' stroke-width='.9' stroke-linejoin='round'/>"
    # Gesichts-Haare
    out += haare(76, 6, 29, 38, 30, 8, "#d9b45e", 1.0, a0=100, a1=290, richtung=(-1, .15), aussen=.6, seed=seed)
    out += flaum(98, 24, 8, 14, 16, 5, "#e9c56e", .9, seed=seed + 8, richtung=(.3, 1), opa=.85)
    out += flaum(90, 26, 16, 14, 34, 7, "#dcb862", 1.2, seed=seed + 12, richtung=(-.4, .7), opa=.9)
    out += flaum(64, 18, 12, 22, 28, 7, "#c99b46", 1.2, seed=seed + 13, richtung=(-1, .2), opa=.8)
    # Facettenauge
    out += ("<g transform='translate(85 -4) rotate(8)'>"
            "<ellipse rx='15.5' ry='22' fill='url(#bAuge)' stroke='#0c0602' stroke-width='1'/>"
            "<ellipse rx='15.5' ry='22' fill='url(#bHex)'/>"
            "<ellipse cx='-5' cy='-9' rx='4.5' ry='8' fill='url(#bGlanz)' transform='rotate(18 -5 -9)'/></g>")
        # Haare oben auf dem Kopf
    out += haare(78, -26, 24, 13, 26, 9, "#eec253", 1.1, a0=190, a1=350, richtung=(-1, -.1), aussen=.9, seed=seed + 5)
    if fuehler:
        out += ("<path d='M96,-10 C102,-26 112,-36 122,-40' fill='none' stroke='#150d06' stroke-width='5.4' stroke-linecap='round'/>"
                "<path d='M96,-10 C102,-26 112,-36 122,-40' fill='none' stroke='#4a3426' stroke-width='3.4' stroke-linecap='round'/>"
                "<path d='M122,-40 C140,-46 160,-38 172,-20' fill='none' stroke='#150d06' stroke-width='4.2' stroke-linecap='round'/>"
                "<path d='M122,-40 C140,-46 160,-38 172,-20' fill='none' stroke='#5a4030' stroke-width='2.6' stroke-linecap='round'/>"
                "<path d='M126,-42 C142,-47 160,-39 172,-20' fill='none' stroke='#c9a67c' stroke-width='2.8' stroke-dasharray='.9 4.4' stroke-linecap='butt'/>"
                "<circle cx='96' cy='-10' r='3.4' fill='#3b2a1c' stroke='#150d06' stroke-width='1'/>")
    return out


def brust_pelz(seed=3):
    """Brust der Biene von der Seite als flauschige Kugel (Unterfell, Pelz, Licht)."""
    p = []
    cx, cy, rx, ry = BRUST_E
    p.append(haare(cx, cy, rx, ry, 60, 8, "#7a4a14", 1.6, seed=seed + 20, aussen=.9, einwaerts=1))
    p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='url(#bBrust)' filter='url(#bFuzz)'/>")
    p.append(flaum(cx, cy + 2, rx - 2, ry - 3, 70, 8, "#6b3f10", 1.3, seed=seed + 2, opa=.45))
    p.append(flaum(cx, cy - 4, rx - 3, ry - 5, 120, 8, "#f6cf62", 1.2, seed=seed + 1, opa=.75))
    p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='url(#bVol)' opacity='.5'/>")
    p.append(haare(cx, cy, rx, ry, 120, 12, "#f4c94f", 1.3, seed=seed, aussen=.85))
    p.append(haare(cx, cy, rx, ry, 40, 12, "#fff0ad", 1.1, seed=seed + 9, a0=190, a1=340, aussen=.9))
    return "".join(p)


def biene_seite(tint=None, fluegel_an=True, ruessel="kurz", beine_an=True, stachel=True, seed=3, fluegelwinkel=0,
                hinterbein_pollen=False):
    """Komplette Biene von der Seite (lokale Koordinaten: Brustmitte = 0,0; Blick nach rechts; Länge etwa −220 … +175).

    `tint` = None oder {"kopf": farbe, "brust": farbe, "hinterleib": farbe} → farbig abgesetzte Abschnitte (Schein + Deckschicht).
    `fluegelwinkel` verstellt beide Flügelpaare (Grad; positiv = weiter nach oben)."""
    p = []
    if tint:
        p.append(_tint_aura(tint))
    # ferne Flügel (hinter dem Körper, blasser)
    if fluegel_an:
        p.append(fluegel_platz(-2, -36, 206 - fluegelwinkel, 168, 46, "vor", .5))
        p.append(fluegel_platz(0, -36, 222 - fluegelwinkel, 112, 34, "hinter", .5))
    # ferne Beine
    if beine_an:
        for k, (pts, dk) in BEINE_NAH.items():
            ver = [(x + 8, y - 3) for x, y in pts]
            p.append(bein(ver, [d * .88 for d in dk], farbe="#2a1e14", glanz="#5a4332", haare_n=0, seed=11, opa=.92))
    # Hinterleib
    p.append(abdomen())
    if stachel:
        p.append(stachel_klein())
    # nahe Beine (vor der Brust gezeichnet: die Brust verdeckt die Ansätze)
    if beine_an:
        for k, (pts, dk) in BEINE_NAH.items():
            p.append(bein(pts, dk, seed=hash(k) % 50, haare_n=10))
        if hinterbein_pollen:
            p.append("<g><ellipse cx='-56' cy='72' rx='11' ry='17' fill='url(#bPollen)' stroke='#a8650a' stroke-width='1.2' transform='rotate(10 -56 72)'/>"
                     "<ellipse cx='-59' cy='66' rx='3.6' ry='6' fill='#fff7b0' opacity='.7' transform='rotate(10 -56 72)'/></g>")
    p.append(brust_pelz(seed))
    # Kopf
    p.append(kopf_seite(ruessel))
    # nahe Flügel
    if fluegel_an:
        p.append(fluegel_platz(-8, -38, 196 - fluegelwinkel, 184, 50, "vor", 1.0))
        p.append(fluegel_platz(-4, -38, 212 - fluegelwinkel, 122, 38, "hinter", 1.0))
    body = "".join(p)
    if tint:
        body += _tint_overlay(tint)
    return body


def _tint_aura(tint):
    """Farbiger Schein hinter jedem Körperteil (weich), damit die Abschnitte sich klar absetzen."""
    cx, cy, rx, ry = BRUST_E
    out = "<g filter='url(#bWeich2)' opacity='.9'>"
    if "kopf" in tint:
        out += f"<path d='{KOPF_D}' fill='{tint['kopf']}' stroke='{tint['kopf']}' stroke-width='15' stroke-linejoin='round'/>"
    if "brust" in tint:
        out += f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{tint['brust']}' stroke='{tint['brust']}' stroke-width='15'/>"
    if "hinterleib" in tint:
        out += f"<path d='{HL_D}' fill='{tint['hinterleib']}' stroke='{tint['hinterleib']}' stroke-width='15' stroke-linejoin='round'/>"
    return out + "</g>"


def _tint_overlay(tint):
    """Leichte Farbdecke über den Körperteilen (der Pelz bleibt sichtbar)."""
    cx, cy, rx, ry = BRUST_E
    out = ""
    if "kopf" in tint:
        out += f"<path d='{KOPF_D}' fill='{tint['kopf']}' fill-opacity='.16'/>"
    if "brust" in tint:
        out += f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{tint['brust']}' fill-opacity='.14'/>"
    if "hinterleib" in tint:
        out += f"<path d='{HL_D}' fill='{tint['hinterleib']}' fill-opacity='.14'/>"
    return out


SPRITES = {}   # id → Markup; wird als <g id=…> in die defs geschrieben, sobald ein <use> darauf zeigt


def sprite(sid, inhalt):
    SPRITES[sid] = inhalt
    return sid


def benutze(sid, x=0.0, y=0.0, s=1.0, rot=0, spiegeln=False):
    """<use> auf ein Sprite (spart Dateigröße bei vielen gleichen Objekten)."""
    sx = -s if spiegeln else s
    r = f" rotate({rot})" if rot else ""
    return f"<use href='#{sid}' transform='translate({x:.1f} {y:.1f}){r} scale({sx:.3f} {s:.3f})'/>"


sprite("bk", (
    "<g filter='url(#fSchatten)'>"
    "<g opacity='.85'><ellipse cx='-8' cy='-13' rx='15' ry='6' transform='rotate(-52 -8 -13)' fill='url(#bFluegel)' stroke='#8fb0c6' stroke-width='.7'/>"
    "<ellipse cx='-2' cy='-13' rx='10' ry='4.3' transform='rotate(-30 -2 -13)' fill='url(#bFluegel)' stroke='#8fb0c6' stroke-width='.7'/></g>"
    "<path d='M-6,-1 C-8,-9 -28,-10 -36,-2 C-39,2 -40,4 -42,7 C-36,11 -22,12 -10,8 C-7,6 -6,3 -6,-1Z' fill='#e6a622'/>"
    "<clipPath id='bkc'><path d='M-6,-1 C-8,-9 -28,-10 -36,-2 C-39,2 -40,4 -42,7 C-36,11 -22,12 -10,8 C-7,6 -6,3 -6,-1Z'/></clipPath>"
    "<g clip-path='url(#bkc)'>"
    "<path d='M-14,-14 Q-18,0 -14,14 L-20,14 Q-24,0 -20,-14Z M-28,-14 Q-32,0 -28,14 L-35,14 Q-39,0 -35,-14Z' fill='#2f2013'/>"
    "<rect x='-45' y='-14' width='45' height='28' fill='url(#bVol)'/></g>"
    "<path d='M-42,7 l-4,2 l3,-4z' fill='#2a1a0a'/>"
    "<ellipse cx='2' cy='-1' rx='9.5' ry='9' fill='url(#bBrust)'/>"
    "<path d='M-5,-6 q4,-5 10,-4 M-6,-1 q5,-4 11,-3' stroke='#f6d673' stroke-width='1.2' fill='none' stroke-linecap='round' opacity='.8'/>"
    "<ellipse cx='2' cy='-1' rx='9.5' ry='9' fill='url(#bVol)' opacity='.55'/>"
    "<ellipse cx='15' cy='1' rx='6.8' ry='7' fill='url(#bKopf)'/>"
    "<ellipse cx='16.5' cy='-.5' rx='3.6' ry='5' fill='url(#bAuge)'/>"
    "<ellipse cx='15.6' cy='-2.4' rx='1.1' ry='1.8' fill='#fff' opacity='.7'/>"
    "<path d='M20,-4 q4,-4 8,-3' stroke='#2a1a0a' stroke-width='1' fill='none' stroke-linecap='round'/>"
    "<path d='M21,5 q3,2 3,5' stroke='#7a4a1e' stroke-width='1.6' fill='none' stroke-linecap='round'/>"
    "<path d='M5,7 l-3,7 M9,7 l1,8 M0,7 l-6,6' stroke='#2a1a0a' stroke-width='1.3' stroke-linecap='round' fill='none'/>"
    "<g opacity='.92'><ellipse cx='-3' cy='-12' rx='14' ry='5.4' transform='rotate(-40 -3 -12)' fill='url(#bFluegel)' stroke='#8fb0c6' stroke-width='.7'/></g>"
    "</g>"))


def biene_klein(x, y, s=1.0, drehung=0, fluegel_winkel=0, zeige_streifen=True, glanz=True):
    """Kleine Biene im Flug (Symbol, Blick nach rechts, Länge ≈ 40·s): Kopf, Brust, gestreifter Hinterleib, 2 Flügelpaare."""
    return benutze("bk", x, y, s, drehung)


# ═══════════════════════════════════════════════════════════════════════════
#  Beschriftung mit Pfeil
# ═══════════════════════════════════════════════════════════════════════════
def beschriftung(x, y, text, zx, zy, farbe=DUNKEL, ueber=True, anker="middle", size=13, w=2.4, lfill=None, punkt=True):
    """Beschriftung mit Pfeil: Der Pfeil beginnt bei (x, y) und endet im Ziel (zx, zy). Der Text steht ÜBER (ueber=True)
    oder UNTER dem Pfeilanfang (≥ 10 px Abstand zur Linie), nie auf der Linie; weißer Halo (svg_helfer.t)."""
    ty = y - 10 if ueber else y + size + 8
    out = pfeil(x, y, zx, zy, farbe, w)
    out += t(x, ty, text, size, 800, lfill or farbe, anker)
    return out


def punkt_marke(x, y, farbe="#fff", r=3):
    return f"<circle cx='{x}' cy='{y}' r='{r}' fill='{farbe}' stroke='#14304a' stroke-width='1'/>"


def platz(inhalt, x, y, s=1.0, rot=0, spiegeln=False):
    """Gruppe verschieben/skalieren/drehen (Mittelpunkt = lokaler Ursprung)."""
    sx = -s if spiegeln else s
    return f"<g transform='translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {s:.3f})'>{inhalt}</g>"


def komprimiere(text):
    """Entfernt überflüssige Nachkommastellen (z. B. 12.0 -> 12) und spart etwa 5 % Dateigröße."""
    import re
    return re.sub(r"(?<=\d)\.0(?!\d)", "", text)


DEFS_EXTRA = []   # weitere Module (bienen_kopf, bienen_innen, szenen_zeichnen) tragen hier ihre Verläufe ein


def aufraeumen(text):
    """Entfernt nicht benutzte Verläufe, Filter, Muster, Beschneidungen und Pfeilspitzen aus den defs (kleinere Dateien)."""
    import re
    while True:
        entfernt = False
        for tag, i in re.findall(r"<(linearGradient|radialGradient|filter|pattern|clipPath|marker) id='([^']+)'", text):
            if not re.search(r"#%s[)']" % re.escape(i), text):
                text = re.sub(r"<%s id='%s'.*?</%s>" % (tag, re.escape(i), tag), "", text, count=1, flags=re.S)
                entfernt = True
        if not entfernt:
            return text


def bild(titel, *teile, w=W, h=H, defs_extra="", **kw):
    """svg() mit den Bienen-Defs, Sprites und komprimierter Ausgabe (einheitlicher Einstieg für alle Grafiken dieser Dateien)."""
    import re
    koerper = "".join(str(t) for t in teile)
    benutzt = set(re.findall(r"href='#([A-Za-z0-9_]+)'", koerper))
    spr, neu = "", set(benutzt)
    while neu:
        gerade, neu = neu, set()
        for sid in gerade:
            if sid in SPRITES:
                spr += f"<g id='{sid}'>{SPRITES[sid]}</g>"
                for t2 in re.findall(r"href='#([A-Za-z0-9_]+)'", SPRITES[sid]):
                    if t2 not in benutzt:
                        benutzt.add(t2)
                        neu.add(t2)
    text = svg(titel, *teile, w=w, h=h, defs_extra=DEFS_BIENE + "".join(DEFS_EXTRA) + spr + defs_extra, **kw)
    return komprimiere(aufraeumen(text))


# ═══ gemeinsame Hilfen für die Schaubild-Dateien ═══
TEXT_ = TEXT


def hintergrund_blueten(h=288):
    """Weicher Hintergrund: Wiese verschwimmt, helle Lichtflecken (Bokeh)."""
    flecken = "".join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{c}' opacity='{o}'/>" for x, y, r, c, o in [
        (60, 60, 38, "#fff6c2", .55), (420, 40, 46, "#e9f7c9", .6), (350, 250, 40, "#fff0b0", .5), (40, 230, 34, "#d8efb0", .55),
        (440, 160, 28, "#ffe9a0", .45), (150, 20, 24, "#ffffff", .6)])
    return f"<g filter='url(#bWeich)'>{flecken}</g>"


def klammer_unten(x0, x1, y, farbe=TEXT, h=7):
    """Geschweifte Klammer unter einer Gruppe (Spitze nach unten)."""
    m = (x0 + x1) / 2
    return (f"<path d='M{x0},{y} q0,{h} {h},{h} H{m - h} q{h},0 {h},{h} q0,-{h} {h},-{h} H{x1 - h} q{h},0 {h},-{h}' "
            f"fill='none' stroke='{farbe}' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/>")


def tangenten(c1, r1, c2, r2):
    """Äußere Tangenten zweier Kreise (für den Lupenkegel): Liste von zwei Strecken ((x1,y1),(x2,y2))."""
    (x1, y1), (x2, y2) = c1, c2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    b = math.acos((r1 - r2) / d)
    res = []
    for s in (1, -1):
        th = a + s * b
        res.append(((x1 + r1 * math.cos(th), y1 + r1 * math.sin(th)), (x2 + r2 * math.cos(th), y2 + r2 * math.sin(th))))
    return res


def pollenstaub(n=26, seed=4, bereich=(0, 0, 480, 288)):
    """Schwebende Pollenkörner (kleine gelbe Kugeln mit Glanz) als Hintergrund."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = bereich
    o = []
    for _ in range(n):
        x, y, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(2.2, 4.6)
        o.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.1f}' fill='url(#bHoeschen)' opacity='{rng.uniform(.55, .95):.2f}'/>")
    return "".join(o)


