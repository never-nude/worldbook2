# Worldbook implementation brief

Read [AGENTS.md](../AGENTS.md), [CLAUDE.md](../CLAUDE.md), [STATUS.md](../STATUS.md), [WORKFLOW.md](WORKFLOW.md), and the relevant [backlog item](TRAIL_BACKLOG.md). Canonical repository: `never-nude/worldbook2`. Work on task branches; merging `main` ships through Pages. Older direct-main examples do not apply.

## Before editing

- Check worktree, branch, and user changes. Preserve unrelated work.
- Define the bounded outcome and files owned by this task.
- Reuse existing research and renderer capabilities before introducing replacements.
- Read the evidence packet for content changes. Existing citations and model-generated figures are not automatically verified.

## Implement

- Use a task branch; use an isolated worktree when implementation runs alongside another writer. One integration owner decides what lands. Fetch and compare main before integrating, preserving existing work.
- The atlas is `v2/index.html`; root `index.html` redirects to `/v2/`. Put reader/runtime assets under `v2/`; preserve the redirect. Separate content from rendering incrementally, with a compatibility adapter. Do not run historical patch scripts indiscriminately.
- Deliver inline atlas changes as an idempotent pure-ASCII Python patch with an exact baseline guard. New external files are normal tracked assets. Bump `window.WB_BUILD` on application changes and preserve GA4, social metadata, attribution and runtime fallbacks.
- Keep stop order, relationship semantics, subject identity, dates, and measurement scope explicit.
- Derive tooltips, legends, and source summaries from the same records.
- Preserve map attribution and the distinction between lifted visible ribbons and invisible surface hit-test geometry.

## Verify and hand off

- Run relevant syntax/build checks and focused data/interaction checks. Test desktop and phone layouts for UI work.
- Add regressions for substantive defects, not tests that merely mirror the implementation.
- Prove the inline patch's second run is byte-identical; reject unexpected baselines. Extract inline scripts and run `node --check`; run relevant external syntax and regression checks.
- Keep the locked border-containment invariants in CLAUDE.md. Border/glow work requires its documented North Atlantic, Western Europe, Aegean, Adriatic, and ZAF/LSO checks.
- Test canonical `/v2/` URLs and runtime asset paths, then update STATUS.md with actual validation, blockers, and delivery state. Stage only intended files.
- Report changes, evidence corrections, checks, gaps, and preview/revision.
- Verify deployment target and rollback before release; follow the user's release authorization, not old boilerplate.

For research-only work, use [TRAIL_RESEARCH_TEMPLATE.md](TRAIL_RESEARCH_TEMPLATE.md) and do not change production data.
