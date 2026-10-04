/* Zusätzliche Bausteine (wachsen mit jedem Projekt). Ursprung = Fußpunkt, feste ids, Farben aus C.
   Naturwissenschaft (aus „Wie Lavoisier den Sauerstoff erklärte“): flamme, kerze, schale, waage, gewicht, holz, metall,
   fragezeichen, glas, kolben, brenner, linse, gelehrter (+LOOK_PRIESTLEY/LOOK_LAVOISIER), kugel (Teilchen).
   Allgemein: hervorheben (Scheinwerfer + roter Pfeil), camPt (Weltpunkt → Bildschirmpunkt für Zoom-Übergänge).
   Biologie (aus „Die Zelle als Fabrik“): helix (DNA), mito, chloroplast, lyso, vesikel, knaeuel (Protein), zucker, blitz,
   bauplan, zeige (Hervorheben bei Zoom), schild + PIKTO (Vergleichs-Schilder ohne Schrift).
   Physik (aus „Der Streuversuch von Rutherford“): teilchen (+/−), elektron, plusZ, minusZ, lichtblitz;
   Hilfen: lerp2, fenster (Sichtbarkeitsfenster), tri (Hin-und-her-Prallen), bahnBis (sich zeichnende Flugbahn). */
'use strict';

// Flamme: Ursprung = Fußpunkt, Höhe ≈ 130·s. hell 0..1 → Lichtkreis
const FLAMME_PTS = smooth([[0, 0], [-26, -18], [-30, -52], [-12, -92], [4, -130], [14, -86], [30, -50], [24, -16]], 5, true);
function flamme(ctx, x, yb, s, id, hell = 0) {
  if (s <= 0.01) return;
  if (hell > 0) halo(ctx, x, yb - 60 * s, 170 * s * (0.6 + hell * 0.6), hell);
  const w = hs(id, G.boil, 5) * 0.09;
  P(ctx, tf(FLAMME_PTS, x, yb, s, w), C.coral, { id, shadow: 0.5 });
  P(ctx, tf(FLAMME_PTS, x, yb, s * 0.72, -w), C.mustard, { id: id + 1, shadow: 0 });
  P(ctx, tf(FLAMME_PTS, x, yb, s * 0.42, w * 0.5), C.mustardL, { id: id + 2, shadow: 0 });
}

// Kerze auf Halter; fl = Flammengröße, hell = Leuchten
function kerze(ctx, x, yb, s, id, fl = 1, hell = 0) {
  P(ctx, rectPts(x - 16 * s, yb - 118 * s, 32 * s, 110 * s), C.coralL, { id, shadow: 0.7 });
  crayon(ctx, [[x, yb - 118 * s], [x + 2 * s, yb - 130 * s]], 1, C.ink, 3.5 * s, { id: id + 1 });
  P(ctx, [[x - 42 * s, yb], [x + 42 * s, yb], [x + 30 * s, yb - 12 * s], [x - 30 * s, yb - 12 * s]], C.mustardD, { id: id + 2, shadow: 0.6 });
  if (fl > 0) flamme(ctx, x, yb - 124 * s, 0.42 * s * fl, id + 3, hell);
}

// Waagschale (Rand bei y)
function schale(ctx, x, y, id, w = 160, col = C.mustardD) {
  P(ctx, arcPts(x, y, w / 2, 30, 0, Math.PI, 12), col, { id, shadow: 0.8 });
  crayon(ctx, [[x - w / 2, y], [x + w / 2, y]], 1, shade(col, -0.25), 4, { id: id + 1 });
}

/* Balkenwaage: Drehpunkt (x,y), Fuß bei yb, Balken ±L, Schalen hängen `hang` tiefer.
   ang > 0: linke Seite unten. inhalt(i, px, py) zeichnet auf die Schale (Rand bei py). */
