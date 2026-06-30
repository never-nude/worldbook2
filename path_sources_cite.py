#!/usr/bin/env python3
"""worldbook_claude build — surface each path/flow layer's SOURCES as a citation.

Every flow/path layer already carries a `sources:[{label,url}]` array, but drawFlowLegend()
never rendered it — sources only showed in the country popup. So when you explore a path
(ocean currents, Silk Road, trade flows, ...) there was no visible attribution.

This appends a "Source / Sources" block to the layer legend, each entry a clickable link
styled like a citation (publication/article title -> external link), reusing the existing
`.src a` styling from the country popup for consistency.

Idempotent. Usage:  python3 path_sources_cite.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = '  if(F.note) b+=`<div class="lg-row" style="color:var(--muted);font-size:10.5px;font-style:italic;margin-top:6px;line-height:1.4">${F.note}</div>`;'

CITE = (
    '\n'
    '  if(F.sources&&F.sources.length){'
    ' b+=`<div class="lg-row" style="margin-top:9px;color:var(--muted);font-size:10px;'
    'text-transform:uppercase;letter-spacing:.6px">${F.sources.length>1?"Sources":"Source"}</div>'
    '<div class="src">`;'
    ' F.sources.forEach(s=>{ b+=`<a href="${s.url}" target="_blank" rel="noopener">↗ ${s.label}</a>`; });'
    ' b+=`</div>`; }'
)

SENTINEL = 'F.sources&&F.sources.length'

if SENTINEL in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, OLD + CITE, 1)
    status = "patched"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] path/flow source citations")
print("OK: path sources now cited in legend" if status in ("patched", "already-applied")
      else "WARN: anchor not found")
sys.exit(0 if status in ("patched", "already-applied") else 1)
