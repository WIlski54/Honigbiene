# Forschend-entwickelnder Ansatz im Honigbienen-AB (verbindlich, Stand 3.10.2026)

Vorgabe von Stephan: Das AB ist für **Jahrgang 6**. Lesen und Fragen beantworten reicht nicht. Der **forschend-entwickelnde Ansatz hat
Vorrang**: Die Kinder sammeln Beobachtungen und Erkenntnisse **selbst** – mit dem 3D-Modell, dem Film und Bildern. Die Multimedia-Bausteine
bleiben, werden aber vom Anschauungsmaterial zum **Forschungsinstrument**. Dazu kommen einfache Textaufgaben, die den **Umgang mit der
deutschen Sprache** trainieren (Sprachwerkstatt). Das Lesen rückt an die zweite Stelle (nachschlagen, bestätigen, vertiefen).

## Ablauf in jedem Reiter (Phasen)

1. **Forscherfrage und Vermutung** – eine Frage, die neugierig macht; Kinder vermuten, ohne Bewertung (`vermutung`).
2. **Erkunden und Beobachten** – mit Modell, Film, Bild: sie zählen, vergleichen, suchen, messen, finden (`erkunden`, `protokoll`, `tabelle`,
   `modellfinden`, `film`, `filmmoment`, `bildpunkte`, `bildwahl`, `diagramm` mit Auswertung). Kein Text vorab, der die Antwort liefert.
3. **Auswerten und Erkenntnis** – Vermutung mit der Beobachtung vergleichen, Erkenntnis in einem Satz festhalten (`pruefen`).
4. **Nachschlagen** – die **Lesestrecke kommt erst jetzt** (kurz, 3–4 Abschnitte, bestätigt und erweitert, was die Kinder selbst gefunden haben; Fragen
   bleiben, Bilder bleiben). Glossar antippbar.
5. **Sprachwerkstatt** – kurze, einfache Aufgaben zum Thema des Reiters, die Sprache trainieren: Wortschatz mit Artikel und Plural (die Biene – die
   Bienen, der Imker – die Imker, das Volk – die Völker), Wörter zusammensetzen (Bienen + Kasten), Verben für Tätigkeiten (saugen, sammeln, fächeln, putzen),
   Eigenschaften beschreiben (Adjektive, Vergleiche: größer, länger, dicker), Sätze bauen (Wortkarten ordnen), Zeitfolge (zuerst, dann, danach, schließlich),
   begründen (weil, denn, damit, deshalb), „je … desto“, W-Fragen stellen (Wie viele …? Warum …? Wo …?), Präpositionen (aus, in, auf, zu, von … nach).
   Umsetzung mit vorhandenen Typen (`sortierung` für Wörter → Satz, `luecke` mit Chips für Artikel/Präpositionen/Konnektoren, `zuordnung` für Artikel/Plural und
   Wortbildung, `mc`, `freitext` mit Bausteinen). Der `eyebrow` beginnt mit **„Sprachwerkstatt“** (Tests zählen es). Fachwörter aus „Feste Wörter“ im Konzept.
6. **Sichern und Anwenden** – Zeichnen, Notizen („Mein Forscherbuch“), Transfer; im Abschluss das **Forscherbuch** (alle Vermutungen und Erkenntnisse).

## Gewichtung (wird von Tests geprüft, `tests/plan.py`)

Gezählt werden Stationen **ohne** Lesestrecke, je Reiter (Abschluss ausgenommen):
- **Echtes Forschen** (Audit 4. Oktober 2026, Entscheidung 3 – „Forschen zählt nur, wo das Kind **Evidenz sammelt**: zählen, vergleichen, suchen, entscheiden am Material“):
  die Typen `vermutung`, `pruefen`, `protokoll`, `tabelle`, `bildwahl`, `filmmoment` und `diagramm` **mit Auswertung** (`ECHT_FORSCHEN_TYPEN` in `tests/plan.py`).
  **Nicht** gezählt (Anwenden/Vokabeln): `bildpunkte` (Benennen/Einordnen am Bild), `zeichnen`, `erkunden`, `modellfinden`, `film`. Sie zählen nur, wenn die Aufgabe selbst
  Evidenz sammeln lässt und `forschen: true` trägt (an der Aufgabe oder an einem Niveau); `forschen: false` nimmt auch einen echten Typ aus der Zählung.
  Anforderung: **mindestens 25 % der Stationen je Reiter** und in den Reitern 2–4 (`koerper`, `volk`, `nutzen`) **mindestens 3 echte Forschen-Stationen**
  (`QUOTE_FORSCHEN_MIN`, `MIN_FORSCHEN`, `MIN_FORSCHEN_ANZAHL`). `nutztier` bleibt bei 25 % und ohne Vermutungspflicht;
