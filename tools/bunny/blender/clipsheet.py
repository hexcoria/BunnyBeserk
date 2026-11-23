# clipsheet.py <anim.blend> <outdir> [view=q|s] : renders 6 frames per clip
import bpy, sys, os, json
sys.path.append(os.path.dirname(__file__)); import rlib
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0]); od = a[1]; view = a[2] if len(a) > 2 else 'q'
os.makedirs(od, exist_ok=True)
sc = rlib.setup(240); sc.display.shading.color_type = 'TEXTURE'
arm = bpy.data.objects['BunnyRig']; arm.hide_render = True; ad = arm.animation_data
# ground line helper: a thin plane at z=0
bpy.ops.mesh.primitive_plane_add(size=0.8, location=(0, -0.05, 0))
cams = {'q': ((0.95, -1.15, 0.55), (0, -0.06, 0.2)), 's': ((1.5, -0.06, 0.2), (0, -0.06, 0.2))}
c = rlib.cam('C', *cams[view], lens=50)
for tr in ad.nla_tracks: tr.mute = True
for tr in ad.nla_tracks:
    act = tr.strips[0].action; ad.action = act
    n = int(act.frame_range[1])
    for i in range(6):
        f = round(i * n / 5); sc.frame_set(f + 1); sc.frame_set(f); bpy.context.view_layer.update()
        rlib.shot(c, os.path.join(od, '%s_%02d.png' % (tr.name, i)))
    ad.action = None
