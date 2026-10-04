// Logiktests für static/js/forschen.js (vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch) – ohne Browser.
// Das Modul läuft in einer Node-Umgebung mit Attrappen für BIE, document und window. Die Aufgaben stammen aus
// tests/fixtures_forschen.js (nicht aus den echten Inhalten). Geprüft wird Logik und Zustand: Zahlprüfung mit Toleranz,
// Chips, Tabellenprüfung, Treffer in Kreisen, Zustand hin und zurück (Autosave), Forscherbuch-Aufbau, Protokolltexte.
// Das Zeichnen im Browser, Touchziele und Breiten prüft die Browserprobe (werkzeuge/qa_forschen.py, README).
// Aufruf: node --test tests/forschen.test.cjs   (pytest ruft das über tests/test_forschen.py auf)
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const { aufbau, fixtures, plain } = require("./_forschen_umgebung.cjs");

// ── Reine Logik ──────────────────────────────────────────────────────────────
test("Zahlen: parseZahl versteht Ziffern, Komma, Einheiten, Zahlwörter und Tausenderpunkte", () => {
  const { logik: L } = aufbau();
  assert.equal(L.parseZahl("6"), 6);
  assert.equal(L.parseZahl(" 6 Beine "), 6);
  assert.equal(L.parseZahl("6,5"), 6.5);
  assert.equal(L.parseZahl("sechs"), 6);
  assert.equal(L.parseZahl("Zwölf"), 12);
  assert.equal(L.parseZahl("50.000"), 50000);
  assert.equal(L.parseZahl("50 000"), 50000);
  assert.equal(L.parseZahl("-3"), -3);
  assert.equal(L.parseZahl(""), null);
  assert.equal(L.parseZahl("viele"), null);
  assert.equal(L.parseZahl("6 7"), null, "zwei Zahlen sind keine Antwort");
  assert.equal(L.parseZahl(null), null);
});

test("Zahlen: Toleranz entscheidet, ohne Toleranz zählt nur die genaue Zahl", () => {
  const { logik: L } = aufbau();
  assert.equal(L.zahlStimmt(6, 6, 0), true);
  assert.equal(L.zahlStimmt(5, 6, 0), false);
  assert.equal(L.zahlStimmt(12, 13, 1), true);
  assert.equal(L.zahlStimmt(14, 13, 1), true);
  assert.equal(L.zahlStimmt(15, 13, 1), false);
  assert.equal(L.zahlStimmt(6.4, 6, 0.5), true);
  assert.equal(L.zahlStimmt(null, 6, 0), false);
  assert.equal(L.zahlStimmt(NaN, 6, 5), false);
});

test("Zeilen des Forscherbogens: leer, falsch, richtig – je Zeilenart", () => {
  const { logik: L } = aufbau();
  const zahl = { art: "zahl", loesung: 6 }, wahl = { art: "wahl", optionen: ["a", "b", "c"], loesung: 2 };
  const mehr = { art: "mehrfach", optionen: ["a", "b", "c", "d"], loesung: [0, 2, 3] }, txt = { art: "text", min: 8 };
  assert.deepEqual(plain(L.zeileAuswerten(zahl, null)), { leer: true, ok: false });
  assert.deepEqual(plain(L.zeileAuswerten(zahl, "  ")), { leer: true, ok: false });
  assert.deepEqual(plain(L.zeileAuswerten(zahl, "7")), { leer: false, ok: false });
  assert.deepEqual(plain(L.zeileAuswerten(zahl, "sechs")), { leer: false, ok: true });
  assert.equal(L.zeileAuswerten(wahl, null).leer, true);
  assert.equal(L.zeileAuswerten(wahl, 1).ok, false);
  assert.equal(L.zeileAuswerten(wahl, 0).ok, false, "Index 0 ist eine echte Wahl");
  assert.equal(L.zeileAuswerten(wahl, 2).ok, true);
  assert.equal(L.zeileAuswerten(mehr, []).leer, true);
  assert.equal(L.zeileAuswerten(mehr, [0, 2]).ok, false, "es fehlt eine richtige");
  assert.equal(L.zeileAuswerten(mehr, [0, 1, 2, 3]).ok, false, "eine falsche ist dabei");
  assert.equal(L.zeileAuswerten(mehr, [3, 0, 2]).ok, true, "Reihenfolge egal");
  assert.equal(L.zeileAuswerten(txt, "zu kurz").ok, false);
  assert.equal(L.zeileAuswerten(txt, "Das ist ein Satz.").ok, true);
  assert.equal(L.zeileAuswerten(txt, "").leer, true);
});

test("Protokolltext ist lesbar: „Beobachtung: Beine = 6 ✅“", () => {
  const { logik: L } = aufbau();
  assert.equal(L.zeilenText({ art: "zahl", einheit: "Beine", frage: "Wie viele Beine hat die Biene?" }, "6", true), "Beobachtung: Beine = 6 ✅");
  assert.equal(L.zeilenText({ art: "zahl", einheit: "Beine", frage: "x" }, "sieben", false), "Beobachtung: Beine = 7 ❌");
  assert.equal(L.zeilenText({ art: "wahl", frage: "Welches Beinpaar trägt das Körbchen?", optionen: ["vorn", "Mitte", "hinten"] }, 2, true), "Beobachtung: Welches Beinpaar trägt das Körbchen = hinten ✅");
  assert.equal(L.zeilenText({ art: "mehrfach", kurz: "Körperteile", optionen: ["Kopf", "Schwanz", "Brust"] }, [0, 2], true), "Beobachtung: Körperteile = Kopf + Brust ✅");
  assert.match(L.zeilenText({ art: "text", kurz: "Augen" }, " Große Augen. ", true), /^Beobachtung: Augen: „Große Augen\.“ ✅$/);
});

test("Tabelle: Zellen prüfen, fehlende zählen, fertig nur wenn alles stimmt", () => {
  const { logik: L, F } = aufbau();
  const c = F.tabs[1].aufgaben[0].niveaus.A;   // 3 Spalten, 2 Zeilen
  let r = L.tabelleAuswerten([[null, null, null], [null, null, null]], c.zeilen, 3);
  assert.deepEqual([r.richtig, r.gesamt, r.leer, r.fertig], [0, 6, 6, false]);
  r = L.tabelleAuswerten([[0, 1, 2], [0, 0, 0]], c.zeilen, 3);
  assert.deepEqual([r.richtig, r.leer, r.fertig], [5, 0, false]);
  assert.deepEqual(plain(r.ok), [[true, true, true], [true, true, false]]);
  r = L.tabelleAuswerten([[0, 1, 2], [0, 0, 1]], c.zeilen, 3);
  assert.equal(r.fertig, true);
  r = L.tabelleAuswerten([[0, 1, 2]], c.zeilen, 3);
  assert.equal(r.leer, 3, "eine fehlende Zeile zählt als leer");
  assert.match(L.tabelleText(c.zeilen, ["Königin", "Arbeiterin", "Drohne"], [[0, 1, 2], [0, 0, 0]], L.tabelleAuswerten([[0, 1, 2], [0, 0, 0]], c.zeilen, 3).ok),
    /Hinterleib: Königin = lang ✅, Arbeiterin = mittel ✅, Drohne = dick ✅ \| Stachel: Königin = hat einen ✅, Arbeiterin = hat einen ✅, Drohne = hat einen ❌/);
});

test("Bildwahl: Treffer in Kreisen – Rand zählt, daneben nicht, bei Überlappung gewinnt der nähere Mittelpunkt", () => {
  const { logik: L } = aufbau();
  const ziele = [{ x: 100, y: 100, r: 50, ok: true }, { x: 160, y: 100, r: 50, ok: false }];
  assert.equal(L.trifftKreis(ziele[0], 100, 100), true);
  assert.equal(L.trifftKreis(ziele[0], 150, 100), true, "genau auf dem Rand");
  assert.equal(L.trifftKreis(ziele[0], 151, 100), false);
  assert.equal(L.zielAn(ziele, 100, 100), 0);
  assert.equal(L.zielAn(ziele, 160, 100), 1);
  assert.equal(L.zielAn(ziele, 130, 100), 0, "Überlappung: gleich weit weg → das erste");
  assert.equal(L.zielAn(ziele, 140, 100), 1, "Überlappung: näher an Ziel 2");
  assert.equal(L.zielAn(ziele, 400, 400), -1);
  assert.equal(L.zielAn([], 1, 1), -1);
});

test("Bildwahl: kleine Kreise werden für Finger vergrößert (Touchziel 44 px), echte Größe zählt, wenn sie größer ist", () => {
  const { logik: L } = aufbau();
  const klein = [{ x: 100, y: 100, r: 20, ok: true }, { x: 300, y: 100, r: 90, ok: false }];
  // Bild 900 Einheiten breit, auf dem Handy 330 px breit: 44 px Durchmesser = 22 px Radius = 60 Einheiten
  const minR = L.minRadius(900, 330);
  assert.ok(Math.abs(minR - 60) < 0.01, `minRadius ${minR}`);
  assert.equal(L.kreisR(klein[0], minR), 60);
  assert.equal(L.kreisR(klein[1], minR), 90, "ein größerer Kreis bleibt, wie er ist");
  assert.equal(L.zielAn(klein, 150, 100), -1, "ohne Vergrößerung daneben");
  assert.equal(L.zielAn(klein, 150, 100, minR), 0, "mit Vergrößerung getroffen");
  assert.equal(L.zielAn(klein, 235, 100, minR), 1);
  assert.equal(L.minRadius(900, 0), 0, "Bild nicht sichtbar: nichts vergrößern");
  assert.equal(L.trifftKreis(klein[0], 150, 100, minR), true);
});

