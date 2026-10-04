/* Bühne, Klassenzimmer, Erzählerin, Übergänge, Ablauf – themenunabhängig.
   Projektspezifisch ist nur szenen.js (WELTEN, UEBERGAENGE, ERZAEHLERIN, INTRO, SCHLUSS, STIMMUNG). */
'use strict';

const D = window.PROJEKT;
const T = D.timeline;

function envAt(str, t) {
  const i = Math.floor(t * D.fps);
  if (i < 0 || i >= str.length) return 0;
  return (str.charCodeAt(i) - 48) / 40;
}
const mouthAt = t => envAt(D.mouth, t);
const roundAt = t => envAt(D.round, t);
const blinkAt = (t, off = 0) => ((t + off) % 4.3) < 0.13;

// ================================================================== Klassenzimmer
const BOARD = { x: 800, y: 230, w: 860, h: 570 };
const TEACHER_HOME = 500;

let titleCanvas = null;
function titleImage() {
  if (titleCanvas) return titleCanvas;
  const c = makeCanvas(1640, 180), x = c.getContext('2d');
  let fs = 104;
  const font = n => `bold ${n}px "Segoe Print", "Ink Free", "Comic Sans MS", "Chalkboard SE", cursive`;
  x.font = font(fs);
  const s = D.titel;
  while (x.measureText(s).width > 1580 && fs > 50) { fs -= 4; x.font = font(fs); }
  x.textBaseline = 'middle'; x.textAlign = 'center';
  x.fillStyle = pattern(x, 'tc', crayonTex(C.crayonBlue));
  x.lineWidth = 3; x.strokeStyle = 'rgba(44,88,201,0.55)';
  x.strokeText(s, 820, 92); x.fillText(s, 820, 92); x.fillText(s, 821, 93);
  titleCanvas = c;
  return c;
}
function drawTitle(ctx, t) {
  const tp = seg(t, T.titel[0], T.titel[1]);
  if (tp <= 0) return;
  const img = titleImage(), tw = 800, th = tw * img.height / img.width;
  ctx.save();
  ctx.beginPath(); ctx.rect(BOARD.x + 30, BOARD.y + 8, tw * tp, th + 10); ctx.clip();
  ctx.drawImage(img, BOARD.x + 30, BOARD.y + 12, tw, th);
  ctx.restore();
}

// Raum: gelbe Wand, Fenster, Uhr (tickt sekündlich), Regal, Pflanze
function classroom(ctx, t, o = {}) {
  backdrop(ctx, C.mustardL, -300, -300, W + 600, H + 600, 11);
  P(ctx, rectPts(-300, 780, W + 600, 400), C.kraft, { id: 12, shadow: 0.5 });
  crayon(ctx, [[-300, 792], [W + 300, 792]], 1, C.kraftD, 5);
  P(ctx, rectPts(250, 170, 230, 270), C.paper, { id: 13 });
  P(ctx, rectPts(266, 186, 198, 238), '#BFE0E4', { id: 14, shadow: 0.2 });
  cloud(ctx, 360, 290, 0.55, 15);
  crayon(ctx, [[365, 186], [365, 424]], 1, C.paper, 9);
  crayon(ctx, [[266, 305], [464, 305]], 1, C.paper, 9);
  const cx = 640, cy = 150;
  ell(ctx, cx, cy, 58, 58, C.paper, { id: 16 });
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; dot(ctx, cx + Math.cos(a) * 44, cy + Math.sin(a) * 44, i % 3 ? 2.5 : 4.5, C.ink); }
  const am = 1.9 + (o.uhrLauf ? seg(t, o.uhrLauf[0], o.uhrLauf[1]) * 0.8 : 0);
  crayon(ctx, [[cx, cy], [cx + Math.cos(am - Math.PI / 2) * 26, cy + Math.sin(am - Math.PI / 2) * 26]], 1, C.ink, 6);
  crayon(ctx, [[cx, cy], [cx + Math.cos(-0.5) * 38, cy + Math.sin(-0.5) * 38]], 1, C.ink, 4);
  const sa = Math.floor(t) / 60 * TAU - Math.PI / 2;
  crayon(ctx, [[cx, cy], [cx + Math.cos(sa) * 44, cy + Math.sin(sa) * 44]], 1, C.red, 2.5);
  dot(ctx, cx, cy, 5, C.ink);
  P(ctx, rectPts(1700, 560, 190, 18), C.wood, { id: 17 });
  [C.coral, C.petrol, C.mustardD, C.violet, C.coralD, C.petrolL].forEach((c, i) => P(ctx, rectPts(1706 + i * 22, 470 + (i % 2) * 10, 20, 90 - (i % 2) * 10), c, { id: 18 + i, shadow: 0.6 }));
  ell(ctx, 1860, 510, 30, 30, C.petrolL, { id: 25 });
  flat(ctx, ellPts(1852, 505, 12, 18), C.green, 0.8);
  crayon(ctx, [[1860, 540], [1860, 560]], 1, C.woodD, 5);
  P(ctx, [[150, 780], [210, 780], [200, 840], [160, 840]], C.coralD, { id: 26 });
  for (let i = 0; i < 5; i++) P(ctx, tf(ellPts(0, -40, 13, 42), 180, 780, 1, -0.9 + i * 0.45), C.greenD, { id: 27 + i, shadow: 0.5 });
}

