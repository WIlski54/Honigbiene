/* Papier-Cutout-Engine: Formen, Texturen, Wachsmalstift, Kamera, Hilfsfunktionen.
   Logische Bildgröße ist immer 1920×1080; die Leinwand kann intern kleiner/größer sein. */
'use strict';

const W = 1920, H = 1080;
const FPS_DRAW = 12;          // Stop-Motion: 12 Zeichnungen pro Sekunde („on twos“)
const G = { boil: 0, t: 0, k: 1, fast: false };   // globaler Zeichen-Zustand pro Bild

// ------------------------------------------------------------------ Farben
const C = {
  mustard: '#E2A83A', mustardD: '#C08624', mustardL: '#F0CB77',
  coral: '#EE7E6A', coralD: '#CC5D4D', coralL: '#F6A898',
  petrol: '#1E6B6E', petrolD: '#134A4D', petrolL: '#5C9E96',
  cream: '#F5EAD3', creamD: '#E7D6B3', paper: '#FFFCF3',
  kraft: '#C8A57A', kraftD: '#A58058', kraftL: '#DCC19C',
  navy: '#1E2A4A', violet: '#4A3A6A', ink: '#2A2833',
  water: '#4F92A6', waterD: '#3A7589', waterL: '#8CC0CB',
  skin: '#F3C9A6', skinD: '#E3AC86', hair: '#8A4527', hairD: '#6C321B',
  grey: '#8E8A86', greyD: '#5D5A58', greyL: '#BDB8B0',
  wood: '#9C6B43', woodD: '#7A5031', woodL: '#B98A5E',
  sky: '#F6E7C6', green: '#6F9B62', greenD: '#4E7A4A', rust: '#8F4A34',
  crayonBlue: '#2C58C9', red: '#C8453A',
};

