#!/usr/bin/env python3
"""One-off script: add a nationality multi-select filter to the search
panel, alongside the existing style-tag filter. Reuses the .tag-toggle
CSS component and the existing flagEmoji() helper -- no new CSS needed
beyond a small flag-inline tweak."""

HTML_PATH = "index.html"

with open(HTML_PATH) as f:
    html = f.read()

# 1. Markup: nationality field after Style
old_markup = """    <div class="field">
      <label class="field-label">Style</label>
      <div id="search-tags"></div>
    </div>
  </div>
</aside>"""
new_markup = """    <div class="field">
      <label class="field-label">Style</label>
      <div id="search-tags"></div>
    </div>
    <div class="field">
      <label class="field-label">Nationality</label>
      <div id="search-nationalities"></div>
    </div>
  </div>
</aside>"""
assert old_markup in html
html = html.replace(old_markup, new_markup, 1)

# 2. CSS: small flag glyph inside the toggle button
old_css = """  .tag-toggle.active { border-color: var(--berghain); color: var(--berghain); }
  .tag-toggle.tag-hidden { display: none; }"""
new_css = """  .tag-toggle.active { border-color: var(--berghain); color: var(--berghain); }
  .tag-toggle.tag-hidden { display: none; }
  .tag-toggle .flag-inline { margin-right: 4px; }"""
assert old_css in html
html = html.replace(old_css, new_css, 1)

# 3. JS: searchState gets a nationalities Set; render/filter/reset/listener wiring
old_state = """const searchState = { name: '', dateFrom: '', dateTo: '', perfMin: 0, perfMax: 0, tags: new Set() };"""
new_state = """const searchState = { name: '', dateFrom: '', dateTo: '', perfMin: 0, perfMax: 0, tags: new Set(), nationalities: new Set() };"""
assert old_state in html
html = html.replace(old_state, new_state, 1)

old_render_call = """function renderTagOptions() {"""
new_render_call = """function renderNationalityOptions() {
  const byCode = new Map();
  Object.values(DATA.djs).forEach(dj => {
    if (dj.nationality) byCode.set(dj.nationality.code, dj.nationality.name);
  });
  const sorted = [...byCode.entries()].sort((a, b) => a[1].localeCompare(b[1]));
  document.getElementById('search-nationalities').innerHTML = sorted.map(([code, name]) =>
    `<button type="button" class="tag-toggle" data-nat="${esc(code)}"><span class="flag-inline">${flagEmoji(code)}</span>${esc(name)}</button>`
  ).join('');
}

function renderTagOptions() {"""
assert old_render_call in html
html = html.replace(old_render_call, new_render_call, 1)

old_tags_rendered_call = """  updatePerfFill();
  searchTagsRendered = true;"""
new_tags_rendered_call = """  updatePerfFill();
  renderNationalityOptions();
  searchTagsRendered = true;"""
assert old_tags_rendered_call in html
html = html.replace(old_tags_rendered_call, new_tags_rendered_call, 1)

old_match = """  if (searchState.tags.size > 0 && !(dj.tags || []).some(t => searchState.tags.has(t))) return false;
  return true;
}"""
new_match = """  if (searchState.tags.size > 0 && !(dj.tags || []).some(t => searchState.tags.has(t))) return false;
  if (searchState.nationalities.size > 0 && (!dj.nationality || !searchState.nationalities.has(dj.nationality.code))) return false;
  return true;
}"""
assert old_match in html
html = html.replace(old_match, new_match, 1)

old_reset = """  document.querySelectorAll('#search-tags .tag-toggle.active').forEach(b => b.classList.remove('active'));
  const maxCount = Number(document.getElementById('search-perf-min').max) || 0;"""
new_reset = """  document.querySelectorAll('#search-tags .tag-toggle.active').forEach(b => b.classList.remove('active'));
  searchState.nationalities.clear();
  document.querySelectorAll('#search-nationalities .tag-toggle.active').forEach(b => b.classList.remove('active'));
  const maxCount = Number(document.getElementById('search-perf-min').max) || 0;"""
assert old_reset in html
html = html.replace(old_reset, new_reset, 1)

old_tag_listener = """document.getElementById('search-tags').addEventListener('click', (e) => {
  const btn = e.target.closest('.tag-toggle');
  if (!btn) return;
  const tag = btn.dataset.tag;
  if (searchState.tags.has(tag)) { searchState.tags.delete(tag); btn.classList.remove('active'); }
  else { searchState.tags.add(tag); btn.classList.add('active'); }
  renderSearchResults();
});"""
new_tag_listener = """document.getElementById('search-tags').addEventListener('click', (e) => {
  const btn = e.target.closest('.tag-toggle');
  if (!btn) return;
  const tag = btn.dataset.tag;
  if (searchState.tags.has(tag)) { searchState.tags.delete(tag); btn.classList.remove('active'); }
  else { searchState.tags.add(tag); btn.classList.add('active'); }
  renderSearchResults();
});
document.getElementById('search-nationalities').addEventListener('click', (e) => {
  const btn = e.target.closest('.tag-toggle');
  if (!btn) return;
  const code = btn.dataset.nat;
  if (searchState.nationalities.has(code)) { searchState.nationalities.delete(code); btn.classList.remove('active'); }
  else { searchState.nationalities.add(code); btn.classList.add('active'); }
  renderSearchResults();
});"""
assert old_tag_listener in html
html = html.replace(old_tag_listener, new_tag_listener, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Added nationality filter. New file size:", len(html), "chars")
