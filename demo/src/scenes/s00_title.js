import gsap from 'gsap';
import { A, el, img } from '../core/util.js';

let logoTxt = null;
export default {
  id: 0, title: 'Title', chapter: 'INTRO',
  story: 'GRAVEYARD SHIFT: a night-shift social deduction game on the cozy cargo ship Nightjar, played from an arcade cabinet in Covey.Town.',
  criteria: [
    '[Overview] In-world social deduction game for 4 to 10 players, joined from the arcade cabinet in the town.',
    '[Demo] Presenter-driven walkthrough of all three user stories (US1 tasks, US2 meetings and voting, US3 joining and secret roles).',
  ],
  async enter(ctx) {
    ctx.hud.hide(); const s = ctx.state = {};
    img(A('screens/27_screen_title_16x9_1920.webp'), 'scene-bg', ctx.world);
    gsap.fromTo(ctx.world.firstChild, { scale: 1.12 }, { scale: 1, duration: 8, ease: 'power1.out' });
    logoTxt ??= await fetch(A('brand/logo.svg')).then((r) => r.text());
    const wrap = el('div', 'logo-wrap', ctx.world); wrap.innerHTML = logoTxt.replace(/width="5504" height="3072"/, '');
    const svg = wrap.querySelector('svg'); svg.style.cssText = 'width:1500px;height:837px;overflow:visible'; s.svg = svg;
    const letters = [...svg.querySelectorAll('[data-char]')];
    gsap.fromTo(letters, { y: -140, opacity: 0 }, { y: 0, opacity: 1, duration: 0.7, ease: 'back.out(2.2)', stagger: 0.045, delay: 0.25 });
    const helmet = svg.querySelector('#helmet_dot'); if (helmet) gsap.fromTo(helmet, { opacity: 0, scale: 0.4, transformOrigin: 'center' }, { opacity: 1, scale: 1, duration: 0.6, ease: 'elastic.out(1,0.4)', delay: 1.1 });
    s.tag = el('div', 'title-tag', ctx.world, 'Clock in. Trust no one. Clock out (if you can).'); gsap.from(s.tag, { y: 30, autoAlpha: 0, duration: 0.6, delay: 1.2 });
    s.btn = el('button', 'clockin', ctx.world, 'CLOCK IN'); gsap.from(s.btn, { scale: 0, duration: 0.6, ease: 'back.out(2.4)', delay: 1.5 });
    gsap.to(s.btn, { scale: 1.06, duration: 0.8, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: 2.2 });
    s.btn.addEventListener('click', () => ctx.director.next());
    ctx.caption(null);
  },
  steps: [
    { label: 'CLOCK IN',
      async run(ctx) {
        const s = ctx.state; gsap.killTweensOf(s.btn);
        await ctx.play(gsap.timeline().to(s.btn, { scale: 0.9, y: 8, duration: 0.1 }).to(s.btn, { scale: 1.15, y: 0, duration: 0.35, ease: 'back.out(3)' }).add(ctx.flash('#F5A54A', 0.7), 0.1));
        ctx.caption('Clock in: the player joins from the arcade cabinet in Covey.Town.'); await ctx.wait(0.8);
      } },
  ],
};
