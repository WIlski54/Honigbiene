"""Sprecherin: neuronale Microsoft-Stimme über edge-tts (braucht Internet; `pip install edge-tts`).

Satzweise Synthese mit eigenen Pausen (edge-tts versteht keine SSML-Pausen).
Liest build/narration.json, schreibt assets/voice/sceneNN.wav (24 kHz mono) und assets/voice/cues.json
und meldet, ob jede Aufnahme in ihr Zeitfenster passt.

Aufruf: python build/tts_edge.py [--only 3] [--voice de-DE-KatjaNeural]
"""
import argparse
import asyncio
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
import edge_tts

ROOT = Path(__file__).resolve().parent.parent
VOICE_DIR = ROOT / "assets" / "voice"
SR = 24000


def sentences(text):
    # nicht nach Ordnungszahlen wie „28.“ trennen
    return [p for p in re.split(r"(?<=[^\d\s][.!?])\s+", text.strip()) if p]


def spoken(s, lex):
    for a, b in lex.items():
        s = s.replace(a, b)
    return s


async def synth(text, voice, rate, out_mp3):
    com = edge_tts.Communicate(text, voice, rate=rate)
    with open(out_mp3, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])


def decode(mp3):
    return subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                          check=True, capture_output=True).stdout


def trim(raw, thresh=180):
    a = np.frombuffer(raw, dtype=np.int16)
    idx = np.nonzero(np.abs(a) > thresh)[0]
    if len(idx) == 0:
        return raw
    pad = int(0.04 * SR)
    return a[max(0, idx[0] - pad): min(len(a), idx[-1] + pad)].tobytes()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default=None)
    ap.add_argument("--only", type=int, default=0)
    args = ap.parse_args()
    N = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))
    if "Willkommen im Papiertheater" in json.dumps(N, ensure_ascii=False):
        print("WARNUNG: narration.json enthält noch den Demo-Text der Vorlage!")
    voice = args.voice or N.get("stimme", "de-DE-SeraphinaMultilingualNeural")
    lex = N.get("aussprache", {})
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = VOICE_DIR / "_tmp"
    tmp.mkdir(exist_ok=True)
    cues_path = VOICE_DIR / "cues.json"
    cues = json.loads(cues_path.read_text(encoding="utf8")) if cues_path.exists() else {}
    for sc in N["szenen"]:
        sid = sc["id"]
        if args.only and sid != args.only:
            continue
        pause = sc.get("pause", N.get("pause", 480))
        rate = sc.get("tempo", N.get("tempo", "-4%"))
        pcm, sc_cues = b"", []
        for i, sent in enumerate(sentences(sc["text"])):
            mp3 = tmp / f"s{sid:02d}_{i}.mp3"
            await synth(spoken(sent, lex), voice, rate, mp3)
            seg = trim(decode(mp3))
            t0 = len(pcm) / 2 / SR
            pcm += seg
            sc_cues.append({"t0": round(t0, 3), "t1": round(len(pcm) / 2 / SR, 3), "text": sent})
            pcm += b"\x00\x00" * int(SR * pause / 1000)
        pcm = pcm[: len(pcm) - 2 * int(SR * pause / 1000)]
        with wave.open(str(VOICE_DIR / f"scene{sid:02d}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
        cues[str(sid)] = sc_cues
        dur = len(pcm) / 2 / SR
        avail = sc["ende"] - sc["start"] - sc.get("sprechBeginn", 0.8) - 0.5
        flag = "ok" if dur <= avail else f"ZU LANG um {dur - avail:.1f} s -> Text kürzen oder 'tempo' erhöhen"
        print(f"Szene {sid:2d}: {dur:5.2f} s von {avail:5.2f} s  {flag}")
    cues_path.write_text(json.dumps(cues, ensure_ascii=False, indent=1), encoding="utf8")
    for f in tmp.glob("*.mp3"):
        f.unlink()


if __name__ == "__main__":
    asyncio.run(main())
