#!/usr/bin/env python3
"""Worldbook: widen the on-load geo fly-to so the whole globe is visible, not just a
regional close-up. zoom 3.6 -> 1.6, matching the existing Recenter/Face-the-Sun convention
for "whole globe" zoom already used elsewhere in the app.
Idempotent, pure ASCII source. Usage: python3 worldbook_geoip_zoomout.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = 'map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:3.6, bearing:0, pitch:0, duration:2200});'
NEW = 'map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:1.6, bearing:0, pitch:0, duration:2200});'
SENTINEL = 'map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:1.6, bearing:0, pitch:0, duration:2200});'

if SENTINEL in text:
    open(OUT, "w", encoding="utf-8").write(text)
    print("  [already-applied] geo fly-to zoom out")
elif OLD in text:
    text = text.replace(OLD, NEW, 1)
    open(OUT, "w", encoding="utf-8").write(text)
    print("  [patched] geo fly-to zoom out (3.6 -> 1.6)")
else:
    open(OUT, "w", encoding="utf-8").write(text)
    print("  [ANCHOR-NOT-FOUND] geo fly-to zoom out")
    sys.exit(1)
print("OK")
