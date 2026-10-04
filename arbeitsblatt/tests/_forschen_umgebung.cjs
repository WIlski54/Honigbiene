// Gemeinsame Umgebung für die Node-Tests von static/js/forschen.js: BIE-Attrappe, document-Attrappe, Fixtures.
// Benutzt von tests/forschen.test.cjs (Fixtures) und tests/_forschen_echt.cjs (echte Inhalte).
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const plain = (x) => JSON.parse(JSON.stringify(x));
const QUELLE = fs.readFileSync(path.join(__dirname, "..", "static", "js", "forschen.js"), "utf8");

function fixtures() {
  const ctx = { window: {} };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, "fixtures_forschen.js"), "utf8"), ctx);
  return plain(ctx.window.FORSCHEN_FIXTURES);
}

// Baut BIE-Attrappe + lädt forschen.js. pruef = Prüfmodus der Lehrkraft.
// sofortFaerben (Standard true): tabelle/protokoll färben schon bei der ersten Prüfung (cfg.sofortFaerben) – die älteren Tests prüfen genau das.
// Die Tests zu „Raten verhindern“ (Audit T3) setzen sofortFaerben: false und prüfen das neue Standardverhalten.
// knopf: true → BIE.film.knopf ist vorhanden (wie in film.js) und merkt sich die Knöpfe in log.knoepfe; sonst gilt der Rückfall BIE.film.befehle.
function aufbau({ pruef = false, niveau = {}, mut = null, inhalte = null, sofortFaerben = true, knopf = false } = {}) {
  const F = inhalte ? { tabs: inhalte.tabs } : fixtures();     // inhalte: echte Inhalte (INHALTE) statt der Fixtures
  if (sofortFaerben) F.tabs.forEach((tab) => tab.aufgaben.forEach((a) => { if (a.typ === "protokoll" || a.typ === "tabelle") Object.values(a.niveaus || {}).forEach((c) => { if (c && c.sofortFaerben === undefined) c.sofortFaerben = true; }); }));
  if (mut) mut(F);
  const log = { antworten: [], fb: [], fertig: [], dirty: 0, befehle: [], toasts: [], neu: [], knoepfe: [] };
  const els = {}, listener = {}, regs = {}, actions = {};
  const fake = (id) => els[id] || (els[id] = { id, innerHTML: "", value: "", dataset: {}, disabled: false, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    setAttribute() {}, focus() {}, closest: () => null, contains: () => false, remove() {}, dispatchEvent() {} });
  const INHALTE = {
    titel: "Testarbeitsblatt",
    filme: inhalte ? inhalte.filme : { biene3d: { art: "modell3d", datei: "/x.html", titel: "Modell" }, volk: { art: "papiertheater", datei: "/y.html", titel: "Film" } },
    tabs: F.tabs,
  };
  const aufgabenByNr = {};
  INHALTE.tabs.forEach((tab) => tab.aufgaben.forEach((a) => { aufgabenByNr[a.nr] = a; }));
  const state = { runtime: {}, completed: new Set(), niveau: Object.assign({}, niveau), restoring: false };
  const niveauOf = (nr) => state.niveau[nr] || "A";
  const BIE = {
    INHALTE, state, actions, pruefmodus: pruef, APP: { pseudonym: "Testkind", klasse: "6a", assetVersion: "1", fach: "NW · Klasse 6" },
    $: () => null, $$: () => [], esc: (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])),
    cfgOf: (t) => (t.niveaus ? t.niveaus[niveauOf(t.nr)] : t), niveauOf, body: (nr) => fake("body-" + nr), card: () => null,
    showFb: (nr, kind, html) => log.fb.push({ nr: String(nr), kind, html }), clearFb: (nr) => log.fb.push({ nr: String(nr), kind: "clear", html: "" }),
    markComplete: (nr) => { log.fertig.push(String(nr)); state.completed.add(String(nr)); },
    sendAntwort: (nr, typ, text, korrekt, frage, max) => log.antworten.push({ nr: String(nr), typ, text, korrekt, frage, max }),
    dirty: () => { log.dirty++; }, aufgabenByNr,
    showToast: (t) => log.toasts.push(t), beimOeffnen: {},
    autosave: { register: (name, collect, apply, order) => { regs[name] = { collect, apply, order }; } },
    aufgaben: { renderBody: (t) => { log.neu.push(String(t.nr)); } },
    film: Object.assign({ befehle: (id, liste) => log.befehle.push({ id, liste }) }, knopf ? { knopf: (k) => log.knoepfe.push(k) } : {}),
  };
  const document = { getElementById: fake, addEventListener: (ev, fn) => { (listener[ev] = listener[ev] || []).push(fn); },
    createElement: () => fake("tmp"), body: { appendChild() {}, classList: { add() {}, remove() {} } }, activeElement: null, execCommand: () => true };
  const sandbox = { BIE, console, document, window: { addEventListener() {}, removeEventListener() {}, print() {} }, navigator: {}, setTimeout: (fn) => 0,
    Event: class { constructor(t) { this.type = t; } }, Intl, Date };
  vm.runInNewContext(QUELLE, sandbox, { filename: "forschen.js" });
  const fo = BIE.forschen;
  const nr = (n) => aufgabenByNr[n];
  const el = (data, extra) => Object.assign({ dataset: Object.fromEntries(Object.entries(data).map(([k, v]) => [k, String(v)])), closest: () => ({ classList: { add() {}, remove() {}, toggle() {} } }), classList: { add() {}, remove() {}, toggle() {} } }, extra || {});
  const act = (name, data) => actions[name](el(data));
  const html = (n) => (els["fo-" + n] ? els["fo-" + n].innerHTML : "");
  const zeige = (n) => { const t = nr(n); els["fo-" + n] = fake("fo-" + n); els["fo-" + n].innerHTML = fo.render(t).replace(/^<div[^>]*>/, "").replace(/<\/div>$/, ""); };
  const letzteFb = () => log.fb.filter((f) => f.kind !== "clear").slice(-1)[0];
  // Eingabe in ein Feld: alle input-Hörer des Moduls bekommen das Ereignis (jeder reagiert nur auf sein data-fo-input)
  const input = (dataset, value) => (listener.input || []).forEach((fn) => fn({ target: { value, dataset } }));
  return { F, log, els, listener, regs, actions, BIE, fo, state, nr, el, act, input, html, zeige, letzteFb, INHALTE, logik: fo.logik, D: () => plain(fo.daten) };
}

module.exports = { aufbau, fixtures, plain };
