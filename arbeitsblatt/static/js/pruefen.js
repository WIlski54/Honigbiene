/* Prüfmodus für die Lehrkraft (/lehrer/pruefen): alle Reiter frei, alle Stationen offen,
   Lesestrecken mit markierter Lösung, ein Niveau-Schalter für alle Aufgaben.
   Es wird nichts gespeichert – Schüler-APIs werden in kern.js abgefangen. */
BIE.pruefen = (() => {
  "use strict";
  if (!BIE.pruefmodus) return { aktiv: false, init() {} };
  const { $$, state, aufgabenByNr, showToast } = BIE;

  function alleNiveaus(n) {
    Object.values(aufgabenByNr).forEach(t => {
      if (!t.niveaus) return;
      state.niveau[t.nr] = n;
      const c = BIE.card(t.nr); if (c) c.dataset.niveau = n;
    });
    $$(".niveau-select").forEach(s => { s.value = n; });
    Object.values(aufgabenByNr).forEach(t => { if (t.niveaus) BIE.aufgaben.renderBody(t); });
    $$("[data-action='pruef-niveau']").forEach(b => b.classList.toggle("is-active", b.dataset.niveau === n));
    showToast(`Alle Aufgaben zeigen jetzt Niveau ${n}.`, "#006AB3");
  }
  BIE.actions["pruef-niveau"] = el => alleNiveaus(el.dataset.niveau);

  function init() {
    $$("details").forEach(d => { d.open = true; });   // Material, Hinweise, Quellen: alles aufgeklappt
    document.title = "Prüfmodus · " + document.title;
  }

  return { aktiv: true, init, alleNiveaus };
})();
