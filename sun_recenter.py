#!/usr/bin/env python3
"""Add two time-bar controls to Worldbook:
  - Face the Sun: orients the globe to the sub-solar point for the current date/time.
  - Recenter / reset view: flies home, north up.
Idempotent, pure ASCII (glyphs built with chr()). Usage: python3 sun_recenter.py index.html index.html"""
import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
t=open(INP,encoding="utf-8").read()
if 'id="tbHome"' in t:
    open(OUT,"w",encoding="utf-8").write(t); print("  [already-applied]"); print("OK (no-op)"); sys.exit(0)
def once(s,a,b,l):
    n=s.count(a); assert n==1,"anchor %s: %d matches"%(l,n); return s.replace(a,b)
SUN=chr(0x2600); TGT=chr(0x2316); DASH=chr(0x2014)
btns=('<button id="tbSun" class="tbtn" title="Face the Sun '+DASH+' orient the globe to where the Sun is overhead at this date/time">'+SUN+'</button>\n'
      '  <button id="tbHome" class="tbtn" title="Recenter / reset the view (north up)">'+TGT+'</button>\n  ')
t=once(t,'<input type="range" id="tbSpeed"', btns+'<input type="range" id="tbSpeed"', "timebar-buttons")
anchor='if(nb) nb.onclick=()=>{ simEpoch=Date.now(); simDays=0; simLast=0; solarDate=new Date(); updateTimeLabel(); updateSunShade(); };'
add=anchor+('\n  const sunB=document.getElementById("tbSun");'
 '\n  if(sunB) sunB.onclick=()=>{ const ss=subsolarPoint(solarDate); map.flyTo({center:[((ss.lng+540)%360)-180, ss.lat], zoom:1.6, bearing:0, pitch:0, duration:900}); lastInteract=Date.now()+4000; };'
 '\n  const homeB=document.getElementById("tbHome");'
 '\n  if(homeB) homeB.onclick=()=>{ map.flyTo({center:[10,28], zoom:1.6, bearing:0, pitch:0, duration:800}); lastInteract=Date.now()+4000; };')
t=once(t, anchor, add, "timebar-handlers")
open(OUT,"w",encoding="utf-8").write(t)
print("  [patched] added Face-the-Sun + Recenter buttons"); print("OK"); sys.exit(0)
