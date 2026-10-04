"""Schaubilder des Reiters „Nutzen & Schutz“ (Lesestrecke L4 und Glossar), viewBox 480 × 288.

Aufruf:  python werkzeuge/grafiken_nutzen.py
Ausgabe: static/img/lese/nutzen-1.svg … nutzen-5.svg, glossar-bestaeubung.svg, glossar-varroamilbe.svg

  nutzen-1  Honigernte (Imker an der Schleuder, Rähmchen mit Honig, Honigglas)
  nutzen-2  Wachs (Biene mit Wachsplättchen, Wabenstück, Kerzen, Salbe)
  nutzen-3  Bestäubung (Blüte → Biene trägt Pollen → nächste Blüte → Apfel)
  nutzen-4  Imkerjahr (Jahreskreis mit Frühling, Sommer, Spätsommer, Winter)
  nutzen-5  Bienen in Gefahr (Blühwiese | kahle Fläche mit Pestizid, Lupe mit Varroa-Milbe)
  glossar-bestaeubung, glossar-varroamilbe

Die Bausteine (Biene, Milbe, Imker, Kasten, Rähmchen, Blüte …) liegen in nutzen_zeichnen.py. Beschriftung nur über
beschr()/etikett()/nummer(); feste Wörter laut AB_KONZEPT.md. Die Wörter im Bild müssen zu lesen_nutzen.py passen
(Schleuder, Rähmchen, Wachs, Wabe, Pollen, Zuckerlösung, Varroa-Milbe, Pestizid, Blühwiese).
Prüfen: python werkzeuge/grafik_uebersicht.py nutzen-   (und glossar-)
"""
import math
import random

from nutzen_zeichnen import *  # noqa: F401,F403  (Bausteine; reicht auch die nötigen Namen aus svg_helfer durch)
from svg_helfer import H, W, erzeuge, gras, himmel_wiese, nadelbaum, sonne, stein, t, tp, wolke


# ═══════════════════════════════════════════════════════════════════════════
#  nutzen-1  Honigernte: Rähmchen mit Honig, Schleuder, Honigglas
# ═══════════════════════════════════════════════════════════════════════════
def nutzen_1():
    p = []
    # Raum: Wand, Sockel, Dielenboden, Fenster
    p.append("<rect width='480' height='288' rx='14' fill='url(#gnWand)'/>")
    p.append("<rect x='0' y='226' width='480' height='62' fill='url(#gnBoden)'/>")
    p.append("<rect x='0' y='222' width='480' height='7' fill='#c18a4e' stroke='#8f5f2e' stroke-width='1'/>")
    for k, yy in enumerate((240, 256, 272)):
        p.append(f"<path d='M0,{yy} H480' stroke='#8a5a2a' stroke-width='1' opacity='.35'/>")
        for xx in range(30 + 40 * (k % 2), 480, 110):
            p.append(f"<path d='M{xx},{yy} V{yy + 16}' stroke='#8a5a2a' stroke-width='1' opacity='.3'/>")
    p.append("<g filter='url(#fSchatten)'><rect x='398' y='18' width='70' height='70' rx='3' fill='#e9f5ff' stroke='#fff' stroke-width='5'/></g>"
             "<rect x='402' y='26' width='62' height='62' fill='url(#gHimmel)'/>"
             "<circle cx='444' cy='44' r='9' fill='#ffd43b'/><path d='M410,76 q4,-9 12,-4 q6,-7 14,0 q8,-2 8,6 z' fill='#fff'/>"
             "<path d='M433,26 V88 M402,57 H464' stroke='#fff' stroke-width='3.5'/>")
    # Werkbank links mit Rähmchen
    p.append("<g filter='url(#fSchatten)'><rect x='6' y='212' width='128' height='10' rx='2' fill='url(#gnTisch)' stroke='#6b3f19' stroke-width='1.2'/>"
             "<rect x='14' y='222' width='8' height='48' fill='#9b6a37'/><rect x='118' y='222' width='8' height='48' fill='#9b6a37'/></g>")
    p.append(raehmchen(22, 124, 94, 88, r=5.4, bienen=3, seed=4))
    # Schleuder
    fuss, s_sch, sx, sy = 82, .8, 208, 272
    p.append(honigschleuder(sx, sy, s_sch, fuss))
    # Glas unter dem Hahn
    hx, hy = sx - 62 * s_sch, sy - (fuss - 10) * s_sch
    p.append(honigstrahl(hx, hy + 1, sy - 14, 4.6))
    p.append(honigglas(hx, sy, .92, fuell=.35, text="Honig", deckel=False))
    # Imker rechts, dreht die Kurbel mit der einen Hand
    knauf = (sx + 23 * s_sch, sy - (fuss + 84 + 24) * s_sch)
    ix, iy, isc = 346, 296, 1.42
    hand_l = ((knauf[0] - ix) / isc, (knauf[1] - iy) / isc)
    korper, arme = imker(ix, iy, isc, haende=(hand_l, (42, -30)))
    p.append(korper + arme)
    # volles Glas rechts (Deckel drauf)
    p.append(honigglas(452, 274, 1.1, fuell=.9, text="Honig"))
    # Beschriftungen
    p.append(beschr(62, 106, "Rähmchen", ziel=(50, 128), size=13))
    p.append(beschr(164, 100, "Schleuder", ziel=(180, 150), size=13, von=(170, 106)))
    p.append(beschr(452, 196, "Honig", ziel=(452, 236), size=13))
    return szene("Honigernte: Imker an der Schleuder, daneben ein Rähmchen mit Honig und volle Honiggläser", *p,
                 defs=wabenmuster("pnDeckel", "deckel", 5.4) + wabenmuster("pnHonig", "honig", 5.4), grund="url(#gnWand)")


