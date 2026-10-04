# Konzept: Interaktives Arbeitsblatt „Die Honigbiene – ein Nutztier mit eigenem Staat“

> **Stand 4. Oktober 2026 – maßgebliche Struktur.** Der Aufbau wurde auf Wunsch von Stephan **forschend-entwickelnd** umgebaut
> (Details: `arbeitsblatt/docs/FORSCHEN.md`). Die Tabelle „Aufgabenplan“ und die Lesestrecken-Liste weiter unten beschreiben die
> **erste, lese-lastige Fassung** und bleiben nur als Quelle der Fakten, Wörter und Bildideen stehen. Die gültige Reihenfolge der
> Stationen steht je Reiter in `arbeitsblatt/plan_<reiter>.py` (`STATIONEN`, `TYPEN`).
>
> | Reiter | Stationen (Reihenfolge) | Forschen / Sprachwerkstatt / Abfrage |
> |---|---|---|
> | Nutztier Biene | 41, 42 (Vermutungen) · 3 Bild „Beim Imker“ · 43 Tabelle Kuh–Huhn–Schaf–Biene · **L1** · 44 Prüfen · 45–47 Sprachwerkstatt · 7 Notizen | 56 % / 33 % / 0 % |
> | Die Biene (3D) | 50 Vermutung · 8 Erkunden · 9 Im Modell finden · 51 Forscherbogen · 52 Prüfen · 53 Vermutung · 54 Tabelle Innenleben · 55 Prüfen (Film Szene 8) · **L2** · 56, 57 Sprachwerkstatt · 15 Zeichnung | 82 % / 18 % / 0 % |
> | Das Bienenvolk (Film) | 60 Vermutung · 18 Film · 61 Prüfen · 62 Beobachtungsbogen · 63 Tabelle Arten · 64 Prüfen · 21 Kasten beschriften · 66 Tanzrätsel · 68 „Echt oder nur im Film?“ · **L3** · 65, 67 Sprachwerkstatt · 26 Zeichnung | 83 % / 17 % / 0 % |
> | Nutzen & Schutz | 70 Vermutung · 71 Forscherbogen Honig (Film) · 72 Apfelzweige (Beispielversuch) · 73 Prüfen · 74 Vermutung · 75 Bild-Rätsel Gefahren · 76 Prüfen · **L4** · 77, 36 Sprachwerkstatt · 35 Zeichnung · 37 Notizen | 73 % / 18 % / 0 % |
> | Abschluss | 80 Forscherbuch · 38 Blitz · 39 Domino · 40 Quellen · T Transfer (Sprachwerkstatt) | – |
>
> Gesamt 52 Stationen. Entscheidungen des Leiters: Wort **„Zuckerlösung“** (nicht „Zuckerfutter“); Funktionen von Herz („pumpt das Blut“) und
> Gehirn („steuert die Biene“) sind als Standardwissen **vorläufig freigegeben** (bitte prüfen); „drittwichtigstes Nutztier“ nur mit „gilt oft als“.


Stand 3. Oktober 2026 · Stephan Wilski, Gesamtschule Meiderich · Fach NW (Naturwissenschaften), **Jahrgang 6**,
Thema **Nutztiere**, **Klassenunterricht** (heterogene Klasse, Niveau A/B/C je Aufgabe, Niveau A ohne freies Schreiben).
Originalarbeitsblatt: **keines** – alle Texte und Aufgaben sind Originale.
Tafel (digitale Tafel für die Sicherungsphase): **Ja** (Pilotbaustein, `references/tafel.md` im Skill `ab-bauen`).

## Ordnerstruktur (alles in einem Git-Projekt)

```
Honigbiene/                 bestehendes Vite/Three.js-Projekt „Anatomie in Bewegung“ (3D-Modell, Explosion)
├── papiertheater/          Film „Ein Bienenvolk im Bienenstock“ (Skill papiertheater-bauen), Drehbuch: papiertheater/drehbuch.md
├── arbeitsblatt/           das Flask-Arbeitsblatt (Skill ab-bauen; Basis: D:\KI Projekte\Ökologie Einstieg)
│   └── static/film/        bienenmodell/ (gebautes 3D-Projekt) + Ein_Bienenvolk_im_Bienenstock.html
└── AB_KONZEPT.md           diese Datei
```
Kürzel (JS-Namespace) des ABs: **`BIE`** (statt `OEK` der Ökologie-Basis). `APP_ID = "gsm-nw-honigbiene-6"`.

