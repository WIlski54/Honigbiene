// Prüft, ob jede übergebene Datei als klassisches Browser-Skript (nicht als Modul) syntaktisch gültig ist.
const vm = require("vm");
const fs = require("fs");
let fehler = 0;
for (const datei of process.argv.slice(2)) {
  try {
    new vm.Script(fs.readFileSync(datei, "utf8"), { filename: datei });
  } catch (e) {
    fehler++;
    console.error(datei + ": " + e.message);
  }
}
process.exit(fehler ? 1 : 0);
