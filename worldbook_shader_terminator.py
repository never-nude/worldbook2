#!/usr/bin/env python3
"""Worldbook: replace the tiled day/night shading with real per-pixel 3D lighting.

Mike's screenshot showed Canada and the US rendering as a visible checkerboard/mosaic
instead of a solid color - not a seam bug (worldbook_fix_terminator_seam.py, which this
patch supersedes for the terminator itself), a fundamental limitation of the old approach:
day/night shading was ~4050 independent flat-shaded GeoJSON polygons (4deg x 4deg cells),
each opacity computed at its own center point. Since real solar elevation varies
continuously across space, EVERY cell ends up a slightly different shade than its neighbor
- that's not a rendering glitch, it's the actual, correct output of a discrete grid trying
to represent a continuous gradient. No amount of edge-padding or finer grid spacing fixes
this in kind - it only makes the tiles smaller, never truly continuous. Mike called this
correctly: "we may have to totally rethink how we color in this layer, maybe an entirely
different type of code." Confirmed with him via AskUserQuestion before doing the rewrite,
given it touches the same Three.js "SKY" system that caused the Moon-occluder GL-state bug
(see worldbook-moon-occluder-fix.md) - he chose "yes, do the full rewrite."

NEW approach: real 3D lighting. The project already has a Three.js scene (SKY.fscene)
compositing the Moon over the map, with an invisible depth-only sphere (earthOccluder)
sized/positioned to exactly match the MapLibre globe's on-screen circle (via the already-
proven gpx measurement) purely so the Moon can occlude/be-occluded correctly. This patch
gives that SAME sphere a real shader material: it keeps writing depth (Moon occlusion still
works, completely unchanged) but now ALSO renders color - a fragment shader that computes,
per pixel, the true angle between that point's surface normal and the real sun direction
(the same sunViewDir() vector already computed every frame for the Sun mesh/light), mapped
to opacity with the exact same day/twilight/night formula the old grid used. This is
standard "lit sphere" 3D graphics - the same technique real 3D-earth visualizations use -
and it's genuinely continuous: no cells, no seams, no mosaic, ever, at any zoom or angle.
It's also cheaper to run: replaces ~4050 setFeatureState calls + JS trig 6x/second with one
small GPU fragment shader that was already going to render every frame regardless.

Four edits:
  1. initSky(): earthOccluder's material changes from an invisible MeshBasicMaterial to a
     THREE.ShaderMaterial (still depthWrite/depthTest true - Moon occlusion unaffected -
     now also transparent+colorWrite for the day/night fragment shader).
  2. renderSky(): the sun-direction vector already computed each frame for the Sun mesh/
     light now also gets copied into the shader's sunDir uniform (one extra line).
  3. The deferred sunshade addSource/addLayer/updateSunShade() call (formerly inside
     _bootHeavyLayers) is removed - shading no longer needs its own MapLibre source/layer.
  4. The per-frame throttled updateSunShade() call inside startSpin()'s frame() is removed
     for the same reason (the old sunGrid/shadeGrid/updateSunShade functions are left
     defined but unused/harmless, in case anything else ever calls them - they're now
     no-ops since map.getSource("sunshade") no longer exists).

Known trade-off, flagged not hidden: the old sunshade layer was deliberately inserted
BELOW "borders" in the map's own layer stack (see worldbook-borders-scope.md) so border
lines wouldn't wash out under the terminator's darkening. The new shading lives in a
SEPARATE canvas composited on top of the entire map (same layer the Moon already uses),
so it could, in principle, sit visually above border lines again on the night side. Kept
the same max opacity (0.5) as before rather than guessing at a new number blindly - worth
watching for border contrast on the night side and tuning down if it becomes a problem.

Idempotent via MARKER. Composes on top of worldbook_fix_terminator_seam.py (safe to run
either order - this patch doesn't touch sunGrid()'s geometry, just stops calling it).
Usage: python3 worldbook_shader_terminator.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "WB_SHADER_TERMINATOR_V1"

A_OLD = ('const earthOccluder=new THREE.Mesh(new THREE.SphereGeometry(1,48,48),new THREE.MeshBasicMaterial({colorWrite:false})); fscene.add(earthOccluder);  '
         '// invisible, depth-only: gives the Moon true GPU depth occlusion against Earth')
A_NEW = ('const earthOccluder=new THREE.Mesh(new THREE.SphereGeometry(1,48,48),new THREE.ShaderMaterial({\n'
         '      uniforms:{sunDir:{value:new THREE.Vector3(0,0,1)}},\n'
         '      transparent:true, depthWrite:true, depthTest:true,\n'
         '      vertexShader:"varying vec3 vN; void main(){ vN=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }",\n'
         '      fragmentShader:"uniform vec3 sunDir; varying vec3 vN; void main(){ float e=dot(vN,normalize(sunDir)); float op=e>0.12?0.0:(e<-0.25?0.5:(0.12-e)/0.37*0.5); gl_FragColor=vec4(0.008,0.016,0.039,op); }"\n'
         '    })); fscene.add(earthOccluder);  '
         '// depth occluder for the Moon (unchanged) AND a truly continuous per-pixel day/night terminator '
         '(/* ' + MARKER + ' */ replaces the old 4050-cell polygon grid, which rendered as a visible mosaic instead of a smooth gradient)')

B_OLD = ('    SKY.sunMesh.position.copy(d); SKY.sunLight.position.copy(d); }   // Sun aligned to the lit hemisphere')
B_NEW = ('    SKY.sunMesh.position.copy(d); SKY.sunLight.position.copy(d);\n'
         '    if(SKY.earthOccluder.material.uniforms) SKY.earthOccluder.material.uniforms.sunDir.value.copy(d).normalize(); }   '
         '// Sun aligned to the lit hemisphere; same direction now also drives the continuous shader-based day/night terminator on earthOccluder')

C_OLD = ('    map.addSource("sunshade",{type:"geojson",data:sunGrid()});\n'
         '    map.addLayer({id:"sunshade",type:"fill",source:"sunshade",\n'
         '      paint:{"fill-color":"#02040a","fill-opacity":["coalesce",["feature-state","op"],0],"fill-opacity-transition":{duration:1500}}}, "borders");   // was "hover" - inserting before "borders" instead puts borders ON TOP of the terminator, so the day/night shading no longer washes out border-line contrast\n'
         '    updateSunShade();\n'
         '    }catch(e2){ console.error("Atlas deferred init (sunshade):",e2); }')
C_NEW = ('    /* sunshade MapLibre layer intentionally removed - day/night shading now lives entirely in the '
         'Three.js earthOccluder shader, see initSky()/renderSky() */\n'
         '    }catch(e2){ console.error("Atlas deferred init (sunshade):",e2); }')

D_OLD = ('      if(t-lastShade>160){ updateSunShade(); lastShade=t; }')
D_NEW = ('      /* day/night shading now driven every rendered frame by the Three.js earthOccluder shader, not this polygon-grid update */')

if MARKER in text:
    status = "already-applied"
else:
    missing = [name for name, old in [("A", A_OLD), ("B", B_OLD), ("C", C_OLD), ("D", D_OLD)] if old not in text]
    if missing:
        status = "ANCHOR-NOT-FOUND (%s)" % ",".join(missing)
    else:
        text = text.replace(A_OLD, A_NEW, 1)
        text = text.replace(B_OLD, B_NEW, 1)
        text = text.replace(C_OLD, C_NEW, 1)
        text = text.replace(D_OLD, D_NEW, 1)
        status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] shader terminator: day/night shading moved from a 4050-cell polygon grid to a continuous per-pixel Three.js shader")
print("OK: shader terminator shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
