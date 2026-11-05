# Stage S : limites de rotation des pièces mobiles (bloc Joints / RotationLimits du drawable).
# Valeurs reprises du pack de référence citroends23 (axe Z pour les portes, axe X pour le capot et le coffre ; radians).
# Sollumz exporte une contrainte « Limit Rotation » (espace local) d'un os comme limite de rotation de cet os.
# Usage (bpy, Sollumz 2.9.0) :  python stageS.py <entrée.blend> <sortie.blend>
import sys, bpy, addon_utils
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
SRC, DST = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
frag = bpy.data.objects['phantomv']
# nom d'os : (axe, min, max)
LIM = {'door_dside_f': ('z', -1.134464, 0), 'door_dside_r': ('z', -1.134464, 0),
       'door_pside_f': ('z', 0, 1.134464), 'door_pside_r': ('z', 0, 1.134464),
       'boot': ('x', -1.06465089, 0), 'bonnet': ('x', 0, 0.9075712)}
for name, (ax, lo, hi) in LIM.items():
    pb = frag.pose.bones[name]
    for c in [c for c in pb.constraints if c.type == 'LIMIT_ROTATION']: pb.constraints.remove(c)
    c = pb.constraints.new('LIMIT_ROTATION'); c.owner_space = 'LOCAL'
    for a in 'xyz':
        setattr(c, f'use_limit_{a}', True); setattr(c, f'min_{a}', lo if a == ax else 0.0); setattr(c, f'max_{a}', hi if a == ax else 0.0)
print('limites de rotation :', {n: frag.pose.bones[n].constraints[0].type for n in LIM})
bpy.ops.wm.save_as_mainfile(filepath=DST, relative_remap=False)
