# DJ avatar photo credits

Only DJs with a confidently-identified, freely-licensed photo get a real
avatar image; everyone else falls back to an initials tile in the page
(rendered at runtime, no image needed). Found via Wikimedia Commons and
Openverse (CC-licensed image search across Flickr/Wikimedia/etc.), same
standard used for the carousel banner: real license, real identity match,
otherwise skip rather than guess.

- **andre_galluzzi.jpg** — "Andre Galluzzi Magdeburg 2009 043" by Tim (Schönebeck, Germany),
  CC BY-SA 2.0, via Wikimedia Commons. Caption: "André Galluzzi DJing at
  Alte Diamantbrauerei, Magdeburg."
  Source: https://commons.wikimedia.org/wiki/File:Andre_Galluzzi_Magdeburg_2009_043_(3626784378).jpg

- **headhunter.jpg** — "HEADHUNTER aka ADDISON GROOVE" by basic_sounds (Flickr),
  CC BY-SA 2.0. Tagged from Decibel Festival (Seattle). Title explicitly
  names both aliases, matching our researched identity (Antony "Tony"
  Williams, Bristol producer, performs as both Headhunter and Addison Groove).
  Source: https://www.flickr.com/photos/84642407@N00/5065784583

All other 23 entries in data/lineup.json have no `photo` field — searched
via Wikipedia, Wikimedia Commons full-text search, and Openverse (multiple
query variants per artist, including real names where known) and found no
confident, freely-licensed match. This lineup skews underground/regional,
so most artists simply aren't the subject of any CC-licensed photography
online. The page renders an initials avatar for these automatically.
