"""Glossar: antippbare Fachbegriffe mit kurzer Erklärung und Schaubild.

Die fett markierten Begriffe der Lesestrecken werden im Browser zu Links. Ein Tipp öffnet
die Erklärung als Einblendung – ohne die App zu verlassen. Sprache: Sek I, kurze Sätze.

Die Einträge stehen NICHT hier, sondern je Reiter in einer eigenen Datei:
    glossar_nutztier.py · glossar_koerper.py · glossar_volk.py · glossar_nutzen.py
Jede Datei definiert `EINTRAEGE = {"<schluessel>": {titel, text, bild, aliase}}`. Dieses Modul
sammelt sie ein, prüft auf doppelte Schlüssel und doppelte Aliase und baut den Alias-Index
(Format und Konventionen: docs/INHALTE_FORMAT.md).
"""

import re

import glossar_koerper
import glossar_nutztier
import glossar_nutzen
import glossar_volk
from config import ASSET_VERSION

BILD = "/static/img/lese/{}.svg?v=" + ASSET_VERSION

_MODULE = (glossar_nutztier, glossar_koerper, glossar_volk, glossar_nutzen)


def normalisieren(text: str) -> str:
    text = re.sub(r"[„“\"'’‚‘]", "", str(text or "")).lower().strip()
    text = re.sub(r"[.,;:!?]+$", "", text).strip()
    return re.sub(r"\s+", " ", text)


def _einsammeln(module) -> dict:
    gesammelt = {}
    for modul in module:
        for key, eintrag in modul.EINTRAEGE.items():
            if key in gesammelt:
                raise ValueError(f"Glossar-Schlüssel „{key}“ ist doppelt definiert ({modul.__name__}).")
            gesammelt[key] = eintrag
    return gesammelt


def _aliase(glossar: dict) -> dict:
    index = {}
    for key, eintrag in glossar.items():
        for alias in list(eintrag.get("aliase", [])) + [eintrag["titel"]]:
            n = normalisieren(alias)
            if n in index and index[n] != key:
                raise ValueError(f"Glossar-Alias „{alias}“ gehört zu „{index[n]}“ und „{key}“.")
            index[n] = key
    return index


GLOSSAR = _einsammeln(_MODULE)
ALIASE = _aliase(GLOSSAR)


def glossar_fuer_client() -> dict:
    return {
        "eintraege": {
            key: {"titel": e["titel"], "text": e["text"], "bild": BILD.format(e["bild"]) if e.get("bild") else None}
            for key, e in GLOSSAR.items()
        },
        "aliase": ALIASE,
    }


def eintrag_fuer(begriff: str):
    key = ALIASE.get(normalisieren(begriff))
    return GLOSSAR.get(key) if key else None
