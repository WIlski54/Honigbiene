"""Lehrer-APIs ohne Passwortformular ansprechen – für die Browser- und Konsolen-QA.

Hintergrund: In der Browserprobe darf nie ein Passwort in das Lehrerformular getippt
werden (Produktionsstandard). Stattdessen wird ein Aktionstoken direkt in die QA-Datenbank
geschrieben und im Header `X-Lehrer-Token` mitgeschickt.

Aufruf:
    python werkzeuge/lehrer_api.py token                      # Token anlegen und ausgeben
    python werkzeuge/lehrer_api.py get  /api/lehrer/state
    python werkzeuge/lehrer_api.py post /api/lehrer/snapshots '{"name": "Stunde 1"}'

Die Basis-URL kommt aus QA_BASE_URL (Standard: http://localhost:5080).
Die Datenbank ist standardmäßig werkzeuge/ausgabe/qa.db (qa_umgebung.py), also die des QA-Servers
(python werkzeuge/qa_server.py). Mit DB_PATH=… lässt sich eine andere Wegwerf-Datei wählen.
"""

import hashlib
import json
import os
import secrets
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qa_umgebung   # noqa: E402
qa_umgebung.setzen()   # Wegwerf-DB, kein KI-Schlüssel – nie die echte Datenbank (data/honigbiene.db)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_ID, DB_PATH   # noqa: E402

BASIS = os.environ.get("QA_BASE_URL", "http://localhost:5080").rstrip("/")


def token_anlegen() -> str:
    """Legt ein Aktionstoken an – gespeichert wird nur sein Hash, wie beim echten Login."""
    token = secrets.token_urlsafe(32)
    gehasht = hashlib.sha256(f"{APP_ID}:{token}".encode()).hexdigest()
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT OR REPLACE INTO lehrer_tokens (token_hash, created_at) VALUES (?, ?)",
                (gehasht, datetime.now(timezone.utc).isoformat(timespec="seconds")))
    con.commit()
    con.close()
    return token


def ruf(pfad: str, token: str, daten=None):
    # Git Bash macht aus „/api/...“ gern einen Windows-Pfad. Deshalb ist auch die
    # Schreibweise ohne führenden Schrägstrich erlaubt („api/lehrer/state“).
    pfad = "/" + pfad.lstrip("/")
    req = urllib.request.Request(
        BASIS + pfad,
        data=json.dumps(daten).encode() if daten is not None else None,
        headers={"X-Lehrer-Token": token, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST" if daten is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def session_cookie() -> str:
    """Signiertes Flask-Session-Cookie mit Lehrer-Rolle – für die Browser-QA.

    So lässt sich das Dashboard im Browser ansehen, ohne ein Passwort in ein
    Formular zu tippen. Funktioniert nur mit dem SECRET_KEY dieser Installation.
    """
    import app as appmodule
    from flask.sessions import SecureCookieSessionInterface

    token = token_anlegen()
    serializer = SecureCookieSessionInterface().get_signing_serializer(appmodule.app)
    if serializer is None:
        raise RuntimeError("SECRET_KEY fehlt")
    return serializer.dumps({"is_lehrer": True, "lehrer_token": token})


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    befehl = sys.argv[1]
    if befehl == "token":
        print(token_anlegen())
        return
    if befehl == "cookie":
        print(session_cookie())
        return
    token = os.environ.get("QA_LEHRER_TOKEN") or token_anlegen()
    pfad = sys.argv[2]
    daten = json.loads(sys.argv[3]) if len(sys.argv) > 3 else (None if befehl == "get" else {})
    status, antwort = ruf(pfad, token, daten)
    print(status)
    print(json.dumps(antwort, ensure_ascii=False, indent=2)[:4000])


if __name__ == "__main__":
    main()
