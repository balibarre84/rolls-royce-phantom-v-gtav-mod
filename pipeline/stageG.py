import bpy, math
from mathutils import Vector, Matrix
from bl_ext.user_default.sollumz.sollumz_properties import SollumType, LODLevel
from bl_ext.user_default.sollumz.tools.blenderhelper import create_blender_object, create_empty_object, add_child_of_bone_constraint
from bl_ext.user_default.sollumz.ydr.shader_materials import create_shader
from bl_ext.user_default.sollumz.tools.meshhelper import get_color_attr_name, create_uv_attr
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend')
addon_ok=True
import addon_utils; addon_utils.enable('bl_ext.user_default.sollumz',default_set=True)
NAME='phantom'
body_img=bpy.data.images['phantom_body_d']; wheel_img=bpy.data.images['phantom_wheels_d']
for im,fn in ((body_img,'phantom_body_d'),(wheel_img,'phantom_wheels_d')):
    im.source='FILE'; im.filepath=f'/home/claude/work/tex/{fn}.dds'; im.reload()
    print('img',im.name,im.size[:],im.filepath)
glass_img=bpy.data.images.load('/home/claude/work/tex/phantom_glass_d.dds'); glass_img.name='phantom_glass_d'
# ---- Sollumz materials
SHADER={'carpaint':'vehicle_paint1.sps','chrome':'vehicle_mesh.sps','black':'vehicle_mesh.sps','white':'vehicle_mesh.sps','mirror':'vehicle_mesh.sps',
 'interior_second':'vehicle_interior.sps','interior_third':'vehicle_interior.sps','interior_fourth':'vehicle_interior.sps',
 'clearglass':'vehicle_vehglass.sps','windowglass':'vehicle_vehglass.sps',
 'greenglass':'vehicle_lightsemissive.sps','orangeglass':'vehicle_lightsemissive.sps','redglass':'vehicle_lightsemissive.sps','yellow':'vehicle_lightsemissive.sps',
 'tire':'vehicle_mesh.sps','rim':'vehicle_mesh.sps','brakedisk':'vehicle_mesh.sps'}
newmat={}
import re
def sollum_mat(old):
    base=re.sub(r'\.\d+$','',old.name)                      # one Sollumz material per base name (tire.001 -> tire)
    if base in newmat: return newmat[base]
    sh=SHADER.get(base,'vehicle_mesh.sps'); m=create_shader(sh); old.name=old.name+'_old'; m.name=base
    newmat[base]=m; return m
def set_diffuse(m,img):
    for n in m.node_tree.nodes:
        if n.bl_idname=='ShaderNodeTexImage' and n.name=='DiffuseSampler': n.image=img
# ---- skeleton
sc=bpy.context.scene
loc={o.name:o.location.copy() for o in bpy.data.objects if o.type=='MESH'}
BONES=[('chassis',(0,0,0.0),None)]
for n in ('wheel_lf','wheel_rf','wheel_lr','wheel_rr'): BONES.append((n,tuple(loc[n]),'chassis'))
for n in ('door_dside_f','door_pside_f','door_dside_r','door_pside_r','bonnet','boot'): BONES.append((n,tuple(loc[n]),'chassis'))
EXTRA=[('seat_dside_f',(-0.40,0.15,0.62)),('seat_pside_f',(0.40,0.15,0.62)),('seat_dside_r',(-0.40,-0.85,0.62)),('seat_pside_r',(0.40,-0.85,0.62)),
 ('steeringwheel',(-0.40,0.55,1.00)),('headlight_l',(-0.72,2.50,0.78)),('headlight_r',(0.72,2.50,0.78)),('taillight_l',(-0.75,-3.28,0.75)),('taillight_r',(0.75,-3.28,0.75)),
 ('engine',(0,1.90,0.75)),('exhaust',(0.55,-3.00,0.35)),('petrolcap',(0.85,-2.20,0.95)),('windscreen',(0,0.75,1.30)),('windscreen_r',(0,-2.10,1.35)),
 ('handles_dside_f',(-0.98,0.10,0.95)),('handles_pside_f',(0.98,0.10,0.95)),('handles_dside_r',(-0.98,-0.75,0.95)),('handles_pside_r',(0.98,-0.75,0.95))]
for n,p in EXTRA: BONES.append((n,p,'chassis'))
arm=bpy.data.armatures.new(NAME+'.skel')
frag=create_blender_object(SollumType.FRAGMENT,NAME,object_data=arm)
bpy.context.view_layer.objects.active=frag; bpy.ops.object.mode_set(mode='EDIT')
eb={}
for n,p,par in BONES:
    b=arm.edit_bones.new(n); b.head=(0,0,0); b.tail=(0,0.05,0); b.matrix=Matrix.Translation(Vector(p))
    if par: b.parent=eb[par]
    eb[n]=b
bpy.ops.object.mode_set(mode='OBJECT')
# ---- drawable and models
draw=create_empty_object(SollumType.DRAWABLE,NAME+'.mesh'); draw.parent=frag
BONE_OF=lambda n: n if n in ('chassis','wheel_lf','wheel_rf','wheel_lr','wheel_rr','door_dside_f','door_pside_f','door_dside_r','door_pside_r','bonnet','boot') else 'chassis'
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.sollum_type!=SollumType.FRAGMENT]:
    me=o.data
    for i,s in enumerate(o.material_slots):
        if s.material and s.material.sollum_type!=bpy.types.Material.bl_rna: 
            nm=sollum_mat(s.material); set_diffuse(nm, glass_img if nm.name in ('clearglass','windowglass') else (wheel_img if o.name.startswith('wheel') else body_img)); s.material=nm
    if not me.uv_layers: create_uv_attr(me,0)
    else:
        me.uv_layers[0].name='UVMap 0'
    for k in (1,2):
        nmk=f'UVMap {k}'
        if nmk not in me.uv_layers:
            l=me.uv_layers.new(name=nmk)
            src=me.uv_layers['UVMap 0']; import numpy as np
            buf=np.empty(len(me.loops)*2,np.float32); src.data.foreach_get('uv',buf); l.data.foreach_set('uv',buf)
    cn=get_color_attr_name(0)
    if cn not in me.color_attributes:
        ca=me.color_attributes.new(cn,'BYTE_COLOR','CORNER'); import numpy as np
        ca.data.foreach_set('color',np.ones(len(me.loops)*4,np.float32))
    o.sollum_type=SollumType.DRAWABLE_MODEL
    o.sz_lods.get_lod(LODLevel.HIGH).mesh=me; o.sz_lods.active_lod_level=LODLevel.HIGH
    o.parent=draw
    bone=BONE_OF(o.name)
    o.location=Vector()
    add_child_of_bone_constraint(o,frag,bone)
td=bpy.context.scene.sz_txds.new_texture_dictionary('phantom')
td.new_texture(body_img); td.new_texture(wheel_img); td.new_texture(glass_img)
print('built; objects:',[ (o.name,o.sollum_type) for o in bpy.data.objects][:30])
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantom_sollumz.blend')
