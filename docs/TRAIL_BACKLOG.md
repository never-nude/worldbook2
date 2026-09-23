# Worldbook migration backlog

Updated 2026-09-22. The first local trail preview is implemented and integrated locally into the canonical repository. Desktop/phone pilot checks and canonical automated checks passed; fresh canonical-path browser checks and publishing are pending.

## First milestone

The existing six-stop Cambodian statue case now has a source-checked evidence packet, normalized content, a globe adapter and a trail reader. Choose two further trails by evidence strength and variety. Do not force incomplete chains to reach a count.

| ID | Work | Status | Evidence / next step |
| --- | --- | --- | --- |
| W01 | Inventory existing research, records and display uses; preserve originals | Complete | [Inventory](RESEARCH_INVENTORY.md), [machine-readable snapshot](../data/research-inventory.json), and reproducible [generator](../scripts/inventory-research.mjs). Includes hidden statue, runtime migration and debt aliases. |
| W02 | Reconcile Shipping Lanes source labels and Drugs quantities/identity | Implemented and tested | [Repair record](FLOW_REPAIRS.md), [adapter](../v2/js/flow-evidence.js), [focused regressions](../tests/flow-evidence.test.cjs). Unsupported drug quantities withheld; source history retained. Drug relationship research and shipping geometry review remain separate follow-up work. |
| W03 | Normalize and source-check the existing statue case | Complete for bounded implementation | [Evidence packet](trails/duryodhana.md) and [six-stop JSON](../v2/data/trails/duryodhana.json) preserve source references, chronology, allegations, settlement qualifications and uncertain geography. A separate primary-source review is complete within the bounded scope; its access limitations and accepted wording correction are recorded in the packet. |
| W04 | Define minimal content format and adapter to the existing globe | Implemented and tested | [Model/adapter](../v2/js/trail-model.js), [atlas bridge](../v2/js/trail-atlas.js), [model tests](../tests/trail-model.test.cjs). Relationship, geometry basis, caveats and source IDs survive conversion. |
| W05 | Build question, itinerary, stop details, evidence, lesson and atlas access | Implemented; local preview checks passed | [Reader entry](../v2/trails.html), [reader code](../v2/js/trail-reader.js), [styles](../v2/css/trails.css). Desktop and 390px/320px layouts, keyboard navigation, motion pause, lesson progression, and direct stop links were checked. See [verification](VERIFICATION.md). |
| W06 | Migrate two further trails with different evidence types | Research started | [Canadian waste-return candidate](trails/NEXT_CANDIDATE.md) establishes a promising branching case; arrival/transfer/disposal records still need targeted verification. Do not present all 69 containers as sharing the two-container Manila leg. |
| W07 | Verify target, prepare release integration and publish within authorized scope | Local integration, automated checks and canonical browser checks complete; auth/publishing pending | [Integration record](PRODUCTION_INTEGRATION.md): reviewed pilot mapped to canonical `v2/`; root redirect preserved; 25 tests pass. Verify access, reconcile remote main, and record any live verification. |
| W08 | Extend contained illumination to legacy atlas layers | Follow-up identified by visual QA | Reader polygon fills remove the inherited coastline bloom. The older Countries treatment still shows halo/spill around Britain and the Aegean in the required zoom sequence. Preserve the locked border invariants when addressing it; do not claim every atlas layer is fixed. |

Codex owns integration and release preparation. Researchers and independent reviewers can work in parallel on nonoverlapping files. Only one worker edits any shared implementation file at a time.

## What the first batch established

The inventory preserves 648 unique stored route records, 203 historical migration corridor records across 52 keyframes, 334 magnitude records, and six explicit stops, all in the statue pilot. These are counts of existing code records, not independently validated journeys. Array-position identifiers and source locations preserve the original research baseline.

| Original issue | Local implementation disposition | Remaining boundary |
| --- | --- | --- |
| Shipping summary claimed IMF/AIS while actual paths were schematic | Source summaries now match route records; retained context figures have metric, period and geographic scope; lines have equal weights | Context for a port or chokepoint does not measure a complete drawn route. Inherited geometry still needs a separate review. |
| Drug estimates appeared as annual corridor quantities | Unsupported quantities are null/withheld; original values and notes remain in the audit | Reinstatement requires an attributable subject, metric, period, scope, method and source locator. |
| Ecuador–Belgium seizure appeared under annual-flow units | Removed from quantitative display and retained with its original note | Direct primary attribution remains unverified; do not promote it to a displayed seizure figure yet. |
| Country-pair magnitude lookup crossed drug substances | Stable subject-aware records and compatibility lookup separate substances; regressions cover collisions | Legacy renderer still uses color as a compatibility subject discriminator until full record-ID extraction. |
| Ownership sequence looked like a physical route | Reader and adapter preserve each connection's relationship, geometry basis and limits; country highlights use one neutral color | Neither numbered stops nor country associations establish an exact shipping itinerary or guilt. |

## DeepSeek participation

The reattached connection was verified by an actual bounded `deepseek-flash` review of supplied material. An accepted finding was that `toFlow` dropped relationship/caveat metadata. The adapter was corrected to preserve relationship, geometry basis, limitations and source IDs, with a focused regression. Country highlighting was also made neutral.

Use DeepSeek for bounded supplied-source extraction, contradiction checks and implementation review. Do not assume independent browsing or treat model agreement as factual corroboration. It does not publish automatically. Primary source checking and independent factual review remain explicit, separate tasks.

## W06 research shortlist

These are starting points from existing inventory records, not ready-to-publish continuous cases:

- **Commodity candidate: Brazil → China soybeans (`food`).** Reuse the existing bilateral corridor and its source references. Identify one supportable chain with meaningful handling or processing stages and an explicit period; do not attach the national total to every stage or infer a particular shipment from trade totals.
- **Illicit candidate: counterfeit goods (`counterfeit`).** Existing records describe Chinese-origin trade, Hong Kong and other transit hubs, and seizure-based evidence. Seek a documented shipment or case with intermediate handoffs. Do not stitch China → Hong Kong and Hong Kong → USA aggregates into one proven journey; retain the distinction between customs provenance and manufacturing origin.
- **Reserve: wildlife trafficking (`wildlife`).** A documented seizure/court case may supply a better evidenced sequence than the existing macro corridors. Establish a specific case before adopting it, and keep seizures, poaching counts and estimated total trafficking separate.

Choose two only after the source review demonstrates continuity and a clear teaching lesson. A waste trail remains a valuable editorial direction, but the current inventory does not justify claiming that a researched waste case already exists.

## Next integration checks

- Canonical `/v2/` desktop/phone browser checks are complete; retain their scope and remaining legacy-glow finding in the release handoff.
- Preserve the qualifications and access limitations recorded in the completed bounded statue review.
- Regenerate the legacy inventory after `v2/index.html` changes so the source hash and locations stay accurate.
- Prepare any release against `never-nude/worldbook2` main, mapping the local atlas and new relative assets into `/v2/` without replacing the root redirect.
- Establish authenticated write access and recheck remote HEAD before publishing; the recorded deployed rollback revision is `bfae443b37e7978b1a11c029c136b8e74d115f01`.

The latest reader emphasizes connections incident to the selected stop using unique stop IDs, while leaving other connections visible as context. Whole trail / Focus stop preserves the chapter and URL. Phone readers can return to the globe from the chapter header. These behaviors have focused regressions in the 25-test suite.

## Defer until the pilot works

Mass catalogue expansion, a general graph editor, a full framework rewrite, mandatory accounts, a separate project-management service, recurring research automation, and mandatory multi-model review of every small change.
