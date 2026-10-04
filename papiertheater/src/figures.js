/* Figuren und Requisiten aus Papier. Alle Figuren: Ursprung = Fußpunkt, y nach oben negativ. */
'use strict';

// ================================================================== Arm-IK
function ik2(sx, sy, tx, ty, L1, L2, elbowDown = true) {
  let dx = tx - sx, dy = ty - sy;
  let d = Math.hypot(dx, dy);
  const maxd = L1 + L2 - 1;
  if (d > maxd) { dx *= maxd / d; dy *= maxd / d; d = maxd; }
  d = Math.max(d, Math.abs(L1 - L2) + 2);
  const a0 = Math.atan2(dy, dx);
  const th = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const sgn = (dx >= 0) === elbowDown ? 1 : -1;
  const ua = a0 + th * sgn;
  const ex = sx + Math.cos(ua) * L1, ey = sy + Math.sin(ua) * L1;
  const fa = Math.atan2(sy + dy - ey, sx + dx - ex);
  return { ex, ey, hx: ex + Math.cos(fa) * L2, hy: ey + Math.sin(fa) * L2, fa };
}
function limb(ctx, x0, y0, x1, y1, w0, w1, fill, id) {
  const a = Math.atan2(y1 - y0, x1 - x0), nx = -Math.sin(a), ny = Math.cos(a);
  const pts = [[x0 + nx * w0 / 2, y0 + ny * w0 / 2], [x1 + nx * w1 / 2, y1 + ny * w1 / 2],
  ...arcPts(x1, y1, w1 / 2, w1 / 2, a + Math.PI / 2, a - Math.PI / 2, 6),
  [x0 - nx * w0 / 2, y0 - ny * w0 / 2], ...arcPts(x0, y0, w0 / 2, w0 / 2, a - Math.PI / 2, a - Math.PI * 1.5, 6)];
  P(ctx, pts, fill, { id, shadow: 0.6 });
}

// ================================================================== Lehrerin
const TEACH = {
  cardigan: C.petrol, cardiganD: C.petrolD, blouse: C.cream, collar: C.paper, skirt: '#7C4A38',
  tights: '#3C3950', shoes: '#6B3B28',
};
const T_SH = { A: [-66, -402], B: [66, -402] };
const T_L1 = 116, T_L2 = 106;

/* st: {x,y,s, handA,handB: [lx,ly] lokale Ziele (Hand), tip: [x,y] Stiftspitze in Elternkoordinaten,
        look:[dx,dy], mouth, round, blink, serious (0..1), hop, desk(bool: Beine weglassen)} */
function teacher(ctx, st) {
  const s = st.s ?? 1;
  ctx.save();
  ctx.translate(st.x, st.y - (st.hop || 0));
  ctx.rotate(st.lean || 0);
  ctx.scale(s, s);
  const ser = st.serious || 0;
  const id = 900;

  // Ziel der Stifthand (B) aus Stiftspitze berechnen
  let hb = st.handB || [84, -196];
  let crayDir = null;
  if (st.tip) {
    const lx = (st.tip[0] - st.x) / s, ly = (st.tip[1] - st.y + (st.hop || 0)) / s;
    const [sx, sy] = T_SH.B;
    const a = Math.atan2(ly - sy, lx - sx);
    crayDir = a;
    hb = [lx - Math.cos(a) * 30, ly - Math.sin(a) * 30];
  }
  const ha = st.handA || [-84, -196];

  // Haare hinten
  P(ctx, [...arcPts(0, -498, 80, 78, Math.PI * 0.95, Math.PI * 2.05, 20), [78, -452], [70, -428], [40, -436], [-40, -436], [-70, -428], [-78, -452]],
    C.hairD, { id: id + 1 });

  if (!st.desk) {
    // Beine & Schuhe
    P(ctx, [[-34, -130], [-10, -130], [-12, -16], [-32, -16]], TEACH.tights, { id: id + 2, shadow: 0.5 });
    P(ctx, [[10, -130], [34, -130], [32, -16], [12, -16]], TEACH.tights, { id: id + 3, shadow: 0.5 });
    ell(ctx, -26, -11, 25, 11, TEACH.shoes, { id: id + 4 });
    ell(ctx, 26, -11, 25, 11, TEACH.shoes, { id: id + 5 });
    // Rock
    P(ctx, [[-60, -272], [60, -272], [88, -118], [-88, -118]], TEACH.skirt, { id: id + 6 });
    crayon(ctx, [[-30, -250], [-40, -130]], 1, '#5E3528', 2.2, { id: 3 });
    crayon(ctx, [[28, -250], [38, -130]], 1, '#5E3528', 2.2, { id: 4 });
  }

  // Hals
  P(ctx, rectPts(-15, -452, 30, 44), C.skinD, { id: id + 7, shadow: 0 });
  // Oberkörper (Strickjacke)
  const torso = [[-58, -420], [-74, -404], [-78, -380], [-66, -262], [66, -262], [78, -380], [74, -404], [58, -420]];
  P(ctx, torso, TEACH.cardigan, { id: id + 8 });
  // Bluse im V-Ausschnitt
  P(ctx, [[-26, -420], [26, -420], [4, -300], [-4, -300]], TEACH.blouse, { id: id + 9, shadow: 0.4 });
  // Strick-Rippen
  for (let i = 0; i < 5; i++) crayon(ctx, [[-60 + i * 4, -380 + i * 22], [-30 + i * 2, -372 + i * 22]], 1, C.petrolD, 2, { id: 20 + i, alpha: 0.5 });
  crayon(ctx, [[-66, -270], [66, -270]], 1, C.petrolD, 3, { id: 30, alpha: 0.6 });
  // Knöpfe
  for (let i = 0; i < 3; i++) dot(ctx, 12 + i * 2.5, -330 + i * 26, 5, C.mustard);
  // Kragen
  P(ctx, tf(ellPts(0, 0, 22, 13), -16, -418, 1, 0.35), C.collar, { id: id + 10, shadow: 0.5 });
  P(ctx, tf(ellPts(0, 0, 22, 13), 16, -418, 1, -0.35), C.collar, { id: id + 11, shadow: 0.5 });

  // Arm A (Betrachter links)
  const A = ik2(T_SH.A[0], T_SH.A[1], ha[0], ha[1], T_L1, T_L2, true);
  limb(ctx, T_SH.A[0], T_SH.A[1], A.ex, A.ey, 38, 32, TEACH.cardigan, id + 12);
  limb(ctx, A.ex, A.ey, A.hx, A.hy, 32, 26, TEACH.cardigan, id + 13);
  ell(ctx, A.hx + Math.cos(A.fa) * 6, A.hy + Math.sin(A.fa) * 6, 17, 16, C.skin, { id: id + 14, shadow: 0.5 });

  // Kopf
  ell(ctx, 0, -492, 58, 64, C.skin, { id: id + 15 });
  // Wangen
  dot(ctx, -34, -468, 12, C.coral, 0.45 - ser * 0.15);
  dot(ctx, 34, -468, 12, C.coral, 0.45 - ser * 0.15);
  // Augen
  const lx = (st.look ? st.look[0] : 0) * 4, ly = (st.look ? st.look[1] : 0) * 3;
  if (st.blink) {
    crayon(ctx, [[-29, -490], [-15, -490]], 1, C.ink, 3.5);
    crayon(ctx, [[15, -490], [29, -490]], 1, C.ink, 3.5);
  } else {
    dot(ctx, -22 + lx, -490 + ly, 6, C.ink);
    dot(ctx, 22 + lx, -490 + ly, 6, C.ink);
    dot(ctx, -20 + lx, -492 + ly, 1.8, '#fff');
    dot(ctx, 24 + lx, -492 + ly, 1.8, '#fff');
  }
  // Brille
  ctx.save();
  ctx.strokeStyle = '#3A2A2C'; ctx.lineWidth = 3.2;
  ctx.fillStyle = 'rgba(255,255,255,0.12)';
  for (const cx of [-22, 22]) { ctx.beginPath(); ctx.arc(cx, -490, 19, 0, TAU); ctx.fill(); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-4, -492); ctx.quadraticCurveTo(0, -497, 4, -492); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-41, -492); ctx.lineTo(-56, -496); ctx.moveTo(41, -492); ctx.lineTo(56, -496); ctx.stroke();
  ctx.restore();
  // Augenbrauen
  const bi = ser * 5;
  crayon(ctx, smooth([[-38, -516], [-24, -523 + bi * 0.2], [-10, -518 + bi]], 4), 1, C.hairD, 4.2, { id: 40 });
  crayon(ctx, smooth([[10, -518 + bi], [24, -523 + bi * 0.2], [38, -516]], 4), 1, C.hairD, 4.2, { id: 41 });
  // Nase
  crayon(ctx, smooth([[2, -482], [5, -470], [-1, -466]], 4), 1, C.skinD, 3, { id: 42 });
  // Mund
  const m = st.mouth || 0, rd = st.round || 0;
  if (m < 0.07) {
    const smile = 5 * (1 - ser);
    crayon(ctx, smooth([[-11, -451], [0, -451 + smile], [11, -451]], 4), 1, '#8C3440', 3.2, { id: 43 });
  } else {
    const rx = 9 + 5 * (1 - rd) * (0.6 + m * 0.4), ry = 2.5 + 10 * m;
    ctx.save();
    ctx.fillStyle = '#7A2B36';
    ctx.beginPath(); ctx.ellipse(0, -450 + ry * 0.25, rx, ry, 0, 0, TAU); ctx.fill();
    if (ry > 6) { ctx.fillStyle = C.coral; ctx.beginPath(); ctx.ellipse(0, -450 + ry * 0.8, rx * 0.55, ry * 0.3, 0, 0, TAU); ctx.fill(); }
    if (m > 0.45) { ctx.fillStyle = '#fff'; ctx.fillRect(-rx * 0.55, -450 - ry * 0.72, rx * 1.1, ry * 0.28); }
    ctx.restore();
  }
  // Haare vorne (Pony mit Seitenscheitel)
  const fr = [...arcPts(0, -494, 70, 72, Math.PI * 1.0, Math.PI * 2.0, 18), [66, -470], [60, -452], [52, -470], [46, -500], [30, -520], [8, -528],
  [-14, -522], [-38, -508], [-54, -486], [-58, -456], [-66, -470]];
  P(ctx, fr, C.hair, { id: id + 16 });
  crayon(ctx, smooth([[4, -556], [-20, -540], [-44, -512]], 5), 1, C.hairD, 3, { id: 44, alpha: 0.7 });
  crayon(ctx, smooth([[10, -556], [34, -542], [52, -512]], 5), 1, C.hairD, 3, { id: 45, alpha: 0.7 });
  // Haarspange
  P(ctx, tf(rrectPts(-19, -6, 38, 12, 5), 38, -530, 1, -0.5), C.mustard, { id: id + 17, shadow: 0.6 });

  // Arm B mit blauem Wachsmalstift
  const B = ik2(T_SH.B[0], T_SH.B[1], hb[0], hb[1], T_L1, T_L2, true);
  limb(ctx, T_SH.B[0], T_SH.B[1], B.ex, B.ey, 38, 32, TEACH.cardigan, id + 18);
  limb(ctx, B.ex, B.ey, B.hx, B.hy, 32, 26, TEACH.cardigan, id + 19);
  if (st.crayon !== false) {
    const ca = crayDir ?? (B.fa - 0.9);
    const cx = B.hx + Math.cos(B.fa) * 8, cy = B.hy + Math.sin(B.fa) * 8;
    const pts = tf([[-6, -6], [36, -6], [46, 0], [36, 6], [-6, 6]], cx, cy, 1, ca);
    P(ctx, pts, C.crayonBlue, { id: id + 20, shadow: 0.5, rough: 0.5 });
    P(ctx, tf(rectPts(2, -6.5, 20, 13), cx, cy, 1, ca), '#8FB0F0', { id: id + 21, shadow: 0, rough: 0.3 });
  }
  ell(ctx, B.hx + Math.cos(B.fa) * 6, B.hy + Math.sin(B.fa) * 6, 17, 16, C.skin, { id: id + 22, shadow: 0.5 });

  ctx.restore();
}

