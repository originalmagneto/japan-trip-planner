"""Tests for accommodation matcher."""
from datetime import date

from src.accommodation import build_accommodation_queries


def test_accommodation_queries_generate_correct_dates():
    """Queries have correct sequential dates based on nights allocation."""
    route = ["Tokyo", "Kyoto", "Osaka"]
    nights = {"Tokyo": 5, "Kyoto": 4, "Osaka": 3}
    
    queries = build_accommodation_queries("2026-09-24", route, nights)
    
    assert len(queries) == 3
    
    # Tokyo: Sept 24-29 (5 nights)
    assert queries[0]["city"] == "Tokyo"
    assert queries[0]["checkin"] == "2026-09-24"
    assert queries[0]["checkout"] == "2026-09-29"
    assert queries[0]["nights"] == 5
    
    # Kyoto: Sept 29 - Oct 3 (4 nights)
    assert queries[1]["city"] == "Kyoto"
    assert queries[1]["checkin"] == "2026-09-29"
    assert queries[1]["checkout"] == "2026-10-03"
    assert queries[1]["nights"] == 4
    
    # Osaka: Oct 3-6 (3 nights)
    assert queries[2]["city"] == "Osaka"
    assert queries[2]["checkin"] == "2026-10-03"
    assert queries[2]["checkout"] == "2026-10-06"
    assert queries[2]["nights"] == 3


def test_accommodation_queries_include_all_urls():
    """Each query includes Airbnb, Agoda, and Booking.com URLs."""
    route = ["Tokyo"]
    nights = {"Tokyo": 4}
    
    queries = build_accommodation_queries("2026-09-24", route, nights)
    
    assert "airbnb.com" in queries[0]["airbnb_url"]
    assert "checkin=2026-09-24" in queries[0]["airbnb_url"]
    assert "checkout=2026-09-28" in queries[0]["airbnb_url"]
    assert "adults=5" in queries[0]["airbnb_url"]
    
    assert "agoda.com" in queries[0]["agoda_url"]
    assert "checkIn=2026-09-24" in queries[0]["agoda_url"]
    
    assert "booking.com" in queries[0]["booking_url"]
    assert "ss=Tokyo" in queries[0]["booking_url"]


def test_accommodation_queries_respect_travellers_and_rooms():
    """Queries use correct travellers and rooms parameters."""
    route = ["Tokyo"]
    nights = {"Tokyo": 4}
    
    queries = build_accommodation_queries("2026-09-24", route, nights, travellers=3, rooms=1)
    
    assert queries[0]["adults"] == 3
    assert queries[0]["rooms"] == 1
    assert "adults=3" in queries[0]["airbnb_url"]
    assert "rooms=1" in queries[0]["agoda_url"]


def test_full_route_accommodation_queries():
    """Full 4-city route generates correct sequence."""
    route = ["Tokyo", "Kanazawa", "Kyoto", "Osaka"]
    nights = {"Tokyo": 4, "Kanazawa": 2, "Kyoto": 4, "Osaka": 3}
    
    queries = build_accommodation_queries("2026-09-24", route, nights)
    
    assert len(queries) == 4
    
    # Verify dates flow correctly
    assert queries[0]["checkout"] == queries[1]["checkin"]
    assert queries[1]["checkout"] == queries[2]["checkin"]
    assert queries[2]["checkout"] == queries[3]["checkin"]
    
    # Total nights should match
    total_nights = sum(q["nights"] for q in queries)
    assert total_nights == 13
