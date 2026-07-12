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

## Commands

```sh
npm run legacy:inventory
npm run legacy:export
npm run verify:legacy-baseline
npm run verify:data
npm test
```

Only an intentional, reviewed data update may regenerate `data/legacy-inventory.v1.json`.
