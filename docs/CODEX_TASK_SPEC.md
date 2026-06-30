# Codex task spec — Worldbook layer/fix (prepend to any request)

You are editing **Worldbook**: `github.com/never-nude/worldbook2`, branch `main` → **worldbook.earth**.
One self-contained `index.html` (~2 MB, mostly inline data): MapLibre GL v5.6.1 globe + Three.js r128, GitHub Pages.
**You are the only tool pushing to this repo.** Do the work, verify, commit to `main`, push.

## Deliver the change as ONE idempotent, pure-ASCII Python patch script
- String-edits `index.html` in place (`python3 patch.py index.html index.html`). No heredocs.
- Idempotent: a sentinel check makes a re-run a no-op (print "already-applied", exit 0), never a double-apply or error.
- Pure ASCII source; use `\uXXXX` in any JS string for non-ASCII glyphs.

## Patterns (match house style exactly)
**Numeric choropleth** (e.g. an index or rate):
1. Parse the `const MAPDATA = {...};` line; for each feature set `properties["<key>"]=value` and `properties["color_<key>"]=ramp(value)`. Re-dump with `json.dumps(...,separators=(",",":"))`.
2. Parse `const META = {...};`; splice into `META.layers` a config: `{group, key:"<key>", label, type:"numeric", prop:"<key>", short, fmtType, unit, stops:[{v,color}...]}` (place it in the right group).
3. Add the format to `labelFor` if new (e.g. a `dec3` branch for a 0–1 index).
4. Add a `LAYER_PROV["<key>"]` card: `{label, metric, unit, higherIs, colorMeaning, primarySource:{org,datasetTitle,url,year}, additionalSources:[], dataKind, provenance, updateFrequency, methodology, limitations, confidence}`.

**Flow / arc layer**:
1. Add to `FLOWS` a `<k>:{label, group, unit, desc, color, dotColor, legend, note, sources:[...], edges:[{from,to,w,c?}...]}`.
2. Splice a `{group, key:"flow_<k>", label, type:"flow", flowKey:"<k>"}` into `META.layers`.
3. Arcs render via the existing lifted-3D ribbon system automatically — do NOT add visible surface lines.

## Sourcing bar (mandatory)
- Real values from a **named dataset** (org · title · URL · year). No invented numbers.
- **Grey (NODATA) for countries without a reported value** — never interpolate. If the legend shows it, the map must show it.
- **Color = information, not good/bad.** Single-hue or diverging that encodes the actual quantity; legend states the mapping.
- Round displayed numbers; always show units. Sensitive topics: consensus ranges + sources.

## Verify, then ship
- Extract the inline `<script>` and run `node --check` on it (must pass).
- Re-run the patch; confirm the output is **byte-identical** (idempotent).
- `git add -A && git commit -m "..." && git push`, then open `https://worldbook.earth/?v=$(date +%s)` to confirm live.

State what you changed, the source(s) used, and how many countries/corridors got data.
