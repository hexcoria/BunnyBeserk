# check.py <rig.blend> <outprefix> : renders rest / upright / fours (3/4 view) and a weight map
import bpy, sys, os, json, colorsys
sys.path.append(os.path.dirname(__file__)); import rlib, posekit as K, poses as P
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0]); out = a[1]
arm = bpy.data.objects['BunnyRig']; body = bpy.data.objects['Body']; K.init(arm)
P.init(json.load(open(a[0].replace('.blend', '_landmarks.json'))))
sc = rlib.setup(420); sc.display.shading.color_type = 'SINGLE'
arm.show_in_front = True; arm.data.display_type = 'STICK'
views = {'q': ((0.95, -1.15, 0.6), (0, -0.03, 0.2)), 's': ((1.4, -0.05, 0.25), (0, -0.05, 0.22)), 'f': ((0.0, -1.4, 0.3), (0, 0, 0.27))}
def shots(tag):
    for k, (loc, tg) in views.items(): rlib.shot(rlib.cam('C'+k, loc, tg, lens=50), '%s_%s_%s.png' % (out, tag, k))
K.reset(); K.upd(); shots('rest')
K.apply(*K.solve(P.up())); shots('up')
K.apply(*K.solve(P.up(aimw=1))); shots('aim')
K.apply(*K.solve(P.fours())); shots('fours')
# weight map: dominant bone per vertex as a colour attribute
K.reset(); K.upd()
names = [g.name for g in body.vertex_groups]
ca = body.data.color_attributes.new('W', 'FLOAT_COLOR', 'POINT')
for v in body.data.vertices:
    g = max(v.groups, key=lambda g: g.weight) if v.groups else None
    h = ((names.index(body.vertex_groups[g.group].name) * 0.381) % 1) if g else 0
    ca.data[v.index].color = (*colorsys.hsv_to_rgb(h, 0.8, 0.95), 1)
sc.display.shading.color_type = 'VERTEX'; arm.hide_render = True
for k in 'qf': rlib.shot(rlib.cam('C'+k, *views[k], lens=50), '%s_weights_%s.png' % (out, k))
