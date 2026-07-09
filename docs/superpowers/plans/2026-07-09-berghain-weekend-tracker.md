# Berghain Weekend Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single self-contained HTML Artifact that lets the user browse the 25 DJs/acts playing Berghain's Friday 21.08.2026 REEF and Saturday 22.08.2026 Klubnacht, with researched bios/links/genre tags and (Saturday only) performance-history stats from the berghain-database API.

**Architecture:** Two phases. Phase 1 (Tasks 1-5) researches and assembles a structured `data/lineup.json` covering all 25 DJs/acts, validated by a small Python script. Phase 2 (Tasks 6-8) builds `berghain-tracker.html` — a static page with the researched data embedded inline as a JS object, styled per the "Split Floor" visual direction, then publishes it as a Claude Artifact.

**Tech Stack:** Plain HTML/CSS/JS (no framework, no build step — required by the Artifact sandbox). Python 3 (stdlib only) for data validation. `curl` for berghain-database API queries.

## Global Constraints

- Deliverable is a single self-contained HTML Artifact — no runtime network calls, no fetch/iframe/external requests (Artifact sandbox blocks these). All data must be inlined at build time.
- Missing research fields (no bio found, no SoundCloud found, etc.) are omitted from that DJ's entry — never fabricated or filled with placeholder text.
- Friday DJs/acts never get a `stats` block — the berghain-database API's dataset excludes Friday-series events (REEF) by design, not by error.
- Palette: near-black concrete background; cool blue-white accent for Berghain; warm amber accent for Panorama Bar; off-white body text; no pure `#000`/`#FFF`; max 3 hues + neutrals.
- Sharp corners only — no `border-radius` anywhere (brutalist/industrial direction).
- Mobile-first responsive: single-column stack below 768px, side-by-side two-column "Split Floor" layout at 768px and above.
- DJ rows are collapsed by default (name + tags only) and expand **inline** on click — no modal.
- This directory was not a git repository at spec time; it has since been initialized locally (`git init`, no remote) to support per-task commits and diff-based review under subagent-driven-development. Commit at the end of each task as normal. Do not add a remote and do not push anywhere.
- Out of scope (do not build): filtering/sorting UI, a favorites/must-see marking feature, live embedded SoundCloud/YouTube/Instagram players, any mechanism to refresh lineup data for dates other than 21-22 Aug 2026.

---

## Task 1: Data schema, skeleton lineup, and validation script

**Files:**
- Create: `data/lineup.json`
- Create: `scripts/validate_lineup.py`

**Interfaces:**
- Produces: `data/lineup.json` — a JSON array of 25 objects, each with keys `name` (string), `day` (`"friday"|"saturday"`), `event` (`"REEF"|"Klubnacht"`), `room` (`"Berghain"|"Panorama Bar"`), `tags` (string[]), `blurb` (string), `bio` (string), `links` (object with optional `soundcloud`/`instagram`/`youtube` string keys), and optionally `stats` (object with `performanceCount` (number), `firstPlayed` (string), `isResident` (bool)) — Saturday entries only.
- Produces: `scripts/validate_lineup.py` — CLI validator, used by every later task. Usage: `python3 scripts/validate_lineup.py [--enriched [--day <day>] [--room <room>]] [--stats]`. Always runs structural checks (fatal on failure); `--enriched` prints non-fatal warnings for entries missing tags/blurb/links, optionally filtered by `--day`/`--room`; `--stats` fatally validates the Friday-never-has-stats rule and Saturday `stats` shape.

- [ ] **Step 1: Create the skeleton data file**

Write `data/lineup.json`:

