import test from 'node:test';
import assert from 'node:assert/strict';
import { twoFingerStep } from '../src/gestures.js';

test('parallel fingers open anatomy without changing zoom', () => {
  const step = twoFingerStep({ y: 300, distance: 120 }, { y: 260, distance: 120 });
  assert.equal(step.mode, 'explode');
  assert.equal(step.movement, 40);
  assert.equal(step.zoomRatio, 1);
});
test('pinch changes zoom without opening anatomy', () => {
  const step = twoFingerStep({ y: 300, distance: 120 }, { y: 302, distance: 160 });
  assert.equal(step.mode, 'pinch');
  assert.equal(step.zoomRatio, .75);
  assert.equal(step.movement, 0);
});
test('small or ambiguous movements do not select a gesture', () => {
  assert.equal(twoFingerStep({ y: 300, distance: 120 }, { y: 304, distance: 125 }).mode, null);
  assert.equal(twoFingerStep({ y: 300, distance: 120 }, { y: 320, distance: 143 }).mode, null);
});
test('gesture stays locked when incidental motion changes direction', () => {
  const step = twoFingerStep({ y: 300, distance: 120 }, { y: 298, distance: 150 }, 'explode');
  assert.equal(step.mode, 'explode');
  assert.equal(step.movement, 2);
  assert.equal(step.zoomRatio, 1);
});
