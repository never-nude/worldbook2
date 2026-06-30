#!/usr/bin/env python3
"""Worldbook: mobile-only bottom bar declutter.

Two changes, both confined to the existing @media (max-width:700px) block (desktop
untouched):
  1) The collapsed layer-legend chip was floating ~80-140px above the time bar with
     dead space in between (two separate-feeling floating panels stacked vertically).
     Pulled its bottom offset in so it sits right above the time bar - one bottom
     cluster, not two. (It still grows upward from this same anchor when expanded,
     so tapping it open is unaffected.)
  2) Sources moves out of the top bar (which only had Sources left in it after the
     Solar System button was removed) to a small pill fixed at bottom-right, level
     with the time bar - reachable in one tap, but no longer competing for attention
     up top. Desktop keeps Sources in the top bar as before (this is a mobile-only
     position:fixed override).
Idempotent, pure ASCII source.
Usage: python3 worldbook_mobile_bottom.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ('dock the collapsed legend chip directly above the time bar instead of floating ~80px higher with dead space underneath, so the two read as one bottom cluster instead of two stacked panels; relocate Sources off the top bar to a small pill anchored bottom-right, same band as the time bar, out of the way but always reachable',
     '#legend{left:50%;right:auto;transform:translateX(-50%);width:min(340px,86vw);max-width:min(340px,86vw);max-height:36vh;bottom:calc(156px + env(safe-area-inset-bottom));padding:9px 11px}',
     '#legend{left:50%;right:auto;transform:translateX(-50%);width:min(340px,86vw);max-width:min(340px,86vw);max-height:36vh;bottom:calc(80px + env(safe-area-inset-bottom));padding:9px 11px}\n    #sourcesBtn{position:fixed!important;top:auto!important;left:auto!important;margin-left:0!important;bottom:calc(14px + env(safe-area-inset-bottom));right:calc(10px + env(safe-area-inset-right));padding:5px 10px;font-size:11px;z-index:6}'),
]

res = []
for name, old, new in EDITS:
    if old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    else:
        res.append((name, "already-applied"))

open(OUT, "w", encoding="utf-8").write(text)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: mobile bottom bar updated")
