import bpy, math, time, numpy as np
t0=time.time()
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/roles.blend')
TARGET={'chassis':85000,'glass':8000,'interior':22000,'lights':5000,'plates':1200,'wheel_lf':7000,'wheel_rf':7000,'wheel_lr':7000,'wheel_rr':7000}
COL={'carpaint':((0.0314,0.0314,0.0314),0.25,0.0,1),'chrome':((0.54,0.54,0.54),0.12,1.0,1),'interior_second':((0.68,0.60,0.46),0.5,0,1),
 'interior_third':((0.36,0.28,0.21),0.6,0,1),'interior_fourth':((0.37,0.106,0.035),0.35,0,1),'black':((0.078,0.078,0.078),0.5,0,1),
 'white':((0.94,0.94,0.94),0.4,0,1),'mirror':((0.47,0.54,0.53),0.05,1.0,1),'clearglass':((0.6,0.6,0.6),0.03,0,0.25),
 'windowglass':((0.07,0.13,0.11),0.03,0,0.55),'redglass':((0.43,0.047,0.047),0.1,0,0.8),'greenglass':((0.10,0.59,0.24),0.1,0,0.8),
 'orangeglass':((0.74,0.29,0.0),0.1,0,0.8),'yellow':((0.94,0.78,0.04),0.3,0,1),'rim':((0.68,0.68,0.68),0.3,0.9,1),'tire':((0.106,0.106,0.106),0.8,0,1),
 'brakedisk':((0.49,0.49,0.49),0.4,0.8,1),'LicPlate_white':((0.98,0.98,0.98),0.4,0,1),'LicPlate_black':((0.02,0.02,0.02),0.5,0,1),
 'LicPlate_blue':((0.125,0.125,0.61),0.4,0,1),'LicPlate_yellow':((0.88,0.71,0.02),0.4,0,1)}
for m in bpy.data.materials:
    if m.name in COL:
        c,r,me_,a=COL[m.name]; m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=me_; b.inputs['Alpha'].default_value=a
        if a<1: m.blend_method='BLEND' if hasattr(m,'blend_method') else None
before={}
for o in list(bpy.data.objects):
    if o.type!='MESH': continue
    nt=len(o.data.polygons); before[o.name]=nt
    tg=TARGET.get(o.name,5000)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    m=o.modifiers.new('dec','DECIMATE'); m.decimate_type='COLLAPSE'; m.ratio=min(1.0,tg/nt); m.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier='dec')
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    o.select_set(False)
    print(o.name,nt,'->',len(o.data.polygons),round(time.time()-t0),'s')
# set wheel origins to their centres
for o in bpy.data.objects:
    if o.name.startswith('wheel_'):
        bpy.context.view_layer.objects.active=o; o.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS'); o.select_set(False)
tot=sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH'); print('TOTAL tris',tot)
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_v_parkward_hd.blend')
