/* PROJEKTSPEZIFISCH: Szenen von „Ein Bienenvolk im Bienenstock“ (4:00, 12 Szenen).
     INTRO        – Szene 1 im Klassenzimmer (Tafel: Bienenkasten, Blumen, Bienen; Zoom in die Wiese)
     drawDraussen – Welt „Wiese“ (S1 Ende, S2, S8, S10 Ende) und „Winter“ (S11): eine Welt, Jahreszeit per Zeit
     drawStock    – Welt „im Stock“ (S3–S7, S9–S10): Kasten-Querschnitt, Waben, Bienen
     SCHLUSS      – Szene 12 im Klassenzimmer
   Alle Zeiten stehen in build/timeline.json (T.…) und werden von build/timeline_erzeugen.py aus den Satzzeiten erzeugt. */
'use strict';

// ================================================================== gemeinsame Hilfen
const fenst = (t, a, e, f = 0.5) => seg(t, a, a + f) * (1 - seg(t, e - f, e));       // sanft ein, sanft aus
const im = (t, [a, e]) => t >= a && t < e;
const progr = (t, [a, e]) => seg(t, a, e);
const sjmix = (a, b, c, sj) => (sj < 1 ? mix(a, b, sj) : mix(b, c, sj - 1));
const stufe = t => Math.floor(t * 12);                         // Stop-Motion-Takt
const BLUE = C.crayonBlue;
// Krabbeln im Stop-Motion-Takt: Beinschritt
const flatter = t => (Math.floor(t * 12) % 2);

// ================================================================== Welt „Wiese“ / „Winter“ (draußen)
const KX = 1100, KYB = 845, KS = 0.4;                          // Bienenkasten in der Wiese
const kw = (px, py) => [KX + px * KS, KYB + py * KS];          // Kastenkoordinaten → Weltkoordinaten
const FL = kw(FLUGLOCH[0], FLUGLOCH[1]);                       // Flugloch in der Welt
const jahres = t => kf([[196.8, 0], [198.7, 1], [201.4, 2]], t, sm);   // 0 Sommer, 1 Herbst, 2 Winter
const DCAM = [
  [17.0, [KX, 640, 2.3]], [23.6, [1180, 690, 1.1]], [25.1, [1180, 690, 1.1]], [28.7, [1060, 700, 1.9]], [33.4, [1060, 700, 1.9]],
  [38.0, [KX, 650, 1.5]], [41.3, [KX, 650, 1.5]],
  [138.9, [KX, 650, 1.5]], [141.3, [KX, 650, 1.5]], [145.0, [1560, 700, 1.8]], [146.2, [1650, 690, 2.5]], [153.4, [1650, 690, 2.5]],
  [158.6, [KX, 650, 1.5]], [161.3, [KX, 650, 1.5]],
  [191.0, [KX, 640, 1.3]], [193.8, [KX, 640, 1.3]], [195.6, [1190, 650, 1.25]], [197.0, [1190, 650, 1.25]], [201.4, [KX, 640, 1.5]],
  [204.4, [KX, 600, 1.5]], [207.0, [KX, 575, 1.62]], [221.0, [KX, 575, 1.62]],
];
const draussenCam = t => kf(DCAM, t, eio);

