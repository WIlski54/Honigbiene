# Inhalte schreiben: Format aller Aufgabentypen

Referenz für die Inhalts-Agenten des Honigbienen-ABs. Das Gerüst ist fertig und läuft mit Platzhaltern; hier steht,
wie man sie ersetzt. Das Konzept (Reiter, feste Aufgabennummern, Fakten, Wörter) steht in `../AB_KONZEPT.md` im
Elternordner – **dort nachlesen, nichts erfinden**. Alle Beispiele unten sind Muster, keine Inhalte des ABs.

## 1. Wer fasst welche Dateien an

Jeder Reiter hat eigene Dateien. **Niemand bearbeitet die Dateien eines anderen Reiters.**

| Reiter (`key`) | Aufgaben (Browser) | Lesestrecke (Server) | Glossar (Server) | Grafiken |
|---|---|---|---|---|
| `nutztier` | `static/js/inhalte_nutztier.js` | `lesen_nutztier.py` | `glossar_nutztier.py` | `werkzeuge/grafiken_nutztier.py` |
| `koerper` | `static/js/inhalte_koerper.js` | `lesen_koerper.py` | `glossar_koerper.py` | `werkzeuge/grafiken_koerper.py` |
| `volk` | `static/js/inhalte_volk.js` | `lesen_volk.py` | `glossar_volk.py` | `werkzeuge/grafiken_volk.py` |
| `nutzen` | `static/js/inhalte_nutzen.js` | `lesen_nutzen.py` | `glossar_nutzen.py` | `werkzeuge/grafiken_nutzen.py` |
| `abschluss` | `static/js/inhalte_abschluss.js` | – | – | – |

**Stationsplan je Reiter**: `plan_nutztier.py`, `plan_koerper.py`, `plan_volk.py`, `plan_nutzen.py`, `plan_abschluss.py` – jede Datei
gehört der Inhalts-Agentin ihres Reiters und enthält zwei Dinge (`config.ABSCHNITTE` und `tests/plan.py` werden daraus gebaut):

```python
STATIONEN = ["L1", 41, 42, 43, "T"]            # Reihenfolge der Karten im Reiter: Zahlen oder Zeichenketten, plus die Lesestrecke
TYPEN = {41: "vermutung", 42: "protokoll"}      # Typ je Aufgabennummer (ohne Lesestrecke); muss zu `typ` in inhalte_<reiter>.js passen
```

* Nummern sind beliebig, aber **eindeutig im ganzen AB**. Zeichenketten nur in **GROSSBUCHSTABEN** („T“, „F1“) und **nicht mit „L“
  beginnend** (der Server wandelt eingehende Nummern in Großbuchstaben um; „L1“–„L4“ sind die Lesestrecken). `python -m pytest -q tests/test_plaene.py` prüft das.
* **Anzeigenummern: Die Kinder sehen 1, 2, 3 … – nicht diese Nummern.** Sichtbar ist die **Position** der Aufgaben-Stationen (ohne Lesestrecken) über alle Reiter in
  der Reihenfolge von `STATIONEN`; „T“ (Transfer) bekommt **immer die letzte** Nummer; Lesestrecken heißen „Lesestrecke 1–4“. Intern bleiben `nr` und die Plan-Nummern
  unverändert (Autosave, Datenbank, Tests, `leseNach`) – **in Texten der Aufgaben („siehe Aufgabe 41“) deshalb nie eine Nummer nennen.** Quellen: Server `config.ANZEIGE_NR`
  / `anzeige_nr()` / `anzeige_label()` (auch als Jinja-Funktionen), Browser `INHALTE.anzeigeNr()` / `BIE.anzeigeNr()` (`static/js/anzeige.js`, läuft auch auf den Tafel-Seiten).
  Die Lehrkraft sieht im Dashboard die Anzeigenummer, die interne Nummer als Tooltip („intern 41“). `tests/test_anzeige.py` prüft: lückenlos 1…N, eindeutig, T zuletzt, Browser = Server.
* **Die Lesestrecke steht an beliebiger Stelle der Liste** (nicht nur ganz oben), z. B. `[41, 42, 43, "L2", 44, 45]`. Im Reiter-Objekt der
  Inhaltsdatei steht dann `lese: "L2"` **und** `leseNach: 43` (die Nummer der Aufgabe direkt davor). Steht sie oben, entfällt `leseNach`.
  Der Test `test_reiter_passen_zu_abschnitte` prüft, dass `leseNach` zum Plan passt. Der forschende Ansatz verlangt: Sie kommt **nach** der
  ersten Erkundung (`docs/FORSCHEN.md`).
* Die Reihenfolge der Aufgaben in `inhalte_<reiter>.js` ist die Reihenfolge von `STATIONEN` (ohne die Lesestrecke).

Gemeinsam und **nicht ändern** (Änderungswunsch an die Gerüst-Verantwortliche): `static/js/inhalte.js` (Kopf mit
`filme`), `config.py`, `werkzeuge/svg_helfer.py`, alle anderen `static/js/*.js`, `app.py`.
Ausnahme: `zeichenauftraege.py` (Merkmale der drei Zeichnungen) gehört der Inhalts-Agentin des Reiters „Die Biene“
(Zeichnung 1) bzw. den Reitern „Das Bienenvolk“ (2) und „Nutzen & Schutz“ (3), je ein Eintrag.

Aufgaben-Dateien sind ein IIFE, damit eigene Konstanten (z. B. `FILM_ZEITEN`) nicht kollidieren:

