import './styles.css';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { ProgressSpring, partTransform, smoothstep } from './motion.js';
import { twoFingerStep } from './gestures.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { createIcons, ChevronDown, SlidersHorizontal, RotateCcw } from 'lucide';
import { TEILE, STANDARD_SCHILDER, ABGELEITET, schluesselFuer } from './teile.js';
import { komponenten, schwerpunkte, REGELN, teileDreiecke } from './teilung.js';
import { BLICKE, parseBefehl, entscheideTipp, statusObjekt, infoObjekt, aktualisiereBesucht } from './protokoll.js';
import { Hervorhebung } from './hervorheben.js';
import { Schilder } from './schilder.js';

const $ = (selector) => document.querySelector(selector);
const BASE = import.meta.env.BASE_URL;
// Einbettungsmodus (?embed=1): kompakte Bedienleiste, keine Kopfzeile; Steuerung per postMessage.
const EMBED = new URLSearchParams(location.search).get('embed') === '1';
document.documentElement.classList.toggle('embed', EMBED);
const eltern = window.parent !== window ? window.parent : null;
const viewport = $('#viewport');
const range = $('#explosion-range');
const progressOutput = $('#progress-output');
const spring = new ProgressSpring(14);
const parts = [];
const pointers = new Map();
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
let renderer, camera, controls, model, rangeDragging = false;
let auto = false, autoDirection = 1, lastTime = 0, raf;
let gesture = null, gestureMode = null, frameCount = 0, lastFpsTime = 0;
let currentPhase = -1, currentPreset = -1, disposed = false;
let cameraFits = [], lastFit = null;
let viewName = 'schraeg', tween = null, focusActive = false, focusQuelle = 'hervorheben', barHeight = 104;
let leisteAn = true, fitUebergang = null;
let organsShown = false, revealFlag = false;
let hervor = null, schilder = null, bereit = false, waehlen = false;
let nameKeys = null, numberKeys = [];
// Diagnose: virtuelle Zeit, damit automatisierte Tests auch in verdeckten Browsertabs (ohne requestAnimationFrame) laufen.
let uhrOffset = 0;
const jetzt = () => performance.now() + uhrOffset;
const fitsByView = new Map();
const viewDirections = new Map(BLICKE.map((b) => [b.name, new THREE.Vector3(...b.richtung).normalize()]));
const meshByName = new Map(), partByName = new Map(), keyMeshes = new Map(), pickable = [];
const besucht = new Set();
let letzterWert = 0;
const scene = new THREE.Scene();
scene.background = new THREE.Color('#f4f2ed');

function fail(message) {
  $('#loading').hidden = true;
  $('#error-panel').hidden = false;
  $('#error-message').textContent = message;
  for (const b of document.querySelectorAll('.presets button, #play, #zoom-in, #zoom-out')) b.disabled = true;
  range.disabled = true;
}

function setPlayLabel(playing) {
  const glyph = playing ? 'Ⅱ' : EMBED ? '▶' : '↗';
  $('#play').innerHTML = `<span class="pt">${playing ? 'Anhalten' : 'Abspielen'}</span> <span class="pg" aria-hidden="true">${glyph}</span>`;
  $('#play').setAttribute('aria-label', playing ? 'Automatische Öffnung anhalten' : 'Öffnung automatisch abspielen');
}

function stopAuto() {
  auto = false;
  setPlayLabel(false);
}

function startAuto() {
  auto = true;
  autoDirection = spring.target > .5 ? -1 : 1;
  setPlayLabel(true);
}

function setProgress(value, user = true) {
  if (user) stopAuto();
  spring.setTarget(value);
  viewport.dataset.targetProgress = spring.target.toFixed(4);
}

function updateUI(value) {
  const pct = Math.round(value * 100);
  progressOutput.innerHTML = `${pct} <span>%</span>`;
  if (!rangeDragging) range.value = String(Math.round(value * 1000));
  range.style.setProperty('--progress', `${(rangeDragging ? spring.target : value) * 100}%`);
  range.setAttribute('aria-valuetext', `${pct} Prozent geöffnet`);
  const phase = value < 0.08 ? 0 : value < 0.46 ? 1 : value < 0.64 ? 2 : 3;
  if (phase !== currentPhase) {
    currentPhase = phase;
    const titles = ['Die äußere Gestalt', 'Die Körperhülle öffnet sich', 'Der Situs', 'Die Systeme werden sichtbar'];
    const subtitles = ['Eine Biene. Schicht für Schicht.', 'Die Organe bleiben an ihrem Ort.', 'Die räumliche Lage der Organe.', 'Zusammenhänge aus jeder Perspektive.'];
    $('#phase-number').textContent = String(phase + 1).padStart(2, '0');
    $('#phase-title').textContent = titles[phase];
    $('#phase-description').textContent = subtitles[phase];
  }
  const preset = value < .04 ? 0 : Math.abs(value - .55) < .055 ? 1 : value > .96 ? 2 : -1;
  if (preset !== currentPreset) {
    currentPreset = preset;
    document.querySelectorAll('[data-progress]').forEach((button, index) => {
      button.classList.toggle('active', index === preset);
      button.setAttribute('aria-pressed', String(index === preset));
    });
  }
}

function textureNoise() {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 512;
  const ctx = canvas.getContext('2d');
  const pixels = ctx.createImageData(512, 512);
  let seed = 73021;
  for (let i = 0; i < pixels.data.length; i += 4) {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    const v = 125 + (seed % 42);
    pixels.data[i] = pixels.data[i+1] = pixels.data[i+2] = v;
    pixels.data[i+3] = 255;
  }
  ctx.putImageData(pixels, 0, 0);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(8, 6);
  return texture;
}

function applyProgress(value) {
  for (const part of parts) {
    const state = partTransform(part.metadata, value);
    part.object.position.set(part.base.x + state.offset[0], part.base.y + state.offset[1], part.base.z + state.offset[2]);
  }
  // Hide completely enclosed internal meshes; retain in-situ coordinates. A highlighted organ
  // stays visible (the ghosted shell then shows it in place).
  organsShown = value > .085 || (revealFlag && !!hervor && (hervor.an || hervor.faktor > 0));
  for (const part of parts) if (part.organ) part.object.visible = organsShown;
  updateUI(value);
}

