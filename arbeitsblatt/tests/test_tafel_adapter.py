"""Tafel-Adapter (static/js/tafel_adapter.js): jede Fassung muss vom Server der Tafel akzeptiert werden.

Der Adapter läuft im Browser; hier wird er mit Node ausgeführt (echte Inhalte + synthetische Aufgaben aller Typen)
und seine Ausgabe gegen die Prüfungen des Server-Pakets tafel/ gehalten (aufgabe_bereinigen, loesung_bereinigen,
karte_bereinigen). Angeboten werden nur: mc, Richtig/Falsch-Liste, luecke, zuordnung, sortierung, freitext.
"""
import functools
import json
import os
import subprocess

import pytest

from inhalte_laden import JS, NODE, ROOT, inhalte_dateien, node_noetig
from plan import OHNE_TAFEL
from tafel import aufgaben as tafel

ANGEBOTEN = {"mc", "luecke", "zuordnung", "sortierung", "freitext"}   # AB-Typen mit Tafel-Fassung


@functools.lru_cache(maxsize=1)
def _daten() -> dict:
    node_noetig()
    p = subprocess.run(
        [NODE, os.path.join(ROOT, "tests", "_tafel_adapter_daten.cjs"), os.path.join(JS, "tafel_adapter.js"),
         *[os.path.join(JS, f) for f in inhalte_dateien()]],
        capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
    return json.loads(p.stdout)


def test_alle_fassungen_werden_vom_server_akzeptiert():
    d = _daten()
    assert d["leer"], "Der Adapter lieferte keine Aufgaben"
    typen = set()
    for e in d["leer"]:
        wer = f"Aufgabe {e['id']} Niveau {e['niveau']}"
        a = tafel.aufgabe_bereinigen(e["aufgabe"])            # wirft ValueError bei Fehlern
        typen.add(a["aufgabentyp"])
        loesung = tafel.loesung_bereinigen(a, e["loesung"])
        if a["aufgabentyp"] == "freitext":
            assert loesung is None, wer
            continue
        ids = tafel.feld_ids(a)
        assert set(loesung) == set(ids), f"{wer}: Lösung deckt nicht alle Felder ab ({set(ids) - set(loesung)})"
        erlaubt = tafel.optionen(a)
        for feld, werte in loesung.items():
            assert werte, f"{wer}: leere Lösung für {feld}"
            if erlaubt is not None:
                gueltig = [w for w in werte for t in (w.split("|") if a.get("mehrfach") else [w]) if t not in erlaubt]
                assert not gueltig, f"{wer}: Lösung {gueltig} steht nicht in den Optionen"
    assert typen == {"mc", "richtigfalsch", "lueckentext", "zuordnung", "sortieren", "freitext"}, typen


def test_nur_geeignete_typen_werden_angeboten():
    d = _daten()
    angeboten = {str(x["aufgabe_id"]) for x in d["liste"]}
    for nr, tauglich in d["tauglich"].items():
        assert tauglich == (nr in angeboten), nr
    # Synthetische Aufgaben 901–906 sind tafeltauglich, 907–918 nicht
    assert {str(n) for n in range(901, 907)} <= angeboten
    assert not angeboten & {str(n) for n in range(907, 919)}
    for x in d["liste"]:
        assert x["typ"] in ANGEBOTEN, f"Typ {x['typ']} dürfte nicht angeboten werden (ohne Tafel: {sorted(OHNE_TAFEL)})"


def test_richtig_falsch_wird_zu_richtigfalsch():
    d = _daten()
    rf = [e for e in d["leer"] if e["id"] == "902"]
    assert len(rf) == 3
    for e in rf:
        assert e["aufgabe"]["aufgabentyp"] == "richtigfalsch"
        assert [a["text"] for a in e["aufgabe"]["aussagen"]][0] in ("A1", "B1", "C1")
        assert set(sum(e["loesung"].values(), [])) <= {"richtig", "falsch"}
    # Niveau A: A1 stimmt, A2 stimmt nicht
    assert next(e for e in rf if e["niveau"] == "A")["loesung"] == {"r0": ["richtig"], "r1": ["falsch"]}


def test_niveau_a_bausteine_laufen_als_sortieren():
    d = _daten()
    a = next(e for e in d["leer"] if e["id"] == "906" and e["niveau"] == "A")
    assert a["aufgabe"]["aufgabentyp"] == "sortieren"
    assert next(e for e in d["leer"] if e["id"] == "906" and e["niveau"] == "B")["aufgabe"]["aufgabentyp"] == "freitext"


def test_karten_aus_dem_arbeitsstand_sind_gueltig():
    d = _daten()
    for name, karten in d["karten"].items():
        assert karten
        for k in karten:
            sauber = tafel.karte_bereinigen(k)
            assert sauber["titel"], (name, k["aufgabe_id"])
    mit = {k["aufgabe_id"]: k for k in d["karten"]["mitAntworten"]}
    assert mit["902"]["bearbeitet"] and "→ falsch" in mit["902"]["inhalt"]["text"] and "→ richtig" in mit["902"]["inhalt"]["text"]
    assert mit["901"]["bearbeitet"] and mit["903"]["bearbeitet"] and mit["904"]["bearbeitet"] and mit["905"]["bearbeitet"]
    assert not any(k["bearbeitet"] for k in d["karten"]["leer"])


def test_echte_aufgaben_und_ausgefuellte_karten_passen_ohne_abschneiden_an_die_tafel():
    """Alle angebotenen echten Aufgaben (A/B/C): Der Server der Tafel darf weder Texte kürzen (Lücken, Zuordnung, Reihenfolge,
    Wortkiste, Fragen) noch Karten (Umbruch langer Sätze, Lücken, Paare) – sonst fehlen Wörter oder eine Lösung ist unerreichbar."""
    node_noetig()
    p = subprocess.run([NODE, os.path.join(ROOT, "tests", "_tafel_adapter_karten.cjs"), os.path.join(JS, "tafel_adapter.js"),
                        *[os.path.join(JS, f) for f in inhalte_dateien()]], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
    d = json.loads(p.stdout)
    assert d["karten"], "keine Karten"
    for e in _daten()["leer"]:
        if str(e["id"]).isdigit() and int(e["id"]) >= 900:
            continue                                                  # synthetische Aufgaben
        wer = f"Aufgabe {e['id']} Niveau {e['niveau']}"
        roh = e["aufgabe"]
        a = tafel.aufgabe_bereinigen(roh)
        for feld in ("frage", "elemente", "wortbank", "optionen", "zeilen", "aussagen", "teile"):
            assert roh.get(feld, None) == a.get(feld, None) or feld in ("zeilen", "aussagen", "teile"), f"{wer}: {feld} wurde gekürzt"
        for z, z2 in zip(roh.get("zeilen", []), a.get("zeilen", [])):
            assert z["text"] == z2["text"], f"{wer}: Zeilentext gekürzt"
        for t, t2 in zip(roh.get("teile", []), a.get("teile", [])):
            assert t.get("text") == t2.get("text"), f"{wer}: Textteil gekürzt"
        grenze = tafel.MAX_LAENGE.get(roh["aufgabentyp"], 200)
        for feld, werte in e["loesung"].items() if e["loesung"] else []:
            assert all(len(w) <= grenze for w in werte), f"{wer}: Lösung länger als {grenze} Zeichen – die Antwort würde abgeschnitten und nie richtig"
    for k in d["karten"]:
        wer = f"Aufgabe {k['aufgabe_id']} Niveau {k['n']}"
        sauber = tafel.karte_bereinigen(k)
        assert sauber["inhalt"] == k["inhalt"], f"{wer}: Karte wird vom Server verändert/gekürzt"
        assert k["bearbeitet"], f"{wer}: Karte gilt trotz Antworten als unbearbeitet"
