#!/usr/bin/env python3
"""worldbook_claude build -- two fixes to the boot sequence in _atlasBoot():

1. COUNTRY LABEL / CITY LABEL COLLISION (Mike: "some countries' names aren't
   showing from any distance (mexico...)"). Root-caused live against production:
   MapLibre resolves cross-layer symbol collisions by LAYER STACK ORDER, not by
   comparing symbol-sort-key values across different layers -- sort-key only
   arbitrates collisions within the same layer. country-labels is added early
   (style index 10, before sunshade/hover/flow/cities), while cities-label-1/2/3
   are added later (indices ~18-20). So whenever a tier-1 city sits near a
   country's label anchor (Monterrey/Guadalajara near "Mexico"), the city label
   silently wins the collision and suppresses the country name -- exactly the
   opposite of what CITY_SORT's own comment says it guarantees ("positive on
   purpose: must always lose collision to country-label sort-keys"). That
   comment describes the intended outcome; the mechanism chosen to achieve it
   (sort-key alone) doesn't actually deliver it across layers.

   Confirmed live via javascript_tool: fixed camera on Mexico (center
   [-101.7573,23.4719], zoom 3.2) -- "Mexico" does not render while cities are
   visible. Ran map.moveLayer("country-labels") (moves it to the top of the
   style stack, i.e. after the city layers) -- "Mexico" renders correctly,
   Monterrey correctly yields (direct collision), Guadalajara still shows (no
   collision there). This is a general, one-time fix: it corrects the priority
   for every country against every city label at once, not just Mexico.

   Fix: call map.moveLayer("country-labels") once, right after both city-layer
   forEach loops finish adding cities-dot-*/cities-label-* (so those layers
   already exist in the style when the move happens).

2. LOADING RELIABILITY ("globe still isn't loading completely all the time...
   make it ironclad but dynamic in the event that we add more layers"). Root-
   caused by reading the boot sequence directly (not guessed): the "Building
   your world..." spinner is hidden by _reveal(), which fires on whichever
   comes first of map.once("idle", _reveal) [the real, correct signal] or a
   flat setTimeout(_reveal, 8000) described in its own comment as "safety net
   only." That description was aspirational, not actual: a flat 8000ms timer
   fires unconditionally 8s after boot starts, with zero awareness of whether
   the map has actually finished. On a slower load -- more data, a slower
   connection/device, or simply more layers added later, all of which push
   idle's real firing time later -- the timer can and will win the race,
   hiding the spinner while the base map is still genuinely mid-load. Every
   time someone adds another data layer to this file, this number silently
   becomes less correct; nobody would think to come back and re-tune a magic
   8000 to match.

   Separately: the deferred post-reveal setup (sunshade, flow layers, the
   282KB sea-collar polygon, the cities source + 6 city layers, sky) all runs
   inside ONE shared try/catch. A single thrown exception anywhere in that
   chain -- today or in a layer added a year from now -- silently cancels
   every step after it for the rest of the session (console.error only,
   nothing a user would ever see). That is a second, independent way the
   globe can end up "not loading completely," intermittently, with no
   correlation to network speed at all.

   Fix, both structural rather than tuned to today's payload:
   a) Replace the flat 8s deadline with a watchdog that re-arms itself on
      every "data"/"dataloading" event the map fires (tile/source activity).
      It only actually fires _reveal after 8s of TRUE inactivity -- a real
      stall -- never mid-load, no matter how much data or how many layers are
      in flight. idle still wins in the normal case; this only changes what
      "safety net" means when idle is unusually slow. Scales automatically:
      more layers means more activity events, which keeps legitimately
      re-arming the net for exactly as long as real work is happening, with
      no timeout number to remember to bump.
   b) Split the one shared try/catch around the deferred block into one
      try/catch per independent step (sunshade, flow layers, sea-collar,
      cities+city layers+the label fix above, the countries/cities visibility
      toggle, sky). A failure in any one step is now isolated -- it can no
      longer take down unrelated features, including whatever gets added to
      this chain next.

   No live end-to-end repro of the stall was captured this session (it did
   reproduce once as a genuinely frozen/unresponsive tab during testing, but
   that tab could not be scripted afterward to extract more detail) -- this
   fix is root-caused from reading the actual gating logic, not from watching
   the specific failure play out to completion. The watchdog's re-arm/timeout
   logic was verified live in isolation (simulated fake "data" events against
   the real map object; confirmed it only fires after a true quiet gap, and
   fires immediately if there's no activity at all).

3. "Colombia / undefined: No data" TOOLTIP BUG -- root-caused (hoverHTML's
   generic fallback branch renders `${c.short}: ${val}`, and the "countries"
   reference layer -- the default view every visitor lands on -- has neither
   `.short` nor `.prop`, so this evaluates to the literal string "undefined:
   No data" for every country until you switch layers), but while re-
   verifying live just before shipping, found commit b326cc81 ("Fix undefined
   hover tooltip on Countries layer") had already landed on main with the
   same diagnosis and an equivalent fix (`if(c.type==="reference") return
   ...name-only...`, as a separate added line rather than folded into the
   raster check). Confirmed live via javascript_tool against production
   (hoverHTML(colombiaProps,false) now returns name-only HTML, no "undefined"
   anywhere) before deciding NOT to duplicate this fix here -- no changes in
   this patch touch hoverHTML.

Idempotent. Usage: python3 fix_loading_reliability_and_country_labels.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

FIXES = [
    ("fault-isolation: sunshade | flow-layers boundary",
     'updateSunShade();\n'
     '    addFlowLayers();\n'
     '    /* DEFERRED_CITIES_SEACOLLAR */',
     'updateSunShade();\n'
     '    }catch(e2){ console.error("Atlas deferred init (sunshade):",e2); }\n'
     '    try{ addFlowLayers(); }catch(e2){ console.error("Atlas deferred init (flow layers):",e2); }\n'
     '    try{\n'
     '    /* DEFERRED_CITIES_SEACOLLAR */'),

    ("fault-isolation: sea-collar | cities boundary",
     'map.addLayer({id:"sea-collar",type:"fill",source:"sea-collar",\n'
     '    layout:{visibility:"none"},\n'
     '    paint:{"fill-color":"#0a1b30"}}, "borders");',
     'map.addLayer({id:"sea-collar",type:"fill",source:"sea-collar",\n'
     '    layout:{visibility:"none"},\n'
     '    paint:{"fill-color":"#0a1b30"}}, "borders");\n'
     '    }catch(e2){ console.error("Atlas deferred init (sea-collar):",e2); }\n'
     '    try{'),

    ("country-labels layer-order fix + fault-isolation: cities | visibility-toggle boundary",
     'paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.7)","text-halo-width":1.1}});\n'
     '});\n'
     '\n'
     '    { const _isCR=',
     'paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.7)","text-halo-width":1.1}});\n'
     '});\n'
     'map.moveLayer("country-labels");   // fix: MapLibre resolves cross-layer symbol collisions by layer stack\n'
     '    // order, not by comparing symbol-sort-key across layers -- country-labels (added near the base\n'
     '    // style, long before the city layers below) was silently losing to nearby tier-1 city labels\n'
     '    // (e.g. Monterrey/Guadalajara suppressing "Mexico"), the opposite of what CITY_SORT intended.\n'
     '    // Re-stacking it above the city layers (which already exist here, right after both forEach\n'
     '    // loops) is what actually delivers that. Confirmed live: without this, "Mexico" never renders.\n'
     '    }catch(e2){ console.error("Atlas deferred init (cities):",e2); }\n'
     '    try{\n'
     '    { const _isCR='),

    ("fault-isolation: visibility-toggle | sky boundary + ironclad/dynamic reveal watchdog",
     '      }); }\n'
     '\n'
     '    initSky();\n'
     '  }catch(e2){ console.error("Atlas deferred init:",e2); } });\n'
     '  };\n'
     '  map.once("idle", _reveal); setTimeout(_reveal, 8000);   // safety net only - deferring cities/sea-collar (see below) should let idle fire well before this in practice',
     '      }); }\n'
     '    }catch(e2){ console.error("Atlas deferred init (visibility toggle):",e2); }\n'
     '    try{ initSky(); }catch(e2){ console.error("Atlas deferred init (sky):",e2); }\n'
     '  });\n'
     '  };\n'
     '  { let _wbRevealWD; const _wbArmReveal=()=>{ if(_revealed) return; clearTimeout(_wbRevealWD); _wbRevealWD=setTimeout(_reveal, 8000); };\n'
     '    map.on("data",_wbArmReveal); map.on("dataloading",_wbArmReveal); _wbArmReveal();\n'
     '    map.once("idle", _reveal); }   // ironclad+dynamic: re-arms an 8s last-resort timer on every style/source/tile\n'
     '    // event, so it only fires after 8s of true inactivity (a real stall) -- never mid-load, no matter how much\n'
     '    // data or how many layers are in flight. idle still wins in the normal case; this only changes what the\n'
     '    // fallback means when idle is unusually slow. Scales with future layers automatically: no timeout to retune.'),
]

results = []
for label, OLD, NEW in FIXES:
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

print("OK: loading reliability + country-label collision fixed" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
