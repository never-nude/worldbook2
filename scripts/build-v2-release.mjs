import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const valueAfter = (flag, fallback) => {
  const index = args.indexOf(flag);
  return index >= 0 ? args[index + 1] : fallback;
};

const sourcePath = resolve(valueAfter("--source", resolve(repoRoot, "index.html")));
const outputPath = resolve(valueAfter("--out", resolve(repoRoot, "dist/v2/index.html")));
const checkOnly = args.includes("--check");

function replaceOnce(source, search, replacement, label) {
  const count = source.split(search).length - 1;
  if (count !== 1) throw new Error(`Expected one ${label}; found ${count}.`);
  return source.replace(search, replacement);
}

let html = await readFile(sourcePath, "utf8");
html = replaceOnce(
  html,
  '<meta property="og:url" content="https://worldbook.earth/" />',
  '<meta property="og:url" content="https://worldbook.earth/v2/" />',
  "Open Graph URL",
);

const descriptionTag = '<meta name="description" content="Worldbook is an interactive 3D globe reference work: sourced data on every country across religion, politics, economy, health, debt, trade, and migration." />';
html = replaceOnce(
  html,
  descriptionTag,
  `${descriptionTag}\n<meta name="robots" content="noindex,follow" />`,
  "description metadata tag",
);

if (!/window\.WB_BUILD="[^"]*v2[^"]*"/.test(html)) {
  throw new Error("V2 releases require a WB_BUILD string containing 'v2'.");
}

if (checkOnly) {
  const existing = await readFile(outputPath, "utf8");
  if (existing !== html) throw new Error(`V2 release artifact is stale: ${outputPath}`);
} else {
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, html);
}

const hash = createHash("sha256").update(html).digest("hex");
console.log(`${checkOnly ? "Verified" : "Built"} ${outputPath} (${html.length} bytes, sha256 ${hash})`);
