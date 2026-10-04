import app as appmodule
import db as dbmod
from conftest import anmelden, session_werte


def test_login_erzeugt_resume_token_und_hash(student):
    s = session_werte(student)
    token, sid = s["resume_token"], s["schueler_id"]
    assert len(token) >= 40
    row = dbmod.get_db().execute("SELECT resume_token_hash FROM schueler WHERE id=?", (sid,)).fetchone()
    assert row["resume_token_hash"] == appmodule.token_hash(token)
    assert token not in row["resume_token_hash"]  # nur der Hash liegt auf dem Server


def test_resume_verbindet_denselben_lernplatz(student):
    s = session_werte(student)
    neu = appmodule.app.test_client()
    assert neu.get("/api/status").status_code == 401
    resp = neu.post("/api/resume", json={"schueler_id": s["schueler_id"], "token": s["resume_token"]})
    assert resp.status_code == 200 and resp.get_json()["pseudonym"] == "Silberfuchs"
    assert neu.get("/api/status").status_code == 200
    assert session_werte(neu)["schueler_id"] == s["schueler_id"]


def test_resume_mit_falschem_token_scheitert(student):
    s = session_werte(student)
    neu = appmodule.app.test_client()
    assert neu.post("/api/resume", json={"schueler_id": s["schueler_id"], "token": "falsch" * 8}).status_code == 403
    assert neu.post("/api/resume", json={"schueler_id": "gibtesnicht", "token": s["resume_token"]}).status_code == 404
    assert neu.post("/api/resume", json={}).status_code == 400
    assert neu.get("/api/status").status_code == 401


def test_logout_loescht_hash_und_token(student):
    s = session_werte(student)
    student.post("/logout")
    row = dbmod.get_db().execute("SELECT resume_token_hash FROM schueler WHERE id=?", (s["schueler_id"],)).fetchone()
    assert row["resume_token_hash"] is None
    assert "resume_token" not in session_werte(student)
    neu = appmodule.app.test_client()
    assert neu.post("/api/resume", json={"schueler_id": s["schueler_id"], "token": s["resume_token"]}).status_code == 403


def test_lehrer_header_token_ohne_session(teacher_token, client):
    assert client.get("/api/lehrer/state").status_code == 401
    assert client.get("/api/lehrer/state", headers={"X-Lehrer-Token": teacher_token}).status_code == 200
    assert client.get("/api/lehrer/state", headers={"X-Lehrer-Token": "kaputt"}).status_code == 401


def test_schueler_login_im_selben_profil_loescht_lehrer_nicht(teacher):
    """Lehrkraft und Lernende testweise im selben Browserprofil (Standard §12)."""
    anmelden(teacher, "Testkind", "6a")
    assert teacher.get("/api/status").status_code == 200
    assert teacher.get("/api/lehrer/state").status_code == 200
    teacher.post("/logout")
    assert teacher.get("/api/lehrer/state").status_code == 200


def test_lehrer_logout_entwertet_token(teacher, teacher_token, client):
    teacher.post("/lehrer/logout")
    assert client.get("/api/lehrer/state", headers={"X-Lehrer-Token": teacher_token}).status_code == 401
    assert teacher.get("/lehrer").status_code == 302
