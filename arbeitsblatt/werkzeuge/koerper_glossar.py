"""Glossarbilder des Reiters „Die Biene“: Facettenauge, Honigmagen, Pollenkörbchen, Stachel (je 480 × 288).

Alle vier arbeiten mit derselben Bildsprache: die Biene links, rechts eine Lupe auf das Gesuchte
(beim Honigmagen: die Biene im Schnitt mit Nektar-Weg).
"""
from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz
from bienen_innen import lupe
from bienen_situs import biene_schnitt
from bienen_bein import hinterbein_gross, MARKEN
from bienen_stachel import stachel_gross
from bienen_kopf import kopf_vorn

BLAU_K, GRUEN_K, MAG_K, ROT_K = "#006AB3", "#12894a", "#AD007C", "#d6336c"
_R = 11.0                                           # Umkreisradius der großen Facetten (Lupe)
_RW, _RH = math.sqrt(3) * _R, 1.5 * _R               # Gitterabstände des Facettenmusters

def _hex_punkte(cx, cy, r):
    return " ".join("%.2f,%.2f" % (cx + r * math.cos(math.radians(-90 + 60 * i)), cy + r * math.sin(math.radians(-90 + 60 * i))) for i in range(6))


_polys = "".join("<polygon points='%s'/>" % _hex_punkte(cx, cy, _R) for cx, cy in [(0, 0), (_RW, 0), (_RW / 2, 1.5 * _R), (0, 3 * _R), (_RW, 3 * _R)])
_bz.DEFS_EXTRA.append(
    "<pattern id='bHexL' patternUnits='userSpaceOnUse' width='%.2f' height='%.2f'><g fill='none' stroke='#f3dcb4' stroke-width='1.5' opacity='.62'>%s</g></pattern>"
    % (_RW, 3 * _R, _polys))


def _sechs(cx, cy, r, **kw):
    pts = " ".join(f"{cx + r * math.cos(math.radians(-90 + 60 * i)):.1f},{cy + r * math.sin(math.radians(-90 + 60 * i)):.1f}" for i in range(6))
    a = " ".join(f"{k.replace('_', '-')}='{v}'" for k, v in kw.items())
    return f"<polygon points='{pts}' {a}/>"


def _kegel(c1, r1, c2, r2):
    (a1, a2), (b1, b2) = tangenten(c1, r1, c2, r2)
    return (f"<polygon points='{a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {b1[0]:.1f},{b1[1]:.1f}' fill='#fff' opacity='.55'/>"
            f"<line x1='{a1[0]:.1f}' y1='{a1[1]:.1f}' x2='{a2[0]:.1f}' y2='{a2[1]:.1f}' stroke='#14304a' stroke-width='1.3' stroke-dasharray='5 4' opacity='.6'/>"
            f"<line x1='{b1[0]:.1f}' y1='{b1[1]:.1f}' x2='{b2[0]:.1f}' y2='{b2[1]:.1f}' stroke='#14304a' stroke-width='1.3' stroke-dasharray='5 4' opacity='.6'/>")


# ═══════════════════════════════════════════════════════════════════════════
def glossar_facettenauge():
    # Lupe links, Kopf von vorn rechts; das linke Auge (näher an der Lupe) ist eingekreist
    hx, hy, hs = 358, 140, .68
    kopf = platz(kopf_vorn(ruessel=False), hx, hy, hs)
    ex, ey = hx - 64 * hs, hy - 10 * hs
    ring = (f"<ellipse cx='{ex:.1f}' cy='{ey:.1f}' rx='{34 * hs + 5:.1f}' ry='{57 * hs + 5:.1f}' transform='rotate(10 {ex:.1f} {ey:.1f})' "
            f"fill='none' stroke='{BLAU_K}' stroke-width='3.2' stroke-dasharray='7 5'/>")
    lx, ly, lr = 118, 146, 100
    # Facetten-Lupe: gewölbtes Auge mit Sechsecken, ein Einzelauge hervorgehoben
    kuppel = (f"<circle cx='{lx}' cy='{ly}' r='{lr}' fill='url(#bAugeV)'/>"
              f"<circle cx='{lx}' cy='{ly}' r='{lr + 4}' fill='url(#bHexL)'/>")
    mrow = round((ly - 20) / _RH / 2) * 2                    # gerade Zeile
    hcx = round(lx / _RW) * _RW
    hcy = mrow * _RH
    kuppel += _sechs(hcx, hcy, _R - .8, fill="#f7a53a", fill_opacity=".92", stroke="#fff", stroke_width="2")
    kuppel += _sechs(hcx, hcy, _R - 3.5, fill="#ffd27a", fill_opacity=".8")
    kuppel += (f"<ellipse cx='{lx - 38}' cy='{ly - 46}' rx='34' ry='15' fill='url(#bGlanz)' opacity='.85' transform='rotate(-28 {lx - 38} {ly - 46})'/>"
               f"<ellipse cx='{lx + 44}' cy='{ly + 50}' rx='16' ry='9' fill='url(#bGlanz)' opacity='.3' transform='rotate(-28 {lx + 44} {ly + 50})'/>")
    kuppel += haare(lx, ly, lr - 6, lr - 6, 46, 9, "#c9a45e", 1.2, richtung=(0, 0), aussen=1, seed=9, einwaerts=14)
    lp = lupe(lx, ly, lr, kuppel, rand="#fff")
    teile = [hintergrund_blueten(), _kegel((ex, ey), 34 * hs + 8, (lx, ly), lr), kopf, ring, lp,
             beschriftung(310, 250, "Facettenauge", ex + 2, ey + 44, BLAU_K, ueber=False, size=14),
             beschriftung(118, 244, "ein Einzelauge", hcx + 1, hcy + 14, "#b45309", ueber=False, size=14),
             t(118, 24, "etwa 5 000 Einzelaugen", 12, 800, TEXT)]
    return bild("Glossarbild: Vergrößertes Facettenauge mit vielen Sechsecken, daneben der Kopf der Biene von vorn mit eingekreistem Auge", *teile)


