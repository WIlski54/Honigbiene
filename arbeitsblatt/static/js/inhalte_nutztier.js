// Reiter 1 „Nutztier Biene“ – forschend-entwickelnd (docs/FORSCHEN.md). Stationen in Reihenfolge: plan_nutztier.py.
// Ablauf: zwei Einstiegsfragen mit sofortiger Rückmeldung (41, 42) → Entdecken am Bild (3, bildwahl) → Vergleichen (43) → Lesestrecke L1 nachschlagen
// → Sprachwerkstatt (45, 46, 47) → Fragen sammeln (7). Server: lesen_nutztier.py, glossar_nutztier.py.
// Idee: Die Kinder kennen Kuh, Huhn und Schaf. Sie finden selbst heraus, was ein Nutztier ausmacht (der Mensch hält es, weil es
// ihm etwas gibt) und warum die Honigbiene ein besonderes Nutztier ist (lebt frei, sucht ihr Futter meist selbst).
// Dieser Reiter hat weder Film noch 3D-Modell: Forschungsinstrumente sind Bilder. Formate: docs/FORSCHEN.md, docs/INHALTE_FORMAT.md.
// 41 und 42 sind normale Multiple-Choice-Fragen (keine Vermutungen): Im Reiter lässt sich nichts prüfen, also gibt es sofort
// Rückmeldung und Erklärung. Nur Station 43 trägt einen Erkenntnissatz (`erkenntnis`) für das Forscherbuch.
// Audit 4.10.2026: Futter ehrlich („meist“), neutrale Optionen, Antwortsätze in den W-Fragen, eigene Hilfetexte in der Sprachwerkstatt.
(() => {
  "use strict";

  // Bild „Beim Imker“ (Aufgabe 3, bildwahl): Trefferkreise in Pixeln von static/img/lese/imker-karte.svg (900 × 560); Mittelpunkte der Objekte
  // aus werkzeuge/imker_karte_punkte.json, Radius ≥ 60 (Touchziel), Überlappungen entscheidet der nächste Mittelpunkt. Im Browser auf dem Bild geprüft.
  const KARTE = { bild: "/static/img/lese/imker-karte.svg", breite: 900, hoehe: 560 };
  const KREIS = {
    kasten:   { x: 660, y: 352, r: 100 },
    bluete:   { x: 98, y: 490, r: 80 },
    obstbaum: { x: 102, y: 280, r: 95 },
    imker:    { x: 298, y: 380, r: 125 },
    rauch:    { x: 468, y: 462, r: 62 },
    glas:     { x: 842, y: 464, r: 62 },
    biene:    { x: 582, y: 160, r: 85 },
    sonne:    { x: 800, y: 92, r: 75 },
    wolke:    { x: 314, y: 66, r: 95 },
  };
  // Ein Ziel: Kreis + ok + (bei falschem Tipp) neutrale Rückmeldung, die auf etwas im Bild lenkt, aber die Lösung nicht nennt.
  const ziel = (name, ok, rueckmeldung) => Object.assign({}, KREIS[name], { ok }, rueckmeldung ? { rueckmeldung } : {});

  // Spaltenköpfe der Tabelle 43 mit Bild (sprachschwache Lernende): static/img/lese/tier-*.svg, gezeichnet von werkzeuge/grafiken_nutztier.py
  const TIER = {
    kuh:   { name: "Kuh",   bild: "/static/img/lese/tier-kuh.svg",   alt: "Kuh" },
    huhn:  { name: "Huhn",  bild: "/static/img/lese/tier-huhn.svg",  alt: "Huhn" },
    schaf: { name: "Schaf", bild: "/static/img/lese/tier-schaf.svg", alt: "Schaf" },
    biene: { name: "Biene", bild: "/static/img/lese/tier-biene.svg", alt: "Biene" },
  };

  // Bild-Knopf für die Tabelle 43 (Station 3 ist beim Bearbeiten eingeklappt): öffnet die Karte „Beim Imker“ im Bild-Fenster.
  const BILD_IMKER = { bild: "/static/img/lese/imker-karte.svg", text: "Bild „Beim Imker“ ansehen",
                       alt: "Bild beim Imker: Bienenkasten, Imker mit Schleier, Rauchgerät, Honigglas, Blüten, Obstbaum und Biene" };

  INHALTE.tabs.push({
    key: "nutztier", label: "Nutztier Biene", icon: "🐝", kurz: "N", lese: "L1", leseNach: 43,
    intro: {
      eyebrow: "Lesestrecke 1", titel: "Eine Biene als Nutztier",
      begriffe: ["Nutztier", "Imker", "Bienenkasten", "Honig", "Wachs", "Bestäubung", "Bienenvolk"],
    },
    aufgaben: [
      // ── 41 · Was bekommen wir von Bienen? (Einstieg, sofortige Rückmeldung mit Erklärung) ──────────
      // A: eine Antwort aus drei. B: zwei aus fünf (Nomen). C: drei aus fünf (ganze Sätze: Honig, Wachs, Bestäubung).
      // Lösungspositionen sind gemischt (Index in `optionen`). Keine `erkenntnis`: Nur Station 43 füllt das Forscherbuch.
      {
        nr: 41, typ: "mc", eyebrow: "Was weißt du schon?", titel: "Was bekommen wir Menschen von Bienen?",
        niveaus: {
          A: { frage: "Was bekommen wir von den Bienen?",
               erklaerung: "Bienen geben uns Honig und Wachs. Sie tragen auch Pollen von Blüte zu Blüte, damit Früchte wachsen.",
               hilfe: "Das lernst du gleich noch genauer kennen.",
               optionen: [
                 { t: "Milch", ok: false },
                 { t: "Honig", ok: true },
                 { t: "Eier", ok: false },
               ] },
          B: { multi: 2, frage: "Was bekommen wir von den Bienen? Wähle ZWEI.",
               erklaerung: "Bienen geben uns Honig und Wachs. Sie tragen auch Pollen von Blüte zu Blüte, damit Früchte wachsen.",
               hilfe: "Das lernst du gleich noch genauer kennen.",
               optionen: [
                 { t: "Eier", ok: false },
                 { t: "Honig", ok: true },
                 { t: "Milch", ok: false },
                 { t: "Wachs für Kerzen", ok: true },
                 { t: "Wolle", ok: false },
               ] },
          C: { multi: 3, frage: "Was tun Bienen für uns? Wähle DREI.",
               erklaerung: "Bienen geben uns Honig und Wachs. Sie tragen auch Pollen von Blüte zu Blüte, damit Früchte wachsen.",
               hilfe: "Das lernst du gleich noch genauer kennen.",
               optionen: [
                 { t: "Sie geben Milch.", ok: false },
                 { t: "Sie tragen Pollen von Blüte zu Blüte (Bestäubung).", ok: true },
                 { t: "Sie machen Honig.", ok: true },
                 { t: "Sie liefern Wolle.", ok: false },
                 { t: "Sie liefern Wachs für Kerzen.", ok: true },
               ] },
        },
      },

      // ── 42 · Schätzfrage: Wie viele Bienen im Sommer? (Auflösung im Film im Reiter „Das Bienenvolk“) ─────
      // Alle Optionen im gleichen Format (nur Zahlen bzw. Sommer/Winter-Paare), damit die richtige nicht herausragt.
      // Die Zahlen 50, 500 und 5 000 stehen nicht im Konzept: Sie sind falsche Optionen, keine Fakten.
      {
        nr: 42, typ: "mc", eyebrow: "Schätzen", titel: "Wie viele Bienen leben im Sommer in einem Bienenstock?",
        niveaus: {
          A: { frage: "Schätze: Wie viele Bienen leben im Sommer in einem Bienenstock?",
               erklaerung: "Im Sommer bis zu etwa 50 000, im Winter etwa 10 000. Im Film im Reiter „Das Bienenvolk“ siehst du es.",
               hilfe: "Das war eine Schätzfrage. Daneben zu liegen ist nicht schlimm.",
               optionen: [
                 { t: "etwa 5 000", ok: false },
                 { t: "etwa 50 000", ok: true },
                 { t: "etwa 500", ok: false },
               ] },
          B: { frage: "Schätze: Wie viele Bienen leben im Sommer in einem Bienenstock?",
               erklaerung: "Im Sommer bis zu etwa 50 000, im Winter etwa 10 000. Im Film im Reiter „Das Bienenvolk“ siehst du es.",
               hilfe: "Das war eine Schätzfrage. Daneben zu liegen ist nicht schlimm.",
               optionen: [
                 { t: "etwa 5 000", ok: false },
                 { t: "etwa 50", ok: false },
                 { t: "etwa 50 000", ok: true },
                 { t: "etwa 500", ok: false },
               ] },
          C: { frage: "Schätze: Wie viele Bienen leben in einem Bienenstock im Sommer und wie viele im Winter?",
               erklaerung: "Im Sommer bis zu etwa 50 000, im Winter etwa 10 000. Im Film im Reiter „Das Bienenvolk“ siehst du es.",
               hilfe: "Das war eine Schätzfrage. Daneben zu liegen ist nicht schlimm.",
               optionen: [
                 { t: "Sommer etwa 5 000, Winter etwa 500", ok: false },
                 { t: "Sommer etwa 500, Winter etwa 50", ok: false },
                 { t: "Sommer etwa 10 000, Winter etwa 50 000", ok: false },
                 { t: "Sommer etwa 50 000, Winter etwa 10 000", ok: true },
               ] },
        },
      },

      // ── 3 · Entdecken: Bild „Beim Imker“ (bildwahl, echtes Forschen: Evidenz am Bild sammeln) ───────────────────
      // Drei Runden: Wo wohnen die Bienen? Wo finden sie Futter? Wer kümmert sich? Das liefert die Beobachtungen für die Tabelle 43
      // (Station 43 verweist darauf und hat einen Bild-Knopf). A: wenige Kreise, B: alle Objekte, C: alle Objekte und eigener Hinweistext.
      // Rückmeldungen nennen nie die Lösung („Hier wohnen keine Bienen“), `hinweis` kommt nach dem zweiten Fehler.
      {
        nr: 3, typ: "bildwahl", eyebrow: "Entdecken", titel: "Beim Imker: Was entdeckst du?",
        niveaus: {
          A: { runden: [
            Object.assign({}, KARTE, {
              frage: "Du besuchst einen Imker. Schau genau hin! Wo wohnen die Bienen? Tippe auf ihr Zuhause.",
              ziele: [ziel("bluete", false, "Hier wachsen Blumen. Wohnen hier Bienen?"), ziel("kasten", true), ziel("obstbaum", false, "Hier wachsen Äpfel. Wohnen hier Bienen?"), ziel("imker", false, "Hier steht ein Mensch.")],
              hinweis: "Die Bienen brauchen ein Dach über dem Kopf. Such etwas aus Holz.",
              erklaerung: "Das ist ein Bienenkasten, die Holzkiste des Imkers. Darin wohnt ein Bienenvolk." }),
            Object.assign({}, KARTE, {
              frage: "Wo findet die Biene ihr Futter? Tippe auf einen Ort im Bild.",
              ziele: [ziel("kasten", false, "Hier wohnt die Biene. Wo ist sie unterwegs?"), ziel("bluete", true), ziel("imker", false, "Hier steht ein Mensch. Wo könnte die Biene selbst Futter finden?"), ziel("obstbaum", true), ziel("glas", false, "Das ist Honig für uns Menschen. Such draußen weiter.")],
              hinweis: "Wovon ernährt sich eine Biene? Such Pflanzen im Bild.",
              erklaerung: "Die Biene besucht Blüten. Dort findet sie ihr Futter meist selbst." }),
            Object.assign({}, KARTE, {
              frage: "Wer kümmert sich um die Bienen? Tippe auf ihn.",
              ziele: [ziel("biene", false, "Das ist eine Biene."), ziel("kasten", false, "Das ist der Bienenkasten."), ziel("imker", true), ziel("rauch", false, "Das ist ein Gerät.")],
              hinweis: "Wer trägt Schutzkleidung für die Arbeit?",
              erklaerung: "Der Imker stellt den Bienenkasten auf und kümmert sich um die Bienen." }),
          ] },
          B: { runden: [
            Object.assign({}, KARTE, {
              frage: "Du besuchst einen Imker. Schau genau hin! Wo wohnen die Bienen? Tippe auf ihr Zuhause.",
              ziele: [ziel("bluete", false), ziel("imker", false), ziel("obstbaum", false), ziel("rauch", false), ziel("glas", false), ziel("kasten", true), ziel("biene", false)],
              hinweis: "Die Bienen brauchen ein Dach über dem Kopf. Such etwas aus Holz.",
              erklaerung: "Das ist ein Bienenkasten, die Holzkiste des Imkers. Darin wohnt ein Bienenvolk." }),
            Object.assign({}, KARTE, {
              frage: "Wo findet die Biene ihr Futter? Tippe auf einen Ort im Bild.",
              ziele: [ziel("kasten", false, "Hier wohnt die Biene. Wo ist sie unterwegs?"), ziel("imker", false, "Hier steht ein Mensch. Wo könnte die Biene selbst Futter finden?"), ziel("obstbaum", true), ziel("rauch", false), ziel("glas", false, "Das ist Honig für uns Menschen. Such draußen weiter."), ziel("bluete", true), ziel("biene", false, "Die Biene sucht Futter. Wohin fliegt sie?")],
              hinweis: "Wovon ernährt sich eine Biene? Such Pflanzen im Bild.",
              erklaerung: "Die Biene besucht Blüten. Dort findet sie ihr Futter meist selbst." }),
            Object.assign({}, KARTE, {
              frage: "Wer kümmert sich um die Bienen? Tippe auf ihn.",
              ziele: [ziel("rauch", false), ziel("kasten", false), ziel("bluete", false), ziel("biene", false), ziel("imker", true), ziel("obstbaum", false), ziel("glas", false)],
              hinweis: "Wer trägt Schutzkleidung für die Arbeit?",
              erklaerung: "Der Imker stellt den Bienenkasten auf und kümmert sich um die Bienen." }),
          ] },
          C: { runden: [
            Object.assign({}, KARTE, {
              frage: "Du besuchst einen Imker. Schau genau hin! Wo wohnen die Bienen? Tippe auf ihr Zuhause.",
              ziele: [ziel("sonne", false), ziel("wolke", false), ziel("bluete", false), ziel("imker", false), ziel("obstbaum", false), ziel("rauch", false), ziel("glas", false), ziel("kasten", true), ziel("biene", false)],
              hinweis: "Die Bienen brauchen ein Dach über dem Kopf. Such etwas aus Holz.",
              erklaerung: "Das ist ein Bienenkasten, die Holzkiste des Imkers. Darin wohnt ein Bienenvolk. Das ganze Zuhause des Volkes heißt Bienenstock." }),
            Object.assign({}, KARTE, {
              frage: "Wo findet die Biene ihr Futter? Tippe auf einen Ort im Bild. Begründe im Kopf: Woran erkennst du es?",
              ziele: [ziel("wolke", false), ziel("kasten", false, "Hier wohnt die Biene. Wo ist sie unterwegs?"), ziel("sonne", false), ziel("imker", false, "Hier steht ein Mensch. Wo könnte die Biene selbst Futter finden?"), ziel("obstbaum", true), ziel("rauch", false), ziel("glas", false, "Das ist Honig für uns Menschen. Such draußen weiter."), ziel("bluete", true), ziel("biene", false, "Die Biene sucht Futter. Wohin fliegt sie?")],
              hinweis: "Wovon ernährt sich eine Biene? Such Pflanzen im Bild.",
              erklaerung: "Die Biene besucht Blüten. Dort findet sie ihr Futter meist selbst." }),
            Object.assign({}, KARTE, {
              frage: "Wer kümmert sich um die Bienen? Tippe auf ihn.",
              ziele: [ziel("sonne", false), ziel("rauch", false), ziel("wolke", false), ziel("kasten", false), ziel("bluete", false), ziel("biene", false), ziel("imker", true), ziel("obstbaum", false), ziel("glas", false)],
              hinweis: "Wer trägt Schutzkleidung für die Arbeit?",
              erklaerung: "Der Imker stellt den Bienenkasten auf und kümmert sich um die Bienen." }),
          ] },
        },
      },

      // ── 43 · Vergleichen: Kuh, Biene, Huhn und Schaf (Erkenntnis: die Biene ist ein besonderes Nutztier) ──
      // Biene steht in der Mitte, die Optionen sind je Zeile gemischt und gleich gebaut („meist“, dritte Option „Beides“), damit sich die
      // Tabelle nicht ohne Hinsehen lösen lässt. Aus Vorwissen und dem Bild „Beim Imker“. Spaltenköpfe mit Bild, Produkte mit Emoji.
      // Die Hinweise lenken auf Merkmale, nennen aber nie die Antwort.
      {
        nr: 43, typ: "tabelle", eyebrow: "Vergleichen", titel: "Kuh, Biene, Huhn und Schaf im Vergleich",
        auftrag: "Vergleiche die Tiere. Tippe auf ein Feld und wähle, was stimmt. Denke an dein Bild „Beim Imker“.",
        erkenntnis: "Die Honigbiene ist ein besonderes Nutztier: Sie lebt frei und sucht ihr Futter meist selbst.",
        niveaus: {
          A: { spalten: [TIER.kuh, TIER.biene, TIER.huhn], zeilen: [
            { merkmal: "Wer sorgt für das Futter?", modell: BILD_IMKER,
              optionen: ["Das Tier holt sich sein Futter meist selbst.", "Beides gleich oft.", "Der Mensch sorgt meist für das Futter."],
              loesung: [2, 0, 2],
              hinweis: "Siehst du im Bild irgendwo Futter für die Biene? Wo könnte sie es finden?" },
            { merkmal: "Wo ist das Tier tagsüber?", modell: BILD_IMKER,
              optionen: ["Meist beim Menschen auf Hof oder Weide.", "Beides gleich oft.", "Meist draußen, es kommt und geht frei."],
              loesung: [0, 2, 0],
              hinweis: "Schau noch einmal auf das Bild vom Imker: Wo stehen die Bienenkästen? Gibt es einen Zaun?" },
            { merkmal: "Was gibt es uns vor allem?",
              optionen: ["🥚 Eier", "🍯 Honig", "🥛 Milch"],
              loesung: [2, 1, 0],
              hinweis: "Denke an das Frühstück: Was kommt von welchem Tier?" },
          ] },
          B: { spalten: [TIER.kuh, TIER.biene, TIER.huhn, TIER.schaf], zeilen: [
            { merkmal: "Wer sorgt für das Futter?", modell: BILD_IMKER,
              optionen: ["Das Tier holt sich sein Futter meist selbst.", "Beides gleich oft.", "Der Mensch sorgt meist für das Futter."],
              loesung: [2, 0, 2, 2],
              hinweis: "Siehst du im Bild irgendwo Futter für die Biene? Wo könnte sie es finden?" },
            { merkmal: "Wo ist das Tier tagsüber?", modell: BILD_IMKER,
              optionen: ["Meist beim Menschen auf Hof oder Weide.", "Beides gleich oft.", "Meist draußen, es kommt und geht frei."],
              loesung: [0, 2, 0, 0],
              hinweis: "Schau noch einmal auf das Bild vom Imker: Wo stehen die Bienenkästen? Gibt es einen Zaun?" },
            { merkmal: "Was gibt es uns vor allem?",
              optionen: ["🍯 Honig", "🧶 Wolle", "🥛 Milch", "🥚 Eier"],
              loesung: [2, 0, 3, 1],
              hinweis: "Denke an das Frühstück und an den Pullover: Was kommt von welchem Tier?" },
          ] },
          C: { spalten: [TIER.kuh, TIER.biene, TIER.huhn, TIER.schaf], zeilen: [
            { merkmal: "Wer sorgt für das Futter?", modell: BILD_IMKER,
              optionen: ["Der Mensch sorgt meist für das Futter.", "Das Tier holt sich sein Futter meist selbst.", "Beides gleich oft."],
              loesung: [0, 1, 0, 0],
              hinweis: "Siehst du im Bild irgendwo Futter für die Biene? Wo könnte sie es finden?" },
            { merkmal: "Wo ist das Tier tagsüber?", modell: BILD_IMKER,
              optionen: ["Meist draußen, es kommt und geht frei.", "Meist beim Menschen auf Hof oder Weide.", "Beides gleich oft."],
              loesung: [1, 0, 1, 1],
              hinweis: "Schau noch einmal auf das Bild vom Imker: Wo stehen die Bienenkästen? Gibt es einen Zaun?" },
            { merkmal: "Wer kümmert sich um das Tier?", modell: BILD_IMKER,
              optionen: ["der Imker", "niemand", "der Bauer"],
              loesung: [2, 0, 2, 2],
              hinweis: "Wer stellt den Bienenkasten auf?" },
            { merkmal: "Was gibt es uns vor allem?",
              optionen: ["🥚 Eier", "🥛 Milch", "🍯 Honig", "🧶 Wolle"],
              loesung: [1, 2, 0, 3],
              hinweis: "Denke an das Frühstück und an den Pullover: Was kommt von welchem Tier?" },
          ] },
        },
      },

      // ── 45 · Sprachwerkstatt: Artikel und Plural ──────────────────────────────────────────────────
      // A: der, die, das (Chips, Emoji am Nomen). B: die richtige Mehrzahl wählen (Chips, keine falschen Formen in der Kiste).
      // C: nur die Mehrzahl schreiben („die“ steht schon da; Umlaut-Varianten gelten). Alle Formen nach Duden;
      // „Imker“ und „Flügel“ bleiben in der Mehrzahl gleich.
      {
        nr: 45, typ: "luecke", eyebrow: "Sprachwerkstatt · Artikel und Plural", titel: "Der, die, das – und die Mehrzahl",
        niveaus: {
          A: { modus: "chips",
               hilfe: "Sprich das Wort laut mit dem Artikel. Was klingt richtig: der, die oder das?",
               text: "Das ist [die] 🐝 Biene. Das ist [der] 🧑‍🌾 Imker. Das ist [das] 🐔 Huhn. Das ist [das] 🐑 Schaf. Das ist [der] 🍯 Honig. Das ist [die] 🌸 Blüte." },
          B: { modus: "chips",
               hilfe: "Manche Wörter bekommen in der Mehrzahl eine Endung oder einen Umlaut (ä, ü). Bei anderen bleibt das Wort gleich.",
               text: "🐝 Eine Biene – viele [Bienen]. 🧑‍🌾 Ein Imker – viele [Imker]. 🐄 Eine Kuh – viele [Kühe]. 🐔 Ein Huhn – viele [Hühner]. Ein Volk – viele [Völker]." },
          C: { modus: "input",
               hilfe: "Bei vielen sagt man immer „die“. Achte auf das Wort danach: Es bekommt eine Endung (-n, -e, -er), einen Umlaut oder bleibt gleich.",
               text: "Die Biene – die [Bienen]. Der Imker – die [Imker]. Das Volk – die [Völker|Voelker|Volker]. Die Kuh – die [Kühe|Kuehe|Kuhe]. Das Huhn – die [Hühner|Huehner|Huhner]. Der Flügel – die [Flügel|Fluegel|Flugel]." },
        },
      },

      // ── 46 · Sprachwerkstatt: Wörter zusammensetzen – das letzte Wort bestimmt den Artikel ─────────
      // A: Artikel beider Wörter stehen da (der Honig + das Glas → [das] Honigglas). B: ohne Artikel, Chips. C: Artikel schreiben.
      {
        nr: 46, typ: "luecke", eyebrow: "Sprachwerkstatt · Zusammengesetzte Wörter", titel: "Wörter zusammensetzen – das letzte Wort sagt: der, die oder das",
        niveaus: {
          A: { modus: "chips",
               hilfe: "Schau auf das Wort ganz rechts: Sein Artikel gilt auch für das neue Wort.",
               text: "der Honig + das Glas → [das] Honigglas. die Bienen + der Kasten → [der] Bienenkasten. das Wachs + die Kerze → [die] Wachskerze. das Obst + der Baum → [der] Obstbaum. der Rauch + das Gerät → [das] Rauchgerät." },
          B: { modus: "chips",
               hilfe: "Der Artikel richtet sich nach dem Wort ganz rechts. Sprich dieses Wort allein mit der, die oder das.",
               text: "Honig + Glas → [das] Honigglas. Bienen + Kasten → [der] Bienenkasten. Wachs + Kerze → [die] Wachskerze. Bienen + Volk → [das] Bienenvolk. Brut + Raum → [der] Brutraum. Obst + Baum → [der] Obstbaum." },
          C: { modus: "input",
               hilfe: "Der Artikel richtet sich nach dem Wort ganz rechts. Sprich dieses Wort allein mit der, die oder das.",
               text: "Flug + Loch → [das] Flugloch. Honig + Magen → [der] Honigmagen. Pollen + Körbchen → [das] Pollenkörbchen. Honig + Raum → [der] Honigraum. Wachs + Kerze → [die] Wachskerze." },
        },
      },

      // ── 47 · Sprachwerkstatt: Fragen stellen (W-Wörter mit vorgegebenem Antwortsatz) ───────────────
      // Jede Frage hat einen Antwortsatz davor und verschiedene Antworttypen (Ort, Person, Sache, Menge, Herkunft, Zeit, Grund, Richtung).
      // Es steht nur ein W-Wort in der Lücke, das zu Antwort UND Rest der Frage passt. Aliase: Wieso/Weshalb/Wieviele.
      {
        nr: 47, typ: "luecke", eyebrow: "Sprachwerkstatt · W-Fragen", titel: "Fragen stellen",
        niveaus: {
          A: { modus: "chips", ablenker: ["Wohin"],
               hilfe: "Lies die Antwort. Wonach fragt die Frage: nach einem Ort, einer Person, einer Sache oder einer Menge?",
               text: "Antwort: Die Bienen sammeln Nektar auf Blüten. Frage: [Wo] sammeln die Bienen Nektar? Antwort: Der Imker stellt den Bienenkasten auf. Frage: [Wer] stellt den Bienenkasten auf? Antwort: Der Imker erntet Honig. Frage: [Was] erntet der Imker? Antwort: Der Imker hat viele Bienenkästen. Frage: [Wie viele|Wieviele] Bienenkästen hat der Imker?" },
          B: { modus: "input",
               hilfe: "Lies die Antwort. Wonach fragt die Frage: Ort, Person, Sache, Menge oder Herkunft?",
               text: "Antwort: Die Bienen wohnen im Bienenkasten. Frage: [Wo] wohnen die Bienen? Antwort: Der Imker kontrolliert das Bienenvolk. Frage: [Wer] kontrolliert das Bienenvolk? Antwort: Die Bienen machen süßen Honig. Frage: [Was] machen die Bienen? Antwort: Der Imker hat viele Bienenkästen. Frage: [Wie viele|Wieviele] Bienenkästen hat der Imker? Antwort: Den Honig bekommen wir von den Bienen. Frage: [Woher] bekommen wir den Honig?" },
          C: { modus: "input",
               hilfe: "Lies die Antwort genau. Wonach fragt die Frage: Sache, Zeit, Grund, Richtung, Menge oder Herkunft?",
               text: "Antwort: Die Bienen sammeln Nektar. Frage: [Was] sammeln die Bienen? Antwort: Der Imker erntet im Sommer Honig. Frage: [Wann] erntet der Imker Honig? Antwort: Die Bienen brauchen den Rest als Vorrat. Frage: [Warum|Wieso|Weshalb] erntet der Imker nur einen Teil des Honigs? Antwort: Der Imker stellt den Bienenkasten auf eine Wiese. Frage: [Wohin] stellt der Imker den Bienenkasten? Antwort: Der Imker hat viele Bienenkästen. Frage: [Wie viele|Wieviele] Bienenkästen hat der Imker? Antwort: Den Honig bekommen wir von den Bienen. Frage: [Woher] bekommen wir den Honig?" },
        },
      },

      // ── 7 · Fragen sammeln: eigene Fragen an einen Imker (landen im Forscherbuch; am Ende prüft das Kind, welche beantwortet sind) ──
      {
        nr: 7, typ: "notizen", eyebrow: "Fragen sammeln", titel: "Meine Fragen an einen Imker", abschnitt: "nutztier",
        hinweis: "Stell dir vor, ein Imker besucht unsere Klasse. Was möchtest du ihn fragen? Schreibe mindestens drei Fragen auf. Beginne sie mit Wie, Was, Warum, Wo oder Wer. Im 3D-Modell, im Film und in den Lesestrecken findest du vielleicht Antworten. Am Ende prüfst du, welche Fragen beantwortet sind.",
        platzhalter: "• Wie viele Bienenkästen hast du?\n• Warum …?",
        quelleNoetig: false,
        kiFrage: "Prüfe diese Fragen an einen Imker (Klasse 6). Sind es echte Fragen mit einem Fragewort? Passen sie zum Thema „Biene als Nutztier“? Gib einen Tipp, wie eine Frage noch besser werden kann. Schreibe keine fertigen Fragen für das Kind.",
      },
    ],
  });
})();