// ================================================================== Papierpersonen
/* o: {coat, pants, skin, hair, hat, dress, long, armL, armR, lean, face, id, w, h, mustache, beard, legs(bool),
       step (Gehphase), mouth, bag} */
function person(ctx, x, y, s, o = {}) {
  const id = o.id ?? 100;
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s * (o.flip ? -1 : 1), s);
  if (o.lean) ctx.rotate(o.lean);
  const w = o.w ?? 1, hh = o.h ?? 1;
  ctx.scale(w, hh);
  const coat = o.coat ?? C.petrol, pants = o.pants ?? C.navy, skin = o.skin ?? C.skin;
  const st = o.step || 0;
  const coatBottom = o.long ? -40 : -74;

  if (o.legs !== false) {
    if (o.dress) {
      P(ctx, [[-24, -130], [24, -130], [34, -12], [-34, -12]], o.dressColor ?? coat, { id: id + 1, shadow: 0.7 });
      ell(ctx, -10, -6, 9, 5, o.shoes ?? C.ink, { id: id + 2, shadow: 0.3, outline: false });
      ell(ctx, 10, -6, 9, 5, o.shoes ?? C.ink, { id: id + 3, shadow: 0.3, outline: false });
    } else {
      const k = Math.sin(st) * 8;
      P(ctx, [[-14, -84], [-2, -84], [-4 + k, -6], [-15 + k, -6]], pants, { id: id + 1, shadow: 0.6 });
      P(ctx, [[2, -84], [14, -84], [15 - k, -6], [4 - k, -6]], pants, { id: id + 2, shadow: 0.6 });
      ell(ctx, -11 + k, -5, 10, 5.5, o.shoes ?? C.ink, { id: id + 3, shadow: 0.2, outline: false });
      ell(ctx, 11 - k, -5, 10, 5.5, o.shoes ?? C.ink, { id: id + 4, shadow: 0.2, outline: false });
    }
  }
  // Arme hinter dem Körper? nein – Arme vorne, aber Oberarm-Ansatz verdeckt
  // ang: Schulterwinkel (0 = hängend, positiv = nach außen/oben); bend: Ellbogenbeugung
  const arm = (side, ang, bend, n) => {
    const sx = side * 21, sy = -146;
    const a = Math.PI / 2 - side * ang;
    let hx, hy, ha;
    if (!bend) {
      hx = sx + Math.cos(a) * 60; hy = sy + Math.sin(a) * 60; ha = a;
      limb(ctx, sx, sy, hx, hy, 13, 11, o.sleeve ?? coat, id + n);
    } else {
      const ex = sx + Math.cos(a) * 32, ey = sy + Math.sin(a) * 32;
      ha = a - side * bend;
      hx = ex + Math.cos(ha) * 32; hy = ey + Math.sin(ha) * 32;
      limb(ctx, sx, sy, ex, ey, 13, 12, o.sleeve ?? coat, id + n);
      limb(ctx, ex, ey, hx, hy, 12, 11, o.sleeve ?? coat, id + n + 1);
    }
    dot(ctx, hx + Math.cos(ha) * 3, hy + Math.sin(ha) * 3, 7, skin);
    if (o.holds && side === 1) o.holds(ctx, hx, hy, ha);
  };
  // Oberkörper
  const tor = o.dress && !o.coatOverDress
    ? [[-20, -154], [20, -154], [23, -120], [-23, -120]]
    : [[-21, -156], [21, -156], [25, coatBottom], [-25, coatBottom]];
  P(ctx, tor, coat, { id: id + 5, shadow: 0.8 });
  if (o.dress && !o.coatOverDress) P(ctx, [[-22, -128], [22, -128], [24, -118], [-24, -118]], o.belt ?? shade(coat, -0.15), { id: id + 6, shadow: 0, outline: false });
  if (o.shirt) P(ctx, [[-6, -156], [6, -156], [0, -132]], o.shirt, { id: id + 7, shadow: 0, outline: false });
  if (o.buttons) for (let i = 0; i < 4; i++) dot(ctx, 0, -146 + i * 17, 2.4, o.buttons);
  if (o.epaulets) { rect(ctx, -26, -160, 14, 6, o.epaulets, { id: id + 8, shadow: 0 }); rect(ctx, 12, -160, 14, 6, o.epaulets, { id: id + 9, shadow: 0 }); }
  arm(-1, o.armL ?? 0.08, o.bendL || 0, 10);
  arm(1, o.armR ?? 0.08, o.bendR || 0, 12);
  // Hals + Kopf
  P(ctx, rectPts(-6, -166, 12, 14), shade(skin, -0.08), { id: id + 14, shadow: 0, outline: false });
  if (o.hair && o.hairStyle === 'long') P(ctx, [...arcPts(0, -176, 24, 24, Math.PI, TAU, 10), [24, -150], [-24, -150]], o.hair, { id: id + 15, shadow: 0.5 });
  ell(ctx, 0, -176, 20, 21, skin, { id: id + 16, shadow: 0.6 });
  // Gesicht
  const f = o.face || 'neutral';
  if (o.eyes !== false) {
    if (f === 'closed') {
      crayon(ctx, [[-10, -176], [-4, -175]], 1, C.ink, 2);
      crayon(ctx, [[4, -175], [10, -176]], 1, C.ink, 2);
    } else {
      dot(ctx, -7, -177, 2.6, C.ink);
      dot(ctx, 7, -177, 2.6, C.ink);
    }
    dot(ctx, -13, -168, 4, C.coral, 0.4);
    dot(ctx, 13, -168, 4, C.coral, 0.4);
    if (f === 'angry') {
      crayon(ctx, [[-12, -186], [-3, -182]], 1, C.ink, 2.2);
      crayon(ctx, [[12, -186], [3, -182]], 1, C.ink, 2.2);
      ell(ctx, 0, -164, 4, 3, '#7A2B36', { shadow: 0, outline: false, tex: false });
    } else if (f === 'worried') {
      crayon(ctx, [[-11, -183], [-3, -186]], 1, C.ink, 2);
      crayon(ctx, [[11, -183], [3, -186]], 1, C.ink, 2);
      crayon(ctx, smooth([[-5, -163], [0, -165], [5, -163]], 3), 1, '#8C3440', 2.2);
    } else if (f === 'shout') {
      ell(ctx, 0, -163, 4.5, 5, '#7A2B36', { shadow: 0, outline: false, tex: false });
    } else if (f === 'smile') {
      crayon(ctx, smooth([[-6, -165], [0, -161], [6, -165]], 3), 1, '#8C3440', 2.2);
    } else {
      crayon(ctx, [[-4, -164], [4, -164]], 1, '#8C3440', 2.2);
    }
  }
  if (o.mustache) P(ctx, [[-11, -168], [-2, -171], [0, -169], [2, -171], [11, -168], [13, -172], [6, -166], [-6, -166], [-13, -172]], o.mustache, { id: id + 17, shadow: 0, outline: false, tex: false });
  if (o.beard) P(ctx, [...arcPts(0, -170, 18, 16, 0, Math.PI, 8)], o.beard, { id: id + 18, shadow: 0, outline: false });
  // Haare
  if (o.hair && o.hat !== 'kerchief') P(ctx, [...arcPts(0, -178, 21, 22, Math.PI * 1.05, Math.PI * 1.95, 10), [16, -186], [0, -190], [-16, -186]], o.hair, { id: id + 19, shadow: 0.3 });
  hat(ctx, o.hat, o.hatColor, id + 20);
  ctx.restore();
}

