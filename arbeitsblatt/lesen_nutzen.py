"""Lesestrecke L4 „Honig, Wachs, Blüten – und Gefahren“ (Reiter „nutzen“) – Server-Teil mit Lösungen.

Nachschlagen NACH der Forschungsphase (plan_nutzen.py: steht nach Station 76). Die Kinder haben dann schon im Film den Weg
vom Nektar zum Honig beobachtet (71), im Beispielversuch Apfelzweige verglichen (72) und am Bild drei Gefahren gefunden (75).
Der Text bestätigt das und erweitert es: Schleuder, Wachs, der Name „Bestäubung“, Imkerjahr, Schutz.

Vier Abschnitte: Honig und Wachs · Bestäubung · Das Imkerjahr · Bienen in Gefahr.
Regeln (references/lernpfad.md, docs/INHALTE_FORMAT.md):
- je Abschnitt 2–5 kurze Sätze (höchstens etwa 15 Wörter), ein Schaubild (`bild` = Dateiname ohne .svg
  unter static/img/lese/, viewBox 480 × 288; gezeichnet von werkzeuge/grafiken_nutzen.py), eine Frage,
  die sich aus dem Abschnitt allein beantworten lässt
- genau 3 Antwortoptionen, `loesung` = Index der richtigen Option (über die Abschnitte verteilt)
- fette Begriffe (<strong>…</strong>) haben einen Eintrag in glossar_nutzen.py
- nur gesicherte Fakten aus AB_KONZEPT.md, dieselben Wörter wie Film und 3D-Modell

Offene Punkte für die Prüfung vor der Veröffentlichung:
- Abschnitt „Bestäubung“, Erklärung: „drittwichtigstes Nutztier“ ist vorsichtig formuliert („gilt oft als“) und stammt vom
  Deutschen Imkerbund; vor dem Ausliefern prüfen.
- Das Futter im Spätsommer heißt im ganzen Reiter „Zuckerlösung“ (nicht „Zuckerfutter“).
- Futterfrage ehrlich (Audit, Entscheidung 4): „Die Bienen suchen ihr Futter meist selbst“; im Spätsommer ergänzt der Imker
  Zuckerlösung. Nirgends „niemand füttert“.
- Das Schaubild nutzen-2 („Wachs“) gehört nicht mehr zu einem eigenen Abschnitt (Honig und Wachs sind einer geworden);
  nutzen-1 zeigt die Honigernte und steht für den gemeinsamen Abschnitt.
"""

LESESTRECKEN = {
    "nutzen": {
        "station": "L4", "eyebrow": "Lesestrecke 4",
        "titel": "Honig, Wachs, Blüten – und Gefahren",
        "abschnitte": [
            {
                "ueberschrift": "Honig und Wachs",
                "bild": "nutzen-1",
                "bild_alt": "Schaubild: Imker an der Schleuder, daneben ein Rähmchen mit Honig und volle Honiggläser",
                "text": ("Im Film hast du gesehen: Aus Nektar wird Honig, der Vorrat für den Winter.\n"
                         "Der Imker nimmt nur einen Teil und holt ihn mit der <strong>Schleuder</strong> aus den Waben.\n"
                         "Arbeiterinnen bilden <strong>Wachs</strong> in Drüsen am Hinterleib.\n"
                         "Daraus bauen sie Waben.\n"
                         "Menschen machen aus Bienenwachs auch Kerzen und Salben."),
                "frage": "Woher kommt das Wachs der Bienen?",
                "optionen": ["Aus den Blüten", "Aus Drüsen am Hinterleib", "Aus dem Holz des Kastens"],
                "loesung": 1,
                "erklaerung": "Richtig: Die Arbeiterinnen bilden das Wachs selbst, in Drüsen am Hinterleib.",
            },
            {
                "ueberschrift": "Bestäubung",
                "bild": "nutzen-3",
                "bild_alt": "Schaubild: Biene holt Pollen an einer Apfelblüte, fliegt zur nächsten Blüte, daraus wächst ein Apfel",
                "text": ("Im ausgedachten Beispiel hatte der Zweig mit Netz nur wenige Äpfel.\n"
                         "Insekten wie Bienen konnten dort keinen Pollen von Blüte zu Blüte tragen.\n"
                         "Dieses Weitertragen heißt <strong>Bestäubung</strong>.\n"
                         "Auf einem Ausflug besucht eine Biene meist nur eine Pflanzenart.\n"
                         "Danach können Früchte und Samen entstehen, etwa bei Apfel, Kirsche und Raps."),
                "frage": "Was geschieht bei der Bestäubung?",
                "optionen": ["Der Imker erntet Honig aus den Waben",
                             "Die Biene baut Waben aus Wachs",
                             "Pollen kommt von einer Blüte zur nächsten"],
                "loesung": 2,
                "erklaerung": ("Richtig: Die Biene trägt Pollen weiter, und daraus können Früchte entstehen. "
                               "Darum gilt die Honigbiene in Deutschland oft als drittwichtigstes Nutztier, "
                               "nach Rind und Schwein."),
            },
            {
                "ueberschrift": "Das Imkerjahr",
                "bild": "nutzen-4",
                "bild_alt": "Schaubild: Imkerjahr als Jahreskreis: Frühling, das Volk wächst; Sommer, Honigernte; Spätsommer, Futter und Behandlung gegen Milben; Winter, die Wintertraube im verschneiten Kasten",
                "text": ("Im Frühling wächst das Volk, und der Imker kontrolliert es.\n"
                         "Die Bienen suchen ihr Futter meist selbst.\n"
                         "Im Sommer erntet der Imker einen Teil des Honigs.\n"
                         "Im Spätsommer ergänzt er Zuckerlösung als Ersatz für den Honig.\n"
                         "Im Spätsommer behandelt er das Volk auch gegen die <strong>Varroa-Milbe</strong>.\n"
                         "Im Winter lässt er die Bienen in Ruhe."),
                "frage": "Warum ergänzt der Imker im Spätsommer Zuckerlösung?",
                "optionen": ["Sie ersetzt den Honig, den er genommen hat",
                             "Damit die Bienen mehr Wachs bilden",
                             "Damit das Volk im Frühling schneller wächst"],
                "loesung": 0,
                "erklaerung": "Richtig: Die Zuckerlösung ersetzt den Honig, den der Imker geerntet hat.",
            },
            {
                "ueberschrift": "Bienen in Gefahr",
                "bild": "nutzen-5",
                "bild_alt": "Schaubild: links eine bunte Blumenwiese mit Bienen, rechts eine kahle Fläche mit Traktor und Pestizid, in der Lupe eine Varroa-Milbe auf einer Biene",
                "text": ("Im Rätselbild hast du drei Gefahren gefunden.\n"
                         "Auf kahlen Flächen finden Bienen kaum Blüten.\n"
                         "Manche <strong>Pestizide</strong> sind Gifte gegen Schädlinge und können Bienen schaden.\n"
                         "Die <strong>Varroa-Milbe</strong> saugt an Larven, Puppen und Bienen und schwächt das Volk.\n"
                         "Eine <strong>Blühwiese</strong> oder ein bienenfreundlicher Garten hilft ihnen."),
                "frage": "Was macht die Varroa-Milbe?",
                "optionen": ["Sie baut Waben im Bienenkasten",
                             "Sie saugt an Larven, Puppen und Bienen",
                             "Sie sammelt Nektar auf Blüten"],
                "loesung": 1,
                "erklaerung": "Richtig: Die Varroa-Milbe saugt an den Bienen und schwächt so das Volk.",
            },
        ],
    },
}
