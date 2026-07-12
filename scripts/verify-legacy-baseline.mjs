import { readFile } from "node:fs/promises";
import path from "node:path";
import { buildLegacyInventory, readLegacyData, stableJson } from "./lib/legacy-data.mjs";

const baselinePath = path.resolve("data/legacy-inventory.v1.json");
const expected = JSON.parse(await readFile(baselinePath, "utf8"));
const actual = buildLegacyInventory(await readLegacyData());

if (stableJson(actual) !== stableJson(expected)) {
  throw new Error(
    "Legacy data no longer matches data/legacy-inventory.v1.json. Review the data change and run npm run legacy:inventory only when it is intentional."
  );
}

console.log(`Legacy data baseline verified: ${actual.counts.countryFeatures} features, ${actual.counts.layers} layers, ${actual.counts.physicalFlows} physical flows.`);
