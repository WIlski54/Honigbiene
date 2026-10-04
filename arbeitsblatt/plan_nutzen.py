"""Stationsplan des Reiters „Nutzen & Schutz“ (key „nutzen“): Reihenfolge der Stationen und Typ je Aufgabe.

Diese Datei gehört der Inhalts-Agentin dieses Reiters. Format und Regeln: siehe plan_nutztier.py und docs/FORSCHEN.md.

DRAMATURGIE (forschend-entwickelnd, Jahrgang 6; Stand nach dem Audit vom 4.10.2026) – Leitfrage des Reiters:
„Warum ist die Biene ein wichtiges Nutztier – und was braucht sie von uns?“ (Die Biene sucht ihr Futter meist selbst.)

  1. Forscherfrage 1 (70): „Wie viele Äpfel trägt ein Baum, wenn keine Insekten kommen?“ – die Kinder vermuten (genauso viele …
     gar keine); jede Option lässt sich mit den Zahlen aus 72 bestätigen oder widerlegen.
  2. Erkunden Honig (71, Film Kapitel 10, Pflicht-Knopf, Zeilenknöpfe mit Sekundensprung): Forscherbogen „Wie wird aus Nektar
     Honig?“ – Weitergabe von Rüssel zu Rüssel, Fächeln, Zellen verschließen, Farbe, der Imker zieht EIN Rähmchen heraus.
  3. Erkunden Bestäubung (72): AUSGEDACHTES Beispiel mit zwei Apfelzweigen (offen / Netz gegen Insekten, je 20 Blüten). Erst nach der
     eigenen Vermutung (Zeile 1) erscheinen die Zahlen („Ausgedachtes Beispiel – nicht gemessen“).
  4. Prüfen (73): gleich lange, prüfbare Aussagen; Evidenz = Zahlen aus 72 und Film Kapitel 12 („Honig, Wachs und viele Früchte“).
  5. Forscherfrage 2 (74): „Was gefährdet die Bienen?“ (mehrfach, alle Optionen am Bild prüfbar) → Erkunden am Rätselbild
     `nutzen-5-raetsel` ohne Etiketten (75, vier Kreise je Runde, Fragen ohne Gefahrenwort; „Pestizid“ und „Varroa-Milbe“ erst in der
     Erklärung nach dem Tipp) → Prüfen (76, Bild-Knopf zum Rätselbild).
  6. Nachschlagen (Lesestrecke L4, 4 Abschnitte, steht NACH 76): bestätigt und erweitert – Schleuder, Wachs, Name „Bestäubung“,
     Imkerjahr mit Zuckerlösung und Behandlung gegen die Varroa-Milbe, Schutz (Blühwiese, bienenfreundlicher Garten).
  7. Sprachwerkstatt: Zeitfolge am Imkerjahr (77, Lückentext mit Chips: im Frühling …; zuerst, dann, schließlich; C tippen) und
     Begründen mit weil, denn, damit (36: Was können wir für Bienen tun?).
  8. Anwenden und Sichern: Zeichnung 3 „Bestäubung“ (35) und „Mein Forscherbuch“-Notizen (37).

Quoten (ohne Lesestrecke, 11 Stationen; ehrlich gezählt nach Entscheidung 3 des Audits): echte Forschen-Stationen 70–76 (7),
Sprachwerkstatt 2 (77, 36), Anwenden 2 (35 Zeichnen, 37 Notizen), Abfrage 0.
Gestrichen gegenüber dem ersten Entwurf: 29, 30, 31, 32, 33, 34 (siehe Bericht).
"""

STATIONEN = [70, 71, 72, 73, 74, 75, 76, "L4", 77, 36, 35, 37]

TYPEN = {
    70: "vermutung", 71: "protokoll", 72: "protokoll", 73: "pruefen", 74: "vermutung", 75: "bildwahl", 76: "pruefen",
    77: "luecke", 36: "freitext", 35: "zeichnen", 37: "notizen",
}
