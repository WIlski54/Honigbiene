"""Glossar-Einträge des Reiters „Die Biene“ (Lesestrecke L2, Aufgaben 8–17).

Begriffe laut AB_KONZEPT.md („Glossar“): Insekt · Facettenauge · Fühler · Rüssel · Honigmagen · Pollenkörbchen · Stachel,
dazu Nektar, Pollen und Flugmuskeln (kommen in L2 fett vor). Bilder (fett im Konzept): glossar-facettenauge,
glossar-honigmagen, glossar-pollenkoerbchen, glossar-stachel – sie zeichnet der Grafik-Agent (werkzeuge/grafiken_koerper.py).

Format: siehe glossar_nutztier.py und docs/INHALTE_FORMAT.md. Schlüssel eindeutig über alle glossar_*.py, Aliase eindeutig
über das ganze Glossar (glossar.py prüft das beim Import). Text höchstens etwa 400 Zeichen, kurze Sätze.
Zahlen nur aus „Gesicherte Fakten“: etwa 5 000 Einzelaugen, etwa 200 Flügelschläge pro Sekunde.
"""

EINTRAEGE = {
    "insekt": {
        "titel": "Insekt", "bild": None,
        "text": ("Ein Insekt hat drei Körperteile: Kopf, Brust und Hinterleib. "
                 "Es hat sechs Beine. Die Biene ist ein Insekt. "
                 "Die Spinne hat acht Beine und ist kein Insekt."),
        "aliase": ["Insekt", "Insekten"],
    },
    "facettenauge": {
        "titel": "Facettenauge", "bild": "glossar-facettenauge",
        "text": ("Das Facettenauge besteht aus etwa 5 000 Einzelaugen. "
                 "Die Biene hat zwei große Facettenaugen an den Seiten des Kopfes. "
                 "Dazu kommen drei kleine Punktaugen oben auf dem Kopf."),
        "aliase": ["Facettenauge", "Facettenaugen"],
    },
    "fuehler": {
        "titel": "Fühler", "bild": None,
        "text": ("Die Fühler sitzen vorn am Kopf. Die Biene hat zwei Fühler. "
                 "Mit ihnen riecht und tastet sie."),
        "aliase": ["Fühler"],
    },
    "ruessel": {
        "titel": "Rüssel", "bild": None,
        "text": ("Der Rüssel sitzt am Kopf der Biene. "
                 "Damit saugt sie Nektar aus den Blüten."),
        "aliase": ["Rüssel"],
    },
    "honigmagen": {
        "titel": "Honigmagen", "bild": "glossar-honigmagen",
        "text": ("Der Honigmagen ist ein Vorratsbehälter im Hinterleib. "
                 "Darin trägt die Biene Nektar zum Bienenstock. "
                 "Er ist vom Magen für die Verdauung getrennt. "
                 "Man sagt auch Honigblase."),
        "aliase": ["Honigmagen", "Honigblase", "Honigblasen"],
    },
    "pollenkoerbchen": {
        "titel": "Pollenkörbchen", "bild": "glossar-pollenkoerbchen",
        "text": ("Das Pollenkörbchen ist eine Mulde am Hinterbein der Biene. "
                 "Dort trägt sie den Pollen nach Hause. "
                 "Der Pollen sieht aus wie ein gelbes Höschen. "
                 "Man sagt deshalb auch Pollenhöschen."),
        "aliase": ["Pollenkörbchen", "Pollenhöschen", "Höschen"],
    },
    "stachel": {
        "titel": "Stachel", "bild": "glossar-stachel",
        "text": ("Der Stachel sitzt am Ende des Hinterleibs. Zu ihm gehört eine Giftblase. "
                 "Arbeiterinnen und die Königin haben einen Stachel, Drohnen nicht. "
                 "Ein Stachel mit Widerhaken bleibt in der Haut von Säugetieren stecken. "
                 "Die Biene stirbt dann meist."),
        "aliase": ["Stachel", "Stacheln"],
    },
    "nektar": {
        "titel": "Nektar", "bild": None,
        "text": ("Nektar ist der süße Saft der Blüten. "
                 "Die Biene saugt ihn mit dem Rüssel auf und trägt ihn im Honigmagen nach Hause. "
                 "Im Bienenstock wird daraus Honig."),
        "aliase": ["Nektar"],
    },
    "pollen": {
        "titel": "Pollen", "bild": None,
        "text": ("Pollen ist der Blütenstaub. "
                 "Er enthält Eiweiß für die Larven. "
                 "Die Biene sammelt ihn und trägt ihn im Pollenkörbchen nach Hause."),
        "aliase": ["Pollen", "Blütenstaub"],
    },
    "flugmuskeln": {
        "titel": "Flugmuskeln", "bild": None,
        "text": ("Die Flugmuskeln liegen in der Brust der Biene. "
                 "Sie bewegen die Flügel etwa 200-mal in der Sekunde. "
                 "Im Winter wärmen sich die Bienen durch das Zittern dieser Muskeln."),
        "aliase": ["Flugmuskeln", "Flugmuskel"],
    },
}
