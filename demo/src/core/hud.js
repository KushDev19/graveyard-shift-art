import gsap from 'gsap';
import { A, el, img } from './util.js';

const BTN = { use: 'btn_use', report: 'btn_report', eliminate: 'btn_eliminate' };
const LABEL = { use: 'USE', report: 'REPORT', eliminate: 'ELIMINATE' };

export class Hud {
  constructor(layer) {
    this.root = el('div', 'hud', layer); gsap.set(this.root, { autoAlpha: 0 });
    // ---- top-left: team bar + task list
    this.left = el('div', 'hud-left', this.root);
    const bar = el('div', 'teambar', this.left);
    el('div', 'teambar-label', bar, 'TEAM TASKS');
    this.pct = el('div', 'teambar-pct', bar, '0%');
    const trough = el('div', 'teambar-trough', bar); img(A('ui/progress_trough.svg'), 'trough-img', trough);
    this.fillClip = el('div', 'teambar-fill', trough); img(A('ui/progress_fill.svg'), '', this.fillClip);
    this.tasksPanel = el('div', 'taskpanel', this.left);
    el('div', 'taskpanel-title', this.tasksPanel, 'TASK LIST');
    this.list = el('div', 'tasklist', this.tasksPanel);
    // ---- top-right: meetings left
    this.meet = el('div', 'meetleft', this.root);
    img(A('ui/icons/btn_emergency.svg'), 'meetleft-ico', this.meet);
    const mt = el('div', 'meetleft-t', this.meet); el('div', 'meetleft-k', mt, 'MEETINGS LEFT');
    this.meetN = el('div', 'meetleft-n', mt, '1');
    // ---- bottom-right: actions
    this.actions = el('div', 'actions', this.root);
    this.btn = {};
    for (const k of ['use', 'report', 'eliminate']) this.makeBtn(k);
    this.toasts = el('div', 'toasts', layer);
    this.tasks = []; this.pctVal = 0; this.handlers = {};
  }
  makeBtn(k) {
    const b = el('button', 'abtn off ' + k, this.actions);
    const im = img(A(`ui/icons/${BTN[k]}_disabled.svg`), 'abtn-img', b);
    const glow = el('div', 'abtn-glow', b);
    const cd = el('div', 'abtn-cd', b); cd.innerHTML = `<svg viewBox="0 0 256 256"><circle cx="128" cy="128" r="100" class="cd-track"/><circle cx="128" cy="128" r="100" class="cd-arc" transform="rotate(-90 128 128)"/></svg><span class="cd-num"></span>`;
    el('div', 'abtn-label', b, LABEL[k]);
    b.addEventListener('click', () => this.handlers[k]?.(b.classList.contains('off')));
    this.btn[k] = { b, im, cd, glow, on: false, cooling: false };
    if (k === 'eliminate') b.style.display = 'none';
  }
  onClick(k, fn) { this.handlers[k] = fn; }
  show(opts = {}) {
    this.btn.eliminate.b.style.display = opts.impostor ? '' : 'none';
    gsap.to(this.root, { autoAlpha: 1, duration: 0.4, overwrite: true });
  }
  hide() { gsap.to(this.root, { autoAlpha: 0, duration: 0.25, overwrite: true }); }
  showMeetings(on = true) { gsap.set(this.meet, { display: on ? 'flex' : 'none' }); }
  setMeetings(n) { this.meetN.textContent = n; gsap.fromTo(this.meetN, { scale: 1.8 }, { scale: 1, duration: 0.5, ease: 'back.out(3)' }); }
  setTasks(list) {
    this.tasks = list; this.list.innerHTML = '';
    for (const t of list) {
      const r = el('div', 'task' + (t.done ? ' done' : ''), this.list); r.dataset.id = t.id;
      el('span', 'task-box', r); const tx = el('span', 'task-text', r); tx.innerHTML = `${t.text}<em>${t.room}</em>`;
    }
  }
  completeTask(id) {
    const r = this.list.querySelector(`[data-id="${id}"]`); if (!r) return;
    r.classList.add('done');
    gsap.fromTo(r, { scale: 1.06 }, { scale: 1, duration: 0.5, ease: 'back.out(3)' });
    const t = this.tasks.find((x) => x.id === id); if (t) t.done = true;
  }
  setBar(pct, animate = true) {
    const o = { v: this.pctVal }; const self = this;
    gsap.killTweensOf(o); gsap.to(o, { v: pct, duration: animate ? 1.1 : 0, ease: 'power3.out', onUpdate() { self.paintBar(o.v); }, onComplete() { self.pctVal = pct; self.paintBar(pct); } });
    this.pctVal = pct;
    if (animate) gsap.fromTo(this.fillClip.parentNode, { scale: 1.04 }, { scale: 1, duration: 0.6, ease: 'elastic.out(1,0.4)', delay: 0.9 });
  }
  paintBar(v) { this.fillClip.style.width = `${Math.max(0, Math.min(100, v)) * 0.95}%`; this.pct.textContent = Math.round(v) + '%'; }
  setBtn(k, on) {
    const B = this.btn[k]; if (B.on === on) return; B.on = on;
    B.b.classList.toggle('off', !on); B.im.src = A(`ui/icons/${BTN[k]}${on ? '' : '_disabled'}.svg`);
    if (on) gsap.fromTo(B.b, { scale: 0.85 }, { scale: 1, duration: 0.45, ease: 'back.out(3)' });
  }
  cooldown(k, sec) {
    const B = this.btn[k]; B.cooling = true; B.b.classList.add('cooling');
    const arc = B.cd.querySelector('.cd-arc'), num = B.cd.querySelector('.cd-num'); const C = 628.32;
    arc.setAttribute('stroke-dasharray', `${C} ${C}`);
    const o = { p: 0 }; this.setBtn(k, false);
    return gsap.to(o, { p: 1, duration: sec, ease: 'none',
      onUpdate: () => { arc.setAttribute('stroke-dashoffset', C * o.p); num.textContent = Math.ceil(sec * (1 - o.p)); },
      onComplete: () => { B.cooling = false; B.b.classList.remove('cooling'); } });
  }
  press(k) { const b = this.btn[k].b; return gsap.fromTo(b, { scale: 0.9 }, { scale: 1, duration: 0.4, ease: 'elastic.out(1,0.4)' }); }
  toast(text, kind = 'info', sec = 2.2) {
    if (this.ctx?.instant) return null;
    const t = el('div', 'toast ' + kind, this.toasts); t.textContent = text;
    gsap.timeline().fromTo(t, { y: -30, autoAlpha: 0, scale: 0.9 }, { y: 0, autoAlpha: 1, scale: 1, duration: 0.4, ease: 'back.out(2.4)' })
      .to(t, { autoAlpha: 0, y: -16, duration: 0.3, delay: sec, onComplete: () => t.remove() });
    return t;
  }
}
