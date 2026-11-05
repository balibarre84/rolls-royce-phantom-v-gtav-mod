# Stage T : corrections issues des tickets Jira MOD-1, MOD-2 et MOD-7.
#  MOD-1  pneus qui clignotent : (a) suppression des faces dupliquées (coïncidentes, même sens) des roues = z-fighting ;
#         (b) matériau « tire » passé au shader vehicle_tire (déformation / patinage corrects), avec les textures
#         de relief, de brillance et de saleté des pneus d'origine du jeu (référencées par nom, comme le pack citroends23).
#  MOD-7  intérieur noir : les matériaux interior_* utilisaient la couche de peinture SECONDAIRE (matDiffuseColor = 2,2,2),
#         donc teintés par la couleur secondaire (noire). Couche « défaut » (2,5,5) : les couleurs de la texture s'affichent telles quelles.
#  MOD-2  conducteur : le volant du modèle est à droite (x ≈ +0,41), les sièges avant ont leurs os à gauche. Sièges avant
#         inversés (conducteur à droite) et relevés de 10 cm ; os du volant placé sur le volant.
# Usage (bpy, Sollumz 2.9.0) :  python stageT.py <entrée.blend> <sortie.blend>
import sys, bpy, bmesh, addon_utils
from mathutils import Vector, Matrix, kdtree
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
from bl_ext.user_default.sollumz.sollumz_properties import LODLevel
from bl_ext.user_default.sollumz.ydr.shader_materials import create_shader
SRC, DST = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
LODL = (LODLevel.HIGH, LODLevel.MEDIUM, LODLevel.LOW, LODLevel.VERYLOW)

# ---- MOD-7 : intérieur
for n in ('interior_second', 'interior_third', 'interior_fourth'):
    nd = bpy.data.materials[n].node_tree.nodes['matDiffuseColor']; nd.outputs['Y'].default_value = 5.0; nd.outputs['Z'].default_value = 5.0

# ---- MOD-1a : faces dupliquées des roues
removed = {}
for w in ('wheel_lf', 'wheel_rf', 'wheel_lr', 'wheel_rr'):
    for lv in LODL:
        me = bpy.data.objects[w].sz_lods.get_lod(lv).mesh
        if me is None: continue
        kd = kdtree.KDTree(len(me.polygons))
        for p in me.polygons: kd.insert(p.center, p.index)
        kd.balance(); drop = set()
        for p in me.polygons:
            if p.index in drop: continue
            for _, i, _ in kd.find_range(p.center, 0.0015):
                if i > p.index and i not in drop and p.normal.dot(me.polygons[i].normal) > 0.99: drop.add(i)
        if drop:
            bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[bm.faces[i] for i in drop], context='FACES')
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
            bm.to_mesh(me); bm.free(); me.update()
        removed[(w, lv.name)] = len(drop)
print('faces dupliquées supprimées :', {k: v for k, v in removed.items() if v})

# ---- MOD-1b : pneus en vehicle_tire
old = bpy.data.materials['tire']
tire = create_shader('vehicle_tire.sps'); tire.name = 'tire_new'
def ph(name):
    # Sollumz exporte le nom de texture = nom du fichier de l'image : on donne un chemin fictif (la texture est dans vehshare)
    im = bpy.data.images.get(name) or bpy.data.images.new(name, 4, 4); im.source = 'FILE'; im.filepath = f'//{name}.dds'; return im
TEX = {'DiffuseSampler': bpy.data.images['phantom_wheels_d'],            # couleur unie de la palette (UV inchangés)
       'DirtSampler': ph('vehicle_generic_tyrewall_dirt'), 'BumpSampler': ph('vehicle_generic_tyrewall_normal'),
       'SpecSampler': ph('vehicle_generic_tyrewall_spec')}
for k, im in TEX.items():
    nd = tire.node_tree.nodes[k]; nd.image = im
    if k != 'DiffuseSampler': nd.texture_properties.embedded = False   # texture du jeu, référencée par nom seulement
old.name = 'tire_old'; tire.name = 'tire'
swapped = 0
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    for lv in LODL:
        try: me = o.sz_lods.get_lod(lv).mesh
        except Exception: me = None
        if me is None: continue
        for i, m in enumerate(me.materials):
            if m == old: me.materials[i] = tire; swapped += 1
print('emplacements de matériau « tire » remplacés :', swapped)

# ---- MOD-2 : sièges avant et volant
frag = bpy.data.objects['phantomv']; arm = frag.data
POS = {'seat_dside_f': (0.38, 0.15, 0.72), 'seat_pside_f': (-0.38, 0.15, 0.72), 'steeringwheel': (0.41, 0.45, 1.09)}
bpy.context.view_layer.objects.active = frag; bpy.ops.object.mode_set(mode='EDIT')
for n, p in POS.items(): arm.edit_bones[n].matrix = Matrix.Translation(Vector(p))
bpy.ops.object.mode_set(mode='OBJECT')
print('os déplacés :', {n: tuple(round(x, 2) for x in arm.bones[n].head_local) for n in POS})
bpy.ops.wm.save_as_mainfile(filepath=DST, relative_remap=False)
