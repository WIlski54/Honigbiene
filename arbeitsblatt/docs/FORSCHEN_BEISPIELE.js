// Mini-Beispiele für die Forschen-Typen (Muster zum Abschreiben – NICHT geladen, kein Teil der echten Inhalte).
// Format im Detail: docs/FORSCHEN.md und docs/INHALTE_FORMAT.md. Jede Aufgabe hier hat A, B und C und besteht den Strukturtest
// (tests/test_forschen.py prüft diese Datei mit denselben Prüfungen wie die echten Inhalte).
// Alle Texte sind einfacher Text (kein HTML). Antwortoptionen kurz (≤ 12 Wörter), Ablenker klar falsch, nie „dumm“.
// Rückmeldungen verraten die Lösung nicht: Sie lenken auf `quelle`, `hinweis`, `hinweis2` oder den Modell-Knopf.
//
// Aufbau jeder Aufgabe:  nr, typ, eyebrow, titel, niveaus: { A, B, C }
// Feld auf Aufgabenebene (optional, bei jedem Typ erlaubt):
//   modell     Knopf wie bei jeder Aufgabe (Film/Modell einstellen), siehe INHALTE_FORMAT.md
//   erkenntnis Merksatz für das Forscherbuch (Pflicht bei `pruefen`; bei protokoll/tabelle/bildwahl empfohlen)
// Reiter-Objekt: lese: "L2", leseNach: <Nummer der Aufgabe, nach der die Lesestrecke kommt>, film: "volk" (oder "biene3d")
window.FORSCHEN_BEISPIELE = (() => {
  const biene = { film: "biene3d", text: "Biene im Modell öffnen", befehle: [{ mw: "ansicht", name: "gestalt" }] };
  const szene = (n) => ({ film: "volk", text: `Szene ${n} ansehen`, befehle: [{ mw: "kapitel", n }] });

  // ── vermutung ─ Forscherfrage, Vermutung ohne Bewertung. „Vermutung festhalten“ sperrt die Karte. ──
  //   A: optionen (eine Wahl; mehrfach: true = mehrere) · B: optionen + satzanfang + begruendung (Bausteine, „…“ wird entfernt)
  //   C: satzanfang + frei: true + min (Zeichen der Fortsetzung, ohne Satzanfang) · id ist eindeutig und wird von pruefen gelesen
  const vermutung = {
    nr: 901, typ: "vermutung", id: "v_anzahl", eyebrow: "Forscherfrage", titel: "Wie viele Bienen leben im Sommer in einem Stock?",
    niveaus: {
      A: { frage: "Was vermutest du?", optionen: ["etwa 50", "etwa 500", "etwa 5 000", "etwa 50 000"] },
      B: { frage: "Was vermutest du?", optionen: ["etwa 50", "etwa 500", "etwa 5 000", "etwa 50 000"], satzanfang: "Ich vermute, dass …", begruendung: ["weil …", "denn …"] },
      C: { frage: "Was vermutest du? Begründe.", satzanfang: "Ich vermute, dass …", frei: true, min: 30 },
    },
  };

  // ── pruefen ─ Vermutung (per id) mit der Beobachtung vergleichen, Erkenntnis festhalten ──
  //   Ablauf: Vermutung anzeigen → Selbsteinschätzung (stimmt / teilweise / nicht / „kann ich hier nicht herausfinden“, keine Bewertung) → Erkenntnis wählen (ok geprüft)
  //   A: nur erkenntnis · B: + beleg · C: + satz { anfang, min }. `quelle` steht als gelber Kasten über den Fragen: NEUTRAL, nennt keine Option.
  //   Der Merksatz `erkenntnis` auf Aufgabenebene (Pflicht) erscheint danach und steht im Forscherbuch.
  //   Audit T2: `erkenntnis.hinweis` Pflicht (nach 2 Fehlern); alle Optionen gleich lang und gleich gebaut, die richtige nicht die (allein) längste und nicht < 70 % der längsten;
  //   `fehltext` (optional) je Frage ersetzt den Standard-Fehlertext. `modell` darf eine LISTE sein: Film-Knöpfe springen und spielen sofort, ein Bild-Knopf { bild, text, alt } öffnet ein Bild.
  const pruefen = {
    nr: 902, typ: "pruefen", vermutung: "v_anzahl", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?",
    quelle: "Sieh dir Szene 1 im Film noch einmal an. Achte auf die Zahl.",
    modell: [szene(1), { film: "volk", text: "▶ Hör zu: die Zahl im zweiten Satz (Szene 1)", befehle: [{ mw: "springe", t: 1.5 }] }],
    erkenntnis: "Im Sommer leben bis zu etwa 50 000 Bienen in einem Stock.",
    niveaus: {
      A: { erkenntnis: { frage: "Was hast du herausgefunden?", hinweis: "Achte auf die Zahl, die die Sprecherin nennt.",
             optionen: [{ t: "Es leben nur wenige hundert Bienen im Stock.", ok: false }, { t: "Es leben bis zu etwa 50 000 Bienen im Stock.", ok: true }, { t: "Es lebt nur eine einzige Biene im ganzen Stock.", ok: false }] } },
      B: { erkenntnis: { frage: "Was hast du herausgefunden?", hinweis: "Achte auf die Zahl im Film.",
             optionen: [{ t: "Es leben etwa 500 Bienen im ganzen Stock drin.", ok: false }, { t: "Es leben bis zu etwa 50 000 Bienen im Stock.", ok: true }, { t: "Es leben immer genau 5 000 Bienen im ganzen Stock.", ok: false }] },
           beleg: { frage: "Woher weißt du das?", hinweis: "Denk daran, was du im Film gesehen hast.", fehltext: "Dieser Beleg passt noch nicht.",
             optionen: [{ t: "Das habe ich im Film gesehen.", ok: true }, { t: "Das habe ich einfach geraten.", ok: false }] } },
      C: { erkenntnis: { frage: "Was hast du herausgefunden?", hinweis: "Sieh dir die Zahl im Film noch einmal an.",
             optionen: [{ t: "Im Sommer sind es bis zu etwa 50 000 Bienen.", ok: true }, { t: "Im Sommer sind es nur etwa 5 Bienen im Stock.", ok: false }, { t: "Im Sommer sind es höchstens etwa 500 Bienen.", ok: false }] },
           satz: { anfang: "Ich habe herausgefunden, dass … Meine Vermutung war …", min: 60 } },
    },
  };

  // ── protokoll ─ Forscherbogen: Zeilen mit Prüfung ──
  //   Zeilenarten: zahl (loesung, toleranz?, einheit?, schritt?) · wahl (optionen, loesung = Index) · mehrfach (optionen, loesung = Indizes)
  //   · text (min Zeichen, satzanfang?; nur Länge geprüft). Je Zeile: frage, hinweis (nach 2 Fehlern), hinweis2 (nach 3), erklaerung (nach „richtig“),
  //   kurz (Beschriftung im Protokoll der Lehrkraft), modell (Zeilen-Knopf, öffnet genau die Ansicht der Antwort).
  //   schluss (optional): bausteine (A, antippen; Baustein als Text oder { t, ok, rueckmeldung }) · anfang ohne bausteine (B, Satz) ·
  //   ohne anfang (C, frei) · min · pflicht: true (ohne den Satz ist die Station nicht erledigt).
  //   Audit T3 „Raten verhindern“: Die erste Prüfung zählt nur („1 von 2 ausgefüllten Zeilen stimmt“), gefärbt wird ab der zweiten; cfg.sofortFaerben: true färbt sofort.
  //   `modell` an einer Zeile darf eine Liste sein (Film-Knöpfe, Bild-Knöpfe).
  const protokoll = {
    nr: 903, typ: "protokoll", eyebrow: "Forschen", titel: "Zähle und beobachte", auftrag: "Drehe die Biene im Modell und trage ein, was du siehst.",
    modell: biene, erkenntnis: "Eine Biene hat drei Körperteile, sechs Beine und vier Flügel.",
    niveaus: {
      A: { zeilen: [
        { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, einheit: "Beine", hinweis: "Zähle auf beiden Seiten.", hinweis2: "Sieh dir die Seitenansicht an.",
          modell: { film: "biene3d", text: "Von der Seite zeigen", befehle: [{ mw: "blick", name: "seite" }] } },
        { frage: "Welches Beinpaar trägt das Körbchen?", art: "wahl", optionen: ["vorn", "Mitte", "hinten"], loesung: 2, hinweis: "Schau dir alle drei Beinpaare an." },
      ], schluss: { anfang: "Ich habe beobachtet, dass …", bausteine: ["die Biene sechs Beine hat.", { t: "die Biene acht Beine hat.", ok: false, rueckmeldung: "Zähle noch einmal." }] } },
      B: { zeilen: [
        { frage: "Wie viele Flügel hat die Biene?", art: "zahl", loesung: 4, einheit: "Flügel", hinweis: "Es sind zwei auf jeder Seite." },
        { frage: "Welche Körperteile hat die Biene?", art: "mehrfach", kurz: "Körperteile", optionen: ["Kopf", "Schwanz", "Brust", "Hinterleib"], loesung: [0, 2, 3], hinweis: "Es sind drei." },
      ], schluss: { anfang: "Ich habe beobachtet, dass …", min: 15 } },
      C: { zeilen: [
        { frage: "Wie lang ist eine Arbeiterin etwa?", art: "zahl", loesung: 13, toleranz: 1, einheit: "mm", hinweis: "Sie ist zwischen 12 und 14 mm lang." },
        { frage: "Beschreibe die Augen der Biene.", art: "text", min: 12, satzanfang: "Die Augen der Biene …" },
      ], schluss: { anfang: "Das habe ich beobachtet:", min: 20, pflicht: true } },
    },
  };

  // ── tabelle ─ Vergleichstabelle: je Zelle Chips wählen; die erste Prüfung zählt nur, ab der zweiten färbt „Prüfen“ und sperrt richtige Zellen (cfg.sofortFaerben: true = sofort) ──
  //   spalten: Überschriften als Text ODER { name, bild, alt } (Bild über dem Namen; 240 × 180, transparent; auch gemischt) ·
  //   zeilen: merkmal, optionen, loesung = je Spalte der Index der richtigen Option, hinweis/hinweis2, modell (Zeilen-Knopf),
  //   optional bild + alt (16:9, 320 × 180 JPG; antippbar → Vergrößerung). Optionen dürfen Emoji enthalten (Textvergleich nach Index).
  const tabelle = {
    nr: 904, typ: "tabelle", eyebrow: "Vergleichen", titel: "Königin, Arbeiterin und Drohne im Vergleich", auftrag: "Sieh dir die drei Bienen an und fülle die Tabelle aus.",
    modell: szene(4), erkenntnis: "Die Drohne hat keinen Stachel. Die Königin hat den längsten Hinterleib.",
    niveaus: {
      A: { spalten: [
        { name: "Königin", bild: "/static/img/lese/bienenart-koenigin.svg", alt: "Königin" },
        { name: "Arbeiterin", bild: "/static/img/lese/bienenart-arbeiterin.svg", alt: "Arbeiterin" },
        { name: "Drohne", bild: "/static/img/lese/bienenart-drohne.svg", alt: "Drohne" },
      ], zeilen: [
        { merkmal: "Hinterleib", optionen: ["lang", "mittel", "dick"], loesung: [0, 1, 2], hinweis: "Achte auf den Hinterleib.", hinweis2: "Die Königin ist am längsten.", modell: szene(4) },
        { merkmal: "Stachel", optionen: ["hat einen", "hat keinen"], loesung: [0, 0, 1],
          bild: "/static/img/film/still-koenigin.jpg", alt: "Film: Die Königin wird von Arbeiterinnen umringt" },
      ] },
      B: { spalten: ["Königin", { name: "Arbeiterin", bild: "/static/img/lese/bienenart-arbeiterin.svg", alt: "Arbeiterin" }, "Drohne"], zeilen: [
        { merkmal: "Aufgabe", optionen: ["legt Eier", "sammelt Nektar", "paart sich"], loesung: [0, 1, 2] },
        { merkmal: "Stachel", optionen: ["hat einen", "hat keinen"], loesung: [0, 0, 1] },
      ] },
      C: { spalten: ["Königin", "Arbeiterin"], zeilen: [
        { merkmal: "Lebensdauer", optionen: ["3–5 Jahre", "5–6 Wochen", "1 Tag"], loesung: [0, 1] },
        { merkmal: "Eier", optionen: ["legt Eier", "legt keine Eier"], loesung: [0, 1] },
      ] },
    },
  };

  // ── bildwahl ─ Entscheiden am Bild in Runden ──
  //   runden: bild (SVG, 900 × 560 empfohlen), breite, hoehe, frage, ziele [{ x, y, r, ok, rueckmeldung? }] (r ≥ 60 empfohlen: Touchziel),
  //   hinweis (nach 2 Fehlversuchen), erklaerung (nach der richtigen Wahl). Mehrere Runden nacheinander, „Weiter“ nach jeder gelösten.
  const bildwahl = {
    nr: 905, typ: "bildwahl", eyebrow: "Rätsel", titel: "Wo ist das Futter?",
    erkenntnis: "Der Tanz zeigt den Bienen, in welche Richtung sie fliegen müssen.",
    niveaus: {
      A: { runden: [
        { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Tippe auf den Baum.",
          ziele: [{ x: 700, y: 180, r: 80, ok: true }, { x: 200, y: 380, r: 80, ok: false, rueckmeldung: "Hier steht kein Baum." }], hinweis: "Bäume sind hoch und haben Blätter.", erklaerung: "Der Baum steht rechts oben." },
      ] },
      B: { runden: [
        { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Tippe auf die Wiese rechts.",
          ziele: [{ x: 700, y: 180, r: 80, ok: true }, { x: 200, y: 380, r: 80, ok: false }], hinweis: "Sieh genau hin.", erklaerung: "Die Wiese liegt rechts." },
        { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Tippe auf die Wiese links unten.",
          ziele: [{ x: 700, y: 180, r: 80, ok: false }, { x: 200, y: 380, r: 80, ok: true }], erklaerung: "Links unten." },
      ] },
      C: { runden: [
        { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Wo ist das Futter?",
          ziele: [{ x: 700, y: 180, r: 80, ok: false }, { x: 200, y: 380, r: 80, ok: true }, { x: 450, y: 450, r: 70, ok: false }], erklaerung: "Das Futter liegt links unten." },
        { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Und jetzt?",
          ziele: [{ x: 700, y: 180, r: 80, ok: true }, { x: 200, y: 380, r: 80, ok: false }], erklaerung: "Jetzt rechts oben." },
      ] },
    },
  };

  // ── forscherbuch ─ Mein Forscherbuch (Abschluss): nur titel und hinweis, keine Niveaus ──
  //   Sammelt je Reiter Forscherfrage → meine Vermutung → meine Erkenntnis (vermutung und pruefen werden über die id über ALLE Reiter
  //   gepaart), dazu weitere Merksätze und die Notizen der Kinder. Drucken/PDF, Text kopieren, abgeben. Höchstens eins im AB.
  const forscherbuch = { nr: 906, typ: "forscherbuch", eyebrow: "Mein Forscherbuch", titel: "Mein Forscherbuch", hinweis: "Hier sammelst du alles, was du erforscht hast." };

  return { vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch };
})();
