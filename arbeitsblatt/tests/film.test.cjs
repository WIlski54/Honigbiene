// Logiktests für static/js/film.js (Knöpfe in Aufgaben) – ohne Browser, mit Attrappen für BIE, DOM und window.
// Geprüft wird (Audit 4. Oktober 2026): Film-Knöpfe SPIELEN SOFORT (T1), Bild-Knopf (T1), Pflicht-Sperre mit ALLEN Pflicht-Knöpfen
// und mindestens 3 s Wiedergabe (T7), Film-Karte mit laufendem Balken (T6), Stationswechsel-Hörer.
// Aufruf: node --test tests/film.test.cjs   (pytest ruft das über tests/test_geruest_js.py auf)
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const plain = (x) => JSON.parse(JSON.stringify(x));
const QUELLE = fs.readFileSync(path.join(__dirname, "..", "static", "js", "film.js"), "utf8");

// ── Mini-DOM ─────────────────────────────────────────────────────────────────
function el(tag) {
  const e = {
    tag, children: [], parentNode: null, innerHTML: "", textContent: "", className: "", dataset: {}, hidden: false, attrs: {}, style: {}, contentWindow: null,
    classList: {
      _s: new Set(), add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); }, contains(c) { return this._s.has(c); },
      toggle(c, f) { const an = f === undefined ? !this._s.has(c) : !!f; if (an) this._s.add(c); else this._s.delete(c); return an; },
    },
    setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k]; }, scrollIntoView() {},
    _l: {}, addEventListener(ev, fn) { (this._l[ev] = this._l[ev] || []).push(fn); },
    appendChild(c) { this.children.push(c); c.parentNode = this; return c; },
    append(...cs) { cs.forEach((c) => this.appendChild(c)); },
    prepend(c) { this.children.unshift(c); c.parentNode = this; },
    insertBefore(n, ref) { const i = this.children.indexOf(ref); this.children.splice(i < 0 ? this.children.length : i, 0, n); n.parentNode = this; },
    after(n) { const p = this.parentNode; if (!p) return; const i = p.children.indexOf(this); p.children.splice(i + 1, 0, n); n.parentNode = p; },
    remove() { const p = this.parentNode; if (p) p.children.splice(p.children.indexOf(this), 1); this.parentNode = null; },
    querySelector(sel) {
      const klasse = sel.startsWith(".") ? sel.slice(1) : null;
      const suche = (n) => { for (const c of n.children) { if (klasse && (c.className || "").split(/\s+/).includes(klasse)) return c; const r = suche(c); if (r) return r; } return null; };
      return suche(this);
    },
  };
  return e;
}

