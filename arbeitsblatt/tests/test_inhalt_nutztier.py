"""Inhalte des Reiters „Nutztier Biene“ (forschend-entwickelnd: Stationen 41, 42, 3, 43, L1, 45, 46, 47, 7).

Geprüft wird nur, was dieser Reiter besitzt: plan_nutztier.py, static/js/inhalte_nutztier.js, lesen_nutztier.py, glossar_nutztier.py.
Die Schaubilder (nutztier-1 … nutztier-4, glossar-bienenkasten, imker-karte) zeichnet ein anderer Agent; die gemeinsamen
Tests in test_lesestrecke.py und test_inhalte_struktur.py prüfen, dass die Dateien vorhanden sind.
"""
import os
import re
import warnings

import pytest

import glossar
import glossar_nutztier
import lesen_nutztier
import plan_nutztier
from config import ABSCHNITTE
from inhalte_laden import ROOT, lade_inhalte
from plan import (ABFRAGE_TYPEN, AUFGABEN_PLAN, DIFFERENZIERT, FORSCHEN_TYPEN, QUOTE_ABFRAGE_MAX, SPRACHWERKSTATT_MIN,
                  max_stationen)

# Dieser Reiter hat keine Vermutungspflicht und nur Bilder als Forschungsinstrument: Forschen mindestens 25 % der Stationen
# (docs/FORSCHEN.md, Absprache mit dem Technik-Agenten; die gemeinsame Quote steht in tests/plan.py).
QUOTE_FORSCHEN_NUTZTIER = 0.25

STATIONEN = [41, 42, 3, 43, "L1", 45, 46, 47, 7]
NUMMERN = [n for n in STATIONEN if n != "L1"]
STRECKE = lesen_nutztier.LESESTRECKEN["nutztier"]
KONZEPT = os.path.join(os.path.dirname(ROOT), "AB_KONZEPT.md")

# Felder, die nur die KI oder die Technik lesen – Kinder sehen sie nicht
UEBERSPRINGEN = {"kontext", "kiFrage", "typ", "key", "film", "geraet", "modus", "mw", "icon", "kurz", "lese", "leseNach", "abschnitt",
                 "label", "bild", "bild_alt", "alt", "karte", "id", "x", "y", "aliase", "kat", "loesung", "multi"}

# Wörter, die für dieselbe Sache nicht verwendet werden dürfen (feste Wörter im Konzept, DaZ)
VERBOTEN = ["Bienenkorb", "Bienenhaus", "Honigblase", "Pollenhöschen", "Stockbiene", "Honigwabe", "Bienenkönigin",
            "Sammelbiene", "Wächterbiene"]

# Die Schätzfrage 42 nennt falsche Zahlen, die nicht im Konzept stehen – es sind Ablenker, keine Fakten.
SCHAETZ_ZAHLEN = {50, 500, 5000}

# Duden-Formen für Sprachwerkstatt 45 und 46
ARTIKEL = {"Biene": "die", "Imker": "der", "Volk": "das", "Wabe": "die", "Flügel": "der", "Bein": "das", "Kuh": "die", "Huhn": "das",
           "Schaf": "das", "Honig": "der", "Blüte": "die", "Bienen": "die",
           "Kasten": "der", "Glas": "das", "Kerze": "die", "Baum": "der", "Gerät": "das", "Loch": "das", "Magen": "der",
           "Körbchen": "das", "Raum": "der", "Wachs": "das", "Obst": "das", "Rauch": "der", "Brut": "die", "Pollen": "der", "Flug": "der"}
PLURAL = {"Biene": "Bienen", "Imker": "Imker", "Volk": "Völker", "Kuh": "Kühe", "Huhn": "Hühner", "Flügel": "Flügel"}
W_WOERTER = {"Wie", "Wie viele", "Wieviele", "Wer", "Warum", "Wieso", "Weshalb", "Wo", "Wann", "Was", "Wohin", "Woher"}
# Emoji vor Nomen (sprachschwache Lernende): Variation Selector und Zero Width Joiner mitzählen
EMOJI = r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u200d\ufe0f]+"


@pytest.fixture(scope="module")
def tab():
    return next(t for t in lade_inhalte()["tabs"] if t["key"] == "nutztier")


@pytest.fixture(scope="module")
def aufg(tab):
    return {a["nr"]: a for a in tab["aufgaben"]}


