"""Accommodation matcher - generates date-aligned search queries for route variants."""
from datetime import date, timedelta
from typing import TypedDict


class AccommodationQuery(TypedDict):
    """Accommodation search query for a specific city and date range."""
    city: str
    checkin: str  # ISO date
    checkout: str  # ISO date
    nights: int
    adults: int
    rooms: int
    airbnb_url: str
    agoda_url: str
    booking_url: str


def build_accommodation_queries(
    flight_departure_date: str,
    route: list[str],
    nights_allocation: dict[str, int],
    travellers: int = 5,
    rooms: int = 2,
) -> list[AccommodationQuery]:
    """Generate accommodation search URLs for each city in route.
    
    Args:
        flight_departure_date: ISO date string (YYYY-MM-DD)
        route: List of city names in order
        nights_allocation: Dict mapping city name to number of nights
        travellers: Number of guests
        rooms: Number of rooms needed
    
    Returns:
        List of AccommodationQuery dicts with search URLs
    """
    queries = []
    current_date = date.fromisoformat(flight_departure_date)
    
    for city in route:
        nights = nights_allocation[city]
        checkout_date = current_date + timedelta(days=nights)
        
        # City name mapping for search URLs
        city_normalized = city.replace(" ", "-")
        
        queries.append({
            "city": city,
            "checkin": current_date.isoformat(),
            "checkout": checkout_date.isoformat(),
            "nights": nights,
            "adults": travellers,
            "rooms": rooms,
            "airbnb_url": (
                f"https://www.airbnb.com/s/{city_normalized}--Japan/homes"
                f"?checkin={current_date.isoformat()}"
                f"&checkout={checkout_date.isoformat()}"
                f"&adults={travellers}"
                f"&children=0"
            ),
            "agoda_url": (
                f"https://www.agoda.com/search"
                f"?city={city}"
                f"&checkIn={current_date.isoformat()}"
                f"&checkOut={checkout_date.isoformat()}"
                f"&rooms={rooms}"
                f"&adults={travellers}"
                f"&cid=1844104"
            ),
            "booking_url": (
                f"https://www.booking.com/searchresults.html"
                f"?ss={city}%2C+Japan"
                f"&checkin={current_date.isoformat()}"
                f"&checkout={checkout_date.isoformat()}"
                f"&group_adults={travellers}"
                f"&no_rooms={rooms}"
            ),
        })
        
        current_date = checkout_date
    
    return queries
