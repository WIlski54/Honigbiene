import datetime as dt

import db as dbmod
import ki
from conftest import anmelden, session_werte

PNG = "data:image/png;base64," + "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" * 3


def test_einzelfreigabe_flow(student, teacher):
    assert student.post("/api/chat", json={"message": "Was ist der Blankoscheck?"}).get_json()["blocked"] is True
    anfrage = student.post("/api/ki-anfrage", json={"typ": "chat", "kontext": "Was ist der Blankoscheck?"}).get_json()
    assert anfrage["status"] == "wartend"
    aid = anfrage["anfrage_id"]
    state = teacher.get("/api/lehrer/state").get_json()
    assert [a["id"] for a in state["anfragen"]] == [aid]
    assert teacher.post("/api/ki-entscheidung", json={"anfrage_id": aid, "entscheid": "freigegeben"}).get_json()["ok"]
    chat = student.post("/api/chat", json={"message": "Was ist der Blankoscheck?", "anfrage_id": aid}).get_json()
    assert "nicht konfiguriert" in chat["response"]
    # Chat-Freigabe gilt nicht für Korrektur oder Zeichnung
    assert student.post("/api/check-answer", json={"anfrage_id": aid, "answer": "x" * 30}).get_json()["blocked"] is True
    assert student.post("/api/zeichnung-analyse", json={"anfrage_id": aid, "png": PNG}).get_json()["blocked"] is True
    assert student.post("/api/handschrift", json={"anfrage_id": aid, "png": PNG}).get_json()["blocked"] is True
    korr = student.post("/api/ki-anfrage", json={"typ": "korrektur", "kontext": "Aufgabe 7"}).get_json()
    teacher.post("/api/ki-entscheidung", json={"anfrage_id": korr["anfrage_id"], "entscheid": "freigegeben"})
    fb = student.post("/api/check-answer", json={"anfrage_id": korr["anfrage_id"], "question": "Q", "answer": "Eine ausführliche Antwort zur Biozönose."}).get_json()
    assert fb["correct"] is None and "gespeichert" in fb["feedback"]
    assert student.post("/api/ki-anfrage", json={"typ": "unsinn"}).status_code == 400
    # Blockierte Anfragen erzeugen keine Antwortprotokolle
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM antworten").fetchone()["n"] == 0


def test_einzelsperre_ist_persistent(student, teacher):
    sid = session_werte(student)["schueler_id"]
    pending = student.post("/api/ki-anfrage", json={"typ": "chat"}).get_json()["anfrage_id"]
    assert teacher.post("/api/lehrer/ki-sperren", json={"schueler_id": sid, "aktion": "sperren"}).get_json()["gesperrt"] is True
    assert student.post("/api/ki-anfrage", json={"typ": "chat"}).get_json()["status"] == "gesperrt"
    assert dbmod.get_db().execute("SELECT status FROM ki_anfragen WHERE id=?", (pending,)).fetchone()["status"] == "abgelehnt"
    assert student.get("/api/status").get_json()["ki_gesperrt"] is True
    dbmod.init_db()  # Prozessneustart simulieren – die Sperre bleibt
    assert ki.ist_gesperrt(sid) and sid in ki.gesperrte_ids()
    assert teacher.post("/api/lehrer/ki-sperren", json={"schueler_id": sid, "aktion": "freigeben"}).get_json()["gesperrt"] is False


