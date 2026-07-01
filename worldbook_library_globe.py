#!/usr/bin/env python3
"""Worldbook: new reference layer - "Library Globe" - an antique mahogany/wood-and-
brass look, living right next to "Countries" in the layer picker (same shapes, same
mechanism, restyled entirely: color, borders, and a subtle surface grain).

Palette: recomputed the country adjacency graph directly from the live MAPDATA (243
polygons -> shapely intersection test with a small buffer for numerically-touching
borders) and greedy-colored it against 14 hand-picked antique tones (aged gold,
terracotta, muted olive/sage, brick red, burnt sienna, dusty rose, chestnut, etc.) -
same technique the modern pastel palette used, but ALSO rejecting perceptually-close
color pairs between actual neighbors (checked RGB distance, not just palette index),
since several of these warm/muted tones are close enough to be confused for the same
color otherwise. Verified: 0 exact adjacent conflicts, only 2 residual "somewhat
close but not identical" adjacent pairs out of ~330 (both involving Botswana, still
separated by the ordinary border line) - accepted as a reasonable real-world result
rather than chasing a perfect palette.

Texture: a small tileable SVG fractalNoise pattern (anisotropic base frequency for a
faint linear "grain" rather than uniform static), warm sepia-tinted, blended with
mix-blend-mode:overlay at low alpha - baked into the SVG itself so the overlay div's
opacity is a clean 0/1 show-hide switch, not a strength dial. Clipped to the globe's
actual on-screen circle every frame (reusing the same gpx/center measurement
renderSky() already computes for the Moon-occlusion work), so it tracks zoom and pan
exactly instead of being a fixed-position guess.

Borders switch to a dark mahogany-brown (#2b1f16) instead of near-black while this
layer is active; country labels/legend behave exactly like "Countries" already does
(type:"reference" already suppresses the legend and is handled by the existing
label-visibility check, both for free, no changes needed there).

Scope note: did not touch the surrounding starfield/space color - that's a separate
Three.js system and a bigger, riskier change than what was asked. Left as a possible
follow-up if the surrounding "space" should feel warmer too.

Idempotent, pure ASCII source.
Usage: python3 worldbook_library_globe.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

DASH = "—"

COUNTRY_ANTIQUE = ["#b08968","#9c6b4a","#c9a15a","#a8493f","#c4a35f","#a05c3f","#5f7a6e","#a8493f","#7c8471","#96694f","#c9a15a","#b5652f","#8a9a5b","#a8493f","#c17f3e","#6f7d55","#b5652f","#9c6b4a","#b08968","#7c8471","#a05c3f","#8b5e6b","#c4a35f","#5f7a6e","#96694f","#c9a15a","#b5652f","#8a9a5b","#a8493f","#c17f3e","#6f7d55","#b5652f","#b08968","#8b5e6b","#9c6b4a","#8b5e6b","#b08968","#a05c3f","#9c6b4a","#b08968","#9c6b4a","#a8493f","#c4a35f","#c4a35f","#96694f","#7c8471","#a05c3f","#8b5e6b","#9c6b4a","#a8493f","#5f7a6e","#c4a35f","#5f7a6e","#a05c3f","#a05c3f","#9c6b4a","#7c8471","#c9a15a","#7c8471","#8b5e6b","#5f7a6e","#8a9a5b","#c4a35f","#c4a35f","#5f7a6e","#7c8471","#c4a35f","#96694f","#96694f","#b08968","#c9a15a","#b5652f","#8a9a5b","#a8493f","#c17f3e","#b5652f","#b5652f","#7c8471","#8b5e6b","#c9a15a","#c17f3e","#96694f","#6f7d55","#c4a35f","#b5652f","#6f7d55","#8b5e6b","#b5652f","#b08968","#7c8471","#5f7a6e","#b5652f","#9c6b4a","#9c6b4a","#b08968","#7c8471","#5f7a6e","#a05c3f","#8b5e6b","#a05c3f","#c4a35f","#c17f3e","#c17f3e","#96694f","#c4a35f","#c9a15a","#8a9a5b","#c9a15a","#a05c3f","#5f7a6e","#5f7a6e","#b5652f","#96694f","#8a9a5b","#c9a15a","#a8493f","#6f7d55","#b5652f","#a8493f","#c9a15a","#8b5e6b","#6f7d55","#8b5e6b","#7c8471","#96694f","#b08968","#c9a15a","#8a9a5b","#c17f3e","#b5652f","#96694f","#8a9a5b","#6f7d55","#7c8471","#b08968","#a8493f","#c17f3e","#5f7a6e","#5f7a6e","#8b5e6b","#5f7a6e","#8a9a5b","#a8493f","#96694f","#c17f3e","#6f7d55","#b08968","#b08968","#c9a15a","#96694f","#7c8471","#a05c3f","#a8493f","#9c6b4a","#6f7d55","#c17f3e","#c17f3e","#8b5e6b","#b5652f","#5f7a6e","#8a9a5b","#b08968","#7c8471","#8a9a5b","#a05c3f","#8b5e6b","#c4a35f","#5f7a6e","#96694f","#6f7d55","#c9a15a","#9c6b4a","#8b5e6b","#c4a35f","#c4a35f","#5f7a6e","#a05c3f","#a8493f","#a8493f","#b5652f","#c17f3e","#8a9a5b","#a8493f","#6f7d55","#8a9a5b","#c17f3e","#9c6b4a","#c17f3e","#9c6b4a","#c4a35f","#c9a15a","#6f7d55","#c9a15a","#6f7d55","#8a9a5b","#c9a15a","#7c8471","#a05c3f","#a8493f","#c9a15a","#96694f","#9c6b4a","#b08968","#b5652f","#8b5e6b","#a05c3f","#9c6b4a","#6f7d55","#96694f","#8b5e6b","#a8493f","#b5652f","#c17f3e","#c17f3e","#9c6b4a","#b08968","#96694f","#9c6b4a","#6f7d55","#b08968","#8a9a5b","#7c8471","#a05c3f","#7c8471","#a05c3f","#8b5e6b","#c4a35f","#5f7a6e","#96694f","#c9a15a","#c17f3e","#b08968","#b5652f","#8a9a5b","#6f7d55","#6f7d55","#8a9a5b","#7c8471","#a05c3f","#8a9a5b","#c4a35f","#a8493f"]
ANTIQUE_JS = "[" + ",".join('"' + c + '"' for c in COUNTRY_ANTIQUE) + "]"

SVG_TEXTURE_URL = (
    "data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20width%3D%27240%27%20"
    "height%3D%27240%27%3E%3Cfilter%20id%3D%27n%27%3E%3CfeTurbulence%20type%3D%27fractalNoise%27%20"
    "baseFrequency%3D%270.012%200.28%27%20numOctaves%3D%274%27%20seed%3D%2711%27%20stitchTiles%3D%27stitch%27%20"
    "result%3D%27t%27/%3E%3CfeColorMatrix%20in%3D%27t%27%20type%3D%27matrix%27%20values%3D%270%200%200%200%200.55%20%20"
    "0%200%200%200%200.42%20%200%200%200%200%200.28%20%200%200%200%200.35%200%27/%3E%3C/filter%3E%3Crect%20width%3D%27100%25%27%20"
    "height%3D%27100%25%27%20filter%3D%27url%28%23n%29%27/%3E%3C/svg%3E"
)

EDITS = []

# ---- 1. new layer entry, right next to "Countries" in the picker (APPEND -> "insert") ----
old1 = '{"group":"Reference","key":"countries","label":"Countries","type":"reference"},'
new1 = old1 + '{"group":"Reference","key":"antique","label":"Library Globe","type":"reference"},'
EDITS.append(("register the Library Globe layer", old1, new1, "insert"))

# ---- 2. COUNTRY_ANTIQUE palette + color_antique per-feature assignment ----
old2 = (
    'const COUNTRY_PASTEL='
)
# anchor further: insert the new const declaration right after COUNTRY_PASTEL's own
# declaration line closes. Easiest unique anchor: the assignment call site itself.
old2b = 'f.properties.color_countries = COUNTRY_PASTEL[i]; });'
new2b = (
    'f.properties.color_countries = COUNTRY_PASTEL[i]; '
    'f.properties.color_antique = COUNTRY_ANTIQUE[i]; });'
)
EDITS.append(("assign color_antique alongside color_countries per feature", old2b, new2b, new2b))

old2c = 'const COUNTRY_PASTEL=['
new2c = 'const COUNTRY_ANTIQUE=' + ANTIQUE_JS + ';\nconst COUNTRY_PASTEL=['
# old2c ("const COUNTRY_PASTEL=[") is a SUFFIX of new2c (new2c ends with exactly that
# text) - checking old-first would keep finding it inside the already-patched text and
# re-insert the whole COUNTRY_ANTIQUE declaration a second time. Tag as "insert" so the
# loop checks the longer string (new) first, same fix as the other prefix/suffix cases.
EDITS.append(("declare the COUNTRY_ANTIQUE palette", old2c, new2c, "insert"))

# ---- 3. setLayer(): switch border color + toggle the texture overlay ----
old3 = (
    '  updateNoDataHatch(key);\n'
    '  { const _showC=(key==="countries"&&!subOn);\n'
    '    if(map.getLayer("country-labels")) map.setLayoutProperty("country-labels","visibility", '
    '(_showC&&typeof USE_3D_LABELS!=="undefined"&&!USE_3D_LABELS)?"visible":"none");\n'
    '    if(typeof countryLabels3D!=="undefined") countryLabels3D.visible = '
    '(_showC&&typeof USE_3D_LABELS!=="undefined"&&USE_3D_LABELS); }\n'
    '  drawLegend(key);\n'
    '}\n'
)
new3 = (
    '  updateNoDataHatch(key);\n'
    '  { const _showC=(key==="countries"&&!subOn);\n'
    '    if(map.getLayer("country-labels")) map.setLayoutProperty("country-labels","visibility", '
    '(_showC&&typeof USE_3D_LABELS!=="undefined"&&!USE_3D_LABELS)?"visible":"none");\n'
    '    if(typeof countryLabels3D!=="undefined") countryLabels3D.visible = '
    '(_showC&&typeof USE_3D_LABELS!=="undefined"&&USE_3D_LABELS); }\n'
    '  { const _isAntique=(key==="antique"&&!subOn);   // Library Globe: mahogany borders + surface grain\n'
    '    if(map.getLayer("borders")) map.setPaintProperty("borders","line-color", _isAntique?"#2b1f16":"#05080f");\n'
    '    const _atx=document.getElementById("antiqueTexture"); if(_atx) _atx.style.opacity=_isAntique?"1":"0"; }\n'
    '  drawLegend(key);\n'
    '}\n'
)
EDITS.append(("setLayer switches border color + texture visibility for Library Globe", old3, new3, new3))

# ---- 4. HTML: new overlay div (APPEND -> "insert") ----
old4 = '<div id="skyTip"></div>'
new4 = '<div id="skyTip"></div>\n<div id="antiqueTexture"></div>'
EDITS.append(("add the antiqueTexture overlay div", old4, new4, "insert"))

# ---- 5. CSS: position/layer the overlay div (APPEND -> "insert") ----
old5 = '#moonCv{position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;pointer-events:none}'
new5 = (
    old5 + '\n  #antiqueTexture{position:absolute;top:0;left:0;width:100%;height:100%;z-index:3;'
    'pointer-events:none;opacity:0;transition:opacity .35s ease;background-repeat:repeat;'
    'mix-blend-mode:overlay;background-image:url("' + SVG_TEXTURE_URL + '")}'
)
EDITS.append(("add antiqueTexture CSS (positioning + the grain texture itself)", old5, new5, "insert"))

# ---- 6. renderSky(): keep the texture clipped to the globe's real on-screen circle ----
old6 = '    if(mx>2) gpx=mx; }catch(e){}'
new6 = '    if(mx>2) gpx=mx; _wbUpdateAntiqueTexture(c0.x,c0.y,gpx); }catch(e){}'
EDITS.append(("clip the texture to the globe's true radius every frame", old6, new6, new6))

# ---- 7. the clip-path helper itself (APPEND-before -> "insert", NEW ends with OLD) ----
old7 = 'function renderSky(){\n  requestAnimationFrame(renderSky);'
new7 = (
    '// Library Globe surface grain: clipped to the globe\'s actual projected circle each\n'
    '// frame (reusing the same measurement renderSky() already does for the Moon), so the\n'
    '// texture tracks zoom/pan exactly instead of guessing a fixed size and position.\n'
    'function _wbUpdateAntiqueTexture(cx,cy,r){\n'
    '  const el=document.getElementById("antiqueTexture"); if(!el) return;\n'
    '  el.style.clipPath = (r&&isFinite(r)) ? ("circle("+r+"px at "+cx+"px "+cy+"px)") : "circle(0px at 0px 0px)";\n'
    '}\n'
    + old7
)
EDITS.append(("add the _wbUpdateAntiqueTexture clip-path helper", old7, new7, "insert"))

res = []
for entry in EDITS:
    if len(entry) == 4 and entry[3] == "insert":
        name, old, new, _ = entry
        if new in text:
            res.append((name, "already-applied"))
        elif old in text:
            text = text.replace(old, new, 1)
            res.append((name, "patched"))
        else:
            res.append((name, "ANCHOR-NOT-FOUND"))
        continue
    name, old, new, sentinel = entry
    if old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    elif sentinel in text:
        res.append((name, "already-applied"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: Library Globe layer added" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
