#!/usr/bin/env python3
"""Worldbook: correct the countries restyle from earlier this session -
Mike's screenshot showed the "lightened" country fill reading as a uniform
washed-out cream, not each country's own pastel hue just lighter. Also adds
a genuinely darker edge color (new ask) and a real 3-level city/country
boldness hierarchy (previous patch collapsed all cities to one weight).

Mike's corrections, in order:
  "the countries on the countries layer should each be their old pastel
  color, just lighter" - COUNTRY_PASTEL is a uniform HSL L=0.70/S=0.595
  palette (only hue varies per country). The previous patch blended 62%
  toward white -> uniform L=0.886, which is close enough to white that the
  per-country hue was barely perceptible - exactly the "uniform cream"
  Mike's screenshot showed. Recalibrated to a 35% blend -> uniform L=0.806:
  clearly lighter than the base pastel, still clearly that country's hue.

  "the edges being 2-3x darker in shade and a bit thicker than they
  currently are" - edges previously used color_countries (the raw,
  unmodified base hue) for country-glow-soft/tight. New COUNTRY_PASTEL_DARK
  array blends 55% toward black -> uniform L=0.316 (base L=0.70 / 0.316 =
  2.2x darker, squarely in the "2-3x" range) - a rich, saturated, clearly
  darker shade of the same per-country hue, not just the unmodified base
  color. Wired in as a new color_countries_dark feature property, used as
  the glow layers' line-color instead of color_countries. Line-width/blur
  bumped a further ~18% on top of the ~20% bump already shipped this
  session (soft 21px->25px, tight 8.5px->10px at the zoom-5 plateau) - the
  darker/more saturated color alone already reads as noticeably more
  prominent, so the additional width bump stays modest per "a bit thicker,"
  not another big jump.

  "the boldness hierarchy of fonts should go country>big cities>regular
  cities, as well as the font sizes" - the previous patch made ALL city
  tiers "Noto Sans Regular" (country bold vs. cities regular, size-only
  differentiation), which collapses to a 2-level hierarchy, not the
  3-level one Mike is asking for. The live style's glyph server
  (demotiles.maplibre.org) was checked directly (fetched real glyph PBFs,
  not assumed) and only hosts Noto Sans Regular/Bold/Italic for the Noto
  Sans family - no Medium/SemiBold/Black exists for it, so a true 3-weight
  hierarchy isn't possible within one family here. It DOES host
  "Open Sans Semibold" (confirmed: a real 200 response with real glyph
  data, not a 404), a genuine middle weight from a closely-related humanist
  sans that reads consistently alongside Noto Sans at small map-label
  sizes. New hierarchy: country-labels stays "Noto Sans Bold" (boldest,
  already correct), tier-1/"big" cities (capitals & megacities) switch to
  "Open Sans Semibold" (real middle weight), tier-2/tier-3/"regular" cities
  stay "Noto Sans Regular" (lightest) - a genuine 3-level boldness
  hierarchy using real, confirmed-available glyph stacks, not a guess.
  Font SIZES already satisfied the hierarchy before this patch (country
  floor 20px / up to ~28.7px, tier-1 cities 13px, tier-2 11px, tier-3
  9.5px - already monotonically decreasing) so CITY_SIZE is untouched.

Idempotent (the COUNTRY_PASTEL_LIGHT/DARK block is regenerated
deterministically from COUNTRY_PASTEL every run via anchor-bounded
replacement, so reapplying always yields byte-identical output without
needing a separate sentinel check for that edit specifically; the other
edits use the standard NEW-in-text-first check). Pure ASCII source.
Usage: python3 worldbook_countries_restyle2.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

LIGHT_JS = "const COUNTRY_PASTEL_LIGHT=" + '["#d7ebb0","#ebb0d7","#b0c3eb","#ebb0b0","#b0c3eb","#ebb0eb","#b0c3eb","#ebb0eb","#ebb0c3","#ebb0b0","#b0ebeb","#c3ebb0","#c3ebb0","#b0ebb0","#ebc3b0","#b0c3eb","#b0ebd7","#ebd7b0","#ebb0b0","#c3b0eb","#b0ebeb","#c3ebb0","#b0ebc3","#b0ebb0","#ebc3b0","#d7b0eb","#b0c3eb","#ebd7b0","#d7b0eb","#ebb0b0","#ebebb0","#b0ebb0","#ebd7b0","#c3b0eb","#ebb0d7","#b0b0eb","#ebc3b0","#b0ebeb","#c3b0eb","#b0ebeb","#b0ebd7","#ebebb0","#b0b0eb","#d7ebb0","#b0ebc3","#c3ebb0","#b0ebc3","#ebc3b0","#ebd7b0","#d7ebb0","#b0d7eb","#d7ebb0","#b0d7eb","#b0ebc3","#c3ebb0","#b0ebd7","#ebb0d7","#d7ebb0","#b0d7eb","#b0ebb0","#b0ebb0","#ebb0eb","#b0b0eb","#d7b0eb","#b0d7eb","#b0b0eb","#ebebb0","#b0ebc3","#ebc3b0","#ebb0eb","#b0c3eb","#ebd7b0","#d7b0eb","#b0ebd7","#c3b0eb","#d7ebb0","#b0ebb0","#ebb0d7","#d7b0eb","#ebb0c3","#ebb0b0","#b0c3eb","#ebd7b0","#ebebb0","#b0ebd7","#ebebb0","#ebb0d7","#ebb0d7","#c3b0eb","#ebb0c3","#ebb0d7","#b0ebeb","#b0ebd7","#c3b0eb","#b0b0eb","#b0ebeb","#d7b0eb","#c3ebb0","#b0ebc3","#ebb0b0","#b0ebb0","#b0d7eb","#b0d7eb","#ebb0eb","#b0ebb0","#ebb0b0","#b0ebd7","#ebc3b0","#ebc3b0","#ebb0c3","#b0d7eb","#b0ebeb","#ebb0eb","#ebb0eb","#ebc3b0","#ebebb0","#c3b0eb","#b0c3eb","#c3ebb0","#b0c3eb","#b0b0eb","#b0ebc3","#ebb0eb","#ebd7b0","#b0ebc3","#ebc3b0","#ebb0c3","#b0ebb0","#ebd7b0","#ebc3b0","#b0ebeb","#ebd7b0","#b0d7eb","#b0ebeb","#ebc3b0","#d7b0eb","#b0ebd7","#b0ebb0","#c3b0eb","#b0ebc3","#ebb0eb","#c3b0eb","#b0ebc3","#b0b0eb","#c3ebb0","#ebb0b0","#ebb0b0","#ebb0c3","#b0c3eb","#ebb0d7","#ebb0eb","#b0ebeb","#b0ebd7","#ebebb0","#b0d7eb","#ebb0c3","#b0ebd7","#b0ebeb","#b0b0eb","#ebb0d7","#d7b0eb","#c3b0eb","#b0b0eb","#c3ebb0","#b0ebeb","#c3ebb0","#b0ebc3","#ebb0d7","#b0ebb0","#b0ebd7","#b0d7eb","#ebb0d7","#b0d7eb","#d7ebb0","#d7ebb0","#ebebb0","#ebc3b0","#c3ebb0","#ebd7b0","#ebb0eb","#b0ebc3","#ebc3b0","#b0c3eb","#d7b0eb","#ebebb0","#b0ebb0","#ebb0eb","#ebd7b0","#b0ebb0","#b0b0eb","#ebb0c3","#b0d7eb","#d7ebb0","#d7b0eb","#ebb0c3","#c3b0eb","#d7ebb0","#d7ebb0","#c3ebb0","#d7ebb0","#ebb0d7","#ebb0c3","#ebb0c3","#b0d7eb","#ebebb0","#ebb0b0","#ebb0c3","#ebebb0","#ebb0d7","#b0b0eb","#c3ebb0","#b0ebc3","#ebb0eb","#ebb0c3","#ebb0b0","#c3b0eb","#b0b0eb","#ebd7b0","#b0ebd7","#b0ebd7","#b0c3eb","#ebb0b0","#ebebb0","#d7b0eb","#b0b0eb","#c3b0eb","#b0b0eb","#d7ebb0","#b0ebeb","#c3ebb0","#d7ebb0","#b0c3eb","#b0ebc3","#c3b0eb","#ebb0b0","#ebebb0","#d7b0eb","#ebd7b0","#b0ebeb","#ebb0d7","#d7b0eb","#b0ebb0"]' + ";"
DARK_JS = "const COUNTRY_PASTEL_DARK=" + '["#57653c","#653c57","#3c4965","#653c3c","#3c4965","#653c65","#3c4965","#653c65","#653c49","#653c3c","#3c6565","#49653c","#49653c","#3c653c","#65493c","#3c4965","#3c6557","#65573c","#653c3c","#493c65","#3c6565","#49653c","#3c6549","#3c653c","#65493c","#573c65","#3c4965","#65573c","#573c65","#653c3c","#65653c","#3c653c","#65573c","#493c65","#653c57","#3c3c65","#65493c","#3c6565","#493c65","#3c6565","#3c6557","#65653c","#3c3c65","#57653c","#3c6549","#49653c","#3c6549","#65493c","#65573c","#57653c","#3c5765","#57653c","#3c5765","#3c6549","#49653c","#3c6557","#653c57","#57653c","#3c5765","#3c653c","#3c653c","#653c65","#3c3c65","#573c65","#3c5765","#3c3c65","#65653c","#3c6549","#65493c","#653c65","#3c4965","#65573c","#573c65","#3c6557","#493c65","#57653c","#3c653c","#653c57","#573c65","#653c49","#653c3c","#3c4965","#65573c","#65653c","#3c6557","#65653c","#653c57","#653c57","#493c65","#653c49","#653c57","#3c6565","#3c6557","#493c65","#3c3c65","#3c6565","#573c65","#49653c","#3c6549","#653c3c","#3c653c","#3c5765","#3c5765","#653c65","#3c653c","#653c3c","#3c6557","#65493c","#65493c","#653c49","#3c5765","#3c6565","#653c65","#653c65","#65493c","#65653c","#493c65","#3c4965","#49653c","#3c4965","#3c3c65","#3c6549","#653c65","#65573c","#3c6549","#65493c","#653c49","#3c653c","#65573c","#65493c","#3c6565","#65573c","#3c5765","#3c6565","#65493c","#573c65","#3c6557","#3c653c","#493c65","#3c6549","#653c65","#493c65","#3c6549","#3c3c65","#49653c","#653c3c","#653c3c","#653c49","#3c4965","#653c57","#653c65","#3c6565","#3c6557","#65653c","#3c5765","#653c49","#3c6557","#3c6565","#3c3c65","#653c57","#573c65","#493c65","#3c3c65","#49653c","#3c6565","#49653c","#3c6549","#653c57","#3c653c","#3c6557","#3c5765","#653c57","#3c5765","#57653c","#57653c","#65653c","#65493c","#49653c","#65573c","#653c65","#3c6549","#65493c","#3c4965","#573c65","#65653c","#3c653c","#653c65","#65573c","#3c653c","#3c3c65","#653c49","#3c5765","#57653c","#573c65","#653c49","#493c65","#57653c","#57653c","#49653c","#57653c","#653c57","#653c49","#653c49","#3c5765","#65653c","#653c3c","#653c49","#65653c","#653c57","#3c3c65","#49653c","#3c6549","#653c65","#653c49","#653c3c","#493c65","#3c3c65","#65573c","#3c6557","#3c6557","#3c4965","#653c3c","#65653c","#573c65","#3c3c65","#493c65","#3c3c65","#57653c","#3c6565","#49653c","#57653c","#3c4965","#3c6549","#493c65","#653c3c","#65653c","#573c65","#65573c","#3c6565","#653c57","#573c65","#3c653c"]' + ";"

results = []

# --- 1. regenerate the LIGHT(+DARK) array block deterministically ---------
# Anchors: starts at the first "const COUNTRY_PASTEL_LIGHT=" (inserted once,
# by the prior patch), ends right before "const COUNTRY_LABELS=" (the next
# declaration, immediately following in both the pre- and post-this-patch
# states). Whatever sits between them - just LIGHT (before this patch) or
# LIGHT+DARK (after) - gets replaced with the freshly computed block, so
# reapplying this script is naturally a no-op on the second run.
start_anchor = "const COUNTRY_PASTEL_LIGHT="
end_anchor = "const COUNTRY_LABELS="
si = text.find(start_anchor)
ei = text.find(end_anchor, si) if si != -1 else -1
if si == -1 or ei == -1:
    results.append(("regenerate COUNTRY_PASTEL_LIGHT/DARK arrays", "ANCHOR-NOT-FOUND"))
else:
    new_block = LIGHT_JS + "\n" + DARK_JS + "\n"
    old_block = text[si:ei]
    if old_block == new_block:
        results.append(("regenerate COUNTRY_PASTEL_LIGHT/DARK arrays", "already-applied"))
    else:
        text = text[:si] + new_block + text[ei:]
        results.append(("regenerate COUNTRY_PASTEL_LIGHT/DARK arrays", "patched"))

# --- 2. set color_countries_dark per feature in the existing forEach ------
OLD_FOREACH = (
    'MAPDATA.features.forEach(function(f,i){ f.properties.color_countries = COUNTRY_PASTEL[i]; '
    'f.properties.color_antique = COUNTRY_ANTIQUE[i]; f.properties.color_countries_light = COUNTRY_PASTEL_LIGHT[i]; });'
)
NEW_FOREACH = (
    'MAPDATA.features.forEach(function(f,i){ f.properties.color_countries = COUNTRY_PASTEL[i]; '
    'f.properties.color_antique = COUNTRY_ANTIQUE[i]; f.properties.color_countries_light = COUNTRY_PASTEL_LIGHT[i]; '
    'f.properties.color_countries_dark = COUNTRY_PASTEL_DARK[i]; });'
)
if NEW_FOREACH in text:
    results.append(("set color_countries_dark per feature", "already-applied"))
elif OLD_FOREACH in text:
    text = text.replace(OLD_FOREACH, NEW_FOREACH, 1)
    results.append(("set color_countries_dark per feature", "patched"))
else:
    results.append(("set color_countries_dark per feature", "ANCHOR-NOT-FOUND"))

# --- 3. glow layers: line-color -> color_countries_dark, width/blur +~18% -
OLD_SOFT = (
    'paint:{"line-color":["get","color_countries"],"line-width":["interpolate",["linear"],["zoom"],0,3,2,9.5,5,21],'
    '"line-blur":["interpolate",["linear"],["zoom"],0,1.8,2,6,5,12],"line-opacity":0.5}}, "borders");'
)
NEW_SOFT = (
    'paint:{"line-color":["get","color_countries_dark"],"line-width":["interpolate",["linear"],["zoom"],0,3.5,2,11.2,5,25],'
    '"line-blur":["interpolate",["linear"],["zoom"],0,2.1,2,7.1,5,14.2],"line-opacity":0.6}}, "borders");'
)
if NEW_SOFT in text:
    results.append(("country-glow-soft: dark edge color + thicker", "already-applied"))
elif OLD_SOFT in text:
    text = text.replace(OLD_SOFT, NEW_SOFT, 1)
    results.append(("country-glow-soft: dark edge color + thicker", "patched"))
else:
    results.append(("country-glow-soft: dark edge color + thicker", "ANCHOR-NOT-FOUND"))

OLD_TIGHT = (
    'paint:{"line-color":["get","color_countries"],"line-width":["interpolate",["linear"],["zoom"],0,1.2,2,3.8,5,8.5],'
    '"line-blur":["interpolate",["linear"],["zoom"],0,0.5,2,1.3,5,2.6],"line-opacity":0.75}}, "borders");'
)
NEW_TIGHT = (
    'paint:{"line-color":["get","color_countries_dark"],"line-width":["interpolate",["linear"],["zoom"],0,1.4,2,4.5,5,10],'
    '"line-blur":["interpolate",["linear"],["zoom"],0,0.6,2,1.5,5,3.1],"line-opacity":0.85}}, "borders");'
)
if NEW_TIGHT in text:
    results.append(("country-glow-tight: dark edge color + thicker", "already-applied"))
elif OLD_TIGHT in text:
    text = text.replace(OLD_TIGHT, NEW_TIGHT, 1)
    results.append(("country-glow-tight: dark edge color + thicker", "patched"))
else:
    results.append(("country-glow-tight: dark edge color + thicker", "ANCHOR-NOT-FOUND"))

# --- 4. city font hierarchy: tier-1 "big" cities get a real middle weight -
OLD_FONT = 'const CITY_FONT={1:"Noto Sans Regular",2:"Noto Sans Regular",3:"Noto Sans Regular"};   // countries carry the bold now - cities differentiate by size only'
NEW_FONT = 'const CITY_FONT={1:"Open Sans Semibold",2:"Noto Sans Regular",3:"Noto Sans Regular"};   // 3-level hierarchy: country=Bold > big/tier-1 cities=Semibold > regular/tier-2-3 cities=Regular (confirmed real glyph stacks on the font server this map uses, not guessed)'
if NEW_FONT in text:
    results.append(("city font: real 3-level boldness hierarchy", "already-applied"))
elif OLD_FONT in text:
    text = text.replace(OLD_FONT, NEW_FONT, 1)
    results.append(("city font: real 3-level boldness hierarchy", "patched"))
else:
    results.append(("city font: real 3-level boldness hierarchy", "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for name, status in results:
    print("  [%16s] %s" % (status, name))
    if status == "ANCHOR-NOT-FOUND":
        ok = False

print("OK: countries restyle correction applied" if ok else "WARN: one or more anchors not found - review before deploying")
sys.exit(0 if ok else 1)
