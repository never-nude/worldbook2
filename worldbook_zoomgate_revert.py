#!/usr/bin/env python3
"""Worldbook: revert the zoom-based label filter - it broke all labels live.

Mike: "letters disappeared again" - same severity as the earlier scoping bug.
The filter (["'>='",["zoom"],["get","minZoom"]]) validated cleanly against the
real MapLibre style-spec expression compiler before shipping, and node --check
passed on the deployed file - but that only proves the expression is syntactically
and semantically well-formed in isolation, not that it behaves correctly at
runtime against a live GeoJSON source on a globe projection, which I have no way
to test in this environment. Follow-up research turned up a real, documented
MapLibre quirk I did not know when I shipped it: zoom expressions inside filters
are only re-evaluated at INTEGER zoom levels, not continuously - a real gap in
my testing, and plausibly part of what went wrong here (on top of whatever else
is specific to this GeoJSON+globe combination).

Rather than layer another unverified guess on top of the last one, this removes
the filter entirely and returns the layer to exactly what it was before -
always-show labels (subject to MapLibre's normal collision handling), the
proven-working behavior for the whole rest of this session. The per-country
minZoom values stay in the data (harmless, unused) in case a more carefully
tested zoom-visibility mechanism is worth revisiting later - just not blindly
shipped again without a way to actually see it run first.
Idempotent, pure ASCII source.
Usage: python3 worldbook_zoomgate_revert.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = 'addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n    filter:[">=",["zoom"],["get","minZoom"]],\n    layout:'
NEW = 'addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n    layout:'

if NEW in text and OLD not in text:
    print("  [already-applied] zoom filter removed from country-labels layer")
elif OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("  [        patched] zoom filter removed from country-labels layer")
else:
    print("  [ ANCHOR-NOT-FOUND] country-labels layer filter clause")
    open(OUT, "w", encoding="utf-8").write(text)
    sys.exit(1)

open(OUT, "w", encoding="utf-8").write(text)
print("OK: labels restored - always visible again, subject to normal collision")
