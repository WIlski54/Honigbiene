"""Zeichenaufträge für die KI-Bewertung (Prüfliste je Zeichnung).

Diese Datei ist die EINZIGE Stelle, an der Merkmale und Auftragstexte der drei Zeichnungen stehen.
`ki.py` liest sie; niemand muss `ki.py` anfassen. Die Schlüssel entsprechen `config.ZEICHEN_GERAETE`
und dem Feld `geraet` der Aufgaben in static/js/inhalte_<reiter>.js.

Felder je Zeichnung:
  nr        Aufgabennummer (muss zu config.ZEICHEN_GERAETE passen)
  titel     kurzer Name der Zeichnung
  motiv     ein Satz: Was soll zu sehen sein? (geht in den Prompt der KI)
  merkmale  Prüfliste in Kindersprache: Was muss eine gelungene Skizze zeigen?
            Formuliere so, dass ein Kind es am Bild wiederfindet („sechs Beine“), nicht als Definition.
  stufen    optional: zusätzliche Merkmale je Niveau {"A": [...], "B": [...], "C": [...]}
  hinweis   optional: Besonderheiten für die Bewertung (z. B. „Skizze, kein Kunstwerk“)

STAND: vorläufig knapp, abgeleitet aus AB_KONZEPT.md (Aufgaben 15, 26, 35). PLATZHALTER für die
Inhalts-Agenten – bitte verfeinern, aber keine Merkmale erfinden, die der Film oder das Modell nicht zeigen.
"""

