# Stage U : tout le véhicule en modèle « skinné » (comme le pack de référence citroends23, un seul modèle, toutes les pièces
# pondérées sur leur os). Les essais en jeu de la 0.1.10 montraient les pièces rigides (portes, capot, coffre, roues) dessinées
# à l'origine du véhicule dès que le drawable contenait le modèle skinné des vitres (stageQ) : mélange rigide / skinné.
# Chaque pièce : sommets en coordonnées du squelette (position de l'os ajoutée), groupe de sommets nommé comme l'os (poids 1),
# contrainte « os parent » retirée (sinon Sollumz ramène les sommets en coordonnées locales de l'os).
# Usage (bpy, Sollumz 2.9.0) :  python stageU.py <entrée.blend> <sortie.blend>
import sys, bpy, addon_utils
from mathutils import Vector
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
from bl_ext.user_default.sollumz.sollumz_properties import SollumType, LODLevel
SRC, DST = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
frag = bpy.data.objects['phantomv']; arm = frag.data
heads = {b.name: Vector(b.head_local) for b in arm.bones}
LODL = (LODLevel.HIGH, LODLevel.MEDIUM, LODLevel.LOW, LODLevel.VERYLOW)
done = {}
for o in [o for o in bpy.data.objects if o.type == 'MESH' and o.sollum_type == SollumType.DRAWABLE_MODEL]:
    cons = [c for c in o.constraints if getattr(c, 'subtarget', '')]
    if not o.vertex_groups:                              # pièce rigide : à convertir (les vitres sont déjà skinnées)
        bone = cons[0].subtarget if cons else 'chassis'
        h = heads[bone]; seen = set()
        for lv in LODL:
            me = o.sz_lods.get_lod(lv).mesh
            if me is None or me.name in seen: continue
            seen.add(me.name)
            if h.length:
                for v in me.vertices: v.co += h
                me.update()
            o.sz_lods.active_lod_level = lv              # les groupes de sommets appartiennent au maillage de chaque LOD :
            assert o.data is me, (o.name, lv)            # il faut activer le niveau (écrire o.data écraserait le LOD actif)
            vg = o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone)
            vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
        done[o.name] = bone
    for c in cons: o.constraints.remove(c)
    o.sz_lods.set_highest_lod_active()
print('pièces passées en skinné :', done)
bpy.ops.wm.save_as_mainfile(filepath=DST, relative_remap=False)
