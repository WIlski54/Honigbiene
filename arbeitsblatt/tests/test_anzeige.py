"""Fortlaufende Anzeigenummern: Die Kinder sehen 1, 2, 3 … statt der internen Aufgabennummern der Stationspläne.

Regel: Anzeigenummer = Position der Aufgaben-Stationen (ohne Lesestrecken) über alle Reiter in der Reihenfolge von STATIONEN;
die Transferaufgabe „T“ bekommt die letzte Nummer; Lesestrecken heißen „Lesestrecke 1–4“ (intern L1–L4). Intern bleiben nr/ids
unverändert (Autosave, Datenbank, Tests). Quelle im Server: config.ANZEIGE_NR, im Browser: static/js/anzeige.js (läuft auch auf den
Tafel-Seiten ohne BIE). Dieser Test hält beide gleich und prüft alle sichtbaren Stellen.
"""
import functools
import json
import os
import re
import subprocess

import pytest

import config
from config import ABSCHNITTE, ANZEIGE_NR, anzeige_label, anzeige_nr, ist_lesestrecke
from conftest import NR, session_werte
from inhalte_laden import JS, NODE, ROOT, inhalte_dateien, node_noetig


def stationen():
    """Alle Aufgaben-Stationen (ohne Lesestrecken) in Planreihenfolge, T zuletzt – unabhängig von config.ANZEIGE_NR berechnet."""
    reihe = [str(n) for a in ABSCHNITTE for n in a["aufgaben"] if not ist_lesestrecke(n)]
    if "T" in reihe:
        reihe.remove("T")
        reihe.append("T")
    return reihe


# ── Server ───────────────────────────────────────────────────────────────────
def test_anzeigenummern_sind_lueckenlos_von_1_bis_n_in_planreihenfolge():
    reihe = stationen()
    n = len(reihe)
    assert n >= 10, "zu wenige Stationen – der Test ist sonst wertlos"
    assert sorted(ANZEIGE_NR.values()) == list(range(1, n + 1)), "lückenlos 1…N, jede Nummer genau einmal"
    assert [nr for nr, _ in sorted(ANZEIGE_NR.items(), key=lambda kv: kv[1])] == reihe, "Reihenfolge = Reihenfolge der Stationen"
    assert set(ANZEIGE_NR) == set(reihe) and len(ANZEIGE_NR) == len(set(ANZEIGE_NR)), "jede interne Nummer hat genau eine Anzeigenummer"
    assert n == len([x for x in config.ALLE_AUFGABEN if not ist_lesestrecke(x)]), "N = Zahl der Aufgaben ohne Lesestrecken"


def test_transfer_hat_die_letzte_nummer():
    assert "T" in ANZEIGE_NR
    assert ANZEIGE_NR["T"] == max(ANZEIGE_NR.values()) == len(ANZEIGE_NR)
    assert anzeige_nr("T") == str(len(ANZEIGE_NR)) and anzeige_nr("t") == anzeige_nr("T")


def test_die_erste_station_eines_jeden_reiters_folgt_dem_vorgaenger():
    """Über Reitergrenzen hinweg geht es fortlaufend weiter (nicht je Reiter von vorn)."""
    vorher = 0
    for a in ABSCHNITTE:
        eigene = [str(n) for n in a["aufgaben"] if not ist_lesestrecke(n) and str(n) != "T"]
        if not eigene:
            continue
        assert int(anzeige_nr(eigene[0])) == vorher + 1, a["key"]
        vorher = int(anzeige_nr(eigene[-1]))


def test_zuordnung_ist_stabil_und_umkehrbar():
    umgekehrt = {}
    for nr in stationen():
        a = anzeige_nr(nr)
        assert anzeige_nr(nr) == a and isinstance(a, str) and a.isdigit()
        assert a not in umgekehrt, f"Anzeigenummer {a} doppelt ({umgekehrt.get(a)} und {nr})"
        umgekehrt[a] = nr
    assert len(umgekehrt) == len(ANZEIGE_NR)


def test_lesestrecken_und_unbekanntes():
    stationen_lese = [str(n) for a in ABSCHNITTE for n in a["aufgaben"] if ist_lesestrecke(n)]
    assert stationen_lese, "es gibt Lesestrecken"
    for nr in stationen_lese:
        assert anzeige_nr(nr) == nr.upper() and nr not in ANZEIGE_NR
        assert anzeige_label(nr) == f"Lesestrecke {nr[1:]}"
    assert anzeige_nr("ZZZ") == "ZZZ" and anzeige_nr(9999) == "9999"
    assert anzeige_label(NR[0]) == f"Aufgabe {anzeige_nr(NR[0])}"


