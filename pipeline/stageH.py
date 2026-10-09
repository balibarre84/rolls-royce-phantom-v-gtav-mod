import bpy, addon_utils
addon_utils.enable('bl_ext.user_default.sollumz',default_set=True)
bpy.ops.wm.open_mainfile(filepath='/home/claude/work/phantom_sollumz2.blend')
import os; out='/home/claude/work/export_test'; os.makedirs(out,exist_ok=True)
r=bpy.ops.sollumz.export_assets(directory=out,direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=False)
print('export',r)
r2=bpy.ops.sollumz.export_ytd(directory=out,direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=False)
print('ytd',r2)
for root,d,f in os.walk(out):
    for x in f: print(os.path.join(root,x),os.path.getsize(os.path.join(root,x)))
