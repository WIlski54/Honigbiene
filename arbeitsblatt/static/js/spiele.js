/* Blitzfragen (nicht wiederholend, Fisher-Yates) und Begriffs-Domino (tap-basiert). */
BIE.spiele = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, shuffle, cfgOf, niveauOf, body, showFb, clearFb, markComplete, sendAntwort, dirty, aufgabenByNr } = BIE;
  // Blitz und Domino werden über ihren Typ gefunden, nicht über eine feste Aufgabennummer.
  const aufgabeVon = typ => INHALTE.tabs.flatMap(tab => tab.aufgaben).find(a => a.typ === typ);

  function render(t) {
    const cfg = cfgOf(t);
    if (t.typ === "blitz") return `<p class="task-question">${esc(t.hinweis)}</p><p class="hint">${esc(cfg.hinweis)}</p><div class="blitz-status" id="blitz-status-${t.nr}" role="status"></div><div id="blitz-${t.nr}" class="blitz-box"></div>`;
    return `<p class="task-question">${esc(t.hinweis)}</p><p class="hint">${esc(cfg.hinweis)}</p>
      <div class="domino-chain" id="domino-chain-${t.nr}" aria-label="Kette"></div>
      <div class="domino-hand-label">Deine Steine – tippe den passenden an:</div>
      <div class="domino-hand" id="domino-hand-${t.nr}" role="group" aria-label="Steine in der Hand"></div>
      <div class="btn-row"><button class="btn btn-outline btn-sm" type="button" data-action="domino-reset" data-nr="${t.nr}">🔄 Neu beginnen</button></div>`;
  }
  function mount(t) { if (t.typ === "blitz") blitzStart(t); else dominoStart(t); }

  // ─── Blitzfragen ──────────────────────────────────────────────────────
  function blitzStart(t, wieder) {
    const cfg = cfgOf(t);
    const rt = wieder || { niveau: niveauOf(t.nr), aktuelle_id: null, gesehen: [], richtig: 0, beantwortet: 0, offen: false, fertig: false };
    state.runtime[t.nr] = rt;
    if (rt.aktuelle_id && rt.offen && t.pool.some(q => q.id === rt.aktuelle_id)) blitzZeige(t, t.pool.find(q => q.id === rt.aktuelle_id));
    else blitzNaechste(t);
  }
  function blitzPool(t) { const cfg = cfgOf(t); return t.pool.filter(q => cfg.stufen.includes(q.stufe)); }
  function blitzStatus(t) {
    const cfg = cfgOf(t); const rt = state.runtime[t.nr];
    const el = document.getElementById("blitz-status-" + t.nr);
    if (el) el.innerHTML = `Richtig: <strong>${rt.richtig}</strong> / ${cfg.ziel} · beantwortet: ${rt.beantwortet} · noch im Vorrat: ${blitzPool(t).filter(q => !rt.gesehen.includes(q.id)).length}`;
  }
  // Gleichmäßig über die Stufen des Niveaus: erst eine Stufe zufällig (aus denen, die noch Fragen haben), dann eine Frage daraus.
  // Sonst kämen auf Niveau C kaum Fragen der schweren Stufe 3 vor (sie ist im Pool die kleinste).
  function naechsteFrage(rest, zufall) {
    const z = zufall || Math.random;
    const stufen = [...new Set(rest.map(q => q.stufe))];
    const stufe = stufen[Math.floor(z() * stufen.length)];
    const aus = rest.filter(q => q.stufe === stufe);
    return aus[Math.floor(z() * aus.length)];
  }
  function blitzNaechste(t) {
    const cfg = cfgOf(t); const rt = state.runtime[t.nr]; const box = document.getElementById("blitz-" + t.nr);
    blitzStatus(t);
    if (rt.richtig >= cfg.ziel) { rt.fertig = true; rt.offen = false; box.innerHTML = `<div class="feedback-box feedback-ok show">🏁 Ziel erreicht: ${rt.richtig} richtige Antworten! <button class="btn btn-quiet btn-sm" type="button" data-action="blitz-reset" data-nr="${t.nr}">Noch eine Runde</button></div>`; markComplete(t.nr); return; }
    const rest = blitzPool(t).filter(q => !rt.gesehen.includes(q.id));
    if (!rest.length) { rt.offen = false; box.innerHTML = `<div class="feedback-box feedback-info show">Der Vorrat ist leer (${rt.richtig} richtig). Wechsle das Niveau oder starte neu. <button class="btn btn-quiet btn-sm" type="button" data-action="blitz-reset" data-nr="${t.nr}">Neu starten</button></div>`; return; }
    const q = naechsteFrage(rest);
    rt.aktuelle_id = q.id; rt.offen = true;
    blitzZeige(t, q);
  }
  function blitzZeige(t, q) {
    const box = document.getElementById("blitz-" + t.nr);
    const opts = shuffle(q.optionen.map((o, i) => ({ o, i })));
    box.innerHTML = `<p class="task-question">⚡ ${esc(q.frage)}</p><div class="mc-options" role="group">${opts.map(x => `<button class="mc-btn" type="button" data-action="blitz-antwort" data-nr="${t.nr}" data-idx="${x.i}">${esc(x.o)}</button>`).join("")}</div>`;
    blitzStatus(t);
  }
  BIE.actions["blitz-antwort"] = el => {
    const nr = el.dataset.nr; const t = aufgabenByNr[nr]; const rt = state.runtime[nr];
    const q = t.pool.find(x => x.id === rt.aktuelle_id); if (!q || !rt.offen) return;
    const idx = parseInt(el.dataset.idx, 10); const ok = idx === q.ok;
    const group = el.closest(".mc-options");
    $$(".mc-btn", group).forEach(b => { b.disabled = true; if (parseInt(b.dataset.idx, 10) === q.ok) b.classList.add("correct"); });
    if (!ok) el.classList.add("incorrect");
    rt.gesehen.push(q.id); rt.beantwortet++; if (ok) rt.richtig++; rt.offen = false;
    sendAntwort(nr, "blitz", `${q.frage} → ${q.optionen[idx]}`, ok, q.frage);
    group.insertAdjacentHTML("afterend", `<div class="feedback-box show ${ok ? "feedback-ok" : "feedback-err"}">${ok ? "✅ Richtig!" : "❌ Leider nicht – die richtige Antwort ist markiert."} <button class="btn btn-primary btn-sm" type="button" data-action="blitz-weiter" data-nr="${nr}">Nächste Frage →</button></div>`);
    blitzStatus(t); dirty();
  };
  BIE.actions["blitz-weiter"] = el => { blitzNaechste(aufgabenByNr[el.dataset.nr]); dirty(); };
  BIE.actions["blitz-reset"] = el => { const t = aufgabenByNr[el.dataset.nr]; clearFb(t.nr); blitzStart(t); dirty(); };

  // ─── Domino ───────────────────────────────────────────────────────────
  function dominoSteine(t) {
    const cfg = cfgOf(t); const paare = t.paare.slice(0, cfg.steine); const n = paare.length;
    return paare.map((p, i) => ({ id: p.id, links: p.definition, rechts: paare[(i + 1) % n].begriff, idx: i }));
  }
  function dominoStart(t, wieder) {
    const steine = dominoSteine(t);
    const rt = wieder || { kette: [steine[0].id], hand: shuffle(steine.slice(1).map(s => s.id)), fehler: 0, fertig: false, niveau: niveauOf(t.nr) };
    rt.steine = steine;
    state.runtime[t.nr] = rt;
    dominoRender(t);
  }
  function dominoRender(t) {
    const rt = state.runtime[t.nr]; const byId = Object.fromEntries(rt.steine.map(s => [s.id, s]));
    const chain = document.getElementById("domino-chain-" + t.nr); const hand = document.getElementById("domino-hand-" + t.nr);
    chain.innerHTML = rt.kette.map((id, i) => { const s = byId[id]; return `<div class="domino-tile placed${i === rt.kette.length - 1 && !rt.fertig ? " open" : ""}"><span class="d-left">${esc(s.links)}</span><span class="d-right">${esc(s.rechts)}</span></div>`; }).join(`<span class="domino-arrow" aria-hidden="true">→</span>`) + (rt.fertig ? `<span class="domino-arrow" aria-hidden="true">↩</span>` : "");
    hand.innerHTML = rt.hand.map(id => { const s = byId[id]; return `<button type="button" class="domino-tile hand" data-action="domino-tile" data-nr="${t.nr}" data-id="${id}"><span class="d-left">${esc(s.links)}</span><span class="d-right">${esc(s.rechts)}</span></button>`; }).join("");
    if (rt.fertig) { showFb(t.nr, "ok", `✅ Kette geschlossen – alle ${rt.kette.length} Steine passen! (${rt.fehler} Fehlversuche)`); if (!state.completed.has(String(t.nr))) markComplete(t.nr); }
  }
  BIE.actions["domino-tile"] = el => {
    const nr = el.dataset.nr; const t = aufgabenByNr[nr]; const rt = state.runtime[nr]; if (rt.fertig) return;
    const byId = Object.fromEntries(rt.steine.map(s => [s.id, s]));
    const offen = byId[rt.kette[rt.kette.length - 1]].rechts;
    const stein = byId[el.dataset.id];
    const passt = rt.steine.find(s => s.links === stein.links && t.paare.find(p => p.id === s.id).begriff === offen) === stein;
    if (passt) {
      rt.kette.push(stein.id); rt.hand = rt.hand.filter(id => id !== stein.id);
      sendAntwort(nr, "domino", `✅ ${offen} ↔ ${stein.links}`, true, "Domino");
      if (!rt.hand.length) rt.fertig = true; else showFb(nr, "ok", `✅ Passt! Offener Begriff: ${esc(stein.rechts)}`);
    } else {
      rt.fehler++; el.classList.add("matched-err"); setTimeout(() => el.classList.remove("matched-err"), 700);
      sendAntwort(nr, "domino", `❌ ${offen} ↔ ${stein.links}`, false, "Domino");
      showFb(nr, "err", `❌ Diese Erklärung passt nicht zu „${esc(offen)}“. Lies die Erklärungen genau.`);
    }
    dominoRender(t); dirty();
  };
  BIE.actions["domino-reset"] = el => { const t = aufgabenByNr[el.dataset.nr]; clearFb(t.nr); dominoStart(t); dirty(); };

  // ─── Backup ───────────────────────────────────────────────────────────
  BIE.autosave.register("blitz", () => {
      const t = aufgabeVon("blitz"), rt = t && state.runtime[t.nr];
      return rt ? { niveau: rt.niveau, aktuelle_id: rt.aktuelle_id, gesehen: rt.gesehen, richtig: rt.richtig, beantwortet: rt.beantwortet, offen: rt.offen, fertig: rt.fertig } : undefined;
    },
    d => {
      const t = aufgabeVon("blitz"); if (!t) return;
      if (d && Array.isArray(d.gesehen)) {
        const ids = new Set(t.pool.map(q => q.id));
        blitzStart(t, { niveau: d.niveau || niveauOf(t.nr), aktuelle_id: ids.has(d.aktuelle_id) ? d.aktuelle_id : null, gesehen: d.gesehen.filter(id => ids.has(id)), richtig: d.richtig || 0, beantwortet: d.beantwortet || 0, offen: !!d.offen, fertig: !!d.fertig });
      } else blitzStart(t);
    }, 45);
  BIE.autosave.register("domino", () => {
      const t = aufgabeVon("domino"), rt = t && state.runtime[t.nr];
      return rt ? { niveau: rt.niveau, kette: rt.kette, fehler: rt.fehler, fertig: rt.fertig } : undefined;
    },
    d => {
      const t = aufgabeVon("domino"); if (!t) return;
      const steine = dominoSteine(t); const ids = new Set(steine.map(s => s.id));
      if (d && Array.isArray(d.kette) && d.kette.length && d.kette.every(id => ids.has(id))) {
        const kette = d.kette;
        dominoStart(t, { kette, hand: shuffle(steine.map(s => s.id).filter(id => !kette.includes(id))), fehler: d.fehler || 0, fertig: !!d.fertig && kette.length === steine.length, niveau: d.niveau || niveauOf(t.nr) });
      } else dominoStart(t);
    }, 46);

  return { render, mount, logik: { naechsteFrage } };
})();