## Leitfrage und Aufbau

Leitfrage: *„Warum gehört die Honigbiene zu den wichtigen Nutztieren – obwohl sie niemand in den Stall sperrt, melkt oder füttert?“*

Fünf Reiter, **nacheinander** freigeschaltet (Schrittmodus). Jeder Reiter beginnt mit einer Lesestrecke (L1–L4).
Ein Reiter ist einzeln im Unterricht nutzbar (Reihe über ca. 3–4 Doppelstunden):

| key | Titel | Icon | Kürzel | Inhalt | Film/Modell |
|---|---|---|---|---|---|
| `nutztier` | Nutztier Biene | 🐝 | N | Was ist ein Nutztier? Biene anders als Kuh & Huhn. Imker. | – |
| `koerper` | Die Biene | 🧊 | B | Insektenkörper, Sinne, Flügel, Honigmagen, Pollenkörbchen, Innenleben (Situs) | **3D-Modell** `biene3d` |
| `volk` | Das Bienenvolk | 🎭 | V | Bienenstock, Wabe, Königin/Arbeiterin/Drohne, Entwicklung, Aufgaben, Tanz | **Papiertheater** `volk` |
| `nutzen` | Nutzen & Schutz | 🍯 | S | Honig, Wachs, Bestäubung, Imkerjahr, Gefahren | Knöpfe in den Film `volk` |
| `abschluss` | Abschluss & Quellen | 🏁 | A | Blitzfragen, Domino, Quellen, Transfer | – |

## Aufgabenplan (Nummern fest; Typen aus der Basis, neue Typen siehe unten)

`config.py → ABSCHNITTE` (muss zu `inhalte` passen):

```
nutztier : L1, 1, 2, 3, 4, 5, 6, 7
koerper  : L2, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
volk     : L3, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28
nutzen   : L4, 29, 30, 31, 32, 33, 34, 35, 36, 37
abschluss: 38, 39, 40, "T"
```

