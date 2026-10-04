/* Schrittmodus: Immer nur eine Station ist offen. Erledigte Stationen klappen zusammen,
   spätere bleiben ausgeblendet. Nach „Weiter“ erscheint die nächste Station.
   „Später machen“ überspringt eine Station, damit niemand stecken bleibt.
   Die Reiter werden nacheinander freigeschaltet. */
BIE.schritte = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, showToast, dirty, stationenVon, aufgabenByNr } = BIE;
  const uebersprungen = new Set();
  const bestaetigt = new Set();
  const reihenfolge = {};
  const tabKeys = INHALTE.tabs.map(t => t.key);
  // Die Lesestrecke steht dort, wo der Plan sie nennt (tab.leseNach), nicht zwingend oben.
  INHALTE.tabs.forEach(tab => { reihenfolge[tab.key] = stationenVon(tab); });
  const tabVon = {};
  Object.entries(reihenfolge).forEach(([key, liste]) => liste.forEach(nr => { tabVon[nr] = key; }));

  const fertigMit = nr => state.completed.has(nr);
  const abgehakt = nr => (fertigMit(nr) && bestaetigt.has(nr)) || uebersprungen.has(nr);
  const durchgearbeitet = nr => fertigMit(nr) || uebersprungen.has(nr);

  function aktuelleStation(tabKey) {
    return (reihenfolge[tabKey] || []).find(nr => !abgehakt(nr)) || null;
  }
  function tabFrei(key) {
    if (BIE.pruefmodus) return true;
    if (BIE.film && BIE.film.tabGesperrt(key)) return false;   // Reiter mit filmFrei: erst nach vollständigem Film
    const i = tabKeys.indexOf(key);
    if (i <= 0) return true;
    return reihenfolge[tabKeys[i - 1]].every(durchgearbeitet);
  }
  function erstesFreiesTab() {
    let frei = tabKeys[0];
    for (const k of tabKeys) { if (tabFrei(k)) frei = k; else break; }
    return frei;
  }
  function elementFuer(tabKey, nr) {
    return nr.startsWith("L") ? document.getElementById("lese-" + tabKey) : BIE.card(nr);
  }
  function titelFuer(tabKey, nr) {
    if (nr.startsWith("L")) return BIE.anzeigeLabel(nr);   // „Lesestrecke 3“
    const t = aufgabenByNr[nr];
    return t ? `${BIE.anzeigeLabel(nr)}: ${t.titel}` : `Station ${BIE.anzeigeNr(nr)}`;   // sichtbar die laufende Nummer, nicht die interne
  }

  // ─── Bedienleiste unter der aktuellen Station ────────────────────────
  function leisteRendern(tabKey, nr, el, istAktuell) {
    const karte = nr.startsWith("L") ? el.querySelector(".lese-card") : el;
    if (!karte) return;
    let leiste = karte.querySelector(":scope > .schritt-leiste");
    if (!istAktuell) { if (leiste) leiste.remove(); return; }
    if (!leiste) { leiste = document.createElement("div"); leiste.className = "schritt-leiste"; karte.appendChild(leiste); }
    const fertig = fertigMit(nr);
    const letzte = reihenfolge[tabKey][reihenfolge[tabKey].length - 1] === nr;
    leiste.innerHTML = fertig
      ? `<span class="schritt-status">✅ Geschafft!</span><button class="btn btn-primary" type="button" data-action="schritt-weiter" data-nr="${esc(nr)}">${letzte ? "Abschnitt abschließen ✓" : "Weiter zur nächsten Aufgabe →"}</button>`
      : `<span class="schritt-status">Erst diese Aufgabe, dann geht es weiter.</span><button class="btn btn-quiet btn-sm" type="button" data-action="schritt-spaeter" data-nr="${esc(nr)}">Später machen ⏭</button>`;
  }

  // ─── Zusammengeklappte Stationen: Kopfzeile mit Aufklapp-Knopf ───────
  function toggleRendern(tabKey, nr, el, zu) {
    const header = el.querySelector(".task-header");
    if (!header) return;
    let btn = header.querySelector(".schritt-toggle");
    if (!zu) { if (btn) btn.remove(); return; }
    if (!btn) { btn = document.createElement("button"); btn.type = "button"; btn.className = "btn btn-quiet btn-sm schritt-toggle"; btn.dataset.action = "schritt-toggle"; btn.dataset.nr = nr; header.appendChild(btn); }
    const offen = el.classList.contains("is-open");
    const status = uebersprungen.has(nr) && !fertigMit(nr) ? "⏭ übersprungen" : "✅ erledigt";
    btn.innerHTML = `<span class="schritt-toggle-status">${status}</span> ${offen ? "Zuklappen ▲" : "Anzeigen ▼"}`;
    btn.setAttribute("aria-expanded", offen);
  }

  function fertigKarte(tabKey, fertig) {
    const panel = document.getElementById("tab-" + tabKey); if (!panel) return;
    let karte = document.getElementById("fertig-" + tabKey);
    if (!fertig) { if (karte) karte.remove(); return; }
    const i = tabKeys.indexOf(tabKey); const next = INHALTE.tabs[i + 1];
    const offen = reihenfolge[tabKey].filter(nr => uebersprungen.has(nr) && !fertigMit(nr));
    if (!karte) { karte = document.createElement("article"); karte.className = "card schritt-fertig"; karte.id = "fertig-" + tabKey; panel.appendChild(karte); }
    karte.innerHTML = `<span class="eyebrow">Abschnitt geschafft</span><h2>🎉 ${esc(INHALTE.tabs[i].label)} durchgearbeitet</h2>
      ${offen.length ? `<p class="hint">Übersprungen: ${offen.map(nr => esc(titelFuer(tabKey, nr))).join(", ")}. Tippe oben auf „Anzeigen“, um sie nachzuholen.</p>` : `<p class="muted">Alle Stationen sind erledigt.</p>`}
      ${next ? `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="tab" data-tab="${next.key}">Weiter zu „${esc(next.label)}“ →</button></div>` : `<p class="muted">Du hast das ganze Arbeitsblatt bearbeitet. Stark!</p>`}`;
  }

  function navAktualisieren() {
    tabKeys.forEach(k => {
      const btn = document.getElementById("btn-tab-" + k); if (!btn) return;
      const frei = tabFrei(k);
      btn.classList.toggle("is-locked", !frei);
      btn.setAttribute("aria-disabled", !frei);
      btn.title = frei ? "" : "Erst den vorherigen Abschnitt durcharbeiten";
    });
  }

  function aktualisieren(tabKey) {
    const liste = reihenfolge[tabKey]; if (!liste) return;
    if (BIE.pruefmodus) {   // alles sichtbar, keine Leisten, keine Sperren
      liste.forEach(nr => { const el = elementFuer(tabKey, nr); if (el) { el.hidden = false; el.classList.remove("is-collapsed", "is-current", "is-open"); } });
      return;
    }
    const aktuell = aktuelleStation(tabKey);
    let danach = false;
    liste.forEach(nr => {
      const el = elementFuer(tabKey, nr); if (!el) return;
      const istAktuell = nr === aktuell;
      el.hidden = danach;
      el.classList.toggle("is-collapsed", !istAktuell && !danach);
      el.classList.toggle("is-current", istAktuell);
      if (istAktuell) el.classList.remove("is-open");
      toggleRendern(tabKey, nr, el, !istAktuell && !danach);
      leisteRendern(tabKey, nr, el, istAktuell);
      if (istAktuell) danach = true;
    });
    fertigKarte(tabKey, aktuell === null);
    navAktualisieren();
    if (BIE.film && BIE.film.stationWechsel) BIE.film.stationWechsel(tabKey, aktuell);   // Bühne ein-/ausklappen je nach Station (film.js)
    if (aktuell && !aktuell.startsWith("L")) {
      const ch = state.charts[aktuell]; if (ch) { try { ch.resize(); } catch (e) { /* egal */ } }
      if (BIE.zeichnen && BIE.zeichnen.resizeAll) BIE.zeichnen.resizeAll();
    }
  }
  function alleAktualisieren() { tabKeys.forEach(aktualisieren); }

  function zurAktuellen(tabKey) {
    const nr = aktuelleStation(tabKey);
    const el = nr ? elementFuer(tabKey, nr) : document.getElementById("fertig-" + tabKey);
    if (el) setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
  }

  // ─── Aktionen ─────────────────────────────────────────────────────────
  BIE.actions["schritt-weiter"] = el => {
    const nr = el.dataset.nr; bestaetigt.add(nr); uebersprungen.delete(nr);
    const tabKey = tabVon[nr]; aktualisieren(tabKey); dirty(); zurAktuellen(tabKey);
  };
  BIE.actions["schritt-spaeter"] = el => {
    const nr = el.dataset.nr; uebersprungen.add(nr);
    const tabKey = tabVon[nr]; aktualisieren(tabKey); dirty(); showToast("⏭ Übersprungen – du kannst die Aufgabe später nachholen.", "#d97706"); zurAktuellen(tabKey);
  };
  BIE.actions["schritt-toggle"] = el => {
    const nr = el.dataset.nr; const tabKey = tabVon[nr];
    const box = elementFuer(tabKey, nr); if (!box) return;
    box.classList.toggle("is-open");
    toggleRendern(tabKey, nr, box, true);
    if (box.classList.contains("is-open")) { const ch = state.charts[nr]; if (ch) { try { ch.resize(); } catch (e) { /* egal */ } } if (BIE.zeichnen && BIE.zeichnen.resizeAll) BIE.zeichnen.resizeAll(); }
  };

  // Nach dem Erledigen einer Station: Leiste zeigt „Weiter“, nichts springt automatisch.
  function nachAbschluss(nr) {
    const tabKey = tabVon[nr]; if (!tabKey) return;
    if (uebersprungen.has(nr)) { uebersprungen.delete(nr); bestaetigt.add(nr); }
    aktualisieren(tabKey);
  }

  function init() {
    alleAktualisieren();
    if (!tabFrei(state.activeTab)) BIE.showTab(erstesFreiesTab(), { silent: true });
  }

  BIE.autosave.register("schritte", () => ({ uebersprungen: Array.from(uebersprungen), bestaetigt: Array.from(bestaetigt) }), data => {
    uebersprungen.clear(); bestaetigt.clear();
    if (data && Array.isArray(data.uebersprungen)) data.uebersprungen.forEach(nr => uebersprungen.add(String(nr)));
    if (data && Array.isArray(data.bestaetigt)) data.bestaetigt.forEach(nr => bestaetigt.add(String(nr)));
    alleAktualisieren();
  }, 95);

  return { init, aktualisieren, alleAktualisieren, nachAbschluss, tabFrei, aktuelleStation, erstesFreiesTab, get uebersprungen() { return uebersprungen; }, get bestaetigt() { return bestaetigt; } };
})();
