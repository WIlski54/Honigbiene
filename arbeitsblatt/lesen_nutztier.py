"""Lesestrecke L1 „Eine Biene als Nutztier“ (Reiter „nutztier“) – Server-Teil mit Lösungen.

Forschend-entwickelnder Ansatz (docs/FORSCHEN.md): Die Lesestrecke steht NACH der Erkundung (Station 3 „Beim Imker“ und der
Vergleichstabelle 43; in plan_nutztier.py steht L1 hinter 43). Sie bestätigt und erweitert, was die Kinder selbst gefunden haben,
und nimmt darauf Bezug („in deiner Tabelle“, „die erste Frage“, „beim Imker“). Das Wort „Vermutung“ kommt nicht mehr vor. Alle vier Abschnitte und Bilder bleiben.

Je Abschnitt vier kurze Sätze (höchstens etwa 15 Wörter, ein Satz pro Zeile), ein Schaubild (`nutztier-1` … `nutztier-4`,
gezeichnet von werkzeuge/grafiken_nutztier.py), eine Frage, die sich aus dem Abschnitt allein beantworten lässt, genau drei Optionen.
Lösungspositionen: 2, 0, 1, 2. Fette Begriffe haben einen Glossar-Eintrag (glossar_nutztier.py; „Wachs“, „Bestäubung“ im Glossar des
Reiters „nutzen“, „Bienenvolk“ im Glossar des Reiters „volk“). Dasselbe Wort für dieselbe Sache: Kuh, Huhn, Schaf (nicht „Rind“).
"""

LESESTRECKEN = {
    "nutztier": {
        "station": "L1", "eyebrow": "Lesestrecke 1",
        "titel": "Eine Biene als Nutztier",
        "abschnitte": [
            {
                "ueberschrift": "Nutztiere helfen uns",
                "bild": "nutztier-1",
                "bild_alt": "Schaubild: Bauernhof mit Kuh, Huhn und Schaf, am Rand stehen Bienenkästen",
                "text": "Du kennst Kühe, Hühner und Schafe.\nSie geben uns Milch, Fleisch, Eier und Wolle.\nMenschen halten sie, weil sie uns etwas geben.\nSolche Tiere heißen <strong>Nutztiere</strong>.",
                "frage": "Warum halten Menschen Nutztiere?",
                "optionen": ["Weil sie hübsch aussehen", "Weil sie gut klettern können", "Weil sie uns etwas geben"],
                "loesung": 2,
                "erklaerung": "Richtig: Nutztiere geben uns zum Beispiel Milch, Eier oder Wolle.",
            },
            {
                "ueberschrift": "Die Biene ist anders",
                "bild": "nutztier-2",
                "bild_alt": "Schaubild: Bienenkästen auf einer Blumenwiese, ein Imker, fliegende Bienen",
                "text": "In deiner Tabelle ist die Biene anders als Kuh und Huhn.\nSie lebt frei und sucht ihr Futter meist selbst.\nDafür fliegt sie meist bis etwa 3 Kilometer weit.\nDer <strong>Imker</strong> stellt einen <strong>Bienenkasten</strong> für sie auf.",
                "frage": "Was ist bei der Honigbiene anders als bei Kuh und Huhn?",
                "optionen": ["Sie lebt frei und sucht ihr Futter meist selbst", "Sie bekommt jeden Tag Futter im Stall", "Sie wird jeden Morgen gemolken"],
                "loesung": 0,
                "erklaerung": "Richtig: Die Biene lebt frei und sucht ihr Futter meist selbst. Der Imker stellt nur den Bienenkasten auf.",
            },
            {
                "ueberschrift": "Was die Biene uns gibt",
                "bild": "nutztier-3",
                "bild_alt": "Schaubild: Honigglas, Kerze und ein Apfelzweig mit einer Biene",
                "text": "Du erinnerst dich an die erste Frage: Was bekommen wir von Bienen?\nBienen machen süßen <strong>Honig</strong> und liefern <strong>Wachs</strong> für Kerzen.\nBeim Flug von Blüte zu Blüte helfen sie den Pflanzen, Früchte zu bilden.\nDas nennt man <strong>Bestäubung</strong>.",
                "frage": "Was bedeutet Bestäubung?",
                "optionen": ["Bienen machen Kerzen aus Wachs", "Bienen helfen den Pflanzen, Früchte zu bilden", "Bienen tragen den Honig zum Imker"],
                "loesung": 1,
                "erklaerung": "Richtig: Bienen fliegen von Blüte zu Blüte. So können Früchte wachsen, zum Beispiel Äpfel.",
            },
            {
                "ueberschrift": "Der Imker kümmert sich",
                "bild": "nutztier-4",
                "bild_alt": "Schaubild: Ein Imker zieht ein Rähmchen mit Waben aus dem Bienenkasten",
                "text": "Du hast beim Imker seine Werkzeuge gefunden.\nDer Imker kontrolliert regelmäßig das <strong>Bienenvolk</strong>.\nEr erntet nur einen Teil des Honigs und lässt den Rest den Bienen.\nAußerdem schützt er sein Volk vor Krankheiten.",
                "frage": "Wie viel Honig erntet der Imker?",
                "optionen": ["Den ganzen Honig", "Keinen Honig", "Nur einen Teil des Honigs"],
                "loesung": 2,
                "erklaerung": "Richtig: Der Imker nimmt nur einen Teil. Der Rest bleibt für die Bienen.",
            },
        ],
    },
}
