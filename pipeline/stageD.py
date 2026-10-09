import bpy, bmesh, numpy as np, time, math, os
t0=time.time()
def log(*a): print(f'[{time.time()-t0:5.0f}s]',*a,flush=True)
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts.blend')
sc=bpy.context.scene
OUT='/home/claude/work/tex/'
GROUPS={'body':(['chassis','door_dside_f','door_pside_f','door_dside_r','door_pside_r','bonnet','boot','interior','lights','plates'],2048),
        'wheels':(['wheel_lf','wheel_rf','wheel_lr','wheel_rr'],1024)}
loc0={o.name:o.location.copy() for o in bpy.data.objects}
# ---- haute définition (source des normales)
pre=set(bpy.data.objects.keys())
with bpy.data.libraries.load('/home/claude/work/roles.blend') as (src,dst):
    dst.objects=[n for n in src.objects if n!='glass']
hd=[o for o in dst.objects if o is not None]
for o in hd:
    bpy.context.collection.objects.link(o); o.name='HD_'+o.name
bpy.ops.object.select_all(action='DESELECT')
for o in hd: o.select_set(True)
bpy.context.view_layer.objects.active=hd[0]; bpy.ops.object.join(); HD=bpy.context.view_layer.objects.active; HD.name='HD_all'
log('HD faces',len(HD.data.polygons)); HD.hide_render=False
# temporary material tweaks for the albedo bake
saved={}
for m in bpy.data.materials:
    b=m.node_tree.nodes.get('Principled BSDF')
    if not b: continue
    saved[m.name]=(tuple(b.inputs['Base Color'].default_value),b.inputs['Metallic'].default_value)
    b.inputs['Metallic'].default_value=0.0
    if m.name=='carpaint': b.inputs['Base Color'].default_value=(0.0025,0.0025,0.0025,1)   # noir de jais (seule couleur proposée)
if sc.world is None: sc.world=bpy.data.worlds.new('w')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.use_denoising=False
def select_only(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
for gname,(names,res) in GROUPS.items():
    objs=[bpy.data.objects[n] for n in names]
    for i,o in enumerate(objs):
        a=o.data.attributes.new('partid','INT','FACE'); a.data.foreach_set('value',[i]*len(o.data.polygons))
    base=np.array(objs[0].location)
    select_only(objs); bpy.ops.object.join(); J=bpy.context.view_layer.objects.active; J.name='J_'+gname
    log(gname,'joined',len(J.data.polygons),'tris')
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=0.0015,scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.0015,rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    uv=J.data.uv_layers.active.data; u=np.empty(len(uv)*2,np.float32); uv.foreach_get('uv',u); u=u.reshape(-1,2)
    log(gname,'uv bounds',u.min(0).round(3),u.max(0).round(3))
    # bake
    mats=[s.material for s in J.material_slots if s.material]
    imgs={}
    for kind in ('diff','nrm'):
        im=bpy.data.images.new(f'phantom_{gname}_{kind}',res,res,alpha=False); im.colorspace_settings.name='sRGB' if kind=='diff' else 'Non-Color'
        if kind=='nrm': im.generated_color=(0.5,0.5,1,1)
        imgs[kind]=im
    def bake(kind,btype,samples):
        for m in mats:
            nt=m.node_tree; n=nt.nodes.get('BAKE_IMG') or nt.nodes.new('ShaderNodeTexImage'); n.name='BAKE_IMG'
            n.image=imgs[kind]; nt.nodes.active=n
        sc.cycles.samples=samples
        sc.render.bake.margin=6; sc.render.bake.target='IMAGE_TEXTURES'
        if btype=='DIFFUSE':
            sc.render.bake.use_pass_direct=False; sc.render.bake.use_pass_indirect=False; sc.render.bake.use_pass_color=True
        select_only([J]); bpy.ops.object.bake(type=btype); log(gname,kind,'baked')
    bake('diff','DIFFUSE',4)
    # normales : HD (sélectionnée) -> modèle jeu (actif)
    sc.render.bake.use_selected_to_active=True; sc.render.bake.cage_extrusion=0.008; sc.render.bake.max_ray_distance=0.012
    sc.render.bake.normal_space='TANGENT'; sc.render.bake.margin=8
    for m in mats:
        nt=m.node_tree; n=nt.nodes['BAKE_IMG']; n.image=imgs['nrm']; nt.nodes.active=n
    sc.cycles.samples=1
    bpy.ops.object.select_all(action='DESELECT'); HD.select_set(True); J.select_set(True); bpy.context.view_layer.objects.active=J
    bpy.ops.object.bake(type='NORMAL'); log(gname,'normals baked')
    sc.render.bake.use_selected_to_active=False
    nn=np.array(imgs['nrm'].pixels[:]).reshape(res,res,4); nn[...,1]=1-nn[...,1]; nn[...,3]=1      # vert inversé (convention DirectX de GTA V)
    nim=bpy.data.images.new(f'phantom_{gname}_n',res,res,alpha=False); nim.colorspace_settings.name='Non-Color'; nim.pixels=nn.ravel(); nim.filepath_raw=OUT+f'phantom_{gname}_n.png'; nim.file_format='PNG'; nim.save()
    d=np.array(imgs['diff'].pixels[:]).reshape(res,res,4)
    f=d.copy(); f[...,3]=1
    fin=bpy.data.images.new(f'phantom_{gname}_d',res,res,alpha=False); fin.pixels=f.ravel(); fin.filepath_raw=OUT+f'phantom_{gname}_d.png'; fin.file_format='PNG'; fin.save()
    imgs['diff'].filepath_raw=OUT+f'{gname}_albedo_raw.png'
    # wire texture into each material
    for m in mats:
        nt=m.node_tree; n=nt.nodes['BAKE_IMG']; n.image=fin; n.interpolation='Linear'
        b=nt.nodes.get('Principled BSDF'); nt.links.new(n.outputs['Color'],b.inputs['Base Color'])
    # split back
    sel_ids=sorted(set(J.data.attributes['partid'].data[i].value for i in range(len(J.data.polygons))))
    for i,nm in enumerate(names):
        o=J.copy(); o.data=J.data.copy(); o.name=nm; o.data.name=nm; bpy.context.collection.objects.link(o)
        bm=bmesh.new(); bm.from_mesh(o.data); lay=bm.faces.layers.int['partid']
        kill=[f for f in bm.faces if f[lay]!=i]; bmesh.ops.delete(bm,geom=kill,context='FACES')
        loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
        bm.to_mesh(o.data); bm.free()
        l=loc0[nm]; v=np.empty(len(o.data.vertices)*3,np.float32); o.data.vertices.foreach_get('co',v); v=v.reshape(-1,3)-np.array(l)+base
        o.data.vertices.foreach_set('co',v.ravel()); o.data.update(); o.location=l
        o.data.attributes.remove(o.data.attributes['partid'])
        select_only([o]); bpy.ops.object.material_slot_remove_unused()
    bpy.data.objects.remove(J,do_unlink=True)
    log(gname,'split done')
bpy.data.objects.remove(HD,do_unlink=True)
for mn,(c,me_) in saved.items():
    b=bpy.data.materials[mn].node_tree.nodes['Principled BSDF']; b.inputs['Metallic'].default_value=me_
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend'); log('saved')
