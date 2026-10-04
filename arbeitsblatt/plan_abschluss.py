"""Stationsplan des Reiters „Abschluss & Quellen“ (key „abschluss“): Reihenfolge der Stationen und Typ je Aufgabe.

Diese Datei gehört der Inhalts-Agentin dieses Reiters. Format und Regeln: siehe plan_nutztier.py und docs/FORSCHEN.md.
Der Abschluss hat keine Lesestrecke und höchstens 6 Stationen; das „Forscherbuch“ (Typ `forscherbuch`) gehört hierher.
Die Quoten (Forschen, Sprachwerkstatt, Abfrage) gelten für diesen Reiter nicht.

DRAMATURGIE
 1. Zurückschauen (80): „Mein Forscherbuch“ sammelt automatisch Forscherfragen, Vermutungen, Erkenntnisse und Notizen aller Reiter
    und lässt sich drucken oder als PDF sichern.
 2. Wiederholen (38 Blitzfragen, 39 Begriffs-Domino): Grundbegriffe und Zusammenhänge aus allen Reitern; die Blitzfragen stützen sich
    auf die Erkenntnissätze der Reiter.
 3. Quellen prüfen (40): Woher weißt du es? (Lesestrecken, Film, 3D-Modell, eigene Beobachtungen im Forscherbuch)
 4. Anwenden (T): Zwei Bienenvölker für die Schule – erklären, begründen (weil, denn), beurteilen; Niveau A mit Textbausteinen.
"""

STATIONEN = [80, 38, 39, 40, "T"]

TYPEN = {
    80: "forscherbuch", 38: "blitz", 39: "domino", 40: "quellen", "T": "transfer",
}
