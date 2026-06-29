import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
if 'function splitWrapped(' not in text:
    helpers=(
      'function splitWrapped(pts){ const segs=[]; let cur=[]; const norm=l=>((l+180)%360+360)%360-180;\n'
      '  for(let i=0;i<pts.length;i++){ const lng=pts[i][0],lat=pts[i][1];\n'
      '    if(i>0){ const k0=Math.floor((pts[i-1][0]+180)/360), k1=Math.floor((lng+180)/360);\n'
      '      if(k0!==k1){ const bk=Math.max(k0,k1)*360-180; const t=(bk-pts[i-1][0])/(lng-pts[i-1][0]); const latB=pts[i-1][1]+(lat-pts[i-1][1])*t;\n'
      '        cur.push([norm(bk),latB]); segs.push(cur); cur=[[norm(bk),latB]]; } }\n'
      '    cur.push([norm(lng),lat]); }\n'
      '  if(cur.length) segs.push(cur); return segs; }\n'
      'function geomFor(coords){ const s=splitWrapped(coords); return s.length>1?{type:"MultiLineString",coordinates:s}:{type:"LineString",coordinates:s[0]}; }\n'
      'function unwrapLng(pts){')
    assert text.count('function unwrapLng(pts){')==1
    text=text.replace('function unwrapLng(pts){', helpers)
for a,b in [
    ('geometry:{type:"LineString",coordinates:pts}','geometry:geomFor(pts)'),
    ('geometry:{type:"LineString",coordinates:pts.slice(0,mid+1)}','geometry:geomFor(pts.slice(0,mid+1))'),
    ('geometry:{type:"LineString",coordinates:pts.slice(mid)}','geometry:geomFor(pts.slice(mid))'),
]:
    text=text.replace(a,b)
open(OUT,"w",encoding="utf-8").write(text)
print("OK: arcs split at date line")
