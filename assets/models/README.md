# 3D Model Spec (HTML / three.js prototype)

- **Format:** `.glb` (binary glTF 2.0), single file, textures embedded. No FBX/OBJ/USDZ.
- **Materials:** PBR metallic-roughness; base color required. Keep textures ≤ 1024×1024.
- **Budget:** ~5k–15k triangles per character.
- **Orientation & scale:** Y-up, 1 unit = 1 metre, character faces +Z, origin at the feet (ground centre).
- **Player rabbit body plan:** **hybrid stance.** Upright on hind legs when idle or using equipment (front paws free); drops to **all fours** to walk/run/hop. Modelled upright in A-pose with front legs long enough to reach the ground when hunched.
- **Rig:** humanoid skeleton (Blender) plus extra bones for ears (`ear_L_01/02`, `ear_R_01/02`) and `tail`. Include `hand_R` / `hand_L` bones (weapon held when upright) and a `weapon_stow` bone on the upper back (weapon slung while on all fours). One armature covers both stances.
- **Animations:** in-place clips inside the same `.glb` (movement comes from code):
  - Upright: `idle_up`, `aim_up`, `fire_up`, `strafe_up` (slow shuffle while firing)
  - All fours: `idle_fours`, `hop` (walk), `run`
  - Transitions: `drop_to_fours`, `rise_to_up` (short, ~0.2–0.3 s)
- **Naming:** `snake_case.glb`, e.g. `bunny_example.glb`.
