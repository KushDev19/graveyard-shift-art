import gsap from 'gsap';
import { el } from '../core/util.js';
import { stageBg, title, lineup, popIn, coverMap } from './reveal.js';

const OTHERS = ['tomato', 'tangerine', 'mustard', 'lime', 'sky', 'cobalt', 'grape', 'bubblegum', 'cream'];

export default {
  id: 3, title: 'Crew reveal', chapter: 'US3',
  story: 'Match start: "Shhh..." then each player privately sees their own role. This is the Crewmate screen: you centred and larger, everyone else beside you.',
  criteria: [
    '[US3] At start each player privately sees Crewmate or Impostor; roles are never sent to other clients.',
    '[US3] Crewmate screen shows the whole crew and the number of Impostors ("There are 2 Impostors among us").',
    '[US3] Every player is drawn in their own colour and cosmetics from the same puppet.',
  ],
  async enter(ctx) {
    ctx.hud.hide(); const s = ctx.state = {};
    s.shh = el('div', 'shh', ctx.world, '<b>SHHH...</b><span>your role is secret</span>');
    gsap.fromTo(s.shh.firstChild, { scale: 0.7, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.6, ease: 'back.out(2)' });
    gsap.to(s.shh.firstChild, { scale: 1.04, repeat: -1, yoyo: true, duration: 0.9, ease: 'sine.inOut', delay: 0.6 });
    ctx.caption('The match is starting…');
  },
  steps: [
    { label: 'Shhh…', async run(ctx) { ctx.caption('Each player receives only their own role.'); await ctx.wait(1.4); } },
    { label: 'CREWMATE reveal',
      async run(ctx) {
        const s = ctx.state; s.shh.remove();
        stageBg(ctx, '28_screen_reveal_crew_1920.webp', 1920, 815, 0.5, 0.5);
        const M = coverMap(1920, 815, 0.5, 0.5); const [, y] = M(0.5, 0.769); const base = y + 10;
        const entries = [
          { id: 'mint', x: 960, y: base + 30, k: 0.4, you: true, sub: 'CREWMATE' },
          ...OTHERS.map((id, i) => { const X = [340, 480, 620, 760, 1150, 1275, 1400, 1525, 1650][i], back = i % 2 === 0; return { id, x: X, y: base + (back ? -34 : 8), k: back ? 0.23 : 0.25 }; }),
        ];
        // keep labels only for you + a few; names for all stay small
        const out = s.out = lineup(ctx, entries);
        const t = title(ctx, 'CREWMATE', 'There are 2 Impostors among us', { tone: 'amber', top: 54 });
        const order = [...OTHERS].reverse().concat('mint');
        ctx.caption('Each player receives only their own role: you see "CREWMATE"; nobody else\'s.');
        const tl = gsap.timeline().fromTo(t, { scale: 2.2, autoAlpha: 0, y: -40 }, { scale: 1, autoAlpha: 1, y: 0, duration: 0.55, ease: 'back.out(1.6)' }, 0.2).add(popIn(out, order, 0.1, 0.35), 0);
        await ctx.play(tl); out.mint.p.doHop(); await ctx.wait(1.2);
      } },
  ],
};
