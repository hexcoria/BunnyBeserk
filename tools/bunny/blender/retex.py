# retex.py <anim.blend> <refined.glb> <texdir> <out.blend> [nopbr]
# Same geometry as the rigged mesh, new UVs from Meshy refine: copy the refine's per-corner UVs onto Body
# (rig, weights, actions untouched) and swap the material's maps for Meshy's (base colour, + normal, roughness).
import bpy, sys, os
from mathutils import Vector
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index('--')+1:]; src, glb, td, out = a[:4]; PBR = not (len(a) > 4 and a[4] == 'nopbr')
bpy.ops.wm.open_mainfile(filepath=src)
body = bpy.data.objects['Body']; me = body.data
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=glb)
ref = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]; rm = ref.data
RV = [ref.matrix_world @ v.co for v in rm.vertices]; BV = [v.co.copy() for v in me.vertices]
def bb(P): return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])
rl, rh = bb(RV); bl, bh = bb(BV)
s = (bh.z - bl.z) / (rh.z - rl.z); rc = Vector(((rl.x+rh.x)/2, (rl.y+rh.y)/2, rl.z)); bc = Vector(((bl.x+bh.x)/2, (bl.y+bh.y)/2, bl.z))
RV = [(p - rc) * s + bc for p in RV]
print('scale', s, 'body polys', len(me.polygons), 'ref polys', len(rm.polygons))
ruv = rm.uv_layers.active.data
kd = KDTree(len(rm.polygons))
for p in rm.polygons: kd.insert(sum((RV[i] for i in p.vertices), Vector()) / len(p.vertices), p.index)
kd.balance()
uvl = me.uv_layers.active; worst = 0.0; worstc = 0.0
for p in me.polygons:
    c = sum((BV[i] for i in p.vertices), Vector()) / len(p.vertices)
    _, j, d = kd.find(c); worst = max(worst, d); q = rm.polygons[j]
    assert len(q.vertices) == len(p.vertices)
    for li in p.loop_indices:
        P = BV[me.loops[li].vertex_index]
        k = min(q.loop_indices, key=lambda l: (RV[rm.loops[l].vertex_index] - P).length)
        worstc = max(worstc, (RV[rm.loops[k].vertex_index] - P).length)
        uvl.data[li].uv = ruv[k].uv
print('MATCH worst centroid dist %.2e  worst corner dist %.2e' % (worst, worstc))
for o in [o for o in bpy.data.objects if o not in before]: bpy.data.objects.remove(o)
for m in [m for m in bpy.data.meshes if m.users == 0]: bpy.data.meshes.remove(m)
for m in [m for m in bpy.data.materials if m.users == 0]: bpy.data.materials.remove(m)
for i in [i for i in bpy.data.images if i.users == 0]: bpy.data.images.remove(i)
# material
mat = me.materials[0]; nt = mat.node_tree; bs = nt.nodes['Principled BSDF']
old = [n.image for n in nt.nodes if n.type == 'TEX_IMAGE']
for n in [n for n in nt.nodes if n.type in ('TEX_IMAGE', 'NORMAL_MAP')]: nt.nodes.remove(n)
for i in old:
    if i and i.users == 0: bpy.data.images.remove(i)
def img(name, cs):
    im = bpy.data.images.load(os.path.join(td, name + '.png')); im.name = name; im.colorspace_settings.name = cs; im.pack(); return im
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img('bunny_basecolor', 'sRGB'); tx.location = (-500, 300)
nt.links.new(tx.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Metallic'].default_value = 0.0
if PBR:
    tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = img('bunny_roughness', 'Non-Color'); tr.location = (-500, 0)
    nt.links.new(tr.outputs['Color'], bs.inputs['Roughness'])
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img('bunny_normal', 'Non-Color'); tn.location = (-800, -300)
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.location = (-500, -300)
    nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])
else:
    bs.inputs['Roughness'].default_value = 0.85
print('IMAGES', [(i.name, tuple(i.size), i.packed_file is not None) for i in bpy.data.images])
bpy.ops.wm.save_as_mainfile(filepath=out)
