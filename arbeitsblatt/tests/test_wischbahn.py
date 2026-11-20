"""Wischbahn unter dem 3D-Modell (static/js/wischbahn.js): Einbindung, Anbindung an film.js und Fingerrechnung."""
import json
import os
import re
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, "static", "js")


def _lies(*teile):
    with open(os.path.join(ROOT, *teile), encoding="utf-8") as f:
        return f.read()


def test_wischbahn_nach_film_und_modell_geladen():
    html = _lies("templates", "index.html")
    reihenfolge = [html.index(f"js/{name}.js") for name in ("film", "modell3d", "wischbahn")]
    assert reihenfolge == sorted(reihenfolge)


def test_film_baustein_kennzeichnet_modell_und_bietet_senden():
    quelle = _lies("static", "js", "film.js")
    assert 'buehne.classList.toggle("ist-modell", artVon(id) === "modell3d")' in quelle
    assert re.search(r"return \{[^}]*\bsenden\b", quelle, re.S)


def test_wischbahn_nur_bei_modell_und_nicht_eingeklappt():
    css = _lies("static", "css", "app.css")
    assert ".wischbahn { display: none;" in css
    assert ".filmbuehne.ist-modell:not(.klein) .wischbahn { display: block; }" in css
    assert "touch-action: none" in css.split(".wb-bahn {", 1)[1].split("}", 1)[0]


@pytest.mark.skipif(not shutil.which("node"), reason="node fehlt")
def test_fingerposition_wird_zur_oeffnung():
    skript = """
const vm = require("vm"), fs = require("fs");
const gesendet = [];
const film = { senden: (id, b) => gesendet.push([id, b]), aktiv: () => "biene3d", beobachten() {} };
const BIE = { film, INHALTE: { filme: { biene3d: { art: "modell3d" } } } };
const sandbox = { BIE, window: { addEventListener() {} }, document: { getElementById: () => null }, requestAnimationFrame: fn => fn(), Date };
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), sandbox);
const w = BIE.wischbahn.wertAus;
console.log(JSON.stringify([w(28, 0, 456), w(456 - 28, 0, 456), w(228, 0, 456), w(-50, 0, 456), w(900, 0, 456), w(100, 100, 0)]));
"""
    aus = subprocess.run(["node", "-e", skript, os.path.join(JS, "wischbahn.js")], capture_output=True, text=True, timeout=30)
    assert aus.returncode == 0, aus.stderr
    links, rechts, mitte, davor, dahinter, ohne_breite = json.loads(aus.stdout)
    assert (links, rechts, davor, dahinter, ohne_breite) == (0, 1, 0, 1, 0)
    assert mitte == pytest.approx(0.5)