test("Vermutung: Gültigkeit je Niveau und Text für Forscherbuch und Protokoll", () => {
  const { logik: L, F } = aufbau();
  const v = F.tabs[0].aufgaben[0].niveaus;
  assert.deepEqual(plain(L.vermutungGueltig(v.A, [], "")), { ok: false, grund: "wahl" });
  assert.equal(L.vermutungGueltig(v.A, [3], "").ok, true);
  assert.deepEqual(plain(L.vermutungGueltig(v.B, [1], "kurz")), { ok: false, grund: "text", min: 10 });
  assert.equal(L.vermutungGueltig(v.B, [1], "es viele sind").ok, true);
  assert.deepEqual(plain(L.vermutungGueltig(v.C, [], "zu kurz")), { ok: false, grund: "text", min: 30 });
  assert.equal(L.vermutungGueltig(v.C, [], "es sind sehr viele, weil das Volk groß ist").ok, true);
  assert.deepEqual(plain(L.vermutungTexte(v.A, [3], "")), { optionen: ["etwa 50 000"], satz: "", text: "etwa 50 000", antwort: "Vermutung: etwa 50 000" });
  const b = L.vermutungTexte(v.B, [3], "es sehr viele sind, weil …");
  assert.equal(b.satz, "Ich vermute, dass es sehr viele sind, weil …");
  assert.equal(b.antwort, "Vermutung: etwa 50 000 · Ich vermute, dass es sehr viele sind, weil …");
  const c = L.vermutungTexte(v.C, [], "es viele sind");
  assert.equal(c.text, "Ich vermute, dass es viele sind");
  assert.equal(c.antwort, "Vermutung: Ich vermute, dass es viele sind");
  assert.equal(L.vermutungTexte({ optionen: ["a", "b", "c"], mehrfach: true }, [2, 0], "").text, "a und c");
  assert.equal(L.anfangOhnePunkte("Ich vermute, dass …"), "Ich vermute, dass");
  assert.equal(L.satzGanz("Ich vermute, dass ...", "  es so ist "), "Ich vermute, dass es so ist");
});

// ── Vermutung ────────────────────────────────────────────────────────────────
test("Vermutung A: ohne Wahl kein Festhalten; mit Bestätigung gesperrt, protokolliert ohne Bewertung, im Autosave", () => {
  const a = aufbau();
  a.zeige(901);
  a.act("fo-verm-sicher", { nr: 901 });
  assert.equal(a.letzteFb().kind, "err");
  assert.match(a.letzteFb().html, /Tippe zuerst eine Möglichkeit an/);
  assert.equal(a.log.fertig.length, 0);
  a.act("fo-verm-wahl", { nr: 901, i: 3 });
  assert.deepEqual(a.D()["901"].wahl, [3]);
  a.act("fo-verm-wahl", { nr: 901, i: 1 });
  assert.deepEqual(a.D()["901"].wahl, [1], "ohne mehrfach ersetzt die neue Wahl die alte");
  a.act("fo-verm-wahl", { nr: 901, i: 1 });
  assert.deepEqual(a.D()["901"].wahl, [], "noch einmal tippen nimmt zurück");
  a.act("fo-verm-wahl", { nr: 901, i: 3 });
  a.act("fo-verm-sicher", { nr: 901 });
  assert.equal(a.letzteFb().kind, "info", "erst Rückfrage");
  assert.equal(a.log.antworten.length, 0);
  a.act("fo-verm-fest", { nr: 901 });
  assert.equal(a.log.antworten.length, 1);
  const s = a.log.antworten[0];
  assert.deepEqual([s.typ, s.text, s.korrekt], ["vermutung", "Vermutung: etwa 50 000", null]);
  assert.equal(a.D()["901"].fest, true);
  assert.deepEqual(a.log.fertig, ["901"]);
  assert.match(a.html(901), /Meine Vermutung/);
  assert.match(a.html(901), /etwa 50 000/);
  assert.doesNotMatch(a.html(901), /fo-chip/, "gesperrt: keine Chips mehr");
  assert.equal(a.fo.vermutungTextFuer("v_anzahl"), "etwa 50 000");
  a.act("fo-verm-wahl", { nr: 901, i: 0 });
  assert.deepEqual(a.D()["901"].wahl, [3], "eine festgehaltene Vermutung ändert sich nicht mehr");
  const gespeichert = a.regs.forschen.collect();
  assert.equal(gespeichert["901"].fest, true);
  assert.equal(gespeichert["901"].text, "etwa 50 000");
});

test("Vermutung B und C: Satz nötig, Bausteine hängen sich an, Mehrfachauswahl", () => {
  const a = aufbau({ niveau: { 901: "B", 907: "A", 910: "C" } });
  a.zeige(901);
  a.act("fo-verm-wahl", { nr: 901, i: 2 });
  a.act("fo-verm-sicher", { nr: 901 });
  assert.match(a.letzteFb().html, /mindestens 10 Zeichen/);
  const ta = a.els["fo-sat-901"] || (a.els["fo-sat-901"] = { value: "", dispatchEvent() {}, focus() {}, id: "fo-sat-901" });
  ta.value = "es sehr viele sind";
  a.input({ foInput: "verm", nr: "901" }, ta.value);
  assert.equal(a.D()["901"].satz, "es sehr viele sind");
  a.act("fo-verm-sicher", { nr: 901 });
  a.act("fo-verm-fest", { nr: 901 });
  assert.equal(a.log.antworten[0].text, "Vermutung: etwa 5 000 · Ich vermute, dass es sehr viele sind");
  // C
  a.zeige(910);
  a.act("fo-verm-sicher", { nr: 910 });
  assert.match(a.letzteFb().html, /mindestens 30 Zeichen/);
});

test("Vermutung A mit mehrfach: mehrere Chips, Reihenfolge der Optionen im Text", () => {
  const a = aufbau({ niveau: { 910: "A" } });
  a.zeige(910);
  a.act("fo-verm-wahl", { nr: 910, i: 2 });
  a.act("fo-verm-wahl", { nr: 910, i: 0 });
  assert.deepEqual(a.D()["910"].wahl, [2, 0]);
  a.act("fo-verm-sicher", { nr: 910 }); a.act("fo-verm-fest", { nr: 910 });
  assert.equal(a.log.antworten[0].text, "Vermutung: Die Bienen brauchen Honig im Winter. | Der Imker mag keinen Honig.");
  assert.equal(a.D()["910"].text, "Die Bienen brauchen Honig im Winter. Der Imker mag keinen Honig.", "Sätze werden ohne „und“ aneinandergehängt");
});

test("Niveauwechsel: nicht festgehaltene Eingaben beginnen neu, die festgehaltene Vermutung bleibt", () => {
  const a = aufbau();
  a.zeige(901);
  a.act("fo-verm-wahl", { nr: 901, i: 2 });
  assert.deepEqual(a.D()["901"].wahl, [2]);
  a.state.niveau[901] = "B";
  a.zeige(901);
  assert.deepEqual(a.D()["901"].wahl, [], "andere Stufe → frischer Start");
  a.state.niveau[901] = "A";
  a.act("fo-verm-wahl", { nr: 901, i: 3 });
  a.act("fo-verm-sicher", { nr: 901 }); a.act("fo-verm-fest", { nr: 901 });
  a.state.niveau[901] = "C";
  a.zeige(901);
  assert.equal(a.D()["901"].fest, true);
  assert.match(a.html(901), /etwa 50 000/);
});

// ── pruefen ──────────────────────────────────────────────────────────────────
function vermutungFesthalten(a, nr, i) {
  a.zeige(nr); a.act("fo-verm-wahl", { nr, i }); a.act("fo-verm-sicher", { nr }); a.act("fo-verm-fest", { nr });
}
test("Prüfen A: zeigt die Vermutung, Einschätzung, falsch lenkt auf die Quelle (ohne Lösung), richtig → Merksatz", () => {
  const a = aufbau();
  vermutungFesthalten(a, 901, 1);
  a.zeige(903);
  assert.match(a.html(903), /Deine Vermutung war/);
  assert.match(a.html(903), /etwa 500/);
  assert.doesNotMatch(a.html(903), /Was hast du herausgefunden/, "erst die Einschätzung");
  a.act("fo-pr-einsch", { nr: 903, i: 2 });
  assert.match(a.html(903), /Was hast du herausgefunden/);
  assert.equal(a.log.antworten.at(-1).korrekt, null, "Einschätzung wird nicht bewertet");
  a.act("fo-pr-erk", { nr: 903, i: 0 });
  const fb = a.letzteFb();
  assert.equal(fb.kind, "err");
  assert.match(fb.html, /gelbe Hinweis oben/, "die Rückmeldung lenkt auf die Quelle (der Kasten oben)");
  assert.doesNotMatch(fb.html, /Szene 1/, "die Quelle steht nur einmal da: im Kasten, nicht noch einmal in der Rückmeldung");
  assert.equal((a.html(903).match(/Szene 1 im Film/g) || []).length, 1, "und der Kasten bleibt");
  assert.doesNotMatch(fb.html, /50 000/, "und verrät die Lösung nicht");
  assert.deepEqual(a.log.antworten.at(-1).korrekt, false);
  assert.match(a.log.antworten.at(-1).text, /^Erkenntnis: Es leben nur wenige hundert Bienen im Stock\. ❌$/);
  assert.match(a.html(903), /incorrect/);
  assert.doesNotMatch(a.html(903), /Merke/);
  a.act("fo-pr-erk", { nr: 903, i: 1 });
  assert.deepEqual(a.log.fertig, ["901", "903"]);
  const s = a.log.antworten.at(-1);
  assert.equal(a.log.antworten.at(-2).korrekt, true, "der richtige Schritt ist bewertet");
  assert.equal(s.korrekt, null, "die Zusammenfassung zählt nicht doppelt");
  assert.match(s.text, /Vermutung: etwa 500 · Einschätzung: stimmt nicht · Erkenntnis: Es leben bis zu etwa 50 000 Bienen im Stock\. ✅/);
  assert.match(a.html(903), /Merke/);
  assert.match(a.html(903), /bis zu etwa 50 000 Bienen in einem Stock/);
  assert.equal(a.D()["903"].fertig, true);
});

test("Prüfen B braucht den Beleg, C den eigenen Satz; ohne festgehaltene Vermutung bleibt es freundlich", () => {
  const a = aufbau({ niveau: { 903: "B", 909: "C" } });
  a.zeige(903);
  assert.match(a.html(903), /noch keine Vermutung festgehalten/);
  a.act("fo-pr-einsch", { nr: 903, i: 0 });
  a.act("fo-pr-erk", { nr: 903, i: 1 });
  assert.equal(a.state.completed.has("903"), false, "B: noch der Beleg");
  assert.match(a.html(903), /Woher weißt du das/);
  a.act("fo-pr-beleg", { nr: 903, i: 1 });
  assert.equal(a.letzteFb().kind, "err");
  assert.equal(a.state.completed.has("903"), false);
  a.act("fo-pr-beleg", { nr: 903, i: 0 });
  assert.equal(a.state.completed.has("903"), true);
  assert.match(a.log.antworten.at(-1).text, /Beleg: Das habe ich im Film gesehen\. ✅/);
  // C
  a.zeige(909);
  a.act("fo-pr-einsch", { nr: 909, i: 1 });
  a.act("fo-pr-erk", { nr: 909, i: 1 });
  assert.equal(a.state.completed.has("909"), false, "C: erst der eigene Satz");
  a.act("fo-pr-satz", { nr: 909 });
  assert.match(a.letzteFb().html, /mindestens 40 Zeichen/);
  a.input({ foInput: "pr-satz", nr: "909" }, "Ich habe herausgefunden, dass eine Arbeiterin 21 Tage braucht.");
  a.act("fo-pr-satz", { nr: 909 });
  assert.equal(a.state.completed.has("909"), true);
  assert.match(a.log.antworten.at(-1).text, /Mein Satz: Ich habe herausgefunden, dass eine Arbeiterin 21 Tage braucht\./);
});

