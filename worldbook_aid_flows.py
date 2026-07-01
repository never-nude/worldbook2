# -*- coding: ascii -*-
"""
Idempotent patch: adds a new "Foreign aid flows" data layer to Worldbook.
Adds:
  - META.layers entry (key: flow_aid, group: "Trade & resources", type: flow, flowKey: aid)
  - LAYER_PROV["aid"] (full provenance: primary + additional sources, methodology, limitations)
  - FLOWS.aid (21 real sourced bilateral aid/ODA corridors, donor -> recipient)

Usage: python3 worldbook_aid_flows.py index.html index.html
"""
import sys, re, json

def extract_balanced(text, start_brace_idx):
    depth = 0; in_str = False; esc = False; i = start_brace_idx; n = len(text)
    while i < n:
        c = text[i]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: return text[start_brace_idx:i+1]
        i += 1
    raise ValueError("unbalanced braces starting at %d" % start_brace_idx)

def find_blob(varname, text):
    m = re.search(r'\b' + re.escape(varname) + r'\s*=\s*\{', text)
    if not m:
        raise ValueError("could not find " + varname)
    brace_idx = m.end() - 1
    blob = extract_balanced(text, brace_idx)
    return blob, brace_idx

# ---------------------------------------------------------------- new content

NEW_META_LAYER = {
    "group": "Trade & resources",
    "key": "flow_aid",
    "label": "Foreign aid flows",
    "type": "flow",
    "flowKey": "aid"
}

NEW_LAYER_PROV = {
    "label": "Foreign aid flows",
    "metric": "Bilateral foreign aid / official development assistance from major donor governments to recipient countries.",
    "unit": "USD millions/year (donor definitions vary - see limitations)",
    "higherIs": "neutral",
    "colorMeaning": "Path color/weight encodes the estimated annual bilateral aid amount from donor to recipient.",
    "primarySource": {
        "org": "USAFacts / USAID",
        "datasetTitle": "US Foreign Aid by Country (ForeignAssistance.gov data)",
        "url": "https://usafacts.org/answers/how-much-foreign-aid-does-the-us-provide/",
        "year": "2024"
    },
    "additionalSources": [
        {"org": "JICA", "datasetTitle": "Data Book 2023 and 2024 (Geographical Distribution of Operations)",
         "url": "https://www.jica.go.jp/english/about/disc/report/2024/__icsFiles/afieldfile/2025/07/17/2024-EN-data.pdf"},
        {"org": "UK FCDO", "datasetTitle": "Statistics on International Development: Final UK ODA Spend 2024",
         "url": "https://assets.publishing.service.gov.uk/media/68cae5911eabc899da7084f2/Statistics_on_International_Development_final_UK_ODA_spend_2024.pdf"},
        {"org": "French Senate Finance Committee", "datasetTitle": "PLF 2025 budget review, citing DG Tresor / OECD bilateral ODA data (2022)",
         "url": "https://www.senat.fr/rap/l24-144-34/l24-144-34_mono.html"},
        {"org": "Devex", "datasetTitle": "Money Matters: How is Germany spending its aid? (2024 data)",
         "url": "https://www.devex.com/news/money-matters-how-is-germany-spending-its-aid-112263"}
    ],
    "dataKind": "measured",
    "provenance": "primary",
    "updateFrequency": "annual",
    "methodology": "Each corridor uses the donor's own official aid reporting for the most recent available year (2022-2024, varies by donor). US figures combine each country's total obligation with its officially-stated economic-assistance share; Japan figures are JICA ODA-loan and investment-finance commitments (a specific instrument, not total bilateral ODA); UK and France figures are each government's bilateral ODA disbursements, converted to USD at that year's average exchange rate.",
    "limitations": "Donors use different definitions and instruments (grants vs. loan commitments vs. total assistance), so figures are not on a single harmonized basis - see each corridor's tooltip for its specific source and definition. Deliberately excludes corridors where aid is overwhelmingly military/security in nature (US to Ukraine and US to Israel are both majority security-classified) since including them at full value alongside development-focused corridors would misrepresent the comparison. This is a sample of major corridors from five donors, not an exhaustive bilateral matrix.",
    "confidence": "medium"
}

