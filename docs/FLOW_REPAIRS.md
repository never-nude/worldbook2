# Drug and shipping evidence repairs (W02)

Reviewed 2026-09-22. This adapter repairs inconsistent display behavior in the existing atlas. It does not complete the drug-corridor evidence audit or reconstruct shipping itineraries.

## Integration

Load `js/flow-evidence.js` before the main inline atlas script. After all four registries are initialized, including `LAYER_PROV`, call:

```js
const FLOW_EVIDENCE = WorldbookFlowEvidence.apply({
  FLOWS, FLOW_MAG, FLOW_MAG_IDX, LAYER_PROV
});
```

At the beginning of `flowTip(key, p)`, before the legacy `p.amt` or country-pair branches:

```js
const repaired = FLOW_EVIDENCE.renderTooltip(key, p, {isoName});
if (repaired !== null) return repaired;
```

The adapter returns `null` for other layers. It requires no geometry changes: existing feature properties include substance color (`c`) and route name (`nm`). Original edges also receive explicit stable IDs and substance keys. Prefer carrying those IDs and subjects into feature properties during a later renderer extraction; color is only the compatibility adapter for the old renderer.

`FLOW_EVIDENCE.tooltip(...)` returns plain structured metadata for other interfaces. `renderTooltip(...)` escapes content and allows HTTP(S) source links only. `FLOW_EVIDENCE.records` contains the normalized records. `FLOW_EVIDENCE.audit` retains a deep copy of affected legacy flow, magnitude and provenance objects before mutation. Reapplying to the same `FLOWS` object returns the same instance and audit; original evidence is not overwritten.

## Drugs: dispositions

The original live index used only `from>to`. Mexico–USA has both cocaine and synthetic-drug arcs, but both inherited a methamphetamine estimate. Myanmar–Thailand has an opiate arc that inherited a methamphetamine estimate. Afghanistan–Pakistan also has multiple substance categories and needs distinct identities even without an indexed number.

All drug arcs now have equal weights. The replacement magnitude registry has subject-aware IDs and null quantities, with no country-pair aliases. Tooltips ignore legacy `amt` and `wv` fields for this layer; they report an unknown corridor volume and explicitly separate seizures, production and corridor flow. The broader category “synthetics” must not imply a verified quantity for a specific synthetic substance.

The following original entries remain in the source history and `audit.original.drugMagnitudes`; none is presented as a verified annual corridor volume:

| Original pair | Original value | Original unit | Disposition |
|---|---:|---|---|
| COL → USA | 225 | tonnes per year (est.) | Withheld: no attributable bilateral estimation method |
| COL → ESP | 300 | tonnes per year (est.) | Withheld: no attributable bilateral estimation method |
| PER → USA | 60 | tonnes per year (est.) | Withheld: no attributable bilateral estimation method; no matching drawn arc |
| AFG → IRN | 155 | tonnes per year (est.) | Withheld: method, period and scope not verified |
| AFG → TUR | 90 | tonnes per year (est.) | Withheld: method, period and scope not verified; no matching drawn arc |
| AFG → RUS | 40 | tonnes per year (est.) | Withheld: method, period and scope not verified; no matching drawn arc |
| MMR → THA | 120 | tonnes per year (est.) | Withheld: synthetic-drug note conflicted with the drawn opiate arc |
| MMR → AUS | 25 | tonnes per year (est.) | Withheld: attributable corridor estimate not verified |
| MEX → USA | 365 | tonnes per year (est.) | Withheld: production estimate was treated as a corridor quantity and attached to cocaine too |
| ECU → BEL | 14.6 | tonnes per year (est.) | Withheld: note describes a 2024 seizure; direct primary attribution not verified |

No direct primary source was verified for the ECU–BEL seizure in this bounded repair, so it is not retained as a displayed seizure statistic either. Its original value and complete note remain in the audit. The original drug production statistics and weights also remain in `audit.original.drugs`; unrelated global totals are removed from the live layer note instead of implying support for individual arcs.

