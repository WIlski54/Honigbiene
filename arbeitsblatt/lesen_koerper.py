"""Lesestrecke L2 „Eine Biene ist ein Insekt“ (Reiter „koerper“) – Server-Teil mit Lösungen.

Fünf Abschnitte laut AB_KONZEPT.md („Lesestrecken“, L2): Körperteile und Beine, Kopf, Brust, Hinterleib, Sammelwerkzeug.
Die Lesestrecke steht NACH der Forschungsphase (plan_koerper.py, leseNach 55): Sie bestätigt und erweitert, was die Kinder im
3D-Modell selbst gezählt und gefunden haben („Du hast im Modell …“), und bringt Neues, das das Modell nicht zeigt (Sinne,
Flugmuskeln, Stachel, Haare und Bürsten). Die Schaubilder koerper-1 … koerper-5 zeichnet der Grafik-Agent
(werkzeuge/grafiken_koerper.py); `bild_alt` beschreibt, was darauf zu sehen sein soll.

Regeln (docs/INHALTE_FORMAT.md): ein Gedanke pro Satz (höchstens etwa 15 Wörter), je Abschnitt eine Frage, die sich aus dem
Abschnitt allein beantworten lässt, genau 3 Antwortoptionen, Lösungsposition über die Abschnitte verteilt (1, 0, 2, 1, 0),
fette Begriffe nur mit Eintrag in glossar_koerper.py. Feste Wörter: Bienenstock, Rüssel, Nektar, Pollen, Honigmagen,
Pollenkörbchen (gelbes „Höschen“), Flugmuskeln, Facettenaugen, Fühler.
Zahlen nur aus „Gesicherte Fakten“ (AB_KONZEPT.md): etwa 5 000 Einzelaugen, etwa 200 Flügelschläge pro Sekunde.
"""

# Zwischen „5“ und „000“ steht ein geschütztes Leerzeichen, damit die Zahl nicht umbricht.
_FUENF_TAUSEND = "5 000"

LESESTRECKEN = {
    "koerper": {
        "station": "L2", "eyebrow": "Lesestrecke 2",
        "titel": "Eine Biene ist ein Insekt",
        "abschnitte": [
            {
                "ueberschrift": "Drei Körperteile, sechs Beine",
                "bild": "koerper-1",
                "bild_alt": "Schaubild: Biene von der Seite. Kopf, Brust und Hinterleib sind in drei Farben zu sehen, sechs Beine hängen an der Brust.",
                "text": ("Du hast im Modell gezählt: Die Biene hat drei Körperteile und sechs Beine.\n"
                         "Darum ist sie ein <strong>Insekt</strong>.\n"
                         "Alle Insekten haben sechs Beine.\n"
                         "Spinnen haben acht Beine und sind keine Insekten.\n"
                         "In echt ist eine Arbeiterin nur etwa 12 bis 14 Millimeter lang."),
                "frage": "Wie viele Beine hat eine Biene?",
                "optionen": ["Acht", "Sechs", "Vier"],
                "loesung": 1,
                "erklaerung": "Richtig: Insekten haben sechs Beine. Spinnen haben acht Beine und gehören nicht zu den Insekten.",
            },
            {
                "ueberschrift": "Der Kopf: Sinne und Mund",
                "bild": "koerper-2",
                "bild_alt": "Schaubild: Kopf der Biene von vorn mit zwei Fühlern, zwei großen Facettenaugen, drei kleinen Punktaugen und dem Rüssel.",
                "text": ("Am Kopf hast du die zwei <strong>Fühler</strong> gefunden.\n"
                         "Sie riechen und tasten.\n"
                         f"Die zwei großen <strong>Facettenaugen</strong> bestehen aus je etwa {_FUENF_TAUSEND} Einzelaugen.\n"
                         "Dazu kommen drei kleine Punktaugen.\n"
                         "Mit dem <strong>Rüssel</strong> saugt die Biene <strong>Nektar</strong>, den süßen Saft der Blüten."),
                "frage": "Womit riecht und tastet die Biene?",
                "optionen": ["Mit den Fühlern", "Mit den Facettenaugen", "Mit dem Rüssel"],
                "loesung": 0,
                "erklaerung": "Richtig: Die Fühler riechen und tasten. Gesehen wird mit den Augen, gesaugt mit dem Rüssel.",
            },
            {
                "ueberschrift": "Die Brust: Flügel und Beine",
                "bild": "koerper-3",
                "bild_alt": "Schaubild: Brust der Biene mit vier Flügeln und sechs Beinen. Im Schnitt sieht man die kräftigen Flugmuskeln.",
                "text": ("Du hast gesehen: Flügel und Beine sitzen an der Brust.\n"
                         "Es sind vier Flügel und sechs Beine.\n"
                         "In der Brust liegen kräftige <strong>Flugmuskeln</strong>.\n"
                         "Sie bewegen die Flügel etwa 200-mal in der Sekunde."),
                "frage": "Was bewegt die Flügel der Biene?",
                "optionen": ["Der Rüssel", "Die Fühler", "Die Flugmuskeln"],
                "loesung": 2,
                "erklaerung": "Richtig: Kräftige Flugmuskeln in der Brust bewegen die Flügel. Sie schlagen etwa 200-mal in der Sekunde.",
            },
            {
                "ueberschrift": "Der Hinterleib: Honigmagen und Stachel",
                "bild": "koerper-4",
                "bild_alt": "Schaubild: Hinterleib der Biene aufgeschnitten. Man sieht den Honigmagen, den Darm und am Ende den Stachel.",
                "text": ("Den <strong>Honigmagen</strong> hast du im Hinterleib gefunden.\n"
                         "Er ist ein Vorratsbehälter, in dem die Biene Nektar zum Bienenstock trägt.\n"
                         "Außerdem liegen dort der Darm und Drüsen, die Wachs bilden.\n"
                         "Am Ende sitzt der <strong>Stachel</strong>, den Drohnen nicht haben."),
                "frage": "Wozu dient der Honigmagen?",
                "optionen": ["Er bewegt die Flügel.", "Er transportiert Nektar.", "Er hilft beim Riechen."],
                "loesung": 1,
                "erklaerung": "Richtig: Im Honigmagen trägt die Biene Nektar zum Bienenstock. Er ist ein Vorratsbehälter.",
            },
            {
                "ueberschrift": "Werkzeug zum Sammeln",
                "bild": "koerper-5",
                "bild_alt": "Schaubild: Hinterbein der Biene mit dem Pollenkörbchen. Der Pollen klebt dort als dickes gelbes Höschen.",
                "text": ("Im Film siehst du das gelbe „Höschen“ am Hinterbein.\n"
                         "Haare am Körper halten <strong>Pollen</strong> fest, den Blütenstaub.\n"
                         "Mit Bürsten an den Beinen streift die Biene ihn ab.\n"
                         "Im <strong>Pollenkörbchen</strong> am Hinterbein trägt sie ihn nach Hause."),
                "frage": "Wo trägt die Biene den Pollen nach Hause?",
                "optionen": ["Im Pollenkörbchen am Hinterbein", "Im Honigmagen im Hinterleib", "Im Rüssel am Kopf"],
                "loesung": 0,
                "erklaerung": "Richtig: Der Pollen klebt im Pollenkörbchen am Hinterbein. Im Honigmagen reist der Nektar.",
            },
        ],
    },
}
