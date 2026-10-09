# Move hub caps / nuts (small chassis components located at a wheel centre) into the matching wheel object
import bpy, bmesh, numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts.blend')
WN=('wheel_lf','wheel_rf','wheel_lr','wheel_rr')
WC={n:np.array(bpy.data.objects[n].location) for n in WN}
ch=bpy.data.objects['chassis']; me=ch.data
nv=len(me.vertices); co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
pv=np.array([[me.loops[l].vertex_index for l in p.loop_indices][:3] for p in me.polygons])
e=np.concatenate([pv[:,[0,1]],pv[:,[1,2]]]); nc,lab=connected_components(sp.coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(nv,nv)),directed=False)
fl=lab[pv[:,0]]
dest=np.array(['']*len(pv),dtype=object)
for c in np.unique(fl):
    v=co[lab==c]; mn,mx=v.min(0),v.max(0); cen=(mn+mx)/2; sz=(mx-mn).max()
    best=min(WN,key=lambda n:np.linalg.norm(cen-WC[n]))
    if np.linalg.norm(cen-WC[best])<0.45 and sz<0.35: dest[fl==c]=best
print({n:int((dest==n).sum()) for n in WN})
bpy.ops.object.select_all(action='DESELECT')
for n in WN:
    sel=dest==n
    if not sel.any(): continue
    src=ch.copy(); src.data=me.copy(); bpy.context.collection.objects.link(src)
    bm=bmesh.new(); bm.from_mesh(src.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not sel[f.index]],context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bmesh.ops.translate(bm,verts=bm.verts[:],vec=-bpy.data.objects[n].location)   # into wheel-local space
    bm.to_mesh(src.data); bm.free(); src.location=(0,0,0)
    w=bpy.data.objects[n]; bpy.ops.object.select_all(action='DESELECT'); src.select_set(True); w.select_set(True)
    bpy.context.view_layer.objects.active=w; bpy.ops.object.join()
    print(n,'tris',len(w.data.polygons),[m.name for m in w.data.materials])
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[f for f in bm.faces if dest[f.index]!=''],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(me); bm.free()
print('chassis tris',len(me.polygons))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_parts.blend')
