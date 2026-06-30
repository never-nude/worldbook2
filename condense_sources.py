#!/usr/bin/env python3
"""worldbook_claude build - condense repeated sources in the country/source blocks.

renderSourceBlock() listed every dataset on its own line, so a publisher like the World Bank
repeated a dozen times. This groups by publisher: each publisher appears once, with its
datasets as compact inline links. Single-dataset publishers render as before.

Idempotent. Usage: python3 condense_sources.py index.html index.html
"""
import sys
INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
'function renderSourceBlock(sources){\n'
'  const srcs=uniqueSources(sources);\n'
'  if(!srcs.length) return "";\n'
'  return `<div class="lg-row" style="margin-top:9px;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.6px">${srcs.length>1?"Sources":"Source"}</div><div class="src">${srcs.map(sourceLink).join("")}</div>`;\n'
'}'
)

NEW = (
'function renderSourceBlock(sources){ /* condensed-by-publisher */\n'
'  const srcs=uniqueSources(sources);\n'
'  if(!srcs.length) return "";\n'
'  const groups={}, order=[];\n'
'  srcs.forEach(s=>{ const p=publisherFor(s); if(!groups[p]){ groups[p]=[]; order.push(p); } groups[p].push(s); });\n'
'  const body=order.map(p=>{\n'
'    const list=groups[p];\n'
'    if(list.length===1) return `<div class="src">${sourceLink(list[0])}</div>`;\n'
'    const items=list.map(s=>{ const full=sourceLabel(s); const i=full.indexOf(" \\u2014 "); const ds=i>=0?full.slice(i+3):full; return `<a href="${escapeHTML(s.url)}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none">${escapeHTML(ds)}</a>`; }).join(`<span style="color:#5a6b80"> &middot; </span>`);\n'
'    return `<div style="margin-top:5px;line-height:1.6"><span style="color:#c4cfdd;font-size:11.5px;font-weight:600">${escapeHTML(p)}</span> <span style="font-size:11px">${items}</span></div>`;\n'
'  }).join("");\n'
'  return `<div class="lg-row" style="margin-top:9px;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.6px">${srcs.length>1?"Sources":"Source"}</div>${body}`;\n'
'}'
)

if "/* condensed-by-publisher */" in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, NEW, 1); status = "condensed sources by publisher"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print("  [" + status + "]")
print("OK: sources condensed" if status != "ANCHOR-NOT-FOUND" else "WARN: anchor not found")
sys.exit(0 if status != "ANCHOR-NOT-FOUND" else 1)