- **Sprachwerkstatt** (`eyebrow` beginnt mit „Sprachwerkstatt“) mindestens **2 Stationen** (und etwa 20 %);
- reine Abfrage-/Sicherungsaufgaben (`mc`, `luecke`, `zuordnung`, `sortierung`, `blitz`, `domino`, `quellen` **ohne** Sprachwerkstatt-Eyebrow) höchstens **30 %**;
- höchstens **12 Stationen** je Reiter (inklusive Lesestrecke); **Ausnahme: der Film-Reiter `volk` darf 13** (`MAX_STATIONEN` in `tests/plan.py`); Abschluss höchstens 6.
- Jeder Reiter beginnt (nach dem Start) mit einer **Forscherfrage** (`vermutung`) und schließt die Forschungsphase mit einem `pruefen` oder einem
  Erkenntnissatz. **Ausnahme `nutztier`** (`OHNE_VERMUTUNG` in `tests/plan.py`): Dort ist der Wissensaufbau einfacher; `vermutung`, `pruefen` und `erkenntnis`
  sind erlaubt, aber nicht verlangt. Ein `pruefen` muss trotzdem auf eine vorhandene `vermutung.id` zeigen. Die Lesestrecke steht **nach** der ersten
  Erkundungsphase (nicht als erste Station).
- **Wann eine Vermutung?** Eine Vermutung nur dort stellen, wo sie **innerhalb des Reiters (in den folgenden Stationen) geprüft** werden kann; sonst ist es eine
  einfache Frage mit Rückmeldung (`mc`). Eine Vermutung ohne spätere Prüfung im selben Reiter ist eine Scheinforschung: Das Kind rät, erfährt aber nie, ob es stimmte.
- Die Modell- und Film-Aufgaben sind jetzt **das Rückgrat**: Mindestens die Hälfte der Forschen-Stationen der Reiter 2 und 3 arbeitet unmittelbar mit Modell bzw. Film.

## Neue Aufgabentypen (Format, `static/js/forschen.js`)

Lauffähige Mini-Beispiele mit A/B/C für jeden Typ: `docs/FORSCHEN_BEISPIELE.js` (nicht geladen; `tests/test_forschen.py` prüft sie). Umgesetzt wie hier beschrieben –
Ergänzungen der Umsetzung (alle **optional**, nichts Verbindliches geändert) stehen unten bei den Typen als „Umsetzung:“.

Alle Texte einfacher Text (kein HTML). Alle Typen haben `nr`, `typ`, `eyebrow`, `titel` und `niveaus: {A, B, C}` (A = antippen statt schreiben, B = Satzanfänge/Chips,
C = frei und begründend). Ein Feld `modell` (Knopf wie bei jeder Aufgabe) und `erkenntnis` (Merksatz für das Forscherbuch) darf auf Aufgabenebene stehen.

### `vermutung` – Forscherfrage mit Vermutung (keine Bewertung)
```js
{ nr: 41, typ: "vermutung", id: "v_anzahl", eyebrow: "Forscherfrage", titel: "Wie viele Bienen leben in einem Stock?",
  frage: "Was vermutest du?",
  niveaus: {
    A: { optionen: ["etwa 50", "etwa 500", "etwa 5 000", "etwa 50 000"] },                                    // eine wählen
    B: { optionen: [...], satzanfang: "Das vermute ich: …", begruendung: ["weil …", "denn …"] },             // wählen + Satz ergänzen
    C: { satzanfang: "Ich vermute, dass …", frei: true, min: 30 }                                            // eigener Satz mit Begründung
  } }
```
Es gibt kein Richtig/Falsch. „Vermutung festhalten“ sperrt die Karte (ehrliche Forschung: Vermutungen werden nicht nachträglich geändert). `id` ist eindeutig
und wird von `pruefen` und `forscherbuch` gelesen. Mehrfachauswahl: `mehrfach: true` im Niveau.