// Lehrerin im Raum: folgt der Stiftspitze auf der Tafel, sonst Geste/Blick
function teacherInRoom(t, tip, o = {}) {
  const home = TEACHER_HOME;
  const st = { x: home, y: 1045, s: 1.05, mouth: mouthAt(t), round: roundAt(t), blink: blinkAt(t, o.blink || 0), look: [0, 0], serious: o.serious || 0 };
  if (tip) {
    st.x = clamp(tip[0] - 175, home, 1400);
    if (o.nurZeigen) st.x = home;
    st.tip = o.nurZeigen ? [Math.min(tip[0], home + 330), Math.max(tip[1], 560)] : tip;
    st.look = [0.9, -0.5];
    st.hop = st.x > home + 2 ? Math.abs(Math.sin(t * 7.5)) * 10 : 0;
  } else if (o.haende) { st.handA = [-60, -250]; st.handB = [60, -250]; }
  else if (o.geste) { st.handA = [-150, -300 + Math.sin(t * 3) * 6]; st.handB = [96, -200]; }
  else { st.handA = [-140, -290 + Math.sin(t * 2) * 8]; }
  return st;
}

// Tischdinge vor der Lehrerin
function deskWithThings(ctx, extra) {
  desk(ctx, 290, 800, 520, 190);
  P(ctx, rectPts(330, 770, 120, 30), C.petrol, { id: 1880 });
  P(ctx, rectPts(340, 746, 104, 26), C.coral, { id: 1881 });
  P(ctx, tf(rrectPts(-30, -6, 60, 12, 5), 700, 790, 1, -0.1), C.mustard, { id: 1882 });
  if (extra) extra(ctx);
}

/* Szene 1: Vorhang auf, Titel an der Tafel, Lehrerin zeichnet, Kamera zoomt in die Zeichnung, dort öffnet sich die erste Welt.
   INTRO = {
     tafel(ctx, t)       – Zeichnung auf der Tafel (im Tafel-Clip). Liefert optional die aktuelle Stiftspitze [x,y] zurück.
     zoom: {a, e, ziel:[x,y], Z}  – Kamerafahrt in einen Punkt der Tafel (Tafelkoordinaten)
     welt(ctx, t, alpha) – erste Welt, die beim Zoom erscheint (Bildschirmkoordinaten)
     weltEin: [a, e]     – Einblendung der Welt
     geste: [a, e]       – Zeiträume mit offener Handgeste (Begrüßung)
   } */
function drawIntro(ctx, t) {
  const I = INTRO;
  const pz = I.zoom ? eio(seg(t, I.zoom.a, I.zoom.e)) : 0;
  const Z = I.zoom ? I.zoom.Z || 9 : 1;
  const z = Math.exp(Math.log(Z) * pz);
  const [fx, fy] = I.zoom ? I.zoom.ziel : [W / 2, H / 2];
  const cx = lerp(W / 2, fx, pz), cy = lerp(H / 2, fy, pz);
  const wa = I.weltEin ? sm(seg(t, I.weltEin[0], I.weltEin[1])) : 0;
  if (wa < 1) {
    ctx.save();
    ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-cx, -cy);
    classroom(ctx, t);
    easel(ctx, BOARD.x, BOARD.y, BOARD.w, BOARD.h);
    drawTitle(ctx, t);
    ctx.save();
    pathPts(ctx, rectPts(BOARD.x, BOARD.y, BOARD.w, BOARD.h)); ctx.clip();
    const tip = I.tafel ? I.tafel(ctx, t) : null;
    ctx.restore();
    const geste = (I.geste || []).some(([a, e]) => t > a && t < e);
    teacher(ctx, teacherInRoom(t, tip, { geste }));
    deskWithThings(ctx);
    ctx.restore();
  }
  if (wa > 0 && I.welt) I.welt(ctx, t, wa);
}

