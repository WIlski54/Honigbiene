"""Interaktives Arbeitsblatt „Die Honigbiene – ein Nutztier mit eigenem Staat“ (NW, Klasse 6) – Flask-Backend.

Vollversion nach dem GSM-Produktionsstandard (Sept. 2026): pseudonymer Lernplatz mit
Resume-Token, exakte Präsenz, differenzierte Aufgaben (A/B/C), Antwortprotokoll,
Server-Autosave mit monotonen Revisionen, KI-Freigaben (Einzel + Gruppe),
temporäre Lehrkraft-Snapshots, IServ-Archiv, Fortsetzungsstunde.
"""

import base64
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
import uuid
from functools import wraps
from urllib.parse import urlsplit

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, join_room

import db as dbmod
import ki
import praesentation
import presence
from config import (
    ABSCHNITTE, AI_REQUEST_TYPES, ALLE_AUFGABEN, anzeige_label, anzeige_nr, ANTWORT_TYPEN, APP_ID, APP_TITEL, ASSET_VERSION,
    ANTWORT_MAX_ZEICHEN, APP_FACH, AUFGABE_ZU_ABSCHNITT, DAILY_TOKEN_LIMIT, LEHRER_PASSWORD, LESESTRECKEN, NIVEAUS, NOTIZ_ABSCHNITTE,
    nr_von_typ,
    SECRET_KEY, SESSION_COOKIE_SECURE, SOCKETIO_ASYNC_MODE, STATE_MAX_BYTES, STATE_SCHEMA_VERSION,
    ZEICHEN_GERAETE,
)
import tafel_anbindung
from db import get_db, now_iso

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE,
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,  # Handschrift-/Zeichnungs-PNGs
)
# Sichtbare Nummern (1, 2, 3 …) für die Lehrerseiten; intern bleiben die Nummern der plan-Dateien (siehe config.ANZEIGE_NR).
app.jinja_env.globals.update(anzeige_nr=anzeige_nr, anzeige_label=anzeige_label)


def socket_origin_erlaubt(origin: str, environ: dict) -> bool:
    """Live-Verbindungen nur von Seiten dieses Hosts – das Schema zählt dabei nicht.

    Hinter Coolify/Traefik endet TLS am Proxy, und bei WebSocket-Upgrades meldet er
    „X-Forwarded-Proto: wss“. Die Standardprüfung von Engine.IO erwartet dann „http://host“
    oder „wss://host“ und lehnt jeden Browser („https://host“) ab: Das Dashboard bekam keine
    Live-Meldungen mehr. Der Host-Vergleich schützt genauso gegen fremde Seiten
    (Cross-Site-WebSocket-Hijacking), weil der Browser den Origin nicht fälschen lässt.
    """
    teile = urlsplit(origin or "")
    if teile.scheme not in ("http", "https") or not teile.netloc:
        return False
    hosts = {environ.get("HTTP_HOST", ""), environ.get("HTTP_X_FORWARDED_HOST", "").split(",")[0].strip()}
    return teile.netloc.lower() in {h.lower() for h in hosts if h}


socketio = SocketIO(app, async_mode=SOCKETIO_ASYNC_MODE, cors_allowed_origins=socket_origin_erlaubt)


# ── Hilfsfunktionen ──────────────────────────────────────────────────────────
def token_hash(token: str) -> str:
    """App-gebundener Hash eines Resume- oder Lehrkraft-Tokens (Standard §10)."""
    return hashlib.sha256(f"{APP_ID}:{token}".encode("utf-8")).hexdigest()


def normalize_name(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def emit_lehrer(event: str, data) -> None:
    socketio.emit(event, data, to="lehrer_room")


def emit_schueler(sid: str, event: str, data) -> None:
    socketio.emit(event, data, to=f"schueler_{sid}")


def emit_watch(sid: str, event: str, data) -> None:
    socketio.emit(event, data, to=f"watch_{sid}")


def touch_student(db, sid: str) -> None:
    db.execute("UPDATE schueler SET last_active=? WHERE id=?", (now_iso(), sid))


def fortsetzung_status() -> dict:
    with get_db() as db:
        row = db.execute("SELECT active, source_name, started_at FROM fortsetzungsstatus WHERE id=1").fetchone()
    if not row:
        return {"active": False, "source_name": None, "started_at": None}
    return {"active": bool(row["active"]), "source_name": row["source_name"], "started_at": row["started_at"]}


def get_schueler_info(sid: str) -> dict:
    with get_db() as db:
        s = db.execute("SELECT * FROM schueler WHERE id=?", (sid,)).fetchone()
        if not s:
            return {}
        rows = db.execute("SELECT aufgabe_nr, niveau FROM fortschritt WHERE schueler_id=?", (sid,)).fetchall()
        antworten = db.execute("SELECT COUNT(*) AS n FROM antworten WHERE schueler_id=?", (sid,)).fetchone()["n"]
        pending = db.execute(
            "SELECT COUNT(*) AS n FROM ki_anfragen WHERE schueler_id=? AND status='wartend'", (sid,)
        ).fetchone()["n"]
        tokens_einzel = db.execute(
            "SELECT COALESCE(SUM(token_count),0) AS t FROM ki_anfragen WHERE schueler_id=?", (sid,)
        ).fetchone()["t"]
        tokens_gruppe = db.execute(
            "SELECT COALESCE(tokens,0) AS t FROM ki_gruppen_nutzung WHERE schueler_id=?", (sid,)
        ).fetchone()
        notizen = db.execute(
            "SELECT COUNT(*) AS n FROM notizen WHERE schueler_id=? AND length(trim(stichpunkte))>0", (sid,)
        ).fetchone()["n"]
        autosave = db.execute("SELECT revision, updated_at FROM arbeitsstaende WHERE schueler_id=?", (sid,)).fetchone()
        zeichnungen = db.execute("SELECT COUNT(*) AS n FROM zeichnungen WHERE schueler_id=? AND geraet!='handschrift'", (sid,)).fetchone()["n"]
        gesperrt = db.execute("SELECT 1 FROM ki_sperren WHERE schueler_id=?", (sid,)).fetchone() is not None
    erledigt = sorted({str(r["aufgabe_nr"]) for r in rows}, key=lambda x: (not x[0].isdigit(), int(x) if x.isdigit() else 0, x))
    abschnitte = {}
    for a in ABSCHNITTE:
        soll = [str(n) for n in a["aufgaben"]]
        abschnitte[a["key"]] = {
            "titel": a["titel"], "kurz": a["kurz"],
            "erledigt": len([n for n in soll if n in erledigt]), "gesamt": len(soll),
        }
    return {
        "id": s["id"], "pseudonym": s["pseudonym"], "klasse": s["klasse"],
        "joined_at": s["joined_at"], "last_active": s["last_active"],
        "online": presence.is_online(sid), "ki_gesperrt": gesperrt,
        "aufgaben_erledigt": len(erledigt), "aufgaben_gesamt": len(ALLE_AUFGABEN),
        "erledigt_liste": erledigt,
        "niveaus": [{"nr": str(r["aufgabe_nr"]), "anzeige": anzeige_nr(r["aufgabe_nr"]), "niveau": r["niveau"]} for r in rows],
        "abschnitte": abschnitte, "antworten": antworten, "notizen": notizen,
        "pending": pending, "tokens": int(tokens_einzel or 0) + int(tokens_gruppe["t"] if tokens_gruppe else 0),
        "autosave_at": autosave["updated_at"] if autosave else None,
        "autosave_revision": autosave["revision"] if autosave else 0,
        "zeichnungen": zeichnungen,
    }


def alle_schueler_infos() -> list[dict]:
    with get_db() as db:
        ids = [r["id"] for r in db.execute("SELECT id FROM schueler ORDER BY last_active DESC").fetchall()]
    return [get_schueler_info(i) for i in ids]


def offene_anfragen() -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT k.*, s.pseudonym, s.klasse FROM ki_anfragen k JOIN schueler s ON k.schueler_id=s.id "
            "WHERE k.status='wartend' ORDER BY k.erstellt_at"
        ).fetchall()
    return [dict(r) for r in rows]


def wartende_fortsetzungsanfrage(sid: str):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM fortsetzungsanfragen WHERE new_student_id=? AND status='wartend'", (sid,)
        ).fetchone()


def fortsetzung_kandidaten(db, pseudonym: str, klasse: str) -> list[str]:
    """Freie alte Lernplätze, die zu einer Anmeldung in der Fortsetzungsstunde passen.

    Das Pseudonym entscheidet. Die Klasse trennt nur, wenn mehrere freie Lernplätze dasselbe
    Pseudonym tragen – so findet „6“ statt „6a“ trotzdem den eigenen Lernplatz, und bei
    zwei gleichen Pseudonymen wird nicht geraten. Genau ein Kandidat = eindeutiger Treffer.
    """
    rows = db.execute(
        "SELECT z.student_id, s.pseudonym, s.klasse FROM fortsetzungsziele z "
        "JOIN schueler s ON s.id=z.student_id WHERE z.status='verfuegbar'"
    ).fetchall()
    gleich = [r for r in rows if normalize_name(r["pseudonym"]) == normalize_name(pseudonym)]
    if len(gleich) > 1:
        gleich = [r for r in gleich if normalize_name(r["klasse"]) == normalize_name(klasse)] or gleich
    return [r["student_id"] for r in gleich]


# ── Zugriffsschutz ───────────────────────────────────────────────────────────
def schueler_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sid = session.get("schueler_id")
        if not sid:
            if request.path.startswith("/api/"):
                return jsonify({"ok": False, "error": "nicht angemeldet"}), 401
            return redirect(url_for("login"))
        with get_db() as db:
            exists = db.execute("SELECT 1 FROM schueler WHERE id=?", (sid,)).fetchone()
        if not exists:
            for key in ("schueler_id", "pseudonym", "klasse", "resume_token"):
                session.pop(key, None)
            if request.path.startswith("/api/"):
                return jsonify({"ok": False, "error": "sitzung abgelaufen"}), 401
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def lehrer_token_gueltig(token: str | None) -> bool:
    if not token:
        return False
    with get_db() as db:
        return db.execute("SELECT 1 FROM lehrer_tokens WHERE token_hash=?", (token_hash(token),)).fetchone() is not None


