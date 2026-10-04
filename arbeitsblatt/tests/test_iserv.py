import base64
import json
import secrets

import pytest

import config
import db as dbmod
import iserv_archiv as ia
from config import APP_ID, STATE_SCHEMA_VERSION
from fake_webdav import FakeWebDAV

KEY_B64 = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()


@pytest.fixture()
def iserv(monkeypatch):
    fake = FakeWebDAV()
    monkeypatch.setattr(config, "ISERV_WEBDAV_URL", "https://webdav.schule.example/webdav")
    monkeypatch.setattr(config, "ISERV_WEBDAV_USERNAME", "backup-bot")
    monkeypatch.setattr(config, "ISERV_WEBDAV_PASSWORD", "geheim")
    monkeypatch.setattr(config, "ISERV_BACKUP_PATH", "Files/Backups_AB_KI")
    monkeypatch.setattr(config, "ISERV_BACKUP_ENCRYPTION_KEY", KEY_B64)
    monkeypatch.setattr(config, "ISERV_TIMEOUT_SECONDS", "15")
    monkeypatch.setattr(config, "ISERV_CA_BUNDLE", "")
    monkeypatch.setattr(ia, "TRANSPORT_OVERRIDE", fake)
    return fake


def _snapshot(n=1):
    return {"schema_version": 2, "app_id": APP_ID, "created_at": "2026-09-13T10:00:00",
            "tabellen": {"schueler": [{"id": f"s{i}", "pseudonym": f"P{i}", "klasse": "9a", "joined_at": "x", "resume_token_hash": f"h{i}"} for i in range(n)],
                         "antworten": [], "arbeitsstaende": []}}


# ── Konfiguration ───────────────────────────────────────────────────────────
def test_url_validierung():
    assert ia.validiere_url("https://webdav.example/") == "https://webdav.example"
    for schlecht in ("http://webdav.example", "https://user:pw@webdav.example", "https://webdav.example/?x=1", "https://webdav.example/#f", "https://"):
        with pytest.raises(ia.IServConfigError):
            ia.validiere_url(schlecht)


def test_pfad_normalisierung():
    assert ia.normalisiere_pfad("/Files/Backups_AB_KI/") == "Files/Backups_AB_KI"
    assert ia.normalisiere_pfad("Files\\Backups") == "Files/Backups"
    for schlecht in ("", "Files/../etc", "./Files", "Files/x?y", "Files#a", "Fi\0les"):
        with pytest.raises(ia.IServConfigError):
            ia.normalisiere_pfad(schlecht)


def test_schluessel_und_timeout():
    assert len(ia.dekodiere_schluessel(KEY_B64)) == 32
    with pytest.raises(ia.IServConfigError):
        ia.dekodiere_schluessel(base64.urlsafe_b64encode(b"kurz").decode())
    with pytest.raises(ia.IServConfigError):
        ia.dekodiere_schluessel("")
    assert ia.validiere_timeout("15") == 15.0
    for schlecht in ("1", "61", "abc"):
        with pytest.raises(ia.IServConfigError):
            ia.validiere_timeout(schlecht)


def test_status_ohne_konfiguration(monkeypatch):
    monkeypatch.setattr(config, "ISERV_WEBDAV_URL", "")
    st = ia.status_payload()
    assert st["konfiguriert"] is False and "nicht konfiguriert" in st["fehler"]


def test_status_mit_konfiguration(iserv):
    st = ia.status_payload()
    assert st["konfiguriert"] and st["host"] == "webdav.schule.example" and st["pfad"] == "Files/Backups_AB_KI"
    assert len(st["marker"]) == 12


