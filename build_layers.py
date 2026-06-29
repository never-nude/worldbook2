#!/usr/bin/env python3
"""Bake 5 new layers into Atlas index.html:
   1. CO2 per capita (numeric)   2. Koppen climate (categorical)
   3. UTC offset (numeric)       4. Remittance corridors (flow)
   5. Bilateral debt (two-tone flow)  + click-to-isolate interaction.
Idempotent-ish: aborts if markers already present."""
import json, sys, re

INP = sys.argv[1] if len(sys.argv) > 1 else "/tmp/atlas/index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/atlas/index.new.html"

# ---------------------------------------------------------------- DATA TABLES
CO2 = {  # tonnes CO2 / person / yr, ~2023, OWID / Global Carbon Project (approx)
'QAT':35,'BHR':25,'KWT':25,'ARE':22,'BRN':23,'TTO':22,'SAU':18,'OMN':15,'KAZ':14,'AUS':15,
'USA':14.3,'CAN':14,'TKM':13,'LUX':13,'KOR':11.6,'RUS':11.4,'MNG':11,'TWN':11,'SGP':8.9,'JPN':8.5,
'CZE':9,'ISL':9,'LBY':9,'CHN':8.0,'POL':8,'EST':8,'IRN':8,'MYS':8,'DEU':7.5,'NLD':7.5,
'BEL':7.5,'NOR':7,'IRL':7,'ZAF':7,'FIN':6.5,'AUT':6.7,'NZL':6.3,'BIH':6,'ISR':6,'BLR':6,
'SVN':6,'BGR':5.8,'SRB':5.7,'CYP':5.7,'GRC':5.5,'ITA':5.5,'SVK':5.5,'BHS':5.5,'TUR':5.3,'ESP':5,
'HKG':5,'MAC':5,'GNQ':4,'XKX':5,'SYC':5,'AND':5,'KNA':5,'GAB':2.5,'PRT':4,'DNK':4.5,
'CHL':4.3,'HUN':4.3,'HRV':4.3,'IRQ':4.4,'LTU':4.5,'CHE':4,'FRA':4.2,'GBR':4.7,'BRB':4,'LIE':4,
'MCO':4,'SMR':4,'NRU':4,'GUY':4,'UKR':4,'AZE':3.4,'THA':3.8,'VEN':3.5,'VNM':3.5,'DZA':4,
'UZB':3.5,'LVA':3.5,'MKD':3.5,'MNE':3.5,'SUR':3.5,'MDV':3.5,'MHL':3,'MLT':3,'MUS':3,'LBN':3,
'ROU':3.7,'ARG':3.7,'MEX':3.6,'SWE':3.6,'EGY':2.3,'IDN':2.6,'JAM':2.6,'LAO':2.7,'TUN':2.7,'GEO':2.7,
'BWA':2.7,'PAN':2.5,'MDA':2.5,'CUB':2.3,'JOR':2.3,'ECU':2.3,'ARM':2.3,'LCA':2.3,'DOM':2.4,'BRA':2.2,
'IND':2.0,'URY':2.0,'VCT':2,'DMA':2,'PRK':1.8,'PER':1.8,'BOL':1.8,'MAR':1.8,'ALB':1.7,'NAM':1.6,
'COL':1.6,'CRI':1.6,'BLZ':1.6,'GRD':2.5,'PRY':1.3,'PHL':1.3,'GTM':1.2,'SLV':1.2,'KHM':1.2,'WSM':1.3,
'LSO':1.3,'FSM':1.4,'SYR':1.5,'KGZ':1.5,'BTN':1.5,'FJI':1.5,'HND':1.0,'PAK':1.0,'LKA':1.0,'CPV':1.0,
'COG':1.0,'SWZ':1.0,'TUV':1,'NIC':0.8,'ZWE':0.8,'PNG':0.8,'MMR':0.7,'MRT':0.7,'GHA':0.6,'BGD':0.6,
'NGA':0.6,'BEN':0.6,'NPL':0.6,'SEN':0.6,'PSE':0.6,'KIR':0.6,'STP':0.6,'VUT':0.6,'KEN':0.4,'ZMB':0.4,
'CMR':0.4,'CIV':0.4,'TGO':0.4,'SLB':0.4,'YEM':0.4,'DJI':0.5,'AGO':0.5,'SDN':0.5,'GIN':0.3,'MLI':0.3,
'GMB':0.3,'COM':0.3,'AFG':0.3,'TZA':0.2,'MOZ':0.2,'BFA':0.2,'LBR':0.2,'GNB':0.2,'ERI':0.2,'MDG':0.15,
'ETH':0.15,'RWA':0.1,'MWI':0.1,'SLE':0.1,'TCD':0.1,'NER':0.1,'SSD':0.1,'SOM':0.1,'UGA':0.13,'COD':0.04,
'CAF':0.04,'NCL':20,'FRO':12,'PLW':12,'GRL':9,'BMU':9,'ABW':8,'CUW':10,'ATG':6,'TLS':0.4,
}

