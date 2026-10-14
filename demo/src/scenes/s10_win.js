import gsap from 'gsap';
import { A, el, img, ROSTER, P } from '../core/util.js';
import { mk } from './common.js';
import { stageBg, title, lineup, popIn, coverMap } from './reveal.js';
import { Lobby, SPOT } from './s02_lobby.js';
import { TASKS } from './s06_eliminate.js';

const GHOSTS = ['tomato', 'grape'];

function winLineup(ctx, mode) {
  const file = mode === 'imp' ? '34_screen_win_impostor_1920.webp' : '33_screen_win_crew_1920.webp';
  stageBg(ctx, file, 1920, 1072, 0.5, 0.5);
  const M = coverMap(1920, 1072, 0.5, 0.5); const [, y] = M(0.5, mode === 'imp' ? 0.8184 : 0.8239); const [x0] = M(mode === 'imp' ? 0.2702 : 0.2754, 0), [x1] = M(mode === 'imp' ? 0.7309 : 0.7246, 0);
  const ids = ROSTER.map((r) => r.id); const entries = ids.map((id, i) => {
    const x = x0 - 190 + ((x1 - x0 + 380) * i) / (ids.length - 1); const imp = P[id].impostor;
    return { id, x, y: y + 6, k: 0.27, small: true, mode: mode === 'imp' ? (imp ? 'cheer' : 'idle') : (imp ? 'idle' : 'cheer'), impostor: imp && mode === 'imp', sub: imp ? 'IMPOSTOR' : 'CREWMATE', subTone: imp ? 'coral' : '' };
  });
  const out = lineup(ctx, entries);
  for (const id of GHOSTS) { out[id].p.setGhost(true); out[id].p.setMode('idle'); out[id].lab.querySelector('i').textContent += ' · GHOST'; }
  return { out, ids };
}

export default {
  id: 10, title: 'Win and back to lobby', chapter: 'END',
  story: 'The match ends the moment a win condition hits: task bar 100% or the last Impostor ejected (Crew wins), or living Crewmates <= Impostors (Impostors win; hotkey I). Every role is revealed, then everyone returns to the lobby.',
  criteria: [
    '[US1] Task bar at 100% ends the game immediately, announces a Crewmate victory to all, returns them to the lobby.',
    '[US2] Ejecting the last Impostor ends the game with a Crewmate victory, returns to the lobby.',
    '[US3] Living Crewmates <= living Impostors ends the game immediately: Impostor victory, all roles shown, back to lobby.',
    '[US3 error] A mid-game disconnect: the match continues and win conditions are re-checked.',
  ],
  async enter(ctx) {
    const hud = ctx.hud; ctx.winMode = ctx.winMode || 'crew'; const mode = ctx.winMode; const s = ctx.state = { mode };
    s.room = await ctx.room('galley');
    const spots = [[560, 800], [760, 880], [1000, 760], [1240, 880], [1440, 800], [900, 930]]; ['tangerine', 'mustard', 'sky', 'lime', 'cream', 'mint'].forEach((id, i) => { const p = mk(id); s.room.add(p, ...spots[i]); });
    hud.setTasks(TASKS.map((t, i) => ({ ...t, done: i < 2 }))); hud.setBar(mode === 'imp' ? 61 : 88, false); hud.show({ impostor: false }); hud.setMeetings(0);
    ctx.caption(mode === 'imp' ? 'Hotkey I: the alternate ending. Two Impostors strike while only two Crewmates are left.' : 'Almost there: the team bar is at 88%.');
  },
  steps: [
    { label: 'Win condition reached',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        if (s.mode === 'imp') {
          ctx.caption('Living Crewmates (2) are now equal to living Impostors (2): the game ends immediately.');
          hud.toast('2 Crewmates left vs 2 Impostors', 'error', 2.6); await ctx.wait(1.8);
        } else {
          ctx.caption('The last task is confirmed by the server: the bar hits 100% and the game ends immediately.');
          hud.completeTask('tapes'); hud.toast('SERVER CONFIRMED: Download Tapes', 'ok', 2.2); await ctx.wait(0.8); hud.setBar(100, true); await ctx.wait(1.8);
        }
        await ctx.play(ctx.flash('#F4E6C8', 0.6));
      } },
    { label: 'Win screen with every role revealed',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud; hud.hide(); s.room.el.remove(); ctx.caption(null);
        const { out, ids } = winLineup(ctx, s.mode);
        const t = title(ctx, s.mode === 'imp' ? 'IMPOSTORS WIN' : 'CREW WINS', s.mode === 'imp' ? 'THE NIGHT SHIFT CLAIMS ANOTHER CREW' : 'CREW CLOCKS OUT SAFE', { tone: s.mode === 'imp' ? 'coral' : 'amber', top: 50 });
        const tl = gsap.timeline().fromTo(t, { scale: 2.4, autoAlpha: 0, y: -50 }, { scale: 1, autoAlpha: 1, y: 0, duration: 0.6, ease: 'back.out(1.7)' }).add(popIn(out, ids, 0.07, 0.3), 0);
        await ctx.play(tl); await ctx.wait(2.2);
      } },
    { label: 'Returning to lobby',
      async run(ctx) {
        const s = ctx.state;
        const msg = el('div', 'returning', ctx.L.fx, 'Returning to lobby…'); const tl = gsap.timeline().fromTo(msg, { y: 30, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.4, ease: 'back.out(2)' });
        ctx.caption('Announced to everyone, roles revealed. Now everyone is sent back to the lobby.'); await ctx.play(tl); await ctx.wait(1.4);
        await ctx.play(gsap.timeline().to(ctx.cover, { opacity: 1, duration: 0.3 })); msg.remove();
        ctx.world.innerHTML = ''; const room = await ctx.room('locker');
        ROSTER.forEach((r) => { const p = mk(r.id); room.add(p, ...SPOT[r.id]); if (r.id === 'mint') p.showName(); });
        const L = new Lobby(ctx.L.modal); L.root.style.pointerEvents = 'none'; ROSTER.filter((r) => r.id !== 'mint' || true).forEach((r) => L.add(r.id, true)); L.setHost('mustard', true);
        await ctx.play(gsap.timeline().to(ctx.cover, { opacity: 0, duration: 0.35 })); ctx.caption('Back in the Locker Room lobby: 10/10 crew, host Mustard.'); await ctx.wait(1.2);
      } },
  ],
};
