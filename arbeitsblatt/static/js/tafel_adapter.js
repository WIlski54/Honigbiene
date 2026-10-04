/* Tafel ↔ dieses Arbeitsblatt: übersetzt Aufgaben aus INHALTE (inhalte.js + inhalte_<reiter>.js) und Arbeitsstände
   (Autosave-Format) in das Format der Tafel. Wird von Schüler- und Lehrerseite geladen.
   Schnittstelle GT.abAdapter (siehe Tafel-Baustein): aufgaben, leer, meineAufgaben, aufgabenVon.

   An der Tafel lösbar sind nur diese AB-Typen (Tafel-Typ in Klammern):
     mc (mc) · mc mit `aussagen` = Richtig/Falsch-Liste (richtigfalsch) · luecke (lueckentext) · zuordnung (zuordnung)
     sortierung (sortieren) · freitext (freitext; auf Niveau A im Baustein-Modus: sortieren)
   NICHT angeboten: film, filmmoment, erkunden, modellfinden, bildpunkte, zeichnen, diagramm, blitz, domino, quellen,
   notizen, transfer. */
(function () {
  "use strict";
  const GT = (window.GT = window.GT || {});
  const I = window.INHALTE;
  if (!I) return;
  const alle = [];
  I.tabs.forEach((tab) => tab.aufgaben.forEach((a) => alle.push(a)));
  const nachNr = {};
  alle.forEach((a) => { nachNr[String(a.nr)] = a; });

  const cfgVon = (t, n) => (t.niveaus ? t.niveaus[n] || t.niveaus.A : t);
  const niveausVon = (t) => (t.niveaus ? ["A", "B", "C"].filter((n) => t.niveaus[n]) : ["A"]);
  // Sichtbar ist die fortlaufende Anzeigenummer (static/js/anzeige.js); aufgabe_id bleibt die interne nr.
  const anzeige = (nr) => (I.anzeigeNr ? I.anzeigeNr(nr) : String(nr));
  const titel = (t) => `Aufgabe ${anzeige(t.nr)}: ${t.titel}`;
  // feste, nicht triviale Reihenfolge (die Lösung soll nicht einfach dastehen)
  const gemischt = (liste) => liste.slice().sort((a, b) => ((a.length * 7 + [...a].reduce((s, c) => s + c.charCodeAt(0), 0)) % 11)
    - ((b.length * 7 + [...b].reduce((s, c) => s + c.charCodeAt(0), 0)) % 11));

  /** Welche Aufgabe wird an der Tafel wie dargestellt? (null = nicht an der Tafel lösbar) */
  function tafelTyp(t, cfg) {
    if (t.typ === "mc") return cfg && cfg.aussagen ? "richtigfalsch" : "mc";
    if (t.typ === "luecke") return "lueckentext";
    if (t.typ === "zuordnung") return "zuordnung";
    if (t.typ === "sortierung") return "sortieren";
    if (t.typ === "freitext") return cfg && cfg.modus === "bausteine" ? "sortieren" : "freitext";
    return null;   // alles andere lässt sich an der Tafel nicht lösen (siehe Kopf der Datei)
  }

  function luecken(text) {
    const teile = [], loesungen = [];
    let rest = String(text || ""), n = 0;
    const re = /\[([^\]]+)\]/g;
    let letzte = 0, m;
    while ((m = re.exec(rest))) {
      if (m.index > letzte) teile.push({ text: rest.slice(letzte, m.index) });
      teile.push({ feld: "l" + n });
      loesungen.push(m[1].split("|").map((s) => s.trim()));
      n++;
      letzte = m.index + m[0].length;
    }
    if (letzte < rest.length) teile.push({ text: rest.slice(letzte) });
    return { teile, loesungen };
  }

  /** Leere Tafel-Aufgabe + Lösung (nur die Lehrkraft schickt die Lösung an den Server). */
  function leerSync(nr, niveau) {
    const t = nachNr[String(nr)];
    if (!t) throw new Error("Unbekannte Aufgabe.");
    const cfg = cfgVon(t, niveau);
    const typ = tafelTyp(t, cfg);
    const basis = { aufgabentyp: typ, titel: titel(t), aufgabe_id: String(t.nr), niveau: t.niveaus ? niveau : null };
    if (typ === "mc") {
      const richtig = cfg.optionen.filter((o) => o.ok).map((o) => o.t);
      return { aufgabe: Object.assign(basis, { frage: cfg.frage, optionen: cfg.optionen.map((o) => o.t), mehrfach: !!cfg.multi }),
        loesung: { wahl: [cfg.multi ? richtig.join("|") : richtig[0]] } };
    }
    if (typ === "richtigfalsch") {
      const loesung = {};
      cfg.aussagen.forEach((a, i) => { loesung["r" + i] = [a.ok ? "richtig" : "falsch"]; });
      return { aufgabe: Object.assign(basis, { aussagen: cfg.aussagen.map((a) => ({ text: a.t })) }), loesung };
    }
    if (typ === "lueckentext") {
      const { teile, loesungen } = luecken(cfg.text);
      const wortbank = [...new Set(loesungen.map((l) => l[0]).concat(cfg.ablenker || []))].sort((a, b) => a.localeCompare(b, "de"));
      const loesung = {};
      loesungen.forEach((l, i) => { loesung["l" + i] = l; });
      return { aufgabe: Object.assign(basis, { teile, wortbank }), loesung };
    }
    if (typ === "zuordnung") {
      const kategorien = [...new Set(cfg.paare.map((p) => p[0]))];
      const loesung = {};
      cfg.paare.forEach((p, i) => { loesung["z" + i] = [p[0]]; });
      return { aufgabe: Object.assign(basis, { zeilen: cfg.paare.map((p) => ({ text: p[1] })), optionen: kategorien }), loesung };
    }
    if (typ === "sortieren") {
      const items = cfg.modus === "bausteine" ? cfg.bausteine : cfg.items;
      const loesung = {};
      items.forEach((x, i) => { loesung["p" + i] = [x]; });
      return { aufgabe: Object.assign(basis, { frage: cfg.hinweis || cfg.aufgabe || "Bringe in die richtige Reihenfolge.", elemente: gemischt(items) }), loesung };
    }
    if (typ === "freitext") return { aufgabe: Object.assign(basis, { frage: cfg.aufgabe || t.titel }), loesung: null };
    throw new Error("Diese Aufgabe lässt sich nicht an der Tafel lösen.");
  }

  /** Antwort eines Arbeitsstands (Autosave-Format) als AB-Karte: {aufgabe_id, titel, typ, niveau, bearbeitet, inhalt}. */
  function eintrag(t, st) {
    const n = (st.niveaus || {})[t.nr] || "A";
    const cfg = cfgVon(t, n);
    const typ = tafelTyp(t, cfg);
    const d = (st.aufgaben || {})[t.nr] || {};
    let inhalt = { text: "" }, bearbeitet = false;
    if (typ === "richtigfalsch") {
      const wahl = d.wahl || [];
      const zeilen = cfg.aussagen.map((a, i) => `${a.t} → ${wahl[i] === "r" ? "richtig" : wahl[i] === "f" ? "falsch" : "…"}`);
      inhalt = { text: wahl.some(Boolean) ? zeilen.join("\n") : "" };
      bearbeitet = wahl.some(Boolean);
    } else if (typ === "mc") {
      const gew = (d.gewaehlt || []).map((i) => cfg.optionen[i] && cfg.optionen[i].t).filter(Boolean);
      inhalt = { text: gew.length ? cfg.frage + "\n→ " + gew.join("\n→ ") : "" };
      bearbeitet = gew.length > 0;
    } else if (typ === "lueckentext") {
      const { teile } = luecken(cfg.text);
      const werte = d.werte || [];
      let i = 0;
      inhalt = { segmente: teile.map((x) => (x.feld ? { luecke: werte[i++] || "…" } : { text: x.text })) };
      bearbeitet = werte.some((w) => String(w || "").trim());
    } else if (typ === "zuordnung") {
      const paare = (d.paare || []).map((i) => cfg.paare[i]).filter(Boolean).map((p) => [p[1], p[0]]);
      inhalt = { paare };
      bearbeitet = paare.length > 0;
    } else if (typ === "sortieren") {
      const items = cfg.modus === "bausteine" ? cfg.bausteine : cfg.items;
      const folge = (cfg.modus === "bausteine" ? d.text : d.reihenfolge) || [];
      inhalt = { text: folge.map((i, k) => `${k + 1}. ${items[i]}`).join("\n") };
      bearbeitet = folge.length > 0;
    } else if (typ === "freitext") {
      const text = (st.texte || {})["ft-" + t.nr] || "";
      inhalt = { text };
      bearbeitet = !!text.trim();
    }
    return { aufgabe_id: String(t.nr), titel: titel(t), typ: typ || "freitext", niveau: t.niveaus ? n : null, bearbeitet, inhalt };
  }

  const tafelTauglich = () => alle.filter((t) => tafelTyp(t, cfgVon(t, niveausVon(t)[0])) || tafelTyp(t, null));

  async function arbeitsstand(sid) {
    const d = await GT.api("GET", "/tafel/api/lehrer/arbeitsstand/" + encodeURIComponent(sid));
    return d.state || {};
  }

  GT.abAdapter = {
    /** Liste für „📋 Aufgabe an die Tafel“; Vorschlag = Niveau des ersten Schülers vorne. */
    async aufgaben(amBrett) {
      let niveaus = {};
      if (amBrett && amBrett[0]) { try { niveaus = (await arbeitsstand(amBrett[0].id)).niveaus || {}; } catch (e) { niveaus = {}; } }
      return tafelTauglich().map((t) => ({ aufgabe_id: String(t.nr), titel: titel(t), typ: t.typ, niveaus: niveausVon(t),
        vorschlag: t.niveaus ? niveaus[t.nr] || "A" : "A" }));
    },
    async leer(nr, niveau) { return leerSync(nr, niveau); },
    /** Schüler: eigene Aufgaben aus dem aktuellen Stand im Browser. */
    async meineAufgaben() {
      const st = window.BIE && BIE.autosave ? BIE.autosave.collectBackup() : {};
      return tafelTauglich().map((t) => eintrag(t, st));
    },
    /** Lehrkraft: Aufgaben eines Schülers aus seinem gespeicherten Arbeitsstand. */
    async aufgabenVon(sid) {
      const st = await arbeitsstand(sid);
      return tafelTauglich().map((t) => eintrag(t, st));
    },
    /** Schüler: Karte zu einer Aufgabe (für „🙋 Ich möchte das vorstellen“). */
    eigeneKarte(nr) {
      const t = nachNr[String(nr)];
      const st = window.BIE && BIE.autosave ? BIE.autosave.collectBackup() : {};
      return t ? eintrag(t, st) : null;
    },
    tafelTauglich: (nr) => !!(nachNr[String(nr)] && tafelTauglich().includes(nachNr[String(nr)])),
  };
})();
