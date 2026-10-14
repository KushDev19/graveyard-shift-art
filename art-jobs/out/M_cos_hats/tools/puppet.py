import re, io, cairosvg
from PIL import Image
P=open('/home/user/graveyard-shift-art/frontend/public/assets/ship/crew/crew_puppet.svg').read()
SIDE=['leg_back','arm_back','leg_front','backpack','body','stripe','dome','visor_glow','visor','collar','antenna','arm_front']
FRONT=['f_leg_l','f_leg_r','f_body','f_stripe','f_collar','f_dome','f_visor_glow','f_visor','f_antenna','f_arm_l','f_arm_r']
def mix(c,t,k): return '#%02X%02X%02X'%tuple(int(a+(b-a)*k) for a,b in zip(c,t))
def tint(hexc):
    c=tuple(int(hexc[i:i+2],16) for i in (1,3,5))
    return {'suit':hexc,'suit-shade':mix(c,(45,30,58),0.25),'suit-back':mix(c,(45,30,58),0.4),'suit-light':mix(c,(255,255,255),0.45)}
def puppet(view,color='#CDCCD4',hide_ant=False,back='',front='',back_first=False):
    s=P
    tv=tint(color)
    for k in ('suit-shade','suit-back','suit-light','suit'):
        s=re.sub(r'var\(--%s, #[0-9A-Fa-f]{6}\)'%k,tv[k],s)
    def show(gid,on):
        nonlocal s
        pat=r'<g id="%s"([^>]*?)( display="none")?>'%gid
        s=re.sub(pat,lambda m:'<g id="%s"%s%s>'%(gid,m.group(1),'' if on else ' display="none"'),s,count=1)
    for g in SIDE: show(g,view=='side')
    for g in FRONT: show(g,view=='front')
    if hide_ant: show('antenna',False); show('f_antenna',False)
    if back:
        anchor='<g id="dome"' if view=='side' else ('<g id="f_leg_l"' if back_first else '<g id="f_dome"')
        s=s.replace(anchor,back+anchor,1)
    if front:
        anchor='<g id="arm_front"' if view=='side' else '<g id="f_arm_l"'
        s=s.replace(anchor,front+anchor,1)
    return s
def render(svg,w=None,h=None):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=w,output_height=h))).convert('RGBA')
if __name__=='__main__':
    render(puppet('front','#E4483C',True),320).save('t_front.png'); render(puppet('side','#6EC3F0'),320).save('t_side.png')
