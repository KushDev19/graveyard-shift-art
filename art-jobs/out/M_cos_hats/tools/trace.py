import vtracer, re, sys, numpy as np
from PIL import Image
def trace(img, scale=None):
    scale=scale or img.info.get("scale",0.5)
    """img: RGBA PIL at source res. returns (inner svg paths as string in source-pixel coords)."""
    w,h=img.size; sm=img.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.NEAREST)
    a=np.asarray(sm).copy(); 
    px=[tuple(int(v) for v in p) for p in a.reshape(-1,4)]
    svg=vtracer.convert_pixels_to_svg(px,size=sm.size,colormode='color',hierarchical='stacked',mode='spline',
        filter_speckle=6,color_precision=8,layer_difference=6,corner_threshold=60,length_threshold=4.0,
        max_iterations=10,splice_threshold=45,path_precision=1)
    paths=re.findall(r'<path[^>]*/>',svg)
    out=[]
    for p in paths:
        fill=re.search(r'fill="([^"]+)"',p).group(1).upper()
        dm=re.search(r'd="([^"]+)"',p)
        if not dm: continue
        d=dm.group(1)
        t=re.search(r'translate\(([-\d.]+),([-\d.]+)\)',p)
        tx,ty=(float(t.group(1)),float(t.group(2))) if t else (0,0)
        out.append((fill,d,tx,ty))
    return out, 1/scale
if __name__=='__main__':
    out,k=trace(Image.open(sys.argv[1]))
    print(len(out), sum(len(d) for _,d,_,_ in out), set(f for f,_,_,_ in out))
