"""Forschend-entwickelnder Ansatz (docs/FORSCHEN.md): die neuen Typen vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch.

* Strukturprüfungen (tests/forschen_pruefen.py) an Test-Fixtures und an den Beispielen aus docs/FORSCHEN_BEISPIELE.js –
  dazu gezielt kaputt gemachte Aufgaben, die die Prüfungen finden müssen.
* Die Logik von static/js/forschen.js unter Node (tests/forschen.test.cjs, ohne Browser).
* Gewichtung (Quoten je Reiter) mit synthetischen Reitern; die echten Inhalte prüft tests/test_inhalte_struktur.py.
* Einhängepunkte, Tafel (bietet die neuen Typen nicht an), Server (Antworttypen, langer Forscherbuch-Text, Autosave, Dashboard).
Die Fixtures liegen in tests/fixtures_forschen.js und kommen nie in die echten Inhalte.
"""
import copy
import functools
import json
import os
import subprocess
import warnings

import pytest

import app as appmodule
import config
import forschen_pruefen as fp
from config import ANTWORT_TYPEN, lese_nach
from conftest import NR, session_werte
from inhalte_laden import NODE, ROOT, node_noetig
from plan import (BEKANNTE_TYPEN, DIFFERENZIERT, ECHT_FORSCHEN_TYPEN, MAX_STATIONEN, MIN_FORSCHEN, MIN_FORSCHEN_ANZAHL, OHNE_TAFEL, OHNE_VERMUTUNG, QUOTE_ABFRAGE_MAX,
                  QUOTE_FORSCHEN_MIN, max_stationen, min_forschen, min_forschen_anzahl, vermutung_pflicht)

FIXTURES = os.path.join(ROOT, "tests", "fixtures_forschen.js")
BEISPIELE = os.path.join(ROOT, "docs", "FORSCHEN_BEISPIELE.js")
FILME = {"biene3d": {"art": "modell3d", "datei": "/x"}, "volk": {"art": "papiertheater", "datei": "/y"}}


@functools.lru_cache(maxsize=None)
def _roh(name, datei):
    node_noetig()
    p = subprocess.run([NODE, os.path.join(ROOT, "tests", "_lade_variable.cjs"), name, datei], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-1500:]
    return p.stdout


def fixtures():
    return json.loads(_roh("FORSCHEN_FIXTURES", FIXTURES))


def beispiele():
    return json.loads(_roh("FORSCHEN_BEISPIELE", BEISPIELE))


def inh_aus(tabs):
    return {"titel": "Test", "filme": FILME, "bildpunkte": {}, "tabs": tabs}


def aufgabe(nr):
    """Eine Fixture-Aufgabe als frische Kopie."""
    for t in fixtures()["tabs"]:
        for a in t["aufgaben"]:
            if a["nr"] == nr:
                return copy.deepcopy(a)
    raise KeyError(nr)


# ── Struktur: Fixtures und Beispiele sind gültig ─────────────────────────────
def test_fixtures_bestehen_die_strukturpruefung():
    inh = inh_aus(fixtures()["tabs"])
    assert fp.pruefe_alle(inh) == []
    typen = {a["typ"] for t in inh["tabs"] for a in t["aufgaben"]}
    assert set(fp.NEUE_TYPEN) <= typen, "die Fixtures decken alle sechs neuen Typen ab"
    for t in inh["tabs"]:
        for a in t["aufgaben"]:
            if a["typ"] in fp.NEUE_TYPEN and a["typ"] != "forscherbuch":
                assert sorted(a["niveaus"]) == ["A", "B", "C"], a["nr"]


def test_beispiele_datei_besteht_dieselbe_pruefung():
    b = beispiele()
    assert set(b) == set(fp.NEUE_TYPEN)
    tabs = [{"key": "nutztier", "aufgaben": [b["vermutung"], b["pruefen"], b["protokoll"], b["tabelle"], b["bildwahl"]]},
            {"key": "abschluss", "aufgaben": [b["forscherbuch"]]}]
    assert fp.pruefe_alle(inh_aus(tabs)) == []
    assert fp.pruefen_qualitaet(inh_aus(tabs)) == [], "die Beispiele halten die Qualitätsregeln von pruefen ein (Hinweis, Optionslängen)"
    assert b["pruefen"]["vermutung"] == b["vermutung"]["id"]


def test_js_dateien_der_tests_und_beispiele_sind_gueltig():
    node_noetig()
    for datei in (FIXTURES, BEISPIELE, os.path.join(ROOT, "static", "js", "forschen.js")):
        p = subprocess.run([NODE, os.path.join(ROOT, "tests", "_syntax.cjs"), datei], capture_output=True, text=True, encoding="utf-8", timeout=30)
        assert p.returncode == 0, (datei, p.stderr[-800:])


def test_stationsplan_der_fixtures_passt_zu_leseNach():
    """Die Fixtures spielen die Lesestrecke mitten in der Liste, am Ende und oben durch – plan und leseNach müssen übereinstimmen."""
    F = fixtures()
    gesehen = set()
    for tab in F["tabs"]:
        stationen = F["plan"][tab["key"]]["STATIONEN"]
        erwartet = lese_nach(stationen)
        if erwartet == "":
            assert "lese" not in tab and "leseNach" not in tab
            continue
        assert tab["lese"] == next(n for n in stationen if config.ist_lesestrecke(n))
        assert tab.get("leseNach") == erwartet, tab["key"]
        gesehen.add("oben" if erwartet is None else "ende" if stationen[-1] == tab["lese"] else "mitte")
        nrs = [a["nr"] for a in tab["aufgaben"]]
        assert nrs == [n for n in stationen if not config.ist_lesestrecke(n)], f"{tab['key']}: Reihenfolge der Aufgaben = Plan"
        assert set(F["plan"][tab["key"]]["TYPEN"]) == {str(n) for n in nrs}   # JSON macht aus Zahlen-Schlüsseln Text
    assert gesehen == {"oben", "mitte", "ende"}