```json
[
  {"name": "Alix Perez", "day": "friday", "event": "REEF", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Darwin", "day": "friday", "event": "REEF", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Dbridge", "day": "friday", "event": "REEF", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Esposito", "day": "friday", "event": "REEF", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Headhunter", "day": "friday", "event": "REEF", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Arthur", "day": "friday", "event": "REEF", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Carré", "day": "friday", "event": "REEF", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Dubrunner", "day": "friday", "event": "REEF", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Jan Loup", "day": "friday", "event": "REEF", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Le Motel & Magugu", "day": "friday", "event": "REEF", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Amanda Mussi", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Andy Martin", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Banu", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "DJ Maria.", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Kaiser", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Kwartz", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Norman Nodge", "day": "saturday", "event": "Klubnacht", "room": "Berghain", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "André Galluzzi", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Deepa", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Franziska Berns", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "HUNEE", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Maruwa", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Mattias El Mansouri", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Nicola Cruz", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}},
  {"name": "Zombies In Miami", "day": "saturday", "event": "Klubnacht", "room": "Panorama Bar", "tags": [], "blurb": "", "bio": "", "links": {}}
]
```

- [ ] **Step 2: Create the validation script**

Write `scripts/validate_lineup.py`:

```python
#!/usr/bin/env python3
"""Validate data/lineup.json against the expected Berghain weekend lineup."""
import json
import sys
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "lineup.json"

EXPECTED_COUNTS = {
    ("friday", "Berghain"): 5,
    ("friday", "Panorama Bar"): 5,
    ("saturday", "Berghain"): 7,
    ("saturday", "Panorama Bar"): 8,
}

REQUIRED_KEYS = {"name", "day", "event", "room", "tags", "blurb", "bio", "links"}


def load():
    with open(DATA_PATH) as f:
        return json.load(f)


def check_structure(entries):
    errors = []
    if len(entries) != 25:
        errors.append(f"expected 25 entries, got {len(entries)}")
    counts = {}
    for e in entries:
        missing = REQUIRED_KEYS - e.keys()
        if missing:
            errors.append(f"{e.get('name', '?')}: missing keys {missing}")
        key = (e.get("day"), e.get("room"))
        counts[key] = counts.get(key, 0) + 1
    for key, expected in EXPECTED_COUNTS.items():
        actual = counts.get(key, 0)
        if actual != expected:
            errors.append(f"{key}: expected {expected} entries, got {actual}")
    return errors


def check_enriched(entries, day=None, room=None):
    warnings = []
    for e in entries:
        if day and e["day"] != day:
            continue
        if room and e["room"] != room:
            continue
        if not e["tags"]:
            warnings.append(f"{e['name']}: no tags")
        if not e["blurb"]:
            warnings.append(f"{e['name']}: no blurb")
        if not e["links"]:
            warnings.append(f"{e['name']}: no links at all")
    return warnings


def check_saturday_stats(entries):
    errors = []
    for e in entries:
        if e["day"] != "saturday":
            if "stats" in e:
                errors.append(f"{e['name']}: Friday entry must not have a stats block")
            continue
        if "stats" in e:
            stats = e["stats"]
            for k in ("performanceCount", "firstPlayed", "isResident"):
                if k not in stats:
                    errors.append(f"{e['name']}: stats missing '{k}'")
    return errors


def main():
    args = sys.argv[1:]
    entries = load()
    errors = check_structure(entries)

    if "--enriched" in args:
        day = args[args.index("--day") + 1] if "--day" in args else None
        room = args[args.index("--room") + 1] if "--room" in args else None
        warnings = check_enriched(entries, day=day, room=room)
        if warnings:
            print(f"WARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")

    if "--stats" in args:
        errors += check_saturday_stats(entries)

    if errors:
        print(f"FAIL ({len(errors)} issue(s)):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print(f"OK: {len(entries)} entries valid")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the validator**

Run: `python3 scripts/validate_lineup.py`
Expected: `OK: 25 entries valid`

- [ ] **Step 4: Commit**

```bash
git add data/lineup.json scripts/validate_lineup.py
git commit -m "Add lineup data schema, skeleton, and validator"
```

---

## Task 2: Research Friday REEF — Berghain room (5 acts)

**Files:**
- Modify: `data/lineup.json` (entries where `day="friday"` and `room="Berghain"`: Alix Perez, Darwin, Dbridge, Esposito, Headhunter)

**Interfaces:**
- Consumes: `data/lineup.json` schema and `scripts/validate_lineup.py` from Task 1.
- Produces: no new interface — same file, same schema, these 5 entries now enriched.

- [ ] **Step 1: Research each artist**

For each of Alix Perez, Darwin, Dbridge, Esposito, Headhunter, use web search to find:
- 1-3 short genre tags (e.g. `"Drum & Bass"`, `"Techno"`, `"Halftime"`) and a one-line style blurb.
- A 2-4 sentence bio (label affiliations, notable releases/history, what they're known for).
- Their official SoundCloud profile URL, Instagram profile URL, and one representative/most-viewed YouTube video URL (a DJ set, Boiler Room, or RA mix if one exists).

Verify each found link actually belongs to this specific artist (these are DJ/producer names — disambiguate against unrelated people/brands with the same name) before recording it.

- [ ] **Step 2: Update the JSON entries**

Edit the 5 corresponding objects in `data/lineup.json`, filling `tags`, `blurb`, `bio`, and `links`. Omit any of `soundcloud`/`instagram`/`youtube` you could not confidently confirm — do not guess a URL. If no bio is found, leave `bio` as `""`.

- [ ] **Step 3: Validate**

Run: `python3 scripts/validate_lineup.py --enriched --day friday --room Berghain`
Expected: `OK: 25 entries valid` plus at most informational `WARNINGS` for any field you were genuinely unable to find (review the warning list — it should only list fields you actually couldn't confirm, not ones you skipped).

- [ ] **Step 4: Commit**

```bash
git add data/lineup.json
git commit -m "Research Friday REEF Berghain lineup"
```

---

## Task 3: Research Friday REEF — Panorama Bar room (5 acts)

**Files:**
- Modify: `data/lineup.json` (entries where `day="friday"` and `room="Panorama Bar"`: Arthur, Carré, Dubrunner, Jan Loup, Le Motel & Magugu)

**Interfaces:**
- Consumes: same as Task 2.
- Produces: same file, these 5 entries now enriched. Note "Le Motel & Magugu" is a back-to-back pairing listed as one slot on the official lineup — research and describe it as a joint act (tags/blurb/bio may cover both names).

- [ ] **Step 1: Research each artist**

Same research approach as Task 2 Step 1, applied to Arthur, Carré, Dubrunner, Jan Loup, and "Le Motel & Magugu" (search the two names both together and separately to disambiguate, since it's a b2b listing).

- [ ] **Step 2: Update the JSON entries**

Same update approach as Task 2 Step 2, applied to these 5 entries.

- [ ] **Step 3: Validate**

Run: `python3 scripts/validate_lineup.py --enriched --day friday --room "Panorama Bar"`
Expected: `OK: 25 entries valid` plus at most informational warnings for genuinely unconfirmable fields.

- [ ] **Step 4: Commit**

```bash
git add data/lineup.json
git commit -m "Research Friday REEF Panorama Bar lineup"
```

---

## Task 4: Research Saturday Klubnacht — Berghain room (7 acts) + performance stats

**Files:**
- Modify: `data/lineup.json` (entries where `day="saturday"` and `room="Berghain"`: Amanda Mussi, Andy Martin, Banu, DJ Maria., Kaiser, Kwartz, Norman Nodge)

**Interfaces:**
- Consumes: same schema as Task 1; berghain-database API at `https://berghain.ravers.workers.dev` (no auth, REST, JSON responses) — relevant endpoints: `/api/artists?search=<query>`, `/api/artists/:id/performances`, `/api/residents/current`.
- Produces: same file, these 7 entries enriched with `tags`/`blurb`/`bio`/`links`, plus `stats` where a confident match is found in berghain-database.

