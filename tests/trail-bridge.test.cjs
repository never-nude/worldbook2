'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const model = require('../v2/js/trail-model.js');
const read = name => fs.readFileSync(path.join(__dirname, '..', 'v2', name), 'utf8');
const trail = JSON.parse(read('data/trails/duryodhana.json'));
const ORIGIN = 'https://worldbook.test';

function surface() {
  const listeners = new Map();
  return {
    addEventListener(type, callback) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(callback);
    },
    emit(type, event) { (listeners.get(type) || []).forEach(callback => callback(event)); }
  };
}
function element(tag = 'div') {
  return Object.assign(surface(), {
    tagName: tag, children: [], attributes: {}, style: {}, hidden: false, textContent: '',
    append(...nodes) { this.children.push(...nodes); },
    replaceChildren(...nodes) { this.children = nodes; },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    querySelector() { if (!this.span) this.span = element('span'); return this.span; },
    focus() { this.focused = true; }, scrollIntoView(options) { this.scrollRequest = options; }
  });
}
function rig(initiallyReady) {
  let layersReady = initiallyReady, id = 0;
  const parent = surface(), child = surface(), queue = [], delivered = [];
  const intervals = new Map(), timeouts = [], installed = [], mapHandlers = [], connectionFocus = [];
  const historyWrites = [];
  let mapHits = [];
  const nodes = new Map();
  const node = name => { if (!nodes.has(name)) nodes.set(name, element()); return nodes.get(name); };
  node('atlas').contentWindow = child;
  parent.postMessage = (data, target) => { assert.equal(target, ORIGIN); queue.push({receiver: parent, data, source: child, origin: ORIGIN}); };
  child.postMessage = (data, target) => { assert.equal(target, ORIGIN); queue.push({receiver: child, data, source: parent, origin: ORIGIN}); };
  const base = {
    URL, URLSearchParams, console, innerWidth: 1200,
    location: {origin: ORIGIN, search: '?trail=duryodhana', href: ORIGIN + '/v2/trails.html?trail=duryodhana&stop=new-york'},
    matchMedia: () => ({matches: false, addEventListener() {}}),
    WorldbookTrailModel: model,
    setInterval(callback) { intervals.set(++id, callback); return id; },
    clearInterval(key) { intervals.delete(key); },
    setTimeout(callback, delay) { timeouts.push({callback, delay}); return ++id; }
  };
  const map = {
    getSource: () => layersReady ? {} : null,
    getLayer: () => layersReady ? {} : null,
    on(...args) { mapHandlers.push(args); },
    easeTo() {}, setPaintProperty() {}, setLayoutProperty() {}, getZoom: () => 1,
    queryRenderedFeatures(point, options) {
      assert.deepEqual(Array.from(options.layers), ['flow-stop-labels', 'flow-stops-dot']);
      return mapHits;
    }
  };
  const result = {
    parent, child, node, installed, intervals, delivered, mapHandlers, connectionFocus, historyWrites,
    clickMap(features) {
      mapHits = features;
      mapHandlers.filter(args => args[0] === 'click').forEach(args => args[1]({point: {x: 100, y: 100}}));
      result.flush();
    },
    atlas() {
      const context = {...base, window: child, parent, location: {...base.location, search: '?reader=1'}};
      vm.runInNewContext(read('js/trail-atlas.js'), context);
      child.WorldbookTrailAtlas.mount({map, FLOWS: {}, META: {layers: []}, pause() {}, focusConnections(ids) { connectionFocus.push(ids); }, setLayer(key) { installed.push(key); }});
    },
    reader() {
      const context = {...base, window: parent, addEventListener: parent.addEventListener.bind(parent),
        document: {getElementById: node, createElement: element, createTextNode: content => ({textContent: content}), querySelectorAll: () => []},
        history: {pushState(...args) { historyWrites.push(args); }}, navigator: {clipboard: {writeText: async () => {}}},
        fetch: async () => ({ok: true, json: async () => trail})
      };
      vm.runInNewContext(read('js/trail-reader.js'), context);
    },
    flush() {
      for (let count = 0; queue.length; count++) {
        if (count > 100) throw new Error('Bridge message loop');
        const message = queue.shift(); delivered.push(message.data.type);
        message.receiver.emit('message', message);
      }
    },
    async settle() { await new Promise(resolve => setImmediate(resolve)); result.flush(); },
    ready() { layersReady = true; },
    tick() { [...intervals.values()].forEach(callback => callback()); result.flush(); },
    after(delay) { timeouts.filter(timer => timer.delay === delay).forEach(timer => timer.callback()); result.flush(); }
  };
  return result;
}

test('reader handshake recovers a ready message sent before its deferred script starts', async () => {
  const app = rig(true);
  app.atlas(); app.flush(); // No parent listener yet: the initial ready event is lost.
  assert.equal(app.installed.length, 0);
  app.reader(); await app.settle();
  assert.deepEqual(app.installed, ['flow_reader_duryodhana']);
  assert.equal(app.node('globe-status').hidden, true);
  assert.equal(app.intervals.size, 0, 'ready atlas does not leak a polling timer');
  const focused = app.delivered.filter(type => type === 'worldbook:focused');
  assert.equal(focused.length, 1);
  app.child.emit('message', {source: app.parent, origin: ORIGIN, data: {type: 'worldbook:hello'}});
  app.flush();
  assert.equal(app.installed.length, 1, 'repeated ready acknowledgments do not reinstall the case');
  assert.equal(app.mapHandlers.filter(args => args[0] === 'click').length, 1);
});

