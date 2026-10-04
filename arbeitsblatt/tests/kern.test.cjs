// Logiktests für Gerüst-Bausteine ohne Browser: kern.js (Stationsreihenfolge mit frei platzierter Lesestrecke, Vergleichsform
// von Eingaben), bildpunkte.js (Trefferkreise für Finger), spiele.js (Blitzfragen gleichmäßig über die Stufen).
// Aufruf: node --test tests/kern.test.cjs   (pytest ruft das über tests/test_geruest_js.py auf)
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const plain = (x) => JSON.parse(JSON.stringify(x));
const quelle = (datei) => fs.readFileSync(path.join(__dirname, "..", "static", "js", datei), "utf8");
const dom = { addEventListener() {}, getElementById: () => null, querySelector: () => null, querySelectorAll: () => [] };

function kern(tabs) {
  const ctx = { console: { log() {}, warn() {}, error() {} }, document: dom, localStorage: {}, navigator: {}, APP: {} };
  ctx.window = ctx; ctx.INHALTE = { tabs };
  vm.createContext(ctx);
  vm.runInContext(quelle("kern.js"), ctx);
  return ctx.BIE;
}

test("Stationen: die Lesestrecke steht dort, wo leseNach sie nennt – oben, mitte, am Ende; unbekannte Nummer → oben", () => {
  const BIE = kern([
    { key: "a", lese: "L1", leseNach: 2, aufgaben: [{ nr: 1 }, { nr: 2 }, { nr: 3 }] },
    { key: "b", lese: "L2", aufgaben: [{ nr: 4 }, { nr: 5 }] },
    { key: "c", lese: "L3", leseNach: "F2", aufgaben: [{ nr: "F1" }, { nr: "F2" }] },
    { key: "d", aufgaben: [{ nr: 6 }] },
    { key: "e", lese: "L4", leseNach: 99, aufgaben: [{ nr: 7 }, { nr: 8 }] },
  ]);
  const st = (k) => plain(BIE.stationenVon(BIE.INHALTE.tabs.find((t) => t.key === k)));
  assert.deepEqual(st("a"), ["1", "2", "L1", "3"]);
  assert.deepEqual(st("b"), ["L2", "4", "5"]);
  assert.deepEqual(st("c"), ["F1", "F2", "L3"]);
  assert.deepEqual(st("d"), ["6"]);
  assert.deepEqual(st("e"), ["L4", "7", "8"]);
});

test("normalize: Umlaute und ß gleichen sich an („Bestäubung“ = „Bestaeubung“), Satzzeichen und Großschreibung egal", () => {
  const { normalize: n } = kern([]);
  assert.equal(n("Bestäubung"), n("Bestaeubung"));
  assert.equal(n("Rähmchen"), n("raehmchen"));
  assert.equal(n("Rüssel"), n("RUESSEL"));
  assert.equal(n("Größe"), n("groesse"));
  assert.equal(n("Schwänzeltanz "), "schwaenzeltanz");
  assert.equal(n("„Honig“."), "honig");
  assert.equal(n("Weiß"), n("weiss"));
  assert.equal(n(null), "");
});

test("normalize: „Wieviele“ = „Wie viele“ (auch wie viel, wie vielen), sonst bleibt der Text unberührt", () => {
  const { normalize: n } = kern([]);
  assert.equal(n("Wieviele"), n("Wie viele"));
  assert.equal(n("  WIE   VIELE "), "wieviele");
  assert.equal(n("Wie viel"), n("wieviel"));
  assert.equal(n("Wie vielen Bienen?"), "wievielen bienen");
  assert.equal(n("Wieviele Bienen leben im Stock?"), n("Wie viele Bienen leben im Stock"));
  assert.equal(n("sie viele"), "sie viele", "nur „wie viel…“ wird zusammengezogen");
  assert.equal(n("Wie vieles"), "wievieles");
  assert.notEqual(n("Wie lange"), n("Wielange x"));
});

function bildpunkte() {
  const BIE = { INHALTE: { bildpunkte: {} }, APP: {}, state: { runtime: {} }, $: () => null, $$: () => [], esc: String, shuffle: (a) => a, normalize: (s) => s, cfgOf: () => ({}), body: () => null,
    showFb() {}, markComplete() {}, sendAntwort() {}, dirty() {}, aufgabenByNr: {}, actions: {}, autosave: { register() {} } };
  vm.runInNewContext(quelle("bildpunkte.js"), { BIE, document: { addEventListener() {} }, window: {}, ResizeObserver: undefined });
  return BIE.bildpunkte.logik;
}