- [ ] **Step 1: Research each artist (bio/links/tags)**

Same web-research approach as Task 2 Step 1, applied to Amanda Mussi, Andy Martin, Banu, DJ Maria., Kaiser, Kwartz, Norman Nodge. Norman Nodge is a well-documented long-time Berghain resident; the others may be more lightly documented — that's expected, omit what can't be confirmed.

- [ ] **Step 2: Query berghain-database for performance history**

For each of the 7 artists, run:

```bash
curl -s "https://berghain.ravers.workers.dev/api/artists?search=<url-encoded-name>" | python3 -m json.tool
```

Inspect the JSON response. If there is a clear, unambiguous match (name matches, not a different artist with a similar name), note the artist's ID and run:

```bash
curl -s "https://berghain.ravers.workers.dev/api/artists/<id>/performances" | python3 -m json.tool
```

From the performance list, compute `performanceCount` (total entries) and `firstPlayed` (earliest date in the list, formatted `YYYY-MM-DD`). Then run:

```bash
curl -s "https://berghain.ravers.workers.dev/api/residents/current" | python3 -m json.tool
```

Set `isResident` to `true` if the artist appears in this residents list, else `false`. If `/api/artists?search=` returns no match or multiple ambiguous matches you can't confidently resolve, skip the `stats` block entirely for that artist — do not guess an ID.

