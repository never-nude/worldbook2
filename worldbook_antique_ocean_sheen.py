#!/usr/bin/env python3
"""Worldbook: Library Globe gets a warm ocean fill + a polished-wood sheen.

1) Ocean: there's already a real "ocean" fill layer (a full-sphere polygon
   grid sitting under "fills" - it's what the dark navy background actually
   is, not a Three.js space effect showing through). Toggle its fill-color
   to a deep mahogany brown for antique mode, navy everywhere else - same
   pattern as the existing borders-color toggle in setLayer(), just one more
   paint property riding along with it.

2) Sheen: a second overlay div (sibling to the existing antiqueTexture wood-
   grain div), a single soft diagonal warm highlight via linear-gradient +
   mix-blend-mode:soft-light, NOT the brighter double-highlight/vignette combo
   from the earlier classroom-globe gloss Mike rejected - this reads as light
   catching a lacquered surface, not a plastic toy sheen. Reuses the exact
   same clip-path-to-the-visible-globe-circle mechanism already computed
   every frame for the wood-grain texture (_wbUpdateAntiqueTexture already
   receives cx/cy/r each frame from renderSky() - just clip-path a second
   element with the same values, no new tracking needed).

Idempotent, pure ASCII source.
Usage: python3 worldbook_antique_ocean_sheen.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = []  # (name, old, new, mode, sentinel)

# ---- 1. ocean fill-color toggle, riding along with the existing antique toggle block ----
old1 = (
    '{ const _isAntique=(key==="antique"&&!subOn);   // Library Globe: mahogany borders + surface grain\n'
    '    if(map.getLayer("borders")) map.setPaintProperty("borders","line-color", _isAntique?"#2b1f16":"#05080f");\n'
    '    const _atx=document.getElementById("antiqueTexture"); if(_atx) _atx.style.opacity=_isAntique?"1":"0"; }'
)
new1 = (
    '{ const _isAntique=(key==="antique"&&!subOn);   // Library Globe: mahogany borders + surface grain + warm sea\n'
    '    if(map.getLayer("borders")) map.setPaintProperty("borders","line-color", _isAntique?"#2b1f16":"#05080f");\n'
    '    if(map.getLayer("ocean")) map.setPaintProperty("ocean","fill-color", _isAntique?"#2e1f15":"#0a1b30");\n'
    '    const _atx=document.getElementById("antiqueTexture"); if(_atx) _atx.style.opacity=_isAntique?"1":"0";\n'
    '    const _ash=document.getElementById("antiqueSheen"); if(_ash) _ash.style.opacity=_isAntique?"1":"0"; }'
)
EDITS.append(("toggle ocean color + sheen opacity alongside the existing antique toggle", old1, new1, "insert", 'getLayer("ocean")) map.setPaintProperty("ocean"'))

# ---- 2. sheen div + CSS, right after the existing antiqueTexture div ----
old2 = '<div id="antiqueTexture"></div>'
new2 = '<div id="antiqueTexture"></div><div id="antiqueSheen"></div>'
EDITS.append(("add the antiqueSheen div next to antiqueTexture", old2, new2, "insert", 'id="antiqueSheen"'))

old3 = (
    '  #antiqueTexture{position:absolute;top:0;left:0;width:100%;height:100%;z-index:3;pointer-events:none;'
)
new3 = (
    '  #antiqueSheen{position:absolute;top:0;left:0;width:100%;height:100%;z-index:4;pointer-events:none;'
    'opacity:0;transition:opacity .35s ease;mix-blend-mode:soft-light;'
    'background:linear-gradient(125deg,rgba(255,244,214,0.38) 0%,rgba(255,244,214,0.14) 20%,'
    'rgba(255,244,214,0) 42%,rgba(255,244,214,0) 100%)}\n'
    + old3
)
EDITS.append(("add antiqueSheen CSS (soft diagonal wood-polish highlight)", old3, new3, "insert", "#antiqueSheen{position:absolute"))

# ---- 3. clip the sheen div to the same visible-globe circle every frame ----
old4 = (
    'function _wbUpdateAntiqueTexture(cx,cy,r){\n'
    '  const el=document.getElementById("antiqueTexture"); if(!el) return;\n'
    '  el.style.clipPath = (r&&isFinite(r)) ? ("circle("+r+"px at "+cx+"px "+cy+"px)") : "circle(0px at 0px 0px)";\n'
    '}'
)
new4 = (
    'function _wbUpdateAntiqueTexture(cx,cy,r){\n'
    '  const cp = (r&&isFinite(r)) ? ("circle("+r+"px at "+cx+"px "+cy+"px)") : "circle(0px at 0px 0px)";\n'
    '  const el=document.getElementById("antiqueTexture"); if(el) el.style.clipPath = cp;\n'
    '  const sh=document.getElementById("antiqueSheen"); if(sh) sh.style.clipPath = cp;\n'
    '}'
)
EDITS.append(("clip antiqueSheen to the same globe circle as antiqueTexture", old4, new4, "insert", "const cp = (r&&isFinite(r))"))

res = []
for name, old, new, mode, sentinel in EDITS:
    if mode == "insert":
        if sentinel in text:
            res.append((name, "already-applied"))
        elif old in text:
            text = text.replace(old, new, 1)
            res.append((name, "patched"))
        else:
            res.append((name, "ANCHOR-NOT-FOUND"))
    else:
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
print("OK: Library Globe now has a warm mahogany sea + a polished-wood sheen" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