# Koppen dominant group per country
_TROP = "BRA IDN NGA COD COL VEN PHL MYS THA VNM KHM MMR BGD LKA SGP BRN PAN CRI NIC HND GTM SLV BLZ CUB DOM HTI JAM TTO BRB GRD LCA VCT DMA ATG KNA BHS GHA CIV CMR GAB COG CAF SSD GNQ LBR SLE GIN GNB GMB BEN TGO UGA TZA KEN AGO MOZ MDG MWI ZMB RWA BDI STP COM ECU GUY SUR PNG FJI SLB VUT TLS MDV KIR TUV NRU WSM TON FSM MHL PLW PRI VIR GUM ASM ABW CUW SXM CPV NCL PYF COK NIU BLM MAF AIA VGB CYM TCA MSR IND SEN".split()
_ARID = "SAU ARE QAT KWT OMN BHR YEM EGY LBY DZA TUN MAR ESH MRT MLI NER TCD SDN SOM DJI ERI NAM BWA IRN IRQ JOR ISR PSE SYR AFG PAK TKM UZB KAZ MNG AUS".split()
_TEMP = "USA GBR FRA DEU ESP ITA PRT IRL NLD BEL CHE AUT DNK GRC TUR MEX ARG CHL URY ZAF NZL JPN KOR CHN GEO AZE HRV SVN SRB BIH MNE MKD BGR ALB CYP MLT LUX MCO AND SMR LIE HKG MAC TWN PRY".split()
_CONT = "RUS CAN SWE FIN NOR POL CZE SVK HUN ROU UKR BLR EST LVA LTU MDA PRK".split()
_POLAR = "GRL ISL".split()
_HIGH = "NPL BTN BOL TJK KGZ LSO ARM ETH".split()
CLIM = {}
for g, lst in [("Tropical",_TROP),("Arid / Desert",_ARID),("Temperate",_TEMP),
               ("Continental",_CONT),("Polar / Tundra",_POLAR),("Highland",_HIGH)]:
    for c in lst: CLIM[c] = g

