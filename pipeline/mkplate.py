# Textures de plaques britanniques (fond noir, caractères blancs) -> phantom_plate_d.png / .dds
import struct, io
from PIL import Image, ImageDraw, ImageFont
TXT='PV63 PKW'; W=1024; H0=219; H=256
def plate(bg,txt):
    im=Image.new('RGB',(W,H0),bg); d=ImageDraw.Draw(im)
    d.rounded_rectangle((3,3,W-4,H0-4),radius=16,outline=(235,235,235),width=4)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',150)
    d.text((W/2,H0/2+6),txt,font=f,fill=(245,245,245),anchor='mm')
    return im.resize((W,H),Image.LANCZOS)
atlas=Image.new('RGB',(W,512)); atlas.paste(plate((12,12,12),TXT),(0,0)); atlas.paste(plate((12,12,12),TXT),(0,256))
atlas.save('/home/claude/work/tex/phantom_plate_d.png')
im=atlas.copy(); w,h=im.size; levels=[]
while True:
    b=io.BytesIO(); im.convert('RGBA').save(b,format='DDS',pixel_format='DXT1'); levels.append(b.getvalue()[128:])
    if w==1 and h==1: break
    w,h=max(1,w//2),max(1,h//2); im=im.resize((w,h),Image.LANCZOS)
W0,H1=atlas.size
hdr=b'DDS '+struct.pack('<7I',124,0xA1007,H1,W0,len(levels[0]),0,len(levels))+b'\0'*44+struct.pack('<2I4s5I',32,4,b'DXT1',0,0,0,0,0)+struct.pack('<5I',0x401008,0,0,0,0)
open('/home/claude/work/tex/phantom_plate_d.dds','wb').write(hdr+b''.join(levels)); print('ok',len(levels))
