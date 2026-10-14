"""Render an SVG at source size, composite over the source crop, save side-by-side + onion, return MAE."""
import io, numpy as np, cairosvg, cv2
from PIL import Image
from kcommon import mae

def render_rgba(svg_text, w, h):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=w, output_height=h)
    return np.array(Image.open(io.BytesIO(png)).convert('RGBA')).astype(np.float32)

def check(svg_text, src_crop, region, name, outdir, label=''):
    h, w = src_crop.shape[:2]
    r = render_rgba(svg_text, w, h)
    a = r[..., 3:4] / 255
    comp = r[..., :3] * a + src_crop.astype(np.float32) * (1 - a)
    reg = cv2.dilate(region.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    score = mae(comp, src_crop, reg)
    sbs = np.hstack([src_crop, comp.astype(np.uint8)])
    onion = (0.5 * comp + 0.5 * src_crop).astype(np.uint8)
    s = 900 / max(sbs.shape[1], 1)
    Image.fromarray(sbs).resize((900, int(sbs.shape[0] * s))).save(f'{outdir}/{name}_side_by_side.png')
    s2 = 700 / w
    Image.fromarray(onion).resize((700, int(h * s2))).save(f'{outdir}/{name}_onion.png')
    return score