```js
(() => {
  "use strict";
  INHALTE.tabs.push({
    key: "koerper", label: "Die Biene", icon: "🧊", kurz: "B", lese: "L2", leseNach: 52,   // leseNach: Aufgabe direkt vor der Lesestrecke (entfällt, wenn sie oben steht)
    film: "biene3d",                      // Bühne mit Modell/Film steht in diesem Reiter
    intro: { eyebrow: "Lesestrecke 2", titel: "Eine Biene ist ein Insekt", begriffe: ["Insekt", "Facettenauge"] },
    aufgaben: [ /* Aufgaben in der Reihenfolge von STATIONEN (plan_<reiter>.py), ohne die Lesestrecke */ ],
  });
})();
```

`key`, `kurz`, `lese` und `leseNach` müssen zum Stationsplan (`plan_<key>.py` → `config.ABSCHNITTE`) passen; die Aufgaben stehen in der
Reihenfolge von `STATIONEN` (ohne die Lesestrecke). `intro.begriffe` listet die Fachbegriffe, die nach der Lesestrecke unter dem Text erscheinen.

## 2. Befehle

```bash
cd arbeitsblatt
python -m pytest -q                      # alle Tests; „Noch nicht geschrieben“ erscheint als Warnung
python -m pytest -q tests/test_inhalte_struktur.py
INHALTE_STRIKT=1 python -m pytest -q tests/test_inhalte_struktur.py::test_inhalte_vollstaendig   # alles da? (ohne Variable: xfail mit Liste)
python werkzeuge/grafiken_<reiter>.py    # SVGs erzeugen → static/img/lese/
python werkzeuge/grafik_uebersicht.py --oeffnen   # alle SVGs im Browser ansehen (Überlappungen!)
node --test tests/modell3d.test.cjs      # Logik der 3D-Modell-Aufgaben
node --test tests/forschen.test.cjs      # Logik der Forschen-Typen (vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch)
python -m pytest -q tests/test_forschen.py tests/test_plaene.py   # Struktur der Forschen-Typen, Stationspläne, Server
INHALTE_STRIKT=1 python -m pytest -q tests/test_inhalte_struktur.py   # auch die Gewichtung (Quoten je Reiter) wird zum Fehler
```

QA-Server (immer ohne KI-Schlüssel und mit Wegwerf-DB, Port **5080**, nie 5060/5061):
`GEMINI_API_KEY="" PORT=5080 DB_PATH=<Wegwerf>.db python app.py` – siehe `README.md`.
Browserprobe der **Forschen-Typen mit den Test-Fixtures** (nicht mit den echten Inhalten): `python werkzeuge/qa_forschen.py` (Port 5085,
Hosts `forschen.localhost` und `lehrer-forschen.localhost`; Details im Kopf der Datei).

`tests/plan.py` ist die Checkliste: Aufgabennummer → Typ, Pflicht-Glossarbegriffe, Teile des Modells. Wer vom Plan
abweicht, ändert ihn dort und sagt es im Bericht.

## 3. Konventionen

* **Sprache**: Sek I, ein Gedanke pro Satz, höchstens etwa 15 Wörter, einfache Wörter, Fachwort beim ersten Mal erklären
  oder ins Glossar. Antwortoptionen ≤ 12 Wörter, Ablenker klar falsch, nicht fies. Fakten und Zahlen **nur** aus
  AB_KONZEPT.md („Gesicherte Fakten“), sonst „etwa“.
* **Feste Wörter** (DaZ: dieselben Wörter in AB, Film und Modell): Bienenstock = ganzes Zuhause, Bienenkasten = Holzkiste
  des Imkers, Flugloch, Wabe, Zelle, Rähmchen, Brutraum, Honigraum, Bienenvolk, Königin, Arbeiterinnen, Drohnen, Ammenbienen,
  Wächterinnen, Sammlerinnen, Rüssel, Nektar, Pollen, Honigmagen, Pollenkörbchen, Larve, Puppe, Schwänzeltanz, Wintertraube,
  Flugmuskeln, Facettenaugen, Fühler.
* **A/B/C**: A antippen statt schreiben (Freitext und Transfer laufen auf A über Textbausteine, `modus: "bausteine"`),
  B Wortspeicher/Satzanfänge, C frei und begründend – in derselben einfachen Sprache.
* **Rückmeldung bei Fehlern verrät die Lösung nicht**, sondern lenkt auf ein sichtbares Merkmal.
* **Lösungsposition variieren** (MC: richtige Option nicht immer zuerst; Lesestrecke: `loesung` 0/1/2 mischen).
* **Film und Modell**: Aufgaben fragen nur, was der Film zeigt oder sagt bzw. was das Modell zeigt. Der Knopf einer
  Aufgabe (`modell`) stellt genau die Ansicht ein, aus der die Antwort folgt.
* **Platzhalter** immer mit dem Wort `PLATZHALTER` kennzeichnen; `test_inhalte_vollstaendig` zählt sie.
* Kommentare auf Deutsch; keine ES-Module (`import`/`export`), die Dateien laufen als klassische Skripte.

## 4. Aufgabentypen

Jede Aufgabe hat `nr`, `typ`, `eyebrow` (kurze Überschrift über dem Titel), `titel`. Differenzierte Typen haben
`niveaus: { A: {…}, B: {…}, C: {…} }`. Alle Texte als einfacher Text (kein HTML), außer in Lesestrecken (siehe 5).

