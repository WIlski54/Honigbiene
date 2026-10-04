/* Gegatete Lesestrecke: ein Abschnitt sichtbar, Frage als Schleuse, Sperre nach Fehlversuch.
   Lösungen und Sperren liegen auf dem Server; ein Reload umgeht die Sperre nicht. */
BIE.lesestrecke = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, shuffle, showToast, postJSON, getJSON, markComplete, dirty, lesestreckeNr } = BIE;
  const daten = {};      // key -> Serverdaten
  const timers = {};     // key -> Countdown-Intervall
  const laden = {};      // key -> Promise

  function station(key) { return lesestreckeNr[key]; }
  // Text und Schaubild nebeneinander; in der Fragephase bleibt beides ausgeblendet.
  // Schaubild als Knopf: Tippen öffnet es bildschirmfüllend (bild.js) – auf dem iPad sonst zu klein.
  const inhalt = a => `<div class="lese-inhalt"><div class="lese-text">${a.text}</div>${a.bild ? `<figure class="lese-figur"><button type="button" class="bild-zoom" data-action="bild-open" aria-label="Schaubild vergrößern"><img src="${esc(a.bild)}" alt="${esc(a.bild_alt || "Schaubild")}" loading="lazy"></button><figcaption class="bild-hinweis">🔍 Tippen zum Vergrößern</figcaption></figure>` : ""}</div>`;

  // ─── Prüfmodus: alle Abschnitte offen, Frage mit markierter Lösung ───
  let pruefDaten = null;
  async function mountPruef(key) {
    const host = document.getElementById("lese-" + key); if (!host) return;
    if (!pruefDaten) {
      const d = await getJSON("/api/lehrer/pruefen/lesestrecken");
      if (!d || !d.ok) { host.innerHTML = `<article class="card intro-card"><span class="eyebrow">Lesestrecke</span><p class="muted">⚠️ ${esc(d && d.fehler ? d.fehler : "Lesestrecken konnten nicht geladen werden.")}</p></article>`; return; }
      pruefDaten = d.lesestrecken;
    }
    const d = pruefDaten[key]; if (!d) return;
    let html = `<article class="card intro-card lese-card" id="lese-card-${key}">
      <header class="task-header">
        <span class="task-number task-number-lese" aria-hidden="true">${esc(station(key))}</span>
        <div class="task-title"><span class="eyebrow">${esc(d.eyebrow)} · Prüfmodus: ${d.anzahl} Abschnitte, Lösung grün</span><h2>${esc(d.titel)}</h2></div>
      </header>`;
    d.abschnitte.forEach((a, i) => {
      html += `<section class="lese-now lese-pruef"><h3>${i + 1}. ${esc(a.ueberschrift)}</h3>${inhalt(a)}
        <div class="lese-frage"><p class="task-question">❓ ${esc(a.frage)}</p>
        <div class="mc-options" role="group">${a.optionen.map((o, j) => `<button class="mc-btn${j === a.loesung ? " correct" : ""}" type="button" disabled>${esc(o)}</button>`).join("")}</div>
        <p class="lese-erkl">💡 ${esc(a.erklaerung)}</p></div></section>`;
    });
    host.innerHTML = html + `</article>`;
    if (BIE.glossar) BIE.glossar.verlinken(host);
  }

  async function mount(key, force) {
    if (BIE.pruefmodus) return mountPruef(key);
    const host = document.getElementById("lese-" + key);
    if (!host) return;
    if (daten[key] && !force) return;
    if (laden[key]) return laden[key];
    if (!daten[key]) host.innerHTML = `<article class="card intro-card"><span class="eyebrow">Lesestrecke</span><p class="muted">Lesestrecke wird geladen …</p></article>`;
    laden[key] = getJSON("/api/lesestrecke/" + key).then(d => {
      delete laden[key];
      if (!d || !d.ok) { host.innerHTML = `<article class="card intro-card"><span class="eyebrow">Lesestrecke</span><p class="muted">⚠️ ${esc(d && d.fehler ? d.fehler : "Lesestrecke konnte nicht geladen werden.")} <button class="btn btn-outline btn-sm" type="button" data-action="lese-reload" data-key="${key}">Erneut laden</button></p></article>`; return; }
      daten[key] = d;
      render(key);
    });
    return laden[key];
  }

  function render(key) {
    const d = daten[key]; const host = document.getElementById("lese-" + key);
    if (!d || !host) return;
    const st = d.status; const n = d.anzahl; const jetzt = Date.now() / 1000;
    clearInterval(timers[key]);
    const gelesen = d.abschnitte.slice(0, st.fertig ? n : st.phase);
    let html = `<article class="card intro-card lese-card" id="lese-card-${key}">
      <header class="task-header">
        <span class="task-number task-number-lese" aria-hidden="true">${esc(station(key))}</span>
        <div class="task-title"><span class="eyebrow">${esc(d.eyebrow)}</span><h2>${esc(d.titel)}</h2></div>
        <span class="done-badge"${st.fertig ? "" : " hidden"}>✅ gelesen</span>
      </header>
      <p class="lese-progress" role="status">${st.fertig ? `Alle ${n} Abschnitte gelesen – zum Nachschlagen aufklappen.` : `Abschnitt ${st.phase + 1} von ${n}`} <span class="lese-dots" aria-hidden="true">${Array.from({ length: n }, (_, i) => `<i class="${i < st.phase || st.fertig ? "done" : i === st.phase ? "now" : ""}"></i>`).join("")}</span></p>`;
    gelesen.forEach((a, i) => {
      html += `<details class="lese-done"><summary>✅ ${i + 1}. ${esc(a.ueberschrift)}</summary>${inhalt(a)}${a.erklaerung ? `<p class="lese-erkl">💡 ${esc(a.erklaerung)}</p>` : ""}</details>`;
    });
    if (!st.fertig) {
      const a = d.abschnitte[st.phase];
      const gesperrt = st.retry_until > jetzt;
      const frageModus = !gesperrt && state.runtime["lese-" + key] && state.runtime["lese-" + key].frage;
      html += `<section class="lese-now" aria-live="polite"><h3>${st.phase + 1}. ${esc(a.ueberschrift)}</h3>${frageModus ? "" : inhalt(a)}`;
      if (gesperrt) {
        const rest = Math.ceil(st.retry_until - jetzt);
        html += `<div class="feedback-box feedback-err show">❌ Das war nicht richtig. Lies den Abschnitt noch einmal in Ruhe – die Frage kommt in <strong id="lese-count-${key}">${rest}</strong> Sekunden wieder.</div>`;
        timers[key] = setInterval(() => {
          const r = Math.ceil(st.retry_until - Date.now() / 1000);
          const el = document.getElementById("lese-count-" + key);
          if (r <= 0) { clearInterval(timers[key]); st.retry_until = 0; render(key); }
          else if (el) el.textContent = r;
        }, 1000);
      } else if (frageModus) {
        const opts = shuffle(a.optionen.map((t, i) => ({ t, i })));
        html += `<div class="lese-frage"><p class="hint">Der Text ist jetzt ausgeblendet. Beantworte die Frage aus dem Gedächtnis.</p><p class="task-question">🔒 ${esc(a.frage)}</p><div class="mc-options" role="group">${opts.map(o => `<button class="mc-btn" type="button" data-action="lese-antwort" data-key="${key}" data-phase="${st.phase}" data-wahl="${o.i}">${esc(o.t)}</button>`).join("")}</div>
          <div class="btn-row"><button class="btn btn-quiet btn-sm" type="button" data-action="lese-zurueck" data-key="${key}">← Abschnitt noch einmal lesen</button></div></div>`;
      } else {
        html += `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="lese-weiter" data-key="${key}">Gelesen – zur Frage →</button></div>`;
      }
      html += `</section>`;
    } else {
      html += `<p class="hint">Fachbegriffe: ${(INHALTE.tabs.find(t => t.key === key) || { intro: { begriffe: [] } }).intro.begriffe.map(b => `<em>${esc(b)}</em>`).join(", ")}</p>`;
    }
    html += `</article>`;
    host.innerHTML = html;
    if (BIE.glossar) BIE.glossar.verlinken(host);
    if (st.fertig && !state.completed.has(station(key))) markComplete(station(key));
    if (BIE.schritte) BIE.schritte.aktualisieren(key);
  }

  BIE.actions["lese-reload"] = el => mount(el.dataset.key, true);
  BIE.actions["lese-weiter"] = el => { state.runtime["lese-" + el.dataset.key] = { frage: true }; render(el.dataset.key); dirty(); };
  BIE.actions["lese-zurueck"] = el => { state.runtime["lese-" + el.dataset.key] = { frage: false }; render(el.dataset.key); };
  BIE.actions["lese-antwort"] = async el => {
    const key = el.dataset.key;
    $$(".mc-btn", el.closest(".mc-options")).forEach(b => { b.disabled = true; });
    const r = await postJSON(`/api/lesestrecke/${key}/antwort`, { phase: parseInt(el.dataset.phase, 10), wahl: parseInt(el.dataset.wahl, 10) });
    if (r.offline || (r.fehler && r.httpStatus !== 429 && r.httpStatus !== 409)) {
      $$(".mc-btn", el.closest(".mc-options")).forEach(b => { b.disabled = false; });
      showToast("⚠️ Keine Verbindung – die Antwort wurde nicht gewertet. Bitte noch einmal.", "#d97706");
      return;
    }
    if (r.httpStatus === 409 || r.httpStatus === 429) { await mount(key, true); return; }
    daten[key].status = r.status;
    state.runtime["lese-" + key] = { frage: false };
    if (r.korrekt) {
      const a = daten[key].abschnitte[parseInt(el.dataset.phase, 10)];
      a.erklaerung = r.erklaerung;
      showToast("✅ Richtig – weiter geht's!");
      if (r.status.fertig) { markComplete(station(key)); showToast("📘 Lesestrecke abgeschlossen!", "#AD007C"); }
    } else {
      el.classList.add("incorrect");
      setTimeout(() => render(key), 700);
      return;
    }
    render(key);
    dirty();
  };

  INHALTE.tabs.forEach(tab => { if (lesestreckeNr[tab.key]) BIE.beimOeffnen[tab.key] = () => mount(tab.key); });

  BIE.autosave.register("lesestrecke", () => {
    const out = {};
    Object.entries(daten).forEach(([k, d]) => { out[k] = Object.assign({}, d.status); });
    return out;
  }, async () => {
    // Der Server ist die Quelle der Wahrheit (Sperren, Phasen); geladene Strecken werden neu geholt.
    await Promise.all(Object.keys(daten).map(k => mount(k, true)));
  }, 40);

  return { mount, render };
})();
