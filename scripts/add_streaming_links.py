#!/usr/bin/env python3
"""One-off script: add researched Bandcamp/Apple Music/Spotify links to
existing DJ profiles in data/lineup.json. Best-effort, identity-verified
findings only -- DJs/platforms not confidently matched are simply absent
from NEW_LINKS below, per the project's never-fabricate rule."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "lineup.json"

NEW_LINKS = {
    "alix-perez": {"bandcamp": "https://alixperez.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/alix-perez/203209842", "spotify": "https://open.spotify.com/artist/4e6pQ61gYReORJoXcrQH1Z"},
    "dbridge": {"bandcamp": "https://dbridge.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/dbridge/152760346", "spotify": "https://open.spotify.com/artist/4G1BTcGLvvsItegHSvBH0y"},
    "headhunter": {"bandcamp": "https://dubstepheadhunter.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/addison-groove/427349322", "spotify": "https://open.spotify.com/artist/6LG1BzyImz45pwMF6ft7Yr"},
    "carre": {"bandcamp": "https://carre-carre.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/carre/1695916096", "spotify": "https://open.spotify.com/artist/4OvPiX5d1CRMoTuqvoq202"},
    "dubrunner": {"bandcamp": "https://dubrunner.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/dubrunner/1487702116", "spotify": "https://open.spotify.com/artist/0rIFRZ3N5Hcwdppkt0wo9w"},
    "jan-loup": {"bandcamp": "https://janloup.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/jan-loup/1460834701", "spotify": "https://open.spotify.com/artist/44MvjyW33ZyJ7SictqJK2G"},
    "le-motel-magugu": {"bandcamp": "https://magugu1.bandcamp.com/album/bitter-better", "applemusic": "https://music.apple.com/gb/album/bitter-better/1823013031", "spotify": "https://open.spotify.com/album/08bubTmlwYnVkMW7m6jGUB"},
    "amanda-mussi": {"bandcamp": "https://amandamussi.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/amanda-mussi/1434450962", "spotify": "https://open.spotify.com/artist/6yoR3GxDnUclI3jI8exbvQ"},
    "andy-martin": {"bandcamp": "https://diasporaechoes.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/andy-martin/485286197", "spotify": "https://open.spotify.com/artist/0Jz8IMWrZOWnILYFJmdyE2"},
    "banu": {"bandcamp": "https://intergalacticresearchinstituteforsound.bandcamp.com/album/transsoundscapes", "applemusic": "https://music.apple.com/us/artist/banu/275718037", "spotify": "https://open.spotify.com/artist/2WXqHLTFdbRHrAsDSBvrHJ"},
    "dj-maria": {"bandcamp": "https://katharsis.bandcamp.com/album/silver-lining-ep-katharsis-006", "applemusic": "https://music.apple.com/us/artist/dj-maria/160953956", "spotify": "https://open.spotify.com/artist/6FQS0bHtvPig6kqIhhzAZO"},
    "kaiser": {"bandcamp": "https://kaiserksr.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/kaiser-k-s-r/1576846126", "spotify": "https://open.spotify.com/artist/5U3XDNsNoGPXsiXQzPg5LR"},
    "kwartz": {"bandcamp": "https://kwartz.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/kwartz/445260517", "spotify": "https://open.spotify.com/artist/6jgHZXMwN5vXQxNs72dQpA"},
    "norman-nodge": {"applemusic": "https://music.apple.com/us/artist/norman-nodge/309702821", "spotify": "https://open.spotify.com/artist/3XsZjgYO83dSNppZzXlzFB"},
    "andre-galluzzi": {"bandcamp": "https://andregalluzzi.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/andr%C3%A9-galluzzi/276537999", "spotify": "https://open.spotify.com/artist/1V9PJvMVxLIxhCdHCn8SC6"},
    "hunee": {"bandcamp": "https://hunee.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/hunee/330283087", "spotify": "https://open.spotify.com/artist/6uElH4moADg7AGB3DCGOwy"},
    "maruwa": {"bandcamp": "https://maruwa.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/maruwa/1456768143", "spotify": "https://open.spotify.com/artist/6jvVhsNfiC1BXMtZHKpgHF"},
    "mattias-el-mansouri": {"bandcamp": "https://melmansouri.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/mattias-el-mansouri/1703214232", "spotify": "https://open.spotify.com/artist/6pNtdoHIGx5LR9iNY2XRxx"},
    "nicola-cruz": {"bandcamp": "https://nicolacruz.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/nicola-cruz/544158384", "spotify": "https://open.spotify.com/artist/0OltT51j3hIkgaDJqqPzDn"},
    "zombies-in-miami": {"bandcamp": "https://zombiesinmiami.bandcamp.com/", "applemusic": "https://music.apple.com/us/artist/zombies-in-miami/519720189", "spotify": "https://open.spotify.com/artist/42ZWiibQTSxTJSBV7oziPy"},
}


def main():
    data = json.loads(DATA_PATH.read_text())
    updated = 0
    for slug, links in NEW_LINKS.items():
        dj = data["djs"][slug]
        dj["links"].update(links)
        updated += 1
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Added streaming links to {updated} DJ profiles")


if __name__ == "__main__":
    main()