// ------------------------------------------------------------------ Mathe
const clamp = (v, a = 0, b = 1) => v < a ? a : v > b ? b : v;
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const eout = t => 1 - Math.pow(1 - t, 3);
const ein = t => t * t * t;
const sm = t => t * t * (3 - 2 * t);
const back = t => { const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const TAU = Math.PI * 2;

function hash(a, b = 0, c = 0) {
  let h = (a | 0) * 374761393 + (b | 0) * 668265263 + (c | 0) * 1274126177;
  h = (h ^ (h >>> 13)) * 1274126177;
  h ^= h >>> 16;
  return ((h >>> 0) % 100000) / 100000;
}
const hs = (a, b = 0, c = 0) => hash(a, b, c) * 2 - 1;   // −1..1

function mulberry(seed) {
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// Keyframe-Interpolation: kf = [[t, v], ...] (v Zahl oder Array)
function kf(frames, t, ease = eio) {
  if (t <= frames[0][0]) return frames[0][1];
  for (let i = 1; i < frames.length; i++) {
    if (t <= frames[i][0]) {
      const [t0, a] = frames[i - 1], [t1, b] = frames[i];
      const p = ease((t - t0) / (t1 - t0));
      if (Array.isArray(a)) return a.map((v, j) => lerp(v, b[j], p));
      return lerp(a, b, p);
    }
  }
  return frames[frames.length - 1][1];
}

// ------------------------------------------------------------------ Texturen
function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

const TEX = {};
function buildTextures() {
  const R = mulberry(7);
  // Gouache-Pinselstriche (hell + dunkel, transparent)
  let c = makeCanvas(320, 320), x = c.getContext('2d');
  for (let i = 0; i < 170; i++) {
    const light = R() < 0.55;
    x.strokeStyle = light ? `rgba(255,250,235,${0.05 + R() * 0.09})` : `rgba(70,45,25,${0.012 + R() * 0.03})`;
    x.lineWidth = 3 + R() * 14;
    x.lineCap = 'round';
    const x0 = R() * 360 - 20, y0 = R() * 360 - 20, a = -0.5 + R() * 0.5 + (R() < .5 ? 0 : Math.PI / 2 * 0.3);
    const L = 30 + R() * 110;
    x.beginPath();
    x.moveTo(x0, y0);
    x.quadraticCurveTo(x0 + Math.cos(a) * L * .5 + (R() - .5) * 20, y0 + Math.sin(a) * L * .5 + (R() - .5) * 20,
      x0 + Math.cos(a) * L, y0 + Math.sin(a) * L);
    x.stroke();
    // Borsten-Linien im Strich
    x.lineWidth = 0.8;
    for (let k = 0; k < 3; k++) {
      x.strokeStyle = light ? 'rgba(255,255,245,0.10)' : 'rgba(50,30,15,0.03)';
      const o = (R() - .5) * 8;
      x.beginPath();
      x.moveTo(x0 + o, y0 - o);
      x.lineTo(x0 + Math.cos(a) * L + o, y0 + Math.sin(a) * L - o);
      x.stroke();
    }
  }
  // trockene Gouache: kleine Aussparungen
  for (let i = 0; i < 900; i++) {
    x.fillStyle = `rgba(255,250,240,${R() * 0.18})`;
    x.fillRect(R() * 320, R() * 320, 1 + R() * 2.5, 1 + R() * 1.5);
  }
  TEX.gouache = c;

  // Papierkorn für das ganze Bild
  c = makeCanvas(512, 512); x = c.getContext('2d');
  const id = x.createImageData(512, 512);
  for (let i = 0; i < id.data.length; i += 4) {
    const v = R();
    const n = v < 0.5 ? 0 : 255;
    id.data[i] = id.data[i + 1] = id.data[i + 2] = n;
    id.data[i + 3] = Math.floor(Math.pow(R(), 3) * 26);
  }
  x.putImageData(id, 0, 0);
  for (let i = 0; i < 260; i++) {           // Papierfasern
    x.strokeStyle = R() < .5 ? 'rgba(90,60,30,0.10)' : 'rgba(255,255,255,0.16)';
    x.lineWidth = 0.6 + R() * 0.8;
    const x0 = R() * 512, y0 = R() * 512, a = R() * TAU, L = 6 + R() * 22;
    x.beginPath(); x.moveTo(x0, y0);
    x.quadraticCurveTo(x0 + Math.cos(a + 0.5) * L / 2, y0 + Math.sin(a + 0.5) * L / 2, x0 + Math.cos(a) * L, y0 + Math.sin(a) * L);
    x.stroke();
  }
  TEX.grain = c;
}

const patCache = new Map();
function pattern(ctx, key, src) {
  let p = patCache.get(key);
  if (!p) { p = ctx.createPattern(src, 'repeat'); patCache.set(key, p); }
  return p;
}

const crayonCache = new Map();
function crayonTex(color) {
  let c = crayonCache.get(color);
  if (c) return c;
  c = makeCanvas(96, 96);
  const x = c.getContext('2d'), R = mulberry(color.length * 31 + color.charCodeAt(1));
  x.fillStyle = color;
  for (let i = 0; i < 2600; i++) {
    x.globalAlpha = 0.25 + R() * 0.75;
    x.fillRect(R() * 96, R() * 96, 1 + R() * 2.2, 1 + R() * 1.2);
  }
  x.globalAlpha = 0.55;
  x.fillRect(0, 0, 96, 96);
  // Wachslücken
  x.globalCompositeOperation = 'destination-out';
  for (let i = 0; i < 160; i++) {
    x.globalAlpha = 0.5 + R() * 0.5;
    x.fillRect(R() * 96, R() * 96, 2 + R() * 6, 1 + R());
  }
  crayonCache.set(color, c);
  return c;
}

// ------------------------------------------------------------------ Transformationsgröße
function curScale(ctx) {
  const m = ctx.getTransform();
  return Math.hypot(m.a, m.b) || 1;
}

// ------------------------------------------------------------------ Papierformen
// Polygone als Arrays [[x,y],...]; Formen-ID sorgt für stabile, aber „boilende“ Kanten.
function roughen(pts, id, amp, closed = true) {
  const out = [];
  const n = pts.length;
  const b = G.boil;
  let k = 0;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % n];
    const L = Math.hypot(x1 - x0, y1 - y0);
    const steps = Math.max(1, Math.min(14, Math.round(L / (amp * 9 + 4))));
    for (let s = 0; s < steps; s++) {
      const f = s / steps;
      const j1 = hs(id, k, b), j2 = hs(id + 77, k, b);
      const s1 = hs(id, k, 999) * 0.6;  // feste Abrisskante (ändert sich nicht)
      out.push([x0 + (x1 - x0) * f + (j1 * 0.5 + s1) * amp, y0 + (y1 - y0) * f + (j2 * 0.5 + hs(id + 5, k, 999) * 0.6) * amp]);
      k++;
    }
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
}

function pathPts(ctx, pts, closed = true) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  if (closed) ctx.closePath();
}