def ist_lehrer() -> bool:
    """Header-Token zuerst (funktioniert auch, wenn Lehrkraft und Lernende dasselbe Browserprofil nutzen)."""
    header = request.headers.get("X-Lehrer-Token")
    if header and lehrer_token_gueltig(header):
        return True
    return bool(session.get("is_lehrer")) and lehrer_token_gueltig(session.get("lehrer_token"))


def praesentation_frei(func):
    """Sperrt während des Präsentationsmodus alles, was Arbeit ist.

    Der Autosave bleibt bewusst offen: Was jemand vorher getippt hat, darf nicht
    verloren gehen. Gesperrt sind Antworten, Fortschritt, Lesestreckenfragen,
    Zeichnungen und alle KI-Aufrufe – damit auch niemand weiterarbeitet, der das
    Overlay im Browser entfernt.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if praesentation.aktiv():
            return jsonify({"ok": False, "error": "Präsentationsmodus aktiv – bitte auf das Bild schauen.",
                            "praesentation": True}), 423
        return func(*args, **kwargs)
    return wrapper


def lehrer_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not ist_lehrer():
            if request.path.startswith("/api/") or request.is_json:
                return jsonify({"ok": False, "error": "nicht autorisiert"}), 401
            return redirect(url_for("lehrer_login"))
        return func(*args, **kwargs)

    return wrapper


# ── Seiten ───────────────────────────────────────────────────────────────────
@app.route("/")
def root():
    if session.get("schueler_id"):
        return redirect(url_for("arbeitsblatt"))
    return redirect(url_for("login"))


@app.route("/health")
def health():
    with get_db() as db:
        db.execute("SELECT 1 FROM schueler LIMIT 1")
    return jsonify({"ok": True, "app": APP_ID, "ki": ki.konfiguriert()})


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    fortsetzung = fortsetzung_status()
    if request.method == "POST":
        pseudonym = request.form.get("pseudonym", "").strip()[:30]
        klasse = request.form.get("klasse", "").strip()[:20]
        if len(pseudonym) < 2:
            error = "Bitte ein Pseudonym mit mindestens 2 Zeichen wählen."
        elif not klasse:
            error = "Bitte die Klasse eintragen."
        elif not request.form.get("privacy_ok"):
            error = "Bitte den Datenschutz- und KI-Hinweis bestätigen."
        else:
            sid = secrets.token_hex(8)
            token = secrets.token_urlsafe(32)
            now = now_iso()
            ziel = None   # alter Lernplatz, wenn die Fortsetzungsstunde eindeutig zuordnen kann
            with get_db() as db:
                db.execute(
                    "INSERT INTO schueler (id, pseudonym, klasse, joined_at, last_active, resume_token_hash) VALUES (?,?,?,?,?,?)",
                    (sid, pseudonym, klasse, now, now, token_hash(token)),
                )
                if fortsetzung["active"]:
                    anfrage_id = uuid.uuid4().hex[:12]
                    db.execute(
                        "INSERT INTO fortsetzungsanfragen (id, new_student_id, pseudonym, klasse, resume_token_hash, status, created_at) "
                        "VALUES (?,?,?,?,?,'wartend',?)",
                        (anfrage_id, sid, pseudonym, klasse, token_hash(token), now),
                    )
                    # Eindeutiger Treffer: sofort den alten Lernplatz öffnen, statt auf einen Klick der
                    # Lehrkraft zu warten. Mehrdeutiges und Unbekanntes bleibt auf der Warteseite.
                    # Läuft in derselben Schreibtransaktion wie das INSERT oben – zwei gleichzeitige
                    # Anmeldungen mit demselben Pseudonym werden von SQLite nacheinander abgearbeitet.
                    kandidaten = fortsetzung_kandidaten(db, pseudonym, klasse)
                    if len(kandidaten) == 1:
                        anfrage = db.execute("SELECT * FROM fortsetzungsanfragen WHERE id=?", (anfrage_id,)).fetchone()
                        if _fortsetzung_zuordnen(db, anfrage, kandidaten[0]):
                            ziel = db.execute("SELECT id, pseudonym, klasse FROM schueler WHERE id=?", (kandidaten[0],)).fetchone()
                db.commit()
            for key in ("schueler_id", "pseudonym", "klasse", "resume_token"):
                session.pop(key, None)
            if ziel:
                session.update({"schueler_id": ziel["id"], "pseudonym": ziel["pseudonym"], "klasse": ziel["klasse"], "resume_token": token})
                emit_lehrer("fortsetzung_update", fortsetzung_payload())
                emit_lehrer("neuer_schueler", get_schueler_info(ziel["id"]))
                return redirect(url_for("arbeitsblatt"))
            session.update({"schueler_id": sid, "pseudonym": pseudonym, "klasse": klasse, "resume_token": token})
            if fortsetzung["active"]:
                emit_lehrer("fortsetzung_update", fortsetzung_payload())
                return redirect(url_for("warten"))
            emit_lehrer("neuer_schueler", get_schueler_info(sid))
            return redirect(url_for("arbeitsblatt"))
    return render_template(
        "login.html", error=error, app_id=APP_ID, v=ASSET_VERSION, fortsetzung=fortsetzung,
        schema_version=STATE_SCHEMA_VERSION, titel=APP_TITEL, fach=APP_FACH,
    )


@app.route("/logout", methods=["GET", "POST"])
def logout():
    sid = session.get("schueler_id")
    if sid:
        with get_db() as db:
            db.execute("UPDATE schueler SET resume_token_hash=NULL WHERE id=?", (sid,))
            db.commit()
    for key in ("schueler_id", "pseudonym", "klasse", "resume_token"):
        session.pop(key, None)
    return redirect(url_for("login", abgemeldet=1))


@app.route("/arbeitsblatt")
@schueler_required
def arbeitsblatt():
    sid = session["schueler_id"]
    if wartende_fortsetzungsanfrage(sid):
        return redirect(url_for("warten"))
    return render_template(
        "index.html",
        pseudonym=session["pseudonym"], klasse=session["klasse"], schueler_id=sid,
        resume_token=session.get("resume_token", ""), abschnitte=ABSCHNITTE,
        aufgaben_gesamt=len(ALLE_AUFGABEN), app_id=APP_ID, schema_version=STATE_SCHEMA_VERSION,
        titel=APP_TITEL, fach=APP_FACH, v=ASSET_VERSION, einstiegsbild=praesentation.BILDER["einstieg"]["datei"],
    )


@app.route("/warten")
def warten():
    return render_template(
        "warten.html", app_id=APP_ID, v=ASSET_VERSION, pseudonym=session.get("pseudonym", ""),
        schueler_id=session.get("schueler_id", ""), resume_token=session.get("resume_token", ""),
        titel=APP_TITEL,
    )


@app.route("/lehrer/login", methods=["GET", "POST"])
def lehrer_login():
    error = None
    if request.method == "POST":
        if not LEHRER_PASSWORD:
            error = "LEHRER_PASSWORD ist auf dem Server nicht gesetzt."
        elif hmac.compare_digest(request.form.get("passwort", ""), LEHRER_PASSWORD):
            token = secrets.token_urlsafe(32)
            with get_db() as db:
                db.execute("INSERT INTO lehrer_tokens (token_hash, created_at) VALUES (?, ?)", (token_hash(token), now_iso()))
                db.commit()
            session["is_lehrer"] = True
            session["lehrer_token"] = token
            return redirect(url_for("lehrer_dashboard"))
        else:
            error = "Falsches Passwort."
    return render_template("lehrer_login.html", error=error, v=ASSET_VERSION, titel=APP_TITEL)


@app.route("/lehrer/logout", methods=["GET", "POST"])
def lehrer_logout():
    token = session.pop("lehrer_token", None)
    session.pop("is_lehrer", None)
    if token:
        with get_db() as db:
            db.execute("DELETE FROM lehrer_tokens WHERE token_hash=?", (token_hash(token),))
            db.commit()
    return redirect(url_for("lehrer_login"))


@app.route("/lehrer")
@lehrer_required
def lehrer_dashboard():
    return render_template(
        "dashboard.html",
        schueler_infos=alle_schueler_infos(), offene=offene_anfragen(),
        today_tokens=ki.get_today_tokens(), token_limit=DAILY_TOKEN_LIMIT, abschnitte=ABSCHNITTE,
        aufgaben_gesamt=len(ALLE_AUFGABEN), ki_konfiguriert=ki.konfiguriert(),
        lehrer_token=session.get("lehrer_token", ""), iserv=iserv_status_payload(),
        fortsetzung=fortsetzung_status(), titel=APP_TITEL, fach=APP_FACH, v=ASSET_VERSION,
        zeichen_nrs=[anzeige_nr(n) for n in ZEICHEN_GERAETE.values() if n],
        nrs={t: "/".join(anzeige_nr(n) for n in nr_von_typ(t)) for t in ("blitz", "domino", "quellen", "transfer", "forscherbuch")},
    )


@app.route("/lehrer/schueler/<sid>")
@lehrer_required
def lehrer_schueler_detail(sid):
    info = get_schueler_info(sid)
    if not info:
        return redirect(url_for("lehrer_dashboard"))
    with get_db() as db:
        antworten = [dict(r) for r in db.execute(
            "SELECT * FROM antworten WHERE schueler_id=? ORDER BY erstellt_at, id", (sid,)).fetchall()]
        notizen = {r["abschnitt"]: dict(r) for r in db.execute("SELECT * FROM notizen WHERE schueler_id=?", (sid,)).fetchall()}
        anfragen = [dict(r) for r in db.execute(
            "SELECT * FROM ki_anfragen WHERE schueler_id=? ORDER BY erstellt_at DESC LIMIT 50", (sid,)).fetchall()]
        zeichnungen = [dict(r) for r in db.execute(
            "SELECT geraet, canvas_json, preview_data, updated_at FROM zeichnungen WHERE schueler_id=?", (sid,)).fetchall()]
    for z in zeichnungen:
        try:
            z["objekte"] = len((json.loads(z["canvas_json"]) or {}).get("objects", []))
        except (json.JSONDecodeError, AttributeError):
            z["objekte"] = 0
        z.pop("canvas_json", None)
    return render_template(
        "schueler_detail.html", info=info, antworten=antworten, notizen=notizen, anfragen=anfragen,
        zeichnungen=zeichnungen, chat=ki.chat_verlauf(sid), abschnitte=ABSCHNITTE,
        lehrer_token=session.get("lehrer_token", ""), titel=APP_TITEL, v=ASSET_VERSION,
    )


# ── Lernplatz-Identität ──────────────────────────────────────────────────────
@app.route("/api/resume", methods=["POST"])
def api_resume():
    """Sichere Wiederaufnahme desselben Lernplatzes über Lernplatz-ID + Resume-Token."""
    data = request.get_json(silent=True) or {}
    sid = str(data.get("schueler_id", ""))[:32]
    token = str(data.get("token", ""))[:128]
    if not sid or not token:
        return jsonify({"ok": False, "error": "Lernplatz-ID und Token fehlen."}), 400
    with get_db() as db:
        row = db.execute("SELECT id, pseudonym, klasse, resume_token_hash FROM schueler WHERE id=?", (sid,)).fetchone()
    fortsetzung = fortsetzung_status()
    if not row:
        return jsonify({"ok": False, "error": "unbekannt", "fortsetzung_aktiv": fortsetzung["active"]}), 404
    if not row["resume_token_hash"] or not secrets.compare_digest(token_hash(token), row["resume_token_hash"]):
        return jsonify({"ok": False, "error": "Token ungültig."}), 403
    with get_db() as db:
        touch_student(db, sid)
        if fortsetzung["active"]:
            db.execute("UPDATE fortsetzungsziele SET status='vergeben' WHERE student_id=? AND status='verfuegbar'", (sid,))
        db.commit()
    for key in ("schueler_id", "pseudonym", "klasse", "resume_token"):
        session.pop(key, None)
    session.update({"schueler_id": sid, "pseudonym": row["pseudonym"], "klasse": row["klasse"], "resume_token": token})
    wartend = wartende_fortsetzungsanfrage(sid) is not None
    if fortsetzung["active"]:
        emit_lehrer("fortsetzung_update", fortsetzung_payload())
    return jsonify({"ok": True, "schueler_id": sid, "pseudonym": row["pseudonym"], "klasse": row["klasse"], "wartend": wartend})


# ── Schüler-API ──────────────────────────────────────────────────────────────
def normalize_task(value) -> str | None:
    text = str(value).strip().upper()
    return text if text in AUFGABE_ZU_ABSCHNITT else None


@app.route("/api/status")
@schueler_required
def api_status():
    sid = session["schueler_id"]
    with get_db() as db:
        rows = db.execute("SELECT aufgabe_nr, niveau FROM fortschritt WHERE schueler_id=?", (sid,)).fetchall()
        autosave = db.execute("SELECT revision, updated_at FROM arbeitsstaende WHERE schueler_id=?", (sid,)).fetchone()
    gruppe = ki.gruppenfreigabe_lesen()
    return jsonify({
        "ok": True,
        "erledigt": [{"nr": r["aufgabe_nr"], "niveau": r["niveau"]} for r in rows],
        "ki_gesperrt": ki.ist_gesperrt(sid) or gruppe["locked"],
        "ki_konfiguriert": ki.konfiguriert(),
        "gruppenfreigabe": {"active": gruppe["active"], "typen": gruppe["typen"], "expires_at": gruppe["expires_at"]},
        "aufgaben_gesamt": len(ALLE_AUFGABEN),
        "autosave": {"revision": autosave["revision"], "updated_at": autosave["updated_at"]} if autosave else None,
        "fortsetzung_aktiv": fortsetzung_status()["active"],
        "praesentation": praesentation.lesen(),
    })


@app.route("/api/praesentation")
@schueler_required
def api_praesentation():
    """Sicherheitsabfrage des Clients: Gilt der Präsentationsmodus noch?"""
    return jsonify({"ok": True, "praesentation": praesentation.lesen()})


@app.route("/api/fortschritt", methods=["POST"])
@schueler_required
@praesentation_frei
def api_fortschritt():
    data = request.get_json(silent=True) or {}
    aufgabe = normalize_task(data.get("aufgabe"))
    niveau = str(data.get("niveau", "A"))
    if aufgabe == "T":
        niveau = "Transfer"
    if not aufgabe or niveau not in NIVEAUS:
        return jsonify({"ok": False, "error": "ungültige Aufgabe"}), 400
    sid = session["schueler_id"]
    with get_db() as db:
        db.execute(
            "INSERT OR IGNORE INTO fortschritt (schueler_id, aufgabe_nr, niveau, erledigt_at) VALUES (?,?,?,?)",
            (sid, aufgabe, niveau, now_iso()),
        )
        touch_student(db, sid)
        db.commit()
    info = get_schueler_info(sid)
    info["aufgaben_neu"] = [{"nr": aufgabe, "anzeige": anzeige_nr(aufgabe), "niveau": niveau}]
    emit_lehrer("fortschritt_update", info)
    return jsonify({"ok": True, "erledigt": info["aufgaben_erledigt"], "gesamt": info["aufgaben_gesamt"]})


@app.route("/api/antwort", methods=["POST"])
@schueler_required
@praesentation_frei
def api_antwort():
    """Expliziter, bewertbarer Versuch – getrennt vom Autosave (Standard §12)."""
    data = request.get_json(silent=True) or {}
    aufgabe = normalize_task(data.get("aufgabe"))
    niveau = str(data.get("niveau", "A"))
    typ = str(data.get("typ", ""))
    if not aufgabe or niveau not in NIVEAUS or typ not in ANTWORT_TYPEN:
        return jsonify({"ok": False, "error": "ungültige Antwort"}), 400
    korrekt = data.get("korrekt")
    korrekt_db = None if korrekt is None else (1 if korrekt else 0)
    text = str(data.get("antwort", ""))[:ANTWORT_MAX_ZEICHEN.get(typ, 500)]
    frage = str(data.get("frage", ""))[:300]
    sid = session["schueler_id"]
    now = now_iso()
    with get_db() as db:
        versuch = db.execute(
            "SELECT COUNT(*) AS n FROM antworten WHERE schueler_id=? AND aufgabe_nr=?", (sid, aufgabe)
        ).fetchone()["n"] + 1
        db.execute(
            "INSERT INTO antworten (schueler_id, aufgabe_nr, niveau, antwort_typ, frage, antwort_text, korrekt, versuch_nr, erstellt_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (sid, aufgabe, niveau, typ, frage, text, korrekt_db, versuch, now),
        )
        touch_student(db, sid)
        db.commit()
        gesamt = db.execute("SELECT COUNT(*) AS n FROM antworten WHERE schueler_id=?", (sid,)).fetchone()["n"]
    emit_watch(sid, "antwort_live", {
        "schueler_id": sid, "aufgabe_nr": aufgabe, "anzeige": anzeige_label(aufgabe), "niveau": niveau, "typ": typ, "frage": frage,
        "antwort": text, "korrekt": korrekt_db, "versuch_nr": versuch, "zeit": now[11:16],
    })
    emit_lehrer("antwort_zaehler", {"schueler_id": sid, "antworten": gesamt})
    return jsonify({"ok": True, "versuch": versuch, "gesamt": gesamt})


# ── Server-Autosave ──────────────────────────────────────────────────────────
def validate_state(state, sid: str) -> dict:
    """Prüft Schema-Version, App-ID, Datentypen und Größe des Arbeitsstands. Wirft ValueError."""
    if not isinstance(state, dict):
        raise ValueError("Arbeitsstand ist kein Objekt.")
    if state.get("app_id") != APP_ID:
        raise ValueError("Arbeitsstand gehört zu einer anderen App.")
    if state.get("schema_version") != STATE_SCHEMA_VERSION:
        raise ValueError("Unbekannte Schema-Version des Arbeitsstands.")
    lernplatz = state.get("lernplatz")
    if lernplatz is not None and (not isinstance(lernplatz, dict) or str(lernplatz.get("schueler_id", sid)) != sid):
        raise ValueError("Arbeitsstand gehört zu einem anderen Lernplatz.")
    typen = {
        "completed": list, "niveaus": dict, "texte": dict, "quellen": list, "aufgaben": dict,
        "lesestrecke": dict, "blitz": dict, "domino": dict, "zeichnungen": dict, "forschen": dict,
    }
    for feld, typ in typen.items():
        if feld in state and state[feld] is not None and not isinstance(state[feld], typ):
            raise ValueError(f"Feld {feld} hat einen falschen Typ.")
    if "active_tab" in state and not isinstance(state.get("active_tab"), (str, type(None))):
        raise ValueError("active_tab hat einen falschen Typ.")
    if any(not isinstance(v, str) for v in (state.get("texte") or {}).values()):
        raise ValueError("Texte müssen Zeichenketten sein.")
    if len(json.dumps(state, ensure_ascii=False).encode("utf-8")) > STATE_MAX_BYTES:
        raise ValueError("Arbeitsstand ist zu groß.")
    return state


@app.route("/api/autosave", methods=["GET"])
@schueler_required
def api_autosave_get():
    sid = session["schueler_id"]
    with get_db() as db:
        row = db.execute("SELECT state_json, revision, updated_at FROM arbeitsstaende WHERE schueler_id=?", (sid,)).fetchone()
    if not row:
        return ("", 204)
    return jsonify({"ok": True, "revision": row["revision"], "updated_at": row["updated_at"], "state": json.loads(row["state_json"])})


@app.route("/api/autosave", methods=["POST"])
@schueler_required
def api_autosave_post():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    try:
        revision = int(data.get("revision"))
        if revision < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "revision fehlt"}), 400
    try:
        state = validate_state(data.get("state"), sid)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    now = now_iso()
    with get_db() as db:
        db.execute(
            "INSERT INTO arbeitsstaende (schueler_id, state_json, revision, updated_at) VALUES (?,?,?,?) "
            "ON CONFLICT(schueler_id) DO UPDATE SET state_json=excluded.state_json, revision=excluded.revision, "
            "updated_at=excluded.updated_at WHERE excluded.revision > arbeitsstaende.revision",
            (sid, json.dumps(state, ensure_ascii=False), revision, now),
        )
        row = db.execute("SELECT revision, updated_at FROM arbeitsstaende WHERE schueler_id=?", (sid,)).fetchone()
        accepted = row["revision"] == revision and row["updated_at"] == now
        geaendert = dbmod.sync_notizen_from_state(db, sid, state, now) if accepted else []
        touch_student(db, sid)
        db.commit()
    if accepted:
        emit_lehrer("autosave_update", {"schueler_id": sid, "revision": revision, "updated_at": now})
        for abschnitt in geaendert:
            texte = state.get("texte") or {}
            if abschnitt == "abschluss":
                payload = {"stichpunkte": texte.get("ft-T", ""), "quellen": json.dumps(state.get("quellen") or [], ensure_ascii=False)}
            else:
                payload = {"stichpunkte": texte.get(f"nt-{abschnitt}", ""), "quellen": texte.get(f"nq-{abschnitt}", "")}
            emit_watch(sid, "notizen_live", dict(payload, schueler_id=sid, abschnitt=abschnitt, zeit=now[11:16]))
    return jsonify({"ok": True, "accepted": accepted, "revision": row["revision"], "updated_at": row["updated_at"]})


# Abschluss-Flush: nur verbundene Sockets werden aufgefordert (Standard §8.4).
_flush_lock = threading.Lock()
_flush_acks: dict[str, int] = {}


def request_flush(timeout: float = 2.5) -> dict:
    online = presence.online_ids()
    with _flush_lock:
        _flush_acks.clear()
    for sid in online:
        emit_schueler(sid, "autosave_flush", {"grund": "abschluss"})
    deadline = time.monotonic() + timeout
    while online and time.monotonic() < deadline:
        with _flush_lock:
            if all(sid in _flush_acks for sid in online):
                break
        socketio.sleep(0.1)
    with _flush_lock:
        confirmed = [sid for sid in online if sid in _flush_acks]
    missing = [sid for sid in online if sid not in confirmed]
    return {"online": online, "confirmed": confirmed, "missing": missing}


# ── Zeichnungen ──────────────────────────────────────────────────────────────
@app.route("/api/zeichnung", methods=["POST"])
@schueler_required
@praesentation_frei
def api_zeichnung():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    geraet = str(data.get("geraet", ""))
    if geraet not in ZEICHEN_GERAETE:
        return jsonify({"ok": False, "error": "unbekanntes Zeichengerät"}), 400
    canvas = data.get("canvas_json")
    preview = str(data.get("preview", ""))
    if not isinstance(canvas, dict) or not isinstance(canvas.get("objects", []), list):
        return jsonify({"ok": False, "error": "canvas_json fehlt"}), 400
    if preview and not preview.startswith("data:image/png;base64,"):
        return jsonify({"ok": False, "error": "Vorschau muss PNG sein"}), 400
    canvas_text = json.dumps(canvas, ensure_ascii=False)
    if len(canvas_text) > STATE_MAX_BYTES or len(preview) > 1_500_000:
        return jsonify({"ok": False, "error": "Zeichnung zu groß"}), 413
    now = now_iso()
    with get_db() as db:
        db.execute(
            "INSERT INTO zeichnungen (schueler_id, geraet, canvas_json, preview_data, updated_at) VALUES (?,?,?,?,?) "
            "ON CONFLICT(schueler_id, geraet) DO UPDATE SET canvas_json=excluded.canvas_json, "
            "preview_data=CASE WHEN excluded.preview_data='' THEN zeichnungen.preview_data ELSE excluded.preview_data END, "
            "updated_at=excluded.updated_at",
            (sid, geraet, canvas_text, preview, now),
        )
        touch_student(db, sid)
        db.commit()
    objekte = len(canvas.get("objects", []))
    emit_watch(sid, "zeichnung_live", {"schueler_id": sid, "geraet": geraet, "objekte": objekte, "preview": preview[:1_500_000], "zeit": now[11:16]})
    return jsonify({"ok": True, "updated_at": now, "objekte": objekte})


@app.route("/api/zeichnungen")
@schueler_required
def api_zeichnungen():
    sid = session["schueler_id"]
    with get_db() as db:
        rows = db.execute("SELECT geraet, canvas_json, preview_data, updated_at FROM zeichnungen WHERE schueler_id=?", (sid,)).fetchall()
    return jsonify({"ok": True, "zeichnungen": {
        r["geraet"]: {"json": json.loads(r["canvas_json"]), "preview": r["preview_data"], "updated_at": r["updated_at"]} for r in rows
    }})


# ── KI ───────────────────────────────────────────────────────────────────────
def _blockiert(pruef: dict, feld: str = "response"):
    return jsonify({feld: None, "blocked": True, "message": pruef["grund"], "feedback": pruef["grund"]})


def _png_bytes(data_url: str) -> bytes | None:
    if not isinstance(data_url, str) or not data_url.startswith("data:image/png;base64,"):
        return None
    try:
        raw = base64.b64decode(data_url.split(",", 1)[1], validate=True)
    except (ValueError, IndexError):
        return None
    return raw if 100 < len(raw) <= 6 * 1024 * 1024 else None


@app.route("/api/ki-anfrage", methods=["POST"])
@schueler_required
def api_ki_anfrage():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    typ = str(data.get("typ", "chat"))
    if typ not in AI_REQUEST_TYPES:
        return jsonify({"status": "error", "message": "Unbekannter Anfragetyp."}), 400
    gruppe = ki.gruppenfreigabe_lesen()
    if gruppe["locked"] or ki.ist_gesperrt(sid):
        return jsonify({"status": "gesperrt", "message": "Der KI-Zugang wurde von der Lehrkraft gesperrt."})
    if not ki.budget_ok():
        return jsonify({"status": "budget_exceeded", "message": "Das Token-Budget für heute ist erschöpft."})
    pruef = ki.ki_pruefen(sid, session.get("klasse", ""), typ)
    if pruef["ok"] and pruef["quelle"] == "gruppe":
        return jsonify({"status": "freigegeben", "quelle": "gruppe", "anfrage_id": None})
    kontext = str(data.get("kontext", ""))[:200]
    now = now_iso()
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO ki_anfragen (schueler_id, typ, kontext, erstellt_at) VALUES (?,?,?,?)", (sid, typ, kontext, now)
        )
        touch_student(db, sid)
        db.commit()
        aid = cur.lastrowid
    emit_lehrer("neue_anfrage", {
        "id": aid, "schueler_id": sid, "pseudonym": session.get("pseudonym", "?"), "klasse": session.get("klasse", "?"),
        "typ": typ, "kontext": kontext, "erstellt_at": now,
    })
    return jsonify({"status": "wartend", "anfrage_id": aid})


def _ki_fehler(exc: Exception, feld: str):
    return jsonify({feld: f"Die KI konnte gerade nicht antworten: {exc}"}), 502


@app.route("/api/chat", methods=["POST"])
@schueler_required
@praesentation_frei
def api_chat():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    pruef = ki.ki_pruefen(sid, session.get("klasse", ""), "chat", data.get("anfrage_id"))
    if not pruef["ok"]:
        return _blockiert(pruef)
    message = str(data.get("message", "")).strip()[:1500]
    if not message:
        return jsonify({"response": "Bitte stelle zuerst eine Frage."}), 400
    if not ki.konfiguriert():
        return jsonify({"response": "Die KI ist noch nicht konfiguriert (GEMINI_API_KEY fehlt). Frag bitte deine Lehrkraft.", "tokens": 0})
    try:
        transcript = []
        for item in (data.get("history") or [])[-8:]:
            role = "KI" if item.get("role") == "assistant" else "Schüler:in"
            transcript.append(f"{role}: {str(item.get('content', ''))[:1200]}")
        transcript.append(f"Schüler:in: {message}")
        kontext = str(data.get("kontext", ""))[:120]
        prompt = f"Aktueller Abschnitt des Arbeitsblatts: {kontext or 'unbekannt'}\nBisheriger Dialog:\n" + "\n".join(transcript)
        response = ki.generate(prompt, ki.SYSTEM_PROMPT)
        reply = (response.text or "").strip() or "Ich konnte gerade keine Antwort formulieren. Versuch es bitte noch einmal."
        tokens = ki.response_token_count(response, message + reply)
    except Exception as exc:  # pragma: no cover - Netzwerk-/API-Fehler
        return _ki_fehler(exc, "response")
    ki.tokens_buchen(sid, tokens, pruef["quelle"], pruef["anfrage"]["id"] if pruef["anfrage"] else None)
    zeit = ki.chat_speichern(sid, "chat", message, reply, tokens)
    emit_lehrer("token_update", ki.budget_payload())
    emit_watch(sid, "chat_live", {"schueler_id": sid, "pseudonym": session.get("pseudonym", "?"), "typ": "chat",
                                  "frage": message[:400], "antwort": reply[:800], "tokens": tokens, "zeit": zeit[11:16]})
    return jsonify({"response": reply, "tokens": tokens})


@app.route("/api/check-answer", methods=["POST"])
@schueler_required
@praesentation_frei
def api_check_answer():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    pruef = ki.ki_pruefen(sid, session.get("klasse", ""), "korrektur", data.get("anfrage_id"))
    if not pruef["ok"]:
        return jsonify({"correct": None, "blocked": True, "feedback": pruef["grund"]})
    answer = str(data.get("answer", "")).strip()[:2500]
    question = str(data.get("question", ""))[:800]
    context = str(data.get("context", ""))[:800]
    if len(answer) < 10:
        return jsonify({"correct": False, "feedback": "Bitte schreibe zuerst eine ausführlichere Antwort.", "hint": ""})
    if not ki.konfiguriert():
        return jsonify({"correct": None, "feedback": "Deine Antwort wurde gespeichert. Für KI-Feedback muss die Lehrkraft den Gemini-Schlüssel eintragen.",
                        "hint": "Vergleiche deine Antwort mit der Lesestrecke des Abschnitts."})
    prompt = f"Aufgabe: {question}\nZusatzkontext: {context}\nSchülerantwort: {answer}"
    try:
        response = ki.generate(prompt, ki.KORREKTUR_PROMPT)
        text = response.text or ""
        result = ki.parse_json_response(text)
        tokens = ki.response_token_count(response, prompt + text)
    except Exception as exc:  # pragma: no cover
        return jsonify({"correct": None, "feedback": f"KI-Feedback derzeit nicht möglich: {exc}", "hint": ""}), 502
    ki.tokens_buchen(sid, tokens, pruef["quelle"], pruef["anfrage"]["id"] if pruef["anfrage"] else None)
    zeit = ki.chat_speichern(sid, "korrektur", f"{question[:200]} → {answer[:600]}", result["feedback"], tokens)
    emit_lehrer("token_update", ki.budget_payload())
    emit_watch(sid, "chat_live", {"schueler_id": sid, "pseudonym": session.get("pseudonym", "?"), "typ": "korrektur",
                                  "frage": f"[KI-Korrektur] {question[:120]} → {answer[:250]}", "antwort": result["feedback"][:800],
                                  "tokens": tokens, "zeit": zeit[11:16]})
    return jsonify(result)


@app.route("/api/zeichnung-analyse", methods=["POST"])
@schueler_required
@praesentation_frei
def api_zeichnung_analyse():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    pruef = ki.ki_pruefen(sid, session.get("klasse", ""), "zeichnung", data.get("anfrage_id"))
    if not pruef["ok"]:
        return jsonify({"sterne": None, "blocked": True, "feedback": pruef["grund"]})
    png = _png_bytes(data.get("png", ""))
    aufgabe = str(data.get("aufgabe", ""))[:600]
    geraet = str(data.get("geraet", ""))[:40]
    niveau = str(data.get("niveau", ""))[:1]
    if not png:
        return jsonify({"sterne": None, "feedback": "Bitte zeichne zuerst etwas."}), 400
    if not ki.konfiguriert():
        return jsonify({"sterne": None, "erkannt": [], "fehlt": [], "feedback": "Die KI ist nicht konfiguriert – deine Zeichnung ist gespeichert."})
    try:
        auftrag = ki.zeichnung_auftrag(geraet, aufgabe, niveau)   # Prüfliste aus zeichenauftraege.py
        response = ki.generate_mit_bild(f"Zeichenauftrag: {auftrag}", png, ki.ZEICHNUNG_PROMPT)
        text = response.text or ""
        result = ki.parse_zeichnung_response(text)
        tokens = ki.response_token_count(response, aufgabe + text)
    except Exception as exc:  # pragma: no cover
        return jsonify({"sterne": None, "feedback": f"KI-Bewertung derzeit nicht möglich: {exc}"}), 502
    ki.tokens_buchen(sid, tokens, pruef["quelle"], pruef["anfrage"]["id"] if pruef["anfrage"] else None)
    zeit = ki.chat_speichern(sid, "zeichnung", f"[Zeichnung] {aufgabe[:300]}", result["feedback"], tokens)
    emit_lehrer("token_update", ki.budget_payload())
    emit_watch(sid, "chat_live", {"schueler_id": sid, "pseudonym": session.get("pseudonym", "?"), "typ": "zeichnung",
                                  "frage": f"[Zeichnung] {aufgabe[:120]}", "antwort": result["feedback"][:800], "tokens": tokens, "zeit": zeit[11:16]})
    return jsonify(result)


@app.route("/api/handschrift", methods=["POST"])
@schueler_required
def api_handschrift():
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    pruef = ki.ki_pruefen(sid, session.get("klasse", ""), "handschrift", data.get("anfrage_id"))
    if not pruef["ok"]:
        return jsonify({"text": None, "blocked": True, "message": pruef["grund"]})
    png = _png_bytes(data.get("png", ""))
    if not png:
        return jsonify({"text": None, "message": "Bitte schreibe zuerst etwas."}), 400
    if not ki.konfiguriert():
        return jsonify({"text": None, "message": "Die KI ist nicht konfiguriert – tippe deine Stichpunkte bitte ein."})
    try:
        response = ki.generate_mit_bild("Transkribiere die Handschrift.", png, ki.HANDSCHRIFT_PROMPT)
        text = (response.text or "").strip()[:2000]
        tokens = ki.response_token_count(response, text)
    except Exception as exc:  # pragma: no cover
        return jsonify({"text": None, "message": f"Handschrifterkennung derzeit nicht möglich: {exc}"}), 502
    ki.tokens_buchen(sid, tokens, pruef["quelle"], pruef["anfrage"]["id"] if pruef["anfrage"] else None)
    zeit = ki.chat_speichern(sid, "handschrift", "[Handschrift]", text, tokens)
    emit_lehrer("token_update", ki.budget_payload())
    emit_watch(sid, "chat_live", {"schueler_id": sid, "pseudonym": session.get("pseudonym", "?"), "typ": "handschrift",
                                  "frage": "[Handschrift erkannt]", "antwort": text[:800], "tokens": tokens, "zeit": zeit[11:16]})
    return jsonify({"text": text, "tokens": tokens})


# ── Lehrer-API ───────────────────────────────────────────────────────────────
def fortsetzung_payload() -> dict:
    status = fortsetzung_status()
    with get_db() as db:
        anfragen = [dict(r) for r in db.execute(
            "SELECT * FROM fortsetzungsanfragen WHERE status='wartend' ORDER BY created_at").fetchall()]
        ziele = [dict(r) for r in db.execute(
            "SELECT z.student_id, z.status, s.pseudonym, s.klasse FROM fortsetzungsziele z "
            "LEFT JOIN schueler s ON s.id=z.student_id ORDER BY s.klasse, s.pseudonym").fetchall()]
        for a in anfragen:
            a.pop("resume_token_hash", None)
            a["kandidaten"] = fortsetzung_kandidaten(db, a["pseudonym"], a["klasse"])
    return {"active": status["active"], "source_name": status["source_name"], "started_at": status["started_at"],
            "anfragen": anfragen, "ziele": ziele}


def iserv_status_payload() -> dict:
    try:
        import iserv_archiv
        return iserv_archiv.status_payload()
    except ImportError:  # pragma: no cover
        return {"konfiguriert": False, "fehler": "Modul fehlt"}


def hakt_payload(limit: int = 8) -> list[dict]:
    """„Woran es hakt“: die Stationen mit den meisten falschen Versuchen der Klasse.

    Gezählt werden nur bewertbare Antworten (korrekt = 0 oder 1). Sortiert nach der Zahl der
    Lernenden mit mindestens einem Fehlversuch, danach nach dem Anteil falscher Versuche.
    """
    with get_db() as db:
        rows = db.execute(
            "SELECT aufgabe_nr, COUNT(*) AS versuche, SUM(korrekt=0) AS falsch, SUM(korrekt=1) AS richtig, "
            "COUNT(DISTINCT schueler_id) AS personen, "
            "COUNT(DISTINCT CASE WHEN korrekt=0 THEN schueler_id END) AS personen_falsch, "
            "MAX(CASE WHEN korrekt=0 THEN frage END) AS beispiel "
            "FROM antworten WHERE korrekt IS NOT NULL GROUP BY aufgabe_nr HAVING SUM(korrekt=0) > 0"
        ).fetchall()
    titel = {a["key"]: a for a in ABSCHNITTE}
    out = []
    for r in rows:
        nr = str(r["aufgabe_nr"])
        abschnitt = titel.get(AUFGABE_ZU_ABSCHNITT.get(nr, ""), {})
        out.append({
            "nr": nr, "anzeige": anzeige_nr(nr), "abschnitt": abschnitt.get("titel", ""), "kurz": abschnitt.get("kurz", ""),
            "versuche": r["versuche"], "falsch": r["falsch"], "richtig": r["richtig"],
            "personen": r["personen"], "personen_falsch": r["personen_falsch"],
            "quote": round(r["falsch"] / r["versuche"], 2), "beispiel": (r["beispiel"] or "")[:140],
        })
    out.sort(key=lambda x: (-x["personen_falsch"], -x["quote"], -x["falsch"]))
    return out[:limit]


def vermutungen_payload(max_saetze: int = 8) -> list[dict]:
    """„Vermutungen der Klasse“: je Forscherfrage die Verteilung der gewählten Optionen und die Sätze der Kinder.

    Gewertet wird die jeweils letzte Vermutung je Kind und Station. Das Protokoll hat die Form
    „Vermutung: <Option> | <Option> · <Satz>“ (Niveau A nur Optionen, B Optionen und Satz, C nur der Satz).
    """
    with get_db() as db:
        rows = db.execute(
            "SELECT a.schueler_id, a.aufgabe_nr, a.niveau, a.frage, a.antwort_text, s.pseudonym FROM antworten a "
            "JOIN schueler s ON s.id = a.schueler_id WHERE a.antwort_typ = 'vermutung' ORDER BY a.id").fetchall()
    letzte = {(r["schueler_id"], r["aufgabe_nr"]): r for r in rows}          # die spätere Vermutung ersetzt die frühere
    gruppen: dict = {}
    for r in letzte.values():
        text = (r["antwort_text"] or "").strip()
        text = text[len("Vermutung:"):].strip() if text.startswith("Vermutung:") else text
        optionen_teil, trenner, satz = text.partition(" · ")
        if not trenner:                                                       # nur eine Sorte: Niveau C ist der freie Satz
            optionen_teil, satz = ("", optionen_teil) if r["niveau"] == "C" else (optionen_teil, "")
        g = gruppen.setdefault(str(r["aufgabe_nr"]), {"nr": str(r["aufgabe_nr"]), "frage": r["frage"], "anzahl": 0, "optionen": {}, "saetze": []})
        g["anzahl"] += 1
        for o in [x.strip() for x in optionen_teil.split(" | ") if x.strip()]:
            g["optionen"][o] = g["optionen"].get(o, 0) + 1
        if satz.strip() and len(g["saetze"]) < max_saetze:
            g["saetze"].append({"pseudonym": r["pseudonym"], "text": satz.strip()[:300]})
    out = []
    for g in gruppen.values():
        verteilung = sorted(({"option": o, "anzahl": n} for o, n in g["optionen"].items()), key=lambda x: (-x["anzahl"], x["option"]))
        out.append({"nr": g["nr"], "anzeige": anzeige_nr(g["nr"]), "frage": g["frage"], "anzahl": g["anzahl"], "verteilung": verteilung, "saetze": g["saetze"]})
    reihenfolge = {n: i for i, n in enumerate(ALLE_AUFGABEN)}
    return sorted(out, key=lambda g: reihenfolge.get(g["nr"], 10**6))


@app.route("/api/lehrer/vermutungen")
@lehrer_required
def api_lehrer_vermutungen():
    return jsonify({"ok": True, "vermutungen": vermutungen_payload()})


@app.route("/api/lehrer/hakt")
@lehrer_required
def api_lehrer_hakt():
    return jsonify({"ok": True, "hakt": hakt_payload()})


@app.route("/api/lehrer/state")
@lehrer_required
def api_lehrer_state():
    return jsonify({
        "ok": True, "schueler": alle_schueler_infos(), "anfragen": offene_anfragen(), "budget": ki.budget_payload(),
        "hakt": hakt_payload(), "vermutungen": vermutungen_payload(),
        "gesperrt": ki.gesperrte_ids(), "gruppenfreigabe": ki.gruppenfreigabe_lesen(),
        "snapshots": dbmod.list_named_snapshots(), "fortsetzung": fortsetzung_payload(), "iserv": iserv_status_payload(),
        "praesentation": praesentation.lesen(),
        "praesentation_bilder": praesentation.bilder_fuer_client(),
    })


@app.route("/api/ki-entscheidung", methods=["POST"])
@lehrer_required
def api_ki_entscheidung():
    data = request.get_json(silent=True) or {}
    try:
        aid = int(data.get("anfrage_id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "anfrage_id fehlt"}), 400
    entscheid = data.get("entscheid")
    if entscheid not in ("freigegeben", "abgelehnt"):
        return jsonify({"ok": False, "error": "ungültige Entscheidung"}), 400
    with get_db() as db:
        row = db.execute("SELECT * FROM ki_anfragen WHERE id=?", (aid,)).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "unbekannte Anfrage"}), 404
        if row["status"] != "wartend":
            return jsonify({"ok": True, "status": row["status"], "already": True})
        db.execute("UPDATE ki_anfragen SET status=?, bearbeitet_at=? WHERE id=?", (entscheid, now_iso(), aid))
        db.commit()
    emit_schueler(row["schueler_id"], "ki_entscheidung", {"anfrage_id": aid, "entscheid": entscheid, "typ": row["typ"]})
    emit_lehrer("anfrage_erledigt", {"anfrage_id": aid, "entscheid": entscheid, "schueler_id": row["schueler_id"]})
    return jsonify({"ok": True, "status": entscheid})


@app.route("/api/lehrer/praesentation")
@lehrer_required
def api_lehrer_praesentation_status():
    return jsonify({"ok": True, "praesentation": praesentation.lesen(),
                    "bilder": praesentation.bilder_fuer_client()})


@app.route("/api/lehrer/praesentation", methods=["POST"])
@lehrer_required
def api_lehrer_praesentation():
    """Bild für alle einblenden oder wieder ausblenden."""
    data = request.get_json(silent=True) or {}
    if data.get("aktiv"):
        try:
            zustand = praesentation.starten(str(data.get("bild", "")), data.get("hinweis", ""))
        except ValueError:
            return jsonify({"ok": False, "error": "unbekanntes Bild"}), 400
        tafel_server.beenden()  # Tafel und Präsentation schließen sich aus
    else:
        zustand = praesentation.beenden()
    # Ein Broadcast an alle verbundenen Lernenden; wer später kommt, bekommt den
    # Zustand über /api/status.
    socketio.emit("praesentation", zustand)
    emit_lehrer("praesentation_update", zustand)
    return jsonify({"ok": True, "praesentation": zustand})


@app.route("/api/lehrer/ki-sperren", methods=["POST"])
@lehrer_required
def api_ki_sperren():
    data = request.get_json(silent=True) or {}
    sid = str(data.get("schueler_id", ""))
    aktion = data.get("aktion", "sperren")
    if not sid:
        return jsonify({"ok": False}), 400
    if aktion == "sperren":
        ki.sperren(sid)
    else:
        ki.entsperren(sid)
    gesperrt = ki.ist_gesperrt(sid)
    emit_schueler(sid, "ki_gesperrt", {"gesperrt": gesperrt})
    emit_lehrer("ki_sperr_status", {"schueler_id": sid, "gesperrt": gesperrt})
    return jsonify({"ok": True, "gesperrt": gesperrt})


@app.route("/api/lehrer/gruppenfreigabe", methods=["POST"])
@lehrer_required
def api_gruppenfreigabe():
    data = request.get_json(silent=True) or {}
    aktion = str(data.get("aktion", ""))
    if aktion == "start":
        gruppe = ki.gruppenfreigabe_setzen(data.get("typen"), data.get("klasse", ""), data.get("minuten", 45),
                                           data.get("token_limit", 0), data.get("per_student_limit", 0))
    elif aktion == "stop":
        gruppe = ki.gruppenfreigabe_beenden()
    elif aktion == "sperren":
        gruppe = ki.gruppe_sperren()
        emit_lehrer("offene_anfragen", offene_anfragen())
    elif aktion == "entsperren":
        gruppe = ki.gruppe_entsperren()
    else:
        return jsonify({"ok": False, "error": "unbekannte Aktion"}), 400
    payload = {"active": gruppe["active"], "locked": gruppe["locked"], "typen": gruppe["typen"], "expires_at": gruppe["expires_at"]}
    socketio.emit("gruppenfreigabe", payload)  # an alle Lernenden-Sockets (ein Broadcast, kein Raumdoppel)
    emit_lehrer("gruppenfreigabe_update", gruppe)
    return jsonify({"ok": True, "gruppenfreigabe": gruppe})


@app.route("/api/lehrer/daten-loeschen", methods=["POST"])
@lehrer_required
def api_daten_loeschen():
    data = request.get_json(silent=True) or {}
    sid = str(data.get("schueler_id", ""))
    if not sid:
        return jsonify({"ok": False}), 400
    dbmod.delete_student(sid)
    tafel_server.person_entfernen(sid)
    presence.drop_student(sid)
    emit_schueler(sid, "sitzung_beendet", {"grund": "geloescht"})
    emit_lehrer("schueler_geloescht", {"id": sid})
    return jsonify({"ok": True})


def _sitzung_ersetzen(grund: str, ids_vorher: list[str]) -> None:
    """Nach Reset/Restore: alte Sockets informieren, Präsenz leeren, Dashboard aktualisieren."""
    for sid in ids_vorher:
        emit_schueler(sid, "sitzung_beendet", {"grund": grund})
    presence.reset()
    tafel_server.neu_laden_und_senden()  # Tafel-Tabellen wurden mit geleert bzw. wiederhergestellt
    emit_lehrer("sitzung_zurueckgesetzt", {"grund": grund})


@app.route("/api/lehrer/sitzung-zuruecksetzen", methods=["POST"])
@lehrer_required
def api_sitzung_zuruecksetzen():
    with get_db() as db:
        ids = [r["id"] for r in db.execute("SELECT id FROM schueler").fetchall()]
    dbmod.clear_live_data()
    _sitzung_ersetzen("zurueckgesetzt", ids)
    return jsonify({"ok": True, "geloescht": len(ids)})


# ── Temporäre Lehrkraft-Snapshots ────────────────────────────────────────────
@app.route("/api/lehrer/snapshots", methods=["GET"])
@lehrer_required
def api_snapshots_list():
    return jsonify({"ok": True, "snapshots": dbmod.list_named_snapshots()})


@app.route("/api/lehrer/snapshots", methods=["POST"])
@lehrer_required
def api_snapshots_save():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()[:60] or f"Zwischenstand {now_iso()[:16].replace('T', ' ')}"
    info = dbmod.save_named_snapshot(name)
    return jsonify({"ok": True, "snapshot": info, "snapshots": dbmod.list_named_snapshots()})


@app.route("/api/lehrer/snapshots/<snapshot_id>/laden", methods=["POST"])
@lehrer_required
def api_snapshots_load(snapshot_id):
    snapshot = dbmod.load_named_snapshot(snapshot_id)
    if not snapshot:
        return jsonify({"ok": False, "error": "Zwischenstand nicht gefunden"}), 404
    with get_db() as db:
        ids_vorher = [r["id"] for r in db.execute("SELECT id FROM schueler").fetchall()]
    try:
        ids = dbmod.restore_snapshot(snapshot, "fortsetzung")
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    _sitzung_ersetzen("ersetzt", ids_vorher)
    emit_lehrer("fortsetzung_update", fortsetzung_payload())
    return jsonify({"ok": True, "lernende": len(ids)})


@app.route("/api/lehrer/snapshots/<snapshot_id>", methods=["DELETE"])
@lehrer_required
def api_snapshots_delete(snapshot_id):
    ok = dbmod.delete_named_snapshot(snapshot_id)
    return jsonify({"ok": ok, "snapshots": dbmod.list_named_snapshots()}), (200 if ok else 404)


# ── Fortsetzungsstunde ───────────────────────────────────────────────────────
def _fortsetzung_zuordnen(db, anfrage, target_id: str) -> bool:
    ziel = db.execute("SELECT status FROM fortsetzungsziele WHERE student_id=?", (target_id,)).fetchone()
    if not ziel or ziel["status"] != "verfuegbar":
        return False
    db.execute("UPDATE schueler SET resume_token_hash=?, last_active=? WHERE id=?", (anfrage["resume_token_hash"], now_iso(), target_id))
    db.execute("DELETE FROM schueler WHERE id=?", (anfrage["new_student_id"],))
    db.execute("UPDATE fortsetzungsziele SET status='vergeben' WHERE student_id=?", (target_id,))
    db.execute("UPDATE fortsetzungsanfragen SET status='zugeordnet', target_student_id=?, decided_at=? WHERE id=?",
               (target_id, now_iso(), anfrage["id"]))
    return True


@app.route("/api/lehrer/fortsetzung/auto", methods=["POST"])
@lehrer_required
def api_fortsetzung_auto():
    """Eindeutige Treffer (Pseudonym, bei Gleichstand + Klasse) in einer Sammelaktion übernehmen."""
    payload = fortsetzung_payload()
    zugeordnet, mehrdeutig, ohne = [], [], []
    with get_db() as db:
        for a in payload["anfragen"]:
            if len(a["kandidaten"]) == 1:
                anfrage = db.execute("SELECT * FROM fortsetzungsanfragen WHERE id=?", (a["id"],)).fetchone()
                if anfrage and _fortsetzung_zuordnen(db, anfrage, a["kandidaten"][0]):
                    zugeordnet.append((a["new_student_id"], a["kandidaten"][0]))
            elif a["kandidaten"]:
                mehrdeutig.append(a["id"])
            else:
                ohne.append(a["id"])
        db.commit()
    for new_id, target in zugeordnet:
        emit_schueler(new_id, "fortsetzung_zugeordnet", {"status": "zugeordnet", "schueler_id": target})
    emit_lehrer("fortsetzung_update", fortsetzung_payload())
    return jsonify({"ok": True, "zugeordnet": len(zugeordnet), "mehrdeutig": len(mehrdeutig), "ohne_treffer": len(ohne)})


@app.route("/api/lehrer/fortsetzung/zuordnen", methods=["POST"])
@lehrer_required
def api_fortsetzung_zuordnen():
    data = request.get_json(silent=True) or {}
    anfrage_id = str(data.get("anfrage_id", ""))
    aktion = str(data.get("aktion", "zuordnen"))
    target = str(data.get("target_student_id", ""))
    with get_db() as db:
        anfrage = db.execute("SELECT * FROM fortsetzungsanfragen WHERE id=? AND status='wartend'", (anfrage_id,)).fetchone()
        if not anfrage:
            return jsonify({"ok": False, "error": "Anfrage nicht (mehr) offen"}), 404
        if aktion == "zuordnen":
            if not _fortsetzung_zuordnen(db, anfrage, target):
                return jsonify({"ok": False, "error": "Dieser Lernplatz ist nicht (mehr) verfügbar."}), 409
            status, neue_id = "zugeordnet", target
        elif aktion == "ablehnen":
            db.execute("UPDATE fortsetzungsanfragen SET status='abgelehnt', decided_at=? WHERE id=?", (now_iso(), anfrage_id))
            db.execute("DELETE FROM schueler WHERE id=?", (anfrage["new_student_id"],))
            status, neue_id = "abgelehnt", None
        elif aktion == "neustart":
            db.execute("UPDATE fortsetzungsanfragen SET status='neustart', decided_at=? WHERE id=?", (now_iso(), anfrage_id))
            status, neue_id = "neustart", anfrage["new_student_id"]
        else:
            return jsonify({"ok": False, "error": "unbekannte Aktion"}), 400
        db.commit()
    emit_schueler(anfrage["new_student_id"], "fortsetzung_zugeordnet", {"status": status, "schueler_id": neue_id})
    emit_lehrer("fortsetzung_update", fortsetzung_payload())
    if status == "neustart":
        emit_lehrer("neuer_schueler", get_schueler_info(neue_id))
    return jsonify({"ok": True, "status": status})


@app.route("/api/lehrer/fortsetzung/beenden", methods=["POST"])
@lehrer_required
def api_fortsetzung_beenden():
    """Beendet den Fortsetzungsmodus, ohne verbundene Lernplätze zu löschen."""
    with get_db() as db:
        wartend = [dict(r) for r in db.execute("SELECT * FROM fortsetzungsanfragen WHERE status='wartend'").fetchall()]
        db.execute("UPDATE fortsetzungsanfragen SET status='neustart', decided_at=? WHERE status='wartend'", (now_iso(),))
        db.execute("UPDATE fortsetzungsstatus SET active=0 WHERE id=1")
        db.execute("DELETE FROM fortsetzungsziele")
        db.commit()
    for a in wartend:
        emit_schueler(a["new_student_id"], "fortsetzung_zugeordnet", {"status": "neustart", "schueler_id": a["new_student_id"]})
    emit_lehrer("fortsetzung_update", fortsetzung_payload())
    return jsonify({"ok": True, "neustarts": len(wartend)})


@app.route("/api/fortsetzung/status", methods=["GET", "POST"])
def api_fortsetzung_status():
    """Warteseite: pollt, bis die Lehrkraft zugeordnet hat oder der Fortsetzungsmodus aktiv ist."""
    data = request.get_json(silent=True) or {}
    sid = session.get("schueler_id") or str(data.get("schueler_id") or request.args.get("schueler_id") or "")
    token = session.get("resume_token") or str(data.get("token") or request.args.get("token") or "")
    status = fortsetzung_status()
    if not sid:
        return jsonify({"ok": True, "status": "unbekannt", "aktiv": status["active"]})
    with get_db() as db:
        anfrage = db.execute("SELECT * FROM fortsetzungsanfragen WHERE new_student_id=? ORDER BY created_at DESC LIMIT 1", (sid,)).fetchone()
        row = db.execute("SELECT id, pseudonym, klasse, resume_token_hash FROM schueler WHERE id=?", (sid,)).fetchone()
    if anfrage and anfrage["status"] == "wartend":
        return jsonify({"ok": True, "status": "wartend", "aktiv": status["active"]})
    if anfrage and anfrage["status"] == "zugeordnet":
        ziel = anfrage["target_student_id"]
        if token and secrets.compare_digest(token_hash(token), anfrage["resume_token_hash"]):
            with get_db() as db:
                zrow = db.execute("SELECT pseudonym, klasse FROM schueler WHERE id=?", (ziel,)).fetchone()
            if zrow:
                session.update({"schueler_id": ziel, "pseudonym": zrow["pseudonym"], "klasse": zrow["klasse"], "resume_token": token})
                return jsonify({"ok": True, "status": "zugeordnet", "schueler_id": ziel, "redirect": url_for("arbeitsblatt")})
        return jsonify({"ok": True, "status": "zugeordnet", "schueler_id": ziel})
    if anfrage and anfrage["status"] == "neustart" and row:
        return jsonify({"ok": True, "status": "neustart", "schueler_id": sid, "redirect": url_for("arbeitsblatt")})
    if anfrage and anfrage["status"] == "abgelehnt":
        return jsonify({"ok": True, "status": "abgelehnt"})
    # Lernplatz mit Token wartet auf eine Fortsetzung, die die Lehrkraft noch nicht gestartet hat
    if row and row["resume_token_hash"] and token and secrets.compare_digest(token_hash(token), row["resume_token_hash"]):
        with get_db() as db:
            db.execute("UPDATE fortsetzungsziele SET status='vergeben' WHERE student_id=? AND status='verfuegbar'", (sid,))
            touch_student(db, sid)
            db.commit()
        session.update({"schueler_id": sid, "pseudonym": row["pseudonym"], "klasse": row["klasse"], "resume_token": token})
        if status["active"]:
            emit_lehrer("fortsetzung_update", fortsetzung_payload())
        return jsonify({"ok": True, "status": "verbunden", "schueler_id": sid, "redirect": url_for("arbeitsblatt")})
    return jsonify({"ok": True, "status": "inaktiv" if not status["active"] else "unbekannt", "aktiv": status["active"]})


# ── Gegatete Lesestrecke (Lösungen nur auf dem Server) ───────────────────────
import inhalte_server  # noqa: E402
import iserv_archiv  # noqa: E402
from config import LESE_SPERRE_SEKUNDEN  # noqa: E402


def _lesestrecke_status(db, sid: str, key: str) -> dict:
    row = db.execute("SELECT phase, fertig, retry_until, versuche FROM lesestrecke_status WHERE schueler_id=? AND abschnitt=?", (sid, key)).fetchone()
    if not row:
        return {"phase": 0, "fertig": False, "retry_until": 0.0, "versuche": 0}
    return {"phase": int(row["phase"]), "fertig": bool(row["fertig"]), "retry_until": float(row["retry_until"] or 0), "versuche": int(row["versuche"])}


@app.route("/api/lesestrecke/<abschnitt>")
@schueler_required
def api_lesestrecke(abschnitt):
    if abschnitt not in inhalte_server.LESESTRECKEN:
        return jsonify({"ok": False, "error": "unbekannter Abschnitt"}), 404
    sid = session["schueler_id"]
    with get_db() as db:
        status = _lesestrecke_status(db, sid, abschnitt)
    return jsonify(dict(inhalte_server.lesestrecke_fuer_client(abschnitt, status), ok=True))


@app.route("/api/lesestrecke/<abschnitt>/antwort", methods=["POST"])
@schueler_required
@praesentation_frei
def api_lesestrecke_antwort(abschnitt):
    if abschnitt not in inhalte_server.LESESTRECKEN:
        return jsonify({"ok": False, "error": "unbekannter Abschnitt"}), 404
    sid = session["schueler_id"]
    data = request.get_json(silent=True) or {}
    strecke = inhalte_server.LESESTRECKEN[abschnitt]
    try:
        phase, wahl = int(data.get("phase")), int(data.get("wahl"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "phase und wahl fehlen"}), 400
    if not 0 <= phase < len(strecke["abschnitte"]) or not 0 <= wahl < len(strecke["abschnitte"][phase]["optionen"]):
        return jsonify({"ok": False, "error": "ungültige Auswahl"}), 400
    now = now_iso()
    jetzt = time.time()
    with get_db() as db:
        status = _lesestrecke_status(db, sid, abschnitt)
        if status["fertig"] or phase != status["phase"]:
            return jsonify({"ok": False, "error": "Diese Phase ist nicht aktiv.", "status": status}), 409
        if status["retry_until"] > jetzt:
            return jsonify({"ok": False, "error": "Noch gesperrt.", "status": status}), 429
        korrekt, erklaerung = inhalte_server.pruefen(abschnitt, phase, wahl)
        frage_text = strecke["abschnitte"][phase]["frage"]
        antwort_text = strecke["abschnitte"][phase]["optionen"][wahl]
        versuch = db.execute("SELECT COUNT(*) AS n FROM antworten WHERE schueler_id=? AND aufgabe_nr=?", (sid, strecke["station"])).fetchone()["n"] + 1
        db.execute(
            "INSERT INTO antworten (schueler_id, aufgabe_nr, niveau, antwort_typ, frage, antwort_text, korrekt, versuch_nr, erstellt_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (sid, strecke["station"], "A", "lesestrecke", f"Abschnitt {phase + 1}: {frage_text}", antwort_text, 1 if korrekt else 0, versuch, now),
        )
        if korrekt:
            status["phase"] = phase + 1
            status["retry_until"] = 0.0
            status["fertig"] = status["phase"] >= len(strecke["abschnitte"])
            if status["fertig"]:
                db.execute("INSERT OR IGNORE INTO fortschritt (schueler_id, aufgabe_nr, niveau, erledigt_at) VALUES (?,?,?,?)", (sid, strecke["station"], "A", now))
        else:
            status["versuche"] += 1
            status["retry_until"] = jetzt + LESE_SPERRE_SEKUNDEN[min(status["versuche"] - 1, len(LESE_SPERRE_SEKUNDEN) - 1)]
        db.execute(
            "INSERT INTO lesestrecke_status (schueler_id, abschnitt, phase, fertig, retry_until, versuche) VALUES (?,?,?,?,?,?) "
            "ON CONFLICT(schueler_id, abschnitt) DO UPDATE SET phase=excluded.phase, fertig=excluded.fertig, retry_until=excluded.retry_until, versuche=excluded.versuche",
            (sid, abschnitt, status["phase"], int(status["fertig"]), status["retry_until"], status["versuche"]),
        )
        touch_student(db, sid)
        db.commit()
    emit_watch(sid, "antwort_live", {"schueler_id": sid, "aufgabe_nr": strecke["station"], "anzeige": anzeige_label(strecke["station"]), "niveau": "A", "typ": "lesestrecke",
                                     "frage": frage_text, "antwort": antwort_text, "korrekt": 1 if korrekt else 0, "versuch_nr": versuch, "zeit": now[11:16]})
    if korrekt and status["fertig"]:
        info = get_schueler_info(sid)
        info["aufgaben_neu"] = [{"nr": strecke["station"], "anzeige": anzeige_nr(strecke["station"]), "niveau": "A"}]
        emit_lehrer("fortschritt_update", info)
    return jsonify({"ok": True, "korrekt": korrekt, "erklaerung": erklaerung, "status": status, "station": strecke["station"]})


import glossar  # noqa: E402


def schueler_oder_lehrer_required(func):
    """Nur-Lese-Inhalte, die Lernende und die Lehrkraft (Prüfmodus) brauchen."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if ist_lehrer() or session.get("schueler_id"):
            return func(*args, **kwargs)
        return jsonify({"ok": False, "error": "nicht angemeldet"}), 401

    return wrapper


