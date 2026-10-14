import json, os, io, numpy as np, cairosvg, re
from PIL import Image, ImageDraw, ImageFont
import build
from build import build as bld, compose, NAMES, OUT, meta, layers
from trace import trace
cos,res=bld()
# ---- cosmetics.json
for e in cos:
    for v in ('side','front'):
        for k in ('x','y'): e[v][k]=round(e[v][k],1)
        if 'back' in e[v]:
            for k in ('x','y'): e[v]['back'][k]=round(e[v]['back'][k],1)
doc={'note':'Hats for crew_puppet.svg (viewBox 640x800). Draw file with its top-left at (x,y) in puppet units, '
 'same scale as the puppet. pivot = the dome centre (320,300) in file-local units: rotate/bob the hat with the head around it. '
 'Side view faces right (mirror the whole puppet+hat for left). Z-order: back layer before #dome (side) / before #f_leg_l (front); '
 'front file after #collar, before #arm_front (side) / before #f_arm_l (front). hidesAntenna: hide #antenna / #f_antenna.',
 'slot':'hat','items':cos}
json.dump(doc,open(OUT+'cosmetics.json','w'),indent=1)
# ---- 2x PNG exports
os.makedirs(OUT+'png',exist_ok=True)
for f in sorted(os.listdir(OUT+'svg')):
    svg=open(OUT+'svg/'+f).read(); w=float(re.search(r'width="([\d.]+)"',svg).group(1))
    cairosvg.svg2png(bytestring=svg.encode(),write_to=OUT+'png/'+f[:-4]+'@2x.png',output_width=int(w*2))
# ---- fidelity: traced front layer vs original pixels (4x downscale of the source crop, opaque region)
src={s:np.asarray(Image.open('/home/user/graveyard-shift-art/raw_originals/'+s).convert('RGB')).astype(float) for s in ('43A_COS_HATS_A.png','43B_COS_HATS_B.png')}
mae={}
for k,m in meta.items():
    L=layers(k); img=L['front']; paths,kk=trace(img)
    w,h=img.size; pal=m['palette']+['#3A2227','#2D1E3A']
    body=''.join(f'<path fill="{build.nearest(f,pal)}" transform="translate({tx:g},{ty:g})" d="{d}"/>' for f,d,tx,ty in paths)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w/kk:g} {h/kk:g}" width="{w//4}" height="{h//4}">{body}</svg>'
    r=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA').resize((w//4,h//4))
    ox,oy=m['origin']; o=Image.fromarray(src[m['sheet']][oy:oy+h,ox:ox+w].astype(np.uint8)).resize((w//4,h//4),Image.BOX)
    a=np.asarray(img.resize((w//4,h//4),Image.BOX))[...,3]>250
    rr=np.asarray(r).astype(float)
    mae[k]=float(np.abs(rr[...,:3]-np.asarray(o).astype(float))[a].mean())
json.dump(mae,open('mae.json','w'),indent=1)
print({k:round(v,1) for k,v in mae.items()})
# ---- wardrobe preview: each hat row = side+front x 3 colours
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(F,26) if os.path.exists(F) else ImageFont.load_default()
COL=[('tomato','#E4483C'),('sky','#6EC3F0'),('mint','#6FD6B0')]
W=250; H=int(W*1020/800); cols=4
names=list(NAMES)
cell_w=W*6; S=Image.new('RGB',(cell_w*2+40,(H+50)*6+20),(244,230,200)); d=ImageDraw.Draw(S)
for i,n in enumerate(names):
    cx=20+(i%2)*cell_w; cy=10+(i//2)*(H+50)
    d.text((cx+10,cy),NAMES[n],fill=(45,30,58),font=font)
    for j,(cn,c) in enumerate(COL):
        for t,v in enumerate(('side','front')):
            im=compose(res,n,v,c,W/800); S.paste(im,(cx+(j*2+t)*W,cy+40),im)
S.save(OUT+'wardrobe_preview.png',optimize=True)
# ---- PREVIEW: every SVG labelled on cream
fs=sorted(f for f in os.listdir(OUT+'png'))
tw=300; P=Image.new('RGB',(tw*6,((len(fs)+5)//6)*(tw+40)),(244,230,200)); d=ImageDraw.Draw(P)
sm=ImageFont.truetype(F,15) if os.path.exists(F) else font
for i,f in enumerate(fs):
    im=Image.open(OUT+'png/'+f); im.thumbnail((tw-30,tw-30))
    x=(i%6)*tw; y=(i//6)*(tw+40)
    P.paste(im,(x+(tw-im.width)//2,y+10+(tw-30-im.height)//2),im)
    d.text((x+10,y+tw-10),f.replace('@2x.png','.svg'),fill=(45,30,58),font=sm)
P.save(OUT+'PREVIEW.png',optimize=True)
