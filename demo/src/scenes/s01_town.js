import gsap from 'gsap';
import { A, el, img, COLORS } from '../core/util.js';
import { paintTown, loadMisa, ARCADE } from '../core/town.js';

/** a real Covey.Town avatar: the "misa" sprite from the class repo atlas, with a name label like the real game */
function pxAvatar(parent, frames, name, x, y, s = 2) {
  const d = el('div', 'px-avatar', parent); d.style.backgroundImage = `url(${A('town/misa.png')})`; d.style.backgroundSize = `${196 * s}px ${86 * s}px`;
  el('div', 'px-name', d, name);
  const o = { walking: false, dir: 'front' }; gsap.set(d, { x, y, xPercent: -50, yPercent: -100 });
  const tick = () => { const f = frames[o.walking ? `misa-${o.dir}-walk.00${Math.floor(gsap.ticker.time * 8) % 4}` : `misa-${o.dir}`]; d.style.width = f.w * s + 'px'; d.style.height = f.h * s + 'px'; d.style.backgroundPosition = `${-f.x * s}px ${-f.y * s}px`; };
  gsap.ticker.add(tick); tick();
  o.el = d;
  o.move = (tx, ty, dur) => { const cx = gsap.getProperty(d, 'x'), cy = gsap.getProperty(d, 'y'); o.dir = Math.abs(tx - cx) > Math.abs(ty - cy) ? (tx > cx ? 'right' : 'left') : (ty > cy ? 'front' : 'back'); return gsap.to(d, { x: tx, y: ty, duration: dur, ease: 'none', onStart: () => (o.walking = true), onComplete: () => { o.walking = false; o.dir = 'front'; }, onUpdate: () => (d.style.zIndex = Math.round(gsap.getProperty(d, 'y'))) }); };
  return o;
}

function arcadeModal(layer, mode) {
  const w = el('div', 'arc-modal', layer); const card = el('div', 'arc-card', w);
  const art = img(A('brand/arcade.webp'), 'arc-art', card);
  const body = el('div', 'arc-body', card);
  el('div', 'arc-h', body, 'GRAVEYARD SHIFT');
  if (mode === 'busy') {
    el('div', 'arc-state bad', body, 'SHIFT IN PROGRESS');
    el('div', 'arc-p', body, 'A crew is already on the Nightjar. You can\'t join right now.');
    const b = el('button', 'arc-btn off', body, 'CHECK BACK LATER');
    return { w, card, body, btn: b };
  }
  el('div', 'arc-state ok', body, '<b>3/10</b> crew clocked in');
  el('div', 'arc-p', body, 'Night shift on the Nightjar. 4 to 10 players. Trust no one.');
  const b = el('button', 'arc-btn', body, 'CLOCK IN');
  return { w, card, body, btn: b };
}

