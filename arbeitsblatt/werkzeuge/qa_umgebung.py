"""Sichere Umgebung für die Browser-QA: Wegwerf-Datenbank, kein KI-Schlüssel, Port 5080.

Hintergrund (references/fallstricke.md): Ein zweiter Server für die Browserprobe zog GEMINI_API_KEY aus der echten
.env und löste einen bezahlten Aufruf aus. `setzen()` überschreibt den Schlüssel deshalb immer mit einem leeren Wert
(python-dotenv überschreibt vorhandene Variablen nicht) und legt die Datenbank unter werkzeuge/ausgabe/ ab
(wird von .gitignore ausgenommen). Port 5060 und 5061 sperren die Browser – nie benutzen.

Wird von qa_server.py und lehrer_api.py vor dem Import von config/app benutzt.
"""
import os

ORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ausgabe")


def setzen() -> None:
    os.makedirs(ORDNER, exist_ok=True)
    os.environ["GEMINI_API_KEY"] = ""                                   # niemals echte KI-Aufrufe in der QA
    os.environ.setdefault("DB_PATH", os.path.join(ORDNER, "qa.db"))     # Wegwerf-Datei, nie data/honigbiene.db
    os.environ.setdefault("SECRET_KEY", "qa-secret-nur-lokal")          # nur für lokale Proben; lehrer_api.py nutzt denselben
    os.environ.setdefault("LEHRER_PASSWORD", "qa-nicht-benutzen")       # das Passwortformular wird in der QA nie benutzt
    os.environ.setdefault("PORT", "5080")