# from, to, w (USD millions, for arc thickness), amt (tooltip display string)
EDGES = [
    ("USA","JOR",1391,"$1.39B/yr (FY2024, ~76% of $1.82B total) - USAID/State, via USAFacts"),
    ("USA","COD",1402,"$1.40B/yr (FY2024, ~99% of total) - USAID/State, via USAFacts"),
    ("USA","ETH",1330,"$1.33B/yr (FY2024, all economic assistance) - USAID/State, via USAFacts"),
    ("USA","KEN",914, "$914M/yr (FY2024, ~93% of total) - USAID/State, via USAFacts"),
    ("USA","AFG",755, "$755M/yr (FY2024, all economic assistance) - USAID/State, via USAFacts"),
    ("USA","COL",546, "$546M/yr (FY2024, ~93% of total) - USAID/State, via USAFacts"),
    ("DEU","UKR",1000,"$1.0B (2024, ~4.2% of Germany's total ODA, its largest recipient) - via Devex"),
    ("DEU","IND",788, "$788M (2024, Germany's 2nd-largest recipient) - via Devex"),
    ("JPN","IND",5892,"$5.89B (JFY2023, ODA loans + investment finance) - JICA Data Book 2024"),
    ("JPN","BGD",2360,"$2.36B (JFY2023, ODA loans + investment finance) - JICA Data Book 2024"),
    ("JPN","IDN",2137,"$2.14B (JFY2022, ODA loans + investment finance) - JICA Data Book 2023"),
    ("JPN","PHL",2117,"$2.12B (JFY2023, ODA loans + investment finance) - JICA Data Book 2024"),
    ("JPN","VNM",727, "$727M (JFY2023, ODA loans + investment finance) - JICA Data Book 2024"),
    ("GBR","UKR",346, "approx. $346M/yr (2024, top UK ODA recipient) - FCDO, converted from GBP"),
    ("GBR","AFG",246, "approx. $246M/yr (2024, +67% vs 2023) - FCDO, converted from GBP"),
    ("GBR","ETH",233, "approx. $233M/yr (2024) - FCDO, converted from GBP"),
    ("GBR","SYR",202, "approx. $202M/yr (2024, up from GBP63.4M in 2022) - FCDO, converted from GBP"),
    ("FRA","CIV",469, "approx. $469M (2022, France's #1 recipient) - Senate Finance Cmte, converted from EUR447M"),
    ("FRA","MAR",416, "approx. $416M (2022, France's #2 recipient) - Senate Finance Cmte, converted from EUR396.6M"),
    ("FRA","CMR",260, "approx. $260M (2022, France's #3 recipient) - Senate Finance Cmte, converted from EUR248M"),
    ("FRA","UKR",252, "approx. $252M (2022, civilian ODA only, separate from military aid) - Senate Finance Cmte, converted from EUR240.4M"),
]

NEW_FLOWS_AID = {
    "label": "Foreign aid flows",
    "group": "Trade & resources",
    "unit": "US$ millions/yr (bilateral development assistance, selected corridors)",
    "desc": "Government-to-government foreign aid: official development assistance and comparable economic assistance from major donor governments to recipient countries. Arrow points to the receiving country.",
    "color": "#b48ee8",
    "dotColor": "#f1e6ff",
    "legend": "Each arc is a bilateral aid corridor; thickness approximates the annual amount from donor to recipient.",
    "note": "Selected major corridors from five donor governments (USA, Germany, Japan, UK, France), each using that donor's own official reporting for the most recent available year - see tooltip for each corridor's exact source and definition. Excludes corridors where aid is overwhelmingly military/security in nature (e.g. US to Ukraine and US to Israel).",
    "sources": [
        {"label": "USAFacts - US Foreign Aid by Country (USAID/State ForeignAssistance.gov data)", "url": "https://usafacts.org/answers/how-much-foreign-aid-does-the-us-provide/", "year": 2024},
        {"label": "JICA - Data Book 2023 / 2024", "url": "https://www.jica.go.jp/english/about/disc/report/2024/__icsFiles/afieldfile/2025/07/17/2024-EN-data.pdf", "year": 2024},
        {"label": "UK FCDO - Statistics on International Development: Final UK ODA Spend 2024", "url": "https://assets.publishing.service.gov.uk/media/68cae5911eabc899da7084f2/Statistics_on_International_Development_final_UK_ODA_spend_2024.pdf", "year": 2024},
        {"label": "French Senate Finance Committee - PLF 2025 budget review (DG Tresor / OECD data)", "url": "https://www.senat.fr/rap/l24-144-34/l24-144-34_mono.html", "year": 2022},
        {"label": "Devex - Money Matters: How is Germany spending its aid?", "url": "https://www.devex.com/news/money-matters-how-is-germany-spending-its-aid-112263", "year": 2024}
    ],
    "edges": [ {"from": f, "to": t, "w": w, "amt": amt} for (f,t,w,amt) in EDGES ]
}

# ---------------------------------------------------------------- apply

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, "r", encoding="utf-8") as f:
        text = f.read()

    changed = False

    # ---- META.layers: add flow_aid if missing ----
    if '"flow_aid"' in text:
        print("META: flow_aid already present, skipping")
    else:
        blob, start = find_blob("META", text)
        meta = json.loads(blob)
        if not any(l.get("key") == "flow_aid" for l in meta["layers"]):
            meta["layers"].append(NEW_META_LAYER)
        new_blob = json.dumps(meta, separators=(",", ":"), ensure_ascii=True)
        text = text[:start] + new_blob + text[start+len(blob):]
        changed = True
        print("META: added flow_aid")

    # ---- LAYER_PROV.aid: add if missing ----
    if '"aid":{"label":"Foreign aid flows"' in text:
        print("LAYER_PROV: aid already present, skipping")
    else:
        blob, start = find_blob("LAYER_PROV", text)
        prov = json.loads(blob)
        if "aid" not in prov:
            prov["aid"] = NEW_LAYER_PROV
        new_blob = json.dumps(prov, separators=(",", ":"), ensure_ascii=True)
        text = text[:start] + new_blob + text[start+len(blob):]
        changed = True
        print("LAYER_PROV: added aid")

    # ---- FLOWS.aid: add if missing ----
    if re.search(r'\baid\s*:\s*\{"label":"Foreign aid flows"', text):
        print("FLOWS: aid already present, skipping")
    else:
        m = re.search(r'\bFLOWS\s*=\s*\{', text)
        if not m:
            raise ValueError("could not find FLOWS")
        insert_at = m.end()  # right after the opening brace
        aid_json = json.dumps(NEW_FLOWS_AID, separators=(",", ":"), ensure_ascii=True)
        insertion = "\naid:" + aid_json + ","
        text = text[:insert_at] + insertion + text[insert_at:]
        changed = True
        print("FLOWS: added aid")

    with open(outp, "w", encoding="utf-8") as f:
        f.write(text)

    print("changed:", changed)

if __name__ == "__main__":
    main()
