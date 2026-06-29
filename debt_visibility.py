import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'c.type==="flow"' not in text.split("function hoverHTML")[1][:400], 'debt_visibility already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,
  '  if(FLOWS[key]&&FLOWS[key].baseColorProp){ map.setPaintProperty("fills","fill-color",["coalesce",["get",FLOWS[key].baseColorProp],"#1a2433"]); map.setPaintProperty("fills","fill-opacity",0.92); return; }',
  '  if(FLOWS[key]&&FLOWS[key].baseColorProp){ map.setPaintProperty("fills","fill-color",["coalesce",["get",FLOWS[key].baseColorProp],"#3b4655"]); map.setPaintProperty("fills","fill-opacity",0.92); return; }',
  'base-fallback')
text=patch(text,
'''function hoverHTML(p,isSub){
  const c=layerCfg(activeLayer);
  if(c.type==="raster") return `<div class="pop-name">${p.name}</div>`;
  const val = c.type==="categorical" ? (p[c.prop]||"No data") : labelFor(c,p[c.prop]);
  return `<div class="pop-name">${p.name}</div><div class="pop-sub">${c.short}: ${val}</div>`;
}''',
'''function hoverHTML(p,isSub){
  const c=layerCfg(activeLayer);
  if(c.type==="raster") return `<div class="pop-name">${p.name}</div>`;
  if(c.type==="flow"){
    const F=FLOWS[c.flowKey]||{};
    if(F.baseColorProp){ const v=p[F.baseColorProp.replace("color_","")];
      const lab=F.dir==="in"?"Owes bilaterally":"Lends bilaterally";
      return `<div class="pop-name">${p.name}</div><div class="pop-sub">${v!=null?lab+": $"+v+"B":lab+": none"}</div>`; }
    return `<div class="pop-name">${p.name}</div>`;
  }
  const val = c.type==="categorical" ? (p[c.prop]||"No data") : labelFor(c,p[c.prop]);
  return `<div class="pop-name">${p.name}</div><div class="pop-sub">${c.short}: ${val}</div>`;
}''',
'hover-flow')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: visible land fallback + flow-aware hover")
