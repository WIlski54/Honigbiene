"""Platzhalter-Schaubilder, damit Lesestrecken und Bildpunkte-Aufgaben ohne echte Grafiken laufen.

Aufruf:  python werkzeuge/grafiken_platzhalter.py
Ausgabe: static/img/lese/platzhalter.svg (480 × 288) und platzhalter-karte.svg (900 × 560)

Die echten Bilder entstehen je Reiter in werkzeuge/grafiken_<reiter>.py (siehe docs/INHALTE_FORMAT.md,
„Grafiken“). Diese Platzhalter werden dann nicht mehr gebraucht und können gelöscht werden.
"""
from svg_helfer import (BLAU, DUNKEL, MAGENTA, W, H, baum, biene, blume, erzeuge, fussleiste, gras, himmel_wiese,
                        sonne, stein, svg, t, tafel, waben_gitter, wolke)


def platzhalter():
    waben = waben_gitter(40, 64, 14, 6, r=17, fuellung=lambda c, z: "url(#gHonig)" if (c + z) % 5 == 0 else None)
    return svg("Platzhalter-Schaubild: Wabenmuster mit der Aufschrift Schaubild folgt", waben,
               tafel(110, 100, 260, 70, ["PLATZHALTER", "Hier folgt das Schaubild"], farbe=MAGENTA, size=16),
               fussleiste(["Platzhalter für ein gegenständliches Schaubild (480 × 288)"], hoehe=30, size=11),
               grund="#fff8e0")


KARTE_W, KARTE_H = 900, 560


def platzhalter_karte():
    """Karte für Bildpunkte-Aufgaben (900 × 560). Die Punkte stehen in static/js/inhalte_nutztier.js
    (INHALTE.bildpunkte.platzhalter) und müssen zu den Positionen hier passen; das Bild trägt selbst keine Nummern."""
    p = [himmel_wiese(300, h=KARTE_H, w=KARTE_W), sonne(780, 92, 40), wolke(220, 90, 1.5),
         baum(112, 330, 2.1), gras(60, 350, 2.0), gras(860, 350, 1.8),
         blume(330, 430, 2.0), blume(560, 450, 1.8, "#c08adf"), stein(724, 470, 1.6)]
    # Platzhalter-Kasten
    p.append("<g filter='url(#fSchatten)'><rect x='440' y='330' width='120' height='76' rx='6' fill='url(#gHolz)' stroke='#7a4b22' stroke-width='3'/>"
             "<rect x='430' y='316' width='140' height='20' rx='4' fill='#8a5a2b'/><rect x='484' y='372' width='30' height='10' rx='3' fill='#3a2a14'/></g>")
    p.append(biene(610, 300, 2.6))
    p.append(t(450, 40, "PLATZHALTER – Bild folgt", 26, 800, MAGENTA))
    return svg("Platzhalter-Karte: Wiese mit Sonne, Baum, Blumen, Stein, Kasten und Biene", *p, w=KARTE_W, h=KARTE_H)


GRAFIKEN = {"platzhalter": platzhalter, "platzhalter-karte": platzhalter_karte}

if __name__ == "__main__":
    erzeuge(GRAFIKEN)
