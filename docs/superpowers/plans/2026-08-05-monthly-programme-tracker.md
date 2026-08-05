# Monthly Programme Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the one-off Berghain weekend page into a self-updating, ever-growing archive of Berghain's monthly programme, with a generalized nav/room layout and three new DJ streaming links, driven by a scheduled monthly scrape+research agent.

**Architecture:** `data/lineup.json` moves from a flat per-day-per-DJ list to a `{djs, days}` archive (deduped DJ profiles + a chronological day list with arbitrary room counts). `index.html` becomes a static shell that `fetch()`s this JSON at load and renders it, instead of embedding data inline. A Claude Code scheduled cron agent runs monthly, scrapes `berghain.berlin/en/program`, researches new DJs, updates the JSON, and auto-commits/pushes.

**Tech Stack:** Vanilla JS/CSS/HTML (no framework, no build step), Python 3 one-off scripts for data migration/validation/HTML rewriting (matches existing repo convention), Claude Code `schedule`/cron for the monthly agent.

## Global Constraints

- Rolling archive starting August 2026 — no month is ever dropped.
- Day nav default selection = the day closest to today, computed **client-side** (not baked in at generation time).
- DJ profiles are deduped by name across the whole archive; a returning DJ's existing profile is reused (never re-researched), and a new `appearances` entry is pushed instead of incrementing a bare counter.
- Monthly agent runs 1st of month, 00:01; auto-commits and pushes on success; aborts **without writing anything** on scrape failure or schema-validation failure, and sends a failure notification.
- Missing bio/tags/links/photo fields are always omitted — never fabricated or placeholder-filled.
- Visual system (palette, typography, sharp corners, inline-expand DJ rows, two-room staircase motif) is unchanged from the current "Split Floor" design.
- New DJ card links: `bandcamp`, `applemusic`, `spotify`, rendered in order Soundcloud, Bandcamp, Apple Music, Spotify, Instagram, YouTube.

Spec: `docs/superpowers/specs/2026-08-05-monthly-programme-tracker-design.md`

---

### Task 1: Rewrite `scripts/validate_lineup.py` for the `{djs, days}` schema

**Files:**
- Modify: `scripts/validate_lineup.py`
- Create: `scripts/test_validate_lineup.py`

