#!/usr/bin/env python3
"""worldbook_claude build -- backfill real per-corridor magnitudes: refugees + wood.

Targeted backfill per Mike's call: lowest-coverage layers first. Adds real, cited
bilateral figures to FLOW_MAG for corridors that are already drawn on the globe but
currently fall back to the generic "no hard per-corridor figure" tooltip line.

refugees (was 12/49 rendered arcs sourced = 24%): +8 corridors, all UNHCR-sourced,
matching the layer's existing primary source (no source-block change needed):
  SDN->TCD 770,000  | SDN->EGY 930,000  | SSD->SDN 613,100  | COD->UGA 558,000
  VEN->PER 1,600,000 | SOM->KEN 299,567  | SOM->ETH 361,949  | ERI->ETH 179,118
  -> 20/49 = 41% coverage.

wood (was 6/21 = 29%): +2 corridors. Both cite a more specific sub-source inline in
the note, same pattern already used elsewhere in this file for the drugs layer
(MEX->USA cites InsightCrime inside a UNODC-sourced layer) -- FAOSTAT's own bilateral
trade matrix isn't usably searchable for specific pairs, so these two come from
customs/national-statistics reporting instead:
  PNG->CHN 2,270,000 m3/yr (China customs data via trade press, 2023)
  RUS->FIN 9,300,000 m3/yr (Luke/Finland, 2021 -- last full year before Finland's
    2022 import ban after Russia's invasion of Ukraine; flow is now defunct, kept
    as a real historical figure with that caveat in the note, same convention as
    the existing Afghan-opium note elsewhere in this file).

trafficking (was 8/30 = 27%): deliberately NOT backfilled. The best available public
figures for the highest-weight gap corridors (e.g. LBY->ITA, NGA->LBY) are migrant
smuggling/crossing counts (IOM Mediterranean arrivals data), not trafficking-victim
counts -- a real conceptual difference (smuggling = paid facilitated border crossing;
trafficking = coercion/exploitation). Using crossing counts as if they were victim
counts would misrepresent the data. Per SOURCING.md's own rule, leaving this layer's
coverage as-is is the correct call, not a shortfall.

Idempotent. Usage: python3 backfill_refugees_wood.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

REFUGEE_NEW = (
    '{"from":"SDN","to":"TCD","value":770000,"note":"Sudanese refugees in Chad since the 2023 civil war, end-2024. UNHCR."},'
    '{"from":"SDN","to":"EGY","value":930000,"note":"Sudanese registered as asylum-seekers in Egypt, Dec 2024. Egypt\'s government reports ~1.5M total arrivals since the crisis began."},'
    '{"from":"SSD","to":"SDN","value":613100,"note":"South Sudanese refugees hosted in Sudan, end-2024; predates the 2023 Sudan civil war."},'
    '{"from":"COD","to":"UGA","value":558000,"note":"Congolese (DRC) refugees in Uganda, end-2024; derived from DRC\'s ~31% share of Uganda\'s 1.8M refugee population."},'
    '{"from":"VEN","to":"PER","value":1600000,"note":"Venezuelan migrants and refugees in Peru, Dec 2024; world\'s 2nd-largest Venezuelan displaced population after Colombia."},'
    '{"from":"SOM","to":"KEN","value":299567,"note":"Somali refugees registered in Kenya, April 2024."},'
    '{"from":"SOM","to":"ETH","value":361949,"note":"Somali refugees hosted in Ethiopia, 2024; 2nd-largest refugee group there after South Sudanese."},'
    '{"from":"ERI","to":"ETH","value":179118,"note":"Eritrean refugees hosted in Ethiopia, 2024; 3rd-largest refugee group there."}'
)

WOOD_NEW = (
    '{"from":"PNG","to":"CHN","value":2270000,"note":"Papua New Guinea was China\'s top hardwood log supplier by volume, 2023 (China customs data via Global Wood Markets Info)."},'
    '{"from":"RUS","to":"FIN","value":9300000,"note":"Finland\'s last full year of Russian roundwood imports before the 2022 ban (Natural Resources Institute Finland / Luke); fell to zero by late 2022."}'
)

FIXES = [
    ("refugees +8 corridors",
     '{"from":"SYR","to":"JOR","value":611000,"note":"Syrian refugees in Jordan."}]}',
     '{"from":"SYR","to":"JOR","value":611000,"note":"Syrian refugees in Jordan."},' + REFUGEE_NEW + ']}'),
    ("wood +2 corridors",
     '{"from":"USA","to":"CHN","value":4500000,"note":"Logs (softwood+hardwood), m3/yr 2023 (~$2.23B); China is top US log market. Value-derived volume estimate."}]}',
     '{"from":"USA","to":"CHN","value":4500000,"note":"Logs (softwood+hardwood), m3/yr 2023 (~$2.23B); China is top US log market. Value-derived volume estimate."},' + WOOD_NEW + ']}'),
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

print("OK: refugees 12->20 corridors, wood 6->8 corridors" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
