import json
import unittest
from pathlib import Path

from src.build_configurator import build, load_data, markdown


class ConfiguratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.html = build()

    def test_html_embeds_all_flight_and_accommodation_options(self):
        self.assertNotIn("__TRIP_DATA__", self.html)
        payload_count = self.html.count('"price_total_eur"')
        self.assertEqual(payload_count, len(self.data["flight_options"]))
        self.assertIn('id="flightList"', self.html)
        self.assertIn('id="cascadeContent"', self.html)

    def test_html_contains_cascading_render_functions_and_sort_controls(self):
        for needle in (
            'id="flightSort"',
            'id="showAllFlights"',
            "function selectFlight",
            "function renderItinerary",
            "function renderStays",
            "function renderTransfers",
            "function renderBudget",
            "state.routeLocationIds",
        ):
            self.assertIn(needle, self.html)

    def test_price_bearing_flights_have_party_context_and_source(self):
        for flight in self.data["flight_options"]:
            if flight.get("price_total_eur") is not None:
                self.assertTrue(flight["search_url"].startswith("http"))
                self.assertIn("price_note", flight)
        self.assertEqual(self.data["trip"]["travellers"], 5)

    def test_markdown_uses_same_data_model(self):
        output = markdown(self.data)
        self.assertIn("## Letecké možnosti", output)
        self.assertIn("## Ubytovanie", output)
        self.assertIn("## Presuny", output)
        for flight in self.data["flight_options"]:
            self.assertIn(flight["label"], output)


if __name__ == "__main__":
    unittest.main()
