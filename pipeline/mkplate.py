# Textures de plaques britanniques (avant blanche, arrière jaune) -> phantom_plate_d.png / .dds
import struct, io
from PIL import Image, ImageDraw, ImageFont
TXT='PV63 PKW'; W=1024; H0=219; H=256
def plate(bg,txt):
    im=Image.new('RGB',(W,H0),bg); d=ImageDraw.Draw(im)
    d.rounded_rectangle((3,3,W-4,H0-4),radius=16,outline=(15,15,15),width=5)
    sw=int(W*0.085); d.rounded_rectangle((8,8,sw+8,H0-9),radius=10,fill=(0,51,153))
    f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',40); d.text((sw/2+8,H0*0.64),'GB',font=f2,fill=(255,255,255),anchor='mm')
    for i in range(12):                                   # étoiles simplifiées
        import math; a=i/12*2*math.pi; x=sw/2+8+math.cos(a)*30; y=H0*0.28+math.sin(a)*30; d.ellipse((x-3,y-3,x+3,y+3),fill=(255,204,0))
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',150)
    d.text(((W+sw)/2,H0/2+6),txt,font=f,fill=(10,10,10),anchor='mm')
    return im.resize((W,H),Image.LANCZOS)
atlas=Image.new('RGB',(W,512)); atlas.paste(plate((236,236,232),TXT),(0,0)); atlas.paste(plate((246,196,22),TXT),(0,256))
atlas.save('/home/claude/work/tex/phantom_plate_d.png')
im=atlas.copy(); w,h=im.size; levels=[]
while True:
    b=io.BytesIO(); im.convert('RGBA').save(b,format='DDS',pixel_format='DXT1'); levels.append(b.getvalue()[128:])
    if w==1 and h==1: break
    w,h=max(1,w//2),max(1,h//2); im=im.resize((w,h),Image.LANCZOS)
W0,H1=atlas.size
hdr=b'DDS '+struct.pack('<7I',124,0xA1007,H1,W0,len(levels[0]),0,len(levels))+b'\0'*44+struct.pack('<2I4s5I',32,4,b'DXT1',0,0,0,0,0)+struct.pack('<5I',0x401008,0,0,0,0)
open('/home/claude/work/tex/phantom_plate_d.dds','wb').write(hdr+b''.join(levels)); print('ok',len(levels))
