import gsap from 'gsap';
import { A, el, img } from './util.js';

const cache = {};
export async function loadManifest(key) { return (cache[key] ??= await fetch(A(`rooms/${key}.json`)).then((r) => r.json())); }

/** A room = painted composite (webp) + scripted actors + a few SVG occluders. Coordinates in manifest are source px. */
export class Room {
  constructor(parent, key, man) {
    this.key = key; this.man = man; this.s = 1920 / man.size[0]; this.oy = (1080 - man.size[1] * this.s) / 2;
    this.el = el('div', 'room', parent);
    this.bg = img(A(`rooms/${key}.webp`), 'room-bg', this.el);
    this.sorted = el('div', 'room-sorted', this.el);   // actors + occluders, z by sortY
    this.fx = el('div', 'room-fx', this.el);
    this.actors = [];
  }
  static async create(parent, key) { return new Room(parent, key, await loadManifest(key)); }
  pt([x, y]) { return [x * this.s, y * this.s + this.oy]; }
  anchor(name, i = null) { const a = this.man.anchors[name]; return this.pt(i == null ? a : a[i]); }
  /** place an svg/png object using source px; sortY puts it in the actor depth order. */
  obj(file, x, y, w, h, { sortY = null, cls = '', parent = null } = {}) {
    const i = img(A(file), 'room-obj ' + cls, parent || this.sorted);
    const [px, py] = this.pt([x, y]);
    Object.assign(i.style, { left: px + 'px', top: py + 'px', width: w * this.s + 'px', height: h * this.s + 'px' });
    if (sortY != null) i.style.zIndex = Math.round(sortY * this.s + this.oy);
    return i;
  }
  add(p, x, y) { p.attach(this.sorted).place(x, y); this.actors.push(p); return p; }
  remove(p) { p.root.remove(); this.actors = this.actors.filter((a) => a !== p); }
  floorBounds() { // handy default walk area in stage px
    return { x0: 280, x1: 1640, y0: 540, y1: 960 };
  }
}
