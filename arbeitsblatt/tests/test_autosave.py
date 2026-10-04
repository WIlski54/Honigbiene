import json

import app as appmodule
import db as dbmod
import presence
from config import APP_ID, STATE_SCHEMA_VERSION
from conftest import session_werte


def zustand(sid, **extra):
    base = {
        "schema_version": STATE_SCHEMA_VERSION, "app_id": APP_ID, "exported_at": "2026-09-13T10:00:00",
        "lernplatz": {"schueler_id": sid, "pseudonym": "Silberfuchs", "klasse": "6a"},
        "active_tab": "nutztier", "completed": ["1"], "niveaus": {"1": "B"},
        "texte": {"nt-nutztier": "• Die Biene gibt Honig", "nq-nutztier": "Schulbuch S. 84"},
        "quellen": [], "aufgaben": {"1": {"typ": "mc", "gewaehlt": [0], "fertig": True}},
    }
    base.update(extra)
    return base


def test_hoehere_revision_gewinnt(student):
    sid = session_werte(student)["schueler_id"]
    assert student.get("/api/autosave").status_code == 204
    r1 = student.post("/api/autosave", json={"revision": 1, "state": zustand(sid)}).get_json()
    assert r1["ok"] and r1["accepted"] and r1["revision"] == 1
    r3 = student.post("/api/autosave", json={"revision": 3, "state": zustand(sid, active_tab="volk")}).get_json()
    assert r3["accepted"] and r3["revision"] == 3
    # Verspäteter Request mit niedrigerer Revision überschreibt nicht
    r2 = student.post("/api/autosave", json={"revision": 2, "state": zustand(sid, active_tab="koerper")}).get_json()
    assert r2["ok"] and r2["accepted"] is False and r2["revision"] == 3
    geladen = student.get("/api/autosave").get_json()
    assert geladen["revision"] == 3 and geladen["state"]["active_tab"] == "volk"


def test_validierung_lehnt_fremde_und_kaputte_zustaende_ab(student):
    sid = session_werte(student)["schueler_id"]
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand(sid, app_id="andere")}).status_code == 400
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand(sid, schema_version=99)}).status_code == 400
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand(sid, texte={"nt-nutztier": 5})}).status_code == 400
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand(sid, completed="1")}).status_code == 400
    assert student.post("/api/autosave", json={"revision": 1, "state": zustand("fremd")}).status_code == 400
    assert student.post("/api/autosave", json={"revision": "x", "state": zustand(sid)}).status_code == 400
    gross = zustand(sid, texte={"nt-nutztier": "x" * (2 * 1024 * 1024 + 10)})
    assert student.post("/api/autosave", json={"revision": 1, "state": gross}).status_code in (400, 413)
    assert student.get("/api/autosave").status_code == 204


def test_notizen_werden_gespiegelt_und_status_zeigt_autosave(student, teacher):
    sid = session_werte(student)["schueler_id"]
    student.post("/api/autosave", json={"revision": 1, "state": zustand(sid)})
    row = dbmod.get_db().execute("SELECT stichpunkte, quellen FROM notizen WHERE schueler_id=? AND abschnitt='nutztier'", (sid,)).fetchone()
    assert row["stichpunkte"] == "• Die Biene gibt Honig" and row["quellen"] == "Schulbuch S. 84"
    status = student.get("/api/status").get_json()
    assert status["autosave"]["revision"] == 1
    info = appmodule.get_schueler_info(sid)
    assert info["autosave_at"] and info["autosave_revision"] == 1
    detail = teacher.get(f"/lehrer/schueler/{sid}").get_data(as_text=True)
    assert "• Die Biene gibt Honig" in detail


def test_flush_protokoll(monkeypatch):
    presence.reset()
    assert appmodule.request_flush(timeout=0.05) == {"online": [], "confirmed": [], "missing": []}
    presence.add("s-off", "sock-1")
    proto = appmodule.request_flush(timeout=0.15)
    assert proto == {"online": ["s-off"], "confirmed": [], "missing": ["s-off"]}

    def sofort_ack(sid, event, data):
        assert event == "autosave_flush"
        with appmodule._flush_lock:
            appmodule._flush_acks[sid] = 9

    monkeypatch.setattr(appmodule, "emit_schueler", sofort_ack)
    proto = appmodule.request_flush(timeout=0.5)
    assert proto == {"online": ["s-off"], "confirmed": ["s-off"], "missing": []}
    presence.reset()
