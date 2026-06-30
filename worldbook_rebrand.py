#!/usr/bin/env python3
"""Worldbook rebrand: rename the product surface from "Atlas" to "Worldbook".
Internal-only identifiers (_atlasBooted, etc.) and proper-noun dataset titles that happen to
contain the word "Atlas" (Sreda's Atlas of Religions, WALS, UNESCO's Interactive Atlas, IIE's
Project Atlas) are left untouched - only user-facing chrome changes.
Adds basic description/OG/twitter share meta tags (none existed before).
Idempotent, pure ASCII source (non-ASCII chars written as \\uXXXX escapes).
Usage: python3 worldbook_rebrand.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

DASH = chr(0x2014)   # em dash, matches the existing "Atlas -- A Layered World Map"
OPLUS = chr(0x2295)  # circled plus, matches the existing "(+) Enter the atlas" button

SHARE_DESC = ("Worldbook is an interactive 3D globe reference work: sourced data on every "
              "country across religion, politics, economy, health, debt, trade, and migration, "
              "plus a real-time solar system.")

EDITS = [
    # 1) <title> + add description/OG/twitter share meta (none existed before)
    ("title + share meta",
     "<title>Atlas " + DASH + " A Layered World Map</title>",
     "<title>Worldbook " + DASH + " A Layered World Map</title>\n"
     '<meta name="description" content="' + SHARE_DESC + '" />\n'
     '<meta property="og:type" content="website" />\n'
     '<meta property="og:url" content="https://worldbook.earth/" />\n'
     '<meta property="og:title" content="Worldbook ' + DASH + ' A Layered World Map" />\n'
     '<meta property="og:description" content="' + SHARE_DESC + '" />\n'
     '<meta name="twitter:card" content="summary" />\n'
     '<meta name="twitter:title" content="Worldbook ' + DASH + ' A Layered World Map" />\n'
     '<meta name="twitter:description" content="' + SHARE_DESC + '" />',
     'property="og:title"'),
    # 2) main H1 wordmark (subtitle span text stays "a layered world map")
    ("h1 wordmark",
     '<h1>Atlas<span id="subtitle">a layered world map</span></h1>',
     '<h1>Worldbook<span id="subtitle">a layered world map</span></h1>',
     '<h1>Worldbook<span id="subtitle">'),
    # 3) "back to globe" button from the solar-system view
    ("solar-back button",
     '<button class="sbtn" id="solarBack">' + OPLUS + ' Enter the atlas</button>',
     '<button class="sbtn" id="solarBack">' + OPLUS + ' Enter Worldbook</button>',
     OPLUS + ' Enter Worldbook'),
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
print("OK: Worldbook rebrand applied" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
