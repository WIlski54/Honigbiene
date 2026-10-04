"""Kontaktbogen aus Testbildern (build/snaps/tNNNN.NN.jpg, erzeugt mit export_video.py --snap):
   python build/kontaktbogen.py bogen.jpg 5 12.5 30 44   (2 Spalten, je 960x540, beliebig viele Bilder)"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
snaps = Path(__file__).parent / "snaps"
out, ts = sys.argv[1], sys.argv[2:]
cols = 2
rows = (len(ts) + 1) // 2
sheet = Image.new("RGB", (960 * cols, 540 * rows), "white")
for i, t in enumerate(ts):
    im = Image.open(snaps / f"t{float(t):07.2f}.jpg").resize((960, 540))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 90, 26], fill="black")
    d.text((6, 6), f"{float(t):.1f}s", fill="white")
    sheet.paste(im, ((i % cols) * 960, (i // cols) * 540))
sheet.save(out, quality=88)