# ── Die Strukturprüfung findet Fehler ────────────────────────────────────────
def _loesch(d, *pfad):
    for k in pfad[:-1]:
        d = d[k]
    del d[pfad[-1]]


FEHLER = [
    # (Aufgabe, Veränderung, erwartete Meldung)
    (901, lambda a: a["niveaus"]["A"].update(optionen=["nur eine"]), "mindestens 2 Optionen"),
    (901, lambda a: a.pop("id"), "id fehlt"),
    (901, lambda a: a.update(id="Gross Schreibung"), "id fehlt oder ist ungültig"),
    (901, lambda a: _loesch(a, "niveaus", "B", "satzanfang"), "satzanfang fehlt"),
    (901, lambda a: a["niveaus"]["C"].update(min=5), "min (Zeichen) von mindestens 20"),
    (901, lambda a: a["niveaus"]["C"].pop("frei"), "frei: true verlangt"),
    (901, lambda a: a["niveaus"]["A"].update(optionen=["eins", "eins"]), "doppelte Optionen"),
    (901, lambda a: _loesch(a, "niveaus", "C"), "niveaus A, B und C verlangt"),
    (903, lambda a: a.update(vermutung="v_gibt_es_nicht"), "verweist auf keine Station vermutung"),
    (903, lambda a: a["niveaus"]["A"]["erkenntnis"]["optionen"][0].update(ok=True), "genau eine Option muss ok sein"),
    (903, lambda a: a.pop("erkenntnis"), "erkenntnis (Merksatz für das Forscherbuch) fehlt"),
    (903, lambda a: _loesch(a, "niveaus", "B", "beleg"), "beleg {frage, optionen} fehlt"),
    (903, lambda a: a["niveaus"]["C"]["satz"].update(min=10), "satz {anfang, min ≥ 20} fehlt"),
    (903, lambda a: a.update(modell={"film": "gibtsnicht", "text": "x", "befehle": []}), "modell.film fehlt oder ist unbekannt"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][0].update(art="schweben"), "art 'schweben' unbekannt"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][0].update(loesung="sechs"), "loesung muss eine Zahl sein"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][1].update(loesung=7), "Index einer Option"),
    (902, lambda a: a["niveaus"]["B"]["zeilen"][1].update(loesung=[0, 1, 2, 3]), "mindestens einer, nicht alle"),
    (902, lambda a: a["niveaus"]["B"]["zeilen"][0].update(toleranz=-1), "toleranz muss eine Zahl ≥ 0"),
    (902, lambda a: a["niveaus"]["A"]["schluss"].update(bausteine=[{"t": "a", "ok": False}, {"t": "b", "ok": False}]), "mindestens ein Baustein muss stimmen"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][0].update(modell={"film": "biene3d", "text": "x", "befehle": [{"mw": "kapitel", "n": 3}]}), "das 3D-Modell hat keine Kapitel"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][0].update(modell={"film": "volk", "text": "x", "befehle": [{"mw": "ansicht", "name": "situs"}]}), "der Film kennt nur"),
    (902, lambda a: a["niveaus"]["A"].update(zeilen=[]), "zeilen fehlen"),
    (905, lambda a: a["niveaus"]["A"]["zeilen"][0].update(loesung=[0, 1]), "loesung braucht je Spalte"),
    (905, lambda a: a["niveaus"]["A"].update(spalten=["Nur eine"]), "mindestens 2 Überschriften"),
    (905, lambda a: a["niveaus"]["A"].update(spalten=["Gleich", "Gleich", "Drohne"]), "doppelte Spaltenüberschriften"),
    (905, lambda a: a["niveaus"]["A"]["zeilen"][1].update(optionen=["nur eine"]), "mindestens 2 Optionen"),
    # Spalten- und Zeilenbilder (tabelle): Datei da, alt nicht leer, Name vorhanden, Namen eindeutig (auch zwischen Text und Objekt)
    (905, lambda a: a["niveaus"]["A"]["spalten"][0].pop("alt"), "Spalte 1 (Königin): alt (Bildbeschreibung) fehlt"),
    (905, lambda a: a["niveaus"]["A"]["spalten"][1].update(alt="  "), "Spalte 2 (Arbeiterin): alt (Bildbeschreibung) fehlt"),
    (905, lambda a: a["niveaus"]["A"]["spalten"][2].update(bild="/static/img/lese/gibt-es-nicht.svg"), "Spalte 3 (Drohne): Bilddatei fehlt"),
    (905, lambda a: a["niveaus"]["A"]["spalten"][2].update(name=""), "mindestens 2 Überschriften"),
    (905, lambda a: a["niveaus"]["A"]["spalten"].__setitem__(2, "Königin"), "doppelte Spaltenüberschriften"),
    (905, lambda a: a["niveaus"]["B"]["spalten"].__setitem__(2, {"name": "Königin"}), "doppelte Spaltenüberschriften"),
    (905, lambda a: a["niveaus"]["A"]["zeilen"][1].pop("alt"), "Zeile 2 (Zeilenbild): alt (Bildbeschreibung) fehlt"),
    (905, lambda a: a["niveaus"]["A"]["zeilen"][1].update(bild="/static/img/film/gibt-es-nicht.jpg"), "Zeile 2 (Zeilenbild): Bilddatei fehlt"),
    # Knöpfe `modell`: Listen, Bild-Knopf { bild, text, alt }, Sekundensprung, spielen/pflicht
    (903, lambda a: a["modell"][1].pop("alt"), "modell.alt (Bildbeschreibung) fehlt"),
    (903, lambda a: a["modell"][1].update(bild="/static/img/lese/gibt-es-nicht.svg"), "Bilddatei fehlt"),
    (903, lambda a: a["modell"][1].pop("text"), "modell.text fehlt"),
    (903, lambda a: a["modell"][0].update(befehle=[{"mw": "springe"}]), "springe braucht t"),
    (903, lambda a: a["modell"][0].update(befehle=[{"mw": "springe", "t": -3}]), "springe braucht t"),
    (903, lambda a: a["modell"][0].update(spielen="ja"), "modell.spielen muss true oder false sein"),
    (903, lambda a: a["modell"][0].update(pflicht=1), "modell.pflicht muss true oder false sein"),
    (903, lambda a: a.update(modell=[]), "modell ist eine leere Liste"),
    (903, lambda a: a["modell"].append({"film": "gibtsnicht", "text": "x", "befehle": []}), "modell.film fehlt oder ist unbekannt"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][0].update(modell=[{"film": "biene3d", "text": "a", "befehle": []}, {"bild": "/static/img/lese/gibt-es-nicht.svg", "text": "B", "alt": "b"}]), "Bilddatei fehlt"),
    (906, lambda a: a["niveaus"]["A"].update(auftrag="  "), "auftrag muss Text sein"),
    (902, lambda a: a["niveaus"]["A"]["zeilen"][0].update(okText=""), "okText muss Text sein"),
    (906, lambda a: a["niveaus"]["A"]["runden"][0]["ziele"][0].update(ok=False), "mindestens ein Ziel muss ok: true sein"),
    (906, lambda a: a["niveaus"]["A"]["runden"][0].update(bild="/static/img/lese/gibt-es-nicht.svg"), "Bilddatei fehlt"),
    (906, lambda a: a["niveaus"]["A"]["runden"][0]["ziele"][1].update(x=5000), "außerhalb des Bildes"),
    (906, lambda a: a["niveaus"]["A"]["runden"][0].update(ziele=[{"x": 1, "y": 1, "r": 80, "ok": True}]), "mindestens 2 ziele"),
    (906, lambda a: a["niveaus"]["A"]["runden"][0].pop("breite"), "breite und hoehe"),
    (913, lambda a: a.pop("titel"), "eyebrow und titel fehlen"),
]