function aufbau({ pruef = false, tabs } = {}) {
  const log = { gesendet: [], toasts: [], antworten: [], fb: [], fertig: [], bilder: [], dirty: 0, beobachter: [] };
  const timers = [];
  let jetzt = 0;
  const fake = {};
  const get = (id) => fake[id] || (fake[id] = Object.assign(el("div"), { id }));
  const panels = el("div"); panels.parentNode = el("div");
  fake.panels = panels;
  const iframes = [];
  const window = {
    innerWidth: 1400, _l: {},
    addEventListener(ev, fn) { (this._l[ev] = this._l[ev] || []).push(fn); },
    dispatch(ev, e) { (this._l[ev] || []).forEach((fn) => fn(e)); },
  };
  const document = {
    body: el("body"), getElementById: get,
    createElement: (tag) => {
      const e = el(tag);
      if (tag === "iframe") { e.contentWindow = { postMessage: (m) => log.gesendet.push({ fenster: e, m }) }; iframes.push(e); }
      return e;
    },
  };
  const INHALTE = {
    filme: { volk: { art: "papiertheater", datei: "/static/film/volk.html", titel: "Volk" }, biene3d: { art: "modell3d", datei: "/static/film/modell.html", titel: "Modell" } },
    tabs: tabs || [{ key: "volk", aufgaben: [
      { nr: 18, typ: "film", film: "volk", titel: "Film ansehen" },
      { nr: 64, typ: "pruefen", titel: "Prüfen", modell: [
        { film: "volk", text: "▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)", befehle: [{ mw: "springe", t: 90 }], pflicht: true },
        { film: "volk", text: "Kapitel 7 ansehen", befehle: [{ mw: "kapitel", n: 7 }], pflicht: true },
        { bild: "/static/img/lese/nutzen-5-raetsel.svg", text: "Bild noch einmal ansehen", alt: "Das Rätselbild" },
      ] },
      { nr: 65, typ: "mc", titel: "Ein Knopf, kein Pflichtknopf", modell: { film: "volk", text: "Kapitel 2", befehle: [{ mw: "kapitel", n: 2 }] } },
      { nr: 66, typ: "mc", titel: "Modell", modell: { film: "biene3d", text: "Im Modell", befehle: [{ mw: "blick", name: "seite" }], pflicht: true } },
      { nr: 67, typ: "mc", titel: "Bild-Pflicht", modell: { bild: "/static/img/lese/x.svg", text: "Bild", alt: "Bild X", pflicht: true } },
      { nr: 68, typ: "mc", titel: "Nur Sprung", modell: { film: "volk", text: "Ohne Abspielen", befehle: [{ mw: "kapitel", n: 3 }], spielen: false } },
    ] }],
  };
  const aufgabenByNr = {}, tabByNr = {};
  INHALTE.tabs.forEach((tab) => tab.aufgaben.forEach((a) => { aufgabenByNr[a.nr] = a; tabByNr[a.nr] = tab; }));
  const state = { runtime: {}, completed: new Set(), restoring: false, activeTab: "volk" };
  const regs = {};
  const BIE = {
    INHALTE, state, APP: { assetVersion: "7" }, pruefmodus: pruef, actions: {}, beimOeffnen: {}, aufgabenByNr, tabByNr,
    $: (sel, root) => (root ? root.querySelector(sel) : sel.startsWith("#") ? get(sel.slice(1)) : null),
    $$: () => [], esc: (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])),
    cfgOf: (t) => (t.niveaus ? t.niveaus.A : t), niveauOf: () => "A",
    body: (nr) => get("body-" + nr), card: () => null,
    showFb: (nr, kind, html) => log.fb.push({ nr: String(nr), kind, html }), clearFb() {},
    markComplete: (nr) => { log.fertig.push(String(nr)); state.completed.add(String(nr)); },
    sendAntwort: (...a) => log.antworten.push(a), dirty: () => { log.dirty++; },
    showToast: (t) => log.toasts.push(t),
    autosave: { register: (name, collect, apply, order) => { regs[name] = { collect, apply, order }; } },
    bild: { oeffnen: (src, alt, ausloeser) => log.bilder.push({ src, alt, ausloeser }) },
  };
  const sandbox = {
    BIE, console, window, document,
    setTimeout: (fn, ms) => { timers.push({ fn, an: jetzt + (ms || 0) }); return timers.length; },
  };
  vm.runInNewContext(QUELLE, sandbox, { filename: "film.js" });
  const film = BIE.film;
  const warten = (ms) => {
    const ende = jetzt + ms;
    for (;;) {
      const f = timers.filter((t) => !t.fertig && t.an <= ende).sort((a, b) => a.an - b.an)[0];
      if (!f) break;
      f.fertig = true; jetzt = Math.max(jetzt, f.an); f.fn();
    }
    jetzt = ende;
  };
  const fensterVon = (id) => iframes.find((f) => (f.src || "").startsWith(INHALTE.filme[id].datei)).contentWindow;
  const status = (id, d) => window.dispatch("message", { data: Object.assign({ mw: "status", t: 0, laeuft: false, gesehen: 0, freigeschaltet: false }, d), source: fensterVon(id) });
  const infoMelden = (id) => window.dispatch("message", { data: { mw: "info", art: INHALTE.filme[id].art }, source: fensterVon(id) });
  const laden = (id) => iframes.find((f) => (f.src || "").startsWith(INHALTE.filme[id].datei))._l.load.forEach((fn) => fn());   // das load-Ereignis des iframes
  // spielt eine Weile ab: je 250 ms eine Meldung, t läuft mit
  const spielen = (id, von, sekunden) => { for (let t = von; t <= von + sekunden + 1e-9; t += 0.25) status(id, { t: Math.round(t * 10) / 10, laeuft: true }); };
  const knopfEl = (nr, i) => ({ dataset: { nr: String(nr), i: String(i) } });
  const druecke = (nr, i) => BIE.actions["film-knopf"](knopfEl(nr, i));
  const zeichne = (nr) => { const t = aufgabenByNr[nr]; if (t.typ === "film") get("body-" + nr); film.nachRender(t); };
  const sperre = (nr) => get("body-" + nr).classList.contains("film-gesperrt");
  const schild = (nr) => { const s = get("body-" + nr).querySelector(".film-sperre"); return s ? s.textContent : null; };
  const leiste = (nr) => get("body-" + nr).querySelector(".film-knoepfe");
  const nachrichten = (id) => log.gesendet.filter((g) => iframes.length && g.fenster.src.startsWith(INHALTE.filme[id].datei)).map((g) => g.m);
  return { log, BIE, film, state, regs, window, warten, status, infoMelden, laden, spielen, druecke, zeichne, sperre, schild, leiste, nachrichten, fensterVon, get, aufgabenByNr, iframes };
}

