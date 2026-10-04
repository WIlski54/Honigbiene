"""Glossar-Einträge des Reiters „Das Bienenvolk“ (Lesestrecke L3 und die Stationen des Reiters, siehe plan_volk.py).

Dieselben Wörter wie die Sprecherin im Film „Ein Bienenvolk im Bienenstock“ (Bienenstock, Bienenkasten, Flugloch, Wabe,
Zelle, Rähmchen, Brutraum, Honigraum, Bienenvolk, Königin, Arbeiterinnen, Drohnen, Ammenbienen, Wächterinnen, Sammlerinnen,
Larve, Puppe, Traube). Der Film sagt „Tanz“ und „Schwänzeln“; der Fachname Schwänzeltanz steht hier.
Fakten nur aus AB_KONZEPT.md („Gesicherte Fakten“).

Format: siehe glossar_nutztier.py und docs/INHALTE_FORMAT.md. Schlüssel eindeutig über alle glossar_*.py,
Aliase eindeutig über das ganze Glossar (sonst wirft glossar.py beim Import einen Fehler).
Verglichen wird nur klein geschrieben (kein Umlaut-Abgleich): Mehrzahl und Beugung stehen deshalb als Aliase da.
"""


EINTRAEGE = {
    "bienenvolk": {
        "titel": "Bienenvolk", "bild": None,
        "text": "Alle Bienen eines Bienenstocks bilden zusammen ein Bienenvolk. Es hat eine Königin, viele Arbeiterinnen und einige Drohnen. "
                "Im Sommer sind es bis zu etwa 50 000 Bienen, im Winter etwa 10 000. Bienen leben nur als Volk.",
        "aliase": ["Bienenvolk", "Bienenvölker", "Bienenvolkes", "Volk", "Völker"],
    },
    "koenigin": {
        "titel": "Königin", "bild": "glossar-koenigin",
        "text": "Die Königin ist die Mutter aller Bienen im Stock. Ihr Hinterleib ist länger als bei den anderen Bienen. "
                "Sie legt jeden Tag bis zu etwa 2 000 Eier und lebt 3 bis 5 Jahre. Befehle gibt sie nicht. "
                "Den roten Punkt im Film malen Imker manchmal auf, damit man sie erkennt.",
        "aliase": ["Königin", "Königinnen", "Bienenkönigin"],
    },
    "arbeiterin": {
        "titel": "Arbeiterin", "bild": None,
        "text": "Arbeiterinnen sind die vielen kleinen Bienen im Volk, etwa 12 bis 14 mm lang. Sie putzen, füttern die Larven, "
                "bauen Waben, halten Wache und sammeln. Mit dem Alter wechselt ihre Aufgabe. "
                "Eine Sommerarbeiterin lebt etwa 5 bis 6 Wochen.",
        "aliase": ["Arbeiterin", "Arbeiterinnen", "Arbeitsbiene", "Arbeitsbienen"],
    },
    "drohne": {
        "titel": "Drohne", "bild": "glossar-drohne",
        "text": "Drohnen sind die Männchen im Bienenvolk. Es gibt nur einige hundert. Sie paaren sich mit jungen Königinnen. "
                "Drohnen haben keinen Stachel. Im Herbst drängen die Arbeiterinnen sie aus dem Stock.",
        "aliase": ["Drohne", "Drohnen"],
    },
    "wabe": {
        "titel": "Wabe", "bild": "glossar-wabe",
        "text": "Eine Wabe besteht aus vielen sechseckigen Zellen aus Wachs. Die Bienen bauen sie selbst. "
                "In den Zellen wachsen die jungen Bienen, oder die Bienen lagern dort Pollen und Honig.",
        "aliase": ["Wabe", "Waben"],
    },
    "zelle": {
        "titel": "Zelle", "bild": None,
        "text": "Eine Zelle ist ein kleines Sechseck aus Wachs in der Wabe. Dort wächst eine junge Biene, oder die Bienen lagern Pollen und Honig. "
                "Sechseckige Zellen sparen Platz und Wachs.",
        "aliase": ["Zelle", "Zellen", "Wabenzelle", "Wabenzellen", "Brutzelle", "Brutzellen"],
    },
    "raehmchen": {
        "titel": "Rähmchen", "bild": None,
        "text": "Ein Rähmchen ist ein kleiner Holzrahmen im Bienenkasten. Die Bienen bauen ihre Waben hinein. "
                "Der Imker kann ein Rähmchen herausziehen und das Volk ansehen. Im echten Kasten hängen viel mehr Rähmchen als im Film.",
        "aliase": ["Rähmchen", "Holzrähmchen"],
    },
    "brutraum": {
        "titel": "Brutraum", "bild": None,
        "text": "Der Brutraum liegt im Bienenkasten unten. Dort wachsen die jungen Bienen in den Zellen der Waben. "
                "Zur Brut gehören Eier, Larven und Puppen.",
        "aliase": ["Brutraum"],
    },
    "honigraum": {
        "titel": "Honigraum", "bild": None,
        "text": "Der Honigraum liegt im Bienenkasten oben, über dem Brutraum. Dort lagern die Bienen den Honig als Vorrat. "
                "Der Imker erntet nur einen Teil davon.",
        "aliase": ["Honigraum"],
    },
    "flugloch": {
        "titel": "Flugloch", "bild": None,
        "text": "Das Flugloch ist die kleine Öffnung am Bienenkasten. Hier fliegen die Bienen ein und aus. "
                "Wächterinnen passen am Eingang auf.",
        "aliase": ["Flugloch"],
    },
    "larve": {
        "titel": "Larve", "bild": None,
        "text": "Nach 3 Tagen schlüpft aus dem Ei eine Larve. Sie ist weiß und liegt gekrümmt in der Zelle. "
                "Ammenbienen füttern sie etwa 6 Tage lang. Dann verdeckeln die Bienen die Zelle mit Wachs.",
        "aliase": ["Larve", "Larven"],
    },
    "puppe": {
        "titel": "Puppe", "bild": None,
        "text": "In der verdeckelten Zelle wird aus der Larve eine Puppe. Sie verwandelt sich etwa 12 Tage lang in eine junge Biene. "
                "Nach 21 Tagen insgesamt schlüpft die Arbeiterin.",
        "aliase": ["Puppe", "Puppen"],
    },
    "schwaenzeltanz": {
        "titel": "Schwänzeltanz", "bild": "glossar-schwaenzeltanz",
        "text": "Mit dem Schwänzeltanz zeigt eine Sammlerin den anderen Bienen, wo es gutes Futter gibt. Sie tanzt auf der senkrechten Wabe. "
                "Der Winkel zwischen der Senkrechten und dem Schwänzellauf ist so groß wie der Winkel zwischen Sonne und Futter. "
                "Je länger das Schwänzeln dauert, desto weiter ist das Futter entfernt. Entdeckt hat das Karl von Frisch.",
        "aliase": ["Schwänzeltanz", "Tanz", "Bienentanz", "Schwänzellauf", "Schwänzeln"],
    },
    "ammenbiene": {
        "titel": "Ammenbiene", "bild": None,
        "text": "Ammenbienen sind junge Arbeiterinnen. Sie füttern die Larven. Später bauen sie Waben und halten Wache.",
        "aliase": ["Ammenbiene", "Ammenbienen"],
    },
    "sammlerin": {
        "titel": "Sammlerin", "bild": None,
        "text": "Sammlerinnen sind die ältesten Arbeiterinnen. Sie fliegen aus und holen Nektar und Pollen von den Blüten. "
                "Der Sammelflug geht meist bis etwa 3 km weit.",
        "aliase": ["Sammlerin", "Sammlerinnen", "Sammelbiene", "Sammelbienen"],
    },
    "waechterin": {
        "titel": "Wächterin", "bild": None,
        "text": "Wächterinnen sind Arbeiterinnen. Sie sitzen am Flugloch und passen am Eingang auf. So bleibt das Bienenvolk geschützt.",
        "aliase": ["Wächterin", "Wächterinnen"],
    },
    "wintertraube": {
        "titel": "Wintertraube", "bild": "glossar-wintertraube",
        "text": "Im Winter rücken die Bienen zu einer Traube zusammen. In der Mitte sitzt die Königin. "
                "Mit zitternden Flugmuskeln machen die Bienen Wärme. Vom Honigvorrat leben sie bis zum Frühling.",
        "aliase": ["Wintertraube", "Traube", "Bienentraube"],
    },
}
