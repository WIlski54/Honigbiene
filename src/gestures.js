// Gesture recognition consumes one complete two-pointer sample per frame.
// Coalescing avoids interpreting the first finger of a translation as a pinch.
export function twoFingerStep(previous, next, lockedMode = null) {
  const dy = next.y - previous.y;
  const distanceDelta = next.distance - previous.distance;
  let mode = lockedMode;
  if (!mode) {
    if (Math.abs(distanceDelta) > 7 && Math.abs(distanceDelta) > Math.abs(dy) * 1.4) mode = 'pinch';
    else if (Math.abs(dy) > 7 && Math.abs(dy) > Math.abs(distanceDelta) * 1.4) mode = 'explode';
  }
  return {
    mode,
    zoomRatio: mode === 'pinch' && next.distance > 0 && previous.distance > 0 ? previous.distance / next.distance : 1,
    movement: mode === 'explode' ? -dy : 0,
  };
}
