# Worldbook — A Layered World Map, inside a Live Solar System

An interactive 3D globe that you can spin, zoom, and drill into — sitting inside a real‑time
depiction of the solar system. Built as a single self‑contained `index.html` (no build step
required to run; just open it in a browser).

**Live demo:** `https://worldbook.earth`

---

## What it does

**The Worldbook globe** (MapLibre GL, Natural Earth 50 m geometry)

- 11 toggleable data layers:
  - **Religion (by branch)** — colored by dominant branch (Catholic / Protestant / Orthodox,
    Sunni / Shia / Ibadi, Theravada / Mahayana / Vajrayana, Hinduism, Sikhism, Judaism, etc.)
  - **Government type**, **Regime type** (EIU‑style)
  - **Language family**, **Population density**, **GDP per capita**, **Life expectancy**, **Internet use**
  - **LGBTQ+ legal status**
  - **Satellite imagery** and **Topographic** (Esri raster)
- **Click any country** to open a detail panel: full religious composition, denominational splits,
  politics, at‑a‑glance demographics, official languages, and cited sources.
- **Drill‑downs** into subnational religion for the US, India, Indonesia, Canada, Germany,
  Switzerland, UK, China, Australia and Russia — plus a **US 2024 presidential vote** map by state.
- **Sun‑driven day/night** terminator computed from the Sun's real position.

**The solar system around it** (Three.js)

- The Sun and planets shown as real, sun‑lit spheres at their **real‑time geocentric positions**,
  around the opaque globe (a faint ecliptic line threads through them).
- **Luna** orbits the globe with a visible orbit ring, scaled to the globe's on‑screen size.
- A **play / pause time engine** with a speed slider: planet positions, Earth's spin, the
  day/night terminator and the Moon all advance to the chosen point in time.

---

## Run it

Just open `index.html` in any modern browser. An internet connection is needed for the map
library, the 3D engine, and the satellite/topographic raster tiles (all loaded from CDNs);
the country data itself is baked into the file.

## Data & sources

- **Pew Research Center** — global & US religious composition
- **CIA World Factbook**, **World Bank Open Data** — demographics & economy
- **EIU Democracy Index** — regime classification
- **ILGA World** / **Equaldex** — LGBTQ+ legal status
- National censuses (US/Pew, India 2011, Statistics Indonesia, StatCan, fowid, Swiss FSO,
  ONS/NRS/NISRA, ABS) — subnational religion
- **Natural Earth** — boundaries · **Esri/Maxar** — imagery · **NASA/JPL** — planetary elements

> Data is research‑grade and approximate (rounded, blended from the sources above), intended for
> exploration rather than authoritative reference. Political/regime/LGBTQ+ classifications change
> over time and are simplified.

## Build (optional)

The deliverable `index.html` is generated from sources in `src/` by `node src/build.js`, which
merges curated data with World Bank indicators, world‑countries, and Natural Earth geometry.
Running it is only needed to regenerate the data — not to use the app.

## License

Code © the author. Underlying datasets remain under their respective licenses/terms (see sources).