function fitViewport() {
  const width = viewport.clientWidth, height = viewport.clientHeight;
  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  if (EMBED && !$('#explosion-control').hidden) barHeight = $('#explosion-control').offsetHeight || barHeight;
  if (model) {
    calculateCameraFits();
    snapToView(viewName);
  }
}

// Ränder, die nicht für das Modell zur Verfügung stehen (Kopfzeile bzw. Bedienkasten).
function margins() {
  const width = viewport.clientWidth;
  if (EMBED) return { top: 8, bottom: (leisteAn ? barHeight : 0) + 8, side: 20 };
  const top = width < 700 ? 138 : 176;
  const bottom = (width < 1000 ? 245 : 205) + (matchMedia('(pointer: coarse)').matches ? 40 : 0);
  return { top, bottom, side: width < 700 ? 30 : 120 };
}

function computeFits(direction) {
  const right = new THREE.Vector3(0, 1, 0).cross(direction).normalize();
  const up = direction.clone().cross(right).normalize();
  const width = viewport.clientWidth, height = viewport.clientHeight;
  const { top, bottom, side } = margins();
  const availableHeight = Math.max(height * .38, height - top - bottom);
  const availableWidth = width - side;
  const tangent = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  return [0, .55, 1].map(progress => {
    applyProgress(progress);
    model.updateMatrixWorld(true);
    const min = new THREE.Vector3(Infinity, Infinity, Infinity);
    const max = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
    const projectedPoints = [];
    model.traverse(object => {
      if (!object.isMesh) return;
      if (!object.geometry.boundingBox) object.geometry.computeBoundingBox();
      const box = object.geometry.boundingBox;
      for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
        const point = new THREE.Vector3(x, y, z).applyMatrix4(object.matrixWorld);
        const projected = new THREE.Vector3(point.dot(right), point.dot(up), point.dot(direction));
        min.min(projected); max.max(projected);
        projectedPoints.push(projected);
      }
    });
    const midpoint = min.clone().add(max).multiplyScalar(.5);
    const horizontal = tangent * camera.aspect * availableWidth / width;
    const vertical = tangent * availableHeight / height;
    const upper = tangent * (1-2*top/height);
    const lower = tangent * (-1+2*bottom/height);
    // Fit each projected mesh corner at its actual depth, rather than adding
    // the worst depth to the worst height of an enclosing box.
    let distance = 8;
    for (const point of projectedPoints) {
      const depth = point.z-midpoint.z;
      distance = Math.max(distance,
        Math.abs(point.x-midpoint.x)/horizontal + depth,
        (point.y-midpoint.y+upper*depth)/vertical,
        (midpoint.y-point.y-lower*depth)/vertical,
      );
    }
    distance *= 1.04;
    const target = right.clone().multiplyScalar(midpoint.x).addScaledVector(up, midpoint.y).addScaledVector(direction, midpoint.z);
    target.addScaledVector(up, -(bottom-top)/height * tangent * distance);
    return { progress, distance, target };
  });
}

// Fits je Blickrichtung, bei Bedarf berechnet; werden bei jeder Größenänderung neu angelegt.
function fitsFor(name) {
  if (!fitsByView.has(name)) {
    fitsByView.set(name, computeFits(viewDirections.get(name)));
    applyProgress(spring.value);
  }
  return fitsByView.get(name);
}

function calculateCameraFits() {
  fitUebergang = null;
  fitsByView.clear();
  cameraFits = fitsFor(viewName);
  viewport.dataset.cameraFits = JSON.stringify(cameraFits.map(f => ({ progress: f.progress, distance: f.distance })));
}

function fitAus(fits, progress) {
  const a = fits[progress <= .55 ? 0 : 1];
  const b = fits[progress <= .55 ? 1 : 2];
  const fraction = progress <= .55 ? smoothstep(.04, .55, progress) : smoothstep(.62, 1, progress);
  return { target: a.target.clone().lerp(b.target, fraction), distance: THREE.MathUtils.lerp(a.distance, b.distance, fraction) };
}

// Beim Ein-/Ausblenden der Leiste geht der Bildausschnitt über 0,5 s von den alten zu den neuen Fits über;
// die relative Nachführung in schritt() hält Drehung und Zoom dabei, der Blick springt nicht.
function fittedCamera(progress) {
  const neu = fitAus(cameraFits, progress);
  if (!fitUebergang) return neu;
  const u = Math.min(1, (jetzt() - fitUebergang.t0) / fitUebergang.dauer);
  if (u >= 1) { fitUebergang = null; return neu; }
  const alt = fitAus(fitUebergang.alt, progress), e = u * u * (3 - 2 * u);
  return { target: alt.target.lerp(neu.target, e), distance: THREE.MathUtils.lerp(alt.distance, neu.distance, e) };
}

// Bedienleiste ein-/ausblenden (Knopf oder Befehl leiste). fokussieren: Fokus auf den jeweils sichtbaren Schalter
// (nur bei Bedienung per Knopf, nie bei einem Befehl, damit das Elternfenster nicht scrollt).
function setLeiste(an, fokussieren = true) {
  if (an === leisteAn) return;
  leisteAn = an;
  $('#explosion-control').hidden = !an;
  $('#app').classList.toggle('controls-hidden', !an);
  $('#controls-show').hidden = an;
  $('#controls-hide').setAttribute('aria-expanded', String(an));
  $('#controls-show').setAttribute('aria-expanded', String(an));
  if (fokussieren) ($('#controls-' + (an ? 'hide' : 'show'))).focus({ preventScroll: true });
  if (EMBED && model) {
    // Nur der Bildausschnitt ändert sich (die Leiste verdeckt jetzt mehr oder weniger); der Blick bleibt.
    if (an) barHeight = $('#explosion-control').offsetHeight || barHeight;
    const alt = cameraFits;
    fitsByView.clear();
    cameraFits = fitsFor(viewName);
    viewport.dataset.cameraFits = JSON.stringify(cameraFits.map(f => ({ progress: f.progress, distance: f.distance })));
    fitUebergang = { alt, t0: jetzt(), dauer: reducedMotion.matches ? 1 : 500 };
  }
  if (bereit) melde();
}

