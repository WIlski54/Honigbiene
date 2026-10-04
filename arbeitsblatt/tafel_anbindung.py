"""Anbindung des Tafel-Bausteins (Paket `tafel/`) an dieses Arbeitsblatt.

Hier – und nur hier – steht, was die Tafel über dieses AB wissen muss:
- Wer ist wer? Lernende über die Flask-Session, die Lehrkraft über ihr Aktionstoken.
- Wo wird gespeichert? In der AB-Datenbank (Tabellen tafel_zustand/tafel_dateien) –
  damit landet die Tafel automatisch in Snapshot, IServ-Archiv und Fortsetzungsstunde.
- Aufgaben/Lösungen liegen hier im Browser (static/js/inhalte*.js) → Browser-Adapter
  static/js/tafel_adapter.js; der Server braucht deshalb keinen Aufgaben-Adapter.
- Tafel und Präsentationsmodus schließen sich gegenseitig aus.
"""
import json

from flask import jsonify, render_template, session

from db import get_db
from tafel import LEHRKRAFT, Person, TafelHost, init_tafel
from tafel.speicher import SqliteSpeicher


class ABHost(TafelHost):
    ab = None  # Browser-Adapter (inhalte.js)

    def __init__(self, lehrer_token_gueltig, praesentation_beenden):
        self.speicher = SqliteSpeicher(get_db)
        self._token_gueltig = lehrer_token_gueltig
        self._praesentation_beenden = praesentation_beenden

    def _schueler_aus_session(self):
        sid = session.get("schueler_id")
        return self.schueler(sid) if sid else None

    def person_socket(self, auth):
        token = auth.get("lehrer_token")
        if token and self._token_gueltig(token):
            return LEHRKRAFT
        return self._schueler_aus_session()

    def person_http(self, anfrage):
        token = anfrage.headers.get("X-Lehrer-Token")
        if token and self._token_gueltig(token):
            return LEHRKRAFT
        return self._schueler_aus_session()

    def schueler(self, schueler_id):
        if not schueler_id:
            return None
        with get_db() as db:
            zeile = db.execute("SELECT id, pseudonym, klasse FROM schueler WHERE id=?", (str(schueler_id),)).fetchone()
        return Person(zeile["id"], "schueler", zeile["pseudonym"], zeile["klasse"]) if zeile else None

    def schueler_liste(self):
        with get_db() as db:
            zeilen = db.execute("SELECT id, pseudonym, klasse FROM schueler ORDER BY pseudonym").fetchall()
        return [Person(z["id"], "schueler", z["pseudonym"], z["klasse"]) for z in zeilen]

    def vor_start(self):
        self._praesentation_beenden()


def einbinden(app, socketio, *, lehrer_token_gueltig, lehrer_required, ist_lehrer, praesentation_beenden, asset_version, titel):
    """Tafel einhängen und die Lehrer-Seiten registrieren. Gibt den TafelServer zurück."""
    server = init_tafel(app, socketio, ABHost(lehrer_token_gueltig, praesentation_beenden))

    @app.route("/lehrer/tafel")
    @lehrer_required
    def tafel_lehrer():
        return render_template("tafel_lehrer.html", lehrer_token=session.get("lehrer_token", ""), v=asset_version, titel=titel)

    @app.route("/lehrer/tafel/rueckblick")
    @lehrer_required
    def tafel_rueckblick():
        return render_template("tafel_rueckblick.html", lehrer_token=session.get("lehrer_token", ""), v=asset_version, titel=titel)

    @app.route("/lehrer/tafel/beamer")
    @lehrer_required
    def tafel_beamer():
        return render_template("tafel_beamer.html", lehrer_token=session.get("lehrer_token", ""), v=asset_version, titel=titel)

    @app.route("/tafel/api/lehrer/arbeitsstand/<sid>")
    def tafel_arbeitsstand(sid):
        """Arbeitsstand eines Lernplatzes – der Browser-Adapter baut daraus AB-Karten (Lehrkraft holt Antwort)."""
        if not ist_lehrer():
            return jsonify({"ok": False, "grund": "Nur für die Lehrkraft."}), 401
        with get_db() as db:
            zeile = db.execute("SELECT state_json FROM arbeitsstaende WHERE schueler_id=?", (sid,)).fetchone()
        return jsonify({"ok": True, "state": json.loads(zeile["state_json"]) if zeile else {}})

    return server
