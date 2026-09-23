const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const model = require('../v2/js/trail-model.js');
const atlas = () => fs.readFileSync(path.join(__dirname, '../v2/index.html'), 'utf8');
const loadTrail = () => JSON.parse(fs.readFileSync(path.join(__dirname, '../v2/data/trails/duryodhana.json'), 'utf8'));

function section(html, from, to) {
  const start = html.indexOf(from), end = html.indexOf(to, start);
  assert.ok(start >= 0 && end > start, 'renderer section exists: ' + from);
  return html.slice(start, end);
}

// Execute the production geometry pipeline; only the map's source/upload APIs
// and Mercator projection are replaced. Keeping projection as an identity lets
// these checks compare uploaded endpoint coordinates with the evidence records.
function renderer(flow) {
  const html = atlas(), sources = new Map();
  let uploaded = [];
  const context = {
    DEG: Math.PI / 180, flowIso: null,
    FLOWS: {subject: flow}, FLOWGEO: null, ISO_CENTROID: {AAA: [10, 20], BBB: [40, 30]},
    flowFocusName: null, flowFocusPair: null, flowFocusIso: null,
    flowEdgeInTrail: () => true,
    maplibregl: {MercatorCoordinate: {fromLngLat: ({lng, lat}) => ({x: lng, y: lat})}},
    map: {getSource: name => ({setData: data => sources.set(name, data)})},
    FLOW3D: {setLines: data => { uploaded = data; }}
  };
  const code = [
    section(html, 'function gcPoints(', '/* ---- flow datasets'),
    section(html, 'function splitWrapped(', 'let _ISO_NAME'),
    section(html, 'function arcPoints(', '/* Lifted flow renderer.'),
    section(html, 'function _hexRgb(', 'function _newFlow3DLayer('),
    section(html, 'function buildFlowGeo(', 'function flowDotsFC(')
  ].join('\n');
  vm.runInNewContext(code, context);
  context.buildFlowGeo('subject');
  return {context, sources, uploaded};
}

function sameLocation(actual, expected, message) {
  const longitudeError = ((actual[0] - expected[0] + 540) % 360) - 180;
  assert.ok(Math.abs(longitudeError) < 1e-9 && Math.abs(actual[1] - expected[1]) < 1e-9,
    message + ': ' + JSON.stringify(actual) + ' vs ' + JSON.stringify(expected));
}

test('dimming a lifted connection changes alpha without changing geometry or weight', () => {
  const html = fs.readFileSync(path.join(__dirname, '../v2/index.html'), 'utf8');
  const start = html.indexOf('function _appendFlow3DLine(');
  const end = html.indexOf('function _newFlow3DLayer(', start);
  assert.ok(start >= 0 && end > start);
  const context = {
    _hexRgb: () => [0.5, 0.6, 0.7], _flowVisibleAlpha: () => 0.8,
    _mercXY: point => point,
    _splitWrappedElev: (pts, elevs) => [{pts, elevs}]
  };
  vm.runInNewContext(html.slice(start, end), context);
  const normal = [], dimmed = [], points = [[1, 2], [3, 4]], elevations = [200, 400];
  context._appendFlow3DLine(normal, points, elevations, 0.75, '#abcdef');
  context._appendFlow3DLine(dimmed, points, elevations, 0.75, '#abcdef', 0.17);
  assert.equal(normal.length, 6 * 14);
  for (let i = 0; i < normal.length; i++) {
    assert.equal(dimmed[i], i % 14 === 12 ? normal[i] * 0.17 : normal[i]);
  }
  assert.equal(normal[6], 0.75, 'the original quantitative weight is untouched');
  assert.equal(normal[12], 0.8, 'legacy rendering keeps its original alpha by default');
});

