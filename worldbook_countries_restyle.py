#!/usr/bin/env python3
"""Worldbook: restyle the Countries layer - bold/bigger country names,
regular-weight city names, each country tinted with its own lightened
color instead of a flat cream fill, and a modest (not overwhelming) bump
to the edge-glow thickness.

Mike's ask, in order::
  "the names of the countries should be in bold while the cities are
  regular" - country-labels was "Noto Sans Regular", city tier 1 was
  "Noto Sans Bold" (backwards from what he wants). Swapped: country names
  now Bold, all three city tiers now Regular (dropped the italic on tier 3
  too, for a cleaner "one look for countries, one look for cities, size is
  what tells tiers apart" hierarchy instead of mixing weight AND style).

  "make each country that same color but about 2-3x lighter" - the flat
  "#f5f0e4" cream fill on the Countries layer is replaced with each
  country's own already-assigned color_countries hue, blended 62% toward
  white (a new precomputed COUNTRY_PASTEL_LIGHT[i] array, same pattern as
  the existing COUNTRY_PASTEL/COUNTRY_ANTIQUE arrays - added as a new
  property in the same MAPDATA.features.forEach that already sets
  color_countries/color_antique). Reads as a pale pastel tint of the same
  hue used for that country's edge-glow and (now bold) name label, instead
  of one flat neutral color for every country.

  "country names should be at least 1.5x as large as the city names" -
  country label text-size was a raw per-country "size" property (live-
  measured range 7 to 22.1). City tier 1 (the largest city tier) is 13, so
  1.5x = 19.5. Applied `max(size*1.3, 20)` - preserves the existing
  "bigger country = bigger label" relative scaling (top end goes from 22.1
  to ~28.7) while flooring every country, even the smallest, comfortably
  above the 19.5 threshold.

  "make the shaded borders a bit thicker, but not overwhelmingly so" -
  bumped the edge-glow line-width interpolation stops by about 20% across
  both the soft and tight layers (e.g. the zoom-5 plateau: soft 18px->21px,
  tight 7px->8.5px) - a visible but modest bump, not another "much thicker"
  jump like the earlier thickening pass this session.

Idempotent, pure ASCII source.
Usage: python3 worldbook_countries_restyle.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

COUNTRY_PASTEL_LIGHT_JS = "const COUNTRY_PASTEL_LIGHT=" + '["#e8f3d1","#f3d1e8","#d1dcf3","#f3d1d1","#d1dcf3","#f3d1f3","#d1dcf3","#f3d1f3","#f3d1dc","#f3d1d1","#d1f3f3","#dcf3d1","#dcf3d1","#d1f3d1","#f3dcd1","#d1dcf3","#d1f3e8","#f3e8d1","#f3d1d1","#dcd1f3","#d1f3f3","#dcf3d1","#d1f3dc","#d1f3d1","#f3dcd1","#e8d1f3","#d1dcf3","#f3e8d1","#e8d1f3","#f3d1d1","#f3f3d1","#d1f3d1","#f3e8d1","#dcd1f3","#f3d1e8","#d1d1f3","#f3dcd1","#d1f3f3","#dcd1f3","#d1f3f3","#d1f3e8","#f3f3d1","#d1d1f3","#e8f3d1","#d1f3dc","#dcf3d1","#d1f3dc","#f3dcd1","#f3e8d1","#e8f3d1","#d1e8f3","#e8f3d1","#d1e8f3","#d1f3dc","#dcf3d1","#d1f3e8","#f3d1e8","#e8f3d1","#d1e8f3","#d1f3d1","#d1f3d1","#f3d1f3","#d1d1f3","#e8d1f3","#d1e8f3","#d1d1f3","#f3f3d1","#d1f3dc","#f3dcd1","#f3d1f3","#d1dcf3","#f3e8d1","#e8d1f3","#d1f3e8","#dcd1f3","#e8f3d1","#d1f3d1","#f3d1e8","#e8d1f3","#f3d1dc","#f3d1d1","#d1dcf3","#f3e8d1","#f3f3d1","#d1f3e8","#f3f3d1","#f3d1e8","#f3d1e8","#dcd1f3","#f3d1dc","#f3d1e8","#d1f3f3","#d1f3e8","#dcd1f3","#d1d1f3","#d1f3f3","#e8d1f3","#dcf3d1","#d1f3dc","#f3d1d1","#d1f3d1","#d1e8f3","#d1e8f3","#f3d1f3","#d1f3d1","#f3d1d1","#d1f3e8","#f3dcd1","#f3dcd1","#f3d1dc","#d1e8f3","#d1f3f3","#f3d1f3","#f3d1f3","#f3dcd1","#f3f3d1","#dcd1f3","#d1dcf3","#dcf3d1","#d1dcf3","#d1d1f3","#d1f3dc","#f3d1f3","#f3e8d1","#d1f3dc","#f3dcd1","#f3d1dc","#d1f3d1","#f3e8d1","#f3dcd1","#d1f3f3","#f3e8d1","#d1e8f3","#d1f3f3","#f3dcd1","#e8d1f3","#d1f3e8","#d1f3d1","#dcd1f3","#d1f3dc","#f3d1f3","#dcd1f3","#d1f3dc","#d1d1f3","#dcf3d1","#f3d1d1","#f3d1d1","#f3d1dc","#d1dcf3","#f3d1e8","#f3d1f3","#d1f3f3","#d1f3e8","#f3f3d1","#d1e8f3","#f3d1dc","#d1f3e8","#d1f3f3","#d1d1f3","#f3d1e8","#e8d1f3","#dcd1f3","#d1d1f3","#dcf3d1","#d1f3f3","#dcf3d1","#d1f3dc","#f3d1e8","#d1f3d1","#d1f3e8","#d1e8f3","#f3d1e8","#d1e8f3","#e8f3d1","#e8f3d1","#f3f3d1","#f3dcd1","#dcf3d1","#f3e8d1","#f3d1f3","#d1f3dc","#f3dcd1","#d1dcf3","#e8d1f3","#f3f3d1","#d1f3d1","#f3d1f3","#f3e8d1","#d1f3d1","#d1d1f3","#f3d1dc","#d1e8f3","#e8f3d1","#e8d1f3","#f3d1dc","#dcd1f3","#e8f3d1","#e8f3d1","#dcf3d1","#e8f3d1","#f3d1e8","#f3d1dc","#f3d1dc","#d1e8f3","#f3f3d1","#f3d1d1","#f3d1dc","#f3f3d1","#f3d1e8","#d1d1f3","#dcf3d1","#d1f3dc","#f3d1f3","#f3d1dc","#f3d1d1","#dcd1f3","#d1d1f3","#f3e8d1","#d1f3e8","#d1f3e8","#d1dcf3","#f3d1d1","#f3f3d1","#e8d1f3","#d1d1f3","#dcd1f3","#d1d1f3","#e8f3d1","#d1f3f3","#dcf3d1","#e8f3d1","#d1dcf3","#d1f3dc","#dcd1f3","#f3d1d1","#f3f3d1","#e8d1f3","#f3e8d1","#d1f3f3","#f3d1e8","#e8d1f3","#d1f3d1"]' + ";"

EDITS = [
    (
        "insert COUNTRY_PASTEL_LIGHT array after COUNTRY_PASTEL",
        'const COUNTRY_LABELS=',
        COUNTRY_PASTEL_LIGHT_JS + '\nconst COUNTRY_LABELS=',
        "replace",
        "const COUNTRY_PASTEL_LIGHT=",
    ),
    (
        "set color_countries_light per feature in the existing forEach",
        'MAPDATA.features.forEach(function(f,i){ f.properties.color_countries = COUNTRY_PASTEL[i]; f.properties.color_antique = COUNTRY_ANTIQUE[i]; });',
        'MAPDATA.features.forEach(function(f,i){ f.properties.color_countries = COUNTRY_PASTEL[i]; f.properties.color_antique = COUNTRY_ANTIQUE[i]; f.properties.color_countries_light = COUNTRY_PASTEL_LIGHT[i]; });',
        "replace",
        "color_countries_light = COUNTRY_PASTEL_LIGHT[i]",
    ),
    (
        "recolor Countries fill to each country's own lightened tint",
        'if(!isRaster) map.setPaintProperty("fills","fill-color", key==="countries"?"#f5f0e4":colorExpr(key));',
        'if(!isRaster) map.setPaintProperty("fills","fill-color", key==="countries"?["coalesce",["get","color_countries_light"],"#f5f0e4"]:colorExpr(key));',
        "replace",
        'coalesce",["get","color_countries_light"]',
    ),
    (
        "country-labels: bold font + size floor (>=1.5x largest city tier)",
        'map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n'
        '    layout:{"text-field":["get","name"],"text-font":["Noto Sans Regular"],\n'
        '      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n'
        '      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n'
        '      "symbol-sort-key":["*",-1,["get","size"]],\n'
        '      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n'
        '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});',
        'map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n'
        '    layout:{"text-field":["get","name"],"text-font":["Noto Sans Bold"],\n'
        '      "text-size":["max",["*",["get","size"],1.3],20],"text-max-width":7,"text-padding":2,\n'
        '      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n'
        '      "symbol-sort-key":["*",-1,["get","size"]],\n'
        '      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n'
        '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});',
        "replace",
        '"text-font":["Noto Sans Bold"]',
    ),
    (
        "city labels: all tiers regular weight (drop bold on tier 1, drop italic on tier 3)",
        'const CITY_FONT={1:"Noto Sans Bold",2:"Noto Sans Regular",3:"Noto Sans Italic"};',
        'const CITY_FONT={1:"Noto Sans Regular",2:"Noto Sans Regular",3:"Noto Sans Regular"};   // countries carry the bold now - cities differentiate by size only',
        "replace",
        'const CITY_FONT={1:"Noto Sans Regular",2:"Noto Sans Regular",3:"Noto Sans Regular"};',
    ),
    (
        "thicken country-glow-soft modestly (~20%)",
        'paint:{"line-color":["get","color_countries"],"line-width":["interpolate",["linear"],["zoom"],0,2.5,2,8,5,18],"line-blur":["interpolate",["linear"],["zoom"],0,1.5,2,5,5,10],"line-opacity":0.5}}, "borders");',
        'paint:{"line-color":["get","color_countries"],"line-width":["interpolate",["linear"],["zoom"],0,3,2,9.5,5,21],"line-blur":["interpolate",["linear"],["zoom"],0,1.8,2,6,5,12],"line-opacity":0.5}}, "borders");',
        "replace",
        '"line-width":["interpolate",["linear"],["zoom"],0,3,2,9.5,5,21]',
    ),
    (
        "thicken country-glow-tight modestly (~20%)",
        'paint:{"line-color":["get","color_countries"],"line-width":["interpolate",["linear"],["zoom"],0,1,2,3.2,5,7],"line-blur":["interpolate",["linear"],["zoom"],0,0.4,2,1.1,5,2.2],"line-opacity":0.75}}, "borders");',
        'paint:{"line-color":["get","color_countries"],"line-width":["interpolate",["linear"],["zoom"],0,1.2,2,3.8,5,8.5],"line-blur":["interpolate",["linear"],["zoom"],0,0.5,2,1.3,5,2.6],"line-opacity":0.75}}, "borders");',
        "replace",
        '"line-width":["interpolate",["linear"],["zoom"],0,1.2,2,3.8,5,8.5]',
    ),
]

results = []
for name, old, new, mode, sentinel in EDITS:
    if sentinel in text:
        results.append((name, "already-applied"))
        continue
    if old not in text:
        results.append((name, "ANCHOR-NOT-FOUND"))
        continue
    text = text.replace(old, new, 1)
    results.append((name, "patched"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for name, status in results:
    print("  [%16s] %s" % (status, name))
    if status == "ANCHOR-NOT-FOUND":
        ok = False

print("OK: countries restyle applied" if ok else "WARN: one or more anchors not found - review before deploying")
sys.exit(0 if ok else 1)