function hat(ctx, type, col, id) {
  if (!type || type === 'none') return;
  switch (type) {
    case 'cap':
      ell(ctx, 3, -192, 25, 6, col ?? C.greyD, { id, shadow: 0.4 });
      P(ctx, arcPts(0, -192, 21, 13, Math.PI, TAU, 10), col ?? C.greyD, { id: id + 1, shadow: 0.3 });
      break;
    case 'bowler':
      ell(ctx, 0, -192, 27, 5, col ?? C.ink, { id, shadow: 0.4 });
      P(ctx, arcPts(0, -192, 17, 20, Math.PI, TAU, 10), col ?? C.ink, { id: id + 1, shadow: 0.3 });
      break;
    case 'fez':
      P(ctx, [[-14, -192], [14, -192], [11, -214], [-11, -214]], col ?? C.red, { id, shadow: 0.4 });
      crayon(ctx, [[0, -214], [9, -206], [10, -196]], 1, C.ink, 2);
      break;
    case 'boater':
      ell(ctx, 0, -193, 30, 5.5, col ?? C.mustardL, { id, shadow: 0.4 });
      P(ctx, rectPts(-16, -208, 32, 15), col ?? C.mustardL, { id: id + 1, shadow: 0.2 });
      P(ctx, rectPts(-16, -199, 32, 5), C.navy, { id: id + 2, shadow: 0, outline: false });
      break;
    case 'police':
      P(ctx, [[-19, -190], [19, -190], [16, -214], [-16, -214]], col ?? C.navy, { id, shadow: 0.4 });
      P(ctx, [[-20, -191], [24, -191], [30, -186], [-20, -186]], C.ink, { id: id + 1, shadow: 0.2 });
      dot(ctx, 0, -202, 3.4, C.mustard);
      break;
    case 'officer':
      P(ctx, [[-19, -190], [19, -190], [17, -212], [-17, -212]], col ?? '#6F8FA6', { id, shadow: 0.4 });
      P(ctx, rectPts(-19, -198, 38, 5), C.mustard, { id: id + 1, shadow: 0, outline: false });
      P(ctx, [[-20, -191], [24, -191], [30, -186], [-20, -186]], C.ink, { id: id + 2, shadow: 0.2 });
      break;
    case 'plume': {  // Franz Ferdinand: hoher Hut mit grünem Federbusch
      P(ctx, [[-20, -190], [20, -190], [17, -216], [-17, -216]], col ?? '#2E4A3E', { id, shadow: 0.4 });
      P(ctx, rectPts(-20, -198, 40, 5), C.mustard, { id: id + 1, shadow: 0, outline: false });
      const fb = (k, dx, a, c) => P(ctx, tf([[0, 0], [5, -18], [3, -36], [-2, -44], [-4, -24]], dx, -214, 1, a), c, { id: id + 3 + k, shadow: 0.3, rough: 0.6 });
      fb(0, -8, -0.55, '#3F8A5E'); fb(1, -2, -0.2, '#2F7650'); fb(2, 4, 0.15, '#4FA06C'); fb(3, 9, 0.5, '#3F8A5E'); fb(4, 0, -0.05, '#5DB07A');
      break;
    }
    case 'wide':   // Sophie: breiter heller Hut
      ell(ctx, 0, -192, 36, 8, col ?? C.paper, { id, shadow: 0.5 });
      P(ctx, arcPts(0, -192, 19, 15, Math.PI, TAU, 10), col ?? C.paper, { id: id + 1, shadow: 0.2 });
      P(ctx, rectPts(-19, -198, 38, 5), C.coral, { id: id + 2, shadow: 0, outline: false });
      dot(ctx, 14, -200, 5, C.coralL);
      break;
    case 'kerchief':
      P(ctx, [...arcPts(0, -176, 24, 25, Math.PI * 0.9, Math.PI * 2.1, 12), [20, -150], [-20, -150]], col ?? C.coral, { id, shadow: 0.4 });
      break;
    case 'helmet':
      P(ctx, arcPts(0, -188, 22, 22, Math.PI, TAU, 10), col ?? C.greyD, { id, shadow: 0.4 });
      break;
  }
}