/* Letzte Szene: zurück im Klassenzimmer, Tafel mit Ergebnis, Dinge auf dem Tisch, Blick ins Publikum, Vorhang zu.
   SCHLUSS = { tafel(ctx,t) -> tip|null, tisch(ctx,t), blick: t, zeigenNur: true, uhrLauf:[a,e] } */
function drawSchluss(ctx, t) {
  const S = SCHLUSS;
  classroom(ctx, t, { uhrLauf: S.uhrLauf });
  easel(ctx, BOARD.x, BOARD.y, BOARD.w, BOARD.h);
  ctx.save();
  pathPts(ctx, rectPts(BOARD.x, BOARD.y, BOARD.w, BOARD.h)); ctx.clip();
  flat(ctx, rectPts(BOARD.x, BOARD.y, BOARD.w, BOARD.h), C.paper);
  const tip = S.tafel ? S.tafel(ctx, t) : null;
  ctx.restore();
  const st = teacherInRoom(t, tip, { nurZeigen: S.zeigenNur !== false, haende: S.blick && t > S.blick, blink: 1.3, serious: S.ernst || 0 });
  teacher(ctx, st);
  deskWithThings(ctx, c => S.tisch && S.tisch(c, t));
}

// Abreißkalender, dessen Blätter nach oben wegklappen (Zeit vergeht) – für Tisch oder Welt
function flipCalendar(ctx, kx, ky, t, a, e, n = 7, mark = 26) {
  P(ctx, rectPts(kx - 6, ky - 10, 122, 150), C.kraftD, { id: 6390, shadow: 1 });
  calendarPage(ctx, kx, ky, 110, 130, 6400, (mark + n * 3) % 35, 1);
  const step = (e - a) / n;
  for (let i = n - 1; i >= 0; i--) {
    const p = seg(t, a + i * step, a + i * step + 0.8);
    if (p >= 1) continue;
    const q = eio(p);
    ctx.save();
    ctx.translate(kx + 55, ky); ctx.scale(1, Math.cos(q * Math.PI)); ctx.rotate(q * 0.3); ctx.translate(-kx - 55, -ky);
    ctx.globalAlpha *= 1 - seg(p, 0.85, 1);
    if (Math.cos(q * Math.PI) > 0) calendarPage(ctx, kx, ky, 110, 130, 6410 + i * 5, i === 0 ? mark : -1, 1);
    else P(ctx, rectPts(kx, ky, 110, 130), C.creamD, { id: 6450 + i, shadow: 0.6 });
    ctx.restore();
  }
}

// ================================================================== Erzählerin am Bühnenrand
/* ERZAEHLERIN = {
     von, bis        – sichtbar (tritt links auf/ab)
     x, s            – Standplatz (Standard 250 / 0.58)
     naeher: [{a, e, x, s}]   – tritt zum Zeichnen näher heran
     posen:  [{a, e, typ}]    – 'zeigen' | 'geste' | 'haende' | 'stift-runter' | 'bogen' | 'folgen' (folgt G.tip)
     ernst:  [[t, 0..1], ...] – Gesichtsausdruck (Keyframes)
   }
   Ohne passende Pose folgt sie automatisch einer Stiftspitze, die eine Szene in G.tip meldet. */
