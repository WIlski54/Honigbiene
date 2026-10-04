// Logiktests für static/js/aufgaben.js ohne Browser: neutraler Standard-Hilfetext (T5), Mehrfachauswahl-Meldung, konfigurierbare Notizen (T9).
// Das Modul läuft in einer Node-Umgebung mit Attrappen für BIE und document.
// Aufruf: node --test tests/aufgaben.test.cjs   (pytest ruft das über tests/test_geruest_js.py auf)
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const QUELLE = fs.readFileSync(path.join(__dirname, "..", "static", "js", "aufgaben.js"), "utf8");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function aufbau(aufgaben, { lesestreckeFertig = false } = {}) {
  const log = { fb: [], antworten: [], fertig: [], dirty: 0 };
  const aktuell = { knoepfe: [] };               // die MC-Knöpfe, die $$(".mc-btn") gerade liefert
  const els = {};
  const feld = (id) => els[id] || (els[id] = { id, value: "", innerHTML: "", dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false } });
  const INHALTE = { tabs: [{ key: "x", lese: "L1", aufgaben }], filme: {} };
  const aufgabenByNr = {}, tabByNr = {};
  aufgaben.forEach((a) => { aufgabenByNr[a.nr] = a; tabByNr[a.nr] = INHALTE.tabs[0]; });
  const state = { runtime: {}, charts: {}, completed: new Set(lesestreckeFertig ? ["L1"] : []), niveau: {}, restoring: false };
  const niveauOf = (nr) => state.niveau[nr] || "A";
  const BIE = {
    INHALTE, state, actions: {}, beimOeffnen: {}, aufgabenByNr, tabByNr, lesestreckeNr: { x: "L1" }, NIVEAU_LABEL: { A: "A", B: "B", C: "C" }, pruefmodus: false,
    $: (sel) => (sel === ".task-question" ? { textContent: "Frage?" } : null), $$: (sel) => (sel === ".mc-btn" ? aktuell.knoepfe : []), esc, shuffle: (a) => a, normalize: (s) => String(s || "").toLowerCase(),
    isDifferenziert: (t) => !!t.niveaus, niveauOf, cfgOf: (t) => (t.niveaus ? t.niveaus[niveauOf(t.nr)] : t),
    card: () => null, body: (nr) => feld("body-" + nr),
    showFb: (nr, kind, html) => log.fb.push({ nr: String(nr), kind, html }), clearFb() {}, retryBtn: () => "",
    markComplete: (nr) => { log.fertig.push(String(nr)); state.completed.add(String(nr)); },
    sendAntwort: (...a) => log.antworten.push(a), dirty: () => { log.dirty++; }, postJSON: async () => ({}),
    anzeigeNr: (nr) => String(nr), autosave: { register() {}, flush() {} },
  };
  const document = { addEventListener() {}, getElementById: feld };
  vm.runInNewContext(QUELLE, { BIE, document, console, window: {}, setTimeout: () => 0 }, { filename: "aufgaben.js" });
  return { BIE, log, els, feld, state, aktuell };
}

// Ein MC-Block mit Knöpfen: idx 0 richtig, 1 falsch, (2 richtig, bei multi)
function mcGruppe(multi, oks) {
  const knoepfe = oks.map((ok, i) => ({ dataset: { idx: String(i), ok: String(ok) }, textContent: "Option " + i, disabled: false, classList: { add() {}, remove() {}, toggle() {} } }));
  const group = { dataset: { multi: String(multi) }, closest: () => ({}), knoepfe };
  return group;
}
function mcAuswerten(a, nr, group, gewaehlt) {
  a.aktuell.knoepfe = group.knoepfe;
  a.state.runtime[nr] = {};
  a.BIE.aufgaben.mcAuswerten(nr, group, gewaehlt, true);
}

const mc = (extra, cfg) => Object.assign({ nr: 41, typ: "mc", eyebrow: "t", titel: "t", niveaus: { A: Object.assign({ frage: "F?", optionen: [{ t: "a", ok: true }, { t: "b", ok: false }] }, cfg || {}) } }, extra || {});

