import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';

const bytes = readFileSync(new URL('../public/models/bee-study.glb', import.meta.url));
assert.equal(bytes.readUInt32LE(0), 0x46546c67, 'GLB magic');
assert.equal(bytes.readUInt32LE(4), 2, 'glTF version');
const jsonLength = bytes.readUInt32LE(12);
const gltf = JSON.parse(bytes.subarray(20, 20 + jsonLength).toString('utf8'));
const parts = gltf.nodes.filter(n => n.extras?.studyPart);

await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.decoder': MeshoptDecoder });

function connectedComponents(primitive) {
  const indices = primitive.getIndices().getArray();
  const parent = new Map();
  const root = vertex => {
    if (!parent.has(vertex)) parent.set(vertex, vertex);
    if (parent.get(vertex) !== vertex) parent.set(vertex, root(parent.get(vertex)));
    return parent.get(vertex);
  };
  for (let i = 0; i < indices.length; i += 3) {
    const a = root(indices[i]);
    parent.set(root(indices[i+1]), a);
    parent.set(root(indices[i+2]), a);
  }
  return new Set([...parent.keys()].map(root)).size;
}

test('each exported leg has one basitarsus and four separate distal tarsomeres', async () => {
  for (const suffix of ['', '-mobile']) {
    const document = await io.readBinary(readFileSync(new URL(`../public/models/bee-study${suffix}.glb`, import.meta.url)));
    const nodes = document.getRoot().listNodes();
    for (const leg of nodes.filter(n => n.getExtras().studyPart && n.getName().startsWith('leg_'))) {
      const basitarsus = leg.listChildren().find(n => n.getName().endsWith('_basitarsus'));
      const distal = leg.listChildren().find(n => n.getName().endsWith('_distal_tarsomeres_2_to_5'));
      assert.ok(basitarsus, leg.getName());
      assert.ok(distal, leg.getName());
      assert.equal(connectedComponents(basitarsus.getMesh().listPrimitives()[0]), 1);
      assert.equal(connectedComponents(distal.getMesh().listPrimitives()[0]), 4);
    }
    const brushes = nodes.filter(n => n.getName().endsWith('_pollen_brush_rows'));
    assert.equal(brushes.length, 2, 'both hind basitarsi retain their brushes');
  }
});

test('export retains all independently movable anatomical parts', () => {
  assert.equal(parts.length, 35);
  assert.equal(parts.filter(n => n.name.startsWith('leg_')).length, 6);
  assert.equal(parts.filter(n => n.extras.category === 'wing').length, 4);
  assert.equal(parts.filter(n => n.name.startsWith('abdomen_tergite_')).length, 6);
  assert.equal(parts.filter(n => n.extras.organ).length, 7);
});
test('all organ systems stay at their original position during situs', () => {
  for (const node of parts.filter(n => n.extras.organ)) {
    assert.ok(node.extras.explosion.start > .55, node.name);
    assert.equal(node.extras.anatomyStatus, 'reference-guided reconstruction; not yet validated');
  }
});
test('compression and geometry bounds are valid', () => {
  assert.ok(gltf.extensionsRequired.includes('EXT_meshopt_compression'));
  assert.ok(bytes.length < 15_000_000, 'compressed first-study asset below 15 MB');
  for (const accessor of gltf.accessors) {
    for (const v of [...(accessor.min ?? []), ...(accessor.max ?? [])]) assert.ok(Number.isFinite(v));
  }
  assert.equal(bytes.readUInt32LE(8), bytes.length);
});

test('mobile asset retains anatomy and paths while reducing exterior geometry', () => {
  const mobileBytes = readFileSync(new URL('../public/models/bee-study-mobile.glb', import.meta.url));
  const mobileJsonLength = mobileBytes.readUInt32LE(12);
  const mobile = JSON.parse(mobileBytes.subarray(20,20+mobileJsonLength).toString('utf8'));
  const mobileParts = mobile.nodes.filter(n => n.extras?.studyPart);
  assert.equal(mobileParts.length, parts.length);
  for (const part of parts) {
    const counterpart = mobileParts.find(n => n.name === part.name);
    assert.ok(counterpart, part.name);
    assert.deepEqual(counterpart.extras.explosion, part.extras.explosion);
  }
  assert.ok(mobileBytes.length < 6_000_000);
  const info = JSON.parse(readFileSync(new URL('../public/models/model-info.json', import.meta.url)));
  const mobileInfo = JSON.parse(readFileSync(new URL('../public/models/model-info-mobile.json', import.meta.url)));
  assert.ok(mobileInfo.triangles < info.triangles * .6);
});
