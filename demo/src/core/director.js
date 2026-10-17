import gsap from 'gsap';
import { A, el, img } from './util.js';
import { startMusic, toggleMusic } from './music.js';

/** Runs scenes -> steps. A step is {label, run(ctx), hold?}. Pressing next while a step runs finishes it instantly, then starts the next. */
export class Director {
  constructor(ctx, scenes) {
    this.ctx = ctx; this.scenes = scenes; this.si = -1; this.step = 0; this.busy = false; this.pending = 0; this.auto = false; this.gen = 0;
    ctx.director = this;
    this.buildChrome();
    addEventListener('keydown', (e) => this.key(e));
  }
  // ---------- chrome (chapter bar, notes)
  buildChrome() {
    const L = this.ctx.L.present;
    this.bar = el('div', 'chapters', L);
    this.pips = []; let last = null;
    this.scenes.forEach((s, i) => {
      if (s.chapter !== last) { last = s.chapter; const c = el('div', 'chap', this.bar); el('b', '', c, s.chapter); this.group = c; }
      const p = el('div', 'pip', this.group); p.title = s.title; p.addEventListener('click', () => this.goto(i)); p.style.cursor = 'pointer'; p.style.pointerEvents = 'auto'; this.pips.push(p);
    });
    this.nowEl = el('div', 'now', this.bar); this.bar.style.pointerEvents = 'none';
    this.hintEl = el('div', 'hint', this.bar, '→ next · ← back · P notes · C captions · M music');
    this.bar.style.pointerEvents = 'auto';
    this.notes = el('div', 'notes', L); gsap.set(this.notes, { autoAlpha: 0 });
  }
  paintChrome() {
    const s = this.scenes[this.si];
    this.pips.forEach((p, i) => { p.classList.toggle('on', i === this.si); p.classList.toggle('done', i < this.si); });
    this.nowEl.textContent = `${this.si}. ${s.title.toUpperCase()}  ·  beat ${Math.min(this.step + 1, s.steps.length)}/${s.steps.length}`;
    this.notes.innerHTML = `<h2>${this.si}. ${s.title}</h2><div class="story">${s.story}</div><ul>${s.criteria.map((c) => { const m = c.match(/^\[(.*?)\]\s*(.*)$/); return `<li>${m ? `<i>${m[1]}</i>${m[2]}` : c}</li>`; }).join('')}</ul><div class="keys">P close · C captions · M music · R restart scene · 1-9 jump · 0 title · W win · I impostors win · A autoplay</div>`;
  }
  key(e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key; document.activeElement?.blur?.(); startMusic();
    if (k === 'ArrowRight' || k === ' ' || k === 'Enter' || k === 'PageDown') { e.preventDefault(); this.next(); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); this.prev(); }
    else if (/^[0-9]$/.test(k)) this.goto(parseInt(k, 10));
    else if (k === 'w' || k === 'W') { this.ctx.winMode = 'crew'; this.goto(10); }
    else if (k === 'i' || k === 'I') { this.ctx.winMode = 'imp'; this.goto(10); }
    else if (k === 's' || k === 'S') this.goto(11);
    else if (k === 'p' || k === 'P') this.toggleNotes();
    else if (k === 'c' || k === 'C') { const on = this.ctx.captions.toggle(); this.ctx.hud.toast(on ? 'Captions on' : 'Captions off', 'info', 1); }
    else if (k === 'r' || k === 'R') this.goto(this.si);
    else if (k === 'a' || k === 'A') { this.auto = !this.auto; this.ctx.hud.toast(this.auto ? 'Autoplay on' : 'Autoplay off', 'info', 1); if (this.auto && !this.busy) this.next(); }
    else if (k === 'm' || k === 'M') { const on = toggleMusic(); this.ctx.hud.toast(on ? 'Music on' : 'Music off', 'info', 1); }
    else if (k === 'f' || k === 'F') { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.(); }
  }
  toggleNotes() { this.notesOpen = !this.notesOpen; const on = this.notesOpen; gsap.to(this.notes, { autoAlpha: on ? 1 : 0, y: on ? 0 : 20, duration: 0.25, overwrite: true }); }

  // ---------- navigation
  async start(i = 0) { await this.goto(i); }
  async goto(si, stepTarget = 0) {
    si = Math.max(0, Math.min(this.scenes.length - 1, si)); const my = ++this.gen;
    const ctx = this.ctx; ctx.killAll(); this.busy = true; this.pending = 0;
    const same = si === this.si && stepTarget === 0;
    await new Promise((r) => gsap.to(ctx.cover, { opacity: 1, duration: same ? 0.18 : 0.22, ease: 'power2.in', onComplete: r }));
    if (my !== this.gen) return;
    this.si = si; this.step = 0; ctx.resetWorld(); const s = this.scenes[si];
    ctx.instant = stepTarget > 0; ctx.sceneGen = my;
    try { await s.enter(ctx); for (let i = 0; i < stepTarget; i++) { await s.steps[i].run(ctx); if (my !== this.gen) return; this.step = i + 1; } } catch (err) { console.error('scene enter/replay failed', err); }
    ctx.instant = false;
    this.paintChrome();
    gsap.to(ctx.cover, { opacity: 0, duration: 0.3, ease: 'power2.out' });
    this.busy = false;
    if (stepTarget === 0 && s.autoStart) this.next();
    else if (this.auto) this.scheduleAuto();
  }
  async next() {
    const ctx = this.ctx;
    if (this.busy) { this.pending++; ctx.finishActive(); return; }
    const s = this.scenes[this.si];
    if (this.step >= s.steps.length) { if (this.si < this.scenes.length - 1) this.goto(this.si + 1); return; }
    this.busy = true; const my = this.gen; const st = s.steps[this.step];
    ctx.captions.set(null);
    try { await st.run(ctx); } catch (err) { console.error('step failed', st.label, err); }
    if (my !== this.gen) return;
    this.step++; this.busy = false; this.paintChrome();
    if (this.pending > 0) { this.pending--; this.next(); }
    else if (this.auto) this.scheduleAuto();
  }
  scheduleAuto() { const s = this.scenes[this.si]; const st = s.steps[Math.min(this.step, s.steps.length - 1)]; clearTimeout(this.autoT); this.autoT = setTimeout(() => { if (this.auto && !this.busy) this.next(); }, (st?.hold ?? 1.6) * 1000); }
  prev() {
    if (this.step > 0) this.goto(this.si, this.step - 1);
    else if (this.si > 0) this.goto(this.si - 1, 0);
  }
}
