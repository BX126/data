# VibeMatch Prototype Plan

Build a runnable Flask app called **VibeMatch** for film-scene vibe matching.

The first version should be a working prototype, but the plan is revised to use **real, source-backed seed data** instead of invented scene metadata. Keep the app local and simple: no React, auth, database, uploads, scraping, or live API calls in the prototype.

## Prototype Goal

A user can browse film and animation references, search by mood, style, director, story, palette, tag, or source, filter by medium, click a scene card, and see similar-vibe recommendations.

The app should feel like a visual research board for directors, editors, storyboard artists, animators, and prompt writers.

## Tech Stack

- Python
- Flask
- Jinja templates
- HTML
- CSS
- Small vanilla JavaScript for search, filter, and modal behavior
- Local static data in `data/scenes.py`

Do not use React, Next.js, TypeScript, build tools, API keys, scraping, or a database.

## File Structure

```text
vibe_match/
  app.py
  requirements.txt
  data/
    __init__.py
    extra_scenes.json
    real_images.json
    scenes.py
  scripts/
    build_expanded_dataset.py
    fetch_real_images.py
  templates/
    index.html
  static/
    assets/
      real/
      generated/
    style.css
    app.js
```

## Run Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app should run at:

```text
http://127.0.0.1:5000
```

## Real Data Strategy

For the prototype, keep the app local at runtime. The first 24 curated rows live in `data/scenes.py`, and the expanded set of 96 additional rows lives in `data/extra_scenes.json`, giving the board 120 references total. Each row includes a `sources` list so the user can tell what each field is based on.

Do not use placeholder images. Every visual asset in the prototype must be one of:

- A real local title image fetched from Wikipedia/Wikimedia page image metadata, clearly marked as a local research thumbnail whose license must be verified before redistribution.
- A local public-domain, Creative Commons, or otherwise licensed image stored in `static/assets/`.
- A generated original reference image stored in `static/assets/generated/`, clearly marked as generated.
- A TMDb image used later only after API setup, attribution, and terms-of-use compliance.
- No image, with the UI showing a clean text-first card state until a usable asset exists.

For copyrighted film stills, store metadata now and defer image ingestion until permissions/API rules are handled.

### Recommended Data Sources

| Need | Source | What It Contributes | Prototype Use |
| --- | --- | --- | --- |
| Movie metadata | Wikidata | CC0 title, release year, director, country, genre, external IDs | Use immediately for title/year/director/source URLs |
| Movie metadata and images | TMDb API | Posters, backdrops, movie metadata, people, image configuration | Later; requires API key and terms/attribution handling |
| Scene boundaries and cinematic style | MovieNet | 1,100 movies, 42K scene boundaries, action/place tags, shot scale/movement style tags, keyframes | Use as the primary future scene/style source |
| Affect/mood labels | LIRIS-ACCEDE | Creative Commons movie excerpts with valence/arousal/fear annotations | Use for real mood mapping and legally safer demo clips |
| Story/social situation labels | MovieGraphs | Clip-level graphs for characters, emotions, relationships, interactions, motivations, timestamps | Use for story tags like betrayal, reunion, threat, confession |
| Broad mood/theme tags | MovieLens Tag Genome | Tag relevance scores across movies, useful for terms like atmospheric, surreal, bleak, romantic | Use later for search expansion and similarity weighting |
| Plot/tag corpus | MPST | About 14K movie synopses with fine-grained plot tags | Use later for story and tone tags when scene-level data is absent |

Source links:

- MovieNet: https://movienet.github.io/
- LIRIS-ACCEDE: https://liris-accede.ec-lyon.fr/
- MovieGraphs paper: https://arxiv.org/abs/1712.06761
- MovieLens datasets: https://grouplens.org/datasets/movielens/
- Wikidata data access: https://www.wikidata.org/wiki/Wikidata:Data_access
- TMDb API docs: https://developer.themoviedb.org/docs/getting-started
- TMDb image basics: https://developer.themoviedb.org/docs/image-basics
- MPST paper: https://arxiv.org/abs/1802.07858

## Prototype Seed Set

Create 24 manually curated scene/reference entries. Prefer entries where title, year, director, and broad genre can be verified from Wikidata or TMDb, and where mood/style/story tags are derived from one of:

- LIRIS-ACCEDE affect labels, if using one of its Creative Commons clips.
- MovieNet action/place/cinematic-style annotations, if the movie/segment is covered.
- MovieGraphs social situation labels, if the clip is covered.
- Manual curation with a `source_notes` field when no scene-level dataset covers the exact scene.

Use these seed references as the first board:

- Before Sunset
- Big Hero 6
- Klaus
- Breaking Bad
- City of God
- The Godfather Part II
- The Lord of the Rings
- Claymore
- Jurassic World
- Scarface
- The Best Offer
- Cocaine Bear
- Spirited Away
- In the Mood for Love
- Amelie
- Her
- Blade Runner 2049
- The Grand Budapest Hotel
- Little Women
- The Tale of the Princess Kaguya
- WALL-E
- Pan's Labyrinth
- Coraline
- The Wind Rises

