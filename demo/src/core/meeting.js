import gsap from 'gsap';
import { A, el, img, PAL, fmtTime, COLORS } from './util.js';
import { makePortrait, suitVars } from './puppet.js';

const K = 1.5; // 1280x720 tablet art -> 1920x1080 stage
const SLOTS = [[88, 140], [640, 140], [88, 225], [640, 225], [88, 310], [640, 310], [88, 395], [640, 395], [88, 480], [640, 480]];
let helmetSvg = '';
export async function preloadMeeting() { helmetSvg = await fetch(A('ui/icons/icon_helmet_front.svg')).then((r) => r.text()); }
export const chip = (color, size = 44) => { const d = el('div', 'chip'); d.innerHTML = helmetSvg; d.style.cssText = `width:${size}px;height:${size}px;${suitVars(COLORS[color])}`; return d; };

/** The Meeting Tablet: plates, discussion + voting timers, two-step vote, voter chips, outcome banner. */
export class MeetingTablet {
  constructor(layer, { players, you, notify }) {
    this.players = players; this.you = you; this.notify = notify || (() => {});
    this.root = el('div', 'tablet', layer); gsap.set(this.root, { yPercent: 100 });
    img(A('ui/tablet_frame.svg'), 'tab-frame', this.root);
    const title = img(A('ui/tablet_title.svg'), 'tab-title', this.root); Object.assign(title.style, { left: 320 * K + 'px', top: 58 * K + 'px', width: 640 * K + 'px' });
    this.sys = el('div', 'tab-sys', this.root, 'NIGHTJAR COMMS // MTG 03<br>BODY: SWITCHBOARD');
    this.callerLine = el('div', 'tab-caller', this.root);
    const chat = el('div', 'tab-chat', this.root); img(A('ui/chat_button.svg'), '', chat); img(A('ui/chat_unread_dot.svg'), 'tab-dot', chat);
    this.plates = {};
    this.players.forEach((p, i) => this.makePlate(p, i));
    // skip
    this.skip = el('button', 'tab-skip', this.root); this.skipImg = img(A('ui/btn_pill_disabled.svg'), '', this.skip); this.skipLbl = el('span', '', this.skip, 'SKIP VOTE');
    this.skipBtns = el('div', 'tab-skipbtns', this.root); this.skipChips = el('div', 'tab-skipchips', this.root);
    this.hint = el('div', 'tab-hint', this.root, 'DISCUSS: TALK IT OUT');
    // timer
    this.timerBox = el('div', 'tab-timer', this.root);
    this.timerLbl = el('div', 'tab-timer-lbl', this.timerBox, 'DISCUSS'); this.timerTxt = el('div', 'tab-timer-t', this.timerBox, '0:15');
    this.dial = el('div', 'tab-dial', this.root);
    img(A('ui/timer_dial_ring.svg'), '', this.dial);
    this.dial.insertAdjacentHTML('beforeend', `<svg viewBox="0 0 112 112" class="dial-arc"><circle cx="56" cy="56" r="37" fill="none" stroke-width="8" stroke-linecap="round" transform="rotate(-90 56 56)"/></svg>`);
    this.arc = this.dial.querySelector('circle'); img(A('ui/timer_dial_center.svg'), '', this.dial);
    this.setArc(1, PAL.seafoam);
    this.banner = el('div', 'tab-banner', this.root); gsap.set(this.banner, { autoAlpha: 0 });
    this.phase = 'idle'; this.selected = null; this.locked = false; this.myVote = null; this.voted = new Set(); this.skipSel = false;
    this.skip.addEventListener('click', () => this.clickTarget('skip'));
  }
  makePlate(p, i) {
    const [sx, sy] = SLOTS[i];
    const d = el('div', 'plate', this.root); d.style.left = sx * K + 'px'; d.style.top = sy * K + 'px';
    const art = img(A('ui/plate_alive.svg'), 'plate-art', d);
    const por = makePortrait(p.color, p.cos || {}, 78); por.el.classList.add('plate-por'); d.appendChild(por.el);
    const nm = el('div', 'plate-name', d, p.name); const sub = el('div', 'plate-sub', d);
    const status = el('div', 'plate-status', d); const badge = img(A('ui/icons/badge_caller.svg'), 'plate-badge', d); badge.style.display = 'none';
    const xTape = img(A('ui/icons/badge_eliminated.svg'), 'plate-x', d); xTape.style.display = 'none';
    const lamp = el('div', 'plate-lamp', d);
    const btns = el('div', 'plate-btns', d);
    const bc = img(A('ui/btn_vote_cancel.svg'), 'pbtn', btns), bo = img(A('ui/btn_vote_confirm.svg'), 'pbtn', btns);
    bc.addEventListener('click', (e) => { e.stopPropagation(); this.deselect(); });
    bo.addEventListener('click', (e) => { e.stopPropagation(); this.confirm(); });
    d.addEventListener('click', () => this.clickTarget(p.id));
    this.plates[p.id] = { p, d, art, por, nm, sub, status, badge, xTape, lamp, btns, chips: el('div', 'plate-chips', d), state: { eliminated: false, caller: false, voted: false, disconnected: false } };
  }
  paint(id) {
    const P = this.plates[id], s = P.state, sel = this.selected === id;
    const base = s.disconnected ? 'disconnected' : s.eliminated ? 'eliminated' : sel ? 'selected' : id === this.you ? 'you' : s.voted ? 'voted' : s.caller ? 'caller' : 'alive';
    const url = A(`ui/plate_${base}.svg`); if (P.art.getAttribute('src') !== url) P.art.src = url;
    P.d.classList.toggle('dead', s.eliminated || s.disconnected);
    P.nm.classList.toggle('struck', s.eliminated);
    P.sub.textContent = s.disconnected ? 'DISCONNECTED' : s.eliminated ? (this.foundIn || 'FOUND IN SWITCHBOARD') : sel ? 'YOUR PICK?' : id === this.you ? (s.caller ? 'YOU · CALLER' : 'YOU') : s.caller ? (this.callerRole || 'CALLER') : '';
    P.badge.style.display = s.caller ? '' : 'none'; P.xTape.style.display = s.eliminated ? '' : 'none';
    P.lamp.style.display = s.voted ? '' : 'none';
    P.btns.style.display = sel ? 'flex' : 'none';
    if (s.voted && !P.status.querySelector('.stamp')) { const st = el('div', 'stamp', P.status, 'VOTED'); gsap.fromTo(st, { scale: 2.4, rotation: -20, autoAlpha: 0 }, { scale: 1, rotation: -6, autoAlpha: 1, duration: 0.35, ease: 'back.out(2)' }); }
    if (!s.voted) P.status.querySelector('.stamp')?.remove();
  }
  paintAll() { for (const id in this.plates) this.paint(id); }
  setCaller(id, reportedName) {
    for (const k in this.plates) this.plates[k].state.caller = k === id;
    const who = this.plates[id].p.name, col = (n) => COLORS[Object.values(this.players).find((q) => q.name === n)?.color] || '#fff';
    this.callerLine.innerHTML = reportedName
      ? `<span style="color:${PAL.seafoam}">${who}</span> reported <span style="color:${col(reportedName)}">${reportedName}</span>`
      : `<span style="color:${PAL.seafoam}">${who}</span> called an <span style="color:${PAL.coral}">emergency meeting</span>`;
    this.callerRole = reportedName ? 'REPORTER' : 'CALLER';
    this.foundIn = 'FOUND IN SWITCHBOARD';
    this.sys.innerHTML = reportedName ? 'NIGHTJAR COMMS // MTG 03<br>BODY: SWITCHBOARD' : 'NIGHTJAR COMMS // MTG 04<br>EMERGENCY TABLE';
    this.paintAll();
  }
  setEliminated(ids) { for (const k in this.plates) this.plates[k].state.eliminated = ids.includes(k); this.paintAll(); }
  reset() { // fresh round: keep eliminated + caller, clear votes
    this.phase = 'idle'; this.selected = null; this.locked = false; this.myVote = null; this.voted.clear(); this.skipSel = false;
    for (const k in this.plates) { const P = this.plates[k]; P.state.voted = false; P.chips.innerHTML = ''; }
    this.skipChips.innerHTML = ''; this.skipBtns.innerHTML = ''; gsap.set(this.banner, { autoAlpha: 0 });
    this.paintAll(); this.setSkip(false);
  }
  setSkip(on) { this.skipImg.src = A(`ui/btn_pill_${on ? 'idle' : 'disabled'}.svg`); this.skip.classList.toggle('off', !on); }
  open() { return gsap.to(this.root, { yPercent: 0, duration: 0.65, ease: 'back.out(1.15)' }); }
  close() { return gsap.to(this.root, { yPercent: 100, duration: 0.45, ease: 'power3.in' }); }