UTC = {  # standard offset at capital, hours from UTC
'USA':-5,'CAN':-5,'MEX':-6,'GTM':-6,'BLZ':-6,'SLV':-6,'HND':-6,'NIC':-6,'CRI':-6,'PAN':-5,
'COL':-5,'ECU':-5,'PER':-5,'CHL':-4,'ARG':-3,'URY':-3,'PRY':-4,'BOL':-4,'BRA':-3,'VEN':-4,
'GUY':-4,'SUR':-3,'BHS':-5,'CUB':-5,'JAM':-5,'HTI':-5,'DOM':-4,'PRI':-4,'TTO':-4,'BRB':-4,
'GRD':-4,'LCA':-4,'VCT':-4,'DMA':-4,'ATG':-4,'KNA':-4,'ABW':-4,'CUW':-4,'SXM':-4,'AIA':-4,
'VGB':-4,'MSR':-4,'BMU':-4,'BLM':-4,'MAF':-4,'CYM':-5,'TCA':-5,'GRL':-2,'ISL':0,'GBR':0,
'IRL':0,'PRT':0,'ESP':1,'FRA':1,'DEU':1,'ITA':1,'NLD':1,'BEL':1,'CHE':1,'AUT':1,
'DNK':1,'NOR':1,'SWE':1,'POL':1,'CZE':1,'SVK':1,'HUN':1,'HRV':1,'SVN':1,'SRB':1,
'BIH':1,'MNE':1,'MKD':1,'ALB':1,'LUX':1,'MLT':1,'MCO':1,'AND':1,'SMR':1,'LIE':1,
'GRC':2,'FIN':2,'EST':2,'LVA':2,'LTU':2,'UKR':2,'ROU':2,'BGR':2,'MDA':2,'CYP':2,
'ISR':2,'PSE':2,'LBN':2,'EGY':2,'LBY':2,'SDN':2,'SSD':2,'ZAF':2,'BWA':2,'ZWE':2,
'ZMB':2,'MWI':2,'MOZ':2,'RWA':2,'BDI':2,'NAM':2,'BLR':3,'RUS':3,'TUR':3,'JOR':3,
'SYR':3,'IRQ':3,'SAU':3,'KWT':3,'QAT':3,'BHR':3,'YEM':3,'KEN':3,'ETH':3,'SOM':3,
'DJI':3,'ERI':3,'TZA':3,'UGA':3,'MDG':3,'COM':3,'IRN':3.5,'AFG':4.5,'ARM':4,'AZE':4,
'GEO':4,'ARE':4,'OMN':4,'MUS':4,'SYC':4,'PAK':5,'TKM':5,'UZB':5,'TJK':5,'KAZ':5,
'MDV':5,'IND':5.5,'LKA':5.5,'NPL':5.75,'BTN':6,'BGD':6,'KGZ':6,'MMR':6.5,'THA':7,'VNM':7,
'KHM':7,'LAO':7,'IDN':7,'MYS':8,'SGP':8,'PHL':8,'CHN':8,'HKG':8,'MAC':8,'TWN':8,
'MNG':8,'BRN':8,'PRK':9,'KOR':9,'JPN':9,'TLS':9,'AUS':10,'PNG':10,'GUM':10,'FSM':11,
'SLB':11,'VUT':11,'NCL':11,'FJI':12,'NZL':12,'KIR':12,'TUV':12,'MHL':12,'NRU':12,'TON':13,
'WSM':13,'COK':-10,'PYF':-10,'NIU':-11,'ASM':-11,'CPV':-1,'MRT':0,'MLI':0,'SEN':0,'GMB':0,
'GIN':0,'GNB':0,'SLE':0,'LBR':0,'CIV':0,'GHA':0,'BFA':0,'TGO':0,'STP':0,'ESH':1,
'MAR':1,'DZA':1,'TUN':1,'NGA':1,'NER':1,'TCD':1,'CMR':1,'GAB':1,'COG':1,'AGO':1,
'CAF':1,'COD':1,'BEN':1,'FRO':0,
}

# ----- numeric stops (value, hex) -----
CO2_STOPS  = [(0.1,"#0d3320"),(1,"#1d6b46"),(3,"#5aa75a"),(6,"#c9c24a"),(12,"#e08a3a"),(25,"#a83232")]
UTC_STOPS  = [(-10,"#3b2f6b"),(-6,"#3f6fb0"),(-3,"#56c5d0"),(0,"#2a9d6f"),(3,"#d8c84a"),(6,"#e8893c"),(9,"#c95f6e"),(12,"#9b3b8a")]
CLIM_COL = {"Tropical":"#2a9d6f","Arid / Desert":"#e0a93a","Temperate":"#6ea8fe",
            "Continental":"#9b7fe0","Polar / Tundra":"#cfe2ff","Highland":"#b5895f"}
NODATA = "#262f3d"

