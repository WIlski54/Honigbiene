/* Präsentationsmodus: Die Lehrkraft blendet allen dasselbe Bild ein.

   Das Overlay liegt über allem und lässt sich von Lernenden nicht schließen.
   Damit es niemanden auslässt, kommt der Zustand auf drei Wegen an:
     1. Socket-Ereignis „praesentation“ – sofort, für alle Verbundenen
     2. /api/status – beim Anmelden und bei jedem Neuladen
     3. /api/praesentation – regelmäßige Sicherheitsabfrage, falls die Verbindung
        zwischendurch weg war und das Ereignis verloren ging

   Der Autosave läuft weiter: Eingetipptes darf nicht verloren gehen. Die
   Arbeits-Endpunkte sperrt zusätzlich der Server (praesentation_frei in app.py).
*/
BIE.praesentation = (() => {
  "use strict";
  const { $, esc, getJSON, on } = BIE;
  const ABFRAGE_MS = 20000;

  let zustand = { active: false };
  let timer = null;
  let vorherFokus = null;

  function overlay() {
    let el = document.getElementById("praes-overlay");
    if (el) return el;
    el = document.createElement("div");
    el.id = "praes-overlay";
    el.className = "praes-overlay";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-modal", "true");
    el.setAttribute("aria-label", "Bild der Lehrkraft");
    el.hidden = true;
    document.body.appendChild(el);
    return el;
  }

  function zeichnen() {
    const el = overlay();
    if (!zustand.active) {
      if (!el.hidden) {
        el.hidden = true;
        el.innerHTML = "";
        document.body.classList.remove("praes-aktiv");
        if (vorherFokus && document.contains(vorherFokus)) { try { vorherFokus.focus(); } catch (e) { /* egal */ } }
        vorherFokus = null;
        BIE.showToast("▶️ Weiter geht's – du kannst wieder arbeiten.");
      }
      return;
    }
    const neu = el.hidden;
    el.innerHTML = `
      <div class="praes-inner">
        <p class="praes-kopf">👀 Schau auf das Bild</p>
        <figure class="praes-figur">
          <img src="${esc(zustand.bild)}" alt="${esc(zustand.alt || zustand.titel || "Bild der Lehrkraft")}">
          <figcaption>${esc(zustand.titel || "")}</figcaption>
        </figure>
        ${zustand.hinweis ? `<p class="praes-hinweis">${esc(zustand.hinweis)}</p>` : ""}
        <p class="praes-fuss">Deine Lehrkraft zeigt allen dasselbe Bild. Gleich geht es weiter.</p>
      </div>`;
    el.hidden = false;
    document.body.classList.add("praes-aktiv");
    if (neu) {
      vorherFokus = document.activeElement;
      // Tastaturfokus einfangen, damit nichts dahinter bedienbar bleibt.
      el.tabIndex = -1;
      try { el.focus(); } catch (e) { /* egal */ }
      BIE.showToast("👀 Deine Lehrkraft zeigt ein Bild.", "#AD007C");
    }
  }

  function fehltImDokument() {
    const el = document.getElementById("praes-overlay");
    return !el || el.hidden || !document.body.contains(el);
  }

  function setzen(neu) {
    const vorher = zustand.active, vorherBild = zustand.key;
    zustand = neu && neu.active ? neu : { active: false };
    // Auch neu zeichnen, wenn das Overlay aus dem Dokument verschwunden ist –
    // sonst bliebe ein entferntes Overlay entfernt, weil sich der Zustand ja nicht
    // geändert hat.
    if (zustand.active !== vorher || zustand.key !== vorherBild || (zustand.active && fehltImDokument())) zeichnen();
    takt();
  }

  // Wird das Overlay aus dem Dokument genommen, kommt es sofort zurück. Der
  // Beobachter sitzt nur auf den direkten Kindern von <body> – dort hängt das
  // Overlay –, damit er die App nicht bei jeder Änderung im Baum beschäftigt.
  if ("MutationObserver" in window) {
    new MutationObserver(() => { if (zustand.active && fehltImDokument()) zeichnen(); })
      .observe(document.body, { childList: true });
  }

  // Solange der Modus läuft, öfter nachsehen: Das Ende soll niemand verpassen.
  function takt() {
    clearInterval(timer);
    timer = setInterval(pruefen, zustand.active ? ABFRAGE_MS / 2 : ABFRAGE_MS);
  }

  async function pruefen() {
    if (document.visibilityState !== "visible") return;
    const r = await getJSON("/api/praesentation");
    if (r && r.ok && r.praesentation) setzen(r.praesentation);
  }

  // Fokus darf das Overlay nicht verlassen, solange es offen ist.
  document.addEventListener("focusin", e => {
    const el = document.getElementById("praes-overlay");
    if (!el || el.hidden || el.contains(e.target)) return;
    try { el.focus(); } catch (err) { /* egal */ }
  });
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") pruefen(); });

  function init(startZustand) {
    on("praesentation", setzen);
    if (BIE.socket) BIE.socket.on("connect", pruefen);
    setzen(startZustand);
  }

  return { init, setzen, pruefen, get aktiv() { return !!zustand.active; } };
})();
