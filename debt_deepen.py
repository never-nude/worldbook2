#!/usr/bin/env python3
"""Deepen the debt story on the baked Atlas index.html:
   - expand FLOWS.debt bilateral arcs (~90 edges, all major lenders)
   - add a 'Govt debt (% GDP)' choropleth (baked per-country color)
   - add DEBT_PROFILE + a creditor-composition bar in the country panel
Run: python3 debt_deepen.py index.html index.html
Idempotent: aborts if already applied."""
import json, sys

INP = sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT = sys.argv[2] if len(sys.argv)>2 else "index.html"

# ----------------------------- DATA -----------------------------
# Government gross debt, % of GDP (~2023-24, IMF WEO / Global Debt Database; approx)
GDEBT = {
'JPN':250,'SDN':256,'LBN':280,'SGP':168,'GRC':162,'ERI':165,'ARG':155,'VEN':150,'ITA':137,
'BHR':130,'ZMB':127,'USA':122,'BTN':121,'MDV':115,'LAO':115,'CPV':113,'BRB':115,'FRA':111,
'ESP':108,'CAN':107,'BEL':106,'LKA':103,'CUB':100,'GBR':101,'PRT':99,'COG':98,'ZWE':98,
'EGY':96,'MOZ':92,'SUR':90,'JOR':89,'UKR':88,'BRA':86,'AGO':85,'SLV':85,'GHA':84,'IND':82,
'CHN':83,'SEN':81,'BOL':80,'TUN':80,'MUS':80,'FJI':80,'YEM':80,'MNG':80,'FIN':76,'AUT':78,
'GNB':78,'PAK':75,'ZAF':74,'GMB':73,'HUN':73,'MWI':71,'RWA':67,'MYS':67,'TGO':67,'BDI':68,
'SVN':69,'KEN':70,'MAR':70,'GAB':70,'CRI':64,'PAN':64,'HRV':63,'URY':63,'DEU':64,'BLZ':64,
'THA':62,'ISL':61,'ISR':60,'SSD':60,'MMR':60,'LSO':60,'PSE':50,'NIC':43,'PHL':57,'ECU':57,
'DOM':60,'CYP':80,'BFA':58,'CIV':58,'SVK':58,'DZA':55,'LBY':55,'LBR':55,'COL':55,'KOR':55,
'NER':51,'MDG':54,'BEN':54,'MLI':52,'HND':51,'PNG':52,'UGA':52,'SRB':52,'MKD':52,'POL':49,
'ROU':49,'AUS':50,'ARM':50,'MLT':50,'NLD':47,'TZA':47,'SLE':47,'KGZ':47,'NZL':46,'NGA':46,
'LVA':45,'IRQ':44,'CZE':44,'TCD':43,'CMR':42,'SWZ':42,'IRL':43,'BLR':42,'QAT':41,'PRY':41,
'NPL':42,'BGD':39,'IDN':39,'CHL':38,'CHE':38,'NOR':38,'ETH':38,'LTU':38,'GEO':39,'NAM':66,
'KHM':36,'OMN':36,'SOM':35,'MDA':35,'UZB':35,'IRN':34,'TUR':34,'PER':34,'GIN':34,'TJK':32,
'SWE':32,'DNK':30,'HTI':30,'BIH':30,'ARE':30,'GTM':30,'GUY':27,'GBR2':0,'GUatemala':0,
'GUY2':0,'BGR':23,'KAZ':24,'SAU':24,'COD':22,'RUS':20,'BWA':19,'EST':19,'XKX':18,'AZE':18,
'LUX':25,'TKM':5,'KWT':3,'AFG':7,'VNM':37,'MEX':53,'ALB':65,'MNE':65,
}
GDEBT.pop('GBR2',None); GDEBT.pop('GUatemala',None); GDEBT.pop('GUY2',None)
DEBT_STOPS=[(0,"#0d2818"),(30,"#1d6b46"),(60,"#c9c24a"),(100,"#e08a3a"),(150,"#c0443a"),(250,"#7a1f2b")]
NODATA="#262f3d"

