"""Verschlüsseltes IServ-WebDAV-Archiv (Standard §15–§17).

Sicherheitsvertrag:
- WebDAV nur über HTTPS, TLS-Prüfung nie deaktiviert, optional schulische CA.
- URL ohne Zugangsdaten, Query oder Fragment; Zielpfad POSIX-normalisiert, ohne `.`/`..`.
- Dateischlüssel per HKDF-SHA256 aus dem 32-Byte-Masterkey, AES-256-GCM, Magic-Header + Salt als AAD.
- Der Abschluss löscht Serverdaten erst nach Upload, Download, Entschlüsselung und Digest-Vergleich.
"""

import datetime as dt
import hashlib
import json
import os
import posixpath
import re
import secrets
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import quote, unquote, urlsplit

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

import config as cfg
from config import APP_ID, ARCHIV_FORMAT, DB_SCHEMA_VERSION, SNAPSHOT_MAX_BYTES
from db import canonical_json, snapshot_digest, validate_snapshot

MAGIC = b"GSMIAB01"
SALT_LEN, NONCE_LEN = 16, 12
HKDF_INFO = b"gsm-iabackup-v1"
ENDUNG = ".iabackup"
DATEINAME_RE = re.compile(r"^[0-9a-f]{12}_\d{8}-\d{6}_[A-Za-z0-9_-]{1,40}\.iabackup$")
LEGACY_RE = re.compile(r"^[A-Za-z0-9_.-]{1,120}\.iabackup$")
MAX_CIPHER_BYTES = SNAPSHOT_MAX_BYTES + 1024 * 1024
TRANSPORT_OVERRIDE = None  # Tests injizieren hier einen Fake-Transport


class IServConfigError(ValueError):
    """Ungültige oder unvollständige IServ-Konfiguration."""


class IServFehler(RuntimeError):
    """Fehler in WebDAV, Krypto oder Verifikation – verständlich, ohne Geheimnisse."""


# ── Konfiguration ───────────────────────────────────────────────────────────
@dataclass
class IServConfig:
    url: str
    username: str
    password: str
    path: str
    key: bytes
    timeout: float
    ca_bundle: str | None


def validiere_url(url: str) -> str:
    teile = urlsplit(url.strip())
    if teile.scheme != "https":
        raise IServConfigError("ISERV_WEBDAV_URL muss mit https:// beginnen.")
    if not teile.hostname:
        raise IServConfigError("ISERV_WEBDAV_URL enthält keinen Hostnamen.")
    if teile.username or teile.password:
        raise IServConfigError("ISERV_WEBDAV_URL darf keine Zugangsdaten enthalten.")
    if teile.query or teile.fragment:
        raise IServConfigError("ISERV_WEBDAV_URL darf weder Query noch Fragment enthalten.")
    return url.strip().rstrip("/")


def normalisiere_pfad(pfad: str) -> str:
    roh = str(pfad or "").strip().replace("\\", "/")
    if not roh or "\0" in roh or "?" in roh or "#" in roh:
        raise IServConfigError("ISERV_BACKUP_PATH ist leer oder enthält unzulässige Zeichen.")
    teile = [t for t in roh.split("/") if t != ""]
    if any(t in (".", "..") for t in teile):
        raise IServConfigError("ISERV_BACKUP_PATH darf keine '.'- oder '..'-Segmente enthalten.")
    norm = posixpath.normpath("/".join(teile))
    if norm in (".", "/") or norm.startswith("../"):
        raise IServConfigError("ISERV_BACKUP_PATH ist ungültig.")
    return norm


def dekodiere_schluessel(text: str) -> bytes:
    text = str(text or "").strip()
    if not text:
        raise IServConfigError("ISERV_BACKUP_ENCRYPTION_KEY fehlt.")
    try:
        import base64
        roh = base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except (ValueError, TypeError) as exc:
        raise IServConfigError("ISERV_BACKUP_ENCRYPTION_KEY ist kein gültiges URL-safe Base64.") from exc
    if len(roh) != 32:
        raise IServConfigError("ISERV_BACKUP_ENCRYPTION_KEY muss genau 32 Byte ergeben.")
    return roh


