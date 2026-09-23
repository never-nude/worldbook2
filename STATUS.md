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

Goal: deploy the approved forensic trail release. Owner: this local Codex session.
Release: [PR #2](https://github.com/never-nude/worldbook2/pull/2) merged to main at `e40ac19819017d592421a7f09b1f9d78df3668c7` on 2026-09-23. Build: `2026-09-23.1 connected-stops`.
Delivery: GitHub Pages deployment [35873358186](https://github.com/never-nude/worldbook2/actions/runs/35873358186) succeeded. The trail is live at https://worldbook.earth/v2/trails.html?trail=duryodhana. The local Git CLI remains unauthenticated; the connected GitHub account handled authorized branch publication and merging.
Validation: root redirect plus all eight runtime files returned HTTP 200 and matched the merged release bytes. Live browser checks passed for the Bangkok chapter and joined junctions, Next to Britain, and Whole trail preserving the selected chapter/URL. The release's 29 tests and prior desktop/phone, syntax, inventory and patch checks remain recorded in docs/VERIFICATION.md; this handoff changes documentation only.
Preservation: original local implementation commits remain on `codex/forensic-trails-local-fb1c19b`. Other computers can fetch main; do not overwrite their unfinished work. Rollback baseline before this release is `bfae443b37e7978b1a11c029c136b8e74d115f01`.
Mirror: required runtime backport is verified on worldbook2-lab main at `0b4d32eb4bea99c076842e999a651a26a8ff3e8c`. Eight runtime files map from canonical `v2/` to mirror root; only the noscript research link uses the absolute production URL. Mirror instructions, launch configuration, other branches and existing PR are preserved.
Open follow-ups: legacy atlas coastline halo, second-browser/real-touch QA, previously unattributed early-load console errors, and the waste case's transfer/arrival/disposal evidence gaps. These were documented before release; no full-atlas factual or accessibility audit is claimed.
Next step: continue the recorded backlog from canonical main. Runtime changes require their own reviewed task branch and verification.

## Unknown / not yet checked

- This task inspected a fresh canonical clone and the local pilot branch. The other computer's checkout and any additional unfinished work have not been inspected.
- Separate Codex conversations and local tasks are not automatically included here.
- This preparation did not perform a fresh browser audit of production behavior.
- Main's recorded July changes do not establish whether newer work exists on either Mac or another branch.

## Next steps

1. The forensic trail release is deployed. Start further work from fetched canonical main and the remaining backlog.
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
