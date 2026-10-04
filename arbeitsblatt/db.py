"""SQLite-Zugriff, additive Migrationen, Snapshots und Bereinigung.

Grundsätze (Standard §6, §13, §17):
- Es wird nichts beim Serverstart gelöscht. Eine laufende Sitzung überlebt Neustart,
  Redeploy und späteren Lehrkraft-Login.
- Schemaänderungen sind additiv; ältere Datenbanken werden nie verworfen.
- Ein vollständiger Snapshot umfasst alle Sitzungstabellen, aber keine temporären
  Lehrkraft-Snapshots und keine Lehrkraft-Token.
"""

import datetime as dt
import hashlib
import json
import os
import sqlite3
import uuid

from tafel.speicher import SQL_SCHEMA as TAFEL_SCHEMA, SQL_TABELLEN as TAFEL_TABELLEN
from config import APP_ID, DB_PATH, DB_SCHEMA_VERSION, NOTIZ_ABSCHNITTE, SNAPSHOT_MAX_BYTES

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS schueler (
    id TEXT PRIMARY KEY, pseudonym TEXT NOT NULL, klasse TEXT NOT NULL,
    joined_at TEXT NOT NULL, last_active TEXT, socket_id TEXT, resume_token_hash TEXT
);
CREATE TABLE IF NOT EXISTS fortschritt (
    id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, aufgabe_nr TEXT NOT NULL,
    niveau TEXT NOT NULL DEFAULT 'A', erledigt_at TEXT NOT NULL, UNIQUE(schueler_id, aufgabe_nr, niveau)
);
CREATE TABLE IF NOT EXISTS antworten (
    id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, aufgabe_nr TEXT NOT NULL,
    niveau TEXT NOT NULL, antwort_typ TEXT NOT NULL, frage TEXT, antwort_text TEXT, korrekt INTEGER,
    versuch_nr INTEGER NOT NULL DEFAULT 1, erstellt_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notizen (
    id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, abschnitt TEXT NOT NULL,
    stichpunkte TEXT NOT NULL DEFAULT '', quellen TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
    UNIQUE(schueler_id, abschnitt)
);
CREATE TABLE IF NOT EXISTS ki_anfragen (
    id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, typ TEXT NOT NULL, kontext TEXT,
    status TEXT NOT NULL DEFAULT 'wartend', token_count INTEGER NOT NULL DEFAULT 0,
    erstellt_at TEXT NOT NULL, bearbeitet_at TEXT
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, typ TEXT NOT NULL,
    frage TEXT NOT NULL, antwort TEXT NOT NULL, tokens INTEGER NOT NULL DEFAULT 0, erstellt_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS token_budget (datum TEXT PRIMARY KEY, tokens_used INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS ki_sperren (schueler_id TEXT PRIMARY KEY, gesperrt_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS zeichnungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT, schueler_id TEXT NOT NULL, geraet TEXT NOT NULL,
    canvas_json TEXT NOT NULL, preview_data TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(schueler_id, geraet)
);
CREATE TABLE IF NOT EXISTS arbeitsstaende (
    schueler_id TEXT PRIMARY KEY, state_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS gespeicherte_sitzungen (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, snapshot_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fortsetzungsstatus (
    id INTEGER PRIMARY KEY CHECK (id = 1), active INTEGER NOT NULL DEFAULT 0, source_name TEXT, started_at TEXT
);
CREATE TABLE IF NOT EXISTS fortsetzungsziele (student_id TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'verfuegbar');
CREATE TABLE IF NOT EXISTS fortsetzungsanfragen (
    id TEXT PRIMARY KEY, new_student_id TEXT NOT NULL, pseudonym TEXT NOT NULL, klasse TEXT NOT NULL,
    resume_token_hash TEXT NOT NULL, target_student_id TEXT, status TEXT NOT NULL DEFAULT 'wartend',
    created_at TEXT NOT NULL, decided_at TEXT
);
CREATE TABLE IF NOT EXISTS ki_gruppenfreigabe (
    id INTEGER PRIMARY KEY CHECK (id = 1), active INTEGER NOT NULL DEFAULT 0, locked INTEGER NOT NULL DEFAULT 0,
    klasse TEXT NOT NULL DEFAULT '', allowed_types TEXT NOT NULL DEFAULT '[]', starts_at TEXT, expires_at TEXT,
    token_limit INTEGER NOT NULL DEFAULT 0, tokens_used INTEGER NOT NULL DEFAULT 0, per_student_limit INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ki_gruppen_nutzung (schueler_id TEXT PRIMARY KEY, tokens INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS lehrer_tokens (token_hash TEXT PRIMARY KEY, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS praesentation (
    id INTEGER PRIMARY KEY CHECK (id = 1), active INTEGER NOT NULL DEFAULT 0,
    bild TEXT, hinweis TEXT NOT NULL DEFAULT '', started_at TEXT
);
CREATE TABLE IF NOT EXISTS lesestrecke_status (
    schueler_id TEXT NOT NULL, abschnitt TEXT NOT NULL, phase INTEGER NOT NULL DEFAULT 0,
    fertig INTEGER NOT NULL DEFAULT 0, retry_until REAL NOT NULL DEFAULT 0, versuche INTEGER NOT NULL DEFAULT 0,
    UNIQUE(schueler_id, abschnitt)
);
"""

# Spalten, die ältere Installationen (Schema 1) noch nicht hatten – additiv ergänzen.
ZUSATZSPALTEN = {
    "schueler": {"resume_token_hash": "TEXT", "last_active": "TEXT", "socket_id": "TEXT"},
    "antworten": {"frage": "TEXT"},
}

# Sitzungstabellen: Bestandteil von Snapshot, Reset und Archiv.
SNAPSHOT_TABELLEN = [
    "schueler", "fortschritt", "antworten", "notizen", "ki_anfragen", "chat_messages",
    "token_budget", "ki_sperren", "zeichnungen", "arbeitsstaende", "ki_gruppenfreigabe",
    "ki_gruppen_nutzung", "lesestrecke_status",
    *TAFEL_TABELLEN,   # Tafel: Zustand + Fotos/Vorlagen → Snapshot, IServ, Fortsetzung
]
# Tabellen ohne Spalte schueler_id – beim Löschen eines Lernplatzes nicht per WHERE löschen.
OHNE_SCHUELER_SPALTE = ("token_budget", "ki_gruppenfreigabe", *TAFEL_TABELLEN)
# Tabellen, die bei Reset/Archiv zusätzlich geleert werden (nicht Teil des Snapshots).
SITZUNGS_HILFSTABELLEN = ["fortsetzungsstatus", "fortsetzungsziele", "fortsetzungsanfragen", "praesentation"]


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA secure_delete=ON")
    return db


def _spalten(db: sqlite3.Connection, tabelle: str) -> set[str]:
    return {r["name"] for r in db.execute(f"PRAGMA table_info({tabelle})").fetchall()}


def init_db() -> None:
    """Legt fehlende Tabellen an und ergänzt fehlende Spalten. Löscht nie Daten."""
    with get_db() as db:
        db.executescript(SCHEMA)
        db.executescript(TAFEL_SCHEMA)
        for tabelle, spalten in ZUSATZSPALTEN.items():
            vorhanden = _spalten(db, tabelle)
            for name, decl in spalten.items():
                if name not in vorhanden:
                    db.execute(f"ALTER TABLE {tabelle} ADD COLUMN {name} {decl}")
        db.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (DB_SCHEMA_VERSION, now_iso()),
        )
        # Alte Socket-IDs sind nach einem Prozessstart wertlos (Standard §11).
        db.execute("UPDATE schueler SET socket_id=NULL WHERE socket_id IS NOT NULL")
        db.commit()


def schema_version() -> int:
    with get_db() as db:
        row = db.execute("SELECT MAX(version) AS v FROM schema_migrations").fetchone()
    return int(row["v"] or 0)


# ── Notizen aus dem Arbeitsstand spiegeln ───────────────────────────────────
def sync_notizen_from_state(db: sqlite3.Connection, sid: str, state: dict, zeit: str) -> list[str]:
    """Spiegelt nt-<abschnitt>/nq-<abschnitt> aus `texte` in die Notizen-Tabelle.

    Liefert die Abschnitte, deren Inhalt sich geändert hat (für Live-Ereignisse).
    """
    texte = state.get("texte") or {}
    if not isinstance(texte, dict):
        return []
    geaendert = []
    for abschnitt in NOTIZ_ABSCHNITTE:
        if abschnitt == "abschluss":
            stich = str(texte.get("ft-T", "") or "")[:4000]
            quellen = json.dumps(state.get("quellen") or [], ensure_ascii=False)[:4000]
        else:
            stich = str(texte.get(f"nt-{abschnitt}", "") or "")[:4000]
            quellen = str(texte.get(f"nq-{abschnitt}", "") or "")[:4000]
        alt = db.execute(
            "SELECT stichpunkte, quellen FROM notizen WHERE schueler_id=? AND abschnitt=?", (sid, abschnitt)
        ).fetchone()
        if alt and alt["stichpunkte"] == stich and alt["quellen"] == quellen:
            continue
        if not alt and not stich and not quellen:
            continue
        db.execute(
            "INSERT INTO notizen (schueler_id, abschnitt, stichpunkte, quellen, updated_at) VALUES (?,?,?,?,?) "
            "ON CONFLICT(schueler_id, abschnitt) DO UPDATE SET stichpunkte=excluded.stichpunkte, "
            "quellen=excluded.quellen, updated_at=excluded.updated_at",
            (sid, abschnitt, stich, quellen, zeit),
        )
        geaendert.append(abschnitt)
    return geaendert


# ── Snapshots ───────────────────────────────────────────────────────────────
def build_snapshot() -> dict:
    """Vollständiger Live-Snapshot aller Sitzungstabellen (inkl. Resume-Token-Hashes)."""
    with get_db() as db:
        tabellen = {
            t: [dict(r) for r in db.execute(f"SELECT * FROM {t}").fetchall()] for t in SNAPSHOT_TABELLEN
        }
    return {
        "schema_version": DB_SCHEMA_VERSION,
        "app_id": APP_ID,
        "created_at": now_iso(),
        "tabellen": tabellen,
    }


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def snapshot_digest(snapshot: dict) -> str:
    return hashlib.sha256(canonical_json(snapshot)).hexdigest()


def validate_snapshot(snapshot) -> dict:
    """Prüft Typen, App-ID, Schema-Version und Größe. Wirft ValueError."""
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot ist kein Objekt.")
    if snapshot.get("app_id") != APP_ID:
        raise ValueError("Snapshot gehört zu einer anderen App.")
    version = snapshot.get("schema_version")
    if not isinstance(version, int) or version < 1 or version > DB_SCHEMA_VERSION:
        raise ValueError("Unbekannte Schema-Version des Snapshots.")
    tabellen = snapshot.get("tabellen")
    if not isinstance(tabellen, dict):
        raise ValueError("Snapshot enthält keine Tabellen.")
    for name, zeilen in tabellen.items():
        if name not in SNAPSHOT_TABELLEN:
            raise ValueError(f"Unbekannte Tabelle im Snapshot: {name}")
        if not isinstance(zeilen, list) or any(not isinstance(z, dict) for z in zeilen):
            raise ValueError(f"Tabelle {name} hat ein falsches Format.")
    if len(canonical_json(snapshot)) > SNAPSHOT_MAX_BYTES:
        raise ValueError("Snapshot ist zu groß.")
    return snapshot


def _insert_rows(db: sqlite3.Connection, tabelle: str, zeilen: list[dict]) -> None:
    spalten = _spalten(db, tabelle)
    for zeile in zeilen:
        felder = [k for k in zeile.keys() if k in spalten]
        if not felder:
            continue
        platzhalter = ",".join("?" for _ in felder)
        db.execute(
            f"INSERT OR REPLACE INTO {tabelle} ({','.join(felder)}) VALUES ({platzhalter})",
            [zeile[k] for k in felder],
        )


def clear_live_data(db: sqlite3.Connection | None = None) -> None:
    """Leert alle Sitzungstabellen (Reset, Restore-Vorbereitung, Archiv-Bereinigung)."""
    eigene = db is None
    db = db or get_db()
    for tabelle in SNAPSHOT_TABELLEN + SITZUNGS_HILFSTABELLEN:
        db.execute(f"DELETE FROM {tabelle}")
    if eigene:
        db.commit()
        db.close()


def restore_snapshot(snapshot: dict, modus: str) -> list[str]:
    """Ersetzt die Live-Tabellen durch den Snapshot.

    modus 'ansicht': Resume-Token-Hashes werden entfernt (keine Wiederverbindung).
    modus 'fortsetzung': Hashes bleiben, Fortsetzungsmodus wird aktiviert, alle
    Lernplätze werden als verfügbar markiert.
    Liefert die IDs der wiederhergestellten Lernplätze.
    """
    if modus not in ("ansicht", "fortsetzung"):
        raise ValueError("Unbekannter Wiederherstellungsmodus.")
    validate_snapshot(snapshot)
    tabellen = snapshot["tabellen"]
    ids = [str(z.get("id")) for z in tabellen.get("schueler", []) if z.get("id")]
    with get_db() as db:
        clear_live_data(db)
        for tabelle in SNAPSHOT_TABELLEN:
            zeilen = tabellen.get(tabelle, [])
            if tabelle == "schueler":
                zeilen = [dict(z, socket_id=None) for z in zeilen]
                if modus == "ansicht":
                    zeilen = [dict(z, resume_token_hash=None) for z in zeilen]
            _insert_rows(db, tabelle, zeilen)
        if modus == "fortsetzung":
            db.execute(
                "INSERT OR REPLACE INTO fortsetzungsstatus (id, active, source_name, started_at) VALUES (1, 1, ?, ?)",
                (str(snapshot.get("name") or snapshot.get("created_at") or ""), now_iso()),
            )
            for sid in ids:
                db.execute("INSERT OR REPLACE INTO fortsetzungsziele (student_id, status) VALUES (?, 'verfuegbar')", (sid,))
        db.commit()
    return ids


def save_named_snapshot(name: str) -> dict:
    snapshot = build_snapshot()
    sid = uuid.uuid4().hex[:12]
    zeit = now_iso()
    with get_db() as db:
        db.execute(
            "INSERT INTO gespeicherte_sitzungen (id, name, snapshot_json, created_at, updated_at) VALUES (?,?,?,?,?)",
            (sid, name, json.dumps(snapshot, ensure_ascii=False), zeit, zeit),
        )
        db.commit()
    return {"id": sid, "name": name, "created_at": zeit, "lernende": len(snapshot["tabellen"]["schueler"])}


def list_named_snapshots() -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, created_at, updated_at, length(snapshot_json) AS groesse FROM gespeicherte_sitzungen ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def load_named_snapshot(sid: str) -> dict | None:
    with get_db() as db:
        row = db.execute("SELECT snapshot_json FROM gespeicherte_sitzungen WHERE id=?", (sid,)).fetchone()
    if not row:
        return None
    return json.loads(row["snapshot_json"])


def delete_named_snapshot(sid: str) -> bool:
    with get_db() as db:
        cur = db.execute("DELETE FROM gespeicherte_sitzungen WHERE id=?", (sid,))
        db.commit()
    return cur.rowcount > 0


def delete_all_named_snapshots() -> None:
    with get_db() as db:
        db.execute("DELETE FROM gespeicherte_sitzungen")
        db.commit()


# ── Bereinigung ─────────────────────────────────────────────────────────────
def delete_student(sid: str) -> None:
    with get_db() as db:
        for tabelle in SNAPSHOT_TABELLEN:
            if tabelle in OHNE_SCHUELER_SPALTE:
                continue  # Tafel-Beiträge entfernt die Tafel selbst (TafelServer.person_entfernen)
            spalte = "id" if tabelle == "schueler" else "schueler_id"
            db.execute(f"DELETE FROM {tabelle} WHERE {spalte}=?", (sid,))
        db.execute("DELETE FROM fortsetzungsziele WHERE student_id=?", (sid,))
        db.execute("DELETE FROM fortsetzungsanfragen WHERE new_student_id=? OR target_student_id=?", (sid, sid))
        db.commit()


def compact_database() -> None:
    """secure_delete ist aktiv; zusätzlich WAL abschneiden und die Datei verdichten."""
    db = get_db()
    try:
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db.commit()
        try:
            db.execute("VACUUM")
        except sqlite3.OperationalError:
            pass  # z. B. bei offener Transaktion – bestmöglich, nicht zwingend
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db.commit()
    finally:
        db.close()


def cleanup_after_archive() -> None:
    """Erst nach bestandener Upload-Download-Digestprüfung aufrufen (Standard §17)."""
    with get_db() as db:
        clear_live_data(db)
        db.execute("DELETE FROM gespeicherte_sitzungen")
        db.commit()
    compact_database()
