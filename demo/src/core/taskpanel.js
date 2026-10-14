import gsap from 'gsap';
import { A, el, img, shuffle } from './util.js';

const SC = 0.56, W = 2048, H = 1536;
const COL = { red: '#E4574A', yellow: '#F2C94C', blue: '#4F7FE0', green: '#52B87A' };
const part = (n) => A(`panels/parts/${n}.svg`);

function frame(layer, bgFile, title) {
  const dim = el('div', 'tp-dim', layer);
  const wrap = el('div', 'tp', layer);
  Object.assign(wrap.style, { left: `${960 - W / 2}px`, top: `${528 - H / 2}px`, width: W + 'px', height: H + 'px', transform: `scale(${SC})` });
  img(A(bgFile), 'tp-bg', wrap);
  const cap = el('div', 'tp-title', layer); cap.textContent = title;
  gsap.set(dim, { opacity: 0 });
  const open = gsap.timeline().to(dim, { opacity: 1, duration: 0.25 }).fromTo(wrap, { scale: SC * 0.55, y: 160, opacity: 0 }, { scale: SC, y: 0, opacity: 1, duration: 0.5, ease: 'back.out(1.6)' }, 0).fromTo(cap, { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: 'back.out(2)' }, 0.2);
  const rect = () => wrap.getBoundingClientRect();
  const toPanel = (ev) => { const r = rect(), s = r.width / W; return [(ev.clientX - r.left) / s, (ev.clientY - r.top) / s]; };
  const close = () => gsap.timeline({ onComplete: () => { dim.remove(); wrap.remove(); cap.remove(); } }).to(wrap, { scale: SC * 0.6, y: 120, opacity: 0, duration: 0.3, ease: 'power2.in' }, 0).to([dim, cap], { opacity: 0, duration: 0.25 }, 0);
  const shake = () => gsap.fromTo(wrap, { x: -22 }, { x: 0, duration: 0.55, ease: 'elastic.out(1.4,0.22)' });
  return { dim, wrap, cap, open, close, shake, toPanel, rect };
}

