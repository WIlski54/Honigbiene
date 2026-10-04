import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import { TEILE, SCHLUESSEL, ABGELEITET, STANDARD_SCHILDER, schluesselFuer } from '../src/teile.js';
import { komponenten, schwerpunkte, REGELN, teileDreiecke } from '../src/teilung.js';

await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });

// Liest eine GLB wie main.js: Meshes mit Gruppe, Teilmeshes aus ABGELEITET werden herausgelöst.
async function lade(suffix) {
  const document = await io.readBinary(readFileSync(new URL(`../public/models/bee-study${suffix}.glb`, import.meta.url)));
  const meshes = [];
  const rest = [];
  for (const node of document.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const primitiv = mesh.listPrimitives()[0];
    const pos = primitiv.getAttribute('POSITION');
    const m = node.getWorldMatrix();
    const tmp = [0, 0, 0];
    const position = (i) => {
      const [x, y, z] = pos.getElement(i, tmp);
      return [m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14]];
    };
    const gruppe = node.getParentNode();
    meshes.push({ gruppe: gruppe.getName(), organ: gruppe.getExtras().organ === true, name: node.getName(), index: primitiv.getIndices().getArray(), position, vertexAnzahl: pos.getCount(), abgeleitet: false });
  }
  for (const regel of ABGELEITET) {
    for (const quelle of meshes.filter((x) => regel.quelle.test(x.name) && !x.abgeleitet)) {
      const zerlegung = komponenten(quelle.index, quelle.vertexAnzahl);
      const mitten = schwerpunkte(quelle.index, zerlegung, quelle.position);
      const auswahl = REGELN[regel.regel](mitten);
      const { drin, draussen } = teileDreiecke(zerlegung, auswahl);
      const sub = (liste) => Uint32Array.from(liste.flatMap((t) => [quelle.index[t * 3], quelle.index[t * 3 + 1], quelle.index[t * 3 + 2]]));
      rest.push({ ...quelle, name: regel.name(quelle.name), index: sub(drin), abgeleitet: true, komponenten: mitten, auswahl });
      quelle.index = sub(draussen);
    }
  }
  return [...meshes, ...rest];
}

const modelle = { desktop: await lade(''), mobile: await lade('-mobile') };

function box(mesh) {
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (const i of new Set(mesh.index)) {
    const p = mesh.position(i);
    for (let a = 0; a < 3; a++) { min[a] = Math.min(min[a], p[a]); max[a] = Math.max(max[a], p[a]); }
  }
  return { min, max };
}

const meshesFuer = (meshes, key) => meshes.filter((m) => schluesselFuer(m.gruppe, m.name).includes(key));

test('Automatischer Namenswechsel trennt die acht Aussenbegriffe von sieben inneren Organen', () => {
  const innen = ['honigmagen', 'darm', 'herz', 'gehirn', 'flugmuskeln', 'stachel', 'luftsaecke'];
  for (const meshes of Object.values(modelle)) {
    const innereKeys = STANDARD_SCHILDER.filter(k => meshesFuer(meshes, k).every(m => m.organ));
    assert.deepEqual(innereKeys, innen);
    assert.equal(STANDARD_SCHILDER.length - innereKeys.length, 8);
  }
});

test('Tabelle teile.js: genau die 19 Schlüssel des Protokolls mit Namen, Rang und Anker', () => {
  assert.deepEqual(SCHLUESSEL.sort(), ['bein', 'brust', 'darm', 'facettenauge', 'fluegel', 'flugmuskeln', 'fuehler', 'gehirn', 'herz', 'hinterbein', 'hinterleib', 'honigmagen', 'kopf', 'luftsaecke', 'mittelbein', 'pollenkoerbchen', 'ruessel', 'stachel', 'vorderbein'].sort());
  for (const k of SCHLUESSEL) {
    assert.ok(TEILE[k].name.length > 1, k);
    assert.ok([1, 2, 3].includes(TEILE[k].rang), k);
    assert.ok(TEILE[k].anker.length >= 1, k);
    assert.ok(TEILE[k].gruppen?.length || TEILE[k].meshen?.length, k);
  }
  assert.ok(STANDARD_SCHILDER.length >= 12 && STANDARD_SCHILDER.every((k) => SCHLUESSEL.includes(k)));
});

