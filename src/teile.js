// Zuordnung Schlüssel -> Meshes der GLB für die Einbettung ins Arbeitsblatt.
// Quelle der Namen: model/build_bee.py (identisch in bee-study.glb und bee-study-mobile.glb;
// tests/teile.test.mjs prüft das). Das Modell ist ein Prototyp: die Zuordnung benennt
// modellierte Teile, sie ist keine anatomische Abgrenzung.
//
// Felder je Schlüssel:
//   name    deutscher Anzeigename (Namensschild)
//   rang    Spezifität bei mehreren Treffern: 1 = Einzelteil, 2 = Beinpaar, 3 = Region (kleiner = spezieller)
//   gruppen RegExp gegen die bewegliche Gruppe (studyPart); alle Meshes darunter gehören dazu
//   meshen  RegExp gegen Meshnamen (zusätzlich zu gruppen)
//   anker   Einheiten für Schild/Nummer. { meshen: [Meshname] } = Mittelpunkt der Box dieser Meshes,
//           { punkt: [x, y, z], gruppe } = Punkt in Ruhelage (glTF-Koordinaten) + aktueller Gruppenversatz.
//           Bei mehreren Einheiten (z. B. links/rechts) wird die der Kamera nächste gewählt.
//   standard  erscheint bei beschriften {an:true} ohne Liste
//   fokusRichtung  Vektor vom Ziel zur Kamera (glTF-Koordinaten), den der Befehl fokus für dieses Teil nutzt, wenn er
//                  allein und ohne blick gesendet wird (Teile, die aus der Standardansicht verdeckt sind).

const SEITEN = ['-1', '1'];
const beinteil = (n) => SEITEN.map((s) => ({ meshen: [`leg_${n}_${s}_coxa_trochanter_femur_tibia`] }));