// ── protokoll ────────────────────────────────────────────────────────────────
test("Protokoll A: richtige und falsche Zahl, Hinweise erst nach Fehlern, Station erledigt wenn alle Zeilen stimmen", () => {
  const a = aufbau();
  a.zeige(902);
  assert.match(a.html(902), /Wie viele Beine hat die Biene/);
  assert.match(a.html(902), /Von der Seite zeigen/, "Zeilen-Knopf");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(a.letzteFb().html, /Trage zuerst etwas ein/);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "5");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(a.html(902), /Zähle noch einmal genau nach/);
  assert.doesNotMatch(a.html(902), /beiden Seiten/, "kein Hinweis nach dem ersten Fehler");
  assert.doesNotMatch(a.html(902), /fo-blink/);
  assert.deepEqual(a.log.antworten.at(-1), { nr: "902", typ: "protokoll", text: "Beobachtung: Beine = 5 ❌", korrekt: false, frage: "Wie viele Beine hat die Biene?", max: undefined });
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "7");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(a.html(902), /Zähle auf beiden Seiten/, "nach dem zweiten Fehler kommt der Tipp");
  assert.doesNotMatch(a.html(902), /Seitenansicht/);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "8");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(a.html(902), /Sieh dir die Seitenansicht an/, "nach dem dritten der zweite Tipp");
  assert.match(a.html(902), /fo-blink/, "der Modell-Knopf blinkt");
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "sechs");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.equal(a.log.antworten.at(-1).text, "Beobachtung: Beine = 6 ✅");
  assert.equal(a.state.completed.has("902"), false, "Zeile 2 fehlt noch");
  a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 0 });
  a.act("fo-alle-pruefen", { nr: 902 });
  assert.equal(a.state.completed.has("902"), false);
  assert.match(a.letzteFb().html, /1 Zeile stimmt noch nicht/);
  a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 });
  a.act("fo-alle-pruefen", { nr: 902 });
  assert.equal(a.state.completed.has("902"), true);
  assert.match(a.html(902), /Eine Biene hat drei Körperteile, sechs Beine und vier Flügel/, "Merksatz");
  assert.match(a.html(902), /Mein Satz/, "Schluss (freiwillig) erscheint");
});

test("Protokoll: Schluss-Satz A (Bausteine, falscher Baustein), B (Satzanfang), C (pflicht)", () => {
  const a = aufbau();
  a.zeige(902);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "6");
  a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 });
  a.act("fo-alle-pruefen", { nr: 902 });
  a.act("fo-schluss-fest", { nr: 902 });
  assert.match(a.letzteFb().html, /Tippe zuerst einen Satzbaustein an/);
  a.act("fo-schluss-wahl", { nr: 902, i: 1 });
  a.act("fo-schluss-fest", { nr: 902 });
  assert.equal(a.letzteFb().kind, "err");
  assert.match(a.letzteFb().html, /Zähle noch einmal/);
  a.act("fo-schluss-wahl", { nr: 902, i: 1 });   // abwählen
  a.act("fo-schluss-wahl", { nr: 902, i: 0 });
  a.act("fo-schluss-fest", { nr: 902 });
  assert.equal(a.log.antworten.at(-1).text, "Mein Satz: Ich habe beobachtet, dass die Biene sechs Beine hat.");
  assert.equal(a.log.antworten.at(-1).korrekt, null);
  // B: Satzanfang + Text
  const b = aufbau({ niveau: { 902: "B" } });
  b.zeige(902);
  b.input({ foInput: "zahl", nr: "902", z: "0" }, "4");
  b.act("fo-zeile-wahl", { nr: 902, z: 1, i: 0 }); b.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 }); b.act("fo-zeile-wahl", { nr: 902, z: 1, i: 3 });
  b.input({ foInput: "zahl", nr: "902", z: "2" }, "6");
  b.act("fo-alle-pruefen", { nr: 902 });
  assert.equal(b.state.completed.has("902"), true);
  b.input({ foInput: "schluss", nr: "902" }, "kurz");
  b.act("fo-schluss-fest", { nr: 902 });
  assert.match(b.letzteFb().html, /mindestens 15 Zeichen/);
  b.input({ foInput: "schluss", nr: "902" }, "die Biene vier Flügel hat.");
  b.act("fo-schluss-fest", { nr: 902 });
  assert.equal(b.log.antworten.at(-1).text, "Mein Satz: Ich habe beobachtet, dass die Biene vier Flügel hat.");
  // C: Toleranz, Textzeile, Schluss ist Pflicht
  const c = aufbau({ niveau: { 902: "C" } });
  c.zeige(902);
  c.input({ foInput: "zahl", nr: "902", z: "0" }, "15");
  c.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.equal(c.log.antworten.at(-1).korrekt, false, "15 liegt außerhalb von 13 ± 1");
  c.input({ foInput: "zahl", nr: "902", z: "0" }, "14");
  c.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.equal(c.log.antworten.at(-1).korrekt, true, "14 liegt innerhalb von 13 ± 1");
  c.input({ foInput: "ztext", nr: "902", z: "1" }, "Zwei große Augen");
  c.act("fo-alle-pruefen", { nr: 902 });
  assert.equal(c.state.completed.has("902"), false, "Schluss ist Pflicht (schluss.pflicht)");
  c.input({ foInput: "schluss", nr: "902" }, "ich zwei große Augen und kleine Punktaugen gesehen habe.");
  c.act("fo-schluss-fest", { nr: 902 });
  assert.equal(c.state.completed.has("902"), true);
});

test("Protokoll: −/+ Zähler beginnt bei 0, geht nicht unter 0 und schreibt in den Zustand", () => {
  const a = aufbau();
  a.zeige(902);
  a.act("fo-zahl", { nr: 902, z: 0, d: -1 });
  assert.equal(a.D()["902"].z[0].w, "0");
  a.act("fo-zahl", { nr: 902, z: 0, d: 1 });
  a.act("fo-zahl", { nr: 902, z: 0, d: 1 });
  assert.equal(a.D()["902"].z[0].w, "2");
});

// ── tabelle ──────────────────────────────────────────────────────────────────
test("Tabelle: ohne alle Felder keine Prüfung, falsche Zellen rot, richtige sperren, Hinweise nach Fehlern", () => {
  const a = aufbau();
  a.zeige(905);
  a.act("fo-zelle", { nr: 905, z: 0, s: 0, i: 0 });
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.match(a.letzteFb().html, /fehlen noch 5 Felder/);
  assert.equal(a.log.antworten.length, 0);
  const setze = (reihen) => reihen.forEach((r, i) => r.forEach((w, j) => { const d = a.D()["905"]; if (d.ok[i][j]) return; if (d.a[i][j] !== w) a.act("fo-zelle", { nr: 905, z: i, s: j, i: w }); }));
  setze([[0, 1, 1], [0, 1, 1]]);          // zwei falsche Zellen: (0,2) und (1,1)
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.equal(a.log.antworten.length, 1);
  assert.equal(a.log.antworten[0].korrekt, false);
  assert.match(a.log.antworten[0].text, /^Tabelle: 4 von 6 Feldern richtig – Hinterleib: Königin = lang ✅, Arbeiterin = mittel ✅, Drohne = mittel ❌ \| Stachel: Königin = hat einen ✅, Arbeiterin = hat keinen ❌, Drohne = hat keinen ✅/);
  assert.match(a.letzteFb().html, /2 Felder stimmen noch nicht/);
  assert.doesNotMatch(a.letzteFb().html, /dick|hat einen/, "keine Lösung in der Rückmeldung");
  assert.deepEqual(plain(a.D()["905"].ok), [[true, true, false], [true, false, true]]);
  assert.deepEqual(plain(a.D()["905"].x), [[false, false, true], [false, true, false]]);
  a.act("fo-zelle", { nr: 905, z: 0, s: 0, i: 2 });
  assert.equal(a.D()["905"].a[0][0], 0, "eine richtige Zelle ist gesperrt");
  assert.doesNotMatch(a.html(905), /Die Königin ist am längsten/, "Hinweis erst nach dem zweiten Fehler");
  setze([[0, 1, 0], [0, 1, 1]]);          // (0,2) jetzt 0 statt 2 – immer noch falsch; (1,1) unverändert falsch
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.match(a.html(905), /Achte auf den Hinterleib/, "nach dem zweiten Fehler zeigt die Zeile ihren Hinweis");
  setze([[0, 1, 2], [0, 0, 1]]);
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.equal(a.state.completed.has("905"), true);
  assert.match(a.letzteFb().html, /Die ganze Tabelle stimmt/);
  assert.match(a.html(905), /Die Drohne hat keinen Stachel/, "Merksatz");
});

