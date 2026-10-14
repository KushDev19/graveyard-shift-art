import sys, json, numpy as np, cv2
from PIL import Image
sys.path.insert(0, '.')
import seg, rooms

def build(room, out):
    full = Image.open('../../../../' + room['source']).convert('RGB')
    W, H = full.size
    img = np.asarray(full.resize((W // 2, H // 2), Image.LANCZOS))
    h, w = img.shape[:2]
    warm = seg.warm(img)
    vv = seg.hsv(img)[2]
    claimed = np.zeros((h, w), bool)
    masks = {}
    for p in room['pieces']:
        R = seg.raster(p['shapes'], h, w)
        if p['mode'] == 'gc':
            m = seg.grabcut(img, R, sure=p.get('sure', 6))
        elif p['mode'] == 'warm':
            m = R & warm
        elif p['mode'] == 'warmgc':
            m = seg.grabcut_init(img, R, R & warm)
        elif p['mode'] == 'cablegc':
            m = seg.grabcut_init(img, R, R & (warm | (vv < 0.35)))
        elif p['mode'] == 'cable':
            m = R & (warm | (vv < 0.33))
        elif p['mode'] == 'steam':
            m = seg.steam(img, R)
        else:
            m = R
        m = seg.clean(m & ~claimed, p.get('close', 2), p.get('min_area', 60)) & ~claimed
        # complete the dark plum outline the colour/GrabCut step tends to leave on the wall
        ring = cv2.dilate(m.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
        m = (m | (ring & (vv < 0.3) & ~claimed)) if p.get('kind') != 'steam' else m
        masks[p['id']] = m
        claimed |= m
    np.savez_compressed(out, **masks)
    return img, masks

if __name__ == '__main__':
    room = getattr(rooms, sys.argv[1])
    img, masks = build(room, sys.argv[2])
    vis = img.astype(float) * 0.35
    rng = np.random.default_rng(3)
    for k, m in masks.items():
        c = rng.integers(60, 255, 3)
        vis[m] = img[m] * 0.45 + c * 0.55
    Image.fromarray(vis.astype(np.uint8)).resize((1600, int(1600 * img.shape[0] / img.shape[1]))).save(sys.argv[3])