| Nr | Typ | Aufgabe | Bindung |
|---|---|---|---|
| 1 | zuordnung | Nutztier ↔ Produkt (Rind–Milch, Huhn–Eier, Schaf–Wolle, Biene–Honig …) | L1 |
| 2 | mc | Was macht ein Tier zum Nutztier? | L1 |
| 3 | bildpunkte | Bild „Beim Imker“ (Bienenkasten, Imker, Schleier, Rauchgerät, Blüten, Honigglas, Obstbaum …) benennen/sortieren („Teich“-Typ der Basis, umbenannt) | SVG `imker-karte.svg` |
| 4 | luecke | Nutztier, Imker, Honig, Wachs im Satz | L1 |
| 5 | mc | Richtig/falsch zu Nutztieren und Bienen | L1 |
| 6 | mc | **Schätzfrage**: Wie viele Bienen leben im Sommer in einem Stock? (Auflösung im Film, S1) | später im Film wieder aufgegriffen |
| 7 | notizen | Meine Fragen an einen Imker (Handschrift-Pad) | |
| 8 | **erkunden** | 3D-Modell erkunden: Außenansicht → Situs → Explosion (Beobachtungsfragen) | Modell `biene3d` |
| 9 | **modellfinden** | „Tippe im Modell auf …“ (A: Kopf, Brust, Hinterleib, Flügel, Bein · B: + Fühler, Hinterbein, Rüssel · C: + Facettenauge, Pollenkörbchen, Stachel) | Modell, Pick |
| 10 | zuordnung | Körperteil ↔ Aufgabe (Kopf: sehen/riechen/fressen · Brust: fliegen/laufen · Hinterleib: verdauen/stechen/Wachs) | Modell-Knopf hervorheben |
| 11 | mc | Insekt oder nicht? (6 Beine, 3 Körperteile; Spinne mit 8 Beinen als Gegenbeispiel) | L2 |
| 12 | luecke | Körperbau der Biene im Satz | L2 |
| 13 | zuordnung | Organ ↔ Aufgabe im Situs (Honigmagen, Herz, Darm, Gehirn, Flugmuskeln, Stachel mit Giftblase) | Modell-Knopf Situs + Nummern |
| 14 | sortierung | Der Weg des Nektars durch die Biene (Blüte → Rüssel → Honigmagen → Stock …) | L2 + Film S8 |
| 15 | zeichnen | **Zeichnung 1**: Biene von der Seite (Kopf, Brust, Hinterleib, 6 Beine, Fühler, Flügel), KI-Bewertung nach Freigabe | |
| 16 | mc | **Modellkritik**: Was zeigt das 3D-Modell richtig, was nicht? (Farben der Organe, Haare, Größe 12–14 mm …) | Modell |
| 17 | notizen | Meine Stichpunkte zur Biene | |
| 18 | **film** | Film ansehen mit Beobachtungsaufträgen | Film `volk` |
| 19 | **filmmoment** | Finde den Moment: Die Königin legt ein Ei (S5) | Film `volk` |
| 20 | zuordnung | Wer macht was? Königin / Arbeiterin / Drohne | Knopf Kapitel 4+5 |
| 21 | bildpunkte | **Bienenstock beschriften**: Dach, Flugloch, Brutraum, Honigraum, Rähmchen, Wabe, Boden | SVG `stock-karte.svg`, Knopf Kapitel 2+3 |
| 22 | sortierung | Entwicklung: Ei → Larve → Puppe → junge Biene (mit Tagen) | Knopf Kapitel 6 |
| 23 | sortierung | Das Leben einer Arbeiterin: putzen → füttern → bauen/Wache → sammeln | Knopf Kapitel 7+8 |
| 24 | diagramm | Bienen im Volk über das Jahr (Linie, „ungefähre Werte“): Wann viele, wann wenige? | L3 |
| 25 | zuordnung | Was verrät der Tanz? (Richtung ↔ Weg, Dauer ↔ Entfernung) | Knopf Kapitel 9 |
| 26 | zeichnen | **Zeichnung 2**: Der Schwänzeltanz (senkrechte Wabe, Tänzerin, Sonne, Richtungslinie) | Knopf Kapitel 9 |
| 27 | mc | **Filmkritik**: Was im Film ist vereinfacht/nachgestellt, was ist so in echt? | Film |
| 28 | notizen | Meine Stichpunkte zum Bienenvolk | |
| 29 | zuordnung | Nutzen der Biene: Honig / Wachs / Bestäubung ↔ Beispiele | L4 |
| 30 | sortierung | Vom Nektar zum Honigglas | Knopf Kapitel 8+10 |
| 31 | mc | Bestäubung: Warum braucht der Apfelbaum die Biene? | L4 |
| 32 | luecke | Bestäubung/Honig im Satz | L4 |
| 33 | zuordnung | Imkerjahr: Jahreszeit ↔ Arbeit des Imkers | L4 |
| 34 | mc | Stimmt das? Bienen-Irrtümer (Die Königin befiehlt nicht · Drohnen haben keinen Stachel · …) | Film S5/S4 |
| 35 | zeichnen | **Zeichnung 3**: Bestäubung (Biene an Blüte → Pollen → Frucht) | |
| 36 | freitext | Was können wir für Bienen tun? (KI-Rückmeldung nach Freigabe; A Bausteine, B Satzanfänge, C frei) | |
| 37 | notizen | Meine Stichpunkte zu Nutzen und Schutz | |
| 38 | blitz | Blitzfragen ohne Wiederholung (Pool ≥ 16 Fragen aus allen Reitern) | |
| 39 | domino | Begriff ↔ Erklärung (geschlossene Kette) | |
| 40 | quellen | Quellenverzeichnis + „Woher weißt du es?“ | |
| T | transfer | **Transfer**: Die Schule soll zwei Bienenvölker bekommen – Brief an die Schulleitung / Plakat „Das darf man am Bienenstock nicht vergessen“. A Textbausteine ordnen (Tap-Tap) + Urteil, B Satzanfänge, C frei | |