def test_gruppenfreigabe_pruefreihenfolge(student, teacher):
    sid = session_werte(student)["schueler_id"]
    # Start: Chat für Klasse 9a, 30 Minuten, Gruppenbudget 1000, persönlich 300
    r = teacher.post("/api/lehrer/gruppenfreigabe", json={"aktion": "start", "typen": ["chat", "handschrift"], "klasse": "6a", "minuten": 30, "token_limit": 1000, "per_student_limit": 300}).get_json()
    assert r["ok"] and r["gruppenfreigabe"]["active"] and r["gruppenfreigabe"]["typen"] == ["chat", "handschrift"]
    assert ki.ki_pruefen(sid, "6a", "chat")["quelle"] == "gruppe"
    assert ki.ki_pruefen(sid, "6a", "korrektur")["ok"] is False          # Typ nicht erlaubt
    assert ki.ki_pruefen(sid, "9b", "chat")["ok"] is False               # falsche Klasse
    assert student.post("/api/ki-anfrage", json={"typ": "chat"}).get_json()["status"] == "freigegeben"
    assert student.post("/api/ki-anfrage", json={"typ": "korrektur"}).get_json()["status"] == "wartend"
    # Persönliches Budget
    ki.tokens_buchen(sid, 300, "gruppe")
    assert ki.ki_pruefen(sid, "6a", "chat")["ok"] is False
    assert ki.gruppenfreigabe_lesen()["tokens_used"] == 300
    # Gruppenbudget erschöpft → Freigabe endet
    ki.tokens_buchen("anderer", 700, "gruppe")
    g = ki.gruppenfreigabe_lesen()
    assert g["active"] is False and g.get("budget_erschoepft")
    # Zeitablauf
    teacher.post("/api/lehrer/gruppenfreigabe", json={"aktion": "start", "typen": ["chat"], "klasse": "", "minuten": 5})
    with dbmod.get_db() as db:
        db.execute("UPDATE ki_gruppenfreigabe SET expires_at=?", ((dt.datetime.now() - dt.timedelta(minutes=1)).isoformat(timespec="seconds"),))
        db.commit()
    assert ki.ki_pruefen(sid, "6a", "chat")["ok"] is False
    # Stop
    assert teacher.post("/api/lehrer/gruppenfreigabe", json={"aktion": "stop"}).get_json()["gruppenfreigabe"]["active"] is False
    assert teacher.post("/api/lehrer/gruppenfreigabe", json={"aktion": "quatsch"}).status_code == 400


def test_gruppensperre_wirkt_sofort_und_ueberlebt_neustart(student, teacher):
    sid = session_werte(student)["schueler_id"]
    pending = student.post("/api/ki-anfrage", json={"typ": "chat"}).get_json()["anfrage_id"]
    teacher.post("/api/ki-entscheidung", json={"anfrage_id": pending, "entscheid": "freigegeben"})
    assert ki.ki_pruefen(sid, "6a", "chat", pending)["ok"] is True
    teacher.post("/api/lehrer/gruppenfreigabe", json={"aktion": "sperren"})
    assert ki.ki_pruefen(sid, "6a", "chat", pending)["ok"] is False
    assert "gesperrt" in student.post("/api/chat", json={"message": "x", "anfrage_id": pending}).get_json()["message"]
    assert student.post("/api/ki-anfrage", json={"typ": "chat"}).get_json()["status"] == "gesperrt"
    dbmod.init_db()
    assert ki.gruppenfreigabe_lesen()["locked"] is True
    # Sperre vor Budget in der Reihenfolge
    ki.add_tokens(10 ** 6)
    assert "gesperrt" in ki.ki_pruefen(sid, "6a", "chat", pending)["grund"]
    teacher.post("/api/lehrer/gruppenfreigabe", json={"aktion": "entsperren"})
    assert "Budget" in ki.ki_pruefen(sid, "6a", "chat", pending)["grund"]


def test_chatverlauf_wird_gespeichert(student):
    sid = session_werte(student)["schueler_id"]
    ki.chat_speichern(sid, "chat", "Frage?", "Antwort.", 12)
    ki.chat_speichern(sid, "korrektur", "Text", "Feedback", 30)
    verlauf = ki.chat_verlauf(sid)
    assert [v["typ"] for v in verlauf] == ["chat", "korrektur"]
    snap = dbmod.build_snapshot()
    assert len(snap["tabellen"]["chat_messages"]) == 2


def test_parse_hilfsfunktionen():
    assert ki.parse_json_response('```json\n{"correct": true, "feedback": "Gut", "hint": "T"}\n```') == {"correct": True, "feedback": "Gut", "hint": "T"}
    assert ki.parse_json_response("kein json")["correct"] is None
    z = ki.parse_zeichnung_response('{"sterne": 2, "erkannt": ["Pfeil"], "fehlt": [], "feedback": "ok"}')
    assert z["sterne"] == 2 and z["erkannt"] == ["Pfeil"]
    assert ki.parse_zeichnung_response('{"sterne": 7}')["sterne"] is None
    assert ki.estimate_tokens("abcd" * 10) == 10
