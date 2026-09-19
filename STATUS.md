# Worldbook shared status

Updated: 2026-09-19. Maintained by Codex sessions alongside the code.

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

Goal: give Codex sessions here and on both computers a shared project handoff.
Owner: this ChatGPT Codex session. Task branch: codex/shared-project-handoff.
Changes: add AGENTS.md session instructions and this status document. No application code changes.
Validation: read repository instructions and recent main history; confirmed the new paths were absent; reviewed documentation scope. No application tests required for this documentation-only task.
Delivery: files pushed on the task branch for integration through a pull request. Check the PR/main before treating this setup as integrated.

## Unknown / not yet checked

- Neither computer's checkout, local branch, uncommitted files, nor unpushed commits has been inspected.
- Separate Codex conversations and local tasks are not automatically included here.
- Current production behavior and application bugs were not audited in this setup task.
- Main's recorded July changes do not establish whether newer work exists on either Mac or another branch.

## Next steps

1. Integrate the handoff PR into main using the existing branch workflow.
2. On each Mac, have Codex inspect its Worldbook checkout, confirm the canonical remote, preserve pending work, fetch, and safely integrate main. Do not blindly pull over local changes or copy one machine's folder over the other.
3. Add any discovered unfinished work here with its branch, validation, and concrete next step. Reconcile with shared history before resuming implementation.
4. Thereafter read this file at session start and update it when handing off a task. Keep one owner per task and push completed handoffs so other devices can fetch them.

## Handoff format for future updates

Task / owner / branch:
Completed:
Validation performed:
Open issues or blockers:
Next step:
Delivery (local, pushed, merged, deployment verified):