// ── T5: neutraler Standard-Hilfetext ─────────────────────────────────────────
test("T5 Hilfetext: ohne cfg.hilfe NEUTRAL „Schau noch einmal genau hin.“ – auch wenn die Lesestrecke schon gelesen ist (sie enthält die Antwort oft nicht)", () => {
  const a = aufbau([mc()], { lesestreckeFertig: true });
  mcAuswerten(a, "41", mcGruppe(1, [true, false]), [1]);
  const fb = a.log.fb.at(-1);
  assert.equal(fb.kind, "err");
  assert.match(fb.html, /Schau noch einmal genau hin\./);
  assert.doesNotMatch(fb.html, /Lesestrecke/);
});

test("T5 Hilfetext: ein Verweis auf die Lesestrecke steht nur, wenn die Aufgabe ihn selbst in cfg.hilfe setzt", () => {
  const a = aufbau([mc({}, { hilfe: "Ein Blick in die Lesestrecke hilft." })]);
  mcAuswerten(a, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(a.log.fb.at(-1).html, /Ein Blick in die Lesestrecke hilft\./);
  assert.doesNotMatch(a.log.fb.at(-1).html, /Schau noch einmal/);
  const b = aufbau([mc({}, { hilfe: "   " })]);
  mcAuswerten(b, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(b.log.fb.at(-1).html, /Schau noch einmal genau hin\./, "leerer Text: Standard");
});

test("Mehrfachauswahl: „Perfekt – beide Aussagen stimmen!“ bei zwei, „alle 3 Aussagen“ bei drei richtigen", () => {
  const a = aufbau([mc({}, { multi: 2, optionen: [{ t: "a", ok: true }, { t: "b", ok: true }, { t: "c", ok: false }] })]);
  mcAuswerten(a, "41", mcGruppe(2, [true, true, false]), [0, 1]);
  assert.match(a.log.fb.at(-1).html, /Perfekt – beide Aussagen stimmen!/);
  const b = aufbau([mc({}, { multi: 3 })]);
  mcAuswerten(b, "41", mcGruppe(3, [true, true, true, false]), [0, 1, 2]);
  assert.match(b.log.fb.at(-1).html, /Perfekt – alle 3 Aussagen stimmen!/);
  assert.doesNotMatch(b.log.fb.at(-1).html, /beide/);
});

// ── F4: Anfang der Fehlermeldung ─────────────────────────────────────────────
test("F4 mc: Standard-Anfang ist neutral „Nicht ganz.“ (nicht „Leider falsch.“); falschText je Niveau oder an der Aufgabe überschreibt ihn", () => {
  const a = aufbau([mc()]);
  mcAuswerten(a, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(a.log.fb.at(-1).html, /^❌ Nicht ganz\./);
  assert.doesNotMatch(a.log.fb.at(-1).html, /Leider/);
  const b = aufbau([mc({}, { falschText: "Das war es noch nicht." })]);
  mcAuswerten(b, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(b.log.fb.at(-1).html, /^❌ Das war es noch nicht\./);
  const c = aufbau([mc({ falschText: "Hmm, nicht ganz." })]);
  mcAuswerten(c, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(c.log.fb.at(-1).html, /^❌ Hmm, nicht ganz\./);
  const d = aufbau([mc({}, { falschText: "<i>x</i>" })]);
  mcAuswerten(d, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(d.log.fb.at(-1).html, /&lt;i&gt;x&lt;\/i&gt;/, "maskiert");
  const e = aufbau([mc({}, { falschText: "  " })]);
  mcAuswerten(e, "41", mcGruppe(1, [true, false]), [1]);
  assert.match(e.log.fb.at(-1).html, /^❌ Nicht ganz\./, "leerer Text: Standard");
  // Mehrfachauswahl wie bisher
  const f = aufbau([mc({}, { multi: 2, optionen: [{ t: "a", ok: true }, { t: "b", ok: true }, { t: "c", ok: false }] })]);
  mcAuswerten(f, "41", mcGruppe(2, [true, true, false]), [0, 2]);
  assert.match(f.log.fb.at(-1).html, /^❌ Nicht ganz\./);
});

// ── T9: Notizen konfigurierbar ───────────────────────────────────────────────
const notiz = (extra) => Object.assign({ nr: 7, typ: "notizen", eyebrow: "Fragen", titel: "Meine Fragen", abschnitt: "nutztier", hinweis: "Schreibe Fragen auf." }, extra || {});
function notizRendern(a, t) { a.BIE.aufgaben.renderBody(t); return a.feld("body-" + t.nr).innerHTML; }
const fuelle = (a, stichpunkte, quelle) => { a.feld("nt-nutztier").value = stichpunkte; a.feld("nq-nutztier").value = quelle || ""; };
const abgeben = (a) => a.BIE.actions["finish-notizen"]({ dataset: { nr: "7", abschnitt: "nutztier" } });

test("T9 Notizen: Standard – Platzhalter, Quelle Pflicht („Abgabe: mindestens drei Stichpunkte und eine Quelle“)", () => {
  const t = notiz();
  const a = aufbau([t]);
  const h = notizRendern(a, t);
  assert.match(h, /placeholder="• Die Biene hat …&#10;• …"/);
  assert.match(h, /Quelle\(n\) für diesen Abschnitt \(Buch mit Seite/);
  assert.doesNotMatch(h, /freiwillig/);
  assert.match(h, /mindestens drei Stichpunkte und eine Quelle/);
  fuelle(a, "• Die Biene sammelt\n• Der Imker hilft\n• Es gibt Honig", "");
  abgeben(a);
  assert.match(a.log.fb.at(-1).html, /mindestens eine Quelle/);
  assert.equal(a.log.fertig.length, 0);
  fuelle(a, "• Die Biene sammelt\n• Der Imker hilft\n• Es gibt Honig", "Schulbuch S. 5");
  abgeben(a);
  assert.deepEqual(a.log.fertig, ["7"]);
  assert.match(a.log.antworten.at(-1)[2], /^3 Stichpunkte, 1 Quelle\(n\): /);
});

test("T9 Notizen: platzhalter und quelleNoetig: false je Aufgabe – die Quelle ist freiwillig, die Abgabe klappt ohne", () => {
  const t = notiz({ platzhalter: "• Wie viele Bienenkästen hast du?\n• Warum …?", quelleNoetig: false });
  const a = aufbau([t]);
  const h = notizRendern(a, t);
  assert.match(h, /placeholder="• Wie viele Bienenkästen hast du\?&#10;• Warum …\?"/);
  assert.match(h, /Quelle\(n\) für diesen Abschnitt \(freiwillig\)/);
  assert.match(h, /mindestens drei Stichpunkte\. Deine/);
  assert.doesNotMatch(h, /und eine Quelle/);
  fuelle(a, "• Wie viele Völker hast du?\n• Warum gibt es Drohnen?\n• Wann erntest du?", "");
  abgeben(a);
  assert.deepEqual(a.log.fertig, ["7"]);
  assert.match(a.log.fb.at(-1).html, /3 Stichpunkte abgegeben/);
  assert.doesNotMatch(a.log.fb.at(-1).html, /Quelle/);
  assert.match(a.log.antworten.at(-1)[2], /^3 Stichpunkte: /, "ohne Quelle steht keine „0 Quelle(n)“ im Protokoll");
});

test("T9 Notizen: die Einstellungen dürfen auch je Niveau stehen; min ändert die Zahl der Stichpunkte; HTML im Platzhalter wird maskiert", () => {
  const t = { nr: 7, typ: "notizen", eyebrow: "Fragen", titel: "Meine Fragen", abschnitt: "nutztier", hinweis: "x", niveaus: { A: { min: 2, quelleNoetig: false, platzhalter: "<b>Frage</b>" } } };
  const a = aufbau([t]);
  const h = notizRendern(a, t);
  assert.match(h, /mindestens zwei Stichpunkte\./);
  assert.match(h, /placeholder="&lt;b&gt;Frage&lt;\/b&gt;"/);
  fuelle(a, "• Wie viele Bienen?", "");
  abgeben(a);
  assert.match(a.log.fb.at(-1).html, /erst 1 Stichpunkt\(e\)\. Notiere mindestens zwei\./);
  fuelle(a, "• Wie viele Bienen?\n• Warum Honig?", "");
  abgeben(a);
  assert.deepEqual(a.log.fertig, ["7"]);
});
