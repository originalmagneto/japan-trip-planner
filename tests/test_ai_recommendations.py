"""Tests for AI recommendations engine."""
import json
from pathlib import Path

from src.ai import (
    calculate_flight_score,
    generate_recommendations,
    get_recommendation_weights,
    add_recommendations_to_data,
)


def test_recommendation_weights_sum_to_one():
    """All recommendation weight sets should sum to ~1.0."""
    for rec_type in ["best_value", "cheapest", "most_flexible", "fastest", "most_convenient"]:
        weights = get_recommendation_weights(rec_type)
        total = sum(weights.values())
        assert 0.95 <= total <= 1.05, f"{rec_type} weights sum to {total}"


def test_calculate_flight_score_for_cheap_flight():
    """Cheap flights score higher with cheapest weights."""
    cheap_flight = {
        "price_total_eur": 4500,
        "verified": True,
        "stops": "1 stop",
        "departure_date": "2026-09-24",
        "arrival_airport": "TYO",
        "departure_airport": "TYO",
    }
    
    weights = get_recommendation_weights("cheapest")
    score = calculate_flight_score(cheap_flight, weights)
    
    assert score > 70  # Should score well for cheapest


def test_calculate_flight_score_for_flexible_flight():
    """Open-jaw flights score higher with flexibility weights."""
    flexible_flight = {
        "price_total_eur": 6000,
        "verified": False,
        "stops": "1 stop",
        "departure_date": "2026-09-24",
        "arrival_airport": "TYO",
        "departure_airport": "OSA",  # Different = open-jaw
    }
    
    weights = get_recommendation_weights("most_flexible")
    score = calculate_flight_score(flexible_flight, weights)
    
    assert score > 50  # Should score reasonably for flexibility


def test_generate_recommendations_returns_all_types():
    """Recommendations should include all 5 types."""
    flights = [
        {
            "id": "f1",
            "price_total_eur": 5000,
            "verified": True,
            "stops": "nonstop",
            "departure_date": "2026-09-24",
            "arrival_airport": "TYO",
            "departure_airport": "TYO",
        },
        {
            "id": "f2",
            "price_total_eur": 4500,
            "verified": False,
            "stops": "1 stop",
            "departure_date": "2026-09-25",
            "arrival_airport": "OSA",
            "departure_airport": "TYO",
        },
    ]
    
    recommendations = generate_recommendations(flights)
    
    assert len(recommendations) == 5
    assert "best_value" in recommendations
    assert "cheapest" in recommendations
    assert "most_flexible" in recommendations
    assert "fastest" in recommendations
    assert "most_convenient" in recommendations


def test_recommendations_include_reason():
    """Each recommendation should have a human-readable reason."""
    flights = [
        {
            "id": "f1",
            "price_total_eur": 5000,
            "verified": True,
            "stops": "nonstop",
            "departure_date": "2026-09-24",
            "arrival_airport": "TYO",
            "departure_airport": "TYO",
        },
    ]
    
    recommendations = generate_recommendations(flights)
    
    for rec_type, rec in recommendations.items():
        assert "reason" in rec
        assert len(rec["reason"]) > 20
        # Most reasons include price, but flexibility focuses on routing
        if rec_type in ["cheapest", "best_value"]:
            assert "€" in rec["reason"]


def test_add_recommendations_to_data():
    """add_recommendations_to_data should inject ai_recommendations key."""
    data = {
        "flight_options": [
            {
                "id": "f1",
                "price_total_eur": 5000,
                "verified": True,
                "stops": "nonstop",
                "departure_date": "2026-09-24",
                "arrival_airport": "TYO",
                "departure_airport": "TYO",
            },
        ]
    }
    
    result = add_recommendations_to_data(data)
    
    assert "ai_recommendations" in result
    assert len(result["ai_recommendations"]) == 5


def test_recommendations_with_real_trip_data():
    """Test recommendations with actual trip_data.json."""
    data_file = Path(__file__).resolve().parents[1] / "data/trip_data.json"
    if not data_file.exists():
        return  # Skip if data not available
    
    data = json.loads(data_file.read_text())
    recommendations = generate_recommendations(data["flight_options"])
    
    # Should have recommendations for flights with prices
    assert len(recommendations) > 0
    
    # Each recommendation should point to a valid flight
    for rec_type, rec in recommendations.items():
        flight_id = rec["flight_id"]
        assert any(f["id"] == flight_id for f in data["flight_options"])
