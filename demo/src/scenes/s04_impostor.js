import gsap from 'gsap';
import { stageBg, title, lineup, popIn, coverMap } from './reveal.js';

export default {
  id: 4, title: 'Impostor view', chapter: 'US3',
  story: 'POV switch: the same moment for an Impostor. Only Impostors see this screen, with their partner in coral visors.',
  criteria: [
    '[US3] Impostors also see the other Impostors; no other player can infer another\'s role from browser data.',
    '[US3] The Impostor screen shows only the Impostor team (coral visors, smug half-lid visor).',
  ],
  async enter(ctx) { ctx.hud.hide(); ctx.state = {}; stageBg(ctx, '29_screen_reveal_impostor_1920.webp', 1920, 1920, 0.5, 1); ctx.caption('Switching to a different player: Grape, secretly an Impostor.'); },
  steps: [
    { label: 'IMPOSTOR VIEW banner + reveal',
      async run(ctx) {
        await ctx.play(ctx.pov('IMPOSTOR VIEW', 'coral', 'only Impostors ever see this screen'));
        const M = coverMap(1920, 1920, 0.5, 1); const [, y] = M(0.5, 0.853);
        const out = lineup(ctx, [
          { id: 'cobalt', x: 1230, y: y + 14, k: 0.42, impostor: true, smug: true, sub: 'IMPOSTOR', subTone: 'coral' },
          { id: 'grape', x: 800, y: y + 40, k: 0.5, you: true, impostor: true, smug: true, sub: 'IMPOSTOR', subTone: 'coral' },
        ]);
        const t = title(ctx, 'IMPOSTOR', 'Your partner is Cobalt. Keep it secret.', { tone: 'coral', top: 54 });
        ctx.caption('Impostors also see the other Impostors, and only them.');
        const tl = gsap.timeline().fromTo(t, { scale: 2.2, autoAlpha: 0, y: -40 }, { scale: 1, autoAlpha: 1, y: 0, duration: 0.55, ease: 'back.out(1.6)' }).add(popIn(out, ['cobalt', 'grape'], 0.25, 0.2), 0);
        await ctx.play(tl); await ctx.wait(1.4);
      } },
  ],
};
