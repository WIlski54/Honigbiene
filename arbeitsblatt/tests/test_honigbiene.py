"""Prüfungen, die zum Honigbienen-AB gehören: neue Antworttypen, „Woran es hakt“, Zeichenaufträge, Gestaltung, Deployment."""
import os
import re

import pytest

import app as appmodule
import ki
import zeichenauftraege
from config import ABSCHNITTE, ALLE_AUFGABEN, ANTWORT_TYPEN, APP_ID, AUFGABEN_TYPEN, LESESTRECKEN, ZEICHEN_GERAETE, anzeige_nr, ist_lesestrecke, nr_von_typ
from conftest import NR, anmelden, session_werte

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS = {"version": "5.3.0", "objects": [{"type": "rect", "left": 1, "top": 1, "width": 9, "height": 9}]}


def lies(*teile):
    return open(os.path.join(ROOT, *teile), encoding="utf-8").read()


# ── Konfiguration ────────────────────────────────────────────────────────────
def test_app_kennung_und_struktur():
    assert APP_ID == "gsm-nw-honigbiene-6"
    assert [a["key"] for a in ABSCHNITTE] == ["nutztier", "koerper", "volk", "nutzen", "abschluss"]
    nummern = [n for a in ABSCHNITTE for n in a["aufgaben"] if not ist_lesestrecke(n)]
    assert nummern == NR and len(set(map(str, nummern))) == len(nummern), "jede Aufgabennummer nur einmal"
    assert set(nummern) == set(AUFGABEN_TYPEN), "STATIONEN und TYPEN der plan-Dateien müssen übereinstimmen"
    # Je Reiter 1–4 genau eine Lesestrecke L1–L4 (an beliebiger Stelle der Liste), der Abschluss hat keine
    assert LESESTRECKEN == {"L1": "nutztier", "L2": "koerper", "L3": "volk", "L4": "nutzen"}
    assert [sum(1 for n in a["aufgaben"] if ist_lesestrecke(n)) for a in ABSCHNITTE] == [1, 1, 1, 1, 0]
    assert ZEICHEN_GERAETE == {"biene": 15, "schwaenzeltanz": 26, "bestaeubung": 35, "handschrift": None}
    assert ANTWORT_TYPEN >= {"film", "filmmoment", "erkunden", "modellfinden", "bildpunkte", "richtigfalsch", "zeichnung"}
    assert "teich" not in ANTWORT_TYPEN


@pytest.mark.parametrize("typ", ["film", "filmmoment", "erkunden", "modellfinden", "bildpunkte", "richtigfalsch", "zeichnung",
                                 "vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch"])
def test_neue_antworttypen_werden_angenommen(student, typ):
    r = student.post("/api/antwort", json={"aufgabe": NR[8], "niveau": "A", "typ": typ, "frage": "Frage", "antwort": "Text", "korrekt": True})
    assert r.status_code == 200 and r.get_json()["ok"]
    assert student.post("/api/antwort", json={"aufgabe": NR[8], "niveau": "A", "typ": "teich", "antwort": "x"}).status_code == 400


def test_alle_aufgaben_sind_als_fortschritt_gueltig(student):
    for a in ABSCHNITTE:
        for nr in a["aufgaben"]:
            assert student.post("/api/fortschritt", json={"aufgabe": nr, "niveau": "A"}).status_code == 200, nr
    status = student.get("/api/status").get_json()
    assert len(status["erledigt"]) == len(ALLE_AUFGABEN)


# ── Zeichnungen und KI-Prüfliste ─────────────────────────────────────────────
def test_zeichnen_nur_fuer_die_drei_motive(student):
    for geraet in ("biene", "schwaenzeltanz", "bestaeubung"):
        r = student.post("/api/zeichnung", json={"geraet": geraet, "canvas_json": CANVAS}).get_json()
        assert r["ok"], geraet
    assert student.post("/api/zeichnung", json={"geraet": "teich", "canvas_json": CANVAS}).status_code == 400


def test_prompt_der_zeichnung_enthaelt_die_pruefliste_vom_server():
    text = ki.zeichnung_auftrag("biene", "Zeichne eine Biene.", "B")
    assert "Prüfliste" in text and "sechs Beine" in text and "Zeichne eine Biene." in text
    for geraet, a in zeichenauftraege.ZEICHENAUFTRAEGE.items():
        t = ki.zeichnung_auftrag(geraet)
        assert a["titel"] in t and all(m in t for m in a["merkmale"]), geraet
    assert "unbekannt" in ki.zeichnung_auftrag("gibtsnicht").lower() or ki.zeichnung_auftrag("gibtsnicht")


def test_zeichnung_analyse_ohne_ki_antwortet_freundlich(student):
    png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" + "A" * 200
    r = student.post("/api/zeichnung-analyse", json={"png": png, "aufgabe": "x", "geraet": "biene", "niveau": "A"})
    # ohne Freigabe erreicht keine Anfrage die KI
    assert r.status_code == 200 and r.get_json()["blocked"] is True


