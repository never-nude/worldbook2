#!/usr/bin/env python3
"""Worldbook: two changes per Mike's review.

1) HIDE (not delete) the Library Globe layer. Mike doesn't like it. Removing just
   the META.layers picker entry - the layer disappears from the sidebar and can't
   be selected, but the palette, texture, and setLayer wiring all stay in the file,
   dormant and harmless. "For now" suggested this might not be a permanent kill, so
   keeping the underlying work intact costs nothing and makes it a one-line
   re-add if he wants to revisit it later, rather than redoing the adjacency-graph
   palette work from scratch.

2) Country labels now show on every layer except satellite (was: only on
   "countries" itself). Exactly the same label rendering/positioning/containment
   logic as before - this only widens WHEN the existing country-labels layer is
   visible, nothing about how a label looks or where it sits changes. Topo
   (physical relief) keeps labels since Mike only called out satellite by name;
   satellite stays label-free since real photographic imagery is the one place
   they'd feel out of place. Still hidden while drilled into a subnational view
   (labeling all 242 countries while looking at just the UK's four nations
   wouldn't make sense) - that part of the condition is unchanged.

Idempotent, pure ASCII source.
Usage: python3 worldbook_hide_antique_and_labels.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = []

# ---- 1. remove the Library Globe entry from the picker (code stays, just unreachable) ----
old1 = (
    '{"group":"Reference","key":"countries","label":"Countries","type":"reference"},'
    '{"group":"Reference","key":"antique","label":"Library Globe","type":"reference"},'
)
new1 = '{"group":"Reference","key":"countries","label":"Countries","type":"reference"},'
EDITS.append(("hide the Library Globe layer from the picker", old1, new1, new1))

# ---- 2. country labels visible on every layer except satellite ----
old2 = 'const _showC=(key==="countries"&&!subOn);'
new2 = 'const _showC=(key!=="satellite"&&!subOn);'
EDITS.append(("show country labels on every layer except satellite", old2, new2, new2))

res = []
for name, old, new, sentinel in EDITS:
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
print("OK: library globe hidden, labels widened to all non-satellite layers" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