// ── T1: Film-Knöpfe spielen sofort ───────────────────────────────────────────
test("befehleFuer: kapitel/springe → spielen wird angehängt; spielen: false, eigenes spielen/anhalten, 3D-Modell und Bild bleiben unverändert", () => {
  const a = aufbau();
  const f = (k) => plain(a.film.befehleFuer(k));
  assert.deepEqual(f({ film: "volk", befehle: [{ mw: "kapitel", n: 5 }] }), [{ mw: "kapitel", n: 5 }, { mw: "spielen" }]);
  assert.deepEqual(f({ film: "volk", befehle: [{ mw: "springe", t: 163.5 }] }), [{ mw: "springe", t: 163.5 }, { mw: "spielen" }]);
  assert.deepEqual(f({ film: "volk", befehle: [{ mw: "kapitel", n: 5 }], spielen: false }), [{ mw: "kapitel", n: 5 }], "spielen: false schaltet es ab");
  assert.deepEqual(f({ film: "volk", befehle: [{ mw: "springe", t: 3 }, { mw: "spielen" }] }), [{ mw: "springe", t: 3 }, { mw: "spielen" }], "schon vorhanden: nicht doppelt");
  assert.deepEqual(f({ film: "volk", befehle: [{ mw: "springe", t: 3 }, { mw: "anhalten" }] }), [{ mw: "springe", t: 3 }, { mw: "anhalten" }], "wer selbst anhält, spielt nicht");
  assert.deepEqual(f({ film: "volk", befehle: [], spielen: true }), [{ mw: "spielen" }], "spielen: true erzwingt es");
  assert.deepEqual(f({ film: "biene3d", befehle: [{ mw: "blick", name: "seite" }] }), [{ mw: "blick", name: "seite" }], "das 3D-Modell spielt nichts");
  assert.deepEqual(f({ bild: "/x.svg", text: "Bild" }), [], "Bild-Knopf: keine Befehle");
});

// Ein Film, der sich schon gemeldet hat (iframe geladen, Skript läuft): zeige() legt den iframe an, der Film meldet sich
function bereiterFilm(a, id = "volk") { a.film.zeige(id); a.laden(id); a.status(id, { t: 0, laeuft: false }); }
const befehleAn = (a, id = "volk") => plain(a.nachrichten(id)).filter((m) => ["kapitel", "springe", "spielen", "anhalten", "blick"].includes(m.mw));

