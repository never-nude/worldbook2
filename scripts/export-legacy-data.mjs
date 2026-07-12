import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { hashValue, readLegacyData, stableJson } from "./lib/legacy-data.mjs";

const output = path.resolve("data/legacy/v1");
const checkOnly = process.argv.includes("--check");
const data = await readLegacyData();
const assets = {
  "world.geojson": data.mapData,
  "meta.json": data.meta,
  "flows.json": data.flows,
  "provenance.json": data.provenance,
  "migration-keyframes.json": data.migrationFrames,
  "migration-index.json": data.migrationIndex,
  "flow-magnitude.json": data.flowMagnitude,
  "country-labels.json": data.countryLabels
};
const manifest = {
  schemaVersion: 1,
  assets: Object.fromEntries(
    Object.entries(assets).map(([file, value]) => [file, { sha256: hashValue(value) }])
  )
};

for (const [file, value] of Object.entries({ ...assets, "manifest.json": manifest })) {
  const target = path.join(output, file);
  const next = stableJson(value);
  if (checkOnly) {
    const current = await readFile(target, "utf8").catch(() => null);
    if (current !== next) throw new Error(`Generated asset is stale: ${path.relative(process.cwd(), target)}`);
  } else {
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, next);
  }
}

console.log(`${checkOnly ? "Verified" : "Exported"} ${Object.keys(assets).length} structured legacy data assets.`);
