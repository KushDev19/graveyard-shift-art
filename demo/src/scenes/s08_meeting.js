import gsap from 'gsap';
import { A, el, img, ROSTER, P } from '../core/util.js';
import { MeetingTablet } from '../core/meeting.js';
import { EmergencyButton } from '../core/ebutton.js';
import { spawn, teleport, seatsOf, SEAT_ORDER, poof, mk } from './common.js';

const SCATTER = { mint: [1480, 900], tomato: [1180, 870], tangerine: [700, 830], mustard: [470, 900], lime: [340, 790], sky: [1660, 810], cobalt: [840, 950], grape: [1010, 900], bubblegum: [1350, 800], cream: [560, 770] };
const PLAYERS = ROSTER.map((r) => ({ id: r.id, name: r.name, color: r.color, cos: r.cos }));
const LIVE = ROSTER.map((r) => r.id).filter((i) => i !== 'tomato');

// votes for meeting 1 (a tie: Grape 2, Sky 2) and meeting 2 (Grape ejected)
const V1 = { mint: 'grape', mustard: 'grape', grape: 'sky', cobalt: 'sky', sky: 'mustard', tangerine: 'cobalt', lime: 'skip', cream: null, bubblegum: null };
const V2 = { mint: 'grape', tangerine: 'grape', mustard: 'grape', lime: 'grape', sky: 'grape', cream: 'grape', bubblegum: 'grape', grape: 'skip', cobalt: 'bubblegum' };

function seatAll(ctx, s, instantish = false) {
  const tl = gsap.timeline(); const seats = seatsOf(s.room);
  LIVE.forEach((id, n) => { const si = SEAT_ORDER[id]; tl.call(() => { s.pp[id].setView(si === 4 || si === 5 ? 'side' : 'front'); s.pp[id].setMode('idle'); }, null, n * 0.07 + 0.16); tl.add(teleport(s.pp[id], ...seats[si], { face: si === 4 ? 1 : si === 5 ? -1 : 0 }), n * 0.07); });
  return tl;
}
function scatterAll(ctx, s) {
  const tl = gsap.timeline(); LIVE.forEach((id, n) => { const [x, y] = SCATTER[id]; tl.call(() => s.pp[id].setView('side'), null, n * 0.04); tl.add(s.pp[id].moveTo(x, y, { speed: 520 }), n * 0.04); });
  return tl;
}
async function runVotes(ctx, s, votes, order, gap = 0.5) {
  const tl = gsap.timeline(); order.forEach((id, n) => tl.call(() => s.tablet.markVoted(id), null, 0.6 + n * gap));
  return ctx.play(tl);
}
function openMeeting(ctx, s, { caller, reported }) {
  const t = s.tablet; t.reset(); t.setEliminated(['tomato']); t.setCaller(caller, reported);
  return t.open();
}

