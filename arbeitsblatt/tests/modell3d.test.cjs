// Logiktests für static/js/modell3d.js (Aufgabentypen „erkunden“ und „modellfinden“) – ohne Browser.
// Das Modul läuft in einer Node-Umgebung mit Attrappen für BIE, film.js, window und document. Geprüft wird,
// was beim Tipp des Modells ({mw:"tipp"}) passiert, welche Befehle an das Modell gehen und was gespeichert wird.
// Aufruf: node --test tests/modell3d.test.cjs   (pytest ruft das über tests/test_modell3d.py auf)
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("vm");
const fs = require("fs");
const path = require("path");

// Objekte aus der vm-Umgebung haben einen anderen Object-Prototyp – vor deepEqual in einfache Objekte umwandeln
const plain = (x) => JSON.parse(JSON.stringify(x));
const QUELLE = fs.readFileSync(path.join(__dirname, "..", "static", "js", "modell3d.js"), "utf8");

const ZIELE_A = [
  { teil: "kopf", frage: "Tippe auf den Kopf.", hinweis: "Dort sitzen die Augen.", ansicht: "gestalt" },
  { teil: "bein", frage: "Tippe auf ein Bein.", hinweis: "Es sind sechs.", ansicht: "gestalt" },
  { teil: "honigmagen", frage: "Tippe auf den Honigmagen.", hinweis: "Er liegt im Hinterleib.", ansicht: "situs" },
];

function aufbau({ ziele = ZIELE_A, gesehen = 0, besucht = [], status = { ansicht: "gestalt" }, info = null } = {}) {
  const log = { befehle: [], antworten: [], fb: [], fertig: [], dirty: 0 };
  const hoerer = [];
  const listener = {};
  const regs = {};
  const fensterModell = {};
  const iframe = { contentWindow: fensterModell, getAttribute: () => "/static/film/bienenmodell/index.html?embed=1&v=1" };
  const erkunden = { nr: 8, typ: "erkunden", film: "biene3d", titel: "Erkunden", auftrag: "Auftrag", beobachtung: ["a", "b"] };
  const finden = { nr: 9, typ: "modellfinden", film: "biene3d", titel: "Finden", niveaus: { A: { auftrag: "x", ziele } } };
  const INHALTE = {
    filme: { biene3d: { art: "modell3d", datei: "/static/film/bienenmodell/index.html?embed=1", titel: "Modell" } },
    tabs: [{ key: "koerper", aufgaben: [erkunden, finden] }],
  };
  const state = { runtime: { 8: {}, 9: {} }, completed: new Set(), restoring: false };
  const st = { v: status };   // letzte Statusmeldung des Modells (null = es hat noch nie geantwortet)
  const stationHoerer = [];
  const film = {
    befehle: (id, liste) => log.befehle.push({ id, liste }),
    status: () => st.v,
    info: () => info,                    // Meldung {mw:"info"} des Modells (null = noch keine); Feld `leiste` zeigt, dass es den Befehl `leiste` kennt
    stationHoerer,
    gesehen: () => gesehen,
    besucht: () => besucht.slice(),
    beobachten: (fn) => hoerer.push(fn),
  };
  const BIE = {
    INHALTE, state, film, actions: {}, pruefmodus: false,
    $: () => null, $$: (sel) => (sel === "#film-rahmen iframe" ? [iframe] : []),
    esc: (s) => String(s), cfgOf: (t) => (t.niveaus ? t.niveaus.A : t), niveauOf: () => "A", body: () => null,
    showFb: (nr, kind, html) => log.fb.push({ nr: String(nr), kind, html }), clearFb: () => {},
    markComplete: (nr) => { log.fertig.push(String(nr)); state.completed.add(String(nr)); },
    sendAntwort: (...a) => log.antworten.push(a), dirty: () => { log.dirty++; },
    aufgabenByNr: { 8: erkunden, 9: finden },
    autosave: { register: (name, collect, apply, order) => { regs[name] = { collect, apply, order }; } },
    aufgaben: { renderBody: () => {} },
  };
  const sandbox = {
    BIE, console, setTimeout: () => 0,
    window: { addEventListener: (ev, fn) => { listener[ev] = fn; } },
    document: { getElementById: () => null },
  };
  vm.runInNewContext(QUELLE, sandbox, { filename: "modell3d.js" });
  const m = BIE.modell3d;
  m.render(finden);
  const tipp = (teil, teile, quelle = fensterModell) => listener.message({ data: { mw: "tipp", teil, teile: teile === undefined ? (teil ? [teil] : []) : teile }, source: quelle });
  const start = () => BIE.actions["mf-start"]({ dataset: { nr: "9" } });
  return { log, BIE, m, state, tipp, start, regs, hoerer, finden, erkunden, fensterModell, st, stationHoerer };
}
const rt = (a) => a.state.runtime[9];
const letzteFb = (a) => a.log.fb[a.log.fb.length - 1];
const alleBefehle = (a) => a.log.befehle.flatMap((b) => b.liste);