// Sofort auf die Standardkamera der Blickrichtung (Zoom und Drehung zurückgesetzt).
function snapToView(name) {
  tween = null;
  viewName = name;
  cameraFits = fitsFor(name);
  lastFit = fittedCamera(spring.value);
  controls.target.copy(lastFit.target);
  camera.position.copy(controls.target).addScaledVector(viewDirections.get(name), lastFit.distance);
  camera.zoom = 1;
  camera.updateProjectionMatrix();
  controls.update();
  controls.saveState();
}

function defaultView() {
  focusActive = false;
  snapToView('schraeg');
}

// Sanfte Kamerafahrt. ziel(fortschritt) liefert { target, dir, dist } und wird je Frame neu ausgewertet,
// damit das Ziel einem sich noch öffnenden Modell folgt.
function startTween(ziel, sekunden = .9) {
  const offset = camera.position.clone().sub(controls.target);
  tween = { t0: jetzt(), dauer: reducedMotion.matches ? 1 : sekunden * 1000, ziel,
    vonZiel: controls.target.clone(), vonRichtung: offset.clone().normalize(), vonAbstand: offset.length() };
}

function stepTween(value, fit) {
  const u = Math.min(1, (jetzt() - tween.t0) / tween.dauer);
  const e = u * u * (3 - 2 * u);
  const ziel = tween.ziel(value);
  controls.target.lerpVectors(tween.vonZiel, ziel.target, e);
  const drehung = new THREE.Quaternion().setFromUnitVectors(tween.vonRichtung, ziel.dir);
  const richtung = tween.vonRichtung.clone().applyQuaternion(new THREE.Quaternion().slerp(drehung, e));
  camera.position.copy(controls.target).addScaledVector(richtung, THREE.MathUtils.lerp(tween.vonAbstand, ziel.dist, e));
  lastFit = fit;
  if (u >= 1) tween = null;
}

function blick(name) {
  viewName = name;
  cameraFits = fitsFor(name);
  focusActive = false;
  const dir = viewDirections.get(name);
  startTween((value) => { const f = fittedCamera(value); return { target: f.target, dir, dist: f.distance }; });
}

// Kamera sanft näher an die gewählten Meshes. Ohne opt.dir bleibt die Blickrichtung erhalten.
// opt: { dir, abstand, faktor, quelle, region } (quelle 'hervorheben' wird beim Aufheben der Hervorhebung zurückgefahren,
// quelle 'fokus' nur durch den Befehl fokus bzw. zurueck; region = Funktion, die je Frame die Zielbox liefert).
function fokussiere(alle, opt = {}) {
  if (!alle.length && !opt.region) return;
  // Paarige Teile (Flügel, Beine, Augen ...): nur die der Kamera zugewandte Körperseite, sonst wäre das
  // Ziel der ganze Körper breit. Mittige Meshes (|z| klein) gehören immer dazu.
  model.updateMatrixWorld(true);
  const mitteZ = (m) => weltBox(m, new THREE.Box3()).getCenter(new THREE.Vector3()).z;
  const dir = opt.dir ? opt.dir.clone() : camera.position.clone().sub(controls.target).normalize();
  const seite = dir.z;
  const nah = Math.abs(seite) > .3
    ? alle.filter((m) => { const z = mitteZ(m); return Math.abs(z) < .08 || Math.sign(z) === Math.sign(seite); })
    : alle;
  const meshes = nah.length ? nah : alle;
  const startDist = camera.position.distanceTo(controls.target);
  const faktor = opt.faktor ?? 2;
  const box = new THREE.Box3(), teil = new THREE.Box3(), mittelpunkt = new THREE.Vector3(), groesse = new THREE.Vector3();
  const right = new THREE.Vector3(0, 1, 0).cross(dir).normalize();
  const up = dir.clone().cross(right).normalize();
  focusActive = true; focusQuelle = opt.quelle ?? 'hervorheben';
  startTween(() => {
    model.updateMatrixWorld(true);
    if (opt.region) box.copy(opt.region());
    else { box.makeEmpty(); for (const m of meshes) box.union(weltBox(m, teil)); }
    box.getCenter(mittelpunkt); box.getSize(groesse);
    const width = viewport.clientWidth, height = viewport.clientHeight;
    const { top, bottom, side } = margins();
    const tangent = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const frei = Math.min(Math.max(height * .38, height - top - bottom) / height * tangent, camera.aspect * (width - side) / width * tangent);
    const radius = Math.max(.15, groesse.length() / 2);
    // Faktor 2 auf den halben Boxdiagonalen-Radius: die Auswahl füllt etwa die Hälfte des freien Bildes, der Rest bleibt als Zusammenhang sichtbar.
    // Der Befehl fokus nutzt einen kleineren Faktor (Antippen kleiner Teile).
    const dist = opt.abstand
      ? THREE.MathUtils.clamp(opt.abstand, controls.minDistance, controls.maxDistance)
      : THREE.MathUtils.clamp(radius * faktor / Math.sin(Math.atan(frei)), controls.minDistance, startDist);
    const target = mittelpunkt.clone().addScaledVector(up, -(bottom - top) / height * tangent * dist);
    return { target, dir, dist };
  }, 1.0);
}

function weltBox(mesh, ziel) {
  if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
  return ziel.copy(mesh.geometry.boundingBox).applyMatrix4(mesh.matrixWorld);
}

function zoom(amount, point = null) {
  tween = null; focusActive = false;
  const delta = camera.position.clone().sub(controls.target);
  const distance = delta.length();
  const nextDistance = THREE.MathUtils.clamp(distance * amount, controls.minDistance, controls.maxDistance);
  if (point) {
    const rect = viewport.getBoundingClientRect();
    const ndc = new THREE.Vector2((point.x-rect.left)/rect.width*2-1, 1-(point.y-rect.top)/rect.height*2);
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(ndc, camera);
    const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(camera.getWorldDirection(new THREE.Vector3()), controls.target);
    const anchor = raycaster.ray.intersectPlane(plane, new THREE.Vector3());
    if (anchor) controls.target.add(anchor.sub(controls.target).multiplyScalar(1-nextDistance/distance));
  }
  delta.setLength(nextDistance);
  camera.position.copy(controls.target).add(delta);
  controls.update();
}

