/* KI: Freigaben (Einzel + Gruppe), Tutor-Chat, Korrektur, Zeichenanalyse, Handschrift.
   Ohne Lehrkraftfreigabe erreicht keine Anfrage die KI. Die Frage bleibt im Feld, bis sie
   freigegeben und versendet ist (Standard §18.1). */
BIE.ki = (() => {
  "use strict";
  const { state, $, $$, esc, showToast, postJSON, showFb, INHALTE } = BIE;
  let pendingTyp = null, pendingCallback = null, pendingId = null, pendingKontext = "";

  // Sicheres Markdown-lite: escapen, dann **fett** und Zeilenumbrüche.
  function md(text) {
    return esc(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/^(?:- |• )/gm, "• ").replace(/\n/g, "<br>");
  }

  function gruppeErlaubt(typ) { return state.gruppe && state.gruppe.active && (state.gruppe.typen || []).includes(typ); }

  function requestKiAccess(typ, kontext, callback) {
    if (state.kiGesperrt) { showToast("🚫 Der KI-Zugang ist gesperrt.", "#dc2626"); return; }
    if (gruppeErlaubt(typ)) { callback(null); return; }
    for (const [id, t] of Object.entries(state.approved)) { if (t === typ) { callback(parseInt(id, 10)); return; } }
    pendingTyp = typ; pendingCallback = callback; pendingId = null; pendingKontext = kontext;
    const texte = {
      chat: ["💬", "KI-Tutor anfragen", "Der KI-Tutor beantwortet deine Frage. Deine Lehrkraft muss die Nutzung kurz freigeben – deine Frage bleibt so lange im Eingabefeld."],
      korrektur: ["✅", "KI-Feedback anfragen", "Die KI gibt dir Rückmeldung zu deinem Text. Deine Lehrkraft muss die Nutzung kurz freigeben."],
      zeichnung: ["🎨", "KI-Bewertung der Zeichnung", "Die KI schaut sich deine Skizze an und sagt, was erkennbar ist und was fehlt. Deine Lehrkraft muss das kurz freigeben."],
      handschrift: ["✍️", "Handschrift erkennen lassen", "Die KI liest deine Handschrift und trägt den Text ein. Deine Lehrkraft muss das kurz freigeben."],
    }[typ] || ["🤖", "KI-Funktion freigeben", ""];
    $("#ki-modal-icon").textContent = texte[0];
    $("#ki-modal-title").textContent = texte[1];
    $("#ki-modal-text").textContent = texte[2];
    $("#ki-request-confirm").hidden = false; $("#ki-waiting").hidden = true;
    $("#ki-overlay").hidden = false;
    setTimeout(() => $("#ki-request-confirm").focus(), 30);
  }
  async function sendeAnfrage() {
    $("#ki-request-confirm").hidden = true; $("#ki-waiting").hidden = false;
    const data = await postJSON("/api/ki-anfrage", { typ: pendingTyp, kontext: pendingKontext || pendingTyp });
    if (data.status === "wartend") { pendingId = data.anfrage_id; return; }
    if (data.status === "freigegeben") { const cb = pendingCallback; closeKiOverlay(); if (cb) cb(null); return; }
    $("#ki-waiting").innerHTML = "⚠️ " + esc(data.message || data.fehler || "Anfrage nicht möglich.");
    setTimeout(closeKiOverlay, 3000);
  }
  function closeKiOverlay() {
    $("#ki-overlay").hidden = true;
    $("#ki-waiting").innerHTML = '<span class="spinner" aria-hidden="true"></span>Warte auf die Lehrkraft …';
    pendingId = null; pendingCallback = null; pendingTyp = null;
  }
  BIE.on("ki_entscheidung", d => {
    if (pendingId && d.anfrage_id !== pendingId) return;
    const cb = pendingCallback;
    closeKiOverlay();
    if (d.entscheid === "freigegeben") { state.approved[d.anfrage_id] = d.typ; showToast("✅ Freigegeben – die KI darf jetzt helfen!"); if (cb) cb(d.anfrage_id); }
    else showToast("❌ Die Lehrkraft hat die Anfrage abgelehnt.", "#dc2626");
  });
  BIE.actions["ki-confirm"] = sendeAnfrage;
  BIE.actions["ki-cancel"] = closeKiOverlay;

  function blockiert(aid, nr, text) { if (aid != null) delete state.approved[aid]; if (nr) showFb(nr, "err", "🔒 " + esc(text || "Nicht freigegeben.")); else showToast("🔒 " + (text || "Nicht freigegeben."), "#dc2626"); }

  function korrektur(nr, question, answer, context, onResult) {
    requestKiAccess("korrektur", BIE.anzeigeLabel(nr), async aid => {
      showFb(nr, "info", "🤖 Deine Antwort wird gerade bewertet …");
      const data = await postJSON("/api/check-answer", { question, answer, context, anfrage_id: aid });
      if (data.offline) { showFb(nr, "err", "⚠️ Keine Verbindung zur KI. Versuch es gleich noch einmal."); return; }
      if (data.blocked) { blockiert(aid, nr, data.feedback); return; }
      onResult(data);
    });
  }
  // extra = { geraet, niveau }: der Server ergänzt damit die Prüfliste aus zeichenauftraege.py
  function zeichnung(nr, png, aufgabe, onResult, extra) {
    requestKiAccess("zeichnung", `Zeichnung ${BIE.anzeigeNr(nr)}`, async aid => {
      showFb(nr, "info", "🤖 Die KI schaut sich deine Zeichnung an …");
      const data = await postJSON("/api/zeichnung-analyse", { png, aufgabe, anfrage_id: aid, geraet: (extra || {}).geraet || "", niveau: (extra || {}).niveau || "" });
      if (data.offline) { showFb(nr, "err", "⚠️ Keine Verbindung zur KI."); return; }
      if (data.blocked) { blockiert(aid, nr, data.feedback); return; }
      onResult(data);
    });
  }
  function handschrift(nr, png, onResult) {
    requestKiAccess("handschrift", "Handschrift", async aid => {
      showFb(nr, "info", "🤖 Handschrift wird gelesen …");
      const data = await postJSON("/api/handschrift", { png, anfrage_id: aid });
      if (data.offline) { showFb(nr, "err", "⚠️ Keine Verbindung zur KI."); return; }
      if (data.blocked) { blockiert(aid, nr, data.message); return; }
      onResult(data);
    });
  }

  // ─── Tutor-Chat ───────────────────────────────────────────────────────
  function addChatMessage(role, text) {
    const list = $("#chat-messages");
    const div = document.createElement("div");
    div.className = "chat-message " + (role === "assistant" ? "assistant" : "user");
    div.innerHTML = `<strong>${role === "assistant" ? "GSM-Tutor" : "Du"}</strong><p>${role === "assistant" ? md(text) : esc(text)}</p>`;
    list.appendChild(div); list.scrollTop = list.scrollHeight;
    return div;
  }
  async function sendMessage() {
    const inp = $("#chat-input");
    const text = inp.value.trim();
    if (!text) return;
    if (state.kiGesperrt) { showToast("🚫 Der KI-Zugang ist gesperrt.", "#dc2626"); return; }
    const tabLabel = (INHALTE.tabs.find(t => t.key === state.activeTab) || {}).label || "Arbeitsblatt";
    requestKiAccess("chat", text.slice(0, 200), async aid => {
      inp.value = "";                         // erst nach Freigabe und Versand leeren
      addChatMessage("user", text);
      const history = state.chat.slice(-8);
      state.chat.push({ role: "user", content: text });
      const thinking = addChatMessage("assistant", "…");
      const data = await postJSON("/api/chat", { message: text, history, kontext: tabLabel, anfrage_id: aid });
      if (data.offline) { thinking.querySelector("p").textContent = "⚠️ Verbindung fehlgeschlagen."; inp.value = text; return; }
      if (data.blocked) { thinking.querySelector("p").textContent = "🔒 " + (data.message || "Nicht freigegeben."); if (aid != null) delete state.approved[aid]; inp.value = text; return; }
      thinking.querySelector("p").innerHTML = md(data.response || "Keine Antwort erhalten.");
      state.chat.push({ role: "assistant", content: data.response || "" });
    });
  }
  function toggleTutor(force) {
    const panel = $("#tutor-panel"); const open = force === undefined ? panel.hidden : force;
    panel.hidden = !open; $("#tutor-toggle").setAttribute("aria-expanded", open);
    if (open) setTimeout(() => $("#chat-input").focus(), 50);
  }
  BIE.actions["tutor-toggle"] = () => toggleTutor();
  BIE.actions["tutor-close"] = () => toggleTutor(false);
  BIE.actions["chat-send"] = sendMessage;
  document.addEventListener("keydown", e => { if (e.key === "Enter" && e.target.id === "chat-input") { e.preventDefault(); sendMessage(); } });

  return { md, requestKiAccess, korrektur, zeichnung, handschrift, sendMessage, toggleTutor };
})();
