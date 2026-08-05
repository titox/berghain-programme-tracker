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