# ═══════════════════════════════════════════════════════════════════════════
def glossar_honigmagen():
    cx, cy, s = 240, 124, .98
    schnitt = platz(biene_schnitt(ruessel_ende=(168, 82)), cx, cy, s)
    fx, fy = cx + 168 * s + 10, cy + 82 * s + 8            # Blütenmitte
    bluete = blume(fx - 3.1, fy + 68, 3.1, "#f08aa8")
    nektar_blume = ("<g><ellipse cx='%.1f' cy='%.1f' rx='7' ry='7.6' fill='url(#bNektar)' stroke='#c47500' stroke-width='1'/>"
                    "<ellipse cx='%.1f' cy='%.1f' rx='2' ry='2.8' fill='#fff' opacity='.85'/></g>" % (fx, fy, fx - 2, fy - 3))
    ziel_crop = (cx - 81 * s, cy + 3 * s)
    teile = [hintergrund_blueten(), "<ellipse cx='235' cy='214' rx='175' ry='6' fill='#000' opacity='.1'/>",
             bluete, nektar_blume, schnitt,
             beschriftung(318, 38, "Honigmagen", ziel_crop[0] + 8, ziel_crop[1] - 20, "#c2185b", size=15),
             beschriftung(424, 110, "Nektar", fx + 6, fy - 12, "#b45309", size=15)]
    return bild("Glossarbild: Biene im Schnitt, der Rüssel saugt Nektar aus der Blüte, der Honigmagen im Hinterleib ist markiert", *teile)


# ═══════════════════════════════════════════════════════════════════════════
def glossar_pollenkoerbchen():
    bs, bx, by = .74, 176, 168
    with dichte(.6):
        bee = platz(biene_seite(fluegel_an=True, hinterbein_pollen=True), bx, by, bs)
    # Pollenhöschen am Bein der kleinen Biene (lokal ≈ (−56, 72))
    px, py = bx + bs * (-56), by + bs * 72
    lx, ly, lr = 370, 150, 98
    hx, hy = MARKEN["hoeschen"]
    ls = 1.36
    inhalt = platz(hinterbein_gross(), lx - ls * hx + 4, ly - ls * hy - 2, ls, 0)
    lp = lupe(lx, ly, lr, inhalt)
    # Zielpunkte in der Lupe
    kx, ky = MARKEN["koerbchen"]
    z_k = (lx - ls * hx + 4 + ls * kx, ly - ls * hy - 2 + ls * ky)
    z_h = (lx + 4, ly - 2)
    teile = [hintergrund_blueten(), pollenstaub(14, 8, (0, 0, 480, 288)), _kegel((px, py), 16, (lx, ly), lr),
             f"<circle cx='{px:.1f}' cy='{py:.1f}' r='16' fill='none' stroke='#14304a' stroke-width='1.8' stroke-dasharray='5 4' opacity='.8'/>",
             bee, lp,
             beschriftung(318, 36, "Pollenhöschen", z_h[0] - 6, z_h[1] - 10, "#b45309", size=14),
             beschriftung(292, 246, "Pollenkörbchen", z_k[0] + 4, z_k[1] + 12, MAG_K, ueber=False, size=14)]
    return bild("Glossarbild: Biene mit gelbem Pollenhöschen am Hinterbein, daneben vergrößert das Pollenkörbchen", *teile)


# ═══════════════════════════════════════════════════════════════════════════
def glossar_stachel():
    bs, bx, by = .52, 104, 178
    with dichte(.7):
        bee = platz(biene_seite(fluegel_an=True, stachel=True, beine_an=True), bx, by, bs, 0, spiegeln=True)
    tx_, ty_ = bx + bs * 222, by + bs * 20                 # Stachelspitze der gespiegelten Biene
    lx, ly, lr = 368, 140, 106
    ss = .56
    gx = lx + ss * 52
    app = platz(stachel_gross(), gx, ly - 2, ss, 0, spiegeln=True)
    lp = lupe(lx, ly, lr, app)
    # Ziele (gespiegelt: x_bild = gx − ss·x_lokal)
    def Z(x, y):
        return gx - ss * x, ly - 2 + ss * y
    z_s, z_w, z_g = Z(-50, 0), Z(-86, 14), Z(150, 4)
    teile = [hintergrund_blueten(), _kegel((tx_, ty_), 14, (lx, ly), lr),
             f"<circle cx='{tx_:.1f}' cy='{ty_:.1f}' r='14' fill='none' stroke='#14304a' stroke-width='1.8' stroke-dasharray='5 4' opacity='.8'/>",
             "<ellipse cx='125' cy='238' rx='96' ry='5' fill='#000' opacity='.1'/>",
             bee, lp,
             beschriftung(446, 30, "Stachel", z_s[0], z_s[1] - 8, MAG_K, size=14),
             beschriftung(430, 254, "Widerhaken", z_w[0] + 2, z_w[1] + 8, ROT_K, ueber=False, size=14),
             beschriftung(318, 30, "Giftblase", z_g[0], z_g[1] - 10, "#0b7285", size=14)]
    return bild("Glossarbild: Stachel der Biene mit Widerhaken und Giftblase, vergrößert neben dem Hinterleib", *teile)
