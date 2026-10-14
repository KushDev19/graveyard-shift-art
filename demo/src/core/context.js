import gsap from 'gsap';
import { A, el, img, ROSTER, P } from './util.js';
import { createStage } from './stage.js';
import { createCaptions } from './captions.js';
import { Hud } from './hud.js';
import { Puppet } from './puppet.js';
import { Room } from './room.js';

export function createContext(root) {
  const S = createStage(root); const L = S.L;
  const ctx = { stage: S, L, instant: false, active: new Set(), finishers: new Set(), alt: null };
  ctx.cover = el('div', 'cover', L.fx);
  ctx.captions = createCaptions(L.present);
  ctx.hud = new Hud(L.hud); ctx.hud.ctx = ctx;
  ctx.world = el('div', 'world', L.world); Object.assign(ctx.world.style, { position: 'absolute', inset: 0 });

  ctx.caption = (t) => ctx.captions.set(t);
  ctx.killAll = () => { gsap.globalTimeline.clear(); gsap.globalTimeline.timeScale(1); ctx.active.clear(); ctx.finishers.clear(); };
  ctx.resetWorld = () => {
    ctx.world.innerHTML = ''; gsap.set(ctx.world, { clearProps: 'all' }); Object.assign(ctx.world.style, { position: 'absolute', inset: '0' });
    for (const k of ['modal', 'splash', 'pov']) L[k].innerHTML = '';
    L.fx.querySelectorAll('.autohint,.fxl').forEach((n) => n.remove());
    ctx.hud.root.style.visibility = 'hidden'; gsap.set(ctx.hud.root, { autoAlpha: 0 });
    ctx.hud.toasts.innerHTML = ''; ctx.hud.setTasks([]); ctx.hud.paintBar(0); ctx.hud.pctVal = 0; ctx.hud.setMeetings(1);
    for (const k of ['use', 'report', 'eliminate']) { ctx.hud.btn[k].on = true; ctx.hud.setBtn(k, false); ctx.hud.btn[k].b.classList.remove('cooling'); }
    ctx.hud.showMeetings(true); ctx.captions.set(null); ctx.hud.btn.eliminate.b.style.display = 'none';
    ctx.state = {};
  };

  // ---- timeline helpers (instant mode = replay)
  ctx.play = (tl) => new Promise((res) => {
    if (!tl || (tl.duration && tl.duration() === 0 && !tl.isActive?.())) { res(); return; }
    ctx.active.add(tl);
    const prev = tl.eventCallback('onComplete'); let fired = false;
    const done = () => { if (fired) return; fired = true; ctx.active.delete(tl); try { prev?.call(tl); } catch (e) { console.error(e); } res(); };
    tl.eventCallback('onComplete', done);
    if (ctx.instant) tl.progress(1, false);
  });
  ctx.wait = (sec) => ctx.play(gsap.timeline().to({}, { duration: sec }));
  ctx.finishActive = () => {
    for (const tl of [...ctx.active]) { try { tl.progress(1, false); } catch (e) { /* noop */ } }
    for (const f of [...ctx.finishers]) f();
  };
  /** interactive beat: setup(done) mounts UI and calls done() when the user finishes; auto(done) fakes it after `sec` or when presenter skips. */
  ctx.interactive = ({ setup, auto, sec = 6, label = 'auto' }) => new Promise((res) => {
    let finished = false; let hint, dc;
    const done = () => { if (finished) return; finished = true; ctx.finishers.delete(skip); dc?.kill(); hint?.remove(); res(); };
    const runAuto = () => { if (finished) return; dc?.kill(); hint?.remove(); auto ? Promise.resolve(auto(done)).then(done) : done(); };
    const skip = () => runAuto();
    ctx.finishers.add(skip);
    setup?.(done);
    if (ctx.instant) { runAuto(); return; }
    hint = el('div', 'autohint', L.fx); let left = sec; hint.textContent = `${label} in ${left}s · or do it yourself`;
    dc = gsap.timeline().to({}, { duration: sec, ease: 'none', onUpdate() { const n = Math.ceil(sec * (1 - this.progress())); if (n !== left) { left = n; hint.textContent = `${label} in ${left}s · or do it yourself`; } }, onComplete: () => runAuto() });
  });

  // ---- scene building helpers
  ctx.room = (key) => Room.create(ctx.world, key);
  ctx.puppet = (id, o = {}) => { const r = P[id]; return new Puppet({ color: r.color, name: r.name, cos: r.cos, impostor: false, ...o }); };
  ctx.bg = (file, cls = '') => { const i = img(A('screens/' + file), 'scene-bg ' + cls, ctx.world); return i; };
  ctx.dim = (on, amt = 0.42) => gsap.to(ctx.world, { filter: on ? `brightness(${amt}) saturate(.8) blur(3px)` : 'brightness(1) saturate(1) blur(0px)', duration: 0.45, ease: 'power2.out' });
  ctx.pov = (text, tone = 'crew', sub = '') => {
    const b = el('div', 'povbanner ' + tone, L.pov); b.innerHTML = `${text}${sub ? `<small>${sub}</small>` : ''}`;
    return gsap.timeline({ onComplete: () => b.remove() }).fromTo(b, { scale: 0.4, autoAlpha: 0, rotation: -4 }, { scale: 1, autoAlpha: 1, rotation: 0, duration: 0.5, ease: 'back.out(2.2)' }).to(b, { autoAlpha: 0, scale: 1.1, duration: 0.3, delay: 1.1 });
  };
  ctx.splash = (kind, title, sub = '', hold = 1.8) => {
    const cfg = kind === 30 ? { svg: '30_rays.svg', fg: '30_screen_splash_emergency_fg_1920.webp', px: 0.2504, py: 0.498 } : { svg: '31_rays.svg', fg: '31_screen_splash_body_fg_1920.webp', px: 0.2573, py: 0.5 };
    const w = el('div', 'splash', L.splash); const clip = el('div', 'splash-clip', w);
    const rays = img(A('screens/' + cfg.svg), 'splash-rays', clip); rays.style.transformOrigin = `${cfg.px * 100}% ${cfg.py * 100}%`;
    img(A('screens/' + cfg.fg), 'splash-fg', clip);
    const t = el('div', 'splash-title', clip); t.innerHTML = `<b>${title}</b>${sub ? `<span>${sub}</span>` : ''}`; t.style.left = cfg.px * 1920 + 'px';
    const spin = gsap.to(rays, { rotation: 360, duration: 14, ease: 'none', repeat: -1 });
    return gsap.timeline({ onComplete: () => { spin.kill(); w.remove(); } })
      .fromTo(w, { clipPath: 'circle(0% at 25% 50%)' }, { clipPath: 'circle(150% at 25% 50%)', duration: 0.55, ease: 'power3.out' })
      .fromTo(t, { scale: 2.6, rotation: -8, autoAlpha: 0 }, { scale: 1, rotation: -3, autoAlpha: 1, duration: 0.42, ease: 'back.out(1.8)' }, 0.2)
      .fromTo(clip, { x: 0 }, { x: 0, duration: hold })
      .to(w, { autoAlpha: 0, scale: 1.06, duration: 0.3, ease: 'power2.in' });
  };
  ctx.flash = (color = '#fff', dur = 0.5) => { const f = el('div', 'fxl', L.fx); f.style.cssText = `position:absolute;inset:0;background:${color};pointer-events:none;`; return gsap.timeline({ onComplete: () => f.remove() }).fromTo(f, { opacity: 0.9 }, { opacity: 0, duration: dur, ease: 'power2.out' }); };
  ctx.roster = ROSTER; ctx.P = P;
  return ctx;
}
