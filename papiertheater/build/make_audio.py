"""Baut die komplette Tonspur (Musik + Geräusche + Sprecherin), die Mund-Hüllkurve und src/data.js.

Eingaben:  build/narration.json, build/timeline.json, assets/voice/sceneNN.wav, assets/voice/cues.json
Ausgaben:  assets/soundtrack.wav, assets/soundtrack.mp3, src/data.js, src/index.html

timeline.json steuert den Ton:
  "musik": [{"a": 0.6, "e": 20, "stimmung": "neugierig"}, ...]   Stimmungen siehe PRESETS
  "zaesur": [t0, t1]            Musik und Atmo fast ganz weg (z. B. beim ernstesten Moment)
  "sfx": [{"typ": "wachsmal", "t": 3.4, "dauer": 1.5, "gain": 1, "pan": 0.2}, ...]   Typen siehe SFX
Automatisch (abschaltbar mit "autoSfx": false): Vorhang auf/zu, Wachsmalstift beim Titel, Papierrascheln an jeder Szenengrenze.

Aufruf: python build/make_audio.py
"""
import json
import subprocess
import wave
from math import gcd
from pathlib import Path

import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
FPS = 24
rng = np.random.default_rng(1914)

NARR = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))
TL = json.loads((ROOT / "build" / "timeline.json").read_text(encoding="utf8"))
CUES = json.loads((ROOT / "assets" / "voice" / "cues.json").read_text(encoding="utf8"))
DUR = TL["dauer"]
N = int(DUR * SR)
music, sfx, amb, voice = np.zeros((2, N)), np.zeros((2, N)), np.zeros((2, N)), np.zeros(N)


# ----------------------------------------------------------------- Hilfen
def t_arr(n): return np.arange(n) / SR
def bp(x, lo, hi, o=2): return signal.sosfilt(signal.butter(o, [lo, hi], btype="band", fs=SR, output="sos"), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, btype="low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, btype="high", fs=SR, output="sos"), x)
def noise(n): return rng.standard_normal(n)


def fade(x, fin=0.01, fout=0.05):
    n = len(x)
    a, b = min(n // 2, int(fin * SR)), min(n // 2, int(fout * SR))
    env = np.ones(n)
    if a: env[:a] = np.linspace(0, 1, a) ** 2
    if b: env[-b:] = np.linspace(1, 0, b) ** 2
    return x * env


def put(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or len(x) == 0: return
    if i < 0: x, i = x[-i:], 0
    x = x[: N - i] * gain
    if isinstance(pan, (list, tuple)): pan = np.linspace(pan[0], pan[1], len(x))
    p = pan if np.isscalar(pan) else pan[: len(x)]
    buf[0, i:i + len(x)] += x * np.cos((p + 1) * np.pi / 4) * 1.4142
    buf[1, i:i + len(x)] += x * np.sin((p + 1) * np.pi / 4) * 1.4142


# ----------------------------------------------------------------- Instrumente
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)


def felt_piano(m, dur, vel=0.6):
    f = midi(m); n = int((dur + 2.2 + max(0, 60 - m) * 0.05) * SR); t = t_arr(n); x = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > 9000: break
        x += (1 / k ** 1.6) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * (1.2 + 0.9 * k) * (0.6 + f / 900))
    rel = np.ones(n); r0 = int(dur * SR)
    if r0 < n: rel[r0:] = np.exp(-(t[r0:] - t[r0]) * 5)
    x = lp(x * np.exp(-t / (1.1 + 180 / f)) * rel, 1500 + vel * 900)
    th = lp(noise(int(0.03 * SR)), 300) * np.exp(-np.linspace(0, 8, int(0.03 * SR))) * 0.15
    x[: len(th)] += th
    return fade(x, 0.004, 0.2) * vel


def saw(f, t, nh, vr=5.0, vd=0.004):
    ph = 2 * np.pi * f * t + (vd * f / vr) * np.sin(2 * np.pi * vr * t); x = np.zeros(len(t))
    for k in range(1, nh + 1):
        if f * k > 7000: break
        x += np.sin(k * ph + rng.uniform(0, 6.28)) / k
    return x


def strings(ms, dur, vel=0.25, att=1.4, rel=1.8, bright=1800):
    n = int((dur + rel) * SR); t = t_arr(n); x = np.zeros(n)
    for m in ms:
        for det in (-0.004, 0.0, 0.005): x += saw(midi(m) * (1 + det), t, 14, 4.6 + rng.uniform(-.4, .4), 0.0025)
    env = np.minimum(1, t / att) ** 1.5; r0 = int(dur * SR); env[r0:] *= np.exp(-(t[r0:] - t[r0]) * (3.0 / rel))
    return lp(x * env, bright) / max(1, len(ms)) * vel * 0.35


def cello(m, dur, vel=0.4, att=0.35):
    n = int((dur + 1.2) * SR); t = t_arr(n)
    x = bp(saw(midi(m), t, 18, 5.3, 0.004), 70, 1400) + 0.02 * bp(noise(n), 200, 2500)
    env = np.minimum(1, t / att) ** 1.3; r0 = int(dur * SR); env[r0:] *= np.exp(-(t[r0:] - t[r0]) * 3.5)
    return x * env * vel * 0.45


CH = {"F": [53, 57, 60, 65], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62], "C": [48, 55, 60, 64], "Gm": [43, 55, 58, 62],
      "A": [45, 57, 61, 64], "A7": [45, 55, 61, 64], "Am": [45, 57, 60, 64], "Dm/F": [41, 57, 62, 65], "Eb": [51, 58, 63, 67],
      "G": [43, 55, 59, 62], "Em": [40, 55, 59, 64]}
