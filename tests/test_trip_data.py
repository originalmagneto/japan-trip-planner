import json
import unittest
from pathlib import Path

from src.build_configurator import markdown, load_data


class TripDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path('data/trip_data.json').read_text(encoding='utf-8'))

    def test_five_travellers_and_four_flight_options(self):
        self.assertEqual(self.data['trip']['travellers'], 5)
        self.assertGreaterEqual(len(self.data['flight_options']), 4)

    def test_core_locations_have_pois_activities_weather_and_maps(self):
        ids = {x['id'] for x in self.data['locations']}
        self.assertTrue({'tokyo', 'kyoto', 'osaka'} <= ids)
        for location in self.data['locations']:
            self.assertTrue(location['pois'])
            self.assertTrue(location['activities'])
            self.assertIn('weather', location)
            self.assertTrue(location['map_url'].startswith('http'))

    def test_markdown_contains_transfer_purchase_links(self):
        output = markdown(load_data())
        self.assertIn('## Presuny', output)
        self.assertIn('kúpiť/info', output)
        self.assertIn('Fushimi Inari', output)

    def test_accommodation_data_has_verified_tokyo_and_exact_two_room_kyoto_options(self):
        data = load_data()
        verified_tokyo = [x for x in data['accommodations'] if x['city'] == 'Tokyo' and x['verified']]
        exact_kyoto = [x for x in data['accommodations'] if x['city'] == 'Kyoto' and x['two_rooms_exact'] and x['verified']]
        self.assertGreaterEqual(len(verified_tokyo), 4)
        self.assertGreaterEqual(len(exact_kyoto), 2)


if __name__ == '__main__':
    unittest.main()
