#!/usr/bin/env python3
"""Build the rich visual travel experience HTML."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "data/trip_data.json"
CSS_FILE = ROOT / "src/templates/visual.css"
TEMPLATE_FILE = ROOT / "src/templates/visual.html"
OUT = ROOT / "outputs/japan-visual.html"


def load_data() -> dict:
    """Load trip data from JSON."""
    return json.loads(DATA.read_text(encoding="utf-8"))


def enrich_data_with_stories(data: dict) -> dict:
    """Add historical stories and cultural context to locations."""
    from src.content.stories import get_location_story, get_poi_story
    
    for location in data["locations"]:
        location["story"] = get_location_story(location["name"])
        
        # Add stories to POIs
        for poi in location.get("pois", []):
            poi["story"] = get_poi_story(poi["name"])
    
    return data


def enrich_data_with_images(data: dict) -> dict:
    """Add Unsplash images to locations and POIs.
    
    Requires UNSPLASH_ACCESS_KEY env var.
    Falls back gracefully if not available.
    """
    import os
    
    if not os.getenv("UNSPLASH_ACCESS_KEY"):
        print("⚠️  UNSPLASH_ACCESS_KEY not set — skipping image fetch")
        print("   Set it with: export UNSPLASH_ACCESS_KEY='your_key'")
        print("   Get one free at: https://unsplash.com/developers")
        return data
    
    try:
        from src.media.unsplash import enrich_locations_with_images, get_japan_hero_image
        
        print("🖼️  Fetching images from Unsplash...")
        data["hero_image"] = get_japan_hero_image()
        enrich_locations_with_images(data["locations"])
        print("   ✓ Images loaded")
    except Exception as e:
        print(f"   ⚠️  Image fetch failed: {e}")
    
    return data


def build_visual_html() -> str:
    """Build the rich visual HTML with all enhancements."""
    data = load_data()
    
    # Add AI recommendations
    from src.ai import add_recommendations_to_data
    data = add_recommendations_to_data(data)
    
    # Add stories and cultural context
    data = enrich_data_with_stories(data)
    
    # Add images (if API key available)
    data = enrich_data_with_images(data)
    
    # Render template
    css = CSS_FILE.read_text(encoding="utf-8")
    template = Template(TEMPLATE_FILE.read_text(encoding="utf-8"))
    
    html = template.render(
        css=css,
        flights=data["flight_options"],
        locations=data["locations"],
        recommendations=data.get("ai_recommendations", {}),
        hero_image=data.get("hero_image"),
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        trip_data_json=json.dumps(data, ensure_ascii=False).replace("</script>", "<\\/script>"),
    )
    
    return html


if __name__ == "__main__":
    print("============================================================")
    print("Building Rich Visual Travel Experience")
    print("============================================================\n")
    
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build_visual_html()
    OUT.write_text(html, encoding="utf-8")
    
    print(f"\n✅ Done!\n")
    print(f"Output: {OUT}")
    print(f"Size: {len(html) / 1024:.1f} KB")
    print(f"\nOpen in browser:")
    print(f"  file://{OUT}")
