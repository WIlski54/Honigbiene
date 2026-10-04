/* Welt „im Stock“: Querschnitt des Bienenkastens, Rähmchen mit Waben, Bienen. Szenen 3–7 und 9–10.
   Eine Welt, Kamera per Keyframes. Alles ist eine reine Funktion der Zeit t. */
'use strict';

const SK = { x: 960, yb: 880 };                                  // Kasten im Stock (Maßstab 1)
const sk = (px, py) => [SK.x + px, SK.yb + py];
const FRX = k => SK.x + (k - 1.5) * 210;                         // Mitte des Rähmchens k (0..3)
const FRY = { u: SK.yb + KASTEN.zU[0] + 12, o: SK.yb + KASTEN.zO[0] + 12 };
const FOC = { cx: FRX(1), yTop: FRY.u };                         // „die“ Wabe der Szenen 4–6
const cellW = (i, j, k = 1, zone = 'u') => zellPos(FRX(k), FRY[zone], i, j);
const FLUG = sk(FLUGLOCH[0], FLUGLOCH[1]);                       // Flugloch im Stock (Welt)
const SCAM = [
  [38.9, [960, 515, 1.0]], [55.2, [960, 515, 1.0]], [60.2, [855, 648, 3.0]], [76.5, [860, 645, 3.15]], [80.4, [868, 640, 3.6]], [118.0, [868, 640, 3.6]],
  [123.0, [790, 695, 1.85]], [134.8, [790, 695, 1.85]], [138.9, [740, 735, 2.2]], [161.3, [740, 735, 2.2]], [164.2, [1060, 650, 2.1]], [178.5, [1060, 650, 2.1]],
  [181.8, [1040, 470, 2.4]], [193.8, [1040, 470, 2.4]],
];
const stockCam = t => kf(SCAM, t, eio);

// ------------------------------------------------------------------ Abreißkalender mit frei wählbaren Blattwechseln
function kalender(ctx, kx, ky, s, t, zeiten, mark = 26) {
  ctx.save(); ctx.translate(kx, ky); ctx.scale(s, s);
  P(ctx, rectPts(-6, -10, 122, 150), C.kraftD, { id: 6390, shadow: 1 });
  calendarPage(ctx, 0, 0, 110, 130, 6400, (mark + zeiten.length * 3) % 35, 1);
  for (let i = zeiten.length - 1; i >= 0; i--) {
    const p = seg(t, zeiten[i], zeiten[i] + 0.8);
    if (p >= 1) continue;
    const q = eio(p);
    ctx.save();
    ctx.translate(55, 0); ctx.scale(1, Math.cos(q * Math.PI)); ctx.rotate(q * 0.3); ctx.translate(-55, 0);
    ctx.globalAlpha *= 1 - seg(p, 0.85, 1);
    if (Math.cos(q * Math.PI) > 0) calendarPage(ctx, 0, 0, 110, 130, 6410 + (i % 12) * 5, i === 0 ? mark : -1, 1);
    else P(ctx, rectPts(0, 0, 110, 130), C.creamD, { id: 6450 + (i % 12), shadow: 0.6 });
    ctx.restore();
  }
  ctx.restore();
}
// Karte „wächst“ aus einem Bildschirmpunkt (Zelle) bis zur Endposition
function popAus(ctx, [ox, oy], p, fn) {
  if (p <= 0) return;
  ctx.save();
  const s = p >= 1 ? 1 : back(p);
  ctx.translate(ox, oy); ctx.scale(s, s); ctx.translate(-ox, -oy);
  fn();
  ctx.restore();
}

// ------------------------------------------------------------------ Rähmchen-Optionen je Zeit
const LEGE = [[0, 5], [1, 5], [2, 5], [3, 5], [4, 5], [4, 7], [3, 7], [2, 7], [1, 7]];
const HC = [1, 7];                         // die Zelle, deren Ei wir bis zur Biene verfolgen
const eiZeit = idx => T.legen[0] + (idx + 0.45) * (T.legen[1] - T.legen[0]) / LEGE.length;
function focusUeber(t) {
  return (c, art) => {
    if (c.j < 5 || c.j > 7 || c.i > 5) return art;
    const idx = LEGE.findIndex(([i, j]) => i === c.i && j === c.j);
    if (idx < 0) return 'leer';
    if (t < eiZeit(idx)) return 'leer';
    const isHC = c.i === HC[0] && c.j === HC[1];
    if (t < T.larve[0] + 0.7) return 'ei';
    if (isHC) return t < T.deckel[0] + 0.8 ? 'larve' : t < T.rausch[1] ? 'brutdeckel' : 'leer';
    if ((c.i === 3 && c.j === 7) || (c.i === 2 && c.j === 5)) return 'larve';
    return t < T.deckel[0] + 0.8 ? 'larve' : 'brutdeckel';
  };
}
function frameOpts(zone, k, t) {
  const o = { id: 7100 + k * 10 + (zone === 'o' ? 100 : 0), kind: zone === 'o' ? 'honig' : 'brut', deckel: 0.55, reif: 1 };
  const fp = t < 100 ? seg(t, T.fuellen[0], T.fuellen[1]) : 1;
  o.prog = fp; o.honigProg = fp; o.pollenProg = fp;
  if (t >= 179 && zone === 'o') { o.reif = seg(t, T.reif[0], T.reif[1]); o.deckel = 0.92 * seg(t, T.verschliessen[0], T.verschliessen[1]); o.honigProg = 1; }
  if (zone === 'u' && k === 1) o.ueberschreibe = focusUeber(t);
  // Szene 7: Zelle, die geputzt wird, und Baustelle (neue Zellen) – siehe heldin()
  return o;
}

// ------------------------------------------------------------------ Teppich aus kleinen Bienen
const TEPPICH = Array.from({ length: 180 }, (_, i) => {
  const zone = hash(i, 1, 3) < 0.6 ? 'u' : 'o';
  return { x: 575 + hash(i, 2, 3) * 770, y: zone === 'u' ? 530 + hash(i, 3, 3) * 235 : 262 + hash(i, 4, 3) * 232, ph: hash(i, 5, 3) * TAU, ph2: hash(i, 6, 3) * TAU, v: 0.6 + hash(i, 7, 3) * 0.9, r: hash(i, 8, 3) };
});
function teppichAnteil(t) {
  if (t < 56.2) return 0;
  if (t < 61.6) return 1;
  if (t < 80) return 1;
  if (t < 100) return 0.38;
  if (t < 120) return 0.8;
  if (t < 135) return 0.4;
  if (t < 160) return 0.4;
  if (t < 190) return 0.35;
  return 0.4;
}
function teppich(ctx, t, cam, ausschluss, dim = 1) {
  const [cx, cy, z] = cam, anteil = teppichAnteil(t);
  if (anteil <= 0) return;
  const vx = 960 / z + 80, vy = 540 / z + 80;
  for (let i = 0; i < TEPPICH.length; i++) {
    const b = TEPPICH[i];
    if (b.r > anteil) continue;
    const w1 = 0.7 * b.v, w2 = 1.9 * b.v;
    const px = b.x + 16 * Math.sin(w1 * t + b.ph) + 8 * Math.sin(w2 * t + b.ph2), py = b.y + 13 * Math.sin(0.6 * b.v * t + b.ph2) + 6 * Math.sin(1.7 * b.v * t + b.ph);
    if (Math.abs(px - cx) > vx || Math.abs(py - cy) > vy) continue;
    if (ausschluss && ausschluss.some(([ex, ey, er]) => Math.hypot(px - ex, py - ey) < er)) continue;
    const dx = 16 * w1 * Math.cos(w1 * t + b.ph) + 8 * w2 * Math.cos(w2 * t + b.ph2), dy = 13 * 0.6 * b.v * Math.cos(0.6 * b.v * t + b.ph2) + 6 * 1.7 * b.v * Math.cos(1.7 * b.v * t + b.ph);
    const rot = Math.atan2(dy, dx) + (flatter(t) ? 0.06 : -0.06);
    const alter = t < 61.6 ? eout(seg(t, T.teppich[0] + b.r * (T.teppich[1] - T.teppich[0]) * 0.8, T.teppich[0] + b.r * (T.teppich[1] - T.teppich[0]) * 0.8 + 0.7)) : 1;
    if (alter <= 0.02) continue;
    biene(ctx, px, py, 0.27 * alter, { rot, id: 5200 + i * 20, lod: 2, alpha: dim });
  }
}

