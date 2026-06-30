#!/usr/bin/env python3
"""Worldbook: account for the left/right UI panels when centering the globe.

Mike: "let's also center canada a bit more by default... China too." Checked the
pixel math on the screenshot: the globe renders centered in the FULL browser
window, but the left LAYERS panel (always present on desktop, ~228px) and the
right country-detail panel (380px, only when a country is selected) both eat
into that window without the map ever being told about them. So content is
always optically shifted left of where it should sit in the space you can
actually see - not a wrong center coordinate, a missing accounting for the UI
chrome around it. This is why both Canada (default view, left panel only) and
China (seen earlier with the detail panel also open) read as off-center: same
root cause, different panel combination.

Fix uses MapLibre's native padding option, which is built exactly for this -
it shifts the optical center within the unpadded region instead of moving the
actual geographic center point. Left padding (240px) is set on the initial map
load and stays on whenever the left panel is showing (desktop only - the left
panel and the detail panel both behave differently on phones, already handled
by the existing mobile layout, so padding is skipped there). Right padding
(380px) is added only while the detail panel is open, animated in/out over the
same 280ms the panel itself already uses, so the recentering and the panel
slide happen together.
Idempotent, pure ASCII source.
Usage: python3 worldbook_map_padding.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ("account for the left LAYERS sidebar in the map's default padding",
     'const map = new maplibregl.Map({\n  container:"map",\n  style:{version:8, projection:{type:"globe"},\n    sources:{}, glyphs:"https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",\n    layers:[{id:"bg",type:"background",paint:{"background-color":"rgba(7,11,20,0)"}}]},\n  center:[10,28], zoom:1.45, attributionControl:false, maxZoom:9\n});',
     'const _wbDesktop=()=>!window.matchMedia("(max-width:700px)").matches;   // left LAYERS panel\n// is ~228px wide on desktop only; account for it so content is optically centered in the\n// visible map area, not the full window (which the left panel eats into).\nconst map = new maplibregl.Map({\n  container:"map",\n  style:{version:8, projection:{type:"globe"},\n    sources:{}, glyphs:"https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",\n    layers:[{id:"bg",type:"background",paint:{"background-color":"rgba(7,11,20,0)"}}]},\n  center:[10,28], zoom:1.45, attributionControl:false, maxZoom:9,\n  padding:_wbDesktop()?{top:0,bottom:0,left:240,right:0}:{top:0,bottom:0,left:0,right:0}\n});',
     'const _wbDesktop=()=>!window.matchMedia("(max-width:700px)").matches;   // left LAYERS panel\n// is ~228px wide on desktop only; account for it so content is optically centered in the\n// visible map area, not the full window (which the left panel eats into).\nconst map = new maplibregl.Map({\n  container:"map",\n  style:{version:8, projection:{type:"globe"},\n    sources:{}, glyphs:"https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",\n    layers:[{id:"bg",type:"background",paint:{"background-color":"rgba(7,11,20,0)"}}]},\n  center:[10,28], zoom:1.45, attributionControl:false, maxZoom:9,\n  padding:_wbDesktop()?{top:0,bottom:0,left:240,right:0}:{top:0,bottom:0,left:0,right:0}\n});'),
    ('pad for the detail panel when opened from a country click',
     'currentISO=p.iso3; subOn=false; cleanupSub(); panelOpen=true;\n  { const _pn=document.getElementById("panel"); _pn.style.transform=""; _pn.style.transition="";\n    _pn.classList.add("open"); _pn.classList.remove("min");\n    _pn.classList.toggle("peek", window.matchMedia("(max-width:700px)").matches); }   // phones open at the peek detent',
     'currentISO=p.iso3; subOn=false; cleanupSub(); panelOpen=true;\n  { const _pn=document.getElementById("panel"); _pn.style.transform=""; _pn.style.transition="";\n    _pn.classList.add("open"); _pn.classList.remove("min");\n    _pn.classList.toggle("peek", window.matchMedia("(max-width:700px)").matches); }   // phones open at the peek detent\n  if(_wbDesktop()) map.easeTo({padding:{top:0,bottom:0,left:240,right:380}, duration:280});   // make room for the open detail panel',
     'currentISO=p.iso3; subOn=false; cleanupSub(); panelOpen=true;\n  { const _pn=document.getElementById("panel"); _pn.style.transform=""; _pn.style.transition="";\n    _pn.classList.add("open"); _pn.classList.remove("min");\n    _pn.classList.toggle("peek", window.matchMedia("(max-width:700px)").matches); }   // phones open at the peek detent\n  if(_wbDesktop()) map.easeTo({padding:{top:0,bottom:0,left:240,right:380}, duration:280});   // make room for the open detail panel'),
    ('pad for the detail panel when opened via the Sources index',
     'currentISO=null; panelOpen=true;\n  const pn=document.getElementById("panel");\n  pn.style.transform=""; pn.style.transition="";\n  pn.classList.add("open"); pn.classList.remove("min");\n  pn.classList.toggle("peek", window.matchMedia("(max-width:700px)").matches);',
     'currentISO=null; panelOpen=true;\n  const pn=document.getElementById("panel");\n  pn.style.transform=""; pn.style.transition="";\n  pn.classList.add("open"); pn.classList.remove("min");\n  pn.classList.toggle("peek", window.matchMedia("(max-width:700px)").matches);\n  if(_wbDesktop()) map.easeTo({padding:{top:0,bottom:0,left:240,right:380}, duration:280});',
     'currentISO=null; panelOpen=true;\n  const pn=document.getElementById("panel");\n  pn.style.transform=""; pn.style.transition="";\n  pn.classList.add("open"); pn.classList.remove("min");\n  pn.classList.toggle("peek", window.matchMedia("(max-width:700px)").matches);\n  if(_wbDesktop()) map.easeTo({padding:{top:0,bottom:0,left:240,right:380}, duration:280});'),
    ('revert padding to left-only when the detail panel closes',
     'function closePanel(){\n  const pn=document.getElementById("panel");\n  pn.style.transition=""; pn.style.transform="";\n  pn.classList.remove("open","min","peek");\n  document.getElementById("hint").style.right="16px";\n  panelOpen=false; lastInteract=Date.now();\n  if(subOn) drillOut();\n}',
     'function closePanel(){\n  const pn=document.getElementById("panel");\n  pn.style.transition=""; pn.style.transform="";\n  pn.classList.remove("open","min","peek");\n  document.getElementById("hint").style.right="16px";\n  panelOpen=false; lastInteract=Date.now();\n  if(subOn) drillOut();\n  if(_wbDesktop()) map.easeTo({padding:{top:0,bottom:0,left:240,right:0}, duration:280});   // back to just the left panel\n}',
     'function closePanel(){\n  const pn=document.getElementById("panel");\n  pn.style.transition=""; pn.style.transform="";\n  pn.classList.remove("open","min","peek");\n  document.getElementById("hint").style.right="16px";\n  panelOpen=false; lastInteract=Date.now();\n  if(subOn) drillOut();\n  if(_wbDesktop()) map.easeTo({padding:{top:0,bottom:0,left:240,right:0}, duration:280});   // back to just the left panel\n}'),
]

res = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
        res.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: map now accounts for left/right panel chrome" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
