# Audit „Funktioniert der forschend-entwickelnde Ansatz?“ (4. Oktober 2026)

Anlass: Stephan will wissen, ob in **allen** Aufgaben der forschend-entwickelnde Ansatz trägt und ob Kinder ihre Vermutungen **innerhalb des ABs
selbst überprüfen** können. Vier unabhängige Prüfer-Agenten haben die Reiter wie ein Kind im Browser durchgespielt (Modell, Film, Bilder).
Dieses Dokument ist der gemeinsame Arbeitsauftrag für die Korrekturen. **Interne Nummern** (aus `plan_*.py`); Anzeigenummern sind fortlaufend 1–46.

## Entscheidungen des Leiters (gelten für alle)

1. **`pruefen` wird neu gedacht.** Bisher fragte es Merksätze ab (richtige Option immer die längste, Ablenker absurd, Beleg stand in der Quelle).
   Neu: (a) **Alle Optionen gleich lang und gleich gebaut**, jede eine **prüfbare Einzelaussage** über das, was man im Modell/Film/Bild sehen kann;
   (b) Ablenker sind **plausible Vermutungen**, die die Evidenz widerlegt; (c) **jede Station hat `erkenntnis.hinweis`** (nach 2 Fehlern) und einen
   **Knopf zur Evidenz** (`modell`: Kapitel/Ansicht, **spielt automatisch ab**), die `quelle` ist **neutral** („Schau dir Kapitel 5 an.“) und verrät keine
   Option; (d) die **Selbsteinschätzung** bekommt eine vierte Antwort „Das kann ich hier nicht herausfinden“ (für freie Vermutungen);
   (e) **jede Vermutungsoption muss durch die Evidenz bestätigt oder widerlegt werden können** – sonst Option streichen oder Evidenz-Zeile ergänzen.
2. **Film-/Modell-Knöpfe in Aufgaben starten die Wiedergabe sofort** (`spielen` anhängen) und springen bei Schlüsselsätzen **sekundengenau**
   (Zeiten aus `papiertheater/docs/ab_uebergabe.md`), Beschriftung: „▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)“.
3. **Ehrliche Quoten:** Forschen zählt nur, wo das Kind **Evidenz sammelt** (zählen, vergleichen, suchen, entscheiden am Material). Reine Vokabelaufgaben am
   Bild und Zeichnen sind **Anwenden**, nicht Forschen. Die Tests zählen entsprechend (Technik-Agent passt an); Reiter dürfen dann ≥ 50 % unterschreiten,
   solange die Forschen-Stationen echt sind (Mindestens 3 echte Forschen-Stationen je Reiter 2–4).
4. **Futterfrage ehrlich:** Die Biene sucht ihr Futter **meist selbst**; im Spätsommer ergänzt der Imker Zuckerlösung. Überall „meist“, kein „niemand füttert“.
   (Leitfrage auf der Startseite ist schon angepasst.)
5. **Keine Zahl/Aussage vorwegnehmen:** Was ein späterer Reiter/Film **erforschen** soll, erscheint vorher nirgends als Erklärung, Option oder Hinweis.
6. **Sprachwerkstatt:** eigener `hilfe`-Text je Aufgabe (nie „Ein Blick in die Lesestrecke hilft“, wenn die Lesestrecke es nicht enthält); Bilder/Beispiele für
   sprachschwache Kinder wo möglich; **alle richtigen Antworten werden akzeptiert** (Artikel mit/ohne, Alias, Umlaute).

## Querschnitt: Technik (`forschen.js`, `film.js`, `aufgaben.js`, `index.html`, Docs, Tests)

- **T1 Film-/Modell-Knöpfe**: `kap()`/`kapZeile()`/Modell-Knöpfe hängen `{mw:"spielen"}` an (Film) und unterstützen `springe` auf Sekunden mit Beschriftung;
  `pruefen` und `protokoll`/`tabelle` können Knopflisten (`modell: [...]`) haben und zeigen sie im Prüfen-Kasten; **Bild-Knopf** (öffnet ein Bild im Overlay) als
  weitere Knopfart (`bild: "/static/img/lese/…"`, `text`) für Stationen ohne Film/Modell (z. B. Rückblick auf das Bild einer früheren Station).
