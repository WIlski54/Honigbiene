"""Konfiguration und Konstanten des interaktiven Arbeitsblatts „Die Honigbiene – ein Nutztier mit eigenem Staat“.

Alle Secrets kommen ausschließlich aus Umgebungsvariablen (Runtime). Nichts davon
darf im Repository oder in Build-Argumenten stehen.
"""

import os
import re
import secrets
import warnings

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH") or os.path.join(BASE_DIR, "data", "honigbiene.db")

# Stabile, eindeutige Kennung dieses Arbeitsblatts. Nie mehr ändern: Sie bindet
# Resume-Token-Hashes, Autosave-Zustände und IServ-Archive an genau diese App.
APP_ID = "gsm-nw-honigbiene-6"
APP_TITEL = "Die Honigbiene – ein Nutztier mit eigenem Staat"
APP_FACH = "NW · Klasse 6"
STATE_SCHEMA_VERSION = 1      # Zustandsvertrag collectBackup()/applyBackupData()
DB_SCHEMA_VERSION = 2         # additive Migrationen
ARCHIV_FORMAT = "gsm-iabackup"
STATE_MAX_BYTES = 2 * 1024 * 1024
SNAPSHOT_MAX_BYTES = 25 * 1024 * 1024
ASSET_VERSION = "20261004g"

# ── Lehrkraft und Sitzung ────────────────────────────────────────────────────
LEHRER_PASSWORD = os.environ.get("LEHRER_PASSWORD", "").strip()
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
if not SECRET_KEY:
    # Ohne festen Schlüssel sind Sessions nach jedem Neustart ungültig. Für die
    # lokale Entwicklung tolerierbar, in Coolify muss SECRET_KEY gesetzt sein.
    SECRET_KEY = secrets.token_hex(32)
    warnings.warn("SECRET_KEY ist nicht gesetzt – es wird ein flüchtiger Schlüssel verwendet.", stacklevel=1)
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "threading")

# ── KI ───────────────────────────────────────────────────────────────────────
AI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview").strip() or "gemini-3-flash-preview"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
DAILY_TOKEN_LIMIT = int(os.environ.get("DAILY_TOKEN_LIMIT", "50000"))
AI_REQUEST_TYPES = ("chat", "korrektur", "zeichnung", "handschrift")

# ── IServ-WebDAV (optional) ─────────────────────────────────────────────────
ISERV_WEBDAV_URL = os.environ.get("ISERV_WEBDAV_URL", "").strip()
ISERV_WEBDAV_USERNAME = os.environ.get("ISERV_WEBDAV_USERNAME", "").strip()
ISERV_WEBDAV_PASSWORD = os.environ.get("ISERV_WEBDAV_PASSWORD", "")
ISERV_BACKUP_PATH = os.environ.get("ISERV_BACKUP_PATH", "Files/Backups_AB_KI").strip()
ISERV_BACKUP_ENCRYPTION_KEY = os.environ.get("ISERV_BACKUP_ENCRYPTION_KEY", "").strip()
ISERV_TIMEOUT_SECONDS = os.environ.get("ISERV_TIMEOUT_SECONDS", "15").strip()
ISERV_CA_BUNDLE = os.environ.get("ISERV_CA_BUNDLE", "").strip()

# ── Lesestrecke ──────────────────────────────────────────────────────────────
LESE_SPERRE_SEKUNDEN = (60, 75, 90)   # 1., 2., ab 3. Fehlversuch

# ── Struktur des Arbeitsblatts ───────────────────────────────────────────────
# Reihenfolge und Typ der Stationen stehen je Reiter in plan_<key>.py (STATIONEN, TYPEN) – dort pflegen die
# Inhalts-Agenten ihren Reiter; hier werden die fünf Dateien nur zusammengesetzt. Die Inhaltsdateien
# static/js/inhalte_<key>.js müssen genau diese Nummern in dieser Reihenfolge liefern; tests/test_inhalte_struktur.py
# meldet, was noch fehlt. „L…“ = Lesestrecke (Server: lesen_<key>.py), sie darf an beliebiger Stelle der Liste stehen
# (Browser: tab.leseNach = Nummer der Aufgabe davor). „T“ = Transferaufgabe. Weitere Zeichenketten-Nummern nur in
# GROSSBUCHSTABEN und nicht mit „L“ beginnend (der Server wandelt eingehende Nummern in Großbuchstaben um).
import plan_abschluss
import plan_koerper
import plan_nutzen
import plan_nutztier
import plan_volk

