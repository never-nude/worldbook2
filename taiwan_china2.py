import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
lines=open(INP,encoding='utf-8').read().split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
META['subnat']['CHN']['excludeBBox']=[119.5,21.8,122.5,25.6]
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)
OLD='    if(cfg.exclude) gj.features=gj.features.filter(f=>!cfg.exclude.includes(f.properties[cfg.nameProp]));'
NEW=('    if(cfg.exclude||cfg.excludeBBox){\n'
 '      const _cc=(f)=>{let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;(function w(o){if(typeof o[0]==="number"){if(o[0]<x0)x0=o[0];if(o[0]>x1)x1=o[0];if(o[1]<y0)y0=o[1];if(o[1]>y1)y1=o[1];}else o.forEach(w);})(f.geometry.coordinates);return[(x0+x1)/2,(y0+y1)/2];};\n'
 '      gj.features=gj.features.filter(f=>{\n'
 '        if(cfg.exclude&&cfg.exclude.includes(f.properties[cfg.nameProp])) return false;\n'
 '        if(cfg.excludeBBox){const c=_cc(f),b=cfg.excludeBBox; if(c[0]>=b[0]&&c[0]<=b[2]&&c[1]>=b[1]&&c[1]<=b[3]) return false;}\n'
 '        return true;\n'
 '      });\n'
 '    }')
if 'excludeBBox){const c=_cc' not in text:
    n=text.count(OLD); assert n==1, f"anchor matched {n}x"
    text=text.replace(OLD,NEW)
open(OUT,'w',encoding='utf-8').write(text)
print("OK: Taiwan dropped by geographic bbox")
