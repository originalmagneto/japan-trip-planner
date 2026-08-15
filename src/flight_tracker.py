#!/usr/bin/env python3
"""Small, dependency-free tracker for manually captured flight observations."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterable


def load_observations(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def cheapest_valid(rows: Iterable[dict[str, str]], passengers: int = 5) -> dict[str, str | float] | None:
    valid = []
    for row in rows:
        try:
            count = int(row.get('passengers', '0'))
            price = float(row.get('price_eur', ''))
        except (TypeError, ValueError):
            continue
        if count == passengers and row.get('booking_url', '').strip() and price > 0:
            item = dict(row)
            item['price_eur'] = price
            valid.append(item)
    return min(valid, key=lambda row: float(row['price_eur'])) if valid else None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / 'data/raw/flight-observations.csv'
    rows = load_observations(path)
    if len(sys.argv) == 2 and sys.argv[1] == 'summary':
        best = cheapest_valid(rows, passengers=5)
        if not best:
            print('No valid observations yet. Add a row to data/raw/flight-observations.csv.')
            return 0
        print(f"Best: {best['origin']} → {best['destination']} | {best['price_eur']:.2f} EUR total | {best['booking_url']}")
        return 0
    print('Usage: python3 src/flight_tracker.py summary')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