- [ ] **Step 3: Update the JSON entries**

Edit the 7 corresponding objects in `data/lineup.json`: fill `tags`/`blurb`/`bio`/`links` as in Task 2, and add a `stats` object (`{"performanceCount": ..., "firstPlayed": "...", "isResident": ...}`) only for artists with a confident berghain-database match.

- [ ] **Step 4: Validate**

Run: `python3 scripts/validate_lineup.py --enriched --day saturday --room Berghain --stats`
Expected: `OK: 25 entries valid` plus at most informational warnings. The `--stats` flag will fatally fail if any Friday entry has a `stats` block or any `stats` object is missing a required key — fix before proceeding.

- [ ] **Step 5: Commit**

```bash
git add data/lineup.json
git commit -m "Research Saturday Klubnacht Berghain lineup + performance stats"
```

---

## Task 5: Research Saturday Klubnacht — Panorama Bar room (8 acts) + performance stats

**Files:**
- Modify: `data/lineup.json` (entries where `day="saturday"` and `room="Panorama Bar"`: André Galluzzi, Deepa, Franziska Berns, HUNEE, Maruwa, Mattias El Mansouri, Nicola Cruz, Zombies In Miami)

**Interfaces:**
- Consumes: same as Task 4.
- Produces: same file, these 8 entries enriched (and `stats` where matched). After this task, all 25 entries in `data/lineup.json` are fully researched.

- [ ] **Step 1: Research each artist (bio/links/tags)**

Same approach as Task 4 Step 1, applied to André Galluzzi, Deepa, Franziska Berns, HUNEE, Maruwa, Mattias El Mansouri, Nicola Cruz, Zombies In Miami. André Galluzzi and HUNEE are well-documented long-time Panorama Bar residents; others (e.g. Zombies In Miami) may be sparsely documented.

- [ ] **Step 2: Query berghain-database for performance history**

Same process as Task 4 Step 2, applied to these 8 artists.

- [ ] **Step 3: Update the JSON entries**

Same process as Task 4 Step 3, applied to these 8 entries.

- [ ] **Step 4: Validate the full dataset**

Run: `python3 scripts/validate_lineup.py --enriched --stats`
Expected: `OK: 25 entries valid` (no `--day`/`--room` filter this time — checks all 25 entries at once). Review any warnings; each should correspond to a field you genuinely could not confirm for that specific artist.

- [ ] **Step 5: Commit**

```bash
git add data/lineup.json
git commit -m "Research Saturday Klubnacht Panorama Bar lineup + performance stats"
```

`data/lineup.json` is now the final, fully-researched dataset feeding the HTML build in Tasks 6-8.

---

## Task 6: Build the HTML artifact — structure, visual system, static render

**Files:**
- Create: `berghain-tracker.html`

**Interfaces:**
- Consumes: the final `data/lineup.json` from Task 5 (its full JSON content is embedded verbatim as a JS `const LINEUP = [...]` inside this file — the Artifact sandbox cannot fetch the external file at runtime).
- Produces: `LINEUP` (array, in-page global), `renderDay(day)` (function, renders both columns for `"friday"` or `"saturday"`) — consumed by Task 7's interactivity code.

