"""Inhalte des Reiters „Die Biene“ (koerper): forschend-entwickelnd, Stationsplan plan_koerper.py, Lesestrecke L2, Glossar, Zeichenauftrag.

Stand nach dem Audit vom 4. Oktober 2026 (docs/AUDIT_FORSCHEN_2026-10-04.md): Station 9 steht hinter 52, `pruefen` hat gleich gebaute und
ähnlich lange Optionen, jede Prüfung `erkenntnis.hinweis` und eine neutrale `quelle`, die Tabelle 54 hat nur eindeutig zuordenbare Organe
mit Pflicht-Knöpfen, die Film-Knöpfe springen auf Sekunden.

Geprüft werden: Plan (Reihenfolge, Typen, A/B/C), der Ablauf (Forscherfrage zuerst, Lesestrecke nach der Forschungsphase), die Quoten
(echte Forschen-Stationen, Sprachwerkstatt, Abfrage, höchstens 12 Stationen), die neuen Typen (vermutung, pruefen, protokoll, tabelle),
Sprache (Satzlängen, feste Wörter), Lösungspositionen, Glossar-Deckung der fetten Begriffe, Zahlen aus dem Konzept und die Modell-Knöpfe
(nur bekannte Teile, Ansichten und Befehle; Innenteile nur ab „situs“). Hinweise und Knopftexte verraten keine Lösung.
Die Browserprüfung mit dem echten 3D-Modell steht im Bericht der Inhalts-Agentin, nicht hier.
"""
import json
import os
import re

import pytest

import glossar
import lesen_koerper
import plan_koerper
import zeichenauftraege
from config import ABSCHNITTE
from inhalte_laden import ROOT, lade_inhalte
from plan import (ABFRAGE_TYPEN, AUFGABEN_PLAN, DIFFERENZIERT, ECHT_FORSCHEN_TYPEN, MIN_FORSCHEN_ANZAHL, MODELL_ANSICHTEN, MODELL_BLICKE,
                  MODELL_TEILE, QUOTE_ABFRAGE_MAX, QUOTE_FORSCHEN_MIN, SPRACHWERKSTATT_MIN, STATIONEN_MAX)

STATIONEN = plan_koerper.STATIONEN
NUMMERN = [n for n in STATIONEN if not str(n).startswith("L")]
INNENTEILE = {"honigmagen", "darm", "herz", "gehirn", "flugmuskeln", "stachel", "luftsaecke"}
MODELL_BEFEHLE = {"ansicht", "blick", "hervorheben", "beschriften", "nummern", "waehlen", "zurueck", "spielen", "anhalten", "fokus"}
FILM_BEFEHLE = {"springe", "kapitel", "spielen", "anhalten"}
GLOSSAR_SCHLUESSEL = ["insekt", "facettenauge", "fuehler", "ruessel", "honigmagen", "pollenkoerbchen", "stachel", "nektar",
                      "pollen", "flugmuskeln"]
GLOSSAR_BILDER = {"facettenauge": "glossar-facettenauge", "honigmagen": "glossar-honigmagen",
                  "pollenkoerbchen": "glossar-pollenkoerbchen", "stachel": "glossar-stachel"}
# Synonyme, die es im AB nicht geben soll (feste Wörter des Konzepts, DaZ: dieselben Wörter in AB, Film und Modell)
VERBOTEN = [r"\bAntenne", r"Saugrüssel", r"Brustkorb", r"Hinterteil", r"Hinterkörper", r"Bienenkorb", r"Pollenhose",
            r"Nektarmagen", r"Flugmuskulatur", r"\bStock\b", r"\bStöcke", r"Facettenaugen?s?-?Auge", r"Körbchen\b(?<!Pollenkörbchen)"]
# Mehrzahlformen nach Duden – nur diese Paare dürfen in der Sprachwerkstatt „Einzahl und Mehrzahl“ vorkommen
PLURAL_DUDEN = {
    "die Biene": "die Bienen", "der Kopf": "die Köpfe", "das Bein": "die Beine", "der Flügel": "die Flügel",
    "das Auge": "die Augen", "der Fühler": "die Fühler", "der Hinterleib": "die Hinterleiber", "der Stachel": "die Stacheln",
    "das Facettenauge": "die Facettenaugen", "der Rüssel": "die Rüssel", "das Pollenkörbchen": "die Pollenkörbchen",
    "das Insekt": "die Insekten", "der Körperteil": "die Körperteile",
}
# Zahlwörter, die eine Lösung verraten würden, wenn sie im Hinweis stünden
ZAHLWOERTER = {2: "zwei", 3: "drei", 4: "vier", 6: "sechs"}
SIGNALWOERTER = ("Zuerst", "Dann", "Danach", "Anschließend", "Schließlich", "Später")


@pytest.fixture(scope="module")
def tab():
    inh = lade_inhalte()
    return next(t for t in inh["tabs"] if t["key"] == "koerper"), inh


@pytest.fixture(scope="module")
def aufgaben(tab):
    return {a["nr"]: a for a in tab[0]["aufgaben"]}


def _klartext(text):
    return re.sub(r"<[^>]+>", "", str(text)).replace(" ", " ")


