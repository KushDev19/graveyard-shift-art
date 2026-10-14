"""Stage 1: cut each hat out of the originals, remove helmets (43B), quantize, save RGBA crops + meta."""
import numpy as np, cv2, json
from PIL import Image
R='raw_originals/'
OUT='crops/'; import os; os.makedirs(OUT,exist_ok=True)
A={'trucker':[(217,168,1209,655),(1645,134,948,717)],'diner':[(2999,215,988,557),(4310,180,878,614)],
   'hardhat':[(204,1101,1169,713),(1607,1098,1057,714)],'beanie':[(3026,980,1012,868),(4253,923,991,928)],
   'cowboy':[(119,2165,1283,615),(1511,2136,1249,677)],'chef':[(3019,2033,1027,925),(4236,2007,1025,958)]}
B={'nightcap':[(519,90,1002,922),(1786,93,963,919)],'party':[(3145,60,758,954),(4234,36,761,977)],
   'headphones':[(616,1143,916,797),(1801,1145,1071,795)],'flowercrown':[(3083,1204,904,736),(4155,1204,954,737)],
   'afro':[(533,2071,1066,932),(1803,2071,1065,933)],'propeller':[(3157,2072,812,931),(4228,2093,817,910)]}
OUTLINE=np.array([0x2D,0x1E,0x3A])
def hexs(c): return '#%02X%02X%02X'%tuple(int(v) for v in c)
HELM=np.array([[0x29,0x1D,0x43],[0x31,0x25,0x56],[0xA1,0xB5,0xC9],[0xD3,0xC9,0xEB],[0x85,0x85,0xA2],[0x4D,0x6F,0x80],[0x25,0x1A,0x3C],[0x2E,0x22,0x50]])
meta={}
for sheet,items in (('43A_COS_HATS_A.png',A),('43B_COS_HATS_B.png',B)):
    img=np.asarray(Image.open(R+sheet).convert('RGB')).astype(np.int32)
    for name,views in items.items():
        for vi,(x,y,w,h) in enumerate(views):
            view=('side','front')[vi]; P=24
            c=img[y-P:y+h+P, x-P:x+w+P]
            r,g,b=c[...,0],c[...,1],c[...,2]
            bg=(r-g>90)&(b-g>90)
            fg=~bg
            # keep only largest blob group (drop specks)
            n,lab,st,_=cv2.connectedComponentsWithStats(fg.astype(np.uint8))
            keep=np.zeros_like(fg)
            for i in range(1,n):
                if st[i,4]>400: keep|=lab==i
            fg=keep
            helm=np.zeros_like(fg)
            if sheet.startswith('43B'):
                inter=fg&(b>r+15)&(b<120)&(r<72)
                inter=cv2.morphologyEx(inter.astype(np.uint8),cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
                n,lab,st,_=cv2.connectedComponentsWithStats(inter)
                hm=np.isin(lab,[i for i in range(1,n) if st[i,4]>8000]).astype(np.uint8)
                cnts,_=cv2.findContours(hm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                hm2=np.zeros_like(hm); cv2.drawContours(hm2,cnts,-1,1,-1)
                RIM=np.array([[0xA1,0xB5,0xC9],[0x85,0x85,0xA2],[0x4D,0x6F,0x80],[0x8C,0xA0,0xB4],[0xB4,0xC4,0xD4],[0xD3,0xC9,0xEB],[0xB9,0xA6,0xAB],[0xC4,0xBC,0xE0]])
                drim=np.min(np.linalg.norm(c[...,None,:]-RIM[None,None],axis=-1),axis=-1)
                band=cv2.dilate(hm2,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(71,71))).astype(bool)
                helm=hm2.astype(bool)|(band&(drim<38)&fg)
                helm=cv2.morphologyEx(helm.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8)).astype(bool)
                hatc=fg&~helm&(np.min(np.linalg.norm(c[...,None,:]-np.array([[0x3F,0x19,0x45],[0x2D,0x1E,0x3A],[0x35,0x1A,0x40]])[None,None],axis=-1),axis=-1)>24)
                hatc=cv2.morphologyEx(hatc.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8)).astype(bool)
                fgh=fg&~helm
                ring=cv2.dilate(helm.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(61,61))).astype(bool)&~helm
                near2=cv2.dilate(hatc.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))).astype(bool)
                fgh&=~(ring&~near2)
                n,lab,st,_=cv2.connectedComponentsWithStats(fgh.astype(np.uint8))
                keep=np.zeros_like(fgh)
                for i in range(1,n):
                    if st[i,4]>4000: keep|=lab==i
                fg=keep
                # helmet ellipse from its outer boundary, ignoring where the hat covers it
                cnts,_=cv2.findContours(helm.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                pts=max(cnts,key=len)[:,0,:]
                hatd=cv2.dilate(hatc.astype(np.uint8),np.ones((41,41),np.uint8)).astype(bool)
                pts=pts[~hatd[pts[:,1],pts[:,0]]]
                ys=pts[:,1]; top,bot=ys.min(),ys.max()
                ell=((0,0),(0,0),0)
                hx,hy,hw,hh=cv2.boundingRect(helm.astype(np.uint8))
            # quantize
            px=c[fg].astype(np.float32)
            edge=fg&~cv2.erode(fg.astype(np.uint8),np.ones((7,7),np.uint8)).astype(bool)
            k={'flowercrown':10,'propeller':9,'trucker':8,'headphones':8}.get(name,6)
            _,lab,cen=cv2.kmeans(c[fg&~edge].astype(np.float32),k,None,(cv2.TERM_CRITERIA_MAX_ITER,40,0.5),4,cv2.KMEANS_PP_CENTERS)
            # merge near-duplicate centres
            cen=cen.astype(np.int32)
            oi=np.argmin(np.linalg.norm(cen-[60,25,68],axis=1)); cen[oi]=OUTLINE
            dist=np.linalg.norm(px[:,None,:]-cen[None].astype(np.float32),axis=-1)
            q=np.argmin(dist,axis=1)
            labimg=np.full(fg.shape,-1,np.int32); labimg[fg]=q; labimg[edge]=oi
            # mode filter to kill antialias speckles
            onehot=np.stack([(labimg==i).astype(np.float32) for i in range(len(cen))])
            onehot=np.stack([cv2.blur(o,(5,5)) for o in onehot])
            labimg2=np.argmax(onehot,0); labimg2[~fg]=-1
            out=np.zeros(fg.shape+(4,),np.uint8)
            out[fg,:3]=cen[labimg2[fg]]; out[fg,3]=255
            fn=f'{name}_{view}.png'; Image.fromarray(out).save(OUT+fn)
            m={'origin':[int(x-P),int(y-P)],'size':[int(c.shape[1]),int(c.shape[0])],'sheet':sheet,
               'palette':[hexs(v) for v in cen]}
            if sheet.startswith('43B'):
                m['helmet_ellipse']=[float(ell[0][0]),float(ell[0][1]),float(ell[1][0]),float(ell[1][1]),float(ell[2])]
                m['helmet_bbox']=[hx,hy,hw,hh]
                Image.fromarray((helm*255).astype(np.uint8)).save(OUT+f'{name}_{view}_helm.png')
            meta[f'{name}_{view}']=m
            print(name,view,m['palette'],m.get('helmet_ellipse'))
json.dump(meta,open('meta.json','w'),indent=1)
