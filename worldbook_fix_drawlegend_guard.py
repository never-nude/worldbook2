#!/usr/bin/env python3
"""Worldbook: guard drawLegend() against a removed-from-picker layer key.

Since Library Globe ("antique") was hidden from META.layers, calling
setLayer("antique") directly (e.g. from the console, to preview/test it while
it's hidden) throws inside drawLegend - layerCfg(key) returns undefined for
any key no longer in META.layers, then `c.type` crashes. Doesn't affect any
real user-facing path (nothing in the UI can pass an unlisted key), but it
means I - or Mike - can't easily preview the hidden layer's WIP styling
without the console throwing. One-line defensive guard: treat a missing
config the same as a reference layer (hide the legend, do nothing else).

Idempotent, pure ASCII source.
Usage: python3 worldbook_fix_drawlegend_guard.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    'function drawLegend(key){\n'
    '  const c=layerCfg(key), el=document.getElementById("legend");\n'
    '  if(c.type==="reference"){ el.style.display="none"; return; }'
)
NEW = (
    'function drawLegend(key){\n'
    '  const c=layerCfg(key), el=document.getElementById("legend");\n'
    '  if(!c || c.type==="reference"){ el.style.display="none"; return; }'
)

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] guard drawLegend against a layer key with no META.layers entry")
print("OK: hidden/unlisted layers no longer crash drawLegend" if status in ("patched","already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