# ═══════════════════════════════════════════════════════════════════════════
#  nutzen-2  Wachs: Biene mit Wachsplättchen, Wabenstück, Kerzen, Salbe auf dem Holztisch
# ═══════════════════════════════════════════════════════════════════════════
def nutzen_2():
    p = []
    p.append("<rect width='480' height='288' rx='14' fill='url(#gnWand)'/>")
    # Fenster
    p.append("<g filter='url(#fSchatten)'><rect x='392' y='22' width='70' height='70' rx='3' fill='#e9f5ff' stroke='#fff' stroke-width='5'/></g>"
             "<rect x='396' y='26' width='62' height='62' fill='url(#gHimmel)'/><circle cx='438' cy='44' r='9' fill='#ffd43b'/>"
             "<path d='M404,76 q4,-9 12,-4 q6,-7 14,0 q8,-2 8,6 z' fill='#fff'/><path d='M427,26 V88 M396,57 H458' stroke='#fff' stroke-width='3.5'/>")
    # Holztisch (Tischplatte von vorn)
    p.append("<path d='M0,206 H480 V288 H0 Z' fill='url(#gnTisch)'/><path d='M0,206 H480' stroke='#e7c18d' stroke-width='3'/>"
             "<path d='M0,209 H480' stroke='#6b3f19' stroke-width='1' opacity='.5'/>")
    p.append(holzmaserung(0, 212, 480, 76, n=8, seed=5))
    # Biene mit Wachsplättchen am Hinterleib
    bx, by, bs, br = 108, 118, 1.8, -5
    p.append(biene(bx, by, bs, br, False, wachs=True, schatten=True))
    pl1 = lokal(bx, by, bs, br, False, -31, 17)
    p.append(beschr(70, 186, "Wachsplättchen", ziel=(pl1[0] - 4, pl1[1] + 9), size=13, von=(pl1[0] - 8, 171)))
    # Wabenstück
    p.append("<ellipse cx='222' cy='238' rx='60' ry='7' fill='#000' opacity='.18'/>")
    p.append(wabenstueck(178, 128, 88, 108))
    p.append(beschr(222, 270, "Wabe", size=13))
    # Kerzen
    for (cx, h, art, fl, sp) in ((312, 94, "gelb", False, False), (342, 118, "hell", True, False), (372, 82, "dunkel", False, True)):
        p.append("<ellipse cx='%d' cy='240' rx='15' ry='4' fill='#000' opacity='.2'/>" % cx)
        p.append(kerze(cx, 238, h, 18, art, fl, sp))
    p.append(beschr(342, 270, "Kerzen", size=13))
    # Salbe
    p.append("<ellipse cx='432' cy='248' rx='26' ry='5' fill='#000' opacity='.18'/>")
    p.append(dose(432, 246, 1.15))
    p.append(beschr(432, 270, "Salbe", size=13))
    return szene("Wachs: Biene mit Wachsplättchen am Hinterleib, Wabenstück, Kerzen und Salbe auf einem Holztisch", *p,
                 defs=wabenmuster("pnLeer", "leer", 8) + MUSTER_SPIRALE, grund="url(#gnWand)")


def ast(d, w=9, farbe="#6b4423", licht="#a5703c"):
    """Ast als dicker Pfad mit hellerem Streifen oben."""
    return (f"<path d='{d}' fill='none' stroke='{farbe}' stroke-width='{w}' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='{d}' fill='none' stroke='{licht}' stroke-width='{max(1.5, w * .3):.1f}' stroke-linecap='round' transform='translate(0 -{w * .22:.1f})' opacity='.7'/>")


def huegel(y, farbe=("#b9df8c", "#86bb55"), h=H, w=W, seed=1):
    rnd = random.Random(seed)
    pts = f"M0,{y + rnd.randint(0, 10)}"
    for i in range(1, 5):
        pts += f" Q{w * (i - .5) / 4:.0f},{y - rnd.randint(8, 22)} {w * i / 4:.0f},{y + rnd.randint(-6, 8)}"
    return (f"<path d='{pts} V{h} H0 Z' fill='url(#gnHuegel)' stroke='#6ba340' stroke-width='1'/>")


# ═══════════════════════════════════════════════════════════════════════════
#  nutzen-3  Bestäubung: Blüte → Biene → Frucht
# ═══════════════════════════════════════════════════════════════════════════
def nutzen_3():
    p = [wolke(60, 40, .8), wolke(400, 52, .7), huegel(236)]
    # Ast mit Zweigen
    p.append(ast("M-12,200 C60,196 120,176 200,164 C280,152 340,134 492,126", 10))
    p.append(ast("M232,158 C240,146 250,138 262,132", 4))
    p.append(ast("M70,190 C76,184 80,180 86,178", 4))
    p.append(ast("M398,128 C400,134 401,138 403,142", 3, "#6b4423", "#6b4423"))
    # Blätter
    for (x, y, l, r, d) in ((128, 178, 34, 200, False), (150, 170, 30, -30, True), (190, 168, 32, 195, False), (318, 140, 32, 210, False),
                            (345, 134, 30, -25, True), (372, 128, 28, 200, False), (428, 128, 30, -20, False), (22, 198, 28, 195, True),
                            (222, 156, 26, -40, True), (300, 146, 26, 15, False)):
        p.append(blatt(x, y, l, r, d))
    # Blüte A (mit Biene) und Blüte B
    p.append(apfelbluete(84, 160, 48, 8))
    p.append(apfelbluete(262, 112, 36, 30))
    # Apfel am Zweig
    p.append(apfel(404, 172, 27))
    # Biene an Blüte A: sammelt Pollen
    ba = (80, 130, 1.0, 16)
    p.append(biene(*ba, False, pollen_beine=True, pollen_haare=True, schatten=True))
    # Flugweg A -> B mit fliegender Biene
    p.append(bogen("M126,104 C150,50 205,46 236,84", "#475569", 2.6, "7 5"))
    p.append(biene(182, 54, .62, -8, False, pollen_beine=True, pollen_haare=True, schatten=True))
    p.append(pollenpunkte([(236, 96), (241, 100), (246, 94), (249, 102)], 1.8))
    # Pfeil B -> Apfel
    p.append(bogen("M298,134 C326,160 350,168 366,172", "#475569", 2.6))
    p.append(t(330, 190, "später", 12, 800, "#475569"))
    # Beschriftung
    pb = lokal(ba[0], ba[1], ba[2], ba[3], False, 1, -10)
    p.append(beschr(40, 64, "Pollen", ziel=(pb[0], pb[1]), size=13, von=(48, 70)))
    # Reihenfolge
    for (x, n, txt) in ((86, 1, "Pollen holen"), (250, 2, "Pollen weitertragen"), (412, 3, "Apfel wächst")):
        b = len(txt) * 6.6 + 44
        p.append(f"<rect x='{x - b / 2:.1f}' y='252' width='{b:.1f}' height='26' rx='13' fill='#fff' opacity='.95' stroke='#334155' stroke-width='1.4' filter='url(#fSchatten)'/>"
                 + nummer(x - b / 2 + 14, 265, n, 9.5)
                 + tp(x + 12, 269.5, txt, 12, 800, TEXT))
    return szene("Bestäubung: Biene holt Pollen an einer Apfelblüte, fliegt zur nächsten Blüte und daraus wächst ein Apfel", *p,
                 defs="<linearGradient id='gnHuegel' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b9df8c'/><stop offset='1' stop-color='#7db04a'/></linearGradient>")


