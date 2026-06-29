import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if 'wlo=m?2.4:2.0' not in text:
    patches=[
      ('  const wlo=m?1.7:1.2, whi=m?4.4:3.2, rlo=m?1.9:1.5, rhi=m?4.0:3.0;',
       '  const wlo=m?2.4:2.0, whi=m?5.6:4.6, rlo=m?2.2:1.8, rhi=m?4.4:3.4;','base'),
      ('  const opI=["interpolate",["linear"],["get","w"], 0, m?0.66:0.58, 1, m?0.95:0.90];',
       '  const opI=["interpolate",["linear"],["get","w"], 0, m?0.82:0.74, 1, m?0.98:0.95];','opacity'),
      ('  map.setPaintProperty("flow-lines","line-width", wI);',
       '  map.setPaintProperty("flow-lines","line-width", wI);\n  map.setPaintProperty("flow-lines","line-blur", 0.18);','blur'),
    ]
    for a,b,l in patches: text=patch(text,a,b,l)
open(OUT,"w",encoding="utf-8").write(text)
print("OK: bolder lines")
