"""Google Flights scraper with rate limiting.

NOTE: This module is designed to be called by Hermes Agent, which has
browser_exec() available. It cannot be run standalone as a Python script.
"""
import json
import time
from datetime import datetime
from pathlib import Path

from .schemas import FlightObservation


def create_search_observation(
    search: dict,
    price_total_eur: float | None,
    travellers: int = 5,
) -> FlightObservation:
    """Create a FlightObservation from search metadata and scraped price."""
    return FlightObservation(
        search_id=f"{search['origin']}-{search['destination']}-{search['outbound_date']}-{search['return_date']}",
        origin=search['origin'],
        destination=search['destination'],
        outbound_date=search['outbound_date'],
        return_date=search['return_date'],
        price_total_eur=price_total_eur,
        price_per_person_eur=price_total_eur / travellers if price_total_eur else None,
        travellers=travellers,
        verified=False,
        search_url=search['url'],
        observed_at=datetime.utcnow().isoformat() + 'Z',
        provider='google_flights',
    )


def scrape_google_flights_batch(
    searches: list[dict],
    output_path: Path,
    delay_seconds: int = 10,
    max_searches: int | None = None,
) -> list[FlightObservation]:
    """Scrape multiple Google Flights searches with rate limiting.
    
    Appends observations to JSONL file and returns list of successful observations.
    """
    if max_searches:
        searches = searches[:max_searches]
    
    observations = []
    
    for i, search in enumerate(searches):
        print(f"[{i+1}/{len(searches)}] {search['origin']} → {search['destination']} | {search['outbound_date']} ({search['nights']}n)")
        
        obs = scrape_google_flights_single(search, delay_after=delay_seconds)
        
        if obs:
            observations.append(obs)
            
            # Append to JSONL immediately (crash-safe)
            with output_path.open('a') as f:
                f.write(obs.model_dump_json() + '\n')
            
            print(f"   ✓ {obs.price_total_eur:.0f} EUR ({obs.price_per_person_eur:.0f} EUR/person)")
        else:
            print(f"   ✗ No price found")
    
    return observations


def load_observations_from_jsonl(jsonl_path: Path) -> list[FlightObservation]:
    """Load all observations from JSONL file."""
    if not jsonl_path.exists():
        return []
    
    observations = []
    for line in jsonl_path.read_text().strip().split('\n'):
        if line:
            observations.append(FlightObservation.model_validate_json(line))
    
    return observations