**Interfaces:**
- Produces: `check(data: dict) -> list[str]` — pure function, takes an already-parsed `{djs, days}` dict, returns a list of human-readable error strings (empty list = valid). Used directly by Task 2 (migration) and by the monthly agent (Task 8/9) before it commits.
- Produces: `load() -> dict` — reads and parses `data/lineup.json`.
- Produces: CLI: `python3 scripts/validate_lineup.py` — exit 0 + `OK: N DJ profiles, M days` on success; exit 1 + `FAIL (...)` listing every error otherwise.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_validate_lineup.py`:

```python
#!/usr/bin/env python3
"""Tests for scripts/validate_lineup.py's schema checks."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_lineup import check


def minimal_dj():
    return {
        "name": "Test DJ",
        "tags": ["Techno"],
        "blurb": "b",
        "bio": "bio",
        "links": {},
        "appearances": [{"date": "2026-08-21", "event": "REEF", "room": "Berghain"}],
    }


def minimal_data():
    return {
        "djs": {"test-dj": minimal_dj()},
        "days": [{
            "date": "2026-08-21", "weekday": "FRI", "event": "REEF",
            "rooms": [{"room": "Berghain", "djSlugs": ["test-dj"]}],
        }],
    }


class ValidateLineupTests(unittest.TestCase):
    def test_valid_minimal_doc_passes(self):
        self.assertEqual(check(minimal_data()), [])

    def test_missing_required_dj_key_fails(self):
        data = minimal_data()
        del data["djs"]["test-dj"]["bio"]
        errors = check(data)
        self.assertTrue(any("missing keys" in e and "bio" in e for e in errors))

    def test_unknown_dj_slug_in_room_fails(self):
        data = minimal_data()
        data["days"][0]["rooms"][0]["djSlugs"] = ["ghost-dj"]
        errors = check(data)
        self.assertTrue(any("unknown dj slug" in e for e in errors))

    def test_day_without_matching_appearance_fails(self):
        data = minimal_data()
        data["djs"]["test-dj"]["appearances"] = [
            {"date": "2026-09-01", "event": "REEF", "room": "Berghain"}
        ]
        errors = check(data)
        self.assertTrue(any("missing appearances entry" in e for e in errors))

    def test_duplicate_date_fails(self):
        data = minimal_data()
        data["days"].append(dict(data["days"][0]))
        errors = check(data)
        self.assertTrue(any("duplicate date" in e for e in errors))

    def test_empty_appearances_fails(self):
        data = minimal_data()
        data["djs"]["test-dj"]["appearances"] = []
        errors = check(data)
        self.assertTrue(any("appearances must be non-empty" in e for e in errors))

    def test_stats_missing_field_fails(self):
        data = minimal_data()
        data["djs"]["test-dj"]["stats"] = {"performanceCount": 1}
        errors = check(data)
        self.assertTrue(any("stats missing" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/test_validate_lineup.py`
Expected: `ImportError: cannot import name 'check' from 'validate_lineup'` (or similar — the old script has no `check` function yet).

- [ ] **Step 3: Replace `scripts/validate_lineup.py` with the new schema validator**

```python
#!/usr/bin/env python3
"""Validate data/lineup.json against the {djs, days} archive schema."""
import json
import re
import sys
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "lineup.json"

REQUIRED_DJ_KEYS = {"name", "tags", "blurb", "bio", "links", "appearances"}
REQUIRED_DAY_KEYS = {"date", "weekday", "event", "rooms"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load():
    with open(DATA_PATH) as f:
        return json.load(f)


def check(data):
    errors = []
    djs = data.get("djs", {})
    days = data.get("days", [])

    if not isinstance(djs, dict):
        errors.append("'djs' must be an object")
        djs = {}
    if not isinstance(days, list):
        errors.append("'days' must be a list")
        days = []

    for slug, dj in djs.items():
        missing = REQUIRED_DJ_KEYS - dj.keys()
        if missing:
            errors.append(f"djs.{slug}: missing keys {missing}")
        if not dj.get("appearances"):
            errors.append(f"djs.{slug}: appearances must be non-empty")
        for a in dj.get("appearances", []):
            for k in ("date", "event", "room"):
                if k not in a:
                    errors.append(f"djs.{slug}: appearance missing '{k}'")
        if "stats" in dj:
            for k in ("performanceCount", "firstPlayed", "isResident"):
                if k not in dj["stats"]:
                    errors.append(f"djs.{slug}: stats missing '{k}'")

    seen_dates = set()
    for day in days:
        missing = REQUIRED_DAY_KEYS - day.keys()
        if missing:
            errors.append(f"days[{day.get('date', '?')}]: missing keys {missing}")
            continue
        if not DATE_RE.match(day["date"]):
            errors.append(f"days: invalid date format '{day['date']}'")
        if day["date"] in seen_dates:
            errors.append(f"days: duplicate date '{day['date']}'")
        seen_dates.add(day["date"])
        for room in day["rooms"]:
            if "room" not in room or "djSlugs" not in room:
                errors.append(f"days[{day['date']}]: room entry missing 'room'/'djSlugs'")
                continue
            for slug in room["djSlugs"]:
                if slug not in djs:
                    errors.append(
                        f"days[{day['date']}]: room '{room['room']}' references unknown dj slug '{slug}'"
                    )
                else:
                    appearance_dates = {a["date"] for a in djs[slug].get("appearances", [])}
                    if day["date"] not in appearance_dates:
                        errors.append(
                            f"djs.{slug}: missing appearances entry for {day['date']} "
                            f"(listed in days but not in appearances)"
                        )

    return errors


def main():
    data = load()
    errors = check(data)
    if errors:
        print(f"FAIL ({len(errors)} issue(s)):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print(f"OK: {len(data.get('djs', {}))} DJ profiles, {len(data.get('days', []))} days")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/test_validate_lineup.py -v`
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_lineup.py scripts/test_validate_lineup.py
git commit -m "$(cat <<'EOF'
Rewrite lineup validator for the {djs, days} archive schema

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Migrate `data/lineup.json` to the new schema

**Files:**
- Create: `scripts/migrate_lineup.py`
- Modify: `data/lineup.json` (rewritten in place by running the script)
- Modify: `assets/dj-photos/CREDITS.md` (filename reference update)
- Rename: `assets/dj-photos/andre_galluzzi.jpg` → `assets/dj-photos/andre-galluzzi.jpg`

**Interfaces:**
- Consumes: `check()` from `scripts/validate_lineup.py` (Task 1), run as a subprocess/CLI check after migrating.
- Produces: `data/lineup.json` in the `{djs, days}` shape all later tasks depend on (slug format: lowercased, accents stripped, non-alphanumeric runs collapsed to single hyphens, e.g. `"André Galluzzi"` → `"andre-galluzzi"`).

- [ ] **Step 1: Write `scripts/migrate_lineup.py`**

```python
#!/usr/bin/env python3
"""One-off migration: convert data/lineup.json from the flat per-day-per-DJ
list into the {djs, days} archive schema. See
docs/superpowers/specs/2026-08-05-monthly-programme-tracker-design.md."""
import json
import re
import unicodedata
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "lineup.json"

WEEKDAYS = {"friday": "FRI", "saturday": "SAT"}
DAY_DATES = {"friday": "2026-08-21", "saturday": "2026-08-22"}


def slugify(name):
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def main():
    entries = json.loads(DATA_PATH.read_text())

    djs = {}
    days = {}

    for e in entries:
        slug = slugify(e["name"])
        date = DAY_DATES[e["day"]]

        if slug not in djs:
            profile = {
                "name": e["name"],
                "tags": e["tags"],
                "blurb": e["blurb"],
                "bio": e["bio"],
                "links": e["links"],
                "appearances": [],
            }
            if e.get("stats"):
                profile["stats"] = e["stats"]
            if e.get("photo"):
                profile["photo"] = f"assets/dj-photos/{slug}.jpg"
            djs[slug] = profile

        djs[slug]["appearances"].append({"date": date, "event": e["event"], "room": e["room"]})

        if date not in days:
            days[date] = {
                "date": date,
                "weekday": WEEKDAYS[e["day"]],
                "event": e["event"],
                "rooms": {},
            }
        days[date]["rooms"].setdefault(e["room"], []).append(slug)

    days_list = []
    for date in sorted(days):
        d = days[date]
        days_list.append({
            "date": d["date"],
            "weekday": d["weekday"],
            "event": d["event"],
            "rooms": [{"room": r, "djSlugs": slugs} for r, slugs in d["rooms"].items()],
        })

    output = {"djs": djs, "days": days_list}
    DATA_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"Migrated {len(entries)} entries -> {len(djs)} DJ profiles, {len(days_list)} days")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the migration**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/migrate_lineup.py`
Expected: `Migrated 25 entries -> 25 DJ profiles, 2 days`

- [ ] **Step 3: Rename the existing avatar file to match the new slug convention**

`headhunter.jpg` already matches its slug (`headhunter`) and needs no change.

Run:
```bash
cd "/Users/voliverm/Documents/brg tracker" && git mv assets/dj-photos/andre_galluzzi.jpg assets/dj-photos/andre-galluzzi.jpg
```

- [ ] **Step 4: Update the photo credits filename reference**

In `assets/dj-photos/CREDITS.md`, replace `andre_galluzzi.jpg` with `andre-galluzzi.jpg` (the credit text itself is unchanged).

- [ ] **Step 5: Validate the migrated data**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/validate_lineup.py`
Expected: `OK: 25 DJ profiles, 2 days`

- [ ] **Step 6: Spot-check the migrated structure**

Run:
```bash
cd "/Users/voliverm/Documents/brg tracker" && python3 -c "
import json
d = json.load(open('data/lineup.json'))
print(d['djs']['headhunter']['photo'])
print(d['djs']['andre-galluzzi']['photo'])
print(d['days'][0]['rooms'])
print(len(d['djs']['darwin']['appearances']))
"
```
Expected:
```
assets/dj-photos/headhunter.jpg
assets/dj-photos/andre-galluzzi.jpg
[{'room': 'Berghain', 'djSlugs': [...5 names...]}, {'room': 'Panorama Bar', 'djSlugs': [...5 names...]}]
1
```

- [ ] **Step 7: Commit**

```bash
git add scripts/migrate_lineup.py data/lineup.json assets/dj-photos/CREDITS.md assets/dj-photos/andre-galluzzi.jpg assets/dj-photos/andre_galluzzi.jpg
git commit -m "$(cat <<'EOF'
Migrate data/lineup.json to the {djs, days} archive schema

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Deploy `data/` and `assets/` on Vercel

**Files:**
- Modify: `.vercelignore`

**Interfaces:**
- None (config-only). Required before Task 4's `fetch('data/lineup.json')` and any `assets/dj-photos/*.jpg` reference can resolve in production.

- [ ] **Step 1: Update `.vercelignore`**

Current content excludes `assets` and `data` — both must now be deployed since `index.html` fetches JSON and references photo files at runtime (the old architecture embedded everything, so excluding these authoring-only directories was correct then; it isn't now).

Read the current file, then replace it with:

```
Screenshot 2026-07-09 at 15.05.46.png
berghain-tracker.html
docs
scripts
.superpowers
*.skill
```

- [ ] **Step 2: Verify the exclusion is gone**

Run: `cd "/Users/voliverm/Documents/brg tracker" && grep -E "^(assets|data)$" .vercelignore`
Expected: no output (grep exits 1, meaning neither line is present).

- [ ] **Step 3: Commit**

```bash
git add .vercelignore
git commit -m "$(cat <<'EOF'
Deploy data/ and assets/ now that index.html fetches lineup.json at runtime

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Rebuild `index.html`'s rendering + navigation engine

**Files:**
- Create: `scripts/rebuild_render_and_nav.py`
- Modify: `index.html` (rewritten in place by running the script)

**Interfaces:**
- Consumes: `data/lineup.json` in the `{djs, days}` shape from Task 2.
- Produces: client-side globals `DATA`, `renderRow(slug)`, `renderFloors(day)`, `renderNav()`, `pickDefaultDate(days)`, `setDay(date)`, `init()` — no later task depends on these directly, but Task 7's manual verification exercises all of them.

This task does **not** touch the existing photo-carousel code (`CAROUSEL`, `renderCarousel`, etc.) — that stays exactly as-is per the design spec.

- [ ] **Step 1: Write `scripts/rebuild_render_and_nav.py`**

```python
#!/usr/bin/env python3
"""One-off script: rebuild index.html's data loading, DJ-card rendering,
room layout, and day navigation to read from the new data/lineup.json
{djs, days} archive schema instead of an embedded LINEUP array."""
import re

HTML_PATH = "index.html"

with open(HTML_PATH) as f:
    html = f.read()

# 1. Remove the embedded LINEUP array -- data now comes from a runtime fetch.
pattern = re.compile(r"\nconst LINEUP = \[.*?\];\n", re.DOTALL)
html, n = pattern.subn("\n", html, count=1)
assert n == 1, f"expected exactly 1 LINEUP removal, got {n}"

# 2. CSS: generalized nav strip + month label + empty-day placeholder.
old_toggle_css = """  .toggle { display: flex; gap: var(--space-2); margin-bottom: var(--space-5); }
  .toggle-btn {
    flex: 1;
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--rule);
    padding: var(--space-3);
    font-family: var(--font);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    cursor: pointer;
  }
  .toggle-btn.active { color: var(--fg); border-color: var(--fg); }"""
new_toggle_css = """  .toggle {
    display: flex;
    gap: var(--space-2);
    margin-bottom: var(--space-5);
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
  }
  .toggle-btn {
    flex: none;
    white-space: nowrap;
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--rule);
    padding: var(--space-2) var(--space-3);
    font-family: var(--font);
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    cursor: pointer;
  }
  .toggle-btn.active { color: var(--fg); border-color: var(--fg); }
  .month-label {
    flex: none;
    align-self: center;
    color: var(--muted);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0 var(--space-2);
  }
  .day-empty {
    padding: var(--space-5) 0;
    color: var(--muted);
    text-align: center;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }"""
assert old_toggle_css in html
html = html.replace(old_toggle_css, new_toggle_css, 1)

# 3. Markup: dynamic nav + dynamic floors container.
old_markup = """  <header class="toggle">
    <button id="toggle-fri" class="toggle-btn active">FRI 21.08 — REEF</button>
    <button id="toggle-sat" class="toggle-btn">SAT 22.08 — KLUBNACHT</button>
  </header>
  <div class="floors">
    <section class="room room--berghain">
      <h2>Berghain</h2>
      <div id="berghain-col"></div>
    </section>
    <div class="staircase" aria-hidden="true"></div>
    <section class="room room--panorama">
      <h2>Panorama Bar</h2>
      <div id="panorama-col"></div>
    </section>
  </div>"""
new_markup = """  <header class="toggle" id="toggle"></header>
  <div class="floors" id="floors"></div>"""
assert old_markup in html
html = html.replace(old_markup, new_markup, 1)

# 4. JS: replace renderRow + renderDay + toggle wiring + setDay + initial call
#    with the schema-driven rendering + nav engine.
old_js = """function renderRow(dj) {
  const tags = dj.tags.map(t => `<span class="tag">${t}</span>`).join('');
  const links = Object.entries(dj.links || {})
    .map(([k, url]) => `<a href="${url}" target="_blank" rel="noopener">${k}</a>`)
    .join('');
  const stats = dj.stats
    ? `<div class="dj-stats">${dj.stats.performanceCount} Klubnacht performances since ${dj.stats.firstPlayed}${dj.stats.isResident ? ' · Resident' : ''}</div>`
    : '';
  const hasDetail = Boolean(dj.blurb || dj.bio || stats || links);
  return `
    <div class="dj-row${hasDetail ? '' : ' dj-row--empty'}">
      <div class="dj-summary">
        ${dj.photo
          ? `<img class="dj-avatar" src="${dj.photo}" alt="" />`
          : `<div class="dj-avatar">${getInitials(dj.name)}</div>`}
        <span class="dj-name">${dj.name}</span>${tags}
      </div>
      <div class="dj-detail">
        ${dj.blurb ? `<p class="dj-blurb">${dj.blurb}</p>` : ''}
        ${dj.bio ? `<p class="dj-bio">${dj.bio}</p>` : ''}
        ${stats}
        <div class="dj-links">${links}</div>
      </div>
    </div>`;
}

