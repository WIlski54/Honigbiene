"""Serverseitige Inhalte: gegatete Lesestrecken mit Verständnisfragen.

Die Lösungen liegen ausschließlich auf dem Server. Der Client erhält Text, Frage und Optionen,
aber nie die richtige Position. Jede Frage lässt sich aus ihrem Abschnitt allein beantworten.
Sprache: Sek I, kurze Sätze, Fakten unverändert.

Die Texte selbst stehen NICHT hier, sondern je Reiter in einer eigenen Datei:
    lesen_nutztier.py · lesen_koerper.py · lesen_volk.py · lesen_nutzen.py
Jede Datei definiert `LESESTRECKEN = {"<reiter-key>": {…}}`. Dieses Modul sammelt sie ein
(Format und Konventionen: docs/INHALTE_FORMAT.md). Wer einen Reiter schreibt, fasst nur seine Datei an.
"""

import random

import lesen_koerper
import lesen_nutztier
import lesen_nutzen
import lesen_volk
from config import ASSET_VERSION

_MODULE = (lesen_nutztier, lesen_koerper, lesen_volk, lesen_nutzen)


def _einsammeln(module) -> dict:
    gesammelt = {}
    for modul in module:
        for key, strecke in modul.LESESTRECKEN.items():
            if key in gesammelt:
                raise ValueError(f"Lesestrecke „{key}“ ist doppelt definiert ({modul.__name__}).")
            gesammelt[key] = strecke
    return gesammelt


LESESTRECKEN = _einsammeln(_MODULE)

STATION_ZU_ABSCHNITT = {v["station"]: k for k, v in LESESTRECKEN.items()}


def _bild(a: dict):
    return f"/static/img/lese/{a['bild']}.svg?v={ASSET_VERSION}" if a.get("bild") else None


def lesestrecke_fuer_client(key: str, status: dict) -> dict:
    """Text, Fragen und Optionen ohne Lösungen. Erklärungen nur für bereits bestandene Abschnitte."""
    strecke = LESESTRECKEN[key]
    phase = int(status.get("phase", 0))
    abschnitte = []
    for i, a in enumerate(strecke["abschnitte"]):
        eintrag = {"ueberschrift": a["ueberschrift"], "text": a["text"], "frage": a["frage"], "optionen": list(a["optionen"]),
                   "bild": _bild(a), "bild_alt": a.get("bild_alt", "")}
        if i < phase:
            eintrag["erklaerung"] = a["erklaerung"]
        abschnitte.append(eintrag)
    return {
        "key": key, "station": strecke["station"], "eyebrow": strecke["eyebrow"], "titel": strecke["titel"],
        "abschnitte": abschnitte, "anzahl": len(abschnitte),
        "status": {"phase": phase, "fertig": bool(status.get("fertig")), "retry_until": float(status.get("retry_until", 0) or 0), "versuche": int(status.get("versuche", 0))},
    }


def lesestrecke_vollstaendig(key: str) -> dict:
    """Für den Prüfmodus der Lehrkraft: alle Abschnitte mit Lösung und Erklärung."""
    strecke = LESESTRECKEN[key]
    abschnitte = [{
        "ueberschrift": a["ueberschrift"], "text": a["text"], "frage": a["frage"], "optionen": list(a["optionen"]),
        "loesung": int(a["loesung"]), "erklaerung": a["erklaerung"],
        "bild": _bild(a), "bild_alt": a.get("bild_alt", ""),
    } for a in strecke["abschnitte"]]
    return {"key": key, "station": strecke["station"], "eyebrow": strecke["eyebrow"], "titel": strecke["titel"],
            "abschnitte": abschnitte, "anzahl": len(abschnitte)}


def pruefen(key: str, phase: int, wahl: int) -> tuple[bool, str]:
    abschnitt = LESESTRECKEN[key]["abschnitte"][phase]
    korrekt = int(wahl) == abschnitt["loesung"]
    return korrekt, abschnitt["erklaerung"] if korrekt else ""


def gemischte_reihenfolge(anzahl: int) -> list[int]:
    reihenfolge = list(range(anzahl))
    random.shuffle(reihenfolge)
    return reihenfolge
