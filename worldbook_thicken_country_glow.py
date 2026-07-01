#!/usr/bin/env python3
"""Worldbook: make the countries-layer edge glow much thicker/bolder.

Mike's ask: the colored border treatment should read as a real, deliberate
design element that actively emphasizes each country's outline - not just a
subtle tint. Roughly doubled both line widths and bumped opacity/blur to
match: outer soft bleed 9->18px width (blur 7->10), inner defined band
3.2->7px width (blur 1.6->2.2), both opacities nudged up so the color reads
clearly at a glance instead of needing a close zoom to notice.

Only touches the two country-glow paint blocks - crisp dark "borders" line,
fill color, and everything else about the countries layer is unchanged.

Idempotent, pure ASCII source.
Usage: python3 worldbook_thicken_country_glow.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    'paint:{"line-color":["get","color_countries"],"line-width":9,"line-blur":7,"line-opacity":0.42}}, "borders");\n'
    '  map.addLayer({id:"country-glow-tight",type:"line",source:"world",\n'
    '    layout:{visibility:"none"},\n'
    '    paint:{"line-color":["get","color_countries"],"line-width":3.2,"line-blur":1.6,"line-opacity":0.62}}, "borders");'
)
NEW = (
    'paint:{"line-color":["get","color_countries"],"line-width":18,"line-blur":10,"line-opacity":0.5}}, "borders");\n'
    '  map.addLayer({id:"country-glow-tight",type:"line",source:"world",\n'
    '    layout:{visibility:"none"},\n'
    '    paint:{"line-color":["get","color_countries"],"line-width":7,"line-blur":2.2,"line-opacity":0.75}}, "borders");'
)

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] thicken country-glow-soft/tight (roughly 2x width, higher opacity)")
print("OK: country edge glow is now much bolder" if status in ("patched","already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
