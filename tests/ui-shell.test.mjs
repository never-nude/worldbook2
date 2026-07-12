import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const html = await readFile(new URL("../index.html", import.meta.url), "utf8");

test("accessible Explorer, search, and contextual research surfaces are present", () => {
  assert.match(html, /id="searchDialog"[\s\S]*role="dialog"[\s\S]*aria-modal="true"/);
  assert.match(html, /id="globalSearch"[\s\S]*placeholder="Search countries or layers"/);
  assert.match(html, /role="tab" data-tab="places"/);
  assert.match(html, /role="tab" data-tab="connections"/);
  assert.match(html, /function wbCountryEntries\(\)/);
  assert.match(html, /function buildSourcesIndex\(focusKey=activeLayer\)/);
  assert.match(html, /This layer: source, method, limits, and confidence/);
  assert.match(html, /function wbDialogKeys\(e\)/);
  assert.match(html, /details:not\(\[open\]\)/);
  assert.match(html, /function bindLegendSource\(el,key\)/);
  assert.match(html, /map\.queryRenderedFeatures\(e\.point,\{layers:\["flow-lines"\]\}\)/);
  assert.match(html, /el\.closest\("button,a,input,textarea,select,summary/);
  assert.match(html, /openCountry\(p,\{focusHeading=false\}=\{\}\)/);
  assert.match(html, /<button class="panel-head" id="layersHead"/);
  assert.match(html, /id="explorerGuide"[\s\S]*Guide &amp; layer index/);
});

test("responsive containment, no-data copy, and reduced-motion defaults are explicit", () => {
  assert.match(html, /id="globeBackdropClip"/);
  assert.match(html, /#globeBackdropClip\{position:fixed;inset:0;z-index:0;overflow:hidden;overflow:clip/);
  assert.match(html, /#panel\{position:fixed;/);
  assert.match(html, /@media \(max-width:430px\)[\s\S]*#subtitle\{display:none\}/);
  assert.match(html, /No reported value — not zero\./);
  assert.match(html, /const WB_REDUCED_MOTION=.*prefers-reduced-motion: reduce/);
  assert.match(html, /paused=WB_REDUCED_MOTION/);
  assert.doesNotMatch(html, /ipwho\.is|get\.geojs\.io/);
});
