# Worldbook architecture migration

## Legacy baseline

The current production application is a self-contained `index.html` with a MapLibre globe, a Three.js backdrop, UI, 241 geometry features, 49 picker layers, 27 physical flow definitions, migration keyframes, and provenance records embedded together. Historical Python scripts mutate that file by string replacement.

This branch establishes a data-equivalence boundary before changing the renderer. `data/legacy-inventory.v1.json` is an immutable inventory of the legacy data model. It records hashes and human-readable counts for geometry, layer metadata, flows, migration frames, provenance, and intentionally irregular geography.

## Data-model rules that must survive migration

- A map feature is identified by stable `featureId` (`name + geometry hash`), not ISO3 alone.
- Three features intentionally have no ISO3: Somaliland, N. Cyprus, and Siachen Glacier.
- Australia has three geometry features sharing `AUS`; the two territorial specks deliberately remain No Data for country-data layers.
- Migration over time is a first-class layer backed by 52 keyframes, even though legacy code currently injects it at runtime.
- `flow-lines` stays non-visible hit geometry. Visible routes are the lifted `flow-3d` renderer.
- The locked border-containment implementation is not part of this migration surface.

## Transition plan

1. Keep the legacy renderer live while structured snapshots are generated and verified.
2. Promote the generated data assets to validated source data with explicit schemas and provenance manifests.
3. Build the new static application in parallel: base geometry first, then country profiles, numeric/categorical layers, and flows.
4. Switch GitHub Pages from repository-root deployment to validated `dist/` deployment only after visual and data parity pass.

## V2 interaction boundary

The first V2 slice deliberately reuses the proven legacy renderer while replacing its control-led shell:

- Explorer derives its Places, Connections, and reference-map groupings from runtime `META.layers`; it does not hard-code the layer count.
- Country search retains the full feature record and joins camera targets by country name to `COUNTRY_LABELS`. It never treats ISO3 as a unique geometry key.
- Guide, search, Sources, country detail, and the mobile Explorer are mutually coordinated surfaces. Guide, search, and Sources are modal; the country inspector remains non-modal so the map stays usable.
- Modal state controls `inert`, `aria-hidden`, focus trapping, Escape dismissal, and exact-trigger focus restoration together.
- Sources opens on the active layer. The complete methodology catalog remains available behind an explicit disclosure.
- Missing data is announced as “No reported value — not zero.” Reduced-motion users start with globe rotation paused.
- Decorative and off-canvas elements are viewport-contained; document width must equal viewport width at 320, 390, 430, tablet, and desktop sizes.
- Initial load performs no automatic IP geolocation request.

Until the modular renderer reaches parity, the renovated shell is published as an isolated `/v2/` preview. The root site remains byte-identical to production. V2 should stay `noindex,follow` to avoid duplicate indexing while both URLs contain the same underlying reference work.

## Commands

```sh
npm run legacy:inventory
npm run legacy:export
npm run verify:legacy-baseline
npm run verify:data
npm test
```

Only an intentional, reviewed data update may regenerate `data/legacy-inventory.v1.json`.
