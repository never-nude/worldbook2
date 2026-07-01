#!/usr/bin/env python3
"""Worldbook: fix flow-layer legends/controls staying invisible after a
reference layer.

Root cause (found live: "Migration over time" showed no year slider/play/
speed controls at all, just the empty time-bar): reference-type layers
(Countries, Library Globe) explicitly set the shared #legend div's
`display:none` inside drawLegend(). Flow layers (Migration over time, Trade
flows, Debt, etc) never call drawLegend() at all - they go through a
completely separate setFlow() -> drawFlowLegend() path that only ever writes
new innerHTML, never touches display. So the content was always being built
correctly (confirmed live: innerHTML had 3751 chars for migtime while display
stayed "none") - it just stayed hidden from whatever the PREVIOUS layer left
behind. Reproduced exactly: countries -> flow_migtime keeps display:none;
religion -> flow_migtime (both non-reference) works fine, since nothing ever
hid it in that path. This affects every flow layer, not just migration -
fixed once at the shared entry point (setFlow) rather than per-layer.

Idempotent, pure ASCII source.
Usage: python3 worldbook_fix_flow_legend_hidden.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    'function setFlow(key){\n'
    '  flowKey = key; flowIso=null; flowFocusIso=null;\n'
    '  const F=FLOWS[key];'
)
NEW = (
    'function setFlow(key){\n'
    '  flowKey = key; flowIso=null; flowFocusIso=null;\n'
    '  const _flEl=document.getElementById("legend"); if(_flEl) _flEl.style.display="";   // flow layers never go through drawLegend(), which is the only other place that clears a reference layer\'s display:none\n'
    '  const F=FLOWS[key];'
)

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] force #legend visible at the top of setFlow()")
print("OK: flow-layer legends/controls no longer stay hidden after a reference layer" if status in ("patched","already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