@pytest.mark.parametrize("nr,aendern,meldung", FEHLER, ids=[f"{nr}-{m[:40]}" for nr, _, m in FEHLER])
def test_strukturpruefung_findet_fehler(nr, aendern, meldung):
    a = aufgabe(nr)
    aendern(a)
    probleme = fp.pruefe_aufgabe(a, inh_aus([]), {"v_anzahl", "v_ei", "v_honig"})
    assert any(meldung in p for p in probleme), (meldung, probleme)


def test_fokus_mit_abstand_wird_geprueft():
    """Audit F2: `fokus: {teile, blick?, abstand?}` bei modellfinden-Zielen und als Befehl an Knöpfen."""
    assert fp.fokus_probleme({"teile": ["fuehler"], "blick": "oben", "abstand": 2.5}, "w") == []
    assert fp.fokus_probleme({"teile": ["fuehler"]}, "w") == []
    for schlecht in ({"teile": []}, {}, {"teile": ["a"], "abstand": 0}, {"teile": ["a"], "abstand": -1}, {"teile": ["a"], "abstand": "2"}, {"teile": ["a"], "blick": ""}):
        assert fp.fokus_probleme(schlecht, "w"), schlecht
    assert fp.fokus_probleme("x", "w")
    modellfinden = {"nr": 9, "typ": "modellfinden", "film": "biene3d", "eyebrow": "x", "titel": "x", "niveaus": {
        "A": {"ziele": [{"teil": "fuehler", "frage": "?", "hinweis": "?", "fokus": {"teile": ["fuehler"], "abstand": 0}}]}}}
    probleme = fp.modellziele_probleme(inh_aus([{"key": "koerper", "aufgaben": [modellfinden]}]))
    assert any("fokus.abstand muss eine Zahl > 0 sein" in p for p in probleme), probleme
    modellfinden["niveaus"]["A"]["ziele"][0]["fokus"]["abstand"] = 2
    assert fp.modellziele_probleme(inh_aus([{"key": "koerper", "aufgaben": [modellfinden]}])) == []
    # als Befehl an einem Knopf
    knopf = {"film": "biene3d", "text": "x", "befehle": [{"mw": "fokus", "teile": ["fuehler"], "abstand": -3}]}
    assert any("fokus.abstand" in p for p in fp._modell(knopf, inh_aus([]), "w"))
    knopf["befehle"][0]["abstand"] = 3
    assert fp._modell(knopf, inh_aus([]), "w") == []


def test_knopflisten_und_bild_knoepfe_der_fixtures_sind_gueltig():
    probleme = fp.pruefe_aufgabe(aufgabe(903), inh_aus([]), {"v_anzahl"})
    assert probleme == [], probleme
    a = aufgabe(903)
    assert isinstance(a["modell"], list) and fp.ist_bild_knopf(a["modell"][1]) and not fp.ist_bild_knopf(a["modell"][0])
    assert fp.knopf_liste(a["modell"]) == a["modell"] and fp.knopf_liste(a["modell"][0]) == [a["modell"][0]] and fp.knopf_liste(None) == []
    # ein reiner Bild-Knopf zählt nicht als „arbeitet mit Modell oder Film“, ein Film-Knopf in der Liste schon
    assert fp.arbeitet_mit_modell(a)
    a["modell"] = [a["modell"][1]]
    assert not fp.arbeitet_mit_modell(a)


# ── Qualität von pruefen (Audit T2) ──────────────────────────────────────────
def test_fixtures_bestehen_die_qualitaetspruefung_von_pruefen():
    assert fp.pruefen_qualitaet(inh_aus(fixtures()["tabs"])) == []


def _pruefen_mit(aendern):
    a = aufgabe(903)
    aendern(a)
    return fp.pruefen_qualitaet(inh_aus([{"key": "nutztier", "aufgaben": [a]}]))


