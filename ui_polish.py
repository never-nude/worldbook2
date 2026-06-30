#!/usr/bin/env python3
# ui_polish.py  --  Worldbook patch (idempotent, pure ASCII)
#
# UI cleanup pass:
#   1. Remove the auto-opening intro modal (the guide no longer takes over on
#      first load). The "?" button still opens it on demand.
#   2. De-duplicate sources: drop the in-legend renderSourceBlock() footer and
#      keep ONE always-visible compact "Source: <org> <year>" line (_legendSrc),
#      now with a fallback to the layer's own .sources so no layer loses its
#      attribution. Full source list stays one tap away in the Sources panel.
#   3. Fix the legend/layers overlap on desktop & laptop by capping each panel's
#      height so they cannot collide at any viewport height (both scroll inside).
#   4. Replace the intro's teaching role with a brief, auto-fading interaction
#      hint that is also shown on mobile (touch-aware wording) and gets out of
#      the way after 7s or the first interaction.
#
# Usage: python3 ui_polish.py index.html index.html

import sys

SENTINEL = "function initHint("

# ---- exact edits (old -> new), each must occur exactly once ----------------

EDITS = []

# 1) intro auto-open removal
EDITS.append((
    '  var seen=false; try{ seen=!!localStorage.getItem("wb_seen_guide"); }catch(e){}\n'
    '  if(!seen) setTimeout(openGuide,800);',
    '  /* intro modal no longer auto-opens; discover via labeled controls + hint; reopen with the ? button */'
))

# 2a) _legendSrc fallback to layer config sources (insert before final return)
EDITS.append((
    '    if(F && F.sources && F.sources[0]){ org=String(F.sources[0].label||"").split("\\u2014")[0].trim(); }\n'
    '  }\n'
    '  if(!org) return "";',
    '    if(F && F.sources && F.sources[0]){ org=String(F.sources[0].label||"").split("\\u2014")[0].trim(); }\n'
    '  }\n'
    '  if(!org){ try{ var _cfg=(typeof layerCfg==="function")?layerCfg(key):null;'
    ' if(_cfg && _cfg.sources && _cfg.sources[0]){'
    ' org=(typeof publisherFor==="function")?publisherFor(_cfg.sources[0])'
    ':String(_cfg.sources[0].label||_cfg.sources[0].org||"").split("\\u2014")[0].trim(); } }catch(e){} }\n'
    '  if(!org) return "";'
))

# 2b) remove redundant in-legend sources footer
EDITS.append((
    '  b+=renderSourceBlock(c.sources);',
    '  /* source shown as one always-visible line (_legendSrc); full list lives in the Sources panel */'
))

# 3) desktop panel height caps (no-overlap guarantee)
EDITS.append((
    'max-height:calc(100vh - 340px)',
    'max-height:calc(60vh - 48px)'
))
EDITS.append((
    'max-height:64vh',
    'max-height:calc(38vh - 36px)'
))

# 4a) mobile hint: show + reposition (was display:none)
EDITS.append((
    '#hint{display:none}',
    '#hint{display:block;right:auto;left:50%;transform:translateX(-50%);bottom:auto;'
    'top:calc(116px + env(safe-area-inset-top));max-width:88vw;text-align:center;'
    'font-size:11px;line-height:1.35;pointer-events:none}'
))

# 4b) wire initHint() alongside the existing init calls
EDITS.append((
    '  wireTimeBar(); try{ initGuide(); }catch(e){} updateTimeLabel();',
    '  wireTimeBar(); try{ initGuide(); }catch(e){} try{ initHint(); }catch(e){} updateTimeLabel();'
))

# ---- insertions ------------------------------------------------------------

FADE_CSS = "  #hint.wbfade{opacity:0 !important;pointer-events:none}\n"

INIT_HINT = (
    "function initHint(){\n"
    "  var h=document.getElementById(\"hint\"); if(!h) return;\n"
    "  var touch=(window.matchMedia && window.matchMedia(\"(pointer:coarse)\").matches) || (\"ontouchstart\" in window);\n"
    "  if(touch){ h.textContent=\"Tap a country for details \\u00b7 pinch to zoom \\u00b7 drag to spin \\u00b7 Layers, top-left\"; }\n"
    "  var done=false;\n"
    "  var fade=function(){ if(done) return; done=true; h.classList.add(\"wbfade\");\n"
    "    setTimeout(function(){ if(h) h.style.display=\"none\"; }, 700); };\n"
    "  setTimeout(fade, 7000);\n"
    "  [\"pointerdown\",\"wheel\",\"touchstart\",\"keydown\"].forEach(function(ev){\n"
    "    try{ window.addEventListener(ev, fade, {once:true, passive:true}); }catch(e){ window.addEventListener(ev, fade); }\n"
    "  });\n"
    "}\n"
)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        t = f.read()

    if SENTINEL in t:
        print("already-applied: ui_polish")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(t)
        return

    # apply exact edits
    for i, (old, new) in enumerate(EDITS):
        n = t.count(old)
        if n != 1:
            raise SystemExit("ERROR: edit %d expected 1 match, found %d\n  needle: %r" % (i, n, old[:80]))
        t = t.replace(old, new)

    # insert fade CSS before </style>
    j = t.find("</style>")
    if j < 0:
        raise SystemExit("ERROR: </style> not found")
    t = t[:j] + FADE_CSS + t[j:]

    # insert initHint() before initGuide()
    k = t.find("function initGuide(){")
    if k < 0:
        raise SystemExit("ERROR: initGuide anchor not found")
    t = t[:k] + INIT_HINT + "\n" + t[k:]

    with open(dst, "w", encoding="utf-8") as f:
        f.write(t)
    print("applied: ui_polish (%d edits + 2 inserts)" % len(EDITS))


if __name__ == "__main__":
    main()