### `mc` – Multiple Choice
```js
{ nr: 2, typ: "mc", eyebrow: "Grundwissen", titel: "Was ist ein Nutztier?",
  niveaus: {
    A: { frage: "…?", optionen: [{ t: "richtig", ok: true }, { t: "falsch", ok: false }, { t: "falsch", ok: false }] },
    B: { frage: "…?", optionen: [ /* 4 Optionen, genau eine ok */ ] },
    C: { multi: 2, frage: "Welche ZWEI Aussagen stimmen?", optionen: [ /* 4 Optionen, genau 2 ok */ ] },
  } }
```
**Richtig/Falsch-Liste** (Aufgaben 5 und 34): statt `optionen` ein Feld `aussagen`. Jede Aussage wird mit „stimmt“ /
„stimmt nicht“ beurteilt; `erklaerung` erscheint nach „alles richtig“. Mindestens eine richtige **und** eine falsche Aussage.
```js
C: { frage: "Stimmt das?", aussagen: [
  { t: "Die Königin befiehlt dem Volk.", ok: false, erklaerung: "Die Königin legt Eier. Befehle gibt sie nicht." },
  { t: "Drohnen haben keinen Stachel.", ok: true } ] }
```
(Typ bleibt `mc`; an der Tafel läuft sie als „richtigfalsch“.)

### `luecke` – Lückentext (Eingaben werden tolerant verglichen)
Lücken stehen als `[Wort]` im Text, Alternativen mit `|`: `[Honigmagen|Honigblase]`. Die erste Schreibweise gilt als
Hauptantwort. Verglichen wird ohne Groß-/Kleinschreibung und Satzzeichen, „ß“ = „ss“ und **Umlaute = ae/oe/ue** („Bestäubung“ = „Bestaeubung“) – das gilt auch für die Namen der
`bildpunkte`-Aufgaben. `modus: "chips"` = Wortkiste zum Antippen (`ablenker`: zusätzliche falsche Wörter), `"input"` = tippen.
```js
{ nr: 4, typ: "luecke", eyebrow: "Fachbegriffe", titel: "…",
  niveaus: {
    A: { modus: "chips", ablenker: ["Wetter"], text: "Ein [Imker] stellt den [Bienenkasten] auf." },
    B: { modus: "input", text: "Der [Honigmagen|Honigblase] ist ein Vorratsbehälter." },
    C: { modus: "input", text: "…" } } }
```

### `zuordnung`
`paare: [[links, rechts], …]` – links ein Begriff (darf mehrfach vorkommen = Kategorie), rechts die Erklärung (**eindeutig**,
mindestens 3 Paare). Die rechte Spalte wird gemischt.
```js
A: { links: "Nutztier", rechts: "Produkt", paare: [["Rind", "Milch"], ["Huhn", "Eier"], ["Schaf", "Wolle"]] }
```

### `sortierung`
`items` in der **richtigen** Reihenfolge (werden gemischt). `hinweis` sagt, wonach sortiert wird.
```js
A: { hinweis: "Fange mit dem Ei an.", items: ["Ei", "Larve", "Puppe"] }
```

### `diagramm`
Das Diagramm steht auf Aufgabenebene (`chart`), die Frage je Niveau (wie `mc`). `datasets[].farbe` (Linie) oder `farben` (Balken).
```js
{ nr: 24, typ: "diagramm", eyebrow: "Diagramm lesen", titel: "…",
  chart: { typ: "line", einheit: "Bienen", yTitel: "Bienen im Volk (ungefähr)", quelle: "Ungefähre Werte. Tippe auf einen Punkt.",
           labels: ["Jan", "Feb"], datasets: [{ label: "Bienen im Volk", data: [10000, 10000], farbe: "#006AB3" }] },
  niveaus: { A: { frage: "…?", optionen: [ /* wie mc */ ] }, B: {…}, C: {…} } }
```

### `freitext` und `transfer` (Nr. „T“)
Niveau A **ohne freies Schreiben**: 4–7 kurze Bausteine (≤ 14 Wörter) in der richtigen Reihenfolge, ein Schlusssatz, ein
Urteil mit genau zwei vertretbaren Optionen. B: Satzanfänge und Begriffe. C: frei. `kontext` (Aufgabenebene) geht an die KI.
```js
{ nr: "T", typ: "transfer", eyebrow: "Transfer · Beurteilen", titel: "…", kontext: "Klasse 6 NW … Begriffe: …",
  niveaus: {
    A: { modus: "bausteine", aufgabe: "…", bausteine: ["Satz 1.", "Satz 2.", "Satz 3.", "Satz 4."], schluss: "…",
         urteil: { frage: "Was meinst du?", optionen: ["Meinung 1.", "Meinung 2."] } },
    B: { aufgabe: "…", starter: ["Ich finde, …", "Dafür spricht, …"], begriffe: ["Bienenvolk"], min: 120 },
    C: { aufgabe: "…", begriffe: ["Bienenvolk", "Bestäubung"], min: 200 } } }
```
`min` = Mindestlänge in Zeichen. „Antwort abgeben“ geht ins Protokoll; „Mit KI prüfen lassen“ braucht die Freigabe der Lehrkraft.

### `notizen` – Meine Stichpunkte (Nr. 7, 17, 28, 37)
```js
{ nr: 7, typ: "notizen", eyebrow: "Eigene Notizen", titel: "Meine Fragen an einen Imker", abschnitt: "nutztier",
  hinweis: "Schreibe Stichpunkte auf.", kiFrage: "Prüfe diese Stichpunkte … (Klasse 6) …" }
```
`abschnitt` = Key des Reiters. Handschrift-Pad und KI-Prüfung sind eingebaut.

### `quellen` (Nr. 40; die Nummer steht im Plan)
```js
{ nr: 40, typ: "quellen", eyebrow: "Quellenverzeichnis", titel: "Meine Quellen", hinweis: "…", min: 2,
  quellenAB: { titel: "Quellen dieses Arbeitsblatts", eintraege: ["Deutscher Imkerbund e. V. (imkerbund.de)", "…"] } }   // optional
```
`quellenAB` (optional) erscheint als aufklappbarer Hinweis „📚 Quellen dieses Arbeitsblatts“ unter der Aufgabe (nur Nennung, keine Zitate).
Höchstens eine Quellen-, eine Blitz- und eine Domino-Aufgabe im AB (der Autosave findet sie über den Typ).

