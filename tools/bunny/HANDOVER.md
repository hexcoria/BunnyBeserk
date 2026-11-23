# Example rabbit (`bunny_example`): handover

How the example rabbit in `assets/models/` was made, and how to rebuild or change it. The user-facing description of the files is in `assets/models/README.md`; this page is for whoever picks up the build.

## The model

- **Source mesh:** Meshy text-to-3D. Preview task `01a20407-98d3-77fb-b105-71753ab5be81` (meshy-7.1, A-pose, remeshed to ~12k triangles, untextured), refine task `01a207f7-9c4d-7425-ac8a-63cc6eea44d2` (meshy-6, PBR, 2k textures, same geometry). The exact request bodies are in `meshy/preview_req.json` and `meshy/refine_req.json` (a `1k` texture resolution was rejected by the API: it accepts only 2k, 4k or 8k).
- **Mesh:** 12,499 triangles, one mesh `Body`, 0.70 m tall, origin at the feet (ground centre).
- **Material:** one PBR material `Bunny` with three 1024x1024 maps: base colour, normal, roughness (Meshy's 2048 maps downscaled with Lanczos). Metalness 0. In the glTF the roughness sits in the green channel of the metallic-roughness texture.
- **Rig:** one armature, 29 bones, 9 in-place clips at 30 fps.

## Files in `assets/models/`

| File | Engine | Notes |
|---|---|---|
| `bunny_example.glb` | three.js / any glTF viewer | +Y up, faces +Z, 1 unit = 1 m, textures embedded. 4.4 MB with three maps. |
| `bunny_example_unity.fbx` | Unity | Rig type Generic. Tick **Bake Axis Conversion** (the FBX carries Blender's -90 deg X node rotation on `Armature` and `Body`). If you extract the textures, mark `bunny_normal` as a **Normal Map**. Set Loop Time on the looping clips. |
| `bunny_example_unreal.fbx` | Unreal | Z up, faces +X, centimetres (about 70 cm tall at Import Uniform Scale 1). The armature object is called `Armature`, so Unreal adds no extra bone: single root bone `root`. Smoothing per face. |
| `bunny_example.blend` | Blender 4.5 LTS (source) | Z up, faces -Y, metres. All nine actions have fake users and an NLA track each; only `idle_up`'s track is unmuted. Textures packed. |

**Neither FBX has been opened in Unity or Unreal yet.** Both were checked only by re-importing into a clean Blender 4.5 scene (`blender/verify.py`: takes, frame ranges, bone and triangle counts, height, facing).

## Skeleton (29 bones)

```
root
└ hips
  ├ spine_01 > spine_02 > spine_03
  │   ├ neck > head > ear_L_01 > ear_L_02
  │   │             > ear_R_01 > ear_R_02
  │   ├ clavicle_L > upperarm_L > forearm_L > hand_L
  │   ├ clavicle_R > upperarm_R > forearm_R > hand_R
  │   └ weapon_stow
  ├ thigh_L > shin_L > foot_L > toe_L
  ├ thigh_R > shin_R > foot_R > toe_R
  └ tail
```

root, hips, spine_01, spine_02, spine_03, neck, head, ear_L_01, ear_L_02, ear_R_01, ear_R_02, clavicle_L, upperarm_L, forearm_L, hand_L, clavicle_R, upperarm_R, forearm_R, hand_R, weapon_stow, thigh_L, shin_L, foot_L, toe_L, thigh_R, shin_R, foot_R, toe_R, tail. No leaf/end bones.

- `root` sits at the origin and only carries the small in-place bob of each clip; travel comes from code.
- `hand_L` / `hand_R`: weapon attach points while upright (`idle_up`, `aim_up`, `fire_up`, `strafe_up`). Each runs from the wrist to the paw tip, so expect to tune the weapon's local offset and rotation once per engine.
- `weapon_stow`: non-deforming bone on the upper back (child of `spine_03`), pointing straight up at rest. Re-parent the weapon here on all fours (`idle_fours`, `hop`, `run`); swap on `drop_to_fours` / `rise_to_up`.
- `root` and `weapon_stow` have no skin weights. Every vertex has at most four influences, normalised.

## Clips (30 fps, in place)

| Clip | Frames | Length | Playback | Pose function in `blender/anim.py` |
|---|---|---|---|---|
| `idle_up` | 60 | 2.0 s | loop | `idle_up(t)` |
| `aim_up` | 30 | 1.0 s | loop | `aim_up(t)` |
| `fire_up` | 12 | 0.4 s | one-shot | `fire_up(t)` (recoil curve `k`, drives `aim_up(t, recoil)`) |
| `strafe_up` | 24 | 0.8 s | loop | `strafe_up(t)` (on top of `aim_up`) |
| `idle_fours` | 60 | 2.0 s | loop | `idle_fours(t)` |
| `hop` | 15 | 0.5 s | loop | `hop(t)` -> `gait(...)` |
| `run` | 12 | 0.4 s | loop | `run(t)` -> `gait(...)` |
| `drop_to_fours` | 8 | 0.27 s | one-shot | `TRANS` list: blend `idle_up(0)` -> `idle_fours(0)` |
| `rise_to_up` | 8 | 0.27 s | one-shot | `TRANS` list: blend `idle_fours(0)` -> `idle_up(0)` |

Each take is keyed from frame 0 to its last frame inclusive; on the looping clips the last frame equals the first. (Blender's FBX importer shows them as frames 1..N+1.)

## Tools and Blender version

- **Blender 4.5 LTS** (built and checked with 4.5.15; on this machine `~/.local/bin/blender45`). Do not use Blender 5.0.1: its FBX and glTF exporters are broken on Ubuntu.
- `python3` with Pillow for `meshy/downscale.py`; `glbcheck.py` is plain Python (no Blender needed).
- Everything takes its paths as arguments; nothing is hard-coded. The scripts in `blender/` import each other (`samp`, `rlib`, `posekit`, `poses`) from their own folder, so keep them together.
- File-name convention the scripts rely on: `rig.py` writes `<rig>_landmarks.json` next to its output; `paint.py` and `check.py` read `<input>_landmarks.json`; `anim.py` reads the landmarks by replacing `painted` with `rig` in its input name. Keep the names `bunny_rig.blend` / `bunny_painted.blend` in one folder as below.

| Folder | Script | What it does |
|---|---|---|
| `meshy/` | `meshy_dl.py` | Polls a Meshy task and downloads model, thumbnail and maps. Reads `MESHY_API_KEY` from the environment (never stored). GET only, no credits. |
| | `downscale.py` | Refine maps 2048 -> the three 1024 maps `retex.py` loads. Reproduces the shipped maps exactly. |
| | `*_req.json`, `*_resp.json` | The request bodies sent and the task ids returned (no keys, no URLs). |
| `blender/` | `prep.py` | Imports the Meshy glb, welds, scales to 0.70 m, feet at z=0, centred. |
| | `rig.py` (+ `samp.py`) | Finds landmarks (crotch, armpits, neck, ears, tail, back) by slicing a point sample of the mesh, builds the 29-bone armature `BunnyRig`, automatic weights. |
| | `paint.py` | The old placeholder texture, rasterised from position/normal/bone. Its texture is replaced by `retex.py`, but it also creates the `Bunny` material that `retex.py` reuses, so it stays in the chain. |
| | `posekit.py`, `poses.py` | Pose solver (two-bone IK, aim, chest-space hands) and the two base stances `up()` and `fours()`. |
| | `anim.py` | Bakes the nine clips as actions + NLA tracks; writes `<out>_clips.json`. |
| | `retex.py` | Copies the Meshy refine's UVs onto `Body` polygon by polygon (same geometry, so rig, weights and actions are untouched) and swaps in Meshy's maps. `nopbr` = base colour only. |
| | `export.py` | glb export (NLA tracks as clips, 4 influences, Y up). |
| | `build_exports2.py` | Writes `bunny_example.blend`, `bunny_example_unity.fbx`, `bunny_example_unreal.fbx` into the out folder (and `unreal_work.blend` into its parent). |
| | `mute.py` | Run on the saved `.blend`: mutes every NLA track except `idle_up`. |
| | `verify.py` | Re-imports an FBX: takes, hierarchy, bone/tri counts, raw axes, engine-space bbox and facing, renders mid-`run`. |
| | `glbcheck.py`, `reimport.py`, `chkblend.py` | Checks of the glb (raw), the glb re-imported into Blender (loop gaps + preview renders), and the final `.blend`. |
| | `check.py`, `clipsheet.py`, `face.py`, `rlib.py`, `sheet.py`, `cmpmesh.py` | Review renders (rest/upright/aim/fours + weight map; 6 frames per clip; front ortho of the face), the render helper, a contact-sheet joiner (Pillow, plain Python) and a mesh comparer for two glbs. |

## Rebuilding from the Meshy meshes

Run from the repo root. `W` is any work folder outside the repo.

```sh
BL=~/.local/bin/blender45; B=tools/bunny/blender; W=/path/to/work
mkdir -p $W/meshy $W/build $W/tex $W/out $W/renders

# 0. Download the Meshy results (needs the key; Meshy may have expired the task assets, so keep the downloads)
set -a; . ~/.config/hexcoria/meshy.env; set +a
python3 -I tools/bunny/meshy/meshy_dl.py 01a20407-98d3-77fb-b105-71753ab5be81 $W/meshy/preview
python3 -I tools/bunny/meshy/meshy_dl.py 01a207f7-9c4d-7425-ac8a-63cc6eea44d2 $W/meshy/refine

# 1. prep: Meshy preview mesh -> clean, scaled mesh
$BL -b --python $B/prep.py -- $W/meshy/preview/model.glb $W/build/bunny_clean.blend height=0.7
# 2. rig: armature + weights (also writes bunny_rig_landmarks.json)
$BL -b --python $B/rig.py -- $W/build/bunny_clean.blend $W/build/bunny_rig.blend
#    optional review renders: $BL -b --python $B/check.py -- $W/build/bunny_rig.blend $W/renders/chk
# 3. paint: placeholder texture + the 'Bunny' material (texture replaced in step 5)
$BL -b --python $B/paint.py -- $W/build/bunny_rig.blend $W/build/bunny_painted.blend $W/build/bunny_basecolor.png
# 4. anim: the nine clips
$BL -b --python $B/anim.py -- $W/build/bunny_painted.blend $W/build/bunny_anim.blend
#    optional: $BL -b --python $B/clipsheet.py -- $W/build/bunny_anim.blend $W/renders/clips q   (s = side view)
# 5. retex: Meshy refine UVs + maps onto the rigged mesh (add 'nopbr' at the end for base colour only)
python3 -I tools/bunny/meshy/downscale.py $W/meshy/refine $W/tex
$BL -b --python $B/retex.py -- $W/build/bunny_anim.blend $W/meshy/refine/model.glb $W/tex $W/build/bunny_anim_meshy.blend
# 6. export glb + checks
$BL -b --python $B/export.py -- $W/build/bunny_anim_meshy.blend $W/out/bunny_example.glb
python3 -I $B/glbcheck.py $W/out/bunny_example.glb
$BL -b --python $B/reimport.py -- $W/out/bunny_example.glb $W/renders
# 7. .blend + Unity and Unreal FBX
$BL -b --python $B/build_exports2.py -- $W/build/bunny_anim_meshy.blend $W/out
# 8. mute every NLA track but idle_up in the shipped .blend
$BL -b $W/out/bunny_example.blend --python $B/mute.py
# 9. verify
$BL -b --python $B/verify.py -- $W/out/bunny_example_unity.fbx unity $W/renders/check_run_unity.png
$BL -b --python $B/verify.py -- $W/out/bunny_example_unreal.fbx unreal $W/renders/check_run_unreal.png
$BL -b $W/out/bunny_example.blend --python $B/chkblend.py
```

Then copy `$W/out/bunny_example.{glb,blend}` and `bunny_example_{unity,unreal}.fbx` to `assets/models/`.

## Changing the animation

- Each clip is a pose function of `t` in 0..1 in `blender/anim.py` (table above), sampled once per frame and solved by `posekit.solve`. Edit the function, then rerun from step 4 (anim) on: retex, export, build_exports2, mute, verify.
- Lengths and loop flags: the `CLIPS` and `TRANS` lists at the bottom of `anim.py`.
- The two base stances (where the feet and paws go, spine/neck/head pitch, ears, tail) are `up()` and `fours()` in `blender/poses.py`; every clip builds on them. The relaxed and aiming paw targets are in `up()` (`rel`/`relt` and `aw`/`at`, chest space); the all-fours paw and foot targets are in `fours()` (world space).
- `hop` and `run` share `gait()` (stride `A`, `flight` height, spine `flex`, left/right phase `ph_lr`, lift heights).
- Rotations in specs are degrees about the armature's axes (`rx > 0` pitches an upright bone forward). Blender space: faces -Y, left = +X, up = +Z.
- `retex.py` only replaces UVs and material, so it can be rerun on any new `bunny_anim.blend`.

## Known limitations

- **Short arms and legs.** The proportions come from the Meshy base mesh.
- **All fours tips well forward.** The body pitches far forward to bring the short front legs to the ground.
- **Aim paws meet in front of the chest**, not out at arm's length (short arms again).
- **`run` reads as leaps.** It is a bounding gait and looks like a series of jumps rather than a fluid run.
- **Transitions are straight blends** between the first frames of the two idles (plus a small dip), so the feet can slide during `drop_to_fours` / `rise_to_up`.
- **glb size.** 4.4 MB with three 1024 maps. Base colour only is about 1.2 MB: rerun `retex.py ... nopbr` and export again.
- **Not tested in Unity or Unreal.** Only Blender re-imports have been checked.
