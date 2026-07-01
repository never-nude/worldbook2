#!/usr/bin/env python3
"""Worldbook: fix a real bug in the just-shipped countries-relief-edges patch.

Root cause (found live: fill went pale as expected, but zero edge glow showed -
country-glow-soft/tight simply didn't exist on the map at all): the previous
patch added the two new glow line layers using `map.addLayer({...}, "borders")`
- the second argument tells MapLibre "insert this layer immediately below the
layer with id 'borders'" - but those two addLayer calls ran BEFORE the actual
"borders" layer was created a few lines later in the same script. MapLibre
throws ("Layer with id 'borders' does not exist on this map") the instant it
can't resolve a beforeId, which aborts the rest of that init pass - so neither
glow layer ever got created. Fix: create "borders" first (unchanged, original
position), THEN add the two glow layers referencing it as beforeId - now it
genuinely exists by the time they run. Pure reorder, no other logic changes.

Idempotent, pure ASCII source.
Usage: python3 worldbook_fix_glow_layer_order.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

GLOW_SOFT = (
    'map.addLayer({id:"country-glow-soft",type:"line",source:"world",\n'
    '    layout:{visibility:"none"},\n'
    '    paint:{"line-color":["get","color_countries"],"line-width":9,"line-blur":7,"line-opacity":0.42}}, "borders");'
)
GLOW_TIGHT = (
    'map.addLayer({id:"country-glow-tight",type:"line",source:"world",\n'
    '    layout:{visibility:"none"},\n'
    '    paint:{"line-color":["get","color_countries"],"line-width":3.2,"line-blur":1.6,"line-opacity":0.62}}, "borders");'
)
BORDERS = (
    'map.addLayer({id:"borders",type:"line",source:"world",\n'
    '    paint:{"line-color":"#05080f","line-width":0.5,"line-opacity-transition":{duration:400}}});'
)

BUGGY = "  " + GLOW_SOFT + "\n  " + GLOW_TIGHT + "\n  " + BORDERS
FIXED = "  " + BORDERS + "\n  " + GLOW_SOFT + "\n  " + GLOW_TIGHT

if BUGGY in text:
    text = text.replace(BUGGY, FIXED, 1)
    status = "patched"
elif FIXED in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] reorder borders before its two dependent glow layers")
print("OK: country-glow-soft/tight now actually get created (borders exists first)" if status in ("patched", "already-applied") else "WARN: anchor not found - nothing broken, but not fixed")
sys.exit(0 if status in ("patched", "already-applied") else 1)
