import bpy, numpy as np
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend')
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='FLAT'; sh.color_type='TEXTURE'
cam=bpy.data.cameras.new('c'); cam.lens=40; c=bpy.data.objects.new('c',cam); bpy.context.collection.objects.link(c); sc.camera=c
sc.render.resolution_x=1400; sc.render.resolution_y=800
for n,loc in (('f34',(-6,6,3.5)),('r34',(6,-6.5,3.2))):
    c.location=loc; c.rotation_euler=(Vector((0,0,0.8))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=f'/home/claude/work/tex_{n}.png'; bpy.ops.render.render(write_still=True)
# open a door and the bonnet for a check
import math
bpy.data.objects['door_dside_f'].rotation_euler=(0,0,math.radians(-60))
bpy.data.objects['bonnet'].rotation_euler=(math.radians(-35),0,0)
c.location=(-7,5,3.0); c.rotation_euler=(Vector((0,0.5,0.8))-Vector(c.location)).to_track_quat('-Z','Y').to_euler()
sc.render.filepath='/home/claude/work/tex_open.png'; bpy.ops.render.render(write_still=True)