function renderDay(day) {
  const inDay = LINEUP.filter(d => d.day === day);
  document.getElementById('berghain-col').innerHTML =
    inDay.filter(d => d.room === 'Berghain').map(renderRow).join('');
  document.getElementById('panorama-col').innerHTML =
    inDay.filter(d => d.room === 'Panorama Bar').map(renderRow).join('');
}

document.getElementById('toggle-fri').addEventListener('click', () => setDay('friday'));
document.getElementById('toggle-sat').addEventListener('click', () => setDay('saturday'));

function setDay(day) {
  document.getElementById('toggle-fri').classList.toggle('active', day === 'friday');
  document.getElementById('toggle-sat').classList.toggle('active', day === 'saturday');
  renderDay(day);
}

document.addEventListener('click', (e) => {
  if (e.target.closest('a')) return;
  const row = e.target.closest('.dj-row');
  if (row && !row.classList.contains('dj-row--empty')) row.classList.toggle('expanded');
});

setDay('friday');"""

new_js = """const LINK_LABELS = [
  ['soundcloud', 'Soundcloud'],
  ['bandcamp', 'Bandcamp'],
  ['applemusic', 'Apple Music'],
  ['spotify', 'Spotify'],
  ['instagram', 'Instagram'],
  ['youtube', 'YouTube'],
];