test('fokusRichtung: nur für die verdeckten Teile, jeweils ein endlicher Richtungsvektor', () => {
  const mit = SCHLUESSEL.filter((k) => TEILE[k].fokusRichtung);
  assert.deepEqual(mit.sort(), ['gehirn', 'herz', 'ruessel', 'stachel']);
  for (const k of mit) {
    const v = TEILE[k].fokusRichtung;
    assert.equal(v.length, 3, k);
    assert.ok(v.every(Number.isFinite) && Math.hypot(...v) > 0.5, k);
  }
});

for (const [art, meshes] of Object.entries(modelle)) {
  test(`${art}: jeder Schlüssel trifft mindestens ein Mesh, und kein Mesh hat zwei gleichrangige Schlüssel`, () => {
    for (const k of SCHLUESSEL) assert.ok(meshesFuer(meshes, k).length > 0, `${k}: kein Mesh`);
    for (const m of meshes) {
      const keys = schluesselFuer(m.gruppe, m.name);
      if (keys.length > 1) assert.notEqual(TEILE[keys[0]].rang, TEILE[keys[1]].rang, `${m.name}: ${keys.join(',')}`);
    }
  });

  test(`${art}: erwartete Meshzahlen je Schlüssel (140 Original-Meshes + 3 abgeleitete)`, () => {
    assert.equal(meshes.length, 143);
    assert.equal(meshes.filter((m) => m.abgeleitet).length, 3);
    const erwartet = {
      kopf: 17, brust: 5, hinterleib: 36, fuehler: 6, facettenauge: 6, ruessel: 3, fluegel: 14, bein: 46,
      vorderbein: 14, mittelbein: 14, hinterbein: 18, pollenkoerbchen: 2, honigmagen: 1, darm: 5, herz: 1,
      gehirn: 1, flugmuskeln: 1, stachel: 2, luftsaecke: 2,
    };
    for (const [k, n] of Object.entries(erwartet)) assert.equal(meshesFuer(meshes, k).length, n, k);
  });
}

test('Desktop- und Mobile-GLB enthalten dieselben Meshnamen je Schlüssel', () => {
  for (const k of SCHLUESSEL) {
    const namen = (m) => meshesFuer(m, k).map((x) => x.name).sort();
    assert.deepEqual(namen(modelle.mobile), namen(modelle.desktop), k);
  }
});

test('Spezifität: speziellster Schlüssel zuerst', () => {
  assert.deepEqual(schluesselFuer('head_ventral_capsule', 'compound_eye_1'), ['facettenauge', 'kopf']);
  assert.deepEqual(schluesselFuer('head_ventral_capsule', 'paired_galeae_folded'), ['ruessel', 'kopf']);
  assert.deepEqual(schluesselFuer('head_ventral_capsule', 'paired_flattened_mandibles'), ['kopf']);
  assert.deepEqual(schluesselFuer('head_dorsal_capsule', 'three_ocelli'), ['kopf']);
  assert.deepEqual(schluesselFuer('leg_3_-1', 'leg_3_-1_tibia_corbicula'), ['pollenkoerbchen', 'hinterbein', 'bein']);
  assert.deepEqual(schluesselFuer('leg_3_1', 'leg_3_1_basitarsus'), ['hinterbein', 'bein']);
  assert.deepEqual(schluesselFuer('leg_1_1', 'leg_1_1_setae'), ['vorderbein', 'bein']);
  assert.deepEqual(schluesselFuer('system_digestive', 'crop_honey_stomach'), ['honigmagen']);
  assert.deepEqual(schluesselFuer('system_digestive', 'oesophagus'), ['darm']);
  assert.deepEqual(schluesselFuer('system_digestive', 'malpighian_tubules_representative_network'), []);
  assert.deepEqual(schluesselFuer('system_glands_sting', 'venom_sac_and_ducts'), ['stachel']);
  assert.deepEqual(schluesselFuer('system_glands_sting', 'hypopharyngeal_mandibular_venom_glands'), []);
});

