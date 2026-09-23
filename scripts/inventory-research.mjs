#!/usr/bin/env node
/** Inventory declarative atlas research without executing v2/index.html or its scripts.
 * Usage: node scripts/inventory-research.mjs [--check]
 * No external dependencies. The deliberately small literal parser rejects expressions.
 */
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import assert from 'node:assert/strict';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = await readFile(resolve(root, 'v2/index.html'), 'utf8');
const locations = new Map();
const lineStarts = [0];
for (let i = 0; i < source.length; i++) if (source[i] === '\n') lineStarts.push(i + 1);
function location(offset) {
  let lo = 0, hi = lineStarts.length;
  while (lo + 1 < hi) { const mid = (lo + hi) >>> 1; if (lineStarts[mid] <= offset) lo = mid; else hi = mid; }
  return { file: 'v2/index.html', line: lo + 1, column: offset - lineStarts[lo] + 1 };
}
function loc(path) { return locations.get(path) || null; }

// This parses only inert object/array/string/number/boolean/null literals, comments,
// identifier property names and unary signs. Calls, getters, spreads, templates,
// member references and arbitrary expressions deliberately fail closed.
class LiteralParser {
  constructor(text, offset, onValue = () => {}) { this.text = text; this.i = offset; this.onValue = onValue; }
  fail(message) { throw new Error(`${message} at offset ${this.i}: ${this.text.slice(this.i, this.i + 70)}`); }
  skip() {
    while (true) {
      while (/\s/.test(this.text[this.i] || '') && this.i < this.text.length) this.i++;
      if (this.text.startsWith('//', this.i)) { const end = this.text.indexOf('\n', this.i); this.i = end < 0 ? this.text.length : end + 1; }
      else if (this.text.startsWith('/*', this.i)) { const end = this.text.indexOf('*/', this.i + 2); if (end < 0) this.fail('Unclosed comment'); this.i = end + 2; }
      else return;
    }
  }
  string() {
    const quote = this.text[this.i++]; let out = '';
    while (this.i < this.text.length) {
      let c = this.text[this.i++];
      if (c === quote) return out;
      if (c === '\n' || c === '\r') this.fail('Unescaped newline in string');
      if (c !== '\\') { out += c; continue; }
      c = this.text[this.i++];
      if (c === '\n') continue;
      if (c === '\r') { if (this.text[this.i] === '\n') this.i++; continue; }
      const escapes = { n: '\n', r: '\r', t: '\t', b: '\b', f: '\f', v: '\v', '0': '\0' };
      if (c === 'u' || c === 'x') {
        const digits = c === 'u' ? 4 : 2, value = this.text.slice(this.i, this.i + digits);
        if (!new RegExp(`^[0-9a-fA-F]{${digits}}$`).test(value)) this.fail('Invalid hexadecimal escape');
        out += String.fromCharCode(parseInt(value, 16)); this.i += digits;
      } else out += escapes[c] ?? c;
    }
    this.fail('Unclosed string');
  }
  value(path) {
    this.skip(); const start = this.i, c = this.text[this.i]; let result;
    if (c === '"' || c === "'") result = this.string();
    else if (c === '{' || c === '[') {
      const object = c === '{', close = object ? '}' : ']'; result = object ? {} : []; this.i++; this.skip();
      while (this.text[this.i] !== close) {
        let key = result.length;
        if (object) {
          if (this.text[this.i] === '"' || this.text[this.i] === "'") key = this.string();
          else { const match = /^[A-Za-z_$][\w$]*|^\d+/.exec(this.text.slice(this.i)); if (!match) this.fail('Expected literal property name'); key = match[0]; this.i += key.length; }
          this.skip(); if (this.text[this.i++] !== ':') this.fail('Expected colon');
          if (Object.hasOwn(result, key)) this.fail(`Duplicate property ${key}`);
        }
        const child = object ? `${path}.${key}` : `${path}[${key}]`;
        const value = this.value(child);
        // defineProperty safely preserves a literal __proto__ name if one occurs.
        Object.defineProperty(result, key, { value, writable: true, enumerable: true, configurable: true });
        this.skip(); if (this.text[this.i] === close) break;
        if (this.text[this.i++] !== ',') this.fail('Expected comma'); this.skip();
      }
      this.i++;
    } else {
      const token = /^(?:[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?|true\b|false\b|null\b)/i.exec(this.text.slice(this.i));
      if (!token) this.fail('Non-literal expression');
      this.i += token[0].length;
      result = token[0] === 'true' ? true : token[0] === 'false' ? false : token[0] === 'null' ? null : Number(token[0]);
    }
    this.onValue(path, start, result); return result;
  }
}
function extract(name, pattern = new RegExp(`\\b(?:const|let|var)\\s+${name}\\s*=`)) {
  const match = pattern.exec(source); if (!match) throw new Error(`Missing declaration: ${name}`);
  const parser = new LiteralParser(source, match.index + match[0].length, (path, offset) => locations.set(path, location(offset)));
  const value = parser.value(name); parser.skip();
  if (source[parser.i] !== ';') throw new Error(`Expected complete literal declaration for ${name}, got ${source.slice(parser.i, parser.i + 35)}`);
  return value;
}
// Focused parser checks guard escapes, comments, exponent units and rejection of code.
assert.deepEqual(new LiteralParser(`{a:[-1,1e6,/*x*/'it\\'s',],b:true,c:null}`, 0).value('test'), { a: [-1, 1e6, "it's"], b: true, c: null });
assert.throws(() => new LiteralParser('{a: fetch("bad")}', 0).value('test'), /Non-literal/);
assert.throws(() => new LiteralParser('{a:1,a:2}', 0).value('test'), /Duplicate/);

const names = ['META', 'SOURCE_DETAILS', 'LAYER_SOURCE_KEYS', 'FLOWS', 'WEEKLY_FLOW_REGISTRY', 'MIG_KEYFRAMES', 'FLOW_MAG', 'FLOW_QTY', 'LAYER_PROV'];
const raw = Object.fromEntries(names.map(name => [name, extract(name)]));
const mapdata = extract('MAPDATA');
const migrationFlow = extract('FLOWS.migtime', /\bFLOWS\.migtime\s*=/);
const migrationLayer = extract('RUNTIME_MIGRATION_LAYER', /const\s+_e\s*=\s*(?=\{group:"Connections",key:"flow_migtime")/);
const { META, SOURCE_DETAILS, LAYER_SOURCE_KEYS, FLOWS, WEEKLY_FLOW_REGISTRY, MIG_KEYFRAMES, FLOW_MAG, FLOW_QTY, LAYER_PROV } = raw;
const record = (path, value) => ({ id: path, sourceLocation: loc(path), original: value });
const urlRecords = [];
function urls(value, path) {
  if (typeof value === 'string' && /^https?:\/\//.test(value)) urlRecords.push({ id: path, url: value, sourceLocation: loc(path) });
  else if (value && typeof value === 'object') for (const [key, child] of Object.entries(value)) urls(child, Array.isArray(value) ? `${path}[${key}]` : `${path}.${key}`);
}
for (const [name, value] of Object.entries(raw)) urls(value, name);

const codeGaps = {
  drugs: ['W02: FLOWS describes indicative widths while FLOW_MAG stores annual numerical estimates.', 'W02: ECU→BEL magnitude note describes a 2024 seizure under a tonnes-per-year unit.', 'W02: endpoint-only FLOW_MAG_IDX can join different drug subjects sharing MEX→USA or MMR→THA; preserve all originals and require subject-aware identity.'],
  shipping: ['W02: summary provenance labels and detailed schematic-route sources must be reconciled; line geometry does not establish a tracked vessel itinerary.'],
  braindrain: ['FLOW_MAG mixes stock, cumulative, newly registered annual flow, training location and birth-country definitions.'],
  aid: ['Donor definitions and years differ; preserve grants, disbursements and loan-commitment distinctions.'],
  cables: ['Named cable design capacity and regional capacity shares are different metrics; do not imply measured traffic.'],
  debt: ['Bilateral debt relationships are not necessarily new annual lending; check stock-versus-flow against FLOW_QTY and tooltip /yr formatting.'],
  debtout: ['Alias of debt, not an independent dataset; stock-versus-annual-flow semantics require review.'],
  debtin: ['Alias of debt, not an independent dataset; stock-versus-annual-flow semantics require review.'],
  migration: ['Stored mid-2024/mid-2020 migrant stocks must remain distinct from observed journeys or annual migration flows.'],
  arms: ['Separate legal major-weapons transfer measurements from illicit trafficking claims and avoid conflating TIV with money.'],
  migtime: ['Runtime player projects selected decade corridor records onto individual years; preserve original period and stated confidence.', 'Some endpoint labels represent wider regions and include refugee stocks or population change; quantities are not automatically comparable decade flows.'],
  weekly_duryodhana_trail: ['Preserve allegation/settlement distinctions and ownership chronology versus physical travel; source review belongs to W03.']
};
const contextFlows = new Set(['currents', 'flyways', 'dust']);
const researchFlows = new Set(['trafficking', 'wildlife', 'counterfeit']);
function disposition(key, type) {
  if (type !== 'flow' || contextFlows.has(key)) return { status: 'context', reason: 'Preserve as optional explanatory context; no claim-level factual verification performed.' };
  if (codeGaps[key]) return { status: 'reconcile', reason: 'Known structural, display or measurement distinctions need reconciliation before a trail is published.' };
  if (researchFlows.has(key)) return { status: 'research', reason: 'Preserve existing corridor material; identify evidence for specific intermediate stops and continuity before constructing a journey.' };
  return { status: 'reuse', reason: 'Existing records and citations are structurally reusable starting material; source accuracy and continuity still require a bounded trail review.' };
}
function flowInventory(key, flow, path, registration = 'initial') {
  let owner = key, edges = flow.edges;
  const seen = new Set([key]);
  while (!edges && FLOWS[owner]?.edgesRef) { owner = FLOWS[owner].edgesRef; assert(!seen.has(owner), `Cyclic edgesRef ${key}`); seen.add(owner); edges = FLOWS[owner]?.edges; }
  assert(Array.isArray(edges), `Unresolved edges for ${key}`);
  const edgePath = owner === key ? `${path}.edges` : `FLOWS.${owner}.edges`;
  const pairGroups = new Map();
  for (let i = 0; i < edges.length; i++) { const e = edges[i], pair = `${e.from}>${e.to}`; if (!pairGroups.has(pair)) pairGroups.set(pair, []); pairGroups.get(pair).push(`${edgePath}[${i}]`); }
  const magnitudes = FLOW_MAG[key]?.corridors || [];
  const metadata = { ...flow }; delete metadata.edges; delete metadata.stops;
  return {
    id: key, sourceLocation: loc(path), registration, disposition: disposition(key, 'flow'),
    metadata, sourceKeys: LAYER_SOURCE_KEYS[`flow_${key}`] || LAYER_SOURCE_KEYS[key] || [],
    counts: { routes: edges.length, routesWithPath: edges.filter(e => Array.isArray(e.path)).length, pathCoordinates: edges.reduce((n, e) => n + (e.path?.length || 0), 0), explicitStops: flow.stops?.length || 0, sequenceEntries: flow.sequence?.length || 0, magnitudeRecords: magnitudes.length },
    edgesRef: flow.edgesRef || null, routeOwner: owner,
    routes: flow.edgesRef ? [] : edges.map((e, i) => record(`${edgePath}[${i}]`, e)),
    referencedRouteIds: flow.edgesRef ? edges.map((_, i) => `${edgePath}[${i}]`) : [],
    stops: (flow.stops || []).map((s, i) => record(`${path}.stops[${i}]`, s)),
    repeatedEndpointPairs: [...pairGroups].filter(([, records]) => records.length > 1).map(([pair, records]) => ({ pair, records })),
    magnitudeRecordIds: magnitudes.map((_, i) => `FLOW_MAG.${key}.corridors[${i}]`),
    magnitudePairsMissingFromGeometry: magnitudes.filter(m => !pairGroups.has(`${m.from}>${m.to}`)).map(m => `${m.from}>${m.to}`),
    gaps: [...(codeGaps[key] || []), ...(flow.stops?.length ? [] : ['No separately evidenced stop records in this flow. A path coordinate is geometry, not an established event.'])]
  };
}
const flows = Object.entries(FLOWS).map(([key, flow]) => flowInventory(key, flow, `FLOWS.${key}`));
for (const [key, story] of Object.entries(WEEKLY_FLOW_REGISTRY)) flows.push(flowInventory(key, story.flow, `WEEKLY_FLOW_REGISTRY.${key}.flow`, 'conditional hidden URL story'));
const timeline = flowInventory('migtime', migrationFlow, 'FLOWS.migtime', 'runtime registration; edges populated from MIG_KEYFRAMES');
timeline.keyframes = MIG_KEYFRAMES.map((kf, i) => ({ ...record(`MIG_KEYFRAMES[${i}]`, kf), counts: { routes: kf.corridors.length, sources: kf.sources.length }, routes: kf.corridors.map((c, j) => record(`MIG_KEYFRAMES[${i}].corridors[${j}]`, c)) }));
timeline.counts.keyframes = MIG_KEYFRAMES.length;
timeline.counts.routesAcrossKeyframes = MIG_KEYFRAMES.reduce((n, kf) => n + kf.corridors.length, 0);
timeline.counts.initialRuntimeRoutes = MIG_KEYFRAMES[0].corridors.length;
flows.push(timeline);
const layers = META.layers.map((layer, i) => ({ ...record(`META.layers[${i}]`, layer), registration: 'initial' }));
layers.push({ ...record('RUNTIME_MIGRATION_LAYER', migrationLayer), registration: 'runtime' });
for (const [key, story] of Object.entries(WEEKLY_FLOW_REGISTRY)) layers.push({ ...record(`WEEKLY_FLOW_REGISTRY.${key}.layer`, story.layer), registration: 'conditional hidden URL story' });
for (const layer of layers) {
  const { key, type, flowKey, prop } = layer.original;
  layer.disposition = disposition(flowKey || key, type);
  layer.flowRecordId = flowKey || null;
  layer.sourceKeys = LAYER_SOURCE_KEYS[key] || [];
  layer.provenanceRecordId = LAYER_PROV[flowKey || key] ? `LAYER_PROV.${flowKey || key}` : null;
  if (prop) layer.countryCoverage = { property: prop, present: mapdata.features.filter(f => f.properties[prop] != null).length, missing: mapdata.features.filter(f => f.properties[prop] == null).length, total: mapdata.features.length };
}
// Country properties carry static values and research fields. Geometry is intentionally
// omitted: its original location and the source SHA identify the unmodified reference.
const countryRecords = mapdata.features.map((f, i) => ({ id: f.properties.iso3 || f.id || `feature-${i}`, sourceLocation: loc(`MAPDATA.features[${i}].properties`), original: f.properties }));
const owned = flows.filter(f => !f.edgesRef && f.id !== 'migtime');
const magnitudeDatasets = Object.entries(FLOW_MAG).map(([key, data]) => {
  const metadata = { ...data }; delete metadata.corridors;
  return { id: `FLOW_MAG.${key}`, sourceLocation: loc(`FLOW_MAG.${key}`), metadata,
    records: (data.corridors || []).map((value, i) => record(`FLOW_MAG.${key}.corridors[${i}]`, value)) };
});
for (const flow of flows) flow.catalogueLayerKeys = layers.filter(layer => layer.flowRecordId === flow.id).map(layer => layer.original.key);
const inventory = {
  schemaVersion: 1,
  scope: 'Preservation and code-audit inventory of inline v2/index.html data. This is not source verification or a factual endorsement. External adapters and new normalized trail files are outside this legacy inventory.',
  source: { file: 'v2/index.html', sha256: createHash('sha256').update(source).digest('hex') },
  method: { extraction: 'Dependency-free inert JavaScript literal parser; no application code is executed.', identity: 'Original IDs retained; records without explicit IDs use declaration/property/array-index locators. Index locators identify this source snapshot and may shift after edits.', geometry: 'Path coordinate counts do not count verified stops; only separate stops records count as explicit stops.', aliases: 'debtin/debtout reference debt records and are excluded from unique route totals.', runtime: 'Migration over time is inventoried separately by decade keyframe; no animation interpolation is asserted as observed data.', limits: 'No network access or citations opened. Existing source labels, dates, estimates and confidence values remain original unverified claims.' },
  counts: {
    initialMenuLayers: META.layers.length, runtimeMenuLayers: 1, conditionalHiddenLayers: Object.keys(WEEKLY_FLOW_REGISTRY).length,
    flowDefinitions: flows.length, initialFlowDefinitions: Object.keys(FLOWS).length, aliasFlowDefinitions: flows.filter(f => f.edgesRef).length,
    uniqueStoredRoutesIncludingHiddenStory: owned.reduce((n, f) => n + f.counts.routes, 0),
    uniqueStoredRoutesWithPath: owned.reduce((n, f) => n + f.counts.routesWithPath, 0),
    explicitStopRecords: owned.reduce((n, f) => n + f.counts.explicitStops, 0),
    timelineKeyframes: timeline.counts.keyframes, timelineCorridorRecords: timeline.counts.routesAcrossKeyframes,
    magnitudeRecords: Object.values(FLOW_MAG).reduce((n, f) => n + (f.corridors?.length || 0), 0),
    countryRecords: countryRecords.length, sourceUrlOccurrences: urlRecords.length, distinctSourceUrls: new Set(urlRecords.map(s => s.url)).size
  },
  layers, flows, magnitudeDatasets, countryRecords,
  preservedData: Object.fromEntries(names.filter(name => !['FLOWS', 'FLOW_MAG', 'MIG_KEYFRAMES', 'WEEKLY_FLOW_REGISTRY'].includes(name)).map(name => [name, record(name, raw[name])])),
  sourceUrls: urlRecords,
  knownGaps: Object.entries(codeGaps).map(([flowId, gaps]) => ({ flowId, gaps })),
  displayUses: [
    { data: 'META.layers', use: 'Layer catalogue and selector; receives runtime Migration over time and conditional weekly story registrations.' },
    { data: 'FLOWS', use: 'Geometry, visual weights, legend copy, notes and source blocks; aliases resolved through edgesRef.' },
    { data: 'FLOW_MAG → FLOW_MAG_IDX', use: 'Tooltip magnitude lookup currently indexes country pair only; amounts and notes can be joined across subjects.' },
    { data: 'FLOW_QTY', use: 'Tooltip quantity fallback scales stored weights; USD formatter adds /yr, requiring stock-versus-flow review.' },
    { data: 'LAYER_PROV', use: 'Summary source labels, metric descriptions and expanded provenance; can disagree with FLOWS.sources.' },
    { data: 'SOURCE_DETAILS + LAYER_SOURCE_KEYS', use: 'Source hydration rewrites matching source metadata at runtime; original records retained separately here.' },
    { data: 'MIG_KEYFRAMES', use: 'Timeline creates edges and sources for selected decade. Explicit keyframes are preserved instead of generated annual samples.' },
    { data: 'WEEKLY_FLOW_REGISTRY', use: 'Only registered when requested by story URL. Sequence and stops are distinct from general atlas paths.' }
  ]
};
assert.equal(flows.find(f => f.id === 'debtin').counts.routes, flows.find(f => f.id === 'debt').counts.routes);
assert.equal(flows.find(f => f.id === 'debtout').routes.length, 0);
assert.equal(flows.find(f => f.id === 'weekly_duryodhana_trail').counts.explicitStops, 6);
assert(timeline.counts.routesAcrossKeyframes > 0);
assert(layers.some(l => l.original.key === 'flow_migtime'));
assert(flows.find(f => f.id === 'drugs').repeatedEndpointPairs.some(p => p.pair === 'MEX>USA'));
assert(urlRecords.every(s => s.sourceLocation));

const c = inventory.counts;
const escapeCell = s => String(s).replace(/\|/g, '\\|').replace(/\n/g, ' ');
const tableRows = flows.map(f => `| ${f.id} | ${escapeCell(f.metadata.label)} | ${f.id === 'migtime' ? `${f.counts.routesAcrossKeyframes} across ${f.counts.keyframes} frames` : `${f.counts.routes}${f.edgesRef ? ` (alias ${f.edgesRef})` : ''}`} | ${f.counts.routesWithPath} | ${f.counts.explicitStops} | ${f.counts.magnitudeRecords} | ${f.disposition.status} |`).join('\n');
const markdown = `# Existing Worldbook research inventory

Generated by \`node scripts/inventory-research.mjs\` from \`v2/index.html\`. Run with \`--check\` to verify checked-in outputs match the current source. SHA-256: \`${inventory.source.sha256}\`.

This is a reproducible **code audit and preservation snapshot**, not source verification. All figures, source labels, confidence levels, dates and caveats remain original claims awaiting the relevant trail's evidence review. No atlas code was executed and no source was opened by this inventory.

## What exists

- ${c.initialMenuLayers} initial catalogue layers, plus Migration over time registered at runtime and ${c.conditionalHiddenLayers} conditional hidden story.
- ${c.flowDefinitions} flow definitions, including ${c.aliasFlowDefinitions} debt aliases and the timeline.
- ${c.uniqueStoredRoutesIncludingHiddenStory} unique stored route records including the hidden story; ${c.uniqueStoredRoutesWithPath} contain path geometry.
- ${c.explicitStopRecords} explicit stop records, all in the statue story. Geometry coordinates are not evidence of stops.
- ${c.timelineCorridorRecords} additional historical corridor records across ${c.timelineKeyframes} migration keyframes. These are not ${c.timelineCorridorRecords} simultaneously visible routes or independently verified annual observations.
- ${c.magnitudeRecords} separate magnitude records, ${c.countryRecords} country-property records, and ${c.distinctSourceUrls} distinct source URLs (${c.sourceUrlOccurrences} occurrences).

The full [machine-readable snapshot](../data/research-inventory.json) preserves original records, citation/caveat metadata, source lines and columns, aliases, and display uses. Country geometry is omitted; country properties and the source hash preserve the static research baseline. Array-position IDs locate originals within this snapshot and are not proposed permanent trail IDs.

## Readiness by flow

**Reuse** means structurally reusable starting material, pending source and continuity review. **Reconcile** marks known measurement, identity or display distinctions. **Research** calls for targeted evidence for intermediate events and continuity. **Context** preserves explanatory maps and natural systems. These dispositions do not validate claims or rank scientific reliability.

| Flow ID | Label | Routes | With paths | Explicit stops | Magnitudes | Disposition |
| --- | --- | ---: | ---: | ---: | ---: | --- |
${tableRows}

Static/reference/raster catalogue entries are inventoried individually as optional context, with source-key mappings and country-property coverage where applicable. Debt-in and debt-out reference the same stored debt routes; their displayed route counts must not be summed into unique totals.

## Hidden and dynamic records

The six-stop statue story lives in \`WEEKLY_FLOW_REGISTRY.weekly_duryodhana_trail\` and only registers when its URL is requested. Its five links preserve the distinction between alleged physical travel, ownership records and return; a continuous shipping itinerary is not established by that sequence.

Migration over time is absent from the initial \`META.layers\` literal. A later assignment registers \`FLOWS.migtime\` and adds the menu entry; its initially empty literal edges are populated from \`MIG_KEYFRAMES\`. The snapshot retains every keyframe's era, confidence, sources and corridor records rather than treating an empty initializer as an empty dataset.

## W02 and other targeted gaps

${Object.entries(codeGaps).map(([key, gaps]) => `- **${key}:** ${gaps.join(' ')}`).join('\n')}

For every flow without explicit stops, research should add events only where the evidence establishes them. An A→B record and a B→C record do not by themselves establish one continuous journey. Quantities preserved here must retain their actual metric, period, subject and geographic scope when migrated.

## Efficient next use

1. Use the statue's existing six stops and five links for the first reader; keep W03 source/legal-status review separate from this mechanical inventory.
2. Repair the shipping and drugs display/identity issues against the originals preserved here. Withhold unsupported quantitative display without erasing the original research record.
3. Choose the next commodity and illicit/waste cases by source strength and continuity, using the per-flow records to define small research assignments. Existing path geometry is a rendering asset, not a reason to skip evidence work.
4. Preserve \`v2/index.html\` declarations incrementally while normalized trails become the reader's source of truth. Future adapters and trail packets are outside this legacy snapshot's scope.

## Verification

The generator rejects executable expressions and duplicate literal keys. Focused assertions check escaped strings/comments/exponent units, debt alias resolution, hidden statue stops, timeline registration, duplicate drug endpoint pairs and source locations. \`--check\` compares both generated files byte-for-byte; it does not claim to test browser behavior or source accuracy.
`;
const outputs = [['data/research-inventory.json', JSON.stringify(inventory, null, 2) + '\n'], ['docs/RESEARCH_INVENTORY.md', markdown]];
const check = process.argv.includes('--check');
for (const [name, content] of outputs) {
  if (check) assert.equal(await readFile(resolve(root, name), 'utf8'), content, `Stale generated inventory: ${name}`);
  else { await mkdir(dirname(resolve(root, name)), { recursive: true }); await writeFile(resolve(root, name), content); }
}
console.log(`${check ? 'Verified' : 'Generated'} research inventory: ${c.uniqueStoredRoutesIncludingHiddenStory} stored routes + ${c.timelineCorridorRecords} timeline records; ${c.explicitStopRecords} explicit stops; ${c.distinctSourceUrls} distinct source URLs.`);