// ------------------------------------------------------------------ Szene 4/5: Königin, Arbeiterin, Drohnen, Hofstaat
const S4 = { q: [836, 626], a: [893, 598], d0: [808, 698], d1: [903, 690] };
const QS = 0.42;
function koeniginPose(t) {
  // gibt [x, y, rot, legt (0..1 Zittern), idx] zurück
  const start = (() => { const c = cellW(LEGE[0][0], LEGE[0][1]); return [c[0] + 158 * QS, c[1]]; })();
  const wob = Math.sin(t * 1.3) * 0.05;
  if (t < T.koeniginBleibt[0]) return [S4.q[0] + Math.sin(t * 0.8) * 3, S4.q[1] + Math.cos(t * 0.7) * 3, -0.25 + wob, 0, -1];
  if (t < eiZeit(0) - 0.6) {
    const q = eio(seg(t, T.koeniginBleibt[0], T.legen[0] - 0.4));
    return [lerp(S4.q[0], start[0], q), lerp(S4.q[1], start[1], q), lerp(-0.25, 0, q) + wob * (1 - q), 0, -1];
  }
  const n = LEGE.length, slot = (T.legen[1] - T.legen[0]) / n;
  const u = clamp((t - T.legen[0]) / (T.legen[1] - T.legen[0]), 0, 0.999999);
  const idx = Math.floor(u * n), f = (u * n) - idx;
  const posOf = k => { const c = cellW(LEGE[k][0], LEGE[k][1]); const th = LEGE[k][1] === 5 ? 0 : Math.PI; return [c[0] + Math.cos(th) * 158 * QS, c[1] + Math.sin(th) * 158 * QS, th]; };
  const cur = posOf(idx), prev = idx > 0 ? posOf(idx - 1) : (() => { return [start[0], start[1], 0]; })();
  const mv = idx === 0 ? 1 : eio(seg(f, 0, 0.3));
  let rot = lerp(prev[2], cur[2], mv);
  const x = lerp(prev[0], cur[0], mv), y = lerp(prev[1], cur[1], mv);
  const lay = f > 0.3 && t < T.legen[1] ? 1 : 0;
  return [x, y + (lay ? (flatter(t) ? 1.4 : -1.4) : 0), rot, lay, idx];
}
function hofstaat(ctx, t, qp) {
  const p = progr(t, T.hofstaat);
  if (p <= 0 || t > 119) return;
  for (let k = 0; k < 6; k++) {
    const q = eout(seg(p, k * 0.1, k * 0.1 + 0.5)) * (1 - seg(t, 117.4, 118.8));
    if (q <= 0) continue;
    const a = k / 6 * TAU + 0.5 + t * 0.12, r = lerp(150, 84, q);
    const x = qp[0] + Math.cos(a) * r, y = qp[1] + Math.sin(a) * r * 0.9;
    biene(ctx, x, y, 0.3 * (0.5 + 0.5 * q), { rot: a + Math.PI + (flatter(t + k * 0.04) ? 0.1 : -0.1), id: 5800 + k * 60, alpha: q, lod: 1 });
  }
}

// ------------------------------------------------------------------ Szene 7: die junge Arbeiterin
const HELD = {
  hc: cellW(HC[0], HC[1]), put: cellW(4, 2), futter: cellW(3, 7), bau: cellW(3, 2, 0), wache: [FLUG[0] + 6, FLUG[1] - 36],
};
function heldin(t) {
  // Position/Rotation der jungen Biene: Keyframes der Wege und Halte
  const H0 = HELD, K = [
    [T.rausch[1] - 0.4, H0.hc[0] + 0, H0.hc[1] + 0],
    [T.rolle1[0] + 0.4, H0.put[0] + 0, H0.put[1] + 14],
    [T.rolle2[0] - 0.6, H0.put[0] + 0, H0.put[1] + 14],
    [T.rolle2[0] + 0.4, H0.futter[0] + 8, H0.futter[1] - 20],
    [T.rolle3[0] - 0.6, H0.futter[0] + 8, H0.futter[1] - 20],
    [T.rolle3[0] + 0.3, H0.bau[0] + 20, H0.bau[1] + 22],
    [T.rolle4[0] - 0.2, H0.bau[0] + 20, H0.bau[1] + 22],
    [T.rolle4[0] + 1.6, H0.wache[0], H0.wache[1]],
    [999, H0.wache[0], H0.wache[1]],
  ];
  const p = kf(K.map(([a, x, y]) => [a, [x, y]]), t, eio);
  // Blickrichtung: während Bewegung in Laufrichtung, an den Stationen zur Aufgabe
  let rot;
  const ph = [[T.rolle1[0] + 0.4, T.rolle2[0] - 0.6, -Math.PI / 2 + 0.2], [T.rolle2[0] + 0.4, T.rolle3[0] - 0.6, Math.PI / 2 - 0.2], [T.rolle3[0] + 0.3, T.rolle4[0] - 0.2, -Math.PI / 2], [T.rolle4[0] + 1.6, 999, Math.PI / 2]];
  const st = ph.find(([a, e]) => t >= a && t < e);
  if (st) rot = st[2];
  else { const p2 = kf(K.map(([a, x, y]) => [a, [x, y]]), t + 0.08, eio); rot = Math.atan2(p2[1] - p[1], p2[0] - p[0]); if (Math.hypot(p2[0] - p[0], p2[1] - p[1]) < 0.05) rot = -0.6; }
  return [p[0], p[1], rot];
}
const ROLLEN = [['besen', 'rolle1'], ['loeffel', 'rolle2'], ['kelle', 'rolle3'], ['wache', 'rolle4']];