def _saetze(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", _klartext(text)) if s.strip()]


SCHLUESSEL_OHNE_TEXT = {"typ", "film", "teil", "geraet", "abschnitt", "mw", "name", "modus", "ansicht", "blick", "links", "rechts",
                        "kiFrage", "id", "vermutung", "art"}


def _alle_texte(aufgabe):
    """Alle Lesetexte einer Aufgabe (Fragen, Aufträge, Hinweise, Optionen, Paare, Items, Lückentexte, Knopf-Texte)."""
    out = []

    def lauf(x, schluessel=""):
        if isinstance(x, str):
            if schluessel not in SCHLUESSEL_OHNE_TEXT:
                out.append(x)
        elif isinstance(x, list):
            for y in x:
                lauf(y, schluessel)
        elif isinstance(x, dict):
            for k, v in x.items():
                lauf(v, k)

    lauf(aufgabe)
    return out


def _alle_aufgaben_texte(tab):
    return [(a["nr"], t) for a in tab[0]["aufgaben"] for t in _alle_texte(a)]


def _liste(m):
    return m if isinstance(m, list) else [m] if m else []


def _knoepfe(a):
    return _liste(a.get("modell"))


def _alle_knoepfe(a):
    """Knöpfe der Aufgabe und der Zeilen eines Forscherbogens."""
    out = list(_knoepfe(a))
    for cfg in (a.get("niveaus") or {}).values():
        for z in cfg.get("zeilen", []) if isinstance(cfg.get("zeilen"), list) else []:
            out += _liste(z.get("modell"))
    return out


def _optionstexte(opts):
    return [o["t"] if isinstance(o, dict) else o for o in opts]


# ── Plan und Ablauf ───────────────────────────────────────────────────────────
def test_aufgaben_stehen_in_der_reihenfolge_des_plans(tab, aufgaben):
    assert [a["nr"] for a in tab[0]["aufgaben"]] == NUMMERN
    assert STATIONEN == [50, 8, 51, 52, 9, 53, 54, 55, "L2", 56, 57, 15]
    assert set(plan_koerper.TYPEN) == set(NUMMERN)
    for nr, a in aufgaben.items():
        assert a["typ"] == AUFGABEN_PLAN[nr] == plan_koerper.TYPEN[nr], f"Aufgabe {nr}: {a['typ']} statt {plan_koerper.TYPEN[nr]}"
        assert a["eyebrow"] and a["titel"], nr
    assert all(50 <= n <= 59 or n in (8, 9, 15) for n in NUMMERN), "neue Nummern gehören in den Bereich 50–59"


def test_reiter_metadaten_und_lesestrecke_nach_der_forschung(tab):
    t = tab[0]
    assert (t["label"], t["kurz"], t["lese"], t["film"]) == ("Die Biene", "B", "L2", "biene3d")
    assert t["intro"]["titel"] == lesen_koerper.LESESTRECKEN["koerper"]["titel"]
    for b in t["intro"]["begriffe"]:
        assert glossar.eintrag_fuer(b) is not None, f"Fachbegriff {b} ohne Glossareintrag"
    i = STATIONEN.index("L2")
    assert i > 0 and t["leseNach"] == STATIONEN[i - 1], "leseNach muss die Station vor der Lesestrecke nennen"
    assert t["leseNach"] == 55


def test_reiter_beginnt_mit_forscherfrage_und_schliesst_forschung_mit_pruefen(aufgaben):
    assert aufgaben[STATIONEN[0]]["typ"] == "vermutung", "die erste Station ist die Forscherfrage"
    vor_lese = [aufgaben[n] for n in STATIONEN[:STATIONEN.index("L2")]]
    assert vor_lese[-1]["typ"] == "pruefen", "die Forschungsphase endet mit einem pruefen"
    ids = [a["id"] for a in aufgaben.values() if a["typ"] == "vermutung"]
    assert len(ids) == len(set(ids)) >= 2 and all(re.fullmatch(r"v_[a-z0-9_]+", i) for i in ids)
    gesehen = []
    for n in NUMMERN:
        a = aufgaben[n]
        if a["typ"] == "vermutung":
            gesehen.append(a["id"])
        if a["typ"] == "pruefen":
            assert a["vermutung"] in gesehen, f"Aufgabe {n}: prüft eine Vermutung, die vorher gestellt wurde"
    geprueft = {a["vermutung"] for a in aufgaben.values() if a["typ"] == "pruefen"}
    assert geprueft == set(ids), "zu jeder Vermutung gehört genau eine Prüfung"
    # Jede Vermutung steht vor ihrer Prüfung, dazwischen liegt Evidenz (Zählen, Tabelle, Film)
    for nr_v, nr_p in ((50, 52), (53, 55)):
        assert STATIONEN.index(nr_v) < STATIONEN.index(nr_p)


def test_quoten_und_stationszahl(aufgaben):
    """Echte Forschen-Stationen (ECHT_FORSCHEN_TYPEN) ≥ 3 und ≥ Mindestanteil, Sprachwerkstatt ≥ 2, Abfrage ≤ 30 %, höchstens 12 Stationen."""
    assert len(STATIONEN) <= STATIONEN_MAX
    n = len(aufgaben)
    echt = [nr for nr, a in aufgaben.items() if a["typ"] in ECHT_FORSCHEN_TYPEN]
    sprache = [nr for nr, a in aufgaben.items() if a["eyebrow"].startswith("Sprachwerkstatt")]
    abfrage = [nr for nr, a in aufgaben.items() if a["typ"] in ABFRAGE_TYPEN and nr not in sprache]
    assert len(echt) >= MIN_FORSCHEN_ANZAHL["koerper"] and len(echt) / n >= QUOTE_FORSCHEN_MIN, (echt, n)
    assert len(sprache) >= SPRACHWERKSTATT_MIN, sprache
    assert len(abfrage) / n <= QUOTE_ABFRAGE_MAX, abfrage
    # Mindestens die Hälfte der echten Forschen-Stationen arbeitet unmittelbar mit Modell bzw. Film
    mit_modell = [nr for nr in echt if any(k["film"] in ("biene3d", "volk") for k in _alle_knoepfe(aufgaben[nr]))]
    assert len(mit_modell) / len(echt) >= 0.5, (mit_modell, echt)


def test_kein_platzhalter_mehr(tab):
    gesamt = json.dumps(tab[0], ensure_ascii=False) + json.dumps(lesen_koerper.LESESTRECKEN, ensure_ascii=False)
    gesamt += json.dumps(zeichenauftraege.ZEICHENAUFTRAEGE["biene"], ensure_ascii=False)
    assert "PLATZHALTER" not in gesamt
    assert not lesen_koerper.LESESTRECKEN["koerper"].get("platzhalter")


def test_differenzierte_aufgaben_haben_a_b_c(aufgaben):
    for nr, a in aufgaben.items():
        if a["typ"] in DIFFERENZIERT or a["typ"] == "erkunden":
            assert sorted(a["niveaus"]) == ["A", "B", "C"], nr


# ── Sprache ───────────────────────────────────────────────────────────────────
def test_saetze_der_aufgaben_sind_kurz(tab):
    """Sek-I-Sprache: höchstens etwa 15 Wörter je Satz (Toleranz 18); Antwortoptionen höchstens 12 Wörter."""
    zu_lang = [(nr, len(s.split()), s[:60]) for nr, t in _alle_aufgaben_texte(tab) for s in _saetze(t) if len(s.split()) > 18]
    assert not zu_lang, zu_lang
    for a in tab[0]["aufgaben"]:
        for cfg in (a.get("niveaus") or {}).values():
            for o in _optionstexte(cfg.get("optionen", [])):
                assert len(o.split()) <= 12, (a["nr"], o)
            for key in ("erkenntnis", "beleg"):
                if isinstance(cfg.get(key), dict):
                    for o in cfg[key]["optionen"]:
                        assert len(o["t"].split()) <= 12, (a["nr"], o["t"])


def test_feste_woerter_statt_synonyme(tab):
    texte = [(nr, re.sub(r"\[[^\]]*\]", "", t)) for nr, t in _alle_aufgaben_texte(tab)]   # Lücken-Alternativen ausnehmen
    texte += [("L2", _klartext(a["text"] + " " + a["frage"] + " " + " ".join(a["optionen"]) + " " + a["erklaerung"]))
              for a in lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"]]
    for nr, t in texte:
        for muster in VERBOTEN:
            assert not re.search(muster, t), f"{nr}: Synonym {muster!r} in „{t[:60]}“"


def test_zahlen_stehen_im_konzept(tab):
    """Jede Zahl (Ziffern) in den Texten dieses Reiters kommt in AB_KONZEPT.md vor (Sekunden der Film-Knöpfe sind keine Texte)."""
    konzept = open(os.path.join(os.path.dirname(ROOT), "AB_KONZEPT.md"), encoding="utf-8").read()
    norm = lambda s: re.sub(r"(?<=\d)[\s  ](?=\d{3}\b)", "", s)
    erlaubt = set(re.findall(r"\d+", norm(konzept)))
    texte = [t for _, t in _alle_aufgaben_texte(tab)]
    for a in lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"]:
        texte += [a["text"], a["frage"], a["erklaerung"]] + list(a["optionen"])
    for e in glossar_eintraege().values():
        texte.append(e["text"])
    for t in texte:
        for z in re.findall(r"\d+", norm(_klartext(t))):
            assert z in erlaubt, f"Zahl {z} nicht im Konzept: „{t[:70]}“"


def glossar_eintraege():
    import glossar_koerper
    return glossar_koerper.EINTRAEGE


# ── Vermutungen ───────────────────────────────────────────────────────────────
def test_vermutungen_sind_offen_und_vollstaendig(aufgaben):
    for nr, a in aufgaben.items():
        if a["typ"] != "vermutung":
            continue
        assert a["frage"].rstrip().endswith("vermutest du?"), nr
        assert not any(k in a for k in ("loesung", "ok")), f"Aufgabe {nr}: eine Vermutung hat keine Lösung"
        cfg = a["niveaus"]
        assert len(cfg["A"]["optionen"]) >= 3 and "satzanfang" not in cfg["A"], nr           # A: antippen
        assert len(cfg["B"]["optionen"]) >= 3 and cfg["B"]["satzanfang"] and cfg["B"]["begruendung"], nr   # B: wählen + Satz
        assert cfg["C"]["frei"] is True and cfg["C"]["satzanfang"] and cfg["C"]["min"] >= 30, nr          # C: eigener Satz
        for n in "AB":
            opts = cfg[n]["optionen"]
            assert len(set(opts)) == len(opts) and all(len(o.split()) <= 12 for o in opts), (nr, n)


def test_vermutungsoptionen_sind_plausibel_und_pruefbar(aufgaben):
    """Keine Unsinns-Hypothesen: Jede Option von 53 nennt Körperteile, an denen die Biene Nektar oder Pollen tragen könnte, und lässt
    sich mit Film (Szene 8) und Modell bestätigen oder widerlegen. Die Optionen von 50 nennen genau Körperteile, Beine und Flügel."""
    for n in "AB":
        for o in aufgaben[53]["niveaus"][n]["optionen"]:
            assert not re.search(r"Fühler|Kopf|Flügel|Facetten", o), (n, o)
            assert re.search(r"Rüssel|Hinterleib|Beine", o), (n, o)
    for n in "AB":
        for o in aufgaben[50]["niveaus"][n]["optionen"]:
            assert re.fullmatch(r"\w+ Körperteile, \w+ Beine, \w+ Flügel", o), (n, o)
    # Die richtige Aussage (Nektar im Hinterleib, Pollen an den Beinen) und mindestens zwei plausible Gegenvermutungen sind enthalten
    for n in "AB":
        opts = aufgaben[53]["niveaus"][n]["optionen"]
        assert any(re.search(r"Nektar im Hinterleib, Pollen an den Beinen", o) for o in opts), n
        assert sum(1 for o in opts if "Nektar im Hinterleib, Pollen an den Beinen" not in o) >= 3, n


# ── Prüfungen (pruefen) ───────────────────────────────────────────────────────
def _laengen_regel(opts, wer):
    """Die richtige Option ist nicht die längste und nicht kürzer als 70 % der längsten (docs/AUDIT_FORSCHEN, Entscheidung 1)."""
    laengen = [len(o["t"]) for o in opts]
    richtig = [len(o["t"]) for o in opts if o["ok"]][0]
    assert richtig < max(laengen), f"{wer}: die richtige Option ist die längste ({laengen})"
    assert richtig >= 0.7 * max(laengen), f"{wer}: die richtige Option ist zu kurz ({laengen})"
    assert min(laengen) >= 0.7 * max(laengen), f"{wer}: Optionen sehr verschieden lang ({laengen})"


def test_pruefungen(aufgaben):
    for nr in (52, 55):
        a = aufgaben[nr]
        assert a["typ"] == "pruefen" and a["quelle"] and a["erkenntnis"] and _knoepfe(a), nr
        assert any(k["film"] in ("biene3d", "volk") for k in _knoepfe(a)), nr
        assert len(_saetze(a["erkenntnis"])) <= 3 and all(len(s.split()) <= 18 for s in _saetze(a["erkenntnis"])), nr
        for n, cfg in a["niveaus"].items():
            erk = cfg["erkenntnis"]
            assert erk.get("hinweis") and len(erk["hinweis"].split()) <= 25, f"{nr} {n}: erkenntnis.hinweis fehlt"
            opts = erk["optionen"]
            assert sum(o["ok"] for o in opts) == 1 and len(opts) == (3 if n == "A" else 4), (nr, n)
            assert len({o["t"] for o in opts}) == len(opts), (nr, n)
            _laengen_regel(opts, f"{nr} {n} Erkenntnis")
            if n == "B":
                bel = cfg["beleg"]
                assert bel.get("hinweis") and sum(o["ok"] for o in bel["optionen"]) == 1 and len(bel["optionen"]) == 3, nr
                _laengen_regel(bel["optionen"], f"{nr} B Beleg")
            if n == "C":
                assert cfg["satz"]["anfang"] and cfg["satz"]["min"] >= 40, nr
        # Lösungsposition der Erkenntnis wechselt zwischen den Niveaus
        pos = {n: [i for i, o in enumerate(c["erkenntnis"]["optionen"]) if o["ok"]][0] for n, c in a["niveaus"].items()}
        assert len(set(pos.values())) >= 2, (nr, pos)


def test_pruefungen_sind_gleich_gebaut(aufgaben):
    """Alle Optionen einer Frage beginnen gleich (gleicher Satzbau), die richtige verrät sich nicht durch eine eigene Form."""
    for nr in (52, 55):
        for n, cfg in aufgaben[nr]["niveaus"].items():
            ts = [o["t"] for o in cfg["erkenntnis"]["optionen"]]
            erste = [t.split()[0] for t in ts]
            assert len(set(erste)) <= 2, (nr, n, erste)
            assert all(t.endswith(".") for t in ts), (nr, n)
    # Beleg-Optionen beginnen alle mit „Ich habe …“ bzw. „Im Film …“
    for nr in (52, 55):
        bel = aufgaben[nr]["niveaus"]["B"]["beleg"]["optionen"]
        assert len({o["t"].split()[0] for o in bel}) == 1, (nr, [o["t"] for o in bel])


def test_quelle_und_knopftexte_der_pruefungen_sind_neutral(aufgaben):
    """Quelle und Knopftexte verraten keine Option: In 55 kein Honigmagen/Hinterbein/Pollenkörbchen, in 52 keine Zahl der Erkenntnis."""
    a55, a52 = aufgaben[55], aufgaben[52]
    texte55 = [a55["quelle"]] + [k["text"] for k in _knoepfe(a55)]
    for t in texte55:
        assert not re.search(r"Honigmagen|Hinterbein|Pollenkörbchen|Höschen|Rüssel", t), t
    assert "Szene 8" in a55["quelle"]
    texte52 = [a52["quelle"]] + [k["text"] for k in _knoepfe(a52)]
    for t in texte52:
        woerter = set(re.findall(r"\w+", t.lower()))
        assert not woerter & set(ZAHLWOERTER.values()), t
    # A-Optionen enthalten die Schlüsselwörter alle, nicht nur die richtige Option
    opts = a55["niveaus"]["A"]["erkenntnis"]["optionen"]
    assert all("Honigmagen" in o["t"] for o in opts) and sum("Hinterbein" in o["t"] for o in opts) >= 2


def test_film_knoepfe_springen_auf_sekunden(aufgaben):
    """Film-Knöpfe nutzen springe (Sekunden, mit „▶“ und Kapitel in der Beschriftung); film.js hängt spielen an. Zeiten: ab_uebergabe.md."""
    a55 = [k for k in _knoepfe(aufgaben[55]) if k["film"] == "volk"]
    assert [k["befehle"] for k in a55] == [[{"mw": "springe", "t": 145}], [{"mw": "springe", "t": 149.5}]]
    assert all(k["text"].startswith("▶ Sieh dir an:") and "(Kapitel 8)" in k["text"] and k.get("pflicht") is True for k in a55)
    a57 = [k for k in _knoepfe(aufgaben[57]) if k["film"] == "volk"]
    assert [k["befehle"] for k in a57] == [[{"mw": "springe", "t": 145}], [{"mw": "springe", "t": 181}]]
    assert [("Kapitel 8" in k["text"], "Kapitel 10" in k["text"]) for k in a57] == [(True, False), (False, True)]
    # 145 s liegt im Satz „Mit dem Rüssel saugen sie Nektar …“ (145,3–149,2), 149,5 s vor „Den Pollen kleben sie …“ (149,7–153,1),
    # 181 s vor „Im Stock geben die Bienen den Nektar weiter …“ (181,4–186,3)
    assert 142 <= 145 < 149.2 and 149.2 <= 149.5 < 149.7 and 180 <= 181 < 181.4


# ── Forscherbogen und Tabelle ─────────────────────────────────────────────────
def test_forscherbogen_zeilen(aufgaben):
    a = aufgaben[51]
    assert a["auftrag"] and not _knoepfe(a), "der Bogen hat keinen Gesamtknopf: jede Zeile bringt ihren eigenen mit"
    for n, cfg in a["niveaus"].items():
        zeilen = cfg["zeilen"]
        assert 4 <= len(zeilen) <= 6, n
        for z in zeilen:
            assert z["frage"] and z["art"] in ("zahl", "wahl", "mehrfach", "text"), (n, z)
            if z["art"] == "zahl":
                assert isinstance(z["loesung"], int) and z["einheit"] and z["hinweis"], (n, z["frage"])
            if z["art"] == "wahl":
                assert 0 <= z["loesung"] < len(z["optionen"]) and len(z["optionen"]) >= 3 and z["hinweis"], (n, z["frage"])
            if z["art"] == "mehrfach":
                assert z["loesung"] and all(0 <= i < len(z["optionen"]) for i in z["loesung"]) and len(z["loesung"]) < len(z["optionen"]), (n, z["frage"])
            assert z["art"] != "text", f"{n}: Textzeilen sind nicht prüfbar (jeder Text zählt) und stehen nicht mehr im Bogen"
            assert z.get("modell"), f"{n}: jede prüfbare Zeile hat ihren Modell-Knopf ({z['frage']})"
    # Schlusssatz: Pflicht in allen Stufen. A und B wählen einen Baustein (mit falschen Bausteinen), C schreibt frei (mindestens 60 Zeichen)
    for n in "AB":
        s = a["niveaus"][n]["schluss"]
        assert s["pflicht"] is True and s["anfang"] and len(s["bausteine"]) == 3, n
        falsche = [b for b in s["bausteine"] if isinstance(b, dict) and b.get("ok") is False]
        assert len(falsche) >= 1 and all(b.get("rueckmeldung") for b in falsche), n
    assert sum(1 for b in a["niveaus"]["B"]["schluss"]["bausteine"] if not (isinstance(b, dict) and b.get("ok") is False)) == 1
    c = a["niveaus"]["C"]["schluss"]
    assert c["pflicht"] is True and c["min"] == 60 and "bausteine" not in c and "anfang" not in c
    # Inhalt: die Zahlen des Körperbaus (AB_KONZEPT.md): 3 Körperteile, 6 Beine, 4 Flügel, 2 Fühler
    for n in "ABC":
        zahlen = {z["einheit"]: z["loesung"] for z in a["niveaus"][n]["zeilen"] if z["art"] == "zahl"}
        assert {"Körperteile": 3, "Beine": 6, "Flügel": 4}.items() <= zahlen.items(), n
    assert {z["einheit"]: z["loesung"] for z in a["niveaus"]["A"]["zeilen"] if z["art"] == "zahl"}["Fühler"] == 2


def test_fluegel_zeile_zeigt_die_vier_fluegel_von_hinten(aufgaben):
    """Audit B1: Nur der Blick von hinten (Außenansicht, Flügel hervorgehoben) zeigt vier getrennte Flügel."""
    for nr, zeilen in [(51, [z for c in aufgaben[51]["niveaus"].values() for z in c["zeilen"]])]:
        zf = [z for z in zeilen if z["art"] == "zahl" and z["einheit"] == "Flügel"]
        assert len(zf) == 3
        for z in zf:
            k = z["modell"]
            assert k["text"] == "Flügel von hinten zeigen"
            blick = [b for b in k["befehle"] if b["mw"] == "blick"]
            assert blick == [{"mw": "blick", "name": "hinten"}], k
            heb = [b for b in k["befehle"] if b["mw"] == "hervorheben"]
            assert heb == [{"mw": "hervorheben", "teile": ["fluegel"], "fokus": False}], k
            assert z["hinweis"] == "Sieh die Flügel von hinten an. Zähle jeden Flügel einzeln."
            assert z["hinweis2"] == "Auf jeder Seite liegt ein großer und ein kleiner Flügel übereinander."
    k52 = [k for k in _knoepfe(aufgaben[52]) if "Flügel" in k["text"]]
    assert k52 and k52[0]["text"] == "Flügel von hinten zeigen"


def test_hinweise_verraten_die_loesung_nicht(aufgaben):
    """Rückmeldungen lenken auf ein sichtbares Merkmal, sie nennen die Lösung nicht."""
    for n, cfg in aufgaben[51]["niveaus"].items():
        for z in cfg["zeilen"]:
            hinweise = " ".join(z.get(k, "") for k in ("hinweis", "hinweis2")).lower()
            if z["art"] == "zahl":
                assert str(z["loesung"]) not in hinweise, (n, z["frage"])
                assert ZAHLWOERTER[z["loesung"]] not in re.findall(r"\w+", hinweise), (n, z["frage"], hinweise)
            elif z["art"] == "wahl":
                assert z["optionen"][z["loesung"]].lower() not in hinweise, (n, z["frage"])
            elif z["art"] == "mehrfach":
                assert not any(z["optionen"][i].lower() in hinweise for i in z["loesung"]), (n, z["frage"])
    for n, cfg in aufgaben[54]["niveaus"].items():
        for z in cfg["zeilen"]:
            assert not any(o.lower() in z["hinweis"].lower() for o in z["optionen"]), (n, z["merkmal"])
    for n, cfg in aufgaben[9]["niveaus"].items():
        for z in cfg["ziele"]:
            name = {"fuehler": "fühler", "fluegel": "flügel", "pollenkoerbchen": "pollenkörbchen", "ruessel": "rüssel",
                    "vorderbein": "vorderbein", "mittelbein": "mittelbein"}.get(z["teil"], z["teil"])
            assert name not in z["hinweis"].lower().replace(" ", ""), (n, z["teil"], z["hinweis"])
    # Die Erkenntnisse der Prüfungen stehen in keinem Hinweis der Station (nur Hilfen zum Hinsehen)
    for nr in (52, 55):
        for n, cfg in aufgaben[nr]["niveaus"].items():
            richtig = [o["t"] for o in cfg["erkenntnis"]["optionen"] if o["ok"]][0]
            assert richtig not in cfg["erkenntnis"]["hinweis"], (nr, n)


def test_tabelle_innenleben(aufgaben):
    a = aufgaben[54]
    assert a["auftrag"] and a["erkenntnis"]
    assert "Du suchst, wo die Biene den Nektar tragen könnte" in a["auftrag"], "Einstiegssatz zur Forscherfrage 53 (Audit W4)"
    assert "Nachbau am Computer" in a["auftrag"] and "Farben" in a["auftrag"]
    ks = _knoepfe(a)
    organ = [k for k in ks if k["text"].endswith("zeigen") and "Alle" not in k["text"]]
    assert [k["text"] for k in organ] == ["Honigmagen zeigen", "Flugmuskeln zeigen", "Gehirn zeigen", "Stachel zeigen"]
    assert all(k.get("pflicht") is True for k in organ), "alle Organ-Knöpfe sind Pflicht (Audit W4)"
    assert sum(1 for k in ks if k.get("pflicht")) == 4
    # Herz und Darm stehen nicht in der Tabelle und haben keinen Knopf (laufen durch mehrere Körperteile)
    assert not any(re.search(r"Herz|Darm", k["text"]) for k in ks)
    erwartet = {"Honigmagen": "Hinterleib", "Stachel": "Hinterleib", "Flugmuskeln": "Brust", "Gehirn": "Kopf"}
    for n, cfg in a["niveaus"].items():
        spalten = cfg["spalten"]
        assert 3 <= len(spalten) <= 4 and len(set(spalten)) == len(spalten) and set(spalten) <= set(erwartet), n
        assert "Herz" not in spalten and "Darm" not in spalten
        for z in cfg["zeilen"]:
            assert len(z["loesung"]) == len(spalten) and all(0 <= i < len(z["optionen"]) for i in z["loesung"]), (n, z["merkmal"])
            assert z["merkmal"] and z["hinweis"], (n, z)
        zeilen = {z["merkmal"]: z for z in cfg["zeilen"]}
        lage = zeilen["Wo liegt es hauptsächlich?"]
        assert lage["optionen"] == ["Kopf", "Brust", "Hinterleib"], n
        assert "gelbe Verdickung" in lage["hinweis"], f"{n}: Hinweis zum Gehirn fehlt (Audit W4)"
        form = zeilen["So sieht es im Modell aus"]
        assert len(set(form["loesung"])) == len(spalten), f"{n}: jede Form genau einmal"
        assert len(form["optionen"]) >= len(spalten)
        for s, i in zip(spalten, lage["loesung"]):
            assert lage["optionen"][i] == erwartet[s], (n, s)
    # Jede Spalte hat einen Knopf und jeder Pflicht-Knopf eine Spalte: alle drei Stufen haben vier Spalten (mit Stachel);
    # C hat zusätzliche falsche Formen
    assert [len(a["niveaus"][n]["spalten"]) for n in "ABC"] == [4, 4, 4]
    for n in "ABC":
        assert a["niveaus"][n]["spalten"] == ["Honigmagen", "Flugmuskeln", "Gehirn", "Stachel"], n
    c_form = [z for z in a["niveaus"]["C"]["zeilen"] if z["merkmal"].startswith("So sieht")][0]
    assert len(c_form["optionen"]) == 6 and len(set(c_form["loesung"])) == 4
    # Merksatz nennt nur Bearbeitetes (alle Stufen: Honigmagen, Flugmuskeln, Gehirn, Stachel)
    assert a["erkenntnis"] == ("Der Honigmagen liegt im Hinterleib. Die Flugmuskeln liegen in der Brust. "
                               "Das Gehirn liegt im Kopf. Der Stachel sitzt am Ende des Hinterleibs.")


# ── Lösungspositionen und Lesestrecke ─────────────────────────────────────────
def test_lesestrecke_l2_ist_echt_und_vollstaendig():
    s = lesen_koerper.LESESTRECKEN["koerper"]
    assert s["station"] == "L2" and s["titel"] == "Eine Biene ist ein Insekt"
    assert len(s["abschnitte"]) == 5
    bilder = [a["bild"] for a in s["abschnitte"]]
    assert bilder == [f"koerper-{i}" for i in range(1, 6)], bilder
    ueberschriften = [a["ueberschrift"] for a in s["abschnitte"]]
    assert ueberschriften == ["Drei Körperteile, sechs Beine", "Der Kopf: Sinne und Mund", "Die Brust: Flügel und Beine",
                              "Der Hinterleib: Honigmagen und Stachel", "Werkzeug zum Sammeln"]
    for a in s["abschnitte"]:
        assert a["bild_alt"].startswith("Schaubild:"), a["bild"]
        assert 3 <= len(_saetze(a["text"])) <= 5, (a["bild"], len(_saetze(a["text"])))
        assert all(len(x.split()) <= 15 for x in _saetze(a["text"])), a["bild"]
        assert len(a["optionen"]) == 3 and 0 <= a["loesung"] < 3 and len(set(a["optionen"])) == 3
        assert a["erklaerung"].startswith("Richtig:"), a["bild"]


def test_lesestrecke_bezieht_sich_auf_die_forschung_ohne_den_film_vorauszusetzen():
    """Die Lesestrecke kommt nach dem Forschen und knüpft an Eigenes an („Du hast …“). Der Film ist nur in Pflicht-Knöpfen von 55
    gesichert; deshalb steht dort „siehst du“ (Audit K6), nie „hast du gesehen“."""
    abschnitte = lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"]
    bezug = [a["bild"] for a in abschnitte if re.search(r"\bDu hast\b|\bhast du\b|\bsiehst du\b", _klartext(a["text"]))]
    assert len(bezug) >= 4, bezug
    film = [a["text"] for a in abschnitte if "Film" in a["text"]]
    assert film and all("Im Film siehst du" in t and "Film hast du" not in t for t in film), film


def test_lesestrecke_loesungen_verteilt():
    pos = [a["loesung"] for a in lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"]]
    assert len(set(pos)) == 3, pos           # alle drei Positionen kommen vor
    assert pos.count(0) <= 2 and pos.count(1) <= 2, pos


def test_lesestrecke_fette_begriffe_haben_glossar():
    fett = []
    for a in lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"]:
        fett += re.findall(r"<strong>(.*?)</strong>", a["text"])
    assert fett, "Die Lesestrecke braucht fette Fachbegriffe"
    assert len(fett) == len(set(f.lower() for f in fett)), f"Begriff doppelt fett: {fett}"
    for b in fett:
        assert glossar.eintrag_fuer(b) is not None, f"fetter Begriff {b} ohne Glossareintrag"


def test_lesestrecke_wiederholt_nicht_die_loesung_in_der_frage():
    for a in lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"]:
        assert a["frage"].rstrip("?") not in a["text"], a["bild"]


# ── Glossar ───────────────────────────────────────────────────────────────────
def test_glossar_eintraege():
    e = glossar_eintraege()
    assert sorted(e) == sorted(GLOSSAR_SCHLUESSEL)
    for key, eintrag in e.items():
        assert eintrag["titel"] and eintrag["aliase"] and len(eintrag["text"]) <= 400, key
        assert len(_saetze(eintrag["text"])) <= 5, key
        assert all(len(s.split()) <= 17 for s in _saetze(eintrag["text"])), key
        assert glossar.GLOSSAR[key] is eintrag
    for key, bild in GLOSSAR_BILDER.items():
        assert e[key]["bild"] == bild, key
    for key in set(e) - set(GLOSSAR_BILDER):
        assert e[key]["bild"] is None, key
    norm = glossar.normalisieren
    for alias in ("Honigblase", "Pollenhöschen", "Pollenkörbchen", "Facettenaugen", "Insekten", "Rüssel", "Fühler", "Stachel"):
        assert norm(alias) in glossar.ALIASE, alias
    assert glossar.ALIASE[norm("Honigblase")] == "honigmagen" and glossar.ALIASE[norm("Pollenhöschen")] == "pollenkoerbchen"


# ── Modell-Aufgaben und Knöpfe ────────────────────────────────────────────────
def test_modell_knoepfe_sind_gueltig(tab, aufgaben):
    inh = tab[1]
    for nr, a in aufgaben.items():
        for k in _alle_knoepfe(a):
            assert k["film"] in inh["filme"] and k["text"] and k["befehle"], nr
            art = inh["filme"][k["film"]]["art"]
            for b in k["befehle"]:
                if art == "modell3d":
                    assert b["mw"] in MODELL_BEFEHLE, (nr, b)
                    if b["mw"] == "ansicht":
                        assert b.get("name") in MODELL_ANSICHTEN, (nr, b)
                    if b["mw"] == "blick":
                        assert b.get("name") in MODELL_BLICKE, (nr, b)
                    if b["mw"] in ("hervorheben", "beschriften", "fokus"):
                        assert set(b["teile"]) <= MODELL_TEILE, (nr, b)
                    if b["mw"] == "fokus":
                        assert b.get("blick", "schraeg") in MODELL_BLICKE and b["teile"], (nr, b)
                else:
                    assert b["mw"] in FILM_BEFEHLE, (nr, b)
                    if b["mw"] == "kapitel":
                        assert 1 <= b.get("n", 1) <= 12, (nr, b)
                    if b["mw"] == "springe":
                        assert 0 <= b["t"] <= 240, (nr, b)
            grenze = 14 if art == "papiertheater" else 7        # Film-Knöpfe nennen Stelle und Frage in der Beschriftung
            assert len(k["text"].split()) <= grenze, (nr, k["text"])


def test_jede_modell_aufgabe_nennt_ihre_quelle(aufgaben):
    """Aufgaben, die am Modell hängen, haben film (8, 9) oder einen Modell-Knopf; Vermutungen und Sprachaufgabe 56 brauchen keine Quelle."""
    for nr in (8, 9):
        assert aufgaben[nr]["film"] == "biene3d"
    for nr in (51, 52, 54, 55, 57, 15):
        ks = _alle_knoepfe(aufgaben[nr])
        assert ks and any(k["film"] in ("biene3d", "volk") for k in ks), nr
    for nr in (50, 53, 56):
        assert not _alle_knoepfe(aufgaben[nr]) and "film" not in aufgaben[nr], nr


def test_pflicht_knoepfe_nur_wo_evidenz_noetig_ist(aufgaben):
    """Pflicht-Knöpfe: die vier Organ-Knöpfe in 54 und die zwei Film-Knöpfe in 55 (ohne sie kann man nur raten)."""
    mit = {nr: [k["text"] for k in _alle_knoepfe(a) if k.get("pflicht")] for nr, a in aufgaben.items()}
    mit = {nr: t for nr, t in mit.items() if t}
    assert set(mit) == {54, 55}, mit
    assert len(mit[54]) == 4 and len(mit[55]) == 2


def test_alle_knoepfe_beginnen_mit_zurueck(aufgaben):
    """Jeder Modell-Knopf beginnt mit „zurueck“: Hervorhebungen, Schilder und Fokus anderer Stationen bleiben nicht stehen."""
    for nr, a in aufgaben.items():
        for k in _alle_knoepfe(a):
            if k["film"] == "biene3d":
                assert k["befehle"][0] == {"mw": "zurueck"}, (nr, k["text"])


def test_organ_knoepfe_stellen_innenansicht_ein(aufgaben):
    """Wer Innenteile hervorhebt, braucht die Ansicht situs oder explosion; der Stachel steht in der Explosion."""
    for nr, a in aufgaben.items():
        for k in _alle_knoepfe(a):
            if k["film"] != "biene3d":
                continue
            ansicht = None
            for b in k["befehle"]:
                if b["mw"] == "ansicht":
                    ansicht = b["name"]
                if b["mw"] in ("hervorheben", "fokus") and set(b["teile"]) & INNENTEILE:
                    assert ansicht in ("situs", "explosion"), (nr, k["text"])
                    if "stachel" in b["teile"]:
                        assert ansicht == "explosion", (nr, k["text"])
    # Rüssel liegt hinter dem Auge: der Knopf schaut von vorn und fährt heran
    r = [k for k in _knoepfe(aufgaben[57]) if any(b["mw"] == "fokus" and "ruessel" in b["teile"] for b in k["befehle"])]
    assert r and all(any(b["mw"] == "fokus" and b["blick"] == "vorn" for b in k["befehle"]) for k in r)


def test_fokus_befehle_haben_blick_und_markieren_nicht(aufgaben):
    """`fokus` fährt ohne Markierung heran, `hervorheben` markiert ohne eigenen Fokus: so hängt der Blick nicht von der alten Kamera ab."""
    for nr, a in aufgaben.items():
        for k in _alle_knoepfe(a):
            fokus = [b for b in k["befehle"] if b["mw"] == "fokus"]
            for b in fokus:
                assert b.get("blick") in MODELL_BLICKE, (nr, k["text"])
            for b in k["befehle"]:
                if b["mw"] == "hervorheben":
                    assert b.get("fokus") is False, (nr, k["text"], "hervorheben ohne eigenen Fokus (Richtung wäre die der alten Kamera)")


def test_modellfinden_ziele(aufgaben):
    a = aufgaben[9]
    erlaubt_klein = {"fuehler", "facettenauge", "ruessel", "mittelbein", "vorderbein"}
    for n, cfg in a["niveaus"].items():
        ziele = cfg["ziele"]
        assert cfg["auftrag"] and 3 <= len(ziele) <= 6, n
        assert len({z["teil"] for z in ziele}) == len(ziele), f"{n}: Ziel doppelt"
        for z in ziele:
            assert z["teil"] in MODELL_TEILE and z["frage"].startswith("Tippe auf") and z["hinweis"], (n, z["teil"])
            assert z.get("ansicht", "gestalt") in MODELL_ANSICHTEN and z.get("blick", "schraeg") in MODELL_BLICKE
            # Keine Organe (Lage und Aussehen erforscht 54) und kein Pollenkörbchen (erforscht 55)
            assert z["teil"] not in INNENTEILE and z["teil"] != "pollenkoerbchen", (n, z["teil"])
            # Kleine Teile haben eine Kamerafahrt (Feld fokus mit dem Teil selbst), sonst sind sie zu klein zum Antippen
            if z["teil"] in erlaubt_klein:
                assert z["fokus"]["teile"] == [z["teil"]] and z["fokus"]["blick"] == z["blick"], (n, z["teil"])
            elif "fokus" in z:
                assert set(z["fokus"]["teile"]) <= MODELL_TEILE
    assert {z["teil"] for z in a["niveaus"]["A"]["ziele"]} == {"kopf", "brust", "hinterleib", "fluegel", "bein"}
    assert all(z["ansicht"] == "gestalt" for z in a["niveaus"]["A"]["ziele"])
    assert {z["teil"] for z in a["niveaus"]["B"]["ziele"]} == {"fuehler", "hinterbein", "brust", "kopf", "hinterleib"}
    assert {z["teil"] for z in a["niveaus"]["C"]["ziele"]} == {"facettenauge", "ruessel", "mittelbein", "vorderbein"}
    # Fühler (B) und alle C-Ziele haben ein Fokus-Feld; Rüssel mit Blick von vorn
    assert [z["teil"] for z in a["niveaus"]["B"]["ziele"] if "fokus" in z] == ["fuehler"]
    assert all("fokus" in z for z in a["niveaus"]["C"]["ziele"])
    assert [z for z in a["niveaus"]["C"]["ziele"] if z["teil"] == "ruessel"][0]["fokus"]["blick"] == "vorn"


def test_aufgabe_9_steht_hinter_52(aufgaben):
    """Erst zählen und prüfen (51, 52), dann Namen und Lage festigen (9): Reihenfolge laut Entscheidung des Leiters zu Audit W5."""
    assert STATIONEN.index(51) < STATIONEN.index(52) < STATIONEN.index(9) < STATIONEN.index(53)


def test_erkunden_auftrag_verweist_auf_vermutung_und_naechste_station(aufgaben):
    for n, cfg in aufgaben[8]["niveaus"].items():
        assert cfg["auftrag"] and 2 <= len(cfg["beobachtung"]) <= 3, n
        assert "Sieh nach, ob deine Vermutung stimmt." in cfg["auftrag"], n
        assert "Die Fragen findest du in der nächsten Station wieder." in cfg["auftrag"], n
    a = " ".join(aufgaben[8]["niveaus"]["A"]["beobachtung"])
    assert "Beine" in a and "Flügel" in a and "Hinterleib" in a      # kommen in 51 und 54 wieder


# ── Sprachwerkstatt ───────────────────────────────────────────────────────────
def test_sprachwerkstatt_einzahl_und_mehrzahl(aufgaben):
    a = aufgaben[56]
    assert a["eyebrow"].startswith("Sprachwerkstatt") and a["typ"] == "zuordnung"
    for n, cfg in a["niveaus"].items():
        links = [p[0] for p in cfg["paare"]]
        rechts = [p[1] for p in cfg["paare"]]
        assert len(set(links)) == len(links) >= 4 and len(set(rechts)) == len(rechts), n
        for e, m in cfg["paare"]:
            assert PLURAL_DUDEN.get(e) == m, f"{n}: {e} – {m} ist keine bestätigte Duden-Form"
            assert e.split()[0] in ("der", "die", "das") and m.split()[0] == "die", (n, e, m)
        # Eigener Anleitungssatz und eigene Hilfe je Niveau (Audit K5, Entscheidung 6): nie „Lesestrecke“, kein „Begriff/Erklärung“
        assert cfg["hinweis"].startswith("Tippe links ein Wort in der Einzahl an, dann rechts die Mehrzahl."), n
        assert cfg["hilfe"] and "Lesestrecke" not in cfg["hilfe"], n
    # Nur Wörter aus diesem Reiter (Wabe und Zelle kommen erst im Reiter „Das Bienenvolk“)
    alle = " ".join(p[0] + " " + p[1] for c in a["niveaus"].values() for p in c["paare"])
    assert not re.search(r"Wabe|Zelle", alle)
    n_paare = [len(a["niveaus"][n]["paare"]) for n in "ABC"]
    assert n_paare == sorted(n_paare) and n_paare[0] < n_paare[2], n_paare


def test_sprachwerkstatt_zeitfolge(aufgaben):
    a = aufgaben[57]
    assert a["eyebrow"].startswith("Sprachwerkstatt") and a["typ"] == "sortierung"
    A, B, C = (a["niveaus"][n]["items"] for n in "ABC")
    assert [i.split()[0] for i in A] == ["Zuerst", "Dann", "Danach", "Schließlich"]
    assert B[0].startswith("Zuerst") and all(i.split()[0] in SIGNALWOERTER for i in B) and len({i.split()[0] for i in B}) == len(B) == 5
    assert not any(i.split()[0] in SIGNALWOERTER for i in C) and len(C) == 6
    for items in (A, B, C):
        assert "Rüssel" in items[1] and "Honigmagen" in items[2] and "Blüte" in items[0]
    # Keine Zellen und Waben (Szene 10 gehört zum Film-Reiter); der Honig-Schritt hat den Film-Knopf zu Kapitel 10
    assert not re.search(r"Wabe|Zelle", " ".join(A + B + C))
    assert C[-1] == "Aus dem Nektar wird im Bienenstock Honig."
    for n, cfg in a["niveaus"].items():
        assert cfg["hilfe"] and "Lesestrecke" not in cfg["hilfe"], n
    # Film Szene 8 und 10 und das Modell sind als Hilfe da (Sekundensprung in test_film_knoepfe_springen_auf_sekunden)
    assert len(_knoepfe(a)) == 4


# ── Zeichnung 1 ───────────────────────────────────────────────────────────────
def test_zeichnung_1_und_pruefliste(aufgaben):
    a = aufgaben[15]
    assert a["geraet"] == "biene"
    z = zeichenauftraege.ZEICHENAUFTRAEGE["biene"]
    assert z["nr"] == 15 and len(z["merkmale"]) >= 4
    gesamt = " ".join(z["merkmale"]).lower()
    for wort in ("kopf", "brust", "hinterleib", "sechs beine", "fühler", "flügel"):
        assert wort in gesamt, wort
    assert set(z["stufen"]) == {"A", "B", "C"} and z["stufen"]["B"] and z["stufen"]["C"]
    for n, cfg in a["niveaus"].items():
        assert cfg["aufgabe"] and cfg["hinweis"] and len(cfg["elemente"]) >= 6, n
        assert {"Kopf", "Brust", "Hinterleib", "sechs Beine", "zwei Fühler", "Flügel"} <= set(cfg["elemente"]), n
    # A: nur die Basisliste, B und C wachsen
    assert len(a["niveaus"]["A"]["elemente"]) < len(a["niveaus"]["B"]["elemente"]) < len(a["niveaus"]["C"]["elemente"])
    assert "Beschriftung" in " ".join(a["niveaus"]["C"]["elemente"])
    for wort in ("Kopf", "Brust", "Hinterleib", "sechs Beine", "zwei Fühler", "Flügel"):
        assert wort in a["niveaus"]["A"]["aufgabe"], wort
    assert "schreibe" not in a["niveaus"]["A"]["aufgabe"].lower()
    prompt = zeichenauftraege.prompt_text("biene", a["niveaus"]["B"]["aufgabe"], "B")
    assert "Streifen" in prompt and "Prüfliste" in prompt


def test_gestrichene_aufgaben_sind_weg(aufgaben):
    """10, 11, 12, 13, 14, 16 und 17 der ersten Fassung gibt es nicht mehr (Platz für das Forschen, Grenze 12 Stationen)."""
    for nr in (10, 11, 12, 13, 14, 16, 17):
        assert nr not in aufgaben and nr not in AUFGABEN_PLAN, nr


def test_modell_wird_ehrlich_eingeordnet(aufgaben):
    """Das Modell ist ein Nachbau (Prototyp): die Tabelle zum Innenleben sagt es, die Lesestrecke nennt die echte Größe."""
    assert "Nachbau am Computer" in aufgaben[54]["auftrag"] and "Farben" in aufgaben[54]["auftrag"]
    erster = lesen_koerper.LESESTRECKEN["koerper"]["abschnitte"][0]["text"]
    assert "12 bis 14 Millimeter" in erster and "Arbeiterin" in erster