// Vordefinierte Figuren (Aussehen)
const LOOK = {
  ff: { coat: '#9DB8CC', pants: '#1E2A4A', hat: 'plume', mustache: '#5A3A22', epaulets: C.mustard, buttons: C.mustard, sleeve: '#9DB8CC', hair: '#5A3A22' },
  sophie: { coat: C.paper, dress: true, dressColor: C.paper, hat: 'wide', hair: '#5A3A22', belt: C.coralL, sleeve: C.paper },
  potiorek: { coat: '#7E9DB4', pants: C.navy, hat: 'officer', mustache: '#EDE6DA', epaulets: C.mustard, buttons: C.mustard },
  police: { coat: C.navy, pants: C.navy, hat: 'police', mustache: '#3A2A22', buttons: C.mustard },
  princip: { coat: '#2E2D3A', pants: '#2E2D3A', hat: 'none', hair: '#2A1E18', shirt: C.cream, w: 0.86 },
  cabrinovic: { coat: '#4A3E3A', pants: '#2F2A2A', hat: 'none', hair: '#2A1E18', shirt: C.cream, w: 0.9 },
  consp: { coat: '#3B3B48', pants: '#2F2E36', hat: 'none', hair: '#2A1E18', shirt: C.cream, w: 0.9 },
  mayor: { coat: C.ink, pants: C.ink, hat: 'fez', mustache: '#EDE6DA', shirt: C.paper },
  doctor: { coat: C.paper, pants: C.greyD, hat: 'none', hair: '#6B6560', mustache: '#6B6560' },
  driver: { coat: C.greyD, pants: C.ink, hat: 'cap', hatColor: C.ink },
};

// Zuschauer-Generator (deterministisch)
const CROWD_COATS = [C.petrol, C.coralD, C.mustardD, C.kraftD, C.greyD, C.navy, C.rust, C.petrolL, '#6D5A7E', C.woodD];
const CROWD_HATS = ['fez', 'fez', 'cap', 'bowler', 'none', 'boater', 'kerchief', 'none', 'fez', 'bowler'];
function crowdLook(i) {
  const r = k => hash(i, k, 77);
  const woman = r(1) < 0.35;
  return {
    coat: CROWD_COATS[Math.floor(r(2) * CROWD_COATS.length)],
    pants: r(3) < 0.5 ? C.ink : C.navy,
    skin: r(4) < 0.5 ? C.skin : C.skinD,
    hair: r(5) < 0.6 ? '#3A2618' : '#6B4A2B',
    hat: woman ? (r(6) < 0.6 ? 'kerchief' : 'wide') : CROWD_HATS[Math.floor(r(6) * CROWD_HATS.length)],
    hatColor: woman ? [C.coral, C.mustardL, C.petrolL, C.paper][Math.floor(r(7) * 4)] : undefined,
    dress: woman, dressColor: [C.coralL, C.mustardL, C.petrolL, C.cream, '#B7A7CF'][Math.floor(r(8) * 5)],
    mustache: !woman && r(9) < 0.5 ? '#3A2618' : undefined,
    h: 0.9 + r(10) * 0.2, w: 0.9 + r(11) * 0.2,
    id: 2000 + i * 40,
  };
}

// ================================================================== Oldtimer (Seitenansicht, fährt nach rechts)
/* o: {occ: [[look, dx]...], rot (Radrotation), color, flag, top(bool Verdeck zurück), id} */
function car(ctx, x, y, s, o = {}) {
  const id = o.id ?? 3000;
  const body = o.color ?? '#23323A';
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  // Rückenlehnen
  P(ctx, rrectPts(-150, -142, 46, 60, 10), '#6E2F2E', { id: id + 1, shadow: 0.5 });
  P(ctx, rrectPts(-20, -126, 36, 44, 8), '#6E2F2E', { id: id + 2, shadow: 0.5 });
  // Insassen
  (o.occ || []).forEach(([lk, dx, extra], i) => {
    person(ctx, dx, -2, 0.78, Object.assign({ id: id + 100 + i * 40, legs: false }, lk, extra || {}));
  });
  // Karosserie
  const b = [[-164, -40], [156, -40], [162, -58], [156, -80], [96, -82], [70, -84], [60, -100], [-60, -102], [-128, -106], [-156, -100], [-166, -76]];
  P(ctx, b, body, { id: id + 3 });
  // Zierlinie
  crayon(ctx, [[-150, -88], [52, -86]], 1, C.mustard, 3, { id: 51 });
  crayon(ctx, [[68, -76], [150, -74]], 1, shade(body, 0.25), 2.5, { id: 52 });
  // Motorhaube Lüftungsschlitze
  for (let i = 0; i < 5; i++) crayon(ctx, [[100 + i * 10, -76], [100 + i * 10, -52]], 1, shade(body, 0.3), 2, { id: 53 + i });
  // Kühler (Messing)
  P(ctx, rectPts(152, -86, 12, 48), C.mustard, { id: id + 4, shadow: 0.5 });
  // Lampen
  ell(ctx, 150, -96, 9, 9, C.mustardL, { id: id + 5, shadow: 0.4 });
  ell(ctx, 58, -106, 6, 6, C.mustardL, { id: id + 6, shadow: 0.3 });
  // Windschutzscheibe
  crayon(ctx, [[62, -100], [70, -150]], 1, C.ink, 3.5);
  flat(ctx, [[64, -104], [72, -148], [90, -146], [84, -102]], '#CFE6EC', 0.45);
  crayon(ctx, [[70, -150], [90, -147], [84, -102]], 1, C.ink, 2.5);
  // Lenkrad
  crayon(ctx, [[40, -100], [50, -118]], 1, C.ink, 3);
  ell(ctx, 50, -118, 11, 4, C.ink, { shadow: 0, outline: false, tex: false });
  // zurückgeklapptes Verdeck
  if (o.top !== false) {
    P(ctx, [[-172, -104], [-120, -110], [-112, -126], [-150, -140], [-178, -126]], '#2A2522', { id: id + 7 });
    for (let i = 0; i < 3; i++) crayon(ctx, [[-168 + i * 16, -108], [-160 + i * 14, -132]], 1, '#4A403A', 2.5, { id: 60 + i });
  }
  // Kotflügel & Trittbrett
  P(ctx, [...arcPts(104, -34, 46, 38, Math.PI, TAU, 10), [150, -30], [58, -30]], shade(body, -0.25), { id: id + 8, shadow: 0.6 });
  P(ctx, [...arcPts(-96, -34, 46, 38, Math.PI, TAU, 10), [-50, -30], [-142, -30]], shade(body, -0.25), { id: id + 9, shadow: 0.6 });
  P(ctx, rectPts(-52, -40, 112, 8), shade(body, -0.3), { id: id + 10, shadow: 0.4 });
  // Räder
  for (const wx of [-96, 104]) wheel(ctx, wx, -32, 33, o.rot || 0, id + (wx > 0 ? 11 : 12));
  // Fähnchen (schwarz-gelb)
  if (o.flag !== false) {
    crayon(ctx, [[144, -84], [146, -132]], 1, C.ink, 2.5);
    const wv = Math.sin(G.boil * 1.7) * 3;
    P(ctx, [[146, -132], [172, -126 + wv], [146, -118]], C.mustard, { id: id + 13, shadow: 0.4, rough: 0.5 });
    flat(ctx, [[146, -125], [164, -125 + wv * 0.6], [146, -121]], C.ink, 0.9);
  }
  ctx.restore();
}
function wheel(ctx, x, y, r, rot, id) {
  ell(ctx, x, y, r, r, C.ink, { id, shadow: 0.8 });
  ell(ctx, x, y, r * 0.72, r * 0.72, C.creamD, { id: id + 1, shadow: 0, outline: false });
  for (let i = 0; i < 10; i++) {
    const a = rot + i / 10 * TAU;
    crayon(ctx, [[x, y], [x + Math.cos(a) * r * 0.7, y + Math.sin(a) * r * 0.7]], 1, C.woodD, 2.2, { id: 70 + i });
  }
  dot(ctx, x, y, r * 0.2, C.mustard);
}