test("Start schaltet den Wählmodus ein und stellt die Ansicht des Ziels ein", () => {
  const a = aufbau();
  a.start();
  const liste = alleBefehle(a);
  assert.deepEqual(plain(liste.find((b) => b.mw === "ansicht")), { mw: "ansicht", name: "gestalt" });
  assert.deepEqual(plain(liste.find((b) => b.mw === "waehlen")), { mw: "waehlen", an: true });
  assert.equal(rt(a).gestartet, true);
});

test("Richtiger Tipp: Antwort protokolliert, nächstes Ziel, Rückmeldung", () => {
  const a = aufbau();
  a.start();
  a.tipp("kopf", ["kopf"]);
  assert.equal(rt(a).index, 1);
  assert.equal(letzteFb(a).kind, "ok");
  const antwort = a.log.antworten[a.log.antworten.length - 1];
  assert.equal(antwort[1], "modellfinden");
  assert.equal(antwort[3], true);
  assert.match(antwort[2], /im ersten Versuch/);
});

test("Oberbegriff genügt: Tipp auf das Hinterbein trifft das Ziel „bein“", () => {
  const a = aufbau();
  a.start();
  a.tipp("kopf", ["facettenauge", "kopf"]);   // Facettenauge liegt im Kopf → Ziel 1 erledigt
  assert.equal(rt(a).index, 1);
  a.tipp("hinterbein", ["hinterbein", "bein", "brust"]);
  assert.equal(rt(a).index, 2, "bein ∈ teile muss genügen");
});

test("Ein Ziel mit blick: Kamerablick wird vor dem Wählmodus eingestellt (kleine Teile wie der Rüssel)", () => {
  const a = aufbau({ ziele: [{ teil: "ruessel", frage: "Tippe auf den Rüssel.", hinweis: "Er ist klein.", ansicht: "gestalt", blick: "vorn" }] });
  a.start();
  const liste = plain(alleBefehle(a));
  const iBlick = liste.findIndex((b) => b.mw === "blick");
  assert.deepEqual(liste[iBlick], { mw: "blick", name: "vorn" });
  assert.ok(iBlick < liste.findIndex((b) => b.mw === "waehlen"), "erst der Blick, dann der Wählmodus");
});

test("Facettenauge zählt für das Ziel „kopf“, wenn das Modell es so meldet (teile enthält kopf)", () => {
  const a = aufbau({ ziele: [{ teil: "kopf", frage: "Tippe auf den Kopf.", hinweis: "x" }] });
  a.start();
  a.tipp("facettenauge", ["facettenauge", "kopf"]);
  assert.equal(rt(a).fertig, true);
});

test("Falscher Tipp verrät die Lösung nicht, zeigt aber den Hinweis auf ein sichtbares Merkmal", () => {
  const a = aufbau();
  a.start();
  a.tipp("hinterleib", ["hinterleib"]);
  const fb = letzteFb(a);
  assert.equal(fb.kind, "err");
  assert.match(fb.html, /Dort sitzen die Augen\./);
  assert.match(fb.html, /den Hinterleib getippt/);
  assert.doesNotMatch(fb.html, /kopf/i, "die Rückmeldung darf das gesuchte Teil nicht nennen");
  assert.equal(rt(a).index, 0);
  assert.equal(rt(a).fehler, 1);
  assert.equal(alleBefehle(a).filter((b) => b.mw === "hervorheben").length, 0, "nach dem ersten Fehler wird noch nichts hervorgehoben");
  const antwort = a.log.antworten[a.log.antworten.length - 1];
  assert.equal(antwort[3], false);
});

