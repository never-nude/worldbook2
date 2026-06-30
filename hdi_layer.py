#!/usr/bin/env python3
"""Add a Human Development Index (HDI) choropleth to Worldbook.
Single-hue sequential ramp (color = information, lower -> higher development).
Source: UNDP Human Development Report 2023/24 (2022 HDI values).
Idempotent, pure ASCII. Usage: python3 hdi_layer.py index.html index.html"""
import json, sys
INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

if "color_hdi" in text[:400000] or '"hdi":{"label":"Human Development Index"' in text:
    open(OUT, "w", encoding="utf-8").write(text)
    print("  [already-applied] HDI layer present"); print("OK: HDI (no-op)"); sys.exit(0)

HDI = {
"CHE":0.967,"NOR":0.966,"ISL":0.959,"HKG":0.956,"DNK":0.952,"SWE":0.952,"DEU":0.950,"IRL":0.950,
"SGP":0.949,"AUS":0.946,"NLD":0.946,"BEL":0.942,"FIN":0.942,"GBR":0.940,"NZL":0.939,"ARE":0.937,
"CAN":0.935,"KOR":0.929,"LUX":0.927,"USA":0.927,"AUT":0.926,"SVN":0.926,"JPN":0.920,"ISR":0.915,
"MLT":0.915,"ESP":0.911,"FRA":0.910,"CYP":0.907,"ITA":0.906,"EST":0.899,"CZE":0.895,"GRC":0.893,
"BHR":0.888,"POL":0.881,"LTU":0.879,"LVA":0.879,"HRV":0.878,"SAU":0.875,"QAT":0.875,"PRT":0.874,
"CHL":0.860,"TUR":0.855,"SVK":0.855,"HUN":0.851,"ARG":0.849,"KWT":0.847,"MNE":0.844,"URY":0.830,
"ROU":0.827,"RUS":0.821,"PAN":0.820,"OMN":0.819,"GEO":0.814,"TTO":0.814,"BHS":0.812,"BRB":0.809,
"MYS":0.807,"CRI":0.806,"SRB":0.805,"MUS":0.802,"KAZ":0.802,"BLR":0.801,"THA":0.803,"BGR":0.799,
"ALB":0.789,"CHN":0.788,"ARM":0.786,"IRN":0.780,"LKA":0.780,"BIH":0.780,"MEX":0.781,"NMK":0.770,
"DOM":0.766,"ECU":0.765,"TKM":0.764,"MDA":0.763,"PER":0.762,"BRA":0.760,"AZE":0.760,"COL":0.758,
"PRY":0.756,"LBY":0.746,"DZA":0.745,"MNG":0.741,"JOR":0.736,"UKR":0.734,"TUN":0.732,"FJI":0.729,
"EGY":0.728,"UZB":0.727,"VNM":0.726,"LBN":0.723,"ZAF":0.717,"IDN":0.713,"PHL":0.710,"BWA":0.708,
"JAM":0.706,"KGZ":0.701,"BOL":0.698,"MAR":0.698,"GAB":0.693,"BTN":0.681,"TJK":0.679,"NIC":0.674,
"SLV":0.674,"IRQ":0.673,"BGD":0.670,"IND":0.644,"GTM":0.629,"HND":0.624,"LAO":0.620,"NAM":0.610,
"SWZ":0.610,"MMR":0.608,"GHA":0.602,"KEN":0.601,"NPL":0.601,"KHM":0.600,"COG":0.593,"AGO":0.591,
"CMR":0.587,"ZMB":0.569,"SYR":0.557,"HTI":0.552,"RWA":0.548,"NGA":0.548,"UGA":0.550,"CIV":0.550,
"ZWE":0.550,"TGO":0.547,"PAK":0.540,"MRT":0.540,"TZA":0.532,"LSO":0.521,"SEN":0.517,"SDN":0.516,
"MWI":0.508,"BEN":0.504,"GMB":0.495,"ERI":0.493,"ETH":0.492,"MDG":0.487,"LBR":0.487,"GNB":0.483,
"COD":0.481,"GIN":0.471,"AFG":0.462,"MOZ":0.461,"SLE":0.458,"BFA":0.438,"YEM":0.424,"BDI":0.420,
"MLI":0.410,"NER":0.394,"TCD":0.394,"CAF":0.387,"SSD":0.381,"SOM":0.380
}
RAMP = [(0.40,"#10243f"),(0.55,"#1b3f66"),(0.68,"#26628f"),(0.78,"#3f8bbf"),(0.88,"#79b8e6"),(0.97,"#cfe8ff")]
NODATA = "#262f3d"
def _hx(c): c=c.lstrip("#"); return (int(c[0:2],16),int(c[2:4],16),int(c[4:6],16))
def _rgb(t): return "#%02x%02x%02x"%t
def ramp(v):
    if v is None: return NODATA
    if v<=RAMP[0][0]: return RAMP[0][1]
    if v>=RAMP[-1][0]: return RAMP[-1][1]
    for i in range(len(RAMP)-1):
        v0,c0=RAMP[i]; v1,c1=RAMP[i+1]
        if v0<=v<=v1:
            f=(v-v0)/(v1-v0); a,b=_hx(c0),_hx(c1)
            return _rgb(tuple(round(a[k]+(b[k]-a[k])*f) for k in range(3)))
    return RAMP[-1][1]
