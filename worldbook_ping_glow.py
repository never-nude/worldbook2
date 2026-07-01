#!/usr/bin/env python3
"""Worldbook: make the geo-ping actually glow and radiate outward before it fades.

The dot now gets its own brightness flash (new @keyframes wbGeoFlash: box-shadow
swells to a much bigger, brighter double-glow at ~18% through, then settles back to
the resting glow). The ring changes from a crisp 2px border to a soft luminous halo
(radial-gradient + a touch of blur) with more room to expand (inset -9px -> -13px,
max scale 2.4 -> 2.6) and now genuinely brightens from nothing up to full glow before
radiating out and fading, instead of just fading down from a flat .6 opacity. Both
animations share the same 2.4s timing and the same ~18% flash-peak moment, so the dot
and the ring read as one cohesive pulse of light rather than two separate effects.

Runs entirely within the existing 2.4s ping window, well before the fade-out/removal
logic kicks in at 2.8s (shipped in the previous patch) - no timing overlap, no
conflict with the "ping once and disappear" behavior already in place.
Idempotent, pure ASCII source.
Usage: python3 worldbook_ping_glow.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = (
    '.wb-geo-marker{width:14px;height:14px;border-radius:50%;background:var(--accent);'
    'box-shadow:0 0 10px 3px rgba(110,168,254,.85);cursor:pointer;position:relative}\n'
    '.wb-geo-marker::after{content:"";position:absolute;inset:-9px;border-radius:50%;'
    'border:2px solid var(--accent);opacity:.6;animation:wbGeoPulse 2.4s ease-out 1 forwards}\n'
    '@keyframes wbGeoPulse{0%{transform:scale(.35);opacity:.8}100%{transform:scale(2.4);opacity:0}}'
)
NEW = (
    '.wb-geo-marker{width:14px;height:14px;border-radius:50%;background:var(--accent);'
    'box-shadow:0 0 10px 3px rgba(110,168,254,.85);cursor:pointer;position:relative;'
    'animation:wbGeoFlash 2.4s ease-out 1 forwards}\n'
    '.wb-geo-marker::after{content:"";position:absolute;inset:-13px;border-radius:50%;'
    'background:radial-gradient(circle,rgba(110,168,254,0) 0%,rgba(110,168,254,.95) 40%,'
    'rgba(110,168,254,.4) 62%,rgba(110,168,254,0) 78%);filter:blur(1px);'
    'animation:wbGeoPulse 2.4s ease-out 1 forwards}\n'
    '@keyframes wbGeoPulse{0%{transform:scale(.3);opacity:0}18%{transform:scale(.6);opacity:1}'
    '100%{transform:scale(2.6);opacity:0}}\n'
    '@keyframes wbGeoFlash{0%{box-shadow:0 0 10px 3px rgba(110,168,254,.85)}'
    '18%{box-shadow:0 0 32px 14px rgba(110,168,254,1),0 0 58px 24px rgba(110,168,254,.55)}'
    '100%{box-shadow:0 0 10px 3px rgba(110,168,254,.85)}}'
)

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("  [        patched] ping now flashes bright and radiates out before fading")
elif NEW in text:
    print("  [already-applied] ping now flashes bright and radiates out before fading")
else:
    print("  [ ANCHOR-NOT-FOUND] .wb-geo-marker CSS block")
    open(OUT, "w", encoding="utf-8").write(text)
    sys.exit(1)

open(OUT, "w", encoding="utf-8").write(text)
print("OK: geo-ping now glows and radiates before it fades")
