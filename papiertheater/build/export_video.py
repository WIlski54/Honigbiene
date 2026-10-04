"""Rendert die Animation Bild für Bild mit Microsoft Edge (headless) und erzeugt ein MP4.

Aufruf:
  python build/export_video.py                      -> <datei>.mp4 (1920x1080, 24 fps, ca. 35 MB je Minute)
  python build/export_video.py --snap 5,30.5,88     -> Einzelbilder als JPG (zum Prüfen)
  python build/export_video.py --start 60 --end 70  -> nur Ausschnitt (Test)
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

ROOT = Path(__file__).resolve().parent.parent
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
import socket


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = free_port()   # frei gewählt: --snap und Export dürfen parallel laufen


class Page:
    def __init__(self):
        exe = next((p for p in EDGE_CANDIDATES if os.path.exists(p)), None)
        if not exe:
            sys.exit("Kein Edge/Chrome gefunden.")
        self.tmp = tempfile.mkdtemp(prefix="sarajevo_edge_")
        url = (ROOT / "src" / "index.html").as_uri() + "#export"
        self.proc = subprocess.Popen([
            exe, "--headless=new", f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
            f"--user-data-dir={self.tmp}", "--window-size=1920,1080", "--hide-scrollbars", "--mute-audio",
            "--force-device-scale-factor=1", "--disable-background-timer-throttling", url,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target = None
        for _ in range(100):
            try:
                lst = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=2).read())
                target = next((x for x in lst if x.get("type") == "page" and "index.html" in x.get("url", "")), None)
                if target:
                    break
            except Exception:
                pass
            time.sleep(0.2)
        if not target:
            self.close()
            sys.exit("Edge-Seite nicht erreichbar.")
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], max_size=None, timeout=120)
        self.mid = 0
        for _ in range(150):
            if self.eval("window.exportReady === true"):
                break
            time.sleep(0.2)
        else:
            err = self.eval("String(window.__err || '')")
            self.close()
            sys.exit("Seite nicht bereit. " + str(err))

    def eval(self, expr):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": "Runtime.evaluate",
                                 "params": {"expression": expr, "returnByValue": True, "awaitPromise": True}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.mid:
                res = msg.get("result", {})
                if "exceptionDetails" in res:
                    raise RuntimeError(json.dumps(res["exceptionDetails"])[:800])
                return res.get("result", {}).get("value")

    def frame(self, t):
        url = self.eval(f"renderAt({t:.5f})")
        return base64.b64decode(url.split(",", 1)[1])

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()
        try:
            self.proc.wait(5)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", default="")
    ap.add_argument("--outdir", default=str(ROOT / "build" / "snaps"))
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=0.0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    narr = json.loads((ROOT / "build" / "narration.json").read_text(encoding="utf8"))
    tl = json.loads((ROOT / "build" / "timeline.json").read_text(encoding="utf8"))
    args.end = args.end or tl["dauer"]
    args.out = args.out or str(ROOT / (narr["datei"] + ".mp4"))

    page = Page()
    try:
        if args.snap:
            od = Path(args.outdir)
            od.mkdir(parents=True, exist_ok=True)
            for s in args.snap.split(","):
                t = float(s)
                (od / f"t{t:07.2f}.jpg").write_bytes(page.frame(t))
                print("Bild", t)
            return

        # 12 Zeichnungen pro Sekunde, jede zweimal -> 24 fps (Stop-Motion „on twos“)
        n = int(round((args.end - args.start) * 12))
        silent = str(ROOT / "build" / "_video_noaudio.mp4")
        ff = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", "12", "-c:v", "mjpeg", "-i", "-",
            "-r", "24", "-c:v", "libx264", "-preset", "slow", "-b:v", "4500k", "-maxrate", "6000k", "-bufsize", "9000k",
            "-pix_fmt", "yuv420p", silent,
        ], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(n):
            t = args.start + i / 12 + 1e-4
            ff.stdin.write(page.frame(t))
            if i % 60 == 0:
                el = time.time() - t0
                print(f"{i}/{n} Bilder  ({el:.0f}s, noch ca. {el / max(1, i) * (n - i):.0f}s)", flush=True)
        ff.stdin.close()
        ff.wait()
        audio = ROOT / "assets" / "soundtrack.wav"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", silent, "-ss", str(args.start), "-t", str(args.end - args.start),
            "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest", args.out,
        ], check=True)
        os.remove(silent)
        print("Fertig:", args.out)
    finally:
        page.close()


if __name__ == "__main__":
    main()
