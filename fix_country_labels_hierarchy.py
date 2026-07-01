#!/usr/bin/env python3
"""worldbook_claude build -- fix the Countries-layer label system: no zoom-gating +
map-aligned text on a curved globe reads as amateur. Mike's own words: "this looks
amateur to me" (screenshot: "St. Pierre and Miquelon" rendered as large/prominent as
"United States of America", crowding "Bermuda"; visible text noticeably curved/warped
following the globe's surface away from view-center).

Root-caused live against production (not guessed), fresh un-cached page load:

1. Every one of the 242 country/territory labels renders at EVERY zoom level, always
   -- there's no filter on the "country-labels" symbol layer at all. Each feature DOES
   already carry a precomputed `minZoom` property (confirmed via the live COUNTRY_LABELS
   data: e.g. Russia=0.00, Canada=1.70, United States of America=2.21, down to
   Curacao=8.48, St. Pierre and Miquelon=8.5) -- this looks like a tiering system that
   was computed but never actually wired into the layer (no filter references it
   anywhere in the file -- grepped all 242 occurrences of "minZoom", every one is inside
   the static data blob, zero in any layout/paint/filter expression). Same idea as the
   existing, working city-label tier system (cities-dot-{1,2,3}/cities-label-{1,2,3},
   each with a real per-tier minzoom) -- countries just never got the equivalent wiring.

2. `text-rotation-alignment:"map"` + `text-pitch-alignment:"map"` keeps each label
   flat against the curved globe surface -- fine directly under the camera, but the
   further a label sits from view-center the more it visually warps/curves on screen
   (an inherent globe-projection effect, confirmed independent of the `rot` property,
   which is 0.0 for literally all 242 features -- the warping was never intentional
   per-feature rotation). Switching both to "viewport" keeps every label flat and
   horizontal on screen regardless of where it sits on the sphere or how it's tilted --
   the standard treatment for point-placed labels on a 3D globe (this is how Google
   Earth-style globes keep place names legible). Also makes MapLibre's own overlap
   detection more reliable, since it's now working with simple upright screen-space
   boxes instead of curved/pitched ones.

Fix for #1: filter:[">=",["zoom"],["-",["get","minZoom"],1.6]] -- shifts every
feature's existing minZoom down by 1.6, the exact literal already used everywhere
else in this file as the canonical world/home-view zoom (geolocate flyTo, the sun
button, the home button, drillOut's reset -- grepped, 4 hits, all "zoom:1.6"). This
is equivalent to "show a label if it was tagged to appear at-or-before the default
world view" -- reusing the app's own existing constant rather than inventing a new
number. Live-counted: 27 of 242 features clear this bar (Russia, Canada, China,
Australia, India, Brazil, USA, and other large/prominent nations) -- a reasonable,
uncluttered world-view set, confirmed by screenshot before writing this patch. Does
NOT touch the underlying minZoom values themselves (they likely encode real
label-fit-within-country-outline constraints per feature/shape -- safer to shift the
whole scale than to touch per-feature numbers I can't fully reverse-engineer).

Also drops the now-pointless `"text-rotate":["get","rot"]` (dead weight: 0.0 for
every feature, confirmed) -- one less moving part, and avoids any confusion pairing
a rotate value with viewport alignment.

Live-verified before shipping: applied both changes via javascript_tool against
production, screenshotted a default-zoom world view (clean, ~27 major-country labels,
no overlap, no warp -- Russia/Kazakhstan/Turkey/India/Niger/Sudan/Brazil all legible
and horizontal) vs. the unpatched fresh-load screenshot (St. Pierre and Miquelon
crowding Bermuda, every one of 242 labels visible at once, visible curve/warp).

Correction after first attempt: the OLD anchor below was originally built against a
fetch of the public https://worldbook.earth CDN, which turned out to be lagging
behind the real `main` branch by at least one prior round (it was still serving
"Noto Sans Regular" + a flat text-size when git main already had "Noto Sans Bold" +
a ["max",["*",["get","size"],1.3],20] size-floor formula from an earlier restyle
patch) -- ANCHOR-NOT-FOUND on first deploy attempt against the real repo. Rebuilt
against a raw.githubusercontent.com/.../main/index.html fetch instead, which matches
what `git pull` actually gives you. This version preserves the Bold font and the
size-floor formula as-is (not reverting other rounds' work) and only adds the
filter + switches alignment to viewport. Lesson: prefer raw.githubusercontent.com
over the public CDN domain when back-to-back deploys are happening in the same
session -- the CDN can lag behind `main` by more than one round, not just ~60s.

Idempotent. Usage: python3 fix_country_labels_hierarchy.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    'map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n'
    '    layout:{"text-field":["get","name"],"text-font":["Noto Sans Bold"],\n'
    '      "text-size":["max",["*",["get","size"],1.3],20],"text-max-width":7,"text-padding":2,\n'
    '      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n'
    '      "symbol-sort-key":["*",-1,["get","size"]],\n'
    '      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n'
    '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});'
)
NEW = (
    'map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n'
    '    filter:[">=",["zoom"],["-",["get","minZoom"],1.6]],\n'
    '    layout:{"text-field":["get","name"],"text-font":["Noto Sans Bold"],\n'
    '      "text-size":["max",["*",["get","size"],1.3],20],"text-max-width":7,"text-padding":2,\n'
    '      "text-rotation-alignment":"viewport","text-pitch-alignment":"viewport",\n'
    '      "symbol-sort-key":["*",-1,["get","size"]],\n'
    '      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n'
    '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});'
)

if NEW in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] country-labels: zoom-gate via existing minZoom + viewport-align text")
print("OK: country label hierarchy fixed" if status in ("patched","already-applied") else "WARN: anchor not found")
sys.exit(0 if status in ("patched","already-applied") else 1)
