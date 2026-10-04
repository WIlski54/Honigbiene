/* Film-Baustein: eine Modellwelt (Skill modellwelt-bauen), ein Papiertheater (papiertheater-bauen) oder eine Archiv-Doku
   (archiv-doku-bauen) im Arbeitsblatt.

   Einbindung und Datenformat: references/film.md. Hier mit Kürzel BIE (aus assets/film/film.js per sed erzeugt).

   ÄNDERUNGEN GEGENÜBER DEM SKILL-BAUSTEIN (Honigbienen-AB, 3. Oktober 2026) – bei einem Update des Bausteins erneut anbringen:
     (a) SYMBOL kennt die Art "modell3d" (🧊). Der Toast „Film vollständig gesehen …“ in freiGeworden() erscheint weiter
         nur für art "modellwelt" (das 3D-Modell meldet freigeschaltet: true von Anfang an, dort wäre er sinnlos).
     (b) standAnzeigen(): Meldet das iframe einen eigenen Statustext (d.standText, z. B. „Außenansicht“), steht dieser
         statt „Pause · 0:00 · gesehen N %“ in der Bühnenkopfzeile (das 3D-Modell hat keine Zeitleiste).
     (c) filmVonAufgabe(): Auch Aufgaben vom Typ "erkunden" und "modellfinden" (Modul modell3d.js) gehören zu ihrem Film
         (Feld film), damit die Bühne in ihrem Reiter erscheint, selbst wenn tab.film fehlt.
   Das Modul modell3d.js nutzt von hier nur die öffentliche API (befehle, status, gesehen, beobachten).

   ERGÄNZUNGEN (4. Oktober 2026, Audit „forschend-entwickelnd“, docs/AUDIT_FORSCHEN_2026-10-04.md T1, T6, T7) – bei einem Update des Bausteins erneut anbringen:
     (d) Film-Knöpfe (art papiertheater/archivdoku) SPIELEN SOFORT AB: Steht in `befehle` ein `kapitel` oder `springe` und kein `spielen`/`anhalten`,
         hängt befehleFuer() ein `spielen` an (Ausnahme: `spielen: false` am Knopf). Springen auf Sekunden: { mw: "springe", t: 90 }; die Beschriftung
         (`text`) nennt Stelle und Satz: „▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)“. Blockiert der Browser den Ton, steht „Tippe im Filmfenster auf ▶“.
     (e) BILD-KNOPF: { bild: "/static/img/lese/…", text, alt } ohne `film` öffnet das Bild im Bild-Fenster (bild.js) – für Stationen ohne Film/Modell.
         `modell` darf überall eine Liste von Knöpfen sein (Aufgabe, Zeile in protokoll/tabelle).
     (f) PFLICHT-SPERRE: Die Station wird erst frei, wenn ALLE `pflicht`-Knöpfe gedrückt wurden – bei Filmen zusätzlich mindestens MIN_SPIELZEIT
         Sekunden Wiedergabe nach dem Druck. Der Stand steht im Autosave (knoepfe[nr] = Liste der erfüllten Knöpfe; alt: true = alle).
     (g) Film-Karte (`film`): Balken und Prozent laufen mit jeder Statusmeldung mit, nicht erst am Ende.
     (h) stationHoerer: andere Module (modell3d.js) erfahren, wenn die Station wechselt.
     (i) ERSTER KLICK GEHT NICHT VERLOREN: Ein gerade erst erzeugter Film-iframe hat seinen Nachrichten-Hörer noch nicht. befehle() puffert deshalb alle
         Befehle, bis sich der Film zum ersten Mal gemeldet hat (info/status) – spätestens nach WARTE_AUF_FILM ms (Rückfall, falls er nie antwortet) –
         und sendet sie dann in der alten Reihenfolge. Danach geht alles direkt.

   Was der Baustein macht
     • Filmbühne: eine iframe-Bühne neben den Aufgaben (breit) bzw. darüber, klebend (iPad/Handy). Sie erscheint in jedem Reiter,
       der einen Film nutzt (tab.film, Aufgabe typ "film"/"filmmoment" oder ein Modell-Knopf). Ein iframe je Film, das nie
       umgehängt wird – so bleibt der Filmstand beim Reiterwechsel erhalten.
     • Status: Die Filme melden per postMessage, was läuft und wie viel vollständig angesehen wurde (Springen zählt nicht).
       Gespeichert wird: gesehen (%), frei (vollständig gesehen → Live-Perspektiven), besucht (Live-Perspektiven), gedrückte Knöpfe.
     • Aufgabentypen: "film" (Film ansehen, Station hakt sich bei ≥ 95 % ab) und "filmmoment" (Finde den Moment: selbst anhalten).
     • Modell-Knöpfe an JEDER Aufgabe (Feld modell): springen zu Zeitpunkt + Blickwinkel/Perspektive; mit pflicht: true bleibt die
       Aufgabe gesperrt, bis die Stelle im Film angesehen wurde (modellgebundene Aufgabe).
   Autoplay: Browser (v. a. iPad) erlauben das Starten mit Ton oft nur durch einen Tipp IM Film. Der Baustein versucht es und
   zeigt sonst „Tippe im Filmfenster auf ▶“. Springen und Anhalten klappen immer. */
