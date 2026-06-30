#!/usr/bin/env python3
"""Worldbook rebrand: README.md title + stale live-demo link (still pointed at the archived
atlas repo's github.io URL instead of worldbook.earth). Idempotent, pure ASCII source.
Usage: python3 worldbook_rebrand_readme.py README.md README.md
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "README.md"
OUT = sys.argv[2] if len(sys.argv) > 2 else "README.md"
text = open(INP, encoding="utf-8").read()

DASH = chr(0x2014)   # em dash
ARROW = chr(0x2192)  # rightwards arrow

EDITS = [
    ("title",
     "# Atlas " + DASH + " A Layered World Map, inside a Live Solar System",
     "# Worldbook " + DASH + " A Layered World Map, inside a Live Solar System",
     "# Worldbook " + DASH),
    ("live demo link",
     "**Live demo:** once GitHub Pages is enabled " + ARROW + " `https://never-nude.github.io/atlas/`",
     "**Live demo:** `https://worldbook.earth`",
     "**Live demo:** `https://worldbook.earth`"),
    ("globe heading",
     "**The atlas globe** (MapLibre GL, Natural Earth 50 m geometry)",
     "**The Worldbook globe** (MapLibre GL, Natural Earth 50 m geometry)",
     "**The Worldbook globe**"),
]

res = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
        res.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: README rebrand applied" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