# Per-country debt profile for the panel. ext = external debt US$bn; gdp = govt debt % GDP;
# cr = creditor composition (% of external debt): china/paris/multi(multilateral)/private/other.
# domestic=True for advanced economies whose debt is mainly market/domestically held.
DPROF = {
'ZMB':{'ext':33,'gdp':127,'cr':{'china':36,'paris':8,'multi':18,'private':28,'other':10}},
'LKA':{'ext':56,'gdp':103,'cr':{'china':20,'paris':12,'multi':22,'private':36,'other':10}},
'PAK':{'ext':130,'gdp':75,'cr':{'china':30,'paris':12,'multi':34,'private':8,'other':16}},
'AGO':{'ext':50,'gdp':85,'cr':{'china':40,'paris':5,'multi':8,'private':40,'other':7}},
'ETH':{'ext':28,'gdp':38,'cr':{'china':36,'paris':8,'multi':40,'private':8,'other':8}},
'KEN':{'ext':38,'gdp':70,'cr':{'china':19,'paris':10,'multi':42,'private':25,'other':4}},
'GHA':{'ext':30,'gdp':84,'cr':{'china':13,'paris':6,'multi':25,'private':50,'other':6}},
'EGY':{'ext':165,'gdp':96,'cr':{'china':8,'paris':14,'multi':30,'private':18,'other':30}},
'NGA':{'ext':42,'gdp':46,'cr':{'china':11,'paris':3,'multi':50,'private':33,'other':3}},
'ARG':{'ext':270,'gdp':155,'cr':{'china':8,'paris':5,'multi':35,'private':45,'other':7}},
'LAO':{'ext':13,'gdp':115,'cr':{'china':50,'paris':5,'multi':20,'private':20,'other':5}},
'MNG':{'ext':33,'gdp':80,'cr':{'china':25,'paris':15,'multi':25,'private':30,'other':5}},
'ECU':{'ext':58,'gdp':57,'cr':{'china':20,'paris':5,'multi':40,'private':30,'other':5}},
'VEN':{'ext':150,'gdp':150,'cr':{'china':18,'paris':5,'multi':5,'private':60,'other':12}},
'MMR':{'ext':13,'gdp':60,'cr':{'china':40,'paris':25,'multi':25,'private':5,'other':5}},
'BGD':{'ext':100,'gdp':39,'cr':{'china':9,'paris':30,'multi':50,'private':6,'other':5}},
'DJI':{'ext':3,'gdp':38,'cr':{'china':43,'paris':10,'multi':35,'private':7,'other':5}},
'MDV':{'ext':8,'gdp':115,'cr':{'china':20,'paris':8,'multi':25,'private':42,'other':5}},
'TJK':{'ext':6,'gdp':32,'cr':{'china':35,'paris':5,'multi':50,'private':5,'other':5}},
'KGZ':{'ext':9,'gdp':47,'cr':{'china':35,'paris':8,'multi':50,'private':2,'other':5}},
'COG':{'ext':5,'gdp':98,'cr':{'china':50,'paris':15,'multi':20,'private':10,'other':5}},
'CMR':{'ext':14,'gdp':42,'cr':{'china':32,'paris':12,'multi':40,'private':11,'other':5}},
'SEN':{'ext':20,'gdp':81,'cr':{'china':18,'paris':18,'multi':30,'private':30,'other':4}},
'CIV':{'ext':30,'gdp':58,'cr':{'china':12,'paris':18,'multi':30,'private':36,'other':4}},
'TZA':{'ext':30,'gdp':47,'cr':{'china':20,'paris':8,'multi':55,'private':12,'other':5}},
'UGA':{'ext':21,'gdp':52,'cr':{'china':20,'paris':6,'multi':55,'private':14,'other':5}},
'SDN':{'ext':56,'gdp':256,'cr':{'china':15,'paris':38,'multi':15,'private':7,'other':25}},
'ZWE':{'ext':18,'gdp':98,'cr':{'china':25,'paris':30,'multi':30,'private':5,'other':10}},
'NPL':{'ext':9,'gdp':42,'cr':{'china':12,'paris':18,'multi':62,'private':3,'other':5}},
'BOL':{'ext':14,'gdp':80,'cr':{'china':22,'paris':8,'multi':55,'private':12,'other':3}},
'GAB':{'ext':7,'gdp':70,'cr':{'china':25,'paris':18,'multi':22,'private':30,'other':5}},
'CRI':{'ext':32,'gdp':64,'cr':{'china':6,'paris':6,'multi':45,'private':40,'other':3}},
'JAM':{'ext':17,'gdp':72,'cr':{'china':10,'paris':8,'multi':45,'private':33,'other':4}},
'IDN':{'ext':410,'gdp':39,'cr':{'china':12,'paris':18,'multi':25,'private':40,'other':5}},
'TUR':{'ext':480,'gdp':34,'cr':{'china':6,'paris':10,'multi':18,'private':60,'other':6}},
'UKR':{'ext':150,'gdp':88,'cr':{'china':2,'paris':25,'multi':45,'private':18,'other':10}},
'SLV':{'ext':20,'gdp':85,'cr':{'china':2,'paris':5,'multi':45,'private':45,'other':3}},
'TUN':{'ext':40,'gdp':80,'cr':{'china':3,'paris':22,'multi':45,'private':25,'other':5}},
'JOR':{'ext':45,'gdp':89,'cr':{'china':3,'paris':12,'multi':35,'private':30,'other':20}},
'JPN':{'gdp':250,'domestic':True},'USA':{'gdp':122,'domestic':True},
'ITA':{'gdp':137,'domestic':True},'GRC':{'gdp':162,'domestic':True},
'FRA':{'gdp':111,'domestic':True},'ESP':{'gdp':108,'domestic':True},
'GBR':{'gdp':101,'domestic':True},'DEU':{'gdp':64,'domestic':True},
'BEL':{'gdp':106,'domestic':True},'PRT':{'gdp':99,'domestic':True},
}

