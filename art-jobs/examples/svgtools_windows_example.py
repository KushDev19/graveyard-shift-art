"""Render helpers for the SVG art: build part/pose variants from a master SVG and rasterize
them with headless Edge. Transparent output uses black/white difference matting, so it does
not depend on the browser supporting a transparent screenshot background."""
import pathlib
import subprocess
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = ROOT / "art/work"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def variant(master, show, rot=None, move=None, whole=None, style=""):
    """Return SVG text containing only the groups in `show` (in that z-order).
    Items in `show` starting with '<' are raw SVG snippets inserted at that position.
    rot: {id: degrees} around the group's data-pivot. move: {id: transform}. whole: transform for all."""
    svg = ET.parse(master).getroot()
    crew = svg.find(f".//{{{NS}}}g[@id='crew']")
    kids = {g.get("id"): g for g in list(crew)}
    for g in list(crew):
        crew.remove(g)
    for gid in show:
        if gid.startswith("<"):
            crew.append(ET.fromstring(f'<g xmlns="{NS}">{gid}</g>'))
            continue
        g = kids[gid]
        g.attrib.pop("display", None)
        t = []
        if move and gid in move:
            t.append(move[gid])
        if rot and gid in rot:
            px, py = g.get("data-pivot").split(",")
            t.append(f"rotate({rot[gid]} {px} {py})")
        if g.get("transform"):
            t.append(g.get("transform"))
        if t:
            g.set("transform", " ".join(t))
        crew.append(g)
    if whole:
        crew.set("transform", whole)
    if style:
        svg.set("style", style)
    return ET.tostring(svg, encoding="unicode")


def screenshot(svgs, cols, cw, ch, bg, scale=1, labels=None, out=None):
    rows = (len(svgs) + cols - 1) // cols
    lab_h = 22 if labels else 0
    cells = "".join(
        f'<div class="c">{s}{f"<div class=l>{labels[i]}</div>" if labels else ""}</div>'
        for i, s in enumerate(svgs))
    html = f"""<!doctype html><meta charset="utf-8"><style>
      html,body{{margin:0;background:{bg};font:14px sans-serif;color:#2A1E35}}
      .g{{display:grid;grid-template-columns:repeat({cols},{cw}px)}}
      .c{{width:{cw}px;height:{ch + lab_h}px}} .c svg{{width:{cw}px;height:{ch}px;display:block}}
      .l{{height:{lab_h}px;text-align:center}}</style><div class="g">{cells}</div>"""
    page = WORK / "_render.html"
    page.write_text(html, encoding="utf-8")
    png = out or (WORK / "_render.png")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={scale}", f"--screenshot={png}",
                    f"--window-size={cols * cw},{rows * (ch + lab_h)}", page.as_uri()],
                   check=True, timeout=180, capture_output=True)
    return Image.open(png).convert("RGB")


def render_rgba(svgs, cols, cw, ch, scale=1):
    """Render on black and on white; recover true colors + alpha from the difference."""
    b = np.asarray(screenshot(svgs, cols, cw, ch, "#000", scale)).astype(np.float32)
    w = np.asarray(screenshot(svgs, cols, cw, ch, "#fff", scale)).astype(np.float32)
    a = np.clip(1 - (w - b).mean(axis=2) / 255, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, b / np.maximum(a[..., None], 1e-3), 0)
    rgba = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def cells(img, n, cols, cw, ch, scale=1):
    for i in range(n):
        r, c = divmod(i, cols)
        x, y = c * cw * scale, r * ch * scale
        yield img.crop((x, y, x + cw * scale, y + ch * scale))


def trim(cell, pad=4):
    box = cell.split()[3].point(lambda v: 255 if v > 2 else 0).getbbox()
    if not box:
        return None, None
    x0, y0 = max(box[0] - pad, 0), max(box[1] - pad, 0)
    x1, y1 = min(box[2] + pad, cell.width), min(box[3] + pad, cell.height)
    return cell.crop((x0, y0, x1, y1)), (x0, y0, x1, y1)


def pack(images, max_w=2048, gap=4):
    """Simple shelf packer. images: {name: Image}. Returns (atlas, {name: (x, y, w, h)})."""
    order = sorted(images, key=lambda k: -images[k].height)
    x = y = shelf = 0
    pos = {}
    for k in order:
        im = images[k]
        if x + im.width > max_w:
            x, y, shelf = 0, y + shelf + gap, 0
        pos[k] = (x, y, im.width, im.height)
        x += im.width + gap
        shelf = max(shelf, im.height)
    atlas = Image.new("RGBA", (max_w, y + shelf), (0, 0, 0, 0))
    for k, (px, py, _, _) in pos.items():
        atlas.paste(images[k], (px, py))
    return atlas, pos


def contact_sheet(named, out, bg=(244, 230, 200), cell=300, cols=6):
    """Preview: every image scaled into a labeled cell on a cream background."""
    from PIL import ImageDraw
    rows = (len(named) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 24)), bg)
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(named.items()):
        r, c = divmod(i, cols)
        t = im.copy()
        t.thumbnail((cell - 16, cell - 16))
        ox = c * cell + (cell - t.width) // 2
        oy = r * (cell + 24) + (cell - t.height) // 2
        sheet.paste(t, (ox, oy), t)
        d.text((c * cell + 8, r * (cell + 24) + cell + 4), name, fill=(42, 30, 53))
    sheet.save(out)
