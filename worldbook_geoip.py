#!/usr/bin/env python3
"""Worldbook: visitor geolocation.
On every page load, silently looks up the visitor's approximate location from their IP
(via the free, keyless, HTTPS/CORS-enabled ipwho.is API - no permission prompt, no GPS),
drops a small glowing pulsing marker there (click for a popup with the place name + an
honest accuracy/VPN caveat), and flies the globe to center on it. Non-blocking: the lookup
runs in the background and never delays the loading screen or globe render. Fails silently
(console.warn only, no UI error) if the lookup fails - the globe just stays at its default
view. Skips the camera fly-to (but still drops the marker) if the visitor has already
started dragging/zooming before the lookup resolves, so it never yanks the view out from
under someone who's already exploring.
Idempotent, pure ASCII source. Usage: python3 worldbook_geoip.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

CSS = """
/* visitor IP-location marker */
.wb-geo-marker{width:14px;height:14px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px 3px rgba(110,168,254,.85);cursor:pointer;position:relative}
.wb-geo-marker::after{content:"";position:absolute;inset:-9px;border-radius:50%;border:2px solid var(--accent);opacity:.6;animation:wbGeoPulse 2.4s ease-out infinite}
@keyframes wbGeoPulse{0%{transform:scale(.35);opacity:.8}100%{transform:scale(2.4);opacity:0}}
.wb-geo-pop-h{font-weight:600;font-size:13px;color:var(--ink);margin-bottom:2px}
.wb-geo-pop-d{font-size:12px;color:var(--ink);opacity:.85;margin-bottom:6px}
.wb-geo-pop-s{font-size:10.5px;color:var(--muted);line-height:1.4}
</style>"""

JS = """map.on("load", _atlasBoot);
var _wbGeo=null, _wbGeoMapReady=false;
function _wbApplyGeo(){
  if(!_wbGeo || !_wbGeoMapReady) return;
  try{
    var el=document.createElement("div");
    el.className="wb-geo-marker";
    new maplibregl.Marker({element:el})
      .setLngLat([_wbGeo.lng,_wbGeo.lat])
      .setPopup(new maplibregl.Popup({closeButton:false,offset:10}).setHTML(
        '<div class="wb-geo-pop-h">You are approximately here'+(_wbGeo.flag?(" "+_wbGeo.flag):"")+'</div>'
        +'<div class="wb-geo-pop-d">'+(_wbGeo.place||"Unknown location")+'</div>'
        +'<div class="wb-geo-pop-s">Located from your IP address - city/region accuracy, not exact. VPNs and proxies will show their own location instead of yours.</div>'
      ))
      .addTo(map);
    if(typeof lastInteract==="undefined" || Date.now()-lastInteract>1200){
      map.flyTo({center:[_wbGeo.lng,_wbGeo.lat], zoom:3.6, bearing:0, pitch:0, duration:2200});
    }
  }catch(e){ if(window.console) console.warn("geo marker failed", e); }
}
fetch("https://ipwho.is/").then(function(r){ return r.json(); }).then(function(d){
  if(d && d.success && typeof d.latitude==="number" && typeof d.longitude==="number"){
    _wbGeo={lat:d.latitude, lng:d.longitude,
      place:[d.city,d.region,d.country].filter(Boolean).join(", "),
      flag:(d.flag && d.flag.emoji) || ""};
    _wbApplyGeo();
  }
}).catch(function(e){ if(window.console) console.warn("IP geolocation lookup failed", e); });
map.on("load", function(){ _wbGeoMapReady=true; _wbApplyGeo(); });"""

EDITS = [
    ("geo marker css", "</style>", CSS, "wb-geo-marker{"),
    ("geo lookup + marker + fly-to", 'map.on("load", _atlasBoot);', JS, "_wbApplyGeo"),
]

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
print("OK: geolocation marker + fly-to applied" if ok else "WARN: an anchor was not found")
sys.exit(0 if ok else 1)
