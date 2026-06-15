import random

from flask import Flask, render_template

from data.scenes import SCENES

app = Flask(__name__)

CATEGORIES = ["All", "Cinematic", "Cartoon", "Anime", "Drawing", "Illustration", "Painting", "3D"]


def source_names(scene):
    return [source["name"] for source in scene.get("sources", [])]


def image_status_label(scene):
    labels = {
        "real_external_thumbnail": "real image",
        "generated": "generated",
        "licensed": "licensed",
        "tmdb": "TMDb",
        "missing": "missing",
    }
    return labels.get(scene.get("image_status"), scene.get("image_status", "image"))


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


def get_similar_scenes(scene_id, limit=4):
    scene = next((item for item in SCENES if item["id"] == scene_id), None)
    if scene is None:
        return []
    ranked = [
        (similarity(scene, other), other)
        for other in SCENES
        if other["id"] != scene_id
    ]
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]


def search_text(scene):
    parts = [
        scene["title"],
        str(scene["year"]),
        scene["director"],
        scene["medium"],
        " ".join(scene.get("mood", [])),
        " ".join(scene.get("style", [])),
        " ".join(scene.get("story", [])),
        " ".join(scene.get("palette", [])),
        " ".join(scene.get("data_tags", [])),
        scene.get("prompt", ""),
    ]
    return " ".join(parts).lower()


def enrich_scenes():
    enriched = []
    for scene in SCENES:
        item = dict(scene)
        item["image_status_label"] = image_status_label(item)
        item["search_text"] = search_text(item)
        item["source_names"] = source_names(item)
        item["similar_scenes"] = get_similar_scenes(item["id"])
        enriched.append(item)
    return enriched


@app.route("/")
def index():
    scenes = enrich_scenes()
    random.shuffle(scenes)
    source_set = sorted({name for scene in scenes for name in scene["source_names"]})
    return render_template(
        "index.html",
        scenes=scenes,
        categories=CATEGORIES,
        sources=source_set,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