- **T2 `pruefen`**: vierte Selbsteinschätzung „Das kann ich hier nicht herausfinden“ (sperrt nichts, Erkenntnis bleibt wählbar); Fehlerrückmeldung nennt **nie**
  „was du beobachtet hast“ bei Beleg-Fragen (eigene Texte je Stufe); `erkenntnis.hinweis` Pflicht (Test); Optionslängen-Test: richtige Option ist nicht die längste
  und nicht kürzer als 70 % der längsten (Test in `forschen_pruefen.py`).
- **T3 Raten verhindern** (`tabelle`, `protokoll`): Die **erste** Prüfung meldet nur „x von y Feldern stimmen“ **ohne Färbung**; ab der zweiten Prüfung Färbung/Hinweise
  (`cfg.sofortFaerben: true` schaltet das alte Verhalten ein). Ein erneutes „Prüfen“ ohne Änderung zählt nicht als Fehlversuch.
- **T4 Zahleingabe**: `parseZahl` kennt Zahlwörter auch größer als zwölf (einundzwanzig, zweitausend, fünfzigtausend, „50 000“, „50.000“, „50000“); Zeilenfeld `fehlertext`.
- **T5 Standard-Hilfetext**: Standardhinweis bei Fehlern in `luecke`/`sortierung`/`zuordnung`/`mc` **neutral** („Schau noch einmal genau hin.“); „Ein Blick in die Lesestrecke
  hilft“ nur, wenn die Aufgabe `hilfe` mit Lesestrecken-Bezug setzt. Zuordnung: `cfg.hinweis` ersetzt den Standardsatz „links Begriff, rechts Erklärung“.
- **T6 Film-Karte** (`film`, Nr. „Film ansehen“): Fortschrittsbalken der Karte aktualisiert **laufend** (nicht erst bei Abschluss), `filmAufgabeAktualisieren` auf jedes Status-Ereignis.
- **T7 Pflicht-Sperre** (`film.js`): Station wird erst frei, wenn **alle** `pflicht`-Knöpfe der Station gedrückt wurden (nicht ein beliebiger); (nach Möglichkeit: Knopf *und*
  mindestens 3 s Wiedergabe bzw. Modell-Meldung).
- **T8 Forscherbuch**: „Abgeben“ schneidet bei 2000 Zeichen ab → Limit auf 8000 (`ANTWORT_MAX_ZEICHEN` und Aufruf); Buch zeigt zusätzlich die **eigene Einschätzung** und – wenn
  vorhanden – den **eigenen C-Satz**; Vermutungs-Satzbau korrigieren (C-Satzanfang „Meine Vermutung: …“, B-Baustein „weil …“ auch ohne Vortext, `min` zählt nur eigenen Text).
- **T9 Notizen** (`aufgaben.js`): Platzhalter und Pflichtfeld „Quelle“ je Aufgabe konfigurierbar (`cfg.platzhalter`, `quelleNoetig: false`).
- **T10 Kleinkram**: `normalize` für Eingaben: „Wieviele“ = „Wie viele“; `index.html` Einleitung „In **den meisten** Abschnitten vermutest du …“; Kommentar „Nutztier 43/44“ in
  `inhalte_abschluss.js` (Inhalts-Agent); `bildpunkte` Alias-/Rückmeldungs-Mechanik: eigener Satz für „Bienenstock“ (siehe Reiter 1).

## Reiter 1 `nutztier` (Agentin C1)

*Blocker*
- **47 (W-Fragen) A/B**: Korrekte Fragen werden als falsch gewertet („Wann sammeln die Bienen Nektar?“; „Wie erntet der Imker den Honig?“); in A steht „Wann“ als Ablenker, das
  eine zweite gültige Frage ergibt. Fix: **A, B wie C** mit vorgegebenem **Antwortsatz** vor der Lücke (z. B. „Antwort: Die Bienen sammeln Nektar auf Blüten. Frage: [Wo] sammeln die
  Bienen Nektar?“); Fragen mit **verschiedenen Antworttypen** (Wo/Was/Wer/Wie viele/Woher); Ablenker „Wann“ in A streichen; C-Antwortsatz „Die Königin legt Eier“ ersetzen durch
  „Die Bienen sammeln Nektar“ (spoilert Reiter 3); Aliase („Wieviele“).
