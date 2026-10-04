"""Übergabe an das Arbeitsblatt (Skill ab-bauen): docs/ab_uebergabe.md
Sammelt, was die AB-Aufgaben brauchen, damit sie genau zum Film passen: Datei, Szenen mit Zeiten und Sprechertext,
Satzzeiten, benannte Bildereignisse aus timeline.json. Spalte „Aufgabenidee“ danach aus dem Drehbuch füllen.
Steuerung im AB: {mw: 'springe', t} · {mw: 'kapitel', n} · 'spielen' · 'anhalten' (siehe src/player.js, Abschnitt Schnittstelle).
Aufruf: python build/ab_uebergabe.py"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
narr = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))
tl = json.loads((ROOT / "build" / "timeline.json").read_text(encoding="utf8"))
cues = json.loads((ROOT / "assets" / "voice" / "cues.json").read_text(encoding="utf8"))
f = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"
datei = narr.get("datei", "Film")
z = [f"# Übergabe an das Arbeitsblatt: {narr['titel']}", "",
     f"- Art: **papiertheater** · Datei: `{datei}.html` → im AB nach `static/film/` · Dauer {tl['dauer']} s",
     f"- Eintrag für `inhalte.js`: `{datei.lower()}: {{ art: \"papiertheater\", datei: \"/static/film/{datei}.html\", titel: \"{narr['titel']}\" }}`",
     "- Befehle: `springe` (t), `kapitel` (n, ab 1 – springt an den Beginn des Übergangs zur Szene), `spielen`, `anhalten`.",
     "- Grundregel (ab-bauen, film.md §2): Jede Film-Aufgabe stützt sich auf eine Stelle unten; dieselben Wörter wie die Sprecherin.", "",
     "## Szenen", "", "| n | Zeit | Titel | Sprechertext |", "|---|---|---|---|"]
for i, s in enumerate(narr["szenen"], 1):
    z.append(f"| {i} | {f(s['start'])}–{f(s['ende'])} | {s['titel']} | {s['text']} |")
z += ["", "## Satzzeiten (für Zeitfenster „Finde den Moment“ und `springe`)", "", "| von | bis | Satz |", "|---|---|---|"]
for s in narr["szenen"]:
    t0 = s["start"] + s.get("sprechBeginn", 0.8)
    for c in cues.get(str(s["id"]), []):
        z.append(f"| {t0 + c['t0']:.1f} | {t0 + c['t1']:.1f} | {c['text']} |")
ereignisse = {k: v for k, v in tl.items() if k not in ("dauer", "musik", "sfx", "zaesur", "ducking", "ausklang", "autoSfx")}
if ereignisse:
    z += ["", "## Bildereignisse (timeline.json)", "", "| Name | Zeit(en) s | Aufgabenidee |", "|---|---|---|"]
    beschr = {}
    bp = ROOT / "docs" / "ereignisse.json"
    if bp.exists():
        beschr = json.loads(bp.read_text(encoding="utf8"))
    z += [f"| {k} | {json.dumps(v)} | {beschr.get(k, '')} |" for k, v in ereignisse.items()]
erg = ROOT / "docs" / "ab_ergaenzung.md"
if erg.exists():
    z += ["", erg.read_text(encoding="utf8")]
else:
    z += ["", "## Kernaussagen, Vereinfachungen", "", "(aus dem Drehbuch übernehmen)", "", "## Aufgabenideen (4–6)", "",
          "Film ansehen mit Beobachtungsauftrag · Finde den Moment · Aussage ↔ Szene zuordnen · Szene nachsehen und beschreiben ·",
          "Was ist echt, was vereinfacht?", ""]
out = ROOT / "docs" / "ab_uebergabe.md"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(z), encoding="utf8")
print("->", out)
