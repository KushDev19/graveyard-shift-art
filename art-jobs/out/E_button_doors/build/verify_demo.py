"""Screenshot emergency_demo.html at fixed times into a labelled contact sheet."""
import io, sys, pathlib
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(__file__).resolve().parent.parent
TIMES = [960, 1100, 1300, 1500]
dst = sys.argv[1] if len(sys.argv) > 1 else '/tmp/frames.png'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1300, 'height': 1000})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto((OUT / 'emergency_demo.html').as_uri())
    W, H, cols = 285, 265, 4
    sheet = Image.new('RGB', (W * cols, (H + 22) * ((len(TIMES) + cols - 1) // cols)), '#F4E6C8')
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(TIMES):
        pg.evaluate(f'renderAt({t})')
        im = Image.open(io.BytesIO(pg.query_selector('#stage').screenshot())).resize((W, H))
        x, y = (i % cols) * W, (i // cols) * (H + 22)
        sheet.paste(im, (x, y + 22)); d.text((x + 6, y + 5), f'{t} ms  theta={pg.evaluate(f"Math.round(stateAt({t}).theta)")}', fill='#2A1E35')
    sheet.save(dst)
    pg.evaluate('play(0,4000)'); pg.wait_for_timeout(1500)
    pg.evaluate('setDoors(true)'); pg.wait_for_timeout(800)
    pg.screenshot(path=dst.replace('.png', '_page.png'))
    print('page errors:', errs or 'none')
    b.close()