- **45 C (Artikel/Plural)**: Plural ohne Artikel gilt als falsch (0 von 6). Fix: Artikel vorgeben („Die Biene – die [Bienen]“), geprüft wird nur die Pluralform (Schwierigkeit: Völker,
  Kühe, Hühner); oder Aliase mit/ohne Artikel. Titelbeispiel „Die Biene – die Bienen“ nicht in die Aufgabe übernehmen.

*Wichtig*
- **43 (Tabelle)** löst sich ohne Hinsehen: (a) Optionswortlaut verrät die Biene („niemand – es sucht selbst“, „fliegt“, „der Imker“); (b) Biene immer letzte Spalte und einzige mit Option 2;
  Optionsreihenfolge = Spaltenreihenfolge (Diagonale). Fix: Biene **in die Mitte** (Kuh, Biene, Huhn, Schaf), Optionsreihenfolge je Zeile **gemischt**, Optionen **neutral und symmetrisch**
  („Der Mensch bringt das Futter.“ / „Das Tier holt sich sein Futter meist selbst.“ / **dritte Option „beides“** in den Zeilen 1 und 2); „Wer kümmert sich?“ (C) mit neutralen Optionen;
  (c) **Bild nicht sichtbar**: Station 3 ist eingeklappt → **Zeilenbild** `/static/img/lese/imker-karte.svg` (antippbar) an die Zeilen „Wo lebt das Tier?“ und (C) „Wer kümmert sich?“
  oder **Bild-Knopf** (T1); Hinweis neu: „Siehst du im Bild irgendwo Futter für die Biene? Wo könnte sie es finden?“ statt „Wohin **muss** die Biene fliegen…“; (d) fachlich: Kuh/Schaf stehen im
  Sommer auf der Weide → „meist“; „Wo lebt das Tier?“ → „Wo ist das Tier tagsüber?“ ohne „fliegt“; Schaf: „Milch“ unscharf → Spalte „Was gibt es uns?“ nur eindeutig (Kuh: Milch, Huhn: Eier, Schaf: Wolle,
  Biene: Honig); (e) Merksatz auf A passt zu den A-Zeilen (A hat keine „Imker kümmert sich“-Zeile → Merksatz kürzen oder Zeile aufnehmen). Das Bild trägt „Wo lebt sie?“ und „Was gibt sie uns?“, **nicht** „Wer füttert?“ –
  Evidenz ergänzen: im SVG (Karte) 2–3 kleine Bienen an Flugloch/Blüte (Grafik-Agent).
- **3 (Bild „Beim Imker“)** ist nicht eingebettet: kein Auftrag. Fix: Auftragstext „Du besuchst einen Imker. Schau genau hin: Wo steht der Bienenkasten? Was tut der Imker? Was macht die Biene? Das brauchst du
  gleich im Vergleich.“ (Station 43 verweist darauf). **C ist eine Sackgasse**: „Räuchergerät“, „Netz“, „Bienenstock“ werden abgelehnt → Aliase (Räuchergerät, Raeuchergeraet, Rauchapparat, Imkerhaube, Imkernetz,
  Netz, Gesichtsschutz, Kopfschutz), für „Bienenstock“ eine eigene Rückmeldung („Bienenstock ist das ganze Zuhause des Volkes. Die Holzkiste heißt …“), `hilfe` mit echter Hilfe.
- **42 (Schätzfrage)** verrät sich: Die richtige Option ist immer die einzige mit „bis zu etwa“ und die größte Zahl. Fix: alle Optionen im **gleichen Format** (A „etwa 500 / etwa 5 000 / etwa 50 000“; B vier Zahlen im
  Format; C Sommer-Winter-Paare im gleichen Muster). **Der Reiter `volk` fragt nicht mehr nach der Bienenzahl** (siehe dort).
