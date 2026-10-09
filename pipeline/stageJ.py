import bpy, addon_utils
addon_utils.enable('bl_ext.user_default.sollumz',default_set=True)
from bl_ext.user_default.sollumz.sollumz_properties import SollumType, LODLevel
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_sollumz2.blend')
dg=bpy.context.evaluated_depsgraph_get()
LODS=((LODLevel.MEDIUM,0.35,'med'),(LODLevel.LOW,0.10,'low'),(LODLevel.VERYLOW,0.03,'vlow'))
SKIP={'plates'}
tot={'high':0,'med':0,'low':0,'vlow':0}
for o in [o for o in bpy.data.objects if o.sollum_type==SollumType.DRAWABLE_MODEL]:
    hi=o.sz_lods.get_lod(LODLevel.HIGH).mesh; tot['high']+=len(hi.polygons)
    if o.name in SKIP: 
        for lv,r,t in LODS: tot[t]+=0
        continue
    for lv,ratio,tag in LODS:
        m=hi.copy(); m.name=f'{o.name}_{tag}'
        tmp=bpy.data.objects.new('tmp',m); bpy.context.collection.objects.link(tmp)
        md=tmp.modifiers.new('d','DECIMATE'); md.decimate_type='COLLAPSE'; md.ratio=ratio; md.use_collapse_triangulate=True
        ev=tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()); new=bpy.data.meshes.new_from_object(ev)
        new.name=m.name; bpy.data.objects.remove(tmp); bpy.data.meshes.remove(m)
        o.sz_lods.get_lod(lv).mesh=new; tot[tag]+=len(new.polygons)
    o.sz_lods.set_highest_lod_active()
print('LOD triangle totals',tot)
d=bpy.data.objects['phantom.mesh'].drawable_properties
d.lod_dist_high=30; d.lod_dist_med=80; d.lod_dist_low=200; d.lod_dist_vlow=9998
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_sollumz3.blend')
