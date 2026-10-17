import gsap from 'gsap';
import { A, el, img } from '../core/util.js';

/** The three priority tiers of the revised plan, shown as columns of the closing card. */
const COLUMNS = [
  { tone: 'amber', label: 'MUST HAVE', sub: 'High priority, built first', items: [
    'Join from the arcade, lobby with a host',
    'Secret roles, nothing leaks to other players',
    'Tasks: keypad and wiring, shared task bar',
    'Eliminate in range, with a cooldown',
    'Report, emergency meeting, vote, ejection',
    'Ghosts, win conditions, back to the lobby',
  ] },
  { tone: 'seafoam', label: 'DESIRABLE', sub: 'Medium priority, after the required work', items: [
    'Fake tasks for Impostors, ghosts finish tasks',
    'Vote locked, meeting details and limits',
    'Vents for Impostors',
    'Tasks that span two rooms',
    'Town and match players kept apart',
    'Ghosts walk through walls, kill rule checks',
  ] },
  { tone: 'coral', label: 'FUTURE', sub: 'Low priority, not in this plan', items: [
    'Sabotage',
    'Security cameras and admin map',
    'Vision fog and line of sight',
    'Ghost-only chat and voice',
    'Anonymous voting, host settings',
    'More mini-games, leaderboard',
  ] },
];

export default {
  id: 11, title: 'Scope', chapter: 'SCOPE',
  story: 'After the feedback on the preliminary plan the work is prioritized: required features first, then desirable ones, and extensions are left as future work.',
  criteria: [
    '[Feedback] User stories had too many essential conditions: each condition is now High (required), Medium (desirable) or Low (future work).',
    '[Feedback] The plan was too ambitious: sabotage, cameras, fog, ghost-only chat and more are extensions, not part of the plan.',
    '[Feedback] Documentation tasks were added to the sprints.',
  ],
  async enter(ctx) {
    ctx.hud.hide(); const s = ctx.state = {};
    img(A('screens/27_screen_title_16x9_1920.webp'), 'scene-bg', ctx.world);
    el('div', 'scope-dim', ctx.world);
    s.head = el('div', 'scope-head', ctx.world, 'WHAT WE BUILD, IN ORDER');
    s.cols = COLUMNS.map((c, i) => {
      const root = el('div', `scope-col ${c.tone}`, ctx.world); root.style.left = `${80 + i * 600}px`;
      el('b', '', root, c.label); el('span', '', root, c.sub);
      const ul = el('ul', '', root); const lis = c.items.map((t) => el('li', '', ul, t));
      return { root, lis };
    });
    s.foot = el('div', 'scope-foot', ctx.world, 'Updated after feedback: stories prioritized, extras made optional, documentation tasks added.');
    gsap.set([s.head, s.foot, ...s.cols.flatMap((c) => [c.root, ...c.lis])], { autoAlpha: 0 });
    ctx.caption(null);
  },
  steps: [
    { label: 'Scope card', hold: 6,
      async run(ctx) {
        const s = ctx.state; const tl = gsap.timeline();
        tl.fromTo(s.head, { y: -30, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5, ease: 'back.out(1.8)' });
        s.cols.forEach((c, i) => {
          const at = 0.4 + i * 0.5;
          tl.fromTo(c.root, { y: 60, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.55, ease: 'back.out(1.5)' }, at)
            .fromTo(c.lis, { x: -24, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.35, stagger: 0.07, ease: 'power2.out' }, at + 0.3);
        });
        tl.fromTo(s.foot, { y: 20, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5 }, 2.3);
        await ctx.play(tl); await ctx.wait(3);
      } },
  ],
};
