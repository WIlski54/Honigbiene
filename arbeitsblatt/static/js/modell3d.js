/* 3D-Modell-Aufgaben: „erkunden“ und „modellfinden“ (Namensraum BIE.modell3d). Wird NACH film.js geladen.

   Das 3D-Modell der Honigbiene ist ein Eintrag in INHALTE.filme (art "modell3d") und läuft als iframe-Bühne des
   Film-Bausteins. Dieses Modul nutzt von film.js nur die öffentliche API (befehle, status, gesehen, besucht,
   beobachten) und lauscht selbst auf window „message“ (für {mw:"tipp"}). Protokoll: AB_KONZEPT.md, „Das 3D-Modell im AB“.

   Aufgabentyp „erkunden“ – das Modell frei erkunden
     { nr, typ: "erkunden", film: "biene3d", eyebrow, titel, auftrag, beobachtung: ["Frage 1", "Frage 2"],
       knopf?: "3D-Modell erkunden", ansichten?: [{ name: "gestalt", label: "Außenansicht" }, …] }
     Fortschrittsbalken = „gesehen“-Wert des Modells (je ein Drittel für Außenansicht, Situs, Explosion).
     Die Station ist bei ≥ 95 % erledigt. Optional niveaus: { A: {auftrag, beobachtung}, … }.

   Aufgabentyp „modellfinden“ – „Tippe im Modell auf …“ (Prüfung im Browser anhand der Meldung des Modells)
     { nr, typ: "modellfinden", film: "biene3d", eyebrow, titel,
       niveaus: { A: { auftrag, ziele: [{ teil: "kopf", frage, hinweis, ansicht?: "gestalt", blick?: "vorn" }, …] }, B: …, C: … } }
     Je Ziel schickt der Baustein „waehlen an“ (und vorher optional „ansicht“ und „blick“ – kleine Teile wie Rüssel
     und Stachel brauchen z. B. blick „vorn“) an das Modell. Das Modell meldet jeden
     Tipp als {mw:"tipp", teil, teile}; richtig ist, wenn teil gleich ziel.teil ist oder ziel.teil in teile steht.
     Je Ziel optional: `fokus: { teile: ["ruessel"], blick?: "vorn", abstand?: 2.5 }` – das Modell fährt vor dem Wählen an die Ankerregion der Teile
     (`abstand`: Zahl > 0, Kameraabstand beim Heranfahren – ohne Angabe gilt der Standard des Modells; nötig bei Fühler und Facettenauge, die sonst die Bühne füllen)
     (Befehl `fokus`, ohne etwas zu markieren: die Lösung bleibt geheim und Tippen bleibt möglich). Vor jedem Ziel geht `zurueck`
     voraus, damit Hervorhebungen und Schilder anderer Aufgaben nicht stehen bleiben.
       richtig  → nächstes Ziel mit Rückmeldung; nach dem letzten Ziel ist die Station erledigt
       falsch   → Hinweis auf ein sichtbares Merkmal (ziel.hinweis), die Lösung wird NICHT verraten
       2× falsch → Tipp: das gesuchte Teil wird im Modell hervorgehoben („hervorheben“)
       Tipp ins Leere (teil: null) zählt nicht als Fehlversuch.

     Bedienleiste des Modells: Sie verdeckt sonst etwa 38 % der Bühne. Kennt das Modell den Befehl `leiste` (Feld `leiste` in info/status), blendet der Baustein
     sie beim Start eines Ziels aus ({mw:"leiste", an:false}) und beim Ende der Station, beim „Noch einmal“ und beim Verlassen der Station wieder ein.
     Kennt das Modell den Befehl nicht, passiert nichts. */
