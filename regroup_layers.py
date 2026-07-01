#!/usr/bin/env python3
"""
regroup_layers.py -- rethink the order & grouping of Worldbook's layer picker.

Idempotent, pure-ASCII patch. Reassigns each META.layers[].group field and
reorders the array so the picker (buildLayerUI), the Sources & Methodology
index (buildSourcesIndex), and the guide index (_guideIdx) all render the
new taxonomy -- all three read META.layers[i].group directly and preserve
first-seen order, so this one edit covers all three UI surfaces.

Old taxonomy (15 groups, accreted in build order):
  Belief, Politics, People & economy, Debt, Environment, Rights & society,
  Health, Connections, Illicit flows, Natural systems, Historic routes,
  Infrastructure & travel, Human movement, Resources, Earth view

New taxonomy (12 groups, no singletons, clearer boundaries):
  Reference, People & culture, Politics & rights, Economy, Debt, Health,
  Environment & natural systems, Human movement, Trade & resources,
  Illicit flows, History, Basemap

Usage: python3 regroup_layers.py <in.html> <out.html>
(in == out for an in-place patch)
"""
import sys, json

# key -> new group. Order of this list IS the target picker order, and
# position within a group's run IS the target within-group order.
NEW_ORDER = [
    ("countries", "Reference"),

    ("religion", "People & culture"),
    ("language", "People & culture"),

    ("govtype", "Politics & rights"),
    ("regime", "Politics & rights"),
    ("lgbt", "Politics & rights"),

    ("popdensity", "Economy"),
    ("gdppc", "Economy"),
    ("internet", "Economy"),
    ("hdi", "Economy"),

    ("govdebt", "Debt"),
    ("flow_debtout", "Debt"),
    ("flow_debtin", "Debt"),

    ("lifeexp", "Health"),
    ("under5mort", "Health"),
    ("matmort", "Health"),
    ("physicians", "Health"),
    ("healthspend", "Health"),
    ("hiv", "Health"),
    ("water", "Health"),
    ("sanitation", "Health"),
    ("flow_braindrain", "Health"),

    ("co2pc", "Environment & natural systems"),
    ("climate", "Environment & natural systems"),
    ("flow_currents", "Environment & natural systems"),
    ("flow_flyways", "Environment & natural systems"),
    ("flow_dust", "Environment & natural systems"),

    ("flow_migration", "Human movement"),
    ("flow_remit", "Human movement"),
    ("flow_refugees", "Human movement"),
    ("flow_students", "Human movement"),

    ("flow_trade", "Trade & resources"),
    ("flow_cables", "Trade & resources"),
    ("flow_oil", "Trade & resources"),
    ("flow_food", "Trade & resources"),
    ("flow_minerals", "Trade & resources"),
    ("flow_wood", "Trade & resources"),
    ("flow_flights", "Trade & resources"),
    ("flow_shipping", "Trade & resources"),

    ("flow_drugs", "Illicit flows"),
    ("flow_arms", "Illicit flows"),
    ("flow_trafficking", "Illicit flows"),
    ("flow_wildlife", "Illicit flows"),
    ("flow_counterfeit", "Illicit flows"),

    ("flow_silkroad", "History"),
    ("flow_voyages", "History"),

    ("satellite", "Basemap"),
    ("topo", "Basemap"),
]


def find_meta_span(content):
    start = content.find('META = {')
    if start == -1:
        raise SystemExit("ERROR: 'META = {' not found")
    obj_start = start + len('META = ')
    i = obj_start
    depth = 0
    in_str = False
    esc = False
    end = None
    while i < len(content):
        c = content[i]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        i += 1
    if end is None:
        raise SystemExit("ERROR: could not find matching close brace for META")
    return obj_start, end


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: regroup_layers.py <in.html> <out.html>")
    src, dst = sys.argv[1], sys.argv[2]
    content = open(src, encoding='utf-8').read()

    obj_start, obj_end = find_meta_span(content)
    blob = content[obj_start:obj_end]
    meta = json.loads(blob)
    layers = meta['layers']

    by_key = {l['key']: l for l in layers}
    target_keys = [k for k, _ in NEW_ORDER]

    missing = set(target_keys) - set(by_key)
    extra = set(by_key) - set(target_keys)
    if missing:
        raise SystemExit("ERROR: keys in NEW_ORDER not found in file: %s" % sorted(missing))
    if extra:
        raise SystemExit("ERROR: keys in file not accounted for in NEW_ORDER: %s" % sorted(extra))
    if len(target_keys) != len(layers):
        raise SystemExit("ERROR: count mismatch: NEW_ORDER=%d file=%d" % (len(target_keys), len(layers)))

    new_layers = []
    for key, group in NEW_ORDER:
        l = by_key[key]
        l['group'] = group
        new_layers.append(l)
    meta['layers'] = new_layers

    new_blob = json.dumps(meta, separators=(',', ':'), ensure_ascii=True)
    new_content = content[:obj_start] + new_blob + content[obj_end:]

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(new_content)

    seen = []
    for key, group in NEW_ORDER:
        if not seen or seen[-1] != group:
            seen.append(group)
    sys.stderr.write("OK: %d layers regrouped into %d groups\n" % (len(new_layers), len(seen)))
    sys.stderr.write("Group order: " + " -> ".join(seen) + "\n")


if __name__ == '__main__':
    main()
