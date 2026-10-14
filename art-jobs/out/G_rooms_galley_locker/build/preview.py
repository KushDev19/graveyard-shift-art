"""Step 5: PREVIEW.png (both rooms + every object, labeled, on cream) and the MAE table for REPORT.md."""
import json

from PIL import Image, ImageDraw

from tracelib import OUT, font

CREAM = (244, 230, 200)
INK = (42, 30, 53)


def main():
    rooms = ["galley", "locker"]
    W = 2400
    tiles = []
    for r in rooms:
        sc = json.loads((OUT / f"build/scores_{r}.json").read_text())
        files = [(k, v) for k, v in sc.items() if isinstance(v, dict) and k not in ("shell", "room")]
        if r == "locker":
            files += [("locker_door_closed", dict(file="objects/locker_door_closed.svg")),
                      ("locker_door_open", dict(file="objects/locker_door_open.svg")),
                      ("locker_clock_hand_hour", dict(file="objects/locker_clock_hand_hour.svg")),
                      ("locker_clock_hand_minute", dict(file="objects/locker_clock_hand_minute.svg"))]
        tiles.append((r, files, sc))
    # layout
    rows = []
    y = 20
    canvas_parts = []
    for r, files, sc in tiles:
        room = Image.open(OUT / f"{r}_room.png").convert("RGB")
        shell = Image.open(OUT / f"{r}_shell.png").convert("RGBA")
        lights = Image.open(OUT / f"{r}_lights.png").convert("RGBA")
        tw = (W - 60) // 3
        th = int(room.height * tw / room.width)
        canvas_parts.append(("label", f"{r.upper()}  (room MAE {sc['room']['mae']})", 20, y))
        y += 50
        for i, (lab, im) in enumerate([("composite", room), ("shell (lights off)", shell), ("lights layer", lights)]):
            canvas_parts.append(("img", im.resize((tw, th)), 20 + i * (tw + 10), y, lab))
        y += th + 50
        x = 20
        rowh = 0
        for name, v in files:
            p = OUT / v["file"].replace(".svg", ".png")
            im = Image.open(p).convert("RGBA")
            s = min(1.0, 260 / im.height, 300 / im.width)
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))
            if x + max(im.width, 150) > W - 20:
                x = 20
                y += rowh + 50
                rowh = 0
            lab = name.replace(f"{r}_", "") + (f"  {v['mae']}" if "mae" in v else "")
            canvas_parts.append(("img", im, x, y, lab))
            x += max(im.width, 170) + 20
            rowh = max(rowh, im.height)
        y += rowh + 70
    can = Image.new("RGB", (W, y), CREAM)
    d = ImageDraw.Draw(can)
    for p in canvas_parts:
        if p[0] == "label":
            d.text((p[2], p[3]), p[1], fill=INK, font=font(34))
        else:
            _, im, x, yy, lab = p
            if im.mode == "RGBA":
                can.paste(im, (x, yy), im)
            else:
                can.paste(im, (x, yy))
            d.text((x, yy + im.height + 6), lab, fill=INK, font=font(18))
    can.save(OUT / "PREVIEW.png", optimize=True)
    print("PREVIEW", can.size)


if __name__ == "__main__":
    main()
