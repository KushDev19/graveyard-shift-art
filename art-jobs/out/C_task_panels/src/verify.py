"""Render SVG -> PNG, then build debug overlays (socket rects from panels.json drawn on each panel),
assembled previews (parts placed by panels.json) and PREVIEW.png.
Usage: python art-jobs/out/C_task_panels/src/verify.py"""
import io
import json
import pathlib

import cairosvg
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(__file__).resolve().parent.parent
PARTS = OUT / "task_parts"
DBG = OUT / "debug"


def render(svg, png, scale=1):
    cairosvg.svg2png(url=str(svg), write_to=str(png), scale=scale)


def load(svg, scale=1):
    return Image.open(io.BytesIO(cairosvg.svg2png(url=str(svg), scale=scale))).convert("RGBA")


def main():
    doc = json.loads((OUT / "panels.json").read_text())
    DBG.mkdir(exist_ok=True)
    for svg in sorted(PARTS.glob("*.svg")):
        render(svg, svg.with_suffix(".png"), 2)          # parts: 2x of panel scale
    for name in doc["panels"]:
        render(OUT / f"{name}.svg", OUT / f"{name}.png")  # panels: native 2048x1536
    for name, p in doc["panels"].items():
        base = Image.open(OUT / f"{name}.png").convert("RGBA")
        # debug overlay: socket rects straight from panels.json
        dbg = base.copy(); d = ImageDraw.Draw(dbg)
        for sid, s in p["sockets"].items():
            x, y, w, h = s["x"], s["y"], s["w"], s["h"]
            if s["kind"] == "needle":
                px, py = s["pivot"]
                d.line([px, py, px, py - h], fill=(255, 0, 255, 255), width=5)
                d.ellipse([px - 10, py - 10, px + 10, py + 10], outline=(255, 0, 255, 255), width=4)
            elif s["kind"] in ("jack", "lamp", "reel", "button"):
                d.ellipse([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline=(255, 0, 255, 255), width=5)
                d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline=(0, 255, 0, 255), width=3)
            else:
                d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline=(255, 0, 255, 255), width=5)
            d.line([x - 14, y, x + 14, y], fill=(0, 255, 0, 255), width=3)
            d.line([x, y - 14, x, y + 14], fill=(0, 255, 0, 255), width=3)
        dbg.save(DBG / f"{name}_debug.png")
        # assembled: place parts exactly as a game would
        asm = base.copy()
        demo = {"key_3": "key_pressed", "key_6": "key_correct", "key_8": "key_wrong",
                "lamp_out_1": "lamp_lit_yellow", "lamp_in_3": "lamp_lit_yellow"}
        for sid, s in p["sockets"].items():
            part = demo.get(sid, s.get("part"))
            if sid == "jack_out_1":  # patched in the demo, plug drawn at its target below
                continue
            if not part or part not in doc["parts"] or (sid.startswith("lamp") and sid not in demo and name == "panel_switchboard"):
                continue
            info = doc["parts"][part]
            sc = s.get("scale", 1.0)
            img = load(PARTS / f"{part}.svg", sc)
            ax, ay = info["anchor"]
            asm.alpha_composite(img, (round(s["x"] - ax * sc), round(s["y"] - ay * sc)))
        if name == "panel_switchboard":  # one patched cable: yellow out_1 -> in_3
            a, b = p["sockets"]["jack_out_1"], p["sockets"]["jack_in_3"]
            d = ImageDraw.Draw(asm)
            pts = [(a["x"] + t / 40 * (b["x"] - 40 - a["x"]),
                    a["y"] + t / 40 * (b["y"] - a["y"]) + 120 * (1 - (2 * t / 40 - 1) ** 2)) for t in range(41)]
            d.line(pts, fill=(42, 30, 53, 255), width=50, joint="curve")
            d.line(pts, fill=(233, 192, 70, 255), width=34, joint="curve")
            info = doc["parts"]["plug_yellow"]; img = load(PARTS / "plug_yellow.svg")
            asm.alpha_composite(img, (round(b["x"] - info["anchor"][0]), round(b["y"] - info["anchor"][1])))
            ring = load(PARTS / "jack_ring.svg")
            asm.alpha_composite(ring, (round(b["x"] - 90), round(b["y"] - 90)))
        asm.save(DBG / f"{name}_assembled.png")
    # PREVIEW: three panels assembled + parts row, labels on cream
    cw = 900; ch = cw * 3 // 4
    sheet = Image.new("RGBA", (3 * cw + 160, ch + 760), "#F4E6C8")
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30); small = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        font = small = ImageFont.load_default()
    for i, name in enumerate(doc["panels"]):
        im = Image.open(DBG / f"{name}_assembled.png").resize((cw, ch), Image.LANCZOS)
        sheet.alpha_composite(im, (40 + i * (cw + 40), 70))
        dr.text((40 + i * (cw + 40), 22), f"{name}  (assembled from panels.json)", fill="#2A1E35", font=font)
    x, y, rowh = 40, ch + 140, 0
    dr.text((40, ch + 92), "task_parts", fill="#2A1E35", font=font)
    for svg in sorted(PARTS.glob("*.svg")):
        im = load(svg, 0.6)
        if x + max(im.width, 150) > sheet.width - 40:
            x, y, rowh = 40, y + rowh + 50, 0
        sheet.alpha_composite(im, (x, y))
        dr.text((x, y + im.height + 6), svg.stem, fill="#2A1E35", font=small)
        x += max(im.width, 150) + 30; rowh = max(rowh, im.height)
    sheet = sheet.crop((0, 0, sheet.width, min(sheet.height, y + rowh + 50)))
    sheet.convert("RGB").save(OUT / "PREVIEW.png")
    print("ok")


if __name__ == "__main__":
    main()
