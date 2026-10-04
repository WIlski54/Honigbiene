/* Warteseite der Fortsetzungsstunde – pollt, bis die Lehrkraft zugeordnet hat. */
(() => {
  "use strict";
  const W = window.WARTEN || {};
  const $ = s => document.querySelector(s);
  const KEY = (W.appId || "gsm") + ":lernplatz";
  let gespeichert = {};
  try { gespeichert = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { gespeichert = {}; }
  const schuelerId = W.schuelerId || gespeichert.schueler_id || "";
  const token = W.resumeToken || gespeichert.token || "";
  if (W.schuelerId && W.resumeToken) {
    try { localStorage.setItem(KEY, JSON.stringify({ schueler_id: W.schuelerId, token: W.resumeToken, pseudonym: gespeichert.pseudonym || "" })); } catch (e) { /* privater Modus */ }
  }

  function setText(text, fertig) {
    $("#warten-text").textContent = text;
    if (fertig) { const sp = $("#warten-status .spinner"); if (sp) sp.hidden = true; }
  }

  async function pruefen() {
    try {
      const res = await fetch("/api/fortsetzung/status", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ schueler_id: schuelerId, token }) });
      const d = await res.json();
      if (d.redirect) {
        if (d.schueler_id) { try { localStorage.setItem(KEY, JSON.stringify({ schueler_id: d.schueler_id, token, pseudonym: gespeichert.pseudonym || "" })); } catch (e) { /* egal */ } }
        setText("Zugeordnet – dein Arbeitsblatt wird geöffnet …", true);
        setTimeout(() => { location.href = d.redirect; }, 600);
        return;
      }
      if (d.status === "abgelehnt") { setText("Deine Lehrkraft hat die Zuordnung abgelehnt. Bitte sprich sie an oder melde dich neu an.", true); return; }
      if (d.status === "inaktiv") { setText("Die Fortsetzungsstunde ist noch nicht gestartet. Diese Seite prüft alle paar Sekunden, ob es losgeht.", false); }
      else if (d.status === "unbekannt") { setText("Kein Arbeitsstand gefunden. Du kannst dich neu anmelden.", true); return; }
      else { setText("Dein Pseudonym passt nicht eindeutig zu einem alten Arbeitsstand. Deine Lehrkraft ordnet ihn dir gleich zu …", false); }
    } catch (e) {
      setText("Keine Verbindung zum Server – es wird weiter versucht.", false);
    }
    setTimeout(pruefen, 3000);
  }
  pruefen();
})();
