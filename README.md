# Rolls-Royce Phantom V Park Ward — mod GTA V (solo)

Véhicule addon pour GTA V (mode solo, PC) : Rolls-Royce Phantom V limousine Park Ward (1963).
Nom de modèle en jeu : `phantomv`.

**Version actuelle : 0.1.0** (voir `CHANGELOG.md`)

## Contenu
| Dossier | Rôle |
|---|---|
| `gta/yft_xml/` | Export CodeWalker XML : `phantomv.yft.xml.xz` (à décompresser), `phantomv.ytd.xml`, textures DDS |
| `gta/meta/` | `vehicles.meta`, `handling.meta`, `carvariations.meta`, `carcols.meta` |
| `gta/dlc/` | `content.xml`, `setup2.xml` |
| `gta/tex/` | Textures DDS (carrosserie 2K, roues 1K) |
| `gta/blend/` | Scène Blender + Sollumz 2.9.0 (`phantomv_sollumz.blend`) |
| `pipeline/` | Scripts Blender (bpy) ayant produit le modèle, étape par étape |
| `docs/` | Gabarit (blueprint) et images de contrôle |

## Installation (résumé)
1. Décompresser `phantomv.yft.xml.xz`, importer le `.yft.xml` et le `.ytd.xml` dans CodeWalker (Import XML) pour obtenir `phantomv.yft` et `phantomv.ytd`.
2. Avec OpenIV (mode édition, dossier `mods`) : créer `mods/update/x64/dlcpacks/phantomv/dlc.rpf` contenant `content.xml`, `setup2.xml`, `x64/vehicles.rpf` (le `.yft` et le `.ytd`) et les quatre `.meta` dans `common/data/…`.
3. Ajouter `<Item>dlcpacks:/phantomv/</Item>` dans `mods/update/update.rpf/common/data/dlclist.xml`.
4. Faire apparaître le véhicule avec le nom `phantomv` (mode solo uniquement).

## État connu (0.1.0)
Voir `CHANGELOG.md`. Problèmes constatés en jeu : portes, capot et coffre invisibles, roue avant gauche absente, enjoliveurs de roues non solidaires des roues.

## Crédits et licence
Modèle d'origine : « Rolls Royce Phantom Park Ward Limo HQ Interior » par **Nieve5677**, licence **CC-BY 4.0**
(https://sketchfab.com/3d-models/rolls-royce-phantom-park-ward-limo-hq-interior-6450ca6444354483ad67fe7a6e311927).
Toute redistribution doit conserver cette attribution (voir `CREDITS.txt`). Modifications : décimation, séparation des pièces, UV, textures, collisions, LOD, configuration GTA V.
Outils : Blender, Sollumz (GPL-3.0), CodeWalker, OpenIV.