function waage(ctx, x, y, yb, L, hang, ang, id, inhalt, o = {}) {
  const col = o.col ?? C.mustardD, colL = o.colL ?? C.mustard;
  P(ctx, [[x - 120, yb], [x + 120, yb], [x + 76, yb - 36], [x - 76, yb - 36]], C.woodD, { id, shadow: 1 });
  P(ctx, rectPts(x - 13, y, 26, yb - 36 - y), col, { id: id + 1, shadow: 0.8 });
  // Skala über dem Drehpunkt
  P(ctx, [...arcPts(x, y, 120, 120, -Math.PI / 2 - 0.34, -Math.PI / 2 + 0.34, 8), ...arcPts(x, y, 96, 96, -Math.PI / 2 + 0.34, -Math.PI / 2 - 0.34, 8)], C.paper, { id: id + 6, shadow: 0.5 });
  crayon(ctx, [[x, y - 124], [x, y - 92]], 1, C.red, 3, { id: id + 7 });
  const ends = [tf([[-L, 0]], x, y, 1, -ang)[0], tf([[L, 0]], x, y, 1, -ang)[0]];
  ends.forEach(([ex, ey], i) => {
    const py = ey + hang;
    crayon(ctx, [[ex, ey], [ex - 68, py]], 1, C.ink, 3, { id: id + 10 + i });
    crayon(ctx, [[ex, ey], [ex + 68, py]], 1, C.ink, 3, { id: id + 12 + i });
    schale(ctx, ex, py, id + 20 + i * 3, 170, col);
    if (inhalt) inhalt(i, ex, py);
  });
  P(ctx, tf(rrectPts(-L - 16, -11, 2 * L + 32, 22, 10), x, y, 1, -ang), colL, { id: id + 2, shadow: 1 });
  P(ctx, tf([[-8, 0], [8, 0], [0, -104]], x, y, 1, -ang), C.ink, { id: id + 3, shadow: 0.4, outline: false });
  ell(ctx, x, y, 17, 17, col, { id: id + 4, shadow: 0.6 });
  dot(ctx, x, y, 6, C.paper);
  return ends;
}

// Messinggewicht (Fuß bei yb)
function gewicht(ctx, x, yb, s, id) {
  P(ctx, rrectPts(x - 26 * s, yb - 44 * s, 52 * s, 44 * s, 8 * s), C.mustardD, { id, shadow: 0.7 });
  ell(ctx, x, yb - 50 * s, 12 * s, 9 * s, C.mustard, { id: id + 1, shadow: 0.4 });
  crayon(ctx, [[x - 18 * s, yb - 30 * s], [x + 18 * s, yb - 30 * s]], 1, C.mustardL, 3 * s, { id: id + 2, alpha: 0.7 });
}

// Holzscheit (rest 0..1) und Aschehaufen (asche 0..1)
function holz(ctx, x, yb, rest, asche, id) {
  if (asche > 0) P(ctx, arcPts(x, yb, 62 * asche, 30 * asche, Math.PI, TAU, 12), C.grey, { id: id + 5, shadow: 0.6 });
  if (rest <= 0.02) return;
  ctx.save(); ctx.translate(x, yb); ctx.scale(0.35 + 0.65 * rest, rest); ctx.translate(-x, -yb);
  P(ctx, rrectPts(x - 64, yb - 40, 128, 40, 18), C.wood, { id, shadow: 0.7 });
  P(ctx, tf(rrectPts(-50, -20, 128, 36, 16), x, yb - 44, 1, -0.12), C.woodL, { id: id + 1, shadow: 0.7 });
  ell(ctx, x + 58, yb - 20, 12, 18, C.kraftL, { id: id + 2, shadow: 0 });
  crayon(ctx, [[x - 50, yb - 22], [x + 30, yb - 24]], 1, C.woodD, 3, { id: id + 3 });
  ctx.restore();
}

// Metallstück (rest 0..1) → grauweißes Pulver (pulver 0..1)
function metall(ctx, x, yb, s, rest, pulver, id, glut = 0) {
  if (glut > 0) halo(ctx, x, yb - 20 * s, 90 * s, glut * 0.8, '240,120,80');
  if (pulver > 0) P(ctx, arcPts(x, yb, 58 * s * (0.5 + 0.5 * pulver), 34 * s * pulver, Math.PI, TAU, 12), C.greyL, { id: id + 3, shadow: 0.6 });
  if (rest <= 0.02) return;
  const h = 40 * s * rest;
  P(ctx, rectPts(x - 44 * s, yb - h, 88 * s, h), glut > 0.3 ? mix(C.greyD, C.coralD, (glut - 0.3) * 0.8) : C.greyD, { id, shadow: 0.7 });
  crayon(ctx, [[x - 34 * s, yb - h + 8 * s], [x + 20 * s, yb - h + 8 * s]], 1, C.greyL, 3 * s, { id: id + 1, alpha: 0.8 });
}

// großes rotes Fragezeichen (Symbol) – zeichnet sich bis prog
function fragezeichen(ctx, x, y, s, prog, id) {
  const pts = smooth([[-40, -58], [-30, -94], [0, -110], [36, -94], [40, -58], [10, -34], [0, -10], [0, 14]].map(([a, b]) => [x + a * s, y + b * s]), 6);
  const tip = crayon(ctx, pts, prog, C.red, 14 * s, { id });
  if (prog >= 1) ell(ctx, x, y + 50 * s, 12 * s, 12 * s, C.red, { id: id + 1, shadow: 0.5 });
  return tip;
}