function wheel(event) {
  event.preventDefault();
  // Trackpad pinch is reported as a Ctrl+wheel event on desktop browsers.
  if (event.ctrlKey || event.metaKey) { zoom(Math.exp(event.deltaY * .004), { x: event.clientX, y: event.clientY }); return; }
  const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1);
  setProgress(spring.target + THREE.MathUtils.clamp(delta * .00055, -.14, .14));
}

function pointerDown(event) {
  if (event.pointerType !== 'touch') return;
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  if (pointers.size === 2) {
    controls.enabled = false;
    gestureMode = null;
    gesture = touchValues();
    stopAuto();
  }
}

function touchValues() {
  const [a, b] = [...pointers.values()];
  return { x: (a.x+b.x)/2, y: (a.y+b.y)/2, distance: Math.hypot(a.x-b.x,a.y-b.y) };
}

function pointerMove(event) {
  if (event.pointerType !== 'touch' || !pointers.has(event.pointerId)) return;
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  if (pointers.size === 2) event.preventDefault();
}

function processTouch() {
  if (pointers.size !== 2 || !gesture) return;
  const next = touchValues();
  const step = twoFingerStep(gesture, next, gestureMode);
  if (!step.mode) return;
  gestureMode = step.mode;
  if (gestureMode === 'pinch') zoom(step.zoomRatio, next);
  if (gestureMode === 'explode') setProgress(spring.target + step.movement / Math.max(250, viewport.clientHeight * .55));
  gesture = next;
}

function pointerUp(event) {
  pointers.delete(event.pointerId);
  // Keep controls locked until all pointers leave, avoiding a camera jump on
  // transition from a two-finger gesture back to a one-finger gesture.
  if (pointers.size === 0) { controls.enabled = true; gesture = null; gestureMode = null; }
}

// ---------------------------------------------------------------- Wählmodus: Antippen eines Teils
let tap = null;

function tapDown(event) {
  if (!event.isPrimary) { if (tap) tap.multi = true; return; }
  if (event.pointerType === 'mouse' && (event.button !== 0 || event.ctrlKey || event.metaKey)) { tap = null; return; }
  tap = { id: event.pointerId, x: event.clientX, y: event.clientY, t: performance.now(), multi: false, moved: false, touch: event.pointerType !== 'mouse' };
}

function tapMove(event) {
  if (!tap || event.pointerId !== tap.id) return;
  if (Math.hypot(event.clientX - tap.x, event.clientY - tap.y) > (tap.touch ? 10 : 6)) tap.moved = true;
}

function tapUp(event) {
  const t = tap;
  if (!t || event.pointerId !== t.id) return;
  tap = null;
  if (!waehlen || t.moved || t.multi || pointers.size > 1 || performance.now() - t.t > 1500) return;
  const ergebnis = pickBei(event.clientX, event.clientY);
  senden({ mw: 'tipp', teil: ergebnis.teil, teile: ergebnis.teile, rohname: ergebnis.rohname, darunter: ergebnis.darunter, davor: ergebnis.davor });
  hervor?.leuchte(ergebnis.teil);
}

const raycaster = new THREE.Raycaster();
const sichtbar = (objekt) => { for (let o = objekt; o; o = o.parent) if (!o.visible) return false; return true; };

function entscheide(treffer) {
  return entscheideTipp(treffer.map((h) => ({ abstand: h.distance, weich: h.object.userData.weich, rohname: h.object.name, teile: h.object.userData.schluessel })));
}

// Strahl durch die Tippstelle; verfehlt er das Modell, werden Strahlen auf Ringen von 9 und 18 px
// versucht (Fingerspitze). Haarmeshes sind nicht wählbar (gleiche Gruppe wie die Haut darunter).
function pickBei(clientX, clientY, ringe = true) {
  const rect = viewport.getBoundingClientRect();
  const liste = pickable.filter(sichtbar);
  const strahl = (dx, dy) => {
    raycaster.setFromCamera(new THREE.Vector2((clientX + dx - rect.left) / rect.width * 2 - 1, 1 - (clientY + dy - rect.top) / rect.height * 2), camera);
    return raycaster.intersectObjects(liste, false);
  };
  const mitte = strahl(0, 0);
  if (mitte.length || !ringe) return entscheide(mitte);
  for (const r of [9, 18]) {
    let beste = null;
    for (let i = 0; i < 8; i++) {
      const w = i * Math.PI / 4;
      const treffer = strahl(Math.cos(w) * r, Math.sin(w) * r);
      if (treffer.length && (!beste || treffer[0].distance < beste[0].distance)) beste = treffer;
    }
    if (beste) return entscheide(beste);
  }
  return entscheide([]);
}

// ---------------------------------------------------------------- Namen und Nummern
const keyUnit = new Map();
const tmpBox = new THREE.Box3(), tmpBoxB = new THREE.Box3(), tmpV = new THREE.Vector3();

function einheitPunkt(einheit) {
  if (einheit.punkt) {
    const gruppe = partByName.get(einheit.gruppe);
    const punkt = new THREE.Vector3(...einheit.punkt);
    if (gruppe) punkt.add(gruppe.object.position).sub(gruppe.base);
    return punkt;
  }
  tmpBox.makeEmpty();
  for (const name of einheit.meshen) { const m = meshByName.get(name); if (m) tmpBox.union(weltBox(m, tmpBoxB)); }
  return tmpBox.isEmpty() ? null : tmpBox.getCenter(new THREE.Vector3());
}

// Ankerpunkt eines Teils in Weltkoordinaten; bei mehreren Einheiten die der Kamera nächste (mit Trägheit).
function ankerWelt(key) {
  const punkte = TEILE[key].anker.map((e, i) => ({ i, p: einheitPunkt(e) })).filter((e) => e.p);
  if (!punkte.length) return null;
  const abstand = (e) => e.p.distanceTo(camera.position);
  let wahl = punkte.reduce((a, b) => (abstand(b) < abstand(a) ? b : a));
  const alt = punkte.find((e) => e.i === keyUnit.get(key));
  if (alt && abstand(alt) < abstand(wahl) * 1.12) wahl = alt;
  keyUnit.set(key, wahl.i);
  return wahl.p;
}

const keyInnen = (key) => (keyMeshes.get(key) ?? []).length > 0 && keyMeshes.get(key).every((m) => m.userData.organ);

