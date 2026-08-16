"""Tests for Google Flights URL encoder and search matrix generation."""
from datetime import date

from src.research.google_flights_encoder import (
    build_google_flights_url,
    generate_search_matrix,
    google_flights_tfs,
)
from src.research.schemas import FlightSearchSpace


def test_google_flights_tfs_encoding():
    """tfs encoding produces valid base64 string."""
    tfs = google_flights_tfs("VIE", "TYO", "2026-09-24", "2026-10-12", adults=5)
    
    assert isinstance(tfs, str)
    assert len(tfs) > 0
    # Should be valid base64
    import base64
    decoded = base64.b64decode(tfs)
    assert len(decoded) > 0


def test_google_flights_url_contains_required_params():
    """Generated URL contains all required query parameters."""
    url = build_google_flights_url(
        "VIE", "TYO", date(2026, 9, 24), date(2026, 10, 12), adults=5
    )
    
    assert "tfs=" in url
    assert "hl=en" in url
    assert "curr=EUR" in url
    assert url.startswith("https://www.google.com/travel/flights/search?")


def test_search_matrix_respects_date_windows():
    """Search matrix only generates combinations within specified windows."""
    space = FlightSearchSpace(
        origins=["VIE"],
        destinations=["TYO"],
        outbound_window=("2026-09-24", "2026-09-26"),
        return_window=("2026-10-10", "2026-10-12"),
        travellers=5,
    )
    
    matrix = generate_search_matrix(space)
    
    assert len(matrix) > 0
    for search in matrix:
        out_date = date.fromisoformat(search["outbound_date"])
        ret_date = date.fromisoformat(search["return_date"])
        
        assert date(2026, 9, 24) <= out_date <= date(2026, 9, 26)
        assert date(2026, 10, 10) <= ret_date <= date(2026, 10, 12)
        assert search["origin"] == "VIE"
        assert search["destination"] == "TYO"


def test_search_matrix_filters_unreasonable_trip_lengths():
    """Search matrix excludes trips shorter than 10 or longer than 25 nights."""
    space = FlightSearchSpace(
        origins=["VIE"],
        destinations=["TYO"],
        outbound_window=("2026-09-24", "2026-09-24"),
        return_window=("2026-09-26", "2026-09-26"),  # Only 2 nights
        travellers=5,
    )
    
    matrix = generate_search_matrix(space)
    
    # Should be empty since 2 nights < 10 night minimum
    assert len(matrix) == 0


def test_search_matrix_multi_origin_multi_destination():
    """Search matrix generates combinations for multiple origins and destinations."""
    space = FlightSearchSpace(
        origins=["VIE", "BUD"],
        destinations=["TYO", "OSA"],
        outbound_window=("2026-09-24", "2026-09-24"),
        return_window=("2026-10-12", "2026-10-12"),
        travellers=5,
    )
    
    matrix = generate_search_matrix(space)
    
    origins_found = {s["origin"] for s in matrix}
    destinations_found = {s["destination"] for s in matrix}
    
    assert origins_found == {"VIE", "BUD"}
    assert destinations_found == {"TYO", "OSA"}
    assert len(matrix) == 4  # 2 origins × 2 destinations × 1 date combo


def test_search_matrix_each_url_is_unique():
    """Every generated search has a unique, valid URL."""
    space = FlightSearchSpace(
        origins=["VIE"],
        destinations=["TYO"],
        outbound_window=("2026-09-24", "2026-09-26"),
        return_window=("2026-10-10", "2026-10-12"),
        travellers=5,
    )
    
    matrix = generate_search_matrix(space)
    urls = [s["url"] for s in matrix]
    
    assert len(urls) == len(set(urls))  # All unique
    for url in urls:
        assert url.startswith("https://www.google.com")