- **45/46/47 Sprachwerkstatt**: je Niveau eigener `hilfe`-Text (nicht „Lesestrecke“); **46**: Sprachziel (letztes Wort bestimmt den Artikel) wird nicht geübt → auf `luecke` mit Chips umstellen („das Glas + der Honig → [das] Honigglas“,
  Artikel wählen) und `TYPEN` anpassen; **45**: Bilder/Emoji am Nomen (🐝 Die Biene …), Artikel farbig (der blau, die rot, das grün – falls im Gerüst möglich, sonst Emoji/Bild), Ablenker „Volke“/„Kuhen“ entfernen.
- **L1**: Abschnitt 2 und 3 wiederholen 43 und 41 fast wörtlich → neue Fakten ergänzen (Sammelflug meist bis etwa 3 km, Bienen kehren zum Kasten zurück; Abschnitt 3 mit Apfelblüte → Apfel nur, wenn 41 sie nicht vorwegnimmt) oder
  L1 auf 3 Abschnitte kürzen (1; 2+3; 4).
- **7 (Notizen)**: Hinweis „Im 3D-Modell, im Film und in den Lesestrecken findest du vielleicht Antworten. Am Ende prüfst du, welche Fragen beantwortet sind.“; Eyebrow nicht „Mein Forscherbuch“; in **Station 80 (Abschluss)** einen Satz/eine Frage „Welche deiner Fragen vom Anfang ist beantwortet?“ (Agentin C1 zuständig).
- **41**: C-Option „Hilfe, damit Früchte wachsen“ missverständlich → „Sie tragen Pollen von Blüte zu Blüte (Bestäubung).“; Hilfetext „Gleich siehst du es beim Imker“ → „Das lernst du gleich noch genauer kennen“; Rückmeldungen „Nicht ganz.“ statt „Leider falsch.“ (über `cfg.hilfe`); Forscherbuch listet 41/42-Erklärungen als „Erkenntnisse“ – nur 43 (Tabelle) trägt `erkenntnis`.

## Reiter 3 `volk` (Agentin C3)

*Blocker*
- **v_chef (60) → 64**: Nur eine von vier Optionen ist prüfbar. Fix: `pruefen` nach Entscheidung 1 neu: Erkenntnis für A/B/C: „Niemand befiehlt. Die Königin legt Eier, die Arbeiterinnen wechseln mit dem Alter ihre Aufgabe, und das Volk arbeitet zusammen.“;
  Ablenker gleich gebaut („Die Königin sagt jeder Biene, was sie tun soll.“ / „Der Imker sagt den Bienen, was sie tun sollen.“ / „Jede Biene macht den ganzen Tag, was sie will.“); **Quelle neutral** mit **drei Knöpfen**: Kapitel 5 (Befehle), Kapitel 7 (Aufgabenwechsel), Kapitel 12 (zusammen) – jeweils mit Satzsprung (T1);
  Imker-Beleg in B/C: „Der Imker kommt nur am Kasten (Kap. 2) und bei der Ernte (Kap. 10) vor.“; **in 62 eine Zeile zu Kapitel 7** für alle Niveaus („Was passiert mit der Arbeit einer Arbeiterin, wenn sie älter wird?“ bleibt gleich / wechselt / hört auf; **ersetzt** die Zeile
  „Wie viele Bienen im Sommer?“); Beleg „Das steht in der Lesestrecke“ entfällt (L3 kommt danach); der Beleg „Das hat mir der Imker im Film erzählt“ ist trivial falsch → ersetzen durch plausible Fehlbelege.

*Wichtig*
- **Bienenzahl** nicht mehr im Reiter `volk` abfragen (Reiter 1 hat die Frage und die Erklärung): 18 Beobachtung 1 und 62 Zeile 1 ersetzen (siehe oben, z. B. 18: „Wo liegt der Honig, wo wachsen die jungen Bienen?“ bleibt als Beobachtung 3 – dafür Beobachtung 1 neu: „Wer legt die Eier, und wie viele an einem Tag?“).
- **68 „Echt oder nur im Film?“**: Spalte „in echt“ ist im AB nicht belegt (nur 12–14 mm steht in Reiter 2). Fix: Nur Zeilen behalten, die das AB belegt, **oder** Station **nach L3 verschieben** (`STATIONEN […, 66, "L3", 68, …]`, `leseNach: 66`) und L3 + Glossar um je einen Satz ergänzen: roter Punkt (Imker malen ihn auf), Rähmchen (im Kasten hängen viel mehr), Honigernte (Honig wird in echt geschleudert – „Schleuder“ steht in L4, daher Zeile streichen oder einen Satz in L3), Entwicklung („im Film in etwa 12 s“ gegen „21 Tage“); Beschreibung „das Bild mit den weißen Eiern, oben rechts“ statt „Zählbild“.
  Erste Prüfung zeigt nur „x von y stimmen“ (T3).
