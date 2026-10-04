/* Autosave: einheitlicher Zustandsvertrag (collectBackup/applyBackupData),
   IndexedDB-Arbeitsstand (48 h), Server-Autosave mit monotonen Revisionen,
   Abschluss-Flush, JSON-Export/-Import mit iPad-Textfallback. Standard §7–§9. */
BIE.autosave = (() => {
  "use strict";
  const { state, APP, $, $$, esc, showToast, postJSON, getJSON } = BIE;
  const SCHEMA_VERSION = APP.schemaVersion || 2;
  const APP_ID = APP.appId;
  const KEY = `${APP_ID}:${APP.schuelerId}`;
  const DB_NAME = `${APP_ID}-autosave`;
  const STORE = "arbeitsstand";
  const TTL_MS = 48 * 60 * 60 * 1000;
  const MAX_BYTES = 2 * 1024 * 1024;

  const registry = [];          // { name, collect(compact) -> any, apply(data) -> void|Promise, order }
  let revision = 0;
  let dirtyFlag = false;
  let enabled = false;
  let stopped = false;
  let localTimer = null, serverTimer = null, intervalTimer = null;
  let lastServerOk = null;
  let saving = false;

  function register(name, collect, apply, order) { registry.push({ name, collect, apply, order: order || 50 }); registry.sort((a, b) => a.order - b.order); }

  // ─── Zustandsvertrag ──────────────────────────────────────────────────
  function collectBackup(opts) {
    const compact = !!(opts && opts.compact);
    const data = {
      schema_version: SCHEMA_VERSION,
      app_id: APP_ID,
      exported_at: new Date().toISOString().slice(0, 19),
      lernplatz: { schueler_id: APP.schuelerId, pseudonym: APP.pseudonym, klasse: APP.klasse },
      active_tab: state.activeTab,
      completed: Array.from(state.completed),
      niveaus: Object.assign({}, state.niveau),
    };
    registry.forEach(r => { try { const v = r.collect(compact); if (v !== undefined) data[r.name] = v; } catch (e) { console.error("collect", r.name, e); } });
    return data;
  }

  function validate(data) {
    if (!data || typeof data !== "object") throw new Error("Die Datei enthält keinen Arbeitsstand.");
    if (data.app_id !== APP_ID) throw new Error("Diese Sicherung gehört zu einem anderen Arbeitsblatt.");
    if (data.schema_version !== SCHEMA_VERSION) throw new Error("Die Sicherung hat eine unbekannte Version.");
    if (data.completed !== undefined && !Array.isArray(data.completed)) throw new Error("Feld completed ist ungültig.");
    if (data.niveaus !== undefined && (typeof data.niveaus !== "object" || Array.isArray(data.niveaus))) throw new Error("Feld niveaus ist ungültig.");
    if (data.texte !== undefined && (typeof data.texte !== "object" || Object.values(data.texte).some(v => typeof v !== "string"))) throw new Error("Feld texte ist ungültig.");
    if (JSON.stringify(data).length > MAX_BYTES) throw new Error("Die Sicherung ist zu groß.");
    return data;
  }

  async function applyBackupData(data, opts) {
    validate(data);
    state.restoring = true;
    try {
      // 1. Kernzustand: Niveaus und Fortschritt (Struktur wird davon abgeleitet)
      state.niveau = {};
      Object.entries(data.niveaus || {}).forEach(([nr, n]) => { if (["A", "B", "C"].includes(n)) state.niveau[nr] = n; });
      state.completed = new Set((data.completed || []).map(String));
      $$(".niveau-select").forEach(s => { s.value = state.niveau[s.dataset.nr] || "A"; const c = BIE.card(s.dataset.nr); if (c) c.dataset.niveau = s.value; });
      // 2. Module in Reihenfolge: Struktur → Felder → Fortschritt → Canvas (asynchron)
      for (const r of registry) {
        try { await r.apply(data[r.name], data); } catch (e) { console.error("apply", r.name, e); }
      }
      state.completed.forEach(nr => { const c = BIE.card(nr); if (c) { c.classList.add("is-done"); const b = $(".done-badge", c); if (b) b.hidden = false; } });
      BIE.updateProgress();
      if (data.active_tab) BIE.showTab(data.active_tab, { silent: true });
    } finally {
      state.restoring = false;   // 5. erst danach Autosave wieder aktivieren
    }
    if (opts && opts.source === "import") { dirtyFlag = true; scheduleServer(); }
  }

  // ─── IndexedDB ────────────────────────────────────────────────────────
  function openDB() {
    return new Promise((resolve, reject) => {
      if (!("indexedDB" in window)) { reject(new Error("kein IndexedDB")); return; }
      let req;
      try { req = indexedDB.open(DB_NAME, 1); } catch (e) { reject(e); return; }
      req.onupgradeneeded = () => { req.result.createObjectStore(STORE); };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error || new Error("IndexedDB"));
      req.onblocked = () => reject(new Error("IndexedDB blockiert"));
    });
  }
  async function idb(mode, fn) {
    const db = await openDB();
    try {
      return await new Promise((resolve, reject) => {
        const tx = db.transaction(STORE, mode);
        const store = tx.objectStore(STORE);
        const req = fn(store);
        tx.oncomplete = () => resolve(req && req.result);
        tx.onerror = () => reject(tx.error);
        tx.onabort = () => reject(tx.error);
      });
    } finally { db.close(); }
  }
  async function saveLocal(data) {
    try { await idb("readwrite", s => s.put({ state: data, revision, saved_at: Date.now() }, KEY)); setStatus("auf diesem Gerät gesichert", "local"); return true; }
    catch (e) { setStatus("lokale Sicherung nicht möglich", "warn"); return false; }
  }
  async function loadLocal() {
    try {
      const rec = await idb("readonly", s => s.get(KEY));
      if (!rec) return null;
      if (Date.now() - (rec.saved_at || 0) > TTL_MS) { await clearLocal(); return null; }
      return rec;
    } catch (e) { return null; }
  }
  async function clearLocal() { try { await idb("readwrite", s => s.delete(KEY)); } catch (e) { /* egal */ } }

  // ─── Server ──────────────────────────────────────────────────────────
  async function saveServer(opts) {
    if (stopped || saving) return false;
    saving = true;
    const rev = ++revision;
    const data = collectBackup({ compact: true });
    setStatus("wird gespeichert …", "busy");
    const r = await postJSON("/api/autosave", { revision: rev, state: data }, opts);
    saving = false;
    if (r.fehler) { setStatus("Speichern fehlgeschlagen – wird erneut versucht", "warn"); return false; }
    if (r.accepted === false && typeof r.revision === "number" && r.revision >= rev) {
      // Der Server kennt einen neueren Stand (anderes Gerät). Unsere Eingabe bleibt die lebende;
      // wir springen über die Server-Revision, damit der nächste Save angenommen wird.
      revision = r.revision;
      dirtyFlag = true;
      scheduleServer();
      return false;
    }
    dirtyFlag = false;
    lastServerOk = r.updated_at || new Date().toISOString();
    setStatus("auf dem Server gesichert · " + BIE.uhrzeit(lastServerOk), "ok");
    saveLocal(data);
    return true;
  }

  // ─── Zeitsteuerung ────────────────────────────────────────────────────
  function markDirty() {
    if (!enabled || stopped) return;
    dirtyFlag = true;
    setStatus("wird gespeichert …", "busy");
    clearTimeout(localTimer);
    localTimer = setTimeout(() => saveLocal(collectBackup({ compact: true })), 300);
    scheduleServer();
  }
  function scheduleServer() {
    clearTimeout(serverTimer);
    serverTimer = setTimeout(() => { if (dirtyFlag) saveServer(); }, 1300);
  }
  async function flush(opts) {
    clearTimeout(localTimer); clearTimeout(serverTimer);
    if (!enabled || stopped) return false;
    await saveLocal(collectBackup({ compact: true }));
    if (!dirtyFlag && !(opts && opts.force)) return true;
    return saveServer(opts);
  }
  function enable() {
    enabled = true;
    intervalTimer = setInterval(() => { if (dirtyFlag) saveServer(); }, 15000);
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") flush({ keepalive: true }); });
    window.addEventListener("pagehide", () => flush({ keepalive: true }));
    BIE.on("autosave_flush", async () => { await flush({ force: true }); BIE.emit("autosave_ack", { revision }); });
    if (!dirtyFlag) setStatus(lastServerOk ? "auf dem Server gesichert · " + BIE.uhrzeit(lastServerOk) : "automatische Sicherung aktiv", "ok");
  }
  function stop() { stopped = true; clearInterval(intervalTimer); clearTimeout(localTimer); clearTimeout(serverTimer); }

  function setStatus(text, kind) {
    const el = $("#autosave-status");
    if (!el) return;
    el.textContent = text;
    el.dataset.kind = kind || "";
  }

  // ─── Start: lokal und Server parallel laden, höhere Revision gewinnt ──
  async function restoreAtStart() {
    const [lokal, server] = await Promise.all([loadLocal(), getJSON("/api/autosave")]);
    const kandidaten = [];
    if (lokal && lokal.state) kandidaten.push({ quelle: "lokal", revision: lokal.revision || 0, state: lokal.state });
    if (server && server.ok && server.state) { kandidaten.push({ quelle: "server", revision: server.revision || 0, state: server.state }); lastServerOk = server.updated_at; }
    if (!kandidaten.length) return null;
    kandidaten.sort((a, b) => b.revision - a.revision);
    const beste = kandidaten[0];
    revision = Math.max(revision, beste.revision);
    if (state.interacted) {
      // Die lernende Person hat schon gearbeitet: ein älterer Restore darf das nicht überschreiben.
      revision = beste.revision + 1;
      dirtyFlag = true;
      return { uebersprungen: true, quelle: beste.quelle };
    }
    try { await applyBackupData(beste.state); } catch (e) { console.error("restore", e); return null; }
    if (beste.quelle === "lokal" && !(server && server.ok && server.revision >= beste.revision)) { dirtyFlag = true; }
    return { quelle: beste.quelle, revision: beste.revision };
  }

  // ─── Manuelle JSON-Sicherung ─────────────────────────────────────────
  function exportText() { return JSON.stringify(collectBackup({ compact: false }), null, 2); }
  function dateiname() { return `${APP_ID}_${(APP.pseudonym || "lernplatz").replace(/[^A-Za-z0-9_-]+/g, "-")}_${new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-")}.json`; }
  async function exportJSON() {
    const text = exportText();
    const name = dateiname();
    try {
      if (navigator.canShare && window.File) {
        const file = new File([text], name, { type: "application/json" });
        if (navigator.canShare({ files: [file] })) { await navigator.share({ files: [file], title: "Arbeitsstand" }); return "geteilt"; }
      }
    } catch (e) { /* Abbruch oder nicht unterstützt → Download */ }
    try {
      const blob = new Blob([text], { type: "application/json" });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click();
      setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
      return "download";
    } catch (e) { return "text"; }
  }
  async function importJSON(text) {
    let data;
    try { data = JSON.parse(text); } catch (e) { throw new Error("Das ist kein gültiges JSON."); }
    await applyBackupData(data, { source: "import" });   // keine neuen bewertbaren Antworten, nur Arbeitsstand
    return data;
  }

  // ─── Sicherungs-Dialog ───────────────────────────────────────────────
  function openDialog() {
    const d = $("#backup-dialog"); if (!d) return;
    $("#backup-text").value = exportText();
    $("#backup-import").value = "";
    $("#backup-msg").textContent = "";
    d.hidden = false;
    setTimeout(() => $("#backup-close").focus(), 30);
  }
  function closeDialog() { const d = $("#backup-dialog"); if (d) d.hidden = true; }
  BIE.actions["backup-open"] = openDialog;
  BIE.actions["backup-close"] = closeDialog;
  BIE.actions["backup-export"] = async () => { const wie = await exportJSON(); $("#backup-msg").textContent = wie === "text" ? "Download nicht möglich – kopiere den Text unten." : "JSON gesichert."; };
  BIE.actions["backup-copy"] = async () => {
    const ta = $("#backup-text"); ta.value = exportText(); ta.select();
    try { await navigator.clipboard.writeText(ta.value); $("#backup-msg").textContent = "In die Zwischenablage kopiert."; }
    catch (e) { $("#backup-msg").textContent = "Text ist markiert – jetzt mit „Kopieren“ übernehmen."; }
  };
  BIE.actions["backup-import"] = async () => {
    const text = $("#backup-import").value.trim();
    if (!text) { $("#backup-msg").textContent = "Füge zuerst den JSON-Text ein oder wähle eine Datei."; return; }
    try { await importJSON(text); $("#backup-msg").textContent = "Arbeitsstand geladen. Antworten wurden nicht neu ins Lehrkraft-Protokoll übertragen."; showToast("✅ Arbeitsstand geladen"); }
    catch (e) { $("#backup-msg").textContent = "⚠️ " + e.message; }
  };
  document.addEventListener("change", e => {
    if (e.target.id === "backup-file" && e.target.files && e.target.files[0]) {
      e.target.files[0].text().then(t => { $("#backup-import").value = t; $("#backup-msg").textContent = "Datei gelesen – jetzt „JSON laden“ tippen."; });
    }
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && $("#backup-dialog") && !$("#backup-dialog").hidden) closeDialog(); });

  return { register, collectBackup, applyBackupData, validate, markDirty, flush, enable, stop, clearLocal, restoreAtStart, exportJSON, importJSON, exportText, get revision() { return revision; }, get dirty() { return dirtyFlag; } };
})();
