#!/usr/bin/env python3
"""One-off fix:
1. 2026-08-08 actually has 3 rooms (Berghain, Panorama Bar, Garten), not 2
   -- confirmed directly against https://www.berghain.berlin/en/event/80737/.
   Steffi, Virginia, Tama Sumo, and Lakuti were originally misattributed to
   Panorama Bar; they actually played Garten (Steffi b2b Virginia, Tama Sumo
   b2b Lakuti). Move them and add the missing room.
2. Add researched nationality for 32 of 54 DJs (extracted from their
   already-written bios, not fresh research -- see conversation)."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "lineup.json"

GARTEN_SLUGS = ["tama-sumo", "lakuti", "steffi", "virginia"]

NATIONALITY = {
    "alix-perez": {"code": "BE", "name": "Belgium"},
    "altinbas-live": {"code": "TR", "name": "Turkey"},
    "amanda-mussi": {"code": "BR", "name": "Brazil"},
    "andre-galluzzi": {"code": "DE", "name": "Germany"},
    "andy-martin": {"code": "MX", "name": "Mexico"},
    "banu": {"code": "TR", "name": "Turkey"},
    "carre": {"code": "US", "name": "United States"},
    "claudio-prc": {"code": "IT", "name": "Italy"},
    "darwin": {"code": "CA", "name": "Canada"},
    "dbridge": {"code": "GB", "name": "United Kingdom"},
    "dj-maria": {"code": "JP", "name": "Japan"},
    "dubrunner": {"code": "GB", "name": "United Kingdom"},
    "efdemin": {"code": "DE", "name": "Germany"},
    "esposito": {"code": "DE", "name": "Germany"},
    "franziska-berns": {"code": "DE", "name": "Germany"},
    "hunee": {"code": "DE", "name": "Germany"},
    "kaiser": {"code": "IT", "name": "Italy"},
    "kwartz": {"code": "ES", "name": "Spain"},
    "lakuti": {"code": "ZA", "name": "South Africa"},
    "laura-bcr": {"code": "FR", "name": "France"},
    "luke-slater": {"code": "GB", "name": "United Kingdom"},
    "marcel-dettmann": {"code": "DE", "name": "Germany"},
    "mattias-el-mansouri": {"code": "SE", "name": "Sweden"},
    "nicola-cruz": {"code": "EC", "name": "Ecuador"},
    "norman-nodge": {"code": "DE", "name": "Germany"},
    "quelza": {"code": "FR", "name": "France"},
    "rami-abi-rafi": {"code": "LB", "name": "Lebanon"},
    "richard-akingbehin": {"code": "GB", "name": "United Kingdom"},
    "steffi": {"code": "NL", "name": "Netherlands"},
    "tama-sumo": {"code": "DE", "name": "Germany"},
    "virginia": {"code": "BR", "name": "Brazil"},
    "zombies-in-miami": {"code": "MX", "name": "Mexico"},
}


def main():
    data = json.loads(DATA_PATH.read_text())

    # 1. Fix Aug 8 rooms
    day = next(d for d in data["days"] if d["date"] == "2026-08-08")
    panorama = next(r for r in day["rooms"] if r["room"] == "Panorama Bar")
    moved = [s for s in GARTEN_SLUGS if s in panorama["djSlugs"]]
    assert set(moved) == set(GARTEN_SLUGS), f"expected to move {GARTEN_SLUGS}, found {moved}"
    panorama["djSlugs"] = [s for s in panorama["djSlugs"] if s not in GARTEN_SLUGS]
    day["rooms"].append({"room": "Garten", "djSlugs": GARTEN_SLUGS})

    for slug in GARTEN_SLUGS:
        appearance = next(a for a in data["djs"][slug]["appearances"] if a["date"] == "2026-08-08")
        assert appearance["room"] == "Panorama Bar"
        appearance["room"] = "Garten"

    # 2. Add nationality
    added = 0
    for slug, nat in NATIONALITY.items():
        assert slug in data["djs"], f"unknown slug {slug}"
        data["djs"][slug]["nationality"] = nat
        added += 1

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Moved {len(GARTEN_SLUGS)} DJs to new Garten room for 2026-08-08")
    print(f"Added nationality for {added} DJs")


if __name__ == "__main__":
    main()