def test_prompts_sind_auf_bienen_zugeschnitten():
    for text in (ki.SYSTEM_PROMPT, ki.KORREKTUR_PROMPT, ki.ZEICHNUNG_PROMPT, ki.HANDSCHRIFT_PROMPT):
        assert "Ökologie" not in text and "Teich" not in text and "Biotop" not in text and "Klasse 8" not in text
    assert "Klasse 6" in ki.SYSTEM_PROMPT and "Honigbiene" in ki.SYSTEM_PROMPT and "Drohnen haben keinen Stachel" in ki.SYSTEM_PROMPT
    assert "21 Tage" in ki.FAKTEN


# ── Woran es hakt ────────────────────────────────────────────────────────────
def test_woran_es_hakt(student, teacher):
    def antwort(c, nr, korrekt, frage="Frage?"):
        c.post("/api/antwort", json={"aufgabe": nr, "niveau": "A", "typ": "mc", "frage": frage, "antwort": "x", "korrekt": korrekt})

    zweiter = anmelden(appmodule.app.test_client(), "Zweiter", "6b")
    erste, zweite, nur_richtig, nicht_bewertbar = NR[1], NR[8], NR[11], NR[6]   # Stationen aus verschiedenen Reitern
    antwort(student, erste, False, "Was ist ein Nutztier?")
    antwort(student, erste, False)
    antwort(zweiter, erste, False)
    antwort(student, erste, True)
    antwort(student, zweite, True)
    antwort(zweiter, zweite, False, "Tippe auf den Kopf.")
    antwort(student, nur_richtig, True)           # nur richtig → erscheint nicht
    antwort(student, nicht_bewertbar, None)       # nicht bewertbar → zählt nicht
    d = teacher.get("/api/lehrer/hakt").get_json()
    assert d["ok"]
    nrs = [h["nr"] for h in d["hakt"]]
    assert nrs == [str(erste), str(zweite)], nrs  # erst die Station, an der zwei Lernende scheitern
    h2 = d["hakt"][0]
    assert (h2["versuche"], h2["falsch"], h2["personen"], h2["personen_falsch"]) == (4, 3, 2, 2)
    reiter = next(a for a in ABSCHNITTE if str(erste) in map(str, a["aufgaben"]))
    assert h2["abschnitt"] == reiter["titel"] and h2["kurz"] == reiter["kurz"] and h2["beispiel"] == "Was ist ein Nutztier?"
    assert teacher.get("/api/lehrer/state").get_json()["hakt"] == d["hakt"]
    assert appmodule.app.test_client().get("/api/lehrer/hakt").status_code == 401


def test_dashboard_zeigt_aufbau_und_hakt(student, teacher):
    html = teacher.get("/lehrer").get_data(as_text=True)
    assert 'id="hakt-card"' in html and "Woran es hakt" in html and 'id="hakt-body"' in html
    # Die Lehrkraft sieht die laufenden Anzeigenummern (config.anzeige_nr), nicht die internen Nummern der Stationspläne
    zeichen = "/".join(anzeige_nr(n) for n in ZEICHEN_GERAETE.values() if n)
    assert f"{zeichen} Zeichenaufträge" in html and f"{anzeige_nr(nr_von_typ('blitz')[0])} Blitzfragen" in html
    assert f"{anzeige_nr(nr_von_typ('domino')[0])} Domino" in html and f"{anzeige_nr('T')} die Transferaufgabe" in html
    for a in ABSCHNITTE:
        assert a["titel"].replace("&", "&amp;") in html
    assert "Ökologie" not in html and "Klasse 8" not in html


# ── Gestaltung: Logos, Titel, Hinweise ───────────────────────────────────────
def test_logos_und_favicon_liegen_vor_und_sind_eingebunden(client):
    for datei in ("logo-gsm.png", "logo-wk-frei.png", "gsm_avatar.png"):
        assert os.path.getsize(os.path.join(ROOT, "static", "img", datei)) > 5000, datei
    login = client.get("/login").get_data(as_text=True)
    assert "logo-gsm.png" in login and "logo-wk-frei.png" in login and 'class="login-logo-wk"' in login and 'class="login-logo"' in login
    assert "NW · Klasse 6" in login and "Die Honigbiene" in login and "ein Nutztier mit eigenem Staat" in login
    assert 'value="6"' in login                       # Klasse vorbelegt


def test_arbeitsblatt_header_nach_gestaltung(student):
    html = student.get("/arbeitsblatt").get_data(as_text=True)
    assert 'class="logo-gsm"' in html and 'class="logo-wk"' in html
    assert html.index('class="logo-gsm"') < html.index('class="ws-title"') < html.index('class="logo-wk"')
    assert "NW · Klasse 6" in html and "Leitfrage" in html and "ihr Futter meist selbst sucht" in html   # Audit: „meist“, nicht „niemand füttert“
    css = lies("static", "css", "app.css")
    assert re.search(r"\.logo-gsm \{ height: 52px", css) and re.search(r"\.logo-wk \{ height: 60px", css)
    assert re.search(r"\.login-logo \{ height: 56px", css) and re.search(r"\.login-logo-wk \{[^}]*height: 84px", css)