def _hex(c): c=c.lstrip("#"); return (int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t): return "#%02x%02x%02x"%t
def ramp(v, stops):
    if v is None: return NODATA
    if v <= stops[0][0]: return stops[0][1]
    if v >= stops[-1][0]: return stops[-1][1]
    for i in range(len(stops)-1):
        v0,c0 = stops[i]; v1,c1 = stops[i+1]
        if v0 <= v <= v1:
            f = (v-v0)/(v1-v0) if v1!=v0 else 0
            a,b = _hex(c0),_hex(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return stops[-1][1]

# ---------------------------------------------------------------- LOAD FILE
lines = open(INP, encoding="utf-8").read().split("\n")
assert "color_co2pc" not in "\n".join(lines[:300]), "Already baked - aborting."

mi = next(i for i,l in enumerate(lines) if l.startswith("const MAPDATA = "))
me = next(i for i,l in enumerate(lines) if l.startswith("const META = "))

# ----- patch MAPDATA features -----
md_raw = lines[mi][len("const MAPDATA = "):].rstrip()
if md_raw.endswith(";"): md_raw = md_raw[:-1]
MAP = json.loads(md_raw)
nfeat=0
for f in MAP["features"]:
    p = f["properties"]; iso = p.get("iso3")
    if not iso: continue
    if iso in CO2:
        p["co2pc"]=CO2[iso]; p["color_co2pc"]=ramp(CO2[iso],CO2_STOPS)
    if iso in CLIM:
        p["climateLabel"]=CLIM[iso]; p["color_climate"]=CLIM_COL[CLIM[iso]]
    nfeat+=1
lines[mi] = "const MAPDATA = " + json.dumps(MAP, separators=(",",":")) + ";"

# ----- patch META.layers -----
mt_raw = lines[me][len("const META = "):].rstrip()
if mt_raw.endswith(";"): mt_raw = mt_raw[:-1]
META = json.loads(mt_raw)
L = META["layers"]
co2_cfg = {"group":"Environment","key":"co2pc","label":"CO₂ per capita","type":"numeric",
  "prop":"co2pc","short":"CO₂ / person","fmtType":"dec1","unit":"tonnes CO₂ / person / yr",
  "stops":[{"v":v,"color":c} for v,c in CO2_STOPS]}
clim_cfg = {"group":"Environment","key":"climate","label":"Climate (Köppen)","type":"categorical",
  "prop":"climateLabel","short":"Climate zone",
  "legend":[{"label":k,"color":CLIM_COL[k]} for k in ["Tropical","Arid / Desert","Temperate","Continental","Polar / Tundra","Highland"]]}
remit_cfg = {"group":"Connections","key":"flow_remit","label":"Remittance corridors","type":"flow","flowKey":"remittances"}
debt_cfg  = {"group":"Connections","key":"flow_debt","label":"Bilateral debt","type":"flow","flowKey":"debt"}
# insert env layers after "internet"; flow layers after "flow_arms"
ii = next(i for i,l in enumerate(L) if l.get("key")=="internet")
L[ii+1:ii+1] = [co2_cfg, clim_cfg]
ia = next(i for i,l in enumerate(L) if l.get("key")=="flow_arms")
L[ia+1:ia+1] = [remit_cfg, debt_cfg]
lines[me] = "const META = " + json.dumps(META, separators=(",",":")) + ";"

text = "\n".join(lines)

# ---------------------------------------------------------------- JS PATCHES
def patch(text, anchor, new, label):
    assert text.count(anchor)==1, f"anchor not unique ({text.count(anchor)}) for {label}"
    return text.replace(anchor, new)

# (b) new FLOWS datasets (remittances + two-tone debt) right after `const FLOWS = {`
FLOW_JS = r'''const FLOWS = {
  remittances: {
    label: "Remittance corridors",
    group: "Connections",
    unit: "US$ billions / yr (approx, World Bank bilateral matrix)",
    desc: "Money sent home by migrant workers — largest country-to-country remittance corridors. Arrow points to the receiving country.",
    color: "#7ee0b8", dotColor:"#d6fff0",
    legend: "Each arc is a major remittance corridor; thickness ≈ annual US$ sent. Arrow / dots point to the receiving country.",
    note: "Top corridors estimated from the World Bank Bilateral Remittance Matrix (2023) and KNOMAD. Figures are approximate and rounded; many smaller corridors are omitted.",
    sources: [
      {label:"World Bank — Bilateral Remittance Matrix / KNOMAD", url:"https://www.knomad.org/data/remittances"},
      {label:"World Bank — Migration & Development Brief 39 (2023)", url:"https://www.worldbank.org/en/news/press-release/2023/12/18/remittance-flows-grow-2023-slower-pace-migration-development-brief"}
    ],
    edges: [
      {from:"USA",to:"MEX",w:65},{from:"USA",to:"IND",w:32},{from:"ARE",to:"IND",w:18},
      {from:"USA",to:"GTM",w:18},{from:"USA",to:"CHN",w:18},{from:"USA",to:"PHL",w:14},
      {from:"SAU",to:"IND",w:12},{from:"ARE",to:"PAK",w:10},{from:"USA",to:"VNM",w:10},
      {from:"USA",to:"DOM",w:9},{from:"USA",to:"COL",w:9},{from:"RUS",to:"UZB",w:8},
      {from:"SAU",to:"EGY",w:8},{from:"USA",to:"SLV",w:8},{from:"USA",to:"HND",w:8},
      {from:"SAU",to:"PAK",w:7},{from:"USA",to:"NGA",w:6},{from:"GBR",to:"IND",w:5},
      {from:"MYS",to:"IDN",w:5},{from:"FRA",to:"MAR",w:5},{from:"KWT",to:"IND",w:5},
      {from:"ARE",to:"EGY",w:5},{from:"RUS",to:"TJK",w:5},{from:"USA",to:"HTI",w:4},
      {from:"USA",to:"ECU",w:4},{from:"CAN",to:"IND",w:4},{from:"GBR",to:"NGA",w:4},
      {from:"QAT",to:"IND",w:4},{from:"DEU",to:"TUR",w:3},{from:"ITA",to:"ROU",w:3},
      {from:"ESP",to:"MAR",w:3},{from:"USA",to:"JAM",w:3},{from:"USA",to:"PER",w:3},
      {from:"ARE",to:"PHL",w:3},{from:"RUS",to:"KGZ",w:3},{from:"USA",to:"BRA",w:3}
    ]
  },
  debt: {
    label: "Bilateral debt (creditor → debtor)",
    group: "Connections",
    twoTone: true, fromColor: "#5bd6c0", toColor: "#e0603a",
    unit: "US$ billions of bilateral debt stock (approx)",
    desc: "Government-to-government lending: who owes whom. The teal end of each line is the creditor; the orange end is the debtor. Dots travel creditor → debtor.",
    color: "#5bd6c0", dotColor:"#e0603a",
    legend: "Each line is a major bilateral lending relationship. Teal end = creditor (lender); orange end = debtor (borrower). Dots move from creditor toward debtor.",
    note: "Approximate bilateral debt-stock figures from World Bank International Debt Statistics and AidData. Bilateral (government-to-government) debt is only part of total external debt — much is owed to bondholders and multilaterals (IMF/World Bank). Chinese lending is estimated and often under-reported.",
    cats: [
      {label:"Creditor (lender)", color:"#5bd6c0"},
      {label:"Debtor (borrower)", color:"#e0603a"}
    ],
    sources: [
      {label:"World Bank — International Debt Statistics", url:"https://www.worldbank.org/en/programs/debt-statistics/ids"},
      {label:"AidData — Chinese overseas development finance", url:"https://www.aiddata.org/china-official-finance"}
    ],
    edges: [
      {from:"CHN",to:"PAK",w:30},{from:"CHN",to:"AGO",w:18},{from:"CHN",to:"ARG",w:18},
      {from:"CHN",to:"LAO",w:12},{from:"CHN",to:"VEN",w:10},{from:"CHN",to:"EGY",w:8},
      {from:"CHN",to:"KEN",w:8},{from:"CHN",to:"IDN",w:8},{from:"CHN",to:"ETH",w:7},
      {from:"CHN",to:"LKA",w:7},{from:"CHN",to:"ZMB",w:6},{from:"CHN",to:"BGD",w:6},
      {from:"CHN",to:"NGA",w:5},{from:"CHN",to:"ECU",w:5},{from:"CHN",to:"CMR",w:5},
      {from:"CHN",to:"BRA",w:5},{from:"CHN",to:"KHM",w:4},{from:"CHN",to:"MMR",w:4},
      {from:"CHN",to:"MYS",w:4},{from:"CHN",to:"SDN",w:3},{from:"CHN",to:"GHA",w:3},
      {from:"CHN",to:"COG",w:3},{from:"CHN",to:"MNG",w:2},{from:"CHN",to:"TZA",w:2},
      {from:"CHN",to:"UGA",w:2},{from:"CHN",to:"ZWE",w:2},{from:"CHN",to:"DJI",w:1.5},
      {from:"CHN",to:"MDV",w:1.4},{from:"CHN",to:"KGZ",w:1.8},{from:"CHN",to:"TJK",w:1.2},
      {from:"JPN",to:"IDN",w:5},{from:"JPN",to:"IND",w:5},{from:"JPN",to:"VNM",w:6},
      {from:"JPN",to:"PHL",w:4},{from:"JPN",to:"BGD",w:4},{from:"JPN",to:"MMR",w:3},
      {from:"FRA",to:"MAR",w:3},{from:"FRA",to:"CIV",w:3},{from:"FRA",to:"SEN",w:2},
      {from:"DEU",to:"TUR",w:3},{from:"USA",to:"UKR",w:8},{from:"USA",to:"EGY",w:3},
      {from:"USA",to:"PAK",w:3},{from:"USA",to:"JOR",w:2},{from:"SAU",to:"PAK",w:5},
      {from:"SAU",to:"EGY",w:5},{from:"ARE",to:"EGY",w:5},{from:"RUS",to:"BLR",w:8},
      {from:"IND",to:"LKA",w:4},{from:"IND",to:"BGD",w:2},{from:"KOR",to:"VNM",w:2}
    ]
  },'''
text = patch(text, "const FLOWS = {", FLOW_JS, "flows-insert")

# (c) two-tone aware line/dot building in flowFeatureCollection
OLD_FC = '''    const col = e.c || F.color;                         // per-edge color, else dataset color
    const dotCol = e.dc || F.dotColor || "#cfe2ff";
    lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:col},
      geometry:{type:"LineString",coordinates:pts}});
    // travelling particles ride the great circle; phase animates them
    const nDots = 1 + Math.round((e.w/wmax)*2);
    for(let d=0; d<nDots; d++){
      const f=( phase + d/nDots + i*0.013 ) % 1;
      const idx=Math.min(pts.length-1, Math.floor(f*pts.length));
      dots.push({type:"Feature",properties:{w:e.w/wmax,c:dotCol},
        geometry:{type:"Point",coordinates:pts[idx]}});
    }'''
NEW_FC = '''    const col = e.c || F.color;                         // per-edge color, else dataset color
    const dotCol = e.dc || F.dotColor || "#cfe2ff";
    const two = F.twoTone;
    if(two){
      const mid=Math.floor(pts.length/2);
      lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:F.fromColor},
        geometry:{type:"LineString",coordinates:pts.slice(0,mid+1)}});
      lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:F.toColor},
        geometry:{type:"LineString",coordinates:pts.slice(mid)}});
    } else {
      lines.push({type:"Feature",properties:{w:e.w/wmax,from:e.from,to:e.to,c:col},
        geometry:{type:"LineString",coordinates:pts}});
    }
    // travelling particles ride the great circle; phase animates them
    const nDots = 1 + Math.round((e.w/wmax)*2);
    for(let d=0; d<nDots; d++){
      const f=( phase + d/nDots + i*0.013 ) % 1;
      const idx=Math.min(pts.length-1, Math.floor(f*pts.length));
      const dc = two ? (idx < pts.length/2 ? F.fromColor : F.toColor) : dotCol;
      dots.push({type:"Feature",properties:{w:e.w/wmax,c:dc,from:e.from,to:e.to},
        geometry:{type:"Point",coordinates:pts[idx]}});
    }'''
text = patch(text, OLD_FC, NEW_FC, "twotone-fc")

# (d-1) edge-skip for focus + focus global, in flowFeatureCollection edges loop
text = patch(text,
  '''  F.edges.forEach((e,i)=>{
    const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to];
    if(!a||!b) return;''',
  '''  F.edges.forEach((e,i)=>{
    if(flowFocusIso && e.from!==flowFocusIso && e.to!==flowFocusIso) return;   // click-to-isolate
    const a=ISO_CENTROID[e.from], b=ISO_CENTROID[e.to];
    if(!a||!b) return;''',
  "focus-skip")

# (d-2) declare flowFocusIso + helpers next to flowIso
text = patch(text,
  'let flowIso=null;                       // isolated category color (drug substance / migration type), or null',
  '''let flowIso=null;                       // isolated category color (drug substance / migration type), or null
let flowFocusIso=null;                  // ISO3 of a clicked country to isolate its web, or null
function setFlowFocus(iso){ flowFocusIso = (flowFocusIso===iso)?null:iso; if(flowActive()) drawFlowLegend(flowKey); }
function clearFlowFocus(){ flowFocusIso=null; if(flowActive()) drawFlowLegend(flowKey); }''',
  "focus-decl")

# (d-3) reset focus when switching flow
text = patch(text, 'function setFlow(key){\n  flowKey = key; flowIso=null;',
  'function setFlow(key){\n  flowKey = key; flowIso=null; flowFocusIso=null;', "focus-reset")

# (d-4) click a country isolates the web when a flow is active; click empty clears
text = patch(text,
  '  map.on("click","fills",e=>{ if(subOn)return; openCountry(e.features[0].properties); });',
  '''  map.on("click","fills",e=>{ if(subOn)return;
    if(flowActive()){ setFlowFocus(e.features[0].properties.iso3); return; }   // isolate this country's web
    openCountry(e.features[0].properties); });
  map.on("click",e=>{ if(flowActive() && !map.queryRenderedFeatures(e.point,{layers:["fills"]}).length) clearFlowFocus(); });''',
  "focus-click")

# (d-5) focus hint + clear link in the flow legend
text = patch(text,
  '''  if(F.note) b+=`<div class="lg-row" style="color:var(--muted);font-size:10.5px;font-style:italic;margin-top:6px;line-height:1.4">${F.note}</div>`;
  el.innerHTML=`<h3>${F.label}<span class="caret">▾</span></h3><div class="lg-body">${b}</div>`;''',
  '''  if(flowFocusIso){ b+=`<div class="lg-row" style="margin-top:7px;color:var(--accent);font-size:11px">Isolated: <b>${flowFocusIso}</b>'s connections — <span id="lgClearFocus" style="text-decoration:underline;cursor:pointer">show all</span></div>`; }
  else { b+=`<div class="lg-row" style="margin-top:7px;color:var(--muted);font-size:10.5px">Click a country to isolate just its connections.</div>`; }
  if(F.note) b+=`<div class="lg-row" style="color:var(--muted);font-size:10.5px;font-style:italic;margin-top:6px;line-height:1.4">${F.note}</div>`;
  el.innerHTML=`<h3>${F.label}<span class="caret">▾</span></h3><div class="lg-body">${b}</div>`;
  { const _cf=el.querySelector("#lgClearFocus"); if(_cf) _cf.onclick=ev=>{ ev.stopPropagation(); clearFlowFocus(); }; }''',
  "focus-legend")

open(OUT,"w",encoding="utf-8").write(text)
print(f"OK: baked {nfeat} features. CO2={sum(1 for f in MAP['features'] if 'co2pc' in f['properties'])} "
      f"CLIM={sum(1 for f in MAP['features'] if 'climateLabel' in f['properties'])}")
print("layers now:", [l.get('key') for l in META['layers']])
