export const clamp01 = (value) => Math.max(0, Math.min(1, value));

export function smoothstep(start, end, value) {
  const t = clamp01((value - start) / (end - start));
  return t * t * (3 - 2 * t);
}

// Exact integration of a critically damped spring for a fixed target per frame.
// Retains velocity when the user reverses; independent of display refresh rate.
export class ProgressSpring {
  constructor(frequency = 13) {
    this.value = 0;
    this.velocity = 0;
    this.target = 0;
    this.frequency = frequency;
  }
  setTarget(value) { this.target = clamp01(value); }
  step(dt) {
    const delta = this.value - this.target;
    const c = this.velocity + this.frequency * delta;
    const decay = Math.exp(-this.frequency * Math.max(0, dt));
    this.value = this.target + (delta + c * dt) * decay;
    this.velocity = (this.velocity - this.frequency * c * dt) * decay;
    if (this.value < 0 || this.value > 1) {
      this.value = clamp01(this.value);
      this.velocity = 0;
    }
    if (Math.abs(this.value - this.target) < 0.00002 && Math.abs(this.velocity) < 0.0002) {
      this.value = this.target;
      this.velocity = 0;
    }
    return this.value;
  }
  reset(value = 0) { this.value = this.target = clamp01(value); this.velocity = 0; }
}

export function partTransform(metadata, progress) {
  const t = smoothstep(metadata.start ?? 0, metadata.end ?? 1, progress);
  // Blender coordinates (X, Y, Z) to glTF/Three coordinates (X, Z, -Y).
  return {
    offset: [(metadata.dx ?? 0) * t, (metadata.dz ?? 0) * t, -(metadata.dy ?? 0) * t],
    rotation: [(metadata.rx ?? 0) * t, (metadata.rz ?? 0) * t, -(metadata.ry ?? 0) * t],
  };
}
