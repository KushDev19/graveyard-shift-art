import gsap from 'gsap';
import { el } from './util.js';

export function createStage(root) {
  const wrap = el('div', 'stage-wrap', root);
  const stage = el('div', 'stage', wrap);
  const L = {};
  for (const n of ['world', 'hud', 'modal', 'splash', 'pov', 'fx', 'present']) L[n] = el('div', 'layer layer-' + n, stage);
  const fit = () => { const s = Math.min(innerWidth / 1920, innerHeight / 1080); stage.style.transform = `translate(-50%,-50%) scale(${s})`; stage.dataset.scale = s; };
  addEventListener('resize', fit); fit();
  return { wrap, stage, L, fit, scale: () => parseFloat(stage.dataset.scale) };
}