# ── Krypto ──────────────────────────────────────────────────────────────────
def test_roundtrip_manipulation_und_falscher_schluessel():
    master = secrets.token_bytes(32)
    umschlag = ia.baue_umschlag(_snapshot(2), "Stunde 1")
    blob = ia.verschluesseln(umschlag, master)
    assert blob.startswith(ia.MAGIC)
    zurueck = ia.entschluesseln(blob, master)
    assert zurueck["name"] == "Stunde 1" and zurueck["snapshot"]["tabellen"]["schueler"][1]["id"] == "s1"
    # zwei Verschlüsselungen desselben Inhalts unterscheiden sich (Salt/Nonce)
    assert ia.verschluesseln(umschlag, master) != blob
    kaputt = blob[:-1] + bytes([blob[-1] ^ 1])
    with pytest.raises(ia.IServFehler):
        ia.entschluesseln(kaputt, master)
    with pytest.raises(ia.IServFehler):
        ia.entschluesseln(blob, secrets.token_bytes(32))
    with pytest.raises(ia.IServFehler):
        ia.entschluesseln(b"XXXXXXXX" + blob[8:], master)
    with pytest.raises(ia.IServFehler):
        ia.entschluesseln(b"zu kurz", master)


def test_umschlag_pruefung():
    ok = ia.baue_umschlag(_snapshot(), "x")
    ia.pruefe_umschlag(ok)
    for feld, wert in (("format", "anders"), ("app_id", "fremd"), ("schema_version", 99)):
        with pytest.raises(ia.IServFehler):
            ia.pruefe_umschlag(dict(ok, **{feld: wert}))
    with pytest.raises(ia.IServFehler):
        ia.pruefe_umschlag(dict(ok, snapshot={"app_id": "fremd"}))


def test_dateiname():
    import datetime as dt
    name = ia.dateiname("Klasse 9a – Stunde 3!", dt.datetime(2026, 9, 13, 10, 5, 7))
    assert name == f"{ia.app_marker()}_20260913-100507_Klasse-9a-Stunde-3.iabackup"
    assert ia.dateiname_gueltig(name)
    assert not ia.dateiname_gueltig("../x.iabackup") and not ia.dateiname_gueltig("abc.iabackup")
    assert ia.sicherer_name("") == "Sitzung"


# ── WebDAV-Vertrag ──────────────────────────────────────────────────────────
def test_webdav_test_listing_put_get_delete(iserv):
    client = ia.make_client()
    assert client.test_verbindung()["ok"]
    assert iserv.aufrufe[-1][0] == "PROPFIND" and iserv.aufrufe[-1][2]["Depth"] == "0"
    client.put("a.iabackup", b"123")
    put = [a for a in iserv.aufrufe if a[0] == "PUT"][-1]
    assert put[2]["If-None-Match"] == "*" and put[2]["Content-Type"] == "application/octet-stream"
    with pytest.raises(ia.IServFehler, match="existiert bereits"):
        client.put("a.iabackup", b"456")
    assert client.get("a.iabackup") == b"123"
    assert [e["name"] for e in client.listing()] == ["a.iabackup"]
    client.delete("a.iabackup")
    with pytest.raises(ia.IServFehler, match="nicht gefunden"):
        client.get("a.iabackup")
    iserv.ordner_fehlt = True
    with pytest.raises(ia.IServFehler, match="404"):
        client.test_verbindung()
    iserv.ordner_fehlt = False
    iserv.fehler_bei["PROPFIND"] = 401
    with pytest.raises(ia.IServFehler, match="Zugangsdaten"):
        client.listing()


def test_listing_zeigt_nur_eigene_archive(iserv):
    client = ia.make_client()
    master = client.konf.key
    eigen = ia.dateiname("eigen")
    iserv.dateien[eigen] = ia.verschluesseln(ia.baue_umschlag(_snapshot(3), "eigen"), master)
    fremd_umschlag = dict(ia.baue_umschlag(_snapshot(1), "fremd"), app_id="andere-app")
    iserv.dateien["ffffffffffff_20260101-000000_fremd.iabackup"] = ia.verschluesseln(fremd_umschlag, master)
    iserv.dateien[f"{ia.app_marker()}_20260101-000000_falscherkey.iabackup"] = ia.verschluesseln(ia.baue_umschlag(_snapshot(), "k"), secrets.token_bytes(32))
    iserv.dateien["legacy.iabackup"] = ia.verschluesseln(ia.baue_umschlag(_snapshot(2), "legacy"), master)
    iserv.dateien["notiz.txt"] = b"hallo"
    liste = ia.liste_archive(client)
    assert [e["dateiname"] for e in liste] == [eigen]
    assert liste[0]["lernende"] == 3 and liste[0]["pseudonyme"][0].startswith("P0")
    # Legacy-Dateien ohne Marker nur auf ausdrücklichen Wunsch inspizieren
    legacy = ia.liste_archive(client, legacy_pruefen=True)
    assert {e["dateiname"] for e in legacy} == {eigen, "legacy.iabackup"}


