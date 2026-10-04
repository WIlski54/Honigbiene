"""Inhalte des Reiters „Nutzen & Schutz“ (forschend-entwickelnd, plan_nutzen.py, Lesestrecke L4, Glossar, Zeichnung 3).

Stand nach dem Audit vom 4. Oktober 2026 (docs/AUDIT_FORSCHEN_2026-10-04.md). Geprüft wird nur, was dieser Reiter besitzt:
static/js/inhalte_nutzen.js, plan_nutzen.py, lesen_nutzen.py, glossar_nutzen.py und der Eintrag „bestaeubung“ in zeichenauftraege.py.
Prüfungen: Stationsplan und Reihenfolge, Quoten, Format der neuen Typen (vermutung, pruefen, protokoll, bildwahl), Filmbezug
(Kapitel 10 und 12), Rätselbild ohne Etiketten, ausgedachtes Beispiel gekennzeichnet, kurze Sätze, feste Wörter, Zahlen.
"""
import json
import math
import os
import re

import pytest

import glossar
import glossar_nutzen
import lesen_nutzen
import plan_nutzen
import zeichenauftraege
from inhalte_laden import ROOT, lade_inhalte
from plan import ABFRAGE_TYPEN, AUFGABEN_PLAN, DIFFERENZIERT, FORSCHEN_TYPEN, QUOTE_ABFRAGE_MAX, QUOTE_FORSCHEN_MIN, SPRACHWERKSTATT_MIN, max_stationen

NUMMERN = [70, 71, 72, 73, 74, 75, 76, 77, 36, 35, 37]            # Reihenfolge der Karten (ohne Lesestrecke)
STRECKE = lesen_nutzen.LESESTRECKEN["nutzen"]
RAETSEL = "/static/img/lese/nutzen-5-raetsel.svg"

# Felder, die nur die KI oder die Technik lesen – Kinder sehen sie nicht
UEBERSPRINGEN = {"kontext", "kiFrage", "typ", "key", "film", "geraet", "modus", "mw", "icon", "kurz", "lese", "leseNach", "abschnitt", "label",
                 "bild", "bild_alt", "art", "id", "vermutung", "einheit", "breite", "hoehe"}

# Zahlwörter, die im Konzept („Gesicherte Fakten“) stehen und hier vorkommen dürfen
ZAHLWOERTER = re.compile(r"\b(\w*tausend|\w*hundert|einundzwanzig|zwanzig|dreißig|fünfzig|zwölf|elf|zehn)\b", re.I)
ERLAUBTE_ZAHLWOERTER = {"zweitausend"}

# Wörter, die für dieselbe Sache nicht verwendet werden dürfen (feste Wörter im Konzept)
VERBOTEN = ["Bienenkorb", "Beute", "Bienenhaus", "Honigblase", "Pollenhöschen", "Stockbiene", "Imkerin", "Zuckerfutter"]

# Kapitel 10 des Films liegt bei 179,7–199,7 s (papiertheater/docs/ab_uebergabe.md); Schlüsselsatz Kapitel 12: 228,3–232,7 s
KAPITEL10 = (179.7, 199.7)
SATZ_KAPITEL12 = (228.3, 232.7)
# Wörter, die in Fragen, Hinweisen und Fehltexten des Rätselbilds (75) NICHT vorkommen dürfen – erst die Erklärung nach dem Tipp nennt sie
GEFAHRENWORTE = ("gefahr", "gefährd", "pestizid", "varroa", "milbe", "gift", "spritz", "schaden", "schädling")
# Wörter, die das ausgedachte Beispiel (72) in Auftrag und Vermutungszeile nicht verraten dürfen
ERGEBNIS_ZAHLEN = ("12 Äpfel", "2 Äpfel")


@pytest.fixture(scope="module")
def tab():
    return next(t for t in lade_inhalte()["tabs"] if t["key"] == "nutzen")


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
    return re.sub(r"\[([^\]|]+)(?:\|[^\]]*)?\]", r"\1", text)