export default {
  id: 1, title: 'Town and arcade', chapter: 'US3',
  story: 'In the Covey.Town street, the player walks up to the glowing arcade cabinet. The prompt shows the lobby count, or a coral warning when a shift is already running.',
  criteria: [
    '[US3] Walking up to the arcade machine shows a prompt with the lobby count (e.g. 3/10); accepting moves the player into the spaceship lobby.',
    '[US3 edge] Lobby full (10) or game in progress: no one can join.',
    '[US3 edge Medium] The arcade prompt says when the lobby is full or a game is in progress.',
    '[US3 edge Medium] Players in the match and players in town cannot see or hear each other.',
  ],
  async enter(ctx) {
    const [canvas, frames] = await Promise.all([paintTown(), loadMisa()]); canvas.className = 'town-canvas'; ctx.world.appendChild(canvas);
    const s = ctx.state = {}; const layer = el('div', 'town-layer', ctx.world);
    const ax = ARCADE.stageX, ay = ARCADE.stageY;
    s.glow = el('div', 'arc-glow', layer); Object.assign(s.glow.style, { left: ax + 'px', top: ay - 64 + 'px' }); gsap.to(s.glow, { opacity: 0.55, scale: 1.12, duration: 1.1, repeat: -1, yoyo: true, ease: 'sine.inOut' });
    s.tag = el('div', 'arc-tag', layer, '▼ GRAVEYARD SHIFT'); Object.assign(s.tag.style, { left: ax + 'px', top: ay - 190 + 'px' }); gsap.to(s.tag, { y: -10, repeat: -1, yoyo: true, duration: 0.7, ease: 'sine.inOut' });
    s.npc = [pxAvatar(layer, frames, 'Tomato', 760, 940), pxAvatar(layer, frames, 'Tangerine', 1250, 960), pxAvatar(layer, frames, 'Grape', 1600, 900)];
    s.npc.forEach((n, i) => { const loop = () => { const tx = 600 + Math.random() * 1100, ty = 880 + Math.random() * 130; n.move(tx, ty, Math.hypot(tx - gsap.getProperty(n.el, 'x'), ty - gsap.getProperty(n.el, 'y')) / 90).eventCallback('onComplete', () => { n.walking = false; n.dir = 'front'; gsap.delayedCall(1 + Math.random() * 2, loop); }); }; gsap.delayedCall(i * 0.6, loop); });
    s.me = pxAvatar(layer, frames, 'Mint', 200, 920); s.me.el.classList.add('me');
    s.modal = null;
    ctx.caption('Covey.Town: players in a match and players in town can\'t see or hear each other.');
  },
  steps: [
    { label: 'Walk to the glowing arcade',
      async run(ctx) {
        const s = ctx.state; ctx.caption('The arcade cabinet glows. Walk up to it.');
        await ctx.play(gsap.timeline().add(s.me.move(ARCADE.stageX - 40, 930, 3.8)).add(s.me.move(ARCADE.stageX, ARCADE.stageY + 78, 1.3))); s.me.walking = false; s.me.dir = 'back';
      } },
    { label: 'Edge: shift in progress',
      async run(ctx) {
        const s = ctx.state; ctx.caption('Edge case: a match is already running, so the prompt says so and no one can join.');
        s.modal = arcadeModal(ctx.L.modal, 'busy'); await ctx.play(gsap.timeline().fromTo(s.modal.card, { scale: 0.6, y: 80, autoAlpha: 0 }, { scale: 1, y: 0, autoAlpha: 1, duration: 0.5, ease: 'back.out(1.8)' }));
        await ctx.wait(2.2); await ctx.play(gsap.timeline().to(s.modal.card, { scale: 0.7, autoAlpha: 0, y: 60, duration: 0.3, ease: 'power2.in' })); s.modal.w.remove();
        ctx.hud.toast('…a few minutes later', 'info', 1.6); await ctx.wait(1.0);
      } },
    { label: 'Prompt: 3/10 → CLOCK IN → ship',
      async run(ctx) {
        const s = ctx.state; ctx.caption('The shift ended. Now the prompt shows the lobby: 3/10 crew clocked in.');
        s.modal = arcadeModal(ctx.L.modal, 'open'); await ctx.play(gsap.timeline().fromTo(s.modal.card, { scale: 0.6, y: 80, autoAlpha: 0 }, { scale: 1, y: 0, autoAlpha: 1, duration: 0.5, ease: 'back.out(1.8)' }));
        await ctx.interactive({ sec: 5, label: 'auto-clock-in', setup: (done) => s.modal.btn.addEventListener('click', done), auto: async () => { await ctx.wait(0.3); } });
        await ctx.play(gsap.timeline().to(s.modal.btn, { scale: 0.92, duration: 0.1 }).to(s.modal.btn, { scale: 1, duration: 0.3, ease: 'back.out(3)' }));
        ctx.caption('Accepting moves you into the spaceship lobby (CRT power-on).');
        const crt = el('div', 'crt-on', ctx.L.fx); const tl = gsap.timeline().to(s.modal.card, { scale: 0.5, autoAlpha: 0, duration: 0.25 }).fromTo(crt, { scaleY: 0.004, scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.25, ease: 'power2.out' }).to(crt, { scaleY: 1, duration: 0.3, ease: 'power3.in' }).to(crt, { opacity: 0, duration: 0.25 });
        await ctx.play(tl); crt.remove();
      } },
  ],
};
