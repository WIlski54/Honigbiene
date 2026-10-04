# GitHub und GitHub Pages

Repository: [WIlski54/Honigbiene](https://github.com/WIlski54/Honigbiene).
Die oeffentliche Website zeigt **nur das 3D-Modell**:
[Honigbiene](https://wilski54.github.io/Honigbiene/).
Arbeitsblatt, Filmquellen und Modellierskripte bleiben im Repository, werden aber nicht auf GitHub Pages ausgeliefert.
Die Website benoetigt keinen Python-Server und keine API-Schluessel.

**Stand 4. Oktober 2026:** Erster Push (`011eb95` auf `main`) und Pages-Deployment erfolgreich.
GitHub Pages ist bereits auf GitHub Actions eingestellt; die Einrichtung unten dient als Referenz.
48 JavaScript-Tests und 487 Arbeitsblatt-Tests bestehen lokal und auf dem GitHub-Runner.
Desktop-/Mobilansicht, Explosion, Ausblenden der Bedienung und Ladepfade unter `/Honigbiene/` sind geprueft.

## GitHub Pages einrichten

1. Im Repository **Settings > Pages** oeffnen.
2. Unter **Build and deployment > Source** den Eintrag **GitHub Actions** waehlen.
3. Auf **main** pushen. Der Workflow **3D-Biene auf GitHub Pages** testet, baut und veroeffentlicht `dist/`.
4. Unter **Actions** auf den gruenen Abschluss warten. Die Website ist danach unter der Adresse oben erreichbar.

Der Workflow kann auch unter **Actions > 3D-Biene auf GitHub Pages > Run workflow** erneut gestartet werden.
Er laedt ausschliesslich `dist/` hoch, nicht das gesamte Repository. `base: './'` in `vite.config.js`
und `%BASE_URL%` im HTML halten Modelle, Schriftdateien und Referenzbilder unter `/Honigbiene/` erreichbar.
Grundlage: [GitHub-Dokumentation zu Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Lokal pruefen und spaeter aktualisieren

Im Projektordner (PowerShell):

```powershell
npm ci
npm run check:repo
npm test
npm run build
npm run preview -- --port 4173 --base=/Honigbiene/
```

Die gebaute Fassung liegt unter `http://127.0.0.1:4173/Honigbiene/`.
Fuer die Entwicklung weiter `npm run dev` bzw. am Tablet `npm run dev:tablet` verwenden.

Nach eigenen Aenderungen:

```powershell
git add .
npm run check:repo
git diff --cached --stat
git commit -m "Modell aktualisieren"
git push
```

Die Musterpruefung sucht bekannte Zugangsschluessel, Laufzeitdateien und Dateien ueber 100 MiB.
Sie ist eine Zusatzkontrolle, keine vollstaendige Sicherheitspruefung. Git ignoriert `.env`, Datenbanken,
Schuelerarbeiten, Python-Caches, lokale QA-Ausgaben und `node_modules/`.

## Welche Dateien mitkommen

- `public/models/`: komprimierte Desktop- und Tablet-GLBs samt Metadaten. Kein Git LFS erforderlich.
- `public/reference/`: die drei vom Nutzer bereitgestellten, in der Modellansicht verwendeten Bildvorlagen.
- `src/`, `tests/`, Modellierskripte und Dokumentation: nachvollziehbarer Quellstand.
- `arbeitsblatt/` und `papiertheater/`: Quellstand inklusive des nutzbaren HTML-Films mit eingebettetem Ton.

Nur lokal bleiben Roh-GLBs, Blender-Dateien, alte GLB-Exporte, QA-Aufnahmen und archivierte Zusatzfotos
mit ungeklaerter Herkunft. Es wird keine neue pauschale Lizenz fuer Quellcode oder Bilder vergeben.

Der MP4-Export hat etwa 129 MiB und bleibt ebenfalls lokal: GitHub
[blockiert Dateien ueber 100 MiB](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
Das Arbeitsblatt verwendet den mitgelieferten HTML-Film und ist vom MP4 unabhaengig.
Falls das MP4 spaeter zum Download angeboten werden soll, kann es als GitHub-Release-Anhang hochgeladen werden.

## Arbeitsblatt spaeter betreiben

GitHub Pages fuehrt weder Flask noch SQLite oder Socket.IO aus. Fuer das gesamte Arbeitsblatt
ist ein Server erforderlich; die Einrichtung steht in `arbeitsblatt/README.md`.
Nach einem frischen Clone zuerst im Hauptordner `npm ci` und `npm run build:ab` ausfuehren.
Der erzeugte Ordner `arbeitsblatt/static/film/bienenmodell/` ist absichtlich nicht versioniert.
Danach kann der vorhandene Docker-Build mit `docker build -t honigbiene-ab ./arbeitsblatt` laufen.
Echte Passwoerter, KI-Schluessel und Lernendendaten duerfen nie in diesen Build-Kontext kopiert werden.
