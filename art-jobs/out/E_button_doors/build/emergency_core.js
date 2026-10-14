// GRAVEYARD SHIFT emergency button: geometry core (shared by emergency_demo.html and build_e.py).
// Units = pixels of the 5504 px room paintings. Camera: 3/4 front view, ellipse ratio K.
// The dome is a glass bell (cylinder + hemisphere) hinged at the BACK of its rim; opening is a
// real 3D rotation about that hinge, projected orthographically, so the outline is recomputed.
const EB = (() => {
  const K = 0.32, CS = Math.sqrt(1 - K * K);
  const VB = [570, 530];
  const CX = 330, TY = 380;           // centre of the base top surface
  const RB = 195, BAND = 70;          // base radius, side band height
  const RD = 150, HD = 50;            // dome radius, dome cylinder height
  const RW = 86, RBT = 62, HBT = 40;  // well radius, button radius, button height
  const LOCK = [462, 420];            // padlock pivot (top of shackle, on the hasp)
  const OL = '#2A1E35', W = 8, w = 5;
  const COL = {
    idle:     { top: '#EC6A5A', hl: '#F7A08F', side: '#C9473D', shade: '#A33A36', spec: 0.85 },
    lit:      { top: '#FF8462', hl: '#FFC7A3', side: '#E0563F', shade: '#B9443A', spec: 0.95 },
    disabled: { top: '#5B4868', hl: '#6C5A7B', side: '#433350', shade: '#33273F', spec: 0.22 },
  };
  const f = n => Math.round(n * 10) / 10;
  const ellD = (cx, cy, rx, ry) => `M${f(cx - rx)},${f(cy)}a${f(rx)},${f(ry)} 0 1,0 ${f(2 * rx)},0a${f(rx)},${f(ry)} 0 1,0 ${f(-2 * rx)},0Z`;
  const cylD = (cx, y1, y2, r) => `M${f(cx - r)},${f(y1)}L${f(cx - r)},${f(y2)}A${f(r)},${f(r * K)} 0 0,0 ${f(cx + r)},${f(y2)}L${f(cx + r)},${f(y1)}A${f(r)},${f(r * K)} 0 0,1 ${f(cx - r)},${f(y1)}Z`;
  const bandD = (cx, ya, yb, r) => `M${f(cx - r)},${f(ya)}A${f(r)},${f(r * K)} 0 0,0 ${f(cx + r)},${f(ya)}L${f(cx + r)},${f(yb)}A${f(r)},${f(r * K)} 0 0,1 ${f(cx - r)},${f(yb)}Z`;
  const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
  const mix = (a, b, t) => '#' + hex(a).map((v, i) => Math.round(v + (hex(b)[i] - v) * t).toString(16).padStart(2, '0')).join('');
  const mixCol = (a, b, t) => ({ top: mix(a.top, b.top, t), hl: mix(a.hl, b.hl, t), side: mix(a.side, b.side, t), shade: mix(a.shade, b.shade, t), spec: a.spec + (b.spec - a.spec) * t });

  // 3D samples of the dome surface in local coords (x, u = along axis, w = depth)
  const SAMP = (() => {
    const p = [], NA = 120;
    for (let i = 0; i < NA; i++) { const a = 2 * Math.PI * i / NA; p.push([RD * Math.cos(a), 0, RD * Math.sin(a)]); }
    for (let e = 0; e <= 90; e += 5) {
      const r = RD * Math.cos(e * Math.PI / 180), u = HD + RD * Math.sin(e * Math.PI / 180);
      const n = Math.max(6, Math.round(NA * r / RD));
      for (let i = 0; i < n; i++) { const a = 2 * Math.PI * i / n; p.push([r * Math.cos(a), u, r * Math.sin(a)]); }
    }
    return p;
  })();
  // hinge on the back-left of the rim (azimuth HA), axis tangent to the rim; top swings outward
  const HA = 235 * Math.PI / 180;
  const HX = RD * Math.cos(HA), HZ = RD * Math.sin(HA);
  const TX = Math.sin(HA), TZ = -Math.cos(HA);
  const HINGE = [CX + HX, TY + HZ * K];
  function rot(x, y, z, th) {           // Rodrigues rotation about axis (TX,0,TZ) through (HX,0,HZ)
    const vx = x - HX, vy = y, vz = z - HZ, c = Math.cos(th), s = Math.sin(th);
    const cx = -TZ * vy, cy = TZ * vx - TX * vz, cz = TX * vy;      // t x v
    const d = (TX * vx + TZ * vz) * (1 - c);
    return [vx * c + cx * s + TX * d + HX, vy * c + cy * s, vz * c + cz * s + TZ * d + HZ];
  }
  const scr = p => [CX + p[0], TY - p[1] * CS + p[2] * K];
  const proj = (x, u, wd, th) => scr(rot(x, u, wd, th));
  function hull(pts) {
    pts = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const p of pts) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
    for (let i = pts.length - 1; i >= 0; i--) { const p = pts[i]; while (up.length > 1 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); }
    return lo.slice(0, -1).concat(up.slice(0, -1));
  }
  const poly = (pts, close) => 'M' + pts.map(p => f(p[0]) + ',' + f(p[1])).join('L') + (close ? 'Z' : '');
  function domeGeom(deg) {
    const th = deg * Math.PI / 180;
    const d = poly(hull(SAMP.map(p => proj(p[0], p[1], p[2], th))), true);
    const c3 = rot(0, 0, 0, th), N = 96, rim = [];
    for (let i = 0; i < N; i++) { const a = 2 * Math.PI * i / N, q = rot(RD * Math.cos(a), 0, RD * Math.sin(a), th); rim.push({ p: scr(q), back: q[2] < c3[2] - 1e-6 }); }
    let st = rim.findIndex((r, i) => r.back && !rim[(i + N - 1) % N].back); if (st < 0) st = 0;
    const seq = rim.slice(st).concat(rim.slice(0, st));
    const nb = seq.filter(r => r.back).length;
    const back = seq.slice(0, nb + 1).map(r => r.p), front = seq.slice(nb).concat([seq[0]]).map(r => r.p);
    const ax = rot(0, 1, 0, th), a0 = rot(0, 0, 0, 0);
    const up = [ax[0] - c3[0], ax[1] - c3[1], ax[2] - c3[2]];
    const facing = -(up[1] * K + up[2] * CS);   // >0: opening faces the camera
    return { d, r0: scr(c3), s0: proj(0, HD, 0, th), rim: poly(rim.map(r => r.p), true), back: poly(back), front: poly(front), facing, th: deg };
  }

  const defs = P => `<defs>
<radialGradient id="${P}halo"><stop offset="0" stop-color="#FFD27A" stop-opacity=".85"/><stop offset=".5" stop-color="#F5A54A" stop-opacity=".35"/><stop offset="1" stop-color="#F5A54A" stop-opacity="0"/></radialGradient>
<clipPath id="${P}band"><path d="${cylD(CX, TY, TY + BAND, RB)}"/></clipPath>
<clipPath id="${P}lockb"><rect x="-30" y="30" width="60" height="50" rx="11"/></clipPath>
</defs>`;

  function base(P) {
    const yb = TY + BAND;
    return `<g id="base" data-pivot="${CX},${TY}">
<ellipse cx="${CX}" cy="${yb + 10}" rx="${RB + 22}" ry="${f((RB + 22) * K)}" fill="#1B1830" opacity=".28"/>
<g clip-path="url(#${P}band)">
<path d="${cylD(CX, TY, yb, RB)}" fill="#F4E6C8"/>
<path d="${bandD(CX, TY + 20, TY + 29, RB)}" fill="#F5A54A"/>
<path d="${bandD(CX, TY + 34, TY + 50, RB)}" fill="#E8574A"/>
<path d="${bandD(CX, TY + 60, TY + 64, RB)}" fill="#E2CFA8"/>
<rect x="${CX + RB * 0.58}" y="${TY - 10}" width="${RB}" height="${BAND + 80}" fill="#3D2A4F" opacity=".2"/>
<rect x="${CX - RB * 0.86}" y="${TY - 10}" width="${RB * 0.09}" height="${BAND + 80}" fill="#FFFFFF" opacity=".35"/>
</g>
<path d="${cylD(CX, TY, yb, RB)}" fill="none" stroke="${OL}" stroke-width="${W}" stroke-linejoin="round"/>
<path d="${ellD(CX, TY, RB, RB * K)}" fill="#DCE2E8" stroke="${OL}" stroke-width="${W}"/>
<path d="M${CX + RB * 0.3},${f(TY + RB * K * 0.95 - 6)}A${RB - 6},${f((RB - 6) * K)} 0 0,0 ${CX + RB - 8},${TY - 4}" fill="none" stroke="#B6BFC9" stroke-width="9" stroke-linecap="round"/>
<path d="${ellD(CX, TY, 176, 176 * K)}" fill="none" stroke="#B3BCC6" stroke-width="5"/>
<path d="M${CX - 150},${f(TY - 176 * K * 0.66)}A176,${f(176 * K)} 0 0,1 ${CX - 60},${f(TY - 176 * K * 0.98)}" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity=".9"/>
<path d="${ellD(CX, TY, RD + 8, (RD + 8) * K)}" fill="#B9C2CC" stroke="${OL}" stroke-width="${w}"/>
<path d="${ellD(CX, TY + 2, RD - 8, (RD - 8) * K)}" fill="#E9EDF1"/>
<path d="${ellD(CX, TY + 2, RW + 12, (RW + 12) * K)}" fill="none" stroke="#C9D0D7" stroke-width="6"/>
<path d="${ellD(CX, TY + 2, RW, RW * K)}" fill="#4A4160" stroke="${OL}" stroke-width="${w}"/>
<path d="${ellD(CX, TY + 9, RW - 6, (RW - 9) * K)}" fill="#372E4A"/>
<g transform="translate(${f(HINGE[0])},${f(HINGE[1] - 4)}) rotate(${f(Math.atan2(TZ * K, TX) * 180 / Math.PI + 180)})"><rect x="-28" y="-9" width="56" height="18" rx="7" fill="#C3CBD3" stroke="${OL}" stroke-width="${w}"/><path d="M-9,-8V8M9,-8V8" stroke="${OL}" stroke-width="3"/></g>
<rect x="${LOCK[0] - 11}" y="${LOCK[1] - 4}" width="22" height="16" rx="4" fill="#C3CBD3" stroke="${OL}" stroke-width="4"/>
</g>`;
  }
  function glow(s) {
    const ring = mix('#6E5648', '#FFCB66', s.glow);
    const sc = 0.8 + 0.4 * s.halo;
    return `<g id="glow_ring" data-pivot="${CX},${TY + 2}">
<ellipse cx="${CX}" cy="${TY - 14}" rx="${f(185 * sc)}" ry="${f(125 * sc)}" fill="url(#${s.P}halo)" opacity="${f(Math.min(1, s.halo))}"/>
<path d="${ellD(CX, TY + 3, RW - 10, (RW - 10) * K)}" fill="none" stroke="${ring}" stroke-width="8"/>
<path d="${ellD(CX, TY + 3, RW - 10, (RW - 10) * K)}" fill="none" stroke="#FFF3D0" stroke-width="3" opacity="${f(s.glow * 0.8)}"/>
</g>`;
  }
  function button(s) {
    const c = s.col, B = TY + 6, yT = B - (HBT - s.depth), r = RBT;
    const tr = `translate(${CX},${B}) scale(${f(s.sx * 1000) / 1000},${f(s.sy * 1000) / 1000}) translate(${-CX},${-B})`;
    const a1 = 200 * Math.PI / 180, a2 = 238 * Math.PI / 180, rr = r * 0.78;
    const sp = `M${f(CX + rr * Math.cos(a1))},${f(yT + rr * K * Math.sin(a1))}A${f(rr)},${f(rr * K)} 0 0,1 ${f(CX + rr * Math.cos(a2))},${f(yT + rr * K * Math.sin(a2))}`;
    return `<g id="button" data-pivot="${CX},${B}" transform="${tr}">
<clipPath id="${s.P}bside"><path d="${cylD(CX, yT, B, r)}"/></clipPath>
<path d="${cylD(CX, yT, B, r)}" fill="${c.side}"/>
<rect x="${CX + r * 0.42}" y="${f(yT - 30)}" width="${r}" height="${HBT + 60}" fill="${c.shade}" clip-path="url(#${s.P}bside)"/>
<rect x="${CX - r * 0.8}" y="${f(yT)}" width="${f(r * 0.12)}" height="${HBT + 30}" fill="#FFFFFF" opacity="${f(c.spec * 0.35)}" clip-path="url(#${s.P}bside)"/>
<path d="${cylD(CX, yT, B, r)}" fill="none" stroke="${OL}" stroke-width="${W - 1}" stroke-linejoin="round"/>
<path d="${ellD(CX, yT, r, r * K)}" fill="${c.top}" stroke="${OL}" stroke-width="${w}"/>
<path d="${ellD(CX - 8, yT - 3, r * 0.66, r * K * 0.6)}" fill="${c.hl}"/>
<path d="${sp}" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="${f(c.spec)}"/>
</g>`;
  }
  function dome(s, part) {
    const g = s.dg, P = s.P, hp = f(HINGE[0]) + ',' + f(HINGE[1]);
    if (part === 'back') {
      const inside = g.facing > 0.05 ? `<path d="${g.rim}" fill="#7FC8B8" opacity="${f(Math.min(0.4, g.facing * 0.7))}"/>` : '';
      return `<g id="dome_back" class="dome" data-pivot="${hp}">
<clipPath id="${P}dclip"><path d="${g.d}"/></clipPath>
<g opacity=".66" clip-path="url(#${P}dclip)"><path d="${g.d}" fill="#9FD6C8"/><path d="${g.d}" transform="translate(-26,-14)" fill="#DDF3ED"/></g>
${inside}<path d="${g.back}" fill="none" stroke="${OL}" stroke-width="14" stroke-linejoin="round" opacity=".6"/>
<path d="${g.back}" fill="none" stroke="#C4EAE0" stroke-width="6" stroke-linejoin="round"/>
</g>`;
    }
    const S = g.s0, R0 = g.r0, r = RD * 0.76, a = d => d * Math.PI / 180;
    const pt = d => [S[0] + r * Math.cos(a(d)), S[1] + r * Math.sin(a(d))];
    const so = Math.max(0, 1 - g.th / 20) * 0.75;
    const streak = so > 0 ? `<path d="M${f(S[0] - r * 0.985)},${f(R0[1] - 16)}L${f(S[0] - r * 0.985)},${f(S[1] + 12)}" stroke="#FFFFFF" stroke-width="13" stroke-linecap="round" opacity="${f(so)}"/>` : '';
    const open = g.facing > 0.05;
    const rimF = `<path d="${g.front}" fill="none" stroke="${OL}" stroke-width="${open ? 15 : 0}" stroke-linejoin="round"/><path d="${g.front}" fill="none" stroke="#C4EAE0" stroke-width="7" stroke-linejoin="round"/>`;
    const p1 = pt(190), p2 = pt(246), p3 = pt(262);
    return `<g id="dome_front" class="dome" data-pivot="${hp}">
${rimF}
<path d="${g.d}" fill="none" stroke="${OL}" stroke-width="${W}" stroke-linejoin="round"/>
${streak}<path d="M${f(p1[0])},${f(p1[1])}A${f(r)},${f(r)} 0 0,1 ${f(p2[0])},${f(p2[1])}" fill="none" stroke="#FFFFFF" stroke-width="14" stroke-linecap="round" opacity=".9"/>
<circle cx="${f(p3[0])}" cy="${f(p3[1])}" r="7" fill="#FFFFFF" opacity=".9"/>
</g>`;
  }
  function padlock(s) {
    const L = s.lock;
    return `<g id="padlock" data-pivot="${LOCK[0]},${LOCK[1]}" opacity="${f(L.op)}" transform="translate(${LOCK[0]},${f(LOCK[1] + L.dy)}) rotate(${f(L.rot)})">
<path d="M-15,36V12A15,15 0 0,1 15,12V36" fill="none" stroke="${OL}" stroke-width="17" stroke-linecap="round"/>
<path d="M-15,36V12A15,15 0 0,1 15,12V36" fill="none" stroke="#C9D1D8" stroke-width="8" stroke-linecap="round"/>
<path d="M-17,14A14,14 0 0,1 -4,0" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity=".8"/>
<g clip-path="url(#${s.P}lockb)"><rect x="-30" y="30" width="60" height="50" fill="#F2B04F"/><rect x="-30" y="64" width="60" height="20" fill="#C9833A"/><rect x="14" y="30" width="20" height="50" fill="#3D2A4F" opacity=".18"/><rect x="-24" y="36" width="5" height="22" rx="2.5" fill="#FFE2A8"/></g>
<rect x="-30" y="30" width="60" height="50" rx="11" fill="none" stroke="${OL}" stroke-width="${w + 1}"/>
<circle cx="0" cy="50" r="6.5" fill="${OL}"/><path d="M-3,52H3L4.5,64H-4.5Z" fill="${OL}"/>
</g>`;
  }
  function flash(s) {
    if (s.flash == null) return `<g id="flash_ring" data-pivot="${CX},${TY}" opacity="0"></g>`;
    const t = s.flash, out = 1 - Math.pow(1 - t, 3);
    const ring = (p, sw, op) => { const rx = 90 + 150 * p; return `<path d="${ellD(CX, TY - 6, rx, rx * K * 1.05)}" fill="none" stroke="#E8574A" stroke-width="${f(sw)}" opacity="${f(op)}"/>`; };
    const t2 = Math.max(0, t - 0.18) / 0.82, out2 = 1 - Math.pow(1 - t2, 3);
    return `<g id="flash_ring" data-pivot="${CX},${TY}">${ring(out, 16 - 12 * t, 1 - t)}${t2 > 0 ? ring(out2 * 0.8, 8 - 6 * t2, (1 - t2) * 0.8) : ''}</g>`;
  }

  // state: {theta, depth, sx, sy, col:{...}|name, glow, halo, flash, lock:{op,dy,rot}}; opts: {P, only:[...parts]}
  function svg(st, opts = {}) {
    const P = opts.P || 'eb';
    const s = Object.assign({ theta: 0, depth: 0, sx: 1, sy: 1, col: 'idle', glow: 0, halo: 0, flash: null, lock: { op: 0, dy: 0, rot: 0 } }, st);
    if (typeof s.col === 'string') s.col = COL[s.col];
    s.P = P; s.dg = domeGeom(s.theta);
    const parts = { base: () => base(P), glow_ring: () => glow(s), dome_back: () => dome(s, 'back'), button: () => button(s), dome_front: () => dome(s, 'front'), padlock: () => padlock(s), flash_ring: () => flash(s) };
    const order = drawOrder(s.theta);
    const body = order.filter(k => !opts.only || opts.only.includes(k)).map(k => parts[k]()).join('\n');
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB[0]} ${VB[1]}" width="${VB[0]}" height="${VB[1]}" id="emergency_button">
${defs(P)}
${body}
</svg>`;
  }
  const drawOrder = deg => deg > 30
    ? ['base', 'glow_ring', 'flash_ring', 'dome_back', 'dome_front', 'button', 'padlock']
    : ['base', 'glow_ring', 'flash_ring', 'dome_back', 'button', 'dome_front', 'padlock'];

  const STATES = {
    idle: { theta: 0, col: 'idle' },
    open: { theta: 110, col: 'lit', glow: 1, halo: 0.75 },
    pressed: { theta: 110, col: 'lit', depth: 14, glow: 1, halo: 1.35 },
    disabled: { theta: 0, col: 'disabled', lock: { op: 1, dy: 0, rot: 0 } },
  };
  return { svg, STATES, COL, mixCol, drawOrder, domeGeom, VB, HINGE, LOCK, CX, TY, K };
})();
if (typeof module !== 'undefined') module.exports = EB;
