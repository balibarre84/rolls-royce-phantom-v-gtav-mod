import bpy
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_parts_uv.blend')
for im in bpy.data.images:
    if im.name in('phantom_body_d','phantom_wheels_d'): im.filepath='//tex/'+im.name+'.png'; im.reload()
    elif im.name.startswith('phantom_') or im.name.endswith('_raw'): 
        if im.users==0: bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/deliver/phantom_v_parkward_gta_parts.blend',relative_remap=False)
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.type=='MESH': print(o.name,len(o.data.polygons),[m.name for m in o.data.materials][:2])
print('total',sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH'))
