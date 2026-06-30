#!/usr/bin/env python3
"""Worldbook: actually fix the Countries default-layer override.

Root cause #2 (the real one): there is a SECOND, pre-existing, hardcoded
setLayer("religion") call at the true tail of _atlasBoot() - after wireInteractions(),
buildLayerUI(), etc. - with its own comment ("default opening layer = Religion"). That
one runs AFTER my earlier setLayer("countries") call and silently wins, which is why
changing the activeLayer variable + adding my own call had no visible effect: the
real switch was never the variable, it was this hardcoded literal. Confirmed live in
Chrome (querySourceFeatures + queryRenderedFeatures pixel-probe at the exact USA
screen point) that color_countries and the fill paint expression were already 100%
correct the whole time - this was purely a "last default-setter wins" ordering bug,
not a data or rendering bug.
Also drops my now-redundant earlier setLayer("countries") call since this is the one
real place a default should be set.
Idempotent, pure ASCII source.
Usage: python3 worldbook_countries_fix2.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ('the REAL default-layer switch (was overriding everything else)',
     'setLayer("religion");   // default opening layer = Religion (static choropleth \u2014 fast, reliable first paint)',
     'setLayer("countries");   // default opening layer = Countries reference map (static choropleth \u2014 fast, reliable first paint)',
     'setLayer("countries");   // default opening layer = Countries reference map (static choropleth \u2014 fast, reliable first paint)'),
    ('drop my now-redundant early setLayer call',
     '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});\n  setLayer("countries");',
     '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});',
     '    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});'),
]

# NOTE: check old-in-text BEFORE the sentinel - edit 2's sentinel is a substring of
# its own "old", so checking sentinel first would always read as already-applied.
res = []
for name, old, new, sentinel in EDITS:
    if old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    elif sentinel in text:
        res.append((name, "already-applied"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: Countries is now actually the default" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