test("Bildpunkte (Audit T10): Aliase zählen, ein typischer Fehlname bekommt seinen eigenen Satz (punkt.falsch), Richtiges geht vor", () => {
  const BIE = { INHALTE: { bildpunkte: {} }, APP: {}, state: { runtime: {} }, $: () => null, $$: () => [], esc: String, shuffle: (a) => a, normalize: (s) => String(s || "").toLowerCase().trim().replace(/[.,;:!?„“"']/g, "").replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue"),
    cfgOf: () => ({}), body: () => null, showFb() {}, markComplete() {}, sendAntwort() {}, dirty() {}, aufgabenByNr: {}, actions: {}, autosave: { register() {} } };
  vm.runInNewContext(quelle("bildpunkte.js"), { BIE, document: { addEventListener() {} }, window: {}, ResizeObserver: undefined });
  const L = BIE.bildpunkte.logik;
  const p = { id: "kasten", name: "Bienenkasten", aliase: ["Kasten", "Beute"], falsch: [{ aliase: ["Bienenstock", "Stock"], text: "Der Bienenstock ist das ganze Zuhause des Volkes. Die Holzkiste heißt …" }] };
  assert.equal(L.nameStimmt(p, "Kasten"), true);
  assert.equal(L.nameStimmt(p, "beute"), true);
  assert.equal(L.nameStimmt(p, "Bienenstock"), false);
  assert.match(L.falschText(p, "Bienenstock"), /das ganze Zuhause des Volkes/);
  assert.match(L.falschText(p, "  STOCK. "), /Holzkiste/);
  assert.equal(L.falschText(p, "Kasten"), null, "richtige Namen bekommen keinen Fehlsatz");
  assert.equal(L.falschText(p, "Haus"), null, "unbekannter Fehlname: der Standardtext genügt");
  assert.equal(L.falschText(p, ""), null);
  assert.equal(L.falschText({ id: "x", name: "Wabe" }, "Bienenstock"), null, "Punkt ohne falsch");
  assert.equal(L.falschText({ id: "x", name: "Wabe", falsch: [{ aliase: "Zelle", text: "Eine Zelle ist nur ein Fach." }] }, "zelle"), "Eine Zelle ist nur ein Fach.", "aliase darf auch ein einzelner Text sein");
  // ein Bienenstock-Alias, der zugleich richtig ist, geht vor
  assert.equal(L.falschText({ id: "y", name: "Stock", falsch: [{ aliase: ["Stock"], text: "?" }] }, "Stock"), null);
});

test("F5 Bildpunkte: der Aufgabentext (auftrag) steht über dem Bild – je Niveau oder an der Aufgabe; ohne auftrag nichts Zusätzliches", () => {
  const karte = { bild: "/static/img/lese/imker-karte.svg", breite: 900, hoehe: 560, punkte: [{ id: "a", x: 100, y: 100, name: "Kasten", kat: 0 }, { id: "b", x: 400, y: 300, name: "Imker", kat: 1 }] };
  const mit = (aufgabe) => {
    const t = Object.assign({ nr: 3, typ: "bildpunkte", karte: "imker", titel: "Beim Imker", niveaus: { A: { modus: "benennen" } } }, aufgabe);
    const BIE = { INHALTE: { bildpunkte: { imker: karte } }, APP: {}, state: { runtime: {} }, $: () => null, $$: () => [], esc: (s) => String(s).replace(/</g, "&lt;"), shuffle: (a) => a, normalize: (s) => s,
      cfgOf: (x) => x.niveaus.A, body: () => null, showFb() {}, markComplete() {}, sendAntwort() {}, dirty() {}, aufgabenByNr: { 3: t }, actions: {}, autosave: { register() {} } };
    vm.runInNewContext(quelle("bildpunkte.js"), { BIE, document: { addEventListener() {} }, window: {}, ResizeObserver: undefined });
    return BIE.bildpunkte.render(t);
  };
  assert.match(mit({ niveaus: { A: { modus: "benennen", auftrag: "Du bist zu Besuch beim Imker. Schau genau hin." } } }), /^<p class="task-question bp-auftrag">Du bist zu Besuch beim Imker\. Schau genau hin\.<\/p>/);
  assert.match(mit({ auftrag: "Aufgabentext an der Aufgabe." }), /^<p class="task-question bp-auftrag">Aufgabentext an der Aufgabe\.<\/p>/);
  assert.match(mit({ niveaus: { A: { modus: "benennen", auftrag: "<b>x" } } }), /&lt;b>x/, "maskiert");
  assert.doesNotMatch(mit({}), /bp-auftrag/);
});

test("Bildpunkte: Trefferkreis mindestens 44 px, bei dicht liegenden Punkten gewinnt der nächste", () => {
  const L = bildpunkte();
  const punkte = [{ x: 100, y: 100 }, { x: 200, y: 100 }, { x: 600, y: 300 }];
  // Handy: Bild 900 Einheiten auf 330 px → 44 px = 120 Einheiten Durchmesser = 60 Einheiten Radius
  const r = L.radien(punkte, 900, 330);
  assert.ok(Math.abs(r.hit - 60) < 0.01, `hit ${r.hit}`);
  assert.ok(r.sicht <= 48 && r.sicht >= 24, "sichtbarer Punkt: höchstens halber Abstand zum Nachbarn minus 2");
  // Tablet: Bild auf 650 px → Trefferkreis 30,5 Einheiten
  assert.ok(Math.abs(L.radien(punkte, 900, 650).hit - 30.46) < 0.1);
  // Desktop: Bild auf 900 px → Mindestradius 24 bleibt
  assert.equal(L.radien(punkte, 900, 900).hit, 24);
  // Tipp zwischen den Punkten 1 und 2, näher an Punkt 2 (Trefferkreise überlappen bei 60)
  assert.equal(L.punktAn(punkte, 160, 100, 60), 1);
  assert.equal(L.punktAn(punkte, 130, 100, 60), 0);
  assert.equal(L.punktAn(punkte, 150, 100, 60), 0, "gleich weit weg: der erste");
  assert.equal(L.punktAn(punkte, 151, 100, 60), 1);
  assert.equal(L.punktAn(punkte, 400, 100, 60), -1, "daneben: kein Punkt");
  assert.equal(L.punktAn(punkte, 600, 355, 60), 2);
  assert.equal(L.radien([punkte[0]], 900, 0).hit, 24, "Bild unsichtbar: nichts vergrößern");
});

test("Blitzfragen: jede Stufe des Niveaus kommt gleich oft dran (nicht nach Poolgröße), Rest ohne Wiederholung", () => {
  const BIE = { INHALTE: { tabs: [] }, state: { runtime: {} }, $: () => null, $$: () => [], esc: String, shuffle: (a) => a, cfgOf: () => ({}), niveauOf: () => "A", body: () => null,
    showFb() {}, clearFb() {}, markComplete() {}, sendAntwort() {}, dirty() {}, aufgabenByNr: {}, actions: {}, autosave: { register() {} } };
  vm.runInNewContext(quelle("spiele.js"), { BIE, document: { getElementById: () => null }, window: {} });
  const { naechsteFrage } = BIE.spiele.logik;
  const pool = [];
  for (let i = 0; i < 11; i++) pool.push({ id: "s1_" + i, stufe: 1 });
  for (let i = 0; i < 9; i++) pool.push({ id: "s2_" + i, stufe: 2 });
  for (let i = 0; i < 7; i++) pool.push({ id: "s3_" + i, stufe: 3 });
  let seed = 12345;
  const zufall = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
  const zaehl = { 1: 0, 2: 0, 3: 0 };
  for (let i = 0; i < 3000; i++) zaehl[naechsteFrage(pool, zufall).stufe]++;
  for (const s of [1, 2, 3]) assert.ok(zaehl[s] > 900 && zaehl[s] < 1100, `Stufe ${s}: ${zaehl[s]} von 3000 (erwartet ≈ 1000)`);
  // ist eine Stufe leer, kommen nur die übrigen dran
  const ohne3 = pool.filter((q) => q.stufe !== 3);
  for (let i = 0; i < 200; i++) assert.notEqual(naechsteFrage(ohne3, zufall).stufe, 3);
  assert.equal(naechsteFrage([pool[0]], zufall).id, "s1_0");
});
