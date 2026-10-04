// Erzeugt alle Tafel-Fassungen des Browser-Adapters (static/js/tafel_adapter.js) als JSON:
// echte Inhalte (Argumente) plus synthetische Aufgaben aller Typen, damit jeder Weg auch ohne fertige Inhalte geprüft wird.
// Aufruf: node _tafel_adapter_daten.js <adapter.js> <inhalte.js> <inhalte_x.js> …
const vm = require("vm");
const fs = require("fs");

const [adapter, ...inhalteDateien] = process.argv.slice(2);
const ctx = { console };
ctx.window = ctx;
ctx.GT = {};
vm.createContext(ctx);
for (const f of inhalteDateien) vm.runInContext(fs.readFileSync(f, "utf8"), ctx, { filename: f });

// Synthetischer Reiter mit je einer Aufgabe pro Typ (Nummern ab 900, damit sie nie mit echten kollidieren)
const mc = (nr, cfgs, extra) => Object.assign({ nr, typ: "mc", eyebrow: "t", titel: "Synthetisch " + nr, niveaus: cfgs }, extra || {});
const ja = (t) => ({ t, ok: true }), nein = (t) => ({ t, ok: false });
ctx.INHALTE.tabs.push({
  key: "synthetisch", label: "S", icon: "x", kurz: "S", aufgaben: [
    mc(901, { A: { frage: "F?", optionen: [ja("r"), nein("f1"), nein("f2")] }, B: { frage: "F?", optionen: [nein("a"), ja("b"), nein("c"), nein("d")] },
      C: { multi: 2, frage: "F?", optionen: [ja("a"), nein("b"), ja("c"), nein("d")] } }),
    mc(902, { A: { frage: "Stimmt das?", aussagen: [{ t: "A1", ok: true }, { t: "A2", ok: false }] },
      B: { frage: "Stimmt das?", aussagen: [{ t: "B1", ok: false }, { t: "B2", ok: true }, { t: "B3", ok: true }] },
      C: { frage: "Stimmt das?", aussagen: [{ t: "C1", ok: true }, { t: "C2", ok: false }] } }),
    { nr: 903, typ: "luecke", eyebrow: "t", titel: "Lücke", niveaus: {
      A: { modus: "chips", ablenker: ["x"], text: "Das ist ein [Wort] und ein [Satz]." },
      B: { modus: "input", text: "Das ist [Honig|Nektar]." }, C: { modus: "input", text: "Ein [Stachel] sticht." } } },
    { nr: 904, typ: "zuordnung", eyebrow: "t", titel: "Zuordnung", niveaus: {
      A: { links: "L", rechts: "R", paare: [["x", "1"], ["x", "2"], ["y", "3"]] }, B: { links: "L", rechts: "R", paare: [["x", "1"], ["y", "2"], ["z", "3"]] },
      C: { links: "L", rechts: "R", paare: [["x", "1"], ["y", "2"], ["z", "3"], ["w", "4"]] } } },
    { nr: 905, typ: "sortierung", eyebrow: "t", titel: "Sortierung", niveaus: {
      A: { hinweis: "H", items: ["eins", "zwei", "drei"] }, B: { hinweis: "H", items: ["eins", "zwei", "drei", "vier"] }, C: { hinweis: "H", items: ["a", "b", "c", "d", "e"] } } },
    { nr: 906, typ: "freitext", eyebrow: "t", titel: "Freitext", niveaus: {
      A: { modus: "bausteine", aufgabe: "Ordne.", bausteine: ["eins.", "zwei.", "drei.", "vier."], schluss: "S", urteil: { frage: "?", optionen: ["a", "b"] } },
      B: { aufgabe: "Schreibe.", starter: ["Ich …"], min: 50 }, C: { aufgabe: "Schreibe mehr.", min: 100 } } },
    // Typen ohne Tafel-Fassung
    { nr: 907, typ: "transfer", eyebrow: "t", titel: "Transfer", niveaus: { A: { modus: "bausteine", aufgabe: "x", bausteine: ["a", "b", "c", "d"], schluss: "s", urteil: { frage: "?", optionen: ["a", "b"] } }, B: { aufgabe: "x" }, C: { aufgabe: "x" } } },
    { nr: 908, typ: "diagramm", eyebrow: "t", titel: "Diagramm", chart: {}, niveaus: { A: { frage: "f", optionen: [ja("a"), nein("b")] }, B: { frage: "f", optionen: [ja("a"), nein("b")] }, C: { frage: "f", optionen: [ja("a"), nein("b")] } } },
    { nr: 909, typ: "bildpunkte", eyebrow: "t", titel: "Bild", karte: "x", niveaus: { A: {}, B: {}, C: {} } },
    { nr: 910, typ: "zeichnen", eyebrow: "t", titel: "Zeichnen", geraet: "biene", niveaus: { A: {}, B: {}, C: {} } },
    { nr: 911, typ: "blitz", eyebrow: "t", titel: "Blitz", niveaus: { A: {}, B: {}, C: {} }, pool: [] },
    { nr: 912, typ: "domino", eyebrow: "t", titel: "Domino", niveaus: { A: {}, B: {}, C: {} }, paare: [] },
    { nr: 913, typ: "quellen", eyebrow: "t", titel: "Quellen" },
    { nr: 914, typ: "notizen", eyebrow: "t", titel: "Notizen", abschnitt: "synthetisch" },
    { nr: 915, typ: "film", eyebrow: "t", titel: "Film", film: "volk" },
    { nr: 916, typ: "filmmoment", eyebrow: "t", titel: "Moment", film: "volk", niveaus: { A: {}, B: {}, C: {} } },
    { nr: 917, typ: "erkunden", eyebrow: "t", titel: "Erkunden", film: "biene3d" },
    { nr: 918, typ: "modellfinden", eyebrow: "t", titel: "Finden", film: "biene3d", niveaus: { A: { ziele: [] }, B: { ziele: [] }, C: { ziele: [] } } },
  ],
});

vm.runInContext(fs.readFileSync(adapter, "utf8"), ctx, { filename: adapter });

(async () => {
  const GT = ctx.GT;
  const liste = await GT.abAdapter.aufgaben([]);
  const leer = [];
  for (const a of liste) {
    for (const n of a.niveaus) leer.push(Object.assign({ id: a.aufgabe_id, niveau: n }, await GT.abAdapter.leer(a.aufgabe_id, n)));
  }
  // Karten aus einem Arbeitsstand: leer und mit Antworten (Autosave-Format)
  const staende = {
    leer: {},
    mitAntworten: {
      niveaus: { 901: "A", 902: "B", 906: "A" },
      aufgaben: {
        901: { gewaehlt: [0] }, 902: { wahl: ["f", "r", null] }, 903: { werte: ["Wort", "Satz"] }, 904: { paare: [0, 1] },
        905: { reihenfolge: [2, 0, 1] }, 906: { text: [0, 1], urteil: 0 },
      },
      texte: { "ft-906": "Text" },
    },
  };
  const karten = {};
  for (const [name, st] of Object.entries(staende)) {
    ctx.BIE = { autosave: { collectBackup: () => st } };
    karten[name] = await GT.abAdapter.meineAufgaben();
  }
  // Prüfungen am Adapter selbst
  const tauglich = {};
  for (const t of ctx.INHALTE.tabs) for (const a of t.aufgaben) tauglich[a.nr] = GT.abAdapter.tafelTauglich(a.nr);
  process.stdout.write(JSON.stringify({ liste, leer, karten, tauglich }));
})().catch((e) => { console.error(e); process.exit(1); });