test("Tabelle: Spaltenbilder (Objekte) und Zeilenbilder – Text, Bild, alt, loading=lazy, Zoom; Strings und Objekte gemischt", () => {
  const { logik: L } = aufbau();
  assert.equal(L.spaltenName("Kuh"), "Kuh");
  assert.equal(L.spaltenName({ name: "Huhn", bild: "/x.svg", alt: "Huhn" }), "Huhn");
  assert.equal(L.spaltenName({ bild: "/x.svg" }), "", "ohne name bleibt der Name leer (der Strukturtest verlangt ihn)");
  assert.equal(L.spaltenBild("Kuh"), null);
  assert.equal(L.spaltenBild({ name: "Kuh" }), null);
  assert.deepEqual(plain(L.spaltenBild({ name: "Kuh", bild: " /static/img/lese/tier-kuh.svg ", alt: "Eine Kuh" })), { src: "/static/img/lese/tier-kuh.svg", alt: "Eine Kuh" });
  assert.equal(L.spaltenBild({ name: "Schaf", bild: "/s.svg" }).alt, "Schaf", "ohne alt dient der Name als Rückfall – die Pflicht prüft der Strukturtest");
  assert.deepEqual(plain(L.zeilenBild({ merkmal: "Die Bienen", bild: "/b.jpg", alt: "Film: Bienen" })), { src: "/b.jpg", alt: "Film: Bienen" });
  assert.equal(L.zeilenBild({ merkmal: "Nur Text" }), null);
  // Antworttext: immer der Name, nie Pfad oder alt – auch bei gemischten Spalten und Emoji-Optionen
  const zeilen = [{ merkmal: "Gibt", optionen: ["🥛 Milch", "🥚 Eier", "🍯 Honig"], loesung: [0, 1, 2] }];
  const sp = [{ name: "Kuh", bild: "/k.svg", alt: "Kuh" }, "Huhn", { name: "Biene" }];
  assert.equal(L.tabelleText(zeilen, sp, [[0, 1, 1]], L.tabelleAuswerten([[0, 1, 1]], zeilen, 3).ok), "Gibt: Kuh = 🥛 Milch ✅, Huhn = 🥚 Eier ✅, Biene = 🥚 Eier ❌");

  const a = aufbau();
  a.zeige(905);
  const h = a.html(905);
  // Niveau A: drei Spaltenbilder + ein Zeilenbild
  const kopf = h.match(/<span role="columnheader" class="fo-spalte[^"]*">.*?<\/span><\/span>/g) || [];
  assert.equal(kopf.length, 3, "drei Spaltenköpfe");
  kopf.forEach((k, i) => {
    assert.match(k, /class="fo-spalte hat-bild"/);
    assert.match(k, /<img class="fo-sp-bild" src="\/static\/img\/lese\/bienenart-[a-z]+\.svg[^"]*" alt="[^"]+" loading="lazy"/);
    assert.match(k, new RegExp(`<span class="fo-sp-name">${["Königin", "Arbeiterin", "Drohne"][i]}</span>`), "der Name bleibt sichtbar");
  });
  assert.match(h, /class="fo-tabelle hat-spaltenbild hat-zeilenbild"/);
  // Stapelmodus: jedes Feld trägt Bild + Name im Etikett
  assert.equal((h.match(/<img class="fo-zl-bild"/g) || []).length, 6, "2 Zeilen × 3 Spalten");
  assert.match(h, /<span class="fo-zelle-label"><img class="fo-zl-bild"[^>]*alt="Königin" loading="lazy"[^>]*><span>Königin<\/span><\/span>/);
  // Zeilenbild: antippbar über bild.js, mit alt und lazy; die Zeile ohne Bild hat keinen Knopf
  const zeilenKnoepfe = h.match(/<button type="button" class="bild-zoom fo-zeilenbild" data-action="bild-open"[^>]*>.*?<\/button>/g) || [];
  assert.equal(zeilenKnoepfe.length, 1, "nur die Zeile mit Bild bekommt den Zoom-Knopf");
  assert.match(zeilenKnoepfe[0], /aria-label="Bild vergrößern: Film: Die Königin wird von Arbeiterinnen umringt"/);
  assert.match(zeilenKnoepfe[0], /<img src="\/static\/img\/film\/still-koenigin\.jpg[^"]*" alt="Film: Die Königin wird von Arbeiterinnen umringt" loading="lazy"/);
  // alle Bilder der Tabelle: alt nicht leer, lazy
  const bilder = h.match(/<img [^>]*>/g) || [];
  assert.equal(bilder.length, 3 + 6 + 1);
  bilder.forEach(b => { assert.match(b, /alt="[^"]+"/); assert.match(b, /loading="lazy"/); });
  assert.doesNotMatch(h, /<img [^>]*data-action/, "Spaltenbilder sind keine Tippziele");
  // Niveau B: Text, Objekt mit Bild, Objekt ohne Bild (nur Name) – gemischt
  const b = aufbau({ niveau: { 905: "B" } });
  b.zeige(905);
  const hb = b.html(905);
  assert.equal((hb.match(/<img class="fo-sp-bild"/g) || []).length, 1, "nur die Spalte mit bild bekommt ein Bild");
  assert.match(hb, /<span role="columnheader" class="fo-spalte"><span class="fo-sp-name">Königin<\/span><\/span>/, "Textspalte unverändert");
  assert.match(hb, /<span role="columnheader" class="fo-spalte"><span class="fo-sp-name">Drohne<\/span><\/span>/, "Objekt ohne Bild wie Text");
  assert.doesNotMatch(hb, /fo-zeilenbild|hat-zeilenbild/);
  // Niveau C: reiner Text wie bisher
  const c = aufbau({ niveau: { 905: "C" } });
  c.zeige(905);
  assert.doesNotMatch(c.html(905), /<img|hat-spaltenbild/);
});

// ── bildwahl ─────────────────────────────────────────────────────────────────
test("Bildwahl: falscher Kreis wird rot und verrät nichts, richtiger löst die Runde, Weiter, letzte Runde → erledigt", () => {
  const a = aufbau({ niveau: { 906: "B" } });
  a.zeige(906);
  assert.match(a.html(906), /Runde 1 von 2/);
  a.act("fo-ziel", { nr: 906, i: 1 });
  assert.equal(a.log.antworten.at(-1).korrekt, false);
  assert.equal(a.log.antworten.at(-1).text, "Wo ist das Futter? · Runde 1: Bereich 2 gewählt ❌".replace("Wo ist das Futter?", "Wo ist das Futter?"));
  assert.match(a.letzteFb().html, /Hier ist es nicht/);
  assert.doesNotMatch(a.letzteFb().html, /rechts/, "die Lösung steht nicht in der Rückmeldung");
  a.act("fo-ziel", { nr: 906, i: 1 });
  assert.equal(a.D()["906"].falsch[0].length, 1, "ein schon falscher Kreis zählt nicht doppelt");
  a.act("fo-ziel", { nr: 906, i: 2 });
  assert.match(a.letzteFb().html, /Sieh genau hin/, "nach dem zweiten Fehler kommt der Hinweis der Runde");
  a.act("fo-ziel", { nr: 906, i: 0 });
  assert.equal(a.log.antworten.at(-1).korrekt, true);
  assert.match(a.log.antworten.at(-1).text, /Runde 1: Bereich 1 gewählt ✅ \(3\. Versuch\)/);
  assert.match(a.html(906), /Die Wiese liegt rechts/, "Erklärung nach der richtigen Wahl");
  assert.match(a.html(906), /Weiter zu Runde 2/);
  assert.equal(a.state.completed.has("906"), false);
  a.act("fo-ziel", { nr: 906, i: 1 });
  assert.equal(a.D()["906"].falsch[0].length, 2, "gelöste Runde ist gesperrt");
  a.act("fo-bild-weiter", { nr: 906 });
  assert.equal(a.D()["906"].runde, 1);
  assert.match(a.html(906), /Runde 2 von 2/);
  a.act("fo-ziel", { nr: 906, i: 1 });
  assert.equal(a.state.completed.has("906"), true);
  assert.match(a.html(906), /Alle 2 Runden geschafft/);
  assert.match(a.html(906), /Der Tanz zeigt den Bienen/, "Merksatz");
});

test("Bildwahl: Tipp neben die Kreise wird über die Bildkoordinaten ausgewertet", () => {
  const a = aufbau();
  a.zeige(906);
  const svg = { tagName: "svg", getBoundingClientRect: () => ({ left: 0, top: 0, width: 450, height: 280 }), viewBox: { baseVal: { width: 900, height: 560 } }, closest: () => null };
  const ev = (x, y) => ({ clientX: x, clientY: y, target: { closest: () => null } });
  a.actions["fo-bild"](Object.assign({ dataset: { nr: "906" } }, svg), ev(350, 90));       // ≈ Bildkoordinate (700, 180) = Ziel 1 (richtig)
  assert.equal(a.state.completed.has("906"), true);
  const b = aufbau();
  b.zeige(906);
  b.actions["fo-bild"](Object.assign({ dataset: { nr: "906" } }, svg), ev(10, 10));        // daneben
  assert.match(b.letzteFb().html, /Tippe in einen der Kreise/);
  assert.equal(b.log.antworten.length, 0, "ein Tipp ins Leere zählt nicht");
});

// ── Zustand hin und zurück ───────────────────────────────────────────────────
test("Zustand hin und zurück: alles aus collect() lässt sich per apply() wiederherstellen (Neuladen)", () => {
  const a = aufbau({ niveau: { 902: "A", 905: "A" } });
  vermutungFesthalten(a, 901, 3);
  a.zeige(903); a.act("fo-pr-einsch", { nr: 903, i: 0 }); a.act("fo-pr-erk", { nr: 903, i: 0 });
  a.zeige(902); a.input({ foInput: "zahl", nr: "902", z: "0" }, "6"); a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  a.zeige(905); a.act("fo-zelle", { nr: 905, z: 0, s: 0, i: 0 });
  a.zeige(906); a.act("fo-ziel", { nr: 906, i: 1 });
  const gespeichert = a.regs.forschen.collect();
  assert.ok(gespeichert["901"] && gespeichert["902"] && gespeichert["903"] && gespeichert["905"] && gespeichert["906"]);
  const kopie = JSON.parse(JSON.stringify(gespeichert));

  const b = aufbau();
  b.regs.forschen.apply(kopie);
  assert.equal(b.fo.vermutungTextFuer("v_anzahl"), "etwa 50 000");
  assert.deepEqual(plain(b.D()["903"].erk.falsch), [0]);
  assert.equal(b.D()["903"].einsch, 0);
  assert.equal(b.D()["902"].z[0].w, "6");
  assert.equal(b.D()["902"].z[0].ok, true);
  assert.equal(b.D()["905"].a[0][0], 0);
  assert.deepEqual(plain(b.D()["906"].falsch[0]), [1]);
  assert.ok(b.log.neu.includes("901") && b.log.neu.includes("903") && b.log.neu.includes("913"), "alle Karten werden neu gezeichnet (pruefen und forscherbuch brauchen die Vermutung)");
  b.zeige(903);
  assert.match(b.html(903), /etwa 50 000/);
  assert.match(b.html(903), /incorrect/);
  assert.equal(JSON.stringify(b.regs.forschen.collect()), JSON.stringify(gespeichert), "collect nach apply liefert denselben Stand");
});

test("Zustand: kaputte Daten aus Autosave/Archiv werden bereinigt statt zu stören", () => {
  const a = aufbau();
  a.regs.forschen.apply({
    "901": { niveau: "A", wahl: [99, -1, "x", 2, 2], satz: 42, fest: true, text: "Meine Vermutung", antwort: "Vermutung: x" },
    "902": { niveau: "A", z: [{ w: { boese: 1 }, ok: "ja", f: -3 }], schluss: { wahl: 77 } },
    "903": { niveau: "Z", einsch: 9, erk: { ok: 99, falsch: [0, 0, 55] }, beleg: null },
    "905": { niveau: "A", a: "keine Liste", ok: [[true]], f: [-1], x: 5 },
    "906": { niveau: "A", runde: 99, ok: [true], versuche: ["a"], falsch: [[5, 0]] },
    "913": { niveau: "A", wahl: [0] },                 // Forscherbuch speichert nichts
    "99999": { niveau: "A" },                          // unbekannte Aufgabe
    "904": { niveau: "A" },                            // anderer Typ
  });
  const D = a.D();
  assert.deepEqual(plain(D["901"].wahl), [2]);
  assert.equal(D["901"].satz, "42");
  assert.equal(D["901"].fest, true);
  assert.equal(D["902"].z.length, 2, "je Zeile des Niveaus ein Eintrag");
  assert.deepEqual(D["902"].z[0], { w: D["902"].z[0].w, ok: true, f: 0, g: false });
  assert.equal(typeof D["902"].z[0].w, "string", "auch ein Objekt wird zu Text");
  assert.deepEqual(D["902"].z[1], { w: null, ok: false, f: 0, g: false });
  assert.equal(D["902"].schluss.wahl, null);
  assert.equal(D["903"].niveau, "A");
  assert.equal(D["903"].einsch, null);
  assert.equal(D["903"].erk.ok, null);
  assert.deepEqual(plain(D["903"].erk.falsch), [0]);
  assert.deepEqual(plain(D["905"].a), [[null, null, null], [null, null, null]]);
  assert.equal(D["906"].runde, 0, "bei einer Runde im Niveau A ist 0 die letzte gültige");
  assert.deepEqual(plain(D["906"].falsch), [[0]]);
  assert.equal(D["913"], undefined);
  assert.equal(D["99999"], undefined);
  assert.equal(D["904"], undefined);
  assert.doesNotThrow(() => a.regs.forschen.apply(null));
  assert.doesNotThrow(() => a.regs.forschen.apply("kaputt"));
  assert.doesNotThrow(() => a.regs.forschen.apply({ "901": 5, "902": [], "903": null }));
});

test("Autosave: ein frisch angelegter, leerer Zustand wird nicht gespeichert", () => {
  const a = aufbau();
  a.zeige(902); a.zeige(905); a.zeige(906); a.zeige(903);
  assert.equal(a.regs.forschen.collect(), undefined);
  assert.equal(a.regs.forschen.order, 32);
});

// ── Forscherbuch ─────────────────────────────────────────────────────────────
test("Forscherbuch: Forscherfrage → Vermutung → Erkenntnis je Reiter, plus Notizen; leer solange nichts da ist", () => {
  const a = aufbau();
  let buch = a.fo.buchEingabe();
  assert.equal(a.logik.buchLeer(buch.map((r) => Object.assign(r, { notizen: [] }))), false, "die Forscherfragen stehen schon im Buch");
  assert.equal(buch[0].eintraege[0].vermutung, null);
  assert.deepEqual(plain(buch[0].eintraege[0].erkenntnisse), []);
  vermutungFesthalten(a, 901, 3);
  a.zeige(903); a.act("fo-pr-einsch", { nr: 903, i: 0 }); a.act("fo-pr-erk", { nr: 903, i: 1 });
  a.zeige(902); a.input({ foInput: "zahl", nr: "902", z: "0" }, "6"); a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 }); a.act("fo-alle-pruefen", { nr: 902 });
  buch = a.fo.buchEingabe();
  const n = buch[0];
  assert.equal(n.label, "Nutztier Biene");
  assert.equal(n.eintraege[0].frage, "Wie viele Bienen leben im Sommer in einem Stock?");
  assert.equal(n.eintraege[0].vermutung, "etwa 50 000");
  assert.deepEqual(plain(n.eintraege[0].erkenntnisse), ["Im Sommer leben bis zu etwa 50 000 Bienen in einem Stock."]);
  assert.deepEqual(plain(n.weitere), ["Eine Biene hat drei Körperteile, sechs Beine und vier Flügel."], "Merksatz des Protokolls");
  const text = a.logik.buchText(buch, "Testkind, Klasse 6a");
  assert.match(text, /^Mein Forscherbuch – Testkind, Klasse 6a/);
  assert.match(text, /== Nutztier Biene ==\nForscherfrage: Wie viele Bienen leben im Sommer in einem Stock\?\nMeine Vermutung: etwa 50 000\nMeine Einschätzung: stimmt\nMeine Erkenntnis: Im Sommer leben bis zu etwa 50 000 Bienen in einem Stock\./);
  assert.match(text, /Das habe ich noch herausgefunden:\n- Eine Biene hat drei/);
  assert.match(text, /Meine Vermutung: noch nicht festgehalten/, "andere Reiter: noch offen");
  const htmlText = a.logik.buchHTML(buch);
  assert.match(htmlText, /Nutztier Biene/);
  assert.match(htmlText, /Forscherfrage/);
  assert.match(htmlText, /noch nicht herausgefunden/);
  assert.doesNotMatch(htmlText, /<script/i);
});

