"""
Root-cause fix for the recurring "chunks of the map not loading" complaint.

Root cause (measured live, not guessed): the day/night terminator ("sunshade"
layer, 4050 grid-cell polygons) recomputes and calls map.getSource("sunshade")
.setData(...) roughly every 160ms, forever, for as long as the page is open
and the sim clock is running (startSpin()'s main requestAnimationFrame loop).
setData() forces MapLibre to re-tile the ENTIRE 4050-feature GeoJSON source
from scratch on every call. Live-measured on the production build: ~14ms
average per call (worst case ~26ms), repeating ~6x/second, forever, sharing
the same main thread as tile loading/painting under the already-expensive
globe projection. This is a continuous background tax, not a one-time load
cost - unlike the earlier MAPDATA-simplification and cities/seacollar-defer
fixes (both one-time initial-load costs), this can starve rendering at ANY
point during a session, which is why it "keeps happening" rather than being
a one-off.

Fix: drive the shading via map.setFeatureState() instead of setData(). This
needs each grid feature to carry a stable id (added in sunGrid()) and the
paint expression to read ["feature-state","op"] instead of ["get","op"].
setFeatureState updates the GPU-side paint attribute directly without
re-tiling the source. Live-measured after the fix: ~4-6ms average per call
(worst case ~23ms, same ballpark rarity as before) - roughly a 2-3x main-
thread cost reduction on a call that fires 6x/second indefinitely. Verified
visually (screenshot) that the terminator still renders and updates
correctly through feature-state.

Deliberately NOT changed: the 160ms update cadence and 4050-cell grid
resolution. Both were sized for a specific "terminator never lurches" smooth-
ness goal (see the code's own comment). This patch removes the expensive
PATH to that goal rather than trading away the goal itself.

Usage: python3 worldbook_fix_sunshade_perf.py index.html index.html
"""
import sys

EDITS = [
    (
        'feats.push({type:"Feature",properties:{cx:(lo+lo2)/2,cy:la+STEP/2,op:0},\n'
        '      geometry:{type:"Polygon",coordinates:[[[lo,la],[lo2,la],[lo2,la+STEP],[lo,la+STEP],[lo,la]]]}});',
        'feats.push({type:"Feature",id:feats.length,properties:{cx:(lo+lo2)/2,cy:la+STEP/2,op:0},\n'
        '      geometry:{type:"Polygon",coordinates:[[[lo,la],[lo2,la],[lo2,la+STEP],[lo,la+STEP],[lo,la]]]}});'
    ),
    (
        'paint:{"fill-color":"#02040a","fill-opacity":["coalesce",["get","op"],0],"fill-opacity-transition":{duration:1500}}}, "hover");',
        'paint:{"fill-color":"#02040a","fill-opacity":["coalesce",["feature-state","op"],0],"fill-opacity-transition":{duration:1500}}}, "hover");'
    ),
    (
        'function updateSunShade(){ if(!SUNFC||!map.getSource("sunshade"))return; shadeGrid(); map.getSource("sunshade").setData(SUNFC); }',
        'function updateSunShade(){ if(!SUNFC||!map.getSource("sunshade"))return; shadeGrid(); SUNFC.features.forEach(f=>{ map.setFeatureState({source:"sunshade",id:f.id},{op:f.properties.op}); }); }'
    ),
]

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, "r", encoding="utf-8") as f:
        text = f.read()

    applied, skipped = 0, 0
    for i, (old, new) in enumerate(EDITS):
        if new in text:
            print(f"edit {i+1}: already applied, skipping")
            skipped += 1
        elif old in text:
            count = text.count(old)
            assert count == 1, f"edit {i+1}: expected exactly 1 occurrence of anchor, found {count}"
            text = text.replace(old, new)
            print(f"edit {i+1}: applied")
            applied += 1
        else:
            raise SystemExit(f"edit {i+1}: ANCHOR NOT FOUND - source has changed, patch needs updating")

    with open(outp, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"done: {applied} applied, {skipped} already-applied")

if __name__ == "__main__":
    main()