Per the Artifact tool's requirements: this file must NOT contain `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags — write the page content directly (styles, markup, script), it gets wrapped automatically at publish time.

- [ ] **Step 1: Write the file with embedded styles, markup, and data**

Write `berghain-tracker.html`. Read the contents of `data/lineup.json` (from Task 5) and paste its JSON array as the value of `LINEUP` in the script block below (replace the `[]` placeholder with the real array — this is the only "placeholder" in this plan, and it's filled from a file produced by Task 5, not invented):

```html
<style>
  :root {
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
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: var(--font);
  }
  .page { max-width: 1100px; margin: 0 auto; padding: var(--space-4); }
  .toggle { display: flex; gap: var(--space-2); margin-bottom: var(--space-5); }
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
  .toggle-btn.active { color: var(--fg); border-color: var(--fg); }
  .floors { display: flex; flex-direction: column; }
  .staircase {
    display: none;
    width: 14px;
    background: repeating-linear-gradient(
      to bottom, var(--rule) 0 6px, transparent 6px 14px
    );
  }
  .room { flex: 1; padding-top: var(--space-4); }
  .room h2 {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 var(--space-3) 0;
    padding-bottom: var(--space-2);
    border-bottom: 3px solid var(--room-accent);
  }
  .room--berghain { --room-accent: var(--berghain); }
  .room--panorama { --room-accent: var(--panorama); }
  .dj-row { border-bottom: 1px solid var(--rule); padding: var(--space-3) 0; cursor: pointer; }
  .dj-summary { display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-2); }
  .dj-name { font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; }
  .tag {
    display: inline-block;
    padding: 2px 8px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid var(--room-accent);
    color: var(--room-accent);
    transform: rotate(-2deg);
  }
  .dj-detail { display: none; padding-top: var(--space-3); color: var(--muted); font-size: 14px; line-height: 1.5; }
  .dj-row.expanded .dj-detail { display: block; }
  .dj-blurb { color: var(--fg); font-style: italic; margin: 0 0 var(--space-2) 0; }
  .dj-bio { margin: 0 0 var(--space-2) 0; }
  .dj-stats { margin: 0 0 var(--space-2) 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
  .dj-links a { color: var(--fg); margin-right: var(--space-3); text-decoration: underline; }
  @media (min-width: 768px) {
    .floors { flex-direction: row; }
    .staircase { display: block; }
    .room { padding-top: 0; padding-left: var(--space-4); padding-right: var(--space-4); }
  }
</style>

<div class="page">
  <header class="toggle">
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
  </div>
</div>

<script>
const LINEUP = [];

function renderRow(dj) {
  const tags = dj.tags.map(t => `<span class="tag">${t}</span>`).join('');
  const links = Object.entries(dj.links || {})
    .map(([k, url]) => `<a href="${url}" target="_blank" rel="noopener">${k}</a>`)
    .join('');
  const stats = dj.stats
    ? `<div class="dj-stats">${dj.stats.performanceCount} Klubnacht performances since ${dj.stats.firstPlayed}${dj.stats.isResident ? ' · Resident' : ''}</div>`
    : '';
  return `
    <div class="dj-row">
      <div class="dj-summary">
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

renderDay('friday');
</script>
```

- [ ] **Step 2: Manually verify structure and data**

Open `berghain-tracker.html` in a browser (double-click the file, or `open "berghain-tracker.html"` on macOS). Confirm:
- The Friday column headers "Berghain" and "Panorama Bar" each show, and together list exactly 10 names (5 + 5).
- Every row shows the DJ's name and their tag(s).
- No row is expanded yet (no interactivity added — that's Task 7).

- [ ] **Step 3: Commit**

```bash
git add berghain-tracker.html
git commit -m "Add HTML artifact structure, visual system, and static render"
```

---

## Task 7: Add day toggle and expand/collapse interactivity

**Files:**
- Modify: `berghain-tracker.html`

**Interfaces:**
- Consumes: `LINEUP`, `renderDay(day)` from Task 6.
- Produces: fully interactive page (no further JS interfaces needed by later tasks — Task 8 only touches CSS).

- [ ] **Step 1: Wire up the day toggle buttons and row expansion**

In `berghain-tracker.html`, inside the existing `<script>` block from Task 6, replace the final line `renderDay('friday');` with:

```js
document.getElementById('toggle-fri').addEventListener('click', () => setDay('friday'));
document.getElementById('toggle-sat').addEventListener('click', () => setDay('saturday'));

function setDay(day) {
  document.getElementById('toggle-fri').classList.toggle('active', day === 'friday');
  document.getElementById('toggle-sat').classList.toggle('active', day === 'saturday');
  renderDay(day);
}

document.addEventListener('click', (e) => {
  const row = e.target.closest('.dj-row');
  if (row) row.classList.toggle('expanded');
});

setDay('friday');
```

(This stays inside the same `<script>...</script>` tag pair already in the file — do not add a second `<script>` block.)

- [ ] **Step 2: Manually verify interactivity**

Open `berghain-tracker.html` in a browser. Confirm:
- Clicking "SAT 22.08 — KLUBNACHT" swaps both columns to show the 7 + 8 Saturday names, and the button's active state (underline/border) moves to it.
- Clicking "FRI 21.08 — REEF" swaps back to the 10 Friday names.
- Clicking any DJ row expands it inline to show blurb/bio/links (and stats, for Saturday DJs that have them) without hiding neighboring rows; clicking it again collapses it.
- Clicking a DJ row whose `bio` is empty (if any) still expands cleanly — it just omits the bio paragraph, no broken layout or empty gap.
- Every outbound link opens in a new tab (`target="_blank"`).

- [ ] **Step 3: Commit**

```bash
git add berghain-tracker.html
git commit -m "Add day toggle and expand/collapse interactivity"
```

---

## Task 8: Responsive polish and final verification

**Files:**
- Modify: `berghain-tracker.html`

**Interfaces:**
- Consumes: the fully interactive page from Task 7.
- Produces: the final artifact, published via the Artifact tool.

- [ ] **Step 1: Verify responsive behavior**

Open `berghain-tracker.html` in a browser and resize the window (or use browser dev tools device emulation) to check both breakpoints:
- **Below 768px:** columns stack vertically (Berghain above Panorama Bar), the staircase divider is hidden (`display: none` per the CSS in Task 6 — confirm it's not visible), no horizontal scrolling or overflow, tags wrap onto multiple lines cleanly instead of overflowing.
- **768px and above:** columns sit side by side with the staircase divider visible between them.

If any overflow, text clipping, or broken wrapping is found, fix the specific CSS rule in `berghain-tracker.html` responsible (e.g. add `flex-wrap: wrap` or adjust padding) and re-check.

- [ ] **Step 2: Run the full spec verification checklist**

Using the running page (or the data file directly), confirm each item from the spec's Verification section:

1. All 25 DJs/acts appear, correctly grouped by day/room — cross-check counts against `python3 scripts/validate_lineup.py` output (`OK: 25 entries valid`).
2. Spot-check at least one SoundCloud link, one Instagram link, and one YouTube link by clicking them and confirming they open the correct artist's profile/video.
3. Mobile width (~375px) and desktop width both render without broken wrapping/overflow (from Step 1).
4. The day toggle correctly swaps between Friday/Saturday content (from Task 7 Step 2).

- [ ] **Step 3: Publish as a Claude Artifact**

Use the Artifact tool with `file_path` set to `berghain-tracker.html`, a descriptive `title` (already set via the page content, but confirm one exists or add a `<title>`... note: per Artifact tool rules, no `<head>` tag is allowed in this file, so skip a literal `<title>` tag — pass the artifact's display title and one-sentence `description` as tool parameters instead), and an appropriate `favicon` emoji (e.g. a single staircase/building-adjacent or music-adjacent emoji such as 🎧 or 🏭).

- [ ] **Step 4: Commit**

```bash
git add berghain-tracker.html
git commit -m "Responsive polish and final verification"
```

The published Artifact URL is the final deliverable — share it with the user.
