/* Anzeigenummern: Die Kinder sehen fortlaufende Nummern 1, 2, 3 … statt der internen Aufgabennummern.
   Regel (identisch zu config.ANZEIGE_NR im Server): Position der Aufgaben-Stationen OHNE Lesestrecken über alle Reiter in der
   Reihenfolge von INHALTE.tabs[].aufgaben (= STATIONEN in plan_<reiter>.py); die Transferaufgabe „T“ bekommt die letzte Nummer.
   Lesestrecken heißen „Lesestrecke 1–4“ (intern L1–L4). Intern bleiben nr/ids unverändert (Autosave, Datenbank, Tests).
   Dieses Skript braucht KEIN BIE: es läuft auch auf den Tafel-Seiten (nur INHALTE + tafel_adapter.js). Laden NACH allen
   inhalte_*.js, VOR kern.js / tafel_adapter.js.
   Schnittstelle: INHALTE.anzeigeNr(nr) → "7" | "L3" (Lesestrecke unverändert) | unbekannt: unverändert
                  INHALTE.anzeigeLabel(nr) → "Aufgabe 7" | "Lesestrecke 3"
                  INHALTE.anzeigeKarte() → { "41": 1, "42": 2, …, "T": 48 }   (nur Aufgaben) */
(function () {
  "use strict";
  const I = window.INHALTE;
  if (!I) return;
  let karte = null, gebautFuer = -1;
  const istLese = (s) => /^L\d+$/.test(s);
  const schluessel = (nr) => String(nr === undefined || nr === null ? "" : nr).trim().toUpperCase();

  function bauen() {
    const reihe = [];
    (I.tabs || []).forEach((tab) => (tab.aufgaben || []).forEach((a) => { const s = schluessel(a.nr); if (s && !istLese(s)) reihe.push(s); }));
    const t = reihe.indexOf("T");
    if (t >= 0) { reihe.splice(t, 1); reihe.push("T"); }
    const k = {};
    reihe.forEach((s, i) => { k[s] = i + 1; });
    return k;
  }
  function anzeigeKarte() {
    // Die Inhaltsdateien hängen ihre Reiter nacheinander an – bei geänderter Reiterzahl neu aufbauen.
    const marke = (I.tabs || []).reduce((n, tab) => n + (tab.aufgaben || []).length + 1, 0);
    if (!karte || marke !== gebautFuer) { karte = bauen(); gebautFuer = marke; }
    return karte;
  }
  function anzeigeNr(nr) {
    const s = schluessel(nr);
    if (istLese(s)) return s;
    const k = anzeigeKarte();
    return Object.prototype.hasOwnProperty.call(k, s) ? String(k[s]) : String(nr);
  }
  function anzeigeLabel(nr) {
    const s = schluessel(nr);
    return istLese(s) ? `Lesestrecke ${s.slice(1)}` : `Aufgabe ${anzeigeNr(nr)}`;
  }
  I.anzeigeKarte = anzeigeKarte;
  I.anzeigeNr = anzeigeNr;
  I.anzeigeLabel = anzeigeLabel;
})();
