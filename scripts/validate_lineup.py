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
