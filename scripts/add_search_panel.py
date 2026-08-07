#!/usr/bin/env python3
"""One-off script: add a search/filter side panel (name, date range,
Klubnacht performance count, style tags) to index.html. Filter controls
live in the panel; results render into the main #floors area (full width,
fully interactive, no modal scrim) reusing renderRow(). See conversation
for the chat-approved design (revised after visual feedback on a first
pass: no scrim, range sliders not number inputs, dark-themed date input,
expandable tag list, results out of the panel)."""
import re

HTML_PATH = "index.html"

with open(HTML_PATH) as f:
    html = f.read()

# 1. CSS
old_css_tail = """  .avatar-flag {
    position: absolute; right: -4px; bottom: -4px;
    width: 17px; height: 17px; border-radius: 50%;
    background: var(--surface); border: 2px solid var(--surface);
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; line-height: 1;
    box-shadow: 0 0 0 1px var(--rule);
  }
</style>"""
new_css_tail = """  .avatar-flag {
    position: absolute; right: -4px; bottom: -4px;
    width: 17px; height: 17px; border-radius: 50%;
    background: var(--surface); border: 2px solid var(--surface);
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; line-height: 1;
    box-shadow: 0 0 0 1px var(--rule);
  }

  .toggle-row { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-5); }
  .toggle-row .toggle { margin-bottom: 0; flex: 1; min-width: 0; }
  .search-icon-btn {
    flex: none; width: 40px; height: 40px; background: var(--surface); border: 1px solid var(--rule);
    color: var(--fg); cursor: pointer; display: flex; align-items: center; justify-content: center;
    padding: 0;
  }
  .search-icon-btn:hover, .search-icon-btn.active { border-color: var(--fg); }
  .search-icon-btn svg { width: 18px; height: 18px; }

  .search-panel {
    display: none; position: fixed; top: 0; right: 0; bottom: 0; width: 320px; max-width: 92vw;
    background: var(--surface); border-left: 1px solid var(--rule); z-index: 15;
    flex-direction: column;
  }
  .search-panel.open { display: flex; }
  .search-panel-head {
    display: flex; align-items: center; justify-content: space-between;
    padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--rule); flex: none;
  }
  .search-panel-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
  .search-panel-close { background: none; border: none; color: var(--muted); font-size: 22px; line-height: 1; cursor: pointer; padding: 0; }
  .search-panel-close:hover { color: var(--fg); }
  .search-panel-body { padding: var(--space-4); overflow-y: auto; flex: 1; }

  @media (min-width: 900px) {
    body.search-open .page { padding-right: 344px; }
  }

  .field { margin-bottom: var(--space-4); }
  .field-label { display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-bottom: var(--space-2); }
  .field input[type="text"], .field input[type="date"] {
    width: 100%; background: var(--bg); border: 1px solid var(--rule); color: var(--fg);
    font-family: var(--font); font-size: 14px; padding: 9px 10px; color-scheme: dark;
  }
  .field input:focus { outline: none; border-color: var(--berghain); }
  .field input::placeholder { color: var(--muted); }
  .field-row-2 { display: flex; gap: var(--space-2); }
  .field-row-2 > * { flex: 1; min-width: 0; }
  .field-row-2-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; display: block; }

  .range-field { margin-bottom: var(--space-3); }
  .range-field-label { display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
  .range-field-label b { color: var(--fg); font-variant-numeric: tabular-nums; }
  .range-field input[type="range"] { width: 100%; accent-color: var(--berghain); }

  .tag-toggle {
    display: inline-block; padding: 3px 9px; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.05em; border: 1px solid var(--rule); color: var(--muted);
    cursor: pointer; margin: 0 6px 6px 0; background: none; font-family: var(--font);
  }
  .tag-toggle.active { border-color: var(--berghain); color: var(--berghain); }
  .tag-toggle.tag-hidden { display: none; }
  .tag-more-btn {
    display: block; background: none; border: none; color: var(--muted); font-family: var(--font);
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; text-decoration: underline;
    cursor: pointer; padding: 2px 0;
  }
  .tag-more-btn:hover { color: var(--fg); }

  .search-results {
    display: block; width: 100%;
  }
  .search-results-count {
    font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em;
    margin-bottom: var(--space-3);
  }
</style>"""
assert old_css_tail in html
html = html.replace(old_css_tail, new_css_tail, 1)

