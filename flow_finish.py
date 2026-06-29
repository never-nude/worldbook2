import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'flowT0' not in text, 'flow_finish already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,'let FLOWGEO=null;','let FLOWGEO=null; let flowT0=0;','flowt0')
text=patch(text,
'''function startFlowAnim(){
  if(flowAnim) cancelAnimationFrame(flowAnim);
  buildFlowGeo(flowKey);                                   // arc lines built ONCE
  let t0=performance.now(), lastDot=0;
  function step(t){
    if(!flowActive()){ flowAnim=null; return; }
    if(!FLOWGEO || FLOWGEO.key!==flowKey || FLOWGEO.focus!==flowFocusIso) buildFlowGeo(flowKey);  // rebuild only when the edge set changes
    if(t-lastDot>=16){                                     // ~60fps dots — cheap now lines are cached; smooth glide
      const ds=map.getSource("flow-dots"); if(ds) ds.setData(flowDotsFC(((t-t0)/9000)%1));
      lastDot=t;
    }
    flowAnim=requestAnimationFrame(step);
  }
  flowAnim=requestAnimationFrame(step);
}''',
'''function startFlowAnim(){
  if(flowAnim){ cancelAnimationFrame(flowAnim); flowAnim=null; }
  buildFlowGeo(flowKey);                                   // arc lines built ONCE
  flowT0=performance.now();                                // dots are driven by the master frame loop — in lockstep with the globe spin
}''',
'startflowanim')
text=patch(text,'    if(orrOn) drawOrr();\n    requestAnimationFrame(frame);',
'''    if(orrOn) drawOrr();
    if(flowActive()){                                      // dots ride the master loop, perfectly in sync with the globe
      if(!FLOWGEO || FLOWGEO.key!==flowKey || FLOWGEO.focus!==flowFocusIso) buildFlowGeo(flowKey);
      const ds=map.getSource("flow-dots"); if(ds) ds.setData(flowDotsFC(((t-flowT0)/9000)%1));
    }
    requestAnimationFrame(frame);''',
'frameloop')
text=patch(text,
'''      return `<div class="pop-name">${p.name}</div><div class="pop-sub">${v!=null?lab+": $"+v+"B":lab+": none"}</div>`; }
    return `<div class="pop-name">${p.name}</div>`;
  }''',
'''      return `<div class="pop-name">${p.name}</div><div class="pop-sub">${v!=null?lab+": $"+v+"B":lab+": none"}</div>`; }
    if(!F.geo){ const role=rolesFor(c.flowKey, flowIso)[p.iso3];
      return `<div class="pop-name">${p.name}</div><div class="pop-sub">${role?roleLabels(c.flowKey)[role]:"Not in these routes"}</div>`; }
    return `<div class="pop-name">${p.name}</div>`;
  }''',
'hover-roles')
NEW_DEBT=[(1,"#8a4a22"),(8,"#b0481f"),(20,"#d05a2a"),(35,"#e8743f"),(60,"#f6ab78")]
NEW_CRED=[(0.5,"#1f7a6a"),(5,"#2aa18d"),(20,"#43c2ac"),(50,"#6fdcc4"),(120,"#9af0e0"),(220,"#d6fff5")]
def _hx(c):c=c.lstrip('#');return(int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t):return'#%02x%02x%02x'%t
def ramp(v,st):
    if v<=st[0][0]:return st[0][1]
    if v>=st[-1][0]:return st[-1][1]
    for i in range(len(st)-1):
        v0,c0=st[i];v1,c1=st[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0) if v1!=v0 else 0;a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return st[-1][1]
lines=text.split('\n')
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
for f in MAP['features']:
    p=f['properties']
    if p.get('debtorDebt') is not None: p['color_debtorDebt']=ramp(float(p['debtorDebt']),NEW_DEBT)
    if p.get('creditorDebt') is not None: p['color_creditorDebt']=ramp(float(p['creditorDebt']),NEW_CRED)
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'
open(OUT,"w",encoding="utf-8").write('\n'.join(lines))
print("OK: smooth dots + role hover + brighter debt ramps")
