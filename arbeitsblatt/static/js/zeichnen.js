/* Objektbasiertes Zeichnen (Fabric.js, lokal) und Handschrift-Pad für Stichpunkte.
   Regeln: Griffe nur im Auswahlmodus, nichts automatisch anwählen, Farbe gilt der nächsten Form,
   was an die KI geht wird sauber auf Weiß gerendert. Jede Änderung wird automatisch gesichert. */
BIE.zeichnen = (() => {
  "use strict";
  const { state, $, $$, esc, cfgOf, niveauOf, card, body, showFb, markComplete, sendAntwort, dirty, aufgabenByNr, postJSON, showToast } = BIE;
  const FARBEN = ["#1e293b", "#dc2626", "#006AB3", "#16a34a", "#d97706", "#AD007C", "#6b7280", "#ffffff"];
  const editors = {};      // nr -> Editor
  const pending = {};      // geraet -> canvas JSON (aus Autosave/Server, noch nicht gemountet)
  const previews = {};     // geraet -> dataURL
  let clipboard = null;
  let lastActive = null;

  function fabricDa() { return typeof fabric !== "undefined"; }

  // ─── Zeichenaufgabe ────────────────────────────────────────────────────
  function render(t) {
    const cfg = cfgOf(t);
    return `
      <p class="task-question">${esc(cfg.aufgabe)}</p>
      <p class="hint">${esc(cfg.hinweis || "")} Die Zeichnung wird automatisch gesichert.</p>
      ${checkliste(t, cfg)}
      <div class="zeichen-tools" role="toolbar" aria-label="Zeichenwerkzeuge">
        <div class="tool-group">
          ${[["select", "↖️", "Auswählen"], ["pencil", "✏️", "Stift"], ["line", "📏", "Linie"], ["rect", "▭", "Rechteck"], ["ellipse", "◯", "Ellipse"], ["text", "🔤", "Text"]].map(([tool, icon, label]) => `<button type="button" class="tool-btn${tool === "pencil" ? " active" : ""}" data-action="zt" data-nr="${t.nr}" data-tool="${tool}" aria-label="${label}" title="${label}"><span aria-hidden="true">${icon}</span><small>${label}</small></button>`).join("")}
        </div>
        <div class="tool-group">
          ${FARBEN.map(f => `<button type="button" class="color-btn${f === "#1e293b" ? " active" : ""}" data-action="zc" data-nr="${t.nr}" data-color="${f}" style="background:${f}" aria-label="Farbe ${f}"></button>`).join("")}
          <input type="color" class="color-pick" data-nr="${t.nr}" value="#1e293b" aria-label="Eigene Farbe">
          <select class="width-select" data-nr="${t.nr}" aria-label="Strichstärke"><option value="2">dünn</option><option value="4" selected>mittel</option><option value="8">dick</option></select>
        </div>
        <div class="tool-group">
          <button type="button" class="tool-btn" data-action="z-copy" data-nr="${t.nr}" aria-label="Kopieren"><span aria-hidden="true">⧉</span><small>Kopieren</small></button>
          <button type="button" class="tool-btn" data-action="z-paste" data-nr="${t.nr}" aria-label="Einfügen"><span aria-hidden="true">📋</span><small>Einfügen</small></button>
          <button type="button" class="tool-btn" data-action="z-delete" data-nr="${t.nr}" aria-label="Objekt löschen"><span aria-hidden="true">🗑️</span><small>Löschen</small></button>
          <button type="button" class="tool-btn" data-action="z-clear" data-nr="${t.nr}" aria-label="Alles leeren"><span aria-hidden="true">🧹</span><small>Leeren</small></button>
        </div>
      </div>
      <div class="zeichen-wrap" id="zw-${t.nr}"><canvas id="zc-${t.nr}" aria-label="Zeichenfläche"></canvas></div>
      <div class="text-meta"><span id="zstat-${t.nr}">0 Objekte</span><span id="zsave-${t.nr}" class="save-state">noch nicht gesichert</span></div>
      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="z-save" data-nr="${t.nr}">💾 Zeichnung abgeben</button>
        <button class="btn btn-ai" type="button" data-action="z-ki" data-nr="${t.nr}">🤖 Von der KI bewerten lassen</button>
      </div>
      <p class="hint ki-hint">Auf dem iPad: Finger oder Pencil. Auswahl, Verschieben, Größe und Drehen im Auswahlmodus. Die KI-Bewertung muss die Lehrkraft freigeben.</p>`;
  }

  // Niveau A: „Das gehört in deine Zeichnung“ – die erwarteten Elemente als Checkliste zum Abhaken (freiwillig, sie werden nicht bewertet)
  const haken = {};     // nr -> [Indizes der abgehakten Elemente]; mit der Zeichnung gesichert (Autosave „zeichenliste“)
  function checkliste(t, cfg) {
    const el = (cfg.elemente || []).filter(x => typeof x === "string" && x.trim());
    if (niveauOf(t.nr) !== "A" || !el.length) return "";
    const an = haken[t.nr] || [];
    return `<div class="zeichen-liste" role="group" aria-label="Das gehört in deine Zeichnung"><p class="eyebrow">Das gehört in deine Zeichnung</p>
      <div class="zeichen-liste-chips">${el.map((x, i) => `<button type="button" class="word-chip zl-punkt${an.includes(i) ? " zl-an" : ""}" aria-pressed="${an.includes(i)}" data-action="z-haken" data-nr="${t.nr}" data-i="${i}">${an.includes(i) ? "✔ " : ""}${esc(x)}</button>`).join("")}</div>
      <p class="hint">Tippe ein Element an, wenn du es gezeichnet hast. Das ist nur eine Gedächtnisstütze.</p></div>`;
  }
  BIE.actions["z-haken"] = el => {
    const nr = el.dataset.nr, i = parseInt(el.dataset.i, 10), a = haken[nr] || (haken[nr] = []);
    const k = a.indexOf(i); if (k >= 0) a.splice(k, 1); else a.push(i);
    const an = a.includes(i);
    el.classList.toggle("zl-an", an); el.setAttribute("aria-pressed", String(an));
    el.textContent = (an ? "✔ " : "") + (((cfgOf(aufgabenByNr[nr]) || {}).elemente || [])[i] || "");
    dirty();
  };
  BIE.autosave.register("zeichenliste", () => { const out = {}; Object.entries(haken).forEach(([nr, a]) => { if (a.length) out[nr] = a.slice(); }); return Object.keys(out).length ? out : undefined; },
    d => { Object.keys(haken).forEach(k => delete haken[k]); Object.entries(d || {}).forEach(([nr, a]) => { if (Array.isArray(a)) haken[nr] = a.filter(Number.isInteger); }); $$(".zeichen-liste").forEach(l => { const b = $(".zl-punkt", l); if (b && haken[b.dataset.nr]) $$(".zl-punkt", l).forEach(x => { const an = haken[x.dataset.nr].includes(parseInt(x.dataset.i, 10)); x.classList.toggle("zl-an", an); x.setAttribute("aria-pressed", String(an)); x.textContent = (an ? "✔ " : "") + x.textContent.replace(/^✔ /, ""); }); }); }, 47);

  function mount(t) {
    if (!fabricDa()) { const w = document.getElementById("zw-" + t.nr); if (w) w.innerHTML = "<p class='muted'>Zeichenmodul nicht geladen.</p>"; return; }
    const panel = card(t.nr).closest(".tab-panel");
    if (panel.hidden) { pendingMount.add(t.nr); return; }
    erzeugeEditor(t);
  }
  const pendingMount = new Set();
  BIE.beimOeffnen["*"] = (orig => key => { if (orig) orig(key); pendingMount.forEach(nr => { const t = aufgabenByNr[nr]; if (t && !card(nr).closest(".tab-panel").hidden) { pendingMount.delete(nr); erzeugeEditor(t); } }); Object.values(editors).forEach(ed => passeGroesseAn(ed)); })(BIE.beimOeffnen["*"]);

  function passeGroesseAn(ed) {
    const wrap = document.getElementById("zw-" + ed.nr); if (!wrap || !wrap.offsetWidth) return;
    const w = Math.max(300, wrap.clientWidth); const h = Math.round(w * 0.6);   // volle Breite des Rahmens – sonst endet die Fläche unsichtbar vor dem Rand
    if (Math.abs(ed.canvas.getWidth() - w) < 2) return;
    const zoom = w / 900;
    ed.canvas.setDimensions({ width: w, height: h });
    ed.canvas.setZoom(zoom);
  }

  // Rahmenbreite beobachten (Fenster, Drehen des iPads, Auf-/Zuklappen) und die Fläche nachziehen
  let resizeTimer = null;
  const beobachter = ("ResizeObserver" in window) ? new ResizeObserver(() => { clearTimeout(resizeTimer); resizeTimer = setTimeout(resizeAll, 80); }) : null;
  function beobachteGroesse(ed) { const wrap = document.getElementById("zw-" + ed.nr); if (beobachter && wrap) beobachter.observe(wrap); }
  window.addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(resizeAll, 150); });

  function erzeugeEditor(t) {
    if (editors[t.nr]) return editors[t.nr];
    const el = document.getElementById("zc-" + t.nr); if (!el) return null;
    const canvas = new fabric.Canvas(el, { isDrawingMode: true, selection: false, backgroundColor: "#ffffff", preserveObjectStacking: true, stopContextMenu: true, fireRightClick: false });
    canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
    const ed = { nr: t.nr, geraet: t.geraet, canvas, tool: "pencil", color: "#1e293b", width: 4, drawing: null, timer: null, laden: false };
    editors[t.nr] = ed;
    passeGroesseAn(ed);
    beobachteGroesse(ed);
    brushAktualisieren(ed);
    const geaendert = () => { if (ed.laden) return; statistik(ed); dirty(); clearTimeout(ed.timer); ed.timer = setTimeout(() => speichern(ed), 1500); };
    canvas.on("object:added", geaendert); canvas.on("object:modified", geaendert); canvas.on("object:removed", geaendert); canvas.on("path:created", geaendert);
    canvas.on("mouse:down", opt => { lastActive = t.nr; formStart(ed, opt); });
    canvas.on("mouse:move", opt => formBewegen(ed, opt));
    canvas.on("mouse:up", () => formEnde(ed));
    if (pending[t.geraet]) { ladeJSON(ed, pending[t.geraet]); }
    statistik(ed);
    return ed;
  }

  function brushAktualisieren(ed) { ed.canvas.freeDrawingBrush.color = ed.color; ed.canvas.freeDrawingBrush.width = ed.width; }
  function statistik(ed) { const s = document.getElementById("zstat-" + ed.nr); if (s) s.textContent = `${ed.canvas.getObjects().length} Objekte`; }
  function punkt(ed, opt) { const p = ed.canvas.getPointer(opt.e); return { x: p.x, y: p.y }; }

  function werkzeugSetzen(ed, tool) {
    ed.tool = tool;
    const sel = tool === "select";
    ed.canvas.isDrawingMode = tool === "pencil";
    ed.canvas.selection = sel;
    ed.canvas.skipTargetFind = !sel;                       // Griffe nur im Auswahlmodus
    ed.canvas.forEachObject(o => { o.selectable = sel; o.evented = sel; });
    if (!sel) ed.canvas.discardActiveObject();
    ed.canvas.defaultCursor = sel ? "default" : "crosshair";
    ed.canvas.requestRenderAll();
    $$(`.tool-btn[data-action="zt"][data-nr="${ed.nr}"]`).forEach(b => b.classList.toggle("active", b.dataset.tool === tool));
  }
  function formStart(ed, opt) {
    if (["line", "rect", "ellipse", "text"].indexOf(ed.tool) < 0) return;
    const p = punkt(ed, opt);
    if (ed.tool === "text") {
      const txt = new fabric.IText("Text", { left: p.x, top: p.y, fontSize: 22, fill: ed.color, fontFamily: "Lato, Arial, sans-serif", selectable: true, evented: true });
      ed.canvas.add(txt);
      werkzeugSetzen(ed, "select");
      ed.canvas.setActiveObject(txt); txt.enterEditing(); txt.selectAll();
      return;
    }
    const common = { stroke: ed.color, strokeWidth: ed.width, fill: "transparent", selectable: false, evented: false, strokeUniform: true };
    let obj;
    if (ed.tool === "line") obj = new fabric.Line([p.x, p.y, p.x, p.y], common);
    else if (ed.tool === "rect") obj = new fabric.Rect(Object.assign({ left: p.x, top: p.y, width: 1, height: 1 }, common));
    else obj = new fabric.Ellipse(Object.assign({ left: p.x, top: p.y, rx: 1, ry: 1 }, common));
    ed.drawing = { obj, x0: p.x, y0: p.y };
    ed.laden = true; ed.canvas.add(obj); ed.laden = false;
  }
  function formBewegen(ed, opt) {
    if (!ed.drawing) return;
    const p = punkt(ed, opt); const { obj, x0, y0 } = ed.drawing;
    if (ed.tool === "line") obj.set({ x2: p.x, y2: p.y });
    else if (ed.tool === "rect") obj.set({ left: Math.min(p.x, x0), top: Math.min(p.y, y0), width: Math.abs(p.x - x0), height: Math.abs(p.y - y0) });
    else obj.set({ left: Math.min(p.x, x0), top: Math.min(p.y, y0), rx: Math.abs(p.x - x0) / 2, ry: Math.abs(p.y - y0) / 2 });
    obj.setCoords(); ed.canvas.requestRenderAll();
  }
  function formEnde(ed) {
    if (!ed.drawing) return;
    const { obj, x0, y0 } = ed.drawing; ed.drawing = null;
    const zuKlein = ed.tool === "line" ? (Math.abs(obj.x2 - x0) < 3 && Math.abs(obj.y2 - y0) < 3) : (obj.width < 3 && obj.height < 3 && !(obj.rx > 1));
    if (zuKlein) { ed.laden = true; ed.canvas.remove(obj); ed.laden = false; return; }
    ed.canvas.fire("object:modified", { target: obj });   // Änderung zählt (Autosave), Objekt bleibt unangewählt
  }

  async function speichern(ed, explizit) {
    const json = ed.canvas.toJSON();
    const preview = ed.canvas.toDataURL({ format: "png", multiplier: Math.min(1, 480 / ed.canvas.getWidth()) });
    previews[ed.geraet] = preview;
    const st = document.getElementById("zsave-" + ed.nr); if (st) st.textContent = "wird gesichert …";
    const r = await postJSON("/api/zeichnung", { geraet: ed.geraet, canvas_json: json, preview });
    if (st) st.textContent = r.ok ? "gesichert · " + BIE.uhrzeit(r.updated_at) : "Sicherung fehlgeschlagen – wird erneut versucht";
    if (!r.ok && !explizit) { clearTimeout(ed.timer); ed.timer = setTimeout(() => speichern(ed), 8000); }
    return r;
  }
  function ladeJSON(ed, json) {
    ed.laden = true;
    try { ed.canvas.loadFromJSON(json, () => { ed.canvas.backgroundColor = "#ffffff"; werkzeugSetzen(ed, ed.tool); ed.canvas.renderAll(); ed.laden = false; statistik(ed); }); }
    catch (e) { ed.laden = false; }
  }
  function sauberesPNG(ed) {
    ed.canvas.discardActiveObject(); ed.canvas.renderAll();
    return ed.canvas.toDataURL({ format: "png", multiplier: Math.min(1.5, 900 / ed.canvas.getWidth()) });
  }

  // ─── Aktionen ────────────────────────────────────────────────────────
  BIE.actions.zt = el => { const ed = editors[el.dataset.nr]; if (ed) werkzeugSetzen(ed, el.dataset.tool); };
  BIE.actions.zc = el => {
    const ed = editors[el.dataset.nr]; if (!ed) return;
    ed.color = el.dataset.color; brushAktualisieren(ed);
    $$(`.color-btn[data-nr="${ed.nr}"]`).forEach(b => b.classList.toggle("active", b.dataset.color === ed.color));
    if (ed.tool === "select") { const o = ed.canvas.getActiveObject(); if (o) { if (o.type === "i-text") o.set("fill", ed.color); else o.set("stroke", ed.color); ed.canvas.requestRenderAll(); ed.canvas.fire("object:modified", { target: o }); } }
  };
  document.addEventListener("input", e => {
    const t = e.target;
    if (t.classList && t.classList.contains("color-pick")) { const ed = editors[t.dataset.nr]; if (ed) { ed.color = t.value; brushAktualisieren(ed); $$(`.color-btn[data-nr="${ed.nr}"]`).forEach(b => b.classList.remove("active")); } }
    if (t.classList && t.classList.contains("width-select")) { const ed = editors[t.dataset.nr]; if (ed) { ed.width = parseInt(t.value, 10); brushAktualisieren(ed); if (ed.tool === "select") { const o = ed.canvas.getActiveObject(); if (o && o.type !== "i-text") { o.set("strokeWidth", ed.width); ed.canvas.requestRenderAll(); ed.canvas.fire("object:modified", { target: o }); } } } }
  });
  function kopieren(ed) { const o = ed.canvas.getActiveObject(); if (!o) { showToast("Wähle zuerst ein Objekt (Auswahlwerkzeug).", "#d97706"); return; } o.clone(c => { clipboard = c; showToast("Kopiert"); }); }
  function einfuegen(ed) {
    if (!clipboard) { showToast("Zwischenablage ist leer.", "#d97706"); return; }
    clipboard.clone(c => {
      c.set({ left: (c.left || 0) + 24, top: (c.top || 0) + 24, selectable: true, evented: true });
      if (c.type === "activeSelection") { c.canvas = ed.canvas; c.forEachObject(o => ed.canvas.add(o)); c.setCoords(); } else ed.canvas.add(c);
      werkzeugSetzen(ed, "select"); ed.canvas.setActiveObject(c); ed.canvas.requestRenderAll();
    });
  }
  function loeschen(ed) { const objs = ed.canvas.getActiveObjects(); if (!objs.length) { showToast("Wähle zuerst ein Objekt (Auswahlwerkzeug).", "#d97706"); return; } ed.canvas.discardActiveObject(); objs.forEach(o => ed.canvas.remove(o)); ed.canvas.requestRenderAll(); }
  BIE.actions["z-copy"] = el => { const ed = editors[el.dataset.nr]; if (ed) kopieren(ed); };
  BIE.actions["z-paste"] = el => { const ed = editors[el.dataset.nr]; if (ed) einfuegen(ed); };
  BIE.actions["z-delete"] = el => { const ed = editors[el.dataset.nr]; if (ed) loeschen(ed); };
  BIE.actions["z-clear"] = el => { const ed = editors[el.dataset.nr]; if (ed && confirm("Wirklich die ganze Zeichnung leeren?")) { ed.canvas.clear(); ed.canvas.backgroundColor = "#ffffff"; ed.canvas.requestRenderAll(); ed.canvas.fire("object:removed", {}); } };
  BIE.actions["z-save"] = async el => {
    const ed = editors[el.dataset.nr]; if (!ed) return;
    const t = aufgabenByNr[ed.nr]; const cfg = cfgOf(t);
    const n = ed.canvas.getObjects().length;
    if (n < 3) { showFb(ed.nr, "err", "⚠️ Zeichne noch etwas mehr – mindestens drei Elemente."); return; }
    clearTimeout(ed.timer);
    const r = await speichern(ed, true);
    if (!r.ok) { showFb(ed.nr, "err", "⚠️ " + (r.fehler || "Sichern fehlgeschlagen.")); return; }
    sendAntwort(ed.nr, "zeichnung", `${n} Objekte abgegeben`, null, cfg.aufgabe);
    showFb(ed.nr, "ok", `✅ Zeichnung mit ${n} Objekten abgegeben – deine Lehrkraft sieht die Vorschau. Du kannst weiter zeichnen.`);
    markComplete(ed.nr);
  };
  BIE.actions["z-ki"] = el => {
    const ed = editors[el.dataset.nr]; if (!ed) return;
    const t = aufgabenByNr[ed.nr]; const cfg = cfgOf(t);
    if (ed.canvas.getObjects().length < 2) { showFb(ed.nr, "err", "⚠️ Zeichne zuerst etwas."); return; }
    const png = sauberesPNG(ed);
    const aufgabe = `${cfg.aufgabe} Erwartete Elemente: ${(cfg.elemente || []).join("; ")}`;
    BIE.ki.zeichnung(ed.nr, png, aufgabe, data => {
      const sterne = data.sterne == null ? "" : "⭐".repeat(data.sterne) + "☆".repeat(3 - data.sterne) + " ";
      const listen = (data.erkannt && data.erkannt.length ? `<br>✔ Erkannt: ${esc(data.erkannt.join(", "))}` : "") + (data.fehlt && data.fehlt.length ? `<br>➕ Fehlt noch: ${esc(data.fehlt.join(", "))}` : "");
      sendAntwort(ed.nr, "zeichnung", `KI: ${data.sterne ?? "?"} Sterne – ${(data.feedback || "").slice(0, 200)}`, data.sterne != null ? data.sterne >= 2 : null, cfg.aufgabe);
      showFb(ed.nr, data.sterne >= 2 ? "ok" : "info", sterne + BIE.ki.md(data.feedback || "") + listen);
      if (data.sterne >= 2) markComplete(ed.nr);
    }, { geraet: ed.geraet, niveau: BIE.niveauOf(ed.nr) });
  };
  document.addEventListener("keydown", e => {
    if (!lastActive || !editors[lastActive]) return;
    const ed = editors[lastActive];
    const inText = ed.canvas.getActiveObject() && ed.canvas.getActiveObject().isEditing;
    if (inText || /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "c") { kopieren(ed); e.preventDefault(); }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "v") { einfuegen(ed); e.preventDefault(); }
    if (e.key === "Delete" || e.key === "Backspace") { if (ed.canvas.getActiveObjects().length) { loeschen(ed); e.preventDefault(); } }
  });

  function dispose(nr) { const ed = editors[nr]; if (!ed) return; clearTimeout(ed.timer); pending[ed.geraet] = ed.canvas.toJSON(); try { ed.canvas.dispose(); } catch (e) { /* egal */ } delete editors[nr]; pendingMount.delete(nr); }

  // ─── Handschrift-Pad (Pencil → KI-Transkription in die Stichpunkte) ─────
  const pads = {};
  function mountPad(t) {
    const host = document.getElementById("pad-host-" + t.abschnitt); if (!host) return;
    host.innerHTML = `<button class="btn btn-outline btn-sm" type="button" data-action="pad-open" data-abschnitt="${t.abschnitt}" data-nr="${t.nr}">✍️ Mit Finger oder Pencil schreiben</button>`;
  }
  BIE.actions["pad-open"] = el => {
    const abschnitt = el.dataset.abschnitt, nr = el.dataset.nr;
    const host = document.getElementById("pad-host-" + abschnitt);
    host.innerHTML = `<div class="pad-box">
        <p class="hint">Schreibe deine Stichpunkte mit dem Stift. „Erkennen lassen“ schickt das Bild an die KI (Freigabe nötig) und trägt den Text oben ein. Das Bild wird danach gelöscht.</p>
        <div class="zeichen-wrap pad-wrap" id="padw-${abschnitt}"><canvas id="pad-${abschnitt}" aria-label="Handschrift-Fläche"></canvas></div>
        <div class="btn-row">
          <button class="btn btn-ai btn-sm" type="button" data-action="pad-erkennen" data-abschnitt="${abschnitt}" data-nr="${nr}">🤖 Erkennen lassen</button>
          <button class="btn btn-quiet btn-sm" type="button" data-action="pad-leeren" data-abschnitt="${abschnitt}">🧹 Leeren</button>
          <button class="btn btn-quiet btn-sm" type="button" data-action="pad-close" data-abschnitt="${abschnitt}" data-nr="${nr}">Schließen</button>
        </div></div>`;
    if (!fabricDa()) return;
    const c = new fabric.Canvas(document.getElementById("pad-" + abschnitt), { isDrawingMode: true, selection: false, backgroundColor: "#ffffff" });
    const padWrap = document.getElementById("padw-" + abschnitt);
    const w = Math.max(300, (padWrap && padWrap.clientWidth) || host.clientWidth);
    c.setDimensions({ width: w, height: 240 });
    c.freeDrawingBrush = new fabric.PencilBrush(c); c.freeDrawingBrush.color = "#1e293b"; c.freeDrawingBrush.width = 3;
    pads[abschnitt] = c;
  };
  BIE.actions["pad-leeren"] = el => { const c = pads[el.dataset.abschnitt]; if (c) { c.clear(); c.backgroundColor = "#ffffff"; c.requestRenderAll(); } };
  BIE.actions["pad-close"] = el => { const c = pads[el.dataset.abschnitt]; if (c) { try { c.dispose(); } catch (e) { /* egal */ } delete pads[el.dataset.abschnitt]; } mountPad({ abschnitt: el.dataset.abschnitt, nr: el.dataset.nr }); };
  BIE.actions["pad-erkennen"] = el => {
    const abschnitt = el.dataset.abschnitt, nr = el.dataset.nr; const c = pads[abschnitt];
    if (!c || c.getObjects().length < 1) { showFb(nr, "err", "⚠️ Schreibe zuerst etwas auf die Fläche."); return; }
    const png = c.toDataURL({ format: "png", multiplier: 1 });
    BIE.ki.handschrift(nr, png, data => {
      if (!data.text) { showFb(nr, "err", "⚠️ " + esc(data.message || "Nichts erkannt.")); return; }
      const ta = document.getElementById("nt-" + abschnitt);
      const zeilen = data.text.split("\n").map(z => z.trim()).filter(Boolean).map(z => (z.startsWith("•") || z.startsWith("-") ? z : "• " + z));
      ta.value = (ta.value.trim() ? ta.value.replace(/\s+$/, "") + "\n" : "") + zeilen.join("\n");
      ta.dispatchEvent(new Event("input", { bubbles: true }));
      c.clear(); c.backgroundColor = "#ffffff"; c.requestRenderAll();
      showFb(nr, "ok", `✅ ${zeilen.length} Zeile(n) erkannt und eingetragen – bitte prüfen und bei Bedarf korrigieren.`);
    });
  };

  // ─── Backup-Registrierung ─────────────────────────────────────────────
  BIE.autosave.register("zeichnungen", compact => {
    const out = {};
    Object.values(editors).forEach(ed => { const j = ed.canvas.toJSON(); out[ed.geraet] = { json: j, objekte: (j.objects || []).length }; if (!compact && previews[ed.geraet]) out[ed.geraet].preview = previews[ed.geraet]; });
    Object.entries(pending).forEach(([g, j]) => { if (!out[g]) out[g] = { json: j, objekte: (j.objects || []).length }; });
    return out;
  }, data => new Promise(resolve => {
    let offen = 0;
    Object.entries(data || {}).forEach(([geraet, d]) => {
      if (!d || !d.json || typeof d.json !== "object") return;
      pending[geraet] = d.json;
      const ed = Object.values(editors).find(e => e.geraet === geraet);
      if (ed) { offen++; ed.laden = true; ed.canvas.loadFromJSON(d.json, () => { ed.canvas.backgroundColor = "#ffffff"; werkzeugSetzen(ed, ed.tool); ed.canvas.renderAll(); ed.laden = false; statistik(ed); if (--offen === 0) resolve(); }); }
    });
    if (!offen) resolve();
  }), 60);

  async function ladeServer() {
    const r = await BIE.getJSON("/api/zeichnungen");
    if (r && r.ok) Object.entries(r.zeichnungen || {}).forEach(([g, z]) => { if (!pending[g] && z.json) pending[g] = z.json; if (z.preview) previews[g] = z.preview; });
  }

  function resizeAll() { Object.values(editors).forEach(ed => { try { passeGroesseAn(ed); } catch (e) { /* egal */ } }); }

  return { render, mount, dispose, mountPad, ladeServer, editors, resizeAll };
})();
