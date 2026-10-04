"""Stationsplan des Reiters „Nutztier Biene“ (key „nutztier“): Reihenfolge der Stationen und Typ je Aufgabe.

Diese Datei gehört der Inhalts-Agentin dieses Reiters. `config.ABSCHNITTE` und `tests/plan.py` lesen sie.

STATIONEN  Reihenfolge der Karten im Reiter. Zahlen oder Zeichenketten in GROSSBUCHSTABEN („T“, „F1“); die Lesestrecke
           „L1“ darf an beliebiger Stelle stehen (Nachschlagen kommt erst nach der ersten Erkundung, siehe docs/FORSCHEN.md).
TYPEN      Aufgabentyp je Aufgabennummer (ohne die Lesestrecke). Muss zu `typ` in static/js/inhalte_nutztier.js passen.
Im Reiter-Objekt der Inhaltsdatei steht `lese: "L1"` und – weil die Lesestrecke nicht oben steht – `leseNach: 43`.

DRAMATURGIE (forschend-entwickelnd, Jahrgang 6; dieser Reiter hat weder Film noch 3D-Modell – Forschungsinstrumente sind Bilder)
 1. Einstieg (41, 42): zwei einfache Fragen mit SOFORTIGER Rückmeldung und Erklärung (Typ mc, keine Vermutungen: Im Reiter lässt
    sich nichts nachprüfen). 41 „Was bekommen wir Menschen von Bienen?“ (A eine, B zwei, C drei Antworten), 42 Schätzfrage
    „Wie viele Bienen im Sommer in einem Bienenstock?“ (C auch Winter); die Auflösung steht im Film im Reiter „Das Bienenvolk“.
 2. Entdecken (3, bildwahl = echtes Forschen): Auf dem Bild „Beim Imker“ finden die Kinder in drei Runden, wo die Bienen wohnen, wo sie Futter
    finden und wer sich kümmert – die Beobachtungen für die Tabelle 43.
 3. Vergleichen (43): Tabelle Kuh, Huhn, Schaf und Biene (Spaltenköpfe mit Bild, Produkte mit Emoji) – wer füttert das Tier,
    wo lebt es, was gibt es uns? Erkenntnis: Die Honigbiene ist ein besonderes Nutztier (frei, sucht selbst, der Imker kümmert sich).
 4. Nachschlagen (L1): kurze Lesestrecke, bestätigt und erweitert, was die Kinder selbst gefunden haben (Bezug auf Tabelle, erste Frage, Bild).
 5. Sprachwerkstatt (45 Artikel und Plural, 46 Wörter zusammensetzen mit Artikelwahl, 47 W-Fragen zu vorgegebenen Antwortsätzen) – am Wortschatz
    des Reiters; jede Aufgabe hat je Niveau einen eigenen Hilfetext.
 6. Fragen sammeln (7): eigene Fragen an einen Imker (W-Wörter aus Aufgabe 47); im Abschluss („Mein Forscherbuch“) prüft das Kind,
    welche seiner Fragen inzwischen beantwortet sind.
Erkenntnissatz für das Forscherbuch: nur 43 (besonderes Nutztier; die Biene sucht ihr Futter meist selbst). 41 und 42 tragen keine `erkenntnis`.
Gestrichen gegenüber der Lese-Fassung: 1 (Zuordnung Nutztier–Produkt, jetzt Tabelle 43), 2 (MC Nutztier, jetzt Erkenntnis 43 und
Blitzfragen 38), 4 (Lücke Fachbegriffe, jetzt Sprachwerkstatt), 5 (Richtig/Falsch, jetzt Blitzfragen), 6 (Schätzfrage, jetzt 42).
Gestrichen im Umbau zum Einstieg mit Rückmeldung: Vermutungen mit den Kennungen v_gaben/v_anzahl und die Station 44 (pruefen).
"""

STATIONEN = [41, 42, 3, 43, "L1", 45, 46, 47, 7]

TYPEN = {
    41: "mc", 42: "mc", 3: "bildwahl", 43: "tabelle",
    45: "luecke", 46: "luecke", 47: "luecke", 7: "notizen",
}
