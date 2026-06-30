#!/usr/bin/env node
const fs = require("fs");

const html = fs.readFileSync("index.html", "utf8");

function extractConst(name) {
  const match = new RegExp(`const\\s+${name}\\s*=`).exec(html);
  const start = match ? match.index : -1;
  if (start < 0) throw new Error(`missing const ${name}`);
  const eq = html.indexOf("=", start);
  const open = html.slice(eq + 1).search(/[\[{]/);
  if (open < 0) throw new Error(`missing initializer for const ${name}`);
  const brace = eq + 1 + open;
  const opener = html[brace];
  const closer = opener === "{" ? "}" : "]";
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let i = brace; i < html.length; i++) {
    const ch = html[i];
    if (quote) {
      if (escaped) escaped = false;
      else if (ch === "\\") escaped = true;
      else if (ch === quote) quote = null;
      continue;
    }
    if (ch === "\"" || ch === "'" || ch === "`") {
      quote = ch;
      continue;
    }
    if (ch === opener) depth++;
    else if (ch === closer && --depth === 0) return html.slice(brace, i + 1);
  }
  throw new Error(`unclosed const ${name}`);
}

const META = Function(`return ${extractConst("META")}`)();
const SOURCE_DETAILS = Function(`return ${extractConst("SOURCE_DETAILS")}`)();
const LAYER_SOURCE_KEYS = Function(`return ${extractConst("LAYER_SOURCE_KEYS")}`)();
const FLOWS = Function(`return ${extractConst("FLOWS")}`)();
const MIG_KEYFRAMES = html.includes("const MIG_KEYFRAMES=")
  ? Function(`return ${extractConst("MIG_KEYFRAMES")}`)()
  : [];
const details = Object.values(SOURCE_DETAILS);

function normalizeSource(source) {
  if (!source) return null;
  const detail = details.find((d) => d.url === source.url || (d.aliases || []).includes(source.url));
  const out = Object.assign({}, source, detail || {});
  out.label = String(out.label || "Source").replace(/\s+-\s+/g, " — ");
  if (out.year == null) {
    const match = out.label.match(/\b(18|19|20)\d{2}\b/);
    out.year = match ? match[0] : "current";
  }
  return out.url ? out : null;
}

function uniqueSources(sources) {
  const seen = new Set();
  const out = [];
  for (const raw of sources || []) {
    const source = normalizeSource(raw);
    if (!source) continue;
    const key = source.url || source.label;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(source);
  }
  return out;
}

function sourceRefs(keys) {
  return (keys || []).map((key) => SOURCE_DETAILS[key]).filter(Boolean).map((source) => Object.assign({}, source));
}

Object.keys(FLOWS).forEach((key) => {
  FLOWS[key].sources = uniqueSources(FLOWS[key].sources || []);
});
if (MIG_KEYFRAMES.length) {
  FLOWS.migtime = {
    sources: uniqueSources((MIG_KEYFRAMES[0] || {}).sources || [])
  };
  if (!META.layers.some((layer) => layer.key === "flow_migtime")) {
    META.layers.push({ key: "flow_migtime", type: "flow", flowKey: "migtime" });
  }
}
META.layers.forEach((layer) => {
  const sources = layer.type === "flow" && layer.flowKey && FLOWS[layer.flowKey]
    ? FLOWS[layer.flowKey].sources
    : sourceRefs(LAYER_SOURCE_KEYS[layer.key]);
  layer.sources = uniqueSources(sources);
});

const missingLayers = META.layers
  .filter((layer) => !layer.sources.length || layer.sources.some((source) => !source.url || !source.label || source.year == null))
  .map((layer) => layer.key);
const missingFlows = Object.entries(FLOWS)
  .filter(([, flow]) => !flow.sources.length || flow.sources.some((source) => !source.url || !source.label || source.year == null))
  .map(([key]) => key);

const allSources = uniqueSources([
  ...sourceRefs(["natural_earth", "mit_election"]),
  ...MIG_KEYFRAMES.flatMap((frame) => frame.sources || []),
  ...META.layers.flatMap((layer) => layer.sources),
  ...Object.values(FLOWS).flatMap((flow) => flow.sources),
  ...Object.values(META.subnat || {}).flatMap((sub) => sub.sources || []),
]);

if (missingLayers.length || missingFlows.length) {
  console.error(JSON.stringify({ missingLayers, missingFlows }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({
  layers: META.layers.length,
  flows: Object.keys(FLOWS).length,
  sources: allSources.length,
  status: "ok"
}, null, 2));
