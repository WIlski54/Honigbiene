# Die Honigbiene – ein Nutztier mit eigenem Staat

Interaktives Arbeitsblatt für die Gesamtschule Meiderich (NW · Jahrgang 6, Thema Nutztiere, Klassenunterricht mit Niveau
A/B/C je Aufgabe). Flask + Socket.IO, SQLite, optional Gemini-KI **nur nach Freigabe der Lehrkraft**. Gerüst nach dem
GSM-Produktionsstandard (Autosave in vier Ebenen, Resume-Token, Präsenz, Snapshots, IServ-Archiv, Fortsetzungsstunde,
Prüfmodus, Präsentationsmodus, digitale Tafel). Das Konzept steht in `../AB_KONZEPT.md`.

**Stand:** Das technische Gerüst läuft; die Inhalte (Aufgaben, Lesestrecken, Glossar, Grafiken) werden je Reiter geschrieben –
siehe `docs/INHALTE_FORMAT.md`. Der **forschend-entwickelnde Ansatz** (Vermuten, Beobachten, Erkenntnis festhalten, Sprachwerkstatt;
Lesestrecke zum Nachschlagen erst danach) steht in `docs/FORSCHEN.md`. Was noch fehlt, zeigt `python -m pytest -q` als Warnung
„Noch nicht geschrieben“ bzw. als erwarteter Fehlschlag der Gewichtung.

## Start

```bash
cd arbeitsblatt
pip install -r requirements.txt
cp .env.example .env            # .env ausfüllen (nur BITTE-ERSETZEN-Werte ersetzen) – wird nie eingecheckt
PORT=5080 python app.py         # http://localhost:5080  (Port 5060/5061 sind im Browser gesperrt!)
```

Die Daten liegen in `data/honigbiene.db` (SQLite, bleibt über Neustarts erhalten – beim Start und beim Lehrer-Login wird nichts
gelöscht). Lehrer-Bereich: `/lehrer` (Passwort aus `LEHRER_PASSWORD`), Prüfmodus der Lehrkraft: `/lehrer/pruefen`.

## Browser-QA (immer ohne KI und mit Wegwerf-Datenbank)

Der normale Start lädt die echte `.env` – für Proben im Browser immer den QA-Start benutzen:

```bash
python werkzeuge/qa_server.py          # http://localhost:5080 · DB werkzeuge/ausgabe/qa.db · GEMINI_API_KEY leer
python werkzeuge/lehrer_api.py cookie  # signiertes Lehrer-Cookie für die Browserprobe (nie das Passwortformular benutzen)
python werkzeuge/lehrer_api.py get /api/lehrer/state
```

`lehrer_api.py` schreibt ein Aktionstoken in die QA-Datenbank und ruft Lehrer-APIs mit dem Header `X-Lehrer-Token` auf. Das
Cookie (`session=…`) im Browser setzen (`document.cookie`) und `/lehrer` öffnen. QA-Datenbank zurücksetzen: Datei löschen.
Beispiel für `.claude/launch.json` (Browser-Pane von Claude Code):

```json
{ "version": "0.0.1", "configurations": [
  { "name": "honigbiene-qa", "runtimeExecutable": "python", "runtimeArgs": ["werkzeuge/qa_server.py"], "port": 5080 } ] }
```

3D-Modell ohne das echte Modell testen: `werkzeuge/modell_attrappe.html` ahmt das Protokoll nach (siehe Kopfkommentar dort).

Forschen-Typen im Browser (mit den Test-Fixtures aus `tests/fixtures_forschen.js`, ohne die echten Inhalte zu berühren – Lesestrecke mitten in der Liste, am Ende, oben):

```bash
GEMINI_API_KEY="" PORT=5085 DB_PATH=<Wegwerf>.db python werkzeuge/qa_forschen.py
# Schüler: http://forschen.localhost:5085/login · Lehrkraft: http://lehrer-forschen.localhost:5085 (Cookie per lehrer_api.py, nie das Passwortformular)
```
Schaubilder prüfen: `python werkzeuge/grafik_uebersicht.py --oeffnen`.

## Tests

```bash
python -m pytest -q                                   # alle Tests
INHALTE_STRIKT=1 python -m pytest -q tests/test_inhalte_struktur.py::test_inhalte_vollstaendig   # sind alle 41 Aufgaben da, keine Platzhalter mehr?
node --test tests/modell3d.test.cjs                   # Logik der 3D-Modell-Aufgaben (läuft auch in pytest)
node --test tests/forschen.test.cjs                   # Logik der Forschen-Typen (läuft auch in pytest: tests/test_forschen.py)
python -m pytest -q tests/test_plaene.py              # Stationspläne plan_<reiter>.py (Nummern, Lesestrecke an beliebiger Stelle)
INHALTE_STRIKT=1 python -m pytest -q tests/test_inhalte_struktur.py   # auch Gewichtung forschend/Sprachwerkstatt/Abfrage wird scharf
```

Die Inhalts-Tests laden die JavaScript-Dateien mit Node (`node` muss im PATH sein, sonst werden sie übersprungen).
`tests/plan.py` ist die Checkliste (Aufgabennummer → Typ, Pflicht-Glossarbegriffe, Teile des Modells).

## Aufbau

