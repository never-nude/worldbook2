#!/usr/bin/env python3
# mobile_hud.py  --  Worldbook patch (idempotent, pure ASCII)
#
# Aligns the mobile bottom panels into a single centered "HUD" stack instead of
# a staggered legend (left) + time bar (center):
#   - Legend and time bar share ONE centerline and ONE width (min(340px,86vw)),
#     stacked vertically with even spacing -> edges line up.
#   - The MapLibre attribution / source dot is tucked into the gap between them,
#     right-aligned to the cluster edge, instead of floating loose.
# Stacks on top of mobile_declutter; edits live in the @media (max-width:700px) block.
#
# Usage: python3 mobile_hud.py index.html index.html

import sys

SENTINEL = "min(340px,86vw)"

EDITS = [
    # legend: centered, fixed cluster width, sits above the gap
    (
        '#legend{max-width:62vw;max-height:40vh;bottom:calc(158px + env(safe-area-inset-bottom));left:calc(10px + env(safe-area-inset-left));padding:9px 11px}',
        '#legend{left:50%;right:auto;transform:translateX(-50%);width:min(340px,86vw);max-width:min(340px,86vw);max-height:36vh;bottom:calc(156px + env(safe-area-inset-bottom));padding:9px 11px}'
    ),
    # time bar: same centerline + same width as the legend
    (
        '#timebar{bottom:calc(10px + env(safe-area-inset-bottom));gap:4px;padding:5px 8px;flex-wrap:wrap;max-width:94vw;justify-content:center}',
        '#timebar{bottom:calc(14px + env(safe-area-inset-bottom));gap:4px;padding:6px 9px;flex-wrap:wrap;width:min(340px,86vw);max-width:min(340px,86vw);justify-content:center}'
    ),
    # attribution dot: into the gap, aligned to the cluster's right edge
    (
        '.maplibregl-ctrl-bottom-right{bottom:calc(150px + env(safe-area-inset-bottom)) !important;right:8px !important}',
        '.maplibregl-ctrl-bottom-right{bottom:calc(120px + env(safe-area-inset-bottom)) !important;right:7vw !important}'
    ),
]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        t = f.read()

    if SENTINEL in t:
        print("already-applied: mobile_hud")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(t)
        return

    for i, (old, new) in enumerate(EDITS):
        n = t.count(old)
        if n != 1:
            raise SystemExit("ERROR: edit %d expected 1 match, found %d: %r" % (i, n, old[:60]))
        t = t.replace(old, new)

    with open(dst, "w", encoding="utf-8") as f:
        f.write(t)
    print("applied: mobile_hud (%d edits)" % len(EDITS))


if __name__ == "__main__":
    main()