function updateSchilder() {
  if (!schilder || schilder.leer) return;
  const width = viewport.clientWidth, height = viewport.clientHeight;
  const kasten = $('#explosion-control');
  const unten = kasten.hidden ? 0 : Math.max(0, height - kasten.offsetTop + 4);
  const anker = new Map();
  const setze = (id, key) => {
    if (keyInnen(key) && !organsShown) return;
    const p = ankerWelt(key);
    if (!p) return;
    tmpV.copy(p).project(camera);
    if (tmpV.z < -1 || tmpV.z > 1) return;
    anker.set(id, { x: (tmpV.x * .5 + .5) * width, y: (-tmpV.y * .5 + .5) * height });
  };
  for (const e of schilder.eintraege) setze(e.id, e.teil);
  schilder.zeichne(anker, width, height, unten);
}

function setzeSchilder() {
  if (!schilder) return;
  const liste = [];
  for (const k of nameKeys ?? []) liste.push({ id: `name:${k}`, typ: 'name', text: TEILE[k].name, teil: k });
  numberKeys.forEach((k, i) => { if (k) liste.push({ id: `nummer:${i + 1}`, typ: 'nummer', text: String(i + 1), teil: k }); });
  schilder.setze(liste);
  $('#names-toggle').setAttribute('aria-pressed', String(!!nameKeys));
}

function setzeHervorhebung(teile, fokus) {
  hervor.setze(teile);
  if (teile.length) {
    revealFlag = hervor.meshes.some((m) => m.userData.organ);
    if (fokus) fokussiere(hervor.meshes);
  } else if (focusActive && focusQuelle === 'hervorheben') blick(viewName);
}

// Zielbox einer Ankereinheit (teile.js): Box der Anker-Meshes bzw. ein Würfel von 1,2 Einheiten um den Ankerpunkt.
function einheitBox(einheit) {
  if (einheit.punkt) return new THREE.Box3().setFromCenterAndSize(einheitPunkt(einheit), new THREE.Vector3(1.2, 1.2, 1.2));
  const box = new THREE.Box3();
  for (const name of einheit.meshen) { const m = meshByName.get(name); if (m) box.union(weltBox(m, tmpBoxB)); }
  return box.isEmpty() ? null : box;
}

// Je Schlüssel die Ankereinheit, die der Zielblickrichtung am meisten zugewandt ist (paarige Teile: nahe Seite).
function ankerRegion(keys, dir) {
  const einheiten = [];
  for (const k of keys) {
    let beste = null, wert = -Infinity;
    for (const e of TEILE[k].anker) {
      const b = einheitBox(e);
      if (b && b.getCenter(tmpV).dot(dir) > wert) { wert = tmpV.dot(dir); beste = e; }
    }
    if (beste) einheiten.push(beste);
  }
  return () => {
    const box = new THREE.Box3();
    for (const e of einheiten) { const b = einheitBox(e); if (b) box.union(b); }
    return box;
  };
}

// Befehl fokus: Kamerafahrt an die Ankerregion der Teile, ohne etwas zu markieren oder zu verändern. teile:[] fährt zurück.
function fokusBefehl(c) {
  if (!c.teile.length) {
    if (focusActive || c.blick) blick(c.blick ?? viewName);
    return;
  }
  let dir = null;
  if (c.blick) { viewName = c.blick; cameraFits = fitsFor(c.blick); dir = viewDirections.get(c.blick); }
  else if (c.teile.length === 1 && TEILE[c.teile[0]].fokusRichtung) dir = new THREE.Vector3(...TEILE[c.teile[0]].fokusRichtung).normalize();
  const ziel = dir ?? camera.position.clone().sub(controls.target).normalize();
  model.updateMatrixWorld(true);
  fokussiere([], { dir, abstand: c.abstand, faktor: 1, quelle: 'fokus', region: ankerRegion(c.teile, ziel) });
}

// ---------------------------------------------------------------- Schnittstelle zum Arbeitsblatt
const wartend = [];
let letzterStatus = '';

function senden(objekt) { if (eltern) eltern.postMessage(objekt, '*'); }

function melde(erzwingen = false) {
  if (!eltern || !bereit) return;
  const s = statusObjekt({ fortschritt: spring.value, laeuft: auto, besucht, blick: viewName, waehlen, hervorgehoben: hervor.aktiv, leiste: leisteAn });
  const key = JSON.stringify({ ...s, fortschritt: 0 });
  if (erzwingen || key !== letzterStatus) { letzterStatus = key; senden(s); }
}

function fuehreAus(c) {
  switch (c.typ) {
    case 'info': senden(infoObjekt()); return;
    case 'status': melde(true); return;
    case 'ansicht': setProgress(c.wert); break;
    case 'blick': stopAuto(); blick(c.name); break;
    case 'hervorheben': setzeHervorhebung(c.teile, c.fokus); break;
    case 'beschriften': nameKeys = c.an ? (c.teile.length ? c.teile : STANDARD_SCHILDER) : null; setzeSchilder(); break;
    case 'nummern': numberKeys = c.teile; setzeSchilder(); break;
    case 'waehlen': waehlen = c.an; viewport.classList.toggle('waehlen', waehlen); break;
    case 'fokus': fokusBefehl(c); break;
    case 'leiste': setLeiste(c.an, false); break;
    case 'spielen': if (!auto) startAuto(); break;
    case 'anhalten': stopAuto(); break;
    case 'zurueck':
      stopAuto(); setProgress(0);
      setzeHervorhebung([], false);
      nameKeys = null; numberKeys = []; setzeSchilder();
      focusActive = false; blick('schraeg');
      break;
    default: return; // freischalten, springe: ohne Wirkung (Kompatibilität)
  }
  melde();
}

function nachricht(daten) {
  const befehl = parseBefehl(daten);
  if (!befehl) return;
  if (befehl.typ === 'info') { senden(infoObjekt()); return; }
  if (!bereit) { wartend.push(befehl); return; }
  fuehreAus(befehl);
}

if (eltern) {
  window.addEventListener('message', (e) => { if (e.source === eltern) nachricht(e.data); });
}