// Wiesenblumen (deterministisch), nach Tiefe sortiert
const WBLUMEN = Array.from({ length: 64 }, (_, i) => {
  const y = 800 + hash(i, 2, 5) * 240;
  return { x: -300 + hash(i, 1, 5) * 2900, y, s: 0.3 + (y - 800) / 240 * 0.55, c: Math.floor(hash(i, 3, 5) * 5), k: i };
}).sort((a, b) => a.y - b.y);
const WCOL = [C.coral, C.violet, C.paper, C.mustardL, C.coralL];
function blumeKlein(ctx, b, a) {
  const col = WCOL[b.c], s = b.s, h = 60 * s + 14, sw = Math.sin(G.t * 1.5 + b.k) * 1.5;
  strich(ctx, [[b.x, b.y], [b.x + sw, b.y - h]], C.greenD, 3.4 * s + 1);
  for (let k = 0; k < 5; k++) { const w = k / 5 * TAU; dot(ctx, b.x + sw + Math.cos(w) * 9 * s, b.y - h + Math.sin(w) * 9 * s, 6.5 * s + 1, col); }
  dot(ctx, b.x + sw, b.y - h, 4.2 * s + 1, C.mustard);
}
// Tannen
function tanne(ctx, x, yb, s, id, schnee = 0) {
  P(ctx, rectPts(x - 7 * s, yb - 26 * s, 14 * s, 26 * s), C.woodD, { id, shadow: 0.3 });
  for (let k = 0; k < 3; k++) {
    const w = (86 - k * 22) * s, y0 = yb - (20 + k * 44) * s, y1 = y0 - 62 * s;
    P(ctx, [[x - w / 2, y0], [x, y1], [x + w / 2, y0]], C.petrolD, { id: id + 1 + k, shadow: 0.5 });
    if (schnee > 0) P(ctx, [[x - w * 0.3 * schnee, y1 + 26 * s * schnee], [x, y1], [x + w * 0.3 * schnee, y1 + 26 * s * schnee], [x + w * 0.1, y1 + 18 * s * schnee], [x - w * 0.1, y1 + 20 * s * schnee]], C.paper, { id: id + 5 + k, shadow: 0, outline: false });
  }
}
// Apfelbaum: Krone folgt der Jahreszeit
function apfelbaum(ctx, x, yb, s, id, sj, t) {
  P(ctx, [[x - 14 * s, yb], [x - 9 * s, yb - 130 * s], [x + 9 * s, yb - 130 * s], [x + 14 * s, yb]], C.woodD, { id, shadow: 0.6 });
  const kron = sjmix(C.green, mix(C.mustard, C.coral, 0.4), C.woodD, sj);
  const blatt = 1 - seg(sj, 1.0, 1.7);
  strich(ctx, [[x, yb - 110 * s], [x - 50 * s, yb - 170 * s]], C.woodD, 8 * s);
  strich(ctx, [[x, yb - 120 * s], [x + 52 * s, yb - 176 * s]], C.woodD, 8 * s);
  if (blatt > 0.02) {
    const k = 0.4 + 0.6 * blatt;
    ell(ctx, x - 44 * s, yb - 176 * s, 62 * s * k, 50 * s * k, shade(kron, -0.08), { id: id + 1, shadow: 0.7 });
    ell(ctx, x + 46 * s, yb - 182 * s, 60 * s * k, 48 * s * k, kron, { id: id + 2, shadow: 0.7 });
    ell(ctx, x, yb - 210 * s, 66 * s * k, 52 * s * k, shade(kron, 0.08), { id: id + 3, shadow: 0.7 });
    if (sj < 0.9) for (let m = 0; m < 6; m++) dot(ctx, x + (hs(id, m) * 70) * s, yb - (185 + hs(id, m + 9) * 28) * s, 7 * s, C.red, 1 - seg(sj, 0.4, 0.8));
  }
  if (sj > 1.3) P(ctx, [[x - 62 * s, yb - 176 * s], [x - 20 * s, yb - 188 * s], [x + 20 * s, yb - 176 * s], [x + 60 * s, yb - 190 * s], [x + 40 * s, yb - 172 * s], [x - 40 * s, yb - 170 * s]], C.paper, { id: id + 9, shadow: 0.2, outline: false, alpha: seg(sj, 1.3, 1.8) });
}
// fliegende Biene (Seitenansicht) auf einer Bahn zwischen Flugloch und Blume
function flugBiene(ctx, t, i, ziel, tempo = 0.11, alpha = 1) {
  const u = ((t * tempo + hash(i, 4, 9)) % 1);
  const out = u < 0.5, v = out ? u * 2 : (u - 0.5) * 2;
  const a = out ? FL : ziel, b = out ? ziel : FL;
  const mid = [(a[0] + b[0]) / 2 + hs(i, 1, 9) * 70, Math.min(a[1], b[1]) - 130 - hash(i, 2, 9) * 130];
  const p = eio(v), x = (1 - p) * (1 - p) * a[0] + 2 * (1 - p) * p * mid[0] + p * p * b[0], y = (1 - p) * (1 - p) * a[1] + 2 * (1 - p) * p * mid[1] + p * p * b[1] + Math.sin(t * 5 + i) * 5;
  const x2 = ((1 - p - 0.02) ** 2) * a[0] + 2 * (1 - p - 0.02) * (p + 0.02) * mid[0] + (p + 0.02) ** 2 * b[0];
  const dir = x2 > x ? -1 : 1;            // schaut in Flugrichtung
  const fade = Math.min(seg(v, 0, 0.1), 1 - seg(v, 0.9, 1)) * (out ? 1 : 1);
  const s = 0.21 + 0.1 * Math.sin(v * Math.PI);
  bieneSeite(ctx, x, y, s, { flip: dir < 0, flap: flatter(t + i * 0.08), id: 8100 + i * 30, alpha: alpha * clamp(fade * 3), lod: 1, rot: dir * (out ? -0.12 : 0.12) });
}
const FLIEGER_ZIELE = [[1560, 790], [1700, 800], [1900, 820], [1380, 840], [1250, 880], [820, 860]];

