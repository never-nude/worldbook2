# Worldbook — session rules (production repo)

**This repo (`never-nude/worldbook2`) is CANONICAL as of 2026-07-06.** It deploys to worldbook.earth via GitHub Pages (the `pages.yml` Action publishes `main` in ~20s). The old `worldbook2-lab` repo is a demoted mirror — do NOT develop there, and NEVER copy its `index.html` over this one (it repeatedly clobbered features in early July 2026: GA4, og:image, a migration rebuild, the geo-ping).

## Workflow

- All work happens **here, on branches**; merging to `main` = production deploy. Treat every merge as shipping to the public beta.
- Bump `window.WB_BUILD` (in index.html) on any shipping change — it's how stale tabs are told apart from real bugs. Verify a deploy with:
  `curl -s "https://worldbook.earth/index.html?cb=$(date +%s)" | grep -o 'WB_BUILD="[^"]*"'`
- After merging, back-port the same change to `worldbook2-lab` main (straight copy of index.html prod→lab is safe in THAT direction only).
- Other files here (methodology.html, docs/, favicon, .py scripts) are prod-only; index.html edits must never remove the GA4/gtag block or og:image tags.

## Border containment canon (LOCKED 2026-07-02)

**A country's edge color must never paint outside that country's own borders — on any layer, at any zoom.** Signed off by Mike; not open for re-litigation.

Implementation lives in `index.html` at the `world-lines` source and the `countries-edge-soft`/`countries-edge-tight` layers, under the banner comment `CANON — COUNTRY BORDER-CONTAINMENT RULES`. Its four invariants (winding normalization; inset offset = width/2 at every stop; per-ring + low-zoom size clamps; round joins/caps) are load-bearing. Do **not** change, relax, or "simplify" them. If a task appears to require breaking one, stop and ask Mike first.

Verification protocol when touching border/glow rendering: check coastlines at z1.8 (North Atlantic), z2.6, z3.6-3.8 (W. Europe), z4.5 (Aegean), z5.5 (Adriatic), and the ZAF/LSO enclave.

## Testing gotchas

- The globe auto-spins; `window.paused = true` is a no-op (`paused` is a closure `let`). Pause via `document.getElementById('tbPlay').click()` before visual tests.
- Boot takes 15-60s; `_atlasBooted === true` is the reliable "layers exist" signal (`map.loaded()` stays false while spinning).
- Pixel-accurate country checks: `map.queryRenderedFeatures(map.project([lng,lat]),{layers:['fills']})[0].properties.iso3`.
- Desktop layout applies `map.setPadding({left:340,...})` — screen center ≠ camera center; call `map.setPadding({top:0,right:0,bottom:0,left:0})` before framing screenshots.
- Runtime CDN dependencies (unpkg, cdnjs, jsdelivr, demotiles glyphs) are guarded/fallback'd as of the 2026-07-06 hardening; keep new external fetches behind the same pattern (fallback host + timeout + visible inline error).
