import sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
def patch(t,a,b,label):
    n=t.count(a); assert n==1, f"{label}: anchor matched {n}x"; return t.replace(a,b)
REF_ADD=(',{from:"SYR",to:"DEU",w:0.7},{from:"SYR",to:"IRQ",w:0.3},{from:"AFG",to:"TUR",w:0.3},'
 '{from:"UKR",to:"CZE",w:0.35},{from:"SDN",to:"SSD",w:0.8},{from:"SDN",to:"ETH",w:0.5},'
 '{from:"SDN",to:"LBY",w:0.2},{from:"SSD",to:"ETH",w:0.4},{from:"SSD",to:"KEN",w:0.15},'
 '{from:"COD",to:"RWA",w:0.2},{from:"COD",to:"TZA",w:0.15},{from:"COD",to:"ZMB",w:0.1},'
 '{from:"COD",to:"BDI",w:0.1},{from:"SOM",to:"YEM",w:0.25},{from:"MMR",to:"THA",w:0.2},'
 '{from:"MMR",to:"MYS",w:0.1},{from:"CAF",to:"TCD",w:0.15},{from:"CAF",to:"COD",w:0.2},'
 '{from:"VEN",to:"BRA",w:0.6},{from:"VEN",to:"ECU",w:0.45},{from:"VEN",to:"CHL",w:0.45},'
 '{from:"NIC",to:"CRI",w:0.25},{from:"MLI",to:"MRT",w:0.2},{from:"MLI",to:"NER",w:0.15},'
 '{from:"BFA",to:"CIV",w:0.15},{from:"NGA",to:"NER",w:0.3},{from:"NGA",to:"CMR",w:0.15},'
 '{from:"ESH",to:"DZA",w:0.17},{from:"ERI",to:"SDN",w:0.1}')
MIG_ADD=(',{from:"IND",to:"KWT",w:1.0},{from:"IND",to:"QAT",w:0.7},{from:"IND",to:"OMN",w:0.7},'
 '{from:"PAK",to:"SAU",w:1.6},{from:"PAK",to:"ARE",w:1.6},{from:"EGY",to:"SAU",w:1.4},'
 '{from:"EGY",to:"ARE",w:0.9},{from:"BGD",to:"ARE",w:1.1},{from:"PHL",to:"SAU",w:0.9},'
 '{from:"IDN",to:"SAU",w:0.6},{from:"YEM",to:"SAU",w:0.9},{from:"NPL",to:"QAT",w:0.4},'
 '{from:"BFA",to:"CIV",w:1.5},{from:"ZWE",to:"ZAF",w:1.0},{from:"MOZ",to:"ZAF",w:0.7},'
 '{from:"LSO",to:"ZAF",w:0.4},{from:"MAR",to:"ESP",w:0.8},{from:"MAR",to:"ITA",w:0.5},'
 '{from:"CUB",to:"USA",w:1.3},{from:"SLV",to:"USA",w:1.4},{from:"GTM",to:"USA",w:1.1},'
 '{from:"DOM",to:"USA",w:1.2},{from:"HND",to:"USA",w:0.7},{from:"COL",to:"USA",w:0.8},'
 '{from:"HTI",to:"USA",w:0.7},{from:"NIC",to:"CRI",w:0.3},{from:"PRY",to:"ARG",w:0.6},'
 '{from:"BOL",to:"ARG",w:0.4},{from:"PER",to:"CHL",w:0.4},{from:"IDN",to:"MYS",w:1.0},'
 '{from:"VNM",to:"USA",w:1.4},{from:"KOR",to:"USA",w:1.0},{from:"UZB",to:"RUS",w:2.5},'
 '{from:"TJK",to:"RUS",w:1.3},{from:"KGZ",to:"RUS",w:0.9},{from:"ARM",to:"RUS",w:1.0},'
 '{from:"AZE",to:"RUS",w:0.9},{from:"ROU",to:"ESP",w:0.9},{from:"ROU",to:"DEU",w:1.0},'
 '{from:"ALB",to:"GRC",w:0.5},{from:"ALB",to:"ITA",w:0.5},{from:"UKR",to:"POL",w:1.5,c:"#d4793a"},'
 '{from:"SYR",to:"DEU",w:0.8,c:"#d4793a"},{from:"NZL",to:"AUS",w:0.6},{from:"IND",to:"AUS",w:0.7},'
 '{from:"CHN",to:"AUS",w:0.7}')
if 'from:"ESH",to:"DZA"' not in text:
    text=patch(text,'{from:"ERI",to:"ETH",w:1.5}','{from:"ERI",to:"ETH",w:1.5}'+REF_ADD,'refugees-edges')
if 'from:"UZB",to:"RUS"' not in text:
    text=patch(text,'{from:"PRI",to:"USA",w:1.2}','{from:"PRI",to:"USA",w:1.2}'+MIG_ADD,'migration-edges')
open(OUT,"w",encoding="utf-8").write(text)
print("OK: refugees +29, migration +46 corridors")
