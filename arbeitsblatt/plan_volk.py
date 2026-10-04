"""Stationsplan des Reiters „Das Bienenvolk“ (key „volk“): Reihenfolge der Stationen und Typ je Aufgabe.

Diese Datei gehört der Inhalts-Agentin dieses Reiters. Format und Regeln: siehe plan_nutztier.py und docs/FORSCHEN.md.

Dramaturgie (Forscherraum mit dem Film „Ein Bienenvolk im Bienenstock“, 12 Szenen = Kapitel 1–12; Stand nach dem Audit vom 4.10.2026):
 1. Forscherfrage: „Wer sagt den Bienen, was sie tun sollen?“ – Vermutung (60, id v_chef).
 2. Erkunden: den Film ansehen mit drei Beobachtungsaufträgen (18); Beobachtungsbogen mit Zahlen und Antworten aus Kapitel 3–7 (62: Räume,
    Arten, Eier, Larve, Tage, Arbeit mit dem Alter); Vergleichstabelle Königin, Arbeiterin, Drohne mit Bildern in den Spaltenköpfen (63).
    Die Zahl der Bienen im Stock fragt dieser Reiter nicht (Reiter 1 hat Frage und Erklärung).
 3. Auswerten: die Vermutung prüfen (64): gleich gebaute, prüfbare Aussagen, neutrale Quelle, drei Knöpfe (Kapitel 5, 7, 12), die den Film
    abspielen und auf die Belegstelle springen; der Erkenntnissatz kommt ins Forscherbuch.
 4. Weiter erkunden: den Bienenkasten beschriften (21, Anwenden: Wortschatz am Bild) und das Tanzrätsel „Wo ist das Futter?“ – Richtung und
    Länge des Schwänzellaufs entdecken (66, Kapitel 9, Pflicht-Knopf spielt den Tanz ab).
 5. Nachschlagen: Lesestrecke bestätigt und erweitert, was der Film nicht sagt (Lebensdauer, Drohnen ohne Stachel, Dach und Boden, Larve 6
    und Puppe 12 Tage) und belegt die Spalte „in echt“ der nächsten Station (roter Punkt, mehr Rähmchen, Entwicklung nur im Film schnell).
 6. Modellgrenzen: Filmkritik als Tabelle „Echt oder nur im Film?“ (68) – steht NACH der Lesestrecke, weil sie belegt, was in echt gilt.
    Zeilen nur zu dem, was das AB belegt: Papierbienen/Länge, roter Punkt, Rähmchen, 40 Eier im Bild gegen „bis zu 2 000“, Entwicklung.
    Honigernte (Schleuder) und Nektar zu Honig gehören zu Reiter 4 und entfallen hier.
 7. Sprachwerkstatt: Zeitfolge „zuerst, dann, danach, schließlich“ am Leben der Arbeiterin (65); „je … desto“, weil, damit, deshalb (67).
 8. Anwenden: Zeichnung 2, der Schwänzeltanz (26).
Alle Film-Knöpfe spielen sofort ab; Schlüsselsätze werden sekundengenau angesprungen (Satzzeiten aus papiertheater/docs/ab_uebergabe.md).
Wegen der Obergrenze (13 Stationen für „volk“) entfallen gegenüber dem ersten Entwurf: Finde den Moment (19, Königin legt ein Ei),
das Jahresdiagramm (24), Wer macht was (20), Was verrät der Tanz (25), zwei Sortieraufgaben (22, 23) und die Notizen (28). Die alte
Filmkritik (27, Multiple Choice) ist als Tabelle 68 neu gebaut. Die Prüfstation 61 zur Bienenzahl entfällt (die Schätzfrage in
Reiter 1 ist keine Vermutung mehr).

Echte Forschen-Stationen (Kind sammelt Evidenz): 60, 62, 63, 64, 66, 68 (dazu 18, der Film selbst). Anwenden: 21 (Wortschatz am Bild),
26 (Zeichnen). Sprachwerkstatt: 65, 67 (2 von 11 Stationen ohne Lesestrecke). Abfrage: 0. Zusammen mit der Lesestrecke 12 Stationen (erlaubt sind 13).
"""

STATIONEN = [60, 18, 62, 63, 64, 21, 66, "L3", 68, 65, 67, 26]

TYPEN = {
    60: "vermutung", 18: "film", 62: "protokoll", 63: "tabelle", 64: "pruefen", 21: "bildpunkte",
    66: "bildwahl", 68: "tabelle", 65: "sortierung", 67: "luecke", 26: "zeichnen",
}
