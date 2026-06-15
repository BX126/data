from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "static" / "assets" / "real"
MANIFEST_PATH = ROOT / "data" / "real_images.json"
USER_AGENT = "VibeMatchLocalPrototype/0.1 (local research prototype; no public redistribution)"

PAGES = {
    "before-sunset-walk": "Before Sunset",
    "big-hero-6-family-lab": "Big Hero 6 (film)",
    "klaus-winter-village": "Klaus (film)",
    "breaking-bad-red-interior": "Breaking Bad",
    "city-of-god-street-chaos": "City of God (2002 film)",
    "godfather-part-ii-candle-room": "The Godfather Part II",
    "lord-of-the-rings-misty-forest": "The Lord of the Rings: The Fellowship of the Ring",
    "claymore-dusk-warrior": "Claymore (manga)",
    "jurassic-world-jungle-awe": "Jurassic World",
    "scarface-neon-crime-room": "Scarface (1983 film)",
    "the-best-offer-auction-hall": "The Best Offer",
    "cocaine-bear-forest-comedy": "Cocaine Bear",
    "spirited-away-bathhouse-night": "Spirited Away",
    "in-the-mood-for-love-corridor": "In the Mood for Love",
    "amelie-paris-whimsy": "Amelie",
    "her-future-loneliness": "Her (2013 film)",
    "blade-runner-2049-desert-neon": "Blade Runner 2049",
    "grand-budapest-hotel-corridor": "The Grand Budapest Hotel",
    "little-women-garden-memory": "Little Women (2019 film)",
    "princess-kaguya-brush-dream": "The Tale of the Princess Kaguya (film)",
    "wall-e-silent-robot": "WALL-E",
    "pans-labyrinth-underworld": "Pan's Labyrinth",
    "coraline-gothic-doorway": "Coraline (film)",
    "the-wind-rises-aviation-dream": "The Wind Rises",
}


def safe_filename(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def fetch_page_image(page_title: str) -> dict:
    page_url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page_title.replace(" ", "_"), safe=":_()'")
    request = urllib.request.Request(page_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=25) as response:
        html = response.read().decode("utf-8", errors="replace")

    og_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    src_match = re.search(r'<td[^>]+class="infobox-image"[\s\S]*?<img[^>]+src="([^"]+)"', html)
    source = None
    if og_match:
        source = og_match.group(1)
    elif src_match:
        source = src_match.group(1)
        if source.startswith("//"):
            source = "https:" + source
        elif source.startswith("/"):
            source = "https://en.wikipedia.org" + source
    if not source:
        raise RuntimeError(f"No page image for {page_title}")
    source = unescape(source)

    title_match = re.search(r'<title>(.*?)</title>', html)
    resolved_title = page_title
    if title_match:
        resolved_title = unescape(title_match.group(1)).replace(" - Wikipedia", "")

    return {
        "page_title": resolved_title,
        "page_url": page_url,
        "source_url": source,
        "image_name": Path(urllib.parse.urlparse(source).path).name,
    }


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        destination.write_bytes(response.read())


def main() -> int:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {}
    failures = {}

    for scene_id, page_title in PAGES.items():
        if scene_id in manifest and (ROOT / manifest[scene_id]["local_path"].lstrip("/")).exists():
            print(f"skip {scene_id}: already fetched")
            continue
        try:
            time.sleep(4.0)
            record = fetch_page_image(page_title)
            suffix = Path(urllib.parse.urlparse(record["source_url"]).path).suffix or ".jpg"
            filename = f"{safe_filename(scene_id)}{suffix}"
            download(record["source_url"], ASSET_DIR / filename)
            manifest[scene_id] = {
                **record,
                "local_path": f"/static/assets/real/{filename}",
                "image_status": "real_external_thumbnail",
                "usage_note": (
                    "Fetched from Wikipedia/Wikimedia page image metadata for local research prototype use. "
                    "Verify license or replace before redistribution."
                ),
            }
            print(f"ok {scene_id}: {record['page_title']}")
        except Exception as exc:
            failures[scene_id] = str(exc)
            print(f"fail {scene_id}: {exc}", file=sys.stderr)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        (ROOT / "data" / "real_images_failures.json").write_text(
            json.dumps(failures, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(f"wrote {MANIFEST_PATH} with {len(manifest)} images")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
