import bpy, sys, os
sys.path.append(os.path.dirname(__file__)); import rlib
a = sys.argv[sys.argv.index('--')+1:]; od = a[1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.context.scene.render.fps = 30; bpy.ops.import_scene.gltf(filepath=a[0])
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]; me = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me.data.calc_loop_triangles()
print('REIMPORT tris', len(me.data.loop_triangles), 'bones', len(arm.data.bones), 'dims', tuple(round(x, 3) for x in me.dimensions), 'imgs', [(i.name, tuple(i.size)) for i in bpy.data.images])
print('ACTIONS', [(ac.name, tuple(ac.frame_range)) for ac in bpy.data.actions])
sc = rlib.setup(640); sc.display.shading.color_type = 'TEXTURE'; sc.render.fps = 30
arm.hide_render = True
ad = arm.animation_data_create()
for tr in list(ad.nla_tracks): ad.nla_tracks.remove(tr)
c = rlib.cam('Q', (0.95, -1.15, 0.6), (0, -0.05, 0.25), lens=55)
def poseof(act, f):
    ad.action = bpy.data.actions[act] if act else None
    if act and hasattr(ad, 'action_slot') and ad.action.slots: ad.action_slot = ad.action.slots[0]
    if not act:
        for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
    sc.frame_set(f + 1); sc.frame_set(f); bpy.context.view_layer.update()
import mathutils
def snap():
    dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
    r = [ (me.matrix_world @ v.co).copy() for v in m.vertices ]; ev.to_mesh_clear(); return r
names = [ac.name for ac in bpy.data.actions]
for n in names:   # loop check: first and last frame give the same mesh
    ac = bpy.data.actions[n]; f0, f1 = int(ac.frame_range[0]), int(ac.frame_range[1])
    poseof(n, f0); A = snap(); poseof(n, f1); B = snap()
    print('LOOPCHECK %-14s max vertex gap first/last frame %.4f m' % (n, max((x - y).length for x, y in zip(A, B))))
poseof(None, 0); rlib.shot(c, os.path.join(od, 'preview_rest.png'))
poseof('idle_up', 0); rlib.shot(c, os.path.join(od, 'preview_upright.png'))
poseof('aim_up', 0); rlib.shot(c, os.path.join(od, 'preview_aim.png'))
poseof('idle_fours', 0); rlib.shot(c, os.path.join(od, 'preview_fours.png'))
poseof('run', 6); rlib.shot(c, os.path.join(od, 'preview_run_mid.png'))