BEAT = 60 / 66
PRESETS = {  # Klavierfigur, Klavier-, Streicher-, Cellostärke, hohe Streicher, Akkordfolge
    "ruhig": ("arp", 0.42, 0.0, 0.0, False, ["F", "Dm", "Bb", "C"]),
    "neugierig": ("arp", 0.42, 0.16, 0.0, False, ["Dm", "Bb", "F", "C"]),
    "heiter": ("arp", 0.44, 0.12, 0.0, False, ["C", "F", "G", "C"]),
    "staunend": ("arp", 0.40, 0.22, 0.0, True, ["F", "C", "Dm", "Bb"]),
    "spannung": ("pulse", 0.36, 0.22, 0.30, False, ["Dm", "Bb", "Gm", "A"]),
    "dicht": ("pulse", 0.40, 0.32, 0.45, True, ["Dm", "Eb", "Gm", "A7"]),
    "ernst": ("single", 0.40, 0.22, 0.28, False, ["Dm", "Bb", "Gm", "Dm"]),
    "traurig": ("sparse", 0.40, 0.26, 0.34, False, ["Gm", "Dm", "Eb", "A"]),
    "nachdenklich": ("arp", 0.36, 0.20, 0.22, False, ["Dm", "Bb", "F", "C"]),
}


def section(t0, t1, stimmung, akkorde=None):
    if stimmung == "zaesur":
        put(music, cello(38, max(1, t1 - t0 - 1), 0.16, att=2.5), t0 + 0.5, 0.6, -0.1)
        put(music, strings([50, 57], max(1, t1 - t0 - 2), 0.10, att=3.0, rel=3.0, bright=900), t0 + 1.5, 0.6, 0.1)
        return
    piano, pv, sv, cv, high, prog = PRESETS[stimmung]
    prog = akkorde or prog
    bar, t, i = BEAT * 4, t0, 0
    while t < t1 - 0.01:
        notes = CH[prog[i % len(prog)]]; bl = min(bar, t1 - t)
        if piano == "arp":
            pat = [0, 2, 1, 3, 2, 1] if i % 2 == 0 else [0, 1, 2, 3, 1, 2]
            for j, idx in enumerate(pat):
                put(music, felt_piano(notes[idx] + (12 if idx > 1 else 0), bl / 6 * 1.6, pv * (0.9 if j else 1)), t + j * bl / 6, 0.5, -0.25 + 0.1 * idx)
        elif piano == "sparse":
            put(music, felt_piano(notes[0] + 12, bl * 0.8, pv), t, 0.5, -0.2)
            put(music, felt_piano(notes[2] + 12, bl * 0.5, pv * 0.8), t + bl / 2, 0.5, 0.15)
        elif piano == "pulse":
            for j in range(8):
                put(music, felt_piano(notes[1] + 12 if j % 2 else notes[0] + 12, bl / 8, pv * (1 if j % 4 == 0 else .7)), t + j * bl / 8, 0.45, -0.1)
        elif piano == "single":
            put(music, felt_piano(notes[-1] + 12, bl, pv), t + 0.15, 0.5, 0.1)
        if sv: put(music, strings(notes[1:], bl, sv), t, 0.6, 0.0)
        if cv: put(music, cello(notes[0] - 12 if notes[0] > 45 else notes[0], bl * 0.92, cv), t, 0.7, -0.3)
        if high: put(music, strings([notes[3] + 12], bl, max(sv, 0.2) * 0.5, att=2.0, bright=3000), t, 0.5, 0.35)
        t += bar; i += 1