test("Nach zwei Fehlversuchen kommt der Tipp: das Teil wird hervorgehoben", () => {
  const a = aufbau();
  a.start();
  a.tipp("hinterleib", ["hinterleib"]);
  a.tipp("brust", ["brust"]);
  const hervor = alleBefehle(a).filter((b) => b.mw === "hervorheben");
  assert.equal(hervor.length, 1);
  assert.deepEqual(plain(hervor[0]), { mw: "hervorheben", teile: ["kopf"], fokus: true });
  assert.match(letzteFb(a).html, /leuchtet/);
  // Richtig getippt: die Hervorhebung wird wieder aufgehoben
  a.tipp("kopf", ["kopf"]);
  const nachTipp = plain(a.log.befehle.slice(-1)[0].liste);
  assert.equal(nachTipp[0].mw, "zurueck", "beim nächsten Ziel hebt „zurueck“ die Hervorhebung auf (vor allen anderen Befehlen)");
  assert.equal(rt(a).index, 1);
  assert.equal(rt(a).fehler, 0, "der Fehlerzähler gilt je Ziel");
});

test("Tipp ins Leere (teil: null) zählt nicht als Fehlversuch", () => {
  const a = aufbau();
  a.start();
  const antwortenVorher = a.log.antworten.length;
  a.tipp(null, []);
  assert.equal(rt(a).fehler, 0);
  assert.equal(a.log.antworten.length, antwortenVorher);
  assert.equal(letzteFb(a).kind, "info");
});

test("Letztes Ziel: Station erledigt, Wählmodus wird beendet", () => {
  const a = aufbau();
  a.start();
  a.tipp("kopf");
  a.tipp("bein", ["bein"]);
  a.tipp("honigmagen", ["honigmagen", "hinterleib"]);
  assert.deepEqual(plain(a.log.fertig), ["9"]);
  assert.equal(rt(a).fertig, true);
  assert.deepEqual(plain(alleBefehle(a).filter((b) => b.mw === "waehlen").pop()), { mw: "waehlen", an: false });
  // Danach werden weitere Tipps ignoriert
  const n = a.log.antworten.length;
  a.tipp("kopf");
  assert.equal(a.log.antworten.length, n);
});

test("Ziele mit eigener Ansicht: der Wechsel wird dem Modell mitgeteilt", () => {
  const a = aufbau();
  a.start();
  a.tipp("kopf");
  a.tipp("bein");   // nächstes Ziel: honigmagen in der Ansicht „situs“
  const ansichten = alleBefehle(a).filter((b) => b.mw === "ansicht").map((b) => b.name);
  assert.equal(ansichten[ansichten.length - 1], "situs");
});

test("Meldungen fremder Fenster und vor dem Start werden ignoriert", () => {
  const a = aufbau();
  a.tipp("kopf");                      // noch nicht gestartet
  assert.equal(rt(a).index, 0);
  a.start();
  a.tipp("kopf", ["kopf"], {});        // anderes Fenster
  assert.equal(rt(a).index, 0);
});

test("Zustand im Autosave: sammeln und nach dem Neuladen wiederherstellen", () => {
  const a = aufbau();
  a.start();
  a.tipp("kopf");
  a.tipp("brust");                     // ein Fehlversuch
  const gesichert = a.regs.modell3d.collect();
  assert.deepEqual(plain(gesichert["9"]), { typ: "modellfinden", index: 1, fehler: 1, versuche: 2, fertig: false });
  // Neuladen: frische Aufgabe, dann apply()
  const b = aufbau();
  b.regs.modell3d.apply(JSON.parse(JSON.stringify(gesichert)));
  assert.equal(rt(b).index, 1);
  assert.equal(rt(b).fehler, 1);
  assert.equal(rt(b).gestartet, false, "der Wählmodus bleibt aus, bis „Weiter im Modell“ gedrückt wird");
  b.start();
  b.tipp("bein");
  assert.equal(rt(b).index, 2);
  // Abgeschlossen speichern und wiederherstellen
  b.tipp("honigmagen");
  const fertig = plain(b.regs.modell3d.collect());
  const c = aufbau();
  c.regs.modell3d.apply(fertig);
  assert.equal(rt(c).fertig, true);
});

test("Kaputter oder fremder Autosave-Stand bricht nichts", () => {
  const a = aufbau();
  a.regs.modell3d.apply({ 9: { index: "x", fehler: -5 }, 77: { index: 3 }, 8: { index: 1 } });
  assert.equal(rt(a).index, 0);
  a.regs.modell3d.apply(undefined);
});

