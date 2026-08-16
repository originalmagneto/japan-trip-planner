"""Unsplash API client for fetching location images.

Free tier: 50 requests/hour
"""
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
CACHE_DIR = Path(__file__).resolve().parents[2] / "data/image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_location_image(query: str, orientation: str = "landscape") -> dict | None:
    """Fetch a single image from Unsplash.
    
    Args:
        query: Search query (e.g., "Tokyo Senso-ji temple")
        orientation: "landscape", "portrait", or "squarish"
    
    Returns:
        Dict with urls, alt_description, user attribution, or None if error
    """
    if not UNSPLASH_ACCESS_KEY:
        return None
    
    # Check cache
    cache_key = f"{query}_{orientation}".replace(" ", "_")
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    
    # Fetch from API
    params = urllib.parse.urlencode({
        "query": query,
        "orientation": orientation,
        "per_page": 1,
    })
    
    url = f"https://api.unsplash.com/search/photos?{params}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        
        if not data.get("results"):
            return None
        
        photo = data["results"][0]
        result = {
            "url_full": photo["urls"]["full"],
            "url_regular": photo["urls"]["regular"],
            "url_small": photo["urls"]["small"],
            "url_thumb": photo["urls"]["thumb"],
            "alt": photo.get("alt_description", query),
            "photographer": photo["user"]["name"],
            "photographer_url": photo["user"]["links"]["html"],
            "unsplash_url": photo["links"]["html"],
        }
        
        # Cache result
        cache_file.write_text(json.dumps(result, indent=2))
        
        return result
    
    except Exception as e:
        print(f"Failed to fetch image for '{query}': {e}")
        return None


def enrich_locations_with_images(locations: list[dict]) -> list[dict]:
    """Add Unsplash images to location and POI data.
    
    Modifies locations in-place.
    """
    for location in locations:
        # City hero image
        city_query = f"{location['name']} Japan cityscape"
        city_img = fetch_location_image(city_query, orientation="landscape")
        if city_img:
            location["hero_image"] = city_img
        
        # POI images
        for poi in location.get("pois", []):
            poi_query = f"{poi['name']} {location['name']} Japan"
            poi_img = fetch_location_image(poi_query, orientation="squarish")
            if poi_img:
                poi["image"] = poi_img
    
    return locations


def get_japan_hero_image() -> dict | None:
    """Get a stunning hero image for the main page."""
    return fetch_location_image("Japan Mount Fuji cherry blossom", orientation="landscape")