# 2. Markup: nav header gets the search icon; panel added after #floors (no scrim)
old_markup = """  <header class="toggle" id="toggle"></header>
  <div class="floors" id="floors"></div>
</div>"""
new_markup = """  <div class="toggle-row">
    <header class="toggle" id="toggle"></header>
    <button class="search-icon-btn" id="search-open" aria-label="Search and filter DJs">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="10.5" cy="10.5" r="6.5"/><line x1="20" y1="20" x2="15.3" y2="15.3"/></svg>
    </button>
  </div>
  <div class="floors" id="floors"></div>
</div>

<aside class="search-panel" id="search-panel" aria-hidden="true">
  <div class="search-panel-head">
    <span class="search-panel-title">Search &amp; Filter</span>
    <button class="search-panel-close" id="search-close" aria-label="Close">&times;</button>
  </div>
  <div class="search-panel-body">
    <div class="field">
      <label class="field-label" for="search-name">Name</label>
      <input type="text" id="search-name" placeholder="e.g. Marcel, Steffi…">
    </div>
    <div class="field">
      <label class="field-label">Playing between</label>
      <div class="field-row-2">
        <div><span class="field-row-2-label">From</span><input type="date" id="search-date-from"></div>
        <div><span class="field-row-2-label">To</span><input type="date" id="search-date-to"></div>
      </div>
    </div>
    <div class="field">
      <label class="field-label">Klubnacht performances</label>
      <div class="range-field">
        <div class="range-field-label"><span>Min</span><b id="search-perf-min-val">0</b></div>
        <input type="range" id="search-perf-min" min="0" max="0" value="0">
      </div>
      <div class="range-field">
        <div class="range-field-label"><span>Max</span><b id="search-perf-max-val">0</b></div>
        <input type="range" id="search-perf-max" min="0" max="0" value="0">
      </div>
    </div>
    <div class="field">
      <label class="field-label">Style</label>
      <div id="search-tags"></div>
    </div>
  </div>
</aside>"""
assert old_markup in html
html = html.replace(old_markup, new_markup, 1)

# 3. JS
old_js = """document.getElementById('toggle').addEventListener('click', (e) => {
  const btn = e.target.closest('.toggle-btn');
  if (btn) setDay(btn.dataset.date);
});

document.addEventListener('click', (e) => {
  if (e.target.closest('a')) return;
  const row = e.target.closest('.dj-row');
  if (row && !row.classList.contains('dj-row--empty')) row.classList.toggle('expanded');
});

let DATA = null;

async function init() {
  try {
    const res = await fetch('data/lineup.json');
    if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
    DATA = await res.json();
    renderNav();
    setDay(pickDefaultDate(DATA.days));
    const activeBtn = document.querySelector('.toggle-btn.active');
    if (activeBtn) activeBtn.scrollIntoView({ inline: 'center', block: 'nearest' });
  } catch (err) {
    document.getElementById('floors').innerHTML = '<div class="day-empty">Couldn\\'t load the programme. Try reloading.</div>';
  }
}

init();"""

