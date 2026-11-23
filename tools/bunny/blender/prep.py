# prep.py <in.glb> <out.blend> height=0.7 : weld, scale to height, feet at z=0, centred; keep UVs
import bpy, sys, bmesh
from mathutils import Vector
a = sys.argv[sys.argv.index('--')+1:]; src, out = a[0], a[1]
opt = dict(x.split('=') for x in a[2:]); H = float(opt.get('height', 0.7))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = [x for x in bpy.data.objects if x.type == 'MESH'][0]
o.name = 'Body'; o.data.name = 'Body'
bpy.context.view_layer.objects.active = o; o.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm = bmesh.new(); bm.from_mesh(o.data)
n0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
print('WELD', n0, '->', len(bm.verts))
ws = [v.co for v in bm.verts]
mn = Vector([min(w[i] for w in ws) for i in range(3)]); mx = Vector([max(w[i] for w in ws) for i in range(3)])
s = H / (mx.z - mn.z); c = Vector(((mn.x+mx.x)/2, (mn.y+mx.y)/2, mn.z))
for v in bm.verts: v.co = (v.co - c) * s
bm.to_mesh(o.data); bm.free()
# loose parts
import collections
o.data.update()
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.mesh.customdata_custom_splitnormals_clear() if o.data.has_custom_normals else None
for poly in o.data.polygons: poly.use_smooth = True
me = o.data; me.calc_loop_triangles()
print('TRIS', len(me.loop_triangles), 'VERTS', len(me.vertices), 'DIMS', tuple(round(d,3) for d in o.dimensions))
bpy.ops.wm.save_as_mainfile(filepath=out)
