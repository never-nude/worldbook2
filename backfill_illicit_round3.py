#!/usr/bin/env python3
"""worldbook_claude build -- round 3 of illicit-route sourcing backfill (drugs +
counterfeit). Mike asked to research illicit routes further for data to back up
existing claims. Ran 4 parallel research agents (drugs, arms, wildlife+counterfeit,
trafficking), each briefed on exactly what a prior round already tried/rejected and
why, told to find NEW angles or confirm the rejections still hold rather than
re-tread the same ground. Net result: 2 real additions clear the bar, everything
else reconfirmed correctly blocked (see agent reports in this session for full
detail per layer).

1. DRUGS +1: Ecuador -> Belgium (Antwerp), cocaine, 14.6 tonnes, 2024. Origin-
   country-specific (not generic "Latin America"), tonnage-native (matches this
   layer's existing unit), current year. Belgian customs data via OCCRP/InsightCrime
   reporting ("Stained With Blood," 2025; corroborated by Belga News Agency citing
   customs administrator-general Kristian Vanderwaeren, Jan 2025) -- seizures at
   this specific port tripled 2021-2024, consistent methodology with this layer's
   other seizure-anchored estimates.

2. COUNTERFEIT: strengthened (not replaced) the existing CHN->USA corridor. That
   corridor's $130B value is an OECD/EUIPO *allocation* of the global total against
   provenance shares -- explicitly labeled "not directly reported." US CBP's FY2024
   IPR Seizure Statistics report is a genuinely different, narrower, but directly-
   measured metric (seizure MSRP, not total trade-flow value) -- China alone >$4.1B
   MSRP seized, China+HK = 94% of all US IPR seizure value. Added as a corroborating
   citation in the note, NOT swapped in as the value, since seizure-value and
   estimated-total-flow-value measure genuinely different things and conflating them
   would overstate precision in one direction or understate scale in the other.

NOT added, despite a real, well-sourced figure found -- flagging why rather than
forcing it:
- ARMS: Iran -> Yemen, 750 tons of weapons (missiles, warheads, drone engines),
  intercepted by Yemeni National Resistance Forces, Jul 2025, confirmed Iranian-
  origin (Farsi manuals, manufacturer's quality certificate), referenced in the UN
  Yemen Panel of Experts final report (S/2025/650). This is a real, dated, bilateral
  diversion figure -- but the "arms" layer's unit is "% share of exporter's total
  arms exports (SIPRI TIV)," used uniformly for all 9 existing legal-transfer
  corridors. A 750-TON figure can't be expressed in that same %-share unit without
  either fabricating a denominator (no sourced "total Iranian arms exports" figure
  exists to divide by) or breaking the shared-unit display for this one entry --
  the same structural constraint that already blocked an Iran-Turkey drugs corridor
  last round (fmtMagDisplay reads one unit string for the whole layer, not
  per-corridor). Needs either a per-corridor unit override or a separate illicit-
  diversion sub-layer to ship correctly -- flagging as a real future-work item, not
  silently dropping it.
- WILDLIFE: reconfirmed 0 additions, now against UNODC's actual published
  methodology annex (not just inference) -- the existing corridors' 1-100 index is
  a species-level weighted-price index, not a country-corridor ranking, and UNODC
  has never published a corridor-to-corridor value table. Nigeria->Vietnam has
  strong qualitative evidence but no reconstructable score.
- TRAFFICKING: reconfirmed 8/30 unchanged. Every promising lead (Nigeria->Italy,
  Nepal->India, Moldova->Russia/EU, Myanmar->Thailand) has real narrative
  confirmation but no source publishes a clean bilateral victim count -- national
  totals and k-anonymity-suppressed cells, not corridor-specific figures. One
  unexplored thread flagged for a future pass: UK Home Office's underlying
  nationality-by-outcome NRM data table (not the summary pages) for Vietnam->UK.

Idempotent. Usage: python3 backfill_illicit_round3.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

FIXES = [
    ("drugs: add Ecuador->Belgium (Antwerp) corridor",
     '{"from":"MEX","to":"USA","value":365,"note":"Mexican methamphetamine -> USA; '
     'production estimated ~292-437 t/yr (InsightCrime). No official production '
     'figures published. Estimate."}]',
     '{"from":"MEX","to":"USA","value":365,"note":"Mexican methamphetamine -> USA; '
     'production estimated ~292-437 t/yr (InsightCrime). No official production '
     'figures published. Estimate."},{"from":"ECU","to":"BEL","value":14.6,"note":'
     '"Cocaine via Antwerp; 14.6t seized 2024 traced to Posorja, Ecuador loading '
     'port (port seizures tripled 2021-24). Belgian customs data via OCCRP/'
     'InsightCrime reporting, corroborated by Belga News Agency Jan 2025."}]'),
    ("counterfeit: strengthen CHN->USA note with CBP seizure-data corroboration",
     '{"from":"CHN","to":"USA","value":130000000000,"note":"ESTIMATED. Corridor $ '
     'are allocations of the $467B global total against published provenance '
     'shares (China ~45% of seizures direct). Not directly reported bilateral '
     'figures."}',
     '{"from":"CHN","to":"USA","value":130000000000,"note":"ESTIMATED. Corridor $ '
     'are allocations of the $467B global total against published provenance '
     'shares (China ~45% of seizures direct). Not directly reported bilateral '
     'figures. Corroborating data point (different metric): US CBP FY2024 IPR '
     'seizure statistics show China alone at over $4.1B MSRP seized, China+Hong '
     'Kong together 94% of all US IPR seizure value -- a directly-measured '
     'seizure figure, not the same thing as estimated total trade-flow value."}'),
]

results = []
for label, OLD, NEW in FIXES:
    if NEW in text:
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

print("OK: illicit-route sourcing round 3 applied" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
