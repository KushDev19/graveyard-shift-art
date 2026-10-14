"""PNG exports (each cosmetic at 1x puppet units, default grey, transparent) + labelled PREVIEW.png."""
import json
from lib import OUT, render
from wardrobe import sheet, puppet, COS
(OUT / 'png').mkdir(exist_ok=True)
for it in COS:
    for v in ('side', 'front'):
        if it[v]:
            f = it[v]['file']
            render(OUT / f, OUT / 'png' / f.replace('.svg', '.png'), it[v]['w'], it[v]['h'])
cells = []
for it in COS:
    svgs = []
    for v in ('side', 'front'):
        if it[v]:
            svgs.append((OUT / it[v]['file']).read_text().split('?>')[-1]
                        .replace('<svg ', '<svg style="width:150px;height:150px" ', 1))
    svgs.append(puppet('side', 'mustard', [it]))
    cells.append((f"{it['id']} ({it['slot']})", svgs))
sheet(OUT / 'PREVIEW.png', cells, 4, 120, 150, 'Job N: 8 toppers, 8 backpacks, 4 visors, 4 decals (item files + fitted on puppet)')
print('ok')
