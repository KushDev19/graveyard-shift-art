import json, math, os, sys, numpy as np, cv2
from PIL import Image
from trace import trace
from puppet import puppet, render
meta=json.load(open('meta.json'))
OUT='/home/user/graveyard-shift-art/art-jobs/out/M_cos_hats/'; os.makedirs(OUT+'svg',exist_ok=True)
NAMES={'trucker':'Trucker cap','diner':'Diner hat','hardhat':'Hard hat','beanie':'Beanie','cowboy':'Cowboy hat','chef':'Chef toque',
 'nightcap':'Nightcap','party':'Party hat','headphones':'Headphones','flowercrown':'Flower crown','afro':'Afro','propeller':'Propeller beanie'}
WRAP={'headphones','flowercrown','afro'}
# 43A placement: crop bottom-centre -> (ox,oy) in puppet units, scale s, rotation rot (deg)
A=json.load(open('place.json'))
def place43b(k):
    m=meta[k]; hx,hy,hw,hh=m['helmet_bbox']; t=A.get(k,{})
    w=t.get('w',hw); cx=t.get('cx',hx+hw/2)
    top=t.get('top', hy if t.get('top_visible') else hy+hh-0.866*w)
    s=404/w
    return dict(s=s*t.get('k',1), ax=cx, ay=top, ox=320+t.get('dx',0), oy=109+t.get('dy',0), rot=t.get('rot',0))
def place43a(k):
    m=meta[k]; w,h=m['size']; t=A[k]
    return dict(s=t['s'], ax=w/2, ay=h-24, ox=t['ox'], oy=t['oy'], rot=t.get('rot',0))
def nearest(fill,pal):
    c=np.array([int(fill[i:i+2],16) for i in (1,3,5)])
    P=np.array([[int(p[i:i+2],16) for i in (1,3,5)] for p in pal])
    return pal[int(np.argmin(np.linalg.norm(P-c,axis=1)))]
def layers(k):
    """split crop RGBA into {'front':img,'back':img or None}"""
    name,view=k.rsplit('_',1)
    im=np.asarray(Image.open(f'crops/{k}.png')).copy()
    a=im[...,3]>0
    back=None
    if name=='headphones' and view=='side':
        n,lab,st,_=cv2.connectedComponentsWithStats(a.astype(np.uint8))
        main=1+np.argmax(st[1:,4]); bm=a&(lab!=main)
        back=im.copy(); back[~bm]=0; im[bm]=0
    elif name=='afro':
        # hair mass behind the dome: fill each row between the outer hair edges, darker shade
        hm=np.asarray(Image.open(f'crops/{k}_helm.png'))>0
        fill=np.zeros_like(a)
        for y in range(a.shape[0]):
            xs=np.nonzero(a[y])[0]
            if len(xs): fill[y,xs[0]:xs[-1]+1]=True
        fill&=~cv2.erode(hm.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)|True
        back=np.zeros_like(im); back[fill]=(0x3A,0x22,0x27,255)
        edge=fill&~cv2.erode(fill.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(23,23))).astype(bool)
        back[edge]=(0x2D,0x1E,0x3A,255)
    elif name=='flowercrown':
        # far side of the ring: same crown, darkened, shifted up, sits behind the dome (peeks out at the ends)
        back=im.copy(); sh=int(0.07*a.shape[0])
        back=np.roll(back,-sh,axis=0); back[-sh:]=0
        rgb=back[...,:3].astype(float); back[...,:3]=(rgb*0.62+np.array([45,30,58])*0.38).astype(np.uint8)
    r={'front':Image.fromarray(im),'back':Image.fromarray(back) if back is not None else None}
    if name=='flowercrown':
        for v in r.values():
            if v is not None: v.info['scale']=0.8
    return r
def paths_svg(img,pal,tr):
    paths,k=trace(img)
    g=[]
    for fill,d,tx,ty in paths:
        g.append(f'<path fill="{nearest(fill,pal)}" transform="translate({tx:g},{ty:g})" d="{d}"/>')
    s,ax,ay,ox,oy,rot=tr['s'],tr['ax'],tr['ay'],tr['ox'],tr['oy'],tr['rot']
    # matrix: puppet = R(rot)*(s*k*(p_small) - s*(ax,ay)) + (ox,oy)
    c,sn=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    S=s*k
    a_,b_,c_,d_=c*S,sn*S,-sn*S,c*S
    e=ox-(c*s*ax-sn*s*ay); f=oy-(sn*s*ax+c*s*ay)
    return f'<g transform="matrix({a_:.5f} {b_:.5f} {c_:.5f} {d_:.5f} {e:.2f} {f:.2f})">'+''.join(g)+'</g>'