Hinweis zu den Satzbausteinen: Ein Baustein `begruendung` hängt sich an den **schon geschriebenen** Text an („Das vermute ich: es sind viele, weil …“). Wähle den Satzanfang so, dass er
mit dem Baustein nicht zusammenstößt – „Ich vermute, dass …“ + „weil …“ ergäbe „dass weil“, wenn jemand den Baustein zuerst tippt; deshalb verlangt die Karte zuerst eigenen Text.
Umsetzung: Vor dem Sperren fragt die Karte einmal nach („Willst du deine Vermutung jetzt festhalten?“). Die Bausteine `begruendung` hängen sich an den **schon
geschriebenen** Text an (vorher: Hinweis „Schreibe zuerst, was du vermutest“) – so entsteht „Ich vermute, dass es viele sind, weil …“, nie „dass weil“. `min` zählt nur die
Fortsetzung, nicht den Satzanfang (Standard B 10, C 30 Zeichen). Das Protokoll der Lehrkraft zeigt „Vermutung: <Option> · <Satz>“ (mehrere Optionen mit „ | “); ohne Bewertung.
Eine festgehaltene Vermutung sperrt auch das Niveau der Karte.

### `pruefen` – Vermutung prüfen und Erkenntnis festhalten
```js
{ nr: 45, typ: "pruefen", vermutung: "v_anzahl", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?",
  quelle: "Sieh dir Szene 1 im Film noch einmal an.", modell: { film: "volk", text: "Szene 1 ansehen", befehle: [{ mw: "kapitel", n: 1 }] },
  erkenntnis: "Im Sommer leben bis zu etwa 50 000 Bienen in einem Stock.",
  niveaus: {
    A: { erkenntnis: { frage: "Was hast du herausgefunden?", optionen: [{ t: "…", ok: true }, { t: "…", ok: false }, { t: "…", ok: false }] } },
    B: { erkenntnis: { … }, beleg: { frage: "Woher weißt du das?", optionen: [{ t: "Aus dem Film.", ok: true }, …] } },
    C: { erkenntnis: { … }, satz: { anfang: "Ich habe herausgefunden, dass … Meine Vermutung war …", min: 60 } } } }
```
Ablauf: (1) zeigt „Deine Vermutung war: …“ (aus der Station `vermutung`); (2) Selbsteinschätzung „Sie stimmt / Sie stimmt teilweise / Sie stimmt nicht / **Das kann ich hier nicht herausfinden**“ (keine Bewertung, sperrt nichts – für freie Vermutungen, die die Evidenz nicht prüfen kann);
(3) Erkenntnis wählen (`ok` wird geprüft, Rückmeldung verrät die Lösung nicht, sondern lenkt auf die Quelle); (4) B/C: Beleg bzw. eigener Satz. Der Merksatz `erkenntnis` erscheint
nach erfolgreichem Abschluss und wird ins Forscherbuch übernommen.

Umsetzung: `quelle` steht **einmal** als gelber Kasten über den Fragen; nach einer falschen Antwort verweist die Rückmeldung nur darauf („… der gelbe Hinweis oben hilft dir“).
Eine falsch gewählte Erkenntnis bleibt rot und gesperrt, so bleibt am Ende nur die richtige übrig. `erkenntnis.hinweis` (optional) erscheint nach dem zweiten Fehler. Die Vermutung
wird über die `id` aus **jedem** Reiter gelesen. Ohne festgehaltene Vermutung steht ein freundlicher Hinweis, geprüft werden kann trotzdem.

### `protokoll` – Forscherbogen (Beobachtungsprotokoll mit Prüfung)
```js
{ nr: 51, typ: "protokoll", eyebrow: "Forschen", titel: "Zähle und beobachte", auftrag: "Drehe die Biene im Modell und trage ein, was du siehst.",
  modell: { film: "biene3d", text: "Biene im Modell öffnen", befehle: [{ mw: "ansicht", name: "gestalt" }] },
  erkenntnis: "Eine Biene hat drei Körperteile, sechs Beine und vier Flügel.",
  niveaus: {
    A: { zeilen: [
      { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, einheit: "Beine", hinweis: "Zähle auf beiden Seiten.", modell: { film: "biene3d", text: "Von der Seite zeigen", befehle: [{ mw: "blick", name: "seite" }] } },
      { frage: "Welches Beinpaar trägt das Körbchen?", art: "wahl", optionen: ["vorn", "Mitte", "hinten"], loesung: 2, hinweis: "Schau dir alle drei Beinpaare an." } ],
      schluss: { anfang: "Ich habe beobachtet, dass …", bausteine: ["die Biene sechs Beine hat.", "…"] } },       // optional: Satz aus Bausteinen (A), Satzanfang (B), frei (C)
    B: { … }, C: { … } } }
```
Zeilenarten: `zahl` (Zähler mit −/+ und Eingabe; `toleranz` optional), `wahl` (Chips, eine richtig = Index `loesung`), `mehrfach` (Chips, `loesung` = Liste der Indizes),
`text` (kurzer Satz, `min` Zeichen, optional `satzanfang`; wird nicht automatisch inhaltlich bewertet, nur auf Länge geprüft und ins Protokoll gespeichert).

