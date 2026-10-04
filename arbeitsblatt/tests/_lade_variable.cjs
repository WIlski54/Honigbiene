// Führt Skripte in einer leeren Umgebung aus und gibt window.<Name> als JSON aus.
// Aufruf: node _lade_variable.cjs <Name> <datei.js> [<datei.js> …]
const vm = require("vm");
const fs = require("fs");

const [name, ...dateien] = process.argv.slice(2);
const ctx = { console, window: {} };
vm.createContext(ctx);
for (const datei of dateien) vm.runInContext(fs.readFileSync(datei, "utf8"), ctx, { filename: datei });
process.stdout.write(JSON.stringify(ctx.window[name]));
