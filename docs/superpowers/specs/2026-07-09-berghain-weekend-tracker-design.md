# Berghain Weekend Tracker — Design Spec

**Date:** 2026-07-09
**Status:** Approved for planning

## Purpose

The user is visiting Berlin the weekend of Friday 21.08.2026 and Saturday
22.08.2026, and plans to go to Berghain both nights:

- **Friday 21.08, 22:00 — REEF**
  - Berghain: Alix Perez, Darwin, Dbridge, Esposito, Headhunter
  - Panorama Bar: Arthur, Carré, Dubrunner, Jan Loup, Le Motel & Magugu
- **Saturday 22.08, 23:59 — Klubnacht**
  - Berghain: Amanda Mussi, Andy Martin, Banu, DJ Maria., Kaiser, Kwartz, Norman Nodge
  - Panorama Bar: André Galluzzi, Deepa, Franziska Berns, HUNEE, Maruwa, Mattias El Mansouri, Nicola Cruz, Zombies In Miami

This is a **one-off deliverable** for this specific weekend — not a
reusable/ongoing tracker. The goal is a single interactive page that lets
the user explore both nights' lineups (25 DJs/acts total): who's playing, what
they sound like, and links to actually listen/watch before deciding who to
prioritize once inside.

## Deliverable

A single self-contained **HTML Artifact** (Claude Artifact tool), viewable
in a browser on desktop or phone. No backend, no build step, no runtime
network calls — the Artifact sandbox blocks external requests (iframes,
fetch, remote assets), so all researched data is baked into the page as a
static JS object at authoring time.

This rules out live embedded SoundCloud/YouTube/Instagram players; DJ cards
instead contain outbound links that open the DJ's profile/video in a new
tab. This tradeoff was chosen deliberately over a local (non-sandboxed)
HTML file so the result is shareable/viewable anywhere, including on a
phone, without needing the source file.

## Data Sources

- **Web research** (search, official bios, label pages, RA profiles, etc.)
  for each of the 25 DJs/acts: short bio, SoundCloud profile URL, Instagram
  profile URL, most-viewed/representative YouTube video URL, and 1–3 genre
  tags + a one-line style blurb.
- **berghain-database API** (`https://berghain.ravers.workers.dev`, no
  auth) for Saturday Klubnacht performance history only — e.g. total
  Klubnacht appearances, first-played date, resident status. This API's
  dataset explicitly excludes Friday-series events (REEF), so Friday DJs
  will have no performance-history stats — this is expected, not a bug.

Research is best-effort. Several names on this lineup are lightly
documented online (e.g. "DJ Maria.", "Banu", "Zombies In Miami"). Missing
fields (no SoundCloud found, no bio available, etc.) are simply omitted
from that DJ's card — no fabricated or placeholder content.

## Data Model

Per DJ:

```
{
  name: string,
  day: "friday" | "saturday",
  event: "REEF" | "Klubnacht",
  room: "Berghain" | "Panorama Bar",
  tags: string[],            // 1-3 short genre tags
  blurb: string,              // one-line style description
  bio: string,                 // 2-4 sentence bio, optional if unavailable
  links: {
    soundcloud?: string,
    instagram?: string,
    youtube?: string,         // most-viewed/representative video
  },
  stats?: {                    // Saturday (Klubnacht) only, from berghain-database
    performanceCount: number,
    firstPlayed: string,       // date
    isResident: boolean,
  }
}
```

## Visual Design

Chosen direction: **"Split Floor"** (see Step 3 divergence in
brainstorming session — two other directions, "Concrete Ledger" and "Set
Times", were considered and rejected in favor of this one because it turns
the club's actual physical layout — two rooms connected by a staircase —
into the page's navigation structure).

- **Palette:** near-black concrete background throughout; Berghain column
  uses a cool blue-white accent; Panorama Bar column uses a warm amber
  accent; off-white body text. No pure black/white. Max 3 hues + neutrals.
- **Typography:** off-white, Helvetica-voice sans-serif (matches Berghain's
  own event-page style, per the reference screenshot). Sharp corners
  throughout, no rounded radius — brutalist/industrial, not soft/consumer.
- **Layout:** a day toggle (Friday REEF / Saturday Klubnacht) at the top
  switches the content below. Two columns — Berghain (left) and Panorama
  Bar (right) — separated by a bold vertical divider styled to evoke the
  staircase physically connecting the two rooms. Mobile-first (single
  column stack on narrow viewports, columns side-by-side on wider ones),
  since the user will likely use this on their phone in Berlin.
- **DJ rows:** collapsed by default, showing name + genre tag(s), tags
  styled as small rotated stamp/ticket labels. Clicking a row expands it
  **inline** within its column (not a modal) to reveal the blurb, bio,
  outbound links, and — Saturday only — performance stats. Other rows in
  the column stay visible; the page reflows around the expansion.

## Error Handling / Edge Cases

- DJ with no bio found → bio field omitted, card still renders with
  tags/links only.
- DJ with no SoundCloud/Instagram/YouTube found → that specific link is
  omitted from the card (no dead links, no "not found" placeholder noise).
- Friday DJs → no `stats` block ever (data source doesn't cover Friday);
  Saturday DJs not found in berghain-database (e.g. brand new artist) →
  `stats` omitted, same as any other missing field.

## Verification

This is a static content artifact, so verification is manual/visual:

1. Render the artifact and visually confirm all 25 DJs/acts appear, correctly
   grouped by day/room.
2. Spot-check a handful of outbound links (at least one per link type)
   actually resolve to the correct profile/video.
3. Check the layout at mobile width (~375px) and desktop width for broken
   wrapping/overflow, per the ui-designer skill's "render and look at your
   own output" step.
4. Confirm the day toggle correctly swaps between Friday/Saturday content.

## Out of Scope

- Any mechanism to refresh/re-pull lineup data for future dates (this is
  explicitly a one-off for the 21–22 Aug 2026 weekend).
- Filtering/sorting UI — 25 DJs/acts across 2 columns is small enough to browse
  directly; adding filters would be premature for this dataset size.
- A "must-see"/favorites marking feature — not requested; the user has
  already decided to attend both nights, this is a browsing/reference tool,
  not a decision-support tool.
- Live embedded audio/video players (ruled out by the Artifact sandbox's
  CSP, see Deliverable section).

## Repo Note

This working directory (`brg tracker`) is not a git repository, so this
spec is saved as a plain file rather than committed. No git init was
performed since it wasn't requested.
