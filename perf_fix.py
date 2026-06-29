#!/usr/bin/env python3
"""Performance + reliability fixes for Atlas:
   1. Cache flow arc lines (build once); animate only the dots, at ~30fps. (was: rebuild ALL
      great-circle geometry every frame -> the main slowdown)
   2. Default opening layer = Religion (static choropleth) instead of the animated drug-routes flow.
   3. Wrap map 'load' setup in try/finally so the 'Building your world…' overlay always clears
      even if something (e.g. WebGL/Three.js) throws.
   python3 perf_fix.py index.html index.html  (idempotent)"""
import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'function buildFlowGeo(' not in text, 'perf_fix already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)

# 1) flow animation: build lines once, animate only dots ~30fps
OLD='''function startFlowAnim(){
  if(flowAnim) cancelAnimationFrame(flowAnim);
  let t0=performance.now();
  function step(t){
    if(!flowActive()){ flowAnim=null; return; }
    const phase = ((t-t0)/9000) % 1;            // one full traverse ≈ 9 s
    const fc = flowFeatureCollection(flowKey, phase);
    const ls=map.getSource("flow-lines"), ds=map.getSource("flow-dots");
    if(ls) ls.setData(fc.lines);
    if(ds) ds.setData(fc.dots);
    flowAnim=requestAnimationFrame(step);
  }
  flowAnim=requestAnimationFrame(step);
}'''
NEW='''let FLOWGEO=null;   // cached arc geometry — lines built once, only dots move per frame
function buildFlowGeo(key){
  const F=FLOWS[key]; const lines=[], items=[]; let wmax=0;
  F.edges.forEach(e=>{ if(e.w>wmax) wmax=e.w; });
  const two=F.twoTone;
  F.edges.forEach((e,i)=>{
    if(flowFocusIso && e.from!==flowFocusIso && e.to!==flowFocusIso) return;
    const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to]; if(!a||!b) return;
    const pts=gcPoints(a,b,48);
    const col=e.c||F.color, dotCol=e.dc||F.dotColor||"#cfe2ff";
    if(two){ const mid=Math.floor(pts.length/2);
      lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:F.fromColor},geometry:{type:"LineString",coordinates:pts.slice(0,mid+1)}});
      lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:F.toColor},geometry:{type:"LineString",coordinates:pts.slice(mid)}});
    } else {
      lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:col},geometry:{type:"LineString",coordinates:pts}});
    }
    items.push({pts,nDots:1+Math.round((e.w/wmax)*2),dotCol,two,from:e.from,to:e.to,w:e.w/wmax,i});
  });
  FLOWGEO={key,focus:flowFocusIso,items};
  const ls=map.getSource("flow-lines"); if(ls) ls.setData({type:"FeatureCollection",features:lines});
}
function flowDotsFC(phase){
  const F=FLOWS[FLOWGEO.key], dots=[];
  FLOWGEO.items.forEach(it=>{
    for(let d=0; d<it.nDots; d++){
      const f=( phase + d/it.nDots + it.i*0.013 ) % 1;
      const idx=Math.min(it.pts.length-1, Math.floor(f*it.pts.length));
      const dc = it.two ? (idx<it.pts.length/2?F.fromColor:F.toColor) : it.dotCol;
      dots.push({type:"Feature",properties:{w:it.w,c:dc,from:it.from,to:it.to},geometry:{type:"Point",coordinates:it.pts[idx]}});
    }
  });
  return {type:"FeatureCollection",features:dots};
}
function startFlowAnim(){
  if(flowAnim) cancelAnimationFrame(flowAnim);
  buildFlowGeo(flowKey);                                   // arc lines built ONCE
  let t0=performance.now(), lastDot=0;
  function step(t){
    if(!flowActive()){ flowAnim=null; return; }
    if(!FLOWGEO || FLOWGEO.key!==flowKey || FLOWGEO.focus!==flowFocusIso) buildFlowGeo(flowKey);  // rebuild only when the edge set changes
    if(t-lastDot>=33){                                     // dots at ~30fps, not 60 — halves the per-frame work
      const ds=map.getSource("flow-dots"); if(ds) ds.setData(flowDotsFC(((t-t0)/9000)%1));
      lastDot=t;
    }
    flowAnim=requestAnimationFrame(step);
  }
  flowAnim=requestAnimationFrame(step);
}'''
text=patch(text,OLD,NEW,'flow-anim')

# 2) default opening layer -> static choropleth
text=patch(text,
  '  setLayer("flow_drugs");   // default opening layer = Drug routes',
  '  setLayer("religion");   // default opening layer = Religion (static choropleth — fast, reliable first paint)',
  'default-layer')

# 3) guarantee the loading overlay clears even if setup throws
text=patch(text,
  'map.on("load",()=>{\n  try{ map.setSky({',
  'map.on("load",()=>{ try{\n  try{ map.setSky({',
  'load-open')
text=patch(text,
  '''  updateSunShade();    // day/night now advances smoothly inside the master clock loop (startSpin)
  document.getElementById("loading").style.display="none";
});''',
  '''  updateSunShade();    // day/night now advances smoothly inside the master clock loop (startSpin)
  }catch(_e){ console.error("Atlas init error:",_e); }
  finally{ document.getElementById("loading").style.display="none"; }
});''',
  'load-close')

open(OUT,"w",encoding="utf-8").write(text)
print("OK: flow-line caching + 30fps dots + static default layer + guarded loading overlay")