## Scene Schema

Each scene entry in `data/scenes.py` should use this schema:

```python
{
    "id": "before-sunset-walk",
    "title": "Before Sunset",
    "year": 2004,
    "director": "Richard Linklater",
    "medium": "Cinematic",
    "image": "/static/assets/real/before-sunset-walk.jpg",
    "image_status": "real_external_thumbnail",
    "mood": ["romantic", "nostalgic", "bittersweet", "intimate"],
    "style": ["naturalistic", "soft daylight", "walking two-shot"],
    "story": ["walking conversation", "emotional reconnection"],
    "palette": ["green", "warm daylight", "natural tones"],
    "data_tags": ["romance", "conversation", "Paris", "reconnection"],
    "prompt": "A naturalistic romantic walking conversation in soft daylight, intimate framing, nostalgic and bittersweet mood.",
    "sources": [
        {
            "name": "Wikidata",
            "url": "https://www.wikidata.org/",
            "fields": ["title", "year", "director"]
        }
    ],
    "source_notes": "Scene-level mood/style tags are manually curated for the prototype; replace with MovieNet/LIRIS/MovieGraphs labels where available."
}
```

Use `image_status` values:

- `licensed`: local/public-domain/Creative Commons image with permission.
- `real_external_thumbnail`: real title image fetched from Wikipedia/Wikimedia page image metadata for local research use; verify license before redistribution.
- `generated`: original AI-generated or hand-created image that is not a film still.
- `tmdb`: TMDb image URL used after API setup and attribution.
- `missing`: no usable image yet; render the card without an image.

## Medium Categories

Use these filter categories:

- All
- Cinematic
- Cartoon
- Anime
- Drawing
- Illustration
- Painting
- 3D

## App Requirements

### `app.py`

- Load `SCENES` from `data/scenes.py`.
- Route `/` renders `index.html`.
- Pass scenes, categories, and source names to the template.
- Implement `get_similar_scenes(scene_id, limit=4)`.
- Precompute `search_text` and `similar_scenes` for every scene.

Similarity score:

- `+1` per overlapping mood tag.
- `+1` per overlapping style tag.
- `+1` per overlapping story tag.
- `+1` per overlapping palette tag.
- `+1` per overlapping `data_tags` tag.
- `+2` for same medium.
- `+1` for same director.
- `+1` if both entries share at least one real data source.

### `data/scenes.py`

- Create 24 primary scene entries using the schema above.
- Merge the 96 additional entries from `data/extra_scenes.json` into `SCENES`.
- Use real title/year/director metadata.
- Use source-backed tags where practical.
- Do not use placeholder images. Use local licensed/generated assets, or set missing assets explicitly:

```python
"image": None,
"image_status": "missing"
```

- Do not scrape websites.
- Do not use API keys.
- Do not download copyrighted stills.
- Do not use `picsum.photos`, stock placeholders, blurred filler images, or fake stills represented as real stills.

### Expansion Scripts

- `scripts/fetch_real_images.py` fetches real images for the original 24 curated rows.
- `scripts/build_expanded_dataset.py` fetches real images and writes `data/extra_scenes.json` for the expanded 96-row set.
- Both scripts are offline ingestion tools. The Flask app should not call external APIs at runtime.

### `templates/index.html`

- White background.
- Header: `VibeMatch`.
- Subtitle: `A vibe search engine for video storytelling references`.
- Search placeholder: `Search by mood, style, color, director, source - anything.`
- Category buttons: `All`, `Cinematic`, `Cartoon`, `Anime`, `Drawing`, `Illustration`, `Painting`, `3D`.
- Sample query chips:
  - `melancholic green`
  - `romantic walking`
  - `dark tense interior`
  - `storybook winter`
  - `surreal lonely`
  - `warm family`
  - `MovieNet style`
  - `LIRIS high arousal`
- Responsive card grid.
- Each card shows the approved image when available, otherwise a clean text-first layout with title, year, director, medium, top tags, and compact source label.
- Clicking a card opens a modal.

### Modal Content

Each modal should show:

- Large approved image when available; omit the image area when `image_status` is `missing`.
- Title, year, director, medium.
- Image status.
- Mood tags.
- Style tags.
- Story tags.
- Palette tags.
- Data tags.
- Generation prompt.
- Source links.
- Source notes.
- Similar vibes section with 4 similar scenes.

### `static/app.js`

Implement client-side:

- Search over `title`, `director`, `medium`, `mood`, `style`, `story`, `palette`, `data_tags`, `prompt`, `sources`, and `source_notes`.
- Category filtering.
- Modal open/close.
- Escape key close.
- Click-outside close.
- Sample query chip behavior.
- Empty-state message when no cards match.