- **66 Tanzrätsel**: A hat nur 2 Runden, Länge wird nie benutzt, Merksatz behauptet sie → A mit 3 Runden **oder** Merksatz je Niveau; A/B nennen die Regel in der Frage (gewollt), **C: erste falsche Rückmeldung neutral** („Schau noch einmal genau hin.“), Kriterien erst im Hinweis nach dem 2. Fehler; C Runde 3: „Ich erkenne es an …“ als Satzfeld; B Runde 1: Hinweis ≠ Tipp aus der Frage. Der Pflicht-Knopf (Kapitel 9) **spielt ab** (T1) und springt auf **163,5 s** (Tanzbeginn) – Beschriftung „▶ Sieh dir den Tanz an (Kapitel 9)“.
- **65, 67 Sprachwerkstatt**: `hilfe` („Sieh dir Kapitel 6 im Film noch einmal an.“ / „Kapitel 9: Was zeigt die Dauer des Schwänzelns?“); 65 C an den Filmtext angleichen („Zuerst putzt …, dann füttert …, später baut sie Waben und hält Wache. Schließlich fliegt sie als Sammlerin aus.“); 67 „deshalb“ mit Aliasen (darum, daher).
- **Zahleingabe**: `fehlertext: "Schreibe die Zahl mit Ziffern, z. B. 12."` bei „21 Tage“-Zeilen (T4 erweitert zusätzlich Zahlwörter).
- **Ehrliche Quote**: 21 (Kasten beschriften) und 26 (Zeichnen) sind Anwenden/Vokabel. Das ist in Ordnung, aber nicht als „Forschen“ zählen (Technik passt die Zählung an). Echte Forschen-Stationen: 60, 62, 63, 64, 66, 68.

*Klein*: 62 `hinweis2` nennt „fünfzigtausend“ (entfällt mit Zeile 1); 62 A „Brutraum“/„Honigraum“ als zwei Binärzeilen → eine Zeile „Was liegt oben, was unten?“; 63 Zeile „Arbeiterin arbeitet im Stock“ → „macht viele Arbeiten (putzen, bauen, sammeln)“; 18 Auftrag 2 „Gibt noch jemand anderes Befehle?“.

## Reiter 4 `nutzen` + Abschluss (Agentin C4)

*Blocker*
- **75 (Bild-Rätsel)** ist kein Forschen: Das Bild `nutzen-5` trägt die Lösungswörter als Etiketten („Blühwiese“, „kahle Fläche“, „Pestizid“, „Varroa-Milbe“), jede Runde hat nur **2 Kreise**, die Fragen nennen die Gefahr, der Fehlertext verrät den Rest, `hinweis` ist unerreichbar.
  Fix: **neue Rätselfassung des Bildes ohne Etiketten** (`nutzen-5-raetsel.svg`, Grafik-Agent; `nutzen-5` mit Etiketten bleibt in L4); **4 Kreise je Runde** (alle Orte des Bildes); Fragen **ohne Gefahrenwort** („Hier fehlen Bienen. Tippe auf einen Grund, den du im Bild findest.“); **ein** neutraler Fehlertext („Hier sitzen Bienen. Such eine Stelle, an der keine sitzen.“); Etiketten/`erklaerung` erst **nach** dem Tippen (Lupe, Wort „Varroa-Milbe“ erst nach richtigem Tipp);
  optional Beobachtungszeile „Auf welcher Seite sitzen keine Bienen?“.
