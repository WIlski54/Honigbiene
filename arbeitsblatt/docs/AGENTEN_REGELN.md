# Regeln für alle Inhalts- und Grafik-Agenten (Honigbienen-AB)

Gilt zusätzlich zu `../../AB_KONZEPT.md` (Konzept, Fakten, feste Wörter) und `INHALTE_FORMAT.md` (Format aller Aufgabentypen).
Pflichtlektüre vor dem ersten Schreiben: beide Dateien, außerdem aus dem Skill `C:/Users/Admin/.claude/skills/ab-bauen/`:
`references/lernpfad.md` (Lesestrecke, Glossar, Sprache Sek I, Niveau A) und `references/fallstricke.md`.
Stilreferenz für Aufgaben und Texte: `D:/KI Projekte/Ökologie Einstieg/static/js/inhalte.js` und `inhalte_server.py`
(nur lesen; **niemals** `.env`-Dateien lesen, kopieren oder ausgeben).

## Haltung
- Das AB soll Schülerinnen und Schüler (Jahrgang 6, Gesamtschule, heterogen, auch GL) **wirklich etwas über Bienen lernen lassen**.
  Aufgaben prüfen Verstehen, nicht Auswendiglernen von Zahlen. Jede Aufgabe hat einen erkennbaren Lernzweck und passt zu ihrer Quelle
  (Lesestrecke, Film, Modell). Nichts abfragen, was weder Text noch Film noch Modell geliefert hat.
- Eigene Originaltexte (kein Abschreiben aus dem Netz). Fakten **nur** aus „Gesicherte Fakten“ im Konzept oder mit „etwa“. Was du
  darüber hinaus für nötig hältst, aber nicht gesichert ist, **weglassen und im Bericht melden**.
- Sprache: ein Gedanke pro Satz, höchstens etwa 15 Wörter, einfache Wörter, Fachwort beim ersten Auftreten erklären oder ins Glossar.
  Feste Wörter des Konzepts verwenden (kein Synonym für dieselbe Sache). Du-Ansprache. Positive, freundliche Rückmeldungen, die
  **nie die Lösung verraten**, sondern auf ein sichtbares Merkmal lenken.
- A = antippen statt schreiben, kurze Sätze, Bildhilfen · B = Wortspeicher/Satzanfänge · C = freie Formulierung/Begründung, gleiche einfache Sprache.
- Lösungspositionen variieren (nie immer die erste/mittlere Option).
- Niemand wird beschämt: keine „dummen“ Ablenker, keine Fangfragen.

## Dateien und Zuständigkeit
Siehe `INHALTE_FORMAT.md`, Abschnitt 1. **Du bearbeitest nur die Dateien deines Reiters** (und `tests/test_inhalt_<reiter>.py`, `werkzeuge/grafiken_<reiter>.py`).
Brauchst du eine Änderung an gemeinsamen Dateien (`config.py`, `inhalte.js`, `static/js/*.js`, `app.py`, `svg_helfer.py`, `tests/plan.py`),
fasse sie **nicht an**, sondern melde es im Bericht mit genauem Änderungswunsch. Läuft etwas wegen eines Fehlers im Gerüst nicht,
umgehe es nicht heimlich – melde den Fehler.

## Testen
- `cd C:/Users/Admin/Documents/ChatGPT/Honigbiene/arbeitsblatt && python -m pytest -q` (alle Tests; „Noch nicht geschrieben“ fremder Reiter ist erlaubt).
- Eigene Tests `tests/test_inhalt_<reiter>.py`: alle Aufgaben deines Reiters vorhanden und vom Typ laut `tests/plan.py`, A/B/C wo verlangt,
  kein „PLATZHALTER“ mehr, Sätze ≤ ~18 Wörter, Lösungspositionen verteilt, Glossar-Deckung der fetten Begriffe, feste Wörter statt Synonyme, Quellenhinweis bei
  Film-/Modell-Aufgaben, jede Zahl in deinen Texten steht im Konzept.
