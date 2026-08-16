"""Tests for dynamic itinerary variant generator."""
from src.itinerary import generate_route_variants, normalize_city_code


def test_normalize_city_code():
    """City code normalization works for all variants."""
    assert normalize_city_code("TYO") == "Tokyo"
    assert normalize_city_code("HND") == "Tokyo"
    assert normalize_city_code("NRT") == "Tokyo"
    assert normalize_city_code("OSA") == "Osaka"
    assert normalize_city_code("KIX") == "Osaka"
    assert normalize_city_code("Tokyo") == "Tokyo"


def test_tokyo_tokyo_round_trip():
    """Tokyo round-trip generates classic route."""
    variant = generate_route_variants("Tokyo", "Tokyo", 18)
    
    assert variant["route"] == ["Tokyo", "Kanazawa", "Kyoto", "Osaka"]
    assert variant["total_nights"] == 18
    assert variant["arrival_city"] == "Tokyo"
    assert variant["departure_city"] == "Tokyo"
    assert sum(variant["nights"].values()) == 18


def test_osaka_osaka_round_trip():
    """Osaka round-trip generates reverse route."""
    variant = generate_route_variants("Osaka", "Osaka", 18)
    
    assert variant["route"] == ["Osaka", "Kyoto", "Kanazawa", "Tokyo"]
    assert variant["total_nights"] == 18
    assert sum(variant["nights"].values()) == 18


def test_tokyo_osaka_open_jaw():
    """Tokyo → Osaka open-jaw generates west-bound route."""
    variant = generate_route_variants("Tokyo", "Osaka", 18)
    
    assert variant["route"] == ["Tokyo", "Kanazawa", "Kyoto", "Osaka"]
    assert variant["arrival_city"] == "Tokyo"
    assert variant["departure_city"] == "Osaka"
    assert variant["total_nights"] == 18


def test_osaka_tokyo_open_jaw():
    """Osaka → Tokyo open-jaw generates east-bound route."""
    variant = generate_route_variants("Osaka", "Tokyo", 18)
    
    assert variant["route"] == ["Osaka", "Kyoto", "Kanazawa", "Tokyo"]
    assert variant["arrival_city"] == "Osaka"
    assert variant["departure_city"] == "Tokyo"


def test_night_allocation_respects_minimums():
    """Night allocation never goes below location minimum."""
    variant = generate_route_variants("Tokyo", "Osaka", 12)
    
    for city in variant["route"]:
        # Each location should have at least its minimum
        from src.itinerary import LOCATION_DB
        assert variant["nights"][city] >= LOCATION_DB[city]["nights_min"]


def test_night_allocation_matches_total():
    """Allocated nights always equal requested total."""
    for total in [12, 15, 18, 21]:
        variant = generate_route_variants("Tokyo", "Osaka", total)
        assert sum(variant["nights"].values()) == total


def test_airport_code_handling():
    """Airport codes are correctly normalized."""
    variant1 = generate_route_variants("TYO", "OSA", 18)
    variant2 = generate_route_variants("HND", "KIX", 18)
    
    assert variant1["arrival_city"] == "Tokyo"
    assert variant1["departure_city"] == "Osaka"
    assert variant2["arrival_city"] == "Tokyo"
    assert variant2["departure_city"] == "Osaka"
    
    # Should generate same route
    assert variant1["route"] == variant2["route"]
