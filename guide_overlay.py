#!/usr/bin/env python3
"""Add a Guide/index overlay to Worldbook: a '?' button (always available) that opens a
short intro + an auto-generated, grouped index of every layer (built from META.layers,
LAYER_PROV.metric, and FLOWS.desc, so it stays in sync). Auto-shows once on first visit
(localStorage), dismissable by X / Esc / backdrop. Idempotent, pure ASCII.
Usage: python3 guide_overlay.py index.html index.html"""
import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
t=open(INP,encoding="utf-8").read()
if 'id="guideBtn"' in t:
    open(OUT,"w",encoding="utf-8").write(t); print("  [already-applied]"); print("OK (no-op)"); sys.exit(0)
def once(s,a,b,l):
    n=s.count(a); assert n==1,"anchor %s: %d matches"%(l,n); return s.replace(a,b)

CSS = """
  /* Guide / index overlay */
  #guideBtn{background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:9px;width:30px;height:30px;font-size:15px;font-weight:600;cursor:pointer;pointer-events:auto;margin-left:10px}
  #guideBtn:hover{border-color:var(--accent)}
  #guide{position:absolute;inset:0;z-index:40;display:none;align-items:center;justify-content:center;background:rgba(5,8,14,.55);backdrop-filter:blur(3px)}
  #guide.open{display:flex}
  #guide .g-card{background:var(--panel);border:1px solid var(--line);border-radius:16px;max-width:540px;width:90vw;max-height:84vh;overflow-y:auto;padding:22px 24px;position:relative;box-shadow:0 24px 70px rgba(0,0,0,.6)}
  #guide .g-x{position:absolute;top:12px;right:12px;background:var(--chip);border:1px solid var(--line);color:var(--ink);width:30px;height:30px;border-radius:8px;cursor:pointer;font-size:16px;line-height:1}
  #guide .g-h{font-size:22px;font-weight:680;letter-spacing:.2px}
  #guide .g-sub{color:var(--muted);font-size:13px;margin-top:4px}
  #guide .g-tips{font-size:13px;margin:14px 0 2px;line-height:1.55}
  #guide .g-idxh{font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);font-weight:600;margin:16px 0 6px}
  #guide .g-grp{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--accent);font-weight:600;margin:12px 0 4px}
  #guide .g-row{display:flex;flex-direction:column;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.05)}
  #guide .g-l{font-size:13px;font-weight:600}
  #guide .g-d{font-size:12px;color:var(--muted);line-height:1.4;margin-top:1px}
  #guide .g-foot{color:var(--muted);font-size:11.5px;margin-top:16px}
</style>"""
t=once(t,"</style>",CSS,"guide-css")

# button in the top bar, right after the title
t=once(t,
  '<h1>Atlas<span id="subtitle">a layered world map</span></h1>',
  '<h1>Atlas<span id="subtitle">a layered world map</span></h1>\n  <button id="guideBtn" title="Guide and index - what is this?">?</button>',
  "guide-btn")

# overlay container
t=once(t,'<div id="topbar">','<div id="guide"></div>\n<div id="topbar">',"guide-div")

# JS: define guide functions before wireTimeBar
JS = r"""function _guideIdx(){
  var prov=(typeof LAYER_PROV!=="undefined")?LAYER_PROV:{}, groups={}, order=[];
  META.layers.forEach(function(l){ if(!groups[l.group]){groups[l.group]=[];order.push(l.group);} groups[l.group].push(l); });
  var h="";
  order.forEach(function(g){
    h+='<div class="g-grp">'+g+'</div>';
    groups[g].forEach(function(l){
      var d="", pk=(typeof provKeyFor==="function")?provKeyFor(l.key):l.key;
      if(prov[pk]&&prov[pk].metric) d=prov[pk].metric;
      else if(l.type==="flow"&&typeof FLOWS!=="undefined"&&l.flowKey&&FLOWS[l.flowKey]&&FLOWS[l.flowKey].desc) d=FLOWS[l.flowKey].desc;
      h+='<div class="g-row"><span class="g-l">'+l.label+'</span>'+(d?'<span class="g-d">'+d+'</span>':'')+'</div>';
    });
  });
  return h;
}
function buildGuide(){
  var el=document.getElementById("guide"); if(!el) return;
  el.innerHTML='<div class="g-card">'
    +'<button class="g-x" id="guideX" title="Close">'+String.fromCharCode(215)+'</button>'
    +'<div class="g-h">Worldbook</div>'
    +'<div class="g-sub">A layered world map - how the facts relate, and why.</div>'
    +'<div class="g-tips">Tap a country for its full profile. Switch layers from the panel at left. Scrub or play time along the bottom. Every figure is sourced - open any layer to see where it comes from.</div>'
    +'<div class="g-idxh">What is in here</div>'
    +'<div class="g-idx">'+_guideIdx()+'</div>'
    +'<div class="g-foot">Reopen this anytime with the ? button, top-left.</div>'
    +'</div>';
  var x=document.getElementById("guideX"); if(x) x.onclick=closeGuide;
}
function openGuide(){ var el=document.getElementById("guide"); if(!el)return; if(!el.dataset.built){ buildGuide(); el.dataset.built="1"; } el.classList.add("open"); }
function closeGuide(){ var el=document.getElementById("guide"); if(el) el.classList.remove("open"); try{ localStorage.setItem("wb_seen_guide","1"); }catch(e){} }
function initGuide(){
  var b=document.getElementById("guideBtn"); if(b) b.onclick=openGuide;
  var el=document.getElementById("guide");
  if(el) el.addEventListener("click",function(e){ if(e.target===el) closeGuide(); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape") closeGuide(); });
  var seen=false; try{ seen=!!localStorage.getItem("wb_seen_guide"); }catch(e){}
  if(!seen) setTimeout(openGuide,800);
}
function wireTimeBar(){"""
t=once(t,"function wireTimeBar(){",JS,"guide-funcs")

# JS: call initGuide once, right after wireTimeBar() runs at startup
t=once(t,"wireTimeBar();","wireTimeBar(); try{ initGuide(); }catch(e){}","guide-init-call")

open(OUT,"w",encoding="utf-8").write(t)
print("  [patched] Guide/index overlay added"); print("OK"); sys.exit(0)
