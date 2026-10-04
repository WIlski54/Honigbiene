// Herauslösen von Teilmeshes aus einem Mesh nach zusammenhängenden Dreiecksgruppen.
// Rein funktional (Typed Arrays), damit Tests und Browser denselben Code nutzen.

// Zusammenhangskomponenten über gemeinsame Vertexindizes.
export function komponenten(index, vertexAnzahl) {
  const eltern = new Int32Array(vertexAnzahl).map((_, i) => i);
  const wurzel = (v) => {
    while (eltern[v] !== v) { eltern[v] = eltern[eltern[v]]; v = eltern[v]; }
    return v;
  };
  for (let i = 0; i < index.length; i += 3) {
    const a = wurzel(index[i]);
    eltern[wurzel(index[i + 1])] = a;
    eltern[wurzel(index[i + 2])] = wurzel(a);
  }
  const nummer = new Map();
  const dreieck = new Int32Array(index.length / 3);
  for (let t = 0; t < dreieck.length; t++) {
    const w = wurzel(index[t * 3]);
    if (!nummer.has(w)) nummer.set(w, nummer.size);
    dreieck[t] = nummer.get(w);
  }
  return { dreieck, anzahl: nummer.size };
}

// Dreieckszahl und Schwerpunkt je Komponente; position(i) -> [x, y, z] des Vertex i im Modellraum.
export function schwerpunkte(index, zerlegung, position) {
  const liste = Array.from({ length: zerlegung.anzahl }, () => ({ dreiecke: 0, summe: [0, 0, 0] }));
  for (let t = 0; t < zerlegung.dreieck.length; t++) {
    const k = liste[zerlegung.dreieck[t]];
    k.dreiecke++;
    for (let e = 0; e < 3; e++) {
      const p = position(index[t * 3 + e]);
      k.summe[0] += p[0]; k.summe[1] += p[1]; k.summe[2] += p[2];
    }
  }
  return liste.map((k) => ({ dreiecke: k.dreiecke, mitte: k.summe.map((s) => s / (k.dreiecke * 3)) }));
}

// Regeln: wählen aus den Komponenten (Index-Menge) das gesuchte Teil. Annahmen stehen in teile.js.
export const REGELN = {
  // Hinterschiene: von den vier Rohrsegmenten (Coxa, Trochanter, Femur, Tibia) das am weitesten seitlich
  // liegende (z im Modellraum = Abstand von der Körpermitte).
  tibia(komp) {
    if (komp.length !== 4) return new Set();
    let best = 0;
    komp.forEach((k, i) => { if (Math.abs(k.mitte[2]) > Math.abs(komp[best].mitte[2])) best = i; });
    return new Set([best]);
  },
  // Giftblase mit Gängen: Komponenten im Hinterleib (x > 1); die Kopfdrüsen liegen bei x < -1,7.
  giftblase(komp) {
    return new Set(komp.map((k, i) => (k.mitte[0] > 1 ? i : -1)).filter((i) => i >= 0));
  },
};

// Dreiecksnummern der gewählten Komponenten und der übrigen.
export function teileDreiecke(zerlegung, auswahl) {
  const drin = [], draussen = [];
  zerlegung.dreieck.forEach((k, t) => (auswahl.has(k) ? drin : draussen).push(t));
  return { drin, draussen };
}
