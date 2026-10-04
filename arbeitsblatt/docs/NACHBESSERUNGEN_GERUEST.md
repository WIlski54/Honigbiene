# Sammelliste: Nachbesserungen an gemeinsamen Dateien (aus den Berichten der Inhalts-Agenten)

Stand 3.10.2026, vom Leiter gesammelt. **Alle 18 Punkte am 4.10.2026 erledigt (Technik-Agent), jeweils mit „→ ✅“ vermerkt.** Wird in **einem** Durchgang von einer Person erledigt, nachdem der Forschen-Baustein fertig ist (damit keine Konflikte in `aufgaben.js` entstehen).
Jeder Punkt: Datei · Befund · gewünschte Lösung · Prüfung.

1. **`forschen.js` Forscherbuch** – `pruefen` wird nur im selben Reiter einer Vermutung zugeordnet; `v_anzahl` (Reiter `nutztier`) wird in `volk` geprüft, im Forscherbuch steht unter „Nutztier Biene“ dauerhaft „noch nicht herausgefunden“. → `pruefen` über alle Reiter suchen und die Erkenntnis beim Eintrag der Vermutung zeigen (der Eintrag erscheint nur einmal).
   → ✅ erledigt (4.10.2026): `buchEingabe()` paart über alle Reiter (id), Erkenntnis beim Eintrag der Vermutung, nicht doppelt; Test `Forscherbuch: … über ALLE Reiter gepaart`; im Browser mit echten Inhalten geprüft.
2. **`aufgaben.js` Lücken-Rückmeldung** (`checkLuecke`) – „Ein Blick in die Lesestrecke hilft“ passt nicht zu Sprachwerkstatt und nicht zu Stationen vor der Lesestrecke. → Hinweistext je Aufgabe (`cfg.hilfe`), Standard neutral („Schau noch einmal genau hin.“).
   → ✅ `cfg.hilfe`; ohne eigenen Text nur dann der Verweis auf die Lesestrecke, wenn sie schon gelesen wurde, sonst „Sieh noch einmal genau hin.“ (`aufgaben.js`, Funktion `hilfe`).
3. **`aufgaben.js` mc** (`mcAuswerten`) – (a) Niveau-Feld `erklaerung` wird nie angezeigt (Schätz-/Vermutungsfragen); (b) Falsch-Rückmeldung enthält „Lies die Lesestrecke noch einmal“ (passt nicht immer) und markiert die richtige Antwort. → Hinweistext je Aufgabe überschreibbar (`cfg.hilfe`), `erklaerung` anzeigen, wenn gesetzt; ob die richtige Antwort markiert wird, steuert ein Aufgabenfeld `zeigeLoesung` (Standard `true` wie bisher, in Forscher-Aufgaben `false` setzbar).
   → ✅ `cfg.erklaerung` wird angezeigt, `cfg.hilfe` überschreibt den Hinweis, Aufgabenfeld `zeigeLoesung: false` markiert die richtige Antwort nicht.
4. **`aufgaben.js` Zuordnung** – Hinweistext „links Begriff, rechts Erklärung“ passt nicht zu Wortbildung. → überschreibbar über `cfg.hinweis`.
   → ✅ `cfg.hinweis` ersetzt den Anleitungssatz der Zuordnung.
5. **`quellen`** (`aufgaben.js`/`spiele.js`) – `quellenAB: {titel, eintraege}` anzeigen als aufklappbares `<details>` „Quellen dieses Arbeitsblatts“.
   → ✅ `quellenAB` als `<details>` „📚 Quellen dieses Arbeitsblatts“ (Aufgabe 40 im Browser geprüft, 5 Einträge); Strukturtest.
6. **`bildpunkte.js` / CSS** – Punkte haben im SVG festen Radius 24; auf dem Bildschirm 54/36/20 px (1100/768/375 px Breite) → unter 44 px. Gilt auch für `stock-karte`. → größerer unsichtbarer Trefferkreis (min. 44 px Durchmesser auf dem Bildschirm), Punkte bleiben unterscheidbar; sehr dicht liegende Punkte (Abstand < 44 px) nicht überlappen lassen (z. B. Karte auf kleinen Breiten mit innerem Zoom/„Bild vergrößern“ statt Verkleinerung).
   → ✅ `bildpunkte.js`: unsichtbarer Trefferkreis ≥ 44 px + sichtbarer Punkt ≈ 32 px, nächster Punkt gewinnt (Tipp über Bildkoordinaten); Browser: imker-karte (3) und stock-karte (21) bei 375 px und 768 px gemessen (Trefferkreis 44 px, Punkt 32/36 px, keine Überdeckung).
7. **Normalisierung bei Lücken/Eingaben** – `normalize` ersetzt nur ß; Umlaute (ä/ö/ü ↔ ae/oe/ue) angleichen, damit „Bestaeubung“ und „Bestäubung“ gleichwertig sind (bei `luecke`, `bildpunkte`-Namen, `protokoll text` falls dort verglichen wird).
   → ✅ `normalize` gleicht ä/ö/ü = ae/oe/ue an (Test `tests/kern.test.cjs`).
