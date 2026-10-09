import bpy, numpy as np, scipy.sparse as sp, time
from scipy.sparse.csgraph import connected_components
t0=time.time()
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/imported.blend')
src=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
FRONT_Y_CM=-216.0; REAR_Y_CM=148.0         # wheel centres (model coords, cm); front is -Y in the source
YMID=(FRONT_Y_CM+REAR_Y_CM)/2
def to_final(c):                          # cm model -> m, front +Y, origin mid-wheelbase on ground
    out=np.empty_like(c); out[:,0]=-c[:,0]; out[:,1]=-(c[:,1]-YMID); out[:,2]=c[:,2]; return out*0.01
WH={('lf'):(-1,1),('rf'):(1,1),('lr'):(-1,-1),('rr'):(1,-1)}
wy=(-(FRONT_Y_CM-YMID)*0.01, -(REAR_Y_CM-YMID)*0.01)   # front +, rear -
print('wheel y front/rear (m):',wy)
roles={}   # role -> list of (verts, faces, matname_per_face)
def add(role,V,F,mats): roles.setdefault(role,[]).append((V,F,mats))
for o in src:
    me=o.data; M=np.array(o.matrix_world)
    nv=len(me.vertices)
    co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3).astype(np.float64)
    co=co@M[:3,:3].T+M[:3,3]
    nl=len(me.loops); lv=np.empty(nl,np.int32); me.loops.foreach_get('vertex_index',lv)
    F=lv.reshape(-1,3)
    mi=np.empty(len(me.polygons),np.int32); me.polygons.foreach_get('material_index',mi)
    names=[m.name.split('.')[0] for m in me.materials]
    # weld
    key=np.round(co*1000).astype(np.int64)
    _,uidx,inv=np.unique(key,axis=0,return_index=True,return_inverse=True)
    inv=inv.ravel(); Vw=co[uidx]; Fw=inv[F]
    ok=(Fw[:,0]!=Fw[:,1])&(Fw[:,1]!=Fw[:,2])&(Fw[:,0]!=Fw[:,2]); Fw=Fw[ok]; mi=mi[ok]
    n=len(Vw)
    e=np.concatenate([Fw[:,[0,1]],Fw[:,[1,2]]]); g=sp.coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(n,n))
    nc,lab=connected_components(g,directed=False)
    fl=lab[Fw[:,0]]                        # component per face
    Vf=to_final(Vw)
    # per-component stats
    cnt=np.bincount(fl,minlength=nc)
    mn=np.full((nc,3),1e9); mx=np.full((nc,3),-1e9)
    for k in range(3):
        v=Vf[Fw[:,0],k]; np.minimum.at(mn[:,k],fl,v); np.maximum.at(mx[:,k],fl,v)
    cen=(mn+mx)/2; dim=(mx-mn)
    mat=names[0] if names else ''
    face_role=np.empty(len(Fw),dtype=object)
    comp_role=np.empty(nc,dtype=object)
    for c in range(nc):
        m=mat; x,y,z=cen[c]; d=dim[c].max()
        if m in('tire','rim','brakedisk'):
            sx=-1 if x<0 else 1; sy='f' if y>0 else 'r'
            comp_role[c]='wheel_'+('l' if sx<0 else 'r')+sy
        elif m in('clearglass','windowglass'): comp_role[c]='glass'
        elif m in('orangeglass','redglass','greenglass','yellow','white') and d<0.5 and (abs(y)>2.2 or z>1.6 or m!='white'): comp_role[c]='lights'
        elif m.startswith('LicPlate'): comp_role[c]='plates'
        elif m.startswith('interior'): comp_role[c]='interior'
        elif m in('carpaint',): comp_role[c]='chassis'
        else:
            inside=(abs(x)<0.76 and 0.30<z<1.45 and -2.05<y<1.75 and d<1.6)
            comp_role[c]='interior' if inside else 'chassis'
    role_of_face=comp_role[fl]
    for r in set(role_of_face):
        sel=role_of_face==r
        add(r,Vf,Fw[sel],[names[i] for i in mi[sel]])
    print(o.name,mat,'comps',nc,'welded verts',n,'t',round(time.time()-t0))
# build role meshes
bpy.ops.wm.read_factory_settings(use_empty=True)
stats={}
for r,lst in roles.items():
    Vs=[];Fs=[];Ms=[];off=0
    for V,F,mats in lst:
        used=np.unique(F); remap=-np.ones(len(V),np.int64); remap[used]=np.arange(len(used))
        Vs.append(V[used]); Fs.append(remap[F]+off); Ms+=mats; off+=len(used)
    V=np.concatenate(Vs); F=np.concatenate(Fs)
    me=bpy.data.meshes.new(r); me.from_pydata(V.tolist(),[],F.tolist()); me.update()
    mnames=sorted(set(Ms)); 
    for nm in mnames:
        mt=bpy.data.materials.get(nm) or bpy.data.materials.new(nm); me.materials.append(mt)
    idx=np.array([mnames.index(x) for x in Ms],np.int32); me.polygons.foreach_set('material_index',idx)
    ob=bpy.data.objects.new(r,me); bpy.context.scene.collection.objects.link(ob)
    stats[r]=(len(F),len(V),mnames)
for r,s in sorted(stats.items()): print(r.ljust(12),s)
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/roles.blend')
print('done',round(time.time()-t0),'s')