// ================================================================== Gebäude
/* Fassade im österreichischen Stil. o: {color, trim, roof: 'tile'|'flat'|'mansard', floors, id, shop, door, shutters (0..1)} */
function facade(ctx, x, yb, w, h, o = {}) {
  const id = o.id ?? 500;
  const col = o.color ?? C.cream, trim = o.trim ?? C.paper;
  const fl = o.floors ?? Math.max(2, Math.round(h / 110));
  // Dach
  if (o.roof === 'tile' || o.roof === undefined) P(ctx, [[x - 10, yb - h + 2], [x + w + 10, yb - h + 2], [x + w - 16, yb - h - 44], [x + 16, yb - h - 44]], o.roofColor ?? C.coralD, { id: id + 1 });
  else if (o.roof === 'mansard') P(ctx, [[x - 8, yb - h + 2], [x + w + 8, yb - h + 2], [x + w - 6, yb - h - 30], [x + w - 30, yb - h - 56], [x + 30, yb - h - 56], [x + 6, yb - h - 30]], o.roofColor ?? C.violet, { id: id + 1 });
  P(ctx, rectPts(x, yb - h, w, h), col, { id: id + 2 });
  // Gesims
  P(ctx, rectPts(x - 8, yb - h - 4, w + 16, 16), trim, { id: id + 3, shadow: 0.6 });
  const fh = (h - 20) / fl;
  const cols = Math.max(2, Math.round(w / 78));
  const cw = w / cols;
  for (let f = 0; f < fl; f++) {
    const fy = yb - h + 20 + f * fh;
    if (f > 0) crayon(ctx, [[x + 4, fy - 4], [x + w - 4, fy - 4]], 1, shade(col, -0.18), 3, { id: id + f });
    for (let c = 0; c < cols; c++) {
      const wx = x + c * cw + cw * 0.28, ww = cw * 0.44, wy = fy + fh * 0.2, wh = fh * 0.58;
      if (f === fl - 1 && (o.shop || o.door)) continue;
      window_(ctx, wx, wy, ww, wh, id + 10 + f * 10 + c, o.arch, o.winColor);
    }
  }
  // Erdgeschoss
  const gy = yb - fh + 6;
  if (o.shop) shopFront(ctx, x + 10, gy, w - 20, fh - 6, o.shop, id + 200, o.shutters || 0, o.torn || 0);
  else if (o.door) {
    P(ctx, [...rectPts(x + w / 2 - 22, gy + 8, 44, fh - 14)], C.woodD, { id: id + 190, shadow: 0.5 });
    for (let c = 0; c < cols; c++) {
      const wx = x + c * cw + cw * 0.28;
      if (Math.abs(wx + cw * 0.22 - (x + w / 2)) < 40) continue;
      window_(ctx, wx, gy + 12, cw * 0.44, fh * 0.5, id + 180 + c, o.arch, o.winColor);
    }
  }
}
function window_(ctx, x, y, w, h, id, arch, winColor) {
  const glass = winColor ?? C.petrolD;
  if (arch) {
    const pts = [[x, y + h], [x, y + w / 2], ...arcPts(x + w / 2, y + w / 2, w / 2, w / 2, Math.PI, TAU, 8), [x + w, y + h]];
    P(ctx, pts, glass, { id, shadow: 0.35, ow: 0.8 });
  } else {
    P(ctx, rectPts(x, y, w, h), glass, { id, shadow: 0.35, ow: 0.8 });
  }
  crayon(ctx, [[x + w / 2, y + 2], [x + w / 2, y + h - 2]], 1, C.cream, 2, { id: id + 1, alpha: 0.7 });
  crayon(ctx, [[x + 2, y + h * 0.45], [x + w - 2, y + h * 0.45]], 1, C.cream, 2, { id: id + 2, alpha: 0.7 });
}
function shopFront(ctx, x, y, w, h, kind, id, shutters, torn) {
  // Markise
  const n = 6;
  for (let i = 0; i < n; i++) {
    P(ctx, [[x + i * w / n, y], [x + (i + 1) * w / n, y], [x + (i + 1) * w / n + 6, y + 30], [x + i * w / n + 6, y + 30]], i % 2 ? C.cream : C.coral, { id: id + i, shadow: i === 0 ? 0.8 : 0 });
  }
  P(ctx, rectPts(x + 8, y + 36, w - 16, h - 40), C.petrolD, { id: id + 10, shadow: 0.4 });
  // Auslage
  const R = mulberry(id);
  const goods = [C.mustard, C.coral, C.red, C.greenD, C.cream, C.petrolL];
  if (torn < 1) {
    for (let i = 0; i < 14; i++) {
      const gx = x + 20 + R() * (w - 40), gy = y + h - 14 - R() * 30;
      dot(ctx, gx, gy, 5 + R() * 5, goods[Math.floor(R() * goods.length)], 1 - torn);
    }
    // Stoffbahnen
    P(ctx, rectPts(x + 20, y + 46, (w - 40) * 0.35, h * 0.35), C.mustardL, { id: id + 11, shadow: 0.3, alpha: 1 - torn });
    P(ctx, rectPts(x + w * 0.55, y + 46, (w - 40) * 0.35, h * 0.35), C.coralL, { id: id + 12, shadow: 0.3, alpha: 1 - torn });
  }
  if (torn > 0) {
    // zerrissene Papierauslage: Fetzen am Boden
    for (let i = 0; i < 7; i++) {
      const fx = x + 10 + (i / 7) * w + hs(id, i) * 10, fy = y + h + 18 + hash(id, i + 9) * 16;
      const sz = 10 + hash(id, i + 20) * 14;
      pop(ctx, fx, fy, seg(torn, i * 0.08, i * 0.08 + 0.4), () =>
        P(ctx, tf([[-sz, -sz * 0.4], [sz * 0.6, -sz * 0.7], [sz, sz * 0.3], [0, sz * 0.5], [-sz * 0.7, sz * 0.3]], fx, fy, 1, i), [C.mustardL, C.coralL, C.cream][i % 3], { id: id + 30 + i, shadow: 0.4 }));
    }
  }
  // Rollläden
  if (shutters > 0) {
    const sh = (h - 36) * shutters;
    P(ctx, rectPts(x + 4, y + 32, w - 8, sh), C.kraftD, { id: id + 20, shadow: 0.8 });
    for (let i = 1; i < 8; i++) {
      const ly = y + 32 + i * 16;
      if (ly < y + 32 + sh - 4) crayon(ctx, [[x + 8, ly], [x + w - 8, ly]], 1, C.woodD, 2.5, { id: id + 21 + i });
    }
  }
}

