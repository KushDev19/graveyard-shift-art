"""Per-object MAE + check images, half-scale PNG exports, labelled PREVIEW.png."""
import io, json, pathlib, re, sys
import numpy as np, cv2, cairosvg
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load, bg_plate, mae, checks

OUT = pathlib.Path(__file__).resolve().parents[1]


def render_str(svg, w, h):
    return np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert("RGBA")).astype(np.float32)


def groups(svg):
    return re.findall(r'<g id="([^"]+)"', svg)


def only(svg, gid, all_ids):
    for g in all_ids:
        if g != gid:
            svg = re.sub(r'<g id="%s"[^>]*>.*?</g>(?=\n|<g id=|</g>|$)' % g, "", svg, flags=re.S)
    return svg


res = {}
for svgname, raw, top in (("logo.svg", "23_LOGO.png", ["glow", "racing_stripe", "moon", "letters", "helmet_dot"]),
                          ("arcade.svg", "26_ARCADE_HD.png", ["cabinet", "marquee", "screen", "coin_door", "controls"])):
    s = (OUT / svgname).read_text()
    orig = load(raw); H, W = orig.shape[:2]; plate = bg_plate(orig)
    full = render_str(s, W, H)
    ys, xs = np.nonzero(full[..., 3] > 0)
    bb = (max(xs.min() - 16, 0), max(ys.min() - 16, 0), min(xs.max() + 16, W), min(ys.max() + 16, H))
    m, _ = mae(full, orig, plate, bb); res[svgname[:-4] + " (whole)"] = round(m, 2)
    ids = groups(s)
    for g in top:
        if g in ("glow", "cabinet"):
            continue
        # group bbox from its own path coordinates (letters group is nested: take everything inside)
        pat = r'<g id="letters">(.*?)</g></g>' if g == "letters" else r'<g id="%s"[^>]*>(.*?)</g>\n' % g
        body = re.search(pat, s + "\n", flags=re.S).group(1)
        nums = np.array([float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", " ".join(re.findall(r'd="([^"]+)"', body)))])
        px, py = nums[0::2], nums[1::2]
        b = (int(max(px.min() - 16, 0)), int(max(py.min() - 16, 0)), int(min(px.max() + 16, W)), int(min(py.max() + 16, H)))
        mm, comp = mae(full, orig, plate, b)
        checks(f"{svgname[:-4]}_{g}", comp, orig[b[1]:b[3], b[0]:b[2]], OUT / "check", maxw=1400)
        res[f"{svgname[:-4]}/{g}"] = round(mm, 2)
    # half-scale PNG export (RGBA)
    Image.fromarray(render_str(s, W // 2, H // 2).astype(np.uint8), "RGBA").save(OUT / svgname.replace(".svg", ".png"), optimize=True)
for extra in ("logo_mono_cream.svg", "arcade_screen.svg", "arcade_marquee_blank.svg"):
    s = (OUT / extra).read_text()
    w, h = [int(v) for v in re.search(r'width="(\d+)" height="(\d+)"', s).groups()]
    Image.fromarray(render_str(s, w // 2, h // 2).astype(np.uint8), "RGBA").save(OUT / extra.replace(".svg", ".png"), optimize=True)
old = json.loads((OUT / "check" / "mae.json").read_text())
old.update({k: {"mae": v} for k, v in res.items()})
(OUT / "check" / "mae.json").write_text(json.dumps(old, indent=1))
print(json.dumps(res, indent=1))
