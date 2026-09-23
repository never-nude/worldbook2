# Worldbook working agreement

Updated 2026-09-22 for the forensic trail direction and local integration into the canonical repository. Follow AGENTS.md and CLAUDE.md: work on task branches; merging main ships to production. This agreement replaces older automatic direct-main examples while retaining the canonical rendering, provenance, and verification rules. No production release is claimed here.

## Product direction

Worldbook is a teaching forensic trail globe: where things come from, where they go, and what happens along the way. Follow goods, people, money, drugs, waste, resources, and information through meaningful stops. Investigate hidden connections, especially where legitimate and illicit systems intersect. Trails lead; static maps provide optional context.

Preserve existing research and useful globe rendering. Redesign the trail reader and separate content from rendering incrementally. A trail does not require a numerical volume; a relationship is not automatically a physical itinerary.

## Ownership and parallel work

- Codex owns the backlog, implementation, integration, verification, and release preparation.
- Research helpers produce an evidence packet for one trail or a small named set of claims.
- An independent reviewer challenges sources, units, chronology, inferred connections, and usability. Claude can fill this role when available; native subagents can do it without manual handoffs.
- DeepSeek is reattached and verified: a bounded `deepseek-flash` review ran against supplied implementation/evidence material. Use it for supplied-source extraction, contradiction checks and independent code review. Do not assume it browsed or independently checked primary sources; model agreement is not evidence. DeepSeek has no automatic publishing role.
- Run independent research and review in parallel. Keep one implementation task active per shared file. Helpers implementing changes need isolated worktrees or explicit nonoverlapping files. Only the integration owner publishes.
- Give each helper the question, relevant files/excerpts, expected output, exclusions, and stopping condition. Avoid whole-conversation handoffs, duplicate audits, retry loops, and mandatory multi-model review of every small change.
- The user sets editorial direction and reviews meaningful milestones. Routine research, local fixes, and reversible implementation proceed within the accepted scope.

## Shared files

- [TRAIL_BACKLOG.md](TRAIL_BACKLOG.md): queued work, dependencies, findings, and completion evidence.
- [TRAIL_RESEARCH_TEMPLATE.md](TRAIL_RESEARCH_TEMPLATE.md): one handoff format for researchers.
- [CODEX_TASK_SPEC.md](CODEX_TASK_SPEC.md): implementation brief.
- [RESEARCH_INVENTORY.md](RESEARCH_INVENTORY.md) and [research-inventory.json](../data/research-inventory.json): preserved legacy records, source locations, counts and provisional dispositions.
- [FLOW_REPAIRS.md](FLOW_REPAIRS.md): shipping/drugs corrections, primary checks and remaining evidence gaps.
- [Duryodhana evidence packet](trails/duryodhana.md) and [normalized JSON](../v2/data/trails/duryodhana.json): the source-checked six-stop pilot and its qualifications.
- [Trail model/adapter](../v2/js/trail-model.js), [reader](../v2/js/trail-reader.js), [atlas bridge](../v2/js/trail-atlas.js) and [preview entry](../v2/trails.html): the first implementation.
- [DEPLOYMENT_TARGET.md](DEPLOYMENT_TARGET.md): verified production repository, path, deployed revision and release constraints.

Create a packet at `docs/trails/<trail-id>.md` when an investigation starts and normalized content at `v2/data/trails/<trail-id>.json`. Use the pilot format before introducing more infrastructure. No additional project-management service is needed now.

## Current local milestone

The preservation inventory, shipping/drugs display repair, source-checked six-stop statue JSON, renderer adapter and first trail reader are implemented. The reader passed the bounded desktop/phone interaction checks recorded in [VERIFICATION.md](VERIFICATION.md). Drug corridor quantities remain unknown where source scope or method cannot support them; display consistency does not mean the drug evidence audit is complete.

DeepSeek's bounded review identified that `toFlow` dropped relationship/caveat metadata. The adapter now preserves each leg's relationship, geometry basis, limitations and source IDs, including qualifications in the legacy popup text. Country highlights use one neutral color to avoid suggesting country-level guilt or evidence status. [Focused model tests](../tests/trail-model.test.cjs) cover the preservation defect. This accepted review is a concrete implementation check, not independent corroboration of the underlying court records.

The [statue packet](trails/duryodhana.md) records completed source checking and a separate bounded primary-source review. The review corrected whose legal title the settlement described, while retaining explicit limits on transport geography and present-day museum status.

## Work loop

1. **Inventory and reuse.** Preserve original record IDs, values, citations, and caveats. Classify material as reusable, needing reconciliation, needing more evidence, or historical context. Do not re-research everything up front.
2. **Prepare one trail.** Write its question, ordered stops/branches, claims, quantities, sources, and gaps. A-to-B plus B-to-C requires evidence of continuity before becoming one journey.
3. **Review evidence.** Check the actual source, observation period, scope, and relevant passage/table. Concentrate independent review on new, disputed, transformed, or magnitude-bearing claims. Model agreement is not corroboration.
4. **Integrate incrementally.** Introduce a normalized content format with an adapter to the existing renderer. Prove one complete case before scaling. Preserve existing atlas behavior and URLs while testing.
5. **Verify the teaching experience.** Readers can identify the question, follow stops, inspect evidence, explain the lesson, and distinguish facts from interpretation. Check desktop/phone layouts, keyboard access, pause/reduced motion, and shareable state.
6. **Prepare and release a coherent change.** Record the tested revision, deployment target, and rollback point. Publish within the user's authorized scope after target verification; these documents do not themselves authorize automatic deployment. Verify live behavior after a release.

