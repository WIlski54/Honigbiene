// Reiter 5 „Abschluss & Quellen“ – Stationen: 80 (Mein Forscherbuch), 38 (Blitzfragen), 39 (Domino), 40 (Quellen), T (Transfer)
// Reihenfolge und Dramaturgie: plan_abschluss.py. Kein Film, keine Lesestrecke. Der Reiter wiederholt aus ALLEN Reitern
// (Nutztier, Körperbau, Bienenvolk, Nutzen & Schutz).
// Nur Fakten aus „Gesicherte Fakten“ in AB_KONZEPT.md; dieselben Wörter wie in den Lesestrecken, im Film und im 3D-Modell.
// Format aller Aufgabentypen: docs/INHALTE_FORMAT.md.
(() => {
  "use strict";

  INHALTE.tabs.push({
    key: "abschluss", label: "Abschluss & Quellen", icon: "🏁", kurz: "A",
    intro: {
      eyebrow: "Abschluss", titel: "Alles zusammen",
      begriffe: [],
    },
    aufgaben: [
      // ── 80 · Mein Forscherbuch: sammelt automatisch alle Forscherfragen, Vermutungen, Erkenntnisse und Notizen ──
      // Das Modul liest nur (Autosave bleibt bei den Aufgaben); Druckansicht und „Text kopieren“ sind eingebaut.
      {
        nr: 80, typ: "forscherbuch", eyebrow: "Mein Forscherbuch", titel: "Das habe ich herausgefunden",
        hinweis: "Hier stehen deine Forscherfragen, deine Vermutungen und deine Erkenntnisse aus allen Reitern. Lies sie in Ruhe durch. Schau auch auf deine Fragen an den Imker aus dem ersten Reiter. Welche deiner Fragen vom Anfang ist jetzt beantwortet? Du kannst dein Forscherbuch drucken oder als PDF sichern.",
      },

      // ── 38 · Blitzfragen: 31 Fragen aus allen Reitern, Stufe 1 Grundbegriffe, Stufe 3 Zusammenhang ──
      // Stufe 1: 14 Fragen (A braucht 6 richtige), Stufe 2: 10 Fragen (B: 8 richtige aus Stufe 1+2), Stufe 3: 7 Fragen (C: 10 richtige).
      // Die Fragen stützen sich auf die Erkenntnissätze der Reiter (Forscherbuch): Nutztier 43 (Tabelle), Die Biene 52/54/55, Bienenvolk 61–64/66, Nutzen & Schutz 71/72/76.
      // Die richtige Option steht nicht immer an derselben Stelle (ok = Index). Der Client mischt die Antworten ohnehin.
      {
        nr: 38, typ: "blitz", eyebrow: "Blitzfragen", titel: "Blitzrunde",
        hinweis: "Jede Frage kommt nur einmal. Die Antworten werden jedes Mal neu gemischt.",
        niveaus: {
          A: { ziel: 6, stufen: [1], hinweis: "Beantworte sechs leichte Fragen richtig. Es geht um die Grundbegriffe." },
          B: { ziel: 8, stufen: [1, 2], hinweis: "Beantworte acht Fragen richtig. Sie sind leicht und mittel." },
          C: { ziel: 10, stufen: [1, 2, 3], hinweis: "Beantworte zehn Fragen richtig. Auch die schweren, mit Zusammenhang, sind dabei." },
        },
        pool: [
          // Stufe 1 – Grundbegriffe
          { id: "b01", stufe: 1, frage: "Wer kümmert sich um das Bienenvolk im Bienenkasten?", optionen: ["Der Förster", "Der Imker", "Der Bäcker"], ok: 1 },
          { id: "b02", stufe: 1, frage: "Was ist ein Nutztier?", optionen: ["Ein Tier, das nur im Wald lebt", "Ein Tier, das nur zum Streicheln da ist", "Ein Tier, das Menschen halten, weil es ihnen etwas gibt"], ok: 2 },
          { id: "b03", stufe: 1, frage: "Was bekommen wir von der Honigbiene?", optionen: ["Honig, Wachs und Hilfe bei der Bestäubung", "Milch, Eier und Wolle", "Fleisch und Leder"], ok: 0 },
          { id: "b04", stufe: 1, frage: "Wie viele Beine hat eine Biene?", optionen: ["Vier", "Acht", "Sechs"], ok: 2 },
          { id: "b05", stufe: 1, frage: "Aus wie vielen Körperteilen besteht eine Biene?", optionen: ["Zwei", "Drei", "Vier"], ok: 1 },
          { id: "b06", stufe: 1, frage: "Welcher Körperteil trägt die Flügel der Biene?", optionen: ["Die Brust", "Der Kopf", "Der Hinterleib"], ok: 0 },
          { id: "b07", stufe: 1, frage: "Wer legt im Bienenstock die Eier?", optionen: ["Die Drohne", "Die Wächterin", "Die Königin"], ok: 2 },
          { id: "b08", stufe: 1, frage: "Wie heißen die männlichen Bienen?", optionen: ["Drohnen", "Arbeiterinnen", "Königinnen"], ok: 0 },
          { id: "b09", stufe: 1, frage: "Woraus bauen die Bienen ihre Waben?", optionen: ["Aus Holz", "Aus Wachs", "Aus Papier"], ok: 1 },
          { id: "b10", stufe: 1, frage: "Was machen die Bienen aus Nektar?", optionen: ["Wolle", "Milch", "Honig"], ok: 2 },
          { id: "b11", stufe: 1, frage: "Wer saugt an Larven, Puppen und Bienen und schwächt das Volk?", optionen: ["Die Varroa-Milbe", "Der Regenwurm", "Der Marienkäfer"], ok: 0 },
          { id: "b12", stufe: 1, frage: "Wie viele Flügel hat eine Biene?", optionen: ["Zwei", "Vier", "Sechs"], ok: 1 },
          { id: "b13", stufe: 1, frage: "Wie viele Königinnen leben in einem Bienenvolk?", optionen: ["Eine", "Viele", "Keine"], ok: 0 },
          { id: "b14", stufe: 1, frage: "Was kann Bienen schaden?", optionen: ["Eine Blühwiese", "Manche Pestizide", "Ein bienenfreundlicher Garten"], ok: 1 },
          // Stufe 2 – Wissen anwenden
          { id: "b15", stufe: 2, frage: "Was ist bei der Honigbiene anders als bei Kuh und Huhn?", optionen: ["Sie steht im Stall und wird gemolken", "Sie lebt frei und sucht ihr Futter meist selbst", "Sie legt jeden Tag Eier"], ok: 1 },
          { id: "b16", stufe: 2, frage: "Wozu dient der Honigmagen der Biene?", optionen: ["Er speichert Nektar für den Transport", "Er bewegt die Flügel", "Er riecht die Blüten"], ok: 0 },
          { id: "b17", stufe: 2, frage: "Wo trägt die Biene den Pollen?", optionen: ["Im Honigmagen", "Am Fühler", "Im Pollenkörbchen am Hinterbein"], ok: 2 },
          { id: "b18", stufe: 2, frage: "Wie lange dauert es vom Ei bis zur jungen Arbeiterin?", optionen: ["3 Tage", "21 Tage", "3 Monate"], ok: 1 },
          { id: "b19", stufe: 2, frage: "Was verrät der Schwänzeltanz den anderen Bienen?", optionen: ["Wo es Futter gibt", "Wann der Winter beginnt", "Wer die Königin ist"], ok: 0 },
          { id: "b20", stufe: 2, frage: "Was ist die Aufgabe der Königin?", optionen: ["Sie befiehlt allen Bienen", "Sie sammelt Nektar", "Sie legt Eier"], ok: 2 },
          { id: "b21", stufe: 2, frage: "Welche Bienen haben keinen Stachel?", optionen: ["Die Arbeiterinnen", "Die Drohnen", "Die Königin"], ok: 1 },
          { id: "b22", stufe: 2, frage: "Warum sind Bienen für Obstbäume wichtig?", optionen: ["Sie bestäuben die Blüten", "Sie fressen die Blätter", "Sie düngen den Boden"], ok: 0 },
          { id: "b23", stufe: 2, frage: "Wann behandelt der Imker das Volk gegen die Varroa-Milbe?", optionen: ["Im Frühling", "Mitten im Winter", "Im Spätsommer"], ok: 2 },
          { id: "b24", stufe: 2, frage: "Wo liegen die Flugmuskeln der Biene?", optionen: ["Im Kopf", "Im Hinterleib", "In der Brust"], ok: 2 },
          // Stufe 3 – Zusammenhänge
          { id: "b25", stufe: 3, frage: "Warum verdaut die Biene den Nektar im Honigmagen nicht?", optionen: ["Der Honigmagen ist vom Magen für die Verdauung getrennt", "Die Biene frisst den Nektar sofort", "Der Nektar bleibt im Pollenkörbchen"], ok: 0 },
          { id: "b26", stufe: 3, frage: "Wie halten sich die Bienen in der Wintertraube warm?", optionen: ["Die Königin heizt allein den Kasten", "Sie zittern mit den Flugmuskeln", "Sie liegen einzeln und schlafen"], ok: 1 },
          { id: "b27", stufe: 3, frage: "Was zeigt die Dauer des Schwänzelns an?", optionen: ["Die Richtung zur Sonne", "Die Zahl der Blüten", "Die Entfernung zum Futter"], ok: 2 },
          { id: "b28", stufe: 3, frage: "Warum erntet der Imker nicht den ganzen Honig?", optionen: ["Die Bienen brauchen ihn als Vorrat im Winter", "Er schmeckt sonst nicht mehr", "Der Honigraum wäre zu schwer"], ok: 0 },
          { id: "b29", stufe: 3, frage: "Wozu brauchen die Larven den Pollen?", optionen: ["Zum Bauen der Waben", "Als Eiweiß zum Wachsen", "Zum Wärmen im Winter"], ok: 1 },
          { id: "b30", stufe: 3, frage: "Warum bauen die Bienen sechseckige Zellen?", optionen: ["So wird der Honig süßer", "So finden die Bienen den Weg", "So sparen sie Wachs und Platz"], ok: 2 },
          { id: "b31", stufe: 3, frage: "Warum hilft eine Blühwiese den Bienen?", optionen: ["Sie müssen dort nicht mehr fliegen", "Sie finden dort Nektar und Pollen", "Dort braucht man keinen Imker mehr"], ok: 1 },
        ],
      },

      // ── 39 · Begriffs-Domino: 12 Paare aus allen Reitern; A nimmt die ersten 6, B die ersten 9, C alle 12 ──
      // Die Kette schließt sich: Stein i trägt die Erklärung von Paar i und den Begriff von Paar i+1.
      {
        nr: 39, typ: "domino", eyebrow: "Spiel", titel: "Begriffs-Domino",
        hinweis: "Jeder Stein hat links eine Erklärung und rechts einen Begriff. Lege den Stein an, dessen Erklärung zum offenen Begriff passt.",
        niveaus: {
          A: { steine: 6, hinweis: "Sechs Steine mit den wichtigsten Begriffen. Die Kette schließt sich am Ende." },
          B: { steine: 9, hinweis: "Neun Steine. Jetzt sind auch Körperteile der Biene dabei." },
          C: { steine: 12, hinweis: "Alle zwölf Steine. Die Kette schließt sich." },
        },
        paare: [
          { id: "d01", begriff: "Nutztier", definition: "Ein Tier, das Menschen halten, weil es ihnen etwas gibt" },
          { id: "d02", begriff: "Imker", definition: "Er stellt den Bienenkasten auf und kümmert sich um die Bienen" },
          { id: "d03", begriff: "Insekt", definition: "Ein Tier mit sechs Beinen und drei Körperteilen" },
          { id: "d04", begriff: "Wabe", definition: "Eine Platte aus sechseckigen Zellen aus Wachs" },
          { id: "d05", begriff: "Königin", definition: "Sie legt bis zu etwa 2 000 Eier am Tag" },
          { id: "d06", begriff: "Nektar", definition: "Süße Flüssigkeit aus der Blüte, aus ihr wird Honig" },
          { id: "d07", begriff: "Honigmagen", definition: "Vorratsbehälter im Hinterleib, der den Nektar transportiert" },
          { id: "d08", begriff: "Drohnen", definition: "Männliche Bienen ohne Stachel" },
          { id: "d09", begriff: "Pollenkörbchen", definition: "Hier am Hinterbein trägt die Biene Pollen" },
          { id: "d10", begriff: "Schwänzeltanz", definition: "Damit zeigt eine Biene den anderen, wo es Futter gibt" },
          { id: "d11", begriff: "Bestäubung", definition: "Pollen kommt von Blüte zu Blüte, und Früchte können wachsen" },
          { id: "d12", begriff: "Varroa-Milbe", definition: "Ein Parasit, der an Larven, Puppen und Bienen saugt" },
        ],
      },

      // ── 40 · Quellen: „Woher weißt du es?“ ────────────────────────────────────────────────────────
      // quellenAB: Quellenverzeichnis des Arbeitsblatts für die Lehrkraft (nur Nennung, keine Zitate). Der Client zeigt es
      // noch nicht an – Änderungswunsch an das Gerüst: als aufklappbaren Hinweis „Quellen dieses Arbeitsblatts“ unter der Aufgabe.
      {
        nr: 40, typ: "quellen", eyebrow: "Quellenverzeichnis", titel: "Woher weißt du es?",
        hinweis: "Woher weißt du, was du jetzt über Bienen weißt? Trage mindestens zwei Quellen ein. Das können die Lesestrecken sein. Das können auch der Film „Ein Bienenvolk im Bienenstock“ und das 3D-Modell „Die Honigbiene in 3D“ sein. Auch deine eigenen Beobachtungen im Forscherbuch zählen. Schreibe dazu, warum du der Quelle glaubst.",
        min: 2,
        quellenAB: {
          titel: "Quellen dieses Arbeitsblatts",
          eintraege: [
            "Deutscher Imkerbund e. V. (imkerbund.de)",
            "Länderinstitut für Bienenkunde Hohen Neuendorf (honigbiene.de)",
            "NABU: Honigbiene (nabu.de)",
            "Karl von Frisch: Aus dem Leben der Bienen (Hinweis zum Schwänzeltanz)",
            "COLOSS BEEBOOK: Anatomie und Physiologie der Honigbiene, Carreck et al. 2013 (Grundlage des 3D-Modells)",
            "Das Apfelzweig-Beispiel im Reiter Nutzen & Schutz ist ausgedacht. Die Zahlen sind nicht gemessen.",
          ],
        },
      },

      // ── T · Transfer: Zwei Bienenvölker für die Schule ────────────────────────────────────────────
      // A ohne freies Schreiben: sechs Bausteine ordnen (die Reihenfolge ergibt sich aus „Dafür“, „Er“, „aber auch“, „Außerdem“),
      // dann ein Urteil mit zwei vertretbaren Meinungen. B Satzanfänge und Begriffe, C frei mit Beurteilung.
      {
        nr: "T", typ: "transfer", eyebrow: "Sprachwerkstatt · Transfer · Beurteilen", titel: "Zwei Bienenvölker für unsere Schule",
        kontext: "Klasse 6 NW, Transferaufgabe zum ganzen Arbeitsblatt Honigbiene. Aufgabe: Die Schule soll zwei Bienenvölker bekommen. Das Kind erklärt, was ein Bienenvolk braucht und wie man sich Bienen gegenüber verhält, und beurteilt den Plan. Begriffe: Bienenvolk, Imker, Bienenkasten, Bestäubung, Nektar, Pollen, Honig, Stachel, Varroa-Milbe. Fakten: Die Bienen suchen ihr Futter meist selbst; der Imker kümmert sich um das Volk, erntet nur einen Teil des Honigs, ergänzt im Spätsommer Zuckerlösung und behandelt gegen die Varroa-Milbe. Arbeiterinnen und Königin haben einen Stachel; nach einem Stich in die Haut stirbt die Biene meist. Bewerte Sachrichtigkeit und Begründung. Gib Hinweise statt Lösungen.",
        niveaus: {
          A: {
            modus: "bausteine",
            aufgabe: "Die Schule soll zwei Bienenvölker bekommen. Erkläre den Mitschülern, was die Bienen brauchen und wie wir uns verhalten. Tippe die Sätze in der richtigen Reihenfolge an. Danach entscheidest du selbst.",
            bausteine: [
              "Unsere Schule soll zwei Bienenvölker bekommen.",
              "Dafür braucht die Schule einen Imker.",
              "Er stellt die Bienenkästen auf und kümmert sich um die Völker.",
              "Die Bienen brauchen aber auch viele Blüten, an denen sie Futter finden.",
              "Außerdem schlagen wir nie nach einer Biene, denn nach einem Stich stirbt sie meist.",
            ],
            schluss: "So können Bienen und Kinder gut zusammen auf dem Schulhof leben.",
            urteil: {
              frage: "Bienen auf dem Schulhof: Was meinst du? Tippe eine Antwort an.",
              optionen: [
                "Gute Idee, weil wir viel über Bienen lernen und die Bienen Blüten bestäuben.",
                "Nur mit Vorsicht, weil Bienen stechen können und ein Imker sich kümmern muss.",
              ],
            },
          },
          B: {
            aufgabe: "Die Schule soll zwei Bienenvölker bekommen. Schreibe einen Brief an die Schulleitung. Erkläre, was ein Bienenvolk braucht und wie wir uns Bienen gegenüber verhalten. Sage am Ende, was du von dem Plan hältst, und begründe mit „weil“ oder „denn“. Nutze die Satzanfänge.",
            starter: ["Ein Bienenvolk braucht …", "Der Imker …", "Wir schlagen nicht nach Bienen, denn …", "Ich finde den Plan …, weil …"],
            begriffe: ["Bienenvolk", "Imker", "Bienenkasten", "Bestäubung", "Stachel"],
            min: 120,
          },
          C: {
            aufgabe: "Die Schule soll zwei Bienenvölker bekommen. Schreibe einen Brief an die Schulleitung. Erkläre, was ein Bienenvolk braucht und wie wir uns verhalten. Erkläre auch, was die Bienen für Pflanzen und Menschen tun. Beurteile den Plan: Was spricht dafür, was dagegen? Begründe mit „weil“, „denn“ oder „deshalb“. Komm zu einem begründeten Urteil.",
            begriffe: ["Bienenvolk", "Imker", "Bienenkasten", "Bestäubung", "Nektar", "Pollen", "Honig", "Stachel", "Varroa-Milbe"],
            min: 200,
          },
        },
      },
    ],
  });
})();