# ═══════════════════════════════════════════════════════════════════════════
#  nutzen-4  Imkerjahr: vier Jahreszeiten-Bilder um einen Kreis
# ═══════════════════════════════════════════════════════════════════════════
TW, TH, SH = 231, 135, 103          # Kachel 231 × 135, Bildfläche darin 103 hoch (Rest = Kopf-/Fußzeile)
KACHEL = {"fruehling": (5, 5), "sommer": (244, 5), "herbst": (244, 148), "winter": (5, 148)}
JZ_FARBE = {"fruehling": "#2e8b3d", "sommer": "#d98a00", "herbst": "#b8501a", "winter": "#2b6cb0"}

DEFS_JZ = (
    "<linearGradient id='gnSkyFr' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#a9d8f5'/><stop offset='1' stop-color='#eaf8ff'/></linearGradient>"
    "<linearGradient id='gnSkySo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#79c6f2'/><stop offset='1' stop-color='#e2f5ff'/></linearGradient>"
    "<linearGradient id='gnSkyHe' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#f4c98c'/><stop offset='1' stop-color='#fdf0d6'/></linearGradient>"
    "<linearGradient id='gnSkyWi' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b7c9dd'/><stop offset='1' stop-color='#eef3f8'/></linearGradient>"
    "<linearGradient id='gnGrFr' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b3e07f'/><stop offset='1' stop-color='#7cc04a'/></linearGradient>"
    "<linearGradient id='gnGrSo' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#8fd055'/><stop offset='1' stop-color='#4f9a2e'/></linearGradient>"
    "<linearGradient id='gnGrHe' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d9bb55'/><stop offset='1' stop-color='#a9822c'/></linearGradient>"
    "<radialGradient id='gnKronePink' cx='.4' cy='.35' r='.8'><stop offset='0' stop-color='#ffffff'/><stop offset='.55' stop-color='#fbd0e1'/><stop offset='1' stop-color='#f09bbd'/></radialGradient>"
    + DEFS_TRAUBE)


def hang(y, breite=TW, hoch=SH, fill="url(#gnGrFr)", seed=1, amp=9):
    """Sanft geschwungene Hügelkante ab Höhe y, bis zum unteren Rand gefüllt."""
    rnd = random.Random(seed)
    d = f"M0,{y + rnd.randint(-3, 6)}"
    n = 4
    for i in range(1, n + 1):
        d += f" Q{breite * (i - .5) / n:.0f},{y - rnd.randint(amp // 2, amp)} {breite * i / n:.0f},{y + rnd.randint(-5, 6)}"
    return f"<path d='{d} V{hoch} H0 Z' fill='{fill}' stroke='#5b8a3a' stroke-width='.9'/>"


def krone(x, y, r, fill, n=5, seed=3):
    """Baumkrone aus überlappenden Kreisen."""
    rnd = random.Random(seed)
    o = f"<circle cx='{x}' cy='{y}' r='{r}' fill='{fill}'/>"
    for i in range(n):
        a = i * 2 * math.pi / n + rnd.uniform(-.3, .3)
        o += f"<circle cx='{f(x + math.cos(a) * r * .7)}' cy='{f(y + math.sin(a) * r * .55)}' r='{f(r * rnd.uniform(.5, .66))}' fill='{fill}'/>"
    return o


def baum_farbig(x, y, s, fill, seed=3, kahl=False):
    """Laubbaum mit frei wählbarer Kronenfüllung; `kahl` = Winterbaum mit Schnee auf den Ästen."""
    out = (f"<g filter='url(#fSchatten)'><path d='M{x - 4 * s},{y} Q{x - 3 * s},{y - 20 * s} {x - 2 * s},{y - 34 * s} H{x + 2 * s} Q{x + 3 * s},{y - 20 * s} {x + 4 * s},{y} Z' fill='url(#gStamm)'/>")
    if kahl:
        return (out + f"<path d='M{x},{y - 30 * s} q-{10 * s},-{12 * s} -{16 * s},-{26 * s} M{x},{y - 30 * s} q{9 * s},-{12 * s} {14 * s},-{28 * s} M{x},{y - 30 * s} V{y - 62 * s}' "
                f"stroke='#6b4423' stroke-width='{2.4 * s:.1f}' fill='none' stroke-linecap='round'/></g>")
    return out + krone(x, y - 48 * s, 22 * s, fill, 5, seed) + "</g>"