// ------------------------------------------------------------------ Szene 9: Tanz
const DC = [1000, 620], DALPHA = 0.9;                          // Mitte des Tanzes, Winkel zur Senkrechten (≈ 52°)
const DU = [Math.sin(DALPHA), -Math.cos(DALPHA)], DN = [-DU[1], DU[0]];
const tanzL = t => lerp(150, 250, eio(seg(t, T.weitWeg[0], T.weitWeg[0] + 1.5)));
function tanzPose(t, L) {
  const t0 = 163.4, cyc = 5.2;
  if (t < t0) return null;
  const p = ((t - t0) / cyc) % 1, S = [DC[0] - DU[0] * L / 2, DC[1] - DU[1] * L / 2], E = [S[0] + DU[0] * L, S[1] + DU[1] * L];
  const sgn = (p < 0.5) ? 1 : -1;
  if (p < 0.24 || (p >= 0.5 && p < 0.74)) {
    const u = (p < 0.24 ? p : p - 0.5) / 0.24;
    return { x: lerp(S[0], E[0], u), y: lerp(S[1], E[1], u), rot: Math.atan2(DU[1], DU[0]) + (flatter(t) ? 0.24 : -0.24), run: true };
  }
  const u = (p < 0.5 ? (p - 0.24) / 0.26 : (p - 0.74) / 0.26), ph = u * Math.PI;
  const nn = [DN[0] * sgn, DN[1] * sgn], M = [(S[0] + E[0]) / 2, (S[1] + E[1]) / 2], r = L / 2;
  const x = M[0] + r * (Math.cos(ph) * DU[0] + Math.sin(ph) * nn[0]), y = M[1] + r * (Math.cos(ph) * DU[1] + Math.sin(ph) * nn[1]);
  const dx = r * (-Math.sin(ph) * DU[0] + Math.cos(ph) * nn[0]), dy = r * (-Math.sin(ph) * DU[1] + Math.cos(ph) * nn[1]);
  return { x, y, rot: Math.atan2(dy, dx), run: false };
}
function tanzSpur(ctx, L, z) {
  const S = [DC[0] - DU[0] * L / 2, DC[1] - DU[1] * L / 2], E = [S[0] + DU[0] * L, S[1] + DU[1] * L], M = [DC[0], DC[1]], r = L / 2;
  for (const sgn of [1, -1]) {
    const pts = [];
    for (let k = 0; k <= 18; k++) { const ph = k / 18 * Math.PI; pts.push([M[0] + r * (Math.cos(ph) * DU[0] + Math.sin(ph) * DN[0] * sgn), M[1] + r * (Math.cos(ph) * DU[1] + Math.sin(ph) * DN[1] * sgn)]); }
    crayon(ctx, pts, 1, C.paper, 4.5 / z, { alpha: 0.5, id: 9300 + (sgn > 0 ? 0 : 1) });
  }
  crayon(ctx, [S, E], 1, C.paper, 4.5 / z, { alpha: 0.5, id: 9302 });
}