BIE.film = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, cfgOf, niveauOf, body, card, showFb, clearFb, markComplete, sendAntwort, dirty, aufgabenByNr, tabByNr, showToast } = BIE;
  const PRUEF = !!BIE.pruefmodus;
  const FILME = INHALTE.filme || {};
  const SCHWELLE = 95;                         // % vollständig angesehen → Station erledigt

  const Z = { filme: {}, knoepfe: {} };        // gespeichert: filme[id] = {gesehen, frei, besucht}, knoepfe[nr] = [erfüllte Knopf-Nummern] (alt: true = alle)
  const lauf = {};                             // letzter Status je Film (nicht gespeichert)
  const info = {};                             // Kapitel, Blickwinkel, Perspektiven je Film (vom Film gemeldet)
  const hoerer = [];                           // fn(id, status)
  const iframes = {};
  let aktiv = null, buehne = null;
  const fz = id => Z.filme[id] || (Z.filme[id] = { gesehen: 0, frei: false, besucht: [] });
  const fmt = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
  const knoepfeVon = t => !t.modell ? [] : (Array.isArray(t.modell) ? t.modell : [t.modell]);
  const filmVonAufgabe = t => (t.typ === "film" || t.typ === "filmmoment" || t.typ === "erkunden" || t.typ === "modellfinden") ? t.film : (knoepfeVon(t).find(k => k && k.film) || {}).film;
  // Das 3D-Modell ist von Anfang an frei (es meldet freigeschaltet: true); nur Modellwelten/Filme mit Live-Perspektiven sperren
  const artVon = id => (FILME[id] || {}).art;
  const brauchtFrei = k => artVon(k.film) !== "modell3d" && (k.befehle || []).some(b => b.mw === "live" || b.mw === "ansicht");
  const SYMBOL = { modellwelt: "🧊", modell3d: "🧊", papiertheater: "🎭", archivdoku: "📜" };
  const symbol = id => SYMBOL[(FILME[id] || {}).art] || "🎬";
  const WARTE_AUF_FILM = 6000;                 // ms nach dem Laden des iframes, dann gilt der Film als bereit (auch ohne Meldung)
  const MIN_SPIELZEIT = 3;                     // Sekunden Wiedergabe nach dem Druck, damit ein Pflicht-Film-Knopf zählt
  const ZEITFILME = ["papiertheater", "archivdoku"];   // Filme mit Zeitachse: Knöpfe springen und spielen sofort
  const istBild = k => !!(k && k.bild && !k.film);     // Bild-Knopf: öffnet ein Bild im Bild-Fenster
  const knopfSymbol = k => (istBild(k) ? "🖼️" : symbol(k.film));
  const knopfText = k => k.text || (istBild(k) ? "Bild ansehen" : artVon(k.film) === "modell3d" ? "Im Modell ansehen" : "Im Film ansehen");
  // Beginnt die Beschriftung schon mit einem Symbol („▶ Hör zu: …“), kommt kein zweites davor (nicht „🎭 ▶ Hör zu“)
  const hatSymbol = text => /^\s*(?:\p{Extended_Pictographic}|[▶▷⏵⏯])/u.test(String(text || ""));
  const knopfBeschriftung = k => (hatSymbol(knopfText(k)) ? "" : knopfSymbol(k) + " ") + esc(knopfText(k));
  const bildQuelle = src => String(src) + (BIE.APP.assetVersion ? (String(src).includes("?") ? "&" : "?") + "v=" + BIE.APP.assetVersion : "");
  // Befehle eines Knopfes. Film mit Zeitachse: springen/Kapitel → danach sofort `spielen` (außer spielen: false oder der Knopf steuert selbst).
  function befehleFuer(k) {
    const liste = (k.befehle || []).slice();
    if (istBild(k) || k.spielen === false || !ZEITFILME.includes(artVon(k.film))) return liste;
    const springt = liste.some(b => b.mw === "kapitel" || b.mw === "springe"), steuert = liste.some(b => b.mw === "spielen" || b.mw === "anhalten");
    if ((springt || k.spielen === true) && !steuert) liste.push({ mw: "spielen" });
    return liste;
  }

  // ─── Bühne ─────────────────────────────────────────────────────────────
  function buehneAufbauen() {
    if (buehne) return buehne;
    const panels = document.getElementById("panels");
    const wrap = document.createElement("div");
    wrap.className = "film-layout";
    panels.parentNode.insertBefore(wrap, panels);
    buehne = document.createElement("aside");
    buehne.className = "filmbuehne"; buehne.id = "filmbuehne"; buehne.hidden = true;
    buehne.setAttribute("aria-label", "Film");
    buehne.innerHTML = `
      <div class="film-kopf">
        <span class="film-titel" id="film-titel"></span>
        <span class="film-stand" id="film-stand" aria-live="polite"></span>
        <button class="btn btn-quiet btn-sm film-klein" type="button" data-action="film-klein" aria-expanded="true" title="Film verkleinern">▾</button>
      </div>
      <div class="film-rahmen" id="film-rahmen"></div>`;
    wrap.append(panels, buehne);
    return buehne;
  }
  BIE.actions["film-klein"] = el => {
    const klein = buehne.classList.toggle("klein");
    el.textContent = klein ? `▸ ${artVon(aktiv) === "modell3d" ? "Modell" : "Film"} zeigen` : "▾"; el.setAttribute("aria-expanded", String(!klein));
  };
  // Auf schmalen Anzeigen (unter 1100 px) klebt die Bühne über den Aufgaben. In Stationen ohne Film-/Modell-Bindung steht sie
  // deshalb eingeklappt (die Kinder können sie jederzeit aufklappen); eine gebundene Station klappt sie auf und zeigt den
  // passenden Film. Gebunden = Typ film/filmmoment/erkunden/modellfinden, Aufgaben-Knopf `modell` oder ein Zeilen-/Zellen-Knopf.
  const schmal = () => window.innerWidth < 1100;
  const zeilenKnoepfe = t => ((t.typ === "protokoll" || t.typ === "tabelle") ? Object.values(t.niveaus || {}) : [])
    .flatMap(c => ((c && c.zeilen) || []).flatMap(z => (z && z.modell ? [].concat(z.modell) : [])).filter(Boolean));
  const stationFilm = t => filmVonAufgabe(t) || (zeilenKnoepfe(t).find(k => k && k.film) || {}).film || null;
  const stationHoerer = [];                      // fn(tabKey, nr) bei jedem Wechsel der Station (z. B. modell3d.js: Bedienleiste wieder einblenden)
  let letzteStation = "";
  function stationWechsel(tabKey, nr) {
    if (PRUEF || !buehne || tabKey !== state.activeTab) return;
    const marke = tabKey + ":" + nr;
    if (marke === letzteStation) return;           // nur beim Wechsel der Station: danach gilt, was das Kind eingestellt hat
    letzteStation = marke;
    stationHoerer.forEach(fn => { try { fn(tabKey, nr); } catch (err) { console.error(err); } });
    if (!schmal()) return;
    const t = nr ? aufgabenByNr[nr] : null, id = t ? stationFilm(t) : null;
    if (id && FILME[id]) zeige(id);
    const klein = buehne.classList.contains("klein");
    if (!!id === klein) BIE.actions["film-klein"]($(".film-klein", buehne));   // gebunden und eingeklappt → aufklappen; ungebunden und offen → einklappen
  }

  function iframeFuer(id) {
    if (iframes[id]) return iframes[id];
    const f = FILME[id];
    if (!f) { console.error("Film fehlt in INHALTE.filme:", id); return null; }
    const fr = document.createElement("iframe");
    fr.title = f.titel || "Film"; fr.allow = "fullscreen; autoplay"; fr.hidden = true;
    fr.src = f.datei + (BIE.APP.assetVersion ? (f.datei.includes("?") ? "&" : "?") + "v=" + BIE.APP.assetVersion : "");
    fr.addEventListener("load", () => {
      if (fz(id).frei || PRUEF) senden(id, { mw: "freischalten" });
      senden(id, { mw: "info" });
      setTimeout(() => kontakt(id), WARTE_AUF_FILM);   // Rückfall: Befehle nicht ewig zurückhalten
    });
    $("#film-rahmen").appendChild(fr);
    iframes[id] = fr;
    return fr;
  }

  function zeige(id) {
    buehneAufbauen();
    if (!id || !FILME[id]) { buehne.hidden = true; document.body.classList.remove("mit-film"); return; }
    if (aktiv && aktiv !== id) senden(aktiv, { mw: "anhalten" });
    iframeFuer(id);
    Object.entries(iframes).forEach(([k, fr]) => { fr.hidden = k !== id; });
    aktiv = id;
    buehne.hidden = false;
    document.body.classList.add("mit-film");
    $("#film-titel").textContent = symbol(id) + " " + (FILME[id].titel || "Film");
    standAnzeigen();
  }

  function filmFuerTab(key) {
    const tab = INHALTE.tabs.find(t => t.key === key);
    if (!tab) return null;
    if (tab.film) return tab.film;
    for (const a of tab.aufgaben) { const f = filmVonAufgabe(a); if (f) return f; }
    return null;
  }
  BIE.beimOeffnen["*"] = (function (vorher) {
    return key => { if (vorher) vorher(key); zeige(filmFuerTab(key)); if (BIE.schritte) stationWechsel(key, BIE.schritte.aktuelleStation(key)); };
  })(BIE.beimOeffnen["*"]);

  // ─── Nachrichten ───────────────────────────────────────────────────────
  function senden(id, befehl) { const fr = iframes[id]; if (fr && fr.contentWindow) fr.contentWindow.postMessage(befehl, "*"); }
  // Erster Kontakt: Ein Film-iframe nimmt Befehle erst an, wenn sein Skript läuft – eine Nachricht davor geht verloren (der erste Klick auf einen Film-Knopf nach
  // dem Laden). Bis zur ersten Meldung (info/status) werden die Befehle gepuffert und danach in der alten Reihenfolge gesendet.
  const bereit = {}, puffer = {};                // id → true / id → [{ fn(verzug), n }, …]  (n = Zahl der Befehle, bestimmt den Abstand zum nächsten Eintrag)
  function kontakt(id) {
    if (bereit[id]) return;
    bereit[id] = true;
    const wartende = puffer[id] || []; delete puffer[id];
    let verzug = 0;                              // mehrere gepufferte Klicks laufen nacheinander, nicht durcheinander
    wartende.forEach(w => { try { w.fn(verzug); } catch (err) { console.error(err); } verzug += w.n * 160; });
  }
  // Läuft fn erst `ms` nach dem tatsächlichen Senden (der Browser-Hinweis „Tippe im Filmfenster auf ▶“ darf nicht vor dem ersten Kontakt erscheinen)
  function nachSenden(id, ms, fn) {
    if (bereit[id]) setTimeout(fn, ms); else (puffer[id] = puffer[id] || []).push({ fn: verzug => setTimeout(fn, ms + verzug), n: 0 });
  }
  function befehle(id, liste) {
    zeige(id);
    if (buehne.classList.contains("klein")) BIE.actions["film-klein"]($(".film-klein", buehne));
    const alle = (verzug = 0) => (liste || []).forEach((b, i) => setTimeout(() => senden(id, b), 120 + verzug + i * 160));
    if (bereit[id]) alle(); else (puffer[id] = puffer[id] || []).push({ fn: alle, n: (liste || []).length });
    if (window.innerWidth < 1100) buehne.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  window.addEventListener("message", e => {
    const d = e.data;
    if (!d || (d.mw !== "status" && d.mw !== "info")) return;
    const id = Object.keys(iframes).find(k => iframes[k].contentWindow === e.source);
    if (!id) return;
    if (!bereit[id]) {                             // erste Meldung: der Film hört jetzt zu
      if (fz(id).frei || PRUEF) senden(id, { mw: "freischalten" });
      if (d.mw === "status") senden(id, { mw: "info" });
      kontakt(id);
    }
    if (d.mw === "info") { info[id] = d; return; }
    lauf[id] = d;
    spielzeitZaehlen(id, d);
    const z = fz(id), vorher = JSON.stringify(z);
    z.gesehen = Math.max(z.gesehen, d.gesehen || 0);
    if (d.freigeschaltet || z.gesehen >= SCHWELLE) z.frei = true;
    (d.besucht || []).forEach(b => { if (!z.besucht.includes(b)) z.besucht.push(b); });
    if (JSON.stringify(z) !== vorher) {
      dirty();
      if (!JSON.parse(vorher).frei && z.frei) { freiGeworden(id); }
    }
    if (id === aktiv) standAnzeigen();
    filmKartenNachfuehren(id);
    hoerer.forEach(fn => { try { fn(id, d); } catch (err) { console.error(err); } });
  });

  function standAnzeigen() {
    const el = $("#film-stand"); if (!el || !aktiv) return;
    const d = lauf[aktiv], z = fz(aktiv);
    if (!d) { el.textContent = ""; return; }
    if (d.standText) { el.textContent = d.standText; return; }   // z. B. 3D-Modell: „Außenansicht“
    const was = d.live ? `Live · ${d.ansichtLabel || d.ansicht}` : d.stopp ? "Quellen-Stopp" : d.laeuft ? "läuft" : "Pause";
    el.textContent = `${was} · ${fmt(d.t)} · gesehen ${z.gesehen} %`;
  }

  function freiGeworden(id) {
    if (FILME[id].art === "modellwelt") showToast("🎬 Film vollständig gesehen – die Live-Perspektiven sind jetzt frei!", "#006AB3");
    INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(t => {
      if (filmVonAufgabe(t) === id && body(t.nr)) { if (t.typ === "film") filmAufgabeAktualisieren(t); else if (knoepfeVon(t).some(brauchtFrei)) knoepfeZeichnen(t); }
    }));
    if (BIE.schritte && BIE.schritte.alleAktualisieren) BIE.schritte.alleAktualisieren();
  }

  // ─── Aufgabentyp „film“: Film ansehen ──────────────────────────────────
  function renderFilm(t) {
    const cfg = cfgOf(t) || t;
    state.runtime[t.nr] = {};
    return `
      ${cfg.auftrag ? `<p class="task-question">${esc(cfg.auftrag)}</p>` : ""}
      ${cfg.beobachtung && cfg.beobachtung.length ? `<div class="film-beobachtung"><p class="eyebrow">👀 Achte beim Ansehen auf …</p>
        <ol>${cfg.beobachtung.map(b => `<li>${esc(b)}</li>`).join("")}</ol></div>` : ""}
      <div class="film-fortschritt"><div class="film-balken"><i id="filmbalken-${t.nr}"></i></div><span id="filmproz-${t.nr}">0 %</span></div>
      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="film-spielen" data-nr="${t.nr}">▶ Film abspielen</button>
      </div>
      <p class="hint">💡 Die Station ist erledigt, wenn du den ganzen Film gesehen hast. Springen zählt nicht.</p>`;
  }
  // Jede Statusmeldung führt den Balken der Film-Karten dieses Films nach (nicht erst der Abschluss)
  function filmKartenNachfuehren(id) {
    INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(t => { if (t.typ === "film" && t.film === id && body(t.nr)) filmAufgabeAktualisieren(t); }));
  }
  function filmAufgabeAktualisieren(t) {
    const z = fz(t.film), p = Math.min(100, z.gesehen);
    const b = document.getElementById("filmbalken-" + t.nr), s = document.getElementById("filmproz-" + t.nr);
    if (b) b.style.width = p + "%";
    if (s) s.textContent = z.frei ? "✅ ganz gesehen" : p + " %";
    if (z.frei && !state.completed.has(String(t.nr))) {
      if (!state.restoring) sendAntwort(t.nr, "film", `Film vollständig angesehen (${p} %)`, true, t.titel);
      showFb(t.nr, "ok", "✅ Film vollständig angesehen.");
      markComplete(t.nr);
    }
  }
  BIE.actions["film-spielen"] = el => {
    const t = aufgabenByNr[el.dataset.nr], id = filmVonAufgabe(t);
    befehle(id, [{ mw: "spielen" }]);
    nachSenden(id, 900, () => {
      const d = lauf[id];
      if (!d || !d.laeuft) showFb(t.nr, "info", "👆 Tippe im Filmfenster auf ▶, um den Film zu starten.");
    });
  };

  // ─── Aufgabentyp „filmmoment“: Finde den Moment ────────────────────────
  // Daten: frage, start (Sekunde, ab der abgespielt wird), niveaus: {A: {fenster: [a, b], tipp}, …}, zu_frueh, zu_spaet, erklaerung
  function renderMoment(t) {
    const cfg = cfgOf(t) || {};
    state.runtime[t.nr] = { versuche: 0, fertig: false, t: null };
    const tippSofort = niveauOf(t.nr) === "A" && cfg.tipp;
    return `
      <p class="task-question">${esc(cfg.frage || t.frage || "")}</p>
      ${tippSofort ? `<p class="hint">💡 ${esc(cfg.tipp)}</p>` : ""}
      <div class="btn-row">
        <button class="btn btn-quiet" type="button" data-action="moment-start" data-nr="${t.nr}">▶ Film ab ${fmt(t.start || 0)} abspielen</button>
        <button class="btn btn-primary" type="button" data-action="moment-pruefen" data-nr="${t.nr}">⏸ Hier habe ich angehalten – prüfen</button>
      </div>
      ${PRUEF ? `<p class="hint pruef-loesung">🔍 Lösung: anhalten zwischen ${fmt(cfg.fenster[0])} und ${fmt(cfg.fenster[1])} (${cfg.fenster[0]}–${cfg.fenster[1]} s).
        <button class="btn btn-quiet btn-sm" type="button" data-action="moment-loesung" data-nr="${t.nr}">Zum Moment springen</button></p>` : ""}`;
  }
  BIE.actions["moment-start"] = el => {
    const t = aufgabenByNr[el.dataset.nr];
    befehle(t.film, [{ mw: "springe", t: t.start || 0 }, { mw: "spielen" }]);
    nachSenden(t.film, 1100, () => { const d = lauf[t.film]; if (!d || !d.laeuft) showFb(t.nr, "info", "👆 Tippe im Filmfenster auf ▶. Halte dann genau im richtigen Moment an."); });
  };
  BIE.actions["moment-loesung"] = el => { const t = aufgabenByNr[el.dataset.nr], c = cfgOf(t); befehle(t.film, [{ mw: "springe", t: (c.fenster[0] + c.fenster[1]) / 2 }]); };
  BIE.actions["moment-pruefen"] = el => momentPruefen(aufgabenByNr[el.dataset.nr]);
  function momentPruefen(t, gespeichert) {
    const cfg = cfgOf(t) || {}, rt = state.runtime[t.nr];
    if (!rt || rt.fertig) return;
    const d = lauf[t.film];
    const zeit = gespeichert !== undefined ? gespeichert : (d && !d.laeuft ? d.t : null);
    if (gespeichert === undefined && d && d.modus === "flug") { showFb(t.nr, "info", "⏳ Der Film startet gerade – halte ihn dann im richtigen Moment an."); return; }
    if (zeit === null || (gespeichert === undefined && Math.abs(zeit - (t.start || 0)) < 0.25)) {
      showFb(t.nr, "info", d && d.laeuft ? "⏸ Halte den Film zuerst an – genau in dem Moment." : "▶ Spiel zuerst den Film ab und halte ihn im richtigen Moment an."); return;
    }
    const [a, b] = cfg.fenster;
    rt.t = zeit;
    if (zeit >= a && zeit <= b) {
      rt.fertig = true;
      if (gespeichert === undefined) sendAntwort(t.nr, "filmmoment", `angehalten bei ${zeit.toFixed(1)} s`, true, cfg.frage || t.titel);
      showFb(t.nr, "ok", `✅ Genau erwischt (${fmt(zeit)})!${t.erklaerung ? " " + esc(t.erklaerung) : ""}`);
      markComplete(t.nr);
    } else {
      rt.versuche++;
      sendAntwort(t.nr, "filmmoment", `angehalten bei ${zeit.toFixed(1)} s`, false, cfg.frage || t.titel);
      const text = zeit < a ? (t.zu_frueh || "Noch zu früh. Spiel ein Stück weiter.") : (t.zu_spaet || "Das war schon danach. Spul ein Stück zurück.");
      const tipp = cfg.tipp && (niveauOf(t.nr) !== "C" || rt.versuche >= 2) ? `<br>💡 ${esc(cfg.tipp)}` : "";
      showFb(t.nr, "err", `❌ ${esc(text)} (du hast bei ${fmt(zeit)} angehalten)${tipp}`);
    }
    dirty();
  }

  // ─── Modell-Knöpfe an jeder Aufgabe ─────────────────────────────────────
  // modell: Knopf ODER Liste von Knöpfen. Ein Knopf: { film, text, befehle: [{mw:'springe', t} | {mw:'kapitel', n} | {mw:'blick', name} | {mw:'live'} | {mw:'ansicht', name}],
  //   pflicht, spielen } oder ein Bild-Knopf { bild, text, alt, pflicht }. Film-Knöpfe spielen sofort ab (befehleFuer).
  // Zustand (Autosave „filme“): Z.knoepfe[nr] = Liste der erfüllten Knopf-Nummern (alt: true = alle). Ein Pflicht-Knopf zählt bei Filmen mit Zeitachse erst nach
  // MIN_SPIELZEIT Sekunden Wiedergabe (warte), sonst schon mit dem Druck. Die Station ist gesperrt, solange irgendein Pflicht-Knopf offen ist.
  const warte = {};                            // "nr:i" → { nr, i, id, summe, letztes } (nicht gespeichert)
  const erfuelltListe = nr => (Array.isArray(Z.knoepfe[nr]) ? Z.knoepfe[nr] : []);
  const istErfuellt = (nr, i) => Z.knoepfe[nr] === true || erfuelltListe(nr).includes(i);
  const pflichtOffen = (t, liste) => (PRUEF ? [] : liste.map((k, i) => (k.pflicht && !istErfuellt(t.nr, i) ? i : -1)).filter(i => i >= 0));
  const brauchtSpielzeit = k => !PRUEF && !!k.pflicht && !istBild(k) && ZEITFILME.includes(artVon(k.film)) && befehleFuer(k).some(b => b.mw === "spielen");
  function erfuellen(nr, i) {
    if (Z.knoepfe[nr] === true || istErfuellt(nr, i)) return;
    Z.knoepfe[nr] = erfuelltListe(nr).concat(i).sort((x, y) => x - y);
    delete warte[nr + ":" + i];
    dirty();
    const t = aufgabenByNr[nr]; if (t && body(t.nr)) knoepfeZeichnen(t);
  }
  // Statusmeldung eines Films: läuft er nach dem Druck zusammenhängend lange genug, ist der Pflicht-Knopf erfüllt
  function spielzeitZaehlen(id, d) {
    Object.values(warte).forEach(w => {
      if (w.id !== id) return;
      if (d.laeuft && typeof d.t === "number") {
        if (w.letztes !== null) { const dt = d.t - w.letztes; if (dt > 0 && dt <= 1.5) w.summe += dt; }
        w.letztes = d.t;
      } else w.letztes = null;
      if (w.summe >= MIN_SPIELZEIT) erfuellen(w.nr, w.i);
    });
  }
  // Führt einen Knopf aus (Aufgaben-Leiste und Zeilen-Knöpfe in forschen.js): Film springen + spielen, Modell stellen, Bild öffnen
  function knopf(k, el) {
    if (!k) return;
    if (istBild(k)) { if (BIE.bild) BIE.bild.oeffnen(bildQuelle(k.bild), k.alt || k.text || "", el); return; }
    const liste = befehleFuer(k);
    befehle(k.film, liste);
    if (liste.some(b => b.mw === "spielen")) {   // Browser erlauben den Start oft nur durch einen Tipp im Film
      nachSenden(k.film, 1300, () => { const d = lauf[k.film]; if (!d || !d.laeuft) showToast("👆 Tippe im Filmfenster auf ▶, damit es startet.", "#006AB3"); });
    }
  }
  function sperrText(t, liste) {
    const pf = liste.map((k, i) => (k.pflicht ? i : -1)).filter(i => i >= 0), offen = pflichtOffen(t, liste), n = pf.length, getan = n - offen.length;
    const k0 = liste[pf[0]] || liste[0], ort = istBild(k0) ? "Bild" : artVon(k0.film) === "modell3d" ? "Modell" : "Film";
    if (n === 1) return `👆 Sieh dir zuerst die Stelle im ${ort} an${warte[t.nr + ":" + pf[0]] ? " – schau ein paar Sekunden zu" : ""} – dann geht es hier los.`;
    const wartet = pf.some(i => warte[t.nr + ":" + i]);
    return `👆 Sieh dir zuerst alle ${n} Stellen an (${getan} von ${n} geschafft)${wartet ? " – schau jeweils ein paar Sekunden zu" : ""} – dann geht es hier los.`;
  }
  function knoepfeZeichnen(t) {
    const host = body(t.nr); if (!host) return;
    const liste = knoepfeVon(t); if (!liste.length) return;
    let leiste = host.querySelector(".film-knoepfe");
    if (!leiste) { leiste = document.createElement("div"); leiste.className = "film-knoepfe"; host.prepend(leiste); }
    leiste.innerHTML = liste.map((k, i) => {
      const gesperrt = brauchtFrei(k) && !fz(k.film).frei && !PRUEF;
      const stand = istErfuellt(t.nr, i) ? "✅ " : warte[t.nr + ":" + i] ? "⏳ " : "";
      return `<button class="btn film-knopf${k.pflicht ? " pflicht" : ""}" type="button" data-action="film-knopf" data-nr="${t.nr}" data-i="${i}"${gesperrt ? " disabled" : ""}>
          ${stand}${knopfBeschriftung(k)}</button>
        ${gesperrt ? `<span class="hint">🔒 Wird frei, wenn du den ganzen Film gesehen hast.</span>` : ""}`;
    }).join("");
    const pflicht = pflichtOffen(t, liste).length > 0;
    host.classList.toggle("film-gesperrt", pflicht);
    let schild = host.querySelector(".film-sperre");
    if (pflicht) {
      if (!schild) { schild = document.createElement("p"); schild.className = "film-sperre"; leiste.after(schild); }
      schild.textContent = sperrText(t, liste);
    } else if (schild) schild.remove();
  }
  BIE.actions["film-knopf"] = el => {
    const t = aufgabenByNr[el.dataset.nr], i = +el.dataset.i, k = knoepfeVon(t)[i]; if (!k) return;
    knopf(k, el);
    if (brauchtSpielzeit(k)) { warte[t.nr + ":" + i] = { nr: String(t.nr), i, id: k.film, summe: 0, letztes: null }; knoepfeZeichnen(t); }
    else erfuellen(String(t.nr), i);
  };

  // Aufruf aus aufgaben.js am Ende von renderBody(t)
  function nachRender(t) {
    if (t.typ === "film") filmAufgabeAktualisieren(t);
    knoepfeZeichnen(t);
  }
  const render = t => t.typ === "filmmoment" ? renderMoment(t) : renderFilm(t);

  // Aufgabenzustand für den Autosave von aufgaben.js (nur filmmoment hat eigenen Zustand)
  function collect(nr) {
    const rt = state.runtime[nr], t = aufgabenByNr[nr];
    if (!t || t.typ !== "filmmoment" || !rt || (rt.t === null && !rt.versuche)) return undefined;
    return { typ: "filmmoment", t: rt.t, versuche: rt.versuche, fertig: rt.fertig };
  }
  function restore(nr, d) {
    const rt = state.runtime[nr], t = aufgabenByNr[nr];
    if (!rt || !d || !t || t.typ !== "filmmoment") return;
    rt.versuche = d.versuche || 0;
    if (d.fertig && typeof d.t === "number") momentPruefen(t, d.t);
  }

  // Filmstand für den Autosave (eigener Eintrag)
  if (BIE.autosave) BIE.autosave.register("filme", () => (Object.keys(Z.filme).length || Object.keys(Z.knoepfe).length ? JSON.parse(JSON.stringify(Z)) : undefined), data => {
    if (!data) return;
    Object.assign(Z.filme, data.filme || {});
    Object.entries(data.knoepfe || {}).forEach(([nr, v]) => {      // alt: true; neu: Liste der erfüllten Knöpfe (kaputte Daten werden ignoriert)
      if (v === true) Z.knoepfe[nr] = true;
      else if (Array.isArray(v)) { const t = aufgabenByNr[nr], n = t ? knoepfeVon(t).length : 0; Z.knoepfe[nr] = [...new Set(v.filter(i => Number.isInteger(i) && i >= 0 && i < n))].sort((x, y) => x - y); }
    });
    Object.keys(Z.filme).forEach(id => { if (Z.filme[id].frei) senden(id, { mw: "freischalten" }); });
    INHALTE.tabs.forEach(tab => tab.aufgaben.forEach(t => { if (body(t.nr)) nachRender(t); }));
  }, 30);

  // Für schritte.js: Reiter mit tab.filmFrei = "<film-id>" bleibt gesperrt, bis der Film vollständig gesehen wurde
  function tabGesperrt(key) {
    const tab = INHALTE.tabs.find(t => t.key === key);
    return !!(tab && tab.filmFrei && !PRUEF && !fz(tab.filmFrei).frei);
  }

  function init() { buehneAufbauen(); zeige(filmFuerTab(state.activeTab)); }

  return {
    init, render, nachRender, collect, restore, tabGesperrt, befehle, befehleFuer, knopf, zeige, stationWechsel, stationHoerer, bereit: id => !!bereit[id],
    frei: id => fz(id).frei, gesehen: id => fz(id).gesehen, besucht: id => fz(id).besucht.slice(), status: id => lauf[id], info: id => info[id],
    beobachten: fn => hoerer.push(fn),
  };
})();