def kopfzeile(key, titel, text, oben=True):
    """Farbige Kopf-/Fußzeile der Kachel mit zwei Textzeilen (Jahreszeit fett, darunter die Arbeit)."""
    x0, y0 = KACHEL[key]
    farbe = JZ_FARBE[key]
    yy = y0 if oben else y0 + TH - 32
    return (f"<rect x='{x0}' y='{yy}' width='{TW}' height='32' fill='{farbe}'/>"
            f"<text x='{x0 + TW / 2}' y='{yy + 13}' font-size='13' font-weight='800' fill='#fff' text-anchor='middle'>{titel}</text>"
            f"<text x='{x0 + TW / 2}' y='{yy + 28}' font-size='10.5' font-weight='700' fill='#fff' text-anchor='middle'>{text}</text>")


def kachel_fruehling():
    p = ["<rect width='231' height='103' fill='url(#gnSkyFr)'/>", hang(56, fill="#c5e8a0", seed=2, amp=14), hang(66, fill="url(#gnGrFr)", seed=5)]
    p.append(baum_farbig(34, 86, 1.25, "url(#gnKronePink)", seed=4))
    for (x, y, r) in ((14, 40, 20), (52, 48, 25), (26, 58, -10), (62, 66, 40), (8, 70, 0), (72, 52, 10)):  # fallende Blütenblätter
        p.append(f"<ellipse cx='{x}' cy='{y}' rx='2.6' ry='1.6' fill='#f8b8d2' transform='rotate({r} {x} {y})'/>")
    p.append(kasten(130, 92, .92, 2, "gelb", bienen=4, seed=3))
    for (x, y, r, sp) in ((166, 52, -10, 0), (186, 66, 8, 1), (112, 40, -14, 1), (150, 34, 6, 0), (102, 58, 14, 1)):
        p.append(biene(x, y, .22, r, bool(sp), schatten=True))
    for (x, y, a, sc) in ((72, 94, "loewenzahn", 1), (86, 99, "loewenzahn", .9), (60, 100, "margerite", .9), (174, 100, "klee", .9), (104, 101, "margerite", .8)):
        p.append(wiesenblume(x, y, sc, a, 14))
    return "".join(p)


def kachel_sommer():
    p = ["<rect width='231' height='103' fill='url(#gnSkySo)'/>", sonne(204, 20, 12), wolke(120, 22, .5), hang(58, fill="#9fd66a", seed=7, amp=12),
         hang(68, fill="url(#gnGrSo)", seed=8)]
    p.append(kasten(84, 96, .95, 3, "blau", bienen=3, seed=5))
    for (x, y, r, sp) in ((124, 52, -8, 0), (52, 24, 10, 1), (132, 74, 4, 0)):
        p.append(biene(x, y, .22, r, bool(sp), schatten=True))
    korper, arme = imker(166, 114, .64, haende=((-40, -60), (40, -60)))
    p.append(korper)
    p.append(raehmchen(166 - 22, 114 - 60 * .64 - 3, 44, 32, r=3.4, bienen=0, mit_pattern=("pnDeckelK", "pnHonigK")))
    p.append(arme)
    p.append("<path d='M198,100 H228' stroke='#8a5a2a' stroke-width='3' stroke-linecap='round'/>")
    p.append(honigglas(214, 98, .62, text=""))
    for (x, y, a, sc) in ((48, 101, "mohn", 1), (128, 101, "margerite", .9), (140, 99, "kornblume", .9)):
        p.append(wiesenblume(x, y, sc, a, 13))
    return "".join(p)


def kachel_herbst():
    p = ["<rect width='231' height='103' fill='url(#gnSkyHe)'/>", hang(58, fill="#e1b45a", seed=11, amp=12), hang(68, fill="url(#gnGrHe)", seed=12)]
    p.append(baum_farbig(70, 84, .75, "url(#gnHerbst)", seed=6))
    p.append(baum_farbig(212, 86, .9, "url(#gnHerbst)", seed=8))
    rnd = random.Random(5)
    for _ in range(12):  # fallende Blätter
        x, y, r = rnd.uniform(46, 224), rnd.uniform(24, 98), rnd.uniform(0, 180)
        p.append(f"<ellipse cx='{x:.0f}' cy='{y:.0f}' rx='3' ry='1.7' fill='{rnd.choice(('#e07a1a', '#c9401a', '#f0b020'))}' transform='rotate({r:.0f} {x:.0f} {y:.0f})'/>")
    p.append(kasten(122, 96, .88, 2, "gruen", bienen=3, seed=9))
    p.append(eimer(122, 96 - 52 * .88 - 7, .9))
    for (x, y, r, sp) in ((154, 62, -8, 0), (92, 56, 10, 1)):
        p.append(biene(x, y, .2, r, bool(sp), schatten=True))
    korper, arme = imker(178, 116, .62, haende=((-32, -44), (36, -34)))
    p.append(korper + arme)
    p.append(flasche(178 - 32 * .62 - 1, 116 - 44 * .62 + 12, .8))
    p.append(kanne(40, 100, .85))
    return "".join(p)


def kachel_winter():
    p = ["<rect width='231' height='103' fill='url(#gnSkyWi)'/>", hang(52, fill="#dce7f1", seed=21, amp=10), hang(64, fill="url(#gnSchnee)", seed=22, amp=6)]
    p.append(nadelbaum(190, 82, .85).replace("#2f7d32", "#3d7a4a").replace("#357f38", "#46865a"))
    p.append(baum_farbig(24, 90, 1.1, "", seed=3, kahl=True))
    p.append("<ellipse cx='108' cy='98' rx='50' ry='5' fill='#9fb6cc' opacity='.45'/>")
    p.append(kasten_schnitt(108, 96, 1.1, 2, True, True, muster=("pnHonigW", "pnLeerW")))
    p.append(schneeflocken(231, 103, 26, 4))
    return "".join(p)


