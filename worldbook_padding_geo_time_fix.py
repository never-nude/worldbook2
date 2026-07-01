#!/usr/bin/env python3
"""Worldbook: three fixes, each verified live against the production page before
being written here (not guessed-and-shipped like some earlier attempts this session).

1) THE REAL CENTERING BUG. Root cause of "Canada/China still not centered" across
   three prior attempts: "padding" is not a valid MapLibre Map CONSTRUCTOR option.
   Checked the actual maplibre-gl@5.6.1 bundle - the constructor's default-options
   object (list of every key it recognizes: center, zoom, bearing, pitch, roll,
   minZoom, maxZoom, ...) has no "padding" entry, so `new maplibregl.Map({...,
   padding:{...}})` just silently drops it - it was never a globe-vs-mercator issue
   or a wrong pixel value, both prior "fixes" (240px, then 340px) were dead on
   arrival. Confirmed live: map.getPadding() read back all-zeros on production
   despite the constructor option being present in the deployed source. padding
   IS supported, but only via setPadding()/jumpTo()/easeTo() - confirmed by finding
   Map.prototype.setPadding in the bundle, which is just `jumpTo({padding})`.
   Fix: drop the padding key from the constructor, call map.setPadding(...) right
   after. Verified LIVE on the running tab before writing this patch: getPadding()
   changed from all-zeros to {340,0,0,0}, and the projected screen center point
   shifted by exactly half the left padding (352.5 -> 522.5px), as expected.

   Separately worth knowing (not changed here - this is a working feature, not a
   bug): the geo-locate lookup also flies the camera to the VISITOR's detected
   location a couple seconds after load (see _wbApplyGeo -> map.flyTo). Testing
   from Westchester will always end with the view centered near Westchester, not
   near a "nice default" - that's the personalization working as designed, and is
   a separate effect from this padding bug. Mentioning it so it is not mistaken
   for this fix having failed.

2) GEO-PING PULSE, ONCE. The ring around the "you are here" marker used
   `animation: wbGeoPulse 2.4s ease-out infinite` - infinite was the whole bug.
   Changed to a single iteration with animation-fill-mode:forwards, so it pulses
   once (the "I see you" wink) and then settles at its own final frame (fully
   faded, scale 2.4/opacity 0) rather than snapping back and repeating. The solid
   dot underneath (its own permanent box-shadow glow, not part of this animation)
   stays put as a calm marker.

3) TIME DEFAULTS TO REAL-TIME. simSpeed is sim-days per real-minute; the speed
   slider is logarithmic across it (0 = 1x/real-time, 1 = 7200x/5 sim-days-per-
   real-minute cap). Boot set simSpeed=524/1440 (524x) by default - changed to
   1/1440 (true 1x). solarDate already started at `new Date()` (now) on boot, so
   that half of "start at now, run at real time" was already correct - only the
   rate needed fixing. Synced the static slider position/label in the HTML
   (value 0.705 -> 0, "524x speed" -> "real-time") so the UI matches on first
   paint instead of only after the user touches the slider. The existing "Now"
   button already reset the date - extended its handler to also reset simSpeed
   and the slider/label back to real-time, so it is the one button that returns
   both the point in time AND the rate to the real-time-now default, as asked.
   Manual control over both is untouched - slider and date picker work exactly
   as before.

Idempotent, pure ASCII source (unicode chars in the target strings are written
as \\uXXXX escapes so this file itself has no encoding surprises).
Usage: python3 worldbook_padding_geo_time_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MULT = "×"   # ×
DASH = "—"   # —
DOTS = "…"   # …

EDITS = []

# ---- 1. padding: constructor option (silently ignored) -> setPadding() after construction ----
old1 = (
    "  center:[10,28], zoom:1.45, attributionControl:false, maxZoom:9,\n"
    "  padding:_wbDesktop()?{top:0,bottom:0,left:340,right:0}:{top:0,bottom:0,left:0,right:0}\n"
    "});"
)
new1 = (
    "  center:[10,28], zoom:1.45, attributionControl:false, maxZoom:9\n"
    "});\n"
    "if(_wbDesktop()) map.setPadding({top:0,bottom:0,left:340,right:0});"
    "   // padding is NOT a Map constructor option in MapLibre (silently ignored there) -"
    " must be applied via setPadding()/jumpTo() after construction; verified live"
)
EDITS.append(("fix real centering bug: setPadding() after construction, not a constructor option", old1, new1, new1))

# ---- 2. geo-ping ring: pulse once instead of looping forever ----
old2 = (
    '.wb-geo-marker::after{content:"";position:absolute;inset:-9px;border-radius:50%;'
    'border:2px solid var(--accent);opacity:.6;animation:wbGeoPulse 2.4s ease-out infinite}'
)
new2 = (
    '.wb-geo-marker::after{content:"";position:absolute;inset:-9px;border-radius:50%;'
    'border:2px solid var(--accent);opacity:.6;animation:wbGeoPulse 2.4s ease-out 1 forwards}'
)
EDITS.append(("make the geo-ping ring pulse once (a wink), not loop forever", old2, new2, new2))

# ---- 3a. boot default speed: 524x -> real-time (1x) ----
old3 = (
    "simEpoch=Date.now(); simDays=0; paused=false; simSpeed=524/1440; solarDate=new Date();"
    "   // default = 524" + MULT + " real time"
)
new3 = (
    "simEpoch=Date.now(); simDays=0; paused=false; simSpeed=1/1440; solarDate=new Date();"
    "   // default = real time (1x); rate and date both remain fully manual after this"
)
EDITS.append(("default time to real-time (1x) instead of 524x on boot", old3, new3, new3))

# ---- 3b. static slider position + label to match the new default ----
old4 = (
    '<input type="range" id="tbSpeed" min="0" max="1" step="0.005" value="0.705" '
    'title="Time speed ' + DASH + ' left = real-time, right = 5 days/min">\n'
    '  <span id="tbSpeedLbl">524' + MULT + ' speed</span>'
)
new4 = (
    '<input type="range" id="tbSpeed" min="0" max="1" step="0.005" value="0" '
    'title="Time speed ' + DASH + ' left = real-time, right = 5 days/min">\n'
    '  <span id="tbSpeedLbl">real-time</span>'
)
EDITS.append(("sync the speed slider's initial position/label to real-time", old4, new4, new4))

# ---- 3c. "Now" button: also reset speed back to real-time, not just the date ----
old5 = (
    '  const nb=document.getElementById("tbNow");\n'
    '  if(nb) nb.onclick=()=>{ simEpoch=Date.now(); simDays=0; simLast=0; solarDate=new Date(); '
    'updateTimeLabel(); updateSunShade(); };'
)
new5 = (
    '  const nb=document.getElementById("tbNow");\n'
    '  if(nb) nb.onclick=()=>{ simEpoch=Date.now(); simDays=0; simLast=0; solarDate=new Date(); simSpeed=1/1440;\n'
    '    if(sp) sp.value=0; if(lbl) lbl.textContent="real-time";\n'
    '    updateTimeLabel(); updateSunShade(); };'
)
EDITS.append(('extend the "Now" button to also reset speed to real-time, not just the date', old5, new5, new5))

# ---- 3d. "Now" button tooltip: reflect that it resets both time and rate ----
old6 = '<button id="tbNow" class="tbtn" title="Jump to now">Now</button>'
new6 = '<button id="tbNow" class="tbtn" title="Reset to real-time, now">Now</button>'
EDITS.append(('update the "Now" button tooltip to reflect the fuller reset', old6, new6, new6))

res = []
for name, old, new, sentinel in EDITS:
    if sentinel in text:
        res.append((name, "already-applied"))
    elif old in text:
        text = text.replace(old, new, 1)
        res.append((name, "patched"))
    else:
        res.append((name, "ANCHOR-NOT-FOUND"))

open(OUT, "w", encoding="utf-8").write(text)
ok = all(s in ("patched", "already-applied") for _, s in res)
for name, s in res:
    print(f"  [{s:>16}] {name}")
print("OK: centering, geo-ping, and time defaults all fixed" if ok else "WARN: an anchor was not found - nothing broken, but not fully applied")
sys.exit(0 if ok else 1)