for s in TL.get("musik", [{"a": 0.6, "e": DUR - 4.5, "stimmung": "neugierig"}]):
    section(s["a"], min(s["e"], DUR - 4.2), s["stimmung"], s.get("akkorde"))
# Ausklang
section(DUR - 8.0, DUR - 3.6, "traurig" if TL.get("ausklang") == "ernst" else "nachdenklich", ["Dm/F"])
put(music, felt_piano(62, 3.5, 0.32), DUR - 3.8, 0.5, 0.1)
put(music, felt_piano(69, 3.2, 0.26), DUR - 3.1, 0.5, 0.2)


def reverb(st, secs=2.6, wet=0.28):
    n = int(secs * SR); ir = lp(noise(n) * np.exp(-np.linspace(0, 7, n)), 5000); ir /= np.sqrt(np.sum(ir ** 2))
    out = np.empty_like(st)
    for c in range(2): out[c] = st[c] * (1 - wet) + signal.fftconvolve(st[c], np.roll(ir, c * 37))[: st.shape[1]] * wet * 1.2
    return out


music = reverb(music)


# ----------------------------------------------------------------- Geräusche
def paper(dur, inten=1.0):
    n = int(dur * SR); base = bp(noise(n), 1200, 7000) * 0.25; crack = np.zeros(n)
    for _ in range(int(dur * 55 * inten) + 2):
        i = rng.integers(0, max(1, n - 800)); L = rng.integers(80, 700)
        crack[i:i + L] += noise(L) * np.exp(-np.linspace(0, 6, L)) * rng.uniform(0.2, 1.0)
    return fade((base + hp(crack, 900) * 0.6) * np.sin(np.linspace(0, np.pi, n)) ** 0.8 * inten, 0.02, 0.08) * 0.5


def crayon_s(dur):
    n = int(dur * SR); t = t_arr(n); x = bp(noise(n), 1800, 5200)
    am = np.abs(np.sin(np.cumsum(2 * np.pi * (6.5 + 2 * np.sin(2 * np.pi * 0.37 * t)) / SR))) ** 0.7
    grit = np.zeros(n)
    for _ in range(int(dur * 260)):
        i = rng.integers(0, n - 60); grit[i:i + 40] += rng.uniform(-1, 1) * np.exp(-np.linspace(0, 5, 40))
    return fade((x * 0.55 + hp(grit, 2500) * 0.8) * (0.35 + 0.65 * am), 0.05, 0.12) * 0.28


def chime(f=1318.5, gain=0.16):
    n = int(2.6 * SR); t = t_arr(n); x = np.zeros(n)
    for r, a, d in ((1, 1, 1.4), (2.0, 0.35, 2.2), (3.01, 0.18, 3.0), (4.17, 0.08, 4.0)): x += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d)
    return fade(x, 0.003, 0.3) * gain


def pop_s():
    n = int(0.12 * SR); x = bp(noise(n), 700, 4000) * np.exp(-np.linspace(0, 9, n))
    return (x + np.sin(2 * np.pi * 140 * t_arr(n)) * np.exp(-np.linspace(0, 12, n)) * 0.6) * 0.22


def whoosh(dur=0.7, lo=300, hi=3000):
    n = int(dur * SR); x = noise(n); out = np.zeros(n)
    for i in range(0, n, 1024):
        f0 = lo + (hi - lo) * np.sin(i / n * np.pi); out[i:i + 1024] = bp(x[i:i + 1024], max(80, f0 * 0.6), min(15000, f0 * 1.6), 1)
    return lp(out * np.sin(np.linspace(0, np.pi, n)) ** 1.5, 5000) * 0.25


