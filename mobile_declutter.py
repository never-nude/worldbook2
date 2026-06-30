#!/usr/bin/env python3
# mobile_declutter.py  --  Worldbook patch (idempotent, pure ASCII)
#
# Decongests the mobile bottom strip:
#   - Lift the legend well clear of the time bar (was bottom:104px, overlapping
#     the bar's top row) and cap its height so an expanded legend still scrolls.
#   - Slim the time bar (tighter gaps/padding, smaller date line, smaller buttons).
#   - Float MapLibre's bottom-right controls (attribution + any zoom) ABOVE the
#     time bar instead of hidden underneath it.
# All edits live inside the existing @media (max-width:700px) block.
#
# Usage: python3 mobile_declutter.py index.html index.html

import sys

SENTINEL = "/* mobile-declutter */"

EDITS = [
    # 1) raise legend above the time bar
    (
        '#legend{max-width:58vw;max-height:52vh;bottom:calc(104px + env(safe-area-inset-bottom));left:calc(10px + env(safe-area-inset-left));padding:9px 11px}',
        '#legend{max-width:62vw;max-height:40vh;bottom:calc(158px + env(safe-area-inset-bottom));left:calc(10px + env(safe-area-inset-left));padding:9px 11px}'
    ),
    # 2) slim the time bar
    (
        '#timebar{bottom:calc(10px + env(safe-area-inset-bottom));gap:5px;padding:6px 9px;flex-wrap:wrap;max-width:96vw;justify-content:center}',
        '#timebar{bottom:calc(10px + env(safe-area-inset-bottom));gap:4px;padding:5px 8px;flex-wrap:wrap;max-width:94vw;justify-content:center}'
    ),
    # 3) smaller, dimmer date line
    (
        '#timebar #tbDate{min-width:0;width:100%;text-align:center;order:9;font-size:11px}',
        '#timebar #tbDate{min-width:0;width:100%;text-align:center;order:9;font-size:10.5px;opacity:.85}'
    ),
]

# 4) inserted after this unique anchor (still inside the mobile media block)
ANCHOR = '#timebar #tbSpeedLbl{display:none}'
INSERT = (
    ANCHOR + "\n"
    "  #timebar button{padding:5px 9px;font-size:12px}\n"
    "  .maplibregl-ctrl-bottom-right{bottom:calc(150px + env(safe-area-inset-bottom)) !important;right:8px !important} " + SENTINEL
)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        t = f.read()

    if SENTINEL in t:
        print("already-applied: mobile_declutter")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(t)
        return

    for i, (old, new) in enumerate(EDITS):
        n = t.count(old)
        if n != 1:
            raise SystemExit("ERROR: edit %d expected 1 match, found %d: %r" % (i, n, old[:60]))
        t = t.replace(old, new)

    if t.count(ANCHOR) != 1:
        raise SystemExit("ERROR: insert anchor not unique: %r" % ANCHOR)
    t = t.replace(ANCHOR, INSERT)

    with open(dst, "w", encoding="utf-8") as f:
        f.write(t)
    print("applied: mobile_declutter (%d edits + 1 insert)" % len(EDITS))


if __name__ == "__main__":
    main()