def bbox_of(img,tr):
    a=np.asarray(img)[...,3]>0; ys,xs=np.nonzero(a)
    pts=np.array([[xs.min(),ys.min()],[xs.max(),ys.min()],[xs.min(),ys.max()],[xs.max(),ys.max()]],float)
    s,ax,ay,ox,oy,rot=tr['s'],tr['ax'],tr['ay'],tr['ox'],tr['oy'],tr['rot']
    c,sn=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    p=(pts-[ax,ay])*s; q=np.stack([c*p[:,0]-sn*p[:,1]+ox, sn*p[:,0]+c*p[:,1]+oy],1)
    return q.min(0)-4,q.max(0)+4
def build(only=None):
    cos=[]; res={}
    for name in NAMES:
        entry={'id':name,'name':NAMES[name],'slot':'hat','hidesAntenna':name not in ('headphones','flowercrown')}
        lay={'back':None,'front':None}
        for view in ('side','front'):
            k=f'{name}_{view}'
            if only and name not in only: continue
            tr=place43b(k) if k in meta and 'helmet_bbox' in meta[k] else place43a(k)
            L=layers(k); pal=meta[k]['palette']+['#3A2227','#2D1E3A']
            ve={}
            for part in ('front','back'):
                img=L[part]
                if img is None: continue
                lo,hi=bbox_of(img,tr); lo=np.floor(lo); hi=np.ceil(hi); w,h=hi-lo
                bpal=pal if part=='front' else list({'#%02X%02X%02X'%tuple(c) for c in np.asarray(img).reshape(-1,4)[np.asarray(img).reshape(-1,4)[:,3]>0][:,:3][::50]})
                body=paths_svg(img,bpal,tr)
                fn=f'hat_{name}_{view}'+('' if (part=='front' and L['back'] is None) else f'_{part}')+'.svg'
                svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}">'
                     f'<g id="hat_{name}_{view}_{part}" transform="translate({-lo[0]:g},{-lo[1]:g})">{body}</g></svg>')
                open(OUT+'svg/'+fn,'w').write(svg)
                ve[part]={'file':'svg/'+fn,'x':float(lo[0]),'y':float(lo[1]),'w':float(w),'h':float(h),'body':body}
            res[k]=ve
            entry[view]={'file':ve['front']['file'],'x':ve['front']['x'],'y':ve['front']['y'],
                         'pivot':[round(320-ve['front']['x'],1),round(300-ve['front']['y'],1)]}
            if 'back' in ve:
                entry[view]['back']={'file':ve['back']['file'],'x':ve['back']['x'],'y':ve['back']['y']}
                lay['back']=lay['back'] or {}
                lay['back'][view]=ve['back']['file']
            if name in WRAP:
                lay['front']=lay['front'] or {}; lay['front'][view]=ve['front']['file']
        entry['layers']=lay
        cos.append(entry)
    return cos,res
def compose(res,name,view,color,scale=1.0):
    ve=res[f'{name}_{view}']
    wrap=lambda p:f'<g>{ve[p]["body"]}</g>' if p in ve else ''
    s=puppet(view,color,hide_ant=name not in ('headphones','flowercrown'),back=wrap('back'),front=wrap('front'),back_first=(name=='afro'))
    # enlarge canvas upward for tall hats
    s=s.replace('viewBox="0 0 640 800" width="640" height="800"','viewBox="-80 -200 800 1020" width="800" height="1020"',1)
    return render(s,int(800*scale))
if __name__=='__main__':
    only=sys.argv[1].split(',') if len(sys.argv)>1 and sys.argv[1]!='all' else None
    cos,res=build(only)
    names=[n for n in NAMES if not only or n in only]
    W=330; S=Image.new('RGBA',(W*2*len(names) if len(names)<4 else W*8, (W*0.78*((len(names)+3)//4 if len(names)>=4 else 1)).__int__()),(244,230,200,255))
    for i,n in enumerate(names):
        for j,v in enumerate(('side','front')):
            im=compose(res,n,v,'#6EC3F0',W/800).crop((0,0,W,int(W*0.75)))
            col=(i%4)*2+j if len(names)>=4 else i*2+j; row=i//4 if len(names)>=4 else 0
            S.paste(im,(col*W,int(row*W*0.78)),im)
    S.save('check.png')
    json.dump(cos,open('cos_tmp.json','w'),indent=1,default=str)