Neue Aufgabentypen: `film`, `filmmoment` (Baustein `film.js`), `erkunden`, `modellfinden` (neu, Modul `modell3d.js`, Beschreibung unten).
Tafel-Typen (nur diese bekommen eine Tafel-Fassung): lueckentext, zuordnung, mc, sortieren, richtigfalsch, freitext.

## Lesestrecken (je Abschnitt 2–4 kurze Sätze, ≤ 15 Wörter je Satz, 1 Frage, 1 Schaubild)

Bilddateien unter `arbeitsblatt/static/img/lese/`, viewBox 480 × 288, Stil: gegenständlich, plastisch (siehe Skill-Datei
`ab-bauen/references/lernpfad.md`). Die Frage lässt sich **allein aus dem Abschnitt** beantworten. Lösungsposition variieren.

**L1 – Eine Biene als Nutztier** (key `nutztier`): 
1. *Nutztiere helfen uns* – Menschen halten Tiere, weil sie etwas geben: Rind (Milch, Fleisch), Huhn (Eier), Schaf (Wolle). Bild `nutztier-1.svg` Bauernhof, am Rand Bienenkästen.
2. *Die Biene ist anders* – lebt frei, sucht ihr Futter selbst, Imker stellt den Bienenkasten auf und kümmert sich. Bild `nutztier-2.svg` Kästen auf der Wiese, Imker, fliegende Bienen.
3. *Was die Biene uns gibt* – Honig, Wachs (Kerzen), Bestäubung (Blüte → Frucht). Bild `nutztier-3.svg` Honigglas, Kerze, Apfelzweig mit Biene.
4. *Der Imker kümmert sich* – kontrolliert das Volk, erntet nur einen Teil des Honigs, schützt vor Krankheiten. Bild `nutztier-4.svg` Imker zieht ein Rähmchen.

**L2 – Eine Biene ist ein Insekt** (key `koerper`):
1. *Drei Körperteile, sechs Beine* – Kopf, Brust, Hinterleib; Insekten haben 6 Beine (Spinnen 8). Bild `biene-1.svg` Biene von der Seite, drei Abschnitte farbig.
2. *Der Kopf: Sinne und Mund* – Fühler (riechen, tasten), zwei Facettenaugen (je etwa 5000 Einzelaugen), drei kleine Punktaugen, Rüssel zum Saugen. Bild `biene-2.svg` Kopf von vorn.
3. *Die Brust: Flügel und Beine* – vier Flügel, sechs Beine, kräftige Flugmuskeln, etwa 200 Flügelschläge pro Sekunde. Bild `biene-3.svg` Brust mit Flügeln, Muskeln als Schnitt.
4. *Der Hinterleib: Honigmagen und Stachel* – Honigmagen (Nektar transportieren), Darm, Wachsdrüsen, Stachel (Drohnen haben keinen). Bild `biene-4.svg` Hinterleib aufgeschnitten.
5. *Werkzeug zum Sammeln* – Haare, Bürsten, Pollenkörbchen am Hinterbein, Pollen als „Höschen“. Bild `biene-5.svg` Hinterbein mit Pollenkörbchen.

**L3 – Wer lebt im Bienenstock?** (key `volk`, Vorwissen *vor* dem Film):
1. *Ein Volk aus vielen Bienen* – Sommer bis ca. 50 000, Winter etwa 10 000; Bienen leben nur als Volk. Bild `volk-1.svg` wimmelnde Wabe.
2. *Königin, Arbeiterin, Drohne* – Aussehen, Aufgabe, Lebensdauer (Königin 3–5 Jahre, Sommerarbeiterin 5–6 Wochen, Winterbiene bis ca. 6 Monate; Drohnen = Männchen ohne Stachel, im Herbst aus dem Stock gedrängt). Bild `volk-2.svg` drei Bienen nebeneinander.
3. *Der Bienenkasten von innen* – Boden, Brutraum, Honigraum, Rähmchen mit Waben, Dach, Flugloch. Bild `volk-3.svg` Querschnitt.
4. *Die Wabe* – sechseckige Zellen aus Wachs (sparen Platz und Wachs), Brutzellen, Pollenzellen, Honigzellen. Bild `volk-4.svg` Wabenausschnitt.

