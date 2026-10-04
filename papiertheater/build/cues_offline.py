"""Grobe Untertitel-Zeitmarken für Aufnahmen ohne cues.json (Offline-Stimme oder eigene Aufnahmen der Lehrkraft).

Verteilt die Sätze jeder Szene proportional zur Zeichenzahl über die Länge der Aufnahme.
Aufruf: python build/cues_offline.py
"""
import json
import re
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))
cues = {}
for sc in N["szenen"]:
    with wave.open(str(ROOT / "assets" / "voice" / f"scene{sc['id']:02d}.wav")) as w:
        dur = w.getnframes() / w.getframerate()
    sents = [p for p in re.split(r"(?<=[^\d\s][.!?])\s+", sc["text"].strip()) if p]
    total = sum(len(s) for s in sents)
    t, lst = 0.0, []
    for s in sents:
        d = dur * len(s) / total
        lst.append({"t0": round(t, 2), "t1": round(t + d - 0.3, 2), "text": s})
        t += d
    cues[str(sc["id"])] = lst
    print(f"Szene {sc['id']}: {dur:.1f} s, {len(sents)} Sätze")
(ROOT / "assets" / "voice" / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=1), encoding="utf8")