// Glas: halbtransparente Papierform + weiße Kontur + Glanzstrich
function glas(ctx, pts, id, a = 0.45) {
  P(ctx, pts, C.waterL, { id, shadow: 0.25, alpha: a });
}
// Rundkolben mit Korken. Fuß bei yb. inhalt(ctx, xBoden, yBoden, s) wird hinter das Glas gezeichnet.
function kolben(ctx, x, yb, s, id, inhalt, korken = true) {
  const r = 50 * s, cy = yb - r;
  if (inhalt) inhalt(ctx, x, yb - 6 * s, s);
  glas(ctx, rectPts(x - 12 * s, cy - r - 62 * s, 24 * s, 70 * s), id + 1, 0.5);
  glas(ctx, ellPts(x, cy, r, r, 26), id, 0.4);
  crayon(ctx, arcPts(x, cy, r * 0.72, r * 0.72, Math.PI * 1.15, Math.PI * 1.45, 6), 1, C.paper, 4 * s, { id: id + 3, alpha: 0.9 });
  if (korken) P(ctx, rectPts(x - 14 * s, cy - r - 78 * s, 28 * s, 20 * s), C.kraftD, { id: id + 2, shadow: 0.5 });
}

// Öllampe/Brenner (Fuß bei yb); an 0..1
function brenner(ctx, x, yb, s, an, id) {
  P(ctx, [[x - 50 * s, yb], [x + 50 * s, yb], [x + 30 * s, yb - 18 * s], [x - 30 * s, yb - 18 * s]], C.mustardD, { id, shadow: 0.8 });
  ell(ctx, x, yb - 40 * s, 34 * s, 26 * s, C.mustard, { id: id + 1, shadow: 0.6 });
  P(ctx, rectPts(x - 6 * s, yb - 74 * s, 12 * s, 12 * s), C.greyD, { id: id + 2, shadow: 0 });
  if (an > 0) flamme(ctx, x, yb - 72 * s, 0.55 * s * an, id + 3, an * 0.6);
}

// Brennglas auf Holzständer, Linsenmitte (x,y), Fuß bei yb
function linse(ctx, x, y, yb, id) {
  P(ctx, rectPts(x - 7, y + 70, 14, yb - y - 70), C.woodD, { id, shadow: 0.6 });
  P(ctx, ellPts(x, yb - 4, 56, 14), C.woodD, { id: id + 1, shadow: 0.8 });
  ell(ctx, x, y, 40, 90, C.mustardD, { id: id + 2, shadow: 0.9 });
  ell(ctx, x, y, 30, 78, C.waterL, { id: id + 3, shadow: 0 });
  crayon(ctx, arcPts(x, y, 18, 56, Math.PI * 1.1, Math.PI * 1.45, 6), 1, C.paper, 5, { id: id + 4 });
}

// Gelehrter des 18. Jh. (Perücke mit seitlichen Locken)
const LOOK_PRIESTLEY = { coat: C.petrol, sleeve: C.petrol, pants: C.kraftD, hat: 'none', hair: C.greyL, shirt: C.paper, buttons: C.mustard, long: true };
const LOOK_LAVOISIER = { coat: C.navy, sleeve: C.navy, pants: C.navy, hat: 'none', hair: C.paper, shirt: C.paper, buttons: C.mustard, long: true };
function gelehrter(ctx, x, y, s, look, extra, id) {
  person(ctx, x, y, s, Object.assign({ id }, look, extra));
  for (const side of [-1, 1]) {
    ell(ctx, x + side * 23 * s, y - 176 * s, 7 * s, 8 * s, look.hair, { id: id + 70 + (side > 0 ? 1 : 0), shadow: 0.3 });
    ell(ctx, x + side * 23 * s, y - 162 * s, 6 * s, 7 * s, look.hair, { id: id + 72 + (side > 0 ? 1 : 0), shadow: 0.3 });
  }
}
// Scheinwerfer + roter Papierpfeil über dem Kopf
function hervorheben(ctx, x, yKopf, r, sp, id) {
  if (sp <= 0) return;
  spotlight(ctx, x, yKopf + r * 0.6, r, sp * 1.25);
  const py = yKopf - 40 - Math.sin(G.t * 4) * 6;
  pop(ctx, x, py, sp, () => P(ctx, [[x - 26, py - 38], [x + 26, py - 38], [x, py + 6]], C.red, { id, shadow: 1 }));
}

