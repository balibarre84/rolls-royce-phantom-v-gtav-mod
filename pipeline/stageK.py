import bpy, addon_utils, os
addon_utils.enable('bl_ext.user_default.sollumz',default_set=True)
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_sollumz3.blend')
bpy.context.view_layer.update()
for n in ('wheel_lf','door_dside_f','bonnet','boot','chassis'): print('MW',n,[round(x,3) for x in bpy.data.objects[n].matrix_world.translation])
bpy.data.objects['phantom'].name='phantomv'; bpy.data.objects['phantom.mesh'].name='phantomv.mesh'; bpy.data.objects['phantom.col'].name='phantomv.col'
td=bpy.context.scene.sz_txds.texture_dictionaries[0]; td.name='phantomv'
for im in bpy.data.images:
    print('img',im.name,im.filepath)
out='/home/claude/deliver2/yft_xml'; os.makedirs(out,exist_ok=True)
kw=dict(directory=out,direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=False)
print(bpy.ops.sollumz.export_assets(**kw)); print(bpy.ops.sollumz.export_ytd(**kw))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/phantomv_final.blend')
for r,d,f in os.walk(out):
    for x in f: print(os.path.join(r,x),os.path.getsize(os.path.join(r,x)))