Umsetzung (optionale Zeilenfelder): `einheit` (steht neben dem Zähler), `schritt` (Schrittweite von −/+, Standard 1), `kurz` (Beschriftung im Protokoll der Lehrkraft, sonst `einheit` oder `frage`),
`erklaerung` (nach „richtig“), `fehlertext` (ersetzt den Satz nach dem ersten Fehler, z. B. bei Rechenzeilen statt „Zähle noch einmal genau nach“). Die Zahleingabe versteht „6“, „6,5“, „sechs“,
„6 Beine“ und „50.000“. `schluss`: A `bausteine` (Texte oder `{t, ok, rueckmeldung}`; ein Baustein mit `ok: false` wird freundlich zurückgewiesen) · B `anfang` ohne `bausteine` (Satz, `min`) ·
C ohne `anfang` (frei); `pflicht: true` macht den Satz zur Bedingung für „erledigt“ (sonst freiwillig). Die Station ist erledigt, wenn alle Zeilen stimmen.
Jede Zeile hat „Prüfen“ (oder eine gemeinsame Taste); falsch → freundlicher Hinweis ohne Lösung, nach zwei Fehlern `hinweis`, nach drei `hinweis2` bzw. Knopf blinkt. Station
erledigt, wenn alle Zeilen richtig bzw. (`text`) ausgefüllt sind. Zeilen dürfen einen eigenen Knopf `modell` tragen (öffnet genau die Ansicht, aus der die Antwort folgt).

### `tabelle` – Vergleichstabelle zum Ausfüllen
```js
{ nr: 61, typ: "tabelle", eyebrow: "Vergleichen", titel: "Königin, Arbeiterin und Drohne im Vergleich", auftrag: "…",
  modell: { film: "volk", text: "Szene 4 ansehen", befehle: [{ mw: "kapitel", n: 4 }] },
  erkenntnis: "Die Königin ist am längsten …",
  niveaus: { A: { spalten: ["Königin", "Arbeiterin", "Drohne"], zeilen: [
      { merkmal: "Körper", optionen: ["lang", "mittel", "dick"], loesung: [0, 1, 2], hinweis: "Achte auf den Hinterleib." },
      { merkmal: "Stachel", optionen: ["hat einen", "hat keinen"], loesung: [0, 0, 1] } ] }, B: { … }, C: { … } } }
```
Je Zelle antippen → Optionen (Chips) wählen. „Prüfen“ färbt die Zellen (richtig/falsch) ohne die Lösung zu nennen; erledigt, wenn alle richtig.

Umsetzung: Die Optionen stehen als Chips direkt in der Zelle (ein Tipp statt zwei). Auf schmalen Anzeigen (bis 760 px) wird jede Zeile zu einem Block mit der Spaltenüberschrift über den Chips,
nie waagerecht scrollen. „Prüfen“ verlangt, dass alle Felder gefüllt sind; richtige Zellen werden grün und gesperrt, falsche bleiben änderbar. Zeilen dürfen einen Knopf `modell` und
`hinweis`/`hinweis2` tragen (ab dem zweiten bzw. dritten Fehler der Zeile).

