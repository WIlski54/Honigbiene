/* Abspielsteuerung: Ton als Taktgeber, Kapitel, Untertitel, Unterrichtsmodus, Vollbild, Export */
'use strict';

(function () {
  const EXPORT = location.hash.includes('export');
  const cv = document.getElementById('stage');
  CANVAS = cv;
  const ctx = cv.getContext('2d', { alpha: false });
  const audio = document.getElementById('audio');
  audio.src = window.SOUNDTRACK_SRC || '../assets/soundtrack.mp3';

  buildTextures();
  titleImage();

  // Kapitel (Sprungziele = Beginn des jeweiligen Übergangs)
  const STOPS = chapterStops();
  const CHAPTERS = D.szenen.map((s, i) => ({ t: STOPS[i], title: s.titel, n: i + 1 }));
  const PAUSES = STOPS.slice(1);

  let scale = 1;           // Auflösungsfaktor (Leistung)
  let tPaused = 0, lastFrame = -1, force = true;
  let lessonMode = false, subs = false;

  function resize() {
    const box = document.getElementById('frame');
    const bw = box.clientWidth, bh = box.clientHeight;
    const w = Math.min(bw, bh * 16 / 9), h = w * 9 / 16;
    cv.style.width = w + 'px'; cv.style.height = h + 'px';
    const dpr = window.devicePixelRatio || 1;
    const target = EXPORT ? W : Math.min(W, Math.round(w * dpr * scale));
    if (cv.width !== target) {
      cv.width = target; cv.height = Math.round(target * 9 / 16);
      G.k = cv.width / W;
      patCache.clear();
      force = true;
    }
    const sub = document.getElementById('subs');
    sub.style.width = w + 'px';
    sub.style.fontSize = Math.max(14, w / 52) + 'px';
    sub.style.bottom = (bh - h) / 2 + h * 0.13 + 'px';
  }
  window.addEventListener('resize', resize);

  const now = () => audio.paused ? tPaused : audio.currentTime;

  // ---------------------------------------------------------------- Zeichnen
  const perf = [];
  function draw(t) {
    const f = Math.floor(t * FPS_DRAW + 1e-6);
    if (f === lastFrame && !force) return;
    lastFrame = f; force = false;
    const t0 = performance.now();
    renderFrame(ctx, t);
    const dt = performance.now() - t0;
    if (!EXPORT && !audio.paused) {
      perf.push(dt);
      if (perf.length >= 18) {
        const avg = perf.reduce((a, b) => a + b) / perf.length;
        perf.length = 0;
        if (avg > 70 && scale > 0.55) { scale -= 0.15; resize(); }
        else if (avg > 70 && !G.fast) { G.fast = true; }
      }
    }
    updateUI(t);
  }
  let prevT = 0;
  function checkStops() {
    let t = now();
    if (!audio.paused && lessonMode) {
      const stop = PAUSES.find(p => prevT < p && t >= p - 0.02);
      if (stop !== undefined) { pause(); tPaused = stop; audio.currentTime = stop; t = stop; force = true; showHint('Pause – weiter mit Leertaste'); }
    }
    if (!audio.paused) merkeGesehen(prevT, t);
    if (t >= D.dauer - 0.05 && !audio.paused) { merkeGesehen(prevT, D.dauer); pause(); tPaused = D.dauer - 0.01; }
    prevT = t;
    return t;
  }
  function loop() {
    draw(checkStops());
    requestAnimationFrame(loop);
  }
  // auch ohne sichtbare Bildschleife (Hintergrund-Tab) zuverlässig anhalten
  audio.addEventListener('timeupdate', checkStops);

  // „Gesehen“ zählt nur echtes Abspielen, kein Springen (für Arbeitsblätter: Film vollständig angesehen?)
  const gesehen = new Uint8Array(Math.ceil(D.dauer));
  let freigeschaltet = false;
  function merkeGesehen(a, b) {
    if (!(b >= a) || b - a > 1.5) return;
    for (let s = Math.floor(a); s <= Math.min(gesehen.length - 1, Math.floor(b)); s++) gesehen[s] = 1;
    if (!freigeschaltet && gesehen.reduce((x, y) => x + y, 0) >= gesehen.length * 0.95) freigeschaltet = true;
  }

  // ---------------------------------------------------------------- Steuerung
  function play() {
    document.getElementById('start').classList.add('hidden');
    if (tPaused >= D.dauer - 0.1) tPaused = 0;
    audio.currentTime = tPaused;
    audio.play().catch(() => { });
    document.body.classList.add('playing');
    setPlayIcon();
    wake();
  }
  function pause() {
    tPaused = audio.currentTime;
    audio.pause();
    document.body.classList.remove('playing');
    setPlayIcon();
    wake();
  }
  function toggle() { audio.paused ? play() : pause(); }
  function seek(t) {
    t = clamp(t, 0, D.dauer - 0.01);
    tPaused = t;
    audio.currentTime = t;
    prevT = t;
    force = true;
    wake();
  }
  function chapterIndex(t) { let i = 0; CHAPTERS.forEach((c, k) => { if (t >= c.t - 0.01) i = k; }); return i; }
  function next() { const i = chapterIndex(now()); if (i < CHAPTERS.length - 1) seek(CHAPTERS[i + 1].t); }
  function prev() { const t = now(), i = chapterIndex(t); seek(t - CHAPTERS[i].t > 2 || i === 0 ? CHAPTERS[i].t : CHAPTERS[i - 1].t); }
  function fullscreen() {
    const el = document.documentElement;
    try {
      const r = !document.fullscreenElement ? (el.requestFullscreen || el.webkitRequestFullscreen).call(el) : document.exitFullscreen();
      if (r && r.catch) r.catch(() => showHint('Vollbild ist hier nicht verfügbar'));
    } catch (e) { showHint('Vollbild ist hier nicht verfügbar'); }
  }

  // ---------------------------------------------------------------- UI
  const $ = id => document.getElementById(id);
  function setPlayIcon() {
    $('btnPlay').innerHTML = audio.paused ? ICON.play : ICON.pause;
    $('btnPlay').title = audio.paused ? 'Abspielen (Leertaste)' : 'Pause (Leertaste)';
  }
  const ICON = {
    play: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l12-7.5z" fill="currentColor"/></svg>',
    pause: '<svg viewBox="0 0 24 24"><path d="M6.5 4.5h4v15h-4zM13.5 4.5h4v15h-4z" fill="currentColor"/></svg>',
  };
  const fmt = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
  function updateUI(t) {
    $('bar').style.width = (t / D.dauer * 100) + '%';
    $('time').textContent = fmt(t) + ' / ' + fmt(D.dauer);
    const i = chapterIndex(t);
    $('chap').textContent = (i + 1) + ' · ' + CHAPTERS[i].title;
    document.querySelectorAll('#chapters li').forEach((li, k) => li.classList.toggle('on', k === i));
    if (subs) {
      const cue = D.cues.find(c => t >= c[0] - 0.1 && t <= c[1] + 0.35);
      const el = $('subs');
      const txt = cue ? cue[2] : '';
      if (el.dataset.txt !== txt) { el.dataset.txt = txt; el.innerHTML = txt ? '<span>' + txt + '</span>' : ''; }
    }
  }
  let hintTimer = 0;
  function showHint(s) {
    const h = $('hint'); h.textContent = s; h.classList.add('show');
    clearTimeout(hintTimer); hintTimer = setTimeout(() => h.classList.remove('show'), 2200);
  }
  let idle = 0;
  function wake() {
    document.body.classList.add('awake');
    clearTimeout(idle);
    idle = setTimeout(() => { if (!audio.paused) document.body.classList.remove('awake'); }, 2600);
  }

  if (!EXPORT) {
    // Kapitelmarken & Liste
    const ticks = $('ticks'), list = $('chapters');
    CHAPTERS.forEach((c, k) => {
      if (k) { const d = document.createElement('i'); d.style.left = (c.t / D.dauer * 100) + '%'; ticks.appendChild(d); }
      const li = document.createElement('li');
      li.innerHTML = '<b>' + c.n + '</b><span>' + c.title + '</span><em>' + fmt(c.t) + '</em>';
      li.onclick = () => { seek(c.t); list.parentElement.classList.remove('open'); };
      list.appendChild(li);
    });
    $('btnPlay').onclick = toggle;
    $('btnPrev').onclick = prev;
    $('btnNext').onclick = next;
    $('btnFull').onclick = fullscreen;
    $('btnChap').onclick = e => { e.stopPropagation(); $('chapWrap').classList.toggle('open'); };
    document.addEventListener('click', () => $('chapWrap').classList.remove('open'));
    $('chapWrap').onclick = e => e.stopPropagation();
    $('btnSubs').onclick = () => { subs = !subs; $('btnSubs').classList.toggle('on', subs); $('subs').innerHTML = ''; $('subs').dataset.txt = ''; showHint(subs ? 'Untertitel an' : 'Untertitel aus'); };
    $('btnLesson').onclick = () => { lessonMode = !lessonMode; $('btnLesson').classList.toggle('on', lessonMode); showHint(lessonMode ? 'Unterrichtsmodus: hält nach jeder Szene an' : 'Unterrichtsmodus aus'); };
    $('btnMute').onclick = () => { audio.muted = !audio.muted; $('btnMute').classList.toggle('off', audio.muted); };
    $('startBtn').onclick = play;
    const track = $('track');
    const seekFromEvent = e => { const r = track.getBoundingClientRect(); seek((e.clientX - r.left) / r.width * D.dauer); };
    let dragging = false;
    track.addEventListener('pointerdown', e => { dragging = true; track.setPointerCapture(e.pointerId); seekFromEvent(e); });
    track.addEventListener('pointermove', e => { if (dragging) seekFromEvent(e); });
    track.addEventListener('pointerup', () => { dragging = false; });
    $('frame').addEventListener('click', e => { if (e.target === cv) toggle(); });
    $('frame').addEventListener('dblclick', e => { if (e.target === cv) fullscreen(); });
    document.addEventListener('mousemove', wake);
    document.addEventListener('touchstart', wake, { passive: true });
    document.addEventListener('keydown', e => {
      const k = e.key;
      if (k === ' ' || k === 'k' || k === 'K') { e.preventDefault(); if ($('start').classList.contains('hidden')) toggle(); else play(); }
      else if (k === 'ArrowRight' || k === 'PageDown') { e.preventDefault(); next(); }
      else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); prev(); }
      else if (k === 'f' || k === 'F') fullscreen();
      else if (k === 'u' || k === 'U') $('btnSubs').click();
      else if (k === 'p' || k === 'P') $('btnLesson').click();
      else if (k === 'm' || k === 'M') $('btnMute').click();
      else if (k === 'Home') seek(0);
      else if (k === '.' ) { if (audio.paused) seek(now() + 1 / 12); }
      else if (k === ',' ) { if (audio.paused) seek(now() - 1 / 12); }
    });
    audio.addEventListener('ended', () => { merkeGesehen(prevT, D.dauer); pause(); tPaused = D.dauer - 0.01; });
    setPlayIcon();

    // -------------------------------------------------------------- Schnittstelle für ein Arbeitsblatt (iframe)
    // Befehle per postMessage: {mw: 'springe', t} · {mw: 'kapitel', n} (ab 1) · 'spielen' · 'anhalten' · 'status' · 'info'
    //   · 'freischalten' (das AB merkt sich den vollständig gesehenen Film)
    // Rückmeldung: {mw: 'status', art: 'papiertheater', t, laeuft, kapitel, gesehen (0–100), freigeschaltet}
    //   bzw. {mw: 'info', art: 'papiertheater', dauer, kapitel: [{t, ende, titel}], blicke: [], ansichten: []}
    // Gleiches Protokoll wie die Modellwelt (Skill modellwelt-bauen) – ein Arbeitsblatt kann beide gleich steuern.
    if (window.parent !== window) {
      document.body.classList.add('eingebettet');
      const eltern = window.parent;
      let letzter = '';
      const melde = (erzwingen) => {
        const t = now();
        const st = { mw: 'status', art: 'papiertheater', t: Math.round(t * 10) / 10, laeuft: !audio.paused, modus: 'film', live: false,
          kapitel: chapterIndex(t) + 1, gesehen: Math.round(gesehen.reduce((a, b) => a + b, 0) / gesehen.length * 100), freigeschaltet };
        const k = JSON.stringify(st);
        if (erzwingen || k !== letzter) { letzter = k; eltern.postMessage(st, '*'); }
      };
      setInterval(melde, 250);
      window.addEventListener('message', e => {
        const m = e.data;
        if (!m || typeof m.mw !== 'string') return;
        if (m.mw === 'springe' || m.mw === 'kapitel') {
          $('start').classList.add('hidden');
          if (!audio.paused) pause();
          seek(m.mw === 'kapitel' ? (CHAPTERS[Math.max(0, Math.min(CHAPTERS.length - 1, (+m.n || 1) - 1))].t) : (+m.t || 0));
        }
        else if (m.mw === 'spielen') { if (audio.paused) play(); }
        else if (m.mw === 'anhalten') { if (!audio.paused) pause(); }
        else if (m.mw === 'status') melde(true);
        else if (m.mw === 'freischalten') freigeschaltet = true;
        else if (m.mw === 'info') eltern.postMessage({ mw: 'info', art: 'papiertheater', dauer: D.dauer,
          kapitel: CHAPTERS.map((c, k) => ({ t: c.t, ende: k < CHAPTERS.length - 1 ? CHAPTERS[k + 1].t : D.dauer, titel: c.title })),
          blicke: [], ansichten: [] }, '*');
      });
    }
  } else {
    document.body.classList.add('export');
  }

  resize();
  if (EXPORT) {
    window.renderAt = t => { G.k = cv.width / W; renderFrame(ctx, t); return cv.toDataURL('image/jpeg', 0.93); };
    window.exportReady = true;
  } else {
    requestAnimationFrame(loop);
  }
  // Test-/Vorschau-Zugriff
  window.PLAYER = { seek, play, pause, renderAt: t => { renderFrame(ctx, t); } };
})();