test("Erkunden: Station erledigt ab 95 % Fortschritt des Modells", () => {
  const unter = aufbau({ gesehen: 67, besucht: ["gestalt", "situs"] });
  unter.hoerer.forEach((fn) => fn("biene3d", {}));
  assert.deepEqual(plain(unter.log.fertig), []);
  const fertig = aufbau({ gesehen: 100, besucht: ["gestalt", "situs", "explosion"] });
  fertig.hoerer.forEach((fn) => fn("biene3d", {}));
  assert.deepEqual(plain(fertig.log.fertig), ["8"]);
  assert.equal(fertig.log.antworten[0][1], "erkunden");
  assert.match(fertig.log.antworten[0][2], /100 %/);
  // nur einmal
  fertig.hoerer.forEach((fn) => fn("biene3d", {}));
  assert.deepEqual(plain(fertig.log.fertig), ["8"]);
});

test("Antwortet das Modell nicht, wird der Start später wiederholt, sobald es sich meldet", () => {
  const a = aufbau({ status: null });
  a.start();
  assert.equal(rt(a).wartet, true);
  const vorher = alleBefehle(a).length;
  a.st.v = { ansicht: "gestalt" };   // das Modell meldet sich endlich
  a.hoerer.forEach((fn) => fn("biene3d", {}));
  assert.equal(rt(a).wartet, false);
  assert.ok(alleBefehle(a).length > vorher, "Befehle müssen noch einmal gesendet werden");
});

test("Vor jedem Ziel geht „zurueck“ voraus (Reste anderer Aufgaben), dann Ansicht, Blick, fokus, waehlen – in dieser Reihenfolge", () => {
  const a = aufbau({ ziele: [{ teil: "ruessel", frage: "Tippe auf den Rüssel.", hinweis: "Er ist klein.", ansicht: "gestalt", blick: "vorn", fokus: { teile: ["ruessel"], blick: "vorn" } },
                             { teil: "stachel", frage: "Tippe auf den Stachel.", hinweis: "Er liegt hinten.", ansicht: "situs", fokus: { teile: ["stachel"] } }] });
  a.start();
  let liste = plain(a.log.befehle.slice(-1)[0].liste);
  assert.deepEqual(liste.map((b) => b.mw), ["zurueck", "ansicht", "blick", "fokus", "waehlen"]);
  assert.deepEqual(liste[3], { mw: "fokus", teile: ["ruessel"], blick: "vorn" });
  a.tipp("ruessel", ["ruessel"]);
  liste = plain(a.log.befehle.slice(-1)[0].liste);
  assert.deepEqual(liste.map((b) => b.mw), ["zurueck", "ansicht", "fokus", "waehlen"], "zweites Ziel: ohne blick");
  assert.deepEqual(liste[2], { mw: "fokus", teile: ["stachel"] }, "kein blick-Feld, wenn keiner angegeben ist");
});

test("F2 fokus mit abstand: der Befehl trägt `abstand` mit (Fühler/Facettenauge füllen sonst die Bühne); ungültige Werte werden weggelassen", () => {
  const ziel = (abstand) => ({ teil: "fuehler", frage: "Tippe auf einen Fühler.", hinweis: "x", ansicht: "gestalt", fokus: { teile: ["fuehler"], blick: "oben", abstand } });
  const fokusBefehl = (abstand) => { const a = aufbau({ ziele: [ziel(abstand)] }); a.start(); return plain(alleBefehle(a).find((b) => b.mw === "fokus")); };
  assert.deepEqual(fokusBefehl(2.5), { mw: "fokus", teile: ["fuehler"], blick: "oben", abstand: 2.5 });
  assert.deepEqual(fokusBefehl(undefined), { mw: "fokus", teile: ["fuehler"], blick: "oben" }, "ohne abstand: wie bisher");
  [0, -1, "2", NaN, Infinity, null].forEach((x) => assert.equal("abstand" in fokusBefehl(x), false, `abstand ${String(x)} wird nicht gesendet`));
  // ohne blick, nur mit abstand
  const a = aufbau({ ziele: [{ teil: "fuehler", frage: "x", hinweis: "x", fokus: { teile: ["fuehler"], abstand: 3 } }] });
  a.start();
  assert.deepEqual(plain(alleBefehle(a).find((b) => b.mw === "fokus")), { mw: "fokus", teile: ["fuehler"], abstand: 3 });
});