@pytest.mark.parametrize("aendern,meldung", [
    (lambda a: a["niveaus"]["A"]["erkenntnis"].pop("hinweis"), "Niveau A: erkenntnis.hinweis fehlt"),
    (lambda a: a["niveaus"]["C"]["erkenntnis"].update(hinweis="  "), "Niveau C: erkenntnis.hinweis fehlt"),
    # die richtige Option ist die (allein) längste
    (lambda a: [a["niveaus"]["A"]["erkenntnis"]["optionen"].__setitem__(i, {"t": "Es leben wenige.", "ok": False}) for i in (0, 2)], "Niveau A erkenntnis: die richtige Option ist die längste"),
    (lambda a: a["niveaus"]["B"]["beleg"]["optionen"].__setitem__(1, {"t": "Geraten.", "ok": False}), "Niveau B beleg: die richtige Option ist die längste"),
    # die richtige Option ist zu kurz (< 70 % der längsten)
    (lambda a: a["niveaus"]["C"]["erkenntnis"]["optionen"].__setitem__(1, {"t": "Im Sommer sind es höchstens etwa 500 Bienen, und zwar im ganzen Stock.", "ok": False}), "Niveau C erkenntnis: die richtige Option ist zu kurz"),
], ids=["hinweis-A", "hinweis-C-leer", "laengste-A", "laengste-beleg", "zu-kurz"])
def test_pruefen_qualitaet_findet_fehler(aendern, meldung):
    probleme = _pruefen_mit(aendern)
    assert any(meldung in p for p in probleme), (meldung, probleme)


def test_pruefen_qualitaet_gleich_lange_optionen_sind_in_ordnung():
    """Gleich lange Optionen (auch mit der richtigen unter den längsten) sind erwünscht; nur die ALLEIN längste und die zu kurze fallen auf."""
    def gleich(a):
        for c in a["niveaus"].values():
            ops = c["erkenntnis"]["optionen"]
            for o in ops:
                o["t"] = o["t"][:30].ljust(30, "x")
    assert _pruefen_mit(gleich) == []


def test_laengenregel_grenzfall_70_prozent():
    from forschen_pruefen import _laengen_probleme
    zehn = "x" * 10
    assert _laengen_probleme([{"t": zehn, "ok": False}, {"t": "y" * 7, "ok": True}], "w") == [], "genau 70 % ist erlaubt"
    assert any("zu kurz" in p for p in _laengen_probleme([{"t": zehn, "ok": False}, {"t": "y" * 6, "ok": True}], "w"))
    assert any("längste" in p for p in _laengen_probleme([{"t": zehn, "ok": False}, {"t": "y" * 11, "ok": True}], "w"))
    assert _laengen_probleme([{"t": zehn, "ok": True}, {"t": "z" * 10, "ok": False}], "w") == [], "gleich lang: kein Verstoß"
    assert _laengen_probleme(None, "w") == [] and _laengen_probleme([{"t": "a", "ok": True}], "w") == []


def test_doppelte_ids_und_zwei_forscherbuecher_werden_gefunden():
    F = fixtures()
    tabs = copy.deepcopy(F["tabs"])
    tabs[2]["aufgaben"][0]["id"] = "v_anzahl"                                  # doppelt
    tabs[3]["aufgaben"].append(copy.deepcopy(tabs[4]["aufgaben"][0]))          # zweites Forscherbuch (im falschen Reiter)
    probleme = " | ".join(fp.pruefe_alle(inh_aus(tabs)))
    assert "nicht eindeutig" in probleme and "höchstens ein Forscherbuch" in probleme and "gehört in den Reiter" in probleme


def test_kleine_touchziele_im_bild_werden_gemeldet():
    a = aufgabe(906)
    a["niveaus"]["A"]["runden"][0]["ziele"][0]["r"] = 40
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert fp.pruefe_aufgabe(a, inh_aus([]), set()) == []
    assert any("Touchziel" in str(x.message) for x in w)


def test_neue_typen_sind_in_den_plan_listen():
    neu = set(fp.NEUE_TYPEN)
    assert neu <= BEKANNTE_TYPEN and neu <= OHNE_TAFEL and neu <= ANTWORT_TYPEN
    assert (neu - {"forscherbuch"}) <= DIFFERENZIERT and "forscherbuch" not in DIFFERENZIERT


def test_css_der_tabellenbilder_haelt_die_masse():
    """Spaltenbild 72–96 px hoch mit object-fit: contain, im Stapelmodus (≤ 760 px) mindestens 56 px; Zeilenbild 16:9 und höchstens 120 px breit,
    ein Tippziel von mindestens 44 px; kein waagerechter Überlauf (Spalten dürfen schrumpfen: minmax(0, …))."""
    import re
    css = open(os.path.join(ROOT, "static", "css", "app.css"), encoding="utf-8").read()
    regel = lambda sel: next(m.group(1) for m in re.finditer(r"(?m)^\s*" + re.escape(sel) + r"\s*\{([^}]*)\}", css))
    sp = regel(".fo-sp-bild")
    assert "object-fit: contain" in sp and re.search(r"height:\s*clamp\(72px,[^,]+,\s*96px\)", sp)
    assert "object-fit: contain" in regel(".fo-zeilenbild img")
    zb = regel(".fo-zeilenbild")
    assert "aspect-ratio: 16 / 9" in zb and "min(100%, 120px)" in zb and "min-height: 44px" in zb
    schmal = css[css.index("@media (max-width: 760px) {\n  .fo-tkopf"):]
    schmal = schmal[:schmal.index("\n}\n")]
    hoehe = re.search(r"\.fo-zl-bild \{[^}]*height:\s*(\d+)px", schmal)
    assert hoehe and int(hoehe.group(1)) >= 56
    assert "grid-template-columns: minmax(0, 1fr)" in schmal
    assert "repeat(var(--fo-n, 3), minmax(0, 1fr))" in css