# Expanded bilateral debt arcs: creditor -> debtor, w = US$bn (approx bilateral stock)
DEBT_EDGES = [
 # ---- China (Belt and Road / official + policy-bank lending) ----
 ('CHN','PAK',30),('CHN','AGO',18),('CHN','ARG',18),('CHN','LAO',12),('CHN','VEN',10),
 ('CHN','EGY',8),('CHN','KEN',8),('CHN','IDN',8),('CHN','TKM',8),('CHN','ETH',7),
 ('CHN','LKA',7),('CHN','ZMB',6),('CHN','BGD',6),('CHN','NGA',5),('CHN','ECU',5),
 ('CHN','CMR',5),('CHN','BRA',5),('CHN','ZAF',5),('CHN','KAZ',5),('CHN','KHM',4),
 ('CHN','MMR',4),('CHN','MYS',4),('CHN','UZB',4),('CHN','SDN',3),('CHN','GHA',3),
 ('CHN','COG',3),('CHN','COD',3),('CHN','SRB',3),('CHN','MNG',2),('CHN','TZA',2),
 ('CHN','UGA',2),('CHN','ZWE',2),('CHN','MOZ',2),('CHN','SEN',2),('CHN','PNG',2),
 ('CHN','PER',2),('CHN','BLR',2),('CHN','GIN',2),('CHN','DJI',1.5),('CHN','KGZ',1.8),
 ('CHN','TJK',1.2),('CHN','MDV',1.4),('CHN','BOL',1.5),
 # ---- Japan (largest Paris Club / ODA lender in Asia) ----
 ('JPN','IDN',5),('JPN','IND',6),('JPN','VNM',6),('JPN','PHL',4),('JPN','BGD',4),
 ('JPN','MMR',3),('JPN','IRQ',3),('JPN','KEN',2),('JPN','EGY',2),('JPN','BRA',2),
 # ---- France / Germany / other EU bilateral ----
 ('FRA','MAR',3),('FRA','CIV',3),('FRA','SEN',2),('FRA','CMR',2),('FRA','TUN',2),
 ('DEU','TUR',3),('DEU','EGY',2),('DEU','IND',2),
 # ---- United States / UK ----
 ('USA','UKR',8),('USA','EGY',3),('USA','PAK',3),('USA','JOR',2),('USA','IRQ',2),
 ('GBR','PAK',2),('GBR','NGA',1),('GBR','KEN',1),
 # ---- Gulf states (G20 Common Framework creditors) ----
 ('SAU','PAK',5),('SAU','EGY',5),('SAU','YEM',3),('SAU','SDN',2),('SAU','BHR',5),
 ('ARE','EGY',5),('ARE','PAK',3),('ARE','ETH',1),('ARE','SDN',1),
 ('QAT','EGY',3),('QAT','TUR',3),('KWT','EGY',2),('KWT','PAK',2),
 # ---- India (lines of credit to neighbours & Africa) ----
 ('IND','LKA',4),('IND','BGD',2),('IND','NPL',1),('IND','MMR',1),('IND','MUS',1),
 # ---- Russia (energy & nuclear loans) ----
 ('RUS','BGD',11),('RUS','EGY',25),('RUS','BLR',8),('RUS','VEN',3),('RUS','IND',2),
 # ---- South Korea ----
 ('KOR','VNM',2),('KOR','IDN',1),
]

# --------------------------- helpers ---------------------------
def _hx(c): c=c.lstrip('#'); return (int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t): return '#%02x%02x%02x'%t
def ramp(v,st):
    if v is None: return NODATA
    if v<=st[0][0]: return st[0][1]
    if v>=st[-1][0]: return st[-1][1]
    for i in range(len(st)-1):
        v0,c0=st[i]; v1,c1=st[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0) if v1!=v0 else 0; a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return st[-1][1]
def patch(text,a,b,label):
    n=text.count(a); assert n==1, f"anchor {label}: found {n}, need 1"
    return text.replace(a,b)

# --------------------------- load ---------------------------
lines=open(INP,encoding='utf-8').read().split('\n')
assert 'color_govdebt' not in '\n'.join(lines[:300]), 'Already applied - aborting.'
mi=next(i for i,l in enumerate(lines) if l.startswith('const MAPDATA = '))
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))

