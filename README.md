# Worldbook

**A teaching forensic trail globe** — follow what moves, what changes hands, and what the records can establish. The existing atlas provides geographic context; the new trail reader walks through sourced connections one stop at a time.

**Live site:** https://worldbook.earth

`v2/trails.html` is the first trail reader: a six-stop Cambodian statue case, with evidence, uncertainty, shareable stops, and a concluding lesson. `v2/index.html` retains the atlas and its existing layer URLs, with a link into the reader. Root `index.html` remains the redirect to `/v2/`. There is no build step. This branch is available in [pull request #2](https://github.com/never-nude/worldbook2/pull/2); it has not been merged or deployed.

The normalized case is in `v2/data/trails/duryodhana.json`; its research packet is in `docs/trails/duryodhana.md`. `v2/js/trail-model.js` validates and adapts the content, `v2/js/trail-atlas.js` connects the existing renderer to the reader, and `v2/js/trail-reader.js` presents the story. Existing drug and shipping display corrections live in `v2/js/flow-evidence.js`; original inline research is preserved.

---

## What it is

Worldbook is a spinnable, zoomable globe (MapLibre GL JS v5.24.0) on a dark-space backdrop. Its initial catalogue carries **49 layers** in two families, plus runtime additions documented in [the inventory](docs/RESEARCH_INVENTORY.md):

- **Choropleth / data layers** — colour each country by a value (religion, GDP per capita, HDI, life expectancy, CO₂ per capita, regime type, …).
- **Flow layers** — animated arcs between country pairs showing cross-border movement (migration, trade, remittances, refugees, drugs, submarine cables, ocean currents, …), sized by a per-edge weight and animated with travelling dots.

Click a country for a detail panel with cited figures; several countries have **subnational drill-downs** (e.g. religion broken down by state/province). A **Sources & Methodology** panel documents each layer's provenance, methodology, confidence and limitations.

### Two data models (both inlined in `v2/index.html`)

- **Choropleth layers** are configured in the **`META.layers`** array (`key, label, group, type, unit, stops/palette`) and coloured from **`MAPDATA`** — a GeoJSON FeatureCollection of 242 country polygons where each feature carries a precomputed **`color_<key>`** property read by `colorExpr`. (The baked colour prop must be named `color_` + the layer key exactly.)
- **Flow layers** live in the **`FLOWS`** object: `label, group, unit, desc, color, dotColor, legend, note, sources[], edges[]`, where each edge is `{from:"ISO3", to:"ISO3", w:<number>}` (plus optional `c:"#hex"` for the multi-substance `drugs` layer). `debtout` / `debtin` reuse the `debt` layer's edge store via `edgesRef`.

---

## Layer catalog (49 layers)

Grouped by their actual `META.layers` group. Data layers show their unit; flow layers (▸) show unit + cited sources.

### Reference
- **Countries** — the default launchpad layer (base political map).

### People & culture
- **Religion (by branch)** — categorical (dominant branch)
- **Language family** — categorical

### Politics & rights
- **Government type** · **Regime type** · **LGBTQ+ legal status** — categorical

### Economy
- **Population density** (people / km²) · **GDP per capita** (US$ current) · **Internet use** (% of population) · **Human Development Index** (0–1 index)

### Debt
- **Govt debt** (% of GDP, gross general govt)
- ▸ **Debt — money lent out** / **Debt — money owed** (US$ billions bilateral) — World Bank International Debt Statistics; AidData Global Chinese Development Finance

### Health
- **Life expectancy** (years) · **Under-5 mortality** (per 1,000 live births) · **Maternal mortality** (per 100,000) · **Physicians / 1,000** · **Health spending** (% GDP) · **HIV prevalence** (% adults 15–49) · **Safe drinking water** (% pop) · **Sanitation access** (% pop)
- ▸ **Medical brain drain** (relative scale, foreign-trained doctors & nurses) — UK NMC register; American Immigration Council; WHO Health Workforce Support & Safeguards List 2023

### Environment & natural systems
- **CO₂ per capita** (t CO₂ / person / yr) · **Climate (Köppen)** — categorical
- ▸ **Ocean currents** (warm/cold, Sverdrups) — NOAA; Meinen et al. 2010; Donohue et al. 2016; Beal et al. 2015; Qiu 2001; Hernández-Guerra et al. 2005; Czeschel et al. 2015
- ▸ **Bird migration flyways** — EAAFP 2023; Wadden Sea Flyway Initiative; CMS Central Asian Flyway; BirdLife; USFWS
- ▸ **Saharan dust** (trans-Atlantic transport) — Yu et al. 2015 (×2); Kok et al. 2021

### Human movement
- ▸ **Migration corridors** (millions, foreign-born stock) — UN DESA International Migrant Stock 2024; UNHCR displacement classification
- ▸ **Remittance corridors** (US$ bn/yr) — World Bank–KNOMAD Bilateral Remittance Matrix; Banco de México
- ▸ **Refugee flows** (forced-displacement corridors) — UNHCR Global Trends / Refugee Data Finder (end-2025)
- ▸ **International students** (enrolled stock) — IIE Open Doors 2024; HESA; Australian Dept of Education; IRCC; JASSO; Campus France

### Trade & resources
- ▸ **Trade flows** (US$ hundreds of billions) — US Census Bureau; UN Comtrade; Australian DFAT
- ▸ **Submarine cables** (intercontinental fibre routes) — TeleGeography; Google Cloud (Dunant)
- ▸ **Oil & gas** — US EIA; China GACC; India DGCI&S; Japan METI; Korea KNOC; UK DUKES; Spain CORES; UN Comtrade (LNG)
- ▸ **Food & grain** (tonnes/yr) — USDA FAS/AMS; FAOSTAT
- ▸ **Minerals & metals** (mixed US$/tonnes) — UN Comtrade; China GACC; USGS; Australia DISR; IEA; UNCTAD; Swiss customs
- ▸ **Timber & wood** (m³ logs/sawnwood, tonnes pulp) — UN Comtrade (HS4403/4407/4703); USDA FAS
- ▸ **Flight corridors** (busiest international air routes) — OAG 2024/2025
- ▸ **Shipping lanes** (lanes & chokepoints) — UNCTAD RMT 2024; EIA World Oil Transit Chokepoints; Panama Canal Authority
- ▸ **Foreign aid flows** (USD millions/year; donor definitions vary) — USAFacts / USAID; JICA; UK FCDO; French Senate / DG Trésor; Devex

### Illicit flows
- ▸ **Drug routes** (by substance) — UNODC World Drug Report 2025; EUDA European Drug Report 2025; UNODC Afghanistan Opium Survey 2023
- ▸ **Arms trafficking** — SIPRI 2024; US GAO-21-322; Small Arms Survey
- ▸ **Human trafficking** (documented victim case records) — CTDC Global Synthetic Dataset; UNODC GLOTIP 2024
- ▸ **Wildlife trafficking** (relative corridor prominence) — South Africa DFFE/SANParks; EIA; UNODC World Wildlife Crime Report 2024
- ▸ **Counterfeit goods** (% share / US$ seized where published) — OECD/EUIPO 2025; EUIPO 2024; US CBP FY2024

### History
- ▸ **Silk Road** — Britannica; UNESCO; Pliny (Perseus/Tufts); Valerie Hansen
- ▸ **Age of Exploration** — Mariners' Museum; Britannica; Royal Museums Greenwich

### Basemap
- **Satellite imagery** · **Topographic** — raster (Esri / ArcGIS World Imagery & Physical)

---

## Data & provenance

The governing principle of this project:

> **Every number traces to a named source; geometry is not fabricated; absence-by-omission is treated as a lie.**

Every flow layer carries a `sources[]` array; every choropleth layer carries full provenance (primary source, methodology, confidence, coverage, limitations) in the in-app **Sources & Methodology** panel (`LAYER_PROV`). Primary providers actually cited across the flow layers include: World Bank (International Debt Statistics, KNOMAD Bilateral Remittance Matrix), AidData, UN DESA, UNHCR, UNESCO/IIE/HESA and national education agencies, US Census & UN Comtrade, US EIA and national energy ministries, USDA/FAOSTAT, USGS, UNCTAD, TeleGeography, OAG, UNODC (World Drug Report, GLOTIP, World Wildlife Crime Report, Afghanistan Opium Survey), EUDA, OECD/EUIPO, US CBP, SIPRI, Small Arms Survey, US GAO, UK NMC, WHO, NOAA, NASA/peer-reviewed oceanography and atmospheric science, CMS, EAAFP, BirdLife, and others. Country-level choropleths draw on the standard authoritative datasets documented per-layer in the Sources panel.

---

## A note on what the arc widths / values mean

Read magnitude **per layer** — it is not one common scale:

- **Quantity-bearing legacy layers** — `migration` (millions of people), `remittances` / `debt` / `trade` (US$ billions), `oil` / `food` / `minerals` / `wood` (volumes, see tooltip), `flights`, `students` (enrolled stock), `currents` (Sverdrups), `dust` (Tg/yr). These have not all received a new record-level audit.
- **Unweighted evidence relationships** — `drugs` now withholds unsupported corridor quantities and distinguishes substances. `shipping` uses equal-width schematic paths with separately scoped port/chokepoint statistics. Neither line width encodes volume. See [repair dispositions](docs/FLOW_REPAIRS.md).
- **Relative corridor prominence, NOT counts** — `wildlife` and `braindrain`. A wider arc = a more prominent corridor in the underlying reports, not a victim count or headcount.
- **Documented case records (a floor, not the true total)** — `trafficking` uses CTDC victim case records, a detection-based undercount.
- **Published seizure share only** — `counterfeit` shows % share or US$ seized where published; muted grey means no published split exists (not zero).
- **Uniform width (encodes nothing)** — `cables` draws all 18 corridors at equal weight; it shows *where* intercontinental fibre runs, not capacity or traffic.
- **Donor-specific definitions** — `aid` combines grants, loans, commitments, and disbursements reported under different national systems; compare individual paths with care.

Don't read the relative, case-record, or uniform layers as measured magnitudes.

---

## Running it

```bash
python3 -m http.server 8000
open http://localhost:8000
```

Open `http://localhost:8000/v2/trails.html` for the reader or `http://localhost:8000/v2/` for the atlas. The root address redirects to the atlas. No `npm install` or build is required. Internet is needed for CDN libraries (MapLibre GL JS v5.24.0, Three.js), map glyphs, and raster tiles. Legacy layer data and country polygons remain inline; the new trail is loaded from JSON.

Focused checks:

```bash
node --test tests/*.test.cjs
node scripts/inventory-research.mjs --check
(cd v2 && node ../source_audit.js)
```

The canonical repository is `never-nude/worldbook2`; task branches integrate through `main`, whose Pages workflow deploys the repository root. Preserve the root redirect and the application under `/v2/`. Read [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), and [WORKFLOW.md](docs/WORKFLOW.md) before changes. Deployment evidence and the rollback revision are recorded in [DEPLOYMENT_TARGET.md](docs/DEPLOYMENT_TARGET.md).

---

## Data pipeline (current state — being migrated)

Layer data is generated and revised by a large set of one-shot **Python scripts in the repo root**. Pass `v2/index.html v2/index.html` explicitly to scripts that accept input and output paths. Each script mutates the atlas in place by string / regex surgery. Broad roles:

- **Layer builders** — `build_layers.py`, `commodities_flows.py`, `illicit_flows.py`, `health_layers.py`, `hdi_layer.py`, the `debt_*.py` set, `enrich_politics.py`, `flows_expand.py`.
- **Backfills / research integration** — `backfill_round2.py`, `backfill_refugees_wood.py`, `backfill_illicit_round3.py`, `condense_sources.py`.
- **Fixes / hardening / UX** — `fix_remit_key_mismatch.py`, `fix_country_labels_hierarchy.py`, `fix_loading_reliability_and_country_labels.py`, `harden_loop.py`, `flow_tooltips.py`, `guide_overlay.py`, and many more.

> ⚠️ **Known fragility:** the editable source of truth and the shipped atlas artifact are the *same* file. A bad regex in any generator can corrupt the only copy of the data, with no clean rollback short of git. This build pattern is slated for a refactor that separates editable data from the shipped `index.html` and replaces in-place HTML surgery with structured writes plus a provenance-validation step. Project docs live in `docs/`.

*(Note: an earlier README described this as "Atlas … inside a Live Solar System" with a `src/build.js` pipeline and a `github.io/atlas/` demo. The name is now Worldbook, the live domain is worldbook.earth, and there is no `src/` build pipeline — the generators above are the real, if transitional, pipeline.)*

---

## License

- **Code** © the author, all rights reserved unless a `LICENSE` file states otherwise.
- **Datasets** remain under the terms of their respective providers (World Bank, UN agencies, FAO, USGS, EIA/IEA, OECD, WHO, TeleGeography, SIPRI, and the many others cited per-layer in the app). Figures are used for visualization; consult each source for authoritative data and reuse terms.
