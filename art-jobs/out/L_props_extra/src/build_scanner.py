"""Med scanner pod: base (repainted under the arch) + arch_back + scan_ring + arch_front (left pillar)."""
import json
from scanner_masks import *
TR = dict(color_precision=8, layer_difference=1, filter_speckle=10, mode='spline')
img, sil = model()
hid = ndi.binary_dilation(arch, iterations=3)
base = q.copy()
base[hid] = 0
base[~ndi.binary_dilation(sil, iterations=6)] = 0
fill = hid & sil
base[fill, :3] = img[fill]; base[fill, 3] = 255
base_p = '\n'.join(paths_of(trace(base, **TR)))
arch_img = q.copy(); arch_img[~arch] = 0
arch_p = '\n'.join(paths_of(trace(arch_img, **TR)))
xx = np.arange(W)[None, :]; yy = np.arange(H)[:, None]
front = arch & (xx < 360) & (yy > 330)
fr_img = q.copy(); fr_img[~front] = 0
front_p = '\n'.join(paths_of(trace(fr_img, **TR)))

# scan ring from the active sprite, shifted +2 px in x into idle coordinates
act = crop('med_scanner_active'); act = np.pad(act, ((0, H - act.shape[0]), (0, W - act.shape[1]), (0, 0)), mode='edge'); act = np.roll(act, 2, axis=1)
al, clean = key(act)
clean = np.stack([ndi.median_filter(clean[..., i], 5) for i in range(3)], -1)
c = np.stack([ndi.median_filter(act[..., i], 5) for i in range(3)], -1).astype(int)
idle_s = np.stack([ndi.median_filter(crop('med_scanner')[..., i], 5) for i in range(3)], -1).astype(int)
diff = np.abs(c - idle_s).sum(-1)
ringcore = (diff > 60) & (c[..., 1] - c[..., 0] > 50) & (c[..., 1] - c[..., 2] > 8) & (yy > 150)
ringcore &= (c[..., 0] < 170) & (c[..., 2] < 225)
ringcore = ndi.binary_opening(ringcore, iterations=5)
lab, k = ndi.label(ringcore); sz = ndi.sum(ringcore, lab, range(1, k + 1))
ringcore = np.isin(lab, [i + 1 for i, s_ in enumerate(sz) if s_ > 1500])
dark = (c.sum(-1) < 330) & (al > 0.5) & (diff > 40)
ringm = ringcore | (ndi.binary_dilation(ringcore, iterations=12) & dark & ~(front & (diff < 40)))
ringm = ndi.binary_closing(ringm, iterations=2) & ~(front & (diff < 60))
# extend the cut ends under the left pillar so the ring can move without showing gaps
fr_d = ndi.binary_dilation(front, iterations=4)
for y in range(H):
    xs = np.where(ringm[y] & ~fr_d[y])[0]
    if len(xs) and fr_d[y, max(xs.min() - 6, 0)]:
        x0 = xs.min(); ext = slice(max(x0 - 60, 0), x0)
        ringm[y, ext] = True; clean[y, ext] = clean[y, x0 + 2]
rq, _ = quantize(clean, ringm, 6, smooth=2)
ring_p = '\n'.join(paths_of(trace(rq, **TR)))
cy_ring = int(np.where(ringm.any(1))[0].mean()); cx_ring = int(np.where(ringm.any(0))[0].mean())
defs = ('<filter id="ringGlow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="12"/></filter>'
        '<radialGradient id="scanLight"><stop offset="0" stop-color="#C8F5D6" stop-opacity="0.45"/>'
        '<stop offset="0.75" stop-color="#C8F5D6" stop-opacity="0.3"/><stop offset="1" stop-color="#C8F5D6" stop-opacity="0"/></radialGradient>')
e_cx, e_cy, e_a, e_b = e_ring_in
ring_g = (f'<ellipse id="scan_light" cx="{e_cx:.0f}" cy="{e_cy - 10:.0f}" rx="{e_a + 30:.0f}" ry="{e_b + 20:.0f}" fill="url(#scanLight)"/>\n'
          f'<g id="scan_ring_glow" filter="url(#ringGlow)" opacity="0.7">{ring_p}</g>\n<g id="scan_ring_core">{ring_p}</g>')
inner = (group('base', base_p) + '\n' + group('arch_back', arch_p) + '\n'
         + group('scan_ring', ring_g, f'data-pivot="{cx_ring},{cy_ring}"') + '\n' + group('arch_front', front_p))
svg = wrap('med_scanner', inner, defs)
open('med_scanner_orig.svg', 'w').write(svg)
idle = svg.replace('<g id="scan_ring"', '<g id="scan_ring" display="none"')
res = json.load(open('src/mae.json'))
res['med_scanner (idle)'] = round(checks('med_scanner', idle, tag='med_scanner_idle'), 2)
res['med_scanner (scanning)'] = round(checks('med_scanner', svg, orig=act[:H, :W], tag='med_scanner_scanning'), 2)
json.dump(res, open('src/mae.json', 'w'), indent=1)
print({k_: v for k_, v in res.items() if 'med' in k_}, len(svg) // 1024, 'KB')
base_only = '<svg' + svg.split('<svg', 1)[1].split('<g id="arch_back"')[0] + '</svg>'
Image.fromarray(render(base_only, W // 2, H // 2)).save('/tmp/claude-0/base.png')
if __name__ == '__main__' and 'dbg' in __import__('sys').argv:
    v = np.zeros((H, W, 3), np.uint8); v[ringm] = (90, 90, 90); v[ringcore] = (0, 255, 0); v[ringm & ~ringcore & dark] = (255, 0, 255)
    Image.fromarray(np.hstack([v, rq[..., :3]])[150:520]).resize((1036, 185)).save('/tmp/claude-0/v.png')
