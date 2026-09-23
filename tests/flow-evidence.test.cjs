"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const Evidence = require("../v2/js/flow-evidence.js");

// Exercise the real legacy records, including their duplicated country pairs.
function actualRegistries() {
  const html = fs.readFileSync(path.join(__dirname, "..", "v2", "index.html"), "utf8");
  const read = (start, end, name) => JSON.parse(JSON.stringify(vm.runInNewContext(
    html.slice(html.indexOf(start), html.indexOf(end, html.indexOf(start))) + "\n;" + name
  )));
  const FLOWS = read("const FLOWS = {", "/* Weekly stories", "FLOWS");
  const FLOW_MAG = read("const FLOW_MAG=", "const FLOW_MAG_IDX=", "FLOW_MAG");
  const LAYER_PROV = JSON.parse(html.match(/const LAYER_PROV=(\{[^\n]+\});/)[1]);
  const FLOW_MAG_IDX = {};
  Object.keys(FLOW_MAG).forEach(key => {
    FLOW_MAG_IDX[key] = {};
    (FLOW_MAG[key].corridors || []).forEach(row => { FLOW_MAG_IDX[key][row.from + ">" + row.to] = row; });
  });
  return { FLOWS, FLOW_MAG, FLOW_MAG_IDX, LAYER_PROV };
}

test("Mexico–US cocaine and synthetics retain distinct identities and no borrowed quantity", () => {
  const context = actualRegistries();
  assert.equal(context.FLOW_MAG_IDX.drugs["MEX>USA"].value, 365);
  const model = Evidence.apply(context);
  const edges = context.FLOWS.drugs.edges.filter(row => row.from === "MEX" && row.to === "USA");
  assert.equal(edges.length, 2);
  assert.equal(new Set(edges.map(row => row.id)).size, 2);
  assert.deepEqual(edges.map(row => model.tooltip("drugs", row).subject), ["cocaine", "synthetics"]);
  edges.forEach(row => {
    const html = model.renderTooltip("drugs", { from: row.from, to: row.to, c: row.c, wv: 365, amt: "365 t/yr" });
    assert.match(html, /Corridor volume unknown/);
    assert.doesNotMatch(html, /365|t\/yr/);
  });
  assert.equal(context.FLOW_MAG_IDX.drugs["MEX>USA"], undefined);
});

test("Myanmar–Thailand opiates cannot inherit the old synthetic-drug estimate", () => {
  const context = actualRegistries();
  assert.equal(context.FLOW_MAG_IDX.drugs["MMR>THA"].value, 120);
  const model = Evidence.apply(context);
  const edge = context.FLOWS.drugs.edges.find(row => row.from === "MMR" && row.to === "THA");
  assert.equal(model.tooltip("drugs", edge).subject, "opiates");
  assert.doesNotMatch(model.renderTooltip("drugs", edge), /120|methamphetamine/);
});

test("seizure stays in the audit and never appears as annual corridor flow", () => {
  const context = actualRegistries();
  const model = Evidence.apply(context);
  const original = model.audit.original.drugMagnitudes.corridors.find(row => row.from === "ECU" && row.to === "BEL");
  assert.equal(original.value, 14.6);
  assert.match(original.note, /seized 2024/);
  const withheld = model.audit.withheld.find(row => row.from === "ECU" && row.to === "BEL");
  assert.match(withheld.reason, /seizure.*annual-flow/);
  assert.doesNotMatch(model.renderTooltip("drugs", { from: "ECU", to: "BEL", c: "#6ea8fe" }), /14\.6|tonnes per year|t\/yr/);
  assert.ok(context.FLOW_MAG.drugs.corridors.every(row => row.value === null));
});

test("unknown substance fails closed even when endpoints match", () => {
  const model = Evidence.apply(actualRegistries());
  const item = model.tooltip("drugs", { from: "MEX", to: "USA" });
  assert.equal(item.subject, "unknown");
  assert.equal(item.measurement, null);
  assert.match(item.description, /not identified/);
});

