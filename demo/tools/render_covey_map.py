"""Renders the REAL Covey.Town map (frontend/public/assets/tilemaps/indoors.json from the class repo)
to a single image, and exports the real "misa" avatar atlas frames used by Covey.Town.

Usage: python render_covey_map.py <path to class repo frontend/public/assets> <demo/public/assets/town>
Writes: covey_map.webp (+ covey_map_preview.png at 1/4 scale), misa.png, misa.json (frame rects)."""
import json
import pathlib
import sys

from PIL import Image

src = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
m = json.load(open(src / "tilemaps" / "indoors.json"))
TW = m["tilewidth"]; W, H = m["width"], m["height"]
sets = []
for ts in m["tilesets"]:
    img = Image.open((src / "tilemaps" / ts["image"]).resolve()).convert("RGBA")
    sets.append((ts["firstgid"], img, ts["columns"], ts.get("margin", 0), ts.get("spacing", 0)))
sets.sort(key=lambda t: -t[0])
FLIPH, FLIPV, FLIPD = 0x80000000, 0x40000000, 0x20000000


def tile(gid):
    for first, img, cols, mar, spc in sets:
        if gid >= first:
            i = gid - first
            x = mar + (i % cols) * (TW + spc); y = mar + (i // cols) * (TW + spc)
            return img.crop((x, y, x + TW, y + TW))
    return None


canvas = Image.new("RGBA", (W * TW, H * TW), (27, 24, 48, 255))
for layer in m["layers"]:
    if layer["type"] != "tilelayer" or not layer.get("visible", True):
        continue
    for idx, raw in enumerate(layer["data"]):
        if raw == 0:
            continue
        gid = raw & ~(FLIPH | FLIPV | FLIPD)
        t = tile(gid)
        if t is None:
            continue
        if raw & FLIPD:
            t = t.transpose(Image.TRANSPOSE)
        if raw & FLIPH:
            t = t.transpose(Image.FLIP_LEFT_RIGHT)
        if raw & FLIPV:
            t = t.transpose(Image.FLIP_TOP_BOTTOM)
        canvas.alpha_composite(t, ((idx % W) * TW, (idx // W) * TW))
canvas.convert("RGB").save(out / "covey_map.webp", quality=88, method=6)
canvas.convert("RGB").resize((W * TW // 4, H * TW // 4)).save(out / "covey_map_preview.png")

atlas = json.load(open(src / "atlas" / "atlas.json"))
Image.open(src / "atlas" / "atlas.png").save(out / "misa.png")
frames = {k: v["frame"] for k, v in atlas["frames"].items()}
json.dump(frames, open(out / "misa.json", "w"))
print("map", canvas.size, "frames", len(frames), sorted(frames)[:4])