### `zeichnen` (Nr. 15, 26, 35)
```js
{ nr: 15, typ: "zeichnen", eyebrow: "Zeichnen", titel: "Die Biene von der Seite", geraet: "biene",
  niveaus: { A: { aufgabe: "Zeichne …", elemente: ["Kopf", "Brust", "Hinterleib"], hinweis: "Tipp: …" }, B: {…}, C: {…} } }
```
`geraet`: `biene` (15), `schwaenzeltanz` (26), `bestaeubung` (35). `elemente` sind die erwarteten Dinge (gehen mit in den
KI-Auftrag). Die **verbindliche Prüfliste** für die KI-Bewertung steht in `zeichenauftraege.py` (Merkmale in Kindersprache,
am Bild wiederfindbar – „sechs Beine“, nicht „Definition“).

### `zeichnen`: Checkliste im Niveau A

Im Niveau A zeigt die Aufgabe die `elemente` als antippbare Checkliste „Das gehört in deine Zeichnung“ (freiwillig, ohne Bewertung; der Stand wird mit der Zeichnung gesichert).
Die Elemente stehen darum in kurzen, kindgerechten Wörtern („sechs Beine“, „zwei Fühler“).

### `blitz` – Blitzfragen (Nr. 38)
Pool aus allen Reitern, mindestens 16 Fragen; jede Frage kommt nur einmal. `stufe` 1 leicht … 3 schwer; das Niveau wählt
Stufen und Ziel (Zahl richtiger Antworten).
```js
{ nr: 38, typ: "blitz", eyebrow: "Blitzfragen", titel: "Blitzrunde", hinweis: "…",
  niveaus: { A: { ziel: 6, stufen: [1], hinweis: "…" }, B: { ziel: 8, stufen: [1, 2], hinweis: "…" }, C: { ziel: 10, stufen: [1, 2, 3], hinweis: "…" } },
  pool: [{ id: "b01", stufe: 1, frage: "…?", optionen: ["richtig", "falsch", "falsch"], ok: 0 }, …] }
```
IDs `b01`, `b02` … stabil und eindeutig (sie stehen im Autosave).
Die nächste Frage wird zuerst über die **Stufen des Niveaus gleichmäßig** gewählt (nicht nach Poolgröße): Auf Niveau C kommt Stufe 3 etwa zu einem Drittel vor.

### `domino` – Begriffs-Domino (Nr. 39)
Geschlossene Kette: Stein *i* trägt die Erklärung von Paar *i* und den Begriff von Paar *i+1*. `steine` = Zahl der Paare (3 bis
`paare.length`).
```js
{ nr: 39, typ: "domino", eyebrow: "Spiel", titel: "Begriffs-Domino", hinweis: "…",
  niveaus: { A: { steine: 6, hinweis: "…" }, B: { steine: 9, hinweis: "…" }, C: { steine: 12, hinweis: "…" } },
  paare: [{ id: "d01", begriff: "Wabe", definition: "Sechseckige Zellen aus Wachs" }, …] }
```

### `bildpunkte` – Bild mit antippbaren Punkten (Nr. 3, 21; früher „teich“)
Die Karte steht im Kopf des Reiter-Files: `INHALTE.bildpunkte.<karte> = { bild, breite, hoehe, punkte }`. Koordinaten = Pixel
im SVG (900 × 560 empfohlen; Abstand zum Rand ≥ 24, damit der Punkt nicht abgeschnitten wird; **Punkte mindestens 48 px auseinander**, besser ≥ 100).
Auf dem Bildschirm ist jeder Trefferkreis mindestens 44 px groß, der sichtbare Punkt etwa 32 px; bei dicht liegenden Punkten gewinnt der nächste. Der Strukturtest prüft die Abstände
und vergleicht mit `werkzeuge/*_karte_punkte.json`. Das Bild trägt keine Nummern, die
zeichnet das Modul darüber. Die ersten `anzahl` Punkte der Reihenfolge gelten je Niveau.
```js
INHALTE.bildpunkte.imker = {
  bild: "/static/img/lese/imker-karte.svg", breite: 900, hoehe: 560,
  punkte: [{ id: "kasten", x: 500, y: 366, name: "Bienenkasten", kat: 1, aliase: ["Beute"] }, …],
};
// in der Aufgabe:
{ nr: 3, typ: "bildpunkte", karte: "imker", eyebrow: "Bild erkunden", titel: "Beim Imker",
  niveaus: {
    A: { modus: "einordnen", anzahl: 6, namen: true, kategorien: ["Lebewesen", "kein Lebewesen"] },
    B: { modus: "benennen", anzahl: 8, ablenker: ["Spinne"] },        // Namen aus einer Wortkiste wählen
    C: { modus: "benennen", anzahl: 10, eingabe: "text" } } }          // Namen selbst eintippen
```
`einordnen`: jeder Punkt hat `kat` 0 oder 1 (Index in `kategorien`); `namen: false` lässt zusätzlich den Namen eintippen.
`benennen`: richtig ist `name` oder ein Eintrag aus `aliase` (Groß-/Kleinschreibung und Umlaute egal). `hilfe` (optional)
ersetzt den Satz nach einem Fehlversuch. **Eigener Satz für einen typischen Fehlnamen** (Audit T10): `punkte[].falsch = [{ aliase: ["Bienenstock", "Stock"], text: "Der Bienenstock ist das ganze Zuhause
des Volkes. Die Holzkiste heißt …" }]` – gibt ein Kind diesen Namen (und nicht den richtigen) ein, erscheint der Satz unter der Rückmeldung (💡). Richtige Namen und Aliase gehen vor.
**`forschen: true`** (an der Aufgabe oder am Niveau) macht eine `bildpunkte`-Station zur echten Forschen-Station für die Quote – nur, wenn die Kinder dabei Evidenz sammeln (z. B. Futter suchen und
auszählen), nicht beim reinen Benennen (siehe docs/FORSCHEN.md „Gewichtung“).

