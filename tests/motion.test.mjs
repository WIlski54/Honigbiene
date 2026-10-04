import test from 'node:test';
import assert from 'node:assert/strict';
import { ProgressSpring, partTransform } from '../src/motion.js';

test('same elapsed time produces the same motion at 30, 60 and 120 Hz', () => {
  const values = [30, 60, 120].map((fps) => {
    const spring = new ProgressSpring(); spring.setTarget(1);
    for (let i = 0; i < fps / 2; i++) spring.step(1 / fps);
    return spring.value;
  });
  assert.ok(Math.max(...values) - Math.min(...values) < 1e-10);
});

test('an interrupted frame does not slow down the analytically integrated spring', () => {
  const regular = new ProgressSpring(); regular.setTarget(1);
  const delayed = new ProgressSpring(); delayed.setTarget(1);
  for (let i = 0; i < 60; i++) regular.step(1 / 60);
  delayed.step(1);
  assert.ok(Math.abs(delayed.value - regular.value) < 1e-12);
  assert.ok(Math.abs(delayed.velocity - regular.velocity) < 1e-12);
  assert.ok(delayed.value > .9999);
});

test('reversal preserves position and velocity, then returns precisely to closed', () => {
  const spring = new ProgressSpring(); spring.setTarget(1);
  for (let i = 0; i < 20; i++) spring.step(1 / 60);
  const before = [spring.value, spring.velocity];
  spring.setTarget(0);
  assert.deepEqual([spring.value, spring.velocity], before);
  assert.ok(Math.abs(spring.step(1 / 60) - before[0]) < 0.06);
  for (let i = 0; i < 180; i++) spring.step(1 / 60);
  assert.equal(spring.value, 0);
});

test('organs stay in anatomical position at the situs stage', () => {
  const organ = { start: 0.62, end: 1, dx: 0.2, dy: -1.2, dz: 0.6 };
  assert.deepEqual(partTransform(organ, 0.55).offset.map(v => v || 0), [0, 0, 0]);
  assert.deepEqual(partTransform(organ, 1).offset, [0.2, 0.6, 1.2]);
});

test('repeated scrubbing never accumulates drift in component transforms', () => {
  const part = { start: 0.1, end: 0.5, dx: 0.4, dy: 0.2, dz: 1.8 };
  const endpoint = partTransform(part, 1);
  for (let i = 0; i < 1000; i++) {
    partTransform(part, (Math.sin(i) + 1) / 2);
    assert.deepEqual(partTransform(part, 1), endpoint);
    assert.deepEqual(partTransform(part, 0).offset.map(v => v || 0), [0, 0, 0]);
  }
});
