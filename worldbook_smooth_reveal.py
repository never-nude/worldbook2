#!/usr/bin/env python3
"""Worldbook: hold the loading screen until EVERYTHING is settled, not just the base
reference layer - trading initial load time for a rock-solid first interaction.

Mike's explicit direction: "i don't care if the page needs twice as long to load at the
beginning, i'd really like one of the main selling points of this site is that it operates
smooth as silk." That's a real priority inversion from how boot currently works, so this
patch changes the actual sequencing, not just cosmetics.

CURRENT (pre-patch) behavior: _reveal() hides the loading spinner and starts the clock/
rotation the MOMENT the base reference style (world/ocean/borders/country-labels/sat/topo)
is idle - then, only AFTER the user can already see and interact with the map, it quietly
adds sunshade, flow layers, cities, and sea-collar in the background (see task #60 history:
this was deliberately built to make first paint fast). That's exactly backwards from what
Mike now wants: a user can start panning/zooming while cities/sea-collar/sunshade are still
being tiled, which is a very plausible contributor to the "looks glitchy right after
interacting" reports (tile gaps, missing labels) - even though this session couldn't pin
that symptom down directly.

NEW behavior: two-phase boot.
  Phase 1 (unchanged trigger: base-style idle or 8s watchdog) now calls _bootHeavyLayers()
  instead of _reveal() directly. This kicks off sunshade/flow-layers/cities/sea-collar/sky
  exactly as before, but the loading spinner STAYS UP and its text changes to "Finishing
  touches..." so it's clear real progress is happening, not that it's silently stuck.
  Phase 2 arms a SECOND idle listener + a 16s watchdog (double the original 8s, matching
  Mike's own "twice as long" framing) that only NOW calls the real _reveal() (hide spinner,
  start the clock). By the time the user ever sees the map, every layer this app ships is
  already tiled and ready - no post-reveal pop-in, no interacting with a half-loaded scene.

Also updates the visibility-resync handler (worldbook_visibility_resync.py, run first) so
regaining tab visibility mid-boot correctly resumes into _bootHeavyLayers rather than
skipping straight to a bare _reveal() that would bypass the heavy layers entirely.

Three small, disjoint edits (not one big replace spanning the huge inline sea-collar
geometry, to keep the diff surgical and low-risk):
  A. Split _reveal's opening: it now only hides the spinner + starts the clock. A new
     _bootHeavyLayers() takes over everything that used to run inside the deferred
     requestAnimationFrame body.
  B. Right after the last deferred-init try/catch (initSky) but still inside that same rAF
     body, arm the phase-2 idle listener + 16s watchdog leading to the real _reveal().
  C. Change the phase-1 watchdog/idle trigger from _reveal to _bootHeavyLayers, and update
     the visibility-resync handler's reveal call site to match.

REQUIRES worldbook_visibility_resync.py to be applied first (edit C's anchor is the
post-visibility-patch text). Idempotent via MARKER. Pure ASCII source.
Usage: python3 worldbook_smooth_reveal.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "/* WB_SMOOTH_REVEAL_V1 */"

A_OLD = ('  const _reveal=()=>{ if(_revealed) return; _revealed=true;\n'
         '    document.getElementById("loading").style.display="none";\n'
         '    startSpin();\n'
         '    requestAnimationFrame(()=>{ try{\n')
A_NEW = (MARKER + '\n'
         '  const _reveal=()=>{ if(_revealed) return; _revealed=true;\n'
         '    document.getElementById("loading").style.display="none";\n'
         '    startSpin();\n'
         '  };\n'
         '  let _heavyBooted=false;\n'
         '  const _bootHeavyLayers=()=>{ if(_heavyBooted) return; _heavyBooted=true;\n'
         '    { const _ld=document.getElementById("loading"); if(_ld) _ld.textContent="Finishing touches\\u2026"; }\n'
         '    requestAnimationFrame(()=>{ try{\n')

B_OLD = ('    try{ initSky(); }catch(e2){ console.error("Atlas deferred init (sky):",e2); }\n'
         '  });\n'
         '  };\n')
B_NEW = ('    try{ initSky(); }catch(e2){ console.error("Atlas deferred init (sky):",e2); }\n'
         '    { let _wbHeavyWD; const _armHeavyWatch=()=>{ if(_revealed) return; clearTimeout(_wbHeavyWD); _wbHeavyWD=setTimeout(_reveal, 16000); };\n'
         '      map.on("data",_armHeavyWatch); map.on("dataloading",_armHeavyWatch); _armHeavyWatch();\n'
         '      map.once("idle", _reveal); }   // phase 2: only reveal once sunshade/flow/cities/sea-collar/sky are ALSO settled - deliberately slower, never shows a half-loaded scene\n'
         '  });\n'
         '  };\n')

C_OLD = ('  { let _wbRevealWD; const _wbArmReveal=()=>{ if(_revealed) return; clearTimeout(_wbRevealWD); _wbRevealWD=setTimeout(_reveal, 8000); };\n'
         '    map.on("data",_wbArmReveal); map.on("dataloading",_wbArmReveal); _wbArmReveal();\n'
         '    map.once("idle", _reveal);\n')
C_NEW = ('  { let _wbRevealWD; const _wbArmReveal=()=>{ if(_heavyBooted) return; clearTimeout(_wbRevealWD); _wbRevealWD=setTimeout(_bootHeavyLayers, 8000); };\n'
         '    map.on("data",_wbArmReveal); map.on("dataloading",_wbArmReveal); _wbArmReveal();\n'
         '    map.once("idle", _bootHeavyLayers);\n')

D_OLD = ('        if(_ld) _ld.textContent = _wbHiddenDuringLoad ? "Building your world\\u2026 (resuming)" : "Building your world\\u2026";\n'
         '        if(map.isStyleLoaded()) _reveal(); else _wbArmReveal();\n')
D_NEW = ('        if(_ld && !_heavyBooted) _ld.textContent = _wbHiddenDuringLoad ? "Building your world\\u2026 (resuming)" : "Building your world\\u2026";\n'
         '        if(map.isStyleLoaded()) _bootHeavyLayers(); else _wbArmReveal();\n')

if MARKER in text:
    status = "already-applied"
else:
    missing = [name for name, old in [("A", A_OLD), ("B", B_OLD), ("C", C_OLD), ("D", D_OLD)] if old not in text]
    if missing:
        status = "ANCHOR-NOT-FOUND (%s) - run worldbook_visibility_resync.py first if D/C missing" % ",".join(missing)
    else:
        text = text.replace(A_OLD, A_NEW, 1)
        text = text.replace(B_OLD, B_NEW, 1)
        text = text.replace(C_OLD, C_NEW, 1)
        text = text.replace(D_OLD, D_NEW, 1)
        status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] smooth reveal: loading screen now stays up until sunshade/flow/cities/sea-collar/sky are ALSO fully settled (not just base style)")
print("OK: smooth reveal shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
