"""Security desk: body (desk + monitor frames) + screens_off + screens_on layers."""
import json
from common import *
n = 'security_desk'
TR = dict(color_precision=8, layer_difference=1, filter_speckle=10, mode='spline')
q = prep(n, 14); mask = q[..., 3] > 0; rgb = q[..., :3].astype(int)
def is_(col): return (np.abs(rgb - np.array(col)).sum(-1) < 4) & mask
H, W = mask.shape
glass = (is_((84, 77, 103)) | is_((80, 54, 88)) | is_((113, 111, 132)) | is_((132, 128, 148))) & (np.arange(H)[:, None] < 470)
glass = ndi.binary_opening(ndi.binary_fill_holes(glass), iterations=3)
lab, k = ndi.label(glass); sizes = ndi.sum(glass, lab, range(1, k + 1))
glass = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 5000])
print('screens found', (sizes > 5000).sum())
body = q.copy(); body[glass] = (84, 77, 103, 255)
body_p = '\n'.join(paths_of(trace(body, **TR)))
off = q.copy(); off[~glass] = 0
off_p = '\n'.join(paths_of(trace(off, **TR)))
# screens on: on-sprite is 4 px lower; align then quantize only the glass interior
on_raw = crop('security_desk_on')[4:4 + H]
_, on_clean = key(on_raw)
on_clean = np.stack([ndi.median_filter(on_clean[..., i], 5) for i in range(3)], -1)
gl2 = ndi.binary_dilation(glass, iterations=4)
qo, _ = quantize(on_clean, gl2, 9, smooth=2)
on_p = '\n'.join(paths_of(trace(qo, **TR)))
gm = np.where(glass[..., None], np.array([0, 0, 0, 255], np.uint8), np.array([255, 255, 255, 0], np.uint8)).astype(np.uint8)
clip = ''.join(paths_of(trace(gm, colormode='binary', filter_speckle=10, mode='spline')))
defs = (f'<clipPath id="deskGlass">{clip}</clipPath>'
        '<filter id="deskSoft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2.5"/></filter>')
inner = (group('body', body_p) + '\n' + group('screens_off', off_p) + '\n'
         + group('screens_on', f'<g clip-path="url(#deskGlass)"><g filter="url(#deskSoft)">\n{on_p}\n</g></g>'))
svg = wrap(n, inner, defs)
open(f'{n}_orig.svg', 'w').write(svg)
svg_off = svg.replace('<g id="screens_on">', '<g id="screens_on" display="none">')
res = json.load(open('src/mae.json'))
res[n + ' (screens off)'] = round(checks(n, svg_off, tag=n + '_off'), 2)
res[n + ' (screens on)'] = round(checks(n, svg, orig=on_raw, tag=n + '_on'), 2)
json.dump(res, open('src/mae.json', 'w'), indent=1)
print(res, len(svg) // 1024, 'KB')
