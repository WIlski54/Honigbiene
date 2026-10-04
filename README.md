# Honigbiene — Anatomie in Bewegung

**Veröffentlichung:** Die 3D-Biene ist für GitHub Pages vorbereitet. Repository:
[WIlski54/Honigbiene](https://github.com/WIlski54/Honigbiene), Modellseite:
[wilski54.github.io/Honigbiene](https://wilski54.github.io/Honigbiene/).
Einrichtung, lokale Vorschau und spätere Pushes: [VEROEFFENTLICHUNG.md](VEROEFFENTLICHUNG.md).
Das Flask-Arbeitsblatt wird nicht über GitHub Pages ausgeliefert.

## Das Projekt im Überblick (Stand 4. Oktober 2026)

Aus der 3D-Studie ist ein komplettes Unterrichtsprojekt für **NW, Jahrgang 6 (Nutztiere)** geworden:

| Teil | Ordner | Was es ist |
|---|---|---|
| 3D-Modell mit Explosionsansicht | dieser Ordner (`src/`, `model/`, `public/`) | die Studie unten; zusätzlich einbettbar (`?embed=1`) und per `postMessage` steuerbar |
| Papiertheater-Film „Ein Bienenvolk im Bienenstock“ (4:00) | `papiertheater/` | HTML-Player, MP4, Drehbuch, Übergabe für das AB |
| Interaktives Arbeitsblatt (Flask) | `arbeitsblatt/` | forschend-entwickelndes AB mit Modell, Film, Tafel und Lehrer-Dashboard |

Einstieg: `AB_KONZEPT.md` (Konzept, Struktur, Fakten) · `arbeitsblatt/README.md` (Start, Tests, Betrieb) ·
`arbeitsblatt/docs/FORSCHEN.md` (didaktischer Ansatz) · `FORTSETZUNG.md` (Stand und nächste Schritte).
Das 3D-Modell wird mit `npm run build:ab` in `arbeitsblatt/static/film/bienenmodell/` gebaut.

## Die 3D-Studie

Lokal laufende erste 3D-Modellstudie einer Arbeiterin von *Apis mellifera*.
Die Vorlage liegt unverändert in `public/reference/bee.png`.
Die beiden zusätzlich vom Nutzer bereitgestellten Schnittbilder sind in
`public/reference/anatomy-model.png` und `anatomy-section.png` gesichert
und über die Bildvorlage auswählbar. Ihre Herkunft ist noch nicht dokumentiert.

## Starten

```powershell
npm install
npm run dev
```

Die Anwendung öffnet unter http://127.0.0.1:5173/.
`npm run build` erzeugt eine statisch hostbare Fassung in `dist/`.
Alle Schriften, Modell- und Referenzdateien werden lokal ausgeliefert;
die Anwendung benötigt zur Laufzeit keine KI-API und keinen Serverdienst.

### Auf dem iPad prüfen

PC und iPad müssen im selben WLAN sein. Den normalen Entwicklungsserver
beenden und `npm run dev:tablet` starten. Vite zeigt dann unter **Network**
die Adresse des PCs an, die in Safari auf dem iPad geöffnet wird.
`127.0.0.1` bezeichnet immer das jeweilige Gerät und funktioniert auf dem
iPad deshalb nicht als Adresse dieses PCs. Der Tablet-Start macht die
Vorschau im lokalen Netzwerk erreichbar; `npm run dev` bindet dagegen nur
die lokale PC-Adresse.

## Bedienung

- **Mausrad:** kontinuierlich öffnen / zusammensetzen.
- **Ziehen:** drehen. **+ / −:** vergrößern / verkleinern.
- **Rechte Maustaste + Ziehen** oder **Strg + Ziehen:** Ausschnitt verschieben.
- **Touch:** ein Finger dreht; zwei parallel bewegte Finger öffnen/schließen;
  Pinch vergrößert/verkleinert. Gesten werden bis zum Loslassen getrennt gehalten.
  Pinch zoomt um den Mittelpunkt zwischen den Fingern.
- **Gestalt / Situs / Explosion:** reproduzierbare Ansichten.
- **Schieberegler:** beliebige Zwischenzustände, auch per Tastatur.
- **Abspielen:** langsame automatische Fahrt zum anderen Endzustand;
  direkte Bedienung hält die Fahrt an.
- **Bildvorlage:** unveränderte Originalreferenz anzeigen.
- **Pfeil rechts oben im Bedienkasten:** untere Bedienelemente ausblenden.
  Das kleine Reglersymbol unten rechts blendet sie wieder ein. Zoom, Drehung
  und Öffnung bleiben erhalten; Touchgesten funktionieren auch ohne Kasten.

## Einbettung ins Arbeitsblatt

`npm run build:ab` baut die Studie mit relativen Pfaden (`base: './'`) nach
`arbeitsblatt/static/film/bienenmodell/` (`vite build --outDir … --emptyOutDir`;
geleert wird nur dieser Zielordner). Beide GLB-Dateien werden mitkopiert. Aufruf im
Arbeitsblatt: `/static/film/bienenmodell/index.html?embed=1`. `npm run dev` und
`npm run build` arbeiten unverändert (`dist/`).

**Einbettungsmodus `?embed=1`:** ohne Kopfzeile, Phasenbeschriftung, Hinweisbox, Footer,
„Über diese Studie“, Bildvorlage und Studienmarke. Unten eine kompakte Leiste
(Außen · Innen · Explosion, Regler, Abspielen, Ansicht zurücksetzen; alle Touchziele
mindestens 44 px, ausblendbar über den Pfeil, Wiedereinblenden über das Reglersymbol).
Ab 480 px Breite steht sie einzeilig (Höhe 58 px), darunter zweizeilig (102 px). In sehr
kleinen Rahmen (Höhe bis 300 px) ist sie einzeilig und ohne Regler und Abspielen (52 px:
Voreinstellungen, Zurücksetzen, Ausblenden). Das Arbeitsblatt kann sie mit dem Befehl
`leiste` aus- und wieder einblenden (siehe unten). Der Kamerabildausschnitt rechnet die
Leistenhöhe mit ein und gleitet beim Aus-/Einblenden in 0,5 s zum neuen Ausschnitt,
Drehung und Zoom bleiben erhalten. Ohne `?embed=1` bleibt die
Standardoberfläche unverändert; dort kommt nur der Schalter **Namen** (Namensschilder
für die Standardteile) hinzu.

**Protokoll** (`window.postMessage`, Feld `mw`; Nachrichten nur vom Elternfenster, Antworten
an `window.parent`; ohne Elternfenster passiert nichts). Quelle: `src/protokoll.js`,
Konzept: `AB_KONZEPT.md`.

| Befehl an das Modell | Wirkung |
|---|---|
| `{mw:'info'}` | Antwort `{mw:'info', art:'modell3d', ansichten, blicke, teile}`, je Liste `{name,label}` |
| `{mw:'ansicht', name:'gestalt'\|'situs'\|'explosion'}` oder `{wert:0…1}` | Fortschritt 0 / 0,55 / 1 bzw. frei |
| `{mw:'blick', name:'schraeg'\|'seite'\|'oben'\|'vorn'\|'hinten'}` | sanfte Kamerafahrt |
| `{mw:'hervorheben', teile:[…], fokus:true}` | gewählte Teile kräftig mit pulsierender Emission, alle anderen blass (Ghost-Material-Klone); `teile:[]` hebt exakt auf; `fokus` fährt näher (bei paarigen Teilen auf die zugewandte Seite) |
| `{mw:'beschriften', an:true, teile:[…]}` / `{an:false}` | Namensschilder (HTML-Overlay, ≥ 15 px, überlappungsfrei); ohne Liste die Standardteile |
| `{mw:'nummern', teile:[…]}` | Nummernkreise (30 px); Position in der Liste = Nummer |
| `{mw:'fokus', teile:[…], blick?, abstand?}` | Kamerafahrt an die Ankerregion der Teile, **ohne Markierung** (die Lösung bleibt geheim, Tippen bleibt möglich); `teile:[]` fährt zurück; ohne `blick` hat ein einzelnes Teil ggf. eine Standardrichtung (`fokusRichtung` in `src/teile.js`) |
| `{mw:'waehlen', an:true}` | Antippen (ohne Ziehen) meldet `{mw:'tipp', teil, teile, rohname, darunter, davor}`; der speziellste Schlüssel gilt, `teile` enthält alle passenden, `darunter` die Schlüssel aller anderen Treffer entlang des Strahls, `davor` die übergangenen Meshes |
| `{mw:'leiste', an:true\|false}` | blendet die Bedienleiste des Einbettungsmodus ein/aus (Status-Feld `leiste`); das Reglersymbol unten rechts bleibt als Ausweg sichtbar; nur dieser Befehl und der Pfeil/das Symbol ändern die Leiste, `zurueck` nicht |
| `spielen` · `anhalten` · `zurueck` | Automatik; `zurueck` setzt Ansicht, Hervorhebung, Schilder, Nummern, Fokus und Kamera zurück (der Wählmodus bleibt) |
| `freischalten` · `springe` | ohne Wirkung (Kompatibilität) |

Statusmeldung `{mw:'status', art:'modell3d', laeuft, live:false, ansicht, ansichtLabel, fortschritt,
gesehen, besucht, freigeschaltet:true, standText, …}` nach dem Laden (davor eingehende Befehle
werden eingereiht), bei jeder Änderung und alle 500 ms. `gesehen` = je ein Drittel für
Außen, Situs und Explosion, sobald der Regler in ihrer Nähe (±0,06) war; Außen zählt
bereits beim Laden (33 %), ein schneller Sprung über die Situs-Zone zählt mit.

**Teile-Schlüssel** (explizite Tabelle `src/teile.js`, Mesh- und Gruppennamen aus
`model/build_bee.py`, in beiden GLBs identisch und per `tests/teile.test.mjs` geprüft):

| Schlüssel | Meshes bzw. Gruppen der GLB |
|---|---|
| `kopf` | Gruppen `head_dorsal_capsule`, `head_ventral_capsule` (mit Augen, Mundwerkzeugen, Punktaugen) |
| `brust` | `thorax_dorsal_cuticle`, `thorax_ventral_cuticle` |
| `hinterleib` | `abdomen_tergite_1…6`, `abdomen_sternite_1…6` |
| `fuehler` | `antenna_-1`, `antenna_1` |
| `facettenauge` | `compound_eye_±1`, `compound_eye_base_±1`, `eye_setae_±1` |
| `ruessel` | `folded_glossa_and_terminal_labellum`, `paired_galeae_folded`, `paired_labial_palps_folded` (ohne Mandibeln) |
| `fluegel` | alle vier: `forewing_±1`, `hindwing_±1` |
| `bein` / `vorderbein` / `mittelbein` / `hinterbein` | Gruppen `leg_1…3_±1` (alle sechs / je ein Paar) |
| `pollenkoerbchen` | Hinterschiene (Tibia) der Hinterbeine; **abgeleitet**: liegt nur zusammen mit Coxa, Trochanter und Femur in `leg_3_±1_coxa_trochanter_femur_tibia` und wird beim Laden als Teilmesh `leg_3_±1_tibia_corbicula` herausgelöst (seitlichstes der vier Rohrsegmente). Die GLB bleibt unverändert; Randborsten (`leg_3_±1_setae`) zählen nicht dazu |
| `honigmagen` | `crop_honey_stomach` |
| `darm` | `oesophagus`, `proventriculus_four_lip_regions`, `ventriculus_corrugated_midgut`, `ileum_rectum`, `six_rectal_pads` (ohne Honigmagen und Malpighi-Schläuche) |
| `herz` | Gruppe `system_dorsal_vessel` (Rückengefäß) |
| `gehirn` | Gruppe `system_nervous` (ein Mesh mit Gehirn, Sehlappen und Bauchmark) |
| `flugmuskeln` | Gruppe `system_flight_muscles` |
| `stachel` | `sting_plates_paired_lancets` plus abgeleitet `venom_sac_and_ducts` (Giftblase, herausgelöst aus `hypopharyngeal_mandibular_venom_glands`) |
| `luftsaecke` | Gruppe `system_tracheal`: Luftsack-Membranen und die darin liegenden Tracheenstämme |

Innenteile (`honigmagen`, `darm`, `herz`, `gehirn`, `flugmuskeln`, `stachel`, `luftsaecke`) sind erst ab
etwa 8,5 % Öffnung sichtbar und antippbar (Situs oder Explosion); ihre Schilder erscheinen
ebenfalls erst dann. Eine hervorgehobene Innenstruktur bleibt auch in der Außenansicht sichtbar
(Durchblick durch die blasse Hülle). Durchsichtige Flügelmembranen und Luftsack-Membranen
blockieren das Antippen dahinterliegender Teile nicht; liegt dahinter nichts, gilt die
Membran selbst. Haarmeshes sind nicht wählbar. Ebenso blockieren die dünnen Tracheenstämme
(zu `luftsaecke`) und Meshes ohne Schlüssel (Malpighi-Schläuche, Fettkörper, Drüsen) keine
benannten Teile dahinter; sie erscheinen nur in `darunter` bzw. `davor`. Verfehlt der Strahl das
Modell, werden Nachbarpunkte im Umkreis von 9 und 18 px geprüft (Fingerspitze).

**Treffbarkeit kleiner Innenteile** (Messung: Raster von 3 bis 8 px über die Bildbox des Teils,
Frame 520 × 330, Ansicht Situs bzw. Explosion; „gemeldet“ = Anteil der Rasterpunkte, an denen ein
Strahl das Teil trifft und der Tipp es meldet). Im Situs ohne Fokus: Honigmagen 81 → 95 %, Darm
50 → 76 %, Gehirn 60 → 78 %, Flugmuskeln 89 → 96 %; Luftsäcke 32 → 21 % (der Rest steht in
`darunter`). Mit `fokus` sind die Tippflächen deutlich größer (Honigmagen etwa 10.600 px² statt
180 px², Rüssel etwa 2.350 px² statt 18 px², Stachel in der Explosion etwa 8.600 px² und
vollständig tippbar, im Situs etwa 3.700 px² bei rund 43 % Sichtbarkeit). Einzelheiten und
Zahlen für 760 × 470 stehen in `FORTSETZUNG.md`.

Das Modell bleibt ein Prototyp. Wie in der Studie selbst gilt: keine Genauigkeit der Zuordnung
über die Meshnamen hinaus behaupten.

## Modell und reproduzierbarer Aufbau

`model/bee-study.blend` ist die bearbeitbare Blender-Datei.
`model/build_bee.py` erzeugt das Modell deterministisch mit Blender 5.1.
Das Rohmodell wird als `model/bee-study.raw.glb` exportiert.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python 'model/build_bee.py'
npm run model:optimize
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python 'model/build_bee.py' -- --mobile
npm run model:optimize -- --mobile
```

Meshopt komprimiert das Rohmodell zur Browserfassung
`public/models/bee-study.glb`. Die aktuellen Rohgeometriezahlen stehen in
`public/models/model-info.json`.
Eine zweite Fassung mit weniger Haar- und Augen-Geometrie wird beim Start
auf Touchgeräten oder schmalen Displays geladen. Anatomische Gruppen,
Organformen und Animation bleiben identisch. Die hochauflösende
Blender-Datei wird beim Erzeugen der mobilen Fassung nicht überschrieben.
Auf Touchgeräten ist außerdem die Renderauflösung auf das 1,25-Fache der
CSS-Auflösung begrenzt, um die GPU des iPads zu entlasten.

35 unabhängig bewegliche Gruppen enthalten Kopf-/Brusthülle, sechs dorsale
und sechs ventrale Hinterleibsplatten, sechs Beine, zwei Fühler, vier Flügel
und sieben rekonstruierte Organsysteme einschließlich Fettkörper. Meshes sind benannt; die GLB-Extras
enthalten Bewegungspfade, Kategorien und einen Anatomie-Status. Spätere
Beschriftungen können an diese IDs und räumliche Anker anschließen.

Die Organsysteme bleiben bis zum Situs-Zustand bei 55 % in Ausgangslage.
Ihre Trennung beginnt erst ab 62 %. Translationen werden stets aus den
gespeicherten Ausgangspositionen berechnet; Richtungswechsel akkumulieren
keine Verschiebungsfehler. Ein analytisch integrierter, kritisch gedämpfter
Fortschrittswert erhält beim Umkehren die aktuelle Geschwindigkeit.
Die Kamera erweitert den Bildausschnitt kontinuierlich passend zur Öffnung;
manuelle Drehung und Zoom bleiben dabei relativ erhalten.

## Qualitätsstand und Grenzen

Diese Version ist ein **technischer und gestalterischer Prototyp**, keine
pixelgenaue Replik und kein fachlich validierter anatomischer Atlas.
Außenflächen und Organe sind prozedural aufgebaut. Flügeladern, Feinstruktur,
Muskelbündel und Tracheen sind modellierte Annäherungen. Organfarben dienen
der Betrachtung und sind keine kalibrierten Präparatfarben. Der Situs zeigt
die im Modell festgelegten Positionen; deren räumliche Genauigkeit muss
noch anhand zusätzlicher Referenzen geprüft werden.

Anatomische Grundlage:
[Carreck et al. (2013), Standard methods for Apis mellifera anatomy and dissection,
COLOSS BEEBOOK](https://www.apiservices.biz/documents/articles-en/standard_methods_for_apis_mellifera_anatomy_and_dissection.pdf),
insbesondere Tafeln 8–12 und die Beschreibungen zur Präparation.
Die zusätzlich bereitgestellten Schnittbilder dienen zur Verfeinerung von
Honigblase, gefaltetem Mitteldarm, Herzschlauch, Muskeln und Drüsenregionen.
Die inneren Organfarben orientieren sich zur Unterscheidung an diesen
Lehrdarstellungen, nicht an natürlichen Präparatfarben.
Die Organformen wurden nicht aus CT-Volumendaten segmentiert.

Zusätzliche Fotos und Organillustrationen vom 3. Oktober sind unverändert
in `model/references/2026-10-03/` gesichert und dort bewertet. Die Fotos
haben eine erste Kopfkorrektur ermöglicht: verjüngte Gesichtskontur,
längliche Augen mit feineren Facetten und Augenhaaren, gerichtete kurze
Gesichtsbehaarung, abgeflachte Mandibeln und gefaltete Mundwerkzeuge.
Desktop- und Mobile-GLB enthalten diese Änderungen. Die zusätzlich
gelieferten Organillustrationen wurden mit dem BEEBOOK abgeglichen. Ein
weiterer Durchgang verfeinert Muskelfasern, Luftsäcke und Drüsen; ihre
Geometrien sind weiterhin Rekonstruktionen. Die KI-generierte Übersicht ist
widersprüchlich beschriftet.

Der aktuelle Außenmodell-Durchgang ergänzt asymmetrische Beinhaltungen,
abgeflachte Hintertibien mit Pollenkörbchen und Randborsten sowie Bürsten am
Basitarsus. Jeder Fuß besitzt jetzt einen Basitarsus und vier weitere Glieder.
Vorder- und Hinterflügel haben eigene Konturen und unregelmäßige Aderzellen.
Körperhaare sind feiner und gerichtet; die Hautstruktur ist zurückgenommen.
Innen wurden Speicheldrüsen und dünne Fettkörperfelder ergänzt. Lagebeziehungen
orientieren sich an den BEEBOOK-Tafeln 8–13, ihre räumlichen Maße bleiben
illustrativ. Aktuelle GLBs: Desktop 12,12 MB, Mobile 5,96 MB.

Für die nächste Stufe der Bildtreue sind zusätzliche Ansichten desselben
Exemplars besonders wertvoll: frontal, seitlich, dorsal und ventral sowie
Nahaufnahmen von Kopf, Mundwerkzeugen, Hinterbeinen und Flügeladern.
Für präzise räumliche Organgeometrie wären passende Mikro-CT-Daten oder
ein wissenschaftlich geprüftes, segmentiertes 3D-Modell die stärkste Basis.
Die erforderlichen Nutzungsrechte müssen zu den konkreten Daten passen.

## Prüfung

```powershell
npm test
npm run build
```

Tests prüfen zeitunabhängige Bewegung, Umkehr ohne Sprung, Rückkehr ohne
Drift, in-situ-Verhalten der Organe, Gestenunterscheidung und den
komprimierten Modellexport. Die Sichtprüfung und praktische Grenzen
werden in `artifacts/verification.md` dokumentiert.

Die Darstellung benötigt WebGL 2. Die Leistung muss auf dem tatsächlich
verwendeten iPad zusätzlich geprüft werden; eine responsive
Browserprüfung ersetzt keinen Test auf dessen GPU und Touchhardware.
Die genaue iPad-Modellbezeichnung und iPadOS-Version sind dafür noch offen.
