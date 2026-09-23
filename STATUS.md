# Worldbook shared status

Updated: 2026-09-23. Maintained by Codex sessions alongside the code.

## Shared home

- Canonical repository: https://github.com/never-nude/worldbook2
- Integration branch: main. Production domain configured in CNAME: worldbook.earth.
- Session rules: AGENTS.md, CLAUDE.md, docs/WORKFLOW.md.
- atlas and worldbook are old repositories; worldbook2-lab is a demoted mirror, not a development source.

## Verified repository baseline

Observed main commit before this documentation task: `2b12070b05cd05524770d38ce0d73e842fca8dc9` (2026-07-28), "Deploy the daily layer landing page".
Earlier recorded changes: "Promote v2 as the Worldbook homepage" (2026-07-13), and "Publish renovated Worldbook at /v2" (2026-07-12).
The root contains index.html, v2/, methodology assets, Python patch scripts, and existing workflow documents. README architecture descriptions may predate these changes; inspect the current entry points before application edits.
These are repository observations, not a fresh browser audit or proof of production deployment.

## Current task

Goal: connect the visible trail lines directly through their mapped stop junctions.
Owner: this local Codex session; independent renderer review and parent browser QA are complete. Task branch: `codex/forensic-trails`.
Completed: integrated reviewed pilot `04f127b9f0a95e2b41ca6dedac19af44fcd637c0` onto canonical main `bfae443b37e7978b1a11c029c136b8e74d115f01`. Atlas and runtime assets live under `v2/`; tests, documents, and inventory paths are adapted. Root redirect, AGENTS/CLAUDE, GA4/OG metadata, CNAME, and Pages workflow are preserved. Build label: `2026-09-22.1 forensic-trails`. An exact-hash-guarded ASCII patch reproduces the inline atlas delta. Fixed the legacy source-audit extractor's comment handling after reproducing its failure on the baseline.
Validation: all 25 tests pass; three inline and four external scripts pass syntax checks; inventory regenerated and verified; legacy source audit passes on baseline and integrated atlas; patch separate-output application, byte-identical rerun, and unknown-baseline refusal pass; protected-file/metadata checks and diff whitespace check pass. See `docs/VERIFICATION.md` and `docs/PRODUCTION_INTEGRATION.md`.
Browser validation: canonical `/v2/` reader, direct stop URL, iframe bridge, chapter/overview/Next behavior, root redirect, atlas reader entry, attribution, and 390×844 phone layout checked. The full named border sequence was inspected; the reader's new fill is contained, but the legacy Countries treatment still shows coastline halo and is tracked as W08. DeepSeek completed a bounded continuation review; Next deliberately returns to stop focus.
Open issues: legacy coastline illumination needs a separate repair; second-browser/touch-device QA and unattributed early-load console errors remain recorded in docs/VERIFICATION.md. The local Git CLI is not authenticated; the connected GitHub account has verified repository write access and was used for branch publication. Credentials were not changed.
Latest change: after local integration commit `f200a7042801e123450adcf65c27ca3670f0f0e8`, reader markers now use the same geographic anchors as their incoming/outgoing arcs. Reader arcs meet ground-level junctions and retain lifted interiors; 64 samples smooth long connections. Small junction dots with collision-managed number labels replace the displaced numbered badge callouts. Labels and dots both select the exact stop. Original evidence coordinates, precision caveats, weights and all legacy geometry defaults are preserved. Build: `2026-09-23.1 connected-stops`.
Latest validation: all 29 tests pass, including actual uploaded ribbon/node coincidence and legacy geometry regressions; all inline/external JavaScript syntax checks pass; inventory regenerated/verified; guarded ASCII patch application, byte-identical rerun and unknown-input refusal pass. Browser review covers Britain/Belgium, Thailand/Cambodia at close zoom, globe dragging, map-label selection, whole-trail state and 390px phone layout. Independent implementation review found no blocking issue. Origin was fetched; main remains `bfae443`.
Next step: address legacy illumination and the next trail's evidence gaps, then fetch and reconcile remote changes before any authorized push or release. The line-joining fix is included in pull request #2.
Delivery: published to `origin/codex/forensic-trails` through the authenticated GitHub connector; [pull request #2](https://github.com/never-nude/worldbook2/pull/2) is open. Application commit `6765cd9ecc7cb2ab350c1edfc1a43b02331b50dc` has the exact tested local tree `355ff154b0a0865dd67e0add858ded879cd108df`. The original local commits are preserved on `codex/forensic-trails-local-fb1c19b`; the active branch tracks GitHub. Other computers can fetch the branch. Nothing has been merged or deployment-verified.

## Unknown / not yet checked

- This task inspected a fresh canonical clone and the local pilot branch. The other computer's checkout and any additional unfinished work have not been inspected.
- Separate Codex conversations and local tasks are not automatically included here.
- This preparation did not perform a fresh browser audit of production behavior.
- Main's recorded July changes do not establish whether newer work exists on either Mac or another branch.

## Next steps

1. Complete the local forensic-trail integration and validation described above; the earlier shared-handoff PR is already present in observed main `bfae443`.
2. On the other Mac, inspect its Worldbook checkout, confirm the canonical remote, preserve pending work, fetch, and safely integrate main. Do not blindly pull over local changes or copy one machine's folder over the other.
3. Add any further discovered unfinished work here with its branch, validation, and concrete next step. Reconcile with shared history before resuming implementation.
4. Read this file at session start and update it when handing off a task. Keep one owner per task and push completed handoffs when authorized so other devices can fetch them.

## Handoff format for future updates

Task / owner / branch:
Completed:
Validation performed:
Open issues or blockers:
Next step:
Delivery (local, pushed, merged, deployment verified):
