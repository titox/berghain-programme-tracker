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

    def test_days_out_of_order_fails(self):
        data = minimal_data()
        data["djs"]["second-dj"] = {
            "name": "Second DJ",
            "tags": ["Techno"],
            "blurb": "b",
            "bio": "bio",
            "links": {},
            "appearances": [{"date": "2026-08-14", "event": "Klubnacht", "room": "Berghain"}],
        }
        data["days"].append({
            "date": "2026-08-14", "weekday": "FRI", "event": "Klubnacht",
            "rooms": [{"room": "Berghain", "djSlugs": ["second-dj"]}],
        })
        errors = check(data)
        self.assertTrue(
            any(
                "not sorted ascending by date (found '2026-08-14' after '2026-08-21')" in e
                for e in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
