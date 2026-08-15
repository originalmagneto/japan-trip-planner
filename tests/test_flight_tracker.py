import csv
import tempfile
import unittest
from pathlib import Path

from src.flight_tracker import load_observations, cheapest_valid


class FlightTrackerTests(unittest.TestCase):
    def test_load_observations_and_find_cheapest_five_passenger_offer(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'flights.csv'
            path.write_text(
                'observed_at,origin,destination,departure_date,return_date,passengers,stops,airlines,price_eur,carry_on_included,booking_url,source,notes\n'
                '2026-08-15,VIE,TYO,2026-09-24,2026-10-12,5,1,Test Air,720,yes,https://a,manual,good\n'
                '2026-08-15,BUD,TYO,2026-09-24,2026-10-12,4,1,Test Air,500,yes,https://b,bad,wrong group\n'
                '2026-08-15,BUD,TYO,2026-09-24,2026-10-12,5,2,Test Air,680,yes,https://c,manual,cheapest\n',
                encoding='utf-8',
            )
            rows = load_observations(path)
            result = cheapest_valid(rows, passengers=5)
            self.assertEqual(result['price_eur'], 680.0)
            self.assertEqual(result['booking_url'], 'https://c')

    def test_missing_url_is_not_valid(self):
        self.assertIsNone(cheapest_valid([{'passengers': '5', 'price_eur': '600', 'booking_url': ''}], 5))


if __name__ == '__main__':
    unittest.main()