// Osmanisches Wohnhaus mit Erker und weitem Dach
function ottomanHouse(ctx, x, yb, w, h, id = 700, col = C.paper) {
  P(ctx, [[x - 24, yb - h + 6], [x + w + 24, yb - h + 6], [x + w * 0.62, yb - h - 46], [x + w * 0.38, yb - h - 46]], C.rust, { id: id + 1 });
  P(ctx, rectPts(x + 8, yb - h * 0.52, w - 16, h * 0.52), col, { id: id + 2 });
  P(ctx, rectPts(x - 4, yb - h, w + 8, h * 0.5), shade(col, -0.04), { id: id + 3 });
  crayon(ctx, [[x - 4, yb - h * 0.5], [x + w + 4, yb - h * 0.5]], 1, C.woodD, 5, { id: id + 4 });
  crayon(ctx, [[x - 2, yb - h + 2], [x - 2, yb - h * 0.5]], 1, C.woodD, 3, { id: id + 5 });
  crayon(ctx, [[x + w + 2, yb - h + 2], [x + w + 2, yb - h * 0.5]], 1, C.woodD, 3, { id: id + 6 });
  const n = Math.max(2, Math.round(w / 40));
  for (let i = 0; i < n; i++) {
    const wx = x + 6 + i * (w - 12) / n + 6;
    P(ctx, rectPts(wx, yb - h + 16, (w - 12) / n - 12, h * 0.26), C.woodD, { id: id + 10 + i, shadow: 0.3, ow: 0.7 });
    crayon(ctx, [[wx + 2, yb - h + 22], [wx + (w - 12) / n - 14, yb - h + 16 + h * 0.24]], 1, C.kraftL, 1.5, { id: id + 20 + i, alpha: 0.6 });
  }
  P(ctx, rectPts(x + w / 2 - 12, yb - h * 0.36, 24, h * 0.36), C.woodD, { id: id + 30, shadow: 0.3 });
}

function minaret(ctx, x, yb, h, id = 800) {
  P(ctx, rectPts(x - 10, yb - h, 20, h), C.paper, { id });
  P(ctx, rectPts(x - 15, yb - h * 0.72, 30, 8), C.creamD, { id: id + 1, shadow: 0.5 });
  P(ctx, [[x - 11, yb - h], [x + 11, yb - h], [x, yb - h - 46]], C.greyD, { id: id + 2 });
  crayon(ctx, [[x, yb - h - 46], [x, yb - h - 58]], 1, C.mustard, 2.5);
}
function mosque(ctx, x, yb, w, id = 820) {
  P(ctx, rectPts(x, yb - w * 0.55, w, w * 0.55), C.paper, { id });
  P(ctx, [...arcPts(x + w / 2, yb - w * 0.55, w * 0.36, w * 0.34, Math.PI, TAU, 14)], C.greyD, { id: id + 1 });
  crayon(ctx, [[x + w / 2, yb - w * 0.89], [x + w / 2, yb - w * 0.98]], 1, C.mustard, 2.5);
  for (let i = 0; i < 3; i++) window_(ctx, x + w * (0.18 + i * 0.25), yb - w * 0.42, w * 0.13, w * 0.24, id + 5 + i * 3, true, C.petrolD);
}

function tree(ctx, x, yb, s = 1, id = 850, col = C.petrolL, kind = 'round') {
  P(ctx, rectPts(x - 6 * s, yb - 60 * s, 12 * s, 60 * s), C.woodD, { id, shadow: 0.5 });
  if (kind === 'poplar') P(ctx, ellPts(x, yb - 120 * s, 26 * s, 80 * s), col, { id: id + 1 });
  else {
    ell(ctx, x - 16 * s, yb - 78 * s, 32 * s, 28 * s, shade(col, -0.1), { id: id + 1 });
    ell(ctx, x + 16 * s, yb - 82 * s, 30 * s, 28 * s, col, { id: id + 2 });
    ell(ctx, x, yb - 104 * s, 30 * s, 27 * s, shade(col, 0.08), { id: id + 3 });
  }
}
function cloud(ctx, x, y, s = 1, id = 870, col = C.paper) {
  P(ctx, [...arcPts(x - 40 * s, y, 36 * s, 26 * s, Math.PI * 0.5, Math.PI * 1.5, 8), ...arcPts(x, y - 16 * s, 40 * s, 32 * s, Math.PI, TAU, 10),
  ...arcPts(x + 44 * s, y, 32 * s, 24 * s, Math.PI * 1.5, Math.PI * 2.5, 8)], col, { id, shadow: 0.5 });
}
function bird(ctx, x, y, s, flap) {
  crayon(ctx, [[x - 14 * s, y - 6 * s * flap], [x, y], [x + 14 * s, y - 6 * s * flap]], 1, C.ink, 2.4 * s);
}
function hill(ctx, pts, col, id) { P(ctx, pts, col, { id, shadow: 0.7 }); }

// Brücke mit Bögen (Seitenansicht). yTop = Fahrbahn, yWater = Wasserlinie
function bridge(ctx, x, yTop, w, yWater, id = 880, col = C.creamD, arches = 3) {
  const pts = [[x - 20, yTop - 10], [x + w + 20, yTop - 10], [x + w + 30, yWater + 10], [x - 30, yWater + 10]];
  ctx.save();
  P(ctx, pts, col, { id });
  const aw = w / arches;
  for (let i = 0; i < arches; i++) {
    const cx = x + aw * (i + 0.5), rx = aw * 0.38, ry = (yWater - yTop) * 0.65;
    P(ctx, [[cx - rx, yWater + 10], ...arcPts(cx, yWater + 10, rx, ry, Math.PI, TAU, 10), [cx + rx, yWater + 10]], C.waterD, { id: id + 1 + i, shadow: 0, outline: false });
    if (i < arches - 1) ell(ctx, x + aw * (i + 1), yTop + (yWater - yTop) * 0.35, aw * 0.08, aw * 0.08, C.waterD, { id: id + 10 + i, shadow: 0, outline: false });
  }
  crayon(ctx, [[x - 20, yTop - 4], [x + w + 20, yTop - 4]], 1, shade(col, -0.25), 4);
  ctx.restore();
}

