# Changelog

## 0.1.1 — 2026-10-09
Corrections issues des essais en jeu de la 0.1.0.
- Portes, capot et coffre exportés dans le drawable principal (ils étaient traités comme enfants physiques, non rendus par le jeu).
- Roue avant gauche : tous les pneus utilisent désormais le shader `vehicle_mesh`.
- Enjoliveurs fusionnés dans l'objet de chaque roue (`pipeline/stageC2.py`).
- Vitres : texture dédiée `phantom_glass_d` (DXT5, canal alpha, ~30 % d'opacité) au lieu de l'atlas opaque (`pipeline/mkglass.py`).
- Occlusion ambiante supprimée des textures (ombres parasites).
- Peinture : noir de jais, seule couleur proposée (`carvariations.meta`).
- Ajout de `gta/meta/textes_gxt2.txt` : nom d'affichage « Rolls-Royce Phantom V (Park Ward) ».
- Bake des normales testé puis écarté (shaders de peinture sans emplacement de normales ; atlas trop fragmenté).
- À revalider en jeu : roues (4 + enjoliveurs), ouverture des portes/capot/coffre, vitres, `wheelScale`, `handling.meta`.

## 0.1.0 — 2026-10-09
Première version fonctionnelle (V1).
- Modèle réel (Nieve5677, CC-BY 4.0) décimé à ~149 000 triangles, aux dimensions réelles (≈ 2,01 × 5,98 × 1,78 m).
- Séparation en pièces : carrosserie, 4 portes, capot, coffre, vitres, habitacle simplifié, optiques, plaques, 4 roues.
- UV et textures 2K (carrosserie) / 1K (roues), DDS DXT1 avec mipmaps.
- Fragment Sollumz : 11 os physiques + os de sièges, phares, poignées, etc.
- Collisions : enveloppe convexe de carrosserie, cylindres de roues, boîtes de portes/capot/coffre.
- LOD : haut, moyen, bas, très bas.
- Fichiers meta et DLC (vehicles, handling, carvariations, carcols, content, setup2).
- Le véhicule apparaît et se conduit normalement en jeu.

### Problèmes connus
- Portes, capot et coffre n'apparaissent pas en jeu.
- La roue avant gauche n'apparaît pas.
- Les enjoliveurs (cercles au centre des roues) ne tournent pas avec les roues : ils sont rattachés à la carrosserie.
- Vitres : rendu en éclats sombres dans la visionneuse de CodeWalker (à vérifier).
- Valeurs de `wheelScale` et de `handling.meta` estimées, non réglées.
