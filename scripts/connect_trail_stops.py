#!/usr/bin/env python3
"""Connect trail arcs to ground-level stops after the forensic reader integration.

Usage: python3 scripts/connect_trail_stops.py v2/index.html v2/index.html
The companion reader/assets are tracked separately. Unknown input is rejected.
"""
from pathlib import Path
import hashlib
import sys

BASE_SHA = '3e5b80cc6ab44edb03511017c262ddc90988a3b4de828cc7f83bbf5c3c004b30'
TARGET_SHA = 'e95f61d8da4376e9ecd0ed2f7dd6f9be8718afa6dfb60c97086fab63d53cd955'
HUNKS = [(390, 392, '<script src="js/trail-model.js?v=5"></script>\n<script src="js/trail-atlas.js?v=5"></script>\n'), (664, 665, 'window.WB_BUILD="2026-09-23.1 connected-stops";\n'), (3087, 3088, 'function _flowElevations(pts,pathMode,anchorStops=false){\n'), (3092, 3093, '  const base=anchorStops?0:(pathMode?21000:40000);\n'), (3094, 3095, '  return pts.map((_,i)=>anchorStops&&(i===0||i===pts.length-1)?0:base+peak*Math.sin(Math.PI*(total?dist[i]/total:i/(pts.length-1||1))));\n'), (3214, 3215, '    if(e.path){ pts=[]; for(let k=0;k<e.path.length-1;k++){ const sg=arcPoints(e.path[k],e.path[k+1],F.anchorStops?64:14); pts=pts.concat(k?sg.slice(1):sg); } }\n'), (3218, 3219, '    const elevs=_flowElevations(pts,pathMode,F.anchorStops===true);\n')]


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: connect_trail_stops.py INPUT OUTPUT")
    source, target = map(Path, sys.argv[1:])
    original = source.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest == TARGET_SHA:
        print("already-applied")
        return
    if digest != BASE_SHA:
        raise SystemExit("baseline mismatch: refusing to overwrite unrelated atlas changes")
    lines = original.decode("utf-8").splitlines(keepends=True)
    for start, end, replacement in reversed(HUNKS):
        lines[start:end] = [replacement]
    result = "".join(lines).encode("utf-8")
    if hashlib.sha256(result).hexdigest() != TARGET_SHA:
        raise SystemExit("target mismatch: patch verification failed")
    target.write_bytes(result)
    print("applied connected-stop delta")


if __name__ == "__main__":
    main()
