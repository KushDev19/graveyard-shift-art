import sys
from PIL import Image
fs = sys.argv[2:]; H = int(sys.argv[1])
ims = [Image.open(f) for f in fs]
ims = [i.resize((int(i.width * H / i.height), H)) for i in ims]
W = 1900; rows = []; row = []; x = 0
for i in ims:
    if x + i.width > W and row: rows.append(row); row = []; x = 0
    row.append(i); x += i.width + 8
rows.append(row)
out = Image.new('RGB', (W, len(rows) * (H + 8)), (30, 30, 30))
for r, rw in enumerate(rows):
    x = 0
    for i in rw: out.paste(i, (x, r * (H + 8))); x += i.width + 8
out.save('/tmp/claude-0/v.png')
