# rig.py <clean.blend> <out.blend> : landmarks from the mesh -> armature -> auto weights
import bpy, sys, os, json
from mathutils import Vector as V
sys.path.append(os.path.dirname(__file__)); import samp
a = sys.argv[sys.argv.index('--')+1:]; bpy.ops.wm.open_mainfile(filepath=a[0]); out = a[1]
body = bpy.data.objects['Body']; P = samp.sample(body)
def sl(z0, z1, f=lambda p: True): return [p for p in P if z0 <= p.z < z1 and f(p)]
def cen(ps): return sum(ps, V()) / len(ps)
def xruns(z0, z1, f=lambda p: True): return samp.runs([p.x for p in sl(z0, z1, f)])
def central(rs): return next((r for r in rs if r[0] <= 0 <= r[1]), None)
H = max(p.z for p in P); L = {}
# --- legs: crotch = first z (from 0.03 up) where front-of-body slice is one run spanning x=0
notail = lambda p: p.y < 0.05
zc = None
for i in range(3, 40):
    z = i*0.005; rs = xruns(z, z+0.005, notail)
    c = central(rs)
    if c and c[0] < -0.02 and c[1] > 0.02: zc = z; break
L['crotch_z'] = zc
for s, sg in (('L', 1), ('R', -1)):
    # character faces -Y, so its left is +X
    side = lambda p, sg=sg: p.x*sg > 0.01
    leg = sl(0.035, zc, lambda p: side(p) and notail(p)); lc = cen(leg)
    foot = sl(0.0, 0.03, side)
    toe = min(foot, key=lambda p: p.y); heel = max(foot, key=lambda p: p.y)
    ank = cen(sl(0.035, 0.06, side)); ank.z = 0.045
    ball = cen([p for p in foot if p.y < toe.y + 0.06 and p.y > toe.y + 0.035]); ball.z = 0.018
    tip = V((ball.x, toe.y + 0.004, 0.012))
    hip = V((lc.x, cen(sl(zc, zc+0.02, notail)).y, zc + 0.025))
    knee = (hip + ank) / 2; knee.y -= 0.012
    L['leg_'+s] = dict(hip=hip, knee=knee, ankle=ank, ball=ball, tip=tip, heel=heel)
# --- arms: armpit = highest z with three x-runs (arm clear of the torso)
za = None
for i in range(60, 20, -1):
    z = i*0.005; rs = xruns(z, z+0.005)
    if len(rs) >= 3 and rs[0][1] < central(rs)[0] and rs[-1][0] > central(rs)[1]: za = z + 0.005; break
L['armpit_z'] = za
cw = central(xruns(za - 0.02, za - 0.01))[1]
for s, sg in (('L', 1), ('R', -1)):
    arm = [p for p in sl(0.12, za + 0.03) if p.x*sg > cw + 0.004]
    tipp = max(arm, key=lambda p: p.x*sg)
    sh = V((sg*(cw + 0.004), cen([p for p in arm if p.z > za - 0.015]).y, za + 0.012))
    d = tipp - sh
    def along(t, r=0.02):
        q = sh + d*t; ps = [p for p in arm if (p - q).length < r]
        return cen(ps) if ps else q
    elb = along(0.45); elb.y += 0.006; wr = along(0.74)
    L['arm_'+s] = dict(clav=V((sg*0.02, sh.y, sh.z + 0.004)), shoulder=sh, elbow=elb, wrist=wr, tip=tipp)
# --- spine / neck / head
def ymid(z): ps = sl(z - 0.005, z + 0.005, lambda p: abs(p.x) < 0.03 and (p.y < 0.055 or z > 0.17)); return (min(p.y for p in ps) + max(p.y for p in ps)) / 2
best = None
for i in range(int(za/0.005) + 4, int(0.40/0.005)):
    z = i*0.005; ps = sl(z, z+0.005, lambda p: abs(p.x) < 0.03)
    dep = max(p.y for p in ps) - min(p.y for p in ps)   # front-to-back depth: the neck is the thinnest
    if best is None or dep < best[1]: best = (z, dep)
zn = best[0]; L['neck_z'] = zn
# ear base: lowest z above the neck where both sides have a run clear of the midline
ze = None
for i in range(int(0.40/0.005), int(H/0.005)):
    z = i*0.005; rs = xruns(z, z+0.005)
    if rs and rs[0][1] < -0.012 and rs[-1][0] > 0.012 and not central(rs) or (central(rs) and central(rs)[1]-central(rs)[0] < 0.05 and len(rs) >= 3):
        ze = z; break
