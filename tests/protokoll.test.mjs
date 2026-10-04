import test from 'node:test';
import assert from 'node:assert/strict';
import {
  ANSICHTEN, BLICKE, ansichtVon, aktualisiereBesucht, gesehenProzent, statusObjekt, infoObjekt, parseBefehl, entscheideTipp, standText,
} from '../src/protokoll.js';
import { SCHLUESSEL } from '../src/teile.js';
import { legeSchilderAus } from '../src/schilder.js';

test('Ansichten entsprechen den Voreinstellungen (0 / 0,55 / 1) und den Knopfschwellen', () => {
  assert.deepEqual(ANSICHTEN.map((a) => a.wert), [0, 0.55, 1]);
  assert.equal(ansichtVon(0), 'gestalt');
  assert.equal(ansichtVon(0.039), 'gestalt');
  assert.equal(ansichtVon(0.2), 'zwischen');
  assert.equal(ansichtVon(0.55), 'situs');
  assert.equal(ansichtVon(0.60), 'situs');
  assert.equal(ansichtVon(0.7), 'zwischen');
  assert.equal(ansichtVon(0.97), 'explosion');
  assert.equal(standText('gestalt', 0), 'Außenansicht');
  assert.equal(standText('zwischen', 0.3), 'Öffnung 30 %');
});

test('gesehen: je ein Drittel für Außen, Situs und Explosion (±0,06)', () => {
  const b = new Set();
  assert.equal(gesehenProzent(b), 0);
  assert.equal(aktualisiereBesucht(b, 0.03), true);
  assert.equal(aktualisiereBesucht(b, 0.03), false, 'keine Änderung bei erneutem Besuch');
  assert.equal(gesehenProzent(b), 33);
  aktualisiereBesucht(b, 0.3);
  assert.equal(gesehenProzent(b), 33, 'Zwischenstand zählt nicht');
  aktualisiereBesucht(b, 0.62);
  assert.equal(gesehenProzent(b), 33, '0,62 liegt knapp außerhalb von 0,55 ± 0,06');
  aktualisiereBesucht(b, 0.60);
  assert.equal(gesehenProzent(b), 67);
  aktualisiereBesucht(b, 0.939);
  assert.equal(gesehenProzent(b), 67);
  aktualisiereBesucht(b, 0.94);
  assert.equal(gesehenProzent(b), 100);
  assert.deepEqual([...b].sort(), ['explosion', 'gestalt', 'situs']);
});

test('gesehen: ein schneller Sprung über die Situs-Zone zählt sie mit (Intervall zwischen zwei Frames)', () => {
  const b = new Set();
  aktualisiereBesucht(b, 0.3, 0.3);
  aktualisiereBesucht(b, 0.7, 0.3);
  assert.deepEqual([...b], ['situs'], 'von 0,3 nach 0,7 überquert 0,49 bis 0,61');
  const c = new Set();
  aktualisiereBesucht(c, 0.3, 0.1);
  aktualisiereBesucht(c, 0.45, 0.3);
  assert.equal(c.size, 0, 'bis 0,45 noch nicht in der Zone');
  aktualisiereBesucht(c, 0.95, 0.9);
  assert.deepEqual([...c], ['explosion']);
});

test('Status enthält alle Felder des Protokolls, freigeschaltet immer true', () => {
  const s = statusObjekt({ fortschritt: 0.55, laeuft: false, besucht: new Set(['situs', 'gestalt']), blick: 'seite', waehlen: true, hervorgehoben: new Set(['kopf']) });
  assert.equal(s.mw, 'status');
  assert.equal(s.art, 'modell3d');
  assert.equal(s.t, 0);
  assert.equal(s.laeuft, false);
  assert.equal(s.live, false);
  assert.equal(s.ansicht, 'situs');
  assert.equal(s.ansichtLabel, 'Innen');
  assert.equal(s.gesehen, 67);
  assert.deepEqual(s.besucht, ['gestalt', 'situs']);
  assert.equal(s.freigeschaltet, true);
  assert.equal(s.standText, 'Innenansicht (Situs)');
  assert.deepEqual(s.hervorgehoben, ['kopf']);
  assert.equal(s.leiste, true, 'Leiste standardmäßig sichtbar');
  assert.equal(statusObjekt({ fortschritt: 0, besucht: new Set(), blick: 'schraeg', leiste: false }).leiste, false);
  assert.equal(JSON.parse(JSON.stringify(s)).gesehen, 67, 'JSON-fähig');
  const z = statusObjekt({ fortschritt: 0.3, laeuft: true, besucht: new Set(), blick: 'schraeg' });
  assert.equal(z.ansicht, 'zwischen');
  assert.equal(z.laeuft, true);
});

