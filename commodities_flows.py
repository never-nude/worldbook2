import json, re, sys
INP=sys.argv[1] if len(sys.argv)>1 else "index.html"
OUT=sys.argv[2] if len(sys.argv)>2 else "index.html"
text=open(INP,encoding="utf-8").read()
assert 'flow_oil' not in text, 'commodity flows already applied - aborting.'
def edges_js(edges):
    return ',\n'.join('      '+','.join(f'{{from:"{a}",to:"{b}",w:{w}}}' for a,b,w in edges[k:k+3])
                      for k in range(0,len(edges),3))
OIL=[('SAU','CHN',4),('SAU','IND',3),('SAU','JPN',3),('SAU','KOR',2.5),('RUS','CHN',4),('RUS','IND',3.5),
('RUS','TUR',2),('IRQ','CHN',3),('IRQ','IND',2.5),('ARE','CHN',2.5),('ARE','JPN',2),('KWT','CHN',2),
('IRN','CHN',2.5),('USA','NLD',2),('USA','KOR',2),('USA','IND',1.5),('CAN','USA',4),('MEX','USA',2),
('VEN','CHN',1.5),('NGA','IND',2),('NGA','ESP',1.5),('AGO','CHN',2.5),('NOR','GBR',1.5),('NOR','DEU',1.5),
('KAZ','ITA',1.5),('LBY','ITA',1.5),('DZA','ESP',1.5),('QAT','JPN',2),('QAT','KOR',1.5),('AUS','JPN',2),('AUS','CHN',2)]
FOOD=[('USA','MEX',3),('USA','CHN',3.5),('USA','JPN',2),('BRA','CHN',4),('ARG','CHN',2.5),('RUS','EGY',3),
('RUS','TUR',2),('UKR','EGY',2),('UKR','CHN',2),('UKR','IDN',1.5),('CAN','USA',2),('CAN','JPN',1.5),
('AUS','IDN',2),('AUS','CHN',2),('FRA','DZA',1.5),('USA','KOR',1.5),('IND','BGD',2),('THA','NGA',1.5),
('VNM','PHL',1.5),('USA','EGY',1.5),('RUS','IRN',1.5),('FRA','EGY',1.5),('BRA','IRN',1.5),('USA','COL',1.5)]
MIN=[('AUS','CHN',5),('BRA','CHN',4),('AUS','JPN',2.5),('AUS','KOR',2),('CHL','CHN',3),('PER','CHN',2.5),
('COD','CHN',3),('ZMB','CHN',2),('ZAF','CHN',2.5),('CHN','JPN',2),('CHN','USA',2),('CHN','DEU',1.5),
('CHN','KOR',1.5),('GIN','CHN',2),('IDN','CHN',3),('PHL','CHN',1.5),('RUS','CHN',2),('MNG','CHN',2),
('CAN','USA',2),('ZAF','JPN',1.5),('BRA','JPN',1.5),('PER','JPN',1)]
WOOD=[('RUS','CHN',4),('CAN','USA',4),('CAN','CHN',2),('USA','CHN',2),('BRA','CHN',2),('NZL','CHN',2.5),
('IDN','CHN',2),('MYS','CHN',1.5),('DEU','CHN',1.5),('SWE','GBR',1.5),('FIN','DEU',1.5),('RUS','FIN',1.5),
('CHL','CHN',2),('GAB','CHN',1.5),('COG','CHN',1.5),('MMR','CHN',1.5),('PNG','CHN',1.5),('USA','JPN',1.5),
('CAN','JPN',1.5),('AUT','ITA',1.5),('RUS','JPN',1.5)]
FLOWS_JS = '''  oil: {
    label: "Oil & gas", group: "Resources",
    unit: "major crude oil & LNG trade routes",
    desc: "Where the world's oil and gas move: from the big exporters (Gulf, Russia, the Americas, West Africa) to the big consumers (China, India, Europe, Japan).",
    color: "#c2862e", dotColor:"#f0d6a0",
    legend: "Each arc is a major oil/gas export route; dots flow from exporter toward importer.",
    note: "Major crude-oil and LNG corridors (IEA / EIA / OPEC). Routes thread strategic chokepoints - Hormuz, Malacca, Suez. Magnitudes are relative.",
    sources: [{label:"IEA - Oil Market Report", url:"https://www.iea.org/topics/oil-market-report"},
      {label:"U.S. EIA - Petroleum & other liquids", url:"https://www.eia.gov/petroleum/"}],
    edges: [
''' + edges_js(OIL) + '''
    ]
  },
  food: {
    label: "Food & grain", group: "Resources",
    unit: "major cereal & staple-crop trade",
    desc: "The world's breadbasket flows - wheat, maize, soy and rice from the great exporters to import-dependent regions.",
    color: "#e6cf4a", dotColor:"#fbf3c0",
    legend: "Each arc is a major food/grain export route; dots flow from exporter toward importer.",
    note: "Major cereal & oilseed corridors (FAO / USDA). Includes the wheat flows from Russia & Ukraine that much of the Middle East and Africa depend on. Magnitudes are relative.",
    sources: [{label:"FAO - Food Outlook", url:"https://www.fao.org/giews/reports/food-outlook/en/"},
      {label:"USDA - Foreign Agricultural Service", url:"https://www.fas.usda.gov/data"}],
    edges: [
''' + edges_js(FOOD) + '''
    ]
  },
  minerals: {
    label: "Minerals & metals", group: "Resources",
    unit: "iron ore, copper, nickel, cobalt, rare earths",
    desc: "The raw materials of industry: iron ore and copper to China, cobalt and nickel for batteries, and the rare earths China ships to the world.",
    color: "#8fa3bf", dotColor:"#e3ebf4",
    legend: "Each arc is a major mineral/metal trade route; dots flow from source toward processor/consumer.",
    note: "Major ore & metal corridors (USGS / UNCTAD): Australian & Brazilian iron ore, Chilean & DRC copper/cobalt, Indonesian nickel, and Chinese rare-earth exports. Magnitudes are relative.",
    sources: [{label:"USGS - Mineral Commodity Summaries", url:"https://www.usgs.gov/centers/national-minerals-information-center"}],
    edges: [
''' + edges_js(MIN) + '''
    ]
  },
  wood: {
    label: "Timber & wood", group: "Resources",
    unit: "logs, lumber, pulp & wood products",
    desc: "Where wood comes from and goes: boreal and tropical timber, lumber and pulp moving to the big manufacturing and construction markets.",
    color: "#8a9a4a", dotColor:"#e2ecc4",
    legend: "Each arc is a major timber/wood-products trade route; dots flow from exporter toward importer.",
    note: "Major roundwood, lumber and pulp corridors (FAO FRA / Forest Products). Includes Russian, Canadian and tropical-hardwood flows to China. Magnitudes are relative.",
    sources: [{label:"FAO - Forest Products Statistics", url:"https://www.fao.org/forestry/statistics/en/"}],
    edges: [
''' + edges_js(WOOD) + '''
    ]
  },
'''
n=text.count('const FLOWS = {'); assert n==1, n
text=text.replace('const FLOWS = {','const FLOWS = {\n'+FLOWS_JS)
lines=text.split('\n')
me=next(i for i,l in enumerate(lines) if l.startswith('const META = '))
META=json.loads(lines[me][len('const META = '):].rstrip().rstrip(';'))
L=META['layers']
new=[{"group":"Resources","key":"flow_"+k,"label":lbl,"type":"flow","flowKey":k}
     for k,lbl in [("oil","Oil & gas"),("food","Food & grain"),("minerals","Minerals & metals"),("wood","Timber & wood")]]
si=next(i for i,l in enumerate(L) if l.get('key')=='satellite')
L[si:si]=new
lines[me]='const META = '+json.dumps(META,separators=(',',':'))+';'
text='\n'.join(lines)
open(OUT,'w',encoding='utf-8').write(text)
print("OK: commodity flows added - oil, food, minerals, wood")
