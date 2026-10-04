"""Startet das Arbeitsblatt für die Browser-QA: Port 5080, Wegwerf-Datenbank, KI aus.

    python werkzeuge/qa_server.py            # http://localhost:5080  (Datenbank: werkzeuge/ausgabe/qa.db)
    DB_PATH=/pfad/neu.db python werkzeuge/qa_server.py     # andere Wegwerf-Datei

Lehrkraft in der Browserprobe NUR per Aktionstoken bzw. signiertem Cookie (python werkzeuge/lehrer_api.py cookie),
nie das Passwortformular benutzen. Zum Zurücksetzen die Datei werkzeuge/ausgabe/qa.db löschen.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qa_umgebung  # noqa: E402

qa_umgebung.setzen()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as ab  # noqa: E402

if __name__ == "__main__":
    port = int(os.environ["PORT"])
    print(f"QA-Server: http://localhost:{port} · DB {os.environ['DB_PATH']} · KI aus")
    ab.socketio.run(ab.app, host="127.0.0.1", port=port, allow_unsafe_werkzeug=True)
