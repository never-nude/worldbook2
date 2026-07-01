#!/usr/bin/env python3
"""worldbook_claude build -- shrink the flat-hit-test-vs-lifted-ribbon divergence
that makes flow-arc hover tooltips hard to trigger.

Root cause, live-verified via javascript_tool against production
(worldbook.earth), not just read from code: flow arcs render as lifted 3D
ribbons (custom WebGL "flow-3d" layer) but are HIT-TESTED against a flat,
invisible proxy line ("flow-lines", opacity 0). A prior patch
(hover_hit_widen.py) widened that proxy line's tolerance band, but for a real
corridor (IND->GBR) I measured the visible ribbon sitting ~14-25 screen px
*above* the flat proxy at a representative point along the arc -- outside the
already-shipped tolerance band (whi=20 => ~10px half-width). Confirmed via
map.queryRenderedFeatures: querying exactly on the visible ribbon returned zero
hits; querying at the flat proxy position (where the ribbon visually is NOT)
returned hits every time.

Two-part fix:
 1. Shrink the elevation formula itself (_flowElevations) for regular
    (non-pathMode) flow arcs -- the dominant term causing screen-space
    divergence in the first place. base 60000->40000 (-33%), peak's
    far-scaled ceiling 290000+595000*far -> 180000+380000*far (~-35-38%).
    pathMode arcs (migtime historical player) are untouched -- their lift is
    already ~3x smaller and wasn't implicated by the live test.
 2. A further, more modest widen of the (invisible, zero visual cost) hit-test
    tolerance on top of the shrink, as a safety margin: wlo/whi/rlo/rhi all
    +~30%. Not widened further than this alone, since the dense-hub live test
    also showed 3 corridors already bundled within the current tolerance --
    over-widening trades hover-miss for hover-wrong-arc.

This changes the height of the 3D arc effect (an aesthetic knob, not the
underlying architecture) -- ribbons are still visibly lifted, just less
dramatically, in exchange for the hover interaction actually working.

Re-verified live after patching (simulated the exact patched values against
the running page via javascript_tool, same IND->GBR corridor): hit-test now
registers reliably in an 8px band centered almost exactly on the visible
ribbon, vs. the previous inconsistent/offset band. Overview screenshot
confirmed the 3D arc effect is still clearly visible, not flattened out.

Idempotent. Usage: python3 fix_flow_hover_divergence.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

FIXES = [
    ("hit-test tolerance: further widen (invisible, safety margin on top of the elevation shrink)",
     '  const wlo=m?10.0:8.0, whi=m?20.0:16.0, rlo=m?2.2:1.8, rhi=m?4.4:3.4;',
     '  const wlo=m?13.0:10.0, whi=m?26.0:20.0, rlo=m?2.9:2.3, rhi=m?5.7:4.4;'),
    ("elevation formula: shrink lift for regular flow arcs (root-cause fix)",
     '  const base=pathMode?21000:60000;\n'
     '  const peak=pathMode?(92000+172000*far):(290000+595000*far);',
     '  const base=pathMode?21000:40000;\n'
     '  const peak=pathMode?(92000+172000*far):(180000+380000*far);'),
]

results = []
for label, OLD, NEW in FIXES:
    if NEW in text:
        results.append((label, "already-applied"))
    elif OLD in text:
        text = text.replace(OLD, NEW, 1)
        results.append((label, "patched"))
    else:
        results.append((label, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for label, status in results:
    print(f"  [{status:>16}] {label}")
    if status not in ("patched", "already-applied"):
        ok = False

print("OK: flow-arc hover divergence reduced" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
