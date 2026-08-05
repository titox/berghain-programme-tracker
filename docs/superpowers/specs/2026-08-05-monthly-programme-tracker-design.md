# Monthly Programme Tracker — Design Spec

**Date:** 2026-08-05
**Status:** Approved for planning

## Purpose

The existing site (`index.html`) is a one-off, hand-built page for a single
weekend (Fri 21.08 REEF / Sat 22.08 Klubnacht 2026), with all DJ research
done manually in a Claude Code chat and all data/photos embedded directly
in the HTML as a Claude Artifact-compatible static file.

This expands it into an **ongoing, self-updating archive** of Berghain's
monthly programme:

- A scheduled agent runs on the **1st of every month at 00:01**, scrapes
  `https://www.berghain.berlin/en/program/` for that month's listings,
  researches any DJs not already known, updates the data, and publishes —
  with no manual step required.
- The site keeps every month starting **August 2026** (a rolling archive,
  not a rolling window) — nothing is dropped.
- The UI keeps its exact current visual language (palette, typography,
  brutalist/industrial styling, inline-expand DJ rows) but generalizes the
  day toggle into a horizontal-scrolling strip of small per-day buttons
  covering the whole archive, and generalizes the two-column Berghain/
  Panorama Bar layout to handle whatever room structure a given day
  actually has.
- DJ cards gain three new optional outbound links: Apple Music, Spotify,
  Bandcamp.

## Non-Goals (this iteration)

- Month-level grouping/selector UI (dropdown, tabs) — the nav is one
  continuous scroll with inline month labels for now; revisit once a few
  months of real data exist.
- Automatic correction of DJ name spelling variants across months.
- Licensing/rights vetting of auto-sourced avatar photos.
- Any venue other than Berghain.

## Deliverable

The site moves from "single self-contained Artifact-style HTML file" to a
normal small static site on Vercel:

- `index.html` — a static shell: layout, styles, nav/render/expand JS. It
  no longer embeds data or photos inline. On load it `fetch()`s
  `data/lineup.json` and renders from it. (The original "no runtime
  fetch" constraint was specific to the Claude Artifact sandbox; this is
  real hosting, so a same-origin fetch is unremarkable.)
- `data/lineup.json` — the full archive (see Data Model).
- `assets/dj-photos/<slug>.jpg` — individual avatar image files (replacing
  the old base64-embedded photos), only for DJs a research pass found a
  usable photo for; everyone else keeps the existing initials-fallback
  avatar.
- A monthly scheduled agent (Claude Code cron/`schedule`) that performs
  the scrape → research → update → commit → push cycle unattended.

## Data Model

`data/lineup.json`:

```jsonc
{
  "djs": {
    "<slug>": {
      "name": "Alix Perez",
      "tags": ["Drum & Bass", "Liquid Funk", "Halftime"],
      "blurb": "one-line style description",
      "bio": "2-4 sentence bio, optional if unavailable",
      "links": {
        "soundcloud": "https://...",
        "bandcamp": "https://...",
        "applemusic": "https://...",
        "spotify": "https://...",
        "instagram": "https://...",
        "youtube": "https://..."
      },
      "photo": "assets/dj-photos/alix-perez.jpg",   // omitted if none found
      "stats": {                                     // from berghain-database, omitted if not found
        "performanceCount": 12,
        "firstPlayed": "2019-03-01",
        "isResident": false
      },
      "appearances": [                                // our own archive tracking
        { "date": "2026-08-21", "event": "REEF", "room": "Berghain" }
      ]
    }
  },
  "days": [
    {
      "date": "2026-08-21",
      "weekday": "FRI",
      "event": "REEF",
      "rooms": [
        { "room": "Berghain", "djSlugs": ["alix-perez", "darwin", "esposito", "..."] },
        { "room": "Panorama Bar", "djSlugs": ["arthur", "..."] }
      ]
    },
    {
      "date": "2026-08-28",
      "weekday": "FRI",
      "event": "Some Concert",
      "rooms": []
    }
  ]
}
```

Key differences from the original flat per-DJ-per-day list:

