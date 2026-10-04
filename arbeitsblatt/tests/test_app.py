import json
import os
import re

import app as appmodule
import db as dbmod
from config import ABSCHNITTE, ALLE_AUFGABEN
from conftest import NR, anmelden, session_werte

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True and data["ki"] is False


def test_login_requires_privacy_and_pseudonym(client):
    resp = client.post("/login", data={"pseudonym": "A", "klasse": "8", "privacy_ok": "on"})
    assert "mindestens 2 Zeichen" in resp.get_data(as_text=True)
    resp = client.post("/login", data={"pseudonym": "Fuchs", "klasse": "8"})
    assert "Datenschutz" in resp.get_data(as_text=True)
    assert client.get("/arbeitsblatt").status_code == 302
    assert client.get("/api/status").status_code == 401


def test_student_page_and_status(student):
    page = student.get("/arbeitsblatt")
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "Die Honigbiene – ein Nutztier mit eigenem Staat" in html and "NW · Klasse 6" in html
    assert "inhalte.js" in html and "inhalte_abschluss.js" in html and "app.js" in html
    assert session_werte(student)["resume_token"] in html  # Token wandert in den Browser-Storage
    status = student.get("/api/status").get_json()
    assert status["ok"] and status["erledigt"] == [] and status["aufgaben_gesamt"] == len(ALLE_AUFGABEN) == len(NR) + 4   # 4 Lesestrecken + alle Aufgaben des Plans
    assert status["ki_konfiguriert"] is False and status["autosave"] is None


def test_fortschritt_and_abschnitte(student):
    assert student.post("/api/fortschritt", json={"aufgabe": NR[0], "niveau": "B"}).get_json()["ok"]
    assert student.post("/api/fortschritt", json={"aufgabe": "T"}).get_json()["ok"]
    assert student.post("/api/fortschritt", json={"aufgabe": "l1", "niveau": "A"}).get_json()["ok"]
    assert student.post("/api/fortschritt", json={"aufgabe": NR[0], "niveau": "B"}).get_json()["erledigt"] == 3
    assert student.post("/api/fortschritt", json={"aufgabe": 99, "niveau": "A"}).status_code == 400
    assert student.post("/api/fortschritt", json={"aufgabe": NR[1], "niveau": "X"}).status_code == 400
    status = student.get("/api/status").get_json()
    assert {e["nr"] for e in status["erledigt"]} == {str(NR[0]), "T", "L1"}
    sid = session_werte(student)["schueler_id"]
    info = appmodule.get_schueler_info(sid)
    assert info["aufgaben_erledigt"] == 3
    assert info["abschnitte"]["nutztier"]["erledigt"] == 2
    assert info["abschnitte"]["abschluss"]["erledigt"] == 1
    assert info["abschnitte"]["abschluss"]["gesamt"] == len(ABSCHNITTE[-1]["aufgaben"])


def test_antwort_protokoll_mit_frage(student):
    r1 = student.post("/api/antwort", json={"aufgabe": NR[2], "niveau": "A", "typ": "zuordnung", "frage": "Was passt zusammen?", "antwort": "✅ Rind → Milch", "korrekt": True}).get_json()
    r2 = student.post("/api/antwort", json={"aufgabe": NR[2], "niveau": "A", "typ": "zuordnung", "antwort": "❌ falsch", "korrekt": False}).get_json()
    assert r1["versuch"] == 1 and r2["versuch"] == 2 and r2["gesamt"] == 2
    assert student.post("/api/antwort", json={"aufgabe": NR[2], "niveau": "A", "typ": "unbekannt", "antwort": "x"}).status_code == 400
    rows = dbmod.get_db().execute("SELECT korrekt, versuch_nr, frage FROM antworten ORDER BY id").fetchall()
    assert [(r["korrekt"], r["versuch_nr"]) for r in rows] == [(1, 1), (0, 2)]
    assert rows[0]["frage"] == "Was passt zusammen?"


def test_teacher_pages_and_auth(student, teacher, client):
    assert client.get("/api/lehrer/state").status_code == 401
    assert client.get("/lehrer").status_code == 302
    with appmodule.app.test_client() as anon:
        assert "Falsches Passwort" in anon.post("/lehrer/login", data={"passwort": "nope"}).get_data(as_text=True)
    student.post("/api/fortschritt", json={"aufgabe": NR[9], "niveau": "C"})
    dash = teacher.get("/lehrer").get_data(as_text=True)
    assert "student-table" in dash
    sid = session_werte(student)["schueler_id"]
    detail = teacher.get(f"/lehrer/schueler/{sid}").get_data(as_text=True)
    assert "Silberfuchs" in detail and f'id="tile-{NR[9]}"' in detail and "niv-C" in detail
    assert teacher.get("/lehrer/schueler/unbekannt").status_code == 302
    state = teacher.get("/api/lehrer/state").get_json()
    assert state["ok"] and {k for k in state} >= {"schueler", "anfragen", "budget", "gesperrt", "gruppenfreigabe", "snapshots", "fortsetzung", "iserv"}


def test_daten_loeschen_und_reset(student, teacher):
    sid = session_werte(student)["schueler_id"]
    student.post("/api/fortschritt", json={"aufgabe": NR[0], "niveau": "A"})
    assert teacher.post("/api/lehrer/daten-loeschen", json={"schueler_id": sid}).get_json()["ok"]
    db = dbmod.get_db()
    for table in ("schueler", "fortschritt"):
        assert db.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"] == 0
    assert student.get("/api/status").status_code == 401
    anmelden(appmodule.app.test_client(), "Zweiter", "9b")
    assert teacher.post("/api/lehrer/sitzung-zuruecksetzen").get_json()["geloescht"] == 1


def test_kein_loeschen_beim_start(student):
    """Ein Neustart (init_db) darf die laufende Sitzung nicht löschen (Standard §6)."""
    student.post("/api/fortschritt", json={"aufgabe": NR[0], "niveau": "A"})
    dbmod.init_db()
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM schueler").fetchone()["n"] == 1
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM fortschritt").fetchone()["n"] == 1


def test_lehrer_login_ohne_passwortkonfiguration(monkeypatch, client):
    monkeypatch.setattr(appmodule, "LEHRER_PASSWORD", "")
    resp = client.post("/lehrer/login", data={"passwort": "irgendwas"})
    assert "nicht gesetzt" in resp.get_data(as_text=True)


def _ids(html: str) -> list[str]:
    return re.findall(r'\sid="([^"]+)"', html)


def test_keine_doppelten_html_ids(student, teacher):
    """Standard §23.1: keine doppelten HTML-IDs in gerenderten Seiten."""
    sid = session_werte(student)["schueler_id"]
    seiten = {
        "login": appmodule.app.test_client().get("/login"),
        "arbeitsblatt": student.get("/arbeitsblatt"),
        "warten": student.get("/warten"),
        "lehrer_login": appmodule.app.test_client().get("/lehrer/login"),
        "dashboard": teacher.get("/lehrer"),
        "detail": teacher.get(f"/lehrer/schueler/{sid}"),
    }
    for name, resp in seiten.items():
        assert resp.status_code == 200, name
        ids = _ids(resp.get_data(as_text=True))
        doppelt = {i for i in ids if ids.count(i) > 1}
        assert not doppelt, f"{name}: doppelte IDs {doppelt}"
