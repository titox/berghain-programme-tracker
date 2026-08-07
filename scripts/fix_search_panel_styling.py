#!/usr/bin/env python3
"""One-off fix, incremental on top of the already-shipped search panel
(commit cc19ba9):

1. --room-accent was only ever set inside .room--berghain/.room--panorama,
   so anything using it outside a .room scope (search results, rendered
   straight into #floors) got an invalid custom property -- tag borders,
   tag text color, and avatar background all silently dropped. Give it a
   default at :root; the .room--* rules still override it locally.
2. Replace the two stacked full-width Min/Max sliders with a single-track
   dual-handle range slider (two overlaid native range inputs + a visual
   fill bar), closer to the familiar "price range" slider pattern.
"""

HTML_PATH = "index.html"

with open(HTML_PATH) as f:
    html = f.read()

# 1. --room-accent default
old_root = """  :root {
    --bg: #16151a;
    --surface: #1c1b21;
    --fg: #efece6;
    --muted: #9b9a9e;
    --berghain: #8fb4c9;
    --panorama: #d98f3d;
    --rule: #38373d;
    --font: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    --space-2: 8px;
    --space-3: 16px;
    --space-4: 24px;
    --space-5: 32px;
  }"""
new_root = """  :root {
    --bg: #16151a;
    --surface: #1c1b21;
    --fg: #efece6;
    --muted: #9b9a9e;
    --berghain: #8fb4c9;
    --panorama: #d98f3d;
    --rule: #38373d;
    --room-accent: var(--berghain);
    --font: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    --space-2: 8px;
    --space-3: 16px;
    --space-4: 24px;
    --space-5: 32px;
  }"""
assert old_root in html
html = html.replace(old_root, new_root, 1)

# 2a. CSS: replace stacked range-field rules with dual-range slider rules
old_css = """  .range-field { margin-bottom: var(--space-3); }
  .range-field-label { display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
  .range-field-label b { color: var(--fg); font-variant-numeric: tabular-nums; }
  .range-field input[type="range"] { width: 100%; accent-color: var(--berghain); }"""
new_css = """  .range-field-label {
    font-size: 13px; color: var(--fg); margin-bottom: var(--space-2);
    font-variant-numeric: tabular-nums;
  }
  .dual-range { position: relative; height: 24px; }
  .dual-range-track {
    position: absolute; top: 50%; left: 0; right: 0; height: 3px;
    background: var(--rule); transform: translateY(-50%); pointer-events: none;
  }
  .dual-range-fill {
    position: absolute; top: 50%; height: 3px;
    background: var(--berghain); transform: translateY(-50%); pointer-events: none;
  }
  .dual-range input[type="range"] {
    position: absolute; top: 0; left: 0; width: 100%; height: 24px; margin: 0;
    background: transparent; pointer-events: none;
    -webkit-appearance: none; appearance: none;
  }
  .dual-range input[type="range"]::-webkit-slider-runnable-track { background: transparent; }
  .dual-range input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none; pointer-events: auto;
    width: 16px; height: 16px; border-radius: 50%;
    background: var(--fg); border: 2px solid var(--bg); cursor: pointer; margin-top: -6.5px;
  }
  .dual-range input[type="range"]::-moz-range-track { background: transparent; border: none; }
  .dual-range input[type="range"]::-moz-range-thumb {
    pointer-events: auto; width: 16px; height: 16px; border-radius: 50%;
    background: var(--fg); border: 2px solid var(--bg); cursor: pointer;
  }"""
assert old_css in html
html = html.replace(old_css, new_css, 1)

# 2b. Markup: single combined range row instead of two stacked ones
old_markup = """    <div class="field">
      <label class="field-label">Klubnacht performances</label>
      <div class="range-field">
        <div class="range-field-label"><span>Min</span><b id="search-perf-min-val">0</b></div>
        <input type="range" id="search-perf-min" min="0" max="0" value="0">
      </div>
      <div class="range-field">
        <div class="range-field-label"><span>Max</span><b id="search-perf-max-val">0</b></div>
        <input type="range" id="search-perf-max" min="0" max="0" value="0">
      </div>
    </div>"""
new_markup = """    <div class="field">
      <label class="field-label">Klubnacht performances</label>
      <div class="range-field-label"><span id="search-perf-min-val">0</span> &#8211; <span id="search-perf-max-val">0</span></div>
      <div class="dual-range">
        <div class="dual-range-track"></div>
        <div class="dual-range-fill" id="search-perf-fill"></div>
        <input type="range" id="search-perf-min" min="0" max="0" value="0">
        <input type="range" id="search-perf-max" min="0" max="0" value="0">
      </div>
    </div>"""
assert old_markup in html
html = html.replace(old_markup, new_markup, 1)

# 2c. JS: add updatePerfFill(), call it after computing maxCount and on both slider inputs
old_js_decl = """let searchOpen = false;
let searchTagsRendered = false;

function renderTagOptions() {"""
new_js_decl = """let searchOpen = false;
let searchTagsRendered = false;

function updatePerfFill() {
  const minSlider = document.getElementById('search-perf-min');
  const maxSlider = document.getElementById('search-perf-max');
  const range = Number(minSlider.max) || 1;
  const leftPct = (Number(minSlider.value) / range) * 100;
  const rightPct = (Number(maxSlider.value) / range) * 100;
  const fill = document.getElementById('search-perf-fill');
  fill.style.left = `${leftPct}%`;
  fill.style.width = `${Math.max(0, rightPct - leftPct)}%`;
}

function renderTagOptions() {"""
assert old_js_decl in html
html = html.replace(old_js_decl, new_js_decl, 1)

old_js_maxcount = """  maxSlider.value = String(maxCount);
  searchState.perfMax = maxCount;
  document.getElementById('search-perf-max-val').textContent = String(maxCount);
  searchTagsRendered = true;"""
new_js_maxcount = """  maxSlider.value = String(maxCount);
  searchState.perfMax = maxCount;
  document.getElementById('search-perf-max-val').textContent = String(maxCount);
  updatePerfFill();
  searchTagsRendered = true;"""
assert old_js_maxcount in html
html = html.replace(old_js_maxcount, new_js_maxcount, 1)

old_js_listeners = """  document.getElementById('search-perf-min-val').textContent = String(searchState.perfMin);
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
});"""
new_js_listeners = """  document.getElementById('search-perf-min-val').textContent = String(searchState.perfMin);
  updatePerfFill();
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
  updatePerfFill();
  renderSearchResults();
});"""
assert old_js_listeners in html
html = html.replace(old_js_listeners, new_js_listeners, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Fixed --room-accent default + replaced stacked sliders with dual-range. New file size:", len(html), "chars")
