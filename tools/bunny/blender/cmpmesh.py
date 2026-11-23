# cmpmesh.py <a.glb> <b.glb> : compare raw mesh data (verts, tris, positions, uvs)
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--')+1:]
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=p)
    ms = [o for o in bpy.data.objects if o.type == 'MESH']; o = ms[0]; me = o.data; me.calc_loop_triangles()
    V = np.array([o.matrix_world @ v.co for v in me.vertices]); UV = np.array([d.uv[:] for d in me.uv_layers.active.data]) if me.uv_layers else None
    print(p, 'meshes', len(ms), 'verts', len(V), 'tris', len(me.loop_triangles), 'uvlayers', len(me.uv_layers), 'mats', [m.name for m in me.materials], 'imgs', [(i.name, tuple(i.size)) for i in bpy.data.images])
    print('  bbox', V.min(0).round(4), V.max(0).round(4))
    return V, UV, [tuple(t.vertices) for t in me.loop_triangles]
A = load(a[0]); B = load(a[1])
if len(A[0]) == len(B[0]):
    print('max pos diff (same order)', np.abs(A[0]-B[0]).max())
    print('tris equal', A[2] == B[2])
    if A[1] is not None and B[1] is not None and A[1].shape == B[1].shape: print('max uv diff', np.abs(A[1]-B[1]).max())
else:
    from mathutils.kdtree import KDTree
    kd = KDTree(len(A[0]))
    for i, v in enumerate(A[0]): kd.insert(v, i)
    kd.balance(); d = np.array([kd.find(v)[2] for v in B[0]]); print('B->A nearest dist max %.5f mean %.5f' % (d.max(), d.mean()))
