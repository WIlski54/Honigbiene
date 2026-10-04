import app as appmodule
import db as dbmod
import presence
from conftest import NR, anmelden, session_werte

CANVAS = {"version": "5.1.0", "objects": [{"type": "rect"}, {"type": "path"}]}
PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


def test_zeichnung_api(student):
    sid = session_werte(student)["schueler_id"]
    assert student.post("/api/zeichnung", json={"geraet": "fremd", "canvas_json": CANVAS}).status_code == 400
    assert student.post("/api/zeichnung", json={"geraet": "biene", "canvas_json": "x"}).status_code == 400
    r = student.post("/api/zeichnung", json={"geraet": "biene", "canvas_json": CANVAS, "preview": PNG}).get_json()
    assert r["ok"] and r["objekte"] == 2
    # Update ohne Vorschau behält die alte Vorschau
    student.post("/api/zeichnung", json={"geraet": "biene", "canvas_json": {"objects": []}, "preview": ""})
    alle = student.get("/api/zeichnungen").get_json()["zeichnungen"]
    assert alle["biene"]["preview"] == PNG and alle["biene"]["json"]["objects"] == []
    assert appmodule.get_schueler_info(sid)["zeichnungen"] == 1


def test_snapshot_speichern_laden_loeschen(student, teacher):
    sid_a = session_werte(student)["schueler_id"]
    student.post("/api/fortschritt", json={"aufgabe": NR[0], "niveau": "A"})
    student.post("/api/zeichnung", json={"geraet": "biene", "canvas_json": CANVAS, "preview": PNG})
    r = teacher.post("/api/lehrer/snapshots", json={"name": "Stunde 1"}).get_json()
    assert r["ok"] and r["snapshot"]["lernende"] == 1
    snap_id = r["snapshot"]["id"]
    assert [s["name"] for s in teacher.get("/api/lehrer/snapshots").get_json()["snapshots"]] == ["Stunde 1"]

    teacher.post("/api/lehrer/daten-loeschen", json={"schueler_id": sid_a})
    b = anmelden(appmodule.app.test_client(), "Zweiter", "9b")
    sid_b = session_werte(b)["schueler_id"]
    presence.add(sid_b, "sock-b")
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM schueler").fetchone()["n"] == 1

    assert teacher.post("/api/lehrer/snapshots/unbekannt/laden").status_code == 404
    r = teacher.post(f"/api/lehrer/snapshots/{snap_id}/laden").get_json()
    assert r["ok"] and r["lernende"] == 1
    ids = {row["id"] for row in dbmod.get_db().execute("SELECT id FROM schueler").fetchall()}
    assert ids == {sid_a}
    assert not presence.is_online(sid_b)  # alte Sockets sind invalidiert
    assert b.get("/api/status").status_code == 401
    z = dbmod.get_db().execute("SELECT canvas_json, preview_data FROM zeichnungen WHERE schueler_id=?", (sid_a,)).fetchone()
    assert z["preview_data"] == PNG and '"rect"' in z["canvas_json"]
    assert appmodule.fortsetzung_status()["active"] is True  # Laden = Fortsetzung mit Token-Hashes

    assert teacher.delete(f"/api/lehrer/snapshots/{snap_id}").get_json()["ok"]
    assert teacher.delete(f"/api/lehrer/snapshots/{snap_id}").status_code == 404
    assert teacher.get("/api/lehrer/snapshots").get_json()["snapshots"] == []


def test_reset_raeumt_praesenz_und_snapshots_bleiben(student, teacher):
    sid = session_werte(student)["schueler_id"]
    presence.add(sid, "sock-1")
    teacher.post("/api/lehrer/snapshots", json={"name": "vorher"})
    assert teacher.post("/api/lehrer/sitzung-zuruecksetzen").get_json()["geloescht"] == 1
    assert presence.online_ids() == []
    assert len(dbmod.list_named_snapshots()) == 1  # Reset löscht keine Zwischenstände
