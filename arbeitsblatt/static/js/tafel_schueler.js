/* Tafel auf der Schülerseite: Overlay (übernimmt den Bildschirm, solange die Tafel live ist),
   Knopf „🙋 vorstellen“ an jeder tafeltauglichen Aufgabe und Hinweis „Tafelbild der Stunde“.
   Anmeldung läuft über das Session-Cookie dieses ABs. */
(function () {
  "use strict";
  if (!window.APP || APP.pruefmodus || !window.GT || !GT.TafelApp) return;
  GT.authKopf = () => ({});
  GT.socketAuth = () => ({});
  GT.abmelden = () => {};
  GT.ich = { id: APP.schuelerId, name: APP.pseudonym };

  const overlay = document.getElementById("tafel-overlay");
  const app = (window.tafelApp = new GT.TafelApp(document.getElementById("tafel-flaeche"), { rolle: "schueler" }));
  let angebote = [];
  const toast = (text, farbe) => (window.BIE && BIE.showToast ? BIE.showToast(text, farbe) : GT.toast(text));

  function tafelbildHinweis(url) {
    let a = document.getElementById("tafelbild-link");
    if (!a) {
      a = document.createElement("a");
      a.id = "tafelbild-link";
      a.className = "tafelbild-link";
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "📋 Tafelbild der Stunde";
      document.body.appendChild(a);
    }
    a.href = url;
  }

  function knoepfe() {
    document.querySelectorAll(".task-card").forEach((karte) => {
      const nr = karte.dataset.nr;
      if (!GT.abAdapter || !GT.abAdapter.tafelTauglich(nr)) return;
      let b = karte.querySelector(".tafel-vorstellen");
      if (!b) {
        b = document.createElement("button");
        b.type = "button";
        b.className = "btn btn-quiet btn-sm tafel-vorstellen";
        b.dataset.action = "tafel-vorstellen";
        b.dataset.nr = nr;
        karte.querySelector(".task-header").appendChild(b);
      }
      const an = angebote.find((x) => String(x.aufgabe_id) === String(nr));
      b.textContent = an ? "✋ zurückziehen" : "🙋 vorstellen";
      b.title = an ? "Angebot zurückziehen" : "Ich möchte das an der Tafel vorstellen";
      b.classList.toggle("an", !!an);
    });
  }

  if (window.BIE && BIE.actions) {
    BIE.actions["tafel-vorstellen"] = async (el) => {
      const nr = el.dataset.nr;
      const an = angebote.find((x) => String(x.aufgabe_id) === String(nr));
      try {
        if (an) { await GT.api("DELETE", "/tafel/api/angebot/" + an.id); return; }
        const karte = GT.abAdapter.eigeneKarte(nr);
        if (!karte || !karte.bearbeitet) { toast("Bearbeite die Aufgabe zuerst.", "#d97706"); return; }
        await GT.api("POST", "/tafel/api/angebot", { aufgabe_id: nr, karte: GT.karteAus(karte) });
        toast("🙋 Deine Lehrkraft sieht, dass du Aufgabe " + ((window.INHALTE && window.INHALTE.anzeigeNr) ? window.INHALTE.anzeigeNr(nr) : nr) + " vorstellen möchtest.");
      } catch (e) { toast(e.message, "#dc2626"); }
    };
  }

  app.onSocket = (s) => {
    s.on("ab:angebote", (liste) => { angebote = liste; knoepfe(); });
    s.on("ab:tafelbild", (d) => { tafelbildHinweis(d.url); toast("📋 Das Tafelbild ist jetzt da (oben rechts)."); });
  };
  app.onZustand = (z) => {
    const zeigen = z.modus === "live";
    if (overlay.hidden === zeigen) {
      overlay.hidden = !zeigen;
      document.body.classList.toggle("tafel-aktiv", zeigen);
      if (zeigen) { if (document.activeElement) document.activeElement.blur(); setTimeout(() => app.buehne.anpassen(), 0); }
    }
  };
  app.starten();
  knoepfe();
  GT.api("GET", "/tafel/api/status").then((s) => {
    angebote = s.angebote || [];
    knoepfe();
    if (s.tafelbild_url) tafelbildHinweis(s.tafelbild_url);
  }).catch(() => {});
})();
