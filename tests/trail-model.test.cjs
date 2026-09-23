const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const model = require('../v2/js/trail-model.js');
const load = () => JSON.parse(fs.readFileSync(path.join(__dirname, '../v2/data/trails/duryodhana.json'), 'utf8'));

test('pilot trail has complete stop and leg evidence references', () => {
  const trail = load(); assert.equal(model.validate(trail), trail);
  assert.equal(trail.stops.length, 6); assert.equal(trail.legs.length, 5);
});
test('adapter retains evidence geometry rather than drawing through displaced labels', () => {
  const trail = load(), flow = model.toFlow(trail);
  assert.deepEqual(flow.edges[0].path[0], trail.stops[0].coordinates);
  assert.equal(flow.animateDots, false);
  assert.ok(flow.edges.every(edge => edge.w === 1));
  assert.deepEqual(flow.stops[0].coord, trail.stops[0].coordinates);
  assert.equal(flow.anchorStops, true);
  assert.ok(flow.stops.every(stop => !stop.badgeCoord), 'reader markers remain at the same anchors as their connections');
  assert.ok(flow.edges.every(edge => edge.amt));
});
test('broken continuity and missing source references fail before rendering', () => {
  const trail = load(); trail.legs[0].to = 'missing-stop';
  assert.throws(() => model.validate(trail), /leg references/);
  const unbacked = load(); unbacked.stops[0].sourceIds = ['missing-source'];
  assert.throws(() => model.validate(unbacked), /missing evidence/);
});
test('ownership and transport limitations survive the renderer adapter', () => {
  const trail = load(), flow = model.toFlow(trail);
  const leg = trail.legs.find(item => item.from === 'belgian-collection');
  const edge = flow.edges.find(item => item.id === leg.id);
  assert.equal(edge.relationship, leg.relationship);
  assert.equal(edge.geometryBasis, leg.geometryBasis);
  assert.equal(edge.limitations, leg.limitations);
  assert.deepEqual(edge.sourceIds, leg.sourceIds);
  assert.ok(edge.amt.includes(leg.limitations));
});
test('invalid coordinates and executable source URLs are rejected', () => {
  const trail = load(); trail.stops[0].coordinates = [190, 12];
  assert.throws(() => model.validate(trail), /coordinates/);
  const unsafe = load(); unsafe.sources[0].url = 'javascript:alert(1)';
  assert.throws(() => model.validate(unsafe), /protocol/);
});
test('share links restore the exact stop and tolerate unknown old stop links', () => {
  const trail = load();
  assert.equal(model.stepFromURL(trail, '?stop=' + trail.stops[3].id), 4);
  assert.equal(model.stepFromURL(trail, '?stop=lesson'), 7);
  assert.equal(model.stepFromURL(trail, '?stop=no-longer-exists'), 0);
});

test('connection focus distinguishes departure and return in the same country', () => {
  const trail = load();
  assert.deepEqual(model.focusForStep(trail, 1), {legIds: [trail.legs[0].id], stopNumbers: [1, 2]});
  assert.deepEqual(model.focusForStep(trail, 6), {legIds: [trail.legs[4].id], stopNumbers: [5, 6]});
  assert.deepEqual(model.focusForStep(trail, 3), {legIds: [trail.legs[1].id, trail.legs[2].id], stopNumbers: [2, 3, 4]});
  for (const [step, showAll] of [[0, false], [7, false], [3, true]]) {
    assert.deepEqual(model.focusForStep(trail, step, showAll), {legIds: null, stopNumbers: [1, 2, 3, 4, 5, 6]});
  }
});
