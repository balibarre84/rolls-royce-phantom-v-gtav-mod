import bpy, addon_utils
addon_utils.enable('bl_ext.user_default.sollumz',default_set=True)
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantomv_final.blend')
for im in bpy.data.images:
    if im.name.startswith('phantom_'): im.filepath='//../tex/'+im.name+'.dds'
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/deliver2/blend/phantomv_sollumz.blend',relative_remap=False)
