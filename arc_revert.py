#!/usr/bin/env python3
"""Revert the arc 'dampening'. Blending toward a straight lng/lat line was wrong: a straight
lng/lat path on a globe is a constant-latitude line, which renders as horizontal rings around
the globe. Set K=1 so arcPoints returns the true great circle (still unwrapped + split at the
date line, which is correct). Pure great-circle arcs are the standard for globe flow maps.
python3 arc_revert.py index.html index.html   (idempotent)"""
import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert ('var K=0.35;' in text) or ('var K=1;' in text), "K marker not found"
text=text.replace('var K=0.35;','var K=1;')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: arcs reverted to pure great circles (K=1); horizontal-ring artifact removed")