# ── Gewichtung ───────────────────────────────────────────────────────────────
def _a(typ, nr, eyebrow="Forschen", **extra):
    return dict({"nr": nr, "typ": typ, "eyebrow": eyebrow, "titel": f"Station {nr}"}, **extra)


def _gut(key="koerper", mit_lese=True):
    """Ein Reiter, der alle Regeln einhält: 10 Stationen, 4 ECHT forschend (3 mit Modell; erkunden/modellfinden sind Anwenden), 2 Sprachwerkstatt, 2 Abfrage."""
    aufg = [_a("vermutung", 1, id="v1"), _a("erkunden", 2), _a("modellfinden", 3), _a("protokoll", 4, modell={"film": "biene3d"}),
            _a("tabelle", 5, modell=[{"film": "biene3d"}, {"bild": "/x.svg", "text": "Bild", "alt": "x"}]), _a("pruefen", 6, vermutung="v1", erkenntnis="Merksatz.", modell={"film": "volk"}),
            _a("mc", 7, "Sprachwerkstatt · Wortschatz"), _a("luecke", 8, "Sprachwerkstatt · Sätze"), _a("mc", 9, "Grundwissen"), _a("zuordnung", 10, "Grundwissen")]
    tab = {"key": key, "aufgaben": aufg}
    if mit_lese:
        tab.update(lese="L1", leseNach=4)
    return tab


def test_gewichtung_gute_reiter_bestehen():
    assert fp.gewichtung_probleme(inh_aus([_gut("nutztier"), _gut("koerper"), _gut("volk"), _gut("nutzen"), {"key": "abschluss", "aufgaben": [_a("blitz", 20), _a("forscherbuch", 21)]}])) == []
    g = fp.gewichtung(_gut())
    assert (g["n"], g["forschen"], g["sprach"], g["abfrage"], g["mit_modell"], g["stationen"]) == (10, 4, 2, 2, 3, 11)
    assert QUOTE_FORSCHEN_MIN == 0.25 and QUOTE_ABFRAGE_MAX == 0.3


@pytest.mark.parametrize("aendern,meldung", [
    (lambda t: t["aufgaben"].__setitem__(slice(1, 6), [_a("mc", n, "Grundwissen") for n in range(2, 7)]), "Stationen forschend"),
    (lambda t: [a.update(eyebrow="Grundwissen") for a in t["aufgaben"] if a["eyebrow"].startswith("Sprach")], "Sprachwerkstatt-Stationen"),
    (lambda t: t["aufgaben"].extend([_a("mc", 11, "Grundwissen"), _a("mc", 12, "Grundwissen"), _a("zuordnung", 13, "Grundwissen")]), "reine Abfrage"),
    (lambda t: t["aufgaben"].extend([_a("protokoll", 11), _a("tabelle", 12)]), "Stationen inklusive Lesestrecke"),
    (lambda t: t["aufgaben"].remove(t["aufgaben"][0]), "keine Forscherfrage"),
    (lambda t: t["aufgaben"][5].pop("erkenntnis") and t["aufgaben"][5].update(typ="mc"), "Forschungsphase endet nicht"),
    (lambda t: t.pop("leseNach"), "Lesestrecke steht an erster Stelle"),
    (lambda t: t["aufgaben"][5].update(vermutung="v_unbekannt"), "verweist auf keine vermutung.id"),
    (lambda t: [a.pop("modell") for a in t["aufgaben"][3:6]], "Modell oder Film"),
    (lambda t: [t["aufgaben"][4].update(modell={"bild": "/x.svg", "text": "Bild", "alt": "x"}), t["aufgaben"][5].pop("modell"), t["aufgaben"][3].pop("modell")], "Modell oder Film"),
], ids=["forschen-zu-wenig", "sprachwerkstatt", "abfrage", "stationen", "vermutung", "erkenntnis", "lese-oben", "verweis", "modell-anteil", "bild-knopf-ist-kein-modell"])
def test_gewichtung_findet_verstoesse(aendern, meldung):
    t = _gut("koerper")
    aendern(t)
    probleme = fp.gewichtung_probleme(inh_aus([t]))
    assert any(meldung in p for p in probleme), (meldung, probleme)


