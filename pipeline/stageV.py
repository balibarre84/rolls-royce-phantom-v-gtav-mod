# Stage V : chrome à la manière du pack citroends23 (et de GTA V) + conducteur légèrement avancé.
# Chrome GTA V : vehicle_mesh avec une texture de couleur très sombre (krom2, ≈ 8 % de gris), une carte de brillance claire
# (krom2_s, ≈ 73 %), un relief neutre (blank_normal) et la saleté du jeu (vehicle_genericmud_car) : la caisse reflète
# l'environnement au lieu d'afficher un gris peint. Appliqué aux matériaux « chrome » et « rim » (jantes / enjoliveurs).
# krom2 et krom2_s sont ajoutés au dictionnaire de textures (gta/tex, gta/yft_xml/phantomv, phantomv.ytd.xml via post.py).
# Usage (bpy, Sollumz 2.9.0) :  python stageV.py <entrée.blend> <sortie.blend>
import sys, bpy, addon_utils
from mathutils import Vector, Matrix
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
SRC, DST = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
def img(name, path=None):
    im = bpy.data.images.get(name)
    if im is None: im = bpy.data.images.new(name, 4, 4)
    im.source = 'FILE'; im.filepath = path or f'//{name}.dds'   # Sollumz exporte le nom du fichier ; blank_normal / vehicle_genericmud_car viennent du jeu (vehshare)
    return im
TEX = {'DiffuseSampler': img('krom2', '//../tex/krom2.dds'), 'SpecSampler': img('krom2_s', '//../tex/krom2_s.dds'),
       'BumpSampler': img('blank_normal'), 'DirtSampler': img('vehicle_genericmud_car')}
for mn in ('chrome', 'rim'):
    m = bpy.data.materials[mn]
    for k, im in TEX.items():
        nd = m.node_tree.nodes[k]; nd.image = im
        nd.texture_properties.embedded = False
td = bpy.context.scene.sz_txds.texture_dictionaries[0]
have = {t.image.name for t in td.textures if t.image}
for n in ('krom2', 'krom2_s'):
    if n not in have: td.new_texture(bpy.data.images[n])
# conducteur avancé de 10 cm
frag = bpy.data.objects['phantomv']; arm = frag.data
bpy.context.view_layer.objects.active = frag; bpy.ops.object.mode_set(mode='EDIT')
arm.edit_bones['seat_dside_f'].matrix = Matrix.Translation(Vector((0.38, 0.25, 0.72)))
bpy.ops.object.mode_set(mode='OBJECT')
print('siège conducteur :', tuple(round(x, 2) for x in arm.bones['seat_dside_f'].head_local))
bpy.ops.wm.save_as_mainfile(filepath=DST, relative_remap=False)