### Filmbühne in schmalen Anzeigen (unter 1100 px, z. B. iPad hochkant)

Die Bühne klebt über den Aufgaben (höchstens 40 % der Höhe). **In Stationen ohne Film-/Modell-Bindung steht sie eingeklappt** (Kopfzeile „▸ Film zeigen“, die Kinder
klappen sie jederzeit auf); eine gebundene Station klappt sie auf und zeigt den passenden Film. **Gebunden** = Typ `film`, `filmmoment`, `erkunden`, `modellfinden`,
ein Aufgaben-Knopf `modell` oder ein Zeilen-/Zellen-Knopf `modell` (`protokoll`, `tabelle`). Der Reiter braucht dafür kein `tab.film`, wenn eine Station gebunden ist.
Bei breiten Anzeigen (ab 1100 px) steht die Bühne unverändert neben den Aufgaben.

### `film` – Film ansehen (Nr. 18)
```js
{ nr: 18, typ: "film", film: "volk", eyebrow: "Film", titel: "Den Film ansehen", auftrag: "Sieh dir den Film ganz an.",
  beobachtung: ["Wer legt die Eier?", "Wie viele Arten von Bienen gibt es?"] }
```
Station erledigt bei ≥ 95 % **echt** abgespielter Zeit (Springen zählt nicht). 2–3 Beobachtungsaufträge, die später
wieder aufgegriffen werden. Die Fragen müssen sich aus dem Film beantworten lassen.

### `filmmoment` – Finde den Moment (Nr. 19)
Die Zeitfenster stehen an **einer** Stelle am Dateianfang (`FILM_ZEITEN`), bis `papiertheater/docs/ab_uebergabe.md` die
Satzzeiten liefert. `start` = Sekunde, ab der der Film läuft; `fenster` = [von, bis] in Sekunden. Szene *n* liegt bei
(n−1)·20 … n·20 s. Niveau A zeigt den Tipp sofort, B nach einem Fehler, C nach zwei.
```js
{ nr: 19, typ: "filmmoment", film: "volk", eyebrow: "Film", titel: "Finde den Moment", start: 78,
  zu_frueh: "Noch zu früh.", zu_spaet: "Das war schon danach.", erklaerung: "Hier legt die Königin ein Ei.",
  niveaus: { A: { frage: "Halte an, wenn …", fenster: [84, 98], tipp: "Achte auf …" }, B: { … fenster: [86, 96] … }, C: { … fenster: [88, 94] … } } }
```

### `erkunden` – 3D-Modell erkunden (Nr. 8)
```js
{ nr: 8, typ: "erkunden", film: "biene3d", eyebrow: "3D-Modell", titel: "Das 3D-Modell erkunden",
  auftrag: "Öffne das Modell. Sieh dir erst außen, dann innen, zuletzt die Explosion an.",
  beobachtung: ["Wie viele Beine siehst du?", "Was liegt im Hinterleib?"] }
```
Fortschrittsbalken = Erkundungsfortschritt des Modells (je ein Drittel für Außenansicht, Situs, Explosion); erledigt bei ≥ 95 %.
Optional `niveaus: { A: { auftrag, beobachtung }, … }`, `knopf` (Beschriftung des Hauptknopfs), `ansichten: [{ name, label }]`.

### `modellfinden` – Tippe im Modell auf … (Nr. 9)
```js
{ nr: 9, typ: "modellfinden", film: "biene3d", eyebrow: "Im Modell", titel: "Tippe im Modell auf …",
  niveaus: {
    A: { auftrag: "…", ziele: [
      { teil: "kopf", frage: "Tippe auf den Kopf.", hinweis: "Dort sitzen die Augen.", ansicht: "gestalt" },
      { teil: "ruessel", frage: "Tippe auf den Rüssel.", hinweis: "…", blick: "vorn" },
      { teil: "honigmagen", frage: "Tippe auf den Honigmagen.", hinweis: "Er liegt im Hinterleib.", ansicht: "situs" } ] },
    B: { … }, C: { … } } }
```
`teil` = Schlüssel aus: `kopf, brust, hinterleib, fuehler, facettenauge, ruessel, fluegel, bein, vorderbein, mittelbein, hinterbein,
pollenkoerbchen, honigmagen, darm, herz, gehirn, flugmuskeln, stachel, luftsaecke`. Das Modell meldet bei jedem Tipp eine Liste der Schlüssel des
getippten Teils (das speziellste zuerst); ein Tipp ist richtig, wenn `teil` in dieser Liste steht. Ein Hinterbein meldet z. B.
`hinterbein` und `bein` (trifft also das Ziel „bein“), ein Facettenauge `facettenauge` und `kopf` (trifft also auch das Ziel „kopf“), das Pollenkörbchen `pollenkoerbchen`, `hinterbein`, `bein`.
Brust, Hinterleib, Fühler und Flügel melden nur sich selbst. Rüssel und Stachel sind in der Standardansicht winzig (der Rüssel liegt hinter
dem Auge): Für solche Ziele `blick: "vorn"` (bzw. passend zum Teil) eintragen. `blick` (optional): Kamerablick `seite`, `oben`, `vorn`, `hinten`, `schraeg` (Standard) –
wird vor dem Wählmodus eingestellt; `ansicht` (optional):
`gestalt` (Standard), `situs`, `explosion` – **Innenteile (honigmagen, darm, herz, gehirn, flugmuskeln, stachel, luftsaecke) nur ab
`situs` antippbar.** `hinweis` zeigt nach einem Fehlversuch auf ein **sichtbares Merkmal und verrät den Namen des Teils nicht**;
nach zwei Fehlversuchen leuchtet das Teil im Modell auf. Tipp ins Leere zählt nicht als Fehlversuch.

