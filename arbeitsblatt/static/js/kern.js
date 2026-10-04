/* Kern des Schüler-Arbeitsbereichs „Die Honigbiene – ein Nutztier mit eigenem Staat“
   Gemeinsamer Namensraum window.BIE: Zustand, Helfer, Fortschritt, Reiter, Socket, Sitzungsende.
   iPad-first: nur Tap, keine Hover-only-Funktionen, kein Drag & Drop. */
window.BIE = (() => {
  "use strict";

  const INHALTE = window.INHALTE;
  const APP = window.APP || {};
  const NIVEAU_LABEL = { A: "🟢 A · Basis", B: "🟡 B · Standard", C: "🔴 C · Experte" };
  const STORAGE_KEY = (APP.appId || "gsm") + ":lernplatz";
  // Prüfmodus der Lehrkraft: keine Schüler-APIs, keine Speicherung, Lehrer-Token im Header.
  const PRUEF = !!APP.pruefmodus;
  const pruefStub = url => PRUEF && String(url).startsWith("/api/") && !String(url).startsWith("/api/lehrer/") && url !== "/api/glossar";
  const apiHeaders = extra => { const h = Object.assign({}, extra || {}); if (PRUEF && APP.lehrerToken) h["X-Lehrer-Token"] = APP.lehrerToken; return h; };

  const state = {
    completed: new Set(),
    niveau: {},            // nr -> 'A' | 'B' | 'C'
    runtime: {},           // nr -> Laufzeitdaten der aktuellen Darstellung
    charts: {},
    activeTab: "material",
    kiGesperrt: false,
    kiKonfiguriert: true,
    gruppe: { active: false, typen: [] },
    chat: [],
    approved: {},          // anfrage_id -> typ
    restoring: false,      // während applyBackupData: keine Dirty-Markierung
    interacted: false,     // Interaktion vor Abschluss des Ladens (Standard §8.3)
  };
  const aufgabenByNr = {};
  const tabByNr = {};
  INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(a => { aufgabenByNr[a.nr] = a; tabByNr[a.nr] = tab; }));
  const lesestreckeNr = {};
  // Ein Reiter hat nur dann eine Lesestrecke, wenn er sie selbst angibt (tab.lese = "L1").
  // Die frühere Regel „die ersten fünf Reiter“ hätte dem Abschluss-Reiter eine Strecke
  // zugeschrieben, die es serverseitig gar nicht gibt.
  INHALTE.tabs.forEach(tab => { if (tab.lese) lesestreckeNr[tab.key] = tab.lese; });
  // Reihenfolge ALLER Stationen eines Reiters als Zeichenketten – die Lesestrecke steht dort, wo plan_<reiter>.py sie nennt:
  // direkt nach der Aufgabe tab.leseNach, ohne leseNach (oder bei unbekannter Nummer) ganz oben.
  function stationenVon(tab) {
    const liste = tab.aufgaben.map(a => String(a.nr));
    const lese = lesestreckeNr[tab.key];
    if (!lese) return liste;
    let i = -1;
    if (tab.leseNach !== undefined && tab.leseNach !== null && tab.leseNach !== "") {
      i = liste.indexOf(String(tab.leseNach));
      if (i < 0) console.warn(`Reiter ${tab.key}: leseNach ${tab.leseNach} gibt es nicht – die Lesestrecke steht oben.`);
    }
    liste.splice(i + 1, 0, lese);
    return liste;
  }
  // Sichtbare Nummern (1, 2, 3 …) statt der internen nr – Quelle: static/js/anzeige.js (läuft auch auf den Tafel-Seiten ohne BIE).
  const anzeigeNr = nr => (INHALTE.anzeigeNr ? INHALTE.anzeigeNr(nr) : String(nr));
  const anzeigeLabel = nr => (INHALTE.anzeigeLabel ? INHALTE.anzeigeLabel(nr) : "Aufgabe " + nr);
  const totalTasks = APP.aufgabenGesamt || (Object.keys(aufgabenByNr).length + Object.keys(lesestreckeNr).length);

  // ─── Helfer ────────────────────────────────────────────────────────────
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const shuffle = arr => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  // Vergleichsform für Eingaben: klein, ohne Satzzeichen, ß = ss, Umlaute ä/ö/ü = ae/oe/ue („Bestäubung“ = „Bestaeubung“)
  // „Wie viele“ = „Wieviele“ (wie viel, wie vielen … ebenso): zusammen- und auseinandergeschrieben gelten beide
  const normalize = s => String(s || "").toLowerCase().trim().replace(/[.,;:!?„“"']/g, "").replace(/ß/g, "ss").replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/\s+/g, " ").replace(/\bwie viel(e|en|er|es|em)?\b/g, "wieviel$1");
  const isDifferenziert = t => !!t.niveaus;
  const niveauOf = nr => state.niveau[nr] || "A";
  const cfgOf = t => t.niveaus ? t.niveaus[niveauOf(t.nr)] : t;
  const card = nr => document.getElementById("card-" + nr);
  const body = nr => document.getElementById("body-" + nr);
  const uhrzeit = iso => (iso || "").slice(11, 16);

  function showFb(nr, kind, html, extraBtn) {
    const fb = document.getElementById("fb-" + nr);
    if (!fb) return;
    fb.className = "feedback-box show feedback-" + kind;
    fb.innerHTML = html + (extraBtn || "");
  }
  function clearFb(nr) { const fb = document.getElementById("fb-" + nr); if (fb) { fb.className = "feedback-box"; fb.innerHTML = ""; } }
  function retryBtn(nr) { return ` <button class="btn btn-quiet btn-sm" data-action="retry" data-nr="${nr}">🔄 Nochmal</button>`; }

  function showToast(text, color) {
    const t = $("#toast");
    if (!t) return;
    t.textContent = text;
    t.style.background = color || "#16a34a";
    t.classList.add("show");
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => t.classList.remove("show"), 3200);
  }

  // Netzwerkfehler dürfen nie als Ausnahme durchschlagen: immer ein Objekt zurückgeben.
  async function postJSON(url, payload, opts) {
    if (pruefStub(url)) return { ok: true, pruefmodus: true, httpStatus: 200 };
    try {
      const res = await fetch(url, { method: "POST", headers: apiHeaders({ "Content-Type": "application/json" }), body: JSON.stringify(payload || {}), keepalive: !!(opts && opts.keepalive) });
      if (res.status === 401) { sessionEnded("abgelaufen"); return { fehler: "Sitzung abgelaufen", httpStatus: 401 }; }
      const data = await res.json().catch(() => ({}));
      data.httpStatus = res.status;   // nie „status“: das Feld gehört den API-Antworten
      if (!res.ok && data.fehler === undefined && data.error) data.fehler = data.error;
      return data;
    } catch (e) {
      return { fehler: "Keine Verbindung zum Server.", offline: true };
    }
  }
  async function getJSON(url) {
    if (pruefStub(url)) return { ok: true, pruefmodus: true, httpStatus: 200 };
    try {
      const res = await fetch(url, { headers: apiHeaders({ "Accept": "application/json" }) });
      if (res.status === 401) { sessionEnded("abgelaufen"); return { fehler: "Sitzung abgelaufen", httpStatus: 401 }; }
      if (res.status === 204) return { httpStatus: 204, leer: true };
      const data = await res.json().catch(() => ({}));
      data.httpStatus = res.status;
      return data;
    } catch (e) {
      return { fehler: "Keine Verbindung zum Server.", offline: true };
    }
  }

  // ─── Lernplatz im Browser (Resume-Token) ─────────────────────────────
  function lernplatzSpeichern() {
    if (!APP.resumeToken) return;
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ schueler_id: APP.schuelerId, token: APP.resumeToken, pseudonym: APP.pseudonym, klasse: APP.klasse })); } catch (e) { /* privater Modus */ }
  }
  function lernplatzLoeschen() { try { localStorage.removeItem(STORAGE_KEY); } catch (e) { /* egal */ } }

  // ─── Dirty-Markierung für den Autosave ───────────────────────────────
  function dirty() {
    if (state.restoring) return;
    state.interacted = true;
    if (window.BIE && BIE.autosave) BIE.autosave.markDirty();
  }

  // ─── Fortschritt ───────────────────────────────────────────────────────
  function updateProgress() {
    const done = state.completed.size;
    const pct = Math.round((done / totalTasks) * 100);
    if (!$("#progress-fill")) return;   // Prüfmodus hat keine Fortschrittsanzeige
    $("#progress-fill").style.width = pct + "%";
    $("#progress-text").textContent = `${done} / ${totalTasks} Stationen`;
    $("#progress-pct").textContent = pct + " %";
    INHALTE.tabs.forEach(tab => {
      const stationen = tab.aufgaben.map(a => String(a.nr)).concat(lesestreckeNr[tab.key] ? [lesestreckeNr[tab.key]] : []);
      const n = stationen.filter(nr => state.completed.has(nr)).length;
      const chip = $(`#tabcount-${tab.key}`);
      if (chip) { chip.textContent = `${n}/${stationen.length}`; chip.classList.toggle("is-complete", n === stationen.length); }
    });
    if (done === totalTasks && !updateProgress._celebrated) { updateProgress._celebrated = true; showToast("🏆 Alle Stationen erledigt – stark!", "#AD007C"); }
  }

  function markComplete(nr) {
    const key = String(nr);
    const first = !state.completed.has(key);
    state.completed.add(key);
    const c = card(nr);
    if (c) { c.classList.add("is-done"); const b = $(".done-badge", c); if (b) b.hidden = false; }
    updateProgress();
    if (first && !state.restoring) {
      postJSON("/api/fortschritt", { aufgabe: key, niveau: key === "T" ? "Transfer" : niveauOf(nr) });
      dirty();
    }
    if (BIE.schritte && !state.restoring) BIE.schritte.nachAbschluss(key);
  }

  // Expliziter, bewertbarer Versuch – getrennt vom Autosave (Standard §12).
  // `max` (optional): längere Texte, z. B. beim Forscherbuch (der Server schneidet bei 2000 Zeichen ab, sonst bei 500).
  function sendAntwort(nr, typ, text, korrekt, frage, max) {
    if (state.restoring) return;
    const key = String(nr);
    postJSON("/api/antwort", { aufgabe: key, niveau: niveauOf(nr), typ, frage: String(frage || "").slice(0, 300), antwort: String(text).slice(0, max || 400), korrekt: korrekt === undefined ? null : korrekt });
  }

  // ─── Navigation ────────────────────────────────────────────────────────
  const beimOeffnen = {};   // Module registrieren hier: beimOeffnen[tabKey] = fn
  function buildNav() {
    const nav = $("#tab-bar");
    const items = [{ key: "material", label: "Arbeitsblatt", icon: "📄" }].concat(INHALTE.tabs);
    nav.innerHTML = items.map((t, i) => {
      const anzahl = t.aufgaben ? t.aufgaben.length + (lesestreckeNr[t.key] ? 1 : 0) : 0;
      return `
      <button class="tab-btn${i === 0 ? " active" : ""}" id="btn-tab-${t.key}" data-action="tab" data-tab="${t.key}" role="tab" aria-selected="${i === 0}" aria-controls="tab-${t.key}">
        <span class="tab-icon" aria-hidden="true">${t.icon}</span><span class="tab-label">${esc(t.label)}</span>
        ${t.aufgaben ? `<span class="tab-count" id="tabcount-${t.key}">0/${anzahl}</span>` : ""}
      </button>`;
    }).join("");
  }

  function showTab(key, opts) {
    if (!document.getElementById("tab-" + key)) key = "material";
    if (BIE.schritte && !BIE.schritte.tabFrei(key)) {
      if (!(opts && opts.silent)) showToast("🔒 Erst den vorherigen Abschnitt durcharbeiten.", "#d97706");
      key = BIE.schritte.erstesFreiesTab();
      if (state.activeTab === key) return;
    }
    const geaendert = state.activeTab !== key;
    state.activeTab = key;
    $$(".tab-btn").forEach(b => { const on = b.dataset.tab === key; b.classList.toggle("active", on); b.setAttribute("aria-selected", on); });
    $$(".tab-panel").forEach(p => { p.hidden = p.dataset.panel !== key; });
    Object.keys(beimOeffnen).forEach(k => { if (k === key || k === "*") { try { beimOeffnen[k](key); } catch (e) { console.error(e); } } });
    if (!(opts && opts.silent)) window.scrollTo({ top: Math.min(window.scrollY, $("#tab-bar").offsetTop - 8), behavior: "smooth" });
    if (geaendert && !(opts && opts.silent)) dirty();
  }

  // ─── Sitzungsende ─────────────────────────────────────────────────────
  function sessionEnded(grund) {
    if (sessionEnded._done) return; sessionEnded._done = true;
    if (BIE.autosave) BIE.autosave.stop();
    const texte = {
      geloescht: "Deine Daten wurden von der Lehrkraft gelöscht.",
      zurueckgesetzt: "Die Lehrkraft hat die Sitzung zurückgesetzt.",
      archiviert: "Die Stunde wurde beendet und sicher archiviert. Für eine Fortsetzung kannst du dich später wieder anmelden.",
      ersetzt: "Die Lehrkraft hat einen anderen Arbeitsstand geladen. Bitte melde dich neu an.",
      abgelaufen: "Die Sitzung ist abgelaufen. Bitte melde dich neu an.",
    };
    if (grund === "geloescht" || grund === "zurueckgesetzt") { lernplatzLoeschen(); if (BIE.autosave) BIE.autosave.clearLocal(); }
    else if (grund === "archiviert" || grund === "ersetzt") { if (BIE.autosave) BIE.autosave.clearLocal(); }   // Token bleibt für die Fortsetzungsstunde
    const o = $("#session-overlay"); o.hidden = false;
    $("#session-overlay-text").textContent = texte[grund] || "Die Unterrichtssitzung wurde beendet.";
    setTimeout(() => { location.href = PRUEF ? "/lehrer/login" : grund === "archiviert" || grund === "ersetzt" ? "/warten" : "/login"; }, 4000);
  }

  // ─── Socket.IO ─────────────────────────────────────────────────────────
  const socketHandlers = {};
  function on(event, fn) { (socketHandlers[event] = socketHandlers[event] || []).push(fn); }
  let socket = null;
  function setupSocket() {
    if (typeof io === "undefined") return;
    socket = io({ transports: ["polling", "websocket"] });   // erst Polling, dann Upgrade: scheitert der WebSocket, bleibt die Live-Verbindung trotzdem
    socket.on("connect", () => socket.emit("schueler_join", {}));
    const events = ["ki_entscheidung", "ki_gesperrt", "gruppenfreigabe", "sitzung_beendet", "autosave_flush", "fortsetzung_zugeordnet", "praesentation"];
    events.forEach(ev => socket.on(ev, d => (socketHandlers[ev] || []).forEach(fn => { try { fn(d); } catch (e) { console.error(e); } })));
  }
  function emit(event, data) { if (socket && socket.connected) socket.emit(event, data || {}); }
  on("sitzung_beendet", d => sessionEnded(d && d.grund));
  on("ki_gesperrt", d => {
    state.kiGesperrt = !!d.gesperrt;
    document.body.classList.toggle("ki-locked", state.kiGesperrt);
    if (state.kiGesperrt) { state.approved = {}; showToast("🚫 KI-Zugang von der Lehrkraft gesperrt.", "#dc2626"); }
    else if (setupSocket._wasLocked) showToast("✅ KI-Zugang wieder freigegeben!");
    setupSocket._wasLocked = state.kiGesperrt;
  });
  on("gruppenfreigabe", d => {
    state.gruppe = { active: !!d.active, typen: d.typen || [], expires_at: d.expires_at || null };
    if (d.locked) { state.kiGesperrt = true; document.body.classList.add("ki-locked"); state.approved = {}; }
    const note = $("#tutor-note");
    if (note && state.kiKonfiguriert) note.textContent = state.gruppe.active ? "KI von der Lehrkraft für die Klasse freigegeben" : "KI-Tutor · Freigabe durch Lehrkraft nötig";
  });
  on("fortsetzung_zugeordnet", () => { location.href = "/warten"; });

  // ─── Ereignis-Delegation ──────────────────────────────────────────────
  const actions = {};
  document.addEventListener("click", e => {
    const el = e.target.closest("[data-action]");
    if (!el) return;
    const fn = actions[el.dataset.action];
    if (fn) { fn(el, e); }
  });
  actions.tab = el => showTab(el.dataset.tab);
  actions.retry = el => { if (BIE.aufgaben) BIE.aufgaben.renderBody(aufgabenByNr[el.dataset.nr]); dirty(); };

  document.addEventListener("change", e => {
    if (e.target.dataset.action === "niveau") {
      const nr = e.target.dataset.nr; state.niveau[nr] = e.target.value;
      if (BIE.aufgaben) BIE.aufgaben.renderBody(aufgabenByNr[nr]);   // nur diese Karte wechselt das Niveau
      const c = card(nr); if (c) c.dataset.niveau = e.target.value;
      dirty();
    }
  });

  return {
    INHALTE, APP, NIVEAU_LABEL, state, aufgabenByNr, tabByNr, lesestreckeNr, stationenVon, totalTasks, pruefmodus: PRUEF,
    anzeigeNr, anzeigeLabel,
    $, $$, esc, shuffle, normalize, isDifferenziert, niveauOf, cfgOf, card, body, uhrzeit,
    showFb, clearFb, retryBtn, showToast, postJSON, getJSON,
    lernplatzSpeichern, lernplatzLoeschen, dirty, updateProgress, markComplete, sendAntwort,
    buildNav, showTab, beimOeffnen, sessionEnded, setupSocket, on, emit, actions,
    get socket() { return socket; },
  };
})();
