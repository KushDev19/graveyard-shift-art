import sys, pathlib
from playwright.sync_api import sync_playwright
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
core=pathlib.Path('emergency_core.js').read_text()
out=sys.argv[1]
html=f"""<html><body style='margin:0;background:#3D2A4F'><div id=r style='display:flex'></div><script>{core}
for (const k of ['idle','open','pressed','disabled']) document.getElementById('r').insertAdjacentHTML('beforeend', EB.svg(EB.STATES[k],{{P:k}}));</script></body></html>"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH); pg=b.new_page(viewport={'width':2280,'height':530})
    pg.set_content(html); pg.screenshot(path=out); b.close()
