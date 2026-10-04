"""Lesestrecke L3 „Wer lebt im Bienenstock?“ (Reiter „volk“) – Server-Teil mit Lösungen.

Nachschlagen NACH dem Erkunden (forschend-entwickelnd, docs/FORSCHEN.md): Die Lesestrecke steht im Reiter „Das Bienenvolk“ nach dem
Tanzrätsel (plan_volk.py) und bestätigt und erweitert, was die Kinder im Film selbst herausgefunden haben (Bezug im Text: „Im Film hast
du gehört …“). Dieselben Wörter wie die Sprecherin. Neu ist hier, was der Film nicht sagt: Lebensdauer (Abschnitt 2), Drohnen ohne
Stachel (Abschnitt 2), Dach und Boden (Abschnitt 3), Larve 6 Tage und Puppe 12 Tage (Abschnitt 4).
Sie belegt außerdem die Spalte „So ist es in echt“ der Filmkritik (Station danach): roter Punkt der Königin von den Imkern (Abschnitt 2),
im echten Kasten viel mehr Rähmchen (Abschnitt 3), im Film dauert die Entwicklung nur wenige Sekunden statt 21 Tage (Abschnitt 4).

Regeln (references/lernpfad.md, docs/INHALTE_FORMAT.md):
- je Abschnitt wenige kurze Sätze (höchstens etwa 15 Wörter), ein Schaubild (`bild` = Dateiname ohne .svg
  unter static/img/lese/, viewBox 480 × 288), eine Frage, die sich aus dem Abschnitt allein beantworten lässt
- genau 3 Antwortoptionen, `loesung` = Index der richtigen Option, Position über die Abschnitte variiert
- fette Begriffe (<strong>…</strong>) haben einen Eintrag in glossar_volk.py
- nur gesicherte Fakten aus AB_KONZEPT.md
Schlüssel des Dicts = Reiter-Key aus config.ABSCHNITTE; `station` = Lx aus config.ABSCHNITTE.
"""

LESESTRECKEN = {
    "volk": {
        "station": "L3", "eyebrow": "Lesestrecke 3",
        "titel": "Wer lebt im Bienenstock?",
        "abschnitte": [
            {
                "ueberschrift": "Ein Volk aus vielen Bienen",
                "bild": "volk-1", "bild_alt": "Schaubild: Eine Wabe voller wimmelnder Bienen",
                "text": "Im Film hast du gehört: Im Sommer leben bis zu 50 000 Bienen im Stock.\n"
                        "Alle diese Bienen zusammen heißen <strong>Bienenvolk</strong>.\n"
                        "Im Winter sind es nur etwa 10 000.\n"
                        "Im Frühling wächst das Volk, im Herbst wird es kleiner.",
                "frage": "Was stimmt für ein Bienenvolk?",
                "optionen": [
                    "Im Winter sind es mehr Bienen als im Sommer",
                    "Im Sommer sind es viel mehr Bienen als im Winter",
                    "Es sind immer gleich viele Bienen im Volk",
                ],
                "loesung": 1,
                "erklaerung": "Richtig: Im Sommer leben bis zu etwa 50 000 Bienen im Volk. Im Winter sind es nur etwa 10 000.",
            },
            {
                "ueberschrift": "Königin, Arbeiterin und Drohne",
                "bild": "volk-2", "bild_alt": "Schaubild: Königin, Arbeiterin und Drohne nebeneinander",
                "text": "Neu: Die <strong>Königin</strong> lebt 3 bis 5 Jahre.\n"
                        "Imker malen ihr manchmal einen roten Punkt auf den Rücken.\n"
                        "<strong>Arbeiterinnen</strong> leben im Sommer nur etwa 5 bis 6 Wochen.\n"
                        "Winterbienen leben bis zu etwa 6 Monate.\n"
                        "<strong>Drohnen</strong> sind Männchen ohne Stachel.\n"
                        "Im Herbst drängen die Arbeiterinnen sie aus dem Stock.",
                "frage": "Welche Biene lebt am längsten?",
                "optionen": [
                    "Die Königin",
                    "Die Winterbiene",
                    "Die Sommerbiene",
                ],
                "loesung": 0,
                "erklaerung": "Richtig: Die Königin lebt 3 bis 5 Jahre. Winterbienen leben bis zu etwa 6 Monate, Sommerbienen nur etwa 5 bis 6 Wochen.",
            },
            {
                "ueberschrift": "Der Bienenkasten von innen",
                "bild": "volk-3",
                "bild_alt": "Schaubild: Querschnitt durch den Bienenkasten mit Dach, Honigraum, Brutraum, Boden und Flugloch",
                "text": "Du hast den Bienenkasten beschriftet.\n"
                        "Unten ist der Boden, oben ist das Dach.\n"
                        "Durch das <strong>Flugloch</strong> fliegen die Bienen ein und aus.\n"
                        "Unten liegt der <strong>Brutraum</strong>, oben der <strong>Honigraum</strong>.\n"
                        "In beiden Räumen hängen <strong>Rähmchen</strong> mit Waben.\n"
                        "Im echten Kasten hängen viel mehr Rähmchen als im Film.",
                "frage": "Wo liegt im Bienenkasten der Honigraum?",
                "optionen": [
                    "Unten, direkt am Boden",
                    "Vorne, neben dem Flugloch",
                    "Oben, über dem Brutraum",
                ],
                "loesung": 2,
                "erklaerung": "Richtig: Oben liegt der Honigraum für den Vorrat. Unten liegt der Brutraum für den Nachwuchs.",
            },
            {
                "ueberschrift": "Die Wabe",
                "bild": "volk-4", "bild_alt": "Schaubild: Ausschnitt einer Wabe mit Brutzellen, Pollenzellen und Honigzellen",
                "text": "Eine <strong>Wabe</strong> besteht aus vielen <strong>Zellen</strong> aus Wachs.\n"
                        "Die Zellen sind sechseckig und sparen Platz und Wachs.\n"
                        "In manchen Zellen lagern Pollen und Honig.\n"
                        "In den Brutzellen wächst aus dem Ei eine Arbeiterin.\n"
                        "Das dauert 21 Tage: Ei 3 Tage, <strong>Larve</strong> 6 Tage, <strong>Puppe</strong> 12 Tage.\n"
                        "Im Film geht das in wenigen Sekunden.",
                "frage": "Was sparen die sechseckigen Zellen?",
                "optionen": [
                    "Zeit und Honig",
                    "Platz und Wachs",
                    "Pollen und Licht",
                ],
                "loesung": 1,
                "erklaerung": "Richtig: Sechseckige Zellen sparen Platz und Wachs. In den Brutzellen wachsen die jungen Bienen.",
            },
        ],
    },
}
