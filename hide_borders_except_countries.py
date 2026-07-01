#!/usr/bin/env python3
"""worldbook_claude build -- hide the country-outline "borders" layer on every layer
except the Countries reference layer.

Mike's request: shaded/outlined borders on every country polygon made choropleth
layers (religion, language, government type, etc.) look like a fragmented mosaic --
adjacent same-colored countries were visually chopped apart by the outline instead
of reading as one continuous region. Live-verified via javascript_tool
(map.setPaintProperty("borders","line-opacity",0)) before writing this patch --
same-color neighbors (e.g. Algeria/Libya/Niger/Chad/Sudan, all Sunni-majority green)
now correctly blend into one region.

There is exactly one shared "borders" line layer (source "world") used across every
non-raster choropleth layer -- no per-layer border layers exist. setLayer() already
computes an `_isCountriesRef` flag (key==="countries" && !subOn) for this exact
purpose (toggling the relief-map glow/city-dot treatment that's countries-only) --
reused here rather than adding a second, parallel condition.

Two call sites needed, not one: setLayer() handles every non-flow layer, but flow-type
layers (drugs, trade, migration, ...) route through setFlow() and setLayer() returns
early before reaching the _isCountriesRef block -- so setFlow() needs its own
unconditional borders-off line (a flow layer is by definition never "countries").

Idempotent. Usage: python3 hide_borders_except_countries.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

FIXES = [
    ("setLayer: toggle borders opacity with _isCountriesRef",
     '  { const _isCountriesRef=(key==="countries"&&!subOn);   // relief-map look: colored glow hugging each border\n'
     '    if(map.getLayer("country-glow-soft")) map.setLayoutProperty("country-glow-soft","visibility",_isCountriesRef?"visible":"none");',
     '  { const _isCountriesRef=(key==="countries"&&!subOn);   // relief-map look: colored glow hugging each border\n'
     '    if(map.getLayer("borders")) map.setPaintProperty("borders","line-opacity",_isCountriesRef?1:0);\n'
     '    if(map.getLayer("country-glow-soft")) map.setLayoutProperty("country-glow-soft","visibility",_isCountriesRef?"visible":"none");'),
    ("setFlow: borders always off (a flow layer is never countries)",
     'function setFlow(key){\n'
     '  flowKey = key; flowIso=null; flowFocusIso=null;',
     'function setFlow(key){\n'
     '  flowKey = key; flowIso=null; flowFocusIso=null;\n'
     '  if(map.getLayer("borders")) map.setPaintProperty("borders","line-opacity",0);'),
]

results = []
for label, OLD, NEW in FIXES:
    # Check NEW first, unconditionally: the setFlow fix is a pure append (OLD is a
    # prefix of NEW), so once patched, OLD still matches as a substring of NEW --
    # checking "OLD not in text and NEW in text" would miss that and re-append on
    # every run. Checking NEW-in-text first is safe for both append-style and
    # rename-style fixes here (confirmed: none of the OLD/NEW pairs below have NEW
    # as a substring of unpatched OLD, so this can't falsely report "already-applied"
    # before the first real patch).
    if NEW in text:
        results.append((label, "already-applied"))
    elif OLD in text:
        text = text.replace(OLD, NEW, 1)
        results.append((label, "patched"))
    else:
        results.append((label, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for label, status in results:
    print(f"  [{status:>16}] {label}")
    if status not in ("patched", "already-applied"):
        ok = False

print("OK: borders now countries-only" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
