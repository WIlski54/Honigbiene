# Ein Bienenvolk im Bienenstock – Papiertheater-Animation

Die Animation dauert 4:00 Minuten und hat 12 Szenen im Stil eines Papier-Cutout-Bilderbuchs. Eine Lehrerin erzählt als Figur auf der Bühne.

## Dateien für den Unterricht

| Datei | Wofür |
|---|---|
| `Ein_Bienenvolk_im_Bienenstock.html` | **Interaktive Fassung** für Smartboard/Beamer. Doppelklick öffnet sie im Browser. Sie läuft offline, der Ton ist enthalten. |
| `Ein_Bienenvolk_im_Bienenstock.mp4` | **Video** (1920×1080, 24 fps) für Moodle, IServ usw. |
| `drehbuch.md` | Szenen, Sprechertexte und Übergänge (von Stephan freigegeben, unverändert) |
| `docs/ab_uebergabe.md` | Übergabe an das Arbeitsblatt: Kapitel mit Zeiten und Sprechertext, Satzzeiten, Bildereignisse, Vereinfachungen, Zeitfenster für „Finde den Moment“ |
| `hoerproben/` | kurze MP3-Varianten zu Wörtern, deren Aussprache zu prüfen ist (Schwänzelns, Larve, Rähmchen) |

### Bedienung der HTML-Fassung
- **Leertaste**: Start/Pause · **← / →** (auch Bild↑/Bild↓ am Präsentations-Clicker): vorherige/nächste Szene
- **F**: Vollbild · **U**: Untertitel ein/aus (z. B. für DaZ-Lernende)
- **P**: *Unterrichtsmodus*. Die Animation hält nach jeder Szene an; mit der Leertaste geht es weiter.
- Das Kapitelmenü (☰) springt direkt zu einer Szene.

## Einbindung ins Arbeitsblatt

Der Film ist **eine** HTML-Datei (Ton eingebettet, ca. 6,7 MB). Im Arbeitsblatt liegt sie unter
`arbeitsblatt/static/film/Ein_Bienenvolk_im_Bienenstock.html` und wird in einem `iframe` angezeigt
(`INHALTE.filme.volk = { art: "papiertheater", datei: "/static/film/Ein_Bienenvolk_im_Bienenstock.html", titel: "Ein Bienenvolk im Bienenstock" }`).
Im iframe schaltet der Player auf eine kompakte Bedienung; die Seite sendet per `postMessage` ihren Zustand an das AB und nimmt Befehle an:

| AB → Film | Wirkung |
|---|---|
| `{mw:"springe", t:45}` | springt auf Sekunde `t` und hält an (Springen zählt nicht als „gesehen“) |
| `{mw:"kapitel", n:5}` | springt an den Beginn von Kapitel `n` (1–12; bei Szenen mit Übergang an dessen Beginn, sonst 0,3 s vor der Szene) |
| `{mw:"spielen"}` / `{mw:"anhalten"}` | Wiedergabe starten / anhalten (Ton: auf iPads oft erst nach Tippen auf ▶) |
| `{mw:"status"}` | schickt sofort einen Status |
| `{mw:"info"}` | schickt `{mw:"info", art:"papiertheater", dauer:240, kapitel:[{t, ende, titel} × 12], blicke:[], ansichten:[]}` |
| `{mw:"freischalten"}` | merkt „Film vollständig gesehen“ (nach Neuladen der AB-Seite) |

| Film → AB | Inhalt |
|---|---|
| `{mw:"status", art:"papiertheater", t, laeuft, modus:"film", live:false, kapitel, gesehen, freigeschaltet}` | etwa alle 250 ms und bei Änderungen; `t` in Sekunden auf 0,1 s, `gesehen` 0–100 % **echt abgespielt**, `freigeschaltet` ab 95 % |

Geprüft (Test-Elternseite, 3. Oktober 2026): `info` liefert 12 Kapitel, `springe 45` meldet t = 45 und `laeuft:false`, `kapitel 5` meldet 79,7,
`anhalten` meldet die Anhaltezeit auf 0,01 s genau (Audio 85,79 s, gemeldet 85,8 s), vollständiges Abspielen (4-fach) ergibt `gesehen:100`, `freigeschaltet:true`.
Die Aufgaben „Finde den Moment“ dürfen die Zeitfenster aus `docs/ab_uebergabe.md` übernehmen; Bildereignisse und Satzzeiten stehen dort ebenfalls.
Der Film hat keinen Text im Bild (außer dem Titel in Szene 1); alle Fachwörter kommen nur von der Sprecherin und stehen in den Untertiteln (Taste U).

## Neu bauen nach Änderungen
1. Texte in `build/narration.json` ändern → `python build/tts_edge.py` (Stimme Seraphina, online)
2. Zeiten, Musik, Geräusche: `python build/timeline_erzeugen.py` (schreibt `build/timeline.json` aus den Satzzeiten) → `python build/make_audio.py`
3. Bilder: `src/szenen.js` (Ablauf, Intro, Wiese/Winter, Schluss), `src/welt_stock.js` (Welt im Stock), `src/bienen.js` (Biene, Kasten, Rähmchen, Zelle, Imker …)
4. Prüfen: `python build/export_video.py --snap 10,60,…` und `python build/kontaktbogen.py bogen.jpg 10 60 …`
5. `python build/bundle.py` (HTML) und `python build/export_video.py` (MP4), `python build/ab_uebergabe.py` (Übergabe an das AB; Ergänzungen in `docs/ab_ergaenzung.md` und `docs/ereignisse.json`)

Eigene Stimme: Aufnahmen als `assets/voice/sceneNN.wav` ablegen, `python build/cues_offline.py`, dann ab Schritt 2.
