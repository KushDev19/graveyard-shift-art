import gsap from 'gsap';
import { el } from '../core/util.js';
import { mk, poof } from './common.js';

export const TASKS = [
  { id: 'reactor', text: 'Reactor Override', room: 'Reactor', done: false },
  { id: 'switch', text: 'Patch the Switchboard', room: 'Switchboard', done: false },
  { id: 'tapes', text: 'Download Tapes', room: 'Radio Room', done: false },
];
export const BODY = [560, 720];

export default {
  id: 6, title: 'Impostor eliminates', chapter: 'US3',
  story: 'POV switch to an Impostor: a fake task list that looks real, and an Eliminate button that only lights near a lone Crewmate. The server validates range and cooldown.',
  criteria: [
    '[US1 edge] Impostors see a fake task list that looks real; it never moves the bar.',
    '[US3 error] An Impostor in range of a living Crewmate can Eliminate: leaves a fallen-avatar marker, starts the Impostor\'s cooldown. The server rejects out-of-range or on-cooldown attempts.',
    '[US3 race] Two Impostors target the same player at once: only one elimination registers, only that cooldown starts.',
    '[US3] Eliminated players become ghosts; living players cannot see or hear ghosts.',
  ],
  async enter(ctx) {
    const hud = ctx.hud; const room = await ctx.room('switchboard'); const s = ctx.state = { room };
    s.tomato = mk('tomato'); room.add(s.tomato, ...BODY); s.tomato.setFacing(1);
    s.grape = mk('grape', { impostorVisor: false }); room.add(s.grape, 1480, 820); s.grape.setFacing(-1); s.grape.showName();
    hud.setTasks(TASKS.map((t) => ({ ...t }))); hud.setBar(35, false); hud.show({ impostor: true }); hud.setMeetings(1);
    hud.setBtn('use', false); hud.setBtn('report', false); hud.setBtn('eliminate', false);
    const [px, py] = BODY; s.ring = el('div', 'rangering', room.fx); gsap.set(s.ring, { autoAlpha: 0 });
    hud.onClick('eliminate', (off) => { if (ctx.director.step === 2 && !off) ctx.director.next(); else if (ctx.director.step === 3) ctx.director.next(); });
    ctx.caption('Switching to a different player: Grape, an Impostor.');
  },
  steps: [
    { label: 'IMPOSTOR VIEW + fake tasks',
      async run(ctx) {
        const hud = ctx.hud, s = ctx.state;
        await ctx.play(ctx.pov('IMPOSTOR VIEW', 'coral', 'a different player, a different screen'));
        ctx.caption('The Impostor\'s task list looks identical. Fake tasks tick off but never move the team bar.');
        hud.completeTask('reactor'); hud.toast('Fake task done: team bar unchanged (35%)', 'info', 2.6);
        await ctx.play(gsap.timeline().fromTo(hud.fillClip.parentNode, { x: -6 }, { x: 0, duration: 0.5, ease: 'elastic.out(1.2,0.3)' }, 0.5)); await ctx.wait(1.2);
      } },
    { label: 'Walk up to a lone Crewmate → Eliminate lights',
      async run(ctx) {
        const hud = ctx.hud, s = ctx.state; const [bx, by] = BODY;
        ctx.caption('Tomato is working alone. Grape walks into range and Eliminate lights up.');
        await ctx.play(s.grape.moveTo(bx + 330, by + 20, { speed: 300 }));
        await ctx.play(s.grape.moveTo(bx + 215, by + 10, { speed: 220 }));
        s.grape.setImpostorVisor(true); s.tomato.setMode('idle');
        const [gx, gy] = [gsap.getProperty(s.grape.root, 'x'), gsap.getProperty(s.grape.root, 'y')];
        Object.assign(s.ring.style, { left: gx - 270 + 'px', top: gy - 120 + 'px' });
        gsap.fromTo(s.ring, { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: 'back.out(2)' });
        hud.setBtn('eliminate', true); await ctx.wait(0.8);
      } },
    { label: 'Eliminate → fallen marker + cooldown',
      async run(ctx) {
        const hud = ctx.hud, s = ctx.state; const [bx, by] = BODY;
        ctx.caption('Server checks range and cooldown. Tomato becomes a fallen avatar; the cooldown starts.');
        await ctx.interactive({ sec: 3, label: 'auto-click', setup: (done) => { s.done = done; hud.onClick('eliminate', (off) => { if (!off) done(); }); }, auto: async () => {} });
        await ctx.play(hud.press('eliminate'));
        const tl = gsap.timeline().add(s.grape.moveTo(bx + 100, by + 6, { dur: 0.18, ease: 'power3.in' })).call(() => { s.tomato.setFallen(true); s.grape.doHop(); }).add(poof(s.room, bx, by - 90), '<')
          .add(ctx.flash('#E8574A', 0.45), '<').to(s.ring, { autoAlpha: 0, duration: 0.3 }, '<');
        await ctx.play(tl);
        hud.cooldown('eliminate', 20); hud.onClick('eliminate', null);
        await ctx.wait(1.2);
      } },
    { label: 'Click again → on cooldown; simultaneous strike rejected',
      async run(ctx) {
        const hud = ctx.hud, s = ctx.state;
        ctx.caption('Clicking again is rejected: the server says on cooldown.');
        await ctx.wait(0.4); hud.toast('On cooldown', 'error', 2.2); await ctx.play(gsap.fromTo(hud.btn.eliminate.b, { x: -10 }, { x: 0, duration: 0.5, ease: 'elastic.out(1.4,0.25)' }));
        await ctx.wait(1.6);
        ctx.caption('If two Impostors strike at once, only one counts and only that cooldown starts.');
        hud.toast('Cobalt struck too: rejected, target already down', 'error', 3.2); await ctx.wait(2.2);
      } },
  ],
};
