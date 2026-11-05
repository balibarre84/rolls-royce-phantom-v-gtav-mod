# Stage R : peinture bi-ton. Ajoute le matériau « carpaint_secondary » (vehicle_paint1, couche de peinture SECONDAIRE :
# matDiffuseColor = (2, 2, 2)) et l'applique au capot et au toit. Le reste de la carrosserie garde « carpaint » (couche PRIMAIRE).
# La couleur réelle est choisie en jeu par carvariations.meta (indices primaire / secondaire).
# Usage (bpy, Sollumz 2.9.0) :  python stageR.py <entrée.blend> <sortie.blend>
import sys, bpy, addon_utils
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
from bl_ext.user_default.sollumz.sollumz_properties import LODLevel
SRC, DST = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
prim = bpy.data.materials['carpaint']
if 'carpaint_secondary' in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials['carpaint_secondary'])
sec = prim.copy(); sec.name = 'carpaint_secondary'
n = sec.node_tree.nodes['matDiffuseColor']; n.outputs['Y'].default_value = 2.0; n.outputs['Z'].default_value = 2.0   # couche SECONDARY
ROOF_Z, ROOF_NZ = 1.62, 0.35
tot = {}
for name in ('bonnet', 'chassis'):
    o = bpy.data.objects[name]
    for lv in (LODLevel.HIGH, LODLevel.MEDIUM, LODLevel.LOW, LODLevel.VERYLOW):
        me = o.sz_lods.get_lod(lv).mesh
        if me is None: continue
        pi = [i for i, m in enumerate(me.materials) if m and m.name == 'carpaint']
        if not pi: continue
        if sec.name not in [m.name for m in me.materials if m]: me.materials.append(sec)
        si = [i for i, m in enumerate(me.materials) if m and m.name == sec.name][0]
        k = 0
        for p in me.polygons:
            if p.material_index != pi[0]: continue
            if name == 'bonnet' or (p.center.z > ROOF_Z and p.normal.z > ROOF_NZ): p.material_index = si; k += 1
        tot[(name, lv.name)] = k
print('faces passées en peinture secondaire :', tot)
dp = bpy.data.objects['phantomv.mesh'].drawable_properties
dp.lod_dist_high = dp.lod_dist_med = dp.lod_dist_low = dp.lod_dist_vlow = 9998   # seuils pilotés par vehicles.meta (lodDistances)
bpy.ops.wm.save_as_mainfile(filepath=DST, relative_remap=False)
