"""Logik der Gerüst-Bausteine unter Node (tests/kern.test.cjs): Stationsreihenfolge mit frei platzierter Lesestrecke,
Eingabe-Vergleich mit Umlauten, Trefferkreise der Bildpunkte, Blitzfragen über alle Stufen."""
import os
import re
import subprocess

from inhalte_laden import NODE, ROOT, node_noetig


def test_geruest_logik_unter_node():
    node_noetig()
    p = subprocess.run([NODE, "--test", os.path.join(ROOT, "tests", "kern.test.cjs")], capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert p.returncode == 0, (p.stdout + p.stderr)[-3000:]
    assert "fail 0" in p.stdout or "# fail 0" in p.stdout, p.stdout[-1500:]


def _node_test(datei, anzahl_min):
    node_noetig()
    p = subprocess.run([NODE, "--test", os.path.join(ROOT, "tests", datei)], capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert p.returncode == 0, (p.stdout + p.stderr)[-3000:]
    assert "fail 0" in p.stdout, p.stdout[-1500:]
    tests = int(re.search(r"tests (\d+)", p.stdout).group(1))
    assert tests >= anzahl_min, f"{datei}: nur {tests} Tests gelaufen"


def test_film_knoepfe_pflicht_und_karte_unter_node():
    """tests/film.test.cjs: Film-Knöpfe spielen sofort, Bild-Knopf, Pflicht-Sperre mit allen Knöpfen und 3 s Wiedergabe, Film-Karte live (Audit T1, T6, T7)."""
    _node_test("film.test.cjs", 13)


def test_aufgaben_hilfetext_und_notizen_unter_node():
    """tests/aufgaben.test.cjs: neutraler Standard-Hilfetext, Mehrfachauswahl-Meldung, konfigurierbare Notizen (Audit T5, T9)."""
    _node_test("aufgaben.test.cjs", 6)
