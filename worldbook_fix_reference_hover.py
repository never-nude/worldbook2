"""
Idempotent patch: hoverHTML() has no branch for type:"reference" layers (only
raster/flow get special-cased; everything else falls into the generic numeric/
categorical branch, which reads a nonexistent c.short + labelFor(c,undefined)
and renders the literal string "undefined: No data" under every country while
hovering on the default "Countries" layer). Give reference layers the same
name-only treatment as raster.

Usage: python3 worldbook_fix_reference_hover.py index.html index.html
"""
import sys

OLD = 'if(c.type==="raster") return `<div class="pop-name">${p.name}</div>`;'
NEW = OLD + '\n  if(c.type==="reference") return `<div class="pop-name">${p.name}</div>`;'

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, "r", encoding="utf-8") as f:
        text = f.read()

    if NEW in text:
        print("already applied, skipping")
    elif OLD in text:
        assert text.count(OLD) == 1, "expected exactly one occurrence of the raster hover branch"
        text = text.replace(OLD, NEW)
        print("applied fix")
    else:
        raise SystemExit("ANCHOR NOT FOUND - hoverHTML raster branch text has changed, patch needs updating")

    with open(outp, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    main()