// ------------------------------------------------------------------ Weltfunktion
function drawStock(ctx, t) {
  const cam = stockCam(t), [cx, cy, z] = cam;
  const inCam = fn => { ctx.save(); camera(ctx, cx, cy, z, 1); fn(); ctx.restore(); };
  const cw = 7 / z;                                            // Linienstärke auf dem Bildschirm ≈ 7 px
  backdrop(ctx, C.kraftL, -300, -300, W + 600, H + 600, 90);
  const rq = eio(progr(t, T.rahmenVor)) * (1 - eio(progr(t, T.rahmenZurueck)));
  const innen = zone => (c, yT) => {
    for (let k = 0; k < 4; k++) {
      if (zone === 'u' && k === 1 && rq > 0.02) continue;
      rahmen(c, (k - 1.5) * 210, yT + 12, frameOpts(zone, k, t));
    }
  };
  const nacht = 0.55 * seg(t, 158.9, 161.5) * (1 - seg(t, 179.0, 182.0));
  let tip = null;
  // ---------------------------------------------------------------- Kasten und Waben
  inCam(() => {
    kasten(ctx, SK.x, SK.yb, 1, { id: 7000, offenU: 1, offenO: 1, innenU: innen('u'), innenO: innen('o'), fluglochSicht: true });
    // blaue Linien um Brut- und Honigraum (Szene 3)
    const pb = progr(t, T.brutLinie), ph = progr(t, T.honigLinie);
    const rectL = (y0, y1) => [[SK.x - 478, y0], [SK.x + 478, y0], [SK.x + 478, y1], [SK.x - 478, y1], [SK.x - 478, y0 - 3]];
    if (t > 40 && t < 61) {
      if (pb > 0 && t < 56) { const tp = crayon(ctx, rectL(524, 786), pb, BLUE, cw, { id: 21 }); if (pb < 1) tip = tp; }
      if (ph > 0 && t < 56) { const tp = crayon(ctx, rectL(236, 500), ph, BLUE, cw, { id: 22 }); if (ph < 1) tip = tp; }
    }
  });
  // ---------------------------------------------------------------- Szene 3: Rähmchen schiebt sich nach vorn
  if (rq > 0.01) inCam(() => {
    flat(ctx, rectPts(-4000, -4000, 12000, 12000), C.navy, 0.5 * rq);
    const fcx = FOC.cx, fcy = FOC.yTop + 125, sc = lerp(1, 3.1, rq);
    ctx.save();
    ctx.translate(lerp(fcx, SK.x, rq), lerp(fcy, 520, rq)); ctx.scale(sc, sc); ctx.translate(-fcx, -fcy);
    rahmen(ctx, fcx, FOC.yTop, Object.assign(frameOpts('u', 1, t), { shadow: 1.6 }));
    // ein Sechseck blau umranden
    const hp = progr(t, T.sechseck);
    if (hp > 0) {
      const c = cellW(2, 4);
      const hx = sechseck(c[0], c[1], RR + 1).concat([sechseck(c[0], c[1], RR + 1)[0]]);
      const tp = crayon(ctx, hx, hp, BLUE, 7 / (z * sc), { id: 23 });
      if (hp < 1) tip = toScreen(ctx, tp[0], tp[1]);
    }
    ctx.restore();
  });
  // ---------------------------------------------------------------- Bienen
  const qp = koeniginPose(t);
  const aus = [];
  if (t >= 60 && t < 118) { if (t < 80.6) aus.push([850, 655, 135]); aus.push([qp[0], qp[1], 200]); if (t >= 80.6) aus.push([860, 690, 190]); }
  inCam(() => {
    teppich(ctx, t, cam, aus, 1);
    if (t >= 57 && t < 119) {
      const grow = t < 62 ? eout(seg(t, 58.5, 60.2)) : 1;
      // Szene 4: Königin, Arbeiterin, Drohnen
      if (t < 80.6) {
        const wob = Math.sin(t * 1.2) * 0.05, ga = 1 - seg(t, 78.4, 80.6);
        biene(ctx, S4.a[0], S4.a[1], 0.34 * grow, { typ: 'arb', rot: -0.7 + wob, id: 6200, alpha: ga });
        biene(ctx, S4.d0[0], S4.d0[1], 0.32 * grow, { typ: 'dro', rot: 0.5 - wob, id: 6300, alpha: ga });
        biene(ctx, S4.d1[0], S4.d1[1], 0.32 * grow, { typ: 'dro', rot: -0.35 + wob, id: 6400, alpha: ga });
        const yq = progr(t, T.paaren);
        if (yq > 0 && yq < 1.01) {
          const a = fenst(t, T.paaren[0], T.paaren[1], 0.5);
          biene(ctx, S4.d0[0] - 74, S4.d0[1] - 22, 0.28 * eout(seg(yq, 0, 0.2)), { typ: 'koe', rot: 0.4, id: 6500, alpha: a });
          pop(ctx, S4.d0[0] - 36, S4.d0[1] - 70 - yq * 18, seg(yq, 0.1, 0.3), () => herz(ctx, S4.d0[0] - 36, S4.d0[1] - 70 - yq * 18, 0.7, 6510, a));
        }
      }
      if (t < 119) biene(ctx, qp[0], qp[1], QS * grow, { typ: 'koe', rot: qp[2], id: 6100, flap: 0.1, alpha: 1 - seg(t, 117.4, 118.8) });
      hofstaat(ctx, t, qp);
      // Glimmer, wenn ein Ei gelegt wurde
      if (t >= T.legen[0] && t < T.legen[1] + 0.8) LEGE.forEach(([i, j], idx) => {
        const q = seg(t, eiZeit(idx), eiZeit(idx) + 0.55);
        if (q > 0 && q < 1) { const c = cellW(i, j); halo(ctx, c[0], c[1], 34 * (0.6 + q * 0.6), (1 - q) * 0.95, '255,244,190'); }
      });
    }
    if (t >= 80 && t < 100) {
      // Ei-Ring um die Zelle HC, bevor die Karte erscheint
      const hcP = progr(t, [T.kartePop[0] - 1.5, T.kartePop[0]]);
      if (hcP > 0 && t < T.karteWeg[1]) { const c = cellW(HC[0], HC[1]); crayon(ctx, ellPts(c[0], c[1], 17, 17, 14).concat([[c[0] + 17, c[1]]]), hcP, C.red, 2.6, { id: 24 }); }
    }
    // Hervorhebungen Szene 4
    for (const [key, pt, id, r, ya] of [['koeniginSpot', [qp[0] - 44, qp[1]], 6700, 58, 52], ['arbeiterinSpot', S4.a, 6710, 44, 34], ['drohnenSpot', [(S4.d0[0] + S4.d1[0]) / 2, (S4.d0[1] + S4.d1[1]) / 2 - 6], 6720, 82, 62]]) {
      const sp = fenst(t, T[key][0], T[key][1], 0.4);
      if (sp > 0 && t < 77) zeige(ctx, pt[0], pt[1], r, sp, id, z, pt[1] - ya);
    }
    // Zusammen: blauer Ring
    const zq = progr(t, T.zusammen);
    if (zq > 0 && t < 79) { const tp = crayon(ctx, smooth(ellPts(850, 655, 108, 78, 22).concat([[958, 655]]), 2), zq, BLUE, cw, { id: 25 }); if (zq < 1) tip = toScreen(ctx, tp[0], tp[1]); }
    // Szene 7: junge Biene und Helferinnen
    if (t >= T.rausch[1] - 1.0 && t < 140) {
      const hp = heldin(t), pos = (t >= 117.0 && t < T.rolle1[0] + 0.4) ? 1 : 1;
      const grow = eout(seg(t, T.rausch[1] - 1.0, T.rausch[1] - 0.3));
      const bauP = progr(t, [T.rolle3[0] + 0.2, T.rolle3[1] - 0.1]), wachs = t > T.rolle3[0] && t < T.rolle4[0] + 0.5;
      // Baustelle: neue Zelle zeichnet sich in Wachs
      if (t > T.rolle3[0]) {
        const c = HELD.bau, hx = sechseck(c[0] - 4, c[1] + 12, RR - 0.5), pr = clamp(bauP);
        P(ctx, hx, mix(WACHS, C.paper, 0.4), { id: 7050, shadow: 0.4, alpha: pr });
        if (pr > 0) crayon(ctx, hx.concat([hx[0]]), pr, WACHS_D, 3, { id: 26 });
      }
      // Begrüßung (S6 → S7): drei Arbeiterinnen am Zellrand
      const gr = fenst(t, T.rausch[1] - 0.6, T.rolle1[0] + 0.4, 0.5);
      if (gr > 0) for (let k = 0; k < 3; k++) {
        const a = -0.7 + k * 1.4, hc = HELD.hc;
        biene(ctx, hc[0] + Math.cos(a) * 62 - 20, hc[1] + Math.sin(a) * 52 - 20, 0.3, { rot: a + Math.PI + (flatter(t + k * 0.1) ? 0.1 : -0.1), id: 6600 + k * 60, alpha: gr, lod: 1 });
      }
      biene(ctx, hp[0], hp[1], 0.42 * grow, { typ: 'arb', rot: hp[2] + (flatter(t) ? 0.07 : -0.07) * (t > T.rolle1[0] ? 1 : 0), id: 6800, flap: 0.05 });
      // Putz-Bewegung: Lappen schwingt; Fütter-Tropfen
      if (t >= T.rolle1[0] + 0.4 && t < T.rolle2[0] - 0.6) {
        const o = Math.sin(t * 11) * 6;
        strich(ctx, [[hp[0] - 6 + o, hp[1] - 36], [hp[0] + 8 + o, hp[1] - 52]], C.paper, 5, 0.9);
      }
      if (t >= T.rolle2[0] + 0.4 && t < T.rolle3[0] - 0.6) {
        for (let k = 0; k < 2; k++) { const u = ((t * 1.2 + k / 2) % 1); dot(ctx, lerp(hp[0], HELD.futter[0], 0.9) + 2, lerp(hp[1] - 14, HELD.futter[1] - 4, u), 5 * (1 - u * 0.4), C.paper, 0.95); }
      }
      // Pfeil auf die junge Biene am Anfang, danach kleiner Pfeil als Marke
      const sp = fenst(t, T.rolle1[0] - 0.8, T.rolle1[0] + 2.4, 0.5);
      if (sp > 0 && t >= 119.6) zeige(ctx, hp[0], hp[1], 64, sp, 6900, z, hp[1] - 24);
      const mk = fenst(t, T.rolle1[0] + 2.4, T.alterRolle[0] - 0.3, 0.5);
      if (mk > 0) { const k = 1.0 / z, py = hp[1] - 40 * k - Math.abs(Math.sin(t * 4)) * 6 * k; pop(ctx, hp[0], py, mk, () => P(ctx, [[hp[0] - 20 * k, py - 30 * k], [hp[0] + 20 * k, py - 30 * k], [hp[0], py + 3 * k]], C.red, { id: 6901, shadow: 1 })); }
    }
    drawS10(ctx, t, z, cw);
  });
  // Dunkelheit (Szene 9) und Wärmelicht um den Tanz
  if (nacht > 0) {
    flat(ctx, rectPts(0, 0, W, H), C.navy, nacht);
    const [sx, sy] = camPt(cam, DC[0], DC[1]);
    halo(ctx, sx, sy, 560 * z / 2.1, nacht * 1.1, '255,210,120');
  }
  inCam(() => drawTanz(ctx, t, z, cw, 0, true));
  // ---------------------------------------------------------------- Karten und Bildschirm-Objekte
  if (t > 60 && t < 78) drawS4Schilder(ctx, t, cam);
  if (t >= 80.2 && t < 98) drawS5Karten(ctx, t, qp);
  if (t >= T.kartePop[0] && t < T.karteWeg[1] + 0.2) drawS6(ctx, t, cam);
  if (t >= 120 && t < 139) drawS7Schilder(ctx, t, cam);
  if (t >= 162 && t < 181) drawS9Inset(ctx, t);
  G.tip = G.tip || tip;
  if (tip) G.tip = tip;
}

// ------------------------------------------------------------------ Szene 4: Schilder ohne Schrift
function drawS4Schilder(ctx, t, cam) {
  const qp = koeniginPose(t);
  const out = 1 - seg(t, 76.4, 77.2);
  const items = [['krone', [qp[0] - 44, qp[1] - 40], 'koeniginSpot', 6760, 0.62, -190], ['hammer', [S4.a[0] + 10, S4.a[1] - 40], 'arbeiterinSpot', 6770, 0.56, -170], ['fluegel', [(S4.d0[0] + S4.d1[0]) / 2, (S4.d0[1] + S4.d1[1]) / 2 + 30], 'drohnenSpot', 6780, 0.56, 150]];
  for (const [typ, pt, key, id, s, oy] of items) {
    const p = seg(t, T[key][0] + 0.2, T[key][0] + 0.7) * out;
    if (p > 0) { ctx.save(); ctx.globalAlpha *= clamp(out * 1.5); schildW(ctx, cam, pt[0], pt[1], s, typ, p, id, 0, oy); ctx.restore(); }
  }
}

