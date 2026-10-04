/* Bausteine für „Ein Bienenvolk im Bienenstock“ – Papierformen aus P-Formen, Farben nur aus C.
   Biene (Draufsicht: Arbeiterin, Königin, Drohne; Seitenansicht mit Honigmagen/Pollenhöschen), Bienenkasten mit
   aufklappbarer Vorderwand, Rähmchen mit Wabe (Sechsecke), Zellen-Querschnitt, Imker, Blume, Honigglas, Kerze, Apfel,
   Piktogramme (Krone, Hammer, Flügel, Besen, Löffel, Kelle, Wache). Ursprung der Figuren = Mitte/Fußpunkt (siehe Kommentar). */
'use strict';

const WACHS = mix(C.mustardL, C.cream, 0.55);          // helles Wachs
const WACHS_D = mix(C.mustardD, C.kraftD, 0.45);        // Zellkante
const HONIG = C.mustard;
const NEKTAR = mix(C.mustardL, C.paper, 0.45);          // frischer, dünner Nektar
const POLLEN = mix(C.coral, C.mustard, 0.55);
const BRUTDECKEL = mix(C.kraft, C.kraftL, 0.5);

// einfache, billige Linie (für kleine Details wie Beine)
function strich(ctx, pts, col, w, a = 1) {
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  pathPts(ctx, pts, false); ctx.stroke(); ctx.restore();
}
function sechseck(cx, cy, r, a0 = -Math.PI / 2) {
  const p = [];
  for (let k = 0; k < 6; k++) { const a = a0 + k * Math.PI / 3; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
  return p;
}
function hexPath(path, cx, cy, r, a0 = -Math.PI / 2) {
  for (let k = 0; k < 6; k++) {
    const a = a0 + k * Math.PI / 3, x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
    if (k) path.lineTo(x, y); else path.moveTo(x, y);
  }
  path.closePath();
}

/* ================================================================== Biene von oben
   Ursprung = Mitte der Brust, schaut nach +x (rot dreht). typ: 'arb' | 'koe' | 'dro'
   o: rot, flip, flap (0..1 Flügelspreizung), pollen (0..1 Höschen), alpha, id, lod (0 voll, 1 einfach, 2 winzig), crayon */
const BIENE_SPEC = {
  arb: { ab: [[-100, 0], [-86, -20], [-56, -31], [-26, -27], [-10, -12], [-8, 0], [-10, 12], [-26, 27], [-56, 31], [-86, 20]],
    bands: [[-98, -84], [-74, -61], [-50, -39]], br: [25, 26], bc: C.mustardD, kopf: [18, 20], aug: [9, 12, 15], augC: C.ink,
    wf: [104, 17], wh: [74, 12], ant: 1, lang: 1 },
  koe: { ab: [[-158, 0], [-140, -12], [-108, -24], [-70, -29], [-34, -27], [-12, -14], [-8, 0], [-12, 14], [-34, 27], [-70, 29], [-108, 24], [-140, 12]],
    bands: [[-120, -110], [-92, -83], [-64, -56]], br: [27, 28], bc: C.woodL, kopf: [17, 19], aug: [7, 10, 14], augC: C.ink,
    wf: [78, 15], wh: [56, 11], ant: 1, lang: 1.15, punkt: true },
  dro: { ab: [[-104, 0], [-98, -22], [-72, -40], [-40, -41], [-14, -30], [-8, 0], [-14, 30], [-40, 41], [-72, 40], [-98, 22]],
    bands: [[-104, -80], [-62, -52]], br: [32, 34], bc: C.woodL, kopf: [15, 22], aug: [19, 24, 14], augC: C.navy,
    wf: [128, 21], wh: [92, 15], ant: 0.6, lang: 0.95, dunkel: true },
};
function biene(ctx, x, y, s, o = {}) {
  const typ = o.typ || 'arb', S = BIENE_SPEC[typ], id = o.id ?? 5000, lod = o.lod || 0;
  const flap = o.flap || 0;
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(s, o.flip ? -s : s);
  const sh = lod ? 0 : 0.5;
  const abPts = smooth(S.ab, lod ? 3 : 5, true);
  const wing = (sg, L, ry, ang, bx, by, k) => {
    const dx = -Math.cos(ang), dy = sg * Math.sin(ang), cx = bx + dx * L / 2, cy = by + dy * L / 2, rot = Math.atan2(dy, dx);
    P(ctx, tf(ellPts(0, 0, L / 2, ry, lod ? 10 : 16), cx, cy, 1, rot), C.waterL, { id: id + k, shadow: 0, alpha: 0.5, outline: lod < 2 });
    if (!lod) strich(ctx, [[bx + dx * 10, by + dy * 10], [bx + dx * L * 0.88, by + dy * L * 0.88]], C.paper, 2.2, 0.7);
  };
  // Beine (hinten)
  if (!lod) {
    const lc = typ === 'dro' ? C.woodD : C.ink, lw = 5.2;
    for (const sg of [-1, 1]) {
      strich(ctx, [[16, sg * 18], [36, sg * 44], [56, sg * 62]], lc, lw);
      strich(ctx, [[-2, sg * 22], [-4, sg * 52], [6, sg * 78]], lc, lw);
      strich(ctx, [[-18, sg * 22], [-46, sg * 50], [-66, sg * 76]], lc, lw);
      if (typ === 'arb' && (o.pollen || 0) > 0) {
        const q = o.pollen;
        P(ctx, tf(ellPts(0, 0, 8 + 10 * q, 7 + 14 * q, 12), -52, sg * 60, 1, sg * 0.55), C.mustardL, { id: id + 40 + (sg > 0 ? 1 : 0), shadow: 0.3 });
        P(ctx, tf(ellPts(0, 0, 4 + 7 * q, 3 + 8 * q, 10), -53, sg * 61, 1, sg * 0.55), C.mustard, { id: id + 42 + (sg > 0 ? 1 : 0), shadow: 0, outline: false });
      }
    }
  }
  // Flügel: Hinterflügel, Vorderflügel (beide Seiten)
  const fa = 0.62 + flap * 0.4;
  for (const sg of [-1, 1]) {
    wing(sg, S.wh[0], S.wh[1], fa + 0.5, -4, sg * 14, 1 + (sg > 0 ? 1 : 0));
    wing(sg, S.wf[0], S.wf[1], fa, 0, sg * 14, 3 + (sg > 0 ? 1 : 0));
  }
  // Hinterleib mit Streifen
  P(ctx, abPts, S.dunkel ? C.woodD : (typ === 'koe' ? C.mustardL : C.mustard), { id: id + 10, shadow: sh });
  ctx.save();
  pathPts(ctx, abPts); ctx.clip();
  ctx.fillStyle = S.dunkel ? C.mustardD : C.ink;
  for (const [x0, x1] of S.bands) {
    ctx.beginPath(); ctx.moveTo(x0, -45); ctx.lineTo(x1, -45); ctx.quadraticCurveTo(x1 + 7, 0, x1, 45); ctx.lineTo(x0, 45); ctx.quadraticCurveTo(x0 + 7, 0, x0, -45); ctx.fill();
  }
  if (typ === 'arb' && lod < 2) { // dunkle Spitze
    ctx.beginPath(); ctx.moveTo(-104, -20); ctx.lineTo(-96, -20); ctx.lineTo(-96, 20); ctx.lineTo(-104, 20); ctx.fill();
  }
  ctx.restore();
  // Brust
  P(ctx, ellPts(S.br[0] * 0 + 2, 0, S.br[0], S.br[1], lod ? 10 : 16), typ === 'arb' ? C.mustardD : S.bc, { id: id + 11, shadow: sh });
  if (lod < 2) {
    strich(ctx, [[-14, -9], [18, -7]], C.ink, 3.6, 0.7);
    strich(ctx, [[-14, 9], [18, 7]], C.ink, 3.6, 0.7);
  }
  if (S.punkt) dot(ctx, 0, 0, 8, C.red);              // Königin: roter Punkt auf dem Rücken
  // Kopf mit Augen und Fühlern
  const hx = S.br[0] + S.kopf[0] - 4;
  if (!lod && S.ant) {
    for (const sg of [-1, 1]) {
      const k = S.ant;
      strich(ctx, [[hx + 6, sg * 7], [hx + 30 * k, sg * 14], [hx + 50 * k, sg * 38 * (typ === 'dro' ? 0.7 : 1)]], C.ink, 3.2);
      dot(ctx, hx + 50 * k, sg * 38 * (typ === 'dro' ? 0.7 : 1), 3.2, C.ink);
    }
  }
  P(ctx, ellPts(hx, 0, S.kopf[0], S.kopf[1], lod ? 8 : 14), C.woodD, { id: id + 12, shadow: sh });
  for (const sg of [-1, 1]) {
    P(ctx, ellPts(hx + 2, sg * S.aug[2], S.aug[0], S.aug[1], lod ? 8 : 12), S.augC, { id: id + 13 + (sg > 0 ? 1 : 0), shadow: 0, outline: false });
    if (!lod) dot(ctx, hx + 5, sg * (S.aug[2] + 3), 2.6, C.paper, 0.85);
  }
  ctx.restore();
}

// einfache winzige Biene (viele auf der Wabe)
function bieneKlein(ctx, x, y, s, rot, id, flip = false) {
  biene(ctx, x, y, s, { rot, id, lod: 2, flip });
}

/* ================================================================== Biene von der Seite (schaut nach rechts)
   Ursprung = Mitte der Brust. o: flip (schaut nach links), rot, flap (0..1), pollen (0..1), magen (−1 aus, 0..1 Füllung),
   ruessel (0..1 ausgestreckt), kopfNick, id, alpha */
function bieneSeite(ctx, x, y, s, o = {}) {
  const id = o.id ?? 5400, flap = o.flap ?? 0.5;
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(o.flip ? -s : s, s);
  const lod = o.lod || 0;
  const wing = (L, ry, deg, bx, by, a, k) => {
    const dx = -Math.cos(deg), dy = -Math.sin(deg), cx = bx + dx * L / 2, cy = by + dy * L / 2, rot = Math.atan2(dy, dx);
    P(ctx, tf(ellPts(0, 0, L / 2, ry, 16), cx, cy, 1, rot), C.waterL, { id: id + k, shadow: 0, alpha: a });
    if (!lod) strich(ctx, [[bx + dx * 8, by + dy * 8], [bx + dx * L * 0.88, by + dy * L * 0.88]], C.paper, 2, a + 0.2);
  };
  const ph = 0.38 + flap * 0.95;
  // ferne Beine und Flügel
  if (!lod) {
    for (const [a, k, kn, f] of [[[10, 18], 0, [26, 40], [40, 62]], [[-4, 20], 1, [-2, 44], [8, 70]], [[-18, 20], 2, [-34, 46], [-44, 72]]]) {
      strich(ctx, [[a[0] + 6, a[1]], [kn[0] + 6, kn[1]], [f[0] + 6, f[1]]], C.woodD, 4.6, 0.8);
    }
  }
  wing(86, 14, ph + 0.3, 0, -18, 0.42, 1);
  wing(62, 10, ph + 0.5, -4, -18, 0.42, 2);
  // Hinterleib
  const ab = smooth([[-100, 8], [-88, -12], [-58, -26], [-26, -24], [-6, -12], [-2, 4], [-10, 18], [-36, 28], [-70, 26], [-92, 20]], lod ? 3 : 5, true);
  P(ctx, ab, C.mustard, { id: id + 3, shadow: lod ? 0 : 0.5 });
  ctx.save(); pathPts(ctx, ab); ctx.clip(); ctx.fillStyle = C.ink;
  for (const [x0, x1] of [[-98, -86], [-76, -63], [-52, -41]]) {
    ctx.beginPath(); ctx.moveTo(x0, -40); ctx.lineTo(x1, -40); ctx.quadraticCurveTo(x1 + 8, 0, x1 - 2, 40); ctx.lineTo(x0 - 2, 40); ctx.quadraticCurveTo(x0 + 6, 0, x0, -40); ctx.fill();
  }
  ctx.restore();
  // Honigmagen (Schnittbild im Hinterleib)
  if ((o.magen ?? -1) >= 0) {
    const q = o.magen, cx = -52, cy = 2, rx = 27, ry = 17;
    P(ctx, ellPts(cx, cy, rx, ry, 18), C.paper, { id: id + 4, shadow: 0.2, alpha: 0.92 });
    if (q > 0) {
      ctx.save(); pathPts(ctx, ellPts(cx, cy, rx - 1, ry - 1, 18)); ctx.clip();
      ctx.fillStyle = C.mustard; ctx.fillRect(cx - rx, cy + ry - 2 * ry * q, 2 * rx, 2 * ry * q + 2);
      ctx.restore();
    }
    crayon(ctx, ellPts(cx, cy, rx, ry, 18).concat([[cx + rx, cy]]), 1, C.crayonBlue, 3.2, { id: id + 5 });
  }
  // Brust
  P(ctx, ellPts(2, 0, 25, 24, 14), C.mustardD, { id: id + 6, shadow: lod ? 0 : 0.5 });
  if (!lod) for (let k = 0; k < 7; k++) strich(ctx, [[-14 + k * 5, -18 + (k % 2) * 6], [-12 + k * 5, -10 + (k % 2) * 6]], C.mustardL, 2.2, 0.8);
  // nahe Beine
  const pol = o.pollen || 0;
  if (!lod) {
    strich(ctx, [[14, 18], [30, 42], [44, 64]], C.ink, 5);
    strich(ctx, [[0, 20], [0, 46], [12, 72]], C.ink, 5);
    strich(ctx, [[-14, 20], [-32, 46], [-42, 74]], C.ink, 5);
    if (pol > 0) {
      P(ctx, tf(ellPts(0, 0, 10 + 9 * pol, 8 + 15 * pol, 14), -37, 56, 1, 0.45), C.mustardL, { id: id + 7, shadow: 0.4 });
      P(ctx, tf(ellPts(0, 0, 5 + 6 * pol, 4 + 8 * pol, 10), -38, 57, 1, 0.45), C.mustard, { id: id + 8, shadow: 0, outline: false });
    }
  }
  // Kopf
  const nick = o.kopfNick || 0;
  ctx.save(); ctx.translate(30, 2); ctx.rotate(nick); ctx.translate(-30, -2);
  const ru = o.ruessel || 0;
  if (ru > 0) {
    const ra = 0.45 + (o.ruesselWinkel || 0);
    strich(ctx, [[50, 10], [50 + Math.cos(ra) * 58 * ru, 10 + Math.sin(ra) * 58 * ru]], C.woodL, 6);
    strich(ctx, [[50, 10], [50 + Math.cos(ra) * 58 * ru, 10 + Math.sin(ra) * 58 * ru]], C.paper, 1.6, 0.6);
  }
  if (!lod) {
    strich(ctx, [[48, -12], [64, -34], [86, -40]], C.ink, 3.2);
    strich(ctx, [[44, -14], [54, -38], [72, -52]], C.ink, 3.2, 0.8);
  }
  P(ctx, ellPts(38, 0, 21, 20, 14), C.woodD, { id: id + 9, shadow: lod ? 0 : 0.5 });
  P(ctx, ellPts(43, -5, 10, 13, 12), C.ink, { id: id + 10, shadow: 0, outline: false });
  dot(ctx, 46, -9, 2.8, C.paper, 0.9);
  ctx.restore();
  // nahe Flügel
  wing(100, 16, ph, 2, -18, 0.55, 11);
  wing(70, 12, ph + 0.2, -4, -18, 0.55, 12);
  ctx.restore();
}

/* ================================================================== Rähmchen mit Wabe (Sechsecke)
   Ursprung: Mitte oben (cx, yTop). Rahmen RW×RH, Wabenfläche RIN, Zellradius RR */
const RW = 190, RH = 250, RR = 14, RIN = { x: 14, y: 26, w: 162, h: 214 };
const combCache = new Map();
function combGrid(w, h, r) {
  const key = w + '|' + h + '|' + r;
  let g = combCache.get(key);
  if (g) return g;
  g = [];
  const dx = Math.sqrt(3) * r, dy = 1.5 * r;
  for (let j = 0; ; j++) {
    const y = r + j * dy;
    if (y + r > h) break;
    const off = j % 2 ? dx / 2 : 0;
    for (let i = 0; ; i++) {
      const x = dx / 2 + off + i * dx;
      if (x + dx / 2 > w + 0.01) break;
      g.push({ i, j, x, y });
    }
  }
  combCache.set(key, g);
  return g;
}
// Mittelpunkt einer Zelle in Weltkoordinaten (Rahmen cx, yTop)
function zellPos(cx, yTop, i, j) {
  const c = combGrid(RIN.w, RIN.h, RR).find(q => q.i === i && q.j === j);
  return c ? [cx - RW / 2 + RIN.x + c.x, yTop + RIN.y + c.y] : [cx, yTop + RH / 2];
}
// Inhalt einer Zelle: 'leer' 'ei' 'larve' 'brutdeckel' 'honig' 'honigdeckel' 'pollen'
function zelleArt(kind, c, fid, o) {
  const h = hash(c.i, c.j, fid * 7 + 3), h2 = hash(c.i * 3 + 1, c.j * 5 + 2, fid + 11);
  const gw = RIN.w, gh = RIN.h;
  if (kind === 'leer') return 'leer';
  if (kind === 'honig') {
    if (h2 > (o.honigProg ?? 1) * 1.0) return 'leer';
    return h < (o.deckel ?? 0.55) ? 'honigdeckel' : 'honig';
  }
  if (kind === 'wachs') return 'leer';
  // Brutwabe: Brutnest in der Mitte, Pollenkranz, Honigbogen oben
  const dx = (c.x - gw * 0.5) / (gw * 0.47), dy = (c.y - gh * 0.58) / (gh * 0.4), d = Math.hypot(dx, dy);
  if (c.y < gh * 0.15) return h2 < (o.honigProg ?? 1) ? (h < 0.5 ? 'honigdeckel' : 'honig') : 'leer';
  if (d < 1) {
    if (h2 > (o.prog ?? 1)) return 'leer';
    if (d < 0.4) return h < 0.7 ? 'brutdeckel' : 'larve';
    if (d < 0.75) return h < 0.4 ? 'larve' : h < 0.6 ? 'ei' : 'brutdeckel';
    return h < 0.5 ? 'ei' : h < 0.75 ? 'larve' : 'leer';
  }
  if (c.y > gh * 0.8 || (d < 1.25 && h < 0.4)) return h2 < (o.pollenProg ?? 1) ? 'pollen' : 'leer';
  return h < 0.35 && h2 < (o.honigProg ?? 1) ? 'honig' : 'leer';
}
/* Wabenfläche zeichnen. gx, gy = linke obere Ecke der Fläche. o: kind, fid, prog, honigProg, deckel, reif (0..1 Nektar→Honig),
   ueberschreibe(c, art) → art, alt (c)→0..1 Deckelfortschritt */
function zellen(ctx, gx, gy, gw, gh, o = {}) {
  const cells = combGrid(gw, gh, RR), r = RR - 0.8;
  const cat = { leer: new Path2D(), honig: new Path2D(), honigdeckel: new Path2D(), brutdeckel: new Path2D(), pollen: new Path2D(), larve: new Path2D(), ei: new Path2D() };
  const edges = new Path2D(), dots = [];
  for (const c of cells) {
    let a = zelleArt(o.kind || 'brut', c, o.fid || 0, o);
    if (o.ueberschreibe) a = o.ueberschreibe(c, a) || a;
    const px = gx + c.x, py = gy + c.y;
    const catName = a === 'ei' || a === 'larve' ? 'leer' : a;
    hexPath(cat[a === 'ei' || a === 'larve' ? 'leer' : a], px, py, r);
    hexPath(edges, px, py, RR);
    if (a === 'ei' || a === 'larve' || a === 'honig' || a === 'honigdeckel' || a === 'brutdeckel') dots.push([a, px, py, c]);
  }
  ctx.save();
  const reif = o.reif ?? 1;
  const honigFarbe = mix(NEKTAR, HONIG, reif);
  ctx.fillStyle = shade(WACHS, -0.08); ctx.fill(cat.leer);
  ctx.fillStyle = mix(C.coral, C.mustard, 0.5); ctx.fill(cat.pollen);
  ctx.fillStyle = honigFarbe; ctx.fill(cat.honig);
  ctx.fillStyle = mix(C.cream, C.mustardL, 0.55); ctx.fill(cat.honigdeckel);
  ctx.fillStyle = BRUTDECKEL; ctx.fill(cat.brutdeckel);
  // Kanten
  ctx.strokeStyle = WACHS_D; ctx.lineWidth = 2.2; ctx.lineJoin = 'round';
  ctx.globalAlpha *= 0.85; ctx.stroke(edges); ctx.globalAlpha /= 0.85;
  // Zelldetails
  for (const [a, px, py] of dots) {
    if (a === 'ei') { ctx.fillStyle = C.paper; ctx.beginPath(); ctx.ellipse(px, py + 2, 2.8, 6.5, 0, 0, TAU); ctx.fill(); }
    else if (a === 'larve') {
      ctx.fillStyle = C.paper; ctx.beginPath(); ctx.arc(px, py + 1, r * 0.62, 0, TAU); ctx.fill();
      ctx.strokeStyle = C.creamD; ctx.lineWidth = 1.8; ctx.beginPath(); ctx.arc(px, py + 1, r * 0.34, 0.4, 4.6); ctx.stroke();
    } else if (a === 'honig') { ctx.fillStyle = mix(honigFarbe, C.paper, 0.5); ctx.beginPath(); ctx.arc(px - 3.5, py - 3.5, 2.6, 0, TAU); ctx.fill(); }
    else if (a === 'honigdeckel') { ctx.strokeStyle = shade(C.creamD, -0.1); ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(px, py, r * 0.55, 0, TAU); ctx.stroke(); }
    else if (a === 'brutdeckel') { ctx.fillStyle = shade(BRUTDECKEL, -0.14); ctx.beginPath(); ctx.arc(px, py, 2.4, 0, TAU); ctx.fill(); }
  }
  ctx.restore();
}
function rahmen(ctx, cx, yTop, o = {}) {
  const id = o.id ?? 7100, x0 = cx - RW / 2;
  P(ctx, rectPts(x0, yTop, RW, RH), C.woodL, { id, shadow: o.shadow ?? 0.7 });
  P(ctx, rectPts(x0 + RIN.x, yTop + RIN.y, RIN.w, RIN.h), WACHS, { id: id + 1, shadow: 0, outline: false, tex: false });
  ctx.save();
  const sc = curScale(ctx), j = [hs(id, G.boil, 3) * 0.7 / sc, hs(id, G.boil, 4) * 0.7 / sc];
  ctx.translate(j[0], j[1]);
  zellen(ctx, x0 + RIN.x, yTop + RIN.y, RIN.w, RIN.h, Object.assign({ fid: id }, o));
  ctx.restore();
  // Gouache-Hauch über der Wabe
  ctx.save();
  const pat = pattern(ctx, 'g', TEX.gouache);
  pat.setTransform(new DOMMatrix().translate(hash(id) * 200, 0).scale(1.2 / sc, 1.2 / sc));
  ctx.globalAlpha = 0.5; ctx.fillStyle = pat; ctx.fillRect(x0 + RIN.x, yTop + RIN.y, RIN.w, RIN.h);
  ctx.restore();
  // Oberträger mit Ohren
  P(ctx, rectPts(x0 - 16, yTop - 6, RW + 32, 22), C.wood, { id: id + 2, shadow: 0.5 });
  strich(ctx, [[x0 - 8, yTop + 3], [x0 + RW + 8, yTop + 3]], C.woodD, 2.6, 0.7);
  strich(ctx, [[x0 + 4, yTop + 10], [x0 + RW - 4, yTop + 10]], C.woodD, 2, 0.5);
}

/* ================================================================== Bienenkasten (aufklappbare Vorderwand)
   Ursprung = Mitte unten (Boden), s = 1: Breite ~1040, Höhe ~735. Zargen: unten = Brutraum, oben = Honigraum.
   o: offenU, offenO (0..1 Vorderwand klappt nach unten), innenU(ctx), innenO(ctx), schnee (0..1), dachHoch (px), id, fluglochSicht */
const KASTEN = { zU: [-370, -100], zO: [-640, -370], flug: [-250, -79], dachTop: -735 };
function kasten(ctx, x, yb, s, o = {}) {
  const id = o.id ?? 7000;
  ctx.save(); ctx.translate(x, yb); ctx.scale(s, s);
  // Beine und Boden
  P(ctx, rectPts(-380, -62, 56, 62), C.woodD, { id, shadow: 0.6 });
  P(ctx, rectPts(324, -62, 56, 62), C.woodD, { id: id + 1, shadow: 0.6 });
  P(ctx, rectPts(-486, -104, 972, 44), C.wood, { id: id + 2, shadow: 0.9 });
  strich(ctx, [[-470, -76], [470, -76]], C.woodD, 2.4, 0.5);
  // Flugloch (Schlitz) und Anflugbrett
  P(ctx, [[-340, -64], [-150, -64], [-124, -44], [-366, -44]], C.woodL, { id: id + 3, shadow: 0.7 });
  P(ctx, rectPts(-340, -98, 180, 30), C.woodD, { id: id + 4, shadow: 0, outline: false });
  P(ctx, rectPts(-334, -93, 168, 20), o.fluglochSicht ? C.sky : C.ink, { id: id + 5, shadow: 0, outline: false, tex: false });
  if (o.fluglochSicht) {
    flat(ctx, rectPts(-334, -81, 168, 8), C.green, 0.9);
    dot(ctx, -250, -85, 6, C.mustard, 0.9);
  }
  // Zargen
  const zarge = (yT, yB, off, col, colD, innen, k) => {
    P(ctx, rectPts(-462, yT, 924, yB - yT), shade(C.woodD, -0.25), { id: id + 10 + k, shadow: 0.9 });
    if (innen) { ctx.save(); pathPts(ctx, rectPts(-462, yT, 924, yB - yT)); ctx.clip(); innen(ctx, yT, yB); ctx.restore(); }
    const f = 1 - 0.88 * off;
    ctx.save(); ctx.translate(0, yB); ctx.scale(1, f); ctx.translate(0, -yB);
    P(ctx, rectPts(-474, yT, 948, yB - yT), col, { id: id + 20 + k, shadow: off > 0.05 ? 1.1 : 0.9 });
    P(ctx, rectPts(-474, yT, 948, 24), colD, { id: id + 30 + k, shadow: 0, outline: false });
    P(ctx, rectPts(-474, yB - 24, 948, 24), colD, { id: id + 40 + k, shadow: 0, outline: false });
    for (let m = 1; m < 5; m++) strich(ctx, [[-450 + m * 20, yT + 60 + m * 10], [-60 + m * 150, yT + 66 + m * 8]], colD, 3, 0.35);
    P(ctx, rrectPts(-120, (yT + yB) / 2 - 14, 240, 28, 14), colD, { id: id + 50 + k, shadow: 0.3, outline: false });   // Griffleiste
    if (off > 0.05) flat(ctx, rectPts(-474, yT, 948, yB - yT), C.ink, off * 0.18);
    ctx.restore();
  };
  zarge(KASTEN.zU[0], KASTEN.zU[1], o.offenU || 0, o.farbeU ?? C.petrol, C.petrolD, o.innenU, 0);
  zarge(KASTEN.zO[0], KASTEN.zO[1], o.offenO || 0, o.farbeO ?? C.mustardL, C.mustard, o.innenO, 1);
  // Dach
  const dh = o.dachHoch || 0;
  ctx.save(); ctx.translate(0, -dh);
  P(ctx, [[-540, -642], [540, -642], [456, -736], [-456, -736]], C.coral, { id: id + 60, shadow: 1 });
  P(ctx, rectPts(-540, -656, 1080, 20), C.cream, { id: id + 61, shadow: 0.7 });
  for (let m = 0; m < 5; m++) strich(ctx, [[-500 + m * 8, -650 - m * 18], [500 - m * 8, -650 - m * 18]], C.coralD, 3, 0.45);
  ell(ctx, 0, -736, 22, 8, C.mustard, { id: id + 62, shadow: 0.4 });
  if ((o.schnee || 0) > 0) {
    const q = o.schnee;
    const top = [[-560, -640], [-472, -742 - 12 * q], [-300, -748 - 14 * q], [0, -752 - 18 * q], [300, -748 - 14 * q], [472, -742 - 12 * q], [560, -640]];
    const bot = []; for (let m = 8; m >= 0; m--) bot.push([-560 + m * 140, -640 + (m % 2 ? 26 : 6) * q + 5 * hs(id, m)]);
    P(ctx, top.concat(bot), C.paper, { id: id + 63, shadow: 0.9 });
    for (let m = 0; m < 5; m++) P(ctx, [[-420 + m * 210, -628], [-398 + m * 210, -628], [-409 + m * 210, -628 + (34 + 22 * (m % 3)) * q]], C.waterL, { id: id + 64 + m, shadow: 0.3, alpha: 0.9 });
  }
  ctx.restore();
  ctx.restore();
}
// Mittelpunkt des Flugloch-Schlitzes in Kastenkoordinaten
const FLUGLOCH = [-250, -83];

/* ================================================================== Zellen-Querschnitt (Karte, Bildschirm- oder Weltkoordinaten)
   Liegende Zelle (offene Seite rechts) mit Stufe: o.ei (0..1), o.larve (0..1), o.puppe (0..1), o.biene (0..1), o.deckel (0..1 schließt),
   o.futter (0..1), o.biss (0..1), o.rausch (0..1 Biene krabbelt heraus). Maße: Breite w, Höhe h */
function zellSchnitt(ctx, cx, cy, w, h, o = {}) {
  const id = o.id ?? 7600, x0 = cx - w / 2, y0 = cy - h / 2, wall = h * 0.12;
  ctx.save();
  // Wände (Wachs) mit Sechseck-Anschnitt
  P(ctx, rectPts(x0 - 10, y0 - wall, w + 20, h + 2 * wall), WACHS, { id, shadow: 1.1 });
  P(ctx, rectPts(x0, y0, w, h), mix(C.cream, C.mustardL, 0.3), { id: id + 1, shadow: 0, outline: false });
  flat(ctx, rectPts(x0, y0, w, h * 0.14), WACHS_D, 0.28);
  flat(ctx, rectPts(x0, y0 + h * 0.86, w, h * 0.14), WACHS_D, 0.28);
  // Öffnung der Zelle rechts: Sechseck-Rahmen
  P(ctx, [[x0 + w + 6, y0 - wall], [x0 + w + 30, y0 + h * 0.22], [x0 + w + 30, y0 + h * 0.78], [x0 + w + 6, y0 + h + wall], [x0 + w - 2, y0 + h], [x0 + w - 2, y0]], WACHS, { id: id + 11, shadow: 0.6 });
  // Rückwand der Zelle (Zellboden: dreieckig angedeutet)
  P(ctx, [[x0, y0], [x0 + 38, y0 + h * 0.12], [x0 + 38, y0 + h * 0.88], [x0, y0 + h]], WACHS_D, { id: id + 2, shadow: 0, outline: false, alpha: 0.7 });
  strich(ctx, [[x0 - 10, y0], [x0 + w + 10, y0]], WACHS_D, 4, 0.9);
  strich(ctx, [[x0 - 10, y0 + h], [x0 + w + 10, y0 + h]], WACHS_D, 4, 0.9);
  const by = cy + h * 0.14;   // Körperachse (etwas unterhalb der Mitte)
  const L = w;
  // Futtersaft
  if ((o.futter || 0) > 0 || (o.larve || 0) > 0.2)
    P(ctx, ellPts(x0 + 120, y0 + h * 0.86, 100, h * 0.1 * (0.6 + (o.futter || 0)), 16), C.paper, { id: id + 3, shadow: 0, outline: false, alpha: 0.9 });
  // Ei
  const ei = o.ei ?? 0, la = o.larve ?? 0, pu = o.puppe ?? 0, bi = o.biene ?? 0;
  if (ei > 0 && la < 1) {
    const sz = (1 - la) * ei;
    P(ctx, ellPts(x0 + 110, by + h * 0.06, 72 * sz + 1, 24 * sz + 1, 16), C.paper, { id: id + 4, shadow: 0.8 });
    strich(ctx, [[x0 + 62, by + h * 0.06 - 8], [x0 + 150, by + h * 0.06 - 10]], C.creamD, 3, 0.8 * sz);
  }
  // Larve: C-förmig, weiß, gegliedert
  if (la > 0 && pu < 1) {
    const g = 0.55 + 0.45 * Math.min(1, la) + 0.35 * (o.futter || 0), a = 1 - pu;
    ctx.save(); ctx.translate(x0 + 50, by); ctx.scale(1.3, 1.3); ctx.translate(-(x0 + 50), -by);
    const arc = smooth([[x0 + 60, by - h * 0.12 * g], [x0 + 120 + 50 * g, by - h * 0.22 * g], [x0 + 210 + 70 * g, by - h * 0.08 * g], [x0 + 230 + 60 * g, by + h * 0.12 * g], [x0 + 150 + 40 * g, by + h * 0.22 * g], [x0 + 80, by + h * 0.18 * g]], 6);
    ctx.save(); ctx.globalAlpha *= a;
    const th = h * 0.2 * g;
    P(ctx, polyBand(arc, th), C.paper, { id: id + 5, shadow: 0.7 });
    for (let k = 1; k < 9; k++) { const pt = polyAt(arc, polyLen(arc), polyLen(arc).slice(-1)[0] * k / 9); strich(ctx, [[pt[0], pt[1] - th * 0.4], [pt[0], pt[1] + th * 0.4]], C.creamD, 2.4, 0.8); }
    dot(ctx, arc[0][0] + 6, arc[0][1], 3, C.ink);   // Auge/Kopf
    ctx.restore();
    ctx.restore();
  }
  // Puppe → junge Biene (liegt in Achsenrichtung, Kopf zur Öffnung)
  if (pu > 0) {
    ctx.save(); ctx.translate(o.dx || 0, 0); ctx.translate(x0 + 80, by); ctx.scale(1.3, 1.3); ctx.translate(-(x0 + 80), -by);
    const pt = Math.min(1, pu), bf = bi, a = 1;
    const px = x0 + 80, ph = h * 0.34, sc = 1;
    const kc = mix(C.cream, C.mustardL, bf), bc = mix(C.cream, C.mustard, bf), tc = mix(C.cream, C.mustardD, bf);
    // Hinterleib, Brust, Kopf
    P(ctx, ellPts(px + 96, by, 108, ph * 0.5, 18), bc, { id: id + 6, shadow: 0.6 });
    if (bf > 0.2) for (const bx of [px + 56, px + 96, px + 134]) strich(ctx, [[bx, by - ph * 0.4], [bx, by + ph * 0.4]], C.ink, 9 * bf, bf);
    P(ctx, ellPts(px + 228, by, 52, ph * 0.46, 14), tc, { id: id + 7, shadow: 0.6 });
    P(ctx, ellPts(px + 296, by, 36, ph * 0.4, 14), mix(kc, C.woodD, bf), { id: id + 8, shadow: 0.6 });
    P(ctx, ellPts(px + 304, by - ph * 0.14, 15 * (0.4 + bf * 0.6), 18 * (0.4 + bf * 0.6), 10), mix(C.creamD, C.ink, bf), { id: id + 9, shadow: 0, outline: false });
    // Beine (gefaltet) und Flügelanlage
    for (const k of [0, 1, 2]) strich(ctx, [[px + 210 + k * 22, by + ph * 0.36], [px + 226 + k * 20, by + ph * 0.5], [px + 214 + k * 22, by + ph * 0.58]], mix(C.creamD, C.ink, bf), 4.2);
    P(ctx, ellPts(px + 200, by - ph * 0.42, 52, 12, 12), C.waterL, { id: id + 10, shadow: 0, alpha: 0.4 + 0.3 * bf });
    // Fühler
    strich(ctx, [[px + 320, by - ph * 0.2], [px + 352, by - ph * 0.4], [px + 372, by - ph * 0.3]], mix(C.creamD, C.ink, bf), 3.4);
    ctx.restore();
  }
  ctx.restore();
}
// Band entlang einer Polylinie (für Larve)
function polyBand(pts, th) {
  const A = [], B = [];
  for (let i = 0; i < pts.length; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[Math.min(pts.length - 1, i + 1)];
    const dx = p1[0] - p0[0], dy = p1[1] - p0[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    const k = Math.sin(Math.PI * (0.15 + 0.7 * i / (pts.length - 1)));
    A.push([pts[i][0] + nx * th * k * 0.5, pts[i][1] + ny * th * k * 0.5]);
    B.unshift([pts[i][0] - nx * th * k * 0.5, pts[i][1] - ny * th * k * 0.5]);
  }
  return A.concat(B);
}

/* ================================================================== Imker (Person im weißen Anzug, Hut mit Schleier)
   o: wie person(); Standard-Look eingebaut. holds(ctx,hx,hy,ha) für Gegenstände in der rechten Hand */
const LOOK_IMKER = { coat: C.paper, sleeve: C.paper, pants: C.cream, hat: 'wide', hatColor: C.paper, hair: '#5A3A22', shirt: C.creamD, shoes: C.woodD, buttons: C.kraft };
function imker(ctx, x, y, s, o = {}) {
  person(ctx, x, y, s, Object.assign({ id: 6100 }, LOOK_IMKER, o));
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (o.flip ? -1 : 1), s);
  const id = (o.id ?? 6100) + 90;
  P(ctx, [[-30, -190], [30, -190], [32, -168], [24, -146], [-24, -146], [-32, -168]], C.paper, { id, shadow: 0, outline: false, alpha: 0.34 });
  for (let k = -2; k <= 2; k++) strich(ctx, [[k * 11, -190], [k * 9, -148]], C.greyL, 1.6, 0.7);
  for (let k = 0; k < 3; k++) strich(ctx, [[-30 + k * 3, -183 + k * 12], [30 - k * 3, -183 + k * 12]], C.greyL, 1.4, 0.6);
  // Handschuhe
  ctx.restore();
}
// Smoker (Rauchgerät) für die Hand des Imkers
function smoker(ctx, hx, hy, a) {
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(a - Math.PI / 2);
  P(ctx, rrectPts(-8, -6, 20, 32, 5), C.greyD, { id: 6300, shadow: 0.3 });
  P(ctx, [[-4, -6], [8, -6], [18, -18], [12, -22]], C.greyD, { id: 6301, shadow: 0.2 });
  P(ctx, rectPts(-20, 8, 12, 18), C.kraftD, { id: 6302, shadow: 0.2 });
  ctx.restore();
}

/* ================================================================== Pflanzen, Sonne, Gläser, Kerze, Apfel */
function blume(ctx, x, yb, s, col, id, o = {}) {
  const h = (o.h ?? 90) * s, sway = Math.sin(G.t * 1.7 + id) * 2 * s;
  const kx = x + sway, ky = yb - h;
  strich(ctx, [[x, yb], [x + sway * 0.4, yb - h * 0.5], [kx, ky]], C.greenD, 5 * s);
  P(ctx, tf(ellPts(0, 0, 18 * s, 7 * s, 10), x - 14 * s, yb - h * 0.34, 1, -0.5), C.green, { id: id + 1, shadow: 0.2, outline: false });
  const n = o.n ?? 7, pr = (o.r ?? 24) * s;
  for (let k = 0; k < n; k++) {
    const a = k / n * TAU + hs(id, 1) * 0.3;
    P(ctx, tf(ellPts(0, 0, pr * 0.8, pr * 0.46, 10), kx + Math.cos(a) * pr * 0.78, ky + Math.sin(a) * pr * 0.78, 1, a), col, { id: id + 10 + k, shadow: 0.25 });
  }
  ell(ctx, kx, ky, pr * 0.45, pr * 0.45, o.mitte ?? C.mustard, { id: id + 30, shadow: 0.3 });
  return [kx, ky];
}
function gras(ctx, x, yb, s, id, col = C.greenD) {
  for (let k = -2; k <= 2; k++) P(ctx, [[x + k * 7 * s - 4 * s, yb], [x + k * 9 * s, yb - (34 + (k % 2 ? 10 : 0)) * s], [x + k * 7 * s + 4 * s, yb]], col, { id: id + k + 3, shadow: 0.15, outline: false });
}
function sonne(ctx, x, y, r, id, t = 0) {
  for (let k = 0; k < 14; k++) {
    const a = k / 14 * TAU + t * 0.1;
    strich(ctx, [[x + Math.cos(a) * r * 1.25, y + Math.sin(a) * r * 1.25], [x + Math.cos(a) * r * (k % 2 ? 1.6 : 1.8), y + Math.sin(a) * r * (k % 2 ? 1.6 : 1.8)]], C.mustard, r * 0.1);
  }
  ell(ctx, x, y, r, r, C.mustardL, { id, shadow: 0.5 });
  ell(ctx, x, y, r * 0.72, r * 0.72, C.mustard, { id: id + 1, shadow: 0, outline: false });
}
// Honigglas (Fuß bei yb), fuell 0..1
function honigglas(ctx, x, yb, s, id, fuell = 1, o = {}) {
  const w = 76 * s, h = 96 * s;
  P(ctx, rrectPts(x - w / 2, yb - h, w, h, 14 * s), C.paper, { id, shadow: 0.9, alpha: 0.7 });
  if (fuell > 0) {
    ctx.save(); pathPts(ctx, rrectPts(x - w / 2 + 4 * s, yb - h + 6 * s, w - 8 * s, h - 10 * s, 11 * s)); ctx.clip();
    ctx.fillStyle = HONIG; ctx.fillRect(x - w, yb - (h - 8 * s) * fuell, 2 * w, h);
    flat(ctx, rectPts(x - w / 2 + 12 * s, yb - h + 20 * s, 9 * s, (h - 36 * s) * fuell), C.mustardL, 0.6);
    ctx.restore();
  }
  P(ctx, rrectPts(x - w / 2 - 2 * s, yb - h - 14 * s, w + 4 * s, 20 * s, 6 * s), C.petrol, { id: id + 1, shadow: 0.6 });
  if (o.etikett !== false) { ell(ctx, x, yb - h * 0.42, 17 * s, 17 * s, C.paper, { id: id + 2, shadow: 0, alpha: 0.95 }); biene(ctx, x, yb - h * 0.42, 0.14 * s, { rot: -0.6, id: id + 3, lod: 2 }); }
}
function kerzeWachs(ctx, x, yb, s, id, an = 1) {
  P(ctx, rrectPts(x - 15 * s, yb - 120 * s, 30 * s, 120 * s, 6 * s), C.mustardL, { id, shadow: 0.8 });
  flat(ctx, rectPts(x - 9 * s, yb - 110 * s, 6 * s, 90 * s), C.paper, 0.45);
  strich(ctx, [[x, yb - 120 * s], [x + 2 * s, yb - 132 * s]], C.ink, 3.5 * s);
  P(ctx, [[x - 15 * s, yb - 112 * s], [x - 4 * s, yb - 100 * s], [x - 8 * s, yb - 108 * s]], C.mustard, { id: id + 1, shadow: 0, outline: false, alpha: 0.9 });
  if (an > 0) flamme(ctx, x, yb - 128 * s, 0.4 * s * an, id + 2, 0.25 * an);
}
function apfel(ctx, x, yb, s, id) {
  ell(ctx, x - 12 * s, yb - 30 * s, 28 * s, 30 * s, C.red, { id, shadow: 0.9 });
  ell(ctx, x + 12 * s, yb - 30 * s, 28 * s, 30 * s, shade(C.red, 0.08), { id: id + 1, shadow: 0 });
  strich(ctx, [[x, yb - 58 * s], [x + 4 * s, yb - 74 * s]], C.woodD, 5 * s);
  P(ctx, tf(ellPts(0, 0, 18 * s, 8 * s, 10), x + 20 * s, yb - 70 * s, 1, -0.4), C.green, { id: id + 2, shadow: 0.3 });
  dot(ctx, x - 18 * s, yb - 44 * s, 6 * s, C.paper, 0.45);
}
// Herz-Symbol (Papier)
function herz(ctx, x, y, s, id, a = 1) {
  const pts = smooth([[0, 18], [-22, 0], [-22, -14], [-10, -22], [0, -12], [10, -22], [22, -14], [22, 0]], 5, true);
  P(ctx, tf(pts, x, y, s), C.coral, { id, shadow: 0.5, alpha: a });
}

/* ================================================================== Piktogramme für Schilder (schild(…) in bausteine.js)  */
Object.assign(PIKTO, {
  krone(c, id) {
    P(c, [[-52, 30], [-58, -20], [-28, 4], [0, -36], [28, 4], [58, -20], [52, 30]], C.mustard, { id, shadow: 0.6 });
    P(c, rectPts(-52, 18, 104, 14), C.mustardD, { id: id + 1, shadow: 0, outline: false });
    for (const [px, py] of [[-58, -22], [0, -38], [58, -22]]) dot(c, px, py, 7, C.coral);
  },
  hammer(c, id) {
    P(c, tf(rrectPts(-6, -48, 12, 100, 5), -6, 4, 1, 0.5), C.woodL, { id, shadow: 0.5 });
    P(c, tf(rrectPts(-30, -12, 60, 24, 6), 20, -34, 1, 0.5), C.greyD, { id: id + 1, shadow: 0.6 });
    P(c, tf(rrectPts(-5, -40, 10, 80, 4), -34, 6, 1, -0.55), C.greyL, { id: id + 2, shadow: 0.4 });
  },
  fluegel(c, id) {
    P(c, tf(ellPts(0, 0, 54, 22, 16), -4, -22, 1, -0.45), C.waterL, { id, shadow: 0.5, alpha: 0.85 });
    P(c, tf(ellPts(0, 0, 54, 22, 16), 6, 18, 1, 0.45), C.waterL, { id: id + 1, shadow: 0.5, alpha: 0.85 });
    strich(c, [[-40, -42], [40, 8]], C.paper, 3); strich(c, [[-30, 40], [44, 0]], C.paper, 3);
    dot(c, 44, 2, 8, C.mustardD);
  },
  besen(c, id) {
    strich(c, [[30, -52], [-18, 22]], C.woodL, 9);
    P(c, [[-8, 12], [-52, 56], [-34, 62], [-8, 52], [10, 60], [24, 36]], C.mustardD, { id, shadow: 0.5 });
    for (let k = 0; k < 4; k++) strich(c, [[-14 + k * 7, 30], [-34 + k * 12, 56]], C.woodD, 2, 0.6);
  },
  loeffel(c, id) {
    strich(c, [[-42, -40], [30, 30]], C.woodL, 10);
    P(c, ellPts(36, 34, 24, 17, 12), C.woodL, { id, shadow: 0.5 });
    P(c, ellPts(-30, -26, 12, 15, 10), C.paper, { id: id + 1, shadow: 0.3 });
  },
  kelle(c, id) {
    P(c, tf([[0, -42], [30, 10], [0, 36], [-30, 10]], -6, 6, 1, 0.5), C.greyD, { id, shadow: 0.6 });
    strich(c, [[12, -8], [52, -46]], C.woodL, 10);
    P(c, tf(sechseck(0, 0, 14), -2, 18, 1), C.mustardL, { id: id + 1, shadow: 0.3 });
  },
  wache(c, id) {
    P(c, [[-44, -42], [44, -42], [44, 8], [0, 52], [-44, 8]], C.petrol, { id, shadow: 0.7 });
    P(c, [[-34, -32], [34, -32], [34, 4], [0, 40], [-34, 4]], C.petrolL, { id: id + 1, shadow: 0, outline: false });
    biene(c, 0, 0, 0.3, { rot: -Math.PI / 2, id: id + 2, lod: 1 });
  },
});
// Schild-Anker aus Weltkoordinaten (camPt) mit Kartengröße s, Hilfsfunktion für die Szenen
function schildW(ctx, cam, wx, wy, s, typ, p, id, ox = 0, oy = -150) {
  const [sx, sy] = camPt(cam, wx, wy);
  schild(ctx, sx, sy, s, typ, p, id, ox, oy);
}
