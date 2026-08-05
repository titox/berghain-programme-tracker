# Monthly Programme Update — Agent Runbook

Run on the 1st of every month at 00:01. Working directory: this repo
(`brg tracker`), on the branch Vercel deploys from.

## 1. Fetch the programme

Fetch `https://www.berghain.berlin/en/program/`. Identify every listing
currently shown on the page — club nights, closing parties, one-off
label nights, concerts, closed days, all of it — regardless of which
month it falls in. Step 2 already skips any date already archived, so
scoping this to "the current month" is unnecessary and would create
permanent gaps if the page hasn't published the full month yet when
this runs; fetching everything shown makes each run self-healing for
whatever the page currently displays, old or new.

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

After appending any new day, re-sort `days[]` ascending by `date` so nav
ordering and default-day selection stay correct.

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