def jahreskreis_mitte():
    """Mitte: Scheibe mit vier farbigen Vierteln und Pfeilen im Uhrzeigersinn (Frühling → Sommer → Herbst → Winter)."""
    cx, cy = 240, 144
    o = [f"<circle cx='{cx}' cy='{cy}' r='34' fill='#fff' filter='url(#fSchatten)'/>"]
    for k, key in enumerate(("fruehling", "sommer", "herbst", "winter")):
        a1, a2 = math.radians(180 + 90 * k + 5), math.radians(270 + 90 * k - 5)
        r = 30
        o.append(f"<path d='M{f(cx + r * math.cos(a1))},{f(cy + r * math.sin(a1))} A{r},{r} 0 0 1 {f(cx + r * math.cos(a2))},{f(cy + r * math.sin(a2))}' "
                 f"stroke='{JZ_FARBE[key]}' stroke-width='4.4' fill='none' stroke-linecap='round'/>")
    o.append(biene(cx, cy - 10, .27, 0, False, fluegel=True))
    o.append(tp(cx, cy + 14, "Imkerjahr", 9.5, 800, "#334155"))
    R = 43
    for th in (-90, 0, 90, 180):
        a1, a2 = math.radians(th - 27), math.radians(th + 22)
        x1, y1, x2, y2 = cx + R * math.cos(a1), cy + R * math.sin(a1), cx + R * math.cos(a2), cy + R * math.sin(a2)
        d = f"M{f(x1)},{f(y1)} A{R},{R} 0 0 1 {f(x2)},{f(y2)}"
        o.append(f"<path d='{d}' stroke='#fff' stroke-width='7.5' fill='none' stroke-linecap='round'/>"
                 f"<path d='{d}' stroke='#475569' stroke-width='3.2' fill='none' stroke-linecap='round'/>")
        ta = a2 + math.pi / 2
        ex, ey = cx + R * math.cos(a2 + .06), cy + R * math.sin(a2 + .06)
        tx, ty = math.cos(ta), math.sin(ta)
        nx, ny = -ty, tx
        pts = [(ex + tx * 8, ey + ty * 8), (ex - tx * 2 + nx * 6.5, ey - ty * 2 + ny * 6.5), (ex - tx * 2 - nx * 6.5, ey - ty * 2 - ny * 6.5)]
        o.append("<polygon points='" + " ".join(f"{f(a)},{f(b)}" for a, b in pts) + "' fill='#475569' stroke='#fff' stroke-width='1.8' stroke-linejoin='round'/>")
    return "".join(o)


def nutzen_4():
    p = []
    clips = ""
    szenen = {"fruehling": kachel_fruehling, "sommer": kachel_sommer, "herbst": kachel_herbst, "winter": kachel_winter}
    texte = {"fruehling": ("Frühling", "Das Volk wächst"), "sommer": ("Sommer", "Der Imker erntet einen Teil des Honigs"),
             "herbst": ("Spätsommer", "Zuckerlösung füttern, Milben behandeln"), "winter": ("Winter", "Ruhe für die Wintertraube")}
    for key, fn in szenen.items():
        x0, y0 = KACHEL[key]
        clips += clip_rect(f"cnK{key}", x0, y0, TW, TH, 12)
        oben = key in ("fruehling", "sommer")
        inner = g(fn(), x0, y0 + (32 if oben else 0))
        titel, txt = texte[key]
        p.append(f"<g clip-path='url(#cnK{key})'>{inner}{kopfzeile(key, titel, txt, oben)}</g>"
                 f"<rect x='{x0}' y='{y0}' width='{TW}' height='{TH}' rx='12' fill='none' stroke='{JZ_FARBE[key]}' stroke-width='2.4'/>")
    p.append(jahreskreis_mitte())
    return szene("Imkerjahr als Jahreskreis: Frühling, das Volk wächst; Sommer, Honigernte; Spätsommer, Futter und Behandlung gegen Milben; Winter, die Wintertraube im verschneiten Kasten", *p,
                 defs=clips + DEFS_JZ + wabenmuster("pnDeckelK", "deckel", 3.4) + wabenmuster("pnHonigK", "honig", 3.4)
                 + wabenmuster("pnHonigW", "honig", 4.2) + wabenmuster("pnLeerW", "leer", 4.2), grund="#eef5fb")


# ═══════════════════════════════════════════════════════════════════════════
#  nutzen-5  Bienen in Gefahr: Blühwiese | kahle Fläche mit Pestizid-Traktor, Lupe mit Varroa-Milbe
# ═══════════════════════════════════════════════════════════════════════════
DEFS_GEFAHR = (
    "<linearGradient id='gnDunst' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#d3dce4' stop-opacity='0'/>"
    "<stop offset='.28' stop-color='#d3dce4' stop-opacity='.95'/><stop offset='1' stop-color='#e6ecf0'/></linearGradient>"
    "<linearGradient id='gnSoil' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#c9a070'/><stop offset='1' stop-color='#86603a'/></linearGradient>"
    "<radialGradient id='gnLupeBg' cx='.5' cy='.45' r='.7'><stop offset='0' stop-color='#fffdf3'/><stop offset='1' stop-color='#fdecc0'/></radialGradient>")


