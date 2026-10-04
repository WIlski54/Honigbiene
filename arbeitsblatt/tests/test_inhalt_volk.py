"""Inhalte des Reiters „Das Bienenvolk“ (Forscherraum mit dem Film, Stationsplan plan_volk.py, Lesestrecke L3, Glossar, Zeichnung 2).

Geprüft wird nur, was dieser Reiter besitzt: static/js/inhalte_volk.js, plan_volk.py, lesen_volk.py, glossar_volk.py und der Eintrag
„schwaenzeltanz“ in zeichenauftraege.py. Grundregel (ab-bauen, references/film.md): Die Aufgaben passen zum Film – jede Film-Aufgabe
nennt die Filmstelle (Kapitel) und fragt nur, was dort gezeigt oder gesagt wird. Forschend-entwickelnd (docs/FORSCHEN.md): Quoten,
Reihenfolge (Forscherfrage zuerst, Lesestrecke erst nach dem Erkunden), Sprachwerkstatt.
"""
import json
import os
import re
import warnings

import pytest

import glossar
import glossar_volk
import lesen_volk
import plan_volk
import zeichenauftraege
from inhalte_laden import ROOT, lade_inhalte
from forschen_pruefen import gewichtung_probleme
from plan import ABFRAGE_TYPEN, AUFGABEN_PLAN, DIFFERENZIERT, QUOTE_ABFRAGE_MAX, SPRACHWERKSTATT_MIN, max_stationen

NUMMERN = [60, 18, 62, 63, 64, 21, 66, 68, 65, 67, 26]            # Reihenfolge der Karten (ohne Lesestrecke)
STRECKE = lesen_volk.LESESTRECKEN["volk"]
UEBERGABE = os.path.join(os.path.dirname(ROOT), "papiertheater", "docs", "ab_uebergabe.md")
TANZ_JSON = os.path.join(ROOT, "werkzeuge", "tanzraetsel_ziele.json")

GLOSSAR_SCHLUESSEL = ["bienenvolk", "koenigin", "arbeiterin", "drohne", "wabe", "zelle", "raehmchen", "brutraum", "honigraum",
                      "flugloch", "larve", "puppe", "schwaenzeltanz", "ammenbiene", "sammlerin", "waechterin", "wintertraube"]
GLOSSAR_BILDER = {"koenigin": "glossar-koenigin", "drohne": "glossar-drohne", "wabe": "glossar-wabe",
                  "schwaenzeltanz": "glossar-schwaenzeltanz", "wintertraube": "glossar-wintertraube"}

# Felder, die nur die KI oder die Technik lesen – Kinder sehen sie nicht
UEBERSPRINGEN = {"kontext", "kiFrage", "typ", "key", "film", "geraet", "modus", "mw", "icon", "kurz", "lese", "leseNach", "abschnitt",
                 "label", "bild", "bild_alt", "karte", "id", "x", "y", "r", "aliase", "kat", "n", "t", "data", "farbe", "labels",
                 "einheit", "start", "nr", "ok", "multi", "anzahl", "eingabe", "pflicht", "vermutung", "art", "loesung", "min",
                 "breite", "hoehe", "frei", "toleranz"}

# Wörter, die für dieselbe Sache nicht verwendet werden dürfen (feste Wörter im Konzept, DaZ)
VERBOTEN = ["Bienenkorb", "Bienenhaus", "Bienenkiste", "Beute", "Weisel", "Brutnest", "Brutkammer", "Honigkammer",
            "Sammelbiene", "Wächterbiene", "Stockbiene", "Arbeitsbiene", "Bienenkönigin", "Honigwabe", "Pollenhöschen"]

# Zahlen, die in Texten stehen dürfen (Quelle in Klammern): AB_KONZEPT.md „Gesicherte Fakten“ bzw. Film
ERLAUBTE_ZAHLEN = {
    "3",        # Ei 3 Tage; Königin 3–5 Jahre
    "4",        # Film dauert 4 Minuten (Drehbuch)
    "5", "6",   # Königin 3–5 Jahre; Sommerarbeiterin 5–6 Wochen; Winterbiene bis etwa 6 Monate; Larve 6 Tage
    "12", "14",  # Puppe 12 Tage; Arbeiterin 12–14 mm
    "21",       # Entwicklung der Arbeiterin 21 Tage
    "10 000", "50 000",     # Winter etwa 10 000; Sommer bis etwa 50 000
    "2 000",    # Königin bis etwa 2 000 Eier am Tag
    "40",       # Zählbild im Film: 40 Eier stehen für „bis zu zweitausend“ (Übergabe, Vereinfachungen), Aufgabe 68
}
# Falsche Antworten in Schätz- und Zahlenfragen (Ablenker, bewusst nicht im Konzept)
ABLENKER_ZAHLEN = {"20", "200", "20 000", "50", "500", "5 000", "500 000"}


@pytest.fixture(scope="module")
def inh():
    return lade_inhalte()


@pytest.fixture(scope="module")
def tab(inh):
    return next(t for t in inh["tabs"] if t["key"] == "volk")


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
    texte += [e["text"] for e in glossar_volk.EINTRAEGE.values()]
    return texte


def _zahlen(text):
    ohne = re.sub(r"(Reiter|Lesestrecke|Kapitel|Szene|Abschnitt|Aufgabe)\s+\d+(?:(?:,|\sund|\sbis)\s*\d+)*", "", text)
    return re.findall(r"\d+(?: \d{3})*", ohne)


def _knoepfe(obj):
    m = obj.get("modell")
    return m if isinstance(m, list) else [m] if m else []