@app.route("/api/glossar")
@schueler_oder_lehrer_required
def api_glossar():
    return jsonify(dict(glossar.glossar_fuer_client(), ok=True))


# ── Prüfmodus: die Lehrkraft sieht das ganze Arbeitsblatt offen, ohne etwas zu speichern ──
@app.route("/lehrer/pruefen")
@lehrer_required
def lehrer_pruefen():
    token = request.headers.get("X-Lehrer-Token") or session.get("lehrer_token", "")
    return render_template(
        "index.html",
        pruefmodus=True, lehrer_token=token,
        pseudonym="Prüfmodus", klasse="—", schueler_id="", resume_token="", abschnitte=ABSCHNITTE,
        aufgaben_gesamt=len(ALLE_AUFGABEN), app_id=APP_ID, schema_version=STATE_SCHEMA_VERSION,
        titel=APP_TITEL, fach=APP_FACH, v=ASSET_VERSION, einstiegsbild=praesentation.BILDER["einstieg"]["datei"],
    )


@app.route("/api/lehrer/pruefen/lesestrecken")
@lehrer_required
def api_lehrer_pruefen_lesestrecken():
    return jsonify({"ok": True, "lesestrecken": {k: inhalte_server.lesestrecke_vollstaendig(k) for k in inhalte_server.LESESTRECKEN}})


