import gsap from 'gsap';
import { mk } from './common.js';
import { createKeypad, createWiring } from '../core/taskpanel.js';
import { createStation } from '../core/station.js';

const TASKS = [
  { id: 'reactor', text: 'Reactor Override', room: 'Reactor', done: false },
  { id: 'switch', text: 'Patch the Switchboard', room: 'Switchboard', done: false },
  { id: 'tapes', text: 'Download Tapes', room: 'Radio Room', done: false },
];
const POS = {
  reactor: { scope: [1500, 560], scopeSpot: [1400, 720], key: [460, 520], keySpot: [560, 660], start: [980, 900] },
  switchboard: { st: [1381, 480], spot: [1381, 640], away: [1000, 880], start: [900, 900] },
};

async function cut(ctx, fn) {
  await ctx.play(gsap.timeline().to(ctx.cover, { opacity: 1, duration: 0.22, ease: 'power2.in' }));
  await fn();
  await ctx.play(gsap.timeline().to(ctx.cover, { opacity: 0, duration: 0.3 }));
}
async function useAt(ctx, onUse) { // light Use, press it (the presenter can click it too), run onUse
  const hud = ctx.hud; hud.setBtn('use', true);
  await ctx.interactive({ sec: 2.4, label: 'auto-use', setup: (done) => hud.onClick('use', (off) => { if (!off) done(); }), auto: async () => {} });
  await ctx.play(hud.press('use')); await onUse();
}

export default {
  id: 5, title: 'Completing tasks', chapter: 'US1',
  story: 'Crewmate view: assigned task list with rooms, the shared team bar, stations that open mini-games (keypad, wiring), server-confirmed credit, and the edge cases.',
  criteria: [
    '[US1] View assigned task list, with the room of each task.',
    '[US1] Approaching an assigned station and interacting opens its task interface; a station with no task for that player shows a message and opens nothing.',
    '[US1] A task counts only after the server confirms it; completing one updates the shared team task bar for all players.',
    '[US1] Completed tasks no longer show as incomplete to that player.',
    '[US1 edge] Closing the task or walking away before finishing resets it, no credit.',
    '[US1] At least two mini-games: keypad entry (numbers in order) and wiring (match coloured wires).',
  ],
  async enter(ctx) {
    const hud = ctx.hud; const room = await ctx.room('reactor'); const s = ctx.state = { room, tasks: TASKS.map((t) => ({ ...t })) };
    await ctx.room('switchboard').then((r) => r.el.remove()); // warm the cache
    s.keypad = await createStation(room.sorted, 'keypad', ...POS.reactor.key, 330);
    s.scope = await createStation(room.sorted, 'scope', ...POS.reactor.scope, 280);
    s.mint = mk('mint'); room.add(s.mint, ...POS.reactor.start); s.mint.showName();
    hud.setTasks(s.tasks); hud.setBar(20, false); hud.show(); hud.showMeetings(true); hud.setMeetings(1);
    ctx.caption('Crewmate view: your task list shows each task and its room. The team bar is shared by everyone.');
  },
  steps: [
    { label: 'Task list + team bar',
      async run(ctx) {
        ctx.caption('Your task list shows each task and its room. The team bar (20%) is shared by the whole crew.');
        const L = ctx.hud.left; await ctx.play(gsap.timeline().fromTo(L, { x: -14 }, { x: 0, duration: 0.5, ease: 'elastic.out(1,0.4)' }));
        ctx.pov('CREWMATE VIEW', 'crew', 'your own role and tasks only');
        await ctx.wait(1.4);
      } },
    { label: 'Edge: station with no task',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud; const m = s.mint;
        ctx.caption('Edge case: a station with no task for you opens nothing.');
        await ctx.play(m.moveTo(...POS.reactor.scopeSpot, { speed: 420 })); s.scope.set('highlight');
        await useAt(ctx, async () => { hud.toast('No task here: nothing assigned to you', 'error', 2.6); await ctx.wait(1.4); });
        s.scope.set('idle'); hud.setBtn('use', false);
      } },
    { label: 'Keypad task',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud, m = s.mint;
        ctx.caption('Assigned station: walk up, press Use, and the keypad mini-game opens. Press 1 to 10 in order.');
        await ctx.play(m.moveTo(...POS.reactor.keySpot, { speed: 420 })); s.keypad.set('highlight');
        let kp;
        await useAt(ctx, async () => {
          kp = createKeypad(ctx.L.modal, { onWrong: () => hud.toast('Wrong key: sequence reset', 'error', 1.6) }); s.kp = kp; await ctx.play(kp.open);
          await ctx.interactive({ sec: 9, label: 'auto-play', setup: (done) => kp.solved.then(done), auto: async () => { await kp.auto((x) => ctx.wait(x)); await ctx.wait(0.7); } });
        });
      } },
    { label: 'Server confirms → team bar rises for everyone',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        await ctx.play(s.kp.close()); s.keypad.set('done'); hud.setBtn('use', false);
        hud.completeTask('reactor'); s.tasks[0].done = true;
        ctx.caption('A task counts only after the server confirms it. The team bar then rises for everyone.');
        hud.toast('SERVER CONFIRMED: Reactor Override', 'ok', 2.6); await ctx.wait(0.9);
        hud.setBar(48, true); await ctx.wait(1.6);
      } },
    { label: 'Edge: walk away mid-task = reset',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        ctx.caption('Next task: Patch the Switchboard (Switchboard room).');
        await cut(ctx, async () => {
          s.room.el.remove(); s.room = await ctx.room('switchboard');
          s.st = await createStation(s.room.sorted, 'switchboard', ...POS.switchboard.st, 330);
          s.mint.root.remove(); s.room.add(s.mint, ...POS.switchboard.start);
        });
        await ctx.play(s.mint.moveTo(...POS.switchboard.spot, { speed: 420 })); s.st.set('highlight');
        ctx.caption('Start a task, then walk away: the panel closes and the task resets with no credit.');
        await useAt(ctx, async () => {
          const w = createWiring(ctx.L.modal); s.w = w; await ctx.play(w.open);
          await ctx.play(w.dragTo(0)); await ctx.wait(0.5);
          const away = s.mint.moveTo(...POS.switchboard.away, { speed: 520 });
          await ctx.play(gsap.timeline().add(away, 0));
          await ctx.play(w.close()); hud.toast('Task reset: no credit', 'error', 2.6); s.st.set('idle'); hud.setBtn('use', false); await ctx.wait(1.2);
        });
      } },
    { label: 'Wiring mini-game completed',
      async run(ctx) {
        const s = ctx.state, hud = ctx.hud;
        ctx.caption('Back at the station: wiring mini-game. Drag each plug to the jack of the same colour.');
        await ctx.play(s.mint.moveTo(...POS.switchboard.spot, { speed: 420 })); s.st.set('highlight');
        await useAt(ctx, async () => {
          const w = createWiring(ctx.L.modal); s.w = w; await ctx.play(w.open);
          await ctx.interactive({ sec: 10, label: 'auto-play', setup: (done) => w.solved.then(done), auto: async () => { await w.auto((tl) => ctx.play(tl)); await ctx.wait(0.7); } });
          await ctx.play(w.close()); s.st.set('done'); hud.setBtn('use', false);
        });
        hud.completeTask('switch'); s.tasks[1].done = true; hud.toast('SERVER CONFIRMED: Patch the Switchboard', 'ok', 2.6);
        ctx.caption('Confirmed tasks stay ticked off for you, and the shared bar moves again.');
        await ctx.wait(0.9); hud.setBar(72, true); await ctx.wait(1.5);
      } },
  ],
};