**L4 – Honig, Wachs, Blüten – und Gefahren** (key `nutzen`):
1. *Honig ist Wintervorrat* – Bienen machen aus Nektar Honig; Imker nimmt nur einen Teil. Bild `nutzen-1.svg` Honigernte/Schleuder.
2. *Wachs und mehr* – Wachs aus Drüsen am Hinterleib; Kerzen, Salben. Bild `nutzen-2.svg` Wachskerze, Wachsplättchen.
3. *Bestäubung* – Biene trägt Pollen von Blüte zu Blüte, daraus werden Früchte (Apfel, Kirsche, Raps). Biene besucht auf einem Ausflug meist eine Pflanzenart. Bild `nutzen-3.svg` Apfelblüte → Apfel.
4. *Das Imkerjahr* – Frühling Volk wächst, Sommer ernten, Spätsommer auffüttern und gegen Milben behandeln, Winter Ruhe. Bild `nutzen-4.svg` Jahreskreis.
5. *Bienen in Gefahr* – Varroa-Milbe, weniger Blumen, Gifte; Schutz: Blühwiesen, bienenfreundliche Gärten. Bild `nutzen-5.svg` Wiese vs. kahle Fläche, Milbe.

## Glossar (antippbar, `glossar.py`; Bilder für die fett markierten Begriffe)

Nutztier · Imker · **Bienenkasten** · Flugloch · **Wabe** · Rähmchen · Brutraum · Honigraum · Bienenvolk · **Königin** ·
Arbeiterin · **Drohne** · Insekt · **Facettenauge** · Fühler · Rüssel · **Honigmagen** (Alias Honigblase) · **Pollenkörbchen**
(Alias Pollenhöschen) · **Stachel** · Nektar · Pollen · **Bestäubung** · Larve · Puppe · **Schwänzeltanz** · **Wintertraube** ·
**Varroa-Milbe** · Wachs · Ammenbiene · Sammlerin · Wächterin · Honig. Jeder fette Begriff im Text hat einen Eintrag oder ist ein Datum.

## Feste Wörter (DaZ: dieselben Wörter in AB, Film und 3D-Modell)

Bienenstock = das ganze Zuhause des Volkes · Bienenkasten = die Holzkiste des Imkers · Flugloch · Wabe · Zelle · Rähmchen ·
Brutraum · Honigraum · Bienenvolk · Königin · Arbeiterinnen · Drohnen · Ammenbienen · Wächterinnen · Sammlerinnen · Rüssel ·
Nektar · Pollen · Honigmagen · Pollenkörbchen (gelbes Höschen) · Larve · Puppe · Schwänzeltanz (im Film „Tanz“/„Schwänzeln“) ·
Traube/Wintertraube · Flugmuskeln · Facettenaugen · Fühler.

## Gesicherte Fakten (nur diese Zahlen verwenden; sonst „etwa“ und nichts erfinden)

