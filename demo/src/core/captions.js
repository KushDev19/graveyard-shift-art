import gsap from 'gsap';
import { el } from './util.js';

export function createCaptions(layer) {
  const bar = el('div', 'caption', layer); const txt = el('span', '', bar);
  let on = true, cur = null;
  const api = {
    set(t) {
      cur = t; if (!t) { gsap.to(bar, { autoAlpha: 0, y: 14, duration: 0.25, overwrite: true }); return; }
      txt.textContent = t;
      if (on) gsap.fromTo(bar, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: 'power3.out', overwrite: true });
    },
    toggle() { on = !on; if (!on) gsap.to(bar, { autoAlpha: 0, duration: 0.15 }); else if (cur) api.set(cur); return on; },
    get on() { return on; },
  };
  gsap.set(bar, { autoAlpha: 0 });
  return api;
}