function presenter(t) {
  const E = ERZAEHLERIN;
  if (!E || t < E.von || t > E.bis + 1.6) return null;
  const x0 = E.x ?? 250, s0 = E.s ?? 0.58;
  const enter = seg(t, E.von, E.von + 1.8), exit = seg(t, E.bis, E.bis + 1.6);
  let x = lerp(-140, x0, eout(enter)), s = s0;
  if (exit > 0) x = lerp(x0, -160, ein(exit));
  let walking = (enter > 0 && enter < 1) || (exit > 0 && exit < 1);
  for (const n of E.naeher || []) {
    const q = seg(t, n.a - 1, n.a) * (1 - seg(t, n.e, n.e + 1.2));
    if (q > 0) { x = lerp(x, n.x, eio(q)); s = lerp(s, n.s, eio(q)); if (q < 1) walking = true; }
  }
  const st = {
    x, y: 1054, s, hop: walking ? Math.abs(Math.sin(t * 8)) * 10 : 0,
    mouth: mouthAt(t), round: roundAt(t), blink: blinkAt(t, 0.7), look: [0.8, -0.2],
    serious: E.ernst ? kf(E.ernst, t, x => x) : 0, handA: [-86, -196], handB: [84, -196],
  };
  const pose = (E.posen || []).find(p => t >= p.a && t < p.e);
  const typ = pose ? pose.typ : (G.tip ? 'folgen' : null);
  switch (typ) {
    case 'folgen': if (G.tip) { st.tip = G.tip; st.look = [0.9, -0.6]; } break;
    case 'zeigen': st.tip = pose.ziel || [x + 330 * s, 1054 - 520 * s]; st.look = [1, -0.5]; break;
    case 'geste': st.handA = [-150, -300 + Math.sin(t * 2.2) * 10]; break;
    case 'haende': st.handA = [-12, -250]; st.handB = [12, -252]; st.look = [0.5, 0.3]; break;
    case 'stift-runter': st.handB = [70, -210]; st.handA = [-20, -250]; st.look = [0.2, 0.6]; break;
    case 'bogen': { const q = seg(t, pose.a, pose.e); st.tip = [x + lerp(200, 330, q) * s, 1054 - lerp(360, 560, q) * s]; break; }
  }
  return st;
}

// ================================================================== Bühne: Vorhänge, Lambrequin, Rahmen, Boden
function curtainOpenAmount(t) {
  const v = eio(seg(t, T.vorhangAuf[0], T.vorhangAuf[1])) * (1 - eio(seg(t, T.vorhangZu[0], T.vorhangZu[1])));
  return G.vorhangMax !== undefined ? Math.min(v, G.vorhangMax) : v;   // Pausenvorhang (z. B. Arbeitsblatt)
}
function drawCurtain(ctx, side, open, t) {
  const w = lerp(W / 2 + 20, 185, open);
  const X = (f, y) => {
    const pinch = open * Math.exp(-Math.pow((y - 640) / 170, 2)) * 0.55;
    const d = f * w * (1 - pinch);
    return side < 0 ? d : W - d;
  };
  const folds = 7, n = 14;
  for (let i = folds - 1; i >= 0; i--) {
    const f0 = i / folds, f1 = (i + 1) / folds;
    const sway = Math.sin(t * 1.3 + i) * 3 * (1 - open * 0.5);
    const pts = [];
    for (let k = 0; k <= n; k++) { const y = 60 + k / n * 950; pts.push([X(f1, y) + sway, y]); }
    for (let k = n; k >= 0; k--) { const y = 60 + k / n * 950; pts.push([X(f0, y), y + (k === n ? 8 * Math.sin(i * 2.1) : 0)]); }
    P(ctx, pts, i % 2 ? C.coral : C.coralD, { id: 9500 + i + (side > 0 ? 20 : 0), shadow: 1.1 });
  }
  if (open > 0.3) ell(ctx, side < 0 ? w * 0.45 : W - w * 0.45, 640, 16, 34, C.mustard, { id: 9540 + side, shadow: 0.8 });
}
function drawStage(ctx, t) {
  const open = curtainOpenAmount(t);
  P(ctx, [[-20, 985], [W + 20, 985], [W + 20, 1100], [-20, 1100]], C.wood, { id: 9600, shadow: 1.4 });
  for (let i = 0; i < 16; i++) crayon(ctx, [[i * 130 - 20, 990], [i * 130 - 60, 1090]], 1, C.woodD, 3, { id: 9610 + i });
  crayon(ctx, [[-20, 1030], [W + 20, 1034]], 1, C.woodD, 3);
  P(ctx, rectPts(-20, 980, W + 40, 14), C.woodL, { id: 9630, shadow: 0.8 });
  drawCurtain(ctx, -1, open, t);
  drawCurtain(ctx, 1, open, t);
  const sc = 14, pts = [[-20, -20], [W + 20, -20], [W + 20, 70]];
  for (let i = sc; i >= 0; i--) { const x = i / sc * W; pts.push([x + W / sc / 2, 70], ...arcPts(x, 70, W / sc / 2, 30, 0, Math.PI, 6)); }
  pts.push([-20, 70]);
  P(ctx, pts.filter(p => p[0] >= -30 && p[0] <= W + 30), C.coralD, { id: 9650, shadow: 1.4 });
  for (let i = 0; i <= sc; i++) dot(ctx, i / sc * W, 104, 7, C.mustard);
  crayon(ctx, [[0, 30], [W, 30]], 1, C.mustard, 6);
  ctx.save();
  ctx.fillStyle = C.kraft;
  ctx.beginPath(); ctx.rect(-50, -50, W + 100, H + 100); ctx.rect(22, 18, W - 44, H - 38);
  ctx.fill('evenodd');
  ctx.fillStyle = pattern(ctx, 'g', TEX.gouache); ctx.fill('evenodd');
  ctx.strokeStyle = C.paper; ctx.lineWidth = 4; ctx.strokeRect(22, 18, W - 44, H - 38);
  ctx.restore();
}

