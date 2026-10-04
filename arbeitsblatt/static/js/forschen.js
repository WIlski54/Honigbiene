/* Forschend-entwickelnder Ansatz (Namensraum BIE.forschen). Wird NACH film.js und modell3d.js geladen.
   Verbindliche Spezifikation: docs/FORSCHEN.md. Format mit Mini-Beispielen: docs/FORSCHEN_BEISPIELE.js.

   Sechs Aufgabentypen – alle (außer forscherbuch) mit niveaus {A, B, C}; alle Texte einfacher Text, kein HTML:
     vermutung    Forscherfrage mit Vermutung, keine Bewertung. „Vermutung festhalten“ sperrt die Karte (ehrliche Forschung).
                  A: optionen (eine, mit mehrfach: true mehrere) · B: optionen + satzanfang + begruendung (Bausteine) · C: satzanfang + frei + min
     pruefen      Vermutung (per id aus der Station `vermutung`) mit der Beobachtung vergleichen: Selbsteinschätzung,
                  Erkenntnis wählen (ok wird geprüft), B Beleg wählen, C eigener Satz. Merksatz `erkenntnis` → Forscherbuch.
     protokoll    Forscherbogen: Zeilen (zahl, wahl, mehrfach, text) mit Prüfung, Hinweisen, Zeilen-Knopf `modell`, optional schluss.
     tabelle      Vergleichstabelle: je Zelle Optionen (Chips) wählen, „Prüfen“ färbt die Zellen, richtige Zellen sperren.
                  Spalten sind Text oder { name, bild, alt } (Bild über dem Namen); Zeilen können ein Bild haben (zeilen[].bild + alt,
                  antippbar zum Vergrößern über bild.js).
     bildwahl     Entscheiden am Bild in mehreren Runden: Tippen auf Trefferkreise (ok: true = richtig).
     forscherbuch Sammelt je Reiter Forscherfrage → Vermutung → Erkenntnis (+ Notizen); Drucken/PDF, Text kopieren, abgeben.

   Zustand: je Aufgabe ein kleines Objekt in D (Schlüssel = Aufgabennummer) – Autosave-Eintrag „forschen“ (order 32), damit
   übersteht alles Neuladen, Snapshots und das IServ-Archiv. Das Forscherbuch liest nur (speichert nichts Eigenes).
   Reine Logik (Zahlprüfung, Tabellenprüfung, Trefferkreise, Texte, Zustandsbereinigung, Forscherbuch) steht in `logik`
   und wird von tests/forschen.test.cjs ohne Browser geprüft. Antworten gehen mit lesbarem Text an den Server
   („Vermutung: …“, „Beobachtung: Beine = 6 ✅“); Vermutungen ohne Bewertung (korrekt = null).
   Zeilen-/Zellen-Knöpfe `modell` (ein Knopf oder eine Liste, auch Bild-Knöpfe) und das Aufgabenfeld `modell` nutzen von film.js nur BIE.film.knopf/befehle.

   Audit 4. Oktober 2026 (docs/AUDIT_FORSCHEN_2026-10-04.md): T1 Knopflisten und Bild-Knöpfe in Zeilen · T2 pruefen mit vierter Einschätzung und eigenen Fehltexten ·
   T3 „Raten verhindern“: die erste wirksame Prüfung von tabelle/protokoll zählt nur („x von y stimmen“), gefärbt wird ab der zweiten (cfg.sofortFaerben: true = sofort),
   ein Prüfen ohne Änderung zählt nicht · T4 Zahlwörter und Tausenderformate · T8 Forscherbuch mit Einschätzung und eigenem Satz, Vermutungs-Satzbau. */
