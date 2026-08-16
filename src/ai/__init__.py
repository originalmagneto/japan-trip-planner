"""AI-powered flight recommendations engine.

Analyzes flights across multiple dimensions and generates recommendations
for different traveler profiles and priorities.
"""
from datetime import datetime
from typing import Literal


RecommendationType = Literal[
    "best_value",      # Best price/experience ratio
    "cheapest",        # Lowest total price
    "most_flexible",   # Best cancellation/change terms
    "fastest",         # Shortest total travel time
    "most_convenient", # Fewest connections, best times
]


def calculate_flight_score(flight: dict, weights: dict[str, float]) -> float:
    """Calculate weighted score for a flight.
    
    Args:
        flight: Flight option dict from trip_data.json
        weights: Dict of criterion -> weight (0.0-1.0)
    
    Returns:
        Normalized score (0-100)
    """
    scores = {}
    
    # Price score (inverse: lower price = higher score)
    if flight.get("price_total_eur"):
        # Normalize to 0-100 (assume range 4000-8000 EUR)
        price_score = max(0, 100 - ((flight["price_total_eur"] - 4000) / 40))
        scores["price"] = price_score
    else:
        scores["price"] = 0
    
    # Verified score (binary: verified = 100, unverified = 50)
    scores["verified"] = 100 if flight.get("verified", False) else 50
    
    # Convenience score (fewer stops = better)
    stops_text = flight.get("stops", "")
    if "nonstop" in stops_text.lower() or "direct" in stops_text.lower():
        scores["convenience"] = 100
    elif "1 stop" in stops_text:
        scores["convenience"] = 70
    elif "2 stop" in stops_text:
        scores["convenience"] = 40
    else:
        scores["convenience"] = 50
    
    # Route flexibility score (open-jaw = more flexible)
    arrival = flight.get("arrival_airport", flight.get("arrival_city", ""))
    departure = flight.get("departure_airport", flight.get("departure_city", ""))
    if arrival != departure:
        scores["flexibility"] = 80
    else:
        scores["flexibility"] = 60
    
    # Timing score (based on outbound window preference)
    # Prefer dates closer to 2026-09-24
    try:
        dep_date = datetime.fromisoformat(flight["departure_date"])
        ideal_date = datetime(2026, 9, 24)
        days_diff = abs((dep_date - ideal_date).days)
        scores["timing"] = max(0, 100 - (days_diff * 10))
    except (KeyError, ValueError):
        scores["timing"] = 50
    
    # Calculate weighted total
    total = sum(scores[key] * weights.get(key, 0) for key in scores)
    return min(100, max(0, total))


def get_recommendation_weights(rec_type: RecommendationType) -> dict[str, float]:
    """Get scoring weights for recommendation type."""
    weights = {
        "best_value": {
            "price": 0.4,
            "verified": 0.3,
            "convenience": 0.2,
            "flexibility": 0.05,
            "timing": 0.05,
        },
        "cheapest": {
            "price": 0.8,
            "verified": 0.1,
            "convenience": 0.05,
            "flexibility": 0.03,
            "timing": 0.02,
        },
        "most_flexible": {
            "price": 0.2,
            "verified": 0.1,
            "convenience": 0.1,
            "flexibility": 0.4,
            "timing": 0.2,
        },
        "fastest": {
            "price": 0.1,
            "verified": 0.2,
            "convenience": 0.6,
            "flexibility": 0.05,
            "timing": 0.05,
        },
        "most_convenient": {
            "price": 0.15,
            "verified": 0.2,
            "convenience": 0.5,
            "flexibility": 0.1,
            "timing": 0.05,
        },
    }
    return weights[rec_type]


def generate_recommendations(flights: list[dict]) -> dict[str, dict]:
    """Generate AI recommendations for all flight options.
    
    Returns dict mapping recommendation_type -> {flight, score, reason}
    """
    recommendations = {}
    
    rec_types: list[RecommendationType] = ["best_value", "cheapest", "most_flexible", "fastest", "most_convenient"]
    
    for rec_type in rec_types:
        weights = get_recommendation_weights(rec_type)
        
        # Score all flights
        scored = []
        for flight in flights:
            if not flight.get("price_total_eur"):
                continue  # Skip flights without price
            
            score = calculate_flight_score(flight, weights)
            scored.append((flight, score))
        
        # Get best
        if scored:
            best_flight, best_score = max(scored, key=lambda x: x[1])
            
            recommendations[rec_type] = {
                "flight_id": best_flight["id"],
                "flight": best_flight,
                "score": round(best_score, 1),
                "reason": _generate_reason(rec_type, best_flight),
            }
    
    return recommendations


def _generate_reason(rec_type: RecommendationType, flight: dict) -> str:
    """Generate human-readable reason for recommendation."""
    price = flight.get("price_total_eur", 0)
    per_person = price / 5
    verified = "verified" if flight.get("verified") else "unverified lead"
    
    reasons = {
        "best_value": f"Best balance of price (€{per_person:.0f}/person), convenience, and reliability. {verified.capitalize()}.",
        "cheapest": f"Lowest total price at €{price:.0f} (€{per_person:.0f}/person). {verified.capitalize()}.",
        "most_flexible": f"Open-jaw routing offers maximum itinerary flexibility. {verified.capitalize()}.",
        "fastest": f"Minimal connections and optimal timing. {verified.capitalize()}.",
        "most_convenient": f"Best combination of departure times and connection efficiency. {verified.capitalize()}.",
    }
    
    return reasons[rec_type]


def add_recommendations_to_data(data: dict) -> dict:
    """Add AI recommendations to trip data structure.
    
    Modifies data in-place and returns it.
    """
    recommendations = generate_recommendations(data["flight_options"])
    data["ai_recommendations"] = recommendations
    return data
