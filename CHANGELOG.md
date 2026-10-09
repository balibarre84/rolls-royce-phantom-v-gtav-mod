# Changelog

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
