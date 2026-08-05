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
