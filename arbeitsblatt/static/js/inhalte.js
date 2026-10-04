// Inhalte des interaktiven Arbeitsblatts „Die Honigbiene – ein Nutztier mit eigenem Staat“
// NW · Klasse 6 · Gesamtschule Meiderich · Klassenunterricht (heterogene Klasse, Niveau A/B/C je Aufgabe)
//
// DIESE DATEI IST NUR DER KOPF. Die Aufgaben stehen je Reiter in einer eigenen Datei, die sich anhängt:
//   inhalte_nutztier.js · inhalte_koerper.js · inhalte_volk.js · inhalte_nutzen.js · inhalte_abschluss.js
// (Ladereihenfolge in templates/index.html = Reihenfolge der Reiter). Jede Datei ist ein IIFE
// `(() => { … INHALTE.tabs.push({ … }); })();` – so kollidieren Konstanten wie FILM_ZEITEN nicht.
// Niemand bearbeitet die Datei eines anderen Reiters.
//
// Aufgabennummern sind FEST und müssen zu ABSCHNITTE in config.py passen (AB_KONZEPT.md).
// Format aller Aufgabentypen mit Beispielen: docs/INHALTE_FORMAT.md.
// Sprache: kurze Sätze (höchstens etwa 15 Wörter), einfache Wörter, Fakten unverändert.
//
// Differenzierung in drei Stufen – die Klasse ist sehr heterogen:
//   A  Antippen statt Schreiben, Bildhilfen, kurze Sätze. Auch Transfer und Beurteilung laufen hier über
//      Textbausteine (modus: "bausteine").
//   B  Mittleres Niveau: Wortspeicher, Satzanfänge, kürzere Mindestlängen.
//   C  Freie Formulierung, Begründung, Beurteilung.

window.INHALTE = {
  titel: "Die Honigbiene – ein Nutztier mit eigenem Staat",

  // ─── Filme und 3D-Modell (Baustein film.js; Protokoll: AB_KONZEPT.md) ──────────────────────
  // Die Dateien liegen unter static/film/. Das 3D-Modell baut `npm run build:ab` im Elternprojekt (nicht von Hand ändern);
  // ohne echtes Modell testet werkzeuge/modell_attrappe.html das Protokoll. Der Film ist bis zur Fertigstellung des
  // Papiertheaters eine Attrappe (static/film/Ein_Bienenvolk_im_Bienenstock.html, gleiches Protokoll).
  filme: {
    biene3d: { art: "modell3d", datei: "/static/film/bienenmodell/index.html?embed=1", titel: "Die Honigbiene in 3D" },
    volk: { art: "papiertheater", datei: "/static/film/Ein_Bienenvolk_im_Bienenstock.html", titel: "Ein Bienenvolk im Bienenstock" },
  },

  // ─── Bilder mit antippbaren Punkten (Aufgabentyp „bildpunkte“) ────────────────────────────
  // Je Bild: INHALTE.bildpunkte.<name> = { bild, breite, hoehe, punkte: [{ id, x, y, name, aliase, kat }] }.
  // Jeder Reiter trägt seine Karten selbst ein (inhalte_<reiter>.js). Koordinaten gehören zur SVG-Datei.
  bildpunkte: {},

  // ─── Reiter ───────────────────────────────────────────────────────────────────────────────
  // Jede Datei inhalte_<reiter>.js hängt genau einen Eintrag an. Reihenfolge = Reihenfolge der Reiter.
  tabs: [],
};
