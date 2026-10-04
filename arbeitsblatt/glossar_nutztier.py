"""Glossar-Einträge des Reiters „Nutztier Biene“ (Lesestrecke L1, Aufgaben 1–7).

Schlüssel sind über ALLE glossar_*.py eindeutig (glossar.py prüft das beim Import), ebenso die Aliase.
Hier stehen: nutztier, imker, bienenkasten (mit Bild glossar-bienenkasten) und honig.
„Wachs“ und „Bestäubung“ (L1, Abschnitt 3) liegen im Glossar des Reiters „nutzen“, „Bienenvolk“ in dem des Reiters „volk“.
Sprache: Sek I, 2–4 kurze Sätze, dieselben Wörter wie im Film und im 3D-Modell.
"""

EINTRAEGE = {
    "nutztier": {
        "titel": "Nutztier", "bild": None,
        "text": "Ein Nutztier ist ein Tier, das Menschen halten, weil es ihnen etwas gibt. Kühe geben Milch, Hühner legen Eier, Schafe liefern Wolle. Auch die Honigbiene ist ein Nutztier. Sie gibt uns Honig und Wachs.",
        "aliase": ["Nutztier", "Nutztiere", "Nutztieren", "Nutztieres"],
    },
    "imker": {
        "titel": "Imker", "bild": None,
        "text": "Ein Imker hält Bienenvölker. Er stellt den Bienenkasten auf und kümmert sich um die Bienen. Er erntet auch den Honig. Eine Frau mit dieser Aufgabe heißt Imkerin.",
        "aliase": ["Imker", "Imkerin", "Imkerinnen", "Imkern", "Imkers"],
    },
    "bienenkasten": {
        "titel": "Bienenkasten", "bild": "glossar-bienenkasten",
        "text": "Der Bienenkasten ist die Holzkiste des Imkers. In ihm wohnt ein Bienenvolk. Durch das Flugloch fliegen die Bienen ein und aus. Das ganze Zuhause des Volkes heißt Bienenstock.",
        "aliase": ["Bienenkasten", "Bienenkästen", "Bienenkastens", "Beute", "Beuten"],
    },
    "honig": {
        "titel": "Honig", "bild": None,
        "text": "Honig machen die Bienen aus Nektar. Er ist ihr Vorrat für den Winter. Der Imker erntet nur einen Teil davon. Als Ersatz füttert er die Bienen im Spätsommer.",
        "aliase": ["Honig", "Honigs"],
    },
}
