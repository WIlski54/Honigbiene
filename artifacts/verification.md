# Prüfstand — 3. Oktober 2026

## Ausblendbare Tablet-Bedienung

Nutzerrückmeldung: bisheriger Stand läuft sehr sauber auf dem Tablet; der
Bedienkasten verdeckt beim Hineinzoomen in die Explosion Modellteile.
Die neue Ausblendfunktion wurde lokal bei 1194 × 834, 834 × 1194 und
390 × 844 geprüft. Einklapp-Pfeil und Wiederherstellung funktionieren per
Klick und Tastatur. Beide Schalter haben 44 × 44 Pixel Trefffläche; Fokus
und `aria-expanded` folgen der Sichtbarkeit. Untere Hinweise, Zoomknöpfe und
Footer werden ebenfalls ausgeblendet. Touchlogik wurde nicht verändert.

Bei 100 % Öffnung und zweifacher Vergrößerung waren zuvor verdeckte Beine
nach dem Ausblenden sichtbar. 16.280 Bild-Samples aus dem vorher bereits
sichtbaren Modellbereich waren im Vorher-/Nachher-Vergleich unverändert
(RGB-Summendifferenz höchstens 18). Der Schalter setzt Kamera oder Öffnung
nicht zurück. 14 vorhandene Tests und Produktionsbuild bestanden.
Neue Prüfbilder: `controls-before-hide.jpg`, `controls-hidden-landscape.jpg`,
`controls-hidden-portrait.jpg` und `controls-hidden-mobile.jpg`.
Die Bedienänderung muss vom Nutzer noch auf dem tatsächlichen Tablet geprüft
werden. Ein Vite-WebSocket-Verbindungsfehler wurde im Konsolenverlauf gesehen;
manuelles Neuladen und die Modell-/UI-Darstellung funktionieren.

## Aktueller Stand v03

Dieser Abschnitt ist der aktuelle Prüfstand; die folgenden älteren Abschnitte
bleiben als Verlauf erhalten. Außenform, Beinprofile, Pollenkörbchen/Bürsten,
gerichtete Haare und getrennte Flügelkonturen/Adernetze sind weitergeführt.
Innen sind Muskelfasern, Luftsäcke und Drüsen verfeinert; Fettkörper und
Speicheldrüsen sind ergänzt. Grundlage bleibt das COLOSS BEEBOOK, Tafeln
8–13; keine fachliche Validierung oder gemessene Organtiefe.

- `npm test`: **14 Tests bestanden**. Ein neuer Geometrietest dekodiert beide
  komprimierten GLBs und prüft pro Bein einen zusammenhängenden Basitarsus
  sowie genau vier weitere, getrennte Fußglieder. Hinterbeinbürsten erhalten.
- `npm run build`: erfolgreich. Weiterhin nur die Größenwarnung des etwa
  596-kB-Three.js-Chunks, kein Buildfehler.
- Beide Exporte: 35 bewegliche Gruppen, sieben Organsysteme, gleiche Pfade.
  Organe einschließlich Fettkörper bleiben bis zum Situs in Ausgangslage.
- Desktop: 1.138.172 Modelldreiecke, 12.116.668 Byte.
  Mobile: 623.650 Modelldreiecke, 5.964.280 Byte. Beide unter den Dateigrenzen.
- Vorschau: Gestalt, Situs und Explosion dargestellt. Mausrad öffnet und
  schließt; Umkehr und Rückkehr auf 0 % geprüft. Mausrotation und Zoom
  funktionieren. Automatik gestartet und über den Regler per Home unterbrochen.
- Desktop 1280 × 720, Tablet 834 × 1194 und 1194 × 834 sowie mobile
  Modellfassung bei 390 × 844: visuell ohne leere Szene, abgeschnittenes Modell
  in der Standardansicht oder horizontalen Seitenüberlauf geprüft.
