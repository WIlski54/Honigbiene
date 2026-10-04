/* Lehrer-Dashboard – Live-Übersicht, KI-Freigaben (Einzel + Gruppe), Zwischenstände, IServ, Fortsetzung.
   Alle Lehrkraftaktionen tragen das Aktionstoken im Header und funktionieren auch, wenn Lehrkraft
   und Lernende dasselbe Browserprofil verwenden. */
(() => {
  "use strict";
  const DASH = window.DASH || {};
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const zeit = iso => (iso || "").slice(11, 16);
  const datum = iso => (iso || "").slice(0, 16).replace("T", " ");
  const students = {};
  const requests = {};
  let gesperrt = new Set();
  const HEAD = { "Content-Type": "application/json", "X-Lehrer-Token": DASH.token || "" };

  function toast(text, color) {
    const t = $("#toast"); t.textContent = text; t.style.background = color || "#16a34a"; t.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove("show"), 3200);
  }
  async function post(url, payload, method) {
    try {
      const res = await fetch(url, { method: method || "POST", headers: HEAD, body: method === "DELETE" ? undefined : JSON.stringify(payload || {}) });
      if (res.status === 401) { location.href = "/lehrer/login"; return {}; }
      const d = await res.json().catch(() => ({})); d._status = res.status; return d;
    } catch (e) { return { ok: false, error: "Keine Verbindung zum Server." }; }
  }
  async function get(url) {
    try {
      const res = await fetch(url, { headers: HEAD });
      if (res.status === 401) { location.href = "/lehrer/login"; return {}; }
      return await res.json();
    } catch (e) { return { ok: false, error: "Keine Verbindung zum Server." }; }
  }

  // ── Budget & KPIs ──
  function renderBudget(d) {
    const pct = Math.min(100, Math.round((d.today / d.limit) * 100));
    $("#budget-label").textContent = `${d.today} / ${d.limit} Tokens (${pct} %)`;
    const fill = $("#budget-fill"); fill.style.width = pct + "%";
    fill.className = pct >= 90 ? "budget-fill-danger" : pct >= 60 ? "budget-fill-warn" : "budget-fill-ok";
    $("#kpi-tokens").textContent = d.today;
  }
  function renderKpis() {
    const list = Object.values(students);
    $("#kpi-students").textContent = list.length;
    $("#kpi-online").textContent = list.filter(s => s.online).length;
    $("#kpi-answers").textContent = list.reduce((a, s) => a + (s.antworten || 0), 0);
    const n = Object.keys(requests).length;
    $("#kpi-requests").textContent = n; $("#request-count").textContent = n;
  }

  // ── Schüler-Tabelle ──
  function rowHTML(s) {
    const pct = Math.round((s.aufgaben_erledigt / s.aufgaben_gesamt) * 100);
    const chips = Object.values(s.abschnitte || {}).map(a => `<span class="abschnitt-chip${a.erledigt === a.gesamt ? " is-complete" : a.erledigt ? " is-started" : ""}" title="${esc(a.titel)}">${esc(a.kurz)} ${a.erledigt}/${a.gesamt}</span>`).join("");
    const locked = gesperrt.has(s.id);
    return `
      <td><span class="dot${s.online ? " online" : ""}" title="${s.online ? "online" : "offline"}"></span></td>
      <td><strong>${esc(s.pseudonym)}</strong></td>
      <td>${esc(s.klasse)}</td>
      <td><div class="mini-progress"><div class="progress-track"><span style="width:${pct}%"></span></div><span>${s.aufgaben_erledigt}/${s.aufgaben_gesamt}</span></div></td>
      <td><div class="abschnitt-chips">${chips}</div></td>
      <td>${s.antworten || 0}</td>
      <td>${s.notizen || 0}/${(DASH.abschnitte || []).length || 5}</td>
      <td>${s.zeichnungen || 0}</td>
      <td title="Revision ${s.autosave_revision || 0}">${s.autosave_at ? zeit(s.autosave_at) : "–"}</td>
      <td><span class="pill ${locked ? "pill-locked" : "pill-open"}">${locked ? "gesperrt" : "frei"}</span>${s.pending ? ` <span class="pill pill-locked">${s.pending} offen</span>` : ""}</td>
      <td>${esc(zeit(s.last_active))}</td>
      <td><div class="row-actions">
        <a class="btn btn-outline btn-sm" href="/lehrer/schueler/${s.id}">Detail</a>
        <button class="btn btn-quiet btn-sm" data-lock="${s.id}" type="button">${locked ? "KI freigeben" : "KI sperren"}</button>
        <button class="btn btn-danger-outline btn-sm" data-delete="${s.id}" type="button">Löschen</button>
      </div></td>`;
  }
  function upsertStudent(s) {
    if (!s || !s.id) return;
    students[s.id] = Object.assign(students[s.id] || {}, s);
    const tbody = $("#student-table");
    const empty = $("#no-students"); if (empty) empty.remove();
    let tr = tbody.querySelector(`tr[data-id="${s.id}"]`);
    if (!tr) { tr = document.createElement("tr"); tr.dataset.id = s.id; tbody.prepend(tr); }
    tr.innerHTML = rowHTML(students[s.id]);
    renderKpis();
  }
  function removeStudent(id) {
    delete students[id];
    const tr = $(`#student-table tr[data-id="${id}"]`); if (tr) tr.remove();
    if (!Object.keys(students).length) $("#student-table").innerHTML = '<tr id="no-students"><td colspan="12" class="empty-state">Noch niemand angemeldet.</td></tr>';
    renderKpis();
  }

  // ── Woran es hakt: Stationen mit den meisten Fehlversuchen ──
  function renderHakt(liste) {
    const body = $("#hakt-body"); if (!body) return;
    $("#hakt-count").textContent = (liste || []).length;
    if (!liste || !liste.length) { body.innerHTML = '<tr id="no-hakt"><td colspan="5" class="empty-state">Noch keine Fehlversuche.</td></tr>'; return; }
    body.innerHTML = liste.map(h => `<tr>
      <td><strong title="intern ${esc(h.nr)}">${esc(h.anzeige || h.nr)}</strong></td>
      <td><span class="abschnitt-chip" title="${esc(h.abschnitt)}">${esc(h.kurz)}</span> ${esc(h.abschnitt)}</td>
      <td>${h.falsch} von ${h.versuche} Versuchen <small>(${Math.round(h.quote * 100)} %)</small></td>
      <td>${h.personen_falsch} von ${h.personen}</td>
      <td class="hakt-frage">${esc(h.beispiel || "–")}</td></tr>`).join("");
  }
  let haktTimer = null;
  function haktLaden() {
    clearTimeout(haktTimer);
    haktTimer = setTimeout(async () => { const r = await get("/api/lehrer/hakt"); if (r.ok) renderHakt(r.hakt); }, 1500);
  }

  // ── Vermutungen der Klasse (Unterrichtsgespräch) ──
  function renderVermutungen(liste) {
    const body = $("#verm-body"); if (!body) return;
    $("#verm-count").textContent = (liste || []).reduce((a, g) => a + g.anzahl, 0);
    if (!liste || !liste.length) { body.innerHTML = '<p class="empty-state" id="no-verm">Noch keine Vermutungen.</p>'; return; }
    body.innerHTML = liste.map(g => {
      const max = Math.max(1, ...g.verteilung.map(v => v.anzahl));
      return `<div class="verm-gruppe"><h3><span class="abschnitt-chip" title="intern ${esc(g.nr)}">${esc(g.anzeige || g.nr)}</span> ${esc(g.frage)} <small>${g.anzahl} ${g.anzahl === 1 ? "Vermutung" : "Vermutungen"}</small></h3>
        ${g.verteilung.map(v => `<div class="verm-zeile"><span class="verm-option">${esc(v.option)}</span><span class="verm-balken" aria-hidden="true"><i style="width:${Math.round(v.anzahl / max * 100)}%"></i></span><b>${v.anzahl}</b></div>`).join("")}
        ${g.saetze.length ? `<details class="verm-saetze"><summary>Sätze der Lernenden (${g.saetze.length})</summary><ul>${g.saetze.map(s => `<li><strong>${esc(s.pseudonym)}:</strong> ${esc(s.text)}</li>`).join("")}</ul></details>` : ""}</div>`;
    }).join("");
  }
  let vermTimer = null;
  function vermLaden() {
    clearTimeout(vermTimer);
    vermTimer = setTimeout(async () => { const r = await get("/api/lehrer/vermutungen"); if (r.ok) renderVermutungen(r.vermutungen); }, 1500);
  }

  // ── Einzelanfragen ──
  const TYP = { chat: "Tutor", korrektur: "Feedback", zeichnung: "Zeichnung", handschrift: "Handschrift" };
  function requestHTML(a, isNew) {
    return `<div class="request-item${isNew ? " is-new" : ""}" data-id="${a.id}">
      <span class="request-typ">${TYP[a.typ] || esc(a.typ)}</span>
      <div class="who"><strong>${esc(a.pseudonym)}</strong><small>Klasse ${esc(a.klasse)} · ${esc(a.kontext || "")} · ${esc(zeit(a.erstellt_at))}</small></div>
      <button class="btn btn-primary btn-sm" data-decide="freigegeben" data-id="${a.id}" type="button">✅ Freigeben</button>
      <button class="btn btn-danger-outline btn-sm" data-decide="abgelehnt" data-id="${a.id}" type="button">✕</button>
    </div>`;
  }
  function renderRequests(list, isNew) {
    const host = $("#request-list");
    if (list) { Object.keys(requests).forEach(k => delete requests[k]); list.forEach(a => { requests[a.id] = a; }); host.innerHTML = ""; }
    const ids = Object.keys(requests);
    if (!ids.length) { host.innerHTML = '<p class="empty-state" id="no-requests">Keine offenen Anfragen.</p>'; renderKpis(); return; }
    const empty = $("#no-requests"); if (empty) empty.remove();
    ids.forEach(id => { if (!host.querySelector(`[data-id="${id}"]`)) host.insertAdjacentHTML("beforeend", requestHTML(requests[id], isNew)); });
    renderKpis();
  }
  function addRequest(a) {
    requests[a.id] = a; renderRequests(null, true);
    if (students[a.schueler_id]) { students[a.schueler_id].pending = (students[a.schueler_id].pending || 0) + 1; upsertStudent(students[a.schueler_id]); }
    toast(`🤖 ${a.pseudonym} fragt ${TYP[a.typ] || a.typ} an`, "#AD007C");
  }
  function removeRequest(id, sid) {
    delete requests[id];
    const el = $(`#request-list [data-id="${id}"]`); if (el) el.remove();
    if (sid && students[sid] && students[sid].pending) { students[sid].pending--; upsertStudent(students[sid]); }
    renderRequests(null);
  }

  // ── Gruppenfreigabe ──
  function renderGruppe(g) {
    const pill = $("#gruppe-pill");
    if (g.locked) { pill.textContent = "gesperrt"; pill.className = "pill pill-locked"; }
    else if (g.active) { pill.textContent = "aktiv"; pill.className = "pill pill-open"; }
    else { pill.textContent = "inaktiv"; pill.className = "pill pill-offline"; }
    const st = $("#gruppe-status");
    if (g.locked) st.textContent = "KI für die Gruppe gesperrt – wartende Einzelanfragen wurden abgelehnt. Nur „Sperre aufheben“ hebt das auf.";
    else if (g.active) st.textContent = `Aktiv bis ${zeit(g.expires_at)} · Funktionen: ${(g.typen || []).map(t => TYP[t] || t).join(", ")} · Klasse: ${g.klasse || "alle"} · verbraucht ${g.tokens_used}${g.token_limit ? " / " + g.token_limit : ""} Tokens${g.per_student_limit ? " · pro Lernplatz max. " + g.per_student_limit : ""}.`;
    else st.textContent = (g.abgelaufen ? "Die letzte Gruppenfreigabe ist abgelaufen. " : g.budget_erschoepft ? "Das Gruppenbudget ist erschöpft. " : "") + "Keine Gruppenfreigabe aktiv – Lernende brauchen Einzelfreigaben.";
  }
  $("#gruppe-form").addEventListener("submit", async e => {
    e.preventDefault();
    const f = e.target;
    const typen = $$("input[name=typ]:checked", f).map(i => i.value);
    if (!typen.length) { toast("Mindestens eine Funktion wählen", "#d97706"); return; }
    const r = await post("/api/lehrer/gruppenfreigabe", { aktion: "start", typen, klasse: f.klasse.value, minuten: parseInt(f.minuten.value, 10), token_limit: parseInt(f.token_limit.value, 10) || 0, per_student_limit: parseInt(f.per_student_limit.value, 10) || 0 });
    if (r.ok) { renderGruppe(r.gruppenfreigabe); toast("✅ Gruppenfreigabe gestartet"); } else toast(r.error || "Fehler", "#dc2626");
  });

  // ─── Präsentationsmodus ────────────────────────────────────────────────
  // Der Zustand kommt immer vom Server; das Dashboard spiegelt ihn nur.
  let praesBilder = [];

  function praesBilderFuellen(bilder) {
    if (!bilder || !bilder.length) return;
    praesBilder = bilder;
    const sel = document.getElementById("praes-bild");
    if (!sel || sel.dataset.gefuellt === String(bilder.length)) return;
    const gruppen = {};
    bilder.forEach(b => { (gruppen[b.gruppe] = gruppen[b.gruppe] || []).push(b); });
    sel.innerHTML = Object.entries(gruppen).map(([gruppe, liste]) =>
      `<optgroup label="${esc(gruppe)}">` +
      liste.map(b => `<option value="${esc(b.key)}">${esc(b.titel)}</option>`).join("") +
      `</optgroup>`).join("");
    sel.dataset.gefuellt = String(bilder.length);
    praesVorschau();
  }

  function praesVorschau() {
    const sel = document.getElementById("praes-bild"), img = document.getElementById("praes-vorschau");
    if (!sel || !img) return;
    const b = praesBilder.find(x => x.key === sel.value);
    img.hidden = !b;
    if (b) img.src = b.bild;
  }

  function renderPraes(p) {
    const status = document.getElementById("praes-status");
    if (!status) return;
    const aktiv = !!(p && p.active);
    status.textContent = aktiv ? "läuft: " + (p.titel || "Bild") : "aus";
    status.classList.toggle("is-live", aktiv);
    const sel = document.getElementById("praes-bild");
    if (aktiv && sel && p.key && sel.value !== p.key) { sel.value = p.key; praesVorschau(); }
    const hinweis = document.getElementById("praes-hinweis");
    if (aktiv && hinweis && !hinweis.matches(":focus")) hinweis.value = p.hinweis || "";
    const start = document.getElementById("praes-start"), stop = document.getElementById("praes-stop");
    if (start) start.textContent = aktiv ? "🔄 Anderes Bild zeigen" : "👀 Allen zeigen";
    if (stop) stop.disabled = !aktiv;
  }

  async function praesSenden(aktiv) {
    const sel = document.getElementById("praes-bild");
    const hinweis = document.getElementById("praes-hinweis");
    const r = await post("/api/lehrer/praesentation", {
      aktiv, bild: sel ? sel.value : "", hinweis: hinweis ? hinweis.value : "",
    });
    if (r.ok) { renderPraes(r.praesentation); toast(aktiv ? "👀 Bild wird allen gezeigt" : "✅ Präsentation beendet"); }
    else toast(r.error || "Fehler", "#dc2626");
  }

  document.addEventListener("click", async e => {
    const g = e.target.closest("[data-gruppe]"); if (!g) return;
    if (g.dataset.gruppe === "sperren" && !confirm("KI für die ganze Gruppe sperren? Wartende Anfragen werden abgelehnt.")) return;
    const r = await post("/api/lehrer/gruppenfreigabe", { aktion: g.dataset.gruppe });
    if (r.ok) { renderGruppe(r.gruppenfreigabe); toast(g.dataset.gruppe === "sperren" ? "🚫 Gruppe gesperrt" : "Aktualisiert"); } else toast(r.error || "Fehler", "#dc2626");
  });

  // ── Zwischenstände ──
  function renderSnapshots(list) {
    const host = $("#snapshot-list"); $("#snapshot-count").textContent = list.length;
    if (!list.length) { host.innerHTML = '<p class="empty-state">Noch keine Zwischenstände.</p>'; return; }
    host.innerHTML = list.map(s => `<div class="request-item" data-snap="${s.id}"><span class="request-typ">temp</span><div class="who"><strong>${esc(s.name)}</strong><small>${datum(s.created_at)} · ${Math.round((s.groesse || 0) / 1024)} KB</small></div>
      <button class="btn btn-primary btn-sm" type="button" data-snap-load="${s.id}">📥 Laden</button><button class="btn btn-danger-outline btn-sm" type="button" data-snap-del="${s.id}">✕</button></div>`).join("");
  }
  $("#snapshot-save").addEventListener("click", async () => {
    const r = await post("/api/lehrer/snapshots", { name: $("#snapshot-name").value.trim() });
    if (r.ok) { renderSnapshots(r.snapshots); $("#snapshot-name").value = ""; toast("💾 Zwischenstand gespeichert"); } else toast(r.error || "Fehler", "#dc2626");
  });
  document.addEventListener("click", async e => {
    const l = e.target.closest("[data-snap-load]");
    if (l) {
      if (!confirm("Diesen Zwischenstand laden? Die laufende Sitzung wird ersetzt, verbundene Lernende werden abgemeldet und der Fortsetzungsmodus startet.")) return;
      const r = await post(`/api/lehrer/snapshots/${l.dataset.snapLoad}/laden`);
      if (r.ok) { toast(`📥 ${r.lernende} Lernplätze geladen – Fortsetzungsmodus aktiv`); loadState(); } else toast(r.error || "Fehler", "#dc2626");
      return;
    }
    const d = e.target.closest("[data-snap-del]");
    if (d) { if (!confirm("Diesen Zwischenstand löschen?")) return; const r = await post(`/api/lehrer/snapshots/${d.dataset.snapDel}`, null, "DELETE"); if (r.ok) renderSnapshots(r.snapshots); else toast(r.error || "Fehler", "#dc2626"); }
  });

  // ── IServ ──
  function protokoll(html, fehler) { const p = $("#iserv-protokoll"); p.hidden = false; p.className = "protokoll " + (fehler ? "protokoll-err" : "protokoll-ok"); p.innerHTML = html; }
  $("#iserv-test").addEventListener("click", async () => {
    const r = await post("/api/lehrer/iserv/test");
    if (r.ok) { toast("🔌 Verbindung zu IServ ok"); protokoll(`Verbindung ok · Ordner „${esc(r.pfad)}“ erreichbar.`); } else { toast(r.error || "Fehler", "#dc2626"); protokoll("⚠️ " + esc(r.error || "Verbindung fehlgeschlagen"), true); }
  });
  function renderArchive(list) {
    const host = $("#iserv-archive");
    if (!list.length) { host.innerHTML = '<p class="empty-state">Keine Archive dieses Arbeitsblatts gefunden.</p>'; return; }
    host.innerHTML = list.map(a => `<div class="request-item" data-archiv="${esc(a.dateiname)}"><span class="request-typ">IServ</span><div class="who"><strong>${esc(a.name)}</strong><small>${esc(a.created_at_utc).replace("T", " ").slice(0, 16)} UTC · ${a.lernende} Lernende · ${a.antworten} Antworten · ${a.zeichnungen} Zeichnungen · ${Math.round(a.groesse / 1024)} KB</small></div>
      <button class="btn btn-quiet btn-sm" type="button" data-archiv-vorschau="${esc(a.dateiname)}">👁 Vorschau</button>
      <button class="btn btn-outline btn-sm" type="button" data-archiv-restore="ansicht" data-datei="${esc(a.dateiname)}">Ansicht</button>
      <button class="btn btn-primary btn-sm" type="button" data-archiv-restore="fortsetzung" data-datei="${esc(a.dateiname)}">Fortsetzungsstunde</button>
      <button class="btn btn-danger-outline btn-sm" type="button" data-archiv-del="${esc(a.dateiname)}">✕</button></div>`).join("");
  }
  $("#iserv-list").addEventListener("click", async () => {
    $("#iserv-archive").innerHTML = '<p class="empty-state">Archive werden geladen und entschlüsselt …</p>';
    const r = await get("/api/lehrer/iserv/archive");
    if (r.ok) renderArchive(r.archive); else { $("#iserv-archive").innerHTML = ""; toast(r.error || "Fehler", "#dc2626"); protokoll("⚠️ " + esc(r.error || ""), true); }
  });
  $("#iserv-abschluss").addEventListener("click", async () => {
    const name = $("#iserv-name").value.trim();
    if (!confirm("Stunde abschließen?\n\nDer komplette Stand wird verschlüsselt auf IServ archiviert. Erst nach erfolgreicher Prüfung werden alle Daten auf dem App-Server gelöscht und die Lernenden abgemeldet.")) return;
    const btn = $("#iserv-abschluss"); btn.disabled = true; btn.textContent = "⏳ Archivierung läuft …";
    const r = await post("/api/lehrer/iserv/abschluss", { name });
    btn.disabled = false; btn.textContent = "🔒 Stunde abschließen & archivieren";
    if (r.ok) {
      const p = r.protokoll;
      protokoll(`<strong>✅ Archiv geschrieben und verifiziert.</strong><br>Datei: ${esc(p.dateiname)}<br>Digest: <code>${esc((p.digest || "").slice(0, 16))}…</code><br>Flush: ${p.flush.confirmed.length} bestätigt, ${p.flush.missing.length} ohne Antwort (offline-Geräte sind durch ihre früheren Autosaves abgedeckt)<br>${p.schritte.map(esc).join("<br>")}`);
      toast("🔒 Stunde archiviert, Server bereinigt"); loadState();
    } else { protokoll("⚠️ " + esc(r.error || "Archivierung fehlgeschlagen") + " – es wurde nichts gelöscht.", true); toast("Archivierung fehlgeschlagen – Daten bleiben erhalten", "#dc2626"); }
  });
  document.addEventListener("click", async e => {
    const v = e.target.closest("[data-archiv-vorschau]");
    if (v) { const r = await post("/api/lehrer/iserv/vorschau", { dateiname: v.dataset.archivVorschau }); if (r.ok) { const a = r.archiv; protokoll(`<strong>Vorschau „${esc(a.name)}“</strong> · ${a.lernende} Lernende · ${a.antworten} Antworten · ${a.arbeitsstaende} Arbeitsstände · ${a.zeichnungen} Zeichnungen · ${a.chat_messages} KI-Nachrichten<br>${esc(a.pseudonyme.join(", "))}`); } else protokoll("⚠️ " + esc(r.error || ""), true); return; }
    const w = e.target.closest("[data-archiv-restore]");
    if (w) {
      const modus = w.dataset.archivRestore;
      const text = modus === "ansicht" ? "Archiv zur Ansicht laden? Die laufende Sitzung wird ersetzt; Lernende können sich NICHT automatisch wieder verbinden (Ansichtsmodus)." : "Archiv als Fortsetzungsstunde laden? Die laufende Sitzung wird ersetzt; Geräte mit passendem Schlüssel verbinden sich automatisch, andere warten auf Zuordnung.";
      if (!confirm(text)) return;
      const r = await post("/api/lehrer/iserv/wiederherstellen", { dateiname: w.dataset.datei, modus });
      if (r.ok) { toast(`📥 ${r.lernende} Lernplätze geladen (${modus})`); loadState(); } else toast(r.error || "Fehler", "#dc2626");
      return;
    }
    const d = e.target.closest("[data-archiv-del]");
    if (d) { if (!confirm("Dieses Archiv auf IServ endgültig löschen?")) return; const r = await post("/api/lehrer/iserv/loeschen", { dateiname: d.dataset.archivDel }); if (r.ok) { toast("Archiv gelöscht"); $("#iserv-list").click(); } else toast(r.error || "Fehler", "#dc2626"); }
  });

  // ── Fortsetzung ──
  function renderFortsetzung(f) {
    const pill = $("#fortsetzung-pill"); pill.textContent = f.active ? "aktiv" : "inaktiv"; pill.className = "pill " + (f.active ? "pill-open" : "pill-offline");
    const frei = (f.ziele || []).filter(z => z.status === "verfuegbar");
    $("#fortsetzung-ziele").textContent = f.active ? `Quelle: ${f.source_name || "–"} · seit ${zeit(f.started_at)} · ${frei.length} von ${(f.ziele || []).length} alten Lernplätzen noch nicht vergeben.` : "";
    const host = $("#fortsetzung-anfragen");
    if (!(f.anfragen || []).length) { host.innerHTML = '<p class="empty-state">Keine wartenden Lernenden.</p>'; return; }
    host.innerHTML = f.anfragen.map(a => {
      const options = frei.map(z => `<option value="${esc(z.student_id)}"${a.kandidaten.length === 1 && a.kandidaten[0] === z.student_id ? " selected" : ""}>${esc(z.pseudonym)} (${esc(z.klasse)})</option>`).join("");
      const hinweis = a.kandidaten.length === 1 ? "eindeutiger Treffer" : a.kandidaten.length > 1 ? `${a.kandidaten.length} mögliche Treffer – bitte wählen` : "kein Treffer – neuer Lernplatz?";
      return `<div class="request-item is-new" data-anfrage="${esc(a.id)}"><span class="request-typ">wartet</span><div class="who"><strong>${esc(a.pseudonym)}</strong><small>Klasse ${esc(a.klasse)} · ${zeit(a.created_at)} · ${hinweis}</small></div>
        <select data-ziel-select aria-label="Alter Lernplatz"><option value="">– alten Lernplatz wählen –</option>${options}</select>
        <button class="btn btn-primary btn-sm" type="button" data-fs="zuordnen" data-id="${esc(a.id)}">Zuordnen</button>
        <button class="btn btn-outline btn-sm" type="button" data-fs="neustart" data-id="${esc(a.id)}">Neu starten</button>
        <button class="btn btn-danger-outline btn-sm" type="button" data-fs="ablehnen" data-id="${esc(a.id)}">Ablehnen</button></div>`;
    }).join("");
  }
  $("#fortsetzung-auto").addEventListener("click", async () => { const r = await post("/api/lehrer/fortsetzung/auto"); if (r.ok) toast(`✨ ${r.zugeordnet} zugeordnet · ${r.mehrdeutig} mehrdeutig · ${r.ohne_treffer} ohne Treffer`); else toast(r.error || "Fehler", "#dc2626"); });
  $("#fortsetzung-beenden").addEventListener("click", async () => { if (!confirm("Fortsetzungsmodus beenden? Wartende Lernende starten mit einem neuen Lernplatz; verbundene bleiben erhalten.")) return; const r = await post("/api/lehrer/fortsetzung/beenden"); if (r.ok) toast("Fortsetzungsmodus beendet"); else toast(r.error || "Fehler", "#dc2626"); });
  document.addEventListener("click", async e => {
    const b = e.target.closest("[data-fs]"); if (!b) return;
    const item = b.closest(".request-item"); const ziel = item.querySelector("[data-ziel-select]").value;
    if (b.dataset.fs === "zuordnen" && !ziel) { toast("Bitte zuerst einen alten Lernplatz wählen", "#d97706"); return; }
    const r = await post("/api/lehrer/fortsetzung/zuordnen", { anfrage_id: b.dataset.id, aktion: b.dataset.fs, target_student_id: ziel });
    if (r.ok) toast("Erledigt: " + r.status); else toast(r.error || "Fehler", "#dc2626");
  });

  // ── Aktionen Tabelle ──
  document.addEventListener("click", async e => {
    const decide = e.target.closest("[data-decide]");
    if (decide) {
      decide.disabled = true;
      const r = await post("/api/ki-entscheidung", { anfrage_id: parseInt(decide.dataset.id, 10), entscheid: decide.dataset.decide });
      if (r.ok) { const a = requests[decide.dataset.id]; removeRequest(decide.dataset.id, a && a.schueler_id); toast(decide.dataset.decide === "freigegeben" ? "✅ Freigegeben" : "Abgelehnt", decide.dataset.decide === "freigegeben" ? "#16a34a" : "#dc2626"); }
      else decide.disabled = false;
      return;
    }
    const lock = e.target.closest("[data-lock]");
    if (lock) {
      const sid = lock.dataset.lock;
      const r = await post("/api/lehrer/ki-sperren", { schueler_id: sid, aktion: gesperrt.has(sid) ? "freigeben" : "sperren" });
      if (r.ok) { if (r.gesperrt) gesperrt.add(sid); else gesperrt.delete(sid); upsertStudent(students[sid]); }
      return;
    }
    const del = e.target.closest("[data-delete]");
    if (del) {
      const s = students[del.dataset.delete];
      if (!confirm(`Alle Daten von „${s ? s.pseudonym : "?"}“ endgültig löschen?`)) return;
      const r = await post("/api/lehrer/daten-loeschen", { schueler_id: del.dataset.delete });
      if (r.ok) { removeStudent(del.dataset.delete); toast("🗑️ Daten gelöscht", "#64748b"); }
      return;
    }
    if (e.target.id === "reset-session") {
      if (!confirm("Wirklich alle Lernenden, Antworten, Arbeitsstände, Zeichnungen und Anfragen dieser Sitzung löschen? Zwischenstände bleiben erhalten.")) return;
      const r = await post("/api/lehrer/sitzung-zuruecksetzen");
      if (r.ok) { Object.keys(students).forEach(removeStudent); renderRequests([]); toast("Sitzung zurückgesetzt", "#64748b"); }
    }
    if (e.target.id === "refresh-dashboard") loadState();
  });

  async function loadState() {
    const d = await get("/api/lehrer/state");
    if (!d.ok) return;
    gesperrt = new Set(d.gesperrt || []);
    Object.keys(students).forEach(k => delete students[k]);
    $("#student-table").innerHTML = '<tr id="no-students"><td colspan="12" class="empty-state">Noch niemand angemeldet.</td></tr>';
    (d.schueler || []).slice().reverse().forEach(upsertStudent);
    renderRequests(d.anfragen || []);
    renderBudget(d.budget);
    renderHakt(d.hakt);
    renderVermutungen(d.vermutungen);
    renderGruppe(d.gruppenfreigabe || {});
    praesBilderFuellen(d.praesentation_bilder);
    renderPraes(d.praesentation);
    renderSnapshots(d.snapshots || []);
    renderFortsetzung(d.fortsetzung || {});
    const st = d.iserv || {};
    $("#iserv-status").textContent = st.konfiguriert ? `Ziel: ${st.host} · ${st.pfad} · Marker ${st.marker}` : (st.fehler || "IServ nicht konfiguriert");
    $("#iserv-pill").textContent = st.konfiguriert ? "IServ konfiguriert" : "IServ nicht konfiguriert";
    $("#iserv-pill").className = "pill " + (st.konfiguriert ? "pill-open" : "pill-offline");
  }

  // ── Socket ──
  function setupSocket() {
    if (typeof io === "undefined") { loadState(); return; }
    const socket = io({ transports: ["polling", "websocket"] });   // erst Polling, dann Upgrade: scheitert der WebSocket, bleibt die Live-Verbindung trotzdem
    socket.on("connect", () => socket.emit("lehrer_join", { token: DASH.token }));
    socket.on("alle_schueler", list => { Object.keys(students).forEach(k => delete students[k]); $("#student-table").innerHTML = '<tr id="no-students"><td colspan="12" class="empty-state">Noch niemand angemeldet.</td></tr>'; list.slice().reverse().forEach(upsertStudent); });
    socket.on("sperr_status_all", d => { gesperrt = new Set(d.gesperrt || []); Object.values(students).forEach(upsertStudent); });
    socket.on("offene_anfragen", list => renderRequests(list));
    socket.on("token_update", renderBudget);
    socket.on("neuer_schueler", s => { upsertStudent(s); toast(`👋 ${s.pseudonym} (Klasse ${s.klasse}) hat sich angemeldet`, "#006AB3"); });
    socket.on("schueler_online", s => upsertStudent(Object.assign({}, s, { online: true })));
    socket.on("schueler_offline", d => { if (students[d.id]) { students[d.id].online = false; upsertStudent(students[d.id]); } });
    socket.on("fortschritt_update", s => upsertStudent(s));
    socket.on("antwort_zaehler", d => { if (students[d.schueler_id]) { students[d.schueler_id].antworten = d.antworten; upsertStudent(students[d.schueler_id]); } haktLaden(); vermLaden(); });
    socket.on("autosave_update", d => { if (students[d.schueler_id]) { students[d.schueler_id].autosave_at = d.updated_at; students[d.schueler_id].autosave_revision = d.revision; upsertStudent(students[d.schueler_id]); } });
    socket.on("neue_anfrage", addRequest);
    socket.on("anfrage_erledigt", d => removeRequest(d.anfrage_id, d.schueler_id));
    socket.on("schueler_geloescht", d => removeStudent(d.id));
    socket.on("ki_sperr_status", d => { if (d.gesperrt) gesperrt.add(d.schueler_id); else gesperrt.delete(d.schueler_id); if (students[d.schueler_id]) upsertStudent(students[d.schueler_id]); });
    socket.on("gruppenfreigabe_update", renderGruppe);
    socket.on("praesentation_update", renderPraes);
    socket.on("fortsetzung_update", renderFortsetzung);
    socket.on("sitzung_zurueckgesetzt", () => loadState());
    loadState();
  }
  document.addEventListener("DOMContentLoaded", () => { renderBudget({ today: parseInt($("#kpi-tokens").textContent, 10) || 0, limit: DASH.limit || 1 }); setupSocket(); });

  // Bedienung des Präsentationsmodus
  document.addEventListener("click", e => {
    const el = e.target.closest("#praes-start, #praes-stop");
    if (!el) return;
    praesSenden(el.id === "praes-start");
  });
  document.addEventListener("change", e => { if (e.target.id === "praes-bild") praesVorschau(); });

})();