function ordinal(n) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

function renderRow(slug) {
  const dj = DATA.djs[slug];
  const tags = dj.tags.map(t => `<span class="tag">${t}</span>`).join('');
  const links = LINK_LABELS
    .filter(([key]) => dj.links && dj.links[key])
    .map(([key, label]) => `<a href="${dj.links[key]}" target="_blank" rel="noopener">${label}</a>`)
    .join('');
  const statsParts = [];
  if (dj.appearances.length > 1) statsParts.push(`${ordinal(dj.appearances.length)} appearance since we started tracking`);
  if (dj.stats) statsParts.push(`${dj.stats.performanceCount} Klubnacht performances since ${dj.stats.firstPlayed}${dj.stats.isResident ? ' · Resident' : ''}`);
  const stats = statsParts.length ? `<div class="dj-stats">${statsParts.join(' · ')}</div>` : '';
  const hasDetail = Boolean(dj.blurb || dj.bio || stats || links);
  return `
    <div class="dj-row${hasDetail ? '' : ' dj-row--empty'}">
      <div class="dj-summary">
        ${dj.photo
          ? `<img class="dj-avatar" src="${dj.photo}" alt="" />`
          : `<div class="dj-avatar">${getInitials(dj.name)}</div>`}
        <span class="dj-name">${dj.name}</span>${tags}
      </div>
      <div class="dj-detail">
        ${dj.blurb ? `<p class="dj-blurb">${dj.blurb}</p>` : ''}
        ${dj.bio ? `<p class="dj-bio">${dj.bio}</p>` : ''}
        ${stats}
        <div class="dj-links">${links}</div>
      </div>
    </div>`;
}