// ================================================================== Übergänge (Bibliothek)
function drawScaled(ctx, fn, ox, oy, k) { ctx.save(); ctx.translate(ox, oy); ctx.scale(k, k); fn(ctx); ctx.restore(); }
function renderToBuffer(idx, fn) {
  const b = getBuffer(idx, CANVAS.width, CANVAS.height);
  const c = b.getContext('2d');
  c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, b.width, b.height);
  c.setTransform(G.k, 0, 0, G.k, 0, 0);
  fn(c);
  return b;
}
function paperSheet(ctx, x, y, w, h, alpha) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.shadowColor = 'rgba(40,25,15,0.35)'; ctx.shadowBlur = 24 * G.k; ctx.shadowOffsetY = 12 * G.k;
  ctx.fillStyle = C.paper; ctx.fillRect(x - 8, y - 8, w + 16, h + 16);
  ctx.restore();
}
// Match-Cut heraus: A liegt als kleines Blatt bei fB (Bildschirmpunkt in B) und hebt sich an den Rändern
function zoomOut(ctx, drawA, drawB, p, fB, Z, bi = 0) {
  const e = eio(p), k = Math.exp(Math.log(Z) * (1 - e));
  const cx = lerp(W / 2, fB[0], e), cy = lerp(H / 2, fB[1], e);
  drawScaled(ctx, drawB, cx - fB[0] * k, cy - fB[1] * k, k);
  const al = 1 - sm(seg(p, 0.5, 0.95));
  if (al <= 0) return;
  const bufA = renderToBuffer(bi, drawA), aw = W * k / Z, ah = H * k / Z, lift = Math.sin(p * Math.PI) * 0.05;
  paperSheet(ctx, cx - aw / 2, cy - ah / 2, aw, ah, al);
  ctx.save(); ctx.globalAlpha *= al;
  ctx.drawImage(bufA, cx - aw / 2 * (1 + lift), cy - ah / 2 * (1 + lift), aw * (1 + lift), ah * (1 + lift));
  ctx.restore();
}
// Match-Cut hinein: B entfaltet sich aus dem Punkt fA (Bildschirmpunkt in A)
function zoomIn(ctx, drawA, drawB, p, fA, Z, bi = 0) {
  const e = eio(p), k = Math.exp(Math.log(Z) * e);
  const cx = lerp(fA[0], W / 2, e), cy = lerp(fA[1], H / 2, e);
  drawScaled(ctx, drawA, cx - fA[0] * k, cy - fA[1] * k, k);
  const al = sm(seg(p, 0.1, 0.6));
  if (al <= 0) return;
  const bufB = renderToBuffer(bi, drawB), bw = W * k / Z, bh = H * k / Z;
  paperSheet(ctx, cx - bw / 2, cy - bh / 2, bw, bh, al);
  ctx.save(); ctx.globalAlpha *= al; ctx.drawImage(bufB, cx - bw / 2, cy - bh / 2, bw, bh); ctx.restore();
}
// Kamera gleitet seitlich, eine große Papierfassade im Vordergrund verdeckt die Naht
function panWipe(ctx, drawA, drawB, p, t, facadeCol = C.mustardL) {
  const e = eio(p);
  drawScaled(ctx, drawA, -W * e, 0, 1);
  drawScaled(ctx, drawB, W * (1 - e), 0, 1);
  ctx.save();
  ctx.translate(W * (1 - e) - 380 + (0.5 - e) * 500, 0); ctx.scale(1.25, 1.25);
  facade(ctx, 0, 1000, 620, 980, { color: facadeCol, id: 9700, floors: 6, door: true, roof: 'flat' });
  ctx.restore();
}
// Szene zieht sich zu einem farbigen Streifen zusammen, der zur nächsten Szene führt (z. B. Wasser, Straße)
function squashStrip(ctx, drawA, drawB, p, t, yA = 900, yB = 935, col = C.water) {
  const p1 = eio(seg(p, 0, 0.55)), p2 = eio(seg(p, 0.2, 1));
  const ys = lerp(yA, yB, p2);
  ctx.save(); ctx.translate(0, ys); ctx.scale(1, Math.max(0.02, p2)); ctx.translate(0, -yB); drawB(ctx); ctx.restore();
  if (p1 < 1) {
    const buf = renderToBuffer(0, drawA), s = 1 - p1 * 0.97;
    ctx.save(); ctx.globalAlpha *= 1 - seg(p, 0.45, 0.6);
    ctx.drawImage(buf, 0, yA - yA * s, W, H * s);
    flat(ctx, rectPts(0, yA - yA * s, W, H * s), col, p1 * 0.9);
    ctx.restore();
  }
  if (p > 0.3 && p < 0.9) {
    ctx.save(); ctx.globalAlpha *= Math.sin(seg(p, 0.3, 0.9) * Math.PI);
    P(ctx, rectPts(-50, ys - 22, W + 100, 44), col, { id: 9750, shadow: 1 });
    crayon(ctx, smooth([[0, ys], [400, ys - 8], [800, ys + 6], [1200, ys - 6], [1600, ys + 6], [2000, ys]], 5), 1, shade(col, 0.4), 5);
    ctx.restore();
  }
}
// Papierband schiebt sich aus A heraus und läuft in einen Punkt von B (z. B. Telegraf, Buch, Maschine)
function tapePan(ctx, drawA, drawB, p, t, pA = [960, 720], pB = [1500, 700], marks = true) {
  const e = eio(seg(p, 0.25, 1)), ax = -W * e, bx = W * (1 - e);
  drawScaled(ctx, drawA, ax, 0, 1);
  drawScaled(ctx, drawB, bx, 0, 1);
  const pts = smooth([[pA[0] + ax, pA[1]], [pA[0] + 340 + ax, pA[1] + 100], [pA[0] + 840 + ax, pA[1] + 40], [pB[0] - 300 + bx, pB[1] + 60], [pB[0] + bx, pB[1]]], 8);
  tape(ctx, pts, seg(p, 0, 0.9), 9800, marks);
}
// Buchseite blättert um (A dreht sich um den linken Rand), darunter liegt B
function pageTurn(ctx, drawA, drawB, p, t) {
  drawB(ctx);
  const e = eio(p), buf = renderToBuffer(0, drawA), sx = Math.cos(e * Math.PI), x0 = 60;
  ctx.save();
  ctx.translate(x0, 0); ctx.scale(sx, 1 - Math.sin(e * Math.PI) * 0.04); ctx.translate(-x0, 0);
  if (sx > 0) { ctx.drawImage(buf, 0, 0, W, H); flat(ctx, rectPts(0, 0, W, H), '#2A1A10', (1 - sx) * 0.35); }
  else { P(ctx, rectPts(x0, 20, W - 80, H - 40), C.cream, { id: 9850, shadow: 1.5 }); flat(ctx, rectPts(x0, 20, W - 80, H - 40), '#2A1A10', (1 + sx) * 0.25); }
  ctx.restore();
  if (sx > 0) {
    const g = ctx.createLinearGradient(x0 + (W - x0) * sx, 0, x0 + (W - x0) * sx + 160, 0);
    g.addColorStop(0, 'rgba(40,25,15,0.28)'); g.addColorStop(1, 'rgba(40,25,15,0)');
    ctx.fillStyle = g; ctx.fillRect(x0 + (W - x0) * sx, 0, 160, H);
  }
}
// Hintergrund rollt sich wie eine Schriftrolle nach oben auf und gibt B frei
function scrollRoll(ctx, drawA, drawB, p, t) {
  drawB(ctx);
  const e = eio(p), h = H * (1 - e);
  if (h < 2) return;
  const buf = renderToBuffer(0, drawA);
  ctx.drawImage(buf, 0, 0, buf.width, buf.height * (1 - e), 0, 0, W, h);
  P(ctx, rrectPts(-30, h - 30, W + 60, 60, 28), C.creamD, { id: 9870, shadow: 1.5 });
  crayon(ctx, [[0, h - 12], [W, h - 12]], 1, C.kraftD, 4, { alpha: 0.6 });
  crayon(ctx, [[0, h + 12], [W, h + 12]], 1, C.kraftD, 3, { alpha: 0.4 });
}
// Gedankenblase/Seifenblase platzt: A dehnt sich und verblasst, Papierschnipsel fliegen, darunter liegt B
function platzen(ctx, drawA, drawB, p) {
  drawB(ctx);
  if (p < 0.6) {
    const q = p / 0.6;
    ctx.save(); ctx.globalAlpha *= 1 - sm(q);
    ctx.translate(W / 2, H / 2); ctx.scale(1 + 0.25 * q, 1 + 0.25 * q); ctx.translate(-W / 2, -H / 2);
    drawA(ctx); ctx.restore();
  }
  for (let k = 0; k < 20; k++) {
    const a = k * 0.314 + hash(k) * 0.3, d = lerp(150, 950, eout(p)), al = 1 - seg(p, 0.55, 1);
    if (al > 0) P(ctx, tf(rectPts(-15, -10, 30, 20), W / 2 + Math.cos(a) * d * 1.3, H / 2 + Math.sin(a) * d * 0.8, 1, a + p * 5), k % 2 ? C.cream : C.paper, { id: 9900 + k, shadow: 0.6, alpha: al });
  }
}
// ================================================================== Ablauf
function worldAt(t) { return WELTEN.find(w => t >= w.a && t < w.e) || WELTEN[WELTEN.length - 1]; }

