#!/usr/bin/env python3
"""Worldbook: soften the day/night terminator from a visible divide into a soft gradient.

Mike confirmed the shader rewrite (worldbook_shader_terminator.py) fixed the mosaic - solid
colors now, no checkerboard. But he correctly spotted a new, more subtle issue in the
preview: the day/night transition itself reads as a visible "divide" (a fairly abrupt
edge) rather than a soft dusk gradient. Root cause: the shader's opacity formula used a
LINEAR ramp over a fairly narrow elevation band (sin(elevation) from +0.12 down to -0.25,
about 21 degrees of arc) - both narrow enough and linear enough (a straight ramp meeting
two flat plateaus has a visible slope-kink at each end, even though the VALUE is
continuous) to read as an edge rather than a haze.

Given a choice (removing the day/night effect entirely vs. fixing the transition), Mike
asked to fix it rather than lose the feature.

Fix: widen the transition band (sin(elevation) from +0.15 down to -0.35, roughly 28
degrees of arc - wider dusk zone) AND replace the hand-rolled linear ramp with GLSL's
built-in smoothstep(), which has zero slope at both ends by construction - no kink where
the gradient meets full day or full night. Also nudged the max night opacity down slightly
(0.5 -> 0.4) for a gentler overall look, matching Mike's "smooth as silk" polish direction.

Idempotent via presence of "smoothstep(-0.35,0.15". Pure ASCII source.
Requires worldbook_shader_terminator.py to already be applied (this only edits its
fragment shader string).
Usage: python3 worldbook_soften_terminator.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "smoothstep(-0.35,0.15"

OLD = ('fragmentShader:"uniform vec3 sunDir; varying vec3 vN; void main(){ float e=dot(vN,normalize(sunDir)); '
       'float op=e>0.12?0.0:(e<-0.25?0.5:(0.12-e)/0.37*0.5); gl_FragColor=vec4(0.008,0.016,0.039,op); }"')

NEW = ('fragmentShader:"uniform vec3 sunDir; varying vec3 vN; void main(){ float e=dot(vN,normalize(sunDir)); '
       'float night=1.0-smoothstep(-0.35,0.15,e); float op=night*0.4; gl_FragColor=vec4(0.008,0.016,0.039,op); }"')

if MARKER in text:
    status = "already-applied"
elif OLD not in text:
    status = "ANCHOR-NOT-FOUND (fragment shader - is worldbook_shader_terminator.py applied first?)"
else:
    text = text.replace(OLD, NEW, 1)
    status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] terminator softened: wider smoothstep-based gradient, no linear kinks, gentler max opacity")
print("OK: terminator softening shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
