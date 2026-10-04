"""Tafel-Baustein im AB: Anmeldung, Speicherung im Snapshot, Präsentationsmodus, Datenschutz."""
import pytest

import app as appmodule
import db as dbmod
import praesentation
from conftest import anmelden, session_werte

NS = "/tafel"


@pytest.fixture(autouse=True)
def frische_tafel(client):
    appmodule.tafel_server.neu_laden_und_senden()  # DB wurde von frische_sitzung geleert
    yield


def _tafel_socket(flask_client, auth=None):
    return appmodule.socketio.test_client(appmodule.app, namespace=NS, flask_test_client=flask_client, auth=auth or {})


def _lehrer(teacher, teacher_token):
    return _tafel_socket(teacher, {"lehrer_token": teacher_token})


def _emit(s, ereignis, daten=None):
    return s.emit(ereignis, daten or {}, callback=True, namespace=NS)


def test_anmeldung_im_tafel_kanal(student, teacher, teacher_token):
    fremd = appmodule.app.test_client()
    assert not _tafel_socket(fremd).is_connected(NS)
    assert not _tafel_socket(fremd, {"lehrer_token": "falsch"}).is_connected(NS)
    s = _tafel_socket(student)
    assert s.is_connected(NS)
    l = _lehrer(teacher, teacher_token)
    assert l.is_connected(NS)
    liste = [e["args"][0] for e in l.get_received(NS) if e["name"] == "lehrer:schueler"][-1]
    assert liste[0]["name"] == "Silberfuchs" and liste[0]["online"]
    # der Default-Kanal des ABs bleibt unberührt
    alt = appmodule.socketio.test_client(appmodule.app, flask_test_client=student)
    alt.emit("schueler_join", {})
    assert alt.is_connected()


def test_schueler_kann_keine_lehrerbefehle(student):
    s = _tafel_socket(student)
    assert _emit(s, "lehrer:modus", {"modus": "live"})["ok"] is False


def test_tafel_landet_im_snapshot_und_kommt_zurueck(teacher, teacher_token):
    l = _lehrer(teacher, teacher_token)
    _emit(l, "lehrer:modus", {"modus": "live"})
    _emit(l, "tafel:op", {"op": "add", "seite": 0, "objekt": {"id": "t1", "typ": "text", "text": "Honig", "farbe": 0}})
    appmodule.tafel_server.sofort_sichern()
    snapshot = dbmod.build_snapshot()
    assert snapshot["tabellen"]["tafel_zustand"], "Tafel fehlt im Snapshot"
    dbmod.validate_snapshot(snapshot)
    # Zwischenstand speichern, Tafel leeren, Zwischenstand laden → Text ist wieder da
    h = {"X-Lehrer-Token": teacher_token}
    info = teacher.post("/api/lehrer/snapshots", json={"name": "vor dem Leeren"}, headers=h).get_json()["snapshot"]
    _emit(l, "lehrer:leeren", {"alle": True})
    assert appmodule.tafel_server.tafel.objekt(0, "t1") is None
    teacher.post(f"/api/lehrer/snapshots/{info['id']}/laden", headers=h)
    assert appmodule.tafel_server.tafel.objekt(0, "t1")["text"] == "Honig"


def test_sitzung_zuruecksetzen_leert_die_tafel(teacher, teacher_token):
    l = _lehrer(teacher, teacher_token)
    _emit(l, "tafel:op", {"op": "add", "seite": 0, "objekt": {"id": "t1", "typ": "text", "text": "x", "farbe": 0}})
    appmodule.tafel_server.sofort_sichern()
    teacher.post("/api/lehrer/sitzung-zuruecksetzen", headers={"X-Lehrer-Token": teacher_token})
    assert appmodule.tafel_server.tafel.objekt(0, "t1") is None


def test_tafel_und_praesentation_schliessen_sich_aus(teacher, teacher_token):
    h = {"X-Lehrer-Token": teacher_token}
    bild = next(iter(praesentation.BILDER))
    teacher.post("/api/lehrer/praesentation", json={"aktiv": True, "bild": bild}, headers=h)
    assert praesentation.aktiv()
    l = _lehrer(teacher, teacher_token)
    _emit(l, "lehrer:modus", {"modus": "live"})
    assert not praesentation.aktiv()
    teacher.post("/api/lehrer/praesentation", json={"aktiv": True, "bild": bild}, headers=h)
    assert appmodule.tafel_server.tafel.modus == "aus"
    teacher.post("/api/lehrer/praesentation", json={"aktiv": False}, headers=h)


def test_angebot_und_karte_vom_browser(student, teacher, teacher_token):
    karte = {"titel": "Aufgabe 3: Lückentext", "aufgabentyp": "lueckentext", "niveau": "A",
             "inhalt": {"segmente": [{"text": "Das ist das "}, {"luecke": "Honig"}]}}
    r = student.post("/tafel/api/angebot", json={"aufgabe_id": "3", "karte": karte})
    assert r.status_code == 200
    l = _lehrer(teacher, teacher_token)
    _emit(l, "lehrer:modus", {"modus": "live"})
    angebot = appmodule.tafel_server.tafel.angebote[0]
    assert _emit(l, "lehrer:angebot_annehmen", {"angebot_id": angebot["id"]})["ok"]
    sid = session_werte(student)["schueler_id"]
    assert appmodule.tafel_server.tafel.ist_am_brett(sid)


def test_arbeitsstand_nur_fuer_lehrkraft(student, teacher, teacher_token):
    sid = session_werte(student)["schueler_id"]
    assert student.get(f"/tafel/api/lehrer/arbeitsstand/{sid}").status_code == 401
    r = teacher.get(f"/tafel/api/lehrer/arbeitsstand/{sid}", headers={"X-Lehrer-Token": teacher_token})
    assert r.status_code == 200 and r.get_json()["ok"]


def test_lernplatz_loeschen_entfernt_tafelbeitraege(student, teacher, teacher_token):
    sid = session_werte(student)["schueler_id"]
    l = _lehrer(teacher, teacher_token)
    s = _tafel_socket(student)
    _emit(l, "lehrer:modus", {"modus": "live"})
    _emit(l, "lehrer:zuschalten", {"schueler_id": sid})
    assert _emit(s, "tafel:op", {"op": "add", "seite": 0, "objekt": {"id": "a", "typ": "strich", "punkte": [[0, 0, .5]], "farbe": 0, "staerke": 2}})["ok"]
    teacher.post("/api/lehrer/daten-loeschen", json={"schueler_id": sid}, headers={"X-Lehrer-Token": teacher_token})
    assert appmodule.tafel_server.tafel.objekt(0, "a") is None


def test_lehrerseiten(teacher):
    for pfad in ("/lehrer/tafel", "/lehrer/tafel/rueckblick", "/lehrer/tafel/beamer"):
        r = teacher.get(pfad)
        assert r.status_code == 200, pfad
        assert b"LEHRER_TOKEN" in r.data
    assert appmodule.app.test_client().get("/lehrer/tafel").status_code == 302


def test_schuelerseite_bindet_tafel_ein(student):
    html = student.get("/arbeitsblatt").get_data(as_text=True)
    assert 'id="tafel-overlay"' in html and "tafel_schueler.js" in html and "tafel/tafel-app.js" in html