- **DJ profiles are deduped** across the whole archive, keyed by a
  slugified name. A returning DJ's existing profile is reused — no
  re-research — and a new entry is pushed onto their `appearances` array
  (this is the "counter," made of real dates rather than a bare integer,
  so it can never drift from what's actually displayed).
- **`stats`** is unchanged in meaning from the original spec: external
  berghain-database performance history, independent of our own
  `appearances` tracking. Both can surface on a card, e.g. "3rd
  appearance since we started tracking · 12 Klubnacht performances
  all-time."
- **`days`** is the new top-level list of every scraped date, in
  chronological order, each with an arbitrary number of `rooms` (0, 1, 2,
  or more) rather than an assumed fixed pair.
- A `days` entry with `rooms: []` is a non-DJ listing (concert, closed
  day, etc.) — rendered as a bare placeholder, not a lineup card.

## UI Design

Visual system (palette, typography, sharp corners, inline-expand DJ rows)
is **unchanged** from the current "Split Floor" design. Two things
generalize:

**Day navigation** — replaces the current two-button Fri/Sat toggle with a
horizontal-scrolling strip of small buttons, one per `days[]` entry, sized
to fit their label (`FRI 21.08 — REEF`) rather than flexing to fill the
row (matches the reference screenshot). A small non-clickable month label
(`AUG`, `SEP`, ...) precedes the first button of each new month as a
visual separator. The default-selected day is computed **client-side**
from the visitor's current date/time (not baked in at generation time) —
whichever day is closest to today, preferring an upcoming/current day
over a past one when equidistant — so the default stays correct every day
between monthly runs, not just on deploy day. The strip auto-scrolls that
button into view on load.

**Room columns** — the Berghain/Panorama Bar two-column layout still
renders for the common case (a day with exactly those two rooms), but the
renderer now iterates `day.rooms` generically: a 1-room day collapses to
a single column, 3+ rooms add columns (still stacking on narrow
viewports, same responsive behavior as today). A `rooms: []` day renders
as a single dim placeholder card (event title + date, no columns, not
expandable) instead of a lineup.

**DJ card links** — `links` gains `bandcamp`, `applemusic`, `spotify`
alongside the existing `soundcloud`, `instagram`, `youtube`. Rendered in a
fixed order — audio platforms first (Soundcloud, Bandcamp, Apple Music,
Spotify), then Instagram, then YouTube — same omit-if-missing behavior as
today, no other markup change (the row renderer already iterates
`Object.entries(links)` generically).

## Monthly Automation Pipeline

A Claude Code scheduled cloud agent (via the `schedule` skill), cron-fired
**1st of each month at 00:01**:

1. **Fetch** `https://www.berghain.berlin/en/program/`; identify every
   listing for the new month (all listing types, not just club nights —
   concerts/closed days included per scope decision).
2. **Diff** against `data/lineup.json.days` by date — any date already
   present is skipped (idempotent against retries or a doubled firing).
3. For each new date: record `date`, `weekday`, `event`, and detected
   `rooms`. A non-DJ listing gets `rooms: []` and nothing further.
4. For each DJ name appearing in a new day's lineup:
   - **Known** (matches an existing `djs` key by trimmed, case-insensitive
     name) → push a new `appearances` entry; no re-research.
   - **New** → research: bio, 1–3 genre tags, one-line blurb, links
     (SoundCloud/Bandcamp/Apple Music/Spotify/Instagram/YouTube, each
     omitted if not found), best-effort avatar photo saved to
     `assets/dj-photos/<slug>.jpg`, and `stats` from berghain-database
     (omitted if not found) — same best-effort/no-fabrication rules as
     the original spec.
5. Run `scripts/validate_lineup.py` (rewritten for the new schema) against
   the updated `data/lineup.json`. **Abort without committing** if it
   fails.
6. Commit `data/lineup.json` and any new photo files; push directly to
   the branch Vercel deploys from.

If the scrape itself fails (site unreachable, page structure changed): the
agent retries once, then aborts the run **without writing or committing
anything**, and sends a failure notification. A skipped month is better
than corrupted or partial data.

`index.html` does not change monthly — only `data/lineup.json` and
`assets/dj-photos/` do. The old `inject_avatars.py` / `inject_carousel.py`
scripts (which embedded base64 into the HTML) are retired in favor of
saving photo files directly; the homepage carousel remains as-is (static,
generic venue photography, not tied to any specific month).

## Error Handling / Edge Cases

- Scrape failure → abort run, no partial writes, failure notification
  sent (see above).
- Missing bio/tags/links/photo for a DJ → field omitted, never fabricated
  or placeholder-filled (unchanged from original spec).
- DJ name spelling variants across months (e.g. "DJ Maria." vs "DJ
  Maria") → may create a duplicate profile instead of merging; not
  auto-resolved in this iteration, fixable by hand-editing
  `lineup.json`.
- Non-standard/unexpected room names (e.g. "Säule") → captured verbatim;
  rendering already handles arbitrary room names/counts.
- Failed schema validation → blocks the commit for that run (see pipeline
  step 5).

## Verification

**This implementation, now** (manual/visual, static content artifact —
same verification style as the original spec):

1. Render locally; confirm the existing Aug 21–22 data still renders
   identically to the current live page (columns, tags, expand
   interaction, stats).
2. Confirm nav renders as a horizontal-scroll strip with inline month
   labels, and the default-selected day is the one closest to today.
3. Add synthetic test days to `lineup.json` — one with 1 room, one with 3
   rooms, one with `rooms: []` — confirm each renders correctly (single
   column, extra column, placeholder card).
4. Confirm new link labels (Bandcamp, Apple Music, Spotify) render and
   open correctly on a test DJ entry.
5. Check mobile (~375px) and desktop widths for broken wrapping/overflow,
   especially the horizontal-scroll nav strip.

**Ongoing**: after the first 1–2 real scheduled runs, manually spot-check
the live site to confirm scrape + research quality before treating the
pipeline as fully unattended.

## Out of Scope

- Month-selector/grouped nav UI — deferred until a few months of real
  data exist to design against.
- Automatic DJ name dedup/typo correction across months.
- Licensing/rights vetting of auto-sourced avatar photos.
- Any venue other than Berghain.
- A UI for manually correcting published archive entries — direct
  `lineup.json` edits + redeploy remains the escape hatch.