  // ---- phases & timers
  setArc(frac, color) { const C = 2 * Math.PI * 37; this.arc.setAttribute('stroke', color); this.arc.setAttribute('stroke-dasharray', `${C * frac} ${C}`); }
  startTimer(kind, shownSec, realSec) {
    this.phase = kind; const total = shownSec; this.timerLbl.textContent = kind === 'discuss' ? 'DISCUSS' : 'VOTING';
    if (kind === 'discuss') { this.setSkip(false); this.hint.textContent = 'DISCUSS: VOTING OPENS WHEN THE TIMER ENDS'; this.paintAll(); }
    else { this.setSkip(!this.locked); this.hint.textContent = this.locked ? 'VOTE LOCKED: WAITING FOR THE CREW' : 'PICK A PLATE TO VOTE, OR SKIP'; }
    const o = { t: total }; this.timerObj = o; const self = this;
    return gsap.to(o, { t: 0, duration: realSec, ease: 'none',
      onUpdate() { self.timerTxt.textContent = fmtTime(Math.max(0, o.t)); const f = o.t / total; self.setArc(Math.max(0.001, f), kind === 'discuss' ? PAL.seafoam : o.t <= 10 ? PAL.coral : PAL.amber); self.timerTxt.classList.toggle('hot', kind === 'vote' && o.t <= 10); } });
  }
  stopTimer() { if (this.timerObj) gsap.killTweensOf(this.timerObj); }

