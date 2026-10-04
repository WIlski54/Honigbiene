"""Lädt INHALTE (static/js/inhalte.js + inhalte_<reiter>.js) mit Node und liefert sie als Python-Dict.

Die Inhalte sind JavaScript-Dateien (eine je Reiter). Statt sie mit regulären Ausdrücken zu zerlegen, führt
`_lade_inhalte.cjs` sie in einer leeren Umgebung aus – in derselben Reihenfolge wie templates/index.html – und gibt
`window.INHALTE` als JSON zurück. Ohne Node werden alle Tests, die das brauchen, übersprungen.
"""
import functools
import json
import os
import re
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, "static", "js")
NODE = shutil.which("node")


def inhalte_dateien() -> list[str]:
    """Inhaltsdateien in der Ladereihenfolge von templates/index.html (Pfade relativ zu static/js)."""
    html = open(os.path.join(ROOT, "templates", "index.html"), encoding="utf-8").read()
    return re.findall(r"filename='js/(inhalte[a-z_]*\.js)'", html)


def node_noetig():
    if not NODE:
        pytest.skip("Node.js nicht gefunden – dieser Test braucht `node` im PATH")


@functools.lru_cache(maxsize=1)
def _geladen() -> str:
    node_noetig()
    dateien = [os.path.join(JS, f) for f in inhalte_dateien()]
    p = subprocess.run([NODE, os.path.join(ROOT, "tests", "_lade_inhalte.cjs"), *dateien],
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
    return p.stdout


def lade_inhalte() -> dict:
    return json.loads(_geladen())


def alle_aufgaben(inhalte: dict | None = None) -> list[tuple[str, dict]]:
    """[(reiter_key, aufgabe), …] in der Reihenfolge der Dateien."""
    inhalte = inhalte or lade_inhalte()
    return [(tab["key"], a) for tab in inhalte["tabs"] for a in tab["aufgaben"]]
