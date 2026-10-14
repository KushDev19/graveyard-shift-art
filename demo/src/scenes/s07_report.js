import gsap from 'gsap';
import { mk } from './common.js';
import { TASKS, BODY } from './s06_eliminate.js';

export default {
  id: 7, title: 'Crew finds the body', chapter: 'US2',
  story: 'Back to the Crewmate view: Mint walks in, the fallen avatar is in range, Report lights up, and pressing it starts a meeting.',
  criteria: [
    '[US2] A living player triggers a meeting by reporting a fallen avatar within range.',
    '[US3] Eliminated avatars stay as a fallen marker until a meeting clears them; ghosts are invisible to the living.',
  ],
  async enter(ctx) {
    const hud = ctx.hud; const room = await ctx.room('switchboard'); const s = ctx.state = { room };
    s.tomato = mk('tomato'); room.add(s.tomato, ...BODY); s.tomato.setFallen(true);
    s.mint = mk('mint'); room.add(s.mint, 1500, 1000); s.mint.setFacing(-1); s.mint.showName();
    hud.setTasks(TASKS.map((t, i) => ({ ...t, done: i < 2 }))); hud.setBar(55, false); hud.show(); hud.setMeetings(1); hud.setBtn('use', false); hud.setBtn('report', false);
    hud.onClick('report', (off) => { if (!off && ctx.director.step === 1) ctx.director.next(); });
  },
  steps: [
    { label: 'Mint walks in and finds the body',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud; const [bx, by] = BODY;
        await ctx.play(ctx.pov('CREWMATE VIEW', 'crew', 'back to Mint'));
        ctx.caption('Mint walks into the Switchboard room…');
        await ctx.play(s.mint.moveTo(bx + 420, by + 120, { speed: 330 }));
        await ctx.play(s.mint.moveTo(bx + 190, by + 20, { speed: 240 })); s.mint.surprise(1.4);
        hud.setBtn('report', true); ctx.caption('A fallen avatar is within range: the Report button lights up.'); await ctx.wait(1.0);
      } },
    { label: 'Report → BODY REPORTED',
      async run(ctx) {
        const hud = ctx.hud;
        await ctx.interactive({ sec: 3, label: 'auto-report', setup: (done) => hud.onClick('report', (off) => { if (!off) done(); }), auto: async () => {} });
        await ctx.play(hud.press('report')); hud.setBtn('report', false); ctx.caption(null);
        await ctx.play(ctx.splash(31, 'BODY<br>REPORTED', 'MINT FOUND TOMATO', 1.9));
      } },
  ],
};