test('info nennt Ansichten, Blicke und alle 19 Teile mit Namen', () => {
  const i = infoObjekt();
  assert.equal(i.mw, 'info');
  assert.equal(i.art, 'modell3d');
  assert.deepEqual(i.ansichten.map((a) => a.name), ['gestalt', 'situs', 'explosion']);
  assert.deepEqual(i.blicke.map((a) => a.name), ['schraeg', 'seite', 'oben', 'vorn', 'hinten']);
  assert.equal(i.teile.length, 19);
  assert.ok(i.teile.every((t) => t.name && t.label));
  assert.equal(i.teile.find((t) => t.name === 'honigmagen').label, 'Honigmagen');
  assert.equal(BLICKE.length, 5);
});

test('parseBefehl: ansicht per Name oder Wert, ungültige Werte werden verworfen', () => {
  assert.deepEqual(parseBefehl({ mw: 'ansicht', name: 'situs' }), { typ: 'ansicht', wert: 0.55 });
  assert.deepEqual(parseBefehl({ mw: 'ansicht', name: 'explosion' }), { typ: 'ansicht', wert: 1 });
  assert.deepEqual(parseBefehl({ mw: 'ansicht', wert: 0.3 }), { typ: 'ansicht', wert: 0.3 });
  assert.deepEqual(parseBefehl({ mw: 'ansicht', wert: 7 }), { typ: 'ansicht', wert: 1 });
  assert.deepEqual(parseBefehl({ mw: 'ansicht', wert: -2 }), { typ: 'ansicht', wert: 0 });
  assert.equal(parseBefehl({ mw: 'ansicht', name: 'quatsch' }), null);
  assert.equal(parseBefehl({ mw: 'ansicht' }), null);
  assert.equal(parseBefehl({ mw: 'ansicht', wert: 'abc' }), null);
});

test('parseBefehl: blick, hervorheben, beschriften, nummern, waehlen', () => {
  assert.deepEqual(parseBefehl({ mw: 'blick', name: 'seite' }), { typ: 'blick', name: 'seite' });
  assert.equal(parseBefehl({ mw: 'blick', name: 'unten' }), null);
  assert.deepEqual(parseBefehl({ mw: 'hervorheben', teile: ['fluegel', 'kopf', 'kopf', 'xyz'], fokus: true }), { typ: 'hervorheben', teile: ['fluegel', 'kopf'], fokus: true });
  assert.deepEqual(parseBefehl({ mw: 'hervorheben', teile: [] }), { typ: 'hervorheben', teile: [], fokus: false });
  assert.deepEqual(parseBefehl({ mw: 'hervorheben' }), { typ: 'hervorheben', teile: [], fokus: false });
  assert.deepEqual(parseBefehl({ mw: 'beschriften', an: true, teile: ['kopf'] }), { typ: 'beschriften', an: true, teile: ['kopf'] });
  assert.deepEqual(parseBefehl({ mw: 'beschriften', an: false }), { typ: 'beschriften', an: false, teile: [] });
  assert.deepEqual(parseBefehl({ mw: 'nummern', teile: ['kopf', 'quatsch', 'brust'] }), { typ: 'nummern', teile: ['kopf', null, 'brust'] }, 'Nummer = Listenposition');
  assert.deepEqual(parseBefehl({ mw: 'nummern', teile: [] }), { typ: 'nummern', teile: [] });
  assert.deepEqual(parseBefehl({ mw: 'waehlen', an: true }), { typ: 'waehlen', an: true });
  assert.deepEqual(parseBefehl({ mw: 'waehlen', an: false }), { typ: 'waehlen', an: false });
  for (const k of SCHLUESSEL) assert.deepEqual(parseBefehl({ mw: 'hervorheben', teile: [k] }).teile, [k]);
});