// Teilchen (Kugel mit Glanzpunkt)
function kugel(ctx, x, y, r, col, id, o = {}) {
  ell(ctx, x, y, r, r, col, { id, shadow: o.shadow ?? 0.5, alpha: o.alpha });
  dot(ctx, x - r * 0.35, y - r * 0.35, r * 0.22, C.paper, 0.8 * (o.alpha ?? 1));
}

// Bildschirmpunkt einer Welt mit Kamera (cx, cy, z), Tiefe 1
const camPt = ([cx, cy, z], x, y) => [W / 2 + (x - cx) * z, H / 2 + (y - cy) * z];

/* ================================================================== Biologie / Zelle (aus „Die Zelle als Fabrik“)
   Organellen biologisch geformt, Fabrik-Schilder ohne Schrift, DNA-Helix, Protein-Knäuel, Vesikel, Zucker, Energie-Blitz.
   Vollständiges Anwendungsbeispiel (eine Welt über 9 Szenen, Protein-Weg, Energieausfall):
   D:\KI Projekte\Lernanimationen\Aufbau einer Zelle\src\szenen.js – dort sind diese Funktionen noch lokal definiert;
   beim Übernehmen NICHT erneut deklarieren (const-Namen kollidieren sonst zwischen den Skripten). */
const AMINO = [C.coral, C.mustard, C.petrol, C.green, C.violet, C.coralD, C.waterD, C.mustardD, C.petrolL, C.rust, C.greenD, C.coralL];
const BLITZ = [[-10, -32], [12, -32], [2, -8], [16, -8], [-12, 32], [-2, 6], [-16, 6]];
const BAUPLAN = mix(C.crayonBlue, C.paper, 0.45);
const KNOT = Array.from({ length: 12 }, (_, k) => { const a = k * 2.4, r = 7.5 * Math.sqrt(k + 0.4); return [Math.cos(a) * r, Math.sin(a) * r]; });

