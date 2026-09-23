#!/usr/bin/env python3
"""Apply the reviewed forensic atlas delta to the exact canonical baseline.

Usage: python3 scripts/apply_forensic_atlas.py v2/index.html v2/index.html
The companion reader/assets are tracked separately. Unknown input is rejected.
"""
from pathlib import Path
import hashlib
import sys

BASE_SHA = '1e0bf2fc2e44624bccb9804efd546cb4fd6333cced689450df96548bd3d4a019'
TARGET_SHA = '3e5b80cc6ab44edb03511017c262ddc90988a3b4de828cc7f83bbf5c3c004b30'
HUNKS = [(15, 15, '  const _wbReader = _wbParams.get("reader") === "1";\n'), (59, 59, '  if(_wbReader) document.documentElement.classList.add("trail-embed");\n'), (316, 316, '/* Reader-only presentation: retain attribution and make geography readable. */\nhtml.trail-embed body,html.trail-embed #map{background:#07111a}\nhtml.trail-embed #moonCv{display:none!important}\nhtml.trail-embed .maplibregl-control-container{display:block!important}\nhtml.trail-embed .maplibregl-ctrl-top-right,html.trail-embed .maplibregl-ctrl-group{display:none!important}\nhtml.trail-embed .maplibregl-ctrl-bottom-right{bottom:3px!important;right:8px!important}\nhtml.trail-embed .maplibregl-popup{display:none!important}\nhtml.trail-embed .maplibregl-ctrl-attrib{font-size:9px!important;background:transparent!important;color:#a4b4b9!important}\n#trailEntry{color:var(--ink);font-size:12px;text-decoration:none;padding:7px 11px;border:1px solid var(--line);border-radius:9px;background:var(--panel)}\n#trailEntry:hover,#trailEntry:focus-visible{border-color:var(--accent)}\n@media(max-width:700px){#trailEntry{position:fixed;right:10px;top:12px;font-size:11px;padding:6px 8px}#topbar h1 span{display:none}}\n'), (352, 352, '    <a id="trailEntry" href="trails.html">Follow a trail \u2197</a>\n'), (375, 375, '<script src="js/flow-evidence.js"></script>\n<script src="js/trail-model.js?v=4"></script>\n<script src="js/trail-atlas.js?v=4"></script>\n'), (634, 635, 'map.addControl(new maplibregl.AttributionControl({compact:true, customAttribution:_wbReader?"Boundaries: Natural Earth \xb7 Evidence in trail":"Boundaries: Natural Earth \xb7 Data: Sources panel"}),"bottom-right");\n'), (647, 648, 'window.WB_BUILD="2026-09-22.1 forensic-trails";\n'), (1215, 1216, '  simEpoch=Date.now(); simDays=0; paused=_wbReader||window.matchMedia("(prefers-reduced-motion: reduce)").matches; simSpeed=_wbRequestedStory?0.3:0.5; solarDate=new Date();   // weekly stories make one legible turn in about 3m20s; the regular atlas keeps its 2-minute turn\n'), (1506, 1507, '      if((!_wbEmbed||_wbRequestedStory||_wbReader) && (!_wbRequestedCenter||_wbRequestedStory||curatedFlowFocusDismissed||_wbReader) && !subOn && !dragging && (Date.now()-lastInteract>1200)){\n'), (2886, 2886, '  const repaired=FLOW_EVIDENCE.renderTooltip(key,p,{isoName});\n  if(repaired!==null) return repaired;\n'), (3099, 3101, 'function _appendFlow3DLine(out,pts,elevs,w,color,opacity=1){\n  const rgb=_hexRgb(color), alpha=_flowVisibleAlpha(color)*opacity;\n'), (3187, 3187, '  const focusedLegs=Array.isArray(F.focusLegIds)?new Set(F.focusLegIds):null;\n'), (3188, 3188, '    const focusAlpha=focusedLegs&&!focusedLegs.has(e.id)?0.17:1;\n'), (3203, 3204, '        _appendFlow3DLine(line3D,firstPts,firstElevs,e.w/wmax,F.fromColor,focusAlpha);\n'), (3207, 3208, '        _appendFlow3DLine(line3D,secondPts,secondElevs,e.w/wmax,F.toColor,focusAlpha);\n'), (3211, 3212, '      _appendFlow3DLine(line3D,pts,elevs,e.w/wmax,col,focusAlpha);\n'), (3213, 3214, '    if(pts.length) items.push({pts,elevs,nDots:Math.max(5,Math.round(pts.length/6)+Math.round((e.w/wmax)*3)),col,dotCol,two,from:e.from,to:e.to,w:e.w/wmax,i,focusAlpha});\n'), (3231, 3232, '    properties:{n:String(stop.n||""),c:stop.color||F.color},\n'), (3251, 3252, '      const rgb=_hexRgb(dc), alpha=_flowVisibleAlpha(it.two?(i0<it.pts.length/2?F.fromColor:F.toColor):it.col)*it.focusAlpha;\n'), (3546, 3546, 'const FLOW_EVIDENCE = WorldbookFlowEvidence.apply({FLOWS,FLOW_MAG,FLOW_MAG_IDX,LAYER_PROV});\nhydrateSources();\n'), (4201, 4201, 'if(_wbReader) WorldbookTrailAtlas.mount({map,FLOWS,META,setLayer,\n  focusConnections(legIds){ if(flowActive()){ FLOWS[flowKey].focusLegIds=legIds; buildFlowGeo(flowKey); } },\n  pause(value){ paused=!!value; simLast=0; }\n});\n')]


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: apply_forensic_atlas.py INPUT OUTPUT")
    source, target = map(Path, sys.argv[1:])
    original = source.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest == TARGET_SHA:
        print("already-applied")
        return
    if digest != BASE_SHA:
        raise SystemExit("baseline mismatch: refusing to overwrite unrelated atlas changes")
    lines = original.decode("utf-8").splitlines(keepends=True)
    for start, end, replacement in reversed(HUNKS):
        lines[start:end] = [replacement]
    result = "".join(lines).encode("utf-8")
    if hashlib.sha256(result).hexdigest() != TARGET_SHA:
        raise SystemExit("target mismatch: patch verification failed")
    target.write_bytes(result)
    print("applied forensic atlas delta")


if __name__ == "__main__":
    main()
