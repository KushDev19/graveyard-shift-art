import { A } from './util.js';

const TS = A('town/tileset.png'), ARC = A('town/arcade_32x64.png');
const load = (src) => new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.src = src; });
const R = { // crops in the extruded tileset (px)
  grass: [194, 178, 32, 32], sand: [434, 184, 32, 32],
  clinic: [478, 512, 166, 134], shop: [646, 512, 169, 134], dark: [308, 512, 166, 134],
  cab1: [306, 655, 168, 125], cab2: [476, 655, 170, 125], cab3: [648, 655, 168, 125], brick: [172, 826, 200, 124], red: [376, 826, 168, 124],
  fountain: [272, 375, 102, 94], tree: [376, 372, 64, 68], stump: [444, 374, 96, 66], statue: [543, 410, 70, 68],
  sign: [613, 476, 36, 34], sign2: [684, 476, 40, 34], lamp: [652, 466, 28, 44],
};

/** paint a Covey.Town-style (Tuxmon tileset) street scene onto a 960x540 canvas */
export async function paintTown() {
  const [ts, arc] = await Promise.all([load(TS), load(ARC)]);
  const c = document.createElement('canvas'); c.width = 960; c.height = 540; const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
  const d = (k, x, y, s = 1) => { const r = R[k]; g.drawImage(ts, r[0], r[1], r[2], r[3], Math.round(x), Math.round(y), r[2] * s, r[3] * s); };
  for (let y = 0; y < 540; y += 32) for (let x = 0; x < 960; x += 32) d('grass', x, y);
  // flowers (small tufts from the sheet top-left)
  for (let i = 0; i < 22; i++) { const x = (i * 197) % 920, y = 200 + ((i * 131) % 300); g.drawImage(ts, 4, 172, 28, 26, x, y, 28, 26); }
  for (let x = 0; x < 960; x += 32) { d('sand', x, 330); d('sand', x, 362); }
  for (let y = 250; y < 540; y += 32) { d('sand', 640, y); d('sand', 672, y); }
  d('clinic', 24, 52); d('cab2', 214, 60); d('dark', 408, 52); d('shop', 590, 52); d('brick', 770, 52);
  d('fountain', 330, 214); d('tree', 150, 214); d('tree', 24, 230); d('tree', 880, 220); d('tree', 790, 232); d('statue', 500, 224); d('sign', 600, 300); d('sign2', 100, 300); d('lamp', 596, 214); d('lamp', 780, 296); d('stump', 56, 410); d('tree', 140, 408); d('tree', 860, 440);
  // arcade cabinet: 32x64 sprite at 2x
  g.drawImage(arc, 0, 0, 32, 64, 700, 224, 96, 192);
  return c;
}

/** tiny procedural pixel avatar (16x24 frames: idle, walk A, idle, walk B), facing right */
export function avatarSheet(shirt = '#6FD6B0', hair = '#3a2a24', skin = '#f0c49a') {
  const c = document.createElement('canvas'); c.width = 64; c.height = 24; const g = c.getContext('2d');
  const f = (i, col, x, y, w, h) => { g.fillStyle = col; g.fillRect(i * 16 + x, y, w, h); };
  for (let i = 0; i < 4; i++) {
    const step = i === 1 ? -1 : i === 3 ? 1 : 0;
    f(i, '#2A1E35', 4, 1, 8, 9); f(i, hair, 5, 1, 7, 4); f(i, skin, 5, 4, 7, 6); f(i, '#2A1E35', 9, 6, 1, 2); // head + eye
    f(i, '#2A1E35', 3, 10, 10, 8); f(i, shirt, 4, 10, 8, 7); f(i, skin, 2 + step, 11, 2, 5); f(i, skin, 12 - step, 11, 2, 5);
    f(i, '#2A1E35', 4, 17, 8, 5); f(i, '#35406b', 5 + step, 17, 3, 4); f(i, '#35406b', 8 - step, 17, 3, 4); f(i, '#2A1E35', 5 + step, 21, 3, 1); f(i, '#2A1E35', 8 - step, 21, 3, 1);
  }
  return c.toDataURL();
}
