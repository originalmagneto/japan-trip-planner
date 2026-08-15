#!/usr/bin/env python3
"""Build a self-contained HTML travel book from Markdown documents."""
from __future__ import annotations

import html
from pathlib import Path
import re


def markdown_to_html(text: str) -> str:
    out = []
    in_table = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if in_table:
                out.append('</table>')
                in_table = False
            continue
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(set(c) <= {'-', ':'} for c in cells):
                continue
            if not in_table:
                out.append('<table>')
                in_table = True
            tag = 'th' if not any('<tr>' in x for x in out[-2:]) else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{html.escape(c)}</{tag}>' for c in cells) + '</tr>')
            continue
        if in_table:
            out.append('</table>')
            in_table = False
        escaped = html.escape(line)
        escaped = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', escaped)
        escaped = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', escaped)
        if line.startswith('### '): out.append(f'<h3>{escaped[4:]}</h3>')
        elif line.startswith('## '): out.append(f'<h2>{escaped[3:]}</h2>')
        elif line.startswith('# '): out.append(f'<h1>{escaped[2:]}</h1>')
        elif line.startswith('- '): out.append(f'<li>{escaped[2:]}</li>')
        else: out.append(f'<p>{escaped}</p>')
    if in_table: out.append('</table>')
    return '\n'.join(out)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    docs = ['itinerary.md', 'day-by-day.md', 'accommodation.md', 'transport.md', 'budget.md', 'flight-options.md']
    sections = [markdown_to_html((root / 'docs' / name).read_text(encoding='utf-8')) for name in docs]
    document = '''<!doctype html><html lang="sk"><head><meta charset="utf-8"><title>Japan Trip Planner</title>
<style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.55;color:#202124}h1{color:#8b1e3f;border-bottom:2px solid #8b1e3f;padding-bottom:.4rem}h2{margin-top:2rem;color:#334e68}h3{color:#486581}table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #bcccdc;padding:.45rem;text-align:left}th{background:#e6eef5}a{color:#1261a0}li{margin:.25rem 0}</style></head><body>'''
    document += '\n<hr>\n'.join(sections) + '</body></html>'
    output = root / 'outputs/japan-trip-planner.html'
    output.write_text(document, encoding='utf-8')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
