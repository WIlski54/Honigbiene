"""Prüfmodus der Lehrkraft: alles sichtbar, Lösungen nur für die Lehrkraft, nichts für Lernende geändert."""
import inhalte_server


def test_pruefmodus_nur_fuer_lehrkraft(client):
    r = client.get("/lehrer/pruefen")
    assert r.status_code == 302 and "/lehrer/login" in r.headers["Location"]
    assert client.get("/api/lehrer/pruefen/lesestrecken").status_code == 401


def test_pruefmodus_seite_und_lesestrecken_mit_loesung(teacher, teacher_token):
    r = teacher.get("/lehrer/pruefen")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "pruefmodus" in html and "Prüfmodus" in html and "pruefen.js" in html
    assert "autosave-status" not in html and "Abmelden" not in html   # keine Schüler-Kopfzeile
    assert "Zum Dashboard" in html

    d = teacher.get("/api/lehrer/pruefen/lesestrecken", headers={"X-Lehrer-Token": teacher_token}).get_json()
    assert d["ok"] and set(d["lesestrecken"]) == set(inhalte_server.LESESTRECKEN)
    for strecke in d["lesestrecken"].values():
        assert strecke["anzahl"] == len(strecke["abschnitte"]) > 0
        for a in strecke["abschnitte"]:
            assert 0 <= a["loesung"] < len(a["optionen"])
            assert a["erklaerung"] and a["bild"] and a["frage"]


def test_glossar_auch_fuer_lehrkraft(client, teacher_token):
    assert client.get("/api/glossar").status_code == 401
    r = client.get("/api/glossar", headers={"X-Lehrer-Token": teacher_token})
    assert r.status_code == 200 and r.get_json()["ok"]


def test_schueler_sehen_weiter_keine_loesung(student):
    d = student.get("/api/lesestrecke/nutztier").get_json()
    assert d["ok"] and all("loesung" not in a for a in d["abschnitte"])
    assert student.get("/lehrer/pruefen").status_code == 302


def test_schaubilder_lassen_sich_vergroessern(student):
    html = student.get("/arbeitsblatt").get_data(as_text=True)
    assert 'id="bild-dialog"' in html and "bild.js" in html
    assert 'data-action="bild-open"' in html   # Glossar-Schaubild ist antippbar