def nutzen_5():
    p = []
    # rechts trüber Himmel, Hügel
    p.append("<rect x='200' y='0' width='280' height='200' fill='url(#gnDunst)'/>")
    p.append("<path d='M0,176 Q60,146 140,166 Q200,176 252,188 V210 H0 Z' fill='#a9d27f' stroke='#6ba340' stroke-width='1'/>")
    p.append(himmel_wiese(184))
    # kahle Fläche (Erde, Furchen, Steine, trockene Büschel)
    p.append("<path d='M232,178 C250,198 234,216 258,234 C270,246 252,264 262,288 H480 V174 C400,166 300,168 232,178 Z' fill='url(#gnSoil)' stroke='#6b4423' stroke-width='1.3'/>")
    for k, (y0, y1) in enumerate(((200, 194), (218, 210), (238, 228), (258, 246))):
        p.append(f"<path d='M{250 + k * 4},{y0} Q370,{y0 - 6 + k} 480,{y1}' stroke='#6b4423' stroke-width='1.6' fill='none' opacity='.35'/>")
    for (x, y, sc) in ((306, 254, 1.0), (356, 270, .8), (282, 276, .6)):
        p.append(stein(x, y, sc))
    for (x, y, sc) in ((318, 214, 1.0), (404, 204, .8), (270, 244, .9), (470, 244, 1.0)):
        p.append(gras(x, y, sc, "#a8a07a"))
    # Wiese mit Blumen: hinten klein, vorn groß
    reihen = [
        (206, .66, [(20, "margerite"), (52, "klee"), (86, "loewenzahn"), (118, "kornblume"), (150, "mohn"), (182, "margerite"), (212, "klee")]),
        (238, 1.0, [(12, "loewenzahn"), (40, "mohn"), (70, "loewenzahn"), (100, "margerite"), (134, "kornblume"), (166, "klee"), (198, "mohn"), (224, "loewenzahn")]),
        (276, 1.55, [(28, "margerite"), (72, "mohn"), (112, "loewenzahn"), (154, "kornblume"), (196, "margerite")]),
    ]
    for y, sc, liste in reihen:
        for i, (x, art) in enumerate(liste):
            p.append(wiesenblume(x, y + (i % 2) * 4, sc * (.92 + (i % 3) * .06), art, 22, i % 2 == 1))
    for x, y, sc in ((40, 270, 1.2), (130, 262, 1.0), (214, 272, 1.1)):
        p.append(gras(x, y, sc))
    # Insekten auf der Wiese
    p.append(schmetterling(66, 150, .9, -14))
    p.append(schmetterling(196, 176, .62, 12, "#a259d9"))
    p.append(hummel(150, 202, .7))
    p.append(marienkaefer(74, 252, 1.0))
    p.append(schwebfliege(34, 196, 1.0))
    p.append(biene(110, 226, .5, -12, False, pollen_beine=True, schatten=True))
    p.append(biene(168, 262, .55, 6, True, pollen_beine=True, schatten=True))
    p.append(biene(30, 232, .46, -8, False, schatten=True))
    # Traktor mit Spritzgestänge
    tx, ty, ts = 410, 270, .8
    p.append(traktor(tx, ty, ts))
    # Lupe mit Varroa-Milbe auf der Biene
    cx, cy, R = 394, 114, 62
    clip = clip_kreis("cnLupe", cx, cy, R)
    bee = (biene_koerper(pollen_beine=True) + varroa(-29, 0, .92, -6))
    p.append(f"<g clip-path='url(#cnLupe)'><circle cx='{cx}' cy='{cy}' r='{R}' fill='url(#gnLupeBg)'/>"
             f"<path d='{ ''.join(f'M{cx - 80 + i * 22},{cy + 64} l11,-19 h22 l11,19 l-11,19 h-22 z' for i in range(8)) }' fill='#fde9b0' opacity='.5'/>"
             + g(bee, cx + 12, cy + 8, 1.28, -4) + "</g>")
    p.append(lupe_rand(cx, cy, R))
    # kleine Biene mit Ring und Lupenstrahlen
    sbx, sby, sbs, sbr = 262, 66, .5, -6
    p.append(biene(sbx, sby, sbs, sbr, False, schatten=True))
    ab = lokal(sbx, sby, sbs, sbr, False, -26, 2)
    p.append(varroa(*lokal(sbx, sby, sbs, sbr, False, -27, -3), .5, sbr))
    p.append(tangenten(ab, 12, (cx, cy), R + 3))
    p.append(f"<circle cx='{f(ab[0])}' cy='{f(ab[1])}' r='12' fill='none' stroke='#c0392b' stroke-width='2.4'/>")
    # Beschriftung
    p.append(etikett(394, 16, "Varroa-Milbe", "#b3261e", 13))
    p.append(etikett(62, 12, "Blühwiese", "#2e8b3d", 13))
    p.append(etikett(322, 205, "kahle Fläche", "#6b5a45", 13))
    p.append(beschr(446, 226, "Pestizid", ziel=(tx + 44 * ts, ty - 22 * ts), size=13, von=(446, 232)))
    return szene("Bienen in Gefahr: links eine bunte Blühwiese mit Bienen und anderen Insekten, rechts eine kahle Fläche mit Traktor und Pestizid, in der Lupe eine Varroa-Milbe auf einer Biene", *p,
                 defs=DEFS_GEFAHR + clip)