test("Ein Film-Knopf springt UND spielt: kapitel, dann spielen (in dieser Reihenfolge), der Film wird gezeigt", () => {
  const a = aufbau();
  bereiterFilm(a);
  a.zeichne(65);
  a.druecke(65, 0);
  a.warten(1000);
  assert.deepEqual(befehleAn(a), [{ mw: "kapitel", n: 2 }, { mw: "spielen" }]);
  a.druecke(65, 0);
  a.warten(1000);
  assert.equal(befehleAn(a).length, 4);
});

test("Ein Knopf mit spielen: false springt nur", () => {
  const a = aufbau();
  bereiterFilm(a);
  a.zeichne(68);
  a.druecke(68, 0);
  a.warten(1000);
  assert.deepEqual(befehleAn(a), [{ mw: "kapitel", n: 3 }]);
});

test("Startet der Film nicht (Browser blockt den Ton), erscheint der Hinweis „Tippe im Filmfenster auf ▶“ – läuft er, nicht", () => {
  const a = aufbau();
  bereiterFilm(a);
  a.zeichne(65);
  a.druecke(65, 0); a.warten(500);
  assert.equal(a.log.toasts.length, 0, "noch nicht abgewartet");
  a.warten(1500);
  assert.match(a.log.toasts.at(-1), /Tippe im Filmfenster auf ▶/);
  const b = aufbau();
  bereiterFilm(b);
  b.zeichne(65);
  b.druecke(65, 0); b.warten(300); b.status("volk", { t: 20, laeuft: true }); b.warten(2000);
  assert.equal(b.log.toasts.length, 0, "läuft: kein Hinweis");
});

// ── F1: der erste Klick nach dem Laden geht nicht verloren ───────────────────
test("F1 Erster Klick: ein gerade erzeugter Film hört noch nicht zu – die Befehle warten auf seine erste Meldung und gehen dann in der alten Reihenfolge raus", () => {
  const a = aufbau();
  a.zeichne(65);
  a.druecke(65, 0);                                // iframe wird gerade erst angelegt, das Skript des Films läuft noch nicht
  a.warten(3000);
  assert.deepEqual(befehleAn(a), [], "vor dem ersten Kontakt wird NICHTS geschickt (es ginge verloren)");
  assert.equal(a.film.bereit("volk"), false);
  a.laden("volk");                                 // load-Ereignis allein genügt noch nicht
  a.warten(1000);
  assert.deepEqual(befehleAn(a), []);
  a.status("volk", { t: 0, laeuft: false });       // erste Meldung des Films: jetzt hört er zu
  assert.equal(a.film.bereit("volk"), true);
  a.warten(1000);
  assert.deepEqual(befehleAn(a), [{ mw: "kapitel", n: 2 }, { mw: "spielen" }]);
});

test("F1 Auch die erste info-Meldung gilt als Kontakt; zwei Klicks vor dem Kontakt gehen beide raus (in der Reihenfolge der Klicks)", () => {
  const a = aufbau();
  a.zeichne(65); a.zeichne(68);
  a.druecke(65, 0);
  a.druecke(68, 0);
  a.warten(500);
  assert.deepEqual(befehleAn(a), []);
  a.infoMelden("volk");
  a.warten(2000);
  assert.deepEqual(befehleAn(a), [{ mw: "kapitel", n: 2 }, { mw: "spielen" }, { mw: "kapitel", n: 3 }]);
});

test("F1 Nach dem Kontakt geht jeder Befehl sofort (ohne Puffer); info wird nicht bei jeder Statusmeldung erneut angefragt", () => {
  const a = aufbau();
  bereiterFilm(a);
  a.zeichne(65);
  a.druecke(65, 0);
  a.warten(400);
  assert.deepEqual(befehleAn(a), [{ mw: "kapitel", n: 2 }, { mw: "spielen" }], "schon nach 400 ms");
  const infos = () => plain(a.nachrichten("volk")).filter((m) => m.mw === "info").length;
  const vorher = infos();
  a.status("volk", { t: 2, laeuft: true }); a.status("volk", { t: 2.25, laeuft: true });
  assert.equal(infos(), vorher);
});