// ------------------------------------------------------------------ Szene 5: Zählbild und „keine Befehle“
function drawS5Karten(ctx, t, qp) {
  const cx0 = 1500, cy0 = 300;
  const a = progr(t, [T.legen[0] - 0.3, T.legen[0] + 0.3]) * (1 - seg(t, T.befehle[0] - 0.2, T.befehle[0] + 0.3));
  if (a > 0) {
    pop(ctx, cx0, cy0, a, () => {
      P(ctx, rrectPts(cx0 - 220, cy0 - 150, 440, 300, 20), C.kraftL, { id: 6830, shadow: 1.2 });
      const n = Math.floor(eio(seg(t, T.legen[0] + 0.1, T.legen[1] + 0.6)) * 40);
      for (let k = 0; k < 40; k++) {
        const col = k % 8, row = Math.floor(k / 8), x = cx0 - 180 + col * 51.5 + (row % 2 ? 24 : 0) - 12, y = cy0 - 106 + row * 52;
        P(ctx, sechseck(x, y, 24), C.cream, { id: 6840 + k, shadow: 0, ow: 0.5, outline: false, alpha: 0.9 });
        if (k < n) pop(ctx, x, y, seg(n - k, 0, 1), () => ell(ctx, x, y + 2, 7, 12, C.paper, { id: 6890 + k, shadow: 0.4 }));
      }
    });
  }
  const b = progr(t, [T.befehle[0], T.befehle[0] + 0.5]);
  if (b > 0 && t < 97.5) {
    const fade = 1 - seg(t, 94.8, 96);
    ctx.save(); ctx.globalAlpha *= fade;
    pop(ctx, cx0, cy0, b, () => {
      P(ctx, rrectPts(cx0 - 120, cy0 - 140, 240, 280, 24), C.paper, { id: 6940, shadow: 1.2 });
      crayon(ctx, [[cx0, cy0 - 100], [cx0 - 4, cy0 + 20]], 1, C.red, 22, { id: 6941 });
      ell(ctx, cx0 - 4, cy0 + 70, 15, 15, C.red, { id: 6942, shadow: 0 });
    });
    const x = progr(t, [T.befehle[0] + 0.5, T.befehle[1] + 0.2]);
    if (x > 0) { crayon(ctx, [[cx0 - 105, cy0 - 120], [cx0 + 105, cy0 + 120]], clamp(x * 2), C.red, 14, { id: 6943 }); crayon(ctx, [[cx0 + 105, cy0 - 120], [cx0 - 105, cy0 + 120]], clamp(x * 2 - 1), C.red, 14, { id: 6944 }); }
    ctx.restore();
  }
}

// ------------------------------------------------------------------ Szene 6: Ei → Larve → Puppe → Biene (Querschnitt)
const C6 = { x: 1090, y: 500, w: 820, h: 270 };
function drawS6(ctx, t, cam) {
  const hc = cellW(HC[0], HC[1]), org = camPt(cam, hc[0], hc[1]);
  const pp = progr(t, T.kartePop), pw = progr(t, T.karteWeg);
  const p = pp * (1 - eio(pw));
  if (p <= 0) return;
  const la = seg(t, T.larve[0], T.larve[1]), pu = seg(t, T.puppe[0], T.puppe[1]), bi = seg(t, T.biene[0], T.biene[1]);
  const fu = seg(t, T.futter[0], T.futter[0] + 0.6) * (1 - seg(t, T.deckel[0] + 0.5, T.deckel[1] + 0.5));
  const dx = kf([[T.biene[1], 0], [T.biss[0] - 0.4, 0], [T.biss[0] + 0.1, 300], [T.rausch[0] + 0.3, 300], [T.rausch[1], 1050]], t, eio);
  popAus(ctx, org, p, () => {
    // Karte mit Rand
    zellSchnitt(ctx, C6.x, C6.y, C6.w, C6.h, { ei: 1, larve: la, puppe: pu, biene: bi, futter: fu, dx, id: 7600 });
    const right = C6.x + C6.w / 2, y0 = C6.y - C6.h / 2;
    // Ammenbienen füttern (Larven-Phase)
    const nq = fenst(t, T.futter[0] - 0.2, T.deckel[0] + 0.6, 0.5);
    if (nq > 0) {
      for (let k = 0; k < 2; k++) {
        bieneSeite(ctx, right + 92 + k * 26, C6.y + (k ? 62 : -52), 0.95, { flip: true, flap: 0, id: 7700 + k * 40, alpha: nq, rot: k ? -0.1 : 0.1, kopfNick: 0.1 });
      }
      for (let k = 0; k < 4; k++) {
        const u = ((t * 0.9 + k / 4) % 1);
        if (t < T.deckel[0] + 0.2) dot(ctx, lerp(right - 14, C6.x - 150, u), C6.y + 36 + Math.sin(u * 9) * 4, 8 * (1 - u * 0.3), C.paper, 0.95 * nq);
      }
    }
    // Wachsdeckel schließt die Zelle
    const dq = progr(t, T.deckel), open = seg(t, T.rausch[0] + 0.2, T.rausch[0] + 1.2);
    if (dq > 0 && open < 1) {
      ctx.save();
      ctx.translate(right + 4 + open * 60, y0 + C6.h * 0.5); ctx.rotate(open * 0.9); ctx.globalAlpha *= 1 - open;
      const hh = C6.h * eio(dq);
      ctx.save(); ctx.translate(0, -C6.h * 0.5);
      P(ctx, rectPts(-20, 0, 40, hh), BRUTDECKEL, { id: 7650, shadow: 0.9 });
      for (let k = 0; k < 4; k++) if (hh > 30 + k * 50) strich(ctx, [[-14, 18 + k * 50], [14, 28 + k * 50]], shade(BRUTDECKEL, -0.25), 3, 0.8);
      const bq = progr(t, T.biss);
      if (bq > 0) for (let k = 0; k < 6; k++) if (bq > k / 7) P(ctx, [[-20, 18 + k * 36], [-4, 26 + k * 36], [-20, 38 + k * 36]], C.woodD, { id: 7660 + k, shadow: 0, outline: false, alpha: 0.85 });
      ctx.restore();
      ctx.restore();
    }
    // Stufen-Marken darunter
    const toks = [['ei', 0], ['larve', T.larve[1] - 0.3], ['puppe', T.puppe[0]], ['biene', T.biene[0] + 0.4]];
    toks.forEach(([typ, tt], k) => {
      const q = seg(t, tt, tt + 0.5);
      if (q <= 0) return;
      const x = C6.x - 330 + k * 220, y = 740;
      if (k) crayonArrow(ctx, [[x - 160, y], [x - 66, y]], seg(t, tt, tt + 0.5), BLUE, 6);
      pop(ctx, x, y, q, () => {
        ell(ctx, x, y, 56, 56, C.kraftL, { id: 7800 + k * 12, shadow: 0.9 });
        if (typ === 'ei') ell(ctx, x, y, 12, 28, C.paper, { id: 7801 + k * 12, shadow: 0.5 });
        if (typ === 'larve') { crayon(ctx, smooth([[x + 22, y - 18], [x + 6, y - 28], [x - 16, y - 12], [x - 20, y + 12], [x, y + 26], [x + 22, y + 14]], 5), 1, C.paper, 16, { id: 7802 + k * 12 }); }
        if (typ === 'puppe') { ell(ctx, x - 10, y, 30, 16, C.paper, { id: 7803 + k * 12, shadow: 0.4 }); ell(ctx, x + 24, y, 11, 11, C.creamD, { id: 7804 + k * 12, shadow: 0 }); for (const dy of [-1, 1]) strich(ctx, [[x - 4, y + dy * 12], [x + 4, y + dy * 24]], C.creamD, 3); }
        if (typ === 'biene') biene(ctx, x, y, 0.3, { rot: -0.4, id: 7805 + k * 12, lod: 1 });
      });
      const cur = k === 3 ? t > T.biene[0] + 0.4 : k === 2 ? (t > T.puppe[0] && t < T.biene[0] + 0.4) : k === 1 ? (t > T.larve[1] - 0.3 && t < T.puppe[0]) : t < T.larve[1] - 0.3;
      if (cur) crayon(ctx, ellPts(x, y, 66, 66, 18).concat([[x + 66, y]]), 1, C.red, 5, { id: 7860 + k });
    });
  });
  // Abreißkalender links
  const kq = progr(t, [T.kartePop[1] - 0.2, T.kartePop[1] + 0.4]) * (1 - pw);
  if (kq > 0) {
    const zt = Array.from({ length: 21 }, (_, k) => T.kalender[0] + k * (T.kalender[1] - T.kalender[0] - 0.8) / 20);
    pop(ctx, 330, 420, kq, () => kalender(ctx, 240, 310, 1.8, t, zt));
  }
}

