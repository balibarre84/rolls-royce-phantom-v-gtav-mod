import sys, bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
import addon_utils
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
exec(compile(open(sys.argv[1]).read(), sys.argv[1], 'exec'))