**Ziel-Feld `fokus`** (optional): `fokus: { teile: ["ruessel"], blick: "vorn" }` – das Modell fährt vor dem Wählen an die Ankerregion der Teile
(Modellbefehl `fokus`, **ohne etwas zu markieren**: die Lösung bleibt geheim, Tippen bleibt möglich; `blick` optional, ohne `blick` nutzt ein einzelnes
Teil seine Standardrichtung). Praktisch für kleine Teile (Rüssel, Stachel, Herz). Reihenfolge der Befehle je Ziel: `zurueck` (setzt Ansicht, Hervorhebung,
Schilder und Kamera zurück – nichts aus anderen Aufgaben bleibt stehen) → `ansicht` → `blick` → `fokus` → `waehlen`. `fokus.teile` müssen Teile des Modells sein
(Strukturtest prüft das).

### Forschen-Typen: `vermutung`, `pruefen`, `protokoll`, `tabelle`, `bildwahl`, `forscherbuch` (Modul `static/js/forschen.js`)

Der forschend-entwickelnde Ansatz (Jahrgang 6): Die Kinder vermuten, beobachten, zählen, vergleichen und halten Erkenntnisse selbst fest –
mit 3D-Modell, Film und Bildern. **Die Spezifikation steht in `docs/FORSCHEN.md`** (Phasen, Gewichtung, alle Felder); **lauffähige Mini-Beispiele
mit A/B/C für jeden Typ** in `docs/FORSCHEN_BEISPIELE.js` (nicht geladen, aber vom Test `tests/test_forschen.py` geprüft). Kurzfassung:

| Typ | Idee | Wichtige Felder (je Niveau A/B/C außer `forscherbuch`) |
|---|---|---|
| `vermutung` | Forscherfrage, Vermutung **ohne Bewertung**; „Vermutung festhalten“ sperrt die Karte | `id` (eindeutig); A `optionen` (+ `mehrfach`) · B `optionen`, `satzanfang`, `begruendung` · C `satzanfang`, `frei: true`, `min` |
| `pruefen` | Vermutung (per `id`) mit der Beobachtung vergleichen | Aufgabenebene: `vermutung` (id), `quelle`, **`erkenntnis`** (Merksatz); A `erkenntnis {frage, optionen[{t, ok}]}` · B + `beleg` · C + `satz {anfang, min}` |
| `protokoll` | Forscherbogen: Zeilen mit Prüfung | `zeilen[{frage, art: zahl/wahl/mehrfach/text, loesung, toleranz, einheit, schritt, optionen, min, hinweis, hinweis2, fehlertext, erklaerung, kurz, modell}]`, optional `schluss {anfang, bausteine, min, pflicht}` |
| `tabelle` | Vergleichstabelle zum Ausfüllen (erste Prüfung nur Zählung, `cfg.sofortFaerben: true` färbt sofort) | `spalten` (Text **oder** `{name, bild, alt}`, auch gemischt), `zeilen[{merkmal, bild, alt, optionen, loesung (je Spalte ein Index), hinweis, hinweis2, modell}]` – `bild`/`alt` bei Spalte und Zeile freiwillig (Spaltenbild über dem Namen, Zeilenbild antippbar zum Vergrößern; `alt` Pflicht, Datei muss existieren) |
| `bildwahl` | Entscheiden am Bild in Runden | `runden[{bild, breite, hoehe, frage, ziele[{x, y, r, ok, rueckmeldung}], hinweis, erklaerung}]` |
| `forscherbuch` | „Mein Forscherbuch“ (Abschluss, höchstens eins im AB) | nur `titel`, `hinweis`; sammelt automatisch (Drucken/PDF, Text kopieren, abgeben) |

Gemeinsame Regeln:

* **Rückmeldungen verraten die Lösung nicht**: falsch → freundlicher Satz; nach zwei Fehlern kommt `hinweis`, nach drei `hinweis2`
  (bzw. blinkt der Zeilen-Knopf `modell`). Hinweise zeigen auf ein sichtbares Merkmal, nennen nie die Antwort.
* **`erkenntnis`** (Aufgabenebene, ein Satz) ist der Merksatz: Er erscheint, sobald die Station geschafft ist, und steht im Forscherbuch.
  Das Forscherbuch paart `vermutung` und `pruefen` über die `id` über **alle** Reiter (Frage in einem, Prüfen in einem anderen Reiter ist erlaubt);
  die Erkenntnis steht beim Eintrag der Vermutung und nur dort. Merksätze von `protokoll`, `tabelle`, `bildwahl` erscheinen unter „Das habe ich noch herausgefunden“.
* **`modell`** (Aufgabenfeld) wie bei jeder Aufgabe; zusätzlich Zeilen-Knöpfe `modell` in `protokoll` und `tabelle`
  (sie öffnen genau die Ansicht, aus der die Antwort folgt). Dafür `tab.film` im Reiter setzen. **`modell` darf überall eine LISTE von Knöpfen sein** (auch in `pruefen`). Film-Knöpfe
  **spielen sofort ab** (`kapitel`/`springe` → `spielen` wird angehängt; `spielen: false` schaltet das ab), Sekundensprung `{ mw: "springe", t: 163.5 }`, und es gibt den **Bild-Knopf**
  `{ bild: "/static/img/lese/….svg", text, alt }` (ohne `film`, öffnet das Bild groß). `pflicht: true` an einem Knopf sperrt die Station, bis **alle** Pflicht-Knöpfe gedrückt wurden
  (Filme zusätzlich 3 s Wiedergabe). Beschriftung nennt Stelle und Satz: „▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)“. Details: `docs/FORSCHEN.md`, Abschnitt „Audit-Technik T1–T10“.