ZEICHENAUFTRAEGE = {
    "biene": {
        "nr": 15,
        "titel": "Die Biene von der Seite",
        "motiv": "Eine Honigbiene von der Seite gesehen, so wie sie im 3D-Modell von der Seite aussieht.",
        "merkmale": [
            "drei getrennte Körperteile hintereinander: der Kopf vorn, die Brust in der Mitte, der Hinterleib hinten (Ovale oder Kreise reichen)",
            "sechs Beine, die an der Brust hängen (sechs Striche oder drei Striche je Seite, wenn sich Beine überdecken)",
            "zwei Fühler vorn am Kopf (zwei dünne Striche)",
            "Flügel, die an der Brust sitzen (zwei oder vier, dünne Flächen)",
        ],
        "stufen": {
            "A": [],
            "B": ["Streifen oder Ringe quer über den Hinterleib",
                  "Namen der Körperteile (Kopf, Brust, Hinterleib), zum Beispiel neben dem Teil oder mit einem Strich"],
            "C": ["Streifen oder Ringe quer über den Hinterleib",
                  "ein kleiner Stachel am Ende des Hinterleibs (Pluspunkt, kein Muss)",
                  "Beschriftung der Körperteile mit Strichen oder Pfeilen",
                  "ein Satz, der erklärt, welche Aufgabe ein Körperteil hat (zum Beispiel: Die Fühler riechen und tasten.)"],
        },
        "hinweis": ("Skizze mit dem Finger, kein Kunstwerk. Die Körperteile müssen nur klar zu erkennen sein. "
                    "Von der Seite verdecken sich Beine und Flügel teilweise: Wer drei Beine auf jeder Seite andeutet "
                    "oder sechs Beine zeichnet, hat alles richtig. Beschriftung ist ein Pluspunkt."),
    },
    "schwaenzeltanz": {
        "nr": 26,
        "titel": "Der Schwänzeltanz",
        "motiv": "Eine Sammlerin tanzt den Schwänzeltanz auf der senkrechten Wabe. Daneben steht die Sonne, und eine Linie zeigt die Richtung des Tanzes.",
        "merkmale": [
            "eine senkrechte Wabe (steht aufrecht wie eine Wand, mit Sechsecken oder Zellen)",
            "eine tanzende Biene auf der Wabe (die Tänzerin)",
            "die Sonne (ein Kreis, meist mit Strahlen)",
            "eine Richtungslinie: Sie zeigt, in welche Richtung die Tänzerin beim Tanzen läuft",
        ],
        "stufen": {
            "A": [],
            "B": ["der Schwänzellauf: ein gerader Weg, bei dem die Biene wackelt (zum Beispiel als Zickzacklinie)",
                  "eine senkrechte Hilfslinie nach oben, damit man sieht, wie schräg die Richtungslinie liegt"],
            "C": ["der Schwänzellauf: ein gerader Weg, bei dem die Biene wackelt (zum Beispiel als Zickzacklinie)",
                  "ein erkennbarer Winkel zwischen der Senkrechten und der Richtungslinie",
                  "eine Beschriftung oder Pfeile: Die Richtung des Tanzes zeigt den Weg, die Dauer des Schwänzelns zeigt, wie weit es ist"],
        },
        "hinweis": ("Skizze mit dem Finger, kein Kunstwerk. Wichtig ist, dass man Wabe, Tänzerin, Sonne und Richtung erkennt; "
                    "die Biene darf einfach sein (Körper, Kopf, Flügel). Die Bögen links und rechts, die zusammen wie eine Acht aussehen, "
                    "sind ein Pluspunkt, aber keine Pflicht. Beim Niveau A zählt der Schwänzellauf nicht als Pflicht."),
    },
    "bestaeubung": {
        "nr": 35,
        "titel": "Die Bestäubung",
        "motiv": "Eine Biene an einer Blüte: Pollen gelangt von Blüte zu Blüte, daraus wird eine Frucht.",
        "merkmale": [
            "eine Blüte mit Blütenblättern",
            "eine Biene an der Blüte (Körper und Flügel erkennbar)",
            "Pollen (gelbe Pünktchen oder gelbes Höschen am Hinterbein)",
            "eine Frucht, zum Beispiel ein Apfel",
        ],
        "stufen": {
            "A": [],
            "B": ["eine zweite Blüte", "ein Pfeil von der ersten zur zweiten Blüte (der Weg des Pollens)"],
            "C": ["eine zweite Blüte", "ein Pfeil von Blüte zu Blüte (der Weg des Pollens)",
                  "mindestens drei Teile beschriftet, zum Beispiel Pollen, Blüte, Frucht"],
        },
        "hinweis": ("Skizze mit dem Finger, kein Kunstwerk. Die Reihenfolge Biene mit Pollen, dann Blüte, dann Frucht soll erkennbar sein. "
                    "Beim Niveau A zählt der Pfeil nicht als Pflicht."),
    },
}


def auftrag_fuer(geraet: str) -> dict | None:
    """Zeichenauftrag zu einem Gerätenamen (None bei Unbekanntem, z. B. „handschrift“)."""
    return ZEICHENAUFTRAEGE.get(geraet)


def prompt_text(geraet: str, aufgabe_client: str = "", niveau: str = "") -> str:
    """Text für die KI: Motiv und Prüfliste vom Server, dazu der Aufgabentext des Clients.

    Der Client schickt den konkreten Auftrag des gewählten Niveaus mit; die Merkmale dieser Datei
    sind die verbindliche Prüfliste. So bewertet die KI immer nach derselben Liste.
    """
    a = auftrag_fuer(geraet)
    teile = []
    if a:
        merkmale = list(a["merkmale"]) + list((a.get("stufen") or {}).get(niveau or "", []))
        teile.append(f"Zeichnung: {a['titel']}. Motiv: {a['motiv']}")
        teile.append("Prüfliste (Merkmale): " + "; ".join(merkmale))
        if a.get("hinweis"):
            teile.append("Hinweis zur Bewertung: " + a["hinweis"])
    if aufgabe_client:
        teile.append("Auftragstext der Schülerin oder des Schülers: " + aufgabe_client)
    return "\n".join(teile) or "Zeichenauftrag unbekannt."
