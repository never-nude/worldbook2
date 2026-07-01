#!/usr/bin/env python3
"""Worldbook: add Burundi's and Tanzania's REAL capitals (Gitega, Dodoma) to the
CITIES dataset, closing a data gap surfaced during the capitals-only cities work.

Burundi's political capital moved to Gitega in Dec 2018 (effective 2019); Tanzania's
moved to Dodoma in 1996 (state functions fully relocated by 2023) - both real, dated,
sourced moves, not disputed or contested. Confirmed via web search, not assumed.
Sources: geodatos.net/latitude.to coordinate lookups for Gitega (-3.427,29.925) and
Dodoma; Dodoma was ALREADY present in this file's CITIES array (tier 3, "regular
city" - correct coordinates, wrong classification), Gitega was missing entirely.

Two edits:
  1. Retier the existing Dodoma entry from tier 3 -> tier 1 (it was already present,
     just misclassified as a non-capital regular city, not added fresh).
  2. Insert a new Gitega entry (tier 1) in alphabetical position, since it didn't
     exist in the 862-entry CITIES array at all.

This intentionally does NOT remove Bujumbura or Dar es Salaam from the data - they
remain as real, populated, tier-1 megacities (former capitals), just no longer
classified as the CURRENT capital once worldbook_cities_capitals_only.py's CAPITALS
list is updated separately to point at Gitega/Dodoma instead.

Idempotent, pure ASCII. Usage: python3 worldbook_add_real_capitals.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

d_old = '["Dodoma",35.75,-6.183,3]'
d_new = '["Dodoma",35.75,-6.183,1]'
g_old = '["Georgetown",-58.167,6.802,1],'
g_new = '["Georgetown",-58.167,6.802,1],["Gitega",29.925,-3.427,1],'

results = []

if d_new in text:
    results.append(("Dodoma retier 3->1", "already-applied"))
elif d_old in text:
    text = text.replace(d_old, d_new, 1)
    results.append(("Dodoma retier 3->1", "patched"))
else:
    results.append(("Dodoma retier 3->1", "ANCHOR-NOT-FOUND"))

if '"Gitega"' in text:
    results.append(("Gitega insert (tier 1)", "already-applied"))
elif g_old in text:
    text = text.replace(g_old, g_new, 1)
    results.append(("Gitega insert (tier 1)", "patched"))
else:
    results.append(("Gitega insert (tier 1)", "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for label, status in results:
    print(f"  [{status:>16}] {label}")
    if status not in ("patched", "already-applied"):
        ok = False
print("OK: Burundi/Tanzania real capitals added" if ok else "WARN: review before deploying")
sys.exit(0 if ok else 1)
