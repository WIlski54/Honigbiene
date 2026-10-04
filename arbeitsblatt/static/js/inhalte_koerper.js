// Reiter 2 „Die Biene“ – forschend-entwickelnd (Plan und Dramaturgie: plan_koerper.py; Lesestrecke L2: lesen_koerper.py)
// Das 3D-Modell ist das Forschungsinstrument: Die Kinder vermuten (50, 53), erkunden (8), zählen und prüfen (51, 52), tippen Teile
// an (9), suchen die Organe im Situs (54) und prüfen ihre zweite Vermutung am Film und am Modell (55).
// Erst danach kommt die Lesestrecke (leseNach: 55), dann die Sprachwerkstatt (56, 57) und die Zeichnung (15).
// Regeln (Audit 4.10.2026, docs/AUDIT_FORSCHEN_2026-10-04.md):
//  • Jeder Knopf stellt genau die Ansicht ein, aus der die Antwort folgt – ohne sie zu verraten (neutrale Beschriftung).
//  • `pruefen`: alle Optionen gleich gebaut und ähnlich lang (die richtige ist nicht die längste), Ablenker sind plausible Vermutungen,
//    die Modell oder Film widerlegen; jede Prüfung hat `erkenntnis.hinweis`, eine neutrale `quelle` und Knöpfe zur Evidenz.
//  • Was ein späterer Abschnitt erforschen soll (Lage der Organe in 54, Nektar und Pollen in 55), steht vorher nirgends als Hinweis.
//  • Das Modell ist ein Prototyp (Farben didaktisch, Lage nachgebaut): Fragen nur dazu, was man darin sieht. Zahlen nur aus AB_KONZEPT.md.
// Technik:
//  • Modell-Befehle: „zurueck“ steht vor jedem Knopf (löscht Hervorhebung, Schilder, Fokus). „fokus“ fährt ohne Markierung heran,
//    „hervorheben“ (ohne fokus) markiert; so ist die Blickrichtung unabhängig davon, wo die Kamera vorher stand.
//  • Film-Knöpfe springen auf Sekunden (springe) und spielen sofort (film.js hängt „spielen“ an). Zeiten: papiertheater/docs/ab_uebergabe.md.
//  • Rüssel und Stachel sind winzig: Ziele in Aufgabe 9 haben ein Feld `fokus` (Kamerafahrt ohne Markierung).
//  • Die Reihenfolge der Aufgaben in diesem Array ist die Reihenfolge in plan_koerper.py (ohne Lesestrecke).
(() => {
  "use strict";

  const MODELL = "biene3d";
  const ZURUECK = { mw: "zurueck" };
  // Ein Knopf, der das Modell einstellt: Text + Befehle (Protokoll: AB_KONZEPT.md); `extra` z. B. { pflicht: true }
  const knopf = (text, befehle, extra) => Object.assign({ film: MODELL, text, befehle }, extra || {});
  // Außenansicht, Blick von einer Seite, Teile hervorgehoben (alle anderen blass); fokus = Kamera fährt an die Teile heran
  const aussen = (text, teile, blickName = "seite", fokus = true, abstand, extra) => knopf(text, [
    ZURUECK, { mw: "ansicht", name: "gestalt" }, { mw: "hervorheben", teile, fokus: false },
    fokus ? Object.assign({ mw: "fokus", teile, blick: blickName }, abstand ? { abstand } : {}) : { mw: "blick", name: blickName },
  ], extra);
  // Innenleben: Organ hervorgehoben, die anderen Teile blass, Kamera fährt heran
  const innen = (text, teile, ansicht = "situs", blickName = "seite", abstand, extra) => knopf(text, [
    ZURUECK, { mw: "ansicht", name: ansicht }, { mw: "hervorheben", teile, fokus: false },
    Object.assign({ mw: "fokus", teile, blick: blickName }, abstand ? { abstand } : {}),
  ], extra);
  // Nur ein Blick auf die Außenansicht, nichts hervorgehoben (für Zählaufgaben)
  const blick = (text, name) => knopf(text, [ZURUECK, { mw: "ansicht", name: "gestalt" }, { mw: "blick", name }]);
  // Film „Ein Bienenvolk im Bienenstock“: springt auf die Sekunde und spielt (Kapitel nur zur Orientierung im Text)
  const film = (text, t, extra) => Object.assign({ film: "volk", text, befehle: [{ mw: "springe", t }] }, extra || {});

  INHALTE.tabs.push({
    key: "koerper", label: "Die Biene", icon: "🧊", kurz: "B", lese: "L2", leseNach: 55,
    film: MODELL,    // die Bühne mit dem 3D-Modell steht in diesem Reiter neben den Aufgaben
    intro: {
      eyebrow: "Lesestrecke 2", titel: "Eine Biene ist ein Insekt",
      begriffe: ["Insekt", "Fühler", "Facettenauge", "Rüssel", "Flugmuskeln", "Honigmagen", "Stachel", "Pollenkörbchen"],
    },
    aufgaben: [
      // ── 50 · Forscherfrage 1: Wie ist eine Biene gebaut? ──────────────────────────────────────────
      // Jede Option lässt sich im Modell zählen (Körperteile, Beine, Flügel) und damit bestätigen oder widerlegen.
      {
        nr: 50, typ: "vermutung", id: "v_bau", eyebrow: "Forscherfrage", titel: "Wie ist eine Biene gebaut?",
        frage: "Wie viele Körperteile, Beine und Flügel hat eine Biene? Was vermutest du?",
        niveaus: {
          A: { optionen: [
            "Zwei Körperteile, vier Beine, zwei Flügel",
            "Drei Körperteile, sechs Beine, vier Flügel",
            "Drei Körperteile, acht Beine, zwei Flügel",
            "Vier Körperteile, sechs Beine, zwei Flügel",
          ] },
          B: { optionen: [
            "Drei Körperteile, sechs Beine, zwei Flügel",
            "Zwei Körperteile, vier Beine, vier Flügel",
            "Vier Körperteile, acht Beine, zwei Flügel",
            "Drei Körperteile, sechs Beine, vier Flügel",
          ], satzanfang: "Das vermute ich: …", begruendung: ["weil …", "denn …"] },
          C: { satzanfang: "Meine Vermutung: …", frei: true, min: 40 },
        },
      },

      // ── 8 · Das 3D-Modell erkunden (Außenansicht → Situs → Explosion) ─────────────────────────────
      // Die Beobachtungsfragen kehren in den nächsten Stationen wieder (Beine, Flügel in 51; Organe in 54).
      {
        nr: 8, typ: "erkunden", film: MODELL, eyebrow: "Forschen · 3D-Modell", titel: "Das 3D-Modell erkunden",
        niveaus: {
          A: {
            auftrag: "Du bist Forscherin oder Forscher. Sieh dir die Biene der Reihe nach an: von außen, von innen (Situs) und als Explosion. Dreh sie dabei mit dem Finger. „Situs“ heißt: Die Organe liegen an ihrem Platz. Sieh nach, ob deine Vermutung stimmt. Die Fragen findest du in der nächsten Station wieder.",
            beobachtung: ["Wie viele Beine siehst du?", "Wo sitzen die Flügel?", "Was liegt im Hinterleib?"],
          },
          B: {
            auftrag: "Erkunde das Modell wie ein Forscher: von außen, von innen (Situs) und als Explosion. „Situs“ heißt: Die Organe liegen an ihrem Platz. Dreh die Biene und sieh sie von allen Seiten an. Sieh nach, ob deine Vermutung stimmt. Die Fragen findest du in der nächsten Station wieder.",
            beobachtung: ["Wie viele Beine siehst du? Woran sitzen sie?", "Wo sitzen die Flügel?", "Welche Organe liegen im Hinterleib?"],
          },
          C: {
            auftrag: "Erkunde das Modell wie ein Forscher: von außen, von innen (Situs) und als Explosion. Achte darauf, was sich beim Öffnen verändert und was man von außen nicht sieht. Sieh nach, ob deine Vermutung stimmt. Die Fragen findest du in der nächsten Station wieder.",
            beobachtung: [
              "Wie viele Beine hat die Biene und woran sitzen sie?",
              "Welche Organe siehst du im Hinterleib, in der Brust und im Kopf?",
              "Was siehst du erst in der Explosion, aber nicht von außen?",
            ],
          },
        },
      },

      // ── 51 · Forscherbogen: zählen und beobachten (jede Zeile hat ihren Modell-Knopf) ───────────────
      // Zahlzeilen: erste Prüfung ohne Färbung (Technik), danach Hinweise. Der Bogen enthält keine Namen, die erst Aufgabe 9 übt.
      {
        nr: 51, typ: "protokoll", eyebrow: "Forschen", titel: "Zähle und beobachte",
        auftrag: "Sieh dir die Biene im Modell genau an. Trage ein, was du zählst und siehst. Die Knöpfe zeigen dir die passende Ansicht.",
        niveaus: {
          A: {
            zeilen: [
              { frage: "Wie viele Körperteile hat die Biene?", art: "zahl", loesung: 3, einheit: "Körperteile",
                hinweis: "Sieh dir die Biene von der Seite an. Zähle die Abschnitte von vorn nach hinten.",
                modell: blick("Von der Seite ansehen", "seite") },
              { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, einheit: "Beine",
                hinweis: "Zähle die Beine auf beiden Seiten der Biene.",
                hinweis2: "Beginne vorn und zähle nach hinten. Zähle erst eine Seite, dann die andere.",
                modell: aussen("Beine von oben zeigen", ["bein"], "oben", false) },
              { frage: "Wie viele Flügel hat die Biene?", art: "zahl", loesung: 4, einheit: "Flügel",
                hinweis: "Sieh die Flügel von hinten an. Zähle jeden Flügel einzeln.",
                hinweis2: "Auf jeder Seite liegt ein großer und ein kleiner Flügel übereinander.",
                modell: aussen("Flügel von hinten zeigen", ["fluegel"], "hinten", false) },
              { frage: "Wie viele Fühler hat die Biene?", art: "zahl", loesung: 2, einheit: "Fühler",
                hinweis: "Sieh dir den Kopf genau an.",
                modell: aussen("Fühler zeigen", ["fuehler"], "oben", true, 3) },
              { frage: "An welchem Körperteil sitzen die Flügel und die Beine?", kurz: "Flügel und Beine sitzen an", art: "wahl", optionen: ["Kopf", "Brust", "Hinterleib"], loesung: 1,
                hinweis: "Sieh genau hin, wo Flügel und Beine am Körper ansetzen.",
                modell: knopf("Namen der Körperteile zeigen", [
                  ZURUECK, { mw: "ansicht", name: "gestalt" }, { mw: "blick", name: "seite" },
                  { mw: "beschriften", an: true, teile: ["kopf", "brust", "hinterleib"] },
                ]) },
            ],
            schluss: { pflicht: true, anfang: "Ich habe beobachtet, dass …", bausteine: [
              "die Biene sechs Beine hat.",
              { t: "die Biene acht Beine hat.", ok: false, rueckmeldung: "Zähle die Beine noch einmal im Modell." },
              "die Biene vier Flügel hat.",
            ] },
          },
          B: {
            zeilen: [
              { frage: "Wie viele Körperteile hat die Biene?", art: "zahl", loesung: 3, einheit: "Körperteile",
                hinweis: "Sieh dir die Biene von der Seite an. Wo ist sie wie eingeschnürt?",
                modell: blick("Von der Seite ansehen", "seite") },
              { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, einheit: "Beine",
                hinweis: "Zähle die Beine auf beiden Seiten der Biene.",
                hinweis2: "Zähle erst die Beine einer Seite, dann die der anderen Seite.",
                modell: aussen("Beine von oben zeigen", ["bein"], "oben", false) },
              { frage: "Wie viele Flügel hat die Biene?", art: "zahl", loesung: 4, einheit: "Flügel",
                hinweis: "Sieh die Flügel von hinten an. Zähle jeden Flügel einzeln.",
                hinweis2: "Auf jeder Seite liegt ein großer und ein kleiner Flügel übereinander.",
                modell: aussen("Flügel von hinten zeigen", ["fluegel"], "hinten", false) },
              { frage: "Welcher Körperteil trägt die Flügel und die Beine?", kurz: "Flügel und Beine sitzen an", art: "wahl", optionen: ["Hinterleib", "Kopf", "Brust"], loesung: 2,
                hinweis: "Sieh genau hin, wo Flügel und Beine am Körper ansetzen.",
                modell: knopf("Namen der Körperteile zeigen", [
                  ZURUECK, { mw: "ansicht", name: "gestalt" }, { mw: "blick", name: "seite" },
                  { mw: "beschriften", an: true, teile: ["kopf", "brust", "hinterleib"] },
                ]) },
              { frage: "Was sitzt am Kopf? Wähle alles Richtige.", kurz: "Am Kopf sitzen", art: "mehrfach", optionen: ["Fühler", "Flügel", "Augen", "Beine"], loesung: [0, 2],
                hinweis: "Sieh dir den Kopf genau an. Nur zwei Antworten stimmen.",
                modell: aussen("Kopf genau ansehen", ["kopf"], "seite", true, 6) },
            ],
            schluss: { pflicht: true, anfang: "Ich habe beobachtet, dass …", bausteine: [
              { t: "die Biene vier Körperteile, sechs Beine und vier Flügel hat.", ok: false, rueckmeldung: "Zähle die Körperteile noch einmal in der Seitenansicht." },
              { t: "die Biene drei Körperteile, sechs Beine und vier Flügel hat.", ok: true },
              { t: "die Biene drei Körperteile, acht Beine und vier Flügel hat.", ok: false, rueckmeldung: "Zähle die Beine noch einmal von oben." },
            ] },
          },
          C: {
            zeilen: [
              { frage: "Wie viele Körperteile hat die Biene?", art: "zahl", loesung: 3, einheit: "Körperteile",
                hinweis: "Sieh dir die Biene von der Seite an. Wo ist sie wie eingeschnürt?",
                modell: blick("Von der Seite ansehen", "seite") },
              { frage: "Wie viele Beine hat die Biene?", art: "zahl", loesung: 6, einheit: "Beine",
                hinweis: "Zähle die Beine auf beiden Seiten der Biene.",
                hinweis2: "Zähle erst die Beine einer Seite, dann die der anderen Seite.",
                modell: aussen("Beine von oben zeigen", ["bein"], "oben", false) },
              { frage: "Wie viele Flügel hat die Biene?", art: "zahl", loesung: 4, einheit: "Flügel",
                hinweis: "Sieh die Flügel von hinten an. Zähle jeden Flügel einzeln.",
                hinweis2: "Auf jeder Seite liegt ein großer und ein kleiner Flügel übereinander.",
                modell: aussen("Flügel von hinten zeigen", ["fluegel"], "hinten", false) },
              { frage: "Was sitzt an der Brust? Wähle alles Richtige.", kurz: "An der Brust sitzen", art: "mehrfach", optionen: ["Fühler", "Flügel", "Beine", "Augen", "Stachel"], loesung: [1, 2],
                hinweis: "Sieh dir an, was von der Brust abgeht. Nur zwei Antworten stimmen.",
                modell: knopf("Namen der Körperteile zeigen", [
                  ZURUECK, { mw: "ansicht", name: "gestalt" }, { mw: "blick", name: "seite" },
                  { mw: "beschriften", an: true, teile: ["kopf", "brust", "hinterleib"] },
                ]) },
              // Die Beinpaare werden ohne Heranfahren gezeigt (gleicher Abstand), damit man ihre Länge vergleichen kann.
              { frage: "Welches Beinpaar ist am längsten?", kurz: "Längstes Beinpaar", art: "wahl", optionen: ["die Vorderbeine", "die Mittelbeine", "die Hinterbeine"], loesung: 2,
                hinweis: "Zeige die Beinpaare nacheinander. Vergleiche, wie weit jedes Bein reicht.",
                modell: [
                  aussen("Vorderbeine zeigen", ["vorderbein"], "seite", false),
                  aussen("Mittelbeine zeigen", ["mittelbein"], "seite", false),
                  aussen("Hinterbeine zeigen", ["hinterbein"], "seite", false),
                ] },
            ],
            schluss: { pflicht: true, min: 60 },
          },
        },
      },

      // ── 52 · Vermutung 1 prüfen: Wie ist eine Biene gebaut? ───────────────────────────────────────
      // Die Optionen sind gleich gebaut und ähnlich lang; die falschen sind plausible Vermutungen, die man im Modell widerlegt.
      {
        nr: 52, typ: "pruefen", vermutung: "v_bau", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung zum Körperbau?",
        quelle: "Sieh dir die Biene noch einmal im Modell an. Zähle genau und sieh, wo die Teile ansetzen.",
        modell: [
          blick("Von der Seite ansehen", "seite"),
          aussen("Beine von oben zeigen", ["bein"], "oben", false),
          aussen("Flügel von hinten zeigen", ["fluegel"], "hinten", false),
        ],
        erkenntnis: "Der Körper einer Biene hat drei Teile: Kopf, Brust und Hinterleib. An der Brust sitzen sechs Beine und vier Flügel.",
        niveaus: {
          A: { erkenntnis: { frage: "Was hast du herausgefunden?", hinweis: "Zähle die Beine und die Flügel noch einmal im Modell.", optionen: [
            { t: "Die Biene hat acht Beine und vier Flügel.", ok: false },
            { t: "Die Biene hat sechs Beine und vier Flügel.", ok: true },
            { t: "Die Biene hat sechs Beine und zwei große Flügel.", ok: false },
          ] } },
          B: {
            erkenntnis: { frage: "Wo setzen die Beine und die Flügel an?", hinweis: "Sieh dir die Biene von der Seite an. Wo setzen Beine und Flügel an?", optionen: [
              { t: "Am Hinterleib sitzen die Beine und die Flügel.", ok: false },
              { t: "Am Kopf sitzen die Beine und die Flügel.", ok: false },
              { t: "An der Brust sitzen die Beine und die Flügel.", ok: true },
              { t: "An der Brust sitzen die Beine, am Kopf die Flügel.", ok: false },
            ] },
            beleg: { frage: "Wie hast du das herausgefunden?", hinweis: "Welche Aussage nennt etwas, das du im Modell selbst gesehen hast?", optionen: [
              { t: "Ich habe im Film gesehen, wo Beine und Flügel ansetzen.", ok: false },
              { t: "Ich habe im Modell gesehen, wo sie ansetzen.", ok: true },
              { t: "Ich habe im Modell nur die Beine gezählt.", ok: false },
            ] },
          },
          C: {
            erkenntnis: { frage: "Welche Aussage über die Biene stimmt?", hinweis: "Prüfe jede Zahl einzeln: Körperteile, Beine, Flügel.", optionen: [
              { t: "Sie hat zwei Körperteile, sechs Beine und vier Flügel.", ok: false },
              { t: "Sie hat drei Körperteile, acht Beine und vier Flügel.", ok: false },
              { t: "Sie hat drei Körperteile, sechs Beine und zwei große Flügel.", ok: false },
              { t: "Sie hat drei Körperteile, sechs Beine und vier Flügel.", ok: true },
            ] },
            satz: { anfang: "Ich habe herausgefunden, dass … Meine Vermutung war …", min: 60 },
          },
        },
      },

      // ── 9 · Tippe im Modell auf … (Wählmodus, Prüfung im Browser) ─────────────────────────────────
      // Steht hinter 52: erst zählen und prüfen, dann Namen und Lage festigen. Vor jedem Ziel schickt der Baustein „zurueck“.
      // A: Körperteile, Flügel, Bein (außen, von der Seite). B: Fühler (mit Fokus), Hinterbein und Körperteile über Beschreibungen.
      // C: kleine Teile mit Fokus: Facettenauge, Rüssel, Mittelbein, Vorderbein. Keine Organe: Lage und Aussehen der Organe
      //    erforscht erst Station 54, kein Pollenkörbchen: Das erforscht Station 55.
      // Treffer: „kopf“ gilt auch beim Tippen aufs Facettenauge, „bein“ auch beim Tippen aufs Hinterbein oder Mittelbein.
      {
        nr: 9, typ: "modellfinden", film: MODELL, eyebrow: "Forschen · Im Modell", titel: "Tippe im Modell auf …",
        niveaus: {
          A: { auftrag: "Tippe im 3D-Modell auf die gesuchten Teile. Du darfst die Biene dazwischen drehen.", ziele: [
            { teil: "kopf", frage: "Tippe auf den Kopf.", hinweis: "Such das vordere Körperteil mit den großen Augen.", ansicht: "gestalt", blick: "seite" },
            { teil: "brust", frage: "Tippe auf die Brust.", hinweis: "Das ist das mittlere Körperteil, zwischen Kopf und Hinterleib.", ansicht: "gestalt", blick: "seite" },
            { teil: "hinterleib", frage: "Tippe auf den Hinterleib.", hinweis: "Das ist das hinterste Körperteil mit den vielen Ringen.", ansicht: "gestalt", blick: "seite" },
            { teil: "fluegel", frage: "Tippe auf einen Flügel.", hinweis: "Such die dünnen Teile, durch die man hindurchsehen kann.", ansicht: "gestalt", blick: "seite" },
            { teil: "bein", frage: "Tippe auf ein Bein.", hinweis: "Such die dünnen, dunklen Teile mit den Gelenken.", ansicht: "gestalt", blick: "seite" },
          ] },
          B: { auftrag: "Tippe im 3D-Modell auf die gesuchten Teile. Manche sind klein. Dreh die Biene, wenn du ein Teil nicht findest.", ziele: [
            { teil: "fuehler", frage: "Tippe auf einen Fühler.", hinweis: "Er ist lang und dünn und sitzt ganz vorn.", ansicht: "gestalt", blick: "oben", fokus: { teile: ["fuehler"], blick: "oben" } },
            { teil: "hinterbein", frage: "Tippe auf ein Hinterbein.", hinweis: "Es ist das Bein, das ganz hinten am Körper ansetzt.", ansicht: "gestalt", blick: "seite" },
            { teil: "brust", frage: "Tippe auf die Brust.", hinweis: "Sie liegt in der Mitte, zwischen den anderen beiden Körperteilen.", ansicht: "gestalt", blick: "seite" },
            { teil: "kopf", frage: "Tippe auf das Körperteil mit den großen Augen.", hinweis: "Es ist das vorderste Körperteil.", ansicht: "gestalt", blick: "seite" },
            { teil: "hinterleib", frage: "Tippe auf das Körperteil mit den Streifen.", hinweis: "Es ist das hinterste Körperteil.", ansicht: "gestalt", blick: "seite" },
          ] },
          C: { auftrag: "Tippe im 3D-Modell auf die gesuchten Teile. Die Kamera fährt von selbst nah heran. Dreh die Biene, wenn du ein Teil nicht findest.", ziele: [
            { teil: "facettenauge", frage: "Tippe auf das Teil, mit dem die Biene sieht.", hinweis: "Such die großen, gewölbten Flächen seitlich am vordersten Körperteil.", ansicht: "gestalt", blick: "seite", fokus: { teile: ["facettenauge"], blick: "seite" } },
            { teil: "ruessel", frage: "Tippe auf den Rüssel.", hinweis: "Er liegt zusammengefaltet unter dem Kopf, zwischen den Mundwerkzeugen.", ansicht: "gestalt", blick: "vorn", fokus: { teile: ["ruessel"], blick: "vorn" } },
            { teil: "mittelbein", frage: "Tippe auf ein Mittelbein.", hinweis: "Es gehört zum mittleren der drei Beinpaare.", ansicht: "gestalt", blick: "seite", fokus: { teile: ["mittelbein"], blick: "seite" } },
            { teil: "vorderbein", frage: "Tippe auf ein Vorderbein.", hinweis: "Es ist das Bein, das ganz vorn am Körper ansetzt.", ansicht: "gestalt", blick: "seite", fokus: { teile: ["vorderbein"], blick: "seite" } },
          ] },
        },
      },

      // ── 53 · Forscherfrage 2: Wie trägt die Biene Nektar und Pollen nach Hause? ───────────────────────
      // Jede Option lässt sich mit Film (Szene 8) und Modell bestätigen oder widerlegen; alle sind plausibel.
      {
        nr: 53, typ: "vermutung", id: "v_sammeln", eyebrow: "Forscherfrage", titel: "Wie trägt die Biene Nektar und Pollen nach Hause?",
        frage: "Nektar ist der süße Saft der Blüten. Pollen ist der Blütenstaub. Was vermutest du?",
        niveaus: {
          A: { optionen: [
            "Beides trägt sie im Rüssel.",
            "Nektar im Hinterleib, Pollen an den Beinen.",
            "Nektar an den Beinen, Pollen im Hinterleib.",
            "Beides trägt sie im Hinterleib.",
          ] },
          B: { optionen: [
            "Beides trägt sie im Hinterleib.",
            "Nektar im Rüssel, Pollen an den Beinen.",
            "Nektar im Hinterleib, Pollen an den Beinen.",
            "Nektar an den Beinen, Pollen im Hinterleib.",
          ], satzanfang: "Das vermute ich: …", begruendung: ["weil …", "denn …"] },
          C: { satzanfang: "Meine Vermutung: …", frei: true, min: 40 },
        },
      },

      // ── 54 · Das Innenleben (Situs): Wo liegt es? Wie sieht es im Modell aus? ──────────────────────────
      // Nur Organe, die das Modell eindeutig einem Körperteil zuordnet: Honigmagen (Hinterleib), Flugmuskeln (Brust), Gehirn (Kopf, die
      // Verdickung), Stachel (Ende des Hinterleibs). Herz und Darm laufen durch mehrere Körperteile und stehen nicht in der Tabelle.
      // Was die Organe tun, steht erst in der Lesestrecke (Honigmagen, Flugmuskeln, Stachel) und im Film (Szene 8: Honigmagen).
      // Alle Organ-Knöpfe sind Pflicht: Man soll jedes Organ sehen, bevor man tippt. Der Stachel steht in der Explosion
      // (im Situs nur etwa zur Hälfte sichtbar).
      {
        nr: 54, typ: "tabelle", eyebrow: "Forschen · Innenleben", titel: "Das Innenleben der Biene",
        auftrag: "Du suchst, wo die Biene den Nektar tragen könnte. Sieh dir dazu die Organe an. Organe sind Teile im Körper, die eine Aufgabe haben. Das Modell ist ein Nachbau am Computer, seine Farben helfen nur beim Unterscheiden. Zeige jedes Organ einzeln und fülle dann die Tabelle aus.",
        modell: [
          innen("Honigmagen zeigen", ["honigmagen"], "situs", "seite", 4, { pflicht: true }),
          innen("Flugmuskeln zeigen", ["flugmuskeln"], "situs", "seite", 4.6, { pflicht: true }),
          innen("Gehirn zeigen", ["gehirn"], "situs", "seite", 5.2, { pflicht: true }),
          innen("Stachel zeigen", ["stachel"], "explosion", "seite", 4.1, { pflicht: true }),
          knopf("Alle Organe zeigen", [ZURUECK, { mw: "ansicht", name: "situs" }, { mw: "blick", name: "seite" }]),
        ],
        erkenntnis: "Der Honigmagen liegt im Hinterleib. Die Flugmuskeln liegen in der Brust. Das Gehirn liegt im Kopf. Der Stachel sitzt am Ende des Hinterleibs.",
        niveaus: {
          // A hat wie B und C vier Spalten, denn alle vier Organ-Knöpfe sind Pflicht (auch der Stachel).
          A: { spalten: ["Honigmagen", "Flugmuskeln", "Gehirn", "Stachel"], zeilen: [
            { merkmal: "Wo liegt es hauptsächlich?", optionen: ["Kopf", "Brust", "Hinterleib"], loesung: [2, 1, 0, 2],
              hinweis: "Zeige das Organ im Modell. In welchem Körperteil liegt der größte Teil? Beim Gehirn: Suche die dicke gelbe Verdickung." },
            { merkmal: "So sieht es im Modell aus", optionen: ["zwei Kugeln mit einem Strang", "ein Säckchen", "klein und spitz", "ein Block aus feinen Fasern"], loesung: [1, 3, 0, 2],
              hinweis: "Sieh dir das Organ genau an, wenn es leuchtet." },
          ] },
          B: { spalten: ["Honigmagen", "Flugmuskeln", "Gehirn", "Stachel"], zeilen: [
            { merkmal: "Wo liegt es hauptsächlich?", optionen: ["Kopf", "Brust", "Hinterleib"], loesung: [2, 1, 0, 2],
              hinweis: "Zeige das Organ im Modell. In welchem Körperteil liegt der größte Teil? Beim Gehirn: Suche die dicke gelbe Verdickung." },
            { merkmal: "So sieht es im Modell aus", optionen: ["ein Block aus feinen Fasern", "klein und spitz", "zwei Kugeln mit einem Strang", "ein Säckchen"], loesung: [3, 0, 2, 1],
              hinweis: "Sieh dir das Organ genau an, wenn es leuchtet." },
          ] },
          // C: zwei zusätzliche Formen sind falsche Antworten (Schlauch, Rohr), die zu keiner Spalte gehören
          C: { spalten: ["Honigmagen", "Flugmuskeln", "Gehirn", "Stachel"], zeilen: [
            { merkmal: "Wo liegt es hauptsächlich?", optionen: ["Kopf", "Brust", "Hinterleib"], loesung: [2, 1, 0, 2],
              hinweis: "Zeige das Organ im Modell. In welchem Körperteil liegt der größte Teil? Beim Gehirn: Suche die dicke gelbe Verdickung." },
            { merkmal: "So sieht es im Modell aus", optionen: ["ein langer Schlauch", "ein Block aus feinen Fasern", "klein und spitz", "ein dünnes Rohr", "zwei Kugeln mit einem Strang", "ein Säckchen"], loesung: [5, 1, 4, 2],
              hinweis: "Sieh dir jedes Organ genau an, wenn es leuchtet. Achte auf die Form." },
          ] },
        },
      },

      // ── 55 · Vermutung 2 prüfen: Film Szene 8 und Modell ──────────────────────────────────────────
      // Film Szene 8 (Sprechertext): Rüssel saugt Nektar, füllt den Honigmagen; Pollen als gelbes Höschen ans Hinterbein.
      // Neutrale Quelle und Knopftexte: Wohin der Nektar geht und wo der Pollen bleibt, sollen Kinder hören und sehen, nicht lesen.
      // Zeiten (ab_uebergabe.md): Nektar 145,3–149,2 s, Pollen 149,7–153,1 s. Beide Film-Knöpfe sind Pflicht.
      {
        nr: 55, typ: "pruefen", vermutung: "v_sammeln", eyebrow: "Vermutung prüfen", titel: "Wie trägt die Biene Nektar und Pollen?",
        quelle: "Sieh dir Szene 8 im Film an. Achte darauf, wohin der Nektar geht und wo der Pollen bleibt.",
        modell: [
          film("▶ Sieh dir an: Was passiert mit dem Nektar? (Kapitel 8)", 145, { pflicht: true }),
          film("▶ Sieh dir an: Was passiert mit dem Pollen? (Kapitel 8)", 149.5, { pflicht: true }),
          innen("Modell: Ein Organ im Körperinneren zeigen", ["honigmagen"], "situs", "seite", 4),
          aussen("Modell: Ein Bein von hinten zeigen", ["pollenkoerbchen"], "hinten", true, 4),
        ],
        erkenntnis: "Die Biene saugt den Nektar mit dem Rüssel und trägt ihn im Honigmagen im Hinterleib. Den Pollen trägt sie als gelbes Höschen am Hinterbein.",
        niveaus: {
          A: { erkenntnis: { frage: "Was hast du herausgefunden?", hinweis: "Sieh dir den Film noch einmal an: Wohin geht der Nektar, wo bleibt der Pollen?", optionen: [
            { t: "Nektar im Honigmagen, Pollen im Hinterleib.", ok: false },
            { t: "Nektar an den Hinterbeinen, Pollen im Honigmagen.", ok: false },
            { t: "Nektar im Honigmagen, Pollen am Hinterbein.", ok: true },
          ] } },
          B: {
            erkenntnis: { frage: "Wohin kommen Nektar und Pollen?", hinweis: "Hör im Film genau hin: Was sagt die Sprecherin zum Nektar, was zum Pollen?", optionen: [
              { t: "Der Nektar und der Pollen kommen beide ans Hinterbein.", ok: false },
              { t: "Der Nektar kommt an die Hinterbeine, der Pollen in den Honigmagen.", ok: false },
              { t: "Der Nektar kommt in den Honigmagen, der Pollen ans Hinterbein.", ok: true },
              { t: "Der Nektar und der Pollen kommen beide in den Honigmagen.", ok: false },
            ] },
            beleg: { frage: "Woran hast du das erkannt?", hinweis: "Welche Aussage sagt, was im Film mit Nektar und Pollen passiert?", optionen: [
              { t: "Im Film fliegt die Biene von einer Blüte zur nächsten Blüte.", ok: false },
              { t: "Im Film füllt sich der Hinterleib, am Bein wird es gelb.", ok: true },
              { t: "Im Film streckt die Biene den Rüssel in eine Blüte.", ok: false },
            ] },
          },
          C: {
            erkenntnis: { frage: "Welche Aussage stimmt?", hinweis: "Prüfe Film und Modell: Wo liegt das Organ, wo sitzt das Höschen?", optionen: [
              { t: "Der Nektar ist im Rüssel. Der Pollen klebt am Hinterbein.", ok: false },
              { t: "Der Nektar ist im Honigmagen. Der Pollen klebt am Hinterbein.", ok: true },
              { t: "Der Nektar ist im Honigmagen im Kopf. Der Pollen klebt am Hinterleib.", ok: false },
              { t: "Der Nektar klebt am Hinterbein. Der Pollen ist im Honigmagen.", ok: false },
            ] },
            satz: { anfang: "Ich habe herausgefunden, dass … Meine Vermutung war …", min: 60 },
          },
        },
      },

      // ── 56 · Sprachwerkstatt: Einzahl und Mehrzahl mit Artikel (Plural nach Duden) ───────────────────
      // Linke und rechte Begriffe sind in jeder Stufe verschieden. „der Flügel – die Flügel“: gleiche Form in der Mehrzahl.
      // Nur Wörter aus diesem Reiter. Alle Paare werden akzeptiert (Tippen und Zuordnen); `hinweis` ersetzt den Anleitungssatz.
      {
        nr: 56, typ: "zuordnung", eyebrow: "Sprachwerkstatt · Einzahl und Mehrzahl", titel: "Eine Biene – viele Bienen",
        niveaus: {
          A: { links: "Einzahl", rechts: "Mehrzahl",
               hinweis: "Tippe links ein Wort in der Einzahl an, dann rechts die Mehrzahl. Beispiel: eine Biene – viele Bienen.",
               hilfe: "Sprich beide Wörter laut. Die Mehrzahl heißt immer „die“. Beispiel: eine Biene – viele Bienen.", paare: [
            ["die Biene", "die Bienen"],
            ["der Kopf", "die Köpfe"],
            ["das Bein", "die Beine"],
            ["der Flügel", "die Flügel"],
          ] },
          B: { links: "Einzahl", rechts: "Mehrzahl",
               hinweis: "Tippe links ein Wort in der Einzahl an, dann rechts die Mehrzahl. Beispiel: ein Bein – viele Beine.",
               hilfe: "Sprich beide Wörter laut. Manche Wörter ändern sich in der Mehrzahl nicht, zum Beispiel „der Flügel“.", paare: [
            ["die Biene", "die Bienen"],
            ["der Kopf", "die Köpfe"],
            ["das Bein", "die Beine"],
            ["der Flügel", "die Flügel"],
            ["das Auge", "die Augen"],
            ["der Fühler", "die Fühler"],
          ] },
          C: { links: "Einzahl", rechts: "Mehrzahl",
               hinweis: "Tippe links ein Wort in der Einzahl an, dann rechts die Mehrzahl. Achte auf Umlaute und auf gleiche Formen.",
               hilfe: "Sprich beide Wörter laut. Bei manchen Wörtern bleibt die Mehrzahl gleich, bei anderen kommt ein Umlaut oder ein „n“ dazu.", paare: [
            ["der Hinterleib", "die Hinterleiber"],
            ["der Stachel", "die Stacheln"],
            ["das Facettenauge", "die Facettenaugen"],
            ["der Rüssel", "die Rüssel"],
            ["das Pollenkörbchen", "die Pollenkörbchen"],
            ["das Insekt", "die Insekten"],
            ["der Körperteil", "die Körperteile"],
          ] },
        },
      },

      // ── 57 · Sprachwerkstatt: Zeitfolge – der Weg des Nektars (Film: Szene 8 und 10, Modell: Rüssel, Honigmagen) ─
      // A: Signalwörter helfen beim Ordnen. B: jeder Satz hat ein anderes Signalwort. C: ohne Signalwörter.
      // Film-Knöpfe springen auf die Sätze: Nektar saugen 145 s (Szene 8), Nektar weitergeben 181 s (Szene 10).
      {
        nr: 57, typ: "sortierung", eyebrow: "Sprachwerkstatt · Zeitfolge", titel: "Der Weg des Nektars: zuerst, dann, danach",
        modell: [
          aussen("Rüssel im Modell zeigen", ["ruessel"], "vorn", true, 3.2),
          innen("Honigmagen im Modell zeigen", ["honigmagen"], "situs", "seite", 4),
          film("▶ Sieh dir an: Der Nektar wird aufgesaugt (Kapitel 8)", 145),
          film("▶ Sieh dir an: Der Nektar wird weitergegeben (Kapitel 10)", 181),
        ],
        niveaus: {
          A: { hinweis: "Achte auf die Wörter zuerst, dann, danach und schließlich.",
               hilfe: "Die Signalwörter zeigen die Reihenfolge: zuerst, dann, danach, schließlich. Die Film-Knöpfe zeigen den Weg.", items: [
            "Zuerst landet die Biene auf einer Blüte.",
            "Dann saugt sie den Nektar mit dem Rüssel.",
            "Danach fließt der Nektar in den Honigmagen.",
            "Schließlich fliegt sie zum Bienenstock zurück.",
          ] },
          B: { hinweis: "Ordne die Sätze. Jedes Signalwort sagt dir, wo der Satz steht.",
               hilfe: "Jedes Signalwort steht an einer anderen Stelle: zuerst, dann, danach, anschließend, schließlich.", items: [
            "Zuerst fliegt die Biene zu einer Blüte.",
            "Dann saugt sie mit dem Rüssel Nektar auf.",
            "Danach fließt der Nektar in den Honigmagen.",
            "Anschließend fliegt sie zurück zum Bienenstock.",
            "Schließlich gibt sie den Nektar im Bienenstock ab.",
          ] },
          C: { hinweis: "Hier helfen keine Signalwörter. Denke an den Weg des Nektars.",
               hilfe: "Frage dich: Was passiert zuerst mit dem Nektar, was zuletzt? Die Film-Knöpfe zeigen Szene 8 und Szene 10.", items: [
            "Die Sammlerin fliegt zu einer Blüte.",
            "Mit dem Rüssel saugt sie den Nektar auf.",
            "Der Nektar sammelt sich im Honigmagen.",
            "Die Sammlerin fliegt zurück in den Bienenstock.",
            "Sie gibt den Nektar an andere Bienen weiter.",
            "Aus dem Nektar wird im Bienenstock Honig.",
          ] },
        },
      },

      // ── 15 · Zeichnung 1: Die Biene von der Seite (Prüfliste für die KI: zeichenauftraege.py, Eintrag „biene“) ──
      // Anwenden, nicht Forschen. `elemente` gehen in den KI-Auftrag; Niveau A zeigt sie als Checkliste (zeichnen.js).
      {
        nr: 15, typ: "zeichnen", eyebrow: "Zeichnen", titel: "Die Biene von der Seite", geraet: "biene",
        modell: blick("Biene von der Seite im Modell ansehen", "seite"),
        niveaus: {
          A: {
            aufgabe: "Zeichne eine Biene von der Seite. Sie braucht: Kopf, Brust, Hinterleib, sechs Beine, zwei Fühler und Flügel.",
            elemente: ["Kopf", "Brust", "Hinterleib", "sechs Beine", "zwei Fühler", "Flügel"],
            hinweis: "Tipp: Fange mit drei Ovalen an. Der Kopf ist vorn, die Brust in der Mitte, der Hinterleib hinten. Dann kommen Beine, Fühler und Flügel.",
          },
          B: {
            aufgabe: "Zeichne eine Biene von der Seite mit Streifen am Hinterleib. Schreibe die Namen der drei Körperteile dazu.",
            elemente: ["Kopf", "Brust", "Hinterleib", "sechs Beine", "zwei Fühler", "Flügel", "Streifen am Hinterleib", "Namen der drei Körperteile"],
            hinweis: "Tipp: Die Streifen laufen quer über den Hinterleib. Schreibe die Namen neben die Körperteile und zeichne einen Strich dorthin.",
          },
          C: {
            aufgabe: "Zeichne eine Biene von der Seite und beschrifte sie. Schreibe zu einem Körperteil, welche Aufgabe er hat.",
            elemente: ["Kopf", "Brust", "Hinterleib", "sechs Beine", "zwei Fühler", "Flügel", "Streifen am Hinterleib", "Stachel am Ende des Hinterleibs", "Beschriftung der Körperteile", "ein Satz zur Aufgabe eines Körperteils"],
            hinweis: "Tipp: Schau dir das Modell von der Seite an. Beschrifte mit Strichen. Ein Satz reicht, zum Beispiel zu den Fühlern oder zur Brust.",
          },
        },
      },
    ],
  });
})();