* **Touchziele**: `bildwahl`-Kreise bekommen mindestens 44 px Durchmesser (kleine Kreise werden vergrößert, bei Überlappung gewinnt der nächste
  Mittelpunkt); `r ≥ 60` ist trotzdem empfohlen. Der Strukturtest warnt bei kleineren Kreisen.
* **Prüfmodus der Lehrkraft**: Lösungen sichtbar, alles frei; Vermutungen und das Forscherbuch erscheinen mit einem Beispiel gefüllt.
* **Protokolltexte** sind lesbar („Vermutung: etwa 5 000“, „Beobachtung: Beine = 6 ✅“); `vermutung` hat keine Bewertung (`korrekt` leer).
  Die Auswahl steht nach „Vermutung: “, mehrere Optionen mit „ | “, die Begründung nach „ · “ (das Dashboard wertet das aus).
* **Wann eine Vermutung?** Eine Vermutung nur dort stellen, wo sie **innerhalb des Reiters (in den folgenden Stationen) geprüft** werden kann; sonst ist es eine
  einfache Frage mit Rückmeldung (`mc`). `pruefen` zeigt immer auf eine vorhandene `vermutung.id`.
* **`pruefen` (Audit T2)**: `erkenntnis.hinweis` je Niveau Pflicht; vierte Selbsteinschätzung „Das kann ich hier nicht herausfinden“; Fehltexte `erkenntnis.fehltext`/`beleg.fehltext`; die richtige
  Option ist nicht die längste und nicht kürzer als 70 % der längsten; `quelle` neutral (nennt keine Option); Knopf zur Evidenz in `modell`.
* **Gewichtung** je Reiter (Abschluss ausgenommen, Details `docs/FORSCHEN.md`): Forschen ≥ 50 % (Reiter `nutztier`: ≥ 25 %, dort auch keine Pflicht zu `vermutung`/`pruefen`/`erkenntnis`; `MIN_FORSCHEN`, `OHNE_VERMUTUNG`), Sprachwerkstatt ≥ 2, Abfrage ≤ 30 %,
  ≤ 12 Stationen inklusive Lesestrecke (Reiter `volk` 13, Abschluss 6). Zahlen und Typen stehen in `tests/plan.py`; geprüft von
  `tests/test_inhalte_struktur.py::test_gewichtung_forschen` (bis die Inhalte umgebaut sind: erwarteter Fehlschlag mit Liste).
* Ein **Diagramm** zählt als Forschen-Station, wenn die Aufgabe das Feld `auswertung` (Text, z. B. „Lies die Werte ab und vergleiche.“) trägt;
  es wird als Kasten „Auswerten“ über dem Diagramm gezeigt.

### Nachtrag F2–F6 (Felder)
`fokus: { teile, blick?, abstand? }` (Ziel von `modellfinden`; `abstand` Zahl > 0), `protokoll`-Zeile `okText` (ersetzt „Das stimmt!“), `mc` `falschText` (Standard „Nicht ganz.“), `auftrag` bei `bildwahl`/`bildpunkte` (wird angezeigt),
Knopf-Texte mit eigenem Symbol („▶ Hör zu: …“) bekommen kein zweites. Details: `docs/FORSCHEN.md`, Abschnitt „Nachtrag F1–F7“.

### `notizen`: Platzhalter und Quelle einstellbar (Audit T9)
`platzhalter` (Text im Stichpunktfeld, Standard „• Die Biene hat …“), `quelleNoetig: false` (das Feld „Quelle“ ist freiwillig, die Abgabe klappt ohne), `min` (Zahl der Stichpunkte, Standard 3) –
an der Aufgabe oder je Niveau. Beispiel: `{ nr: 7, typ: "notizen", abschnitt: "nutztier", hinweis: "…", platzhalter: "• Wie viele Bienenkästen hast du?\n• Warum …?", quelleNoetig: false }`.

### Hinweistexte der Standardtypen (`mc`, `luecke`, `zuordnung`, `sortierung`, Richtig/Falsch)

* `cfg.hilfe` (je Niveau, Text): Satz, der nach einer falschen Antwort angezeigt wird. Ohne Eintrag steht **neutral** „Schau noch einmal genau hin.“ – ein Verweis auf die Lesestrecke
  („Ein Blick in die Lesestrecke hilft.“) erscheint nur, wenn die Aufgabe ihn selbst in `hilfe` setzt (Audit T5; wichtig bei Aufgaben vor der Lesestrecke und in der Sprachwerkstatt).
* `mc`: `cfg.erklaerung` (je Niveau) erscheint nach der Antwort; das Aufgabenfeld `zeigeLoesung: false` verrät die richtige Antwort nach einem Fehler nicht
  (für Forscher-Aufgaben; Standard `true` wie bisher).
* `zuordnung`: `cfg.hinweis` ersetzt den Satz „Tippe zuerst links auf einen Begriff …“ (z. B. bei Wortbildung).

