from __future__ import annotations

from html import escape
from pathlib import Path

from .utils import ensure_dirs, write_text


def write_svg_card(path: Path, title: str, lines: list[str]) -> None:
    ensure_dirs(path.parent)
    body = []
    y = 90
    for line in lines:
        body.append(
            f'<text x="40" y="{y}" font-family="Consolas, monospace" font-size="20" fill="#0f172a">{escape(line)}</text>'
        )
        y += 34
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{max(300, y + 40)}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <rect x="20" y="20" width="1560" height="{max(240, y)}" rx="16" fill="#ffffff" stroke="#cbd5e1"/>
  <text x="40" y="60" font-family="Segoe UI, Arial, sans-serif" font-size="28" font-weight="700" fill="#0f172a">{escape(title)}</text>
  {''.join(body)}
</svg>
'''
    write_text(path, svg)
