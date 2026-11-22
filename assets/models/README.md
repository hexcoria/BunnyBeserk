# 3D Model Spec (HTML / three.js prototype)

- **Format:** `.glb` (binary glTF 2.0), single file, textures embedded. No FBX/OBJ/USDZ.
- **Materials:** PBR metallic-roughness; base color required. Keep textures ≤ 1024×1024.
- **Budget:** ~5k–15k triangles per character.
- **Orientation & scale:** Y-up, 1 unit = 1 metre, character faces +Z, origin at the feet (ground centre).
- **Player rabbit body plan:** upright **biped** (walks/runs on hind legs, front paws free to hold weapons). Modelled in A-pose for rigging.
- **Rig:** humanoid skeleton (Blender) plus extra bones for ears (`ear_L_01/02`, `ear_R_01/02`) and `tail`. Include a `hand_R` / `hand_L` bone so weapons can be parented to it in code.
- **Animations:** clips named `idle`, `walk`, `run` inside the same `.glb`, animated in place (movement comes from code).
- **Naming:** `snake_case.glb`, e.g. `bunny_example.glb`.
