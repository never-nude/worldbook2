#!/usr/bin/env python3
"""worldbook_claude build -- layer-by-layer sourcing backfill, round 2.

Continuation of the refugees/wood backfill from the previous session. Same rules:
only real, specific, citable bilateral figures; skip and say so rather than force a
number. Researched via parallel deep-research passes across 4 layer groups + direct
research on remittances, covering all remaining magnitude-bearing layers.

Adds (62 corridors across 9 layers):
  trade: +8
  oil: +6
  minerals: +7
  food: +8
  braindrain: +7
  cables: +8
  flights: +3
  students: +8
  remittances: +7

Deliberately NOT touched, with reasons (see session handoff doc for detail):
  arms        - the formal/trackable gap corridors are not in any public SIPRI table
                (would need interactive DB access); the illicit ones (Libya-Mali,
                Iran-Yemen, Libya-Chad, Pakistan-Afghanistan) are confirmed untrackable
                by design (UN Panel of Experts / CAR document them qualitatively only).
  drugs       - nothing found met the bar: either not bilateral-specific (UNODC treats
                Andes->Mexico->US as one continuous flow, not measurable legs), stale
                (2003/2015 data), or a unit mismatch ($ value where the layer needs tonnes).
  wildlife    - found strong real evidence (a named 12.9-tonne Singapore pangolin-scale
                seizure anchoring Nigeria->Vietnam) but the layer's unit is an arbitrary
                1-100 relative-weight index with no disclosed formula to calibrate a new
                score against -- assigning one myself would be editorializing, not sourcing.
  counterfeit - confirmed the OECD/EUIPO report has no China-to-specific-country matrix,
                only a provenance-economy ranking crossed with an EU-aggregate destination
                figure. None of the 10 target corridors exist as a citable bilateral number.
  trafficking - reconfirmed at 8/30 (unchanged). CTDC applies k-anonymity suppression
                (won't surface any country-pair cell under 10 victim records) -- a citable
                methodological reason, not just "couldn't find it." Also caught a near-miss:
                a "120,000 trafficked INTO Myanmar" stat describes the reverse direction of
                the Myanmar->Thailand corridor and would have been a substitution error.

Idempotent. Usage: python3 backfill_round2.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

FIXES = [
    ("trade +8 corridors",
     '{"from":"CHN","to":"NLD","value":120000000000,"note":"China exports to Netherlands (EU gateway port of Rotterdam); UN Comtrade/OEC. One direction."}]}',
     '{"from":"CHN","to":"NLD","value":120000000000,"note":"China exports to Netherlands (EU gateway port of Rotterdam); UN Comtrade/OEC. One direction."},{"from":"MEX","to":"USA","value":839000000000,"note":"Largest single bilateral goods trading relationship in North America; Mexico was the top source of US imports for a 2nd straight year, 2024 (US Census Bureau)."},{"from":"CAN","to":"USA","value":909100000000,"note":"US goods+services trade with Canada, 2024; Canada was the top destination for US exports (USTR). Not goods-only like most entries here."},{"from":"DEU","to":"USA","value":236000000000,"note":"US goods trade with Germany, 2024: $76B exports, $160B imports (US Census Bureau)."},{"from":"JPN","to":"USA","value":228000000000,"note":"US goods trade with Japan, 2024, up 2.3%: $80B exports, $148B imports (US Census Bureau)."},{"from":"USA","to":"CHN","value":143500000000,"note":"US goods exports to China only, 2024 (one direction; US Census Bureau) -- far smaller than the two-way total given the US trade deficit with China."},{"from":"KOR","to":"CHN","value":328080000000,"note":"China remained South Korea\'s top trading partner for a 21st consecutive year, 2024 (Korean MOFA/customs data). Korean- and Chinese-reported totals differ slightly, a common mirror-statistics gap."},{"from":"RUS","to":"CHN","value":244800000000,"note":"Russia-China trade hit a record for a 3rd straight year, though growth slowed amid Western sanctions on bank settlements, 2024 (China customs data)."},{"from":"DEU","to":"FRA","value":120510000000,"note":"Germany\'s exports to France only, 2024 (one direction; UN Comtrade); France is a top-5 German export destination."}]}'),
    ("oil +6 corridors",
     '{"from":"USA","to":"NLD","value":22.0,"note":"LNG in million tonnes/year; representative of US LNG to Europe (Europe took 53% of US LNG, ~6.3 bcf/d, in 2024; NLD/FRA/UK = 46% of that). Measured."}]}',
     '{"from":"USA","to":"NLD","value":22.0,"note":"LNG in million tonnes/year; representative of US LNG to Europe (Europe took 53% of US LNG, ~6.3 bcf/d, in 2024; NLD/FRA/UK = 46% of that). Measured."},{"from":"SAU","to":"IND","value":640000,"note":"Crude, barrels/day; Saudi Arabia was India\'s 3rd-largest crude supplier, 13.0% of India\'s imports, 2024 (tanker-tracking analysis)."},{"from":"ARE","to":"CHN","value":35500000,"note":"Crude, tonnes/year (not barrels/day like most entries here); UAE was China\'s 6th-largest crude supplier by volume, 2024 (China customs data)."},{"from":"AGO","to":"CHN","value":205000000,"note":"Crude, barrels/year (not barrels/day); Angola supplied 5.1% of China\'s crude imports by volume, 2024 (China customs data)."},{"from":"RUS","to":"TUR","value":16700000,"note":"Crude, tonnes/year; Turkiye\'s Russian crude purchases rose ~1.5x YoY, 2024, as the SOCAR/STAR refinery switched fully to Russian crude (CREA)."},{"from":"KWT","to":"CHN","value":290000000,"note":"Crude, barrels/year (not barrels/day); Kuwait supplied 7.1% of China\'s crude imports by volume, 2024, down 1% from 2023 (China customs data)."},{"from":"IRN","to":"CHN","value":1400000,"note":"Crude, barrels/day; independent tanker-tracking estimate (Kpler/Vortexa-style analysis). China does not officially report Iranian crude imports, typically routed/relabeled via Malaysia to evade US sanctions -- no customs-confirmed figure exists from either side."}]}'),
    ("minerals +7 corridors",
     '{"from":"COD","to":"CHN","value":114000,"note":"Cobalt content in intermediates/hydroxide; DRC ~75%+ of global cobalt. Gross hydroxide tonnage ~3-4x higher. Derived from 2024 China imports."}]}',
     '{"from":"COD","to":"CHN","value":114000,"note":"Cobalt content in intermediates/hydroxide; DRC ~75%+ of global cobalt. Gross hydroxide tonnage ~3-4x higher. Derived from 2024 China imports."},{"from":"ZAF","to":"CHN","value":15930000,"note":"Manganese ore, tonnes/year; South Africa supplied 54% of China\'s manganese ore imports, 2024 (China customs data)."},{"from":"AUS","to":"KOR","value":51000000,"note":"Iron ore, tonnes/year; South Korea was Australia\'s 3rd-largest iron ore export market by volume, 5.6% share, 2024."},{"from":"CHN","to":"JPN","value":5380,"note":"Rare earth oxides/compounds, tonnes/year; China\'s exports to Japan rose ~26% YoY, 2024, just ahead of 2025 export-control tightening (Japan customs data via industry analysis)."},{"from":"CHN","to":"USA","value":15000,"note":"Rare earths (compounds+metals), tonnes/year; China supplied ~71% of all US rare-earth imports, 2021-2024 average (USGS Mineral Commodity Summaries 2025)."},{"from":"GIN","to":"CHN","value":110200000,"note":"Bauxite, tonnes/year; Guinea shipped a record 110.2Mt to China in 2024, 76% of Guinea\'s total bauxite exports (Guinea shipping/customs data)."},{"from":"MNG","to":"CHN","value":75000000,"note":"Coking coal, tonnes/year; Mongolia\'s total coal exports hit a record 83.7Mt in 2024, ~90% to China. Derived (share x total), not a directly published bilateral figure (Mongolia customs data)."},{"from":"CHN","to":"DEU","value":11000,"note":"Rare earth permanent magnets, tonnes/year (approx.); Germany was the top destination for Chinese rare-earth magnet exports, 18.8% of a record 58,152t total, 2024 -- critical for Germany\'s auto/wind sectors (Adamas Intelligence)."}]}'),
    ("food +8 corridors",
     '{"from":"ARG","to":"IND","value":5000000,"note":"Soybean meal; Argentina exported 16.2 Mt total in 2023 (drought-reduced), main buyers India, China, Netherlands."}]}',
     '{"from":"ARG","to":"IND","value":5000000,"note":"Soybean meal; Argentina exported 16.2 Mt total in 2023 (drought-reduced), main buyers India, China, Netherlands."},{"from":"ARG","to":"CHN","value":1736410,"note":"Soybeans, tonnes; Argentina\'s top single soybean export market by volume, 2023 (UN Comtrade)."},{"from":"USA","to":"JPN","value":2280240,"note":"Soybeans, tonnes; Japan sourced roughly three-quarters of its soybean imports from the US, 2023 (UN Comtrade)."},{"from":"UKR","to":"CHN","value":5440220,"note":"Corn, tonnes; China\'s largest single source of Ukrainian corn before Brazil\'s 2024 displacement (UN Comtrade)."},{"from":"CAN","to":"USA","value":2060990,"note":"Wheat, tonnes; Canada\'s top wheat export corridor by volume, 2023 (UN Comtrade)."},{"from":"IND","to":"BGD","value":215124,"note":"Rice, tonnes, 2023 (UN Comtrade); spans both sides of India\'s mid-2023 non-basmati white rice export ban, so not a steady-state baseline."},{"from":"UKR","to":"IDN","value":665294,"note":"Wheat, tonnes; Indonesia was the 3rd-largest buyer of Ukrainian wheat by volume, 2023 (UN Comtrade)."},{"from":"CAN","to":"JPN","value":1991320,"note":"Wheat, tonnes; Canada\'s largest single wheat export market in Asia, 2023 (UN Comtrade)."},{"from":"USA","to":"KOR","value":909953,"note":"Corn, tonnes; South Korea\'s leading source of imported corn under the KORUS trade agreement, 2023 (UN Comtrade)."}]}'),
    ("braindrain +7 corridors",
     '{"from":"NGA","to":"GBR","value":4722,"note":"Nurses/midwives newly registered (latest year); Nigeria 3rd-largest origin of UK-registered nurses. Annual flow, not full stock. Estimate."}]}',
     '{"from":"NGA","to":"GBR","value":4722,"note":"Nurses/midwives newly registered (latest year); Nigeria 3rd-largest origin of UK-registered nurses. Annual flow, not full stock. Estimate."},{"from":"ZWE","to":"GBR","value":4794,"note":"Zimbabwe-trained nurses on the UK Nursing and Midwifery Council register, as of 30 Sep 2025."},{"from":"ZAF","to":"GBR","value":2903,"note":"South Africa-trained nurses on the UK Nursing and Midwifery Council register, as of 30 Sep 2025."},{"from":"DZA","to":"FRA","value":6320,"note":"Algeria-trained physicians practicing in France, 2023 (OECD Health Workforce Migration Database)."},{"from":"MAR","to":"FRA","value":1286,"note":"Morocco-trained physicians practicing in France, 2023 (OECD Health Workforce Migration Database)."},{"from":"ROU","to":"DEU","value":3914,"note":"Romania-trained physicians practicing in Germany, 2021 (OECD Health Workforce Migration Database; Germany does not report nurse-by-origin data to OECD)."},{"from":"MEX","to":"USA","value":10036,"note":"Mexico-trained physicians licensed in the US, 2020 (FSMB Census of Licensed Physicians). Measures medical-school location, not birth."},{"from":"NGA","to":"USA","value":5000,"note":"Nigeria-born physicians and surgeons in the US, 2021, rounded (Migration Policy Institute analysis of US Census ACS). Measures birth country, not training."}]}'),
    ("cables +8 corridors",
     '{"from":"JPN","to":"USA","value":60,"note":"JUPITER (2020); Japan/Philippines - Los Angeles; >60 Tbps."}]}',
     '{"from":"JPN","to":"USA","value":60,"note":"JUPITER (2020); Japan/Philippines - Los Angeles; >60 Tbps."},{"from":"USA","to":"BRA","value":160,"note":"BRUSA cable, 8 fiber pairs, ready for service 2018; Virginia Beach to Fortaleza/Rio de Janeiro (Telxius)."},{"from":"USA","to":"JPN","value":60,"note":"JUPITER cable, 5 fiber pairs, ready for service 2021; Hermosa Beach to Maruyama/Shima (NTT/FCC filing)."},{"from":"GBR","to":"IND","value":180,"note":"2Africa (Pearls extension), 16 fiber-pair system; Bude, Cornwall to Mumbai landing completed 2024 (2Africa consortium)."},{"from":"FRA","to":"SGP","value":126,"note":"SEA-ME-WE 6, 10 fiber pairs; Marseille landing April 2024 to Tuas, Singapore (Orange Newsroom). PEACE Cable serves the same city pair at a higher stated capacity."},{"from":"EGY","to":"IND","value":28,"note":"Europe India Gateway (EIG), 3 fiber pairs, upgraded capacity; Zafarana, Egypt to Mumbai, India (Capacity Media)."},{"from":"JPN","to":"SGP","value":126,"note":"SJC2 cable, 8 fiber pairs, went live July 2025; 11 landing stations including Japan and Singapore (NEC)."},{"from":"SGP","to":"IND","value":132,"note":"SEA-ME-WE 6, Tuas, Singapore to Chennai/Mumbai, India; consortium-updated capacity as of Nov 2025."},{"from":"KOR","to":"USA","value":70,"note":"New Cross Pacific (NCP), 7 fiber pairs, ready for service 2018; Busan to Pacific City, Oregon."}]}'),
    ("flights +3 corridors",
     '{"from":"USA","to":"GBR","value":4010000,"note":"New York JFK-London Heathrow (LHR); #10; busiest transatlantic/long-haul route."}]}',
     '{"from":"USA","to":"GBR","value":4010000,"note":"New York JFK-London Heathrow (LHR); #10; busiest transatlantic/long-haul route."},{"from":"ARE","to":"IND","value":19000000,"note":"~19M passengers, 2023, ~30% of India\'s total international air traffic (Observer Research Foundation, citing DGCA data). Passenger count, not scheduled-seat capacity."},{"from":"GBR","to":"ESP","value":13900000,"note":"UK-Spain was Europe\'s largest single-country aviation capacity market, 2024/25 season, up 8.2% YoY (OAG)."},{"from":"THA","to":"CHN","value":8000000,"note":"Thailand-China seat capacity, 2024, declining to ~7.6M in 2025 (OAG)."}]}'),
    ("students +8 corridors",
     '{"from":"NGA","to":"USA","value":20029,"note":"2023/24, Nigeria (Open Doors)."}]}',
     '{"from":"NGA","to":"USA","value":20029,"note":"2023/24, Nigeria (Open Doors)."},{"from":"CHN","to":"CAN","value":102150,"note":"China-citizenship study permit holders with valid permits in Canada, end of 2023 (IRCC)."},{"from":"NGA","to":"GBR","value":57505,"note":"Nigerian-domicile student enrolments at UK HE providers, 2023/24, down 36% vs 2022/23 due to dependent-visa restrictions (HESA)."},{"from":"SAU","to":"USA","value":14828,"note":"Saudi Arabian students enrolled in the US, 2023/24 academic year (IIE Open Doors)."},{"from":"FRA","to":"CAN","value":26980,"note":"France-citizenship study permit holders with valid permits in Canada, end of 2023 (IRCC)."},{"from":"MAR","to":"FRA","value":42015,"note":"Moroccan students in French higher education, 2024/25, down 3% YoY; Morocco remains the top single origin country for foreign students in France (Campus France)."},{"from":"PAK","to":"GBR","value":45720,"note":"Pakistani-domicile student enrolments at UK HE providers, 2023/24; Pakistan was the UK\'s fastest-growing origin market that year, +38% (HESA)."},{"from":"BRA","to":"USA","value":16877,"note":"Brazilian students enrolled in the US, 2023/24 academic year (IIE Open Doors)."},{"from":"CHN","to":"JPN","value":123485,"note":"Chinese nationals enrolled in Japan as of 1 May 2024, up 6.9% YoY (JASSO/MEXT Annual International Student Survey)."}]}'),
    ("remittances +7 corridors",
     '{"from":"HKG","to":"CHN","value":5500000000,"note":"Hong Kong SAR -> mainland China; KNOMAD bilateral matrix (~2021). Estimate."}]}',
     '{"from":"HKG","to":"CHN","value":5500000000,"note":"Hong Kong SAR -> mainland China; KNOMAD bilateral matrix (~2021). Estimate."},{"from":"ARE","to":"PAK","value":5500000000,"note":"UAE was Pakistan\'s 2nd-largest remittance source, 18.7% of total inflows, FY2024 (State Bank of Pakistan)."},{"from":"SAU","to":"PAK","value":7400000000,"note":"Saudi Arabia was Pakistan\'s largest remittance source, 25% of total inflows, FY2024 (State Bank of Pakistan)."},{"from":"RUS","to":"UZB","value":11500000000,"note":"Russia supplied 77% of Uzbekistan\'s record $14.8B in remittances, 2024, up 29% YoY (Central Bank of Uzbekistan)."},{"from":"GBR","to":"IND","value":12820000000,"note":"UK accounted for 10.8% of India\'s $118.7B in remittance inflows, 2023-24 (RBI Remittances Survey). Advanced economies overtook Gulf nations as India\'s top remittance source that year."},{"from":"USA","to":"DOM","value":8600000000,"note":"Derived: ~80% of the Dominican Republic\'s $10,756M in 2024 remittances came from the US (Central Bank of the Dominican Republic)."},{"from":"USA","to":"COL","value":6280000000,"note":"Derived: 53% of Colombia\'s record $11.848B in 2024 remittances came from the US (Colombian central bank / BBVA Research)."},{"from":"USA","to":"SLV","value":7360000000,"note":"Derived: ~90% of El Salvador\'s $8.182B in 2023 remittances came from the US -- its dominant single source (Banco Central de Reserva)."}]}'),
]

results = []
for label, OLD, NEW in FIXES:
    if OLD not in text and NEW in text:
        results.append((label, "already-applied"))
    elif OLD in text:
        text = text.replace(OLD, NEW, 1)
        results.append((label, "patched"))
    else:
        results.append((label, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for label, status in results:
    print(f"  [{status:>16}] {label}")
    if status not in ("patched", "already-applied"):
        ok = False

print("OK: round 2 backfill applied" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
