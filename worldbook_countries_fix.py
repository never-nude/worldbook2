#!/usr/bin/env python3
"""Worldbook: fix the Countries layer (shipped colorless) + make it the default layer.

Root cause: the color_countries injection ran AFTER map.addSource("world",{data:
MAPDATA}) - MapLibre snapshots/tiles GeoJSON source data immediately on addSource
(it hands the data to a worker), so mutating the MAPDATA objects afterward had no
effect on what was actually rendered. Every OTHER layer (religion, gdp, etc.) worked
because their color_<key> props were baked into MAPDATA from the start, before any
of this runtime code ran - Countries was the first layer whose color got set live,
and the ordering bug only showed up there. Fix: inject before addSource, not after.

Also: activeLayer="flow_drugs" was never actually applied at boot (nothing called
setLayer(activeLayer) on load - the real initial view has always just been whatever
the hardcoded paint on the "fills" layer happened to be, i.e. religion colors). Mike
asked for Countries to be the default, so this also flips the declared default AND
adds the boot-time setLayer("countries") call that actually makes a default mean
something.
Idempotent, pure ASCII source.
Usage: python3 worldbook_countries_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ("fix: bake color_countries before the GeoJSON source is created (was added after addSource, so MapLibre's worker had already snapshotted the un-colored data and activate Countries by default at boot",
     'map.addSource("world",{type:"geojson",data:MAPDATA,promoteId:"iso3"});\n  map.addLayer({id:"fills",type:"fill",source:"world",\n    paint:{"fill-color":colorExpr("religion"),"fill-opacity":1,\n      "fill-color-transition":{duration:500,delay:0},"fill-opacity-transition":{duration:400}}});\n  map.addLayer({id:"borders",type:"line",source:"world",\n    paint:{"line-color":"#05080f","line-width":0.5,"line-opacity-transition":{duration:400}}});\n  MAPDATA.features.forEach(function(f,i){ f.properties.color_countries = COUNTRY_PASTEL[i]; });\n  map.addSource("country-labels",{type:"geojson",data:COUNTRY_LABELS});\n  map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n    layout:{"text-field":["get","name"],"text-font":["Open Sans Regular"],\n      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});',
     '  MAPDATA.features.forEach(function(f,i){ f.properties.color_countries = COUNTRY_PASTEL[i]; });\n  map.addSource("world",{type:"geojson",data:MAPDATA,promoteId:"iso3"});\n  map.addLayer({id:"fills",type:"fill",source:"world",\n    paint:{"fill-color":colorExpr("religion"),"fill-opacity":1,\n      "fill-color-transition":{duration:500,delay:0},"fill-opacity-transition":{duration:400}}});\n  map.addLayer({id:"borders",type:"line",source:"world",\n    paint:{"line-color":"#05080f","line-width":0.5,"line-opacity-transition":{duration:400}}});\n  map.addSource("country-labels",{type:"geojson",data:COUNTRY_LABELS});\n  map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n    layout:{"text-field":["get","name"],"text-font":["Open Sans Regular"],\n      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});\n  setLayer("countries");',
     'setLayer("countries");'),
    ('make Countries the declared default layer',
     'let activeLayer="flow_drugs";   // open on Drug routes by default',
     'let activeLayer="countries";   // Countries reference map opens by default',
     'let activeLayer="countries"'),
]

res = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
        res.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: Countries layer fixed + set as default" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