/* Zeichnet ein Stück Papier.
   o.id      – Formkennung (für Kanten und Textur-Versatz)
   o.rough   – Rauheit der Kante in lokalen px (Standard: automatisch)
   o.shadow  – 0 (aus) … 1 (normal) … 2 (hoch)
   o.outline – weiße Papierkontur (Standard: an)
   o.tex     – Gouache-Textur (Standard: an)
   o.alpha   – Deckkraft */
function P(ctx, pts, fill, o = {}) {
  const id = o.id ?? 1;
  const sc = curScale(ctx);
  const amp = o.rough ?? (1.4 / sc + 0.4);
  const bj = G.boil;
  const jitterX = hs(id, bj, 1) * 0.9 / sc, jitterY = hs(id, bj, 2) * 0.9 / sc;
  const r = roughen(pts, id, amp);
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  ctx.translate(jitterX, jitterY);
  pathPts(ctx, r);
  const sh = o.shadow ?? 1;
  const outline = o.outline ?? true;
  if (outline || sh) {
    if (sh && !G.fast) {
      ctx.shadowColor = `rgba(55,32,18,${0.26 * Math.min(1.4, sh)})`;
      ctx.shadowBlur = 9 * sh * G.k;
      ctx.shadowOffsetX = 3 * sh * G.k;
      ctx.shadowOffsetY = 5 * sh * G.k;
    }
    ctx.lineJoin = 'round';
    ctx.strokeStyle = o.edge || C.paper;
    ctx.lineWidth = (outline ? 5.2 : 0.6) / sc * (o.ow ?? 1);
    ctx.stroke();
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
  }
  ctx.fillStyle = fill;
  ctx.fill();
  if ((o.tex ?? true) && !G.fast) {
    const p = pattern(ctx, 'g', TEX.gouache);
    const m = new DOMMatrix();
    const s = (o.texScale ?? 1) / sc * 1.2;
    p.setTransform(m.translate(hash(id) * 300, hash(id, 3) * 300).scale(s, s).rotate(hash(id, 9) * 40 - 20));
    ctx.fillStyle = p;
    ctx.globalAlpha *= o.texAlpha ?? 0.75;
    ctx.fill();
  }
  ctx.restore();
}

// Hilfsformen -> Punktlisten
function rectPts(x, y, w, h) { return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]; }
function ellPts(cx, cy, rx, ry, n = 0, a0 = 0) {
  n = n || Math.max(10, Math.min(48, Math.round((rx + ry) / 2.2)));
  const p = [];
  for (let i = 0; i < n; i++) {
    const a = a0 + i / n * TAU;
    p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]);
  }
  return p;
}
function rrectPts(x, y, w, h, r) {
  const p = [];
  const q = (cx, cy, a0) => { for (let i = 0; i <= 4; i++) { const a = a0 + i / 4 * Math.PI / 2; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } };
  q(x + w - r, y + r, -Math.PI / 2); q(x + w - r, y + h - r, 0); q(x + r, y + h - r, Math.PI / 2); q(x + r, y + r, Math.PI);
  return p;
}
function arcPts(cx, cy, rx, ry, a0, a1, n = 16) {
  const p = [];
  for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); }
  return p;
}
function tf(pts, dx, dy, s = 1, rot = 0) {
  const c = Math.cos(rot), si = Math.sin(rot);
  return pts.map(([x, y]) => [dx + (x * c - y * si) * s, dy + (x * si + y * c) * s]);
}