_REITER = [
    ("nutztier", "Nutztier Biene", "N", plan_nutztier),
    ("koerper", "Die Biene", "B", plan_koerper),
    ("volk", "Das Bienenvolk", "V", plan_volk),
    ("nutzen", "Nutzen & Schutz", "S", plan_nutzen),
    ("abschluss", "Abschluss & Quellen", "A", plan_abschluss),
]
ABSCHNITTE = [
    {"key": key, "titel": titel, "kurz": kurz, "aufgaben": list(plan.STATIONEN)}
    for key, titel, kurz, plan in _REITER
]
LESE_MUSTER = re.compile(r"L\d+")


def ist_lesestrecke(nr) -> bool:
    """Ist diese Station eine Lesestrecke („L1“ …)? Nur Zeichenketten der Form L<Zahl> zählen."""
    return isinstance(nr, str) and bool(LESE_MUSTER.fullmatch(nr))


# Aufgabennummer → Typ (Vereinigung aller TYPEN; Schlüssel wie in den plan-Dateien: Zahl oder Zeichenkette)
AUFGABEN_TYPEN = {}
for _key, _titel, _kurz, _plan in _REITER:
    AUFGABEN_TYPEN.update(_plan.TYPEN)
ALLE_AUFGABEN = [str(nr) for a in ABSCHNITTE for nr in a["aufgaben"]]


def _anzeige_karte() -> dict:
    """Anzeigenummern: Die Kinder sehen fortlaufende Nummern 1, 2, 3 … (Position der Aufgaben-Stationen ohne Lesestrecken über
    alle Reiter in der Reihenfolge von STATIONEN); „T“ (Transfer) bekommt die letzte Nummer. Intern bleiben die Nummern der
    plan-Dateien (Autosave, Datenbank, Tests). Der Client rechnet dasselbe in static/js/anzeige.js aus den Inhaltsdateien."""
    reihe = [str(nr) for a in ABSCHNITTE for nr in a["aufgaben"] if not ist_lesestrecke(nr)]
    if "T" in reihe:
        reihe.remove("T")
        reihe.append("T")
    return {nr: i + 1 for i, nr in enumerate(reihe)}


ANZEIGE_NR = _anzeige_karte()


def anzeige_nr(nr):
    """Sichtbare Nummer zu einer internen Station: Zahl 1…N für Aufgaben, „L3“ bleibt „L3“ (Lesestrecke), Unbekanntes unverändert."""
    s = str(nr).strip().upper()
    if ist_lesestrecke(s):
        return s
    return str(ANZEIGE_NR[s]) if s in ANZEIGE_NR else str(nr)


def anzeige_label(nr) -> str:
    """„Aufgabe 7“ bzw. „Lesestrecke 3“ – für Listen und Protokolle der Lehrkraft."""
    s = str(nr).strip().upper()
    if ist_lesestrecke(s):
        return f"Lesestrecke {s[1:]}"
    return f"Aufgabe {anzeige_nr(s)}"
AUFGABE_ZU_ABSCHNITT = {str(nr): a["key"] for a in ABSCHNITTE for nr in a["aufgaben"]}
# {"L1": "nutztier", …} – die Lesestrecke steht irgendwo in der Liste, nicht zwingend vorn
LESESTRECKEN = {nr: a["key"] for a in ABSCHNITTE for nr in a["aufgaben"] if ist_lesestrecke(nr)}


def lese_nach(stationen):
    """Nummer der Station, nach der die Lesestrecke erscheint (None = ganz oben; "" = der Reiter hat keine Lesestrecke)."""
    for i, nr in enumerate(stationen):
        if ist_lesestrecke(nr):
            return stationen[i - 1] if i > 0 else None
    return ""


