#!/usr/bin/env python3
"""Worldbook: harden visitor geolocation (v2) after it failed to recenter for a real visitor.
Replaces the v1 block (worldbook_geoip.py) with:
  1) No more "skip fly-to if you already touched the globe" guard - Mike asked for it to
     ALWAYS center on load; that guard was speculative and unrequested, and is the prime
     suspect for "it just opened with the default view" since globe-projection setup may
     fire camera events that look like user interaction.
  2) A two-provider fallback chain (ipwho.is, then get.geojs.io) instead of a single point
     of failure - if one is blocked by a privacy extension or has an outage, the other
     still gets a marker on screen.
  3) Robust numeric coercion (Number()+isFinite) instead of a strict typeof "number" check -
     geojs.io returns latitude/longitude as strings, which the v1 check silently rejected.
  4) Clearer, consistently-prefixed console logging ("[worldbook geo] ...") so a failure
     mode is diagnosable from devtools in one glance instead of guessing.
Idempotent, pure ASCII source. Usage: python3 worldbook_geoip_fix.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

OLD = ('var _wbGeo=null, _wbGeoMapReady=false;\n'
       'function _wbApplyGeo(){\n'
       '  if(!_wbGeo || !_wbGeoMapReady) return;\n'
       '  try{\n'
       '    var el=document.createElement("div");\n'
       '    el.className="wb-geo-marker";\n'
       '    new maplibregl.Marker({element:el})\n'
       '      .setLngLat([_wbGeo.lng,_wbGeo.lat])\n'
       '      .setPopup(new maplibregl.Popup({closeButton:false,offset:10}).setHTML(\n'
       '        \'<div class="wb-geo-pop-h">You are approximately here\'+(_wbGeo.flag?(" "+_wbGeo.flag):"")+\'</div>\'\n'
       '        +\'<div class="wb-geo-pop-d">\'+(_wbGeo.place||"Unknown location")+\'</div>\'\n'
       '        +\'<div class="wb-geo-pop-s">Located from your IP address - city/region accuracy, not exact. VPNs and proxies will show their own location instead of yours.</div>\'\n'
       '      ))\n'
       '      .addTo(map);\n'
       '    if(typeof lastInteract==="undefined" || Date.now()-lastInteract>1200){\n'
       '      map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:3.6, bearing:0, pitch:0, duration:2200});\n'
       '    }\n'
       '  }catch(e){ if(window.console) console.warn("geo marker failed", e); }\n'
       '}\n'
       'fetch("https://ipwho.is/").then(function(r){ return r.json(); }).then(function(d){\n'
       '  if(d && d.success && typeof d.latitude==="number" && typeof d.longitude==="number"){\n'
       '    _wbGeo={lat:d.latitude, lng:d.longitude,\n'
       '      place:[d.city,d.region,d.country].filter(Boolean).join(", "),\n'
       '      flag:(d.flag && d.flag.emoji) || ""};\n'
       '    _wbApplyGeo();\n'
       '  }\n'
       '}).catch(function(e){ if(window.console) console.warn("IP geolocation lookup failed", e); });\n'
       'map.on("load", function(){ _wbGeoMapReady=true; _wbApplyGeo(); });')

NEW = ('var _wbGeo=null, _wbGeoMapReady=false;\n'
       'function _wbApplyGeo(){\n'
       '  if(!_wbGeo || !_wbGeoMapReady) return;\n'
       '  try{\n'
       '    var el=document.createElement("div");\n'
       '    el.className="wb-geo-marker";\n'
       '    new maplibregl.Marker({element:el})\n'
       '      .setLngLat([_wbGeo.lng,_wbGeo.lat])\n'
       '      .setPopup(new maplibregl.Popup({closeButton:false,offset:10}).setHTML(\n'
       '        \'<div class="wb-geo-pop-h">You are approximately here\'+(_wbGeo.flag?(" "+_wbGeo.flag):"")+\'</div>\'\n'
       '        +\'<div class="wb-geo-pop-d">\'+(_wbGeo.place||"Unknown location")+\'</div>\'\n'
       '        +\'<div class="wb-geo-pop-s">Located from your IP address - city/region accuracy, not exact. VPNs and proxies will show their own location instead of yours.</div>\'\n'
       '      ))\n'
       '      .addTo(map);\n'
       '    map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:3.6, bearing:0, pitch:0, duration:2200});\n'
       '    if(window.console) console.info("[worldbook geo] centered on", _wbGeo.place||(_wbGeo.lat+","+_wbGeo.lng));\n'
       '  }catch(e){ if(window.console) console.warn("[worldbook geo] marker/fly-to failed", e); }\n'
       '}\n'
       'function _wbGeoFromIpwhois(){\n'
       '  return fetch("https://ipwho.is/").then(function(r){ return r.json(); }).then(function(d){\n'
       '    var lat=Number(d&&d.latitude), lng=Number(d&&d.longitude);\n'
       '    if(!d || d.success===false || !isFinite(lat) || !isFinite(lng)) throw new Error("ipwho.is: no usable result");\n'
       '    return {lat:lat, lng:lng, place:[d.city,d.region,d.country].filter(Boolean).join(", "), flag:(d.flag&&d.flag.emoji)||""};\n'
       '  });\n'
       '}\n'
       'function _wbGeoFromGeojs(){\n'
       '  return fetch("https://get.geojs.io/v1/ip/geo.json").then(function(r){ return r.json(); }).then(function(d){\n'
       '    var lat=Number(d&&d.latitude), lng=Number(d&&d.longitude);\n'
       '    if(!d || !isFinite(lat) || !isFinite(lng)) throw new Error("geojs.io: no usable result");\n'
       '    return {lat:lat, lng:lng, place:[d.city,d.region,d.country].filter(Boolean).join(", "), flag:""};\n'
       '  });\n'
       '}\n'
       '_wbGeoFromIpwhois().catch(function(e){\n'
       '  if(window.console) console.warn("[worldbook geo] primary lookup failed, trying fallback", e);\n'
       '  return _wbGeoFromGeojs();\n'
       '}).then(function(g){\n'
       '  _wbGeo=g; _wbApplyGeo();\n'
       '}).catch(function(e){ if(window.console) console.warn("[worldbook geo] all lookups failed - no marker this visit", e); });\n'
       'map.on("load", function(){ _wbGeoMapReady=true; _wbApplyGeo(); });')

SENTINEL = "_wbGeoFromIpwhois"

if SENTINEL in text:
    open(OUT, "w", encoding="utf-8").write(text)
    print("  [ already-applied] geo v2 hardening")
    print("OK (no-op)")
    sys.exit(0)

if OLD not in text:
    open(OUT, "w", encoding="utf-8").write(text)
    print("  [ ANCHOR-NOT-FOUND] geo v2 hardening")
    print("WARN: v1 geo block not found verbatim - has it already been hand-edited?")
    sys.exit(1)

text = text.replace(OLD, NEW, 1)
open(OUT, "w", encoding="utf-8").write(text)
print("  [        patched] geo v2 hardening")
print("OK: geolocation hardened (always-fly, two-provider fallback, robust parsing, clearer logs)")
sys.exit(0)