8. **`film.js`** – Sperrtext „Sieh dir zuerst die Stelle im Film an …“ erscheint auch bei Modell-Aufgaben; bei `art: "modell3d"` → „Sieh dir zuerst die Stelle im Modell an …“.
   → ✅ Sperrtext und Knopfbeschriftung nach Art (Modell/Film); das 3D-Modell sperrt nie (verhinderte, dass ein Modell-Knopf in einem Reiter mit anderem Film dauerhaft gesperrt blieb).
9. **`zeichnen.js`** – `elemente` der Zeichenaufgabe werden nicht angezeigt (nur an die KI). → in Niveau A als Checkliste „Das gehört in deine Zeichnung“ anzeigen (antippbar abhaken, optional).
   → ✅ Niveau A: Checkliste „Das gehört in deine Zeichnung“ (antippbar, Zustand im Autosave „zeichenliste“); Aufgabe 15 im Browser geprüft.
10. **`modell3d.js`** – Ziel-Feld `fokus: {teile:[…], blick?}` bei `modellfinden`-Zielen (Befehl `fokus` wird vor dem Wählen gesendet); Text „Tippe unten auf ‚Los‘“ stimmt nicht, wenn der Knopf oben steht; Erkunden-Balken zeigt nach dem Laden „0 %“ obwohl das Modell schon 33 % meldet.
   → ✅ `fokus` je Ziel + `zurueck` vor jedem Ziel (Test `modell3d.test.cjs`, Befehl am echten Modell geprüft); Hinweistext „Tippe auf ‚Los‘“; der Erkunden-Balken zeigt bis zur ersten Modellmeldung „Modell wird geladen …“ statt „0 %“ (im Browser kam der Balken nach ≈ 1 s auf 33 %).
11. **`film.css`** – Bühne misst bei 768 × 1024 mit Kopfzeile 46 % der Höhe (Filmrahmen allein 40 %). → Kopfzeile kompakter oder Rahmen 36 %, damit die Bühne ≤ 40 % bleibt.
   → ✅ Rahmen 34 vh, kompakte Kopfzeile: Bühne 402 px = 39 % bei 768 × 1024 (vorher 46 %).
12. **Glossar-Links im Fließtext** der Lesestrecke sind 28 px hoch → unsichtbare Trefferfläche ≥ 44 px (Padding, ohne Zeilenabstand zu ändern).
   → ✅ Unsichtbare Trefferfläche 44 px per Pseudo-Element (Zeilenabstand und Hintergrund unverändert; `test_darstellung` grün); gemessen: ±22 px um den Link.
13. **Blitz** – Stufen-Gewichtung: Auf Niveau C kommen nur ~2 von 10 Fragen aus Stufe 3; → gewichten (Stufen des Niveaus gleichmäßig oder aufsteigend).
   → ✅ Nächste Frage: erst eine Stufe des Niveaus zufällig, dann eine Frage daraus (Test: je ≈ 1/3).
14. **`ASSET_VERSION`** in `config.py` erhöhen (Bilder sind ersetzt worden).
   → ✅ `ASSET_VERSION` = 20261004b.
15. **`INHALTE.bildpunkte`** – prüfen, dass die Karten-Daten aller `bildpunkte`/`bildwahl`-Aufgaben aus den JSON-Dateien der Grafik-Agenten (`werkzeuge/*_punkte.json`, `tanzraetsel_ziele.json`) stimmen (Test: jeder Punkt liegt im Bild, Rand ≥ 24, Abstände).
   → ✅ Test `test_kartenpunkte_und_ziele_stimmen_mit_den_daten_der_grafik_agenten_ueberein`: Randabstand ≥ 24, Punktabstand ≥ 48 (Warnung < 100), Abgleich mit `werkzeuge/*_karte_punkte.json` und `tanzraetsel_ziele.json`.
16. **`film.js`/`film.css` Bühne in Stationen ohne Film** – Auf schmalen Anzeigen (< 1100 px, auch iPad quer) klebt die Bühne in **jeder** Station des Reiters oben und verdeckt ein Drittel, obwohl nur einzelne Stationen Film/Modell brauchen. → In Stationen ohne `modell`/`film`-Bindung die Bühne standardmäßig eingeklappt anzeigen (einklappbar bleibt sie), beim Öffnen einer gebundenen Station automatisch aufklappen.
   → ✅ In Stationen ohne Film-/Modell-Bindung steht die Bühne unter 1100 px eingeklappt; gebundene Stationen klappen sie auf (34/34 Stationen der Reiter 2–4 im Browser geprüft). Die eingeklappte Bühne behält 320 × 180 px (sonst meldet der Film `drawImage`-Fehler).
17. **`forschen.js` `protokoll`** – Fehlermeldung bei falscher Zahl lautet immer „Zähle noch einmal genau nach“, auch bei Rechenzeilen. → optionales Feld `fehlertext` je Zeile.
   → ✅ Optionales Zeilenfeld `fehlertext`.
18. **`FORSCHEN.md` `vermutung` Niveau B** – Beispiel „Ich vermute, dass …“ + Baustein „weil …“ ergibt „dass weil“ → Beispiel in der Doku anpassen („Das vermute ich, …“ + „weil …“).
   → ✅ `FORSCHEN.md`: Satzanfang „Das vermute ich: …“ + Hinweis, wie Bausteine angehängt werden.
