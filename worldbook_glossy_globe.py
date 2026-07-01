#!/usr/bin/env python3
"""Worldbook: give the globe a glossy, laminated-plastic sheen - the classroom-globe
nostalgia Mike asked to lean into further.

Two-layer look, both driven by the sphere's real on-screen position/radius (reusing
gpx and the globe's projected center point, which renderSky() already computes every
frame for the Moon-occlusion work - no new measurement needed, just reused):

  1. A broad, soft highlight offset toward the upper-left, like an overhead classroom
     light catching the laminate. Not a laser-point specular dot - real diffuse plastic
     sheen is broad and soft, so it fades out over a wide radius.
  2. A faint dark vignette right at the true limb (the sphere's actual edge, not a
     guess) - glossy spheres show a touch more edge falloff than matte ones, and this
     reads as roundness/depth even at a glance.

Both are plain low-alpha rgba() radial gradients on a new full-viewport overlay div,
positioned/sized in JS each frame - no CSS blend-mode tricks (those interact
unpredictably with the WebGL canvases underneath), just ordinary alpha compositing,
kept subtle enough not to fight border/label legibility. This is a from-scratch
aesthetic call per Mike's steer to make these judgment calls directly - easy to
tune (all the numbers live in one place, _wbUpdateGloss) if he wants it stronger,
weaker, or angled differently once he sees it live.

Idempotent, pure ASCII source.
Usage: python3 worldbook_glossy_globe.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = []

# ---- 1. new overlay div, alongside the existing sky/moon layers ----
old1 = (
    '<div id="map"></div>\n'
    '<canvas id="sky"></canvas>\n'
    '<canvas id="moonCv"></canvas>\n'
    '<div id="skyTip"></div>'
)
new1 = (
    '<div id="map"></div>\n'
    '<canvas id="sky"></canvas>\n'
    '<canvas id="moonCv"></canvas>\n'
    '<div id="glossHi"></div>\n'
    '<div id="skyTip"></div>'
)
EDITS.append(("add the glossHi overlay div", old1, new1, new1))

# ---- 2. CSS: position/layer it with the other full-screen overlays ----
old2 = (
    '#moonCv{position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;pointer-events:none}'
)
new2 = (
    '#moonCv{position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;pointer-events:none}\n'
    '  #glossHi{position:absolute;top:0;left:0;width:100%;height:100%;z-index:3;pointer-events:none}'
)
EDITS.append(("add glossHi CSS positioning", old2, new2, new2))

# ---- 3. JS helper that paints the gradient from the globe's real screen center/radius ----
old3 = 'function renderSky(){\n  requestAnimationFrame(renderSky);'
new3 = (
    '// classroom-globe gloss: a soft off-center highlight (overhead-light sheen on the\n'
    '// laminate) plus a faint dark vignette right at the sphere\'s true limb. Positioned\n'
    '// from the globe\'s real projected center/radius, so it tracks zoom and pan exactly.\n'
    'function _wbUpdateGloss(cx,cy,r){\n'
    '  const el=document.getElementById("glossHi"); if(!el) return;\n'
    '  if(!r || !isFinite(r)){ el.style.background="none"; return; }\n'
    '  const hx=cx-r*0.32, hy=cy-r*0.38;\n'
    '  el.style.background=\n'
    '    "radial-gradient(circle at "+hx+"px "+hy+"px, rgba(255,255,255,.55) 0%, rgba(255,255,255,.26) 16%, rgba(255,255,255,.08) 38%, rgba(255,255,255,0) 65%),"+\n'
    '    "radial-gradient(circle at "+cx+"px "+cy+"px, rgba(5,10,20,0) 76%, rgba(5,10,20,.10) 90%, rgba(5,10,20,.24) 100%)";\n'
    '}\n'
    'function renderSky(){\n'
    '  requestAnimationFrame(renderSky);'
)
EDITS.append(("add _wbUpdateGloss helper", old3, new3, new3))

# ---- 4. call it from inside renderSky(), reusing c0/gpx it already computed ----
old4 = '    if(mx>2) gpx=mx; }catch(e){}'
new4 = '    if(mx>2) gpx=mx; _wbUpdateGloss(c0.x,c0.y,gpx); }catch(e){}'
EDITS.append(("wire the gloss update into the existing per-frame gpx measurement", old4, new4, new4))

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
print("OK: glossy classroom-globe sheen added" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