def test_quote_ehrlich_mindestens_25_prozent_und_drei_echte_forschen_stationen_je_reiter_2_bis_4():
    """Audit-Entscheidung 3: Forschen zählt nur mit Evidenzsammlung. Quote: mindestens 25 % je Reiter; Reiter 2–4 (koerper, volk, nutzen) zusätzlich mindestens 3 ECHTE
    Forschen-Stationen; „nutztier“ bleibt bei 25 % ohne Vermutungspflicht (keine vermutung-/pruefen-/erkenntnis-Pflicht)."""
    assert MIN_FORSCHEN == {"nutztier": 0.25} and OHNE_VERMUTUNG == {"nutztier"} and QUOTE_FORSCHEN_MIN == 0.25
    assert MIN_FORSCHEN_ANZAHL == {"koerper": 3, "volk": 3, "nutzen": 3}
    assert [min_forschen(k) for k in ("nutztier", "koerper", "volk", "nutzen")] == [0.25] * 4
    assert [min_forschen_anzahl(k) for k in ("nutztier", "koerper", "volk", "nutzen", "abschluss")] == [0, 3, 3, 3, 0]
    assert [vermutung_pflicht(k) for k in ("nutztier", "koerper", "volk", "nutzen")] == [False, True, True, True]
    # 8 Aufgaben, 2 echt forschend (= 25 %; bildpunkte nur mit forschen: true), keine Forscherfrage, kein Prüfen, kein Erkenntnissatz: für „nutztier“ in Ordnung
    einfach = lambda key: {"key": key, "lese": "L1", "leseNach": 3, "aufgaben": [
        _a("mc", 1, "Einstieg"), _a("mc", 2, "Einstieg"), _a("bildpunkte", 3, "Entdecken", karte="x", forschen=True), _a("tabelle", 4, "Vergleichen"),
        _a("luecke", 5, "Sprachwerkstatt · Wörter"), _a("zuordnung", 6, "Sprachwerkstatt · Artikel"), _a("luecke", 7, "Sprachwerkstatt · Sätze"), _a("notizen", 8, "Forscherbuch")]}
    assert fp.gewichtung_probleme(inh_aus([einfach("nutztier")])) == []
    probleme = " | ".join(fp.gewichtung_probleme(inh_aus([einfach("koerper")])))
    assert "keine Forscherfrage" in probleme and "endet nicht" in probleme, "andere Reiter behalten die Pflicht"
    assert "nur 2 echte Forschen-Stationen (mindestens 3" in probleme, "25 % genügen, aber Reiter 2–4 brauchen mindestens drei echte Stationen"
    assert "forschend (mindestens" not in probleme
    # ohne forschen: true ist das Benennen am Bild Anwenden: 1 von 8 = 12,5 % ist auch für nutztier zu wenig
    t = einfach("nutztier")
    t["aufgaben"][2].pop("forschen")
    assert any("1 von 8 Stationen forschend (mindestens 25 %)" in p for p in fp.gewichtung_probleme(inh_aus([t])))
    # mehr als 25 % reichen nicht, wenn die Zahl 3 fehlt; drei echte Stationen in einem großen Reiter genügen
    gross = lambda key, n_forschen: {"key": key, "lese": "L1", "leseNach": 2, "aufgaben": (
        [_a("vermutung", 1, id="v1"), _a("pruefen", 2, vermutung="v1", erkenntnis="x.")] + [_a("protokoll", 3 + i) for i in range(n_forschen - 2)]
        + [_a("mc", 20, "Sprachwerkstatt · A"), _a("mc", 21, "Sprachwerkstatt · B")])}
    assert not any("echte Forschen-Stationen" in p for p in fp.gewichtung_probleme(inh_aus([gross("nutzen", 3)])))
    assert any("nur 2 echte Forschen-Stationen" in p for p in fp.gewichtung_probleme(inh_aus([gross("nutzen", 2)])))


def test_nutztier_ohne_vermutung_darf_pruefen_nur_mit_vorhandener_vermutung_id_nutzen():
    t = {"key": "nutztier", "aufgaben": [_a("tabelle", 1), _a("bildpunkte", 2), _a("mc", 3, "Sprachwerkstatt · A"), _a("mc", 4, "Sprachwerkstatt · B"),
                                         _a("pruefen", 5, vermutung="v_gibt_es_nicht", erkenntnis="Merksatz.")]}
    probleme = fp.gewichtung_probleme(inh_aus([t]))
    assert any("verweist auf keine vermutung.id" in p for p in probleme), probleme
    t["aufgaben"].insert(0, _a("vermutung", 0, id="v_gibt_es_nicht"))
    assert not any("verweist auf keine vermutung.id" in p for p in fp.gewichtung_probleme(inh_aus([t])))


def test_stationsgrenzen_je_reiter_und_abschluss():
    assert MAX_STATIONEN == {"volk": 13} and max_stationen("volk") == 13
    assert [max_stationen(k) for k in ("nutztier", "koerper", "nutzen", "abschluss")] == [12, 12, 12, 6]
    elf_plus = lambda key: dict(_gut(key), aufgaben=_gut(key)["aufgaben"] + [_a("protokoll", 11, modell={"film": "volk"}), _a("tabelle", 12, modell={"film": "volk"})])   # 12 + Lesestrecke = 13
    assert fp.gewichtung_probleme(inh_aus([elf_plus("volk")])) == []                                      # volk darf 13
    assert any("13 Stationen" in p for p in fp.gewichtung_probleme(inh_aus([elf_plus("nutzen")])))       # nutzen nicht
    sieben = {"key": "abschluss", "aufgaben": [_a("blitz", n) for n in range(7)]}
    assert any("höchstens 6" in p for p in fp.gewichtung_probleme(inh_aus([sieben])))