- `node --check` für deine JS-Datei; keine doppelten Aufgabennummern; Tafel-Adapter-Test (`tests/test_tafel_adapter.py`) bleibt grün.

## Browserprüfung (Pflicht, Zahlen nennen)
- Eigene QA-Instanz, **eigener Port** (siehe Auftrag; nie 5060/5061), `GEMINI_API_KEY=""`, `DB_PATH` auf eine Wegwerf-Datei im Scratchpad
  (`C:/Users/Admin/AppData/Local/Temp/claude/C--Users-Admin-Documents-ChatGPT-Honigbiene/aa758495-9b1c-466e-94d4-240c3b19d31b/scratchpad/`), Start laut `README.md`.
  Server nach Template-/Python-Änderungen neu starten (Flask cached).
- Browser: `mcp__Claude_Browser__*` (vorher Skill `anthropic-skills:built-in-browser` lesen). **Andere Agenten nutzen dasselbe Browserfenster**:
  öffne immer einen **eigenen neuen Tab** (`tabs_create`), arbeite nur darin, schließe ihn am Ende, rühre fremde Tabs nicht an, setze
  `resize_window` am Ende wieder auf `desktop`. Screenshots nur bei sichtbarem Panel; sonst `read_page`, `get_page_text`, `javascript_tool`.
- Schüler-Login über das normale Formular mit Testname (mind. 2 Zeichen) und Klasse. **Lehrkraft nur per Aktionstoken** (`werkzeuge/lehrer_api.py`),
  **nie ein Passwort ins Formular**. Zum schnellen Durchsehen aller Aufgaben gibt es den Prüfmodus `/lehrer/pruefen` (alle Reiter und Stationen offen,
  Lösungen sichtbar); zusätzlich mindestens zwei Aufgaben je Typ einmal wie ein Kind im Schrittmodus lösen (richtig, falsch, Neuladen).
- Prüfen: jede Aufgabe rendert in A, B und C; Rückmeldungen sinnvoll; Lesestrecke komplett (Text, Bild, Frage ohne Text, falsch → Text zurück, Sperre);
  Glossar-Begriffe antippbar; Breiten **768 px und 375 px** ohne waagerechtes Scrollen, Touchziele ≥ 44 px; keine Konsolenfehler.
  Sichtbarkeit nie an `hidden` messen, sondern an `getBoundingClientRect`/`getComputedStyle`.

## Grafiken
Siehe `INHALTE_FORMAT.md`, Abschnitt 7, und `lernpfad.md` (gegenständliche, plastische Szenen, nie Kästchen-Schemata; Beschriftung über/unter Pfeilen mit weißem Halo).
Jede Grafik wird **angesehen**: als PNG rendern (Edge headless: `"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=960,576 --screenshot=<out.png> file:///<pfad>.svg`,
`--virtual-time-budget=6000` für Animation) und mit dem Read-Werkzeug betrachten. Mindestens eine Korrekturrunde.
Biologische Richtigkeit zuerst: Biene = 3 Körperteile, 6 Beine, 4 Flügel (vorn/hinten), 2 Fühler, 2 große Facettenaugen, gestreifter Hinterleib mit Stachel;
Königin: längerer Hinterleib, Flügel kürzer als der Hinterleib; Drohne: dick, riesige Augen, kein Stachel; Wabenzellen sechseckig.

## Allgemein
Keine Git-Commits. Keine Secrets. Keine Änderungen außerhalb von `arbeitsblatt/` (außer Lesen). Kommentare auf Deutsch.

## Bericht (knapp, Deutsch, mit Zahlen)
Was ist fertig (Dateien, Aufgabenliste mit Typ), Testergebnisse (pytest-Zeile, Browserprüfungen mit Messwerten), Fakten/Aussagen, bei denen du unsicher bist,
Änderungswünsche an gemeinsame Dateien, offene Punkte, eigene Fehler und ihre Ursache.
