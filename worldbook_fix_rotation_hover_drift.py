#!/usr/bin/env python3
"""Worldbook: fix the stuck/drifting country-hover tooltip during auto-rotation.

Mike's "last chance" screenshot showed a dark tooltip box reading "United States of
America" floating over the Gulf of Mexico, nowhere near actual US territory - a real,
distinct bug, unrelated to the loading-time work. Root cause, found by reading
wireInteractions() and startSpin()'s frame() together:

  - The hover tooltip (a maplibregl.Popup) is anchored via pop.setLngLat(e.lngLat) - a
    real geographic point, set only inside the "mousemove" handler on the "fills" layer.
  - The globe auto-rotates continuously (frame()'s `map.setCenter(c)` call, every frame,
    whenever the user isn't dragging/paused/zoomed into a sub-view).
  - Browsers only fire "mousemove" on actual pointer movement - never just because content
    moved under a STATIONARY cursor. So if you hover a country and hold your mouse still,
    the globe keeps rotating underneath it, but the popup and the "hover" highlight filter
    never get a new event to update from - they stay anchored to the last real mouse
    position/feature, which the auto-rotation then visibly drags away from the country
    that's actually now under the cursor. That's exactly the screenshot: a "United States
    of America" tooltip that had been anchored somewhere over the Gulf coast, dragged
    south/east by the rotation once the mouse stopped moving.

Fix: give wireInteractions() a shared, idempotent-cheap `window._wbClearHover()` (hoisted
onto window so frame() can reach it, since the two functions don't otherwise share scope),
call it from the existing "mouseleave" handler (no behavior change there), and ALSO call it
from frame()'s auto-rotation branch every time the globe actually rotates. Net effect: the
moment the globe moves out from under a hover that isn't being freshly re-confirmed by real
mouse movement, the stale tooltip and highlight are cleared instead of drifting to the wrong
spot. If the user's cursor is still genuinely over a country, the very next real mousemove
immediately restores a correct, freshly-positioned tooltip - so nothing is lost, the stale
state just never lingers or visibly drifts.

Guarded with a `_wbHoverActive` flag so the clear is a no-op (not a redundant setFilter/
Popup.remove() call) on every single rotation frame when there's nothing to clear.

Idempotent via presence of `_wbClearHover`. Pure ASCII source.
Usage: python3 worldbook_fix_rotation_hover_drift.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "_wbClearHover"

A_OLD = ('  const pop=new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});\n'
         '  let _onLine=false;\n'
         '  map.on("mousemove","fills",e=>{\n'
         '    if(subOn) return;\n'
         '    if(_onLine) return;\n'
         '    map.getCanvas().style.cursor="pointer";\n'
         '    const f=e.features[0]; const p=f.properties;\n'
         '    map.setFilter("hover",["==","iso3",p.iso3||""]);\n'
         '    pop.setLngLat(e.lngLat).setHTML(hoverHTML(p,false)).addTo(map);\n'
         '  });\n'
         '  map.on("mouseleave","fills",()=>{ if(subOn)return; map.getCanvas().style.cursor=""; map.setFilter("hover",["==","iso3",""]); pop.remove(); });\n')

A_NEW = ('  window._wbHoverPop=new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});\n'
         '  window._wbHoverActive=false;\n'
         '  window._wbClearHover=()=>{ if(!window._wbHoverActive) return; window._wbHoverActive=false;\n'
         '    map.getCanvas().style.cursor=""; map.setFilter("hover",["==","iso3",""]); window._wbHoverPop.remove(); };\n'
         '  let _onLine=false;\n'
         '  map.on("mousemove","fills",e=>{\n'
         '    if(subOn) return;\n'
         '    if(_onLine) return;\n'
         '    window._wbHoverActive=true;\n'
         '    map.getCanvas().style.cursor="pointer";\n'
         '    const f=e.features[0]; const p=f.properties;\n'
         '    map.setFilter("hover",["==","iso3",p.iso3||""]);\n'
         '    window._wbHoverPop.setLngLat(e.lngLat).setHTML(hoverHTML(p,false)).addTo(map);\n'
         '  });\n'
         '  map.on("mouseleave","fills",()=>{ if(subOn)return; window._wbClearHover(); });\n')

B_OLD = ('      if(!subOn && !dragging && (Date.now()-lastInteract>1200)){\n'
         '        const c=map.getCenter(); c.lng=((c.lng - (simSpeed/60)*360*dt + 540)%360)-180; map.setCenter(c);\n'
         '      }\n')

B_NEW = ('      if(!subOn && !dragging && (Date.now()-lastInteract>1200)){\n'
         '        const c=map.getCenter(); c.lng=((c.lng - (simSpeed/60)*360*dt + 540)%360)-180; map.setCenter(c);\n'
         '        if(window._wbClearHover) window._wbClearHover();   // rotation moved the globe under a stationary cursor - a stale hover would otherwise silently drift with it\n'
         '      }\n')

if MARKER in text and "window._wbHoverPop" in text:
    status = "already-applied"
else:
    missing = [name for name, old in [("A", A_OLD), ("B", B_OLD)] if old not in text]
    if missing:
        status = "ANCHOR-NOT-FOUND (%s)" % ",".join(missing)
    else:
        text = text.replace(A_OLD, A_NEW, 1)
        text = text.replace(B_OLD, B_NEW, 1)
        status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] rotation-hover-drift fix: clears stale hover tooltip/highlight whenever auto-rotation moves the globe under a stationary cursor")
print("OK: rotation-hover-drift fix shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
