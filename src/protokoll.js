// Schnittstelle zum einbettenden Arbeitsblatt (postMessage, Feld "mw"). Rein funktionale Teile,
// ohne DOM und ohne three.js, damit sie unter Node getestet werden können.
// Protokoll: siehe AB_KONZEPT.md, Abschnitt "Das 3D-Modell im AB (Schnittstelle)".
import { SCHLUESSEL, TEILE, teilInfo } from './teile.js';

export const ANSICHTEN = Object.freeze([
  { name: 'gestalt', label: 'Außen', wert: 0 },
  { name: 'situs', label: 'Innen', wert: 0.55 },
  { name: 'explosion', label: 'Explosion', wert: 1 },
]);

// richtung: Vektor vom Ziel zur Kamera (glTF-Koordinaten, Kopf bei -x, Betrachter bei +z = Körperseite -1).
export const BLICKE = Object.freeze([
  { name: 'schraeg', label: 'Schräg', richtung: [-3.7, 6.8, 9.4] },
  { name: 'seite', label: 'Von der Seite', richtung: [0, 0.05, 1] },
  { name: 'oben', label: 'Von oben', richtung: [0, 1, 0.02] },
  { name: 'vorn', label: 'Von vorn', richtung: [-1, 0.05, 0] },
  { name: 'hinten', label: 'Von hinten', richtung: [1, 0.05, 0] },
]);

const clamp01 = (v) => Math.max(0, Math.min(1, v));

// Dieselben Schwellen wie die Voreinstellungs-Knöpfe in main.js.
export function ansichtVon(p) {
  if (p < 0.04) return 'gestalt';
  if (Math.abs(p - 0.55) < 0.055) return 'situs';
  if (p > 0.96) return 'explosion';
  return 'zwischen';
}

export const ansichtLabel = (name, p = 0) =>
  name === 'zwischen' ? 'Zwischenstand' : ANSICHTEN.find((a) => a.name === name)?.label ?? String(p);

export function standText(name, p) {
  if (name === 'gestalt') return 'Außenansicht';
  if (name === 'situs') return 'Innenansicht (Situs)';
  if (name === 'explosion') return 'Explosionsansicht';
  return `Öffnung ${Math.round(p * 100)} %`;
}

// Erkundungsfortschritt: eine Ansicht gilt als gesehen, sobald der Regler in ihrer Nähe (±0,06) war.
// "vorher" ist der Wert des letzten Frames: Das Intervall zwischen beiden zählt, damit ein schneller
// Sprung (z. B. von Außen direkt zu Explosion) die Situs-Zone nicht je nach Bildrate überspringt.
export function aktualisiereBesucht(besucht, p, vorher = p) {
  const anzahl = besucht.size;
  const lo = Math.min(p, vorher), hi = Math.max(p, vorher);
  if (lo <= 0.06) besucht.add('gestalt');
  if (hi >= 0.55 - 0.06 - 1e-9 && lo <= 0.55 + 0.06 + 1e-9) besucht.add('situs');
  if (hi >= 0.94) besucht.add('explosion');
  return besucht.size !== anzahl;
}

export const gesehenProzent = (besucht) => Math.round((besucht.size / ANSICHTEN.length) * 100);

export function statusObjekt(z) {
  const ansicht = ansichtVon(z.fortschritt);
  return {
    mw: 'status', art: 'modell3d', t: 0, laeuft: !!z.laeuft, live: false,
    ansicht, ansichtLabel: ansichtLabel(ansicht, z.fortschritt),
    fortschritt: Math.round(z.fortschritt * 1000) / 1000,
    gesehen: gesehenProzent(z.besucht),
    besucht: ANSICHTEN.map((a) => a.name).filter((n) => z.besucht.has(n)),
    freigeschaltet: true,
    standText: standText(ansicht, z.fortschritt),
    blick: z.blick, waehlen: !!z.waehlen, hervorgehoben: [...(z.hervorgehoben ?? [])], leiste: z.leiste !== false, bereit: true,
  };
}

export const infoObjekt = () => ({
  mw: 'info', art: 'modell3d',
  ansichten: ANSICHTEN.map(({ name, label }) => ({ name, label })),
  blicke: BLICKE.map(({ name, label }) => ({ name, label })),
  teile: teilInfo(),
});

