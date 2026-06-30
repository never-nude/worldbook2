#!/usr/bin/env python3
"""Worldbook: fix Countries label rendering + small follow-up polish.

Root-caused the country-labels symbol layer rendering zero text:
  1) "Open Sans Regular" is not a valid standalone glyph directory on the
     demotiles.maplibre.org glyph server - confirmed via direct fetch (404).
     The repo only ships it combined as "Open Sans Regular,Arial Unicode MS
     Regular". Switched to "Noto Sans Regular", confirmed 200 on its own.
  2) The visibility toggle for the country-labels layer was only ever wired
     into setFlowBase() (the flow-layer base-painter), which never runs for
     the Countries layer since its type is "reference", not "flow" - so the
     toggle code was dead for the one layer that needed it. Added the real
     toggle into setLayer(), the function that actually handles the Countries
     layer switch (also subOn-aware so this plays nice once subnational
     drill-down labels ship).

Also:
  3) Hide the legend panel entirely when viewing Countries - it is purely
     decorative with no data to key, and the panel was obtrusive on mobile.
  4) Guard the IP geolocation marker so it applies at most once per page load
     (it had two call sites with no shared one-time guard between them).
Idempotent, pure ASCII source.
Usage: python3 worldbook_labels_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ('fix glyph font name (Open Sans Regular alone 404s on demotiles - only the combined Open Sans Regular,Arial Unicode MS Regular stack exists there; Noto Sans Regular is the simplest standalone name that is actually served)',
     '"text-field":["get","name"],"text-font":["Open Sans Regular"],',
     '"text-field":["get","name"],"text-font":["Noto Sans Regular"],',
     'text-font":["Noto Sans Regular"]'),
    ("wire country-labels visibility into setLayer() - it was only ever toggled inside setFlowBase(), which never runs for the Countries reference layer (type 'reference', not 'flow'), so the labels were permanently stuck at visibility:none regardless of the active layer",
     '  updateNoDataHatch(key);\n  drawLegend(key);\n}\n\nfunction layerCfg(key)',
     '  updateNoDataHatch(key);\n  if(map.getLayer("country-labels")) map.setLayoutProperty("country-labels","visibility", (key==="countries"&&!subOn)?"visible":"none");\n  drawLegend(key);\n}\n\nfunction layerCfg(key)',
     'setLayoutProperty("country-labels","visibility", (key==="countries"&&!subOn)'),
    ("hide the legend panel entirely for the Countries reference layer - purely decorative, self-explanatory, no data to key - instead of showing a 'color carries no data' note",
     'function drawLegend(key){\n  const c=layerCfg(key), el=document.getElementById("legend");\n  let b="";\n  if(c.type==="raster"){',
     'function drawLegend(key){\n  const c=layerCfg(key), el=document.getElementById("legend");\n  if(c.type==="reference"){ el.style.display="none"; return; }\n  el.style.display="";\n  let b="";\n  if(c.type==="raster"){',
     'if(c.type==="reference"){ el.style.display="none"; return; }'),
    ('make the IP geolocation marker/flyTo apply exactly once per page load - it could previously run its full body from either of two independent call sites (fetch resolution or map load event) with no shared guard',
     'var _wbGeo=null, _wbGeoMapReady=false;\nfunction _wbApplyGeo(){\n  if(!_wbGeo || !_wbGeoMapReady) return;\n  try{',
     'var _wbGeo=null, _wbGeoMapReady=false, _wbGeoApplied=false;\nfunction _wbApplyGeo(){\n  if(!_wbGeo || !_wbGeoMapReady || _wbGeoApplied) return;\n  _wbGeoApplied=true;\n  try{',
     '_wbGeoApplied=false;\nfunction _wbApplyGeo(){\n  if(!_wbGeo || !_wbGeoMapReady || _wbGeoApplied) return;'),
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
print("OK: labels + polish applied" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