def validiere_timeout(wert) -> float:
    try:
        sekunden = float(wert)
    except (TypeError, ValueError) as exc:
        raise IServConfigError("ISERV_TIMEOUT_SECONDS ist keine Zahl.") from exc
    if not 2 <= sekunden <= 60:
        raise IServConfigError("ISERV_TIMEOUT_SECONDS muss zwischen 2 und 60 liegen.")
    return sekunden


def lade_konfiguration() -> IServConfig:
    if not cfg.ISERV_WEBDAV_URL:
        raise IServConfigError("IServ ist nicht konfiguriert (ISERV_WEBDAV_URL fehlt).")
    if not cfg.ISERV_WEBDAV_USERNAME or not cfg.ISERV_WEBDAV_PASSWORD:
        raise IServConfigError("ISERV_WEBDAV_USERNAME oder ISERV_WEBDAV_PASSWORD fehlt.")
    ca = cfg.ISERV_CA_BUNDLE or None
    if ca and not os.path.isfile(ca):
        raise IServConfigError("ISERV_CA_BUNDLE zeigt auf keine Datei.")
    return IServConfig(
        url=validiere_url(cfg.ISERV_WEBDAV_URL), username=cfg.ISERV_WEBDAV_USERNAME, password=cfg.ISERV_WEBDAV_PASSWORD,
        path=normalisiere_pfad(cfg.ISERV_BACKUP_PATH), key=dekodiere_schluessel(cfg.ISERV_BACKUP_ENCRYPTION_KEY),
        timeout=validiere_timeout(cfg.ISERV_TIMEOUT_SECONDS), ca_bundle=ca,
    )


def status_payload() -> dict:
    try:
        konf = lade_konfiguration()
    except IServConfigError as exc:
        return {"konfiguriert": False, "fehler": str(exc), "marker": app_marker()}
    return {"konfiguriert": True, "host": urlsplit(konf.url).hostname, "pfad": konf.path, "marker": app_marker(), "fehler": None}


# ── Krypto ──────────────────────────────────────────────────────────────────
def app_marker() -> str:
    return hashlib.sha256(APP_ID.encode("utf-8")).hexdigest()[:12]


def _dateischluessel(master: bytes, salt: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=HKDF_INFO).derive(master)


def baue_umschlag(snapshot: dict, name: str) -> dict:
    return {
        "format": ARCHIV_FORMAT, "schema_version": DB_SCHEMA_VERSION, "app_id": APP_ID,
        "name": str(name)[:60], "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "snapshot": snapshot,
    }


def pruefe_umschlag(umschlag) -> dict:
    if not isinstance(umschlag, dict):
        raise IServFehler("Archiv hat kein gültiges Format.")
    if umschlag.get("format") != ARCHIV_FORMAT:
        raise IServFehler("Archiv hat eine unbekannte Formatkennung.")
    version = umschlag.get("schema_version")
    if not isinstance(version, int) or version < 1 or version > DB_SCHEMA_VERSION:
        raise IServFehler("Archiv hat eine unbekannte Schema-Version.")
    if umschlag.get("app_id") != APP_ID:
        raise IServFehler("Archiv gehört zu einem anderen Arbeitsblatt.")
    try:
        validate_snapshot(umschlag.get("snapshot"))
    except ValueError as exc:
        raise IServFehler(f"Snapshot im Archiv ist ungültig: {exc}") from exc
    return umschlag


