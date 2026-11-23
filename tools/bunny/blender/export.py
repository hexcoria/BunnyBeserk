# export.py <anim.blend> <out.glb>
import bpy, sys
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0]); out = a[1]
arm = bpy.data.objects['BunnyRig']; body = bpy.data.objects['Body']
for o in list(bpy.data.objects):
    if o.type not in ('MESH', 'ARMATURE'): bpy.data.objects.remove(o)
bpy.context.view_layer.objects.active = body; bpy.ops.object.select_all(action='DESELECT'); body.select_set(True)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
ad = arm.animation_data; ad.action = None
for tr in ad.nla_tracks: tr.mute = False; tr.is_solo = False
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.scene.frame_set(0)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=False, export_yup=True, export_apply=False,
    export_cameras=False, export_lights=False, export_texcoords=True, export_normals=True, export_materials='EXPORT',
    export_image_format='AUTO', export_skins=True, export_def_bones=False, export_influence_nb=4,
    export_animations=True, export_animation_mode='NLA_TRACKS', export_force_sampling=True, export_frame_step=1,
    export_anim_slide_to_zero=True, export_optimize_animation_size=False, export_reset_pose_bones=True, export_morph=False)
print('EXPORTED', out)
