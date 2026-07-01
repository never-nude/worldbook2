#!/usr/bin/env python3
"""Worldbook: bring a restrained touch of the Library Globe's "varnished object"
warmth into the DEFAULT (Countries) view - Mike wants the whole site to read as
professional/engaging with "a slight touch of nostalgia... the default globe that
looks like something from a 90's elementary school classroom."

The full antique treatment (mahogany ocean/borders, brown-monochrome country
fills, bespoke 3D serif labels) already exists but is deliberately NOT what's
being reused here - that's a full costume change, not a "slight touch," and
would fight the existing pastel-choropleth/dark-space identity that's already
been tuned extensively this project. Instead this reuses the two purely-optical
overlay elements the antique layer already has (#antiqueSheen - a warm
soft-light gradient simulating a lacquered/varnished surface catching overhead
light; #antiqueTexture - a faint aged-paper grain via SVG feTurbulence, overlay-
blended) and extends their trigger to ALSO fire at reduced intensity on the
Countries/default view, leaving every color (borders, ocean, country fills,
fonts) exactly as-is. A dynamic version of this (`glossHi`, tracking cursor/
globe position every frame) was tried earlier this project and removed - this
takes the simpler, static, already-tested CSS-gradient approach instead of
re-attempting the dynamic one, on the theory that a static restrained accent is
lower-risk than a moving highlight that was already tried and pulled.

Chosen intensities (fully static, tunable via two numbers if it reads too
strong/weak live): sheen 0.45 of full (vs 1.0 on the real antique layer),
texture 0.22 of full (vs 1.0) - meant to read as "well-loved object" grain,
not a color cast. Verify live before considering this final; these are
starting values, not a measured-optimal result.

Idempotent, pure ASCII. Usage: python3 worldbook_default_nostalgic_sheen.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = ('const _atx=document.getElementById("antiqueTexture"); if(_atx) _atx.style.opacity=_isAntique?"1":"0";\n'
       '    const _ash=document.getElementById("antiqueSheen"); if(_ash) _ash.style.opacity=_isAntique?"1":"0"; }')
NEW = ('const _isCountriesDefault=(key==="countries"&&!subOn);   // slight nostalgic sheen/grain on the default reference view too - restrained, not the full antique reskin\n'
       '    const _atx=document.getElementById("antiqueTexture"); if(_atx) _atx.style.opacity=_isAntique?"1":(_isCountriesDefault?"0.22":"0");\n'
       '    const _ash=document.getElementById("antiqueSheen"); if(_ash) _ash.style.opacity=_isAntique?"1":(_isCountriesDefault?"0.45":"0"); }')

if NEW in text:
    status = "already-applied"
elif OLD in text:
    text = text.replace(OLD, NEW, 1)
    status = "patched"
else:
    status = "ANCHOR-NOT-FOUND"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] restrained nostalgic sheen/texture on default Countries view")
print("OK: default view now has a slight varnished-globe touch" if status in ("patched","already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