def verschluesseln(umschlag: dict, master: bytes) -> bytes:
    klartext = canonical_json(umschlag)
    if len(klartext) > SNAPSHOT_MAX_BYTES:
        raise IServFehler("Der Snapshot ist zu groß für ein Archiv.")
    salt = secrets.token_bytes(SALT_LEN)
    nonce = secrets.token_bytes(NONCE_LEN)
    aead = AESGCM(_dateischluessel(master, salt))
    chiffre = aead.encrypt(nonce, klartext, MAGIC + salt)
    blob = MAGIC + salt + nonce + chiffre
    if len(blob) > MAX_CIPHER_BYTES:
        raise IServFehler("Das verschlüsselte Archiv ist zu groß.")
    return blob


def entschluesseln(blob: bytes, master: bytes) -> dict:
    if not isinstance(blob, (bytes, bytearray)) or len(blob) < len(MAGIC) + SALT_LEN + NONCE_LEN + 16:
        raise IServFehler("Archivdatei ist zu kurz oder leer.")
    if len(blob) > MAX_CIPHER_BYTES:
        raise IServFehler("Archivdatei ist zu groß.")
    if bytes(blob[: len(MAGIC)]) != MAGIC:
        raise IServFehler("Archivdatei hat keinen gültigen Kopf.")
    salt = bytes(blob[len(MAGIC): len(MAGIC) + SALT_LEN])
    nonce = bytes(blob[len(MAGIC) + SALT_LEN: len(MAGIC) + SALT_LEN + NONCE_LEN])
    chiffre = bytes(blob[len(MAGIC) + SALT_LEN + NONCE_LEN:])
    try:
        klartext = AESGCM(_dateischluessel(master, salt)).decrypt(nonce, chiffre, MAGIC + salt)
    except InvalidTag as exc:
        raise IServFehler("Archiv konnte nicht entschlüsselt werden (falscher Schlüssel oder manipulierte Datei).") from exc
    try:
        return json.loads(klartext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IServFehler("Archivinhalt ist kein gültiges JSON.") from exc


def sicherer_name(name: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_-]+", "-", str(name or "").strip()).strip("-")
    return (text or "Sitzung")[:40]


def dateiname(name: str, zeit: dt.datetime | None = None) -> str:
    zeit = zeit or dt.datetime.now(dt.timezone.utc)
    return f"{app_marker()}_{zeit:%Y%m%d-%H%M%S}_{sicherer_name(name)}{ENDUNG}"


def dateiname_gueltig(name: str) -> bool:
    return bool(DATEINAME_RE.match(name or ""))


# ── WebDAV ──────────────────────────────────────────────────────────────────
def fehlertext(status: int) -> str:
    return {
        401: "IServ hat die Zugangsdaten abgelehnt (401).",
        403: "Keine Berechtigung für diesen Ordner (403).",
        404: "Ordner oder Datei auf IServ nicht gefunden (404).",
        409: "Der Zielordner existiert nicht (409) – er muss administrativ angelegt werden.",
        412: "Die Datei existiert bereits (412).",
        423: "Die Datei ist gesperrt (423).",
        507: "Kein Speicherplatz auf IServ (507).",
    }.get(status, f"IServ hat mit HTTP {status} geantwortet.")


def _requests_transport(method, url, headers, data, auth, timeout, verify):
    import requests
    try:
        resp = requests.request(method, url, headers=headers, data=data, auth=auth, timeout=timeout, verify=verify)
    except requests.exceptions.SSLError as exc:
        raise IServFehler("TLS-Prüfung fehlgeschlagen – Zertifikat prüfen oder ISERV_CA_BUNDLE setzen.") from exc
    except requests.exceptions.Timeout as exc:
        raise IServFehler("IServ hat nicht rechtzeitig geantwortet (Timeout).") from exc
    except requests.exceptions.RequestException as exc:
        raise IServFehler("Verbindung zu IServ fehlgeschlagen.") from exc
    return resp.status_code, dict(resp.headers), resp.content


def parse_multistatus(xml_bytes: bytes) -> list[dict]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise IServFehler("IServ-Antwort konnte nicht gelesen werden.") from exc
    ns = {"D": "DAV:"}
    eintraege = []
    for resp in root.findall("D:response", ns):
        href = (resp.findtext("D:href", default="", namespaces=ns) or "").strip()
        groesse = resp.findtext(".//D:getcontentlength", default="", namespaces=ns) or "0"
        ist_ordner = resp.find(".//D:resourcetype/D:collection", ns) is not None
        name = unquote(href.rstrip("/").rsplit("/", 1)[-1])
        try:
            groesse = int(groesse)
        except ValueError:
            groesse = 0
        eintraege.append({"href": href, "name": name, "groesse": groesse, "ordner": ist_ordner})
    return eintraege


class WebDAVClient:
    def __init__(self, konf: IServConfig, transport=None):
        self.konf = konf
        self.transport = transport or TRANSPORT_OVERRIDE or _requests_transport

    def _url(self, name: str = "") -> str:
        basis = f"{self.konf.url}/{quote(self.konf.path)}"
        return f"{basis}/{quote(name)}" if name else basis

    def _request(self, method: str, name: str, headers: dict | None = None, data: bytes | None = None):
        return self.transport(
            method, self._url(name), headers or {}, data, (self.konf.username, self.konf.password),
            self.konf.timeout, self.konf.ca_bundle or True,
        )

    def test_verbindung(self) -> dict:
        status, _, body = self._request("PROPFIND", "", {"Depth": "0"})
        if status not in (207, 200):
            raise IServFehler(fehlertext(status))
        eintraege = parse_multistatus(body) if body else []
        return {"ok": True, "pfad": self.konf.path, "eintraege": len(eintraege)}

    def listing(self) -> list[dict]:
        status, _, body = self._request("PROPFIND", "", {"Depth": "1"})
        if status not in (207, 200):
            raise IServFehler(fehlertext(status))
        return [e for e in parse_multistatus(body) if not e["ordner"]]

    def put(self, name: str, data: bytes) -> None:
        status, _, _ = self._request(
            "PUT", name, {"Content-Type": "application/octet-stream", "If-None-Match": "*"}, data
        )
        if status not in (200, 201, 204):
            raise IServFehler(fehlertext(status))

    def get(self, name: str, max_bytes: int = MAX_CIPHER_BYTES) -> bytes:
        status, headers, body = self._request("GET", name)
        if status != 200:
            raise IServFehler(fehlertext(status))
        laenge = headers.get("Content-Length") or headers.get("content-length")
        if laenge and int(laenge) > max_bytes:
            raise IServFehler("Archivdatei ist zu groß.")
        if len(body) > max_bytes:
            raise IServFehler("Archivdatei ist zu groß.")
        return body

    def delete(self, name: str) -> None:
        status, _, _ = self._request("DELETE", name)
        if status not in (200, 204):
            raise IServFehler(fehlertext(status))


def make_client() -> WebDAVClient:
    return WebDAVClient(lade_konfiguration())


# ── Archiv-Operationen ──────────────────────────────────────────────────────
def _zusammenfassung(umschlag: dict, dateiname_: str, groesse: int) -> dict:
    tabellen = umschlag["snapshot"].get("tabellen", {})
    lernende = tabellen.get("schueler", [])
    return {
        "dateiname": dateiname_, "name": umschlag.get("name", ""), "created_at_utc": umschlag.get("created_at_utc", ""),
        "groesse": groesse, "lernende": len(lernende), "antworten": len(tabellen.get("antworten", [])),
        "arbeitsstaende": len(tabellen.get("arbeitsstaende", [])), "zeichnungen": len(tabellen.get("zeichnungen", [])),
        "chat_messages": len(tabellen.get("chat_messages", [])),
        "pseudonyme": sorted(f"{s.get('pseudonym', '?')} ({s.get('klasse', '?')})" for s in lernende)[:60],
        "schema_version": umschlag.get("schema_version"),
    }


def archiv_laden_und_pruefen(client: WebDAVClient, name: str) -> tuple[dict, int]:
    """Lädt, entschlüsselt und validiert ein Archiv; liefert (Umschlag, Größe)."""
    if not (dateiname_gueltig(name) or LEGACY_RE.match(name or "")):
        raise IServFehler("Ungültiger Archivdateiname.")
    blob = client.get(name)
    umschlag = pruefe_umschlag(entschluesseln(blob, client.konf.key))
    return umschlag, len(blob)


def liste_archive(client: WebDAVClient, legacy_pruefen: bool = False) -> list[dict]:
    """Nur Archive der aktuellen App: Marker-Vorauswahl, dann Entschlüsseln und App-ID prüfen."""
    marker = app_marker()
    ergebnis = []
    for eintrag in client.listing():
        name = eintrag["name"]
        if not name.endswith(ENDUNG):
            continue
        ist_eigen = dateiname_gueltig(name) and name.startswith(marker + "_")
        if not ist_eigen and not (legacy_pruefen and LEGACY_RE.match(name) and not DATEINAME_RE.match(name)):
            continue
        try:
            umschlag, groesse = archiv_laden_und_pruefen(client, name)
        except IServFehler:
            continue  # fremde App, anderer Schlüssel oder defekt – nicht anzeigen
        ergebnis.append(_zusammenfassung(umschlag, name, groesse))
    ergebnis.sort(key=lambda e: e["created_at_utc"], reverse=True)
    return ergebnis


def abschluss_durchfuehren(name: str, request_flush, build_snapshot, cleanup, client: WebDAVClient | None = None) -> dict:
    """Verifizieren-vor-Löschen als feste Transaktion (Standard §15.6). Bei jedem Fehler bleibt alles erhalten."""
    client = client or make_client()
    protokoll = {"schritte": [], "flush": None, "dateiname": None, "digest": None, "geloescht": False}

    def schritt(text):
        protokoll["schritte"].append(text)

    protokoll["flush"] = request_flush()
    schritt(f"Flush angefordert: {len(protokoll['flush']['confirmed'])} bestätigt, {len(protokoll['flush']['missing'])} ohne Antwort")
    snapshot = build_snapshot()
    validate_snapshot(snapshot)
    schritt(f"Snapshot erfasst: {len(snapshot['tabellen'].get('schueler', []))} Lernplätze")
    digest = snapshot_digest(snapshot)
    protokoll["digest"] = digest
    umschlag = baue_umschlag(snapshot, name)
    blob = verschluesseln(umschlag, client.konf.key)
    schritt(f"Verschlüsselt: {len(blob)} Byte")
    datei = dateiname(name)
    protokoll["dateiname"] = datei
    client.put(datei, blob)
    schritt("Hochgeladen (PUT mit If-None-Match: *)")
    zurueck = client.get(datei)
    schritt(f"Zurückgelesen: {len(zurueck)} Byte")
    if len(zurueck) != len(blob):
        raise IServFehler("Zurückgelesene Datei hat eine andere Größe – nichts gelöscht.")
    umschlag2 = pruefe_umschlag(entschluesseln(zurueck, client.konf.key))
    schritt("Entschlüsselt, Format/Schema/App-ID geprüft")
    if snapshot_digest(umschlag2["snapshot"]) != digest:
        raise IServFehler("Digest der zurückgelesenen Datei stimmt nicht überein – nichts gelöscht.")
    schritt("Digest stimmt überein")
    cleanup()
    protokoll["geloescht"] = True
    schritt("Temporäre Serverdaten bereinigt")
    return protokoll


def archiv_loeschen(client: WebDAVClient, name: str) -> None:
    """Vor jeder Remote-Löschung: herunterladen, entschlüsseln, Eigentum der aktuellen App validieren."""
    archiv_laden_und_pruefen(client, name)
    client.delete(name)
