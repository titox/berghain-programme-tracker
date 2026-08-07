#!/usr/bin/env python3
"""One-off script: add the Aug 6/7/8 2026 programme (3 new days, 29 new
DJ profiles) to data/lineup.json, following the same {djs, days} schema
and dedup rules as docs/weekly-agent-runbook.md."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "lineup.json"

NEW_DJS = {
    "rami-abi-rafi": {
        "name": "Rami Abi Rafi",
        "tags": ["Experimental", "Cold Wave", "Electronic"],
        "blurb": "Sound artist splicing Lebanese folk memory with cold wave and experimental electronics.",
        "bio": "Rami Abi Rafi is a Lebanese DJ, sound artist, and photographer, born in London and now based between Berlin and Beirut. He hosts radio programs on Radio Al-Hara, NOODS Radio, and Cashmere Radio that blend experimental and traditional Lebanese music, electronic music, cold wave, and folk documentation. His work aims to empower imagination, retelling cultural stories through sound.",
        "links": {"soundcloud": "https://soundcloud.com/ramiabirafi", "instagram": "https://www.instagram.com/ramiabirafi"},
    },
    "conceptual-live": {
        "name": "CONCEPTUAL",
        "tags": ["Techno", "Live Act", "Experimental"],
        "blurb": "Techno reframed as performance art, built from hardware live sets and visual-artist collaboration.",
        "bio": "CONCEPTUAL is a Berlin-based techno live act born from a devotion to techno and to visual and performance art. Performances are frequently built around collaborations with visual artists, staged as immersive audiovisual experiences rather than straightforward DJ sets. In 2021 the artist founded DUNA, a Berlin recording project and label showcasing an evolving roster of experimental techno producers.",
        "links": {"soundcloud": "https://soundcloud.com/conceptual2020"},
    },
    "ayesha": {
        "name": "Ayesha",
        "tags": ["Percussive Techno", "Breaks", "Bass"],
        "blurb": "Brooklyn diaspora sounds channeled into tactile, percussive club tracks.",
        "bio": "Ayesha is a Brooklyn-based DJ and producer who channels the sounds of her diaspora into tactile club experiences, blending American percussive techno with UK soundsystem culture, breaks, and bass. She released the Potential Energy EP on Scuffed Recordings and is a resident at NYC's Nowadays.",
        "links": {"soundcloud": "https://soundcloud.com/aye5ha", "bandcamp": "https://aye5ha.bandcamp.com", "spotify": "https://open.spotify.com/artist/2nmIga6kAJM6a18mZqsE1U", "instagram": "https://www.instagram.com/aye5ha/"},
    },
    "tikiman": {
        "name": "Tikiman",
        "tags": ["Dub", "Reggae", "Dub Techno"],
        "blurb": "The reggae singjay voice that defined the Rhythm & Sound dub-techno sound.",
        "bio": "Tikiman is the alias of Paul St. Hilaire, a reggae vocalist and longtime collaborator of Rhythm & Sound (Mark Ernestus and Moritz von Oswald of Basic Channel). From the mid-1990s onward he became the defining voice on a string of dub-techno singles for Rhythm & Sound and Burial Mix, fusing traditional Jamaican vocal style with minimal, cavernous techno production. In 2023 he released Tikiman Vol. 1, his first solo album in 17 years, on Richard Akingbehin's Kynant Records.",
        "links": {},
    },
    "parallel-9": {
        "name": "Parallel 9",
        "tags": ["Dub Techno", "Deep Techno", "House"],
        "blurb": "Steve Rachmad's rare, hypnotic dub-techno alias, decades deep and still evolving.",
        "bio": "Parallel 9 is one of several aliases of Amsterdam techno pioneer Steve Rachmad (also known as Sterac), reserved for his deepest, most hypnotic and dub-infused productions. Active since the mid-1990s, the project surfaces only at selected moments, marking 2026 as Rachmad's 45th year in music with appearances including Panorama Bar in Berlin. A Parallel 9 set is built as a slow, atmospheric journey emphasizing depth and subtlety over dancefloor immediacy.",
        "links": {"soundcloud": "https://soundcloud.com/steverachmad", "instagram": "https://www.instagram.com/steve_rachmad_sterac/", "spotify": "https://open.spotify.com/artist/5VWshOLeHwzhDjFl3HrbMG"},
    },
    "richard-akingbehin": {
        "name": "Richard Akingbehin",
        "tags": ["Dub Techno", "House", "Techno"],
        "blurb": "Kynant Records founder threading dub weight through house and techno.",
        "bio": "Richard Akingbehin is a British-Nigerian DJ and curator based in Berlin whose sets draw on Jamaican and UK soundsystem culture, using the heavy basslines and spatial effects of dub to guide a blend of house and techno. He founded Kynant Records in 2015 and co-founded Berlin's Refuge Worldwide radio station in 2021. He has a close collaborative history with dub vocalist Tikiman, whose 2023 comeback album he released on Kynant.",
        "links": {"soundcloud": "https://soundcloud.com/richard-akingbehin", "instagram": "https://instagram.com/richardakingbehin"},
    },
    "aurora-halal": {
        "name": "Aurora Halal",
        "tags": ["Techno", "Acid", "Experimental"],
        "blurb": "Shadowy, psychedelic hardware techno with metallic dancefloor intensity.",
        "bio": "Aurora Halal is a New York-based producer and DJ who has been a driving force in the NYC underground since 2010, founding both the Sustain-Release festival and Brooklyn's Mutual Dreaming party series. Her hardware-driven live and DJ sets are shadowy and psychedelic, marked by a hazy sensuality and metallic dancefloor intensity. She has held residencies at Nowadays in New York and played regularly at Berghain in Berlin.",
        "links": {"instagram": "https://www.instagram.com/AuroraHalal/"},
    },
    "laura-bcr": {
        "name": "Laura BCR",
        "tags": ["Dub Techno", "Ambient Techno", "Deep House"],
        "blurb": "Deep, dubby, vinyl-only techno from the founder of On Board Music.",
        "bio": "Laura BCR, real name Laura Le Marchand, is a French DJ-producer and founder of the On Board Music label and agency. She took her alias from Bass Cadet Records, a Berlin record store she co-founded in 2013, and is known for transportive, atmospheric DJ sets that move between deep, dubby techno and ambient textures. Originally from southern France, she played bass in a band before moving into DJing and party organizing between Paris and Berlin.",
        "links": {"soundcloud": "https://soundcloud.com/laurabcr", "bandcamp": "https://laurabcr01.bandcamp.com", "instagram": "https://www.instagram.com/laura___bcr/"},
    },
    "altinbas-live": {
        "name": "Altinbas",
        "tags": ["Techno", "Electronic"],
        "blurb": "Turkish/Belgian producer and Fuse resident known for sculpted sound design and emotionally-charged, journey-driven techno.",
        "bio": "Ahmet Altinbas is a Turkish/Belgian producer, Fuse resident, and co-curator of the Fuse Imprint label based in Brussels. His productions favor researched, sculpted sound design over pure impact, released on labels including Token Records, SK11, and Non Series, as well as his own imprint Observer Station. As a DJ he builds sets as narrative journeys, and he has contributed podcasts to Hate, Slam Radio, Reclaim Your City, and Monument.",
        "links": {"soundcloud": "https://soundcloud.com/altinbas", "applemusic": "https://music.apple.com/us/artist/altinbas/1038438994"},
        "stats": {"performanceCount": 11, "firstPlayed": "2024-03-23"},
    },
    "fadi-mohem-live": {
        "name": "Fadi Mohem",
        "tags": ["Techno"],
        "blurb": "Berlin-based Berghain resident driving hypnotic, peak-time techno rooted in a drum & bass upbringing.",
        "bio": "Fadi Mohem is a Berlin-based electronic music producer and current Berghain resident DJ. He discovered dance music through drum and bass as a teenager before developing a broad stylistic range with no strict genre boundaries. His debut Reckless EP launched Werk, a label offshoot of the Berlin event series of the same name, and his releases have since appeared on techno imprints including Klockworks.",
        "links": {"soundcloud": "https://soundcloud.com/fadimohem", "instagram": "https://www.instagram.com/fadi.mohem/", "applemusic": "https://music.apple.com/us/artist/fadi-mohem/1294383534"},
        "stats": {"performanceCount": 39, "firstPlayed": "2019-12-28", "isResident": True},
    },
    "claudio-prc": {
        "name": "Claudio PRC",
        "tags": ["Techno", "House"],
        "blurb": "Sardinian producer crafting deep, hypnotic techno and house rooted in Detroit and Birmingham influences.",
        "bio": "Claudio PRC grew up near Oristano in Sardinia, Italy, discovering music through his father's Northern Soul record collection. He began exploring Detroit techno and artists like Plastikman and Donato Dozzy at 18, DJing across Sardinia from 2004 before turning to production in 2007. His deep, hypnotic techno and house releases have appeared on Prologue, Stroboscopic Artefacts, and Elettronica Romana.",
        "links": {"soundcloud": "https://soundcloud.com/claudioprc", "bandcamp": "https://claudioprc.bandcamp.com", "instagram": "https://www.instagram.com/claudioprc/", "applemusic": "https://music.apple.com/us/artist/claudio-prc/265933617"},
        "stats": {"performanceCount": 7, "firstPlayed": "2011-10-08"},
    },
    "efdemin": {
        "name": "Efdemin",
        "tags": ["Techno", "House", "Minimal"],
        "blurb": "Berlin producer known for a deep, psychedelic, idiosyncratic take on house and techno, longtime Ostgut Ton/Dial artist.",
        "bio": "Efdemin, real name Phillip Sollmann, is a Berlin-based DJ, producer and musician born in 1974 in Kassel, Germany. Known for a deep, psychedelic and idiosyncratic take on house and techno, he has released numerous 12-inches alongside three albums on Hamburg's Dial Records and the 2019 LP New Atlantis on Berghain's own label Ostgut Ton. He studied at the Institute for Computer Music in Vienna and has also worked in sound installation and opera.",
        "links": {"soundcloud": "https://soundcloud.com/efdemin", "instagram": "https://www.instagram.com/efdemin/", "applemusic": "https://music.apple.com/us/artist/efdemin/187025980"},
        "stats": {"performanceCount": 87, "firstPlayed": "2006-08-05", "isResident": True},
    },
    "gigi-fm": {
        "name": "GiGi FM",
        "tags": ["Techno"],
        "blurb": "Techno DJ and producer building a growing profile in the Berlin club scene.",
        "bio": "GiGi FM, also known as Gisele Soares Costa Ribeiro, is a techno DJ and producer who has been playing Berghain's Klubnacht since 2022. Her music is distributed digitally, including via Bandcamp and Apple Music.",
        "links": {"soundcloud": "https://soundcloud.com/gigifm", "bandcamp": "https://gigifm.bandcamp.com", "instagram": "https://www.instagram.com/gigifm/", "applemusic": "https://music.apple.com/us/artist/gigi-fm/1605657044"},
        "stats": {"performanceCount": 12, "firstPlayed": "2022-06-25"},
    },
    "inox-traxx": {
        "name": "Inox Traxx",
        "tags": ["Techno"],
        "blurb": "Rising techno producer with a distinctive, unmistakable sound, releasing on Ostgut Ton and a Berghain regular.",
        "bio": "Inox Traxx has risen quickly in the techno scene over the past few years, carving out a signature sound that's unmistakably her own. She has released on labels including Ostgut Ton, Somov, WSNWG, and KNTXT, and makes regular appearances at Berghain, cementing her position as an artist to watch.",
        "links": {"soundcloud": "https://soundcloud.com/inoxtraxx", "bandcamp": "https://inoxtraxx.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/inox-traxx/1486314931"},
        "stats": {"performanceCount": 14, "firstPlayed": "2022-10-01"},
    },
    "isabel-soto": {
        "name": "Isabel Soto",
        "tags": ["Techno"],
        "blurb": "Techno DJ and producer, founder of the Nyxii Records label.",
        "bio": "Isabel Soto is a techno DJ and producer, and founder of the Nyxii Records label. She has become a regular presence at Berghain's Klubnacht since 2024, with her productions distributed digitally including via Bandcamp and Apple Music.",
        "links": {"soundcloud": "https://soundcloud.com/isabelsoto", "bandcamp": "https://isabelsoto.bandcamp.com", "instagram": "https://www.instagram.com/isabelsoto/", "applemusic": "https://music.apple.com/us/artist/isabel-soto/1629622792"},
        "stats": {"performanceCount": 11, "firstPlayed": "2024-03-16"},
    },
    "jakojako": {
        "name": "JakoJako",
        "tags": ["Techno", "Electronic"],
        "blurb": "Berlin-based Berghain resident building hypnotic, modular-synth-driven live techno sets.",
        "bio": "JakoJako is a Berlin-based techno producer and current Berghain resident known for live modular synthesis performances. She got her start through sound manipulation and DIY synthesizers, and in 2017 began working at Schneidersladen, Berlin's renowned synth shop, educating musicians on synthesis. Her releases include the Verve EP, Segmente EP, and Tết 41, and her work spans Berghain, MUTE, and Leisure System.",
        "links": {"soundcloud": "https://soundcloud.com/jakojako_live", "bandcamp": "https://jakojako.bandcamp.com", "instagram": "https://www.instagram.com/jakojako_live/", "applemusic": "https://music.apple.com/us/artist/jakojako/1269610965"},
        "stats": {"performanceCount": 32, "firstPlayed": "2021-11-13", "isResident": True},
    },
    "luke-slater": {
        "name": "Luke Slater",
        "tags": ["Techno", "Electronic"],
        "blurb": "UK techno pioneer and torchbearer for the Detroit sound since the early '90s, also known as Planetary Assault Systems.",
        "bio": "Luke Slater (born 1968, Reading, England) is a prolific UK techno producer and DJ recording under multiple aliases, most notably Planetary Assault Systems and L.B. Dub Corp. He debuted on vinyl in 1989 and became known as the UK torchbearer for the Detroit techno sound, breaking through in the '90s with tracks like 'Love' and 'All Exhale' via Peacefrog Records. In 2006 he launched his own label, Mote-Evolver, and has remained a fixture at clubs including Fabric, Nitsa, and Berghain.",
        "links": {"soundcloud": "https://soundcloud.com/luke-slater", "instagram": "https://www.instagram.com/lukeslater/", "applemusic": "https://music.apple.com/us/artist/luke-slater/32314650"},
        "stats": {"performanceCount": 86, "firstPlayed": "2005-04-09", "isResident": True},
    },
    "quelza": {
        "name": "Quelza",
        "tags": ["Techno", "Breakbeat"],
        "blurb": "French producer crafting hypnotic, soul-summoning techno and cantankerous breakbeats.",
        "bio": "Quelza, aka Léo Naïtaïssa, is a French producer and DJ who emerged in Berlin's music scene and has since become an in-demand name on the international club circuit. His productions and sets mine hypnotic, soul-summoning techno alongside cantankerous breakbeats.",
        "links": {"soundcloud": "https://soundcloud.com/quelza", "bandcamp": "https://quelza.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/quelza/1464174707"},
        "stats": {"performanceCount": 24, "firstPlayed": "2022-09-24", "isResident": True},
    },
    "cinthie": {
        "name": "Cinthie",
        "tags": ["House", "Disco", "Techno"],
        "blurb": "Berlin house selector and label boss serving classic Chicago/NYC-rooted, disco-inflected house.",
        "bio": "Cinthie is a Berlin-based DJ, producer and label owner who has been active in house music since the early 1990s. She co-founded the Beste Modus collective, runs 803 Crystal Grooves/Collective Cuts and the Elevate record store, and released her debut album on Will Saul's Aus imprint in 2020. She tours internationally, from Paris and London to Seoul and Osaka.",
        "links": {"soundcloud": "https://soundcloud.com/cinthie", "bandcamp": "https://cinthie.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/cinthie/525782272"},
        "stats": {"performanceCount": 19, "firstPlayed": "2021-10-30"},
    },
    "marcel-dettmann": {
        "name": "Marcel Dettmann",
        "tags": ["Techno", "Industrial Techno"],
        "blurb": "Berghain's signature dark, hypnotic, industrial-tinged techno stylist.",
        "bio": "Marcel Dettmann is a German DJ, producer and label owner, born in 1977 in Pößneck, Thuringia. A Berghain resident and former staffer at Berlin's Hard Wax record store (2002-2012), he has been a defining force behind the club's austere, driving techno sound since the mid-2000s, releasing through Ostgut Ton and his own label, MDR.",
        "links": {"soundcloud": "https://soundcloud.com/marceldettmann", "bandcamp": "https://marceldettmann.bandcamp.com", "instagram": "https://instagram.com/marceldettmann"},
        "stats": {"performanceCount": 202, "firstPlayed": "2004-12-18", "isResident": True},
    },
    "fiedel": {
        "name": "Fiedel",
        "tags": ["Techno", "House", "Electro"],
        "blurb": "Longtime Berghain resident known as a tastemaking crate-digger across techno, house and electro.",
        "bio": "Fiedel (Michael Fiedler) is a Berlin-based DJ and longtime Berghain resident, celebrated for building surprising, groove-driven sets that move between techno, house, acid and electro-funk. He is also one half of the duo MMM with Errorsmith, releasing on Ostgut Ton and related imprints.",
        "links": {"soundcloud": "https://soundcloud.com/fiedel", "bandcamp": "https://fiedel.bandcamp.com", "instagram": "https://instagram.com/fiedel.official", "applemusic": "https://music.apple.com/us/artist/fiedel/266845665"},
        "stats": {"performanceCount": 188, "firstPlayed": "2004-12-31", "isResident": True},
    },
    "gallegos": {
        "name": "Gallegos",
        "tags": ["House", "Broken Beat", "Garage"],
        "blurb": "UK house producer serving jazzy, soulful grooves with a broken-beat backbone.",
        "bio": "Gallegos is a UK-based (Bristol) house DJ and producer known for jazz-inflected, soulful house and broken-beat productions, releasing via labels including Banoffee Pies and Room Service Recordings. He discovered turntablism as a child after watching the documentary Scratch, and has built an international following alongside scene peers like Soulphiction and Brawther.",
        "links": {"soundcloud": "https://soundcloud.com/gallegos_1991", "bandcamp": "https://gallegos.bandcamp.com", "spotify": "https://open.spotify.com/artist/7hmArnXZVkRgobbxJBLJMF", "instagram": "https://instagram.com/gallegos_1991", "applemusic": "https://music.apple.com/us/artist/gallegos/41251381"},
        "stats": {"performanceCount": 11, "firstPlayed": "2022-10-15"},
    },
    "gerd-janson": {
        "name": "Gerd Janson",
        "tags": ["House", "Disco", "Techno"],
        "blurb": "Running Back label boss reframing house and disco classics with an eclectic, playful touch.",
        "bio": "Gerd Janson is a Frankfurt-based DJ and founder of the Running Back label, which he established in 2002. Long associated with Frankfurt's Robert Johnson club through its Liquid night, he is regarded as one of house and techno's most respected selectors for his genre-spanning, unexpected reworkings of classic material.",
        "links": {"soundcloud": "https://soundcloud.com/gerdjanson", "bandcamp": "https://gerdjanson.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/gerd-janson/456981573"},
        "stats": {"performanceCount": 89, "firstPlayed": "2010-04-03", "isResident": True},
    },
    "lakuti": {
        "name": "Lakuti",
        "tags": ["House", "Techno", "Soul/Funk"],
        "blurb": "Soweto-born selector weaving soulful house, jazz and Chicago/Detroit influences into purposeful sets.",
        "bio": "Lakuti (Lerato Khathi) is a South African-born, Berlin-based DJ, producer and Panorama Bar resident. She founded Uzuri Recordings and the Uzuri Artist Agency, and has spent decades championing Black artists and inclusive spaces in electronic music through genre-fluid sets rooted in soul, funk, jazz and Chicago house.",
        "links": {"soundcloud": "https://soundcloud.com/lakuti", "instagram": "https://instagram.com/lakuti_"},
        "stats": {"performanceCount": 30, "firstPlayed": "2012-12-15"},
    },
    "nd-baumecker": {
        "name": "nd_baumecker",
        "tags": ["House", "Minimal House", "Deep House"],
        "blurb": "Longtime Panorama Bar resident and former booker spinning minimal, groove-focused deep house.",
        "bio": "Andreas 'nd_baumecker' Baumecker is a Berlin-based DJ and former in-house booker at Panorama Bar, a resident since the venue's OstGut days. He is also one half of the production duo Barker & Baumecker (with Sam Barker), with releases on Ostgut Ton, and runs the Freundinnen Audio label.",
        "links": {"soundcloud": "https://soundcloud.com/ndbaumecker", "instagram": "https://instagram.com/nd_baumecker", "bandcamp": "https://barkerbaumecker.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/nd-baumecker/922879880"},
        "stats": {"performanceCount": 196, "firstPlayed": "2004-12-31", "isResident": True},
    },
    "nick-hoppner": {
        "name": "Nick Höppner",
        "tags": ["House", "Minimal", "Electro"],
        "blurb": "Former Ostgut Ton label manager crafting refined house shaded with alt-pop and IDM textures.",
        "bio": "Nick Höppner is a Berlin-based DJ and producer, and a former Panorama Bar resident who managed the Ostgut Ton label from 2005 to 2012 before turning to production full-time. His solo albums, including Work, blend house music with alt-pop and IDM influences across ambient and dancefloor-oriented material alike.",
        "links": {"soundcloud": "https://soundcloud.com/nick-hoeppner", "bandcamp": "https://nickhoeppner.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/nick-h%C3%B6ppner/155889976"},
        "stats": {"performanceCount": 171, "firstPlayed": "2004-12-31"},
    },
    "steffi": {
        "name": "Steffi",
        "tags": ["Techno", "House", "Electro"],
        "blurb": "Dutch-born Berghain resident moving from warm, atmospheric house into intricate electro-techno.",
        "bio": "Steffi (Steffi Doms) is a Dutch DJ, producer and label owner (Klakson, Dolly) and a longtime Berghain/Panorama Bar resident since the mid-2000s. Her productions have evolved from warm, atmospheric techno-house into a more complex, intricate electro-techno sound, released via Ostgut Ton and her own imprints.",
        "links": {"instagram": "https://instagram.com/steffi_dolly_klakson/", "bandcamp": "https://steffiedoms.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/steffi/29056576"},
        "stats": {"performanceCount": 158, "firstPlayed": "2005-11-12", "isResident": True},
    },
    "tama-sumo": {
        "name": "Tama Sumo",
        "tags": ["House", "Techno", "Disco"],
        "blurb": "Panorama Bar resident since 2004 weaving house, techno, disco and Afrobeat into genre-fluid journeys.",
        "bio": "Tama Sumo (Kerstin Egert) is a German DJ and Panorama Bar/Berghain resident, having played the gay/lesbian 'Dance with the Aliens' parties at the old OstGut from 2001 before becoming a resident at the new club at the end of 2004. Renowned for masterfully blending house, techno, disco and Afrobeat, she records for Ostgut Ton, often alongside close collaborator Lakuti.",
        "links": {"soundcloud": "https://soundcloud.com/tama-sumo", "applemusic": "https://music.apple.com/us/artist/tama-sumo/309708179"},
        "stats": {"performanceCount": 148, "firstPlayed": "2005-02-26"},
    },
    "virginia": {
        "name": "Virginia",
        "tags": ["House", "Techno", "Vocal House"],
        "blurb": "Brazilian-heritage, Berlin-based Panorama Bar resident blending minimal house/techno with her own vocals.",
        "bio": "Virginia is a DJ, singer, songwriter and producer of Brazilian heritage based in Berlin, and a Panorama Bar resident since 2012. Signed to Ostgut Ton, her productions merge minimal house and techno with her own singing, as showcased on her debut full-length exploring themes of love, lust and life.",
        "links": {"soundcloud": "https://soundcloud.com/virginia-dj", "bandcamp": "https://virginia-dj.bandcamp.com", "applemusic": "https://music.apple.com/us/artist/virginia/1569823236"},
        "stats": {"performanceCount": 111, "firstPlayed": "2011-08-27", "isResident": True},
    },
}

NEW_DAYS = [
    {
        "date": "2026-08-06", "weekday": "THU", "event": "SÄULE",
        "rooms": [{"room": "Säule", "djSlugs": ["rami-abi-rafi", "conceptual-live", "ayesha"]}],
    },
    {
        "date": "2026-08-07", "weekday": "FRI", "event": "Kynant",
        "rooms": [{"room": "Panorama Bar", "djSlugs": ["tikiman", "parallel-9", "richard-akingbehin", "aurora-halal", "laura-bcr"]}],
    },
    {
        "date": "2026-08-08", "weekday": "SAT", "event": "Ostgut Ton Klubnacht",
        "rooms": [
            {"room": "Berghain", "djSlugs": ["altinbas-live", "fadi-mohem-live", "claudio-prc", "efdemin", "gigi-fm", "inox-traxx", "isabel-soto", "jakojako", "luke-slater", "quelza"]},
            {"room": "Panorama Bar", "djSlugs": ["cinthie", "fiedel", "gallegos", "gerd-janson", "lakuti", "marcel-dettmann", "nd-baumecker", "nick-hoppner", "steffi", "tama-sumo", "virginia"]},
        ],
    },
]


def main():
    data = json.loads(DATA_PATH.read_text())

    for slug, profile in NEW_DJS.items():
        assert slug not in data["djs"], f"{slug} already exists"
        profile["appearances"] = []
        data["djs"][slug] = profile

    for day in NEW_DAYS:
        assert day["date"] not in [d["date"] for d in data["days"]], f"{day['date']} already archived"
        for room in day["rooms"]:
            for slug in room["djSlugs"]:
                data["djs"][slug]["appearances"].append({
                    "date": day["date"], "event": day["event"], "room": room["room"],
                })
        data["days"].append(day)

    data["days"].sort(key=lambda d: d["date"])

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Added {len(NEW_DJS)} DJ profiles and {len(NEW_DAYS)} days")


if __name__ == "__main__":
    main()
