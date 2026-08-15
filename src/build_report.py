#!/usr/bin/env python3
"""Generate a compact Markdown summary from captured flight observations."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def render_summary(rows: Iterable[dict[str, str]]) -> str:
    valid = []
    for row in rows:
        try:
            price = float(row.get('price_eur', ''))
        except (TypeError, ValueError):
            continue
        if price > 0 and row.get('booking_url', '').strip():
            valid.append((price, row))
    if not valid:
        return '# Flight observations\n\nNo valid flight observations yet.\n'
    price, row = min(valid, key=lambda item: item[0])
    return (
        '# Flight observations\n\n'
        f"Best recorded offer: **{price:.2f} EUR** total ({price / 5:.2f} EUR/person).\n\n"
        f"Route: {row.get('origin', '?')} → {row.get('destination', '?')}\n\n"
        f"Booking/search link: {row['booking_url']}\n"
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source = root / 'data/raw/flight-observations.csv'
    output = root / 'outputs/flight-summary.md'
    with source.open(newline='', encoding='utf-8') as handle:
        text = render_summary(csv.DictReader(handle))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
