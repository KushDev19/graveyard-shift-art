import gsap from 'gsap';
import crewSvg from '../assets/crew_puppet.svg?raw';
import { COLORS, el, cosDB } from './util.js';

const SIDE = ['leg_back', 'arm_back', 'leg_front', 'backpack', 'body', 'stripe', 'dome', 'visor_glow', 'visor', 'glass_highlight', 'collar', 'antenna', 'arm_front'];
const FRONT = ['f_leg_l', 'f_leg_r', 'f_body', 'f_stripe', 'f_dome', 'f_visor_glow', 'f_visor', 'f_collar', 'f_antenna', 'f_arm_l', 'f_arm_r'];
const VISORS = ['visor', 'visor_coral', 'visor_ghost', 'visor_blink', 'visor_surprised'];
const FALLEN = ['fallen_suit', 'fallen_fx', 'fallen_helmet'];
const PIV = {};
let uid = 0;

function hexToHsl(h) {
  const r = parseInt(h.slice(1, 3), 16) / 255, g = parseInt(h.slice(3, 5), 16) / 255, b = parseInt(h.slice(5, 7), 16) / 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let H = 0, S = 0; const L = (mx + mn) / 2;
  if (mx !== mn) { const d = mx - mn; S = L > 0.5 ? d / (2 - mx - mn) : d / (mx + mn); H = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; H /= 6; }
  return [H, S, L];
}
function hslToHex(H, S, L) {
  const f = (p, q, t) => { if (t < 0) t += 1; if (t > 1) t -= 1; if (t < 1 / 6) return p + (q - p) * 6 * t; if (t < 1 / 2) return q; if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6; return p; };
  let r, g, b; if (S === 0) { r = g = b = L; } else { const q = L < 0.5 ? L * (1 + S) : L + S - L * S, p = 2 * L - q; r = f(p, q, H + 1 / 3); g = f(p, q, H); b = f(p, q, H - 1 / 3); }
  return '#' + [r, g, b].map((x) => Math.round(x * 255).toString(16).padStart(2, '0')).join('');
}
const tone = (hex, f) => { const [h, s, l] = hexToHsl(hex); return hslToHex(h, s, Math.min(0.95, l * f)); };
export const suitVars = (hex) => `--suit:${hex};--suit-shade:${tone(hex, 0.78)};--suit-back:${tone(hex, 0.64)};--suit-light:${tone(hex, 1.16)}`;

const live = new Set();
let tickerOn = false;
function ensureTicker() {
  if (tickerOn) return; tickerOn = true;
  gsap.ticker.add((time) => { for (const p of live) { if (!p.root.isConnected) { continue; } if (p.static) continue; p.frame(time); } });
}

