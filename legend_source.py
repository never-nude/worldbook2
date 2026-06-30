#!/usr/bin/env python3
# legend_source.py  --  Worldbook patch (idempotent, pure ASCII)
#
# Surfaces the ACTIVE layer's source directly on its legend, on every viewport.
# A compact "Source: <org>, <year>" line is added to each legend, placed OUTSIDE
# .lg-body so it stays visible even when the legend collapses to a pill on mobile.
# Clicking it opens the existing full "Sources & Methodology" panel.
#
# Touches the three legend builders (drawLegend / drawFlowLegend / drawMigLegend),
# all of which share the exact join `</h3><div class="lg-body">` and all of which
# have `key` in scope. Source text comes from LAYER_PROV[provKeyFor(key)].primarySource,
# falling back to FLOWS[provKeyFor(key)].sources[0] for flow-only layers.
#
# Usage: python3 legend_source.py index.html index.html

import sys

SENTINEL = "function _legendSrc("

CSS = (
    "  #legend .lg-src{font-size:11px;line-height:1.35;color:#9fb0c0;"
    "padding:5px 0 1px;margin-top:3px;cursor:pointer;"
    "border-top:1px solid rgba(255,255,255,.09);letter-spacing:.2px;"
    "white-space:normal}\n"
    "  #legend .lg-src:hover{color:#dce8f4;text-decoration:underline}\n"
)

JSFN = (
    "function _legendSrc(key){\n"
    "  var pv=LAYER_PROV[provKeyFor(key)];\n"
    "  var org=\"\", yr=\"\";\n"
    "  if(pv && pv.primarySource){ org=pv.primarySource.org||\"\"; yr=pv.primarySource.year||\"\"; }\n"
    "  if(!org){\n"
    "    var F=FLOWS[provKeyFor(key)];\n"
    "    if(F && F.sources && F.sources[0]){ org=String(F.sources[0].label||\"\").split(\"\\u2014\")[0].trim(); }\n"
    "  }\n"
    "  if(!org) return \"\";\n"
    "  var txt=\"Source: \"+escapeHTML(org)+(yr?\", \"+escapeHTML(String(yr)):\"\");\n"
    "  return '<div class=\"lg-src\" onclick=\"openSourcesIndex()\" title=\"View all sources and methodology\">'+txt+' \\u2197</div>';\n"
    "}\n"
)

JOIN_OLD = '</h3><div class="lg-body">'
JOIN_NEW = '</h3>${_legendSrc(key)}<div class="lg-body">'


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        t = f.read()

    if SENTINEL in t:
        print("already-applied: legend_source")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(t)
        return

    # 1) CSS before </style>
    i = t.find("</style>")
    if i < 0:
        raise SystemExit("ERROR: </style> not found")
    t = t[:i] + CSS + t[i:]

    # 2) JS helper before drawLegend
    anchor = "function drawLegend(key){"
    j = t.find(anchor)
    if j < 0:
        raise SystemExit("ERROR: drawLegend anchor not found")
    t = t[:j] + JSFN + "\n" + t[j:]

    # 3) inject source line into all three legend innerHTML joins
    n = t.count(JOIN_OLD)
    if n < 1:
        raise SystemExit("ERROR: legend innerHTML join not found")
    t = t.replace(JOIN_OLD, JOIN_NEW)

    with open(dst, "w", encoding="utf-8") as f:
        f.write(t)
    print("applied: legend_source (CSS + helper + %d legend joins)" % n)


if __name__ == "__main__":
    main()
