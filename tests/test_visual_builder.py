"""Tests for visual HTML builder."""
import json
from pathlib import Path

from src.build_visual import build_visual_html, enrich_data_with_stories


def test_build_visual_html_produces_valid_output():
    """Visual HTML should be generated without errors."""
    html = build_visual_html()
    
    assert len(html) > 50000  # Should be substantial
    assert "<!DOCTYPE html>" in html
    assert "Japan Trip Planner" in html
    assert "🤖 AI Odporúčania" in html
    assert "🗾 Destinácie" in html


def test_visual_html_includes_ai_recommendations():
    """Visual HTML should embed AI recommendations."""
    html = build_visual_html()
    
    # Should have recommendation cards
    assert "Najlepší pomer cena/výkon" in html or "best_value" in html
    assert "rec-card" in html


def test_visual_html_includes_location_stories():
    """Visual HTML should include historical stories."""
    html = build_visual_html()
    
    # Should have location taglines
    assert "Zaujímavosti" in html or "fun-facts" in html
    assert "Kultúrne tipy" in html or "cultural_tips" in html


def test_enrich_data_with_stories_adds_content():
    """Story enrichment should add taglines and facts."""
    data_file = Path(__file__).resolve().parents[1] / "data/trip_data.json"
    data = json.loads(data_file.read_text())
    
    enriched = enrich_data_with_stories(data)
    
    # Check that stories were added
    assert len(enriched["locations"]) > 0
    
    # Find Tokyo or Kyoto (we have stories for those)
    major_cities = [loc for loc in enriched["locations"] if loc["name"] in ["Tokyo", "Kyoto", "Osaka"]]
    assert len(major_cities) > 0
    
    tokyo = next((loc for loc in enriched["locations"] if loc["name"] == "Tokyo"), None)
    if tokyo:
        assert "story" in tokyo
        assert "tagline" in tokyo["story"]
        assert "fun_facts" in tokyo["story"]
        assert len(tokyo["story"]["fun_facts"]) > 0


def test_visual_html_has_expandable_sections():
    """Visual HTML should have collapsible sections."""
    html = build_visual_html()
    
    assert "expand-toggle" in html
    assert "expand-content" in html
    assert "toggleExpand" in html


def test_visual_html_responsive_design():
    """Visual HTML should include responsive CSS."""
    html = build_visual_html()
    
    assert "@media" in html
    assert "clamp(" in html  # Fluid typography
    assert "grid-template-columns" in html