# ── Browser-Modul gleich Server ──────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _client():
    node_noetig()
    p = subprocess.run([NODE, os.path.join(ROOT, "tests", "_anzeige.cjs"), JS, *[os.path.join(JS, f) for f in inhalte_dateien()]],
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
    return json.loads(p.stdout)


def test_browser_und_server_rechnen_gleich():
    d = _client()
    assert d["karte"] == {k: v for k, v in ANZEIGE_NR.items()}, "static/js/anzeige.js und config.ANZEIGE_NR müssen übereinstimmen"
    assert d["alleNr"] == stationen() or sorted(d["alleNr"]) == sorted(stationen()), "die Aufgaben in INHALTE sind die des Plans"
    for nr, an in d["nrs"].items():
        assert an == anzeige_nr(nr), nr
        assert d["labels"][nr] == anzeige_label(nr)
    assert sorted(int(v) for v in d["nrs"].values()) == list(range(1, len(d["nrs"]) + 1))
    for lese in d["lese"]:
        assert lese["anzeige"] == lese["nr"] and lese["label"] == f"Lesestrecke {lese['nr'][1:]}"
    assert d["unbekannt"] == ["ZZZ", "9999", str(len(ANZEIGE_NR))], "unbekannte Nummern bleiben, „t“ zählt wie „T“"


def test_tafel_titel_tragen_die_anzeigenummer_aber_die_id_bleibt_intern():
    d = _client()
    assert d["adapter"], "der Tafel-Adapter bietet Aufgaben an"
    for e in d["adapter"]:
        assert e["id"] in d["nrs"], e
        assert e["titel"].startswith(f"Aufgabe {d['nrs'][e['id']]}: "), e
        assert not e["titel"].startswith(f"Aufgabe {e['id']}: ") or e["id"] == d["nrs"][e["id"]], "nicht die interne Nummer"


NODE_SYNTHETISCH = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { console }; ctx.window = ctx; ctx.INHALTE = { tabs: [] }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
const I = ctx.INHALTE;
const a = (nr) => ({ nr, typ: "mc" });
I.tabs.push({ key: "x", lese: "L1", leseNach: 41, aufgaben: [a(41), a(42), a(3)] });
const vor = { ...I.anzeigeKarte() };
I.tabs.push({ key: "y", aufgaben: [a("F1"), a(7), a("T"), a("F2")] });       // später angehängter Reiter: Karte wird neu berechnet
const nach = { ...I.anzeigeKarte() };
process.stdout.write(JSON.stringify({ vor, nach, t: I.anzeigeNr("T"), l: I.anzeigeNr("L1"), ll: I.anzeigeLabel("l1"), f: I.anzeigeLabel("f2"), s: I.anzeigeNr(" 7 ") }));
"""


def test_browsermodul_synthetisch_zahlen_und_text_nummern_t_zuletzt_lese_ausgenommen():
    node_noetig()
    p = subprocess.run([NODE, "-e", NODE_SYNTHETISCH, os.path.join(JS, "anzeige.js")], capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert p.returncode == 0, p.stderr[-1500:]
    d = json.loads(p.stdout)
    assert d["vor"] == {"41": 1, "42": 2, "3": 3}
    assert d["nach"] == {"41": 1, "42": 2, "3": 3, "F1": 4, "7": 5, "F2": 6, "T": 7}, "T rückt ans Ende, auch hinter F2"
    assert d["t"] == "7" and d["l"] == "L1" and d["ll"] == "Lesestrecke 1" and d["f"] == "Aufgabe 6" and d["s"] == "5"


# ── Sichtbare Stellen: keine interne Nummer im Text ──────────────────────────
VERBOTEN_JS = [
    (r"Aufgabe \$\{[^}]*\bnr\b[^}]*\}", "„Aufgabe ${…nr}“ – BIE.anzeigeLabel/anzeigeNr benutzen"),
    (r"Station \$\{[^}]*\bnr\b[^}]*\}(?!\))", "„Station ${…nr}“ – BIE.anzeigeNr benutzen"),
    (r"Aufgabe \" \+ ", "„Aufgabe “ + nr – anzeigeNr benutzen"),
    (r'class="task-number"[^>]*>\$\{t\.nr\}', "Nummern-Badge mit interner nr"),
]
AUSGENOMMEN_JS = {"anzeige.js"}      # definiert die Funktionen selbst


def _js_ohne_inhalte():
    for f in sorted(os.listdir(JS)):
        if f.endswith(".js") and not f.startswith("inhalte") and f not in AUSGENOMMEN_JS:
            yield f, open(os.path.join(JS, f), encoding="utf-8").read()


@pytest.mark.parametrize("muster,hinweis", VERBOTEN_JS, ids=[h[:30] for _, h in VERBOTEN_JS])
def test_keine_interne_nummer_in_sichtbaren_texten_der_skripte(muster, hinweis):
    for f, text in _js_ohne_inhalte():
        for i, zeile in enumerate(text.split("\n"), start=1):
            if re.search(muster, zeile) and "anzeige" not in zeile.lower():      # Zeilen mit anzeigeNr/anzeigeLabel/….anzeige sind in Ordnung
                pytest.fail(f"static/js/{f}:{i}: {hinweis}\n  {zeile.strip()[:140]}")


def test_die_stellen_benutzen_die_zentrale_funktion():
    """Jede umgestellte Stelle ruft anzeigeNr/anzeigeLabel (Browser) bzw. anzeige_nr/anzeige_label (Server) auf."""
    erwartet = {
        "aufgaben.js": ["anzeigeNr(t.nr)", "Aufgabe ${an}: "],
        "schritte.js": ["BIE.anzeigeLabel(nr)"],
        "ki.js": ["BIE.anzeigeLabel(nr)", "BIE.anzeigeNr(nr)"],
        "tafel_adapter.js": ["anzeigeNr(nr)"],
        "tafel_schueler.js": ["INHALTE.anzeigeNr"],
        "detail.js": ["d.anzeige", "a.anzeige"],
        "dashboard.js": ["h.anzeige", "g.anzeige"],
        "kern.js": ["anzeigeNr, anzeigeLabel"],
    }
    for f, teile in erwartet.items():
        text = open(os.path.join(JS, f), encoding="utf-8").read()
        for t in teile:
            assert t in text, f"{f}: {t!r} fehlt"
    for f in ("index.html", "tafel_lehrer.html"):
        html = open(os.path.join(ROOT, "templates", f), encoding="utf-8").read()
        assert "js/anzeige.js" in html, f
        assert html.index("js/anzeige.js") < html.index("js/kern.js" if f == "index.html" else "js/tafel_adapter.js"), f"{f}: anzeige.js muss vor kern.js/tafel_adapter.js geladen werden"
        assert html.index("js/inhalte_abschluss.js") < html.index("js/anzeige.js"), "anzeige.js nach allen Inhaltsdateien"


# ── Lehrerseiten ─────────────────────────────────────────────────────────────
def test_dashboard_aufbau_zeigt_anzeigenummern_mit_tooltip_der_internen_nummer(student, teacher):
    html = teacher.get("/lehrer").get_data(as_text=True)
    for nr in stationen()[:3]:
        assert f'<span title="{anzeige_label(nr)} (intern {nr})">{anzeige_nr(nr)}</span>' in html, nr
    for a in ABSCHNITTE:
        sichtbar = "".join(f'>{anzeige_nr(n)}</span>' for n in a["aufgaben"])
        assert sichtbar and all(f">{anzeige_nr(n)}</span>" in html for n in a["aufgaben"])
    # Hilfetext: Zeichenaufträge, Blitz, Transfer mit Anzeigenummern
    assert f"{anzeige_nr('T')} die Transferaufgabe" in html


def test_hakt_und_vermutungen_liefern_anzeigenummern(student, teacher):
    erste = NR[1]
    student.post("/api/antwort", json={"aufgabe": erste, "niveau": "A", "typ": "mc", "frage": "F?", "antwort": "x", "korrekt": False})
    h = teacher.get("/api/lehrer/hakt").get_json()["hakt"]
    assert h[0]["nr"] == str(erste) and h[0]["anzeige"] == anzeige_nr(erste)
    verm = config.nr_von_typ("vermutung")[0]
    student.post("/api/antwort", json={"aufgabe": verm, "niveau": "A", "typ": "vermutung", "frage": "Was vermutest du?", "antwort": "Vermutung: A", "korrekt": None})
    v = teacher.get("/api/lehrer/vermutungen").get_json()["vermutungen"]
    assert v[0]["nr"] == str(verm) and v[0]["anzeige"] == anzeige_nr(verm)
    assert teacher.get("/api/lehrer/state").get_json()["hakt"][0]["anzeige"] == anzeige_nr(erste)


def test_detailseite_zeigt_kacheln_und_antworten_mit_anzeigenummer(student, teacher):
    erste, zweite = NR[1], NR[4]
    student.post("/api/fortschritt", json={"aufgabe": str(zweite), "niveau": "B"})
    student.post("/api/antwort", json={"aufgabe": erste, "niveau": "A", "typ": "mc", "frage": "F?", "antwort": "meine Antwort", "korrekt": True})
    sid = session_werte(student)["schueler_id"]
    html = teacher.get(f"/lehrer/schueler/{sid}").get_data(as_text=True)
    kachel = re.search(rf'<div class="tile[^"]*" id="tile-{zweite}" title="[^"]*">([^<]*)(<small>|</div>)', html)
    assert kachel, "Kachel der erledigten Station fehlt"
    assert kachel.group(1).strip() == anzeige_nr(zweite), "die Kachel zeigt die Anzeigenummer"
    assert f'title="Aufgabe {anzeige_nr(zweite)} (intern {zweite})"' in html
    assert f'<strong title="intern {erste}">Aufgabe {anzeige_nr(erste)}</strong>' in html, "Antwortliste: „Aufgabe N“ statt „Station nr“"
    assert "<strong>Station " not in html


def test_status_und_live_ereignisse_tragen_die_anzeigenummer(student):
    from app import get_schueler_info
    sid = session_werte(student)["schueler_id"]
    student.post("/api/fortschritt", json={"aufgabe": str(NR[2]), "niveau": "A"})
    info = get_schueler_info(sid)
    assert info["niveaus"] == [{"nr": str(NR[2]), "anzeige": anzeige_nr(NR[2]), "niveau": "A"}]
    assert info["erledigt_liste"] == [str(NR[2])], "intern bleibt intern (Autosave, Fortschritt)"
