import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
if 'function arcPoints(' not in text:
    helper=('function arcPoints(a,b,segs){ var gc=gcPoints(a,b,segs); unwrapLng(gc);\n'
      '  var bl=b[0]; while(bl-a[0]>180)bl-=360; while(bl-a[0]<-180)bl+=360;\n'
      '  var K=0.45;\n'
      '  for(var i=0;i<gc.length;i++){ var f=i/segs, linLng=a[0]+(bl-a[0])*f, linLat=a[1]+(b[1]-a[1])*f;\n'
      '    gc[i][0]=linLng+(gc[i][0]-linLng)*K; gc[i][1]=linLat+(gc[i][1]-linLat)*K; }\n'
      '  return gc; }\n'
      'function unwrapLng(pts){')
    text=patch(text,'function unwrapLng(pts){',helper,'arcPoints-helper')
    text=patch(text,'pts=gcPoints(a,b,48);','pts=arcPoints(a,b,48);','centroid-arc')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: centroid arcs dampened — no more polar rings")