function bindUI() {
  createIcons({ icons: { ChevronDown, SlidersHorizontal, RotateCcw } });
  $('#controls-hide').addEventListener('click', () => setLeiste(false));
  $('#controls-show').addEventListener('click', () => setLeiste(true));
  range.addEventListener('pointerdown', () => { rangeDragging = true; });
  window.addEventListener('pointerup', () => { rangeDragging = false; });
  window.addEventListener('pointercancel', () => { rangeDragging = false; });
  range.addEventListener('input', () => setProgress(Number(range.value) / 1000));
  document.querySelectorAll('[data-progress]').forEach(button => button.addEventListener('click', () => setProgress(Number(button.dataset.progress))));
  setPlayLabel(false);
  if (EMBED) {
    const embedLabels = [['Außen', 'Außenansicht'], ['Innen', 'Innenansicht (Situs)'], ['Explosion', 'Explosionsansicht']];
    document.querySelectorAll('[data-progress]').forEach((button, i) => { button.textContent = embedLabels[i][0]; button.setAttribute('aria-label', embedLabels[i][1]); });
  }
  $('#play').addEventListener('click', () => { if (auto) stopAuto(); else startAuto(); });
  $('#reset-view').addEventListener('click', defaultView);
  $('#reset-embed').addEventListener('click', defaultView);
  $('#names-toggle').addEventListener('click', () => { nameKeys = nameKeys ? null : STANDARD_SCHILDER; setzeSchilder(); });
  $('#zoom-in').addEventListener('click', () => zoom(.84));
  $('#zoom-out').addEventListener('click', () => zoom(1.19));
  const ref = $('#reference-panel');
  function toggleReference(open) { ref.hidden = !open; $('#reference-toggle').setAttribute('aria-expanded', String(open)); }
  $('#reference-toggle').addEventListener('click', () => toggleReference(ref.hidden));
  $('#reference-close').addEventListener('click', () => toggleReference(false));
  const references = [
    { src: `${BASE}reference/bee.png`, alt: 'Honigbiene aus erhöhter Dreiviertelansicht', caption: 'Vorlage für Haltung, Proportionen und Oberflächen. Die 3D-Rekonstruktion wird schrittweise daran verfeinert.' },
    { src: `${BASE}reference/anatomy-model.png`, alt: 'Vom Nutzer bereitgestelltes anatomisches Schnittmodell einer Biene', caption: 'Anatomisches Schnittmodell als Referenz für Formen und Lagebeziehungen. Die Farben dienen der Unterscheidung der Organe.' },
    { src: `${BASE}reference/anatomy-section.png`, alt: 'Vom Nutzer bereitgestellte beschriftete Schnittzeichnung der inneren Bienenanatomie', caption: 'Beschriftete Schnittzeichnung für Honigblase, Mitteldarm, Herzschlauch, Drüsen und Flugmuskulatur. Die räumliche Tiefe wird rekonstruiert.' },
  ];
  document.querySelectorAll('[data-reference]').forEach(button => button.addEventListener('click', () => {
    const index = Number(button.dataset.reference);
    $('#reference-image').src = references[index].src;
    $('#reference-image').alt = references[index].alt;
    $('#reference-caption').textContent = references[index].caption;
    document.querySelectorAll('[data-reference]').forEach(tab => tab.setAttribute('aria-selected', String(tab === button)));
  }));
  $('#about-toggle').addEventListener('click', () => {
    const open = $('#about-panel').hidden;
    $('#about-panel').hidden = !open;
    $('#about-toggle').setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') { toggleReference(false); $('#about-panel').hidden = true; $('#about-toggle').setAttribute('aria-expanded', 'false'); stopAuto(); }
    if (event.target instanceof HTMLInputElement) return;
    if (event.key === '+' || event.key === '=') zoom(.9);
    if (event.key === '-') zoom(1.1);
  });
  $('#retry').addEventListener('click', () => location.reload());
  viewport.addEventListener('wheel', wheel, { passive: false });
  // Install gesture recognizers before OrbitControls' pointer listeners.
  viewport.addEventListener('pointerdown', pointerDown, true);
  viewport.addEventListener('pointermove', pointerMove, { capture: true, passive: false });
  viewport.addEventListener('pointerup', pointerUp, true);
  viewport.addEventListener('pointercancel', pointerUp, true);
  viewport.addEventListener('lostpointercapture', pointerUp, true);
  viewport.addEventListener('pointerdown', tapDown, true);
  viewport.addEventListener('pointermove', tapMove, true);
  viewport.addEventListener('pointerup', tapUp, true);
  viewport.addEventListener('pointercancel', () => { tap = null; }, true);
  if (matchMedia('(pointer: coarse)').matches) {
    $('#interaction-hint').innerHTML = '<p><strong>Drehen</strong> 1 Finger</p><p><strong>Öffnen</strong> 2 Finger ↑↓</p><p><strong>Zoom</strong> Pinch</p>';
  }
}

function frame(time) {
  if (disposed) return;
  raf = requestAnimationFrame(frame);
  schritt(time);
}

function schritt(time, erzwingen = false) {
  // The spring is integrated analytically: elapsed time must not be capped,
  // otherwise autoplay slows down when the browser drops or throttles frames.
  const dt = lastTime ? Math.max(0, (time-lastTime)/1000) : 1/60;
  lastTime = time;
  if (document.hidden && !erzwingen) return;
  if (auto) {
    spring.setTarget(spring.target + autoDirection * dt / 12);
    if ((autoDirection === 1 && spring.target === 1) || (autoDirection === -1 && spring.target === 0)) stopAuto();
  }
  processTouch();
  hervor.aktualisiere(dt, reducedMotion.matches);
  const value = spring.step(reducedMotion.matches ? dt * 2 : dt);
  applyProgress(value);
  if (aktualisiereBesucht(besucht, value, letzterWert)) melde();
  letzterWert = value;
  const fit = fittedCamera(value);
  if (tween) stepTween(value, fit);
  else {
    const viewVector = camera.position.clone().sub(controls.target).multiplyScalar(fit.distance / lastFit.distance);
    controls.target.add(fit.target.clone().sub(lastFit.target));
    camera.position.copy(controls.target).add(viewVector);
    lastFit = fit;
  }
  controls.update();
  const renderStart = performance.now();
  renderer.render(scene, camera);
  const renderCpuMs = performance.now() - renderStart;
  updateSchilder();
  frameCount++;
  if (time-lastFpsTime > 1500) {
    const fps = Math.round(frameCount * 1000 / (time-lastFpsTime));
    if (lastFpsTime > 0) $('#render-status').textContent = `Echtzeit · ${fps} fps`;
    viewport.dataset.renderCpuMs = renderCpuMs.toFixed(2);
    viewport.dataset.frameMs = (dt * 1000).toFixed(2);
    viewport.dataset.drawCalls = String(renderer.info.render.calls);
    viewport.dataset.triangles = String(renderer.info.render.triangles);
    frameCount = 0; lastFpsTime = time;
  }
}

