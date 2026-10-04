import json
import os
import sqlite3

import db as dbmod
from config import APP_ID, DB_SCHEMA_VERSION


def _tabellen():
    with dbmod.get_db() as db:
        return {r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def test_init_db_legt_alle_tabellen_an():
    dbmod.init_db()
    erwartet = set(dbmod.SNAPSHOT_TABELLEN) | set(dbmod.SITZUNGS_HILFSTABELLEN) | {
        "gespeicherte_sitzungen", "lehrer_tokens", "schema_migrations",
    }
    assert erwartet <= _tabellen()
    assert dbmod.schema_version() == DB_SCHEMA_VERSION


def test_migration_ergaenzt_spalten_ohne_datenverlust(tmp_path, monkeypatch):
    alt = tmp_path / "alt.db"
    con = sqlite3.connect(alt)
    con.executescript(
        """
        CREATE TABLE schueler (id TEXT PRIMARY KEY, pseudonym TEXT NOT NULL, klasse TEXT NOT NULL, joined_at TEXT NOT NULL, last_active TEXT, socket_id TEXT);
        CREATE TABLE antworten (id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, aufgabe_nr TEXT NOT NULL, niveau TEXT NOT NULL, antwort_typ TEXT NOT NULL, antwort_text TEXT, korrekt INTEGER, versuch_nr INTEGER NOT NULL DEFAULT 1, erstellt_at TEXT NOT NULL);
        INSERT INTO schueler VALUES ('abc', 'Fuchs', '9a', '2026-09-01T08:00:00', '2026-09-01T08:30:00', 'socket-alt');
        INSERT INTO antworten (schueler_id, aufgabe_nr, niveau, antwort_typ, antwort_text, korrekt, erstellt_at) VALUES ('abc', '1', 'A', 'mc', 'x', 1, '2026-09-01T08:10:00');
        """
    )
    con.commit()
    con.close()
    monkeypatch.setattr(dbmod, "DB_PATH", str(alt))
    dbmod.init_db()
    with dbmod.get_db() as db:
        spalten = {r["name"] for r in db.execute("PRAGMA table_info(schueler)").fetchall()}
        assert "resume_token_hash" in spalten
        assert "frage" in {r["name"] for r in db.execute("PRAGMA table_info(antworten)").fetchall()}
        row = db.execute("SELECT * FROM schueler").fetchone()
        assert row["pseudonym"] == "Fuchs"
        assert row["socket_id"] is None  # alte Socket-IDs werden beim Start geleert
        assert db.execute("SELECT COUNT(*) AS n FROM antworten").fetchone()["n"] == 1
    # Zweiter Aufruf ist idempotent
    dbmod.init_db()


def test_daten_ueberleben_neuinitialisierung():
    dbmod.init_db()
    dbmod.clear_live_data()
    with dbmod.get_db() as db:
        db.execute("INSERT INTO schueler (id, pseudonym, klasse, joined_at) VALUES ('s1', 'Maus', '9', '2026-09-13T10:00:00')")
        db.commit()
    dbmod.init_db()
    with dbmod.get_db() as db:
        assert db.execute("SELECT COUNT(*) AS n FROM schueler").fetchone()["n"] == 1


def test_snapshot_roundtrip_mit_zeichnungen_und_modi():
    dbmod.init_db()
    dbmod.clear_live_data()
    with dbmod.get_db() as db:
        db.execute("INSERT INTO schueler (id, pseudonym, klasse, joined_at, resume_token_hash) VALUES ('s1', 'Maus', '9', '2026-09-13T10:00:00', 'hash1')")
        db.execute("INSERT INTO zeichnungen (schueler_id, geraet, canvas_json, preview_data, updated_at) VALUES ('s1', 'buendnis', '{\"objects\":[1]}', 'data:image/png;base64,AAA', '2026-09-13T10:01:00')")
        db.execute("INSERT INTO arbeitsstaende (schueler_id, state_json, revision, updated_at) VALUES ('s1', '{\"a\":1}', 7, '2026-09-13T10:02:00')")
        db.execute("INSERT INTO chat_messages (schueler_id, typ, frage, antwort, tokens, erstellt_at) VALUES ('s1', 'chat', 'F', 'A', 12, '2026-09-13T10:03:00')")
        db.commit()
    snap = dbmod.build_snapshot()
    assert snap["app_id"] == APP_ID and snap["schema_version"] == DB_SCHEMA_VERSION
    assert snap["tabellen"]["zeichnungen"][0]["preview_data"].startswith("data:image/png")
    digest = dbmod.snapshot_digest(snap)
    assert digest == dbmod.snapshot_digest(json.loads(json.dumps(snap)))

    dbmod.clear_live_data()
    ids = dbmod.restore_snapshot(snap, "ansicht")
    assert ids == ["s1"]
    with dbmod.get_db() as db:
        assert db.execute("SELECT resume_token_hash FROM schueler WHERE id='s1'").fetchone()[0] is None
        assert db.execute("SELECT revision FROM arbeitsstaende WHERE schueler_id='s1'").fetchone()[0] == 7
        assert db.execute("SELECT active FROM fortsetzungsstatus").fetchone() is None

    dbmod.restore_snapshot(snap, "fortsetzung")
    with dbmod.get_db() as db:
        assert db.execute("SELECT resume_token_hash FROM schueler WHERE id='s1'").fetchone()[0] == "hash1"
        assert db.execute("SELECT active FROM fortsetzungsstatus WHERE id=1").fetchone()[0] == 1
        assert db.execute("SELECT status FROM fortsetzungsziele WHERE student_id='s1'").fetchone()[0] == "verfuegbar"
        assert db.execute("SELECT COUNT(*) AS n FROM chat_messages").fetchone()["n"] == 1


def test_snapshot_validierung_lehnt_fremde_und_kaputte_ab():
    import pytest
    with pytest.raises(ValueError):
        dbmod.validate_snapshot({"app_id": "andere-app", "schema_version": 1, "tabellen": {}})
    with pytest.raises(ValueError):
        dbmod.validate_snapshot({"app_id": APP_ID, "schema_version": 99, "tabellen": {}})
    with pytest.raises(ValueError):
        dbmod.validate_snapshot({"app_id": APP_ID, "schema_version": 2, "tabellen": {"boese": []}})
    with pytest.raises(ValueError):
        dbmod.validate_snapshot({"app_id": APP_ID, "schema_version": 2, "tabellen": {"schueler": "kein-array"}})
    # Ältere Snapshots ohne optionale Tabellen sind gültig
    dbmod.validate_snapshot({"app_id": APP_ID, "schema_version": 1, "tabellen": {"schueler": []}})


def test_benannte_snapshots_speichern_laden_loeschen():
    dbmod.init_db()
    dbmod.clear_live_data()
    dbmod.delete_all_named_snapshots()
    with dbmod.get_db() as db:
        db.execute("INSERT INTO schueler (id, pseudonym, klasse, joined_at) VALUES ('s1', 'Maus', '9', '2026-09-13T10:00:00')")
        db.commit()
    info = dbmod.save_named_snapshot("Stunde 1")
    assert info["lernende"] == 1
    liste = dbmod.list_named_snapshots()
    assert [s["name"] for s in liste] == ["Stunde 1"]
    geladen = dbmod.load_named_snapshot(info["id"])
    assert geladen["tabellen"]["schueler"][0]["pseudonym"] == "Maus"
    assert dbmod.delete_named_snapshot(info["id"]) is True
    assert dbmod.list_named_snapshots() == []
    assert dbmod.load_named_snapshot("gibt-es-nicht") is None


def test_notizen_sync_spiegelt_texte():
    dbmod.init_db()
    dbmod.clear_live_data()
    state = {"texte": {"nt-nutztier": "• Die Biene gibt Honig", "nq-nutztier": "imkerbund.de", "ft-T": "Transfer"}, "quellen": [{"titel": "bpb"}]}
    with dbmod.get_db() as db:
        geaendert = dbmod.sync_notizen_from_state(db, "s1", state, "2026-09-13T10:00:00")
        db.commit()
        assert set(geaendert) == {"nutztier", "abschluss"}
        row = db.execute("SELECT stichpunkte, quellen FROM notizen WHERE schueler_id='s1' AND abschnitt='nutztier'").fetchone()
        assert row["stichpunkte"] == "• Die Biene gibt Honig" and row["quellen"] == "imkerbund.de"
        # unverändert → keine Änderung gemeldet
        assert dbmod.sync_notizen_from_state(db, "s1", state, "2026-09-13T10:01:00") == []


def test_cleanup_after_archive_leert_alles_und_verdichtet():
    dbmod.init_db()
    with dbmod.get_db() as db:
        db.execute("INSERT OR REPLACE INTO schueler (id, pseudonym, klasse, joined_at) VALUES ('s9', 'X', '9', '2026-09-13T10:00:00')")
        db.commit()
    dbmod.save_named_snapshot("temp")
    dbmod.cleanup_after_archive()
    with dbmod.get_db() as db:
        for t in dbmod.SNAPSHOT_TABELLEN + ["gespeicherte_sitzungen"]:
            assert db.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"] == 0, t
    assert os.path.exists(dbmod.DB_PATH)