**Spaltenbilder und Zeilenbilder** (Bild statt nur Text, z. B. Kuh · Huhn · Schaf · Biene oder Standbilder aus dem Film). Beides ist freiwillig, darf gleichzeitig vorkommen und
sich mit reinem Text mischen:
```js
spalten: ["Königin", { name: "Arbeiterin", bild: "/static/img/lese/bienenart-arbeiterin.svg", alt: "Arbeiterin" }, { name: "Drohne", bild: "/static/img/lese/bienenart-drohne.svg", alt: "Drohne" }],
zeilen: [{ merkmal: "Die Bienen", bild: "/static/img/film/still-bienen.jpg", alt: "Film: Papierbienen am Flugloch", optionen: ["…"], loesung: [0, 1, 2] }]
```
* **Spalte** = Text **oder** Objekt `{ name, bild, alt }`. Der `name` ist Pflicht und bleibt immer sichtbar (und steht im Protokolltext); `bild` ist ein Pfad unter `/static/…`
  (empfohlen SVG 240 × 180, transparent), `alt` (Bildbeschreibung) ist Pflicht, sobald es ein `bild` gibt. Das Bild steht im Spaltenkopf **über** dem Namen
  (Höhe 72–96 px, `object-fit: contain`) und ist nur zur Anzeige. Bis 760 px steht es im Etikett über den Chips jedes Feldes (64 px hoch, daneben der Name).
* **Zeile** = zusätzlich `bild` + `alt` neben `merkmal` (empfohlen JPG 16:9, 320 × 180). Das Bild steht **über** dem Merkmalstext (etwa 120 px breit, nie breiter als die Zelle) und ist
  **antippbar**: Tippen öffnet es groß im vorhandenen Bild-Fenster (`bild-open`, Schließen per Knopf, Escape oder Tipp daneben).
* Alle Bilder laden verzögert (`loading="lazy"`) und tragen ihr `alt`. Die Tabelle läuft bei 768 und 375 px nie waagerecht über; Chips und Bildknöpfe sind mindestens 44 px hoch.
* Chips dürfen Emoji enthalten; verglichen wird immer der Optionsindex, nie der Text.
* Strukturtest (`tests/forschen_pruefen.py`): Bilddatei vorhanden, `alt` nicht leer, Spaltennamen eindeutig (auch zwischen Text- und Objekt-Spalten).

### `bildwahl` – Entscheiden am Bild (Rätsel)
```js
{ nr: 66, typ: "bildwahl", eyebrow: "Tanzrätsel", titel: "Wo ist das Futter?",
  niveaus: { A: { runden: [ { bild: "/static/img/lese/tanzraetsel-1.svg", breite: 900, hoehe: 560, frage: "Tippe auf die Wiese mit dem Futter.",
      ziele: [{ x: 700, y: 180, r: 70, ok: true }, { x: 200, y: 380, r: 70, ok: false, rueckmeldung: "Der Tanz zeigt in eine andere Richtung." }], hinweis: "…", erklaerung: "…" } ] }, B: { … }, C: { … } } }
```
Tippen auf Trefferkreise (`ok:true` = richtig). Mehrere Runden nacheinander. Rückmeldung ohne die Lösung zu verraten; `erklaerung` nach der richtigen Wahl.

Umsetzung: Nach der richtigen Wahl bleibt die Runde mit der Erklärung stehen, bis „Weiter zu Runde n“ getippt wird. Die Kreise tragen Nummern (Bereich 1, 2, …) und sind mit der Tastatur bedienbar.
Kleine Kreise werden auf dem Bildschirm auf mindestens 44 px Durchmesser vergrößert (Touchziel); trotzdem `r ≥ 60` verwenden. Tipps neben die Kreise werden über die Bildkoordinaten ausgewertet.
`breite`/`hoehe` sind die Pixel des SVG (900 × 560 empfohlen).

### `forscherbuch` – Mein Forscherbuch (Abschluss)
Keine Konfiguration außer `titel`, `hinweis`. Sammelt automatisch je Reiter: Forscherfrage → **meine Vermutung** → **meine Erkenntnis** (Merksatz), dazu die Notizen der Kinder
(Station `notizen`), und bietet „Drucken / als PDF sichern“ (Druckansicht) und „Text kopieren“. Teil des Autosaves (liest nur, speichert nichts Eigenes).

Umsetzung: `vermutung` und `pruefen` werden über die `id` über **alle** Reiter gepaart; die Erkenntnis steht beim Eintrag der Vermutung und nicht doppelt. Weitere Merksätze (`erkenntnis` von
`protokoll`, `tabelle`, `bildwahl` und `pruefen` ohne passende Vermutung) stehen je Reiter unter „Das habe ich noch herausgefunden“. „Abgeben“ schickt den ganzen Text (bis 2000 Zeichen) ins Protokoll der Lehrkraft;
Drucken, Kopieren und Abgeben erledigen die Station. Druckansicht: A4, schlicht, Kopf mit GSM-Logo, Name, Klasse und Datum.

