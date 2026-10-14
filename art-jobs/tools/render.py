"""Portable SVG -> PNG renderer for the art jobs (Linux/Windows/macOS).
Usage: python art-jobs/tools/render.py in.svg out.png [width]
Tries, in order: cairosvg, rsvg-convert, inkscape, playwright (headless Chromium).
Transparent background is preserved. Note: cairosvg does not support CSS var(); playwright does."""
import pathlib
import shutil
import subprocess
import sys


def render(svg, png, width=None):
    svg, png = pathlib.Path(svg), pathlib.Path(png)
    png.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=width)
        return "cairosvg"
    except Exception as e:  # noqa: BLE001
        errors.append(f"cairosvg: {e}")
    if shutil.which("rsvg-convert"):
        cmd = ["rsvg-convert", "-o", str(png), str(svg)] + (["-w", str(width)] if width else [])
        if subprocess.run(cmd).returncode == 0:
            return "rsvg-convert"
    if shutil.which("inkscape"):
        cmd = ["inkscape", str(svg), "-o", str(png)] + ([f"--export-width={width}"] if width else [])
        if subprocess.run(cmd).returncode == 0:
            return "inkscape"
    try:
        from playwright.sync_api import sync_playwright
        text = svg.read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": width or 1024, "height": 1024})
            page.set_content(f"<body style='margin:0;background:transparent'>{text}</body>")
            el = page.query_selector("svg")
            if width:
                el.evaluate("(e, w) => { e.setAttribute('width', w); e.removeAttribute('height'); }", width)
            el.screenshot(path=str(png), omit_background=True)
            b.close()
        return "playwright"
    except Exception as e:  # noqa: BLE001
        errors.append(f"playwright: {e}")
    raise SystemExit("No SVG renderer worked:\n" + "\n".join(errors) +
                     "\nTry: pip install cairosvg (after apt-get install -y libcairo2), or pip install playwright && playwright install chromium")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    print("rendered with", render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None))
