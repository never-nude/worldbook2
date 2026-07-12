import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { buildLegacyInventory, readLegacyData, stableJson } from "./lib/legacy-data.mjs";

const target = path.resolve("data/legacy-inventory.v1.json");
const accept = process.argv.includes("--accept");

if (!accept) {
  throw new Error("Refusing to overwrite the legacy baseline without --accept.");
}

const data = await readLegacyData();
const inventory = buildLegacyInventory(data);
await mkdir(path.dirname(target), { recursive: true });
await writeFile(target, stableJson(inventory));
console.log(`Wrote ${path.relative(process.cwd(), target)} with ${inventory.counts.countryFeatures} features and ${inventory.counts.layers} layers.`);