def test_keine_reste_der_oekologie_basis():
    """Weder Texte noch Namen der Vorlage dürfen im Gerüst stehen bleiben."""
    verboten = ["Ökologie", "Oekologie", "oekologie", "Biotop", "Teichbild", "OekoHost", "teich-karte", "teich.js",
                "Einstieg in die", "Klasse 8", "weltkrieg", "Weltkrieg", "Chemie EF", "OEK."]
    funde = []
    for ordner in (".", "static/js", "static/css", "templates", "tafel", "tests", "werkzeuge"):
        pfad = os.path.join(ROOT, ordner)
        for name in sorted(os.listdir(pfad)):
            voll = os.path.join(pfad, name)
            if not os.path.isfile(voll) or not name.endswith((".py", ".js", ".html", ".css", ".md", ".example", ".txt", ".cjs")):
                continue
            if name in ("test_honigbiene.py",):
                continue
            text = open(voll, encoding="utf-8", errors="ignore").read()
            for v in verboten:
                if v in text:
                    funde.append(f"{os.path.relpath(voll, ROOT)}: {v}")
    assert not funde, funde


# ── Deployment-Vertrag ───────────────────────────────────────────────────────
def test_dockerfile_und_betriebsdateien():
    docker = lies("Dockerfile")
    assert "COPY *.py ./" in docker and "COPY tafel/ tafel/" in docker and "COPY static/ static/" in docker
    assert 'python -c "import app"' in docker and "HEALTHCHECK" in docker and "curl" in docker
    gun = lies("gunicorn.conf.py")
    assert "workers = 1" in gun and 'worker_class = "gthread"' in gun
    ignore = lies(".dockerignore")
    assert ".env" in ignore and "data/" in ignore and "tests/" in ignore
    gi = lies(".gitignore")
    assert all(x in gi for x in (".env", "data/", "__pycache__/", ".pytest_cache/"))
    beispiel = lies(".env.example")
    assert "BITTE-ERSETZEN" in beispiel and "AIza" + "Sy" not in beispiel and "honigbiene.db" in beispiel
    assert not [l for l in beispiel.splitlines() if re.match(r"(SECRET_KEY|LEHRER_PASSWORD)=(?!BITTE-ERSETZEN)\S", l)]


def test_modul_dateien_sind_vollstaendig():
    for f in ("lesen_nutztier.py", "lesen_koerper.py", "lesen_volk.py", "lesen_nutzen.py", "glossar_nutztier.py",
              "glossar_koerper.py", "glossar_volk.py", "glossar_nutzen.py", "zeichenauftraege.py",
              "werkzeuge/svg_helfer.py", "werkzeuge/grafik_uebersicht.py", "werkzeuge/modell_attrappe.html",
              "static/js/film.js", "static/css/film.css", "static/js/modell3d.js", "static/js/bildpunkte.js",
              "docs/INHALTE_FORMAT.md", "README.md"):
        assert os.path.exists(os.path.join(ROOT, f)), f


def test_film_und_modell_bausteine_sind_eingehaengt():
    """Die fünf Einhängepunkte aus references/film.md §4 (Kürzel BIE)."""
    html = lies("templates", "index.html")
    assert "css/film.css" in html and html.index("js/aufgaben.js") < html.index("js/film.js")            # 1
    auf = lies("static", "js", "aufgaben.js")
    assert "BIE.film.render" in auf and "BIE.film.nachRender(t)" in auf                                    # 2 (renderBody)
    assert "BIE.film.collect(t.nr)" in auf and "BIE.film.restore(nr, d)" in auf                            # 2 (Autosave)
    assert "BIE.film.init()" in lies("static", "js", "app.js")                                             # 3
    assert "BIE.film.tabGesperrt(key)" in lies("static", "js", "schritte.js")                              # 4
    assert {"film", "filmmoment"} <= ANTWORT_TYPEN                                                         # 5
    film = lies("static", "js", "film.js")
    assert "KUERZEL" not in film and "BIE.film = " in film
    assert 'modell3d: "🧊"' in film and "d.standText" in film and '"erkunden"' in film                     # Änderungen (a), (b), (c) dokumentiert
    assert "ÄNDERUNGEN GEGENÜBER DEM SKILL-BAUSTEIN" in film


def test_qa_umgebung_schuetzt_vor_echten_aufrufen(monkeypatch, tmp_path):
    """qa_umgebung.setzen(): KI-Schlüssel leer, Wegwerf-DB unter werkzeuge/ausgabe, Port 5080."""
    import importlib.util
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-schluessel-nicht-echt")
    spec = importlib.util.spec_from_file_location("qa_umgebung", os.path.join(ROOT, "werkzeuge", "qa_umgebung.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    modul.setzen()
    assert os.environ["GEMINI_API_KEY"] == ""
    assert os.environ["DB_PATH"].replace("\\", "/").endswith("werkzeuge/ausgabe/qa.db")
    assert os.environ["PORT"] == "5080"