- **73 und 76 (`pruefen`)** prüfen die Vermutung nicht, sie fragen den Merksatz ab (richtige Option **immer die längste**, Beleg steht wörtlich in der Quelle, absurde Ablenker, keine `hinweis`, **76 hat keinen Knopf zum Bild**). Fix nach Entscheidung 1:
  gleich lange, gleich gebaute Optionen aus prüfbaren Einzelaussagen (73 A z. B. „Ohne Bienen gäbe es keinen Honig und weniger Früchte.“ / „… keinen Honig, aber genauso viele Früchte.“ / „… Honig, aber weniger Früchte.“); Beleg-Optionen als **konkrete Beobachtungen** („Im Film machen die Bienen aus Nektar Honig.“);
  `erkenntnis.hinweis` setzen; 73: `modell` mit Kapitel 10 **und** 12 (nicht Pflicht); 76: **Bild-Knopf** (T1) zur Rätsel-Karte 75; Quelle neutral.

*Wichtig*
- **72 (Apfelzweige)**: Ergebnis (12 und 2 Äpfel) steht schon im Auftrag, Z1/Z3 abschreibbar, Option verrät Antwort; Mechanismus nicht aus den Zahlen ableitbar. Fix: Auftrag nur mit Aufbau (Zweig 1 offen, Zweig 2 mit Netz gegen Insekten, je 20 Blüten); **erste Zeile `art: "text"`: „Meine Vermutung: Wie viele Äpfel wachsen an Zweig 2?“** (nur Länge geprüft), **danach** (als `erklaerung` dieser Zeile) die Beispielzahlen; klare Kennzeichnung „**Ausgedachtes Beispiel** – die Zahlen sind nicht gemessen“; Merksatz/L4 nicht als Beleg („Forscher haben das untersucht“ nur mit echter Quelle – hat das Konzept nicht → „Im Beispiel…“); C-Hinweis „Wähle nur, was du aus den Zahlen ablesen kannst“ ersetzen (die richtige Option „Ohne Bestäubung bilden Blüten kaum Früchte“ ist **nicht** direkt ablesbar → Zeile „Was könnte der Grund sein?“ mit Vermutungscharakter); „Bienen“ im Aufbau → „Insekten“ (das Netz hält alle fern).
- **Doppelungen mit Reiter 1/2**: 41 hat denselben Merksatz wie 70→73; 71 Zeile 0 („Wohin kommt der Nektar?“) wiederholt `v_sammeln` aus Reiter 2. Fix: 70 **schärfer** („Wie viele Äpfel trägt ein Baum, wenn keine Insekten kommen?“) oder Reiter 1 nennt Bestäubung nicht (**Entscheidung: Reiter 1 behält Bestäubung nur als Option in 41; Reiter 4 ändert 70**); 71 Zeile 0 ersetzen durch eine neue Beobachtung aus Kapitel 10 (z. B. „Was machen die Bienen mit dem Nektar im Stock?“).
- **74-Ablenker** „Regen im Sommer“, „Vögel“ sind im AB weder belegt noch widerlegt → ersetzen durch durch Bild/Film **widerlegbare** Optionen oder 76 erhält einen ehrlichen Satz („Regen und Vögel zeigt das Bild nicht – dazu wissen wir hier nichts“).
- **36 A**: Reihenfolge nicht eindeutig (Pestizid-Satz vs. „So finden…“) → Pestizid-Satz als letzten Baustein, „So …“ eindeutig an „Deshalb … Blühwiese“ binden.
- **77 Sprachwerkstatt**: A/B sortieren nur Jahreszeiten; B-Sätze sind wörtlich L4 Abschnitt 3 → B ohne Jahreszeitwörter („Dann erntet er …“, „Danach füttert er …“) oder als Lücken mit Chips (zuerst, dann, danach, schließlich); C-Hinweis zählt die Lösung auf.

