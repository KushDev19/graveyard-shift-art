import { A } from './util.js';

const MAP = A('town/covey_map.webp'), ARC = A('town/arcade_32x64.png');
const load = (src) => new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.src = src; });

/** The REAL Covey.Town map (indoors.json rendered by tools/render_covey_map.py): a 960x540 crop of the
 *  museum hall, shown at 2x. Our arcade cabinet stands on its open floor. Arcade feet are at canvas (370, 350). */
export const ARCADE = { x: 370, y: 350, stageX: 740, stageY: 700 };
export async function paintTown() {
  const [map, arc] = await Promise.all([load(MAP), load(ARC)]);
  const c = document.createElement('canvas'); c.width = 960; c.height = 540; const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
  g.drawImage(map, 1480, 760, 960, 540, 0, 0, 960, 540);
  g.drawImage(arc, 0, 0, 32, 64, ARCADE.x - 16, ARCADE.y - 64, 32, 64);
  return c;
}

/** real Covey.Town "misa" avatar atlas frame rects (atlas.json of the class repo) */
export async function loadMisa() { return (await fetch(A('town/misa.json'))).json(); }

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
