import './style.css';
import gsap from 'gsap';
import { createContext } from './core/context.js';
import { Director } from './core/director.js';
import { preloadCosmetics } from './core/util.js';
import { preloadMeeting } from './core/meeting.js';
import { SCENES } from './scenes/index.js';

async function boot() {
  const root = document.getElementById('app');
  await Promise.all([preloadCosmetics(), preloadMeeting(), document.fonts.load("20px Bungee"), document.fonts.load("20px VT323"), document.fonts.load("700 20px 'Space Grotesk'")]);
  const ctx = createContext(root);
  const params = new URLSearchParams(location.search);
  const d = new Director(ctx, SCENES); window.__d = d; window.__ctx = ctx; window.gsap = gsap;
  await d.start(params.has('scene') ? +params.get('scene') : 0);
  if (params.has('step')) { /* debug: ?scene=8&step=3 */ await d.goto(+params.get('scene') || 0, +params.get('step')); }
}
boot().catch((e) => { console.error(e); document.body.insertAdjacentHTML('beforeend', `<pre style="color:#fff;padding:20px">${e.stack}</pre>`); });
