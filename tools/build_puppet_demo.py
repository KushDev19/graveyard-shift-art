"""Writes frontend/public/assets/ship/crew/puppet_demo.html: a self-contained page that animates the
SVG crew puppet in code (idle / walk / run / ghost / impostor visor / surprised hop, 10 colors, facing).
The animation functions are the reference for the Wizard-of-Oz prototype and the Phaser rig.
URL params for screenshots: ?mode=walk&t=0.3&ghost=1&color=tomato freezes a single frame."""
from svgtools import ROOT

SVG = (ROOT / "frontend/public/assets/ship/crew/crew_puppet.svg").read_text(encoding="utf-8")
OUT = ROOT / "frontend/public/assets/ship/crew/puppet_demo.html"

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crew Puppet Demo</title>
<style>
  :root { --bg:#1B1830; --cream:#F4E6C8; --amber:#F5A54A; --plum:#2A1E35; --teal:#2F6F73; }
  body { margin:0; background:var(--bg); color:var(--cream); font:15px/1.4 system-ui, sans-serif; }
  header { padding:12px 16px; display:flex; flex-wrap:wrap; gap:8px; align-items:center; }
  header .sep { width:1px; height:26px; background:#3D2A4F; margin:0 6px; }
  button { background:var(--teal); color:var(--cream); border:0; border-radius:999px; padding:8px 14px; font-weight:700; cursor:pointer; }
  button.on { background:var(--amber); color:var(--plum); }
  .sw { width:26px; height:26px; border-radius:50%; border:3px solid var(--plum); padding:0; }
  .sw.on { outline:3px solid var(--cream); }
  #stage { position:relative; height:520px; overflow:hidden; background:#2B4A5E; }
  #floor { position:absolute; left:0; right:0; bottom:0; height:130px;
           background:repeating-linear-gradient(90deg,#24425A 0 158px,#1C344A 158px 162px); }
  #main { position:absolute; left:50%; bottom:46px; width:340px; height:425px; margin-left:-170px; }
  #main svg, .mini svg { width:100%; height:100%; overflow:visible; display:block; }
  .flip svg { transform:scaleX(-1); }
  #crowd { display:flex; gap:6px; justify-content:center; padding:14px 8px; background:#24425A; flex-wrap:wrap; }
  .mini { width:96px; height:120px; }
  p.note { padding:4px 16px 16px; opacity:.75; margin:0; }
</style></head>
<body>
<header id="ui"></header>
<div id="stage"><div id="floor"></div><div id="main"></div></div>
<div id="crowd"></div>
<p class="note">Animated entirely in code from crew_puppet.svg: legs/arms rotate around their pivots, the body bobs and rocks,
the antenna lags behind, the visor blinks. Arrow keys flip facing. Space = surprised hop (meeting called).</p>
<script>
const SVG_TEXT = `__SVG__`;
const COLORS = {tomato:"#E4483C", tangerine:"#F28A2E", mustard:"#E9C046", lime:"#A6D64A", mint:"#6FD6B0",
                sky:"#6EC3F0", cobalt:"#3F5FD9", grape:"#8E5AC8", bubblegum:"#F07BB5", cream:"#F4E6C8"};

function hexToHsl(h){ let r=parseInt(h.slice(1,3),16)/255,g=parseInt(h.slice(3,5),16)/255,b=parseInt(h.slice(5,7),16)/255;
  const mx=Math.max(r,g,b), mn=Math.min(r,g,b); let H=0,S=0; const L=(mx+mn)/2;
  if(mx!==mn){ const d=mx-mn; S=L>.5?d/(2-mx-mn):d/(mx+mn);
    H = mx===r ? (g-b)/d+(g<b?6:0) : mx===g ? (b-r)/d+2 : (r-g)/d+4; H/=6; }
  return [H,S,L]; }
function hslToHex(H,S,L){ const f=(p,q,t)=>{ if(t<0)t+=1; if(t>1)t-=1; if(t<1/6)return p+(q-p)*6*t; if(t<1/2)return q; if(t<2/3)return p+(q-p)*(2/3-t)*6; return p; };
  let r,g,b; if(S===0){ r=g=b=L; } else { const q=L<.5?L*(1+S):L+S-L*S, p=2*L-q; r=f(p,q,H+1/3); g=f(p,q,H); b=f(p,q,H-1/3); }
  return "#"+[r,g,b].map(x=>Math.round(x*255).toString(16).padStart(2,"0")).join(""); }
function tone(hex,f){ const [h,s,l]=hexToHsl(hex); return hslToHex(h,s,Math.min(.95,l*f)); }
function styleFor(hex){ return hex ? `--suit:${hex};--suit-shade:${tone(hex,.78)};--suit-back:${tone(hex,.64)};--suit-light:${tone(hex,1.16)}` : ""; }

const IDS = ["crew","leg_back","arm_back","leg_front","arm_front","antenna","visor","visor_glow","visor_blink",
             "visor_surprised","visor_coral","visor_ghost","ghost_tail"];
function makePuppet(el, color, offset){
  el.innerHTML = SVG_TEXT; const svg = el.querySelector("svg"); svg.setAttribute("style", styleFor(color));
  const parts = {}, piv = {};
  for (const id of IDS){ parts[id] = svg.querySelector("#"+id); const p = parts[id].getAttribute("data-pivot"); if (p) piv[id] = p.split(",").map(Number); }
  return {el, svg, parts, piv, offset: offset||0};
}
function rot(p,id,a){ const [x,y]=p.piv[id]; p.parts[id].setAttribute("transform",`rotate(${a.toFixed(2)} ${x} ${y})`); }
function show(p,id,on){ p.parts[id].setAttribute("display", on ? "inline" : "none"); }

// one frame of animation; t in seconds
function animate(p, t, s){
  const tt = t + p.offset;
  const speed = s.mode==="run" ? 11 : s.mode==="walk" ? 7 : 0;
  const ph = tt*speed, sn = Math.sin(ph);
  let leg=0, arm=0, bob=0, rock=0, lean=0, ant=0, sy=1;
  if (s.mode==="walk"){ leg=24*sn; arm=-20*sn; bob=-Math.abs(sn)*12; rock=3*sn; lean=2; ant=-8*Math.sin(ph-.9); }
  else if (s.mode==="run"){ leg=38*sn; arm=-46*sn; bob=-Math.abs(sn)*22; rock=4*sn; lean=9; ant=-14*Math.sin(ph-.9)-10; }
  else { bob=Math.sin(tt*2.2)*3; ant=4*Math.sin(tt*1.6); sy=1+.014*Math.sin(tt*2.2); }
  if (s.ghost){ leg=0; bob=Math.sin(tt*2.4)*10-16; rock=3*Math.sin(tt*1.7); sy=1; }
  const hop = s.hopUntil && t < s.hopUntil ? Math.sin((s.hopUntil - t)/.6*Math.PI) : 0;
  bob -= 34*Math.max(0, hop);
  rot(p,"leg_front",leg); rot(p,"leg_back",-leg); rot(p,"arm_front",arm); rot(p,"arm_back",-arm); rot(p,"antenna",ant - hop*12);
  p.parts.crew.setAttribute("transform",
    `translate(0 ${bob.toFixed(2)}) rotate(${(rock+lean).toFixed(2)} 320 790) translate(320 790) scale(${(2-sy).toFixed(4)} ${sy.toFixed(4)}) translate(-320 -790)`);
  const blink = !s.ghost && (tt % 3.4) < .13;
  const v = hop>0 ? "visor_surprised" : s.ghost ? "visor_ghost" : blink ? "visor_blink" : s.impostor ? "visor_coral" : "visor";
  for (const id of ["visor","visor_coral","visor_ghost","visor_blink","visor_surprised"]) show(p,id,id===v);
  show(p,"visor_glow", v==="visor"); show(p,"ghost_tail", s.ghost); show(p,"leg_front", !s.ghost); show(p,"leg_back", !s.ghost);
  p.svg.style.opacity = s.ghost ? .62 : 1;
}

const state = {mode:"walk", ghost:false, impostor:false, color:"tomato", facing:1, hopUntil:0};
const main = makePuppet(document.getElementById("main"), COLORS[state.color]);
const crowd = Object.keys(COLORS).filter(c=>c!==state.color).slice(0,8).map((c,i)=>{
  const d = document.createElement("div"); d.className="mini"; document.getElementById("crowd").appendChild(d);
  return makePuppet(d, COLORS[c], i*.37); });

// UI
const ui = document.getElementById("ui");
function btn(label, on, fn){ const b=document.createElement("button"); b.textContent=label; b.onclick=()=>{fn(); render();}; ui.appendChild(b); return [b,on]; }
const toggles = [];
for (const m of ["idle","walk","run"]) toggles.push(btn(m[0].toUpperCase()+m.slice(1), ()=>state.mode===m, ()=>state.mode=m));
ui.appendChild(Object.assign(document.createElement("span"),{className:"sep"}));
toggles.push(btn("Ghost", ()=>state.ghost, ()=>state.ghost=!state.ghost));
toggles.push(btn("Impostor visor", ()=>state.impostor, ()=>state.impostor=!state.impostor));
toggles.push(btn("Meeting called!", ()=>false, ()=>state.hopUntil=performance.now()/1000+.6));
toggles.push(btn("Flip", ()=>state.facing<0, ()=>state.facing*=-1));
ui.appendChild(Object.assign(document.createElement("span"),{className:"sep"}));
const swatches = Object.entries(COLORS).map(([name,hex])=>{ const b=document.createElement("button"); b.className="sw"; b.title=name;
  b.style.background=hex; b.onclick=()=>{ state.color=name; main.svg.setAttribute("style", styleFor(hex)); render(); }; ui.appendChild(b); return [b,name]; });
function render(){ for (const [b,on] of toggles) b.classList.toggle("on", on());
  for (const [b,name] of swatches) b.classList.toggle("on", state.color===name);
  document.getElementById("main").classList.toggle("flip", state.facing<0); }
addEventListener("keydown", e=>{ if(e.key==="ArrowLeft") state.facing=-1; if(e.key==="ArrowRight") state.facing=1;
  if(e.key===" "){ state.hopUntil=performance.now()/1000+.6; e.preventDefault(); } render(); });

const floor = document.getElementById("floor");
function frame(t){
  const s = state; animate(main, t, s); for (const p of crowd) animate(p, t, {...s, impostor:false, hopUntil:s.hopUntil});
  const v = s.ghost ? 60 : s.mode==="run" ? 420 : s.mode==="walk" ? 190 : 0;
  floor.style.backgroundPosition = `${(-t*v*s.facing).toFixed(1)}px 0`;
}
const q = new URLSearchParams(location.search);
if (q.has("t")){
  state.mode = q.get("mode")||"walk"; state.ghost = q.get("ghost")==="1"; state.impostor = q.get("impostor")==="1";
  if (q.get("color")) { state.color=q.get("color"); main.svg.setAttribute("style", styleFor(COLORS[state.color])); }
  render(); frame(parseFloat(q.get("t")));
} else {
  render(); const loop = ms => { frame(ms/1000); requestAnimationFrame(loop); }; requestAnimationFrame(loop);
}
</script>
</body></html>
"""

OUT.write_text(HTML.replace("__SVG__", SVG), encoding="utf-8")
print("wrote", OUT)
