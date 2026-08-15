import tempfile
import unittest
from pathlib import Path

from src.build_report import render_summary


class ReportTests(unittest.TestCase):
    def test_render_summary_reports_empty_observations(self):
        text = render_summary([])
        self.assertIn('No valid flight observations', text)

    def test_render_summary_reports_best_offer(self):
        text = render_summary([{'origin': 'VIE', 'destination': 'TYO', 'price_eur': '650', 'booking_url': 'https://example.com'}])
        self.assertIn('650.00 EUR', text)
        self.assertIn('https://example.com', text)


if __name__ == '__main__':
    unittest.main()
