import gsap from 'gsap';
import { A, el, img, ROSTER, P } from '../core/util.js';
import { mk } from './common.js';
import { chip } from '../core/meeting.js';
import { createStation } from '../core/station.js';

const ARRIVE = [1010, 1050]; // bottom door (stage px)
const SPOT = { tangerine: [760, 760], mustard: [1130, 760], mint: [960, 860], lime: [600, 820], sky: [1360, 840], bubblegum: [1230, 900], tomato: [480, 900], cream: [1480, 770], cobalt: [820, 910], grape: [1600, 900] };

class Lobby {
  constructor(layer) {
    this.root = el('div', 'lobby', layer); this.ids = []; this.host = null;
    const head = el('div', 'lobby-head', this.root); el('b', '', head, 'LOBBY · NIGHTJAR'); this.count = el('span', '', head, '0/10');
    this.rows = el('div', 'lobby-rows', this.root);
    this.start = el('button', 'lobby-start off', this.root); this.startImg = img(A('ui/btn_pill_disabled.svg'), '', this.start); this.startLbl = el('span', '', this.start, 'START SHIFT');
    this.tip = el('div', 'lobby-tip', this.root, 'Only the host can start · needs 4+ crew'); gsap.set(this.tip, { autoAlpha: 0 });
    this.leave = el('button', 'lobby-leave', this.root); img(A('ui/icons/badge_leave.svg'), '', this.leave); el('span', '', this.leave, 'LEAVE');
    this.cursor = el('div', 'fakecursor', this.root); this.cursor.innerHTML = '<svg viewBox="0 0 24 32"><path d="M2 2 L2 24 L8 18 L12 28 L16 26 L12 17 L21 17 Z" fill="#F4E6C8" stroke="#2A1E35" stroke-width="2" stroke-linejoin="round"/></svg>'; gsap.set(this.cursor, { autoAlpha: 0, x: 1200, y: 700 });
  }
  paintCount() { this.count.textContent = `${this.ids.length}/10`; gsap.fromTo(this.count, { scale: 1.5 }, { scale: 1, duration: 0.4, ease: 'back.out(3)' }); }
  add(id, instant = false) {
    this.ids.push(id); const r = el('div', 'lobby-row', this.rows); r.dataset.id = id;
    r.appendChild(chip(P[id].color, 36)); el('span', 'lr-name', r, P[id].name); const cr = img(A('ui/icons/badge_host_crown.svg'), 'lr-crown', r); cr.style.display = 'none';
    if (id === 'mint') { el('em', '', r, 'YOU'); }
    if (!this.host) this.setHost(id, true);
    if (!instant) gsap.from(r, { x: -60, autoAlpha: 0, duration: 0.45, ease: 'back.out(2)' }); this.paintCount(); this.paintStart();
  }
  remove(id) { this.ids = this.ids.filter((x) => x !== id); const r = this.rows.querySelector(`[data-id="${id}"]`); if (r) gsap.to(r, { x: -60, autoAlpha: 0, height: 0, duration: 0.4, onComplete: () => r.remove() }); this.paintCount(); this.paintStart(); }
  setHost(id, silent) { this.host = id; this.rows.querySelectorAll('.lr-crown').forEach((c) => (c.style.display = 'none')); const c = this.rows.querySelector(`[data-id="${id}"] .lr-crown`); if (c) { c.style.display = ''; if (!silent) gsap.fromTo(c, { scale: 2.4, rotation: -30 }, { scale: 1, rotation: 0, duration: 0.6, ease: 'back.out(2.4)' }); } this.paintStart(); }
  paintStart() { const can = this.host === 'mint' && this.ids.length >= 4; this.start.classList.toggle('off', !can); this.startImg.src = A(`ui/btn_pill_${can ? 'idle' : 'disabled'}.svg`); this.tip.textContent = this.host !== 'mint' ? 'Only the host can start · needs 4+ crew' : 'Needs 4+ crew to start'; }
}

