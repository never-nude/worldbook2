#!/usr/bin/env python3
"""worldbook_claude build -- fix "remit" vs "remittances" key mismatch (root-cause version).

Bug: the Remittance Corridors path layer is registered everywhere in the live UI as
FLOWS.remittances / setLayer("remittances"), but its sourced data lives under the
key "remit" in both FLOW_MAG (9 real bilateral $ figures, incl. the world's single
largest remittance corridor, USA -> MEX at $60.5B/yr) and LAYER_PROV (this layer's
metric/methodology/limitations/confidence card).

Effect: FLOW_MAG_IDX["remittances"] and LAYER_PROV["remittances"] are always
undefined, so every remittance-corridor tooltip silently falls back to the generic
"no hard per-corridor figure" line instead of the real cited dollar amount, and its
tooltip "what" description falls back to the terser F.desc instead of the richer
LAYER_PROV metric text.

Correction from an earlier draft of this patch: META.layers ALSO has a shadow entry
for this layer, but keyed "flow_remit" (its `.key`), which buildSourcesIndex used to
resolve into LAYER_PROV via provCard(l.key) -> provKeyFor() stripping the "flow_"
prefix -> "remit". Renaming LAYER_PROV's key without accounting for this would have
silently DELETED the Remittance Corridors card from the Sources & Methodology panel
(it currently renders fine today, pre-fix, purely by accident of the old key still
matching). Root-cause fix instead of a second patch-on-patch: every META.layers
flow-type entry already carries an authoritative `.flowKey` field (used correctly
elsewhere in the file, e.g. setFlow(cfg.flowKey), FLOWS[c.flowKey]) that always
points at the real FLOWS/LAYER_PROV bare key regardless of what `.key` itself is
named. Pointing buildSourcesIndex's provCard() call at `l.flowKey||l.key` instead of
`l.key` fixes this specific case AND makes the Sources panel immune to this entire
class of bug for any future flow-layer renames (confirmed live: all 26 flow-type
META.layers entries already carry a valid, FLOWS-matching .flowKey).

Idempotent. Usage: python3 fix_remit_key_mismatch.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

FIXES = [
    ("FLOW_MAG key",
     '"remit":{"unit":"US$ per year","dataKind":"estimated"',
     '"remittances":{"unit":"US$ per year","dataKind":"estimated"'),
    ("LAYER_PROV key",
     '"remit":{"label":"Remittance corridors"',
     '"remittances":{"label":"Remittance corridors"'),
    ("buildSourcesIndex provCard lookup (root-cause fix)",
     'order.forEach(g=>{ const cards=seen[g].map(l=>provCard(l.key)).filter(Boolean).join("");',
     'order.forEach(g=>{ const cards=seen[g].map(l=>provCard(l.flowKey||l.key)).filter(Boolean).join("");'),
]

results = []
for label, OLD, NEW in FIXES:
    if OLD not in text and NEW in text:
        results.append((label, "already-applied"))
    elif OLD in text:
        text = text.replace(OLD, NEW, 1)
        results.append((label, "patched"))
    else:
        results.append((label, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)

ok = True
for label, status in results:
    print(f"  [{status:>16}] {label}")
    if status not in ("patched", "already-applied"):
        ok = False

print("OK: remittance corridor sourcing fixed, Sources panel unaffected" if ok else "WARN: one or more anchors not found")
sys.exit(0 if ok else 1)