# ── IServ-Archiv ─────────────────────────────────────────────────────────────
def _iserv_client():
    return iserv_archiv.make_client()


@app.route("/api/lehrer/iserv/status")
@lehrer_required
def api_iserv_status():
    return jsonify(iserv_archiv.status_payload())


@app.route("/api/lehrer/iserv/test", methods=["POST"])
@lehrer_required
def api_iserv_test():
    try:
        return jsonify(_iserv_client().test_verbindung())
    except iserv_archiv.IServConfigError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except iserv_archiv.IServFehler as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502


@app.route("/api/lehrer/iserv/abschluss", methods=["POST"])
@lehrer_required
def api_iserv_abschluss():
    """Sitzungsabschluss: Flush → Snapshot → Verschlüsseln → PUT → GET → Prüfen → erst dann bereinigen."""
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()[:60] or "Sitzung"
    try:
        client = _iserv_client()
    except iserv_archiv.IServConfigError as exc:
        return jsonify({"ok": False, "error": str(exc), "geloescht": False}), 400
    with get_db() as db:
        ids_vorher = [r["id"] for r in db.execute("SELECT id FROM schueler").fetchall()]
    try:
        protokoll = iserv_archiv.abschluss_durchfuehren(name, request_flush, dbmod.build_snapshot, dbmod.cleanup_after_archive, client)
    except (iserv_archiv.IServFehler, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc), "geloescht": False}), 502
    for sid in ids_vorher:
        emit_schueler(sid, "sitzung_beendet", {"grund": "archiviert"})
    presence.reset()
    tafel_server.neu_laden_und_senden()
    emit_lehrer("sitzung_zurueckgesetzt", {"grund": "archiviert"})
    emit_lehrer("fortsetzung_update", fortsetzung_payload())
    emit_lehrer("gruppenfreigabe_update", ki.gruppenfreigabe_lesen())
    return jsonify({"ok": True, "protokoll": protokoll})