// Neue Geometrie aus den gewählten Dreiecken einer Geometrie (Attribute werden als Float32 kopiert).
function extrahiere(geometry, dreiecke) {
  const index = geometry.index.array;
  const neu = new Map(), neuerIndex = [];
  for (const t of dreiecke) for (let e = 0; e < 3; e++) {
    const v = index[t * 3 + e];
    if (!neu.has(v)) neu.set(v, neu.size);
    neuerIndex.push(neu.get(v));
  }
  const alt = [...neu.keys()];
  const ergebnis = new THREE.BufferGeometry();
  for (const [name, a] of Object.entries(geometry.attributes)) {
    const werte = new Float32Array(alt.length * a.itemSize);
    alt.forEach((v, i) => { for (let c = 0; c < a.itemSize; c++) werte[i * a.itemSize + c] = [a.getX, a.getY, a.getZ, a.getW][c].call(a, v); });
    ergebnis.setAttribute(name, new THREE.BufferAttribute(werte, a.itemSize));
  }
  ergebnis.setIndex(neuerIndex);
  ergebnis.computeBoundingBox();
  ergebnis.computeBoundingSphere();
  return ergebnis;
}

// Löst Teilmeshes aus vorhandenen Meshes (Pollenkörbchen, Giftblase); die GLB bleibt unverändert.
function loeseAb(wurzel) {
  const meshes = [];
  wurzel.traverse((o) => { if (o.isMesh) meshes.push(o); });
  for (const regel of ABGELEITET) for (const mesh of meshes) {
    if (!regel.quelle.test(mesh.name)) continue;
    mesh.updateMatrix();
    const geo = mesh.geometry, pos = geo.getAttribute('position'), v = new THREE.Vector3();
    const zerlegung = komponenten(geo.index.array, pos.count);
    const mitten = schwerpunkte(geo.index.array, zerlegung, (i) => { v.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrix); return [v.x, v.y, v.z]; });
    const auswahl = REGELN[regel.regel](mitten);
    if (!auswahl.size) { console.warn(`Teilung ${regel.regel} für ${mesh.name} ergab keine Auswahl.`); continue; }
    const { drin, draussen } = teileDreiecke(zerlegung, auswahl);
    const neu = new THREE.Mesh(extrahiere(geo, drin), mesh.material);
    neu.name = regel.name(mesh.name);
    neu.position.copy(mesh.position); neu.quaternion.copy(mesh.quaternion); neu.scale.copy(mesh.scale);
    mesh.parent.add(neu);
    mesh.geometry = extrahiere(geo, draussen);
    geo.dispose();
  }
}