// ------------------------------------------------------------------ Szene 7: Werkzeug-Schilder, Kalender, Aufgabenfolge
function drawS7Schilder(ctx, t, cam) {
  const hp = heldin(t);
  ROLLEN.forEach(([typ, key], k) => {
    const a = T[key][0], e = k < 3 ? T[ROLLEN[k + 1][1]][0] : T.alterRolle[0] - 0.3;
    const p = fenst(t, a + 0.1, e, 0.4);
    if (p > 0 && t < T.alterRolle[0] - 0.2) schildW(ctx, cam, hp[0], hp[1], 0.62, typ, p, 6950 + k * 40, 0, -150);
  });
  // Kalender links: springt bei jedem Wechsel weiter
  const zt = [];
  ROLLEN.forEach(([typ, key]) => { for (let k = 0; k < 4; k++) zt.push(T[key][0] + k * 0.18); });
  const kq = progr(t, [T.rolle1[0] - 0.4, T.rolle1[0] + 0.2]) * (1 - seg(t, T.flugCam[0] + 1.5, T.flugCam[0] + 2.2));
  if (kq > 0) pop(ctx, 310, 400, kq, () => kalender(ctx, 230, 300, 1.7, t, zt, 12));
  // Abschluss: vier Aufgaben in einer Reihe mit Pfeilen
  const rowOut = 1 - seg(t, T.flugCam[0] + 0.4, T.flugCam[0] + 1.2);
  if (rowOut > 0) ROLLEN.forEach(([typ], k) => {
    const x = 760 + k * 230, y = 215, p = progr(t, [T.alterRolle[k], T.alterRolle[k] + 0.45]) * rowOut;
    if (p <= 0) return;
    if (k) crayonArrow(ctx, [[x - 142, y], [x - 92, y]], seg(t, T.alterRolle[k] - 0.1, T.alterRolle[k] + 0.4), BLUE, 6);
    schild(ctx, x, y, 0.68, typ, p, 7000 + k * 40, 0, 0);
  });
}

// ------------------------------------------------------------------ Szene 9: der Tanz
function drawTanz(ctx, t, z, cw, nacht, nurHell) {
  if (t < 160.5 || t > 182) return;
  const L = tanzL(t);
  const strichZ = (nurHell ? 1 : 1);
  // Tanzspur
  const spurA = fenst(t, T.tanzSammeln[0], T.folgerGehen[0] + 1.5, 0.8) * (nurHell ? 1 : 0);
  if (nurHell) {
    if (t > 163.4 && t < T.folgerGehen[1]) tanzSpur(ctx, L, z);
    // Zuschauerinnen
    const gather = progr(t, T.tanzSammeln), leave = progr(t, T.folgerGehen);
    for (let k = 0; k < 8; k++) {
      const a = k / 8 * TAU + 0.4 + Math.sin(t * 0.3 + k) * 0.1;
      const appear = eout(seg(gather, k * 0.07, k * 0.07 + 0.5)), gone = ein(seg(leave, k * 0.05, k * 0.05 + 0.7));
      if (appear <= 0 || gone >= 1) continue;
      const rr = lerp(L * 0.55 + 110, L * 0.55 + 400, 1 - appear) + gone * 380;
      const x = DC[0] + Math.cos(a) * rr * 1.08, y = DC[1] + Math.sin(a) * rr * 0.86;
      const flying = gone > 0.05;
      biene(ctx, x, y, 0.46, { rot: a + Math.PI + (gone > 0 ? Math.PI : 0) + (flatter(t + k * 0.05) ? 0.08 : -0.08) * 1, id: 9500 + k * 40, flap: flying ? flatter(t + k * 0.03) : 0, alpha: appear * (1 - gone) });
    }
    // Tänzerin
    const arr = progr(t, T.tanzKommt);
    const pose = tanzPose(t, L);
    const poll = 0.9 * (1 - seg(t, T.tropfen[0], T.tropfen[0] + 2));
    if (t < 163.4) {
      const q = eio(arr);
      const sx = FLUG[0] + 10, sy = FLUG[1] - 20;
      const x = lerp(sx, DC[0] - DU[0] * L / 2, q), y = lerp(sy, DC[1] - DU[1] * L / 2, q) + Math.sin(q * Math.PI) * 24;
      biene(ctx, x, y, 0.55, { rot: Math.atan2(DC[1] - DU[1] * L / 2 - sy, DC[0] - DU[0] * L / 2 - sx), pollen: poll, id: 9100, alpha: eout(seg(arr, 0, 0.2)) });
    } else if (t < T.folgerGehen[1] + 0.2) {
      biene(ctx, pose.x, pose.y, 0.55, { rot: pose.rot, pollen: poll, id: 9100 });
    }
    // Linien (Richtung zur Senkrechten) und Winkelbogen
    const pr = progr(t, T.richtung);
    const pa = DC, up = [0, -270], ln = [DU[0] * 270, DU[1] * 270];
    const la = 1 - seg(t, 176.4, 177.8);
    if (pr > 0 && la > 0) {
      crayon(ctx, [[pa[0], pa[1] + 6], [pa[0], pa[1] - 270]], seg(pr, 0, 0.35), BLUE, cw, { id: 31, dash: [14, 12], alpha: 0.95 * la });
      ctx.save(); ctx.globalAlpha *= la; crayonArrow(ctx, [[pa[0], pa[1] + 6], [pa[0] + ln[0], pa[1] + ln[1]]], seg(pr, 0.3, 0.7), BLUE, cw); ctx.restore();
      crayon(ctx, arcPts(pa[0], pa[1], 150, 150, -Math.PI / 2, -Math.PI / 2 + DALPHA, 14), seg(pr, 0.65, 1), BLUE, cw * 0.9, { id: 33, alpha: la });
    }
  }
}