const bekannt = new Set(SCHLUESSEL);
const liste = (v) => (Array.isArray(v) ? v.filter((x) => typeof x === 'string') : []);

// Prüft eine eingehende Nachricht. Gibt ein normalisiertes Kommando oder null zurück (unbekannt/ungültig).
export function parseBefehl(m) {
  if (!m || typeof m !== 'object' || typeof m.mw !== 'string') return null;
  switch (m.mw) {
    case 'info': case 'status': case 'spielen': case 'anhalten': case 'freischalten': case 'springe': case 'zurueck':
      return { typ: m.mw };
    case 'ansicht': {
      const a = ANSICHTEN.find((x) => x.name === m.name);
      if (a) return { typ: 'ansicht', wert: a.wert };
      const w = Number(m.wert);
      return m.wert !== undefined && m.wert !== null && m.wert !== '' && Number.isFinite(w) ? { typ: 'ansicht', wert: clamp01(w) } : null;
    }
    case 'blick':
      return BLICKE.some((b) => b.name === m.name) ? { typ: 'blick', name: m.name } : null;
    case 'hervorheben':
      return { typ: 'hervorheben', teile: [...new Set(liste(m.teile).filter((k) => bekannt.has(k)))], fokus: m.fokus === true };
    case 'beschriften':
      return { typ: 'beschriften', an: m.an !== false, teile: [...new Set(liste(m.teile).filter((k) => bekannt.has(k)))] };
    case 'nummern':
      // Position in der Liste = Nummer; unbekannte Schlüssel lassen ihre Nummer aus.
      return { typ: 'nummern', teile: liste(m.teile).map((k) => (bekannt.has(k) ? k : null)) };
    case 'waehlen':
      return { typ: 'waehlen', an: m.an !== false };
    case 'leiste':
      return { typ: 'leiste', an: m.an !== false };
    case 'fokus': {
      // Kamerafahrt zu den Teilen ohne Markierung; teile:[] fährt zurück. blick und abstand (Modelleinheiten) optional.
      const abstand = Number(m.abstand);
      return {
        typ: 'fokus',
        teile: [...new Set(liste(m.teile).filter((k) => bekannt.has(k)))],
        blick: BLICKE.some((b) => b.name === m.blick) ? m.blick : null,
        abstand: Number.isFinite(abstand) && abstand > 0 ? abstand : null,
      };
    }
    default:
      return null;
  }
}

// Wählmodus: Treffer von vorn nach hinten (abstand aufsteigend), je { weich, rohname, teile: [Schlüssel, speziellster zuerst] }.
// Gewählt wird der erste feste Treffer mit Schlüssel. Durchsichtige Membranen (Flügel, Luftsack-Membranen: weich) und
// Meshes ohne Schlüssel (Malpighi-Schläuche, Fettkörper, Drüsen: nicht antwortfähig) blockieren dahinterliegende Teile nicht.
// Gibt es dahinter nichts Festes mit Schlüssel, gilt eine Membran mit Schlüssel (Flügel bzw. Luftsäcke sind so antippbar),
// sonst der erste Treffer überhaupt (teil: null).
// darunter: Schlüssel aller anderen Treffer entlang des Strahls (vorn nach hinten), davor: Meshnamen der übergangenen
// Treffer vor dem gewählten. Die Fachseite kann damit selbst entscheiden.
export function entscheideTipp(treffer) {
  const sortiert = [...treffer].sort((a, b) => a.abstand - b.abstand);
  const gewaehlt = sortiert.find((t) => !t.weich && t.teile.length) ?? sortiert.find((t) => t.teile.length) ?? sortiert[0];
  if (!gewaehlt) return { teil: null, teile: [], rohname: null, darunter: [], davor: [] };
  const eigene = new Set(gewaehlt.teile);
  const darunter = [...new Set(sortiert.filter((t) => t !== gewaehlt).flatMap((t) => t.teile))].filter((k) => !eigene.has(k));
  const davor = sortiert.slice(0, sortiert.indexOf(gewaehlt)).map((t) => t.rohname);
  return { teil: gewaehlt.teile[0] ?? null, teile: [...gewaehlt.teile], rohname: gewaehlt.rohname, darunter, davor };
}

export const anzeigeName = (k) => TEILE[k]?.name ?? k;