@app.route("/api/lehrer/iserv/archive")
@lehrer_required
def api_iserv_archive():
    try:
        archive = iserv_archiv.liste_archive(_iserv_client(), legacy_pruefen=request.args.get("legacy") == "1")
    except iserv_archiv.IServConfigError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except iserv_archiv.IServFehler as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502
    return jsonify({"ok": True, "archive": archive})


@app.route("/api/lehrer/iserv/vorschau", methods=["POST"])
@lehrer_required
def api_iserv_vorschau():
    data = request.get_json(silent=True) or {}
    name = str(data.get("dateiname", ""))
    try:
        client = _iserv_client()
        umschlag, groesse = iserv_archiv.archiv_laden_und_pruefen(client, name)
    except iserv_archiv.IServConfigError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except iserv_archiv.IServFehler as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True, "archiv": iserv_archiv._zusammenfassung(umschlag, name, groesse)})


@app.route("/api/lehrer/iserv/wiederherstellen", methods=["POST"])
@lehrer_required
def api_iserv_wiederherstellen():
    data = request.get_json(silent=True) or {}
    name = str(data.get("dateiname", ""))
    modus = str(data.get("modus", ""))
    if modus not in ("ansicht", "fortsetzung"):
        return jsonify({"ok": False, "error": "Modus muss 'ansicht' oder 'fortsetzung' sein."}), 400
    try:
        client = _iserv_client()
        umschlag, _ = iserv_archiv.archiv_laden_und_pruefen(client, name)
    except iserv_archiv.IServConfigError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except iserv_archiv.IServFehler as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    snapshot = dict(umschlag["snapshot"], name=umschlag.get("name") or name)
    with get_db() as db:
        ids_vorher = [r["id"] for r in db.execute("SELECT id FROM schueler").fetchall()]
    try:
        ids = dbmod.restore_snapshot(snapshot, modus)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    _sitzung_ersetzen("ersetzt", ids_vorher)
    emit_lehrer("fortsetzung_update", fortsetzung_payload())
    emit_lehrer("gruppenfreigabe_update", ki.gruppenfreigabe_lesen())
    return jsonify({"ok": True, "lernende": len(ids), "modus": modus})