function drawDraussen(ctx, t) {
  const [cx, cy, z] = draussenCam(t), sj = jahres(t), winter = seg(sj, 1.2, 2.0);
  const skyC = sjmix(C.sky, mix(C.sky, C.coralL, 0.3), mix(C.violet, C.cream, 0.5), sj);
  backdrop(ctx, skyC, -300, -300, W + 600, H + 600, 70);
  const L = (d, fn) => { ctx.save(); camera(ctx, cx, cy, z, d); fn(); ctx.restore(); };
  // Himmel
  L(0.12, () => {
    if (winter < 0.95) { ctx.save(); ctx.globalAlpha *= 1 - winter; sonne(ctx, 640, 215, 64, 71, t); ctx.restore(); }
    cloud(ctx, 330 + t * 3, 190, 1.4, 73, sjmix(C.paper, C.creamD, C.waterL, sj));
    cloud(ctx, 820 + t * 2, 300, 1.0, 74, sjmix(C.paper, C.creamD, C.waterL, sj));
    cloud(ctx, 60 + t * 2.5, 250, 1.2, 75, sjmix(C.paper, C.creamD, C.waterL, sj));
  });
  const hillFar = sjmix(C.petrolL, mix(C.petrolL, C.mustardD, 0.3), mix(C.waterL, C.paper, 0.55), sj);
  const hillMid = sjmix(C.green, mix(C.green, C.mustardD, 0.55), mix(C.paper, C.waterL, 0.2), sj);
  L(0.3, () => hill(ctx, [[-900, 780], [-300, 500], [300, 590], [900, 470], [1500, 580], [2100, 480], [2700, 590], [3300, 780]], hillFar, 72));
  L(0.6, () => {
    hill(ctx, [[-900, 820], [-400, 640], [200, 700], [800, 610], [1500, 690], [2200, 630], [2800, 700], [3300, 820]], hillMid, 76);
    for (const [x, s, i] of [[-100, 1.0, 0], [300, 0.8, 1], [1600, 1.1, 2], [2100, 0.9, 3], [2500, 1.0, 4]]) tanne(ctx, x, 690 + (i % 2) * 14, s, 2300 + i * 10, winter);
  });
  // Boden
  const groundC = sjmix(C.green, mix(C.green, C.mustardD, 0.55), mix(C.paper, C.waterL, 0.14), sj);
  L(1, () => {
    P(ctx, [[-1000, 760], [400, 740], [1500, 750], [3000, 745], [3200, 1500], [-1000, 1500]], groundC, { id: 77, shadow: 0.5 });
    P(ctx, [[-1000, 790], [600, 775], [1700, 790], [3000, 780], [3200, 1500], [-1000, 1500]], mix(groundC, C.greenD, 0.25 * (1 - winter)), { id: 78, shadow: 0 });
    for (const [k, y0, col] of [[0, 835, mix(groundC, C.greenD, 0.14)], [1, 905, mix(groundC, C.mustardL, 0.2)], [2, 975, mix(groundC, C.greenD, 0.26)]]) {
      const top = []; for (let m = 0; m <= 12; m++) top.push([-1000 + m * 350, y0 + Math.sin(m * 1.3 + k * 2) * 14]);
      P(ctx, top.concat([[3200, 1500], [-1000, 1500]]), col, { id: 90 + k, shadow: 0.5 });
    }
    if (winter > 0.01) for (let k = 0; k < 7; k++) P(ctx, arcPts(-200 + k * 480, 800 + (k % 3) * 70, 260, 40 * winter + 4, Math.PI, TAU, 10), C.paper, { id: 79 + k, shadow: 0.4, alpha: winter });
    // Apfelbäume
    apfelbaum(ctx, 250, 790, 1.1, 8300, sj, t);
    apfelbaum(ctx, 1850, 800, 1.2, 8320, sj, t);
    // weitere Kästen (Bienenkästen im Plural) – ploppen auf
    const k1 = progr(t, [T.kaesten[0], T.kaesten[0] + 0.5]), k2 = progr(t, [T.kaesten[1], T.kaesten[1] + 0.5]);
    const spaeter = t > 40;
    popup(ctx, 560, 805, spaeter ? 1 : k1, () => kasten(ctx, 560, 805, 0.27, { id: 7300, farbeU: C.coral, farbeO: C.mustardL, innenU: null }));
    popup(ctx, 2060, 810, spaeter ? 1 : k2, () => kasten(ctx, 2060, 810, 0.29, { id: 7320, farbeU: C.mustard, farbeO: C.petrolL }));
    // Blumen in der Tiefe
    const bl = 1 - seg(sj, 0.2, 0.9);
    if (bl > 0.02) { ctx.save(); ctx.globalAlpha *= bl; for (const b of WBLUMEN) if (b.y < 900) blumeKlein(ctx, b, 1); ctx.restore(); }
    // Der Kasten
    const oU = t < 100 ? progr(t, T.kastenAuf) : 0;
    const oO = t < 100 ? progr(t, T.kastenAuf) : seg(t, 190.6, 191.3) * (1 - eio(seg(t, 198.4, 199.6)));
    const frameIn = (zone, k0) => (c, yT, yB) => {
      for (let k = 0; k < 4; k++) {
        if (zone === 'o' && k === 2 && t > T.rahmenZiehen[0] + 0.2) continue;
        rahmen(c, (k - 1.5) * 210, yT + 12, { kind: zone === 'o' ? 'honig' : 'brut', id: 7100 + k * 10 + (zone === 'o' ? 100 : 0), deckel: 0.8 });
      }
    };
    kasten(ctx, KX, KYB, KS, { id: 7000, offenU: oU, offenO: oO, innenU: frameIn('u'), innenO: frameIn('o'), schnee: seg(sj, 1.2, 2.0), fluglochSicht: false });
    // Schnee auf dem Anflugbrett
    if (winter > 0.1) P(ctx, [[...kw(-336, -66)], [...kw(-150, -66)], [...kw(-140, -58)], [...kw(-340, -58)]], C.paper, { id: 8340, shadow: 0.3, alpha: winter, outline: false });
    // Imker
    const imkerDa = (t > 20 && t < 41) || (t > 190.5 && t < 200.6);
    if (imkerDa) drawImkerWiese(ctx, t);
    // Wächterinnen am Flugloch
    if (t > 20 && t < 41) for (const [dx, fl] of [[-14, 1], [30, 0]]) {
      const [gx, gy] = [FL[0] + dx, FL[1] + 11];
      bieneSeite(ctx, gx, gy, 0.2, { flip: !fl, flap: 0, id: 8200 + dx, rot: 0 });
    }
    // fliegende Bienen
    if (t > 20.5 && t < 41) for (let i = 0; i < 6; i++) flugBiene(ctx, t, i, FLIEGER_ZIELE[i], 0.1, seg(t, 20.5, 22));
    if (t > 139 && t < 160) for (let i = 0; i < 4; i++) flugBiene(ctx, t, i + 20, FLIEGER_ZIELE[i + 1], 0.09, 1);
    if (t > 191 && t < 200) for (let i = 0; i < 3; i++) flugBiene(ctx, t, i + 40, FLIEGER_ZIELE[i], 0.09, (1 - seg(sj, 0.6, 1.2)));
    // Blumen im Vordergrund (nahe, mit Papierform)
    if (bl > 0.02) { ctx.save(); ctx.globalAlpha *= bl; for (const b of WBLUMEN) if (b.y >= 900) { if (b.s > 0.62) blume(ctx, b.x, b.y, b.s * 1.1, WCOL[b.c], 8400 + b.k * 40, { h: 90, r: 24 }); else blumeKlein(ctx, b, 1); } ctx.restore(); }
    // Zielblume für die Sammlerin (Szene 8) – groß
    if (bl > 0.02 && t > 139 && t < 161) {
      ctx.save(); ctx.globalAlpha *= bl;
      const hb = blume(ctx, 1640, 1010, 1.9, C.coral, 8900, { h: 170, r: 38, n: 8, mitte: C.mustard });
      ctx.restore();
    }
    // Gras / Büschel
    if (bl > 0.02) for (let k = 0; k < 14; k++) gras(ctx, -200 + k * 190 + hs(k, 3) * 40, 1010 + hs(k, 4) * 20, 1.2, 8500 + k * 6, sjmix(C.greenD, mix(C.greenD, C.mustardD, 0.5), C.paper, sj));
    if (t > 139 && t < 160) drawSammlerin(ctx, t, z);
    if (t > T.schnitt[0] - 0.4 && t < 219) drawWinterKarte(ctx, t, z);
  });
  // Scheinwerfer (Szene 2: Flugloch, Wächterinnen)
  if (t > 28 && t < 41) {
    const sp = fenst(t, T.waechter[0], T.waechter[1], 0.7);
    if (sp > 0) {
      const [sx, sy] = camPt([cx, cy, z], FL[0] + 8, FL[1] + 2);
      zeige(ctx, sx, sy + 14, 150, sp, 8800, 1, sy - 50);
    }
  }
  // Dämmerlicht und Schnee/Blätter (Bildschirmkoordinaten)
  if (winter > 0) { flat(ctx, rectPts(0, 0, W, H), C.navy, 0.2 * winter); }
  drawFall(ctx, t, sj);
  if (t > T.zittern[0] - 0.4 && t < 219) drawS11Inset(ctx, t);
}
// Schneeflocken und fallende Blätter (Bildschirmraum, deterministisch)
function drawFall(ctx, t, sj) {
  const blattQ = seg(sj, 0.05, 0.5) * (1 - seg(sj, 1.2, 1.7));
  if (blattQ > 0.02) {
    for (let k = 0; k < 26; k++) {
      const sp = 70 + hash(k, 1, 4) * 80, x0 = hash(k, 2, 4) * W, ph = hash(k, 3, 4) * 20;
      const y = ((t * sp + ph * 100 + k * 90) % (H + 160)) - 80, x = x0 + Math.sin(t * 1.4 + k) * 60;
      const col = [C.mustard, C.coral, C.mustardD, C.rust][k % 4];
      if (hash(k, 5, 4) > blattQ) continue;
      P(ctx, tf(smooth([[0, -9], [8, 0], [0, 10], [-8, 0]], 3, true), x, y, 1, t * 2 + k), col, { id: 8600 + k, shadow: 0.2, outline: false });
    }
  }
  const schneeQ = seg(sj, 1.0, 1.8);
  if (schneeQ > 0.02) {
    for (let k = 0; k < 70; k++) {
      if (hash(k, 7, 4) > schneeQ) continue;
      const sp = 40 + hash(k, 1, 6) * 60, x0 = hash(k, 2, 6) * W;
      const y = ((t * sp + hash(k, 3, 6) * H) % (H + 40)) - 20, x = x0 + Math.sin(t * 0.9 + k) * 30;
      dot(ctx, x, y, 3 + hash(k, 4, 6) * 4, C.paper, 0.95);
    }
  }
}
// Imker neben dem Kasten (Szene 2 und Szene 10)
function drawImkerWiese(ctx, t) {
  const spaet = t > 150;
  let x = 1500, y = 872, o = { flip: true, id: 6100 };
  if (!spaet) {
    const gp = progr(t, T.imkerGeht);
    x = lerp(2250, 1500, eio(gp));
    o.step = gp > 0 && gp < 1 ? t * 9 : 0;
    o.armR = gp >= 1 ? 0.5 + Math.sin(t * 1.6) * 0.04 : 0.12; o.bendR = gp >= 1 ? 1.4 : 0; o.holds = gp >= 1 ? smoker : undefined;
    o.face = 'smile';
    imker(ctx, x, y, 1.7, o);
    return;
  }
  // Szene 10: Rähmchen aus dem Honigraum ziehen, Honig tropft ins Glas; im Herbst geht der Imker weg
  const zi = progr(t, T.rahmenZiehen), ab = seg(t, 198.6, 200.4);
  x = lerp(1590, 2350, eio(ab));
  const hold = eio(seg(zi, 0, 0.5));
  o.step = ab > 0 && ab < 1 ? t * 9 : 0;
  o.armR = lerp(0.2, 1.5, hold); o.armL = 0.12; o.bendR = 0; o.face = 'smile';
  imker(ctx, x, y, 1.7, o);
  // Tisch mit Glas zwischen Kasten und Imker
  const tAl = 1 - seg(t, 198.4, 199.4);
  if (t > T.glasFuellen[0] - 1.8 && tAl > 0) {
    const ap = seg(t, T.glasFuellen[0] - 1.8, T.glasFuellen[0] - 1.2);
    ctx.save(); ctx.globalAlpha *= tAl;
    popup(ctx, 1420, 880, ap, () => {
      P(ctx, rectPts(1330, 868, 180, 18), C.wood, { id: 7920, shadow: 0.8 });
      P(ctx, rectPts(1342, 886, 14, 54), C.woodD, { id: 7921, shadow: 0.3 });
      P(ctx, rectPts(1484, 886, 14, 54), C.woodD, { id: 7922, shadow: 0.3 });
      honigglas(ctx, 1420, 868, 1.15, 7930, 0.8 * eio(progr(t, T.glasFuellen)));
    });
    ctx.restore();
  }
  // Rähmchen: vom Platz im Honigraum zur Hand, dann über das Glas
  if (zi > 0 && ab < 0.6) {
    const slot = kw(105, KASTEN.zO[0] + 12);
    const q = eio(seg(zi, 0.0, 0.5)), sk2 = lerp(KS, 0.62, q);
    const hand = [1425, 600];
    const px = lerp(slot[0], hand[0], q), py = lerp(slot[1], hand[1], q) - Math.sin(q * Math.PI) * 70;
    ctx.save(); ctx.globalAlpha *= 1 - seg(ab, 0.2, 0.6); ctx.translate(px, py); ctx.rotate(lerp(0, -0.12, q) + Math.sin(t * 2) * 0.015 * q); ctx.scale(sk2, sk2);
    rahmen(ctx, 0, 0, { kind: 'honig', id: 7900, deckel: 0.75, shadow: 0.9 });
    ctx.restore();
    const gl = progr(t, T.glasFuellen);
    if (gl > 0.02 && gl < 1) {
      const fy = py + 250 * sk2, top = 868 - 96 * 1.15 - 8;
      crayon(ctx, [[px + 4, fy], [1421, top - 10], [1420, top + 24]], 1, C.mustardD, 6, { id: 7910 });
    }
  }
}
// Sammlerin an der Blume (Szene 8)
function drawSammlerin(ctx, t, z) {
  const fl = progr(t, T.ausflug), la = progr(t, T.landen);
  const start = [FL[0] + 6, FL[1] - 6], blume0 = [1706, 648];
  // Flugbahn zur Blume und zurück
  let pos, flip = true, rot = 0, s = 0.22, flap = flatter(t), ru = 0, ruw = 0;
  const rk = progr(t, T.rueckflug);
  if (t < T.landen[1] + 0.2) {
    const q = eio(fl);
    const mid = [1400, 480];
    const x = (1 - q) * (1 - q) * start[0] + 2 * (1 - q) * q * mid[0] + q * q * blume0[0], y = (1 - q) * (1 - q) * start[1] + 2 * (1 - q) * q * mid[1] + q * q * blume0[1];
    pos = [x, y]; s = lerp(0.2, 0.78, q); rot = lerp(0.25, -0.3, q); flip = true;
    if (t > T.landen[0]) flap = 0.15 + 0.1 * flatter(t);
  } else if (rk <= 0) { pos = blume0; s = 0.78; rot = -0.32; flap = 0.12; }
  else {
    const q = eio(rk);
    const mid = [1380, 520];
    const x = (1 - q) * (1 - q) * blume0[0] + 2 * (1 - q) * q * mid[0] + q * q * (FL[0] + 6), y = (1 - q) * (1 - q) * blume0[1] + 2 * (1 - q) * q * mid[1] + q * q * (FL[1] - 4);
    pos = [x, y]; s = lerp(0.78, 0.22, q); rot = lerp(0.3, -0.2, q); flip = false; flap = flatter(t);
    // beladen aussehend: leichter Hänger
  }
  const ruK = seg(t, T.ruessel[0], T.ruessel[1]) * (1 - seg(t, T.magenFuell[1], T.magenFuell[1] + 0.8));
  const mag = clamp(seg(t, T.magenFuell[0], T.magenFuell[1]));
  const poll = t > T.pollenFuell[0] ? seg(t, T.pollenFuell[0], T.pollenFuell[1]) : 0;
  const rkQ = rk > 0 ? 1 : 0;
  bieneSeite(ctx, pos[0], pos[1], s, { flip, rot, flap, ruessel: ruK, magen: t > T.ruessel[0] ? (rkQ ? 0.85 : mag * 0.85) : 0.1, pollen: rkQ ? 0.9 : poll * 0.9, id: 8700 });
  // Scheinwerfer + roter Pfeil: Rüssel, Honigmagen, Höschen
  const lp = (lx, ly) => { const sx = lx * s * (flip ? -1 : 1), sy = ly * s, c = Math.cos(rot), si = Math.sin(rot); return [pos[0] + sx * c - sy * si, pos[1] + sx * si + sy * c]; };
  if (rk <= 0) for (const [key, loc, id, r] of [['spotRuessel', [96, 28], 8780, 52], ['spotMagen', [-52, 2], 8781, 62], ['spotHoeschen', [-37, 60], 8782, 52]]) {
    const sp = fenst(t, T[key][0], T[key][1], 0.4);
    if (sp > 0) { const q = lp(loc[0], loc[1]); zeige(ctx, q[0], q[1], r, sp, id, z, q[1] - r * 0.55 - 6); }
  }
  // Strichbild: Rüssel → Honigmagen (blaue Wachsmalstift-Pfeile), nur während der Erklärung
  if (t > T.strich[0] - 0.1 && t < T.rueckflug[0] + 0.3) {
    const q = progr(t, T.strich), a = 1 - seg(t, T.rueckflug[0] - 0.4, T.rueckflug[0]);
    ctx.save(); ctx.globalAlpha *= a;
    ctx.translate(pos[0], pos[1]); ctx.scale(-s, s); ctx.rotate(0);   // flip nach links
    const tipx = 50 + 52, tipy = 10 + 25;
    const pts = smooth([[tipx - 6, tipy - 4], [58, 6], [26, -36], [-10, -44], [-40, -26], [-52, -4]], 6);
    const tipP = crayonArrow(ctx, pts, q, BLUE, 5 / Math.max(0.3, s) * 0.9);
    ctx.restore();
    if (q < 1 && q > 0) G.tip = toScreen(ctx, pos[0] - tipP[0] * s, pos[1] + tipP[1] * s);
  }
}

