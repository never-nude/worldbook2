#!/usr/bin/env python3
"""Worldbook: restyle the "countries" reference layer to look like a physical
relief atlas map (the National Geographic / Michelin classroom-wall-map look
Mike referenced with a photo) - pale near-white interiors with each country's
own already-assigned pastel color concentrated as a soft glow right at its
border, fading inward, instead of a flat uniform fill.

Only affects key==="countries". Every other layer (religion, language, GDP,
etc, and Library Globe) is untouched - those still need a flat, unambiguous
choropleth fill to actually convey their data; turning THOSE into a white/edge
look would erase the data signal that's the whole point of a choropleth.

Technique (native MapLibre, no rasterization/precompute needed):
  1. "fills" flat color becomes a warm off-white ("#f5f0e4") only when
     key==="countries", instead of colorExpr("countries") (still per-country
     for every other key, unchanged).
  2. Two new line layers, both sourced from the same "world" GeoJSON and
     colored with the SAME ["get","color_countries"] already on every
     feature (exactly the colors already assigned, per Mike's ask) - one
     wide + heavily blurred (the soft outer bleed), one narrower + lightly
     blurred (a slightly more defined inner band) - stacked between "fills"
     and the existing crisp dark "borders" line, so borders stay crisp on
     top and the glow reads as color hugging each country's edge and fading
     toward the pale interior.
  3. Both new layers start with visibility:"none" in their layout (harmless
     if "countries" isn't the default layer on load) and get toggled by a new
     _isCountriesRef block in setLayer(), mirroring the existing _isAntique
     toggle block already in this function for Library Globe.

Idempotent, pure ASCII source.
Usage: python3 worldbook_countries_relief_edges.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = []  # (name, old, new, mode, sentinel)  mode: "delete" old-first, "insert" new-first
# sentinel = a minimal, order-independent marker used for the already-applied check instead
# of the full `new` text - needed because a LATER patch (worldbook_fix_glow_layer_order.py)
# reorders these same three addLayer calls, which would otherwise make the exact contiguous
# `new1` string stop matching and cause this edit to silently re-apply (and duplicate the
# glow layers -> MapLibre "layer already exists" error) if this script ever runs again after
# that fix. Checking a stable substring instead of the whole reordered block sidesteps that.

# ---- 1. insert the two new glow line layers right before "borders" ----
old1 = 'map.addLayer({id:"borders",type:"line",source:"world",\n    paint:{"line-color":"#05080f","line-width":0.5,"line-opacity-transition":{duration:400}}});'
new1 = (
    'map.addLayer({id:"country-glow-soft",type:"line",source:"world",\n'
    '    layout:{visibility:"none"},\n'
    '    paint:{"line-color":["get","color_countries"],"line-width":9,"line-blur":7,"line-opacity":0.42}}, "borders");\n'
    '  map.addLayer({id:"country-glow-tight",type:"line",source:"world",\n'
    '    layout:{visibility:"none"},\n'
    '    paint:{"line-color":["get","color_countries"],"line-width":3.2,"line-blur":1.6,"line-opacity":0.62}}, "borders");\n'
    '  map.addLayer({id:"borders",type:"line",source:"world",\n'
    '    paint:{"line-color":"#05080f","line-width":0.5,"line-opacity-transition":{duration:400}}});'
)
EDITS.append(("insert country-glow-soft/tight halo layers before borders", old1, new1, "insert", 'id:"country-glow-soft"'))

# ---- 2. flat fill becomes warm off-white for countries only ----
old2 = 'if(!isRaster) map.setPaintProperty("fills","fill-color",colorExpr(key));'
new2 = 'if(!isRaster) map.setPaintProperty("fills","fill-color", key==="countries"?"#f5f0e4":colorExpr(key));'
EDITS.append(("countries fill goes pale off-white, other layers unchanged", old2, new2, "delete", new2))

# ---- 3. toggle the two glow layers on/off alongside the existing _isAntique block ----
old3 = (
    '{ const _isAntique=(key==="antique"&&!subOn);   // Library Globe: mahogany borders + surface grain\n'
    '    if(map.getLayer("borders")) map.setPaintProperty("borders","line-color", _isAntique?"#2b1f16":"#05080f");\n'
    '    const _atx=document.getElementById("antiqueTexture"); if(_atx) _atx.style.opacity=_isAntique?"1":"0"; }'
)
new3 = (
    old3 + '\n'
    '  { const _isCountriesRef=(key==="countries"&&!subOn);   // relief-map look: colored glow hugging each border\n'
    '    if(map.getLayer("country-glow-soft")) map.setLayoutProperty("country-glow-soft","visibility",_isCountriesRef?"visible":"none");\n'
    '    if(map.getLayer("country-glow-tight")) map.setLayoutProperty("country-glow-tight","visibility",_isCountriesRef?"visible":"none"); }'
)
EDITS.append(("toggle glow layers on for countries, off elsewhere", old3, new3, "insert", "_isCountriesRef"))

res = []
for name, old, new, mode, sentinel in EDITS:
    if mode == "insert":
        if sentinel in text:
            res.append((name, "already-applied"))
        elif old in text:
            text = text.replace(old, new, 1)
            res.append((name, "patched"))
        else:
            res.append((name, "ANCHOR-NOT-FOUND"))
    else:  # delete-style: check old first
        if old in text:
            text = text.replace(old, new, 1)
            res.append((name, "patched"))
        elif sentinel in text:
            res.append((name, "already-applied"))
        else:
            res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: countries layer now pale relief-map style with per-country edge glow" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
