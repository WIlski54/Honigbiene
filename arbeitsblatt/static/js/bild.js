/* Bildvergrößerung: Tippen auf ein Schaubild (Lesestrecke, Glossar) öffnet es bildschirmfüllend.
   Auf dem iPad sind die Schaubilder neben dem Text sonst zu klein. Schließen per Knopf, Escape
   oder Tipp auf den dunklen Rand; der Fokus kehrt zum Auslöser zurück. */
BIE.bild = (() => {
  "use strict";
  const { $ } = BIE;
  let letzterAusloeser = null;

  function offen() { const d = $("#bild-dialog"); return d && !d.hidden; }

  function oeffnen(src, alt, ausloeser) {
    if (!src) return;
    letzterAusloeser = ausloeser || null;
    const img = $("#bild-gross");
    img.src = src; img.alt = alt || "Schaubild";
    $("#bild-caption").textContent = alt || "";
    $("#bild-dialog").hidden = false;
    document.body.classList.add("no-scroll");
    setTimeout(() => $("#bild-close").focus(), 30);
  }
  function schliessen() {
    if (!offen()) return;
    $("#bild-dialog").hidden = true;
    $("#bild-gross").removeAttribute("src");
    document.body.classList.remove("no-scroll");
    if (letzterAusloeser && letzterAusloeser.focus) letzterAusloeser.focus();
  }

  BIE.actions["bild-open"] = el => { const img = el.querySelector("img"); if (img) oeffnen(img.currentSrc || img.src, img.alt, el); };
  BIE.actions["bild-close"] = schliessen;
  // Escape schließt zuerst die Vergrößerung, nicht das darunterliegende Glossar-Fenster.
  document.addEventListener("keydown", e => { if (e.key === "Escape" && offen()) { e.stopImmediatePropagation(); schliessen(); } }, true);
  document.addEventListener("click", e => { if (e.target.id === "bild-dialog") schliessen(); });

  return { oeffnen, schliessen, offen };
})();
