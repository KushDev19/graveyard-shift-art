"""Assemble hall_preview.png from the rendered half-scale hall PNGs: tiling + corner joins
(including horizontally mirrored corners) and a same-scale crop of the Galley for comparison."""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[2]
HALL = ROOT / "frontend/public/assets/ship/hall"
GALLEY = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
BG = (27, 24, 48, 255)


def load(n):
    return Image.open(HALL / f"{n}.png").convert("RGBA")


def main():
    h, v, ru, rd = load("hall_h"), load("hall_v"), load("hall_corner_ru"), load("hall_corner_rd")
    lu, ld = ImageOps.mirror(ru), ImageOps.mirror(rd)
    hw, hh = h.size
    vw, vh = v.size
    cw, ch = ru.size
    vx_m = cw - vw                      # x of hall_v column inside a mirrored corner
    gap = 120
    W = max(3 * hw, 2 * cw + hw)
    yA = 0
    yB = yA + hh + gap                  # hall_v x3 above ru / x1 above lu
    yR = yB + 3 * vh                    # ru row
    yD = yR + ch + gap                  # rd row
    yG = yD + ch + 3 * vh + gap         # galley comparison
    gal = None
    if GALLEY:
        g = Image.open(GALLEY).convert("RGBA")
        gal = g.crop((1400, 0, 3400, 2900)).resize((1000, 1450), Image.LANCZOS)
    H = yG + (max(gal.height, hh) if gal else hh) + 40
    out = Image.new("RGBA", (W, H), BG)
    for i in range(3):
        out.alpha_composite(h, (i * hw, yA))
    for i in range(3):
        out.alpha_composite(v, (0, yB + i * vh))
    out.alpha_composite(v, (cw + hw + vx_m, yB + 2 * vh))
    out.alpha_composite(ru, (0, yR))
    out.alpha_composite(h, (cw, yR + (ch - hh)))
    out.alpha_composite(lu, (cw + hw, yR))
    out.alpha_composite(rd, (0, yD))
    out.alpha_composite(h, (cw, yD))
    out.alpha_composite(ld, (cw + hw, yD))
    for i in range(3):
        out.alpha_composite(v, (0, yD + ch + i * vh))
    out.alpha_composite(v, (cw + hw + vx_m, yD + ch))
    if gal:
        out.alpha_composite(gal, (0, yG))
        out.alpha_composite(h, (gal.width + 40, yG))
        d = ImageDraw.Draw(out)
        d.text((10, yG + gal.height + 8), "Galley (half scale)", fill=(244, 230, 200, 255))
        d.text((gal.width + 50, yG + hh + 8), "hall_h (half scale)", fill=(244, 230, 200, 255))
    out.convert("RGB").save(ROOT / "art/work/hall_preview.png", optimize=True)
    print(out.size)


if __name__ == "__main__":
    main()