// DNA als gewundene Doppelhelix (zwei Stränge + Sprossen) entlang eines Pfades (z. B. smooth([...], 8))
function helix(ctx, pts, amp, per, col, w, id, a = 1) {
  const L = polyLen(pts), tot = L[L.length - 1], n = Math.max(8, Math.round(tot / 5));
  const A = [], B = [];
  for (let i = 0; i <= n; i++) {
    const d = tot * i / n, p = polyAt(pts, L, d), q1 = polyAt(pts, L, Math.min(tot, d + 3)), q0 = polyAt(pts, L, Math.max(0, d - 3));
    const dx = q1[0] - q0[0], dy = q1[1] - q0[1], len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
    const sn = Math.sin(d / per * TAU) * amp;
    A.push([p[0] + nx * sn, p[1] + ny * sn]); B.push([p[0] - nx * sn, p[1] - ny * sn]);
  }
  for (let i = 2; i < n; i += 4) crayon(ctx, [A[i], B[i]], 1, col, w * 0.45, { id: id + 3 + i, alpha: 0.6 * a });
  crayon(ctx, A, 1, col, w, { id, alpha: a });
  crayon(ctx, B, 1, shade(col, 0.25), w, { id: id + 1, alpha: a });
}
// Hervorheben in einer gezoomten Welt: Scheinwerfer + roter Pfeil, der auf dem Bildschirm gleich groß bleibt (z = Kamerazoom)
function zeige(ctx, x, y, r, sp, id, z = 1, yTop = y - r) {
  if (sp <= 0) return;
  spotlight(ctx, x, y, r, sp * 1.25);
  const k = 1.15 / z, py = yTop - 16 * k - Math.sin(G.t * 4) * 6 * k;
  pop(ctx, x, py, sp, () => P(ctx, [[x - 26 * k, py - 40 * k], [x + 26 * k, py - 40 * k], [x, py + 4 * k]], C.red, { id, shadow: 1 }));
}
// Mitochondrium (Bohne mit Innenfalten), ~190×92 bei s = 1; o.alt → grau, zerknittert
function mito(ctx, x, y, rot, s, id, o = {}) {
  const col = o.alt ? mix(C.rust, C.grey, 0.6) : C.rust, inn = o.alt ? mix(C.coralL, C.greyL, 0.6) : C.coralL;
  P(ctx, tf(ellPts(0, 0, 95, 46, 26), x, y, s, rot), col, { id, shadow: 0.9, alpha: o.alpha });
  P(ctx, tf(ellPts(0, 0, 80, 33, 24), x, y, s, rot), inn, { id: id + 1, shadow: 0, outline: false, alpha: o.alpha });
  const z = []; for (let i = 0; i <= 8; i++) z.push([-66 + i * 16.5, (i % 2 ? 1 : -1) * 24]);
  crayon(ctx, tf(z, x, y, s, rot), 1, col, 6 * s, { id: id + 2, alpha: o.alpha });
  if (o.alt) crayon(ctx, tf([[-50, -30], [-20, 10], [10, -20], [40, 25]], x, y, s, rot), 1, C.greyD, 4 * s, { id: id + 3, alpha: o.alpha });
}
// Chloroplast mit Grana-Stapeln
function chloroplast(ctx, x, y, rot, id, s = 1) {
  P(ctx, tf(ellPts(0, 0, 60, 29, 22), x, y, s, rot), C.green, { id, shadow: 0.7 });
  for (let g = -1; g <= 1; g++) for (let j = 0; j < 3; j++) flat(ctx, tf(rectPts(g * 28 - 8, -9 + j * 7, 16, 4.5), x, y, s, rot), C.greenD, 0.9);
}
// Lysosom (dunkles Bläschen mit Enzym-Punkten)
function lyso(ctx, x, y, r, id, a = 1) {
  P(ctx, ellPts(x, y, r, r, 24), C.navy, { id, shadow: 0.7, alpha: a });
  for (let k = 0; k < 6; k++) { const w = k * 1.05 + 0.3, d = r * (k % 2 ? 0.5 : 0.28); dot(ctx, x + Math.cos(w) * d, y + Math.sin(w) * d, Math.max(3, r * 0.11), C.mustardL); }
}
// Vesikel (Bläschen) mit Inhalt (Funktion) und optionalem Fähnchen (Farbe = Ziel)
function vesikel(ctx, x, y, r, id, inhalt, flagge, fp = 1, a = 1) {
  if (r <= 1) return;
  P(ctx, ellPts(x, y, r, r, 22), mix(C.mustardL, C.paper, 0.55), { id, shadow: 0.6, alpha: 0.85 * a });
  if (inhalt) inhalt();
  crayon(ctx, ellPts(x, y, r - 2, r - 2, 22).concat([[x + r - 2, y]]), 1, C.mustardD, 4, { id: id + 1, alpha: 0.8 * a });
  if (flagge && fp > 0) pop(ctx, x + r * 0.5, y - r * 0.9, fp, () => {
    crayon(ctx, [[x + r * 0.5, y - r * 0.8], [x + r * 0.5, y - r - 30]], 1, C.woodD, 4, { id: id + 2 });
    P(ctx, [[x + r * 0.5, y - r - 30], [x + r * 0.5 + 28, y - r - 21], [x + r * 0.5, y - r - 12]], flagge, { id: id + 3, shadow: 0.4, alpha: a });
  });
}
// Gefaltetes Protein: 12 bunte Perlen (Aminosäuren); zu 0..1 → Zuckerreste (Golgi)
function knaeuel(ctx, x, y, s, id, zu = 0, a = 1) {
  KNOT.forEach(([dx, dy], k) => kugel(ctx, x + dx * s, y + dy * s, 9.5 * s, AMINO[k], id + k, { alpha: a, shadow: 0.3 }));
  if (zu > 0) [1, 5, 9].forEach((k, i) => {
    const q = seg(zu, i * 0.3, i * 0.3 + 0.4);
    if (q > 0) P(ctx, ellPts(x + KNOT[k][0] * s * 1.55, y + KNOT[k][1] * s * 1.55, 6.5 * s * q, 6.5 * s * q, 6), C.paper, { id: id + 20 + i, shadow: 0.3, alpha: a });
  });
}
// Zuckerwürfel (Traubenzucker), ~32 px bei s = 1
function zucker(ctx, x, y, s, id, a = 1) {
  const h = 16 * s;
  P(ctx, [[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]], C.paper, { id, shadow: 0.5, alpha: a });
  P(ctx, [[x - h, y - h], [x - h * 0.4, y - h * 1.6], [x + h * 1.6, y - h * 1.6], [x + h, y - h]], C.cream, { id: id + 1, shadow: 0, alpha: a });
  P(ctx, [[x + h, y - h], [x + h * 1.6, y - h * 1.6], [x + h * 1.6, y + h * 0.4], [x + h, y + h]], C.creamD, { id: id + 2, shadow: 0, alpha: a });
}
// Energie-Blitz (Symbol)
function blitz(ctx, x, y, s, id, a = 1) { P(ctx, tf(BLITZ, x, y, s), C.mustard, { id, shadow: 0.6, alpha: a }); }
// Bauplan-Blatt (blau, weiße Linien, keine Schrift)
function bauplan(ctx, x, y, s, id) {
  P(ctx, tf(rectPts(-90, -62, 180, 124), x, y, s, -0.06), BAUPLAN, { id, shadow: 1 });
  for (let i = 1; i < 4; i++) crayon(ctx, tf([[-80, -62 + i * 31], [80, -62 + i * 31]], x, y, s, -0.06), 1, C.paper, 2, { id: id + i, alpha: 0.35 });
  const pts = [[-55, 10], [-30, -12], [0, 8], [28, -14], [55, 6]];
  crayon(ctx, tf(pts, x, y, s, -0.06), 1, C.paper, 3, { id: id + 5, alpha: 0.9 });
  pts.forEach((p, k) => { const [px, py] = tf([p], x, y, s, -0.06)[0]; crayon(ctx, ellPts(px, py, 9 * s, 9 * s, 10).concat([[px + 9 * s, py]]), 1, C.paper, 3, { id: id + 6 + k }); });
}

