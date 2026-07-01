#!/usr/bin/env python3
"""Worldbook: undo the country-label size inflation from this session's
countries-restyle patches - it broke three separate things Mike flagged in
quick succession from live screenshots:

  1. "scale the country labels down so they don't ever expand over that
     country's borders... never be disproportionately large as compared
     with the geographical size of that country" - tiny territories
     (St. Pierre and Miquelon, Bermuda, St. Vincent and the Grenadines)
     had labels ballooning far past their own tiny landmass into open
     ocean/neighboring countries.
  2. "we can't have countries like italy and france without labels while
     we're still showing their cities" - in densely-packed regions
     (Western/Central Europe), the same oversized labels lost collision
     against equally-oversized neighboring labels and simply didn't
     render at all, even though those countries' cities (unaffected,
     still their original modest size) rendered fine.
  3. "look at how obtrusive the names are" - across the whole globe view,
     large countries (Russia, China, Kazakhstan, Turkey...) rendered with
     text so large it visually dominated the map.

Root cause, one line: `"text-size":["max",["*",["get","size"],1.3],20]`.
The pre-existing "size" property is a per-country value already computed
and tuned (earlier in the project, across the label-placement/containment
work) to fit that specific country's silhouette without crossing borders
or colliding with neighbors. Multiplying it by 1.3 and then flooring every
country at 20px regardless of its actual size overrode that tuning -
hardest on small/compact countries (whose base size was well under the
15.4 threshold where the floor kicks in, so they got inflated the most in
relative terms), but visibly heavy-handed everywhere.

Fix: drop the multiplier and floor entirely, back to the exact value the
existing containment system already computes per country. Keeps the bold
weight (that request stands - it's what gives country names their
hierarchy over city names now) but no longer overrides the underlying
sizing logic that was already correct.

Idempotent, pure ASCII source.
Usage: python3 worldbook_country_label_size_revert.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = '"text-size":["max",["*",["get","size"],1.3],20],"text-max-width":7,"text-padding":2,'
NEW = '"text-size":["get","size"],"text-max-width":7,"text-padding":2,'

if NEW in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] revert country-label text-size to the original per-country computed value (drop 1.3x + 20px-floor inflation)")
print("OK: country labels back to their original, containment-safe sizing" if status in ("patched", "already-applied") else "WARN: anchor not found - review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
