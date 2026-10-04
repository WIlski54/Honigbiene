"""Erzeugt build/timeline.json aus den Satzzeiten der Stimme (assets/voice/cues.json) und den Szenenzeiten.
Alle Bild-Ereignisse liegen auf dem Satz bzw. Satzteil, der sie nennt (Wortzeiten werden aus der Satzlänge geschätzt).
Aufruf: python build/timeline_erzeugen.py   (danach: python build/make_audio.py)"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))
CUES = json.loads((ROOT / "assets" / "voice" / "cues.json").read_text(encoding="utf8"))
SC = {s["id"]: s for s in N["szenen"]}


def satz(sid, i):
    """(von, bis) des i-ten Satzes (0-basiert) in absoluten Sekunden."""
    s = SC[sid]
    a = s["start"] + s.get("sprechBeginn", 0.8)
    q = CUES[str(sid)][i]
    return round(a + q["t0"], 2), round(a + q["t1"], 2)


def _gew(tok):
    if tok in ",;":
        return 0.7
    if tok in ":":
        return 0.9
    if tok in ".!?":
        return 0.0
    return max(1, len(re.findall(r"[aeiouyäöü]+", tok.lower()))) + 0.3 * len(tok) / 6


def wort(sid, i, frag):
    """(von, bis) eines Satzteils `frag` im i-ten Satz, geschätzt nach Silben (±0,3 s)."""
    s = SC[sid]
    a = s["start"] + s.get("sprechBeginn", 0.8)
    q = CUES[str(sid)][i]
    t0, t1 = a + q["t0"], a + q["t1"]
    toks = re.findall(r"[\wäöüÄÖÜß-]+|[,.:!?;]", q["text"])
    cum, tot = [], 0.0
    for tk in toks:
        cum.append((tot, tot + _gew(tk)))
        tot += _gew(tk)
    ft = re.findall(r"[\wäöüÄÖÜß-]+", frag)
    low = [t.lower() for t in toks]
    for k in range(len(toks)):
        if all(k + j < len(toks) and low[k + j].startswith(ft[j].lower()[:5]) for j in range(len(ft))):
            e = k + len(ft) - 1
            f0, f1 = cum[k][0] / tot, cum[e][1] / tot
            return round(t0 + (t1 - t0) * f0, 2), round(t0 + (t1 - t0) * f1, 2)
    raise SystemExit(f"Satzteil nicht gefunden: {frag!r} in Szene {sid} Satz {i}")


def r(*v):
    return [round(x, 2) for x in v]


E = {}
SFX = []


def sfx(typ, t, **kw):
    SFX.append(dict(typ=typ, t=round(t, 2), **kw))


# ------------------------------------------------------------------ Szene 1 (Klassenzimmer, Tafel)
E["dauer"] = 240
E["vorhangAuf"] = [0.2, 2.9]
E["titel"] = [0.9, 3.1]
E["vorhangZu"] = [235.4, 239.6]
s1a = satz(1, 0); s1b = satz(1, 1); s1c = satz(1, 2); s1d = satz(1, 3)
bienen_w = wort(1, 1, "bis zu fünfzigtausend Bienen")
E["tafelKasten"] = r(3.5, 6.7)
E["tafelBlumen"] = r(6.9, 9.0)
E["tafelBienen"] = r(bienen_w[0], bienen_w[1] + 0.6)
E["tafelFrage"] = r(s1c[0] + 0.1, s1c[1] - 0.4)
E["aufklappen"] = r(s1d[0], s1d[0] + 1.3)
E["zoom"] = r(s1d[0] + 0.4, s1d[0] + 3.4)
E["geste"] = [0.8, 3.2]

# ------------------------------------------------------------------ Szene 2 (Wiese, Kasten, Imker)
a1, a2, a3 = satz(2, 0), satz(2, 1), satz(2, 2)
E["wieseRaus"] = r(20.0, 23.6)                 # Kamera zieht aus dem Tafelbild heraus
E["imkerGeht"] = r(a1[0] - 0.4, a1[0] + 3.0)
kast_w = wort(2, 0, "Bienenkästen")
E["kaesten"] = r(kast_w[0], kast_w[0] + 0.5, kast_w[0] + 1.0)
E["flugFokus"] = r(a2[0] - 0.4, a2[0] + 3.2)   # Kamera fährt zum Kasten
fl_w = wort(2, 1, "Flugloch")
E["flugRing"] = r(fl_w[0] - 0.1, fl_w[0] + 1.3)
E["waechter"] = r(a3[0] + 0.1, a3[1] + 1.0)
E["kastenAuf"] = r(39.0, 40.4)

# ------------------------------------------------------------------ Szene 3 (Waben, Brutraum, Honigraum)
b1, b2, b3 = satz(3, 0), satz(3, 1), satz(3, 2)
hex_w = wort(3, 0, "sechseckigen Zellen")
E["fuellen"] = r(42.2, 46.4)
E["rahmenVor"] = r(hex_w[0] - 1.4, hex_w[0] - 0.1)
E["sechseck"] = r(hex_w[0] - 0.3, hex_w[1] + 0.4)
E["rahmenZurueck"] = r(b1[1] + 0.0, b1[1] + 1.3)
E["brutLinie"] = r(b2[0] + 0.5, b2[1] - 0.2)
E["honigLinie"] = r(b3[0] + 0.5, b3[1] - 0.2)
E["kamStock"] = r(55.2, 60.2)                  # Kamera fährt über die Wabe
E["teppich"] = r(56.2, 61.6)

# ------------------------------------------------------------------ Szene 4 (drei Arten)
c1, c2, c3 = satz(4, 0), satz(4, 1), satz(4, 2)
k_w = wort(4, 0, "eine Königin")
w_w = wort(4, 0, "viele tausend Arbeiterinnen")
d_w = wort(4, 0, "einige hundert Drohnen")
E["koeniginSpot"] = r(k_w[0] - 0.3, k_w[1] + 0.2)
E["arbeiterinSpot"] = r(E["koeniginSpot"][1], max(w_w[1] + 0.2, E["koeniginSpot"][1] + 1.4))
E["drohnenSpot"] = r(E["arbeiterinSpot"][1], max(d_w[1] + 0.9, E["arbeiterinSpot"][1] + 1.8))
E["paaren"] = r(c2[0] + 0.3, c2[1] - 0.2)
E["zusammen"] = r(c3[0], c3[1] + 0.6)
E["koeniginBleibt"] = r(c3[1] + 0.9, 80.0)

# ------------------------------------------------------------------ Szene 5 (Königin legt Eier)
d1, d2, d3 = satz(5, 0), satz(5, 1), satz(5, 2)
E["hofstaat"] = r(d1[0] - 0.2, d1[0] + 1.2)
E["legen"] = r(d2[0] + 0.4, d2[1] - 0.2)
E["befehle"] = r(d3[0], d3[1] + 0.3)
E["haende"] = r(d3[0] - 0.3, d3[1] + 1.8)
E["kartePop"] = r(96.0, 97.4)

# ------------------------------------------------------------------ Szene 6 (Ei → Biene)
e1, e2, e3, e4 = satz(6, 0), satz(6, 1), satz(6, 2), satz(6, 3)
lv_w = wort(6, 0, "eine Larve")
E["kalender"] = r(e1[0] - 0.1, e1[0] + 12.6)      # 21 Blätter
E["larve"] = r(lv_w[0] - 0.6, lv_w[0] + 0.5)
E["futter"] = r(e2[0] + 0.1, e2[0] + 2.4)
vd_w = wort(6, 1, "verdeckelt")
E["deckel"] = r(vd_w[0] - 0.7, vd_w[1] + 0.2)
E["puppe"] = r(e3[0], e3[0] + 1.6)
E["biene"] = r(e3[1] + 0.2, e4[0] + 2.0)
E["biss"] = r(e4[0] + 2.2, e4[0] + 3.4)
E["rausch"] = r(e4[0] + 3.4, e4[0] + 5.4)
E["karteWeg"] = r(e4[1] + 0.9, e4[1] + 2.4)

# ------------------------------------------------------------------ Szene 7 (Aufgaben)
f1, f2, f3, f4 = satz(7, 0), satz(7, 1), satz(7, 2), satz(7, 3)
bw = wort(7, 2, "bauen sie Waben")
ww = wort(7, 2, "halten Wache")
E["rolle1"] = r(f1[0] - 0.1, f2[0] - 0.2)
E["rolle2"] = r(f2[0] - 0.1, bw[0] - 0.1)
E["rolle3"] = r(bw[0] - 0.1, ww[0] - 0.2)
E["rolle4"] = r(ww[0] - 0.1, 138.9)
E["alterRolle"] = r(f4[0], f4[0] + 1.0, f4[0] + 1.6, f4[0] + 2.2)   # vier Schilder mit Pfeilen
E["flugCam"] = r(f4[1] + 0.3, 138.9)

# ------------------------------------------------------------------ Szene 8 (Sammlerinnen)
g1, g2, g3 = satz(8, 0), satz(8, 1), satz(8, 2)
rw = wort(8, 1, "Rüssel")
nw = wort(8, 1, "Nektar")
mw = wort(8, 1, "Honigmagen")
pw = wort(8, 2, "Pollen")
hw = wort(8, 2, "Hinterbein")
E["ausflug"] = r(140.6, g1[1] + 0.8)
E["landen"] = r(g1[1] + 0.3, g2[0] + 0.5)
E["ruessel"] = r(rw[0] - 0.2, rw[0] + 0.8)
E["spotRuessel"] = r(rw[0] - 0.1, rw[1] + 0.6)
E["strich"] = r(nw[0], mw[1] + 0.3)
E["spotMagen"] = r(mw[0] - 0.2, g2[1] + 0.3)
E["magenFuell"] = r(nw[0], g2[1] + 0.2)
E["spotHoeschen"] = r(pw[0] - 0.1, g3[1] + 0.4)
E["pollenFuell"] = r(pw[0], g3[1] + 0.3)
E["rueckflug"] = r(g3[1] + 0.8, 158.6)

# ------------------------------------------------------------------ Szene 9 (Tanz)
h1, h2, h3 = satz(9, 0), satz(9, 1), satz(9, 2)
E["tanzKommt"] = r(161.3, 163.3)
E["tanzSammeln"] = r(163.6, 166.2)
E["richtung"] = r(h2[0] + 0.1, h2[1] + 0.8)
E["dauerTanz"] = r(h3[0] + 0.1, h3[1] + 1.0)
E["weitWeg"] = r(h3[0] + 1.2, h3[1] + 2.0)
E["folgerGehen"] = r(175.5, 178.3)
E["tropfen"] = r(178.0, 181.6)

# ------------------------------------------------------------------ Szene 10 (Honig)
i1, i2, i3, i4 = satz(10, 0), satz(10, 1), satz(10, 2), satz(10, 3)
E["weitergeben"] = r(i1[0], i1[0] + 3.8)
E["faecheln"] = r(i1[0] + 3.6, i2[1] + 2.0)
E["reif"] = r(i2[0], i2[1] + 0.4)
E["verschliessen"] = r(i3[0] + 0.1, i3[1] + 0.2)
E["ernteZoom"] = r(i4[0] - 0.4, i4[0] + 1.8)             # Übergang nach draußen
E["rahmenZiehen"] = r(i4[0] + 1.2, i4[1] + 1.5)
E["glasFuellen"] = r(i4[0] + 1.5, i4[1] + 3.5)
E["herbst"] = r(196.8, 200.4)
E["kamWinter"] = r(197.0, 201.6)

# ------------------------------------------------------------------ Szene 11 (Winter)
j1, j2, j3, j4 = satz(11, 0), satz(11, 1), satz(11, 2), satz(11, 3)
E["schnitt"] = r(j1[1] - 0.2, j1[1] + 0.9)                # Querschnitt erscheint
E["schnittZoom"] = r(j1[1] + 0.5, j2[0] + 2.0)
E["traube"] = r(j2[0], j2[1] + 0.3)
E["zittern"] = r(j3[0], j3[1] + 0.8)
E["muskel"] = r(j3[0] + 0.6, j3[1])
E["honigVorrat"] = r(j4[0], j4[1] + 0.8)

# ------------------------------------------------------------------ Szene 12 (Schluss)
l1, l2, l3 = satz(12, 0), satz(12, 1), satz(12, 2)
E["karten"] = r(l1[0] + 0.1, l1[0] + 0.8, l1[0] + 1.5, l1[0] + 2.0)
E["verbinden"] = r(l1[0] + 1.6, l1[1] + 0.2)
E["ring"] = r(l2[0], l2[1] + 0.2)
ho_w = wort(12, 2, "Honig")
wa_w = wort(12, 2, "Wachs")
fr_w = wort(12, 2, "Früchte")
E["tischDinge"] = r(ho_w[0] - 0.2, wa_w[0] - 0.2, fr_w[0] - 0.2)
E["blick"] = 233.2

# ------------------------------------------------------------------ Musik und Zäsur
E["musik"] = [
    {"a": 0.6, "e": 9, "stimmung": "ruhig"},
    {"a": 9, "e": 20, "stimmung": "neugierig"},
    {"a": 20, "e": 80, "stimmung": "heiter"},
    {"a": 80, "e": 120, "stimmung": "staunend"},
    {"a": 120, "e": 200, "stimmung": "heiter"},
    {"a": 200, "e": 232, "stimmung": "nachdenklich"},
]
E["zaesur"] = r(205.0, 214.5)        # Winter: Musik und Atmo fast weg

# ------------------------------------------------------------------ Geräusche
stock_hum = [(40, 60, 0.42), (60, 125, 0.5), (160, 195, 0.5)]
# Wiese: Vögel, Wind, leises Summen
sfx("voegel", 14.2, dauer=26, gain=0.55)
sfx("wind", 17.0, dauer=23, gain=0.5)
sfx("summen", 20, dauer=19, von=205, gain=0.35)
sfx("summen", 20, dauer=19, von=250, gain=0.22)
# Im Stock dichter
for a, b, g in stock_hum:
    sfx("summen", a, dauer=b - a, von=190, gain=g)
    sfx("summen", a, dauer=b - a, von=235, gain=g * 0.8)
    sfx("summen", a + 1, dauer=b - a - 2, von=270, gain=g * 0.55)
sfx("summen", 120, dauer=20, von=200, gain=0.4)
sfx("summen", 125, dauer=15, von=240, gain=0.3)
sfx("voegel", 139, dauer=21, gain=0.55)
sfx("wind", 140, dauer=19, gain=0.45)
sfx("summen", 140, dauer=19, von=215, gain=0.35)
sfx("summen", 196, dauer=6, von=205, gain=0.3)
sfx("voegel", 193.5, dauer=5, gain=0.45)
sfx("wind", 196, dauer=10, gain=0.45)
sfx("wind", 200, dauer=18, gain=0.6)
sfx("summen", 201, dauer=18, von=180, gain=0.12)

# Papier- und Zeichengeräusche
def wachs(a, b, pan=0.2):
    sfx("wachsmal", a, dauer=round(b - a, 2), pan=pan)

wachs(*E["tafelKasten"], pan=0.3)
wachs(*E["tafelBlumen"], pan=0.35)
wachs(*E["tafelBienen"], pan=0.3)
wachs(*E["tafelFrage"], pan=0.3)
sfx("papier", E["aufklappen"][0], dauer=1.2)
for k, t in enumerate(E["kaesten"]):
    sfx("pop", t)
sfx("pop", E["imkerGeht"][1])
wachs(*E["flugRing"], pan=-0.2)
sfx("glocke", E["flugRing"][1] + 0.1, ton=1174.7)
sfx("glocke", E["waechter"][0] + 0.6, ton=1174.7)
sfx("wusch", 38.8, dauer=1.2, gain=0.5)
sfx("pop", E["kastenAuf"][0] + 0.3)
wachs(*E["brutLinie"], pan=-0.2)
sfx("glocke", E["brutLinie"][1], ton=1318.5)
wachs(*E["honigLinie"], pan=0.2)
sfx("glocke", E["honigLinie"][1], ton=1568)
sfx("papier", E["rahmenVor"][0], dauer=1.0, gain=0.6)
sfx("papier", E["rahmenZurueck"][0], dauer=1.0, gain=0.6)
for key, ton in [("koeniginSpot", 1318.5), ("arbeiterinSpot", 1174.7), ("drohnenSpot", 1046.5)]:
    sfx("pop", E[key][0] + 0.3)
    sfx("glocke", E[key][0] + 0.5, ton=ton)
sfx("pop", E["paaren"][0]); sfx("glocke", E["paaren"][0] + 0.2, ton=1568)
wachs(*E["zusammen"], pan=0.0)
sfx("glocke", E["zusammen"][1], ton=1318.5)
sfx("pop", E["hofstaat"][0] + 0.2)
for k in range(8):
    sfx("pop", E["legen"][0] + 0.2 + k * (E["legen"][1] - E["legen"][0] - 0.4) / 7, gain=0.6)
sfx("pop", E["befehle"][0] + 0.1)
sfx("pop", E["kartePop"][0])
sfx("blaettern", E["kalender"][0], dauer=round(E["kalender"][1] - E["kalender"][0], 2), gain=0.8)
sfx("uhr", E["kalender"][0], dauer=round(E["kalender"][1] - E["kalender"][0], 2), gain=0.5)
sfx("glocke", E["larve"][1], ton=1174.7)
sfx("pop", E["larve"][0] + 0.4)
sfx("klick", E["deckel"][1])
sfx("glocke", E["puppe"][1], ton=1318.5)
sfx("pop", E["rausch"][0] + 0.5)
sfx("glocke", E["rausch"][1], ton=1568)
for k, key in enumerate(["rolle1", "rolle2", "rolle3", "rolle4"]):
    sfx("pop", E[key][0] + 0.1)
    sfx("blaettern", E[key][0], dauer=0.9, gain=0.6)
for t in E["alterRolle"]:
    sfx("pop", t, gain=0.7)
wachs(E["alterRolle"][0] + 0.5, E["alterRolle"][3] + 0.6, pan=0.0)
sfx("glocke", E["alterRolle"][3] + 0.8, ton=1318.5)
sfx("wusch", 138.8, dauer=1.2, gain=0.5)
sfx("wusch", 158.8, dauer=1.2, gain=0.5)
sfx("pop", E["spotRuessel"][0] + 0.2); sfx("glocke", E["spotRuessel"][0] + 0.4, ton=1174.7)
wachs(*E["strich"], pan=0.2)
sfx("pop", E["spotMagen"][0] + 0.2); sfx("glocke", E["spotMagen"][0] + 0.4, ton=1318.5)
sfx("pop", E["spotHoeschen"][0] + 0.2); sfx("glocke", E["spotHoeschen"][0] + 0.4, ton=1568)
wachs(E["richtung"][0] + 0.2, E["richtung"][1] - 0.2, pan=0.0)
sfx("glocke", E["richtung"][1], ton=1318.5)
wachs(E["dauerTanz"][0] + 0.2, E["dauerTanz"][1] - 0.2, pan=0.0)
sfx("glocke", E["dauerTanz"][1], ton=1568)
sfx("pop", E["tropfen"][0] + 1.0, gain=0.7)
sfx("papier", E["faecheln"][0], dauer=3.0, gain=0.5)
sfx("klick", E["verschliessen"][0] + 0.3, gain=0.5)
sfx("klick", E["verschliessen"][0] + 0.9, gain=0.5)
sfx("klick", E["verschliessen"][0] + 1.4, gain=0.5)
sfx("wusch", E["ernteZoom"][0] + 0.2, dauer=1.4, gain=0.5)
sfx("glocke", E["glasFuellen"][1], ton=1568)
sfx("blaettern", E["herbst"][0], dauer=3.0, gain=0.5)
sfx("pop", E["schnitt"][0] + 0.2)
sfx("pop", E["zittern"][0] - 0.1)
sfx("pop", E["richtung"][0] - 0.1)
sfx("papier", E["kartePop"][0] + 0.1, dauer=0.8, gain=0.6)
sfx("glocke", E["traube"][0] + 0.3, ton=1046.5, gain=0.6)
sfx("glocke", E["muskel"][0] + 0.3, ton=1174.7, gain=0.6)
for k, t in enumerate(E["karten"]):
    sfx("pop", t)
wachs(*E["verbinden"], pan=0.3)
sfx("glocke", E["verbinden"][1], ton=1318.5)
wachs(*E["ring"], pan=0.3)
for t, ton in zip(E["tischDinge"], (1174.7, 1318.5, 1568)):
    sfx("pop", t); sfx("glocke", t + 0.2, ton=ton)

E["ducking"] = 0.45
E["sfx"] = sorted(SFX, key=lambda e: e["t"])
(ROOT / "build" / "timeline.json").write_text(json.dumps(E, ensure_ascii=False, indent=1), encoding="utf8")
print(f"timeline.json: {len(E)} Felder, {len(SFX)} Geräusche")