  // ---- voting
  clickTarget(id) {
    if (this.phase === 'discuss') { this.notify('Voting opens after the discussion', 'error'); gsap.fromTo(this.plates[id]?.d || this.skip, { x: -8 }, { x: 0, duration: 0.4, ease: 'elastic.out(1.2,0.3)' }); return; }
    if (this.phase !== 'vote') return;
    const dead = id !== 'skip' && (this.plates[id].state.eliminated || this.plates[id].state.disconnected);
    if (dead) { this.notify("Can't vote for an eliminated player", 'error'); return; }
    if (this.locked) { this.notify('Vote locked', 'error'); gsap.fromTo(this.tabEl(id), { x: -10 }, { x: 0, duration: 0.45, ease: 'elastic.out(1.2,0.3)' }); return; }
    this.select(id);
  }
  tabEl(id) { return id === 'skip' ? this.skip : this.plates[id].d; }
  select(id) {
    const prev = this.selected; this.selected = id; if (prev && prev !== 'skip') this.paint(prev);
    this.skipBtns.innerHTML = '';
    if (id === 'skip') this.mountSkipButtons(); else this.paint(id);
    gsap.fromTo(this.tabEl(id), { scale: 1.03 }, { scale: 1, duration: 0.35, ease: 'back.out(3)' });
  }
  mountSkipButtons() {
    const bc = img(A('ui/btn_vote_cancel.svg'), 'pbtn', this.skipBtns), bo = img(A('ui/btn_vote_confirm.svg'), 'pbtn', this.skipBtns);
    bc.addEventListener('click', () => this.deselect()); bo.addEventListener('click', () => this.confirm());
    gsap.from(this.skipBtns.children, { scale: 0, stagger: 0.08, ease: 'back.out(3)', duration: 0.3 });
  }
  deselect() { const p = this.selected; this.selected = null; this.skipBtns.innerHTML = ''; if (p && p !== 'skip') this.paint(p); }
  confirm() {
    if (!this.selected || this.locked) return;
    this.locked = true; this.myVote = this.selected; const id = this.selected; this.selected = null; this.skipBtns.innerHTML = '';
    if (id !== 'skip') this.paint(id);
    this.markVoted(this.you); this.setSkip(false); this.hint.textContent = 'VOTE LOCKED: WAITING FOR THE CREW';
    this.onVote?.(id);
  }
  /** programmatic vote (used by the auto-complete fallback and for stage-managed votes) */
  autoVote(id) { if (this.locked) return Promise.resolve(); this.select(id); return gsap.timeline().add(() => this.confirm(), '+=0.7'); }
  markVoted(id) { this.plates[id].state.voted = true; this.voted.add(id); this.paint(id); }

  // ---- results
  reveal(votes) { // votes: { voterId: targetId | 'skip' | null }
    this.phase = 'results'; this.hint.textContent = 'VOTES ARE IN'; this.setSkip(false);
    for (const k in this.plates) { const st = this.plates[k].status.querySelector('.stamp'); if (st) gsap.to(st, { autoAlpha: 0, scale: 0.6, duration: 0.25, onComplete: () => st.remove() }); this.plates[k].state.voted = false; this.plates[k].lamp.style.display = 'none'; }
    const tl = gsap.timeline(); const tally = {};
    for (const [voter, tgt] of Object.entries(votes)) {
      if (!tgt) continue; tally[tgt] = (tally[tgt] || 0) + 1;
      const host = tgt === 'skip' ? this.skipChips : this.plates[tgt].chips; const c = chip(this.plates[voter].p.color, tgt === 'skip' ? 54 : 58); host.appendChild(c);
      tl.fromTo(c, { scale: 0, y: -24 }, { scale: 1, y: 0, duration: 0.35, ease: 'back.out(3)' }, '>-0.1');
    }
    this.tally = tally; return tl;
  }
  showBanner(text, sub, tone = 'amber') {
    this.banner.className = 'tab-banner ' + tone; this.banner.innerHTML = `<b>${text}</b><span>${sub || ''}</span>`;
    return gsap.fromTo(this.banner, { autoAlpha: 0, scale: 0.7, y: 40 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.5, ease: 'back.out(2)' });
  }
  hideBanner() { return gsap.to(this.banner, { autoAlpha: 0, duration: 0.25 }); }
}
