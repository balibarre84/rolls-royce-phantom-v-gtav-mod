# Plaques britanniques : supprime les caractères 3D d'origine, ajoute deux panneaux texturés (avant blanc / arrière jaune)
import bpy, bmesh, numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend')
o=bpy.data.objects['plates']; me=o.data
nv=len(me.vertices); co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
pv=np.array([[me.loops[l].vertex_index for l in p.loop_indices][:3] for p in me.polygons])
e=np.concatenate([pv[:,[0,1]],pv[:,[1,2]]]); nc,lab=connected_components(sp.coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(nv,nv)),directed=False)
fl=lab[pv[:,0]]
matn=np.array([o.material_slots[p.material_index].material.name for p in me.polygons])
frames={}; kill=np.zeros(len(pv),bool)
for k in range(nc):
    f=np.where(fl==k)[0]; v=co[lab==k]; w=v[:,0].max()-v[:,0].min(); m=matn[f[0]]
    if m=='LicPlate_black' and w>0.4: frames['f' if v[:,1].mean()>0 else 'r']=v
    elif m=='LicPlate_black' or m=='LicPlate_yellow' or (m=='LicPlate_white' and len(f) in (40,48)): kill[f]=True
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[f for f in bm.faces if kill[f.index]],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS'); bm.to_mesh(me); bm.free()
mat=bpy.data.materials.new('LicPlate_uk'); mat.use_nodes=True
for tag,v in frames.items():
    c=v.mean(0); u,s,vt=np.linalg.svd(v-c); n=vt[2]
    sgn=1 if tag=='f' else -1
    if n[1]*sgn<0: n=-n
    z=np.array([0,0,1.0]); up=z-(z@n)*n; up/=np.linalg.norm(up); r=np.cross(up,n)
    pr=(v-c)@r; pu=(v-c)@up; pn=(v-c)@n
    w0,w1,h0,h1=pr.min(),pr.max(),pu.min(),pu.max(); off=pn.max()+0.0015
    P=[c+r*w0+up*h0+n*off,c+r*w1+up*h0+n*off,c+r*w1+up*h1+n*off,c+r*w0+up*h1+n*off]
    q=bpy.data.meshes.new('plate_'+('front' if tag=='f' else 'rear')); q.from_pydata([tuple(p) for p in P],[],[(0,1,2,3)]); q.update()
    q.materials.append(mat); uv=q.uv_layers.new(name='UVMap 0')
    v0,v1=(0.5,1.0) if tag=='f' else (0.0,0.5)
    for lp,(uu,vv) in zip(q.polygons[0].loop_indices,[(0,v0),(1,v0),(1,v1),(0,v1)]): uv.data[lp].uv=(uu,vv)
    ob=bpy.data.objects.new(q.name,q); bpy.context.collection.objects.link(ob)
    print('plate',tag,'w',round(w1-w0,3),'h',round(h1-h0,3),'n',n.round(2))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend')
