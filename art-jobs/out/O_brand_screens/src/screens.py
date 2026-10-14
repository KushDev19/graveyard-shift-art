"""Export screens 27-34 as WebP (1920 and 3840 wide, q85) plus the 16:9 title crop."""
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parents[1] / "screens"
TITLE_169_Y0 = 1720  # 4096x2304 window keeps the planet ring and the whole ship

for src in sorted((ROOT / "raw_originals").glob("[23][0-9]_SCREEN_*.png")):
    im = Image.open(src).convert("RGB")
    jobs = [(src.stem.lower(), im)]
    if src.stem.startswith("27"):
        jobs.append((src.stem.lower() + "_16x9", im.crop((0, TITLE_169_Y0, 4096, TITLE_169_Y0 + 2304))))
    for name, img in jobs:
        for w in (1920, 3840):
            r = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
            r.save(OUT / f"{name}_{w}.webp", "WEBP", quality=85, method=6)
        print(name, img.size)
