// Reiter 3 „Das Bienenvolk“ – Forscherraum mit dem Film „Ein Bienenvolk im Bienenstock“ (INHALTE.filme.volk, Papiertheater,
// 12 Szenen à 20 s = Kapitel 1–12). Stationsplan und Dramaturgie: plan_volk.py. Server: lesen_volk.py, glossar_volk.py.
// Forschend-entwickelnd (docs/FORSCHEN.md): Forscherfrage und Vermutung → mit dem Film erkunden (Beobachtungsbogen, Vergleich,
// Bild beschriften, Tanzrätsel) → Vermutung prüfen und Erkenntnis festhalten → nachschlagen (Lesestrecke) → Filmkritik „Echt oder nur im
// Film?“ (erst nach der Lesestrecke, weil sie die Spalte „in echt“ belegt) → Sprachwerkstatt → Zeichnen.
// Grundregel: Jede Film-Aufgabe fragt nur, was der Film zeigt oder sagt, und nennt die Filmstelle (eyebrow, Knopf).
// Was der Film nicht sagt (Lebensdauer, Stachel, Larve 6 / Puppe 12 Tage), steht erst in der Lesestrecke und wird davor nicht gefragt.
// Audit 4.10.2026: Knöpfe spielen sofort ab und springen bei Schlüsselsätzen auf die Sekunde (Satzzeiten aus papiertheater/docs/ab_uebergabe.md).
// In Kindertexten steht keine Aufgabennummer (die Anzeige zählt fortlaufend).
(() => {
  "use strict";

  // ─── Film-Knöpfe ───────────────────────────────────────────────────────────────────────────────
  // Jeder Knopf springt und spielt sofort ab. Beschriftung: „▶ Hör zu (Kapitel 5)“. Die Beschriftung nennt das Thema, nie die Antwort.
  const VORLAUF = 0.3;   // Sekunden vor dem Satzbeginn, damit der Satz nicht abgeschnitten klingt
  // Kapitelanfang (kapitel n springt an den Beginn der Szene)
  const kap = (n, titel) => ({ film: "volk", text: `▶ Im Film ansehen: Kapitel ${n} – ${titel}`, befehle: [{ mw: "kapitel", n }, { mw: "spielen" }] });
  const kapZeile = n => ({ film: "volk", text: `▶ Kapitel ${n} ansehen`, befehle: [{ mw: "kapitel", n }, { mw: "spielen" }] });
  // Satzsprung: t = Beginn des Satzes in Sekunden (Satzzeiten der Stimme), vorlauf = Sekunden davor
  const satz = (n, t, text, vorlauf = VORLAUF) => ({
    film: "volk", text: `▶ ${text} (Kapitel ${n})`, befehle: [{ mw: "springe", t: Math.round((t - vorlauf) * 10) / 10 }, { mw: "spielen" }],
  });
  const hoer = (n, t) => satz(n, t, "Hör zu");   // neutraler Zeilen-Knopf im Beobachtungsbogen

  // Spaltenköpfe der Vergleichstabelle (Aufgabe 63) mit Bild, damit auch sprachschwache Kinder die Bienenart erkennen.
  // Die drei SVGs zeichnet die Grafik-Agentin (static/img/lese/bienenart-*.svg). name = Beschriftung, bild, alt = Bildbeschreibung.
  const ART_SPALTEN = [
    { name: "Königin", bild: "/static/img/lese/bienenart-koenigin.svg", alt: "Königin" },
    { name: "Arbeiterin", bild: "/static/img/lese/bienenart-arbeiterin.svg", alt: "Arbeiterin" },
    { name: "Drohne", bild: "/static/img/lese/bienenart-drohne.svg", alt: "Drohne" },
  ];

  // Zeilenbilder der Tabelle „Echt oder nur im Film?“ (Aufgabe 68): Standbilder aus dem Film (static/img/film/, 320 × 180). Sie zeigen nur,
  // was der Film zeigt (Spalte „Das siehst du im Film“), nie die Lösung der Spalte „So ist es in echt“. Jedes Bild ist angesehen und geprüft.
  // Für die Zeile „Vom Ei zur jungen Biene“ gibt es noch kein Standbild (Vorschlag: Kapitel 6, Kalender mit Querschnittskarte bei etwa 108 s).
  const STILL = {
    bienen: { bild: "/static/img/film/still-bienen.jpg", alt: "Film: Papierbienen am Flugloch" },
    koenigin: { bild: "/static/img/film/still-koenigin.jpg", alt: "Film: Königin mit Krone-Schild" },
    raehmchen: { bild: "/static/img/film/still-raehmchen.jpg", alt: "Film: Rähmchen mit Wabe im aufgeklappten Kasten" },
    eier: { bild: "/static/img/film/still-eier.jpg", alt: "Film: Wabe mit Eiern, Bild mit weißen Eiern oben rechts" },
  };

  // Bild „Der Bienenkasten von innen“ (Aufgabe 21). Koordinaten = Pixel in static/img/lese/stock-karte.svg (900 × 560),
  // im Browser auf dem Bild geprüft: Jeder Punkt liegt auf seinem Objekt (Flugloch = dunkle Öffnung, Brutraum = türkise Wand
  // des unteren Kastens, Honigraum = gelbe Wand des oberen Kastens, Rähmchen = Holzrahmen, Wabe = Wabe im Rähmchen, Dach, Boden),
  // keine zwei Punkte näher als 100 px, Rand ≥ 24. Die Reihenfolge ist wichtig: Niveau A nimmt die ersten 4 Punkte, B die ersten 6, C alle 7.
  // Die Wörter sind die der Sprecherin (Kapitel 2 und 3) und der Lesestrecke.
  INHALTE.bildpunkte.stock = {
    bild: "/static/img/lese/stock-karte.svg",
    breite: 900, hoehe: 560,
    punkte: [
      { id: "flugloch",  x: 168, y: 419, name: "Flugloch",  kat: 0, aliase: ["Einflugloch", "Eingang"] },
      { id: "brutraum",  x: 532, y: 362, name: "Brutraum",  kat: 0, aliase: ["Brutkammer", "Brutnest"] },
      { id: "honigraum", x: 532, y: 201, name: "Honigraum", kat: 0, aliase: ["Honigkammer", "Vorratsraum"] },
      { id: "wabe",      x: 743, y: 399, name: "Wabe",      kat: 0, aliase: ["Waben", "Honigwabe"] },
      { id: "raehmchen", x: 642, y: 404, name: "Rähmchen",  kat: 0, aliase: ["Rahmen", "Holzrähmchen", "Holzrahmen"] },
      { id: "dach",      x: 350, y: 76,  name: "Dach",      kat: 0, aliase: ["Kastendach", "Deckel"] },
      { id: "boden",     x: 417, y: 468, name: "Boden",     kat: 0, aliase: ["Kastenboden", "Bodenbrett"] },
    ],
  };

  // Tanzrätsel (Aufgabe 66): drei Karten tanzraetsel-1 … 3.svg (900 × 560), links die Wabe mit der Tänzerin, rechts die Wiese
  // mit Stock, Sonne und drei Blumenfeldern A, B, C. Trefferkreise = Mittelpunkte der Felder (werkzeuge/tanzraetsel_ziele.json,
  // an den Bildern geprüft). Richtig: Runde 1 → B (Lauf nach oben, mittellang), Runde 2 → C (Lauf waagerecht nach rechts),
  // Runde 3 → A (Lauf schräg nach rechts oben, sehr lang: weit weg; B liegt in derselben Richtung, aber nah).
  // rueck = Rückmeldungen für Niveau A und B (lenken auf das Merkmal); Niveau C bekommt nur „Schau noch einmal genau hin.“ –
  // die Kriterien stehen erst im Hinweis nach dem zweiten Fehler.
  const TANZ = {
    1: { ziele: [{ x: 486, y: 270, r: 60, ok: false }, { x: 650, y: 165, r: 60, ok: true }, { x: 776, y: 436, r: 60, ok: false }],
         rueck: ["Schau noch einmal: In welche Richtung läuft die Tänzerin?", null, "Schau noch einmal: In welche Richtung läuft die Tänzerin?"],
         hinweis: "Oben auf der Wabe heißt: in Richtung Sonne.",
         erklaerung: "Der Schwänzellauf zeigt nach oben. Das heißt: Das Futter liegt in Richtung Sonne." },
    2: { ziele: [{ x: 485, y: 300, r: 60, ok: false }, { x: 735, y: 153, r: 60, ok: false }, { x: 810, y: 300, r: 60, ok: true }],
         rueck: ["Achte auf links und rechts: Wohin läuft die Tänzerin auf der Wabe?",
                 "Der Schwänzellauf zeigt nicht schräg nach oben. Wie groß ist der Winkel zur Senkrechten?", null],
         hinweis: "Vergleiche den Winkel zur Senkrechten mit dem Winkel zur Sonne. Achte auf links und rechts.",
         erklaerung: "Der Schwänzellauf zeigt im rechten Winkel nach rechts. Das Futter liegt im gleichen Winkel rechts von der Sonne." },
    3: { ziele: [{ x: 735, y: 275, r: 60, ok: true }, { x: 601, y: 388, r: 60, ok: false }, { x: 794, y: 443, r: 60, ok: false }],
         rueck: [null, "Die Richtung passt. Aber wie lang ist der Schwänzellauf?", "Vergleiche noch einmal die Richtung."],
         hinweis: "Zwei Dinge zählen: die Richtung und die Länge des Schwänzellaufs.",
         erklaerung: "Der Schwänzellauf geht schräg nach rechts oben und ist lang. Das Futter liegt in dieser Richtung und weit weg." },
  };
  const NEUTRAL = "Schau noch einmal genau hin.";
  // neutral = true (Niveau C): erste falsche Rückmeldung neutral; hinweis: Standard aus TANZ, Niveau A und B bekommen bei Bedarf einen anderen
  // Hinweis als den Tipp in der Frage
  const tanzRunde = (n, frage, { hinweis, neutral } = {}) => ({
    bild: `/static/img/lese/tanzraetsel-${n}.svg`, breite: 900, hoehe: 560, frage,
    ziele: TANZ[n].ziele.map((z, i) => (z.ok ? { ...z } : { ...z, rueckmeldung: neutral ? NEUTRAL : TANZ[n].rueck[i] })),
    hinweis: hinweis || TANZ[n].hinweis, erklaerung: TANZ[n].erklaerung,
  });

  INHALTE.tabs.push({
    key: "volk", label: "Das Bienenvolk", icon: "🎭", kurz: "V", lese: "L3", leseNach: 66,
    film: "volk",       // die Bühne mit dem Film steht in diesem Reiter neben den Aufgaben
    intro: {
      eyebrow: "Lesestrecke 3", titel: "Wer lebt im Bienenstock?",
      begriffe: ["Bienenvolk", "Königin", "Arbeiterin", "Drohne", "Flugloch", "Brutraum", "Honigraum", "Rähmchen", "Wabe"],
    },
    aufgaben: [
      // ── 60 · Forscherfrage 1: Wer sagt den Bienen, was sie tun sollen? ────────────────────────────
      // Ausgewertet in Station 64. Jede Option lässt sich mit dem Film bestätigen oder widerlegen:
      // Königin (Kapitel 5: „Befehle gibt sie aber nicht“), Imker (kommt nur am Kasten, Kapitel 2, und bei der Ernte, Kapitel 10, vor),
      // jede Biene für sich (Kapitel 7: Aufgaben wechseln mit dem Alter; Kapitel 12: nur zusammen), zusammenarbeiten (Kapitel 7 und 12).
      // Es gibt kein Richtig/Falsch; die Optionen sind alle vernünftige Vermutungen.
      {
        nr: 60, typ: "vermutung", id: "v_chef", eyebrow: "Forscherfrage", titel: "Wer sagt den Bienen, was sie tun sollen?",
        frage: "Im Bienenstock gibt es viel zu tun. Was vermutest du?",
        niveaus: {
          A: { optionen: [
            "Die Königin sagt jeder Biene, was sie tun soll.",
            "Die Bienen arbeiten zusammen, und keine ist der Chef.",
            "Der Imker sagt den Bienen, was sie tun sollen.",
            "Jede Biene macht den ganzen Tag, was sie will.",
          ] },
          B: { optionen: [
            "Der Imker sagt den Bienen, was sie tun sollen.",
            "Die Königin sagt jeder Biene, was sie tun soll.",
            "Jede Biene macht den ganzen Tag, was sie will.",
            "Die Bienen arbeiten zusammen, und keine ist der Chef.",
          ], satzanfang: "Ich vermute, dass …", begruendung: ["weil …", "denn …"] },
          C: { satzanfang: "Ich vermute, dass …", frei: true, min: 30 },
        },
      },

      // ── 18 · Film ansehen (ganzer Film) ───────────────────────────────────────────────────────────
      // Die Beobachtungsaufträge sind abgestimmt auf: 1 → Beobachtungsbogen 62 (Eier, Kapitel 5), 2 → Vermutung 60 und Prüfung 64,
      // 3 → Tanzrätsel 66. Die Zahl der Bienen im Stock fragt dieser Reiter nicht (Reiter 1 hat die Frage und die Erklärung).
      {
        nr: 18, typ: "film", film: "volk", eyebrow: "Film · ganzer Film", titel: "Den Film ansehen",
        auftrag: "Sieh dir den Film „Ein Bienenvolk im Bienenstock“ ganz an. Er dauert 4 Minuten. Du bist Forscherin oder Forscher: Achte auf die drei Fragen und vergleiche mit deiner Vermutung.",
        beobachtung: [
          "Wer legt die Eier, und wie viele an einem Tag?",
          "Gibt die Königin den Bienen Befehle? Gibt noch jemand anderes Befehle?",
          "Was zeigt der Tanz der Sammlerin den anderen Bienen?",
        ],
      },

      // ── 62 · Beobachtungsbogen zum Film ───────────────────────────────────────────────────────────
      // Jede Zeile hat einen Knopf, der abspielt und auf den Satz der Sprecherin springt (Beschriftung neutral, damit sie keine Antwort verrät).
      // Kapitel 3: „Unten liegt der Brutraum … Oben liegt der Honigraum“ (47,9 s) · Kapitel 4: „drei Arten von Bienen“ (61,4 s) ·
      // Kapitel 5: „bis zu zweitausend Eier“ (85,0 s) · Kapitel 6: „Ammenbienen füttern sie“ (105,3 s), „Nach einundzwanzig Tagen schlüpft
      // eine junge Biene“ (111,9 s) · Kapitel 7: putzen, füttern, bauen und Wache halten, „Mit dem Alter wechselt also ihre Aufgabe“ (ab 121,4 s).
      {
        nr: 62, typ: "protokoll", eyebrow: "Forschen · Film Kapitel 3 bis 7", titel: "Beobachtungsbogen zum Film",
        auftrag: "Sieh dir den Film in Stücken an. Trage ein, was du siehst und hörst. Jede Zeile hat einen Knopf zur richtigen Stelle.",
        modell: kap(3, "Waben, Brutraum und Honigraum"),
        erkenntnis: "Die Königin legt bis zu etwa 2 000 Eier am Tag. Nach 21 Tagen schlüpft die junge Biene. Mit dem Alter wechselt die Aufgabe der Arbeiterin.",
        niveaus: {
          A: {
            zeilen: [
              { frage: "Was liegt im Bienenkasten oben, was unten?", kurz: "Räume oben und unten", art: "wahl",
                optionen: ["oben der Brutraum, unten der Honigraum", "oben der Honigraum, unten der Brutraum"], loesung: 1,
                hinweis: "Die Sprecherin zeigt beide Räume mit blauen Linien. Sieh genau hin.", modell: hoer(3, 47.9) },
              { frage: "Wie viele Arten von Bienen hat ein Bienenvolk?", kurz: "Arten von Bienen", art: "zahl", loesung: 3, einheit: "Arten",
                fehlertext: "Schreibe die Zahl mit Ziffern, z. B. 12.",
                hinweis: "Zähle, wer nacheinander ins Scheinwerferlicht tritt.", modell: hoer(4, 61.4) },
              { frage: "Wie viele Eier legt die Königin jeden Tag höchstens?", kurz: "Eier pro Tag", art: "wahl",
                optionen: ["etwa 20", "etwa 200", "bis zu etwa 2 000", "bis zu etwa 20 000"], loesung: 2,
                hinweis: "Hör genau auf die Zahl, die die Sprecherin nennt.", modell: hoer(5, 85.0) },
              { frage: "Nach wie vielen Tagen schlüpft aus dem Ei eine junge Biene?", kurz: "Tage bis zur jungen Biene", art: "zahl", loesung: 21, einheit: "Tage",
                fehlertext: "Schreibe die Zahl mit Ziffern, z. B. 12.",
                hinweis: "Hör auf die letzte Zahl im Satz der Sprecherin.", hinweis2: "Spiel Kapitel 6 noch einmal ab. Achte auf das Wort „Tagen“.",
                modell: hoer(6, 111.9) },
              { frage: "Was passiert mit der Arbeit einer Arbeiterin, wenn sie älter wird?", kurz: "Arbeit mit dem Alter", art: "wahl",
                optionen: ["sie bleibt gleich", "sie wechselt", "sie hört auf"], loesung: 1,
                hinweis: "Sieh dir an, was die junge Arbeiterin zuerst macht und was später.", modell: hoer(7, 121.4) },
            ],
            schluss: { anfang: "Ich habe beobachtet, dass …", bausteine: [
              "ein Bienenvolk drei Arten von Bienen hat.",
              { t: "ein Bienenvolk nur aus einer einzigen Biene besteht.", ok: false, rueckmeldung: "Das hast du nicht beobachtet. Lies noch einmal, was in deinen Zeilen steht." },
              "die Königin jeden Tag viele Eier legt.",
              "aus dem Ei nach 21 Tagen eine junge Biene wird.",
              "die Arbeit einer Arbeiterin mit dem Alter wechselt.",
            ] },
          },
          B: {
            zeilen: [
              { frage: "Was liegt im Bienenkasten oben, was unten?", kurz: "Räume oben und unten", art: "wahl",
                optionen: ["oben der Honigraum, unten der Brutraum", "oben der Brutraum, unten der Honigraum", "beide Räume liegen nebeneinander"], loesung: 0,
                hinweis: "Die Sprecherin zeigt beide Räume mit blauen Linien. Sieh genau hin.", modell: hoer(3, 47.9) },
              { frage: "Wie viele Arten von Bienen hat ein Bienenvolk?", kurz: "Arten von Bienen", art: "zahl", loesung: 3, einheit: "Arten",
                fehlertext: "Schreibe die Zahl mit Ziffern, z. B. 12.",
                hinweis: "Zähle, wer nacheinander ins Scheinwerferlicht tritt.", modell: hoer(4, 61.4) },
              { frage: "Wie viele Eier legt die Königin jeden Tag höchstens?", kurz: "Eier pro Tag", art: "wahl",
                optionen: ["etwa 20", "bis zu etwa 2 000", "etwa 200", "bis zu etwa 20 000"], loesung: 1,
                hinweis: "Hör genau auf die Zahl, die die Sprecherin nennt.", modell: hoer(5, 85.0) },
              { frage: "Wer füttert die Larve in der Zelle?", kurz: "füttert die Larve", art: "wahl", optionen: ["die Drohnen", "die Wächterinnen", "die Ammenbienen"], loesung: 2,
                hinweis: "Hör auf den Satz nach „Larve“.", modell: hoer(6, 105.3) },
              { frage: "Nach wie vielen Tagen schlüpft aus dem Ei eine junge Biene?", kurz: "Tage bis zur jungen Biene", art: "zahl", loesung: 21, einheit: "Tage",
                fehlertext: "Schreibe die Zahl mit Ziffern, z. B. 12.",
                hinweis: "Hör auf die letzte Zahl im Satz der Sprecherin.", hinweis2: "Spiel Kapitel 6 noch einmal ab. Achte auf das Wort „Tagen“.",
                modell: hoer(6, 111.9) },
              { frage: "Was passiert mit der Arbeit einer Arbeiterin, wenn sie älter wird?", kurz: "Arbeit mit dem Alter", art: "wahl",
                optionen: ["sie hört auf", "sie bleibt gleich", "sie wechselt"], loesung: 2,
                hinweis: "Sieh dir an, was die junge Arbeiterin zuerst macht und was später.", modell: hoer(7, 121.4) },
            ],
            schluss: { anfang: "Ich habe beobachtet, dass …", min: 30 },
          },
          C: {
            zeilen: [
              { frage: "Welche ZWEI Räume hat der Bienenkasten? Wähle zwei.", kurz: "Räume im Bienenkasten", art: "mehrfach",
                optionen: ["Brutraum", "Schlafraum", "Honigraum", "Futterraum"], loesung: [0, 2],
                hinweis: "Die Sprecherin nennt zwei Räume und sagt, wofür sie da sind.", modell: hoer(3, 47.9) },
              { frage: "Wie viele Eier legt die Königin jeden Tag höchstens?", kurz: "Eier pro Tag", art: "wahl",
                optionen: ["bis zu etwa 20 000", "etwa 20", "etwa 200", "bis zu etwa 2 000"], loesung: 3,
                hinweis: "Hör genau auf die Zahl, die die Sprecherin nennt.", modell: hoer(5, 85.0) },
              { frage: "Wer füttert die Larve in der Zelle?", kurz: "füttert die Larve", art: "wahl", optionen: ["die Ammenbienen", "die Drohnen", "die Wächterinnen"], loesung: 0,
                hinweis: "Hör auf den Satz nach „Larve“.", modell: hoer(6, 105.3) },
              { frage: "Nach wie vielen Tagen schlüpft aus dem Ei eine junge Biene?", kurz: "Tage bis zur jungen Biene", art: "zahl", loesung: 21, einheit: "Tage",
                fehlertext: "Schreibe die Zahl mit Ziffern, z. B. 12.",
                hinweis: "Hör auf die letzte Zahl im Satz der Sprecherin.", hinweis2: "Spiel Kapitel 6 noch einmal ab. Achte auf das Wort „Tagen“.",
                modell: hoer(6, 111.9) },
              { frage: "Was passiert mit der Arbeit einer Arbeiterin, wenn sie älter wird?", kurz: "Arbeit mit dem Alter", art: "wahl",
                optionen: ["sie wechselt", "sie hört auf", "sie bleibt gleich"], loesung: 0,
                hinweis: "Sieh dir an, was die junge Arbeiterin zuerst macht und was später.", modell: hoer(7, 121.4) },
              { frage: "Schreibe einen Satz: Was sagt die Sprecherin über die Königin?", kurz: "Satz über die Königin", art: "text", satzanfang: "Die Königin …", min: 20,
                modell: hoer(5, 81.4) },
            ],
            schluss: { anfang: "Ich habe beobachtet, dass …", frei: true, min: 40 },
          },
        },
      },

      // ── 63 · Vergleichstabelle: Königin, Arbeiterin, Drohne (Film Kapitel 4 und 5) ───────────────
      // Nur Merkmale, die der Film in Kapitel 4 und 5 zeigt oder sagt (und die Zeile zur Arbeit aus Kapitel 7, die Station 62 vorher abgefragt hat).
      // Stachel und Lebensdauer kommen erst in der Lesestrecke. Körper und Augen zeigt das Bild (Scheinwerfer auf Königin, Arbeiterin, Drohnen),
      // Aufgabe und Zahlen sagt die Sprecherin.
      {
        nr: 63, typ: "tabelle", eyebrow: "Vergleichen · Film Kapitel 4 und 5", titel: "Königin, Arbeiterin und Drohne im Vergleich",
        auftrag: "Vergleiche die drei Arten von Bienen. Sieh dir Kapitel 4 und 5 im Film an. Wähle für jedes Feld das passende Wort.",
        modell: [satz(4, 61.4, "Hör zu: die drei Arten"), satz(5, 81.4, "Hör zu: die Königin")],
        erkenntnis: "Die Königin legt die Eier. Es gibt nur eine Königin, viele tausend Arbeiterinnen und einige hundert Drohnen. Die Drohnen paaren sich mit jungen Königinnen.",
        niveaus: {
          A: { spalten: ART_SPALTEN, zeilen: [
            { merkmal: "Körper", optionen: ["klein", "groß, langer Hinterleib", "dick"], loesung: [1, 0, 2], hinweis: "Achte auf den Hinterleib und die Größe." },
            { merkmal: "Aufgabe", optionen: ["legt die Eier", "macht viele Arbeiten (putzen, bauen, sammeln)", "paart sich mit jungen Königinnen"], loesung: [0, 1, 2],
              hinweis: "Hör auf die Sprecherin. Das Werkzeug-Schild zeigt die Arbeit." },
            { merkmal: "Wie viele im Volk?", optionen: ["eine", "einige hundert", "viele tausend"], loesung: [0, 2, 1], hinweis: "Hör auf die Zahlwörter im ersten Satz." },
          ] },
          B: { spalten: ART_SPALTEN, zeilen: [
            { merkmal: "Körper", optionen: ["klein", "groß, langer Hinterleib", "dick"], loesung: [1, 0, 2], hinweis: "Achte auf den Hinterleib und die Größe." },
            { merkmal: "Augen", optionen: ["normal groß", "riesig"], loesung: [0, 0, 1], hinweis: "Sieh dir die Köpfe im Scheinwerferlicht an." },
            { merkmal: "Aufgabe", optionen: ["paart sich mit jungen Königinnen", "legt die Eier", "macht viele Arbeiten (putzen, bauen, sammeln)"], loesung: [1, 2, 0],
              hinweis: "Hör auf die Sprecherin. Das Werkzeug-Schild zeigt die Arbeit." },
            { merkmal: "Wie viele im Volk?", optionen: ["viele tausend", "einige hundert", "eine"], loesung: [2, 0, 1], hinweis: "Hör auf die Zahlwörter im ersten Satz." },
          ] },
          C: { spalten: ART_SPALTEN, zeilen: [
            { merkmal: "Körper", optionen: ["dick", "klein", "groß, langer Hinterleib"], loesung: [2, 1, 0], hinweis: "Achte auf den Hinterleib und die Größe." },
            { merkmal: "Augen", optionen: ["riesig", "normal groß"], loesung: [1, 1, 0], hinweis: "Sieh dir die Köpfe im Scheinwerferlicht an." },
            { merkmal: "Aufgabe", optionen: ["macht viele Arbeiten (putzen, bauen, sammeln)", "paart sich mit jungen Königinnen", "legt die Eier"], loesung: [2, 0, 1],
              hinweis: "Hör auf die Sprecherin. Das Werkzeug-Schild zeigt die Arbeit." },
            { merkmal: "Wie viele im Volk?", optionen: ["einige hundert", "eine", "viele tausend"], loesung: [1, 2, 0], hinweis: "Hör auf die Zahlwörter im ersten Satz." },
            { merkmal: "Mutter aller Bienen im Stock?", optionen: ["nein", "ja"], loesung: [1, 0, 0], hinweis: "Hör auf den ersten Satz in Kapitel 5." },
          ] },
        },
      },

      // ── 64 · Vermutung prüfen: Wer sagt den Bienen, was sie tun sollen? (Film Kapitel 5, 7 und 12) ──
      // Neu nach dem Audit: Alle Optionen sind gleich gebaute, prüfbare Einzelaussagen (die richtige ist weder die längste noch die kürzeste),
      // die falschen sind die Vermutungen aus Station 60, die der Film widerlegt. Die Quelle ist neutral, drei Knöpfe spielen die Belegstellen ab:
      // Kapitel 5 (ab 85,0 s: Eier, „Befehle gibt sie aber nicht“ 90,4 s), Kapitel 7 (ab 121,4 s: putzen, füttern, bauen; „Mit dem Alter wechselt
      // also ihre Aufgabe“ 131,7 s), Kapitel 12 (ab 221,6 s: „Ein Bienenvolk arbeitet zusammen wie ein einziger Körper“). Der Imker kommt nur am
      // Kasten (Kapitel 2) und bei der Ernte (Kapitel 10) vor – das steht im Hinweis für B und C.
      {
        nr: 64, typ: "pruefen", vermutung: "v_chef", eyebrow: "Vermutung prüfen · Film Kapitel 5, 7 und 12", titel: "Stimmte deine Vermutung?",
        quelle: "Schau dir Kapitel 5, 7 und 12 im Film an.",
        modell: [satz(5, 85.0, "Hör zu: die Königin"), satz(7, 121.4, "Hör zu: die Arbeiterinnen"), satz(12, 221.6, "Hör zu: das ganze Volk")],
        erkenntnis: "Niemand befiehlt. Die Königin legt Eier, die Arbeiterinnen wechseln mit dem Alter ihre Aufgabe, und das Volk arbeitet zusammen.",
        niveaus: {
          A: { erkenntnis: { frage: "Was hast du im Film gesehen und gehört?", fehltext: "Das passt noch nicht zu dem, was du im Film gesehen und gehört hast.", optionen: [
            { t: "Die Königin sagt jeder Biene, was sie tun soll.", ok: false },
            { t: "Jede Biene macht den ganzen Tag, was sie will.", ok: false },
            { t: "Niemand befiehlt, alle arbeiten zusammen.", ok: true },
          ], hinweis: "Achte darauf, was die Sprecherin über die Königin sagt." } },
          B: { erkenntnis: { frage: "Was hast du im Film gesehen und gehört?", fehltext: "Das passt noch nicht zu dem, was du im Film gesehen und gehört hast.", optionen: [
            { t: "Der Imker sagt den Bienen, was sie tun sollen.", ok: false },
            { t: "Die Königin sagt jeder Biene, was sie tun soll.", ok: false },
            { t: "Jede Biene macht den ganzen Tag, was sie will.", ok: false },
            { t: "Niemand befiehlt, das Volk arbeitet zusammen.", ok: true },
          ], hinweis: "Prüfe jede Aussage einzeln: Kannst du sie im Film sehen oder hören? Wann kommt der Imker im Film vor?" },
            beleg: { frage: "Woran erkennst du das im Film?", optionen: [
              { t: "Die Sprecherin sagt: Der Imker teilt die Arbeit ein.", ok: false },
              { t: "Die Sprecherin sagt: Befehle gibt sie aber nicht.", ok: true },
              { t: "Im Film zeigt die Königin auf die Arbeiterinnen.", ok: false },
            ], hinweis: "Überlege: Welche Aussage kannst du im Film wirklich hören oder sehen?" } },
          C: { erkenntnis: { frage: "Was hast du im Film gesehen und gehört?", fehltext: "Das passt noch nicht zu dem, was du im Film gesehen und gehört hast.", optionen: [
            { t: "Die Königin teilt die Arbeit ein und kontrolliert alle.", ok: false },
            { t: "Der Imker teilt die Arbeit der Bienen im Stock ein.", ok: false },
            { t: "Jede Biene tut ihr ganzes Leben lang dieselbe Arbeit.", ok: false },
            { t: "Niemand befiehlt: Die Aufgaben wechseln mit dem Alter.", ok: true },
          ], hinweis: "Prüfe jede Aussage einzeln. Der Imker kommt im Film nur bei zwei Gelegenheiten vor (Kapitel 2 und 10). Was zeigt Kapitel 7?" },
            satz: { anfang: "Ich habe herausgefunden, dass … Meine Vermutung war …", min: 60 } },
        },
      },

      // ── 21 · Den Bienenkasten beschriften (Kapitel 2 und 3) ───────────────────────────────────────
      // Wörter wie die Sprecherin: Flugloch (Kapitel 2, 25,5 s), Waben, Rähmchen, Brutraum, Honigraum (Kapitel 3, ab 42,0 s); Dach und Boden kennt
      // jedes Kind vom Bild (Niveau C schreibt sie selbst, die Lesestrecke bestätigt sie). A: 4 Wörter aus der Wortkiste, B: 6 mit Ablenkern,
      // C: alle 7 selbst eintippen. Anwenden (Wortschatz am Bild), nicht Forschen.
      {
        nr: 21, typ: "bildpunkte", karte: "stock", eyebrow: "Anwenden · Film Kapitel 2 und 3", titel: "Den Bienenkasten beschriften",
        modell: [satz(2, 25.5, "Hör zu: das Flugloch"), satz(3, 42.0, "Sieh dir an: der Kasten von innen")],
        niveaus: {
          A: { modus: "benennen", anzahl: 4, ablenker: ["Schleier"],
               hilfe: "Schau dir die Nummern noch einmal genau an. Im Film, Kapitel 2 und 3, siehst du die Teile." },
          B: { modus: "benennen", anzahl: 6, ablenker: ["Schleier", "Blüte"],
               hilfe: "Brutraum und Honigraum haben verschiedene Aufgaben. Sieh dir Kapitel 3 im Film an." },
          C: { modus: "benennen", anzahl: 7, eingabe: "text",
               hilfe: "Schreibe die Wörter so, wie die Sprecherin sie sagt. Kapitel 2 und 3 im Film helfen dir." },
        },
      },

      // ── 66 · Tanzrätsel: Wo ist das Futter? (Film Kapitel 9, Pflicht-Knopf) ───────────────────────
      // Der Film sagt: „Die Richtung des Tanzes zeigt den Weg. Die Dauer des Schwänzelns zeigt, wie weit es ist.“ Das Bild im Film
      // zeigt Senkrechte, Richtung und Winkel zur Sonne. Die Kinder entdecken Richtung und Länge an drei Karten.
      // A: Regel steht in der Frage, 3 Runden (Länge kommt in Runde 3 vor) · B: Regel nur als Tipp, 3 Runden · C: keine Regel, 3 Runden,
      // schwerste Karte zuerst, erste falsche Rückmeldung neutral. Der Pflicht-Knopf spielt den Tanz ab (ab 163,5 s).
      {
        nr: 66, typ: "bildwahl", eyebrow: "Tanzrätsel · Film Kapitel 9", titel: "Wo ist das Futter?",
        modell: { ...satz(9, 163.5, "Sieh dir den Tanz an", 0), pflicht: true },
        erkenntnis: "Der Schwänzellauf zeigt den Weg: Sein Winkel zur Senkrechten ist der Winkel zwischen Futter und Sonne. Ein langer Schwänzellauf heißt: Das Futter ist weit weg.",
        niveaus: {
          A: { runden: [
            tanzRunde(1, "Die Tänzerin läuft auf der Wabe nach oben. Oben heißt: in Richtung Sonne. Tippe auf die Wiese mit dem Futter.",
              { hinweis: "Auf der Wiese geht eine gestrichelte Linie vom Stock zur Sonne. Welche Wiese liegt an dieser Linie?" }),
            tanzRunde(2, "Jetzt läuft die Tänzerin waagerecht nach rechts. Der Winkel zur Senkrechten ist so groß wie der Winkel zur Sonne. Tippe auf die Wiese mit dem Futter.",
              { hinweis: "Das ist ein rechter Winkel. Liegt die Wiese vom Stock aus gesehen links oder rechts der Linie zur Sonne?" }),
            tanzRunde(3, "Jetzt läuft die Tänzerin schräg nach rechts oben. Der Schwänzellauf ist sehr lang. Ein langer Schwänzellauf heißt: Das Futter ist weit weg. Tippe auf die Wiese.",
              { hinweis: "Zwei Wiesen liegen in dieser Richtung. Eine ist nah, eine ist weit weg." }),
          ] },
          B: { runden: [
            tanzRunde(1, "Wo liegt das Futter? Tipp: Auf der Wabe heißt „oben“: in Richtung Sonne.",
              { hinweis: "Auf der Wiese geht eine gestrichelte Linie vom Stock zur Sonne. Welche Wiese liegt an dieser Linie?" }),
            tanzRunde(2, "Wo liegt das Futter jetzt? Vergleiche den Winkel zur Senkrechten mit dem Winkel zur Sonne."),
            tanzRunde(3, "Wo liegt das Futter? Achte auf die Richtung und auf die Länge des Schwänzellaufs."),
          ] },
          C: { runden: [
            tanzRunde(3, "Wo liegt das Futter? Sieh dir Kapitel 9 im Film an, wenn du unsicher bist.", { neutral: true }),
            tanzRunde(2, "Wo liegt das Futter jetzt?", { neutral: true }),
            tanzRunde(1, "Wo liegt das Futter? Ich erkenne es an …", { neutral: true }),
          ] },
        },
      },

      // ── 68 · Filmkritik: Echt oder nur im Film? (Modellgrenzen offenlegen, film.md §2) ────────────────
      // Steht NACH der Lesestrecke: Die Spalte „So ist es in echt“ ist im AB belegt – roter Punkt, mehr Rähmchen und 21 Tage in der
      // Lesestrecke, Länge der Biene (etwa 12 bis 14 mm) in Reiter 2 und im Glossar (Arbeiterin), „bis zu zweitausend Eier“ sagt die Sprecherin.
      // Entfallen sind die Zeilen Honigernte (Schleuder steht erst in Reiter 4) und Nektar zu Honig (Reiter 4).
      // Quelle der Vereinfachungen: papiertheater/docs/ab_uebergabe.md („Vereinfachungen“). Je Zeile: Spalte 1 = was der Film zeigt,
      // Spalte 2 = echt. Die dritte Option ist in beiden Spalten falsch. Zeilenbilder sind Film-Standbilder; sie zeigen nur, was der Film zeigt.
      {
        nr: 68, typ: "tabelle", eyebrow: "Filmkritik · Film Kapitel 2 bis 6", titel: "Echt oder nur im Film?",
        auftrag: "Der Film zeigt vieles einfacher als die Wirklichkeit. Sieh dir die Stellen im Film an und lies noch einmal in der Lesestrecke nach. Wähle in jeder Zeile: Was siehst du im Film? Was ist in echt so?",
        erkenntnis: "Der Film ist stark vereinfacht: Die Bienen sind aus Papier und viel zu groß. Zahlen und Zeiten sind verkürzt. Den roten Punkt der Königin malen Imker manchmal auf.",
        niveaus: {
          A: { spalten: ["Das siehst du im Film", "So ist es in echt"], zeilen: [
            { merkmal: "Die Bienen", ...STILL.bienen, optionen: ["Papierfiguren, viel größer als in echt", "echte Tiere, etwa 12 bis 14 mm lang", "Papierfiguren, genau so groß wie echt"], loesung: [0, 1],
              hinweis: "Sieh dir die Bienen im Film genau an. Lies nach, wie lang eine Arbeiterin wirklich ist.", modell: kapZeile(2) },
            { merkmal: "Die Königin", ...STILL.koenigin, optionen: ["kein Punkt, Imker malen ihn manchmal auf", "blauer Streifen auf dem Hinterleib", "roter Punkt auf dem Rücken"], loesung: [2, 0],
              hinweis: "Achte im Film auf den Rücken der Königin. Lies in der Lesestrecke nach, wer den Punkt aufmalt.", modell: kapZeile(4) },
            { merkmal: "Die Rähmchen im Kasten", ...STILL.raehmchen, optionen: ["gar keine Rähmchen", "nur wenige Rähmchen", "mehr Rähmchen im Kasten"], loesung: [1, 2],
              hinweis: "Sieh dir im Film an, wie viele Rähmchen im Kasten hängen. Lies nach, wie es im echten Kasten ist.", modell: kapZeile(3) },
          ] },
          B: { spalten: ["Das siehst du im Film", "So ist es in echt"], zeilen: [
            { merkmal: "Die Bienen", ...STILL.bienen, optionen: ["echte Tiere, etwa 12 bis 14 mm lang", "Papierfiguren, genau so groß wie echt", "Papierfiguren, viel größer als in echt"], loesung: [2, 0],
              hinweis: "Sieh dir die Bienen im Film genau an. Lies nach, wie lang eine Arbeiterin wirklich ist.", modell: kapZeile(2) },
            { merkmal: "Die Königin", ...STILL.koenigin, optionen: ["roter Punkt auf dem Rücken", "blauer Streifen auf dem Hinterleib", "kein Punkt, Imker malen ihn manchmal auf"], loesung: [0, 2],
              hinweis: "Achte im Film auf den Rücken der Königin. Lies in der Lesestrecke nach, wer den Punkt aufmalt.", modell: kapZeile(4) },
            { merkmal: "Die Eier der Königin", ...STILL.eier, optionen: ["bis zu etwa 2 000 Eier am Tag", "nur 40 Eier am Tag", "40 Eier im Bild oben rechts"], loesung: [2, 0],
              hinweis: "Sieh dir das Bild mit den weißen Eiern oben rechts an. Hör, welche Zahl die Sprecherin nennt.", modell: kapZeile(5) },
            { merkmal: "Vom Ei zur jungen Biene", optionen: ["21 Tage", "nur 3 Tage", "nur wenige Sekunden"], loesung: [2, 0],
              hinweis: "Sieh dir an, wie schnell der Film die Entwicklung zeigt. Lies nach, wie lange sie wirklich dauert.", modell: kapZeile(6) },
          ] },
          C: { spalten: ["Das siehst du im Film", "So ist es in echt"], zeilen: [
            { merkmal: "Die Bienen", ...STILL.bienen, optionen: ["Papierfiguren, genau so groß wie echt", "Papierfiguren, viel größer als in echt", "echte Tiere, etwa 12 bis 14 mm lang"], loesung: [1, 2],
              hinweis: "Sieh dir die Bienen im Film genau an. Lies nach, wie lang eine Arbeiterin wirklich ist.", modell: kapZeile(2) },
            { merkmal: "Die Königin", ...STILL.koenigin, optionen: ["kein Punkt, Imker malen ihn manchmal auf", "roter Punkt auf dem Rücken", "blauer Streifen auf dem Hinterleib"], loesung: [1, 0],
              hinweis: "Achte im Film auf den Rücken der Königin. Lies in der Lesestrecke nach, wer den Punkt aufmalt.", modell: kapZeile(4) },
            { merkmal: "Die Rähmchen im Kasten", ...STILL.raehmchen, optionen: ["mehr Rähmchen im Kasten", "gar keine Rähmchen", "nur wenige Rähmchen"], loesung: [2, 0],
              hinweis: "Sieh dir im Film an, wie viele Rähmchen im Kasten hängen. Lies nach, wie es im echten Kasten ist.", modell: kapZeile(3) },
            { merkmal: "Die Eier der Königin", ...STILL.eier, optionen: ["40 Eier im Bild oben rechts", "nur 40 Eier am Tag", "bis zu etwa 2 000 Eier am Tag"], loesung: [0, 2],
              hinweis: "Sieh dir das Bild mit den weißen Eiern oben rechts an. Hör, welche Zahl die Sprecherin nennt.", modell: kapZeile(5) },
            { merkmal: "Vom Ei zur jungen Biene", optionen: ["nur 3 Tage", "nur wenige Sekunden", "21 Tage"], loesung: [1, 2],
              hinweis: "Sieh dir an, wie schnell der Film die Entwicklung zeigt. Lies nach, wie lange sie wirklich dauert.", modell: kapZeile(6) },
          ] },
        },
      },

      // ── 65 · Sprachwerkstatt: Zeitfolge (Film Kapitel 6 bis 8, Lesestrecke nur für Tage) ──────────
      // Sprachziel: zuerst, dann, danach, später, schließlich. Der Film sagt: Larve „nach drei Tagen“, Ammenbienen füttern, Zelle verdeckelt,
      // Puppe, „einundzwanzig Tage“ (Kapitel 6); putzen „zuerst“, dann füttern, „später“ bauen und Wache halten (Kapitel 7); die ältesten
      // Arbeiterinnen fliegen aus (Kapitel 8). C folgt dem Filmtext von Kapitel 7.
      {
        nr: 65, typ: "sortierung", eyebrow: "Sprachwerkstatt · Zeitfolge · Film Kapitel 6 bis 8", titel: "Zuerst, dann, danach, schließlich",
        modell: [satz(6, 101.6, "Hör zu: vom Ei zur Biene"), satz(7, 121.4, "Hör zu: die Arbeiterinnen"), satz(8, 142.0, "Hör zu: die Sammlerinnen")],
        niveaus: {
          A: { hinweis: "Ordne vom Ei bis zur jungen Biene. Achte auf die kleinen Wörter: zuerst, dann, danach, schließlich.",
               hilfe: "Sieh dir Kapitel 6 im Film noch einmal an. Was passiert zuerst, was danach?", items: [
            "Zuerst legt die Königin ein Ei in die Zelle.",
            "Dann schlüpft aus dem Ei eine Larve.",
            "Danach verwandelt sich die Larve zur Puppe.",
            "Schließlich schlüpft die junge Biene.",
          ] },
          B: { hinweis: "Ordne, was in der Zelle passiert. Achte auf die kleinen Wörter, die die Zeit zeigen.",
               hilfe: "Sieh dir Kapitel 6 im Film noch einmal an. Achte auf die Zahlen und auf das Wort „dann“.", items: [
            "Zuerst legt die Königin ein Ei in eine Zelle.",
            "Nach 3 Tagen schlüpft aus dem Ei eine Larve.",
            "Dann füttern Ammenbienen die Larve.",
            "Danach verdeckeln die Bienen die Zelle mit Wachs.",
            "Als Puppe verwandelt sich die Larve in eine Biene.",
            "Schließlich schlüpft nach 21 Tagen die junge Biene.",
          ] },
          C: { hinweis: "Ordne ein ganzes Arbeiterinnen-Leben: vom Ei bis zur Sammlerin. Die Zeitwörter helfen dir.",
               hilfe: "Sieh dir Kapitel 6 und 7 im Film noch einmal an. Was macht die junge Biene zuerst, was später?", items: [
            "Zuerst legt die Königin ein Ei in eine Zelle.",
            "Nach 3 Tagen schlüpft aus dem Ei eine Larve.",
            "Dann verdeckeln die Bienen die Zelle mit Wachs.",
            "Nach 21 Tagen schlüpft die junge Biene.",
            "Die junge Biene putzt zuerst die Zellen.",
            "Dann füttert sie als Ammenbiene die Larven.",
            "Später baut sie Waben und hält Wache.",
            "Schließlich fliegt sie als Sammlerin aus.",
          ] },
        },
      },

      // ── 67 · Sprachwerkstatt: je … desto, weil, damit (Film Kapitel 9 und 12) ──────────────────────
      // Sprachziel: Vergleichssätze mit „je … desto“ (länger – weiter, kürzer – näher) und Begründungen mit weil / damit / deshalb.
      // Inhalt aus dem Film: „Die Dauer des Schwänzelns zeigt, wie weit es ist“; „Hat eine Sammlerin eine gute Wiese gefunden, tanzt sie im Stock“;
      // „Keine Biene schafft es allein.“ „deshalb“ gilt auch als „darum“ und „daher“.
      {
        nr: 67, typ: "luecke", eyebrow: "Sprachwerkstatt · je … desto und weil · Film Kapitel 9", titel: "Je länger, desto weiter",
        modell: satz(9, 167.0, "Sieh dir den Tanz an"),
        niveaus: {
          A: { modus: "chips", ablenker: ["schneller", "dunkler"],
               hilfe: "Sieh dir Kapitel 9 im Film noch einmal an: Was zeigt die Dauer des Schwänzelns?",
               text: "Je [länger] die Tänzerin schwänzelt, desto [weiter] ist die Wiese entfernt. Je [kürzer] sie schwänzelt, desto [näher] liegt die Wiese." },
          B: { modus: "input",
               hilfe: "Sieh dir Kapitel 9 im Film noch einmal an: Was zeigt die Dauer des Schwänzelns? Warum fliegen die anderen Bienen los?",
               text: "Je [länger] das Schwänzeln dauert, desto [weiter] ist das Futter entfernt. Je [kürzer] es dauert, desto [näher] liegt das Futter. Die anderen Bienen fliegen los, [weil] die Sammlerin eine gute Wiese gefunden hat." },
          C: { modus: "input",
               hilfe: "Überlege bei jeder Lücke: Passt das Wort zum Sinn des Satzes? Kapitel 9 und 12 im Film helfen dir.",
               text: "[Je] kürzer das Schwänzeln dauert, [desto] näher liegt die Wiese. Die Tänzerin tanzt, [damit] die anderen Bienen die Wiese finden. Die anderen Bienen fliegen los, [weil] die Sammlerin eine gute Wiese gefunden hat. Keine Biene schafft es allein, [deshalb|darum|daher] arbeitet das Volk zusammen." },
        },
      },

      // ── 26 · Zeichnung 2: Der Schwänzeltanz (Anwenden, Film Kapitel 9) ────────────────────────────
      // Prüfliste für die KI-Bewertung: zeichenauftraege.py, Eintrag „schwaenzeltanz“.
      {
        nr: 26, typ: "zeichnen", eyebrow: "Zeichnen · Film Kapitel 9", titel: "Der Schwänzeltanz", geraet: "schwaenzeltanz",
        modell: satz(9, 163.5, "Sieh dir den Tanz an", 0),
        niveaus: {
          A: { aufgabe: "Zeichne eine senkrechte Wabe mit einer tanzenden Biene. Zeichne die Sonne daneben. Zeichne eine Linie, die zeigt, in welche Richtung die Biene läuft.",
               elemente: ["senkrechte Wabe", "tanzende Biene (Tänzerin)", "Sonne", "Richtungslinie"],
               hinweis: "Tipp: Die Wabe steht aufrecht wie eine Wand. Die Richtungslinie ist ein Pfeil auf der Wabe." },
          B: { aufgabe: "Zeichne die senkrechte Wabe mit der Tänzerin, der Sonne und der Richtungslinie. Zeichne auch den Schwänzellauf ein, bei dem die Biene wackelt.",
               elemente: ["senkrechte Wabe", "Tänzerin mit Schwänzellauf", "Sonne", "Richtungslinie", "senkrechte Hilfslinie"],
               hinweis: "Tipp: Zeichne zuerst eine gerade Linie nach oben. Die Richtungslinie läuft schräg dazu." },
          C: { aufgabe: "Zeichne den Schwänzeltanz: senkrechte Wabe, Tänzerin mit Schwänzellauf, Sonne und Richtungslinie mit Winkel. Beschrifte, was die Richtung und was die Dauer des Schwänzelns zeigen.",
               elemente: ["senkrechte Wabe", "Tänzerin mit Schwänzellauf", "Sonne", "Richtungslinie mit Winkel zur Senkrechten", "Beschriftung: Richtung zeigt den Weg, Dauer zeigt die Entfernung"],
               hinweis: "Tipp: Der Winkel liegt zwischen der Senkrechten und der Richtungslinie. Er ist so groß wie der Winkel zwischen Flugrichtung und Sonne." },
        },
      },
    ],
  });
})();
