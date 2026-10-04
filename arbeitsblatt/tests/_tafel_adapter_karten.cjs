// Baut für jede an der Tafel angebotene echte Aufgabe (A/B/C) einen vollständig ausgefüllten Arbeitsstand und übersetzt ihn in
// Tafel-Karten (Browser-Adapter static/js/tafel_adapter.js). Ausgabe: JSON {karten: [...], aufgaben: [...]}.
// Aufruf: node _tafel_adapter_karten.cjs <adapter.js> <inhalte.js> <inhalte_x.js> …
const vm = require("vm");
const fs = require("fs");

const [adapter, ...inhalteDateien] = process.argv.slice(2);
const ctx = { console };
ctx.window = ctx;
ctx.GT = {};
vm.createContext(ctx);
for (const f of inhalteDateien) vm.runInContext(fs.readFileSync(f, "utf8"), ctx, { filename: f });
vm.runInContext(fs.readFileSync(adapter, "utf8"), ctx, { filename: adapter });

(async () => {
  const GT = ctx.GT;
  const liste = await GT.abAdapter.aufgaben([]);
  const karten = [];
  for (const a of liste) {
    for (const n of a.niveaus) {
      const { aufgabe, loesung } = await GT.abAdapter.leer(a.aufgabe_id, n);
      const st = { niveaus: { [a.aufgabe_id]: n }, aufgaben: {}, texte: {} };
      const t = ctx.INHALTE.tabs.flatMap((x) => x.aufgaben).find((x) => String(x.nr) === String(a.aufgabe_id));
      const cfg = t.niveaus ? t.niveaus[n] : t;
      if (aufgabe.aufgabentyp === "lueckentext") st.aufgaben[a.aufgabe_id] = { werte: Object.keys(loesung).sort().map((k) => loesung[k][0]) };
      else if (aufgabe.aufgabentyp === "zuordnung") st.aufgaben[a.aufgabe_id] = { paare: cfg.paare.map((_, i) => i) };
      else if (aufgabe.aufgabentyp === "sortieren") st.aufgaben[a.aufgabe_id] = cfg.modus === "bausteine" ? { text: cfg.bausteine.map((_, i) => i) } : { reihenfolge: cfg.items.map((_, i) => i) };
      else if (aufgabe.aufgabentyp === "freitext") st.texte["ft-" + a.aufgabe_id] = "Ein langer Satz über Bienen, der in der Karte ankommen muss. ".repeat(8);
      else if (aufgabe.aufgabentyp === "mc") st.aufgaben[a.aufgabe_id] = { gewaehlt: [0] };
      else if (aufgabe.aufgabentyp === "richtigfalsch") st.aufgaben[a.aufgabe_id] = { wahl: cfg.aussagen.map(() => "r") };
      ctx.BIE = { autosave: { collectBackup: () => st } };
      const k = (await GT.abAdapter.meineAufgaben()).find((x) => String(x.aufgabe_id) === String(a.aufgabe_id));
      karten.push(Object.assign({ n }, k));
    }
  }
  process.stdout.write(JSON.stringify({ karten, aufgaben: liste }));
})().catch((e) => { console.error(e); process.exit(1); });
