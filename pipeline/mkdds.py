import struct, io
from PIL import Image
def dxt1_chain(src, dst):
    im=Image.open(src).convert('RGB'); w,h=im.size; levels=[]
    while True:
        b=io.BytesIO(); im.convert('RGBA').save(b,format='DDS',pixel_format='DXT1'); levels.append(b.getvalue()[128:])
        if w==1 and h==1: break
        w,h=max(1,w//2),max(1,h//2); im=im.resize((w,h),Image.LANCZOS)
        if w<4 and h<4 and len(levels)>=1 and (w<4 or h<4): 
            pass
    # note: Pillow pads sub-4px levels to one 8-byte block, which matches DXT1 layout
    W,H=Image.open(src).size
    hdr=b'DDS '+struct.pack('<7I',124,0xA1007,H,W,len(levels[0]),0,len(levels))+b'\0'*44+struct.pack('<2I4s5I',32,4,b'DXT1',0,0,0,0,0)+struct.pack('<5I',0x401008,0,0,0,0)
    assert len(hdr)==128,len(hdr)
    open(dst,'wb').write(hdr+b''.join(levels)); return len(levels)
import os
os.makedirs('/home/claude/work/tex',exist_ok=True)
for n in ('phantom_body_d','phantom_wheels_d'):
    print(n,dxt1_chain(f'/home/claude/work/tex/{n}.png',f'/home/claude/work/tex/{n}.dds'),os.path.getsize(f'/home/claude/work/tex/{n}.dds'))
