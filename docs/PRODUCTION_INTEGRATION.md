# Forensic trail integration staging

Prepared and applied locally 2026-09-22. This is an integration note, not a deployment record.

## Checked out state

- Canonical remote: `https://github.com/never-nude/worldbook2.git`.
- Fetched main: `bfae443b37e7978b1a11c029c136b8e74d115f01` (`Add shared Codex instructions and project status (#1)`). A subsequent `git ls-remote` returned the same main SHA.
- Local task branch: `codex/forensic-trails`; no branch with that name was reported by the canonical remote.
- `index.html` is a 441-byte redirect to `/v2/`. The application is `v2/index.html`.
- The Pages workflow publishes the repository root when main changes. A task-branch commit does not itself deploy.
- Reviewed pilot `04f127b9f0a95e2b41ca6dedac19af44fcd637c0` is integrated on the local task branch. Nothing has been pushed or published from this canonical checkout.

## Verified content relationship

Production `v2/index.html` is byte-identical to `index.html` at `b0dc9c9` in the recovered pilot checkout. Both contain 1,644,291 bytes and SHA-256:

`1e0bf2fc2e44624bccb9804efd546cb4fd6333cced689450df96548bd3d4a019`

The final reviewed recovered pilot checkout was pinned to `04f127b9f0a95e2b41ca6dedac19af44fcd637c0` for integration. Its atlas and integrated `v2/index.html` are byte-identical, SHA-256 `3e5b80cc6ab44edb03511017c262ddc90988a3b4de828cc7f83bbf5c3c004b30`. Application files were read from that commit, not copied from a moving working tree.

The production root redirect must be preserved. Whole-repository copying or directly applying the pilot commits to production root paths would put the atlas in the wrong location. The byte-identical application baseline supports a narrowly mapped application delta; it does not establish whole-tree equivalence or Git ancestry between repositories.

## Integration mapping

| Pilot path | Canonical path | Notes |
| --- | --- | --- |
| `index.html` delta from `b0dc9c9` | `v2/index.html` | Reviewed delta applied against verified baseline; `WB_BUILD` is `2026-09-22.1 forensic-trails`. |
| `trails.html` | `v2/trails.html` | Existing relative iframe and atlas links then resolve correctly. Change its noscript research link to `../docs/trails/duryodhana.md`. |
| `css/trails.css` | `v2/css/trails.css` | Relative stylesheet reference remains valid. |
| `js/flow-evidence.js`, `js/trail-model.js`, `js/trail-atlas.js`, `js/trail-reader.js` | `v2/js/` | Relative atlas imports and reader imports remain valid. |
| `data/trails/duryodhana.json` | `v2/data/trails/duryodhana.json` | Reader's relative fetch remains valid. |
| `docs/trails/duryodhana.md` and new evidence/workflow reports | `docs/` | Preserve canonical AGENTS/CLAUDE; reconcile existing workflow/task-spec documents rather than overwriting them. |
| `tests/*.test.cjs` | `tests/` | Adapt paths to `v2/index.html`, `v2/js/`, and `v2/data/trails/`. Update URL fixtures to `/v2/trails.html` where appropriate. |
| `scripts/inventory-research.mjs` | `scripts/inventory-research.mjs` | Make the input and all recorded source locations `v2/index.html`; keep generated audit files under root `data/` and `docs/`. Regenerate after the final atlas/build-label change. |
| `data/research-inventory.json` | `data/research-inventory.json` | Regenerate with the canonical path and final source hash; it is an audit artifact, not reader runtime data. |
| `README.md` delta | `README.md` | Rewrite paths for the canonical tree; do not carry references to absent `almanac.html` or `weekly-landing.html`. |

`source_audit.js` currently reads `index.html` relative to the current working directory. Running it at production root audits the redirect and fails. It can be run from `v2/` as `node ../source_audit.js`, or deliberately updated to accept the actual atlas path. Most old Python patch scripts also predate the `/v2/` layout; inspect their input handling before running them.

## Instructions and remaining checks

Read `AGENTS.md`, `STATUS.md`, `CLAUDE.md`, `docs/WORKFLOW.md`, and `docs/CODEX_TASK_SPEC.md` before integration. The newer AGENTS/CLAUDE branch workflow overrides older direct-main examples. The application-patch convention requires an idempotent pure-ASCII Python patch, syntax verification, and a byte-identical second run.

Preserve analytics, metadata, attribution, existing fallback behavior, the lifted `flow-3d` renderer, and border-containment invariants. Both inspected atlases retain three `gtag(` occurrences and four `og:image` occurrences. The integrated build label is `2026-09-22.1 forensic-trails`.

Border/glow changes require visual checks at North Atlantic z1.8, z2.6, Western Europe z3.6-3.8, Aegean z4.5, Adriatic z5.5, and ZAF/LSO. The country edge must never paint outside its polygon; the locked winding, inset, per-ring/zoom clamps, and round-join invariants remain intact.