def engine(dur, rpm=15.0):
    n = int(dur * SR); t = t_arr(n); x = np.zeros(n); per = SR / rpm; i = 0.0
    while i < n - 2000:
        L = min(int(per * 0.8), n - int(i)); x[int(i):int(i) + L] += lp(noise(L), 260) * np.exp(-np.linspace(0, 5, L)) * rng.uniform(0.7, 1)
        i += per * rng.uniform(0.9, 1.1)
    x += np.sin(2 * np.pi * 42 * t + 2 * np.sin(2 * np.pi * rpm * t)) * 0.15 + bp(noise(n), 900, 2600) * 0.03
    return fade(x, min(1.0, dur / 3), min(1.5, dur / 3)) * 0.35


def murmur(dur, busy=1.0, angry=False):
    n = int(dur * SR); t = t_arr(n); x = np.zeros(n)
    for v in range(7):
        f = rng.uniform(260, 900) * (1.25 if angry else 1)
        env = lp(np.clip(np.sin(2 * np.pi * rng.uniform(2.5, 4.5) * t + rng.uniform(0, 6)) + rng.uniform(-.2, .4), 0, 1), 12)
        x += bp(noise(n), f * 0.7, f * 1.5) * env * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.05, 0.2) * t + v))
    return fade(lp(x, 2200 if angry else 1600) * busy * 0.09, min(1.5, dur / 3), min(1.5, dur / 3))


def pink(n):
    return signal.lfilter([0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400], noise(n))


def street(dur): return fade(lp(pink(int(dur * SR)), 900) * 0.10, min(1.5, dur / 3), min(1.5, dur / 3))


def step():
    n = int(0.09 * SR); x = lp(noise(n), 500) * np.exp(-np.linspace(0, 10, n))
    return (x + np.sin(2 * np.pi * 95 * t_arr(n)) * np.exp(-np.linspace(0, 14, n)) * 0.5) * 0.25


def tick(hi=True):
    n = int(0.03 * SR); x = hp(noise(n), 2500 if hi else 1800) * np.exp(-np.linspace(0, 14, n))
    return (x + np.sin(2 * np.pi * (3100 if hi else 2500) * t_arr(n)) * np.exp(-np.linspace(0, 20, n)) * 0.4) * 0.16


def boom():
    n = int(2.2 * SR); t = t_arr(n)
    x = np.sin(2 * np.pi * np.cumsum(58 * np.exp(-t * 0.8) + 30) / SR) * np.exp(-t * 2.2) + lp(noise(n), 380) * np.exp(-t * 4.5) * 1.6
    return fade(lp(x, 520), 0.004, 0.4) * 0.55


def pulse_s():
    n = int(0.5 * SR); t = t_arr(n)
    return fade(lp(noise(n), 220) * np.exp(-t * 18) + np.sin(2 * np.pi * 70 * t) * np.exp(-t * 16) * 0.6, 0.003, 0.1) * 0.35


def bubbles(n, k, lo=500, hi=1400, lvl=0.25):
    x = np.zeros(n)
    for _ in range(k):
        i = rng.integers(0, max(1, n - 3000)); L = rng.integers(1200, 2800); tt = t_arr(L); fb = rng.uniform(lo, hi)
        x[i:i + L] += np.sin(2 * np.pi * (fb + 900 * tt / tt[-1]) * tt) * np.exp(-tt * 40) * lvl
    return x


def splash():
    n = int(1.1 * SR); x = bp(noise(n), 500, 3500) * np.exp(-t_arr(n) * 4.5) + bubbles(n, 14)
    return fade(lp(x, 4000), 0.005, 0.2) * 0.3


def telegraph_s(dur):
    n = int(dur * SR); x = np.zeros(n); t = 0.0
    while t < dur - 0.2:
        d = rng.choice([0.08, 0.08, 0.22])
        for tt, h in ((t, True), (t + d, False)):
            c = tick(h) * (1.4 if h else 1.0); i = int(tt * SR)
            if i + len(c) < n: x[i:i + len(c)] += c
        t += d + rng.choice([0.09, 0.09, 0.25, 0.4])
    return x


def flutter(dur, rate=9):
    n = int(dur * SR); x = np.zeros(n); t = 0.0
    while t < dur - 0.15:
        f = paper(0.12, 1.2); i = int(t * SR); x[i:i + len(f)] += f[: n - i]; t += 1 / rate * rng.uniform(0.7, 1.3)
    return x * 0.5


