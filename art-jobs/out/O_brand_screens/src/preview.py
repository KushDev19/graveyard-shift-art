"""PREVIEW.png: every Job O deliverable, labelled, on cream."""
import io, json, pathlib, re
import numpy as np, cairosvg, cv2
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(__file__).resolve().parents[1]
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
CREAM, PLUM, INK = (244, 230, 200), (61, 42, 79), (42, 30, 53)
mae = json.loads((OUT / "check" / "mae.json").read_text())


def svg(path, w, drop=()):
    s = (OUT / path).read_text()
    for g in drop:
        s = re.sub(r'<g id="%s"[^>]*>.*?</g>\n' % g, "", s, flags=re.S)
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=w))).convert("RGBA")


def tile(im, label, sub="", bg=None, w=None):
    if w and im.width != w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    t = Image.new("RGBA", (im.width + 20, im.height + 70), CREAM + (255,))
    if bg:
        t.paste(Image.new("RGBA", im.size, bg + (255,)), (10, 10))
    t.alpha_composite(im, (10, 10))
    d = ImageDraw.Draw(t)
    d.text((10, im.height + 16), label, font=F, fill=INK)
    if sub:
        d.text((10, im.height + 44), sub, font=FS, fill=(90, 70, 100))
    return t


def row(tiles, gap=10):
    h = max(t.height for t in tiles); w = sum(t.width for t in tiles) + gap * (len(tiles) - 1)
    r = Image.new("RGBA", (w, h), CREAM + (255,)); x = 0
    for t in tiles:
        r.alpha_composite(t, (x, 0)); x += t.width + gap
    return r


m = lambda k: f"MAE {mae[k]['mae']}"
rows = []
rows.append(row([tile(svg("logo.svg", 1100), "logo.svg (layered)", m("logo (whole)") + "  stripe " + m("logo/racing_stripe")[4:] +
                      "  letters " + m("logo/letters")[4:] + "  moon " + m("logo/moon")[4:] + "  helmet " + m("logo/helmet_dot")[4:], bg=PLUM),
                 tile(svg("logo_mono_cream.svg", 700), "logo_mono_cream.svg", "one colour, cream", bg=PLUM)]))
arc = 560
rows.append(row([tile(svg("arcade.svg", arc), "arcade.svg", m("arcade (whole)")),
                 tile(svg("arcade.svg", arc, drop=("screen",)), "screen layer hidden", "CRT-off glass underneath"),
                 tile(svg("arcade_screen.svg", 420), "arcade_screen.svg", "screen " + m("arcade/screen")[4:] + ", controls " + m("arcade/controls")[4:], bg=PLUM),
                 tile(svg("arcade_marquee_blank.svg", 420), "arcade_marquee_blank.svg", "marquee " + m("arcade/marquee")[4:] + ", coin door " + m("arcade/coin_door")[4:], bg=PLUM)]))
poses = sorted((OUT / "poses").glob("pose_*.png"))
pt = []
for p in poses:
    im = Image.open(p).convert("RGBA"); im.thumbnail((300, 300))
    c = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); c.alpha_composite(im, ((300 - im.width) // 2, (300 - im.height) // 2))
    pt.append(tile(c, p.stem.replace("pose_", ""), "", bg=PLUM))
rows.append(row(pt[:5])); rows.append(row(pt[5:]))
sc = []
for name, label in (("27_screen_title_16x9_1920.webp", "27 title 16:9 crop"), ("28_screen_reveal_crew_1920.webp", "28 reveal crew"),
                    ("29_screen_reveal_impostor_1920.webp", "29 reveal impostor"), ("33_screen_win_crew_1920.webp", "33 win crew"),
                    ("34_screen_win_impostor_1920.webp", "34 win impostor")):
    im = Image.open(OUT / "screens" / name).convert("RGB")
    key = name.rsplit("_", 1)[0]
    meta = json.loads((OUT / "screens.json").read_text())["screens"].get(key.replace("_16x9", ""), {})
    if "podium_top" in meta:
        a = np.array(im)[..., ::-1].copy(); s = im.width / meta["size"][0]; pd = meta["podium_top"]; st = meta["stage_line"]
        cv2.ellipse(a, (round(pd["cx"] * s), round(pd["cy"] * s)), (round(pd["rx"] * s), round(pd["ry"] * s)), 0, 0, 360, (0, 255, 0), 4)
        cv2.line(a, (round(st["x0"] * s), round(st["y"] * s)), (round(st["x1"] * s), round(st["y"] * s)), (255, 255, 0), 4)
        im = Image.fromarray(a[..., ::-1]); label += " +podium"
    sc.append(tile(im.convert("RGBA"), label, "", w=360))
rows.append(row(sc))
rr = []
for n in ("30", "31"):
    r = svg(f"screens/{n}_rays.svg", 560)
    fg = Image.open(next((OUT / "screens").glob(f"{n}_*_fg_1920.webp"))).convert("RGBA").resize(r.size)
    rr.append(tile(r, f"{n}_rays.svg", "backing + spinnable #rays"))
    rr.append(tile(fg, f"{n} foreground webp", "goes over the rays", bg=(120, 120, 120)))
rows.append(row(rr))
W = max(r.width for r in rows) + 40
H = sum(r.height for r in rows) + 30 * len(rows) + 90
P = Image.new("RGBA", (W, H), CREAM + (255,))
d = ImageDraw.Draw(P)
d.text((20, 20), "JOB O: brand + screens (logo, HD arcade, screens pack, pose cutouts)", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34), fill=INK)
y = 80
for r in rows:
    P.alpha_composite(r, (20, y)); y += r.height + 30
P.convert("RGB").save(OUT / "PREVIEW.png", optimize=True)
print(P.size)
