#!/usr/bin/env python3
"""Worldbook: make cities reveal as a real population hierarchy, not appear
all at once at the default view.

Mike's ask: "cities should only start to show up once we zoom in, first
country names should appear and then cities, almost like a hierarchy of
population determines when the cities will appear (larger ones appear from
further away, smaller ones appear as you zoom in past a certain threshold)."

Previously tier-1 (capitals/megacities) had minzoom:0 - visible immediately
at the default world view (zoom 1.45), competing with country names right
from the first paint. Country-name labels already follow exactly this
"more important = visible from further away" pattern (each has its own
precomputed minZoom, big countries show at world view, small ones need a
zoom-in) - this fix brings cities in line with that same established
convention instead of introducing a different one, and makes sure NOTHING
in the cities layer shows before the user has actually zoomed in past the
default view.

New thresholds (same relative stagger as before, shifted so nothing shows
at the 1.45 default):
  tier 1 (capitals/megacities) : 0    -> 2.2
  tier 2 (major, pop >= 750k)  : 2    -> 3.6
  tier 3 (midsize, pop >= 200k): 3.5  -> 5.0

Purely a minzoom change - does not touch which layer(s) cities are gated to
(still Countries-reference-only via the existing _isCountriesRef toggle),
font/size/color styling, or the underlying data.

Idempotent, pure ASCII source.
Usage: python3 worldbook_cities_zoomtier_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = "const CITY_MINZ={1:0,2:2,3:3.5};"
NEW = "const CITY_MINZ={1:2.2,2:3.6,3:5.0};   // nothing shows at the default 1.45 view - country names get the first paint to themselves, cities reveal in population order as you zoom in"

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] raise city minzoom tiers so nothing shows at the default view; population hierarchy reveals on zoom-in")
print("OK: cities now reveal by population as you zoom, country names get the world view to themselves" if status in ("patched", "already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
