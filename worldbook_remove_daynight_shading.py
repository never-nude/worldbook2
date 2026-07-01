#!/usr/bin/env python3
"""Worldbook: remove day/night shading entirely, per Mike's explicit request.

Three rounds in: the original polygon-grid sunshade rendered as a visible checkerboard
mosaic (fixed via a Three.js shader rewrite); the shader's transition then read as a hard
"divide" (softened with a wider smoothstep gradient); now, at more extreme zoom levels,
Mike is seeing a badly offset/oversized dark halo floating outside the globe entirely when
zoomed way out, and a distinct hard-edged "semispherical crown" shape on the limb at medium
zoom - both look like the earthOccluder sphere's screen-space sizing/positioning doesn't
track the actual MapLibre globe projection cleanly across the zoom range, something the
Moon-occlusion use of this same sphere apparently tolerates but a full-color shaded overlay
makes obvious. Mike asked directly: "is there any way to remove whatever's causing these
altogether" - so this patch removes the day/night visual effect entirely rather than
attempting a 4th fix.

This does NOT touch Moon rendering/occlusion - earthOccluder's ORIGINAL, long-proven
MeshBasicMaterial({colorWrite:false}) is restored exactly as it was before any of this
round's changes, so the Moon still correctly hides behind/in front of Earth. Only the
color/shading contribution added by worldbook_shader_terminator.py +
worldbook_soften_terminator.py is removed. The old polygon-grid sunshade system (sunGrid/
shadeGrid/updateSunShade, the "sunshade" MapLibre source/layer) stays removed too - not
resurrected - since that was the original source of the mosaic bug; the net result of this
patch is simply NO day/night shading of any kind, the globe is lit uniformly at all times.

Two edits, both reverting parts of worldbook_shader_terminator.py:
  1. earthOccluder's material: ShaderMaterial -> back to the original MeshBasicMaterial.
  2. renderSky(): removes the now-pointless sunDir uniform update line (harmless to leave
     since MeshBasicMaterial has no .uniforms and the call was already guarded, but cleaner
     to remove so nothing in the code implies day/night shading still exists).

Idempotent via presence of the restored MeshBasicMaterial line. Pure ASCII source.
Usage: python3 worldbook_remove_daynight_shading.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = 'new THREE.MeshBasicMaterial({colorWrite:false})); fscene.add(earthOccluder);  // invisible, depth-only'

A_OLD = ('const earthOccluder=new THREE.Mesh(new THREE.SphereGeometry(1,48,48),new THREE.ShaderMaterial({\n'
         '      uniforms:{sunDir:{value:new THREE.Vector3(0,0,1)}},\n'
         '      transparent:true, depthWrite:true, depthTest:true,\n'
         '      vertexShader:"varying vec3 vN; void main(){ vN=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }",\n'
         '      fragmentShader:"uniform vec3 sunDir; varying vec3 vN; void main(){ float e=dot(vN,normalize(sunDir)); float night=1.0-smoothstep(-0.35,0.15,e); float op=night*0.4; gl_FragColor=vec4(0.008,0.016,0.039,op); }"\n'
         '    })); fscene.add(earthOccluder);  // depth occluder for the Moon (unchanged) AND a truly continuous per-pixel day/night terminator (/* WB_SHADER_TERMINATOR_V1 */ replaces the old 4050-cell polygon grid, which rendered as a visible mosaic instead of a smooth gradient)')

A_NEW = ('const earthOccluder=new THREE.Mesh(new THREE.SphereGeometry(1,48,48),' + MARKER)

B_OLD = ('    SKY.sunMesh.position.copy(d); SKY.sunLight.position.copy(d);\n'
         '    if(SKY.earthOccluder.material.uniforms) SKY.earthOccluder.material.uniforms.sunDir.value.copy(d).normalize(); }   // Sun aligned to the lit hemisphere; same direction now also drives the continuous shader-based day/night terminator on earthOccluder')
B_NEW = ('    SKY.sunMesh.position.copy(d); SKY.sunLight.position.copy(d); }   // Sun aligned to the lit hemisphere; day/night shading removed per Mike\'s request (zoom-dependent artifacts on the earthOccluder sphere) - see worldbook_remove_daynight_shading.py')

if MARKER in text:
    status = "already-applied"
else:
    missing = [name for name, old in [("A", A_OLD), ("B", B_OLD)] if old not in text]
    if missing:
        status = "ANCHOR-NOT-FOUND (%s)" % ",".join(missing)
    else:
        text = text.replace(A_OLD, A_NEW, 1)
        text = text.replace(B_OLD, B_NEW, 1)
        status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] day/night shading removed entirely - earthOccluder reverted to its original invisible depth-only material, Moon occlusion unaffected")
print("OK: day/night removal shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
