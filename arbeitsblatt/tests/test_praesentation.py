"""Präsentationsmodus: Die Lehrkraft zeigt allen dasselbe Bild.

Kern der Prüfungen: Niemand wird ausgelassen. Der Zustand gilt für bereits
Angemeldete, für später Hinzukommende und über einen Serverneustart hinweg.
Arbeit ist währenddessen serverseitig gesperrt – der Autosave aber nicht.
"""
import inhalte_server
import praesentation
import pytest
from conftest import NR, anmelden, appmodule, session_werte

CANVAS = {"version": "5.3.0", "objects": [{"type": "rect", "left": 1, "top": 1, "width": 9, "height": 9}]}


@pytest.fixture(autouse=True)
def ohne_laufende_praesentation():
    """Der teacher-Fixture setzt die Sitzung nicht zurück – hier selbst aufräumen."""
    praesentation.beenden()
    yield
    praesentation.beenden()


def start(teacher, bild="einstieg", hinweis=""):
    return teacher.post("/api/lehrer/praesentation",
                        json={"aktiv": True, "bild": bild, "hinweis": hinweis}).get_json()


def stopp(teacher):
    return teacher.post("/api/lehrer/praesentation", json={"aktiv": False}).get_json()


def test_bilderliste_enthaelt_einstieg_und_lesestrecken():
    bilder = praesentation.bilder_fuer_client()
    keys = {b["key"] for b in bilder}
    assert "einstieg" in keys
    assert "nutztier-1" in keys and "nutzen-1" in keys
    # Einstiegsbild + je ein Eintrag pro Abschnitt jeder Lesestrecke
    assert len(bilder) == 1 + sum(len(s["abschnitte"]) for s in inhalte_server.LESESTRECKEN.values())
    for b in bilder:
        assert b["bild"].startswith("/static/img/lese/") and b["titel"] and b["gruppe"]


def test_start_und_stopp(student, teacher):
    assert student.get("/api/status").get_json()["praesentation"]["active"] is False
    r = start(teacher, "einstieg", "Beschreibe, was du siehst.")
    assert r["ok"] and r["praesentation"]["active"] is True
    assert r["praesentation"]["titel"] == "Beim Imker (Einstiegsbild)"
    assert r["praesentation"]["hinweis"] == "Beschreibe, was du siehst."
    assert ".svg" in r["praesentation"]["bild"] and "/static/img/lese/" in r["praesentation"]["bild"]

    # Bereits angemeldete Lernende erfahren es über Status und Sicherheitsabfrage
    assert student.get("/api/status").get_json()["praesentation"]["active"] is True
    assert student.get("/api/praesentation").get_json()["praesentation"]["active"] is True

    assert stopp(teacher)["praesentation"]["active"] is False
    assert student.get("/api/status").get_json()["praesentation"]["active"] is False


def test_wer_sich_spaeter_anmeldet_sieht_es_auch(student, teacher):
    start(teacher, "nutztier-1")
    spaet = anmelden(appmodule.app.test_client(), "Spätzünder", "6b")
    zustand = spaet.get("/api/status").get_json()["praesentation"]
    assert zustand["active"] is True and zustand["key"] == "nutztier-1"


def test_unbekanntes_bild_wird_abgelehnt(teacher):
    r = teacher.post("/api/lehrer/praesentation", json={"aktiv": True, "bild": "../../etc/passwd"})
    assert r.status_code == 400
    assert praesentation.lesen()["active"] is False


def test_nur_die_lehrkraft_darf_schalten(student):
    assert student.post("/api/lehrer/praesentation", json={"aktiv": True, "bild": "einstieg"}).status_code == 401
    assert student.get("/api/lehrer/praesentation").status_code == 401
    assert praesentation.lesen()["active"] is False


@pytest.mark.parametrize("pfad,nutzlast", [
    ("/api/fortschritt", {"aufgabe": NR[1], "niveau": "A"}),
    ("/api/antwort", {"aufgabe": NR[1], "niveau": "A", "typ": "mc", "antwort": "x", "korrekt": True}),
    ("/api/zeichnung", {"geraet": "biene", "canvas_json": CANVAS}),
    ("/api/chat", {"message": "Hallo"}),
    ("/api/lesestrecke/nutztier/antwort", {"phase": 0, "wahl": 0}),
])
def test_arbeit_ist_waehrend_der_praesentation_gesperrt(student, teacher, pfad, nutzlast):
    """Auch wer das Overlay im Browser entfernt, kann nicht weiterarbeiten."""
    start(teacher)
    r = student.post(pfad, json=nutzlast)
    assert r.status_code == 423, pfad
    assert r.get_json()["praesentation"] is True
    stopp(teacher)
    assert student.post(pfad, json=nutzlast).status_code != 423, pfad


def test_autosave_bleibt_offen(student, teacher):
    """Eingetipptes darf nicht verloren gehen, nur weil ein Bild gezeigt wird."""
    from config import APP_ID, STATE_SCHEMA_VERSION
    sid = session_werte(student)["schueler_id"]
    start(teacher)
    zustand = {"schema_version": STATE_SCHEMA_VERSION, "app_id": APP_ID,
               "lernplatz": {"schueler_id": sid}, "texte": {"ft-36": "Mein Text"}}
    r = student.post("/api/autosave", json={"revision": 1, "state": zustand})
    assert r.status_code == 200 and r.get_json()["ok"]
    assert student.get("/api/autosave").get_json()["state"]["texte"]["ft-36"] == "Mein Text"


def test_zustand_ueberlebt_neustart(student, teacher):
    """Der Zustand liegt in der Datenbank, nicht im Arbeitsspeicher."""
    start(teacher, "koerper-1", "Was fällt dir auf?")
    frisch = praesentation.lesen()      # neuer Lesevorgang, kein zwischengespeicherter Wert
    assert frisch["active"] and frisch["key"] == "koerper-1" and frisch["hinweis"] == "Was fällt dir auf?"


def test_status_im_dashboard(teacher):
    start(teacher, "volk-1")
    d = teacher.get("/api/lehrer/state").get_json()
    assert d["praesentation"]["active"] is True and d["praesentation"]["key"] == "volk-1"
    assert len(d["praesentation_bilder"]) == len(praesentation.BILDER)
    stopp(teacher)


def test_hinweis_wird_begrenzt(teacher):
    r = start(teacher, "einstieg", "x" * 500)
    assert len(r["praesentation"]["hinweis"]) == 200


def test_reset_beendet_die_praesentation(student, teacher):
    """Beim Zurücksetzen der Sitzung darf kein Bild hängen bleiben."""
    start(teacher)
    teacher.post("/api/lehrer/sitzung-zuruecksetzen", json={})
    assert praesentation.lesen()["active"] is False