test("Forscherbuch: Notizen der Kinder kommen mit, HTML wird maskiert", () => {
  const a = aufbau();
  a.els["nt-nutztier"] = { value: "• Bienen sind <b>Nutztiere</b>\n• Der Imker kümmert sich", id: "nt-nutztier" };
  const buch = a.fo.buchEingabe();
  assert.equal(buch[0].notizen.length, 1);
  const h = a.logik.buchHTML(buch);
  assert.match(h, /Meine Notizen/);
  assert.match(h, /&lt;b&gt;Nutztiere&lt;\/b&gt;/);
  assert.doesNotMatch(h, /<b>Nutztiere/);
  assert.match(a.logik.buchText(buch), /Meine Notizen:\n• Bienen sind <b>Nutztiere<\/b>/, "im Text bleibt alles wörtlich");
});

test("Forscherbuch abgeben: ein langer, lesbarer Text geht ans Protokoll, die Station ist erledigt", () => {
  const a = aufbau();
  vermutungFesthalten(a, 901, 3);
  a.act("fo-buch-abgabe", { nr: 913 });
  const s = a.log.antworten.at(-1);
  assert.equal(s.typ, "forscherbuch");
  assert.equal(s.max, 8000, "das Forscherbuch darf länger sein als 400 Zeichen");
  assert.equal(s.korrekt, null);
  assert.match(s.text, /Mein Forscherbuch – Testkind, Klasse 6a/);
  assert.match(s.text, /Meine Vermutung: etwa 50 000/);
  assert.equal(a.state.completed.has("913"), true);
});

// ── Prüfmodus ────────────────────────────────────────────────────────────────
test("Prüfmodus: Lösungen sichtbar, Vermutung und Erkenntnis ausgefüllt vorzeigbar, Forscherbuch gefüllt", () => {
  const a = aufbau({ pruef: true });
  a.zeige(903);
  assert.match(a.html(903), /Beispiel im Prüfmodus/, "die Vermutung erscheint als Beispiel");
  assert.match(a.html(903), /fo-loesung/, "richtige Antworten markiert");
  assert.match(a.html(903), /Merke/);
  assert.match(a.html(903), /Prüfmodus/);
  a.zeige(902);
  assert.match(a.html(902), /Lösung: 6/);
  a.zeige(905);
  assert.match(a.html(905), /fo-loesung/);
  a.zeige(906);
  assert.match(a.html(906), /Richtig ist Bereich 1/);
  a.zeige(901);
  assert.match(a.html(901), /Beispiel festhalten/);
  const buch = a.fo.buchEingabe();
  assert.match(buch[0].eintraege[0].vermutung, /Beispiel im Prüfmodus/);
  assert.equal(buch[0].eintraege[0].erkenntnisse.length, 1, "Erkenntnis ohne Bearbeiten sichtbar");
  assert.ok(buch[0].weitere.length >= 1);
  assert.equal(a.logik.buchLeer(buch), false);
});

test("Alle Typen rendern auf allen Niveaus ohne Fehler und ohne unmaskiertes HTML", () => {
  for (const n of ["A", "B", "C"]) {
    const a = aufbau({ niveau: Object.fromEntries([901, 902, 903, 905, 906, 907, 908, 909, 910, 911, 912].map((x) => [x, n])), pruef: n === "C" });
    for (const nr of [901, 902, 903, 905, 906, 907, 908, 909, 910, 911, 912, 913]) {
      const t = a.nr(nr);
      let h;
      assert.doesNotThrow(() => { h = a.fo.render(t); }, `Aufgabe ${nr} Niveau ${n}`);
      assert.ok(h.includes('class="fo-wrap'), `Aufgabe ${nr} Niveau ${n}: Wrapper fehlt`);
      assert.doesNotMatch(h, /undefined|\[object Object\]|NaN/, `Aufgabe ${nr} Niveau ${n}`);
      assert.doesNotMatch(h, /Für dieses Niveau fehlen Angaben/, `Aufgabe ${nr} Niveau ${n}`);
    }
  }
});

test("Fehlende Angaben im Niveau führen zu einem freundlichen Hinweis, nicht zu einem Absturz", () => {
  const a = aufbau();
  const t = a.nr(902);
  const kaputt = JSON.parse(JSON.stringify(t));
  kaputt.niveaus.A = {};
  a.BIE.aufgabenByNr[902] = kaputt;
  assert.match(a.fo.render(kaputt), /fehlen Angaben/);
  const t2 = JSON.parse(JSON.stringify(a.nr(905))); t2.niveaus.A = { spalten: [], zeilen: [] };
  assert.match(a.fo.render(t2), /fehlen Angaben/);
});

test("Der Zeilen-Knopf öffnet genau die Ansicht der Zeile (BIE.film.befehle)", () => {
  const a = aufbau();
  a.act("fo-modell", { nr: 902, z: 0 });
  assert.deepEqual(plain(a.log.befehle), [{ id: "biene3d", liste: [{ mw: "blick", name: "seite" }] }]);
  const b = aufbau({ niveau: { 911: "A" } });
  b.act("fo-modell", { nr: 911, z: 0 });
  assert.deepEqual(plain(b.log.befehle), [{ id: "volk", liste: [{ mw: "kapitel", n: 10 }] }]);
  const c = aufbau();
  c.act("fo-modell", { nr: 902, z: 1 });
  assert.equal(c.log.befehle.length, 0, "Zeile ohne Knopf: nichts passiert");
});