test('late atlas readiness recovers after the 45-second warning', async () => {
  const app = rig(false);
  app.reader(); app.flush(); // Initial parent probe is lost before the child script exists.
  app.atlas(); app.node('atlas').emit('load'); await app.settle();
  app.after(45000);
  assert.ok(app.delivered.includes('worldbook:error'));
  assert.equal(app.node('globe-status').hidden, false);
  assert.equal(app.installed.length, 0);
  app.ready(); app.tick();
  assert.deepEqual(app.installed, ['flow_reader_duryodhana']);
  assert.equal(app.node('globe-status').hidden, true);
  assert.equal(app.intervals.size, 0);
});

test('iframe load retries a parent probe lost before the child listener existed', async () => {
  const app = rig(true);
  app.reader(); app.flush();
  app.atlas(); app.flush(); await app.settle();
  // A frame load is also the synchronization point after a child document reload.
  const before = app.installed.length;
  app.node('atlas').emit('load'); app.flush();
  assert.equal(app.installed.length, before + 1);
  assert.equal(app.node('globe-status').hidden, true);
});

test('atlas rejects hello and installation from an untrusted origin or window', () => {
  const app = rig(true); app.atlas(); app.flush();
  const before = app.delivered.length;
  for (const identity of [{source: app.parent, origin: 'https://other.test'}, {source: {}, origin: ORIGIN}]) {
    for (const data of [{type: 'worldbook:hello'}, {type: 'worldbook:trail', trail, step: 5}]) {
      app.child.emit('message', {...identity, data});
    }
  }
  app.flush();
  assert.equal(app.delivered.length, before);
  assert.equal(app.installed.length, 0);
});

test('reader rejects forged ready and installed messages', async () => {
  const app = rig(false); app.reader(); await app.settle();
  const before = app.delivered.length;
  for (const identity of [{source: app.child, origin: 'https://other.test'}, {source: {}, origin: ORIGIN}]) {
    for (const data of [{type: 'worldbook:ready'}, {type: 'worldbook:installed'}]) {
      app.parent.emit('message', {...identity, data});
    }
  }
  app.flush();
  assert.equal(app.delivered.length, before, 'forged readiness does not send the trail');
  assert.equal(app.node('globe-status').hidden, false, 'forged installation cannot dismiss the loading status');
});

test('whole-trail toggle preserves the chapter, URL history and reading position', async () => {
  const app = rig(true); app.atlas(); app.reader(); await app.settle();
  const chapter = app.node('chapter'), content = chapter.children;
  chapter.scrollTop = 210;
  const initialFocus = app.connectionFocus.at(-1);
  assert.equal(initialFocus.length, 2, 'New York connects to the preceding and following records');
  app.node('overview').emit('click'); app.flush();
  assert.equal(app.connectionFocus.at(-1), null, 'overview restores all connections');
  assert.equal(app.node('overview').span.textContent, 'Focus stop');
  assert.equal(chapter.children, content, 'reading content is not replaced');
  assert.equal(chapter.scrollTop, 210);
  assert.equal(app.node('step-count').textContent, '5 of 6');
  assert.equal(app.historyWrites.length, 0);
  app.node('overview').emit('click'); app.flush();
  assert.deepEqual(app.connectionFocus.at(-1), initialFocus);
  app.node('overview').emit('click'); app.flush();
  app.node('next').emit('click'); app.flush();
  assert.equal(app.node('step-count').textContent, '6 of 6');
  assert.equal(app.node('overview').span.textContent, 'Whole trail');
  assert.deepEqual(app.connectionFocus.at(-1), [trail.legs.at(-1).id]);
  assert.equal(app.historyWrites.length, 1, 'only chapter navigation writes history');
});

test('an overview request before globe readiness survives installation', async () => {
  const app = rig(false); app.reader(); await app.settle();
  app.node('overview').emit('click');
  app.atlas(); app.ready(); app.tick();
  assert.equal(app.connectionFocus.at(-1), null);
  assert.equal(app.node('step-count').textContent, '5 of 6');
  assert.equal(app.node('overview').span.textContent, 'Focus stop');
});

test('returning to the globe keeps the chapter and history intact', async () => {
  const app = rig(true); app.atlas(); app.reader(); await app.settle();
  const content = app.node('chapter').children;
  app.node('return-globe').emit('click');
  assert.equal(app.node('globe').focused, true);
  assert.equal(app.node('globe').scrollRequest.block, 'start');
  assert.equal(app.node('chapter').children, content);
  assert.equal(app.historyWrites.length, 0);
});

test('rendered junctions and their number labels select the exact stop once', async () => {
  const app = rig(true); app.atlas(); app.reader(); await app.settle();
  app.clickMap([{layer: {id: 'flow-stop-labels'}, properties: {n: '1'}}, {layer: {id: 'flow-stops-dot'}, properties: {n: '6'}}]);
  assert.equal(app.node('step-count').textContent, '1 of 6', 'the top rendered label wins over a nearby node');
  assert.equal(app.historyWrites.length, 1);
  app.clickMap([{layer: {id: 'flow-stops-dot'}, properties: {n: '6'}}]);
  assert.equal(app.node('step-count').textContent, '6 of 6', 'return and departure in Cambodia stay distinct');
  assert.equal(app.historyWrites.length, 2);
  app.clickMap([]);
  assert.equal(app.historyWrites.length, 2, 'empty map space does not select a stop');
});
