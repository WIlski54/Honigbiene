// Test-Fixtures für die Forschen-Typen (vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch).
// Nur für Tests und die Browserprobe – NICHT Teil der echten Inhalte und nicht in index.html eingebunden.
// Geladen von tests/forschen.test.cjs (Node), tests/test_forschen.py (Strukturprüfung) und werkzeuge/qa_forschen.py (Browserprobe).
// Die Nummern 901–913 und die Stationslisten stehen in FORSCHEN_FIXTURES.plan (so, wie sie in plan_<reiter>.py stünden).
// Die Texte sind Muster. Fakten nur aus „Gesicherte Fakten“ in AB_KONZEPT.md.
window.FORSCHEN_FIXTURES = (() => {
  const film = { film: "biene3d", text: "Biene im Modell öffnen", befehle: [{ mw: "ansicht", name: "gestalt" }, { mw: "blick", name: "seite" }] };
  const kapitel = n => ({ film: "volk", text: `Szene ${n} ansehen`, befehle: [{ mw: "kapitel", n }] });
  const tabs = [
    // ── nutztier: Lesestrecke MITTEN in der Liste (nach 902) ──────────────────────────────────────
    { key: "nutztier", label: "Nutztier Biene", icon: "🐝", kurz: "N", lese: "L1", leseNach: 902, film: "biene3d",
      intro: { eyebrow: "Lesestrecke 1", titel: "Eine Biene als Nutztier", begriffe: ["Nutztier"] },
      aufgaben: [
        { nr: 901, typ: "vermutung", id: "v_anzahl", eyebrow: "Forscherfrage", titel: "Wie viele Bienen leben im Sommer in einem Stock?",
          niveaus: {
            A: { frage: "Was vermutest du?", optionen: ["etwa 50", "etwa 500", "etwa 5 000", "etwa 50 000"] },
            B: { frage: "Was vermutest du?", optionen: ["etwa 50", "etwa 500", "etwa 5 000", "etwa 50 000"], satzanfang: "Ich vermute, dass …", begruendung: ["weil …", "denn …"] },
            C: { frage: "Was vermutest du? Begründe.", satzanfang: "Ich vermute, dass …", frei: true, min: 30 },
          } },
        { nr: 902, typ: "protokoll", eyebrow: "Forschen", titel: "Zähle und beobachte", auftrag: "Drehe die Biene im Modell und trage ein, was du siehst.",
          modell: film, erkenntnis: "Eine Biene hat drei Körperteile, sechs Beine und vier Flügel.",
          niveaus: {
            A: { zeilen: [
              { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, einheit: "Beine", hinweis: "Zähle auf beiden Seiten.", hinweis2: "Sieh dir die Seitenansicht an.",
                modell: { film: "biene3d", text: "Von der Seite zeigen", befehle: [{ mw: "blick", name: "seite" }] } },
              { frage: "Welches Beinpaar trägt das Körbchen?", art: "wahl", optionen: ["vorn", "Mitte", "hinten"], loesung: 2, hinweis: "Schau dir alle drei Beinpaare an." },
            ], schluss: { anfang: "Ich habe beobachtet, dass …", bausteine: ["die Biene sechs Beine hat.", { t: "die Biene acht Beine hat.", ok: false, rueckmeldung: "Zähle noch einmal." }] } },
            B: { zeilen: [
              { frage: "Wie viele Flügel hat die Biene?", art: "zahl", loesung: 4, einheit: "Flügel", hinweis: "Es sind zwei auf jeder Seite." },
              { frage: "Welche Körperteile hat die Biene?", art: "mehrfach", optionen: ["Kopf", "Schwanz", "Brust", "Hinterleib"], loesung: [0, 2, 3], hinweis: "Es sind drei." },
              { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, toleranz: 0, einheit: "Beine" },
            ], schluss: { anfang: "Ich habe beobachtet, dass …", min: 15 } },
            C: { zeilen: [
              { frage: "Wie lang ist eine Arbeiterin etwa in Millimetern?", art: "zahl", loesung: 13, toleranz: 1, einheit: "mm", hinweis: "Sie ist zwischen 12 und 14 mm lang." },
              { frage: "Beschreibe die Augen der Biene.", art: "text", min: 12, satzanfang: "Die Augen der Biene …" },
            ], schluss: { anfang: "Das habe ich beobachtet:", min: 20, pflicht: true } },
          } },
        { nr: 903, typ: "pruefen", vermutung: "v_anzahl", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?",
          quelle: "Sieh dir Szene 1 im Film noch einmal an.",
          // Knopfliste: Film springt auf Sekunden (und spielt sofort), Bild-Knopf öffnet das Bild
          modell: [{ film: "volk", text: "▶ Hör zu: die Zahl im zweiten Satz (Szene 1)", befehle: [{ mw: "springe", t: 1.5 }] }, { bild: "/static/img/lese/imker-karte.svg", text: "Bild noch einmal ansehen", alt: "Karte beim Imker" }],
          erkenntnis: "Im Sommer leben bis zu etwa 50 000 Bienen in einem Stock.",
          niveaus: {
            A: { erkenntnis: { frage: "Was hast du herausgefunden?", optionen: [{ t: "Es leben nur wenige hundert Bienen im Stock.", ok: false }, { t: "Es leben bis zu etwa 50 000 Bienen im Stock.", ok: true }, { t: "Es lebt nur eine einzige Biene im ganzen Stock.", ok: false }], hinweis: "Achte auf die Zahl, die die Sprecherin nennt." } },
            B: { erkenntnis: { frage: "Was hast du herausgefunden?", optionen: [{ t: "Es leben etwa 500 Bienen im ganzen Stock drin.", ok: false }, { t: "Es leben bis zu etwa 50 000 Bienen im Stock.", ok: true }, { t: "Es leben immer genau 5 000 Bienen im ganzen Stock.", ok: false }], hinweis: "Achte auf die Zahl im Film." },
                 beleg: { frage: "Woher weißt du das?", hinweis: "Denk daran, was du im Film gesehen hast.", optionen: [{ t: "Das habe ich im Film gesehen.", ok: true }, { t: "Das habe ich einfach geraten.", ok: false }] } },
            C: { erkenntnis: { frage: "Was hast du herausgefunden?", hinweis: "Sieh dir die Zahl im Film noch einmal an.", optionen: [{ t: "Im Sommer sind es bis zu etwa 50 000 Bienen.", ok: true }, { t: "Im Sommer sind es nur etwa 5 Bienen im Stock.", ok: false }, { t: "Im Sommer sind es höchstens etwa 500 Bienen.", ok: false }] },
                 satz: { anfang: "Ich habe herausgefunden, dass … Meine Vermutung war …", min: 60 } },
          } },
        { nr: 904, typ: "notizen", eyebrow: "Eigene Notizen", titel: "Meine Fragen an einen Imker", abschnitt: "nutztier",
          hinweis: "Schreibe Stichpunkte auf.", kiFrage: "Prüfe diese Stichpunkte (Klasse 6)." },
      ] },

    // ── koerper: Lesestrecke OBEN (ohne leseNach) ─────────────────────────────────────────────────
    { key: "koerper", label: "Die Biene", icon: "🧊", kurz: "B", lese: "L2", film: "biene3d",
      intro: { eyebrow: "Lesestrecke 2", titel: "Eine Biene ist ein Insekt", begriffe: ["Insekt"] },
      aufgaben: [
        { nr: 905, typ: "tabelle", eyebrow: "Vergleichen", titel: "Königin, Arbeiterin und Drohne im Vergleich", auftrag: "Sieh dir die drei Bienen an und fülle die Tabelle aus.",
          modell: kapitel(4), erkenntnis: "Die Drohne hat keinen Stachel. Die Königin hat den längsten Hinterleib.",
          niveaus: {
            // A: Spaltenbilder (Objekte) UND ein Zeilenbild; B: Spalten gemischt (Text und Objekt); C: nur Text
            A: { spalten: [
              { name: "Königin", bild: "/static/img/lese/bienenart-koenigin.svg", alt: "Königin" },
              { name: "Arbeiterin", bild: "/static/img/lese/bienenart-arbeiterin.svg", alt: "Arbeiterin" },
              { name: "Drohne", bild: "/static/img/lese/bienenart-drohne.svg", alt: "Drohne" },
            ], zeilen: [
              { merkmal: "Hinterleib", optionen: ["lang", "mittel", "dick"], loesung: [0, 1, 2], hinweis: "Achte auf den Hinterleib.", hinweis2: "Die Königin ist am längsten.", modell: kapitel(4) },
              { merkmal: "Stachel", optionen: ["hat einen", "hat keinen"], loesung: [0, 0, 1],
                bild: "/static/img/film/still-koenigin.jpg", alt: "Film: Die Königin wird von Arbeiterinnen umringt" },
            ] },
            B: { spalten: ["Königin", { name: "Arbeiterin", bild: "/static/img/lese/bienenart-arbeiterin.svg", alt: "Arbeiterin" }, { name: "Drohne" }], zeilen: [
              { merkmal: "Aufgabe", optionen: ["legt Eier", "sammelt Nektar", "paart sich"], loesung: [0, 1, 2] },
              { merkmal: "Stachel", optionen: ["hat einen", "hat keinen"], loesung: [0, 0, 1] },
              { merkmal: "Geschlecht", optionen: ["weiblich", "männlich"], loesung: [0, 0, 1] },
            ] },
            C: { spalten: ["Königin", "Arbeiterin"], zeilen: [
              { merkmal: "Lebensdauer", optionen: ["3–5 Jahre", "5–6 Wochen", "1 Tag"], loesung: [0, 1] },
              { merkmal: "Eier", optionen: ["legt Eier", "legt keine Eier"], loesung: [0, 1] },
            ] },
          } },
        { nr: 906, typ: "bildwahl", eyebrow: "Rätsel", titel: "Wo ist das Futter?",
          erkenntnis: "Der Tanz zeigt den Bienen, in welche Richtung sie fliegen müssen.",
          niveaus: {
            A: { runden: [
              { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Tippe auf den Baum.",
                ziele: [{ x: 700, y: 180, r: 80, ok: true }, { x: 200, y: 380, r: 80, ok: false, rueckmeldung: "Hier steht kein Baum." }], hinweis: "Bäume sind hoch und haben Blätter.", erklaerung: "Der Baum steht rechts oben." },
            ] },
            B: { runden: [
              { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Tippe auf die Wiese rechts.",
                ziele: [{ x: 700, y: 180, r: 80, ok: true }, { x: 200, y: 380, r: 80, ok: false }, { x: 450, y: 450, r: 70, ok: false }], hinweis: "Sieh genau hin.", erklaerung: "Die Wiese liegt rechts." },
              { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Tippe auf die Wiese links unten.",
                ziele: [{ x: 700, y: 180, r: 80, ok: false }, { x: 200, y: 380, r: 80, ok: true }], erklaerung: "Links unten." },
            ] },
            C: { runden: [
              { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Wo ist das Futter?",
                ziele: [{ x: 700, y: 180, r: 80, ok: false }, { x: 200, y: 380, r: 80, ok: true }], erklaerung: "Das Futter liegt links unten." },
              { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Und jetzt?",
                ziele: [{ x: 700, y: 180, r: 80, ok: true }, { x: 200, y: 380, r: 80, ok: false }], erklaerung: "Jetzt rechts oben." },
              { bild: "/static/img/lese/platzhalter-karte.svg", breite: 900, hoehe: 560, frage: "Zum Schluss.",
                ziele: [{ x: 450, y: 450, r: 90, ok: true }, { x: 200, y: 200, r: 80, ok: false }], erklaerung: "Unten Mitte." },
            ] },
          } },
      ] },

    // ── volk: Lesestrecke ganz am ENDE, Zeilen-Knopf mit Film ─────────────────────────────────────
    { key: "volk", label: "Das Bienenvolk", icon: "🎭", kurz: "V", lese: "L3", leseNach: 909, film: "volk",
      intro: { eyebrow: "Lesestrecke 3", titel: "Wer lebt im Bienenstock?", begriffe: ["Königin"] },
      aufgaben: [
        { nr: 907, typ: "vermutung", id: "v_ei", eyebrow: "Forscherfrage", titel: "Wie lange dauert es, bis aus einem Ei eine Arbeiterin wird?",
          niveaus: {
            A: { frage: "Was vermutest du?", optionen: ["etwa 2 Tage", "etwa 3 Wochen", "etwa 3 Monate"], mehrfach: false },
            B: { frage: "Was vermutest du?", optionen: ["etwa 2 Tage", "etwa 3 Wochen", "etwa 3 Monate"], satzanfang: "Ich vermute, dass es …", begruendung: ["weil …"] },
            C: { satzanfang: "Ich vermute, dass …", frei: true, min: 30 },
          } },
        { nr: 908, typ: "protokoll", eyebrow: "Forschen", titel: "Vom Ei zur Biene", auftrag: "Sieh dir Szene 6 an und trage die Tage ein.",
          erkenntnis: "Aus dem Ei wird in 21 Tagen eine Arbeiterin.",
          niveaus: {
            A: { zeilen: [{ frage: "Wie viele Tage ist es ein Ei?", art: "zahl", loesung: 3, einheit: "Tage", hinweis: "Achte auf die erste Zahl.", modell: kapitel(6) }] },
            B: { zeilen: [{ frage: "Wie viele Tage ist es eine Larve?", art: "zahl", loesung: 6, einheit: "Tage", modell: kapitel(6) }, { frage: "Wie viele Tage ist es eine Puppe?", art: "zahl", loesung: 12, einheit: "Tage" }] },
            C: { zeilen: [{ frage: "Wie viele Tage dauert die ganze Entwicklung?", art: "zahl", loesung: 21, einheit: "Tage", modell: kapitel(6) }] },
          } },
        { nr: 909, typ: "pruefen", vermutung: "v_ei", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?", quelle: "Sieh dir Szene 6 noch einmal an.",
          modell: kapitel(6), erkenntnis: "Eine Arbeiterin braucht 21 Tage vom Ei bis zur Biene.",
          niveaus: {
            A: { erkenntnis: { hinweis: "Sieh dir an, wie lange jede Stufe dauert.", optionen: [{ t: "Es dauert etwa 3 Wochen vom Ei bis zur Biene.", ok: true }, { t: "Es dauert etwa 2 Tage vom Ei bis zu einer Biene.", ok: false }] } },
            B: { erkenntnis: { hinweis: "Sieh dir an, wie lange jede Stufe dauert.", optionen: [{ t: "Es dauert etwa 2 Tage vom Ei bis zu einer Biene.", ok: false }, { t: "Es dauert etwa 3 Wochen vom Ei bis zur Biene.", ok: true }] }, beleg: { hinweis: "Wo hast du die Stufen gesehen?", optionen: [{ t: "Das habe ich im Film gesehen.", ok: true }, { t: "Das habe ich einfach geraten.", ok: false }] } },
            C: { erkenntnis: { hinweis: "Sieh dir an, wie lange jede Stufe dauert.", optionen: [{ t: "Es dauert etwa 3 Monate vom Ei bis zur Biene.", ok: false }, { t: "Es dauert etwa 3 Wochen vom Ei bis zur Biene.", ok: true }] }, satz: { anfang: "Ich habe herausgefunden, dass …", min: 40 } },
          } },
      ] },

    // ── nutzen: Lesestrecke nach der Vermutung, C-Vermutung frei ───────────────────────────────────
    { key: "nutzen", label: "Nutzen & Schutz", icon: "🍯", kurz: "S", lese: "L4", leseNach: 910, film: "volk",
      intro: { eyebrow: "Lesestrecke 4", titel: "Honig, Wachs, Blüten", begriffe: ["Nektar"] },
      aufgaben: [
        { nr: 910, typ: "vermutung", id: "v_honig", eyebrow: "Forscherfrage", titel: "Warum nimmt der Imker nur einen Teil des Honigs?",
          niveaus: {
            A: { optionen: ["Die Bienen brauchen Honig im Winter.", "Der Honig schmeckt den Bienen nicht.", "Der Imker mag keinen Honig."], mehrfach: true },
            B: { optionen: ["Die Bienen brauchen Honig im Winter.", "Der Honig schmeckt den Bienen nicht."], satzanfang: "Ich vermute, dass …", begruendung: ["weil …"], min: 12 },
            C: { satzanfang: "Ich vermute, dass …", frei: true, min: 30 },
          } },
        { nr: 911, typ: "tabelle", eyebrow: "Vergleichen", titel: "Was gibt die Biene?", auftrag: "Ordne zu.", erkenntnis: "Die Biene gibt uns Honig, Wachs und Bestäubung.",
          niveaus: {
            A: { spalten: ["Honig", "Wachs"], zeilen: [{ merkmal: "Wofür?", optionen: ["zum Essen", "für Kerzen"], loesung: [0, 1], modell: kapitel(10) }] },
            B: { spalten: ["Honig", "Wachs"], zeilen: [{ merkmal: "Wofür?", optionen: ["zum Essen", "für Kerzen"], loesung: [0, 1] }, { merkmal: "Woher?", optionen: ["aus Nektar", "aus Drüsen"], loesung: [0, 1] }] },
            C: { spalten: ["Honig", "Wachs"], zeilen: [{ merkmal: "Woher?", optionen: ["aus Nektar", "aus Drüsen", "aus Holz"], loesung: [0, 1] }] },
          } },
        { nr: 912, typ: "pruefen", vermutung: "v_honig", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?", erkenntnis: "Der Honig ist der Wintervorrat der Bienen.",
          niveaus: {
            A: { erkenntnis: { hinweis: "Wozu brauchen die Bienen den Honig im Winter?", optionen: [{ t: "Honig ist der Wintervorrat der Bienen im Stock.", ok: true }, { t: "Honig ist ein Abfall, den die Bienen loswerden.", ok: false }] } },
            B: { erkenntnis: { hinweis: "Wozu brauchen die Bienen den Honig im Winter?", optionen: [{ t: "Honig ist ein Abfall, den die Bienen loswerden.", ok: false }, { t: "Honig ist der Wintervorrat der Bienen im Stock.", ok: true }] }, beleg: { hinweis: "Was machen die Bienen im Winter?", optionen: [{ t: "Das habe ich im Film gesehen.", ok: true }, { t: "Das habe ich einfach geraten.", ok: false }] } },
            C: { erkenntnis: { hinweis: "Wozu brauchen die Bienen den Honig im Winter?", optionen: [{ t: "Honig ist ein Abfall, den die Bienen loswerden.", ok: false }, { t: "Honig ist der Wintervorrat der Bienen im Stock.", ok: true }] }, satz: { anfang: "Ich habe herausgefunden, dass …", min: 40 } },
          } },
      ] },

    // ── abschluss: das Forscherbuch ───────────────────────────────────────────────────────────────
    { key: "abschluss", label: "Abschluss & Quellen", icon: "🏁", kurz: "A", intro: { eyebrow: "Abschluss", titel: "Alles zusammen", begriffe: [] },
      aufgaben: [
        { nr: 913, typ: "forscherbuch", eyebrow: "Mein Forscherbuch", titel: "Mein Forscherbuch", hinweis: "Hier sammelst du alles, was du erforscht hast." },
      ] },
  ];
  // Stationspläne so, wie sie in plan_<reiter>.py stünden (Lesestrecke an beliebiger Stelle)
  const plan = {
    nutztier: { STATIONEN: [901, 902, "L1", 903, 904], TYPEN: { 901: "vermutung", 902: "protokoll", 903: "pruefen", 904: "notizen" } },
    koerper: { STATIONEN: ["L2", 905, 906], TYPEN: { 905: "tabelle", 906: "bildwahl" } },
    volk: { STATIONEN: [907, 908, 909, "L3"], TYPEN: { 907: "vermutung", 908: "protokoll", 909: "pruefen" } },
    nutzen: { STATIONEN: [910, "L4", 911, 912], TYPEN: { 910: "vermutung", 911: "tabelle", 912: "pruefen" } },
    abschluss: { STATIONEN: [913], TYPEN: { 913: "forscherbuch" } },
  };
  return { tabs, plan };
})();
