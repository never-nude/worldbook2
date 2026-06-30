#!/usr/bin/env python3
"""Worldbook: fix the country-labels-vanished regression from worldbook_label_3d.py.

Root cause: USE_3D_LABELS and countryLabels3D were declared with const INSIDE
the _atlasBoot() function body (right after the country-labels addLayer call,
which also lives inside _atlasBoot()). But setLayer() - the function that actually
flips label visibility on and off - is a SEPARATE, sibling top-level function. It
cannot see const/let bindings declared inside a different function body; that
scoping is local. The typeof X!=="undefined" guards in setLayer() were meant to
protect against the variables not existing yet, but they silently masked the real
bug: from inside setLayer(), neither USE_3D_LABELS nor countryLabels3D is ever in
scope, so typeof always reports "undefined" there, both visibility branches
evaluate false, and NEITHER the flat layer nor the 3D layer ever gets shown.
Confirmed live: the browser console showed countryLabels3D as literally undefined
at the page top level, exactly matching this diagnosis.

Fix: attach both to window explicitly (window.X = ...) instead of const. Global
window properties resolve correctly as bare identifiers from any function, anywhere
in the page, regardless of where the assignment statement physically sits - no need
to relocate the (large) custom-layer code block itself.

Also defaults USE_3D_LABELS back to false for this emergency fix - restores the
proven-working flat rotated labels immediately. The 3D layer code is untouched and
still there; flip window.USE_3D_LABELS to true (one line, same spot) and redeploy
whenever ready to test it again now that it can actually be reached.
Idempotent, pure ASCII source.
Usage: python3 worldbook_label_3d_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ('fix variable scoping bug: USE_3D_LABELS must be global, not local to _atlasBoot()',
     'const USE_3D_LABELS=true;',
     'window.USE_3D_LABELS=false;',
     'window.USE_3D_LABELS=false;'),
    ('fix variable scoping bug: countryLabels3D must be global, not local to _atlasBoot()',
     'const countryLabels3D={',
     'window.countryLabels3D={',
     'window.countryLabels3D={'),
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
print("OK: labels restored (flat 2D), 3D layer fixed but left off" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