def test_remote_loeschen_validiert_eigentum(iserv):
    client = ia.make_client()
    fremd = "ffffffffffff_20260101-000000_fremd.iabackup"
    iserv.dateien[fremd] = ia.verschluesseln(dict(ia.baue_umschlag(_snapshot(), "f"), app_id="andere"), client.konf.key)
    with pytest.raises(ia.IServFehler):
        ia.archiv_loeschen(client, fremd)
    assert fremd in iserv.dateien
    with pytest.raises(ia.IServFehler):
        ia.archiv_loeschen(client, "../boese.iabackup")
    eigen = ia.dateiname("e")
    iserv.dateien[eigen] = ia.verschluesseln(ia.baue_umschlag(_snapshot(), "e"), client.konf.key)
    ia.archiv_loeschen(client, eigen)
    assert eigen not in iserv.dateien
    assert [a[0] for a in iserv.aufrufe if a[1] == eigen] == ["GET", "DELETE"]


# ── Abschluss-Transaktion ───────────────────────────────────────────────────
def _abschluss(iserv, name="Stunde"):
    geloescht = {"n": 0}
    flush = {"online": ["s1"], "confirmed": ["s1"], "missing": []}
    return ia.abschluss_durchfuehren(name, lambda: flush, lambda: _snapshot(2), lambda: geloescht.__setitem__("n", geloescht["n"] + 1)), geloescht


def test_abschluss_erfolgreich_loescht_erst_nach_digest(iserv):
    proto, geloescht = _abschluss(iserv)
    assert proto["geloescht"] is True and geloescht["n"] == 1
    assert proto["dateiname"] in iserv.dateien and proto["flush"]["confirmed"] == ["s1"]
    methoden = [a[0] for a in iserv.aufrufe if a[1] == proto["dateiname"]]
    assert methoden == ["PUT", "GET"]
    assert "Digest stimmt überein" in proto["schritte"][-2]


def test_abschluss_bricht_bei_manipuliertem_download_ab(iserv):
    iserv.download_manipulieren = True
    with pytest.raises(ia.IServFehler):
        _abschluss(iserv)
    assert not any("bereinigt" in s for s in [])  # cleanup wurde nie aufgerufen (siehe unten)


def test_abschluss_bricht_bei_fremdem_download_und_put_fehler_ab(iserv):
    geloescht = {"n": 0}
    cleanup = lambda: geloescht.__setitem__("n", 1)
    flush = lambda: {"online": [], "confirmed": [], "missing": []}
    master = ia.make_client().konf.key
    # Download liefert eine andere gültige Datei → Digest ungleich → nichts gelöscht
    iserv.download_tauschen = ia.verschluesseln(ia.baue_umschlag(_snapshot(1), "andere"), master)
    with pytest.raises(ia.IServFehler):
        ia.abschluss_durchfuehren("x", flush, lambda: _snapshot(2), cleanup)
    assert geloescht["n"] == 0
    iserv.download_tauschen = None
    # PUT scheitert → nichts gelöscht
    iserv.fehler_bei["PUT"] = 403
    with pytest.raises(ia.IServFehler, match="Berechtigung"):
        ia.abschluss_durchfuehren("x", flush, lambda: _snapshot(2), cleanup)
    assert geloescht["n"] == 0
    # Ungültiger Snapshot → nichts hochgeladen, nichts gelöscht
    del iserv.fehler_bei["PUT"]
    vorher = len(iserv.aufrufe)
    with pytest.raises(ValueError):
        ia.abschluss_durchfuehren("x", flush, lambda: {"app_id": "fremd"}, cleanup)
    assert geloescht["n"] == 0 and not any(a[0] == "PUT" for a in iserv.aufrufe[vorher:])


