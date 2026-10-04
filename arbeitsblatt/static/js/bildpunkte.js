/* Bild mit antippbaren Punkten: einordnen oder benennen (Aufgabentyp „bildpunkte“, früher „teich“).

   Daten:  INHALTE.bildpunkte.<karte> = { bild, breite, hoehe, punkte: [{ id, x, y, name, aliase, kat }] }
           Aufgabe: { nr, typ: "bildpunkte", karte: "<karte>", niveaus: { A: cfg, B: cfg, C: cfg } }
   Die Koordinaten gehören zur SVG-Datei (Pixel im Bild). Die ersten `anzahl` Punkte der Datenreihenfolge
   gelten je Niveau – so sieht die Lehrkraft im Dashboard vergleichbare Antworten.

   Zwei Modi je Niveau (cfg.modus):
     "einordnen" (Standard): Punkt antippen, dann einer von zwei Kategorien zuordnen.
                  cfg.kategorien = [„Kategorie für kat 0“, „Kategorie für kat 1“]; cfg.namen: false = Name zusätzlich eintippen.
     "benennen":  Punkt antippen, dann den Namen wählen (Wortkiste; cfg.ablenker = zusätzliche falsche Wörter)
                  oder eintippen (cfg.eingabe: "text").
   Format mit Beispielen: docs/INHALTE_FORMAT.md. */