*Klein*: 71 Zeile 3 „Wie viele volle Rähmchen …“ → „Wie viele Rähmchen zieht der Imker **im Film** heraus?“ (Antwort 1 ist die Papier-Vereinfachung); Zeile 2 „dick und goldfarben“ → „Welche Farbe bekommen die Zellen?“; 71 Zeile 1 A: Ablenker „zurück auf die Wiese“ absurd + Hinweis nennt die Lösung → plausibler Ablenker, neutraler Hinweis; 71 Schluss A: ein Baustein `ok:false`; 73 C: zwei Textzeilen statt „zwei Lücken in einem Feld“; 73 C „weniger Honig, weniger Wachs“ widerspricht A/B → „keinen Honig, kein Bienenwachs und weniger Früchte“; T Transfer: „ruhig bleiben, Abstand halten“ wird im AB nirgends vermittelt → streichen oder in L4 ergänzen; 40 Quellen: „Apfelzweig-Beispiel ist ausgedacht“; 73/76 Rückmeldung „was du beobachtet hast“ bei Beleg-Frage unpassend (T2).

## Reiter 2 `koerper` (Agentin C2)

Kern: Dramaturgie und Technik tragen (Zählen am Modell, gestufte Hinweise, Lesestrecke danach). Drei Dinge verhindern echte Überprüfbarkeit.

*Blocker*
- **B1 – Vier Flügel sind mit dem Knopf nicht sichtbar** (51 Zeile 3, A/B/C): „Flügel in der Explosion“ zeigt nur 3 Umrisse (Vorder-/Hinterflügel liegen von oben fast deckungsgleich). Nur `blick: hinten` (Außenansicht, Flügel hervorgehoben) zeigt 4 getrennte Flügel.
  Fix: Knopf ersetzen durch `aussen("Flügel von hinten zeigen", ["fluegel"], "hinten", false)` (A, B, C); Hinweis 1 neutral („Sieh die Flügel von hinten an. Zähle jeden Flügel einzeln.“), Hinweis 2 „Auf jeder Seite liegt ein großer und ein kleiner Flügel übereinander.“ Der alte Hinweis „Auf jeder Seite sitzt mehr als ein Flügel“ liefert die 4 fast direkt → ersetzen.
  Prüfe im echten Modell (Blick hinten) jede Zahl mit einem Kind-Blick (Snapshot/Beschreibung).

*Wichtig*
- **W2 – Station 55 (`pruefen` v_sammeln)**: `quelle` und Knopftexte nennen die Lösungswörter („Honigmagen“, „Hinterbein“); A-Option mit beiden Wörtern ist die einzige richtige; Film-Knopf startet nicht von selbst (Beweisstelle erst ab etwa 2:25). Fix: neutrale `quelle` („Sieh dir Szene 8 im Film an. Achte darauf, wohin der Nektar geht und wo der Pollen bleibt.“); Knopftexte neutral („Organ im Modell zeigen“, „Bein von hinten zeigen“); Film-Knopf `springe t:142` + `spielen`, `pflicht: true` (T1); A-Optionen **plausibel und gleich gebaut** („Beides trägt sie im Honigmagen.“ statt „in den Fühlern“; keine Nonsens-Hypothesen wie „Fühler“, „Kopf“); B-Beleg: richtige Option nicht die längste; Distraktor „Film über den Winter“ ersetzen; `erkenntnis.hinweis` (Entscheidung 1).
- **W3 – Station 9 C: Tipp-Ziele zu klein** (Honigmagen 180 px², Flugmuskeln 378 px², Pollenkörbchen 396 px², Fühler 72 px² ohne Fokus). Fix: `fokus: { teile: [...] }` je Ziel (Technik-Agent liefert das Ziel-Feld; teste mit den neuen Treffflächen: mit Fokus 1 875–5 775 px²), in B auch für „Fühler“ (Blick oben). Der C-Hinweis zum Honigmagen („Vorratsbehälter für Nektar“) verrät Reiter-Inhalt **vor** Vermutung 53 → ersetzen durch Lage-/Formhinweis („Ein kleines Ei im Hinterleib.“); das Ziel „Pollenkörbchen“ nennt schon die Antwort auf die Pollenfrage → aus C streichen oder ans Ende **nach** 55 verschieben (Entscheidung: **streichen**, Pollenkörbchen kommt in 55/Lesestrecke).
- **W4 – Station 54 (Tabelle Innenleben)**: Herz, Gehirn, Darm sind im Modell nicht eindeutig einem Körperteil zuzuordnen (Rückengefäß je zur Hälfte Brust/Hinterleib; Gehirn-Mesh enthält das Bauchmark durch Brust und Hinterleib; Darm: Speiseröhre durch Kopf und Brust). Fix: **Herz aus der C-Tabelle nehmen**, Hinweis zum Gehirn („Suche die dicke gelbe Verdickung.“), „Wo liegt es **hauptsächlich**?“ nur für Honigmagen (Hinterleib), Flugmuskeln (Brust), Gehirn (Kopf = die Verdickung); Merksatz auf das Bearbeitete kürzen (A: Honigmagen, Flugmuskeln, Gehirn); einen **Einstiegssatz zur Forscherfrage 53** („Du suchst, wo die Biene den Nektar tragen könnte. Sieh dir dazu die Organe an.“); die Organ-Knöpfe **alle** Pflicht oder zumindest der Honigmagen-Knopf (sonst tippt man ohne Sehen); Zeile „Wo liegt es?“ ist teils aus Alltagswissen lösbar (Gehirn = Kopf) → eine Zeile „So sieht es aus“ (Form) als Evidenz-Zeile behalten.
- **W5 – Reihenfolge 9 vor 51 verrät „3 Körperteile“ (Namen und Hinweise).** **Entscheidung: Station 9 hinter 52 verschieben** (`STATIONEN [50, 8, 51, 52, 9, 53, …]`): erst zählen/prüfen, dann Namen und Lage festigen. 51 Zeile 5 („Welcher Körperteil trägt Flügel und Beine?“) bleibt mit Namens-Chips. Kommentar in `plan_koerper.py` („Hervorhebungen bleiben stehen“) ist überholt (`modellfinden` sendet vor jedem Ziel `zurueck`).