- Bildpixelprüfung in den mittleren Szenenbereichen aller acht neuen Prüfbilder:
  zwischen 1.207 und 6.099 dunkle Modell-Samples, alle nicht leer.
  Siehe `pixel-checks-v03.json`. Dies ist eine Prüfung der gerenderten Bilder,
  keine direkte GPU-Zeitmessung.
- Browserkonsole: keine Warnungen oder Fehler beim abschließenden Laden.
  Während der Bedienprüfung ca. 60 fps, 16,7 ms Callback-Abstand und
  1,0–1,1 ms CPU-Renderübergabe. Mobile Explosion: 145 Draw Calls,
  633.002 gerenderte Dreiecke (Export- und Renderzählung unterscheiden sich).
- Die früheren Chat-/Browserabbrüche sind damit nicht als behoben nachgewiesen.
  Safari, echte Zweifingerbedienung, thermische Last und Leistung auf dem
  tatsächlichen iPad bleiben offen. Beschriftungen sind noch nicht umgesetzt.

Aktuelle Bilder: `current-v03.jpg`, `situs-v03.jpg`, `explosion-v03.jpg`,
`tablet-portrait-v03.jpg`, `tablet-landscape-v03.jpg`, `mobile-closed-v03.jpg`
und `mobile-explosion-v03.jpg`. `exterior-v03.jpg` dokumentiert den zuvor
abgeschlossenen Außenmodell-Durchgang. Alte PNGs zeigen frühere Fassungen.
Die lokale Vorschau läuft unter http://127.0.0.1:5173/.

## Frühere Prüfungen

Diese Prüfung betrifft die erste lokal ausführbare Modellstudie. Die vom
Nutzer gewünschte pixelgenaue Replik und anatomische Validierung sind noch
nicht erreicht. Zielgerät ist ein iPad; Modell und iPadOS-Version sind offen.

## Automatische Prüfungen

- `npm test`: 13 Tests bestanden. Analytische Bewegung bei 30/60/120 Hz,
  verzögerte Frames, Richtungswechsel mit erhaltener Geschwindigkeit,
  Rückkehr ohne Drift und unveränderte Organpositionen im Situs.
- Gestenlogik: parallele Fingerbewegung, Pinch, Schwellenwert und Sperre
  einer einmal gewählten Geste geprüft. Dies ersetzt keinen Hardwaretest.
- Beide GLB-Dateien: gültiger Container, Meshopt-Kompression, endliche
  Geometriegrenzen, gleiche 34 bewegliche Gruppen und Bewegungspfade.
- Aktuelle Kopfkorrektur: Desktop 1.004.900 Dreiecke insgesamt, GLB 10,92 MB;
  Mobile 503.994 Dreiecke insgesamt, GLB 4,92 MB. Organformen bleiben gleich.
- `npm run build`: erfolgreich. Vite weist auf den etwa 596-kB-Three.js-Chunk
  hin (gzip etwa 151 kB); dies ist eine Größenwarnung.
- `npm install --package-lock-only`: Audit meldet keine Schwachstellen.

## Bedienung im eingebetteten Browser

- Modell geladen; Ausgangsform, Situs bei 55 % und Explosion bei 100 % sichtbar.
- Mausrad vorwärts und rückwärts verändert den Fortschritt.
- Slider per Tastatur bis 0 % zurückgeführt, Ausgangsform wiederhergestellt.
- Mausziehen dreht das Modell; Zurücksetzen stellt die Referenzkamera her.
- Abspielen/Anhalten und direkte Unterbrechung durch Bedienung funktionieren.
- Die drei Originalbilder sind über die Bildvorlage auswählbar.
- Schmale Darstellung bei 390 × 844 ohne horizontalen Seitenüberlauf geprüft.
  Tablet-Hochformat 834 × 1194 und Querformat 1194 × 834 visuell geprüft,
  jeweils ohne horizontalen Seitenüberlauf. Ein überdeckter Bedienhinweis
  im Hochformat wurde mit mehr Abstand zum Regler korrigiert.
- Ein vorübergehender Ladefehler während der Erstellung der mobilen GLB
  wurde nach Export und Neuladen behoben; kein aktueller Ladefehler sichtbar.

