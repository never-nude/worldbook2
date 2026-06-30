#!/usr/bin/env python3
"""worldbook_claude build - UI fixes:
 1) the white attribution bubble (bottom-right) -> dark, unobtrusive chip (keeps the Esri
    imagery credit legally intact, just not a white eyesore).
 2) migration-over-time freeze: harden the playback tick so an uncaught error can't kill the
    requestAnimationFrame loop (which looked like a freeze when switching speeds), and reset
    the frame clock on speed change.
Idempotent. Usage: python3 ui_fixes.py index.html index.html"""
import sys
INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

EDITS = [
    # 1) dark attribution
    ("attribution dark",
     "</style>",
     "\n  /* dark, unobtrusive attribution (was a white pill) */\n"
     "  .maplibregl-ctrl-attrib{background:rgba(10,15,25,0.5)!important;border-radius:8px!important;backdrop-filter:blur(6px)}\n"
     "  .maplibregl-ctrl-attrib-inner,.maplibregl-ctrl-attrib a{color:#6b7787!important;font-size:9px!important}\n"
     "  .maplibregl-ctrl-attrib-button{filter:invert(1) brightness(.55)}\n</style>",
     "was a white pill"),
    # 2a) reset frame clock on speed change
    ("speed clock reset",
     "function migSetSpeed(s){ MIG_SPEED=s;",
     "function migSetSpeed(s){ MIG_SPEED=s; MIG_LAST=performance.now();",
     "MIG_SPEED=s; MIG_LAST=performance.now()"),
    # 2b) harden the tick loop against throws
    ("tick hardened",
     'const dt=Math.min(0.1,(t-MIG_LAST)/1000); MIG_LAST=t; let ny=MIG_YEAR+MIG_BASE_YPS*MIG_SPEED*dt; if(ny>=MIG_Y1){ migSetYear(MIG_Y1); migStop(); return; } migSetYear(ny); MIG_RAF=requestAnimationFrame(migTick);',
     'const dt=Math.min(0.1,(t-MIG_LAST)/1000); MIG_LAST=t; try{ let ny=MIG_YEAR+MIG_BASE_YPS*MIG_SPEED*dt; if(ny>=MIG_Y1){ migSetYear(MIG_Y1); migStop(); return; } migSetYear(ny); }catch(err){ if(window.console)console.warn("migTick",err); } MIG_RAF=requestAnimationFrame(migTick);',
     'catch(err){ if(window.console)console.warn("migTick"'),
]

res = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
        res.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new, 1); res.append((name, "patched"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res: print(f"  [{s:>16}] {name}")
print("OK: UI fixes applied" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