- Arbeiterin etwa 12–14 mm lang. Sommervolk 30 000–50 000 Bienen (Film: „bis zu fünfzigtausend“), Winter etwa 10 000.
- Königin legt bis etwa 2 000 Eier am Tag, lebt 3–5 Jahre. Drohnen: einige hundert, Männchen, kein Stachel, paaren sich mit jungen Königinnen, werden im Spätsommer/Herbst aus dem Stock gedrängt.
- Entwicklung Arbeiterin **21 Tage**: Ei 3 Tage, Larve 6 Tage (Zelle wird danach verdeckelt), Puppe 12 Tage. (Königin 16, Drohne 24 Tage.)
- Aufgaben der Arbeiterin nach Alter: putzen (erste Tage) → Ammenbiene (füttert Larven) → baut Waben/hält Wache → Sammlerin (ab etwa 3 Wochen). Sommerarbeiterin lebt etwa 5–6 Wochen.
- Facettenauge etwa 5 000 Einzelaugen; drei Punktaugen. Flügelschläge etwa 200 pro Sekunde. Sammelflug meist bis etwa 3 km.
- Nektar = süße Blütenflüssigkeit (→ Honig), Pollen = Blütenstaub (Eiweiß für die Larven). Honigmagen = Vorratsbehälter im Hinterleib, getrennt vom Verdauungsmagen.
- Wachs: Wachsdrüsen an der Unterseite des Hinterleibs der Arbeiterinnen. Sechseckige Zellen sparen Wachs und Platz.
- Schwänzeltanz (Karl von Frisch, Nobelpreis 1973): Winkel des Schwänzellaufs zur Senkrechten = Winkel zwischen Flugrichtung und Sonne; Dauer des Schwänzelns = Entfernung; Rundtanz bei nahem Futter.
- Stachel: Arbeiterinnen und Königin haben einen, Drohnen nicht. Stachel mit Widerhaken bleibt in der Haut von Säugetieren stecken, die Biene stirbt dann meist.
- Wintertraube: Bienen wärmen sich durch Zittern der Flugmuskeln; Königin in der Mitte; Honig als Vorrat. Der Imker ersetzt geernteten Honig durch Zuckerfutter (offen sagen).
- Varroa-Milbe: Parasit, saugt an Larven, Puppen und Bienen, schwächt das Volk. Behandlung im Spätsommer.
- Bestäubung: Pollen gelangt von Blüte zu Blüte, die Blüte kann dann Früchte/Samen bilden. Die Honigbiene gilt in Deutschland nach Rind und Schwein als drittwichtigstes Nutztier (Deutscher Imkerbund; **vor Veröffentlichung prüfen**).
- Quellen für das Quellenverzeichnis: Deutscher Imkerbund e. V. (imkerbund.de), Länderinstitut für Bienenkunde Hohen Neuendorf (honigbiene.de), NABU „Honigbiene“, Karl von Frisch „Aus dem Leben der Bienen“ (Hinweis), COLOSS BEEBOOK (Anatomie, Carreck et al. 2013) für das 3D-Modell. Keine Zitate, nur Nennung.

## Das 3D-Modell im AB (Schnittstelle)

Das Vite-Projekt (`src/main.js`) wird um einen **Einbettungsmodus** erweitert und mit `npm run build:ab` nach
`arbeitsblatt/static/film/bienenmodell/` gebaut (relative Pfade, `base: './'`). Es bleibt zugleich als eigenständige Studie
nutzbar. Im AB ist es ein Eintrag in `INHALTE.filme`:
`biene3d: { art: "modell3d", datei: "/static/film/bienenmodell/index.html?embed=1", titel: "Die Honigbiene in 3D" }`.
Gesprochen wird dasselbe `postMessage`-Protokoll wie bei den Filmen (Baustein `film.js`), erweitert um Befehle für das Modell.

