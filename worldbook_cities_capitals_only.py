#!/usr/bin/env python3
"""Worldbook: scope the cities layer to capitals-only, table tiers 2/3.

Mike, two related requests handled together:
  - "let's only do capital cities for now, table the rest"
  - clarified via AskUserQuestion: "we're only going to display countries
    until we zoom in to a reasonable level before the capital cities
    appear" - i.e. country names/fills paint first, capital cities reveal
    only once zoomed to a reasonable level (tier-1's existing minzoom 2.2
    already satisfies this, untouched here), and tier-2/3 "regular" cities
    are deferred entirely for now.

What this does:
  1. Adds a CAPITALS lookup (Set of 199 names) and stamps a `cap:0/1`
     property onto every city feature at construction time - the
     underlying 862-entry CITIES array itself is NOT touched, so nothing
     about the data is lost, only how it's filtered for display.
  2. Tier-1 layers (cities-dot-1 / cities-label-1) now require BOTH
     tier==1 AND cap==1 - so only true national capitals render, not the
     non-capital megacities tier 1 was previously mixing in (Atlanta,
     Mumbai, Shanghai, Sao Paulo, Sydney, etc.)
  3. Tiers 2/3 minzoom raised from 3.6/5.0 to 99 (effectively never) -
     "table the rest" without deleting any layer, data, or styling, so
     re-enabling later is a one-line revert.

Classification approach: pulled the actual 276 tier-1 names straight from
this codebase's live CITIES array (not from memory/assumption), then
classified each one individually as true-national-capital vs
non-capital-megacity. Multi-capital countries keep every seat: South
Africa (Pretoria/Cape Town/Bloemfontein), Bolivia (La Paz/Sucre), Cote
d'Ivoire (Yamoussoukro/Abidjan kept OUT - Yamoussoukro is the official
capital, Abidjan is the non-capital economic hub, same pattern as the
other single-capital countries). Contested/de-facto seats (Taipei,
Jerusalem, Hargeysa, Vatican City) kept as capitals of the entity they
represent, consistent with their pre-existing tier-1 status. Verified via
live web search rather than assumption where currency was in question -
confirmed Jakarta is still Indonesia's official capital as of mid-2026
(Nusantara is legally the designated future/political capital per
Presidential Regulation 79/2025, but Jakarta remains capital under Law
2/2024 pending a presidential decree; full transfer targeted for 2028).

UPDATE: the Burundi/Tanzania gap flagged below is now fixed by a companion
patch (worldbook_add_real_capitals.py, run first or in either order - no
anchor overlap) that adds Gitega and retiers Dodoma to tier 1. This
patch's own CAPITALS list now points at the real capitals directly.

(Original gap note, now resolved by the companion patch above): Burundi's
actual capital is Gitega (since 2019) and Tanzania's is Dodoma (since
1996, completed 2023) - neither city was present/correctly tiered in the
862-entry CITIES array. Bujumbura and Dar es Salaam remain in the data as
real tier-1 megacities (former capitals) - just no longer flagged as
CURRENT capitals, matching every other single-capital country's pattern.

Idempotent via MARKER sentinel (four coupled edits - CAPITALS lookup,
property stamping, tier-1 filter, tier-2/3 minzoom - checked as a single
unit rather than four separate presence-checks). Pure ASCII source.
Usage: python3 worldbook_cities_capitals_only.py index.html index.html
"""
import sys

INP = sys.argv[1] if len(sys.argv) > 1 else "index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"
text = open(INP, encoding="utf-8").read()

