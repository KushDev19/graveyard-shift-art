// Background music: very simple, loops forever, M toggles mute.
// 1) If public/assets/audio/music.mp3 exists, that file is looped.
// 2) Otherwise a soft lo-fi loop is synthesized with WebAudio (no files, no licensing).
// Browsers block audio until a user gesture, so start() is called from the first key press or click.
import { A } from './util.js';

const VOL = 0.32;
let ctx = null, master = null, started = false, muted = false, timer = null, audioEl = null;

const midi = (n) => 440 * Math.pow(2, (n - 69) / 12);
const BPM = 78, BEAT = 60 / BPM, BAR = BEAT * 4;
// Am9 - Fmaj9 - Cmaj7 - G6 : root (bass), chord tones (pad), arpeggio notes
const CHORDS = [
  { root: 45, pad: [57, 60, 64, 71], arp: [64, 67, 71, 72] },
  { root: 41, pad: [53, 57, 60, 67], arp: [60, 64, 67, 69] },
  { root: 48, pad: [55, 59, 64, 67], arp: [64, 67, 71, 72] },
  { root: 43, pad: [55, 59, 62, 64], arp: [62, 67, 69, 71] },
];

function reverb(ac) {
  const len = ac.sampleRate * 2.4, buf = ac.createBuffer(2, len, ac.sampleRate);
  for (let c = 0; c < 2; c++) { const d = buf.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3); }
  const cv = ac.createConvolver(); cv.buffer = buf; return cv;
}

function note(ac, dest, freq, t, dur, type, peak, attack = 0.02) {
  const o = ac.createOscillator(), g = ac.createGain(); o.type = type; o.frequency.value = freq;
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(peak, t + attack); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g); g.connect(dest); o.start(t); o.stop(t + dur + 0.05);
}

function scheduleBar(ac, bus, wet, t, idx) {
  const c = CHORDS[idx % CHORDS.length];
  c.pad.forEach((n, i) => { note(ac, bus, midi(n) * (i % 2 ? 1.003 : 0.997), t, BAR * 1.05, 'triangle', 0.05, 0.5); });
  note(ac, bus, midi(c.root), t, BEAT * 1.8, 'sine', 0.2, 0.03); note(ac, bus, midi(c.root), t + BEAT * 2.5, BEAT * 1.2, 'sine', 0.14, 0.03);
  // sparse pluck arpeggio with a little swing, quiet and reverbed
  [0, 1, 2, 3, 4, 5, 6, 7].forEach((s) => {
    if (s % 2 === 1 && Math.random() < 0.35) return;
    const when = t + s * (BEAT / 2) + (s % 2 ? BEAT * 0.06 : 0), n = c.arp[(s * 3) % 4] + (s === 7 ? 12 : 0);
    note(ac, wet, midi(n), when, BEAT * 1.1, 'triangle', s % 2 ? 0.045 : 0.07, 0.008);
  });
  // soft kick on beats 1 and 3
  [0, 2].forEach((b) => { const o = ac.createOscillator(), g = ac.createGain(), w = t + b * BEAT; o.frequency.setValueAtTime(110, w); o.frequency.exponentialRampToValueAtTime(40, w + 0.14); g.gain.setValueAtTime(0.16, w); g.gain.exponentialRampToValueAtTime(0.0001, w + 0.22); o.connect(g); g.connect(bus); o.start(w); o.stop(w + 0.25); });
}

function startSynth() {
  const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
  ctx = new AC(); master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination);
  const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 2400; lp.connect(master);
  const dry = ctx.createGain(); dry.gain.value = 1; dry.connect(lp);
  const wet = ctx.createGain(); wet.gain.value = 0.9; const rv = reverb(ctx); const rvOut = ctx.createGain(); rvOut.gain.value = 0.55; wet.connect(rv); rv.connect(rvOut); rvOut.connect(lp); wet.connect(dry);
  let next = ctx.currentTime + 0.15, bar = 0;
  const tick = () => { while (next < ctx.currentTime + 1.2) { scheduleBar(ctx, dry, wet, next, bar++); next += BAR; } };
  tick(); timer = setInterval(tick, 400);
  master.gain.linearRampToValueAtTime(muted ? 0 : VOL, ctx.currentTime + 2.5);
}

export async function startMusic() {
  if (started) return; started = true;
  try {
    const r = await fetch(A('audio/music.mp3'), { method: 'HEAD' });
    if (r.ok && (r.headers.get('content-type') || '').includes('audio')) {
      audioEl = new Audio(A('audio/music.mp3')); audioEl.loop = true; audioEl.volume = muted ? 0 : VOL; await audioEl.play(); return;
    }
  } catch (_) { /* fall through to synth */ }
  startSynth();
}

export function toggleMusic() {
  muted = !muted;
  if (!started) startMusic();
  if (audioEl) audioEl.volume = muted ? 0 : VOL;
  if (ctx && master) master.gain.linearRampToValueAtTime(muted ? 0 : VOL, ctx.currentTime + 0.4);
  return !muted;
}
export const musicOn = () => !muted;