def curtain(dur):
    n = int(dur * SR)
    return fade(bp(noise(n), 180, 2200) * np.sin(np.linspace(0, np.pi, n)) ** 1.2 * (0.8 + 0.2 * np.sin(np.linspace(0, 11, n))), 0.3, 0.6) * 0.20


def wind(dur):
    n = int(dur * SR); t = t_arr(n); x = pink(n); out = np.zeros(n)
    for i in range(0, n, 2048):
        f0 = max(120.0, 400 + 300 * np.sin(2 * np.pi * 0.13 * i / SR) + 150 * np.sin(2 * np.pi * 0.31 * i / SR))
        out[i:i + 2048] = bp(x[i:i + 2048], f0 * 0.5, f0 * 1.8, 1)
    return fade(out * (0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t)) * 0.8, min(1.5, dur / 3), min(1.5, dur / 3))


def rain(dur):
    n = int(dur * SR); x = hp(pink(n), 1500) * 0.15; drops = np.zeros(n)
    for _ in range(int(dur * 120)):
        i = rng.integers(0, n - 200); drops[i:i + 120] += noise(120) * np.exp(-np.linspace(0, 8, 120)) * rng.uniform(0.1, 0.5)
    return fade(x + hp(drops, 2000), min(1.5, dur / 3), min(1.5, dur / 3)) * 0.5


def brook(dur):
    n = int(dur * SR)
    return fade(bp(pink(n), 300, 3000) * 0.2 + bubbles(n, int(dur * 25), 600, 1800, 0.08), min(1.5, dur / 3), min(1.5, dur / 3))


def bird(dur):
    n = int(dur * SR); x = np.zeros(n); t = rng.uniform(0, 0.5)
    while t < dur - 0.4:
        f0 = rng.uniform(2500, 4200)
        for k in range(rng.integers(2, 5)):
            L = int(rng.uniform(0.04, 0.09) * SR); tt = t_arr(L); i = int((t + k * 0.11) * SR)
            if i + L < n: x[i:i + L] += np.sin(2 * np.pi * (f0 + rng.uniform(-800, 800) * tt / tt[-1]) * tt) * np.sin(np.linspace(0, np.pi, L)) * 0.12
        t += rng.uniform(0.8, 2.2)
    return x


def fire(dur):
    n = int(dur * SR); x = lp(pink(n), 500) * 0.2; cr = np.zeros(n)
    for _ in range(int(dur * 30)):
        i = rng.integers(0, n - 400); cr[i:i + 300] += noise(300) * np.exp(-np.linspace(0, 9, 300)) * rng.uniform(0.2, 1)
    return fade(x + hp(cr, 1500) * 0.4, min(1.5, dur / 3), min(1.5, dur / 3)) * 0.6


def hum(dur, f0=55.0, f1=None):
    """Leises Fabriksummen; f1 ≠ f0 → Ton gleitet (Energie fällt aus / läuft wieder an)."""
    n = int(dur * SR); t = t_arr(n); f1 = f0 if f1 is None else f1
    f = f0 + (f1 - f0) * np.clip(t / max(0.1, dur * 0.8), 0, 1); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph) + lp(noise(n), 300) * 0.25
    x *= 1 + 0.12 * np.sin(2 * np.pi * 0.7 * t)
    return fade(lp(x, 900), min(1.5, dur / 3), min(1.5, dur / 3)) * 0.12


def blubb(dur):
    n = int(dur * SR)
    return fade(lp(bubbles(n, max(2, int(dur * 2.5)), 250, 800, 0.2), 2500), min(1.0, dur / 3), min(1.0, dur / 3))


def klick_s():
    n = int(0.08 * SR); t = t_arr(n)
    return (lp(noise(n), 1800) * np.exp(-t * 90) + np.sin(2 * np.pi * 620 * t) * np.exp(-t * 60) * 0.5) * 0.2


