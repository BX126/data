from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "static" / "assets" / "real"
OUT_PATH = ROOT / "data" / "extra_scenes.json"
USER_AGENT = "VibeMatchLocalPrototype/0.2 (local research prototype; no public redistribution)"
TARGET_EXTRA = 96

SOURCE_NOTE = (
    "Title, year, director, and image source are grounded in Wikipedia/Wikimedia page data "
    "and manual prototype review. Mood/style/story tags are curated for vibe search and should "
    "be replaced or weighted with MovieNet, LIRIS-ACCEDE, MovieGraphs, MovieLens, or MPST labels later."
)

WIKIPEDIA = {"name": "Wikipedia", "url": "https://www.wikipedia.org/", "fields": ["title", "year", "director", "image"]}
WIKIMEDIA = {"name": "Wikipedia/Wikimedia page image", "url": "https://www.wikipedia.org/", "fields": ["image"]}
CURATION = {"name": "Manual expansion curation", "url": "/readme.md", "fields": ["mood", "style", "story", "palette", "data_tags", "prompt"]}

CATALOG = [
    ("parasite-house-tension", "Parasite (2019 film)", "Parasite", 2019, "Bong Joon-ho", "Cinematic", "satirical thriller", "class tension", "modern house"),
    ("moonlight-blue-memory", "Moonlight (2016 film)", "Moonlight", 2016, "Barry Jenkins", "Cinematic", "tender melancholic", "identity", "blue night"),
    ("lost-in-translation-hotel", "Lost in Translation (film)", "Lost in Translation", 2003, "Sofia Coppola", "Cinematic", "lonely intimate", "hotel connection", "neon city"),
    ("eternal-sunshine-memory", "Eternal Sunshine of the Spotless Mind", "Eternal Sunshine of the Spotless Mind", 2004, "Michel Gondry", "Cinematic", "surreal bittersweet", "memory breakup", "winter beach"),
    ("arrival-fog-language", "Arrival (film)", "Arrival", 2016, "Denis Villeneuve", "Cinematic", "awe solemn", "first contact", "mist gray"),
    ("interstellar-cosmic-family", "Interstellar (film)", "Interstellar", 2014, "Christopher Nolan", "Cinematic", "epic emotional", "family time", "space black"),
    ("mad-max-fury-road-chase", "Mad Max: Fury Road", "Mad Max: Fury Road", 2015, "George Miller", "Cinematic", "furious kinetic", "desert chase", "orange dust"),
    ("the-matrix-green-choice", "The Matrix", "The Matrix", 1999, "The Wachowskis", "Cinematic", "cool paranoid", "reality choice", "green black"),
    ("pulp-fiction-neon-diner", "Pulp Fiction", "Pulp Fiction", 1994, "Quentin Tarantino", "Cinematic", "cool volatile", "crime coincidence", "yellow black"),
    ("goodfellas-night-energy", "Goodfellas", "Goodfellas", 1990, "Martin Scorsese", "Cinematic", "restless dangerous", "criminal rise", "night red"),
    ("taxi-driver-street-alienation", "Taxi Driver", "Taxi Driver", 1976, "Martin Scorsese", "Cinematic", "alienated gritty", "urban isolation", "yellow neon"),
    ("fight-club-basement-chaos", "Fight Club", "Fight Club", 1999, "David Fincher", "Cinematic", "raw nihilistic", "identity revolt", "sickly green"),
    ("se7en-rain-investigation", "Seven (1995 film)", "Seven", 1995, "David Fincher", "Cinematic", "bleak tense", "murder investigation", "rain gray"),
    ("zodiac-paper-obsession", "Zodiac (film)", "Zodiac", 2007, "David Fincher", "Cinematic", "obsessive procedural", "unsolved mystery", "paper beige"),
    ("social-network-blue-ambition", "The Social Network", "The Social Network", 2010, "David Fincher", "Cinematic", "cold ambitious", "friendship fracture", "blue amber"),
    ("whiplash-stage-pressure", "Whiplash (2014 film)", "Whiplash", 2014, "Damien Chazelle", "Cinematic", "intense obsessive", "mentor conflict", "gold black"),
    ("la-la-land-dream-dance", "La La Land", "La La Land", 2016, "Damien Chazelle", "Cinematic", "romantic dreamy", "ambition romance", "purple gold"),
    ("the-lighthouse-storm-madness", "The Lighthouse (2019 film)", "The Lighthouse", 2019, "Robert Eggers", "Cinematic", "claustrophobic uncanny", "isolation madness", "black white"),
    ("the-witch-forest-dread", "The Witch (2015 film)", "The Witch", 2015, "Robert Eggers", "Cinematic", "austere dreadful", "family paranoia", "forest brown"),
    ("midsommar-daylight-horror", "Midsommar", "Midsommar", 2019, "Ari Aster", "Cinematic", "bright unsettling", "ritual grief", "white floral"),
    ("get-out-suburban-dread", "Get Out", "Get Out", 2017, "Jordan Peele", "Cinematic", "uneasy satirical", "social horror", "suburban green"),
    ("nope-sky-spectacle", "Nope (film)", "Nope", 2022, "Jordan Peele", "Cinematic", "awe ominous", "spectacle survival", "sky blue"),
    ("ex-machina-glass-control", "Ex Machina (film)", "Ex Machina", 2014, "Alex Garland", "Cinematic", "clinical tense", "ai manipulation", "glass green"),
    ("annihilation-biological-dream", "Annihilation (film)", "Annihilation", 2018, "Alex Garland", "Cinematic", "surreal eerie", "mutation journey", "iridescent forest"),
    ("children-of-men-long-take", "Children of Men", "Children of Men", 2006, "Alfonso Cuaron", "Cinematic", "desperate urgent", "hope survival", "war gray"),
    ("roma-domestic-memory", "Roma (2018 film)", "Roma", 2018, "Alfonso Cuaron", "Cinematic", "quiet observant", "domestic memory", "black white"),
    ("gravity-space-survival", "Gravity (2013 film)", "Gravity", 2013, "Alfonso Cuaron", "Cinematic", "isolated suspenseful", "space survival", "earth blue"),
    ("birdman-theater-frenzy", "Birdman (film)", "Birdman", 2014, "Alejandro G. Inarritu", "Cinematic", "anxious theatrical", "ego collapse", "backstage amber"),
    ("revenant-winter-revenge", "The Revenant (2015 film)", "The Revenant", 2015, "Alejandro G. Inarritu", "Cinematic", "brutal elemental", "revenge survival", "snow gray"),
    ("tree-of-life-cosmic-childhood", "The Tree of Life (film)", "The Tree of Life", 2011, "Terrence Malick", "Cinematic", "spiritual lyrical", "childhood grace", "sun green"),
    ("thin-red-line-war-reverie", "The Thin Red Line (1998 film)", "The Thin Red Line", 1998, "Terrence Malick", "Cinematic", "poetic haunted", "war nature", "jungle green"),
    ("portrait-lady-fire-coastal", "Portrait of a Lady on Fire", "Portrait of a Lady on Fire", 2019, "Celine Sciamma", "Painting", "restrained romantic", "forbidden portrait", "sea blue"),
    ("blue-is-warmest-intimacy", "Blue Is the Warmest Colour", "Blue Is the Warmest Colour", 2013, "Abdellatif Kechiche", "Cinematic", "intimate yearning", "first love", "blue warm"),
    ("call-me-by-your-name-summer", "Call Me by Your Name (film)", "Call Me by Your Name", 2017, "Luca Guadagnino", "Cinematic", "sensual nostalgic", "summer desire", "peach green"),
    ("lady-bird-sacramento", "Lady Bird (film)", "Lady Bird", 2017, "Greta Gerwig", "Cinematic", "restless tender", "mother daughter", "warm suburban"),
    ("frances-ha-friendship", "Frances Ha", "Frances Ha", 2012, "Noah Baumbach", "Cinematic", "awkward hopeful", "friendship drift", "black white"),
    ("marriage-story-apartment", "Marriage Story", "Marriage Story", 2019, "Noah Baumbach", "Cinematic", "raw intimate", "divorce family", "neutral apartment"),
    ("the-favourite-palace-games", "The Favourite", "The Favourite", 2018, "Yorgos Lanthimos", "Cinematic", "acid comic", "court rivalry", "candle palace"),
    ("poor-things-surreal-voyage", "Poor Things (film)", "Poor Things", 2023, "Yorgos Lanthimos", "Cinematic", "surreal liberated", "self invention", "candy color"),
    ("everything-everywhere-chaos", "Everything Everywhere All at Once", "Everything Everywhere All at Once", 2022, "Daniel Kwan and Daniel Scheinert", "Cinematic", "chaotic heartfelt", "multiverse family", "rainbow neon"),
    ("past-lives-city-memory", "Past Lives (film)", "Past Lives", 2023, "Celine Song", "Cinematic", "quiet wistful", "missed connection", "city blue"),
    ("aftersun-pool-memory", "Aftersun", "Aftersun", 2022, "Charlotte Wells", "Cinematic", "tender haunted", "father daughter memory", "sun washed"),
    ("drive-neon-silence", "Drive (2011 film)", "Drive", 2011, "Nicolas Winding Refn", "Cinematic", "cool lonely", "criminal romance", "pink neon"),
    ("nightcrawler-late-night-hunger", "Nightcrawler (film)", "Nightcrawler", 2014, "Dan Gilroy", "Cinematic", "predatory nocturnal", "media ambition", "sodium night"),
    ("uncut-gems-diamond-anxiety", "Uncut Gems", "Uncut Gems", 2019, "Josh Safdie and Benny Safdie", "Cinematic", "anxious frantic", "gambling spiral", "jewel neon"),
    ("the-batman-rain-noir", "The Batman (film)", "The Batman", 2022, "Matt Reeves", "Cinematic", "rainy brooding", "detective vengeance", "red black"),
    ("joker-staircase-alienation", "Joker (2019 film)", "Joker", 2019, "Todd Phillips", "Cinematic", "unstable lonely", "social collapse", "green red"),
    ("dune-desert-prophecy", "Dune (2021 film)", "Dune", 2021, "Denis Villeneuve", "Cinematic", "monumental mystical", "desert prophecy", "sand black"),
    ("dune-part-two-war-vision", "Dune: Part Two", "Dune: Part Two", 2024, "Denis Villeneuve", "Cinematic", "epic severe", "holy war", "sand orange"),
    ("oppenheimer-fire-ethics", "Oppenheimer (film)", "Oppenheimer", 2023, "Christopher Nolan", "Cinematic", "grave explosive", "scientific guilt", "fire black"),
    ("tenet-time-inversion", "Tenet (film)", "Tenet", 2020, "Christopher Nolan", "Cinematic", "cool intricate", "time espionage", "steel blue"),
    ("barbie-plastic-crisis", "Barbie (film)", "Barbie", 2023, "Greta Gerwig", "Cinematic", "bright existential", "identity comedy", "pink cyan"),
    ("jojo-rabbit-childhood-war", "Jojo Rabbit", "Jojo Rabbit", 2019, "Taika Waititi", "Cinematic", "comic tragic", "childhood propaganda", "pastel war"),
    ("the-shape-of-water-lab-romance", "The Shape of Water", "The Shape of Water", 2017, "Guillermo del Toro", "Cinematic", "romantic aquatic", "outsider love", "teal green"),
    ("crimson-peak-gothic-red", "Crimson Peak", "Crimson Peak", 2015, "Guillermo del Toro", "Cinematic", "gothic lush", "haunted romance", "red snow"),
    ("nightmare-alley-carnival", "Nightmare Alley (2021 film)", "Nightmare Alley", 2021, "Guillermo del Toro", "Cinematic", "noir doomed", "con artistry", "carnival amber"),
    ("moulin-rouge-stage-romance", "Moulin Rouge!", "Moulin Rouge!", 2001, "Baz Luhrmann", "Cinematic", "maximal romantic", "stage tragedy", "red gold"),
    ("romeo-juliet-aquarium", "Romeo + Juliet", "Romeo + Juliet", 1996, "Baz Luhrmann", "Cinematic", "youthful feverish", "doomed love", "neon blue"),
    ("amelia-earhart-sky", "The Aviator (2004 film)", "The Aviator", 2004, "Martin Scorsese", "Cinematic", "glamorous obsessive", "flight ambition", "cyan gold"),
    ("casino-velvet-power", "Casino (1995 film)", "Casino", 1995, "Martin Scorsese", "Cinematic", "glittering dangerous", "empire decay", "casino red"),
    ("spirited-away", "Howl's Moving Castle (film)", "Howl's Moving Castle", 2004, "Hayao Miyazaki", "Anime", "magical romantic", "curse refuge", "pastel sky"),
    ("my-neighbor-totoro-rain", "My Neighbor Totoro", "My Neighbor Totoro", 1988, "Hayao Miyazaki", "Anime", "gentle wondrous", "childhood nature", "forest green"),
    ("princess-mononoke-forest-war", "Princess Mononoke", "Princess Mononoke", 1997, "Hayao Miyazaki", "Anime", "mythic fierce", "nature war", "forest blood"),
    ("nausicaa-toxic-jungle", "Nausicaa of the Valley of the Wind (film)", "Nausicaa of the Valley of the Wind", 1984, "Hayao Miyazaki", "Anime", "ecological epic", "toxic prophecy", "blue green"),
    ("castle-in-the-sky-clouds", "Castle in the Sky", "Castle in the Sky", 1986, "Hayao Miyazaki", "Anime", "adventurous airy", "lost civilization", "sky blue"),
    ("kikis-delivery-seaside", "Kiki's Delivery Service", "Kiki's Delivery Service", 1989, "Hayao Miyazaki", "Anime", "cozy independent", "coming of age", "seaside red"),
    ("ponyo-ocean-child", "Ponyo", "Ponyo", 2008, "Hayao Miyazaki", "Anime", "playful oceanic", "child magic", "sea blue"),
    ("grave-fireflies-war-grief", "Grave of the Fireflies", "Grave of the Fireflies", 1988, "Isao Takahata", "Anime", "devastating tender", "war siblings", "firefly orange"),
    ("only-yesterday-memory", "Only Yesterday (1991 film)", "Only Yesterday", 1991, "Isao Takahata", "Anime", "nostalgic pastoral", "adult memory", "field green"),
    ("wolf-children-family-nature", "Wolf Children", "Wolf Children", 2012, "Mamoru Hosoda", "Anime", "warm bittersweet", "single parent", "mountain green"),
    ("your-name-comet-longing", "Your Name", "Your Name", 2016, "Makoto Shinkai", "Anime", "romantic cosmic", "body swap fate", "twilight purple"),
    ("weathering-with-you-rain", "Weathering with You", "Weathering with You", 2019, "Makoto Shinkai", "Anime", "rainy yearning", "weather miracle", "rain blue"),
    ("suzume-doorway", "Suzume", "Suzume", 2022, "Makoto Shinkai", "Anime", "adventurous mournful", "disaster doors", "sunset blue"),
    ("akira-neon-mutation", "Akira (1988 film)", "Akira", 1988, "Katsuhiro Otomo", "Anime", "explosive cyberpunk", "mutation rebellion", "red neon"),
    ("ghost-shell-city-rain", "Ghost in the Shell (1995 film)", "Ghost in the Shell", 1995, "Mamoru Oshii", "Anime", "philosophical cyberpunk", "identity network", "rain teal"),
    ("perfect-blue-pop-psychosis", "Perfect Blue", "Perfect Blue", 1997, "Satoshi Kon", "Anime", "paranoid fractured", "celebrity identity", "stage blue"),
    ("paprika-dream-parade", "Paprika (2006 film)", "Paprika", 2006, "Satoshi Kon", "Anime", "surreal vibrant", "dream invasion", "rainbow red"),
    ("tokyo-godfathers-winter", "Tokyo Godfathers", "Tokyo Godfathers", 2003, "Satoshi Kon", "Anime", "comic heartfelt", "found family", "winter city"),
    ("redline-racing-chaos", "Redline (2009 film)", "Redline", 2009, "Takeshi Koike", "Anime", "kinetic wild", "racing spectacle", "red black"),
    ("into-spider-verse-comic-city", "Spider-Man: Into the Spider-Verse", "Spider-Man: Into the Spider-Verse", 2018, "Bob Persichetti, Peter Ramsey, and Rodney Rothman", "Cartoon", "electric heartfelt", "multiverse hero", "comic neon"),
    ("across-spider-verse-collage", "Spider-Man: Across the Spider-Verse", "Spider-Man: Across the Spider-Verse", 2023, "Joaquim Dos Santos, Kemp Powers, and Justin K. Thompson", "Cartoon", "collage kinetic", "identity destiny", "ink neon"),
    ("toy-story-bedroom", "Toy Story", "Toy Story", 1995, "John Lasseter", "3D", "playful nostalgic", "friendship jealousy", "primary colors"),
    ("toy-story-3-incinerator", "Toy Story 3", "Toy Story 3", 2010, "Lee Unkrich", "3D", "emotional adventurous", "letting go", "warm plastic"),
    ("finding-nemo-ocean", "Finding Nemo", "Finding Nemo", 2003, "Andrew Stanton", "3D", "bright anxious", "parent search", "ocean blue"),
    ("inside-out-headquarters", "Inside Out (2015 film)", "Inside Out", 2015, "Pete Docter", "3D", "colorful emotional", "inner feelings", "memory glow"),
    ("soul-jazz-afterlife", "Soul (2020 film)", "Soul", 2020, "Pete Docter", "3D", "spiritual warm", "life purpose", "jazz blue"),
    ("coco-marigold-bridge", "Coco (2017 film)", "Coco", 2017, "Lee Unkrich", "3D", "familial festive", "ancestor memory", "marigold orange"),
    ("up-balloon-house", "Up (2009 film)", "Up", 2009, "Pete Docter", "3D", "bittersweet adventurous", "grief adventure", "sky balloons"),
    ("ratatouille-kitchen", "Ratatouille (film)", "Ratatouille", 2007, "Brad Bird", "3D", "warm culinary", "hidden talent", "kitchen gold"),
    ("incredibles-family-action", "The Incredibles", "The Incredibles", 2004, "Brad Bird", "3D", "retro heroic", "family teamwork", "red black"),
    ("iron-giant-forest-friend", "The Iron Giant", "The Iron Giant", 1999, "Brad Bird", "Cartoon", "gentle heroic", "child robot friendship", "autumn gray"),
    ("giant-robot-city", "The Lego Movie", "The Lego Movie", 2014, "Phil Lord and Christopher Miller", "3D", "comic energetic", "ordinary hero", "plastic rainbow"),
    ("mitchells-machines-family-road", "The Mitchells vs. the Machines", "The Mitchells vs. the Machines", 2021, "Mike Rianda", "Cartoon", "chaotic warm", "family roadtrip", "pop neon"),
    ("puss-boots-last-wish", "Puss in Boots: The Last Wish", "Puss in Boots: The Last Wish", 2022, "Joel Crawford", "Cartoon", "storybook adventurous", "mortality chase", "painted gold"),
    ("shrek-swamp-fairy-tale", "Shrek", "Shrek", 2001, "Andrew Adamson and Vicky Jenson", "3D", "comic irreverent", "fairy tale reversal", "swamp green"),
    ("kung-fu-panda-training", "Kung Fu Panda", "Kung Fu Panda", 2008, "John Stevenson and Mark Osborne", "3D", "comic inspirational", "training destiny", "jade gold"),
    ("dragon-flight-friendship", "How to Train Your Dragon (film)", "How to Train Your Dragon", 2010, "Chris Sanders and Dean DeBlois", "3D", "soaring tender", "trust flight", "sky sea"),
    ("nightmare-before-christmas-town", "The Nightmare Before Christmas", "The Nightmare Before Christmas", 1993, "Henry Selick", "Cartoon", "gothic whimsical", "holiday identity", "black orange"),
    ("fantastic-mr-fox-autumn", "Fantastic Mr. Fox (film)", "Fantastic Mr. Fox", 2009, "Wes Anderson", "Cartoon", "dry warm", "family caper", "autumn orange"),
    ("isle-of-dogs-trash-island", "Isle of Dogs (film)", "Isle of Dogs", 2018, "Wes Anderson", "Cartoon", "deadpan loyal", "rescue mission", "dust red"),
    ("anomalisa-hotel", "Anomalisa", "Anomalisa", 2015, "Charlie Kaufman and Duke Johnson", "Cartoon", "lonely uncanny", "hotel connection", "beige red"),
    ("mary-max-letters", "Mary and Max", "Mary and Max", 2009, "Adam Elliot", "Cartoon", "melancholic tender", "letter friendship", "sepia gray"),
    ("song-sea-selkie", "Song of the Sea (2014 film)", "Song of the Sea", 2014, "Tomm Moore", "Illustration", "mythic gentle", "sibling folklore", "sea teal"),
    ("wolfwalkers-forest-girl", "Wolfwalkers", "Wolfwalkers", 2020, "Tomm Moore and Ross Stewart", "Illustration", "wild luminous", "forest freedom", "green orange"),
    ("secret-kells-illumination", "The Secret of Kells", "The Secret of Kells", 2009, "Tomm Moore and Nora Twomey", "Illustration", "sacred adventurous", "manuscript magic", "ink green"),
    ("breadwinner-story", "The Breadwinner (film)", "The Breadwinner", 2017, "Nora Twomey", "Illustration", "brave intimate", "survival storytelling", "sand blue"),
    ("loving-vincent-painted", "Loving Vincent", "Loving Vincent", 2017, "Dorota Kobiela and Hugh Welchman", "Painting", "restless painterly", "artist mystery", "oil blue"),
    ("waking-life-dream-talk", "Waking Life", "Waking Life", 2001, "Richard Linklater", "Drawing", "philosophical drifting", "dream conversations", "rotoscope color"),
    ("scanner-darkly-paranoia", "A Scanner Darkly (film)", "A Scanner Darkly", 2006, "Richard Linklater", "Drawing", "paranoid unstable", "identity surveillance", "rotoscope dark"),
    ("persepolis-revolution-memory", "Persepolis (film)", "Persepolis", 2007, "Marjane Satrapi and Vincent Paronnaud", "Drawing", "bold autobiographical", "revolution growing up", "black white"),
    ("waltz-bashir-memory-war", "Waltz with Bashir", "Waltz with Bashir", 2008, "Ari Folman", "Drawing", "haunted political", "war memory", "yellow black"),
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fetch_summary(page_title: str) -> dict:
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(page_title.replace(" ", "_"), safe=":_()'")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        path.write_bytes(response.read())


def vibe_fields(mood: str, story: str, palette: str, medium: str, title: str) -> dict:
    mood_tags = mood.split()
    story_tags = story.split()
    palette_tags = palette.split()
    style_map = {
        "Cinematic": ["cinematic", "composed lighting", "visual storytelling"],
        "Anime": ["anime", "drawn motion", "expressive color"],
        "Cartoon": ["stylized animation", "bold shapes", "expressive staging"],
        "3D": ["3D animation", "polished lighting", "character staging"],
        "Drawing": ["drawn texture", "graphic line", "expressive abstraction"],
        "Illustration": ["illustrated", "storybook design", "decorative composition"],
        "Painting": ["painterly", "textured color", "fine-art composition"],
    }
    return {
        "mood": mood_tags[:4],
        "style": style_map.get(medium, ["visual reference", "composed lighting", "story mood"]),
        "story": story_tags[:4],
        "palette": palette_tags[:4],
        "data_tags": [title.lower(), medium.lower(), *mood_tags[:2], *story_tags[:2]],
        "prompt": f"A {medium.lower()} reference with {mood} mood, {story} story energy, and a {palette} palette.",
    }


def build_scene(item: tuple, image_record: dict) -> dict:
    scene_id, page, title, year, director, medium, mood, story, palette = item
    fields = vibe_fields(mood, story, palette, medium, title)
    return {
        "id": scene_id,
        "title": title,
        "year": year,
        "director": director,
        "medium": medium,
        "image": image_record["local_path"],
        "image_status": "real_external_thumbnail",
        "image_source_url": image_record["page_url"],
        "image_usage_note": image_record["usage_note"],
        **fields,
        "sources": [WIKIPEDIA, WIKIMEDIA, CURATION],
        "source_notes": SOURCE_NOTE,
    }


def main() -> int:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    existing = []
    if OUT_PATH.exists():
        existing = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    by_id = {scene["id"]: scene for scene in existing}

    for item in CATALOG:
        scene_id, page, *_ = item
        if len(by_id) >= TARGET_EXTRA:
            break
        if scene_id in by_id and (ROOT / by_id[scene_id]["image"].lstrip("/")).exists():
            print(f"skip {scene_id}")
            continue

        try:
            time.sleep(2.5)
            data = fetch_summary(page)
            image = data.get("thumbnail") or data.get("originalimage")
            if not image:
                print(f"miss {scene_id}: no image")
                continue
            source_url = image["source"]
            suffix = Path(urllib.parse.urlparse(source_url).path).suffix or ".jpg"
            filename = f"{slugify(scene_id)}{suffix}"
            local_path = ASSET_DIR / filename
            download(source_url, local_path)
            image_record = {
                "local_path": f"/static/assets/real/{filename}",
                "page_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
                "usage_note": (
                    "Fetched from Wikipedia/Wikimedia page image metadata for local research prototype use. "
                    "Verify license or replace before redistribution."
                ),
            }
            by_id[scene_id] = build_scene(item, image_record)
            print(f"ok {scene_id} ({len(by_id)}/{TARGET_EXTRA})")
        except Exception as exc:
            print(f"fail {scene_id}: {exc}")

    scenes = list(by_id.values())[:TARGET_EXTRA]
    OUT_PATH.write_text(json.dumps(scenes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(scenes)} scenes to {OUT_PATH}")
    return 0 if len(scenes) >= TARGET_EXTRA else 1


if __name__ == "__main__":
    raise SystemExit(main())