### `modell` – Knopf an jeder Aufgabe (Feld einer beliebigen Aufgabe)
Der Knopf stellt Film bzw. Modell ein. `pflicht: true` sperrt die Aufgabe, bis der Knopf gedrückt wurde (modellgebundene
Aufgabe). Auch als Liste möglich.
```js
modell: { film: "volk", text: "Im Film ansehen (Kapitel 5)", befehle: [{ mw: "kapitel", n: 5 }], pflicht: true }
modell: { film: "biene3d", text: "Im Modell ansehen", befehle: [{ mw: "ansicht", name: "situs" }, { mw: "hervorheben", teile: ["honigmagen"] }] }
```
Befehle **Film** (`volk`): `springe` (`t` in s), `kapitel` (`n` 1–12), `spielen`, `anhalten`. Befehle **Modell** (`biene3d`): `ansicht`
(`name` gestalt/situs/explosion oder `wert` 0–1), `blick` (`name` seite/oben/vorn/hinten/schraeg), `hervorheben` (`teile`, `fokus`),
`beschriften` (`an`, `teile`), `nummern` (`teile`), `waehlen` (`an`), `zurueck`. Jeden Knopf im Browser prüfen: Zeigt die Ansicht
wirklich, wonach gefragt wird?

## 5. Lesestrecken (`lesen_<reiter>.py`)

```python
LESESTRECKEN = {
    "koerper": {                                # Key = Reiter
        "station": "L2", "eyebrow": "Lesestrecke 2",
        "titel": "Eine Biene ist ein Insekt",
        "abschnitte": [                         # 4–7 Abschnitte (Konzept: 4–5)
            {
                "ueberschrift": "Drei Körperteile, sechs Beine",
                "bild": "koerper-1", "bild_alt": "Schaubild: Biene von der Seite, drei Abschnitte farbig",
                "text": "Eine Biene hat drei Körperteile.\nDas sind Kopf, Brust und Hinterleib.\nSie hat <strong>sechs</strong> Beine.",
                "frage": "Wie viele Beine hat eine Biene?",
                "optionen": ["Acht", "Sechs", "Vier"],     # genau 3, kurz
                "loesung": 1,                              # Index der richtigen Option, über die Abschnitte variieren
                "erklaerung": "Richtig: Insekten haben sechs Beine. Spinnen haben acht.",
            },
        ],
    },
}
```
* 2–4 kurze Sätze je Abschnitt (≤ 15 Wörter), `\n` zwischen den Sätzen. **Ein Schaubild je Abschnitt** (`bild` = Dateiname ohne `.svg`).
* Die Frage lässt sich **allein aus dem Abschnitt** beantworten. Lösungen bleiben auf dem Server (Sperre 60/75/90 s nach Fehlversuch).
* **Fette Begriffe** (`<strong>…</strong>`) brauchen einen Glossar-Eintrag (oder sind ein Datum) – der Test prüft das.
* `"platzhalter": True` entfernen, sobald die Strecke echt ist (steht im Platzhalter und wird von den Tests gezählt).

## 6. Glossar (`glossar_<reiter>.py`)

```python
EINTRAEGE = {
    "facettenauge": {
        "titel": "Facettenauge", "bild": "glossar-facettenauge",   # Bild oder None
        "text": "Das Facettenauge besteht aus etwa 5 000 Einzelaugen. Die Biene sieht damit Bewegungen sehr gut.",
        "aliase": ["Facettenauge", "Facettenaugen"],
    },
}
```
Schlüssel = ASCII-Kleinschreibung, eindeutig über **alle** `glossar_*.py`; Aliase eindeutig über das ganze Glossar (sonst Fehler
beim Import). Text höchstens ~400 Zeichen, 2–4 kurze Sätze. Pflichtbegriffe und welche ein Bild brauchen: `tests/plan.py`.

## 7. Grafiken

* Ordner `static/img/lese/`, Format **SVG**, viewBox **480 × 288** (Lesestrecke, Glossar) bzw. **900 × 560** (Karten für `bildpunkte`).
* Namen: `<reiter>-<n>.svg` für Lesestrecken-Abschnitte (`nutztier-1.svg` … `nutzen-5.svg`), `glossar-<schluessel>.svg` für
  Glossarbilder, `<name>-karte.svg` für Karten (`imker-karte.svg`, `stock-karte.svg`). `platzhalter*.svg` sind die Platzhalter.
* Erzeugt von `werkzeuge/grafiken_<reiter>.py` mit den Helfern aus `werkzeuge/svg_helfer.py`:
  ```python
  from svg_helfer import *
  def nutztier_1():
      return svg("Bauernhof mit Bienenkästen am Rand", himmel_wiese(170), sonne(410, 48), baum(60, 190, .9), ...,
                 fussleiste(["Nutztiere helfen uns"]))
  GRAFIKEN = {"nutztier-1": nutztier_1}
  if __name__ == "__main__":
      erzeuge(GRAFIKEN)
  ```
* Gegenständliche, plastische Szenen (Verläufe, Schatten), **keine Kästchen-Schemata**. Pfeilbeschriftung über oder unter dem
  Pfeil (≥ 10 px Abstand), nie auf der Linie, mit weißem Halo. Animation nur als CSS-Keyframes im SVG, Endzustand trägt die Aussage.
* **Vor dem Abgeben alle Bilder ansehen**: `python werkzeuge/grafik_uebersicht.py --oeffnen`.
* Bilder, die später durch echte Abbildungen ersetzt werden, behalten den Dateinamen (und `ASSET_VERSION` in `config.py` wird erhöht).

## 8. Bildnamen im Präsentationsmodus

Der Präsentationsmodus der Lehrkraft listet das Einstiegsbild (`imker-karte`, bis es existiert der Platzhalter) und alle Schaubilder
der Lesestrecken (`<reiter>-<abschnitt>`) – dafür ist nichts zu tun, außer dass jeder Abschnitt ein `bild` hat.
