import gsap from 'gsap';
import { ROSTER, P } from '../core/util.js';
import { Puppet } from '../core/puppet.js';

export const K = 0.24;
export const mk = (id, o = {}) => new Puppet({ color: P[id].color, name: P[id].name, cos: P[id].cos, impostor: !!o.impostorVisor, k: o.k ?? K, ...o });

/** spawn a roster subset into a room at given stage positions */
export function spawn(room, spec, o = {}) {
  const out = {};
  for (const [id, pos] of Object.entries(spec)) { const p = mk(id, o); room.add(p, pos[0], pos[1]); if (pos[2] === -1) p.setFacing(-1); out[id] = p; }
  return out;
}
/** squash-and-pop teleport used by meetings */
export function teleport(p, x, y, { at = 0, face = null } = {}) {
  const tl = gsap.timeline();
  tl.to(p.root, { scaleX: 0.2, scaleY: 1.5, opacity: 0, duration: 0.16, ease: 'power2.in' }, at)
    .call(() => { p.place(x, y); p.setMode('idle'); p.setFacing(face ?? (x > 960 ? -1 : 1)); if (face === 0) p.setFacing(1); }, null, at + 0.16)
    .fromTo(p.root, { scaleX: 1.6, scaleY: 0.3, opacity: 0 }, { scaleX: 1, scaleY: 1, opacity: 1, duration: 0.42, ease: 'elastic.out(1,0.45)' }, at + 0.16);
  return tl;
}
export const seatsOf = (room) => room.man.anchors.seats.map((s) => room.pt(s));
export const SEAT_ORDER = { tangerine: 0, mustard: 1, lime: 2, sky: 3, cobalt: 4, grape: 5, mint: 6, bubblegum: 7, cream: 8 };
export const nameOf = (id) => P[id].name;

export function poof(room, x, y) { // little star burst at x,y
  const d = document.createElement('div'); d.className = 'poof'; d.style.left = x + 'px'; d.style.top = y + 'px'; d.innerHTML = '★★★'; room.fx.appendChild(d);
  return gsap.timeline({ onComplete: () => d.remove() }).fromTo(d, { scale: 0.3, autoAlpha: 1, y: 0 }, { scale: 1.6, autoAlpha: 0, y: -90, duration: 0.8, ease: 'power2.out' });
}