const ell = (ctx, cx, cy, rx, ry, fill, o) => P(ctx, ellPts(cx, cy, rx, ry), fill, o);
const rect = (ctx, x, y, w, h, fill, o) => P(ctx, rectPts(x, y, w, h), fill, o);
const rrect = (ctx, x, y, w, h, r, fill, o) => P(ctx, rrectPts(x, y, w, h, r), fill, o);

// Einfache Füllung ohne Papier-Effekte (für kleine Details)
function flat(ctx, pts, fill, alpha = 1) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.fillStyle = fill;
  pathPts(ctx, pts);
  ctx.fill();
  ctx.restore();
}
function dot(ctx, x, y, r, fill, alpha = 1) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.fillStyle = fill;
  ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  ctx.restore();
}

// ------------------------------------------------------------------ Wachsmalstift
function polyLen(pts) {
  const L = [0];
  for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  return L;
}
function polyAt(pts, L, d) {
  if (d <= 0) return pts[0];
  const tot = L[L.length - 1];
  if (d >= tot) return pts[pts.length - 1];
  let i = 1;
  while (L[i] < d) i++;
  const f = (d - L[i - 1]) / (L[i] - L[i - 1]);
  return [lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)];
}
// Glatte Kurve durch Stützpunkte (Catmull-Rom), gibt dichte Polylinie zurück
function smooth(pts, per = 8, closed = false) {
  const out = [];
  const n = pts.length;
  const g = i => closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)];
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2);
    for (let s = 0; s < per; s++) {
      const t = s / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(k => 0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
    }
  }
  out.push(closed ? pts[0] : pts[n - 1]);
  return out;
}

/* Zeichnet eine Wachsmalstift-Linie bis zum Anteil prog (0..1).
   Liefert die Stiftspitze in lokalen Koordinaten zurück. */
function crayon(ctx, pts, prog = 1, color = C.crayonBlue, width = 7, o = {}) {
  if (prog <= 0 || pts.length < 2) return pts[0];
  const L = o.L || polyLen(pts);
  const tot = L[L.length - 1];
  const d = tot * clamp(prog);
  const sc = curScale(ctx);
  const tex = pattern(ctx, 'c' + color, crayonTex(color));
  tex.setTransform(new DOMMatrix().scale(1 / sc * 1.3, 1 / sc * 1.3));
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  if (o.dash) ctx.setLineDash(o.dash.map(v => v));
  const passes = G.fast ? 1 : 2;
  for (let pass = 0; pass < passes; pass++) {
    const ox = (pass ? 1.1 : -0.4) / sc, oy = (pass ? -0.8 : 0.5) / sc;
    const jid = (o.id || 3) + pass * 13;
    ctx.beginPath();
    let tip = pts[0];
    ctx.moveTo(pts[0][0] + ox, pts[0][1] + oy);
    for (let i = 1; i < pts.length; i++) {
      if (L[i] > d) {
        tip = polyAt(pts, L, d);
        ctx.lineTo(tip[0] + ox, tip[1] + oy);
        break;
      }
      const j = hs(jid, i, G.boil) * 0.9 / sc;
      ctx.lineTo(pts[i][0] + ox + j, pts[i][1] + oy - j);
      tip = pts[i];
    }
    ctx.strokeStyle = pass ? tex : color;
    ctx.globalAlpha *= pass ? 1 : 0.55;
    ctx.lineWidth = width * (pass ? 1 : 0.8);
    ctx.stroke();
    if (!pass) ctx.globalAlpha /= 0.55;
  }
  ctx.restore();
  return polyAt(pts, L, d);
}

// Pfeilspitze am Ende einer Linie
function crayonArrow(ctx, pts, prog, color, width) {
  const tip = crayon(ctx, pts, prog, color, width);
  if (prog < 0.98) return tip;
  const n = pts.length;
  const [x1, y1] = pts[n - 1], [x0, y0] = pts[Math.max(0, n - 4)];
  const a = Math.atan2(y1 - y0, x1 - x0), s = width * 3.2;
  crayon(ctx, [[x1 - Math.cos(a - 0.5) * s, y1 - Math.sin(a - 0.5) * s], [x1, y1], [x1 - Math.cos(a + 0.5) * s, y1 - Math.sin(a + 0.5) * s]], 1, color, width);
  return tip;
}