# ═══════════════════════════════════════════════════════════════════════════
#  glossar-bestaeubung  vereinfachter Ablauf: Blüte → Biene trägt Pollen → Blüte → Apfel
# ═══════════════════════════════════════════════════════════════════════════
def glossar_bestaeubung():
    p = [wolke(400, 44, .7)]
    # Wiese und Zweig
    p.append("<path d='M0,238 Q120,214 240,232 T480,224 V288 H0 Z' fill='url(#gnHuegel)' stroke='#6ba340' stroke-width='1.2'/>")
    p.append(ast("M-12,196 C60,196 120,192 200,190 C280,188 340,170 492,156", 9))
    for (x, y, l, r, d) in ((140, 194, 34, 200, False), (176, 190, 30, -25, True), (230, 188, 32, 205, False), (338, 176, 32, 205, False),
                            (366, 166, 28, -22, True), (20, 196, 30, 200, True)):
        p.append(blatt(x, y, l, r, d))
    # Blüte 1 mit viel Pollen, Blüte 2, Apfel
    p.append(apfelbluete(80, 150, 54, 10))
    p.append(apfelbluete(300, 140, 46, 36, pollen=False))
    p.append(apfel(424, 196, 28))
    p.append(ast("M418,160 Q420,170 421,176", 3, "#6b4423", "#6b4423"))
    # Pollen-Körner, die an Blüte 2 ankommen (Narbe in der Mitte)
    p.append(pollenpunkte([(284, 128), (290, 122), (276, 136), (296, 128), (282, 144)], 2.1))
    # Flugweg der Biene mit Pollen
    p.append(bogen("M118,98 C150,38 232,34 268,92", "#475569", 2.8, "7 5"))
    ba = (190, 58, .9, -6)
    p.append(biene(*ba, False, pollen_beine=True, pollen_haare=True, schatten=True))
    # Pfeil Blüte → Apfel
    p.append(bogen("M344,150 C372,150 392,164 404,184", "#475569", 2.8))
    p.append(t(384, 128, "später", 12, 800, "#475569"))
    # Beschriftung
    anth = (68, 138)
    p.append(beschr(44, 40, "Pollen", ziel=anth, size=14, von=(46, 46)))
    p.append(beschr(190, 20, "Biene", size=14))
    p.append(beschr(300, 254, "Blüte", size=14))
    p.append(beschr(80, 254, "Blüte", size=14))
    p.append(beschr(424, 254, "Apfel", size=14))
    return szene("Bestäubung: Die Biene trägt Pollen von einer Blüte zur nächsten, danach kann ein Apfel wachsen", *p,
                 defs="<linearGradient id='gnHuegel' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#b9df8c'/><stop offset='1' stop-color='#7db04a'/></linearGradient>")


# ═══════════════════════════════════════════════════════════════════════════
#  glossar-varroamilbe  Milbe stark vergrößert, Größenvergleich zur Biene
# ═══════════════════════════════════════════════════════════════════════════
def glossar_varroamilbe():
    p = []
    cx, cy, R = 362, 150, 104
    clip = clip_kreis("cnGross", cx, cy, R)
    # kleine Biene links mit winziger Milbe (echte Größenordnung)
    bx, by, bs, br = 112, 168, 1.5, -4
    p.append(biene(bx, by, bs, br, False, schatten=True))
    ab = lokal(bx, by, bs, br, False, -26, -4)
    p.append(varroa(ab[0], ab[1], .4 * bs, br))
    # Lupenstrahlen und Ring
    p.append(tangenten(ab, 17, (cx, cy), R + 3))
    p.append(f"<circle cx='{f(ab[0])}' cy='{f(ab[1])}' r='17' fill='none' stroke='#c0392b' stroke-width='2.6'/>")
    # große Lupe mit Milbe
    p.append(f"<g clip-path='url(#cnGross)'><circle cx='{cx}' cy='{cy}' r='{R}' fill='url(#gnLupeBg)'/>"
             + g(varroa_koerper(rx=78, ry=56), cx, cy + 4, 1.0, -8) + "</g>")
    p.append(lupe_rand(cx, cy, R))
    # Beschriftung
    p.append(etikett(cx, 10, "Varroa-Milbe", "#b3261e", 15, hoehe=24))
    p.append(beschr(cx, 277, "stark vergrößert", size=13))
    p.append(beschr(104, 232, "Biene, etwa 12–14 mm", size=13))
    p.append(beschr(ab[0] - 6, 60, "echte Größe", ziel=(ab[0], ab[1] - 17), size=13, von=(ab[0] - 6, 66)))
    return szene("Varroa-Milbe: links eine Biene mit einer winzigen Milbe, rechts die Milbe stark vergrößert", *p,
                 defs=DEFS_GEFAHR + clip, grund="url(#gHimmel)")


# ═══════════════════════════════════════════════════════════════════════════
#  nutzen-5-raetsel  Rätselfassung von nutzen-5: 900 × 560, KEIN Text, vier antippbare Orte
# ═══════════════════════════════════════════════════════════════════════════
RS = 900 / 480          # Maßstab: die Szene wird in 480 × 299 gezeichnet und mit 1,875 vergrößert
# Orte zum Antippen (Pixel in 900 × 560): Mittelpunkt x, y und empfohlener Radius r. Abstand der Ränder ≥ 60 px.
RAETSEL_ORTE = {
    "wiese": {"x": 235, "y": 408, "r": 150},     # Blühwiese mit sieben Bienen (ganze Wiese links von x ≈ 460)
    "kahl": {"x": 565, "y": 482, "r": 70},       # kahle Fläche ohne Blumen und ohne Bienen
    "traktor": {"x": 784, "y": 469, "r": 80},    # Traktor mit Sprühnebel
    "lupe": {"x": 700, "y": 190, "r": 125},      # Lupe mit Biene und Varroa-Milbe
}


