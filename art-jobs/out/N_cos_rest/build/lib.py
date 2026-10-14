"""Shared helpers for job N: Chromium rendering (supports var() and filters) and MAE checks."""
import pathlib, re
from PIL import Image
import numpy as np

CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parents[1]
_pw = _br = _pg = None


def page():
    global _pw, _br, _pg
    if _pg is None:
        from playwright.sync_api import sync_playwright
        _pw = sync_playwright().start()
        _br = _pw.chromium.launch(executable_path=CHROME)
        _pg = _br.new_page()
    return _pg


def render(svg, png, width, height, bg='transparent', css=''):
    """Render an SVG (path or markup) into a width x height PNG, scaling the viewBox to fit."""
    if isinstance(svg, (str, pathlib.Path)) and str(svg).endswith('.svg'):
        svg = pathlib.Path(svg).read_text()
    svg = re.sub(r'(<svg\b[^>]*?)\s(width|height)="[^"]*"', r'\1', svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\s(width|height)="[^"]*"', r'\1', svg, count=1)
    svg = svg.replace('<svg ', f'<svg width="{width}" height="{height}" ', 1)
    html = (f'<html><head><style>html,body{{margin:0;background:{bg}}}svg{{display:block}}{css}</style></head>'
            f'<body>{svg}</body></html>')
    p = page()
    p.set_viewport_size({'width': int(width), 'height': int(height)})
    p.set_content(html)
    p.screenshot(path=str(png), omit_background=(bg == 'transparent'),
                 clip={'x': 0, 'y': 0, 'width': int(width), 'height': int(height)})
    return png


def mae(a, b, mask=None, down=4):
    """Mean absolute error (0-255) between two RGB images on a 4x downscale, optionally masked."""
    w, h = a.size
    a = np.asarray(a.convert('RGB').resize((w // down, h // down), Image.LANCZOS)).astype(float)
    b = np.asarray(b.convert('RGB').resize((w // down, h // down), Image.LANCZOS)).astype(float)
    d = np.abs(a - b).mean(2)
    if mask is not None:
        m = np.asarray(mask.convert('L').resize((w // down, h // down))) > 127
        return float(d[m].mean())
    return float(d.mean())