test("Ohne fokus im Ziel wird kein fokus-Befehl geschickt; der Hinweistext nennt den Knopf nicht mehr „unten“", () => {
  const a = aufbau();
  a.start();
  assert.ok(!alleBefehle(a).some((b) => b.mw === "fokus"));
  assert.doesNotMatch(QUELLE, /Tippe unten auf/, "der Knopf „Los“ steht nicht immer unten");
});

// ── Bedienleiste des Modells (Befehl `leiste`) ───────────────────────────────
test("leiste: kennt das Modell den Befehl nicht (kein Feld `leiste` in info/status), wird nichts geschickt", () => {
  const a = aufbau();
  a.start();
  assert.ok(!alleBefehle(a).some((b) => b.mw === "leiste"));
  a.tipp("kopf", ["kopf"]); a.tipp("bein", ["bein"]); a.tipp("honigmagen", ["honigmagen"]);
  assert.ok(!alleBefehle(a).some((b) => b.mw === "leiste"), "auch am Ende nicht");
  const b = aufbau({ info: { mw: "info", art: "modell3d" } });
  b.start();
  assert.ok(!alleBefehle(b).some((b2) => b2.mw === "leiste"), "info ohne Feld `leiste`");
});

test("leiste: beim Start eines Ziels aus (nach zurueck, vor ansicht/waehlen), bei jedem nächsten Ziel wieder aus, am Ende der Station wieder an", () => {
  const a = aufbau({ info: { mw: "info", leiste: true } });
  a.start();
  let liste = plain(a.log.befehle.slice(-1)[0].liste);
  assert.deepEqual(liste.map((b) => b.mw), ["zurueck", "leiste", "ansicht", "waehlen"]);
  assert.deepEqual(liste[1], { mw: "leiste", an: false });
  a.tipp("kopf", ["kopf"]);
  liste = plain(a.log.befehle.slice(-1)[0].liste);
  assert.deepEqual(liste[1], { mw: "leiste", an: false }, "nächstes Ziel: wieder ausgeblendet");
  a.tipp("bein", ["bein"]);
  a.tipp("honigmagen", ["honigmagen"]);
  assert.equal(rt(a).fertig, true);
  const ende = plain(a.log.befehle.slice(-1)[0].liste);
  assert.deepEqual(ende.slice(-2), [{ mw: "waehlen", an: false }, { mw: "leiste", an: true }], "am Ende: Wählmodus aus, Leiste wieder an");
});

test("leiste: auch das Feld `leiste` im Status genügt (false = gerade ausgeblendet); „Noch einmal“ blendet die Leiste wieder ein", () => {
  const a = aufbau({ status: { ansicht: "gestalt", leiste: false } });
  a.start();
  assert.deepEqual(plain(a.log.befehle.slice(-1)[0].liste)[1], { mw: "leiste", an: false });
  a.BIE.actions["mf-reset"]({ dataset: { nr: "9" } });
  assert.deepEqual(plain(a.log.befehle.slice(-1)[0].liste).filter((b) => b.mw === "leiste"), [{ mw: "leiste", an: true }]);
});

test("leiste: verlässt das Kind die Station mitten in einem Ziel, geht der Wählmodus aus und die Leiste wieder an; die eigene Station löst nichts aus", () => {
  const a = aufbau({ info: { mw: "info", leiste: true } });
  a.start();
  assert.equal(a.stationHoerer.length, 1);
  const n = a.log.befehle.length;
  a.stationHoerer[0]("koerper", "9");                     // dieselbe Station: nichts
  assert.equal(a.log.befehle.length, n);
  a.stationHoerer[0]("koerper", "55");                    // andere Station
  const liste = plain(a.log.befehle.slice(-1)[0].liste);
  assert.deepEqual(liste.slice(-2), [{ mw: "waehlen", an: false }, { mw: "leiste", an: true }]);
  assert.equal(rt(a).gestartet, false, "beim Zurückkommen beginnt es wieder mit „Los“");
  const m = a.log.befehle.length;
  a.stationHoerer[0]("koerper", "56");                    // kein Ziel mehr aktiv: nichts
  assert.equal(a.log.befehle.length, m);
});