# Reiter-Key → Nummer der Station, nach der die Lesestrecke erscheint (None = ganz oben); Reiter ohne Lesestrecke fehlen.
# Entspricht tab.leseNach in static/js/inhalte_<key>.js.
LESE_NACH = {a["key"]: lese_nach(a["aufgaben"]) for a in ABSCHNITTE if lese_nach(a["aufgaben"]) != ""}
NOTIZ_ABSCHNITTE = {a["key"] for a in ABSCHNITTE}
NIVEAUS = {"A", "B", "C", "Transfer"}
ANTWORT_TYPEN = {
    # Basis
    "mc", "mc-multi", "luecke", "zuordnung", "sortierung", "diagramm",
    "freitext", "freitext-kreativ", "notizen", "quellen", "lesestrecke", "zeichnung",
    "handschrift", "blitz", "domino", "transfer",
    # Bienen-AB: Bildpunkte (früher „teich“), Richtig/Falsch-Aufgaben
    "bildpunkte", "richtigfalsch",
    # Film-Baustein (film.js) und 3D-Modell (modell3d.js)
    "film", "filmmoment", "erkunden", "modellfinden",
    # Forschend-entwickelnder Ansatz (forschen.js, docs/FORSCHEN.md)
    "vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch",
}
# Längere Antworttexte für einzelne Typen (Standard 500 Zeichen): das Forscherbuch ist ein ganzes Heft
ANTWORT_MAX_ZEICHEN = {"forscherbuch": 8000}


def nr_von_typ(typ: str) -> list:
    """Aufgabennummern eines Typs in Planreihenfolge (z. B. nr_von_typ("zeichnen") → [15, 26, 35])."""
    return [nr for a in ABSCHNITTE for nr in a["aufgaben"] if AUFGABEN_TYPEN.get(nr) == typ]


def pruefe_plaene() -> list[str]:
    """Liefert eine Liste verständlicher Fehlermeldungen zu den Stationsplänen (leer = alles in Ordnung).

    Wird von tests/test_plaene.py aufgerufen – absichtlich nicht beim Import, damit ein Tippfehler in einer
    plan-Datei nicht die ganze App lahmlegt.
    """
    probleme = []
    gesehen = {}
    for key, _titel, _kurz, plan in _REITER:
        stationen, typen = list(plan.STATIONEN), dict(plan.TYPEN)
        lesen = [nr for nr in stationen if ist_lesestrecke(nr)]
        if len(lesen) > 1:
            probleme.append(f"plan_{key}: mehr als eine Lesestrecke {lesen}")
        for nr in stationen:
            if not isinstance(nr, (int, str)) or isinstance(nr, bool):
                probleme.append(f"plan_{key}: Nummer {nr!r} muss eine Zahl oder Zeichenkette sein")
                continue
            if str(nr) in gesehen:
                probleme.append(f"Nummer {nr} steht in plan_{key} und in plan_{gesehen[str(nr)]}")
            gesehen[str(nr)] = key
            if isinstance(nr, str) and not ist_lesestrecke(nr):
                if nr != nr.upper() or nr.startswith("L") or nr != nr.strip() or not nr:
                    probleme.append(f"plan_{key}: Nummer {nr!r} muss in GROSSBUCHSTABEN stehen und darf nicht mit „L“ beginnen")
            if not ist_lesestrecke(nr) and nr not in typen:
                probleme.append(f"plan_{key}: Nummer {nr!r} steht in STATIONEN, aber nicht in TYPEN")
        for nr in typen:
            if nr not in stationen:
                probleme.append(f"plan_{key}: TYPEN kennt {nr!r}, STATIONEN nicht")
        if not stationen:
            probleme.append(f"plan_{key}: STATIONEN ist leer")
    return probleme
# Zeichenaufträge: Aufgabennummer je Motiv. Merkmale und Auftragstexte für die KI-Bewertung
# stehen in zeichenauftraege.py (dort verfeinern, nicht hier).
ZEICHEN_GERAETE = {"biene": 15, "schwaenzeltanz": 26, "bestaeubung": 35, "handschrift": None}
