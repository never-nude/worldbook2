#!/usr/bin/env python3
"""Worldbook: prune the Library Globe palette to strictly brown/ochre/sienna.

Old 14-color antique palette had 5 tones that don't belong in a "polished
mahogany / fine library" scheme - muted sage/olive (x2), sage-gray, teal-slate,
and dusty rose/mauve. Dropped those, kept the 9 genuine brown/ochre/sienna
survivors, and added 5 more strictly-warm tones (checked: all hues 5-41 degrees,
i.e. red-brown through gold - nothing green/blue/purple/pink) for the same
14-color total the adjacency-graph coloring had before, so conflict-avoidance
doesn't get starved by a suddenly-smaller palette.

Re-ran the full pipeline against live MAPDATA: shapely adjacency graph (242
countries, 329 border-sharing edges, buffer(0.02) touch-detection + bbox
pre-filter + prepared-geometry intersection tests), Welsh-Powell greedy
coloring (highest-degree country first, least-used-so-far color as tie-break
for even palette distribution), with a perceptual-distance (RGB Euclidean
<40) rejection pass so literal geographic neighbors don't get similar-looking
colors even when both are technically "different" hex values. Result: 0 exact
color clashes across all 329 shared borders, only 3 residual perceptually-
close pairs (Zambia/Botswana, Namibia/Botswana - same two accepted in the
original pastel-adjacent pass as fine given the border line always
disambiguates them; plus one new one, Azerbaijan/Armenia, same reasoning).
Usage spread stayed even: each of the 14 colors used 17 or 18 times.

Only touches COUNTRY_ANTIQUE (used solely by color_antique, which only
feeds the antique/Library Globe layer) - COUNTRY_PASTEL and every other
layer's colors are untouched.

Idempotent, pure ASCII source.
Usage: python3 worldbook_antique_palette.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = 'const COUNTRY_ANTIQUE=["#b08968","#9c6b4a","#c9a15a","#a8493f","#c4a35f","#a05c3f","#5f7a6e","#a8493f","#7c8471","#96694f","#c9a15a","#b5652f","#8a9a5b","#a8493f","#c17f3e","#6f7d55","#b5652f","#9c6b4a","#b08968","#7c8471","#a05c3f","#8b5e6b","#c4a35f","#5f7a6e","#96694f","#c9a15a","#b5652f","#8a9a5b","#a8493f","#c17f3e","#6f7d55","#b5652f","#b08968","#8b5e6b","#9c6b4a","#8b5e6b","#b08968","#a05c3f","#9c6b4a","#b08968","#9c6b4a","#a8493f","#c4a35f","#c4a35f","#96694f","#7c8471","#a05c3f","#8b5e6b","#9c6b4a","#a8493f","#5f7a6e","#c4a35f","#5f7a6e","#a05c3f","#a05c3f","#9c6b4a","#7c8471","#c9a15a","#7c8471","#8b5e6b","#5f7a6e","#8a9a5b","#c4a35f","#c4a35f","#5f7a6e","#7c8471","#c4a35f","#96694f","#96694f","#b08968","#c9a15a","#b5652f","#8a9a5b","#a8493f","#c17f3e","#b5652f","#b5652f","#7c8471","#8b5e6b","#c9a15a","#c17f3e","#96694f","#6f7d55","#c4a35f","#b5652f","#6f7d55","#8b5e6b","#b5652f","#b08968","#7c8471","#5f7a6e","#b5652f","#9c6b4a","#9c6b4a","#b08968","#7c8471","#5f7a6e","#a05c3f","#8b5e6b","#a05c3f","#c4a35f","#c17f3e","#c17f3e","#96694f","#c4a35f","#c9a15a","#8a9a5b","#c9a15a","#a05c3f","#5f7a6e","#5f7a6e","#b5652f","#96694f","#8a9a5b","#c9a15a","#a8493f","#6f7d55","#b5652f","#a8493f","#c9a15a","#8b5e6b","#6f7d55","#8b5e6b","#7c8471","#96694f","#b08968","#c9a15a","#8a9a5b","#c17f3e","#b5652f","#96694f","#8a9a5b","#6f7d55","#7c8471","#b08968","#a8493f","#c17f3e","#5f7a6e","#5f7a6e","#8b5e6b","#5f7a6e","#8a9a5b","#a8493f","#96694f","#c17f3e","#6f7d55","#b08968","#b08968","#c9a15a","#96694f","#7c8471","#a05c3f","#a8493f","#9c6b4a","#6f7d55","#c17f3e","#c17f3e","#8b5e6b","#b5652f","#5f7a6e","#8a9a5b","#b08968","#7c8471","#8a9a5b","#a05c3f","#8b5e6b","#c4a35f","#5f7a6e","#96694f","#6f7d55","#c9a15a","#9c6b4a","#8b5e6b","#c4a35f","#c4a35f","#5f7a6e","#a05c3f","#a8493f","#a8493f","#b5652f","#c17f3e","#8a9a5b","#a8493f","#6f7d55","#8a9a5b","#c17f3e","#9c6b4a","#c17f3e","#9c6b4a","#c4a35f","#c9a15a","#6f7d55","#c9a15a","#6f7d55","#8a9a5b","#c9a15a","#7c8471","#a05c3f","#a8493f","#c9a15a","#96694f","#9c6b4a","#b08968","#b5652f","#8b5e6b","#a05c3f","#9c6b4a","#6f7d55","#96694f","#8b5e6b","#a8493f","#b5652f","#c17f3e","#c17f3e","#9c6b4a","#b08968","#96694f","#9c6b4a","#6f7d55","#b08968","#8a9a5b","#7c8471","#a05c3f","#7c8471","#a05c3f","#8b5e6b","#c4a35f","#5f7a6e","#96694f","#c9a15a","#c17f3e","#b08968","#b5652f","#8a9a5b","#6f7d55","#6f7d55","#8a9a5b","#7c8471","#a05c3f","#8a9a5b","#c4a35f","#a8493f"]'
NEW = 'const COUNTRY_ANTIQUE=["#6b4226","#c4a35f","#c98a52","#c17f3e","#c4a35f","#a05c3f","#c98a52","#c98a52","#a05c3f","#dbb877","#c9a15a","#b5652f","#a8493f","#c17f3e","#9c6b4a","#b08968","#a8493f","#a05c3f","#c4a35f","#96694f","#d4a84a","#8b4a2b","#c98a52","#6b4226","#dbb877","#c9a15a","#b5652f","#a8493f","#c17f3e","#9c6b4a","#b08968","#c98a52","#c9a15a","#c98a52","#dbb877","#dbb877","#a05c3f","#9c6b4a","#a05c3f","#c4a35f","#9c6b4a","#b5652f","#c98a52","#8b4a2b","#dbb877","#96694f","#c17f3e","#96694f","#b5652f","#c4a35f","#c9a15a","#b08968","#6b4226","#d4a84a","#c98a52","#c9a15a","#a05c3f","#b08968","#d4a84a","#8b4a2b","#b5652f","#96694f","#c98a52","#96694f","#6b4226","#96694f","#8b4a2b","#dbb877","#dbb877","#a8493f","#c9a15a","#b5652f","#a8493f","#c17f3e","#b08968","#b5652f","#dbb877","#9c6b4a","#a05c3f","#96694f","#9c6b4a","#c9a15a","#6b4226","#8b4a2b","#c98a52","#b08968","#6b4226","#a05c3f","#c4a35f","#dbb877","#8b4a2b","#c9a15a","#a05c3f","#a05c3f","#c4a35f","#96694f","#a8493f","#d4a84a","#8b4a2b","#c17f3e","#c98a52","#c17f3e","#c17f3e","#c9a15a","#a8493f","#c4a35f","#6b4226","#9c6b4a","#b08968","#c98a52","#6b4226","#c4a35f","#dbb877","#b5652f","#c9a15a","#a05c3f","#9c6b4a","#b5652f","#c98a52","#c17f3e","#d4a84a","#b5652f","#dbb877","#b5652f","#c4a35f","#a05c3f","#b08968","#9c6b4a","#a8493f","#a8493f","#b5652f","#a8493f","#d4a84a","#96694f","#a05c3f","#c17f3e","#9c6b4a","#b08968","#c9a15a","#c17f3e","#b5652f","#d4a84a","#c17f3e","#c9a15a","#a8493f","#b08968","#8b4a2b","#b08968","#d4a84a","#a8493f","#9c6b4a","#c4a35f","#a05c3f","#a05c3f","#dbb877","#c4a35f","#b08968","#6b4226","#c98a52","#b5652f","#a8493f","#c4a35f","#96694f","#c9a15a","#d4a84a","#8b4a2b","#c98a52","#6b4226","#dbb877","#96694f","#c9a15a","#9c6b4a","#d4a84a","#d4a84a","#b08968","#dbb877","#9c6b4a","#c17f3e","#a8493f","#b5652f","#b08968","#a8493f","#c17f3e","#c17f3e","#8b4a2b","#9c6b4a","#b08968","#9c6b4a","#b5652f","#96694f","#6b4226","#9c6b4a","#b08968","#b08968","#a8493f","#c9a15a","#a05c3f","#8b4a2b","#8b4a2b","#b5652f","#d4a84a","#a05c3f","#c4a35f","#96694f","#6b4226","#6b4226","#d4a84a","#8b4a2b","#6b4226","#d4a84a","#c17f3e","#c98a52","#8b4a2b","#9c6b4a","#96694f","#c17f3e","#dbb877","#d4a84a","#8b4a2b","#c4a35f","#c4a35f","#96694f","#d4a84a","#c4a35f","#d4a84a","#8b4a2b","#c98a52","#6b4226","#dbb877","#c9a15a","#c9a15a","#c9a15a","#b5652f","#8b4a2b","#96694f","#6b4226","#96694f","#a8493f","#dbb877","#a8493f","#6b4226","#c17f3e"]'

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] recolor Library Globe to brown/ochre/sienna-only palette")
print("OK: Library Globe palette pruned to strictly warm tones" if status in ("patched","already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
