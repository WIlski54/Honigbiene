/* Aufgaben-Renderer mit Serialisierung: MC (auch als Richtig/Falsch-Liste), Lückentext, Zuordnung, Sortierung,
   Diagramm, Freitext, Notizen (mit Handschrift-Pad), Quellenverzeichnis, Transfer.
   Weitere Typen liefern eigene Module: bildpunkte.js, zeichnen.js, spiele.js (Blitz, Domino), film.js
   (film, filmmoment), modell3d.js (erkunden, modellfinden) und forschen.js (vermutung, pruefen, protokoll, tabelle,
   bildwahl, forscherbuch).
   Jeder Typ kann seinen Zustand für den Autosave sammeln und wiederherstellen. */
BIE.aufgaben = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, shuffle, normalize, isDifferenziert, niveauOf, cfgOf, card, body, showFb, clearFb, retryBtn, markComplete, sendAntwort, dirty, aufgabenByNr, NIVEAU_LABEL, postJSON, anzeigeNr } = BIE;

  // ─── Aufbau der Reiter ─────────────────────────────────────────────────
  // Karten und Lesestrecke in der Reihenfolge des Plans: Die Lesestrecke („Nachschlagen“) steht direkt nach der
  // Aufgabe tab.leseNach, ohne leseNach ganz oben (BIE.stationenVon, kern.js).
  function buildPanels() {
    const host = $("#panels");
    host.innerHTML = INHALTE.tabs.map(tab => `
      <section class="tab-panel" id="tab-${tab.key}" data-panel="${tab.key}" role="tabpanel" hidden>
        ${BIE.stationenVon(tab).map(nr => nr === BIE.lesestreckeNr[tab.key] ? `<div id="lese-${tab.key}"></div>` : renderCardShell(aufgabenByNr[nr])).join("")}
      </section>`).join("");
    INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(renderBody));
  }

  function renderCardShell(t) {
    const an = anzeigeNr(t.nr);   // sichtbar: fortlaufende Nummer 1, 2, 3 … (intern bleibt t.nr, siehe static/js/anzeige.js)
    const select = isDifferenziert(t) ? `
      <select class="niveau-select" data-action="niveau" data-nr="${t.nr}" aria-label="Niveau Aufgabe ${an}">
        ${["A", "B", "C"].map(n => `<option value="${n}"${niveauOf(t.nr) === n ? " selected" : ""}>${NIVEAU_LABEL[n]}</option>`).join("")}
      </select>` : "";
    return `
      <article class="card task-card" id="card-${t.nr}" data-nr="${t.nr}" data-typ="${t.typ}">
        <header class="task-header">
          <span class="task-number" aria-hidden="true">${an}</span>
          <div class="task-title"><span class="eyebrow">${esc(t.eyebrow)}</span><h3>Aufgabe ${an}: ${esc(t.titel)}</h3></div>
          ${select}
          <span class="done-badge" hidden>✅ erledigt</span>
        </header>
        <div class="task-body" id="body-${t.nr}"></div>
        <div class="feedback-box" id="fb-${t.nr}" role="status" aria-live="polite"></div>
      </article>`;
  }

  // Hilfesatz nach einer falschen Antwort: `cfg.hilfe` (Text je Niveau, siehe docs/INHALTE_FORMAT.md) oder – ohne eigenen Text – NEUTRAL:
  // „Schau noch einmal genau hin.“ Ein Verweis auf die Lesestrecke steht nur, wenn die Aufgabe ihn selbst in `hilfe` setzt
  // (die Lesestrecke enthält die Antwort oft gar nicht, oder sie kommt im forschenden Ablauf erst später).
  const hilfe = (nr, cfg) => {
    if (cfg && typeof cfg.hilfe === "string" && cfg.hilfe.trim()) return esc(cfg.hilfe.trim());
    return "Schau noch einmal genau hin.";
  };
  // Eine Aufgabe läuft im Baustein-Modus, wenn ihr aktuelles Niveau das vorgibt.
  const istBausteine = t => (t.typ === "transfer" || t.typ === "freitext") && (cfgOf(t) || {}).modus === "bausteine";
  const renderers = {};
  function renderBody(t) {
    const host = body(t.nr);
    if (!host) return;
    clearFb(t.nr);
    state.runtime[t.nr] = {};
    if (state.charts[t.nr]) { state.charts[t.nr].destroy(); delete state.charts[t.nr]; }
    if (t.typ === "zeichnen" && BIE.zeichnen) BIE.zeichnen.dispose(t.nr);
    const r = renderers[t.typ]
      || (BIE.bildpunkte && t.typ === "bildpunkte" ? BIE.bildpunkte.render : null)
      || (BIE.zeichnen && t.typ === "zeichnen" ? BIE.zeichnen.render : null)
      || (BIE.spiele && (t.typ === "blitz" || t.typ === "domino") ? BIE.spiele.render : null)
      || (BIE.film && (t.typ === "film" || t.typ === "filmmoment") ? BIE.film.render : null)
      || (BIE.modell3d && (t.typ === "erkunden" || t.typ === "modellfinden") ? BIE.modell3d.render : null)
      || (BIE.forschen && BIE.forschen.istMein(t) ? BIE.forschen.render : null);
    host.innerHTML = r ? r(t) : "<p>Unbekannter Aufgabentyp.</p>";
    if (t.typ === "diagramm" && !card(t.nr).closest(".tab-panel").hidden) ensureChart(t);
    if (t.typ === "quellen") fillQuellen(t);
    if (t.typ === "zeichnen" && BIE.zeichnen) BIE.zeichnen.mount(t);
    if (t.typ === "notizen" && BIE.zeichnen) BIE.zeichnen.mountPad(t);
    if ((t.typ === "blitz" || t.typ === "domino") && BIE.spiele) BIE.spiele.mount(t);
    if (istBausteine(t) && state.runtime[t.nr] && state.runtime[t.nr].modus === "bausteine") bausteineZeichnen(t.nr);
    if (t.typ === "bildpunkte" && BIE.bildpunkte) BIE.bildpunkte.nachRender(t);   // Punktgrößen für Finger (bildpunkte.js)
    if (BIE.film) BIE.film.nachRender(t);          // Film-Aufgaben und Modell-Knöpfe (film.js)
    if (BIE.modell3d) BIE.modell3d.nachRender(t);  // Erkunden / Modell finden (modell3d.js)
    if (BIE.forschen) BIE.forschen.nachRender(t);  // Vermutung, Prüfen, Protokoll, Tabelle, Bildwahl, Forscherbuch (forschen.js)
  }

  // ─── Multiple Choice ───────────────────────────────────────────────────
  function renderMC(nr, cfg, hidden) {
    const opts = shuffle(cfg.optionen.map((o, i) => ({ ...o, i })));
    return `
      <div class="mc-block" id="mc-${nr}"${hidden ? " hidden" : ""}>
        <p class="task-question">${esc(cfg.frage)}</p>
        <div class="mc-options" data-multi="${cfg.multi || 1}" role="group" aria-label="Antwortmöglichkeiten">
          ${opts.map(o => `<button class="mc-btn" type="button" data-action="mc" data-nr="${nr}" data-idx="${o.i}" data-ok="${o.ok}">${esc(o.t)}</button>`).join("")}
        </div>
        ${cfg.multi ? `<p class="hint">💡 Wähle genau ${cfg.multi} richtige Aussagen.</p>` : ""}
      </div>`;
  }
  // Eine MC-Aufgabe läuft als Richtig/Falsch-Liste, wenn ihr aktuelles Niveau `aussagen` angibt
  // ([{t: "Aussage", ok: true|false, erklaerung?}]). Typ der Aufgabe bleibt "mc".
  const istRF = t => t.typ === "mc" && Array.isArray((cfgOf(t) || {}).aussagen);
  renderers.mc = t => (istRF(t) ? renderRF(t.nr, cfgOf(t)) : renderMC(t.nr, cfgOf(t)));


  // ─── Richtig/Falsch-Liste (MC-Variante) ────────────────────────────────
  function renderRF(nr, cfg) {
    state.runtime[nr].rf = { wahl: cfg.aussagen.map(() => null), geprueft: false };
    return `
      <div class="rf-block" id="rf-${nr}">
        <p class="task-question">${esc(cfg.frage || "Stimmt das?")}</p>
        <div class="rf-liste">
          ${cfg.aussagen.map((a, i) => `
            <div class="rf-zeile" id="rf-${nr}-${i}" data-i="${i}">
              <p class="rf-text">${esc(a.t)}</p>
              <div class="rf-knoepfe" role="group" aria-label="Stimmt die Aussage?">
                <button class="mc-btn rf-btn" type="button" data-action="rf" data-nr="${nr}" data-i="${i}" data-wahl="r">✅ stimmt</button>
                <button class="mc-btn rf-btn" type="button" data-action="rf" data-nr="${nr}" data-i="${i}" data-wahl="f">❌ stimmt nicht</button>
              </div>
            </div>`).join("")}
        </div>
        <p class="hint">💡 Beurteile jede Aussage. Dann tippe auf „Prüfen“.</p>
        <div class="btn-row">
          <button class="btn btn-primary" type="button" data-action="rf-pruefen" data-nr="${nr}">✅ Prüfen</button>
          <button class="btn btn-outline" type="button" data-action="rf-reset" data-nr="${nr}">🔄 Zurücksetzen</button>
        </div>
      </div>`;
  }
  function rfZeichnen(nr) {
    const rt = state.runtime[nr] && state.runtime[nr].rf; if (!rt) return;
    $$(".rf-btn", body(nr)).forEach(b => b.classList.toggle("selected-multi", rt.wahl[parseInt(b.dataset.i, 10)] === b.dataset.wahl));
  }
  function rfPruefen(nr, silent) {
    const t = aufgabenByNr[nr], cfg = cfgOf(t), rt = state.runtime[nr].rf;
    if (!rt) return;
    const offen = rt.wahl.filter(w => w === null).length;
    if (offen) { if (!silent) showFb(nr, "err", `⚠️ Beurteile erst alle Aussagen. Es fehlen noch ${offen}.`); return; }
    let richtig = 0;
    const zeilen = cfg.aussagen.map((a, i) => {
      const ok = rt.wahl[i] === (a.ok ? "r" : "f");
      if (ok) richtig++;
      const z = document.getElementById(`rf-${nr}-${i}`);
      if (z) { z.classList.toggle("correct", ok); z.classList.toggle("incorrect", !ok); }
      return `${ok ? "✅" : "❌"} ${a.t.slice(0, 60)} → ${rt.wahl[i] === "r" ? "stimmt" : "stimmt nicht"}`;
    });
    rt.geprueft = true;
    const alle = richtig === cfg.aussagen.length;
    if (!silent) sendAntwort(nr, "richtigfalsch", zeilen.join(" | ").slice(0, 390), alle, cfg.frage || t.titel);
    if (alle) {
      const erkl = cfg.aussagen.filter(a => a.erklaerung).map(a => `<li>${esc(a.erklaerung)}</li>`).join("");
      showFb(nr, "ok", "✅ Alles richtig!" + (erkl ? `<ul class="rf-erkl">${erkl}</ul>` : ""));
      markComplete(nr);
    } else {
      showFb(nr, "err", `❌ ${richtig} von ${cfg.aussagen.length} richtig. Die roten Aussagen stimmen noch nicht – denk noch einmal nach. ${hilfe(nr, cfg)}`);
    }
    dirty();
  }
  BIE.actions.rf = el => {
    const nr = el.dataset.nr, rt = state.runtime[nr] && state.runtime[nr].rf; if (!rt) return;
    const i = parseInt(el.dataset.i, 10);
    rt.wahl[i] = el.dataset.wahl;
    if (rt.geprueft) {   // nach einer Prüfung darf weiter korrigiert werden
      rt.geprueft = false;
      $$(".rf-zeile", body(nr)).forEach(z => z.classList.remove("correct", "incorrect"));
      clearFb(nr);
    }
    rfZeichnen(nr); dirty();
  };
  BIE.actions["rf-pruefen"] = el => rfPruefen(el.dataset.nr);
  BIE.actions["rf-reset"] = el => { renderBody(aufgabenByNr[el.dataset.nr]); dirty(); };
  function rfRestore(nr, data) {
    const t = aufgabenByNr[nr], cfg = cfgOf(t), rt = state.runtime[nr] && state.runtime[nr].rf;
    if (!rt || !data || !Array.isArray(data.wahl) || data.wahl.length !== cfg.aussagen.length) return;
    rt.wahl = data.wahl.map(w => (w === "r" || w === "f" ? w : null));
    rfZeichnen(nr);
    if (data.geprueft) rfPruefen(nr, true);
  }

  function mcAuswerten(nr, group, gewaehlt, silent) {
    const t = aufgabenByNr[nr];
    const cfg = cfgOf(t), zeigeLoesung = t.zeigeLoesung !== false;   // Aufgabenfeld zeigeLoesung: false = die richtige Antwort wird nach einem Fehler nicht verraten (Forscher-Aufgaben)
    const erkl = typeof cfg.erklaerung === "string" && cfg.erklaerung.trim() ? `<br>💡 ${esc(cfg.erklaerung.trim())}` : "";
    const multi = parseInt(group.dataset.multi, 10) || 1;
    const typ = t.typ === "mc" ? (multi > 1 ? "mc-multi" : "mc") : t.typ;
    const frage = $(".task-question", group.closest(".mc-block")).textContent;
    const buttons = $$(".mc-btn", group);
    const sel = buttons.filter(b => gewaehlt.includes(parseInt(b.dataset.idx, 10)));
    group.dataset.done = "1";
    buttons.forEach(b => { b.disabled = true; });
    const allOk = sel.length === multi && sel.every(b => b.dataset.ok === "true");
    sel.forEach(b => b.classList.add(b.dataset.ok === "true" ? "correct" : "incorrect"));
    if (!allOk && zeigeLoesung) buttons.forEach(b => { if (b.dataset.ok === "true") b.classList.add("correct"); });
    state.runtime[nr].mc = { gewaehlt, fertig: true, ok: allOk };

    if (!silent) sendAntwort(nr, typ, sel.map(b => b.textContent.trim()).join(" | "), allOk, frage);
    if (allOk) { showFb(nr, "ok", (multi > 1 ? `✅ Perfekt – ${multi === 2 ? "beide" : "alle " + multi} Aussagen stimmen!` : "✅ Richtig!") + erkl); markComplete(nr); }
    // Anfang der Fehlermeldung: neutral „Nicht ganz.“ (Standard); `cfg.falschText` (oder `falschText` an der Aufgabe) setzt einen eigenen Text
    else showFb(nr, "err", "❌ " + esc(typeof (cfg.falschText ?? t.falschText) === "string" && String(cfg.falschText ?? t.falschText).trim() ? String(cfg.falschText ?? t.falschText).trim() : "Nicht ganz.") + (zeigeLoesung ? (multi > 1 ? " Die richtigen Aussagen sind markiert." : " Die richtige Antwort ist markiert.") : "") + " " + hilfe(nr, cfg) + erkl, retryBtn(nr));
  }
  BIE.actions.mc = btn => {
    const nr = btn.dataset.nr;
    const group = btn.closest(".mc-options");
    if (group.dataset.done === "1") return;
    const multi = parseInt(group.dataset.multi, 10) || 1;
    const idx = parseInt(btn.dataset.idx, 10);
    if (multi === 1) { mcAuswerten(nr, group, [idx]); dirty(); return; }
    btn.classList.toggle("selected-multi");
    const selected = $$(".mc-btn.selected-multi", group).map(b => parseInt(b.dataset.idx, 10));
    state.runtime[nr].mc = { gewaehlt: selected, fertig: false };
    dirty();
    if (selected.length < multi) { showFb(nr, "info", `💡 ${selected.length} von ${multi} ausgewählt …`); return; }
    mcAuswerten(nr, group, selected);
  };
  function mcRestore(nr, data) {
    const group = $(`#mc-${nr} .mc-options`);
    if (!group || !data || !Array.isArray(data.gewaehlt)) return;
    if (data.fertig) mcAuswerten(nr, group, data.gewaehlt, true);
    else $$(".mc-btn", group).forEach(b => b.classList.toggle("selected-multi", data.gewaehlt.includes(parseInt(b.dataset.idx, 10))));
    state.runtime[nr].mc = data;
  }

  // ─── Lückentext ────────────────────────────────────────────────────────
  function parseGaps(text) {
    const parts = []; let last = 0; const re = /\[([^\]]+)\]/g; let m;
    while ((m = re.exec(text))) { parts.push({ text: text.slice(last, m.index) }); parts.push({ gap: m[1].split("|").map(s => s.trim()) }); last = re.lastIndex; }
    parts.push({ text: text.slice(last) });
    return parts;
  }
  renderers.luecke = t => {
    const cfg = cfgOf(t);
    const parts = parseGaps(cfg.text);
    const gaps = parts.filter(p => p.gap);
    let html = "";
    if (cfg.modus === "chips") {
      const words = shuffle(gaps.map(g => g.gap[0]).concat(cfg.ablenker || []));
      html += `<div class="word-bank" role="group" aria-label="Wortkiste"><span class="word-bank-label">📚 Wortkiste</span>${words.map((w, i) => `<button class="word-chip" type="button" id="chip-${t.nr}-${i}" data-action="chip" data-nr="${t.nr}" data-word="${esc(w)}">${esc(w)}</button>`).join("")}</div>`;
      html += `<div class="gap-text">${parts.map((p, i) => p.gap ? `<button type="button" class="gap-tap" data-action="gap-clear" data-nr="${t.nr}" data-answer="${esc(p.gap.join("|"))}" data-idx="${i}" aria-label="Lücke">___</button>` : esc(p.text)).join("")}</div>`;
      html += `<p class="hint">Tippe auf ein Wort – es füllt die nächste freie Lücke. Tippe auf eine gefüllte Lücke, um sie zu leeren.</p>`;
    } else {
      html += `<div class="gap-text">${parts.map(p => p.gap ? `<input class="gap-input" data-nr="${t.nr}" data-answer="${esc(p.gap.join("|"))}" placeholder="?" autocomplete="off" autocapitalize="off" aria-label="Lücke">` : esc(p.text)).join("")}</div>`;
      html += `<p class="hint">Schreibe die passenden Begriffe in die Lücken. Groß-/Kleinschreibung ist egal.</p>`;
    }
    html += `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="check-luecke" data-nr="${t.nr}">✅ Überprüfen</button><button class="btn btn-outline" type="button" data-action="reset-luecke" data-nr="${t.nr}">🔄 Zurücksetzen</button></div>`;
    return html;
  };
  function useChip(chip) {
    if (chip.disabled) return;
    const host = body(chip.dataset.nr);
    const gap = $$(".gap-tap:not(.filled)", host)[0];
    if (!gap) { showFb(chip.dataset.nr, "info", "Alle Lücken sind gefüllt – tippe auf eine Lücke, um sie zu leeren."); return; }
    gap.textContent = chip.dataset.word; gap.dataset.filled = chip.dataset.word; gap.dataset.chipId = chip.id;
    gap.classList.add("filled"); gap.classList.remove("correct", "incorrect");
    chip.disabled = true; chip.classList.add("used");
    dirty();
  }
  function clearGap(gap) {
    if (!gap.classList.contains("filled")) return;
    const chip = document.getElementById(gap.dataset.chipId);
    if (chip) { chip.disabled = false; chip.classList.remove("used"); }
    gap.textContent = "___"; gap.classList.remove("filled", "correct", "incorrect"); gap.dataset.filled = ""; delete gap.dataset.chipId;
    dirty();
  }
  function matches(value, answers) {
    const v = normalize(value);
    return answers.some(a => { const n = normalize(a); return v === n || (n.length > 6 && v.length >= 5 && (v === n.replace(/-/g, " ") || v.replace(/-/g, " ") === n.replace(/-/g, " "))); });
  }
  function checkLuecke(nr, silent) {
    const host = body(nr);
    const gaps = $$(".gap-tap, .gap-input", host);
    let correct = 0; const wrong = [];
    gaps.forEach(g => {
      const answers = g.dataset.answer.split("|");
      const val = g.classList.contains("gap-input") ? g.value : (g.dataset.filled || "");
      g.classList.remove("correct", "incorrect");
      if (val && matches(val, answers)) { g.classList.add("correct"); correct++; }
      else { g.classList.add("incorrect"); wrong.push(`${val || "leer"} statt ${answers[0]}`); }
    });
    const ok = correct === gaps.length;
    state.runtime[nr].geprueft = true;
    if (!silent) sendAntwort(nr, "luecke", ok ? "alle Lücken richtig" : wrong.join("; "), ok, `${correct}/${gaps.length} Lücken`);
    if (ok) { showFb(nr, "ok", "✅ Alle Lücken richtig!"); markComplete(nr); }
    else showFb(nr, "err", `❌ ${correct} von ${gaps.length} richtig. Rot markierte Lücken noch einmal prüfen. ${hilfe(nr, cfgOf(aufgabenByNr[nr]))}`);
    dirty();
  }
  function resetLuecke(nr) {
    const host = body(nr);
    $$(".word-chip", host).forEach(c => { c.disabled = false; c.classList.remove("used"); });
    $$(".gap-tap", host).forEach(g => { g.textContent = "___"; g.classList.remove("filled", "correct", "incorrect"); g.dataset.filled = ""; delete g.dataset.chipId; });
    $$(".gap-input", host).forEach(i => { i.value = ""; i.classList.remove("correct", "incorrect"); });
    state.runtime[nr].geprueft = false;
    clearFb(nr); dirty();
  }
  function lueckeCollect(nr) {
    const host = body(nr); if (!host) return undefined;
    const werte = $$(".gap-tap, .gap-input", host).map(g => g.classList.contains("gap-input") ? g.value : (g.dataset.filled || ""));
    return { typ: "luecke", werte, geprueft: !!state.runtime[nr].geprueft };
  }
  function lueckeRestore(nr, data) {
    const host = body(nr); if (!host || !data || !Array.isArray(data.werte)) return;
    const gaps = $$(".gap-tap, .gap-input", host);
    gaps.forEach((g, i) => {
      const w = data.werte[i] || "";
      if (g.classList.contains("gap-input")) { g.value = w; return; }
      if (!w) return;
      const chip = $$(".word-chip", host).find(c => c.dataset.word === w && !c.disabled);
      if (chip) { g.textContent = w; g.dataset.filled = w; g.dataset.chipId = chip.id; g.classList.add("filled"); chip.disabled = true; chip.classList.add("used"); }
    });
    if (data.geprueft) checkLuecke(nr, true);
  }
  BIE.actions.chip = useChip;
  BIE.actions["gap-clear"] = clearGap;
  BIE.actions["check-luecke"] = el => checkLuecke(el.dataset.nr);
  BIE.actions["reset-luecke"] = el => resetLuecke(el.dataset.nr);
  document.addEventListener("input", e => { if (e.target.classList && e.target.classList.contains("gap-input")) dirty(); });
  document.addEventListener("keydown", e => {
    if (e.key === "Enter" && e.target.classList && e.target.classList.contains("gap-input")) {
      e.preventDefault();
      const inputs = $$(".gap-input", body(e.target.dataset.nr)); const i = inputs.indexOf(e.target);
      if (i >= 0 && i < inputs.length - 1) inputs[i + 1].focus(); else checkLuecke(e.target.dataset.nr);
    }
  });

  // ─── Zuordnung ─────────────────────────────────────────────────────────
  renderers.zuordnung = t => {
    const cfg = cfgOf(t);
    const rechts = shuffle(cfg.paare.map((p, i) => ({ text: p[1], i })));
    state.runtime[t.nr] = { matched: [], total: cfg.paare.length, selected: null };
    return `
      <p class="hint">${esc(cfg.hinweis || "Tippe zuerst links auf einen Begriff, dann rechts auf die passende Erklärung.")}</p>
      <div class="match-columns">
        <div><div class="match-col-header">${esc(cfg.links)}</div>${cfg.paare.map((p, i) => `<button type="button" class="match-item" data-action="match-left" data-nr="${t.nr}" data-pair="${i}">${esc(p[0])}</button>`).join("")}</div>
        <div><div class="match-col-header">${esc(cfg.rechts)}</div>${rechts.map(r => `<button type="button" class="match-item" data-action="match-right" data-nr="${t.nr}" data-pair="${r.i}">${esc(r.text)}</button>`).join("")}</div>
      </div>
      <div class="btn-row"><button class="btn btn-outline" type="button" data-action="reset-match" data-nr="${t.nr}">🔄 Zurücksetzen</button></div>`;
  };
  function markPairMatched(nr, pairIdx) {
    const host = body(nr);
    $$(`.match-item[data-pair="${pairIdx}"]`, host).forEach(el => { el.classList.remove("selected"); el.classList.add("matched-ok"); el.disabled = true; });
  }
  BIE.actions["match-left"] = el => {
    if (el.classList.contains("matched-ok")) return;
    $$(".match-item.selected", body(el.dataset.nr)).forEach(e => e.classList.remove("selected"));
    el.classList.add("selected");
    state.runtime[el.dataset.nr].selected = el;
  };
  BIE.actions["match-right"] = el => {
    const nr = el.dataset.nr; const rt = state.runtime[nr];
    if (!rt.selected || el.classList.contains("matched-ok")) { if (!rt.selected) showFb(nr, "info", "👈 Wähle zuerst links einen Begriff."); return; }
    const left = rt.selected;
    let ok = left.dataset.pair === el.dataset.pair;
    if (!ok) {
      // Gleicher Begriff links (z. B. zweimal „Honig“): Das passende Paar zählt, die beiden linken Knöpfe tauschen ihre Paarnummer.
      const paare = cfgOf(aufgabenByNr[nr]).paare, L = parseInt(left.dataset.pair, 10), R = parseInt(el.dataset.pair, 10);
      const anderer = $$(`[data-action="match-left"][data-pair="${R}"]`, body(nr))[0];
      if (anderer && !anderer.classList.contains("matched-ok") && paare[L] && paare[R] && paare[L][0] === paare[R][0]) {
        anderer.dataset.pair = String(L); left.dataset.pair = String(R); ok = true;
      }
    }
    sendAntwort(nr, "zuordnung", `${ok ? "✅" : "❌"} ${left.textContent.trim()} → ${el.textContent.trim()}`, ok, "Zuordnung");
    if (ok) {
      rt.matched.push(parseInt(el.dataset.pair, 10)); rt.selected = null;
      markPairMatched(nr, el.dataset.pair);
      if (rt.matched.length >= rt.total) { showFb(nr, "ok", "✅ Alle Zuordnungen richtig!"); markComplete(nr); }
      else showFb(nr, "ok", `✅ Passt! ${rt.matched.length} von ${rt.total} zugeordnet.`);
    } else {
      left.classList.remove("selected"); el.classList.add("matched-err"); setTimeout(() => el.classList.remove("matched-err"), 700);
      rt.selected = null;
      showFb(nr, "err", "❌ Das passt nicht zusammen. Versuch es noch einmal! " + hilfe(nr, cfgOf(aufgabenByNr[nr])));
    }
    dirty();
  };
  BIE.actions["reset-match"] = el => { renderBody(aufgabenByNr[el.dataset.nr]); dirty(); };
  function zuordnungRestore(nr, data) {
    const rt = state.runtime[nr]; if (!rt || !data || !Array.isArray(data.paare)) return;
    rt.matched = data.paare.slice();
    data.paare.forEach(p => markPairMatched(nr, p));
    if (rt.matched.length >= rt.total) showFb(nr, "ok", "✅ Alle Zuordnungen richtig!");
    else if (rt.matched.length) showFb(nr, "ok", `✅ ${rt.matched.length} von ${rt.total} zugeordnet.`);
  }

  // ─── Sortierung ────────────────────────────────────────────────────────
  renderers.sortierung = t => {
    const cfg = cfgOf(t);
    let order = shuffle(cfg.items.map((_, i) => i));
    if (order.every((v, i) => v === i) && order.length > 1) order = order.slice(1).concat(order[0]);
    state.runtime[t.nr] = { order, selected: null, items: cfg.items };
    return `<p class="hint">${esc(cfg.hinweis || "Bringe die Ereignisse in die richtige Reihenfolge.")} Tippe zwei Einträge nacheinander an, um sie zu tauschen.</p>
      <div class="sort-list" id="sort-${t.nr}" role="list">${renderSortItems(t.nr)}</div>
      <div class="btn-row"><button class="btn btn-primary" type="button" data-action="check-sort" data-nr="${t.nr}">✅ Reihenfolge prüfen</button><button class="btn btn-outline" type="button" data-action="reset-sort" data-nr="${t.nr}">🔄 Neu mischen</button></div>`;
  };
  function renderSortItems(nr) {
    const rt = state.runtime[nr];
    return rt.order.map((idx, pos) => `<button type="button" role="listitem" class="sort-item${rt.selected === pos ? " selected-sort" : ""}${rt.result ? (rt.result[pos] ? " correct" : " incorrect") : ""}" data-action="sort-item" data-nr="${nr}" data-pos="${pos}"><span class="handle">${pos + 1}.</span><span>${esc(rt.items[idx])}</span><span class="swap-hint" aria-hidden="true">⇅</span></button>`).join("");
  }
  BIE.actions["sort-item"] = el => {
    const nr = el.dataset.nr; const rt = state.runtime[nr]; const pos = parseInt(el.dataset.pos, 10);
    rt.result = null;
    if (rt.selected === null || rt.selected === undefined) rt.selected = pos;
    else if (rt.selected === pos) rt.selected = null;
    else { [rt.order[rt.selected], rt.order[pos]] = [rt.order[pos], rt.order[rt.selected]]; rt.selected = null; }
    document.getElementById("sort-" + nr).innerHTML = renderSortItems(nr);
    dirty();
  };
  function checkSort(nr, silent) {
    const rt = state.runtime[nr];
    rt.result = rt.order.map((idx, pos) => idx === pos);
    rt.selected = null;
    document.getElementById("sort-" + nr).innerHTML = renderSortItems(nr);
    const ok = rt.result.every(Boolean);
    const richtig = rt.result.filter(Boolean).length;
    if (!silent) sendAntwort(nr, "sortierung", ok ? "richtige Reihenfolge" : `${richtig}/${rt.order.length} Positionen richtig: ` + rt.order.map(i => rt.items[i].slice(0, 25)).join(" → "), ok, "Reihenfolge");
    if (ok) { showFb(nr, "ok", "✅ Richtige Reihenfolge!"); markComplete(nr); }
    else showFb(nr, "err", `❌ ${richtig} von ${rt.order.length} Positionen stimmen (grün). Weiter tauschen! ${hilfe(nr, cfgOf(aufgabenByNr[nr]))}`);
    dirty();
  }
  BIE.actions["check-sort"] = el => checkSort(el.dataset.nr);
  BIE.actions["reset-sort"] = el => { renderBody(aufgabenByNr[el.dataset.nr]); dirty(); };
  function sortRestore(nr, data) {
    const rt = state.runtime[nr]; if (!rt || !data || !Array.isArray(data.reihenfolge)) return;
    if (data.reihenfolge.length === rt.items.length && data.reihenfolge.every(i => Number.isInteger(i) && i >= 0 && i < rt.items.length)) rt.order = data.reihenfolge.slice();
    document.getElementById("sort-" + nr).innerHTML = renderSortItems(nr);
    if (data.geprueft) checkSort(nr, true);
  }

  // ─── Diagramm (Chart.js) ───────────────────────────────────────────────
  // Optional `auswertung` (Text) macht das Diagramm zur Forschungsaufgabe: Die Kinder lesen Werte ab und vergleichen (FORSCHEN.md).
  renderers.diagramm = t => {
    const cfg = cfgOf(t);
    const auswertung = typeof t.auswertung === "string" && t.auswertung ? `<div class="film-beobachtung"><p class="eyebrow">🔬 Auswerten</p><p>${esc(t.auswertung)}</p></div>` : "";
    return `${auswertung}<div class="chart-wrap"><canvas id="chart-${t.nr}" aria-label="${esc(t.chart.yTitel)}" role="img"></canvas></div>
      <p class="chart-source">${esc(t.chart.quelle)}${t.chart.legendeExtra ? " · " + esc(t.chart.legendeExtra) : ""}</p>
      <div class="feedback-box feedback-info show chart-info" id="chartinfo-${t.nr}" role="status">👆 Tippe auf das Diagramm, um Werte zu sehen.</div>
      ${renderMC(t.nr, cfg)}`;
  };
  // Ein Chart, der in einem 0 px breiten Container entsteht, bleibt dauerhaft leer –
  // resize() heilt ihn nicht mehr. Das passiert bei zugeklappten Stationen, beim
  // Reiterwechsel und beim Drehen des iPads. Deshalb wird der Aufbau verschoben,
  // bis der Rahmen wirklich Breite hat, und über einen ResizeObserver nachgeholt.
  const chartBeobachter = ("ResizeObserver" in window)
    ? new ResizeObserver(eintraege => eintraege.forEach(e => {
        const nr = e.target.dataset.chartNr;
        if (!nr || e.contentRect.width < 1) return;
        const t = aufgabenByNr[nr];
        if (!t) return;
        if (!state.charts[nr]) ensureChart(t);
        else { try { state.charts[nr].resize(); } catch (err) { /* egal */ } }
      }))
    : null;

  function ensureChart(t) {
    const canvas = document.getElementById("chart-" + t.nr);
    if (!canvas || state.charts[t.nr] || typeof Chart === "undefined") return;
    const rahmen = canvas.parentElement;
    if (rahmen && chartBeobachter && !rahmen.dataset.chartNr) {
      rahmen.dataset.chartNr = String(t.nr);
      chartBeobachter.observe(rahmen);
    }
    // Noch keine Breite: Der Beobachter ruft uns wieder auf, sobald die Karte offen ist.
    if (rahmen && rahmen.getBoundingClientRect().width < 1) return;
    const ch = t.chart;
    const datasets = ch.datasets.map(d => ({
      label: d.label, data: d.data,
      backgroundColor: d.farben || (ch.typ === "line" ? "rgba(0,106,179,.15)" : d.farbe),
      borderColor: d.farbe || "#006AB3", borderWidth: ch.typ === "line" ? 3 : 0, borderRadius: 4,
      fill: ch.typ === "line", tension: 0.3, pointRadius: ch.typ === "line" ? 6 : 0, pointHoverRadius: 8,
    }));
    const valueAxis = { beginAtZero: true, title: { display: true, text: ch.yTitel } };
    state.charts[t.nr] = new Chart(canvas, {
      type: ch.typ === "line" ? "line" : "bar",
      data: { labels: ch.labels, datasets },
      options: {
        responsive: true, maintainAspectRatio: false, indexAxis: ch.horizontal ? "y" : "x",
        plugins: { legend: { display: ch.datasets.length > 1, position: "top" }, tooltip: { enabled: true } },
        scales: ch.horizontal ? { x: valueAxis, y: { ticks: { autoSkip: false, font: { size: 11 } } } } : { y: valueAxis },
        onClick: (evt, elements) => {
          if (!elements.length) return;
          const el = elements[0]; const ds = ch.datasets[el.datasetIndex];
          document.getElementById("chartinfo-" + t.nr).innerHTML = `<strong>${esc(ch.labels[el.index])}</strong> · ${esc(ds.label)}: <strong>${ds.data[el.index]} ${esc(ch.einheit)}</strong>`;
        },
      },
    });
  }

  // ─── Freitext, Transfer ────────────────────────────────────────────────
  function renderTextTask(nr, cfg, extra) {
    return `
      <p class="task-question">${esc(cfg.aufgabe)}</p>
      ${cfg.starter ? `<div class="starter-row">${cfg.starter.map(s => `<button type="button" class="word-chip starter-chip" data-action="starter" data-nr="${nr}" data-text="${esc(s)}">${esc(s)}</button>`).join("")}</div>` : ""}
      ${cfg.begriffe ? `<p class="hint">Nutze die Begriffe: ${cfg.begriffe.map(b => `<em>${esc(b)}</em>`).join(", ")}</p>` : ""}
      <label class="sr-only" for="ft-${nr}">Deine Antwort</label>
      <textarea class="freitext" id="ft-${nr}" data-min="${cfg.min || 60}" rows="${cfg.min > 120 ? 8 : 5}" placeholder="Deine Antwort in ganzen Sätzen …" data-action-input="count" data-nr="${nr}"></textarea>
      <div class="text-meta"><span id="count-${nr}">0 Zeichen · mindestens ${cfg.min || 60}</span></div>
      ${extra || ""}
      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="save-freitext" data-nr="${nr}">💾 Antwort abgeben</button>
        <button class="btn btn-ai" type="button" data-action="check-freitext" data-nr="${nr}">🤖 Mit KI prüfen lassen</button>
      </div>
      <p class="hint ki-hint">„Antwort abgeben“ schickt deinen Text ins Protokoll der Lehrkraft. Das KI-Feedback muss die Lehrkraft freigeben; die KI gibt Hinweise, aber keine Lösungen.</p>`;
  }
  // Niveau A darf statt freiem Schreiben Textbausteine ordnen (Gemeinsames Lernen).
  // Das gilt für Transfer- UND Freitextaufgaben: cfg.modus === "bausteine" entscheidet.
  const textTask = t => { const cfg = cfgOf(t); return cfg.modus === "bausteine" ? renderBausteine(t.nr, cfg) : renderTextTask(t.nr, cfg); };
  renderers.freitext = textTask;
  renderers.transfer = textTask;

  // ─── Textbausteine (Niveau A der Transferaufgabe): antippen, ordnen, Urteil wählen ───
  function renderBausteine(nr, cfg) {
    let pool = shuffle(cfg.bausteine.map((_, i) => i));
    if (pool.every((v, i) => v === i)) pool = pool.slice(1).concat(pool[0]);
    state.runtime[nr] = { modus: "bausteine", pool, text: [], result: null, urteil: null, bausteine: cfg.bausteine };
    return `
      <p class="task-question">${esc(cfg.aufgabe)}</p>
      <p class="hint">👆 Tippe einen Baustein an – er wandert in deinen Text. Tippe ihn dort noch einmal an, wenn er zurück soll.</p>
      <div class="baustein-bereich">
        <div><p class="field-label">Bausteine</p><div class="sort-list baustein-pool" id="pool-${nr}" role="list"></div></div>
        <div><p class="field-label">Dein Text (in der richtigen Reihenfolge)</p><div class="sort-list baustein-text" id="text-${nr}" role="list"></div>
          <p class="baustein-schluss">${esc(cfg.schluss)}</p></div>
      </div>
      <div class="btn-row"><button class="btn btn-primary" type="button" data-action="check-bausteine" data-nr="${nr}">✅ Reihenfolge prüfen</button><button class="btn btn-outline" type="button" data-action="reset-bausteine" data-nr="${nr}">🔄 Neu anfangen</button></div>
      <div class="urteil" id="urteil-${nr}" hidden>
        <p class="task-question">${esc(cfg.urteil.frage)}</p>
        <div class="mc-options" role="group">${cfg.urteil.optionen.map((o, i) => `<button class="mc-btn" type="button" data-action="urteil" data-nr="${nr}" data-idx="${i}">${esc(o)}</button>`).join("")}</div>
      </div>`;
  }
  function bausteineZeichnen(nr) {
    const rt = state.runtime[nr]; if (!rt || rt.modus !== "bausteine") return;
    const pool = document.getElementById("pool-" + nr), text = document.getElementById("text-" + nr);
    if (!pool || !text) return;
    pool.innerHTML = rt.pool.map(idx => `<button type="button" role="listitem" class="sort-item baustein" data-action="baustein-rein" data-nr="${nr}" data-idx="${idx}"><span class="handle">+</span><span>${esc(rt.bausteine[idx])}</span></button>`).join("")
      || `<p class="muted baustein-leer">Alle Bausteine sind in deinem Text.</p>`;
    text.innerHTML = rt.text.map((idx, pos) => `<button type="button" role="listitem" class="sort-item${rt.result ? (rt.result[pos] ? " correct" : " incorrect") : ""}" data-action="baustein-raus" data-nr="${nr}" data-pos="${pos}"><span class="handle">${pos + 1}.</span><span>${esc(rt.bausteine[idx])}</span><span class="swap-hint" aria-hidden="true">✕</span></button>`).join("")
      || `<p class="muted baustein-leer">Noch leer – tippe links einen Baustein an.</p>`;
    const urteil = document.getElementById("urteil-" + nr);
    if (urteil) {
      urteil.hidden = !(rt.result && rt.result.every(Boolean));
      $$(".mc-btn", urteil).forEach(b => b.classList.toggle("correct", rt.urteil !== null && parseInt(b.dataset.idx, 10) === rt.urteil));
    }
  }
  BIE.actions["baustein-rein"] = el => {
    const nr = el.dataset.nr, rt = state.runtime[nr]; const idx = parseInt(el.dataset.idx, 10);
    rt.pool = rt.pool.filter(i => i !== idx); rt.text.push(idx); rt.result = null;
    bausteineZeichnen(nr); dirty();
  };
  BIE.actions["baustein-raus"] = el => {
    const nr = el.dataset.nr, rt = state.runtime[nr]; const pos = parseInt(el.dataset.pos, 10);
    const [idx] = rt.text.splice(pos, 1); rt.pool.push(idx); rt.result = null;
    bausteineZeichnen(nr); dirty();
  };
  function checkBausteine(nr, silent) {
    const rt = state.runtime[nr]; if (!rt) return;
    const n = rt.bausteine.length;
    if (rt.text.length < n) { showFb(nr, "err", `⚠️ Es fehlen noch ${n - rt.text.length} Bausteine. Tippe sie links an.`); return; }
    rt.result = rt.text.map((idx, pos) => idx === pos);
    const ok = rt.result.every(Boolean); const richtig = rt.result.filter(Boolean).length;
    bausteineZeichnen(nr);
    if (!silent) sendAntwort(nr, "sortierung", ok ? "Bausteine in richtiger Reihenfolge" : `${richtig}/${n} Bausteine richtig`, ok, "Textbausteine ordnen");
    if (ok) showFb(nr, "ok", rt.urteil === null ? "✅ Richtige Reihenfolge! Jetzt noch dein Urteil: Tippe unten eine Antwort an." : "✅ Richtige Reihenfolge und Urteil gewählt – fertig!");
    else showFb(nr, "err", `❌ ${richtig} von ${n} Bausteinen stehen richtig (grün). Tippe falsche Bausteine an, sie gehen zurück – dann noch einmal einsetzen.`);
    dirty();
  }
  BIE.actions["check-bausteine"] = el => checkBausteine(el.dataset.nr);
  BIE.actions["reset-bausteine"] = el => { renderBody(aufgabenByNr[el.dataset.nr]); bausteineZeichnen(el.dataset.nr); dirty(); };
  BIE.actions.urteil = el => {
    const nr = el.dataset.nr, rt = state.runtime[nr]; if (!rt || !rt.result || !rt.result.every(Boolean)) return;
    rt.urteil = parseInt(el.dataset.idx, 10);
    bausteineZeichnen(nr);
    const t = aufgabenByNr[nr]; const cfg = cfgOf(t);
    const text = rt.text.map(i => rt.bausteine[i]).join(" ") + " " + cfg.schluss + " Urteil: " + cfg.urteil.optionen[rt.urteil];
    sendAntwort(nr, "freitext-kreativ", text.slice(0, 400), null, cfg.aufgabe);
    showFb(nr, "ok", "✅ Fertig! Dein Text steht in der richtigen Reihenfolge und du hast ein Urteil gewählt. Deine Lehrkraft sieht ihn im Protokoll.");
    markComplete(nr); dirty();
  };
  function bausteineRestore(nr, data) {
    const rt = state.runtime[nr]; if (!rt || rt.modus !== "bausteine" || !data || !Array.isArray(data.text)) return;
    const n = rt.bausteine.length;
    const text = data.text.filter(i => Number.isInteger(i) && i >= 0 && i < n).filter((v, i, a) => a.indexOf(v) === i);
    rt.text = text; rt.pool = rt.bausteine.map((_, i) => i).filter(i => !text.includes(i));
    rt.urteil = Number.isInteger(data.urteil) ? data.urteil : null;
    if (data.geprueft) checkBausteine(nr, true); else bausteineZeichnen(nr);
  }
  function updateCount(nr) {
    const ta = document.getElementById("ft-" + nr); const c = document.getElementById("count-" + nr);
    if (!ta || !c) return;
    const min = parseInt(ta.dataset.min, 10) || 60;
    c.textContent = `${ta.value.length} Zeichen · mindestens ${min}`;
    c.classList.toggle("ok", ta.value.length >= min);
  }
  BIE.actions.starter = btn => {
    const ta = document.getElementById("ft-" + btn.dataset.nr); if (!ta) return;
    ta.value = ta.value ? ta.value.replace(/\s+$/, "") + " " + btn.dataset.text : btn.dataset.text;
    ta.focus(); updateCount(btn.dataset.nr); dirty();
  };
  BIE.actions["save-freitext"] = el => {
    const nr = el.dataset.nr; const t = aufgabenByNr[nr]; const cfg = cfgOf(t);
    const ta = document.getElementById("ft-" + nr); const text = (ta ? ta.value : "").trim();
    const min = cfg.min || 60;
    if (text.length < min) { showFb(nr, "err", `⚠️ Bitte schreibe noch etwas mehr (mindestens ${min} Zeichen).`); return; }
    sendAntwort(nr, nr === "T" ? "freitext-kreativ" : "freitext", text.slice(0, 400), null, cfg.aufgabe);
    showFb(nr, "ok", "✅ Antwort abgegeben – deine Lehrkraft sieht sie im Protokoll. Du kannst weiter daran arbeiten.");
    markComplete(nr);
  };
  BIE.actions["check-freitext"] = el => {
    const nr = el.dataset.nr; const t = aufgabenByNr[nr]; const cfg = cfgOf(t);
    const ta = document.getElementById("ft-" + nr); const text = (ta ? ta.value : "").trim();
    const min = cfg.min || 60;
    if (text.length < min) { showFb(nr, "err", `⚠️ Bitte schreibe noch etwas mehr (mindestens ${min} Zeichen).`); return; }
    const question = `${cfg.aufgabe} (Niveau ${niveauOf(nr)}${nr === "T" ? ", Transfer" : ""})`;
    BIE.ki.korrektur(nr, question, text, t.kontext || "", data => {
      sendAntwort(nr, nr === "T" ? "freitext-kreativ" : "freitext", text.slice(0, 220) + " → KI: " + (data.feedback || "").slice(0, 150), data.correct, cfg.aufgabe);
      const hint = data.hint ? `<br><span class="ki-hint-text">💡 ${esc(data.hint)}</span>` : "";
      if (data.correct === true) { showFb(nr, "ok", "✅ " + BIE.ki.md(data.feedback) + hint); markComplete(nr); }
      else if (data.correct === false) showFb(nr, "err", "💡 " + BIE.ki.md(data.feedback) + hint + " <br><small>Überarbeite deinen Text und prüfe erneut.</small>");
      else { showFb(nr, "info", "📝 " + BIE.ki.md(data.feedback) + hint); markComplete(nr); }
    });
  };

  // ─── Recherche-Notizen ─────────────────────────────────────────────────
  // Notizen: je Aufgabe (oder je Niveau) konfigurierbar – `platzhalter` (Text im Stichpunktfeld), `quelleNoetig: false` (das Feld „Quelle“ ist dann freiwillig),
  // `min` (Zahl der Stichpunkte, Standard 3). Siehe docs/INHALTE_FORMAT.md.
  const notizCfg = t => {
    const c = cfgOf(t) || t, wert = (k, std) => (c[k] !== undefined ? c[k] : t[k] !== undefined ? t[k] : std);
    return { platzhalter: String(wert("platzhalter", "• Die Biene hat …\n• …")), quelleNoetig: wert("quelleNoetig", true) !== false, min: Number.isInteger(wert("min", 3)) && wert("min", 3) > 0 ? wert("min", 3) : 3 };
  };
  const ANZAHL = ["null", "ein", "zwei", "drei", "vier", "fünf", "sechs"];
  renderers.notizen = t => {
    const nc = notizCfg(t);
    return `
      <p class="task-question">${esc(t.hinweis)}</p>
      <label class="field-label" for="nt-${t.abschnitt}">Stichpunkte (ein Stichpunkt pro Zeile)</label>
      <textarea class="freitext notiz" id="nt-${t.abschnitt}" rows="7" placeholder="${esc(nc.platzhalter).replace(/\n/g, "&#10;")}" data-action-input="notiz" data-abschnitt="${t.abschnitt}" data-nr="${t.nr}"></textarea>
      <div class="pad-host" id="pad-host-${t.abschnitt}" data-abschnitt="${t.abschnitt}" data-nr="${t.nr}"></div>
      <label class="field-label" for="nq-${t.abschnitt}">Quelle(n) für diesen Abschnitt${nc.quelleNoetig ? "" : " (freiwillig)"} (Buch mit Seite, Website mit Adresse …)</label>
      <textarea class="freitext notiz notiz-quelle" id="nq-${t.abschnitt}" rows="2" placeholder="z. B. Schulbuch S. 84–89; nabu.de: Honigbiene" data-action-input="notiz" data-abschnitt="${t.abschnitt}" data-nr="${t.nr}"></textarea>
      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="finish-notizen" data-nr="${t.nr}" data-abschnitt="${t.abschnitt}">✅ Stichpunkte abgeben</button>
        <button class="btn btn-ai" type="button" data-action="check-notizen" data-nr="${t.nr}" data-abschnitt="${t.abschnitt}">🤖 Von der KI prüfen lassen</button>
      </div>
      <p class="hint">Abgabe: mindestens ${ANZAHL[nc.min] || nc.min} Stichpunkte${nc.quelleNoetig ? " und eine Quelle" : ""}. Deine Stichpunkte werden automatisch gesichert, die Lehrkraft sieht sie live.</p>`;
  };
  function notizLines(text) { return String(text || "").split("\n").map(l => l.replace(/^[\s•\-–*·]+/, "").trim()).filter(l => l.length >= 4); }
  BIE.actions["finish-notizen"] = el => {
    const nr = el.dataset.nr, abschnitt = el.dataset.abschnitt;
    const s = document.getElementById("nt-" + abschnitt), q = document.getElementById("nq-" + abschnitt);
    const nc = notizCfg(aufgabenByNr[nr]), lines = notizLines(s.value), quellen = notizLines(q.value);
    if (lines.length < nc.min) { showFb(nr, "err", `⚠️ Du hast erst ${lines.length} Stichpunkt(e). Notiere mindestens ${ANZAHL[nc.min] || nc.min}.`); return; }
    if (nc.quelleNoetig && quellen.length < 1) { showFb(nr, "err", "⚠️ Trage mindestens eine Quelle ein – so weiß man, woher du es hast."); return; }
    sendAntwort(nr, "notizen", `${lines.length} Stichpunkte${quellen.length ? `, ${quellen.length} Quelle(n)` : ""}: ` + lines.join(" | ").slice(0, 250), null, "Stichpunkte " + abschnitt);
    showFb(nr, "ok", `✅ ${lines.length} Stichpunkte${quellen.length ? ` mit ${quellen.length} Quelle(n)` : ""} abgegeben. Du kannst sie weiter bearbeiten.`);
    markComplete(nr);
    if (BIE.autosave) BIE.autosave.flush({ force: true });
  };
  BIE.actions["check-notizen"] = el => {
    const nr = el.dataset.nr, abschnitt = el.dataset.abschnitt; const t = aufgabenByNr[nr];
    const s = document.getElementById("nt-" + abschnitt), q = document.getElementById("nq-" + abschnitt);
    const lines = notizLines(s.value);
    if (lines.length < 2) { showFb(nr, "err", "⚠️ Schreibe zuerst mindestens zwei Stichpunkte."); return; }
    const answer = "Stichpunkte:\n" + lines.map(l => "- " + l).join("\n") + "\nQuellen: " + (q.value.trim() || "keine angegeben");
    BIE.ki.korrektur(nr, t.kiFrage, answer, "Arbeitsblatt zur Honigbiene, Klasse 6 NW. Bewerte Richtigkeit, Vollständigkeit und Quellenangabe der Stichpunkte.", data => {
      sendAntwort(nr, "notizen", lines.join(" | ").slice(0, 200) + " → KI: " + (data.feedback || "").slice(0, 150), data.correct, "Stichpunkte " + abschnitt);
      const hint = data.hint ? `<br><span class="ki-hint-text">💡 ${esc(data.hint)}</span>` : "";
      showFb(nr, data.correct === false ? "err" : "info", (data.correct === false ? "💡 " : "📝 ") + BIE.ki.md(data.feedback) + hint);
    });
  };

  // ─── Quellenverzeichnis ────────────────────────────────────────────────
  const QUELLEN_ARTEN = ["Schulbuch", "Website", "Buch / Lexikon", "Dokumentation / Video", "Podcast", "Sonstiges"];
  const QUELLEN_WERT = ["sehr verlässlich", "eher verlässlich", "unsicher"];
  // Optional `quellenAB: { titel, eintraege: [Text, …] }` = Quellen dieses Arbeitsblatts als aufklappbarer Hinweis (nur Nennung, keine Zitate)
  const quellenAbHtml = t => (t.quellenAB && Array.isArray(t.quellenAB.eintraege) && t.quellenAB.eintraege.length
    ? `<details class="material-details quellen-ab"><summary>📚 ${esc(t.quellenAB.titel || "Quellen dieses Arbeitsblatts")}</summary><ul class="howto">${t.quellenAB.eintraege.map(e => `<li>${esc(e)}</li>`).join("")}</ul></details>` : "");
  renderers.quellen = t => `<p class="task-question">${esc(t.hinweis)}</p>
      ${quellenAbHtml(t)}
      <div class="quellen-list" id="quellen-${t.nr}"></div>
      <div class="btn-row">
        <button class="btn btn-outline" type="button" data-action="add-quelle" data-nr="${t.nr}">＋ Quelle hinzufügen</button>
        <button class="btn btn-primary" type="button" data-action="save-quellen" data-nr="${t.nr}">✅ Quellenverzeichnis abgeben</button>
      </div>`;
  function quelleRow(nr, q, i) {
    q = q || {};
    return `<div class="quelle-row" data-row="${i}">
      <div class="quelle-grid">
        <label><span>Titel / Autor:in</span><input data-field="titel" value="${esc(q.titel || "")}" placeholder="z. B. Schulbuch, S. 84"></label>
        <label><span>Adresse / Verlag / Jahr</span><input data-field="ort" value="${esc(q.ort || "")}" placeholder="z. B. imkerbund.de oder Klett 2020"></label>
        <label><span>Art</span><select data-field="art">${QUELLEN_ARTEN.map(a => `<option${q.art === a ? " selected" : ""}>${a}</option>`).join("")}</select></label>
        <label><span>Verlässlichkeit</span><select data-field="wert">${QUELLEN_WERT.map(a => `<option${q.wert === a ? " selected" : ""}>${a}</option>`).join("")}</select></label>
        <label class="span-2"><span>Warum ist die Quelle (nicht) verlässlich?</span><input data-field="grund" value="${esc(q.grund || "")}" placeholder="z. B. Verband von Imkern, Autor genannt, Quellen belegt"></label>
      </div>
      <button class="btn btn-quiet btn-sm" type="button" data-action="remove-quelle" data-nr="${nr}" data-row="${i}">✕ entfernen</button>
    </div>`;
  }
  // Die Aufgabe „Quellenverzeichnis“ wird über ihren Typ gefunden, nicht über eine feste Nummer.
  const quellenAufgabe = () => INHALTE.tabs.flatMap(tab => tab.aufgaben).find(a => a.typ === "quellen");
  function readQuellen() {
    const q = quellenAufgabe();
    const host = q && document.getElementById("quellen-" + q.nr); if (!host) return [];
    return $$(".quelle-row", host).map(row => { const o = {}; $$("[data-field]", row).forEach(f => { o[f.dataset.field] = f.value.trim(); }); return o; });
  }
  function fillQuellen(t, list) {
    const host = document.getElementById("quellen-" + t.nr); if (!host) return;
    if (!Array.isArray(list) || !list.length) list = [{}, {}];
    host.innerHTML = list.map((q, i) => quelleRow(t.nr, q, i)).join("");
  }
  BIE.actions["add-quelle"] = el => { const host = document.getElementById("quellen-" + el.dataset.nr); host.insertAdjacentHTML("beforeend", quelleRow(el.dataset.nr, {}, host.children.length)); dirty(); };
  BIE.actions["remove-quelle"] = el => { const host = document.getElementById("quellen-" + el.dataset.nr); const row = host.querySelector(`.quelle-row[data-row="${el.dataset.row}"]`); if (row && host.children.length > 1) row.remove(); dirty(); };
  BIE.actions["save-quellen"] = el => {
    const nr = el.dataset.nr; const t = aufgabenByNr[nr];
    const list = readQuellen();
    const valid = list.filter(q => q.titel.length >= 3 && q.ort.length >= 3 && q.grund.length >= 10);
    if (valid.length < (t.min || 2)) { showFb(nr, "err", `⚠️ Erst ${valid.length} vollständige Quelle(n). Für jede Quelle brauchst du Titel, Adresse/Verlag und eine Begründung (mindestens ${t.min || 2} Quellen).`); return; }
    sendAntwort(nr, "quellen", valid.map(q => `${q.titel} (${q.art}, ${q.wert})`).join(" | ").slice(0, 300), null, "Quellenverzeichnis");
    showFb(nr, "ok", `✅ ${valid.length} Quellen eingetragen und begründet – so gehört es sich für eine Recherche!`);
    markComplete(nr);
    if (BIE.autosave) BIE.autosave.flush({ force: true });
  };
  document.addEventListener("input", e => {
    const t = e.target;
    if (t.dataset.actionInput === "count") { updateCount(t.dataset.nr); dirty(); }
    if (t.dataset.actionInput === "notiz") dirty();
    if (t.dataset.actionInput === "bpname" && BIE.actions.bpname) BIE.actions.bpname(t);
    if (t.closest && t.closest(".quelle-row")) dirty();
  });
  document.addEventListener("change", e => { if (e.target.closest && e.target.closest(".quelle-row")) dirty(); });

  // ─── Backup-Registrierung ───────────────────────────────────────────────
  BIE.autosave.register("texte", () => {
    const texte = {};
    $$("textarea.freitext").forEach(ta => { if (ta.id && ta.value) texte[ta.id] = ta.value; });
    return texte;
  }, data => {
    Object.entries(data || {}).forEach(([id, v]) => { const ta = document.getElementById(id); if (ta && ta.tagName === "TEXTAREA") { ta.value = String(v); } });
    $$("textarea.freitext[data-action-input='count']").forEach(ta => updateCount(ta.dataset.nr));
  }, 20);
  BIE.autosave.register("quellen", () => readQuellen(), data => { const t = quellenAufgabe(); if (t) fillQuellen(t, Array.isArray(data) ? data : null); }, 21);
  BIE.autosave.register("aufgaben", () => {
    const out = {};
    INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(t => {
      const rt = state.runtime[t.nr] || {};
      if (istRF(t)) { if (rt.rf && rt.rf.wahl.some(w => w !== null)) out[t.nr] = { typ: "richtigfalsch", wahl: rt.rf.wahl.slice(), geprueft: !!rt.rf.geprueft }; }
      else if (t.typ === "mc" || t.typ === "diagramm") { if (rt.mc) out[t.nr] = Object.assign({ typ: t.typ }, rt.mc); }
      else if (t.typ === "luecke") { const v = lueckeCollect(t.nr); if (v && (v.werte.some(Boolean) || v.geprueft)) out[t.nr] = v; }
      else if (t.typ === "zuordnung") { if (rt.matched && rt.matched.length) out[t.nr] = { typ: "zuordnung", paare: rt.matched.slice() }; }
      else if (t.typ === "sortierung") { if (rt.order) out[t.nr] = { typ: "sortierung", reihenfolge: rt.order.slice(), geprueft: !!rt.result }; }
      else if (t.typ === "bildpunkte" && BIE.bildpunkte) { const v = BIE.bildpunkte.collect(t.nr); if (v) out[t.nr] = v; }
      else if (t.typ === "filmmoment" && BIE.film) { const v = BIE.film.collect(t.nr); if (v) out[t.nr] = v; }
      else if (istBausteine(t) && rt.modus === "bausteine" && (rt.text.length || rt.urteil !== null)) out[t.nr] = { typ: "transfer", text: rt.text.slice(), urteil: rt.urteil, geprueft: !!rt.result };
    }));
    return out;
  }, data => {
    // Struktur zuerst: Karten nach Niveau neu rendern, dann Zustände setzen
    INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(t => { if (isDifferenziert(t) && t.typ !== "zeichnen") renderBody(t); }));
    Object.entries(data || {}).forEach(([nr, d]) => {
      const t = aufgabenByNr[nr]; if (!t || !d) return;
      if (istRF(t)) rfRestore(nr, d);
      else if (t.typ === "mc" || t.typ === "diagramm") mcRestore(nr, d);
      else if (t.typ === "luecke") lueckeRestore(nr, d);
      else if (t.typ === "zuordnung") zuordnungRestore(nr, d);
      else if (t.typ === "sortierung") sortRestore(nr, d);
      else if (t.typ === "bildpunkte" && BIE.bildpunkte) BIE.bildpunkte.restore(nr, d);
      else if (t.typ === "filmmoment" && BIE.film) BIE.film.restore(nr, d);
      else if (istBausteine(t)) bausteineRestore(nr, d);
    });
  }, 10);

  BIE.beimOeffnen["*"] = key => { const tab = INHALTE.tabs.find(t => t.key === key); if (tab) tab.aufgaben.forEach(a => { if (a.typ === "diagramm") ensureChart(a); }); };

  return { buildPanels, renderBody, renderMC, ensureChart, mcAuswerten, notizLines, readQuellen, fillQuellen };
})();