## Leistung und offene Abnahme

Die Vorschau zeigte zu Beginn ungefähr 60 fps, bei späteren Prüfungen
überwiegend 1 fps und bei der abschließenden Prüfung wieder 60 fps.
Gemessen wurden im langsamen Zustand rund 1.000 ms zwischen
Animation-Callbacks, bei etwa 0,9–1,2 ms CPU-Zeit für die Renderübergabe.
Das misst weder die GPU-Ausführungszeit noch beweist es die Ursache des
langsamen Callback-Takts. Die finale Geschmeidigkeit ist damit **nicht
abgenommen**. Die Zeitintegration wurde korrigiert, damit verzögerte Frames
die automatische Fahrt nicht künstlich verlangsamen.
Die letzte Situs-Aufnahme zeigte 16,5 ms zwischen Frames und rund 0,8 ms
CPU-Zeit für die Renderübergabe. Die Ursache des zeitweise langsamen
Vorschautakts ist damit weiterhin nicht eindeutig bestimmt.

Auf dem echten iPad sind Safari-Bildrate, thermische Last, Einfingerrotation,
Zweifingeröffnung, Pinch, Richtungswechsel und die Auswahl der mobilen
Modellfassung noch zu prüfen. Die PC-Vorschau läuft nur auf 127.0.0.1;
`npm run dev:tablet` ermöglicht bei Bedarf den Test im gemeinsamen WLAN.

## Bildtreue und Anatomie

Haare, Facettenaugen, vier geäderte Flügel, sechs gegliederte Beine,
Körperplatten und sechs Organsysteme sind echte 3D-Geometrie.
Die neuen Schnittbilder haben Honigblase, Mitteldarmfalten, Flugmuskeln,
Herzschlauch und Drüsenregionen beeinflusst. Organfarben sind didaktisch.

Silhouette, Oberflächen, Beinhaltung und Flügeladern weichen noch von der
Makrovorlage ab. Die räumliche Tiefe der Organe ist rekonstruiert und nicht
aus Mikro-CT-Daten segmentiert. Für die nächste Stufe sind zusätzliche
Außenansichten und eine fachliche Prüfung der Organlage erforderlich.

Screenshots: `closed.png`, `situs.png`, `mobile-explosion.png` und die
abschließend gespeicherten Tablet-Ansichten dokumentieren den Prototyp.

## Nachtrag: Kopfkorrektur und Browserverbindung

Die zusätzlichen Referenzen sind unverändert unter
`model/references/2026-10-03/` gesichert. Kopfkontur, Facettenaugen,
Gesichtsbehaarung, Mandibeln und gefaltete Mundwerkzeuge sind in beiden
Modellfassungen überarbeitet. Die neuen Organillustrationen sind bisher
Referenzmaterial; sie haben in diesem Durchgang keine Änderung an den
inneren Organformen ausgelöst. 13 Tests und Produktionsbuild bestanden
nach dem erneuten Export.

Die Browsersteuerung verlor wiederholt ihren zuvor verwendeten Tab.
Ein erneutes Verbinden funktionierte zeitweise; später meldete sie keine
verfügbaren Tabs. Die vom Nutzer sichtbare zusätzliche Bad-Request-Meldung
ist dadurch nicht vollständig erklärt. Der lokale Server antwortete mit
HTTP 200. Eine neu geöffnete Vorschau lud das aktualisierte Modell und
zeigte in der abschließenden Aufnahme 60 fps. Das belegt die erfolgreiche
Darstellung zu diesem Zeitpunkt, keine dauerhafte Behebung der
Browseranbindung und keine Leistungsabnahme auf dem iPad.

`current-refined-model.png` zeigt den abschließenden Stand;
`refined-head-view.png` eine vergrößerte Ansicht davor. Alte Screenshots
und der erste Abschnitt dokumentieren teilweise den vorherigen Stand.
Eine aktuelle Sichtprüfung der mobilen Datei auf echter Touchhardware
steht weiterhin aus.
