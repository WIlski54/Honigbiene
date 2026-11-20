/* Wischbahn unter dem 3D-Modell (Namensraum BIE.wischbahn). Wird NACH film.js und modell3d.js geladen.

   Auf dem iPad sollen die Kinder die Biene selbst öffnen: Ein Finger wischt auf der breiten Bahn unter dem Modell nach
   rechts – die Biene öffnet sich stufenlos von außen über das Innenleben (Situs) bis zur Explosion; nach links schließt
   sie sich wieder. Ein Tipp auf die Bahn springt an diese Stelle. Tastatur: Pfeile (5 %), Bild auf/ab (25 %), Pos1/Ende.

   Die Bahn sendet {mw:"ansicht", wert:0…1} an das Modell (film.js → senden, höchstens ein Befehl pro Bildschirmbild).
   Bewegt sich das Modell anders (Knopf in einer Aufgabe, Regler im Modell, zwei Finger im Modell), folgt der Griff der
   Statusmeldung (`fortschritt`). Direkt nach dem Wischen wartet er kurz, damit er nicht hinter der Feder herhinkt.
   Sichtbar ist die Bahn nur, wenn die Bühne ein Modell zeigt (Klasse `ist-modell`, film.js Ergänzung j) und nicht eingeklappt ist.
   Gespeichert wird nichts: Was die Kinder gesehen haben, zählt das Modell selbst (`gesehen`, Station „erkunden“). */
BIE.wischbahn = (() => {
  "use strict";
  const film = BIE.film;
  if (!film || !film.senden) return { wertAus: () => 0 };

  const RAND = 28;                 // halbe Griffbreite: So weit bleibt der Griffmittelpunkt vom Rand der Bahn weg
  const RUHE_MS = 1200;            // so lange nach dem Wischen keine Statusmeldung auf den Griff übertragen
  const MARKEN = [{ wert: 0, text: "Außen" }, { wert: 0.55, text: "Innen" }, { wert: 1, text: "Explosion" }];
  const klemmen = w => Math.max(0, Math.min(1, w));
  const ansichtText = w => (w < 0.08 ? "Außenansicht" : w < 0.46 ? "Die Hülle öffnet sich" : w < 0.64 ? "Innenleben (Situs)" : w < 0.96 ? "Die Teile lösen sich" : "Explosion");

  // Fingerposition → Öffnung 0…1 (reine Rechnung, auch für Tests)
  function wertAus(clientX, links, breite, rand = RAND) {
    const nutzbar = breite - 2 * rand;
    return nutzbar > 0 ? klemmen((clientX - links - rand) / nutzbar) : 0;
  }

  const modellId = () => {
    const a = film.aktiv && film.aktiv();
    const filme = (BIE.INHALTE && BIE.INHALTE.filme) || {};
    if (a && filme[a] && filme[a].art === "modell3d") return a;
    return Object.keys(filme).find(id => filme[id].art === "modell3d") || null;
  };

  let el = null, bahn = null, wert = 0, ziehen = false, zeiger = null, geplant = 0, zuletztSelbst = 0;

  function zeigen(w) {
    wert = klemmen(w);
    bahn.style.setProperty("--wert", wert.toFixed(4));
    bahn.setAttribute("aria-valuenow", String(Math.round(wert * 100)));
    bahn.setAttribute("aria-valuetext", `${Math.round(wert * 100)} Prozent geöffnet – ${ansichtText(wert)}`);
    el.classList.toggle("ist-offen", wert > 0.96);
  }
  function senden() {
    if (geplant) return;
    geplant = requestAnimationFrame(() => {
      geplant = 0;
      const id = modellId();
      if (id) film.senden(id, { mw: "ansicht", wert: Number(wert.toFixed(3)) });
    });
  }
  function setzen(w) { zuletztSelbst = Date.now(); zeigen(w); senden(); }

  function anbringen() {
    if (el) return true;
    const buehne = document.getElementById("filmbuehne"), rahmen = document.getElementById("film-rahmen");
    if (!buehne || !rahmen) return false;
    el = document.createElement("div");
    el.className = "wischbahn"; el.id = "wischbahn";
    el.innerHTML = `
      <p class="wb-hinweis"><span aria-hidden="true">👆</span> Wische nach rechts: Die Biene öffnet sich. Nach links: Sie schließt sich.</p>
      <div class="wb-bahn" role="slider" tabindex="0" aria-label="Biene öffnen und schließen" aria-valuemin="0" aria-valuemax="100">
        <span class="wb-fuellung" aria-hidden="true"></span>
        <span class="wb-pfeile" aria-hidden="true">› › ›</span>
        <span class="wb-griff" aria-hidden="true">🐝</span>
      </div>
      <div class="wb-marken" aria-hidden="true">${MARKEN.map(m => `<span style="--pos:${m.wert}">${m.text}</span>`).join("")}</div>`;
    rahmen.after(el);
    bahn = el.querySelector(".wb-bahn");
    bahn.style.setProperty("--rand", RAND + "px");
    zeigen(0);

    const ausZeiger = e => { const r = bahn.getBoundingClientRect(); return wertAus(e.clientX, r.left, r.width); };
    bahn.addEventListener("pointerdown", e => {
      if (e.button > 0 || ziehen) return;
      ziehen = true; zeiger = e.pointerId;
      try { bahn.setPointerCapture(e.pointerId); } catch (err) { /* ältere Browser */ }
      el.classList.add("zieht");
      setzen(ausZeiger(e));
      e.preventDefault();
    });
    bahn.addEventListener("pointermove", e => { if (ziehen && e.pointerId === zeiger) setzen(ausZeiger(e)); });
    const ende = e => {
      if (!ziehen || e.pointerId !== zeiger) return;
      ziehen = false; zeiger = null; zuletztSelbst = Date.now();
      el.classList.remove("zieht");
    };
    bahn.addEventListener("pointerup", ende);
    bahn.addEventListener("pointercancel", ende);
    bahn.addEventListener("lostpointercapture", ende);
    bahn.addEventListener("keydown", e => {
      const schritt = { ArrowRight: 0.05, ArrowUp: 0.05, ArrowLeft: -0.05, ArrowDown: -0.05, PageUp: 0.25, PageDown: -0.25 }[e.key];
      if (schritt !== undefined) setzen(wert + schritt);
      else if (e.key === "Home") setzen(0);
      else if (e.key === "End") setzen(1);
      else return;
      e.preventDefault();
    });
    return true;
  }

  film.beobachten((id, d) => {
    if (!anbringen() || id !== modellId() || ziehen || Date.now() - zuletztSelbst < RUHE_MS) return;
    if (d && typeof d.fortschritt === "number") zeigen(d.fortschritt);
  });
  window.addEventListener("DOMContentLoaded", anbringen);

  return { wertAus, anbringen, wert: () => wert };
})();
