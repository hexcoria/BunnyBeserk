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

---

# Example rabbit: `bunny_example`

A rigged, animated cartoon rabbit built to the spec above. The same model, skeleton and nine clips ship in four files.

## Which file for which engine

| File | Use it for | Axes and units |
|---|---|---|
| `bunny_example.glb` | The HTML / three.js prototype, or any glTF viewer | Y up, faces +Z, 1 unit = 1 m |
| `bunny_example_unity.fbx` | Unity | Y up, faces +Z after import, 1 unit = 1 m (Scale Factor 1, Convert Units on) |
| `bunny_example_unreal.fbx` | Unreal Engine | Z up, faces +X, centimetres (about 70 cm tall on import, Import Uniform Scale 1) |
| `bunny_example.blend` | Editing in Blender (4.5 LTS) | Blender's Z up, faces -Y, metres |

All files: about 0.70 m tall, origin at the feet (ground centre), 12,499 triangles, one PBR material with three 1024×1024 maps (embedded in the FBX and glTF files, packed in the `.blend`). No cameras or lights.

**Texture.** Hand-painted cartoon texture from Meshy's texturing (refine) pass on the same base mesh, downscaled from 2048 to 1024: base colour (light-brown fur, cream belly, muzzle, paws and tail, pink inner ears and nose, big dark eyes, red headband with a knot), a normal map and a roughness map. Metalness is 0. In the glTF the roughness sits in the green channel of the metallic-roughness texture.

### Unity notes
- Use rig type **Generic**: the skeleton has rabbit proportions and extra ear and tail bones, so Humanoid retargeting is not a good fit.
- Each clip is a separate take; Unity lists them as `idle_up`, `aim_up`, and so on. Set **Loop Time** on the looping clips (table below).
- The FBX has Blender's usual -90° X node rotation on `Armature` and `Body`. Tick **Bake Axis Conversion** in the Model tab to fold it into the data; the model faces +Z either way.
- The textures are embedded: use **Extract Textures** in the Materials tab if you want them as separate assets (mark `bunny_normal` as a Normal Map if Unity asks).

### Unreal notes
- Import as a **Skeletal Mesh** with **Import Animations** on; each take becomes an Animation Sequence.
- The armature object is named `Armature`, so Unreal does not add it as an extra bone: the skeleton has 29 bones with `root` at the top.
- Smoothing is written per face (`mesh_smooth_type='FACE'`), so there are no smoothing-group warnings.

### Blender notes
- Mesh `Body` (Armature modifier), armature `Armature`.
- All nine actions have fake users and an NLA track each. Only `idle_up`'s track is unmuted; to preview another clip, mute `idle_up` and unmute (or solo) the one you want, or assign the action in the Action Editor.

## Clips (30 fps, all in place)

| Clip | Frames | Length | Playback |
|---|---|---|---|
| `idle_up` | 60 | 2.0 s | loop |
| `aim_up` | 30 | 1.0 s | loop |
| `fire_up` | 12 | 0.4 s | one-shot |
| `strafe_up` | 24 | 0.8 s | loop |
| `idle_fours` | 60 | 2.0 s | loop |
| `hop` | 15 | 0.5 s | loop |
| `run` | 12 | 0.4 s | loop |
| `drop_to_fours` | 8 | 0.27 s | one-shot |
| `rise_to_up` | 8 | 0.27 s | one-shot |

Each take is keyed from frame 0 to its last frame inclusive; on the looping clips the last frame equals the first.

## Skeleton (29 bones)

`root` > `hips` > `spine_01` > `spine_02` > `spine_03` > `neck` > `head` > `ear_L_01/02`, `ear_R_01/02`; `spine_03` > `clavicle_L/R` > `upperarm_L/R` > `forearm_L/R` > `hand_L/R`; `spine_03` > `weapon_stow`; `hips` > `thigh_L/R` > `shin_L/R` > `foot_L/R` > `toe_L/R`; `hips` > `tail`. No leaf/end bones.

- **`root`** sits at the origin on the ground and is not animated for travel (clips are in place); movement comes from code.
- **`hand_L` / `hand_R`**: attach the weapon here when the rabbit is upright (`idle_up`, `aim_up`, `fire_up`, `strafe_up`). The bone runs from the wrist to the paw tip; expect to tune the weapon's local offset and rotation once in the engine.
- **`weapon_stow`**: a non-deforming bone on the upper back (child of `spine_03`), pointing straight up in the rest pose. Re-parent the weapon here on all fours (`idle_fours`, `hop`, `run`) and swap on `drop_to_fours` / `rise_to_up`.
- `root` and `weapon_stow` have no skin weights; every vertex has at most four influences, normalised.

## Known limitations
- **Short arms and legs.** The proportions come from the Meshy base mesh, so the limbs are short for the body.
- **The gallop reads as leaps.** `run` is a bounding gait that looks like a series of jumps rather than a fluid run.
- Tested by re-importing each FBX into a clean Blender 4.5 scene (takes, frame ranges, bone and triangle counts, height and facing all checked). Not yet opened in Unity or Unreal themselves.