@app.route("/api/lehrer/iserv/loeschen", methods=["POST"])
@lehrer_required
def api_iserv_loeschen():
    data = request.get_json(silent=True) or {}
    name = str(data.get("dateiname", ""))
    try:
        iserv_archiv.archiv_loeschen(_iserv_client(), name)
    except iserv_archiv.IServConfigError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except iserv_archiv.IServFehler as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True})


# ── Socket.IO ────────────────────────────────────────────────────────────────
@socketio.on("schueler_join")
def on_schueler_join(_data=None):
    sid = session.get("schueler_id")
    if not sid:
        return
    with get_db() as db:
        cur = db.execute("UPDATE schueler SET socket_id=?, last_active=? WHERE id=?", (request.sid, now_iso(), sid))
        db.commit()
    if not cur.rowcount:
        emit("sitzung_beendet", {"grund": "unbekannt"})
        return
    join_room(f"schueler_{sid}")
    became_online = presence.add(sid, request.sid)
    gruppe = ki.gruppenfreigabe_lesen()
    emit("ki_gesperrt", {"gesperrt": ki.ist_gesperrt(sid) or gruppe["locked"]})
    emit("gruppenfreigabe", {"active": gruppe["active"], "locked": gruppe["locked"], "typen": gruppe["typen"], "expires_at": gruppe["expires_at"]})
    if became_online:
        emit_lehrer("schueler_online", get_schueler_info(sid))


