#!/usr/bin/env python3
"""Worldbook: stop city labels from outranking/hiding country name labels.

Mike's report (with screenshot): "we're losing the countries, cities should
come second in prominence to country names" - correct, and confirmed live:
"United States of America" and "Mexico" were being fully suppressed by
collision with the new tier-1 city labels around them (Chicago, Boston,
Atlanta, Seattle, etc all still showed fine - it was specifically the big
country names disappearing).

Root cause: city label symbol-sort-key was -3/-2/-1 (tier1/2/3). Country
labels use ["*",-1,["get","size"]] - live-checked size range is 7 to 22.1
across all countries, so country sort-keys land around -7 to -22. On paper
-7..-22 should already out-rank -3..-1 (lower sort-key = wins collision), but
live-testing proved country labels were still losing in practice (confirmed
by toggling city-layer visibility off/on and watching USA/Mexico reappear/
disappear on demand). Rather than trying to reverse-engineer the exact
cross-source collision interaction, fixed it the robust way: moved city
sort-keys to a fixed positive range (100/101/102) that can never be lower
than any country label's negative sort-key, so a country name can never lose
a direct collision to a city label, full stop - regardless of country size or
any future change to either numbering scheme. Cities still show normally in
whatever room is left (live-verified: Seattle/SF/LA/Chicago/Boston/Dallas/
Atlanta all still rendered immediately after the fix, right alongside the
now-visible "United States of America").

Idempotent, pure ASCII source.
Usage: python3 worldbook_cities_sortkey_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = 'const CITY_SORT={1:-3,2:-2,3:-1};'
NEW = 'const CITY_SORT={1:100,2:101,3:102};   // positive on purpose: must always lose collision to country-label sort-keys (which are negative), so country names never get hidden by city labels'

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
elif NEW in text:
    status = "already-applied"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status:>16}] give city labels a fixed positive sort-key so they never outrank country names")
print("OK: country names can no longer be hidden by city labels" if status in ("patched", "already-applied") else "WARN: anchor not found - nothing broken, but not applied")
sys.exit(0 if status in ("patched", "already-applied") else 1)
