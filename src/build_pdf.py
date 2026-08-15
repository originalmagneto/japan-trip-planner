#!/usr/bin/env python3
"""Create a readable PDF from the project's Markdown itinerary."""
from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if Path(FONT).exists():
    pdfmetrics.registerFont(TTFont('DejaVu', FONT))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', FONT_BOLD))
    BASE, BOLD = 'DejaVu', 'DejaVu-Bold'
else:
    BASE, BOLD = 'Helvetica', 'Helvetica-Bold'


def inline_markup(text: str) -> str:
    text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', text)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return text


def build_pdf_bytes(markdown: str) -> bytes:
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TripBody', parent=styles['BodyText'], fontName=BASE, fontSize=9.5, leading=13, spaceAfter=4))
    styles.add(ParagraphStyle(name='TripH1', parent=styles['Heading1'], fontName=BOLD, fontSize=18, leading=22, spaceAfter=10))
    styles.add(ParagraphStyle(name='TripH2', parent=styles['Heading2'], fontName=BOLD, fontSize=13, leading=16, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name='TripH3', parent=styles['Heading3'], fontName=BOLD, fontSize=11, leading=14, spaceBefore=6, spaceAfter=3))
    story = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 3))
        elif line.startswith('### '):
            story.append(Paragraph(inline_markup(line[4:]), styles['TripH3']))
        elif line.startswith('## '):
            story.append(Paragraph(inline_markup(line[3:]), styles['TripH2']))
        elif line.startswith('# '):
            story.append(Paragraph(inline_markup(line[2:]), styles['TripH1']))
        elif line.startswith('- '):
            story.append(Paragraph('• ' + inline_markup(line[2:]), styles['TripBody']))
        elif line.startswith('|') or line.startswith('---'):
            # Markdown tables are represented as readable pipe-separated text.
            if not line.startswith('---'):
                story.append(Paragraph(inline_markup(line.replace('|', '  |  ')), styles['TripBody']))
        else:
            story.append(Paragraph(inline_markup(line), styles['TripBody']))
    doc.build(story)
    return stream.getvalue()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    doc_names = ['itinerary.md', 'day-by-day.md', 'accommodation.md', 'transport.md', 'budget.md', 'flight-options.md']
    markdown = '\n\n'.join((root / 'docs' / name).read_text(encoding='utf-8') for name in doc_names)
    output = root / 'outputs/japan-trip-planner.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(build_pdf_bytes(markdown))
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
