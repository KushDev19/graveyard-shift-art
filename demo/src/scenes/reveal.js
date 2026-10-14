import gsap from 'gsap';
import { A, el, img, P } from '../core/util.js';
import { Puppet } from '../core/puppet.js';

/** map normalised image coords to stage px for object-fit:cover with the given focal point */
export function coverMap(w, h, px = 0.5, py = 0.5) {
  const s = Math.max(1920 / w, 1080 / h), dw = w * s, dh = h * s, ox = (1920 - dw) * px, oy = (1080 - dh) * py;
  return (nx, ny) => [ox + nx * dw, oy + ny * dh];
}
export function stageBg(ctx, file, w, h, px = 0.5, py = 0.5) {
  const i = img(A('screens/' + file), 'scene-bg', ctx.world); i.style.objectPosition = `${px * 100}% ${py * 100}%`; return i;
}
export function title(ctx, text, sub, { tone = 'cream', top = 70 } = {}) {
  const t = el('div', `reveal-title ${tone}`, ctx.world); t.style.top = top + 'px'; t.innerHTML = `<b>${text}</b>${sub ? `<span>${sub}</span>` : ''}`; return t;
}
/** front-view puppets standing on the stage line. entries: {id,x,y,k,you,label,sub,impostor,smug,cos} */
export function lineup(ctx, entries) {
  const out = {};
  for (const e of entries) {
    const p = new Puppet({ color: P[e.id].color, name: P[e.id].name, cos: P[e.id].cos, view: 'front', k: e.k, impostor: !!e.impostor });
    p.smug = !!e.smug; p.attach(ctx.world).place(e.x, e.y); p.setMode(e.mode || 'idle');
    const lab = el('div', 'lineup-label' + (e.you ? ' you' : '') + (e.small ? ' sm' : ''), ctx.world); lab.style.left = e.x + 'px'; lab.style.top = e.y + 16 + 'px'; lab.style.zIndex = Math.round(e.y) + 1;
    lab.innerHTML = `<b>${e.you ? 'YOU · ' : ''}${P[e.id].name}</b>${e.sub ? `<i class="${e.subTone || ''}">${e.sub}</i>` : ''}`;
    out[e.id] = { p, lab, e };
  }
  return out;
}
export function popIn(out, ids, stagger = 0.09, at = 0) {
  const tl = gsap.timeline();
  ids.forEach((id, n) => { const { p, lab } = out[id]; gsap.set([p.root, lab], { autoAlpha: 0 });
    tl.fromTo(p.root, { y: p.root._gsap.y + 70, scale: 0.4, autoAlpha: 0 }, { y: p.root._gsap.y, scale: 1, autoAlpha: 1, duration: 0.5, ease: 'back.out(2.4)' }, at + n * stagger)
      .fromTo(lab, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.3 }, at + n * stagger + 0.25); });
  return tl;
}
