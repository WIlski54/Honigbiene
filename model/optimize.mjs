import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { meshopt } from '@gltf-transform/functions';
import { MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';
import { fileURLToPath } from 'node:url';
import { stat } from 'node:fs/promises';

const suffix = process.argv.includes('--mobile') ? '-mobile' : '';
const input = fileURLToPath(new URL(`./bee-study${suffix}.raw.glb`, import.meta.url));
const output = fileURLToPath(new URL(`../public/models/bee-study${suffix}.glb`, import.meta.url));
await Promise.all([MeshoptDecoder.ready, MeshoptEncoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.decoder': MeshoptDecoder,
  'meshopt.encoder': MeshoptEncoder,
});
const document = await io.read(input);
await document.transform(meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
await io.write(output, document);
const [before, after] = await Promise.all([stat(input), stat(output)]);
console.log(`GLB: ${(before.size / 1e6).toFixed(2)} MB → ${(after.size / 1e6).toFixed(2)} MB`);
