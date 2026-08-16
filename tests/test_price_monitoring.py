"""Tests for price monitoring."""
import json
from pathlib import Path

from src.monitoring.price_watch import (
    add_flight_to_watch,
    remove_flight_from_watch,
    load_watch_list,
    record_price_history,
)


def test_add_flight_to_watch(tmp_path):
    """Can add a flight to watch list."""
    # Use temp file for testing
    import src.monitoring.price_watch as pw
    pw.WATCH_FILE = tmp_path / "watch.json"
    
    add_flight_to_watch("f1", "https://example.com/flight", target_price=5000)
    
    watches = load_watch_list()
    assert len(watches) == 1
    assert watches[0]["flight_id"] == "f1"
    assert watches[0]["target_price_eur"] == 5000


def test_remove_flight_from_watch(tmp_path):
    """Can remove a flight from watch list."""
    import src.monitoring.price_watch as pw
    pw.WATCH_FILE = tmp_path / "watch.json"
    
    add_flight_to_watch("f1", "https://example.com/flight")
    add_flight_to_watch("f2", "https://example.com/flight2")
    
    remove_flight_from_watch("f1")
    
    watches = load_watch_list()
    assert len(watches) == 1
    assert watches[0]["flight_id"] == "f2"


def test_record_price_history(tmp_path):
    """Price history is appended to JSONL."""
    import src.monitoring.price_watch as pw
    pw.HISTORY_FILE = tmp_path / "history.jsonl"
    
    record_price_history("f1", 5000, "https://example.com")
    record_price_history("f1", 4800, "https://example.com")
    
    lines = pw.HISTORY_FILE.read_text().strip().split("\n")
    assert len(lines) == 2
    
    first = json.loads(lines[0])
    assert first["flight_id"] == "f1"
    assert first["price_eur"] == 5000


def test_watch_list_prevents_duplicates(tmp_path):
    """Cannot add same flight twice."""
    import src.monitoring.price_watch as pw
    pw.WATCH_FILE = tmp_path / "watch.json"
    
    add_flight_to_watch("f1", "https://example.com/flight")
    add_flight_to_watch("f1", "https://example.com/flight")
    
    watches = load_watch_list()
    assert len(watches) == 1
