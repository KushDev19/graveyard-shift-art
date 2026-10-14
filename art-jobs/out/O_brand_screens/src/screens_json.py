"""Write screens.json: files, sizes, title crop, podium ellipses + stage lines, burst-ray layers."""
import json, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parents[1]
pods = json.load(open(OUT / "src" / "podiums_fit.json"))
rays = json.load(open(OUT / "src" / "_rays_meta.json"))
doc = {"_coords": "source pixels of raw_originals/<file>; *_norm values are 0..1 of width/height so they work for any export size",
       "screens": {}}
for src in sorted((ROOT / "raw_originals").glob("[23][0-9]_SCREEN_*.png")):
    W, H = Image.open(src).size
    key = src.stem.lower(); n = src.stem[:2]
    e = {"source": f"raw_originals/{src.name}", "size": [W, H],
         "webp": [f"screens/{key}_{w}.webp" for w in (1920, 3840)]}
    if n == "27":
        y0 = 1720
        e["crop_16x9"] = {"x": 0, "y": y0, "w": 4096, "h": 2304,
                          "webp": [f"screens/{key}_16x9_{w}.webp" for w in (1920, 3840)]}
    if src.stem in pods:
        cx, cy, a, b, _ = pods[src.stem]
        e["podium_top"] = {"cx": cx, "cy": cy, "rx": a, "ry": b,
                           "cx_norm": round(cx / W, 4), "cy_norm": round(cy / H, 4),
                           "rx_norm": round(a / W, 4), "ry_norm": round(b / H, 4)}
        x0, x1 = round(cx - 0.8 * a), round(cx + 0.8 * a)
        e["stage_line"] = {"y": cy, "x0": x0, "x1": x1, "y_norm": round(cy / H, 4),
                           "x0_norm": round(x0 / W, 4), "x1_norm": round(x1 / W, 4),
                           "note": "feet of standing characters go on this line (centre of the podium top); spread lineups between x0 and x1"}
    if n in rays:
        r = rays[n]
        e["burst"] = {"svg": r["rays_svg"], "group": "rays", "backing": "backing", "pivot": r["pivot"],
                      "pivot_norm": [round(r["pivot"][0] / W, 4), round(r["pivot"][1] / H, 4)],
                      "foreground_webp": r["fg"], "ray_count": r["ray_count"],
                      "stack": "backing rect, then rotate #rays about pivot, then the foreground WebP on top"}
    doc["screens"][key] = e
(OUT / "screens.json").write_text(json.dumps(doc, indent=1))
print(json.dumps(doc["screens"]["33_screen_win_crew"], indent=0)[:400])