const ROOM_ACCENTS = { 'Berghain': 'berghain', 'Panorama Bar': 'panorama' };
const FALLBACK_ACCENTS = ['berghain', 'panorama'];

function roomAccentClass(room, index) {
  return ROOM_ACCENTS[room] || FALLBACK_ACCENTS[index % FALLBACK_ACCENTS.length];
}

function renderFloors(day) {
  const floorsEl = document.getElementById('floors');
  if (!day.rooms.length) {
    floorsEl.innerHTML = `<div class="day-empty">${day.event} — no lineup listed</div>`;
    return;
  }
  const sections = day.rooms.map((r, i) => `
    <section class="room room--${roomAccentClass(r.room, i)}">
      <h2>${r.room}</h2>
      <div>${r.djSlugs.map(renderRow).join('')}</div>
    </section>`);
  const withDividers = [];
  sections.forEach((s, i) => {
    if (i > 0) withDividers.push('<div class="staircase" aria-hidden="true"></div>');
    withDividers.push(s);
  });
  floorsEl.innerHTML = withDividers.join('');
}

const MONTH_NAMES = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

function formatDayLabel(day) {
  const [, mm, dd] = day.date.split('-');
  return `${day.weekday} ${dd}.${mm} — ${day.event}`;
}

function renderNav() {
  const nav = document.getElementById('toggle');
  let html = '';
  let lastMonth = null;
  for (const day of DATA.days) {
    const month = day.date.slice(0, 7);
    if (month !== lastMonth) {
      const mm = Number(day.date.slice(5, 7));
      html += `<span class="month-label">${MONTH_NAMES[mm - 1]}</span>`;
      lastMonth = month;
    }
    html += `<button class="toggle-btn" data-date="${day.date}">${formatDayLabel(day)}</button>`;
  }
  nav.innerHTML = html;
}

function pickDefaultDate(days) {
  const todayStr = new Date().toISOString().slice(0, 10);
  const upcoming = days.find(d => d.date >= todayStr);
  return upcoming ? upcoming.date : days[days.length - 1].date;
}

function setDay(date) {
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.date === date);
  });
  const day = DATA.days.find(d => d.date === date);
  renderFloors(day);
}