BIE.forschen = (() => {
  "use strict";
  const { INHALTE, state, $, $$, esc, cfgOf, niveauOf, body, card, showFb, clearFb, markComplete, sendAntwort, dirty, aufgabenByNr, APP } = BIE;
  const PRUEF = !!BIE.pruefmodus;
  const TYPEN = ["vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch"];
  const ZEILENARTEN = ["zahl", "wahl", "mehrfach", "text"];
  const EINSCHAETZUNG = ["Sie stimmt", "Sie stimmt teilweise", "Sie stimmt nicht", "Das kann ich hier nicht herausfinden"];   // die vierte sperrt nichts (freie Vermutungen)
  const EINSCH_KURZ = ["stimmt", "stimmt teilweise", "stimmt nicht", "kann ich hier nicht herausfinden"];       // für das Protokoll der Lehrkraft und das Forscherbuch
  const istMein = t => TYPEN.includes(t.typ);
  const FORSCHERBUCH_MAX = 8000;                  // Zeichen beim Abgeben (Server: config.ANTWORT_MAX_ZEICHEN)
  const alleAufgaben = () => INHALTE.tabs.flatMap(tab => tab.aufgaben);
  const liste = x => (Array.isArray(x) ? x : []);
  // Bilddatei mit Versionsmarke (neue Fassung der Datei wird nach einem Update sofort geladen)
  const bildQuelle = src => String(src) + (APP.assetVersion ? (String(src).includes("?") ? "&" : "?") + "v=" + APP.assetVersion : "");
  const ganz = x => Number.isInteger(x);
  const text = (x, max) => String(x == null ? "" : x).slice(0, max || 4000);

  // ═══ Reine Logik (ohne DOM) ═══════════════════════════════════════════════════════════════════
  // Zahlwörter bis 999 999 („einundzwanzig“, „zweihundertdreiundvierzig“, „fünfzigtausend“, „hunderttausend“); Umlaute und ß werden angeglichen
  const EINER = { null: 0, ein: 1, eins: 1, eine: 1, einen: 1, zwei: 2, zwo: 2, drei: 3, vier: 4, fuenf: 5, sechs: 6, sieben: 7, acht: 8, neun: 9, zehn: 10, elf: 11, zwoelf: 12,
    dreizehn: 13, vierzehn: 14, fuenfzehn: 15, sechzehn: 16, siebzehn: 17, achtzehn: 18, neunzehn: 19 };
  const ZEHNER = { zwanzig: 20, dreissig: 30, vierzig: 40, fuenfzig: 50, sechzig: 60, siebzig: 70, achtzig: 80, neunzig: 90 };
  const hat = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  function bis99(x) {
    if (hat(EINER, x)) return EINER[x];
    if (hat(ZEHNER, x)) return ZEHNER[x];
    const m = x.match(/^(.+?)und(.+)$/);                                        // einundzwanzig
    return m && hat(EINER, m[1]) && EINER[m[1]] >= 1 && EINER[m[1]] <= 9 && hat(ZEHNER, m[2]) ? EINER[m[1]] + ZEHNER[m[2]] : null;
  }
  function bis999(x) {
    const i = x.indexOf("hundert");
    if (i < 0) return bis99(x);
    const h = i === 0 ? 1 : bis99(x.slice(0, i)), rest = x.slice(i + 7).replace(/^und/, "");
    if (h === null || h < 1 || h > 9) return null;
    const r = rest === "" ? 0 : bis99(rest);
    return r === null ? null : h * 100 + r;
  }
  function zahlWort(s) {
    s = s.replace(/ß/g, "ss").replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/[\s-]+/g, "");
    if (!/^[a-z]+$/.test(s)) return null;
    const i = s.indexOf("tausend");
    if (i < 0) return bis999(s);
    const v = i === 0 ? 1 : bis999(s.slice(0, i)), rest = s.slice(i + 7).replace(/^und/, "");
    if (v === null || v < 1) return null;
    const r = rest === "" ? 0 : bis999(rest);
    return r === null ? null : v * 1000 + r;
  }
  // „6“, „6,5“, „6 Beine“, „sechs“, „einundzwanzig“, „50 000“, „50.000“, „50000“, „fünfzigtausend“, „50 000 Bienen“ → Zahl; sonst null
  function parseZahl(eingabe) {
    const s = String(eingabe == null ? "" : eingabe).trim().toLowerCase().replace(/[\u00a0\u202f]/g, " ");
    if (!s) return null;
    const m = s.match(/^(-?\d[\d .,]*)\s*([^\d]*)$/);                          // Ziffern (mit Tausendertrennern) + Einheit
    if (m) {
      let z = m[1].trim().replace(/[ .,]+$/, "");
      if (/^-?\d{1,3}([ .]\d{3})+(,\d+)?$/.test(z)) z = z.replace(/[ .]/g, "");   // Tausendertrennzeichen
      if (!/^-?\d+([.,]\d+)?$/.test(z)) return null;
      const n = parseFloat(z.replace(",", "."));
      return Number.isFinite(n) ? n : null;
    }
    if (/\d/.test(s)) return null;
    const ganzes = zahlWort(s);                                                // „fünfzig tausend“, „einundzwanzig“
    if (ganzes !== null) return ganzes;
    const erstes = s.split(/\s+/)[0];                                          // „sechs Beine“, „fünfzigtausend Bienen“
    return erstes !== s ? zahlWort(erstes) : null;
  }
  const zahlStimmt = (wert, loesung, toleranz) => typeof wert === "number" && Number.isFinite(wert) && Math.abs(wert - Number(loesung)) <= (Number(toleranz) || 0) + 1e-9;
  const wahlStimmt = (wahl, loesung) => ganz(wahl) && wahl === loesung;
  function mehrfachStimmt(wahl, loesung) {
    const a = [...new Set(liste(wahl).filter(ganz))].sort((x, y) => x - y), b = [...new Set(liste(loesung).filter(ganz))].sort((x, y) => x - y);
    return a.length === b.length && a.every((v, i) => v === b[i]);
  }
  // Eine Zeile des Forscherbogens: {leer, ok}. w = Eingabe (zahl: Text, wahl: Index, mehrfach: Liste, text: Text)
  function zeileAuswerten(row, w) {
    const art = ZEILENARTEN.includes(row.art) ? row.art : "zahl";
    if (art === "zahl") { if (w === null || w === undefined || String(w).trim() === "") return { leer: true, ok: false }; return { leer: false, ok: zahlStimmt(parseZahl(w), row.loesung, row.toleranz) }; }
    if (art === "wahl") { if (!ganz(w)) return { leer: true, ok: false }; return { leer: false, ok: wahlStimmt(w, row.loesung) }; }
    if (art === "mehrfach") { if (!liste(w).length) return { leer: true, ok: false }; return { leer: false, ok: mehrfachStimmt(w, row.loesung) }; }
    const t = String(w == null ? "" : w).trim();
    return { leer: !t, ok: t.length >= (row.min || 6) };      // text: nur Länge, keine inhaltliche Bewertung
  }
  const kurzTitel = r => String(r.kurz || r.einheit || r.frage || "").replace(/[?:\s]+$/, "").trim().slice(0, 50);
  // Lesbarer Protokolltext einer Zeile, z. B. „Beobachtung: Beine = 6 ✅“
  function zeilenText(row, w, ok) {
    const art = ZEILENARTEN.includes(row.art) ? row.art : "zahl", ops = liste(row.optionen), lab = kurzTitel(row);
    let inhalt;
    if (art === "zahl") { const n = parseZahl(w); inhalt = `${lab} = ${n === null ? String(w).trim() : n}`; }
    else if (art === "wahl") inhalt = `${lab} = ${ops[w] === undefined ? "?" : ops[w]}`;
    else if (art === "mehrfach") inhalt = `${lab} = ${liste(w).map(i => ops[i]).filter(x => x !== undefined).join(" + ")}`;
    else inhalt = `${lab}: „${String(w).trim()}“`;
    return `Beobachtung: ${inhalt} ${ok ? "✅" : "❌"}`;
  }
  // Tabelle: auswahl[i][j] = gewählter Optionsindex (oder null), zeilen[i].loesung[j] = richtiger Index
  function tabelleAuswerten(auswahl, zeilen, spalten) {
    const ok = zeilen.map((z, i) => Array.from({ length: spalten }, (_, j) => {
      const w = liste(auswahl[i])[j];
      return !ganz(w) ? null : w === liste(z.loesung)[j];
    }));
    let richtig = 0, gesamt = 0, leer = 0;
    ok.forEach(r => r.forEach(x => { gesamt++; if (x === true) richtig++; else if (x === null) leer++; }));
    return { ok, richtig, gesamt, leer, fertig: gesamt > 0 && richtig === gesamt };
  }
  // Spalten dürfen Text oder ein Objekt { name, bild, alt } sein (auch gemischt); der Name steht immer im Text der Antwort.
  const spaltenName = s => String(s !== null && typeof s === "object" ? (s.name ?? "") : (s ?? ""));
  const bildVon = (x, alt) => (x && typeof x === "object" && typeof x.bild === "string" && x.bild.trim() ? { src: x.bild.trim(), alt: String(x.alt || alt || "") } : null);
  const spaltenBild = s => bildVon(s, spaltenName(s));
  const zeilenBild = z => bildVon(z, z && z.merkmal);
  function tabelleText(zeilen, spalten, auswahl, ok) {
    const teile = zeilen.map((z, i) => `${z.merkmal}: ` + spalten.map((s, j) => {
      const o = liste(z.optionen)[liste(auswahl[i])[j]];
      return `${spaltenName(s)} = ${o === undefined ? "?" : o} ${ok[i][j] === true ? "✅" : ok[i][j] === false ? "❌" : ""}`.trim();
    }).join(", "));
    return teile.join(" | ");
  }
  // Bildwahl: Trifft der Punkt (x, y) im Bildkoordinatensystem ein Ziel? Bei Überlappung gewinnt der nächste Mittelpunkt.
  // Kleine Kreise werden so weit vergrößert, dass sie mindestens `minR` (Bildeinheiten) groß sind – Touchziel ≥ 44 px
  const kreisR = (z, minR) => Math.max(Number(z.r) || 0, Number(minR) || 0);
  const trifftKreis = (z, x, y, minR) => Math.hypot(x - z.x, y - z.y) <= kreisR(z, minR);
  function zielAn(ziele, x, y, minR) {
    let best = -1, abstand = Infinity;
    liste(ziele).forEach((z, i) => { const a = Math.hypot(x - z.x, y - z.y); if (a <= kreisR(z, minR) && a < abstand) { best = i; abstand = a; } });
    return best;
  }
  const MIN_ZIEL_PX = 44;                       // kleinstes Touchziel in Pixeln (Durchmesser)
  const minRadius = (breiteBild, breitePx) => (breitePx > 0 ? (MIN_ZIEL_PX / 2) * breiteBild / breitePx : 0);   // Bildeinheiten
  // Satzanfang „Ich vermute, dass …“ + Fortsetzung → ein Satz
  const anfangOhnePunkte = a => String(a || "").replace(/\s*(…|\.\.\.)\s*$/, "").trim();
  const satzGanz = (anfang, rest) => [anfangOhnePunkte(anfang), String(rest || "").trim()].filter(Boolean).join(" ");
  const baustein = b => String(b || "").replace(/\s*(…|\.\.\.)\s*$/, "").trim();
  // Vermutung: Mindestlänge je Niveau – A wählt nur, B ergänzt einen Satz, C schreibt frei
  const vermutungMin = cfg => (cfg.min != null ? cfg.min : (cfg.frei ? 30 : 10));
  // `min` zählt nur den EIGENEN Text: angetippte Satzbausteine („weil …“) zählen nicht mit
  function eigenerText(cfg, satz) {
    const bs = liste(cfg.begruendung).map(b => String(b || "").replace(/\s*(…|\.\.\.)\s*$/, "").trim()).filter(Boolean);
    let s = String(satz || "");
    if (bs.length) s = s.replace(new RegExp("(?<!\\p{L})(?:" + bs.map(b => b.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(?!\\p{L})", "giu"), " ");
    return s.replace(/\s+/g, " ").trim();
  }
  const eigeneLaenge = (cfg, satz) => eigenerText(cfg, satz).length;
  function vermutungGueltig(cfg, wahl, satz) {
    const ops = liste(cfg.optionen);
    if (ops.length && !liste(wahl).length) return { ok: false, grund: "wahl" };
    if ((cfg.frei || cfg.satzanfang) && eigeneLaenge(cfg, satz) < vermutungMin(cfg)) return { ok: false, grund: "text", min: vermutungMin(cfg) };
    return { ok: true };
  }
  // Mehrere Optionen: „a und b“; endet eine Option schon mit einem Satzzeichen, folgt die nächste ohne „und“
  const optionenText = ops => ops.map((o, i) => (i === 0 ? "" : (/[.!?]$/.test(ops[i - 1]) ? " " : " und ")) + o).join("");
  function vermutungTexte(cfg, wahl, satz) {
    const ops = liste(cfg.optionen), gewaehlt = [...new Set(liste(wahl).filter(ganz))].sort((a, b) => a - b).map(i => ops[i]).filter(x => x !== undefined);
    // „Meine Vermutung: …“ als Satzanfang steht schon im Feld-Etikett: im Text der Vermutung nicht doppelt („Vermutung: Meine Vermutung: …“)
    const anfang = /^meine vermutung\s*:?$/i.test(anfangOhnePunkte(cfg.satzanfang)) ? "" : cfg.satzanfang;
    const satzT = (cfg.frei || cfg.satzanfang) && String(satz || "").trim() ? satzGanz(anfang, satz) : "";
    return {
      optionen: gewaehlt, satz: satzT,
      text: [optionenText(gewaehlt), satzT].filter(Boolean).join(" – "),
      // „ · “ trennt Optionen und Begründung: das Dashboard wertet die Optionen aus
      antwort: "Vermutung: " + [gewaehlt.join(" | "), satzT].filter(Boolean).join(" · "),
    };
  }

  // ─── Zustand (D) bereinigen: kommt aus Autosave/IServ und darf nichts kaputt machen ───
  const idxListe = (x, n) => [...new Set(liste(x).filter(i => ganz(i) && i >= 0 && i < n))];
  function bereinigen(t, d) {
    if (!d || typeof d !== "object") return null;
    const cfgs = t.niveaus || {}, niveau = ["A", "B", "C"].includes(d.niveau) ? d.niveau : "A", cfg = cfgs[niveau] || {};
    const out = { niveau };
    if (t.typ === "vermutung") {
      out.wahl = idxListe(d.wahl, liste(cfg.optionen).length); out.satz = text(d.satz, 2000);
      if (d.fest) { out.fest = true; out.text = text(d.text, 2000); out.antwort = text(d.antwort, 2000); out.optionen = liste(d.optionen).map(x => text(x, 300)); }
      return out;
    }
    if (t.typ === "pruefen") {
      const erk = d.erk || {}, bel = d.beleg || {}, ne = liste(cfg.erkenntnis && cfg.erkenntnis.optionen).length, nb = liste(cfg.beleg && cfg.beleg.optionen).length;
      out.einsch = ganz(d.einsch) && d.einsch >= 0 && d.einsch < EINSCHAETZUNG.length ? d.einsch : null;
      out.erk = { ok: ganz(erk.ok) && erk.ok >= 0 && erk.ok < ne ? erk.ok : null, falsch: idxListe(erk.falsch, ne) };
      out.beleg = { ok: ganz(bel.ok) && bel.ok >= 0 && bel.ok < nb ? bel.ok : null, falsch: idxListe(bel.falsch, nb) };
      out.satz = text(d.satz, 2000); out.fertig = !!d.fertig;
      return out;
    }
    if (t.typ === "protokoll") {
      const zeilen = liste(cfg.zeilen);
      out.z = zeilen.map((row, i) => {
        const z = liste(d.z)[i] || {}, art = ZEILENARTEN.includes(row.art) ? row.art : "zahl", n = liste(row.optionen).length;
        let w = null;
        if (art === "zahl") w = z.w == null ? null : text(z.w, 20);
        else if (art === "wahl") w = ganz(z.w) && z.w >= 0 && z.w < n ? z.w : null;
        else if (art === "mehrfach") w = idxListe(z.w, n);
        else w = z.w == null ? null : text(z.w, 500);
        return { w, ok: !!z.ok, f: ganz(z.f) && z.f > 0 ? Math.min(z.f, 99) : 0, g: !!z.g };
      });
      out.pr = ganz(d.pr) && d.pr > 0 ? Math.min(d.pr, 99) : 0; out.sig = text(d.sig, 600);          // wirksame Prüfungen (T3)
      const sw = d.schluss && d.schluss.wahl, nb = liste(cfg.schluss && cfg.schluss.bausteine).length;
      out.schluss = { wahl: ganz(sw) && sw >= 0 && sw < nb ? sw : null, satz: text(d.schluss && d.schluss.satz, 2000), fertig: !!(d.schluss && d.schluss.fertig) };
      return out;
    }
    if (t.typ === "tabelle") {
      const zeilen = liste(cfg.zeilen), sp = liste(cfg.spalten).length;
      out.a = zeilen.map((z, i) => Array.from({ length: sp }, (_, j) => { const w = liste(liste(d.a)[i])[j]; return ganz(w) && w >= 0 && w < liste(z.optionen).length ? w : null; }));
      out.ok = zeilen.map((z, i) => Array.from({ length: sp }, (_, j) => !!liste(liste(d.ok)[i])[j] && out.a[i][j] !== null));
      out.f = zeilen.map((z, i) => (ganz(liste(d.f)[i]) && d.f[i] > 0 ? Math.min(d.f[i], 99) : 0));
      out.x = zeilen.map((z, i) => Array.from({ length: sp }, (_, j) => !!liste(liste(d.x)[i])[j] && out.a[i][j] !== null && !out.ok[i][j]));   // geprüft und falsch
      out.pr = ganz(d.pr) && d.pr > 0 ? Math.min(d.pr, 99) : 0; out.sig = text(d.sig, 600);          // wirksame Prüfungen (T3)
      return out;
    }
    if (t.typ === "bildwahl") {
      const runden = liste(cfg.runden);
      out.runde = ganz(d.runde) ? Math.max(0, Math.min(d.runde, runden.length - 1)) : 0;
      out.ok = runden.map((r, i) => !!liste(d.ok)[i]);
      out.versuche = runden.map((r, i) => (ganz(liste(d.versuche)[i]) && d.versuche[i] > 0 ? Math.min(d.versuche[i], 99) : 0));
      out.falsch = runden.map((r, i) => idxListe(liste(d.falsch)[i], liste(r.ziele).length));
      out.fertig = runden.length > 0 && out.ok.every(Boolean);
      return out;
    }
    return null;
  }
  // Hat dieser Zustand etwas, das gespeichert werden muss? (Ein frisch angelegter, leerer Zustand wird nicht gesichert.)
  function hatInhalt(d) {
    if (!d) return false;
    if (d.fest || d.fertig || d.pr > 0) return true;
    if (d.einsch !== undefined && d.einsch !== null) return true;
    if (liste(d.wahl).length || (d.satz && d.satz.trim())) return true;
    if (d.erk && (d.erk.ok !== null || d.erk.falsch.length)) return true;
    if (d.beleg && (d.beleg.ok !== null || d.beleg.falsch.length)) return true;
    if (d.z && d.z.some(z => z.f || z.ok || (z.w !== null && z.w !== "" && !(Array.isArray(z.w) && !z.w.length)))) return true;
    if (d.a && d.a.some(r => r.some(x => x !== null))) return true;
    if (d.runde > 0 || (d.versuche && d.versuche.some(Boolean))) return true;
    return !!(d.schluss && (d.schluss.fertig || d.schluss.wahl !== null || (d.schluss.satz && d.schluss.satz.trim())));
  }

  // ─── Forscherbuch: Eingabe (aus dem Live-Zustand) → Text und HTML ───
  // buch = [{ key, label, icon, eintraege: [{ frage, vermutung|null, einschaetzung?, erkenntnisse: [], saetze?: [] }], weitere: [], notizen: [] }]
  // einschaetzung = „stimmt“ / „stimmt teilweise“ / … (Selbsteinschätzung aus pruefen), saetze = eigene Sätze der Kinder (Niveau C)
  const buchLeer = buch => !buch.some(r => r.eintraege.length || r.weitere.length || r.notizen.length);
  function buchText(buch, kopf) {
    const z = [`Mein Forscherbuch${kopf ? " – " + kopf : ""}`, ""];
    buch.forEach(r => {
      if (!r.eintraege.length && !r.weitere.length && !r.notizen.length) return;
      z.push(`== ${r.label} ==`);
      r.eintraege.forEach(e => {
        z.push(`Forscherfrage: ${e.frage}`);
        z.push(`Meine Vermutung: ${e.vermutung || "noch nicht festgehalten"}`);
        if (e.einschaetzung) z.push(`Meine Einschätzung: ${e.einschaetzung}`);
        z.push(`Meine Erkenntnis: ${e.erkenntnisse.length ? e.erkenntnisse.join(" ") : "noch nicht herausgefunden"}`);
        liste(e.saetze).forEach(s => z.push(`Mein Satz dazu: ${s}`));
        z.push("");
      });
      if (r.weitere.length) { z.push("Das habe ich noch herausgefunden:"); r.weitere.forEach(w => z.push(`- ${w}`)); z.push(""); }
      r.notizen.forEach(n => { z.push("Meine Notizen:"); z.push(n); z.push(""); });
    });
    return z.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }
  function buchHTML(buch) {
    if (buchLeer(buch)) return `<p class="muted fo-buch-leer">Dein Forscherbuch ist noch leer. Es füllt sich, wenn du Vermutungen festhältst und Erkenntnisse sammelst.</p>`;
    return buch.map(r => {
      if (!r.eintraege.length && !r.weitere.length && !r.notizen.length) return "";
      return `<section class="fo-buch-reiter"><h4>${esc(r.icon || "")} ${esc(r.label)}</h4>
        ${r.eintraege.map(e => `<div class="fo-eintrag">
          <p class="fo-b-frage"><span class="fo-b-label">Forscherfrage</span> ${esc(e.frage)}</p>
          <p class="fo-b-verm"><span class="fo-b-label">Meine Vermutung</span> ${e.vermutung ? esc(e.vermutung) : '<em class="muted">noch nicht festgehalten</em>'}</p>
          ${e.einschaetzung ? `<p class="fo-b-einsch"><span class="fo-b-label">Meine Einschätzung</span> ${esc(e.einschaetzung)}</p>` : ""}
          <p class="fo-b-erk"><span class="fo-b-label">Meine Erkenntnis</span> ${e.erkenntnisse.length ? e.erkenntnisse.map(esc).join(" ") : '<em class="muted">noch nicht herausgefunden</em>'}</p>
          ${liste(e.saetze).map(s => `<p class="fo-b-satz"><span class="fo-b-label">Mein Satz dazu</span> ${esc(s)}</p>`).join("")}
        </div>`).join("")}
        ${r.weitere.length ? `<div class="fo-eintrag"><p class="fo-b-label">Das habe ich noch herausgefunden</p><ul>${r.weitere.map(w => `<li>${esc(w)}</li>`).join("")}</ul></div>` : ""}
        ${r.notizen.map(n => `<div class="fo-eintrag"><p class="fo-b-label">Meine Notizen</p><p class="fo-b-notiz">${esc(n)}</p></div>`).join("")}
      </section>`;
    }).join("");
  }

  // Beginnt die Beschriftung eines Knopfes schon mit einem Symbol („▶ Hör zu: …“, „🧊 …“), kommt kein zweites davor (nicht „🎭 ▶ Hör zu“)
  const hatSymbol = text => /^\s*(?:\p{Extended_Pictographic}|[▶▷⏵⏯])/u.test(String(text || ""));
  const logik = { parseZahl, zahlStimmt, wahlStimmt, mehrfachStimmt, zeileAuswerten, zeilenText, tabelleAuswerten, tabelleText, spaltenName, spaltenBild, zeilenBild, trifftKreis, zielAn, kreisR, minRadius,
    anfangOhnePunkte, satzGanz, vermutungGueltig, vermutungTexte, vermutungMin, bereinigen, hatInhalt, buchText, buchHTML, buchLeer, hatSymbol };

  // ═══ Zustand und Hilfen im Browser ═════════════════════════════════════════════════════════════
  let D = {};                                   // Aufgabennummer (Text) → Zustand, nur Daten (Autosave „forschen“)
  const nrKey = t => String(t.nr);
  // Zustand zum aktuellen Niveau. Ein Niveauwechsel beginnt neu – nur die festgehaltene Vermutung bleibt (ehrliche Forschung).
  function dt(t, anlegen) {
    let d = D[nrKey(t)];
    if (d && d.niveau !== niveauOf(t.nr) && !d.fest) { delete D[nrKey(t)]; d = null; }
    if (!d && anlegen) d = D[nrKey(t)] = neuerZustand(t);
    return d || null;
  }
  function neuerZustand(t) {
    const cfg = cfgOf(t) || {}, n = niveauOf(t.nr), sp = liste(cfg.spalten).length;
    if (t.typ === "vermutung") return { niveau: n, wahl: [], satz: "" };
    if (t.typ === "pruefen") return { niveau: n, einsch: null, erk: { ok: null, falsch: [] }, beleg: { ok: null, falsch: [] }, satz: "", fertig: false };
    if (t.typ === "protokoll") return { niveau: n, z: liste(cfg.zeilen).map(row => ({ w: row.art === "mehrfach" ? [] : null, ok: false, f: 0, g: false })), pr: 0, sig: "", schluss: { wahl: null, satz: "", fertig: false } };
    if (t.typ === "tabelle") return { niveau: n, a: liste(cfg.zeilen).map(() => Array(sp).fill(null)), ok: liste(cfg.zeilen).map(() => Array(sp).fill(false)), f: liste(cfg.zeilen).map(() => 0), x: liste(cfg.zeilen).map(() => Array(sp).fill(false)), pr: 0, sig: "" };
    if (t.typ === "bildwahl") return { niveau: n, runde: 0, ok: liste(cfg.runden).map(() => false), versuche: liste(cfg.runden).map(() => 0), falsch: liste(cfg.runden).map(() => []), fertig: false };
    return { niveau: n };
  }
  const rtVon = t => state.runtime[t.nr] || (state.runtime[t.nr] = {});
  const wrap = nr => document.getElementById("fo-" + nr);
  // Nur den eigenen Inhalt neu zeichnen – der Modell-Knopf (film.js) und die Rückmeldung bleiben stehen.
  function neuZeichnen(t) {
    const w = wrap(t.nr); if (!w) return;
    const fokus = document.activeElement && w.contains(document.activeElement) ? document.activeElement.id : "";
    w.innerHTML = inner(t);
    if (fokus) { const e = document.getElementById(fokus); if (e && !e.disabled) e.focus(); }
    if (t.typ === "bildwahl") bildAnpassen(w);
    aktualisiereBuecher();
  }
  const aenderung = t => { dirty(); aktualisiereBuecher(); return t; };
  const fehlHinweis = "<p class=\"muted\">⚠️ Für dieses Niveau fehlen Angaben in den Inhalten.</p>";
  const symbolVon = id => (({ modell3d: "🧊", modellwelt: "🧊", papiertheater: "🎭", archivdoku: "📜" })[((INHALTE.filme || {})[id] || {}).art] || "🎬");
  const loesungKasten = html => (PRUEF ? `<div class="pruef-loesung fo-pruef">🔍 ${html}</div>` : "");

  // Zeilen-Knopf `modell` (öffnet genau die Ansicht, aus der die Antwort folgt): ein Knopf ODER eine Liste; Film-Knöpfe springen und spielen sofort (film.js),
  // ein Bild-Knopf { bild, text, alt } öffnet das Bild im Bild-Fenster.
  const knopfListe = k => (Array.isArray(k) ? k : k ? [k] : []).filter(x => x && (x.film || x.bild));
  const knopfSymbol = k => (k.bild && !k.film ? "🖼️" : symbolVon(k.film));
  const knopfBeschriftung = k => { const text = k.text || (k.bild && !k.film ? "Bild ansehen" : "Im Modell ansehen"); return (hatSymbol(text) ? "" : knopfSymbol(k) + " ") + esc(text); };
  function modellKnopf(nr, k, z, blinken) {
    const knoepfe = knopfListe(k).map((x, j) => `<button class="btn btn-quiet btn-sm fo-modell${blinken ? " fo-blink" : ""}" type="button" data-action="fo-modell" data-nr="${nr}" data-z="${z}" data-k="${j}">${knopfBeschriftung(x)}</button>`);
    return knoepfe.length > 1 ? `<span class="fo-modellreihe">${knoepfe.join("")}</span>` : knoepfe.join("");
  }
  BIE.actions["fo-modell"] = el => {
    const t = aufgabenByNr[el.dataset.nr]; if (!t) return;
    const cfg = cfgOf(t) || {}, quelle = t.typ === "tabelle" || t.typ === "protokoll" ? liste(cfg.zeilen)[parseInt(el.dataset.z, 10)] : null;
    const k = knopfListe(quelle && quelle.modell)[parseInt(el.dataset.k || "0", 10)]; if (!k) return;
    if (BIE.film && BIE.film.knopf) BIE.film.knopf(k, el);
    else if (k.film && BIE.film && BIE.film.befehle) BIE.film.befehle(k.film, k.befehle || []);
    el.classList.remove("fo-blink");
  };

  function chips(attrs, ops, gewaehlt, extraKlasse, gesperrt) {
    return ops.map((o, i) => {
      const an = gewaehlt.includes(i);
      return `<button type="button" class="fo-chip${an ? " is-on" : ""}${extraKlasse ? " " + extraKlasse : ""}" aria-pressed="${an}" ${attrs} data-i="${i}"${gesperrt ? " disabled" : ""}>${esc(o)}</button>`;
    }).join("");
  }
  const chipsMarkieren = (host, gewaehlt) => $$(".fo-chip", host).forEach(b => { const an = gewaehlt.includes(parseInt(b.dataset.i, 10)); b.classList.toggle("is-on", an); b.setAttribute("aria-pressed", String(an)); });

  // ═══ vermutung ═════════════════════════════════════════════════════════════════════════════════
  const vermutungAufgabe = id => alleAufgaben().find(a => a.typ === "vermutung" && a.id === id);
  const demoVermutung = t => {
    const cfg = cfgOf(t) || {}, o = liste(cfg.optionen)[0];
    if (cfg.satzanfang || cfg.frei) return (o ? `${o} – ` : "") + `${anfangOhnePunkte(cfg.satzanfang) || "Ich vermute, dass"} … (Beispiel im Prüfmodus)`;
    return `${o || "…"} (Beispiel im Prüfmodus)`;
  };
  // Text der festgehaltenen Vermutung zu einer Vermutungs-id (für pruefen und das Forscherbuch); null = nicht festgehalten
  function vermutungTextFuer(id) {
    const v = vermutungAufgabe(id); if (!v) return null;
    const d = D[nrKey(v)];
    if (d && d.fest) return d.text;
    return PRUEF ? demoVermutung(v) : null;
  }
  function vermutungInner(t) {
    const d = dt(t), cfg = cfgOf(t) || {}, nr = t.nr, rt = rtVon(t);
    if (!cfg || (!liste(cfg.optionen).length && !cfg.frei && !cfg.satzanfang)) return fehlHinweis;
    if (d && d.fest) {
      return `<div class="fo-fest"><span class="eyebrow">🔒 Meine Vermutung</span><blockquote class="fo-zitat">${esc(d.text)}</blockquote>
        <p class="hint">Du hast deine Vermutung festgehalten. Sie bleibt so stehen – echte Forscherinnen und Forscher ändern ihre Vermutung nicht nachträglich. Gleich findest du heraus, ob sie stimmt.</p></div>`;
    }
    const x = dt(t, true), ops = liste(cfg.optionen);
    const frage = `<p class="task-question">${esc(cfg.frage || t.frage || "Was vermutest du?")}</p>`;
    const optionen = ops.length ? `<div class="fo-chips" role="group" aria-label="Möglichkeiten">${chips(`data-action="fo-verm-wahl" data-nr="${nr}"`, ops, x.wahl)}</div>${cfg.mehrfach ? `<p class="hint">Du darfst mehrere Möglichkeiten antippen.</p>` : ""}` : "";
    const satz = (cfg.frei || cfg.satzanfang) ? `
      <label class="field-label" for="fo-sat-${nr}">${esc(cfg.satzanfang || "Meine Vermutung:")}</label>
      ${liste(cfg.begruendung).length ? `<div class="fo-chips fo-bausteine" role="group" aria-label="Satzbausteine">${liste(cfg.begruendung).map((b, i) => `<button type="button" class="fo-chip fo-chip-baustein" data-action="fo-verm-baustein" data-nr="${nr}" data-i="${i}">${esc(b)}</button>`).join("")}</div>` : ""}
      <textarea id="fo-sat-${nr}" class="fo-text" rows="${cfg.frei && !ops.length ? 4 : 3}" data-fo-input="verm" data-nr="${nr}" placeholder="Schreibe hier weiter …">${esc(x.satz)}</textarea>
      <div class="text-meta"><span id="fo-zaehl-${nr}">${eigeneLaenge(cfg, x.satz)} Zeichen · mindestens ${vermutungMin(cfg)}</span></div>` : "";
    return `${frage}${optionen}${satz}
      <p class="hint">💡 Hier gibt es kein Richtig und kein Falsch. Danach kannst du deine Vermutung nicht mehr ändern.</p>
      <div class="btn-row" id="fo-vk-${nr}">${vermutungKnoepfe(t)}</div>
      ${loesungKasten(`<strong>Prüfmodus:</strong> Beispiel: ${esc(demoVermutung(t))} <button class="btn btn-quiet btn-sm" type="button" data-action="fo-verm-demo" data-nr="${nr}">Beispiel festhalten</button>`)}`;
  }
  const vermutungKnoepfe = t => (rtVon(t).sicher
    ? `<button class="btn btn-primary" type="button" data-action="fo-verm-fest" data-nr="${t.nr}">✅ Ja, jetzt festhalten</button><button class="btn btn-quiet" type="button" data-action="fo-verm-aendern" data-nr="${t.nr}">Noch ändern</button>`
    : `<button class="btn btn-primary" type="button" data-action="fo-verm-sicher" data-nr="${t.nr}">🔒 Vermutung festhalten</button>`);
  function vermutungSicherheitZuruecksetzen(t) {
    const rt = rtVon(t); if (!rt.sicher) return;
    rt.sicher = false; clearFb(t.nr);
    const k = document.getElementById("fo-vk-" + t.nr); if (k) k.innerHTML = vermutungKnoepfe(t);
  }
  BIE.actions["fo-verm-wahl"] = el => {
    const t = aufgabenByNr[el.dataset.nr], cfg = cfgOf(t) || {}, d = dt(t, true), i = parseInt(el.dataset.i, 10);
    if (!d || d.fest) return;
    if (cfg.mehrfach) d.wahl = d.wahl.includes(i) ? d.wahl.filter(x => x !== i) : d.wahl.concat(i);
    else d.wahl = d.wahl.includes(i) ? [] : [i];
    chipsMarkieren(el.closest(".fo-chips"), d.wahl);
    vermutungSicherheitZuruecksetzen(t); aenderung(t);
  };
  BIE.actions["fo-verm-baustein"] = el => {
    const t = aufgabenByNr[el.dataset.nr], cfg = cfgOf(t) || {}, d = dt(t, true), ta = document.getElementById("fo-sat-" + el.dataset.nr);
    if (!d || d.fest || !ta) return;
    const b = baustein(liste(cfg.begruendung)[parseInt(el.dataset.i, 10)]);   // auch ohne Vortext: „weil “ steht dann am Anfang des Feldes (bei gewählter Option folgt es auf sie)
    ta.value = (ta.value.trim() ? ta.value.replace(/\s+$/, "") + (/[.,;!?]$/.test(ta.value.trim()) ? " " : ", ") : "") + b + " ";
    ta.dispatchEvent(new Event("input", { bubbles: true })); ta.focus();
  };
  function vermutungPruefen(t) {
    const cfg = cfgOf(t) || {}, d = dt(t, true), g = vermutungGueltig(cfg, d.wahl, d.satz);
    if (g.ok) return true;
    showFb(t.nr, "err", g.grund === "wahl" ? "⚠️ Tippe zuerst eine Möglichkeit an." : `⚠️ Schreibe noch ein bisschen mehr zu deiner Vermutung (mindestens ${g.min} Zeichen).`);
    return false;
  }
  BIE.actions["fo-verm-sicher"] = el => {
    const t = aufgabenByNr[el.dataset.nr]; if (!vermutungPruefen(t)) return;
    rtVon(t).sicher = true;
    const k = document.getElementById("fo-vk-" + t.nr); if (k) k.innerHTML = vermutungKnoepfe(t);
    showFb(t.nr, "info", "🔒 Willst du deine Vermutung jetzt festhalten? Danach kannst du sie nicht mehr ändern.");
  };
  BIE.actions["fo-verm-aendern"] = el => vermutungSicherheitZuruecksetzen(aufgabenByNr[el.dataset.nr]);
  function vermutungFesthalten(t, demo) {
    const cfg = cfgOf(t) || {}, d = dt(t, true);
    if (demo) { d.wahl = liste(cfg.optionen).length ? [0] : []; d.satz = (cfg.frei || cfg.satzanfang) ? "… (Beispiel im Prüfmodus)" : ""; }
    else if (!vermutungPruefen(t)) return;
    const x = vermutungTexte(cfg, d.wahl, d.satz);
    d.fest = true; d.text = x.text || demoVermutung(t); d.antwort = x.antwort; d.optionen = x.optionen;
    rtVon(t).sicher = false;
    neuZeichnen(t); sperreNiveau(t);
    sendAntwort(t.nr, "vermutung", x.antwort, null, `${t.titel}`);
    showFb(t.nr, "ok", "✅ Deine Vermutung ist festgehalten. Jetzt kannst du forschen und herausfinden, ob sie stimmt.");
    markComplete(t.nr); aenderung(t);
    pruefenAktualisieren(t.id);
  }
  BIE.actions["fo-verm-fest"] = el => vermutungFesthalten(aufgabenByNr[el.dataset.nr], false);
  BIE.actions["fo-verm-demo"] = el => vermutungFesthalten(aufgabenByNr[el.dataset.nr], true);
  // Eine festgehaltene Vermutung bleibt – auch das Niveau lässt sich dann nicht mehr ändern
  function sperreNiveau(t) { const s = $(".niveau-select", card(t.nr)); if (s) { const d = D[nrKey(t)]; s.disabled = !!(d && d.fest); } }
  document.addEventListener("input", e => {
    const el = e.target; if (!el.dataset || el.dataset.foInput !== "verm") return;
    const t = aufgabenByNr[el.dataset.nr], cfg = t && cfgOf(t), d = t && dt(t, true); if (!d || d.fest) return;
    d.satz = el.value.slice(0, 2000);
    const z = document.getElementById("fo-zaehl-" + t.nr); if (z) { z.textContent = `${eigeneLaenge(cfg, d.satz)} Zeichen · mindestens ${vermutungMin(cfg)}`; z.classList.toggle("ok", eigeneLaenge(cfg, d.satz) >= vermutungMin(cfg)); }
    vermutungSicherheitZuruecksetzen(t); aenderung(t);
  });

  // ═══ pruefen ═══════════════════════════════════════════════════════════════════════════════════
  // Die Karten „Vermutung prüfen“ zeigen die Vermutung der verknüpften Station; wird sie festgehalten, ziehen sie nach.
  function pruefenAktualisieren(vermutungId) {
    alleAufgaben().filter(a => a.typ === "pruefen" && a.vermutung === vermutungId).forEach(a => { if (body(a.nr)) neuZeichnen(a); });
  }
  const pruefenFertigVoraussetzung = (cfg, d) => d.erk.ok !== null && (!cfg.beleg || d.beleg.ok !== null) && (!cfg.satz || d.satz.trim().length >= (cfg.satz.min || 40));
  function optionsKnoepfe(nr, aktion, ops, falsch, okIdx) {
    return `<div class="mc-options fo-optionen" role="group">${ops.map((o, i) => {
      const gesperrt = okIdx !== null || falsch.includes(i);
      const kl = okIdx === i ? " correct" : falsch.includes(i) ? " incorrect" : "";
      return `<button class="mc-btn${kl}${PRUEF && o.ok ? " fo-loesung" : ""}" type="button" data-action="${aktion}" data-nr="${nr}" data-i="${i}"${gesperrt && !PRUEF ? " disabled" : ""}>${esc(o.t)}</button>`;
    }).join("")}</div>`;
  }
  function pruefenInner(t) {
    const cfg = cfgOf(t) || {}, nr = t.nr, d = dt(t, true), erk = cfg.erkenntnis;
    if (!erk || !liste(erk.optionen).length) return fehlHinweis;
    const vt = vermutungTextFuer(t.vermutung);
    const verm = vt ? `<div class="fo-verm-box"><span class="eyebrow">Deine Vermutung war</span><blockquote class="fo-zitat">${esc(vt)}</blockquote></div>`
      : `<div class="fo-verm-box fo-leer"><p>Du hast noch keine Vermutung festgehalten. Das ist nicht schlimm – du kannst trotzdem herausfinden, was stimmt.</p></div>`;
    const quelle = t.quelle ? `<p class="fo-quelle">🔎 ${esc(t.quelle)}</p>` : "";
    let h = `${verm}${quelle}
      <p class="task-question">Wie passt deine Vermutung zu dem, was du herausgefunden hast?</p>
      <div class="fo-chips" role="group" aria-label="Meine Einschätzung">${chips(`data-action="fo-pr-einsch" data-nr="${nr}"`, EINSCHAETZUNG, d.einsch === null ? [] : [d.einsch], "", d.fertig)}</div>
      <p class="hint">Alle Antworten sind in Ordnung. Auch Forscherinnen und Forscher irren sich manchmal.</p>`;
    if (d.einsch !== null || PRUEF) {
      h += `<div class="fo-stufe"><p class="task-question">${esc(erk.frage || "Was hast du herausgefunden?")}</p>${optionsKnoepfe(nr, "fo-pr-erk", erk.optionen, d.erk.falsch, d.erk.ok)}</div>`;
    }
    if (cfg.beleg && (d.erk.ok !== null || PRUEF)) {
      h += `<div class="fo-stufe"><p class="task-question">${esc(cfg.beleg.frage || "Woher weißt du das?")}</p>${optionsKnoepfe(nr, "fo-pr-beleg", liste(cfg.beleg.optionen), d.beleg.falsch, d.beleg.ok)}</div>`;
    }
    if (cfg.satz && (d.erk.ok !== null || PRUEF)) {
      const min = cfg.satz.min || 40;
      h += `<div class="fo-stufe"><label class="field-label" for="fo-ps-${nr}">${esc(cfg.satz.anfang || "Ich habe herausgefunden, dass …")}</label>
        <textarea id="fo-ps-${nr}" class="fo-text" rows="4" data-fo-input="pr-satz" data-nr="${nr}" placeholder="Schreibe hier weiter …"${d.fertig ? " disabled" : ""}>${esc(d.satz)}</textarea>
        <div class="text-meta"><span id="fo-pszaehl-${nr}">${d.satz.trim().length} Zeichen · mindestens ${min}</span></div>
        ${d.fertig ? "" : `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="fo-pr-satz" data-nr="${nr}">✅ Erkenntnis festhalten</button></div>`}</div>`;
    }
    if (d.fertig || (PRUEF && t.erkenntnis)) {
      h += `<div class="fo-merke"><span class="eyebrow">📌 Merke</span><p>${esc(t.erkenntnis || "")}</p><p class="hint">Dieser Satz steht jetzt in deinem Forscherbuch.</p></div>`;
    }
    return h + loesungKasten("<strong>Prüfmodus:</strong> Die richtigen Antworten sind grün umrandet. Die Vermutung erscheint hier als Beispiel.");
  }
  function pruefenAbschliessen(t, d) {
    const cfg = cfgOf(t) || {}, erk = cfg.erkenntnis;
    d.fertig = true;
    const ops = liste(erk.optionen);
    const teile = [`Vermutung: ${vermutungTextFuer(t.vermutung) || "nicht festgehalten"}`, `Einschätzung: ${EINSCH_KURZ[d.einsch === null ? 0 : d.einsch]}`,
      `Erkenntnis: ${text(ops[d.erk.ok] && ops[d.erk.ok].t, 150)} ✅`];
    if (cfg.beleg) teile.push(`Beleg: ${text(liste(cfg.beleg.optionen)[d.beleg.ok] && liste(cfg.beleg.optionen)[d.beleg.ok].t, 100)} ✅`);
    if (cfg.satz) teile.push(`Mein Satz: ${d.satz.trim()}`);
    sendAntwort(t.nr, "pruefen", teile.join(" · "), null, t.titel);   // Zusammenfassung ohne Bewertung (die Schritte davor sind schon bewertet)
    neuZeichnen(t);
    showFb(t.nr, "ok", "✅ Gut gemacht! Deine Erkenntnis steht jetzt in deinem Forscherbuch.");
    markComplete(t.nr); aenderung(t);
  }
  function pruefenWeiter(t, d) {
    const cfg = cfgOf(t) || {};
    if (cfg.satz) { neuZeichnen(t); return; }                       // C: erst den eigenen Satz festhalten
    if (cfg.beleg && d.beleg.ok === null) { neuZeichnen(t); return; }
    pruefenAbschliessen(t, d);
  }
  BIE.actions["fo-pr-einsch"] = el => {
    const t = aufgabenByNr[el.dataset.nr], d = dt(t, true), i = parseInt(el.dataset.i, 10); if (!d || d.fertig) return;
    d.einsch = i; neuZeichnen(t); aenderung(t);
    sendAntwort(t.nr, "pruefen", `Einschätzung meiner Vermutung: ${EINSCH_KURZ[i]}`, null, t.titel);
  };
  function pruefenWahl(el, art) {
    const t = aufgabenByNr[el.dataset.nr], cfg = cfgOf(t) || {}, d = dt(t, true), i = parseInt(el.dataset.i, 10); if (!d || d.fertig) return;
    const q = art === "erk" ? cfg.erkenntnis : cfg.beleg, z = d[art === "erk" ? "erk" : "beleg"], o = liste(q.optionen)[i];
    if (!o || z.ok !== null || z.falsch.includes(i)) return;
    const was = art === "erk" ? "Erkenntnis" : "Beleg";
    if (o.ok) {
      z.ok = i;
      sendAntwort(t.nr, "pruefen", `${was}: ${o.t} ✅ (${z.falsch.length + 1}. Versuch)`, true, q.frage || t.titel);
      aenderung(t); clearFb(t.nr); pruefenWeiter(t, d);
    } else {
      z.falsch.push(i);
      sendAntwort(t.nr, "pruefen", `${was}: ${o.t} ❌`, false, q.frage || t.titel);
      neuZeichnen(t); aenderung(t);
      // Eigene Texte je Stufe: bei der Beleg-Frage nie „was du beobachtet hast“; `fehltext` an der Frage überschreibt den Standard
      const standard = art === "erk" ? "Das passt noch nicht zu dem, was du beobachtet hast." : "Dieser Beleg passt noch nicht.";
      const quelle = t.quelle ? " Schau noch einmal genau hin – der gelbe Hinweis oben hilft dir." : " Schau noch einmal genau hin.";
      showFb(t.nr, "err", `❌ ${esc(typeof q.fehltext === "string" && q.fehltext.trim() ? q.fehltext.trim() : standard)}${quelle}${q.hinweis && z.falsch.length >= 2 ? `<br>💡 ${esc(q.hinweis)}` : ""}`);
    }
  }
  BIE.actions["fo-pr-erk"] = el => pruefenWahl(el, "erk");
  BIE.actions["fo-pr-beleg"] = el => pruefenWahl(el, "beleg");
  BIE.actions["fo-pr-satz"] = el => {
    const t = aufgabenByNr[el.dataset.nr], cfg = cfgOf(t) || {}, d = dt(t, true), min = (cfg.satz && cfg.satz.min) || 40; if (!d || d.fertig) return;
    if (d.satz.trim().length < min) { showFb(t.nr, "err", `⚠️ Schreibe noch ein bisschen mehr (mindestens ${min} Zeichen).`); return; }
    if (cfg.beleg && d.beleg.ok === null) { showFb(t.nr, "err", "⚠️ Wähle zuerst oben aus, woher du das weißt."); return; }
    pruefenAbschliessen(t, d);
  };
  document.addEventListener("input", e => {
    const el = e.target; if (!el.dataset || el.dataset.foInput !== "pr-satz") return;
    const t = aufgabenByNr[el.dataset.nr], cfg = t && cfgOf(t), d = t && dt(t, true); if (!d || d.fertig) return;
    d.satz = el.value.slice(0, 2000);
    const min = (cfg.satz && cfg.satz.min) || 40, z = document.getElementById("fo-pszaehl-" + t.nr);
    if (z) { z.textContent = `${d.satz.trim().length} Zeichen · mindestens ${min}`; z.classList.toggle("ok", d.satz.trim().length >= min); }
    aenderung(t);
  });

  // ═══ protokoll ═════════════════════════════════════════════════════════════════════════════════
  function zeilenMeldung(row, z) {
    // `okText` ersetzt „Das stimmt!“ (z. B. bei einer Vermutungs-Textzeile: „Danke, deine Vermutung ist notiert.“ – eine Vermutung stimmt nicht oder nicht)
    if (z.ok) return `<span class="fo-ok">✅ ${typeof row.okText === "string" && row.okText.trim() ? esc(row.okText.trim()) : "Das stimmt!"}${row.erklaerung ? " " + esc(row.erklaerung) : ""}</span>`;
    if (!z.g) return "";
    const art = row.art || "zahl";
    const keineZahl = art === "zahl" && parseZahl(z.w) === null;                    // gar keine Zahl eingegeben: Hinweis zum Format
    const basis = typeof row.fehlertext === "string" && row.fehlertext.trim() ? esc(row.fehlertext.trim())
      : keineZahl ? "Schreibe eine Zahl, zum Beispiel 12." : art === "zahl" ? "Noch nicht ganz. Zähle noch einmal genau nach." : art === "mehrfach" ? "Noch nicht ganz. Prüfe jede Antwort einzeln." : art === "text" ? "Schreibe einen ganzen Satz." : "Noch nicht ganz. Schau noch einmal genau hin.";
    let s = `<span class="fo-err">❌ ${basis}</span>`;
    if (z.f >= 2 && row.hinweis) s += `<br><span class="fo-tipp">💡 ${esc(row.hinweis)}</span>`;
    if (z.f >= 3) s += row.hinweis2 ? `<br><span class="fo-tipp">💡 ${esc(row.hinweis2)}</span>` : (row.modell ? `<br><span class="fo-tipp">💡 Sieh dir die Stelle im Modell noch einmal an.</span>` : "");
    return s;
  }
  function zeileHtml(t, row, i, d) {
    const nr = t.nr, z = d.z[i], art = ZEILENARTEN.includes(row.art) ? row.art : "zahl", gesperrt = z.ok;
    const id = `fo-z-${nr}-${i}`, ops = liste(row.optionen);
    let ctl = "";
    if (art === "zahl") {
      ctl = `<div class="fo-zahl"><button type="button" class="fo-pm" data-action="fo-zahl" data-nr="${nr}" data-z="${i}" data-d="-1" aria-label="eins weniger"${gesperrt ? " disabled" : ""}>−</button>
        <input id="${id}" class="fo-zahl-feld" type="text" inputmode="decimal" autocomplete="off" value="${esc(z.w == null ? "" : z.w)}" data-fo-input="zahl" data-nr="${nr}" data-z="${i}" aria-label="${esc(row.frage)}"${gesperrt ? " disabled" : ""}>
        <button type="button" class="fo-pm" data-action="fo-zahl" data-nr="${nr}" data-z="${i}" data-d="1" aria-label="eins mehr"${gesperrt ? " disabled" : ""}>+</button>
        ${row.einheit ? `<span class="fo-einheit">${esc(row.einheit)}</span>` : ""}</div>`;
    } else if (art === "wahl" || art === "mehrfach") {
      ctl = `<div class="fo-chips" role="group" aria-label="${esc(row.frage)}">${chips(`data-action="fo-zeile-wahl" data-nr="${nr}" data-z="${i}"`, ops, art === "wahl" ? (ganz(z.w) ? [z.w] : []) : liste(z.w), "", gesperrt)}</div>${art === "mehrfach" ? `<p class="hint">Du darfst mehrere antippen.</p>` : ""}`;
    } else {
      ctl = `${row.satzanfang ? `<label class="field-label" for="${id}">${esc(row.satzanfang)}</label>` : ""}<textarea id="${id}" class="fo-text fo-text-kurz" rows="2" data-fo-input="ztext" data-nr="${nr}" data-z="${i}" placeholder="Schreibe hier …" aria-label="${esc(row.frage)}"${gesperrt ? " disabled" : ""}>${esc(z.w == null ? "" : z.w)}</textarea>`;
    }
    const loes = !PRUEF ? "" : `<div class="pruef-loesung fo-pruef">🔍 Lösung: ${art === "zahl" ? `${esc(row.loesung)}${row.toleranz ? ` (± ${esc(row.toleranz)})` : ""}` : art === "wahl" ? esc(ops[row.loesung]) : art === "mehrfach" ? liste(row.loesung).map(k => esc(ops[k])).join(", ") : `ein Satz mit mindestens ${row.min || 6} Zeichen`}</div>`;
    return `<div class="fo-zeile${z.ok ? " is-ok" : z.g ? " is-falsch" : ""}" id="fo-zeile-${nr}-${i}">
      <div class="fo-frage"><label class="fo-frage-text" for="${id}">${esc(row.frage)}</label>${modellKnopf(nr, row.modell, i, z.f >= 3 && !z.ok)}</div>
      ${ctl}
      <div class="fo-zeile-fb" id="fo-zfb-${nr}-${i}" role="status" aria-live="polite">${zeilenMeldung(row, z)}</div>
      ${z.ok ? "" : `<div class="btn-row fo-zeile-knopf"><button class="btn btn-outline btn-sm" type="button" data-action="fo-zeile-pruefen" data-nr="${nr}" data-z="${i}">✅ Prüfen</button></div>`}
      ${loes}</div>`;
  }
  // Schluss-Satz des Forscherbogens: A Bausteine antippen, B Satzanfang, C frei
  function schlussHtml(t, cfg, d) {
    const sc = cfg.schluss, nr = t.nr, s = d.schluss;
    if (!sc) return "";
    const alle = d.z.every(z => z.ok);
    if (!alle && !PRUEF) return "";
    const bs = liste(sc.bausteine);
    let h = `<div class="fo-schluss"><span class="eyebrow">Mein Satz${sc.pflicht ? "" : " (freiwillig)"}</span>`;
    if (bs.length) {
      h += `<p class="task-question">${esc(sc.anfang || "Ich habe beobachtet, dass …")}</p><div class="fo-chips" role="group" aria-label="Satzbausteine">${chips(`data-action="fo-schluss-wahl" data-nr="${nr}"`, bs.map(b => (typeof b === "string" ? b : b.t)), s.wahl === null ? [] : [s.wahl], "", s.fertig)}</div>`;
    } else {
      h += `<label class="field-label" for="fo-sc-${nr}">${esc(sc.anfang || "Das habe ich beobachtet:")}</label>
        <textarea id="fo-sc-${nr}" class="fo-text" rows="3" data-fo-input="schluss" data-nr="${nr}" placeholder="Schreibe hier weiter …"${s.fertig ? " disabled" : ""}>${esc(s.satz)}</textarea>
        <div class="text-meta"><span id="fo-sczaehl-${nr}">${s.satz.trim().length} Zeichen · mindestens ${sc.min || 20}</span></div>`;
    }
    return h + (s.fertig ? `<p class="fo-ok">✅ Dein Satz ist gespeichert.</p>` : `<div class="btn-row"><button class="btn btn-primary btn-sm" type="button" data-action="fo-schluss-fest" data-nr="${nr}">💾 Satz speichern</button></div>`) + `</div>`;
  }
  // Alle Zeilen richtig (und der Schluss-Satz, wenn schluss.pflicht gesetzt ist) – aus dem Zustand der Karte
  const protokollFertig = (cfg, d) => d.z.every(z => z.ok) && (!(cfg.schluss && cfg.schluss.pflicht) || d.schluss.fertig);
  function protokollInner(t) {
    const cfg = cfgOf(t) || {}, zeilen = liste(cfg.zeilen), nr = t.nr;
    if (!zeilen.length) return fehlHinweis;
    const d = dt(t, true), ok = d.z.filter(z => z.ok).length;
    const merke = (protokollFertig(cfg, d) || PRUEF) && t.erkenntnis ? `<div class="fo-merke"><span class="eyebrow">📌 Merke</span><p>${esc(t.erkenntnis)}</p><p class="hint">Dieser Satz steht jetzt in deinem Forscherbuch.</p></div>` : "";
    return `${cfg.auftrag || t.auftrag ? `<p class="task-question">${esc(cfg.auftrag || t.auftrag)}</p>` : ""}
      <div class="fo-fortschritt" role="status">${ok} von ${zeilen.length} Zeilen geschafft <span class="lese-dots" aria-hidden="true">${zeilen.map((r, i) => `<i class="${d.z[i].ok ? "done" : ""}"></i>`).join("")}</span></div>
      <div class="fo-zeilen">${zeilen.map((row, i) => zeileHtml(t, row, i, d)).join("")}</div>
      ${ok < zeilen.length ? `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="fo-alle-pruefen" data-nr="${nr}">✅ Alle Zeilen prüfen</button></div>` : ""}
      ${schlussHtml(t, cfg, d)}${merke}`;
  }
  // T3 „Raten verhindern“: Die ERSTE wirksame Prüfung zählt nur („x von y stimmen“) – nichts wird gefärbt oder gesperrt. Gefärbt, gesperrt und mit Hinweisen
  // wird ab der zweiten wirksamen Prüfung (= nach einer Änderung). cfg.sofortFaerben: true schaltet das alte Verhalten ein.
  // Ein erneutes Prüfen ohne Änderung zählt nicht (kein Fehlversuch, kein Protokolleintrag).
  const faerbtSchon = (cfg, d) => !!cfg.sofortFaerben || d.pr >= 1;
  const NICHT_GEAENDERT = "👆 Du hast seit dem letzten Prüfen nichts geändert. Ändere zuerst etwas, dann prüfe noch einmal.";
  // Eine Zeile prüfen. Rückgabe: "leer" | "ok" | "falsch" | "gleich". faerben: Zeile färben/sperren; sonst nur zählen.
  function zeilePruefen(t, i, faerben) {
    const cfg = cfgOf(t) || {}, row = liste(cfg.zeilen)[i], d = dt(t, true), z = d && d.z[i];
    if (!row || !z || z.ok) return "ok";
    if (faerben && z.g) return "gleich";                                  // schon als falsch gefärbt und seitdem nicht geändert
    const r = zeileAuswerten(row, z.w);
    if (r.leer) return "leer";
    if (faerben) { z.g = !r.ok; z.ok = r.ok; }
    if (!r.ok) z.f++;
    sendAntwort(t.nr, "protokoll", zeilenText(row, z.w, r.ok), r.ok, row.frage);
    return r.ok ? "ok" : "falsch";
  }
  function protokollNachPruefung(t, meldung) {
    const cfg = cfgOf(t) || {}, d = dt(t, true), alle = d.z.every(z => z.ok), pflichtSchluss = cfg.schluss && cfg.schluss.pflicht;
    neuZeichnen(t); aenderung(t);
    if (alle && (!pflichtSchluss || d.schluss.fertig)) {
      if (!state.completed.has(String(t.nr))) { showFb(t.nr, "ok", "✅ Alle Zeilen stimmen. Gut beobachtet!" + (cfg.schluss && !d.schluss.fertig ? " Schreibe jetzt noch deinen Satz dazu." : "")); markComplete(t.nr); neuZeichnen(t); }
    } else if (alle) showFb(t.nr, "info", "✅ Alle Zeilen stimmen. Schreibe jetzt noch deinen Satz dazu, dann bist du fertig.");
    else if (meldung) showFb(t.nr, meldung.art, meldung.text);
  }
  // Prüfen im Forscherbogen. nurZeile: Zeilen-Nummer (Knopf einer Zeile, Enter im Zahlfeld) oder null (alle Zeilen).
  function protokollPruefen(t, nurZeile) {
    const cfg = cfgOf(t) || {}, d = dt(t, true), zeilen = liste(cfg.zeilen), sig = () => JSON.stringify(d.z.map(z => z.w));
    let faerben = faerbtSchon(cfg, d);
    // Zwischen der ersten (zählenden) und der zweiten (färbenden) Prüfung muss sich etwas geändert haben; später schützt z.g jede schon gefärbte, unveränderte Zeile
    if (!cfg.sofortFaerben && d.pr === 1 && d.sig === sig()) { showFb(t.nr, "info", NICHT_GEAENDERT); return; }
    if (!faerben) {
      // Erste wirksame Prüfung: egal welcher Knopf – alle ausgefüllten Zeilen werden gezählt, nichts wird verraten
      const auswertung = zeilen.map((row, i) => (d.z[i].ok ? { leer: false, ok: true } : zeileAuswerten(row, d.z[i].w)));
      if (auswertung.every(r => r.leer)) { showFb(t.nr, "err", "⚠️ Trage zuerst etwas ein."); return; }
      faerben = auswertung.every(r => !r.leer && r.ok);                   // alles ausgefüllt und richtig: sofort abschließen
      if (!faerben) {
        let leer = 0, richtig = 0, gefuellt = 0;
        zeilen.forEach((row, i) => { const r = zeilePruefen(t, i, false); if (r === "leer") leer++; else { gefuellt++; if (r === "ok") richtig++; } });
        d.pr++; d.sig = sig();
        clearFb(t.nr);
        protokollNachPruefung(t, { art: "err", text: `❌ ${richtig} von ${gefuellt} ausgefüllten Zeilen ${richtig === 1 ? "stimmt" : "stimmen"}.${leer ? ` Bei ${leer} Zeile${leer > 1 ? "n" : ""} fehlt noch deine Eingabe.` : ""} Welche das sind, findest du selbst heraus: Sieh noch einmal genau hin, ändere, was nicht passt, und prüfe dann noch einmal.` });
        return;
      }
    }
    let leer = 0, falsch = 0, gleich = 0, geprueft = 0;
    zeilen.forEach((row, i) => {
      if ((nurZeile !== null && nurZeile !== i) || d.z[i].ok) return;
      const r = zeilePruefen(t, i, true);
      if (r === "leer") leer++; else if (r === "gleich") gleich++; else { geprueft++; if (r === "falsch") falsch++; }
    });
    if (nurZeile !== null) {
      if (leer) { showFb(t.nr, "err", "⚠️ Trage zuerst etwas ein."); return; }
      if (gleich && !geprueft) { showFb(t.nr, "info", NICHT_GEAENDERT); return; }
    } else if (gleich && !geprueft && !leer) { showFb(t.nr, "info", NICHT_GEAENDERT); return; }
    if (geprueft) { d.pr++; d.sig = sig(); }
    const meldung = nurZeile !== null ? null : leer ? { art: "err", text: `⚠️ Bei ${leer} Zeile${leer > 1 ? "n" : ""} fehlt noch deine Eingabe.${falsch ? ` ${falsch} Zeile${falsch > 1 ? "n stimmen" : " stimmt"} noch nicht (rot).` : ""}` }
      : falsch ? { art: "err", text: `❌ ${falsch} Zeile${falsch > 1 ? "n stimmen" : " stimmt"} noch nicht – sie sind rot. Schau noch einmal genau hin.` } : null;
    clearFb(t.nr); protokollNachPruefung(t, meldung);
  }
  BIE.actions["fo-zeile-pruefen"] = el => protokollPruefen(aufgabenByNr[el.dataset.nr], parseInt(el.dataset.z, 10));
  BIE.actions["fo-alle-pruefen"] = el => protokollPruefen(aufgabenByNr[el.dataset.nr], null);
  function zeileAendern(t, i, w) {
    const d = dt(t, true), z = d && d.z[i]; if (!z || z.ok) return;
    z.w = w; z.g = false;
    const k = document.getElementById(`fo-zfb-${t.nr}-${i}`); if (k) k.innerHTML = "";
    const zeile = document.getElementById(`fo-zeile-${t.nr}-${i}`); if (zeile) zeile.classList.remove("is-falsch");
    aenderung(t);
  }
  BIE.actions["fo-zahl"] = el => {
    const t = aufgabenByNr[el.dataset.nr], i = parseInt(el.dataset.z, 10), cfg = cfgOf(t) || {}, row = liste(cfg.zeilen)[i], d = dt(t, true); if (!row || !d || d.z[i].ok) return;
    const schritt = Number(row.schritt) || 1, jetzt = parseZahl(d.z[i].w);
    let n = (jetzt === null ? 0 : jetzt) + parseInt(el.dataset.d, 10) * schritt;
    if (row.min === undefined && n < 0) n = 0;
    n = Math.round(n * 1000) / 1000;
    const feld = document.getElementById(`fo-z-${t.nr}-${i}`); if (feld) feld.value = String(n);
    zeileAendern(t, i, String(n));
  };
  BIE.actions["fo-zeile-wahl"] = el => {
    const t = aufgabenByNr[el.dataset.nr], i = parseInt(el.dataset.z, 10), cfg = cfgOf(t) || {}, row = liste(cfg.zeilen)[i], d = dt(t, true), k = parseInt(el.dataset.i, 10);
    if (!row || !d || d.z[i].ok) return;
    let w;
    if (row.art === "mehrfach") { const alt = liste(d.z[i].w); w = alt.includes(k) ? alt.filter(x => x !== k) : alt.concat(k); }
    else w = d.z[i].w === k ? null : k;
    chipsMarkieren(el.closest(".fo-chips"), row.art === "mehrfach" ? w : (w === null ? [] : [w]));
    zeileAendern(t, i, w);
  };
  function schlussSpeichern(t, cfg, d) {
    const sc = cfg.schluss, s = d.schluss, bs = liste(sc.bausteine);
    let satz;
    if (bs.length) {
      if (s.wahl === null) { showFb(t.nr, "err", "⚠️ Tippe zuerst einen Satzbaustein an."); return; }
      const b = bs[s.wahl]; if (typeof b === "object" && b.ok === false) { showFb(t.nr, "err", `❌ ${b.rueckmeldung || "Das hast du nicht beobachtet. Schau noch einmal auf deine Zeilen."}`); return; }
      satz = satzGanz(sc.anfang, typeof b === "string" ? b : b.t);
    } else {
      if (s.satz.trim().length < (sc.min || 20)) { showFb(t.nr, "err", `⚠️ Schreibe noch ein bisschen mehr (mindestens ${sc.min || 20} Zeichen).`); return; }
      satz = satzGanz(sc.anfang, s.satz);
    }
    s.fertig = true; sendAntwort(t.nr, "protokoll", `Mein Satz: ${satz}`, null, t.titel);
    clearFb(t.nr); protokollNachPruefung(t, null);
  }
  BIE.actions["fo-schluss-wahl"] = el => {
    const t = aufgabenByNr[el.dataset.nr], d = dt(t, true), k = parseInt(el.dataset.i, 10); if (!d || d.schluss.fertig) return;
    d.schluss.wahl = d.schluss.wahl === k ? null : k;
    chipsMarkieren(el.closest(".fo-chips"), d.schluss.wahl === null ? [] : [d.schluss.wahl]); aenderung(t);
  };
  BIE.actions["fo-schluss-fest"] = el => {
    const t = aufgabenByNr[el.dataset.nr], d = dt(t, true);
    if (!PRUEF && !d.z.every(z => z.ok)) { showFb(t.nr, "info", "👆 Prüfe zuerst alle Zeilen. Danach schreibst du deinen Satz."); return; }
    schlussSpeichern(t, cfgOf(t) || {}, d);
  };
  document.addEventListener("input", e => {
    const el = e.target, a = el.dataset && el.dataset.foInput; if (!a || !["zahl", "ztext", "schluss"].includes(a)) return;
    const t = aufgabenByNr[el.dataset.nr]; if (!t) return;
    if (a === "schluss") {
      const d = dt(t, true), sc = (cfgOf(t) || {}).schluss || {}; if (!d || d.schluss.fertig) return;
      d.schluss.satz = el.value.slice(0, 2000);
      const z = document.getElementById("fo-sczaehl-" + t.nr); if (z) { z.textContent = `${d.schluss.satz.trim().length} Zeichen · mindestens ${sc.min || 20}`; z.classList.toggle("ok", d.schluss.satz.trim().length >= (sc.min || 20)); }
      aenderung(t); return;
    }
    zeileAendern(t, parseInt(el.dataset.z, 10), el.value.slice(0, a === "zahl" ? 20 : 500));
  });
  document.addEventListener("keydown", e => {
    const el = e.target;
    if (e.key === "Enter" && el.dataset && el.dataset.foInput === "zahl") { e.preventDefault(); BIE.actions["fo-zeile-pruefen"]({ dataset: { nr: el.dataset.nr, z: el.dataset.z } }); }
  });

  // ═══ tabelle ═══════════════════════════════════════════════════════════════════════════════════
  function tabelleInner(t) {
    const cfg = cfgOf(t) || {}, zeilen = liste(cfg.zeilen), sp = liste(cfg.spalten), nr = t.nr;
    if (!zeilen.length || !sp.length) return fehlHinweis;
    const d = dt(t, true), fertig = d.ok.every(r => r.every(Boolean));        // alle Zellen geprüft und richtig (nicht state.completed: Niveauwechsel setzt die Karte zurück)
    // Spaltenbild: über dem Namen, nur zur Anzeige (kein Tippziel); der Name bleibt sichtbar. Im Stapelmodus (schmal) steht es im Feld-Etikett.
    const spImg = (s, klasse) => { const b = spaltenBild(s); return b ? `<img class="${klasse}" src="${esc(bildQuelle(b.src))}" alt="${esc(b.alt)}" loading="lazy" decoding="async">` : ""; };
    const kopf = `<div class="fo-tzeile fo-tkopf" role="row"><span role="columnheader" class="fo-leer-zelle"></span>${sp.map(s => `<span role="columnheader" class="fo-spalte${spaltenBild(s) ? " hat-bild" : ""}">${spImg(s, "fo-sp-bild")}<span class="fo-sp-name">${esc(spaltenName(s))}</span></span>`).join("")}</div>`;
    const reihen = zeilen.map((z, i) => {
      const zellen = sp.map((s, j) => {
        const w = d.a[i][j], gut = d.ok[i][j], schlecht = d.x[i][j];
        const ops = liste(z.optionen), sn = spaltenName(s);
        return `<div role="cell" class="fo-zelle${gut ? " is-ok" : schlecht ? " is-falsch" : ""}" data-label="${esc(sn)}">
          <span class="fo-zelle-label">${spImg(s, "fo-zl-bild")}<span>${esc(sn)}</span></span>
          <div class="fo-chips" role="group" aria-label="${esc(z.merkmal)} – ${esc(sn)}">${ops.map((o, k) => `<button type="button" class="fo-chip${w === k ? " is-on" : ""}${PRUEF && liste(z.loesung)[j] === k ? " fo-loesung" : ""}" aria-pressed="${w === k}" data-action="fo-zelle" data-nr="${nr}" data-z="${i}" data-s="${j}" data-i="${k}"${gut ? " disabled" : ""}>${esc(o)}</button>`).join("")}</div></div>`;
      }).join("");
      const fehlerHinweis = d.f[i] >= 2 && z.hinweis && d.x[i].some(Boolean) ? `<p class="fo-tipp">💡 ${esc(z.hinweis)}${d.f[i] >= 3 && z.hinweis2 ? `<br>💡 ${esc(z.hinweis2)}` : ""}</p>` : "";
      const zb = zeilenBild(z);
      const zeilenImg = zb ? `<button type="button" class="bild-zoom fo-zeilenbild" data-action="bild-open" aria-label="Bild vergrößern: ${esc(zb.alt)}"><img src="${esc(bildQuelle(zb.src))}" alt="${esc(zb.alt)}" loading="lazy" decoding="async"></button>` : "";
      return `<div class="fo-tzeile${zb ? " hat-bild" : ""}" role="row"><div role="rowheader" class="fo-merkmal">${zeilenImg}<span>${esc(z.merkmal)}</span>${modellKnopf(nr, z.modell, i, d.f[i] >= 3 && d.ok[i].some(x => !x) && !fertig)}</div>${zellen}${fehlerHinweis ? `<div class="fo-zeilenhinweis">${fehlerHinweis}</div>` : ""}</div>`;
    }).join("");
    const merke = (fertig || PRUEF) && t.erkenntnis ? `<div class="fo-merke"><span class="eyebrow">📌 Merke</span><p>${esc(t.erkenntnis)}</p><p class="hint">Dieser Satz steht jetzt in deinem Forscherbuch.</p></div>` : "";
    return `${cfg.auftrag || t.auftrag ? `<p class="task-question">${esc(cfg.auftrag || t.auftrag)}</p>` : ""}
      <div class="fo-tabelle${sp.some(spaltenBild) ? " hat-spaltenbild" : ""}${zeilen.some(zeilenBild) ? " hat-zeilenbild" : ""}" role="table" style="--fo-n:${sp.length}" aria-label="${esc(t.titel)}">${kopf}${reihen}</div>
      <p class="hint">${cfg.sofortFaerben || d.pr >= 1 ? "Tippe in jedem Feld eine Möglichkeit an. Richtige Felder werden grün und bleiben stehen." : "Tippe in jedem Feld eine Möglichkeit an. Beim ersten Prüfen siehst du nur, wie viele Felder stimmen – danach werden die Felder gefärbt."}</p>
      ${fertig ? "" : `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="fo-tab-pruefen" data-nr="${nr}">✅ Prüfen</button></div>`}${merke}
      ${loesungKasten("<strong>Prüfmodus:</strong> Die richtigen Chips sind grün umrandet.")}`;
  }
  BIE.actions["fo-zelle"] = el => {
    const t = aufgabenByNr[el.dataset.nr], d = dt(t, true), i = parseInt(el.dataset.z, 10), j = parseInt(el.dataset.s, 10), k = parseInt(el.dataset.i, 10);
    if (!d || d.ok[i][j]) return;
    d.a[i][j] = d.a[i][j] === k ? null : k;
    chipsMarkieren(el.closest(".fo-chips"), d.a[i][j] === null ? [] : [d.a[i][j]]);
    d.x[i][j] = false;
    const zelle = el.closest(".fo-zelle"); if (zelle) zelle.classList.remove("is-falsch");
    aenderung(t);
  };
  BIE.actions["fo-tab-pruefen"] = el => {
    const t = aufgabenByNr[el.dataset.nr], cfg = cfgOf(t) || {}, zeilen = liste(cfg.zeilen), sp = liste(cfg.spalten), d = dt(t, true);
    const r = tabelleAuswerten(d.a, zeilen, sp.length);
    if (r.leer) { showFb(t.nr, "err", `⚠️ Es ${r.leer === 1 ? "fehlt noch 1 Feld" : `fehlen noch ${r.leer} Felder`}. Tippe in jedem Feld eine Möglichkeit an.`); return; }
    // T3: erste wirksame Prüfung = nur Zählung (ohne Färbung); alles richtig oder sofortFaerben: gleich gefärbt
    const sig = JSON.stringify(d.a), faerben = !!cfg.sofortFaerben || d.pr >= 1 || r.fertig;
    if (d.sig && sig === d.sig && !r.fertig) { showFb(t.nr, "info", `${NICHT_GEAENDERT} (${r.richtig} von ${r.gesamt} Feldern stimmen.)`); return; }
    d.sig = sig; d.pr++;
    if (faerben) r.ok.forEach((reihe, i) => { reihe.forEach((x, j) => { d.ok[i][j] = x === true; d.x[i][j] = x === false; }); });
    r.ok.forEach((reihe, i) => { if (reihe.some(x => !x)) d.f[i]++; });
    sendAntwort(t.nr, "tabelle", `Tabelle: ${r.richtig} von ${r.gesamt} Feldern richtig – ${tabelleText(zeilen, sp, d.a, r.ok)}`, r.fertig, t.titel);
    clearFb(t.nr); neuZeichnen(t); aenderung(t);
    if (r.fertig) { showFb(t.nr, "ok", "✅ Die ganze Tabelle stimmt. Gut verglichen!"); markComplete(t.nr); neuZeichnen(t); }
    else if (faerben) showFb(t.nr, "err", `❌ ${r.gesamt - r.richtig} ${r.gesamt - r.richtig === 1 ? "Feld stimmt" : "Felder stimmen"} noch nicht – sie sind rot. Schau noch einmal genau hin und ändere sie.`);
    else showFb(t.nr, "err", `❌ ${r.richtig} von ${r.gesamt} Feldern stimmen. Welche das sind, findest du selbst heraus: Sieh noch einmal genau hin, ändere, was nicht passt, und prüfe dann noch einmal.`);
  };

  // ═══ bildwahl ══════════════════════════════════════════════════════════════════════════════════
  // Mehrere Runden nacheinander. Eine gelöste Runde bleibt mit ihrer Erklärung stehen, bis „Weiter“ getippt wird.
  function bildwahlInner(t) {
    const cfg = cfgOf(t) || {}, runden = liste(cfg.runden), nr = t.nr;
    if (!runden.length) return fehlHinweis;
    const d = dt(t, true), i = Math.min(d.runde, runden.length - 1), r = runden[i], geloest = !!d.ok[i];
    const fertig = d.ok.every(Boolean), letzte = i === runden.length - 1;
    const punkte = `<span class="lese-dots" aria-hidden="true">${runden.map((_, k) => `<i class="${d.ok[k] ? "done" : k === i ? "now" : ""}"></i>`).join("")}</span>`;
    const fort = runden.length === 1 ? (fertig ? `<div class="mf-fortschritt" role="status">✅ Geschafft</div>` : "")
      : `<div class="mf-fortschritt" role="status">${fertig ? `Alle ${runden.length} Runden geschafft` : `Runde ${i + 1} von ${runden.length}`} ${punkte}</div>`;
    const breite = r.breite || 900, hoehe = r.hoehe || 560;
    const bild = bildQuelle(r.bild);
    const falsch = liste(d.falsch[i]);
    const kreise = liste(r.ziele).map((z, k) => {
      const kl = geloest ? (z.ok ? " ok" : "") : falsch.includes(k) ? " falsch" : "";
      return `<g class="fo-ziel${kl}${PRUEF && z.ok && !geloest ? " fo-loesung" : ""}" data-nr="${nr}" data-i="${k}" data-r="${z.r}" role="button" tabindex="0" aria-label="Bereich ${k + 1}${kl === " ok" ? " (richtig)" : kl === " falsch" ? " (nicht richtig)" : ""}"><circle cx="${z.x}" cy="${z.y}" r="${z.r}"/><text x="${z.x}" y="${z.y}" text-anchor="middle" dominant-baseline="central" class="fo-ziel-nr" aria-hidden="true">${k + 1}</text></g>`;
    }).join("");
    const erklaerung = geloest && r.erklaerung ? `<div class="fo-merke"><span class="eyebrow">💡 Das hast du gefunden</span><p>${esc(r.erklaerung)}</p></div>` : "";
    const weiter = geloest && !letzte ? `<div class="btn-row"><button class="btn btn-primary" type="button" data-action="fo-bild-weiter" data-nr="${nr}">Weiter zu Runde ${i + 2} →</button></div>` : "";
    const abschluss = fertig && (t.erkenntnis || PRUEF) ? `<div class="fo-merke"><span class="eyebrow">📌 Merke</span><p>${esc(t.erkenntnis || "")}</p><p class="hint">Dieser Satz steht jetzt in deinem Forscherbuch.</p></div>` : "";
    const auftrag = cfg.auftrag || t.auftrag;       // Aufgabentext (freiwillig, je Niveau oder an der Aufgabe): steht über jeder Runde
    return `${auftrag ? `<p class="task-question fo-auftrag">${esc(auftrag)}</p>` : ""}${fort}<p class="task-question">${esc(r.frage || "Tippe auf die richtige Stelle im Bild.")}</p>
      <div class="map-wrap fo-bild-wrap"><svg viewBox="0 0 ${breite} ${hoehe}" class="map-svg fo-bild" data-action="fo-bild" data-nr="${nr}" xmlns="http://www.w3.org/2000/svg" role="group" aria-label="${esc(r.frage || t.titel)} – Bild mit ${liste(r.ziele).length} antippbaren Bereichen">
        <image href="${esc(bild)}" x="0" y="0" width="${breite}" height="${hoehe}"/>${kreise}</svg></div>
      ${geloest ? "" : `<p class="hint">👆 Tippe in einen der Kreise.</p>`}${erklaerung}${weiter}${abschluss}
      ${loesungKasten(`<strong>Prüfmodus:</strong> Richtig ist ${liste(r.ziele).map((z, k) => z.ok ? `Bereich ${k + 1}` : "").filter(Boolean).join(", ")} (grün umrandet).${r.erklaerung ? " " + esc(r.erklaerung) : ""}`)}`;
  }
  // Ein Tipp auf Ziel k der aktuellen Runde (Kreis oder Tastatur)
  function zielGewaehlt(t, k) {
    const cfg = cfgOf(t) || {}, runden = liste(cfg.runden), d = dt(t, true); if (!d || !runden.length) return;
    const i = Math.min(d.runde, runden.length - 1), r = runden[i], z = liste(r.ziele)[k];
    if (!z || d.ok[i] || liste(d.falsch[i]).includes(k)) return;
    d.versuche[i]++;
    const nr = k + 1, kopf = `${t.titel} · Runde ${i + 1}`;
    if (z.ok) {
      d.ok[i] = true;
      const fertig = d.ok.every(Boolean); if (fertig) d.fertig = true;
      sendAntwort(t.nr, "bildwahl", `${kopf}: Bereich ${nr} gewählt ✅ (${d.versuche[i]}. Versuch)`, true, r.frage || t.titel);
      neuZeichnen(t); aenderung(t);
      showFb(t.nr, "ok", `✅ Genau!${fertig ? " Du hast alle Runden geschafft." : " Lies die Erklärung und tippe dann auf „Weiter“."}`);
      if (fertig) { markComplete(t.nr); neuZeichnen(t); }
    } else {
      d.falsch[i].push(k);
      sendAntwort(t.nr, "bildwahl", `${kopf}: Bereich ${nr} gewählt ❌`, false, r.frage || t.titel);
      neuZeichnen(t); aenderung(t);
      showFb(t.nr, "err", `❌ ${esc(z.rueckmeldung || "Hier ist es nicht. Schau noch einmal genau hin.")}${d.falsch[i].length >= 2 && r.hinweis ? `<br>💡 ${esc(r.hinweis)}` : ""}`);
    }
  }
  BIE.actions["fo-ziel"] = el => { const t = aufgabenByNr[el.dataset.nr]; if (t) zielGewaehlt(t, parseInt(el.dataset.i, 10)); };   // Tastatur (Enter/Leertaste auf einem Kreis)
  BIE.actions["fo-bild-weiter"] = el => {
    const t = aufgabenByNr[el.dataset.nr], cfg = cfgOf(t) || {}, d = dt(t, true); if (!d) return;
    if (d.ok[d.runde] && d.runde < liste(cfg.runden).length - 1) { d.runde++; clearFb(t.nr); neuZeichnen(t); aenderung(t); }
  };
  // Jeder Tipp ins Bild (auf einen Kreis oder daneben) wird über die Bildkoordinaten ausgewertet: Kleine Kreise sind
  // mindestens 44 px groß (minRadius), bei Überlappung gewinnt der nächste Mittelpunkt.
  BIE.actions["fo-bild"] = (el, ev) => {
    const t = aufgabenByNr[el.dataset.nr], svg = el.tagName === "svg" ? el : el.closest("svg"); if (!t || !svg || !ev) return;
    const cfg = cfgOf(t) || {}, d = dt(t, true), r = liste(cfg.runden)[d && d.runde]; if (!r || d.ok[d.runde]) return;
    const box = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
    if (!box.width || !vb.width) return;
    const k = zielAn(r.ziele, (ev.clientX - box.left) * vb.width / box.width, (ev.clientY - box.top) * vb.height / box.height, minRadius(vb.width, box.width));
    if (k >= 0) zielGewaehlt(t, k); else showFb(t.nr, "info", "👆 Tippe in einen der Kreise.");
  };
  // Kreise an die tatsächliche Breite anpassen (nach dem Zeichnen und bei jeder Größenänderung)
  function kreiseAnpassen(svg) {
    const vb = svg.viewBox && svg.viewBox.baseVal, px = svg.getBoundingClientRect().width;
    if (!vb || !vb.width || !px) return;
    const minR = minRadius(vb.width, px);
    svg.querySelectorAll(".fo-ziel").forEach(g => { const c = g.querySelector("circle"); if (c) c.setAttribute("r", String(kreisR({ r: g.dataset.r }, minR))); });
  }
  const bildBeobachter = ("ResizeObserver" in window) ? new ResizeObserver(es => es.forEach(e => kreiseAnpassen(e.target))) : null;
  function bildAnpassen(host) {
    $$("svg.fo-bild", host || document).forEach(svg => { kreiseAnpassen(svg); if (bildBeobachter && !svg.dataset.beobachtet) { svg.dataset.beobachtet = "1"; bildBeobachter.observe(svg); } });
  }
  document.addEventListener("keydown", e => {
    const g = e.target; if ((e.key === "Enter" || e.key === " ") && g.classList && g.classList.contains("fo-ziel")) { e.preventDefault(); BIE.actions["fo-ziel"](g); }
  });

  // ═══ forscherbuch ══════════════════════════════════════════════════════════════════════════════
  const erledigt = nr => PRUEF || state.completed.has(String(nr));
  function notizText(a) {
    const ta = document.getElementById("nt-" + a.abschnitt);
    return ta ? ta.value.trim() : "";
  }
  // Aus dem Live-Zustand: je Reiter Forscherfrage → Vermutung → Erkenntnis (Merksatz), dazu Notizen.
  // Vermutung und Prüfen werden über die id über ALLE Reiter gepaart (die Forscherfrage kann in einem Reiter stehen und
  // in einem anderen geprüft werden); die Erkenntnis steht beim Eintrag der Vermutung und kommt nicht doppelt vor.
  function buchEingabe() {
    const alle = alleAufgaben(), vorhanden = new Set(alle.filter(a => a.typ === "vermutung").map(a => a.id));
    const pruefs = alle.filter(a => a.typ === "pruefen" && a.erkenntnis);
    const gepaart = new Set(pruefs.filter(p => vorhanden.has(p.vermutung)).map(p => String(p.nr)));
    return INHALTE.tabs.map(tab => {
      const eintraege = tab.aufgaben.filter(a => a.typ === "vermutung").map(v => {
        const dv = D[nrKey(v)], fertige = pruefs.filter(p => p.vermutung === v.id && erledigt(p.nr));
        // eigene Einschätzung und (Niveau C) eigener Satz aus der zugehörigen Prüfen-Station
        const dp = fertige.map(p => ({ p, d: D[nrKey(p)] })).filter(x => x.d && x.d.fertig);
        const einsch = dp.find(x => ganz(x.d.einsch));
        const saetze = dp.map(x => { const sc = (x.p.niveaus && x.p.niveaus[x.d.niveau] || {}).satz; return sc && x.d.satz && x.d.satz.trim() ? satzGanz(sc.anfang, x.d.satz) : ""; }).filter(Boolean);
        return { frage: v.titel, vermutung: dv && dv.fest ? dv.text : (PRUEF ? demoVermutung(v) : null),
          einschaetzung: einsch ? EINSCH_KURZ[einsch.d.einsch] : (PRUEF && fertige.length ? EINSCH_KURZ[0] : null),
          erkenntnisse: fertige.map(p => p.erkenntnis), saetze };
      });
      const weitere = tab.aufgaben.filter(a => a.erkenntnis && !["vermutung", "forscherbuch"].includes(a.typ) && !gepaart.has(String(a.nr)) && erledigt(a.nr)).map(a => a.erkenntnis);
      const notizen = tab.aufgaben.filter(a => a.typ === "notizen").map(notizText).filter(Boolean);
      return { key: tab.key, label: tab.label, icon: tab.icon, eintraege, weitere, notizen };
    });
  }
  const kopfZeile = () => [APP.pseudonym ? `${APP.pseudonym}${APP.klasse ? ", Klasse " + APP.klasse : ""}` : "", new Date().toLocaleDateString("de-DE")].filter(Boolean).join(" · ");
  function aktualisiereBuecher() {
    const buecher = $$(".fo-buch"); if (!buecher.length) return;
    const html = buchHTML(buchEingabe());
    buecher.forEach(b => { b.innerHTML = html; });
  }
  function renderForscherbuch(t) {
    return `<div class="fo-wrap" id="fo-${t.nr}">${t.hinweis ? `<p class="task-question">${esc(t.hinweis)}</p>` : `<p class="task-question">Hier steht alles, was du erforscht hast: deine Fragen, deine Vermutungen und deine Erkenntnisse.</p>`}
      <div class="fo-buch" id="fo-buch-${t.nr}" aria-live="polite"></div>
      <div class="btn-row">
        <button class="btn btn-quiet" type="button" data-action="fo-buch-neu" data-nr="${t.nr}">🔄 Aktualisieren</button>
        <button class="btn btn-outline" type="button" data-action="fo-buch-druck" data-nr="${t.nr}">🖨️ Drucken / als PDF sichern</button>
        <button class="btn btn-outline" type="button" data-action="fo-buch-kopie" data-nr="${t.nr}">📋 Text kopieren</button>
        <button class="btn btn-primary" type="button" data-action="fo-buch-abgabe" data-nr="${t.nr}">📤 Forscherbuch abgeben</button>
      </div></div>`;
  }
  function buchErledigt(t) { if (!state.completed.has(String(t.nr))) markComplete(t.nr); }
  BIE.actions["fo-buch-neu"] = () => { aktualisiereBuecher(); BIE.showToast("🔄 Dein Forscherbuch ist aktuell."); };
  BIE.actions["fo-buch-abgabe"] = el => {
    const t = aufgabenByNr[el.dataset.nr], buch = buchEingabe();
    if (buchLeer(buch)) { showFb(t.nr, "err", "⚠️ Dein Forscherbuch ist noch leer. Halte zuerst Vermutungen fest und sammle Erkenntnisse."); return; }
    aktualisiereBuecher();
    sendAntwort(t.nr, "forscherbuch", buchText(buch, kopfZeile()), null, "Mein Forscherbuch", FORSCHERBUCH_MAX);
    showFb(t.nr, "ok", "✅ Dein Forscherbuch ist abgegeben. Deine Lehrkraft kann es lesen.");
    buchErledigt(t); dirty();
  };
  BIE.actions["fo-buch-kopie"] = async el => {
    const t = aufgabenByNr[el.dataset.nr], inhalt = buchText(buchEingabe(), kopfZeile());
    let ok = false;
    try { if (navigator.clipboard && navigator.clipboard.writeText) { await navigator.clipboard.writeText(inhalt); ok = true; } } catch (e) { ok = false; }
    if (!ok) {   // Rückfall: Text markieren und kopieren
      const ta = document.createElement("textarea"); ta.value = inhalt; ta.setAttribute("readonly", ""); ta.style.cssText = "position:fixed;left:-9999px;top:0";
      document.body.appendChild(ta); ta.select();
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      ta.remove();
    }
    if (ok) { showFb(t.nr, "ok", "✅ Der Text deines Forscherbuchs ist kopiert. Du kannst ihn jetzt einfügen."); BIE.showToast("📋 Text kopiert"); buchErledigt(t); dirty(); }
    else showFb(t.nr, "err", "⚠️ Kopieren hat nicht geklappt. Nimm stattdessen „Drucken / als PDF sichern“.");
  };
  // Druckansicht: schlicht, A4, GSM-Kopf. Nur #fo-druck bleibt sichtbar (Stylesheet: @media print in app.css)
  BIE.actions["fo-buch-druck"] = el => {
    const t = aufgabenByNr[el.dataset.nr], buch = buchEingabe();
    if (buchLeer(buch)) { showFb(t.nr, "err", "⚠️ Dein Forscherbuch ist noch leer. Es gibt noch nichts zum Drucken."); return; }
    let seite = document.getElementById("fo-druck"); if (seite) seite.remove();
    seite = document.createElement("div"); seite.id = "fo-druck"; seite.className = "fo-druck";
    seite.innerHTML = `<header class="fo-druck-kopf"><img src="/static/img/logo-gsm.png" alt="Gesamtschule Meiderich"><div><p class="fo-druck-schule">Gesamtschule Meiderich · ${esc((APP.fach || "NW · Klasse 6"))}</p><h1>Mein Forscherbuch</h1><p class="fo-druck-name">${esc(kopfZeile())}</p></div></header>
      <p class="fo-druck-titel">${esc(INHALTE.titel || "")}</p>${buchHTML(buch)}`;
    document.body.appendChild(seite);
    document.body.classList.add("fo-drucken");
    const aufraeumen = () => { document.body.classList.remove("fo-drucken"); const s = document.getElementById("fo-druck"); if (s) s.remove(); window.removeEventListener("afterprint", aufraeumen); };
    window.addEventListener("afterprint", aufraeumen);
    buchErledigt(t); dirty();
    setTimeout(() => { try { window.print(); } catch (e) { aufraeumen(); } if (!("onafterprint" in window)) aufraeumen(); }, 80);
  };

  // ═══ gemeinsam ═════════════════════════════════════════════════════════════════════════════════
  function inner(t) {
    if (t.typ === "vermutung") return vermutungInner(t);
    if (t.typ === "pruefen") return pruefenInner(t);
    if (t.typ === "protokoll") return protokollInner(t);
    if (t.typ === "tabelle") return tabelleInner(t);
    if (t.typ === "bildwahl") return bildwahlInner(t);
    return "";
  }
  // Aufruf aus aufgaben.js: renderBody(t) → host.innerHTML = render(t); danach nachRender(t)
  function render(t) {
    if (t.typ === "forscherbuch") return renderForscherbuch(t);
    return `<div class="fo-wrap fo-${t.typ}" id="fo-${t.nr}" data-typ="${t.typ}">${inner(t)}</div>`;
  }
  function nachRender(t) {
    if (!istMein(t)) return;
    if (t.typ === "forscherbuch") aktualisiereBuecher();
    if (t.typ === "vermutung") sperreNiveau(t);
    if (t.typ === "bildwahl") bildAnpassen(body(t.nr));
  }

  // Forscherbuch frisch halten: beim Öffnen des Reiters und wenn der Schrittmodus eine neue Station zeigt
  const vorher = BIE.beimOeffnen["*"];
  BIE.beimOeffnen["*"] = key => { if (vorher) vorher(key); aktualisiereBuecher(); };
  document.addEventListener("click", e => { if (e.target.closest && e.target.closest('[data-action="schritt-weiter"], [data-action="schritt-spaeter"]')) setTimeout(aktualisiereBuecher, 90); });

  // ─── Autosave ───
  BIE.autosave.register("forschen", () => {
    const out = {};
    alleAufgaben().forEach(t => { const d = D[nrKey(t)]; if (istMein(t) && t.typ !== "forscherbuch" && hatInhalt(d)) out[nrKey(t)] = d; });
    return Object.keys(out).length ? JSON.parse(JSON.stringify(out)) : undefined;
  }, data => {
    D = {};
    Object.entries(data || {}).forEach(([nr, d]) => { const t = aufgabenByNr[nr]; if (!t || !istMein(t) || t.typ === "forscherbuch") return; const sauber = bereinigen(t, d); if (sauber) D[nr] = sauber; });
    // erst jetzt zeichnen: alle Karten neu (pruefen und forscherbuch brauchen die Vermutungen)
    alleAufgaben().forEach(t => { if (istMein(t) && body(t.nr) && BIE.aufgaben) BIE.aufgaben.renderBody(t); });
  }, 32);

  return { render, nachRender, logik, TYPEN, istMein, vermutungTextFuer, buchEingabe, aktualisiereBuecher, get daten() { return D; }, init() {} };
})();