# typ: (Funktion(e) -> Signal, Bus)
SFX = {
    "papier": (lambda e: paper(e.get("dauer", 0.6), e.get("staerke", 1.0)), "sfx"),
    "wachsmal": (lambda e: crayon_s(e.get("dauer", 1.5)), "sfx"),
    "glocke": (lambda e: chime(e.get("ton", 1318.5)), "sfx"),          # „heller Ton“, wenn ein Zusammenhang sichtbar wird
    "pop": (lambda e: pop_s(), "sfx"),                                    # Papier springt auf
    "wusch": (lambda e: whoosh(e.get("dauer", 0.7)), "sfx"),
    "blaettern": (lambda e: flutter(e.get("dauer", 3.0)), "sfx"),
    "uhr": (None, "sfx"),                                                 # Ticken, 1/s über „dauer“
    "vorhang": (lambda e: curtain(e.get("dauer", 3.0)), "sfx"),
    "knall": (lambda e: boom(), "sfx"),                                   # gedämpft, nie drastisch
    "impuls": (lambda e: pulse_s(), "sfx"),                               # sehr gedämpfter Stoß
    "platsch": (lambda e: splash(), "sfx"),
    "telegraf": (lambda e: telegraph_s(e.get("dauer", 3.0)), "sfx"),
    "cello": (lambda e: cello(e.get("note", 38), e.get("dauer", 3.0), 0.2), "sfx"),  # tiefer Einzelton (Bedrohung, Ernst)
    "schritte": (None, "amb"),                                            # anzahl, abstand
    "motor": (lambda e: engine(e.get("dauer", 5.0), e.get("rpm", 15.0)), "amb"),
    "gemurmel": (lambda e: murmur(e.get("dauer", 5.0), e.get("staerke", 1.0), e.get("wuetend", False)), "amb"),
    "strasse": (lambda e: street(e.get("dauer", 10.0)), "amb"),
    "wind": (lambda e: wind(e.get("dauer", 8.0)), "amb"),
    "regen": (lambda e: rain(e.get("dauer", 8.0)), "amb"),
    "bach": (lambda e: brook(e.get("dauer", 8.0)), "amb"),
    "voegel": (lambda e: bird(e.get("dauer", 8.0)), "amb"),
    "feuer": (lambda e: fire(e.get("dauer", 6.0)), "amb"),
    "summen": (lambda e: hum(e.get("dauer", 8.0), e.get("von", 55.0), e.get("bis")), "amb"),   # Maschinen/Fabrik, gleitend
    "blubbern": (lambda e: blubb(e.get("dauer", 6.0)), "amb"),                                   # Flüssigkeit, Zellplasma
    "klick": (lambda e: klick_s(), "sfx"),                                                        # Riegel, Tresor, Einrasten
    "klackern": (None, "sfx"),                                                                    # anzahl, abstand (Bausteine reihen sich)
}


def place(e):
    typ = e["typ"]
    if typ not in SFX: raise SystemExit(f"Unbekannter Geräuschtyp: {typ}. Erlaubt: {', '.join(SFX)}")
    fn, bus = SFX[typ]
    buf = sfx if bus == "sfx" else amb
    g, pan = e.get("gain", 1.0), e.get("pan", 0.0)
    if typ == "uhr":
        k, tt = 0, e["t"]
        while tt < e["t"] + e.get("dauer", 5):
            put(buf, tick(k % 2 == 0), tt, 0.9 * g, pan); tt += 1.0; k += 1
    elif typ == "klackern":
        for k in range(e.get("anzahl", 8)): put(buf, klick_s(), e["t"] + k * e.get("abstand", 0.4), 0.8 * g, pan)
    elif typ == "schritte":
        for k in range(e.get("anzahl", 8)): put(buf, step(), e["t"] + k * e.get("abstand", 0.5), 0.7 * g, pan)
    else:
        put(buf, fn(e), e["t"], g, pan)


if TL.get("autoSfx", True):
    place({"typ": "vorhang", "t": TL["vorhangAuf"][0], "dauer": 2.8, "gain": 0.9})
    place({"typ": "wachsmal", "t": TL["titel"][0], "dauer": TL["titel"][1] - TL["titel"][0]})
    for sc in NARR["szenen"][1:]:
        place({"typ": "papier", "t": sc["start"] - 1.1, "dauer": 2.2, "gain": 0.95, "pan": float(rng.uniform(-.3, .3))})
    place({"typ": "vorhang", "t": TL["vorhangZu"][0], "dauer": TL["vorhangZu"][1] - TL["vorhangZu"][0] + 0.4, "gain": 1.1})
for e in TL.get("sfx", []):
    place(e)


