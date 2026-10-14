"""Render an SVG at source size, composite over the source background plate, write check images + MAE.
usage: verify.py <svg> <raw_original> <name> [x0 y0 x1 y1]"""
import io, json, pathlib, sys
import numpy as np, cv2, cairosvg
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, bg_plate, mae, checks

OUT = pathlib.Path(__file__).resolve().parents[1]


def render(svg, w, h):
    png = cairosvg.svg2png(url=str(svg), output_width=w, output_height=h)
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA")).astype(np.float32)


def run(svg, raw, name, bbox=None):
    orig = load(raw)
    h, w = orig.shape[:2]
    plate = bg_plate(orig)
    rgba = render(svg, w, h)
    if bbox is None:
        ys, xs = np.nonzero(rgba[..., 3] > 0)
        bbox = (max(xs.min() - 16, 0), max(ys.min() - 16, 0), min(xs.max() + 16, w), min(ys.max() + 16, h))
    m, comp = mae(rgba, orig, plate, bbox)
    x0, y0, x1, y1 = bbox
    checks(name, comp, orig[y0:y1, x0:x1], OUT / "check")
    res = json.loads((OUT / "check" / "mae.json").read_text()) if (OUT / "check" / "mae.json").exists() else {}
    res[name] = {"mae": round(m, 2), "bbox": [int(v) for v in bbox]}
    (OUT / "check" / "mae.json").write_text(json.dumps(res, indent=1))
    print(name, "MAE", round(m, 2), "bbox", bbox)
    return rgba


if __name__ == "__main__":
    a = sys.argv[1:]
    run(a[0], a[1], a[2], tuple(map(int, a[3:7])) if len(a) > 3 else None)
