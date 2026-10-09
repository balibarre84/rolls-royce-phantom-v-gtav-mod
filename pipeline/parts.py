import bpy, numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/imported.blend')
import mathutils
out=[]
for o in sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name):
    me=o.data; nv=len(me.vertices)
    co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); co=co@M[:3,:3].T+M[:3,3]
    ed=np.empty(len(me.edges)*2,np.int32); me.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
    g=sp.coo_matrix((np.ones(len(ed)),(ed[:,0],ed[:,1])),shape=(nv,nv))
    n,lab=connected_components(g,directed=False)
    sizes=np.bincount(lab)
    big=np.argsort(-sizes)[:6]
    desc=[]
    for b in big:
        c=co[lab==b]; desc.append((int(sizes[b]),c.min(0).round(0).tolist(),c.max(0).round(0).tolist()))
    print(o.name,me.materials[0].name if me.materials else '-', 'verts',nv,'components',n)
    for d in desc[:4]: print('    ',d)
