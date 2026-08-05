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
