import json, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'debtout:' not in text, 'follow-the-money debt already applied - aborting.'
def patch(t,a,b,l):
    n=t.count(a); assert n==1, f"anchor {l}: {n} matches"; return t.replace(a,b)
text=patch(text,
  '  const F=FLOWS[key]; const lines=[], items=[]; let wmax=0;\n  F.edges.forEach(e=>{ if(e.w>wmax) wmax=e.w; });',
  '  const F=FLOWS[key]; const edges=F.edges||(F.edgesRef?FLOWS[F.edgesRef].edges:[]); const lines=[], items=[]; let wmax=0;\n  edges.forEach(e=>{ if(e.w>wmax) wmax=e.w; });',
  'bfg-edges')
text=patch(text,
  '  F.edges.forEach((e,i)=>{\n    if(flowFocusIso && e.from && e.to && e.from!==flowFocusIso && e.to!==flowFocusIso) return;',
  '  edges.forEach((e,i)=>{\n    if(flowFocusIso && e.from && e.to){ if(F.dir==="out"){ if(e.from!==flowFocusIso) return; } else if(F.dir==="in"){ if(e.to!==flowFocusIso) return; } else if(e.from!==flowFocusIso && e.to!==flowFocusIso) return; }',
  'bfg-dir')
text=patch(text,
  '  const F=FLOWS[key]; const froms=new Set(), tos=new Set();\n  F.edges.forEach(e=>{ if(isoColor',
  '  const F=FLOWS[key]; const edges=F.edges||(F.edgesRef?FLOWS[F.edgesRef].edges:[]); const froms=new Set(), tos=new Set();\n  edges.forEach(e=>{ if(isoColor',
  'roles-edges')
text=patch(text,
  '  if(FLOWS[key]&&FLOWS[key].geo){ map.setPaintProperty("fills","fill-color","#162130"); map.setPaintProperty("fills","fill-opacity",0.72); return; }',
  '  if(FLOWS[key]&&FLOWS[key].geo){ map.setPaintProperty("fills","fill-color","#162130"); map.setPaintProperty("fills","fill-opacity",0.72); return; }\n  if(FLOWS[key]&&FLOWS[key].baseColorProp){ map.setPaintProperty("fills","fill-color",["coalesce",["get",FLOWS[key].baseColorProp],"#1a2433"]); map.setPaintProperty("fills","fill-opacity",0.92); return; }',
  'base-prop')
text=patch(text,'  if(!F.geo){ const RL=roleLabels(key);','  if(!F.geo && !F.baseColorProp){ const RL=roleLabels(key);','legend-skip')
FLOWS_JS='''  debtout: {
    label: "Debt — money lent out", group: "Debt", edgesRef: "debt", dir: "out",
    color: "#5bd6c0", dotColor: "#d6fff5", baseColorProp: "color_creditorDebt",
    unit: "US$ billions of bilateral lending",
    desc: "Follow the money OUT — each arc is a loan a government has made; dots travel from lender toward borrower. Countries are shaded teal by how much they lend.",
    legend: "Teal arcs = money flowing OUT from lenders (dots move lender to borrower). Country shade = total lent (brighter = bigger lender). Click a country to isolate just the money IT lends out.",
    note: "Same bilateral-debt data as 'money owed', from the lender's side. Approximate — World Bank IDS / AidData; Chinese lending dominates.",
    sources: [{label:"World Bank — International Debt Statistics", url:"https://www.worldbank.org/en/programs/debt-statistics/ids"},{label:"AidData — Chinese overseas development finance", url:"https://www.aiddata.org/china-official-finance"}]
  },
  debtin: {
    label: "Debt — money owed", group: "Debt", edgesRef: "debt", dir: "in",
    color: "#e0603a", dotColor: "#ffd9c4", baseColorProp: "color_debtorDebt",
    unit: "US$ billions of bilateral debt owed",
    desc: "Follow the money IN — each arc is debt a government owes; dots travel from lender toward borrower. Countries are shaded orange by how much they owe.",
    legend: "Orange arcs = money owed, arriving at borrowers (dots move lender to borrower). Country shade = total owed (brighter = deeper in debt). Click a country to isolate just where ITS debt comes from.",
    note: "Same bilateral-debt data as 'money lent out', from the borrower's side. Approximate — World Bank IDS / AidData.",
    sources: [{label:"World Bank — International Debt Statistics", url:"https://www.worldbank.org/en/programs/debt-statistics/ids"},{label:"AidData — Chinese overseas development finance", url:"https://www.aiddata.org/china-official-finance"}]
  },
'''
text=patch(text,'const FLOWS = {','const FLOWS = {\n'+FLOWS_JS,'flows-insert')
lines=text.split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
di=next(i for i,l in enumerate(L) if l.get('key')=='flow_debt')
L[di:di+1]=[
  {"group":"Debt","key":"flow_debtout","label":"Debt — money lent out","type":"flow","flowKey":"debtout"},
  {"group":"Debt","key":"flow_debtin","label":"Debt — money owed","type":"flow","flowKey":"debtin"},
]
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)
open(OUT,'w',encoding='utf-8').write(text)
print("OK: directional debt maps")
