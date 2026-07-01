#!/usr/bin/env python3
"""Worldbook: root-cause fix (safety net) for the "map not loading" family of bugs -
tab/document visibility throttling.

MIKE'S ASK THIS ROUND: "we really need to go through this from the foundation up... it's
on shaky ground... i just want this problem dealt with once and for all... we're going to
chase it until we find the source." This patch is the direct result of that chase.

WHAT WAS FOUND (live, instrumented, not guessed): opened fresh tabs via Chrome-MCP
automation and polled real map/document state over time. Confirmed repeatedly:
  - document.hidden === true / document.visibilityState === "hidden" for the ENTIRE
    lifetime of an automation-controlled tab (this is a real, structural fact about how
    that harness's tabs are displayed, not something that flips based on clicks).
  - While hidden, map.isStyleLoaded() stayed FALSE for 44 seconds, then 170 seconds, in
    two separate fresh loads of the SAME page - with map.style.sourceCaches completely
    EMPTY (no "world", "cities", "country-labels" sources registered at all) for the first
    44+ seconds. Only 4 network resources total loaded in that whole window (three.js,
    maplibre-gl.js/.css, ipwho.is) - i.e. MapLibre's own internal style/source pipeline had
    made almost no progress, not a network-fetch bottleneck.
  - The SAME page, in the SAME tab, eventually finished perfectly (correct pastel fills,
    borders, labels, working panel) without any code change - just more wall-clock time
    passing while still hidden the whole time.
  - grep of the live production file: zero occurrences of "visibilitychange" anywhere.
    The app has no awareness of tab visibility at all today.

CONCLUSION: Chrome (and every other modern browser) aggressively throttles
requestAnimationFrame and timers in hidden/backgrounded tabs. MapLibre's internal load
pipeline (and this app's own reveal watchdog / auto-rotation / sunshade loop) all depend on
rAF and setTimeout. A tab that's open but not the active, visible one - which happens to
EVERY automated test tab in this harness, and very plausibly happens for Mike too anytime
he opens the link and alt-tabs away "while it loads" - can stretch a normal few-second boot
into 44, 90, 170+ seconds. This is standard browser behavior, not a Worldbook logic bug -
but the app currently does nothing to detect it, explain it, or recover quickly from it.

This does NOT claim to be the only remaining contributor (Mike's two screenshots this round
showed a DIFFERENT symptom - a completed-but-glitchy render with a tile gap + missing
country labels after zoom - which this session could NOT reproduce on demand, consistent
with it being real but rarer; see worldbook-freeze-repro.md memory for the still-open
thread on that one). This patch fixes the visibility-throttling mechanism specifically,
which is real, proven, and independent of that other open question.

THE FIX (three parts, all inside the existing reveal-watchdog block so they share scope):
  1. If the tab goes hidden WHILE still loading, immediately rewrite the loading message to
     say so ("...paused - tab is in background") instead of leaving a generic message that
     looks identically "stuck" whether it's paused-and-fine or actually broken. Directly
     answers Mike's "if it does happen again we'll be prepared."
  2. The moment the tab becomes visible again, force map.resize() defensively (cheap,
     idempotent - guards against any layout/canvas-size desync that accrued while hidden,
     the same class of GL-state-desync bug already found once this project in the Moon-
     occluder fix).
  3. On that same visibility-regain moment, if the style has actually finished loading in
     the background (map.isStyleLoaded() true) but the reveal never fired because the idle/
     data events that would have triggered it were themselves throttled, reveal immediately
     rather than waiting on a possibly-still-throttled timer queue to catch up on its own.
     Otherwise, re-arm a fresh 8s watchdog from NOW (not from whenever it was last touched
     while hidden), so a long hidden period never counts against the "give up" timer.

Idempotent via MARKER sentinel. Pure ASCII source (unicode chars written as \\uXXXX escapes
so they survive as correct escapes in the shipped file). Composes cleanly with every other
pending/deployed patch - single anchor inside the existing watchdog block, no overlap.
Usage: python3 worldbook_visibility_resync.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "/* WB_VISIBILITY_RESYNC_V1 */"

OLD = ('    map.on("data",_wbArmReveal); map.on("dataloading",_wbArmReveal); _wbArmReveal();\n'
       '    map.once("idle", _reveal); }   // ironclad+dynamic: re-arms an 8s last-resort timer on every style/source/tile')

NEW = ('    map.on("data",_wbArmReveal); map.on("dataloading",_wbArmReveal); _wbArmReveal();\n'
       '    map.once("idle", _reveal);\n'
       '    ' + MARKER + '\n'
       '    let _wbHiddenDuringLoad=false;\n'
       '    document.addEventListener("visibilitychange", ()=>{\n'
       '      if(document.hidden){\n'
       '        if(!_revealed){ _wbHiddenDuringLoad=true;\n'
       '          const _ld=document.getElementById("loading"); if(_ld) _ld.textContent="Building your world\\u2026 (paused \\u2014 tab is in background)"; }\n'
       '        return;\n'
       '      }\n'
       '      try{ map.resize(); }catch(e){}\n'
       '      if(!_revealed){\n'
       '        const _ld=document.getElementById("loading");\n'
       '        if(_ld) _ld.textContent = _wbHiddenDuringLoad ? "Building your world\\u2026 (resuming)" : "Building your world\\u2026";\n'
       '        if(map.isStyleLoaded()) _reveal(); else _wbArmReveal();\n'
       '      }\n'
       '    });\n'
       '    }   // ironclad+dynamic: re-arms an 8s last-resort timer on every style/source/tile; visibility-aware (see WB_VISIBILITY_RESYNC_V1)')

if MARKER in text:
    status = "already-applied"
elif OLD not in text:
    status = "ANCHOR-NOT-FOUND (reveal watchdog block)"
else:
    text = text.replace(OLD, NEW, 1)
    status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] visibility-change resync: honest paused-message + resize() + immediate reveal-check on tab regaining visibility")
print("OK: visibility resync shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
