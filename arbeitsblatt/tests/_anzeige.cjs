// Lädt die Inhaltsdateien (Argumente nach dem Ordner-Argument, in Ladereihenfolge) samt static/js/anzeige.js und tafel_adapter.js
// und gibt die Anzeigenummern, die Adapter-Titel und die Kopfzeilen der Karten (aufgaben.js) als JSON aus.
// Aufruf: node _anzeige.cjs <static/js-Ordner> <inhalte.js> <inhalte_x.js> …
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const [ordner, ...inhalteDateien] = process.argv.slice(2);
const ctx = { console };
ctx.window = ctx;
ctx.GT = {};
vm.createContext(ctx);
const lade = (f) => vm.runInContext(fs.readFileSync(f, "utf8"), ctx, { filename: f });
inhalteDateien.forEach(lade);
lade(path.join(ordner, "anzeige.js"));
lade(path.join(ordner, "tafel_adapter.js"));
const I = ctx.INHALTE;

(async () => {
  const liste = await ctx.GT.abAdapter.aufgaben([]);
  const karte = I.anzeigeKarte();
  const nrs = {};
  const alleNr = [];
  I.tabs.forEach((t) => t.aufgaben.forEach((a) => { alleNr.push(String(a.nr)); nrs[String(a.nr)] = I.anzeigeNr(a.nr); }));
  const lese = I.tabs.filter((t) => t.lese).map((t) => ({ nr: t.lese, anzeige: I.anzeigeNr(t.lese), label: I.anzeigeLabel(t.lese) }));
  const labels = {};
  alleNr.forEach((n) => { labels[n] = I.anzeigeLabel(n); });
  process.stdout.write(JSON.stringify({
    karte, nrs, alleNr, lese, labels,
    adapter: liste.map((x) => ({ id: x.aufgabe_id, titel: x.titel })),
    unbekannt: [I.anzeigeNr("ZZZ"), I.anzeigeNr(9999), I.anzeigeNr("t")],
  }));
})().catch((e) => { console.error(e); process.exit(1); });
