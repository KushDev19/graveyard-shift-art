import { A, el } from './util.js';

const cache = {};
/** Task station (K job *_front svg) with idle / highlight / done state layers. x,y = bottom-centre in stage px. */
export async function createStation(parent, kind, x, y, h, z = null) {
  const file = kind === 'timeclock' ? 'props/timeclock_front.svg' : `props/station_${kind}_front.svg`;
  const txt = (cache[file] ??= await fetch(A(file)).then((r) => r.text()));
  const vb = txt.match(/viewBox="([\d.\s-]+)"/)[1].split(/\s+/).map(Number); const w = (h * vb[2]) / vb[3];
  const d = el('div', 'station', parent); d.innerHTML = txt.replace(/width="[^"]*"\s+height="[^"]*"/, '');
  Object.assign(d.style, { left: x - w / 2 + 'px', top: y - h + 'px', width: w + 'px', height: h + 'px', zIndex: z ?? Math.round(y) });
  const svg = d.querySelector('svg'); svg.setAttribute('width', w); svg.setAttribute('height', h);
  const S = { el: d, w, h, state: 'idle' };
  S.set = (st) => { S.state = st; for (const n of ['idle', 'highlight', 'done', 'ready']) { const g = svg.querySelector('#state_' + n); if (g) g.setAttribute('display', n === st ? 'inline' : 'none'); } };
  S.set('idle'); return S;
}