test("Forscherbuch: Vermutung und Prüfen werden über die id über ALLE Reiter gepaart, die Erkenntnis steht nicht doppelt", () => {
  // Prüfen 912 (Reiter nutzen) prüft die Vermutung v_anzahl aus dem Reiter nutztier
  const a = aufbau({ mut: (F) => { F.tabs[3].aufgaben[2].vermutung = "v_anzahl"; } });
  vermutungFesthalten(a, 901, 3);
  a.zeige(912); a.act("fo-pr-einsch", { nr: 912, i: 0 }); a.act("fo-pr-erk", { nr: 912, i: 0 });
  assert.equal(a.state.completed.has("912"), true);
  assert.match(a.html(912), /etwa 50 000/, "Prüfen zeigt die Vermutung aus dem anderen Reiter");
  const buch = a.fo.buchEingabe();
  const nutztier = buch.find((r) => r.key === "nutztier"), nutzen = buch.find((r) => r.key === "nutzen");
  assert.deepEqual(plain(nutztier.eintraege[0].erkenntnisse), ["Der Honig ist der Wintervorrat der Bienen."], "Erkenntnis beim Eintrag der Vermutung");
  assert.deepEqual(plain(nutzen.weitere), [], "nicht noch einmal unter „weitere“ im Reiter, in dem geprüft wurde");
  assert.deepEqual(plain(nutzen.eintraege[0].erkenntnisse), [], "die Vermutung v_honig hat kein eigenes Prüfen mehr");
  const text = a.logik.buchText(buch);
  assert.equal((text.match(/Wintervorrat/g) || []).length, 1, "genau einmal im Text");
});

test("Niveauwechsel setzt die Karte zurück: Tabelle und Forscherbogen zeigen wieder Prüfen-Knöpfe, keinen Merksatz (auch bei bleibendem state.completed)", () => {
  const a = aufbau({ niveau: { 905: "A", 902: "A" } });
  a.zeige(905);
  [[0, 1, 2], [0, 0, 1]].forEach((r, i) => r.forEach((w, j) => a.act("fo-zelle", { nr: 905, z: i, s: j, i: w })));
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.equal(a.state.completed.has("905"), true);
  assert.match(a.html(905), /Merke/);
  assert.doesNotMatch(a.html(905), /fo-tab-pruefen/, "fertig: kein Prüfen-Knopf mehr");
  a.state.niveau[905] = "B";                       // state.completed bleibt (Gerüst), die Karte beginnt neu
  a.zeige(905);
  assert.match(a.html(905), /fo-tab-pruefen/, "neue Stufe: der Prüfen-Knopf ist wieder da");
  assert.doesNotMatch(a.html(905), /Merke/);
  assert.equal(a.state.completed.has("905"), true);
  // Forscherbogen genauso
  a.zeige(902);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "6"); a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 }); a.act("fo-alle-pruefen", { nr: 902 });
  assert.match(a.html(902), /Merke/);
  a.state.niveau[902] = "B"; a.zeige(902);
  assert.doesNotMatch(a.html(902), /Merke/);
  assert.match(a.html(902), /fo-alle-pruefen/);
});

test("Bildwahl mit nur einer Runde: kein „Alle 1 Runden“", () => {
  const a = aufbau();   // 906 Niveau A hat eine Runde
  a.zeige(906);
  assert.doesNotMatch(a.html(906), /Runde 1 von 1/);
  a.act("fo-ziel", { nr: 906, i: 0 });
  assert.match(a.html(906), /Geschafft/);
  assert.doesNotMatch(a.html(906), /Alle 1 Runden/);
});

// ═══ Audit 4. Oktober 2026 (docs/AUDIT_FORSCHEN_2026-10-04.md): T1–T4, T8 ═══════════════════════════════
// ── T4: Zahlwörter und Tausenderformate ──────────────────────────────────────
test("T4 Zahlen: Zahlwörter über zwölf, Tausenderformate und Einheiten", () => {
  const { logik: L } = aufbau();
  const erwartet = {
    einundzwanzig: 21, "Einundzwanzig": 21, zweitausend: 2000, "fünfzigtausend": 50000, "fünfzig tausend": 50000, fuenfzigtausend: 50000, "50 000": 50000, "50.000": 50000,
    "50000": 50000, zweihundertdreiundvierzig: 243, hundert: 100, hunderttausend: 100000, "dreißig": 30, dreissig: 30, achtzehn: 18, neunundneunzig: 99, einhundertzwei: 102,
    eintausendzweihundert: 1200, "zwölf": 12, "sechs Beine": 6, "50 000 Bienen": 50000, "fünfzigtausend Bienen": 50000, "6,5": 6.5, "12.500": 12500, "1,5": 1.5, "6.": 6, null: 0,
  };
  Object.entries(erwartet).forEach(([eingabe, n]) => assert.equal(L.parseZahl(eingabe), n, `„${eingabe}“ → ${n}`));
  ["viel", "", "2 3", "abc 5", "sechsundsechzigtausendx", "tausendeins2"].forEach((s) => assert.equal(L.parseZahl(s), null, `„${s}“ ist keine Zahl`));
  assert.equal(L.zeileAuswerten({ art: "zahl", loesung: 50000 }, "fünfzigtausend").ok, true);
  assert.equal(L.zeileAuswerten({ art: "zahl", loesung: 21 }, "einundzwanzig").ok, true);
  assert.equal(L.zeileAuswerten({ art: "zahl", loesung: 50000 }, "50 000").ok, true);
});

test("T4 Zahleingabe: keine Zahl → Hinweis zum Format; fehlertext der Zeile überschreibt; eine falsche Zahl bekommt den Standardtext", () => {
  const a = aufbau();
  a.zeige(902);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "viele");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(a.html(902), /Schreibe eine Zahl, zum Beispiel 12\./);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "5");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(a.html(902), /Zähle noch einmal genau nach/);
  const b = aufbau({ mut: (F) => { F.tabs[0].aufgaben[1].niveaus.A.zeilen[0].fehlertext = "Schreibe die Zahl mit Ziffern, z. B. 12."; } });
  b.zeige(902);
  b.input({ foInput: "zahl", nr: "902", z: "0" }, "viele");
  b.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.match(b.html(902), /Schreibe die Zahl mit Ziffern/);
});

// ── T3: Raten verhindern ─────────────────────────────────────────────────────
const tabelleSetzen = (a, reihen) => reihen.forEach((r, i) => r.forEach((w, j) => { const d = a.D()["905"]; if (!d.ok[i][j] && d.a[i][j] !== w) a.act("fo-zelle", { nr: 905, z: i, s: j, i: w }); }));

test("T3 Tabelle: die erste Prüfung zählt nur (keine Färbung, nichts gesperrt); gefärbt wird ab der zweiten; Prüfen ohne Änderung zählt nicht", () => {
  const a = aufbau({ sofortFaerben: false });
  a.zeige(905);
  assert.match(a.html(905), /Beim ersten Prüfen siehst du nur, wie viele Felder stimmen/);
  tabelleSetzen(a, [[0, 1, 1], [0, 1, 1]]);                       // 4 von 6 richtig
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.match(a.letzteFb().html, /4 von 6 Feldern stimmen\. Welche das sind/);
  assert.doesNotMatch(a.letzteFb().html, /rot/, "nichts ist rot");
  assert.deepEqual(a.D()["905"].ok.flat(), Array(6).fill(false), "nichts gesperrt");
  assert.deepEqual(a.D()["905"].x.flat(), Array(6).fill(false), "nichts gefärbt");
  assert.doesNotMatch(a.html(905), /is-ok|is-falsch/);
  assert.equal(a.D()["905"].pr, 1);
  assert.equal(a.log.antworten.length, 1, "die Lehrkraft sieht den Versuch");
  assert.match(a.log.antworten[0].text, /^Tabelle: 4 von 6 Feldern richtig/);
  assert.equal(a.log.antworten[0].korrekt, false);
  a.act("fo-tab-pruefen", { nr: 905 });                           // ohne Änderung
  assert.match(a.letzteFb().html, /nichts geändert/);
  assert.equal(a.log.antworten.length, 1, "zählt nicht als Fehlversuch");
  assert.equal(a.D()["905"].pr, 1);
  assert.deepEqual(plain(a.D()["905"].f), [1, 1], "je Zeile ein gezählter Versuch");
  tabelleSetzen(a, [[0, 1, 1], [0, 0, 1]]);                       // eine Zelle geändert: jetzt wird gefärbt
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.match(a.html(905), /is-ok/);
  assert.equal(a.D()["905"].ok.flat().filter(Boolean).length, 5);
  assert.deepEqual(plain(a.D()["905"].x), [[false, false, true], [false, false, false]]);
  assert.equal(a.D()["905"].pr, 2);
  assert.match(a.letzteFb().html, /1 Feld stimmt noch nicht – sie sind rot/);
  const n = a.log.antworten.length;
  a.act("fo-tab-pruefen", { nr: 905 });                           // wieder ohne Änderung
  assert.equal(a.log.antworten.length, n);
  assert.match(a.letzteFb().html, /nichts geändert/);
  assert.deepEqual(plain(a.D()["905"].f), [2, 1], "Zeile 1 hat zwei Fehlversuche, Zeile 2 nur den ersten");
  tabelleSetzen(a, [[0, 1, 2], [0, 0, 1]]);
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.equal(a.state.completed.has("905"), true);
});

test("T3 Tabelle: alles richtig schon bei der ersten Prüfung → sofort gefärbt und erledigt; sofortFaerben: true färbt von Anfang an", () => {
  const a = aufbau({ sofortFaerben: false });
  a.zeige(905);
  tabelleSetzen(a, [[0, 1, 2], [0, 0, 1]]);
  a.act("fo-tab-pruefen", { nr: 905 });
  assert.equal(a.state.completed.has("905"), true);
  assert.match(a.letzteFb().html, /Die ganze Tabelle stimmt/);
  const b = aufbau({ sofortFaerben: true });
  b.zeige(905);
  assert.doesNotMatch(b.html(905), /Beim ersten Prüfen/);
  tabelleSetzen(b, [[0, 1, 1], [0, 1, 1]]);
  b.act("fo-tab-pruefen", { nr: 905 });
  assert.match(b.html(905), /is-falsch/, "sofort gefärbt");
  assert.deepEqual(plain(b.D()["905"].x), [[false, false, true], [false, true, false]]);
});

