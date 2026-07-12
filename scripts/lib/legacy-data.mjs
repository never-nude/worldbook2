import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import vm from "node:vm";

const assignmentPattern = (name) => new RegExp(`(?:const|let|var)\\s+${name}\\s*=`);

/**
 * Extract a top-level JavaScript assignment without relying on fragile line numbers.
 * The legacy document is trusted project source; this scanner deliberately supports
 * object/array literals, strings, and comments used by its embedded data records.
 */
export function extractAssignmentExpression(source, name) {
  const match = assignmentPattern(name).exec(source);
  if (!match) throw new Error(`Could not find ${name} in the legacy document.`);

  const equals = source.indexOf("=", match.index);
  if (equals === -1) throw new Error(`Could not find assignment operator for ${name}.`);

  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;

  for (let index = equals + 1; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (lineComment) {
      if (character === "\n") lineComment = false;
      continue;
    }
    if (blockComment) {
      if (character === "*" && next === "/") {
        blockComment = false;
        index += 1;
      }
      continue;
    }
    if (quote) {
      if (escaped) {
        escaped = false;
      } else if (character === "\\") {
        escaped = true;
      } else if (character === quote) {
        quote = null;
      }
      continue;
    }
    if (character === "/" && next === "/") {
      lineComment = true;
      index += 1;
      continue;
    }
    if (character === "/" && next === "*") {
      blockComment = true;
      index += 1;
      continue;
    }
    if (character === "\"" || character === "'" || character === "`") {
      quote = character;
      continue;
    }
    if (character === "{" || character === "[" || character === "(") depth += 1;
    if (character === "}" || character === "]" || character === ")") depth -= 1;
    if (character === ";" && depth === 0) return source.slice(equals + 1, index);
  }

  throw new Error(`Could not find the end of ${name}.`);
}

export function evaluateLegacyExpression(expression, filename, context = {}) {
  return vm.runInNewContext(`(${expression})`, context, { filename });
}

export async function readLegacyData(file = "index.html") {
  const source = await readFile(file, "utf8");
  const evaluate = (name, context) =>
    evaluateLegacyExpression(extractAssignmentExpression(source, name), `${file}:${name}`, context);

  const migrationFrames = evaluate("MIG_KEYFRAMES");
  return {
    source,
    mapData: evaluate("MAPDATA"),
    meta: evaluate("META"),
    flows: evaluate("FLOWS"),
    provenance: evaluate("LAYER_PROV"),
    migrationFrames,
    migrationIndex: evaluate("MIG_BY", { MIG_KEYFRAMES: migrationFrames }),
    flowMagnitude: evaluate("FLOW_MAG"),
    countryLabels: evaluate("COUNTRY_LABELS")
  };
}

export function stableValue(value) {
  if (Array.isArray(value)) return Array.from(value, stableValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort((left, right) => left.localeCompare(right))
        .map((key) => [key, stableValue(value[key])])
    );
  }
  return value;
}

export function stableJson(value) {
  return `${JSON.stringify(stableValue(value), null, 2)}\n`;
}

export function hashValue(value) {
  return createHash("sha256").update(stableJson(value)).digest("hex");
}

function slug(value) {
  return String(value || "feature")
    .toLocaleLowerCase("en")
    .normalize("NFKD")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "feature";
}

export function featureRecords(features) {
  const seen = new Map();
  return Array.from(features, (feature, index) => {
    const geometryHash = hashValue(feature.geometry);
    const baseId = `${slug(feature.properties?.name || feature.properties?.iso3)}-${geometryHash.slice(0, 12)}`;
    const occurrence = seen.get(baseId) || 0;
    seen.set(baseId, occurrence + 1);
    return {
      featureId: occurrence === 0 ? baseId : `${baseId}-${occurrence + 1}`,
      index,
      name: feature.properties?.name || null,
      iso3: feature.properties?.iso3 || null,
      geometryType: feature.geometry?.type || null,
      geometryHash,
      propertiesHash: hashValue(feature.properties || {})
    };
  });
}

function urlsIn(value, urls = new Set()) {
  if (typeof value === "string" && /^https?:\/\//.test(value)) urls.add(value);
  if (Array.isArray(value)) value.forEach((item) => urlsIn(item, urls));
  if (value && typeof value === "object") Object.values(value).forEach((item) => urlsIn(item, urls));
  return urls;
}

export function buildLegacyInventory(data) {
  const features = featureRecords(data.mapData.features);
  const layers = data.meta.layers.map((layer) => ({
    key: layer.key,
    group: layer.group,
    type: layer.type,
    label: layer.label,
    hash: hashValue(layer)
  }));
  const flows = Object.entries(data.flows)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([key, flow]) => ({
      key,
      edgesRef: flow.edgesRef || null,
      edgeCount: Array.isArray(flow.edges) ? flow.edges.length : 0,
      hash: hashValue(flow)
    }));
  const provenance = Object.keys(data.provenance)
    .sort((left, right) => left.localeCompare(right))
    .map((key) => ({ key, hash: hashValue(data.provenance[key]) }));

  return {
    schemaVersion: 1,
    counts: {
      countryFeatures: features.length,
      layers: layers.length,
      physicalFlows: flows.length,
      directFlowEdges: flows.reduce((sum, flow) => sum + flow.edgeCount, 0),
      provenanceCards: provenance.length,
      migrationFrames: data.migrationFrames.length,
      migrationCorridors: data.migrationFrames.reduce((sum, frame) => sum + (frame.edges?.length || 0), 0)
    },
    hashes: {
      mapData: hashValue(data.mapData),
      meta: hashValue(data.meta),
      flows: hashValue(data.flows),
      provenance: hashValue(data.provenance),
      migrationFrames: hashValue(data.migrationFrames),
      migrationIndex: hashValue(data.migrationIndex),
      flowMagnitude: hashValue(data.flowMagnitude),
      countryLabels: hashValue(data.countryLabels)
    },
    exceptions: {
      nullIso3FeatureNames: features.filter((feature) => !feature.iso3).map((feature) => feature.name),
      duplicateIso3: Object.entries(
        features.reduce((groups, feature) => {
          if (feature.iso3) (groups[feature.iso3] ||= []).push(feature.name);
          return groups;
        }, {})
      )
        .filter(([, names]) => names.length > 1)
        .map(([iso3, names]) => ({ iso3, names }))
    },
    features,
    layers,
    flows,
    provenance,
    sourceUrls: [...urlsIn({ meta: data.meta, flows: data.flows, provenance: data.provenance })].sort()
  };
}

export async function resolveFromRepository(...segments) {
  return path.resolve(process.cwd(), ...segments);
}
