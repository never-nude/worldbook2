#!/usr/bin/env python3
"""worldbook_claude build - make flow-arc hover/click register more easily.

The visible arcs are lifted 3D ribbons, but the queryable hit-test geometry is the FLAT
surface 'flow-lines' layer (opacity 0). Lift makes the aimed-at ribbon and the actual hit
line diverge on screen (worst at the arc apex). The hit line was also thin (~3-6px desktop).
This widens that INVISIBLE hit line so the cursor catches arcs far more easily. Visuals
unchanged (the line stays opacity 0; the real art is the separate WebGL ribbon layer).

Idempotent. Usage: python3 hover_hit_widen.py index.html index.html
"""
import sys
INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = "  const wlo=m?7.0:3.0, whi=m?13.0:6.5, rlo=m?2.2:1.8, rhi=m?4.4:3.4;"
NEW = "  const wlo=m?10.0:8.0, whi=m?20.0:16.0, rlo=m?2.2:1.8, rhi=m?4.4:3.4;"

if NEW in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, NEW, 1); status = "patched (hit-line widened)"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print("  [" + status + "]")
print("OK: flow hover/click target widened" if status != "ANCHOR-NOT-FOUND" else "WARN: anchor not found")
sys.exit(0 if status != "ANCHOR-NOT-FOUND" else 1)
