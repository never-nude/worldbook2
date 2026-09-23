(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const el = (tag, className, content) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content != null) node.textContent = content;
    return node;
  };
  const items = value => Array.isArray(value) ? value : value ? [value] : [];
  let trail, step = 0, mapReady = false, paused = true, installSent = false, mapOverview = false;
  const frame = $('atlas'), chapter = $('chapter');
  const post = (type, fields = {}) => frame.contentWindow.postMessage({type, ...fields}, location.origin);
  function install() {
    if (mapReady && trail && !installSent) { installSent = true; post('worldbook:trail', {trail, step, showAll: mapOverview}); }
  }
  function setMotion(value) {
    paused = value;
    $('motion').setAttribute('aria-pressed', String(!paused));
    $('motion').querySelector('span').textContent = paused ? 'Rotate globe' : 'Pause globe';
    $('motion').setAttribute('aria-label', paused ? 'Rotate globe' : 'Pause globe');
  }
  function renderMapState() {
    if (!trail) return;
    const selected = step > 0 && step <= trail.stops.length ? trail.stops[step - 1] : null;
    const label = selected && (selected.shortLabel || selected.place.split(',')[0]);
    const overview = $('overview');
    overview.querySelector('span').textContent = selected && mapOverview ? 'Focus stop' : 'Whole trail';
    overview.setAttribute('aria-pressed', String(!selected || mapOverview));
    const action = selected && mapOverview ? 'Focus on stop ' + step + ': ' + label
      : selected ? 'Show the whole trail and keep stop ' + step + ' selected' : 'Reset the whole-trail view';
    overview.setAttribute('aria-label', action);
    overview.setAttribute('title', action);
    $('map-caption').textContent = !selected ? 'One object. ' + trail.stops.length + ' stops. A trail through the records.'
      : mapOverview ? 'Whole trail · ' + label + ' remains selected.'
      : 'Stop ' + step + ' of ' + trail.stops.length + ' · ' + label + '. Bright lines connect this record; other connections stay visible.';
  }
  function sourceList(ids) {
    const list = el('ul', 'source-list');
    [...new Set(ids)].forEach(id => {
      const source = trail.sources.find(record => record.id === id);
      if (!source) return;
      const row = el('li'), link = el('a', '', source.title);
      link.href = source.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
      row.append(link, el('small', '', [source.publisher, source.published || source.publicationDate, source.locator].filter(Boolean).join(' · ')));
      list.append(row);
    });
    return list;
  }
  function note(title, values) {
    const box = el('div', 'reading-note');
    box.append(el('strong', '', title));
    items(values).forEach(value => box.append(el('p', '', value)));
    return box;
  }
  function evidence(record) {
    const section = el('section', 'evidence');
    section.append(el('h3', '', 'How we know'), sourceList(record.sourceIds));
    if (items(record.limitations).length) {
      const detail = el('details'), summary = el('summary', '', 'What these records don’t establish');
      detail.append(summary);
      items(record.limitations).forEach(value => detail.append(el('p', '', value)));
      section.append(detail);
    }
    return section;
  }
  function renderOverview() {
    chapter.append(el('p', 'chapter-kicker', trail.period), el('h2', '', trail.title), el('p', 'chapter-copy', trail.summary));
    const meta = el('div', 'case-meta');
    [[String(trail.stops.length), 'stops in the record'], [String(trail.sources.length), 'primary sources'], ['1', 'object to follow']].forEach(([number, caption]) => {
      const item = el('div'); item.append(el('strong', '', number), el('span', '', caption)); meta.append(item);
    });
    chapter.append(meta, note('Read the connections', 'Some lines trace reported movement; others connect sale, ownership, or return records. They do not reconstruct the exact journey between places.'));
    chapter.append(el('p', 'chapter-copy', 'Follow the numbered stops. At each one, look at what changed—and which record lets us say so.'));
  }
  function renderStop(stop) {
    const kicker = el('p', 'chapter-kicker'); kicker.append(el('i'), document.createTextNode(stop.date));
    chapter.append(kicker, el('h2', '', stop.title), el('p', 'chapter-place', stop.place + ' · ' + stop.locationPrecision));
    const status = el('div', 'evidence-label');
    status.append(el('strong', '', 'Evidence'), el('span', '', stop.evidenceStatus.replace(/[-_]/g, ' ')));
    chapter.append(status, el('p', 'chapter-copy', stop.summary));
    if (stop.role) chapter.append(note('What changes here', stop.role));
    chapter.append(evidence(stop));
    const outgoing = trail.legs.filter(leg => leg.from === stop.id);
    outgoing.forEach(leg => {
      const next = trail.stops.find(item => item.id === leg.to), section = el('section', 'connection');
      section.append(el('h3', '', 'The next connection'), el('p', '', leg.summary), el('p', 'relationship', [leg.relationship, leg.geometryBasis].join(' · ')));
      if (items(leg.limitations).length) section.append(el('p', '', items(leg.limitations).join(' ')));
      const sources = el('details'); sources.append(el('summary', '', 'Evidence for this connection'), sourceList(leg.sourceIds)); section.append(sources);
      if (next) section.setAttribute('aria-label', 'Connection to ' + next.place);
      chapter.append(section);
    });
  }
  function renderLesson() {
    chapter.append(el('p', 'chapter-kicker', 'Follow the records'), el('h2', '', 'What the trail reveals'), el('p', 'chapter-copy', trail.lesson));
    const takeaways = el('ul', 'takeaways'); items(trail.takeaways).forEach(value => takeaways.append(el('li', '', value))); chapter.append(takeaways);
    if (items(trail.unknowns).length) chapter.append(note('Still unknown', trail.unknowns));
    const section = el('section', 'evidence'); section.append(el('h3', '', 'The source record'), sourceList(trail.sources.map(source => source.id))); chapter.append(section);
  }
  function render(options = {}) {
    if (!trail) return;
    chapter.replaceChildren();
    if (step === 0) renderOverview();
    else if (step === trail.stops.length + 1) renderLesson();
    else renderStop(trail.stops[step - 1]);
    $('chapter-label').textContent = step === 0 ? 'The question' : step > trail.stops.length ? 'The bigger picture' : 'Stop ' + String(step).padStart(2, '0') + ' / ' + String(trail.stops.length).padStart(2, '0');
    $('step-count').textContent = step > 0 && step <= trail.stops.length ? step + ' of ' + trail.stops.length : '';
    $('progress-fill').style.width = 100 * step / (trail.stops.length + 1) + '%';
    $('previous').disabled = step === 0;
    $('next').textContent = step === 0 ? 'Follow the trail →' : step === trail.stops.length ? 'What it reveals →' : step > trail.stops.length ? 'Start again ↺' : 'Next stop →';
    document.querySelectorAll('.stop-button').forEach((button, i) => {
      if (i + 1 === step) button.setAttribute('aria-current', 'step'); else button.removeAttribute('aria-current');
    });
    $('reader-status').textContent = '';
    if (options.writeHistory) {
      const url = new URL(location.href); url.searchParams.set('trail', trail.id);
      if (step === 0) url.searchParams.delete('stop'); else url.searchParams.set('stop', step > trail.stops.length ? 'lesson' : trail.stops[step - 1].id);
      history.pushState({step}, '', url);
    }
    setMotion(true);
    renderMapState();
    if (mapReady && installSent) post('worldbook:focus', {step, showAll: mapOverview});
    if (options.focus) {
      // Keep the itinerary visible when choosing a stop, while bringing the newly
      // selected text into view on phones and resetting the desktop reading panel.
      if (innerWidth > 760) chapter.scrollTop = 0;
      chapter.focus({preventScroll: true});
      if (innerWidth <= 760) $('reader').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
    }
  }
  function go(next, focus = true) {
    step = Math.max(0, Math.min(trail.stops.length + 1, next));
    mapOverview = false;
    render({writeHistory: true, focus});
  }
  window.addEventListener('message', event => {
    if (event.source !== frame.contentWindow || event.origin !== location.origin || !event.data) return;
    const data = event.data;
    if (data.type === 'worldbook:ready') { mapReady = true; install(); }
    if (data.type === 'worldbook:installed') { $('globe-status').hidden = true; }
    if (data.type === 'worldbook:select' && trail && Number.isInteger(data.step) && data.step > 0 && data.step <= trail.stops.length) go(data.step);
    if (data.type === 'worldbook:motion' || data.type === 'worldbook:focused') setMotion(data.paused !== false);
    if (data.type === 'worldbook:error') { $('globe-status').textContent = 'The globe is unavailable. Every stop and source remains readable.'; $('globe-status').hidden = false; }
  });
  // Probe after our listener exists, and again once the iframe has finished loading.
  // This covers both startup orders and allows a reloaded iframe to reinstall the case.
  frame.addEventListener('load', () => {
    mapReady = false; installSent = false;
    post('worldbook:hello');
  });
  post('worldbook:hello');
  $('previous').addEventListener('click', () => { if (trail) go(step - 1); });
  $('next').addEventListener('click', () => { if (trail) go(step > trail.stops.length ? 0 : step + 1); });
  $('overview').addEventListener('click', () => {
    if (!trail) return;
    mapOverview = step > 0 && step <= trail.stops.length ? !mapOverview : false;
    setMotion(true);
    renderMapState();
    if (mapReady && installSent) post('worldbook:focus', {step, showAll: mapOverview});
  });
  $('return-globe').addEventListener('click', () => {
    const globe = $('globe');
    globe.focus({preventScroll: true});
    globe.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
  });
  $('motion').addEventListener('click', () => { if (mapReady) { setMotion(!paused); post('worldbook:motion', {paused}); } });
  $('zoom-in').addEventListener('click', () => post('worldbook:zoom', {direction: 1}));
  $('zoom-out').addEventListener('click', () => post('worldbook:zoom', {direction: -1}));
  $('share').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); $('reader-status').textContent = 'Link copied to this point in the trail.'; }
    catch (_) { $('reader-status').textContent = 'Copy the page address to share this point in the trail.'; }
  });
  addEventListener('popstate', () => { if (trail) { step = WorldbookTrailModel.stepFromURL(trail, location.href); mapOverview = false; render(); } });
  const requested = new URLSearchParams(location.search).get('trail') || 'duryodhana';
  if (requested !== 'duryodhana') {
    chapter.replaceChildren(el('h2', '', 'This trail is not available yet.'), el('p', 'chapter-copy', 'Open the first fieldnote to follow a Cambodian statue through the records.'));
    const link = el('a', '', 'Open the statue trail →'); link.href = 'trails.html?trail=duryodhana'; chapter.append(link);
    $('next').disabled = true; $('previous').disabled = true;
    return;
  }
  fetch('data/trails/' + requested + '.json').then(response => {
    if (!response.ok) throw new Error('Trail content could not be loaded');
    return response.json();
  }).then(input => {
    trail = WorldbookTrailModel.validate(input);
    document.title = trail.title + ' — Worldbook';
    $('trail-question').textContent = trail.question;
    const list = $('stop-list');
    trail.stops.forEach(stop => {
      const row = el('li'), button = el('button', 'stop-button'); button.type = 'button';
      button.append(el('span', 'stop-number', stop.number), el('span', 'stop-name', stop.shortLabel || stop.place.split(',')[0]));
      button.setAttribute('aria-label', 'Stop ' + stop.number + ': ' + stop.place);
      button.addEventListener('click', () => go(stop.number)); row.append(button); list.append(row);
    });
    step = WorldbookTrailModel.stepFromURL(trail, location.href); render(); install();
  }).catch(error => {
    chapter.replaceChildren(el('h2', '', 'The trail couldn’t load.'), el('p', 'chapter-copy', 'Please reload to try again. The full atlas remains available from the link above.'));
    $('next').disabled = true; $('previous').disabled = true;
    console.error(error);
  });
  setTimeout(() => { if (!mapReady) $('globe-status').textContent = 'The globe is taking longer to load. You can still follow the story.'; }, 20000);
})();
