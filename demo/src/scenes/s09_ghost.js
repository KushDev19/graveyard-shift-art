import gsap from 'gsap';
import { A, el, img } from '../core/util.js';
import { mk } from './common.js';
import { createKeypad } from '../core/taskpanel.js';
import { createStation } from '../core/station.js';

export default {
  id: 9, title: 'Ghost view', chapter: 'EDGE',
  story: 'Eliminated players become ghosts: they pass through walls, finish their remaining tasks, and chat only with other ghosts. Living players cannot see or hear them.',
  criteria: [
    '[US1 edge] Ghosts can move through walls and finish their remaining tasks.',
    '[US3] Eliminated players become ghosts; living players cannot see or hear ghosts.',
    '[US2 edge] Eliminated players\' chat and voice reach only other eliminated players.',
    '[US1 error] A disconnecting player\'s tasks are removed from the total so the match stays winnable.',
  ],
  async enter(ctx) {
    const hud = ctx.hud; const room = await ctx.room('reactor'); const s = ctx.state = { room };
    s.key = await createStation(room.sorted, 'keypad', 460, 520, 330);
    s.ghost = mk('tomato'); room.add(s.ghost, 2050, 700); s.ghost.setGhost(true); s.ghost.setFacing(-1); s.ghost.showName();
    hud.setTasks([{ id: 'r', text: 'Reactor Override', room: 'Reactor', done: false }, { id: 'w', text: 'Fix Wiring', room: 'Switchboard', done: true }]); hud.setBar(72, false); hud.show(); hud.setMeetings(0);
    ctx.world.style.filter = 'saturate(.35) brightness(.9) hue-rotate(-10deg)';
    s.tint = el('div', 'ghost-tint', ctx.L.fx); ctx.caption('Tomato was eliminated and is now a ghost.');
  },
  steps: [
    { label: 'Float through the wall',
      async run(ctx) {
        const s = ctx.state; ctx.pov('GHOST VIEW', 'ghost', 'you are Tomato, now a ghost'); ctx.caption('Ghosts can move through walls. Tomato drifts in through the right wall, past the reactor.');
        const wall = el('div', 'wallring', s.room.fx); Object.assign(wall.style, { left: '1790px', top: '640px' });
        const tl = gsap.timeline().add(s.ghost.moveTo(1400, 760, { speed: 360 })).fromTo(wall, { scale: 0.2, autoAlpha: 0 }, { scale: 1.2, autoAlpha: 1, duration: 0.4 }, 0.5).to(wall, { autoAlpha: 0, duration: 0.4 }, 0.9)
          .add(s.ghost.moveTo(900, 620, { speed: 340 })).add(s.ghost.moveTo(570, 650, { speed: 340 }));
        await ctx.play(tl); wall.remove(); s.key.set('highlight');
      } },
    { label: 'Ghost finishes a task',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud; ctx.caption('Ghosts can still finish their remaining tasks, and the team bar moves.');
        const kp = createKeypad(ctx.L.modal); await ctx.play(kp.open);
        await ctx.interactive({ sec: 4, label: 'auto-play', setup: (done) => kp.solved.then(done), auto: async () => { await kp.auto((x) => ctx.wait(x * 0.45)); await ctx.wait(0.4); } });
        await ctx.play(kp.close()); s.key.set('done'); hud.completeTask('r'); hud.toast('SERVER CONFIRMED: Reactor Override', 'ok', 2.4); await ctx.wait(0.7); hud.setBar(81, true); await ctx.wait(1.3);
      } },
    { label: 'Ghost-only chat',
      async run(ctx) {
        const s = ctx.state; ctx.caption('Ghost chat is only seen by other ghosts. Living players can\'t see or hear ghosts.');
        const chat = el('div', 'ghostchat', ctx.L.modal);
        chat.innerHTML = `<div class="gc-h"><i></i>GHOST CHAT<span>Only ghosts can see this</span></div><div class="gc-m"><b>Tomato</b> It was Grape! He was right behind me.</div>`;
        gsap.fromTo(chat, { x: -80, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.5, ease: 'back.out(2)' });
        await ctx.wait(1.6);
        const m2 = el('div', 'gc-m', chat.querySelector('.gc-m').parentNode); m2.innerHTML = '<b>Bubblegum</b> (ghost) wow, I never saw him'; gsap.from(m2, { y: 20, autoAlpha: 0, duration: 0.4 });
        const tag = el('div', 'gc-lock', ctx.L.modal, 'Only ghosts can see this'); gsap.fromTo(tag, { scale: 0.5, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.5, ease: 'back.out(2)' });
        await ctx.wait(2.2);
      } },
    { label: 'Living view: no ghosts',
      async run(ctx) {
        const s = ctx.state; ctx.L.modal.innerHTML = '';
        await ctx.play(gsap.timeline().to(ctx.cover, { opacity: 1, duration: 0.18 }));
        ctx.world.style.filter = ''; s.tint.remove(); s.ghost.root.style.visibility = 'hidden'; ctx.hud.hide();
        const m = mk('mint'); s.room.add(m, 1500, 860); m.setFacing(-1); m.showName();
        await ctx.play(gsap.timeline().to(ctx.cover, { opacity: 0, duration: 0.25 }));
        ctx.caption('The same room for a living Crewmate: no ghost, no chat, nothing to hear.');
        const tl = ctx.pov('CREWMATE VIEW', 'crew', 'Mint sees no ghosts'); await ctx.play(gsap.timeline().add(m.moveTo(600, 720, { speed: 300 })).add(tl, 0));
        await ctx.wait(0.8);
      } },
  ],
};