BIE.modell3d = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, cfgOf, niveauOf, body, showFb, clearFb, markComplete, sendAntwort, dirty, aufgabenByNr } = BIE;
  const film = BIE.film;
  const PRUEF = !!BIE.pruefmodus;
  const SCHWELLE = 95;                    // % Erkundungsfortschritt → Station „erkunden“ erledigt
  const WARTE_MS = 4000;                  // so lange auf die erste Meldung des Modells warten

  if (!film) {   // ohne film.js gibt es keine Bühne – die Aufgaben zeigen dann nur einen Hinweis
    const fehlt = () => "<p class=\"muted\">⚠️ Der Film-Baustein (film.js) ist nicht geladen.</p>";
    return { render: fehlt, nachRender() {}, init() {} };
  }

  const ANSICHTEN = { gestalt: "Außenansicht", situs: "Innenleben (Situs)", explosion: "Explosion" };
  // Deutsche Namen der Teile (AB_KONZEPT.md) – für Rückmeldungen wie „Du hast auf den Hinterleib getippt“.
  const TEILNAMEN = {
    kopf: "den Kopf", brust: "die Brust", hinterleib: "den Hinterleib", fuehler: "einen Fühler", facettenauge: "ein Facettenauge",
    ruessel: "den Rüssel", fluegel: "einen Flügel", bein: "ein Bein", vorderbein: "ein Vorderbein", mittelbein: "ein Mittelbein",
    hinterbein: "ein Hinterbein", pollenkoerbchen: "ein Pollenkörbchen", honigmagen: "den Honigmagen", darm: "den Darm",
    herz: "das Herz", gehirn: "das Gehirn", flugmuskeln: "die Flugmuskeln", stachel: "den Stachel", luftsaecke: "die Luftsäcke",
  };
  const teilName = key => TEILNAMEN[key] || (key ? `„${key}“` : "");
  // Name ohne Artikel für Rückmeldungen im Nominativ („Richtig: Kopf!“)
  const teilKurz = key => (TEILNAMEN[key] || "").replace(/^(den|die|das|einen|eine|ein) /, "") || String(key || "");

  const alle = typ => INHALTE.tabs.flatMap(tab => tab.aufgaben).filter(a => a.typ === typ);
  const filmId = t => t.film || "biene3d";
  // Bedienleiste ein/aus – nur, wenn das Modell den Befehl kennt (Feld `leiste` in info oder status), sonst ignorieren
  const kenntLeiste = id => { const i = film.info && film.info(id), s = film.status && film.status(id); return !!((i && i.leiste !== undefined) || (s && s.leiste !== undefined)); };
  const leisteBefehle = (id, an) => (kenntLeiste(id) ? [{ mw: "leiste", an }] : []);
  const basisPfad = id => ((INHALTE.filme || {})[id] || { datei: "" }).datei.split("?")[0];
  const rahmen = () => $$("#film-rahmen iframe");
  const filmDesFensters = quelle => {
    const fr = rahmen().find(f => f.contentWindow === quelle);
    if (!fr) return null;
    const pfad = (fr.getAttribute("src") || "").split("?")[0];
    return Object.keys(INHALTE.filme || {}).find(id => basisPfad(id) === pfad) || null;
  };
  const beobachtungHTML = cfg => (cfg.beobachtung && cfg.beobachtung.length
    ? `<div class="film-beobachtung"><p class="eyebrow">👀 Achte beim Erkunden auf …</p><ol>${cfg.beobachtung.map(b => `<li>${esc(b)}</li>`).join("")}</ol></div>` : "");

  // ═══ erkunden ═══════════════════════════════════════════════════════════
  function renderErkunden(t) {
    const cfg = cfgOf(t) || t;
    state.runtime[t.nr] = { zuletzt: -1 };
    const ansichten = t.ansichten || Object.keys(ANSICHTEN).map(name => ({ name, label: ANSICHTEN[name] }));
    return `
      ${cfg.auftrag ? `<p class="task-question">${esc(cfg.auftrag)}</p>` : ""}
      ${beobachtungHTML(cfg)}
      <div class="film-fortschritt"><div class="film-balken"><i id="erkbalken-${t.nr}"></i></div><span id="erkproz-${t.nr}">0 %</span></div>
      <ul class="erk-ansichten" id="erkans-${t.nr}" aria-label="Ansichten des Modells">
        ${ansichten.map(a => `<li data-ansicht="${esc(a.name)}"><span class="erk-haken" aria-hidden="true">⬜</span>
          <button class="btn btn-quiet btn-sm" type="button" data-action="erk-ansicht" data-nr="${t.nr}" data-name="${esc(a.name)}">${esc(a.label)}</button></li>`).join("")}
      </ul>
      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="erk-oeffnen" data-nr="${t.nr}">🧊 ${esc(t.knopf || cfg.knopf || "3D-Modell erkunden")}</button>
      </div>
      <p class="hint">💡 Die Station ist erledigt, wenn du das Modell von außen, von innen und als Explosion angesehen hast. Drehen und Schieben geht mit dem Finger.</p>
      ${PRUEF ? `<p class="hint pruef-loesung">🔍 Prüfmodus: Die Station gilt bei ≥ ${SCHWELLE} % als erledigt – je ein Drittel für Außenansicht, Situs und Explosion. Die drei Knöpfe oben stellen die Ansichten ein.</p>` : ""}`;
  }

  function erkAktualisieren(t) {
    const rt = state.runtime[t.nr]; if (!rt) return;
    const id = filmId(t), p = Math.min(100, film.gesehen(id) || 0), besucht = film.besucht(id), geladen = !!film.status(id);
    if (rt.zuletzt !== p || rt.besucht !== besucht.length || rt.geladen !== geladen) {
      rt.zuletzt = p; rt.besucht = besucht.length; rt.geladen = geladen;
      const b = document.getElementById("erkbalken-" + t.nr), s = document.getElementById("erkproz-" + t.nr);
      if (b) b.style.width = p + "%";
      if (s) s.textContent = p >= SCHWELLE ? "✅ ganz erkundet" : (!geladen && p === 0 ? "Modell wird geladen …" : p + " %");   // vor der ersten Meldung des Modells keine falsche „0 %“
      $$(`#erkans-${t.nr} li`).forEach(li => {
        const da = besucht.includes(li.dataset.ansicht), h = $(".erk-haken", li);
        li.classList.toggle("erk-besucht", da); if (h) h.textContent = da ? "✅" : "⬜";
      });
    }
    if (p >= SCHWELLE && !state.completed.has(String(t.nr))) {
      if (!state.restoring) sendAntwort(t.nr, "erkunden", `Modell erkundet (${p} %) – Ansichten: ${besucht.join(", ") || "–"}`, true, t.titel);
      showFb(t.nr, "ok", "✅ Du hast das 3D-Modell ganz erkundet.");
      markComplete(t.nr);
    }
  }
  BIE.actions["erk-oeffnen"] = el => { const t = aufgabenByNr[el.dataset.nr]; film.befehle(filmId(t), []); };
  BIE.actions["erk-ansicht"] = el => { const t = aufgabenByNr[el.dataset.nr]; film.befehle(filmId(t), [{ mw: "ansicht", name: el.dataset.name }]); };

  // ═══ modellfinden ═══════════════════════════════════════════════════════
  let aktiv = null;   // { nr, film } – die Aufgabe, die gerade auf Tipps aus dem Modell wartet

  const zieleVon = t => (cfgOf(t) || {}).ziele || [];

  function renderFinden(t) {
    const cfg = cfgOf(t) || {};
    if (aktiv && aktiv.nr === String(t.nr)) beenden(t);        // altes Niveau/Neustart: Wählmodus im Modell beenden
    state.runtime[t.nr] = { index: 0, fehler: 0, versuche: 0, fertig: false, gestartet: false, hervorgehoben: false, wartet: false };
    return `
      ${cfg.auftrag ? `<p class="task-question">${esc(cfg.auftrag)}</p>` : ""}
      <div class="mf-fortschritt" id="mfprog-${t.nr}" role="status"></div>
      <div class="mf-ziel" id="mfziel-${t.nr}"></div>
      <div class="btn-row" id="mfknoepfe-${t.nr}"></div>
      ${PRUEF ? `<div class="pruef-loesung mf-loesung">🔍 <strong>Prüfmodus – Ziele und Lösung:</strong><ol id="mfloesung-${t.nr}"></ol></div>` : ""}`;
  }

  function mfZeichnen(nr) {
    const t = aufgabenByNr[nr], rt = state.runtime[nr], ziele = zieleVon(t);
    const prog = document.getElementById("mfprog-" + nr), zielBox = document.getElementById("mfziel-" + nr), knoepfe = document.getElementById("mfknoepfe-" + nr);
    if (!rt || !prog || !zielBox || !knoepfe) return;
    const n = ziele.length;
    prog.innerHTML = n
      ? `${rt.fertig ? `Alle ${n} Ziele gefunden` : `Ziel ${Math.min(rt.index + 1, n)} von ${n}`} <span class="lese-dots" aria-hidden="true">${ziele.map((_, i) => `<i class="${i < rt.index || rt.fertig ? "done" : i === rt.index ? "now" : ""}"></i>`).join("")}</span>`
      : "Für dieses Niveau sind keine Ziele eingetragen.";
    if (rt.fertig) {
      zielBox.innerHTML = "";
      knoepfe.innerHTML = `<button class="btn btn-quiet" type="button" data-action="mf-reset" data-nr="${nr}">🔄 Noch einmal</button>`;
    } else if (n) {
      const z = ziele[rt.index];
      zielBox.innerHTML = `<p class="task-question">🎯 ${esc(z.frage)}</p>${rt.gestartet ? "" : "<p class=\"hint\">Tippe auf „Los“. Dann tippst du im 3D-Modell das gesuchte Teil an.</p>"}`;
      knoepfe.innerHTML = rt.gestartet
        ? `<button class="btn btn-primary" type="button" data-action="mf-modell" data-nr="${nr}">🧊 Zum Modell</button>`
        : `<button class="btn btn-primary" type="button" data-action="mf-start" data-nr="${nr}">▶ ${rt.index || rt.versuche ? "Weiter im Modell" : "Los: im Modell antippen"}</button>`;
    }
    const l = document.getElementById("mfloesung-" + nr);
    if (l) {
      l.innerHTML = ziele.map((z, i) => `<li>${esc(z.frage)} <strong>→ ${esc(z.teil)}</strong>${z.ansicht ? ` <small>(Ansicht: ${esc(z.ansicht)})</small>` : ""}
        <button class="btn btn-quiet btn-sm" type="button" data-action="mf-zeigen" data-nr="${nr}" data-i="${i}">🧊 Im Modell zeigen</button>
        ${z.hinweis ? `<br><small>Hinweis bei Fehler: ${esc(z.hinweis)}</small>` : ""}</li>`).join("");
    }
  }

  function zielStarten(t) {
    const rt = state.runtime[t.nr], z = zieleVon(t)[rt.index]; if (!z) return;
    aktiv = { nr: String(t.nr), film: filmId(t) };
    // „zurueck“ zuerst: setzt Ansicht, Hervorhebung, Schilder und Kamera zurück (Reste anderer Aufgaben und des letzten Ziels)
    const cmds = [{ mw: "zurueck" }, ...leisteBefehle(filmId(t), false)];   // die Bedienleiste verdeckt die Bühne, solange ein Ziel gesucht wird
    rt.hervorgehoben = false;
    if (z.ansicht) cmds.push({ mw: "ansicht", name: z.ansicht });
    if (z.blick) cmds.push({ mw: "blick", name: z.blick });
    if (z.fokus && Array.isArray(z.fokus.teile) && z.fokus.teile.length) {
      cmds.push(Object.assign({ mw: "fokus", teile: z.fokus.teile.slice() }, z.fokus.blick ? { blick: z.fokus.blick } : {},
        typeof z.fokus.abstand === "number" && Number.isFinite(z.fokus.abstand) && z.fokus.abstand > 0 ? { abstand: z.fokus.abstand } : {}));
    }
    cmds.push({ mw: "waehlen", an: true });
    film.befehle(filmId(t), cmds);
    // Antwortet das Modell nicht (Datei fehlt, noch nicht geladen), bleibt die Aufgabe bedienbar und sagt es offen.
    if (!film.status(filmId(t))) {
      rt.wartet = true;
      setTimeout(() => {
        if (rt.wartet && !film.status(filmId(t))) {
          showFb(t.nr, "err", "⚠️ Das 3D-Modell antwortet nicht. Warte einen Moment und tippe noch einmal auf „Zum Modell“ – oder lade die Seite neu und sag deiner Lehrkraft Bescheid.");
        }
      }, WARTE_MS);
    }
    mfZeichnen(t.nr);
  }
  function beenden(t) {
    const rt = state.runtime[t.nr];
    const cmds = [{ mw: "waehlen", an: false }, ...leisteBefehle(filmId(t), true)];
    if (rt && rt.hervorgehoben) { cmds.unshift({ mw: "hervorheben", teile: [] }); rt.hervorgehoben = false; }
    film.befehle(filmId(t), cmds);
    if (aktiv && aktiv.nr === String(t.nr)) aktiv = null;
  }

  BIE.actions["mf-start"] = el => {
    const t = aufgabenByNr[el.dataset.nr], rt = state.runtime[t.nr]; if (!rt) return;
    rt.gestartet = true; clearFb(t.nr); zielStarten(t); dirty();
  };
  BIE.actions["mf-modell"] = el => { const t = aufgabenByNr[el.dataset.nr]; clearFb(t.nr); zielStarten(t); };
  BIE.actions["mf-reset"] = el => { const t = aufgabenByNr[el.dataset.nr]; if (aktiv && aktiv.nr === String(t.nr)) beenden(t); BIE.aufgaben.renderBody(t); dirty(); };
  BIE.actions["mf-zeigen"] = el => {   // nur im Prüfmodus: Ziel im Modell zeigen
    const t = aufgabenByNr[el.dataset.nr], z = zieleVon(t)[parseInt(el.dataset.i, 10)]; if (!z) return;
    film.befehle(filmId(t), [{ mw: "ansicht", name: z.ansicht || "gestalt" }, { mw: "hervorheben", teile: [z.teil], fokus: true }]);
  };

  function tippAuswerten(t, d) {
    const rt = state.runtime[t.nr], ziele = zieleVon(t), z = ziele[rt && rt.index];
    if (!rt || !z || rt.fertig || !rt.gestartet) return;
    const teile = Array.isArray(d.teile) ? d.teile : [];
    const getippt = d.teil || teile[0] || null;
    if (!getippt) { showFb(t.nr, "info", "👆 Tippe direkt auf das Modell, nicht daneben."); return; }   // zählt nicht als Fehlversuch
    const treffer = d.teil === z.teil || teile.includes(z.teil);
    rt.versuche++;
    if (treffer) {
      sendAntwort(t.nr, "modellfinden", `Ziel ${rt.index + 1}/${ziele.length} „${z.teil}“: richtig${rt.fehler ? ` nach ${rt.fehler + 1} Versuchen` : " im ersten Versuch"}`, true, z.frage);
      rt.index++; rt.fehler = 0;
      if (rt.index >= ziele.length) {
        rt.fertig = true;
        const cmds = [];
        if (rt.hervorgehoben) { cmds.push({ mw: "hervorheben", teile: [] }); rt.hervorgehoben = false; }
        cmds.push({ mw: "waehlen", an: false }, ...leisteBefehle(filmId(t), true));
        film.befehle(filmId(t), cmds);
        aktiv = null;
        mfZeichnen(t.nr);
        showFb(t.nr, "ok", `✅ Richtig! Du hast alle ${ziele.length} Teile gefunden.`);
        markComplete(t.nr);
      } else {
        zielStarten(t);   // löscht eine Hervorhebung, stellt die Ansicht des nächsten Ziels ein und schaltet den Wählmodus an
        showFb(t.nr, "ok", `✅ Richtig: ${esc(teilKurz(z.teil))}! Weiter mit dem nächsten Ziel.`);
      }
    } else {
      rt.fehler++;
      sendAntwort(t.nr, "modellfinden", `Ziel ${rt.index + 1}/${ziele.length} „${z.teil}“: getippt „${getippt}“`, false, z.frage);
      let html = `❌ Das ist nicht das gesuchte Teil. Du hast auf ${esc(teilName(getippt))} getippt.`;
      html += `<br>💡 ${esc(z.hinweis || "Schau noch einmal genau hin.")}`;
      if (rt.fehler >= 2) {
        rt.hervorgehoben = true;
        film.befehle(filmId(t), [{ mw: "hervorheben", teile: [z.teil], fokus: true }]);
        html += "<br>🔦 Tipp: Das gesuchte Teil leuchtet jetzt im Modell. Tippe es an.";
      }
      showFb(t.nr, "err", html);
    }
    dirty();
  }

  window.addEventListener("message", e => {
    const d = e.data;
    if (!d || d.mw !== "tipp" || !aktiv) return;
    const id = filmDesFensters(e.source);
    if (!id || id !== aktiv.film) return;
    const t = aufgabenByNr[aktiv.nr];
    if (t && t.typ === "modellfinden") tippAuswerten(t, d);
  });

  // ═══ gemeinsam ══════════════════════════════════════════════════════════
  const render = t => (t.typ === "erkunden" ? renderErkunden(t) : renderFinden(t));

  // Aufruf aus aufgaben.js am Ende von renderBody(t)
  function nachRender(t) {
    if (t.typ === "erkunden") erkAktualisieren(t);
    else if (t.typ === "modellfinden") mfZeichnen(t.nr);
  }

  // Jede Meldung des Modells: Balken der Erkunden-Aufgaben nachführen; ein verspätet antwortendes Modell
  // bekommt die Befehle des laufenden Ziels noch einmal.
  film.beobachten((id) => {
    alle("erkunden").filter(t => filmId(t) === id).forEach(erkAktualisieren);
    if (aktiv && aktiv.film === id) {
      const t = aufgabenByNr[aktiv.nr], rt = t && state.runtime[t.nr];
      if (rt && rt.wartet) { rt.wartet = false; clearFb(t.nr); zielStarten(t); }
    }
  });

  // Verlässt das Kind die Station mitten in einem Ziel („Später machen“, Weiter): Wählmodus aus, Bedienleiste wieder an
  if (film.stationHoerer) film.stationHoerer.push((tabKey, nr) => {
    if (!aktiv || aktiv.nr === String(nr)) return;
    const t = aufgabenByNr[aktiv.nr], rt = t && state.runtime[t.nr];
    if (!t) return;
    beenden(t);
    if (rt) { rt.gestartet = false; mfZeichnen(t.nr); }
  });

  // Zustand im Autosave (eigener Eintrag, nach „aufgaben“ und „filme“)
  BIE.autosave.register("modell3d", () => {
    const out = {};
    alle("modellfinden").forEach(t => {
      const rt = state.runtime[t.nr];
      if (rt && (rt.index || rt.fehler || rt.versuche || rt.fertig)) out[t.nr] = { typ: "modellfinden", index: rt.index, fehler: rt.fehler, versuche: rt.versuche, fertig: !!rt.fertig };
    });
    return Object.keys(out).length ? out : undefined;
  }, data => {
    alle("erkunden").forEach(erkAktualisieren);
    Object.entries(data || {}).forEach(([nr, d]) => {
      const t = aufgabenByNr[nr], rt = state.runtime[nr];
      if (!t || t.typ !== "modellfinden" || !rt || !d) return;
      const n = zieleVon(t).length;
      rt.index = Math.max(0, Math.min(Number.isInteger(d.index) ? d.index : 0, n));
      rt.fehler = Number.isInteger(d.fehler) ? d.fehler : 0;
      rt.versuche = Number.isInteger(d.versuche) ? d.versuche : 0;
      rt.fertig = n > 0 && rt.index >= n;
      rt.gestartet = false;   // der Wählmodus im Modell wird erst nach „Weiter im Modell“ wieder eingeschaltet
      mfZeichnen(nr);
    });
  }, 31);

  function init() { alle("erkunden").forEach(erkAktualisieren); }

  return { init, render, nachRender };
})();
