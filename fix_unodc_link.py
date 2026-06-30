#!/usr/bin/env python3
"""Fix the dead UNODC World Drug Report link in the older flow-layer citations
(align to the working -2025 URL already used by the Sources & Methodology panel).
Idempotent. Usage: python3 fix_unodc_link.py index.html index.html"""
import sys
INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

DEAD = "https://www.unodc.org/unodc/en/data-and-analysis/world-drug-report.html"
GOOD = "https://www.unodc.org/unodc/en/data-and-analysis/world-drug-report-2025.html"

n = text.count(DEAD)
if n:
    text = text.replace(DEAD, GOOD)
open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{'fixed '+str(n)+' link(s)' if n else 'already-applied (no dead link)'}]")
print("OK: UNODC link fixed")