export class Puppet {
  /**
   * @param {{color:string,name?:string,cos?:object,view?:'side'|'front',k?:number,static?:boolean,crop?:string}} o
   */
  constructor(o) {
    this.o = o; this.name = o.name || ''; this.colorKey = o.color; this.hex = COLORS[o.color] || o.color;
    this.k = o.k ?? 0.26; this.view = o.view || 'side'; this.facing = 1; this.mode = 'idle'; this.ghost = false;
    this.impostorVisor = !!o.impostor; this.fallen = false; this.static = !!o.static; this.smug = false;
    this.hop = 0; this.offset = Math.random() * 6; this.bobY = 0; this.surprised = 0; this.hideAnt = false;
    const k = this.k;
    this.root = el('div', 'puppet'); this.flip = el('div', 'pp-flip', this.root);
    const n = ++uid;
    const txt = crewSvg
      .replace(/id="(clip\w+|glow)"/g, (m, a) => `id="${a}_${n}"`)
      .replace(/url\(#(clip\w+|glow)\)/g, (m, a) => `url(#${a}_${n})`)
      .replace(/width="640" height="800"/, '');
    this.flip.innerHTML = txt;
    this.svg = this.flip.querySelector('svg');
    this.svg.setAttribute('style', suitVars(this.hex));
    this.svg.style.cssText += `;position:absolute;left:${-320 * k}px;top:${-790 * k}px;width:${640 * k}px;height:${800 * k}px;overflow:visible`;
    this.g = {}; this.crew = this.svg.querySelector('#crew');
    for (const id of [...SIDE, ...FRONT, ...VISORS, ...FALLEN, 'ghost_tail']) { const e = this.crew.querySelector(':scope > #' + id); if (e) this.g[id] = e; }
    this.g.crew = this.crew;
    for (const id of ['leg_back', 'arm_back', 'leg_front', 'arm_front', 'antenna', 'visor', 'f_leg_l', 'f_leg_r', 'f_antenna', 'f_arm_l', 'f_arm_r']) { const p = this.g[id].getAttribute('data-pivot'); PIV[id] = p.split(',').map(Number); }
    // front view needs its own copy of the glass highlight above the front dome
    const gh = this.g.glass_highlight.cloneNode(true); gh.id = 'glass_highlight_f'; gh.setAttribute('display', 'none');
    this.g.f_visor.after(gh); this.g.gh_f = gh;
    this.applyCosmetics(o.cos || {});
    if (o.crop) this.svg.setAttribute('viewBox', o.crop);
    this.setView(this.view);
    if (o.name) { this.tag = el('div', 'nametag', this.root, o.name); this.tag.style.top = `${-800 * k - 18}px`; this.tag.style.display = 'none'; }
    if (!this.static) { live.add(this); ensureTicker(); }
  }

  // ---------- cosmetics
  nest(file, x, y) {
    const t = cosDB.svg[file.replace(/^svg\//, '')]; if (!t) return null;
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g'); g.setAttribute('class', 'cos');
    g.innerHTML = t.replace('<svg ', `<svg x="${x}" y="${y}" overflow="visible" `);
    return g;
  }
  applyCosmetics(cos) {
    const c = this.crew;
    if (cos.hat) {
      const it = cosDB.hats[cos.hat]; if (it) {
        const L = it.layers || {};
        if (L.back) { if (L.back.side) c.insertBefore(this.nest(L.back.side, it.side.x, it.side.y), this.g.dome); if (L.back.front) c.insertBefore(this.nest(L.back.front, it.front.x, it.front.y), this.g.f_leg_l); }
        const sideF = L.front?.side || it.side.file, frontF = L.front?.front || it.front.file;
        c.insertBefore(this.nest(sideF, it.side.x, it.side.y), this.g.arm_front);
        c.insertBefore(this.nest(frontF, it.front.x, it.front.y), this.g.f_arm_l);
        if (it.hidesAntenna) this.hideAnt = true;
      }
    }
    for (const slot of ['visor', 'topper', 'decal']) {
      const id = cos[slot]; if (!id) continue; const it = cosDB.rest[id]; if (!it) continue;
      const sideAfter = this.g[it.z.side], frontAfter = this.g[it.z.front];
      const s = this.nest(it.side.file, it.side.x, it.side.y), f = this.nest(it.front.file, it.front.x, it.front.y);
      if (s) sideAfter.after(s); if (f) frontAfter.after(f);
      for (const r of it.replaces.side) this.g[r]?.setAttribute('data-replaced', '1');
      for (const r of it.replaces.front) this.g[r]?.setAttribute('data-replaced', '1');
      if (slot === 'visor') this.cosVisor = true;
      if (it.hidesAntenna) this.hideAnt = true;
    }
  }

  // ---------- state
  setView(v) {
    this.view = v; this.refresh();
  }
  refresh() {
    const front = this.view === 'front';
    const hide = (id, on) => this.g[id] && this.g[id].setAttribute('display', on ? 'inline' : 'none');
    for (const id of SIDE) hide(id, !front && !this.fallen && !this.g[id].getAttribute('data-replaced'));
    for (const id of FRONT) hide(id, front && !this.fallen && !this.g[id].getAttribute('data-replaced'));
    for (const id of ['visor_coral', 'visor_ghost', 'visor_blink', 'visor_surprised']) hide(id, false);
    for (const id of ['visor_glow']) hide(id, !front && !this.fallen && !this.g.visor_glow.getAttribute('data-replaced'));
    hide('f_visor_glow', front && !this.fallen && !this.g.f_visor_glow.getAttribute('data-replaced'));
    hide('glass_highlight', !front && !this.fallen); hide('gh_f', front && !this.fallen);
    hide('ghost_tail', false);
    for (const id of FALLEN) hide(id, this.fallen);
    // cosmetics visibility follows the view + fallen state
    this.crew.querySelectorAll(':scope > .cos').forEach((c) => { c.style.display = this.fallen ? 'none' : ''; });
    this.root.classList.toggle('is-front', front);
  }
  setColor(c) {
    this.hex = COLORS[c] || c;
    for (const decl of suitVars(this.hex).split(';')) { const [k, v] = decl.split(':'); this.svg.style.setProperty(k, v); }
  }
  setMode(m) { this.mode = m; }
  setGhost(on) { this.ghost = on; if (on) this.root.classList.add('ghost'); else this.root.classList.remove('ghost'); }
  setFacing(f) { this.facing = f; this.flip.style.transform = `scaleX(${f})`; }
  setImpostorVisor(on) { this.impostorVisor = on; }
  showName(on = true) { if (this.tag) this.tag.style.display = on ? '' : 'none'; }
  /** knocked-out marker (fallen suit + popped helmet). */
  setFallen(on) { this.fallen = on; this.refresh(); if (this.tag) this.tag.style.display = 'none'; }
  doHop() { this.hopT = gsap.ticker.time + 0.6; }
  surprise(sec = 0.9) { this.surpriseT = gsap.ticker.time + sec; }
  place(x, y) { gsap.set(this.root, { x, y }); this.root.style.zIndex = Math.round(y); return this; }
  attach(parent) { parent.appendChild(this.root); return this; }

  moveTo(x, y, { speed = 360, dur = null, ease = 'none', run = false } = {}) {
    const cx = gsap.getProperty(this.root, 'x'), cy = gsap.getProperty(this.root, 'y');
    const d = dur ?? Math.max(0.15, Math.hypot(x - cx, y - cy) / speed);
    const self = this;
    if (Math.abs(x - cx) > 4) this.setFacing(x > cx ? 1 : -1);
    return gsap.to(this.root, { x, y, duration: d, ease,
      onStart() { self.setMode(run ? 'run' : 'walk'); },
      onUpdate() { self.root.style.zIndex = Math.round(gsap.getProperty(self.root, 'y')); },
      onComplete() { self.setMode('idle'); self.root.style.zIndex = Math.round(y); } });
  }
  walkPath(pts, opts = {}) {
    const tl = gsap.timeline();
    for (const [x, y] of pts) tl.add(this.moveTo(x, y, opts));
    return tl;
  }

  // ---------- per-frame animation (ported from puppet_demo.html)
  rot(id, a) { const [x, y] = PIV[id]; this.g[id].setAttribute('transform', `rotate(${a.toFixed(2)} ${x} ${y})`); }
  frame(t) {
    if (this.fallen) return;
    const tt = t + this.offset; let m = this.mode;
    const hop = this.hopT && t < this.hopT ? Math.sin(((this.hopT - t) / 0.6) * Math.PI) : 0;
    const surprised = (this.surpriseT && t < this.surpriseT) || hop > 0;
    const front = this.view === 'front';
    let leg = 0, arm = 0, arm2 = 0, bob = 0, rock = 0, lean = 0, ant = 0, sy = 1;
    const speed = m === 'run' ? 11 : m === 'walk' ? 7 : 0, ph = tt * speed, sn = Math.sin(ph);
    if (m === 'walk') { leg = 24 * sn; arm = -20 * sn; arm2 = -arm; bob = -Math.abs(sn) * 12; rock = 3 * sn; lean = front ? 0 : 2; ant = -8 * Math.sin(ph - 0.9); }
    else if (m === 'run') { leg = 38 * sn; arm = -46 * sn; arm2 = -arm; bob = -Math.abs(sn) * 22; rock = 4 * sn; lean = front ? 0 : 9; ant = -14 * Math.sin(ph - 0.9) - 10; }
    else { bob = Math.sin(tt * 2.2) * 3; ant = 4 * Math.sin(tt * 1.6); sy = 1 + 0.014 * Math.sin(tt * 2.2); }
    let armUp = false, armUp2 = false;
    if (m === 'cheer') { bob = -Math.abs(Math.sin(tt * 6)) * 26; armUp = armUp2 = true; arm = 150 + 14 * Math.sin(tt * 12); arm2 = 150 - 14 * Math.sin(tt * 12); ant = 12 * Math.sin(tt * 12); }
    if (m === 'wave') { armUp = true; arm = 140 + 22 * Math.sin(tt * 9); ant = 6 * Math.sin(tt * 3); }
    if (m === 'point') { armUp = true; arm = 100; }
    if (this.ghost) { leg = 0; bob = Math.sin(tt * 2.4) * 12 - 18; rock = 3 * Math.sin(tt * 1.7); sy = 1; }
    bob -= 34 * Math.max(0, hop);
    this.bobY = bob;
    const k = this.k;
    if (!front) {
      const sgn = armUp ? -1 : 1;
      this.rot('leg_front', leg); this.rot('leg_back', -leg);
      this.rot('arm_front', armUp ? -arm : arm); this.rot('arm_back', armUp2 ? -arm2 : -arm);
      this.rot('antenna', ant - hop * 12);
    } else {
      this.rot('f_leg_l', leg * 0.6); this.rot('f_leg_r', -leg * 0.6);
      if (armUp) { this.rot('f_arm_l', armUp2 ? arm2 : 6 * Math.sin(tt * 2)); this.rot('f_arm_r', -arm); }
      else { this.rot('f_arm_l', arm * 0.7 + Math.sin(tt * 2) * 2); this.rot('f_arm_r', arm2 * 0.7 - Math.sin(tt * 2) * 2); }
      this.rot('f_antenna', ant * 0.8 - hop * 10);
    }
    this.crew.setAttribute('transform', `translate(0 ${bob.toFixed(2)}) rotate(${(rock + lean).toFixed(2)} 320 790) translate(320 790) scale(${(2 - sy).toFixed(4)} ${sy.toFixed(4)}) translate(-320 -790)`);
    if (this.hideAnt) { this.g.antenna.setAttribute('display', 'none'); this.g.f_antenna.setAttribute('display', 'none'); }
    // visor state
    const blink = !this.ghost && (tt % 3.4) < 0.13;
    if (!front) {
      if (this.g.visor.getAttribute('data-replaced')) { this.setVisorSide(null); }
      else { const v = surprised ? 'visor_surprised' : this.ghost ? 'visor_ghost' : blink ? 'visor_blink' : this.impostorVisor ? 'visor_coral' : 'visor'; this.setVisorSide(v); }
      this.g.ghost_tail.setAttribute('display', this.ghost ? 'inline' : 'none');
      this.g.leg_front.setAttribute('display', this.ghost ? 'none' : 'inline'); this.g.leg_back.setAttribute('display', this.ghost ? 'none' : 'inline');
    } else {
      this.frontVisor(blink, surprised);
    }
  }
  setVisorSide(v) {
    for (const id of VISORS) this.g[id].setAttribute('display', id === v ? 'inline' : 'none');
    if (!this.g.visor_glow.getAttribute('data-replaced')) this.g.visor_glow.setAttribute('display', v === 'visor' ? 'inline' : 'none');
  }
  frontVisor(blink, surprised) {
    const fv = this.g.f_visor; if (fv.getAttribute('data-replaced')) return;
    const rect = fv.querySelector('rect');
    const col = this.ghost ? ['#B5EAD8', '#5E9C8A'] : this.impostorVisor ? ['#EE6A55', '#A43A2E'] : ['#F7AE4E', '#C26E2C'];
    if (rect.getAttribute('fill') !== col[0]) { rect.setAttribute('fill', col[0]); rect.setAttribute('stroke', col[1]); }
    let sy = blink ? 0.12 : 1;
    if (this.smug && !blink) sy = 1;
    fv.setAttribute('transform', `translate(0 323) scale(1 ${sy}) translate(0 -323)`);
    this.g.f_visor_glow.setAttribute('transform', `translate(0 323) scale(1 ${sy}) translate(0 -323)`);
    if (this.smug) this.ensureLid(fv, col[1]);
    this.lid && this.lid.setAttribute('display', this.smug ? 'inline' : 'none');
    if (surprised) fv.setAttribute('transform', `translate(321 323) scale(1.06 1.12) translate(-321 -323)`);
  }
  ensureLid(fv, stroke) {
    if (this.lid) { this.lid.querySelector('path').setAttribute('fill', stroke); return; }
    const id = 'lidclip' + uid + Math.floor(Math.random() * 1e5);
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.innerHTML = `<clipPath id="${id}"><rect x="204" y="245" width="234" height="157" rx="54"/></clipPath><g clip-path="url(#${id})"><path d="M 190 235 H 450 V 318 C 380 336 260 336 190 318 Z" fill="${stroke}"/><path d="M 204 322 C 270 340 372 340 438 322" fill="none" stroke="#2A1E35" stroke-width="7" stroke-linecap="round"/></g>`;
    this.lid = g; fv.appendChild(g);
  }
}

export function makePortrait(color, cos = {}, size = 78) {
  const p = new Puppet({ color, cos, view: 'front', static: true, k: 1, crop: '96 50 448 448' });
  const wrap = el('div', 'portrait');
  wrap.style.width = wrap.style.height = size + 'px';
  p.svg.style.cssText += `;position:absolute;left:0;top:0;width:${size}px;height:${size}px`;
  p.root.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0';
  p.flip.style.cssText = '';
  wrap.appendChild(p.svg);
  p.crew.setAttribute('transform', '');
  p.g.f_visor.removeAttribute('transform');
  return { el: wrap, puppet: p };
}
