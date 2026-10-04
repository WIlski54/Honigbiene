// Führt die Inhaltsdateien (Argumente, in Ladereihenfolge) in einer leeren Umgebung aus und gibt INHALTE als JSON aus.
const vm = require("vm");
const fs = require("fs");

const ctx = { console };
ctx.window = ctx;
vm.createContext(ctx);
for (const datei of process.argv.slice(2)) {
  vm.runInContext(fs.readFileSync(datei, "utf8"), ctx, { filename: datei });
}
process.stdout.write(JSON.stringify(ctx.INHALTE));