// Szene 9: Karte mit Wiese, Sonne, Wegweiser (Bildschirmkoordinaten)
function drawS9Inset(ctx, t) {
  const p = fenst(t, T.richtung[0] - 0.2, T.folgerGehen[1], 0.5);
  if (p <= 0) return;
  const cx0 = 1520, cy0 = 380, w = 400, h = 340;
  pop(ctx, cx0, cy0, p, () => {
    P(ctx, rrectPts(cx0 - w / 2, cy0 - h / 2, w, h, 22), C.paper, { id: 9700, shadow: 1.3 });
    ctx.save(); pathPts(ctx, rrectPts(cx0 - w / 2 + 10, cy0 - h / 2 + 10, w - 20, h - 20, 16)); ctx.clip();
    flat(ctx, rectPts(cx0 - w / 2, cy0 - h / 2, w, h), C.sky);
    P(ctx, [[cx0 - w / 2 - 20, cy0 + 40], [cx0 - 70, cy0 + 8], [cx0 + 120, cy0 + 30], [cx0 + w / 2 + 20, cy0 + 10], [cx0 + w / 2 + 20, cy0 + h / 2 + 20], [cx0 - w / 2 - 20, cy0 + h / 2 + 20]], C.green, { id: 9701, shadow: 0, outline: false });
    // Kasten (klein), Sonne, Blumen, Wegweiser
    const hv = [cx0 - 70, cy0 + 112];
    const alpha = DALPHA;
    const sun = [hv[0] - Math.sin(0.0) * 0 + 40 * 0, hv[1] - 190];
    const sunP = [hv[0] - 20, hv[1] - 178];
    const dist = lerp(120, 205, eio(seg(t, T.weitWeg[0], T.weitWeg[0] + 1.5)));
    const fl = [hv[0] + Math.sin(alpha) * dist - 20, hv[1] - Math.cos(alpha) * dist * 0.92];
    sonne(ctx, sunP[0] - 14, sunP[1] + 18, 22, 9710, 0);
    kasten(ctx, hv[0], hv[1] + 18, 0.085, { id: 9720 });
    for (let k = 0; k < 4; k++) blume(ctx, fl[0] + (k - 1.5) * 18, fl[1] + 24 + (k % 2) * 8, 0.32, WCOL[k], 9730 + k * 40, { h: 70, r: 22 });
    ctx.restore();
    // Linien: Senkrechte zur Sonne, Weg zu den Blumen, Winkelbogen (blau)
    const q = seg(t, T.richtung[0] + 0.6, T.richtung[1] + 0.2);
    crayon(ctx, [hv, [sunP[0] - 14, sunP[1] + 18]], seg(q, 0, 0.35), BLUE, 4, { id: 9760, dash: [10, 9] });
    crayonArrow(ctx, [hv, [fl[0], fl[1] + 12]], seg(q, 0.3, 0.75), BLUE, 4.5);
    crayon(ctx, arcPts(hv[0], hv[1], 78, 78, -Math.PI / 2 - 0.1, -Math.PI / 2 + alpha, 12), seg(q, 0.7, 1), BLUE, 3.6, { id: 9761 });
    // Wegweiser am Rand der Wiese
    const sx0 = cx0 + 120, sy0 = cy0 + 150;
    P(ctx, rectPts(sx0 - 5, sy0 - 80, 10, 80), C.woodD, { id: 9770, shadow: 0.5 });
    P(ctx, [[sx0 - 54, sy0 - 98], [sx0 + 40, sy0 - 98], [sx0 + 62, sy0 - 80], [sx0 + 40, sy0 - 62], [sx0 - 54, sy0 - 62]], C.mustard, { id: 9771, shadow: 0.6 });
    ell(ctx, sx0 - 34, sy0 - 80, 9, 9, C.paper, { id: 9772, shadow: 0 });
  });
}

// ------------------------------------------------------------------ Szene 10: Nektar weitergeben, fächeln, verdeckeln
function drawS10(ctx, t, z, cw) {
  if (t < 178 || t > 194) return;
  // (a) Übergabe Rüssel zu Rüssel: Sammlerin → Stockbiene A → Stockbiene B
  const SB = [1000, 586], AB = [1000, 532], BB = [1044, 532];
  const tq = progr(t, T.tropfen), wq = progr(t, T.weitergeben);
  const sAlpha = 1 - seg(t, T.weitergeben[0] + 1.2, T.weitergeben[0] + 2.2);
  if (t >= 178.2) {
    const sRot = -Math.PI / 2, aRot = lerp(Math.PI / 2, 0, eio(seg(t, T.weitergeben[0] + 1.6, T.weitergeben[0] + 2.2)));
    const sCent = lerp(1, 1, 1);
    // alte Sammlerin vom Tanz nahe der Position
    const sam = lerp(0, 1, eio(seg(t, 177.6, 179.2)));
    const sx = lerp(DC[0], SB[0], sam), sy = lerp(DC[1], SB[1], sam);
    if (sAlpha > 0) biene(ctx, sx, sy, 0.55, { rot: lerp(0.6, sRot, sam), pollen: 0.9 * (1 - seg(t, T.tropfen[0], T.tropfen[0] + 2)), id: 9100, alpha: sAlpha });
    const aA = eout(seg(t, 178.4, 179.6));
    biene(ctx, AB[0] + (1 - aA) * -90, AB[1], 0.5, { rot: aRot, id: 9900, alpha: aA });
    const bA = eout(seg(t, T.weitergeben[0] + 1.4, T.weitergeben[0] + 2.4));
    if (bA > 0) biene(ctx, BB[0] + (1 - bA) * 80, BB[1], 0.5, { rot: Math.PI, id: 9950, alpha: bA });
    // Tropfen wandert
    const d1 = seg(t, 179.8, T.weitergeben[0] + 1.5), d2 = seg(t, T.weitergeben[0] + 2.3, T.weitergeben[0] + 3.4);
    if (d1 > 0 && d1 < 1) { const x = lerp(SB[0], AB[0], 0.5), y = lerp(SB[1] - 28, AB[1] + 26, d1); dot(ctx, x, y, 5, C.mustard); }
    if (d2 > 0 && d2 < 1) { dot(ctx, lerp(AB[0] + 28, BB[0] - 28, d2), AB[1], 5, C.mustard); }
  }
  // (b) Fächelnde Bienen
  const fq = fenst(t, T.faecheln[0] - 0.3, 191.7, 0.6);
  if (fq > 0) {
    for (let k = 0; k < 4; k++) {
      const x = [900, 1010, 1110, 1190][k], y = 362 + (k % 2) * 28, rot = -Math.PI / 2 + (k - 1.5) * 0.12;
      biene(ctx, x, y, 0.5 * fq, { rot, flap: flatter(t + k * 0.04), id: 9980 + k * 60, alpha: fq });
      for (let m = 0; m < 3; m++) {
        const u = ((t * 1.1 + m / 3 + k * 0.2) % 1);
        crayon(ctx, arcPts(x + (m - 1) * 26, y - 40 - u * 50, 14, 7, Math.PI * 1.1, Math.PI * 1.9, 5), 1, C.waterD, 2.6 / Math.max(z / 2.4, 0.5), { alpha: 0.7 * fq * (1 - u), id: 9960 + k * 3 + m });
      }
    }
  }
  // (c) Verdeckeln: Arbeiterinnen laufen an den Zellen entlang
  const vq = fenst(t, T.verschliessen[0], T.verschliessen[1] + 0.4, 0.4);
  if (vq > 0) {
    for (let k = 0; k < 3; k++) {
      const u = seg(t, T.verschliessen[0], T.verschliessen[1]);
      const x = 880 + k * 150 + 40 * Math.sin(t * 1.3 + k * 2), y = 440 + k * 18 - u * 20;
      biene(ctx, x, y, 0.5 * vq, { rot: -Math.PI / 2 + 0.5 * Math.sin(t * 1.1 + k), id: 10100 + k * 60, alpha: vq });
    }
  }
}