test("F1 Rückfall: meldet sich der Film nie, werden die Befehle nach dem Laden + 6 s trotzdem gesendet (nichts hängt ewig)", () => {
  const a = aufbau();
  a.zeichne(65);
  a.druecke(65, 0);
  a.laden("volk");
  a.warten(5000);
  assert.deepEqual(befehleAn(a), []);
  a.warten(2000);
  assert.deepEqual(befehleAn(a), [{ mw: "kapitel", n: 2 }, { mw: "spielen" }]);
  assert.equal(a.film.bereit("volk"), true);
});

test("F1 Der Hinweis „Tippe im Filmfenster auf ▶“ erscheint nicht, solange der Film noch gar nicht angesprochen wurde", () => {
  const a = aufbau();
  a.zeichne(65);
  a.druecke(65, 0);
  a.warten(4000);
  assert.equal(a.log.toasts.length, 0, "noch kein Kontakt: kein Hinweis");
  a.status("volk", { t: 0, laeuft: false });
  a.warten(2000);
  assert.equal(a.log.toasts.length, 1, "nach dem Kontakt und gut 1,3 s ohne Wiedergabe: Hinweis");
  assert.match(a.log.toasts[0], /Tippe im Filmfenster auf ▶/);
});

test("F1 Auch die Film-Karte („Film abspielen“) wartet auf den ersten Kontakt; der Hinweis kommt erst danach", () => {
  const a = aufbau();
  a.zeichne(18);
  a.BIE.actions["film-spielen"]({ dataset: { nr: "18" } });
  a.warten(3000);
  assert.deepEqual(befehleAn(a), []);
  assert.equal(a.log.fb.filter((f) => f.nr === "18").length, 0, "kein „Tippe auf ▶“ vor dem Kontakt");
  a.status("volk", { t: 0, laeuft: false });
  a.warten(1200);
  assert.deepEqual(befehleAn(a), [{ mw: "spielen" }]);
  assert.match(a.log.fb.at(-1).html, /Tippe im Filmfenster auf ▶/);
});

test("Bild-Knopf: öffnet das Bild im Bild-Fenster (mit alt und Versionsmarke), zählt sofort als erfüllt, steht in der Leiste mit 🖼️", () => {
  const a = aufbau();
  a.zeichne(64);
  assert.match(a.leiste(64).innerHTML, /🖼️ Bild noch einmal ansehen/);
  a.druecke(64, 2);
  assert.deepEqual(plain(a.log.bilder.map((b) => [b.src, b.alt])), [["/static/img/lese/nutzen-5-raetsel.svg?v=7", "Das Rätselbild"]]);
  assert.equal(a.nachrichten("volk").length, 0, "kein Film wird angefasst");
  assert.match(a.leiste(64).innerHTML, /✅ 🖼️ Bild noch einmal ansehen/);
  // Pflicht-Bild-Knopf löst die Sperre mit dem Druck
  const b = aufbau();
  b.zeichne(67);
  assert.equal(b.sperre(67), true);
  assert.match(b.schild(67), /Stelle im Bild/);
  b.druecke(67, 0);
  assert.equal(b.sperre(67), false);
});

test("Knopflisten: jeder Knopf einer Liste steht in der Leiste, Beschriftung unverändert (mit Satz und Kapitel)", () => {
  const a = aufbau();
  a.zeichne(64);
  const h = a.leiste(64).innerHTML;
  assert.equal((h.match(/data-action="film-knopf"/g) || []).length, 3);
  assert.match(h, /▶ Hör zu: ‚Befehle gibt sie aber nicht‘ \(Kapitel 5\)/);
  assert.match(h, /🎭 Kapitel 7 ansehen/, "Film-Symbol bei Beschriftung ohne eigenes Symbol");
});