No frameworks.

### `static/style.css`

Create a clean modern visual board:

- White background.
- Responsive grid.
- Rounded cards.
- Soft shadows.
- Tight metadata layout.
- Tag chips.
- Small source badges.
- Modal overlay.
- Similar scene mini-cards.

Keep the UI practical and visual-reference focused, not like a marketing landing page.

## One-Hour Build Schedule

### 0-10 min: Flask Skeleton

Create the project files, install Flask, and verify `python app.py` opens the index page.

### 10-30 min: Real Local Seed Data

Create 24 local scene entries. Use real title/year/director metadata and source URLs. Do not overbuild importers yet.

The goal is a believable local dataset whose provenance is clear.

### 30-45 min: UI

Build the grid:

- Search bar.
- Category filters.
- Sample query chips.
- Scene cards.
- Source badges.

Cards should include searchable data attributes:

```html
<article
  class="scene-card"
  data-medium="{{ scene.medium }}"
  data-search="{{ scene.search_text }}"
>
```

### 45-55 min: Modal

Click a card to open a modal. The easiest implementation is to render hidden modal content for each scene and show the selected one with JavaScript.

### 55-60 min: Similar Vibes and Polish

Precompute similar scenes in Flask and show them in the modal.

The demo should support queries like:

- `lonely green painterly`
- `romantic walking`
- `dark tense interior`
- `warm family`
- `storybook winter`
- `surreal lonely`
- `high arousal`
- `social betrayal`

## Minimal `app.py` Logic

```python
from flask import Flask, render_template
from data.scenes import SCENES

app = Flask(__name__)

CATEGORIES = ["All", "Cinematic", "Cartoon", "Anime", "Drawing", "Illustration", "Painting", "3D"]


def source_names(scene):
    return [source["name"] for source in scene.get("sources", [])]


def similarity(a, b):
    score = 0
    for field in ["mood", "style", "story", "palette", "data_tags"]:
        score += len(set(a.get(field, [])) & set(b.get(field, [])))
    if a["medium"] == b["medium"]:
        score += 2
    if a["director"] == b["director"]:
        score += 1
    if set(source_names(a)) & set(source_names(b)):
        score += 1
    return score


def enrich_scenes():
    enriched = []
    for scene in SCENES:
        s = dict(scene)
        sources = " ".join(source_names(s))
        s["search_text"] = " ".join([
            s["title"],
            str(s["year"]),
            s["director"],
            s["medium"],
            " ".join(s.get("mood", [])),
            " ".join(s.get("style", [])),
            " ".join(s.get("story", [])),
            " ".join(s.get("palette", [])),
            " ".join(s.get("data_tags", [])),
            s.get("prompt", ""),
            sources,
            s.get("source_notes", ""),
        ]).lower()

        ranked = []
        for other in SCENES:
            if other["id"] == s["id"]:
                continue
            ranked.append((similarity(s, other), other))
        ranked.sort(key=lambda item: item[0], reverse=True)
        s["similar_scenes"] = [item[1] for item in ranked[:4]]
        enriched.append(s)
    return enriched


@app.route("/")
def index():
    scenes = enrich_scenes()
    source_set = sorted({name for scene in scenes for name in source_names(scene)})
    return render_template(
        "index.html",
        scenes=scenes,
        categories=CATEGORIES,
        sources=source_set,
    )


if __name__ == "__main__":
    app.run(debug=True)
```

## Later Data Pipeline

After the prototype works, add an offline ingestion script, not a live app dependency:

```text
scripts/
  build_seed_data.py
  normalize_wikidata.py
  normalize_liris.py
  normalize_movienet.py
  normalize_moviegraphs.py
```

Pipeline:

1. Start with a manually reviewed title list.
2. Resolve stable IDs from Wikidata/TMDb/IMDb where allowed.
3. Pull title/year/director/country/genre from Wikidata.
4. Add scene/style candidates from MovieNet.
5. Add valence/arousal/fear labels from LIRIS-ACCEDE.
6. Add interaction/motivation/story tags from MovieGraphs.
7. Add broad vibe tags from MovieLens Tag Genome or MPST.
8. Export a reviewed `data/scenes.py` or `data/scenes.json`.

Keep the app itself local and deterministic. Data refresh should be a separate command.

## Licensing Notes

- Wikidata data is CC0, but attribution is still recommended.
- LIRIS-ACCEDE uses Creative Commons movie excerpts but requires EULA-based access.
- MovieNet distributes annotations, metadata, and keyframes under its own access conditions; full movies are restricted by copyright.
- MovieLens datasets have usage terms in their README files and usually should not be publicly redistributed.
- TMDb requires an API key and terms-of-use compliance. Image URLs are constructed from `base_url`, `file_size`, and `file_path` returned by the API configuration.
- Do not ship copyrighted film stills unless the project has permission or a license.