async function init() {
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    const touchDevice = matchMedia('(pointer: coarse)').matches;
    renderer.setPixelRatio(Math.min(devicePixelRatio, touchDevice ? 1.25 : 1.75));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.03;
    viewport.appendChild(renderer.domElement);
    camera = new THREE.PerspectiveCamera(38, 1, .05, 100);
    schilder = new Schilder($('#schilder'));
    bindUI();
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = .09;
    controls.enableZoom = false;
    controls.enablePan = true;
    controls.minDistance = EMBED ? 1.6 : 3.2; // im Arbeitsblatt darf die Kamera für kleine Teile näher heran
    controls.maxDistance = 55;
    controls.rotateSpeed = .65;
    controls.touches.ONE = THREE.TOUCH.ROTATE;
    controls.touches.TWO = null;
    controls.addEventListener('start', () => { stopAuto(); tween = null; focusActive = false; });
    const environment = new RoomEnvironment();
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(environment, .04).texture;
    environment.dispose();
    pmrem.dispose();
    scene.environmentIntensity = .55;
    scene.add(new THREE.HemisphereLight(0xffffff, 0x9f8462, 1.25));
    const key = new THREE.DirectionalLight(0xffefd7, 1.6); key.position.set(-3, 7, 5); scene.add(key);
    const fill = new THREE.DirectionalLight(0xffffff, .85); fill.position.set(3, 2, -5); scene.add(fill);
    const rim = new THREE.DirectionalLight(0xffe7c0, 1.5); rim.position.set(2, 5, -1); scene.add(rim);

    const mobileQuality = matchMedia('(pointer: coarse)').matches || viewport.clientWidth < 700;
    const modelPath = `${BASE}models/${mobileQuality ? 'bee-study-mobile.glb' : 'bee-study.glb'}`;
    const gltf = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync(modelPath, event => {
      if (event.total) $('#loading-detail').textContent = `3D-Modell wird geladen · ${Math.round(event.loaded/event.total*100)} %`;
    });
    model = gltf.scene;
    loeseAb(model);
    const noise = textureNoise();
    const eintraege = [];
    model.traverse(object => {
      if (object.userData.studyPart) {
        parts.push({ object, metadata: object.userData.explosion, base: object.position.clone(), organ: object.userData.organ === true });
        partByName.set(object.name, parts.at(-1));
      }
      if (!object.isMesh) return;
      object.frustumCulled = true;
      const group = (() => { let o = object.parent; while (o && !o.userData.studyPart) o = o.parent; return o; })();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        material.envMapIntensity = .65;
        if (material.name.startsWith('Cuticle') || material.name.startsWith('Articulations')) {
          material.bumpMap = noise;
          material.bumpScale = .006;
          material.roughness = material.name.startsWith('Articulations') ? .28 : .32;
        }
        if (material.name.startsWith('Wing membrane')) {
          material.transparent = true;
          material.opacity = .19;
          material.depthWrite = false;
          material.side = THREE.DoubleSide;
          object.renderOrder = 2;
        }
        if (material.name.startsWith('Air sacs')) {
          material.transparent = true;
          material.opacity = .22;
          material.depthWrite = false;
          material.side = THREE.DoubleSide;
          object.renderOrder = 1;
        }
      }
      const materialName = materials[0].name;
      object.userData.schluessel = schluesselFuer(group?.name ?? '', object.name);
      object.userData.organ = group?.userData.organ === true;
      // Weich = blockiert beim Antippen keine festen Teile dahinter: Flügelmembranen, Luftsack-Membranen und die dünnen,
      // pearlfarbenen Tracheenstämme davor (Atmungssystem, siehe teile.js).
      object.userData.weich = materialName.startsWith('Wing membrane') || materialName.startsWith('Air sacs') || materialName.startsWith('Tracheal system');
      meshByName.set(object.name, object);
      eintraege.push({ mesh: object, schluessel: object.userData.schluessel });
      for (const k of object.userData.schluessel) { if (!keyMeshes.has(k)) keyMeshes.set(k, []); keyMeshes.get(k).push(object); }
      if (!materialName.startsWith('Setae')) pickable.push(object);
    });
    hervor = new Hervorhebung(eintraege);
    scene.add(model);
    fitViewport();
    snapToView('schraeg');
    const resizeObserver = new ResizeObserver(fitViewport);
    resizeObserver.observe(viewport);
    applyProgress(0);
    renderer.render(scene, camera);
    $('#loading').hidden = true;
    lastFpsTime = performance.now();
    raf = requestAnimationFrame(frame);
    renderer.domElement.addEventListener('webglcontextlost', event => {
      event.preventDefault(); stopAuto(); cancelAnimationFrame(raf);
      fail('Die Grafikverbindung wurde unterbrochen. Bitte laden Sie die Ansicht erneut.');
    });
    document.addEventListener('visibilitychange', () => { lastTime = 0; lastFpsTime = performance.now(); frameCount = 0; });
    // Diagnostics for development and automated validation; no production UI.
    window.beeStudy = {
      get progress() { return spring.value; },
      get target() { return spring.target; },
      get auto() { return auto; },
      get parts() { return parts.map(p => ({ name: p.object.name, organ: p.organ, base: p.base.toArray(), position: p.object.position.toArray(), metadata: p.metadata })); },
      get renderInfo() { return { calls: renderer.info.render.calls, triangles: renderer.info.render.triangles, geometries: renderer.info.memory.geometries }; },
      get zustand() { return { leiste: leisteAn, blick: viewName, waehlen, hervorgehoben: [...hervor.aktiv], faktor: hervor.faktor, namen: nameKeys, nummern: numberKeys, organsShown, tween: !!tween, fokus: focusActive, distanz: camera.position.distanceTo(controls.target), bar: barHeight }; },
      meshesFuer: (k) => (keyMeshes.get(k) ?? []).map((m) => m.name),
      // Bildschirmpunkt (Client-Koordinaten im Frame) des Ankers eines Teils, für automatisierte Tests.
      bildschirmpunkt(k) {
        const p = ankerWelt(k); if (!p) return null;
        const r = viewport.getBoundingClientRect(); const q = p.clone().project(camera);
        return { x: r.left + (q.x * .5 + .5) * r.width, y: r.top + (-q.y * .5 + .5) * r.height };
      },
      // Mittelpunkt eines Meshes auf dem Bildschirm (Client-Koordinaten).
      meshPunkt(name) {
        const m = meshByName.get(name); if (!m) return null;
        model.updateMatrixWorld(true);
        const c = weltBox(m, new THREE.Box3()).getCenter(new THREE.Vector3()).project(camera);
        const r = viewport.getBoundingClientRect();
        return { x: r.left + (c.x * .5 + .5) * r.width, y: r.top + (-c.y * .5 + .5) * r.height };
      },
      pick: (x, y, ringe = true) => pickBei(x, y, ringe),
      // Alle Strahltreffer durch einen Punkt (Client-Koordinaten), von vorn nach hinten; nur für Messungen.
      pickDetail(x, y) {
        const r = viewport.getBoundingClientRect();
        raycaster.setFromCamera(new THREE.Vector2((x - r.left) / r.width * 2 - 1, 1 - (y - r.top) / r.height * 2), camera);
        return raycaster.intersectObjects(pickable.filter(sichtbar), false).map((h) => ({ n: h.object.name, k: h.object.userData.schluessel, d: +h.distance.toFixed(3), w: !!h.object.userData.weich }));
      },
      snapshot() { renderer.render(scene, camera); return renderer.domElement.toDataURL('image/jpeg', .86); },
      // Simuliert Sekunden Laufzeit in einem Schritt (Federn, Kamerafahrten und Einblendungen sind zeitintegriert).
      simuliere(sekunden = 2) { uhrOffset += sekunden * 1000; schritt((lastTime || performance.now()) + sekunden * 1000, true); schritt(lastTime + 16, true); },
      // Diagnose: Fokus mit freier Blickrichtung (nur für Messungen von Standardblicken je Teil).
      fokusMit(keys, richtung, abstand) {
        const v = new THREE.Vector3(...richtung).normalize();
        model.updateMatrixWorld(true);
        fokussiere([], { dir: v, abstand, faktor: 1, quelle: 'fokus', region: ankerRegion(keys, v) });
      },
      nachricht,
      setProgress,
      setExactProgress(value) { stopAuto(); spring.reset(value); applyProgress(value); renderer.render(scene, camera); },
      resetView: defaultView,
      scene, camera,
    };
    window.addEventListener('pagehide', () => {
      disposed = true; cancelAnimationFrame(raf); resizeObserver.disconnect(); controls.dispose(); renderer.dispose();
    }, { once: true });
    // Ab jetzt nimmt die Schnittstelle Befehle an: wartende ausführen, erste Statusmeldung senden.
    bereit = true;
    for (const befehl of wartend.splice(0)) fuehreAus(befehl);
    melde(true);
    if (eltern) {
      setInterval(() => melde(false), 100);
      setInterval(() => melde(true), 500);
    }
  } catch (error) {
    console.error(error);
    fail('Bitte prüfen Sie, ob WebGL 2 im Browser verfügbar ist und die lokale Anwendung läuft. ' + error.message);
  }
}

init();