test("F6 Nur ein Symbol: beginnt der Text schon mit ▶ (oder einem Emoji), steht davor kein 🎭/🧊 – nicht „🎭 ▶ Hör zu“", () => {
  const a = aufbau();
  a.zeichne(64);
  const h = a.leiste(64).innerHTML;
  assert.doesNotMatch(h, /🎭\s*▶/);
  assert.match(h, />\s*▶ Hör zu/);
  // Modell-Knopf mit eigenem Emoji im Text
  const b = aufbau({ tabs: [{ key: "volk", aufgaben: [{ nr: 70, typ: "mc", titel: "x", modell: [
    { film: "biene3d", text: "🧊 Organ zeigen", befehle: [] }, { film: "biene3d", text: "Bein zeigen", befehle: [] }, { bild: "/x.svg", text: "🖼️ Bild", alt: "x" }] }] }] });
  b.zeichne(70);
  const hb = b.leiste(70).innerHTML;
  assert.doesNotMatch(hb, /🧊\s*🧊/);
  assert.match(hb, />\s*🧊 Organ zeigen/);
  assert.match(hb, />\s*🧊 Bein zeigen/, "ohne eigenes Symbol: das Modell-Symbol davor");
  assert.doesNotMatch(hb, /🖼️\s*🖼️/);
});

// ── T7: Pflicht-Sperre ───────────────────────────────────────────────────────
test("Pflicht: ALLE Pflicht-Knöpfe nötig – einer allein löst die Sperre nicht; nach dem Druck zählt erst 3 s Wiedergabe", () => {
  const a = aufbau();
  a.zeichne(64);
  assert.equal(a.sperre(64), true);
  assert.match(a.schild(64), /alle 2 Stellen an \(0 von 2 geschafft\)/);
  a.druecke(64, 0);
  assert.match(a.leiste(64).innerHTML, /⏳ ▶ Hör zu/, "gedrückt, aber noch nicht lange genug gesehen");
  assert.equal(a.sperre(64), true);
  a.spielen("volk", 90, 2.0);                      // nur 2 s
  assert.equal(a.sperre(64), true, "2 s reichen nicht");
  a.spielen("volk", 92, 1.5);                      // zusammen > 3 s
  assert.match(a.leiste(64).innerHTML, /✅ ▶ Hör zu/);
  assert.equal(a.sperre(64), true, "der zweite Pflicht-Knopf fehlt noch");
  assert.match(a.schild(64), /1 von 2 geschafft/);
  a.druecke(64, 1);
  a.spielen("volk", 120, 3.5);
  assert.equal(a.sperre(64), false, "beide gesehen: die Station ist frei");
  assert.equal(a.schild(64), null);
  assert.deepEqual(plain(a.regs.filme.collect().knoepfe), { 64: [0, 1] });
  assert.ok(a.log.dirty > 0);
});

test("Pflicht: Springen und Anhalten zählen nicht als Wiedergabe; ein Pausieren unterbricht die Zählung", () => {
  const a = aufbau();
  a.zeichne(64);
  a.druecke(64, 0);
  a.status("volk", { t: 90, laeuft: true });
  a.status("volk", { t: 150, laeuft: true });      // Sprung um 60 s: keine Spielzeit
  a.status("volk", { t: 150.25, laeuft: true });
  a.status("volk", { t: 160, laeuft: false });     // pausiert
  a.status("volk", { t: 160.25, laeuft: false });
  assert.equal(a.sperre(64), true);
  a.spielen("volk", 160, 1.0); a.status("volk", { t: 161.25, laeuft: false }); a.spielen("volk", 200, 1.0);
  assert.equal(a.sperre(64), true, "2 × 1 s mit Pause dazwischen sind nicht 3 s am Stück");
  a.spielen("volk", 300, 3.25);
  assert.equal(a.sperre(64), true, "der zweite Pflicht-Knopf fehlt ja noch");
});

