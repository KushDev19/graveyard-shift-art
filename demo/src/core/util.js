import gsap from 'gsap';

export const A = (p) => `${import.meta.env.BASE_URL}assets/${p}`.replace('//', '/');

export function el(tag, cls = '', parent = null, html = '') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html) e.innerHTML = html;
  if (parent) parent.appendChild(e);
  return e;
}
export const img = (src, cls = '', parent = null) => { const i = el('img', cls, parent); i.src = src; i.draggable = false; return i; };

export const COLORS = {
  tomato: '#E4483C', tangerine: '#F28A2E', mustard: '#E9C046', lime: '#A6D64A', mint: '#6FD6B0',
  sky: '#6EC3F0', cobalt: '#3F5FD9', grape: '#8E5AC8', bubblegum: '#F07BB5', cream: '#F4E6C8',
};
export const PAL = { indigo: '#1B1830', plum: '#3D2A4F', outline: '#2A1E35', teal: '#2F6F73', seafoam: '#7FC8B8', amber: '#F5A54A', cream: '#F4E6C8', coral: '#E8574A', pink: '#D9738C' };

// You = Mint. Impostors = Grape + Cobalt. cos: hat | visor | topper | decal ids from art-jobs/out/M,N
export const ROSTER = [
  { id: 'mint',      name: 'Mint',      color: 'mint',      cos: { hat: 'headphones' } },
  { id: 'tomato',    name: 'Tomato',    color: 'tomato',    cos: { hat: 'party' } },
  { id: 'tangerine', name: 'Tangerine', color: 'tangerine', cos: {} },
  { id: 'mustard',   name: 'Mustard',   color: 'mustard',   cos: { hat: 'hardhat' } },
  { id: 'lime',      name: 'Lime',      color: 'lime',      cos: { topper: 'top_star' } },
  { id: 'sky',       name: 'Sky',       color: 'sky',       cos: { hat: 'flowercrown' } },
  { id: 'cobalt',    name: 'Cobalt',    color: 'cobalt',    cos: { visor: 'visor_aviator' }, impostor: true },
  { id: 'grape',     name: 'Grape',     color: 'grape',     cos: { hat: 'cowboy' }, impostor: true },
  { id: 'bubblegum', name: 'Bubblegum', color: 'bubblegum', cos: { visor: 'visor_heart' } },
  { id: 'cream',     name: 'Cream',     color: 'cream',     cos: { hat: 'chef' } },
];
export const P = Object.fromEntries(ROSTER.map((r) => [r.id, r]));

// ---- cosmetics cache (svg text), loaded once at boot
export const cosDB = { hats: {}, rest: {}, svg: {} };
export async function preloadCosmetics() {
  const [h, r] = await Promise.all([fetch(A('cos/hats.json')).then((x) => x.json()), fetch(A('cos/rest.json')).then((x) => x.json())]);
  h.items.forEach((i) => (cosDB.hats[i.id] = i));
  r.items.forEach((i) => (cosDB.rest[i.id] = i));
  const files = new Set();
  ROSTER.forEach(({ cos }) => {
    if (cos.hat) { const it = cosDB.hats[cos.hat]; collectHat(it).forEach((f) => files.add(f)); }
    ['visor', 'topper', 'decal'].forEach((s) => { if (cos[s]) { const it = cosDB.rest[cos[s]]; files.add(it.side.file); files.add(it.front.file); } });
  });
  await Promise.all([...files].map(async (f) => { cosDB.svg[f] = await fetch(A('cos/' + f.replace(/^svg\//, ''))).then((x) => x.text()); }));
}
export function collectHat(it) {
  const out = [it.side.file.replace(/^svg\//, ''), it.front.file.replace(/^svg\//, '')];
  const L = it.layers || {};
  for (const k of ['back', 'front']) if (L[k]) for (const v of Object.values(L[k])) out.push(v.replace(/^svg\//, ''));
  return out;
}

// ---- time helpers
export const fmtTime = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
export const rnd = (a, b) => a + Math.random() * (b - a);
export function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
export function shake(target, amp = 14) {
  return gsap.fromTo(target, { x: -amp }, { x: 0, duration: 0.45, ease: 'elastic.out(1.2,0.25)', overwrite: false, clearProps: 'x' });
}