export default {
  id: 8, title: 'Meeting & voting', chapter: 'US2',
  story: 'A report starts a meeting; everyone is pulled to the Galley, discusses, votes with two-step confirm, and the result is shown to all.',
  criteria: [
    '[US2] A living player triggers a meeting by reporting a fallen avatar OR via the emergency meeting table.',
    '[US2] Meeting start: movement stops, fallen avatars are cleared, all living players move to the meeting area.',
    '[US2] During a meeting all living players hear each other through video chat, wherever they stood.',
    '[US2] Meeting UI shows all participants, alive/eliminated status, and who called the meeting.',
    '[US2] After the discussion timer each living player votes for a living player or skips.',
    '[US2 error] No multiple votes, no changing a submitted vote ("Vote locked").',
    '[US2 edge] Voting timer expiry: non-voters count as casting no vote.',
    '[US2] Most votes is ejected and becomes a ghost; result shown to all. Eliminated players cannot vote.',
    '[US2 edge] Tie for most votes (or skip, or no votes): no one ejected, play resumes.',
    '[US2 edge] Limited emergency meetings per player; after that the table no longer starts one.',
    '[US2 error] A disconnecting player has their vote removed before counting.',
  ],
  async enter(ctx) {
    const room = await ctx.room('galley'); const s = ctx.state = { room };
    s.pp = spawn(room, SCATTER);
    s.pp.mint.showName(); s.pp.tomato.setFallen(true); s.pp.cobalt.setMode('idle');
    const [px, py] = room.anchor('emergency_pedestal'); s.eb = new EmergencyButton(room.sorted, px, py - 4, 0.5); s.eb.root.style.zIndex = Math.round(py + 4);
    ctx.hud.setTasks([{ id: 'a', text: 'Reactor Override', room: 'Reactor', done: true }, { id: 'b', text: 'Patch the Switchboard', room: 'Switchboard', done: true }, { id: 'c', text: 'Download Tapes', room: 'Radio Room', done: false }]);
    ctx.hud.setBar(55, false); ctx.hud.show(); ctx.hud.setMeetings(1); ctx.hud.setBtn('use', false); ctx.hud.setBtn('report', true);
    s.tablet = new MeetingTablet(ctx.L.modal, { players: PLAYERS, you: 'mint', notify: (t, k) => ctx.hud.toast(t, k) });
    ctx.hud.onClick('report', () => { if (ctx.director.step === 0) ctx.director.next(); });
    ctx.caption('Mint is next to Tomato\'s body. The Report button is lit.');
  },
  steps: [
    { label: 'Report → everyone teleports to seats',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        ctx.caption('Meeting start: movement stops, the fallen avatar is cleared, every living player is moved to the Galley.');
        await ctx.play(hud.press('report')); hud.setBtn('report', false);
        const tl = gsap.timeline();
        tl.add(poof(s.room, ...(() => { const [x, y] = SCATTER.tomato; return [x, y - 60]; })()), 0).to(s.pp.tomato.root, { scale: 0, duration: 0.4, ease: 'back.in(2)' }, 0)
          .call(() => LIVE.forEach((id) => s.pp[id].surprise(0.9)), null, 0.1)
          .add(seatAll(ctx, s), 0.7).add(ctx.dim(true, 0.5), 1.0).call(() => hud.hide(), null, 1.0);
        await ctx.play(tl);
      } },
    { label: 'Tablet: caller line, plates, discussion timer',
      async run(ctx) {
        const s = ctx.state, t = s.tablet;
        ctx.caption('Everyone hears everyone through video chat, wherever they stood.');
        await ctx.play(openMeeting(ctx, s, { caller: 'mint', reported: 'Tomato' }));
        const tl = gsap.timeline(); tl.add(t.startTimer('discuss', 15, 9), 0);
        ['sky', 'mustard', 'cream', 'lime', 'tangerine', 'cobalt'].forEach((id, n) => tl.call(() => s.pp[id].doHop(), null, 0.8 + n * 1.2));
        tl.call(() => t.clickTarget('grape'), null, 3.2);   // voting is disabled during discussion
        await ctx.play(tl);
      } },
    { label: 'Voting: select Grape → confirm → locked',
      async run(ctx) {
        const s = ctx.state, t = s.tablet;
        ctx.caption('Voting is open. Pick a player, then confirm: Mint votes Grape.');
        const timer = t.startTimer('vote', 120, 40);
        t.onVote = null;
        await ctx.interactive({ sec: 7, label: 'auto-vote',
          setup: (done) => { t.onVote = () => done(); },
          auto: async () => { await ctx.play(t.autoVote('grape')); } });
        t.onVote = null;
        ctx.caption('Vote locked: no changing it. Others show VOTED (who, never whom).');
        const tl = gsap.timeline().call(() => t.clickTarget('sky'), null, 0.6);
        ['tangerine', 'mustard', 'sky', 'lime', 'grape', 'cobalt'].forEach((id, n) => tl.call(() => t.markVoted(id), null, 1.3 + n * 0.55));
        await ctx.play(tl);
      } },
    { label: 'Timer expires → results → tie, no one ejected',
      async run(ctx) {
        const s = ctx.state, t = s.tablet;
        ctx.caption('Timer expired: non-voters (Bubblegum, Cream) count as no vote.');
        const left = t.timerObj ? Math.max(1, t.timerObj.t) : 30; t.stopTimer();
        await ctx.play(t.startTimer('vote', left, 2.2));
        t.phase = 'results';
        await ctx.play(t.reveal(V1)); await ctx.wait(1.6);
        ctx.caption(null);
        await ctx.play(t.showBanner('NO ONE WAS EJECTED (TIE)', 'GRAPE 2 · SKY 2 · TIES EJECT NO ONE, PLAY RESUMES', 'seafoam'));
      } },
    { label: 'Play resumes: crew walks back',
      async run(ctx) {
        const s = ctx.state;
        ctx.caption('Meeting over. Everyone walks back to work; Mint has 1 emergency meeting left.');
        const tl = gsap.timeline().add(s.tablet.hideBanner(), 0).add(s.tablet.close(), 0.2).add(ctx.dim(false), 0.3).call(() => ctx.hud.show(), null, 0.5);
        tl.add(scatterAll(ctx, s), 0.5);
        await ctx.play(tl);
      } },
    { label: 'Emergency button slam → EMERGENCY MEETING',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        ctx.caption('Mint slams the emergency button on the Galley table: this uses their only emergency meeting.');
        const [bx, by] = s.room.anchor('emergency_pedestal');
        await ctx.play(s.pp.mint.moveTo(bx + 120, by + 210, { speed: 480 }));
        hud.setBtn('use', true); await ctx.wait(0.4); await ctx.play(hud.press('use'));
        const tl = s.eb.slam(); const done = ctx.play(tl);
        gsap.delayedCall(ctx.instant ? 0 : 1.0, () => { hud.setMeetings(0); s.pp.mint.doHop(); }); if (ctx.instant) hud.setMeetings(0);
        await done; hud.setBtn('use', false);
        await ctx.play(ctx.splash(30, 'EMERGENCY<br>MEETING', 'CALLED BY MINT', 1.6));
      } },
    { label: 'Second meeting: vote Grape → ejected',
      async run(ctx) {
        const s = ctx.state, t = s.tablet, hud = ctx.hud;
        ctx.caption('Second meeting: this time the crew converges on Grape.');
        const tl0 = gsap.timeline().add(ctx.dim(true, 0.5), 0).call(() => hud.hide(), null, 0).add(seatAll(ctx, s), 0.1);
        await ctx.play(tl0);
        await ctx.play(openMeeting(ctx, s, { caller: 'mint', reported: null }));
        await ctx.play(t.startTimer('discuss', 15, 3));
        t.startTimer('vote', 120, 30);
        await ctx.interactive({ sec: 5, label: 'auto-vote', setup: (done) => { t.onVote = () => done(); }, auto: async () => { await ctx.play(t.autoVote('grape')); } });
        t.onVote = null;
        const tl = gsap.timeline(); ['tangerine', 'mustard', 'lime', 'sky', 'cream', 'bubblegum', 'cobalt', 'grape'].forEach((id, n) => tl.call(() => t.markVoted(id), null, 0.2 + n * 0.28));
        await ctx.play(tl);
        t.stopTimer(); await ctx.play(t.reveal(V2)); await ctx.wait(1.4);
        ctx.caption(null);
        await ctx.play(t.showBanner('GRAPE IS BEING EJECTED', '7 VOTES · MOST VOTES IS EJECTED AND BECOMES A GHOST', 'coral'));
        await ctx.wait(0.6);
      } },
    { label: 'Eject cutscene',
      async run(ctx) {
        const s = ctx.state;
        ctx.caption(null);
        ctx.L.modal.style.visibility = 'hidden'; ctx.world.style.display = 'none';
        const wrap = el('div', 'eject', ctx.L.splash); const bg = img(A('screens/32_screen_eject_1920.webp'), 'scene-bg', wrap); bg.style.objectPosition = '12% 50%';
        const g = mk('grape', { k: 0.34, impostor: true }); g.attach(wrap).place(180, 560); g.setMode('idle'); g.surprise(30);
        const txt = el('div', 'eject-text', wrap); txt.innerHTML = '<b></b><span></span>';
        const [b, sp] = txt.children;
        const tl = gsap.timeline();
        tl.fromTo(wrap, { opacity: 0 }, { opacity: 1, duration: 0.4 })
            .to(g.root, { x: 2300, y: 300, rotation: 1080, duration: 4.4, ease: 'power1.in' }, 0.6)
          .fromTo(g.root, { scale: 0.3 }, { scale: 0.7, duration: 4.4, ease: 'none' }, 0.6)
          ;
        // typewriter by hand (no TextPlugin dependency)
        const type = (node, str, at, dur) => { const o = { n: 0 }; tl.to(o, { n: str.length, duration: dur, ease: 'none', onUpdate() { node.textContent = str.slice(0, Math.round(o.n)); } }, at); };
        type(b, 'GRAPE WAS AN IMPOSTOR.', 1.2, 1.6); type(sp, '1 IMPOSTOR REMAINS.', 3.2, 1.2);
        ctx.caption('Non-voters count as no vote. If a player disconnects mid-vote, their vote is removed before counting.');
        await ctx.play(tl); await ctx.wait(0.8);
      } },
    { label: 'Edge: table disabled once your meetings are used',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        ctx.L.splash.innerHTML = ''; ctx.world.style.display = ''; ctx.L.modal.style.visibility = ''; s.tablet.root.style.display = 'none'; ctx.dim(false);
        s.pp.grape.root.remove(); s.pp.tomato.root.remove();
        hud.show(); hud.setMeetings(0); s.pp.cobalt.setImpostorVisor(false);
        LIVE.filter((i) => i !== 'grape').forEach((id) => { const [x, y] = SCATTER[id]; s.pp[id].place(x, y); });
        ctx.caption('Edge case: the table no longer starts a meeting for a player who has used all of theirs.');
        const [bx, by] = s.room.anchor('emergency_pedestal');
        await ctx.play(s.pp.mint.moveTo(bx + 120, by + 210, { speed: 520 }));
        hud.setBtn('use', true); await ctx.wait(0.35); await ctx.play(hud.press('use'));
        hud.toast('No emergency meetings left', 'error', 2.4); await ctx.play(s.eb.denied()); hud.setBtn('use', false);
      } },
  ],
};
