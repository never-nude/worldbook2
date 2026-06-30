#!/usr/bin/env python3
"""Worldbook: make the Moon properly occlude behind the Earth instead of popping.

Mike: "make the moon's movement behind the earth not so janky... so it actually
seems to disappear and reappear behind the earth." The Moon renders in its own
Three.js scene on a separate canvas layered on top of the globe (not part of the
same WebGL context/depth buffer as the globe itself), so there was no natural GPU
occlusion between them. The existing code worked around that with a "manual cull":
every frame it computed the Moon's position and just flipped luna.visible on/off
based on whether it was within a measured cutoff circle - a binary, whole-disc pop
the instant it crossed that circle, not a gradual reveal. The in-code comment right
above that logic actually already described the better approach ("an invisible
occluder sized to the globe makes it disappear only when it's genuinely behind
Earth") but that part was apparently never implemented - only the cruder cull was.

This adds that occluder for real: an invisible sphere (colorWrite:false, so it
draws no pixels, but still writes to the depth buffer like any normal opaque mesh)
sized every frame to the globe's already-measured on-screen radius (gpx) and fixed
at the view origin, in the same scene as the Moon. Standard GPU depth testing then
hides the Moon against it automatically and pixel-exactly - it slides behind the
actual circular limb and gets clipped gradually as it crosses, instead of the whole
disc vanishing in one frame. The old binary visible-toggle is removed entirely since
it is now redundant (and was the source of the popping).
Idempotent, pure ASCII source.
Usage: python3 worldbook_moon_occluder.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ("add invisible depth-occluder sphere for the Earth in the Moon's front scene",
     'const fscene=new THREE.Scene();\n    fscene.add(new THREE.AmbientLight(0x223046,0.55));\n    const moonLight=new THREE.PointLight(0xfff2d0,2.2,0,0); fscene.add(moonLight);\n    const fgroup=new THREE.Group(); fscene.add(fgroup);\n    const lunaPivot=new THREE.Group(); lunaPivot.rotation.set(0.38,0,0.08); fgroup.add(lunaPivot);\n    const luna=new THREE.Mesh(new THREE.SphereGeometry(0.004527,24,24),new THREE.MeshStandardMaterial({color:0xd8d8d8,roughness:1}));  // 0.273\xd7Earth radius \xf7 60.3 orbit = to-scale Moon\n    lunaPivot.add(luna);\n    SKY={renderer,scene,camera,sky,bodies,sunLight,sunMesh,fr,frontCam,fscene,fgroup,moonLight,luna,lunaPivot,lunaA:0,ray:new THREE.Raycaster()};',
     'const fscene=new THREE.Scene();\n    fscene.add(new THREE.AmbientLight(0x223046,0.55));\n    const moonLight=new THREE.PointLight(0xfff2d0,2.2,0,0); fscene.add(moonLight);\n    const fgroup=new THREE.Group(); fscene.add(fgroup);\n    const earthOccluder=new THREE.Mesh(new THREE.SphereGeometry(1,48,48),new THREE.MeshBasicMaterial({colorWrite:false})); fscene.add(earthOccluder);  // invisible, depth-only: gives the Moon true GPU depth occlusion against Earth\n    const lunaPivot=new THREE.Group(); lunaPivot.rotation.set(0.38,0,0.08); fgroup.add(lunaPivot);\n    const luna=new THREE.Mesh(new THREE.SphereGeometry(0.004527,24,24),new THREE.MeshStandardMaterial({color:0xd8d8d8,roughness:1}));  // 0.273\xd7Earth radius \xf7 60.3 orbit = to-scale Moon\n    lunaPivot.add(luna);\n    SKY={renderer,scene,camera,sky,bodies,sunLight,sunMesh,fr,frontCam,fscene,fgroup,earthOccluder,moonLight,luna,lunaPivot,lunaA:0,ray:new THREE.Raycaster()};',
     'const fscene=new THREE.Scene();\n    fscene.add(new THREE.AmbientLight(0x223046,0.55));\n    const moonLight=new THREE.PointLight(0xfff2d0,2.2,0,0); fscene.add(moonLight);\n    const fgroup=new THREE.Group(); fscene.add(fgroup);\n    const earthOccluder=new THREE.Mesh(new THREE.SphereGeometry(1,48,48),new THREE.MeshBasicMaterial({colorWrite:false})); fscene.add(earthOccluder);  // invisible, depth-only: gives the Moon true GPU depth occlusion against Earth\n    const lunaPivot=new THREE.Group(); lunaPivot.rotation.set(0.38,0,0.08); fgroup.add(lunaPivot);\n    const luna=new THREE.Mesh(new THREE.SphereGeometry(0.004527,24,24),new THREE.MeshStandardMaterial({color:0xd8d8d8,roughness:1}));  // 0.273\xd7Earth radius \xf7 60.3 orbit = to-scale Moon\n    lunaPivot.add(luna);\n    SKY={renderer,scene,camera,sky,bodies,sunLight,sunMesh,fr,frontCam,fscene,fgroup,earthOccluder,moonLight,luna,lunaPivot,lunaA:0,ray:new THREE.Raycaster()};'),
    ('replace manual visibility-toggle cull with real GPU depth occlusion',
     'if(gpx) SKY.lunaPivot.scale.setScalar(60.3*gpx);\n  SKY.fgroup.rotation.set(rx,ry,0,"YXZ");\n  SKY.moonLight.position.copy(SKY.sunMesh.position).normalize().multiplyScalar(8000);\n  // Manual cull: hide the Moon ONLY when it is genuinely behind Earth (negative depth) AND\n  // projected inside the globe\'s disc. No depth-buffer occluder \u2014 deterministic and exact.\n  if(gpx){ SKY.fgroup.updateMatrixWorld(true);\n    const P=new THREE.Vector3(); SKY.luna.getWorldPosition(P);\n    SKY.luna.visible = !(P.z<0 && Math.hypot(P.x,P.y) < gpx*1.08); }\n  SKY.fr.render(SKY.fscene,SKY.frontCam);',
     'if(gpx){ SKY.lunaPivot.scale.setScalar(60.3*gpx); SKY.earthOccluder.scale.setScalar(gpx); }\n  SKY.fgroup.rotation.set(rx,ry,0,"YXZ");\n  SKY.moonLight.position.copy(SKY.sunMesh.position).normalize().multiplyScalar(8000);\n  // True GPU depth occlusion: earthOccluder is invisible (colorWrite:false) but still writes\n  // depth, sized exactly to the globe\'s measured on-screen radius (gpx) and fixed at the view\n  // origin. The Moon mesh depth-tests against it like any normal opaque object, so it slides\n  // behind Earth\'s actual silhouette pixel-by-pixel instead of popping on a hard cutoff circle.\n  SKY.luna.visible = true;\n  SKY.fr.render(SKY.fscene,SKY.frontCam);',
     'if(gpx){ SKY.lunaPivot.scale.setScalar(60.3*gpx); SKY.earthOccluder.scale.setScalar(gpx); }\n  SKY.fgroup.rotation.set(rx,ry,0,"YXZ");\n  SKY.moonLight.position.copy(SKY.sunMesh.position).normalize().multiplyScalar(8000);\n  // True GPU depth occlusion: earthOccluder is invisible (colorWrite:false) but still writes\n  // depth, sized exactly to the globe\'s measured on-screen radius (gpx) and fixed at the view\n  // origin. The Moon mesh depth-tests against it like any normal opaque object, so it slides\n  // behind Earth\'s actual silhouette pixel-by-pixel instead of popping on a hard cutoff circle.\n  SKY.luna.visible = true;\n  SKY.fr.render(SKY.fscene,SKY.frontCam);'),
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
print("OK: Moon now uses real depth occlusion against Earth" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
