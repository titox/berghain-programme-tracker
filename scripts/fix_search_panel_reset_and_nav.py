#!/usr/bin/env python3
"""One-off fix, incremental on top of the shipped search panel:

1. Add a "Reset" button in the panel header that clears all active filters
   without closing the panel.
2. Closing the panel (X, Escape, or clicking a day-nav button) now resets
   all filter state instead of leaving it persistent for next time.
3. Day-nav buttons are visually disabled and inert while the search panel
   is open (dimmed, no pointer events) instead of being clickable.
"""

HTML_PATH = "index.html"

with open(HTML_PATH) as f:
    html = f.read()

# 1. CSS: disabled nav while searching + reset button style
old_toggle_btn = """  .toggle-btn {
    flex: none;
    white-space: nowrap;
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--rule);
    padding: var(--space-2) var(--space-3);
    font-family: var(--font);"""
new_toggle_btn = """  body.search-open .toggle-btn {
    opacity: 0.4;
    pointer-events: none;
  }
  .search-reset-btn {
    background: none; border: none; color: var(--muted); font-family: var(--font);
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; text-decoration: underline;
    cursor: pointer; padding: 0; margin-right: var(--space-3);
  }
  .search-reset-btn:hover { color: var(--fg); }
  .toggle-btn {
    flex: none;
    white-space: nowrap;
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--rule);
    padding: var(--space-2) var(--space-3);
    font-family: var(--font);"""
assert old_toggle_btn in html
html = html.replace(old_toggle_btn, new_toggle_btn, 1)

# 2. Markup: add Reset button to panel head
old_head = """  <div class="search-panel-head">
    <span class="search-panel-title">Search &amp; Filter</span>
    <button class="search-panel-close" id="search-close" aria-label="Close">&times;</button>
  </div>"""
new_head = """  <div class="search-panel-head">
    <span class="search-panel-title">Search &amp; Filter</span>
    <div>
      <button class="search-reset-btn" id="search-reset" type="button">Reset</button>
      <button class="search-panel-close" id="search-close" aria-label="Close">&times;</button>
    </div>
  </div>"""
assert old_head in html
html = html.replace(old_head, new_head, 1)

# 3. JS: resetSearchFilters(), wired into the Reset button and into closeSearchPanel()
old_close = """function closeSearchPanel() {
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
document.getElementById('search-close').addEventListener('click', closeSearchPanel);"""
new_close = """function resetSearchFilters() {
  searchState.name = '';
  searchState.dateFrom = '';
  searchState.dateTo = '';
  searchState.tags.clear();
  document.getElementById('search-name').value = '';
  document.getElementById('search-date-from').value = '';
  document.getElementById('search-date-to').value = '';
  document.querySelectorAll('#search-tags .tag-toggle.active').forEach(b => b.classList.remove('active'));
  const maxCount = Number(document.getElementById('search-perf-min').max) || 0;
  searchState.perfMin = 0;
  searchState.perfMax = maxCount;
  document.getElementById('search-perf-min').value = '0';
  document.getElementById('search-perf-max').value = String(maxCount);
  document.getElementById('search-perf-min-val').textContent = '0';
  document.getElementById('search-perf-max-val').textContent = String(maxCount);
  updatePerfFill();
}

function closeSearchPanel() {
  searchOpen = false;
  if (searchTagsRendered) resetSearchFilters();
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
document.getElementById('search-reset').addEventListener('click', () => {
  resetSearchFilters();
  renderSearchResults();
});"""
assert old_close in html
html = html.replace(old_close, new_close, 1)

# 4. Day-nav click: nav is now inert while searching (CSS pointer-events:none),
# so drop the "close panel then switch" branch -- clicking is impossible while open.
old_nav_click = """document.getElementById('toggle').addEventListener('click', (e) => {
  const btn = e.target.closest('.toggle-btn');
  if (btn) {
    if (searchOpen) closeSearchPanel();
    setDay(btn.dataset.date);
  }
});"""
new_nav_click = """document.getElementById('toggle').addEventListener('click', (e) => {
  if (searchOpen) return;
  const btn = e.target.closest('.toggle-btn');
  if (btn) setDay(btn.dataset.date);
});"""
assert old_nav_click in html
html = html.replace(old_nav_click, new_nav_click, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Added filter reset + disabled nav while searching. New file size:", len(html), "chars")
