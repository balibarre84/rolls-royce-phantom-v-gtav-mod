import bpy, bmesh, numpy as np
from mathutils import Vector
import addon_utils; addon_utils.enable('bl_ext.user_default.sollumz',default_set=True)
from bl_ext.user_default.sollumz.sollumz_properties import SollumType
from bl_ext.user_default.sollumz.tools.blenderhelper import create_blender_object, create_empty_object, add_child_of_bone_constraint
from bl_ext.user_default.sollumz.tools.boundhelper import create_bound_box, create_bound_cylinder
from bl_ext.user_default.sollumz.ybn.collision_materials import create_collision_material_from_index
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_sollumz.blend')
frag=bpy.data.objects['phantom']; arm=frag.data
PHYS=['chassis','wheel_lf','wheel_rf','wheel_lr','wheel_rr','door_dside_f','door_pside_f','door_dside_r','door_pside_r','bonnet','boot']
for n in PHYS: arm.bones[n].sollumz_use_physics=True
comp=create_empty_object(SollumType.BOUND_COMPOSITE,'phantom.col'); comp.parent=frag
cmat=create_collision_material_from_index(116)   # CAR_METAL
bpy.context.view_layer.update()
def verts_world(o):
    me=o.data; v=np.empty(len(me.vertices)*3,np.float32); me.vertices.foreach_get('co',v); v=v.reshape(-1,3)
    # object has parent-inverse-free constraint; mesh coords are bone-local, add object bone position
    return v
bonepos={b.name:np.array(b.head_local) for b in arm.bones}
def world_verts(o):
    b=[c for c in o.constraints if c.type=='COPY_TRANSFORMS'][0].subtarget
    return verts_world(o)+bonepos[b], b
MASS={'chassis':1900,'wheel_lf':25,'wheel_rf':25,'wheel_lr':25,'wheel_rr':25,'door_dside_f':35,'door_pside_f':35,'door_dside_r':40,'door_pside_r':40,'bonnet':28,'boot':22}
# chassis hull bound
cv,_=world_verts(bpy.data.objects['chassis'])
bm=bmesh.new()
for p in cv[::7]: bm.verts.new(p)
bmesh.ops.convex_hull(bm,input=bm.verts[:],use_existing_faces=False)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.dissolve_limit(bm,angle_limit=np.radians(6),verts=bm.verts[:],edges=bm.edges[:])
bmesh.ops.triangulate(bm,faces=bm.faces[:])
me=bpy.data.meshes.new('chassis.col'); bm.to_mesh(me); print('hull tris',len(bm.faces)); bm.free()
ch=create_blender_object(SollumType.BOUND_GEOMETRY,'chassis.col',object_data=me); me.materials.append(cmat)
ch.parent=comp; add_child_of_bone_constraint(ch,frag,'chassis'); ch.child_properties.mass=MASS['chassis']
# per-part boxes / wheel cylinders (location relative to bone)
for n in PHYS[1:]:
    o=bpy.data.objects[n]; v,b=world_verts(o); mn,mx=v.min(0),v.max(0); c=(mn+mx)/2; d=mx-mn
    if n.startswith('wheel'):
        bo=create_bound_cylinder(); bo.dimensions=(d[0],d[1],d[2])   # cylinder axis Y in Sollumz primitives; wheel axis is X -> rotate
        bo.rotation_euler=(0,0,np.radians(90)); bo.scale=(d[1]/2,d[0]/2,d[2]/2) if False else (d[2]/2,d[0]/2,d[2]/2)
    else:
        bo=create_bound_box(); bo.scale=tuple(d)
    bo.name=n+'.col'; bo.data.materials.append(cmat); bo.parent=comp
    add_child_of_bone_constraint(bo,frag,n); bo.location=Vector(c-bonepos[n]); bo.child_properties.mass=MASS[n]
    if n.startswith(('door','bonnet','boot')):
        o.sollumz_is_physics_child_mesh=True
        off=c-bonepos[n]                       # model origin = bound centre (Sollumz adds the bound offset as child matrix)
        co=np.empty(len(o.data.vertices)*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)-off.astype(np.float32)
        o.data.vertices.foreach_set('co',co.ravel()); o.data.update(); o.location=Vector(off)
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_sollumz2.blend')
print('ok')
