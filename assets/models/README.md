# 3D Model Spec (HTML / three.js prototype)

- **Format:** `.glb` (binary glTF 2.0), single file, textures embedded. No FBX/OBJ/USDZ.
- **Materials:** PBR metallic-roughness; base color required. Keep textures ≤ 1024×1024.
- **Budget:** ~5k–15k triangles per character.
- **Orientation & scale:** Y-up, 1 unit = 1 metre, character faces +Z, origin at the feet (ground centre).
- **Rig/animation (optional):** If rigged, include clips named `idle`, `hop`/`walk`, `run` inside the same `.glb`.
- **Naming:** `snake_case.glb`, e.g. `bunny_example.glb`.
