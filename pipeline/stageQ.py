# Stage Q : découpe du verre en vitres indépendantes et cassables (VehicleGlassWindows).
# Usage (Blender/bpy, Sollumz 2.9.0) :  python stageQ.py <entrée.blend> <sortie.blend>
# Chaque vitre devient : un modèle de dessin rattaché à un os physique + une collision « fenêtre de véhicule »
# (mode Sollumz « Simple » = cassable sans shattermap, comme le pack de référence citroends23).
import sys, bpy, bmesh, numpy as np, addon_utils
from mathutils import Vector, Matrix
addon_utils.enable('bl_ext.user_default.sollumz', default_set=True)
from bl_ext.user_default.sollumz.sollumz_properties import SollumType, LODLevel
from bl_ext.user_default.sollumz.tools.blenderhelper import create_blender_object, add_child_of_bone_constraint
from bl_ext.user_default.sollumz.tools.boundhelper import create_bound_box
from bl_ext.user_default.sollumz.ybn.collision_materials import create_collision_material_from_index
from bl_ext.user_default.sollumz.ydr.shader_materials import create_shader

SRC, DST = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
frag = bpy.data.objects['phantomv']; arm = frag.data
draw = bpy.data.objects['phantomv.mesh']; comp = bpy.data.objects['phantomv.col']
glass = bpy.data.objects['glass']
HI = glass.sz_lods.get_lod(LODLevel.HIGH).mesh
LODS = ((LODLevel.MEDIUM, 0.35, 'med'), (LODLevel.LOW, 0.10, 'low'), (LODLevel.VERYLOW, 0.03, 'vlow'))
TILING = 2.345  # CracksTextureTiling du pack de référence

# ---- 1. composantes connexes du verre : on garde en l'état les petites pièces (optiques, cloison)
bm = bmesh.new(); bm.from_mesh(HI); bm.faces.ensure_lookup_table()
seen, comps = set(), []
for f in bm.faces:
    if f.index in seen: continue
    st, cf = [f], []; seen.add(f.index)
    while st:
        x = st.pop(); cf.append(x.index)
        for e in x.edges:
            for y in e.link_faces:
                if y.index not in seen: seen.add(y.index); st.append(y)
    comps.append(cf)
bm.free()
def stats(idx):
    bm2 = bmesh.new(); bm2.from_mesh(HI); bm2.faces.ensure_lookup_table()
    co = np.array([v.co[:] for i in idx for v in bm2.faces[i].verts]); mats = {bm2.faces[i].material_index for i in idx}; bm2.free()
    return co, mats
panes = []
for idx in comps:
    co, mats = stats(idx); mn, mx = co.min(0), co.max(0)
    if mats == {1} and (mx - mn).max() > 0.3: panes.append((idx, co))   # vitres teintées de grande taille

def role(c):
    c = c.mean(0)
    if abs(c[0]) < 0.2 and c[1] > 0.4: return 'windscreen'
    if abs(c[0]) < 0.2 and c[1] < -2.0: return 'windscreen_r'
    return None
sides = {'l': [], 'r': []}; named = {}
for idx, co in panes:
    r = role(co)
    if r: named[r] = (idx, co)
    else: sides['l' if co[:, 0].mean() < 0 else 'r'].append((idx, co))
SIDE = {'l': ('misc_a', 'window_lf', 'window_lr', 'misc_c'), 'r': ('misc_b', 'window_rf', 'window_rr', 'misc_d')}
for s in 'lr':
    for nm, (idx, co) in zip(SIDE[s], sorted(sides[s], key=lambda t: -t[1][:, 1].mean())): named[nm] = (idx, co)
assert len(named) == 10, sorted(named)
PARENT = {'window_lf': 'door_dside_f', 'window_lr': 'door_dside_r', 'window_rf': 'door_pside_f', 'window_rr': 'door_pside_r'}
print('vitres :', {k: len(v[0]) for k, v in named.items()})

# ---- 2. os des vitres (les os windscreen / windscreen_r existent déjà)
heads = {n: np.array(b.head_local) for n, b in ((b.name, b) for b in arm.bones)}
box = {}
for n, (idx, co) in named.items():                       # boîte de collision orientée (plan de la vitre)
    cen = co.mean(0); w, V = np.linalg.eigh(np.cov((co - cen).T)); nrm = V[:, 0]
    want = {'windscreen': (0, 1, 0), 'windscreen_r': (0, -1, 0)}.get(n, (-1, 0, 0) if n in ('window_lf', 'window_lr', 'misc_a', 'misc_c') else (1, 0, 0))
    if float(np.dot(nrm, want)) < 0: nrm = -nrm
    nrm = Vector(nrm); u = Vector((0, 0, 1)).cross(nrm).normalized(); v = nrm.cross(u)
    P = np.array([[(Vector(p) - Vector(cen)).dot(u), (Vector(p) - Vector(cen)).dot(v), (Vector(p) - Vector(cen)).dot(nrm)] for p in co])
    lo, hi = P.min(0), P.max(0); c3 = Vector(cen) + u * ((lo[0] + hi[0]) / 2) + v * ((lo[1] + hi[1]) / 2) + nrm * ((lo[2] + hi[2]) / 2)
    box[n] = (c3, Matrix((u, v, nrm)).transposed(), (hi[0] - lo[0], hi[1] - lo[1], max(hi[2] - lo[2], 0.03)))
