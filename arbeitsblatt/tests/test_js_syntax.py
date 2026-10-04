"""Alle eigenen JavaScript-Dateien müssen syntaktisch gültig sein (Standard: `node --check` je Modul).

Zusätzlich werden sie als klassische Browser-Skripte geparst: Das Elternprojekt hat package.json mit
"type": "module", `node --check` behandelt .js-Dateien deshalb als ES-Module; im Browser laufen sie als Skripte.
"""
import glob
import os
import subprocess

import pytest

from inhalte_laden import NODE, ROOT, node_noetig

DATEIEN = sorted(glob.glob(os.path.join(ROOT, "static", "js", "*.js")) + glob.glob(os.path.join(ROOT, "static", "tafel", "**", "*.js"), recursive=True))


def test_dateien_gefunden():
    assert len(DATEIEN) >= 25


@pytest.mark.parametrize("datei", DATEIEN, ids=[os.path.relpath(d, ROOT).replace(os.sep, "/") for d in DATEIEN])
def test_node_check(datei):
    node_noetig()
    p = subprocess.run([NODE, "--check", datei], capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert p.returncode == 0, p.stderr[-1500:]


def test_als_klassische_skripte_parsbar():
    node_noetig()
    p = subprocess.run([NODE, os.path.join(ROOT, "tests", "_syntax.cjs"), *DATEIEN], capture_output=True, text=True,
                       encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