def patch_once(t,a,b,lbl):
    n=t.count(a); assert n==1, "anchor %s: %d matches"%(lbl,n); return t.replace(a,b)

lines = text.split("\n")
mi = next(i for i,l in enumerate(lines) if l.startswith("const MAPDATA = "))
me = next(i for i,l in enumerate(lines) if l.startswith("const META = "))
MAP = json.loads(lines[mi][len("const MAPDATA = "):].rstrip().rstrip(";"))
n=0
for f in MAP["features"]:
    iso = f["properties"].get("iso3")
    if iso in HDI:
        f["properties"]["hdi"]=HDI[iso]; f["properties"]["color_hdi"]=ramp(HDI[iso]); n+=1
lines[mi] = "const MAPDATA = " + json.dumps(MAP, separators=(",",":")) + ";"
META = json.loads(lines[me][len("const META = "):].rstrip().rstrip(";"))
cfg = {"group":"People & economy","key":"hdi","label":"Human Development Index","type":"numeric",
       "prop":"hdi","short":"HDI","fmtType":"dec3","unit":"0-1 index (higher = more developed)",
       "stops":[{"v":v,"color":c} for v,c in RAMP]}
L=META["layers"]; li=next(i for i,l in enumerate(L) if l.get("key")=="internet")
L[li+1:li+1]=[cfg]
lines[me] = "const META = " + json.dumps(META, separators=(",",":")) + ";"
text = "\n".join(lines)
text = patch_once(text,
    'if(c.fmtType==="dec1")  return (+v).toFixed(1);',
    'if(c.fmtType==="dec1")  return (+v).toFixed(1);\n  if(c.fmtType==="dec3")  return (+v).toFixed(3);',
    "labelFor-dec3")
prov = ('"hdi":{"label":"Human Development Index","metric":"A composite of life expectancy at birth, '
 'education (mean and expected years of schooling), and gross national income per capita.",'
 '"unit":"0-1 index (higher = more developed)","higherIs":"good",'
 '"colorMeaning":"Color encodes HDI from lower to higher human development.",'
 '"primarySource":{"org":"UNDP","datasetTitle":"Human Development Report 2023/24 \\u2014 Human Development Index (2022 values)",'
 '"url":"https://hdr.undp.org/data-center/human-development-index","year":"2024"},'
 '"additionalSources":[],"dataKind":"estimated","provenance":"primary","updateFrequency":"annual",'
 '"methodology":"Geometric mean of normalized indices for the three HDI dimensions (a long and healthy life, '
 'knowledge, and a decent standard of living).",'
 '"limitations":"A national average that masks within-country inequality; the income dimension is capped, '
 'and a few countries lack a reported value (shown as no data).","confidence":"high"},')
text = patch_once(text, "const LAYER_PROV={", "const LAYER_PROV={"+prov, "LAYER_PROV-hdi")
open(OUT, "w", encoding="utf-8").write(text)
print("  [patched] HDI baked into %d countries"%n); print("OK: HDI layer added"); sys.exit(0)