new_bones = [n for n in named if n not in heads]
bpy.context.view_layer.objects.active = frag; bpy.ops.object.mode_set(mode='EDIT')
for n in new_bones:
    b = arm.edit_bones.new(n); b.head = (0, 0, 0); b.tail = (0, 0.05, 0); b.matrix = Matrix.Translation(box[n][0])
    b.parent = arm.edit_bones[PARENT.get(n, 'chassis')]
bpy.ops.object.mode_set(mode='OBJECT')
for n in named: arm.bones[n].sollumz_use_physics = True
heads = {b.name: np.array(b.head_local) for b in arm.bones}

# ---- 3. modèles de dessin, collisions, retrait du verre d'origine
cmat = create_collision_material_from_index(121)         # CAR_GLASS_MEDIUM
glass_mat = [m for m in HI.materials if m.name == 'windowglass'][0]
def decimated(mesh, ratio, name):
    tmp = bpy.data.objects.new('tmp', mesh.copy()); bpy.context.collection.objects.link(tmp)
    md = tmp.modifiers.new('d', 'DECIMATE'); md.decimate_type = 'COLLAPSE'; md.ratio = ratio; md.use_collapse_triangulate = True
    ev = tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()); new = bpy.data.meshes.new_from_object(ev); new.name = name
    old = tmp.data; bpy.data.objects.remove(tmp); bpy.data.meshes.remove(old); return new
for n, (idx, co) in named.items():
    b = bmesh.new(); b.from_mesh(HI); b.faces.ensure_lookup_table()
    keep = set(idx); bmesh.ops.delete(b, geom=[f for f in b.faces if f.index not in keep], context='FACES')
    bmesh.ops.delete(b, geom=[v for v in b.verts if not v.link_faces], context='VERTS')
    me = bpy.data.meshes.new(n); b.to_mesh(me); b.free()
    for m in HI.materials: me.materials.append(m)
    o = create_blender_object(SollumType.DRAWABLE_MODEL, n, object_data=me)
    o.sz_lods.get_lod(LODLevel.HIGH).mesh = me; o.sz_lods.active_lod_level = LODLevel.HIGH
    # modèle « skinné » : poids 1 sur l'os de la vitre (le jeu et Sollumz exigent BlendIndices = os de la vitre) ;
    # les sommets restent donc en coordonnées du squelette, non relatives à l'os
    o.parent = draw; o.location = Vector()
    o.vertex_groups.new(name=n).add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    for lv, ratio, tag in LODS: o.sz_lods.get_lod(lv).mesh = decimated(me, ratio, f'{n}_{tag}')
    o.sz_lods.set_highest_lod_active()
    c3, R, dims = box[n]
    bo = create_bound_box(); bo.name = n + '.col'; bo.data.materials.append(cmat); bo.parent = comp
    add_child_of_bone_constraint(bo, frag, n); bo.location = Vector(c3 - Vector(heads[n]))
    bo.rotation_euler = R.to_euler(); bo.scale = dims; bo.child_properties.mass = 1.0
    bo.child_properties.shattermap_mode = 'MANUAL_NO_SHATTERMAP'; bo.vehicle_window_properties.cracks_texture_tiling = TILING
# verre restant (optiques, cloison) : on retire les vitres puis on régénère ses LOD
b = bmesh.new(); b.from_mesh(HI); b.faces.ensure_lookup_table()
rm = {i for idx, _ in named.values() for i in idx}
bmesh.ops.delete(b, geom=[f for f in b.faces if f.index in rm], context='FACES')
bmesh.ops.delete(b, geom=[v for v in b.verts if not v.link_faces], context='VERTS')
b.to_mesh(HI); b.free(); HI.update()
for lv, ratio, tag in LODS: glass.sz_lods.get_lod(lv).mesh = decimated(HI, ratio, f'glass_{tag}')
glass.sz_lods.set_highest_lod_active()
print('verre restant :', len(HI.polygons), 'faces')
bpy.ops.wm.save_as_mainfile(filepath=DST, relative_remap=False)