test("Pflicht: Modell-Knopf und alte Speicherstände (knoepfe[nr] = true) – ein Druck genügt bzw. alles erfüllt", () => {
  const a = aufbau();
  a.zeichne(66);
  assert.equal(a.sperre(66), true);
  a.druecke(66, 0);
  assert.equal(a.sperre(66), false, "3D-Modell: der Druck genügt (keine Zeitachse)");
  const b = aufbau();
  b.regs.filme.apply({ filme: {}, knoepfe: { 64: true } });
  b.zeichne(64);
  assert.equal(b.sperre(64), false, "alter Stand: true = alle Pflicht-Knöpfe erfüllt");
  const c = aufbau();
  c.regs.filme.apply({ filme: {}, knoepfe: { 64: [0, 7, -1, "x"], 66: "kaputt" } });
  c.zeichne(64); c.zeichne(66);
  assert.deepEqual(plain(c.regs.filme.collect().knoepfe), { 64: [0] }, "kaputte Einträge werden verworfen");
  assert.equal(c.sperre(64), true);
});

test("Pflicht: im Prüfmodus der Lehrkraft gibt es keine Sperre", () => {
  const a = aufbau({ pruef: true });
  a.zeichne(64);
  assert.equal(a.sperre(64), false);
  assert.equal(a.schild(64), null);
});

test("Station ohne Pflicht-Knopf: nie gesperrt, auch nicht nach dem Druck", () => {
  const a = aufbau();
  a.zeichne(65);
  assert.equal(a.sperre(65), false);
  a.druecke(65, 0);
  assert.equal(a.sperre(65), false);
  assert.match(a.leiste(65).innerHTML, /✅ 🎭 Kapitel 2/, "gedrückt: Haken");
});

// ── T6: Film-Karte ───────────────────────────────────────────────────────────
test("Film-Karte: Balken und Prozent laufen mit jeder Statusmeldung mit, die Station hakt erst bei vollständig gesehen ab", () => {
  const a = aufbau();
  a.zeichne(18);
  a.BIE.actions["film-spielen"]({ dataset: { nr: "18" } });
  a.warten(200);
  a.status("volk", { t: 5, laeuft: true, gesehen: 12 });
  assert.equal(a.get("filmbalken-18").style.width, "12%");
  assert.equal(a.get("filmproz-18").textContent, "12 %");
  a.status("volk", { t: 40, laeuft: true, gesehen: 47 });
  assert.equal(a.get("filmbalken-18").style.width, "47%");
  assert.equal(a.get("filmproz-18").textContent, "47 %");
  assert.equal(a.state.completed.has("18"), false);
  a.status("volk", { t: 235, laeuft: true, gesehen: 96, freigeschaltet: true });
  assert.equal(a.get("filmproz-18").textContent, "✅ ganz gesehen");
  assert.equal(a.state.completed.has("18"), true);
  assert.equal(a.log.antworten.filter((x) => x[1] === "film").length, 1, "genau eine Antwort");
  a.status("volk", { t: 236, laeuft: true, gesehen: 97, freigeschaltet: true });
  assert.equal(a.log.antworten.filter((x) => x[1] === "film").length, 1, "nicht noch einmal");
});

// ── Stationswechsel-Hörer ────────────────────────────────────────────────────
test("stationHoerer: andere Module erfahren den Wechsel der Station (nur beim Wechsel, nicht doppelt)", () => {
  const a = aufbau();
  a.film.init();
  const gesehen = [];
  a.film.stationHoerer.push((tab, nr) => gesehen.push(tab + ":" + nr));
  a.film.stationWechsel("volk", "64");
  a.film.stationWechsel("volk", "64");
  a.film.stationWechsel("volk", "65");
  assert.deepEqual(gesehen, ["volk:64", "volk:65"]);
  a.film.stationWechsel("anderer", "1");
  assert.deepEqual(gesehen, ["volk:64", "volk:65"], "nicht für Reiter, die nicht offen sind");
});
