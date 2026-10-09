# Palette de couleurs unies : chaque matériau pointe vers une case de couleur (plus d'îlots UV ni de bake).
# Évite les débordements de mipmaps entre îlots (pneus gris/noir) et les UV fragmentés.
import bpy, numpy as np, re
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts.blend')
CELL=32; N=8; RES=CELL*N
def srgb(c): return np.where(c<=0.0031308,c*12.92,1.055*np.power(np.clip(c,0,None),1/2.4)-0.055)
cols={}
for m in bpy.data.materials:
    b=m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
    if not b: continue
    base=re.sub(r'\.\d+$','',m.name); c=np.array(b.inputs['Base Color'].default_value[:3])
    if base=='carpaint': c=np.array([0.80,0.80,0.80])      # neutre clair : le noir vient de la palette du jeu
    cols.setdefault(base,c)
names=sorted(cols); assert len(names)<=N*N,len(names)
idx={n:i for i,n in enumerate(names)}
img=np.zeros((RES,RES,4),np.float32); img[...,3]=1
for n,i in idx.items():
    r,c=divmod(i,N); img[r*CELL:(r+1)*CELL,c*CELL:(c+1)*CELL,:3]=srgb(cols[n])
img=img[::-1]                                   # PNG : origine en haut ; Blender : origine en bas
from PIL import Image
im8=(np.clip(img[::-1,:,:3],0,1)*255+0.5).astype(np.uint8)    # image affichée normalement (ligne 0 en haut = rang 0)
for fn in ('phantom_body_d','phantom_wheels_d'):
    Image.fromarray(im8).save(f'/home/claude/work/tex/{fn}.png')
    bi=bpy.data.images.new(fn,RES,RES,alpha=False); bi.use_fake_user=True
# UV : centre de la case du matériau. Rang r (en haut) -> v = 1-(r+0.5)/N
for o in [o for o in bpy.data.objects if o.type=='MESH']:
    me=o.data
    uv=me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n=re.sub(r'\.\d+$','',o.material_slots[p.material_index].material.name); i=idx[n]; r,c=divmod(i,N)
        u=(c+0.5)/N; v=1-(r+0.5)/N
        for l in p.loop_indices: uv.data[l].uv=(u,v)
print('palette',len(names),names)
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend')
