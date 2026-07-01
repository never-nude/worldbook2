#!/usr/bin/env python3
"""Worldbook: increase the map's left padding - the first attempt was apparently
not enough correction.

Mike confirmed the globe still does not look centered after the first padding
patch (left:240, matching the LAYERS panel's literal CSS edge at 16+212=228px).
I cannot render this myself to verify visually, so this is a best-effort second
pass: bumping left padding from 240 to 340px (one honest caveat - I could not
find documentation confirming MapLibre's padding option is fully supported on
globe projection specifically, vs flat mercator where it is well established; if
this still does not look right, that divergence is the more likely explanation,
not the literal pixel value).
Idempotent, pure ASCII source.
Usage: python3 worldbook_padding_bump.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = "left:240"
NEW = "left:340"

count = text.count(NEW)
old_count = text.count(OLD)
if count >= 4:
    print("  [already-applied] left padding bump (240 -> 340)")
elif old_count >= 4:
    text = text.replace(OLD, NEW)
    print(f"  [        patched] left padding bump (240 -> 340), {old_count} occurrences")
else:
    print(f"  [ ANCHOR-NOT-FOUND] expected 4 occurrences of left:240, found {old_count}")
    open(OUT, "w", encoding="utf-8").write(text)
    sys.exit(1)

open(OUT, "w", encoding="utf-8").write(text)
print("OK: left padding increased")