let CANVAS = null;
function renderFrame(ctx, tRaw) {
  const t = Math.floor(tRaw * FPS_DRAW + 1e-6) / FPS_DRAW;
  G.t = t;
  G.boil = Math.floor(tRaw * 6 + 1e-6);
  G.tip = null;
  ctx.setTransform(G.k, 0, 0, G.k, 0, 0);
  ctx.fillStyle = C.cream;
  ctx.fillRect(0, 0, W, H);
  const tr = UEBERGAENGE.find(x => t >= x.a && t < x.e);
  if (tr) tr.fn(ctx, c => tr.A(c, t), c => tr.B(c, t), (t - tr.a) / (tr.e - tr.a), t);
  else worldAt(t).draw(ctx, t);
  // Stimmung: Farben werden matter (0..1)
  const ms = typeof STIMMUNG === 'function' ? STIMMUNG(t) : 0;
  if (ms > 0) {
    ctx.save();
    ctx.globalCompositeOperation = 'saturation'; ctx.globalAlpha = ms;
    ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, W, H);
    ctx.restore();
    flat(ctx, rectPts(0, 0, W, H), '#3A3440', ms * 0.12);
  }
  const ps = presenter(t);
  if (ps) teacher(ctx, ps);
  drawStage(ctx, t);
  if (!G.fast) {
    ctx.save();
    const gp = pattern(ctx, 'grain', TEX.grain);
    gp.setTransform(new DOMMatrix().translate((G.boil % 3) * 37, (G.boil % 2) * 53));
    ctx.fillStyle = gp; ctx.globalAlpha = 0.85; ctx.fillRect(0, 0, W, H);
    ctx.restore();
    const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.0);
    g.addColorStop(0, 'rgba(60,35,20,0)'); g.addColorStop(1, 'rgba(60,35,20,0.28)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
}

// Kapitel-Sprungziele: Beginn des Übergangs vor jeder Szene (sonst kurz vor der Grenze)
function chapterStops() {
  return D.szenen.map((s, i) => {
    if (i === 0) return 0;
    const tr = UEBERGAENGE.find(x => s.start >= x.a && s.start <= x.e);
    return tr ? tr.a : s.start - 0.3;
  });
}
