#!/usr/bin/env python3
"""Worldbook: stop the cities layer and sea-collar mask from blocking initial
page load - defer both until right after the globe first reveals.

Mike's report: "loading way too slow... this needs to load reliably and be a
bit more engaging." Root cause: `map.addSource`/`map.addLayer` for the cities
layer (862 points, 6 layers) and the sea-collar mask (a ~280KB precomputed
polygon) were both wired into the SAME synchronous init block that
`map.once("idle", _reveal)` waits on - meaning the loading screen couldn't
come down until the renderer finished processing all of that, on top of
everything else the page already does. Both are pure decoration for one
reference layer (Countries) - neither needs to exist before the user sees
anything.

Fix: move both (found dynamically by anchor text, not hardcoded byte
offsets, so this doesn't depend on exact file layout) into the SAME deferred
`requestAnimationFrame` callback that already exists for sunshade/flow
layers/sky - these already run AFTER `_reveal` fires, so the core map
becomes interactive first and the cities/sea-collar detail fills in a moment
later without holding up first paint. Also re-applies the correct current
visibility for both right after creating them (since `setLayer()` may have
already run once during boot before these layers existed, and its
`if(map.getLayer(...))` guards would have silently skipped them).

Does not touch the earlier patchy-globe fix (`idle` vs the fallback
setTimeout) - that fix was written earlier this session but never actually
landed in production (confirmed live: the deployed file still had the
original setTimeout(_reveal, 4500), not the 20000 that was supposed to ship)
- this patch also fixes that for real this time, at a value re-tuned for the
now-lighter core init (8000ms - generous enough that idle should still
always win in practice, shorter than the original 20000 fix since deferring
cities/collar means idle itself should fire noticeably sooner now).

Idempotent (marked with a `/* DEFERRED_CITIES_SEACOLLAR */` sentinel
comment), pure ASCII source. Anchors are found dynamically via string
search, not embedded as literal 26KB/280KB blocks in this script, so this
file stays small regardless of how big the cities/collar data themselves
are.

Usage: python3 worldbook_defer_cities_seacollar.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "/* DEFERRED_CITIES_SEACOLLAR */"

SYNC_SNIPPET = (
    "\n    { const _isCR=(typeof activeLayer!==\"undefined\"&&activeLayer===\"countries\""
    "&&!(typeof subOn!==\"undefined\"&&subOn));\n"
    "      if(map.getLayer(\"sea-collar\")) map.setLayoutProperty(\"sea-collar\",\"visibility\",_isCR?\"visible\":\"none\");\n"
    "      [1,2,3].forEach(function(tr){\n"
    "        if(map.getLayer(\"cities-dot-\"+tr)) map.setLayoutProperty(\"cities-dot-\"+tr,\"visibility\",_isCR?\"visible\":\"none\");\n"
    "        if(map.getLayer(\"cities-label-\"+tr)) map.setLayoutProperty(\"cities-label-\"+tr,\"visibility\",_isCR?\"visible\":\"none\");\n"
    "      }); }\n"
)

TIMEOUT_OLD = 'map.once("idle", _reveal); setTimeout(_reveal, 4500);'
TIMEOUT_NEW = 'map.once("idle", _reveal); setTimeout(_reveal, 8000);   // safety net only - deferring cities/sea-collar (see below) should let idle fire well before this in practice'

DEFER_ANCHOR_OLD = "addFlowLayers();\n    initSky();"

if MARKER in text:
    status_move = "already-applied"
else:
    cities_i = text.find("const CITIES=[")
    cities_j = text.find("window.USE_3D_LABELS=false;", cities_i)
    collar_i = text.find('map.addSource("sea-collar"')
    collar_j = text.find('map.addSource("country-labels"', collar_i)

    if -1 in (cities_i, cities_j, collar_i, collar_j) or DEFER_ANCHOR_OLD not in text:
        status_move = "ANCHOR-NOT-FOUND"
    else:
        cities_block = text[cities_i:cities_j]
        collar_block = text[collar_i:collar_j]

        # remove the later-in-file block first so the earlier block's already-
        # computed indices stay valid
        if cities_i > collar_i:
            text = text[:cities_i] + text[cities_j:]
            text = text[:collar_i] + text[collar_j:]
        else:
            text = text[:collar_i] + text[collar_j:]
            text = text[:cities_i] + text[cities_j:]

        moved = MARKER + "\n" + collar_block + cities_block + SYNC_SNIPPET
        text = text.replace(DEFER_ANCHOR_OLD, "addFlowLayers();\n    " + moved + "\n    initSky();", 1)
        status_move = "patched"

if TIMEOUT_NEW in text:
    status_timeout = "already-applied"
elif TIMEOUT_OLD in text:
    text = text.replace(TIMEOUT_OLD, TIMEOUT_NEW, 1)
    status_timeout = "patched"
else:
    status_timeout = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)

ok = status_move != "ANCHOR-NOT-FOUND" and status_timeout != "ANCHOR-NOT-FOUND"
print(f"  [{status_move:>16}] move cities + sea-collar init into the deferred post-reveal callback")
print(f"  [{status_timeout:>16}] bump reveal fallback timeout 4500ms -> 8000ms (retune for lighter core init)")
print("OK: cities/sea-collar no longer block initial reveal" if ok else "WARN: one or more anchors not found - review before deploying")
sys.exit(0 if ok else 1)