@socketio.on("autosave_ack")
def on_autosave_ack(data=None):
    sid = presence.student_connection_owners.get(request.sid)
    if not sid:
        return
    with _flush_lock:
        _flush_acks[sid] = int((data or {}).get("revision") or 0)


@socketio.on("lehrer_join")
def on_lehrer_join(data=None):
    token = (data or {}).get("token") if isinstance(data, dict) else None
    if not (lehrer_token_gueltig(token) or (session.get("is_lehrer") and lehrer_token_gueltig(session.get("lehrer_token")))):
        return
    join_room("lehrer_room")
    emit("alle_schueler", alle_schueler_infos())
    emit("token_update", ki.budget_payload())
    emit("offene_anfragen", offene_anfragen())
    emit("sperr_status_all", {"gesperrt": ki.gesperrte_ids()})
    emit("gruppenfreigabe_update", ki.gruppenfreigabe_lesen())
    emit("fortsetzung_update", fortsetzung_payload())


@socketio.on("watch_schueler")
def on_watch_schueler(data):
    token = (data or {}).get("token") if isinstance(data, dict) else None
    if not (lehrer_token_gueltig(token) or (session.get("is_lehrer") and lehrer_token_gueltig(session.get("lehrer_token")))):
        return
    sid = str((data or {}).get("schueler_id", ""))
    if sid:
        join_room(f"watch_{sid}")
        emit("ki_sperr_status", {"schueler_id": sid, "gesperrt": ki.ist_gesperrt(sid)})


@socketio.on("disconnect")
def on_disconnect(*_args):
    sid, went_offline = presence.remove(request.sid)
    if not sid:
        return
    if went_offline:
        with get_db() as db:
            db.execute("UPDATE schueler SET socket_id=NULL, last_active=? WHERE id=?", (now_iso(), sid))
            db.commit()
        emit_lehrer("schueler_offline", {"id": sid})


dbmod.init_db()
presence.reset()


# ── Tafel (Baustein tafel/, Anbindung tafel_anbindung.py) ─────────────────────
def _praesentation_fuer_tafel_beenden() -> None:
    if praesentation.aktiv():
        zustand = praesentation.beenden()
        socketio.emit("praesentation", zustand)
        emit_lehrer("praesentation_update", zustand)


tafel_server = tafel_anbindung.einbinden(
    app, socketio, lehrer_token_gueltig=lehrer_token_gueltig, lehrer_required=lehrer_required, ist_lehrer=ist_lehrer,
    praesentation_beenden=_praesentation_fuer_tafel_beenden, asset_version=ASSET_VERSION, titel=APP_TITEL)


if __name__ == "__main__":
    import os
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")),
                 debug=os.environ.get("FLASK_DEBUG", "0") == "1", allow_unsafe_werkzeug=True)