test('parseBefehl leiste: an/aus, ohne Angabe an', () => {
  assert.deepEqual(parseBefehl({ mw: 'leiste', an: false }), { typ: 'leiste', an: false });
  assert.deepEqual(parseBefehl({ mw: 'leiste', an: true }), { typ: 'leiste', an: true });
  assert.deepEqual(parseBefehl({ mw: 'leiste' }), { typ: 'leiste', an: true });
});

test('parseBefehl: einfache Befehle, Fremdes wird ignoriert', () => {
  for (const mw of ['info', 'status', 'spielen', 'anhalten', 'freischalten', 'springe', 'zurueck']) assert.deepEqual(parseBefehl({ mw }), { typ: mw });
  for (const m of [null, undefined, 'x', 42, {}, { mw: 3 }, { mw: 'unbekannt' }, { type: 'resize' }]) assert.equal(parseBefehl(m), null);
});

test('Tipp: erster fester Treffer gilt, durchsichtige Membranen blockieren nicht', () => {
  const kopf = { abstand: 5, weich: false, rohname: 'head_roof', teile: ['kopf'] };
  const auge = { abstand: 4, weich: false, rohname: 'compound_eye_1', teile: ['facettenauge', 'kopf'] };
  const fluegel = { abstand: 3, weich: true, rohname: 'wing_membrane_1_False', teile: ['fluegel'] };
  assert.deepEqual(entscheideTipp([kopf, auge]), { teil: 'facettenauge', teile: ['facettenauge', 'kopf'], rohname: 'compound_eye_1', darunter: [], davor: [] }, 'spezieller Schlüssel zuerst; kopf steckt schon in teile');
  assert.equal(entscheideTipp([fluegel, kopf]).teil, 'kopf', 'Flügel davor blockiert nicht');
  assert.equal(entscheideTipp([fluegel]).teil, 'fluegel', 'Flügel allein ist antippbar');
  assert.equal(entscheideTipp([kopf, fluegel]).teil, 'kopf');
  assert.deepEqual(entscheideTipp([]), { teil: null, teile: [], rohname: null, darunter: [], davor: [] });
  const ohne = entscheideTipp([{ abstand: 1, weich: false, rohname: 'paired_flattened_mandibles', teile: [] }]);
  assert.equal(ohne.teil, null);
  assert.equal(ohne.rohname, 'paired_flattened_mandibles');
});

test('Tipp: Meshes ohne Schlüssel blockieren keine benannten Teile dahinter; darunter und davor melden den Strahl', () => {
  const schlauch = { abstand: 1, weich: false, rohname: 'malpighian_tubules_representative_network', teile: [] };
  const darm = { abstand: 2, weich: false, rohname: 'ventriculus_corrugated_midgut', teile: ['darm'] };
  const magen = { abstand: 3, weich: false, rohname: 'crop_honey_stomach', teile: ['honigmagen'] };
  const sack = { abstand: 0.5, weich: true, rohname: 'tracheal_air_sac_membranes', teile: ['luftsaecke'] };
  const r = entscheideTipp([schlauch, magen]);
  assert.equal(r.teil, 'honigmagen', 'Schlauch davor zählt nicht');
  assert.deepEqual(r.davor, ['malpighian_tubules_representative_network']);
  assert.deepEqual(r.darunter, []);
  const r2 = entscheideTipp([sack, schlauch, darm, magen]);
  assert.equal(r2.teil, 'darm', 'fester Treffer mit Schlüssel vor dem Magen');
  assert.deepEqual(r2.darunter, ['luftsaecke', 'honigmagen'], 'alle anderen Schlüssel entlang des Strahls, vorn nach hinten');
  assert.deepEqual(r2.davor, ['tracheal_air_sac_membranes', 'malpighian_tubules_representative_network']);
  assert.equal(entscheideTipp([schlauch]).teil, null, 'nur Unbenanntes: null mit rohname');
  assert.equal(entscheideTipp([schlauch]).rohname, 'malpighian_tubules_representative_network');
  assert.equal(entscheideTipp([sack, schlauch]).teil, 'luftsaecke', 'Membran mit Schlüssel vor Unbenanntem');
  assert.deepEqual(entscheideTipp([darm, magen]).darunter, ['honigmagen']);
});