for (const [art, meshes] of Object.entries(modelle)) {
  test(`${art}: Pollenkörbchen ist die seitlichste der vier Rohrsegmente der Hinterbeine`, () => {
    for (const seite of ['-1', '1']) {
      const korb = meshes.find((m) => m.name === `leg_3_${seite}_tibia_corbicula`);
      const rest = meshes.find((m) => m.name === `leg_3_${seite}_coxa_trochanter_femur_tibia`);
      assert.ok(korb?.abgeleitet && korb.index.length === 196 * 3, `Tibia ${seite}`);
      assert.equal(rest.index.length, 3 * 196 * 3, 'Rest: Coxa, Trochanter, Femur');
      const lateral = (m) => Math.abs((box(m).min[2] + box(m).max[2]) / 2);
      assert.ok(lateral(korb) > lateral(rest), 'Tibia liegt weiter außen als der Rest');
      assert.equal(korb.komponenten.length, 4);
    }
  });

  test(`${art}: Giftblase mit Gängen wird aus den Kopfdrüsen herausgelöst`, () => {
    const sack = meshes.find((m) => m.name === 'venom_sac_and_ducts');
    const rest = meshes.find((m) => m.name === 'hypopharyngeal_mandibular_venom_glands');
    assert.deepEqual([...sack.auswahl].length, 3, 'Blase und zwei Gänge');
    assert.equal(sack.index.length / 3, 1280 + 296 + 296);
    assert.ok(box(sack).min[0] > 1.5, 'im Hinterleib');
    assert.ok(box(rest).max[0] < 0, 'Kopf- und Brustdrüsen bleiben im Rest');
    assert.ok(rest.organ && sack.organ);
  });

  test(`${art}: Anker verweisen auf Meshes des Schlüssels bzw. liegen im Bereich seiner Meshes`, () => {
    for (const k of SCHLUESSEL) {
      const eigene = meshesFuer(meshes, k);
      const namen = new Set(eigene.map((m) => m.name));
      for (const einheit of TEILE[k].anker) {
        if (einheit.meshen) for (const n of einheit.meshen) assert.ok(namen.has(n), `${k}: Ankermesh ${n} gehört nicht dazu`);
        if (einheit.punkt) {
          const boxen = eigene.map(box);
          const min = [0, 1, 2].map((a) => Math.min(...boxen.map((b) => b.min[a])) - 0.1);
          const max = [0, 1, 2].map((a) => Math.max(...boxen.map((b) => b.max[a])) + 0.1);
          einheit.punkt.forEach((v, a) => assert.ok(v >= min[a] && v <= max[a], `${k}: Ankerpunkt außerhalb (Achse ${a})`));
          assert.ok(eigene.some((m) => m.gruppe === einheit.gruppe), `${k}: Gruppe ${einheit.gruppe}`);
        }
      }
    }
  });

  test(`${art}: innere Schlüssel liegen nur in Organgruppen, äußere nie`, () => {
    const innen = new Set(['honigmagen', 'darm', 'herz', 'gehirn', 'flugmuskeln', 'stachel', 'luftsaecke']);
    for (const k of SCHLUESSEL) {
      const flags = meshesFuer(meshes, k).map((m) => m.organ);
      assert.equal(flags.every(Boolean), innen.has(k), k);
      assert.equal(flags.some(Boolean), innen.has(k), k);
    }
  });
}
