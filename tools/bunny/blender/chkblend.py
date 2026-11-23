import bpy
print('OBJS', [(o.name, o.type) for o in bpy.data.objects], 'cams', len(bpy.data.cameras), 'lights', len(bpy.data.lights))
print('ACTIONS', [(a.name, tuple(a.frame_range), a.use_fake_user) for a in bpy.data.actions])
arm = bpy.data.objects['Armature']; ad = arm.animation_data
print('ACTIVE', ad.action, 'NLA', [(t.name, [(s.name, s.action.name, s.frame_start, s.frame_end) for s in t.strips]) for t in ad.nla_tracks])
print('IMAGES', [(i.name, tuple(i.size), i.packed_file is not None) for i in bpy.data.images])
b = bpy.data.objects['Body']; b.data.calc_loop_triangles(); print('TRIS', len(b.data.loop_triangles), 'BONES', len(arm.data.bones), 'mods', [m.type for m in b.modifiers], 'fps', bpy.context.scene.render.fps)