L['ear_base_z'] = ze
spz = [zc, zc + 0.035, zc + 0.035 + (zn - 0.02 - zc - 0.035)/3, zc + 0.035 + 2*(zn - 0.02 - zc - 0.035)/3, zn - 0.02]
L['spine'] = [V((0, ymid(z), z)) for z in spz]
L['neck'] = [V((0, ymid(zn - 0.02), zn - 0.02)), V((0, ymid(zn + 0.025), zn + 0.025))]
L['head_top'] = V((0, ymid(ze - 0.01), ze))
for s, sg in (('L', 1), ('R', -1)):
    ear = [p for p in P if p.z > ze and p.x*sg > 0.012]
    b = cen([p for p in ear if p.z < ze + 0.02]); t = cen([p for p in ear if p.z > H - 0.015])
    m = cen([p for p in ear if abs(p.z - (b.z + t.z)/2) < 0.01])
    L['ear_'+s] = [b, m, t]
tail = [p for p in P if p.y > 0.055 and 0.05 < p.z < 0.17]
tc = cen(tail); tt = max(tail, key=lambda p: p.y)
L['tail'] = [V((0, 0.05, tc.z)), V((0, tt.y - 0.01, tc.z))]
s3 = L['spine'][3]; back = max(p.y for p in sl(s3.z - 0.01, s3.z + 0.01, lambda p: abs(p.x) < 0.03))
L['stow'] = [V((0, back + 0.015, s3.z - 0.03)), V((0, back + 0.015, s3.z + 0.05))]
def fmt(v): return '(%.3f, %.3f, %.3f)' % tuple(v)
print('LANDMARKS height %.3f crotch %.3f armpit %.3f neck %.3f ear_base %.3f' % (H, zc, za, zn, ze))
for k, v in L.items():
    if isinstance(v, dict): print('  ', k, ' '.join('%s=%s' % (kk, fmt(vv)) for kk, vv in v.items()))
    elif isinstance(v, list): print('  ', k, ' -> '.join(fmt(x) for x in v))
    elif isinstance(v, V): print('  ', k, fmt(v))
# --- armature
arm = bpy.data.armatures.new('BunnyRig'); ao = bpy.data.objects.new('BunnyRig', arm)
bpy.context.scene.collection.objects.link(ao); bpy.context.view_layer.objects.active = ao
bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
def B(name, h, t, parent=None, conn=False, deform=True):
    b = eb.new(name); b.head = h; b.tail = t; b.parent = eb[parent] if parent else None
    b.use_connect = conn; b.use_deform = deform; return b
sp = L['spine']
B('root', V((0, 0, 0)), V((0, -0.08, 0)), deform=False)
B('hips', sp[0] + V((0,0,-0.0)), sp[1], 'root')
B('spine_01', sp[1], sp[2], 'hips', True); B('spine_02', sp[2], sp[3], 'spine_01', True); B('spine_03', sp[3], sp[4], 'spine_02', True)
B('neck', sp[4], L['neck'][1], 'spine_03', True); B('head', L['neck'][1], L['head_top'], 'neck', True)
for s in 'LR':
    e = L['ear_'+s]; B('ear_%s_01' % s, e[0], e[1], 'head'); B('ear_%s_02' % s, e[1], e[2], 'ear_%s_01' % s, True)
    m = L['arm_'+s]
    B('clavicle_'+s, m['clav'], m['shoulder'], 'spine_03')
    B('upperarm_'+s, m['shoulder'], m['elbow'], 'clavicle_'+s, True); B('forearm_'+s, m['elbow'], m['wrist'], 'upperarm_'+s, True)
    B('hand_'+s, m['wrist'], m['tip'], 'forearm_'+s, True)
    g = L['leg_'+s]
    B('thigh_'+s, g['hip'], g['knee'], 'hips'); B('shin_'+s, g['knee'], g['ankle'], 'thigh_'+s, True)
    B('foot_'+s, g['ankle'], g['ball'], 'shin_'+s, True); B('toe_'+s, g['ball'], g['tip'], 'foot_'+s, True)
B('tail', L['tail'][0], L['tail'][1], 'hips')
B('weapon_stow', L['stow'][0], L['stow'][1], 'spine_03', deform=False)
for b in eb:   # consistent rolls: local X = character's left (+X) where possible
    b.align_roll(V((0, 0, 1)) if abs(b.vector.normalized().z) < 0.7 else V((0, -1, 0)))
bpy.ops.object.mode_set(mode='OBJECT')
print('BONES', len(arm.bones), [b.name for b in arm.bones])
# --- skin
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); ao.select_set(True); bpy.context.view_layer.objects.active = ao
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
vg = body.vertex_groups; me = body.data
unw = [v.index for v in me.vertices if not any(g.weight > 1e-4 for g in v.groups)]
print('UNWEIGHTED', len(unw))
json.dump({k: ([list(x) for x in v] if isinstance(v, list) else {kk: list(vv) for kk, vv in v.items()} if isinstance(v, dict) else list(v) if isinstance(v, V) else v) for k, v in L.items()}, open(out.replace('.blend', '_landmarks.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=out)
