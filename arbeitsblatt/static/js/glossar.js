/* Glossar: fett markierte Fachbegriffe werden antippbar und öffnen eine Erklärung mit Schaubild. */
BIE.glossar = (() => {
  "use strict";
  const { $, $$, esc, getJSON } = BIE;
  let daten = null;
  let laden = null;
  let letzterAusloeser = null;

  const norm = s => String(s || "").replace(/[„“"'’‚‘]/g, "").toLowerCase().trim().replace(/[.,;:!?]+$/, "").trim().replace(/\s+/g, " ");

  async function holen() {
    if (daten) return daten;
    if (!laden) laden = getJSON("/api/glossar").then(d => { daten = d && d.ok ? d : { eintraege: {}, aliase: {} }; return daten; });
    return laden;
  }

  // Wandelt <strong> und <em> innerhalb eines Elements in Glossar-Links um, wenn ein Eintrag existiert.
  async function verlinken(root) {
    const d = await holen();
    if (!root) return;
    $$("strong, em", root).forEach(el => {
      if (el.closest(".glossar-link") || el.dataset.glossar) return;
      const key = d.aliase[norm(el.textContent)];
      if (!key) return;
      el.dataset.glossar = key;
      const btn = document.createElement("button");
      btn.type = "button"; btn.className = "glossar-link"; btn.dataset.action = "glossar-open"; btn.dataset.key = key;
      btn.setAttribute("aria-label", `Erklärung: ${d.eintraege[key].titel}`);
      btn.innerHTML = el.innerHTML + '<span class="glossar-i" aria-hidden="true">i</span>';
      el.replaceWith(btn);
    });
  }

  function oeffnen(key, ausloeser) {
    const e = daten && daten.eintraege[key]; if (!e) return;
    letzterAusloeser = ausloeser || null;
    $("#glossar-titel").textContent = e.titel;
    $("#glossar-text").textContent = e.text;
    const fig = $("#glossar-figur"); const img = $("#glossar-bild");
    if (e.bild) { img.src = e.bild; img.alt = "Schaubild: " + e.titel; fig.hidden = false; } else { fig.hidden = true; img.removeAttribute("src"); }
    $("#glossar-dialog").hidden = false;
    document.body.classList.add("no-scroll");
    setTimeout(() => $("#glossar-close").focus(), 30);
  }
  function schliessen() {
    $("#glossar-dialog").hidden = true;
    document.body.classList.remove("no-scroll");
    if (letzterAusloeser && letzterAusloeser.focus) letzterAusloeser.focus();
  }
  BIE.actions["glossar-open"] = el => oeffnen(el.dataset.key, el);
  BIE.actions["glossar-close"] = schliessen;
  document.addEventListener("keydown", e => { if (e.key === "Escape" && $("#glossar-dialog") && !$("#glossar-dialog").hidden) schliessen(); });
  document.addEventListener("click", e => { if (e.target.id === "glossar-dialog") schliessen(); });

  return { holen, verlinken, oeffnen, schliessen };
})();