// ------------------------------------------------------------------ Kamera & Ebenen
// Weltpunkt (cx,cy) in Bildmitte, Zoom z, Ebenentiefe d (Parallaxe)
function camera(ctx, cx, cy, z, d = 1, sx = W / 2, sy = H / 2) {
  ctx.translate(sx, sy);
  ctx.scale(z, z);
  ctx.translate(-cx * d, -cy);
}
function toScreen(ctx, x, y) {
  const m = ctx.getTransform();
  return [(m.a * x + m.c * y + m.e) / G.k, (m.b * x + m.d * y + m.f) / G.k];
}

// Aufklapp-Effekt: Formen stehen aus der Fläche auf (scaleY um Fußpunkt)
function popup(ctx, x, y, p, fn) {
  if (p <= 0) return;
  ctx.save();
  ctx.translate(x, y);
  const s = p >= 1 ? 1 : back(p);
  ctx.scale(1, Math.max(0.02, s));
  ctx.translate(-x, -y);
  fn();
  ctx.restore();
}
// Einblenden mit kleinem Hüpfer (Skalierung um Mittelpunkt)
function pop(ctx, x, y, p, fn) {
  if (p <= 0) return;
  ctx.save();
  ctx.translate(x, y);
  const s = p >= 1 ? 1 : back(p);
  ctx.scale(s, s);
  ctx.translate(-x, -y);
  fn();
  ctx.restore();
}

// Offscreen-Puffer für Übergänge
const buffers = [];
function getBuffer(i, cw, ch) {
  let b = buffers[i];
  if (!b || b.width !== cw || b.height !== ch) { b = makeCanvas(cw, ch); buffers[i] = b; }
  return b;
}

// Scheinwerfer (Bühnenlicht): Umgebung abdunkeln, Kreis um (x,y) frei lassen
function spotlight(ctx, x, y, r, strength, color = '20,16,40') {
  if (strength <= 0) return;
  ctx.save();
  const g = ctx.createRadialGradient(x, y, r * 0.55, x, y, r * 1.25);
  g.addColorStop(0, `rgba(${color},0)`);
  g.addColorStop(1, `rgba(${color},${0.5 * strength})`);
  ctx.fillStyle = g;
  ctx.fillRect(-4000, -4000, 12000, 12000);
  ctx.restore();
}

// Weicher warmer Lichtkreis (Hervorhebung)
function halo(ctx, x, y, r, a, color = '255,214,120') {
  if (a <= 0) return;
  ctx.save();
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${color},${0.55 * a})`);
  g.addColorStop(0.6, `rgba(${color},${0.25 * a})`);
  g.addColorStop(1, `rgba(${color},0)`);
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  ctx.restore();
}

// Hintergrundpapier mit sanfter Tönung
function backdrop(ctx, color, x = -200, y = -200, w = W + 400, h = H + 400, id = 5) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
  if (!G.fast) {
    const p = pattern(ctx, 'g', TEX.gouache);
    p.setTransform(new DOMMatrix().translate(hash(id) * 200, 0).scale(2.2, 2.2));
    ctx.save();
    ctx.globalAlpha = 0.6;
    ctx.fillStyle = p;
    ctx.fillRect(x, y, w, h);
    ctx.restore();
  }
}

// Farbe abdunkeln/aufhellen
function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  let r = n >> 16, g = n >> 8 & 255, b = n & 255;
  if (f < 0) { r *= 1 + f; g *= 1 + f; b *= 1 + f; }
  else { r += (255 - r) * f; g += (255 - g) * f; b += (255 - b) * f; }
  return '#' + [r, g, b].map(v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0')).join('');
}
function mix(h1, h2, f) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const c = [16, 8, 0].map(s => Math.round(lerp(a >> s & 255, b >> s & 255, f)));
  return '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
}