def _kapitel(k):
    """Kapitel eines Film-Knopfes: Kapitelsprung (kapitel n) oder Satzsprung (springe t; Kapitel n = t // 20 + 1)."""
    b = k["befehle"][0]
    return b["n"] if b["mw"] == "kapitel" else int(b["t"] // 20) + 1


def _alle_knoepfe(a):
    """Alle Film-Knöpfe einer Aufgabe: Aufgabenebene und Zeilen aller Niveaus."""
    liste = list(_knoepfe(a))
    for c in (a.get("niveaus") or {}).values():
        liste += [z["modell"] for z in c.get("zeilen", []) if z.get("modell")]
    return liste


# ── Stationsplan, Reihenfolge, Quoten ────────────────────────────────────────
def test_plan_und_inhalte_stimmen_ueberein(tab, aufg):
    assert tab["lese"] == "L3" and tab["film"] == "volk" and tab["kurz"] == "V"
    assert [n for n in plan_volk.STATIONEN if n != "L3"] == NUMMERN
    assert [a["nr"] for a in tab["aufgaben"]] == NUMMERN
    assert tab["leseNach"] == 66 and plan_volk.STATIONEN[plan_volk.STATIONEN.index("L3") - 1] == 66
    assert plan_volk.STATIONEN[plan_volk.STATIONEN.index("L3") + 1] == 68, "die Filmkritik steht NACH der Lesestrecke (sie belegt die Spalte „in echt“)"
    assert plan_volk.TYPEN == {nr: aufg[nr]["typ"] for nr in NUMMERN}
    for nr in NUMMERN:
        assert AUFGABEN_PLAN[nr] == aufg[nr]["typ"], nr
        if aufg[nr]["typ"] in DIFFERENZIERT:
            assert sorted(aufg[nr]["niveaus"]) == ["A", "B", "C"], nr
    assert tab["intro"]["begriffe"] and len(tab["intro"]["begriffe"]) >= 6


def test_reihenfolge_forscherfrage_zuerst_lesestrecke_spaeter(tab):
    stationen = plan_volk.STATIONEN
    assert len(stationen) == 12 <= max_stationen("volk") == 13, "12 Stationen inklusive Lesestrecke (erlaubt sind 13)"
    assert plan_volk.TYPEN[stationen[0]] == "vermutung", "der Reiter beginnt mit der Forscherfrage"
    assert stationen.index("L3") >= 3, "die Lesestrecke kommt erst nach der ersten Erkundungsphase"
    # die Forschungsphase schließt mit einem pruefen
    letzte_pruefung = max(i for i, nr in enumerate(stationen) if nr != "L3" and plan_volk.TYPEN[nr] == "pruefen")
    assert letzte_pruefung < stationen.index("L3")
    assert plan_volk.TYPEN[stationen[-1]] == "zeichnen", "zum Schluss wird angewendet (Zeichnung)"


def test_quoten_forschen_sprachwerkstatt_abfrage(aufg, inh):
    """Ehrliche Quoten (Audit): Forschen zählt nur, wo das Kind Evidenz sammelt; Wortschatz am Bild (21) und Zeichnen (26) sind Anwenden."""
    n = len(NUMMERN)
    sprach = [nr for nr in NUMMERN if aufg[nr]["eyebrow"].startswith("Sprachwerkstatt")]
    forschen_echt = [nr for nr in NUMMERN if aufg[nr]["typ"] in ("vermutung", "pruefen", "protokoll", "tabelle", "bildwahl")]
    anwenden = [nr for nr in NUMMERN if aufg[nr]["typ"] in ("bildpunkte", "zeichnen")]
    abfrage = [nr for nr in NUMMERN if aufg[nr]["typ"] in ABFRAGE_TYPEN and nr not in sprach]
    assert forschen_echt == [60, 62, 63, 64, 66, 68], "echte Forschen-Stationen laut Audit"
    assert len(forschen_echt) >= 3 and len(forschen_echt) / n >= 0.5, (forschen_echt, n)       # 6 von 11 = 55 %
    assert anwenden == [21, 26] and all(aufg[nr]["eyebrow"].startswith(("Anwenden", "Zeichnen")) for nr in anwenden)
    assert sprach == [65, 67] and len(sprach) >= SPRACHWERKSTATT_MIN, sprach              # 2 von 11 = 18 %
    assert len(abfrage) / n <= QUOTE_ABFRAGE_MAX and abfrage == []
    # die gemeinsame Gewichtungsprüfung (tests/forschen_pruefen.py) hat an diesem Reiter nichts auszusetzen
    assert [p for p in gewichtung_probleme(inh) if p.startswith("volk")] == []


def test_film_ist_das_forschungsinstrument(aufg):
    """Mindestens die Hälfte der echten Forschen-Stationen arbeitet unmittelbar mit dem Film (Aufgaben- oder Zeilenknopf)."""
    forschen = [60, 62, 63, 64, 66, 68]
    mit_film = [nr for nr in forschen if _alle_knoepfe(aufg[nr])]
    assert mit_film == [62, 63, 64, 66, 68], mit_film
    assert len(mit_film) / len(forschen) >= 0.5


def test_keine_platzhalter_mehr(tab):
    alle = " ".join(_alle_kindertexte(tab))
    assert "PLATZHALTER" not in alle.upper()
    assert not STRECKE.get("platzhalter")
    assert len(STRECKE["abschnitte"]) == 4


def test_keine_aufgabennummer_in_kindertexten(tab):
    """Die Anzeige zählt fortlaufend (1, 2, 3 …): In Kindertexten steht keine Aufgaben- oder Stationsnummer."""
    for text in _alle_kindertexte(tab):
        assert not re.search(r"(Aufgabe|Station|Aufgaben)\s+\d+", text), text[:80]
        assert "Reiter 1" not in text and "Reiter 3" not in text, text[:80]


def test_feste_woerter_statt_synonyme(tab):
    text = " ".join(_alle_kindertexte(tab))
    gefunden = [w for w in VERBOTEN if w.lower() in text.lower()]
    assert not gefunden, f"Synonyme statt fester Wörter: {gefunden}"
    assert "Pollenkörbchen" not in text      # der Film sagt „Höschen“; das Pollenkörbchen gehört in Reiter 2


def test_saetze_sind_kurz(tab):
    zu_lang = []
    for text in _alle_kindertexte(tab):
        for satz in _saetze(text):
            if _woerter(satz) > 18:
                zu_lang.append((_woerter(satz), satz[:80]))
    assert not zu_lang, zu_lang
    for a in STRECKE["abschnitte"]:
        for satz in _saetze(a["text"]):
            assert _woerter(satz) <= 15, satz            # Lesetext strenger: höchstens 15 Wörter


def test_jede_zahl_steht_im_konzept(tab):
    fremd = []
    for text in _alle_kindertexte(tab):
        for z in _zahlen(_klar(text)):
            if z not in ERLAUBTE_ZAHLEN and z not in ABLENKER_ZAHLEN:
                fremd.append((z, text[:60]))
    assert not fremd, fremd


def test_erkenntnissaetze_enthalten_nur_gesicherte_zahlen(aufg):
    for nr, a in aufg.items():
        if a.get("erkenntnis"):
            for z in _zahlen(a["erkenntnis"]):
                assert z in ERLAUBTE_ZAHLEN, (nr, z)
            assert 1 <= len(_saetze(a["erkenntnis"])) <= 3 and all(_woerter(s) <= 18 for s in _saetze(a["erkenntnis"])), nr


# ── Forscherfrage und Auswertung ─────────────────────────────────────────────
def test_vermutung_60(aufg, inh):
    a = aufg[60]
    assert a["id"] == "v_chef" and a["frage"] and "Forscherfrage" in a["eyebrow"]
    ids = [x.get("id") for t in inh["tabs"] for x in t["aufgaben"] if x["typ"] == "vermutung"]
    assert len(ids) == len(set(ids)), "Vermutungs-ids eindeutig"
    n = a["niveaus"]
    assert len(n["A"]["optionen"]) == 4 and len(set(n["A"]["optionen"])) == 4
    assert sorted(n["A"]["optionen"]) == sorted(n["B"]["optionen"])
    assert n["B"]["satzanfang"].startswith("Ich vermute") and n["B"]["begruendung"]
    assert n["C"]["satzanfang"].startswith("Ich vermute") and n["C"]["frei"] and n["C"]["min"] >= 20
    # keine Bewertung: kein Feld „ok“ bei Vermutungen
    assert "ok" not in json.dumps(n)
    # die Option, die der Film stützt, steht nicht in beiden Niveaus an derselben Stelle (Positionen verteilt)
    stuetzt = "keine ist der Chef"
    assert [i for i, o in enumerate(n["A"]["optionen"]) if stuetzt in o] != [i for i, o in enumerate(n["B"]["optionen"]) if stuetzt in o]


def test_pruefen_64(aufg, inh):
    """Audit-Entscheidung 1: gleich gebaute, prüfbare Optionen, neutrale Quelle, drei Knöpfe, hinweis."""
    vermutungen = {x.get("id") for t in inh["tabs"] for x in t["aufgaben"] if x["typ"] == "vermutung"}
    assert 61 not in aufg, "Station 61 (pruefen zu v_anzahl) entfällt: die Schätzfrage ist keine Vermutung mehr"
    assert not any(a.get("vermutung") == "v_anzahl" for a in aufg.values())
    assert "v_chef" in vermutungen
    a = aufg[64]
    assert a["vermutung"] == "v_chef" and "Kapitel 5, 7 und 12" in a["eyebrow"]
    assert a["erkenntnis"].startswith("Niemand befiehlt.") and "wechseln mit dem Alter" in a["erkenntnis"] and "arbeitet zusammen" in a["erkenntnis"]
    # neutrale Quelle: verrät keine Option
    assert a["quelle"] == "Schau dir Kapitel 5, 7 und 12 im Film an."
    assert not re.search(r"Befehl|Imker|Königin|zusammen|Alter", a["quelle"])
    # drei Knöpfe mit Satzsprung, spielen sofort ab, Beschriftung nennt das Thema, nicht die Antwort
    knoepfe = _knoepfe(a)
    assert [_kapitel(k) for k in knoepfe] == [5, 7, 12]
    assert [k["befehle"][0]["t"] for k in knoepfe] == [84.7, 121.1, 221.3]       # Satzbeginn minus 0,3 s Vorlauf (Übergabe: 85,0 / 121,4 / 221,6)
    assert all(k["befehle"][-1] == {"mw": "spielen"} and k["befehle"][0]["mw"] == "springe" for k in knoepfe)
    assert not any(re.search(r"Befehl|nicht", k["text"]) for k in knoepfe)
    for n, cfg in a["niveaus"].items():
        e = cfg["erkenntnis"]
        opts = e["optionen"]
        assert sum(o["ok"] for o in opts) == 1 and len({o["t"] for o in opts}) == len(opts), n
        assert e["frage"] and e["hinweis"], f"{n}: erkenntnis.hinweis (nach zwei Fehlern) ist Pflicht"
        # gleich lange Optionen: die richtige ist weder die längste noch kürzer als 70 % der längsten (Zeichen und Wörter)
        laenge = [len(o["t"]) for o in opts]
        ok = next(len(o["t"]) for o in opts if o["ok"])
        assert ok < max(laenge) and ok >= 0.7 * max(laenge), (n, laenge, ok)
        worte = [_woerter(o["t"]) for o in opts]
        assert next(_woerter(o["t"]) for o in opts if o["ok"]) < max(worte) + 1
        assert max(laenge) - min(laenge) <= 12, (n, laenge)
        assert all(_woerter(o["t"]) <= 14 for o in opts)
    # Ablenker sind die Vermutungen aus Station 60 (plausibel, vom Film widerlegt), nicht absurd
    vorschlaege = " ".join(aufg[60]["niveaus"]["A"]["optionen"])
    for satz in ("Die Königin sagt jeder Biene, was sie tun soll.", "Jede Biene macht den ganzen Tag, was sie will.", "Der Imker sagt den Bienen, was sie tun sollen."):
        assert satz in vorschlaege and any(satz in [o["t"] for o in a["niveaus"][n]["erkenntnis"]["optionen"]] for n in "ABC")
    b_cfg, c_cfg = a["niveaus"]["B"], a["niveaus"]["C"]
    # Beleg (B): plausible Fehlbelege, kein trivial falscher („erzählt“), kein Verweis auf die Lesestrecke (kommt danach)
    bo = b_cfg["beleg"]["optionen"]
    assert sum(o["ok"] for o in bo) == 1 and b_cfg["beleg"]["hinweis"]
    assert "Befehle gibt sie aber nicht" in next(o["t"] for o in bo if o["ok"])
    alle_belege = " ".join(o["t"] for o in bo)
    assert "erzählt" not in alle_belege and "Lesestrecke" not in alle_belege
    ok_b = next(len(o["t"]) for o in bo if o["ok"])
    assert ok_b < max(len(o["t"]) for o in bo) and ok_b >= 0.7 * max(len(o["t"]) for o in bo)
    # Imker-Beleg in B und C: kommt nur am Kasten (Kapitel 2) und bei der Ernte (Kapitel 10) vor
    assert "Imker" in b_cfg["erkenntnis"]["hinweis"] and "Kapitel 2 und 10" in c_cfg["erkenntnis"]["hinweis"]
    assert c_cfg["satz"]["anfang"] and c_cfg["satz"]["min"] >= 40
    pos = [i for n in "ABC" for i, o in enumerate(a["niveaus"][n]["erkenntnis"]["optionen"]) if o["ok"]]
    assert len(set(pos)) >= 2, pos


# ── Film-Aufgaben: Abgleich mit dem Film ─────────────────────────────────────
def test_film_aufgabe_18(aufg):
    a = aufg[18]
    assert a["film"] == "volk" and 2 <= len(a["beobachtung"]) <= 3
    text = " ".join(a["beobachtung"])
    assert "Bienen im Stock" not in text and "50 000" not in text and "Reiter" not in text, "keine Bienenzahl: Reiter 1 hat Frage und Erklärung"
    assert "Eier" in a["beobachtung"][0] and "Gibt noch jemand anderes Befehle?" in a["beobachtung"][1] and "Tanz" in a["beobachtung"][2]


def test_film_knoepfe_an_den_richtigen_kapiteln(aufg):
    soll = {62: [3], 63: [4, 5], 64: [5, 7, 12], 21: [2, 3], 66: [9], 65: [6, 7, 8], 67: [9], 26: [9]}
    for nr, kapitel in soll.items():
        ist = []
        for k in _knoepfe(aufg[nr]):
            assert k["film"] == "volk" and k["text"].startswith("▶ ") and f"Kapitel {_kapitel(k)}" in k["text"], (nr, k["text"])
            ist.append(_kapitel(k))
        assert ist == kapitel, (nr, ist)
        assert "Kapitel" in aufg[nr]["eyebrow"], nr           # Hinweis auf die Filmstelle
    pflicht = [nr for nr, a in aufg.items() if any(k.get("pflicht") for k in _knoepfe(a))]
    assert pflicht == [66], "Pflicht-Knopf nur beim Tanzrätsel (der Tanz wird nur im Film gezeigt)"
    assert not any(a["typ"] == "filmmoment" for a in aufg.values()), "Finde den Moment entfällt (Obergrenze der Stationen)"


def test_alle_film_knoepfe_spielen_sofort_ab(aufg):
    """Audit-Entscheidung 2: Jeder Knopf springt (Kapitel oder Satz) und hängt `spielen` an; Sprungzeiten liegen im richtigen Kapitel."""
    anzahl = 0
    for nr in NUMMERN:
        for k in _alle_knoepfe(aufg[nr]):
            anzahl += 1
            assert k["film"] == "volk" and len(k["befehle"]) == 2 and k["befehle"][1] == {"mw": "spielen"}, (nr, k)
            sprung = k["befehle"][0]
            assert sprung["mw"] in ("kapitel", "springe"), (nr, k)
            if sprung["mw"] == "kapitel":
                assert 1 <= sprung["n"] <= 12
            else:
                assert 0 <= sprung["t"] < 240 and f"Kapitel {int(sprung['t'] // 20) + 1}" in k["text"], (nr, k["text"])
    assert anzahl >= 30, anzahl


def test_protokoll_62(aufg):
    a = aufg[62]
    assert a["auftrag"] and a["erkenntnis"] and [_kapitel(k) for k in _knoepfe(a)] == [3] and "Kapitel 3 bis 7" in a["eyebrow"]
    assert "2 000" in a["erkenntnis"] and "21 Tagen" in a["erkenntnis"] and "Alter" in a["erkenntnis"]
    assert "50 000" not in json.dumps(a, ensure_ascii=False) and "fünfzigtausend" not in json.dumps(a, ensure_ascii=False), "keine Bienenzahl in diesem Reiter"
    for n, cfg in a["niveaus"].items():
        assert 5 <= len(cfg["zeilen"]) <= 7 and cfg["schluss"]["anfang"], n
        assert all(z.get("kurz") for z in cfg["zeilen"]), f"{n}: kurze Titel für das Protokoll der Lehrkraft"
        for z in cfg["zeilen"]:
            assert z["frage"] and z["art"] in ("zahl", "wahl", "mehrfach", "text"), (n, z)
            k = z["modell"]
            assert k["film"] == "volk" and k["befehle"][0]["mw"] == "springe" and k["befehle"][1] == {"mw": "spielen"}, (n, z["frage"])
            assert k["text"].startswith("▶ Hör zu (Kapitel") and 3 <= _kapitel(k) <= 7, (n, k["text"])        # neutrale Beschriftung
            if z["art"] == "zahl":
                assert isinstance(z["loesung"], int) and z["einheit"], (n, z)
                assert z["fehlertext"] == "Schreibe die Zahl mit Ziffern, z. B. 12.", (n, z["frage"])
            elif z["art"] == "wahl":
                assert 2 <= len(z["optionen"]) <= 4 and 0 <= z["loesung"] < len(z["optionen"]), (n, z)
            elif z["art"] == "mehrfach":
                assert all(0 <= i < len(z["optionen"]) for i in z["loesung"]) and len(z["loesung"]) >= 2, (n, z)
            else:
                assert z["min"] >= 10 and z["satzanfang"], (n, z)
            if z["art"] != "text":
                assert z["hinweis"], (n, z["frage"])
    # Schlusssatz: A Bausteine (einer ist falsch und wird abgelehnt), B Satzanfang, C frei
    sa = a["niveaus"]["A"]["schluss"]["bausteine"]
    assert len(sa) == 5 and sum(1 for b in sa if isinstance(b, dict) and b["ok"] is False and b["rueckmeldung"]) == 1
    assert any("Alter" in (b if isinstance(b, str) else b["t"]) for b in sa)
    assert "bausteine" not in a["niveaus"]["B"]["schluss"] and a["niveaus"]["C"]["schluss"]["frei"] and a["niveaus"]["C"]["schluss"]["min"] >= 30
    assert [len(a["niveaus"][k]["zeilen"]) for k in "ABC"] == [5, 6, 6]
    # Antworten laut Film: Kapitel 3 Brutraum unten und Honigraum oben (47,9 s), Kapitel 4 drei Arten (61,4 s), Kapitel 5 bis zu 2 000 Eier (85,0 s),
    # Kapitel 6 Ammenbienen füttern (105,3 s) und einundzwanzig Tage (111,9 s), Kapitel 7 Aufgabe wechselt mit dem Alter (ab 121,4 s)
    A = a["niveaus"]["A"]["zeilen"]
    assert A[0]["kurz"] == "Räume oben und unten" and A[0]["optionen"][A[0]["loesung"]] == "oben der Honigraum, unten der Brutraum"
    assert A[1]["loesung"] == 3 and "2 000" in A[2]["optionen"][A[2]["loesung"]] and A[3]["loesung"] == 21
    zeiten = {z["kurz"]: z["modell"]["befehle"][0]["t"] for n in "ABC" for z in a["niveaus"][n]["zeilen"]}
    assert zeiten == {"Räume oben und unten": 47.6, "Arten von Bienen": 61.1, "Eier pro Tag": 84.7, "Tage bis zur jungen Biene": 111.6,
                      "Arbeit mit dem Alter": 121.1, "Räume im Bienenkasten": 47.6, "füttert die Larve": 105.0, "Satz über die Königin": 81.1}
    for n in "ABC":
        z = a["niveaus"][n]["zeilen"]
        arbeit = next(x for x in z if x["kurz"] == "Arbeit mit dem Alter")
        assert arbeit["optionen"][arbeit["loesung"]] == "sie wechselt" and len(arbeit["optionen"]) == 3, n
        assert not any("Bienen im Sommer" == x["kurz"] for x in z), "die Bienenzahl-Zeile entfällt"
        if n != "A":
            eier = next(x for x in z if "Eier" in x["frage"])
            assert "2 000" in eier["optionen"][eier["loesung"]]
            assert next(x for x in z if "Tagen" in x["frage"])["loesung"] == 21
            larve = next(x for x in z if "füttert" in x["frage"])
            assert larve["optionen"][larve["loesung"]] == "die Ammenbienen"
    assert [z["art"] for z in a["niveaus"]["C"]["zeilen"]] == ["mehrfach", "wahl", "wahl", "zahl", "wahl", "text"]
    c0 = a["niveaus"]["C"]["zeilen"][0]
    assert [c0["optionen"][i] for i in c0["loesung"]] == ["Brutraum", "Honigraum"]
    # Positionen der richtigen Antworten variieren
    pos = [z["loesung"] for n in "ABC" for z in a["niveaus"][n]["zeilen"] if z["art"] == "wahl"]
    assert len(set(pos)) >= 3, pos


def test_tabelle_63_nur_merkmale_aus_kapitel_4_und_5(aufg):
    a = aufg[63]
    assert a["auftrag"] and a["erkenntnis"] and [_kapitel(k) for k in _knoepfe(a)] == [4, 5]
    alles = json.dumps(a, ensure_ascii=False)
    for verboten in ("Stachel", "Jahre", "Wochen", "Monate", "Lebensdauer"):
        assert verboten not in alles, f"„{verboten}“ steht erst in der Lesestrecke 3, nicht in der Tabelle vor der Lesestrecke"
    zeilen_anzahl = []
    bilder_fehlen = set()
    for n, cfg in a["niveaus"].items():
        assert [s["name"] for s in cfg["spalten"]] == ["Königin", "Arbeiterin", "Drohne"], n
        for s, datei in zip(cfg["spalten"], ("koenigin", "arbeiterin", "drohne")):
            assert s["bild"] == f"/static/img/lese/bienenart-{datei}.svg" and s["alt"] == s["name"], (n, s)
            if not os.path.exists(os.path.join(ROOT, s["bild"].lstrip("/"))):
                bilder_fehlen.add(s["bild"])
            assert s["alt"].strip(), (n, s)
        zeilen_anzahl.append(len(cfg["zeilen"]))
        for z in cfg["zeilen"]:
            assert z["merkmal"] and z["hinweis"] and len(z["loesung"]) == 3, (n, z)
            assert all(0 <= i < len(z["optionen"]) for i in z["loesung"]), (n, z["merkmal"])
            assert len(set(z["optionen"])) == len(z["optionen"])
    assert zeilen_anzahl == [3, 4, 5]
    assert not bilder_fehlen, f"Spaltenbilder der Tabelle fehlen: {sorted(bilder_fehlen)}"
    # Inhalt laut Film: Königin legt die Eier, Drohne paart sich, Arbeiterin viele tausend, Drohnen einige hundert, Königin eine
    for n, cfg in a["niveaus"].items():
        zeile = {z["merkmal"]: z for z in cfg["zeilen"]}
        wert = lambda m, s: zeile[m]["optionen"][zeile[m]["loesung"][s]]
        assert wert("Aufgabe", 0) == "legt die Eier" and wert("Aufgabe", 1) == "macht viele Arbeiten (putzen, bauen, sammeln)"
        assert wert("Aufgabe", 2) == "paart sich mit jungen Königinnen"
        assert "arbeitet im Stock" not in json.dumps(cfg, ensure_ascii=False)
        assert [wert("Wie viele im Volk?", s) for s in range(3)] == ["eine", "viele tausend", "einige hundert"]
        if "Augen" in zeile:
            assert [wert("Augen", s) for s in range(3)] == ["normal groß", "normal groß", "riesig"]
    # die Lösungsspalte ist je Niveau anders angeordnet (Optionen vertauscht)
    pos = [tuple(z["loesung"]) for n in "ABC" for z in a["niveaus"][n]["zeilen"] if z["merkmal"] == "Aufgabe"]
    assert len(set(pos)) == 3, pos


def test_tabelle_68_echt_oder_nur_im_film(aufg):
    """Modellgrenzen offenlegen (film.md §2). Steht nach der Lesestrecke; Zeilen nur zu dem, was das AB belegt."""
    a = aufg[68]
    assert a["typ"] == "tabelle" and a["eyebrow"].startswith("Filmkritik") and "Kapitel 2 bis 6" in a["eyebrow"]
    assert a["auftrag"] and "Lesestrecke" in a["auftrag"]
    assert _woerter(a["erkenntnis"]) <= 30 and "Imker" in a["erkenntnis"] and "Papier" in a["erkenntnis"] and "verkürzt" in a["erkenntnis"]
    anzahl = []
    for n, cfg in a["niveaus"].items():
        assert cfg["spalten"] == ["Das siehst du im Film", "So ist es in echt"], n
        anzahl.append(len(cfg["zeilen"]))
        for z in cfg["zeilen"]:
            assert len(z["optionen"]) == 3 and len(z["loesung"]) == 2 and z["loesung"][0] != z["loesung"][1], (n, z["merkmal"])
            assert all(_woerter(o) <= 8 for o in z["optionen"]), (n, z["merkmal"])
            assert z["hinweis"] and "Hinweis" not in z["hinweis"]
            k = z["modell"]
            assert k["film"] == "volk" and k["befehle"] == [{"mw": "kapitel", "n": k["befehle"][0]["n"]}, {"mw": "spielen"}] and 2 <= k["befehle"][0]["n"] <= 6, (n, z["merkmal"])
            # die dritte Option ist in beiden Spalten falsch
            dritte = ({0, 1, 2} - set(z["loesung"])).pop()
            assert z["optionen"][dritte], (n, z["merkmal"])
    assert anzahl == [3, 4, 5]
    # Inhalt je Merkmal (Spalte 1 = Film, Spalte 2 = echt); jede Zeile kommt in mindestens einem Niveau vor
    erwartet = {
        "Die Bienen": ("Papierfiguren, viel größer als in echt", "echte Tiere, etwa 12 bis 14 mm lang"),
        "Die Königin": ("roter Punkt auf dem Rücken", "kein Punkt, Imker malen ihn manchmal auf"),
        "Die Rähmchen im Kasten": ("nur wenige Rähmchen", "mehr Rähmchen im Kasten"),
        "Die Eier der Königin": ("40 Eier im Bild oben rechts", "bis zu etwa 2 000 Eier am Tag"),
        "Vom Ei zur jungen Biene": ("nur wenige Sekunden", "21 Tage"),
    }
    gesehen = set()
    for n, cfg in a["niveaus"].items():
        for z in cfg["zeilen"]:
            film, echt = (z["optionen"][i] for i in z["loesung"])
            assert (film, echt) == erwartet[z["merkmal"]], (n, z["merkmal"], film, echt)
            gesehen.add(z["merkmal"])
    assert gesehen == set(erwartet)
    gesamt = json.dumps(a, ensure_ascii=False)
    for verboten in ("Honigernte", "geschleudert", "Schleuder", "Nektar", "Zählbild"):
        assert verboten not in gesamt, f"„{verboten}“ gehört zu Reiter 4 bzw. ist im AB nicht belegt"
    # Kapitel der Zeilen laut Übergabe: Bienen K2, Königin K4, Rähmchen K3, Eier K5, Entwicklung K6
    kap = {z["merkmal"]: z["modell"]["befehle"][0]["n"] for cfg in a["niveaus"].values() for z in cfg["zeilen"]}
    assert kap == {"Die Bienen": 2, "Die Königin": 4, "Die Rähmchen im Kasten": 3, "Die Eier der Königin": 5, "Vom Ei zur jungen Biene": 6}
    # Positionen der richtigen Optionen variieren
    pos = {tuple(z["loesung"]) for cfg in a["niveaus"].values() for z in cfg["zeilen"]}
    assert len(pos) >= 4, pos
    # Zeilenbilder: Film-Standbilder (angesehen: sie zeigen nur, was der Film zeigt, nie die Lösung der Spalte „in echt“); die Entwicklung hat keins
    stills = {"Die Bienen": ("still-bienen", "Film: Papierbienen am Flugloch"),
              "Die Königin": ("still-koenigin", "Film: Königin mit Krone-Schild"),
              "Die Rähmchen im Kasten": ("still-raehmchen", "Film: Rähmchen mit Wabe im aufgeklappten Kasten"),
              "Die Eier der Königin": ("still-eier", "Film: Wabe mit Eiern, Bild mit weißen Eiern oben rechts")}
    for n, cfg in a["niveaus"].items():
        for z in cfg["zeilen"]:
            if z["merkmal"] not in stills:
                assert "bild" not in z, "für die Entwicklung gibt es noch kein Standbild"
                continue
            datei, alt = stills[z["merkmal"]]
            assert z["bild"] == f"/static/img/film/{datei}.jpg" and z["alt"] == alt, (n, z["merkmal"])
            assert os.path.exists(os.path.join(ROOT, z["bild"].lstrip("/"))), z["bild"]
            assert "echt" not in z["alt"].lower().split() and "geschleudert" not in z["alt"].lower(), "das Bild darf die Lösung nicht verraten"


def test_filmkritik_ist_in_der_lesestrecke_und_im_glossar_belegt():
    """Die Spalte „So ist es in echt“ steht im AB, bevor sie gefragt wird (Station 68 kommt nach der Lesestrecke)."""
    text = " ".join(_klar(a["text"]) for a in STRECKE["abschnitte"])
    assert "Imker malen ihr manchmal einen roten Punkt auf den Rücken" in text
    assert "Im echten Kasten hängen viel mehr Rähmchen als im Film" in text
    assert "21 Tage" in text and "Im Film geht das in wenigen Sekunden" in text
    assert "Im echten Kasten hängen viel mehr Rähmchen als im Film" in glossar_volk.EINTRAEGE["raehmchen"]["text"]
    assert "etwa 12 bis 14 mm" in glossar_volk.EINTRAEGE["arbeiterin"]["text"]
    assert "roten Punkt" in glossar_volk.EINTRAEGE["koenigin"]["text"]


def test_bildpunkte_21_stock_karte(inh, aufg):
    k = inh["bildpunkte"]["stock"]
    namen = [p["name"] for p in k["punkte"]]
    assert namen == ["Flugloch", "Brutraum", "Honigraum", "Wabe", "Rähmchen", "Dach", "Boden"]
    assert k["breite"] == 900 and k["hoehe"] == 560 and k["bild"].startswith("/static/img/lese/stock-karte.svg")
    assert os.path.exists(os.path.join(ROOT, "static", "img", "lese", "stock-karte.svg"))
    for p in k["punkte"]:
        assert 24 <= p["x"] <= 900 - 24 and 24 <= p["y"] <= 560 - 24, p["id"]
    punkte = k["punkte"]
    for i, p in enumerate(punkte):
        for q in punkte[i + 1:]:
            assert ((p["x"] - q["x"]) ** 2 + (p["y"] - q["y"]) ** 2) ** 0.5 >= 52, f"{p['id']} und {q['id']} überlappen"
    a = aufg[21]
    assert a["karte"] == "stock"
    assert [a["niveaus"][n]["anzahl"] for n in "ABC"] == [4, 6, 7]
    assert all(a["niveaus"][n]["modus"] == "benennen" for n in "ABC") and a["niveaus"]["C"]["eingabe"] == "text"
    assert [_kapitel(k2) for k2 in _knoepfe(a)] == [2, 3] and a["eyebrow"].startswith("Anwenden")


def test_bildwahl_66_tanzraetsel(aufg):
    a = aufg[66]
    assert a["erkenntnis"] and "Winkel" in a["erkenntnis"] and "weit weg" in a["erkenntnis"]
    k = _knoepfe(a)[0]
    assert k["pflicht"] and k["befehle"] == [{"mw": "springe", "t": 163.5}, {"mw": "spielen"}] and k["text"] == "▶ Sieh dir den Tanz an (Kapitel 9)"
    with open(TANZ_JSON, encoding="utf-8") as f:
        daten = json.load(f)
    richtig_je_karte = {i + 1: [z["id"] for z in r if z["ok"]] for i, r in enumerate(daten["runden"])}
    assert richtig_je_karte == {1: ["B"], 2: ["C"], 3: ["A"]}
    runden_je_niveau = {}
    for n, cfg in a["niveaus"].items():
        runden_je_niveau[n] = len(cfg["runden"])
        for r in cfg["runden"]:
            karte = int(re.search(r"tanzraetsel-(\d)\.svg", r["bild"]).group(1))
            assert os.path.exists(os.path.join(ROOT, r["bild"].lstrip("/")))
            assert (r["breite"], r["hoehe"]) == (daten["breite"], daten["hoehe"]) and r["frage"] and r["hinweis"] and r["erklaerung"]
            assert sum(z["ok"] for z in r["ziele"]) == 1 and len(r["ziele"]) == 3, (n, karte)
            for z, soll in zip(r["ziele"], daten["runden"][karte - 1]):
                assert (z["x"], z["y"], z["r"], z["ok"]) == (soll["x"], soll["y"], soll["r"], soll["ok"]), (n, karte, soll["id"])
                assert 0 < z["r"] <= 70 and z["r"] <= z["x"] <= 900 - z["r"] and z["r"] <= z["y"] <= 560 - z["r"]
                assert z["ok"] or z.get("rueckmeldung"), "jedes falsche Ziel hat eine Rückmeldung"
                if n == "C":
                    assert z["ok"] or z["rueckmeldung"] == "Schau noch einmal genau hin.", "C: erste falsche Rückmeldung neutral"
                else:
                    assert z["ok"] or z["rueckmeldung"] != "Schau noch einmal genau hin."
                assert not z["ok"] or "rueckmeldung" not in z
            for i, z in enumerate(r["ziele"]):
                for y in r["ziele"][i + 1:]:
                    assert ((z["x"] - y["x"]) ** 2 + (z["y"] - y["y"]) ** 2) ** 0.5 > z["r"] + y["r"], "Trefferkreise überlappen"
    assert runden_je_niveau == {"A": 3, "B": 3, "C": 3}, "A hat jetzt drei Runden: Die Länge des Schwänzellaufs kommt vor, bevor der Merksatz sie behauptet"
    # A sagt die Regel in der Frage (auch die Länge in Runde 3), C nicht; der Hinweis wiederholt nie den Tipp aus der Frage
    A, B, C = (a["niveaus"][k]["runden"] for k in "ABC")
    assert "in Richtung Sonne" in A[0]["frage"] and "weit weg" in A[2]["frage"] and all("Richtung Sonne" not in r["frage"] for r in C)
    assert "Länge" in B[2]["frage"] and C[2]["frage"] == "Wo liegt das Futter? Ich erkenne es an …"
    for runden in (A, B):
        assert "Linie vom Stock zur Sonne" in runden[0]["hinweis"], "A und B Runde 1: Hinweis ≠ Tipp aus der Frage"
    assert C[0]["hinweis"] == "Zwei Dinge zählen: die Richtung und die Länge des Schwänzellaufs."      # C: Kriterien erst im Hinweis
    assert [r["bild"][-5] for r in C] == ["3", "2", "1"] and [r["bild"][-5] for r in A] == ["1", "2", "3"]
    # Rückmeldungen und Erklärungen nennen die Lösung nicht als Buchstabe
    text = json.dumps(a["niveaus"], ensure_ascii=False)
    assert not re.search(r"Feld [ABC]|Wiese [ABC]\b", text)


# ── Sprachwerkstatt ──────────────────────────────────────────────────────────
def test_sprachwerkstatt_65_zeitfolge(aufg):
    a = aufg[65]
    assert a["eyebrow"].startswith("Sprachwerkstatt") and [_kapitel(k) for k in _knoepfe(a)] == [6, 7, 8]
    n = a["niveaus"]
    for k in "ABC":
        assert n[k]["hilfe"] and "Lesestrecke" not in n[k]["hilfe"] and "Kapitel" in n[k]["hilfe"], f"{k}: eigener hilfe-Text mit Filmverweis"
    assert [len(n[k]["items"]) for k in "ABC"] == [4, 6, 8]
    for k in "ABC":
        items = n[k]["items"]
        assert len(set(items)) == len(items)
        assert items[0].startswith("Zuerst") and items[-1].startswith("Schließlich"), k
        assert "zuerst" in n[k]["hinweis"].lower() or "zeit" in n[k]["hinweis"].lower()
    assert "3 Tagen" in n["B"]["items"][1] and "21 Tagen" in n["B"]["items"][-1]       # Film: „nach drei Tagen“, „einundzwanzig Tage“
    # C: die Reihenfolge der Arbeiterinnen-Aufgaben wie im Film (Kapitel 7): putzen, füttern, bauen und Wache halten, ausfliegen
    c = n["C"]["items"]
    # Filmtext Kapitel 7: „putzen zuerst … Dann füttern sie … Später bauen sie Waben und halten Wache.“ Kapitel 8: die ältesten fliegen aus
    assert c[4] == "Die junge Biene putzt zuerst die Zellen." and c[5].startswith("Dann füttert sie als Ammenbiene")
    assert c[6] == "Später baut sie Waben und hält Wache." and c[7] == "Schließlich fliegt sie als Sammlerin aus."


def test_sprachwerkstatt_67_je_desto(aufg):
    a = aufg[67]
    assert a["eyebrow"].startswith("Sprachwerkstatt") and [_kapitel(k) for k in _knoepfe(a)] == [9]
    n = a["niveaus"]
    for k in "ABC":
        assert n[k]["hilfe"] and "Lesestrecke" not in n[k]["hilfe"], f"{k}: eigener hilfe-Text, nie die Lesestrecke"
    assert "Kapitel 9" in n["A"]["hilfe"] and "Dauer des Schwänzelns" in n["A"]["hilfe"]
    assert n["A"]["modus"] == "chips" and n["B"]["modus"] == "input" and n["C"]["modus"] == "input"
    luecken = {k: re.findall(r"\[([^\]]+)\]", n[k]["text"]) for k in "ABC"}
    assert luecken["A"] == ["länger", "weiter", "kürzer", "näher"]
    assert luecken["B"] == ["länger", "weiter", "kürzer", "näher", "weil"]
    assert luecken["C"] == ["Je", "desto", "damit", "weil", "deshalb|darum|daher"]     # alle richtigen Antworten gelten
    assert all(w not in n["A"]["ablenker"] for w in luecken["A"])
    # länger ↔ weiter, kürzer ↔ näher (Film: „Die Dauer des Schwänzelns zeigt, wie weit es ist.“)
    assert "Je [länger]" in n["A"]["text"] and "desto [weiter]" in n["A"]["text"] and "desto [näher]" in n["A"]["text"]


# ── Lesestrecke L3 (nachschlagen) ────────────────────────────────────────────
def test_lesestrecke_bestaetigt_den_film():
    t = [a["text"] for a in STRECKE["abschnitte"]]
    assert "Im Film hast du gehört" in t[0] and "Du hast den Bienenkasten beschriftet" in t[2] and "Im Film geht das in wenigen Sekunden" in t[3]
    assert t[1].startswith("Neu: Die <strong>Königin</strong> lebt 3 bis 5 Jahre.")
    belege = ["Im Winter sind es nur etwa 10 000", "<strong>Königin</strong> lebt 3 bis 5 Jahre", "oben der <strong>Honigraum</strong>", "sparen Platz und Wachs"]
    for text, beleg in zip(t, belege):
        assert beleg in text, beleg
    sommer = STRECKE["abschnitte"][0]["optionen"][STRECKE["abschnitte"][0]["loesung"]]
    assert "Sommer" in sommer and "mehr Bienen" in sommer


def test_lesestrecke_loesungen_verteilt_und_optionen_kurz():
    positionen = [a["loesung"] for a in STRECKE["abschnitte"]]
    assert set(positionen) == {0, 1, 2}, positionen
    for a in STRECKE["abschnitte"]:
        assert len(a["optionen"]) == 3 and all(len(o.split()) <= 12 for o in a["optionen"])
        assert a["bild_alt"].startswith("Schaubild:")


def test_lesestrecke_schaubilder_sind_da():
    for i, a in enumerate(STRECKE["abschnitte"], 1):
        assert a["bild"] == f"volk-{i}", a["bild"]
        assert os.path.exists(os.path.join(ROOT, "static", "img", "lese", a["bild"] + ".svg")), a["bild"]


def test_lesestrecke_enthaelt_das_wissen_das_der_film_nicht_sagt():
    """Lebensdauer, Drohnen ohne Stachel, Dach/Boden, Larve 6 und Puppe 12 Tage stehen erst hier – nirgends vorher gefragt."""
    text = " ".join(_klar(a["text"]) for a in STRECKE["abschnitte"])
    for beleg in ["3 bis 5 Jahre", "5 bis 6 Wochen", "6 Monate", "ohne Stachel", "aus dem Stock", "Boden", "Dach",
                  "Larve 6 Tage", "Puppe 12 Tage", "21 Tage", "Frühling wächst", "sechseckig"]:
        assert beleg in text, beleg


def test_wissen_der_lesestrecke_wird_vor_ihr_nicht_gefragt(aufg):
    """Station vor der Lesestrecke fragen nach nichts, was nur die Lesestrecke liefert (Stachel, Lebensdauer, Larve 6 / Puppe 12 Tage)."""
    vorher = [nr for nr in NUMMERN[:NUMMERN.index(66) + 1]]        # alle Stationen vor der Lesestrecke (68 steht danach und darf sie benutzen)
    for nr in vorher:
        text = json.dumps({k: v for k, v in aufg[nr].items() if k not in ("film", "modell")}, ensure_ascii=False)
        for stichwort in ("Stachel", "6 Monate", "6 Wochen", "5 Jahre", "6 Tage", "12 Tage", "Winterbiene", "Sommerbiene"):
            assert stichwort not in text, (nr, stichwort)


# ── Glossar ───────────────────────────────────────────────────────────────────
def test_glossar_vollstaendig_eindeutig_und_mit_bildern():
    assert sorted(glossar_volk.EINTRAEGE) == sorted(GLOSSAR_SCHLUESSEL)
    norm = glossar.normalisieren
    for key, e in glossar_volk.EINTRAEGE.items():
        assert len(e["text"]) < 420 and e["aliase"] and e["titel"], key
        assert all(_woerter(s) <= 18 for s in _saetze(e["text"])), key
        assert glossar.ALIASE[norm(e["titel"])] == key, key
        if key in GLOSSAR_BILDER:
            assert e["bild"] == GLOSSAR_BILDER[key], key
            assert os.path.exists(os.path.join(ROOT, "static", "img", "lese", e["bild"] + ".svg")), key
        else:
            assert e["bild"] is None, f"{key}: laut Auftrag kein Bild"
    for alias in ["Schwänzeltanz", "Tanz", "Bienentanz", "Arbeiterinnen", "Drohnen", "Königinnen", "Zellen", "Waben"]:
        assert norm(alias) in glossar.ALIASE


def test_glossar_koenigin_und_schwaenzeltanz_ergaenzt():
    k = glossar_volk.EINTRAEGE["koenigin"]["text"]
    assert "roten Punkt" in k and "Imker" in k and "manchmal" in k
    s = glossar_volk.EINTRAEGE["schwaenzeltanz"]["text"]
    for wort in ("Winkel", "senkrechten", "Sonne", "Je länger"):
        assert wort in s, wort
    assert glossar.ALIASE[glossar.normalisieren("Schwänzellauf")] == "schwaenzeltanz"


def test_fette_begriffe_haben_glossareintraege():
    for a in STRECKE["abschnitte"]:
        for fett in re.findall(r"<strong>(.*?)</strong>", a["text"]):
            assert glossar.normalisieren(fett) in glossar.ALIASE, fett
    texte = " ".join(a["text"] for a in STRECKE["abschnitte"])
    gefunden = {glossar.ALIASE[glossar.normalisieren(f)] for f in re.findall(r"<strong>(.*?)</strong>", texte)}
    assert {"bienenvolk", "koenigin", "arbeiterin", "drohne", "flugloch", "brutraum", "honigraum", "raehmchen", "wabe", "zelle",
            "larve", "puppe"} <= gefunden


def test_glossartexte_nennen_nur_gesicherte_zahlen():
    for key, e in glossar_volk.EINTRAEGE.items():
        for z in _zahlen(e["text"]):
            assert z in ERLAUBTE_ZAHLEN, (key, z)


# ── Zeichnung 2 (Aufgabe 26) ────────────────────────────────────────────────
def test_zeichnung_schwaenzeltanz(aufg):
    z = zeichenauftraege.ZEICHENAUFTRAEGE["schwaenzeltanz"]
    assert z["nr"] == 26 and aufg[26]["geraet"] == "schwaenzeltanz"
    merkmale = " ".join(z["merkmale"])
    for wort in ["senkrechte Wabe", "tanzende Biene", "Sonne", "Richtungslinie"]:
        assert wort in merkmale, wort
    assert all(len(m.split()) <= 25 for m in z["merkmale"]), "Kindersprache: kurze Merkmale"
    assert any("Hilfslinie" in m for m in z["stufen"]["B"]) and any("Winkel" in m for m in z["stufen"]["C"])
    for n, cfg in aufg[26]["niveaus"].items():
        text = " ".join(cfg["elemente"]).lower()
        for wort in ("wabe", "sonne", "richtung"):
            assert wort in text, (n, wort)
    assert "Kapitel 9" in aufg[26]["eyebrow"] and [_kapitel(k) for k in _knoepfe(aufg[26])] == [9]
    assert "Acht" in z["hinweis"] and "Skizze" in z["hinweis"]


def test_der_echte_film_liegt_im_arbeitsblatt():
    pfad = os.path.join(ROOT, "static", "film", "Ein_Bienenvolk_im_Bienenstock.html")
    assert os.path.exists(pfad)
    if os.path.getsize(pfad) < 1_000_000:
        warnings.warn("static/film/Ein_Bienenvolk_im_Bienenstock.html ist noch die Attrappe, nicht der echte Film", stacklevel=1)
    # Kapitelzahl laut Übergabe
    if os.path.exists(UEBERGABE):
        with open(UEBERGABE, encoding="utf-8") as f:
            zeilen = [z for z in f.read().splitlines() if re.match(r"\| \d+ \| \d:\d\d\.\d–", z)]
        assert len(zeilen) == 12