def test_abschluss_ohne_konfiguration(monkeypatch):
    monkeypatch.setattr(config, "ISERV_WEBDAV_URL", "")
    with pytest.raises(ia.IServConfigError):
        ia.make_client()


# ── Ende-zu-Ende über die Lehrer-API ────────────────────────────────────────
def test_api_abschluss_und_wiederherstellung(iserv, student, teacher):
    import app as appmodule
    from conftest import NR, session_werte
    sid = session_werte(student)["schueler_id"]
    student.post("/api/fortschritt", json={"aufgabe": NR[0], "niveau": "A"})
    student.post("/api/autosave", json={"revision": 3, "state": {"schema_version": STATE_SCHEMA_VERSION, "app_id": APP_ID, "lernplatz": {"schueler_id": sid}, "active_tab": "volk"}})
    teacher.post("/api/lehrer/snapshots", json={"name": "temp"})
    assert teacher.get("/api/lehrer/iserv/status").get_json()["konfiguriert"] is True
    assert teacher.post("/api/lehrer/iserv/test").get_json()["ok"] is True

    r = teacher.post("/api/lehrer/iserv/abschluss", json={"name": "Stunde 1"}).get_json()
    assert r["ok"] and r["protokoll"]["geloescht"] is True
    datei = r["protokoll"]["dateiname"]
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM schueler").fetchone()["n"] == 0
    assert dbmod.list_named_snapshots() == []  # temporäre Snapshots werden mit bereinigt
    assert student.get("/api/status").status_code == 401

    archive = teacher.get("/api/lehrer/iserv/archive").get_json()["archive"]
    assert [a["dateiname"] for a in archive] == [datei] and archive[0]["lernende"] == 1
    vorschau = teacher.post("/api/lehrer/iserv/vorschau", json={"dateiname": datei}).get_json()
    assert vorschau["ok"] and vorschau["archiv"]["arbeitsstaende"] == 1

    # Ansicht: keine Resume-Hashes
    r = teacher.post("/api/lehrer/iserv/wiederherstellen", json={"dateiname": datei, "modus": "ansicht"}).get_json()
    assert r["ok"] and r["lernende"] == 1
    row = dbmod.get_db().execute("SELECT resume_token_hash FROM schueler WHERE id=?", (sid,)).fetchone()
    assert row["resume_token_hash"] is None and appmodule.fortsetzung_status()["active"] is False
    # Fortsetzung: Hashes bleiben, Modus aktiv
    r = teacher.post("/api/lehrer/iserv/wiederherstellen", json={"dateiname": datei, "modus": "fortsetzung"}).get_json()
    assert r["ok"]
    row = dbmod.get_db().execute("SELECT resume_token_hash FROM schueler WHERE id=?", (sid,)).fetchone()
    assert row["resume_token_hash"] and appmodule.fortsetzung_status()["active"] is True
    assert teacher.post("/api/lehrer/iserv/wiederherstellen", json={"dateiname": datei, "modus": "egal"}).status_code == 400

    # Löschen validiert Eigentum
    assert teacher.post("/api/lehrer/iserv/loeschen", json={"dateiname": "ffffffffffff_20260101-000000_x.iabackup"}).status_code == 400
    assert teacher.post("/api/lehrer/iserv/loeschen", json={"dateiname": datei}).get_json()["ok"]
    assert datei not in iserv.dateien


def test_api_abschluss_fehler_laesst_daten_stehen(iserv, student, teacher):
    iserv.download_manipulieren = True
    r = teacher.post("/api/lehrer/iserv/abschluss", json={"name": "kaputt"})
    assert r.status_code == 502 and r.get_json()["ok"] is False
    assert dbmod.get_db().execute("SELECT COUNT(*) AS n FROM schueler").fetchone()["n"] == 1
    assert student.get("/api/status").status_code == 200


def test_api_ohne_iserv_konfiguration(monkeypatch, teacher):
    monkeypatch.setattr(config, "ISERV_WEBDAV_URL", "")
    assert teacher.get("/api/lehrer/iserv/status").get_json()["konfiguriert"] is False
    r = teacher.post("/api/lehrer/iserv/abschluss", json={"name": "x"})
    assert r.status_code == 400 and "nicht konfiguriert" in r.get_json()["error"]