test('parseBefehl fokus: Teile, optional blick und abstand; ungültige Angaben entfallen', () => {
  assert.deepEqual(parseBefehl({ mw: 'fokus', teile: ['ruessel'] }), { typ: 'fokus', teile: ['ruessel'], blick: null, abstand: null });
  assert.deepEqual(parseBefehl({ mw: 'fokus', teile: ['ruessel', 'ruessel', 'xyz'], blick: 'vorn', abstand: 2.5 }), { typ: 'fokus', teile: ['ruessel'], blick: 'vorn', abstand: 2.5 });
  assert.deepEqual(parseBefehl({ mw: 'fokus', teile: [] }), { typ: 'fokus', teile: [], blick: null, abstand: null }, 'zurück');
  assert.deepEqual(parseBefehl({ mw: 'fokus' }), { typ: 'fokus', teile: [], blick: null, abstand: null });
  assert.deepEqual(parseBefehl({ mw: 'fokus', teile: ['stachel'], blick: 'unten', abstand: -3 }), { typ: 'fokus', teile: ['stachel'], blick: null, abstand: null });
  assert.equal(parseBefehl({ mw: 'fokus', teile: ['stachel'], abstand: 'abc' }).abstand, null);
});

const ueberlappt = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

test('Layout: gedrängte Schilder überlappen sich nicht und bleiben im Rahmen', () => {
  const breite = 520, hoehe = 330, unten = 104;
  // 19 Schilder mit Ankern in einem engen Bereich (Körpermitte), Namen und Nummern gemischt.
  const items = SCHLUESSEL.map((k, i) => ({ id: k, typ: i % 3 === 0 ? 'nummer' : 'name', w: i % 3 === 0 ? 30 : 60 + (i % 5) * 14, h: i % 3 === 0 ? 30 : 28, ax: 190 + (i * 37) % 150, ay: 60 + (i * 53) % 110 }));
  const ergebnis = legeSchilderAus(items, { breite, hoehe, unten });
  assert.equal(ergebnis.length, items.length);
  const boxen = ergebnis.map((r, i) => ({ x: r.x, y: r.y, w: items[i].w, h: items[i].h }));
  for (let i = 0; i < boxen.length; i++) {
    assert.ok(boxen[i].x >= 0 && boxen[i].y >= 0 && boxen[i].x + boxen[i].w <= breite && boxen[i].y + boxen[i].h <= hoehe - unten + 1, `Rahmen ${i}`);
    for (let j = i + 1; j < boxen.length; j++) assert.ok(!ueberlappt(boxen[i], boxen[j]), `Überlappung ${i}/${j}`);
  }
});

test('Layout: Schild sitzt radial außerhalb des Ankers, Nummer direkt auf dem Anker; stabil bei Wiederholung', () => {
  const gedaechtnis = new Map();
  const items = [{ id: 'a', typ: 'name', w: 70, h: 28, ax: 300, ay: 120 }, { id: 'n', typ: 'nummer', w: 30, h: 30, ax: 120, ay: 120 }];
  const opts = { breite: 520, hoehe: 330, unten: 0, mitte: [260, 165], gedaechtnis };
  const r1 = legeSchilderAus(items, opts);
  assert.ok(r1[0].x > 300 - 35, 'rechts vom Zentrum nach außen');
  assert.equal(r1[0].linie, true);
  assert.deepEqual([r1[1].x + 15, r1[1].y + 15], [120, 120], 'Nummer zentriert auf dem Anker');
  assert.equal(r1[1].linie, false);
  assert.deepEqual(legeSchilderAus(items, opts), r1);
});