# ----------------------------------------------------------------- Sprecherin
def load_wav(p):
    with wave.open(str(p)) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    if sr != SR: g = gcd(sr, SR); a = signal.resample_poly(a, SR // g, sr // g)
    return a


abs_cues = []
for sc in NARR["szenen"]:
    a = load_wav(ROOT / "assets" / "voice" / f"scene{sc['id']:02d}.wav")
    t0 = sc["start"] + sc.get("sprechBeginn", 0.8)
    i = int(t0 * SR); voice[i:i + len(a)] += a[: N - i]
    end = t0 + len(a) / SR
    if end > sc["ende"] - 0.3: print(f"WARNUNG Szene {sc['id']}: Sprechtext endet bei {end:.1f} s, Szene endet {sc['ende']} s")
    for c in CUES[str(sc["id"])]: abs_cues.append([round(t0 + c["t0"], 2), round(t0 + c["t1"], 2), c["text"]])

voice = voice + 0.25 * lp(voice, 220)
voice = voice / (np.max(np.abs(voice)) or 1) * 0.72
venv = lp(np.abs(voice), 3.0); venv = venv / (np.max(venv) or 1)
duck = 1 - TL.get("ducking", 0.5) * np.clip(venv * 3, 0, 1)
tt = t_arr(N)
cut = np.ones(N)
if "zaesur" in TL:
    z0, z1 = TL["zaesur"]
    cut = np.where(tt < z0, 1, np.where(tt < z0 + 0.6, 1 - (tt - z0) / 0.6 * 0.94, 0.06))
    cut = np.where(tt > z1, np.minimum(1, cut + (tt - z1) / 3.5), cut)
tail = np.clip((DUR - tt) / 4.0, 0, 1) ** 1.2

music = music / (np.max(np.abs(music)) or 1)
mix = music * 0.30 * duck * cut * tail + amb * 0.9 * duck * np.maximum(cut, 0.05) + sfx + voice[None, :]
ax = np.abs(mix)
mix = np.where(ax < 0.8, mix, np.sign(mix) * (0.8 + 0.17 * np.tanh((ax - 0.8) / 0.17)))   # weicher Begrenzer, Stimme unberührt
out = (np.clip(mix, -1, 1).T * 32767).astype(np.int16)
wav_path = ROOT / "assets" / "soundtrack.wav"
with wave.open(str(wav_path), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav_path), "-c:a", "libmp3lame", "-b:a", "160k", str(ROOT / "assets" / "soundtrack.mp3")], check=True)

# ----------------------------------------------------------------- Mund-Hüllkurve + data.js
hop = SR // FPS; frames = N // hop; mouth, cen = [], []
for f in range(frames):
    s = voice[f * hop:(f + 1) * hop]; r = np.sqrt(np.mean(s ** 2)); mouth.append(r)
    if r > 1e-4:
        sp = np.abs(np.fft.rfft(s * np.hanning(len(s)))); fr = np.fft.rfftfreq(len(s), 1 / SR); cen.append(np.sum(sp * fr) / (np.sum(sp) + 1e-9))
    else: cen.append(0)
mouth = np.array(mouth)
if np.any(mouth > 0.02): mouth = np.clip((mouth - 0.012) / (np.percentile(mouth[mouth > 0.02], 90) - 0.012), 0, 1)
roundness = np.clip(1 - (np.array(cen) - 700) / 1800, 0, 1) * (mouth > 0.08)
enc = lambda v: "".join(chr(48 + int(round(x * 40))) for x in v)
data = {"dauer": DUR, "fps": FPS, "titel": NARR["titel"],
        "szenen": [{"id": s["id"], "start": s["start"], "ende": s["ende"], "titel": s["titel"]} for s in NARR["szenen"]],
        "timeline": TL, "cues": abs_cues, "mouth": enc(mouth), "round": enc(roundness)}
(ROOT / "src" / "data.js").write_text("window.PROJEKT = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf8")

# index.html aus der Vorlage (Titel, Szenenzahl, Länge)
tpl = (ROOT / "src" / "index.vorlage.html").read_text(encoding="utf8")
mins = f"{int(DUR // 60)}:{int(DUR % 60):02d} Minuten"
html = (tpl.replace("{{TITEL}}", NARR["titel"]).replace("{{KURZTITEL}}", NARR.get("kurztitel", NARR["titel"]))
        .replace("{{SZENEN}}", str(len(NARR["szenen"]))).replace("{{MINUTEN}}", mins))
(ROOT / "src" / "index.html").write_text(html, encoding="utf8")
print(f"Tonspur fertig: {DUR} s, {len(TL.get('sfx', []))} Geräusche, {len(TL.get('musik', []))} Musikabschnitte")
