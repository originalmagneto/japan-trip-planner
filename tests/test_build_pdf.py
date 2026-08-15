import unittest

from src.build_pdf import build_pdf_bytes


class PdfBuildTests(unittest.TestCase):
    def test_pdf_starts_with_pdf_signature_and_contains_pages(self):
        data = build_pdf_bytes('# Japan Trip Planner\n\nMajo\n')
        self.assertTrue(data.startswith(b'%PDF-'))
        self.assertIn(b'/Type /Page', data)


if __name__ == '__main__':
    unittest.main()
