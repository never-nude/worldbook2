import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { buildLegacyInventory, readLegacyData } from "../scripts/lib/legacy-data.mjs";

test("legacy inventory preserves known geometry and data-model exceptions", async () => {
  const inventory = buildLegacyInventory(await readLegacyData());

  assert.equal(inventory.counts.countryFeatures, 241);
  assert.equal(inventory.counts.layers, 49);
  assert.equal(inventory.counts.physicalFlows, 27);
  assert.equal(inventory.counts.migrationFrames, 52);
  assert.deepEqual(inventory.exceptions.nullIso3FeatureNames.sort(), ["N. Cyprus", "Siachen Glacier", "Somaliland"]);
  assert.deepEqual(inventory.exceptions.duplicateIso3, [{ iso3: "AUS", names: ["Australia", "Indian Ocean Ter.", "Ashmore and Cartier Is."] }]);
});

test("initial runtime does not include automatic IP geolocation providers", async () => {
  const source = await readFile("index.html", "utf8");
  assert.doesNotMatch(source, /ipwho\.is/i);
  assert.doesNotMatch(source, /get\.geojs\.io/i);
});
