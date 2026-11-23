# build_exports2.py <anim.blend> <outdir> [bst]: bunny_example.blend, bunny_example_unity.fbx, bunny_example_unreal.fbx
# Also writes <outdir>/../unreal_work.blend (the scene after the Unreal turn/scale, for debugging). 'bst' = bake_space_transform on the Unity FBX (not used for the shipped files).
import bpy, sys, os, math
from mathutils import Matrix
a = sys.argv[sys.argv.index('--')+1:]; src, od = a[0], a[1]; BST = len(a) > 2 and a[2] == 'bst'
bpy.ops.wm.open_mainfile(filepath=src)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type not in ('MESH', 'ARMATURE'): bpy.data.objects.remove(o)
for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)
for l in list(bpy.data.lights): bpy.data.lights.remove(l)
arm = bpy.data.objects['BunnyRig']; body = bpy.data.objects['Body']
arm.name = 'Armature'; arm.data.name = 'Armature'
# same weight clean-up as the glb export (max 4 influences, normalised)
bpy.context.view_layer.objects.active = body; bpy.ops.object.select_all(action='DESELECT'); body.select_set(True)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
ad = arm.animation_data; ad.action = None
for ac in bpy.data.actions: ac.use_fake_user = True
for tr in ad.nla_tracks:
    tr.mute = False; tr.is_solo = False
    for s in tr.strips: s.mute = False
def rest():
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
rest(); sc.frame_start, sc.frame_end = 0, 60; sc.render.fps = 30; sc.frame_set(0)
bpy.ops.file.pack_all()
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(od, 'bunny_example.blend'), compress=True, copy=True)
print('SAVED blend')

# For the exports only: an active 'rest' action, so the static pose written to the FBX (bone Lcl transforms) is the bind pose
# rather than the NLA result at frame 0. Not an NLA strip, so it is not exported as a take.
def add_rest_action():
    ra = bpy.data.actions.new('_rest'); ad.action = ra
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
        pb.keyframe_insert('rotation_quaternion', frame=0); pb.keyframe_insert('location', frame=0)
    if hasattr(ad, 'action_slot') and ra.slots: ad.action_slot = ra.slots[0]
    sc.frame_set(0)
add_rest_action()
def sel():
    bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
COMMON = dict(use_selection=True, object_types={'ARMATURE', 'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='FACE',
    use_tspace=True, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False,
    armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0,
    path_mode='COPY', embed_textures=True, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
    use_custom_props=False)

# Unity: metres, Y up; Blender -Y front -> FBX +Z -> Unity +Z
sel(); rest()
bpy.ops.export_scene.fbx(filepath=os.path.join(od, 'bunny_example_unity.fbx'), axis_forward='-Z', axis_up='Y', bake_space_transform=BST, **COMMON)
print('EXPORTED unity')

# Unreal: centimetres, Z up, character faces +X. Turn and scale the data itself (no node transforms):
# rotate +90 deg about Z (front -Y -> +X) and x100; scene unit scale 0.01 so the FBX unit factor is 1 (cm).
M = Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Scale(100, 4)
body.data.transform(M)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
R3 = M.to_3x3().normalized()
old = {eb.name: (eb.head.copy(), eb.tail.copy(), eb.z_axis.copy()) for eb in arm.data.edit_bones}
for eb in arm.data.edit_bones:   # set all at once (eb.transform one by one double-moves connected children)
    h, t, z = old[eb.name]; eb.head = M @ h; eb.tail = M @ t
for eb in arm.data.edit_bones: eb.align_roll(R3 @ old[eb.name][2])
bpy.ops.object.mode_set(mode='OBJECT')
for ac in bpy.data.actions:
    for fc in ac.fcurves:
        if fc.data_path.endswith('.location') and ac.name != '_rest':
            for k in fc.keyframe_points:
                k.co[1] *= 100; k.handle_left[1] *= 100; k.handle_right[1] *= 100
sc.unit_settings.scale_length = 0.01; sc.unit_settings.length_unit = 'CENTIMETERS'
sel(); rest()
bpy.ops.export_scene.fbx(filepath=os.path.join(od, 'bunny_example_unreal.fbx'), axis_forward='Y', axis_up='Z', bake_space_transform=False, **COMMON)
print('EXPORTED unreal'); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(od, '..', 'unreal_work.blend'), copy=True)