MARKER = "/* CITIES_CAPITALS_ONLY_V1 */"
CAPITALS_JSON = '["Abu Dhabi","Abuja","Accra","Addis Ababa","Algiers","Amman","Amsterdam","Andorra","Ankara","Antananarivo","Apia","Ashgabat","Asmara","Astana","Asuncion","Athens","Baghdad","Baku","Bamako","Bandar Seri Begawan","Bangkok","Bangui","Banjul","Basseterre","Beijing","Beirut","Belgrade","Belmopan","Berlin","Bern","Bishkek","Bissau","Bloemfontein","Bogota","Brasilia","Bratislava","Brazzaville","Bridgetown","Brussels","Bucharest","Budapest","Buenos Aires","Cairo","Canberra","Cape Town","Caracas","Castries","Chisinau","Colombo","Conakry","Cotonou","Dakar","Damascus","Dhaka","Dili","Djibouti","Dodoma","Doha","Dublin","Dushanbe","Freetown","Funafuti","Gaborone","Georgetown","Gitega","Guatemala","Hamilton","Hanoi","Harare","Hargeysa","Havana","Helsinki","Honiara","Islamabad","Jakarta","Jerusalem","Kabul","Kampala","Kathmandu","Khartoum","Kiev","Kigali","Kingston","Kingstown","Kinshasa","Kobenhavn","Kuala Lumpur","Kuwait City","La Paz","Libreville","Lilongwe","Lima","Lisbon","Ljubljana","Lome","London","Luanda","Lusaka","Luxembourg","Madrid","Majuro","Malabo","Male","Managua","Manama","Manila","Maputo","Maseru","Mbabane","Melekeok","Mexico City","Minsk","Mogadishu","Monaco","Monrovia","Montevideo","Moroni","Moscow","Muscat","Nairobi","Nassau","Naypyidaw","Ndjamena","New Delhi","Niamey","Nicosia","Nouakchott","Nukualofa","Oslo","Ottawa","Ouagadougou","Palikir","Panama City","Paramaribo","Paris","Phnom Penh","Podgorica","Port Louis","Port Moresby","Port Vila","Port-au-Prince","Port-of-Spain","Prague","Praia","Pretoria","Pristina","Pyongyang","Quito","Rabat","Reykjavik","Riga","Riyadh","Rome","Roseau","Saint George\'s","Saint John\'s","San Jose","San Marino","San Salvador","Sanaa","Santiago","Santo Domingo","Sao Tome","Sarajevo","Seoul","Singapore","Skopje","Sofia","Stockholm","Sucre","Suva","Taipei","Tallinn","Tarawa","Tashkent","Tbilisi","Tegucigalpa","Tehran","Thimphu","Tirana","Tokyo","Tripoli","Tunis","Ulaanbaatar","Vaduz","Valletta","Vatican City","Victoria","Vienna","Vientiane","Vilnius","Warsaw","Washington, D.C.","Wellington","Windhoek","Yamoussoukro","Yaounde","Yerevan","Zagreb"]'  # a Python str containing JS array-literal text

if MARKER in text:
    status = "already-applied"
else:
    anchor = 'map.addSource("cities"'
    a_i = text.find(anchor)
    p_old = 'properties:{name:c[0],tier:c[3]}}; })}});'
    p_new = 'properties:{name:c[0],tier:c[3],cap:CAPITALS.has(c[0])?1:0}}; })}});'
    m_old = 'const CITY_MINZ={1:2.2,2:3.6,3:5.0};'
    m_new = 'const CITY_MINZ={1:2.2,2:99,3:99};'
    f_old = 'filter:["==",["get","tier"],tr],'
    f_new = 'filter:tr===1?["all",["==",["get","tier"],1],["==",["get","cap"],1]]:["==",["get","tier"],tr],'

    if a_i == -1:
        status = "ANCHOR-NOT-FOUND (addSource cities)"
    elif p_old not in text:
        status = "ANCHOR-NOT-FOUND (properties)"
    elif m_old not in text:
        status = "ANCHOR-NOT-FOUND (CITY_MINZ)"
    elif text.count(f_old) != 2:
        status = "ANCHOR-MISMATCH (expected 2 filter occurrences, found %d)" % text.count(f_old)
    else:
        text = (text[:a_i] + MARKER + "\nconst CAPITALS = new Set(" + CAPITALS_JSON + ");\n"
                + text[a_i:])
        text = text.replace(p_old, p_new, 1)
        text = text.replace(m_old, m_new, 1)
        text = text.replace(f_old, f_new)  # both occurrences, same correct fix
        status = "patched"

open(OUT, "w", encoding="utf-8").write(text)
print(f"  [{status}] cities layer scoped to capitals-only (tier-1: cap==1 required, 199 names); tiers 2/3 tabled (minzoom->99)")
print("OK: capitals-only cities layer shipped" if status in ("patched", "already-applied") else "WARN: review before deploying")
sys.exit(0 if status in ("patched", "already-applied") else 1)