def nutzen_5_raetsel():
    """Wie nutzen-5, aber ohne jede Beschriftung (das Bild-Rätsel „Warum gibt es hier weniger Bienen?“).
    Links eine Blühwiese mit sieben gut zählbaren Bienen, rechts eine kahle Fläche ohne Bienen mit Traktor und
    Sprühnebel, oben eine Lupe auf eine Biene mit Varroa-Milbe."""
    HZ = 299
    p = []
    p.append("<rect x='200' y='0' width='280' height='200' fill='url(#gnDunst)'/>")
    p.append(f"<path d='M0,176 Q60,146 140,166 Q200,176 252,188 V210 H0 Z' fill='#a9d27f' stroke='#6ba340' stroke-width='1'/>")
    p.append(himmel_wiese(184, h=HZ))
    # kahle Fläche: Erde, Furchen, Steine, trockene Büschel – keine Blumen, keine Insekten
    p.append(f"<path d='M232,178 C250,198 234,216 258,234 C270,246 252,264 262,{HZ} H480 V174 C400,166 300,168 232,178 Z' fill='url(#gnSoil)' stroke='#6b4423' stroke-width='1.3'/>")
    for k, (y0, y1) in enumerate(((200, 194), (218, 210), (238, 228), (258, 246), (278, 266))):
        p.append(f"<path d='M{250 + k * 4},{y0} Q370,{y0 - 6 + k} 480,{y1}' stroke='#6b4423' stroke-width='1.6' fill='none' opacity='.35'/>")
    for (x, y, sc) in ((300, 244, 1.0), (338, 262, .85), (278, 280, .7), (452, 214, .7)):
        p.append(stein(x, y, sc))
    for (x, y, sc) in ((318, 218, 1.0), (404, 204, .8), (272, 250, .9), (344, 288, .9)):
        p.append(gras(x, y, sc, "#a8a07a"))
    # Wiese mit Blumen: hinten klein, vorn groß
    reihen = [
        (206, .66, [(20, "margerite"), (52, "klee"), (86, "loewenzahn"), (118, "kornblume"), (150, "mohn"), (182, "margerite"), (212, "klee")]),
        (240, 1.0, [(12, "loewenzahn"), (40, "mohn"), (70, "loewenzahn"), (100, "margerite"), (134, "kornblume"), (166, "klee"), (198, "mohn"), (224, "loewenzahn")]),
        (282, 1.5, [(28, "margerite"), (72, "mohn"), (112, "loewenzahn"), (154, "kornblume"), (196, "margerite")]),
    ]
    for y, sc, liste in reihen:
        for i, (x, art) in enumerate(liste):
            p.append(wiesenblume(x, y + (i % 2) * 4, sc * (.92 + (i % 3) * .06), art, 22, i % 2 == 1))
    for x, y, sc in ((40, 276, 1.2), (130, 270, 1.0), (214, 280, 1.1)):
        p.append(gras(x, y, sc))
    # andere Insekten (keine bienenähnlichen, damit die Bienen eindeutig zählbar bleiben)
    p.append(schmetterling(70, 150, .9, -14))
    p.append(schmetterling(228, 146, .62, 12, "#a259d9"))
    p.append(marienkaefer(166, 276, 1.1))
    # genau sieben Bienen, weit auseinander, keine überdeckt eine andere
    for (x, y, r, sp, pol) in ((58, 218, -10, False, False), (104, 186, 8, True, True), (154, 218, -6, False, True), (200, 184, 10, True, False),
                               (78, 254, -8, False, True), (134, 250, 6, True, False), (190, 252, -10, False, False)):
        p.append(biene(x, y, .46, r, sp, pollen_beine=pol, schatten=True))
    # Traktor mit Sprühnebel auf der kahlen Fläche
    p.append(traktor(406, 276, .95))
    # Lupe: Glas mit Biene und Varroa-Milbe, Griff nach rechts unten
    cx, cy, R = RAETSEL_ORTE["lupe"]["x"] / RS, RAETSEL_ORTE["lupe"]["y"] / RS, 62
    clip = clip_kreis("cnLupeR", f(cx), f(cy), R)
    bee = biene_koerper(pollen_beine=True) + varroa(-29, 0, .92, -6)
    p.append(f"<path d='M{f(cx + R * .74)},{f(cy + R * .74)} L{f(cx + R * 1.24)},{f(cy + R * 1.24)}' stroke='#fff' stroke-width='13' stroke-linecap='round'/>"
             f"<path d='M{f(cx + R * .74)},{f(cy + R * .74)} L{f(cx + R * 1.24)},{f(cy + R * 1.24)}' stroke='#5b3a1d' stroke-width='9' stroke-linecap='round'/>"
             f"<path d='M{f(cx + R * .78)},{f(cy + R * .78)} L{f(cx + R * 1.18)},{f(cy + R * 1.18)}' stroke='#9a6a3a' stroke-width='2.4' stroke-linecap='round'/>")
    p.append(f"<g clip-path='url(#cnLupeR)'><circle cx='{f(cx)}' cy='{f(cy)}' r='{R}' fill='url(#gnLupeBg)'/>"
             f"<path d='{''.join(f'M{f(cx - 80 + i * 22)},{f(cy + 64)} l11,-19 h22 l11,19 l-11,19 h-22 z' for i in range(8))}' fill='#fde9b0' opacity='.5'/>"
             + g(bee, cx + 12, cy + 8, 1.28, -4) + "</g>")
    p.append(lupe_rand(f(cx), f(cy), R))
    inhalt = f"<g transform='scale({RS})'>{''.join(p)}</g>"
    return szene("Rätselbild: links eine Wiese mit Blumen, Bienen und anderen Insekten, rechts ein Feld mit einem Traktor, oben eine Lupe", inhalt,
                 defs=DEFS_GEFAHR + clip, w=900, h=560)


def raetsel_punkte_schreiben():
    """Schreibt werkzeuge/nutzen5_raetsel_punkte.json (Orte des Rätselbilds in Pixeln, 900 × 560)."""
    import json
    import os
    daten = {"bild": "/static/img/lese/nutzen-5-raetsel.svg", "breite": 900, "hoehe": 560,
             "hinweis": "Mittelpunkt x, y und empfohlener Radius r je Ort; Ränder der Kreise ≥ 60 px auseinander, Durchmesser ≥ 110 px.",
             "orte": RAETSEL_ORTE}
    pfad = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutzen5_raetsel_punkte.json")
    with open(pfad, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(daten, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return pfad


GRAFIKEN = {"nutzen-1": nutzen_1, "nutzen-2": nutzen_2, "nutzen-3": nutzen_3, "nutzen-4": nutzen_4, "nutzen-5": nutzen_5,
            "nutzen-5-raetsel": nutzen_5_raetsel,
            "glossar-bestaeubung": glossar_bestaeubung, "glossar-varroamilbe": glossar_varroamilbe}

if __name__ == "__main__":
    erzeuge(GRAFIKEN)
    print(raetsel_punkte_schreiben())
