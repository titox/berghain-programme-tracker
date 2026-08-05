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
    prev_date = None
    for day in days:
        missing = REQUIRED_DAY_KEYS - day.keys()
        if missing:
            errors.append(f"days[{day.get('date', '?')}]: missing keys {missing}")
            continue
        if not DATE_RE.match(day["date"]):
            errors.append(f"days: invalid date format '{day['date']}'")
        if day["date"] in seen_dates:
            errors.append(f"days: duplicate date '{day['date']}'")
        if prev_date is not None and day["date"] < prev_date:
            errors.append(
                f"days: not sorted ascending by date (found '{day['date']}' after '{prev_date}')"
            )
        prev_date = day["date"]
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
