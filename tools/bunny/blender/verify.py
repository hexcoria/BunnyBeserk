# verify.py <fbx> <unity|unreal> <render.png>
import bpy, sys, os, math
sys.path.append(os.path.dirname(os.path.abspath(__file__)))   # rlib.py sits next to this script
from mathutils import Vector
a = sys.argv[sys.argv.index('--')+1:]; f, eng, png = a
# --- raw FBX structure
from io_scene_fbx import parse_fbx
root, ver = parse_fbx.parse(f)
def find(e, name): return [c for c in e.elems if c.id == name]
def props(e):
    d = {}
    for p in find(find(e, b'Properties70')[0], b'P'): d[p.props[0].decode()] = p.props[4:]
    return d
gs = props(find(find(root, b'GlobalSettings')[0], b'Properties70') and find(root, b'GlobalSettings')[0])
print('GLOBAL', {k: gs[k] for k in ('UpAxis', 'UpAxisSign', 'FrontAxis', 'FrontAxisSign', 'CoordAxis', 'CoordAxisSign', 'UnitScaleFactor', 'TimeMode')})
objs = find(root, b'Objects')[0]
models = {m.props[0]: (m.props[1].split(b'\x00\x01')[0].decode(), m.props[2].decode()) for m in find(objs, b'Model')}
stacks = [s.props[1].split(b'\x00\x01')[0].decode() for s in find(objs, b'AnimationStack')]
vids = [(v.props[1].split(b'\x00\x01')[0].decode(), sum(len(c.props[0]) for c in find(v, b'Content') if c.props and isinstance(c.props[0], bytes))) for v in find(objs, b'Video')]
print('STACKS', stacks); print('VIDEO embedded bytes', vids)
par = {}
for c in find(find(root, b'Connections')[0], b'C'):
    if c.props[0] == b'OO' and c.props[1] in models: par[c.props[1]] = c.props[2]
tops = [k for k in models if par.get(k, 0) not in models]
def tree(k, d=0, out=[]):
    out.append('  ' * d + '%s (%s)' % models[k]); kids = [c for c in models if par.get(c) == k]
    if d < 2:
        for c in kids: tree(c, d + 1, out)
    elif kids: out.append('  ' * (d + 1) + '... %d more below' % len(kids))
    return out
for t in tops:
    for line in tree(t, 0, []): print('HIER ' + line)
print('LIMBNODES', sum(1 for v in models.values() if v[1] == 'LimbNode'), 'NULLS', [v[0] for v in models.values() if v[1] == 'Null'], 'MESHES', [v[0] for v in models.values() if v[1] == 'Mesh'])
# --- normal import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=f, use_anim=True)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]; me = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me.data.calc_loop_triangles()
print('IMPORT objects', [(o.name, o.type) for o in bpy.data.objects], 'bones', len(arm.data.bones), 'root bones', [b.name for b in arm.data.bones if not b.parent],
      'tris', len(me.data.loop_triangles), 'images', [(i.name, tuple(i.size), i.packed_file is not None) for i in bpy.data.images])
for ac in bpy.data.actions: print('ACTION %-28s frames %s' % (ac.name, tuple(round(x, 2) for x in ac.frame_range)))
# --- raw axes: import again with no axis conversion, so Blender coords = FBX coords (x unit-factor/100)
def bounds_and_front():
    dg = bpy.context.evaluated_depsgraph_get(); m = me.evaluated_get(dg).to_mesh(); ws = [me.matrix_world @ v.co for v in m.vertices]
    lo = Vector([min(w[i] for w in ws) for i in range(3)]); hi = Vector([max(w[i] for w in ws) for i in range(3)])
    pb = {p.name: arm.matrix_world @ p.head for p in arm.pose.bones}
    toe = (pb['toe_L'] + pb['toe_R']) / 2 - (pb['foot_L'] + pb['foot_R']) / 2
    me.evaluated_get(dg).to_mesh_clear(); return lo, hi, toe
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=f, use_anim=False, use_manual_orientation=True, axis_forward='Y', axis_up='Z', global_scale=1.0)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]; me = [o for o in bpy.data.objects if o.type == 'MESH'][0]
lo, hi, toe = bounds_and_front()
k = 100.0 / float(gs['UnitScaleFactor'][0])   # back to raw FBX numbers
lo, hi, toe = lo * k, hi * k, toe * k
r = lambda v: tuple(round(x, 3) for x in v)
print('RAW FBX bbox min', r(lo), 'max', r(hi), 'toe dir (rest)', r(toe.normalized()))
if eng == 'unity':   # Unity: FBX right-handed Y up -> negate x; units from UnitScaleFactor (cm per unit)
    s = float(gs['UnitScaleFactor'][0]) / 100
    U = lambda v: Vector((-v.x, v.y, v.z))
    lo2, hi2 = U(lo), U(hi)
    print('UNITY bbox (m) x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f  height %.3f m  facing %s' % (min(lo2.x, hi2.x) * s, max(lo2.x, hi2.x) * s, lo.y * s, hi.y * s, lo.z * s, hi.z * s, (hi.y - lo.y) * s, r(U(toe).normalized())))
else:               # Unreal: declared axes == Unreal's import axis system (Z up, front -Y, RH), then Y flipped; units cm
    s = float(gs['UnitScaleFactor'][0])
    U = lambda v: Vector((v.x, -v.y, v.z))
    lo2, hi2 = U(lo), U(hi)
    print('UNREAL bbox (cm) x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f  height %.1f cm  facing %s' % (lo.x * s, hi.x * s, min(lo2.y, hi2.y) * s, max(lo2.y, hi2.y) * s, lo.z * s, hi.z * s, (hi.z - lo.z) * s, r(U(toe).normalized())))
# --- render mid-run from the normal import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=f, use_anim=True)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]; me = [o for o in bpy.data.objects if o.type == 'MESH'][0]
import rlib
sc = rlib.setup(400); sc.render.fps = 30
ad = arm.animation_data_create()
run = [ac for ac in bpy.data.actions if ac.name.split('|')[-1] == 'run' or '|run|' in ac.name or ac.name.endswith('|run')][0]
ad.action = run
if hasattr(ad, 'action_slot') and run.slots: ad.action_slot = run.slots[0]
mid = int(round((run.frame_range[0] + run.frame_range[1]) / 2)); sc.frame_set(mid)
lo, hi, toe = bounds_and_front()
print('RUN action', run.name, 'frame', mid, 'bbox', r(lo), r(hi))
c = (lo + hi) / 2; d = max(hi - lo)
# camera 3/4 front-left of the model's facing, in the imported (Blender Z-up) space
fw = Vector((0, -1, 0)) if eng == 'unity' else Vector((1, 0, 0)); side = fw.cross(Vector((0, 0, 1)))
cam = rlib.cam('C', tuple(c + (fw * 2.2 - side * 1.6 + Vector((0, 0, 0.9))) * d * 1.2), tuple(c), lens=50)
arm.hide_render = True
rlib.shot(cam, os.path.abspath(png)); print('RENDER', png)
