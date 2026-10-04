// Hervorhebung und kurzes Aufleuchten über Material-Klone. Die Originalmaterialien werden nie verändert;
// beim Aufheben bekommt jedes Mesh exakt sein ursprüngliches Material zurück.
import * as THREE from 'three';

const GHOST = 0.14;      // Deckkraft nicht gewählter Teile (bei bereits durchsichtigen Materialien anteilig)
const FADE = 0.35;       // Sekunden für Ein-/Ausblenden
const AMBER = new THREE.Color(0xffa63a);
// Nur-Tiefe-Material: Innenorgane sind ineinander verschachtelt (Muskelfasern, Tubuli, Drüsen). Ohne Vorpass
// summieren sich ihre Ghost-Schichten zu fast voller Deckkraft; mit Vorpass bleibt je Bildpunkt die vorderste.
const TIEFE = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: true, transparent: true, side: THREE.DoubleSide });

export class Hervorhebung {
  // eintraege: [{ mesh, schluessel: [..] }]
  constructor(eintraege) {
    this.eintraege = eintraege;
    this.aktiv = new Set();     // gewählte Schlüssel
    this.faktor = 0;            // 0 = alles normal, 1 = voll hervorgehoben
    this.blitz = null;          // { key, t0 }
    this.klone = new Map();     // Originalmaterial -> { ghost, bold, flash }
    this.zustand = 'normal';    // zuletzt zugewiesene Materialart
    this.zeit = 0;
  }

  get an() { return this.aktiv.size > 0; }
  get meshes() { return this.eintraege.filter((e) => this.#gewaehlt(e)).map((e) => e.mesh); }
  #gewaehlt(e) { return e.schluessel.some((k) => this.aktiv.has(k)); }

  setze(schluessel) {
    this.aktiv = new Set(schluessel);
    this.#zuweisen();
  }

  leuchte(schluessel, dauer = 0.9) {
    this.blitz = schluessel ? { key: schluessel, dauer, t0: this.zeit } : null;
    this.#zuweisen();
  }

  #vorpass(e) {
    if (!e.pre) {
      e.pre = new THREE.Mesh(e.mesh.geometry, TIEFE);
      e.pre.renderOrder = -1;
      e.pre.raycast = () => {};
      e.mesh.add(e.pre);
    }
    return e.pre;
  }

  #klon(material) {
    let k = this.klone.get(material);
    if (k) return k;
    const basis = material.opacity;
    const ghost = material.clone();
    ghost.transparent = true; ghost.depthWrite = false;
    ghost.userData.basis = basis; ghost.userData.ziel = material.transparent ? basis * 0.4 : GHOST; ghost.userData.opak = !material.transparent;
    const bold = material.clone();
    bold.emissive = AMBER.clone(); bold.emissiveIntensity = 0.15;
    // Schon durchsichtige Teile (Flügel, Luftsäcke) werden gewählt kräftiger, sonst bliebe die Auswahl unsichtbar.
    if (material.transparent) { bold.opacity = Math.min(0.8, basis * 4); bold.userData.glimmer = 2.4; }
    const flash = material.clone();
    flash.emissive = new THREE.Color(0xffd27a); flash.emissiveIntensity = 0;
    if (material.transparent) flash.opacity = Math.min(0.7, basis * 3.4);
    k = { ghost, bold, flash };
    this.klone.set(material, k);
    return k;
  }

  // Weist jedem Mesh Original-, Ghost-, Bold- oder Flash-Material zu (nur bei Zustandswechsel).
  #zuweisen() {
    const hervor = this.an || this.faktor > 0;
    for (const e of this.eintraege) {
      const orig = e.mesh.userData.original ?? (e.mesh.userData.original = e.mesh.material);
      const blitzt = this.blitz && e.schluessel.includes(this.blitz.key);
      let art = 'normal';
      if (blitzt) art = 'flash';
      else if (hervor) art = this.#gewaehlt(e) && this.an ? 'bold' : 'ghost';
      const ziel = art === 'normal' ? orig : this.#klon(orig)[art];
      if (e.mesh.material !== ziel) e.mesh.material = ziel;
      if (e.mesh.userData.organ) this.#vorpass(e).visible = art === 'ghost';
      // Gewählte durchsichtige Teile (Flügel, Luftsäcke) werden vor den Tiefen-Vorpässen gezeichnet.
      const ro = e.mesh.userData.ro ?? (e.mesh.userData.ro = e.mesh.renderOrder);
      e.mesh.renderOrder = art === 'bold' && orig.transparent ? ro - 5 : ro;
    }
  }

  // Pro Frame: Ein-/Ausblenden, Pulsieren, Blitz. Gibt true zurück, solange sich etwas ändert.
  aktualisiere(dt, ruhig = false) {
    this.zeit += dt;
    const sollFaktor = this.an ? 1 : 0;
    const vorher = this.faktor;
    if (this.faktor !== sollFaktor) {
      const schritt = dt / FADE;
      this.faktor = sollFaktor > this.faktor ? Math.min(1, this.faktor + schritt) : Math.max(0, this.faktor - schritt);
      // Beim Ausblenden kommen die Ghost-Materialien erst zurück zur Originaldeckkraft, dann die Originale.
      if (vorher === 0 || this.faktor === 0) this.#zuweisen();
    }
    const pulsieren = ruhig ? 0.22 : 0.17 + 0.13 * Math.sin(this.zeit * 3.4);
    const f = this.faktor * this.faktor * (3 - 2 * this.faktor);
    for (const k of this.klone.values()) {
      k.ghost.opacity = k.ghost.userData.basis + (k.ghost.userData.ziel - k.ghost.userData.basis) * f;
      k.ghost.depthWrite = k.ghost.userData.opak && f < 0.5;
      k.bold.emissiveIntensity = pulsieren * this.faktor * (k.bold.userData.glimmer ?? 1);
    }
    if (this.blitz) {
      const u = (this.zeit - this.blitz.t0) / this.blitz.dauer;
      const wert = u >= 1 ? 0 : 1.1 * (1 - u) * (1 - u);
      for (const k of this.klone.values()) k.flash.emissiveIntensity = wert;
      if (u >= 1) { this.blitz = null; this.#zuweisen(); }
    }
    return this.an || this.faktor > 0 || !!this.blitz;
  }
}