test("drugs and shipping render with equal weights and scoped legend copy", () => {
  const context = actualRegistries();
  const model = Evidence.apply(context);
  ["drugs", "shipping"].forEach(key => {
    assert.deepEqual([...new Set(context.FLOWS[key].edges.map(row => row.w))], [1]);
    assert.match(context.FLOWS[key].weightNote, /equal weight/);
    assert.doesNotMatch(context.FLOWS[key].legend + context.FLOWS[key].weightNote, /Thicker|prominence|density/);
  });
  assert.deepEqual(context.FLOWS.shipping.edges.map(row => row.path), model.audit.original.shipping.edges.map(row => row.path));
});

test("shipping reports primary source, period and scope per route without PortWatch attribution", () => {
  const context = actualRegistries();
  const model = Evidence.apply(context);
  const cases = [
    ["Trans-Pacific → Panama Canal", 9944, "FY2024", "Panama Canal Authority", "canal-transits"],
    ["Trans-Pacific → US West Coast", 51506000, "January–December 2024", "Shanghai Municipal Government", "port-throughput"],
    ["Persian Gulf oil via Hormuz", 20.9, "Q1 2025", "US EIA", "chokepoint-oil-flow"]
  ];
  cases.forEach(([nm, value, period, org, metric]) => {
    const item = model.tooltip("shipping", { nm });
    assert.equal(item.measurement.value, value);
    assert.equal(item.measurement.period, period);
    assert.equal(item.measurement.metric, metric);
    assert.equal(item.sources[0].org, org);
    assert.match(item.note, /Port \/ chokepoint context/);
    assert.doesNotMatch(model.renderTooltip("shipping", { nm }), /IMF|PortWatch/);
  });
  assert.doesNotMatch(context.LAYER_PROV.shipping.primarySource.org, /IMF|PortWatch/);
  assert.equal(context.LAYER_PROV.shipping.dataKind, "curated");
  assert.ok(context.FLOWS.shipping.sources.some(source => source.label.includes("Panama Canal Authority")));
});

test("unrecognized shipping route gets no unrelated source or number", () => {
  const model = Evidence.apply(actualRegistries());
  const item = model.tooltip("shipping", { nm: "Unreviewed route", amt: "100M" });
  assert.equal(item.measurement, null);
  assert.deepEqual(item.sources, []);
  assert.doesNotMatch(model.renderTooltip("shipping", { nm: "Unreviewed route", amt: "100M" }), /100M|Source:/);
});

test("adapter preserves originals, leaves other layers alone and is idempotent", () => {
  const context = actualRegistries();
  const before = JSON.stringify({ flow: context.FLOWS.arms, magnitude: context.FLOW_MAG.arms, provenance: context.LAYER_PROV.arms });
  const originalDrugs = JSON.stringify(context.FLOWS.drugs);
  const model = Evidence.apply(context);
  assert.equal(JSON.stringify(model.audit.original.drugs), originalDrugs);
  assert.equal(Evidence.apply(context), model);
  assert.equal(JSON.stringify({ flow: context.FLOWS.arms, magnitude: context.FLOW_MAG.arms, provenance: context.LAYER_PROV.arms }), before);
  assert.equal(model.renderTooltip("arms", {}), null);
});

test("tooltip markup escapes data and refuses executable source URLs", () => {
  const context = actualRegistries();
  context.FLOWS.drugs.sources = [{ label: '<img src=x onerror="alert(1)">', url: 'javascript:alert(1)' }];
  const model = Evidence.apply(context);
  const html = model.renderTooltip("drugs", { nm: '<script>alert(1)</script>', c: "#6ea8fe" });
  assert.doesNotMatch(html, /<script|<img|href="javascript:/);
  assert.match(html, /&lt;script&gt;/);
});
