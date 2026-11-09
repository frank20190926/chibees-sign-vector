#!/usr/bin/env python3
"""Render board1/2/3.html (1600x1200 CSS px, DPR 2) with headless Chrome -> chibees_boardN.jpg at 3200x2400, q95."""
import pathlib, subprocess, sys, tempfile
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def render(n):
    html = ROOT / f"board{n}.html"
    out = ROOT / f"chibees_board{n}.jpg"
    with tempfile.TemporaryDirectory() as td:
        png = pathlib.Path(td) / "shot.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--user-data-dir={td}/profile", "--allow-file-access-from-files",
                        "--force-device-scale-factor=2", "--window-size=1600,1200",
                        "--virtual-time-budget=8000", f"--screenshot={png}", html.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        im = Image.open(png).convert("RGB")
        if im.size != (3200, 2400):
            print("size", im.size, "-> adjusting"); im = im.crop((0, 0, 3200, 2400)) if im.size[0] >= 3200 and im.size[1] >= 2400 else im.resize((3200, 2400), Image.LANCZOS)
        im.save(out, quality=95, subsampling=0)
    print("wrote", out.name, Image.open(out).size)

if __name__ == "__main__":
    for n in (sys.argv[1:] or ["1", "2", "3"]):
        render(n)