// ------------------------------------------------------------------ Szene 11: Querschnitt im Winter – Wintertraube
const WK = { x: 1100, y: 575, w: 620, h: 470 };                   // Karte in Weltkoordinaten (Draußen-Welt)
const TRAUBE = Array.from({ length: 130 }, (_, i) => ({ r: Math.sqrt(hash(i, 1, 11)) * 150, a: hash(i, 2, 11) * TAU, ph: hash(i, 3, 11) * TAU, v: 0.5 + hash(i, 4, 11), sx: WK.x + (hash(i, 5, 11) - 0.5) * 560, sy: WK.y + (hash(i, 6, 11) - 0.5) * 420 }));
function drawWinterKarte(ctx, t, z) {
  const pq = progr(t, T.schnitt);
  if (pq <= 0) return;
  const cx0 = WK.x, cy0 = WK.y, org = [KX, 697];
  ctx.save();
  const sc = pq >= 1 ? 1 : back(pq);
  ctx.translate(org[0], org[1]); ctx.scale(sc, sc); ctx.translate(-org[0], -org[1]);
  P(ctx, rrectPts(cx0 - WK.w / 2 - 16, cy0 - WK.h / 2 - 16, WK.w + 32, WK.h + 32, 26), C.kraft, { id: 11000, shadow: 1.4 });
  P(ctx, rrectPts(cx0 - WK.w / 2, cy0 - WK.h / 2, WK.w, WK.h, 18), mix(C.navy, C.violet, 0.4), { id: 11001, shadow: 0, outline: false });
  ctx.save(); pathPts(ctx, rrectPts(cx0 - WK.w / 2, cy0 - WK.h / 2, WK.w, WK.h, 18)); ctx.clip();
  // Honigvorrat rundum
  const R0 = 168;
  zellen(ctx, cx0 - WK.w / 2 + 6, cy0 - WK.h / 2 + 6, WK.w - 12, WK.h - 12, { kind: 'honig', fid: 77, deckel: 0.7, honigProg: 1,
    ueberschreibe: (c, art) => (Math.hypot(cx0 - WK.w / 2 + 6 + c.x - cx0, cy0 - WK.h / 2 + 6 + c.y - cy0) < R0 + 8 ? 'leer' : art) });
  // Wärmeschimmer
  const warm = seg(t, T.traube[0] + 0.6, T.traube[1]) * (0.55 + 0.45 * seg(t, T.zittern[0], T.zittern[0] + 1.5));
  halo(ctx, cx0, cy0, 300, warm * 1.1, '238,110,90');
  // Bienen: erst verstreut, dann zur Traube; außen und innen tauschen sich aus
  const gq = eio(progr(t, [T.traube[0], T.traube[1]]));
  const amp = 1.3 + 2.6 * seg(t, T.zittern[0], T.zittern[0] + 1.0);
  TRAUBE.forEach((b, i) => {
    const swap = 0.5 + 0.5 * Math.sin(0.5 * t * b.v + b.ph);
    const r = b.r * (0.55 + 0.45 * swap), bx = cx0 + Math.cos(b.a + t * 0.04 * (i % 2 ? 1 : -1)) * r, by = cy0 + Math.sin(b.a + t * 0.04 * (i % 2 ? 1 : -1)) * r * 0.97;
    const sx = b.sx + Math.sin(t * 0.8 * b.v + b.ph) * 14, sy = b.sy + Math.cos(t * 0.7 * b.v + b.ph) * 12;
    const x = lerp(sx, bx, gq) + hs(i, stufe(t), 3) * amp * gq, y = lerp(sy, by, gq) + hs(i, stufe(t), 4) * amp * gq;
    if (Math.hypot(x - cx0, y - cy0) > R0 + 6 && gq > 0.95) return;
    biene(ctx, x, y, 0.21, { rot: lerp(b.a * 3 + t * 0.2, b.a + Math.PI / 2, gq), id: 11100 + i * 20, lod: 2, alpha: 1 });
  });
  // Königin in der Mitte
  biene(ctx, cx0, cy0, 0.3, { typ: 'koe', rot: 0.5, id: 11050 });
  ctx.restore();
  ctx.restore();
  // Honigvorrat: Pfeil und blaue Linie
  const hv = fenst(t, T.honigVorrat[0], T.honigVorrat[1] + 1.2, 0.5);
  if (hv > 0) {
    ctx.save();
    crayon(ctx, smooth([[cx0 - 130, cy0 - 70], [cx0 - 200, cy0 - 120], [cx0 - 255, cy0 - 150]], 5), seg(t, T.honigVorrat[0] + 0.2, T.honigVorrat[0] + 1.6), BLUE, 7 / z, { id: 11060 });
    zeige(ctx, cx0 - 230, cy0 - 130, 105, hv, 11070, z, cy0 - 168);
    ctx.restore();
  }
}
// Lupe auf die zitternde Biene (Bildschirmkoordinaten)
function drawS11Inset(ctx, t) {
  const p = fenst(t, T.zittern[0] - 0.2, T.honigVorrat[0] + 0.4, 0.5);
  if (p <= 0) return;
  const cx0 = 1565, cy0 = 330, r = 168;
  pop(ctx, cx0, cy0, p, () => {
    ell(ctx, cx0, cy0, r + 12, r + 12, C.paper, { id: 11200, shadow: 1.3 });
    ctx.save(); pathPts(ctx, ellPts(cx0, cy0, r, r, 40)); ctx.clip();
    flat(ctx, rectPts(cx0 - r, cy0 - r, 2 * r, 2 * r), mix(C.navy, C.violet, 0.4));
    halo(ctx, cx0 - 20, cy0 - 10, 150, 0.85 * seg(t, T.zittern[0], T.zittern[0] + 1.2), '238,110,90');
    const sh = (flatter(t) ? 2.4 : -2.4) * seg(t, T.zittern[0], T.zittern[0] + 1);
    bieneSeite(ctx, cx0 - 24 + sh, cy0 + 10, 1.16, { flap: 0.1, id: 11210 });
    // Flugmuskeln in der Brust: roter Fleck mit Zitterlinien
    const mq = seg(t, T.muskel[0], T.muskel[0] + 0.8);
    if (mq > 0) {
      ell(ctx, cx0 - 24 + sh + 3, cy0 + 8, 24 * mq, 22 * mq, C.coral, { id: 11220, shadow: 0, alpha: 0.85 });
      for (let k = 0; k < 4; k++) { const a = -1.2 + k * 0.8; strich(ctx, [[cx0 - 24 + Math.cos(a) * 46, cy0 + 8 + Math.sin(a) * 40], [cx0 - 24 + Math.cos(a) * 62 + sh * 2, cy0 + 8 + Math.sin(a) * 54]], C.red, 4, mq); }
    }
    ctx.restore();
    if (t > T.muskel[0] && t < T.muskel[1] + 1) {
      const sp = fenst(t, T.muskel[0], T.muskel[1] + 0.6, 0.4);
      const py = cy0 - 74 - Math.sin(t * 4) * 6;
      pop(ctx, cx0 - 20, py, sp, () => P(ctx, [[cx0 - 46, py - 40], [cx0 + 6, py - 40], [cx0 - 20, py + 4]], C.red, { id: 11230, shadow: 1 }));
    }
  });
}