test("T3 Tabelle: pr und sig stehen im Autosave und überstehen das Neuladen (die erste Prüfung bleibt die erste)", () => {
  const a = aufbau({ sofortFaerben: false });
  a.zeige(905);
  tabelleSetzen(a, [[0, 1, 1], [0, 1, 1]]);
  a.act("fo-tab-pruefen", { nr: 905 });
  const kopie = JSON.parse(JSON.stringify(a.regs.forschen.collect()));
  assert.equal(kopie["905"].pr, 1);
  const b = aufbau({ sofortFaerben: false });
  b.regs.forschen.apply(kopie);
  b.zeige(905);
  b.act("fo-tab-pruefen", { nr: 905 });
  assert.match(b.letzteFb().html, /nichts geändert/, "die Signatur kommt aus dem Speicher");
  assert.equal(b.D()["905"].pr, 1);
  // kaputte Werte werden bereinigt
  const c = aufbau({ sofortFaerben: false });
  c.regs.forschen.apply({ 905: { niveau: "A", a: [[0, 0, 0], [0, 0, 0]], ok: [], f: [], x: [], pr: "viel", sig: 5 } });
  assert.equal(c.D()["905"].pr, 0);
  assert.equal(c.D()["905"].sig, "5");
});

test("T3 Protokoll: die erste Prüfung zählt nur alle ausgefüllten Zeilen, färbt nichts und sperrt nichts; ab der zweiten gefärbt; Prüfen ohne Änderung zählt nicht", () => {
  const a = aufbau({ sofortFaerben: false });
  a.zeige(902);
  a.act("fo-alle-pruefen", { nr: 902 });
  assert.match(a.letzteFb().html, /Trage zuerst etwas ein/);
  assert.equal(a.D()["902"].pr, 0, "ein leeres Prüfen ist keine Prüfung");
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "5");
  a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 });                // Zeile 1 falsch, Zeile 2 richtig
  a.act("fo-zeile-pruefen", { nr: 902, z: 1 });                   // ein Zeilenknopf prüft in der ersten Prüfung ALLE Zeilen
  assert.match(a.letzteFb().html, /1 von 2 ausgefüllten Zeilen stimmt\./);
  assert.doesNotMatch(a.letzteFb().html, /Beine|hinten/, "nichts wird verraten");
  assert.deepEqual(plain(a.D()["902"].z.map((z) => [z.ok, z.g])), [[false, false], [false, false]], "nichts gefärbt, nichts gesperrt");
  assert.doesNotMatch(a.html(902), /is-ok|is-falsch|fo-err|fo-ok/);
  assert.equal(a.D()["902"].pr, 1);
  assert.equal(a.log.antworten.length, 2, "je Zeile ein Eintrag für die Lehrkraft");
  assert.deepEqual(a.log.antworten.map((x) => x.korrekt), [false, true]);
  a.act("fo-alle-pruefen", { nr: 902 });                          // ohne Änderung
  assert.match(a.letzteFb().html, /nichts geändert/);
  assert.equal(a.log.antworten.length, 2, "zählt nicht");
  assert.equal(a.D()["902"].z[0].f, 1);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "7");           // Änderung → zweite Prüfung färbt
  a.act("fo-alle-pruefen", { nr: 902 });
  assert.equal(a.D()["902"].pr, 2);
  assert.equal(a.D()["902"].z[0].g, true);
  assert.equal(a.D()["902"].z[1].ok, true, "die richtige Zeile ist jetzt gesperrt");
  assert.match(a.html(902), /fo-err/);
  assert.equal(a.D()["902"].z[0].f, 2);
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });                   // Zeile unverändert
  assert.match(a.letzteFb().html, /nichts geändert/);
  assert.equal(a.D()["902"].z[0].f, 2, "kein weiterer Fehlversuch");
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "sechs");
  a.act("fo-zeile-pruefen", { nr: 902, z: 0 });
  assert.equal(a.D()["902"].z[0].ok, true);
  assert.equal(a.state.completed.has("902"), true);
});

test("T3 Protokoll: alles richtig und ausgefüllt schon bei der ersten Prüfung → gleich erledigt; Enter im Zahlfeld prüft wie der Knopf", () => {
  const a = aufbau({ sofortFaerben: false });
  a.zeige(902);
  a.input({ foInput: "zahl", nr: "902", z: "0" }, "6");
  a.act("fo-zeile-wahl", { nr: 902, z: 1, i: 2 });
  a.act("fo-alle-pruefen", { nr: 902 });
  assert.equal(a.state.completed.has("902"), true);
  assert.equal(a.D()["902"].z.every((z) => z.ok), true);
  const b = aufbau({ sofortFaerben: false });
  b.zeige(902);
  b.input({ foInput: "zahl", nr: "902", z: "0" }, "6");
  (b.listener.keydown || []).forEach((fn) => fn({ key: "Enter", target: { dataset: { foInput: "zahl", nr: "902", z: "0" } }, preventDefault() {} }));
  assert.match(b.letzteFb().html, /1 von 1 ausgefüllten Zeilen stimmt\./);
});

// ── T2: pruefen ──────────────────────────────────────────────────────────────
test("T2 pruefen: vier Selbsteinschätzungen, die vierte „Das kann ich hier nicht herausfinden“ sperrt nichts", () => {
  const a = aufbau();
  vermutungFesthalten(a, 901, 1);
  a.zeige(903);
  assert.equal((a.html(903).match(/data-action="fo-pr-einsch"/g) || []).length, 4);
  assert.match(a.html(903), /Das kann ich hier nicht herausfinden/);
  assert.match(a.html(903), /Alle Antworten sind in Ordnung/);
  a.act("fo-pr-einsch", { nr: 903, i: 3 });
  assert.equal(a.log.antworten.at(-1).text, "Einschätzung meiner Vermutung: kann ich hier nicht herausfinden");
  assert.match(a.html(903), /Was hast du herausgefunden/, "die Erkenntnis bleibt wählbar");
  a.act("fo-pr-erk", { nr: 903, i: 1 });
  assert.equal(a.state.completed.has("903"), true);
  assert.match(a.log.antworten.at(-1).text, /Einschätzung: kann ich hier nicht herausfinden · Erkenntnis: /);
  a.regs.forschen.apply(JSON.parse(JSON.stringify(a.regs.forschen.collect())));            // der Index 3 übersteht das Neuladen
  assert.equal(a.D()["903"].einsch, 3);
  const b = aufbau();
  b.regs.forschen.apply({ 903: { niveau: "A", einsch: 4, erk: { ok: null, falsch: [] }, beleg: { ok: null, falsch: [] }, satz: "", fertig: false } });
  assert.equal(b.D()["903"].einsch, null, "Index 4 gibt es nicht");
});

test("T2 pruefen: die Fehlermeldung nennt bei der Beleg-Frage NIE „was du beobachtet hast“; fehltext je Frage überschreibt den Standard", () => {
  const a = aufbau({ niveau: { 903: "B" } });
  a.zeige(903);
  a.act("fo-pr-einsch", { nr: 903, i: 0 });
  a.act("fo-pr-erk", { nr: 903, i: 0 });
  assert.match(a.letzteFb().html, /Das passt noch nicht zu dem, was du beobachtet hast/, "Erkenntnis-Frage: wie bisher");
  a.act("fo-pr-erk", { nr: 903, i: 1 });
  a.act("fo-pr-beleg", { nr: 903, i: 1 });
  assert.equal(a.letzteFb().kind, "err");
  assert.doesNotMatch(a.letzteFb().html, /beobachtet/);
  assert.match(a.letzteFb().html, /Dieser Beleg passt noch nicht/);
  const b = aufbau({ niveau: { 903: "B" }, mut: (F) => { const c = F.tabs[0].aufgaben[2].niveaus.B; c.beleg.fehltext = "Daraus folgt das noch nicht."; c.erkenntnis.fehltext = "Das widerspricht dem Film."; } });
  b.zeige(903);
  b.act("fo-pr-einsch", { nr: 903, i: 0 });
  b.act("fo-pr-erk", { nr: 903, i: 0 });
  assert.match(b.letzteFb().html, /Das widerspricht dem Film\./);
  b.act("fo-pr-erk", { nr: 903, i: 1 });
  b.act("fo-pr-beleg", { nr: 903, i: 1 });
  assert.match(b.letzteFb().html, /Daraus folgt das noch nicht\./);
  assert.doesNotMatch(b.letzteFb().html, /beobachtet/);
});

// ── T1: Knopflisten und Bild-Knöpfe in Zeilen ────────────────────────────────
test("T1 Zeilen-Knöpfe: eine Liste zeigt alle Knöpfe, ein Bild-Knopf trägt 🖼️; jeder geht über BIE.film.knopf (spielt, springt, öffnet das Bild)", () => {
  const knoepfe = [
    { film: "volk", text: "▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)", befehle: [{ mw: "springe", t: 90 }] },
    { film: "biene3d", text: "Bein von hinten zeigen", befehle: [{ mw: "blick", name: "hinten" }] },
    { bild: "/static/img/lese/imker-karte.svg", text: "Bild noch einmal ansehen", alt: "Karte beim Imker" },
  ];
  const a = aufbau({ knopf: true, mut: (F) => { F.tabs[0].aufgaben[1].niveaus.A.zeilen[1].modell = knoepfe; } });
  a.zeige(902);
  const h = a.html(902);
  assert.equal((h.match(/data-action="fo-modell" data-nr="902" data-z="1"/g) || []).length, 3);
  assert.match(h, /<span class="fo-modellreihe">/);
  assert.match(h, /data-k="0">▶ Hör zu: ‚Befehle gibt sie aber nicht‘ \(Kapitel 5\)<\/button>/, "F6: die Beschriftung beginnt schon mit ▶ – kein zweites Symbol davor");
  assert.doesNotMatch(h, /🎭 ▶/);
  assert.match(h, /🖼️ Bild noch einmal ansehen/);
  assert.match(h, /🧊 Bein von hinten zeigen/);
  a.act("fo-modell", { nr: 902, z: 1, k: 0 });
  a.act("fo-modell", { nr: 902, z: 1, k: 2 });
  assert.deepEqual(plain(a.log.knoepfe.map((k) => k.text)), ["▶ Hör zu: ‚Befehle gibt sie aber nicht‘ (Kapitel 5)", "Bild noch einmal ansehen"]);
  assert.equal(a.log.befehle.length, 0, "mit film.knopf wird nichts doppelt geschickt");
  a.act("fo-modell", { nr: 902, z: 1, k: 9 });                      // gibt es nicht
  assert.equal(a.log.knoepfe.length, 2);
  // Rückfall ohne BIE.film.knopf: Film-Knopf → befehle, Bild-Knopf → nichts
  const b = aufbau({ mut: (F) => { F.tabs[0].aufgaben[1].niveaus.A.zeilen[1].modell = knoepfe; } });
  b.act("fo-modell", { nr: 902, z: 1, k: 1 }); b.act("fo-modell", { nr: 902, z: 1, k: 2 });
  assert.deepEqual(plain(b.log.befehle), [{ id: "biene3d", liste: [{ mw: "blick", name: "hinten" }] }]);
});

