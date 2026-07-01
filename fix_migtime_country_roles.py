#!/usr/bin/env python3
"""worldbook_claude build -- make migration-over-time light up source (emigration)
and destination (immigration) countries in distinct colors, updating live as the
decade changes.

Mike's ask: "the source countries should light up one color when people emigrate,
and the destinations should light up another." Turns out this exact mechanism
already exists in the codebase and already works correctly -- it's just never
invoked when the migtime decade changes.

`setFlowBase(key)` (called by `setFlow()` when any flow layer activates) already
does precisely this for every flow layer, generically: it calls `rolesFor(key,
flowIso)`, which walks `FLOWS[key].edges` and buckets each ISO3 code into
source/transit/consumer, then recolors the "fills" layer with a
`["match",["get","iso3"], ...]` expression using the existing `ROLE_COL` palette
(`source:"#2f9e6e"` green, `consumer:"#c0556b"` rose, `transit:"#d9a441"` gold for
a country that's both in the same period, `none:"#26303f"` dimmed slate for
everyone else). Confirmed live via javascript_tool: calling `setFlowBase('migtime')`
by hand at 1850 correctly colored IRL/DEU/GBR/AGO/CHN/IND green (source) and
USA/CUB/GUY rose (destination) for that decade's real corridors.

The bug: `migApplyDecade(dec)` -- called on every slider drag / play-tick / decade
change -- updates `FLOWS.migtime.edges` (the data) and calls `buildFlowGeo` (the
visible arcs), but never calls `setFlowBase`. Confirmed live: after `migSetYear(1950)`,
`map.getPaintProperty("fills","fill-color")` was still the stale 1850 match
expression; only an explicit `setFlowBase('migtime')` call produced the correct
1950s roles (PAK/ITA/MEX/PRI/GBR source, IND/DEU/USA/AUS destination). So the
country highlight either never appears or freezes on whatever decade it last
happened to be recomputed for -- not "missing," just never wired to refresh.

Fix: one added call, guarded the same way the existing `buildFlowGeo` call already
is (only while migtime is the active flow). Re-verified after patching: simulated
the exact patched function live, scrubbed to 1880 ("First mass wave peaks; 5.2M to
US"), screenshotted -- USA rose/red (destination), Scandinavia/British Isles green
(source), everyone else dimmed to the neutral slate.

Idempotent. Usage: python3 fix_migtime_country_roles.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    'function migApplyDecade(dec){ FLOWS.migtime.edges=migEdgesFor(dec); '
    'const kf=MIG_BY[dec]||{}; FLOWS.migtime.sources=uniqueSources(kf.sources||[]); '
    'if(typeof flowKey!=="undefined"&&flowKey==="migtime") buildFlowGeo("migtime"); }'
)
NEW = (
    'function migApplyDecade(dec){ FLOWS.migtime.edges=migEdgesFor(dec); '
    'const kf=MIG_BY[dec]||{}; FLOWS.migtime.sources=uniqueSources(kf.sources||[]); '
    'if(typeof flowKey!=="undefined"&&flowKey==="migtime"){ buildFlowGeo("migtime"); setFlowBase("migtime"); } }'
)

if NEW in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] migApplyDecade: recolor source/destination countries on every decade change")
print("OK: migration-over-time country roles now refresh live" if status in ("patched","already-applied") else "WARN: anchor not found")
sys.exit(0 if status in ("patched","already-applied") else 1)
