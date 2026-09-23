(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.WorldbookTrailModel = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const COLORS = ['#e8c478', '#dcab7b', '#ca9187', '#aa94b9', '#83aaba', '#87bda9'];
  const safeId = value => typeof value === 'string' && /^[a-z0-9][a-z0-9_-]*$/.test(value);
  const text = value => typeof value === 'string' && value.trim().length > 0;
  function coordinates(value) {
    return Array.isArray(value) && value.length === 2 && value.every(Number.isFinite)
      && Math.abs(value[0]) <= 180 && Math.abs(value[1]) <= 90;
  }
  function validate(trail) {
    const fail = message => { throw new Error('Invalid trail: ' + message); };
    if (!trail || !safeId(trail.id) || !text(trail.title) || !text(trail.question)) fail('identity or question');
    if (!Array.isArray(trail.stops) || trail.stops.length < 2) fail('at least two stops are required');
    if (!Array.isArray(trail.sources) || !trail.sources.length || !Array.isArray(trail.legs)) fail('sources and legs');
    const sources = new Set(), stops = new Set(), legs = new Set();
    trail.sources.forEach(source => {
      if (!safeId(source.id) || sources.has(source.id) || !text(source.title)) fail('source identity');
      let url; try { url = new URL(source.url); } catch (_) { fail('source URL'); }
      if (url.protocol !== 'https:' && url.protocol !== 'http:') fail('source URL protocol');
      sources.add(source.id);
    });
    const refs = (record, label) => {
      if (!Array.isArray(record.sourceIds) || !record.sourceIds.length || record.sourceIds.some(id => !sources.has(id))) fail(label + ' has missing evidence references');
    };
    trail.stops.forEach((stop, index) => {
      if (!safeId(stop.id) || stops.has(stop.id) || stop.number !== index + 1) fail('stop identity/order');
      if (!coordinates(stop.coordinates) || (stop.displayCoordinates && !coordinates(stop.displayCoordinates))) fail('stop coordinates');
      if (!text(stop.locationPrecision) || !text(stop.summary) || !text(stop.evidenceStatus)) fail('stop meaning or precision');
      refs(stop, 'stop ' + stop.id); stops.add(stop.id);
    });
    trail.legs.forEach(leg => {
      if (!safeId(leg.id) || legs.has(leg.id) || !stops.has(leg.from) || !stops.has(leg.to) || leg.from === leg.to) fail('leg references');
      if (!text(leg.relationship) || !text(leg.geometryBasis) || !text(leg.summary)) fail('leg semantics');
      refs(leg, 'leg ' + leg.id); legs.add(leg.id);
    });
    return trail;
  }
  function toFlow(input) {
    const trail = validate(input), byId = new Map(trail.stops.map(stop => [stop.id, stop]));
    const countryColors = {};
    trail.stops.forEach(stop => { if (stop.countryIso) countryColors[stop.countryIso] = '#27454d'; });
    return {
      label: trail.title, group: 'Forensic trails', geo: true, disableCountryFocus: true,
      showCountryLabels: false, illuminateCountries: false, animateDots: false, compactStops: false, anchorStops: true,
      color: COLORS[0], dotColor: '#f8e8c5', unit: 'documented records; lines do not encode quantity',
      desc: trail.summary, legend: trail.question, note: 'Connections link evidence records. They are not reconstructed transport routes.',
      weightNote: 'Equal line widths; color and number indicate stop order, not quantity or certainty.',
      highlightCountryColors: countryColors,
      sources: trail.sources.map(source => ({label: source.publisher + ' — ' + source.title, url: source.url})),
      stops: trail.stops.map((stop, i) => ({
        n: stop.number, coord: stop.coordinates,
        place: stop.place, year: stop.date, carrier: stop.summary, color: COLORS[i % COLORS.length]
      })),
      edges: trail.legs.map(leg => {
        const from = byId.get(leg.from), to = byId.get(leg.to);
        return {id: leg.id, from: from.countryIso, to: to.countryIso, w: 1,
          nm: from.place + ' → ' + to.place,
          relationship: leg.relationship, geometryBasis: leg.geometryBasis,
          limitations: leg.limitations, sourceIds: [...leg.sourceIds],
          amt: [leg.summary, leg.relationship, leg.geometryBasis, Array.isArray(leg.limitations) ? leg.limitations.join(' ') : leg.limitations].filter(Boolean).join(' · '),
          c: COLORS[(to.number - 1) % COLORS.length], path: [from.coordinates, to.coordinates]};
      })
    };
  }
  function stepFromURL(trail, url) {
    const id = new URL(url, 'https://worldbook.earth/').searchParams.get('stop');
    if (id === 'lesson') return trail.stops.length + 1;
    const index = trail.stops.findIndex(stop => stop.id === id);
    return index < 0 ? 0 : index + 1;
  }
  function focusForStep(trail, step, showAll = false) {
    const stop = Number.isInteger(step) ? trail.stops[step - 1] : null;
    if (!stop || showAll) return {legIds: null, stopNumbers: trail.stops.map(item => item.number)};
    const legs = trail.legs.filter(leg => leg.from === stop.id || leg.to === stop.id);
    const connected = new Set([stop.id, ...legs.flatMap(leg => [leg.from, leg.to])]);
    return {legIds: legs.map(leg => leg.id), stopNumbers: trail.stops.filter(item => connected.has(item.id)).map(item => item.number)};
  }
  return {COLORS, validate, toFlow, stepFromURL, focusForStep};
});