test("T1 Zeilen-Knopf als einzelnes Objekt und Bild-Knopf in der Tabelle (Zeile)", () => {
  const a = aufbau({ knopf: true, mut: (F) => { F.tabs[1].aufgaben[0].niveaus.A.zeilen[1].modell = { bild: "/static/img/lese/x.svg", text: "Bild ansehen", alt: "x" }; } });
  a.zeige(905);
  assert.match(a.html(905), /🖼️ Bild ansehen/);
  assert.doesNotMatch(a.html(905), /fo-modellreihe/, "ein einzelner Knopf ohne Reihe");
  a.act("fo-modell", { nr: 905, z: 1 });
  assert.deepEqual(plain(a.log.knoepfe), [{ bild: "/static/img/lese/x.svg", text: "Bild ansehen", alt: "x" }]);
});

// ── T8: Forscherbuch und Vermutungs-Satzbau ──────────────────────────────────
test("T8 Forscherbuch: eigene Einschätzung und (Niveau C) eigener Satz stehen im Buch – im Text, im HTML und im Protokoll", () => {
  const a = aufbau({ niveau: { 903: "C" } });
  vermutungFesthalten(a, 901, 2);
  a.zeige(903);
  a.act("fo-pr-einsch", { nr: 903, i: 1 });
  a.act("fo-pr-erk", { nr: 903, i: 0 });
  a.input({ foInput: "pr-satz", nr: "903" }, "es viele sind, mehr als ich dachte, und noch ein bisschen mehr Text.");
  a.act("fo-pr-satz", { nr: 903 });
  assert.equal(a.state.completed.has("903"), true);
  const eintrag = a.fo.buchEingabe()[0].eintraege[0];
  assert.equal(eintrag.einschaetzung, "stimmt teilweise");
  assert.deepEqual(plain(eintrag.saetze), ["Ich habe herausgefunden, dass … Meine Vermutung war es viele sind, mehr als ich dachte, und noch ein bisschen mehr Text."]);
  const text = a.logik.buchText(a.fo.buchEingabe(), "Kind");
  assert.match(text, /Meine Vermutung: etwa 5 000\nMeine Einschätzung: stimmt teilweise\nMeine Erkenntnis: Im Sommer leben bis zu etwa 50 000 Bienen in einem Stock\.\nMein Satz dazu: Ich habe herausgefunden/);
  const h = a.logik.buchHTML(a.fo.buchEingabe());
  assert.match(h, /fo-b-einsch"><span class="fo-b-label">Meine Einschätzung<\/span> stimmt teilweise/);
  assert.match(h, /fo-b-satz"><span class="fo-b-label">Mein Satz dazu<\/span> Ich habe herausgefunden/);
  a.act("fo-buch-abgabe", { nr: 913 });
  assert.match(a.log.antworten.at(-1).text, /Meine Einschätzung: stimmt teilweise/);
  // ohne Einschätzung/Satz bleibt alles wie vorher
  const b = aufbau();
  vermutungFesthalten(b, 901, 3);
  assert.doesNotMatch(b.logik.buchText(b.fo.buchEingabe(), "Kind"), /Meine Einschätzung|Mein Satz/);
  assert.doesNotMatch(b.logik.buchHTML(b.fo.buchEingabe()), /fo-b-einsch|fo-b-satz/);
  // Prüfmodus: Einschätzung als Beispiel
  const p = aufbau({ pruef: true });
  assert.equal(p.fo.buchEingabe()[0].eintraege[0].einschaetzung, "stimmt");
});

test("T8 Forscherbuch: Abgabe bis 8000 Zeichen (nicht mehr bei 2000 abgeschnitten)", () => {
  const a = aufbau();
  vermutungFesthalten(a, 901, 3);
  a.act("fo-buch-abgabe", { nr: 913 });
  assert.equal(a.log.antworten.at(-1).max, 8000);
});

test("T8 Vermutung: ein Baustein „weil …“ geht auch ohne Vortext; die Mindestlänge zählt nur den EIGENEN Text", () => {
  const a = aufbau({ niveau: { 901: "B" } });
  a.zeige(901);
  const ta = a.els["fo-sat-901"] || (a.els["fo-sat-901"] = { value: "", dispatchEvent() {}, focus() {}, id: "fo-sat-901" });
  a.act("fo-verm-wahl", { nr: 901, i: 3 });
  a.act("fo-verm-baustein", { nr: 901, i: 0 });
  assert.equal(ta.value, "weil ", "ohne Vortext: der Baustein steht allein am Anfang");
  assert.equal(a.letzteFb(), undefined, "kein „Schreibe zuerst …“ mehr");
  a.input({ foInput: "verm", nr: "901" }, ta.value);
  a.act("fo-verm-sicher", { nr: 901 });
  assert.match(a.letzteFb().html, /Schreibe noch ein bisschen mehr .*mindestens 10 Zeichen/, "„weil“ allein zählt nicht");
  a.input({ foInput: "verm", nr: "901" }, "weil denn viele");
  a.act("fo-verm-sicher", { nr: 901 });
  assert.match(a.letzteFb().html, /mindestens 10 Zeichen/, "„weil“ und „denn“ zählen nicht mit: übrig bleibt „viele“");
  const { logik: L, F } = aufbau();
  const v = F.tabs[0].aufgaben[0].niveaus;
  assert.equal(L.vermutungGueltig(v.B, [1], "weil denn weil").ok, false);
  assert.equal(L.vermutungGueltig(v.B, [1], "weil es viele Bienen sind").ok, true);
  assert.equal(L.vermutungGueltig(v.B, [1], "Weil, denn: es viele Bienen sind").ok, true);
  assert.equal(L.vermutungGueltig(v.B, [1], "weilige Zeit").ok, true, "ein Wort wie „weilige“ wird nicht zerschnitten");
});

test("T8 Vermutung: „Meine Vermutung: …“ als Satzanfang steht im Text nur einmal (nicht „Vermutung: Meine Vermutung: …“)", () => {
  const { logik: L } = aufbau();
  const c = { satzanfang: "Meine Vermutung: …", frei: true, min: 10 };
  const x = L.vermutungTexte(c, [], "Es sind sehr viele.");
  assert.equal(x.satz, "Es sind sehr viele.");
  assert.equal(x.antwort, "Vermutung: Es sind sehr viele.");
  assert.equal(L.vermutungTexte({ satzanfang: "Ich vermute, dass …", frei: true }, [], "es viele sind").satz, "Ich vermute, dass es viele sind");
});

// ═══ Nachtrag (F3, F5, F6) ═══════════════════════════════════════════════════
test("F3 Protokoll-Textzeile: okText ersetzt „Das stimmt!“ (eine Vermutung stimmt nicht oder nicht)", () => {
  const mit = (okText) => aufbau({ niveau: { 902: "C" }, sofortFaerben: true, mut: (F) => { if (okText) F.tabs[0].aufgaben[1].niveaus.C.zeilen[1].okText = okText; } });
  const a = mit("Danke, deine Vermutung ist notiert.");
  a.zeige(902);
  a.input({ foInput: "ztext", nr: "902", z: "1" }, "Ich sehe zwei große Augen.");
  a.act("fo-zeile-pruefen", { nr: 902, z: 1 });
  assert.match(a.html(902), /✅ Danke, deine Vermutung ist notiert\./);
  assert.doesNotMatch(a.html(902), /Das stimmt!/);
  const b = mit(null);
  b.zeige(902);
  b.input({ foInput: "ztext", nr: "902", z: "1" }, "Ich sehe zwei große Augen.");
  b.act("fo-zeile-pruefen", { nr: 902, z: 1 });
  assert.match(b.html(902), /✅ Das stimmt!/, "ohne okText wie bisher");
  const c = mit("<b>Danke</b>");                                    // maskiert
  c.zeige(902);
  c.input({ foInput: "ztext", nr: "902", z: "1" }, "Ich sehe zwei große Augen.");
  c.act("fo-zeile-pruefen", { nr: 902, z: 1 });
  assert.match(c.html(902), /&lt;b&gt;Danke&lt;\/b&gt;/);
});

test("F5 bildwahl: der Aufgabentext (auftrag) steht über jeder Runde – je Niveau oder an der Aufgabe", () => {
  const a = aufbau({ niveau: { 906: "A" }, mut: (F) => { F.tabs[1].aufgaben[1].niveaus.A.auftrag = "Du bist Futtersucherin. Suche den Ort mit dem Futter."; } });
  a.zeige(906);
  assert.match(a.html(906), /<p class="task-question fo-auftrag">Du bist Futtersucherin\. Suche den Ort mit dem Futter\.<\/p>/);
  a.act("fo-ziel", { nr: 906, i: 0 });
  assert.match(a.html(906), /fo-auftrag/, "auch nach dem Tipp");
  const b = aufbau({ mut: (F) => { F.tabs[1].aufgaben[1].auftrag = "Aufgabentext an der Aufgabe."; } });
  b.zeige(906);
  assert.match(b.html(906), /fo-auftrag">Aufgabentext an der Aufgabe\./);
  const c = aufbau();
  c.zeige(906);
  assert.doesNotMatch(c.html(906), /fo-auftrag/, "ohne auftrag nichts Zusätzliches");
});

test("F6 Knopf-Beschriftung: ein Symbol genügt – beginnt der Text schon mit ▶ oder einem Emoji, kommt kein zweites davor", () => {
  const { logik: L } = aufbau();
  ["▶ Hör zu", "  ▶ Hör zu", "🧊 Modell", "🎭 Film", "🖼️ Bild", "▷ Weiter", "⏵ Spielen", "👂 Hör zu"].forEach((t) => assert.equal(L.hatSymbol(t), true, t));
  ["Szene 4 ansehen", "Hör zu ▶", "", null, "Im Modell ansehen", "1. Kapitel"].forEach((t) => assert.equal(L.hatSymbol(t), false, String(t)));
});