test('reader connections meet the geographic stop nodes at ground level, with lifted interiors', () => {
  const trail = loadTrail(), original = JSON.stringify(trail), flow = model.toFlow(trail);
  const {context, sources, uploaded} = renderer(flow);
  const stops = new Map(sources.get('flow-stops').features.map(feature => [Number(feature.properties.n), feature]));
  const byId = new Map(trail.stops.map(stop => [stop.id, stop]));
  assert.equal(stops.size, trail.stops.length);
  assert.equal(sources.get('flow-stop-leaders').features.length, 0, 'reader has no displaced badge callouts');
  assert.equal(context.FLOWGEO.items.length, trail.legs.length);
  let uploadedOffset = 0;
  trail.legs.forEach((leg, index) => {
    const item = context.FLOWGEO.items[index], from = byId.get(leg.from), to = byId.get(leg.to);
    const start = stops.get(from.number).geometry.coordinates, end = stops.get(to.number).geometry.coordinates;
    assert.deepEqual(start, from.coordinates, 'start node retains evidence coordinates');
    assert.deepEqual(end, to.coordinates, 'end node retains evidence coordinates');
    sameLocation(item.pts[0], start, leg.id + ' starts at its node');
    sameLocation(item.pts.at(-1), end, leg.id + ' ends at its node');
    assert.equal(item.elevs[0], 0, leg.id + ' starts at the surface');
    assert.equal(item.elevs.at(-1), 0, leg.id + ' ends at the surface');
    assert.ok(item.elevs.slice(1, -1).every(height => height > 0), 'interior remains visibly lifted');
    assert.ok(item.pts.length >= 60, 'reader arc has enough samples for the close views');
    assert.equal(item.w, 1, 'connection width still does not invent quantities');
    const vertexCount = (item.pts.length - 1) * 6, lastVertex = uploadedOffset + (vertexCount - 1) * 14;
    sameLocation(uploaded.slice(uploadedOffset, uploadedOffset + 2), start, 'uploaded start joins the node');
    sameLocation(uploaded.slice(lastVertex + 2, lastVertex + 4), end, 'uploaded end joins the node');
    assert.equal(uploaded[uploadedOffset + 7], 0, 'uploaded start altitude is ground level');
    assert.equal(uploaded[lastVertex + 8], 0, 'uploaded end altitude is ground level');
    uploadedOffset += vertexCount * 14;
  });
  assert.equal(uploadedOffset, uploaded.length, 'all uploaded ribbons were checked');
  assert.notDeepEqual(stops.get(1).geometry.coordinates, stops.get(6).geometry.coordinates,
    'Cambodia departure and return remain distinct events, not a shared country centroid');
  assert.equal(JSON.stringify(trail), original, 'rendering leaves evidence and display hints unchanged');
});

test('legacy flows retain their lifted endpoints, sampling and displaced badge callouts', () => {
  const flow = {
    color: '#abcdef',
    stops: [{n: 1, coord: [10, 20], badgeCoord: [12, 22]}],
    edges: [
      {from: 'AAA', to: 'BBB', w: 2, path: [[10, 20], [40, 30]]},
      {from: 'AAA', to: 'BBB', w: 1}
    ]
  };
  const {context, sources} = renderer(flow), [explicit, inferred] = context.FLOWGEO.items;
  assert.equal(explicit.pts.length, 15, 'legacy explicit paths keep their existing sampling');
  assert.equal(inferred.pts.length, 49, 'legacy centroid arcs keep their existing sampling');
  for (const [item, baseline] of [[explicit, 21000], [inferred, 40000]]) {
    assert.equal(item.elevs[0], baseline);
    assert.ok(Math.abs(item.elevs.at(-1) - baseline) < 1e-8);
    assert.ok(item.elevs[Math.floor(item.elevs.length / 2)] > baseline);
  }
  assert.equal(explicit.w, 1);
  assert.equal(inferred.w, 0.5, 'legacy relative quantity weights are unchanged');
  assert.deepEqual(sources.get('flow-stops').features[0].geometry.coordinates, [12, 22]);
  assert.deepEqual(Array.from(sources.get('flow-stop-leaders').features[0].geometry.coordinates), [[10, 20], [12, 22]]);
});

test('anchored elevation profiles also handle short and empty paths without floating endpoints', () => {
  const {context} = renderer({edges: [], color: '#abcdef'});
  assert.equal(context._flowElevations([], true, true).length, 0);
  for (const points of [[[10, 20]], [[10, 20], [40, 30]]]) {
    const elevations = context._flowElevations(points, true, true);
    assert.equal(elevations[0], 0);
    assert.equal(elevations.at(-1), 0);
    assert.ok(elevations.every(Number.isFinite));
  }
});
