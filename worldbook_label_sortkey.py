#!/usr/bin/env python3
"""Worldbook: prioritize bigger countries' labels when two neighbors collide.

Mike: "some labels (UK here) aren't visible" - UK was rendering correctly
(checked the live data: reasonable anchor point in central England, normal
size) but text-allow-overlap is false and the country-labels layer had no
symbol-sort-key, so when two labels are close enough to collide (UK sits
~6deg from Ireland), MapLibre falls back to its own internal placement order
rather than anything cartographically meaningful - so the more prominent
country can lose to a smaller neighbor for no good reason.

Adds "symbol-sort-key":["*",-1,["get","size"]] to the country-labels layer.
Lower sort-key = higher placement priority in MapLibre, so multiplying size by
-1 means bigger countries (bigger text-size, which already scales with country
area) consistently win collisions against smaller close neighbors - UK over
Ireland, Czechia over Slovakia, etc. - instead of an arbitrary default ordering.
This is a layer-config change only, no label data is touched.
Idempotent, pure ASCII source.
Usage: python3 worldbook_label_sortkey.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

LAYOUT_OLD = '    layout:{"text-field":["get","name"],"text-font":["Noto Sans Regular"],\n      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n'
LAYOUT_NEW = '    layout:{"text-field":["get","name"],"text-font":["Noto Sans Regular"],\n      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n      "symbol-sort-key":["*",-1,["get","size"]],\n      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n'

if LAYOUT_NEW in text:
    print("  [already-applied] symbol-sort-key on country-labels layer")
elif LAYOUT_OLD in text:
    text = text.replace(LAYOUT_OLD, LAYOUT_NEW, 1)
    print("  [        patched] symbol-sort-key on country-labels layer")
else:
    print("  [ ANCHOR-NOT-FOUND] country-labels layer layout block")
    open(OUT, "w", encoding="utf-8").write(text)
    sys.exit(1)

open(OUT, "w", encoding="utf-8").write(text)
print("OK: bigger countries now win label collisions")