```
app.py                      Routen, KI-Aufrufe, Socket.IO (Live-Verbindung mit Host-Origin-Prüfung), Fortsetzungsstunde
config.py                   APP_ID, ABSCHNITTE (aus plan_<reiter>.py gebaut), Antworttypen, Versionen
plan_<reiter>.py            Stationsplan je Reiter: STATIONEN (Reihenfolge, Lesestrecke an beliebiger Stelle) und TYPEN
db.py · presence.py         SQLite (additive Migration), Snapshots · Online/Offline aus Lernenden-Sockets
ki.py · zeichenauftraege.py KI-Prompts (nur Bienenfakten) · Merkmale der drei Zeichnungen (15, 26, 35)
iserv_archiv.py             verschlüsseltes IServ-Archiv mit Verify-before-delete
inhalte_server.py           sammelt die Lesestrecken aus lesen_<reiter>.py (Lösungen nur auf dem Server)
glossar.py                  sammelt die Einträge aus glossar_<reiter>.py
praesentation.py            Präsentationsmodus (Einstiegsbild + alle Schaubilder der Lesestrecken)
tafel/ · tafel_anbindung.py digitale Tafel (Baustein, nicht ändern) und ihre Anbindung
static/js/inhalte.js        Kopf: INHALTE = {titel, filme, bildpunkte, tabs}
static/js/inhalte_<reiter>.js  je Reiter die Aufgaben (nutztier, koerper, volk, nutzen, abschluss)
static/js/kern.js … app.js  Namensraum BIE, Autosave, Schrittmodus, Lesestrecke, Glossar, Zeichnen, Spiele, KI, Prüfmodus
static/js/bildpunkte.js     Bild mit antippbaren Punkten (einordnen/benennen)
static/js/film.js · modell3d.js   Film-Baustein (Bühne, Filmaufgaben, Modell-Knöpfe) · Aufgaben „erkunden“ und „modellfinden“
static/js/forschen.js       Forschend-entwickelnder Ansatz: vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch (docs/FORSCHEN.md)
static/js/tafel_adapter.js  Aufgaben für die Tafel (mc, Richtig/Falsch, Lücke, Zuordnung, Sortierung, Freitext)
static/film/                Film (Papiertheater) und 3D-Modell (bienenmodell/, gebaut mit `npm run build:ab` im Elternordner)
static/img/lese/            Schaubilder (SVG; Namen siehe docs/INHALTE_FORMAT.md)
werkzeuge/                  svg_helfer.py, grafik_uebersicht.py, qa_server.py, lehrer_api.py, modell_attrappe.html
tests/                      pytest + Node-Tests
docs/INHALTE_FORMAT.md      Format aller Aufgabentypen, Lesestrecken, Glossar, Grafiken
docs/FORSCHEN.md · FORSCHEN_BEISPIELE.js   Spezifikation des forschenden Ansatzes · Mini-Beispiele A/B/C je Typ (nicht geladen, getestet)
```

## Einen Reiter befüllen (Kurzfassung)

0. `plan_<reiter>.py`: Reihenfolge der Stationen (`STATIONEN`, die Lesestrecke an beliebiger Stelle) und Typ je Aufgabe (`TYPEN`).
1. `static/js/inhalte_<reiter>.js`: Aufgaben in der Reihenfolge von `STATIONEN` (A/B/C je Aufgabe); steht die Lesestrecke nicht oben: `leseNach`.
2. `lesen_<reiter>.py`: Lesestrecke (4–5 Abschnitte, je ein Schaubild und eine Frage) – `"platzhalter": True` entfernen.
3. `glossar_<reiter>.py`: Einträge für alle fett markierten Begriffe.
4. `werkzeuge/grafiken_<reiter>.py`: Schaubilder erzeugen, mit `grafik_uebersicht.py` ansehen.
5. `python -m pytest -q` – dann im Browser (QA-Server) einmal durchklicken, auch im Prüfmodus.

Nach Änderungen an Bildern oder Skripten `ASSET_VERSION` in `config.py` erhöhen (Browser-Cache), Server neu starten.

## Umgebungsvariablen (nur zur Laufzeit, nie im Repository)

| Variable | Bedeutung |
|---|---|
| `SECRET_KEY` | Session-Schlüssel (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `LEHRER_PASSWORD` | Passwort des Lehrerbereichs; ohne Wert ist er gesperrt |
| `GEMINI_API_KEY`, `GEMINI_MODEL`, `DAILY_TOKEN_LIMIT` | KI (optional; ohne Schlüssel läuft alles Übrige) |
| `ISERV_WEBDAV_URL`, `_USERNAME`, `_PASSWORD`, `ISERV_BACKUP_PATH`, `ISERV_BACKUP_ENCRYPTION_KEY`, `ISERV_TIMEOUT_SECONDS`, `ISERV_CA_BUNDLE` | IServ-Archiv (optional) |
| `DB_PATH` | Datenbankdatei (Standard `data/honigbiene.db`) |
| `SESSION_COOKIE_SECURE` | `1` hinter HTTPS |
| `PORT` | Port (Docker 5000) |

`.env.example` enthält nur `BITTE-ERSETZEN`-Platzhalter.

## Auslieferung (Coolify)

Dockerfile (Port 5000, `/health`, Volume `/app/data`, ein gthread-Worker, `COPY *.py ./` und `COPY tafel/ tafel/`, Build-Probe
`import app`). Secrets nur als Runtime-Variablen. Vor jedem Push: `git grep -I --cached -n "AIzaSy"` und
`git check-ignore -v .env`. Nach dem ersten Deployment die Live-Verbindung **auf der echten Domain** prüfen: Upgrade-Test mit
`Origin` muss 101 liefern (nicht 400), und eine Anmeldung muss ohne Neuladen im Dashboard erscheinen (`references/deployment.md`
im Skill `ab-bauen`). Nicht mitten in der Stunde deployen. Film und 3D-Modell liegen in `static/film/` und gehen mit dem Image raus.

## Hinweis zur Tafel (Pilot)

Die digitale Tafel ist im Browser getestet, an echten iPads im Schul-WLAN noch nicht – vor dem Unterrichtseinsatz den
Praxistest laut `references/tafel.md` machen.
