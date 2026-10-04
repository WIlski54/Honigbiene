"""Logik des Moduls static/js/modell3d.js (Aufgabentypen „erkunden“ und „modellfinden“).

Die eigentlichen Prüfungen stehen in tests/modell3d.test.cjs (Node, ohne Browser); hier läuft `node --test` und der
Pytest-Lauf fasst das Ergebnis zusammen. Der Browser-Durchlauf mit echtem Modell bzw. Attrappe ist Teil der Browser-QA.
"""
import os
import subprocess

from inhalte_laden import NODE, ROOT, node_noetig


def test_modell3d_logik_unter_node():
    node_noetig()
    p = subprocess.run([NODE, "--test", os.path.join(ROOT, "tests", "modell3d.test.cjs")],
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert p.returncode == 0, (p.stdout + p.stderr)[-3000:]
    assert "fail 0" in p.stdout or "# fail 0" in p.stdout, p.stdout[-1500:]


def test_modul_nutzt_film_nur_ueber_die_oeffentliche_api():
    """modell3d.js darf von film.js nur befehle, status, info, gesehen, besucht und beobachten benutzen (info: Feld `leiste` des Modells)."""
    import re
    quelle = open(os.path.join(ROOT, "static", "js", "modell3d.js"), encoding="utf-8").read()
    benutzt = set(re.findall(r"(?<![\w/.])film\.(?!js\b)([A-Za-z_]+)\s*\(", quelle))   # Aufrufe film.xyz(…), nicht „film.js“ im Kommentar
    assert benutzt <= {"befehle", "status", "info", "gesehen", "besucht", "beobachten"}, benutzt
    assert "BIE.film." not in quelle
    html = open(os.path.join(ROOT, "templates", "index.html"), encoding="utf-8").read()
    assert html.index("js/film.js") < html.index("js/modell3d.js") < html.index("js/schritte.js")