/* Schild ohne Schrift: Papierkarte (180×144 bei s = 1) auf einem Stiel, zeigt ein Piktogramm – für Vergleiche
   („Mitochondrium = Kraftwerk“). In BILDSCHIRM-Koordinaten zeichnen (nach der Welt, Anker per camPt), dann bleibt es bei
   jedem Zoom gleich groß. p = Aufklapp-Fortschritt, (ox, oy) = Versatz der Karte vom Anker in px.
   Piktogramme: tor, halle, tresor, werkbank, foerderband, paket, kraftwerk, recycling, mauer, solar, lager – neue in PIKTO ergänzen. */
const PIKTO = {
  tor(c, id) {
    [[-78, 0], [30, 3]].forEach(([x0, o]) => {
      for (let j = 0; j < 3; j++) { const x = x0 + j * 17; P(c, [[x, 44], [x, -30], [x + 7, -42], [x + 14, -30], [x + 14, 44]], C.woodL, { id: id + j + o, shadow: 0.4 }); }
      crayon(c, [[x0 - 2, -8], [x0 + 50, -8]], 1, C.woodD, 5, { id: id + 8 + o });
      crayon(c, [[x0 - 2, 24], [x0 + 50, 24]], 1, C.woodD, 5, { id: id + 9 + o });
    });
    crayonArrow(c, [[-9, -48], [-9, 40]], 1, C.green, 7);
    crayonArrow(c, [[10, 40], [10, -48]], 1, C.coralD, 7);
  },
  halle(c, id) {
    P(c, rectPts(-72, -8, 144, 58), C.kraft, { id, shadow: 0.5 });
    const roof = [[-72, -8]]; for (let j = 0; j < 4; j++) roof.push([-72 + j * 36, -46], [-36 + j * 36, -8]);
    P(c, roof, C.mustard, { id: id + 1, shadow: 0.4 });
    for (let j = 0; j < 3; j++) P(c, rectPts(-60 + j * 44, 6, 28, 18), C.waterL, { id: id + 2 + j, shadow: 0 });
    P(c, rectPts(-12, 28, 24, 22), C.woodD, { id: id + 6, shadow: 0 });
  },
  tresor(c, id) {
    P(c, tf(rrectPts(-70, -9, 140, 18, 9), 24, -50, 1, -0.25), BAUPLAN, { id: id + 5, shadow: 0.4 });
    P(c, rrectPts(-62, -46, 112, 98, 10), C.greyD, { id, shadow: 0.8 });
    P(c, rrectPts(-52, -36, 92, 78, 8), C.grey, { id: id + 1, shadow: 0 });
    ell(c, -8, 3, 24, 24, C.greyL, { id: id + 2, shadow: 0.3 });
    for (let k = 0; k < 6; k++) { const a = k / 6 * TAU; crayon(c, [[-8, 3], [-8 + Math.cos(a) * 20, 3 + Math.sin(a) * 20]], 1, C.greyD, 3, { id: id + 10 + k }); }
    P(c, rectPts(26, -12, 8, 30), C.mustard, { id: id + 3, shadow: 0.3 });
  },
  werkbank(c, id) {
    P(c, rectPts(-74, 14, 148, 14), C.wood, { id, shadow: 0.6 });
    P(c, rectPts(-66, 28, 12, 32), C.woodD, { id: id + 1, shadow: 0.3 });
    P(c, rectPts(54, 28, 12, 32), C.woodD, { id: id + 2, shadow: 0.3 });
    const g = []; for (let k = 0; k < 32; k++) { const a = k / 32 * TAU, r = Math.floor(k / 2) % 2 ? 25 : 34; g.push([Math.cos(a) * r, Math.sin(a) * r]); }
    P(c, tf(g, -22, -22, 1, G.t * 0.6), C.mustardD, { id: id + 3, shadow: 0.6 });
    dot(c, -22, -22, 9, C.paper);
    P(c, tf(rectPts(-4, -34, 8, 48), 42, -6, 1, 0.45), C.woodL, { id: id + 4, shadow: 0.4 });
    P(c, tf(rectPts(-17, -46, 34, 14), 42, -6, 1, 0.45), C.greyD, { id: id + 5, shadow: 0.4 });
  },
  foerderband(c, id) {
    crayon(c, [[-60, 40], [-60, 62]], 1, C.greyD, 5, { id: id + 9 });
    crayon(c, [[60, 40], [60, 62]], 1, C.greyD, 5, { id: id + 10 });
    P(c, rrectPts(-78, 14, 156, 28, 14), C.greyD, { id, shadow: 0.7 });
    [-64, 0, 64].forEach((x, k) => ell(c, x, 28, 10, 10, C.greyL, { id: id + 1 + k, shadow: 0 }));
    const sh = (G.t * 16) % 30;
    [-58, 6].forEach((x0, k) => { const x = x0 + sh; P(c, rectPts(x, -24, 38, 36), C.kraft, { id: id + 5 + k, shadow: 0.5 }); crayon(c, [[x + 19, -24], [x + 19, 12]], 1, C.kraftD, 3, { id: id + 7 + k }); });
    crayonArrow(c, [[-44, -50], [44, -50]], 1, C.crayonBlue, 6);
  },
  paket(c, id) {
    P(c, rectPts(-52, -8, 84, 60), C.kraft, { id, shadow: 0.7 });
    P(c, [[-52, -8], [-32, -28], [52, -28], [32, -8]], C.kraftL, { id: id + 1, shadow: 0 });
    P(c, [[32, -8], [52, -28], [52, 32], [32, 52]], C.kraftD, { id: id + 2, shadow: 0 });
    crayon(c, [[-10, -8], [-10, 52]], 1, C.mustardD, 6, { id: id + 3 });
    crayon(c, [[-30, -18], [42, -18]], 1, C.mustardD, 5, { id: id + 4 });
    crayon(c, [[40, -28], [40, -62]], 1, C.woodD, 4, { id: id + 5 });
    P(c, [[40, -64], [74, -54], [40, -44]], C.red, { id: id + 6, shadow: 0.4 });
  },
  kraftwerk(c, id) {
    ell(c, 56, -58, 12, 10, C.creamD, { id: id + 7, shadow: 0 });
    ell(c, 68, -68, 15, 12, C.creamD, { id: id + 8, shadow: 0 });
    P(c, rectPts(38, -48, 22, 100), C.grey, { id: id + 1, shadow: 0.6 });
    P(c, rectPts(-72, 0, 110, 52), C.greyL, { id, shadow: 0.6 });
    for (let j = 0; j < 3; j++) P(c, rectPts(-62 + j * 34, 12, 20, 16), C.waterL, { id: id + 2 + j, shadow: 0 });
    blitz(c, -18, -24, 0.95, id + 6);
  },
  recycling(c, id) {
    for (let k = 0; k < 3; k++) { const a0 = k * TAU / 3 - 1.5; crayonArrow(c, arcPts(0, 2, 46, 46, a0, a0 + 1.6, 12), 1, C.green, 10); }
  },
  mauer(c, id) {
    for (let r = 0; r < 4; r++) for (let j = 0; j < 4; j++) {
      const x = -74 + j * 40 + (r % 2 ? 20 : 0); if (x > 40) continue;
      P(c, rectPts(x, -46 + r * 24, 36, 20), r % 2 ? C.greenD : C.green, { id: id + r * 5 + j, shadow: 0.3 });
    }
  },
  solar(c, id) {
    for (let k = 0; k < 8; k++) { const a = k / 8 * TAU; crayon(c, [[-48 + Math.cos(a) * 26, -38 + Math.sin(a) * 26], [-48 + Math.cos(a) * 36, -38 + Math.sin(a) * 36]], 1, C.mustardD, 4, { id: id + 10 + k }); }
    ell(c, -48, -38, 20, 20, C.mustard, { id, shadow: 0.4 });
    P(c, [[-44, 52], [72, 52], [52, -8], [-18, -8]], C.navy, { id: id + 1, shadow: 0.6 });
    for (let j = 1; j < 3; j++) crayon(c, [[lerp(-18, -44, j / 3), lerp(-8, 52, j / 3)], [lerp(52, 72, j / 3), lerp(-8, 52, j / 3)]], 1, C.petrolL, 3, { id: id + 2 + j });
    for (let j = 1; j < 4; j++) crayon(c, [[lerp(-18, 52, j / 4), -8], [lerp(-44, 72, j / 4), 52]], 1, C.petrolL, 3, { id: id + 5 + j });
  },
  lager(c, id) {
    P(c, rrectPts(-50, -48, 100, 100, 22), C.waterL, { id, shadow: 0.6 });
    crayon(c, [[-50, -18], [50, -18]], 1, C.waterD, 4, { id: id + 1 });
    crayon(c, [[-50, 22], [50, 22]], 1, C.waterD, 4, { id: id + 2 });
    P(c, smooth([[0, -26], [16, 2], [12, 18], [0, 24], [-12, 18], [-16, 2]], 4, true), C.waterD, { id: id + 3, shadow: 0.4 });
  },
};
function schild(ctx, sx, sy, s, typ, p, id, ox = 0, oy = -140) {
  if (p <= 0) return;
  const cx = sx + ox, cy = sy + oy;
  if (Math.hypot(ox, oy) > 20) crayon(ctx, [[sx, sy], [cx, cy]], p, C.kraftD, 5, { id: id + 1 });
  dot(ctx, sx, sy, 7, C.kraftD);
  pop(ctx, cx, cy, p, () => {
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
    P(ctx, rrectPts(-90, -72, 180, 144, 16), C.paper, { id, shadow: 1.3 });
    PIKTO[typ](ctx, id + 10);
    ctx.restore();
  });
}