BIE.bildpunkte = (() => {
  "use strict";
  const { INHALTE, APP, state, $, $$, esc, shuffle, normalize, cfgOf, body, showFb, markComplete,
          sendAntwort, dirty, aufgabenByNr } = BIE;

  const spec = t => INHALTE.bildpunkte && INHALTE.bildpunkte[t.karte];
  const modusVon = cfg => cfg.modus || (cfg.kategorien ? "einordnen" : "benennen");
  const katVon = p => (Number.isInteger(p.kat) ? p.kat : 0);

  function punkteFuer(t) {
    const cfg = cfgOf(t) || {};
    const alle = (spec(t) || { punkte: [] }).punkte;
    return alle.slice(0, Math.min(cfg.anzahl || alle.length, alle.length));
  }

  function buildSVG(t, punkte) {
    const s = spec(t);
    const bild = s.bild + (APP.assetVersion ? (s.bild.includes("?") ? "&" : "?") + "v=" + APP.assetVersion : "");
    // Jeder Punkt: ein unsichtbarer Trefferkreis (bp-hit, auf dem Bildschirm mindestens 44 px) und der sichtbare Punkt (bp-sicht).
    // Die Größen setzt anpassen() nach dem Zeichnen und bei jeder Größenänderung; getippt wird über das Bild (bp-bild).
    const dots = punkte.map((p, i) => `
      <g class="bp-dot" data-nr="${t.nr}" data-spot="${p.id}" role="button" tabindex="0" aria-label="Punkt ${i + 1}">
        <circle class="bp-hit" cx="${p.x}" cy="${p.y}" r="24"/>
        <circle class="bp-sicht" cx="${p.x}" cy="${p.y}" r="24"/>
        <text class="hs-icon" x="${p.x}" y="${p.y}" text-anchor="middle" dominant-baseline="central" aria-hidden="true">${i + 1}</text>
      </g>`).join("");
    return `
      <div class="map-wrap bp-wrap">
        <svg viewBox="0 0 ${s.breite} ${s.hoehe}" class="map-svg bp-svg" data-action="bp-bild" data-nr="${t.nr}" xmlns="http://www.w3.org/2000/svg"
             role="group" aria-label="${esc(t.titel)} – Bild mit ${punkte.length} antippbaren Punkten">
          <image href="${esc(bild)}" x="0" y="0" width="${s.breite}" height="${s.hoehe}"/>
          ${dots}
        </svg>
      </div>`;
  }

  function render(t) {
    const cfg = cfgOf(t) || {};
    if (!spec(t)) return `<p class="muted">⚠️ Bild „${esc(t.karte)}“ fehlt in INHALTE.bildpunkte.</p>`;
    const punkte = punkteFuer(t);
    const modus = modusVon(cfg);
    const rt = state.runtime[t.nr] = { modus, wahl: {}, namen: {}, geprueft: false, fertig: false, anzahl: punkte.length };
    if (modus === "benennen") rt.wortkiste = shuffle([...new Set(punkte.map(p => p.name).concat(cfg.ablenker || []))]);
    const kat = cfg.kategorien || [];
    const auftrag = cfg.auftrag || t.auftrag;       // Aufgabentext (freiwillig, je Niveau oder an der Aufgabe) über dem Bild
    return `${auftrag ? `<p class="task-question bp-auftrag">${esc(auftrag)}</p>` : ""}${buildSVG(t, punkte)}
      <div class="feedback-box feedback-info show bp-info" id="bpinfo-${t.nr}" role="status">
        👆 Tippe einen nummerierten Punkt im Bild an. ${modus === "benennen" ? "Dann gib ihm den richtigen Namen." : "Ordne ihn dann ein."}
        <span class="map-progress" id="bpprog-${t.nr}">0/${punkte.length}</span>
      </div>
      <div class="bp-panel" id="bppanel-${t.nr}" hidden></div>
      ${modus === "einordnen" && kat.length ? `<p class="bp-legende">
        <span class="bp-chip bp-chip-a">${esc(kat[0])}</span><span class="bp-chip bp-chip-b">${esc(kat[1] || "")}</span></p>` : ""}
      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="bp-pruefen" data-nr="${t.nr}">✅ Prüfen</button>
      </div>`;
  }

  function panelZeigen(nr, p) {
    const t = aufgabenByNr[nr], cfg = cfgOf(t) || {}, rt = state.runtime[nr];
    const punkte = punkteFuer(t);
    const pos = punkte.findIndex(x => x.id === p.id) + 1;
    const panel = document.getElementById("bppanel-" + nr);
    let html;
    if (rt.modus === "benennen") {
      if (cfg.eingabe === "text") {
        html = `<label class="bp-name-label">Wie heißt Nummer ${pos}?
          <input type="text" class="bp-name" id="bpname-${nr}" data-action-input="bpname" data-nr="${nr}" data-spot="${p.id}"
                 value="${esc(rt.namen[p.id] || "")}" autocomplete="off" autocapitalize="off" placeholder="Name eintippen"></label>`;
      } else {
        html = `<p class="bp-frage">Wie heißt Nummer ${pos}?</p>
          <div class="bp-wortkiste" role="group" aria-label="Wortkiste für Nummer ${pos}">
            ${rt.wortkiste.map(w => `<button class="word-chip bp-wort${rt.namen[p.id] === w ? " bp-gewaehlt" : ""}" type="button"
              data-action="bp-name" data-nr="${nr}" data-spot="${p.id}" data-name="${esc(w)}">${esc(w)}</button>`).join("")}
          </div>`;
      }
    } else {
      const kat = cfg.kategorien || ["Gruppe 1", "Gruppe 2"];
      const gewaehlt = rt.wahl[p.id];
      const nameFeld = cfg.namen === false
        ? `<label class="bp-name-label">Wie heißt Nummer ${pos}?
             <input type="text" class="bp-name" id="bpname-${nr}" data-action-input="bpname" data-nr="${nr}" data-spot="${p.id}"
                    value="${esc(rt.namen[p.id] || "")}" autocomplete="off" autocapitalize="off" placeholder="Name eintippen"></label>`
        : `<p class="bp-name-fest">Nummer ${pos}: <strong>${esc(p.name)}</strong></p>`;
      html = `${nameFeld}
        <p class="bp-frage">Wohin gehört das?</p>
        <div class="mc-options bp-wahl" role="group" aria-label="Einordnung von Nummer ${pos}">
          <button class="mc-btn${gewaehlt === 0 ? " selected-multi" : ""}" type="button" data-action="bp-wahl" data-nr="${nr}" data-spot="${p.id}" data-kat="0">${esc(kat[0])}</button>
          <button class="mc-btn${gewaehlt === 1 ? " selected-multi" : ""}" type="button" data-action="bp-wahl" data-nr="${nr}" data-spot="${p.id}" data-kat="1">${esc(kat[1] || "")}</button>
        </div>`;
    }
    panel.hidden = false;
    panel.innerHTML = html;
    $$(".bp-dot.active", body(nr)).forEach(e => e.classList.remove("active"));
    const g = $(`.bp-dot[data-spot="${p.id}"]`, body(nr));
    if (g) g.classList.add("active");
  }

  // gesetzt = der Punkt hat eine Antwort (Einordnung bzw. Name)
  const gesetzt = (rt, p) => (rt.modus === "benennen" ? !!normalize(rt.namen[p.id] || "") : rt.wahl[p.id] !== undefined);

  function fortschritt(nr) {
    const t = aufgabenByNr[nr], rt = state.runtime[nr];
    if (!rt) return;
    const punkte = punkteFuer(t);
    const el = document.getElementById("bpprog-" + nr);
    if (el) el.textContent = `${punkte.filter(p => gesetzt(rt, p)).length}/${punkte.length}`;
    punkte.forEach(p => {
      const g = $(`.bp-dot[data-spot="${p.id}"]`, body(nr));
      if (g) g.classList.toggle("gesetzt", gesetzt(rt, p));
    });
  }

  function nachAenderung(nr) {
    const rt = state.runtime[nr];
    if (rt.geprueft) {
      // Nach einer Prüfung mit Fehlern darf weiter korrigiert werden – sonst steht
      // „die roten Punkte passen noch nicht“ da, ohne dass man etwas ändern kann.
      rt.geprueft = false;
      $$(".bp-dot", body(nr)).forEach(g => g.classList.remove("korrekt", "falsch"));
      BIE.clearFb(nr);
    }
    fortschritt(nr);
    dirty();
  }

  const punktMit = (nr, id) => punkteFuer(aufgabenByNr[nr]).find(x => x.id === id);

  BIE.actions.bpspot = g => { const p = punktMit(g.dataset.nr, g.dataset.spot); if (p) panelZeigen(g.dataset.nr, p); };

  // ─── Größen auf dem Bildschirm: Touchziel ≥ 44 px, nächster Punkt gewinnt ───
  const ZIEL_PX = 44, SICHT_PX = 32, MIN_R = 24;
  // Nächster Punkt, dessen Trefferkreis (hitR) den Tippunkt (x, y) enthält; -1 = keiner
  function punktAn(punkte, x, y, hitR) {
    let best = -1, abstand = Infinity;
    punkte.forEach((p, i) => { const a = Math.hypot(x - p.x, y - p.y); if (a <= hitR && a < abstand) { best = i; abstand = a; } });
    return best;
  }
  // Radien in Bildeinheiten für eine Bildbreite in Pixeln: Trefferkreis ≥ 44 px Durchmesser, sichtbarer Punkt ≈ 32 px,
  // aber nie so groß, dass sich zwei Punkte überdecken (halber Abstand zum nächsten Nachbarn).
  function radien(punkte, bildBreite, px) {
    const einheit = px > 0 ? bildBreite / px : 1;               // Bildeinheiten je Pixel
    let nah = Infinity;
    punkte.forEach((p, i) => punkte.slice(i + 1).forEach(q => { nah = Math.min(nah, Math.hypot(p.x - q.x, p.y - q.y)); }));
    const hit = Math.max(MIN_R, ZIEL_PX / 2 * einheit);
    const sicht = Math.max(MIN_R, Math.min(SICHT_PX / 2 * einheit, nah / 2 - 2));
    return { hit, sicht, schrift: Math.max(24, Math.min(sicht * 0.95, 15 * einheit)) };
  }
  function anpassen(svg) {
    const t = aufgabenByNr[svg.dataset.nr], vb = svg.viewBox.baseVal, px = svg.getBoundingClientRect().width;
    if (!t || !vb || !vb.width || !px) return;
    const r = radien(punkteFuer(t), vb.width, px);
    svg.dataset.hit = String(r.hit);
    $$(".bp-hit", svg).forEach(c => c.setAttribute("r", String(r.hit)));
    $$(".bp-sicht", svg).forEach(c => c.setAttribute("r", String(r.sicht)));
    $$(".hs-icon", svg).forEach(x => { x.style.fontSize = r.schrift + "px"; });
  }
  const beobachter = ("ResizeObserver" in window) ? new ResizeObserver(es => es.forEach(e => anpassen(e.target))) : null;
  function nachRender(t) {
    const svg = $("svg.bp-svg", body(t.nr)); if (!svg) return;
    anpassen(svg);
    if (beobachter && !svg.dataset.beobachtet) { svg.dataset.beobachtet = "1"; beobachter.observe(svg); }
  }
  // Tipp ins Bild: der nächstgelegene Punkt im Trefferkreis (so wählt man auch bei dicht liegenden Punkten den richtigen)
  BIE.actions["bp-bild"] = (svg, ev) => {
    if (!ev || !svg.viewBox) return;
    const t = aufgabenByNr[svg.dataset.nr], box = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal; if (!t || !box.width) return;
    const punkte = punkteFuer(t), hit = parseFloat(svg.dataset.hit) || MIN_R;
    const i = punktAn(punkte, (ev.clientX - box.left) * vb.width / box.width, (ev.clientY - box.top) * vb.height / box.height, hit);
    if (i >= 0) panelZeigen(t.nr, punkte[i]);
  };
  BIE.actions["bp-wahl"] = el => {
    const nr = el.dataset.nr, rt = state.runtime[nr];
    if (!rt || rt.fertig) return;          // nur wenn schon alles stimmte, ist Schluss
    rt.wahl[el.dataset.spot] = parseInt(el.dataset.kat, 10);
    nachAenderung(nr);
    panelZeigen(nr, punktMit(nr, el.dataset.spot));
  };
  BIE.actions["bp-name"] = el => {
    const nr = el.dataset.nr, rt = state.runtime[nr];
    if (!rt || rt.fertig) return;
    rt.namen[el.dataset.spot] = el.dataset.name;
    nachAenderung(nr);
    panelZeigen(nr, punktMit(nr, el.dataset.spot));
  };
  BIE.actions.bpname = el => {
    const rt = state.runtime[el.dataset.nr];
    if (!rt || rt.fertig) return;
    rt.namen[el.dataset.spot] = el.value;
    nachAenderung(el.dataset.nr);
  };
  document.addEventListener("keydown", e => {
    if ((e.key === "Enter" || e.key === " ") && e.target.classList && e.target.classList.contains("bp-dot")) {
      e.preventDefault(); BIE.actions.bpspot(e.target);
    }
  });

  function nameStimmt(p, eingabe) {
    const n = normalize(eingabe || "");
    if (!n) return false;
    return [p.name].concat(p.aliase || []).some(a => normalize(a) === n);
  }
  // Eigene Rückmeldung zu einem typischen Fehlnamen: punkt.falsch = [{ aliase: ["Bienenstock"], text: "Der Bienenstock ist das ganze Zuhause des Volkes. Die Holzkiste heißt …" }].
  // Gilt nur für eine falsche Eingabe (die richtigen Namen und Aliase gehen vor); gibt den Text oder null zurück.
  function falschText(p, eingabe) {
    const n = normalize(eingabe || "");
    if (!n || nameStimmt(p, eingabe)) return null;
    const f = (Array.isArray(p.falsch) ? p.falsch : []).find(x => x && typeof x.text === "string" && [].concat(x.aliase || []).some(a => normalize(a) === n));
    return f ? f.text : null;
  }

  function pruefen(nr, silent) {
    const t = aufgabenByNr[nr], cfg = cfgOf(t) || {}, rt = state.runtime[nr];
    if (!rt) return;
    const punkte = punkteFuer(t);
    const offen = punkte.filter(p => !gesetzt(rt, p));
    if (offen.length && !silent) {
      showFb(nr, "err", `⚠️ Es fehlen noch ${offen.length} von ${punkte.length} Punkten. Tippe sie im Bild an.`);
      return;
    }
    if (offen.length) return;
    let richtig = 0, namenRichtig = 0;
    const sonderHinweise = [];
    punkte.forEach(p => {
      const ok = rt.modus === "benennen" ? nameStimmt(p, rt.namen[p.id]) : rt.wahl[p.id] === katVon(p);
      if (!ok && rt.modus === "benennen") { const f = falschText(p, rt.namen[p.id]); if (f && !sonderHinweise.includes(f)) sonderHinweise.push(f); }
      if (ok) richtig++;
      if (rt.modus === "einordnen" && cfg.namen === false && nameStimmt(p, rt.namen[p.id])) namenRichtig++;
      const g = $(`.bp-dot[data-spot="${p.id}"]`, body(nr));
      if (g) { g.classList.remove("gesetzt"); g.classList.add(ok ? "korrekt" : "falsch"); }
    });
    rt.geprueft = true;
    const alle = richtig === punkte.length;
    rt.fertig = alle;
    const namenTeil = rt.modus === "einordnen" && cfg.namen === false ? ` ${namenRichtig} von ${punkte.length} Namen erkannt.` : "";
    const was = rt.modus === "benennen" ? "richtig benannt" : "richtig eingeordnet";
    if (!silent) {
      sendAntwort(nr, "bildpunkte", `${richtig}/${punkte.length} ${was}`, alle, t.titel);
      if (alle) {
        showFb(nr, "ok", `✅ Alle ${punkte.length} ${was}!${namenTeil}`);
        markComplete(nr);
      } else {
        showFb(nr, "err", `❌ ${richtig} von ${punkte.length} ${was}. Die roten Punkte passen noch nicht. ${cfg.hilfe || "Schau sie dir noch einmal genau an."}${namenTeil}${sonderHinweise.map(h => `<br>💡 ${esc(h)}`).join("")}`);
      }
    } else if (alle) {
      markComplete(nr);
    }
    dirty();
  }
  BIE.actions["bp-pruefen"] = el => pruefen(el.dataset.nr);

  function collect(nr) {
    const rt = state.runtime[nr];
    if (!rt || !rt.wahl) return undefined;
    if (!Object.keys(rt.wahl).length && !Object.keys(rt.namen).length) return undefined;
    return { typ: "bildpunkte", wahl: Object.assign({}, rt.wahl), namen: Object.assign({}, rt.namen),
             geprueft: !!rt.geprueft, fertig: !!rt.fertig };
  }
  function restore(nr, d) {
    const rt = state.runtime[nr];
    if (!rt || !d) return;
    rt.wahl = Object.assign({}, d.wahl || {});
    rt.namen = Object.assign({}, d.namen || {});
    fortschritt(nr);
    if (d.geprueft) pruefen(nr, true);
  }

  return { render, nachRender, collect, restore, logik: { punktAn, radien, nameStimmt, falschText } };
})();