new_js = """let currentDate = null;

document.getElementById('toggle').addEventListener('click', (e) => {
  const btn = e.target.closest('.toggle-btn');
  if (btn) {
    if (searchOpen) closeSearchPanel();
    setDay(btn.dataset.date);
  }
});

document.addEventListener('click', (e) => {
  if (e.target.closest('a')) return;
  const row = e.target.closest('.dj-row');
  if (row && !row.classList.contains('dj-row--empty')) row.classList.toggle('expanded');
});

const TAGS_VISIBLE_DEFAULT = 12;
const searchState = { name: '', dateFrom: '', dateTo: '', perfMin: 0, perfMax: 0, tags: new Set() };
let searchOpen = false;
let searchTagsRendered = false;

function renderTagOptions() {
  const allTags = new Set();
  Object.values(DATA.djs).forEach(dj => (dj.tags || []).forEach(t => allTags.add(t)));
  const sorted = [...allTags].sort((a, b) => a.localeCompare(b));
  const el = document.getElementById('search-tags');
  const buttons = sorted.map((t, i) =>
    `<button type="button" class="tag-toggle${i >= TAGS_VISIBLE_DEFAULT ? ' tag-hidden' : ''}" data-tag="${esc(t)}">${esc(t)}</button>`
  ).join('');
  const extra = sorted.length - TAGS_VISIBLE_DEFAULT;
  const moreBtn = extra > 0 ? `<button type="button" class="tag-more-btn" id="tag-more-btn">+${extra} more</button>` : '';
  el.innerHTML = buttons + moreBtn;
  const moreBtnEl = document.getElementById('tag-more-btn');
  if (moreBtnEl) {
    moreBtnEl.addEventListener('click', () => {
      const hidden = el.querySelectorAll('.tag-hidden');
      const expanding = hidden.length > 0;
      hidden.forEach(b => b.classList.remove('tag-hidden'));
      if (expanding) {
        moreBtnEl.textContent = 'Show less';
      } else {
        [...el.querySelectorAll('.tag-toggle')].slice(TAGS_VISIBLE_DEFAULT).forEach(b => b.classList.add('tag-hidden'));
        moreBtnEl.textContent = `+${extra} more`;
      }
    });
  }

  const maxCount = Math.max(0, ...Object.values(DATA.djs).map(dj => (dj.stats ? dj.stats.performanceCount : 0)));
  const minSlider = document.getElementById('search-perf-min');
  const maxSlider = document.getElementById('search-perf-max');
  minSlider.max = String(maxCount);
  maxSlider.max = String(maxCount);
  maxSlider.value = String(maxCount);
  searchState.perfMax = maxCount;
  document.getElementById('search-perf-max-val').textContent = String(maxCount);
  searchTagsRendered = true;
}

function djMatchesSearch(slug) {
  const dj = DATA.djs[slug];
  if (searchState.name && !dj.name.toLowerCase().includes(searchState.name.toLowerCase())) return false;
  if (searchState.dateFrom || searchState.dateTo) {
    const inRange = (dj.appearances || []).some(a =>
      (!searchState.dateFrom || a.date >= searchState.dateFrom) &&
      (!searchState.dateTo || a.date <= searchState.dateTo)
    );
    if (!inRange) return false;
  }
  const maxCount = Number(document.getElementById('search-perf-max').max);
  if (searchState.perfMin > 0 || searchState.perfMax < maxCount) {
    if (!dj.stats) return false;
    if (dj.stats.performanceCount < searchState.perfMin) return false;
    if (dj.stats.performanceCount > searchState.perfMax) return false;
  }
  if (searchState.tags.size > 0 && !(dj.tags || []).some(t => searchState.tags.has(t))) return false;
  return true;
}

function renderSearchResults() {
  const matches = Object.keys(DATA.djs).filter(djMatchesSearch).sort((a, b) => DATA.djs[a].name.localeCompare(DATA.djs[b].name));
  const countLabel = `${matches.length} DJ${matches.length === 1 ? '' : 's'} match`;
  document.getElementById('floors').innerHTML =
    `<div class="search-results"><div class="search-results-count">${countLabel}</div>${matches.map(renderRow).join('')}</div>`;
}

function openSearchPanel() {
  if (!searchTagsRendered) renderTagOptions();
  searchOpen = true;
  document.getElementById('search-panel').classList.add('open');
  document.getElementById('search-panel').setAttribute('aria-hidden', 'false');
  document.getElementById('search-open').classList.add('active');
  document.body.classList.add('search-open');
  renderSearchResults();
  document.getElementById('search-name').focus();
}

function closeSearchPanel() {
  searchOpen = false;
  document.getElementById('search-panel').classList.remove('open');
  document.getElementById('search-panel').setAttribute('aria-hidden', 'true');
  document.getElementById('search-open').classList.remove('active');
  document.body.classList.remove('search-open');
  if (currentDate) {
    const day = DATA.days.find(d => d.date === currentDate);
    if (day) renderFloors(day);
  }
}

document.getElementById('search-open').addEventListener('click', () => {
  if (searchOpen) closeSearchPanel(); else openSearchPanel();
});
document.getElementById('search-close').addEventListener('click', closeSearchPanel);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && searchOpen) closeSearchPanel();
});

document.getElementById('search-name').addEventListener('input', (e) => {
  searchState.name = e.target.value;
  renderSearchResults();
});
document.getElementById('search-date-from').addEventListener('change', (e) => {
  searchState.dateFrom = e.target.value;
  renderSearchResults();
});
document.getElementById('search-date-to').addEventListener('change', (e) => {
  searchState.dateTo = e.target.value;
  renderSearchResults();
});
document.getElementById('search-perf-min').addEventListener('input', (e) => {
  searchState.perfMin = Number(e.target.value);
  if (searchState.perfMin > searchState.perfMax) {
    searchState.perfMax = searchState.perfMin;
    document.getElementById('search-perf-max').value = String(searchState.perfMax);
    document.getElementById('search-perf-max-val').textContent = String(searchState.perfMax);
  }
  document.getElementById('search-perf-min-val').textContent = String(searchState.perfMin);
  renderSearchResults();
});
document.getElementById('search-perf-max').addEventListener('input', (e) => {
  searchState.perfMax = Number(e.target.value);
  if (searchState.perfMax < searchState.perfMin) {
    searchState.perfMin = searchState.perfMax;
    document.getElementById('search-perf-min').value = String(searchState.perfMin);
    document.getElementById('search-perf-min-val').textContent = String(searchState.perfMin);
  }
  document.getElementById('search-perf-max-val').textContent = String(searchState.perfMax);
  renderSearchResults();
});
document.getElementById('search-tags').addEventListener('click', (e) => {
  const btn = e.target.closest('.tag-toggle');
  if (!btn) return;
  const tag = btn.dataset.tag;
  if (searchState.tags.has(tag)) { searchState.tags.delete(tag); btn.classList.remove('active'); }
  else { searchState.tags.add(tag); btn.classList.add('active'); }
  renderSearchResults();
});

let DATA = null;

async function init() {
  try {
    const res = await fetch('data/lineup.json');
    if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
    DATA = await res.json();
    renderNav();
    currentDate = pickDefaultDate(DATA.days);
    setDay(currentDate);
    const activeBtn = document.querySelector('.toggle-btn.active');
    if (activeBtn) activeBtn.scrollIntoView({ inline: 'center', block: 'nearest' });
  } catch (err) {
    document.getElementById('floors').innerHTML = '<div class="day-empty">Couldn\\'t load the programme. Try reloading.</div>';
  }
}

init();"""
assert old_js in html
html = html.replace(old_js, new_js, 1)

# 4. setDay() needs to track currentDate so closeSearchPanel can restore it
old_setday = """function setDay(date) {
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.date === date);
  });
  const day = DATA.days.find(d => d.date === date);
  renderFloors(day);
}"""
new_setday = """function setDay(date) {
  currentDate = date;
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.date === date);
  });
  const day = DATA.days.find(d => d.date === date);
  renderFloors(day);
}"""
assert old_setday in html
html = html.replace(old_setday, new_setday, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Added search/filter panel (v2: main-area results, no scrim). New file size:", len(html), "chars")
