"""Stationsplan des Reiters „Die Biene“ (key „koerper“): Reihenfolge der Stationen und Typ je Aufgabe.

Diese Datei gehört der Inhalts-Agentin dieses Reiters. Format und Regeln: siehe plan_nutztier.py und docs/FORSCHEN.md.

Dramaturgie (forschend-entwickelnd, das 3D-Modell ist das Forschungsinstrument; Stand nach dem Audit vom 4.10.2026):
 1. Forscherfrage 1 (50): „Wie ist eine Biene gebaut?“ – die Kinder vermuten Körperteile, Beine, Flügel.
 2. Erkunden (8): frei von außen, innen (Situs) und als Explosion – drei Beobachtungsaufträge (kehren in 51 und 54 wieder).
 3. Forscherbogen (51): zählen und prüfen am Modell (Körperteile, Beine, Flügel von hinten, Fühler, wer trägt Flügel und Beine).
 4. Vermutung prüfen (52): Erkenntnis „drei Körperteile, sechs Beine, vier Flügel“ – gleich lange Optionen, Knöpfe zur Evidenz.
 5. Im Modell finden (9): erst zählen und prüfen, dann Namen und Lage festigen. Kleine Teile mit Kamerafahrt (Feld `fokus`).
    Keine Organe und kein Pollenkörbchen: Was dort erforscht wird (54, 55), nimmt Station 9 nicht vorweg.
 6. Forscherfrage 2 (53): „Wie trägt die Biene Nektar und Pollen nach Hause?“ – vermuten, bevor man ins Innere schaut.
 7. Tabelle (54): Innenleben im Situs – Lage und Aussehen von Honigmagen, Flugmuskeln, Gehirn, Stachel (alle Organ-Knöpfe Pflicht).
 8. Vermutung prüfen (55): Film Szene 8 (zwei Pflicht-Knöpfe mit Sekundensprung) plus Blick ins Modell.
 9. Nachschlagen (L2): Lesestrecke nach der Forschungsphase – bestätigt und erweitert, was die Kinder selbst gefunden haben.
10. Sprachwerkstatt (56, 57): Einzahl und Mehrzahl mit Artikel; Zeitfolge „zuerst, dann, danach, schließlich“ am Weg des Nektars.
11. Zeichnen (15): die Biene von der Seite (Anwenden; KI-Bewertung nach Freigabe).
Gestrichen gegenüber der ersten Fassung: 10, 11, 12, 13, 14, 16, 17 (Grenze: höchstens 12 Stationen).
Zustand im Modell: Der Baustein modell3d.js schickt vor jedem Ziel von Aufgabe 9 „zurueck“, jeder Knopf in diesem Reiter beginnt
ebenfalls mit „zurueck“ – Hervorhebungen und Namensschilder aus anderen Stationen bleiben nicht stehen.
"""

STATIONEN = [50, 8, 51, 52, 9, 53, 54, 55, "L2", 56, 57, 15]

TYPEN = {
    50: "vermutung", 8: "erkunden", 51: "protokoll", 52: "pruefen", 9: "modellfinden",
    53: "vermutung", 54: "tabelle", 55: "pruefen", 56: "zuordnung", 57: "sortierung", 15: "zeichnen",
}
