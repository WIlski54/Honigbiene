"""Aufgabenplan und Pflichtlisten des Honigbienen-ABs (aus AB_KONZEPT.md) – die Checkliste der Inhalts-Agenten.

`tests/test_inhalte_struktur.py::test_inhalte_vollstaendig` prüft, ob alles davon geschrieben ist. Solange Inhalte
fehlen oder noch „PLATZHALTER“ enthalten, meldet der Test das als erwarteten Fehlschlag (xfail) mit einer Liste.
Wer bewusst vom Plan abweicht, ändert ihn hier und sagt es im Bericht.
"""

# Aufgabennummer → Typ: die Vereinigung aller TYPEN aus plan_<reiter>.py (dort pflegen die Inhalts-Agenten ihren Reiter).
# „T“ = Transfer. Die Reihenfolge der Stationen steht in STATIONEN derselben Dateien (config.ABSCHNITTE).
import plan_abschluss
import plan_koerper
import plan_nutzen
import plan_nutztier
import plan_volk

PLAENE = {"nutztier": plan_nutztier, "koerper": plan_koerper, "volk": plan_volk, "nutzen": plan_nutzen, "abschluss": plan_abschluss}
AUFGABEN_PLAN = {}
for _plan in PLAENE.values():
    AUFGABEN_PLAN.update(_plan.TYPEN)

# Typen des forschend-entwickelnden Ansatzes (docs/FORSCHEN.md, static/js/forschen.js)
FORSCH_NEU = {"vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch"}
# ALTE, weite Zählung (Forschen + Anwenden): wird von den test_inhalt_<reiter>.py der Inhalts-Agenten importiert – nicht mehr für die Quote benutzt.
FORSCHEN_TYPEN = {"vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "erkunden", "modellfinden", "film",
                  "filmmoment", "bildpunkte", "zeichnen"}