document.getElementById('toggle').addEventListener('click', (e) => {
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
  const res = await fetch('data/lineup.json');
  DATA = await res.json();
  renderNav();
  setDay(pickDefaultDate(DATA.days));
  const activeBtn = document.querySelector('.toggle-btn.active');
  if (activeBtn) activeBtn.scrollIntoView({ inline: 'center', block: 'nearest' });
}

init();"""

assert old_js in html
html = html.replace(old_js, new_js, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print("Rebuilt render + nav engine. New file size:", len(html), "chars")
```

- [ ] **Step 2: Run it**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/rebuild_render_and_nav.py`
Expected: `Rebuilt render + nav engine. New file size: <a number much smaller than 1312618> chars` (the ~53KB embedded LINEUP array is gone; the carousel's base64 blob, which this script never touches, still dominates the file size).

- [ ] **Step 3: Sanity-check the output**

Run: `cd "/Users/voliverm/Documents/brg tracker" && grep -c "const LINEUP" index.html && grep -c "id=\"toggle\"" index.html && grep -c "id=\"floors\"" index.html`
Expected: `0`, `1`, `1`.

- [ ] **Step 4: Commit**

```bash
git add scripts/rebuild_render_and_nav.py index.html
git commit -m "$(cat <<'EOF'
Rebuild index.html to fetch data/lineup.json and render N rooms/days

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

(Full browser verification of this task happens in Task 7, alongside the copy changes from Task 5 and the cleanup from Task 6 — the page isn't meaningfully viewable in isolation after each of these small file-level tasks.)

---

### Task 5: Genericize site copy + regenerate the OG image

**Files:**
- Create: `scripts/genericize_copy.py`
- Modify: `index.html` (rewritten in place by running the script)
- Modify: `scripts/compose_og_image.py`
- Create: `og-image.jpg` (regenerated, overwrites the existing file)

**Interfaces:**
- None consumed/produced beyond static text — this task only changes copy, not behavior.

- [ ] **Step 1: Write `scripts/genericize_copy.py`**

```python
#!/usr/bin/env python3
"""One-off script: replace weekend-specific copy in index.html (title, meta
tags, intro headline) with copy that describes an ongoing archive instead of
one fixed weekend."""

HTML_PATH = "index.html"

with open(HTML_PATH) as f:
    html = f.read()

REPLACEMENTS = [
    (
        "<title>Your Berghain Weekend — 21–22.08.2026</title>",
        "<title>Berghain Programme Tracker</title>",
    ),
    (
        '<meta name="description" content="Interactive lineup guide for Berghain\'s Friday 21.08 REEF and Saturday 22.08 Klubnacht — bios, genre tags, links and performance history for all 25 DJs across both rooms.">',
        '<meta name="description" content="Interactive programme guide for Berghain — lineups, bios, genre tags and links for every night, updated automatically each month.">',
    ),
    (
        '<meta property="og:title" content="Your Berghain Weekend — 21–22.08.2026">',
        '<meta property="og:title" content="Berghain Programme Tracker">',
    ),
    (
        '<meta property="og:description" content="REEF (Fri) + Klubnacht (Sat) — bios, genre tags, links and performance history for all 25 DJs across both rooms.">',
        '<meta property="og:description" content="Every night at Berghain — bios, genre tags and links for the full lineup, updated automatically each month.">',
    ),
    (
        '<meta name="twitter:title" content="Your Berghain Weekend — 21–22.08.2026">',
        '<meta name="twitter:title" content="Berghain Programme Tracker">',
    ),
    (
        '<meta name="twitter:description" content="REEF (Fri) + Klubnacht (Sat) — bios, genre tags, links and performance history for all 25 DJs across both rooms.">',
        '<meta name="twitter:description" content="Every night at Berghain — bios, genre tags and links for the full lineup, updated automatically each month.">',
    ),
    (
        '''  <div class="intro">
    <span class="intro-eyebrow">Berlin &#183; 21&#8211;22.08.2026</span>
    <h1 class="intro-headline">Your Berghain Weekend</h1>
    <p class="intro-subtext">Two nights, two rooms, 25 sets. REEF on Friday, Klubnacht on Saturday — tap any name for their sound, bio and links before you're inside.</p>
  </div>''',
        '''  <div class="intro">
    <span class="intro-eyebrow">Berlin &#183; Ongoing</span>
    <h1 class="intro-headline">Berghain Programme Tracker</h1>
    <p class="intro-subtext">Every night at Berghain, tracked monthly — tap any name for their sound, bio and links before you're inside.</p>
  </div>''',
    ),
]

for old, new in REPLACEMENTS:
    assert old in html, f"replacement text not found:\n{old[:80]}..."
    html = html.replace(old, new, 1)

with open(HTML_PATH, "w") as f:
    f.write(html)

print(f"Applied {len(REPLACEMENTS)} copy replacements.")
```

- [ ] **Step 2: Run it**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/genericize_copy.py`
Expected: `Applied 7 copy replacements.`

- [ ] **Step 3: Verify no weekend-specific date text remains**

Run: `cd "/Users/voliverm/Documents/brg tracker" && grep -c "21–22.08.2026\|21.08.2026\|22.08.2026" index.html`
Expected: `0`

- [ ] **Step 4: Update `scripts/compose_og_image.py` copy and output path**

Modify the three text lines and the save path:

```python
tracked_text(draw, (margin, 96), "BERLIN  ·  PROGRAMME TRACKER", eyebrow_font, PANORAMA, tracking=2)
draw.text((margin, 150), "BERGHAIN", font=headline_font, fill=FG)
draw.text((margin, 234), "TRACKER", font=headline_font, fill=FG)
draw.text((margin, 358), "Lineups, bios, sets & links — updated automatically each month", font=sub_font, fill=MUTED)
```

```python
canvas.save("og-image.jpg", quality=85)
print("Saved og-image.jpg", canvas.size)
```

(replacing the previous `"BERLIN  ·  21–22.08.2026"` / `"YOUR BERGHAIN"` / `"WEEKEND"` / `"REEF (Fri)  +  Klubnacht (Sat)  —  25 DJs, bios, sets & links"` lines and the `"assets/og-image.jpg"` save path.)

- [ ] **Step 5: Regenerate the OG image**

Run: `cd "/Users/voliverm/Documents/brg tracker" && python3 scripts/compose_og_image.py`
Expected: `Saved og-image.jpg (1200, 630)`

- [ ] **Step 6: Visually confirm the image**

Read `og-image.jpg` (image file) and confirm the text reads "BERLIN · PROGRAMME TRACKER" / "BERGHAIN" / "TRACKER" / the lineups subtext, cleanly within the canvas with no overflow or clipping.

- [ ] **Step 7: Commit**

```bash
git add scripts/genericize_copy.py scripts/compose_og_image.py index.html og-image.jpg
git commit -m "$(cat <<'EOF'
Genericize site copy and OG image for an ongoing programme archive

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Retire superseded files

**Files:**
- Delete: `berghain-tracker.html`
- Delete: `scripts/inject_avatars.py`
- Delete: `scripts/inject_carousel.py`

**Interfaces:** None — pure cleanup.

`berghain-tracker.html` was the pre-Vercel duplicate of `index.html` (already excluded from deployment via `.vercelignore`); left in place it would silently diverge from the real page. `inject_avatars.py` and `inject_carousel.py` both hardcode `HTML_PATH = "berghain-tracker.html"` and embed base64 photo/carousel data into it — both targets and technique are gone as of Tasks 2 and 4.

- [ ] **Step 1: Confirm nothing else references these files**

Run: `cd "/Users/voliverm/Documents/brg tracker" && grep -rl "berghain-tracker.html\|inject_avatars\|inject_carousel" --include="*.py" --include="*.html" --include="*.md" --include="*.json" . 2>/dev/null | grep -v "^\./docs/superpowers/"`
Expected: only the three files themselves (`berghain-tracker.html`, `scripts/inject_avatars.py`, `scripts/inject_carousel.py`) — historical references inside `docs/superpowers/plans` and `docs/superpowers/specs` are fine to leave as-is (they're a record of past decisions, not live code).

- [ ] **Step 2: Delete the files**

```bash
cd "/Users/voliverm/Documents/brg tracker" && git rm berghain-tracker.html scripts/inject_avatars.py scripts/inject_carousel.py
```

- [ ] **Step 3: Commit**

```bash
git commit -m "$(cat <<'EOF'
Retire berghain-tracker.html and its base64-embedding inject scripts

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Manual end-to-end browser verification

**Files:** None created/modified in the repo (all edits in this task are made to a scratch copy and reverted).

**Interfaces:** Exercises everything from Tasks 2–6 together: `fetch`-based load, `renderRow`/`renderFloors`/`renderNav`/`pickDefaultDate`/`setDay`, generic copy, deployed `data/`+`assets/`.

- [ ] **Step 1: Serve the site locally**

`fetch()` of a relative path is blocked by CORS under a `file://` origin, so a local HTTP server is required.

Run (background): `cd "/Users/voliverm/Documents/brg tracker" && python3 -m http.server 8000`

- [ ] **Step 2: Verify the real August data renders correctly**

Open `http://localhost:8000/index.html` in a browser (use the `run` skill or equivalent). Confirm:
- The nav strip shows two buttons: `FRI 21.08 — REEF` and `SAT 22.08 — KLUBNACHT`, with a single `AUG` label before the first one.
- The default-selected button matches whichever of the two dates is closest to the current date (both are in the past relative to 2026-08-05 → Saturday 22.08 should be selected, per `pickDefaultDate`'s fallback to the last day when none are upcoming).
- Berghain/Panorama Bar two-column layout, tag stamps, expand-on-click, and outbound links all behave exactly as before.
- Headhunter and André Galluzzi show their real photos (loaded from `assets/dj-photos/*.jpg`, not embedded); every other DJ shows an initials tile.
- The intro headline reads "Berghain Programme Tracker" (no weekend-specific date).

- [ ] **Step 3: Verify generalized room/day rendering with synthetic data**

Append temporary test days directly to the local `data/lineup.json` (do not commit):

```bash
cd "/Users/voliverm/Documents/brg tracker" && python3 -c "
import json
d = json.load(open('data/lineup.json'))
d['djs']['test-solo'] = {
    'name': 'Test Solo', 'tags': ['Techno'], 'blurb': 'b', 'bio': '',
    'links': {}, 'appearances': [{'date': '2026-09-05', 'event': 'Test Night', 'room': 'Berghain'}],
}
d['days'].append({'date': '2026-09-05', 'weekday': 'SAT', 'event': 'Test Night',
                   'rooms': [{'room': 'Berghain', 'djSlugs': ['test-solo']}]})
d['days'].append({'date': '2026-09-12', 'weekday': 'SAT', 'event': 'Closed', 'rooms': []})
json.dump(d, open('data/lineup.json', 'w'), indent=2)
"
```

Reload the page. Confirm:
- A new `SEP` month label appears before the Sep 5 button.
- Selecting `SAT 05.09 — TEST NIGHT` renders a single column (no staircase divider, no second room).
- Selecting `SAT 12.09 — CLOSED` renders the dim "no lineup listed" placeholder, not empty columns.
- The default-selected day is now Sep 5 (closest upcoming date relative to today) — reload and confirm this without manually clicking anything.

- [ ] **Step 4: Revert the synthetic data**

Run: `cd "/Users/voliverm/Documents/brg tracker" && git checkout -- data/lineup.json`
Verify: `git status` shows `data/lineup.json` is no longer modified.

- [ ] **Step 5: Check mobile width**

Resize the browser (or use device emulation) to ~375px wide. Confirm the nav strip scrolls horizontally without wrapping or breaking layout, and the room columns stack vertically as before.

- [ ] **Step 6: Stop the local server**

Stop the background `http.server` process.

No commit for this task (no repo changes survive it).

---

### Task 8: Write the monthly agent runbook

**Files:**
- Create: `docs/monthly-agent-runbook.md`

**Interfaces:**
- Consumes: the `{djs, days}` schema (Task 2), `scripts/validate_lineup.py`'s CLI (Task 1), the link/photo conventions from Task 4.
- Produces: the exact instructions used as the scheduled agent's prompt in Task 9.

- [ ] **Step 1: Write the runbook**

Create `docs/monthly-agent-runbook.md`:

```markdown
# Monthly Programme Update — Agent Runbook

Run on the 1st of every month at 00:01. Working directory: this repo
(`brg tracker`), on the branch Vercel deploys from.

## 1. Fetch the programme

Fetch `https://www.berghain.berlin/en/program/`. Identify every listing
for the current calendar month — club nights, closing parties, one-off
label nights, concerts, closed days, all of it.

If the fetch fails (unreachable, unexpected structure) after one retry:
**stop here**. Do not write or commit anything. Send a failure
notification describing what went wrong, so this can be checked and
retried by hand.

## 2. Diff against the archive

Read `data/lineup.json`. For each listing found in Step 1, check whether
its date already exists in `days[]`. Skip any date already present (this
makes the run safe to retry or re-trigger without duplicating data).

## 3. Record each new day

For every new date:
- `date` (`YYYY-MM-DD`), `weekday` (`MON`/`TUE`/.../`SUN`), `event` (the
  listing's title as shown on the programme page).
- If it's a DJ/club night: `rooms`, one entry per room actually listed
  (`{"room": "<name>", "djSlugs": [...]}`), using whatever room name the
  page uses verbatim (don't force it into "Berghain"/"Panorama Bar" if
  it's something else, e.g. "Säule").
- If it's not a DJ/club night (concert, closed day, etc.): `rooms: []`
  and nothing further for that date.

## 4. Resolve each DJ name

For every DJ name appearing in a new day's lineup, slugify it the same
way `scripts/migrate_lineup.py` does: lowercase, strip accents, collapse
runs of non-alphanumeric characters to a single hyphen, trim leading/
trailing hyphens (e.g. `"André Galluzzi"` → `"andre-galluzzi"`).

- **Slug already exists in `djs`:** push a new entry onto that DJ's
  `appearances` array (`{"date", "event", "room"}`) for this date. Do
  **not** re-research or modify their `bio`/`tags`/`blurb`/`links`/
  `photo` — those stay exactly as previously researched.
- **New slug:** research and create a full profile:
  - `name`: exact display name as listed.
  - `tags`: 1–3 short genre tags.
  - `blurb`: one-line style description.
  - `bio`: 2–4 sentence bio (omit the key/leave empty string if nothing
    findable — never fabricate).
  - `links`: any of `soundcloud`, `bandcamp`, `applemusic`, `spotify`,
    `instagram`, `youtube` you can confidently find (each omitted if not
    found — no dead links, no placeholders).
  - `photo`: best-effort search for a usable, appropriately-licensed
    press/profile photo (same standard as `assets/dj-photos/CREDITS.md`
    documents: real license, confident identity match, otherwise skip).
    If found: save the image to `assets/dj-photos/<slug>.jpg`, set
    `photo` to that relative path, and append a credit line to
    `assets/dj-photos/CREDITS.md` in the same format as the existing
    entries. If not found: omit `photo` entirely — the page already
    falls back to an initials tile.
  - `stats`: query the berghain-database API
    (`https://berghain.ravers.workers.dev`) for this DJ's Klubnacht
    performance history. If found: `{"performanceCount", "firstPlayed",
    "isResident"}`. If not found: omit the key entirely.
  - `appearances`: a single entry for this date/event/room.

## 5. Validate before writing anything live

Run `python3 scripts/validate_lineup.py`. If it fails: **stop here**, do
not commit, send a failure notification with the validator's output.

## 6. Commit and publish

```bash
git add data/lineup.json assets/dj-photos/
git commit -m "Add <Month Year> programme"
git push
```

If nothing changed in Step 3 (e.g. the programme page hasn't been updated
yet for the new month), skip the commit entirely — an empty run is not a
failure.
```

- [ ] **Step 2: Verify it renders correctly and covers every pipeline step from the spec**

Read the file back and cross-check each numbered section against the
"Monthly Automation Pipeline" section of
`docs/superpowers/specs/2026-08-05-monthly-programme-tracker-design.md`
— confirm all 6 spec steps (fetch, diff, record days, resolve DJs,
validate, commit) are represented with concrete, actionable instructions
and no placeholders.

- [ ] **Step 3: Commit**

```bash
cd "/Users/voliverm/Documents/brg tracker" && git add docs/monthly-agent-runbook.md
git commit -m "$(cat <<'EOF'
Add monthly agent runbook

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Register the monthly scheduled agent

**Files:** None (this registers a cron job via tooling, not a repo file).

**Interfaces:**
- Consumes: `docs/monthly-agent-runbook.md` (Task 8) as the scheduled agent's prompt.

**This task creates a live, recurring, autonomous job that will scrape an
external site and push commits to this repo without further human
approval, starting from its first scheduled fire. Confirm with the user
before completing this task — it is the one step in this plan with an
ongoing real-world effect beyond the repo itself.**

- [ ] **Step 1: Load the `schedule` skill**

Invoke the `schedule` skill to see its exact registration flow and required parameters.

- [ ] **Step 2: Register the routine**

Using the `schedule` skill (backed by `CronCreate`), register a routine:
- **Prompt:** the full contents of `docs/monthly-agent-runbook.md`.
- **Schedule:** 1st of every month at 00:01 (cron: `1 0 1 * *`), in the
  timezone the user confirms is correct for "1st of the month" (Berlin
  time, since the programme is for a Berlin venue — confirm with the user
  if the `schedule` skill asks for an explicit timezone).
- **Working directory / repo context:** this repository, on the branch
  Vercel deploys from.

- [ ] **Step 3: Verify registration without triggering a live run**

List registered routines/cron jobs (via `CronList` or the `schedule`
skill's list view). Confirm:
- The new routine appears with the correct schedule and prompt.
- It has not fired yet (no run has been triggered by registering it).

- [ ] **Step 4: Report back to the user**

Summarize: the routine is registered, its exact schedule, and that its
first live run will be at 00:01 on the 1st of the next calendar month —
at which point it will scrape, research, and (if everything validates)
auto-commit and push without further confirmation, per the approved
design. Suggest the user spot-check the site after that first run.

No code commit for this task.
