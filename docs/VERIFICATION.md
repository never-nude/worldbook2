# Local preview verification — 2026-09-22

The first implementation batch is complete as a local preview. It has not been deployed. This is a bounded pilot, not a factual audit of every atlas layer or a full accessibility certification.

## Automated checks

- All 25 tests pass with `node --test tests/*.test.cjs`.
- All external JavaScript and all three nonempty inline atlas scripts pass `node --check`.
- The regenerated research inventory passes `node scripts/inventory-research.mjs --check`.
- `git diff --check` passes.

Regressions cover substance collisions, unsupported quantities, seizure-versus-flow treatment, source/metric/period alignment, original data preservation, tooltip escaping, invalid evidence references, actual versus displaced coordinates, connection qualification preservation, both iframe startup orders, delayed atlas loading, and message origin/source validation.

## Browser checks

Checked in the Codex in-app browser against a local HTTP server:

- The six-stop reader renders and connects to the existing globe.
- Numbered itinerary selection updates the chapter and shareable stop URL.
- Clicking a numbered globe marker opens its corresponding chapter (tested with stop 3).
- A direct New York stop URL survives reload with the correct chapter.
- Sequential navigation reaches the return chapter, then the lesson; keyboard Enter restarts the trail.
- Rotation is initially paused, can be enabled explicitly, and pauses on selecting a stop.
- Desktop layout uses a scrollable evidence panel with persistent previous/next controls.
- Phone layouts at 390px and 320px keep all six itinerary controls, readable source text, and no horizontal page overflow. Long questions grow above the globe; controls no longer obscure map attribution.
- Existing drug and shipping layers load with revised source summaries, uniform-width explanations, and appropriately qualified descriptions. Tooltip behavior is covered by tests using the actual atlas registries.

The browser console captured intermittent, unattributed `MutationObserver.observe` initialization errors during early loads. No matching observer exists in the repository's reader/atlas source, and the tested flows continued to work. Their origin was not established; this is not a clean-console claim. A second browser and real touch device should be checked during production integration.

## Evidence and review

See [AGENT_REVIEW.md](AGENT_REVIEW.md), the [statue packet](trails/duryodhana.md), and [FLOW_REPAIRS.md](FLOW_REPAIRS.md). DeepSeek participated in a bounded supplied-material review; a separate reviewer checked consequential statue claims against primary records.

## Release boundary

The production repository is `never-nude/worldbook2`, and the atlas is under `v2/`. The restored working checkout's layout and remotes differ. See [DEPLOYMENT_TARGET.md](DEPLOYMENT_TARGET.md) before integration. Authenticated write access is not yet established. Do not publish this checkout's root over the production root redirect.

## Visual refinement after user review

The reader now uses restrained teal polygon fills with a brighter selected country and crisp borders. Reader flows disable the inherited blurred country illumination, which produced spill and faceting at close zoom. Country color stays subordinate to the routes and numbered stops. The atlas's other layer treatments are unchanged.

The reading panel now shares the dark shell, a consistent type hierarchy, sentence-case evidence cards, source/disclosure styling, and navigation buttons. Desktop headings occupy their natural layout height above the globe so close-up geometry cannot paint behind the question. Versioned asset URLs prevent the old panel and map styles remaining in browser caches.

Verified the United Kingdom close-up, selected-country treatment, overview and chapter presentation at 1280×720. All 20 existing tests still pass; no new tests were added for the cosmetic changes.

## Connected-stop interaction

Selecting a stop now emphasizes its incoming and outgoing record connections, with other paths and markers dimmed. Selection uses stop IDs so Cambodian departure and return do not become the same event. Line geometry, source qualifications and weights are unchanged; only displayed opacity varies. The lifted renderer remains responsible for visible lines, and surface hit-test layers remain invisible.

Whole trail / Focus stop preserves the selected chapter, share URL and reading position, including requests made before globe startup completes. A mobile Globe button returns to the map without discarding the chapter. Five additional regressions cover these behaviors and the renderer's geometry/weight preservation. Independent implementation review caught the need to dim marker stroke opacity as well as fill opacity; this is corrected.

Checked the reading panel at 390×844 with no horizontal overflow, mobile Globe return, and Whole trail preserving the Britain chapter and URL. The build label is now `2026-09-22.1 forensic-trails`.

## Canonical integration verification

The reviewed pilot `04f127b9f0a95e2b41ca6dedac19af44fcd637c0` is integrated locally onto canonical main `bfae443b37e7978b1a11c029c136b8e74d115f01`. The atlas and runtime reader assets now live under `v2/`; the root redirect is preserved. All 25 adapted tests, three inline scripts, four external scripts, regenerated inventory, and diff whitespace checks pass. Protected canonical files and analytics/social metadata remain unchanged.

