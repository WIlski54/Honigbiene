"""Lesestrecken (Server) – laufen über die Aggregation aus lesen_<reiter>.py.

Platzhalter-Strecken (`"platzhalter": True`) bestehen die Struktur-Tests, die Qualitätstests für echte Strecken
(Abschnittszahl, Verteilung der Lösungen) überspringen sie mit Hinweis. Ob schon alles geschrieben ist, prüft
tests/test_inhalte_struktur.py::test_inhalte_vollstaendig.
"""
import os
import re
import time
import warnings

import db as dbmod
import inhalte_server as inh
from conftest import session_werte

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERSTE = next(iter(inh.LESESTRECKEN))     # der erste Reiter mit Lesestrecke: „nutztier“


def _echte():
    """Nur geschriebene Lesestrecken; Platzhalter werden als „noch nicht geschrieben“ gemeldet."""
    echte = {k: s for k, s in inh.LESESTRECKEN.items() if not s.get("platzhalter")}
    offen = sorted(set(inh.LESESTRECKEN) - set(echte))
    if offen:
        warnings.warn(f"Noch nicht geschrieben: Lesestrecke(n) {', '.join(offen)} (Platzhalter)", stacklevel=2)
    return echte


def test_aggregation_und_struktur():
    assert set(inh.LESESTRECKEN) == {"nutztier", "koerper", "volk", "nutzen"}
    for key, strecke in inh.LESESTRECKEN.items():
        assert strecke["abschnitte"], key
        for a in strecke["abschnitte"]:
            assert len(a["optionen"]) == 3 and 0 <= a["loesung"] < 3
            assert len(set(a["optionen"])) == 3
            assert a["erklaerung"] and a["text"] and a["frage"] and a["ueberschrift"]


def test_echte_lesestrecken_haben_4_bis_7_abschnitte():
    for key, strecke in _echte().items():
        assert 4 <= len(strecke["abschnitte"]) <= 7, key


def test_jeder_abschnitt_hat_ein_schaubild():
    for key, strecke in inh.LESESTRECKEN.items():
        for a in strecke["abschnitte"]:
            assert a.get("bild") and a.get("bild_alt"), (key, a["ueberschrift"])
            assert os.path.exists(os.path.join(ROOT, "static", "img", "lese", a["bild"] + ".svg")), a["bild"]


def test_loesungspositionen_sind_verteilt():
    """Sonst ist „wahl=0“ im Netzwerkverkehr immer richtig (fallstricke.md)."""
    for key, strecke in _echte().items():
        positionen = [a["loesung"] for a in strecke["abschnitte"]]
        assert len(set(positionen)) >= 2, (key, positionen)
    alle = [a["loesung"] for s in _echte().values() for a in s["abschnitte"]]
    if len(alle) >= 12:
        for pos in (0, 1, 2):
            assert alle.count(pos) >= 3, (pos, alle)
    # Auch die Platzhalter liegen nicht alle auf Position 0
    assert len({s["abschnitte"][0]["loesung"] for s in inh.LESESTRECKEN.values()}) >= 2


def test_saetze_der_lesestrecken_sind_kurz():
    """Sek-I-Sprache: ein Gedanke pro Satz, höchstens etwa 15 Wörter (lernpfad.md)."""
    zu_lang = []
    for key, strecke in inh.LESESTRECKEN.items():
        for a in strecke["abschnitte"]:
            klartext = re.sub(r"<[^>]+>", "", a["text"])
            for satz in re.split(r"[.!?]\s|\n", klartext):
                woerter = [w for w in satz.split() if w.strip()]
                if len(woerter) > 17:
                    zu_lang.append((key, len(woerter), satz.strip()[:70]))
    assert not zu_lang, zu_lang


def test_antwortoptionen_sind_kurz():
    """Antwortoptionen kurz halten – höchstens 12 Wörter (lernpfad.md)."""
    zu_lang = [(k, o) for k, s in inh.LESESTRECKEN.items() for a in s["abschnitte"] for o in a["optionen"] if len(o.split()) > 12]
    assert not zu_lang, zu_lang


