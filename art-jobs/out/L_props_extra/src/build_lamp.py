"""Floor lamp: unlit body + separate glow layer (bulb + shade light + optional halo)."""
import json
from common import *
n = 'floor_lamp'
c = crop(n); al, clean = key(c); mask = ndi.binary_opening(al > 0.5)
clean = np.stack([ndi.median_filter(clean[..., i], 5) for i in range(3)], -1)
q, cent = quantize(clean, mask, 12, smooth=2, extra=[(123, 55, 81)])
rgb = q[..., :3].astype(int)
def is_(col): return (np.abs(rgb - np.array(col)).sum(-1) < 4) & mask
H = q.shape[0]; top = np.arange(H)[:, None] < 380
RIM, MID, CEN, BULB, DIM = (239, 160, 101), (249, 172, 105), (251, 189, 113), (253, 242, 186), (214, 140, 106)
mid, cen, bulb = is_(MID) & top, is_(CEN) & top, is_(BULB)
shade = ndi.binary_fill_holes(is_(RIM) | mid | cen) & top & ~ndi.binary_dilation(bulb | is_(DIM) | is_((143, 77, 82)), iterations=2)
body = q.copy()
body[(mid | cen) & shade] = RIM + (255,)
body[bulb] = DIM + (255,)
TR = dict(color_precision=8, layer_difference=1, filter_speckle=10, mode='spline')
body_paths = '\n'.join(paths_of(trace(body, **TR)))
# glow pieces
def binpaths(m, fill):
    im = np.where(m[..., None], np.array([0, 0, 0, 255], np.uint8), np.array([255, 255, 255, 0], np.uint8))
    s = trace(im.astype(np.uint8), colormode='binary', filter_speckle=10, mode='spline')
    return '\n'.join(p.replace('fill="#000000"', f'fill="{fill}"') for p in paths_of(s))
bulb_paths = binpaths(ndi.binary_opening(bulb, iterations=2), '#FDF2BA')
clip_paths = binpaths(shade, '#000')
mid_p = binpaths(ndi.binary_opening(mid | cen, iterations=2), '#F9AC69')
cen_p = binpaths(ndi.binary_opening(cen, iterations=2), '#FBBD71')
defs = (f'<clipPath id="lampShadeClip">{clip_paths.replace(chr(10), "")}</clipPath>'
        '<filter id="lampSoft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>'
        '<filter id="lampBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>'
        '<radialGradient id="lampHalo"><stop offset="0" stop-color="#FFD98A" stop-opacity="0.55"/>'
        '<stop offset="1" stop-color="#FFD98A" stop-opacity="0"/></radialGradient>')
w = q.shape[1]
glow = (f'<g id="glow_shade" clip-path="url(#lampShadeClip)"><g filter="url(#lampSoft)">{mid_p}\n{cen_p}</g></g>\n'
        f'<g id="glow_bulb">{bulb_paths}\n<g filter="url(#lampBlur)" opacity="0.6">{bulb_paths}</g></g>\n'
        f'<ellipse id="glow_halo" display="none" cx="{w / 2:.0f}" cy="200" rx="{w * 0.9:.0f}" ry="330" fill="url(#lampHalo)"/>')
svg = wrap(n, group('body', body_paths) + '\n' + group('glow', glow), defs)
open(f'{n}_orig.svg', 'w').write(svg)
res = json.load(open('src/mae.json')); res[n] = round(checks(n, svg), 2); json.dump(res, open('src/mae.json', 'w'), indent=1)
print(n, res[n], len(svg) // 1024, 'KB')
off = svg.replace('<g id="glow">', '<g id="glow" display="none">')
Image.fromarray(np.hstack([c[:420], render(svg, w, H)[:420, :, :3], render(off, w, H)[:420, :, :3]])).save('/tmp/claude-0/v.png')