## Weitere Felder der Umsetzung
- **`diagramm` mit `auswertung`**: Textfeld auf Aufgabenebene (z. B. „Lies die Werte ab und vergleiche.“). Nur dann zählt das Diagramm als Forschen-Station; der Text erscheint als Kasten „Auswerten“.
- **Hinweistexte der Standardtypen**: `cfg.hilfe` (nach falscher Antwort bei `mc`, `luecke`, `zuordnung`, `sortierung`, Richtig/Falsch), `cfg.hinweis` (Zuordnung: ersetzt den Anleitungssatz), `cfg.erklaerung` (`mc`),
  Aufgabenfeld `zeigeLoesung: false` (`mc`: die richtige Antwort wird nach einem Fehler nicht markiert). Ohne `cfg.hilfe` verweist die Rückmeldung nur auf die Lesestrecke, wenn sie schon gelesen wurde.

## Lesestrecke nachschlagen (Position)
`tab.leseNach: <nr>` (Aufgabennummer, **nach** der die Lesestrecke als Station erscheint; Standard wäre ganz oben). Die Reihenfolge der Stationen steht je Reiter in
`plan_<reiter>.py` (`STATIONEN`), nicht mehr in `config.py`.

## Audit-Technik T1–T10 (4. Oktober 2026)

Ergebnis des Audits „Funktioniert der forschend-entwickelnde Ansatz?“ (`docs/AUDIT_FORSCHEN_2026-10-04.md`). Die Technik dazu steht in `film.js`, `forschen.js`, `aufgaben.js`,
`kern.js`, `modell3d.js`; die Tests in `tests/film.test.cjs`, `tests/forschen.test.cjs`, `tests/aufgaben.test.cjs`, `tests/modell3d.test.cjs`, `tests/test_forschen.py`, `tests/forschen_pruefen.py`.

### T1 Knöpfe zur Evidenz: spielen sofort, Sekundensprung, Bild-Knopf, Listen
`modell` (an der Aufgabe, an einer Zeile von `protokoll`/`tabelle`) ist **ein Knopf oder eine Liste von Knöpfen**. Ein Knopf ist ein Film-/Modell-Knopf oder ein Bild-Knopf:
```js
modell: [
  { film: "volk", text: "▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)", befehle: [{ mw: "springe", t: 90 }] },     // springt auf 90 s UND spielt sofort
  { film: "volk", text: "Kapitel 7 ansehen", befehle: [{ mw: "kapitel", n: 7 }], pflicht: true },                       // Anfang der Szene, spielt sofort, Pflicht
  { film: "biene3d", text: "Bein von hinten zeigen", befehle: [{ mw: "blick", name: "hinten" }] },                       // 3D-Modell: stellt nur ein
  { bild: "/static/img/lese/nutzen-5-raetsel.svg", text: "Bild noch einmal ansehen", alt: "Rätselbild mit Blühwiese" },  // Bild-Knopf: ohne `film`
]
```
* **Film-Knöpfe spielen sofort ab.** Steht in `befehle` ein `kapitel` oder `springe` (und kein `spielen`/`anhalten`), hängt `film.js` automatisch `{ mw: "spielen" }` an
  (Filme mit Zeitachse: Papiertheater, Archiv-Doku). `spielen: false` am Knopf schaltet das ab, `spielen: true` erzwingt es. Das 3D-Modell spielt nichts. Blockiert der Browser den
  Ton (v. a. iPad), erscheint „Tippe im Filmfenster auf ▶“.
* **Sekundengenau**: `{ mw: "springe", t: 163.5 }` (Sekunden, Zeiten aus `papiertheater/docs/ab_uebergabe.md`). Die Beschriftung `text` nennt Stelle und Satz:
  „▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)“ oder „▶ Sieh dir den Tanz an (Kapitel 9)“.
* **Bild-Knopf** `{ bild, text, alt }` (ohne `film`): öffnet das Bild im Bild-Fenster (Vergrößerung, Schließen per Knopf/Escape). Für Stationen ohne Film/Modell, z. B. der Rückblick
  auf das Bild einer früheren Station. `alt` ist Pflicht (Strukturtest prüft auch, dass die Datei existiert). Ein reiner Bild-Knopf zählt nicht als „arbeitet mit Modell oder Film“.
