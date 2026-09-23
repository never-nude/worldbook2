(function () {
  'use strict';
  window.WorldbookTrailAtlas = {
    mount(api) {
      if (!new URLSearchParams(location.search).has('reader') || parent === window) return;
      const {map, FLOWS, META} = api;
      const reduced = matchMedia('(prefers-reduced-motion: reduce)');
      let trail = null, ready = false, active = 0, poll = null;
      const send = (type, fields = {}) => parent.postMessage({type, ...fields}, location.origin);
      function focus(step, animate, showAll = false) {
        if (!trail) return;
        active = Math.max(0, Math.min(trail.stops.length + 1, Number(step) || 0));
        api.pause(true);
        const stop = trail.stops[active - 1];
        const connections = WorldbookTrailModel.focusForStep(trail, active, showAll);
        api.focusConnections(connections.legIds);
        // Color the polygon interiors only. Blurred/offset border blooms create
        // spill and faceting around narrow coastlines at close zoom levels.
        const countries = [...new Set(trail.stops.map(item => item.countryIso).filter(Boolean))];
        if (map.getLayer('fills')) {
          map.setPaintProperty('fills', 'fill-color', ['case',
            ['==', ['get', 'iso3'], stop?.countryIso || ''], '#2d505a',
            ['in', ['get', 'iso3'], ['literal', countries]], '#27454d', '#192933']);
          map.setPaintProperty('fills', 'fill-opacity', 1);
        }
        if (map.getLayer('borders')) {
          map.setPaintProperty('borders', 'line-color', ['case',
            ['==', ['get', 'iso3'], stop?.countryIso || ''], '#79a6ad', '#41535e']);
        }
        const small = innerWidth < 600;
        const target = stop && !showAll ? stop.coordinates : [30, 28];
        map.easeTo({center: target, zoom: stop && !showAll ? (small ? 1.6 : 2.05) : (small ? 0.65 : 1.1),
          bearing: 0, pitch: 0, padding: {top: 0, right: 0, bottom: 0, left: 0},
          duration: animate && !reduced.matches ? 850 : 0});
        const chosen = stop ? String(stop.number) : '';
        const selected = ['==', ['get', 'n'], chosen];
        if (map.getLayer('flow-stops-ring')) {
          // Junctions stay on their geographic anchors. Only the small number
          // labels move around them to avoid collisions in crowded regions.
          map.setPaintProperty('flow-stops-ring', 'circle-radius', ['case', selected, 7, 4.5]);
          map.setPaintProperty('flow-stops-dot', 'circle-radius', ['case', selected, 4, 2.5]);
          map.setPaintProperty('flow-stops-ring', 'circle-stroke-width', ['case', selected, 2, 1]);
          map.setPaintProperty('flow-stops-ring', 'circle-stroke-color', ['case', selected, '#fff7df', ['get', 'c']]);
          for (const id of ['flow-stops-ring', 'flow-stops-dot']) map.setLayoutProperty(id, 'circle-sort-key', ['case', selected, 1, 0]);
          map.setPaintProperty('flow-stop-labels', 'text-color', ['case', selected, '#fff7df', ['get', 'c']]);
        }
        const connected = ['in', ['to-number', ['get', 'n']], ['literal', connections.stopNumbers]];
        [['flow-stops-ring', 'circle-opacity'], ['flow-stops-ring', 'circle-stroke-opacity'], ['flow-stops-dot', 'circle-opacity'], ['flow-stops-dot', 'circle-stroke-opacity'], ['flow-stop-labels', 'text-opacity'], ['flow-stop-leaders', 'line-opacity']].forEach(([id, property]) => {
          if (map.getLayer(id)) map.setPaintProperty(id, property, ['case', connected, 1, 0.28]);
        });
        send('worldbook:focused', {step: active, paused: true});
      }
      function install(input, step, showAll) {
        trail = WorldbookTrailModel.validate(input);
        const flowKey = 'reader_' + trail.id, layerKey = 'flow_' + flowKey;
        FLOWS[flowKey] = WorldbookTrailModel.toFlow(trail);
        if (!META.layers.some(layer => layer.key === layerKey)) META.layers.push({key: layerKey, type: 'flow', flowKey, label: trail.title, group: 'Forensic trails', hidden: true});
        api.setLayer(layerKey);
        map.setLayoutProperty('flow-stop-labels', 'text-size', 13);
        map.setLayoutProperty('flow-stop-labels', 'text-variable-anchor', ['top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right']);
        map.setLayoutProperty('flow-stop-labels', 'text-radial-offset', 1.1);
        map.setLayoutProperty('flow-stop-labels', 'text-allow-overlap', false);
        map.setLayoutProperty('flow-stop-labels', 'text-ignore-placement', false);
        map.setLayoutProperty('flow-stop-labels', 'text-padding', 3);
        map.setPaintProperty('flow-stop-labels', 'text-halo-color', '#07111a');
        map.setPaintProperty('flow-stop-labels', 'text-halo-width', 2);
        // Keep the basemap subordinate to the trail, with no coastline bloom.
        if (map.getLayer('ocean')) map.setPaintProperty('ocean', 'fill-color', '#101e27');
        if (map.getLayer('borders')) {
          map.setPaintProperty('borders', 'line-color', '#41535e');
          map.setPaintProperty('borders', 'line-width', 0.8);
          map.setPaintProperty('borders', 'line-opacity', 0.6);
        }
        focus(step, false, showAll);
        send('worldbook:installed', {trailId: trail.id});
      }
      window.addEventListener('message', event => {
        if (event.source !== parent || event.origin !== location.origin || !event.data) return;
        const message = event.data;
        // The parent's deferred script may start after our first ready message.
        // A probe always gets the current readiness instead of relying on that event.
        if (message.type === 'worldbook:hello') {
          if (ready) send('worldbook:ready'); else check();
          return;
        }
        if (!ready) return;
        try {
          if (message.type === 'worldbook:trail') install(message.trail, message.step, message.showAll === true);
          if (message.type === 'worldbook:focus') focus(message.step, true, message.showAll === true);
          if (message.type === 'worldbook:motion') {
            api.pause(message.paused !== false);
            send('worldbook:motion', {paused: message.paused !== false});
          }
          if (message.type === 'worldbook:zoom') map.easeTo({zoom: Math.max(0, Math.min(5, map.getZoom() + (message.direction === 1 ? 0.4 : -0.4))), duration: reduced.matches ? 0 : 200});
        } catch (error) { send('worldbook:error', {message: 'The trail could not be drawn. Its evidence is still available in the reader.'}); console.error(error); }
      });
      function check() {
        if (ready || !map.getSource('flow-stops') || !map.getLayer('fills')) return;
        ready = true; clearInterval(poll); api.pause(true);
        map.on('click', event => {
          const hits = map.queryRenderedFeatures(event.point, {layers: ['flow-stop-labels', 'flow-stops-dot']});
          const step = Number(hits[0]?.properties?.n);
          if (trail && Number.isInteger(step) && step > 0 && step <= trail.stops.length) send('worldbook:select', {step});
        });
        map.on('dragstart', () => { api.pause(true); send('worldbook:motion', {paused: true}); });
        send('worldbook:ready');
      }
      poll = setInterval(check, 250); check();
      // Slow/background loads remain recoverable when the atlas eventually finishes.
      setTimeout(() => { if (!ready) send('worldbook:error', {message: 'The globe is taking longer to load. You can still follow every stop below.'}); }, 45000);
      reduced.addEventListener('change', () => { if (reduced.matches) { api.pause(true); send('worldbook:motion', {paused: true}); } });
    }
  };
})();