Before delivery, test the site from the canonical repository root at `/v2/trails.html`, including direct stop links, JSON/JS/CSS requests, iframe origin messages, attribution, atlas entry, and mobile layout. Run tests with the adapted paths, extract/check inline scripts, regenerate/check the inventory, and inspect the full diff. Update STATUS with actual validation and delivery state.

GitHub authentication was reported unavailable by the parent session; this task neither changed nor attempted credentials. Fetch again before any authorized push, reconcile remote changes, and use the task branch. Do not describe local commits as available on the other computer or deployed. Publishing and any documented post-deploy mirror back-port are separate from this preparation.

## Executed integration checks

- Generated `scripts/apply_forensic_atlas.py`: 5,124 ASCII bytes and 21 changed-code hunks; no full inline data payload. It requires the exact baseline SHA, reconstructs and checks the target SHA, and prints `already-applied` without writing on a target rerun.
- Verified application to a separate output, a byte-identical second run, and refusal of unknown input without changing the target.
- Adapted all four test files; `node --test tests/*.test.cjs` passed 25/25.
- All three nonempty inline atlas scripts and four external scripts passed `node --check`.
- Generated and checked the inventory with `v2/index.html` source locations and final source hash.
- Reproduced the old `source_audit.js` failure on the unmodified baseline: its extractor treated comment apostrophes as string starts. Added comment skipping; `(cd v2 && node ../source_audit.js)` now reports 50 layers, 28 flows, 145 normalized source entries, status `ok`. The same audit also passes on the untouched baseline. These counts describe that legacy audit's narrower scope, not the separate inventory's distinct-URL count.
- Verified root redirect, AGENTS.md, CLAUDE.md, CNAME and Pages workflow remain byte-identical to canonical HEAD; analytics and OG metadata markers remain intact.
- Updated canonical workflow/task brief to the accepted trail direction while preserving task branches, locked borders, inline patch discipline and release verification.

The parent completed canonical-path desktop and phone browser checks, including the root redirect, direct stop URL, bridge, navigation, overview preservation and mobile Globe return. The documented border sequence was inspected; legacy coastline halo remains a follow-up, so this is not a full-atlas containment pass. See VERIFICATION.md. Changes are saved on the local task branch; no push, merge or deployment has occurred.

## Subsequent local correction — 2026-09-23

Integration was saved as `f200a7042801e123450adcf65c27ca3670f0f0e8`. The next local change anchors reader junctions and lifted-line endpoints to the same source coordinates at ground level, replaces offset geographic badges with nearby collision-managed number labels, and keeps all legacy flow geometry defaults. Its guarded incremental patch is `scripts/connect_trail_stops.py`; the build label is `2026-09-23.1 connected-stops`. The original hashes and counts above describe the earlier integration, not this subsequent atlas revision. Current test count is 29 passing; detailed browser and geometry checks are in VERIFICATION.md. Origin main was fetched and remains `bfae443`; no release has occurred.

## Branch publication — 2026-09-23

The user authorized pushing. Local Git lacked credentials, while the connected GitHub account had verified push access. The GitHub connector published application commit `6765cd9ecc7cb2ab350c1edfc1a43b02331b50dc` on `codex/forensic-trails`, with tree `355ff154b0a0865dd67e0add858ded879cd108df` verified byte-for-byte against the tested local snapshot. [Pull request #2](https://github.com/never-nude/worldbook2/pull/2) is open against main. The original local commits remain on `codex/forensic-trails-local-fb1c19b`; the active checkout tracks the published branch. This following documentation-only commit records delivery. No merge, production deployment, or live deployment verification has occurred.

## Production deployment — 2026-09-23

The user authorized deployment. PR #2 merged at `e40ac19819017d592421a7f09b1f9d78df3668c7`; [Deploy Pages run 35873358186](https://github.com/never-nude/worldbook2/actions/runs/35873358186) succeeded. The live root redirect and eight runtime assets match the release bytes, and browser checks verified joined junctions, chapter navigation and overview preservation. Production trail: https://worldbook.earth/v2/trails.html?trail=duryodhana. The preceding local-only statements describe earlier checkpoints; this section records the actual deployment. Rollback baseline remains `bfae443b37e7978b1a11c029c136b8e74d115f01`.

The required mirror backport fast-forwarded worldbook2-lab main from `1b1ae0b7611a6baf9e98842dc88b026e472e0602` to `0b4d32eb4bea99c076842e999a651a26a8ff3e8c`. Eight runtime files map canonical `v2/` to mirror root; only the reader noscript research link is adapted to the absolute production URL. All remote bytes match staged hashes, three inline and four external scripts pass syntax checks, asset paths resolve, and case JSON is valid. Mirror CLAUDE.md, launch configuration, other branches and its existing PR remain unchanged. Canonical development remains in worldbook2.