**AB → Modell** (`{mw: …}`):
- `info` → Modell antwortet mit `{mw:"info", art:"modell3d", ansichten, blicke, teile}`.
- `ansicht` `{name:"gestalt"|"situs"|"explosion"}` (Fortschritt 0 / 0,55 / 1) oder `{wert: 0…1}`.
- `blick` `{name:"seite"|"oben"|"vorn"|"hinten"|"schraeg"}` Kamerafahrt zu einer Ansicht (schraeg = Standard).
- `hervorheben` `{teile:["fluegel"]}` hebt die Teile hervor, alle anderen werden blass/transparent; `{teile:[]}` hebt auf. Mit `{fokus:true}` fährt die Kamera sanft näher.
- `beschriften` `{an:true, teile:[…]}` zeigt kleine Namensschilder (deutscher Name) an den Teilen, `{an:false}` blendet aus.
- `nummern` `{teile:["kopf","brust",…]}` zeigt nummerierte Markierungen ①②③ ohne Namen (für Beschriftungsaufgaben); `{teile:[]}` entfernt.
- `fokus` `{teile:["ruessel"], blick?:"vorn", abstand?:2.5}` fährt die Kamera sanft an die **Ankerregion** der Teile (bei `punkt`-Ankern ein Würfel von 1,2 Einheiten um den Ankerpunkt, bei Mesh-Ankern deren Box; bei paarigen Teilen die zugewandte Seite), **ohne etwas zu markieren oder zu verändern** (die Lösung wird nicht verraten, Tippen bleibt möglich). Ohne `blick` nutzt ein einzelnes Teil seine Standardrichtung aus `src/teile.js` (`fokusRichtung`: `ruessel` von vorn unten, `stachel` von der Seite hinten unten, `herz` von der Seite, `gehirn` von vorn oben), sonst bleibt die Blickrichtung. `abstand` = Kameraabstand in Modelleinheiten (Standard: Bildausschnitt füllt das Teil, mindestens 1,6). `{teile:[]}` fährt zurück (mit `blick` zu dieser Ansicht); `zurueck` setzt den Fokus ebenfalls zurück. Ein späteres `hervorheben` mit `teile:[]` fährt eine mit `fokus` gesetzte Kamera nicht zurück. Der Stachel braucht dazu `ansicht` situs oder explosion (in der Explosion ist er danach vollständig, im Situs etwa zur Hälfte sichtbar: Enddarm und Platten verdecken ihn).
- `waehlen` `{an:true}` Wählmodus: Antippen/Klicken eines Teils schickt `{mw:"tipp", teil:"<key>"|null, teile:[…], rohname, darunter:[…], davor:[…]}`; kurzes Aufleuchten des angetippten Teils, **keine** Richtig/Falsch-Anzeige im Modell. `{an:false}` beendet. `teil` = speziellster Schlüssel des getroffenen Meshes, `teile` = alle seine Schlüssel. Gewählt wird der erste feste Treffer mit Schlüssel entlang des Strahls: durchsichtige Membranen (Flügel, Luftsäcke samt Tracheenstämmen) und Meshes ohne Schlüssel (Malpighi-Schläuche, Fettkörper, Drüsen) blockieren nicht. `darunter` = Schlüssel **aller anderen** Treffer entlang des Strahls (vorn nach hinten), `davor` = Meshnamen der übergangenen Treffer vor dem gewählten. Die Fachseite entscheidet damit selbst, ob ein verdecktes Zielteil gilt (z. B. `teil==="darm"`, `darunter` enthält `honigmagen`).
- `leiste` `{an:true|false}` blendet die Bedienleiste des Einbettungsmodus ein/aus (für Tipp-Aufgaben: Leiste weg, das Modell bekommt den ganzen Rahmen). Der Kamera-Fit passt sich in 0,5 s an, ohne den Blick zu verändern; das Reglersymbol „einblenden“ (44 px, unten rechts) bleibt als Ausweg sichtbar. Nur `leiste` und das Ein-/Ausblenden-Symbol ändern die Leiste, `zurueck` stellt sie **nicht** wieder her. In sehr kleinen Rahmen (Höhe ≤ 300 px) ist die Leiste einzeilig (Voreinstellungen, Zurücksetzen, Ausblenden; kein Regler, kein Abspielen; 52 px statt 102 px).
- `spielen` / `anhalten` (automatisches Öffnen/Schließen), `freischalten` und `springe` ohne Wirkung (Kompatibilität).
- `zurueck` setzt Ansicht, Hervorhebung, Beschriftungen, Fokus und Kamera zurück (der Wählmodus bleibt).

**Modell → AB:** `{mw:"status", t:0, laeuft, live:false, ansicht:"gestalt"|"situs"|"explosion"|"zwischen", ansichtLabel, gesehen:0–100, besucht:["gestalt","situs","explosion"], freigeschaltet:true, standText:"Außenansicht", leiste:true|false}` (`leiste` = Bedienleiste sichtbar)
beim Laden, bei jeder Änderung und etwa alle 500 ms. `gesehen` = Erkundungsfortschritt: je ein Drittel für die drei Ansichten, sobald der
Fortschrittsregler in ihrer Nähe (±0,06) war. `freigeschaltet:true` immer (Modell-Knöpfe sind nie gesperrt).