* **Listen**: In `pruefen`, `protokoll` und `tabelle` darf `modell` eine Liste sein. Aufgaben-Knöpfe stehen als Leiste oben in der Karte (mit ✅ nach dem Ansehen), Zeilen-Knöpfe in der
  Zeile. Mit `quelle` (neutral: „Schau dir Kapitel 5 an.“, nie eine Option vorwegnehmen) und der Liste sehen die Kinder die Evidenz direkt neben der Frage.

### T2 `pruefen` neu gedacht (Entscheidung 1)
* **Vierte Selbsteinschätzung** „Das kann ich hier nicht herausfinden“ – sperrt nichts, die Erkenntnis bleibt wählbar (Protokoll: „kann ich hier nicht herausfinden“).
* **Fehlertexte je Frage**: Erkenntnis-Frage „Das passt noch nicht zu dem, was du beobachtet hast.“; Beleg-Frage „Dieser Beleg passt noch nicht.“ (nie „beobachtet“). Ein eigener Text:
  `erkenntnis.fehltext` / `beleg.fehltext`.
* **`erkenntnis.hinweis` ist Pflicht** (je Niveau; erscheint nach dem zweiten Fehler); `beleg.hinweis` empfohlen.
* **Optionslängen-Regel**: Die richtige Option ist nicht die (allein) längste und nicht kürzer als 70 % der längsten – sonst rät man nach der Länge. Alle Optionen gleich lang und gleich
  gebaut, jede eine prüfbare Einzelaussage über das, was man im Modell/Film/Bild sehen kann; Ablenker sind plausible Vermutungen, die die Evidenz widerlegt. Test:
  `tests/forschen_pruefen.py::pruefen_qualitaet` (echte Inhalte: `test_pruefen_qualitaet`, bis alles umgebaut ist als xfail mit Liste, mit `INHALTE_STRIKT=1` ein Fehler).

### T3 Raten verhindern (`tabelle`, `protokoll`)
Die **erste wirksame Prüfung** meldet nur „x von y Feldern stimmen“ (Tabelle) bzw. „x von y ausgefüllten Zeilen stimmen“ (Protokoll) – **ohne Färbung, ohne Sperre, ohne Hinweise**. Erst ab der
**zweiten** wirksamen Prüfung (nach einer Änderung) werden Felder/Zeilen gefärbt, richtige gesperrt und Hinweise gezeigt. Ein erneutes „Prüfen“ **ohne Änderung** zählt nicht (kein Fehlversuch,
kein Protokolleintrag, Meldung „Du hast seit dem letzten Prüfen nichts geändert“). Ist beim ersten Prüfen alles richtig, ist die Station sofort erledigt.
`cfg.sofortFaerben: true` (je Niveau) schaltet das alte Verhalten ein (färbt sofort). Im Protokoll prüft in der ersten Runde jeder Prüfen-Knopf **alle** ausgefüllten Zeilen; die Lehrkraft sieht
trotzdem je Zeile einen Eintrag. Zustand: `pr` (wirksame Prüfungen) und `sig` stehen im Autosave. In der Zahl der Zeilen steht „x von y Zeilen geschafft“.

### T4 Zahleingabe
`parseZahl` versteht Zahlwörter bis 999 999 (zwölf, einundzwanzig, zweihundertdreiundvierzig, zweitausend, fünfzigtausend, „fünfzig tausend“) und Tausenderformate („50 000“, „50.000“,
„50000“, auch mit Einheit: „50 000 Bienen“). Keine Zahl eingegeben → „Schreibe eine Zahl, zum Beispiel 12.“; `fehlertext` der Zeile überschreibt den Standardtext.

### T5 Standard-Hilfetext
Nach einer falschen Antwort in `luecke`/`sortierung`/`zuordnung`/`mc` steht neutral **„Schau noch einmal genau hin.“** Ein Verweis auf die Lesestrecke erscheint nur, wenn die Aufgabe ihn selbst in
`cfg.hilfe` setzt. Zuordnung: `cfg.hinweis` ersetzt den Standardsatz „Tippe zuerst links auf einen Begriff …“. Mehrfachauswahl meldet „Perfekt – beide/alle N Aussagen stimmen!“.

