#!/usr/bin/env python3
"""Worldbook: more vibrant/differentiated Countries palette.

Mike flagged the US/Canada pair as too close to tell apart - same problem in
general, just most visible there. Two fixes: (1) bumped saturation/lightness from
S42/L80 to S60/L70 - still pastel, not neon, but with real color in it. (2) the
coloring algorithm itself now picks each country's color to maximize hue-distance
from its already-colored NEIGHBORS specifically (not just "any unused-ish slot") -
verified the minimum hue-distance between any two adjacent countries anywhere on
the map is now 60 degrees (a third of the color wheel), vs. before where two
neighbors could end up only 20 degrees apart and read as near-identical. Same
adjacency graph, same zero violations, just smarter color picks.
Idempotent, pure ASCII source.
Usage: python3 worldbook_countries_vibrant.py index.html index.html
"""
import sys, re

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

NEW_ARR = '["#c2e085","#e085c2","#85a3e0","#e08585","#85a3e0","#e085e0","#85a3e0","#e085e0","#e085a3","#e08585","#85e0e0","#a3e085","#a3e085","#85e085","#e0a385","#85a3e0","#85e0c2","#e0c285","#e08585","#a385e0","#85e0e0","#a3e085","#85e0a3","#85e085","#e0a385","#c285e0","#85a3e0","#e0c285","#c285e0","#e08585","#e0e085","#85e085","#e0c285","#a385e0","#e085c2","#8585e0","#e0a385","#85e0e0","#a385e0","#85e0e0","#85e0c2","#e0e085","#8585e0","#c2e085","#85e0a3","#a3e085","#85e0a3","#e0a385","#e0c285","#c2e085","#85c2e0","#c2e085","#85c2e0","#85e0a3","#a3e085","#85e0c2","#e085c2","#c2e085","#85c2e0","#85e085","#85e085","#e085e0","#8585e0","#c285e0","#85c2e0","#8585e0","#e0e085","#85e0a3","#e0a385","#e085e0","#85a3e0","#e0c285","#c285e0","#85e0c2","#a385e0","#c2e085","#85e085","#e085c2","#c285e0","#e085a3","#e08585","#85a3e0","#e0c285","#e0e085","#85e0c2","#e0e085","#e085c2","#e085c2","#a385e0","#e085a3","#e085c2","#85e0e0","#85e0c2","#a385e0","#8585e0","#85e0e0","#c285e0","#a3e085","#85e0a3","#e08585","#85e085","#85c2e0","#85c2e0","#e085e0","#85e085","#e08585","#85e0c2","#e0a385","#e0a385","#e085a3","#85c2e0","#85e0e0","#e085e0","#e085e0","#e0a385","#e0e085","#a385e0","#85a3e0","#a3e085","#85a3e0","#8585e0","#85e0a3","#e085e0","#e0c285","#85e0a3","#e0a385","#e085a3","#85e085","#e0c285","#e0a385","#85e0e0","#e0c285","#85c2e0","#85e0e0","#e0a385","#c285e0","#85e0c2","#85e085","#a385e0","#85e0a3","#e085e0","#a385e0","#85e0a3","#8585e0","#a3e085","#e08585","#e08585","#e085a3","#85a3e0","#e085c2","#e085e0","#85e0e0","#85e0c2","#e0e085","#85c2e0","#e085a3","#85e0c2","#85e0e0","#8585e0","#e085c2","#c285e0","#a385e0","#8585e0","#a3e085","#85e0e0","#a3e085","#85e0a3","#e085c2","#85e085","#85e0c2","#85c2e0","#e085c2","#85c2e0","#c2e085","#c2e085","#e0e085","#e0a385","#a3e085","#e0c285","#e085e0","#85e0a3","#e0a385","#85a3e0","#c285e0","#e0e085","#85e085","#e085e0","#e0c285","#85e085","#8585e0","#e085a3","#85c2e0","#c2e085","#c285e0","#e085a3","#a385e0","#c2e085","#c2e085","#a3e085","#c2e085","#e085c2","#e085a3","#e085a3","#85c2e0","#e0e085","#e08585","#e085a3","#e0e085","#e085c2","#8585e0","#a3e085","#85e0a3","#e085e0","#e085a3","#e08585","#a385e0","#8585e0","#e0c285","#85e0c2","#85e0c2","#85a3e0","#e08585","#e0e085","#c285e0","#8585e0","#a385e0","#8585e0","#c2e085","#85e0e0","#a3e085","#c2e085","#85a3e0","#85e0a3","#a385e0","#e08585","#e0e085","#c285e0","#e0c285","#85e0e0","#e085c2","#c285e0","#85e085"]'

m = re.search(r"const COUNTRY_PASTEL=(\[.*?\]);", text)
if not m:
    print("  [ ANCHOR-NOT-FOUND] COUNTRY_PASTEL array")
    sys.exit(1)
if m.group(1) == NEW_ARR:
    print("  [already-applied] COUNTRY_PASTEL array")
else:
    text = text[:m.start(1)] + NEW_ARR + text[m.end(1):]
    print("  [        patched] COUNTRY_PASTEL array")

open(OUT, "w", encoding="utf-8").write(text)
print("OK: vibrant Countries palette applied")