/* ================================================================== Physik/Teilchen & Hilfen (aus „Der Streuversuch von Rutherford“)
   Anwendungsbeispiel: D:\KI Projekte\Lernanimationen\Rutherford Streuversuch\src\szenen.js
   (dort noch lokal definiert – beim Übernehmen NICHT erneut deklarieren). */
const lerp2 = (a, b, q) => [lerp(a[0], b[0], q), lerp(a[1], b[1], q)];
// 0 → 1 ab a (Einblenden über f s), 1 → 0 ab e: Sichtbarkeit einer Hervorhebung/eines Schilds
const fenster = (t, a, e, f = 0.6) => seg(t, a, a + f) * (1 - seg(t, e, e + f));
// Dreieckswelle 0..1..0 – Teilchen, die zwischen Wänden hin- und herprallen: x = x0 + tri(t * v + phase) * breite
const tri = u => { const f = ((u % 2) + 2) % 2; return f < 1 ? f : 2 - f; };
// Teilpfad bis Anteil q (0..1) und Punkt dort – Flugbahnen, die sich hinter einem Teilchen zeichnen
function bahnBis(pts, q) {
  const L = polyLen(pts), d = L[L.length - 1] * clamp(q), out = [pts[0]];
  for (let i = 1; i < pts.length && L[i] < d; i++) out.push(pts[i]);
  const p = polyAt(pts, L, d); out.push(p);
  return [out, p];
}
// Ladungszeichen (Symbole sind im Bild erlaubt)
function plusZ(ctx, x, y, s, col, id, a = 1) {
  crayon(ctx, [[x - s, y], [x + s, y]], 1, col, s * 0.6, { id, alpha: a });
  crayon(ctx, [[x, y - s], [x, y + s]], 1, col, s * 0.6, { id: id + 1, alpha: a });
}
function minusZ(ctx, x, y, s, col, id, a = 1) { crayon(ctx, [[x - s, y], [x + s, y]], 1, col, s * 0.6, { id, alpha: a }); }
// geladenes Teilchen: Kugel mit + oder − (Alpha-Teilchen, Ion, Proton …)
function teilchen(ctx, x, y, r, col, id, zeichen = '+', a = 1) {
  kugel(ctx, x, y, r, col, id, { alpha: a, shadow: 0.4 });
  if (zeichen === '+') plusZ(ctx, x, y, r * 0.5, C.paper, id + 2, a);
  else if (zeichen === '-') minusZ(ctx, x, y, r * 0.5, C.paper, id + 2, a);
}
const elektron = (ctx, x, y, r, id, a = 1) => teilchen(ctx, x, y, r, C.crayonBlue, id, '-', a);
// kurzer heller Lichtblitz (Treffer auf Leuchtschirm, Funke, Aufprall); a = Sichtbarkeit 0..1
function lichtblitz(ctx, x, y, s, a, id) {
  if (a <= 0) return;
  halo(ctx, x, y, 70 * s, a, '255,244,190');
  const pts = []; for (let k = 0; k < 16; k++) { const r = (k % 2 ? 7 : 24) * s, w = k / 16 * TAU + 0.2; pts.push([x + Math.cos(w) * r, y + Math.sin(w) * r]); }
  P(ctx, pts, C.mustardL, { id, shadow: 0, alpha: a });
}