export default {
  id: 2, title: 'Locker Room lobby', chapter: 'US3',
  story: 'Inside the Nightjar lobby: crew arrive one by one, the first is host; only the host can start (4+); the crown moves if the host leaves; anyone can leave; the host starts the shift at the time clock.',
  criteria: [
    '[US3] Accepting the arcade prompt moves the player into the spaceship lobby; lobby holds 4 to 10.',
    '[US3] First to join is host; if the host leaves, the next player who joins becomes host.',
    '[US3] A player can leave the lobby before the game starts and return to town.',
    '[US3 error] Only the host can start, and only with at least 4 players.',
    '[US3] Players in the match and players in town cannot see or hear each other.',
  ],
  async enter(ctx) {
    const room = await ctx.room('locker'); const s = ctx.state = { room, pp: {} };
    const [cx, cy] = room.pt([4432, 1320]);
    s.clock = await createStation(room.sorted, 'timeclock', cx + 20, cy + 150, 250); s.clock.set('idle');
    // bulkhead door starts OPEN: assembled open art over the painted (closed) door, leaves slide shut later
    const O = (f, x, y, w, h, cls = '', parent = null) => room.obj(`rooms/obj/${f}`, x, y, w, h, { cls, parent });
    const open = img(A('rooms/obj/locker_door_open.svg'), 'room-obj'); room.fx.appendChild(open); Object.assign(open.style, { left: room.pt([952, 486])[0] + 'px', top: room.pt([952, 486])[1] + 'px', width: 912 * room.s + 'px', height: 893 * room.s + 'px' });
    const clip = el('div', 'door-clip', room.fx); const [kx, ky] = room.pt([1088, 700]); Object.assign(clip.style, { left: kx + 'px', top: ky + 'px', width: 648 * room.s + 'px', height: 636 * room.s + 'px' });
    const leaf = (f, x, w, dx) => { const i = img(A(`rooms/obj/${f}.svg`), 'room-obj', clip); Object.assign(i.style, { left: (x - 1088) * room.s + 'px', top: (698 - 700) * room.s + 'px', width: w * room.s + 'px', height: 641 * room.s + 'px' }); gsap.set(i, { x: dx * room.s }); return i; };
    s.leafL = leaf('locker_door_leaf_left', 1086, 321, -321); s.leafR = leaf('locker_door_leaf_right', 1403, 336, 336);
    const frame = img(A('rooms/obj/locker_door_frame.svg'), 'room-obj', room.fx); Object.assign(frame.style, { left: room.pt([952, 486])[0] + 'px', top: room.pt([952, 486])[1] + 'px', width: 912 * room.s + 'px', height: 893 * room.s + 'px' });
    // beacon: rotating warm cone (idle = slow, shift start = fast)
    const [bx, by] = room.pt([1405, 450]); s.beacon = el('div', 'beacon', room.fx); Object.assign(s.beacon.style, { left: bx - 220 + 'px', top: by - 220 + 'px' }); s.beaconTw = gsap.to(s.beacon, { rotation: 360, duration: 6, ease: 'none', repeat: -1 }); gsap.set(s.beacon, { opacity: 0.0 });
    s.lobby = new Lobby(ctx.L.modal); s.lobby.root.style.pointerEvents = 'none'; s.lobby.start.style.pointerEvents = 'auto'; s.lobby.leave.style.pointerEvents = 'auto';
    for (const id of ['tangerine', 'mustard', 'mint']) { const p = mk(id); room.add(p, ...SPOT[id]); s.pp[id] = p; s.lobby.add(id, true); }
    s.pp.mint.showName(); s.pp.tangerine.setFacing(-1);
    ctx.caption('Inside the Nightjar lobby. First to clock in is the host.');
  },
  steps: [
    { label: 'Crew clock in (3/10 → 6/10), host crown',
      async run(ctx) {
        const s = ctx.state, L = s.lobby;
        ctx.caption('The lobby holds 4 to 10. The first to clock in (Tangerine) is host.');
        const tl = gsap.timeline();
        ['lime', 'sky', 'bubblegum'].forEach((id, n) => {
          const p = mk(id); s.pp[id] = p; s.room.add(p, ...ARRIVE); gsap.set(p.root, { autoAlpha: 0 });
          tl.set(p.root, { autoAlpha: 1 }, n * 1.0).add(p.moveTo(...SPOT[id], { speed: 330 }), n * 1.0).call(() => L.add(id), null, n * 1.0 + 0.3);
        });
        await ctx.play(tl); await ctx.wait(0.4);
      } },
    { label: 'Non-host hovers Start → disabled',
      async run(ctx) {
        const s = ctx.state, L = s.lobby;
        ctx.caption('Error case: only the host can start, and only with 4+ players. Mint is not the host.');
        const r = L.start.getBoundingClientRect(); const st = ctx.stage; const sc = st.scale(); const b = st.stage.getBoundingClientRect();
        const tx = (r.left - b.left) / sc + 90, ty = (r.top - b.top) / sc + 30;
        const tl = gsap.timeline().set(L.cursor, { autoAlpha: 1, x: 1100, y: 600 }).to(L.cursor, { x: tx, y: ty, duration: 0.9, ease: 'power3.inOut' })
          .fromTo(L.start, { x: -10 }, { x: 0, duration: 0.5, ease: 'elastic.out(1.4,0.25)' }).to(L.tip, { autoAlpha: 1, y: 0, duration: 0.3 }, '<')
          .call(() => ctx.hud.toast('Only the host can start the shift', 'error', 2.2), null, '<');
        await ctx.play(tl); await ctx.wait(1.6); await ctx.play(gsap.timeline().to(L.tip, { autoAlpha: 0, duration: 0.25 }).to(L.cursor, { autoAlpha: 0, duration: 0.2 }, 0));
      } },
    { label: 'Edge: host leaves → crown passes on',
      async run(ctx) {
        const s = ctx.state, L = s.lobby;
        ctx.caption('Edge case: the host leaves, so the crown passes to the next player.');
        const t = s.pp.tangerine; const tl = gsap.timeline();
        tl.add(t.moveTo(...ARRIVE, { speed: 380 })).to(t.root, { autoAlpha: 0, duration: 0.25 }).call(() => { L.remove('tangerine'); ctx.hud.toast('Tangerine left · Mustard is the new host', 'info', 2.6); }, null, '>-0.1')
          .call(() => L.setHost('mustard'), null, '>+0.45');
        await ctx.play(tl); await ctx.wait(1.1);
      } },
    { label: 'Edge: a player leaves → back to town',
      async run(ctx) {
        const s = ctx.state, L = s.lobby;
        ctx.caption('A player can leave before the game starts and go back to the town.');
        const sky = s.pp.sky; const r = L.leave.getBoundingClientRect();
        const tl = gsap.timeline().add(gsap.fromTo(L.leave, { scale: 1.2 }, { scale: 1, duration: 0.4, ease: 'back.out(3)' }), 0).add(sky.moveTo(...ARRIVE, { speed: 420 }), 0.2).to(sky.root, { autoAlpha: 0, duration: 0.25 })
          .call(() => { L.remove('sky'); ctx.hud.toast('Sky left the lobby · back in town', 'info', 2.4); });
        await ctx.play(tl); await ctx.wait(0.8);
      } },
    { label: 'Crew refills; host starts the shift at the time clock',
      async run(ctx) {
        const s = ctx.state, L = s.lobby;
        ctx.caption('More crew clock in (7/10). Now the host presses the time clock to start the shift.');
        const tl = gsap.timeline();
        ['tomato', 'cream', 'cobalt', 'grape'].forEach((id, n) => { const p = mk(id); s.pp[id] = p; s.room.add(p, ...ARRIVE); gsap.set(p.root, { autoAlpha: 0 });
          tl.set(p.root, { autoAlpha: 1 }, n * 0.55).add(p.moveTo(...SPOT[id], { speed: 460 }), n * 0.55).call(() => L.add(id), null, n * 0.55 + 0.2); });
        await ctx.play(tl); await ctx.wait(0.3);
        const m = s.pp.mustard; const [cx, cy] = s.room.pt([4432, 1320]);
        await ctx.play(m.moveTo(cx - 40, cy + 215, { speed: 520 })); s.clock.set('ready');
        L.start.classList.remove('off'); L.startImg.src = A('ui/btn_pill_idle.svg'); await ctx.wait(0.5);
        await ctx.play(gsap.timeline().add(() => m.doHop()).fromTo(L.start, { scale: 0.92 }, { scale: 1, duration: 0.4, ease: 'back.out(3)' }));
        ctx.hud.toast('SHIFT STARTING', 'ok', 2.4);
        const tl2 = gsap.timeline().set(s.beacon, { opacity: 1 }).to(s.beaconTw, { timeScale: 5, duration: 0.5 }, 0)
          .to(s.leafL, { x: 0, duration: 1.3, ease: 'power3.inOut' }, 0.2).to(s.leafR, { x: 0, duration: 1.3, ease: 'power3.inOut' }, 0.2)
          .call(() => ctx.flash('#F5A54A', 0.5), null, 1.4);
        await ctx.play(tl2); await ctx.wait(0.7);
      } },
  ],
};