*Klein*
- K1 Bühne: Die Bedienleiste verdeckt ~38 % der Bühne → Technik (3D-Agent: Befehl `leiste` + kompakte Leiste; `modellfinden`-Ziele blenden die Leiste aus).
- K2 52: die zwei Knöpfe („Seite“, „Explosion“, ohne Hervorhebung) durch dieselben gezielten Ansichten wie in 51 ersetzen („Beine von oben zeigen“, „Flügel von hinten zeigen“); K3 52 B: Beleg „in der Lesestrecke gelesen“ ist offensichtlich falsch (L2 kommt später) → durch plausiblen Fehlbeleg ersetzen; K4 51 C: Textzeile/Schlusssatz nehmen jeden Text ≥ 25/60 Zeichen → Pflichtwort („Beine“) prüfen oder Satzbausteine; K5 56: `cfg.hinweis` („Tippe links auf ein Wort in der Einzahl, dann rechts auf die Mehrzahl.“); 56 C enthält „Wabe/Zelle“ (erst Reiter 3) → Wörter aus diesem Reiter; K6 L2: „Im Film hast du …“ vorsichtiger („Im Film kannst du sehen …“), solange Knopf 55 nicht Pflicht ist (mit Pflicht in W2 wieder in Ordnung); K7 53 A: Optionen A3/A4 nicht plausibel → ersetzen; K8 8 (erkunden): Beobachtungsfragen werden nirgends erfasst → Hinweis auf die eigene Vermutung („Sieh nach, ob deine Vermutung stimmt.“) und „Du findest die Fragen in der nächsten Station wieder.“; K9 siehe B1; K10 siehe W4; 57 C enthält „Zellen der Wabe“ (Film Szene 10 aus anderem Reiter) → ersetzen oder mit Knopf Kapitel 10 belegen; 51: Zahlzeilen lassen sich per +1 durchprobieren (T3 löst das); 51 C-Knopf „Hinterbeine von hinten“ zeigt nur ein Beinpaar, Frage verlangt Vergleich der drei Paare → Knöpfe für alle drei Beinpaare (`vorderbein`/`mittelbein`/`hinterbein`) als Liste.
- 15 Zeichnen ist **Anwenden** (nicht Forschen); 8 und 9 zählen nicht als echte Forschen-Stationen (siehe Entscheidung 3).

