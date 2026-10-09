import bpy, bmesh, numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_v_parkward_hd_150k.blend')
ch=bpy.data.objects['chassis']; me=ch.data
nv=len(me.vertices); co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
pv=np.array([[me.loops[l].vertex_index for l in p.loop_indices][:3] for p in me.polygons])
e=np.concatenate([pv[:,[0,1]],pv[:,[1,2]]])
nc,lab=connected_components(sp.coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(nv,nv)),directed=False)
fl=lab[pv[:,0]]; cnt=np.bincount(fl,minlength=nc)
cen=co[pv].mean(1)                      # face centroids
mn=np.full((nc,3),1e9); mx=np.full((nc,3),-1e9)
for k in range(3):
    np.minimum.at(mn[:,k],lab[pv[:,0]],co[pv[:,0],k]); np.maximum.at(mx[:,k],lab[pv[:,0]],co[pv[:,0],k])
# main body: huge or spanning the whole car
main=(cnt>5000)|((mx[:,1]-mn[:,1])>3.0)
part=np.array(['chassis']*len(pv),dtype=object)
ax=np.abs(cen[:,0]); y=cen[:,1]; z=cen[:,2]; side=np.where(cen[:,0]<0,'dside','pside')
BON={262,270,268}; BOOT={407}
inbon=np.isin(fl,list(BON))
cand=(~main[fl])&(~inbon)
door_zone=cand&(ax>0.70)&(ax<1.02)&(z>0.30)&(z<1.70)
for s in ('dside','pside'):
    for kind,(y0,y1) in (('f',(-0.29,0.88)),('r',(-1.27,-0.29))):
        sel=door_zone&(side==s)&(y>=y0)&(y<y1)
        part[sel]=f'door_{s}_{kind}'
# bonnet halves and top strip, boot lid (explicit components found by inspection)
BON={262,270,268}; BOOT={407}
isb=inbon&(z>1.0)&(ax<0.80)
# majority smoothing over face adjacency (within bonnet components)
E=np.concatenate([pv[:,[0,1]],pv[:,[1,2]],pv[:,[2,0]]]); fi=np.tile(np.arange(len(pv)),3)
E.sort(axis=1); key=E[:,0].astype(np.int64)*nv+E[:,1]; od=np.argsort(key); ks=key[od]; fs=fi[od]
same=ks[1:]==ks[:-1]; a=fs[:-1][same]; b=fs[1:][same]
A=sp.coo_matrix((np.ones(len(a)*2),(np.r_[a,b],np.r_[b,a])),shape=(len(pv),len(pv))).tocsr()
for _ in range(6):
    nb=np.asarray(A.sum(1)).ravel(); yes=A@isb.astype(float)
    isb=np.where(inbon&(nb>0),yes/np.maximum(nb,1)>0.5,isb)&inbon
part[isb]='bonnet'
print('bonnet faces',int(isb.sum()))
part[np.isin(fl,list(BOOT))]='boot'
for p in sorted(set(part)): print(p,int((part==p).sum()))
# split
mats=list(me.materials)
cols={'chassis':(.6,.6,.62,1),'door_dside_f':(.9,.1,.1,1),'door_pside_f':(.1,.8,.1,1),'door_dside_r':(.1,.1,.9,1),
      'door_pside_r':(.9,.8,.1,1),'bonnet':(.9,.1,.9,1),'boot':(.1,.9,.9,1)}
for p in sorted(set(part)):
    if p=='chassis': continue
    o=ch.copy(); o.data=me.copy(); o.name=p; o.data.name=p
    bpy.context.collection.objects.link(o)
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    kill=[f for f in bm.faces if part[f.index]!=p]
    bmesh.ops.delete(bm,geom=kill,context='FACES'); 
    loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.to_mesh(o.data); bm.free()
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
kill=[f for f in bm.faces if part[f.index]!='chassis']
bmesh.ops.delete(bm,geom=kill,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(me); bm.free()

from mathutils import Vector
for o in list(bpy.data.objects):
    if o.name.startswith('door_') or o.name in('bonnet','boot'):
        v=np.empty(len(o.data.vertices)*3,np.float32); o.data.vertices.foreach_get('co',v); v=v.reshape(-1,3)
        mn,mx=v.min(0),v.max(0)
        if o.name.startswith('door_'):
            sg=-1 if 'dside' in o.name else 1
            piv=np.array([sg*np.abs(v[:,0]).mean(),mx[1],(mn[2]+mx[2])/2])
        elif o.name=='bonnet': piv=np.array([0,mn[1],mx[2]])
        else: piv=np.array([0,mx[1],mx[2]])
        v-=piv; o.data.vertices.foreach_set('co',v.ravel()); o.data.update(); o.location=Vector(piv)
        print(o.name,'pivot',piv.round(3),'tris',len(o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_parts.blend')
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.color_type='OBJECT'; sc.display.shading.light='STUDIO'
for o in bpy.data.objects:
    if o.type=='MESH': o.color=cols.get(o.name,(.3,.3,.35,1))
for o in bpy.data.objects:
    if o.name in('glass','interior','lights','plates') or o.name.startswith('wheel'): o.hide_render=True
cam=bpy.data.cameras.new('c'); cam.lens=40; co_=bpy.data.objects.new('c',cam); bpy.context.collection.objects.link(co_); sc.camera=co_
sc.render.resolution_x=1400; sc.render.resolution_y=800
for name,loc in (('left',(-9,0,1.2)),('front34',(-6,6,3.5))):
    co_.location=loc; d=Vector((0,0,0.8))-Vector(loc); co_.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=f'/home/claude/work/diag_{name}.png'; bpy.ops.render.render(write_still=True)
