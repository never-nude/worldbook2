/* Bounded evidence adapter for legacy drug and shipping layers.
 * Geometry stays in the atlas. Original research is retained in the returned audit.
 * CommonJS and ordinary browser scripts intentionally share the same implementation.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.WorldbookFlowEvidence = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const instances = new WeakMap();
  const clone = value => value == null ? value : JSON.parse(JSON.stringify(value));
  const escape = value => String(value == null ? "" : value).replace(/[&<>"']/g,
    char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const SUBJECTS = {
    cocaine: { label: "Cocaine", color: "#6ea8fe" },
    opiates: { label: "Heroin / opiates", color: "#d4793a" },
    synthetics: { label: "Synthetics (methamphetamine / precursors)", color: "#9b7fe0" },
    cannabis: { label: "Cannabis / resin", color: "#2a9d6f" }
  };
  const DRUG_NOTE = "This overview shows schematic relationships by substance. It does not establish a single shipment's itinerary. No attributable, comparable corridor-volume estimate has been verified for these records; seizures and production totals do not measure the quantity moving along an arc.";
  const SHIPPING_NOTE = "These are schematic maritime connections. The figures describe a whole port or chokepoint in the stated period, not the quantity moving along the displayed route. Different metrics and periods cannot be compared as one flow scale. The lines are not individual vessel tracks.";
  const SOURCES = {
    suez: {
      org: "UNCTAD", datasetTitle: "Review of Maritime Transport 2024, table I.8 (p. 19)",
      url: "https://unctad.org/system/files/official-document/rmt2024_en.pdf", year: "2024",
      locator: "Table I.8, Suez Canal: share of all global container traffic (TEU)"
    },
    shanghai: {
      org: "Shanghai Municipal Government", datasetTitle: "Shanghai's top 10 transportation events in 2024, item 5",
      url: "https://english.shanghai.gov.cn/en-InFocus/20250117/41d3081fbe6a46a688a742b8b02f5a52.html", year: "2025",
      locator: "Item 5, Shanghai Port; January–December 2024 container throughput"
    },
    panama: {
      org: "Panama Canal Authority", datasetTitle: "Panama Canal financial results for FY2024",
      url: "https://pancanal.com/en/presents-financial-results-for-fy24-with-a-focus-on-sustainability-and-the-future/", year: "FY2024",
      locator: "Main FY24 Results: Deep-Draft Transits"
    },
    hormuz: {
      org: "US EIA", datasetTitle: "Global Energy Security Data, table 4 (August 2026 release)",
      url: "https://www.eia.gov/outlooks/steo/report/energysecurity/article.php", year: "2026",
      locator: "Table 4: total oil flows through the Strait of Hormuz, 1Q25; Global Chokepoints methodology"
    }
  };
  const SHIPPING = [
    {
      id: "shipping:asia-europe-suez", name: "Asia–Europe via Malacca + Suez", source: "suez",
      measurement: { value: 22, metric: "chokepoint-share", unit: "% of global container traffic (TEU)", period: "2024 report; entry does not specify a reference year", scope: "Suez Canal, all routes", method: "UNCTAD synthesis of shipping statistics" },
      display: "Suez Canal: 22% of global container traffic (TEU) · UNCTAD 2024 report",
      note: "Historical chokepoint context. The cited table does not give a reference year for this entry or a quantity for the complete Asia–Europe route."
    },
    {
      id: "shipping:transpacific-west-coast", name: "Trans-Pacific → US West Coast", source: "shanghai",
      measurement: { value: 51506000, metric: "port-throughput", unit: "TEU", period: "January–December 2024", scope: "Shanghai Port, all destinations", method: "Municipal transport statistics" },
      display: "Shanghai Port: 51.506 million TEU · full year 2024",
      note: "Total port container throughput, including traffic beyond the US West Coast. It is not a count of individual containers or a volume for this route."
    },
    {
      id: "shipping:transpacific-panama", name: "Trans-Pacific → Panama Canal", source: "panama",
      measurement: { value: 9944, metric: "canal-transits", unit: "deep-draft ship transits", period: "FY2024", scope: "Panama Canal, all routes and both directions", method: "Canal Authority operational reporting" },
      display: "Panama Canal: 9,944 deep-draft ship transits · FY2024",
      note: "Canal-wide transits, not unique vessels or trans-Pacific route traffic. The original generic world-trade share is withheld here."
    },
    {
      id: "shipping:hormuz-oil", name: "Persian Gulf oil via Hormuz", source: "hormuz",
      measurement: { value: 20.9, metric: "chokepoint-oil-flow", unit: "million barrels per day", period: "Q1 2025", scope: "Strait of Hormuz, all oil routes", method: "EIA estimates based on Vortexa tanker tracking and additional analysis" },
      display: "Strait of Hormuz: 20.9 million barrels of oil/day · Q1 2025",
      note: "Historical quarterly average across the strait, including crude, condensate and petroleum products. This is not a full-year 2025 figure or a measurement of the drawn route."
    }
  ];

  function subjectFor(properties) {
    if (Object.prototype.hasOwnProperty.call(SUBJECTS, properties.subject)) return properties.subject;
    const color = String(properties.c || "").toLowerCase();
    return Object.keys(SUBJECTS).find(key => SUBJECTS[key].color === color) || "unknown";
  }
  function recordId(from, to, subject) { return "drugs:" + from + ">" + to + ":" + subject; }
  function provenanceSource(source) {
    return { label: source.org + " — " + source.datasetTitle, url: source.url, year: source.year };
  }
  function sourceLink(source) {
    const label = source.label || [source.org, source.datasetTitle].filter(Boolean).join(" — ");
    return /^https?:\/\//i.test(source.url || "")
      ? '<a href="' + escape(source.url) + '" target="_blank" rel="noopener noreferrer">' + escape(label) + "</a>"
      : escape(label);
  }

  function apply(context) {
    const { FLOWS, FLOW_MAG, FLOW_MAG_IDX, LAYER_PROV } = context;
    if (!FLOWS || !FLOW_MAG || !FLOW_MAG_IDX || !LAYER_PROV) throw new Error("Flow evidence requires all four initialized atlas registries");
    if (instances.has(FLOWS)) return instances.get(FLOWS);
    const audit = {
      version: 1, reviewedAt: "2026-09-22", scope: ["drugs", "shipping"],
      original: clone({
        drugs: FLOWS.drugs, drugMagnitudes: FLOW_MAG.drugs, drugProvenance: LAYER_PROV.drugs,
        shipping: FLOWS.shipping, shippingMagnitudes: FLOW_MAG.shipping, shippingProvenance: LAYER_PROV.shipping
      }),
      withheld: [],
      decisions: [
        "No drug corridor tonnage retained without record-level attribution and scope.",
        "Country pair alone cannot identify a drug-substance record.",
        "Shipping context metrics never set route width; paths remain schematic."
      ]
    };
    const records = { drugs: [], shipping: [] };

    if (FLOWS.drugs) {
      const flow = FLOWS.drugs;
      Object.assign(flow, {
        unit: "qualitative corridors by substance",
        desc: "Selected international drug-trafficking relationships, grouped by substance.",
        legend: "Color identifies the substance category. Equal-width arcs show schematic relationships; they do not compare drug volumes.",
        weightNote: "All arcs have equal weight. No verified corridor tonnage is displayed.",
        note: DRUG_NOTE
      });
      (flow.edges || []).forEach(edge => {
        const subject = subjectFor(edge);
        Object.assign(edge, { id: recordId(edge.from, edge.to, subject), subject, w: 1, amt: null });
        records.drugs.push({ id: edge.id, from: edge.from, to: edge.to, subject, measurement: null });
      });
      const legacy = FLOW_MAG.drugs || { corridors: [] };
      (legacy.corridors || []).forEach(record => audit.withheld.push({
        layer: "drugs", from: record.from, to: record.to, value: record.value, unit: legacy.unit,
        originalNote: record.note,
        reason: record.from === "ECU" && record.to === "BEL"
          ? "Reported seizure was stored under an annual-flow unit; direct primary attribution has not been verified."
          : "No verified attributable method, period and matching substance for a bilateral corridor volume."
      }));
      // Replace the unsafe quantitative table; its original contents remain in audit.original.
      FLOW_MAG.drugs = {
        unit: "qualitative corridor", dataKind: "curated", source: clone(legacy.source),
        corridors: records.drugs.map(record => Object.assign({}, record, {
          value: null, note: "No verified corridor tonnage available for this substance."
        }))
      };
      FLOW_MAG_IDX.drugs = {};
      FLOW_MAG.drugs.corridors.forEach(record => { FLOW_MAG_IDX.drugs[record.id] = record; });
      LAYER_PROV.drugs = Object.assign({}, LAYER_PROV.drugs, {
        metric: flow.desc, unit: flow.unit, colorMeaning: flow.legend, dataKind: "curated", provenance: "synthesized",
        methodology: "Existing country-pair relationships retained as qualitative context, with substance-aware identities and uniform weights.",
        limitations: DRUG_NOTE, confidence: "limited", updateFrequency: "editorial review; no live measurement"
      });
    }

    if (FLOWS.shipping) {
      const flow = FLOWS.shipping;
      records.shipping = SHIPPING.map(record => Object.assign(clone(record), { source: clone(SOURCES[record.source]) }));
      Object.assign(flow, {
        unit: "schematic routes with separate port and chokepoint context",
        desc: "Selected maritime connections and the ports and chokepoints along them.",
        legend: "Equal-width lines show schematic maritime connections. Hover for dated port or chokepoint context.",
        weightNote: "All lines have equal weight. Port throughput, canal transits and oil flows use different units and scopes.",
        note: SHIPPING_NOTE,
        sources: Object.values(SOURCES).map(provenanceSource)
      });
      (flow.edges || []).forEach(edge => {
        const record = records.shipping.find(item => item.name === edge.nm);
        edge.w = 1;
        // Safe fallback if a caller bypasses renderTooltip: context is labeled in the amount itself.
        edge.amt = record ? "Port / chokepoint context — " + record.display : null;
        if (record) edge.id = record.id;
      });
      const summary = { org: "UNCTAD · Shanghai Municipal Government · Panama Canal Authority · US EIA", datasetTitle: "Route-specific port and chokepoint context", url: SOURCES.suez.url, year: "mixed periods; see each route" };
      LAYER_PROV.shipping = Object.assign({}, LAYER_PROV.shipping, {
        metric: flow.desc, unit: flow.unit, colorMeaning: flow.legend, primarySource: summary,
        additionalSources: Object.values(SOURCES).map(clone), dataKind: "curated", provenance: "synthesized",
        updateFrequency: "dated source snapshots; editorial review",
        methodology: "Schematic connections compiled editorially. Context figures come from the explicitly linked port/chokepoint records; there is no imported PortWatch density layer.",
        limitations: SHIPPING_NOTE, confidence: "medium"
      });
    }

    function tooltip(key, properties, options) {
      if (key !== "drugs" && key !== "shipping") return null;
      const p = properties || {};
      const isoName = options && options.isoName || (iso => iso);
      const title = p.nm || (p.from && p.to ? isoName(p.from) + " → " + isoName(p.to) : (FLOWS[key] || {}).label || "Route");
      if (key === "drugs") {
        const subject = subjectFor(p);
        const label = SUBJECTS[subject] ? SUBJECTS[subject].label : "Substance not identified";
        return {
          id: recordId(p.from || "", p.to || "", subject), title, subject, measurement: null,
          description: label + " · schematic relationship",
          display: "Corridor volume unknown",
          note: "No verified tonnage for this record. A seizure or production estimate is not the total transported. Intermediate stops and a continuous shipment are not established by this arc.",
          sourceLabel: "Layer background sources; record-level verification pending",
          sources: clone((FLOWS.drugs || {}).sources || [])
        };
      }
      const record = records.shipping.find(item => item.id === p.id || item.name === p.nm);
      return {
        id: record ? record.id : null, title, description: "Schematic shipping connection",
        measurement: record ? clone(record.measurement) : null,
        display: record ? record.display : "No verified route quantity",
        note: record ? "Port / chokepoint context. " + record.note + " The line is not an individual vessel track." : SHIPPING_NOTE,
        sourceLabel: "Context source", sources: record ? [clone(record.source)] : []
      };
    }
    function renderTooltip(key, properties, options) {
      const item = tooltip(key, properties, options);
      if (!item) return null;
      return '<div class="pop-name">' + escape(item.title) + '</div>' +
        '<div class="pop-sub">' + escape(item.description) + '</div>' +
        '<div class="pop-sub" style="color:#e8eef6;font-weight:600;margin-top:4px">' + escape(item.display) + '</div>' +
        '<div class="pop-sub" style="opacity:.85;margin-top:4px">' + escape(item.note) + '</div>' +
        (item.sources.length ? '<div class="pop-sub" style="opacity:.75;font-size:10px;margin-top:6px">' + escape(item.sourceLabel) + ': ' + item.sources.map(sourceLink).join("; ") + '</div>' : "");
    }
    const result = { audit, records, tooltip, renderTooltip };
    instances.set(FLOWS, result);
    return result;
  }
  return { apply, subjectFor, recordId };
});