The 21-hunk pure-ASCII inline patch was verified with separate input/output paths, a byte-identical second run, and refusal of unknown input. The legacy source audit initially failed on both baseline and integrated atlas because its extractor did not skip comments. After fixing that tooling defect, it passes on both versions with 50 layers, 28 flows, and 145 normalized source entries. See [integration details](PRODUCTION_INTEGRATION.md).

Fresh canonical-path checks passed at `http://127.0.0.1:8766/v2/trails.html`: JSON/JS/CSS load, the iframe bridge installs the trail, stop selection updates the chapter and URL, Whole trail retains the selected chapter, and Next focuses the next stop. A direct Britain stop URL loads correctly. The root URL redirects to `/v2/`, whose Follow a trail link targets the reader. Attribution remains visible. At 390×844, the document width is 390px, evidence remains readable, and Globe returns focus to the map without changing the stop. Temporary viewport overrides were reset. Desktop review used 1280×720.

The canonical border sequence was inspected on the unchanged Countries treatment using paused embed URLs: North Atlantic at z1.8 and z2.6, Western Europe at z3.7, Aegean at z4.5, Adriatic at z5.5, and ZAF/LSO at z5.5. The Lesotho enclave remains distinct. This is not a blanket containment pass: the legacy glow still shows visible halo/spill around some coastlines, particularly Britain and the Aegean. Reader-specific fills suppress that inherited effect and were separately inspected around Britain. The locked border geometry was not changed. Extending the contained treatment to legacy atlas layers remains a recorded follow-up.

This integration is saved on the local task branch; it is unpublished. Authentication and live deployment verification remain outstanding.

## Joined trail junctions — 2026-09-23

The user identified disconnected-looking connections at close zoom. Two causes were corrected: the reader used displaced geographic badge positions while arcs ended at the evidence coordinates, and the lifted renderer kept its endpoints 21 km above ground. Reader stops now stay at the evidence coordinates, with small junction dots and nearby collision-managed number labels. Reader arcs explicitly reach zero altitude at each endpoint, retaining elevated interiors and using 64 samples per leg for smooth curves. The former badge offsets remain in the source JSON as unused presentation history; they no longer move a reader stop or its line. Source location-precision qualifications remain visible.

All 29 tests pass. New regressions exercise the actual great-circle/elevation/vertex-upload/buildFlowGeo pipeline: every reader endpoint meets its corresponding node at ground level, interior samples remain lifted, the two Cambodian events remain distinct, and old flow sampling, elevations, badge callouts and weights remain unchanged. Click regressions cover label/node priority and exact stop selection. The surface hit-test lines remain invisible.

Browser checks passed around Britain/Belgium and Thailand/Cambodia, including close zoom, dragging the globe to an oblique view, clicking number 1 to open Koh Ker, and whole-trail state preservation. At 390×844, the document width remains 390px, junctions remain connected, and all six itinerary controls remain available. Collision handling can omit an overlapping map number at wide views; its itinerary control remains available. A real touch device was not tested.

The inline change is reproduced from the integrated `f200a70` atlas by `scripts/connect_trail_stops.py`, a seven-hunk ASCII patch with exact input/output hashes. Separate-output application, a byte-identical second run and refusal of unknown input passed. Three inline scripts and all four external scripts pass syntax checks. Inventory verification and diff whitespace checks pass. Build is `2026-09-23.1 connected-stops`; nothing has been published. Country border/glow code is untouched by this fix.

The label placement uses MapLibre's documented [variable anchors and radial offsets](https://maplibre.org/maplibre-style-spec/layers/#text-variable-anchor); geographic junction positions do not change with label placement.

## Production release verification — 2026-09-23

PR #2 merged at `e40ac19819017d592421a7f09b1f9d78df3668c7`. [Deploy Pages run 35873358186](https://github.com/never-nude/worldbook2/actions/runs/35873358186) completed successfully. The root redirect and eight runtime resources (atlas, reader, four scripts, stylesheet and case JSON) all returned HTTP 200 and matched the merged release bytes. Atlas SHA-256: `e95f61d8da4376e9ecd0ed2f7dd6f9be8718afa6dfb60c97086fab63d53cd955`.

The live browser loaded the Bangkok direct link with its joined geographic junctions, source-qualified chapter and visible attribution. Next selected Britain and updated the URL; Whole trail retained that chapter and URL. Build is `2026-09-23.1 connected-stops`. Existing legacy-glow and second-browser/touch-device limits remain as documented above. This subsequent release record changes documentation only, not the tested runtime.
