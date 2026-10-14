import gsap from 'gsap';
import { A, el, img } from './util.js';

const R = { base: [109, 309, 442, 221], off: [246, 350, 168, 66], on: [123, 225, 414, 282], bright: [79, 195, 491, 335], btn: [260, 319, 140, 95], pressed: [260, 333, 140, 81], pad: [425, 404, 74, 103], domeB: [22, 31, 469, 401], domeF: [18, 27, 470, 409] };
const place = (e, [x, y, w, h]) => Object.assign(e.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px' });

/** Animated emergency button (job E rig) built from png parts. x,y = stage px where the base top-centre should land. */
export class EmergencyButton {
  constructor(parent, x, y, sc = 0.5) {
    this.root = el('div', 'ebtn', parent); this.sc = sc;
    Object.assign(this.root.style, { left: x - 330 * sc + 'px', top: y - 380 * sc + 'px', transform: `scale(${sc})`, transformOrigin: '0 0' });
    const P = (n, rect, cls = '') => { const i = img(A(`button/${n}.png`), 'eb ' + cls, this.root); place(i, rect); return i; };
    this.base = P('base', R.base); this.gOff = P('glow_ring_off', R.off); this.gOn = P('glow_ring_on', R.on); this.gBright = P('glow_ring_bright', R.bright);
    this.flash = el('div', 'eb', this.root); this.flash.innerHTML = '<svg width="570" height="530" viewBox="0 0 570 530" style="overflow:visible"><ellipse class="f1" cx="330" cy="374" rx="90" ry="30" fill="none" stroke="#E8574A" stroke-width="16"/><ellipse class="f2" cx="330" cy="374" rx="90" ry="30" fill="none" stroke="#E8574A" stroke-width="16"/></svg>';
    this.f1 = this.flash.querySelector('.f1'); this.f2 = this.flash.querySelector('.f2'); gsap.set([this.f1, this.f2], { opacity: 0 });
    this.domeB = el('div', 'eb dome', this.root); place(this.domeB, R.domeB); this.domeB.style.backgroundImage = `url(${A('button/dome_back_strip.png')})`;
    this.btnI = P('button_idle', R.btn); this.btnL = P('button_lit', R.btn); this.btnP = P('button_pressed', R.pressed); this.btnD = P('button_disabled', R.btn);
    this.domeF = el('div', 'eb dome', this.root); place(this.domeF, R.domeF); this.domeF.style.backgroundImage = `url(${A('button/dome_front_strip.png')})`;
    this.pad = P('padlock', R.pad);
    for (const d of [this.domeB, this.domeF]) d.style.backgroundSize = `${13 * parseInt(d.style.width)}px 100%`;
    gsap.set([this.gOn, this.gBright, this.btnL, this.btnP, this.btnD, this.pad], { opacity: 0 }); gsap.set(this.gOff, { opacity: 1 });
    this.pad.style.zIndex = 8; this.flash.style.zIndex = 3; this.angle = 0; this.setAngle(0);
  }
  setAngle(a) {
    this.angle = a; const f = Math.max(0, Math.min(12, Math.round(a / 10)));
    for (const d of [this.domeB, this.domeF]) d.style.backgroundPositionX = `${-f * parseInt(d.style.width)}px`;
    const z = a > 30 ? { domeB: 5, domeF: 6, btn: 4 } : { domeB: 4, domeF: 7, btn: 6 };
    this.domeB.style.zIndex = z.domeB; this.domeF.style.zIndex = z.domeF; for (const b of [this.btnI, this.btnL, this.btnP, this.btnD]) b.style.zIndex = z.btn;
  }
  /** dome opens, lights up, slam, flash ring (job E timings) */
  slam() {
    const o = { a: 0 }, self = this; const tl = gsap.timeline();
    tl.to(o, { a: 110, duration: 0.65, ease: 'back.out(1.25)', onUpdate: () => self.setAngle(o.a) }, 0)
      .to(this.btnL, { opacity: 1, duration: 0.3 }, 0.2).to(this.btnI, { opacity: 0, duration: 0.3 }, 0.2)
      .to(this.gOn, { opacity: 1, duration: 0.35, ease: 'sine.inOut' }, 0.3).to(this.gOff, { opacity: 0, duration: 0.35 }, 0.3)
      .to([this.btnL, this.btnI], { y: 18, scaleX: 1.12, scaleY: 0.78, transformOrigin: '50% 100%', duration: 0.1, ease: 'cubic.in' }, 0.9)
      .set(this.btnP, { opacity: 1 }, 1.0).set([this.btnL, this.btnI], { opacity: 0, y: 0, scaleX: 1, scaleY: 1 }, 1.0)
      .to(this.gBright, { opacity: 1, duration: 0.1 }, 0.95).to(this.gOn, { opacity: 0, duration: 0.1 }, 0.95);
    for (const [f, d] of [[this.f1, 0.95], [this.f2, 1.07]]) {
      tl.set(f, { opacity: 1, attr: { rx: 90, ry: 30, 'stroke-width': 16 } }, d).to(f, { attr: { rx: 240, ry: 80.6, 'stroke-width': 4 }, opacity: 0, duration: 0.65, ease: 'power2.out' }, d);
    }
    tl.to(this.btnP, { opacity: 0, duration: 0.5 }, 1.9).to(this.btnD, { opacity: 1, duration: 0.5 }, 1.9).to(this.gBright, { opacity: 0, duration: 0.5 }, 1.9).to(this.gOff, { opacity: 0.6, duration: 0.5 }, 1.9)
      .to(o, { a: 0, duration: 0.45, ease: 'power2.inOut', onUpdate: () => self.setAngle(o.a) }, 2.1).to(this.pad, { opacity: 1, duration: 0.3 }, 2.5);
    this.tl = tl; return tl;
  }
  /** blocked press (no meetings left): padlock shake */
  denied() { return gsap.timeline().fromTo(this.root, { x: -10 }, { x: 0, duration: 0.5, ease: 'elastic.out(1.4,0.25)' }).fromTo(this.pad, { rotation: -14, transformOrigin: '50% 10%' }, { rotation: 0, duration: 0.6, ease: 'elastic.out(1.2,0.3)' }, 0); }
  glow(on) { return gsap.to(this.gOn, { opacity: on ? 0.9 : 0, duration: 0.3 }); }
}
