"""Dynamic itinerary variant generator.

Generates optimal route and night allocation based on arrival/departure cities
and total trip duration.
"""
from typing import TypedDict


class NightAllocation(TypedDict):
    """Night allocation for a location."""
    location: str
    nights: int


class ItineraryVariant(TypedDict):
    """Complete itinerary variant."""
    route: list[str]
    nights: dict[str, int]
    total_nights: int
    arrival_city: str
    departure_city: str


# Location database with constraints
LOCATION_DB = {
    "Tokyo": {"nights_min": 3, "nights_max": 6, "must_visit": True, "weight": 4},
    "Kanazawa": {"nights_min": 2, "nights_max": 3, "must_visit": False, "weight": 2},
    "Kyoto": {"nights_min": 3, "nights_max": 5, "must_visit": True, "weight": 4},
    "Osaka": {"nights_min": 2, "nights_max": 3, "must_visit": True, "weight": 3},
}


def normalize_city_code(code: str) -> str:
    """Convert airport/city codes to full city names."""
    mapping = {
        "TYO": "Tokyo",
        "HND": "Tokyo",
        "NRT": "Tokyo",
        "OSA": "Osaka",
        "KIX": "Osaka",
        "ITM": "Osaka",
    }
    return mapping.get(code, code)


def generate_route_variants(
    arrival_city: str,
    departure_city: str,
    total_nights: int,
) -> ItineraryVariant:
    """Generate optimal route and night allocation.
    
    Logic:
    - Tokyo → Tokyo: Classic route (Tokyo → Kanazawa → Kyoto → Osaka)
    - Osaka → Osaka: Reverse route (Osaka → Kyoto → Kanazawa → Tokyo)
    - Tokyo → Osaka: Open-jaw west (Tokyo → Kanazawa → Kyoto → Osaka)
    - Osaka → Tokyo: Open-jaw east (Osaka → Kyoto → Kanazawa → Tokyo)
    
    Night allocation is proportional to location weights with min/max constraints.
    """
    arrival_city = normalize_city_code(arrival_city)
    departure_city = normalize_city_code(departure_city)
    
    # Determine route based on open-jaw logic
    if arrival_city == "Tokyo" and departure_city == "Tokyo":
        route = ["Tokyo", "Kanazawa", "Kyoto", "Osaka"]
    elif arrival_city == "Osaka" and departure_city == "Osaka":
        route = ["Osaka", "Kyoto", "Kanazawa", "Tokyo"]
    elif arrival_city == "Tokyo" and departure_city == "Osaka":
        route = ["Tokyo", "Kanazawa", "Kyoto", "Osaka"]
    elif arrival_city == "Osaka" and departure_city == "Tokyo":
        route = ["Osaka", "Kyoto", "Kanazawa", "Tokyo"]
    else:
        # Fallback: Tokyo-centric route
        route = ["Tokyo", "Kyoto", "Osaka"]
    
    # Allocate nights proportionally by weight
    total_weight = sum(LOCATION_DB[loc]["weight"] for loc in route)
    nights_allocation = {}
    
    for loc in route:
        ideal_nights = int((LOCATION_DB[loc]["weight"] / total_weight) * total_nights)
        # Apply min/max constraints
        nights = max(
            LOCATION_DB[loc]["nights_min"],
            min(LOCATION_DB[loc]["nights_max"], ideal_nights)
        )
        nights_allocation[loc] = nights
    
    # Adjust if total doesn't match (rounding errors)
    allocated_total = sum(nights_allocation.values())
    diff = total_nights - allocated_total
    
    if diff > 0:
        # Add extra nights to first location (arrival city)
        nights_allocation[route[0]] += diff
    elif diff < 0:
        # Remove nights from locations with most nights
        sorted_locs = sorted(route, key=lambda l: nights_allocation[l], reverse=True)
        for loc in sorted_locs:
            if nights_allocation[loc] > LOCATION_DB[loc]["nights_min"]:
                reduction = min(abs(diff), nights_allocation[loc] - LOCATION_DB[loc]["nights_min"])
                nights_allocation[loc] -= reduction
                diff += reduction
                if diff == 0:
                    break
    
    return {
        "route": route,
        "nights": nights_allocation,
        "total_nights": sum(nights_allocation.values()),
        "arrival_city": arrival_city,
        "departure_city": departure_city,
    }
