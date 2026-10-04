// Namensschilder und nummerierte Markierungen als HTML-Overlay über dem Modell.
// legeSchilderAus() ist rein funktional (testbar); Schilder verwaltet die DOM-Elemente.
import { smoothstep } from './motion.js';

// Erst die Aussenbeschriftung abbauen, dann die Innenbeschriftung zeigen, ohne beide zu stapeln.
export function schildDeckkraft({ typ, innen, automatisch, organsShown, fortschritt }) {
  if (innen && !organsShown) return 0;
  if (typ !== 'name' || !automatisch) return 1;
  return innen ? smoothstep(0.32, 0.55, fortschritt) : 1 - smoothstep(0.05, 0.27, fortschritt);
}

const WINKEL = [0, 40, -40, 80, -80, 120, -120, 160, 180].map((g) => (g * Math.PI) / 180);
const RADIEN_NAME = [16, 40, 70, 105, 145];
const RADIEN_NUMMER = [0, 26, 48, 74, 104];

// items: [{ id, ax, ay, w, h, typ: 'name' | 'nummer' }] mit Ankerpunkt (ax, ay) in Pixeln.
// Rückgabe je Item: { id, x, y, ax, ay, linie } mit linker oberer Ecke (x, y); linie = Verbindungslinie nötig.
// Schilder wandern radial vom Modellmittelpunkt weg und weichen einander (und dem Rand) aus.
export function legeSchilderAus(items, { breite, hoehe, unten = 0, rand = 6, abstand = 4, mitte = [breite / 2, hoehe / 2], gedaechtnis = new Map() }) {
  const platziert = [];
  const ergebnis = [];
  const frei = (k) => k.x >= rand && k.y >= rand && k.x + k.w <= breite - rand && k.y + k.h <= hoehe - unten - rand
    && platziert.every((p) => k.x >= p.x + p.w + abstand || k.x + k.w + abstand <= p.x || k.y >= p.y + p.h + abstand || k.y + k.h + abstand <= p.y);
  const ueberlappung = (k) => platziert.reduce((s, p) => s + Math.max(0, Math.min(k.x + k.w, p.x + p.w) - Math.max(k.x, p.x)) * Math.max(0, Math.min(k.y + k.h, p.y + p.h) - Math.max(k.y, p.y)), 0);
  for (const it of items) {
    const dx = it.ax - mitte[0], dy = it.ay - mitte[1];
    const basis = Math.hypot(dx, dy) < 1 ? -Math.PI / 2 : Math.atan2(dy, dx);
    const radien = it.typ === 'nummer' ? RADIEN_NUMMER : RADIEN_NAME;
    const kandidaten = [];
    radien.forEach((r, ri) => WINKEL.forEach((w, wi) => {
      if (r === 0 && wi > 0) return;
      const c = Math.cos(basis + w), s = Math.sin(basis + w);
      const ausdehnung = it.typ === 'nummer' ? 0 : Math.abs(c) * it.w / 2 + Math.abs(s) * it.h / 2;
      const cx = it.ax + c * (r + ausdehnung), cy = it.ay + s * (r + ausdehnung);
      kandidaten.push({ id: ri * 100 + wi, x: Math.round(cx - it.w / 2), y: Math.round(cy - it.h / 2), w: it.w, h: it.h });
    }));
    const letzte = gedaechtnis.get(it.id);
    if (letzte !== undefined) kandidaten.sort((a, b) => (b.id === letzte) - (a.id === letzte));
    let wahl = kandidaten.find(frei);
    if (!wahl) {
      // Kein freier Platz: den Kandidaten mit der kleinsten Überlappung nehmen, in den Rahmen geschoben.
      wahl = kandidaten.map((k) => ({
        ...k,
        x: Math.max(rand, Math.min(breite - rand - k.w, k.x)),
        y: Math.max(rand, Math.min(hoehe - unten - rand - k.h, k.y)),
      })).reduce((best, k) => (!best || ueberlappung(k) < ueberlappung(best) ? k : best), null);
    }
    gedaechtnis.set(it.id, wahl.id);
    platziert.push(wahl);
    // Nächster Punkt des Schildes zum Anker bestimmt, ob und wohin die Linie führt.
    const nx = Math.max(wahl.x, Math.min(wahl.x + wahl.w, it.ax)), ny = Math.max(wahl.y, Math.min(wahl.y + wahl.h, it.ay));
    ergebnis.push({ id: it.id, x: wahl.x, y: wahl.y, ax: it.ax, ay: it.ay, nx, ny, linie: Math.hypot(nx - it.ax, ny - it.ay) > 3 });
  }
  return ergebnis;
}

