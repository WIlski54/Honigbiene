/* Initialisierung: Aufbau → Wiederherstellung (lokal ∥ Server, höhere Revision gewinnt)
   → Serverstatus → Socket → Autosave aktivieren. */
(async () => {
  "use strict";
  const { state, $, $$, showToast, getJSON } = BIE;

  BIE.buildNav();
  BIE.aufgaben.buildPanels();
  if (BIE.film) BIE.film.init();        // Filmbühne (film.js) – auch im Prüfmodus
  if (BIE.pruefmodus) {   // Lehrkraft: alles offen, keine Sitzung, keine Speicherung
    BIE.schritte.init();
    BIE.pruefen.init();
    BIE.showTab(state.activeTab, { silent: true });
    showToast("🔍 Prüfmodus: alle Reiter offen, nichts wird gespeichert.", "#006AB3");
    return;
  }
  BIE.lernplatzSpeichern();
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  if (isIOS) document.body.classList.add("is-ios");

  const statusP = getJSON("/api/status");
  const zeichnungenP = BIE.zeichnen.ladeServer();
  let restore = null;
  try { restore = await BIE.autosave.restoreAtStart(); } catch (e) { console.error("restore", e); }
  await zeichnungenP;
  const status = await statusP;
  if (status && status.ok) {
    state.restoring = true;
    (status.erledigt || []).forEach(x => { state.completed.add(String(x.nr)); if (x.niveau && x.niveau !== "Transfer" && !state.niveau[x.nr]) state.niveau[x.nr] = x.niveau; });
    state.completed.forEach(nr => { const c = BIE.card(nr); if (c) { c.classList.add("is-done"); const b = $(".done-badge", c); if (b) b.hidden = false; } });
    $$(".niveau-select").forEach(s => { if (state.niveau[s.dataset.nr]) s.value = state.niveau[s.dataset.nr]; });
    state.restoring = false;
    state.kiGesperrt = !!status.ki_gesperrt; document.body.classList.toggle("ki-locked", state.kiGesperrt);
    state.kiKonfiguriert = status.ki_konfiguriert !== false;
    if (status.gruppenfreigabe) state.gruppe = { active: !!status.gruppenfreigabe.active, typen: status.gruppenfreigabe.typen || [], expires_at: status.gruppenfreigabe.expires_at };
    const note = $("#tutor-note");
    if (!state.kiKonfiguriert) note.textContent = "KI ist noch nicht konfiguriert – Aufgaben funktionieren trotzdem.";
    else if (state.gruppe.active) note.textContent = "KI von der Lehrkraft für die Klasse freigegeben";
  }
  BIE.updateProgress();
  BIE.schritte.init();
  BIE.showTab(state.activeTab, { silent: true });
  BIE.setupSocket();
  // Präsentationsmodus erst nach dem Socket: dann greift auch der Reconnect-Haken.
  if (BIE.praesentation) BIE.praesentation.init(status && status.praesentation);
  BIE.autosave.enable();
  if (restore && restore.uebersprungen) showToast("Deine neuen Eingaben bleiben erhalten – ein älterer Stand wurde nicht geladen.", "#d97706");
  else if (restore && restore.quelle) showToast(restore.quelle === "server" ? "Arbeitsstand vom Server wiederhergestellt" : "Arbeitsstand von diesem Gerät wiederhergestellt", "#006AB3");
})();