Existing UNODC/EUDA background links are preserved and identified as layer background, with record-level verification pending. This is a disclosure of the current evidence gap, not a claim that each legacy relationship has been independently verified. Reinstating a number requires a specific substance, metric, unit, observation period, geographic scope, attributable method and source locator. A seizure remains a seizure; an estimate of production remains production.

## Shipping: primary checks and display changes

The live provenance previously said IMF PortWatch traffic density, while the layer contained four editorially drawn paths and route notes pointing to UNCTAD, EIA and Panama Canal reporting. The corrected summary names the sources actually used by the route records. It does not claim a PortWatch import, live feed, traffic-density measurement or observed vessel track.

All four paths are preserved. Their weights are equal, and the legend no longer says that thicker lines mean larger flow. Each popup identifies its number as context for an entire port or chokepoint, with a metric and period; none measures the full drawn route.

| Route | Retained context | Exact scope / locator | Source |
|---|---|---|---|
| Asia–Europe via Malacca + Suez | 22% of global container traffic, in TEU | Suez Canal; table I.8, printed p. 19. The entry does not state a reference year, so the display says “UNCTAD 2024 report,” without assigning a year to the observation. | [UNCTAD Review of Maritime Transport 2024](https://unctad.org/system/files/official-document/rmt2024_en.pdf) |
| Trans-Pacific → US West Coast | 51.506 million TEU, full year 2024 | Shanghai Port across destinations; item 5, “Shanghai Port.” Replaces an undated 50 million milestone. TEU is capacity-equivalent throughput, not a number of distinct boxes or trans-Pacific exports. | [Shanghai Municipal Government, 17 January 2025](https://english.shanghai.gov.cn/en-InFocus/20250117/41d3081fbe6a46a688a742b8b02f5a52.html) |
| Trans-Pacific → Panama Canal | 9,944 deep-draft ship transits, FY2024 | Entire canal, both directions; “Main FY24 Results,” deep-draft transits. Not unique ships or trans-Pacific traffic. | [Panama Canal Authority FY2024 results](https://pancanal.com/en/presents-financial-results-for-fy24-with-a-focus-on-sustainability-and-the-future/) |
| Persian Gulf oil via Hormuz | 20.9 million barrels/day, Q1 2025 | Entire Strait of Hormuz, total oil; table 4, column 1Q25, in the August 2026 data release. EIA estimate based on Vortexa tracking plus analysis. Not all of 2025 and not this particular path. | [EIA Global Energy Security Data](https://www.eia.gov/outlooks/steo/report/energysecurity/article.php) |

The old 2025 Hormuz label did not identify a quarter or half-year. The currently inspected EIA table supports Q1 2025, which is what the new record says; this does not silently reinterpret the old record. The old Panama “~3%” and unverified general note figures remain in the preserved original instead of being mixed into the new route metadata.

The primary UNCTAD PDF's indexed table was accessible in web search; direct document fetch returned 403. The locator above comes from that indexed table. The Panama, Shanghai and EIA content was directly read. All checks were performed 2026-09-22. Future source updates require an explicit record revision, not automatic substitution of the latest number.

## Remaining work

- Complete primary, record-level evidence packets for the drug relationships before introducing quantities or continuous trails.
- Review shipping geometry separately. In particular, the inherited Hormuz path doubles back; it is disclosed as schematic and has not been promoted to an observed itinerary.
- Extract the legacy registries into durable data files once the adapter format has proved itself. The runtime audit and untouched source records preserve the original work in the meantime.
- Other layers and their magnitude issues are outside W02.

## Verification

Run `node --test tests/flow-evidence.test.cjs`.

The focused tests load the actual atlas records and cover both substance collisions, ambiguous-substance fallback, seizure-versus-flow display, equal weights, geometry preservation, source/period/scope consistency, an unknown shipping route, idempotence, unrelated-layer preservation, and tooltip escaping. Browser integration remains the integration owner's responsibility after adding the two hooks.
