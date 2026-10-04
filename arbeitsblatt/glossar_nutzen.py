"""Glossar-Einträge des Reiters „Nutzen & Schutz“ (Lesestrecke L4, Aufgaben 29–37).

Hier stehen die fetten Begriffe der Lesestrecke 4: Wachs · Bestäubung · Varroa-Milbe · Schleuder · Pestizid · Blühwiese.
Bilder (gezeichnet von werkzeuge/grafiken_nutzen.py): glossar-bestaeubung, glossar-varroamilbe.

Nicht hier (gehören zu anderen Reitern, damit kein Schlüssel doppelt ist): Nektar, Pollen, Honig, Wintertraube.

Format: siehe glossar_nutztier.py und docs/INHALTE_FORMAT.md. Schlüssel eindeutig über alle glossar_*.py,
Aliase eindeutig über das ganze Glossar (sonst wirft glossar.py beim Import einen Fehler).
"""

EINTRAEGE = {
    "wachs": {
        "titel": "Wachs", "bild": None,
        "text": ("Wachs ist der Baustoff der Bienen. Arbeiterinnen bilden es in Drüsen "
                 "an der Unterseite des Hinterleibs. Daraus bauen sie die Zellen der Waben. "
                 "Auch Kerzen und Salben macht man aus Bienenwachs."),
        "aliase": ["Wachs", "Bienenwachs"],
    },
    "bestaeubung": {
        "titel": "Bestäubung", "bild": "glossar-bestaeubung",
        "text": ("Bei der Bestäubung gelangt Pollen von einer Blüte zur nächsten. "
                 "Die Biene trägt ihn auf ihrem Körper weiter. "
                 "Danach kann die Blüte Früchte und Samen bilden, zum Beispiel einen Apfel."),
        "aliase": ["Bestäubung", "bestäubt", "bestäuben"],
    },
    "varroamilbe": {
        "titel": "Varroa-Milbe", "bild": "glossar-varroamilbe",
        "text": ("Die Varroa-Milbe ist ein winziger Parasit. Ein Parasit lebt auf Kosten eines anderen Lebewesens. "
                 "Die Milbe saugt an Larven, Puppen und Bienen und schwächt so das Volk. "
                 "Der Imker behandelt die Völker im Spätsommer dagegen."),
        "aliase": ["Varroa-Milbe", "Varroa-Milben", "Varroamilbe", "Varroa", "Milbe", "Milben"],
    },
    "schleuder": {
        "titel": "Schleuder", "bild": None,
        "text": ("Die Schleuder holt den Honig aus den Waben. Die Waben drehen sich darin schnell. "
                 "Der Honig fliegt aus den Zellen und läuft an der Wand nach unten."),
        "aliase": ["Schleuder", "Honigschleuder"],
    },
    "pestizid": {
        "titel": "Pestizid", "bild": None,
        "text": ("Pestizide sind Mittel, die Schädlinge auf Feldern und in Gärten bekämpfen. "
                 "Manche davon können auch Bienen schaden."),
        "aliase": ["Pestizid", "Pestizide"],
    },
    "bluehwiese": {
        "titel": "Blühwiese", "bild": None,
        "text": ("Eine Blühwiese ist eine Wiese mit vielen verschiedenen Blumen. "
                 "Bienen finden dort Nektar und Pollen."),
        "aliase": ["Blühwiese", "Blühwiesen"],
    },
}