**Teile (`teile`-Schlüssel, deutsche Namen)**: `kopf`, `brust`, `hinterleib`, `fuehler`, `facettenauge`, `ruessel`, `fluegel` (alle vier),
`bein` (alle sechs), `vorderbein`, `mittelbein`, `hinterbein`, `pollenkoerbchen`, `honigmagen`, `darm`, `herz`, `gehirn`, `flugmuskeln`,
`stachel` (Stachel und Giftblase), `luftsaecke`. Die Zuordnung Mesh → Schlüssel entsteht aus den Meshnamen der GLB (140 Meshes in 35 Gruppen);
Innenteile sind nur ab Situs sichtbar (der Pick-Test muss das beachten: Innenteile antippen verlangt Ansicht „situs“ oder „explosion“).

**Modul `modell3d.js` im AB** (neu): Aufgabentyp `erkunden` (Fortschrittsbalken aus `gesehen`, Station erledigt bei ≥ 95 %),
Aufgabentyp `modellfinden` (Ziele nacheinander, Prüfung im Browser anhand `tipp.teil`, Rückmeldung ohne Lösung zu verraten, Hinweis nach Fehlversuch,
`sendAntwort` je Ziel, Zustand im Autosave). Dazu die Modell-Knöpfe an beliebigen Aufgaben über das Feld `modell` von `film.js`:
`modell: {film:"biene3d", text:"Im Modell ansehen", befehle:[{mw:"ansicht",name:"situs"},{mw:"hervorheben",teile:["honigmagen"]}], pflicht:true}`.

## Der Film im AB

`INHALTE.filme.volk = { art:"papiertheater", datei:"/static/film/Ein_Bienenvolk_im_Bienenstock.html", titel:"Ein Bienenvolk im Bienenstock" }`.
12 Szenen à 20 s (= `kapitel` 1–12 für `film.js`). Szenen: 1 Besuch/Titel · 2 Bienenkasten auf der Wiese (Flugloch, Wächterinnen) · 3 Waben, Brutraum, Honigraum ·
4 Drei Arten von Bienen · 5 Die Königin legt Eier · 6 Vom Ei zur Biene in 21 Tagen · 7 Aufgaben der Arbeiterinnen · 8 Sammlerinnen (Rüssel, Nektar, Honigmagen, Höschen) ·
9 Der Tanz · 10 Aus Nektar wird Honig · 11 Winter (Traube, Flugmuskeln) · 12 Schluss. Wortlaut: `papiertheater/drehbuch.md` (und später `docs/ab_uebergabe.md`).
**Aufgaben dürfen nur fragen, was der Film zeigt oder sagt**; Zeitfenster für `filmmoment` werden aus den Satzzeiten der Stimme berechnet
(`papiertheater/docs/ab_uebergabe.md`). Bis dahin: Platzhalter in einer einzigen Konstante `FILM_ZEITEN` am Dateianfang des Tab-Moduls.

## Arbeitsteilung der Dateien (damit parallel gearbeitet werden kann)

Jeder Reiter hat **eigene Inhaltsdateien**; niemand bearbeitet die Inhalte eines anderen Reiters:

- `static/js/inhalte.js`: Kopf (`window.INHALTE = {titel, filme, bildpunkte, tabs: []}`) – danach hängt je Reiter eine Datei an:
  `static/js/inhalte_nutztier.js`, `…_koerper.js`, `…_volk.js`, `…_nutzen.js`, `…_abschluss.js` mit `INHALTE.tabs.push({…})`
  (Ladereihenfolge in `templates/index.html`, Reihenfolge = Reiterfolge).
- Server: `inhalte_server.py` sammelt `LESESTRECKEN` aus `lesen_nutztier.py`, `lesen_koerper.py`, `lesen_volk.py`, `lesen_nutzen.py`
  (je ein Dict mit Abschnitten, Fragen, Lösungen, Erklärungen); `glossar.py` sammelt Einträge aus `glossar_<reiter>.py`.
- Grafiken: `werkzeuge/grafiken_<reiter>.py` je Reiter erzeugt `static/img/lese/<name>.svg` (gemeinsame Helfer in `werkzeuge/svg_helfer.py`, nicht ändern).
- Tests je Reiter: `tests/test_inhalt_<reiter>.py`.