## Evidence and display rules

- Separate route geometry, claims/evidence, and measurements. Every displayed claim and connection points to its supporting source.
- Give each quantity its own metric, unit, subject/substance, period, geographic scope, method, and source locator. Separate seizures, production, stocks, annual flows, capacity, value, and case counts.
- Unknown is `null`, not zero or an invented estimate. An estimate needs an attributable method and scope; '(est.)' alone is insufficient.
- Compare widths only for compatible measurements. Otherwise use unweighted lines. Animation indicates direction unless a calibrated rate is supported.
- Distinguish observed geography, reported waypoints, schematic relationships, and uncertain links. Ownership chronology must not imply a reconstructed shipping route.
- Distinguish allegations, findings, settlements, and established events. A country's appearance in a case does not establish guilt.
- Generate legends, tooltips, and source summaries from the same records. Use stable subject-aware record IDs; country pair alone is insufficient.
- Preserve superseded research with its disposition rather than silently deleting or validating it.

## Proportional verification

Check relevant syntax/build and affected interactions. Add focused regressions for substantive defects: substance collisions, seizure-versus-flow units, missing evidence, invalid stop references, and source inconsistencies. For inline atlas changes, provide an idempotent pure-ASCII Python patch targeting `v2/index.html`; verify a byte-identical second run. New external data, reader code, and styles are tracked as normal files. Documentation-only changes need content/link checks, not application tests.

Preserve map attribution and existing lifted flow geometry unless a replacement is explicitly under test. Do not accidentally make invisible surface hit-test layers visible.

## Canonical checkout and release workflow

- Canonical repository: **`never-nude/worldbook2`**; integration branch: **`main`**. Do not develop in archived repositories or treat recovered remotes as deployment authority.
- Root `index.html` redirects to `/v2/`; the atlas is `v2/index.html`. Reader, scripts, styles, and runtime JSON live under `v2/`. Documentation, tests, and audit tooling live at repository root.
- Read AGENTS.md, STATUS.md and CLAUDE.md before work; inspect branch, remote, status and recent commits, then fetch when available. Preserve unrelated local and unpushed work. Never reset, clean, force-push, or automatically stash it.
- Use one task branch and one integration owner per change. Read the latest fetched main status before reconciling. Push completed work only within the user's authorization; use a reviewed branch integration, never the old automatic direct-main command.
- Any application release updates `window.WB_BUILD` in `v2/index.html`. Preserve GA4/gtag, social metadata, attribution and runtime fallbacks. The root redirect is not the application build-label endpoint.
- Verify the live application at `https://worldbook.earth/v2/` after an authorized release. A local commit, branch push or merge is not proof of successful production behavior. Record actual delivery and verification in STATUS.md.
- The observed rollback reference is `bfae443b37e7978b1a11c029c136b8e74d115f01`. Its atlas matched the recovered pilot baseline byte-for-byte; the application delta was mapped into this canonical tree, preserving the root redirect. Historical verification evidence is in [DEPLOYMENT_TARGET.md](DEPLOYMENT_TARGET.md); integration details are in [PRODUCTION_INTEGRATION.md](PRODUCTION_INTEGRATION.md).

## Locked rendering requirements

A country's edge color must never paint outside its own borders at any zoom. Preserve the canonical winding normalization, inset offset of width/2, per-ring and low-zoom size clamps, and round joins/caps documented in CLAUDE.md. Reader illumination uses contained polygon fills; it does not relax those invariants.

When border/glow rendering changes, verify North Atlantic coastlines at z1.8 and z2.6, Western Europe at z3.6-3.8, the Aegean at z4.5, the Adriatic at z5.5, and the ZAF/LSO enclave. Visible flow geometry remains the lifted `flow-3d` ribbons; surface `flow-lines` and `flow-dots` stay invisible for hit testing. Keep required map attribution visible.

The reviewed inline delta is reproducible with `python3 scripts/apply_forensic_atlas.py v2/index.html v2/index.html`. The patch accepts only its exact baseline, rejects unrelated content, and prints `already-applied` for its verified target. Do not reuse that fixed patch on a later unknown atlas revision.

The subsequent connected-stop correction is `python3 scripts/connect_trail_stops.py v2/index.html v2/index.html`, starting from the atlas at `f200a70` (the first patch's target). Apply these patches in order only when reconstructing those exact historical revisions; ordinary development uses the tracked current files.

Current delivery remains on the local task branch. Canonical-path desktop/phone checks are recorded in VERIFICATION.md; legacy coastline glow still needs follow-up. Authenticated release work is pending. The other computer does not yet have these changes.