// ================================================================== Szene 1: Klassenzimmer
const KB = [1480, 705], KBS = 0.22;                       // Kasten auf der Tafel (rechts zuerst)
const TAFEL_BLUMEN = [[1250, 705, 0], [1160, 705, 1], [1070, 705, 2]];
const TAFEL_BIENEN = Array.from({ length: 26 }, (_, k) => [1250 + hash(k, 1, 8) * 140 + (k % 5) * 10, 470 + hash(k, 2, 8) * 120]);
const INTRO = {
  geste: [T.geste],
  tafel(ctx, t) {
    let tip = null;
    // Papierlandschaft klappt auf (zuerst, damit die Wachsmalstift-Linien oben bleiben)
    const ap = (d) => progr(t, [T.aufklappen[0] + d, T.aufklappen[0] + d + 0.6]);
    popup(ctx, 1230, 790, ap(0), () => P(ctx, [[820, 790], [900, 706], [1100, 716], [1300, 700], [1500, 712], [1640, 700], [1650, 790]], C.green, { id: 60 }));
    popup(ctx, KB[0], KB[1], ap(0.3), () => kasten(ctx, KB[0], KB[1], KBS, { id: 7400 }));
    TAFEL_BLUMEN.forEach(([x, y, i], k) => popup(ctx, x, y, ap(0.5 + k * 0.15), () => blume(ctx, x, y, 0.62, WCOL[i], 8000 + i * 40, { h: 90, r: 24 })));
    pop(ctx, 1580, 470, ap(0.7), () => sonne(ctx, 1580, 470, 28, 61, 0));
    // Kasten (blaue Linien)
    const pk = progr(t, T.tafelKasten);
    const tfk = pts => tf(pts, KB[0], KB[1], KBS);
    const kl = [
      { p: [0, 0.3], pts: [[-540, -642], [540, -642], [456, -736], [-456, -736], [-540, -642]] },
      { p: [0.3, 0.75], pts: [[-474, -642], [-474, -104], [474, -104], [474, -642]] },
      { p: [0.55, 0.8], pts: [[-474, -370], [474, -370]] },
      { p: [0.8, 1], pts: [[-340, -98], [-160, -98], [-160, -68], [-340, -68], [-340, -98]] },
    ];
    for (const q of kl) { const pp = seg(pk, q.p[0], q.p[1]); if (pp > 0) { const r2 = crayon(ctx, tfk(q.pts), pp, BLUE, 5.5, { id: 11 }); if (pp < 1 && pk < 1) tip = r2; } }
    // Blumen (blaue Linien)
    const pb = progr(t, T.tafelBlumen);
    TAFEL_BLUMEN.forEach(([x, y], k) => {
      const q = seg(pb, k / 3, (k + 1) / 3);
      if (q <= 0) return;
      const st = crayon(ctx, [[x, y], [x, y - 70]], clamp(q * 2), BLUE, 5, { id: 12 + k });
      const kopf = ellPts(x, y - 86, 17, 17, 14).concat([[x + 17, y - 86]]);
      const hd = crayon(ctx, kopf, clamp(q * 2 - 1), BLUE, 5, { id: 15 + k });
      if (q < 1) tip = q < 0.5 ? st : hd;
    });
    // Bienenpunkte (schwirrende Schar)
    const pbi = progr(t, T.tafelBienen);
    TAFEL_BIENEN.forEach(([x, y], k) => {
      const q = seg(pbi, k / TAFEL_BIENEN.length * 0.85, k / TAFEL_BIENEN.length * 0.85 + 0.15);
      if (q <= 0) return;
      const tp = crayon(ctx, ellPts(x, y, 11, 7, 10).concat([[x + 11, y]]), q, C.mustardD, 6, { id: 20 + k });
      if (q > 0.5) { crayon(ctx, [[x - 3, y - 6], [x - 3, y + 6]], 1, C.ink, 3, { id: 80 + k }); crayon(ctx, [[x + 3, y - 6], [x + 3, y + 6]], 1, C.ink, 3, { id: 110 + k }); crayon(ctx, [[x - 1, y - 8], [x + 6, y - 16]], 1, BLUE, 2.5, { id: 50 + k }); }
      if (q < 1 && pbi < 1) tip = tp;
    });
    // Fragezeichen
    const pf = progr(t, T.tafelFrage);
    if (pf > 0) { const tp = fragezeichen(ctx, 1100, 520, 0.75, pf, 70); if (pf < 1) tip = tp; }
    return tip;
  },
  zoom: { a: T.zoom[0], e: T.zoom[1], ziel: [1480, 645], Z: 4.4 },
  weltEin: [T.zoom[1] - 1.3, T.zoom[1]],
  welt: (ctx, t, a) => { ctx.save(); ctx.globalAlpha *= a; drawDraussen(ctx, t); ctx.restore(); },
};

