# Worldbook — Tooling & Routing (canon)

The single rule set for who does what and how changes ship. Keep this in `worldbook2/docs/`.

## Source of truth
- **`github.com/never-nude/worldbook2`, branch `main` → serves worldbook.earth.**
- Archived / DO NOT TOUCH: `never-nude/atlas`, `never-nude/worldbook`.
- The app is one self-contained `index.html` (~2 MB, mostly inline data): MapLibre GL v5.6.1 globe + Three.js r128, GitHub Pages.

## The one rule that prevents disasters
**Only one tool commits to `worldbook2` per task. Ever.** The past fork came from two tools pushing the same repo. Pick one owner per change; never run two against the repo at once.
- **Default: Codex owns pushes.** If Cowork/Claude builds something, it hands over a patch file — it does **not** also push.

## Routing — who to assign
**Codex = default for "build this layer/fix and ship it."**
- Strengths: fetches fresh data; authors the patch; **pushes to `worldbook2` directly** (no copy-paste step).
- Use for: new sourced layers, data refreshes, self-contained fixes that end in a commit.

**Cowork / Claude = verification, visual QA, and design iteration.**
- Strengths: applies a patch in a sandbox and proves it (`node --check` + byte-identical re-run), render-checks the live page in a real browser, iterates conversationally with full thread context.
- Use for: pre-deploy verification, "does this read right" visual review, multi-step design back-and-forth, drafting a patch you'll hand to Codex.
- Limitation: cannot push — delivers a patch file, you (or Codex) deploy it.

Rule of thumb: **Codex fetches + builds + ships; Claude verifies + reviews + iterates.**

## Patch discipline (applies to whoever writes it)
- Changes are **idempotent, pure-ASCII Python patch scripts** that string-edit `index.html` (`in == out`). Use `\uXXXX` in JS for any non-ASCII glyph. **No giant heredocs** (they corrupt on paste).
- Idempotent = a sentinel check makes a re-run a no-op (or byte-identical), never an error or a double-apply.
- **Verify before declaring done:** extract the inline `<script>`, run `node --check`; re-run the patch and confirm the file is **byte-identical**.
- Arcs stay **lifted 3D ribbons** (`flow-3d`); the `flow-lines`/`flow-dots` layers stay at opacity 0 as hit-test geometry only — never re-enable visible surface lines (polar-ring artifact).
- A removed attribution control drops the legally-required Esri credit — darken it, don't delete it.

## Sourcing bar (Freamon-grade — non-negotiable)
- Every datum traces to a **named dataset** (org · dataset title · URL · year). A citation must mean the number came from that source.
- Show **value + unit**; round (e.g. `83%`, not `83.274%`).
- **Grey (NODATA) for any country without a reported value — never invent or interpolate one.** If the legend lists a category, the map must show it.
- **Color = information, never morality.** Encode lower→higher / creditor→debtor / source→consumer. Every legend states its mapping.
- Sensitive topics: scholarly-consensus figures with **ranges + sources**, never one politicized number.
- Each layer carries a `LAYER_PROV` card: label · metric · unit · higherIs · colorMeaning · primarySource · dataKind · provenance · updateFrequency · methodology · limitations · confidence.

## Deploy (one paste, idempotent)
```bash
cd ~/Documents/Claude/Projects/worldbook2 && git pull && \
cp <patch>.py . && python3 <patch>.py index.html index.html && \
git add -A && git commit -m "..." && git push && \
open "https://worldbook.earth/?v=$(date +%s)"
```
GitHub Pages can lag ~60 s; the `?v=` cache-busts the live check.