# bake choropleth into MAPDATA
MAP=json.loads(lines[mi][len('const MAPDATA = '):].rstrip().rstrip(';'))
nb=0
for f in MAP['features']:
    p=f['properties']; iso=p.get('iso3')
    if iso and iso in GDEBT:
        p['debtGdp']=GDEBT[iso]; p['color_govdebt']=ramp(GDEBT[iso],DEBT_STOPS); nb+=1
lines[mi]='const MAPDATA = '+json.dumps(MAP,separators=(',',':'))+';'

# add META choropleth layer after 'internet'
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
cfg={'group':'People & economy','key':'govdebt','label':'Govt debt (% GDP)','type':'numeric',
     'prop':'debtGdp','short':'Debt / GDP','fmtType':'pct','unit':'% of GDP (gross general govt)',
     'stops':[{'v':v,'color':c} for v,c in DEBT_STOPS]}
ii=next(i for i,l in enumerate(L) if l.get('key')=='internet')
L[ii+1:ii+1]=[cfg]
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'

text='\n'.join(lines)

# replace FLOWS.debt edges (span between unique anchors, inclusive)
S='{from:"CHN",to:"PAK",w:30}'; E='{from:"KOR",to:"VNM",w:2}'
i0=text.index(S); i1=text.index(E,i0)+len(E)
new_edges=',\n'.join('      '+','.join(f'{{from:"{a}",to:"{b}",w:{w}}}' for a,b,w in DEBT_EDGES[k:k+3])
                     for k in range(0,len(DEBT_EDGES),3))
text=text[:i0]+new_edges.strip()+text[i1:]

# DEBT_PROFILE + creditorBar + CSS, injected before openCountry
dprof_js='const DEBT_PROFILE = '+json.dumps(DPROF,separators=(',',':'))+';\n'
bar_js='''function creditorBar(cr){
  const defs=[["China","china","#e0603a"],["Paris Club","paris","#5b8def"],["Multilateral","multi","#56c5d0"],["Private bondholders","private","#d4b13a"],["Other / Gulf","other","#9aa6b6"]];
  let bar='<div class="dbar">',leg='<div class="dleg">';
  defs.forEach(function(d){var v=cr[d[1]]||0; if(v>0){bar+='<span style="width:'+v+'%;background:'+d[2]+'"></span>'; leg+='<span><i style="background:'+d[2]+'"></i>'+d[0]+' '+v+'%</span>';}});
  return '<div class="note" style="margin-top:7px">Creditor composition (share of external debt):</div>'+bar+'</div>'+leg+'</div>';
}
'''
text=patch(text,'function openCountry(p){', dprof_js+bar_js+'function openCountry(p){','inject-debt-fns')

# panel section after the "At a glance" block
anchor='''  if(p.internet) h+=`<div class="stat"><span class="k">Internet users</span><span class="v">${fmt.dec1(p.internet)}%</span></div>`;
  h+=`</div>`;'''
debt_sec=anchor+'''
  if((typeof DEBT_PROFILE!=="undefined" && DEBT_PROFILE[p.iso3]) || p.debtGdp!=null){
    const dp=(typeof DEBT_PROFILE!=="undefined" && DEBT_PROFILE[p.iso3])||{};
    const g=(dp.gdp!=null)?dp.gdp:p.debtGdp;
    h+=`<div class="sec"><h4>Debt</h4>`;
    if(g!=null) h+=`<div class="stat"><span class="k">Govt debt</span><span class="v">≈ ${g}% of GDP</span></div>`;
    if(dp.ext!=null) h+=`<div class="stat"><span class="k">External debt</span><span class="v">≈ $${dp.ext}B</span></div>`;
    if(dp.cr) h+=creditorBar(dp.cr);
    else if(dp.domestic) h+=`<div class="note" style="margin-top:6px">Predominantly domestic / market-held debt — not bilateral.</div>`;
    h+=`</div>`;
  }'''
text=patch(text,anchor,debt_sec,'inject-debt-panel')

# CSS for the bar, appended into the existing <style> (after .pill rule if present, else before </style>)
css='''  .dbar{display:flex;height:13px;border-radius:4px;overflow:hidden;margin:7px 0 6px;border:1px solid var(--line)}
  .dbar span{display:block;height:100%}
  .dleg{display:flex;flex-wrap:wrap;gap:9px;font-size:11px;color:var(--muted)}
  .dleg i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:4px;vertical-align:middle}
'''
text=patch(text,'</style>',css+'</style>','inject-css')

open(OUT,'w',encoding='utf-8').write(text)
print(f"OK: choropleth baked for {nb} countries; debt edges={len(DEBT_EDGES)}; DEBT_PROFILE={len(DPROF)}")
print("layers:", [l.get('key') for l in META['layers']])