export const TEILE = {
  kopf: {
    name: 'Kopf', rang: 3, standard: true,
    gruppen: [/^head_(dorsal|ventral)_capsule$/],
    anker: [{ meshen: ['head_roof', 'head_floor'] }],
  },
  brust: {
    name: 'Brust', rang: 3, standard: true,
    gruppen: [/^thorax_(dorsal|ventral)_cuticle$/],
    anker: [{ meshen: ['thorax_roof', 'thorax_floor'] }],
  },
  hinterleib: {
    name: 'Hinterleib', rang: 3, standard: true,
    gruppen: [/^abdomen_(tergite|sternite)_[1-6]$/],
    anker: [{ meshen: ['tergite_3', 'tergite_4', 'sternite_3', 'sternite_4'] }],
  },
  fuehler: {
    name: 'Fühler', rang: 1, standard: true,
    gruppen: [/^antenna_-?1$/],
    anker: SEITEN.map((s) => ({ meshen: [`antenna_pedicel_flagellum_${s}`] })),
  },
  facettenauge: {
    // Die drei Punktaugen (three_ocelli) gehören nur zum Kopf, nicht zum Facettenauge.
    name: 'Facettenauge', rang: 1, standard: true,
    meshen: [/^compound_eye_(base_)?-?1$/, /^eye_setae_-?1$/],
    anker: SEITEN.map((s) => ({ meshen: [`compound_eye_${s}`] })),
  },
  ruessel: {
    // Glossa, Galeae und Labialpalpen. Die Mandibeln (paired_flattened_mandibles) zählen nicht dazu.
    name: 'Rüssel', rang: 1, standard: true,
    meshen: [/^folded_glossa_and_terminal_labellum$/, /^paired_galeae_folded$/, /^paired_labial_palps_folded$/],
    anker: [{ meshen: ['folded_glossa_and_terminal_labellum', 'paired_galeae_folded'] }],
    fokusRichtung: [-1, -0.6, 0], // von vorn unten: gemessen die größte Tippfläche (der Rüssel liegt unter dem Kopf)
  },
  fluegel: {
    name: 'Flügel', rang: 1, standard: true,
    gruppen: [/^(fore|hind)wing_-?1$/],
    anker: SEITEN.map((s) => ({ meshen: [`wing_membrane_${s}_False`] })),
  },
  bein: {
    name: 'Bein', rang: 3, standard: true,
    gruppen: [/^leg_[123]_-?1$/],
    anker: beinteil(2),
  },
  vorderbein: {
    name: 'Vorderbein', rang: 2,
    gruppen: [/^leg_1_-?1$/],
    anker: beinteil(1),
  },
  mittelbein: {
    name: 'Mittelbein', rang: 2,
    gruppen: [/^leg_2_-?1$/],
    anker: beinteil(2),
  },
  hinterbein: {
    name: 'Hinterbein', rang: 2,
    gruppen: [/^leg_3_-?1$/],
    anker: beinteil(3),
  },
  pollenkoerbchen: {
    // Konkave Hinterschiene (Tibia) der Hinterbeine. Sie liegt in der GLB nicht als eigenes Mesh vor,
    // sondern zusammen mit Coxa, Trochanter und Femur in leg_3_*_coxa_trochanter_femur_tibia. Beim Laden
    // wird sie daraus als Teilmesh herausgelöst (siehe ABGELEITET, src/teilung.js). Die GLB bleibt unverändert.
    // Die Randborsten (leg_3_*_setae) sind nicht abtrennbar und zählen nicht dazu.
    name: 'Pollenkörbchen', rang: 1,
    meshen: [/^leg_3_-?1_tibia_corbicula$/],
    anker: SEITEN.map((s) => ({ meshen: [`leg_3_${s}_tibia_corbicula`] })),
  },
  honigmagen: {
    name: 'Honigmagen', rang: 1, standard: true,
    meshen: [/^crop_honey_stomach$/],
    anker: [{ meshen: ['crop_honey_stomach'] }],
  },
  darm: {
    // Speiseröhre, Proventriculus, Mitteldarm, Enddarm, Rektalpolster. Ohne Honigmagen (eigener Schlüssel)
    // und ohne die Malpighi-Schläuche (Ausscheidungsorgane, kein Darmabschnitt).
    name: 'Darm', rang: 1, standard: true,
    meshen: [/^oesophagus$/, /^proventriculus_four_lip_regions$/, /^ventriculus_corrugated_midgut$/, /^ileum_rectum$/, /^six_rectal_pads$/],
    anker: [{ meshen: ['ventriculus_corrugated_midgut'] }],
  },
  herz: {
    name: 'Herz', rang: 1, standard: true,
    gruppen: [/^system_dorsal_vessel$/],
    anker: [{ punkt: [0.9, 0.5, 0], gruppe: 'system_dorsal_vessel' }],
    fokusRichtung: [0, 0.2, 1], // von der Seite: in der Explosion sonst vom Rückenschild verdeckt
  },
  gehirn: {
    // Das Mesh enthält Gehirn, Sehlappen und das Bauchmark mit seinen Ganglien in einem Stück.
    name: 'Gehirn', rang: 1, standard: true,
    gruppen: [/^system_nervous$/],
    anker: [{ punkt: [-1.74, 0.22, 0], gruppe: 'system_nervous' }],
    fokusRichtung: [-1, 0.6, 0.2], // von vorn oben: Gehirn liegt hinter Augen und Flugmuskeln
  },
  flugmuskeln: {
    name: 'Flugmuskeln', rang: 1, standard: true,
    gruppen: [/^system_flight_muscles$/],
    anker: [{ meshen: ['longitudinal_and_dorsoventral_flight_fibres'] }],
  },
  stachel: {
    // Stachelplatten mit Stechborsten plus die Giftblase mit Ausführungsgängen. Die Giftblase steckt in
    // hypopharyngeal_mandibular_venom_glands (zusammen mit den Kopfdrüsen) und wird beim Laden abgetrennt.
    name: 'Stachel', rang: 1, standard: true,
    meshen: [/^sting_plates_paired_lancets$/, /^venom_sac_and_ducts$/],
    anker: [{ meshen: ['sting_plates_paired_lancets'] }],
    fokusRichtung: [0.4, -0.5, 1], // von der Seite, leicht von hinten unten (im Situs verdecken Enddarm und Platten ihn sonst)
  },
  luftsaecke: {
    // Das ganze Atmungssystem der Gruppe system_tracheal: Luftsack-Membranen und die darin liegenden
    // Tracheenstämme. Tracheen sind kein eigener Schlüssel; sie liegen sichtbar innerhalb der Säcke.
    name: 'Luftsäcke', rang: 1, standard: true,
    gruppen: [/^system_tracheal$/],
    anker: [{ punkt: [1.28, -0.04, 0.59], gruppe: 'system_tracheal' }, { punkt: [1.28, -0.04, -0.59], gruppe: 'system_tracheal' }],
  },
};

export const SCHLUESSEL = Object.keys(TEILE);
export const STANDARD_SCHILDER = SCHLUESSEL.filter((k) => TEILE[k].standard);

// Teilmeshes, die beim Laden aus einem vorhandenen Mesh herausgelöst werden (Regel: src/teilung.js).
export const ABGELEITET = [
  { quelle: /^leg_3_(-?1)_coxa_trochanter_femur_tibia$/, regel: 'tibia', name: (q) => q.replace('coxa_trochanter_femur_tibia', 'tibia_corbicula') },
  { quelle: /^hypopharyngeal_mandibular_venom_glands$/, regel: 'giftblase', name: () => 'venom_sac_and_ducts' },
];

const REIHENFOLGE = new Map(SCHLUESSEL.map((k, i) => [k, i]));

// Alle Schlüssel, die auf ein Mesh passen, der speziellste zuerst.
export function schluesselFuer(gruppe, mesh) {
  const treffer = SCHLUESSEL.filter((k) => {
    const t = TEILE[k];
    return (t.gruppen ?? []).some((r) => r.test(gruppe)) || (t.meshen ?? []).some((r) => r.test(mesh));
  });
  return treffer.sort((a, b) => TEILE[a].rang - TEILE[b].rang || REIHENFOLGE.get(a) - REIHENFOLGE.get(b));
}

export const teilInfo = () => SCHLUESSEL.map((name) => ({ name, label: TEILE[name].name }));