### T6/T7 Film
* **Film-Karte** (`film`): Balken und Prozent laufen mit **jeder** Statusmeldung mit, die Station hakt bei „vollständig gesehen“ ab.
* **Pflicht-Sperre**: Die Station wird erst frei, wenn **alle** `pflicht`-Knöpfe erfüllt sind – bei Filmen mit Zeitachse nach dem Druck zusätzlich mindestens **3 Sekunden Wiedergabe**
  (Springen und Pausieren zählen nicht), bei 3D-Modell und Bild mit dem Druck. Das Schild zeigt „(1 von 2 geschafft)“; erfüllte Knöpfe tragen ✅, wartende ⏳. Stand im Autosave
  (`filme.knoepfe[nr]` = Liste der erfüllten Knöpfe; alte Stände mit `true` gelten als „alle erfüllt“). Im Prüfmodus der Lehrkraft gibt es keine Sperre.

### T8 Forscherbuch
„Abgeben“ schickt bis **8000** Zeichen (`ANTWORT_MAX_ZEICHEN`, vorher 2000). Das Buch zeigt zu jeder Forscherfrage zusätzlich die **eigene Einschätzung** („Meine Einschätzung: stimmt teilweise“) und – bei
Niveau C – den **eigenen Satz** („Mein Satz dazu: …“). Vermutung: Ein Baustein „weil …“ geht auch ohne Vortext; `min` zählt nur den **eigenen** Text (Bausteine zählen nicht mit);
ein Satzanfang „Meine Vermutung: …“ steht im Text der Vermutung nur einmal.

### T9 Notizen (`notizen`)
Je Aufgabe (oder Niveau) einstellbar: `platzhalter` (Text im Stichpunktfeld, Standard „• Die Biene hat …“), `quelleNoetig: false` (das Feld „Quelle“ ist freiwillig, die Abgabe klappt ohne),
`min` (Zahl der Stichpunkte, Standard 3).

### Nachtrag F1–F7 (4. Oktober 2026, nach den Inhalts-Berichten)
* **F1 Der erste Klick geht nicht verloren.** Ein gerade erzeugter Film-iframe hört noch nicht zu; `film.js` puffert deshalb alle Befehle (Knöpfe, „Film abspielen“, „Moment“) bis zur ersten Meldung des Films
  (`info`/`status`), höchstens `WARTE_AUF_FILM` (6 s) nach dem Laden, und sendet sie dann in der Reihenfolge der Klicks. Der Hinweis „Tippe im Filmfenster auf ▶“ erscheint erst danach. Test: `tests/film.test.cjs` (F1).
* **F2 `fokus` mit `abstand`**: `fokus: { teile: ["fuehler"], blick: "oben", abstand: 2.5 }` (Ziel von `modellfinden`) bzw. der Befehl `{ mw: "fokus", teile, blick?, abstand? }` an einem Knopf. `abstand` ist eine Zahl > 0
  (Kameraabstand beim Heranfahren, ohne Angabe gilt der Standard des Modells); nötig bei Fühler und Facettenauge, die sonst die Bühne füllen. Der Strukturtest prüft `teile`, `blick` und `abstand`.
* **F3 `protokoll`, Zeilenfeld `okText`**: ersetzt „Das stimmt!“ nach einer ausgefüllten Textzeile, z. B. bei einer Vermutungszeile: `okText: "Danke, deine Vermutung ist notiert."`.
* **F4 `mc`, `falschText`**: Der Anfang der Fehlermeldung ist neutral **„Nicht ganz.“** (früher „Leider falsch.“); `cfg.falschText` (je Niveau) oder `falschText` an der Aufgabe setzt einen eigenen Text.
* **F5 `bildwahl` und `bildpunkte`: `auftrag`** (je Niveau oder an der Aufgabe) wird jetzt über dem Bild angezeigt (bei `bildwahl` über jeder Runde).
* **F6 Knopf-Beschriftung**: Beginnt `text` schon mit einem Symbol („▶ Hör zu: …“, „🧊 …“), kommt kein zweites davor – nicht mehr „🎭 ▶ Hör zu“.
* **F7** Lückenfelder (`input.gap-input`, 170 px) laufen bei 768 und 375 px nicht über (Browserprobe); `ASSET_VERSION` erhöht.

### T10 Kleinkram
`normalize` (Eingaben vergleichen): „Wieviele“ = „Wie viele“ (auch wie viel/wie vielen). Startseite: „In **den meisten** Abschnitten vermutest du zuerst etwas.“ 3D-Modell: `modellfinden` blendet die
Bedienleiste des Modells beim Start eines Ziels aus und danach wieder ein (Befehl `leiste`, nur wenn das Modell ihn kennt). `bildpunkte`: Aliase und eigene Rückmeldungen siehe `docs/INHALTE_FORMAT.md`.
