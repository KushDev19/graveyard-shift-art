"""PREVIEW.png: every deliverable labelled on cream."""
import pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(__file__).resolve().parent.parent
cell = lambda f, label, h: f'<figure><img src="{f}" style="height:{h}px"><figcaption>{label}</figcaption></figure>'
row1 = ''.join(cell(f'emergency_button_{s}.png', f'button · {s}', 260) for s in ['idle', 'open', 'pressed', 'disabled'])
row2 = cell('parts/dome_back_strip.png', 'parts/dome_back_strip.png (0-120°, 13 frames)', 120) + cell('parts/dome_front_strip.png', 'parts/dome_front_strip.png', 120)
row3 = ''.join(cell(f + '.png', f, 330) for f in ['door_front_closed', 'door_front_open', 'door_side_closed', 'door_side_open', 'door_side_r_closed', 'door_side_r_open'])
html = f"""<html><body style="margin:0;background:#F4E6C8;font:600 15px system-ui,sans-serif;color:#2A1E35;padding:18px;width:1640px">
<style>.r{{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end;margin-bottom:16px}}figure{{margin:0;text-align:center}}
figcaption{{margin-top:4px}}h1{{margin:0 0 10px;font-size:22px;letter-spacing:.05em}}</style>
<h1>JOB E · EMERGENCY BUTTON + DOORS</h1><div class=r>{row1}</div><div class=r>{row2}</div><div class=r>{row3}</div></body></html>"""
(OUT / '_preview.html').write_text(html)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1676, 'height': 800}); pg.goto((OUT / '_preview.html').as_uri())
    pg.screenshot(path=str(OUT / 'PREVIEW.png'), full_page=True); b.close()
(OUT / '_preview.html').unlink()
