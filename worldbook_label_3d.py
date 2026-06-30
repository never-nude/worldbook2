#!/usr/bin/env python3
"""Worldbook: EXPERIMENTAL - true sphere-tangent country labels (custom WebGL layer).

Mike asked twice whether the country-name letters could actually flatten against the
globe, "as if printed right on it", instead of the flat camera-facing plane every
MapLibre symbol layer renders (confirmed live: Russia's label stayed a big flat sign
near the limb even with text-rotation-alignment/text-pitch-alignment set to "map" -
that combo is built for tilted flat maps, not a sphere, and MapLibre's own globe dev
docs only describe adapting symbol COLLISION boxes for the curve, not flattening the
rendered text plane itself).

This adds a second, custom-rendered label system that bypasses MapLibre's symbol
engine entirely: each country name is rendered once to a canvas texture, then drawn
as a quad whose 4 corners are placed via real great-circle offsets from the label
point (the same destPoint() math the day/night terminator already uses) and run
through MapLibre's own injected globe projection shader code (the projectTile()
function every internal MapLibre globe shader uses) - so the quad is genuinely tangent
to the sphere at that point and will foreshorten naturally near the limb, not just
rotate in place. A simple greedy screen-space collision filter (biggest country wins)
stands in for MapLibre's built-in collision system, which a custom layer does not get
for free.

This is genuinely new rendering code with no MapLibre safety net, and nobody has seen
it render yet - it could not be visually verified before shipping (only syntax-
checked and idempotency-tested). A single flag controls it:
  const USE_3D_LABELS=true;
Flip that line to false (or delete it) and the page falls straight back to the flat
MapLibre text layer, which is left fully intact, just permanently hidden while the 3D
flag is on - a one-line, zero-risk revert if the 3D version looks wrong or hurts
performance.
Idempotent, pure ASCII source.
Usage: python3 worldbook_label_3d.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    ('add the sphere-tangent custom WebGL label layer (countryLabels3D), dormant until enabled',
     'map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n    layout:{"text-field":["get","name"],"text-font":["Noto Sans Regular"],\n      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});',
     'map.addLayer({id:"country-labels",type:"symbol",source:"country-labels",\n    layout:{"text-field":["get","name"],"text-font":["Noto Sans Regular"],\n      "text-size":["get","size"],"text-max-width":7,"text-padding":2,\n      "text-rotate":["get","rot"],"text-rotation-alignment":"map","text-pitch-alignment":"map",\n      "symbol-placement":"point","text-allow-overlap":false,"visibility":"none"},\n    paint:{"text-color":"#3a3226","text-halo-color":"rgba(255,255,255,0.55)","text-halo-width":1.1}});\nconst USE_3D_LABELS=true;\nfunction _cl3dCorners(lng,lat,rotDeg,halfW,halfH){\n  const upBrg=(-rotDeg)*DEG, diag=Math.hypot(halfW,halfH), off=Math.atan2(halfW,halfH);\n  const c1=destPoint(lat,lng,upBrg+off,diag*DEG);\n  const c2=destPoint(lat,lng,upBrg-off,diag*DEG);\n  const c3=destPoint(lat,lng,upBrg+Math.PI+off,diag*DEG);\n  const c4=destPoint(lat,lng,upBrg+Math.PI-off,diag*DEG);\n  return [c2,c1,c4,c3];\n}\nfunction _cl3dTexture(gl,name,sizeUnits){\n  const fs=Math.max(22,Math.round(sizeUnits*2.6)), pad=Math.round(fs*0.35);\n  const meas=document.createElement("canvas").getContext("2d");\n  meas.font="600 "+fs+"px \\\'Open Sans\\\',Arial,sans-serif";\n  const tw=Math.max(1,Math.ceil(meas.measureText(name).width));\n  const w=tw+pad*2, h=Math.ceil(fs*1.25)+pad*2;\n  const c=document.createElement("canvas"); c.width=w; c.height=h;\n  const x=c.getContext("2d");\n  x.font="600 "+fs+"px \\\'Open Sans\\\',Arial,sans-serif";\n  x.textBaseline="middle"; x.textAlign="center"; x.lineJoin="round"; x.miterLimit=2;\n  x.strokeStyle="rgba(255,255,255,0.6)"; x.lineWidth=Math.max(2,fs*0.16);\n  x.strokeText(name,w/2,h/2);\n  x.fillStyle="#3a3226"; x.fillText(name,w/2,h/2);\n  const tex=gl.createTexture();\n  gl.bindTexture(gl.TEXTURE_2D,tex);\n  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,c);\n  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);\n  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);\n  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);\n  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);\n  return {tex:tex,w:w,h:h};\n}\nconst countryLabels3D={\n  id:"country-labels-3d",type:"custom",renderingMode:"3d",\n  shaderMap:new Map(), visible:false, items:null,\n  getShader(gl,shaderDescription){\n    if(this.shaderMap.has(shaderDescription.variantName)) return this.shaderMap.get(shaderDescription.variantName);\n    const vs="#version 300 es\\n"+shaderDescription.vertexShaderPrelude+"\\n"+shaderDescription.define+\n      "in vec2 a_pos;in vec2 a_uv;out vec2 v_uv;void main(){gl_Position=projectTile(a_pos);v_uv=a_uv;}";\n    const fs="#version 300 es\\nprecision mediump float;in vec2 v_uv;out vec4 fragColor;uniform sampler2D u_tex;"+\n      "void main(){vec4 c=texture(u_tex,v_uv); if(c.a<0.02) discard; fragColor=c;}";\n    const vsh=gl.createShader(gl.VERTEX_SHADER); gl.shaderSource(vsh,vs); gl.compileShader(vsh);\n    const fsh=gl.createShader(gl.FRAGMENT_SHADER); gl.shaderSource(fsh,fs); gl.compileShader(fsh);\n    const prog=gl.createProgram(); gl.attachShader(prog,vsh); gl.attachShader(prog,fsh); gl.linkProgram(prog);\n    if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){ console.warn("[wb labels3d] shader link failed",gl.getProgramInfoLog(prog)); }\n    const info={prog:prog,aPos:gl.getAttribLocation(prog,"a_pos"),aUv:gl.getAttribLocation(prog,"a_uv"),\n      uTex:gl.getUniformLocation(prog,"u_tex")};\n    this.shaderMap.set(shaderDescription.variantName,info);\n    return info;\n  },\n  onAdd(mapInst,gl){\n    try{\n      this.items=(COUNTRY_LABELS.features||[]).map(function(f){\n        const lng=f.geometry.coordinates[0], lat=f.geometry.coordinates[1], p=f.properties;\n        const tx=_cl3dTexture(gl,p.name,p.size||14);\n        const spanDeg=Math.max(0.6,p.span||4), perpDeg=Math.max(0.4,p.perp||3);\n        let halfW=Math.min(0.45*spanDeg, 0.45*spanDeg), halfH=halfW*(tx.h/tx.w);\n        if(halfH>0.45*perpDeg){ const s=(0.45*perpDeg)/halfH; halfW*=s; halfH*=s; }\n        const corners=_cl3dCorners(lng,lat,p.rot||0,halfW,halfH);\n        const verts=new Float32Array(8);\n        for(let i=0;i<4;i++){\n          const mc=maplibregl.MercatorCoordinate.fromLngLat({lng:corners[i][0],lat:corners[i][1]});\n          verts[i*2]=mc.x; verts[i*2+1]=mc.y;\n        }\n        const uvs=new Float32Array([0,0, 1,0, 0,1, 1,1]);\n        const vbuf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,vbuf); gl.bufferData(gl.ARRAY_BUFFER,verts,gl.STATIC_DRAW);\n        const ubuf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,ubuf); gl.bufferData(gl.ARRAY_BUFFER,uvs,gl.STATIC_DRAW);\n        return {name:p.name,size:p.size||14,tex:tx.tex,vbuf:vbuf,ubuf:ubuf,lng:lng,lat:lat};\n      });\n    }catch(e){ console.warn("[wb labels3d] onAdd failed",e); this.items=[]; }\n  },\n  render(gl,args){\n    if(!this.visible || !this.items || !this.items.length) return;\n    try{\n      const info=this.getShader(gl,args.shaderData);\n      gl.useProgram(info.prog);\n      gl.uniformMatrix4fv(gl.getUniformLocation(info.prog,"u_projection_fallback_matrix"),false,args.defaultProjectionData.fallbackMatrix);\n      gl.uniformMatrix4fv(gl.getUniformLocation(info.prog,"u_projection_matrix"),false,args.defaultProjectionData.mainMatrix);\n      gl.uniform4f(gl.getUniformLocation(info.prog,"u_projection_tile_mercator_coords"),\n        args.defaultProjectionData.tileMercatorCoords[0],args.defaultProjectionData.tileMercatorCoords[1],\n        args.defaultProjectionData.tileMercatorCoords[2],args.defaultProjectionData.tileMercatorCoords[3]);\n      gl.uniform4f(gl.getUniformLocation(info.prog,"u_projection_clipping_plane"),\n        args.defaultProjectionData.clippingPlane[0],args.defaultProjectionData.clippingPlane[1],\n        args.defaultProjectionData.clippingPlane[2],args.defaultProjectionData.clippingPlane[3]);\n      gl.uniform1f(gl.getUniformLocation(info.prog,"u_projection_transition"),args.defaultProjectionData.projectionTransition);\n      gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);\n\n      let placed=this.items;\n      try{\n        const proj=this.items.map(function(it){ const pt=map.project([it.lng,it.lat]); return {it:it,x:pt.x,y:pt.y}; })\n          .sort(function(a,b){ return b.it.size-a.it.size; });\n        const kept=[];\n        proj.forEach(function(cand){\n          for(let i=0;i<kept.length;i++){\n            const p=kept[i], dx=cand.x-p.x, dy=cand.y-p.y, minDist=(cand.it.size+p.it.size)*1.7;\n            if(dx*dx+dy*dy<minDist*minDist) return;\n          }\n          kept.push(cand);\n        });\n        placed=kept.map(function(k){ return k.it; });\n      }catch(e2){ placed=this.items; }\n\n      for(let i=0;i<placed.length;i++){\n        const it=placed[i];\n        gl.activeTexture(gl.TEXTURE0);\n        gl.bindTexture(gl.TEXTURE_2D,it.tex);\n        gl.uniform1i(info.uTex,0);\n        gl.bindBuffer(gl.ARRAY_BUFFER,it.vbuf);\n        gl.enableVertexAttribArray(info.aPos);\n        gl.vertexAttribPointer(info.aPos,2,gl.FLOAT,false,0,0);\n        gl.bindBuffer(gl.ARRAY_BUFFER,it.ubuf);\n        gl.enableVertexAttribArray(info.aUv);\n        gl.vertexAttribPointer(info.aUv,2,gl.FLOAT,false,0,0);\n        gl.drawArrays(gl.TRIANGLE_STRIP,0,4);\n      }\n    }catch(e){ console.warn("[wb labels3d] render failed",e); }\n  }\n};\nmap.addLayer(countryLabels3D);',
     'const countryLabels3D={'),
    ('wire layer visibility to the USE_3D_LABELS flag instead of always showing the flat symbol layer',
     'updateNoDataHatch(key);\n  if(map.getLayer("country-labels")) map.setLayoutProperty("country-labels","visibility", (key==="countries"&&!subOn)?"visible":"none");\n  drawLegend(key);',
     'updateNoDataHatch(key);\n  { const _showC=(key==="countries"&&!subOn);\n    if(map.getLayer("country-labels")) map.setLayoutProperty("country-labels","visibility", (_showC&&typeof USE_3D_LABELS!=="undefined"&&!USE_3D_LABELS)?"visible":"none");\n    if(typeof countryLabels3D!=="undefined") countryLabels3D.visible = (_showC&&typeof USE_3D_LABELS!=="undefined"&&USE_3D_LABELS); }\n  drawLegend(key);',
     'typeof countryLabels3D!=="undefined") countryLabels3D.visible'),
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
print("OK: 3D sphere-tangent labels added (experimental)" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