// Rathaus (Vijećnica): gestreifte Fassade, Hufeisenbögen, Zinnen
function vijecnicaFacade(ctx, x, yb, w, h, id = 1100) {
  const stripes = 16;
  P(ctx, rectPts(x, yb - h, w, h), C.mustardL, { id });
  ctx.save();
  pathPts(ctx, rectPts(x, yb - h, w, h)); ctx.clip();
  for (let i = 0; i < stripes; i++) if (i % 2) flat(ctx, rectPts(x, yb - h + i * h / stripes, w, h / stripes), C.coralL, 0.85);
  ctx.restore();
  // Zinnen
  const mer = Math.round(w / 36);
  for (let i = 0; i < mer; i++) P(ctx, [[x + i * w / mer + 6, yb - h], [x + (i + 1) * w / mer - 6, yb - h], [x + (i + 0.5) * w / mer, yb - h - 22]], C.coralD, { id: id + 2 + i, shadow: 0.4, ow: 0.6 });
  // Fenster in drei Reihen
  const cols = Math.max(3, Math.round(w / 90));
  for (let r = 0; r < 3; r++) for (let c = 0; c < cols; c++) {
    const cw = w / cols;
    const wx = x + c * cw + cw * 0.22, wy = yb - h + 30 + r * (h - 40) / 3;
    if (r === 2 && Math.abs(c - (cols - 1) / 2) < 0.6) continue;
    horseshoe(ctx, wx, wy, cw * 0.56, (h - 40) / 3 * 0.72, id + 40 + r * 20 + c);
  }
  // Portal
  horseshoe(ctx, x + w / 2 - 48, yb - (h - 40) / 3 + 4, 96, (h - 40) / 3 - 4, id + 99, C.woodD);
}
function horseshoe(ctx, x, y, w, h, id, col = C.petrolD) {
  const r = w / 2;
  const pts = [[x + r * 0.15, y + h], [x + r * 0.15, y + r * 1.1], ...arcPts(x + r, y + r, r, r, Math.PI * 0.8, Math.PI * 2.2, 14), [x + w - r * 0.15, y + r * 1.1], [x + w - r * 0.15, y + h]];
  P(ctx, pts, col, { id, shadow: 0.4, ow: 0.8 });
}

// Konak (Amtssitz des Landeschefs): gelber Bau mit weißen Fensterrahmen
function konakFacade(ctx, x, yb, w, h, id = 1300) {
  P(ctx, [[x - 12, yb - h + 2], [x + w + 12, yb - h + 2], [x + w - 30, yb - h - 60], [x + 30, yb - h - 60]], C.violet, { id: id + 1 });
  P(ctx, rectPts(x, yb - h, w, h), C.mustard, { id: id + 2 });
  P(ctx, rectPts(x - 8, yb - h - 4, w + 16, 14), C.paper, { id: id + 3, shadow: 0.5 });
  const cols = Math.round(w / 80);
  for (let r = 0; r < 2; r++) for (let c = 0; c < cols; c++) {
    const cw = w / cols, wx = x + c * cw + cw * 0.3, wy = yb - h + 34 + r * h * 0.45;
    if (r === 1 && Math.abs(c - (cols - 1) / 2) < 0.6) continue;
    P(ctx, rectPts(wx - 5, wy - 5, cw * 0.4 + 10, h * 0.3 + 10), C.paper, { id: id + 10 + r * 20 + c, shadow: 0.3, ow: 0.5 });
    P(ctx, rectPts(wx, wy, cw * 0.4, h * 0.3), C.petrolD, { id: id + 50 + r * 20 + c, shadow: 0, outline: false });
  }
  P(ctx, [[x + w / 2 - 36, yb], [x + w / 2 - 36, yb - h * 0.34], ...arcPts(x + w / 2, yb - h * 0.34, 36, 30, Math.PI, TAU, 8), [x + w / 2 + 36, yb]], C.woodD, { id: id + 90, shadow: 0.5 });
}

// Krankenhaus-Symbol (kleines Haus mit rotem Kreuz)
function hospitalIcon(ctx, x, y, s, prog, id = 1400) {
  const pts = [[-50, 40], [-50, -20], [0, -58], [50, -20], [50, 40], [-50, 40]].map(([a, b]) => [x + a * s, y + b * s]);
  crayon(ctx, pts, prog, C.crayonBlue, 6);
  if (prog > 0.8) {
    const q = seg(prog, 0.8, 1);
    pop(ctx, x, y + 6 * s, q, () => {
      P(ctx, rectPts(x - 22 * s, y - 16 * s, 44 * s, 44 * s), C.paper, { id, shadow: 0.6 });
      P(ctx, rectPts(x - 6 * s, y - 10 * s, 12 * s, 32 * s), C.red, { id: id + 1, shadow: 0, outline: false });
      P(ctx, rectPts(x - 16 * s, y, 32 * s, 12 * s), C.red, { id: id + 2, shadow: 0, outline: false });
    });
  }
}

// Schwarze Hand (Symbol des Geheimbunds)
function blackHand(ctx, x, y, s, id = 1500) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  const palm = [[-40, 60], [-46, 0], [-40, -30], [40, -30], [44, 10], [36, 60]];
  P(ctx, palm, C.ink, { id, shadow: 1.2 });
  const fing = [[-34, -30, 14, 62, -0.12], [-14, -30, 14, 78, -0.04], [6, -30, 14, 80, 0.03], [26, -28, 13, 66, 0.1]];
  fing.forEach(([fx, fy, fw, fl, a], i) => P(ctx, tf(rrectPts(-fw / 2, -fl, fw, fl + 8, fw / 2), fx + fw / 2, fy, 1, a), C.ink, { id: id + 1 + i, shadow: 0.8 }));
  P(ctx, tf(rrectPts(-7, -48, 14, 52, 7), -44, 10, 1, -0.9), C.ink, { id: id + 6, shadow: 0.8 });
  ctx.restore();
}

// Telegrafenapparat (Morseschreiber)
function telegraph(ctx, x, y, s, t, id = 1600) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  P(ctx, rrectPts(-260, -40, 520, 60, 10), C.wood, { id });
  P(ctx, rrectPts(-250, -60, 500, 28, 8), C.woodL, { id: id + 1, shadow: 0.6 });
  // Papierrolle
  ell(ctx, -180, -150, 62, 62, C.paper, { id: id + 2 });
  ell(ctx, -180, -150, 20, 20, C.mustardD, { id: id + 3, shadow: 0.3 });
  P(ctx, rectPts(-190, -100, 20, 50), C.mustardD, { id: id + 4, shadow: 0.5 });
  // Laufwerk
  P(ctx, rrectPts(-60, -190, 170, 132, 14), C.mustard, { id: id + 5 });
  const rot = t * 3;
  for (let i = 0; i < 2; i++) {
    const gx = -20 + i * 90, gy = -130;
    ell(ctx, gx, gy, 30, 30, C.mustardD, { id: id + 6 + i, shadow: 0.4 });
    for (let k = 0; k < 6; k++) { const a = rot * (i ? -1 : 1) + k / 6 * TAU; crayon(ctx, [[gx, gy], [gx + Math.cos(a) * 24, gy + Math.sin(a) * 24]], 1, C.woodD, 3); }
  }
  // Taste
  const press = Math.sin(t * 17) > 0.3 ? 1 : 0;
  P(ctx, rectPts(150, -80, 90, 20), C.greyD, { id: id + 9, shadow: 0.5 });
  P(ctx, tf(rrectPts(0, -8, 110, 16, 6), 140, -96 + press * 6, 1, -0.08 + press * 0.06), C.mustardD, { id: id + 10, shadow: 0.6 });
  ell(ctx, 244, -104 + press * 10, 16, 10, C.ink, { id: id + 11, shadow: 0.6 });
  ctx.restore();
}

// Papierstreifen (Telegrafenband) entlang Polylinie mit Morsezeichen
function tape(ctx, pts, prog, id = 1700, marks = true) {
  const L = polyLen(pts);
  const d = L[L.length - 1] * clamp(prog);
  const out = [];
  for (let s = 0; s <= d; s += 12) out.push(polyAt(pts, L, s));
  if (out.length < 2) return;
  ctx.save();
  ctx.lineCap = 'butt'; ctx.lineJoin = 'round';
  ctx.strokeStyle = 'rgba(55,32,18,0.2)'; ctx.lineWidth = 26;
  pathPts(ctx, out.map(([x, y]) => [x + 3, y + 5]), false); ctx.stroke();
  ctx.strokeStyle = C.paper; ctx.lineWidth = 24;
  pathPts(ctx, out, false); ctx.stroke();
  if (marks) {
    ctx.strokeStyle = C.ink; ctx.lineWidth = 3.5; ctx.lineCap = 'round';
    for (let s = 20, k = 0; s < d - 10; k++) {
      const len = hash(id, k) < 0.4 ? 14 : 2;
      const a = polyAt(pts, L, s), b = polyAt(pts, L, s + len);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
      s += len + 10 + (hash(id, k + 50) < 0.3 ? 16 : 0);
    }
  }
  ctx.restore();
}