const SVG = 'http://www.w3.org/2000/svg';

export class Schilder {
  constructor(container) {
    this.container = container;
    this.eintraege = []; // { id, typ, text, el }
    this.svg = document.createElementNS(SVG, 'svg');
    this.svg.setAttribute('class', 'schilder-linien');
    this.svg.setAttribute('aria-hidden', 'true');
    container.append(this.svg);
    this.gedaechtnis = new Map();
    this.groesse = '';
  }

  // liste: [{ id, typ: 'name' | 'nummer', text }] in Zeichenreihenfolge.
  setze(liste) {
    const gleich = liste.length === this.eintraege.length && liste.every((e, i) => e.id === this.eintraege[i].id && e.typ === this.eintraege[i].typ && e.text === this.eintraege[i].text && e.automatisch === this.eintraege[i].automatisch);
    if (gleich) return;
    for (const e of this.eintraege) { e.el.remove(); e.linie.remove(); e.punkt.remove(); }
    this.gedaechtnis.clear();
    this.eintraege = liste.map((e) => {
      const el = document.createElement('div');
      el.className = `schild ${e.typ === 'nummer' ? 'schild-nummer' : 'schild-name'} aus`;
      el.classList.toggle('schild-auto', e.automatisch === true);
      el.textContent = e.text;
      el.dataset.teil = e.id;
      this.container.append(el);
      const linie = document.createElementNS(SVG, 'line');
      const punkt = document.createElementNS(SVG, 'circle');
      punkt.setAttribute('r', '4');
      this.svg.append(linie, punkt);
      return { ...e, el, linie, punkt, w: 0, h: 0 };
    });
    this.messen();
  }

  messen() {
    for (const e of this.eintraege) { e.w = e.el.offsetWidth; e.h = e.el.offsetHeight; }
  }

  get leer() { return this.eintraege.length === 0; }

  // anker: Map id -> { x, y } in Pixeln oder null/undefined (Teil gerade nicht sichtbar).
  zeichne(anker, breite, hoehe, unten = 0, deckkraft = new Map()) {
    const key = `${breite}x${hoehe}`;
    if (key !== this.groesse) { this.groesse = key; this.svg.setAttribute('viewBox', `0 0 ${breite} ${hoehe}`); this.svg.setAttribute('width', breite); this.svg.setAttribute('height', hoehe); }
    const sichtbar = this.eintraege.filter((e) => anker.get(e.id));
    if (sichtbar.some((e) => !e.w)) this.messen();
    const layout = new Map(legeSchilderAus(sichtbar.map((e) => ({ id: e.id, typ: e.typ, w: e.w, h: e.h, ax: anker.get(e.id).x, ay: anker.get(e.id).y })), { breite, hoehe, unten, gedaechtnis: this.gedaechtnis }).map((l) => [l.id, l]));
    for (const e of this.eintraege) {
      const l = layout.get(e.id);
      const opacity = l ? (deckkraft.get(e.id) ?? 1) : 0;
      e.el.classList.toggle('aus', !l);
      e.el.style.opacity = e.linie.style.opacity = e.punkt.style.opacity = String(opacity);
      e.el.setAttribute('aria-hidden', String(opacity === 0));
      e.linie.style.display = e.punkt.style.display = l ? '' : 'none';
      if (!l) continue;
      e.el.style.transform = `translate(${l.x}px, ${l.y}px)`;
      e.linie.setAttribute('x1', l.ax.toFixed(1)); e.linie.setAttribute('y1', l.ay.toFixed(1));
      e.linie.setAttribute('x2', l.nx.toFixed(1)); e.linie.setAttribute('y2', l.ny.toFixed(1));
      e.linie.style.display = l.linie ? '' : 'none';
      e.punkt.setAttribute('cx', l.ax.toFixed(1)); e.punkt.setAttribute('cy', l.ay.toFixed(1));
      e.punkt.style.display = e.typ === 'nummer' && !l.linie ? 'none' : '';
    }
  }
}