// ================================================================== Szene 12: Klassenzimmer, Schluss
const SCHLUSS = {
  tafel(ctx, t) {
    const pos = [[1010, 470, 'koe'], [1230, 410, 'arb'], [1460, 470, 'dro']];
    const kx = 1240, ky = 700;
    let tip = null;
    // Kasten-Symbol in der Mitte unten
    pop(ctx, kx, ky - 60, seg(t, T.karten[3] - 0.3, T.karten[3] + 0.3) , () => kasten(ctx, kx, ky, 0.2, { id: 7500 }));
    pos.forEach(([x, y, typ], i) => pop(ctx, x, y, progr(t, [T.karten[i], T.karten[i] + 0.5]), () => {
      ell(ctx, x, y, 78, 62, [C.coralL, C.mustardL, C.petrolL][i], { id: 7510 + i, shadow: 0.9 });
      biene(ctx, x + 8, y, typ === 'koe' ? 0.44 : typ === 'arb' ? 0.5 : 0.46, { typ, id: 7520 + i * 60, rot: -0.2 + i * 0.1, lod: 1 });
    }));
    const pv = progr(t, T.verbinden);
    const lines = [[[1010, 535], [1190, 640]], [[1230, 475], [1240, 585]], [[1460, 535], [1290, 640]]];
    lines.forEach((l, i) => {
      const q = seg(pv, i / 3, (i + 1) / 3 + 0.05);
      if (q > 0) { const tp = crayon(ctx, smooth([l[0], [(l[0][0] + l[1][0]) / 2 + (i - 1) * 16, (l[0][1] + l[1][1]) / 2], l[1]], 6), q, BLUE, 7, { id: 30 + i }); if (q < 1) tip = tp; }
    });
    const pr = progr(t, T.ring);
    if (pr > 0) { const tp = crayon(ctx, smooth(ellPts(1235, 560, 330, 190, 20).concat([[1565, 560]]), 2), pr, BLUE, 5, { id: 40 }); if (pr < 1) tip = tp; }
    return tip;
  },
  tisch(ctx, t) {
    const items = [
      { x: 650, f: (c) => honigglas(c, 650, 800, 1.15, 7600, 0.82) },
      { x: 724, f: (c) => kerzeWachs(c, 724, 800, 1.0, 7620) },
      { x: 778, f: (c) => apfel(c, 778, 800, 1.05, 7640) },
    ];
    items.forEach((it, i) => {
      const q = t < T.tischDinge[0] - 0.3 ? 1 : 1;
      it.f(ctx);
      const sp = fenst(t, T.tischDinge[i] - 0.2, T.tischDinge[i] + 1.1, 0.4);
      if (sp > 0) { const py = 640 - 12 + Math.sin(t * 4) * 6; pop(ctx, it.x, py, sp, () => P(ctx, [[it.x - 20, py - 30], [it.x + 20, py - 30], [it.x, py + 4]], C.red, { id: 7660 + i, shadow: 1 })); }
    });
  },
  blick: T.blick,
};

