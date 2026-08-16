"""Tests for flight search space schemas."""
import json
from datetime import date
from pathlib import Path

import pytest

from src.research.schemas import FlightSearchSpace, FlightObservation


def test_search_space_validates():
    """Search space JSON loads and validates correctly."""
    data = json.loads(Path("data/search_space.json").read_text())
    space = FlightSearchSpace(**data)
    
    assert len(space.origins) >= 1
    assert space.travellers == 5
    assert space.cabin == "economy"
    assert space.carry_on_only is True


def test_search_space_date_parsing():
    """Date parsing helpers work correctly."""
    space = FlightSearchSpace(
        origins=["VIE"],
        destinations=["TYO"],
        outbound_window=("2026-09-24", "2026-09-26"),
        return_window=("2026-10-10", "2026-10-12"),
        travellers=5,
    )
    
    out_start, out_end = space.outbound_dates()
    assert out_start == date(2026, 9, 24)
    assert out_end == date(2026, 9, 26)
    
    ret_start, ret_end = space.return_dates()
    assert ret_start == date(2026, 10, 10)


def test_flight_observation_nights_calculation():
    """Flight observation calculates nights correctly."""
    obs = FlightObservation(
        search_id="VIE-TYO-2026-09-24-2026-10-12",
        origin="VIE",
        destination="TYO",
        outbound_date="2026-09-24",
        return_date="2026-10-12",
        price_total_eur=5000.0,
        travellers=5,
        search_url="https://example.com",
        observed_at="2026-08-16T10:00:00Z",
        provider="test",
    )
    
    assert obs.nights() == 18


def test_flight_observation_without_price():
    """Flight observation validates even without price (blocked source)."""
    obs = FlightObservation(
        search_id="VIE-TYO-2026-09-24-2026-10-12",
        origin="VIE",
        destination="TYO",
        outbound_date="2026-09-24",
        return_date="2026-10-12",
        price_total_eur=None,
        travellers=5,
        search_url="https://example.com",
        observed_at="2026-08-16T10:00:00Z",
        provider="test",
    )
    
    assert obs.price_total_eur is None
    assert obs.nights() == 18