def _texte(obj):
    """Alle Texte, die Kinder sehen (rekursiv, ohne technische Felder)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from _texte(x)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in UEBERSPRINGEN:
                yield from _texte(v)


def _klar(text):
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\[([^\]|]+)(?:\|[^\]]*)?\]", r"\1", text)       # Lücke [Wort|Alias] → Wort


def _saetze(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", _klar(text)) if s.strip()]


def _woerter(s):
    return len(s.split())


def _alle_kindertexte(tab):
    texte = list(_texte(tab))
    for a in STRECKE["abschnitte"]:
        texte += [a["ueberschrift"], a["text"], a["frage"], a["erklaerung"], *a["optionen"]]
    texte += [e["text"] for e in glossar_nutztier.EINTRAEGE.values()]
    return texte


def _zahlen(text):
    ohne = re.sub(r"(Reiter|Lesestrecke|Kapitel|Szene|Abschnitt|Aufgabe) \d+", "", text)
    return {int(re.sub(r"\D", "", z)) for z in re.findall(r"\d+(?:[   ]\d{3})*", ohne)}


def _konzept_zahlen():
    if not os.path.exists(KONZEPT):
        pytest.skip("AB_KONZEPT.md liegt nicht neben dem Projekt")
    text = open(KONZEPT, encoding="utf-8").read()
    abschnitt = text.split("## Gesicherte Fakten", 1)[1].split("\n## ", 1)[0]
    return _zahlen(abschnitt)


def _luecken(cfg):
    return [m.split("|") for m in re.findall(r"\[([^\]]+)\]", cfg["text"])]


# ── Stationsplan, Reihenfolge, Quoten ───────────────────────────────────────────────────
def test_plan_und_reihenfolge(tab, aufg):
    abschnitt = next(a for a in ABSCHNITTE if a["key"] == "nutztier")
    assert plan_nutztier.STATIONEN == STATIONEN == abschnitt["aufgaben"]
    assert tab["label"] == "Nutztier Biene" and tab["kurz"] == "N" and tab["lese"] == "L1" and tab["leseNach"] == 43
    assert "film" not in tab, "Dieser Reiter hat weder Film noch 3D-Modell"
    assert [a["nr"] for a in tab["aufgaben"]] == NUMMERN
    for nr in NUMMERN:
        assert aufg[nr]["typ"] == AUFGABEN_PLAN[nr] == plan_nutztier.TYPEN[nr], f"Aufgabe {nr}"
        assert aufg[nr]["eyebrow"] and aufg[nr]["titel"]
        assert "modell" not in aufg[nr] and "film" not in aufg[nr], "keine Film-/Modell-Knöpfe in diesem Reiter"
    # Dramaturgie: zwei Einstiegsfragen mit sofortiger Rückmeldung, Lesestrecke erst nach dem Erkunden (Bild, Tabelle)
    assert STATIONEN[:2] == [41, 42] and aufg[41]["typ"] == aufg[42]["typ"] == "mc"
    i = STATIONEN.index("L1")
    assert i >= 3 and STATIONEN[i - 1] == 43 and 44 not in STATIONEN
    assert not [a for a in tab["aufgaben"] if a["typ"] in ("vermutung", "pruefen")], "keine Vermutungen und kein pruefen in diesem Reiter"


def test_quoten(tab):
    """docs/FORSCHEN.md, „Gewichtung“: Stationen ohne Lesestrecke; Sprachwerkstatt-Eyebrow zählt nicht als Abfrage."""
    stationen = tab["aufgaben"]
    n = len(stationen)
    assert n + 1 <= max_stationen("nutztier")
    sw = [a for a in stationen if a["eyebrow"].startswith("Sprachwerkstatt")]
    forschen = [a for a in stationen if a["typ"] in FORSCHEN_TYPEN and a not in sw]
    abfrage = [a for a in stationen if a["typ"] in ABFRAGE_TYPEN and a not in sw]
    assert len(forschen) / n >= QUOTE_FORSCHEN_NUTZTIER, (len(forschen), n)
    assert len(sw) >= SPRACHWERKSTATT_MIN and len(sw) / n <= 0.4, (len(sw), n)
    assert len(abfrage) / n <= QUOTE_ABFRAGE_MAX + 1e-9, (len(abfrage), n)
    assert [a["nr"] for a in forschen] == [3, 43] and [a["nr"] for a in abfrage] == [41, 42]
    assert [a["nr"] for a in sw] == [45, 46, 47]


def test_keine_platzhalter_mehr(tab):
    for text in _alle_kindertexte(tab):
        assert "PLATZHALTER" not in text.upper(), text[:60]
    assert "platzhalter" not in STRECKE
    for datei in (os.path.join(ROOT, "static", "js", "inhalte_nutztier.js"), lesen_nutztier.__file__, glossar_nutztier.__file__):
        # Das Notizen-Feld `platzhalter:` (Beispieltext im Eingabefeld, Gerüst T9) ist kein Platzhalter-Inhalt
        text = open(datei, encoding="utf-8").read().replace("platzhalter:", "").upper()
        assert "PLATZHALTER" not in text


def test_abc_wo_verlangt(aufg):
    for nr in NUMMERN:
        if aufg[nr]["typ"] in DIFFERENZIERT:
            assert sorted(aufg[nr]["niveaus"]) == ["A", "B", "C"], nr


# ── 41 und 42: Einstiegsfragen mit sofortiger Rückmeldung ──────────────────────────────
def test_einstieg_41_gaben(aufg):
    a = aufg[41]
    n = a["niveaus"]
    assert a["typ"] == "mc" and a["titel"] == "Was bekommen wir Menschen von Bienen?" and a["eyebrow"] == "Was weißt du schon?"
    assert [n[x].get("multi", 1) for x in "ABC"] == [1, 2, 3]
    assert [len(n[x]["optionen"]) for x in "ABC"] == [3, 5, 5]
    assert "Wähle ZWEI" in n["B"]["frage"] and "Wähle DREI" in n["C"]["frage"]
    richtig = {x: {o["t"] for o in n[x]["optionen"] if o["ok"]} for x in "ABC"}
    assert richtig["A"] == {"Honig"} and richtig["B"] == {"Honig", "Wachs für Kerzen"}
    # C: ganze Sätze, die Bestäubung ist eine Option (Entscheidung des Leiters: Reiter 1 behält sie hier)
    assert richtig["C"] == {"Sie machen Honig.", "Sie liefern Wachs für Kerzen.", "Sie tragen Pollen von Blüte zu Blüte (Bestäubung)."}
    falsch = {x: {o["t"] for o in n[x]["optionen"] if not o["ok"]} for x in "ABC"}
    assert falsch["B"] == {"Eier", "Milch", "Wolle"} and falsch["C"] == {"Sie geben Milch.", "Sie liefern Wolle."}
    assert falsch["A"] <= {"Milch", "Eier", "Wolle"}
    for niv, cfg in n.items():
        assert sum(o["ok"] for o in cfg["optionen"]) == cfg.get("multi", 1), niv
        assert all(_woerter(o["t"]) <= 12 for o in cfg["optionen"]), niv
        assert cfg["erklaerung"] == "Bienen geben uns Honig und Wachs. Sie tragen auch Pollen von Blüte zu Blüte, damit Früchte wachsen.", niv
        assert cfg["hilfe"] == "Das lernst du gleich noch genauer kennen.", f"{niv}: kein „gleich beim Imker“ und kein Lesehinweis"
    # Lösungspositionen gemischt: A nicht oben, B und C nicht die ersten beiden
    assert next(i for i, o in enumerate(n["A"]["optionen"]) if o["ok"]) != 0
    for niv in "BC":
        assert [i for i, o in enumerate(n[niv]["optionen"]) if o["ok"]] != [0, 1], niv
    assert "erkenntnis" not in a, "Nur Station 43 trägt einen Erkenntnissatz für das Forscherbuch"
    assert "zeigeLoesung" not in a, "Sofortige Rückmeldung: die richtige Antwort wird markiert"


def test_einstieg_42_schaetzfrage(aufg):
    a = aufg[42]
    n = a["niveaus"]
    assert a["typ"] == "mc" and a["eyebrow"] == "Schätzen" and "Bienenstock" in a["titel"], "Bienenstock = ganzes Zuhause des Volkes"
    assert [len(n[x]["optionen"]) for x in "ABC"] == [3, 4, 4]
    pos = []
    for niv, cfg in n.items():
        assert sum(o["ok"] for o in cfg["optionen"]) == 1 and "Schätze" in cfg["frage"], niv
        assert "Lesestrecke" not in cfg["hilfe"] + cfg["frage"]
        richtig = next(o["t"] for o in cfg["optionen"] if o["ok"])
        assert "50 000" in richtig, niv
        assert all(_woerter(o["t"]) <= 12 for o in cfg["optionen"]), niv
        # Auflösung: Sommer bis zu etwa 50 000, Winter etwa 10 000, Verweis auf den Film (mit dem Namen des Reiters)
        assert cfg["erklaerung"] == "Im Sommer bis zu etwa 50 000, im Winter etwa 10 000. Im Film im Reiter „Das Bienenvolk“ siehst du es.", niv
        pos.append(next(i for i, o in enumerate(cfg["optionen"]) if o["ok"]))
    assert len(set(pos)) == 3, f"Lösungsposition über A/B/C verteilen (nicht dreimal gleich): {pos}"
    # Alle Optionen im gleichen Format: in A und B nur „etwa <Zahl>“, die richtige sticht nicht durch ein „bis zu“ heraus
    for niv in "AB":
        assert all(re.fullmatch(r"etwa [\d ]+", o["t"]) for o in n[niv]["optionen"]), niv
    muster = r"Sommer etwa [\d ]+, Winter etwa [\d ]+"
    assert all(re.fullmatch(muster, o["t"]) for o in n["C"]["optionen"]), "C: Sommer-Winter-Paare im gleichen Muster"
    assert sorted(o["t"] for o in n["B"]["optionen"]) == sorted(["etwa 50", "etwa 500", "etwa 5 000", "etwa 50 000"])
    assert any(o["t"] == "Sommer etwa 10 000, Winter etwa 50 000" for o in n["C"]["optionen"]), "C: auch die umgekehrte Falle"
    assert "Winter" in n["C"]["frage"]
    assert "erkenntnis" not in a, "Nur Station 43 trägt einen Erkenntnissatz für das Forscherbuch"


# ── 3: Entdecken (bildwahl am Bild „Beim Imker“) ────────────────────────────────────────
# Umgebende Rechtecke der Objekte in imker-karte.svg (Pixel im Bild 900 × 560; Quelle werkzeuge/imker_karte_punkte.json)
OBJEKT = {"kasten": (578, 264, 745, 438), "imker": (217, 251, 379, 509), "bluete": (20, 441, 172, 540), "obstbaum": (27, 211, 177, 379),
          "rauch": (423, 315, 533, 510), "glas": (790, 400, 894, 527), "biene": (491, 95, 666, 213), "sonne": (716, 8, 884, 176),
          "wolke": (224, 9, 402, 120)}


def _objekt(z):
    """Name des Objekts, dessen Rechteck den Mittelpunkt des Zielkreises enthält (None, wenn keines)."""
    treffer = [n for n, (x0, y0, x1, y1) in OBJEKT.items() if x0 <= z["x"] <= x1 and y0 <= z["y"] <= y1]
    if not treffer:
        return None
    return min(treffer, key=lambda n: (z["x"] - (OBJEKT[n][0] + OBJEKT[n][2]) / 2) ** 2 + (z["y"] - (OBJEKT[n][1] + OBJEKT[n][3]) / 2) ** 2)


def test_bild_beim_imker_3(aufg):
    a = aufg[3]
    assert a["typ"] == "bildwahl" and a["eyebrow"] == "Entdecken" and a["titel"] == "Beim Imker: Was entdeckst du?"
    assert "erkenntnis" not in a, "Nur Station 43 trägt einen Erkenntnissatz für das Forscherbuch"
    assert os.path.exists(os.path.join(ROOT, "static", "img", "lese", "imker-karte.svg"))
    n = a["niveaus"]
    # Drei Runden je Niveau: Zuhause (Bienenkasten) → Futter (Blüten oder Obstbaum) → Wer kümmert sich (Imker)
    erwartet = [{"kasten"}, {"bluete", "obstbaum"}, {"imker"}]
    for niv, cfg in n.items():
        assert len(cfg["runden"]) == 3, niv
        for i, r in enumerate(cfg["runden"]):
            wer = f"{niv} Runde {i + 1}"
            assert r["bild"] == "/static/img/lese/imker-karte.svg" and (r["breite"], r["hoehe"]) == (900, 560), wer
            ziele = r["ziele"]
            assert {_objekt(z) for z in ziele if z["ok"]} == erwartet[i], f"{wer}: ok-Kreise liegen nicht auf den richtigen Objekten"
            assert all(_objekt(z) is not None for z in ziele), f"{wer}: ein Kreis liegt auf keinem Objekt"
            assert len({_objekt(z) for z in ziele}) == len(ziele), f"{wer}: zwei Kreise auf demselben Objekt"
            assert all(z["r"] >= 60 for z in ziele), f"{wer}: Touchziel zu klein"
            assert not all(z["ok"] for z in ziele) and not ziele[0]["ok"], f"{wer}: Lösung nicht gleich der erste Kreis"
            # Kreise dürfen sich nicht überdecken (sonst entscheidet der Zufall, was getippt wurde)
            for k, z in enumerate(ziele):
                for q in ziele[k + 1:]:
                    assert ((z["x"] - q["x"]) ** 2 + (z["y"] - q["y"]) ** 2) ** 0.5 >= z["r"] + q["r"] - 5, (wer, _objekt(z), _objekt(q))
            assert r["hinweis"] and r["erklaerung"] and len(r["frage"]) <= 150, wer
            # Der Hinweis lenkt, nennt aber nicht das gesuchte Objekt; falsche Tipps bekommen eine Rückmeldung ohne die Lösung
            gesucht = [["kasten"], ["blüte", "obstbaum", "baum"], ["imker"]][i]
            texte = [r["hinweis"]] + [z.get("rueckmeldung", "") for z in ziele if not z["ok"]]
            for t in texte:
                assert not any(g in t.lower() for g in gesucht), f"{wer}: verrät die Lösung: {t}"
        # Die erste Runde stellt die Situation vor (Du besuchst einen Imker …), alle Fragen sind Fragen oder Aufträge zum Tippen
        assert cfg["runden"][0]["frage"].startswith("Du besuchst einen Imker. Schau genau hin!"), niv
        assert all(("Tippe" in r["frage"]) for r in cfg["runden"]), niv
    # Differenzierung: A hat weniger Kreise als B, C die meisten (zusätzlich Sonne und Wolke als Ablenker)
    anzahl = {niv: [len(r["ziele"]) for r in cfg["runden"]] for niv, cfg in n.items()}
    assert all(x < y < z or x < y <= z for x, y, z in zip(anzahl["A"], anzahl["B"], anzahl["C"])), anzahl
    assert all(a_ < c_ for a_, c_ in zip(anzahl["A"], anzahl["C"])), anzahl
    assert sum(o["ok"] for o in n["A"]["runden"][1]["ziele"]) == 2 and sum(o["ok"] for o in n["C"]["runden"][1]["ziele"]) == 2
    assert {_objekt(z) for z in n["C"]["runden"][0]["ziele"]} >= {"sonne", "wolke", "kasten", "imker", "biene", "bluete", "obstbaum", "rauch", "glas"}
    # Bienenstock = ganzes Zuhause des Volkes: erst in C genannt, mit dem Unterschied zum Bienenkasten
    assert "Bienenstock" in n["C"]["runden"][0]["erklaerung"] and "Bienenstock" not in n["A"]["runden"][0]["erklaerung"]


# ── 43: Tabelle ─────────────────────────────────────────────────────────────────────────
def test_tabelle_43(aufg):
    a = aufg[43]
    assert a["typ"] == "tabelle" and a["auftrag"] and "Bild „Beim Imker“" in a["auftrag"]
    # Merksatz passt zu allen Niveaus: nur „frei“ und „Futter meist selbst“ (A hat keine „Imker kümmert sich“-Zeile)
    assert a["erkenntnis"] == "Die Honigbiene ist ein besonderes Nutztier: Sie lebt frei und sucht ihr Futter meist selbst."
    n = a["niveaus"]
    assert [len(n[x]["spalten"]) for x in "ABC"] == [3, 4, 4]
    assert [len(n[x]["zeilen"]) for x in "ABC"] == [3, 3, 4]

    def namen(cfg):
        return [sp["name"] for sp in cfg["spalten"]]
    # Die Biene steht in der Mitte (Audit: sonst löst sich die Tabelle über die Diagonale)
    assert namen(n["A"]) == ["Kuh", "Biene", "Huhn"] and namen(n["B"]) == namen(n["C"]) == ["Kuh", "Biene", "Huhn", "Schaf"]
    # Spaltenköpfe mit Bild (sprachschwache Lernende): Datei, Alternativtext; die Grafik-Agentin zeichnet tier-*.svg
    for cfg in n.values():
        for sp in cfg["spalten"]:
            assert sp["alt"] == sp["name"] and sp["bild"] == f"/static/img/lese/tier-{sp['name'].lower()}.svg", sp
    fehlt = [sp["bild"] for sp in n["C"]["spalten"] if not os.path.exists(os.path.join(ROOT, sp["bild"].lstrip("/")))]
    assert not fehlt, f"Tierbilder fehlen: {fehlt}"
    futter, ort = "Wer sorgt für das Futter?", "Wo ist das Tier tagsüber?"
    for niv, cfg in n.items():
        zeilen = {z["merkmal"]: z for z in cfg["zeilen"]}
        assert [z["merkmal"] for z in cfg["zeilen"]][:2] == [futter, ort], niv
        for z in cfg["zeilen"]:
            wer = f"{niv}: {z['merkmal']}"
            assert len(z["loesung"]) == len(cfg["spalten"]), wer
            assert all(0 <= i < len(z["optionen"]) for i in z["loesung"]), wer
            assert len(set(z["loesung"])) >= 2, f"{wer}: eine Zeile, in der überall dasselbe steht, vergleicht nichts"
            assert len(set(z["optionen"])) == len(z["optionen"]) and all(_woerter(o) <= 8 for o in z["optionen"]), wer
            # Der Hinweis lenkt auf ein Merkmal, nennt aber keine Antwort der Zeile
            assert z["hinweis"] and not any(o.lower() in z["hinweis"].lower() for o in z["optionen"]), f"{wer}: Hinweis nennt die Antwort"
        # Neutral und symmetrisch: „meist“ in beiden Antworten, dritte Option „Beides gleich oft.“ in den Zeilen Futter und Ort
        for name in (futter, ort):
            ops = zeilen[name]["optionen"]
            assert len(ops) == 3 and "Beides gleich oft." in ops, f"{niv}: {name}"
            assert sum("meist" in o.lower() for o in ops) == 2, f"{niv}: {name}: beide echten Antworten sagen „meist“"
        assert not any(w in " ".join(z["optionen"]).lower() for z in cfg["zeilen"] for w in ("fliegt", "niemand – es sucht", "muss")), niv
        # Die Biene ist in Futter und Ort die „andere“ Spalte, steht aber nicht immer an derselben Optionsstelle wie die Kuh
        b = namen(cfg).index("Biene")
        for name in (futter, ort):
            assert zeilen[name]["loesung"][b] != zeilen[name]["loesung"][0], f"{niv}: {name}"
    # Antworten nicht in Spaltenreihenfolge: Optionsreihenfolge je Zeile gemischt (keine Diagonale)
    for niv, cfg in n.items():
        for z in cfg["zeilen"]:
            assert z["loesung"] != sorted(z["loesung"]) or len(set(z["loesung"])) < len(z["loesung"]), f"{niv}: {z['merkmal']}: Diagonale"
        produkte = next(z for z in cfg["zeilen"] if z["merkmal"] == "Was gibt es uns vor allem?")
        ops = produkte["optionen"]
        erwartet = {"Kuh": "🥛 Milch", "Biene": "🍯 Honig", "Huhn": "🥚 Eier", "Schaf": "🧶 Wolle"}
        for sp, i in zip(namen(cfg), produkte["loesung"]):
            assert ops[i] == erwartet[sp], f"{niv}: {sp}"
        assert sorted(ops) == sorted(erwartet[x] for x in namen(cfg)), niv      # jede Antwort genau einmal
    # „Wer kümmert sich?“ nur in C, mit neutralen Optionen (auch „niemand“)
    assert not any(z["merkmal"].startswith("Wer kümmert") for z in n["A"]["zeilen"] + n["B"]["zeilen"])
    kuemmern = next(z for z in n["C"]["zeilen"] if z["merkmal"] == "Wer kümmert sich um das Tier?")
    assert sorted(kuemmern["optionen"]) == ["der Bauer", "der Imker", "niemand"]
    assert [kuemmern["optionen"][i] for i in kuemmern["loesung"]] == ["der Bauer", "der Imker", "der Bauer", "der Bauer"]
    # Hinweis zur Futterzeile: Beobachtung am Bild statt „muss fliegen“
    assert "Siehst du im Bild irgendwo Futter für die Biene?" in n["A"]["zeilen"][0]["hinweis"]


# ── 45–47: Sprachwerkstatt ──────────────────────────────────────────────────────────────
def test_sprachwerkstatt_eyebrow(aufg):
    for nr in (45, 46, 47):
        assert aufg[nr]["eyebrow"].startswith("Sprachwerkstatt ·"), nr
        assert aufg[nr]["typ"] == "luecke", "Sprachwerkstatt 45–47: Lückentext mit Chips bzw. Tippen"


def test_sprachwerkstatt_45_artikel_und_plural(aufg):
    a = aufg[45]
    n = a["niveaus"]
    assert "Die Biene – die Bienen" not in a["titel"], "Das Titelbeispiel darf nicht die erste Lösung sein"
    assert [n[x]["modus"] for x in "ABC"] == ["chips", "chips", "input"]
    assert all(n[x]["hilfe"] and "Lesestrecke" not in n[x]["hilfe"] for x in "ABC")
    # A: „Das ist [die] 🐝 Biene.“ (Emoji am Nomen)
    treffer = re.findall(rf"Das ist \[(der|die|das)\] ({EMOJI}) (\w+)\.", n["A"]["text"])
    assert len(treffer) == len(_luecken(n["A"])) >= 6
    for art, _, nomen in treffer:
        assert ARTIKEL[nomen] == art, f"{art} {nomen}"
    assert {t[0] for t in treffer} == {"der", "die", "das"}
    # B: „🐝 Eine Biene – viele [Bienen].“ Keine falschen Formen in der Wortkiste (kein Ablenker)
    assert not n["B"].get("ablenker")
    paare = re.findall(r"(?:Ein|Eine) (\w+) – viele \[(\w+)\]\.", n["B"]["text"])
    assert len(paare) == len(_luecken(n["B"])) >= 5
    for nomen, plural in paare:
        assert PLURAL[nomen] == plural, f"{nomen} → {plural}"
        assert (ARTIKEL[nomen] == "die") == bool(re.search(rf"Eine {nomen} ", n["B"]["text"])), f"Ein/Eine bei {nomen}"
    # C: „Die Biene – die [Bienen].“ Der Artikel „die“ steht schon da, geprüft wird nur die Pluralform (Umlaut-Varianten gelten)
    zeilen = re.findall(r"(Der|Die|Das) (\w+) – die \[([^\]]+)\]\.", n["C"]["text"])
    assert len(zeilen) == len(_luecken(n["C"])) >= 6
    for art, nomen, antw in zeilen:
        assert ARTIKEL[nomen] == art.lower(), f"{art} {nomen}"
        haupt, *alias = antw.split("|")
        assert haupt == PLURAL[nomen], f"{nomen}: {antw}"
        if any(ch in haupt for ch in "äöü"):
            assert any("ue" in x or "ae" in x or "oe" in x for x in alias) and any(not re.search("[äöü]", x) for x in alias), f"{nomen}: Umlaut-Varianten fehlen"
    assert {a for a, _, _ in zeilen} == {"Der", "Die", "Das"}


def test_sprachwerkstatt_46_zusammengesetzte_woerter(aufg):
    a = aufg[46]
    n = a["niveaus"]
    assert a["typ"] == "luecke" and "letzte Wort" in a["titel"]
    assert [n[x]["modus"] for x in "ABC"] == ["chips", "chips", "input"]
    assert all(n[x]["hilfe"] and "Lesestrecke" not in n[x]["hilfe"] and "Wort ganz rechts" in n[x]["hilfe"] for x in "ABC")
    gesamt = []
    # A: „der Honig + das Glas → [das] Honigglas.“ (Artikel beider Teile stehen da)
    teile_a = re.findall(r"(der|die|das) (\w+) \+ (der|die|das) (\w+) → \[(der|die|das)\] (\w+)\.", n["A"]["text"])
    assert len(teile_a) == len(_luecken(n["A"])) >= 5
    for a1, w1, a2, w2, art, wort in teile_a:
        assert ARTIKEL[w1] == a1 and ARTIKEL[w2] == a2, (w1, w2)
        assert wort.lower() == (w1[:-1] if w1 == "Bienen" and False else w1).lower() + w2.lower() or wort == w1 + w2.lower(), wort
        assert art == a2, f"{wort}: das letzte Wort bestimmt den Artikel"
        gesamt.append(wort)
    # B/C: nur die Wörter, der Artikel kommt vom letzten Wort
    for niv in "BC":
        zeilen = re.findall(r"(\w+) \+ (\w+) → \[(der|die|das)\] (\w+)\.", n[niv]["text"])
        assert len(zeilen) == len(_luecken(n[niv])) >= 5, niv
        for w1, w2, art, wort in zeilen:
            assert wort == w1 + w2.lower(), f"{w1} + {w2} → {wort}"
            assert ARTIKEL[w2] == art, f"{wort}: Artikel von {w2}"
            gesamt.append(wort)
    assert len(_luecken(n["B"])) >= len(_luecken(n["A"]))
    # Die Wörter stehen im AB (feste Wörter)
    for w in ("Bienenkasten", "Flugloch", "Honigmagen", "Pollenkörbchen", "Honigraum", "Bienenvolk", "Brutraum"):
        assert w in gesamt, w
    # Keine Artikel-Kiste mit Unsinn: nur der, die, das; C wird getippt (alle drei Artikel kommen vor)
    assert {l[0] for l in _luecken(n["B"])} == {"der", "die", "das"} and {l[0] for l in _luecken(n["C"])} == {"der", "die", "das"}


def test_sprachwerkstatt_47_fragen_stellen(aufg):
    n = aufg[47]["niveaus"]
    assert [n[x]["modus"] for x in "ABC"] == ["chips", "input", "input"]
    assert all(n[x]["hilfe"] and "Lesestrecke" not in n[x]["hilfe"] for x in "ABC")
    for niv, cfg in n.items():
        woerter = [l[0] for l in _luecken(cfg)]
        assert all(w in W_WOERTER for w in woerter), (niv, woerter)
        assert len(woerter) >= 4
        # Jede Frage hat einen Antwortsatz davor (Audit: sonst werden gültige Fragen als falsch gewertet)
        assert cfg["text"].count("Antwort:") == cfg["text"].count("Frage:") == len(woerter), niv
        for frage in re.findall(r"Frage: (.*?)(?= Antwort:|$)", cfg["text"]):
            assert frage.endswith("?"), (niv, frage)
    a = _luecken(n["A"])
    assert len({l[0] for l in a}) == len(a), "A: jedes W-Wort nur einmal (Wortkiste)"
    assert not set(n["A"]["ablenker"]) & {l[0] for l in a}
    assert "Wann" not in n["A"]["ablenker"], "„Wann“ ergäbe in A eine zweite gültige Frage"
    assert {l[0] for l in a} == {"Wo", "Wer", "Was", "Wie viele"}
    # Verschiedene Antworttypen (Ort, Person, Sache, Menge, Herkunft, Zeit, Grund, Richtung) über die Niveaus
    alle = {l[0] for x in "ABC" for l in _luecken(n[x])}
    assert {"Wo", "Wer", "Was", "Wie viele", "Woher", "Wann", "Warum", "Wohin"} <= alle
    # Warum darf auch Wieso/Weshalb heißen, Wie viele auch Wieviele
    for niv in "BC":
        for l in _luecken(n[niv]):
            if l[0] == "Warum":
                assert set(l) == {"Warum", "Wieso", "Weshalb"}
    for niv in "ABC":
        for l in _luecken(n[niv]):
            if l[0] == "Wie viele":
                assert set(l) == {"Wie viele", "Wieviele"}
    # Antwortsätze verraten nichts aus den Reitern „Die Biene“ und „Das Bienenvolk“
    for cfg in n.values():
        t = cfg["text"].lower()
        assert "königin legt" not in t and "sechs" not in t and not re.search(r"\d", t)
    assert "Die Bienen sammeln Nektar" in n["C"]["text"]


def test_notizen_7(aufg):
    n = aufg[7]
    assert n["abschnitt"] == "nutztier" and n["titel"] == "Meine Fragen an einen Imker" and n["eyebrow"] == "Fragen sammeln"
    assert "mindestens drei" in n["hinweis"]
    assert all(w in n["hinweis"] for w in ("Wie", "Was", "Warum", "Wo", "Wer")), "W-Wörter aus Aufgabe 47 wieder aufgreifen"
    assert "Im 3D-Modell, im Film und in den Lesestrecken findest du vielleicht Antworten. Am Ende prüfst du, welche Fragen beantwortet sind." in n["hinweis"]
    assert n["kiFrage"] and "Klasse 6" in n["kiFrage"]
    assert n["quelleNoetig"] is False and n["platzhalter"].startswith("• Wie viele")
    assert "Quelle" not in n["hinweis"], "Die Quelle ist freiwillig (quelleNoetig: false), der Hinweis verlangt sie nicht"


# ── Lesestrecke (nachschlagen) ──────────────────────────────────────────────────────────
def test_lesestrecke_aufbau():
    assert STRECKE["station"] == "L1" and STRECKE["eyebrow"] == "Lesestrecke 1" and not STRECKE.get("platzhalter")
    assert STRECKE["titel"] == "Eine Biene als Nutztier"
    ab = STRECKE["abschnitte"]
    assert [a["ueberschrift"] for a in ab] == ["Nutztiere helfen uns", "Die Biene ist anders", "Was die Biene uns gibt", "Der Imker kümmert sich"]
    assert [a["bild"] for a in ab] == [f"nutztier-{i}" for i in range(1, 5)]
    for a in ab:
        assert a["bild_alt"].startswith("Schaubild:")
        assert 2 <= len(a["text"].split("\n")) <= 4, a["ueberschrift"]
        assert len(a["optionen"]) == 3 and len(set(a["optionen"])) == 3 and 0 <= a["loesung"] < 3
        assert a["frage"].endswith("?") and a["erklaerung"].startswith("Richtig")
        assert all(_woerter(o) <= 12 for o in a["optionen"])
        for satz in _saetze(a["text"]):
            assert _woerter(satz) <= 15, f"{a['ueberschrift']}: {_woerter(satz)} Wörter: {satz}"


def test_lesestrecke_loesungspositionen_verteilt():
    pos = [a["loesung"] for a in STRECKE["abschnitte"]]
    assert len(set(pos)) == 3, pos
    assert all(pos.count(p) <= 2 for p in (0, 1, 2)), pos


def test_lesestrecke_nimmt_bezug_auf_das_erforschte():
    """Nachschlagen: bestätigt und erweitert (Bezug auf Tabelle, erste Frage und Bild beim Imker; neues Wissen: Sammelflug)."""
    s1, s2, s3, s4 = [a["text"] for a in STRECKE["abschnitte"]]
    assert "Tabelle" in s2 and "erste Frage" in s3 and "beim Imker" in s4
    assert "Du kennst" in s1
    assert "meist selbst" in s2 and "etwa 3 Kilometer" in s2, "Abschnitt 2 ergänzt den Sammelflug (meist bis etwa 3 km) und sagt „meist“"
    assert "niemand füttert" not in s2.lower()


def test_frage_laesst_sich_aus_dem_abschnitt_beantworten():
    """Das Wort der richtigen Antwort steht im Text des Abschnitts (mindestens ein Inhaltswort)."""
    for a in STRECKE["abschnitte"]:
        text = _klar(a["text"]).lower()
        richtig = a["optionen"][a["loesung"]].lower()
        inhalt = [w for w in re.findall(r"[a-zäöüß]{5,}", richtig)]
        assert any(w[:6] in text for w in inhalt), f"{a['ueberschrift']}: Antwort „{richtig}“ steht nicht im Text"
        for i, o in enumerate(a["optionen"]):
            if i != a["loesung"]:
                assert o.lower().rstrip(".") not in text, f"{a['ueberschrift']}: falsche Option steht im Text"


def test_lesestrecke_inhalt_nach_konzept():
    ab = {a["ueberschrift"]: a["text"] for a in STRECKE["abschnitte"]}
    s1, s2, s3, s4 = ab.values()
    for wort in ("Milch", "Fleisch", "Eier", "Wolle", "<strong>Nutztiere</strong>"):
        assert wort in s1, wort
    assert "lebt frei" in s2 and "Futter meist selbst" in s2 and "<strong>Imker</strong>" in s2 and "<strong>Bienenkasten</strong>" in s2
    assert "<strong>Honig</strong>" in s3 and "<strong>Wachs</strong>" in s3 and "Kerzen" in s3 and "<strong>Bestäubung</strong>" in s3
    assert "kontrolliert" in s4 and "nur einen Teil des Honigs" in s4 and "Krankheiten" in s4
    assert _zahlen(" ".join(ab.values())) == {3}, "Im Text steht nur „etwa 3 Kilometer“ (Sammelflug meist bis etwa 3 km, Konzept)"


def test_lesestrecke_kommt_beim_server_an(student):
    r = student.get("/api/lesestrecke/nutztier").get_json()
    assert r["ok"] and r["anzahl"] == 4 and r["titel"] == "Eine Biene als Nutztier"
    for a in r["abschnitte"]:
        assert "loesung" not in a and "erklaerung" not in a and len(a["optionen"]) == 3


# ── Glossar ─────────────────────────────────────────────────────────────────────────────
def test_glossar_eintraege():
    e = glossar_nutztier.EINTRAEGE
    assert set(e) == {"nutztier", "imker", "bienenkasten", "honig"}
    assert e["bienenkasten"]["bild"] == "glossar-bienenkasten"
    assert {"Imkerin", "Bienenkästen", "Beute"} <= set(e["imker"]["aliase"]) | set(e["bienenkasten"]["aliase"])
    for key, eintrag in e.items():
        assert re.fullmatch(r"[a-z0-9]+", key)
        assert len(eintrag["text"]) <= 400, key
        assert 2 <= len(_saetze(eintrag["text"])) <= 4, key
        for satz in _saetze(eintrag["text"]):
            assert _woerter(satz) <= 18, (key, satz)
    for key, eintrag in e.items():
        assert glossar.GLOSSAR[key] is eintrag
        for alias in eintrag["aliase"] + [eintrag["titel"]]:
            assert glossar.ALIASE[glossar.normalisieren(alias)] == key, alias
    for begriff in ("Nutztier", "Imker", "Bienenkasten", "Honig"):
        assert glossar.eintrag_fuer(begriff) is not None, begriff


def test_fette_begriffe_haben_glossareintrag(tab):
    fett = set()
    for a in STRECKE["abschnitte"]:
        fett |= set(re.findall(r"<strong>(.*?)</strong>", a["text"]))
    assert fett == {"Nutztiere", "Imker", "Bienenkasten", "Honig", "Wachs", "Bestäubung", "Bienenvolk"}
    for begriff in fett:
        assert glossar.eintrag_fuer(begriff) is not None, f"Glossar-Eintrag fehlt: {begriff}"
    for begriff in tab["intro"]["begriffe"]:
        assert glossar.eintrag_fuer(begriff) is not None, f"Fachbegriff {begriff} ohne Glossareintrag"
    assert "<strong>" not in str(tab["aufgaben"]), "Aufgaben haben kein HTML"


def test_glossar_stimmt_mit_den_nachbarreitern_ueberein():
    """Bienenstock = ganzes Zuhause, Bienenkasten = Holzkiste des Imkers (feste Wörter)."""
    kasten = glossar_nutztier.EINTRAEGE["bienenkasten"]["text"]
    assert "Holzkiste" in kasten and "Bienenstock" in kasten
    honig = glossar_nutztier.EINTRAEGE["honig"]["text"]
    assert "Winter" in honig and "nur einen Teil" in honig


# ── Sprache, feste Wörter, Zahlen ───────────────────────────────────────────────────────
def test_saetze_sind_kurz(tab):
    zu_lang = []
    for text in _alle_kindertexte(tab):
        for satz in _saetze(text):
            if _woerter(satz) > 18:
                zu_lang.append((_woerter(satz), satz[:80]))
    assert not zu_lang, zu_lang


def test_optionen_kurz(aufg):
    for nr in (41, 42):
        for niv, cfg in aufg[nr]["niveaus"].items():
            assert all(_woerter(o["t"]) <= 12 for o in cfg["optionen"]), (nr, niv)


def test_keine_vermutung_und_keine_aufgabennummer_im_kindertext(tab):
    """Der Reiter kennt keine Vermutungen mehr; Aufgabennummern werden vom Gerüst angezeigt (fortlaufend) und stehen in keinem Text."""
    for text in _alle_kindertexte(tab):
        assert "vermut" not in text.lower(), f"„Vermutung“ im Kindertext: {text[:70]}"
        assert not re.search(r"(Aufgabe|Station|Nr[.]?) ?\d+", text), f"Aufgabennummer im Kindertext: {text[:70]}"
    for a in STRECKE["abschnitte"]:
        assert "vermut" not in (a["text"] + a["frage"] + a["erklaerung"]).lower()


def test_feste_woerter_statt_synonyme(tab):
    ganz = " ".join(_alle_kindertexte(tab))
    for w in VERBOTEN:
        assert w.lower() not in ganz.lower(), f"„{w}“ statt des festen Worts"
    assert not re.search(r"Imker[^.]{0,40}Bienenstock", ganz), "Der Imker arbeitet am Bienenkasten, nicht am Bienenstock"
    # Kuh, Huhn, Schaf: im ganzen Reiter dasselbe Wort (nicht mal „Rind“, mal „Kuh“)
    assert not re.search(r"\bRind(er)?\b", ganz), "„Kuh“ statt „Rind“ in diesem Reiter"


def test_jede_zahl_steht_im_konzept(tab, aufg):
    erlaubt = _konzept_zahlen()
    for nr, a in aufg.items():
        extra = SCHAETZ_ZAHLEN if nr == 42 else set()
        for text in _texte(a):
            fremd = _zahlen(text) - erlaubt - extra
            assert not fremd, f"Aufgabe {nr}: Zahl {fremd} steht nicht im Konzept: {text[:70]}"
    for text in [e["text"] for e in glossar_nutztier.EINTRAEGE.values()]:
        assert not (_zahlen(text) - erlaubt), text
    for a in STRECKE["abschnitte"]:
        for text in (a["text"], a["frage"], a["erklaerung"], *a["optionen"]):
            assert not (_zahlen(text) - erlaubt), text
    assert 50000 in erlaubt and 10000 in erlaubt
