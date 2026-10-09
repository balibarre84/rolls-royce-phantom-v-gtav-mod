import struct, io
from PIL import Image
def dxt5_chain(rgba, size, dst):
    im=Image.new('RGBA',(size,size),rgba); w=h=size; levels=[]
    while True:
        b=io.BytesIO(); im.save(b,format='DDS',pixel_format='DXT5'); levels.append(b.getvalue()[128:])
        if w==1: break
        w=h=max(1,w//2); im=im.resize((w,h))
    hdr=b'DDS '+struct.pack('<7I',124,0xA1007,size,size,len(levels[0]),0,len(levels))+b'\0'*44+struct.pack('<2I4s5I',32,4,b'DXT5',0,0,0,0,0)+struct.pack('<5I',0x401008,0,0,0,0)
    open(dst,'wb').write(hdr+b''.join(levels))
# verre teinté sombre, ~30 % d'opacité
dxt5_chain((22,26,28,80),16,'/home/claude/work/tex/phantom_glass_d.dds')
