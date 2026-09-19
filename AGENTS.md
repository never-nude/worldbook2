# Worldbook: shared Codex instructions

## Canonical project

Use `never-nude/worldbook2`. Shared integration branch: `main`. Production domain: `worldbook.earth`.
Do not develop in `atlas`, `worldbook`, or `worldbook2-lab`, or copy their files over this repository.

## Start every session

1. Read this file, `STATUS.md`, `CLAUDE.md`, and `docs/WORKFLOW.md` before editing. For layer work also read `docs/CODEX_TASK_SPEC.md`.
2. Inspect the actual checkout: remote URL, current branch, `git status --short --branch`, and recent commits. Fetch origin when available. Compare local and remote history before integrating changes.
3. Preserve uncommitted and unpushed work. Never reset, clean, force-push, automatically stash, or overwrite it to make a checkout match another machine. Fast-forward only a clean branch with its confirmed upstream; otherwise inspect divergence and reconcile safely.
4. Read status from the latest fetched main as well as the current branch when they differ. A local status file can be stale. If offline, explicitly say the shared state could not be checked.
5. Work on a task branch, following the branch-based production workflow in `CLAUDE.md`. Merging main ships through Pages. The older direct-main examples in docs are not a reason to skip the branch workflow.

## Coordinate between devices

- One session owns a task and its commits. Do not independently implement the same task on two computers. Separate concurrent tasks use separate branches.
- Record a known active task, branch, session/device if known, and next step in STATUS.md. Never invent a device name or claim another session is idle.
- STATUS.md is a handoff, not a lock or automatic synchronization service. Fetch before pushing, reconcile concurrent updates, and never force-push over another session.
- Chats, uncommitted files, credentials, dependencies, and machine settings do not synchronize just because these documents exist.

## Preserve project rules

Honor the border-containment invariants, provenance requirements, attribution, analytics, metadata, and rendering constraints in the existing project documents. Inspect current files before trusting older README architecture descriptions. Apply the existing application verification and build-label requirements when changing application code; documentation-only changes do not require changing WB_BUILD.

## Finish every session

Update STATUS.md in the same task branch with a concise handoff: what changed, actual validation, open problems, next step, and whether work is local, pushed, merged, or deployment-verified. Include a known commit reference when useful; do not invent the hash of the commit currently being authored.
Stage only intended files. Push completed work when authorized; use the project's branch workflow. If network or authorization prevents a push, state that other devices do not yet have the work. Never equate a commit, push, or merge with verified production behavior.

## First use on either Mac

Inspect local work before pulling. Confirm this canonical remote, preserve pending changes, fetch, and safely integrate the shared handoff files after their PR is merged. Record any unpushed work discovered and its branch. Initial setup is incomplete until both computers have been checked.