// ================================================================== Ablauf
const WELTEN = [
  { a: -1, e: 20, draw: drawIntro },
  { a: 20, e: 40, draw: drawDraussen },
  { a: 40, e: 140, draw: drawStock },
  { a: 140, e: 160, draw: drawDraussen },
  { a: 160, e: 192.7, draw: drawStock },
  { a: 192.7, e: 220, draw: drawDraussen },
  { a: 220, e: 999, draw: drawSchluss },
];
const UEBERGAENGE = [
  // S2 → S3: Vorderwand klappt auf, Zoom ins Innere
  { a: 38.9, e: 41.1, A: drawDraussen, B: drawStock, fn: (c, A, B, p) => zoomIn(c, A, B, p, camPt([KX, 650, 1.5], KX, KYB + KASTEN.zU[0] * KS), 6) },
  // S7 → S8: Flugloch weitet sich zum hellen Himmel über der Wiese
  { a: 138.9, e: 141.1, A: drawStock, B: drawDraussen, fn: (c, A, B, p) => zoomIn(c, A, B, p, camPt([740, 735, 2.2], FLUG[0], FLUG[1]), 12) },
  // S8 → S9: Kamera folgt der Biene durchs Flugloch in den Stock
  { a: 158.9, e: 161.1, A: drawDraussen, B: drawStock, fn: (c, A, B, p) => zoomIn(c, A, B, p, camPt([KX, 650, 1.5], FL[0], FL[1]), 12) },
  // S10: aus dem Stock hinaus zum Imker am Kasten
  { a: T.ernteZoom[0], e: T.ernteZoom[1], A: drawStock, B: drawDraussen, fn: (c, A, B, p) => zoomOut(c, A, B, p, camPt([KX, 640, 1.3], KX, KYB + (KASTEN.zO[0] + KASTEN.zO[1]) / 2 * KS), 6) },
  // S11 → S12: Seite wird umgeblättert, zurück ins Klassenzimmer
  { a: 218.6, e: 221.4, A: drawDraussen, B: drawSchluss, fn: (c, A, B, p, t) => pageTurn(c, A, B, p, t) },
];
const ERZAEHLERIN = {
  von: 20.2, bis: 217.8,
  posen: [
    { a: 21, e: 24.5, typ: 'geste' }, { a: 29.7, e: 33, typ: 'zeigen' },
    { a: 42, e: 44.4, typ: 'geste' }, { a: 44.6, e: 48, typ: 'zeigen' },
    { a: 61.4, e: 63.4, typ: 'geste' }, { a: 69.5, e: 72.6, typ: 'zeigen' },
    { a: 81.4, e: 84.2, typ: 'geste' }, { a: T.haende[0], e: T.haende[1], typ: 'haende' },
    { a: 101.6, e: 103.8, typ: 'zeigen' }, { a: 109.3, e: 113, typ: 'zeigen' },
    { a: 121.4, e: 123.4, typ: 'geste' }, { a: 131.7, e: 134.6, typ: 'zeigen' },
    { a: 142, e: 144.4, typ: 'geste' },
    { a: 162, e: 164.6, typ: 'geste' }, { a: 170.2, e: 173.6, typ: 'zeigen' },
    { a: 181.4, e: 184, typ: 'geste' }, { a: 192, e: 195, typ: 'zeigen' },
    { a: 202, e: 206, typ: 'haende' }, { a: 211.4, e: 216, typ: 'haende' },
  ],
  ernst: [[20, 0], [200, 0], [205, 0.5], [214, 0.5], [218, 0]],
};
function STIMMUNG(t) { return 0.28 * seg(t, 200.5, 203.5) * (1 - seg(t, 215.5, 218.4)); }
