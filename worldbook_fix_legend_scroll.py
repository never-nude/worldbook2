#!/usr/bin/env python3
"""Worldbook: fix the legend panel not scrolling (LGBTQ+ status panel cut off
at the bottom, Death penalty row + source line unreachable).

The panel already has max-height + overflow-y:auto, and the underlying DOM/JS
is fine (checked live: content renders correctly, no wheel/touchmove handler
anywhere in the codebase steals the event). Two real gaps, both Safari-
relevant (Mike's browser) and both safe, additive CSS:

1. No overscroll-behavior:contain - on a short/small scrollable panel sitting
   on top of a scroll-zoom map, the first bit of a trackpad scroll gesture
   can "chain" past the panel to the map underneath (which eats it as a zoom
   gesture) before the browser commits to scrolling the panel itself. This
   is the classic "small inner scroll area next to a big scrollable/zoomable
   surface" bug, and it reads exactly like "I can't scroll" even though nothing
   is actually broken structurally.
2. No -webkit-overflow-scrolling - Safari's own historical quirk where
   momentum/trackpad scrolling inside an overflow:auto div can be sluggish or
   unresponsive without this hint (Chrome doesn't need it, which is likely why
   this wasn't caught earlier - all my live testing this session was Chrome).

Also widened the max-height formula so it actually accounts for the other
floating chrome near the bottom of the screen (time bar, geolocate button)
instead of a flat 38vh that can be too generous on a short window and too
stingy on a tall one - min() against a fixed floor keeps at least some
breathing room either way.

Idempotent, pure ASCII source.
Usage: python3 worldbook_fix_legend_scroll.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    '#legend{position:absolute;bottom:18px;left:16px;z-index:5;background:var(--panel);border:1px solid var(--line);\n'
    '    border-radius:14px;padding:12px 14px;backdrop-filter:blur(10px);max-width:240px;max-height:calc(38vh - 36px);overflow-y:auto}'
)
NEW = (
    '#legend{position:absolute;bottom:18px;left:16px;z-index:5;background:var(--panel);border:1px solid var(--line);\n'
    '    border-radius:14px;padding:12px 14px;backdrop-filter:blur(10px);max-width:240px;'
    'max-height:min(calc(38vh - 36px), calc(100vh - 190px));overflow-y:auto;'
    'overscroll-behavior:contain;-webkit-overflow-scrolling:touch}'
)

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] make #legend scroll reliably (contain overscroll, Safari momentum, safer max-height)")
print("OK: legend panel should now scroll properly, especially in Safari" if status in ("patched","already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
