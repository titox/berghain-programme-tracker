#!/usr/bin/env python3
"""One-off script: re-embed data/lineup.json (now with a photo field) into
berghain-tracker.html, and add DJ avatar (photo or initials) rendering."""
import json, re

HTML_PATH = "berghain-tracker.html"

with open("data/lineup.json") as f:
    lineup = json.load(f)
lineup_js = json.dumps(lineup, ensure_ascii=False)

with open(HTML_PATH) as f:
    html = f.read()

# 1. Replace the embedded LINEUP array with the updated data (source of truth: data/lineup.json)
pattern = re.compile(r"const LINEUP = \[.*?\];", re.DOTALL)
new_html, n = pattern.subn(f"const LINEUP = {lineup_js};", html, count=1)
assert n == 1, f"expected exactly 1 LINEUP replacement, got {n}"
html = new_html

# 2. Add avatar CSS
CSS_BLOCK = """
  .dj-summary { gap: var(--space-3); }
  .dj-avatar {
    width: 40px; height: 40px; flex-shrink: 0; object-fit: cover;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 13px; letter-spacing: 0.02em;
    background: var(--room-accent); color: var(--bg);
  }
"""
assert "</style>" in html
html = html.replace("</style>", CSS_BLOCK + "</style>", 1)

# .dj-summary already had "gap: var(--space-2);" from Task 6 -- remove the
# duplicate declaration so the new gap (space-3, room for the avatar) wins
# without leaving a dead rule.
html = html.replace(
    ".dj-summary { display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-2); }",
    ".dj-summary { display: flex; align-items: center; flex-wrap: wrap; }",
    1,
)

# 3. Add getInitials helper + avatar markup in renderRow
assert "function renderRow(dj) {" in html
html = html.replace(
    "function renderRow(dj) {",
    """function getInitials(name) {
  const words = name.replace(/[.]/g, '').split(/\\s+/).filter(w => w.length > 1 && w !== '&');
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
  const w = words[0] || name;
  return w.slice(0, 2).toUpperCase();
}

function renderRow(dj) {""",
    1,
)

old_summary = '''      <div class="dj-summary">
        <span class="dj-name">${dj.name}</span>${tags}
      </div>'''
new_summary = '''      <div class="dj-summary">
        ${dj.photo
          ? `<img class="dj-avatar" src="${dj.photo}" alt="" />`
          : `<div class="dj-avatar">${getInitials(dj.name)}</div>`}
        <span class="dj-name">${dj.name}</span>${tags}
      </div>'''
assert old_summary in html
html = html.replace(old_summary, new_summary, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Injected avatars. New file size:", len(html), "chars")