def test_glossar_deckt_alle_fetten_begriffe(student):
    """Jeder fett markierte Begriff ist entweder ein Datum oder hat einen Glossareintrag."""
    import glossar
    datum = re.compile(r"^\d{1,2}\.(/\d{1,2}\.)? ?[A-Za-zä]+( \d{4})?$|^\d{4}$")
    fehlend = []
    for key, strecke in inh.LESESTRECKEN.items():
        for a in strecke["abschnitte"]:
            for begriff in re.findall(r"<strong>(.*?)</strong>", a["text"]):
                if datum.match(begriff.strip()):
                    continue
                if glossar.eintrag_fuer(begriff) is None:
                    fehlend.append((key, begriff))
    assert not fehlend, fehlend
    r = student.get("/api/glossar").get_json()
    assert r["ok"] and "nutztier" in r["eintraege"] and r["aliase"]["nutztiere"] == "nutztier"
    assert r["eintraege"]["nutztier"]["titel"] == "Nutztier"


def test_client_daten_enthalten_keine_loesung(student):
    r = student.get(f"/api/lesestrecke/{ERSTE}").get_json()
    assert r["ok"] and r["anzahl"] == len(inh.LESESTRECKEN[ERSTE]["abschnitte"]) and r["status"]["phase"] == 0
    for a in r["abschnitte"]:
        assert "loesung" not in a and "erklaerung" not in a
        assert len(a["optionen"]) == 3
        assert a["bild"].startswith("/static/img/lese/") and a["bild_alt"]
    assert student.get("/api/lesestrecke/unbekannt").status_code == 404
    for key in inh.LESESTRECKEN:
        assert student.get(f"/api/lesestrecke/{key}").get_json()["ok"], key


def test_richtig_falsch_sperre_und_abschluss(student):
    """Sperre 60/75/90 s nach Fehlversuch, Reload umgeht sie nicht, Abschluss setzt die Station."""
    key = ERSTE
    strecke = inh.LESESTRECKEN[key]
    station = strecke["station"]
    sid = session_werte(student)["schueler_id"]
    loesung = strecke["abschnitte"][0]["loesung"]
    falsch = (loesung + 1) % 3
    url = f"/api/lesestrecke/{key}"
    # falsche Antwort → protokolliert, Sperre 60 s, Phase bleibt 0
    r = student.post(url + "/antwort", json={"phase": 0, "wahl": falsch}).get_json()
    assert r["korrekt"] is False and r["status"]["phase"] == 0 and r["status"]["versuche"] == 1
    assert 55 <= r["status"]["retry_until"] - time.time() <= 61
    # Antwort während der Sperre → 429 mit retry_until (Reload umgeht die Sperre nicht)
    r2 = student.post(url + "/antwort", json={"phase": 0, "wahl": loesung})
    assert r2.status_code == 429 and r2.get_json()["status"]["retry_until"] == r["status"]["retry_until"]
    assert student.get(url).get_json()["status"]["retry_until"] == r["status"]["retry_until"]

    def sperre_aufheben():
        with dbmod.get_db() as db:
            db.execute("UPDATE lesestrecke_status SET retry_until=0 WHERE schueler_id=?", (sid,))
            db.commit()

    # zweiter Fehlversuch → 75 s, dritter → 90 s
    sperre_aufheben()
    r = student.post(url + "/antwort", json={"phase": 0, "wahl": falsch}).get_json()
    assert 70 <= r["status"]["retry_until"] - time.time() <= 76
    sperre_aufheben()
    r = student.post(url + "/antwort", json={"phase": 0, "wahl": falsch}).get_json()
    assert 85 <= r["status"]["retry_until"] - time.time() <= 91
    sperre_aufheben()
    # falsche Phase → 409
    assert student.post(url + "/antwort", json={"phase": 5, "wahl": 0}).status_code in (400, 409)
    # richtig → nächste Phase mit Erklärung bzw. fertig
    r = student.post(url + "/antwort", json={"phase": 0, "wahl": loesung}).get_json()
    assert r["korrekt"] is True and r["erklaerung"]
    for phase in range(1, len(strecke["abschnitte"])):
        l = strecke["abschnitte"][phase]["loesung"]
        r = student.post(url + "/antwort", json={"phase": phase, "wahl": l}).get_json()
    assert r["status"]["fertig"] is True and r["station"] == station
    status = student.get("/api/status").get_json()
    assert {e["nr"] for e in status["erledigt"]} == {station}
    n = len(strecke["abschnitte"])
    antworten = dbmod.get_db().execute("SELECT korrekt FROM antworten WHERE schueler_id=? AND antwort_typ='lesestrecke'", (sid,)).fetchall()
    assert [a["korrekt"] for a in antworten] == [0, 0, 0] + [1] * n
    # nach Abschluss keine weiteren Antworten
    assert student.post(url + "/antwort", json={"phase": n - 1, "wahl": 0}).status_code == 409
    daten = student.get(url).get_json()
    assert all("erklaerung" in a for a in daten["abschnitte"])