def test_zaehlung_ist_ehrlich_nur_echte_evidenz_zaehlt_als_forschen():
    """Audit-Entscheidung 3: vermutung, pruefen, protokoll, tabelle, bildwahl, filmmoment (und Diagramm mit auswertung) zählen. Benennen am Bild, Zeichnen, Erkunden,
    Modell-Ziele und der Film sind Anwenden/Vokabeln und zählen nur mit `forschen: true` (an der Aufgabe oder am Niveau); `forschen: false` nimmt auch Echtes heraus."""
    assert ECHT_FORSCHEN_TYPEN == {"vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "filmmoment"}
    assert not fp.zaehlt_als_forschen(_a("diagramm", 1))
    assert fp.zaehlt_als_forschen(_a("diagramm", 1, auswertung="Lies Werte ab und vergleiche."))
    for typ in sorted(ECHT_FORSCHEN_TYPEN):
        assert fp.zaehlt_als_forschen(_a(typ, 9)), typ
    for typ in ("bildpunkte", "zeichnen", "erkunden", "modellfinden", "film"):
        assert not fp.zaehlt_als_forschen(_a(typ, 2)), typ
        assert fp.zaehlt_als_forschen(_a(typ, 2, forschen=True)), f"{typ} mit forschen: true"
        assert fp.zaehlt_als_forschen(_a(typ, 2, niveaus={"A": {}, "B": {"forschen": True}, "C": {}})), f"{typ} mit forschen: true am Niveau"
    assert not fp.zaehlt_als_forschen(_a("tabelle", 3, forschen=False))
    assert not fp.zaehlt_als_forschen(_a("mc", 5)) and not fp.zaehlt_als_forschen(_a("sortierung", 6)) and not fp.zaehlt_als_forschen(_a("mc", 5, forschen=False))
    assert fp.ist_sprachwerkstatt(_a("mc", 7, "Sprachwerkstatt · Artikel")) and not fp.ist_sprachwerkstatt(_a("mc", 8, "Grundwissen"))


# ── Logik unter Node ─────────────────────────────────────────────────────────
def test_forschen_logik_unter_node():
    node_noetig()
    p = subprocess.run([NODE, "--test", os.path.join(ROOT, "tests", "forschen.test.cjs")], capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert p.returncode == 0, (p.stdout + p.stderr)[-3500:]
    assert "fail 0" in p.stdout or "# fail 0" in p.stdout, p.stdout[-1500:]


# ── Einhängepunkte, Tafel ────────────────────────────────────────────────────
def lies(*teile):
    return open(os.path.join(ROOT, *teile), encoding="utf-8").read()


def test_einhaengepunkte():
    html = lies("templates", "index.html")
    assert html.index("js/modell3d.js") < html.index("js/forschen.js") < html.index("js/schritte.js") < html.index("js/app.js")
    assert html.index("js/autosave.js") < html.index("js/forschen.js")
    auf = lies("static", "js", "aufgaben.js")
    assert "BIE.forschen.istMein(t) ? BIE.forschen.render" in auf and "BIE.forschen.nachRender(t)" in auf
    forschen = lies("static", "js", "forschen.js")
    assert "BIE.forschen = " in forschen and 'register("forschen"' in forschen
    assert "docs/FORSCHEN_BEISPIELE.js" in forschen and os.path.exists(BEISPIELE)
    import re
    benutzt = set(re.findall(r"BIE\.film\.([A-Za-z_]+)", forschen))
    assert benutzt <= {"befehle", "knopf"}, f"forschen.js darf von film.js nur knopf() und befehle() benutzen: {benutzt}"
    assert 'tafel_lehrer' not in forschen
    # die Prüfseite (index.html mit pruefmodus) lädt dieselben Skripte; die Lehrer-Tafelseite braucht forschen.js nicht
    assert "forschen.js" not in lies("templates", "tafel_lehrer.html")


def test_tafel_adapter_bietet_die_neuen_typen_nicht_an():
    node_noetig()
    code = f"""
const vm = require("vm"), fs = require("fs");
const ctx = {{ console, window: {{}} }}; ctx.window = ctx; ctx.GT = {{}}; vm.createContext(ctx);
vm.runInContext(fs.readFileSync({json.dumps(os.path.join(ROOT, "static", "js", "inhalte.js"))}, "utf8"), ctx);
vm.runInContext(fs.readFileSync({json.dumps(FIXTURES)}, "utf8"), ctx);
ctx.INHALTE.tabs.push(...ctx.window.FORSCHEN_FIXTURES.tabs);
vm.runInContext(fs.readFileSync({json.dumps(os.path.join(ROOT, "static", "js", "tafel_adapter.js"))}, "utf8"), ctx);
(async () => {{
  const liste = await ctx.GT.abAdapter.aufgaben([]);
  const nrs = ctx.window.FORSCHEN_FIXTURES.tabs.flatMap(t => t.aufgaben.map(a => a.nr));
  process.stdout.write(JSON.stringify({{ angeboten: liste.map(x => x.aufgabe_id), tauglich: nrs.map(n => ctx.GT.abAdapter.tafelTauglich(n)) }}));
}})();
"""
    p = subprocess.run([NODE, "-e", code], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-1500:]
    d = json.loads(p.stdout)
    assert d["angeboten"] == [] and not any(d["tauglich"]), d


# ── Server ───────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("typ", fp.NEUE_TYPEN)
def test_server_nimmt_die_neuen_antworttypen_mit_lesbarem_text_an(student, teacher, typ):
    text = {"vermutung": "Vermutung: etwa 50 000 · Ich vermute, dass es viele sind", "pruefen": "Erkenntnis: Es leben bis zu etwa 50 000 Bienen im Stock. ✅",
            "protokoll": "Beobachtung: Beine = 6 ✅", "tabelle": "Tabelle: 6 von 6 Feldern richtig", "bildwahl": "Wo ist das Futter? · Runde 1: Bereich 2 gewählt ✅",
            "forscherbuch": "Mein Forscherbuch – Silberfuchs"}[typ]
    r = student.post("/api/antwort", json={"aufgabe": NR[1], "niveau": "B", "typ": typ, "frage": "Frage?", "antwort": text, "korrekt": None if typ in ("vermutung", "forscherbuch") else True})
    assert r.status_code == 200 and r.get_json()["ok"]
    sid = session_werte(student)["schueler_id"]
    detail = teacher.get(f"/lehrer/schueler/{sid}").get_data(as_text=True)
    assert text.split(" ✅")[0] in detail and typ in detail, "die Detailseite zeigt Antworttext und Typ"


def test_vermutung_ohne_bewertung_zaehlt_nicht_bei_woran_es_hakt(student, teacher):
    student.post("/api/antwort", json={"aufgabe": NR[1], "niveau": "A", "typ": "vermutung", "frage": "F", "antwort": "Vermutung: x", "korrekt": None})
    student.post("/api/antwort", json={"aufgabe": NR[1], "niveau": "A", "typ": "protokoll", "frage": "Wie viele Beine?", "antwort": "Beobachtung: Beine = 5 ❌", "korrekt": False})
    hakt = teacher.get("/api/lehrer/hakt").get_json()["hakt"]
    assert [(h["nr"], h["versuche"], h["falsch"]) for h in hakt] == [(str(NR[1]), 1, 1)]


def test_forscherbuch_darf_lang_sein_alles_andere_wird_bei_500_gekappt(student):
    lang = "Zeile mit Vermutung und Erkenntnis.\n" * 300                  # ≈ 10 800 Zeichen
    assert student.post("/api/antwort", json={"aufgabe": NR[0], "niveau": "A", "typ": "forscherbuch", "antwort": lang}).status_code == 200
    assert student.post("/api/antwort", json={"aufgabe": NR[0], "niveau": "A", "typ": "protokoll", "antwort": lang}).status_code == 200
    zeilen = appmodule.get_db().execute("SELECT antwort_typ, length(antwort_text) AS n FROM antworten ORDER BY id").fetchall()
    assert [(z["antwort_typ"], z["n"]) for z in zeilen] == [("forscherbuch", 8000), ("protokoll", 500)]
    assert config.ANTWORT_MAX_ZEICHEN == {"forscherbuch": 8000}, "das Forscherbuch ist ein ganzes Heft (Audit T8: 8000 statt 2000)"


def test_autosave_nimmt_den_forschen_zustand_an_und_gibt_ihn_zurueck(student):
    from config import APP_ID, STATE_SCHEMA_VERSION
    sid = session_werte(student)["schueler_id"]
    zustand = {"schema_version": STATE_SCHEMA_VERSION, "app_id": APP_ID, "lernplatz": {"schueler_id": sid}, "active_tab": "nutztier",
               "forschen": {str(NR[0]): {"niveau": "A", "wahl": [2], "satz": "", "fest": True, "text": "etwa 5 000", "antwort": "Vermutung: etwa 5 000", "optionen": ["etwa 5 000"]}}}
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand}).get_json()["accepted"] is not False
    d = student.get("/api/autosave").get_json()
    assert d["state"]["forschen"][str(NR[0])]["text"] == "etwa 5 000"
    kaputt = dict(zustand, forschen=["keine", "Zuordnung"])
    assert student.post("/api/autosave", json={"revision": 2, "state": kaputt}).status_code == 400
    assert student.get("/api/autosave").get_json()["state"]["forschen"][str(NR[0])]["fest"] is True