/** Reactor Override: press keys 1..10 in order. Wrong key = shake + full reset. */
export function createKeypad(layer, { onWrong, onProgress } = {}) {
  const f = frame(layer, 'panels/panel_keypad.svg', 'REACTOR OVERRIDE: PRESS 1 TO 10 IN ORDER');
  const KX = [364, 694, 1024, 1354, 1684], KY = [795, 1145];
  const labels = shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  const keys = labels.map((n, i) => {
    const k = el('button', 'tp-key', f.wrap); const x = KX[i % 5], y = KY[Math.floor(i / 5)];
    Object.assign(k.style, { left: x - 120 + 'px', top: y - 120 + 'px' });
    const im = img(part('key_idle'), '', k); const t = el('span', '', k, String(n));
    return { k, im, n, x, y, t, state: 'idle' };
  });
  const disp = el('div', 'tp-disp', f.wrap); Object.assign(disp.style, { left: 1500 - 330 + 'px', top: 377 - 119 + 'px', width: '660px', height: '238px' });
  const needle = img(part('vu_needle'), 'tp-needle', f.wrap); Object.assign(needle.style, { left: 520 - 30 * 0.714 + 'px', top: 472 - 280 * 0.714 + 'px', width: 60 * 0.714 + 'px', height: 320 * 0.714 + 'px', transformOrigin: `${30 * 0.714}px ${280 * 0.714}px` });
  const lamp = img(part('lamp_lit_amber'), 'tp-lamp', f.wrap); Object.assign(lamp.style, { left: 1850 - 60 * 0.824 + 'px', top: 1422 - 60 * 0.824 + 'px', width: 120 * 0.824 + 'px', height: 120 * 0.824 + 'px', opacity: 0 });
  let next = 1, solved = false, resolveSolved; const solvedP = new Promise((r) => (resolveSolved = r));
  const paintDisp = (msg, bad) => { disp.innerHTML = `<div class="${bad ? 'bad' : ''}">${msg}</div>`; };
  const setNeedle = () => gsap.to(needle, { rotation: -80 + (next - 1) * 16, duration: 0.45, ease: 'back.out(2)' });
  paintDisp('PRESS 1'); gsap.set(needle, { rotation: -80 });
  const setKey = (K, st) => { K.state = st; K.im.src = part('key_' + st); };
  function press(n) {
    if (solved) return false; const K = keys.find((x) => x.n === n); if (!K || K.state === 'correct') return false;
    setKey(K, 'pressed'); gsap.fromTo(K.k, { y: 8 }, { y: 0, duration: 0.25, ease: 'back.out(3)' });
    if (n === next) {
      gsap.delayedCall(0.07, () => setKey(K, 'correct')); next++; setNeedle(); onProgress?.(n);
      if (next > 10) { solved = true; paintDisp('ACCESS GRANTED'); gsap.to(lamp, { opacity: 1, duration: 0.3 }); gsap.fromTo(lamp, { scale: 1.6 }, { scale: 1, duration: 0.5, ease: 'back.out(3)' }); gsap.delayedCall(0.6, () => resolveSolved()); }
      else paintDisp(`OK: PRESS ${next}`);
      return true;
    }
    wrong(K); return false;
  }
  function wrong(K) {
    // logic resets immediately (so rapid or scripted presses can't pile up); the red flash is cosmetic
    for (const x of keys) if (x !== K) setKey(x, 'idle');
    next = 1; setNeedle(); setKey(K, 'wrong'); paintDisp('WRONG KEY: RESET', true); f.shake(); onWrong?.();
    gsap.delayedCall(0.55, () => { if (K.state === 'wrong') setKey(K, 'idle'); if (next === 1) paintDisp('PRESS 1'); });
  }
  keys.forEach((K) => K.k.addEventListener('click', () => press(K.n)));
  /** presenter fallback: one deliberate wrong press, then the full sequence */
  async function auto(wait) {
    await wait(0.4); for (const n of [1, 2, 3]) { press(n); await wait(0.32); }
    const wrongN = [10, 9, 8].find((m) => m !== next); press(wrongN); await wait(0.95);
    for (let n = 1; n <= 10; n++) { press(n); await wait(0.24); }
  }
  return { ...f, keys, press, auto, solved: solvedP, get isSolved() { return solved; } };
}