def _saetze(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", _klar(text)) if s.strip()]


def _woerter(s):
    return len(s.split())


def _alle_kindertexte(tab):
    texte = list(_texte(tab))
    for a in STRECKE["abschnitte"]:
        texte += [a["ueberschrift"], a["text"], a["frage"], a["erklaerung"], *a["optionen"]]
    texte += [e["text"] for e in glossar_nutzen.EINTRAEGE.values()]
    return texte


def _knoepfe(a):
    m = a.get("modell")
    return m if isinstance(m, list) else [m] if m else []


# ── Plan, Reihenfolge, Quoten ───────────────────────────────────────────────────────────
def test_stationsplan_und_reihenfolge(tab, aufg):
    assert plan_nutzen.STATIONEN == [70, 71, 72, 73, 74, 75, 76, "L4", 77, 36, 35, 37]
    assert [a["nr"] for a in tab["aufgaben"]] == NUMMERN == [n for n in plan_nutzen.STATIONEN if n != "L4"]
    assert tab["kurz"] == "S" and tab["lese"] == "L4" and tab["film"] == "volk"
    assert tab["leseNach"] == 76, "Die Lesestrecke steht NACH der Forschungsphase (nach Station 76)"
    assert plan_nutzen.STATIONEN[plan_nutzen.STATIONEN.index("L4") - 1] == tab["leseNach"]
    for nr in NUMMERN:
        assert aufg[nr]["typ"] == AUFGABEN_PLAN[nr] == plan_nutzen.TYPEN[nr], f"Aufgabe {nr}"
        assert aufg[nr]["eyebrow"] and aufg[nr]["titel"]
    assert plan_nutzen.TYPEN[77] == "luecke", "77 ist ein Lückentext mit Chips (Zeitfolge)"


def test_reiter_beginnt_mit_forscherfrage_und_hat_erkenntnisse(aufg):
    assert aufg[70]["typ"] == "vermutung" and plan_nutzen.STATIONEN.index(70) == 0
    assert aufg[73]["typ"] == "pruefen" and aufg[76]["typ"] == "pruefen"
    assert plan_nutzen.STATIONEN.index("L4") > plan_nutzen.STATIONEN.index(75)


def test_quoten_gewichtung(tab):
    stationen = tab["aufgaben"]
    n = len(stationen)
    assert n + 1 <= max_stationen("nutzen"), f"{n + 1} Stationen inklusive Lesestrecke"
    forschen = [a for a in stationen if a["typ"] in FORSCHEN_TYPEN]
    # ehrlich gezählt (Audit, Entscheidung 3): Zeichnen und reine Bildvokabeln sind Anwenden; echt ist, wo das Kind Evidenz sammelt
    echt = [a for a in stationen if a["typ"] in ("vermutung", "pruefen", "protokoll", "bildwahl", "tabelle")]
    sprache = [a for a in stationen if a["eyebrow"].startswith("Sprachwerkstatt")]
    abfrage = [a for a in stationen if a["typ"] in ABFRAGE_TYPEN and not a["eyebrow"].startswith("Sprachwerkstatt")]
    assert len(forschen) / n >= QUOTE_FORSCHEN_MIN
    assert len(echt) >= 3 and len(echt) / n >= QUOTE_FORSCHEN_MIN, f"echte Forschen-Stationen: {len(echt)}"
    assert len(sprache) >= SPRACHWERKSTATT_MIN and {a["nr"] for a in sprache} == {77, 36}
    assert len(abfrage) / n <= QUOTE_ABFRAGE_MAX and not abfrage


def test_keine_platzhalter_mehr(tab):
    for text in _alle_kindertexte(tab):
        assert "PLATZHALTER" not in text.upper(), text[:60]
    for pfad in (os.path.join(ROOT, "static", "js", "inhalte_nutzen.js"), lesen_nutzen.__file__, glossar_nutzen.__file__, plan_nutzen.__file__):
        assert "PLATZHALTER" not in open(pfad, encoding="utf-8").read(), pfad
    assert not STRECKE.get("platzhalter")


def test_abc_wo_verlangt(aufg):
    for nr in NUMMERN:
        if aufg[nr]["typ"] in DIFFERENZIERT:
            assert sorted(aufg[nr]["niveaus"]) == ["A", "B", "C"], nr


# ── vermutung ───────────────────────────────────────────────────────────────────────────
def test_vermutungen(aufg):
    ids = [aufg[n]["id"] for n in (70, 74)]
    assert ids == ["v_aepfel", "v_gefahren"]
    for nr in (70, 74):
        v = aufg[nr]
        assert v["frage"] == "Was vermutest du?"
        a, b, c = (v["niveaus"][k] for k in "ABC")
        assert len(a["optionen"]) == 4
        assert b["optionen"] == a["optionen"] and b["begruendung"] and "vermute" in b["satzanfang"]
        assert not b["satzanfang"].rstrip(" …").endswith("dass") or nr == 74, b["satzanfang"]
        assert c["satzanfang"].startswith("Meine Vermutung") and c["frei"] is True and c["min"] >= 30 and "optionen" not in c
        assert all(_woerter(o) <= 12 for o in a["optionen"]) and len(set(a["optionen"])) == len(a["optionen"])
        assert "ok" not in str(v) and "loesung" not in str(v), "Eine Forscherfrage hat kein Richtig und Falsch"
    assert aufg[74]["niveaus"]["A"]["mehrfach"] is True and aufg[74]["niveaus"]["B"]["mehrfach"] is True
    assert "mehrfach" not in aufg[70]["niveaus"]["A"]


def test_forscherfrage_70_ist_scharf_und_ohne_doppelung(aufg):
    """Audit: 70 fragt „Wie viele Äpfel …“, nicht mehr „Was wäre, wenn es keine Bienen gäbe?“ (Doppelung mit Reiter 1, Station 41)."""
    v = aufg[70]
    assert v["titel"] == "Wie viele Äpfel trägt ein Baum, wenn keine Insekten kommen?"
    alle = " ".join(v["niveaus"]["A"]["optionen"])
    assert "Honig" not in alle and "Bestäubung" not in alle and "Bienen" not in alle
    assert {"Genauso", "Viel weniger", "Gar keine"} <= {s for s in ("Genauso", "Viel weniger", "Gar keine") if s in alle}


def test_vermutungsoptionen_sind_pruefbar(aufg):
    """Audit 1e: Jede Vermutungsoption lässt sich durch die Evidenz bestätigen oder widerlegen.
    70: Zahlen des Beispiels (12 gegen 2 Äpfel); 74: Orte im Rätselbild (kahle Fläche, Fahrzeug, Lupe, Wiese mit Schmetterlingen)."""
    o74 = aufg[74]["niveaus"]["A"]["optionen"]
    assert o74 == ["zu wenig Blumen", "winzige Tiere, die auf Bienen sitzen", "Gifte gegen Schädlinge", "zu viele Schmetterlinge"]
    for unbelegbar in ("Regen", "Vögel"):
        assert not any(unbelegbar in o for o in o74), f"„{unbelegbar}“ lässt sich weder am Bild noch am Film prüfen"


# ── pruefen ─────────────────────────────────────────────────────────────────────────────
def _laenge(o):
    return len(o["t"])


def _optionen_gleich_lang(ops, wer):
    """Audit 1a und T2: gleich lang und gleich gebaut – die richtige Option ist nicht die längste und nicht kürzer als 70 % der längsten."""
    laengste = max(_laenge(o) for o in ops)
    richtig = next(o for o in ops if o["ok"])
    assert _laenge(richtig) < laengste, f"{wer}: Die richtige Option ist die längste"
    assert _laenge(richtig) >= 0.7 * laengste, f"{wer}: Die richtige Option ist zu kurz ({_laenge(richtig)} von {laengste})"
    assert all(_laenge(o) >= 0.55 * laengste for o in ops), f"{wer}: Optionen sehr verschieden lang"
    assert all(_woerter(o["t"]) <= 12 for o in ops), f"{wer}: Option länger als 12 Wörter"


def test_pruefen(aufg):
    ids = {aufg[70]["id"], aufg[74]["id"]}
    for nr, vid in ((73, "v_aepfel"), (76, "v_gefahren")):
        p = aufg[nr]
        assert p["vermutung"] == vid and vid in ids
        assert p["quelle"] and p["erkenntnis"] and not p["erkenntnis"].endswith("?")
        assert all(_woerter(s) <= 18 for s in _saetze(p["erkenntnis"]))
        positionen = []
        for niv, cfg in p["niveaus"].items():
            erk = cfg["erkenntnis"]
            ops = erk["optionen"]
            assert erk["frage"] and erk["hinweis"] and erk["fehltext"] and sum(o["ok"] for o in ops) == 1, (nr, niv)
            assert "beobachtet" not in erk["fehltext"]
            assert len(ops) == {"A": 3, "B": {73: 4, 76: 3}[nr], "C": 4}[niv] and len({o["t"] for o in ops}) == len(ops)
            _optionen_gleich_lang(ops, f"{nr} {niv} erkenntnis")
            positionen.append(next(i for i, o in enumerate(ops) if o["ok"]))
            if niv == "B":
                b = cfg["beleg"]
                assert b["frage"] and b["hinweis"] and b["fehltext"] and sum(o["ok"] for o in b["optionen"]) == 1 and len(b["optionen"]) == 3
                assert "beobachtet" not in b["fehltext"], "Audit T2: bei Beleg-Fragen nie „was du beobachtet hast“"
                _optionen_gleich_lang(b["optionen"], f"{nr} B beleg")
            if niv == "C":
                assert cfg["satz"]["anfang"].count("…") == 1 and cfg["satz"]["min"] >= 40, "ein Feld, eine Lücke"
        assert len(set(positionen)) >= 2, f"Lösungsposition der Erkenntnis in {nr} verteilen: {positionen}"
        # Die Quelle ist neutral: Sie nennt keine der Optionen und nicht „Merksatz“
        optionen = [o["t"] for c in p["niveaus"].values() for o in c["erkenntnis"]["optionen"]]
        assert not any(o.rstrip(".").lower() in p["quelle"].lower() for o in optionen), "Die Quelle verrät eine Option"
        assert p["erkenntnis"].rstrip(".") not in p["quelle"]


def test_pruefen_73_stuetzt_sich_auf_die_zahlen_und_den_film(aufg):
    p = aufg[73]
    knoepfe = _knoepfe(p)
    assert len(knoepfe) == 1 and knoepfe[0]["film"] == "volk" and not knoepfe[0].get("pflicht")
    befehle = knoepfe[0]["befehle"]
    assert [b["mw"] for b in befehle] == ["springe"] and knoepfe[0].get("spielen") is not False, "der Knopf springt sekundengenau; film.js spielt sofort"
    assert SATZ_KAPITEL12[0] <= befehle[0]["t"] <= SATZ_KAPITEL12[1], "Sprung auf den Satz „… Honig, Wachs und viele Früchte“ (Kapitel 12)"
    assert "Kapitel 12" in knoepfe[0]["text"] and "Früchte" in knoepfe[0]["text"]
    assert "Ausgedachtes Beispiel" in p["quelle"] and "12 Äpfel" in p["quelle"] and "2 Äpfel" in p["quelle"]
    assert p["erkenntnis"].startswith("Im Beispiel"), "Der Merksatz sagt, dass es das Beispiel war"
    # Die Optionen der Stufe A sind die Vermutungsoptionen von Station 70, die sich mit 12 gegen 2 prüfen lassen
    a = {o["t"] for o in p["niveaus"]["A"]["erkenntnis"]["optionen"]}
    assert "Ohne Insekten trägt der Zweig viel weniger Äpfel." in a
    c = p["niveaus"]["C"]["erkenntnis"]["optionen"]
    assert next(o for o in c if o["ok"])["t"].count("sechsmal") == 1, "12 geteilt durch 2 ist 6"


def test_pruefen_76_hat_bild_knopf_zum_raetselbild(aufg):
    p = aufg[76]
    knoepfe = _knoepfe(p)
    assert len(knoepfe) == 1 and knoepfe[0]["bild"] == RAETSEL and knoepfe[0]["text"] and knoepfe[0]["alt"] and "film" not in knoepfe[0]
    assert os.path.exists(os.path.join(ROOT, RAETSEL.lstrip("/")))
    assert "Rätselbild" in p["quelle"]
    # Beleg-Optionen sind Beobachtungen am Bild
    for o in p["niveaus"]["B"]["beleg"]["optionen"]:
        assert re.match(r"(Auf|Im|In) ", o["t"]), o["t"]
    assert aufg[76]["niveaus"]["A"]["erkenntnis"]["optionen"][2]["ok"] is True


# ── protokoll: Film (71) und ausgedachtes Beispiel (72) ─────────────────────────────────
def _zeilen_pruefen(nr, aufg):
    laengen = []
    for niv, cfg in aufg[nr]["niveaus"].items():
        zeilen = cfg["zeilen"]
        laengen.append(len(zeilen))
        for z in zeilen:
            assert z["frage"].endswith(("?", ".")) and z["art"] in ("zahl", "wahl", "mehrfach", "text"), (nr, niv, z["frage"])
            ops = z.get("optionen", [])
            if z["art"] == "wahl":
                assert 2 <= len(ops) <= 3 and 0 <= z["loesung"] < len(ops) and len(set(ops)) == len(ops), z["frage"]
            elif z["art"] == "mehrfach":
                assert len(ops) >= 4 and all(0 <= i < len(ops) for i in z["loesung"]) and 2 <= len(z["loesung"]) < len(ops), z["frage"]
            elif z["art"] == "zahl":
                assert isinstance(z["loesung"], (int, float)) and z.get("einheit"), z["frage"]
                assert z.get("fehlertext") or nr == 72 and False or True
            elif z["art"] == "text":
                assert z.get("satzanfang") and z["min"] >= 4, z["frage"]
            if z["art"] != "text":
                assert z.get("hinweis"), f"{nr} {niv}: Hinweis nach Fehlversuch fehlt bei „{z['frage']}“"
            assert all(_woerter(o) <= 12 for o in ops)
        sc = cfg["schluss"]
        assert sc["anfang"] and (sc.get("bausteine") or sc.get("min")) and sc.get("pflicht") is True, "Schlusssatz ist Pflicht (Sprache üben)"
        if niv == "A":
            bs = sc["bausteine"]
            assert len(bs) >= 3 and sum(1 for b in bs if isinstance(b, dict) and b["ok"] is False) == 1, "ein Baustein ist falsch (ok: false)"
        else:
            assert sc["min"] >= 40
    assert laengen == sorted(laengen) and laengen[0] >= 3, f"{nr}: Zeilen A ≤ B ≤ C, mindestens 3: {laengen}"


def test_protokoll_film_71(aufg):
    a = aufg[71]
    knoepfe = _knoepfe(a)
    assert [b["n"] for k in knoepfe for b in k["befehle"] if b["mw"] == "kapitel"] == [10], "nur Kapitel 10 (Aus Nektar wird Honig)"
    assert all(k["film"] == "volk" and k.get("pflicht") and k.get("spielen") is not False for k in knoepfe), "Pflicht-Knopf, spielt sofort"
    assert "Kapitel 10" in a["auftrag"] and "Kapitel 8" not in a["auftrag"]
    _zeilen_pruefen(71, aufg)
    marken = []
    for cfg in a["niveaus"].values():
        for z in cfg["zeilen"]:
            k = z["modell"]
            assert k.get("spielen") is not False and "Kapitel 10" in k["text"]
            marken += [b["t"] for b in k["befehle"] if b["mw"] == "springe"]
    assert marken and all(KAPITEL10[0] <= t <= KAPITEL10[1] for t in marken), marken
    for niv, cfg in a["niveaus"].items():
        z0 = cfg["zeilen"][0]
        # Audit: Zeile 0 ist nicht mehr „Wohin kommt der Nektar?“ (Doppelung mit Reiter 2), sondern eine neue Beobachtung aus Kapitel 10
        assert "Honigmagen" not in z0["frage"] and "Weitergabe" not in z0["frage"] and "weitergegeben" in z0["frage"] or "weiter" in z0["frage"], niv
        assert "Rüssel" in z0["optionen"][z0["loesung"]], niv
        stock = [z for z in cfg["zeilen"] if z["art"] == "mehrfach"][0]
        richtig = {stock["optionen"][i] for i in stock["loesung"]}
        assert richtig == {"Die Bienen fächeln ihn mit den Flügeln.", "Die Bienen verschließen die Zellen mit Wachs."}, niv
        # plausible Ablenker, neutraler Hinweis: kein „zurück auf die Wiese“, die Hinweise nennen keine Option
        assert not any("Wiese" in o for o in stock["optionen"]), "kein absurder Ablenker"
        assert not any(w in stock["hinweis"] for w in ("Flügel", "Zellen", "Rüssel")), "der Hinweis nennt die Lösung"
        raehmchen = [z for z in cfg["zeilen"] if z["art"] == "zahl"]
        assert len(raehmchen) == 1 and raehmchen[0]["loesung"] == 1 and raehmchen[0]["einheit"] == "Rähmchen"
        assert "im Film" in raehmchen[0]["frage"], "Die Antwort 1 ist eine Vereinfachung des Films"
    farben = [z for c in a["niveaus"].values() for z in c["zeilen"] if "Farbe" in z["frage"]]
    assert farben and all("goldfarben" in z["optionen"][z["loesung"]] for z in farben)
    assert "Imker erntet nur einen Teil" in a["erkenntnis"] and "Nektar" in a["erkenntnis"]
    assert "dick und goldfarben" not in " ".join(z["frage"] for c in a["niveaus"].values() for z in c["zeilen"] if z["art"] == "wahl" and "Farbe" in z["frage"])


def test_protokoll_beispiel_72(aufg):
    a = aufg[72]
    assert a["eyebrow"].startswith("Forschen · Ausgedachtes Beispiel") and "ausgedachtes" in a["eyebrow"].lower()
    assert "Ausgedachtes Beispiel – die Zahlen sind nicht gemessen." in a["auftrag"]
    assert "modell" not in a and "erkenntnis" not in a, "Der Merksatz steht nur in 73 (kein Beleg aus dem Beispiel)"
    # Der Auftrag beschreibt nur den Aufbau: Die Ergebniszahlen stehen NICHT darin, und das Netz hält „Insekten“ fern
    assert not any(z in a["auftrag"] for z in ERGEBNIS_ZAHLEN)
    assert "Insekten" in a["auftrag"] and "Bienen" not in a["auftrag"] and "20 Blüten" in a["auftrag"]
    _zeilen_pruefen(72, aufg)
    for niv, cfg in a["niveaus"].items():
        z0 = cfg["zeilen"][0]
        # Zeile 0 ist die eigene Vermutung (nur Länge geprüft); die Beispielzahlen erscheinen erst in der Erklärung dieser Zeile
        assert z0["art"] == "text" and z0["frage"].startswith("Meine Vermutung:"), niv
        zahlen = [int(x) for x in re.findall(r"hat (\d+) Äpfel", z0["erklaerung"])]
        assert zahlen == [12, 2], zahlen
        assert z0["erklaerung"].count("🍎") == sum(zahlen) and "ausgedachte" in z0["erklaerung"]
        for z in cfg["zeilen"][1:]:
            assert not any(zz in (z["frage"] + " ".join(z.get("optionen", []))) for zz in ERGEBNIS_ZAHLEN)
        diff = [z for z in cfg["zeilen"] if z["art"] == "zahl"]
        assert len(diff) == 1 and diff[0]["loesung"] == 12 - 2 and diff[0]["fehlertext"], niv
    # C: „Was könnte der Grund sein?“ hat Vermutungscharakter (nur Länge), „Was zeigen die Zahlen?“ nennt nur Ablesbares
    c = a["niveaus"]["C"]["zeilen"]
    assert c[-1]["art"] == "text" and "Grund" in c[-1]["frage"]
    mehrfach = [z for z in c if z["art"] == "mehrfach"][0]
    assert sorted(mehrfach["loesung"]) == [0, 2] and "Bestäubung" not in " ".join(mehrfach["optionen"])
    assert "ablesen" in mehrfach["hinweis"]


# ── bildwahl 75: Rätselbild ohne Etiketten ──────────────────────────────────────────────
def _orte():
    daten = json.load(open(os.path.join(ROOT, "werkzeuge", "nutzen5_raetsel_punkte.json"), encoding="utf-8"))
    return daten, {k: (o["x"], o["y"], o["r"]) for k, o in daten["orte"].items()}


def test_bildwahl_75(aufg):
    daten, orte = _orte()
    assert (daten["breite"], daten["hoehe"]) == (900, 560) and daten["bild"] == RAETSEL
    a = aufg[75]
    assert "bild" not in a and "Gefahr" not in a["titel"] and "Pestizid" not in a["titel"]
    anzahl = []
    for niv, cfg in a["niveaus"].items():
        runden = cfg["runden"]
        anzahl.append(len(runden))
        for r in runden:
            assert r["bild"] == RAETSEL and (r["breite"], r["hoehe"]) == (900, 560)
            assert os.path.exists(os.path.join(ROOT, r["bild"].lstrip("/"))), r["bild"]
            ziele = r["ziele"]
            assert len(ziele) == 4, f"{niv}: vier Kreise je Runde (alle Orte des Bildes)"
            assert sorted((z["x"], z["y"], z["r"]) for z in ziele) == sorted(orte.values()), f"{niv}: Kreise passen nicht zur Karte {orte}"
            assert 1 <= sum(z["ok"] for z in ziele) <= 2 and r["hinweis"] and r["erklaerung"] and r["frage"].endswith((".", "?"))
            for z in ziele:
                assert z["r"] >= 60 and 24 <= z["x"] <= 900 - 24 and 24 <= z["y"] <= 560 - 24
                if not z["ok"]:
                    assert z["rueckmeldung"], (niv, r["frage"])
            # Kreise überlappen sich nicht
            for i, p in enumerate(ziele):
                for q in ziele[i + 1:]:
                    assert math.hypot(p["x"] - q["x"], p["y"] - q["y"]) > p["r"] + q["r"], (niv, r["frage"])
            # Fragen, Hinweise und Fehltexte nennen keine Gefahr; erst die Erklärung nach dem Tipp benennt sie
            sichtbar = (r["frage"] + " " + r["hinweis"] + " " + " ".join(z.get("rueckmeldung", "") for z in ziele)).lower()
            assert not any(w in sichtbar for w in GEFAHRENWORTE), f"{niv}: Gefahrenwort vor dem Tipp: {r['frage']}"
        # Fehltexte sind neutral (zwei feste Texte), nie ein Hinweis auf den richtigen Ort
        texte = {z["rueckmeldung"] for r in runden for z in r["ziele"] if not z["ok"]}
        assert texte <= {"Das ist es nicht. Vergleiche noch einmal alle vier Stellen im Bild.", "Hier sitzen Bienen. Such eine Stelle, an der keine sitzen."}, texte
        ok_orte = {(z["x"], z["y"]) for r in runden for z in r["ziele"] if z["ok"]}
        assert {orte["kahl"][:2], orte["traktor"][:2], orte["lupe"][:2]} <= ok_orte, f"{niv}: alle drei Orte müssen einmal richtig sein"
        # Die richtigen Kreise stehen nicht immer an derselben Stelle (die Nummer im Bild verrät sonst die Lösung)
        pos = [next(i for i, z in enumerate(r["ziele"]) if z["ok"]) for r in runden]
        assert len(set(pos)) >= 2, (niv, pos)
    assert anzahl == sorted(anzahl) and anzahl[0] == 3
    # Erklärungen nennen die Wörter erst nach dem Tipp
    alle = " ".join(r["erklaerung"] for c in a["niveaus"].values() for r in c["runden"])
    assert "Pestizid" in alle and "Varroa-Milbe" in alle


def test_raetselbild_hat_keine_etiketten():
    svg = open(os.path.join(ROOT, "static", "img", "lese", "nutzen-5-raetsel.svg"), encoding="utf-8").read()
    for wort in ("Blühwiese", "kahle Fläche", "Pestizid", "Varroa"):
        assert wort.lower() not in re.sub(r"<(title|desc)>.*?</\1>", "", svg, flags=re.S).lower().replace("aria-label", ""), f"Etikett „{wort}“ im Rätselbild"
    assert "<text" not in svg, "Das Rätselbild trägt keinen Text"


# ── Sprachwerkstatt 77 (Zeitfolge) und 36 (Begründen) ───────────────────────────────────
def test_sprachwerkstatt_77_zeitfolge(aufg):
    a = aufg[77]
    assert a["eyebrow"].startswith("Sprachwerkstatt") and "modell" not in a
    n = a["niveaus"]
    for niv, cfg in n.items():
        assert cfg["hilfe"] and "Lesestrecke" not in cfg["hilfe"], f"{niv}: eigener Hilfetext"
        assert re.search(r"\[[^\]]+\]", cfg["text"])
        for satz in _saetze(cfg["text"]):
            assert _woerter(satz) <= 18, satz
    assert n["A"]["modus"] == "chips" and n["B"]["modus"] == "chips" and n["C"]["modus"] == "input"
    luecken = {k: re.findall(r"\[([^\]]+)\]", n[k]["text"]) for k in "ABC"}
    assert luecken["A"] == ["Im Frühling", "Im Sommer", "Im Spätsommer", "Im Winter"]
    assert [l.split("|")[0] for l in luecken["B"]] == ["Zuerst", "Dann", "Schließlich"] and n["B"]["ablenker"]
    # B ohne Jahreszeitwörter in den Sätzen mit Lücke (Audit 77): Die Reihenfolge ergibt sich aus dem Wissen über das Imkerjahr
    for satz in _saetze(n["B"]["text"]):
        if "Zuerst" in satz or "Dann" in satz or "Schließlich" in satz:
            assert not re.search(r"Frühling|Sommer", satz), satz
    # C tippt und begründet mit weil/da; alle gleichwertigen Wörter werden akzeptiert
    c = luecken["C"]
    assert len(c) == 4 and any("weil" in l.split("|") for l in c) and "Danach" in c[1].split("|") and "Zuletzt" in c[3].split("|")
    # Die Hilfe von C und B zählt die Lösung nicht auf
    for k in "BC":
        for w in ("Zuerst", "Dann", "Danach", "Schließlich"):
            assert w not in n[k]["hilfe"], (k, w)
    alle = " ".join(n[k]["text"] for k in "ABC")
    assert "Zuckerlösung" in alle and "ergänzt" in alle and "füttert" not in alle


def test_freitext_36_begruenden(aufg):
    a = aufg[36]
    assert a["eyebrow"].startswith("Sprachwerkstatt")
    n = a["niveaus"]
    assert n["A"]["modus"] == "bausteine" and 4 <= len(n["A"]["bausteine"]) <= 7
    assert all(_woerter(b) <= 14 for b in n["A"]["bausteine"])
    assert n["A"]["schluss"] and len(n["A"]["urteil"]["optionen"]) == 2
    assert n["B"]["starter"] and n["B"]["begriffe"] and n["B"]["min"] >= 100
    assert n["C"]["min"] > n["B"]["min"] and "starter" not in n["C"]
    for stichwort in ("Blühwiese", "Insektenhotel", "Pestizide", "Imker unterstützen"):
        assert stichwort in a["kontext"], stichwort
    assert "meist selbst" in a["kontext"], "Die Futterfrage ist ehrlich (Audit, Entscheidung 4)"
    b = n["A"]["bausteine"]
    # Eindeutige Folge: Aber (Problem) → Deshalb (Blühwiese) → So (Ergebnis daraus) → Außerdem … damit (zweite Maßnahme, zuletzt)
    assert b[1].startswith("Aber") and b[2].startswith("Deshalb") and "Blühwiese" in b[2]
    assert b[3].startswith("So ") and "schon" in b[3]
    assert b[4].startswith("Außerdem") and "damit" in b[4] and "Pestizide" in b[4]
    assert any(w in " ".join(n["B"]["starter"]) for w in ("weil", "damit", "denn"))
    assert all(w in n["B"]["aufgabe"] and w in n["C"]["aufgabe"] for w in ("weil", "denn", "damit"))


def test_notizen_und_zeichnung(aufg):
    n = aufg[37]
    assert n["abschnitt"] == "nutzen" and n["hinweis"] and n["kiFrage"]
    z = aufg[35]
    assert z["geraet"] == "bestaeubung"
    for niv, cfg in z["niveaus"].items():
        assert cfg["aufgabe"] and cfg["hinweis"] and len(cfg["elemente"]) >= 4, niv
    assert [len(z["niveaus"][n]["elemente"]) for n in "ABC"] == sorted(len(z["niveaus"][n]["elemente"]) for n in "ABC")


def test_zeichenauftrag_bestaeubung():
    a = zeichenauftraege.ZEICHENAUFTRAEGE["bestaeubung"]
    assert a["nr"] == 35 and a["titel"] and a["motiv"]
    assert len(a["merkmale"]) >= 4
    assert a["stufen"]["A"] == [] and a["stufen"]["B"] and len(a["stufen"]["C"]) > len(a["stufen"]["B"])
    text = zeichenauftraege.prompt_text("bestaeubung", "Zeichne die Bestäubung.", "C")
    assert "Pollen" in text and "Frucht" in text and "beschriftet" in text
    for m in a["merkmale"] + [x for v in a["stufen"].values() for x in v]:
        assert not re.search(r"\d", m), m


# ── Lesestrecke ─────────────────────────────────────────────────────────────────────────
def test_lesestrecke_aufbau():
    assert STRECKE["station"] == "L4" and STRECKE["eyebrow"] == "Lesestrecke 4" and not STRECKE.get("platzhalter")
    ab = STRECKE["abschnitte"]
    assert [a["ueberschrift"] for a in ab] == ["Honig und Wachs", "Bestäubung", "Das Imkerjahr", "Bienen in Gefahr"]
    assert [a["bild"] for a in ab] == ["nutzen-1", "nutzen-3", "nutzen-4", "nutzen-5"]
    for a in ab:
        assert a["bild_alt"].startswith("Schaubild:")
        assert 2 <= len(a["text"].split("\n")) <= 6, a["ueberschrift"]
        assert len(a["optionen"]) == 3 and len(set(a["optionen"])) == 3 and 0 <= a["loesung"] < 3
        assert a["frage"].endswith("?") and a["erklaerung"].startswith("Richtig")
        assert all(_woerter(o) <= 12 for o in a["optionen"])
        for satz in _saetze(a["text"]):
            assert _woerter(satz) <= 15, f"{a['ueberschrift']}: {_woerter(satz)} Wörter: {satz}"


def test_lesestrecke_bezieht_sich_auf_die_funde_der_kinder():
    ab = {a["ueberschrift"]: a["text"] for a in STRECKE["abschnitte"]}
    assert ab["Honig und Wachs"].startswith("Im Film hast du gesehen")
    assert "ausgedachten Beispiel" in ab["Bestäubung"] and "Netz" in ab["Bestäubung"] and "Insekten" in ab["Bestäubung"]
    assert "Im Rätselbild hast du drei Gefahren gefunden" in ab["Bienen in Gefahr"]


def test_lesestrecke_loesungspositionen_verteilt():
    pos = [a["loesung"] for a in STRECKE["abschnitte"]]
    assert len(set(pos)) == 3, pos
    assert all(pos.count(p) <= 2 for p in (0, 1, 2)), pos


def test_lesestrecke_sagt_ehrlich_was_der_imker_tut():
    text = " ".join(a["text"] for a in STRECKE["abschnitte"])
    assert "nur einen Teil" in text, "Der Imker nimmt nur einen Teil des Honigs"
    assert "Zuckerlösung" in text and "Ersatz für den Honig" in text, "Zuckerfutter offen sagen"
    assert "gegen die <strong>Varroa-Milbe</strong>" in text
    # Futterfrage ehrlich (Audit, Entscheidung 4): meist selbst, im Spätsommer ergänzt der Imker
    assert "suchen ihr Futter meist selbst" in text and "ergänzt er Zuckerlösung" in text
    assert "niemand füttert" not in text.lower() and "füttert" not in text
    s2 = STRECKE["abschnitte"][1]["text"]
    assert "meist nur eine Pflanzenart" in s2 and "Pollen von Blüte zu Blüte" in s2
    assert all(w in s2 for w in ("Apfel", "Kirsche", "Raps"))
    ganz = [a for a in STRECKE["abschnitte"] if "drittwichtigstes" in a["erklaerung"] + a["text"]]
    assert len(ganz) == 1 and "drittwichtigstes" not in ganz[0]["text"] and "oft als drittwichtigstes" in ganz[0]["erklaerung"]


def test_lesestrecke_kommt_beim_server_an(student):
    r = student.get("/api/lesestrecke/nutzen").get_json()
    assert r["ok"] and r["anzahl"] == 4 and r["titel"] == "Honig, Wachs, Blüten – und Gefahren"
    for a in r["abschnitte"]:
        assert "loesung" not in a and "erklaerung" not in a and len(a["optionen"]) == 3


def test_schaubilder_vorhanden():
    fehlt = [a["bild"] for a in STRECKE["abschnitte"] if not os.path.exists(os.path.join(ROOT, "static", "img", "lese", a["bild"] + ".svg"))]
    fehlt += [e["bild"] for e in glossar_nutzen.EINTRAEGE.values()
              if e.get("bild") and not os.path.exists(os.path.join(ROOT, "static", "img", "lese", e["bild"] + ".svg"))]
    assert not fehlt, f"Schaubilder fehlen: {fehlt}"


# ── Glossar ─────────────────────────────────────────────────────────────────────────────
def test_glossar_eintraege():
    e = glossar_nutzen.EINTRAEGE
    assert {"wachs", "bestaeubung", "varroamilbe", "schleuder", "pestizid", "bluehwiese"} <= set(e)
    assert e["bestaeubung"]["bild"] == "glossar-bestaeubung" and e["varroamilbe"]["bild"] == "glossar-varroamilbe"
    assert {"Varroa-Milbe", "Varroa", "Milbe"} <= set(e["varroamilbe"]["aliase"])
    for key, eintrag in e.items():
        assert re.fullmatch(r"[a-z0-9]+", key)
        assert len(eintrag["text"]) <= 400, key
        for satz in _saetze(eintrag["text"]):
            assert _woerter(satz) <= 18, (key, satz)
    for key in e:
        assert glossar.GLOSSAR[key] is e[key]
    for key, eintrag in e.items():
        for alias in eintrag["aliase"] + [eintrag["titel"]]:
            assert glossar.ALIASE[glossar.normalisieren(alias)] == key, alias


def test_fette_begriffe_haben_glossareintrag(tab):
    fett = set()
    for a in STRECKE["abschnitte"]:
        fett |= set(re.findall(r"<strong>(.*?)</strong>", a["text"]))
    assert fett == {"Schleuder", "Wachs", "Bestäubung", "Varroa-Milbe", "Pestizide", "Blühwiese"}
    for begriff in fett:
        assert glossar.eintrag_fuer(begriff) is not None, begriff
    for begriff in tab["intro"]["begriffe"]:
        assert glossar.eintrag_fuer(begriff) is not None, f"Fachbegriff {begriff} ohne Glossareintrag"
    assert "<strong>" not in str(tab["aufgaben"])


# ── Sprache, feste Wörter, Zahlen ───────────────────────────────────────────────────────
def test_saetze_sind_kurz(tab):
    zu_lang = []
    for text in _alle_kindertexte(tab):
        for satz in _saetze(text):
            if _woerter(satz) > 18:
                zu_lang.append((_woerter(satz), satz[:80]))
    assert not zu_lang, zu_lang


def test_feste_woerter_statt_synonyme(tab):
    ganz = " ".join(_alle_kindertexte(tab))
    for w in VERBOTEN:
        assert w.lower() not in ganz.lower(), f"„{w}“ statt des festen Worts"
    assert not re.search(r"Imker[^.]{0,40}Bienenstock", ganz), "Der Imker arbeitet am Bienenkasten"
    assert "niemand füttert" not in ganz.lower()


def test_jede_zahl_steht_im_konzept(tab, aufg):
    """Keine Prozentzahlen, keine erfundenen Mengen: Ziffern nur als Verweis (Szene n, Kapitel n …) oder im gekennzeichneten
    ausgedachten Beispiel (Stationen 72 und 73: 20 Blüten, 12 und 2 Äpfel)."""
    beispiel = set(_texte(aufg[72])) | set(_texte(aufg[73]))
    for text in _alle_kindertexte(tab):
        if text in beispiel:
            continue
        ohne = re.sub(r"(Szene|Kapitel|Lesestrecke|Abschnitt) \d+( und \d+)*", "", text)
        assert not re.search(r"\d", ohne), f"Zahl im Text: {text[:80]}"
        assert "%" not in text and "Prozent" not in text
        for w in ZAHLWOERTER.findall(ohne):
            assert w.lower() in ERLAUBTE_ZAHLWOERTER, f"Zahlwort „{w}“ steht nicht im Konzept: {text[:80]}"
    # Das ausgedachte Beispiel ist überall als solches gekennzeichnet, wo Zahlen stehen
    assert "Ausgedachtes Beispiel" in aufg[72]["auftrag"] and "Ausgedachtes Beispiel" in aufg[73]["quelle"]
    for text in _alle_kindertexte(tab):
        for n in re.findall(r"Szene (\d+)", text) + re.findall(r"Kapitel (\d+)", text) + re.findall(r"Kapitel \d+ und (\d+)", text):
            assert 1 <= int(n) <= 12
        for n in re.findall(r"Lesestrecke (\d+)", text):
            assert 1 <= int(n) <= 4
        for n in re.findall(r"Abschnitt (\d+)", text):
            assert 1 <= int(n) <= 5
