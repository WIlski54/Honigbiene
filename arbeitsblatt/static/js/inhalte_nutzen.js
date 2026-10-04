// Reiter 4 „Nutzen & Schutz“ – forschend-entwickelnd (docs/FORSCHEN.md, Reihenfolge und Dramaturgie: plan_nutzen.py)
// Stand nach dem Audit vom 4. Oktober 2026 (docs/AUDIT_FORSCHEN_2026-10-04.md, Reiter 4).
// Leitfrage: „Warum ist die Biene ein wichtiges Nutztier – und was braucht sie von uns?“
//   Forscherfrage 1 (70, Äpfel ohne Insekten) → Film beobachten (71) → ausgedachtes Beispiel mit zwei Apfelzweigen (72) → Prüfen (73)
//   Forscherfrage 2 (74) → Rätselbild ohne Etiketten erkunden (75) → Prüfen (76, Bild-Knopf) → Lesestrecke 4 nachschlagen (nach 76)
//   → Sprachwerkstatt Zeitfolge (77) und Begründen (36) → Zeichnung 3 (35) → Forscherbuch-Notizen (37).
// Film „Ein Bienenvolk im Bienenstock“ (INHALTE.filme.volk, 12 Szenen = Kapitel 1–12): Station 71 (Kapitel 10, Pflicht-Knopf) und
// 73 (Kapitel 12, Schlüsselsatz). Aufgaben dürfen nur fragen, was der Film, das Bild oder die Lesestrecke 4 zeigt oder sagt.
// Feste Wörter: Bienenstock (ganzes Zuhause) · Bienenkasten (Holzkiste des Imkers) · Wabe · Zelle · Honigmagen · Rüssel · Sammlerin …
// „Zuckerlösung“ ist im ganzen Reiter die Bezeichnung für das Futter im Spätsommer; die Bienen suchen ihr Futter meist selbst.
// Zahlen in Station 72 sind ein AUSGEDACHTES Beispiel und stehen dort ausdrücklich als „Ausgedachtes Beispiel – nicht gemessen“.
(() => {
  "use strict";

  // Film-Knöpfe (Kapitel n = Szene n; Sekunden aus papiertheater/docs/ab_uebergabe.md). film.js hängt `spielen` an: alle starten sofort.
  // Kapitel 10 „Aus Nektar wird Honig“ (179,7–199,7 s), Kapitel 12 „Ein Volk wie ein Körper“ (218,6–240 s).
  const K10 = { film: "volk", text: "▶ Sieh dir an: Aus Nektar wird Honig (Kapitel 10)", befehle: [{ mw: "kapitel", n: 10 }], pflicht: true };
  const K12 = { film: "volk", text: "▶ Hör zu: „… Honig, Wachs und viele Früchte“ (Kapitel 12)", befehle: [{ mw: "springe", t: 228.3 }] };
  // Sprungmarken für einzelne Zeilen des Forscherbogens 71
  const stelle = (t, text) => ({ film: "volk", text, befehle: [{ mw: "springe", t }] });
  // Bild-Knopf: öffnet das Rätselbild (ohne Etiketten) im Overlay – die Evidenz für Station 76
  const RAETSEL = "/static/img/lese/nutzen-5-raetsel.svg";
  const BILD_KNOPF = { bild: RAETSEL, text: "Rätselbild noch einmal ansehen",
    alt: "Rätselbild. Links eine Wiese mit Bienen, rechts eine kahle Fläche mit Fahrzeug, oben eine Lupe mit einer Biene." };

  // Bildwahl 75: Orte im Rätselbild (viewBox 900 × 560), Werte aus werkzeuge/nutzen5_raetsel_punkte.json
  const WIESE = { x: 235, y: 408, r: 150 }, KAHL = { x: 565, y: 482, r: 70 }, TRAKTOR = { x: 784, y: 469, r: 80 }, LUPE = { x: 700, y: 190, r: 125 };
  const NEUTRAL = "Das ist es nicht. Vergleiche noch einmal alle vier Stellen im Bild.";
  const OHNE_BIENEN = "Hier sitzen Bienen. Such eine Stelle, an der keine sitzen.";
  // Ziel = Ort + ok (+ Rückmeldung bei falsch)
  const ziel = (ort, ok, rueckmeldung) => (ok ? { ...ort, ok: true } : { ...ort, ok: false, rueckmeldung });
  const runde = (frage, ziele, hinweis, erklaerung) => ({ bild: RAETSEL, breite: 900, hoehe: 560, frage, ziele, hinweis, erklaerung });

  const ERKL_KAHL = "Rechts sitzen keine Bienen, denn dort wachsen keine Blumen. Auf einer kahlen Fläche finden Bienen kaum Nahrung.";
  const ERKL_TRAKTOR = "Das Fahrzeug spritzt ein Pestizid. Das ist ein Mittel gegen Schädlinge. Manche Pestizide können auch Bienen schaden.";
  const ERKL_LUPE = "Die Lupe zeigt die Varroa-Milbe. Sie saugt an Bienen und schwächt das ganze Volk.";
  const ERKL_WIESE = "Auf der Wiese blühen viele Blumen. Dort finden Bienen Nektar und Pollen.";

  INHALTE.tabs.push({
    key: "nutzen", label: "Nutzen & Schutz", icon: "🍯", kurz: "S", lese: "L4", leseNach: 76,
    film: "volk",
    intro: {
      eyebrow: "Lesestrecke 4", titel: "Honig, Wachs, Blüten – und Gefahren",
      begriffe: ["Schleuder", "Wachs", "Bestäubung", "Varroa-Milbe", "Pestizid", "Blühwiese"],
    },
    aufgaben: [
      // ─── 70 · Forscherfrage 1: Wie viele Äpfel trägt ein Baum, wenn keine Insekten kommen? ──────────
      // Jede Option lässt sich mit den Zahlen aus Station 72 bestätigen oder widerlegen (12 gegen 2 Äpfel).
      {
        nr: 70, typ: "vermutung", id: "v_aepfel", eyebrow: "Forscherfrage", titel: "Wie viele Äpfel trägt ein Baum, wenn keine Insekten kommen?",
        frage: "Was vermutest du?",
        niveaus: {
          A: { optionen: ["Genauso viele Äpfel wie sonst.", "Ein wenig weniger Äpfel als sonst.", "Viel weniger Äpfel als sonst.", "Gar keine Äpfel."] },
          B: { optionen: ["Genauso viele Äpfel wie sonst.", "Ein wenig weniger Äpfel als sonst.", "Viel weniger Äpfel als sonst.", "Gar keine Äpfel."],
               satzanfang: "Das vermute ich, …", begruendung: ["weil …", "denn …"] },
          C: { satzanfang: "Meine Vermutung: …", frei: true, min: 30 },
        },
      },

      // ─── 71 · Forschen mit dem Film: Wie wird aus Nektar Honig? (Kapitel 10, Pflicht-Sperre) ─────────
      // Nur, was der Film zeigt: Nektar wird von Rüssel zu Rüssel weitergegeben (181–185 s), die Bienen fächeln (185–190 s) und
      // verschließen die Zellen mit Wachs (189–192 s), der Nektar wird dick und goldfarben (187–189 s), der Imker zieht EIN volles
      // Rähmchen heraus (193–196 s; im Film stark vereinfacht), ein Honigglas füllt sich.
      {
        nr: 71, typ: "protokoll", eyebrow: "Forschen · Film", titel: "Wie wird aus Nektar Honig?",
        auftrag: "Sieh dir im Film Kapitel 10 genau an. Trage ein, was du beobachtest.",
        modell: [K10],
        erkenntnis: "Aus Nektar machen die Bienen Honig. Der Imker erntet nur einen Teil davon.",
        niveaus: {
          A: {
            zeilen: [
              { frage: "Womit geben die Bienen den Nektar weiter?", art: "wahl", optionen: ["mit den Beinen", "mit den Rüsseln", "mit den Flügeln"], loesung: 1,
                hinweis: "Schau genau auf die Köpfe der beiden Bienen.", hinweis2: "Der Nektar geht von einer Biene zur nächsten. Sieh dir die Stelle noch einmal an.",
                modell: stelle(181.4, "▶ Sieh dir die Stelle an (Kapitel 10)") },
              { frage: "Was passiert danach mit dem Nektar? Wähle alles, was du siehst.", art: "mehrfach",
                optionen: ["Die Bienen mischen ihn mit Pollen.", "Die Bienen fächeln ihn mit den Flügeln.", "Die Bienen füllen ihn in den Honigmagen.", "Die Bienen verschließen die Zellen mit Wachs."],
                loesung: [1, 3], hinweis: "Schau dir den Stock noch einmal genau an. Wähle nur, was du wirklich siehst.", hinweis2: "Zwei Antworten sind richtig.",
                modell: stelle(185, "▶ Sieh dir den Stock an (Kapitel 10)") },
              { frage: "Wie viele Rähmchen zieht der Imker im Film heraus?", art: "zahl", loesung: 1, einheit: "Rähmchen",
                hinweis: "Schau auf die Hände des Imkers.", hinweis2: "Zähle nur das Rähmchen, das er in der Hand hält.",
                fehlertext: "Zähle noch einmal im Film nach.", modell: stelle(192.5, "▶ Sieh dir die Ernte an (Kapitel 10)") },
            ],
            schluss: { pflicht: true, anfang: "Ich habe beobachtet, dass …", bausteine: ["der Imker nur einen Teil des Honigs erntet.",
              { t: "der Imker den ganzen Honig erntet.", ok: false, rueckmeldung: "Sieh dir noch einmal an, was im Kasten bleibt." },
              "die Bienen die Zellen mit Wachs verschließen."] },
          },
          B: {
            zeilen: [
              { frage: "Womit geben die Bienen den Nektar weiter?", art: "wahl", optionen: ["mit den Flügeln", "mit den Beinen", "mit den Rüsseln"], loesung: 2,
                hinweis: "Schau genau auf die Köpfe der beiden Bienen.", hinweis2: "Der Nektar geht von einer Biene zur nächsten. Sieh dir die Stelle noch einmal an.",
                modell: stelle(181.4, "▶ Sieh dir die Stelle an (Kapitel 10)") },
              { frage: "Was passiert danach mit dem Nektar? Wähle alles, was du siehst.", art: "mehrfach",
                optionen: ["Die Bienen füllen ihn in den Honigmagen.", "Die Bienen verschließen die Zellen mit Wachs.", "Die Bienen mischen ihn mit Pollen.", "Die Bienen fächeln ihn mit den Flügeln."],
                loesung: [1, 3], hinweis: "Schau dir den Stock noch einmal genau an. Wähle nur, was du wirklich siehst.", hinweis2: "Zwei Antworten sind richtig.",
                modell: stelle(185, "▶ Sieh dir den Stock an (Kapitel 10)") },
              { frage: "Welche Farbe haben die Zellen am Ende?", art: "wahl", optionen: ["goldfarben", "hellgelb", "weiß"], loesung: 0,
                hinweis: "Vergleiche die Farbe der Zellen vor und nach dem Fächeln.", modell: stelle(186.5, "▶ Sieh dir die Zellen an (Kapitel 10)") },
              { frage: "Wie viele Rähmchen zieht der Imker im Film heraus?", art: "zahl", loesung: 1, einheit: "Rähmchen",
                hinweis: "Schau auf die Hände des Imkers.", hinweis2: "Zähle nur das Rähmchen, das er in der Hand hält.",
                fehlertext: "Zähle noch einmal im Film nach.", modell: stelle(192.5, "▶ Sieh dir die Ernte an (Kapitel 10)") },
            ],
            schluss: { pflicht: true, anfang: "Zuerst geben die Bienen den Nektar weiter. Dann …", min: 40 },
          },
          C: {
            zeilen: [
              { frage: "Wie wird der Nektar im Stock weitergegeben?", art: "wahl", optionen: ["von Bein zu Bein", "von Rüssel zu Rüssel", "über die Flügel"], loesung: 1,
                hinweis: "Schau genau auf die Köpfe der beiden Bienen.", hinweis2: "Der Nektar geht von einer Biene zur nächsten. Sieh dir die Stelle noch einmal an.",
                modell: stelle(181.4, "▶ Sieh dir die Stelle an (Kapitel 10)") },
              { frage: "Was passiert danach mit dem Nektar? Wähle alles, was du siehst.", art: "mehrfach",
                optionen: ["Die Bienen verschließen die Zellen mit Wachs.", "Die Bienen mischen ihn mit Pollen.", "Die Bienen fächeln ihn mit den Flügeln.", "Die Bienen tragen ihn nach draußen.", "Die Bienen füllen ihn in den Honigmagen."],
                loesung: [0, 2], hinweis: "Schau dir den Stock noch einmal genau an. Wähle nur, was du wirklich siehst.", hinweis2: "Zwei Antworten sind richtig.",
                modell: stelle(185, "▶ Sieh dir den Stock an (Kapitel 10)") },
              { frage: "Was passiert mit dem Nektar, wenn die Bienen fächeln?", art: "wahl",
                optionen: ["Er wird dünner und klar.", "Er wird dicker und goldfarben.", "Er wird kälter und weiß."], loesung: 1,
                hinweis: "Vergleiche die Farbe der Zellen vor und nach dem Fächeln.", modell: stelle(186.5, "▶ Sieh dir die Zellen an (Kapitel 10)") },
              { frage: "Wie viele Rähmchen zieht der Imker im Film heraus?", art: "zahl", loesung: 1, einheit: "Rähmchen",
                hinweis: "Schau auf die Hände des Imkers.", hinweis2: "Zähle nur das Rähmchen, das er in der Hand hält.",
                fehlertext: "Zähle noch einmal im Film nach.", modell: stelle(192.5, "▶ Sieh dir die Ernte an (Kapitel 10)") },
            ],
            schluss: { pflicht: true, anfang: "So wird aus Nektar Honig: …", frei: true, min: 80 },
          },
        },
      },

      // ─── 72 · Forschen mit einem ausgedachten Beispiel: zwei Apfelzweige ──────────────────────────
      // Die Zahlen sind AUSGEDACHT und stehen deshalb ausdrücklich als „Ausgedachtes Beispiel – nicht gemessen“ im Titel, im Auftrag
      // und in der Erklärung der ersten Zeile. Erst NACH der eigenen Vermutung (Zeile 1) erscheinen die Zahlen.
      {
        nr: 72, typ: "protokoll", eyebrow: "Forschen · Ausgedachtes Beispiel", titel: "Zwei Apfelzweige im Vergleich",
        auftrag: "Ausgedachtes Beispiel – die Zahlen sind nicht gemessen. Eine Forscherin vergleicht zwei Apfelzweige mit je 20 Blüten. "
          + "Zweig 1 bleibt offen, Insekten können kommen. Zweig 2 bekommt ein Netz, Insekten kommen nicht an die Blüten. Im Herbst zählt sie die Äpfel.",
        niveaus: {
          A: {
            zeilen: [
              { frage: "Meine Vermutung: Wie viele Äpfel wachsen an Zweig 2?", art: "text", satzanfang: "Zweig 2 hat …", min: 4, kurz: "Meine Vermutung", fehlertext: "Schreibe ein Wort, zum Beispiel „viele“ oder „wenige“.",
                erklaerung: "So sieht das ausgedachte Beispiel aus: Zweig 1 (offen) hat 12 Äpfel: 🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎. Zweig 2 (Netz) hat 2 Äpfel: 🍎🍎." },
              { frage: "Welcher Zweig hat mehr Äpfel?", art: "wahl", optionen: ["Zweig 2 (Netz)", "Beide gleich viele", "Zweig 1 (offen)"], loesung: 2, hinweis: "Vergleiche die beiden Zahlen im Beispiel." },
              { frage: "Wie viele Äpfel hat Zweig 1 mehr als Zweig 2?", art: "zahl", loesung: 10, einheit: "Äpfel", hinweis: "Ziehe die kleinere Zahl von der größeren ab.",
                fehlertext: "Rechne noch einmal: Zweig 1 minus Zweig 2." },
              { frage: "Was ist bei Zweig 2 anders?", art: "wahl", optionen: ["Zweig 2 hat mehr Blüten.", "Zweig 2 bleibt offen.", "Insekten kommen nicht an die Blüten."], loesung: 2,
                hinweis: "Lies noch einmal, was die Forscherin mit Zweig 2 gemacht hat." },
            ],
            schluss: { pflicht: true, anfang: "Ich habe herausgefunden, dass …", bausteine: ["Zweig 2 viel weniger Äpfel hat als Zweig 1.",
              { t: "beide Zweige gleich viele Äpfel haben.", ok: false, rueckmeldung: "Vergleiche die Zahlen noch einmal." },
              "Zweig 1 offen für Insekten ist."] },
          },
          B: {
            zeilen: [
              { frage: "Meine Vermutung: Wie viele Äpfel wachsen an Zweig 2?", art: "text", satzanfang: "Ich vermute, dass Zweig 2 …", min: 12, kurz: "Meine Vermutung",
                erklaerung: "So sieht das ausgedachte Beispiel aus: Zweig 1 (offen) hat 12 Äpfel: 🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎. Zweig 2 (Netz) hat 2 Äpfel: 🍎🍎." },
              { frage: "Welcher Zweig hat mehr Äpfel?", art: "wahl", optionen: ["Zweig 2 (Netz)", "Beide gleich viele", "Zweig 1 (offen)"], loesung: 2, hinweis: "Vergleiche die beiden Zahlen im Beispiel." },
              { frage: "Wie viele Äpfel hat Zweig 1 mehr als Zweig 2?", art: "zahl", loesung: 10, einheit: "Äpfel", hinweis: "Ziehe die kleinere Zahl von der größeren ab.",
                fehlertext: "Rechne noch einmal: Zweig 1 minus Zweig 2." },
              { frage: "Was ist der Unterschied zwischen den beiden Zweigen?", art: "wahl",
                optionen: ["Zweig 2 hatte weniger Blüten.", "Bei Zweig 2 kamen Insekten an die Blüten.", "Bei Zweig 2 kamen keine Insekten an die Blüten."], loesung: 2,
                hinweis: "Lies noch einmal, was die Forscherin mit Zweig 2 gemacht hat." },
            ],
            schluss: { pflicht: true, anfang: "Der Zweig mit Netz …", min: 40 },
          },
          C: {
            zeilen: [
              { frage: "Meine Vermutung: Wie viele Äpfel wachsen an Zweig 2? Begründe.", art: "text", satzanfang: "Ich vermute, dass Zweig 2 … Äpfel hat, weil …", min: 25, kurz: "Meine Vermutung",
                erklaerung: "So sieht das ausgedachte Beispiel aus: Zweig 1 (offen) hat 12 Äpfel: 🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎. Zweig 2 (Netz) hat 2 Äpfel: 🍎🍎." },
              { frage: "Wie viele Äpfel hat Zweig 1 mehr als Zweig 2?", art: "zahl", loesung: 10, einheit: "Äpfel", hinweis: "Ziehe die kleinere Zahl von der größeren ab.",
                fehlertext: "Rechne noch einmal: Zweig 1 minus Zweig 2." },
              { frage: "Was zeigen die Zahlen im Beispiel? Wähle alles, was stimmt.", art: "mehrfach",
                optionen: ["Mit Netz wachsen viel weniger Äpfel.", "Ein Netz macht die Äpfel größer.", "Offen wachsen mehr Äpfel als mit Netz.", "Das Netz hat keinen Einfluss auf die Äpfel."], loesung: [0, 2],
                hinweis: "Wähle nur, was du direkt an den beiden Zahlen ablesen kannst.", hinweis2: "Zwei Antworten sind richtig." },
              { frage: "Was könnte der Grund sein, dass Zweig 2 so wenige Äpfel hat?", art: "text", satzanfang: "Ich vermute, dass …", min: 25, kurz: "Möglicher Grund" },
            ],
            schluss: { pflicht: true, anfang: "Das Beispiel zeigt, …", frei: true, min: 60 },
          },
        },
      },

      // ─── 73 · Vermutung 1 prüfen: gleich lange, prüfbare Aussagen; Evidenz = Zahlen aus 72 und Film Kapitel 12 ─
      {
        nr: 73, typ: "pruefen", vermutung: "v_aepfel", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?",
        quelle: "Ausgedachtes Beispiel: Zweig 1 (offen) hat 12 Äpfel, Zweig 2 (Netz) hat 2 Äpfel. Hör dann im Film zu.",
        modell: [K12],
        erkenntnis: "Im Beispiel trägt der Zweig ohne Insekten viel weniger Äpfel. Insekten sind wichtig für Früchte.",
        niveaus: {
          A: { erkenntnis: { frage: "Was hast du herausgefunden?", fehltext: "Das passt nicht zu den Zahlen im Beispiel.", hinweis: "Vergleiche die beiden Zahlen: 12 und 2.", optionen: [
            { t: "Ohne Insekten trägt der Zweig genauso viele Äpfel.", ok: false },
            { t: "Ohne Insekten trägt der Zweig viel weniger Äpfel.", ok: true },
            { t: "Ohne Insekten trägt der Zweig ein wenig weniger Äpfel.", ok: false },
          ] } },
          B: {
            erkenntnis: { frage: "Was hast du herausgefunden?", fehltext: "Das passt nicht zu den Zahlen im Beispiel.", hinweis: "Vergleiche die beiden Zahlen: 12 und 2.", optionen: [
              { t: "Ohne Insekten trägt der Zweig viel weniger Äpfel.", ok: true },
              { t: "Ohne Insekten trägt der Zweig gar keine Äpfel.", ok: false },
              { t: "Ohne Insekten trägt der Zweig ein wenig weniger Äpfel.", ok: false },
              { t: "Ohne Insekten trägt der Zweig genauso viele Äpfel.", ok: false },
            ] },
            beleg: { frage: "Woran siehst du das?", fehltext: "Das steht so nicht im Beispiel.", hinweis: "Lies die Zahlen für Zweig 1 und Zweig 2 noch einmal genau.", optionen: [
              { t: "Zweig 2 hat 12 Äpfel, und Zweig 1 hat nur 2.", ok: false },
              { t: "Beide Zweige haben ungefähr gleich viele Äpfel.", ok: false },
              { t: "Zweig 1 hat 12 Äpfel, Zweig 2 hat nur 2.", ok: true },
            ] },
          },
          C: {
            erkenntnis: { frage: "Was hast du herausgefunden? Wie viele Äpfel trägt Zweig 1 im Vergleich zu Zweig 2?", fehltext: "Das passt nicht zu den Zahlen im Beispiel.", hinweis: "Teile die Zahl von Zweig 1 durch die Zahl von Zweig 2.", optionen: [
              { t: "Zweig 1 trägt dreimal so viele Äpfel wie Zweig 2.", ok: false },
              { t: "Zweig 1 trägt fünfmal so viele Äpfel wie Zweig 2.", ok: false },
              { t: "Zweig 1 trägt sechsmal so viele Äpfel wie Zweig 2.", ok: true },
              { t: "Zweig 1 trägt zwanzigmal so viele Äpfel wie Zweig 2.", ok: false },
            ] },
            satz: { anfang: "Ich habe herausgefunden, dass …", min: 40 },
          },
        },
      },

      // ─── 74 · Forscherfrage 2: Was gefährdet die Bienen? ─────────────────────────────────────
      // Jede Option lässt sich am Rätselbild (75) bestätigen oder widerlegen: Wiese ohne Etiketten, kahle Fläche, Fahrzeug mit
      // Spritzmittel, Lupe mit einer Milbe auf der Biene, Bienen und Schmetterlinge zusammen auf der Wiese.
      {
        nr: 74, typ: "vermutung", id: "v_gefahren", eyebrow: "Forscherfrage", titel: "Was gefährdet die Bienen?",
        frage: "Was vermutest du?",
        niveaus: {
          A: { mehrfach: true, optionen: ["zu wenig Blumen", "winzige Tiere, die auf Bienen sitzen", "Gifte gegen Schädlinge", "zu viele Schmetterlinge"] },
          B: { mehrfach: true, optionen: ["zu wenig Blumen", "winzige Tiere, die auf Bienen sitzen", "Gifte gegen Schädlinge", "zu viele Schmetterlinge"],
               satzanfang: "Ich vermute, dass Bienen in Gefahr sind, …", begruendung: ["weil …", "denn …"] },
          C: { satzanfang: "Meine Vermutung: …", frei: true, min: 40 },
        },
      },

      // ─── 75 · Forschen am Rätselbild ohne Etiketten: Warum fehlen hier Bienen? ────────────────────
      // Vier Kreise je Runde (alle Orte des Bildes), Fragen ohne Gefahrenwort, ein neutraler Fehltext. Die Wörter „Pestizid“ und
      // „Varroa-Milbe“ stehen erst in der Erklärung NACH dem richtigen Tipp.
      {
        nr: 75, typ: "bildwahl", eyebrow: "Forschen · Bild", titel: "Hier fehlen Bienen – finde heraus, warum",
        niveaus: {
          A: { runden: [
            runde("Auf der Wiese sitzen viele Bienen. Tippe auf eine Stelle, an der keine Biene sitzt.",
              [ziel(LUPE, false, OHNE_BIENEN), ziel(KAHL, true), ziel(WIESE, false, OHNE_BIENEN), ziel(TRAKTOR, true)],
              "Vergleiche die linke und die rechte Seite des Bildes.", ERKL_KAHL),
            runde("Tippe auf etwas, das Menschen mitgebracht haben.",
              [ziel(TRAKTOR, true), ziel(KAHL, false, NEUTRAL), ziel(WIESE, false, NEUTRAL), ziel(LUPE, false, NEUTRAL)],
              "Suche etwas, das nicht in die Natur gehört.", ERKL_TRAKTOR),
            runde("Tippe auf etwas Winziges, das auf einer Biene sitzt.",
              [ziel(WIESE, false, NEUTRAL), ziel(TRAKTOR, false, NEUTRAL), ziel(LUPE, true), ziel(KAHL, false, NEUTRAL)],
              "Eine Lupe zeigt etwas Kleines groß. Wo siehst du eine Lupe?", ERKL_LUPE),
          ] },
          B: { runden: [
            runde("Auf der Wiese sitzen viele Bienen. Wo sitzt keine Biene? Tippe auf eine Stelle.",
              [ziel(TRAKTOR, true), ziel(LUPE, false, OHNE_BIENEN), ziel(KAHL, true), ziel(WIESE, false, OHNE_BIENEN)],
              "Vergleiche die linke und die rechte Seite des Bildes.", ERKL_KAHL),
            runde("Tippe auf etwas, das Menschen auf Feldern ausbringen.",
              [ziel(WIESE, false, NEUTRAL), ziel(LUPE, false, NEUTRAL), ziel(KAHL, false, NEUTRAL), ziel(TRAKTOR, true)],
              "Suche etwas, das nicht in die Natur gehört.", ERKL_TRAKTOR),
            runde("Tippe auf das winzige Tier, das auf einer Biene sitzt.",
              [ziel(LUPE, true), ziel(KAHL, false, NEUTRAL), ziel(TRAKTOR, false, NEUTRAL), ziel(WIESE, false, NEUTRAL)],
              "Eine Lupe zeigt etwas Kleines groß. Wo siehst du eine Lupe?", ERKL_LUPE),
            runde("Auf einer Seite finden Bienen genug Nektar und Pollen. Tippe auf einen Ort dort.",
              [ziel(KAHL, false, NEUTRAL), ziel(WIESE, true), ziel(LUPE, false, NEUTRAL), ziel(TRAKTOR, false, NEUTRAL)],
              "Wo sitzen die meisten Bienen?", ERKL_WIESE),
          ] },
          C: { runden: [
            runde("Auf der Wiese sitzen viele Bienen, auf der anderen Seite keine. Tippe auf einen Ort, an dem Bienen kaum Nahrung finden.",
              [ziel(KAHL, true), ziel(TRAKTOR, true), ziel(WIESE, false, OHNE_BIENEN), ziel(LUPE, false, OHNE_BIENEN)],
              "Wo wachsen keine Blumen?", ERKL_KAHL),
            runde("Tippe auf etwas, das Menschen auf Feldern ausbringen.",
              [ziel(LUPE, false, NEUTRAL), ziel(WIESE, false, NEUTRAL), ziel(TRAKTOR, true), ziel(KAHL, false, NEUTRAL)],
              "Suche etwas, das nicht in die Natur gehört.", ERKL_TRAKTOR),
            runde("Tippe auf das winzige Tier, das auf einer Biene sitzt.",
              [ziel(TRAKTOR, false, NEUTRAL), ziel(KAHL, false, NEUTRAL), ziel(LUPE, true), ziel(WIESE, false, NEUTRAL)],
              "Eine Lupe zeigt etwas Kleines groß. Wo siehst du eine Lupe?", ERKL_LUPE),
            runde("Auf einer Seite finden Bienen genug Nektar und Pollen. Tippe auf einen Ort dort.",
              [ziel(WIESE, true), ziel(LUPE, false, NEUTRAL), ziel(KAHL, false, NEUTRAL), ziel(TRAKTOR, false, NEUTRAL)],
              "Wo sitzen die meisten Bienen?", ERKL_WIESE),
          ] },
        },
      },

      // ─── 76 · Vermutung 2 prüfen: prüfbare Aussagen über das Rätselbild, Bild-Knopf zur Evidenz ──────
      {
        nr: 76, typ: "pruefen", vermutung: "v_gefahren", eyebrow: "Vermutung prüfen", titel: "Stimmte deine Vermutung?",
        quelle: "Schau dir das Rätselbild noch einmal genau an.",
        modell: [BILD_KNOPF],
        erkenntnis: "Bienen sind in Gefahr. Blüten fehlen, manche Pestizide schaden und die Varroa-Milbe schwächt das Volk.",
        niveaus: {
          A: { erkenntnis: { frage: "Was zeigt das Bild?", fehltext: "Das passt nicht zu dem, was im Rätselbild zu sehen ist.", hinweis: "Zähle, was auf der rechten Seite anders ist als auf der Wiese.", optionen: [
            { t: "Das Bild zeigt nur einen Grund: Auf der kahlen Fläche fehlen Blumen.", ok: false },
            { t: "Das Bild zeigt keinen Grund: Bienen finden überall Nahrung.", ok: false },
            { t: "Das Bild zeigt drei Gründe: fehlende Blumen, Spritzmittel, Milbe.", ok: true },
          ] } },
          B: {
            erkenntnis: { frage: "Was zeigt das Bild?", fehltext: "Das passt nicht zu dem, was im Rätselbild zu sehen ist.", hinweis: "Schau auf alle vier Stellen im Bild, auch auf die Lupe.", optionen: [
              { t: "Bienen haben nur Probleme durch Spritzmittel, sonst ist im Bild alles gut.", ok: false },
              { t: "Bienen haben Probleme durch fehlende Blumen, Spritzmittel und Milben.", ok: true },
              { t: "Bienen haben Probleme, weil es zu viele Blumen und Bienen gibt.", ok: false },
            ] },
            beleg: { frage: "Woran siehst du das im Bild?", fehltext: "Das siehst du so nicht im Bild.", hinweis: "Suche die Lupe. Was sitzt auf der Biene?", optionen: [
              { t: "Auf der Wiese sitzt keine einzige Biene mehr.", ok: false },
              { t: "Auf einer Biene sitzt ein winziges Tier.", ok: true },
              { t: "Auf der kahlen Fläche blühen sehr viele Blumen.", ok: false },
            ] },
          },
          C: {
            erkenntnis: { frage: "Was zeigt das Bild?", fehltext: "Das passt nicht zu dem, was im Rätselbild zu sehen ist.", hinweis: "Prüfe jede Stelle im Bild einzeln: Wiese, kahle Fläche, Fahrzeug, Lupe.", optionen: [
              { t: "Blumen fehlen, ein Fahrzeug spritzt, eine Milbe sitzt auf einer Biene.", ok: true },
              { t: "Nur die Milbe schadet den Bienen, alles andere im Bild ist harmlos.", ok: false },
              { t: "Nur das Fahrzeug schadet den Bienen, alles andere im Bild ist harmlos.", ok: false },
              { t: "Nur fehlende Blumen schaden den Bienen, alles andere im Bild ist harmlos.", ok: false },
            ] },
            satz: { anfang: "Ich habe herausgefunden, dass …", min: 40 },
          },
        },
      },

      // ─── 77 · Sprachwerkstatt: Zeitfolge am Imkerjahr (Lückentext mit Chips; nach der Lesestrecke 4) ──
      // A: Zeitangaben (im Frühling … im Winter) · B: zuerst, dann, schließlich ohne Jahreszeitwörter · C: tippen, dazu begründen mit weil.
      {
        nr: 77, typ: "luecke", eyebrow: "Sprachwerkstatt · Zeitfolge", titel: "Das Imkerjahr: zuerst, dann, schließlich",
        niveaus: {
          A: { modus: "chips",
            hilfe: "Denke an das Imkerjahr: Wann wächst das Volk? Wann erntet der Imker? Wann ruhen die Bienen?",
            text: "[Im Frühling] wächst das Volk. [Im Sommer] erntet der Imker einen Teil des Honigs. [Im Spätsommer] ergänzt er Zuckerlösung als Ersatz für den Honig. [Im Winter] lässt er die Bienen in Ruhe." },
          B: { modus: "chips", ablenker: ["Deshalb", "Weil"],
            hilfe: "Welches Wort passt an den Anfang? Welches an den Schluss? Lies die Sätze und ordne sie in Gedanken.",
            text: "[Zuerst] wächst das Volk. [Dann] erntet der Imker einen Teil des Honigs. Im Spätsommer ergänzt er Zuckerlösung als Ersatz für den Honig. [Schließlich] lässt er die Bienen im Winter in Ruhe." },
          C: { modus: "input",
            hilfe: "Überlege: Was kommt am Anfang, was in der Mitte, was am Schluss? Warum ergänzt der Imker Zuckerlösung?",
            text: "[Zuerst|Als Erstes] wächst das Volk. [Dann|Danach|Anschließend] erntet der Imker einen Teil des Honigs. Im Spätsommer ergänzt er Zuckerlösung, [weil|da] er Honig genommen hat. [Schließlich|Zuletzt|Am Ende] lässt er die Bienen im Winter in Ruhe." },
        },
      },

      // ─── 36 · Sprachwerkstatt: Begründen mit weil, denn, damit – Was können wir für Bienen tun? ──
      {
        nr: 36, typ: "freitext", eyebrow: "Sprachwerkstatt · Begründen", titel: "Was können wir für Bienen tun?",
        kontext: "Klasse 6 NW, Reiter Nutzen und Schutz, Leitfrage: Warum ist die Honigbiene ein wichtiges Nutztier und was können wir für Bienen tun? "
          + "Sprachziel: begründen mit weil, denn, damit, deshalb. "
          + "Gelernt: Honig als Vorrat (der Imker nimmt nur einen Teil), Wachs, Bestäubung bei Apfel, Kirsche und Raps, "
          + "Imkerjahr (die Bienen suchen ihr Futter meist selbst, im Spätsommer ergänzt der Imker Zuckerlösung und behandelt gegen die Varroa-Milbe), "
          + "Gefahren: Varroa-Milbe, weniger Blumen, Pestizide; Hilfe: Blühwiese, bienenfreundlicher Garten. "
          + "Gute Antworten nennen eine Gefahr, eine passende Maßnahme und eine Begründung mit weil, denn oder damit. "
          + "Auch richtig: Blühwiese oder Blumen auf dem Balkon anlegen, im Garten auf Pestizide verzichten, Imker unterstützen, "
          + "Insektenhotel bauen (hilft vor allem Wildbienen, nicht dem Honigbienenvolk). "
          + "Stichworte: Blühwiese, Insektenhotel, Pestizide, Imker unterstützen, Varroa-Milbe, Nahrung. "
          + "Rückmeldung freundlich, ohne fertige Lösung; auf Verbindungswörter achten.",
        niveaus: {
          // A: Textbausteine in der richtigen Reihenfolge, danach ein Urteil per Antippen (kein freies Schreiben).
          // Eindeutige Folge: Aber (Problem) → Deshalb (Blühwiese) → So (Ergebnis dieses Schritts) → Außerdem (zweite Maßnahme, zuletzt).
          A: {
            modus: "bausteine",
            aufgabe: "Viele Bienen finden zu wenig Nahrung. Ordne die Sätze. Achte auf die Wörter aber, deshalb, so und außerdem. Danach entscheidest du selbst.",
            bausteine: [
              "Bienen finden Nektar und Pollen in Blüten.",
              "Aber auf kahlen Flächen gibt es kaum Blüten.",
              "Deshalb können wir eine Blühwiese anlegen.",
              "So finden die Bienen schon mehr Nahrung.",
              "Außerdem verzichten wir auf Pestizide, damit sie den Bienen nicht schaden.",
            ],
            schluss: "Schon kleine Schritte helfen den Bienen.",
            urteil: {
              frage: "Was würdest du zuerst tun? Tippe eine Antwort an.",
              optionen: [
                "Ich würde eine Blühwiese anlegen, damit die Bienen Nahrung finden.",
                "Ich würde den Imker unterstützen, damit er sich um die Bienen kümmern kann.",
              ],
            },
          },
          B: {
            aufgabe: "Bienen sind in Gefahr. Erkläre, was wir für sie tun können. Begründe mit weil, denn oder damit. Nutze die Satzanfänge.",
            starter: ["Bienen sind in Gefahr, weil …", "Wir legen eine Blühwiese an, damit …", "Wir verzichten auf Pestizide, weil …", "Das hilft den Bienen, denn …"],
            begriffe: ["Varroa-Milbe", "Blühwiese", "Pestizide", "Nektar"],
            min: 120,
          },
          C: {
            aufgabe: "Beurteile: Was ist der wichtigste Schritt, um Bienen zu schützen? Nenne mindestens zwei Gefahren und zwei Maßnahmen. Begründe mit weil, denn oder damit.",
            begriffe: ["Varroa-Milbe", "Blühwiese", "Pestizide", "Imker", "Bestäubung"],
            min: 200,
          },
        },
      },

      // ─── 35 · Zeichnung 3: Bestäubung (Prüfliste: zeichenauftraege.py, Schlüssel „bestaeubung“) ───
      {
        nr: 35, typ: "zeichnen", eyebrow: "Zeichnen", titel: "Die Bestäubung", geraet: "bestaeubung",
        niveaus: {
          A: { aufgabe: "Zeichne eine Blüte und eine Biene daran. Zeichne gelbe Pünktchen für den Pollen. Zeichne daneben einen Apfel.",
               elemente: ["Blüte", "Biene an der Blüte", "gelbe Pünktchen (Pollen)", "Apfel"],
               hinweis: "Tipp: Erst die Blüte mit Blütenblättern, dann die Biene mit Flügeln und gestreiftem Hinterleib." },
          B: { aufgabe: "Zeichne die Bestäubung. Zeichne eine Biene mit Pollen an einer Blüte, einen Pfeil zu einer zweiten Blüte und daneben einen Apfel.",
               elemente: ["Biene mit Pollen an einer Blüte", "zweite Blüte", "Pfeil von Blüte zu Blüte", "Frucht (Apfel)"],
               hinweis: "Tipp: Der Pfeil zeigt den Weg des Pollens. Der Apfel steht am Ende." },
          C: { aufgabe: "Zeichne die Bestäubung von der Biene bis zur Frucht. Beschrifte mindestens drei Teile mit dem Textwerkzeug.",
               elemente: ["Biene an einer Blüte", "Pollen", "zweite Blüte", "Pfeil von Blüte zu Blüte", "Frucht", "mindestens drei Beschriftungen"],
               hinweis: "Tipp: Beschrifte zum Beispiel Pollen, Blüte und Frucht. Nutze Pfeile für die Reihenfolge." },
        },
      },

      // ─── 37 · Mein Forscherbuch: Stichpunkte zu Nutzen und Schutz ─────────────────────────────
      {
        nr: 37, typ: "notizen", eyebrow: "Eigene Notizen", titel: "Meine Stichpunkte zu Nutzen und Schutz", abschnitt: "nutzen",
        hinweis: "Schreibe Stichpunkte zu Honig, Wachs, Bestäubung, Imkerjahr und Gefahren auf. Nutze deine Erkenntnisse, die Lesestrecke und den Film.",
        kiFrage: "Prüfe diese Stichpunkte zum Thema Nutzen und Schutz der Honigbiene (Klasse 6): Stimmen sie fachlich? "
          + "Fehlt etwas Wichtiges zu Honig, Wachs, Bestäubung, Imkerjahr oder zu den Gefahren (Varroa-Milbe, weniger Blumen, Pestizide)? "
          + "Gib freundliche Hinweise, aber keine fertigen Lösungen.",
      },
    ],
  });
})();