// Unbeschriebenes Telegramm (gefalteter Umschlag)
function telegram(ctx, x, y, s, rot, id) {
  const pts = tf([[-30, -20], [30, -20], [30, 20], [-30, 20]], x, y, s, rot);
  P(ctx, pts, C.paper, { id, shadow: 1.2 });
  crayon(ctx, tf([[-30, -20], [0, 4], [30, -20]], x, y, s, rot), 1, C.kraftD, 2.2 * s);
}

// Kalender (Abreißkalender) – ohne Zahlen, ein Tag markiert
function calendarPage(ctx, x, y, w, h, id, mark = -1, markProg = 1) {
  P(ctx, rectPts(x, y, w, h), C.paper, { id, shadow: 0.8 });
  P(ctx, rectPts(x, y, w, h * 0.16), C.coral, { id: id + 1, shadow: 0, outline: false });
  const cols = 7, rows = 5;
  const gw = (w - 24) / cols, gh = (h * 0.84 - 20) / rows;
  ctx.save();
  ctx.strokeStyle = 'rgba(120,90,60,0.35)'; ctx.lineWidth = 1.5;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) ctx.strokeRect(x + 12 + c * gw, y + h * 0.16 + 10 + r * gh, gw - 4, gh - 4);
  ctx.restore();
  if (mark >= 0) {
    const c = mark % cols, r = Math.floor(mark / cols);
    const cx = x + 12 + c * gw + gw / 2 - 2, cy = y + h * 0.16 + 10 + r * gh + gh / 2 - 2;
    crayon(ctx, smooth(ellPts(cx, cy, gw * 0.62, gh * 0.62, 10, -1).concat([[cx + gw * 0.5, cy - gh * 0.7]]), 4), markProg, C.red, 4);
  }
}

// Bilderrahmen mit Porträt (FF oder Sophie)
function portrait(ctx, x, y, s, who, id, ribbon = 1) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  P(ctx, rectPts(-80, -100, 160, 200), C.woodD, { id, shadow: 1.3 });
  P(ctx, rectPts(-66, -86, 132, 172), C.creamD, { id: id + 1, shadow: 0, outline: false });
  P(ctx, ellPts(0, 0, 56, 76), C.cream, { id: id + 2, shadow: 0.3 });
  ctx.save();
  pathPts(ctx, ellPts(0, 0, 56, 76)); ctx.clip();
  const lk = who === 'ff' ? LOOK.ff : LOOK.sophie;
  person(ctx, 0, 228, 1.3, Object.assign({ id: id + 10, legs: false, armL: 0, armR: 0 }, lk));
  ctx.restore();
  if (ribbon > 0) {
    ctx.globalAlpha *= ribbon;
    P(ctx, [[34, -100], [80, -100], [80, -54]], C.ink, { id: id + 5, shadow: 0.5, outline: false });
  }
  ctx.restore();
}

// Schreibtisch (Vorderansicht)
function desk(ctx, x, y, w, h, id = 1800) {
  P(ctx, rectPts(x, y, w, 26), C.woodL, { id, shadow: 1.1 });
  P(ctx, rectPts(x + 14, y + 22, w - 28, h - 22), C.wood, { id: id + 1 });
  P(ctx, rectPts(x + 30, y + 44, w * 0.36, h * 0.28), C.woodL, { id: id + 2, shadow: 0.4 });
  dot(ctx, x + 30 + w * 0.18, y + 44 + h * 0.14, 5, C.mustard);
  P(ctx, rectPts(x + w - 30 - w * 0.36, y + 44, w * 0.36, h * 0.28), C.woodL, { id: id + 3, shadow: 0.4 });
  dot(ctx, x + w - 30 - w * 0.18, y + 44 + h * 0.14, 5, C.mustard);
  for (let i = 0; i < 3; i++) crayon(ctx, [[x + 30, y + h * 0.55 + i * 18], [x + w - 30, y + h * 0.55 + i * 18]], 1, C.woodD, 2.5, { id: id + 10 + i, alpha: 0.5 });
}

// Staffelei-Tafel (Papierbogen auf Holzgestell)
function easel(ctx, x, y, w, h, id = 1850) {
  crayon(ctx, [[x + w * 0.2, y + h + 150], [x + w * 0.32, y - 20]], 1, C.woodD, 14);
  crayon(ctx, [[x + w * 0.8, y + h + 150], [x + w * 0.68, y - 20]], 1, C.woodD, 14);
  P(ctx, rectPts(x - 16, y - 16, w + 32, h + 32), C.kraft, { id, shadow: 1.2 });
  P(ctx, rectPts(x, y, w, h), C.paper, { id: id + 1, shadow: 0.4 });
  P(ctx, rectPts(x + w * 0.1, y + h + 12, w * 0.8, 18), C.wood, { id: id + 2, shadow: 0.8 });
}

// kleine Papierbombe
function bomb(ctx, x, y, s, id = 1900) {
  ell(ctx, x, y, 12 * s, 12 * s, C.ink, { id, shadow: 0.8 });
  crayon(ctx, [[x + 6 * s, y - 8 * s], [x + 12 * s, y - 16 * s]], 1, C.greyL, 2.5 * s);
}

// graue gezackte Papierwolke
function smokeCloud(ctx, x, y, s, p, id = 1950) {
  if (p <= 0) return;
  const n = 18;
  const pts = [];
  for (let i = 0; i < n; i++) {
    const a = i / n * TAU;
    const r = (i % 2 ? 0.62 : 1) * (0.85 + hash(id, i) * 0.3);
    pts.push([x + Math.cos(a) * r * 120 * s, y + Math.sin(a) * r * 90 * s]);
  }
  P(ctx, pts, C.greyL, { id, shadow: 1 });
  const inner = pts.map(([px, py]) => [x + (px - x) * 0.6, y + (py - y) * 0.6 - 8 * s]);
  P(ctx, inner, C.grey, { id: id + 1, shadow: 0.4 });
}

// Papierstreifen unter Spannung zwischen zwei Punkten
function tensionStrip(ctx, a, b, amp, phase, col, id, w = 18) {
  const n = 16, pts1 = [], pts2 = [];
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), nx = -dy / L, ny = dx / L;
  for (let i = 0; i <= n; i++) {
    const f = i / n;
    const off = Math.sin(f * Math.PI) * Math.sin(phase + f * 9) * amp;
    const zig = (i % 2 ? 1 : -1) * 3;
    pts1.push([a[0] + dx * f + nx * (off + w / 2 + zig), a[1] + dy * f + ny * (off + w / 2 + zig)]);
    pts2.unshift([a[0] + dx * f + nx * (off - w / 2 + zig), a[1] + dy * f + ny * (off - w / 2 + zig)]);
  }
  P(ctx, pts1.concat(pts2), col, { id, shadow: 1 });
}

// Pistole (sehr klein, schematisch)
function pistol(ctx, x, y, s, a, id = 1990) {
  P(ctx, tf([[0, 0], [26, 0], [26, 7], [8, 7], [6, 18], [0, 18]], x, y, s, a), C.ink, { id, shadow: 0.5, rough: 0.4 });
}