# EHRLICHE Zählung (Audit 4. Oktober 2026, Entscheidung 3): Forschen zählt nur, wo das Kind EVIDENZ sammelt (zählen, vergleichen, suchen, entscheiden am Material).
# bildpunkte (Benennen/Einordnen), erkunden, modellfinden, film und zeichnen sind Anwenden/Vokabeln und zählen nur mit `forschen: true` an der Aufgabe oder am Niveau;
# diagramm zählt nur mit `auswertung` (siehe forschen_pruefen.zaehlt_als_forschen).
ECHT_FORSCHEN_TYPEN = {"vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "filmmoment"}
ANWENDEN_TYPEN = {"bildpunkte", "erkunden", "modellfinden", "film", "zeichnen"}
# Reine Abfrage-/Sicherungsaufgaben (zählen nur ohne Sprachwerkstatt-Eyebrow)
ABFRAGE_TYPEN = {"mc", "luecke", "zuordnung", "sortierung", "blitz", "domino", "quellen"}
# Quoten je Reiter (Abschluss ausgenommen), siehe docs/FORSCHEN.md „Gewichtung“
QUOTE_FORSCHEN_MIN = 0.25                # Anteil echter Forschen-Stationen je Reiter (früher 50 % mit weiter Zählung); bleibt als Konstante erhalten (test_inhalt_<reiter>.py importieren sie)
MIN_FORSCHEN = {"nutztier": 0.25}        # Ausnahmen/Festlegungen je Reiter: der Einstiegsreiter „nutztier“ ist einfacher (25 %, keine Vermutungspflicht)
MIN_FORSCHEN_ANZAHL = {"koerper": 3, "volk": 3, "nutzen": 3}   # Reiter 2–4: mindestens 3 ECHTE Forschen-Stationen (ECHT_FORSCHEN_TYPEN)
# Reiter ohne Pflicht zu Forscherfrage/Prüfen/Erkenntnis: Dort steht der Wissensaufbau am Anfang (einfache Fragen mit Rückmeldung);
# vermutung/pruefen sind erlaubt, aber nicht verlangt. pruefen.vermutung muss trotzdem auf eine vorhandene vermutung.id zeigen.
# Regel dahinter: Eine Vermutung nur dort stellen, wo sie innerhalb des Reiters (in den folgenden Stationen) geprüft werden kann.
OHNE_VERMUTUNG = {"nutztier"}
QUOTE_ABFRAGE_MAX = 0.3
SPRACHWERKSTATT_MIN = 2
STATIONEN_MAX = 12                       # Standard je Reiter (inklusive Lesestrecke)
MAX_STATIONEN = {"volk": 13}             # Ausnahmen je Reiter: der Film-Reiter „volk“ darf 13 Stationen haben
STATIONEN_MAX_ABSCHLUSS = 6


def min_forschen(key: str) -> float:
    """Mindestanteil der Forschen-Stationen (ohne Lesestrecke) im Reiter: MIN_FORSCHEN[key], sonst 50 %."""
    return MIN_FORSCHEN.get(key, QUOTE_FORSCHEN_MIN)


def min_forschen_anzahl(key: str) -> int:
    """Mindestzahl echter Forschen-Stationen im Reiter (Reiter 2–4: 3, sonst 0)."""
    return MIN_FORSCHEN_ANZAHL.get(key, 0)


def vermutung_pflicht(key: str) -> bool:
    """Verlangt der Reiter eine Forscherfrage (vermutung) und ein Prüfen/einen Erkenntnissatz? Nicht in OHNE_VERMUTUNG."""
    return key not in OHNE_VERMUTUNG


def max_stationen(key: str) -> int:
    """Höchstzahl der Stationen (inklusive Lesestrecke) für einen Reiter: MAX_STATIONEN[key], sonst 12; Abschluss 6."""
    if key == "abschluss":
        return STATIONEN_MAX_ABSCHLUSS
    return MAX_STATIONEN.get(key, STATIONEN_MAX)


# Glossar (AB_KONZEPT.md): alle Begriffe müssen als Alias vorkommen; die fett markierten brauchen ein Bild.
GLOSSAR_PFLICHT = [
    "Nutztier", "Imker", "Bienenkasten", "Flugloch", "Wabe", "Rähmchen", "Brutraum", "Honigraum", "Bienenvolk",
    "Königin", "Arbeiterin", "Drohne", "Insekt", "Facettenauge", "Fühler", "Rüssel", "Honigmagen", "Honigblase",
    "Pollenkörbchen", "Pollenhöschen", "Stachel", "Nektar", "Pollen", "Bestäubung", "Larve", "Puppe",
    "Schwänzeltanz", "Wintertraube", "Varroa-Milbe", "Wachs", "Ammenbiene", "Sammlerin", "Wächterin", "Honig",
]
GLOSSAR_MIT_BILD = [
    "Bienenkasten", "Wabe", "Königin", "Drohne", "Facettenauge", "Honigmagen", "Pollenkörbchen", "Stachel",
    "Bestäubung", "Schwänzeltanz", "Wintertraube", "Varroa-Milbe",
]

# Schlüssel der Teile im 3D-Modell (AB_KONZEPT.md, „Das 3D-Modell im AB“)
MODELL_TEILE = {
    "kopf", "brust", "hinterleib", "fuehler", "facettenauge", "ruessel", "fluegel", "bein", "vorderbein", "mittelbein",
    "hinterbein", "pollenkoerbchen", "honigmagen", "darm", "herz", "gehirn", "flugmuskeln", "stachel", "luftsaecke",
}
MODELL_ANSICHTEN = {"gestalt", "situs", "explosion"}
MODELL_BLICKE = {"seite", "oben", "vorn", "hinten", "schraeg"}

# Aufgabentypen, die der Client kennt (static/js: aufgaben.js, bildpunkte.js, zeichnen.js, spiele.js, film.js, modell3d.js, forschen.js)
BEKANNTE_TYPEN = {
    "mc", "luecke", "zuordnung", "sortierung", "diagramm", "freitext", "notizen", "quellen", "transfer", "zeichnen",
    "blitz", "domino", "bildpunkte", "film", "filmmoment", "erkunden", "modellfinden",
    "vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch",
}
# Typen, die A/B/C verlangen (Differenzierung je Aufgabe). film, erkunden, notizen, quellen, forscherbuch dürfen einstufig sein.
DIFFERENZIERT = {
    "mc", "luecke", "zuordnung", "sortierung", "diagramm", "freitext", "transfer", "zeichnen", "blitz", "domino",
    "bildpunkte", "filmmoment", "modellfinden",
    "vermutung", "pruefen", "protokoll", "tabelle", "bildwahl",
}
# Typen ohne Tafel-Fassung (der Tafel-Adapter darf sie nicht anbieten)
OHNE_TAFEL = {
    "film", "filmmoment", "erkunden", "modellfinden", "bildpunkte", "zeichnen", "diagramm", "blitz", "domino",
    "quellen", "notizen", "transfer",
    "vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch",
}