/** Patch the Switchboard: drag the four coloured plugs to their matching jacks. */
export function createWiring(layer, { onProgress } = {}) {
  const f = frame(layer, 'panels/panel_switchboard.svg', 'PATCH THE SWITCHBOARD: MATCH THE COLOURS');
  const OUT = ['red', 'yellow', 'blue', 'green'], IN = ['green', 'red', 'blue', 'yellow'], Y = [350, 630, 910, 1190];
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('class', 'tp-cables'); f.wrap.appendChild(svg);
  const lampImg = (color, x, y) => { const i = img(part('lamp_lit_' + color), 'tp-lamp', f.wrap); Object.assign(i.style, { left: x - 60 * 0.882 + 'px', top: y - 60 * 0.882 + 'px', width: 120 * 0.882 + 'px', height: 120 * 0.882 + 'px', opacity: 0 }); return i; };
  const power = lampImg('amber', 1024, 1460); power.style.width = 120 * 0.706 + 'px'; power.style.height = 120 * 0.706 + 'px'; power.style.left = 1024 - 60 * 0.706 + 'px'; power.style.top = 1460 - 60 * 0.706 + 'px';
  const plugs = OUT.map((c, i) => {
    const jy = Y[i], jx = 330; const rest = [jx + 330, jy];
    const path = (o) => { const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('fill', 'none'); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-width', o.w); p.setAttribute('stroke', o.c); svg.appendChild(p); return p; };
    const cOut = path({ w: 34, c: '#2A1E35' }), cFill = path({ w: 22, c: COL[c] });
    const im = img(part('plug_' + c), 'tp-plug', f.wrap); im.style.width = '380px'; im.style.height = '124px';
    const P = { color: c, jx, jy, tip: [...rest], rest, im, cOut, cFill, lampOut: lampImg(c, 470, jy), connected: false, drag: false };
    const draw = () => {
      im.style.left = P.tip[0] - 340 + 'px'; im.style.top = P.tip[1] - 62 + 'px';
      const ax = P.tip[0] - 340 + 10, ay = P.tip[1] + 2, sx = jx, sy = jy; const sag = 40 + Math.abs(ax - sx) * 0.15;
      const d = `M ${sx} ${sy} C ${sx + 120} ${sy + sag}, ${ax - 120} ${ay + sag}, ${ax} ${ay}`; cOut.setAttribute('d', d); cFill.setAttribute('d', d);
    };
    P.draw = draw; draw(); return P;
  });
  const inLamps = IN.map((c, i) => lampImg(c, 1790, Y[i]));
  const jackIn = IN.map((c, i) => ({ color: c, x: 1640, y: Y[i], lamp: inLamps[i], taken: false }));
  let connected = 0, solved = false, resolveSolved; const solvedP = new Promise((r) => (resolveSolved = r));
  const retract = (P, bad) => { if (bad) f.shake(); return gsap.to(P.tip, { 0: P.rest[0], 1: P.rest[1], duration: 0.5, ease: 'back.out(1.4)', onUpdate: P.draw }); };
  function drop(P) {
    P.drag = false; P.im.style.zIndex = 3;
    const near = jackIn.find((j) => Math.hypot(j.x - P.tip[0], j.y - P.tip[1]) < 95);
    if (near && near.color === P.color && !near.taken) {
      near.taken = true; P.connected = true; connected++;
      gsap.to(P.tip, { 0: near.x + 8, 1: near.y, duration: 0.18, ease: 'power2.out', onUpdate: P.draw });
      for (const l of [near.lamp, P.lampOut]) { gsap.to(l, { opacity: 1, duration: 0.2 }); gsap.fromTo(l, { scale: 1.5 }, { scale: 1, duration: 0.4, ease: 'back.out(3)' }); }
      onProgress?.(connected);
      if (connected === 4 && !solved) { solved = true; gsap.to(power, { opacity: 1, duration: 0.3 }); gsap.fromTo(power, { scale: 1.8 }, { scale: 1, duration: 0.5, ease: 'back.out(3)' }); gsap.delayedCall(0.7, () => resolveSolved()); }
      return true;
    }
    retract(P, !!near); return false;
  }
  plugs.forEach((P) => {
    P.im.addEventListener('pointerdown', (e) => {
      if (P.connected || solved) return; e.preventDefault(); P.drag = true; P.im.style.zIndex = 9; P.im.setPointerCapture(e.pointerId); gsap.killTweensOf(P.tip);
      const mv = (ev) => { const [x, y] = f.toPanel(ev); P.tip[0] = Math.max(300, Math.min(1900, x)); P.tip[1] = Math.max(250, Math.min(1400, y)); P.draw(); };
      const up = () => { P.im.removeEventListener('pointermove', mv); P.im.removeEventListener('pointerup', up); drop(P); };
      P.im.addEventListener('pointermove', mv); P.im.addEventListener('pointerup', up);
    });
  });
  /** scripted drag of one plug (used by auto-complete and by the walk-away demo) */
  function dragTo(i, wait) {
    const P = plugs[i], target = jackIn.find((j) => j.color === P.color); const tl = gsap.timeline();
    P.im.style.zIndex = 9; gsap.killTweensOf(P.tip);
    tl.to(P.tip, { 0: (P.rest[0] + target.x) / 2, 1: P.rest[1] - 40, duration: 0.45, ease: 'power2.out', onUpdate: P.draw })
      .to(P.tip, { 0: target.x, 1: target.y, duration: 0.45, ease: 'power2.inOut', onUpdate: P.draw })
      .call(() => drop(P));
    return tl;
  }
  async function auto(play) { for (let i = 0; i < 4; i++) { await play(dragTo(i)); await play(gsap.timeline().to({}, { duration: 0.12 })); } }
  return { ...f, plugs, dragTo, auto, solved: solvedP, get connected() { return connected; }, get isSolved() { return solved; } };
}
