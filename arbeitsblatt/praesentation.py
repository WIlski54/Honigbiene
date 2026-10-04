"""Präsentationsmodus: Die Lehrkraft blendet allen Lernenden dasselbe Bild ein.

Gedacht für den Einstieg: Alle sehen nur die Ausgangssituation (zum Beispiel den Imker mit seinen
Bienenkästen) und beschreiben, was sie sehen. Nichts anderes ist bedienbar.

Der Zustand liegt in der Datenbank, nicht im Arbeitsspeicher. Damit gilt er auch
nach einem Serverneustart weiter und erreicht jede Person, die sich erst währenddessen
anmeldet. Der Client bekommt ihn auf drei Wegen: als Socket-Ereignis, über /api/status
beim Anmelden und Neuladen, und über eine Sicherheitsabfrage, falls die Verbindung
zwischenzeitlich abgerissen war.

Das Bild wird nie als Pfad vom Client übernommen, sondern immer über einen Schlüssel
aus BILDER aufgelöst.
"""

import datetime as dt
import os

from config import ASSET_VERSION, BASE_DIR
from db import get_db
from inhalte_server import LESESTRECKEN


def _einstiegsbild() -> str:
    """Das Einstiegsbild „Beim Imker“ (Aufgabe 3). Solange es nicht gezeichnet ist: Platzhalter."""
    for name in ("imker-karte", "platzhalter-karte"):
        if os.path.exists(os.path.join(BASE_DIR, "static", "img", "lese", name + ".svg")):
            return name
    return "platzhalter-karte"


def _bildliste() -> dict:
    """Alle Bilder, die sich präsentieren lassen – Schlüssel, Titel, Pfad, Gruppe."""
    bilder = {
        "einstieg": {
            "titel": "Beim Imker (Einstiegsbild)",
            "gruppe": "Einstieg",
            "datei": _einstiegsbild(),
            "alt": "Bild vom Imker mit Bienenkästen, Blüten und Obstbaum",
        },
    }
    for key, strecke in LESESTRECKEN.items():
        for i, abschnitt in enumerate(strecke["abschnitte"], start=1):
            if not abschnitt.get("bild"):
                continue
            bilder[f"{key}-{i}"] = {
                "titel": abschnitt["ueberschrift"],
                "gruppe": strecke["titel"],
                "datei": abschnitt["bild"],
                "alt": abschnitt.get("bild_alt", abschnitt["ueberschrift"]),
            }
    return bilder


BILDER = _bildliste()


def bild_pfad(key: str) -> str:
    return f"/static/img/lese/{BILDER[key]['datei']}.svg?v={ASSET_VERSION}"


def bilder_fuer_client() -> list:
    return [{"key": k, "titel": b["titel"], "gruppe": b["gruppe"], "bild": bild_pfad(k)}
            for k, b in BILDER.items()]


def lesen() -> dict:
    """Aktueller Zustand. Ein unbekannt gewordener Schlüssel schaltet still ab."""
    with get_db() as db:
        row = db.execute("SELECT * FROM praesentation WHERE id=1").fetchone()
    if not row or not row["active"] or row["bild"] not in BILDER:
        return {"active": False, "bild": None, "key": None, "titel": "", "alt": "", "hinweis": "", "started_at": None}
    key = row["bild"]
    return {
        "active": True,
        "key": key,
        "bild": bild_pfad(key),
        "titel": BILDER[key]["titel"],
        "alt": BILDER[key]["alt"],
        "hinweis": row["hinweis"] or "",
        "started_at": row["started_at"],
    }


def starten(key: str, hinweis: str = "") -> dict:
    if key not in BILDER:
        raise ValueError("unbekanntes Bild")
    hinweis = str(hinweis or "").strip()[:200]
    jetzt = dt.datetime.now().isoformat(timespec="seconds")
    with get_db() as db:
        db.execute(
            "INSERT INTO praesentation (id, active, bild, hinweis, started_at) VALUES (1, 1, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET active=1, bild=excluded.bild, hinweis=excluded.hinweis, "
            "started_at=excluded.started_at",
            (key, hinweis, jetzt),
        )
        db.commit()
    return lesen()


def beenden() -> dict:
    with get_db() as db:
        db.execute("INSERT INTO praesentation (id, active) VALUES (1, 0) "
                   "ON CONFLICT(id) DO UPDATE SET active=0")
        db.commit()
    return lesen()


def aktiv() -> bool:
    return lesen()["active"]