def test_dashboard_zeigt_die_vermutungen_der_klasse(student, teacher, client):
    """Verteilung der gewählten Optionen je Forscherfrage und Sätze der Kinder; gezählt wird je Kind die letzte Vermutung."""
    from conftest import anmelden
    zweiter = anmelden(appmodule.app.test_client(), "Zweiter", "6a")
    dritter = anmelden(appmodule.app.test_client(), "Dritter", "6a")
    def verm(c, niveau, text, nr=NR[0]):
        assert c.post("/api/antwort", json={"aufgabe": nr, "niveau": niveau, "typ": "vermutung", "frage": "Wie viele Bienen?", "antwort": text, "korrekt": None}).status_code == 200
    verm(student, "A", "Vermutung: etwa 500")
    verm(student, "A", "Vermutung: etwa 5 000")                                   # ersetzt die erste
    verm(zweiter, "B", "Vermutung: etwa 5 000 · Ich vermute, dass es viele sind, weil das Volk groß ist.")
    verm(dritter, "C", "Vermutung: Ich vermute, dass es mehr als tausend sind, weil ein Stock so groß ist.")
    verm(dritter, "A", "Vermutung: Die Bienen brauchen Honig. | Der Imker mag keinen Honig.", nr=NR[1])
    d = teacher.get("/api/lehrer/vermutungen").get_json()
    assert d["ok"] and [g["nr"] for g in d["vermutungen"]] == [str(NR[0]), str(NR[1])]
    g = d["vermutungen"][0]
    assert g["anzahl"] == 3 and g["frage"] == "Wie viele Bienen?"
    assert g["verteilung"] == [{"option": "etwa 5 000", "anzahl": 2}]
    assert [(s["pseudonym"], s["text"][:20]) for s in g["saetze"]] == [("Zweiter", "Ich vermute, dass es"), ("Dritter", "Ich vermute, dass es")]
    assert {v["option"]: v["anzahl"] for v in d["vermutungen"][1]["verteilung"]} == {"Die Bienen brauchen Honig.": 1, "Der Imker mag keinen Honig.": 1}
    state = teacher.get("/api/lehrer/state").get_json()
    assert state["vermutungen"] == d["vermutungen"]
    assert client.get("/api/lehrer/vermutungen").status_code == 401
    assert 'id="vermutungen-card"' in teacher.get("/lehrer").get_data(as_text=True)


def test_forschen_zustand_ueberlebt_zwischenstand_und_wiederherstellung(student, teacher):
    """Snapshot (und ebenso das IServ-Archiv, das dieselben Arbeitsstände sichert): der Forschen-Zustand ist Teil des Arbeitsstands."""
    import db as dbmod
    from config import APP_ID, STATE_SCHEMA_VERSION
    sid = session_werte(student)["schueler_id"]
    forschen = {str(NR[0]): {"niveau": "A", "wahl": [1], "satz": "", "fest": True, "text": "etwa 500", "antwort": "Vermutung: etwa 500", "optionen": ["etwa 500"]},
                str(NR[1]): {"niveau": "A", "z": [{"w": "6", "ok": True, "f": 1, "g": False}], "schluss": {"wahl": None, "satz": "", "fertig": False}}}
    zustand = {"schema_version": STATE_SCHEMA_VERSION, "app_id": APP_ID, "lernplatz": {"schueler_id": sid}, "active_tab": "nutztier", "forschen": forschen}
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand}).status_code == 200
    snap = teacher.post("/api/lehrer/snapshots", json={"name": "Forschen"}).get_json()["snapshot"]["id"]
    teacher.post("/api/lehrer/daten-loeschen", json={"schueler_id": sid})
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM arbeitsstaende").fetchone()["n"] == 0
    assert teacher.post(f"/api/lehrer/snapshots/{snap}/laden").get_json()["ok"]
    row = dbmod.get_db().execute("SELECT state_json FROM arbeitsstaende WHERE schueler_id=?", (sid,)).fetchone()
    assert json.loads(row["state_json"])["forschen"] == forschen


def test_dashboard_erklaert_die_neuen_stationen(teacher):
    html = teacher.get("/lehrer").get_data(as_text=True)
    assert "Lesestrecken (Nachschlagen" in html and "Stationsplan" in html
