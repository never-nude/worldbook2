#!/usr/bin/env python3
"""Worldbook: three corrections to the previous deploy, per Mike's review.

1) GLOSS REMOVED. Mike reviewed the glossy classroom-globe sheen live and
   rejected it - reverting glossHi (div, CSS, _wbUpdateGloss, and its call
   site in renderSky()) back out cleanly, byte-for-byte undoing the earlier
   worldbook_glossy_globe.py patch.

2) TIME DEFAULT CORRECTED: 24 sim-hours per real minute, not literal 1x.
   Literal real-time (what shipped last round) makes the globe look frozen -
   nothing you'd actually see move on a human timescale. Mike's real ask:
   a full simulated day should pass every real minute. In the app's own
   units (simSpeed = sim-days per real-minute) that is simply simSpeed=1
   (1440x on the old multiplier scale the speed slider uses). Boot default,
   the slider's initial position/label, and the "Now" button's reset target
   all updated together so they stay consistent with each other.

3) GEO-PING NOW FULLY DISAPPEARS. Last round only stopped the pulsing RING
   from looping - the solid dot marker itself stayed on the map forever.
   Mike wants the whole marker (dot, ring, and its popup) to fade out and be
   removed a moment after the single ping, not persist as a permanent
   fixture. Ring still pulses once (2.4s), holds briefly, then the whole
   marker fades over 0.6s and is removed from the map (~3.4s total
   lifetime).

Idempotent, pure ASCII source.
Usage: python3 worldbook_followup_fixes.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

DASH = "—"   # em dash, appears inside an existing title attribute we touch

EDITS = []

# ---- 1a. remove the glossHi div ----
old1 = (
    '<canvas id="sky"></canvas>\n'
    '<canvas id="moonCv"></canvas>\n'
    '<div id="glossHi"></div>\n'
    '<div id="skyTip"></div>'
)
new1 = (
    '<canvas id="sky"></canvas>\n'
    '<canvas id="moonCv"></canvas>\n'
    '<div id="skyTip"></div>'
)
EDITS.append(("remove glossHi div", old1, new1, new1))

# ---- 1b. remove the glossHi CSS rule ----
old2 = (
    '#moonCv{position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;pointer-events:none}\n'
    '  #glossHi{position:absolute;top:0;left:0;width:100%;height:100%;z-index:3;pointer-events:none}'
)
new2 = (
    '#moonCv{position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;pointer-events:none}'
)
EDITS.append(("remove glossHi CSS", old2, new2, new2))

# ---- 1c. remove the _wbUpdateGloss helper ----
old3 = (
    '// classroom-globe gloss: a soft off-center highlight (overhead-light sheen on the\n'
    '// laminate) plus a faint dark vignette right at the sphere\'s true limb. Positioned\n'
    '// from the globe\'s real projected center/radius, so it tracks zoom and pan exactly.\n'
    'function _wbUpdateGloss(cx,cy,r){\n'
    '  const el=document.getElementById("glossHi"); if(!el) return;\n'
    '  if(!r || !isFinite(r)){ el.style.background="none"; return; }\n'
    '  const hx=cx-r*0.32, hy=cy-r*0.38;\n'
    '  el.style.background=\n'
    '    "radial-gradient(circle at "+hx+"px "+hy+"px, rgba(255,255,255,.55) 0%, rgba(255,255,255,.26) 16%, rgba(255,255,255,.08) 38%, rgba(255,255,255,0) 65%),"+\n'
    '    "radial-gradient(circle at "+cx+"px "+cy+"px, rgba(5,10,20,0) 76%, rgba(5,10,20,.10) 90%, rgba(5,10,20,.24) 100%)";\n'
    '}\n'
    'function renderSky(){\n'
    '  requestAnimationFrame(renderSky);'
)
new3 = (
    'function renderSky(){\n'
    '  requestAnimationFrame(renderSky);'
)
EDITS.append(("remove _wbUpdateGloss helper", old3, new3, new3))

# ---- 1d. remove the call site ----
old4 = '    if(mx>2) gpx=mx; _wbUpdateGloss(c0.x,c0.y,gpx); }catch(e){}'
new4 = '    if(mx>2) gpx=mx; }catch(e){}'
EDITS.append(("remove gloss call site", old4, new4, new4))

# ---- 2a. boot default: 1x real-time -> 24 sim-hours/real-minute (simSpeed=1) ----
old5 = (
    'simEpoch=Date.now(); simDays=0; paused=false; simSpeed=1/1440; solarDate=new Date();'
    '   // default = real time (1x); rate and date both remain fully manual after this'
)
new5 = (
    'simEpoch=Date.now(); simDays=0; paused=false; simSpeed=1; solarDate=new Date();'
    '   // default = 24 sim-hours per real minute (1 sim-day/min); rate and date both remain fully manual after this'
)
EDITS.append(("boot default speed -> 24 sim-hrs/real-min", old5, new5, new5))

# ---- 2b. slider initial position + label to match (mult~1440 -> v~0.81879, "1.4k x speed") ----
old6 = (
    '<input type="range" id="tbSpeed" min="0" max="1" step="0.005" value="0" '
    'title="Time speed ' + DASH + ' left = real-time, right = 5 days/min">\n'
    '  <span id="tbSpeedLbl">real-time</span>'
)
new6 = (
    '<input type="range" id="tbSpeed" min="0" max="1" step="0.005" value="0.81879" '
    'title="Time speed ' + DASH + ' left = real-time, right = 5 days/min">\n'
    '  <span id="tbSpeedLbl">1.4k× speed</span>'
)
EDITS.append(("slider initial position/label -> 1.4k x speed", old6, new6, new6))

# ---- 2c. "Now" button: reset target -> the new default, not literal real-time ----
old7 = (
    '  const nb=document.getElementById("tbNow");\n'
    '  if(nb) nb.onclick=()=>{ simEpoch=Date.now(); simDays=0; simLast=0; solarDate=new Date(); simSpeed=1/1440;\n'
    '    if(sp) sp.value=0; if(lbl) lbl.textContent="real-time";\n'
    '    updateTimeLabel(); updateSunShade(); };'
)
new7 = (
    '  const nb=document.getElementById("tbNow");\n'
    '  if(nb) nb.onclick=()=>{ simEpoch=Date.now(); simDays=0; simLast=0; solarDate=new Date(); simSpeed=1;\n'
    '    if(sp) sp.value=0.81879; if(lbl) lbl.textContent="1.4k× speed";\n'
    '    updateTimeLabel(); updateSunShade(); };'
)
EDITS.append(('"Now" button resets to the 24hr/min default, not real-time', old7, new7, new7))

# ---- 2d. "Now" button tooltip: no longer literally "real-time" ----
old8 = '<button id="tbNow" class="tbtn" title="Reset to real-time, now">Now</button>'
new8 = '<button id="tbNow" class="tbtn" title="Reset time &amp; speed to default">Now</button>'
EDITS.append(('"Now" button tooltip no longer says real-time', old8, new8, new8))

# ---- 3. geo marker: fade out and remove after one ping instead of staying forever ----
old9 = (
    'var el=document.createElement("div");\n'
    '    el.className="wb-geo-marker";\n'
    '    new maplibregl.Marker({element:el})\n'
    '      .setLngLat([_wbGeo.lng,_wbGeo.lat])\n'
    '      .setPopup(new maplibregl.Popup({closeButton:false,offset:10}).setHTML(\n'
)
new9 = (
    'var el=document.createElement("div");\n'
    '    el.className="wb-geo-marker";\n'
    '    var _wbMarker=new maplibregl.Marker({element:el})\n'
    '      .setLngLat([_wbGeo.lng,_wbGeo.lat])\n'
    '      .setPopup(new maplibregl.Popup({closeButton:false,offset:10}).setHTML(\n'
)
EDITS.append(("capture the marker instance so it can be removed later", old9, new9, new9))

old10 = (
    'map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:1.6, bearing:0, pitch:0, duration:2200});\n'
    '    if(window.console) console.info("[worldbook geo] centered on", _wbGeo.place||(_wbGeo.lat+","+_wbGeo.lng));'
)
new10 = (
    'map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:1.6, bearing:0, pitch:0, duration:2200});\n'
    '    if(window.console) console.info("[worldbook geo] centered on", _wbGeo.place||(_wbGeo.lat+","+_wbGeo.lng));\n'
    '    // one ping, then gone: hold briefly after the ring pulse (2.4s), fade the whole\n'
    '    // marker out, then actually remove it - a wink, not a permanent map fixture.\n'
    '    setTimeout(function(){ el.style.transition="opacity .6s ease"; el.style.opacity="0"; }, 2800);\n'
    '    setTimeout(function(){ try{ _wbMarker.remove(); }catch(e){} }, 3400);'
)
# This one is an APPEND: new10 == old10 + extra lines, so old10 is a prefix of new10.
# Checking old-first (like everything else) would keep matching the prefix inside
# the already-patched text and re-append a second copy forever. Tag it "insert" so
# the loop below checks the LONGER string (new) first for this one instead.
EDITS.append(("marker fades out and is removed ~3.4s after appearing", old10, new10, "insert"))

res = []
for entry in EDITS:
    if len(entry) == 4 and entry[3] == "insert":
        name, old, new, _ = entry
        if new in text:
            res.append((name, "already-applied"))
        elif old in text:
            text = text.replace(old, new, 1)
            res.append((name, "patched"))
        else:
            res.append((name, "ANCHOR-NOT-FOUND"))
        continue
    name, old, new, sentinel = entry
    # Check OLD first, not the sentinel: several of these edits DELETE a suffix/
    # trailing chunk, which means NEW ends up being a plain substring of OLD (e.g.
    # removing "...none}\n  #glossHi{...}" down to "...none}" - the shorter NEW is
    # literally a prefix of the original OLD). Checking the sentinel first would
    # misreport "already-applied" on the very first run, before anything changed.
    # Checking "is OLD (the full pre-edit text) still there" first is unambiguous.
    if old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    elif sentinel in text:
        res.append((name, "already-applied"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: gloss removed, time defaults to 24hr/min, geo-ping fully disappears" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
